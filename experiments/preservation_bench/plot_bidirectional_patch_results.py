#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


CONDITION_ORDER = [
    "source_full",
    "b_source_align_attention_copy_long",
    "b_behavior_distill",
    "b_frozen_random",
]

CONDITION_LABELS = {
    "source_full": "Source",
    "b_source_align_attention_copy_long": "Copied attention",
    "b_behavior_distill": "Behavior distill",
    "b_frozen_random": "Frozen random",
}

COLORS = {
    "source_full": "#4d4d4d",
    "b_source_align_attention_copy_long": "#277da1",
    "b_behavior_distill": "#f3722c",
    "b_frozen_random": "#90be6d",
}


def load_json(path: Path):
    with path.open() as f:
        return json.load(f)


def save_figure(fig, output_base: Path) -> None:
    output_base.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_base.with_suffix(".png"), dpi=200, bbox_inches="tight")
    fig.savefig(output_base.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)


def summary_lookup(contrasts: dict) -> dict[str, dict]:
    return {item["condition"]: item for item in contrasts["summaries"]}


def paired_delta_lookup(contrasts: dict) -> dict[tuple[str, str], dict]:
    return {
        (item["baseline_condition"], item["metric"]): item
        for item in contrasts["paired_seed_deltas"]
    }


def plot_bidirectional_summary(contrasts: dict, output_dir: Path) -> None:
    summaries = summary_lookup(contrasts)
    labels = [CONDITION_LABELS[condition] for condition in CONDITION_ORDER]
    x = np.arange(len(CONDITION_ORDER))

    action_values = [
        summaries[condition]["source_with_donor_interchange_action_agreement"]
        for condition in CONDITION_ORDER
    ]
    q_values = [
        max(summaries[condition]["source_with_donor_delta_q_mse_to_source"], 1e-3)
        for condition in CONDITION_ORDER
    ]
    donor_attn = [
        summaries[condition]["donor_attention_l1_to_source_b"]
        for condition in CONDITION_ORDER
    ]
    colors = [COLORS[condition] for condition in CONDITION_ORDER]

    fig, (ax_action, ax_q, ax_attn) = plt.subplots(1, 3, figsize=(13.2, 4.8))

    ax_action.bar(x, action_values, color=colors)
    ax_action.set_ylim(0, 1.05)
    ax_action.set_ylabel("Action agreement")
    ax_action.set_title("Source counterfactual action")
    ax_action.set_xticks(x)
    ax_action.set_xticklabels(labels, rotation=24, ha="right")
    ax_action.spines["top"].set_visible(False)
    ax_action.spines["right"].set_visible(False)

    bars = ax_q.bar(x, q_values, color=colors)
    ax_q.set_yscale("log")
    ax_q.set_ylabel("Q-delta error to source")
    ax_q.set_title("Counterfactual Q geometry")
    ax_q.set_xticks(x)
    ax_q.set_xticklabels(labels, rotation=24, ha="right")
    ax_q.spines["top"].set_visible(False)
    ax_q.spines["right"].set_visible(False)
    for bar, condition in zip(bars, CONDITION_ORDER):
        raw = summaries[condition]["source_with_donor_delta_q_mse_to_source"]
        label = "0" if raw == 0 else f"{raw:.3g}"
        ax_q.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            label,
            ha="center",
            va="bottom",
            fontsize=8,
        )

    ax_attn.bar(x, donor_attn, color=colors)
    ax_attn.set_ylabel("L1 to source-B attention")
    ax_attn.set_title("Donor attention alignment")
    ax_attn.set_xticks(x)
    ax_attn.set_xticklabels(labels, rotation=24, ha="right")
    ax_attn.spines["top"].set_visible(False)
    ax_attn.spines["right"].set_visible(False)

    fig.suptitle(
        "Bidirectional target-to-source attention patching, full 22-source panel"
    )
    fig.tight_layout()
    save_figure(fig, output_dir / "fig8_bidirectional_attention_patch_full22")


def plot_paired_deltas(contrasts: dict, output_dir: Path) -> None:
    lookup = paired_delta_lookup(contrasts)
    metrics = [
        ("source_with_donor_interchange_action_agreement", "Action agreement", False),
        ("source_with_donor_delta_q_mse_to_source", "Q-delta error", True),
        ("source_with_donor_q_mse_to_source_cf", "Patched-Q error", True),
        (
            "source_with_donor_delta_self_report_l1_to_source",
            "Report-delta error",
            True,
        ),
    ]
    baselines = ["b_behavior_distill", "b_frozen_random"]

    fig, axes = plt.subplots(2, 2, figsize=(8.8, 6.4))
    axes = axes.ravel()
    for ax, (metric, title, lower_is_better) in zip(axes, metrics):
        labels = []
        means = []
        lows = []
        highs = []
        colors = []
        for baseline in baselines:
            item = lookup[(baseline, metric)]
            labels.append("vs behavior" if baseline == "b_behavior_distill" else "vs random")
            means.append(item["mean_delta"])
            lows.append(item["mean_delta_ci95_low"])
            highs.append(item["mean_delta_ci95_high"])
            colors.append("#f3722c" if baseline == "b_behavior_distill" else "#90be6d")
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
        ax.set_xticklabels(labels)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    fig.suptitle("Copied attention minus baselines, source-seed paired deltas")
    fig.tight_layout()
    save_figure(fig, output_dir / "fig9_bidirectional_paired_deltas_full22")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Plot Paper 5 bidirectional patch results."
    )
    parser.add_argument("--contrasts", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    contrasts = load_json(args.contrasts)
    plot_bidirectional_summary(contrasts, args.output_dir)
    plot_paired_deltas(contrasts, args.output_dir)
    print(f"wrote bidirectional figures to {args.output_dir}")


if __name__ == "__main__":
    main()
