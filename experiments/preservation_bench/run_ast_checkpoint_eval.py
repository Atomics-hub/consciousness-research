#!/usr/bin/env python3
import argparse
import copy
import json
import platform
import sys
from pathlib import Path

import torch
import torch.nn.functional as F

EXPERIMENTS_DIR = Path(__file__).resolve().parents[1]
if str(EXPERIMENTS_DIR) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS_DIR))

from ast_preservation.agent.ablated import make_ablated_agent
from ast_preservation.agent.full_agent import AgentOutput, FullAgent
from ast_preservation.config import Config, set_seed
from ast_preservation.env.arena import CH_DISTRACTOR, CH_GOAL, Arena
from ast_preservation.evaluation.behavioral import (
    build_identity_probe_cues,
    evaluate_identity_probe_accuracy,
    evaluate_memory_overlap,
)
from ast_preservation.transplant.substrate_b import SubstrateBAgent
from ast_preservation.training.trainer import Trainer, detach_agent_state
from ast_preservation.transplant.transplant import finetune_transplanted, transplant_schema
from benchmark.ast_eval import run_ast_episode_log
from benchmark.episode_logs import (
    aggregate_episode_logs,
    summarize_episode,
    write_episode_logs_jsonl,
)
from benchmark.seeds import build_seed_registry, stable_seed, write_seed_registry


SUPPORTED_CONDITIONS = {
    "source_full",
    "source_attention_ablated",
    "source_schema_ablated",
    "source_self_model_ablated",
    "a_to_a_copy",
    "b_frozen_copy",
    "b_adapter_repair_copy",
    "b_source_align_repair_copy",
    "b_source_align_repair_copy_long",
    "b_source_align_policy_copy_long",
    "b_source_align_attention_copy_long",
    "b_source_align_attention_adapter_long",
    "b_source_align_control_adapter_long",
    "b_source_align_attention_copy_trainable_long",
    "b_source_align_attention_copy_random_adapter_long",
    "b_source_align_identity_adapter_long",
    "b_frozen_random",
    "b_trainable_copy",
    "b_trainable_random",
    "b_behavior_distill",
    "b_full_retrain",
}


def load_config(path: Path) -> dict:
    with path.open() as f:
        return json.load(f)


def load_source_agent(cfg: Config, checkpoint_path: Path) -> FullAgent:
    source_agent = FullAgent(cfg)
    ckpt = torch.load(checkpoint_path, weights_only=False, map_location=cfg.device)
    source_agent.load_state_dict(ckpt["agent"])
    if "memory" in ckpt:
        source_agent.self_model.load_memory_state(ckpt["memory"])
    source_agent.eval()
    return source_agent


def freeze_schema_and_self_model(agent) -> None:
    for param in agent.schema.parameters():
        param.requires_grad = False
    for param in agent.self_model.parameters():
        param.requires_grad = False


def transplant_policy_head(source_agent, target_agent, freeze_policy: bool = True) -> None:
    target_agent.dqn_head.load_state_dict(copy.deepcopy(source_agent.dqn_head.state_dict()))
    if freeze_policy:
        for param in target_agent.dqn_head.parameters():
            param.requires_grad = False


def transplant_attention(source_agent, target_agent, freeze_attention: bool = True) -> None:
    target_agent.attention = copy.deepcopy(source_agent.attention)
    for param in target_agent.attention.parameters():
        param.requires_grad = not freeze_attention


def initialize_identity_linear(module: torch.nn.Linear) -> None:
    if module.weight.shape[0] != module.weight.shape[1]:
        raise ValueError("Identity initialization requires a square linear layer.")
    with torch.no_grad():
        module.weight.zero_()
        module.weight += torch.eye(module.weight.shape[0], device=module.weight.device)
        module.bias.zero_()


def initialize_identity_adapters(agent) -> None:
    initialize_identity_linear(agent.schema_adapter)
    initialize_identity_linear(agent.feature_adapter)


class SourceInterfaceAdapter(torch.nn.Module):
    def __init__(self, map_size: int, feature_dim: int) -> None:
        super().__init__()
        self.attn_delta = torch.nn.Sequential(
            torch.nn.Linear(map_size, map_size * 2),
            torch.nn.ReLU(),
            torch.nn.Linear(map_size * 2, map_size),
        )
        self.feature_delta = torch.nn.Sequential(
            torch.nn.Linear(feature_dim, feature_dim * 2),
            torch.nn.ReLU(),
            torch.nn.Linear(feature_dim * 2, feature_dim),
        )
        self._zero_last_layer(self.attn_delta)
        self._zero_last_layer(self.feature_delta)

    @staticmethod
    def _zero_last_layer(module: torch.nn.Sequential) -> None:
        last = module[-1]
        with torch.no_grad():
            last.weight.zero_()
            last.bias.zero_()

    def forward(
        self,
        attention_weights: torch.Tensor,
        attended_features: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        attn_logits = torch.log(attention_weights.clamp_min(1e-6))
        adapted_attention = F.softmax(attn_logits + self.attn_delta(attention_weights), dim=-1)
        adapted_features = attended_features + self.feature_delta(attended_features)
        return adapted_attention, adapted_features


class SourceInterfaceSubstrateBAgent(SubstrateBAgent):
    def __init__(self, cfg: Config) -> None:
        super().__init__(cfg)
        self.schema_adapter = torch.nn.Identity()
        self.feature_adapter = torch.nn.Identity()
        self.source_interface = SourceInterfaceAdapter(
            map_size=cfg.attn_map_size,
            feature_dim=cfg.attn_feature_dim,
        )

    def forward(self, obs):
        if self.schema_hidden is None:
            self.reset_episode(obs.size(0), obs.device)

        raw_attn, raw_features = self.attention(obs, self.last_modulation)
        adapted_attn, adapted_features = self.source_interface(raw_attn, raw_features)

        schema_out, self.schema_hidden = self.schema(adapted_attn, self.schema_hidden)
        self.last_modulation = schema_out.modulation.detach()

        sm_out = self.self_model(adapted_features, schema_out.state)
        dqn_input = torch.cat([adapted_features, schema_out.state, sm_out.identity], dim=-1)
        q_values = self.dqn_head(dqn_input)

        return AgentOutput(
            q_values=q_values,
            attention_weights=adapted_attn,
            attended_features=adapted_features,
            schema=schema_out,
            self_model=sm_out,
        )


def condition_seed(
    study_id: str,
    master_seed: int,
    role: str,
    condition: str,
    train_idx: int,
    condition_seed_aliases: dict[str, str] | None = None,
) -> int:
    seed_condition = (condition_seed_aliases or {}).get(condition, condition)
    return stable_seed(
        study_id=study_id,
        master_seed=master_seed,
        role=role,
        condition=seed_condition,
        training_seed_index=train_idx,
    )


def copy_config_with_seed(cfg: Config, seed: int) -> Config:
    new_cfg = copy.copy(cfg)
    new_cfg.seed = seed
    return new_cfg


def condition_seed_aliases(cfg: Config) -> dict[str, str]:
    return dict(getattr(cfg, "condition_seed_aliases", {}) or {})


def copy_config_for_condition(cfg: Config, seed: int, condition: str) -> Config:
    new_cfg = copy_config_with_seed(cfg, seed)
    condition_steps = getattr(cfg, "condition_finetune_steps", {}) or {}
    if condition in condition_steps:
        new_cfg.finetune_steps = int(condition_steps[condition])
    return new_cfg


def maybe_finetune(
    agent,
    cfg: Config,
    study_id: str,
    master_seed: int,
    condition: str,
    train_idx: int,
) -> None:
    finetune_seed = condition_seed(
        study_id,
        master_seed,
        "finetune_env_seed",
        condition,
        train_idx,
        condition_seed_aliases(cfg),
    )
    ft_cfg = copy_config_for_condition(cfg, finetune_seed, condition)
    set_seed(finetune_seed)
    ft_env = Arena(ft_cfg)
    finetune_transplanted(agent, ft_env, ft_cfg)


def train_target_from_scratch(
    agent,
    cfg: Config,
    study_id: str,
    master_seed: int,
    condition: str,
    train_idx: int,
) -> None:
    train_seed = condition_seed(
        study_id,
        master_seed,
        "finetune_env_seed",
        condition,
        train_idx,
        condition_seed_aliases(cfg),
    )
    train_cfg = copy_config_with_seed(cfg, train_seed)
    set_seed(train_seed)
    env = Arena(train_cfg)
    trainer = Trainer(agent, train_cfg)
    while trainer.global_step < train_cfg.total_steps:
        trainer.train_step(env)
    agent.eval()


def distill_behavior_only(
    student_agent,
    teacher_agent,
    cfg: Config,
    study_id: str,
    master_seed: int,
    condition: str,
    train_idx: int,
) -> None:
    distill_seed = condition_seed(
        study_id,
        master_seed,
        "finetune_env_seed",
        condition,
        train_idx,
        condition_seed_aliases(cfg),
    )
    distill_cfg = copy_config_for_condition(cfg, distill_seed, condition)
    set_seed(distill_seed)
    env = Arena(distill_cfg)
    env.set_curriculum_phase(3)

    teacher_agent.eval()
    student_agent.train()
    optimizer = torch.optim.Adam(student_agent.parameters(), lr=cfg.lr)

    step = 0
    while step < distill_cfg.finetune_steps:
        obs = env.reset()
        teacher_agent.reset_episode(batch_size=1, device=cfg.device)
        student_agent.reset_episode(batch_size=1, device=cfg.device)

        while True:
            obs_t = torch.tensor(obs, dtype=torch.float32, device=cfg.device).unsqueeze(0)

            with torch.no_grad():
                teacher_out = teacher_agent(obs_t)
                teacher_action = teacher_out.q_values.argmax(dim=-1).item()

            student_out = student_agent(obs_t)
            q_loss = F.smooth_l1_loss(student_out.q_values, teacher_out.q_values.detach())
            attention_loss = F.mse_loss(
                student_out.attention_weights,
                teacher_out.attention_weights.detach(),
            )
            report_loss = F.mse_loss(
                student_out.schema.self_report,
                teacher_out.schema.self_report.detach(),
            )
            other_report_loss = F.mse_loss(
                student_out.schema.other_report,
                teacher_out.schema.other_report.detach(),
            )
            loss = q_loss + 0.1 * attention_loss + cfg.report_loss_weight * (
                report_loss + other_report_loss
            )

            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(student_agent.parameters(), 1.0)
            optimizer.step()
            detach_agent_state(student_agent)
            detach_agent_state(teacher_agent)

            result = env.step(
                teacher_action,
                attention_weights=teacher_out.attention_weights.squeeze(0).detach().cpu().numpy(),
            )
            obs = result.obs
            step += 1

            if result.done or step >= distill_cfg.finetune_steps:
                break

    student_agent.eval()


def align_copied_target_to_source(
    target_agent,
    source_agent,
    cfg: Config,
    study_id: str,
    master_seed: int,
    condition: str,
    train_idx: int,
) -> None:
    align_seed = condition_seed(
        study_id,
        master_seed,
        "finetune_env_seed",
        condition,
        train_idx,
        condition_seed_aliases(cfg),
    )
    align_cfg = copy_config_for_condition(cfg, align_seed, condition)
    set_seed(align_seed)
    env = Arena(align_cfg)
    env.set_curriculum_phase(3)

    source_agent.eval()
    target_agent.train()
    trainable_params = [p for p in target_agent.parameters() if p.requires_grad]
    optimizer = torch.optim.Adam(trainable_params, lr=cfg.lr)

    step = 0
    while step < align_cfg.finetune_steps:
        obs = env.reset()
        source_agent.reset_episode(batch_size=1, device=cfg.device)
        target_agent.reset_episode(batch_size=1, device=cfg.device)

        while True:
            obs_t = torch.tensor(obs, dtype=torch.float32, device=cfg.device).unsqueeze(0)

            with torch.no_grad():
                source_out = source_agent(obs_t)
                source_action = source_out.q_values.argmax(dim=-1).item()

            target_out = target_agent(obs_t)
            q_loss = F.smooth_l1_loss(target_out.q_values, source_out.q_values.detach())
            attention_loss = F.mse_loss(
                target_out.attention_weights,
                source_out.attention_weights.detach(),
            )
            feature_loss = F.mse_loss(
                target_out.attended_features,
                source_out.attended_features.detach(),
            )
            self_report_loss = F.mse_loss(
                target_out.schema.self_report,
                source_out.schema.self_report.detach(),
            )
            other_report_loss = F.mse_loss(
                target_out.schema.other_report,
                source_out.schema.other_report.detach(),
            )
            identity_loss = F.mse_loss(
                target_out.self_model.identity,
                source_out.self_model.identity.detach(),
            )
            loss = (
                q_loss
                + 0.25 * attention_loss
                + 0.25 * feature_loss
                + cfg.report_loss_weight * (self_report_loss + other_report_loss)
                + 0.1 * identity_loss
            )

            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(trainable_params, 1.0)
            optimizer.step()
            detach_agent_state(target_agent)
            detach_agent_state(source_agent)

            result = env.step(
                source_action,
                attention_weights=source_out.attention_weights.squeeze(0).detach().cpu().numpy(),
            )
            obs = result.obs
            step += 1

            if result.done or step >= align_cfg.finetune_steps:
                break

    target_agent.eval()


def attention_mass_loss(obs_t: torch.Tensor, attention_weights: torch.Tensor) -> torch.Tensor:
    goal_mask = (obs_t[:, CH_GOAL].reshape(obs_t.size(0), -1) > 0).float()
    distractor_mask = (obs_t[:, CH_DISTRACTOR].reshape(obs_t.size(0), -1) > 0).float()
    goal_mass = (attention_weights * goal_mask).sum(dim=-1)
    distractor_mass = (attention_weights * distractor_mask).sum(dim=-1)
    return -goal_mass.mean() + 0.5 * distractor_mass.mean()


def align_copied_target_to_source_with_control(
    target_agent,
    source_agent,
    cfg: Config,
    study_id: str,
    master_seed: int,
    condition: str,
    train_idx: int,
) -> None:
    align_seed = condition_seed(
        study_id,
        master_seed,
        "finetune_env_seed",
        condition,
        train_idx,
        condition_seed_aliases(cfg),
    )
    align_cfg = copy_config_for_condition(cfg, align_seed, condition)
    set_seed(align_seed)
    env = Arena(align_cfg)
    env.set_curriculum_phase(3)

    source_agent.eval()
    target_agent.train()
    trainable_params = [p for p in target_agent.parameters() if p.requires_grad]
    optimizer = torch.optim.Adam(trainable_params, lr=cfg.lr)

    step = 0
    while step < align_cfg.finetune_steps:
        obs = env.reset()
        source_agent.reset_episode(batch_size=1, device=cfg.device)
        target_agent.reset_episode(batch_size=1, device=cfg.device)

        while True:
            obs_t = torch.tensor(obs, dtype=torch.float32, device=cfg.device).unsqueeze(0)

            with torch.no_grad():
                source_out = source_agent(obs_t)
                source_action = source_out.q_values.argmax(dim=-1).item()

            target_out = target_agent(obs_t)
            q_loss = F.smooth_l1_loss(target_out.q_values, source_out.q_values.detach())
            action_loss = F.cross_entropy(
                target_out.q_values,
                torch.tensor([source_action], dtype=torch.long, device=cfg.device),
            )
            attention_loss = torch.abs(
                target_out.attention_weights - source_out.attention_weights.detach()
            ).sum(dim=-1).mean()
            feature_loss = F.mse_loss(
                target_out.attended_features,
                source_out.attended_features.detach(),
            )
            self_report_loss = F.mse_loss(
                target_out.schema.self_report,
                source_out.schema.self_report.detach(),
            )
            other_report_loss = F.mse_loss(
                target_out.schema.other_report,
                source_out.schema.other_report.detach(),
            )
            identity_loss = F.mse_loss(
                target_out.self_model.identity,
                source_out.self_model.identity.detach(),
            )
            goal_control_loss = attention_mass_loss(obs_t, target_out.attention_weights)

            result = env.step(
                source_action,
                attention_weights=target_out.attention_weights.squeeze(0).detach().cpu().numpy(),
            )

            saved_hidden = target_agent.schema_hidden
            saved_mod = target_agent.last_modulation
            next_obs_t = torch.tensor(result.obs, dtype=torch.float32, device=cfg.device).unsqueeze(0)
            with torch.no_grad():
                next_out = target_agent(next_obs_t)
                next_q = next_out.q_values.max(dim=1)[0]
                target_q = torch.tensor([result.reward], dtype=torch.float32, device=cfg.device)
                target_q = target_q + align_cfg.gamma * next_q * (1 - float(result.done))
            target_agent.schema_hidden = saved_hidden
            target_agent.last_modulation = saved_mod

            chosen_q = target_out.q_values[0, source_action].unsqueeze(0)
            td_loss = F.smooth_l1_loss(chosen_q, target_q)

            loss = (
                q_loss
                + action_loss
                + 0.5 * attention_loss
                + 0.25 * feature_loss
                + cfg.report_loss_weight * (self_report_loss + other_report_loss)
                + 0.1 * identity_loss
                + 0.5 * td_loss
                + goal_control_loss
            )

            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(trainable_params, 1.0)
            optimizer.step()
            detach_agent_state(target_agent)
            detach_agent_state(source_agent)

            obs = result.obs
            step += 1

            if result.done or step >= align_cfg.finetune_steps:
                break

    target_agent.eval()


def build_condition_agent(
    name: str,
    source_agent: FullAgent,
    cfg: Config,
    env: Arena,
    study_id: str,
    master_seed: int,
    train_idx: int,
):
    if name == "source_full":
        return source_agent
    if name == "source_attention_ablated":
        return make_ablated_agent(source_agent, "attention", env, cfg)
    if name == "source_schema_ablated":
        return make_ablated_agent(source_agent, "schema", env, cfg)
    if name == "source_self_model_ablated":
        return make_ablated_agent(source_agent, "self_model", env, cfg)
    if name == "a_to_a_copy":
        set_seed(condition_seed(study_id, master_seed, "target_init_seed", name, train_idx, condition_seed_aliases(cfg)))
        agent = FullAgent(cfg)
        transplant_schema(source_agent, agent, freeze_copied_state=True)
        return agent
    if name == "b_frozen_copy":
        set_seed(condition_seed(study_id, master_seed, "target_init_seed", name, train_idx, condition_seed_aliases(cfg)))
        agent = SubstrateBAgent(cfg)
        transplant_schema(source_agent, agent, freeze_copied_state=True)
        return agent
    if name == "b_adapter_repair_copy":
        set_seed(condition_seed(study_id, master_seed, "target_init_seed", name, train_idx, condition_seed_aliases(cfg)))
        agent = SubstrateBAgent(cfg)
        transplant_schema(source_agent, agent, freeze_copied_state=True)
        maybe_finetune(agent, cfg, study_id, master_seed, name, train_idx)
        return agent
    if name in ("b_source_align_repair_copy", "b_source_align_repair_copy_long"):
        set_seed(condition_seed(study_id, master_seed, "target_init_seed", name, train_idx, condition_seed_aliases(cfg)))
        agent = SubstrateBAgent(cfg)
        transplant_schema(source_agent, agent, freeze_copied_state=True)
        align_copied_target_to_source(agent, source_agent, cfg, study_id, master_seed, name, train_idx)
        return agent
    if name == "b_source_align_policy_copy_long":
        set_seed(condition_seed(study_id, master_seed, "target_init_seed", name, train_idx, condition_seed_aliases(cfg)))
        agent = SubstrateBAgent(cfg)
        transplant_schema(source_agent, agent, freeze_copied_state=True)
        transplant_policy_head(source_agent, agent, freeze_policy=True)
        align_copied_target_to_source(agent, source_agent, cfg, study_id, master_seed, name, train_idx)
        return agent
    if name == "b_source_align_attention_copy_long":
        set_seed(condition_seed(study_id, master_seed, "target_init_seed", name, train_idx, condition_seed_aliases(cfg)))
        agent = SubstrateBAgent(cfg)
        transplant_schema(source_agent, agent, freeze_copied_state=True)
        transplant_attention(source_agent, agent, freeze_attention=True)
        initialize_identity_adapters(agent)
        align_copied_target_to_source(agent, source_agent, cfg, study_id, master_seed, name, train_idx)
        return agent
    if name == "b_source_align_attention_adapter_long":
        set_seed(condition_seed(study_id, master_seed, "target_init_seed", name, train_idx, condition_seed_aliases(cfg)))
        agent = SourceInterfaceSubstrateBAgent(cfg)
        transplant_schema(source_agent, agent, freeze_copied_state=True)
        align_copied_target_to_source(agent, source_agent, cfg, study_id, master_seed, name, train_idx)
        return agent
    if name == "b_source_align_control_adapter_long":
        set_seed(condition_seed(study_id, master_seed, "target_init_seed", name, train_idx, condition_seed_aliases(cfg)))
        agent = SourceInterfaceSubstrateBAgent(cfg)
        transplant_schema(source_agent, agent, freeze_copied_state=True)
        align_copied_target_to_source_with_control(agent, source_agent, cfg, study_id, master_seed, name, train_idx)
        return agent
    if name == "b_source_align_attention_copy_trainable_long":
        set_seed(condition_seed(study_id, master_seed, "target_init_seed", name, train_idx, condition_seed_aliases(cfg)))
        agent = SubstrateBAgent(cfg)
        transplant_schema(source_agent, agent, freeze_copied_state=True)
        transplant_attention(source_agent, agent, freeze_attention=False)
        initialize_identity_adapters(agent)
        align_copied_target_to_source(agent, source_agent, cfg, study_id, master_seed, name, train_idx)
        return agent
    if name == "b_source_align_attention_copy_random_adapter_long":
        set_seed(condition_seed(study_id, master_seed, "target_init_seed", name, train_idx, condition_seed_aliases(cfg)))
        agent = SubstrateBAgent(cfg)
        transplant_schema(source_agent, agent, freeze_copied_state=True)
        transplant_attention(source_agent, agent, freeze_attention=True)
        align_copied_target_to_source(agent, source_agent, cfg, study_id, master_seed, name, train_idx)
        return agent
    if name == "b_source_align_identity_adapter_long":
        set_seed(condition_seed(study_id, master_seed, "target_init_seed", name, train_idx, condition_seed_aliases(cfg)))
        agent = SubstrateBAgent(cfg)
        transplant_schema(source_agent, agent, freeze_copied_state=True)
        initialize_identity_adapters(agent)
        align_copied_target_to_source(agent, source_agent, cfg, study_id, master_seed, name, train_idx)
        return agent
    if name == "b_frozen_random":
        set_seed(condition_seed(study_id, master_seed, "target_init_seed", name, train_idx, condition_seed_aliases(cfg)))
        agent = SubstrateBAgent(cfg)
        freeze_schema_and_self_model(agent)
        return agent
    if name == "b_trainable_copy":
        set_seed(condition_seed(study_id, master_seed, "target_init_seed", name, train_idx, condition_seed_aliases(cfg)))
        agent = SubstrateBAgent(cfg)
        transplant_schema(source_agent, agent, freeze_copied_state=False)
        maybe_finetune(agent, cfg, study_id, master_seed, name, train_idx)
        return agent
    if name == "b_trainable_random":
        set_seed(condition_seed(study_id, master_seed, "target_init_seed", name, train_idx, condition_seed_aliases(cfg)))
        agent = SubstrateBAgent(cfg)
        maybe_finetune(agent, cfg, study_id, master_seed, name, train_idx)
        return agent
    if name == "b_behavior_distill":
        set_seed(condition_seed(study_id, master_seed, "target_init_seed", name, train_idx, condition_seed_aliases(cfg)))
        agent = SubstrateBAgent(cfg)
        distill_behavior_only(agent, source_agent, cfg, study_id, master_seed, name, train_idx)
        return agent
    if name == "b_full_retrain":
        set_seed(condition_seed(study_id, master_seed, "target_init_seed", name, train_idx, condition_seed_aliases(cfg)))
        agent = SubstrateBAgent(cfg)
        train_target_from_scratch(agent, cfg, study_id, master_seed, name, train_idx)
        return agent
    raise ValueError(f"Unsupported checkpoint condition: {name}")


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(data, f, indent=2, sort_keys=True)


def run_condition(
    agent,
    env: Arena,
    cfg: Config,
    study_id: str,
    condition: str,
    train_idx: int,
    n_eval_episodes: int,
    master_seed: int,
    source_reference_agent=None,
) -> list:
    logs = []
    for eval_idx in range(n_eval_episodes):
        eval_seed = stable_seed(
            study_id=study_id,
            master_seed=master_seed,
            role="eval_episode_seed",
            condition="paired_eval",
            training_seed_index=train_idx,
            eval_episode_index=eval_idx,
        )
        logs.append(
            run_ast_episode_log(
                agent=agent,
                env=env,
                cfg=cfg,
                study_id=study_id,
                condition=condition,
                training_seed_index=train_idx,
                eval_episode_index=eval_idx,
                eval_seed=eval_seed,
                source_reference_agent=source_reference_agent,
            )
        )
    return logs


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate Paper 2 checkpoint conditions with PreservationBench logs."
    )
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()

    run_cfg = load_config(args.config)
    study_id = run_cfg["study_id"]
    master_seed = int(run_cfg["master_seed"])
    n_eval_episodes = int(run_cfg["n_eval_episodes"])
    train_idx = 0

    conditions = list(run_cfg["conditions"])
    unsupported = sorted(set(conditions) - SUPPORTED_CONDITIONS)
    if unsupported:
        supported = ", ".join(sorted(SUPPORTED_CONDITIONS))
        raise SystemExit(f"Unsupported conditions for this runner: {unsupported}. Supported: {supported}")

    cfg = Config()
    source_seed = int(
        run_cfg.get(
            "checkpoint_source_seed",
            stable_seed(study_id, master_seed, "source_train_seed", "source", train_idx),
        )
    )
    cfg.seed = source_seed
    cfg.max_steps = int(run_cfg.get("max_steps", cfg.max_steps))
    cfg.finetune_steps = int(run_cfg.get("finetune_steps", cfg.finetune_steps))
    cfg.total_steps = int(
        run_cfg.get(
            "target_train_steps",
            run_cfg.get("source_steps", cfg.total_steps),
        )
    )
    cfg.condition_finetune_steps = dict(run_cfg.get("condition_finetune_steps", {}))
    cfg.condition_seed_aliases = dict(run_cfg.get("condition_seed_aliases", {}))
    set_seed(cfg.seed)

    checkpoint_path = Path(run_cfg["checkpoint"])
    output_dir = Path(run_cfg["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    source_agent = load_source_agent(cfg, checkpoint_path)
    source_memories = source_agent.self_model.get_memory_state()
    identity_seed = stable_seed(study_id, master_seed, "identity_probe_seed", "source", train_idx)
    identity_cues = build_identity_probe_cues(n_probes=32, seed=identity_seed)

    seed_records = build_seed_registry(
        study_id=study_id,
        master_seed=master_seed,
        conditions=conditions,
        n_train_seeds=1,
        n_eval_episodes=n_eval_episodes,
        source_train_seed_override=source_seed,
        condition_seed_aliases=run_cfg.get("condition_seed_aliases", {}),
    )
    write_seed_registry(output_dir / "seed_registry.csv", seed_records)

    manifest = {
        "study_id": study_id,
        "config": run_cfg,
        "checkpoint": str(checkpoint_path),
        "python": sys.version,
        "platform": platform.platform(),
        "torch": torch.__version__,
        "checkpoint_source_seed": source_seed,
        "source_memory_count": len(source_memories),
    }
    write_json(output_dir / "manifest.json", manifest)

    all_episode_summaries = []
    seed_summaries = []

    for condition in conditions:
        print(f"Evaluating {condition}...")
        env = Arena(cfg)
        agent = build_condition_agent(
            name=condition,
            source_agent=source_agent,
            cfg=cfg,
            env=env,
            study_id=study_id,
            master_seed=master_seed,
            train_idx=train_idx,
        )
        agent.eval()
        logs = run_condition(
            agent=agent,
            env=env,
            cfg=cfg,
            study_id=study_id,
            condition=condition,
            train_idx=train_idx,
            n_eval_episodes=n_eval_episodes,
            master_seed=master_seed,
            source_reference_agent=source_agent,
        )
        write_episode_logs_jsonl(output_dir / f"{condition}_episodes.jsonl", logs)

        episode_summaries = [summarize_episode(log) for log in logs]
        all_episode_summaries.extend(episode_summaries)

        seed_summary = aggregate_episode_logs(logs)
        seed_summary["identity_probe_accuracy"] = evaluate_identity_probe_accuracy(
            agent,
            source_agent,
            identity_cues,
        )
        seed_summary["memory_overlap"] = evaluate_memory_overlap(agent, source_memories)
        seed_summaries.append(seed_summary)

    write_json(output_dir / "episode_summaries.json", all_episode_summaries)
    write_json(output_dir / "seed_summaries.json", seed_summaries)

    print("\nSummary")
    for summary in seed_summaries:
        print(
            f"{summary['condition']:<28} "
            f"reward={summary['reward']:>7.2f} "
            f"self_report={summary['self_report_corr']:>6.3f} "
            f"identity={summary['identity_probe_accuracy']:>5.3f}"
        )
    print(f"\nWrote artifacts to {output_dir}")


if __name__ == "__main__":
    main()
