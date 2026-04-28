from dataclasses import dataclass, field


@dataclass(frozen=True)
class ValidationResult:
    passed: bool
    reasons: list[str] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)


def validate_source_summary(summary: dict, validation_cfg: dict) -> ValidationResult:
    if not validation_cfg.get("enabled", True):
        return ValidationResult(passed=True, metrics={"validation_enabled": False})

    min_self_report = float(validation_cfg.get("min_self_report_corr", 0.5))
    min_self_queries = int(validation_cfg.get("min_self_queries", 1))
    min_reward = float(validation_cfg.get("min_reward", -1e9))
    min_goals_found = float(validation_cfg.get("min_goals_found", -1e9))
    require_memory = bool(validation_cfg.get("require_memory", False))

    self_report = float(summary.get("self_report_corr", 0.0))
    self_queries = int(summary.get("n_self_queries", 0))
    reward = float(summary.get("reward", 0.0))
    goals_found = float(summary.get("goals_found", 0.0))
    memory_overlap = float(summary.get("memory_overlap", 0.0))

    reasons = []
    if self_report < min_self_report:
        reasons.append(
            f"self_report_corr {self_report:.3f} < min_self_report_corr {min_self_report:.3f}"
        )
    if self_queries < min_self_queries:
        reasons.append(f"n_self_queries {self_queries} < min_self_queries {min_self_queries}")
    if reward < min_reward:
        reasons.append(f"reward {reward:.3f} < min_reward {min_reward:.3f}")
    if goals_found < min_goals_found:
        reasons.append(f"goals_found {goals_found:.3f} < min_goals_found {min_goals_found:.3f}")
    if require_memory and memory_overlap <= 0.0:
        reasons.append("source memory is empty")

    return ValidationResult(
        passed=not reasons,
        reasons=reasons,
        metrics={
            "self_report_corr": self_report,
            "n_self_queries": self_queries,
            "reward": reward,
            "goals_found": goals_found,
            "memory_overlap": memory_overlap,
            "min_self_report_corr": min_self_report,
            "min_self_queries": min_self_queries,
            "min_reward": min_reward,
            "min_goals_found": min_goals_found,
            "require_memory": require_memory,
        },
    )
