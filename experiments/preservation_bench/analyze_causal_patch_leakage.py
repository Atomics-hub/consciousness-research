#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


CONDITION_ORDER = [
    "source_full",
    "b_source_align_attention_copy_long",
    "b_behavior_distill",
    "b_frozen_random",
]

SUBSETS = [
    "all_rows",
    "source_cf_differs_from_donor_source_b_action",
    "source_cf_differs_from_target_unpatched_action",
    "action_mismatch_rows",
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


def subset_rows(rows: list[dict], subset: str) -> list[dict]:
    if subset == "all_rows":
        return rows
    if subset == "source_cf_differs_from_donor_source_b_action":
        return [
            row
            for row in rows
            if int(row["source_cf_action"]) != int(row["donor_source_b_action"])
        ]
    if subset == "source_cf_differs_from_target_unpatched_action":
        return [
            row
            for row in rows
            if int(row["source_cf_action"]) != int(row["target_unpatched_action"])
        ]
    if subset == "action_mismatch_rows":
        return [row for row in rows if row["donor_control"] == "action_mismatch"]
    raise ValueError(f"Unsupported subset: {subset}")


def summarize(rows: list[dict]) -> dict:
    n = len(rows)
    summary = {
        "n_rows": n,
        "n_source_seeds": len({row["training_seed_index"] for row in rows}),
    }
    if not rows:
        for key in [
            "source_cf_action_agreement",
            "target_unpatched_action_agreement",
            "donor_source_b_action_agreement",
            "matched_reference_action_agreement",
            "source_cf_equals_donor_source_b_action",
            "source_cf_equals_target_unpatched_action",
            "source_cf_equals_matched_reference_action",
            "target_patch_action_changed",
            "counterfactual_vs_unpatched_action_gap",
            "counterfactual_vs_donor_source_b_action_gap",
            "counterfactual_vs_matched_reference_action_gap",
        ]:
            summary[key] = float("nan")
        return summary

    source_cf = [
        int(row["target_patched_action"]) == int(row["source_cf_action"])
        for row in rows
    ]
    unpatched = [
        int(row["target_patched_action"]) == int(row["target_unpatched_action"])
        for row in rows
    ]
    donor_source_b = [
        int(row["target_patched_action"]) == int(row["donor_source_b_action"])
        for row in rows
    ]
    matched_ref = [
        int(row["target_patched_action"]) == int(row["matched_source_cf_action"])
        for row in rows
    ]
    summary["source_cf_action_agreement"] = mean([float(x) for x in source_cf])
    summary["target_unpatched_action_agreement"] = mean(
        [float(x) for x in unpatched]
    )
    summary["donor_source_b_action_agreement"] = mean(
        [float(x) for x in donor_source_b]
    )
    summary["matched_reference_action_agreement"] = mean(
        [float(x) for x in matched_ref]
    )
    summary["source_cf_equals_donor_source_b_action"] = mean(
        [
            float(int(row["source_cf_action"]) == int(row["donor_source_b_action"]))
            for row in rows
        ]
    )
    summary["source_cf_equals_target_unpatched_action"] = mean(
        [
            float(int(row["source_cf_action"]) == int(row["target_unpatched_action"]))
            for row in rows
        ]
    )
    summary["source_cf_equals_matched_reference_action"] = mean(
        [
            float(int(row["source_cf_action"]) == int(row["matched_source_cf_action"]))
            for row in rows
        ]
    )
    summary["target_patch_action_changed"] = mean(
        [float(row["target_patch_action_changed"]) for row in rows]
    )
    summary["counterfactual_vs_unpatched_action_gap"] = (
        summary["source_cf_action_agreement"]
        - summary["target_unpatched_action_agreement"]
    )
    summary["counterfactual_vs_donor_source_b_action_gap"] = (
        summary["source_cf_action_agreement"]
        - summary["donor_source_b_action_agreement"]
    )
    summary["counterfactual_vs_matched_reference_action_gap"] = (
        summary["source_cf_action_agreement"]
        - summary["matched_reference_action_agreement"]
    )
    return summary


def condition_sort_key(key: tuple[str, str, str]) -> tuple[str, int, str]:
    subset, donor, condition = key
    try:
        condition_idx = CONDITION_ORDER.index(condition)
    except ValueError:
        condition_idx = len(CONDITION_ORDER)
    return subset, condition_idx, donor


def build_payload(rows: list[dict], rows_path: Path) -> dict:
    payload = {
        "rows_path": str(rows_path),
        "vector_paths": sorted({row["vector_path"] for row in rows}),
        "summaries": [],
    }
    grouped = defaultdict(list)
    for subset in SUBSETS:
        for row in subset_rows(rows, subset):
            grouped[(subset, row["donor_control"], row["condition"])].append(row)

    for (subset, donor_control, condition), group in sorted(
        grouped.items(), key=lambda item: condition_sort_key(item[0])
    ):
        payload["summaries"].append(
            {
                "subset": subset,
                "donor_control": donor_control,
                "condition": condition,
                **summarize(group),
            }
        )
    return payload


def fmt(value: float) -> str:
    if value != value:
        return "nan"
    return f"{value:.3f}"


def markdown_table(items: list[dict], title: str) -> list[str]:
    lines = [
        f"## {title}",
        "",
        "| donor | condition | n | seeds | cf action | unpatched action | donor-B action | matched-ref action | cf-vs-unpatched gap | cf-vs-donor-B gap | cf-vs-matched-ref gap | cf=donor-B | cf=unpatched | patch changed |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in items:
        lines.append(
            "| {donor} | {condition} | {n} | {seeds} | {cf} | {unpatched} | "
            "{donor_b} | {matched} | {gap_unpatched} | {gap_donor_b} | "
            "{gap_matched} | {cf_eq_b} | {cf_eq_unpatched} | {changed} |".format(
                donor=item["donor_control"],
                condition=item["condition"],
                n=item["n_rows"],
                seeds=item["n_source_seeds"],
                cf=fmt(item["source_cf_action_agreement"]),
                unpatched=fmt(item["target_unpatched_action_agreement"]),
                donor_b=fmt(item["donor_source_b_action_agreement"]),
                matched=fmt(item["matched_reference_action_agreement"]),
                gap_unpatched=fmt(item["counterfactual_vs_unpatched_action_gap"]),
                gap_donor_b=fmt(item["counterfactual_vs_donor_source_b_action_gap"]),
                gap_matched=fmt(item["counterfactual_vs_matched_reference_action_gap"]),
                cf_eq_b=fmt(item["source_cf_equals_donor_source_b_action"]),
                cf_eq_unpatched=fmt(item["source_cf_equals_target_unpatched_action"]),
                changed=fmt(item["target_patch_action_changed"]),
            )
        )
    lines.append("")
    return lines


def build_markdown(payload: dict) -> str:
    vector_path = ", ".join(payload["vector_paths"])
    lines = [
        "# Causal Patch Leakage And Shortcut Audit",
        "",
        f"Rows: `{payload['rows_path']}`",
        f"Patch path: `{vector_path}`",
        "",
        "This report checks whether causal-patch action agreement can be explained by simple action-level shortcuts: preserving the target's unpatched action, copying the donor source-B action, or following the stale matched-reference counterfactual action.",
        "",
        "The strongest anti-leakage row subset is `source_cf_differs_from_donor_source_b_action`: on those rows, the donor's ordinary source-B action is not the same as the source counterfactual caused by the patch.",
        "",
    ]
    for subset in SUBSETS:
        items = [item for item in payload["summaries"] if item["subset"] == subset]
        if not items:
            continue
        lines.extend(markdown_table(items, subset))
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit causal patch rows for action-level leakage shortcuts."
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
    for item in payload["summaries"]:
        if item["subset"] != "source_cf_differs_from_donor_source_b_action":
            continue
        if item["condition"] != "b_source_align_attention_copy_long":
            continue
        print(
            "{donor}/{condition} n={n_rows} cf={cf:.3f} donorB={donor_b:.3f} "
            "unpatched={unpatched:.3f} matchedRef={matched:.3f}".format(
                donor=item["donor_control"],
                condition=item["condition"],
                n_rows=item["n_rows"],
                cf=item["source_cf_action_agreement"],
                donor_b=item["donor_source_b_action_agreement"],
                unpatched=item["target_unpatched_action_agreement"],
                matched=item["matched_reference_action_agreement"],
            )
        )


if __name__ == "__main__":
    main()
