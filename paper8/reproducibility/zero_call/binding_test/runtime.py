"""End-to-end binding from a sampled joint assignment to session execution.

The assignment engine and state machine are intentionally separate concerns.
This module is their trust boundary: it validates every row and complete
schedule fingerprint before mutating any session, then supplies the exact
materialized schedule and a pre-call tool-budget guard to the executor.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Callable, Mapping

from .assignment import LOW, SELF, JointAssignment
from .items import (
    MaterializedAssignment,
    MaterializedScheduleRow,
    render_execution_interface,
    schedule_fingerprint,
    variant_label_mapping,
)
from .parsers import ChoiceCategory
from .state_machine import EnforcementArm, SessionStage, TwoChoiceSession


RUNTIME_STRATUM_PREFIX = "binding-v1"


@dataclass(frozen=True, slots=True)
class RuntimeStratum:
    model_snapshot: str
    target_family: str
    pair_id: str
    dose: str
    variant_id: str

    def encode(self) -> str:
        values = (
            RUNTIME_STRATUM_PREFIX,
            self.model_snapshot,
            self.target_family,
            self.pair_id,
            self.dose,
            self.variant_id,
        )
        if any(not value or "|" in value for value in values):
            raise ValueError("runtime stratum values must be nonempty and cannot contain '|'")
        if self.dose not in {"active", "zero_dose"}:
            raise ValueError("runtime stratum dose must be active or zero_dose")
        return "|".join(values)


def parse_runtime_stratum(value: str) -> RuntimeStratum:
    parts = value.split("|")
    if len(parts) != 6 or parts[0] != RUNTIME_STRATUM_PREFIX:
        raise ValueError("runtime stratum must use binding-v1 structured encoding")
    result = RuntimeStratum(*parts[1:])
    if result.encode() != value:
        raise ValueError("runtime stratum is not in canonical form")
    return result


def encode_runtime_stratum(
    *,
    model_snapshot: str,
    target_family: str,
    pair_id: str,
    dose: str,
    variant_id: str,
) -> str:
    return RuntimeStratum(
        model_snapshot=model_snapshot,
        target_family=target_family,
        pair_id=pair_id,
        dose=dose,
        variant_id=variant_id,
    ).encode()


@dataclass(slots=True)
class ToolCallGuard:
    """Authorize tool calls before their side effects occur."""

    enabled_tools: tuple[str, ...]
    max_calls: int
    used_calls: int = 0

    def authorize(self, tool_name: str) -> int:
        if tool_name not in self.enabled_tools:
            raise PermissionError(f"tool {tool_name!r} is not enabled by the schedule")
        if self.used_calls >= self.max_calls:
            raise PermissionError("assigned tool-call cap exhausted")
        self.used_calls += 1
        return self.used_calls


@dataclass(slots=True)
class BoundExecution:
    session: TwoChoiceSession
    assignment_row: Any
    materialized_row: MaterializedScheduleRow
    execution_interface: Mapping[str, Any]

    def execute(
        self,
        executor: Callable[
            [Mapping[str, Any], Mapping[str, Any], ToolCallGuard],
            Mapping[str, Any],
        ],
    ) -> Mapping[str, Any]:
        """Execute once with the exact schedule and pre-side-effect tool guard."""

        schedule = json.loads(self.materialized_row.schedule_json)
        digest = hashlib.sha256(
            json.dumps(
                schedule,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            ).encode("utf-8")
        ).hexdigest()
        if digest != self.materialized_row.schedule_digest:
            raise RuntimeError("materialized schedule fingerprint changed")
        affordance = schedule["tool_affordance"]
        guard = ToolCallGuard(
            enabled_tools=tuple(affordance["enabled_tools"]),
            max_calls=int(affordance["max_calls"]),
        )

        def call_bound(item_id: str, received: ChoiceCategory) -> Mapping[str, Any]:
            if item_id != self.session.item_id:
                raise RuntimeError("executor item/session binding changed")
            if received.value != self.materialized_row.received_schedule:
                raise RuntimeError("executor schedule/assignment binding changed")
            record = executor(
                json.loads(json.dumps(self.execution_interface)),
                json.loads(self.materialized_row.schedule_json),
                guard,
            )
            if not isinstance(record, Mapping):
                raise TypeError("bound executor must return a mapping")
            declared_calls = record.get("tool_calls_used")
            if declared_calls is not None and declared_calls != guard.used_calls:
                raise ValueError("execution record tool count disagrees with guard")
            return record

        return self.session.execute(
            call_bound,
            execution_interface=self.execution_interface,
        )


def bind_joint_assignment(
    bank: Mapping[str, Any],
    assignment: JointAssignment,
    materialized: MaterializedAssignment,
    sessions: Mapping[str, TwoChoiceSession],
) -> tuple[BoundExecution, ...]:
    """Validate the whole block, then atomically bind its eight sessions."""

    if assignment.block_id != materialized.block_id:
        raise ValueError("assignment/materialization block IDs differ")
    if assignment.allowed_set_index != materialized.allowed_set_index:
        raise ValueError("assignment/materialization allowed-set indices differ")
    stratum = parse_runtime_stratum(materialized.stratum)
    if stratum.pair_id != materialized.pair_id or stratum.dose != materialized.dose:
        raise ValueError("structured stratum pair/dose differ from materialization")
    item_matches = [item for item in bank["items"] if item["pair_id"] == stratum.pair_id]
    if len(item_matches) != 1 or item_matches[0]["family"] != stratum.target_family:
        raise ValueError("structured stratum target family differs from item bank")
    expected_display_mapping = variant_label_mapping(bank, stratum.variant_id)
    assignment_by_id = {row.session_id: row for row in assignment.sessions}
    materialized_by_id = {row.session_id: row for row in materialized.rows}
    if set(sessions) != set(assignment_by_id) or set(sessions) != set(materialized_by_id):
        raise ValueError("session, assignment, and materialization IDs must match exactly")

    pending: list[
        tuple[TwoChoiceSession, Any, MaterializedScheduleRow, Mapping[str, Any]]
    ] = []
    for session_id in sorted(sessions):
        session = sessions[session_id]
        row = assignment_by_id[session_id]
        materialized_row = materialized_by_id[session_id]
        if session.session_id != session_id:
            raise ValueError("session mapping key does not equal session.session_id")
        if session.stage is not SessionStage.BASELINE_RECORDED or session.baseline is None:
            raise ValueError("every bound session must have a valid recorded baseline")
        if session.displayed_label_to_canonical != expected_display_mapping:
            raise ValueError("session counterbalance mapping differs from structured stratum")
        if session.baseline.category.value != row.baseline_choice:
            raise ValueError("state-machine baseline differs from assignment baseline")
        for field in (
            "arm",
            "baseline_choice",
            "received_schedule",
            "donor_session_id",
        ):
            if getattr(materialized_row, field) != getattr(row, field):
                raise ValueError(f"materialized row differs from assignment field {field}")
        if materialized_row.pair_id != materialized.pair_id or materialized_row.dose != materialized.dose:
            raise ValueError("materialized row pair/dose metadata differ")
        canonical_name = "low" if row.received_schedule == LOW else "high"
        expected_digest, expected_schedule_json = schedule_fingerprint(
            bank,
            materialized.pair_id,
            materialized.dose,
            canonical_name,
        )
        if (
            materialized_row.schedule_digest != expected_digest
            or materialized_row.schedule_json != expected_schedule_json
        ):
            raise ValueError("materialized schedule differs from the frozen item bank")
        expected_payload_id = bank_item_payload_id(bank, materialized.pair_id, "baseline")
        expected_followup_id = bank_item_payload_id(bank, materialized.pair_id, "followup")
        if session.item_id != expected_payload_id or session.followup_item_id != expected_followup_id:
            raise ValueError("state-machine payload IDs differ from bound item pair")
        execution_interface = render_execution_interface(
            bank,
            pair_id=materialized.pair_id,
            dose=materialized.dose,
            canonical=canonical_name,
        )
        pending.append((session, row, materialized_row, execution_interface))

    # No session is assigned until the complete eight-row validation succeeds.
    bound: list[BoundExecution] = []
    for session, row, materialized_row, execution_interface in pending:
        arm = (
            EnforcementArm.SELF_CONTINGENT if row.arm == SELF else EnforcementArm.YOKED
        )
        schedule = ChoiceCategory.LOW if row.received_schedule == LOW else ChoiceCategory.HIGH
        session.assign(arm, schedule)
        bound.append(
            BoundExecution(
                session=session,
                assignment_row=row,
                materialized_row=materialized_row,
                execution_interface=execution_interface,
            )
        )
    return tuple(bound)


def bank_item_payload_id(bank: Mapping[str, Any], pair_id: str, phase: str) -> str:
    if phase not in {"baseline", "followup"}:
        raise ValueError("phase must be baseline or followup")
    matches = [item for item in bank["items"] if item["pair_id"] == pair_id]
    if len(matches) != 1:
        raise KeyError(pair_id)
    return str(matches[0][phase]["payload_id"])
