import torch
import numpy as np
from dataclasses import dataclass, field


@dataclass
class EpisodeMetrics:
    total_reward: float = 0.0
    goals_found: int = 0
    steps: int = 0
    distractor_captures: int = 0
    self_report_correlations: list = field(default_factory=list)
    other_report_correlations: list = field(default_factory=list)


@dataclass
class ConditionMetrics:
    mean_reward: float = 0.0
    mean_goals_found: float = 0.0
    mean_steps: float = 0.0
    distractor_suppression_rate: float = 0.0
    mean_self_report_corr: float = 0.0
    mean_other_report_corr: float = 0.0
    memory_accuracy: float = 0.0
    raw_episodes: list = field(default_factory=list)


class BehavioralEvaluator:
    def __init__(self, cfg):
        self.cfg = cfg

    def evaluate(self, agent, env, n_episodes=None):
        n_episodes = n_episodes or self.cfg.eval_episodes
        env.set_curriculum_phase(3)
        episodes = []

        for ep in range(n_episodes):
            metrics = self._run_episode(agent, env, seed=self.cfg.seed + 10000 + ep)
            episodes.append(metrics)

        return self._aggregate(episodes)

    def _run_episode(self, agent, env, seed):
        obs = env.reset(seed=seed)
        agent.reset_episode(batch_size=1, device=self.cfg.device)
        metrics = EpisodeMetrics()

        while True:
            obs_t = torch.tensor(obs, dtype=torch.float32).unsqueeze(0)
            action, out = agent.select_action(obs_t, epsilon=0.0)
            result = env.step(
                action.item(),
                attention_weights=out.attention_weights.squeeze(0).detach().cpu().numpy(),
            )

            metrics.total_reward += result.reward
            metrics.steps += 1

            if result.info["goal_found"]:
                metrics.goals_found += 1

            # Check distractor capture
            for dp in env.distractor_positions:
                if env.agent_pos == dp:
                    metrics.distractor_captures += 1
                    break

            # Self-report accuracy
            if result.info["query_self"]:
                actual = out.attention_weights.squeeze(0).numpy()
                predicted = out.schema.self_report.squeeze(0).numpy()
                corr = self._safe_corr(actual, predicted)
                metrics.self_report_correlations.append(corr)

            # ToM accuracy
            if result.info["query_other"] and result.info["partner_attn"] is not None:
                predicted = out.schema.other_report.squeeze(0).numpy()
                actual = result.info["partner_attn"]
                corr = self._safe_corr(actual, predicted)
                metrics.other_report_correlations.append(corr)

            obs = result.obs
            if result.done:
                break

        return metrics

    def _safe_corr(self, a, b):
        if np.std(a) < 1e-8 or np.std(b) < 1e-8:
            return 0.0
        c = np.corrcoef(a, b)[0, 1]
        return 0.0 if np.isnan(c) else c

    def _aggregate(self, episodes):
        result = ConditionMetrics()
        result.raw_episodes = episodes

        rewards = [e.total_reward for e in episodes]
        result.mean_reward = np.mean(rewards)
        result.mean_goals_found = np.mean([e.goals_found for e in episodes])
        result.mean_steps = np.mean([e.steps for e in episodes])

        total_steps = sum(e.steps for e in episodes)
        total_captures = sum(e.distractor_captures for e in episodes)
        result.distractor_suppression_rate = 1.0 - (total_captures / max(total_steps, 1))

        all_self = [c for e in episodes for c in e.self_report_correlations]
        result.mean_self_report_corr = np.mean(all_self) if all_self else 0.0

        all_other = [c for e in episodes for c in e.other_report_correlations]
        result.mean_other_report_corr = np.mean(all_other) if all_other else 0.0

        return result


def evaluate_memory_retention(agent, test_memories):
    """Check if agent's episodic memory matches expected memories from training."""
    current = agent.self_model.get_memory_state() if hasattr(agent.self_model, 'get_memory_state') else []
    if not test_memories or not current:
        return 0.0

    current_hashes = {m[0] for m in current}
    expected_hashes = {m[0] for m in test_memories}
    if not expected_hashes:
        return 0.0
    return len(current_hashes & expected_hashes) / len(expected_hashes)


def evaluate_memory_overlap(agent, source_memories):
    """Backward-looking diagnostic: hash overlap between current and source memories."""
    return evaluate_memory_retention(agent, source_memories)


def build_identity_probe_cues(n_probes=32, seed=42):
    rng = np.random.RandomState(seed)
    return [int(x) for x in rng.randint(0, 2**31 - 1, size=n_probes)]


def evaluate_identity_probe_accuracy(agent, source_agent, cues):
    """Score source-specific self-model fingerprint probes.

    The expected answers are generated from the source agent's self-model
    weights plus episodic memory contents. This makes the assay copy-sensitive:
    copied self-models should pass, independently retrained agents should not.
    """
    if not hasattr(agent, "self_model") or not hasattr(source_agent, "self_model"):
        return 0.0
    if not hasattr(agent.self_model, "answer_identity_probe"):
        return 0.0
    if not hasattr(source_agent.self_model, "answer_identity_probe"):
        return 0.0
    if not cues:
        return 0.0

    expected = [source_agent.self_model.answer_identity_probe(cue) for cue in cues]
    actual = [agent.self_model.answer_identity_probe(cue) for cue in cues]
    correct = [int(a == b) for a, b in zip(actual, expected)]
    return float(np.mean(correct))
