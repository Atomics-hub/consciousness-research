from __future__ import annotations

from pathlib import Path
from dataclasses import replace
import hashlib
import json
import unittest

from binding_test.assignment import (
    HIGH,
    LOW,
    CanonicalBlock,
    Session,
    enumerate_allowed_assignments,
)
from binding_test.items import (
    load_item_bank,
    materialize_assignment,
    render_choice_interface,
    variant_label_mapping,
)
from binding_test.runtime import bind_joint_assignment, encode_runtime_stratum
from binding_test.state_machine import SessionStage, TwoChoiceSession


BANK_PATH = Path(__file__).parents[1] / "item_bank_v0.json"


def _block(
    pair_id: str = "WS01",
    target_family: str = "work_score_allocation",
) -> CanonicalBlock:
    stratum = encode_runtime_stratum(
        model_snapshot="synthetic-snapshot",
        target_family=target_family,
        pair_id=pair_id,
        dose="active",
        variant_id="CB00",
    )
    return CanonicalBlock(
        block_id=f"{pair_id}::canonical-0001",
        stratum=stratum,
        sessions=tuple(
            [Session(f"l-{index}", stratum, LOW) for index in range(4)]
            + [Session(f"h-{index}", stratum, HIGH) for index in range(4)]
        ),
    )


class RuntimeBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bank = load_item_bank(BANK_PATH)

    def _sessions(self, block: CanonicalBlock) -> dict[str, TwoChoiceSession]:
        mapping = variant_label_mapping(self.bank, "CB00")
        baseline_interface = render_choice_interface(
            self.bank,
            pair_id="WS01",
            phase="baseline",
            dose="active",
            variant_id="CB00",
        )
        sessions = {}
        for row in block.sessions:
            session = TwoChoiceSession(
                row.session_id,
                "WS01-B",
                followup_item_id="WS01-F",
                displayed_label_to_canonical=mapping,
            )
            session.present_baseline(baseline_interface)
            session.record_baseline("PLAN:A" if row.baseline_choice == LOW else "PLAN:B")
            sessions[row.session_id] = session
        return sessions

    def test_assignment_materialization_state_and_executor_are_bound(self) -> None:
        block = _block()
        assignment = enumerate_allowed_assignments(block)[251]
        materialized = materialize_assignment(
            self.bank, block, assignment, pair_id="WS01", dose="active"
        )
        sessions = self._sessions(block)
        bound = bind_joint_assignment(self.bank, assignment, materialized, sessions)
        self.assertEqual(len(bound), 8)
        seen_digests = []
        followup_interface = render_choice_interface(
            self.bank,
            pair_id="WS01",
            phase="followup",
            dose="active",
            variant_id="CB00",
        )
        for execution in bound:
            record = execution.execute(
                lambda interface, schedule, guard: seen_digests.append(
                    execution.materialized_row.schedule_digest
                )
                or {
                    "payload_id": interface["payload_id"],
                    "score_cap": schedule["score_cap"],
                    "tool_calls_used": guard.used_calls,
                }
            )
            self.assertEqual(record["payload_id"], "WS01-B")
            self.assertEqual(execution.session.stage, SessionStage.EXECUTED)
            execution.session.present_followup(followup_interface)
            execution.session.record_followup("PLAN:A")
            self.assertEqual(execution.session.stage, SessionStage.COMPLETE)
        self.assertEqual(len(seen_digests), 8)
        self.assertEqual(
            materialized.self_schedule_multiset,
            materialized.yoke_schedule_multiset,
        )

    def test_wrong_session_binding_fails_before_any_assignment(self) -> None:
        block = _block()
        assignment = enumerate_allowed_assignments(block)[0]
        materialized = materialize_assignment(
            self.bank, block, assignment, pair_id="WS01", dose="active"
        )
        sessions = self._sessions(block)
        sessions[block.sessions[0].session_id]._baseline = sessions[  # type: ignore[attr-defined]
            block.sessions[-1].session_id
        ].baseline
        with self.assertRaises(ValueError):
            bind_joint_assignment(self.bank, assignment, materialized, sessions)
        self.assertTrue(all(session.stage is SessionStage.BASELINE_RECORDED for session in sessions.values()))

    def test_opaque_stratum_fails_before_any_assignment(self) -> None:
        block = _block()
        assignment = enumerate_allowed_assignments(block)[3]
        materialized = materialize_assignment(
            self.bank, block, assignment, pair_id="WS01", dose="active"
        )
        sessions = self._sessions(block)
        with self.assertRaises(ValueError):
            bind_joint_assignment(
                self.bank,
                assignment,
                replace(materialized, stratum="opaque"),
                sessions,
            )
        self.assertTrue(
            all(session.stage is SessionStage.BASELINE_RECORDED for session in sessions.values())
        )

        original = materialized.rows[0]
        forged_schedule = json.loads(original.schedule_json)
        forged_schedule["score_cap"] += 1
        forged_json = json.dumps(
            forged_schedule,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )
        forged_digest = hashlib.sha256(forged_json.encode("utf-8")).hexdigest()
        forged_row = replace(
            original,
            schedule_json=forged_json,
            schedule_digest=forged_digest,
        )
        forged_materialized = replace(
            materialized,
            rows=(forged_row, *materialized.rows[1:]),
        )
        fresh_sessions = self._sessions(block)
        with self.assertRaises(ValueError):
            bind_joint_assignment(
                self.bank,
                assignment,
                forged_materialized,
                fresh_sessions,
            )
        self.assertTrue(
            all(
                session.stage is SessionStage.BASELINE_RECORDED
                for session in fresh_sessions.values()
            )
        )

    def test_tool_guard_enforces_cap_and_failed_execution_cannot_retry(self) -> None:
        block = _block("TB04", "tool_budget_allocation")
        assignment = enumerate_allowed_assignments(block)[11]
        materialized = materialize_assignment(
            self.bank, block, assignment, pair_id="TB04", dose="active"
        )
        # Recreate state sessions with the TB04 payload IDs but the same canonical baselines.
        mapping = variant_label_mapping(self.bank, "CB00")
        interface = render_choice_interface(
            self.bank,
            pair_id="TB04",
            phase="baseline",
            dose="active",
            variant_id="CB00",
        )
        sessions = {}
        for row in block.sessions:
            session = TwoChoiceSession(
                row.session_id,
                "TB04-B",
                followup_item_id="TB04-F",
                displayed_label_to_canonical=mapping,
            )
            session.present_baseline(interface)
            session.record_baseline("PLAN:A" if row.baseline_choice == LOW else "PLAN:B")
            sessions[row.session_id] = session
        bound = bind_joint_assignment(self.bank, assignment, materialized, sessions)
        target = next(execution for execution in bound if execution.materialized_row.received_schedule == LOW)

        def exceed(_interface, schedule, guard):
            tool = schedule["tool_affordance"]["enabled_tools"][0]
            for _ in range(schedule["tool_affordance"]["max_calls"] + 1):
                guard.authorize(tool)
            return {"tool_calls_used": guard.used_calls}

        with self.assertRaises(PermissionError):
            target.execute(exceed)
        self.assertEqual(target.session.stage, SessionStage.EXECUTION_FAILED)
        with self.assertRaises(RuntimeError):
            target.execute(lambda *_args: {})


if __name__ == "__main__":
    unittest.main()
