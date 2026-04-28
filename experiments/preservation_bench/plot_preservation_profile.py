#!/usr/bin/env python3
import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


DEFAULT_CONDITIONS = (
    "source_full",
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
    "b_behavior_distill",
    "b_frozen_random",
)

DEFAULT_METRICS = (
    "reward",
    "goals_found",
    "goal_attention_mass",
    "self_report_corr",
    "source_action_agreement",
    "identity_probe_accuracy",
)


def load_rows(path: Path) -> list[dict]:
    return json.loads(path.read_text())


def parse_train_seed_index(path: Path) -> int | None:
    match = re.search(r"train_seed_(\d+)", str(path))
    if not match:
        return None
    return int(match.group(1))


def load_validated_seed_indices(summary_json: Path, run_dir: Path | None) -> set[int]:
    base_dir = run_dir or summary_json.parent
    validation_paths = sorted(base_dir.glob("train_seed_*/source_validation.json"))
    if not validation_paths and (base_dir / "source_validation.json").exists():
        validation_paths = [base_dir / "source_validation.json"]

    passed = set()
    for path in validation_paths:
        train_idx = parse_train_seed_index(path)
        if train_idx is None:
            continue
        result = json.loads(path.read_text())
        if bool(result.get("passed", False)):
            passed.add(train_idx)
    if not passed:
        raise SystemExit(f"No passed source validation files found under {base_dir}")
    return passed


def mean_by_condition(rows: list[dict], metric: str) -> dict[str, float]:
    values = defaultdict(list)
    for row in rows:
        if metric in row:
            values[row["condition"]].append(float(row[metric]))
    return {condition: float(np.mean(vals)) for condition, vals in values.items() if vals}


def normalized_scores(rows: list[dict], conditions: list[str], metrics: list[str]) -> np.ndarray:
    scores = np.zeros((len(metrics), len(conditions)), dtype=float)
    for row_idx, metric in enumerate(metrics):
        means = mean_by_condition(rows, metric)
        source = means.get("source_full", 0.0)
        random = means.get("b_frozen_random", 0.0)
        denom = source - random
        for col_idx, condition in enumerate(conditions):
            value = means.get(condition, np.nan)
            if np.isnan(value):
                scores[row_idx, col_idx] = np.nan
            elif abs(denom) < 1e-12:
                scores[row_idx, col_idx] = 0.0
            else:
                scores[row_idx, col_idx] = (value - random) / denom
    return scores


def plot_profile(rows: list[dict], conditions: list[str], metrics: list[str], output: Path) -> None:
    scores = normalized_scores(rows, conditions, metrics)
    color_scores = np.clip(scores, 0.0, 1.0)

    fig, ax = plt.subplots(figsize=(max(8, len(conditions) * 1.6), max(4, len(metrics) * 1.1)))
    image = ax.imshow(color_scores, vmin=0.0, vmax=1.0, cmap="viridis", aspect="auto")

    ax.set_xticks(np.arange(len(conditions)), labels=conditions, rotation=35, ha="right")
    ax.set_yticks(np.arange(len(metrics)), labels=metrics)
    ax.set_title("Normalized Preservation Profile")

    for row_idx in range(len(metrics)):
        for col_idx in range(len(conditions)):
            value = scores[row_idx, col_idx]
            label = "na" if np.isnan(value) else f"{value:.2f}"
            ax.text(col_idx, row_idx, label, ha="center", va="center", color="white")

    cbar = fig.colorbar(image, ax=ax)
    cbar.set_label("normalized score")
    fig.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot a PreservationBench profile heatmap.")
    parser.add_argument("summary_json", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--conditions", nargs="*", default=list(DEFAULT_CONDITIONS))
    parser.add_argument("--metrics", nargs="*", default=list(DEFAULT_METRICS))
    parser.add_argument(
        "--validated-only",
        action="store_true",
        help="Only include training seeds whose source_validation.json passed.",
    )
    parser.add_argument(
        "--run-dir",
        type=Path,
        default=None,
        help="Run directory containing train_seed_*/source_validation.json.",
    )
    args = parser.parse_args()

    rows = load_rows(args.summary_json)
    if args.validated_only:
        passed = load_validated_seed_indices(args.summary_json, args.run_dir)
        rows = [row for row in rows if int(row["training_seed_index"]) in passed]

    plot_profile(rows, list(args.conditions), list(args.metrics), args.output)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
