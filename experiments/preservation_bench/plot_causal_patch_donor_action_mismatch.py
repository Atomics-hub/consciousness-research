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


def load_json(path: Path):
    with path.open() as f:
        return json.load(f)


def save_figure(fig, output_base: Path) -> None:
    output_base.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_base.with_suffix(".png"), dpi=200, bbox_inches="tight")
    fig.savefig(output_base.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)


def leakage_lookup(leakage: dict) -> dict[str, dict]:
    return {
        item["condition"]: item
        for item in leakage["summaries"]
        if item["subset"] == "all_rows"
        and item["donor_control"] == "donor_action_mismatch"
    }


def contrast_lookup(contrasts: dict) -> dict[str, dict]:
    return {
        item["condition"]: item
        for item in contrasts["summaries"]
        if item["donor_control"] == "donor_action_mismatch"
    }


def plot_donor_action_mismatch(contrasts: dict, leakage: dict, output_dir: Path) -> None:
    leak = leakage_lookup(leakage)
    contrast = contrast_lookup(contrasts)
    labels = [CONDITION_LABELS[condition] for condition in CONDITION_ORDER]
    x = np.arange(len(CONDITION_ORDER))

    fig, (ax_action, ax_q) = plt.subplots(
        1,
        2,
        figsize=(11.2, 4.9),
        gridspec_kw={"width_ratios": [1.45, 1.0]},
    )

    action_series = [
        ("Source counterfactual", "source_cf_action_agreement", "#277da1"),
        ("Donor-B ordinary", "donor_source_b_action_agreement", "#f3722c"),
        ("Matched reference", "matched_reference_action_agreement", "#577590"),
        ("Unpatched target", "target_unpatched_action_agreement", "#90be6d"),
    ]
    width = 0.18
    offsets = np.linspace(-1.5 * width, 1.5 * width, len(action_series))
    for offset, (name, key, color) in zip(offsets, action_series):
        values = [leak[condition][key] for condition in CONDITION_ORDER]
        ax_action.bar(x + offset, values, width, label=name, color=color)

    ax_action.set_ylim(0, 1.05)
    ax_action.set_ylabel("Action agreement")
    ax_action.set_title("Decoupled donor action labels")
    ax_action.set_xticks(x)
    ax_action.set_xticklabels(labels, rotation=20, ha="right")
    ax_action.legend(frameon=False, fontsize=8, ncols=2, loc="upper center")
    ax_action.spines["top"].set_visible(False)
    ax_action.spines["right"].set_visible(False)

    q_values = [
        max(contrast[condition]["target_patch_delta_q_mse_to_source"], 1e-3)
        for condition in CONDITION_ORDER
    ]
    colors = ["#4d4d4d", "#277da1", "#f3722c", "#90be6d"]
    bars = ax_q.bar(x, q_values, color=colors)
    ax_q.set_yscale("log")
    ax_q.set_ylabel("Q-delta error to source (log scale)")
    ax_q.set_title("Counterfactual geometry")
    ax_q.set_xticks(x)
    ax_q.set_xticklabels(labels, rotation=20, ha="right")
    ax_q.spines["top"].set_visible(False)
    ax_q.spines["right"].set_visible(False)
    for bar, condition in zip(bars, CONDITION_ORDER):
        raw = contrast[condition]["target_patch_delta_q_mse_to_source"]
        label = "0" if raw == 0 else f"{raw:.3g}"
        ax_q.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            label,
            ha="center",
            va="bottom",
            fontsize=8,
        )

    fig.suptitle(
        "Attention-state donor-action-mismatch follow-up: action labels vs Q geometry"
    )
    fig.tight_layout()
    save_figure(fig, output_dir / "fig7_attention_donor_action_mismatch")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Plot donor-action-mismatch follow-up for Paper 5."
    )
    parser.add_argument("--contrasts", type=Path, required=True)
    parser.add_argument("--leakage", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    contrasts = load_json(args.contrasts)
    leakage = load_json(args.leakage)
    plot_donor_action_mismatch(contrasts, leakage, args.output_dir)
    print(f"wrote donor-action-mismatch figure to {args.output_dir}")


if __name__ == "__main__":
    main()
