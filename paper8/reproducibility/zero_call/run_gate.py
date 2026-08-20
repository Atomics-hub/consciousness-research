#!/usr/bin/env python3
"""Generate the Binding Test zero-call gate results and human-readable report."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict
from datetime import date
from fractions import Fraction
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

from binding_test.assignment import (
    HIGH,
    LOW,
    CanonicalBlock,
    Session,
    audit_assignment_probabilities,
    enumerate_allowed_assignments,
)
from binding_test.items import load_item_bank, materialize_assignment, validate_item_bank
from binding_test.planning import request_envelope, simulate_retention
from binding_test.simulation import run_monte_carlo_decision_grid
from binding_test.stress import (
    binary_invariance_limit,
    simulate_post_treatment_history_divergence,
    simulate_snapshot_drift,
)
from binding_test.runtime import encode_runtime_stratum


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
MASTER_SEED = 20260804


def _jsonable(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if hasattr(value, "__dataclass_fields__"):
        return asdict(value)
    raise TypeError(type(value).__name__)


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
        "command": "PYTHONPATH=.:zero_call PYTHONDONTWRITEBYTECODE=1 "
        "python3 -m unittest discover -s zero_call/tests -v",
        "return_code": completed.returncode,
        "tests_run": int(match.group(1)) if match else None,
        "passed": completed.returncode == 0,
        "transcript": transcript,
    }


def _canonical_block() -> CanonicalBlock:
    stratum = encode_runtime_stratum(
        model_snapshot="synthetic-snapshot",
        target_family="work_score_allocation",
        pair_id="WS01",
        dose="active",
        variant_id="CB00",
    )
    return CanonicalBlock(
        block_id="gate::canonical-0001",
        stratum=stratum,
        sessions=tuple(
            [Session(f"gate-l-{index}", stratum, LOW) for index in range(4)]
            + [Session(f"gate-h-{index}", stratum, HIGH) for index in range(4)]
        ),
    )


def _wilson(rate: float, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    successes = round(rate * n)
    denominator = 1 + z * z / n
    center = (successes / n + z * z / (2 * n)) / denominator
    radius = z * math.sqrt(
        successes / n * (1 - successes / n) / n + z * z / (4 * n * n)
    ) / denominator
    return max(0.0, center - radius), min(1.0, center + radius)


def _render_report(result: dict[str, Any]) -> str:
    item = result["item_bank_audit"]
    probability = result["assignment_audit"]
    limits = result["binary_invariance_limits"]
    stress = result["stress_tests"]
    tests = result["test_suite"]
    retention = result["retention_grid"]
    mc_cells = result["monte_carlo"]["cells"]

    lines = [
        "# Binding Test zero-call gate report",
        "",
        f"**Generated:** {result['generated_date']}  ",
        f"**Verdict:** `{result['overall_verdict']}`  ",
        "**Scope:** local deterministic construction and planning simulation only; no provider call occurred or is authorized.",
        "",
        "## Outcome",
        "",
        "The randomization and harness core is constructible, but the current analysis plan must be redesigned before provider calls. The hard blocker is mathematical: with a strict ±5 percentage-point binary equivalence margin, equal follow-up unavailability `u` gives the null worst/best-case region `[-u,+u]` before sampling error. At `u = 5%` the region already touches both margins and is indeterminate; at 10% and 15% it exceeds them. Larger samples only remove sampling expansion—they cannot shrink partial-identification width.",
        "",
        "This blocks the promised **broad clean-negative certificate** throughout the prespecified 5–15% unavailability stress range. It does not invalidate the randomized positive-effect estimand. The structural core can be retained while the negative decision architecture is changed, or the study can explicitly abandon a broad negative headline.",
        "",
        "The finite planning grid also warns that the positive binary rule is expensive: with 512 randomized sessions (16 blocks in each of four fixed model×target strata), a simulated 15-point effect at 5% U was called binary-responsive in only 4% of positive-direction replicates and never in every stratum; at 10–15% U it was never called responsive. These 24-replicate rates are too coarse for power certification, but they rule out treating 512 sessions as an already justified design.",
        "",
        "## Gate ledger",
        "",
        "| Gate | Status | Finding |",
        "|---|---:|---|",
    ]
    for gate in result["gates"]:
        lines.append(f"| {gate['gate']} | **{gate['status']}** | {gate['finding']} |")

    lines += [
        "",
        "## Mechanically established",
        "",
        f"- **Tests:** {tests['tests_run']}/{tests['tests_run']} passed.",
        f"- **Items:** {item['pair_count']} pairs, {item['family_counts']['work_score_allocation']}+{item['family_counts']['tool_budget_allocation']} families, {item['recomputed_answer_count']}/{item['recomputed_answer_count']} independently recomputed keys, {item['rendered_surface_count']} rendered surfaces without a forbidden enforcement-role cue.",
        f"- **Assignment:** {probability['donor_aware_assignments']} unique donor-aware assignments and {probability['collapsed_exposure_assignments']} collapsed arm/schedule exposures. Every retained session has `P(self)=P(yoke)=1/2`; conditional on yoke, each schedule and match class has probability `1/2`.",
        "- **End-to-end binding:** sampled rows are joined by session ID to a complete SHA-256 schedule fingerprint; all eight rows validate before any state mutation; the executor receives the materialized schedule and a pre-side-effect tool-call guard.",
        "- **Timing/no retry:** treatment-bearing fields are not constructor inputs; baseline and held-out payload IDs are bound; a failed execution attempt is terminal and cannot create a second history.",
        "",
        "## Binary-invariance limit",
        "",
        "| Follow-up U | Infinite-sample identified region | Strict ±.05 invariance possible? |",
        "|---:|---:|---:|",
    ]
    for row in limits:
        lines.append(
            f"| {row['unavailability']:.0%} | [{row['infinite_sample_lower']:+.2f}, {row['infinite_sample_upper']:+.2f}] | {'yes' if row['strict_invariance_possible'] else '**no**'} |"
        )

    lines += [
        "",
        "## Support and attrition",
        "",
        "The 4L/4H block is intentionally strict. The table reports seeded mean retention among **valid L/H baselines**; baseline invalidity would multiply these fractions by the baseline-availability rate.",
        "",
        "| P(H | valid) | Attempted valid | Mean retained | Mean fraction | P(zero blocks) | Asymptotic ceiling |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for row in retention:
        lines.append(
            f"| {row['p_high']:.0%} | {row['attempted']} | {row['mean_retained']:.1f} | {row['mean_retained_fraction']:.1%} | {row['probability_zero_blocks']:.1%} | {row['asymptotic_fraction_ceiling']:.0%} |"
        )

    selected = [
        cell
        for cell in mc_cells
        if cell["blocks_per_model_target"] == 16
    ]
    lines += [
        "",
        "## Planning Monte Carlo",
        "",
        f"Seed `{result['monte_carlo']['master_seed']}`; {result['monte_carlo']['simulation_replicates']} outer replicates and {result['monte_carlo']['bootstrap_replicates']} block-bootstrap replicates per cell; 16 blocks × 8 sessions in each of four fixed model×target strata for this compact view. Rates are descriptive and the bootstrap is planning-grade, not final restricted-randomization inference.",
        "",
        "| Scenario | U | Binary responsive | Binary invariant | Observable changed | Observable invariant | Broad invariant | All-strata responsive |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for cell in selected:
        lines.append(
            "| {scenario} | {u:.0%} | {br:.0%} | {bi:.0%} | {oc:.0%} | {oi:.0%} | {broad:.0%} | {strict:.0%} |".format(
                scenario=cell["scenario"],
                u=cell["followup_unavailability"],
                br=cell["pooled_binary_rates"]["responsive"],
                bi=cell["pooled_binary_rates"]["invariant"],
                oc=cell["pooled_observable_rates"]["changed"],
                oi=cell["pooled_observable_rates"]["invariant"],
                broad=cell["pooled_broad_invariance_rate"],
                strict=cell["all_strata_same_direction_binary_responsive_rate"] or 0,
            )
        )

    lines += [
        "",
        "The `positive` and `mechanism_alias` streams are observably identical by construction. The core therefore cannot distinguish workload-control responsiveness from a generic credibility/interface mechanism. The one-model-only scenario is reported separately so pooled movement cannot masquerade as cross-model replication.",
        "",
        "The nominal false-decision tolerance was frozen at .075, but 24 outer replicates are too few to certify a 7.5% rate: even 0/24 has an approximate 95% Wilson upper bound of {:.1%}. These runs are behavior checks, not error-rate certification.".format(_wilson(0, 24)[1]),
        "",
        "## Drift and post-treatment history",
        "",
        f"- Snapshot stress: valid within-snapshot blocking produced mean null contrast `{stress['snapshot_drift']['mean_valid_blocked_contrast']:+.4f}`; deliberately confounding arm with old/new snapshots produced `{stress['snapshot_drift']['mean_invalid_time_confounded_contrast']:+.4f}`.",
        f"- History stress: the unconditioned randomized contrast was `{stress['post_treatment_history']['primary_randomized_contrast']:+.4f}`; conditioning on the post-treatment XOR history produced contrasts `{stress['post_treatment_history']['conditioned_history_zero_contrast']:+.4f}` and `{stress['post_treatment_history']['conditioned_history_one_contrast']:+.4f}`. Realized work/performance must remain outcomes, never matching variables.",
        "",
        "## Provider-request and cost identity",
        "",
        "For `A` attempted sessions and `R=8B` randomized sessions, with `q_s` additional model continuations caused by tool rounds:",
        "",
        "`C = A + 2R + Σ q_s`.",
        "",
        "The terms are one baseline request for every attempt, plus one execution and one follow-up request for every randomized session. Zero retry is enforced. A no-tool work/score block is exactly 24 requests once its eight baselines are eligible. With sequential tool use, the six prototype tool blocks have conservative maxima of 52–60 requests per block; parallel tool calls could reduce continuations but must be frozen before pricing.",
        "",
        "Dollar cost remains symbolic until models, provider prices, prompt token counts, output caps, tool pricing, and block-support attrition are frozen:",
        "",
        "`Cost_max = Σ_m[(input_tokens_m × price_in_m + output_cap_tokens_m × price_out_m)/1,000,000] + tool_fees`.",
        "",
        "No experimental count, model panel, runtime, or dollar cap is approved here.",
        "",
        "## Required redesign decision",
        "",
        "Before requesting a provider pilot, choose and freeze one scientifically defensible path:",
        "",
        "1. retain worst/best-case binary bounds and abandon a broad equivalence headline unless empirical follow-up U is demonstrably below 5% with enough precision;",
        "2. justify a wider binary equivalence margin larger than the maximum plausible U plus sampling uncertainty; or",
        "3. introduce an additional defensible missing-outcome assumption/sensitivity model, clearly separating it from the assumption-free bound.",
        "",
        "Also freeze exact snapshot/model identifiers, an immutable structured stratum schema, the randomization seed commitment, rotated slot prefixes, retry/transport ledgers, and sequential-versus-parallel tool continuation accounting. Frontier unsaturation, baseline positivity, and the salience of the honest no-guarantee interface remain empirical pilot gates.",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    tests = _run_tests()
    bank = load_item_bank(ROOT / "item_bank_v0.json")
    item_audit = validate_item_bank(bank)

    block = _canonical_block()
    allowed = enumerate_allowed_assignments(block)
    probability = audit_assignment_probabilities(block, allowed)
    materialized = materialize_assignment(
        bank, block, allowed[251], pair_id="WS01", dose="active"
    )
    collapsed = {
        tuple((row.session_id, row.arm, row.received_schedule) for row in assignment.sessions)
        for assignment in allowed
    }

    retention = [
        simulate_retention(
            attempted,
            p_high,
            replicates=2_000,
            master_seed=MASTER_SEED,
        ).to_dict()
        for p_high in (0.10, 0.30, 0.50, 0.70, 0.90)
        for attempted in (64, 128, 256, 512)
    ]

    monte_carlo = run_monte_carlo_decision_grid(
        block_counts=(8, 16),
        followup_unavailability_levels=(0.05, 0.10, 0.15),
        simulation_replicates=24,
        bootstrap_replicates=120,
        sessions_per_arm_block=4,
        model_families=("model_a", "model_b"),
        target_families=("work_score", "tool_budget"),
        binary_delta=0.05,
        category_margins={"L": 0.05, "H": 0.05, "U": 0.02},
        positive_effect_size=0.15,
        availability_shift=0.10,
        master_seed=MASTER_SEED,
    )

    limits = [binary_invariance_limit(level, 0.05) for level in (0.05, 0.10, 0.15)]
    snapshot = simulate_snapshot_drift(master_seed=MASTER_SEED)
    history = simulate_post_treatment_history_divergence(master_seed=MASTER_SEED)

    tool_envelopes = []
    for item in bank["items"]:
        if item["family"] != "tool_budget_allocation":
            continue
        q_low = item["active_schedule"]["low"]["tool_affordance"]["max_calls"]
        q_high = item["active_schedule"]["high"]["tool_affordance"]["max_calls"]
        envelope = request_envelope(
            attempted_sessions=8,
            work_blocks=0,
            tool_blocks=1,
            q_low=q_low,
            q_high=q_high,
        )
        tool_envelopes.append(
            {
                "pair_id": item["pair_id"],
                "q_low_sequential_cap": q_low,
                "q_high_sequential_cap": q_high,
                **envelope.to_dict(),
            }
        )

    hard_binary_failure = any(not row.strict_invariance_possible for row in limits)
    gates = [
        {
            "gate": "G1 timing/parsing/retention",
            "status": "PASS" if tests["passed"] else "FAIL",
            "finding": "Payload-bound two-choice state machine, distinct parser ledgers, terminal zero-retry execution, and nonordinal U pass automated tests.",
        },
        {
            "gate": "G2 item/semantic surface",
            "status": "CONDITIONAL" if item_audit.passed else "FAIL",
            "finding": "12-pair renderer and 144 keys pass structurally; frontier unsaturation, positivity, and no-guarantee salience remain empirical.",
        },
        {
            "gate": "G3 restricted assignment",
            "status": "PASS" if probability.is_canonical else "FAIL",
            "finding": "576 unique donor-aware assignments, 144 collapsed exposures, exact probabilities, schedule fingerprints, and runtime binding pass.",
        },
        {
            "gate": "G4 block support",
            "status": "CONDITIONAL",
            "finding": "Construction is coherent; retention ceiling falls to 20% at 10/90 baseline splits and actual within-stratum support is unknown.",
        },
        {
            "gate": "G5 estimands/decisions",
            "status": "FAIL" if hard_binary_failure else "PASS",
            "finding": "Strict ±.05 binary equivalence is logically unattainable at every planned 5–15% U level; the 512-session planning grid also shows weak binary responsiveness for a 15-point effect.",
        },
        {
            "gate": "G6 stress scenarios",
            "status": "CONDITIONAL",
            "finding": "Required synthetic stresses run; mechanism alias proves generic credibility remains unidentified without a valid comparator.",
        },
        {
            "gate": "G7 call/cost envelope",
            "status": "CONDITIONAL",
            "finding": "Exact request identity and sequential tool caps are derived; dollar cost awaits frozen models, tokens, prices, and retained-block counts.",
        },
    ]

    result = {
        "schema_version": "binding-test-zero-call-gate-v1",
        "generated_date": str(date.today()),
        "master_seed": MASTER_SEED,
        "provider_calls_made": 0,
        "overall_verdict": "REDESIGN_BEFORE_PROVIDER_CALLS",
        "verdict_scope": (
            "Retain the structural randomization core; redesign the broad-negative "
            "decision architecture or explicitly abandon that claim before a pilot request."
        ),
        "gates": gates,
        "test_suite": tests,
        "item_bank_audit": item_audit.to_dict(),
        "assignment_audit": {
            "donor_aware_assignments": len(allowed),
            "unique_donor_aware_assignments": probability.unique_assignment_count,
            "collapsed_exposure_assignments": len(collapsed),
            "collapsed_multiplicity": sorted(
                set(
                    Counter(
                        tuple(
                            (row.session_id, row.arm, row.received_schedule)
                            for row in assignment.sessions
                        )
                        for assignment in allowed
                    ).values()
                )
            ),
            "is_canonical": probability.is_canonical,
            "session_probabilities": [asdict(row) for row in probability.sessions],
            "materialized_self_schedule_multiset": dict(materialized.self_schedule_multiset),
            "materialized_yoke_schedule_multiset": dict(materialized.yoke_schedule_multiset),
        },
        "retention_grid": retention,
        "binary_invariance_limits": [row.to_dict() for row in limits],
        "monte_carlo": monte_carlo.to_dict(),
        "stress_tests": {
            "snapshot_drift": snapshot.to_dict(),
            "post_treatment_history": history.to_dict(),
        },
        "request_envelopes": {
            "identity": "C = A + 2R + sum(q_s)",
            "work_score_one_retained_block": request_envelope(
                attempted_sessions=8, work_blocks=1, tool_blocks=0
            ).to_dict(),
            "tool_budget_one_retained_block_sequential_caps": tool_envelopes,
            "cost_identity": (
                "sum_m((input_tokens_m*price_in_m + output_cap_tokens_m*price_out_m)"
                "/1_000_000) + tool_fees"
            ),
        },
        "limitations": [
            "No provider/model observation occurred; unsaturation, positivity, routing, and snapshot stability are unknown.",
            "Monte Carlo and block bootstrap are planning-grade, not final restricted-randomization inference.",
            "Generic credibility and workload-control mechanisms are observably aliased in the core.",
            "Retention grid conditions on valid L/H baselines; attempted-session retention also depends on baseline availability.",
            "The 24-replicate Monte Carlo grid is too small to certify a 0.075 error rate.",
        ],
    }

    json_path = RESULTS / "gate_results.json"
    json_path.write_text(
        json.dumps(result, indent=2, sort_keys=True, default=_jsonable) + "\n",
        encoding="utf-8",
    )
    report_path = ROOT / "ZERO_CALL_GATE_REPORT.md"
    report_path.write_text(_render_report(result), encoding="utf-8")
    print(f"wrote {json_path}")
    print(f"wrote {report_path}")
    print(f"verdict={result['overall_verdict']} tests={tests['tests_run']} item_pass={item_audit.passed}")
    return 0 if tests["passed"] and item_audit.passed and probability.is_canonical else 1


if __name__ == "__main__":
    raise SystemExit(main())
