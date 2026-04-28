#!/usr/bin/env python3
import argparse
import json
import re
from collections import defaultdict
from pathlib import Path


DEFAULT_COLUMNS = (
    "training_seed_index",
    "condition",
    "reward",
    "goals_found",
    "distractor_capture_rate",
    "self_report_corr",
    "identity_probe_accuracy",
    "memory_overlap",
    "goal_attention_mass",
    "distractor_attention_mass",
    "source_attention_l1",
    "source_feature_mse",
    "source_action_agreement",
)


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


def format_value(value) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def print_rows(rows: list[dict], columns: list[str]) -> None:
    print("| " + " | ".join(columns) + " |")
    print("| " + " | ".join(["---"] * len(columns)) + " |")
    for row in rows:
        print("| " + " | ".join(format_value(row.get(col, "")) for col in columns) + " |")


def print_means(rows: list[dict], columns: list[str]) -> None:
    metric_columns = [c for c in columns if c not in ("training_seed_index", "condition")]
    groups = defaultdict(list)
    for row in rows:
        groups[row["condition"]].append(row)

    output_columns = ["condition", "n", *metric_columns]
    print("| " + " | ".join(output_columns) + " |")
    print("| " + " | ".join(["---"] * len(output_columns)) + " |")
    for condition, condition_rows in groups.items():
        values = [condition, str(len(condition_rows))]
        for col in metric_columns:
            numeric = [row[col] for row in condition_rows if isinstance(row.get(col), (int, float))]
            values.append(format_value(sum(numeric) / len(numeric)) if numeric else "")
        print("| " + " | ".join(values) + " |")


def main() -> None:
    parser = argparse.ArgumentParser(description="Print a Markdown table from seed summaries.")
    parser.add_argument("summary_json", type=Path)
    parser.add_argument("--columns", nargs="*", default=list(DEFAULT_COLUMNS))
    parser.add_argument(
        "--means",
        action="store_true",
        help="Print condition means instead of one row per seed and condition.",
    )
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
    columns = list(args.columns)

    if args.validated_only:
        passed = load_validated_seed_indices(args.summary_json, args.run_dir)
        rows = [row for row in rows if int(row["training_seed_index"]) in passed]

    if args.means:
        print_means(rows, columns)
    else:
        print_rows(rows, columns)


if __name__ == "__main__":
    main()
