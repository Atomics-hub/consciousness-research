#!/usr/bin/env python3
import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

from benchmark.stats import compare_paired, holm_bonferroni


DEFAULT_CONTRASTS = (
    ("self_report_corr", "source_full", "source_schema_ablated"),
    ("self_report_corr", "b_adapter_repair_copy", "b_frozen_copy"),
    ("self_report_corr", "b_source_align_repair_copy", "b_frozen_copy"),
    ("self_report_corr", "b_source_align_repair_copy_long", "b_frozen_copy"),
    ("self_report_corr", "b_source_align_repair_copy_long", "b_source_align_repair_copy"),
    ("self_report_corr", "b_source_align_policy_copy_long", "b_source_align_repair_copy_long"),
    ("self_report_corr", "b_source_align_attention_copy_long", "b_source_align_repair_copy_long"),
    ("self_report_corr", "b_source_align_attention_adapter_long", "b_source_align_repair_copy_long"),
    ("self_report_corr", "b_source_align_control_adapter_long", "b_source_align_repair_copy_long"),
    ("self_report_corr", "b_source_align_attention_copy_trainable_long", "b_source_align_repair_copy_long"),
    ("self_report_corr", "b_source_align_attention_copy_random_adapter_long", "b_source_align_repair_copy_long"),
    ("self_report_corr", "b_source_align_identity_adapter_long", "b_source_align_repair_copy_long"),
    ("self_report_corr", "b_source_align_attention_adapter_long", "b_source_align_attention_copy_long"),
    ("self_report_corr", "b_source_align_control_adapter_long", "b_source_align_attention_adapter_long"),
    ("self_report_corr", "b_source_align_control_adapter_long", "b_source_align_attention_copy_long"),
    ("self_report_corr", "b_source_align_attention_adapter_long", "b_source_align_attention_copy_trainable_long"),
    ("self_report_corr", "b_source_align_attention_adapter_long", "b_source_align_attention_copy_random_adapter_long"),
    ("self_report_corr", "b_source_align_attention_copy_trainable_long", "b_source_align_attention_copy_long"),
    ("self_report_corr", "b_source_align_attention_copy_trainable_long", "b_source_align_attention_copy_random_adapter_long"),
    ("self_report_corr", "b_source_align_attention_copy_long", "b_source_align_attention_copy_random_adapter_long"),
    ("self_report_corr", "b_source_align_attention_copy_long", "b_source_align_identity_adapter_long"),
    ("self_report_corr", "b_source_align_policy_copy_long", "b_frozen_copy"),
    ("self_report_corr", "b_source_align_attention_copy_long", "b_frozen_copy"),
    ("self_report_corr", "b_source_align_attention_adapter_long", "b_frozen_copy"),
    ("self_report_corr", "b_source_align_control_adapter_long", "b_frozen_copy"),
    ("self_report_corr", "b_source_align_attention_copy_trainable_long", "b_frozen_copy"),
    ("self_report_corr", "b_source_align_attention_copy_random_adapter_long", "b_frozen_copy"),
    ("self_report_corr", "b_source_align_identity_adapter_long", "b_frozen_copy"),
    ("self_report_corr", "b_source_align_repair_copy", "b_behavior_distill"),
    ("self_report_corr", "b_source_align_repair_copy_long", "b_behavior_distill"),
    ("self_report_corr", "b_source_align_policy_copy_long", "b_behavior_distill"),
    ("self_report_corr", "b_source_align_attention_copy_long", "b_behavior_distill"),
    ("self_report_corr", "b_source_align_attention_adapter_long", "b_behavior_distill"),
    ("self_report_corr", "b_source_align_control_adapter_long", "b_behavior_distill"),
    ("self_report_corr", "b_source_align_attention_copy_trainable_long", "b_behavior_distill"),
    ("self_report_corr", "b_source_align_attention_copy_random_adapter_long", "b_behavior_distill"),
    ("self_report_corr", "b_source_align_identity_adapter_long", "b_behavior_distill"),
    ("self_report_corr", "b_adapter_repair_copy", "b_behavior_distill"),
    ("self_report_corr", "b_trainable_copy", "b_trainable_random"),
    ("self_report_corr", "b_trainable_copy", "b_behavior_distill"),
    ("identity_probe_accuracy", "b_adapter_repair_copy", "b_frozen_random"),
    ("identity_probe_accuracy", "b_source_align_repair_copy", "b_frozen_random"),
    ("identity_probe_accuracy", "b_source_align_repair_copy_long", "b_frozen_random"),
    ("identity_probe_accuracy", "b_source_align_policy_copy_long", "b_frozen_random"),
    ("identity_probe_accuracy", "b_source_align_attention_copy_long", "b_frozen_random"),
    ("identity_probe_accuracy", "b_source_align_attention_adapter_long", "b_frozen_random"),
    ("identity_probe_accuracy", "b_source_align_control_adapter_long", "b_frozen_random"),
    ("identity_probe_accuracy", "b_source_align_attention_copy_trainable_long", "b_frozen_random"),
    ("identity_probe_accuracy", "b_source_align_attention_copy_random_adapter_long", "b_frozen_random"),
    ("identity_probe_accuracy", "b_source_align_identity_adapter_long", "b_frozen_random"),
    ("identity_probe_accuracy", "b_source_align_repair_copy", "b_behavior_distill"),
    ("identity_probe_accuracy", "b_source_align_repair_copy_long", "b_behavior_distill"),
    ("identity_probe_accuracy", "b_source_align_policy_copy_long", "b_behavior_distill"),
    ("identity_probe_accuracy", "b_source_align_attention_copy_long", "b_behavior_distill"),
    ("identity_probe_accuracy", "b_source_align_attention_adapter_long", "b_behavior_distill"),
    ("identity_probe_accuracy", "b_source_align_control_adapter_long", "b_behavior_distill"),
    ("identity_probe_accuracy", "b_source_align_attention_copy_trainable_long", "b_behavior_distill"),
    ("identity_probe_accuracy", "b_source_align_attention_copy_random_adapter_long", "b_behavior_distill"),
    ("identity_probe_accuracy", "b_source_align_identity_adapter_long", "b_behavior_distill"),
    ("identity_probe_accuracy", "b_adapter_repair_copy", "b_behavior_distill"),
    ("identity_probe_accuracy", "b_trainable_copy", "b_trainable_random"),
    ("reward", "b_adapter_repair_copy", "b_frozen_copy"),
    ("reward", "b_source_align_repair_copy", "b_frozen_copy"),
    ("reward", "b_source_align_repair_copy_long", "b_frozen_copy"),
    ("reward", "b_source_align_repair_copy_long", "b_source_align_repair_copy"),
    ("reward", "b_source_align_policy_copy_long", "b_source_align_repair_copy_long"),
    ("reward", "b_source_align_attention_copy_long", "b_source_align_repair_copy_long"),
    ("reward", "b_source_align_attention_adapter_long", "b_source_align_repair_copy_long"),
    ("reward", "b_source_align_control_adapter_long", "b_source_align_repair_copy_long"),
    ("reward", "b_source_align_attention_copy_trainable_long", "b_source_align_repair_copy_long"),
    ("reward", "b_source_align_attention_copy_random_adapter_long", "b_source_align_repair_copy_long"),
    ("reward", "b_source_align_identity_adapter_long", "b_source_align_repair_copy_long"),
    ("reward", "b_source_align_attention_adapter_long", "b_source_align_attention_copy_long"),
    ("reward", "b_source_align_control_adapter_long", "b_source_align_attention_adapter_long"),
    ("reward", "b_source_align_control_adapter_long", "b_source_align_attention_copy_long"),
    ("reward", "b_source_align_attention_adapter_long", "b_source_align_attention_copy_trainable_long"),
    ("reward", "b_source_align_attention_adapter_long", "b_source_align_attention_copy_random_adapter_long"),
    ("reward", "b_source_align_attention_copy_trainable_long", "b_source_align_attention_copy_long"),
    ("reward", "b_source_align_attention_copy_trainable_long", "b_source_align_attention_copy_random_adapter_long"),
    ("reward", "b_source_align_attention_copy_long", "b_source_align_attention_copy_random_adapter_long"),
    ("reward", "b_source_align_attention_copy_long", "b_source_align_identity_adapter_long"),
    ("reward", "b_source_align_policy_copy_long", "b_frozen_copy"),
    ("reward", "b_source_align_attention_copy_long", "b_frozen_copy"),
    ("reward", "b_source_align_attention_adapter_long", "b_frozen_copy"),
    ("reward", "b_source_align_control_adapter_long", "b_frozen_copy"),
    ("reward", "b_source_align_attention_copy_trainable_long", "b_frozen_copy"),
    ("reward", "b_source_align_attention_copy_random_adapter_long", "b_frozen_copy"),
    ("reward", "b_source_align_identity_adapter_long", "b_frozen_copy"),
    ("reward", "b_source_align_repair_copy", "b_behavior_distill"),
    ("reward", "b_source_align_repair_copy_long", "b_behavior_distill"),
    ("reward", "b_source_align_policy_copy_long", "b_behavior_distill"),
    ("reward", "b_source_align_attention_copy_long", "b_behavior_distill"),
    ("reward", "b_source_align_attention_adapter_long", "b_behavior_distill"),
    ("reward", "b_source_align_control_adapter_long", "b_behavior_distill"),
    ("reward", "b_source_align_attention_copy_trainable_long", "b_behavior_distill"),
    ("reward", "b_source_align_attention_copy_random_adapter_long", "b_behavior_distill"),
    ("reward", "b_source_align_identity_adapter_long", "b_behavior_distill"),
    ("reward", "b_adapter_repair_copy", "b_behavior_distill"),
    ("reward", "b_trainable_copy", "b_trainable_random"),
    ("reward", "b_trainable_copy", "b_behavior_distill"),
    ("reward", "b_adapter_repair_copy", "b_full_retrain"),
    ("goal_attention_mass", "b_source_align_attention_copy_long", "b_source_align_repair_copy_long"),
    ("goal_attention_mass", "b_source_align_attention_adapter_long", "b_source_align_repair_copy_long"),
    ("goal_attention_mass", "b_source_align_control_adapter_long", "b_source_align_repair_copy_long"),
    ("goal_attention_mass", "b_source_align_attention_copy_trainable_long", "b_source_align_repair_copy_long"),
    ("goal_attention_mass", "b_source_align_control_adapter_long", "b_source_align_attention_adapter_long"),
    ("goal_attention_mass", "b_source_align_control_adapter_long", "b_source_align_attention_copy_long"),
    ("goal_attention_mass", "b_source_align_attention_adapter_long", "b_source_align_attention_copy_long"),
    ("source_action_agreement", "b_source_align_attention_copy_long", "b_source_align_repair_copy_long"),
    ("source_action_agreement", "b_source_align_attention_adapter_long", "b_source_align_repair_copy_long"),
    ("source_action_agreement", "b_source_align_control_adapter_long", "b_source_align_repair_copy_long"),
    ("source_action_agreement", "b_source_align_attention_copy_trainable_long", "b_source_align_repair_copy_long"),
    ("source_action_agreement", "b_source_align_control_adapter_long", "b_source_align_attention_adapter_long"),
    ("source_action_agreement", "b_source_align_control_adapter_long", "b_source_align_attention_copy_long"),
    ("source_action_agreement", "b_source_align_attention_adapter_long", "b_source_align_attention_copy_long"),
    ("source_attention_l1", "b_source_align_attention_copy_long", "b_source_align_repair_copy_long"),
    ("source_attention_l1", "b_source_align_attention_adapter_long", "b_source_align_repair_copy_long"),
    ("source_attention_l1", "b_source_align_control_adapter_long", "b_source_align_repair_copy_long"),
    ("source_attention_l1", "b_source_align_attention_copy_trainable_long", "b_source_align_repair_copy_long"),
    ("source_attention_l1", "b_source_align_control_adapter_long", "b_source_align_attention_adapter_long"),
    ("source_attention_l1", "b_source_align_control_adapter_long", "b_source_align_attention_copy_long"),
    ("source_attention_l1", "b_source_align_attention_adapter_long", "b_source_align_attention_copy_long"),
    ("source_feature_mse", "b_source_align_attention_copy_long", "b_source_align_repair_copy_long"),
    ("source_feature_mse", "b_source_align_attention_adapter_long", "b_source_align_repair_copy_long"),
    ("source_feature_mse", "b_source_align_control_adapter_long", "b_source_align_repair_copy_long"),
    ("source_feature_mse", "b_source_align_attention_copy_trainable_long", "b_source_align_repair_copy_long"),
    ("source_feature_mse", "b_source_align_control_adapter_long", "b_source_align_attention_adapter_long"),
    ("source_feature_mse", "b_source_align_control_adapter_long", "b_source_align_attention_copy_long"),
    ("source_feature_mse", "b_source_align_attention_adapter_long", "b_source_align_attention_copy_long"),
)


def parse_contrast(raw: str) -> tuple[str, str, str]:
    parts = raw.split(":")
    if len(parts) != 3:
        raise argparse.ArgumentTypeError("Contrasts must use metric:condition_a:condition_b.")
    return parts[0], parts[1], parts[2]


def load_seed_values(rows: list[dict]) -> dict:
    values = defaultdict(dict)
    for row in rows:
        condition = row["condition"]
        train_idx = int(row["training_seed_index"])
        for key, value in row.items():
            if isinstance(value, (int, float)):
                values[(condition, key)][train_idx] = float(value)
    return values


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


def paired_values(values: dict, metric: str, condition_a: str, condition_b: str):
    a_by_seed = values[(condition_a, metric)]
    b_by_seed = values[(condition_b, metric)]
    shared = sorted(set(a_by_seed) & set(b_by_seed))
    return [a_by_seed[i] for i in shared], [b_by_seed[i] for i in shared]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run paired contrasts from seed summaries.")
    parser.add_argument("summary_json", type=Path)
    parser.add_argument(
        "--contrast",
        action="append",
        type=parse_contrast,
        default=None,
        help="metric:condition_a:condition_b. Can be repeated.",
    )
    parser.add_argument("--alpha", type=float, default=0.05)
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

    rows = json.loads(args.summary_json.read_text())
    if args.validated_only:
        passed = load_validated_seed_indices(args.summary_json, args.run_dir)
        rows = [row for row in rows if int(row["training_seed_index"]) in passed]

    values = load_seed_values(rows)
    contrasts = args.contrast or list(DEFAULT_CONTRASTS)

    results = []
    for metric, condition_a, condition_b in contrasts:
        try:
            a_vals, b_vals = paired_values(values, metric, condition_a, condition_b)
        except KeyError:
            continue
        if not a_vals:
            continue
        results.append(
            compare_paired(
                metric=metric,
                condition_a=condition_a,
                condition_b=condition_b,
                values_a=a_vals,
                values_b=b_vals,
            )
        )

    significant = holm_bonferroni([r.p_value for r in results], alpha=args.alpha)

    columns = [
        "metric",
        "contrast",
        "n",
        "mean_a",
        "mean_b",
        "mean_diff",
        "ci_low",
        "ci_high",
        "dz",
        "p",
        "holm_sig",
    ]
    print("| " + " | ".join(columns) + " |")
    print("| " + " | ".join(["---"] * len(columns)) + " |")
    for result, sig in zip(results, significant):
        row = [
            result.metric,
            f"{result.condition_a} - {result.condition_b}",
            str(result.n_pairs),
            f"{result.mean_a:.3f}",
            f"{result.mean_b:.3f}",
            f"{result.mean_diff:.3f}",
            f"{result.ci_low:.3f}",
            f"{result.ci_high:.3f}",
            f"{result.cohen_dz:.3f}",
            f"{result.p_value:.4f}",
            "yes" if sig else "no",
        ]
        print("| " + " | ".join(row) + " |")


if __name__ == "__main__":
    main()
