#!/usr/bin/env python3
"""Verify the Paper 8 stage-1 zero-call release without provider artifacts.

This verifier intentionally reads only the local stage-1 release directory and
the sealed ``zero_call`` package.  It never reads external-lane responses,
subscription-calibration artifacts, provider records, or transcripts.
"""

from __future__ import annotations

import hashlib
from importlib import metadata
import json
import math
import os
from pathlib import Path, PurePosixPath
import platform
import re
import subprocess
import sys
from typing import Any, Mapping


RELEASE_ROOT = Path(__file__).resolve().parent
REPOSITORY_ROOT = RELEASE_ROOT.parents[1]
ZERO_CALL_ROOT = REPOSITORY_ROOT / "zero_call"
ZERO_CALL_MANIFEST = ZERO_CALL_ROOT / "zero_call_manifest.sha256"
REDESIGN_RESULT = ZERO_CALL_ROOT / "results" / "redesign_gate_results.json"
AMENDMENT_ROOT = RELEASE_ROOT / "amendment_v1"
AMENDMENT_TEST_ROOT = AMENDMENT_ROOT / "tests"
DEPENDENCE_RESULT = AMENDMENT_ROOT / "results" / "dependence_diagnostics.json"
DEPENDENCE_RUNNER = AMENDMENT_ROOT / "run_dependence_diagnostics.py"
STATISTICAL_DECISION_AUTHORITY = (
    AMENDMENT_ROOT / "statistical_decision_authority.py"
)

EXPECTED_SOURCE_AGGREGATE = (
    "e0459b557e7e2c8b02d4565c554b9c09e82568c6271fcff15fe6e6096f3108d4"
)
EXPECTED_SOURCE_FILE_COUNT = 29
EXPECTED_SCHEMA_VERSION = "binding-test-redesigned-zero-call-gate-v1"
EXPECTED_MASTER_SEED = 20260805
EXPECTED_MODEL_SNAPSHOTS = ["reference_snapshot_a", "reference_snapshot_b"]
EXPECTED_TARGET_FAMILIES = [
    "work_score_allocation",
    "tool_budget_allocation",
]
EXPECTED_UNAVAILABILITY = [0.0, 0.05, 0.1, 0.15]
EXPECTED_BLOCK_ICC = [0.0, 0.1, 0.25]
EXPECTED_FALSE_SCENARIOS = [
    "null",
    "positive_boundary",
    "availability_only",
    "one_cell_only",
    "one_model_only",
    "fine_stratum_heterogeneity",
]
EXPECTED_ZERO_CALL_CLAIM_CEILING = (
    "observed L/H/U disposition reallocation in the exact tested "
    "snapshot-by-target cells and prospectively supported randomized "
    "population; no latent-choice or mechanism identification"
)
REFERENCE_PYTHON = "3.14.3"
REFERENCE_NUMPY = "2.4.2"
EXPECTED_AMENDMENT_TEST_COUNT = 63
EXPECTED_STATISTICAL_PANEL_INPUT_SCHEMA = "binding-statistical-panel-input-v1"
EXPECTED_STATISTICAL_PANEL_RESULT_SCHEMA = "binding-statistical-panel-result-v1"
EXPECTED_STATISTICAL_POLICY_SCHEMA = "binding-statistical-decision-policy-v1"
EXPECTED_STATISTICAL_DECISION_POLICY = {
    "schema_version": EXPECTED_STATISTICAL_POLICY_SCHEMA,
    "required_macro_cell_count": 4,
    "categories": ["L", "H", "U"],
    "primary_direction": "paired_H_up_L_down",
    "primary_threshold": "0.05",
    "primary_has_u_guard": False,
    "primary_requires_separate_u_reporting": True,
    "equivalence_margins": {"L": "0.05", "H": "0.05", "U": "0.02"},
    "vector_equivalence_role": "secondary_non_authorizing",
    "vector_equivalence_can_create_rescue_or_veto_primary": False,
    "standard_error_rule": (
        "finite_standard_error_at_or_below_epsilon_is_inference_invalid"
    ),
    "positive_standard_error_rule": (
        "every_finite_standard_error_strictly_above_epsilon_is_eligible"
    ),
    "positive_standard_error_requires_strict_estimate_within_bounds": True,
    "component_bounds_recomputed_by_this_authority": False,
    "degrees_of_freedom_recomputed_by_this_authority": False,
    "upstream_frozen_analyzer_provenance_required": True,
    "numerical_integrity_epsilon": "0.000000000001",
    "effect_and_margin_boundaries_use_epsilon_guard_bands": True,
    "epsilon_is_substantive_effect_increment": False,
    "grid_or_sample_change_requires_epsilon_reproof": True,
    "complete_component_estimates_must_sum_to_zero_within_epsilon": True,
    "numerical_integrity_rationale": (
        "The frozen grid uses quarter-point block contrasts and at most 128 "
        "blocks per fine stratum at B=3072; its smallest one-stratum nonzero "
        "macro-cell standard error is approximately 8.14e-5, so 1e-12 is "
        "below attainable genuine nonzero resolution. Any grid or "
        "sample-structure change requires a new proof and recertification."
    ),
    "ordinary_failure_disposition": "U",
    "local_abort_retains_u_row": True,
    "local_abort_invalidates_affected_and_panel_headlines": True,
    "mandatory_reporting_fields": [
        "U_simultaneous_interval_by_macro_cell",
        "terminal_source_subtype_counts_by_arm_assigned_schedule_macro_cell",
    ],
}
EXPECTED_TERMINAL_FLOW_POLICY_SCHEMA = "binding-terminal-flow-policy-v1"
EXPECTED_TERMINAL_FLOW_POLICY = {
    "schema_version": EXPECTED_TERMINAL_FLOW_POLICY_SCHEMA,
    "source_rules": [
        {
            "source": "followup_choice",
            "allowed_subtypes": ["none"],
            "allowed_dispositions": ["L", "H"],
        },
        {
            "source": "followup_unavailable",
            "allowed_subtypes": [
                "missing_response",
                "empty_response",
                "explicit_refusal",
                "invalid_response",
            ],
            "allowed_dispositions": ["U"],
        },
        {
            "source": "execution_failure",
            "allowed_subtypes": [
                "invalid_response",
                "transport_error",
                "timeout",
                "provider_error",
                "quota_exhausted",
                "tool_error",
                "tool_limit_exceeded",
            ],
            "allowed_dispositions": ["U"],
        },
        {
            "source": "followup_failure",
            "allowed_subtypes": [
                "transport_error",
                "timeout",
                "provider_error",
                "quota_exhausted",
            ],
            "allowed_dispositions": ["U"],
        },
        {
            "source": "local_protocol_abort",
            "allowed_subtypes": [
                "assignment_binding_mismatch",
                "schedule_integrity_mismatch",
                "role_leak_detected",
                "runtime_contract_violation",
                "controller_abort",
                "unknown",
            ],
            "allowed_dispositions": ["U"],
        },
    ],
    "local_protocol_abort_integrity": {
        "retains_composite_u_ledger_row": True,
        "marks_integrity_failure": True,
        "invalidates_affected_macro_cell_headline": True,
        "invalidates_all_cell_headline": True,
    },
    "valid_cell_decomposition": {
        "requires_valid_ledger_assignment_and_support": True,
        "terminal_rows_per_complete_block": 8,
        "arm_order": ["self", "yoke"],
        "assigned_schedule_order": ["L", "H"],
        "rows_per_arm_assigned_schedule_per_complete_block": 2,
    },
}
EXPECTED_DEPENDENCE_RESULT_SHA256 = (
    "f1cfcece6e7df658109ee58812fe2883b5964d8c7b73be6d6811a7e1f3e190ef"
)
EXPECTED_DEPENDENCE_SCHEMA = "binding-test-dependence-diagnostic-v1"
EXPECTED_DEPENDENCE_STATUS = "NON_GATING_SYNTHETIC_SCREEN"
EXPECTED_ASSIGNMENT_TABLE_SHA256 = (
    "ead4c7c1b7ddd8e0ce2f81b3e6e99bcb08273fb0140742590efa22fed13ab0d3"
)
EXPECTED_FORMATION_PROFILES = ["independent", "provider_batch"]
EXPECTED_DEPENDENCE_PROFILES = {
    "independent": [],
    "donor_only": ["donor_pair"],
    "shared_shocks": ["provider", "batch", "block"],
    "joint": ["provider", "batch", "block", "donor_pair"],
}
EXPECTED_OUTCOME_PROFILES = [
    {
        "label": "positive15_independent_none",
        "scenario": "positive_15",
        "dependence_profile": "independent",
        "failure_profile": "none",
    },
    {
        "label": "positive15_donor_symmetric",
        "scenario": "positive_15",
        "dependence_profile": "donor_only",
        "failure_profile": "symmetric",
    },
    {
        "label": "positive15_shared_symmetric",
        "scenario": "positive_15",
        "dependence_profile": "shared_shocks",
        "failure_profile": "symmetric",
    },
    {
        "label": "positive15_joint_symmetric",
        "scenario": "positive_15",
        "dependence_profile": "joint",
        "failure_profile": "symmetric",
    },
    {
        "label": "positive15_joint_differential",
        "scenario": "positive_15",
        "dependence_profile": "joint",
        "failure_profile": "differential",
    },
    {
        "label": "null_joint_symmetric",
        "scenario": "null",
        "dependence_profile": "joint",
        "failure_profile": "symmetric",
    },
    {
        "label": "null_joint_differential",
        "scenario": "null",
        "dependence_profile": "joint",
        "failure_profile": "differential",
    },
    {
        "label": "boundary_joint_symmetric",
        "scenario": "positive_boundary",
        "dependence_profile": "joint",
        "failure_profile": "symmetric",
    },
]
EXPECTED_GENERATED_ARTIFACT_COUNT = 15
EXPECTED_EMBEDDED_SVG_COUNT = 6
SHA256_LINE = re.compile(r"^([0-9a-f]{64})  (.+)$")


class VerificationError(RuntimeError):
    """A release invariant failed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_relative_path(raw: str, *, manifest: Path) -> PurePosixPath:
    require("\\" not in raw, f"backslash path in {manifest}: {raw!r}")
    relative = PurePosixPath(raw)
    require(not relative.is_absolute(), f"absolute path in {manifest}: {raw!r}")
    require(
        raw == relative.as_posix() and all(part not in {"", ".", ".."} for part in relative.parts),
        f"non-canonical path in {manifest}: {raw!r}",
    )
    return relative


def read_manifest(path: Path) -> dict[str, str]:
    require(path.is_file() and not path.is_symlink(), f"manifest missing or unsafe: {path}")
    entries: dict[str, str] = {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        match = SHA256_LINE.fullmatch(line)
        require(match is not None, f"malformed {path}:{line_number}")
        checksum, raw = match.groups()
        relative = safe_relative_path(raw, manifest=path).as_posix()
        require(relative not in entries, f"duplicate manifest path: {relative}")
        entries[relative] = checksum
    require(bool(entries), f"empty manifest: {path}")
    return entries


def package_files(root: Path, manifest: Path) -> dict[str, Path]:
    files: dict[str, Path] = {}
    for path in root.rglob("*"):
        if path.is_symlink():
            raise VerificationError(f"symlink forbidden in sealed package: {path}")
        if not path.is_file() or path == manifest:
            continue
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        relative = path.relative_to(root).as_posix()
        files[relative] = path
    return files


def verify_manifest_tree(root: Path, manifest: Path) -> int:
    expected = read_manifest(manifest)
    actual = package_files(root, manifest)
    missing = sorted(set(expected) - set(actual))
    extra = sorted(set(actual) - set(expected))
    mismatched = sorted(
        relative
        for relative in set(expected) & set(actual)
        if sha256_file(actual[relative]) != expected[relative]
    )
    require(not missing, f"manifest paths missing: {missing}")
    require(not extra, f"unmanifested package paths: {extra}")
    require(not mismatched, f"manifest digest mismatches: {mismatched}")
    return len(expected)


def load_json(path: Path) -> dict[str, Any]:
    require(path.is_file() and not path.is_symlink(), f"JSON artifact missing or unsafe: {path}")

    def reject_nonfinite(value: str) -> Any:
        raise VerificationError(f"non-finite JSON number in {path}: {value}")

    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle, parse_constant=reject_nonfinite)
    require(isinstance(value, dict), f"expected JSON object: {path}")
    return value


def expect_equal(label: str, actual: Any, expected: Any) -> None:
    require(actual == expected, f"{label}: expected {expected!r}, found {actual!r}")


def expect_true(label: str, actual: Any) -> None:
    require(actual is True, f"{label}: expected true, found {actual!r}")


def mapping(value: Any, label: str) -> Mapping[str, Any]:
    require(isinstance(value, dict), f"{label}: expected object")
    return value


def list_value(value: Any, label: str) -> list[Any]:
    require(isinstance(value, list), f"{label}: expected array")
    return value


def scientific_source_snapshot() -> tuple[dict[str, str], str]:
    fixed = (
        ZERO_CALL_ROOT / "REDESIGN_GATE_SPEC.md",
        ZERO_CALL_ROOT / "item_bank_v0.json",
        ZERO_CALL_ROOT / "run_redesign_gate.py",
    )
    discovered = tuple(sorted((ZERO_CALL_ROOT / "binding_test").glob("*.py"))) + tuple(
        sorted((ZERO_CALL_ROOT / "tests").glob("*.py"))
    )
    paths = fixed + discovered
    expect_equal("scientific source file count", len(paths), EXPECTED_SOURCE_FILE_COUNT)
    files: dict[str, str] = {}
    for path in paths:
        require(path.is_file() and not path.is_symlink(), f"scientific source missing or unsafe: {path}")
        files[path.relative_to(ZERO_CALL_ROOT).as_posix()] = sha256_file(path)
    canonical = json.dumps(
        files,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return files, hashlib.sha256(canonical).hexdigest()


def verify_scientific_source_integrity(result: Mapping[str, Any]) -> None:
    integrity = mapping(result.get("scientific_source_integrity"), "scientific_source_integrity")
    startup = mapping(
        integrity.get("startup_snapshot_before_scientific_imports"),
        "scientific_source_integrity.startup_snapshot_before_scientific_imports",
    )
    current_files, current_aggregate = scientific_source_snapshot()
    expect_equal("scientific source algorithm", startup.get("algorithm"), "SHA-256")
    expect_equal("current scientific source aggregate", current_aggregate, EXPECTED_SOURCE_AGGREGATE)
    expect_equal("stored scientific source aggregate", startup.get("aggregate_digest"), current_aggregate)
    expect_equal("stored scientific source file map", startup.get("files"), current_files)
    expect_true(
        "scientific source unchanged-through-prepublication flag",
        integrity.get("unchanged_through_prepublication_check"),
    )


def expected_sensitivity_grid() -> list[list[float]]:
    return [[u_value, icc] for u_value in EXPECTED_UNAVAILABILITY for icc in EXPECTED_BLOCK_ICC]


def verify_cell_assessments(certification: Mapping[str, Any]) -> None:
    assessments = list_value(certification.get("cell_assessments"), "cell_assessments")
    expect_equal("cell assessment count", len(assessments), 84)

    expected_roles = {"positive_15": "power"}
    expected_roles.update({scenario: "false_control" for scenario in EXPECTED_FALSE_SCENARIOS})
    observed: set[tuple[str, float, float]] = set()
    power_rows: list[Mapping[str, Any]] = []
    false_rows: list[Mapping[str, Any]] = []

    for index, raw_assessment in enumerate(assessments):
        assessment = mapping(raw_assessment, f"cell_assessments[{index}]")
        config = mapping(assessment.get("config"), f"cell_assessments[{index}].config")
        rate = mapping(assessment.get("rate"), f"cell_assessments[{index}].rate")
        scenario = config.get("scenario")
        require(scenario in expected_roles, f"unexpected trust-root scenario: {scenario!r}")
        role = expected_roles[str(scenario)]
        expect_equal(f"{scenario} role", assessment.get("role"), role)
        expect_equal(f"{scenario} metric", assessment.get("metric"), "positive_all_cells")
        expect_true(f"{scenario} cell passed", assessment.get("passed"))
        expect_true(f"{scenario} replicate eligibility", assessment.get("replicate_eligible"))
        expect_equal(f"{scenario} blocks per macro cell", config.get("blocks_per_macro_cell"), 384)
        expect_equal(f"{scenario} model snapshots", config.get("model_snapshots"), EXPECTED_MODEL_SNAPSHOTS)
        expect_equal(f"{scenario} target families", config.get("target_families"), EXPECTED_TARGET_FAMILIES)
        u_value = config.get("followup_unavailability")
        icc = config.get("block_icc")
        require(u_value in EXPECTED_UNAVAILABILITY, f"unexpected U value: {u_value!r}")
        require(icc in EXPECTED_BLOCK_ICC, f"unexpected ICC value: {icc!r}")
        key = (str(scenario), float(u_value), float(icc))
        require(key not in observed, f"duplicate trust-root cell: {key}")
        observed.add(key)
        expect_equal(f"{scenario} replicate accounting", rate.get("replicates"), config.get("outer_replicates"))
        if role == "power":
            require(rate.get("replicates", 0) >= 10_000, f"power replicate floor failed: {key}")
            require(rate.get("interval_lower", -math.inf) >= 0.90, f"power criterion failed: {key}")
            power_rows.append(assessment)
        else:
            require(rate.get("replicates", 0) >= 20_000, f"false-control replicate floor failed: {key}")
            require(rate.get("interval_upper", math.inf) <= 0.055, f"false-control criterion failed: {key}")
            false_rows.append(assessment)

    expected = {
        (scenario, u_value, icc)
        for scenario in ["positive_15", *EXPECTED_FALSE_SCENARIOS]
        for u_value in EXPECTED_UNAVAILABILITY
        for icc in EXPECTED_BLOCK_ICC
    }
    expect_equal("exact trust-root cell coordinates", observed, expected)
    expect_equal("power cell count", len(power_rows), 12)
    expect_equal("false-control cell count", len(false_rows), 72)

    worst_power = min(
        power_rows,
        key=lambda row: mapping(row["rate"], "power rate")["estimate"],
    )
    worst_power_rate = mapping(worst_power["rate"], "worst power rate")
    expect_equal("worst power estimate", worst_power_rate.get("estimate"), 0.9625)
    expect_equal(
        "worst power Wilson lower",
        worst_power_rate.get("interval_lower"),
        0.9585952728131844,
    )
    expect_equal(
        "worst power Wilson upper",
        worst_power_rate.get("interval_upper"),
        0.9660495286939397,
    )
    maximum_false_upper = max(
        mapping(row["rate"], "false-control rate")["interval_upper"]
        for row in false_rows
    )
    expect_equal(
        "maximum false-control Wilson upper",
        maximum_false_upper,
        0.0001920360561046254,
    )


def verify_resource_plan(result: Mapping[str, Any]) -> None:
    plans = mapping(result.get("resource_plans"), "resource_plans")
    plan_384 = mapping(plans.get("384"), "resource_plans.384")
    expected = {
        "0.10": (98_304, 147_456),
        "0.30": (31_776, 80_928),
        "0.50": (18_624, 67_776),
    }
    for support, (attempts, requests) in expected.items():
        plan = mapping(plan_384.get(support), f"resource_plans.384.{support}")
        expect_equal(f"{support} retained blocks", plan.get("retained_blocks"), 1_536)
        expect_equal(f"{support} retained sessions", plan.get("retained_sessions"), 12_288)
        expect_equal(f"{support} attempted sessions", plan.get("attempted_sessions"), attempts)
        expect_equal(f"{support} generation cap", plan.get("known_generation_requests_range"), [requests, requests])
        expect_true(f"{support} complete request cap", plan.get("complete_generation_request_cap"))
        expect_equal(f"{support} provider-cost envelope", plan.get("complete_provider_cost_envelope"), False)
        expect_equal(f"{support} dollar cost", plan.get("dollar_cost"), None)


def verify_trust_root(result: Mapping[str, Any]) -> None:
    expect_equal("schema version", result.get("schema_version"), EXPECTED_SCHEMA_VERSION)
    expect_equal("master seed", result.get("master_seed"), EXPECTED_MASTER_SEED)
    expect_equal("overall verdict", result.get("overall_verdict"), "CONFIRMATORY_SIZE_IDENTIFIED")
    expect_equal("provider calls", result.get("provider_calls_made"), 0)
    expect_equal("external spend", result.get("external_spend"), 0)
    expect_equal("external action status", result.get("external_action_status"), "NO_PROVIDER_CALL_AUTHORIZED")
    expect_equal(
        "historical zero-call claim ceiling",
        result.get("claim_ceiling"),
        EXPECTED_ZERO_CALL_CLAIM_CEILING,
    )

    tests = mapping(result.get("test_suite"), "test_suite")
    expect_true("stored test pass", tests.get("passed"))
    expect_equal("stored test return code", tests.get("return_code"), 0)
    expect_equal("stored test count", tests.get("tests_run"), 120)

    certification = mapping(result.get("confirmatory_size_certification"), "confirmatory_size_certification")
    expect_equal("size status", certification.get("size_status"), "CONFIRMATORY_SIZE_IDENTIFIED")
    expect_true("confirmatory size identified", certification.get("confirmatory_size_identified"))
    expect_true("numerical gate eligible", certification.get("numerical_gate_eligible"))
    expect_true("numerical gate passed", certification.get("numerical_gate_passed"))
    expect_equal("blocks per macro cell", certification.get("blocks_per_macro_cell"), 384)
    expect_equal("blocks per fine stratum", certification.get("blocks_per_fine_stratum"), 16)
    expect_equal("expected trust-root cells", certification.get("expected_grid_cells"), 84)
    expect_equal("observed trust-root cells", certification.get("observed_grid_cells"), 84)
    expect_equal("certified model snapshots", certification.get("model_snapshots"), EXPECTED_MODEL_SNAPSHOTS)
    expect_equal("certified target families", certification.get("target_families"), EXPECTED_TARGET_FAMILIES)
    expect_equal(
        "required sensitivity grid",
        certification.get("required_sensitivity_grid"),
        expected_sensitivity_grid(),
    )
    verify_cell_assessments(certification)

    selected = mapping(result.get("selected_sizes"), "selected_sizes")
    positive = mapping(selected.get("positive_15"), "selected_sizes.positive_15")
    expect_equal("selected positive size", positive.get("blocks_per_macro_cell"), 384)
    expect_true("selected positive certification", positive.get("whole_design_certified"))
    expect_equal("broad equivalence status", selected.get("broad_equivalence_headline"), "ABANDONED")
    expect_equal("maximum tested equivalence size", selected.get("maximum_tested_equivalence_blocks_per_macro_cell"), 3_072)

    frontiers = mapping(result.get("sample_size_frontiers"), "sample_size_frontiers")
    equivalence = list_value(frontiers.get("equivalence_null"), "sample_size_frontiers.equivalence_null")
    maximum_equivalence = next(
        (mapping(row, "equivalence row") for row in equivalence if mapping(row, "equivalence row").get("blocks_per_macro_cell") == 3_072),
        None,
    )
    require(maximum_equivalence is not None, "missing B=3072 equivalence frontier row")
    expect_equal("maximum-size equivalence rate", maximum_equivalence.get("estimate"), 0.6684)
    verify_resource_plan(result)
    verify_scientific_source_integrity(result)


def amendment_environment() -> dict[str, str]:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return environment


def verify_amendment_tests() -> str:
    require(
        AMENDMENT_TEST_ROOT.is_dir() and not AMENDMENT_TEST_ROOT.is_symlink(),
        f"amendment test directory missing or unsafe: {AMENDMENT_TEST_ROOT}",
    )
    try:
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                "-m",
                "unittest",
                "discover",
                "-s",
                str(AMENDMENT_TEST_ROOT),
                "-p",
                "test_*.py",
            ],
            cwd=REPOSITORY_ROOT,
            env=amendment_environment(),
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=60,
        )
    except subprocess.TimeoutExpired as error:
        raise VerificationError("amendment_v1 unit tests timed out") from error
    transcript = "\n".join((completed.stdout, completed.stderr))
    require(
        completed.returncode == 0,
        f"amendment_v1 unit tests failed (exit {completed.returncode}): {transcript.strip()}",
    )
    counts = re.findall(r"^Ran ([0-9]+) tests in [0-9.]+s$", transcript, re.MULTILINE)
    require(
        counts == [str(EXPECTED_AMENDMENT_TEST_COUNT)],
        f"expected exactly {EXPECTED_AMENDMENT_TEST_COUNT} amendment tests; transcript={transcript.strip()!r}",
    )
    status_lines = [line.strip() for line in transcript.splitlines() if line.strip() == "OK"]
    require(
        status_lines == ["OK"],
        f"amendment test completion status was not exactly OK: {transcript.strip()!r}",
    )
    return f"PASS amendment_v1 tests: {EXPECTED_AMENDMENT_TEST_COUNT}"


def verify_statistical_decision_policy() -> str:
    require(
        STATISTICAL_DECISION_AUTHORITY.is_file()
        and not STATISTICAL_DECISION_AUTHORITY.is_symlink(),
        "statistical decision authority missing or unsafe: "
        f"{STATISTICAL_DECISION_AUTHORITY}",
    )
    probe = r'''
import importlib.util
import json
from pathlib import Path
import sys

path = Path(sys.argv[1]).resolve()
name = "_paper8_sealed_statistical_decision_authority"
spec = importlib.util.spec_from_file_location(name, path)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load statistical decision authority")
module = importlib.util.module_from_spec(spec)
sys.modules[name] = module
spec.loader.exec_module(module)
payload = {
    "module_path": str(Path(module.__file__).resolve()),
    "panel_input_schema": module.PANEL_INPUT_SCHEMA_VERSION,
    "panel_result_schema": module.PANEL_RESULT_SCHEMA_VERSION,
    "policy_schema": module.POLICY_SCHEMA_VERSION,
    "policy": module.POLICY.to_mapping(),
    "terminal_flow_policy_schema": module.TERMINAL_FLOW_POLICY_SCHEMA_VERSION,
    "terminal_flow_policy": module.TERMINAL_FLOW_POLICY.to_mapping(),
}
sys.stdout.write(
    json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )
    + "\n"
)
'''
    expected = {
        "module_path": str(STATISTICAL_DECISION_AUTHORITY.resolve()),
        "panel_input_schema": EXPECTED_STATISTICAL_PANEL_INPUT_SCHEMA,
        "panel_result_schema": EXPECTED_STATISTICAL_PANEL_RESULT_SCHEMA,
        "policy_schema": EXPECTED_STATISTICAL_POLICY_SCHEMA,
        "policy": EXPECTED_STATISTICAL_DECISION_POLICY,
        "terminal_flow_policy_schema": EXPECTED_TERMINAL_FLOW_POLICY_SCHEMA,
        "terminal_flow_policy": EXPECTED_TERMINAL_FLOW_POLICY,
    }
    expected_stdout = json.dumps(
        expected,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ) + "\n"
    try:
        completed = subprocess.run(
            [
                sys.executable,
                "-I",
                "-B",
                "-c",
                probe,
                str(STATISTICAL_DECISION_AUTHORITY.resolve()),
            ],
            cwd=REPOSITORY_ROOT,
            env=amendment_environment(),
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
        )
    except subprocess.TimeoutExpired as error:
        raise VerificationError(
            "statistical decision authority probe timed out"
        ) from error
    require(
        completed.returncode == 0,
        "statistical decision authority probe failed "
        f"(exit {completed.returncode}): {completed.stderr.strip()!r}",
    )
    require(
        not completed.stderr,
        "statistical decision authority probe wrote stderr: "
        f"{completed.stderr!r}",
    )
    require(
        completed.stdout == expected_stdout,
        "statistical decision authority envelope mismatch",
    )
    return (
        "PASS statistical decision and terminal-flow policies: paired H/L "
        "threshold 0.05; U reported separately; equivalence margins "
        "0.05/0.05/0.02; SE<=1e-12 invalid; exact source/subtype-to-U map"
    )


def verify_dependence_result() -> str:
    require(
        DEPENDENCE_RESULT.is_file() and not DEPENDENCE_RESULT.is_symlink(),
        f"dependence result missing or unsafe: {DEPENDENCE_RESULT}",
    )
    expect_equal(
        "dependence result SHA-256",
        sha256_file(DEPENDENCE_RESULT),
        EXPECTED_DEPENDENCE_RESULT_SHA256,
    )
    result = load_json(DEPENDENCE_RESULT)

    amendment_path = str(AMENDMENT_ROOT)
    inserted_path = amendment_path not in sys.path
    if inserted_path:
        sys.path.insert(0, amendment_path)
    try:
        import dependence_diagnostics

        module_path = Path(dependence_diagnostics.__file__).resolve()
        expected_module_path = (AMENDMENT_ROOT / "dependence_diagnostics.py").resolve()
        require(
            module_path == expected_module_path,
            f"unexpected dependence validator module: {module_path}",
        )
        dependence_diagnostics.validate_result(result)
    except (ImportError, TypeError, ValueError) as error:
        raise VerificationError(
            f"strict dependence-result validation failed: {error}"
        ) from error
    finally:
        if inserted_path:
            sys.path.remove(amendment_path)

    expect_equal("dependence schema", result.get("schema_version"), EXPECTED_DEPENDENCE_SCHEMA)
    expect_equal("dependence status", result.get("status"), EXPECTED_DEPENDENCE_STATUS)
    expect_equal("dependence gate effect", result.get("gate_effect"), "none")
    expect_equal(
        "dependence numerical-gate eligibility",
        result.get("numerical_gate_eligible"),
        False,
    )
    expect_equal("dependence master seed", result.get("master_seed"), 20260808)

    assignment = mapping(result.get("assignment_audit"), "assignment_audit")
    expect_equal(
        "dependence assignment audit",
        assignment,
        {
            "allowed_assignment_count": 576,
            "canonical_assignment_table_sha256": EXPECTED_ASSIGNMENT_TABLE_SHA256,
            "donor_rule": "each self donor supplies exactly one yoke recipient in every block",
            "sampling_policy": "exact discrete uniform over allowed_set_index 0..575",
            "selection_probability": "1/576",
        },
    )
    design = mapping(result.get("design"), "dependence design")
    expect_equal(
        "outcome replicates per cell",
        design.get("outcome_replicates_per_cell"),
        1_000,
    )
    expect_equal(
        "formation replicates per cell",
        design.get("formation_replicates_per_cell"),
        2_000,
    )
    dgp = mapping(result.get("dgp"), "dependence dgp")
    expect_equal(
        "formation profiles",
        dgp.get("formation_profiles"),
        EXPECTED_FORMATION_PROFILES,
    )
    expect_equal(
        "dependence profiles",
        dgp.get("dependence_profiles"),
        EXPECTED_DEPENDENCE_PROFILES,
    )
    expect_equal(
        "outcome profiles",
        dgp.get("outcome_profiles"),
        EXPECTED_OUTCOME_PROFILES,
    )

    formations = list_value(result.get("formation_diagnostics"), "formation_diagnostics")
    expect_equal("formation diagnostic count", len(formations), 6)
    formation_coordinates = [
        [
            mapping(row, f"formation_diagnostics[{index}]").get("profile"),
            mapping(row, f"formation_diagnostics[{index}]").get(
                "high_probability_given_valid"
            ),
            mapping(row, f"formation_diagnostics[{index}]").get("outer_replicates"),
        ]
        for index, row in enumerate(formations)
    ]
    expect_equal(
        "formation diagnostic coordinates",
        formation_coordinates,
        [
            [profile, high_probability, 2_000]
            for profile in EXPECTED_FORMATION_PROFILES
            for high_probability in (0.1, 0.3, 0.5)
        ],
    )

    outcomes = list_value(result.get("outcome_diagnostics"), "outcome_diagnostics")
    expect_equal("outcome diagnostic count", len(outcomes), 8)
    observed_outcome_profiles: list[dict[str, Any]] = []
    for index, raw_row in enumerate(outcomes):
        row = mapping(raw_row, f"outcome_diagnostics[{index}]")
        expect_equal(
            f"outcome_diagnostics[{index}] outer replicates",
            row.get("outer_replicates"),
            1_000,
        )
        observed_outcome_profiles.append(
            {
                "label": row.get("label"),
                "scenario": row.get("scenario"),
                "dependence_profile": row.get("dependence_profile"),
                "failure_profile": row.get("failure_profile"),
            }
        )
    expect_equal(
        "stored outcome diagnostic profile order",
        observed_outcome_profiles,
        EXPECTED_OUTCOME_PROFILES,
    )
    return (
        "PASS dependence result: non-gating; 6 formation x 2000 and "
        "8 outcome x 1000 profiles; sha256=" + EXPECTED_DEPENDENCE_RESULT_SHA256
    )


def verify_dependence_replay() -> str:
    require(
        DEPENDENCE_RUNNER.is_file() and not DEPENDENCE_RUNNER.is_symlink(),
        f"dependence runner missing or unsafe: {DEPENDENCE_RUNNER}",
    )
    try:
        completed = subprocess.run(
            [sys.executable, "-B", str(DEPENDENCE_RUNNER), "--check"],
            cwd=REPOSITORY_ROOT,
            env=amendment_environment(),
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=600,
        )
    except subprocess.TimeoutExpired as error:
        raise VerificationError(
            "deterministic dependence replay exceeded the 600-second gate"
        ) from error
    detail = "\n".join((completed.stdout, completed.stderr)).strip()
    require(
        completed.returncode == 0,
        f"deterministic dependence replay failed (exit {completed.returncode}): {detail}",
    )
    expected = re.compile(
        r"^PASS dependence diagnostic replay: sha256="
        + re.escape(EXPECTED_DEPENDENCE_RESULT_SHA256)
        + r" elapsed_seconds=[0-9]+\.[0-9]{3}$"
    )
    lines = [line for line in completed.stdout.splitlines() if line]
    require(
        len(lines) == 1 and expected.fullmatch(lines[0]) is not None,
        f"unexpected deterministic dependence replay output: {detail!r}",
    )
    require(not completed.stderr.strip(), f"dependence replay wrote stderr: {completed.stderr!r}")
    return lines[0]


def forbidden_release_path(relative: PurePosixPath) -> bool:
    parts = set(relative.parts)
    name = relative.name
    return bool(
        parts & {"subscription_calibration", "paper8_external_lanes", "records", "transcripts"}
        or name.endswith("_raw.json")
        or name.endswith("_response.md")
        or name == "events.jsonl"
    )


def verify_release_scope_and_optional_manifest() -> str:
    local_files: dict[str, Path] = {}
    for path in RELEASE_ROOT.rglob("*"):
        if path.is_symlink():
            raise VerificationError(f"symlink forbidden in stage-1 release: {path}")
        if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        relative = PurePosixPath(path.relative_to(RELEASE_ROOT).as_posix())
        require(not forbidden_release_path(relative), f"forbidden private/raw release path: {relative}")
        local_files[relative.as_posix()] = path

    candidates = sorted(
        path
        for path in RELEASE_ROOT.glob("*.sha256")
        if "manifest" in path.name.lower()
    )
    require(
        len(candidates) == 1,
        f"expected exactly one local release manifest, found: {candidates}",
    )

    manifest = candidates[0]
    expected = read_manifest(manifest)
    actual = {
        relative: path
        for relative, path in local_files.items()
        if path != manifest
    }
    for relative in expected:
        require(
            not forbidden_release_path(PurePosixPath(relative)),
            f"forbidden private/raw manifest path: {relative}",
        )
    missing = sorted(set(expected) - set(actual))
    extra = sorted(set(actual) - set(expected))
    mismatched = sorted(
        relative
        for relative in set(expected) & set(actual)
        if sha256_file(actual[relative]) != expected[relative]
    )
    require(not missing, f"local release manifest paths missing: {missing}")
    require(not extra, f"unmanifested local release paths: {extra}")
    require(not mismatched, f"local release digest mismatches: {mismatched}")
    return f"PASS ({len(expected)} entries; {manifest.name})"


def environment_status() -> str:
    python_version = platform.python_version()
    try:
        numpy_version = metadata.version("numpy")
    except metadata.PackageNotFoundError:
        numpy_version = "not installed"
    match = python_version == REFERENCE_PYTHON and numpy_version == REFERENCE_NUMPY
    return (
        f"runtime Python={python_version}, NumPy={numpy_version}; "
        f"current-reference match={str(match).lower()} (non-gating, not original-environment proof)"
    )


def verify_generated_artifacts() -> str:
    generator = RELEASE_ROOT / "generate_tables_figures.py"
    require(
        generator.is_file() and not generator.is_symlink(),
        f"generator missing or unsafe: {generator}",
    )
    try:
        completed = subprocess.run(
            [sys.executable, str(generator), "--check"],
            cwd=REPOSITORY_ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=120,
        )
    except subprocess.TimeoutExpired as error:
        raise VerificationError("generated-artifact check timed out") from error
    detail = (completed.stderr or completed.stdout).strip()
    require(
        completed.returncode == 0,
        f"generated-artifact check failed (exit {completed.returncode}): {detail}",
    )
    matches = re.findall(
        r"^PASS generated artifacts: ([0-9]+) files match byte-for-byte$",
        completed.stdout,
        re.MULTILINE,
    )
    require(
        len(matches) == 1
        and int(matches[0]) == EXPECTED_GENERATED_ARTIFACT_COUNT,
        f"unexpected generated-artifact check output: {completed.stdout.strip()!r}",
    )
    return f"PASS generated artifacts: {matches[0]} files match byte-for-byte"


def verify_self_contained_html() -> str:
    html_path = RELEASE_ROOT / "output" / "html" / "binding_test_stage1.html"
    require(
        html_path.is_file() and not html_path.is_symlink(),
        f"rendered HTML missing or unsafe: {html_path}",
    )
    rendered = html_path.read_text(encoding="utf-8")
    embedded_count = rendered.count('src="data:image/svg+xml;base64,')
    require(
        embedded_count == EXPECTED_EMBEDDED_SVG_COUNT,
        "rendered HTML embedded-SVG count mismatch: "
        f"{embedded_count} != {EXPECTED_EMBEDDED_SVG_COUNT}",
    )
    require(
        re.search(r'src="figures/[^"]+\.svg"', rendered) is None,
        "rendered HTML retains a relative SVG reference",
    )
    require("file://" not in rendered, "rendered HTML contains a local file URI")
    return f"PASS self-contained HTML: {embedded_count} embedded SVG figures"


def main() -> int:
    try:
        release_manifest_status = verify_release_scope_and_optional_manifest()
        manifest_count = verify_manifest_tree(ZERO_CALL_ROOT, ZERO_CALL_MANIFEST)
        result = load_json(REDESIGN_RESULT)
        verify_trust_root(result)
        amendment_test_status = verify_amendment_tests()
        statistical_decision_status = verify_statistical_decision_policy()
        dependence_result_status = verify_dependence_result()
        dependence_replay_status = verify_dependence_replay()
        generated_artifact_status = verify_generated_artifacts()
        self_contained_html_status = verify_self_contained_html()
    except (
        KeyError,
        OSError,
        OverflowError,
        TypeError,
        UnicodeError,
        ValueError,
        VerificationError,
    ) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    print(f"PASS zero_call manifest: {manifest_count} entries")
    print(f"PASS scientific source aggregate: {EXPECTED_SOURCE_AGGREGATE}")
    print("PASS stable trust root: 84 cells; B=384; broad equivalence ABANDONED")
    print(
        "PASS stable-metadata policy: generated_date and test_suite.transcript/timing "
        "were deliberately excluded from scientific equality checks"
    )
    print(amendment_test_status)
    print(statistical_decision_status)
    print(dependence_result_status)
    print(dependence_replay_status)
    print(generated_artifact_status)
    print(self_contained_html_status)
    print(f"LOCAL release manifest: {release_manifest_status}")
    print(f"INFO reference environment: {environment_status()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
