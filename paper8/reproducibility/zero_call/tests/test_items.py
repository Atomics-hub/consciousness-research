from __future__ import annotations

from collections import Counter
from dataclasses import replace
from pathlib import Path
import unittest

from binding_test.assignment import (
    HIGH,
    LOW,
    CanonicalBlock,
    Session,
    enumerate_allowed_assignments,
)
from binding_test.items import (
    ROLE_CUE,
    load_item_bank,
    materialize_assignment,
    render_choice_interface,
    render_execution_interface,
    validate_item_bank,
    variant_label_mapping,
)


BANK_PATH = Path(__file__).parents[1] / "item_bank_v0.json"


class ItemBankTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bank = load_item_bank(BANK_PATH)

    def test_executable_structural_audit_recomputes_all_answers(self) -> None:
        audit = validate_item_bank(self.bank)
        self.assertTrue(audit.passed, "\n".join(audit.errors))
        self.assertEqual(audit.pair_count, 12)
        self.assertEqual(audit.family_counts, {
            "work_score_allocation": 6,
            "tool_budget_allocation": 6,
        })
        self.assertEqual(audit.payload_count, 24)
        self.assertEqual(audit.slot_count, 144)
        self.assertEqual(audit.recomputed_answer_count, 144)
        self.assertEqual(audit.rendered_surface_count, 240)
        self.assertTrue(audit.warnings)

    def test_rendered_surfaces_have_no_enforcement_role_input_or_cue(self) -> None:
        choice = render_choice_interface(
            self.bank,
            pair_id="WS01",
            phase="baseline",
            dose="active",
            variant_id="CB10",
        )
        execution = render_execution_interface(
            self.bank,
            pair_id="WS01",
            dose="active",
            canonical="high",
        )
        self.assertIsNone(ROLE_CUE.search(choice["text"]))
        self.assertIsNone(ROLE_CUE.search(str(execution)))
        self.assertEqual(
            variant_label_mapping(self.bank, "CB10"),
            {"A": "high", "B": "low"},
        )
        self.assertEqual(len(execution["enabled_slots"]), 6)

    def test_complete_donor_schedule_fingerprints_match_across_arms(self) -> None:
        block = CanonicalBlock(
            block_id="item::canonical-0001",
            stratum="item",
            sessions=tuple(
                [Session(f"l-{index}", "item", LOW) for index in range(4)]
                + [Session(f"h-{index}", "item", HIGH) for index in range(4)]
            ),
        )
        assignment = enumerate_allowed_assignments(block)[137]
        materialized = materialize_assignment(
            self.bank,
            block,
            assignment,
            pair_id="TB03",
            dose="active",
        )
        self.assertEqual(
            materialized.self_schedule_multiset,
            materialized.yoke_schedule_multiset,
        )
        self.assertEqual(sum(materialized.self_schedule_multiset.values()), 4)
        self.assertEqual(
            Counter(row.received_schedule for row in materialized.rows if row.arm == "self"),
            Counter({LOW: 2, HIGH: 2}),
        )
        for row in materialized.rows:
            self.assertEqual(len(row.schedule_digest), 64)

    def test_materializer_rejects_valid_shape_with_wrong_allowed_set_index(self) -> None:
        block = CanonicalBlock(
            block_id="forged::canonical-0001",
            stratum="forged",
            sessions=tuple(
                [Session(f"l-{index}", "forged", LOW) for index in range(4)]
                + [Session(f"h-{index}", "forged", HIGH) for index in range(4)]
            ),
        )
        allowed = enumerate_allowed_assignments(block)
        forged = replace(allowed[0], allowed_set_index=1)
        with self.assertRaises(ValueError):
            materialize_assignment(
                self.bank,
                block,
                forged,
                pair_id="WS01",
                dose="active",
            )


if __name__ == "__main__":
    unittest.main()
