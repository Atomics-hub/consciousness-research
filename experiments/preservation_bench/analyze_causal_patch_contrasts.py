#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path


BOOTSTRAP_REPS = 5000

CONDITION_ORDER = [
    "source_full",
    "b_source_align_attention_copy_long",
    "b_behavior_distill",
    "b_frozen_random",
]

SUMMARY_METRICS = [
    "source_patch_action_changed",
    "source_control_matches_matched_reference_action",
    "target_interchange_action_agreement",
    "target_patched_matched_reference_action_agreement",
    "target_patch_action_changed",
    "target_patch_shift_match",
    "target_patch_delta_q_mse_to_source",
    "target_patched_q_mse_to_source_cf",
    "target_patched_q_mse_to_matched_reference_cf",
    "target_patch_delta_self_report_l1_to_source",
    "target_unpatched_source_a_action_agreement",
]


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else float("nan")


def deterministic_seed(*parts: object) -> int:
    text = "|".join(str(part) for part in parts)
    value = 0
    for char in text:
        value = (value * 131 + ord(char)) % (2**32)
    return value


def percentile(sorted_values: list[float], q: float) -> float:
    if not sorted_values:
        return float("nan")
    if len(sorted_values) == 1:
        return sorted_values[0]
    pos = q * (len(sorted_values) - 1)
    lower = int(pos)
    upper = min(lower + 1, len(sorted_values) - 1)
    frac = pos - lower
    return sorted_values[lower] * (1.0 - frac) + sorted_values[upper] * frac


def bootstrap_mean_ci(
    values: list[float],
    seed: int,
    reps: int = BOOTSTRAP_REPS,
) -> dict:
    if not values:
        return {
            "bootstrap_reps": 0,
            "mean_delta_ci95_low": float("nan"),
            "mean_delta_ci95_high": float("nan"),
        }
    if len(values) == 1:
        return {
            "bootstrap_reps": 0,
            "mean_delta_ci95_low": values[0],
            "mean_delta_ci95_high": values[0],
        }
    rng = random.Random(seed)
    samples = []
    for _ in range(reps):
        samples.append(mean([values[rng.randrange(len(values))] for _ in values]))
    samples.sort()
    return {
        "bootstrap_reps": reps,
        "mean_delta_ci95_low": percentile(samples, 0.025),
        "mean_delta_ci95_high": percentile(samples, 0.975),
    }


def group_rows(rows: list[dict], keys: tuple[str, ...]) -> dict[tuple, list[dict]]:
    grouped = defaultdict(list)
    for row in rows:
        grouped[tuple(row[key] for key in keys)].append(row)
    return dict(grouped)


def summarize_rows(rows: list[dict]) -> dict:
    summary = {
        "n_rows": len(rows),
        "n_source_seeds": len({row["training_seed_index"] for row in rows}),
    }
    for metric in SUMMARY_METRICS:
        summary[metric] = mean([float(row[metric]) for row in rows])
    summary["causal_specificity_gap_action"] = (
        summary["target_interchange_action_agreement"]
        - summary["target_patched_matched_reference_action_agreement"]
    )
    return summary


def condition_sort_key(item: tuple[str, str]) -> tuple[int, str]:
    condition, donor_control = item
    try:
        condition_idx = CONDITION_ORDER.index(condition)
    except ValueError:
        condition_idx = len(CONDITION_ORDER)
    return condition_idx, donor_control


def grouped_summaries(rows: list[dict]) -> list[dict]:
    grouped = group_rows(rows, ("condition", "donor_control"))
    summaries = []
    for (condition, donor_control), group in sorted(
        grouped.items(),
        key=lambda item: condition_sort_key(item[0]),
    ):
        summaries.append(
            {
                "condition": condition,
                "donor_control": donor_control,
                **summarize_rows(group),
            }
        )
    return summaries


def source_flip_only_summaries(rows: list[dict]) -> list[dict]:
    matched_flip_rows = [
        row
        for row in rows
        if row["donor_control"] == "matched"
        and int(row["source_patch_action_changed"]) == 1
    ]
    return grouped_summaries(matched_flip_rows)


def mean_by_seed(rows: list[dict], metric: str) -> dict[int, float]:
    grouped = group_rows(rows, ("training_seed_index",))
    return {
        int(seed_key[0]): mean([float(row[metric]) for row in group])
        for seed_key, group in grouped.items()
    }


def paired_seed_deltas(
    rows: list[dict],
    donor_control: str,
    target_condition: str,
    baseline_conditions: list[str],
    metrics: list[str],
) -> list[dict]:
    output = []
    donor_rows = [row for row in rows if row["donor_control"] == donor_control]
    for baseline in baseline_conditions:
        for metric in metrics:
            target_by_seed = mean_by_seed(
                [
                    row
                    for row in donor_rows
                    if row["condition"] == target_condition
                ],
                metric,
            )
            baseline_by_seed = mean_by_seed(
                [row for row in donor_rows if row["condition"] == baseline],
                metric,
            )
            seeds = sorted(set(target_by_seed) & set(baseline_by_seed))
            deltas = [target_by_seed[seed] - baseline_by_seed[seed] for seed in seeds]
            ci = bootstrap_mean_ci(
                deltas,
                seed=deterministic_seed(
                    donor_control,
                    target_condition,
                    baseline,
                    metric,
                ),
            )
            output.append(
                {
                    "donor_control": donor_control,
                    "target_condition": target_condition,
                    "baseline_condition": baseline,
                    "metric": metric,
                    "n_source_seeds": len(seeds),
                    "mean_delta": mean(deltas),
                    **ci,
                    "per_seed_delta": {
                        str(seed): deltas[idx] for idx, seed in enumerate(seeds)
                    },
                }
            )
    return output


def fmt(value: float) -> str:
    if value != value:
        return "nan"
    return f"{value:.3f}"


def markdown_table(summaries: list[dict], title: str) -> list[str]:
    lines = [
        f"## {title}",
        "",
        "| donor | condition | n | seeds | src flip | control=matched | donor action | matched-ref action | specificity gap | patch changed | shift match | q delta | report delta | unpatched A |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for summary in summaries:
        lines.append(
            "| {donor} | {condition} | {n_rows} | {n_source_seeds} | {src_flip} | "
            "{control_match} | {donor_action} | {matched_action} | {gap} | "
            "{patch_changed} | {shift} | {q_delta} | {report_delta} | {unpatched_a} |".format(
                donor=summary["donor_control"],
                condition=summary["condition"],
                n_rows=summary["n_rows"],
                n_source_seeds=summary["n_source_seeds"],
                src_flip=fmt(summary["source_patch_action_changed"]),
                control_match=fmt(
                    summary["source_control_matches_matched_reference_action"]
                ),
                donor_action=fmt(summary["target_interchange_action_agreement"]),
                matched_action=fmt(
                    summary["target_patched_matched_reference_action_agreement"]
                ),
                gap=fmt(summary["causal_specificity_gap_action"]),
                patch_changed=fmt(summary["target_patch_action_changed"]),
                shift=fmt(summary["target_patch_shift_match"]),
                q_delta=fmt(summary["target_patch_delta_q_mse_to_source"]),
                report_delta=fmt(
                    summary["target_patch_delta_self_report_l1_to_source"]
                ),
                unpatched_a=fmt(summary["target_unpatched_source_a_action_agreement"]),
            )
        )
    lines.append("")
    return lines


def deltas_markdown(deltas: list[dict]) -> list[str]:
    lines = [
        "## Paired Seed Deltas",
        "",
        "`mean_delta` is copied-attention minus the listed baseline, after averaging rows within each source seed.",
        "",
        "| donor | baseline | metric | seeds | mean delta | 95% bootstrap CI |",
        "| --- | --- | --- | ---: | ---: | ---: |",
    ]
    for item in deltas:
        lines.append(
            "| {donor} | {baseline} | {metric} | {seeds} | {delta} | [{low}, {high}] |".format(
                donor=item["donor_control"],
                baseline=item["baseline_condition"],
                metric=item["metric"],
                seeds=item["n_source_seeds"],
                delta=fmt(item["mean_delta"]),
                low=fmt(item["mean_delta_ci95_low"]),
                high=fmt(item["mean_delta_ci95_high"]),
            )
        )
    lines.append("")
    return lines


def build_report(payload: dict) -> str:
    lines = [
        "# Causal Patch Contrast Report",
        "",
        "This report summarizes source activation interchange rows. It is a toy PreservationBench-AST analysis and does not measure consciousness, identity, survival, or AST truth.",
        "",
    ]
    lines.extend(markdown_table(payload["summaries"], "All Rows"))
    if payload["source_flip_only_summaries"]:
        lines.extend(
            markdown_table(
                payload["source_flip_only_summaries"],
                "Matched Donors, Source-Action-Flip Rows Only",
            )
        )
    lines.extend(deltas_markdown(payload["paired_seed_deltas"]))
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Summarize Paper 5 causal patch contrast rows."
    )
    parser.add_argument("rows", type=Path)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--output-md", type=Path)
    args = parser.parse_args()

    rows = load_jsonl(args.rows)
    donor_controls = sorted({row["donor_control"] for row in rows})
    delta_metrics = [
        "target_interchange_action_agreement",
        "target_patch_delta_q_mse_to_source",
        "target_patched_q_mse_to_source_cf",
        "target_patched_q_mse_to_matched_reference_cf",
        "target_patch_delta_self_report_l1_to_source",
        "target_unpatched_source_a_action_agreement",
    ]
    deltas = []
    for donor_control in donor_controls:
        deltas.extend(
            paired_seed_deltas(
                rows=rows,
                donor_control=donor_control,
                target_condition="b_source_align_attention_copy_long",
                baseline_conditions=["b_behavior_distill", "b_frozen_random"],
                metrics=delta_metrics,
            )
        )

    payload = {
        "rows_path": str(args.rows),
        "n_rows": len(rows),
        "summaries": grouped_summaries(rows),
        "source_flip_only_summaries": source_flip_only_summaries(rows),
        "paired_seed_deltas": deltas,
    }

    if args.output_json:
        write_json(args.output_json, payload)
    if args.output_md:
        args.output_md.parent.mkdir(parents=True, exist_ok=True)
        args.output_md.write_text(build_report(payload), encoding="utf-8")

    print(f"rows={len(rows)}")
    for summary in payload["summaries"]:
        print(
            "{condition}/{donor:<16} n={n_rows:>3} src_flip={src:.3f} "
            "donor_action={donor_action:.3f} matched_action={matched:.3f} "
            "gap={gap:.3f} q_delta={q:.4f}".format(
                condition=summary["condition"],
                donor=summary["donor_control"],
                n_rows=summary["n_rows"],
                src=summary["source_patch_action_changed"],
                donor_action=summary["target_interchange_action_agreement"],
                matched=summary[
                    "target_patched_matched_reference_action_agreement"
                ],
                gap=summary["causal_specificity_gap_action"],
                q=summary["target_patch_delta_q_mse_to_source"],
            )
        )


if __name__ == "__main__":
    main()
