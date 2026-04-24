import numpy as np
from scipy import stats as sp_stats
from dataclasses import dataclass


@dataclass
class ComparisonResult:
    metric: str
    condition_a: str
    condition_b: str
    mean_a: float
    mean_b: float
    effect_size: float  # Cohen's d
    p_value: float
    ci_low: float
    ci_high: float
    significant: bool


def cohens_d(a, b):
    """Paired Cohen's d: effect size on the differences."""
    a, b = np.asarray(a), np.asarray(b)
    if len(a) < 2 or len(b) < 2:
        return 0.0
    diffs = a - b
    sd = np.std(diffs, ddof=1)
    if sd < 1e-10:
        return 0.0
    return np.mean(diffs) / sd


def bootstrap_ci(data, n_bootstrap=10000, ci=0.95, seed=42):
    rng = np.random.RandomState(seed)
    means = np.array([np.mean(rng.choice(data, len(data), replace=True)) for _ in range(n_bootstrap)])
    alpha = (1 - ci) / 2
    return np.percentile(means, alpha * 100), np.percentile(means, (1 - alpha) * 100)


def compare_conditions(conditions_metrics, metric_name, alpha=0.05, n_comparisons=6):
    """Compare all pairs of conditions on a given metric.

    Args:
        conditions_metrics: dict of condition_name -> ConditionMetrics
        metric_name: attribute name on ConditionMetrics (e.g., 'mean_reward')
        alpha: significance level before correction
        n_comparisons: number of comparisons for Bonferroni correction
    Returns:
        list of ComparisonResult
    """
    corrected_alpha = alpha / n_comparisons
    results = []
    names = sorted(conditions_metrics.keys())

    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a_name, b_name = names[i], names[j]
            a_metrics = conditions_metrics[a_name]
            b_metrics = conditions_metrics[b_name]

            a_vals = _extract_per_episode(a_metrics, metric_name)
            b_vals = _extract_per_episode(b_metrics, metric_name)

            if len(a_vals) < 2 or len(b_vals) < 2:
                continue

            # Wilcoxon signed-rank paired test. Episodes share seeds.
            try:
                w_stat, p_val = sp_stats.wilcoxon(a_vals, b_vals, alternative='two-sided')
            except ValueError:
                # Fallback if all differences are zero
                p_val = 1.0
            d = cohens_d(a_vals, b_vals)
            diff = np.array(a_vals) - np.mean(b_vals)  # difference from b mean
            ci_lo, ci_hi = bootstrap_ci(a_vals)

            results.append(ComparisonResult(
                metric=metric_name,
                condition_a=a_name,
                condition_b=b_name,
                mean_a=np.mean(a_vals),
                mean_b=np.mean(b_vals),
                effect_size=d,
                p_value=p_val,
                ci_low=ci_lo,
                ci_high=ci_hi,
                significant=p_val < corrected_alpha,
            ))

    return results


def _extract_per_episode(metrics, metric_name):
    """Extract per-episode values for a metric."""
    episodes = metrics.raw_episodes

    if metric_name == "reward":
        return [e.total_reward for e in episodes]
    elif metric_name == "goals_found":
        return [e.goals_found for e in episodes]
    elif metric_name == "steps":
        return [e.steps for e in episodes]
    elif metric_name == "self_report_corr":
        return [np.mean(e.self_report_correlations) if e.self_report_correlations else 0.0 for e in episodes]
    elif metric_name == "other_report_corr":
        return [np.mean(e.other_report_correlations) if e.other_report_correlations else 0.0 for e in episodes]
    elif metric_name == "distractor_captures":
        return [e.distractor_captures for e in episodes]
    else:
        raise ValueError(f"Unknown metric: {metric_name}")


def format_results_table(all_results):
    """Format comparison results as a markdown table."""
    lines = ["| Metric | A vs B | Mean A | Mean B | Cohen's d | p-value | Sig |",
             "|--------|--------|--------|--------|-----------|---------|-----|"]
    for r in all_results:
        sig = "***" if r.significant else ""
        lines.append(
            f"| {r.metric} | {r.condition_a} vs {r.condition_b} | "
            f"{r.mean_a:.3f} | {r.mean_b:.3f} | {r.effect_size:.2f} | "
            f"{r.p_value:.4f} | {sig} |"
        )
    return "\n".join(lines)
