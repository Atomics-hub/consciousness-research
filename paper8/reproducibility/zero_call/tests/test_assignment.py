from __future__ import annotations

from collections import Counter
from fractions import Fraction
import unittest

from zero_call.binding_test.assignment import (
    CANONICAL_ALLOWED_ASSIGNMENT_COUNT,
    HIGH,
    LOW,
    SELF,
    YOKE,
    CanonicalBlock,
    Session,
    audit_assignment_probabilities,
    enumerate_allowed_assignments,
    form_canonical_blocks,
    sample_assignment,
    validate_joint_assignment,
)


def canonical_block(block_id: str = "target-a::canonical-0001") -> CanonicalBlock:
    sessions = tuple(
        [Session(f"low-{index}", "target-a", LOW) for index in range(1, 5)]
        + [Session(f"high-{index}", "target-a", HIGH) for index in range(1, 5)]
    )
    return CanonicalBlock(block_id=block_id, stratum="target-a", sessions=sessions)


class AllowedAssignmentTests(unittest.TestCase):
    def test_complete_allowed_set_has_576_unique_donor_aware_assignments(self) -> None:
        block = canonical_block()
        allowed = enumerate_allowed_assignments(block)

        self.assertEqual(len(allowed), CANONICAL_ALLOWED_ASSIGNMENT_COUNT)
        signatures = {
            tuple(
                (row.session_id, row.arm, row.received_schedule, row.donor_session_id)
                for row in assignment.sessions
            )
            for assignment in allowed
        }
        self.assertEqual(len(signatures), CANONICAL_ALLOWED_ASSIGNMENT_COUNT)
        self.assertEqual(
            [assignment.allowed_set_index for assignment in allowed],
            list(range(CANONICAL_ALLOWED_ASSIGNMENT_COUNT)),
        )
        collapsed = Counter(
            tuple(
                (row.session_id, row.arm, row.received_schedule)
                for row in assignment.sessions
            )
            for assignment in allowed
        )
        self.assertEqual(len(collapsed), 144)
        self.assertEqual(set(collapsed.values()), {4})

    def test_every_enumerated_assignment_satisfies_all_constraints(self) -> None:
        block = canonical_block()
        for assignment in enumerate_allowed_assignments(block):
            validate_joint_assignment(block, assignment)
            self_rows = [row for row in assignment.sessions if row.arm == SELF]
            yoke_rows = [row for row in assignment.sessions if row.arm == YOKE]

            self.assertEqual(len(self_rows), 4)
            self.assertEqual(len(yoke_rows), 4)
            self.assertEqual([row.baseline_choice for row in self_rows].count(LOW), 2)
            self.assertEqual([row.baseline_choice for row in self_rows].count(HIGH), 2)
            self.assertCountEqual(
                [row.donor_session_id for row in yoke_rows],
                [row.session_id for row in self_rows],
            )
            self.assertCountEqual(
                [row.received_schedule for row in yoke_rows],
                [row.received_schedule for row in self_rows],
            )
            self.assertEqual(sum(row.is_match for row in yoke_rows), 2)
            self.assertEqual(sum(not row.is_match for row in yoke_rows), 2)

            cells = {
                (recipient_choice, schedule): sum(
                    row.baseline_choice == recipient_choice and row.received_schedule == schedule
                    for row in yoke_rows
                )
                for recipient_choice in (LOW, HIGH)
                for schedule in (LOW, HIGH)
            }
            self.assertEqual(set(cells.values()), {1})

    def test_exact_assignment_probability_audit(self) -> None:
        audit = audit_assignment_probabilities(canonical_block())
        audit.assert_canonical()

        self.assertTrue(audit.is_canonical)
        self.assertEqual(audit.total_assignments, 576)
        self.assertEqual(audit.unique_assignment_count, 576)
        self.assertEqual(len(audit.sessions), 8)
        for session in audit.sessions:
            self.assertEqual(session.p_self, Fraction(1, 2))
            self.assertEqual(session.p_yoke, Fraction(1, 2))
            self.assertEqual(session.p_receive_high_given_yoke, Fraction(1, 2))
            self.assertEqual(session.p_receive_low_given_yoke, Fraction(1, 2))
            self.assertEqual(session.p_match_given_yoke, Fraction(1, 2))
            self.assertEqual(session.p_mismatch_given_yoke, Fraction(1, 2))
            self.assertTrue(session.has_both_yoke_exposure_classes)

    def test_probability_audit_rejects_repeated_allowed_members(self) -> None:
        block = canonical_block()
        allowed = enumerate_allowed_assignments(block)
        representative_by_exposure = {}
        for assignment in allowed:
            exposure = tuple(
                (row.session_id, row.arm, row.received_schedule)
                for row in assignment.sessions
            )
            representative_by_exposure.setdefault(exposure, assignment)
        representatives = tuple(representative_by_exposure.values())
        self.assertEqual(len(representatives), 144)
        repeated = tuple(
            assignment
            for assignment in representatives
            for _ in range(4)
        )
        audit = audit_assignment_probabilities(block, repeated)
        self.assertEqual(audit.total_assignments, 576)
        self.assertEqual(audit.unique_assignment_count, 144)
        self.assertFalse(audit.is_canonical)

    def test_each_session_has_both_match_and_mismatch_yoke_support(self) -> None:
        block = canonical_block()
        allowed = enumerate_allowed_assignments(block)
        for session in block.sessions:
            yoke_rows = [
                assignment.for_session(session.session_id)
                for assignment in allowed
                if assignment.for_session(session.session_id).arm == YOKE
            ]
            self.assertEqual({row.received_schedule for row in yoke_rows}, {LOW, HIGH})
            self.assertEqual({row.is_match for row in yoke_rows}, {False, True})

    def test_seeded_sampling_is_repeatable_and_returns_allowed_member(self) -> None:
        block = canonical_block()
        allowed = enumerate_allowed_assignments(block)
        first = sample_assignment(block, seed="frozen-seed")
        second = sample_assignment(block, seed="frozen-seed")

        self.assertEqual(first, second)
        self.assertEqual(first, allowed[first.allowed_set_index])
        validate_joint_assignment(block, first)

        sampled_indices = {sample_assignment(block, seed=seed).allowed_set_index for seed in range(20)}
        self.assertGreater(len(sampled_indices), 1)


class BlockFormationTests(unittest.TestCase):
    def test_deterministic_formation_and_transparent_attrition(self) -> None:
        sessions = (
            [Session(f"alpha-l-{index}", "alpha", LOW) for index in range(1, 7)]
            + [Session(f"alpha-h-{index}", "alpha", HIGH) for index in range(1, 6)]
            + [Session("alpha-invalid", "alpha", "U")]
            + [Session(f"beta-l-{index}", "beta", LOW) for index in range(1, 9)]
            + [Session(f"beta-h-{index}", "beta", HIGH) for index in range(1, 9)]
        )

        forward = form_canonical_blocks(sessions)
        reverse = form_canonical_blocks(reversed(sessions))

        self.assertEqual(forward, reverse)
        self.assertTrue(forward.accounts_for_all_sessions)
        self.assertEqual(forward.retained_session_count, 24)
        self.assertEqual(forward.attrited_session_count, 4)
        self.assertEqual(
            [block.block_id for block in forward.blocks],
            [
                "alpha::canonical-0001",
                "beta::canonical-0001",
                "beta::canonical-0002",
            ],
        )
        self.assertEqual(
            {record.session.session_id for record in forward.attrition},
            {"alpha-l-5", "alpha-l-6", "alpha-h-5", "alpha-invalid"},
        )
        reason_by_id = {
            record.session.session_id: record.reason for record in forward.attrition
        }
        self.assertEqual(reason_by_id["alpha-invalid"], "invalid_baseline")
        self.assertEqual(reason_by_id["alpha-l-5"], "unmatched_block_support")
        self.assertEqual(reason_by_id["alpha-l-6"], "unmatched_block_support")
        self.assertEqual(reason_by_id["alpha-h-5"], "unmatched_block_support")

    def test_block_formation_never_borrows_support_across_strata(self) -> None:
        sessions = [Session(f"only-l-{index}", "low-only", LOW) for index in range(4)]
        sessions += [Session(f"only-h-{index}", "high-only", HIGH) for index in range(4)]

        formation = form_canonical_blocks(sessions)
        self.assertEqual(formation.blocks, ())
        self.assertEqual(len(formation.attrition), 8)
        self.assertTrue(all(row.reason == "unmatched_block_support" for row in formation.attrition))

    def test_duplicate_session_ids_are_rejected(self) -> None:
        sessions = [Session("duplicate", "a", LOW), Session("duplicate", "a", HIGH)]
        with self.assertRaisesRegex(ValueError, "globally unique"):
            form_canonical_blocks(sessions)

    def test_malformed_canonical_block_is_rejected(self) -> None:
        sessions = tuple(
            [Session(f"l-{index}", "a", LOW) for index in range(5)]
            + [Session(f"h-{index}", "a", HIGH) for index in range(3)]
        )
        with self.assertRaisesRegex(ValueError, "exactly 4 L and 4 H"):
            CanonicalBlock(block_id="bad", stratum="a", sessions=sessions)


if __name__ == "__main__":
    unittest.main()
