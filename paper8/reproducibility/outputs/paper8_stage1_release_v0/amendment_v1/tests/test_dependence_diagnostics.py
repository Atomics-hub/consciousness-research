from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest


AMENDMENT_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
for value in (AMENDMENT_ROOT, REPOSITORY_ROOT / "zero_call"):
    if str(value) not in sys.path:
        sys.path.insert(0, str(value))

from dependence_diagnostics import (  # noqa: E402
    CANONICAL_ALLOWED_ASSIGNMENT_COUNT,
    CLAIM_CEILING,
    DEPENDENCE_PROFILES,
    FORMATION_CAPS,
    FORMATION_PROFILES,
    GATE_EFFECT,
    OUTCOME_PROFILES,
    SCHEMA_VERSION,
    STATUS,
    analytic_terminal_truth,
    assignment_table,
    block_formation_sentinel,
    failure_probability_bounds,
    formation_probability_bounds,
    map_terminal_disposition,
    outcome_probability_bounds,
    run_diagnostics,
    run_formation_cell,
    serialize_result,
    simulate_one_terminal_block,
    validate_result,
)
from protocol_authority import SOURCE_SUBTYPES  # noqa: E402


class AssignmentAndTerminalTests(unittest.TestCase):
    def test_actual_allowed_set_and_donor_pairs(self) -> None:
        table = assignment_table()
        self.assertEqual(table.arm_self.shape, (576, 8))
        self.assertEqual(CANONICAL_ALLOWED_ASSIGNMENT_COUNT, 576)
        self.assertEqual(len(table.digest), 64)
        for assignment_index in (0, 17, 233, 575):
            arms = table.arm_self[assignment_index]
            schedules = table.schedule_high[assignment_index]
            pairs = table.pair_slot[assignment_index]
            self.assertEqual(int(arms.sum()), 4)
            self.assertEqual(int((schedules & arms).sum()), 2)
            self.assertEqual(int((schedules & ~arms).sum()), 2)
            self.assertEqual(sorted(pairs.tolist()), [0, 0, 1, 1, 2, 2, 3, 3])
            for slot in range(4):
                members = pairs == slot
                self.assertEqual(int((members & arms).sum()), 1)
                self.assertEqual(int((members & ~arms).sum()), 1)

    def test_terminal_mapping_is_composite_u_and_source_preserving(self) -> None:
        self.assertEqual(
            map_terminal_disposition(
                failed=True,
                followup_category="H",
                failure_type_draw=0.25,
            ),
            ("U", "execution_failure", "provider_error"),
        )
        self.assertEqual(
            map_terminal_disposition(
                failed=True,
                followup_category="L",
                failure_type_draw=0.90,
            ),
            ("U", "execution_failure", "transport_error"),
        )
        self.assertEqual(
            map_terminal_disposition(
                failed=False,
                followup_category="U",
                failure_type_draw=0.10,
            ),
            ("U", "followup_unavailable", "invalid_response"),
        )
        self.assertEqual(
            map_terminal_disposition(
                failed=False,
                followup_category="H",
                failure_type_draw=0.10,
            ),
            ("H", "followup_choice", "none"),
        )

    def test_one_block_always_has_exactly_eight_terminal_rows(self) -> None:
        rows = simulate_one_terminal_block(
            assignment_index=233,
            scenario="positive_15",
            dependence_profile="joint",
            failure_profile="differential",
        )
        self.assertEqual(len(rows), 8)
        self.assertEqual(len({row.session_id for row in rows}), 8)
        self.assertEqual(sum(row.arm == "self" for row in rows), 4)
        self.assertEqual(sum(row.arm == "yoke" for row in rows), 4)
        donors = {row.session_id for row in rows if row.arm == "self"}
        self.assertEqual(
            {row.donor_session_id for row in rows if row.arm == "yoke"},
            donors,
        )
        for row in rows:
            if row.disposition_source == "execution_failure":
                self.assertEqual(row.category, "U")
                self.assertIn(row.failure_subtype, SOURCE_SUBTYPES["execution_failure"])
            else:
                self.assertIn(row.failure_subtype, SOURCE_SUBTYPES[row.disposition_source])

    def test_actual_block_former_sentinel_accounts_for_every_attempt(self) -> None:
        sentinel = block_formation_sentinel()
        self.assertEqual(sentinel["blocks"], 1)
        self.assertEqual(sentinel["retained_sessions"], 8)
        self.assertEqual(sentinel["attrited_sessions"], 2)
        self.assertTrue(sentinel["accounts_for_all_sessions"])
        self.assertEqual(
            sentinel["attrition_reasons"],
            ["invalid_baseline", "unmatched_block_support"],
        )


class DgpTruthTests(unittest.TestCase):
    def assertVectorAlmostEqual(self, actual, expected) -> None:
        self.assertEqual(len(actual), len(expected))
        for left, right in zip(actual, expected, strict=True):
            self.assertAlmostEqual(left, right, places=12)

    def test_analytic_truths_are_assignment_policy_terminal_contrasts(self) -> None:
        self.assertVectorAlmostEqual(
            analytic_terminal_truth("positive_15", "symmetric"),
            (-0.1425, 0.1425, 0.0),
        )
        self.assertVectorAlmostEqual(
            analytic_terminal_truth("positive_15", "differential"),
            (-0.15075, 0.12825, 0.0225),
        )
        self.assertVectorAlmostEqual(
            analytic_terminal_truth("null", "differential"),
            (-0.01125, -0.01125, 0.0225),
        )
        self.assertVectorAlmostEqual(
            analytic_terminal_truth("positive_boundary", "symmetric"),
            (-0.0475, 0.0475, 0.0),
        )

    def test_all_declared_probability_stresses_are_feasible(self) -> None:
        for _label, scenario, dependence, failure in OUTCOME_PROFILES:
            outcome = outcome_probability_bounds(scenario, dependence)
            failures = failure_probability_bounds(failure, dependence)
            self.assertGreaterEqual(outcome["minimum"], 0.0)
            self.assertLessEqual(outcome["maximum"], 1.0)
            self.assertGreaterEqual(failures["minimum"], 0.0)
            self.assertLessEqual(failures["maximum"], 1.0)
        for profile in FORMATION_PROFILES:
            for high_probability in FORMATION_CAPS:
                bounds = formation_probability_bounds(high_probability, profile)
                for minimum, maximum in bounds.values():
                    self.assertGreaterEqual(minimum, 0.0)
                    self.assertLessEqual(maximum, 1.0)


class DeterminismAndSchemaTests(unittest.TestCase):
    def test_formation_cell_is_chunk_invariant(self) -> None:
        first = run_formation_cell(
            "provider_batch", 0.10, 4, chunk_size=1
        )
        second = run_formation_cell(
            "provider_batch", 0.10, 4, chunk_size=3
        )
        self.assertEqual(first, second)

    def test_complete_small_result_is_chunk_invariant_and_closed(self) -> None:
        first = run_diagnostics(
            outcome_replicates=2,
            formation_replicates=2,
            chunk_size=1,
        )
        second = run_diagnostics(
            outcome_replicates=2,
            formation_replicates=2,
            chunk_size=3,
        )
        self.assertEqual(first, second)
        validate_result(first)
        self.assertEqual(first["schema_version"], SCHEMA_VERSION)
        self.assertEqual(first["status"], STATUS)
        self.assertEqual(first["gate_effect"], GATE_EFFECT)
        self.assertFalse(first["numerical_gate_eligible"])
        self.assertEqual(first["claim_ceiling"], CLAIM_CEILING)
        self.assertEqual(len(first["formation_diagnostics"]), 6)
        self.assertEqual(len(first["outcome_diagnostics"]), 8)
        self.assertEqual(
            {row["label"] for row in first["outcome_diagnostics"]},
            {row[0] for row in OUTCOME_PROFILES},
        )
        serialized = serialize_result(first)
        self.assertEqual(serialized, serialize_result(second))
        self.assertNotIn("session_id", serialized)
        self.assertNotIn("raw_response", serialized)
        json.loads(serialized)

    def test_closed_schema_rejects_extra_or_gating_mutation(self) -> None:
        result = run_diagnostics(
            outcome_replicates=2,
            formation_replicates=1,
            chunk_size=2,
        )
        extra = deepcopy(result)
        extra["unexpected"] = True
        with self.assertRaises(ValueError):
            validate_result(extra)
        gating = deepcopy(result)
        gating["numerical_gate_eligible"] = True
        with self.assertRaises(ValueError):
            validate_result(gating)
        tampered = deepcopy(result)
        tampered["outcome_diagnostics"][0]["decision_rates"][
            "positive_all_cells"
        ]["successes"] += 1
        with self.assertRaises(ValueError):
            validate_result(tampered)

    def test_profile_declarations_are_exact(self) -> None:
        self.assertEqual(
            set(DEPENDENCE_PROFILES),
            {"independent", "donor_only", "shared_shocks", "joint"},
        )
        self.assertEqual(len(OUTCOME_PROFILES), 8)
        self.assertEqual(set(FORMATION_PROFILES), {"independent", "provider_batch"})


if __name__ == "__main__":
    unittest.main()
