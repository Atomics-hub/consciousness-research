#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


CONDITIONS = [
    "b_behavior_distill",
    "b_source_align_attention_copy_long",
]

METRICS = [
    "target_unpatched_source_a_action_agreement",
    "target_interchange_action_agreement",
    "target_patch_shift_match",
    "target_patch_delta_q_mse_to_source",
    "target_patched_q_mse_to_source_cf",
    "target_patch_delta_self_report_l1_to_source",
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


def grouped_condition_pairs(rows: list[dict], donor_control: str) -> list[dict]:
    grouped = defaultdict(dict)
    for row in rows:
        if row["donor_control"] != donor_control:
            continue
        key = (
            row["training_seed_index"],
            row["candidate_index"],
            row["donor_candidate_index"],
            row["donor_control"],
        )
        grouped[key][row["condition"]] = row
    pairs = []
    for key, group in grouped.items():
        if all(condition in group for condition in CONDITIONS):
            pairs.append(
                {
                    "key": key,
                    "behavior": group["b_behavior_distill"],
                    "copied_attention": group["b_source_align_attention_copy_long"],
                }
            )
    return pairs


def subset_pairs(pairs: list[dict], name: str) -> list[dict]:
    if name == "all_pairs":
        return pairs
    if name == "behavior_unpatched_matches_source_a":
        return [
            pair
            for pair in pairs
            if pair["behavior"]["target_unpatched_source_a_action_agreement"] == 1
        ]
    if name == "both_unpatched_match_source_a":
        return [
            pair
            for pair in pairs
            if pair["behavior"]["target_unpatched_source_a_action_agreement"] == 1
            and pair["copied_attention"]["target_unpatched_source_a_action_agreement"]
            == 1
        ]
    if name == "behavior_matches_source_a_and_source_patch_flips":
        return [
            pair
            for pair in pairs
            if pair["behavior"]["target_unpatched_source_a_action_agreement"] == 1
            and pair["behavior"]["source_patch_action_changed"] == 1
        ]
    raise ValueError(f"Unsupported subset: {name}")


def summarize_condition(rows: list[dict]) -> dict:
    summary = {
        "n_rows": len(rows),
        "n_source_seeds": len({row["training_seed_index"] for row in rows}),
    }
    for metric in METRICS:
        summary[metric] = mean([float(row[metric]) for row in rows])
    return summary


def summarize_pairs(pairs: list[dict]) -> dict:
    behavior_rows = [pair["behavior"] for pair in pairs]
    copied_rows = [pair["copied_attention"] for pair in pairs]
    summary = {
        "n_pairs": len(pairs),
        "n_source_seeds": len(
            {pair["behavior"]["training_seed_index"] for pair in pairs}
        ),
        "behavior": summarize_condition(behavior_rows),
        "copied_attention": summarize_condition(copied_rows),
        "copied_minus_behavior": {},
    }
    for metric in METRICS:
        summary["copied_minus_behavior"][metric] = mean(
            [
                float(pair["copied_attention"][metric])
                - float(pair["behavior"][metric])
                for pair in pairs
            ]
        )
    return summary


def build_payload(rows: list[dict], rows_path: Path) -> dict:
    subset_names = [
        "all_pairs",
        "behavior_unpatched_matches_source_a",
        "both_unpatched_match_source_a",
        "behavior_matches_source_a_and_source_patch_flips",
    ]
    donor_controls = sorted({row["donor_control"] for row in rows})
    payload = {
        "rows_path": str(rows_path),
        "subsets": [],
    }
    for donor_control in donor_controls:
        pairs = grouped_condition_pairs(rows, donor_control)
        for subset_name in subset_names:
            subset = subset_pairs(pairs, subset_name)
            payload["subsets"].append(
                {
                    "donor_control": donor_control,
                    "subset": subset_name,
                    **summarize_pairs(subset),
                }
            )
    return payload


def fmt(value: float) -> str:
    if value != value:
        return "nan"
    return f"{value:.3f}"


def build_markdown(payload: dict) -> str:
    lines = [
        "# Behavior-Matched Causal Patch Subsets",
        "",
        "This report asks whether behavior distillation still fails causal intervention on rows where it matches the ordinary source-A action.",
        "",
        "| donor | subset | pairs | seeds | behavior ordinary | behavior causal | copied ordinary | copied causal | copied-behavior causal | copied-behavior q-delta | copied-behavior patched-Q |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in payload["subsets"]:
        b = item["behavior"]
        c = item["copied_attention"]
        d = item["copied_minus_behavior"]
        lines.append(
            "| {donor} | {subset} | {pairs} | {seeds} | {b_ord} | {b_causal} | "
            "{c_ord} | {c_causal} | {d_causal} | {d_q} | {d_pq} |".format(
                donor=item["donor_control"],
                subset=item["subset"],
                pairs=item["n_pairs"],
                seeds=item["n_source_seeds"],
                b_ord=fmt(b["target_unpatched_source_a_action_agreement"]),
                b_causal=fmt(b["target_interchange_action_agreement"]),
                c_ord=fmt(c["target_unpatched_source_a_action_agreement"]),
                c_causal=fmt(c["target_interchange_action_agreement"]),
                d_causal=fmt(d["target_interchange_action_agreement"]),
                d_q=fmt(d["target_patch_delta_q_mse_to_source"]),
                d_pq=fmt(d["target_patched_q_mse_to_source_cf"]),
            )
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze behavior-matched causal-patch subsets."
    )
    parser.add_argument("rows", type=Path)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--output-md", type=Path)
    args = parser.parse_args()

    rows = load_jsonl(args.rows)
    payload = build_payload(rows, args.rows)
    if args.output_json:
        write_json(args.output_json, payload)
    if args.output_md:
        args.output_md.parent.mkdir(parents=True, exist_ok=True)
        args.output_md.write_text(build_markdown(payload), encoding="utf-8")

    print(f"rows={len(rows)}")
    for item in payload["subsets"]:
        if item["subset"] not in {
            "behavior_unpatched_matches_source_a",
            "both_unpatched_match_source_a",
        }:
            continue
        print(
            "{donor}/{subset} n={n_pairs} seeds={n_source_seeds} "
            "behavior_causal={b:.3f} copied_causal={c:.3f} delta={d:.3f}".format(
                donor=item["donor_control"],
                subset=item["subset"],
                n_pairs=item["n_pairs"],
                n_source_seeds=item["n_source_seeds"],
                b=item["behavior"]["target_interchange_action_agreement"],
                c=item["copied_attention"][
                    "target_interchange_action_agreement"
                ],
                d=item["copied_minus_behavior"][
                    "target_interchange_action_agreement"
                ],
            )
        )


if __name__ == "__main__":
    main()
