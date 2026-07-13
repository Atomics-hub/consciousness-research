#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


CONDITION_LABELS = {
    "source_full": "Source",
    "b_source_align_attention_copy_long": "Copied attention",
    "b_behavior_distill": "Behavior distill",
    "b_frozen_random": "Frozen random",
}

CONDITION_ORDER = [
    "source_full",
    "b_source_align_attention_copy_long",
    "b_behavior_distill",
    "b_frozen_random",
]

COLORS = {
    "source_full": "#4d4d4d",
    "b_source_align_attention_copy_long": "#277da1",
    "b_behavior_distill": "#f3722c",
    "b_frozen_random": "#90be6d",
}


def load_json(path: Path):
    with path.open() as f:
        return json.load(f)


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else float("nan")


def summary_lookup(contrasts: dict) -> dict[tuple[str, str], dict]:
    return {
        (item["condition"], item["donor_control"]): item
        for item in contrasts["summaries"]
    }


def paired_delta_lookup(contrasts: dict) -> dict[tuple[str, str, str], dict]:
    return {
        (item["donor_control"], item["baseline_condition"], item["metric"]): item
        for item in contrasts["paired_seed_deltas"]
    }


def save_figure(fig, output_base: Path) -> None:
    output_base.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_base.with_suffix(".png"), dpi=200, bbox_inches="tight")
    fig.savefig(output_base.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)


def plot_action_mismatch_specificity(contrasts: dict, output_dir: Path) -> None:
    lookup = summary_lookup(contrasts)
    conditions = CONDITION_ORDER
    x = np.arange(len(conditions))
    width = 0.26

    donor_values = [
        lookup[(condition, "action_mismatch")]["target_interchange_action_agreement"]
        for condition in conditions
    ]
    matched_values = [
        lookup[(condition, "action_mismatch")][
            "target_patched_matched_reference_action_agreement"
        ]
        for condition in conditions
    ]
    gap_values = [
        lookup[(condition, "action_mismatch")]["causal_specificity_gap_action"]
        for condition in conditions
    ]

    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    ax.bar(x - width, donor_values, width, color="#277da1", label="Donor action")
    ax.bar(x, matched_values, width, color="#f3722c", label="Matched reference")
    ax.bar(x + width, gap_values, width, color="#577590", label="Specificity gap")
    ax.axhline(0, color="#222222", linewidth=0.8)
    ax.set_ylim(-0.15, 1.05)
    ax.set_ylabel("Agreement / gap")
    ax.set_title("Action-mismatch causal specificity, full 22-source panel")
    ax.set_xticks(x)
    ax.set_xticklabels([CONDITION_LABELS[condition] for condition in conditions])
    ax.legend(frameon=False, ncols=3, loc="upper center", bbox_to_anchor=(0.5, 1.12))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    save_figure(fig, output_dir / "fig1_action_mismatch_specificity_full22")


def plot_paired_deltas(contrasts: dict, output_dir: Path) -> None:
    lookup = paired_delta_lookup(contrasts)
    metrics = [
        ("target_interchange_action_agreement", "Action agreement", False),
        ("target_patch_delta_q_mse_to_source", "Q-delta error", True),
        ("target_patch_delta_self_report_l1_to_source", "Report-delta error", True),
        ("target_patched_q_mse_to_source_cf", "Patched Q error", True),
    ]
    donors = ["matched", "action_mismatch", "same_action"]
    baselines = ["b_behavior_distill", "b_frozen_random"]

    fig, axes = plt.subplots(2, 2, figsize=(9.2, 6.8))
    axes = axes.ravel()
    for ax, (metric, title, lower_is_better) in zip(axes, metrics):
        labels = []
        means = []
        lows = []
        highs = []
        colors = []
        for donor in donors:
            for baseline in baselines:
                item = lookup[(donor, baseline, metric)]
                labels.append(
                    donor.replace("_", " ") + "\nvs "
                    + ("behavior" if baseline == "b_behavior_distill" else "random")
                )
                means.append(item["mean_delta"])
                lows.append(item["mean_delta_ci95_low"])
                highs.append(item["mean_delta_ci95_high"])
                colors.append(
                    "#277da1"
                    if baseline == "b_behavior_distill"
                    else "#90be6d"
                )
        x = np.arange(len(labels))
        lower_err = [m - low for m, low in zip(means, lows)]
        upper_err = [high - m for m, high in zip(means, highs)]
        ax.bar(x, means, color=colors)
        ax.errorbar(
            x,
            means,
            yerr=[lower_err, upper_err],
            fmt="none",
            ecolor="#222222",
            elinewidth=1.0,
            capsize=3,
        )
        ax.axhline(0, color="#222222", linewidth=0.8)
        ax.set_title(title + (" (lower better)" if lower_is_better else ""))
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    fig.suptitle("Copied attention minus baselines, source-seed paired deltas")
    fig.tight_layout()
    save_figure(fig, output_dir / "fig2_paired_seed_deltas_full22")


def plot_source_leverage(rows: list[dict], output_dir: Path) -> None:
    by_seed = defaultdict(list)
    mismatch_by_seed = defaultdict(list)
    for row in rows:
        if row["condition"] != "source_full":
            continue
        if row["donor_control"] == "matched":
            by_seed[int(row["training_seed_index"])].append(row)
        elif row["donor_control"] == "action_mismatch":
            mismatch_by_seed[int(row["training_seed_index"])].append(row)

    seeds = sorted(by_seed)
    flip_rates = [
        mean([float(row["source_patch_action_changed"]) for row in by_seed[seed]])
        for seed in seeds
    ]
    mismatch_counts = [len(mismatch_by_seed[seed]) for seed in seeds]

    fig, ax1 = plt.subplots(figsize=(9.5, 4.8))
    x = np.arange(len(seeds))
    ax1.bar(x, flip_rates, color="#277da1", label="Matched source action flip rate")
    ax1.set_ylim(0, 1.05)
    ax1.set_ylabel("Flip rate")
    ax1.set_xticks(x)
    ax1.set_xticklabels([str(seed) for seed in seeds], rotation=90)
    ax1.set_xlabel("Training seed index")
    ax2 = ax1.twinx()
    ax2.plot(x, mismatch_counts, color="#f3722c", marker="o", linewidth=1.5)
    ax2.set_ylim(0, 8.5)
    ax2.set_ylabel("Action-mismatch donors")
    ax1.set_title("Source-level causal leverage and mismatch donor availability")
    ax1.spines["top"].set_visible(False)
    ax2.spines["top"].set_visible(False)
    fig.tight_layout()
    save_figure(fig, output_dir / "fig3_source_leverage_full22")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Plot Paper 5 causal patch full-panel results."
    )
    parser.add_argument("--contrasts", type=Path, required=True)
    parser.add_argument("--rows", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    contrasts = load_json(args.contrasts)
    rows = load_jsonl(args.rows)
    plot_action_mismatch_specificity(contrasts, args.output_dir)
    plot_paired_deltas(contrasts, args.output_dir)
    plot_source_leverage(rows, args.output_dir)
    print(f"wrote figures to {args.output_dir}")


if __name__ == "__main__":
    main()
