#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import platform
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENTS_DIR = SCRIPT_DIR.parent
if str(EXPERIMENTS_DIR) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS_DIR))
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from ast_preservation.config import set_seed
from ast_preservation.env.arena import Arena
from benchmark.seeds import stable_seed
from run_ast_checkpoint_eval import build_condition_agent, load_source_agent
from run_ast_perturbation_probe import (
    make_cfg,
    mean_abs,
    mse,
    numeric_train_seed_index,
    read_json,
    recurrent_snapshot,
    restore_recurrent,
    validated_source_seed_dirs,
    write_json,
    write_jsonl,
)


PRIMARY_METRICS = [
    "source_patch_action_changed",
    "source_patch_q_delta_mse",
    "source_patch_self_report_delta_l1",
    "target_interchange_action_agreement",
    "target_patch_shift_match",
    "target_patch_delta_q_mse_to_source",
    "target_patch_delta_self_report_l1_to_source",
    "target_patched_q_mse_to_source_cf",
    "target_patched_self_report_l1_to_source_cf",
]


def load_config(path: Path) -> dict:
    with path.open() as f:
        return json.load(f)


def clone_tensor(value):
    if value is None:
        return None
    return value.detach().clone()


def clone_snapshot(snapshot):
    return tuple(clone_tensor(value) for value in snapshot)


def patch_snapshot(base_snapshot, donor_snapshot, vector_path: str):
    if vector_path not in {
        "schema_hidden",
        "last_modulation",
        "recurrent_state",
        "schema_state",
        "attention_state",
    }:
        raise ValueError(
            "Supported vector paths: schema_hidden, last_modulation, "
            "recurrent_state, schema_state, attention_state."
        )
    if vector_path in {"schema_state", "attention_state"}:
        raise ValueError(f"{vector_path} is an activation patch, not a snapshot patch.")
    if len(base_snapshot) < 2 or len(donor_snapshot) < 2:
        raise ValueError("Cannot patch from incomplete recurrent snapshot.")
    patched = list(clone_snapshot(base_snapshot))
    if vector_path in {"schema_hidden", "recurrent_state"}:
        patched[0] = clone_tensor(donor_snapshot[0])
    if vector_path in {"last_modulation", "recurrent_state"}:
        patched[1] = clone_tensor(donor_snapshot[1])
    return tuple(patched)


def patch_metadata(vector_path: str) -> dict:
    labels = {
        "schema_hidden": {
            "donor": "source_context_b_schema_hidden",
            "recipient": "condition_context_a_schema_hidden",
            "alignment": "identity_same_hidden_dimension",
        },
        "last_modulation": {
            "donor": "source_context_b_last_modulation",
            "recipient": "condition_context_a_last_modulation",
            "alignment": "identity_same_modulation_dimension",
        },
        "recurrent_state": {
            "donor": "source_context_b_schema_hidden_and_last_modulation",
            "recipient": "condition_context_a_schema_hidden_and_last_modulation",
            "alignment": "identity_same_recurrent_dimensions",
        },
        "schema_state": {
            "donor": "source_context_b_schema_state_activation",
            "recipient": "condition_context_a_schema_state_activation",
            "alignment": "identity_same_schema_state_dimension",
        },
        "attention_state": {
            "donor": "source_context_b_attention_weights_and_attended_features",
            "recipient": "condition_context_a_attention_weights_and_attended_features",
            "alignment": "identity_same_attention_dimensions",
        },
    }
    if vector_path not in labels:
        raise ValueError(f"Unsupported vector path for patch metadata: {vector_path}")
    return {"vector_path": vector_path, **labels[vector_path]}


def snapshot_tensor_mse(left_snapshot, right_snapshot, idx: int) -> float:
    left = left_snapshot[idx]
    right = right_snapshot[idx]
    if left is None or right is None:
        return 0.0
    return mse(left.detach().cpu().numpy() - right.detach().cpu().numpy())


def agent_response(agent, obs, cfg) -> dict:
    obs_t = torch.tensor(obs, dtype=torch.float32, device=cfg.device).unsqueeze(0)
    with torch.no_grad():
        out = agent(obs_t)
    return {
        "action": int(out.q_values.argmax(dim=-1).item()),
        "attention": out.attention_weights.squeeze(0).detach().cpu().numpy(),
        "features": out.attended_features.squeeze(0).detach().cpu().numpy(),
        "q_values": out.q_values.squeeze(0).detach().cpu().numpy(),
        "self_report": out.schema.self_report.squeeze(0).detach().cpu().numpy(),
        "schema_state": out.schema.state.squeeze(0).detach().cpu().numpy(),
    }


def agent_response_with_schema_state_patch(agent, obs, cfg, donor_schema_state) -> dict:
    obs_t = torch.tensor(obs, dtype=torch.float32, device=cfg.device).unsqueeze(0)
    donor_state = torch.tensor(
        donor_schema_state,
        dtype=torch.float32,
        device=cfg.device,
    ).reshape(1, -1)
    with torch.no_grad():
        out = agent(obs_t)
        self_report = F.softmax(agent.schema.self_report_head(donor_state), dim=-1)
        sm_out = agent.self_model(out.attended_features, donor_state)
        dqn_input = torch.cat([out.attended_features, donor_state, sm_out.identity], dim=-1)
        q_values = agent.dqn_head(dqn_input)
    return {
        "action": int(q_values.argmax(dim=-1).item()),
        "attention": out.attention_weights.squeeze(0).detach().cpu().numpy(),
        "features": out.attended_features.squeeze(0).detach().cpu().numpy(),
        "q_values": q_values.squeeze(0).detach().cpu().numpy(),
        "self_report": self_report.squeeze(0).detach().cpu().numpy(),
        "schema_state": donor_state.squeeze(0).detach().cpu().numpy(),
    }


def agent_response_with_attention_state_patch(
    agent,
    obs,
    cfg,
    donor_attention,
    donor_features,
) -> dict:
    donor_attention_t = torch.tensor(
        donor_attention,
        dtype=torch.float32,
        device=cfg.device,
    ).reshape(1, -1)
    donor_features_t = torch.tensor(
        donor_features,
        dtype=torch.float32,
        device=cfg.device,
    ).reshape(1, -1)
    with torch.no_grad():
        if agent.schema_hidden is None:
            agent.reset_episode(batch_size=1, device=cfg.device)
        schema_out, _ = agent.schema(donor_attention_t, agent.schema_hidden)
        sm_out = agent.self_model(donor_features_t, schema_out.state)
        dqn_input = torch.cat([donor_features_t, schema_out.state, sm_out.identity], dim=-1)
        q_values = agent.dqn_head(dqn_input)
    return {
        "action": int(q_values.argmax(dim=-1).item()),
        "attention": donor_attention_t.squeeze(0).detach().cpu().numpy(),
        "features": donor_features_t.squeeze(0).detach().cpu().numpy(),
        "q_values": q_values.squeeze(0).detach().cpu().numpy(),
        "self_report": schema_out.self_report.squeeze(0).detach().cpu().numpy(),
        "schema_state": schema_out.state.squeeze(0).detach().cpu().numpy(),
    }


def response_delta(after: dict, before: dict, key: str):
    return after[key] - before[key]


def advance_source_history(
    source_agent,
    target_agent,
    cfg,
    eval_seed: int,
    warmup_steps: int,
) -> dict:
    env = Arena(cfg)
    env.set_curriculum_phase(3)
    obs = env.reset(seed=eval_seed)
    source_agent.reset_episode(batch_size=1, device=cfg.device)
    if target_agent is not None:
        target_agent.reset_episode(batch_size=1, device=cfg.device)

    actual_steps = 0
    completed = False
    for _ in range(warmup_steps):
        obs_t = torch.tensor(obs, dtype=torch.float32, device=cfg.device).unsqueeze(0)
        with torch.no_grad():
            source_out = source_agent(obs_t)
            if target_agent is not None:
                target_agent(obs_t)
        source_action = int(source_out.q_values.argmax(dim=-1).item())
        source_attention = source_out.attention_weights.squeeze(0).detach().cpu().numpy()
        result = env.step(source_action, attention_weights=source_attention)
        actual_steps += 1
        obs = result.obs
        if result.done:
            completed = True
            break

    return {
        "obs": obs,
        "source_snapshot": recurrent_snapshot(source_agent),
        "target_snapshot": None
        if target_agent is None
        else recurrent_snapshot(target_agent),
        "actual_steps": actual_steps,
        "completed": int(completed),
    }


def source_patch_responses(source_agent, cfg, context_a: dict, context_b: dict, vector_path: str):
    source_a_snapshot = context_a["source_snapshot"]
    source_b_snapshot = context_b["source_snapshot"]

    restore_recurrent(source_agent, source_a_snapshot)
    source_a = agent_response(source_agent, context_a["obs"], cfg)

    restore_recurrent(source_agent, source_b_snapshot)
    source_b = agent_response(source_agent, context_b["obs"], cfg)

    restore_recurrent(source_agent, source_a_snapshot)
    if vector_path == "schema_state":
        source_cf = agent_response_with_schema_state_patch(
            source_agent,
            context_a["obs"],
            cfg,
            donor_schema_state=source_b["schema_state"],
        )
    elif vector_path == "attention_state":
        source_cf = agent_response_with_attention_state_patch(
            source_agent,
            context_a["obs"],
            cfg,
            donor_attention=source_b["attention"],
            donor_features=source_b["features"],
        )
    else:
        restore_recurrent(
            source_agent,
            patch_snapshot(source_a_snapshot, source_b_snapshot, vector_path),
        )
        source_cf = agent_response(source_agent, context_a["obs"], cfg)

    return source_a, source_cf, source_b


def source_patch_metrics(source_a: dict, source_cf: dict) -> dict:
    q_delta = response_delta(source_cf, source_a, "q_values")
    report_delta = response_delta(source_cf, source_a, "self_report")
    attention_delta = response_delta(source_cf, source_a, "attention")
    feature_delta = response_delta(source_cf, source_a, "features")
    schema_state_delta = response_delta(source_cf, source_a, "schema_state")
    action_changed = int(source_a["action"] != source_cf["action"])
    return {
        "source_patch_action_changed": action_changed,
        "source_patch_q_delta_mse": mse(q_delta),
        "source_patch_self_report_delta_l1": mean_abs(report_delta),
        "source_patch_attention_delta_l1": mean_abs(attention_delta),
        "source_patch_feature_delta_mse": mse(feature_delta),
        "source_patch_schema_state_delta_mse": mse(schema_state_delta),
        "source_patch_selection_score": float(
            10.0 * action_changed
            + mse(q_delta)
            + 5.0 * mean_abs(report_delta)
            + mse(schema_state_delta)
        ),
    }


def candidate_eval_seed(
    study_id: str,
    master_seed: int,
    train_idx: int,
    candidate_idx: int,
    side: str,
) -> int:
    return stable_seed(
        study_id=study_id,
        master_seed=master_seed,
        role="causal_patch_eval_seed",
        # Fixed namespace for reproducibility across the Paper 5 causal-patch panels.
        condition="schema_hidden_interchange",
        training_seed_index=train_idx,
        eval_episode_index=candidate_idx,
        extra=side,
    )


def select_source_candidates(
    source_agent,
    cfg,
    study_id: str,
    master_seed: int,
    train_idx: int,
    candidate_eval_pairs: int,
    selected_pairs: int,
    warmup_steps: int,
    vector_path: str,
) -> tuple[list[dict], list[dict]]:
    candidates = []
    for candidate_idx in range(candidate_eval_pairs):
        seed_a = candidate_eval_seed(study_id, master_seed, train_idx, candidate_idx, "A")
        seed_b = candidate_eval_seed(study_id, master_seed, train_idx, candidate_idx, "B")
        context_a = advance_source_history(
            source_agent=source_agent,
            target_agent=None,
            cfg=cfg,
            eval_seed=seed_a,
            warmup_steps=warmup_steps,
        )
        context_b = advance_source_history(
            source_agent=source_agent,
            target_agent=None,
            cfg=cfg,
            eval_seed=seed_b,
            warmup_steps=warmup_steps,
        )
        source_a, source_cf, source_b = source_patch_responses(
            source_agent=source_agent,
            cfg=cfg,
            context_a=context_a,
            context_b=context_b,
            vector_path=vector_path,
        )
        metrics = source_patch_metrics(source_a, source_cf)
        candidates.append(
            {
                "candidate_index": candidate_idx,
                "seed_a": int(seed_a),
                "seed_b": int(seed_b),
                "context_a": context_a,
                "context_b": context_b,
                "source_a": source_a,
                "source_cf": source_cf,
                "source_b": source_b,
                **metrics,
                "source_a_action": int(source_a["action"]),
                "source_cf_action": int(source_cf["action"]),
                "source_b_action": int(source_b["action"]),
                "source_b_action_matches_cf": int(source_b["action"] == source_cf["action"]),
            }
        )

    ranked = sorted(
        candidates,
        key=lambda item: (
            -float(item["source_patch_selection_score"]),
            -int(item["source_patch_action_changed"]),
            int(item["candidate_index"]),
        ),
    )
    selected = ranked[:selected_pairs]
    for rank, item in enumerate(selected):
        item["source_patch_selection_rank"] = rank
        item["source_patch_candidate_pool_size"] = candidate_eval_pairs
        item["selected_by_source_patch"] = 1
    return selected, candidates


def patched_source_response_for_donor(
    source_agent,
    cfg,
    selected: dict,
    donor: dict,
    vector_path: str,
) -> dict:
    restore_recurrent(source_agent, selected["context_a"]["source_snapshot"])
    if vector_path == "schema_state":
        return agent_response_with_schema_state_patch(
            source_agent,
            selected["context_a"]["obs"],
            cfg,
            donor_schema_state=donor["source_b"]["schema_state"],
        )
    if vector_path == "attention_state":
        return agent_response_with_attention_state_patch(
            source_agent,
            selected["context_a"]["obs"],
            cfg,
            donor_attention=donor["source_b"]["attention"],
            donor_features=donor["source_b"]["features"],
        )
    restore_recurrent(
        source_agent,
        patch_snapshot(
            selected["context_a"]["source_snapshot"],
            donor["context_b"]["source_snapshot"],
            vector_path,
        ),
    )
    return agent_response(source_agent, selected["context_a"]["obs"], cfg)


def control_spec_from_donor(
    source_agent,
    cfg,
    selected: dict,
    donor: dict,
    vector_path: str,
    donor_control: str,
) -> dict:
    spec = dict(selected)
    control_source_cf = (
        selected["source_cf"]
        if donor_control == "matched"
        else patched_source_response_for_donor(
            source_agent=source_agent,
            cfg=cfg,
            selected=selected,
            donor=donor,
            vector_path=vector_path,
        )
    )
    metrics = source_patch_metrics(selected["source_a"], control_source_cf)
    spec.update(
        {
            **metrics,
            "source_cf": control_source_cf,
            "source_cf_action": int(control_source_cf["action"]),
            "matched_source_cf": selected["source_cf"],
            "matched_source_cf_action": int(selected["source_cf"]["action"]),
            "donor_control": donor_control,
            "donor_control_found": 1,
            "donor_candidate_index": int(donor["candidate_index"]),
            "donor_seed_b": int(donor["seed_b"]),
            "donor_context_b": donor["context_b"],
            "donor_source_b": donor["source_b"],
            "donor_source_b_action": int(donor["source_b_action"]),
            "source_b_action_matches_cf": int(
                donor["source_b_action"] == control_source_cf["action"]
            ),
        }
    )
    return spec


def choose_shuffled_selected_donor(
    selected_candidates: list[dict],
    selected_index: int,
) -> dict:
    if len(selected_candidates) <= 1:
        return selected_candidates[selected_index]
    return selected_candidates[(selected_index + 1) % len(selected_candidates)]


def choose_same_action_donor(
    source_agent,
    cfg,
    selected: dict,
    candidate_pool: list[dict],
    vector_path: str,
) -> tuple[dict | None, dict | None]:
    source_a_action = int(selected["source_a_action"])
    ranked_pool = sorted(
        candidate_pool,
        key=lambda item: (
            -float(item.get("source_patch_selection_score", 0.0)),
            int(item["candidate_index"]),
        ),
    )
    for donor in ranked_pool:
        cf = patched_source_response_for_donor(
            source_agent=source_agent,
            cfg=cfg,
            selected=selected,
            donor=donor,
            vector_path=vector_path,
        )
        if int(cf["action"]) == source_a_action:
            return donor, cf
    return None, None


def choose_action_mismatch_donor(
    source_agent,
    cfg,
    selected: dict,
    candidate_pool: list[dict],
    vector_path: str,
) -> tuple[dict | None, dict | None]:
    matched_action = int(selected["source_cf_action"])
    ranked_pool = sorted(
        candidate_pool,
        key=lambda item: (
            -float(item.get("source_patch_selection_score", 0.0)),
            int(item["candidate_index"]),
        ),
    )
    for donor in ranked_pool:
        cf = patched_source_response_for_donor(
            source_agent=source_agent,
            cfg=cfg,
            selected=selected,
            donor=donor,
            vector_path=vector_path,
        )
        if int(cf["action"]) != matched_action:
            return donor, cf
    return None, None


def choose_donor_action_mismatch_donor(
    source_agent,
    cfg,
    selected: dict,
    candidate_pool: list[dict],
    vector_path: str,
) -> tuple[dict | None, dict | None]:
    ranked_pool = sorted(
        candidate_pool,
        key=lambda item: (
            -float(item.get("source_patch_selection_score", 0.0)),
            int(item["candidate_index"]),
        ),
    )
    matches = []
    source_a_action = int(selected["source_a_action"])
    for donor in ranked_pool:
        cf = patched_source_response_for_donor(
            source_agent=source_agent,
            cfg=cfg,
            selected=selected,
            donor=donor,
            vector_path=vector_path,
        )
        if int(cf["action"]) == int(donor["source_b_action"]):
            continue
        metrics = source_patch_metrics(selected["source_a"], cf)
        matches.append(
            (
                -int(cf["action"] != source_a_action),
                -float(metrics["source_patch_selection_score"]),
                int(donor["candidate_index"]),
                donor,
                cf,
            )
        )
    if not matches:
        return None, None
    matches.sort()
    return matches[0][3], matches[0][4]


def build_control_specs(
    source_agent,
    cfg,
    selected_candidates: list[dict],
    candidate_pool: list[dict],
    vector_path: str,
    donor_controls: list[str],
) -> list[dict]:
    specs: list[dict] = []
    for selected_index, selected in enumerate(selected_candidates):
        for donor_control in donor_controls:
            if donor_control == "matched":
                specs.append(
                    control_spec_from_donor(
                        source_agent=source_agent,
                        cfg=cfg,
                        selected=selected,
                        donor=selected,
                        vector_path=vector_path,
                        donor_control=donor_control,
                    )
                )
            elif donor_control == "shuffled_selected":
                specs.append(
                    control_spec_from_donor(
                        source_agent=source_agent,
                        cfg=cfg,
                        selected=selected,
                        donor=choose_shuffled_selected_donor(
                            selected_candidates,
                            selected_index,
                        ),
                        vector_path=vector_path,
                        donor_control=donor_control,
                    )
                )
            elif donor_control == "same_action":
                donor, cf = choose_same_action_donor(
                    source_agent=source_agent,
                    cfg=cfg,
                    selected=selected,
                    candidate_pool=candidate_pool,
                    vector_path=vector_path,
                )
                if donor is None or cf is None:
                    continue
                spec = control_spec_from_donor(
                    source_agent=source_agent,
                    cfg=cfg,
                    selected=selected,
                    donor=donor,
                    vector_path=vector_path,
                    donor_control=donor_control,
                )
                spec["source_cf"] = cf
                spec["source_cf_action"] = int(cf["action"])
                specs.append(spec)
            elif donor_control == "action_mismatch":
                donor, cf = choose_action_mismatch_donor(
                    source_agent=source_agent,
                    cfg=cfg,
                    selected=selected,
                    candidate_pool=candidate_pool,
                    vector_path=vector_path,
                )
                if donor is None or cf is None:
                    continue
                spec = control_spec_from_donor(
                    source_agent=source_agent,
                    cfg=cfg,
                    selected=selected,
                    donor=donor,
                    vector_path=vector_path,
                    donor_control=donor_control,
                )
                spec["source_cf"] = cf
                spec["source_cf_action"] = int(cf["action"])
                specs.append(spec)
            elif donor_control == "donor_action_mismatch":
                donor, cf = choose_donor_action_mismatch_donor(
                    source_agent=source_agent,
                    cfg=cfg,
                    selected=selected,
                    candidate_pool=candidate_pool,
                    vector_path=vector_path,
                )
                if donor is None or cf is None:
                    continue
                spec = control_spec_from_donor(
                    source_agent=source_agent,
                    cfg=cfg,
                    selected=selected,
                    donor=donor,
                    vector_path=vector_path,
                    donor_control=donor_control,
                )
                spec["source_cf"] = cf
                spec["source_cf_action"] = int(cf["action"])
                specs.append(spec)
            else:
                raise ValueError(f"Unsupported donor_control: {donor_control}")
    return specs


def condition_row(
    study_id: str,
    condition: str,
    train_idx: int,
    selected: dict,
    target_unpatched: dict,
    target_patched: dict,
    target_snapshot_a,
    source_snapshot_a,
    vector_path: str,
    obs_match: int,
) -> dict:
    source_a = selected["source_a"]
    source_cf = selected["source_cf"]
    matched_source_cf = selected.get("matched_source_cf", source_cf)

    source_delta_q = response_delta(source_cf, source_a, "q_values")
    target_delta_q = response_delta(target_patched, target_unpatched, "q_values")
    source_delta_report = response_delta(source_cf, source_a, "self_report")
    target_delta_report = response_delta(target_patched, target_unpatched, "self_report")
    source_delta_attention = response_delta(source_cf, source_a, "attention")
    target_delta_attention = response_delta(target_patched, target_unpatched, "attention")
    source_delta_schema_state = response_delta(source_cf, source_a, "schema_state")
    target_delta_schema_state = response_delta(
        target_patched,
        target_unpatched,
        "schema_state",
    )

    source_patch_action_changed = int(selected["source_patch_action_changed"])
    target_patch_action_changed = int(
        target_unpatched["action"] != target_patched["action"]
    )

    return {
        "study_id": study_id,
        "condition": condition,
        "training_seed_index": train_idx,
        "candidate_index": int(selected["candidate_index"]),
        "source_patch_selection_rank": int(selected["source_patch_selection_rank"]),
        "source_patch_candidate_pool_size": int(
            selected["source_patch_candidate_pool_size"]
        ),
        "eval_seed_a": int(selected["seed_a"]),
        "eval_seed_b": int(selected["seed_b"]),
        "vector_path": vector_path,
        "warmup_actual_steps_a": int(selected["context_a"]["actual_steps"]),
        "warmup_actual_steps_b": int(selected["context_b"]["actual_steps"]),
        "warmup_completed_episode_a": int(selected["context_a"]["completed"]),
        "warmup_completed_episode_b": int(selected["context_b"]["completed"]),
        "target_context_obs_matches_source_context_a": int(obs_match),
        "source_a_action": int(selected["source_a_action"]),
        "source_b_action": int(selected["source_b_action"]),
        "donor_control": str(selected.get("donor_control", "matched")),
        "donor_control_found": int(selected.get("donor_control_found", 1)),
        "donor_candidate_index": int(
            selected.get("donor_candidate_index", selected["candidate_index"])
        ),
        "donor_seed_b": int(selected.get("donor_seed_b", selected["seed_b"])),
        "donor_source_b_action": int(
            selected.get("donor_source_b_action", selected["source_b_action"])
        ),
        "source_cf_action": int(selected["source_cf_action"]),
        "matched_source_cf_action": int(
            selected.get("matched_source_cf_action", selected["source_cf_action"])
        ),
        "source_b_action_matches_cf": int(selected["source_b_action_matches_cf"]),
        "target_unpatched_action": int(target_unpatched["action"]),
        "target_patched_action": int(target_patched["action"]),
        "source_patch_action_changed": source_patch_action_changed,
        "target_patch_action_changed": target_patch_action_changed,
        "target_patch_shift_match": int(
            target_patch_action_changed == source_patch_action_changed
        ),
        "target_interchange_action_agreement": int(
            target_patched["action"] == source_cf["action"]
        ),
        "target_unpatched_source_a_action_agreement": int(
            target_unpatched["action"] == source_a["action"]
        ),
        "target_unpatched_source_cf_action_agreement": int(
            target_unpatched["action"] == source_cf["action"]
        ),
        "target_patched_matched_reference_action_agreement": int(
            target_patched["action"] == matched_source_cf["action"]
        ),
        "source_control_matches_matched_reference_action": int(
            source_cf["action"] == matched_source_cf["action"]
        ),
        "source_patch_selection_score": float(selected["source_patch_selection_score"]),
        "source_patch_q_delta_mse": float(selected["source_patch_q_delta_mse"]),
        "source_patch_self_report_delta_l1": float(
            selected["source_patch_self_report_delta_l1"]
        ),
        "source_patch_attention_delta_l1": float(
            selected["source_patch_attention_delta_l1"]
        ),
        "source_patch_feature_delta_mse": float(
            selected["source_patch_feature_delta_mse"]
        ),
        "source_patch_schema_state_delta_mse": float(
            selected["source_patch_schema_state_delta_mse"]
        ),
        "target_patch_q_delta_mse": mse(target_delta_q),
        "target_patch_self_report_delta_l1": mean_abs(target_delta_report),
        "target_patch_attention_delta_l1": mean_abs(target_delta_attention),
        "target_patch_schema_state_delta_mse": mse(target_delta_schema_state),
        "target_patch_delta_q_mse_to_source": mse(target_delta_q - source_delta_q),
        "target_patch_delta_self_report_l1_to_source": mean_abs(
            target_delta_report - source_delta_report
        ),
        "target_patch_delta_attention_l1_to_source": mean_abs(
            target_delta_attention - source_delta_attention
        ),
        "target_patch_delta_schema_state_mse_to_source": mse(
            target_delta_schema_state - source_delta_schema_state
        ),
        "target_patched_q_mse_to_source_cf": mse(
            target_patched["q_values"] - source_cf["q_values"]
        ),
        "target_patched_self_report_l1_to_source_cf": mean_abs(
            target_patched["self_report"] - source_cf["self_report"]
        ),
        "target_patched_attention_l1_to_source_cf": mean_abs(
            target_patched["attention"] - source_cf["attention"]
        ),
        "target_patched_q_mse_to_matched_reference_cf": mse(
            target_patched["q_values"] - matched_source_cf["q_values"]
        ),
        "target_patched_self_report_l1_to_matched_reference_cf": mean_abs(
            target_patched["self_report"] - matched_source_cf["self_report"]
        ),
        "target_unpatched_q_mse_to_source_a": mse(
            target_unpatched["q_values"] - source_a["q_values"]
        ),
        "target_unpatched_self_report_l1_to_source_a": mean_abs(
            target_unpatched["self_report"] - source_a["self_report"]
        ),
        "schema_hidden_mse_target_a_to_source_a": snapshot_tensor_mse(
            source_snapshot_a,
            target_snapshot_a,
            idx=0,
        ),
    }


def source_full_rows(
    study_id: str,
    train_idx: int,
    selected_candidates: list[dict],
    vector_path: str,
) -> list[dict]:
    rows = []
    for selected in selected_candidates:
        rows.append(
            condition_row(
                study_id=study_id,
                condition="source_full",
                train_idx=train_idx,
                selected=selected,
                target_unpatched=selected["source_a"],
                target_patched=selected["source_cf"],
                target_snapshot_a=selected["context_a"]["source_snapshot"],
                source_snapshot_a=selected["context_a"]["source_snapshot"],
                vector_path=vector_path,
                obs_match=1,
            )
        )
    return rows


def target_condition_rows(
    study_id: str,
    master_seed: int,
    train_idx: int,
    condition: str,
    source_agent,
    target_agent,
    cfg,
    selected_candidates: list[dict],
    warmup_steps: int,
    vector_path: str,
) -> list[dict]:
    rows = []
    for selected in selected_candidates:
        target_context_a = advance_source_history(
            source_agent=source_agent,
            target_agent=target_agent,
            cfg=cfg,
            eval_seed=int(selected["seed_a"]),
            warmup_steps=warmup_steps,
        )
        obs_match = bool(np.allclose(target_context_a["obs"], selected["context_a"]["obs"]))

        restore_recurrent(target_agent, target_context_a["target_snapshot"])
        target_unpatched = agent_response(target_agent, selected["context_a"]["obs"], cfg)

        restore_recurrent(target_agent, target_context_a["target_snapshot"])
        if vector_path == "schema_state":
            target_patched = agent_response_with_schema_state_patch(
                target_agent,
                selected["context_a"]["obs"],
                cfg,
                donor_schema_state=selected.get("donor_source_b", selected["source_b"])[
                    "schema_state"
                ],
            )
        elif vector_path == "attention_state":
            donor_source_b = selected.get("donor_source_b", selected["source_b"])
            target_patched = agent_response_with_attention_state_patch(
                target_agent,
                selected["context_a"]["obs"],
                cfg,
                donor_attention=donor_source_b["attention"],
                donor_features=donor_source_b["features"],
            )
        else:
            restore_recurrent(
                target_agent,
                patch_snapshot(
                    target_context_a["target_snapshot"],
                    selected.get("donor_context_b", selected["context_b"])[
                        "source_snapshot"
                    ],
                    vector_path,
                ),
            )
            target_patched = agent_response(target_agent, selected["context_a"]["obs"], cfg)

        rows.append(
            condition_row(
                study_id=study_id,
                condition=condition,
                train_idx=train_idx,
                selected=selected,
                target_unpatched=target_unpatched,
                target_patched=target_patched,
                target_snapshot_a=target_context_a["target_snapshot"],
                source_snapshot_a=selected["context_a"]["source_snapshot"],
                vector_path=vector_path,
                obs_match=int(obs_match),
            )
        )
    return rows


def aggregate_rows(rows: list[dict]) -> list[dict]:
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row["condition"], row.get("donor_control", "matched"))].append(row)

    metric_names = sorted(
        {
            key
            for row in rows
            for key, value in row.items()
            if isinstance(value, (int, float))
            and key
            not in {
                "training_seed_index",
                "candidate_index",
                "source_patch_selection_rank",
                "source_patch_candidate_pool_size",
                "eval_seed_a",
                "eval_seed_b",
            }
        }
    )

    summaries = []
    for (condition, donor_control), group in sorted(grouped.items()):
        summary = {
            "condition": condition,
            "donor_control": donor_control,
            "n_rows": len(group),
            "n_source_seeds": len({row["training_seed_index"] for row in group}),
        }
        for metric in metric_names:
            summary[metric] = float(np.mean([row[metric] for row in group]))
        summaries.append(summary)
    return summaries


def markdown_report(manifest: dict, summaries: list[dict]) -> str:
    lines = [
        "# Paper 5 Causal Patching Smoke",
        "",
        "This is a toy PreservationBench-AST causal-patching smoke. It patches one source recurrent vector from context B into context A and asks whether each condition follows the source counterfactual response. It does not measure consciousness, survival, personal identity, or AST truth.",
        "",
        "## Run",
        "",
        f"- study_id: `{manifest['study_id']}`",
        f"- vector_path: `{manifest['patch']['vector_path']}`",
        f"- source_run_dir: `{manifest['source_run_dir']}`",
        f"- selected source seeds: `{manifest['seed_status']['selected_train_seed_indices']}`",
        f"- candidate pairs per seed: `{manifest['candidate_eval_pairs']}`",
        f"- selected pairs per seed: `{manifest['selected_pairs']}`",
        "",
        "## Summary",
        "",
        "| condition | n | source flip | interchange action | shift match | delta q mse to source | delta report l1 to source | patched q mse to source cf |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    by_condition = {
        (summary["condition"], summary.get("donor_control", "matched")): summary
        for summary in summaries
    }
    order = [
        "source_full",
        "b_source_align_attention_copy_long",
        "b_behavior_distill",
        "b_frozen_random",
    ]
    donor_controls = sorted(
        {summary.get("donor_control", "matched") for summary in summaries}
    )
    for donor_control in donor_controls:
        for condition in order:
            summary = by_condition.get((condition, donor_control))
            if summary is None:
                continue
            label = (
                condition
                if donor_control == "matched"
                else f"{condition}/{donor_control}"
            )
            lines.append(
                "| {condition} | {n_rows:.0f} | {source_flip:.3f} | {action:.3f} | "
                "{shift:.3f} | {q_delta:.4f} | {report_delta:.4f} | {patched_q:.4f} |".format(
                    condition=label,
                    n_rows=summary["n_rows"],
                    source_flip=summary.get("source_patch_action_changed", 0.0),
                    action=summary.get("target_interchange_action_agreement", 0.0),
                    shift=summary.get("target_patch_shift_match", 0.0),
                    q_delta=summary.get("target_patch_delta_q_mse_to_source", 0.0),
                    report_delta=summary.get(
                        "target_patch_delta_self_report_l1_to_source",
                        0.0,
                    ),
                    patched_q=summary.get("target_patched_q_mse_to_source_cf", 0.0),
                )
            )
    lines.extend(
        [
            "",
            "## Interpretation Gate",
            "",
            "- `source_full` is the within-source positive control: it should have perfect interchange agreement by construction, while the selected source pairs report whether patching had a real source-side effect.",
            "- Target rows use direct hidden-state identity patching. This is appropriate for copied schema/attention conditions but intentionally harsh for behavior-only and random controls.",
            "- A green result requires copied attention to separate from behavior distillation and frozen random on source-counterfactual agreement or source-delta distance, while behavior-only remains ordinary-behavior plausible but causally weaker.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a bounded AST causal-patching/interchange smoke."
    )
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()

    run_cfg = load_config(args.config)
    study_id = run_cfg["study_id"]
    master_seed = int(run_cfg["master_seed"])
    source_run_dir = Path(run_cfg["source_run_dir"])
    output_dir = Path(run_cfg["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    source_manifest = read_json(source_run_dir / "manifest.json")
    source_run_cfg = copy.deepcopy(source_manifest["config"])
    source_study_id = source_run_cfg["study_id"]
    source_master_seed = int(source_run_cfg["master_seed"])
    vector_path = str(run_cfg.get("patch", {}).get("vector_path", "schema_hidden"))
    conditions = list(run_cfg["conditions"])
    warmup_steps = int(run_cfg.get("warmup_steps", 8))
    candidate_eval_pairs = int(run_cfg.get("candidate_eval_pairs", 8))
    selected_pairs = int(run_cfg.get("selected_pairs", 4))
    donor_controls = list(run_cfg.get("donor_controls", ["matched"]))
    max_train_seeds = run_cfg.get("max_train_seeds")
    max_train_seeds = None if max_train_seeds is None else int(max_train_seeds)

    seed_dirs = validated_source_seed_dirs(source_run_dir, max_train_seeds)
    if not seed_dirs:
        raise SystemExit(f"No validated source seeds found under {source_run_dir}")

    rows: list[dict] = []
    seed_status = {
        "source_run_dir": str(source_run_dir),
        "source_study_id": source_study_id,
        "source_master_seed": source_master_seed,
        "selected_train_seed_indices": [],
    }

    for seed_dir in seed_dirs:
        train_idx = numeric_train_seed_index(seed_dir)
        seed_manifest = read_json(seed_dir / "manifest.json")
        source_seed = int(seed_manifest["source_seed"])
        cfg = make_cfg(source_run_cfg, source_seed)
        set_seed(cfg.seed)
        source_agent = load_source_agent(cfg, seed_dir / "source_final.pt")
        seed_status["selected_train_seed_indices"].append(train_idx)

        print(f"Selecting source patch pairs for train_seed_{train_idx}...", flush=True)
        selected_candidates, candidate_pool = select_source_candidates(
            source_agent=source_agent,
            cfg=cfg,
            study_id=study_id,
            master_seed=master_seed,
            train_idx=train_idx,
            candidate_eval_pairs=candidate_eval_pairs,
            selected_pairs=selected_pairs,
            warmup_steps=warmup_steps,
            vector_path=vector_path,
        )
        control_specs = build_control_specs(
            source_agent=source_agent,
            cfg=cfg,
            selected_candidates=selected_candidates,
            candidate_pool=candidate_pool,
            vector_path=vector_path,
            donor_controls=donor_controls,
        )
        source_flip_rate = np.mean(
            [item["source_patch_action_changed"] for item in selected_candidates]
        )
        print(
            f"Selected {len(selected_candidates)} pairs; "
            f"source_action_flip_rate={source_flip_rate:.3f}.",
            flush=True,
        )

        for condition in conditions:
            if condition == "source_full":
                print(f"Evaluating train_seed_{train_idx}/{condition}...", flush=True)
                rows.extend(
                    source_full_rows(
                        study_id=study_id,
                        train_idx=train_idx,
                        selected_candidates=control_specs,
                        vector_path=vector_path,
                    )
                )
                continue

            print(f"Evaluating train_seed_{train_idx}/{condition}...", flush=True)
            env = Arena(cfg)
            target_agent = build_condition_agent(
                name=condition,
                source_agent=source_agent,
                cfg=cfg,
                env=env,
                study_id=source_study_id,
                master_seed=source_master_seed,
                train_idx=train_idx,
            )
            target_agent.eval()
            rows.extend(
                target_condition_rows(
                    study_id=study_id,
                    master_seed=master_seed,
                    train_idx=train_idx,
                    condition=condition,
                    source_agent=source_agent,
                    target_agent=target_agent,
                    cfg=cfg,
                    selected_candidates=control_specs,
                    warmup_steps=warmup_steps,
                    vector_path=vector_path,
                )
            )

    summaries = aggregate_rows(rows)
    manifest = {
        "study_id": study_id,
        "config": run_cfg,
        "source_run_dir": str(source_run_dir),
        "seed_status": seed_status,
        "candidate_eval_pairs": candidate_eval_pairs,
        "selected_pairs": selected_pairs,
        "donor_controls": donor_controls,
        "warmup_steps": warmup_steps,
        "conditions": conditions,
        "patch": patch_metadata(vector_path),
        "primary_metrics": PRIMARY_METRICS,
        "python": sys.version,
        "platform": platform.platform(),
        "torch": torch.__version__,
        "metric_boundary": (
            "This causal-patching smoke tests toy source-counterfactual functional "
            "responses. It does not measure consciousness, survival, identity, or AST truth."
        ),
    }
    write_json(output_dir / "manifest.json", manifest)
    write_jsonl(output_dir / "causal_patch_rows.jsonl", rows)
    write_json(output_dir / "causal_patch_summary.json", summaries)
    (output_dir / "causal_patch_report.md").write_text(
        markdown_report(manifest, summaries),
        encoding="utf-8",
    )

    print("\nSummary", flush=True)
    for summary in summaries:
        label = summary["condition"]
        if summary.get("donor_control", "matched") != "matched":
            label = f"{label}/{summary['donor_control']}"
        print(
            f"{label:<60} "
            f"n={summary['n_rows']:.0f} "
            f"source_flip={summary.get('source_patch_action_changed', 0.0):.3f} "
            f"interchange_action={summary.get('target_interchange_action_agreement', 0.0):.3f} "
            f"shift_match={summary.get('target_patch_shift_match', 0.0):.3f} "
            f"delta_q_to_source={summary.get('target_patch_delta_q_mse_to_source', 0.0):.4f} "
            f"delta_report_to_source={summary.get('target_patch_delta_self_report_l1_to_source', 0.0):.4f}",
            flush=True,
        )


if __name__ == "__main__":
    main()
