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
    "source_with_donor_interchange_action_agreement",
    "source_with_donor_shift_match",
    "source_with_donor_source_a_action_agreement",
    "source_with_donor_source_b_action_agreement",
    "donor_action_matches_source_b_action",
    "donor_action_matches_source_cf_action",
    "source_with_donor_delta_q_mse_to_source",
    "source_with_donor_q_mse_to_source_cf",
    "source_with_donor_delta_self_report_l1_to_source",
    "source_with_donor_self_report_l1_to_source_cf",
    "donor_attention_l1_to_source_b",
    "donor_feature_mse_to_source_b",
    "donor_q_mse_to_source_b",
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


def bootstrap_mean_ci(values: list[float], seed: int) -> dict:
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
    for _ in range(BOOTSTRAP_REPS):
        samples.append(mean([values[rng.randrange(len(values))] for _ in values]))
    samples.sort()
    return {
        "bootstrap_reps": BOOTSTRAP_REPS,
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
    return summary


def condition_sort_key(condition: str) -> tuple[int, str]:
    try:
        return CONDITION_ORDER.index(condition), condition
    except ValueError:
        return len(CONDITION_ORDER), condition


def grouped_summaries(rows: list[dict]) -> list[dict]:
    grouped = group_rows(rows, ("condition",))
    summaries = []
    for (condition,), group in sorted(
        grouped.items(),
        key=lambda item: condition_sort_key(item[0][0]),
    ):
        summaries.append({"condition": condition, **summarize_rows(group)})
    return summaries


def mean_by_seed(rows: list[dict], metric: str) -> dict[int, float]:
    grouped = group_rows(rows, ("training_seed_index",))
    return {
        int(seed_key[0]): mean([float(row[metric]) for row in group])
        for seed_key, group in grouped.items()
    }


def paired_seed_deltas(
    rows: list[dict],
    target_condition: str,
    baseline_conditions: list[str],
    metrics: list[str],
) -> list[dict]:
    output = []
    for baseline in baseline_conditions:
        for metric in metrics:
            target_by_seed = mean_by_seed(
                [row for row in rows if row["condition"] == target_condition],
                metric,
            )
            baseline_by_seed = mean_by_seed(
                [row for row in rows if row["condition"] == baseline],
                metric,
            )
            seeds = sorted(set(target_by_seed) & set(baseline_by_seed))
            deltas = [target_by_seed[seed] - baseline_by_seed[seed] for seed in seeds]
            ci = bootstrap_mean_ci(
                deltas,
                seed=deterministic_seed(target_condition, baseline, metric),
            )
            output.append(
                {
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


def markdown_report(payload: dict) -> str:
    lines = [
        "# Bidirectional Patch Contrasts",
        "",
        "Target-B activations are patched back into source context A and compared with the source-B-to-source-A source counterfactual.",
        "",
        "## Condition Summary",
        "",
        "| condition | n | seeds | src flip | action agreement | shift match | q-delta error | patched-Q error | donor attention L1 | donor feature MSE |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for summary in payload["summaries"]:
        lines.append(
            "| {condition} | {n_rows} | {n_source_seeds} | {src_flip} | {action} | "
            "{shift} | {q_delta} | {patched_q} | {attn} | {features} |".format(
                condition=summary["condition"],
                n_rows=summary["n_rows"],
                n_source_seeds=summary["n_source_seeds"],
                src_flip=fmt(summary["source_patch_action_changed"]),
                action=fmt(
                    summary["source_with_donor_interchange_action_agreement"]
                ),
                shift=fmt(summary["source_with_donor_shift_match"]),
                q_delta=fmt(summary["source_with_donor_delta_q_mse_to_source"]),
                patched_q=fmt(summary["source_with_donor_q_mse_to_source_cf"]),
                attn=fmt(summary["donor_attention_l1_to_source_b"]),
                features=fmt(summary["donor_feature_mse_to_source_b"]),
            )
        )
    lines.extend(
        [
            "",
            "## Paired Seed Deltas",
            "",
            "| baseline | metric | seeds | copied-minus-baseline | 95% CI |",
            "| --- | --- | ---: | ---: | --- |",
        ]
    )
    for item in payload["paired_seed_deltas"]:
        lines.append(
            "| {baseline} | {metric} | {seeds} | {delta} | [{low}, {high}] |".format(
                baseline=item["baseline_condition"],
                metric=item["metric"],
                seeds=item["n_source_seeds"],
                delta=fmt(item["mean_delta"]),
                low=fmt(item["mean_delta_ci95_low"]),
                high=fmt(item["mean_delta_ci95_high"]),
            )
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze Paper 5 bidirectional patch contrasts."
    )
    parser.add_argument("--rows", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()

    rows = load_jsonl(args.rows)
    payload = {
        "rows_path": str(args.rows),
        "summaries": grouped_summaries(rows),
        "paired_seed_deltas": paired_seed_deltas(
            rows,
            target_condition="b_source_align_attention_copy_long",
            baseline_conditions=["b_behavior_distill", "b_frozen_random"],
            metrics=[
                "source_with_donor_interchange_action_agreement",
                "source_with_donor_delta_q_mse_to_source",
                "source_with_donor_q_mse_to_source_cf",
                "source_with_donor_delta_self_report_l1_to_source",
            ],
        ),
        "metric_boundary": (
            "These are toy AST bidirectional activation-patching contrasts. "
            "They do not measure consciousness, survival, personal identity, "
            "biological preservation, or AST truth."
        ),
    }
    write_json(args.output_json, payload)
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(markdown_report(payload), encoding="utf-8")
    print(f"wrote {args.output_json}")
    print(f"wrote {args.output_md}")


if __name__ == "__main__":
    main()
