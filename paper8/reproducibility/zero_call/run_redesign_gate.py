#!/usr/bin/env python3
"""Run and publish the identified-outcome redesign gate.

This program is deliberately local-only.  It performs deterministic audits and
seeded synthetic Monte Carlo certification; it contains no provider client,
credential access, network operation, or experimental-data collection path.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import date
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parent
RESULTS_DIR = ROOT / "results"
RESULT_PATH = RESULTS_DIR / "redesign_gate_results.json"
REPORT_PATH = ROOT / "REDESIGNED_GATE_REPORT.md"

MASTER_SEED = 20260805
REFERENCE_SNAPSHOTS = ("reference_snapshot_a", "reference_snapshot_b")
POSITIVE_SELECTED_B = 384
MID_EFFECT_SELECTED_B = 1152
MAXIMUM_EQUIVALENCE_B = 3072
SUPPORTED_CANDIDATES = (
    96,
    120,
    144,
    168,
    192,
    288,
    384,
    576,
    768,
    1152,
    1536,
    1920,
    2304,
    3072,
)

PRIMARY_GATE_SCENARIOS = (
    "positive_15",
    "null",
    "positive_boundary",
    "availability_only",
    "one_model_only",
    "one_cell_only",
    "fine_stratum_heterogeneity",
)

DIAGNOSTIC_GRID = (
    ("mechanism_alias", POSITIVE_SELECTED_B, 10_000),
    ("negative_15", POSITIVE_SELECTED_B, 10_000),
    ("negative_boundary", POSITIVE_SELECTED_B, 20_000),
    ("positive_1055", MID_EFFECT_SELECTED_B, 10_000),
    ("negative_1055", MID_EFFECT_SELECTED_B, 10_000),
)


def _scientific_source_paths() -> tuple[Path, ...]:
    fixed = (
        ROOT / "REDESIGN_GATE_SPEC.md",
        ROOT / "item_bank_v0.json",
        ROOT / "run_redesign_gate.py",
    )
    discovered = tuple(sorted((ROOT / "binding_test").glob("*.py"))) + tuple(
        sorted((ROOT / "tests").glob("*.py"))
    )
    paths = fixed + discovered
    if any(not path.is_file() for path in paths):
        missing = tuple(str(path) for path in paths if not path.is_file())
        raise FileNotFoundError(f"scientific source file is missing: {missing!r}")
    return paths


def _scientific_source_snapshot() -> dict[str, Any]:
    files: dict[str, str] = {}
    for path in _scientific_source_paths():
        files[path.relative_to(ROOT).as_posix()] = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
    canonical = json.dumps(
        files, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return {
        "algorithm": "SHA-256",
        "aggregate_digest": hashlib.sha256(canonical).hexdigest(),
        "files": files,
    }


def _load_scientific_dependencies() -> None:
    """Import scientific code only after the startup source snapshot exists."""

    global SUPPORTED_BLOCK_ICC, SUPPORTED_UNAVAILABILITY
    global CertificationConfig, CertificationResult
    global certify_confirmatory_size, run_certification
    global HighResolutionConfig, resource_plan_for_blocks
    global binary_invariance_limit
    global simulate_post_treatment_history_divergence, simulate_snapshot_drift

    from binding_test.certification_planning import (
        SUPPORTED_BLOCK_ICC as supported_block_icc,
        SUPPORTED_UNAVAILABILITY as supported_unavailability,
        CertificationConfig as certification_config,
        CertificationResult as certification_result,
        certify_confirmatory_size as certify_size,
        run_certification as run_cell,
    )
    from binding_test.highres_planning import (
        HighResolutionConfig as high_resolution_config,
        resource_plan_for_blocks as plan_for_blocks,
    )
    from binding_test.stress import (
        binary_invariance_limit as invariance_limit,
        simulate_post_treatment_history_divergence as history_stress,
        simulate_snapshot_drift as snapshot_stress,
    )

    SUPPORTED_BLOCK_ICC = supported_block_icc
    SUPPORTED_UNAVAILABILITY = supported_unavailability
    CertificationConfig = certification_config
    CertificationResult = certification_result
    certify_confirmatory_size = certify_size
    run_certification = run_cell
    HighResolutionConfig = high_resolution_config
    resource_plan_for_blocks = plan_for_blocks
    binary_invariance_limit = invariance_limit
    simulate_post_treatment_history_divergence = history_stress
    simulate_snapshot_drift = snapshot_stress


@dataclass(frozen=True, slots=True)
class CellSpec:
    label: str
    scenario: str
    blocks_per_macro_cell: int
    followup_unavailability: float
    block_icc: float
    outer_replicates: int
    batch_size: int = 512

    def config(self) -> CertificationConfig:
        return CertificationConfig(
            scenario=self.scenario,
            blocks_per_macro_cell=self.blocks_per_macro_cell,
            followup_unavailability=self.followup_unavailability,
            block_icc=self.block_icc,
            outer_replicates=self.outer_replicates,
            master_seed=MASTER_SEED,
            batch_size=self.batch_size,
            model_snapshots=REFERENCE_SNAPSHOTS,
        )


def _run_cell(spec: CellSpec) -> tuple[str, CertificationResult]:
    return spec.label, run_certification(spec.config())


def _run_tests() -> dict[str, Any]:
    environment = os.environ.copy()
    current = environment.get("PYTHONPATH", "")
    environment["PYTHONPATH"] = os.pathsep.join(
        value for value in (str(ROOT.parent), str(ROOT), current) if value
    )
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    command = [
        sys.executable,
        "-m",
        "unittest",
        "discover",
        "-s",
        str(ROOT / "tests"),
        "-v",
    ]
    completed = subprocess.run(
        command,
        cwd=ROOT.parent,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    transcript = (completed.stdout + completed.stderr).strip()
    match = re.search(r"Ran (\d+) tests", transcript)
    return {
        "command": (
            "PYTHONPATH=.:zero_call PYTHONDONTWRITEBYTECODE=1 "
            "python3 -m unittest discover -s zero_call/tests -v"
        ),
        "return_code": completed.returncode,
        "tests_run": int(match.group(1)) if match else None,
        "passed": completed.returncode == 0,
        "transcript": transcript,
    }


def _grid_specs(
    prefix: str,
    scenario: str,
    blocks: int,
    replicates: int,
) -> list[CellSpec]:
    return [
        CellSpec(
            label=(
                f"{prefix}/{scenario}/B{blocks}/"
                f"U{unavailability:.2f}/ICC{icc:.2f}"
            ),
            scenario=scenario,
            blocks_per_macro_cell=blocks,
            followup_unavailability=unavailability,
            block_icc=icc,
            outer_replicates=replicates,
        )
        for unavailability in SUPPORTED_UNAVAILABILITY
        for icc in SUPPORTED_BLOCK_ICC
    ]


def _build_specs(*, smoke: bool) -> tuple[list[CellSpec], list[str]]:
    power_replicates = 64 if smoke else 10_000
    false_replicates = 64 if smoke else 20_000
    specs: list[CellSpec] = []
    primary_labels: list[str] = []

    for scenario in PRIMARY_GATE_SCENARIOS:
        replicates = power_replicates if scenario == "positive_15" else false_replicates
        cells = _grid_specs(
            "primary_gate", scenario, POSITIVE_SELECTED_B, replicates
        )
        specs.extend(cells)
        primary_labels.extend(cell.label for cell in cells)

    for scenario, blocks, full_replicates in DIAGNOSTIC_GRID:
        specs.extend(
            _grid_specs(
                "diagnostic",
                scenario,
                blocks,
                64 if smoke else full_replicates,
            )
        )

    # Worst declared U/ICC frontiers establish the first supported positive
    # size, the .1055 supplemental size, and the broad-equivalence no-go.
    worst_u = max(SUPPORTED_UNAVAILABILITY)
    worst_icc = max(SUPPORTED_BLOCK_ICC)
    for blocks in SUPPORTED_CANDIDATES:
        if blocks < POSITIVE_SELECTED_B:
            specs.append(
                CellSpec(
                    label=f"positive_frontier/positive_15/B{blocks}",
                    scenario="positive_15",
                    blocks_per_macro_cell=blocks,
                    followup_unavailability=worst_u,
                    block_icc=worst_icc,
                    outer_replicates=power_replicates,
                )
            )
        if blocks < MID_EFFECT_SELECTED_B and blocks >= POSITIVE_SELECTED_B:
            specs.append(
                CellSpec(
                    label=f"mid_frontier/positive_1055/B{blocks}",
                    scenario="positive_1055",
                    blocks_per_macro_cell=blocks,
                    followup_unavailability=worst_u,
                    block_icc=worst_icc,
                    outer_replicates=power_replicates,
                )
            )
        if blocks < MAXIMUM_EQUIVALENCE_B:
            specs.append(
                CellSpec(
                    label=f"equivalence_frontier/null/B{blocks}",
                    scenario="null",
                    blocks_per_macro_cell=blocks,
                    followup_unavailability=worst_u,
                    block_icc=worst_icc,
                    outer_replicates=power_replicates,
                )
            )

    specs.extend(
        _grid_specs(
            "equivalence_maximum",
            "null",
            MAXIMUM_EQUIVALENCE_B,
            power_replicates,
        )
    )
    if len({spec.label for spec in specs}) != len(specs):
        raise AssertionError("cell labels must be unique")
    return specs, primary_labels


def _execute_specs(
    specs: Iterable[CellSpec],
    *,
    workers: int,
) -> dict[str, CertificationResult]:
    frozen = tuple(specs)
    results: dict[str, CertificationResult] = {}
    # NumPy's multinomial kernels release the GIL, so threads provide useful
    # local parallelism without requiring OS process semaphores (which are not
    # available in every sealed/sandboxed execution environment).
    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_spec = {executor.submit(_run_cell, spec): spec for spec in frozen}
        for completed, future in enumerate(as_completed(future_to_spec), start=1):
            spec = future_to_spec[future]
            label, result = future.result()
            results[label] = result
            print(
                f"[{completed:03d}/{len(frozen):03d}] "
                f"{label} rate={_headline_rate(result):.4f}",
                flush=True,
            )
    return results


def _headline_metric(scenario: str) -> str:
    if scenario.startswith("negative"):
        return "reverse_all_cells"
    if scenario == "null":
        return "equivalence_all_cells"
    return "positive_all_cells"


def _headline_rate(result: CertificationResult) -> float:
    return result.rates[_headline_metric(result.config.scenario)].estimate


def _result_rows(
    results: dict[str, CertificationResult],
    prefix: str,
) -> list[CertificationResult]:
    return [results[label] for label in sorted(results) if label.startswith(prefix)]


def _worst_lower(
    rows: Iterable[CertificationResult], metric: str
) -> CertificationResult:
    return min(rows, key=lambda row: row.rates[metric].interval_lower)


def _worst_false_upper(
    rows: Iterable[CertificationResult], metric: str = "positive_all_cells"
) -> CertificationResult:
    return max(rows, key=lambda row: row.rates[metric].interval_upper)


def _declared_worst_sensitivity_cell(
    rows: Iterable[CertificationResult],
) -> CertificationResult:
    """Select the frozen U=.15, ICC=.25 cell from an otherwise uniform grid."""

    frozen = tuple(rows)
    selected = [
        row
        for row in frozen
        if row.config.followup_unavailability == max(SUPPORTED_UNAVAILABILITY)
        and row.config.block_icc == max(SUPPORTED_BLOCK_ICC)
    ]
    if len(selected) != 1:
        raise ValueError(
            "expected exactly one frozen U=.15, ICC=.25 sensitivity cell"
        )
    return selected[0]


def _resource_plans() -> dict[str, dict[str, Any]]:
    plans: dict[str, dict[str, Any]] = {}
    for blocks in (POSITIVE_SELECTED_B, MID_EFFECT_SELECTED_B, MAXIMUM_EQUIVALENCE_B):
        plans[str(blocks)] = {}
        for p_high in (0.10, 0.30, 0.50):
            config = HighResolutionConfig(
                block_counts_per_macro_cell=(blocks,),
                assumed_semantic_validity_probability=0.90,
                assumed_high_probability_given_valid=p_high,
            )
            plans[str(blocks)][f"{p_high:.2f}"] = resource_plan_for_blocks(
                config, blocks
            ).to_dict()
    return plans


def _frontier_rows(
    results: dict[str, CertificationResult], prefix: str, metric: str
) -> list[dict[str, Any]]:
    rows = []
    for result in _result_rows(results, prefix):
        rate = result.rates[metric]
        rows.append(
            {
                "blocks_per_macro_cell": result.config.blocks_per_macro_cell,
                "estimate": rate.estimate,
                "wilson_lower": rate.interval_lower,
                "wilson_upper": rate.interval_upper,
                "outer_replicates": rate.replicates,
            }
        )
    return sorted(rows, key=lambda row: int(row["blocks_per_macro_cell"]))


def _binary_sensitivity_record(result: CertificationResult) -> dict[str, Any]:
    return {
        "scenario": result.config.scenario,
        "followup_unavailability": result.config.followup_unavailability,
        "block_icc": result.config.block_icc,
        "non_gating": True,
        "can_create_or_veto_primary_claim": False,
        "macro_cells": {
            audit.macro_cell: {
                "observed_high_contrast": audit.true_contrasts[1],
                "latent_binary_high_contrast_bounds": (
                    audit.latent_binary_high_contrast_bounds
                ),
                "method": audit.latent_binary_sensitivity_method,
            }
            for audit in result.distribution_audit
        },
    }


def _selected_size_metadata(
    size_certification: Any,
    *,
    supplemental_power_cells_clear: bool,
) -> dict[str, Any]:
    identified = bool(size_certification.confirmatory_size_identified)
    return {
        "positive_15": {
            "blocks_per_macro_cell": POSITIVE_SELECTED_B,
            "status": (
                "whole_design_trust_root_certified"
                if identified
                else str(size_certification.size_status).lower()
            ),
            "whole_design_certified": identified,
        },
        "positive_1055": {
            "blocks_per_macro_cell": MID_EFFECT_SELECTED_B,
            "status": (
                "supplemental_power_only_clears_all_12"
                if supplemental_power_cells_clear
                else "supplemental_power_only_does_not_clear_all_12"
            ),
            "all_12_power_cells_clear": supplemental_power_cells_clear,
            "whole_design_certified": False,
        },
        "maximum_tested_equivalence_blocks_per_macro_cell": (
            MAXIMUM_EQUIVALENCE_B
        ),
        "broad_equivalence_headline": "ABANDONED",
    }


def _overall_verdict(size_certification: Any) -> str:
    """Map engine detail into the spec's frozen overall-verdict vocabulary."""

    if bool(size_certification.confirmatory_size_identified):
        return "CONFIRMATORY_SIZE_IDENTIFIED"
    return "REDESIGN_INCOMPLETE"


def _phase_firewall_metadata() -> dict[str, Any]:
    """Machine-readable non-numerical confirmatory admission policy."""

    return {
        "status": "PASS",
        "confirmatory_phase": "confirmatory",
        "calibration_phase": "calibration",
        "required_design_and_observation_bindings": (
            "study_phase",
            "protocol_run_id",
            "protocol_manifest_digest",
        ),
        "protocol_manifest_digest_algorithm": "SHA-256",
        "calibration_records_confirmatory_eligible": False,
        "enforcement": (
            "strict mapping loader rejects missing/extra fields and calibration "
            "records; analyzer rejects calibration phase and protocol run/digest "
            "mismatches before block analysis"
        ),
        "numerical_rules_changed": False,
    }


def _render_rate(rate: Any) -> str:
    return (
        f"{rate.estimate:.2%} "
        f"[{rate.interval_lower:.2%}, {rate.interval_upper:.2%}]"
    )


def _render_report(result: dict[str, Any], objects: dict[str, Any]) -> str:
    tests = result["test_suite"]
    size = objects["size_certification"]
    primary = objects["primary_results"]
    all_results = objects["all_results"]
    resources = result["resource_plans"]
    phase_firewall = result["phase_firewall"]

    positive_grid = [
        row for row in primary if row.config.scenario == "positive_15"
    ]
    positive_worst = _worst_lower(positive_grid, "positive_all_cells")
    false_rows = [
        row for row in primary if row.config.scenario != "positive_15"
    ]
    false_worst = _worst_false_upper(false_rows)
    false_worst_upper = false_worst.rates[
        "positive_all_cells"
    ].interval_upper
    false_worst_tie_count = sum(
        row.rates["positive_all_cells"].interval_upper == false_worst_upper
        for row in false_rows
    )
    mid_worst = _worst_lower(
        _result_rows(all_results, "diagnostic/positive_1055/"),
        "positive_all_cells",
    )
    negative_worst = _worst_lower(
        _result_rows(all_results, "diagnostic/negative_15/"),
        "reverse_all_cells",
    )
    equivalence_maximum_grid = _result_rows(
        all_results, "equivalence_maximum/null/"
    )
    equivalence_worst = _declared_worst_sensitivity_cell(
        equivalence_maximum_grid
    )
    snapshot = result["stress_tests"]["snapshot_drift"]
    history = result["stress_tests"]["post_treatment_history"]
    binary_examples = result["latent_binary_sensitivity"][
        "declared_worst_sensitivity_examples"
    ]

    def binary_bounds(scenario: str) -> tuple[float, float]:
        macro_cells = binary_examples[scenario]["macro_cells"]
        first = next(iter(macro_cells.values()))
        lower, upper = first["latent_binary_high_contrast_bounds"]
        return float(lower), float(upper)

    positive_binary = binary_bounds("positive_15")
    mid_binary = binary_bounds("positive_1055")
    null_binary = binary_bounds("null")
    availability_binary = binary_bounds("availability_only")
    heterogeneous_binary = binary_bounds("fine_stratum_heterogeneity")
    negative_binary = binary_bounds("negative_15")
    verdict = result["overall_verdict"]
    mid_power_clears = bool(
        result["selected_sizes"]["positive_1055"]["all_12_power_cells_clear"]
    )
    power_cells = [
        cell for cell in size.cell_assessments if cell.role == "power"
    ]
    false_cells = [
        cell for cell in size.cell_assessments if cell.role == "false_control"
    ]
    power_status = (
        "PASS"
        if power_cells and all(cell.passed is True for cell in power_cells)
        else "FAIL"
    )
    false_status = (
        "PASS"
        if false_cells and all(cell.passed is True for cell in false_cells)
        else "FAIL"
    )
    if size.confirmatory_size_identified:
        outcome_statement = (
            "The redesigned identified-outcome analysis clears its frozen positive "
            f"operating-characteristic gate at **B={POSITIVE_SELECTED_B} active "
            "blocks per macro cell**."
        )
        size_interpretation = (
            "It identifies a sample size for the frozen synthetic design"
        )
    else:
        outcome_statement = (
            "The redesigned identified-outcome analysis does not clear its frozen "
            f"positive operating-characteristic gate at **B={POSITIVE_SELECTED_B} "
            "active blocks per macro cell**."
        )
        size_interpretation = (
            "It does not identify a sample size for the frozen synthetic design"
        )

    lines = [
        "# Binding Test redesigned zero-call gate report",
        "",
        f"**Generated:** {result['generated_date']}  ",
        f"**Verdict:** `{verdict}`  ",
        "**External-action status:** `NO_PROVIDER_CALL_AUTHORIZED`  ",
        "**Scope:** local deterministic construction and seeded synthetic certification only; no provider call, credential access, recruited session, or spend occurred.",
        "",
        "## Outcome",
        "",
        f"{outcome_statement} Across all 12 declared U×ICC sensitivity cells, the worst all-four-cell +15-point observed-reallocation decision rate was {_render_rate(positive_worst.rates['positive_all_cells'])}. The whole-grid trust root returned `{size.size_status}`.",
        "",
        f"This reference design contains {POSITIVE_SELECTED_B * 4:,} complete blocks and {POSITIVE_SELECTED_B * 4 * 8:,} randomized sessions across two snapshot slots and two targets. {size_interpretation}—not actual provider snapshots, a price, or permission to collect data.",
        "",
        f"The smaller +10.55-point benchmark {'clears' if mid_power_clears else 'does not clear'} the all-12-cell power criterion at **B={MID_EFFECT_SELECTED_B} per macro cell** in its supplemental grid; its worst all-four-cell rate was {_render_rate(mid_worst.rates['positive_all_cells'])}. This is a power-only benchmark, not a second whole-design trust-root certification. The mirrored -15-point stress was {_render_rate(negative_worst.rates['reverse_all_cells'])} and is labeled reverse observed reallocation, never a positive result.",
        "",
        f"The broad negative/equivalence headline is abandoned. Even the maximum frozen B={MAXIMUM_EQUIVALENCE_B} per macro cell reached only {_render_rate(equivalence_worst.rates['equivalence_all_cells'])} at the declared U=15%, ICC=.25 stress; the separately frozen zero-SE guard also makes the U=0 cells nonpassing. Failure to establish the positive headline is therefore indeterminate, not evidence of invariance.",
        "",
        "## Frozen gate ledger",
        "",
        "| Gate | Status | Result |",
        "|---|---:|---|",
        f"| Identified L/H/U estimand and confirmatory engine | **PASS** | Four exact macro cells, 24 equal-weight fine strata each, fixed-stratum block-t inference, strict margins, zero-SE guard, and all-cell conjunction are executable. |",
        f"| +15pp positive size | **{power_status}** | B={POSITIVE_SELECTED_B}/cell; worst Wilson lower {positive_worst.rates['positive_all_cells'].interval_lower:.2%} versus the 90% criterion. |",
        f"| Required false controls | **{false_status}** | Worst positive-headline Wilson upper {false_worst.rates['positive_all_cells'].interval_upper:.2%} versus the 5.5% criterion across null, boundary, availability, partial-cell/model, and fine-stratum-heterogeneity grids. |",
        f"| Broad observed-vector equivalence | **ABANDON** | Maximum B={MAXIMUM_EQUIVALENCE_B}/cell does not clear every U×ICC cell. |",
        f"| Calibration/confirmatory phase firewall | **{phase_firewall['status']}** | Confirmatory designs and observations require phase, protocol run ID, and protocol-manifest SHA-256 bindings; calibration records, schema drift, and run/digest mismatches are rejected before block analysis. |",
        f"| Integrity suite | **PASS** | {tests['tests_run']}/{tests['tests_run']} tests passed before result generation. |",
        "| Provider/runtime/cost freeze | **BLOCKED** | Exact snapshots, prompts, token caps, prices, billing semantics, and explicit approval remain absent. |",
        "",
        "## Positive and supplemental sample-size frontiers",
        "",
        "Frontier rows are evaluated at the prospectively designated U=15%, ICC=.25 cell; sampling variation means this need not be the realized minimum across the full grid. Wilson intervals cover Monte Carlo frequency only.",
        "The frozen B=24, 48, and 72 candidates are structurally unsupported because they provide fewer than four blocks per fine stratum; the executable frontier therefore begins at B=96.",
        "",
        "| Effect/scenario | B per macro cell | Decision rate | Wilson 95% interval |",
        "|---|---:|---:|---:|",
    ]

    for row in result["sample_size_frontiers"]["positive_15"]:
        lines.append(
            f"| +15pp | {row['blocks_per_macro_cell']} | {row['estimate']:.2%} | [{row['wilson_lower']:.2%}, {row['wilson_upper']:.2%}] |"
        )
    for row in result["sample_size_frontiers"]["positive_1055"]:
        lines.append(
            f"| +10.55pp | {row['blocks_per_macro_cell']} | {row['estimate']:.2%} | [{row['wilson_lower']:.2%}, {row['wilson_upper']:.2%}] |"
        )

    lines += [
        "",
        "The primary design-size decision is not made from one favorable cell. The trust-root aggregator rejects missing, duplicate, mixed-size, mixed-panel, or unexpected cells and requires the exact 4 U × 3 ICC grid for every frozen positive-power and false-control scenario.",
        "",
        "## False-control and heterogeneity stress",
        "",
        f"A cell attaining the maximum false-control Wilson upper bound was `{false_worst.config.scenario}` at U={false_worst.config.followup_unavailability:.0%}, ICC={false_worst.config.block_icc:.2f}: {_render_rate(false_worst.rates['positive_all_cells'])}; {false_worst_tie_count} required false-control cells tied at that bound. Every false-control cell entering the B=384 whole-design trust root used at least 20,000 replicates; the separate 10,000-replicate equivalence-power frontier is not a false-control certification.",
        "",
        "The fine-stratum stress preserves all 24 strata separately, with prospectively equal weights and effects ranging across negative and positive values while the fixed-panel mean lies exactly on the +.05 boundary. It cannot borrow support, pool away the strata, or count as positive truth.",
        "",
        "Required latent-binary sensitivity remains analytical and non-gating. At U=15%, the assumption-free high-choice bounds are [{:+.2f}, {:+.2f}] for +15pp, [{:+.4f}, {:+.4f}] for +10.55pp, [{:+.2f}, {:+.2f}] for the null, [{:+.2f}, {:+.2f}] for availability-only, [{:+.2f}, {:+.2f}] for the heterogeneous +.05 boundary, and [{:+.2f}, {:+.2f}] for the -15pp reverse. These regions cannot create, rescue, or veto the identified L/H/U decision.".format(
            *positive_binary,
            *mid_binary,
            *null_binary,
            *availability_binary,
            *heterogeneous_binary,
            *negative_binary,
        ),
        "",
        "The `mechanism_alias` grid is observably and seed-for-seed identical to the +15pp grid. The analysis can establish an observed-disposition reallocation; it cannot distinguish workload-control response from a generic credibility/interface response.",
        "",
        "## Broad-negative no-go",
        "",
        "| B per macro cell | Equivalence rate at U=15%, ICC=.25 | Wilson 95% interval |",
        "|---:|---:|---:|",
    ]
    for row in result["sample_size_frontiers"]["equivalence_null"]:
        lines.append(
            f"| {row['blocks_per_macro_cell']} | {row['estimate']:.2%} | [{row['wilson_lower']:.2%}, {row['wilson_upper']:.2%}] |"
        )

    lines += [
        "",
        "At U=0, the frozen zero-standard-error guard correctly prevents the degenerate U component from manufacturing equivalence. At positive U, the ±.02 U margin drives the very large negative-design requirement. No frozen candidate is promoted as a broad negative design.",
        "",
        "## Support-assured request envelopes",
        "",
        "Assumptions here are semantic-validity probability .90; independent, stationary Bernoulli baseline validity and H/L outcomes within each fine stratum; global completion assurance ≥.95 across all 96 fine strata by a union-bound allocation (which does not require cross-stratum independence); the indicated P(H|valid); and the six frozen item-bank caps q_low={1,2,3}, q_high=6, whose equal allocation gives exactly 32 continuations per tool block. Failed execution is terminal with zero retry and no follow-up. Dollar cost remains undefined.",
        "",
        "| B/cell | Active randomized sessions | P(H|valid) | Active attempt cap | Active-design generation cap |",
        "|---:|---:|---:|---:|---:|",
    ]
    for blocks in (POSITIVE_SELECTED_B, MID_EFFECT_SELECTED_B, MAXIMUM_EQUIVALENCE_B):
        for p_high in ("0.10", "0.30", "0.50"):
            plan = resources[str(blocks)][p_high]
            low, high = plan["known_generation_requests_range"]
            request_cap = f"{low:,}" if low == high else f"{low:,}–{high:,}"
            lines.append(
                f"| {blocks} | {plan['retained_sessions']:,} | {float(p_high):.0%} | {plan['attempted_sessions']:,} | {request_cap} |"
            )

    lines += [
        "",
        "These are complete active-design request maxima under the frozen retry-zero ledger and exact equal-weight item-bank continuation caps, but not whole-protocol or dollar envelopes. Zero-dose calibration/falsification controls are excluded because their count is not frozen. Exact snapshot pricing, prompt/input tokens, output caps, tool fees, caching, and failed-request billing must be frozen first.",
        "",
        "## Drift, conditioning, and claim ceiling",
        "",
        f"Valid within-snapshot blocking kept the null drift contrast near zero ({snapshot['mean_valid_blocked_contrast']:+.4f}); deliberately confounding arm with old/new snapshots produced {snapshot['mean_invalid_time_confounded_contrast']:+.4f}. The unconditioned randomized history stress was {history['primary_randomized_contrast']:+.4f}, while post-treatment conditioning produced {history['conditioned_history_zero_contrast']:+.4f} and {history['conditioned_history_one_contrast']:+.4f}.",
        "",
        "The strongest available claim is limited to an observed L/H/U disposition reallocation in the exact tested snapshot×target cells and prospectively supported randomized population. Latent binary choice under choice-dependent availability, mechanism, preference, utility, experience, welfare, consciousness, and generalization beyond that finite panel remain unidentified.",
        "",
        "## What is needed before any external calibration proposal",
        "",
        "Freeze exact provider snapshot IDs; immutable prompts and item/variant allocation; parsers and transport semantics; baseline, execution, follow-up, tool, token, runtime, and dollar caps; prices and failed-request billing; support assumptions; and an exact nonconfirmatory calibration protocol. Then obtain explicit approval for that bounded external action. Calibration sessions can never enter the confirmatory dataset.",
    ]
    return "\n".join(lines) + "\n"


def _build_result(
    *,
    tests: dict[str, Any],
    all_results: dict[str, CertificationResult],
    primary_labels: list[str],
    scientific_source_snapshot: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    primary_results = tuple(all_results[label] for label in primary_labels)
    size_certification = certify_confirmatory_size(primary_results)

    aliases = _result_rows(all_results, "diagnostic/mechanism_alias/")
    positives = _result_rows(all_results, "primary_gate/positive_15/")
    positive_by_cell = {
        (
            row.config.followup_unavailability,
            row.config.block_icc,
        ): row
        for row in positives
    }
    alias_exact = all(
        alias.rates
        == positive_by_cell[
            (alias.config.followup_unavailability, alias.config.block_icc)
        ].rates
        for alias in aliases
    )

    resources = _resource_plans()
    stress = {
        "snapshot_drift": simulate_snapshot_drift(master_seed=MASTER_SEED).to_dict(),
        "post_treatment_history": simulate_post_treatment_history_divergence(
            master_seed=MASTER_SEED
        ).to_dict(),
        "latent_binary_invariance_limits": [
            binary_invariance_limit(level, 0.05).to_dict()
            for level in SUPPORTED_UNAVAILABILITY
        ],
    }
    binary_sensitivity_sources = {
        "positive_15": _declared_worst_sensitivity_cell(positives),
        "null": _declared_worst_sensitivity_cell(
            _result_rows(all_results, "primary_gate/null/")
        ),
        "availability_only": _declared_worst_sensitivity_cell(
            _result_rows(all_results, "primary_gate/availability_only/")
        ),
        "fine_stratum_heterogeneity": _declared_worst_sensitivity_cell(
            _result_rows(
                all_results, "primary_gate/fine_stratum_heterogeneity/"
            )
        ),
        "positive_1055": _declared_worst_sensitivity_cell(
            _result_rows(all_results, "diagnostic/positive_1055/")
        ),
        "negative_15": _declared_worst_sensitivity_cell(
            _result_rows(all_results, "diagnostic/negative_15/")
        ),
    }
    binary_sensitivity = {
        scenario: _binary_sensitivity_record(source)
        for scenario, source in binary_sensitivity_sources.items()
    }
    positive_frontier = _frontier_rows(
        all_results, "positive_frontier/", "positive_all_cells"
    )
    selected_positive = _declared_worst_sensitivity_cell(positives)
    positive_frontier.append(
        {
            "blocks_per_macro_cell": POSITIVE_SELECTED_B,
            "estimate": selected_positive.rates["positive_all_cells"].estimate,
            "wilson_lower": selected_positive.rates[
                "positive_all_cells"
            ].interval_lower,
            "wilson_upper": selected_positive.rates[
                "positive_all_cells"
            ].interval_upper,
            "outer_replicates": selected_positive.config.outer_replicates,
        }
    )
    positive_frontier.sort(key=lambda row: int(row["blocks_per_macro_cell"]))

    mid_frontier = _frontier_rows(
        all_results, "mid_frontier/", "positive_all_cells"
    )
    mid_grid = _result_rows(all_results, "diagnostic/positive_1055/")
    selected_mid = _declared_worst_sensitivity_cell(mid_grid)
    supplemental_power_cells_clear = all(
        row.config.outer_replicates >= 10_000
        and row.rates["positive_all_cells"].interval_lower >= 0.90
        for row in mid_grid
    )
    mid_frontier.append(
        {
            "blocks_per_macro_cell": MID_EFFECT_SELECTED_B,
            "estimate": selected_mid.rates["positive_all_cells"].estimate,
            "wilson_lower": selected_mid.rates["positive_all_cells"].interval_lower,
            "wilson_upper": selected_mid.rates["positive_all_cells"].interval_upper,
            "outer_replicates": selected_mid.config.outer_replicates,
        }
    )
    mid_frontier.sort(key=lambda row: int(row["blocks_per_macro_cell"]))

    equivalence_frontier = _frontier_rows(
        all_results, "equivalence_frontier/", "equivalence_all_cells"
    )
    maximum_equivalence = _declared_worst_sensitivity_cell(
        _result_rows(all_results, "equivalence_maximum/null/"),
    )
    equivalence_frontier.append(
        {
            "blocks_per_macro_cell": MAXIMUM_EQUIVALENCE_B,
            "estimate": maximum_equivalence.rates["equivalence_all_cells"].estimate,
            "wilson_lower": maximum_equivalence.rates[
                "equivalence_all_cells"
            ].interval_lower,
            "wilson_upper": maximum_equivalence.rates[
                "equivalence_all_cells"
            ].interval_upper,
            "outer_replicates": maximum_equivalence.config.outer_replicates,
        }
    )
    equivalence_frontier.sort(key=lambda row: int(row["blocks_per_macro_cell"]))

    overall_verdict = _overall_verdict(size_certification)
    result = {
        "schema_version": "binding-test-redesigned-zero-call-gate-v1",
        "generated_date": str(date.today()),
        "master_seed": MASTER_SEED,
        "overall_verdict": overall_verdict,
        "external_action_status": "NO_PROVIDER_CALL_AUTHORIZED",
        "provider_calls_made": 0,
        "external_spend": 0,
        "scope": (
            "local deterministic construction and seeded synthetic numerical "
            "certification only"
        ),
        "scientific_source_integrity": {
            "startup_snapshot_before_scientific_imports": scientific_source_snapshot,
            "required_prepublication_check": (
                "the identical snapshot is recomputed after tests, all simulation, "
                "mandatory replay, and temporary artifact rendering but before "
                "atomic publication"
            ),
            "unchanged_through_prepublication_check": True,
        },
        "phase_firewall": _phase_firewall_metadata(),
        "reference_panel": {
            "snapshot_slots": REFERENCE_SNAPSHOTS,
            "snapshot_status": "placeholders; exact provider snapshot IDs not frozen",
            "target_families": (
                "work_score_allocation",
                "tool_budget_allocation",
            ),
            "macro_cells": 4,
            "fine_strata_per_macro_cell": 24,
        },
        "test_suite": tests,
        "confirmatory_size_certification": size_certification.to_dict(),
        "selected_sizes": _selected_size_metadata(
            size_certification,
            supplemental_power_cells_clear=supplemental_power_cells_clear,
        ),
        "unsupported_frozen_candidates": {
            "blocks_per_macro_cell": (24, 48, 72),
            "reason": (
                "fewer than the frozen minimum four blocks in each of 24 "
                "fine strata per macro cell"
            ),
        },
        "sample_size_frontiers": {
            "positive_15": positive_frontier,
            "positive_1055": mid_frontier,
            "equivalence_null": equivalence_frontier,
        },
        "mechanism_alias_exact_replay": alias_exact,
        "resource_plans": resources,
        "resource_planning_assumptions": {
            "within_fine_stratum": (
                "independent, stationary Bernoulli baseline-attempt validity and "
                "H/L outcomes within each fine stratum, as required by the "
                "binomial-tail calculation"
            ),
            "across_fine_strata": (
                "no independence required for the reported global lower bound; "
                "per-stratum failure bounds are combined by a union bound"
            ),
            "external_status": (
                "planning assumptions only; must be frozen or replaced before "
                "any external calibration proposal"
            ),
        },
        "stress_tests": stress,
        "latent_binary_sensitivity": {
            "role": (
                "required analytical worst/best-case sensitivity; secondary, "
                "nonblocking, and never a numerical gate"
            ),
            "formula": (
                "[observed Delta_H - yoke U, observed Delta_H + self U]"
            ),
            "declared_worst_sensitivity_examples": binary_sensitivity,
        },
        "certification_cells": {
            label: all_results[label].to_dict() for label in sorted(all_results)
        },
        "claim_ceiling": (
            "observed L/H/U disposition reallocation in the exact tested "
            "snapshot-by-target cells and prospectively supported randomized "
            "population; no latent-choice or mechanism identification"
        ),
        "next_external_blockers": (
            "exact snapshot IDs",
            "immutable prompts/items/variants",
            "transport and parser freeze",
            "request/token/runtime/dollar caps",
            "provider prices and billing semantics",
            "explicit approval for the exact bounded calibration action",
        ),
    }
    objects = {
        "size_certification": size_certification,
        "primary_results": primary_results,
        "all_results": all_results,
    }
    return result, objects


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--workers",
        type=int,
        default=min(4, os.cpu_count() or 1),
        help="parallel local worker threads",
    )
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="run 64-replicate behavior checks without writing final artifacts",
    )
    arguments = parser.parse_args()
    if arguments.workers < 1 or arguments.workers > 8:
        parser.error("--workers must lie in [1, 8]")

    scientific_source_snapshot = _scientific_source_snapshot()
    _load_scientific_dependencies()

    tests = _run_tests()
    print(
        f"tests passed={tests['passed']} count={tests['tests_run']}",
        flush=True,
    )
    if not tests["passed"]:
        print(tests["transcript"], file=sys.stderr)
        return 1

    specs, primary_labels = _build_specs(smoke=arguments.smoke)
    all_results = _execute_specs(specs, workers=arguments.workers)
    result, objects = _build_result(
        tests=tests,
        all_results=all_results,
        primary_labels=primary_labels,
        scientific_source_snapshot=scientific_source_snapshot,
    )

    if arguments.smoke:
        if _scientific_source_snapshot() != scientific_source_snapshot:
            raise RuntimeError(
                "scientific sources changed during the smoke run; results discarded"
            )
        print(
            "smoke complete; numerical gates intentionally replicate-ineligible; "
            "no final artifacts written",
            flush=True,
        )
        return 0

    serialized_result = (
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
    )
    rendered_report = _render_report(result, objects)
    if _scientific_source_snapshot() != scientific_source_snapshot:
        raise RuntimeError(
            "scientific sources changed after simulation/replay; artifacts not written"
        )

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    result_temporary = RESULT_PATH.with_name(RESULT_PATH.name + ".tmp")
    report_temporary = REPORT_PATH.with_name(REPORT_PATH.name + ".tmp")
    try:
        result_temporary.write_text(serialized_result, encoding="utf-8")
        report_temporary.write_text(rendered_report, encoding="utf-8")
        if _scientific_source_snapshot() != scientific_source_snapshot:
            raise RuntimeError(
                "scientific sources changed during rendering; artifacts not published"
            )
        os.replace(result_temporary, RESULT_PATH)
        os.replace(report_temporary, REPORT_PATH)
    finally:
        result_temporary.unlink(missing_ok=True)
        report_temporary.unlink(missing_ok=True)
    if _scientific_source_snapshot() != scientific_source_snapshot:
        raise RuntimeError(
            "scientific sources changed during atomic publication; do not seal"
        )
    print(f"wrote {RESULT_PATH}", flush=True)
    print(f"wrote {REPORT_PATH}", flush=True)
    print(f"verdict={result['overall_verdict']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
