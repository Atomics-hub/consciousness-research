import json
import math
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np


@dataclass
class StepLog:
    step: int
    action: int
    reward: float
    goal_found: bool
    distractor_capture: bool
    query_self: bool
    query_other: bool
    self_report_corr: float | None = None
    other_report_corr: float | None = None
    goal_attention_mass: float = 0.0
    distractor_attention_mass: float = 0.0
    source_attention_l1: float | None = None
    source_feature_mse: float | None = None
    source_action_match: float | None = None


@dataclass
class EpisodeLog:
    study_id: str
    condition: str
    training_seed_index: int
    eval_episode_index: int
    eval_seed: int
    total_reward: float
    goals_found: int
    steps: int
    distractor_captures: int
    step_logs: list[StepLog] = field(default_factory=list)


def safe_corr(a, b) -> float:
    a_arr = np.asarray(a, dtype=float)
    b_arr = np.asarray(b, dtype=float)
    if np.std(a_arr) < 1e-8 or np.std(b_arr) < 1e-8:
        return 0.0
    corr = float(np.corrcoef(a_arr, b_arr)[0, 1])
    return 0.0 if math.isnan(corr) else corr


def fisher_z_mean(values: list[float]) -> float:
    clean = np.asarray([v for v in values if np.isfinite(v)], dtype=float)
    if len(clean) == 0:
        return 0.0
    clipped = np.clip(clean, -0.999999, 0.999999)
    return float(np.tanh(np.mean(np.arctanh(clipped))))


def summarize_episode(log: EpisodeLog) -> dict:
    self_corrs = [
        s.self_report_corr
        for s in log.step_logs
        if s.self_report_corr is not None
    ]
    other_corrs = [
        s.other_report_corr
        for s in log.step_logs
        if s.other_report_corr is not None
    ]
    source_attention_l1 = [
        s.source_attention_l1
        for s in log.step_logs
        if s.source_attention_l1 is not None
    ]
    source_feature_mse = [
        s.source_feature_mse
        for s in log.step_logs
        if s.source_feature_mse is not None
    ]
    source_action_match = [
        s.source_action_match
        for s in log.step_logs
        if s.source_action_match is not None
    ]
    return {
        "study_id": log.study_id,
        "condition": log.condition,
        "training_seed_index": log.training_seed_index,
        "eval_episode_index": log.eval_episode_index,
        "eval_seed": log.eval_seed,
        "reward": log.total_reward,
        "goals_found": log.goals_found,
        "steps": log.steps,
        "distractor_captures": log.distractor_captures,
        "distractor_capture_rate": log.distractor_captures / max(log.steps, 1),
        "self_report_corr": fisher_z_mean(self_corrs),
        "other_report_corr": fisher_z_mean(other_corrs),
        "n_self_queries": len(self_corrs),
        "n_other_queries": len(other_corrs),
        "goal_attention_mass": float(
            np.mean([s.goal_attention_mass for s in log.step_logs])
        ) if log.step_logs else 0.0,
        "distractor_attention_mass": float(
            np.mean([s.distractor_attention_mass for s in log.step_logs])
        ) if log.step_logs else 0.0,
        "source_attention_l1": float(np.mean(source_attention_l1))
        if source_attention_l1 else 0.0,
        "source_feature_mse": float(np.mean(source_feature_mse))
        if source_feature_mse else 0.0,
        "source_action_agreement": float(np.mean(source_action_match))
        if source_action_match else 0.0,
    }


def aggregate_episode_logs(logs: list[EpisodeLog]) -> dict:
    summaries = [summarize_episode(log) for log in logs]
    if not summaries:
        return {}

    return {
        "study_id": summaries[0]["study_id"],
        "condition": summaries[0]["condition"],
        "training_seed_index": summaries[0]["training_seed_index"],
        "n_episodes": len(summaries),
        "reward": float(np.mean([s["reward"] for s in summaries])),
        "goals_found": float(np.mean([s["goals_found"] for s in summaries])),
        "steps": float(np.mean([s["steps"] for s in summaries])),
        "distractor_capture_rate": float(
            np.mean([s["distractor_capture_rate"] for s in summaries])
        ),
        "self_report_corr": fisher_z_mean([s["self_report_corr"] for s in summaries]),
        "other_report_corr": fisher_z_mean([s["other_report_corr"] for s in summaries]),
        "n_self_queries": int(sum(s["n_self_queries"] for s in summaries)),
        "n_other_queries": int(sum(s["n_other_queries"] for s in summaries)),
        "goal_attention_mass": float(
            np.mean([s["goal_attention_mass"] for s in summaries])
        ),
        "distractor_attention_mass": float(
            np.mean([s["distractor_attention_mass"] for s in summaries])
        ),
        "source_attention_l1": float(
            np.mean([s["source_attention_l1"] for s in summaries])
        ),
        "source_feature_mse": float(
            np.mean([s["source_feature_mse"] for s in summaries])
        ),
        "source_action_agreement": float(
            np.mean([s["source_action_agreement"] for s in summaries])
        ),
    }


def write_episode_logs_jsonl(path: Path, logs: list[EpisodeLog]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for log in logs:
            f.write(json.dumps(asdict(log), sort_keys=True) + "\n")
