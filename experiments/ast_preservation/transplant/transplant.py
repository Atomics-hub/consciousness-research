import torch
import copy
from ..agent.full_agent import FullAgent
from .substrate_b import SubstrateBAgent
from ..training.trainer import compute_auxiliary_losses, detach_agent_state


def extract_copied_state(agent):
    """Extract the copied-state payload from a trained agent.

    Returns a dict containing:
    - schema weights
    - self-model weights
    - episodic memory buffer
    """
    return {
        "schema": copy.deepcopy(agent.schema.state_dict()),
        "self_model_weights": copy.deepcopy(agent.self_model.state_dict()),
        "memory": agent.self_model.get_memory_state(),
    }


def transplant_schema(source_agent, target_agent, freeze_copied_state=True):
    """Transplant schema + self-model from source into target.

    Args:
        source_agent: trained FullAgent (Substrate A)
        target_agent: SubstrateBAgent or FullAgent (new substrate)
        freeze_copied_state: if True, freeze schema + self-model params
    Returns:
        target_agent with transplanted schema and self-model
    """
    copied_state = extract_copied_state(source_agent)

    target_agent.schema.load_state_dict(copied_state["schema"])
    target_agent.self_model.load_state_dict(copied_state["self_model_weights"])
    target_agent.self_model.load_memory_state(copied_state["memory"])

    if freeze_copied_state:
        for param in target_agent.schema.parameters():
            param.requires_grad = False
        for param in target_agent.self_model.parameters():
            param.requires_grad = False

    return target_agent


def create_transplant_conditions(trained_agent, cfg):
    """Create all four transplant conditions for the experiment.

    Returns:
        dict of condition_name -> agent
    """
    conditions = {}

    # 1. Transplant: schema + self-model from A into Substrate B
    transplanted = SubstrateBAgent(cfg)
    transplant_schema(trained_agent, transplanted, freeze_copied_state=True)
    conditions["transplant"] = transplanted

    # 2. Random control: Substrate B with random schema + self-model
    random_ctrl = SubstrateBAgent(cfg)
    conditions["random_control"] = random_ctrl

    # 3. Architecture-matched: schema + self-model from A into new Substrate A
    arch_match = FullAgent(cfg)
    transplant_schema(trained_agent, arch_match, freeze_copied_state=True)
    conditions["arch_matched"] = arch_match

    return conditions


def finetune_transplanted(agent, env, cfg):
    """Fine-tune only the trainable parts (adapters + DQN head) of a transplanted agent.
    Maintains GRU hidden state across steps within episodes (not resetting every step)."""
    trainable_params = [p for p in agent.parameters() if p.requires_grad]
    optimizer = torch.optim.Adam(trainable_params, lr=cfg.lr)

    env.set_curriculum_phase(3)
    episode_rewards = []

    step = 0
    while step < cfg.finetune_steps:
        obs = env.reset()
        agent.reset_episode(batch_size=1, device=cfg.device)
        ep_reward = 0

        while True:
            obs_t = torch.tensor(obs, dtype=torch.float32).unsqueeze(0)
            eps = max(0.1, 1.0 - step / cfg.finetune_steps)

            out = agent(obs_t)
            if torch.rand(1).item() < eps:
                action_int = torch.randint(0, cfg.n_actions, (1,)).item()
            else:
                action_int = out.q_values.argmax(dim=-1).item()

            result = env.step(
                action_int,
                attention_weights=out.attention_weights.squeeze(0).detach().cpu().numpy(),
            )

            # Compute target without resetting hidden state
            saved_hidden = agent.schema_hidden
            saved_mod = agent.last_modulation
            next_obs_t = torch.tensor(result.obs, dtype=torch.float32).unsqueeze(0)
            with torch.no_grad():
                next_out = agent(next_obs_t)
                next_q = next_out.q_values.max(dim=1)[0]
                target = result.reward + cfg.gamma * next_q * (1 - float(result.done))
            # Restore hidden state (target computation was speculative)
            agent.schema_hidden = saved_hidden
            agent.last_modulation = saved_mod

            q = out.q_values[0, action_int]
            td_loss = torch.nn.functional.smooth_l1_loss(q.unsqueeze(0), target)
            report_loss, tom_loss = compute_auxiliary_losses(out, result.info, cfg)
            loss = td_loss + cfg.report_loss_weight * (report_loss + tom_loss)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            detach_agent_state(agent)

            ep_reward += result.reward
            obs = result.obs
            step += 1

            if result.done or step >= cfg.finetune_steps:
                break

        episode_rewards.append(ep_reward)

    return episode_rewards
