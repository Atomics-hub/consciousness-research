from __future__ import annotations

import unittest

from binding_test.parsers import ChoiceCategory, parse_choice, parse_display_choice
from binding_test.state_machine import EnforcementArm, SessionStage, TwoChoiceSession


class ParserTests(unittest.TestCase):
    def test_strict_and_semantic_ledgers_are_distinct(self) -> None:
        strict = parse_choice('{"choice":"H"}')
        token = parse_choice("L")
        fenced = parse_choice('```json\n{"choice":"H"}\n```')
        self.assertTrue(strict.strict_valid and strict.semantic_valid)
        self.assertFalse(token.strict_valid)
        self.assertTrue(token.semantic_valid)
        self.assertFalse(fenced.strict_valid)
        self.assertTrue(fenced.semantic_valid)

    def test_strict_parser_rejects_duplicate_or_normalized_values(self) -> None:
        duplicate = parse_choice('{"choice":"L","choice":"H"}')
        fenced_duplicate = parse_choice(
            '```json\n{"choice":"L","choice":"H"}\n```'
        )
        normalized = parse_choice('{"choice":" h "}')
        self.assertFalse(duplicate.strict_valid)
        self.assertEqual(duplicate.category, ChoiceCategory.UNAVAILABLE)
        self.assertFalse(fenced_duplicate.semantic_valid)
        self.assertEqual(fenced_duplicate.category, ChoiceCategory.UNAVAILABLE)
        self.assertFalse(normalized.strict_valid)
        self.assertEqual(normalized.category, ChoiceCategory.UNAVAILABLE)

    def test_unavailable_is_never_ordinal(self) -> None:
        for raw in (None, "", "REFUSAL", "I choose H because...", '{"choice":"X"}'):
            parsed = parse_choice(raw)
            self.assertEqual(parsed.category, ChoiceCategory.UNAVAILABLE)
            self.assertFalse(parsed.available)

    def test_counterbalanced_display_parser_recodes_without_prose_recovery(self) -> None:
        mapping = {"A": "high", "B": "low"}
        trimmed = parse_display_choice(
            "  PLAN:A\n", displayed_label_to_canonical=mapping
        )
        self.assertEqual(trimmed.category, ChoiceCategory.HIGH)
        self.assertFalse(trimmed.strict_valid)
        self.assertTrue(trimmed.semantic_valid)
        invalid = parse_display_choice(
            "I choose PLAN:A", displayed_label_to_canonical=mapping
        )
        self.assertEqual(invalid.category, ChoiceCategory.UNAVAILABLE)
        self.assertFalse(invalid.semantic_valid)


class StateMachineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.session = TwoChoiceSession("s1", "item1")
        self.interface = {
            "payload_id": "item1",
            "text": "Choose L or H. The applied schedule is selected after this response."
        }

    def test_assignment_cannot_exist_before_valid_baseline(self) -> None:
        with self.assertRaises(RuntimeError):
            self.session.assign(EnforcementArm.YOKED, ChoiceCategory.HIGH)

    def test_treatment_fields_are_not_constructor_or_property_inputs(self) -> None:
        with self.assertRaises(TypeError):
            TwoChoiceSession("bad", "item", arm=EnforcementArm.YOKED)  # type: ignore[call-arg]
        with self.assertRaises(AttributeError):
            self.session.arm = EnforcementArm.YOKED  # type: ignore[misc]
        before = self.session.audit_record()
        self.assertIsNone(before["arm"])
        self.assertIsNone(before["received_schedule"])
        self.session.present_baseline(self.interface)
        self.session.record_baseline("REFUSAL")
        self.assertEqual(self.session.stage, SessionStage.BASELINE_UNAVAILABLE)
        with self.assertRaises(RuntimeError):
            self.session.assign(EnforcementArm.YOKED, ChoiceCategory.HIGH)

    def test_self_schedule_must_equal_baseline_choice(self) -> None:
        self.session.present_baseline(self.interface)
        self.session.record_baseline('{"choice":"L"}')
        with self.assertRaises(ValueError):
            self.session.assign(EnforcementArm.SELF_CONTINGENT, ChoiceCategory.HIGH)

    def test_complete_two_choice_session_and_hide_role(self) -> None:
        self.session.present_baseline(self.interface)
        self.session.record_baseline('{"choice":"L"}')
        self.session.assign(EnforcementArm.YOKED, ChoiceCategory.HIGH)
        record = self.session.execute(
            lambda item_id, schedule: {
                "item_id": item_id,
                "applied_schedule": schedule.value,
                "completed_units": 6,
                "score": 6,
                "score_cap": 6,
            }
        )
        self.assertEqual(record["applied_schedule"], "H")
        self.assertNotIn("yoked", self.session.visible_text().lower())
        self.session.present_followup(
            {
                "payload_id": "item1::heldout",
                "text": "Choose a schedule for a held-out item.",
            }
        )
        result = self.session.record_followup("H")
        self.assertEqual(result.category, ChoiceCategory.HIGH)
        self.assertEqual(self.session.stage, SessionStage.COMPLETE)

    def test_executor_cannot_emit_role_field(self) -> None:
        self.session.present_baseline(self.interface)
        self.session.record_baseline("H")
        self.session.assign(EnforcementArm.SELF_CONTINGENT, ChoiceCategory.HIGH)
        with self.assertRaises(ValueError):
            self.session.execute(lambda _item, _schedule: {"role": "hidden"})
        self.assertEqual(self.session.stage, SessionStage.EXECUTION_FAILED)
        self.assertTrue(self.session.execution_attempted)
        with self.assertRaises(RuntimeError):
            self.session.execute(lambda _item, _schedule: {"score": 1})

    def test_executor_rejects_nested_or_value_role_leaks(self) -> None:
        self.session.present_baseline(self.interface)
        self.session.record_baseline("H")
        self.session.assign(EnforcementArm.SELF_CONTINGENT, ChoiceCategory.HIGH)
        with self.assertRaises(ValueError):
            self.session.execute(
                lambda _item, _schedule: {"metadata": {"note": "yoked session"}}
            )

    def test_interfaces_reject_role_cues(self) -> None:
        with self.assertRaises(ValueError):
            self.session.present_baseline(
                {"payload_id": "item1", "text": "You are in the treatment arm."}
            )

        clean = TwoChoiceSession("clean", "baseline", followup_item_id="heldout")
        clean.present_baseline(
            {"payload_id": "baseline", "text": "Choose a configuration."}
        )
        clean.record_baseline("H")
        clean.assign(EnforcementArm.SELF_CONTINGENT, ChoiceCategory.HIGH)
        clean.execute(lambda item, schedule: {"item": item, "schedule": schedule.value})
        with self.assertRaises(ValueError):
            clean.present_followup(
                {
                    "payload_id": "heldout",
                    "metadata": {"group": "control group"},
                }
            )

    def test_followup_is_distinct_and_never_passed_to_executor(self) -> None:
        executed: list[str] = []
        session = TwoChoiceSession("heldout", "WS01-B", followup_item_id="WS01-F")
        session.present_baseline(
            {"payload_id": "WS01-B", "text": "Choose L or H."}
        )
        session.record_baseline("L")
        session.assign(EnforcementArm.SELF_CONTINGENT, ChoiceCategory.LOW)
        session.execute(
            lambda item, schedule: executed.append(item) or {"schedule": schedule.value}
        )
        session.present_followup({"payload_id": "WS01-F"})
        session.record_followup("H")
        self.assertEqual(executed, ["WS01-B"])
        self.assertNotIn("WS01-F", executed)
        with self.assertRaises(ValueError):
            TwoChoiceSession("bad-heldout", "same", followup_item_id="same")

    def test_item_bank_display_contract_runs_through_state_machine(self) -> None:
        session = TwoChoiceSession(
            "display",
            "WS01",
            displayed_label_to_canonical={"A": "high", "B": "low"},
        )
        session.present_baseline(
            {"payload_id": "WS01", "text": "Return PLAN:A or PLAN:B."}
        )
        baseline = session.record_baseline("PLAN:A")
        self.assertEqual(baseline.category, ChoiceCategory.HIGH)
        session.assign(EnforcementArm.SELF_CONTINGENT, ChoiceCategory.HIGH)
        session.execute(lambda _item, schedule: {"applied_schedule": schedule.value})
        session.present_followup(
            {
                "payload_id": "WS01::heldout",
                "text": "Return PLAN:A or PLAN:B.",
            }
        )
        followup = session.record_followup("PLAN:B")
        self.assertEqual(followup.category, ChoiceCategory.LOW)
        self.assertNotIn("category", session.visible_text())

    def test_match_surface_is_identical_across_internal_arms(self) -> None:
        def complete(arm: EnforcementArm) -> tuple[object, ...]:
            session = TwoChoiceSession(
                arm.value,
                "WS01",
                displayed_label_to_canonical={"A": "low", "B": "high"},
            )
            session.present_baseline(
                {"payload_id": "WS01", "text": "Return PLAN:B."}
            )
            session.record_baseline("PLAN:B")
            session.assign(arm, ChoiceCategory.HIGH)
            session.execute(
                lambda item, schedule: {
                    "item_id": item,
                    "applied_schedule": schedule.value,
                    "score": 4,
                }
            )
            session.present_followup(
                {"payload_id": "WS01::heldout", "text": "Held-out choice."}
            )
            return session.visible_events

        self.assertEqual(
            complete(EnforcementArm.SELF_CONTINGENT),
            complete(EnforcementArm.YOKED),
        )

    def test_visible_records_are_deep_snapshots(self) -> None:
        interface = {"payload_id": "item1", "nested": {"text": "Choose."}}
        self.session.present_baseline(interface)
        interface["nested"]["text"] = "treatment arm"  # type: ignore[index]
        self.session.record_baseline("L")
        self.session.assign(EnforcementArm.SELF_CONTINGENT, ChoiceCategory.LOW)
        returned = self.session.execute(
            lambda _item, _schedule: {"nested": {"score": 1}}
        )
        returned["nested"]["treatment"] = "leak"  # type: ignore[index]
        visible = self.session.visible_text().lower()
        self.assertNotIn("treatment", visible)
        self.assertIn("choose", visible)

    def test_followup_payload_binding_is_enforced(self) -> None:
        session = TwoChoiceSession("bind", "B", followup_item_id="F")
        session.present_baseline({"payload_id": "B"})
        session.record_baseline("H")
        session.assign(EnforcementArm.SELF_CONTINGENT, ChoiceCategory.HIGH)
        session.execute(lambda _item, _schedule: {"score": 1})
        with self.assertRaises(ValueError):
            session.present_followup({"payload_id": "B"})


if __name__ == "__main__":
    unittest.main()
