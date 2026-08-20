#!/usr/bin/env python3
"""Generate deterministic Paper 8 stage-1 tables and SVG figures.

The scientific-data inputs are the zero-call redesigned-gate result and the
separate amendment-v1 dependence diagnostic.  Both record local deterministic
construction or seeded synthetic planning only: neither contains provider/model
observations or authorizes external action.  The dependence diagnostic is
strictly non-gating and cannot certify B=384.  This script uses only the Python
standard library, emits no timestamps, and writes only below
``outputs/paper8_stage1_release_v0``.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import io
import json
import math
from pathlib import Path
import sys
import tempfile
from typing import Any, Iterable, Mapping, Sequence


OUTPUT_ROOT = Path(__file__).resolve().parent
WORKSPACE_ROOT = OUTPUT_ROOT.parents[1]
SOURCE_PATH = WORKSPACE_ROOT / "zero_call" / "results" / "redesign_gate_results.json"
DEPENDENCE_SOURCE_PATH = (
    OUTPUT_ROOT / "amendment_v1" / "results" / "dependence_diagnostics.json"
)

PLANNING_LABEL = "SYNTHETIC PLANNING ONLY — NO PROVIDER/MODEL OBSERVATIONS"
DEPENDENCE_LABEL = (
    "NON-GATING SYNTHETIC SCREEN — NO PROVIDER OBSERVATIONS — CANNOT CERTIFY B=384"
)
FONT_STACK = "Arial, Helvetica, sans-serif"

DEPENDENCE_TOP_LEVEL_KEYS = {
    "schema_version",
    "generated_date",
    "status",
    "gate_effect",
    "numerical_gate_eligible",
    "master_seed",
    "scope",
    "claim_ceiling",
    "assignment_audit",
    "design",
    "dgp",
    "formation_diagnostics",
    "outcome_diagnostics",
    "method",
    "rng_method",
}
DEPENDENCE_DESIGN_KEYS = {
    "macro_cells",
    "fine_strata_per_macro_cell",
    "required_fine_strata",
    "blocks_per_macro_cell",
    "blocks_per_fine_stratum",
    "sessions_per_block",
    "outcome_batches",
    "outcome_replicates_per_cell",
    "formation_replicates_per_cell",
    "alpha",
    "positive_threshold",
    "equivalence_margins_L_H_U",
}
DEPENDENCE_FORMATION_KEYS = {
    "profile",
    "high_probability_given_valid",
    "semantic_validity_probability",
    "attempt_cap_per_fine_stratum",
    "attempt_batch_size",
    "target_blocks_per_fine_stratum",
    "required_fine_strata",
    "probability_bounds",
    "outer_replicates",
    "whole_panel_support_rate",
    "supported_strata_quantiles",
    "total_attempts_quantiles",
    "semantic_invalid_quantiles",
    "unmatched_valid_quantiles",
    "retained_blocks_quantiles",
    "stopping_rule",
}
DEPENDENCE_OUTCOME_KEYS = {
    "label",
    "scenario",
    "dependence_profile",
    "failure_profile",
    "blocks_per_macro_cell",
    "blocks_per_fine_stratum",
    "outer_replicates",
    "outcome_probability_bounds",
    "failure_probability_bounds",
    "analytic_terminal_truth_L_H_U",
    "truth_roles",
    "decision_rates",
    "empirical_standard_deviation",
    "mean_reported_standard_error",
    "mean_reported_variance",
    "empirical_to_reported_variance_ratio",
    "macro_estimate_correlation_by_category",
    "terminal_sources_by_arm_schedule",
    "donor_pair_agreement",
}
WILSON_KEYS = {
    "successes",
    "replicates",
    "estimate",
    "interval_lower",
    "interval_upper",
    "confidence_level",
    "interval_method",
}
QUANTILE_KEYS = {"minimum", "p05", "p50", "p95", "maximum"}
EXPECTED_OUTCOME_PROFILES = (
    ("positive15_independent_none", "positive_15", "independent", "none"),
    ("positive15_donor_symmetric", "positive_15", "donor_only", "symmetric"),
    ("positive15_shared_symmetric", "positive_15", "shared_shocks", "symmetric"),
    ("positive15_joint_symmetric", "positive_15", "joint", "symmetric"),
    ("positive15_joint_differential", "positive_15", "joint", "differential"),
    ("null_joint_symmetric", "null", "joint", "symmetric"),
    ("null_joint_differential", "null", "joint", "differential"),
    ("boundary_joint_symmetric", "positive_boundary", "joint", "symmetric"),
)
EXPECTED_FORMATION_CELLS = tuple(
    (profile, high_probability, cap)
    for profile in ("independent", "provider_batch")
    for high_probability, cap in ((0.1, 1024), (0.3, 331), (0.5, 194))
)


class ArtifactError(RuntimeError):
    """Raised when the sealed result shape cannot support a requested artifact."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ArtifactError(message)


def as_mapping(value: Any, label: str) -> Mapping[str, Any]:
    require(isinstance(value, dict), f"{label} must be an object")
    return value


def as_sequence(value: Any, label: str) -> Sequence[Any]:
    require(isinstance(value, list), f"{label} must be an array")
    return value


def finite_number(value: Any, label: str) -> float:
    require(
        isinstance(value, (int, float)) and not isinstance(value, bool),
        f"{label} must be numeric",
    )
    converted = float(value)
    require(math.isfinite(converted), f"{label} must be finite")
    return converted


def integer(value: Any, label: str) -> int:
    require(isinstance(value, int) and not isinstance(value, bool), f"{label} must be an integer")
    return value


def text(value: Any, label: str) -> str:
    require(isinstance(value, str) and value != "", f"{label} must be nonempty text")
    return value


def exact_keys(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    observed = set(value)
    require(
        observed == expected,
        f"{label} keys drifted; missing={sorted(expected - observed)}, "
        f"extra={sorted(observed - expected)}",
    )


def scalar(value: int | float) -> str:
    if isinstance(value, int):
        return str(value)
    cleaned = 0.0 if abs(value) <= 1e-12 else value
    # Twelve significant digits retain far more precision than the manuscript
    # display requires while avoiding irrelevant IEEE-754 representation tails.
    return format(cleaned, ".12g")


def source_scalar(value: int | float) -> str:
    """Serialize a validated source number without display-time normalization."""

    require(isinstance(value, (int, float)) and not isinstance(value, bool), "source scalar must be numeric")
    require(math.isfinite(float(value)), "source scalar must be finite")
    return json.dumps(value, allow_nan=False, separators=(",", ":"))


def percent(value: float, digits: int = 2) -> str:
    cleaned = 0.0 if abs(value) <= 1e-12 else value
    return f"{100.0 * cleaned:.{digits}f}%"


def display_delta(value: float) -> str:
    cleaned = 0.0 if abs(value) <= 1e-12 else value
    return f"{cleaned:+.4f}"


def write_text(path: Path, value: str, *, output_root: Path = OUTPUT_ROOT) -> None:
    require(path == output_root or output_root in path.parents, "output escaped generation directory")
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = value.replace("\r\n", "\n").replace("\r", "\n")
    if not normalized.endswith("\n"):
        normalized += "\n"
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(normalized)


def write_csv(
    path: Path,
    fieldnames: Sequence[str],
    rows: Iterable[Mapping[str, Any]],
    *,
    output_root: Path = OUTPUT_ROOT,
) -> None:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(
        buffer,
        fieldnames=list(fieldnames),
        extrasaction="raise",
        lineterminator="\n",
    )
    writer.writeheader()
    for row in rows:
        writer.writerow({name: row.get(name, "") for name in fieldnames})
    write_text(path, buffer.getvalue(), output_root=output_root)


def svg_text(
    x: float,
    y: float,
    value: str,
    *,
    size: int = 14,
    weight: int = 400,
    anchor: str = "start",
    fill: str = "#17212b",
    css_class: str | None = None,
) -> str:
    class_attribute = f' class="{html.escape(css_class)}"' if css_class else ""
    return (
        f'<text x="{x:.2f}" y="{y:.2f}" text-anchor="{anchor}" '
        f'font-family="{FONT_STACK}" font-size="{size}" font-weight="{weight}" '
        f'fill="{fill}"{class_attribute}>{html.escape(value)}</text>'
    )


def svg_document(width: int, height: int, title: str, description: str, body: str) -> str:
    return "\n".join(
        [
            '<?xml version="1.0" encoding="UTF-8"?>',
            (
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
                f'height="{height}" viewBox="0 0 {width} {height}" role="img" '
                f'aria-labelledby="title description">'
            ),
            f"<title id=\"title\">{html.escape(title)}</title>",
            f"<desc id=\"description\">{html.escape(description)}</desc>",
            '<rect width="100%" height="100%" fill="#ffffff"/>',
            body,
            "</svg>",
        ]
    )


def load_source() -> tuple[dict[str, Any], str]:
    source_bytes = SOURCE_PATH.read_bytes()
    try:
        document = json.loads(source_bytes)
    except json.JSONDecodeError as error:
        raise ArtifactError("redesigned gate result is not valid JSON") from error
    require(isinstance(document, dict), "redesigned gate result must be an object")
    require(
        document.get("schema_version") == "binding-test-redesigned-zero-call-gate-v1",
        "unexpected redesigned gate schema",
    )
    require(document.get("provider_calls_made") == 0, "source is not zero-provider-call evidence")
    require(document.get("external_spend") == 0, "source reports external spend")
    require(
        document.get("scope") == "local deterministic construction and seeded synthetic numerical certification only",
        "source scope drifted",
    )
    require(
        document.get("external_action_status") == "NO_PROVIDER_CALL_AUTHORIZED",
        "source external-action status drifted",
    )
    return document, hashlib.sha256(source_bytes).hexdigest()


def validate_wilson_rate(
    raw: Any,
    label: str,
    *,
    expected_replicates: int,
) -> Mapping[str, Any]:
    rate = as_mapping(raw, label)
    exact_keys(rate, WILSON_KEYS, label)
    successes = integer(rate.get("successes"), f"{label}.successes")
    replicates = integer(rate.get("replicates"), f"{label}.replicates")
    require(replicates == expected_replicates, f"{label} replicate count drifted")
    require(0 <= successes <= replicates, f"{label} counts are impossible")
    estimate = successes / replicates
    z = 1.959963984540054
    z2 = z * z
    denominator = 1.0 + z2 / replicates
    center = (estimate + z2 / (2.0 * replicates)) / denominator
    radius = z * math.sqrt(
        estimate * (1.0 - estimate) / replicates
        + z2 / (4.0 * replicates * replicates)
    ) / denominator
    expected = {
        "successes": successes,
        "replicates": replicates,
        "estimate": estimate,
        "interval_lower": max(0.0, center - radius),
        "interval_upper": min(1.0, center + radius),
        "confidence_level": 0.95,
        "interval_method": "Wilson score interval for Monte Carlo frequency only",
    }
    require(dict(rate) == expected, f"{label} is inconsistent with its counts")
    return rate


def validate_quantiles(raw: Any, label: str) -> Mapping[str, Any]:
    quantiles = as_mapping(raw, label)
    exact_keys(quantiles, QUANTILE_KEYS, label)
    values = [
        integer(quantiles[key], f"{label}.{key}")
        for key in ("minimum", "p05", "p50", "p95", "maximum")
    ]
    require(values == sorted(values), f"{label} must be nondecreasing")
    require(values[0] >= 0, f"{label} cannot be negative")
    return quantiles


def validate_probability_bounds(raw: Any, label: str) -> Mapping[str, Any]:
    bounds = as_mapping(raw, label)
    exact_keys(bounds, {"minimum", "maximum"}, label)
    minimum = finite_number(bounds["minimum"], f"{label}.minimum")
    maximum = finite_number(bounds["maximum"], f"{label}.maximum")
    require(0.0 <= minimum <= maximum <= 1.0, f"{label} left [0,1]")
    return bounds


def validate_numeric_matrix(raw: Any, label: str, rows: int, columns: int) -> None:
    matrix = as_sequence(raw, label)
    require(len(matrix) == rows, f"{label} row count drifted")
    for row_index, raw_row in enumerate(matrix):
        row = as_sequence(raw_row, f"{label}[{row_index}]")
        require(len(row) == columns, f"{label}[{row_index}] column count drifted")
        for column_index, value in enumerate(row):
            finite_number(value, f"{label}[{row_index}][{column_index}]")


def load_dependence_source() -> tuple[dict[str, Any], str]:
    source_bytes = DEPENDENCE_SOURCE_PATH.read_bytes()

    def reject_constant(value: str) -> None:
        raise ArtifactError(f"dependence diagnostic contains non-finite JSON constant {value}")

    try:
        document = json.loads(source_bytes, parse_constant=reject_constant)
    except json.JSONDecodeError as error:
        raise ArtifactError("dependence diagnostic is not valid JSON") from error
    require(isinstance(document, dict), "dependence diagnostic must be an object")
    exact_keys(document, DEPENDENCE_TOP_LEVEL_KEYS, "dependence diagnostic")
    require(
        document.get("schema_version") == "binding-test-dependence-diagnostic-v1",
        "unexpected dependence diagnostic schema",
    )
    require(document.get("generated_date") == "2026-08-08", "dependence date drifted")
    require(document.get("status") == "NON_GATING_SYNTHETIC_SCREEN", "dependence status drifted")
    require(document.get("gate_effect") == "none", "dependence diagnostic became gating")
    require(document.get("numerical_gate_eligible") is False, "dependence diagnostic became gate eligible")
    require(document.get("master_seed") == 20260808, "dependence master seed drifted")
    require(
        document.get("scope") == "local seeded synthetic dependence and feasibility diagnostics only",
        "dependence scope drifted",
    )
    claim_ceiling = text(document.get("claim_ceiling"), "dependence claim ceiling")
    for required_phrase in (
        "cannot estimate provider dependence",
        "certify or rescue B=384",
        "authorize collection or spend",
    ):
        require(required_phrase in claim_ceiling, f"dependence claim ceiling lost: {required_phrase}")

    assignment = as_mapping(document.get("assignment_audit"), "dependence assignment_audit")
    exact_keys(
        assignment,
        {
            "allowed_assignment_count",
            "sampling_policy",
            "selection_probability",
            "canonical_assignment_table_sha256",
            "donor_rule",
        },
        "dependence assignment_audit",
    )
    require(assignment.get("allowed_assignment_count") == 576, "assignment count drifted")
    require(assignment.get("selection_probability") == "1/576", "assignment probability drifted")
    digest = text(assignment.get("canonical_assignment_table_sha256"), "assignment digest")
    require(len(digest) == 64 and all(character in "0123456789abcdef" for character in digest), "assignment digest malformed")

    design = as_mapping(document.get("design"), "dependence design")
    exact_keys(design, DEPENDENCE_DESIGN_KEYS, "dependence design")
    expected_design = {
        "macro_cells": 4,
        "fine_strata_per_macro_cell": 24,
        "required_fine_strata": 96,
        "blocks_per_macro_cell": 384,
        "blocks_per_fine_stratum": 16,
        "sessions_per_block": 8,
        "outcome_batches": 4,
        "alpha": 0.05,
        "positive_threshold": 0.05,
        "equivalence_margins_L_H_U": [0.05, 0.05, 0.02],
    }
    for key, expected_value in expected_design.items():
        require(design.get(key) == expected_value, f"dependence design.{key} drifted")
    outcome_replicates = integer(
        design.get("outcome_replicates_per_cell"),
        "dependence design.outcome_replicates_per_cell",
    )
    formation_replicates = integer(
        design.get("formation_replicates_per_cell"),
        "dependence design.formation_replicates_per_cell",
    )
    require(outcome_replicates >= 2 and formation_replicates >= 1, "dependence replicate count invalid")

    dgp = as_mapping(document.get("dgp"), "dependence dgp")
    exact_keys(
        dgp,
        {
            "formation_profiles",
            "formation_caps_by_high_probability",
            "formation_provider_batch_shifts",
            "dependence_amplitudes_HL_U_failure",
            "dependence_profiles",
            "scenario_probabilities_conditional_on_no_failure",
            "failure_probabilities_by_arm_schedule",
            "failure_mapping",
            "outcome_profiles",
        },
        "dependence dgp",
    )
    require(dgp.get("formation_profiles") == ["independent", "provider_batch"], "formation profiles drifted")
    require(
        dgp.get("formation_caps_by_high_probability") == {"0.10": 1024, "0.30": 331, "0.50": 194},
        "formation caps drifted",
    )
    expected_declared_outcomes = [
        {
            "label": label,
            "scenario": scenario,
            "dependence_profile": dependence,
            "failure_profile": failure,
        }
        for label, scenario, dependence, failure in EXPECTED_OUTCOME_PROFILES
    ]
    require(dgp.get("outcome_profiles") == expected_declared_outcomes, "declared outcome profiles drifted")
    require(
        dgp.get("failure_mapping")
        == {
            "primary_category": "U",
            "disposition_source": "execution_failure",
            "subtype_probabilities": {"provider_error": 0.75, "transport_error": 0.25},
            "followup_after_failure": False,
            "terminal_rows_per_randomized_session": 1,
        },
        "terminal failure mapping drifted",
    )

    formations = as_sequence(document.get("formation_diagnostics"), "formation_diagnostics")
    require(len(formations) == len(EXPECTED_FORMATION_CELLS), "formation row count drifted")
    for index, (raw, expected_cell) in enumerate(zip(formations, EXPECTED_FORMATION_CELLS)):
        row = as_mapping(raw, f"formation_diagnostics[{index}]")
        exact_keys(row, DEPENDENCE_FORMATION_KEYS, f"formation_diagnostics[{index}]")
        profile, high_probability, cap = expected_cell
        require(row.get("profile") == profile, f"formation_diagnostics[{index}].profile drifted")
        require(row.get("high_probability_given_valid") == high_probability, f"formation_diagnostics[{index}].high probability drifted")
        require(row.get("semantic_validity_probability") == 0.9, f"formation_diagnostics[{index}].validity drifted")
        require(row.get("attempt_cap_per_fine_stratum") == cap, f"formation_diagnostics[{index}].cap drifted")
        require(row.get("attempt_batch_size") == 32, f"formation_diagnostics[{index}].batch drifted")
        require(row.get("target_blocks_per_fine_stratum") == 16, f"formation_diagnostics[{index}].target drifted")
        require(row.get("required_fine_strata") == 96, f"formation_diagnostics[{index}].strata drifted")
        require(row.get("outer_replicates") == formation_replicates, f"formation_diagnostics[{index}].replicates drifted")
        probability_bounds = as_mapping(row.get("probability_bounds"), f"formation_diagnostics[{index}].probability_bounds")
        exact_keys(probability_bounds, {"semantic_validity", "high_given_valid"}, f"formation_diagnostics[{index}].probability_bounds")
        for key in ("semantic_validity", "high_given_valid"):
            values = as_sequence(probability_bounds.get(key), f"formation_diagnostics[{index}].probability_bounds.{key}")
            require(len(values) == 2, f"formation_diagnostics[{index}].probability_bounds.{key} length drifted")
            lower = finite_number(values[0], f"formation_diagnostics[{index}].probability_bounds.{key}[0]")
            upper = finite_number(values[1], f"formation_diagnostics[{index}].probability_bounds.{key}[1]")
            require(0.0 <= lower <= upper <= 1.0, f"formation_diagnostics[{index}].probability_bounds.{key} invalid")
        validate_wilson_rate(
            row.get("whole_panel_support_rate"),
            f"formation_diagnostics[{index}].whole_panel_support_rate",
            expected_replicates=formation_replicates,
        )
        for key in (
            "supported_strata_quantiles",
            "total_attempts_quantiles",
            "semantic_invalid_quantiles",
            "unmatched_valid_quantiles",
            "retained_blocks_quantiles",
        ):
            validate_quantiles(row.get(key), f"formation_diagnostics[{index}].{key}")
        text(row.get("stopping_rule"), f"formation_diagnostics[{index}].stopping_rule")

    outcomes = as_sequence(document.get("outcome_diagnostics"), "outcome_diagnostics")
    require(len(outcomes) == len(EXPECTED_OUTCOME_PROFILES), "outcome row count drifted")
    decision_keys = {
        "positive_all_cells",
        "reverse_all_cells",
        "equivalence_all_cells",
        "simultaneous_coverage_all_12",
    }
    role_keys = {"positive_all_cells", "reverse_all_cells", "equivalence_all_cells"}
    for index, (raw, coordinates) in enumerate(zip(outcomes, EXPECTED_OUTCOME_PROFILES)):
        row = as_mapping(raw, f"outcome_diagnostics[{index}]")
        exact_keys(row, DEPENDENCE_OUTCOME_KEYS, f"outcome_diagnostics[{index}]")
        actual_coordinates = (
            row.get("label"),
            row.get("scenario"),
            row.get("dependence_profile"),
            row.get("failure_profile"),
        )
        require(actual_coordinates == coordinates, f"outcome_diagnostics[{index}] coordinates drifted")
        require(row.get("blocks_per_macro_cell") == 384, f"outcome_diagnostics[{index}].B drifted")
        require(row.get("blocks_per_fine_stratum") == 16, f"outcome_diagnostics[{index}].blocks/fine drifted")
        require(row.get("outer_replicates") == outcome_replicates, f"outcome_diagnostics[{index}].replicates drifted")
        validate_probability_bounds(row.get("outcome_probability_bounds"), f"outcome_diagnostics[{index}].outcome_probability_bounds")
        validate_probability_bounds(row.get("failure_probability_bounds"), f"outcome_diagnostics[{index}].failure_probability_bounds")
        truth = as_sequence(row.get("analytic_terminal_truth_L_H_U"), f"outcome_diagnostics[{index}].truth")
        require(len(truth) == 3, f"outcome_diagnostics[{index}] truth length drifted")
        for truth_index, value in enumerate(truth):
            finite_number(value, f"outcome_diagnostics[{index}].truth[{truth_index}]")
        roles = as_mapping(row.get("truth_roles"), f"outcome_diagnostics[{index}].truth_roles")
        exact_keys(roles, role_keys, f"outcome_diagnostics[{index}].truth_roles")
        require(set(roles.values()) <= {"power", "false_control"}, f"outcome_diagnostics[{index}] truth role invalid")
        rates = as_mapping(row.get("decision_rates"), f"outcome_diagnostics[{index}].decision_rates")
        exact_keys(rates, decision_keys, f"outcome_diagnostics[{index}].decision_rates")
        for metric in sorted(decision_keys):
            validate_wilson_rate(
                rates.get(metric),
                f"outcome_diagnostics[{index}].decision_rates.{metric}",
                expected_replicates=outcome_replicates,
            )
        for key in (
            "empirical_standard_deviation",
            "mean_reported_standard_error",
            "mean_reported_variance",
            "empirical_to_reported_variance_ratio",
        ):
            validate_numeric_matrix(row.get(key), f"outcome_diagnostics[{index}].{key}", 4, 3)

    return document, hashlib.sha256(source_bytes).hexdigest()


def positive_cells(document: Mapping[str, Any]) -> list[dict[str, Any]]:
    certification = as_mapping(
        document.get("confirmatory_size_certification"),
        "confirmatory_size_certification",
    )
    assessments = as_sequence(certification.get("cell_assessments"), "cell_assessments")
    selected: list[dict[str, Any]] = []
    for index, raw in enumerate(assessments):
        row = dict(as_mapping(raw, f"cell_assessments[{index}]"))
        config = as_mapping(row.get("config"), f"cell_assessments[{index}].config")
        if config.get("scenario") == "positive_15":
            require(row.get("metric") == "positive_all_cells", "positive_15 metric drifted")
            require(row.get("role") == "power", "positive_15 role drifted")
            row["_source_index"] = index
            selected.append(row)
    selected.sort(
        key=lambda row: (
            finite_number(as_mapping(row["config"], "positive config")["followup_unavailability"], "U"),
            finite_number(as_mapping(row["config"], "positive config")["block_icc"], "ICC"),
        )
    )
    expected_grid = as_sequence(certification.get("required_sensitivity_grid"), "required_sensitivity_grid")
    observed_grid = [
        [row["config"]["followup_unavailability"], row["config"]["block_icc"]]
        for row in selected
    ]
    require(observed_grid == expected_grid, "positive_15 sensitivity grid is incomplete or reordered")
    return selected


def build_design_summary(document: Mapping[str, Any]) -> list[dict[str, str]]:
    panel = as_mapping(document.get("reference_panel"), "reference_panel")
    certification = as_mapping(
        document.get("confirmatory_size_certification"),
        "confirmatory_size_certification",
    )
    selected_sizes = as_mapping(document.get("selected_sizes"), "selected_sizes")
    selected_positive = as_mapping(selected_sizes.get("positive_15"), "selected_sizes.positive_15")
    resources = as_mapping(document.get("resource_plans"), "resource_plans")
    b384 = as_mapping(as_mapping(resources.get("384"), "resource_plans.384").get("0.50"), "resource_plans.384.0.50")
    cells = positive_cells(document)
    first_config = as_mapping(cells[0].get("config"), "positive config")
    margins = as_sequence(first_config.get("equivalence_margin_items"), "equivalence margins")

    rows: list[dict[str, str]] = []

    def add(section: str, field: str, value: str, unit: str, source: str, note: str = "") -> None:
        rows.append(
            {
                "section": section,
                "field": field,
                "value": value,
                "unit": unit,
                "source_json_path": source,
                "note": note,
            }
        )

    add("evidence", "provider calls made", str(document["provider_calls_made"]), "calls", "provider_calls_made")
    add("evidence", "external spend", str(document["external_spend"]), "currency units", "external_spend")
    add("evidence", "scope", text(document["scope"], "scope"), "", "scope")
    add("panel", "macro cells", str(integer(panel["macro_cells"], "macro cells")), "cells", "reference_panel.macro_cells")
    add("panel", "snapshot slots", "; ".join(as_sequence(panel["snapshot_slots"], "snapshot slots")), "", "reference_panel.snapshot_slots", text(panel["snapshot_status"], "snapshot status"))
    add("panel", "target families", "; ".join(as_sequence(panel["target_families"], "target families")), "", "reference_panel.target_families")
    add("panel", "fine strata per macro cell", str(integer(panel["fine_strata_per_macro_cell"], "fine strata")), "strata/cell", "reference_panel.fine_strata_per_macro_cell")
    add("outcome", "nominal categories", "; ".join(str(item[0]) for item in margins), "", "confirmatory_size_certification.cell_assessments[*].config.equivalence_margin_items")
    for category, margin in margins:
        add("outcome", f"{category} equivalence margin", scalar(finite_number(margin, f"{category} margin")), "probability difference", "confirmatory_size_certification.cell_assessments[*].config.equivalence_margin_items")
    add("inference", "alpha", scalar(finite_number(first_config["alpha"], "alpha")), "one-sided level", "confirmatory_size_certification.cell_assessments[*].config.alpha")
    add("inference", "positive threshold", scalar(finite_number(first_config["positive_threshold"], "positive threshold")), "probability difference", "confirmatory_size_certification.cell_assessments[*].config.positive_threshold")
    add("selected design", "blocks per macro cell", str(integer(selected_positive["blocks_per_macro_cell"], "selected B")), "blocks/cell", "selected_sizes.positive_15.blocks_per_macro_cell")
    add("selected design", "blocks per fine stratum", str(integer(certification["blocks_per_fine_stratum"], "blocks per fine stratum")), "blocks/stratum", "confirmatory_size_certification.blocks_per_fine_stratum")
    add("selected design", "total retained blocks", str(integer(b384["retained_blocks"], "retained blocks")), "blocks", "resource_plans.384.0.50.retained_blocks", "Invariant across stored support assumptions at B=384.")
    add("selected design", "active randomized sessions", str(integer(b384["retained_sessions"], "retained sessions")), "sessions", "resource_plans.384.0.50.retained_sessions", "No provider sessions were collected; this is a planned count.")
    add("simulation", "master seed", str(integer(document["master_seed"], "master seed")), "seed", "master_seed")
    add("simulation", "required sensitivity cells", str(len(as_sequence(certification["required_sensitivity_grid"], "sensitivity grid"))), "U×ICC cells", "confirmatory_size_certification.required_sensitivity_grid", "Count derived from the stored exact grid.")
    add("simulation", "gating assessments", str(len(as_sequence(certification["cell_assessments"], "cell assessments"))), "scenario×sensitivity cells", "confirmatory_size_certification.cell_assessments")
    return rows


def build_heatmap_rows(document: Mapping[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for cell in positive_cells(document):
        config = as_mapping(cell["config"], "positive config")
        rate = as_mapping(cell["rate"], "positive rate")
        index = integer(cell["_source_index"], "source index")
        rows.append(
            {
                "followup_unavailability": scalar(finite_number(config["followup_unavailability"], "U")),
                "block_icc": scalar(finite_number(config["block_icc"], "ICC")),
                "blocks_per_macro_cell": str(integer(config["blocks_per_macro_cell"], "B")),
                "outer_replicates": str(integer(rate["replicates"], "replicates")),
                "successes": str(integer(rate["successes"], "successes")),
                "decision_rate": scalar(finite_number(rate["estimate"], "estimate")),
                "wilson_lower": scalar(finite_number(rate["interval_lower"], "lower")),
                "wilson_upper": scalar(finite_number(rate["interval_upper"], "upper")),
                "decision_rate_percent": percent(finite_number(rate["estimate"], "estimate")),
                "wilson_95_percent": (
                    f"[{percent(finite_number(rate['interval_lower'], 'lower'))}, "
                    f"{percent(finite_number(rate['interval_upper'], 'upper'))}]"
                ),
                "source_json_path": f"confirmatory_size_certification.cell_assessments[{index}]",
            }
        )
    return rows


def build_frontier_rows(document: Mapping[str, Any]) -> list[dict[str, str]]:
    frontiers = as_mapping(document.get("sample_size_frontiers"), "sample_size_frontiers")
    labels = {
        "positive_15": "+15pp paired H-up/L-down",
        "positive_1055": "+10.55pp paired H-up/L-down",
        "equivalence_null": "Observed-vector equivalence",
    }
    rows: list[dict[str, str]] = []
    for series in ("positive_15", "positive_1055", "equivalence_null"):
        values = as_sequence(frontiers.get(series), f"sample_size_frontiers.{series}")
        previous = -1
        for index, raw in enumerate(values):
            row = as_mapping(raw, f"sample_size_frontiers.{series}[{index}]")
            blocks = integer(row["blocks_per_macro_cell"], "frontier B")
            require(blocks > previous, f"{series} frontier must be strictly ordered")
            previous = blocks
            estimate = finite_number(row["estimate"], "frontier estimate")
            lower = finite_number(row["wilson_lower"], "frontier lower")
            upper = finite_number(row["wilson_upper"], "frontier upper")
            rows.append(
                {
                    "series": series,
                    "series_label": labels[series],
                    "blocks_per_macro_cell": str(blocks),
                    "outer_replicates": str(integer(row["outer_replicates"], "frontier replicates")),
                    "decision_rate": scalar(estimate),
                    "wilson_lower": scalar(lower),
                    "wilson_upper": scalar(upper),
                    "decision_rate_percent": percent(estimate),
                    "wilson_95_percent": f"[{percent(lower)}, {percent(upper)}]",
                    "source_json_path": f"sample_size_frontiers.{series}[{index}]",
                }
            )
    return rows


def build_false_control_rows(document: Mapping[str, Any]) -> list[dict[str, str]]:
    certification = as_mapping(
        document.get("confirmatory_size_certification"),
        "confirmatory_size_certification",
    )
    assessments = as_sequence(certification.get("cell_assessments"), "cell_assessments")
    grouped: dict[str, list[tuple[int, Mapping[str, Any]]]] = {}
    for index, raw in enumerate(assessments):
        row = as_mapping(raw, f"cell_assessments[{index}]")
        if row.get("role") != "false_control":
            continue
        config = as_mapping(row.get("config"), f"cell_assessments[{index}].config")
        scenario = text(config.get("scenario"), "false-control scenario")
        grouped.setdefault(scenario, []).append((index, row))

    expected = {
        str(metric[0])
        for metric in as_sequence(
            certification.get("required_gating_scenario_metrics"),
            "required_gating_scenario_metrics",
        )
        if str(metric[2]) == "false_control"
    }
    require(set(grouped) == expected, "false-control scenario coverage drifted")

    rows: list[dict[str, str]] = []
    for scenario in sorted(grouped):
        values = grouped[scenario]
        estimates = [finite_number(as_mapping(row["rate"], "rate")["estimate"], "estimate") for _, row in values]
        uppers = [finite_number(as_mapping(row["rate"], "rate")["interval_upper"], "upper") for _, row in values]
        replicates = {integer(as_mapping(row["rate"], "rate")["replicates"], "replicates") for _, row in values}
        thresholds = {finite_number(row["threshold"], "threshold") for _, row in values}
        require(len(replicates) == 1 and len(thresholds) == 1, f"{scenario} false-control contract drifted")
        rows.append(
            {
                "scenario": scenario,
                "sensitivity_cells": str(len(values)),
                "replicates_per_cell": str(next(iter(replicates))),
                "maximum_decision_rate": scalar(max(estimates)),
                "maximum_decision_rate_percent": percent(max(estimates)),
                "maximum_wilson_upper": scalar(max(uppers)),
                "maximum_wilson_upper_percent": percent(max(uppers), 3),
                "criterion_maximum_wilson_upper": scalar(next(iter(thresholds))),
                "all_cells_passed": str(all(bool(row["passed"]) for _, row in values)).lower(),
                "source_json_path": (
                    "confirmatory_size_certification.cell_assessments"
                    f" (role=false_control, scenario={scenario})"
                ),
            }
        )
    return rows


def build_support_rows(document: Mapping[str, Any]) -> list[dict[str, str]]:
    resources = as_mapping(document.get("resource_plans"), "resource_plans")
    selected = as_mapping(resources.get("384"), "resource_plans.384")
    rows: list[dict[str, str]] = []
    for probability in sorted(selected, key=float):
        source = f"resource_plans.384.{probability}"
        row = as_mapping(selected[probability], source)
        generation_range = as_sequence(row["known_generation_requests_range"], f"{source}.known_generation_requests_range")
        require(len(generation_range) == 2 and generation_range[0] == generation_range[1], "B=384 request cap is not exact")
        rows.append(
            {
                "p_high_given_valid": scalar(finite_number(row["assumed_high_probability_given_valid"], "p_high")),
                "semantic_validity_probability": scalar(finite_number(row["assumed_semantic_validity_probability"], "validity")),
                "blocks_per_macro_cell": str(integer(row["blocks_per_macro_cell"], "B")),
                "blocks_per_fine_stratum": str(integer(row["blocks_per_fine_stratum"], "blocks/fine")),
                "attempted_sessions_per_fine_stratum": str(integer(row["attempted_sessions_per_fine_stratum"], "attempts/fine")),
                "attempted_sessions": str(integer(row["attempted_sessions"], "attempts")),
                "retained_blocks": str(integer(row["retained_blocks"], "blocks")),
                "active_randomized_sessions": str(integer(row["retained_sessions"], "sessions")),
                "active_design_generation_request_cap": str(integer(generation_range[1], "request cap")),
                "union_bound_global_support_lower_bound": scalar(finite_number(row["union_bound_global_support_lower_bound"], "support lower")),
                "dollar_cost": "" if row["dollar_cost"] is None else scalar(finite_number(row["dollar_cost"], "dollar cost")),
                "source_json_path": source,
            }
        )
    return rows


def build_latent_rows(document: Mapping[str, Any]) -> list[dict[str, str]]:
    sensitivity = as_mapping(document.get("latent_binary_sensitivity"), "latent_binary_sensitivity")
    examples = as_mapping(
        sensitivity.get("declared_worst_sensitivity_examples"),
        "declared_worst_sensitivity_examples",
    )
    preferred_order = (
        "null",
        "availability_only",
        "fine_stratum_heterogeneity",
        "positive_1055",
        "positive_15",
        "negative_15",
    )
    require(set(examples) == set(preferred_order), "latent-sensitivity scenario set drifted")
    rows: list[dict[str, str]] = []
    for scenario in preferred_order:
        source = f"latent_binary_sensitivity.declared_worst_sensitivity_examples.{scenario}"
        example = as_mapping(examples[scenario], source)
        macro_cells = as_mapping(example["macro_cells"], f"{source}.macro_cells")
        require(len(macro_cells) == 4, f"{scenario} must include four macro cells")
        signatures: set[tuple[float, float, float]] = set()
        for value in macro_cells.values():
            cell = as_mapping(value, f"{source}.macro_cells[*]")
            bounds = as_sequence(cell["latent_binary_high_contrast_bounds"], "latent bounds")
            require(len(bounds) == 2, "latent bound must have two endpoints")
            signatures.add(
                (
                    finite_number(cell["observed_high_contrast"], "observed contrast"),
                    finite_number(bounds[0], "lower bound"),
                    finite_number(bounds[1], "upper bound"),
                )
            )
        require(len(signatures) == 1, f"{scenario} macro-cell sensitivity records differ")
        observed, lower, upper = next(iter(signatures))
        rows.append(
            {
                "scenario": scenario,
                "followup_unavailability": scalar(finite_number(example["followup_unavailability"], "U")),
                "block_icc": scalar(finite_number(example["block_icc"], "ICC")),
                "observed_high_contrast": scalar(observed),
                "latent_binary_lower": scalar(lower),
                "latent_binary_upper": scalar(upper),
                "macro_cells_with_same_record": str(len(macro_cells)),
                "gating_role": "non-gating analytical sensitivity",
                "source_json_path": source,
            }
        )
    return rows


def build_dependence_outcome_rows(document: Mapping[str, Any]) -> list[dict[str, str]]:
    outcomes = as_sequence(document.get("outcome_diagnostics"), "outcome_diagnostics")
    rows: list[dict[str, str]] = []
    metric_prefixes = (
        ("positive_all_cells", "positive"),
        ("reverse_all_cells", "reverse"),
        ("equivalence_all_cells", "equivalence"),
        ("simultaneous_coverage_all_12", "coverage_12"),
    )
    for index, raw in enumerate(outcomes):
        outcome = as_mapping(raw, f"outcome_diagnostics[{index}]")
        truth = as_sequence(
            outcome.get("analytic_terminal_truth_L_H_U"),
            f"outcome_diagnostics[{index}].analytic_terminal_truth_L_H_U",
        )
        roles = as_mapping(outcome.get("truth_roles"), f"outcome_diagnostics[{index}].truth_roles")
        rates = as_mapping(outcome.get("decision_rates"), f"outcome_diagnostics[{index}].decision_rates")
        row = {
            "label": text(outcome.get("label"), f"outcome_diagnostics[{index}].label"),
            "scenario": text(outcome.get("scenario"), f"outcome_diagnostics[{index}].scenario"),
            "dependence_profile": text(outcome.get("dependence_profile"), f"outcome_diagnostics[{index}].dependence_profile"),
            "failure_profile": text(outcome.get("failure_profile"), f"outcome_diagnostics[{index}].failure_profile"),
            "blocks_per_macro_cell": str(integer(outcome.get("blocks_per_macro_cell"), f"outcome_diagnostics[{index}].blocks_per_macro_cell")),
            "blocks_per_fine_stratum": str(integer(outcome.get("blocks_per_fine_stratum"), f"outcome_diagnostics[{index}].blocks_per_fine_stratum")),
            "outer_replicates": str(integer(outcome.get("outer_replicates"), f"outcome_diagnostics[{index}].outer_replicates")),
            "analytic_truth_L": source_scalar(finite_number(truth[0], f"outcome_diagnostics[{index}].truth[0]")),
            "analytic_truth_H": source_scalar(finite_number(truth[1], f"outcome_diagnostics[{index}].truth[1]")),
            "analytic_truth_U": source_scalar(finite_number(truth[2], f"outcome_diagnostics[{index}].truth[2]")),
            "positive_truth_role": text(roles.get("positive_all_cells"), f"outcome_diagnostics[{index}].positive role"),
            "reverse_truth_role": text(roles.get("reverse_all_cells"), f"outcome_diagnostics[{index}].reverse role"),
            "equivalence_truth_role": text(roles.get("equivalence_all_cells"), f"outcome_diagnostics[{index}].equivalence role"),
            "status": text(document.get("status"), "dependence status"),
            "gate_effect": text(document.get("gate_effect"), "dependence gate effect"),
            "source_json_path": f"outcome_diagnostics[{index}]",
        }
        for metric, prefix in metric_prefixes:
            rate = as_mapping(rates.get(metric), f"outcome_diagnostics[{index}].decision_rates.{metric}")
            row[f"{prefix}_successes"] = str(integer(rate.get("successes"), f"{metric}.successes"))
            row[f"{prefix}_estimate"] = source_scalar(finite_number(rate.get("estimate"), f"{metric}.estimate"))
            row[f"{prefix}_wilson_lower"] = source_scalar(finite_number(rate.get("interval_lower"), f"{metric}.lower"))
            row[f"{prefix}_wilson_upper"] = source_scalar(finite_number(rate.get("interval_upper"), f"{metric}.upper"))
        first_rate = as_mapping(rates.get("positive_all_cells"), f"outcome_diagnostics[{index}].positive rate")
        row["wilson_confidence_level"] = source_scalar(finite_number(first_rate.get("confidence_level"), "Wilson confidence"))
        row["wilson_interval_method"] = text(first_rate.get("interval_method"), "Wilson method")
        rows.append(row)
    return rows


def build_block_formation_rows(document: Mapping[str, Any]) -> list[dict[str, str]]:
    formations = as_sequence(document.get("formation_diagnostics"), "formation_diagnostics")
    rows: list[dict[str, str]] = []
    for index, raw in enumerate(formations):
        formation = as_mapping(raw, f"formation_diagnostics[{index}]")
        bounds = as_mapping(formation.get("probability_bounds"), f"formation_diagnostics[{index}].probability_bounds")
        validity_bounds = as_sequence(bounds.get("semantic_validity"), f"formation_diagnostics[{index}].semantic_validity bounds")
        high_bounds = as_sequence(bounds.get("high_given_valid"), f"formation_diagnostics[{index}].high bounds")
        support = as_mapping(formation.get("whole_panel_support_rate"), f"formation_diagnostics[{index}].support rate")
        row = {
            "profile": text(formation.get("profile"), f"formation_diagnostics[{index}].profile"),
            "high_probability_given_valid": source_scalar(finite_number(formation.get("high_probability_given_valid"), f"formation_diagnostics[{index}].high probability")),
            "semantic_validity_probability": source_scalar(finite_number(formation.get("semantic_validity_probability"), f"formation_diagnostics[{index}].validity probability")),
            "semantic_validity_bound_lower": source_scalar(finite_number(validity_bounds[0], f"formation_diagnostics[{index}].validity lower")),
            "semantic_validity_bound_upper": source_scalar(finite_number(validity_bounds[1], f"formation_diagnostics[{index}].validity upper")),
            "high_probability_bound_lower": source_scalar(finite_number(high_bounds[0], f"formation_diagnostics[{index}].high lower")),
            "high_probability_bound_upper": source_scalar(finite_number(high_bounds[1], f"formation_diagnostics[{index}].high upper")),
            "attempt_cap_per_fine_stratum": str(integer(formation.get("attempt_cap_per_fine_stratum"), f"formation_diagnostics[{index}].cap")),
            "attempt_batch_size": str(integer(formation.get("attempt_batch_size"), f"formation_diagnostics[{index}].batch")),
            "target_blocks_per_fine_stratum": str(integer(formation.get("target_blocks_per_fine_stratum"), f"formation_diagnostics[{index}].target")),
            "required_fine_strata": str(integer(formation.get("required_fine_strata"), f"formation_diagnostics[{index}].required strata")),
            "outer_replicates": str(integer(formation.get("outer_replicates"), f"formation_diagnostics[{index}].outer replicates")),
            "support_successes": str(integer(support.get("successes"), f"formation_diagnostics[{index}].support successes")),
            "support_estimate": source_scalar(finite_number(support.get("estimate"), f"formation_diagnostics[{index}].support estimate")),
            "support_wilson_lower": source_scalar(finite_number(support.get("interval_lower"), f"formation_diagnostics[{index}].support lower")),
            "support_wilson_upper": source_scalar(finite_number(support.get("interval_upper"), f"formation_diagnostics[{index}].support upper")),
            "wilson_confidence_level": source_scalar(finite_number(support.get("confidence_level"), f"formation_diagnostics[{index}].support confidence")),
            "wilson_interval_method": text(support.get("interval_method"), f"formation_diagnostics[{index}].support method"),
            "stopping_rule": text(formation.get("stopping_rule"), f"formation_diagnostics[{index}].stopping rule"),
            "status": text(document.get("status"), "dependence status"),
            "gate_effect": text(document.get("gate_effect"), "dependence gate effect"),
            "source_json_path": f"formation_diagnostics[{index}]",
        }
        for source_key, prefix in (
            ("supported_strata_quantiles", "supported_strata"),
            ("total_attempts_quantiles", "total_attempts"),
            ("semantic_invalid_quantiles", "semantic_invalid"),
            ("unmatched_valid_quantiles", "unmatched_valid"),
            ("retained_blocks_quantiles", "retained_blocks"),
        ):
            quantiles = as_mapping(formation.get(source_key), f"formation_diagnostics[{index}].{source_key}")
            for quantile in ("minimum", "p05", "p50", "p95", "maximum"):
                row[f"{prefix}_{quantile}"] = str(integer(quantiles.get(quantile), f"{source_key}.{quantile}"))
        rows.append(row)
    return rows


def parse_numeric_rows(rows: Sequence[Mapping[str, str]], fields: Sequence[str]) -> list[dict[str, Any]]:
    parsed: list[dict[str, Any]] = []
    for row in rows:
        converted: dict[str, Any] = dict(row)
        for field in fields:
            converted[field] = float(row[field])
        parsed.append(converted)
    return parsed


def heat_color(value: float) -> str:
    low = (239, 246, 255)
    high = (8, 81, 156)
    fraction = max(0.0, min(1.0, (value - 0.95) / 0.05))
    rgb = tuple(round(low[index] + fraction * (high[index] - low[index])) for index in range(3))
    return "#" + "".join(f"{component:02x}" for component in rgb)


def render_heatmap(rows: Sequence[Mapping[str, str]]) -> str:
    parsed = parse_numeric_rows(
        rows,
        ("followup_unavailability", "block_icc", "decision_rate", "wilson_lower", "wilson_upper"),
    )
    u_values = sorted({row["followup_unavailability"] for row in parsed})
    icc_values = sorted({row["block_icc"] for row in parsed})
    require(len(u_values) == 4 and len(icc_values) == 3, "heatmap requires a 4x3 grid")
    lookup = {(row["followup_unavailability"], row["block_icc"]): row for row in parsed}
    width, height = 1000, 690
    left, top, cell_width, cell_height = 245, 175, 215, 100
    parts = [
        svg_text(50, 48, "+15pp all-four-cell decision rate at B=384 per macro cell", size=24, weight=700),
        svg_text(50, 78, PLANNING_LABEL, size=13, weight=700, fill="#8f2d20"),
        svg_text(50, 104, "Cell labels: Monte Carlo rate and Wilson 95% interval (10,000 replicates/cell)", size=13, fill="#425466"),
        svg_text(120, 370, "Follow-up U", size=15, weight=700, anchor="middle"),
        svg_text(565, 145, "Block-arm ICC sensitivity", size=15, weight=700, anchor="middle"),
    ]
    for column, icc in enumerate(icc_values):
        parts.append(svg_text(left + column * cell_width + (cell_width - 10) / 2, 166, f"ICC={icc:.2f}", size=14, weight=700, anchor="middle"))
    for row_index, u_value in enumerate(u_values):
        y = top + row_index * cell_height
        parts.append(svg_text(left - 24, y + 47, f"U={100*u_value:.0f}%", size=14, weight=700, anchor="end"))
        for column, icc in enumerate(icc_values):
            x = left + column * cell_width
            cell = lookup[(u_value, icc)]
            fill = heat_color(cell["decision_rate"])
            label_fill = "#ffffff" if cell["decision_rate"] >= 0.98 else "#17212b"
            parts.append(
                f'<rect x="{x}" y="{y}" width="{cell_width - 10}" height="{cell_height - 10}" '
                f'rx="8" fill="{fill}" stroke="#385170" stroke-width="1"/>'
            )
            parts.append(svg_text(x + (cell_width - 10) / 2, y + 39, percent(cell["decision_rate"]), size=20, weight=700, anchor="middle", fill=label_fill))
            parts.append(svg_text(x + (cell_width - 10) / 2, y + 66, f"[{percent(cell['wilson_lower'])}, {percent(cell['wilson_upper'])}]", size=12, anchor="middle", fill=label_fill))
    legend_x, legend_y = 280, 605
    for index in range(11):
        value = 0.95 + 0.005 * index
        parts.append(f'<rect x="{legend_x + index*38}" y="{legend_y}" width="38" height="16" fill="{heat_color(value)}"/>')
    parts.extend(
        [
            svg_text(legend_x, legend_y + 38, "95%", size=11, anchor="middle"),
            svg_text(legend_x + 10 * 38, legend_y + 38, "100%", size=11, anchor="middle"),
            svg_text(50, 669, "Source: confirmatory_size_certification.cell_assessments, scenario=positive_15. Wilson intervals quantify Monte Carlo frequency only.", size=11, fill="#566573"),
        ]
    )
    return svg_document(
        width,
        height,
        "+15pp U by ICC planning heatmap",
        "Synthetic planning heatmap of all-four-cell positive decision rates over four follow-up unavailability levels and three block-arm ICC sensitivities.",
        "\n".join(parts),
    )


def render_frontier(rows: Sequence[Mapping[str, str]], power_threshold: float) -> str:
    parsed = parse_numeric_rows(rows, ("blocks_per_macro_cell", "decision_rate", "wilson_lower", "wilson_upper"))
    width, height = 1100, 720
    left, right, top, bottom = 100, 1040, 135, 550
    all_x = [row["blocks_per_macro_cell"] for row in parsed]
    log_min, log_max = math.log10(min(all_x)), math.log10(max(all_x))

    def x_position(value: float) -> float:
        return left + (math.log10(value) - log_min) / (log_max - log_min) * (right - left)

    def y_position(value: float) -> float:
        return bottom - value * (bottom - top)

    colors = {
        "positive_15": "#0072B2",
        "positive_1055": "#D55E00",
        "equivalence_null": "#009E73",
    }
    labels = {
        "positive_15": "+15pp paired H-up/L-down",
        "positive_1055": "+10.55pp paired H-up/L-down",
        "equivalence_null": "Observed-vector equivalence",
    }
    parts = [
        svg_text(50, 46, "Synthetic sample-size frontiers with Wilson intervals", size=24, weight=700),
        svg_text(50, 76, PLANNING_LABEL, size=13, weight=700, fill="#8f2d20"),
        svg_text(50, 102, "Rates are all-four-cell decisions in the stored frontier summaries; x-axis is logarithmic.", size=13, fill="#425466"),
    ]
    for tick in (0.0, 0.25, 0.50, 0.75, 1.0):
        y = y_position(tick)
        parts.append(f'<line x1="{left}" y1="{y:.2f}" x2="{right}" y2="{y:.2f}" stroke="#dfe6ec" stroke-width="1"/>')
        parts.append(svg_text(left - 14, y + 5, f"{100*tick:.0f}%", size=12, anchor="end"))
    threshold_y = y_position(power_threshold)
    parts.append(f'<line x1="{left}" y1="{threshold_y:.2f}" x2="{right}" y2="{threshold_y:.2f}" stroke="#6f42c1" stroke-width="2" stroke-dasharray="8 6"/>')
    parts.append(svg_text(right - 4, threshold_y - 8, f"Power criterion {percent(power_threshold, 0)}", size=11, anchor="end", fill="#6f42c1"))
    x_ticks = [value for value in (96, 192, 384, 768, 1536, 3072) if min(all_x) <= value <= max(all_x)]
    for tick in x_ticks:
        x = x_position(tick)
        parts.append(f'<line x1="{x:.2f}" y1="{top}" x2="{x:.2f}" y2="{bottom}" stroke="#eef2f5" stroke-width="1"/>')
        parts.append(svg_text(x, bottom + 25, f"{tick:,}", size=12, anchor="middle"))
    parts.append(svg_text((left + right) / 2, bottom + 60, "Active blocks per macro cell (log scale)", size=14, weight=700, anchor="middle"))
    y_axis_midpoint = (top + bottom) / 2
    parts.append(
        f'<text x="30" y="{y_axis_midpoint:.2f}" '
        f'transform="rotate(-90 30 {y_axis_midpoint:.2f})" text-anchor="middle" '
        f'font-family="{FONT_STACK}" font-size="14" font-weight="700" '
        'fill="#17212b">Decision rate</text>'
    )

    for series in ("positive_15", "positive_1055", "equivalence_null"):
        values = sorted((row for row in parsed if row["series"] == series), key=lambda row: row["blocks_per_macro_cell"])
        coordinates = [(x_position(row["blocks_per_macro_cell"]), y_position(row["decision_rate"])) for row in values]
        points = " ".join(f"{x:.2f},{y:.2f}" for x, y in coordinates)
        parts.append(f'<polyline points="{points}" fill="none" stroke="{colors[series]}" stroke-width="3" stroke-linejoin="round"/>')
        for row, (x, y) in zip(values, coordinates):
            lower_y = y_position(row["wilson_lower"])
            upper_y = y_position(row["wilson_upper"])
            parts.append(f'<line x1="{x:.2f}" y1="{upper_y:.2f}" x2="{x:.2f}" y2="{lower_y:.2f}" stroke="{colors[series]}" stroke-width="2"/>')
            parts.append(f'<line x1="{x-5:.2f}" y1="{upper_y:.2f}" x2="{x+5:.2f}" y2="{upper_y:.2f}" stroke="{colors[series]}" stroke-width="2"/>')
            parts.append(f'<line x1="{x-5:.2f}" y1="{lower_y:.2f}" x2="{x+5:.2f}" y2="{lower_y:.2f}" stroke="{colors[series]}" stroke-width="2"/>')
            parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4.5" fill="{colors[series]}" stroke="#ffffff" stroke-width="1.5"/>')
    legend_y = 650
    for index, series in enumerate(("positive_15", "positive_1055", "equivalence_null")):
        x = 115 + index * 300
        parts.append(f'<line x1="{x}" y1="{legend_y}" x2="{x+36}" y2="{legend_y}" stroke="{colors[series]}" stroke-width="4"/>')
        parts.append(svg_text(x + 46, legend_y + 5, labels[series], size=12))
    parts.append(svg_text(50, 705, "Source: sample_size_frontiers.{positive_15, positive_1055, equivalence_null}. Error bars are Wilson 95% intervals for Monte Carlo frequency only.", size=11, fill="#566573"))
    return svg_document(
        width,
        height,
        "Synthetic sample-size frontiers",
        "Planning-only sample-size frontier plot comparing positive fifteen-point, positive ten-point-five-five, and observed-vector equivalence decision rates with Wilson intervals.",
        "\n".join(parts),
    )


def render_latent_intervals(rows: Sequence[Mapping[str, str]], threshold: float) -> str:
    parsed = parse_numeric_rows(rows, ("observed_high_contrast", "latent_binary_lower", "latent_binary_upper"))
    width, height = 1050, 690
    left, right, top, bottom = 285, 990, 145, 580
    minimum = min(row["latent_binary_lower"] for row in parsed) - 0.05
    maximum = max(row["latent_binary_upper"] for row in parsed) + 0.05

    def x_position(value: float) -> float:
        return left + (value - minimum) / (maximum - minimum) * (right - left)

    display_labels = {
        "null": "Null",
        "availability_only": "Availability only",
        "fine_stratum_heterogeneity": "Fine-stratum boundary",
        "positive_1055": "+10.55pp observed",
        "positive_15": "+15pp observed",
        "negative_15": "−15pp observed",
    }
    parts = [
        svg_text(50, 46, "Latent-binary high-choice sensitivity at the stored worst cell", size=24, weight=700),
        svg_text(50, 76, PLANNING_LABEL, size=13, weight=700, fill="#8f2d20"),
        svg_text(50, 102, "Horizontal lines are assumption-free bounds; dots are observed H contrasts. Sensitivity is secondary and non-gating.", size=13, fill="#425466"),
    ]
    tick_start = math.floor(minimum / 0.1) * 0.1
    tick_end = math.ceil(maximum / 0.1) * 0.1
    tick = tick_start
    while tick <= tick_end + 1e-9:
        x = x_position(tick)
        parts.append(f'<line x1="{x:.2f}" y1="{top}" x2="{x:.2f}" y2="{bottom}" stroke="#e3e9ee" stroke-width="1"/>')
        parts.append(svg_text(x, bottom + 25, f"{tick:+.1f}", size=11, anchor="middle"))
        tick += 0.1
    for boundary, color, dash in ((0.0, "#17212b", ""), (-threshold, "#6f42c1", "6 5"), (threshold, "#6f42c1", "6 5")):
        x = x_position(boundary)
        dash_attribute = f' stroke-dasharray="{dash}"' if dash else ""
        parts.append(f'<line x1="{x:.2f}" y1="{top}" x2="{x:.2f}" y2="{bottom}" stroke="{color}" stroke-width="2"{dash_attribute}/>')
    for index, row in enumerate(parsed):
        y = top + 38 + index * 64
        lower_x = x_position(row["latent_binary_lower"])
        upper_x = x_position(row["latent_binary_upper"])
        observed_x = x_position(row["observed_high_contrast"])
        parts.append(svg_text(left - 18, y + 5, display_labels[row["scenario"]], size=13, weight=700, anchor="end"))
        parts.append(f'<line x1="{lower_x:.2f}" y1="{y}" x2="{upper_x:.2f}" y2="{y}" stroke="#0072B2" stroke-width="7" stroke-linecap="round"/>')
        parts.append(f'<circle cx="{observed_x:.2f}" cy="{y}" r="6" fill="#D55E00" stroke="#ffffff" stroke-width="2"/>')
        parts.append(svg_text(right, y - 10, f"[{display_delta(row['latent_binary_lower'])}, {display_delta(row['latent_binary_upper'])}]", size=11, anchor="end", fill="#425466"))
    parts.append(svg_text((left + right) / 2, bottom + 60, "Self-minus-yoke high-choice probability contrast", size=14, weight=700, anchor="middle"))
    parts.append(svg_text(50, 669, "Source: latent_binary_sensitivity.declared_worst_sensitivity_examples. Values within 1e−12 of zero are displayed as zero.", size=11, fill="#566573"))
    return svg_document(
        width,
        height,
        "Latent-binary sensitivity intervals",
        "Planning-only interval plot of observed high-disposition contrasts and assumption-free latent-binary high-choice bounds in six scenarios.",
        "\n".join(parts),
    )


def render_dependence_outcome_screen(rows: Sequence[Mapping[str, str]]) -> str:
    parsed = parse_numeric_rows(
        rows,
        (
            "positive_estimate",
            "positive_wilson_lower",
            "positive_wilson_upper",
            "coverage_12_estimate",
            "coverage_12_wilson_lower",
            "coverage_12_wilson_upper",
            "analytic_truth_L",
            "analytic_truth_H",
            "analytic_truth_U",
        ),
    )
    require(len(parsed) == 8, "dependence outcome chart requires eight profiles")
    width, height = 1500, 900
    left, right, top = 360, 1055, 230
    row_spacing = 64

    def x_position(value: float) -> float:
        return left + value * (right - left)

    labels = {
        "positive15_independent_none": "+15 independent / no failure",
        "positive15_donor_symmetric": "+15 donor / symmetric failure",
        "positive15_shared_symmetric": "+15 shared / symmetric failure",
        "positive15_joint_symmetric": "+15 joint / symmetric failure",
        "positive15_joint_differential": "+15 joint / differential failure",
        "null_joint_symmetric": "Null joint / symmetric failure",
        "null_joint_differential": "Null joint / differential failure",
        "boundary_joint_symmetric": "Boundary joint / symmetric failure",
    }
    parts = [
        svg_text(50, 46, "Outcome decision and coverage rates under declared dependence profiles", size=24, weight=700),
        svg_text(50, 78, DEPENDENCE_LABEL, size=13, weight=700, fill="#8f2d20"),
        svg_text(50, 106, "Eight declared profiles; 1,000 replicates/profile; horizontal bars are Wilson 95% Monte Carlo intervals.", size=13, fill="#425466"),
        svg_text(50, 130, "Truth vectors are exact terminal self-minus-yoke contrasts ordered [L, H, U].", size=13, fill="#425466"),
    ]
    for tick in (0.0, 0.25, 0.50, 0.75, 1.0):
        x = x_position(tick)
        parts.append(f'<line x1="{x:.2f}" y1="{top-22}" x2="{x:.2f}" y2="{top+row_spacing*7+32}" stroke="#e3e9ee" stroke-width="1"/>')
        parts.append(svg_text(x, top - 34, percent(tick, 0), size=11, anchor="middle"))
    parts.extend(
        [
            f'<line x1="{left}" y1="{top-22}" x2="{left}" y2="{top+row_spacing*7+32}" stroke="#566573" stroke-width="1.5"/>',
            svg_text(1078, top - 34, "Analytic truth [L, H, U]", size=11, weight=700),
            svg_text(1360, top - 34, "Positive / coverage", size=11, weight=700, anchor="middle"),
            f'<line x1="{left}" y1="166" x2="{left+28}" y2="166" stroke="#0072B2" stroke-width="3"/>',
            f'<circle cx="{left+14}" cy="166" r="5" fill="#0072B2" stroke="#ffffff" stroke-width="1.5"/>',
            svg_text(left + 38, 171, "All-cell positive decision", size=12),
            f'<line x1="{left+255}" y1="166" x2="{left+283}" y2="166" stroke="#D55E00" stroke-width="3" stroke-dasharray="7 4"/>',
            f'<polygon points="{left+269},159 {left+276},166 {left+269},173 {left+262},166" fill="#ffffff" stroke="#D55E00" stroke-width="2"/>',
            svg_text(left + 293, 171, "Simultaneous 12-component coverage", size=12),
        ]
    )
    for index, row in enumerate(parsed):
        y = top + index * row_spacing
        if index in (5, 7):
            parts.append(f'<line x1="50" y1="{y-31}" x2="1450" y2="{y-31}" stroke="#c9d2da" stroke-width="1.5"/>')
        parts.append(svg_text(left - 20, y + 5, labels[row["label"]], size=12, weight=700, anchor="end"))
        parts.append(f'<line x1="{left}" y1="{y+31}" x2="{right}" y2="{y+31}" stroke="#f0f3f5" stroke-width="1"/>')

        positive_y = y - 9
        positive_lower = x_position(row["positive_wilson_lower"])
        positive_upper = x_position(row["positive_wilson_upper"])
        positive_x = x_position(row["positive_estimate"])
        parts.append(f'<line x1="{positive_lower:.2f}" y1="{positive_y}" x2="{positive_upper:.2f}" y2="{positive_y}" stroke="#0072B2" stroke-width="3"/>')
        parts.append(f'<line x1="{positive_lower:.2f}" y1="{positive_y-5}" x2="{positive_lower:.2f}" y2="{positive_y+5}" stroke="#0072B2" stroke-width="2"/>')
        parts.append(f'<line x1="{positive_upper:.2f}" y1="{positive_y-5}" x2="{positive_upper:.2f}" y2="{positive_y+5}" stroke="#0072B2" stroke-width="2"/>')
        parts.append(f'<circle cx="{positive_x:.2f}" cy="{positive_y}" r="5" fill="#0072B2" stroke="#ffffff" stroke-width="1.5"/>')

        coverage_y = y + 10
        coverage_lower = x_position(row["coverage_12_wilson_lower"])
        coverage_upper = x_position(row["coverage_12_wilson_upper"])
        coverage_x = x_position(row["coverage_12_estimate"])
        parts.append(f'<line x1="{coverage_lower:.2f}" y1="{coverage_y}" x2="{coverage_upper:.2f}" y2="{coverage_y}" stroke="#D55E00" stroke-width="3" stroke-dasharray="7 4"/>')
        parts.append(f'<line x1="{coverage_lower:.2f}" y1="{coverage_y-5}" x2="{coverage_lower:.2f}" y2="{coverage_y+5}" stroke="#D55E00" stroke-width="2"/>')
        parts.append(f'<line x1="{coverage_upper:.2f}" y1="{coverage_y-5}" x2="{coverage_upper:.2f}" y2="{coverage_y+5}" stroke="#D55E00" stroke-width="2"/>')
        parts.append(f'<polygon points="{coverage_x:.2f},{coverage_y-6} {coverage_x+6:.2f},{coverage_y:.2f} {coverage_x:.2f},{coverage_y+6} {coverage_x-6:.2f},{coverage_y:.2f}" fill="#ffffff" stroke="#D55E00" stroke-width="2"/>')

        truth_label = "[" + ", ".join(display_delta(row[key]) for key in ("analytic_truth_L", "analytic_truth_H", "analytic_truth_U")) + "]"
        parts.append(svg_text(1078, y + 5, truth_label, size=11, fill="#425466"))
        parts.append(svg_text(1360, y + 5, f"{percent(row['positive_estimate'], 1)} / {percent(row['coverage_12_estimate'], 1)}", size=11, anchor="middle"))
    parts.extend(
        [
            svg_text((left + right) / 2, top + row_spacing * 7 + 70, "Monte Carlo decision or coverage rate", size=14, weight=700, anchor="middle"),
            svg_text(50, 846, "Source: amendment_v1/results/dependence_diagnostics.json, outcome_diagnostics[0:8]. Synthetic sensitivity only; no provider observations.", size=11, fill="#566573"),
            svg_text(50, 870, "This non-gating screen cannot estimate provider dependence, certify or rescue B=384, or authorize collection or spend.", size=11, weight=700, fill="#8f2d20"),
        ]
    )
    return svg_document(
        width,
        height,
        "Non-gating synthetic dependence outcome screen",
        "Eight-profile synthetic comparison of all-cell positive decision rates and simultaneous twelve-component coverage with Wilson intervals and analytic terminal truth vectors. No provider observations; cannot certify B=384.",
        "\n".join(parts),
    )


def render_block_formation_support(rows: Sequence[Mapping[str, str]]) -> str:
    parsed = parse_numeric_rows(
        rows,
        (
            "high_probability_given_valid",
            "support_estimate",
            "support_wilson_lower",
            "support_wilson_upper",
            "attempt_cap_per_fine_stratum",
        ),
    )
    require(len(parsed) == 6, "block-formation chart requires six cells")
    width, height = 1180, 740
    left, right, top, bottom = 110, 1080, 190, 575
    high_values = (0.1, 0.3, 0.5)

    def x_position(value: float) -> float:
        return left + (value - high_values[0]) / (high_values[-1] - high_values[0]) * (right - left)

    def y_position(value: float) -> float:
        return bottom - value * (bottom - top)

    styles = {
        "independent": ("#0072B2", "", "circle", "Independent attempts"),
        "provider_batch": ("#D55E00", "8 5", "diamond", "Shared provider/batch shocks"),
    }
    parts = [
        svg_text(50, 46, "Whole-panel block-formation support under two declared profiles", size=24, weight=700),
        svg_text(50, 78, DEPENDENCE_LABEL, size=13, weight=700, fill="#8f2d20"),
        svg_text(50, 106, "Six declared cells; 2,000 replicates/cell; vertical bars are Wilson 95% Monte Carlo intervals.", size=13, fill="#425466"),
        svg_text(50, 130, "Support requires all 96 fine strata to reach 16 complete blocks before the exact per-stratum cap.", size=13, fill="#425466"),
    ]
    for tick in (0.0, 0.25, 0.50, 0.75, 1.0):
        y = y_position(tick)
        parts.append(f'<line x1="{left}" y1="{y:.2f}" x2="{right}" y2="{y:.2f}" stroke="#e3e9ee" stroke-width="1"/>')
        parts.append(svg_text(left - 14, y + 5, percent(tick, 0), size=11, anchor="end"))
    for high_probability in high_values:
        x = x_position(high_probability)
        cap = next(int(row["attempt_cap_per_fine_stratum"]) for row in parsed if row["high_probability_given_valid"] == high_probability)
        parts.append(f'<line x1="{x:.2f}" y1="{top}" x2="{x:.2f}" y2="{bottom}" stroke="#f0f3f5" stroke-width="1"/>')
        parts.append(svg_text(x, bottom + 28, percent(high_probability, 0), size=12, weight=700, anchor="middle"))
        parts.append(svg_text(x, bottom + 49, f"cap {cap:,}/stratum", size=10, anchor="middle", fill="#566573"))
    parts.append(svg_text((left + right) / 2, bottom + 83, "Declared Pr(H | semantically valid)", size=14, weight=700, anchor="middle"))
    y_axis_midpoint = (top + bottom) / 2
    parts.append(
        f'<text x="30" y="{y_axis_midpoint:.2f}" transform="rotate(-90 30 {y_axis_midpoint:.2f})" '
        f'text-anchor="middle" font-family="{FONT_STACK}" font-size="14" font-weight="700" '
        'fill="#17212b">Whole-panel support rate</text>'
    )
    for profile in ("independent", "provider_batch"):
        color, dash, marker, label = styles[profile]
        values = sorted((row for row in parsed if row["profile"] == profile), key=lambda row: row["high_probability_given_valid"])
        coordinates = [(x_position(row["high_probability_given_valid"]), y_position(row["support_estimate"])) for row in values]
        points = " ".join(f"{x:.2f},{y:.2f}" for x, y in coordinates)
        dash_attribute = f' stroke-dasharray="{dash}"' if dash else ""
        parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="3"{dash_attribute}/>' )
        for row, (x, y) in zip(values, coordinates):
            upper_y = y_position(row["support_wilson_upper"])
            lower_y = y_position(row["support_wilson_lower"])
            parts.append(f'<line x1="{x:.2f}" y1="{upper_y:.2f}" x2="{x:.2f}" y2="{lower_y:.2f}" stroke="{color}" stroke-width="2"/>')
            parts.append(f'<line x1="{x-6:.2f}" y1="{upper_y:.2f}" x2="{x+6:.2f}" y2="{upper_y:.2f}" stroke="{color}" stroke-width="2"/>')
            parts.append(f'<line x1="{x-6:.2f}" y1="{lower_y:.2f}" x2="{x+6:.2f}" y2="{lower_y:.2f}" stroke="{color}" stroke-width="2"/>')
            if marker == "circle":
                parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="6" fill="{color}" stroke="#ffffff" stroke-width="1.5"/>')
            else:
                parts.append(f'<polygon points="{x:.2f},{y-7:.2f} {x+7:.2f},{y:.2f} {x:.2f},{y+7:.2f} {x-7:.2f},{y:.2f}" fill="#ffffff" stroke="{color}" stroke-width="2"/>')
            label_anchor = "end" if x >= right - 1 else "start"
            label_x = x - 10 if label_anchor == "end" else x + 10
            parts.append(svg_text(label_x, y - 10, percent(row["support_estimate"], 1), size=11, weight=700, anchor=label_anchor, fill=color))
        legend_x = 150 if profile == "independent" else 520
        parts.append(f'<line x1="{legend_x}" y1="665" x2="{legend_x+38}" y2="665" stroke="{color}" stroke-width="3"{dash_attribute}/>' )
        if marker == "circle":
            parts.append(f'<circle cx="{legend_x+19}" cy="665" r="5" fill="{color}" stroke="#ffffff" stroke-width="1.5"/>')
        else:
            parts.append(f'<polygon points="{legend_x+19},659 {legend_x+25},665 {legend_x+19},671 {legend_x+13},665" fill="#ffffff" stroke="{color}" stroke-width="2"/>')
        parts.append(svg_text(legend_x + 50, 670, label, size=12))
    parts.extend(
        [
            svg_text(50, 707, "Source: amendment_v1/results/dependence_diagnostics.json, formation_diagnostics[0:6]. Synthetic feasibility only; no provider observations.", size=11, fill="#566573"),
            svg_text(50, 730, "This non-gating screen cannot certify or rescue B=384 or authorize collection or spend.", size=11, weight=700, fill="#8f2d20"),
        ]
    )
    return svg_document(
        width,
        height,
        "Non-gating synthetic block-formation support screen",
        "Six-cell synthetic comparison of whole-panel block-formation support under independent and shared provider-batch shock profiles, with Wilson intervals. No provider observations; cannot certify B=384.",
        "\n".join(parts),
    )


def render_design_flow(document: Mapping[str, Any]) -> str:
    panel = as_mapping(document.get("reference_panel"), "reference_panel")
    certification = as_mapping(document.get("confirmatory_size_certification"), "confirmatory_size_certification")
    macro_cells = integer(panel["macro_cells"], "macro cells")
    fine_strata = integer(panel["fine_strata_per_macro_cell"], "fine strata")
    blocks = integer(certification["blocks_per_macro_cell"], "blocks/cell")
    width, height = 1250, 430
    boxes = (
        (45, "Prospective baseline", "request L or H"),
        (225, "Eligibility gate", "semantic L/H only"),
        (405, "Canonical support", "complete block"),
        (585, "Restricted assignment", "self or yoke"),
        (765, "Assigned execution", "role-neutral surface"),
        (945, "Held-out follow-up", "D ∈ {L,H,U}"),
    )
    parts = [
        svg_text(45, 48, "Binding Test stage-1 design flow", size=24, weight=700),
        svg_text(45, 78, PLANNING_LABEL, size=13, weight=700, fill="#8f2d20"),
    ]
    for index, (x, heading, subheading) in enumerate(boxes):
        parts.append(f'<rect x="{x}" y="145" width="150" height="105" rx="12" fill="#f4f7fa" stroke="#385170" stroke-width="2"/>')
        parts.append(svg_text(x + 75, 186, heading, size=13, weight=700, anchor="middle"))
        parts.append(svg_text(x + 75, 216, subheading, size=12, anchor="middle", fill="#425466"))
        if index < len(boxes) - 1:
            arrow_start = x + 150
            arrow_end = boxes[index + 1][0]
            parts.append(f'<line x1="{arrow_start+6}" y1="198" x2="{arrow_end-10}" y2="198" stroke="#0072B2" stroke-width="3"/>')
            parts.append(f'<polygon points="{arrow_end-10},192 {arrow_end},198 {arrow_end-10},204" fill="#0072B2"/>')
    parts.append(f'<rect x="315" y="305" width="620" height="65" rx="12" fill="#e8f4fa" stroke="#0072B2" stroke-width="2"/>')
    parts.append(svg_text(625, 334, f"Equal-weight fixed-stratum inference: {macro_cells} macro cells × {fine_strata} fine strata/cell", size=15, weight=700, anchor="middle"))
    parts.append(svg_text(625, 357, f"Selected synthetic design: B={blocks} active blocks per macro cell", size=13, anchor="middle", fill="#425466"))
    parts.append(svg_text(45, 411, "Sources: reference_panel.{macro_cells,fine_strata_per_macro_cell}; confirmatory_size_certification.blocks_per_macro_cell. Diagram is a design schematic, not observed participant flow.", size=11, fill="#566573"))
    return svg_document(
        width,
        height,
        "Binding Test stage-1 design flow",
        "Schematic from prospective baseline request through eligibility, canonical support, restricted assignment, execution, held-out follow-up, and fixed-stratum analysis.",
        "\n".join(parts),
    )


def render_markdown(
    document: Mapping[str, Any],
    source_sha256: str,
    dependence_document: Mapping[str, Any],
    dependence_sha256: str,
    heatmap_rows: Sequence[Mapping[str, str]],
    false_rows: Sequence[Mapping[str, str]],
    dependence_outcome_rows: Sequence[Mapping[str, str]],
    block_formation_rows: Sequence[Mapping[str, str]],
) -> str:
    certification = as_mapping(document["confirmatory_size_certification"], "certification")
    positive = parse_numeric_rows(heatmap_rows, ("decision_rate", "wilson_lower", "wilson_upper"))
    worst_positive = min(positive, key=lambda row: row["decision_rate"])
    worst_false_upper = max(float(row["maximum_wilson_upper"]) for row in false_rows)
    dependence_outcomes = parse_numeric_rows(
        dependence_outcome_rows,
        ("positive_estimate", "coverage_12_estimate"),
    )
    positive_dependence_rows = [
        row for row in dependence_outcomes if row["scenario"] == "positive_15"
    ]
    formation_rows = parse_numeric_rows(
        block_formation_rows,
        ("high_probability_given_valid", "support_estimate"),
    )
    selected_sizes = as_mapping(document["selected_sizes"], "selected sizes")
    source_relative = "../../zero_call/results/redesign_gate_results.json"
    dependence_relative = "amendment_v1/results/dependence_diagnostics.json"
    return f"""# Paper 8 stage-1 tables and figures

> **{PLANNING_LABEL}.** The zero-call source reports
> `provider_calls_made={document['provider_calls_made']}` and
> `external_spend={document['external_spend']}`. Both scientific-data sources
> describe local deterministic construction or seeded synthetic operating
> characteristics; they are not empirical model-behavior results and do not
> authorize collection.
>
> **{DEPENDENCE_LABEL}.** The amendment-v1 dependence artifact has
> `status={dependence_document['status']}`, `gate_effect={dependence_document['gate_effect']}`,
> and contains no provider observations. It cannot certify or rescue B=384.

## Provenance

- Zero-call source: [`{source_relative}`]({source_relative})
  - Schema: `{document['schema_version']}`
  - Generated date: `{document['generated_date']}`
  - SHA-256: `{source_sha256}`
- Non-gating dependence source: [`{dependence_relative}`]({dependence_relative})
  - Schema: `{dependence_document['schema_version']}`
  - Generated date: `{dependence_document['generated_date']}`
  - SHA-256: `{dependence_sha256}`
  - Evidence class: local seeded synthetic screen; no provider observations;
    cannot certify or rescue B=384.
- Generator: [`generate_tables_figures.py`](generate_tables_figures.py)
- Rebuild: `python3 outputs/paper8_stage1_release_v0/generate_tables_figures.py`
- All CSV rows include a `source_json_path`. Figure footers name the corresponding
  source objects. Values within `1e-12` of zero are normalized to zero only for
  display in the latent-bound artifact.

## Quantitative orientation

- The selected +15pp synthetic design uses
  `B={certification['blocks_per_macro_cell']}` active blocks per macro cell and
  `{certification['blocks_per_fine_stratum']}` blocks per fine stratum
  (`confirmatory_size_certification.*`).
- Its worst stored U×ICC decision rate is
  **{percent(worst_positive['decision_rate'])}** with Wilson 95% interval
  **[{percent(worst_positive['wilson_lower'])}, {percent(worst_positive['wilson_upper'])}]**
  (`confirmatory_size_certification.cell_assessments`, scenario `positive_15`).
- The largest false-control Wilson upper bound is
  **{percent(worst_false_upper, 3)}** across the stored required false-control
  cells (`confirmatory_size_certification.cell_assessments`).
- The +10.55pp supplemental size is
  `B={as_mapping(selected_sizes['positive_1055'], 'positive_1055')['blocks_per_macro_cell']}`;
  the broad equivalence headline is
  `{selected_sizes['broad_equivalence_headline']}`
  (`selected_sizes`).
- All sizes are conditional on the frozen complete-block planning process, which
  models self/yoke arm counts independently and omits terminal execution failure.
  They must be recertified after the required endpoint and dependence amendments.
- In the separate non-gating dependence screen, the lowest positive-all-cell rate
  among the five +15 profiles is
  **{percent(min(row['positive_estimate'] for row in positive_dependence_rows))}**;
  the lowest simultaneous 12-component coverage across all eight profiles is
  **{percent(min(row['coverage_12_estimate'] for row in dependence_outcomes))}**
  (`outcome_diagnostics`). These are synthetic Monte Carlo frequencies, not
  provider-behavior estimates.
- Whole-panel block-formation support spans
  **{percent(min(row['support_estimate'] for row in formation_rows))}** to
  **{percent(max(row['support_estimate'] for row in formation_rows))}** across the
  six declared synthetic formation cells (`formation_diagnostics`). This screen
  is diagnostic only and cannot certify B=384.

## Tables

1. [`tables/design_summary.csv`](tables/design_summary.csv) — frozen panel,
   outcome, margins, selected design, and evidence boundary.
2. [`tables/positive15_u_icc.csv`](tables/positive15_u_icc.csv) — full 4×3
   +15pp U×ICC power grid with Wilson intervals.
3. [`tables/sample_size_frontier.csv`](tables/sample_size_frontier.csv) — +15pp,
   +10.55pp, and observed-vector-equivalence frontiers.
4. [`tables/false_controls.csv`](tables/false_controls.csv) — scenario-wise
   maximum false-headline rate and Wilson upper bound.
5. [`tables/support_request_b384.csv`](tables/support_request_b384.csv) — B=384
   support-assured attempts and active-design request caps under stored planning
   assumptions. Dollar cost remains absent in the source.
6. [`tables/latent_binary_intervals.csv`](tables/latent_binary_intervals.csv) —
   secondary, non-gating assumption-free high-choice bounds.
7. [`tables/dependence_outcome_screen.csv`](tables/dependence_outcome_screen.csv) —
   all eight declared non-gating outcome profiles with analytic L/H/U truth,
   truth roles, decision counts, and Wilson intervals.
8. [`tables/block_formation_screen.csv`](tables/block_formation_screen.csv) — all
   six declared block-formation cells with probability bounds, exact caps,
   support counts and Wilson intervals, and stored support/attempt quantiles.

## Figures

### Figure 1. Prospective design flow

![Prospective design flow](figures/design_flow.svg)

Source keys: `reference_panel` and `confirmatory_size_certification`.
This is a protocol schematic, not an observed participant-flow diagram.

### Figure 2. Latent-binary sensitivity bounds

![Latent-binary sensitivity bounds](figures/latent_binary_intervals.svg)

Source key: `latent_binary_sensitivity.declared_worst_sensitivity_examples`.
These analytical intervals are secondary and cannot create, rescue, or veto the
identified L/H/U planning decision.

### Figure 3. +15pp U×ICC heatmap

![Synthetic U by ICC power heatmap](figures/positive15_u_icc_heatmap.svg)

Source key: `confirmatory_size_certification.cell_assessments`, filtered to
`scenario=positive_15`. Intervals quantify Monte Carlo frequency only.

### Figure 4. Sample-size frontiers

![Synthetic sample-size frontiers](figures/sample_size_frontiers.svg)

Source keys: `sample_size_frontiers.positive_15`,
`sample_size_frontiers.positive_1055`, and
`sample_size_frontiers.equivalence_null`. Vertical bars are Wilson 95%
intervals for Monte Carlo frequency.

### Figure 5. Non-gating dependence outcome screen

![Non-gating dependence outcome screen](figures/dependence_outcome_screen.svg)

Suggested manuscript numbering: Figure 5. Source key: `outcome_diagnostics` in
`amendment_v1/results/dependence_diagnostics.json`. The plot compares the
all-cell positive decision rate with simultaneous 12-component coverage and
prints analytic terminal truth vectors. It is a synthetic screen with no
provider observations and cannot certify or rescue B=384.

### Figure 6. Non-gating block-formation support screen

![Non-gating block-formation support screen](figures/block_formation_support.svg)

Suggested manuscript numbering: Figure 6. Source key: `formation_diagnostics`
in `amendment_v1/results/dependence_diagnostics.json`. Wilson intervals quantify
Monte Carlo frequency only. The synthetic feasibility comparison contains no
provider observations and cannot certify or rescue B=384.

## Interpretation boundary

The sealed v0 source records the historical claim ceiling
`{document['claim_ceiling']}`. For this amended release, that wording is narrowed
to: `paired H-increase/L-decrease in observed terminal dispositions, with U
reported separately, in the exact tested snapshot-by-target cells and
prospectively supported randomized population; no latent-choice or mechanism
identification`. Snapshot labels are placeholders, and provider snapshots,
empirical support, token/dollar envelopes, and external approval are not supplied
by this package. The endpoint, `.05` H/L decision boundary, `.05/.05/.02`
secondary margins, exclusion and separate reporting of U, and component-specific
`SE<=1e-12` precedence are statistically frozen only within the amendment
bundle. They are not production-integrated, dependence/resource recertified, or
collection-authorizing. The v0 execution-failure gap additionally blocks
provider collection; see `PROTOCOL_AMENDMENTS_REQUIRED.md`.

The dependence additions are separately bounded by:
`{dependence_document['claim_ceiling']}` They are a **NON-GATING SYNTHETIC
SCREEN**, have `gate_effect=none`, contain no provider observations, and cannot
certify B=384.
"""


def generate(output_root: Path = OUTPUT_ROOT) -> tuple[Path, ...]:
    output_root = output_root.resolve()
    table_root = output_root / "tables"
    figure_root = output_root / "figures"
    document, source_sha256 = load_source()
    dependence_document, dependence_sha256 = load_dependence_source()
    design_rows = build_design_summary(document)
    heatmap_rows = build_heatmap_rows(document)
    frontier_rows = build_frontier_rows(document)
    false_rows = build_false_control_rows(document)
    support_rows = build_support_rows(document)
    latent_rows = build_latent_rows(document)
    dependence_outcome_rows = build_dependence_outcome_rows(dependence_document)
    block_formation_rows = build_block_formation_rows(dependence_document)

    write_csv(
        table_root / "design_summary.csv",
        ("section", "field", "value", "unit", "source_json_path", "note"),
        design_rows,
        output_root=output_root,
    )
    write_csv(
        table_root / "positive15_u_icc.csv",
        (
            "followup_unavailability",
            "block_icc",
            "blocks_per_macro_cell",
            "outer_replicates",
            "successes",
            "decision_rate",
            "wilson_lower",
            "wilson_upper",
            "decision_rate_percent",
            "wilson_95_percent",
            "source_json_path",
        ),
        heatmap_rows,
        output_root=output_root,
    )
    write_csv(
        table_root / "sample_size_frontier.csv",
        (
            "series",
            "series_label",
            "blocks_per_macro_cell",
            "outer_replicates",
            "decision_rate",
            "wilson_lower",
            "wilson_upper",
            "decision_rate_percent",
            "wilson_95_percent",
            "source_json_path",
        ),
        frontier_rows,
        output_root=output_root,
    )
    write_csv(
        table_root / "false_controls.csv",
        (
            "scenario",
            "sensitivity_cells",
            "replicates_per_cell",
            "maximum_decision_rate",
            "maximum_decision_rate_percent",
            "maximum_wilson_upper",
            "maximum_wilson_upper_percent",
            "criterion_maximum_wilson_upper",
            "all_cells_passed",
            "source_json_path",
        ),
        false_rows,
        output_root=output_root,
    )
    write_csv(
        table_root / "support_request_b384.csv",
        (
            "p_high_given_valid",
            "semantic_validity_probability",
            "blocks_per_macro_cell",
            "blocks_per_fine_stratum",
            "attempted_sessions_per_fine_stratum",
            "attempted_sessions",
            "retained_blocks",
            "active_randomized_sessions",
            "active_design_generation_request_cap",
            "union_bound_global_support_lower_bound",
            "dollar_cost",
            "source_json_path",
        ),
        support_rows,
        output_root=output_root,
    )
    write_csv(
        table_root / "latent_binary_intervals.csv",
        (
            "scenario",
            "followup_unavailability",
            "block_icc",
            "observed_high_contrast",
            "latent_binary_lower",
            "latent_binary_upper",
            "macro_cells_with_same_record",
            "gating_role",
            "source_json_path",
        ),
        latent_rows,
        output_root=output_root,
    )
    write_csv(
        table_root / "dependence_outcome_screen.csv",
        (
            "label",
            "scenario",
            "dependence_profile",
            "failure_profile",
            "blocks_per_macro_cell",
            "blocks_per_fine_stratum",
            "outer_replicates",
            "analytic_truth_L",
            "analytic_truth_H",
            "analytic_truth_U",
            "positive_truth_role",
            "reverse_truth_role",
            "equivalence_truth_role",
            "positive_successes",
            "positive_estimate",
            "positive_wilson_lower",
            "positive_wilson_upper",
            "reverse_successes",
            "reverse_estimate",
            "reverse_wilson_lower",
            "reverse_wilson_upper",
            "equivalence_successes",
            "equivalence_estimate",
            "equivalence_wilson_lower",
            "equivalence_wilson_upper",
            "coverage_12_successes",
            "coverage_12_estimate",
            "coverage_12_wilson_lower",
            "coverage_12_wilson_upper",
            "wilson_confidence_level",
            "wilson_interval_method",
            "status",
            "gate_effect",
            "source_json_path",
        ),
        dependence_outcome_rows,
        output_root=output_root,
    )
    write_csv(
        table_root / "block_formation_screen.csv",
        (
            "profile",
            "high_probability_given_valid",
            "semantic_validity_probability",
            "semantic_validity_bound_lower",
            "semantic_validity_bound_upper",
            "high_probability_bound_lower",
            "high_probability_bound_upper",
            "attempt_cap_per_fine_stratum",
            "attempt_batch_size",
            "target_blocks_per_fine_stratum",
            "required_fine_strata",
            "outer_replicates",
            "support_successes",
            "support_estimate",
            "support_wilson_lower",
            "support_wilson_upper",
            "wilson_confidence_level",
            "wilson_interval_method",
            "supported_strata_minimum",
            "supported_strata_p05",
            "supported_strata_p50",
            "supported_strata_p95",
            "supported_strata_maximum",
            "total_attempts_minimum",
            "total_attempts_p05",
            "total_attempts_p50",
            "total_attempts_p95",
            "total_attempts_maximum",
            "semantic_invalid_minimum",
            "semantic_invalid_p05",
            "semantic_invalid_p50",
            "semantic_invalid_p95",
            "semantic_invalid_maximum",
            "unmatched_valid_minimum",
            "unmatched_valid_p05",
            "unmatched_valid_p50",
            "unmatched_valid_p95",
            "unmatched_valid_maximum",
            "retained_blocks_minimum",
            "retained_blocks_p05",
            "retained_blocks_p50",
            "retained_blocks_p95",
            "retained_blocks_maximum",
            "stopping_rule",
            "status",
            "gate_effect",
            "source_json_path",
        ),
        block_formation_rows,
        output_root=output_root,
    )

    power_threshold = min(
        finite_number(row["threshold"], "power threshold")
        for row in positive_cells(document)
    )
    first_config = as_mapping(positive_cells(document)[0]["config"], "positive config")
    positive_threshold = finite_number(first_config["positive_threshold"], "positive threshold")
    write_text(
        figure_root / "positive15_u_icc_heatmap.svg",
        render_heatmap(heatmap_rows),
        output_root=output_root,
    )
    write_text(
        figure_root / "sample_size_frontiers.svg",
        render_frontier(frontier_rows, power_threshold),
        output_root=output_root,
    )
    write_text(
        figure_root / "latent_binary_intervals.svg",
        render_latent_intervals(latent_rows, positive_threshold),
        output_root=output_root,
    )
    write_text(
        figure_root / "design_flow.svg",
        render_design_flow(document),
        output_root=output_root,
    )
    write_text(
        figure_root / "dependence_outcome_screen.svg",
        render_dependence_outcome_screen(dependence_outcome_rows),
        output_root=output_root,
    )
    write_text(
        figure_root / "block_formation_support.svg",
        render_block_formation_support(block_formation_rows),
        output_root=output_root,
    )
    write_text(
        output_root / "TABLES_AND_FIGURES.md",
        render_markdown(
            document,
            source_sha256,
            dependence_document,
            dependence_sha256,
            heatmap_rows,
            false_rows,
            dependence_outcome_rows,
            block_formation_rows,
        ),
        output_root=output_root,
    )
    return (
        OUTPUT_ROOT / "generate_tables_figures.py",
        output_root / "TABLES_AND_FIGURES.md",
        table_root / "design_summary.csv",
        table_root / "positive15_u_icc.csv",
        table_root / "sample_size_frontier.csv",
        table_root / "false_controls.csv",
        table_root / "support_request_b384.csv",
        table_root / "latent_binary_intervals.csv",
        table_root / "dependence_outcome_screen.csv",
        table_root / "block_formation_screen.csv",
        figure_root / "design_flow.svg",
        figure_root / "positive15_u_icc_heatmap.svg",
        figure_root / "sample_size_frontiers.svg",
        figure_root / "latent_binary_intervals.svg",
        figure_root / "dependence_outcome_screen.svg",
        figure_root / "block_formation_support.svg",
    )


def check_generated_artifacts() -> tuple[Path, ...]:
    """Regenerate in a temporary directory and byte-compare every output."""

    with tempfile.TemporaryDirectory(prefix="paper8-stage1-generator-check-") as temporary:
        temporary_root = Path(temporary).resolve()
        regenerated = generate(temporary_root)[1:]
        checked: list[Path] = []
        missing: list[str] = []
        unsafe: list[str] = []
        mismatched: list[str] = []
        for candidate in regenerated:
            relative = candidate.relative_to(temporary_root)
            current = OUTPUT_ROOT / relative
            display = relative.as_posix()
            if not current.exists():
                missing.append(display)
                continue
            if not current.is_file() or current.is_symlink():
                unsafe.append(display)
                continue
            if candidate.read_bytes() != current.read_bytes():
                mismatched.append(display)
                continue
            checked.append(current)
        require(not missing, f"generated artifacts missing: {missing}")
        require(not unsafe, f"generated artifact paths unsafe: {unsafe}")
        require(not mismatched, f"generated artifact byte mismatches: {mismatched}")
        require(len(checked) == 15, f"unexpected generated-artifact count: {len(checked)}")
        return tuple(checked)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="regenerate in a temporary directory and byte-compare current artifacts",
    )
    arguments = parser.parse_args(argv)
    if arguments.check:
        try:
            checked = check_generated_artifacts()
        except (
            ArtifactError,
            KeyError,
            OSError,
            OverflowError,
            TypeError,
            UnicodeError,
            ValueError,
        ) as error:
            print(f"FAIL generated artifacts: {error}", file=sys.stderr)
            return 1
        print(f"PASS generated artifacts: {len(checked)} files match byte-for-byte")
        return 0

    generated = generate()
    for path in generated[1:]:
        print(path.relative_to(WORKSPACE_ROOT).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
