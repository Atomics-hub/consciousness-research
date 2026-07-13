#!/usr/bin/env python3
"""Generate Paper 4 summary tables and figures from PreservationBench runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = Path(__file__).resolve().parent
FIGURES_DIR = PAPER_DIR / "figures"
TABLES_DIR = PAPER_DIR / "tables"

TARGET = "b_source_align_attention_copy_long"
BASELINE = "b_frozen_random"

RECURRENT_STUDIES = [
    (
        "Selected source-policy delay 4",
        "selected-d4",
        "source-selected",
        "paper4/source_contrasts/selected-d4/recurrent_contrasts.json",
    ),
    (
        "Unselected source-policy delay 4",
        "unselected-d4",
        "source-unselected",
        "paper4/source_contrasts/unselected-d4/recurrent_contrasts.json",
    ),
    (
        "Unselected source-policy delay 8",
        "unselected-d8",
        "source-unselected",
        "paper4/source_contrasts/unselected-d8/recurrent_contrasts.json",
    ),
    (
        "Shifted-policy delay 4",
        "shifted-d4",
        "shifted-policy",
        "paper4/source_contrasts/shifted-d4/recurrent_contrasts.json",
    ),
    (
        "Random-policy delay 4",
        "random-d4",
        "random-policy",
        "paper4/source_contrasts/random-d4/recurrent_contrasts.json",
    ),
    (
        "Random-policy delay 8",
        "random-d8",
        "random-policy",
        "paper4/source_contrasts/random-d8/recurrent_contrasts.json",
    ),
    (
        "Random-policy delay 12",
        "random-d12",
        "random-policy",
        "paper4/source_contrasts/random-d12/recurrent_contrasts.json",
    ),
    (
        "Random-policy history 16 delay 12",
        "random-h16-d12",
        "random-policy",
        "paper4/source_contrasts/random-h16-d12/recurrent_contrasts.json",
    ),
    (
        "Random-policy history 16 delay 12 altseed",
        "random-h16-d12-alt",
        "random-policy-alt",
        "paper4/source_contrasts/random-h16-d12-alt/recurrent_contrasts.json",
    ),
    (
        "Scripted-cycle delay 8",
        "cycle-d8",
        "scripted-cycle",
        "paper4/source_contrasts/cycle-d8/recurrent_contrasts.json",
    ),
    (
        "Scripted-cycle stride 2 delay 8",
        "cycle-s2-d8",
        "scripted-cycle",
        "paper4/source_contrasts/cycle-s2-d8/recurrent_contrasts.json",
    ),
    (
        "Scripted-cycle stride 2 delay 12",
        "cycle-s2-d12",
        "scripted-cycle",
        "paper4/source_contrasts/cycle-s2-d12/recurrent_contrasts.json",
    ),
    (
        "Scripted-cycle stride 2 history 16 delay 12",
        "cycle-s2-h16-d12",
        "scripted-cycle",
        "paper4/source_contrasts/cycle-s2-h16-d12/recurrent_contrasts.json",
    ),
]

PERTURBATION_REPORT = (
    ROOT
    / "paper4/source_contrasts/perturbation-expanded22/perturbation_contrasts.json"
)


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def metric_mean(summary: dict[str, Any], metric: str) -> float:
    return float(summary[metric]["mean"])


def improvement(contrast: dict[str, Any], metric: str) -> float:
    item = contrast[metric]
    if "mean_improvement_vs_baseline" in item:
        return float(item["mean_improvement_vs_baseline"])
    return float(item["mean_delta"])


def improvement_ci(contrast: dict[str, Any], metric: str) -> list[float]:
    item = contrast[metric]
    return list(item.get("bootstrap_95_ci_improvement") or item.get("bootstrap_95_ci") or [0.0, 0.0])


def win_rate(contrast: dict[str, Any], metric: str) -> float:
    return float(contrast[metric].get("win_rate_vs_baseline", 0.0))


def report_failure_count(contrast_path: Path) -> tuple[int | None, list[int]]:
    failure_path = contrast_path.with_name("report_failure_inspection.json")
    if not failure_path.exists():
        return None, []
    payload = read_json(failure_path)
    return (
        payload.get("report_delta_failure_count"),
        [int(seed) for seed in payload.get("report_delta_failure_seeds", [])],
    )


def recurrent_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for label, short_label, family, raw_path in RECURRENT_STUDIES:
        path = ROOT / raw_path
        if not path.exists():
            continue
        payload = read_json(path)
        target_summary = payload["condition_summary"][TARGET]
        baseline_summary = payload["condition_summary"][payload.get("baseline", BASELINE)]
        target_contrast = payload["paired_contrasts_vs_baseline"][TARGET]
        failures, failure_seeds = report_failure_count(path)
        row = {
            "label": label,
            "short_label": short_label,
            "family": family,
            "path": raw_path,
            "n_rows": int(payload["n_rows"]),
            "n_train_seeds": int(payload["n_train_seeds"]),
            "query_mode": payload.get("query_mode", "unknown"),
            "history_policy_mode": payload.get("history_policy_mode", "source"),
            "report_delay_steps": int(payload.get("report_delay_steps", 0)),
            "target_warm_action_agreement": metric_mean(target_summary, "warm_action_agreement"),
            "baseline_warm_action_agreement": metric_mean(baseline_summary, "warm_action_agreement"),
            "target_hidden_mse": metric_mean(target_summary, "schema_hidden_mse_to_source_at_probe"),
            "baseline_hidden_mse": metric_mean(baseline_summary, "schema_hidden_mse_to_source_at_probe"),
            "target_report_delta": metric_mean(target_summary, "history_delta_self_report_l1_to_source"),
            "baseline_report_delta": metric_mean(baseline_summary, "history_delta_self_report_l1_to_source"),
            "warm_action_improvement": improvement(target_contrast, "warm_action_agreement"),
            "warm_action_ci": improvement_ci(target_contrast, "warm_action_agreement"),
            "warm_action_win_rate": win_rate(target_contrast, "warm_action_agreement"),
            "hidden_mse_improvement": improvement(target_contrast, "schema_hidden_mse_to_source_at_probe"),
            "hidden_mse_ci": improvement_ci(target_contrast, "schema_hidden_mse_to_source_at_probe"),
            "hidden_mse_win_rate": win_rate(target_contrast, "schema_hidden_mse_to_source_at_probe"),
            "report_delta_improvement": improvement(target_contrast, "history_delta_self_report_l1_to_source"),
            "report_delta_ci": improvement_ci(target_contrast, "history_delta_self_report_l1_to_source"),
            "report_delta_win_rate": win_rate(target_contrast, "history_delta_self_report_l1_to_source"),
            "report_delta_failure_count": failures,
            "report_delta_failure_seeds": failure_seeds,
        }
        rows.append(row)
    return rows


def perturbation_summary() -> dict[str, Any]:
    payload = read_json(PERTURBATION_REPORT)
    rows = []
    for condition, summary in payload["condition_summary"].items():
        row = {
            "condition": condition,
            "n_rows": int(summary["n_rows"]),
            "n_train_seeds": int(summary["n_train_seeds"]),
            "perturbed_action_agreement": metric_mean(summary, "perturbed_action_agreement"),
            "attention_delta_l1_to_source": metric_mean(summary, "attention_delta_l1_to_source"),
            "q_delta_mse_to_source": metric_mean(summary, "q_delta_mse_to_source"),
            "self_report_delta_l1_to_source": metric_mean(summary, "self_report_delta_l1_to_source"),
            "action_shift_match": metric_mean(summary, "action_shift_match"),
        }
        if condition in payload["paired_contrasts_vs_baseline"]:
            contrast = payload["paired_contrasts_vs_baseline"][condition]
            row["perturbed_action_delta_vs_random"] = float(
                contrast["perturbed_action_agreement"]["mean_delta"]
            )
        rows.append(row)
    return {
        "path": str(PERTURBATION_REPORT.relative_to(ROOT)),
        "baseline": payload["baseline"],
        "rows": sorted(rows, key=lambda row: row["perturbed_action_agreement"], reverse=True),
    }


def write_outputs(rows: list[dict[str, Any]], perturbation: dict[str, Any]) -> None:
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "boundary": (
            "Toy functional benchmark only. These outputs do not measure consciousness, "
            "identity, survival, biological preservation, or whole-agent equivalence."
        ),
        "target_condition": TARGET,
        "baseline_condition": BASELINE,
        "recurrent_rows": rows,
        "perturbation": perturbation,
    }
    (TABLES_DIR / "paper4_results_summary.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (TABLES_DIR / "paper4_results_summary.md").write_text(summary_markdown(rows, perturbation), encoding="utf-8")


def summary_markdown(rows: list[dict[str, Any]], perturbation: dict[str, Any]) -> str:
    lines = [
        "# Paper 4 Results Summary",
        "",
        "Boundary: toy functional benchmark only. This is not a consciousness, identity, survival, biological preservation, or whole-agent equivalence result.",
        "",
        "## Recurrent Sweep",
        "",
        "| Run | Policy family | Delay | Seeds | Target/base warm | Warm improvement | Hidden improvement | Report improvement | Report failures |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        failure_value = row["report_delta_failure_count"]
        failures = "" if failure_value is None else str(failure_value)
        lines.append(
            "| {label} | `{family}` | {delay} | {seeds} | {warm:.3f}/{base:.3f} | {warm_imp:.3f} | {hidden_imp:.4f} | {report_imp:.4f} | {failures} |".format(
                label=row["label"],
                family=row["family"],
                delay=row["report_delay_steps"],
                seeds=row["n_train_seeds"],
                warm=row["target_warm_action_agreement"],
                base=row["baseline_warm_action_agreement"],
                warm_imp=row["warm_action_improvement"],
                hidden_imp=row["hidden_mse_improvement"],
                report_imp=row["report_delta_improvement"],
                failures=failures,
            )
        )
    lines.extend(
        [
            "",
            "## Perturbation Layer",
            "",
            "| Condition | Perturbed action agreement | Attention delta | Q delta MSE | Self-report delta |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in perturbation["rows"]:
        lines.append(
            "| `{condition}` | {paa:.3f} | {attn:.4f} | {q:.4f} | {report:.4f} |".format(
                condition=row["condition"],
                paa=row["perturbed_action_agreement"],
                attn=row["attention_delta_l1_to_source"],
                q=row["q_delta_mse_to_source"],
                report=row["self_report_delta_l1_to_source"],
            )
        )
    lines.extend(
        [
            "",
            "## Working Interpretation",
            "",
            "Copied attention is consistently separated from frozen random on warm-action agreement and source-hidden-state distance across selected, deterministic unselected, shifted-policy, random-policy, and scripted-cycle histories. The report channel is positive but trajectory-sensitive, so the paper should argue for history-dependent functional continuity under bounded toy conditions, not consciousness preservation.",
            "",
        ]
    )
    return "\n".join(lines)


def plot_recurrent(rows: list[dict[str, Any]]) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    labels = [row["short_label"] for row in rows]
    x = np.arange(len(rows))

    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    panels = [
        ("warm_action_improvement", "Warm-action improvement vs frozen random", "#2a9d8f"),
        ("hidden_mse_improvement", "Hidden-state MSE improvement vs frozen random", "#2f5f98"),
        ("report_delta_improvement", "Self-report delta improvement vs frozen random", "#e9c46a"),
    ]
    for ax, (key, title, color) in zip(axes, panels):
        vals = [row[key] for row in rows]
        lo = [max(0.0, row[key] - row[key.replace("_improvement", "_ci")][0]) for row in rows]
        hi = [max(0.0, row[key.replace("_improvement", "_ci")][1] - row[key]) for row in rows]
        ax.bar(x, vals, yerr=np.vstack([lo, hi]), color=color, capsize=3, edgecolor="#222", linewidth=0.4)
        ax.axhline(0, color="#333", linewidth=0.8)
        ax.set_ylabel("improvement")
        ax.set_title(title)
        ax.grid(axis="y", alpha=0.22)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    axes[-1].set_xticks(x)
    axes[-1].set_xticklabels(labels, rotation=35, ha="right")
    fig.suptitle("Paper 4 recurrent stress sweep: copied attention vs frozen random", fontsize=14, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.98])
    fig.savefig(FIGURES_DIR / "fig1_recurrent_stress_sweep.png", dpi=180)
    plt.close(fig)


def plot_perturbation(perturbation: dict[str, Any]) -> None:
    rows = [
        row
        for row in perturbation["rows"]
        if row["condition"]
        in {
            "source_full",
            TARGET,
            "b_source_align_control_adapter_long",
            "b_source_align_attention_adapter_long",
            "b_source_align_repair_copy_long",
            "b_behavior_distill",
            BASELINE,
        }
    ]
    labels = [
        {
            "source_full": "Source",
            TARGET: "Copied attention",
            "b_source_align_control_adapter_long": "Control bridge",
            "b_source_align_attention_adapter_long": "Attention bridge",
            "b_source_align_repair_copy_long": "Long repair",
            "b_behavior_distill": "Behavior distill",
            BASELINE: "Frozen random",
        }[row["condition"]]
        for row in rows
    ]
    x = np.arange(len(rows))

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    axes[0].bar(
        x,
        [row["perturbed_action_agreement"] for row in rows],
        color="#2a9d8f",
        edgecolor="#222",
        linewidth=0.4,
    )
    axes[0].set_title("Perturbed action agreement")
    axes[0].set_ylabel("agreement")
    axes[0].set_ylim(0, 1.05)
    axes[0].grid(axis="y", alpha=0.22)

    width = 0.28
    axes[1].bar(
        x - width,
        [row["attention_delta_l1_to_source"] for row in rows],
        width,
        label="Attention delta",
        color="#2f5f98",
    )
    axes[1].bar(
        x,
        [row["self_report_delta_l1_to_source"] for row in rows],
        width,
        label="Report delta",
        color="#e9c46a",
    )
    axes[1].bar(
        x + width,
        [min(row["q_delta_mse_to_source"] / 100.0, 0.08) for row in rows],
        width,
        label="Q delta MSE / 100",
        color="#e76f51",
    )
    axes[1].set_title("Internal response distance to source")
    axes[1].set_ylabel("distance")
    axes[1].grid(axis="y", alpha=0.22)
    axes[1].legend(frameon=False, fontsize=8)

    for ax in axes:
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=35, ha="right")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    fig.suptitle("Paper 4 perturbation layer", fontsize=14, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(FIGURES_DIR / "fig2_perturbation_layer.png", dpi=180)
    plt.close(fig)


def main() -> None:
    rows = recurrent_rows()
    perturbation = perturbation_summary()
    write_outputs(rows, perturbation)
    plot_recurrent(rows)
    plot_perturbation(perturbation)
    print(f"Wrote {TABLES_DIR / 'paper4_results_summary.json'}")
    print(f"Wrote {TABLES_DIR / 'paper4_results_summary.md'}")
    print(f"Wrote {FIGURES_DIR / 'fig1_recurrent_stress_sweep.png'}")
    print(f"Wrote {FIGURES_DIR / 'fig2_perturbation_layer.png'}")


if __name__ == "__main__":
    main()
