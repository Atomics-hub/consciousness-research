#!/usr/bin/env python3
import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


FOCUSED_CONDITIONS = (
    ("source_full", "Source"),
    ("b_frozen_copy", "Frozen copy"),
    ("b_source_align_repair_copy_long", "Long repair"),
    ("b_source_align_attention_copy_long", "Copied attention"),
    ("b_source_align_attention_adapter_long", "Attention bridge"),
    ("b_source_align_control_adapter_long", "Control bridge"),
    ("b_behavior_distill", "Behavior distill"),
    ("b_frozen_random", "Frozen random"),
)

FOCUSED_METRICS = (
    ("self_report_corr", "Self-report corr"),
    ("goals_found", "Goals found"),
    ("source_action_agreement", "Source action agreement"),
    ("identity_probe_accuracy", "Identity probe accuracy"),
)

COLORS = {
    "source_full": "#2f5f98",
    "b_frozen_copy": "#7f7f7f",
    "b_source_align_repair_copy_long": "#4c956c",
    "b_source_align_attention_copy_long": "#2a9d8f",
    "b_source_align_attention_adapter_long": "#e9c46a",
    "b_source_align_control_adapter_long": "#e76f51",
    "b_behavior_distill": "#8e6bbd",
    "b_frozen_random": "#444444",
}


def read_json(path: Path):
    with path.open() as f:
        return json.load(f)


def parse_train_seed_index(path: Path) -> int | None:
    match = re.search(r"train_seed_(\d+)", str(path))
    if not match:
        return None
    return int(match.group(1))


def validation_counts(run_dir: Path) -> dict:
    paths = sorted(run_dir.glob("train_seed_*/source_validation.json"))
    passed = []
    failed = []
    reasons = defaultdict(int)
    for path in paths:
        train_idx = parse_train_seed_index(path)
        if train_idx is None:
            continue
        result = read_json(path)
        if result.get("passed", False):
            passed.append(train_idx)
        else:
            failed.append(train_idx)
            for reason in result.get("reasons", []):
                reasons[reason] += 1
    return {
        "attempted": len(paths),
        "passed": len(passed),
        "failed": len(failed),
        "passed_indices": passed,
        "failed_indices": failed,
        "failed_reasons": dict(reasons),
    }


def load_valid_rows(summary_json: Path, run_dir: Path) -> tuple[list[dict], dict]:
    counts = validation_counts(run_dir)
    passed = set(counts["passed_indices"])
    rows = [
        row
        for row in read_json(summary_json)
        if int(row["training_seed_index"]) in passed
    ]
    return rows, counts


def values_by_condition(rows: list[dict], metric: str) -> dict[str, list[float]]:
    values = defaultdict(list)
    for row in rows:
        if metric in row:
            values[row["condition"]].append(float(row[metric]))
    return dict(values)


def bootstrap_mean_ci(values: list[float], seed: int = 42) -> tuple[float, float, float]:
    if not values:
        return np.nan, np.nan, np.nan
    arr = np.asarray(values, dtype=float)
    if len(arr) == 1:
        mean = float(arr[0])
        return mean, mean, mean
    rng = np.random.default_rng(seed)
    means = np.empty(5000, dtype=float)
    for idx in range(len(means)):
        sample = rng.choice(arr, size=len(arr), replace=True)
        means[idx] = float(np.mean(sample))
    return (
        float(np.mean(arr)),
        float(np.quantile(means, 0.025)),
        float(np.quantile(means, 0.975)),
    )


def write_summary_json(path: Path, rows: list[dict], counts: dict) -> None:
    payload = {
        "validation": counts,
        "focused_means": {},
    }
    for metric, _label in FOCUSED_METRICS:
        metric_values = values_by_condition(rows, metric)
        payload["focused_means"][metric] = {}
        for condition, _condition_label in FOCUSED_CONDITIONS:
            mean, ci_low, ci_high = bootstrap_mean_ci(metric_values.get(condition, []))
            payload["focused_means"][metric][condition] = {
                "mean": mean,
                "ci_low": ci_low,
                "ci_high": ci_high,
            }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(payload, f, indent=2, sort_keys=True)


def plot_validation_flow(counts: dict, output: Path) -> None:
    labels = ["Attempted\nsources", "Validated\nsources", "Rejected\nsources"]
    values = [counts["attempted"], counts["passed"], counts["failed"]]
    colors = ["#2f5f98", "#2a9d8f", "#e76f51"]

    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    bars = ax.bar(labels, values, color=colors, width=0.58)
    ax.set_ylabel("source seeds")
    ax.set_title("Source Validation Flow")
    ax.set_ylim(0, max(values) + 2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.22)

    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.15,
            str(value),
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
        )

    failed = counts.get("failed_indices", [])
    if failed:
        reason_text = "Rejected seeds: " + ", ".join(str(idx) for idx in failed)
        ax.text(
            0.5,
            -0.20,
            reason_text,
            transform=ax.transAxes,
            ha="center",
            va="top",
            fontsize=10,
        )

    fig.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180)
    plt.close(fig)


def plot_focused_bars(rows: list[dict], output: Path) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(13, 8.2), sharex=True)
    axes = axes.flatten()
    x = np.arange(len(FOCUSED_CONDITIONS))
    condition_labels = [label for _condition, label in FOCUSED_CONDITIONS]
    condition_colors = [COLORS[condition] for condition, _label in FOCUSED_CONDITIONS]

    for ax, (metric, label) in zip(axes, FOCUSED_METRICS):
        metric_values = values_by_condition(rows, metric)
        means = []
        low_err = []
        high_err = []
        for condition, _condition_label in FOCUSED_CONDITIONS:
            mean, ci_low, ci_high = bootstrap_mean_ci(metric_values.get(condition, []))
            means.append(mean)
            low_err.append(max(0.0, mean - ci_low))
            high_err.append(max(0.0, ci_high - mean))

        ax.bar(
            x,
            means,
            yerr=np.vstack([low_err, high_err]),
            color=condition_colors,
            width=0.7,
            capsize=3,
            edgecolor="#222222",
            linewidth=0.4,
        )
        ax.set_title(label)
        ax.grid(axis="y", alpha=0.22)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        if metric != "reward":
            lower = min(0.0, min(v for v in means if not np.isnan(v)))
            upper = max(1.0, max(v for v in means if not np.isnan(v)))
            ax.set_ylim(lower - 0.08, upper + 0.14)

    for ax in axes[-2:]:
        ax.set_xticks(x, condition_labels, rotation=35, ha="right")
    for ax in axes[:2]:
        ax.tick_params(axis="x", labelbottom=False)

    fig.suptitle("Core Transfer Metrics, Validated Seeds", y=0.99, fontsize=15)
    fig.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot focused figures for the core AST v0 run.")
    parser.add_argument("summary_json", type=Path)
    parser.add_argument("--run-dir", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    run_dir = args.run_dir or args.summary_json.parent
    rows, counts = load_valid_rows(args.summary_json, run_dir)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    plot_validation_flow(counts, args.output_dir / "source_validation_flow.png")
    plot_focused_bars(rows, args.output_dir / "focused_transfer_metrics.png")
    write_summary_json(args.output_dir / "core_figure_values.json", rows, counts)

    print(f"Wrote {args.output_dir / 'source_validation_flow.png'}")
    print(f"Wrote {args.output_dir / 'focused_transfer_metrics.png'}")
    print(f"Wrote {args.output_dir / 'core_figure_values.json'}")


if __name__ == "__main__":
    main()
