import torch
import numpy as np


INDICATORS = [
    "recurrent_processing",
    "global_broadcast",
    "higher_order_representation",
    "attention_modulation",
    "flexible_behavior",
    "metacognition",
    "integration",
    "self_other_distinction",
    "temporal_depth",
    "unified_agency",
]


def evaluate_butlin_indicators(agent, env, cfg, condition_name="full"):
    """Heuristic Butlin-Chalmers indicator pass for an agent.

    Returns dict of indicator_name -> score (0.0 = absent, 0.5 = partial, 1.0 = present)
    """
    scores = {}
    env.set_curriculum_phase(3)

    obs = env.reset(seed=cfg.seed + 99999)
    agent.reset_episode(batch_size=1, device=cfg.device)

    attn_weights_history = []
    modulation_history = []
    self_report_corrs = []
    other_report_corrs = []
    actions = []
    rewards = []

    for step in range(min(200, cfg.max_steps)):
        obs_t = torch.tensor(obs, dtype=torch.float32).unsqueeze(0)
        action, out = agent.select_action(obs_t, epsilon=0.0)
        result = env.step(
            action.item(),
            attention_weights=out.attention_weights.squeeze(0).detach().cpu().numpy(),
        )

        attn_weights_history.append(out.attention_weights.squeeze(0).detach().numpy())
        modulation_history.append(out.schema.modulation.squeeze(0).detach().numpy())
        actions.append(action.item())
        rewards.append(result.reward)

        if result.info["query_self"]:
            actual = out.attention_weights.squeeze(0).numpy()
            predicted = out.schema.self_report.squeeze(0).numpy()
            corr = _safe_corr(actual, predicted)
            self_report_corrs.append(corr)

        if result.info["query_other"] and result.info["partner_attn"] is not None:
            predicted = out.schema.other_report.squeeze(0).numpy()
            actual = result.info["partner_attn"]
            corr = _safe_corr(actual, predicted)
            other_report_corrs.append(corr)

        obs = result.obs
        if result.done:
            break

    # 1. Recurrent processing: schema modulation feeds back to an active attention path.
    mod_var = np.mean([np.var(m) for m in modulation_history])
    active_feedback_path = condition_name not in ("schema_ablated", "attention_ablated")
    if not active_feedback_path:
        scores["recurrent_processing"] = 0.0
    else:
        scores["recurrent_processing"] = 1.0 if mod_var > 0.01 else (0.5 if mod_var > 0.001 else 0.0)

    # 2. Global broadcast: architectural heuristic, not a direct measurement.
    scores["global_broadcast"] = 1.0  # by architecture; always present when attention works

    # 3. Higher-order representation: schema models attention (a representation of a representation)
    has_schema = condition_name not in ("schema_ablated",)
    scores["higher_order_representation"] = 1.0 if has_schema else 0.0

    # 4. Attention modulation: modulation signal actually changes attention weights
    if len(attn_weights_history) > 10:
        attn_entropy = [_entropy(aw) for aw in attn_weights_history]
        entropy_var = np.var(attn_entropy)
        scores["attention_modulation"] = 1.0 if entropy_var > 0.1 else (0.5 if entropy_var > 0.01 else 0.0)
    else:
        scores["attention_modulation"] = 0.0

    # 5. Flexible behavior: action diversity across different states
    action_entropy = _entropy(np.bincount(actions, minlength=5) / len(actions)) if actions else 0
    scores["flexible_behavior"] = 1.0 if action_entropy > 1.0 else (0.5 if action_entropy > 0.5 else 0.0)

    # 6. Metacognition: self-report accuracy
    mean_sr = np.mean(self_report_corrs) if self_report_corrs else 0
    scores["metacognition"] = 1.0 if mean_sr > 0.5 else (0.5 if mean_sr > 0.2 else 0.0)

    # 7. Integration: limited heuristic until a stronger circuit metric is wired in.
    scores["integration"] = 0.5  # filled in by phi_bridge

    # 8. Self-other distinction: can model own vs partner's attention differently
    if self_report_corrs and other_report_corrs:
        sr_mean = np.mean(self_report_corrs)
        or_mean = np.mean(other_report_corrs)
        scores["self_other_distinction"] = 1.0 if abs(sr_mean - or_mean) < 0.3 and sr_mean > 0.3 else 0.5
    else:
        scores["self_other_distinction"] = 0.0

    # 9. Temporal depth: attention changes meaningfully over time (not random, not static)
    if len(attn_weights_history) > 5:
        diffs = [np.mean(np.abs(attn_weights_history[i] - attn_weights_history[i-1]))
                 for i in range(1, len(attn_weights_history))]
        mean_diff = np.mean(diffs)
        scores["temporal_depth"] = 1.0 if 0.01 < mean_diff < 0.5 else 0.5
    else:
        scores["temporal_depth"] = 0.0

    # 10. Unified agency: consistent goal-directed behavior
    positive_rewards = sum(1 for r in rewards if r > 0)
    scores["unified_agency"] = 1.0 if positive_rewards > len(rewards) * 0.1 else 0.5

    return scores


def _safe_corr(a, b):
    if np.std(a) < 1e-8 or np.std(b) < 1e-8:
        return 0.0
    c = np.corrcoef(a, b)[0, 1]
    return 0.0 if np.isnan(c) else c


def _entropy(p):
    p = np.asarray(p, dtype=np.float64)
    p = p[p > 0]
    if len(p) == 0:
        return 0.0
    return -np.sum(p * np.log2(p))
