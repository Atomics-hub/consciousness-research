"""Deterministic two-choice Binding Test session state machine.

Treatment assignment is structurally impossible until a valid baseline choice
has been recorded. Enforcement-arm labels are internal and never emitted in a
model-visible event.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
from enum import Enum
import re
from typing import Any, Callable, Mapping

from .parsers import ChoiceCategory, ParseResult, parse_choice, parse_display_choice


class SessionStage(str, Enum):
    CREATED = "created"
    BASELINE_PRESENTED = "baseline_presented"
    BASELINE_RECORDED = "baseline_recorded"
    BASELINE_UNAVAILABLE = "baseline_unavailable"
    ASSIGNED = "assigned"
    EXECUTION_ATTEMPTED = "execution_attempted"
    EXECUTED = "executed"
    EXECUTION_FAILED = "execution_failed"
    FOLLOWUP_PRESENTED = "followup_presented"
    COMPLETE = "complete"


class EnforcementArm(str, Enum):
    SELF_CONTINGENT = "self_contingent"
    YOKED = "yoked"


@dataclass(frozen=True)
class VisibleEvent:
    kind: str
    payload: Mapping[str, Any]


_ROLE_LEAK = re.compile(
    r"\b(?:roles?|arms?|treatments?|control[-_ ]?groups?|experimental[-_ ]?groups?|"
    r"self[-_ ]?contingent|yokes?|yoked|donors?|recipients?|"
    r"enforcement[-_ ]?arm|treatment[-_ ]?arm|assignment[-_ ]?role)\b",
    flags=re.IGNORECASE,
)


def _contains_role_leak(value: Any) -> bool:
    if isinstance(value, Mapping):
        return any(
            _ROLE_LEAK.search(str(key)) or _contains_role_leak(nested)
            for key, nested in value.items()
        )
    if isinstance(value, (list, tuple, set)):
        return any(_contains_role_leak(nested) for nested in value)
    return isinstance(value, str) and _ROLE_LEAK.search(value) is not None


class TwoChoiceSession:
    """Supported public API for a single confirmatory two-choice session.

    Treatment-bearing state has read-only public properties and cannot be
    supplied to the constructor.  Python cannot defend against deliberate
    mutation of underscore-prefixed internals; the structural claim is scoped
    to this supported API and its serialized/model-visible outputs.
    """

    def __init__(
        self,
        session_id: str,
        item_id: str,
        *,
        followup_item_id: str | None = None,
        displayed_label_to_canonical: Mapping[str, str] | None = None,
    ) -> None:
        if not session_id or not item_id:
            raise ValueError("session_id and item_id must be nonempty")
        self._session_id = session_id
        self._item_id = item_id
        self._followup_item_id = followup_item_id or f"{item_id}::heldout"
        if self._followup_item_id == item_id:
            raise ValueError("followup_item_id must be held out from execution item_id")
        self._stage = SessionStage.CREATED
        self._baseline: ParseResult | None = None
        self._followup: ParseResult | None = None
        self._arm: EnforcementArm | None = None
        self._received_schedule: ChoiceCategory | None = None
        self._execution_record: dict[str, Any] | None = None
        self._execution_attempted = False
        self._execution_error: dict[str, str] | None = None
        self._visible_events: list[VisibleEvent] = []
        self._display_mapping = (
            dict(displayed_label_to_canonical)
            if displayed_label_to_canonical is not None
            else None
        )
        if self._display_mapping is not None:
            # Validate the frozen mapping without accepting a response.
            parse_display_choice(
                None,
                displayed_label_to_canonical=self._display_mapping,
            )

    @property
    def session_id(self) -> str:
        return self._session_id

    @property
    def item_id(self) -> str:
        return self._item_id

    @property
    def followup_item_id(self) -> str:
        return self._followup_item_id

    @property
    def stage(self) -> SessionStage:
        return self._stage

    @property
    def baseline(self) -> ParseResult | None:
        return self._baseline

    @property
    def followup(self) -> ParseResult | None:
        return self._followup

    @property
    def arm(self) -> EnforcementArm | None:
        return self._arm

    @property
    def received_schedule(self) -> ChoiceCategory | None:
        return self._received_schedule

    @property
    def execution_record(self) -> Mapping[str, Any] | None:
        return deepcopy(self._execution_record) if self._execution_record is not None else None

    @property
    def execution_attempted(self) -> bool:
        return self._execution_attempted

    @property
    def displayed_label_to_canonical(self) -> Mapping[str, str] | None:
        return dict(self._display_mapping) if self._display_mapping is not None else None

    @property
    def visible_events(self) -> tuple[VisibleEvent, ...]:
        return tuple(
            VisibleEvent(event.kind, deepcopy(event.payload))
            for event in self._visible_events
        )

    def present_baseline(self, interface: Mapping[str, Any]) -> None:
        self._require(SessionStage.CREATED)
        if interface.get("payload_id") != self._item_id:
            raise ValueError("baseline interface payload_id must equal item_id")
        if _contains_role_leak(interface):
            raise ValueError("baseline interface leaks an enforcement-role cue")
        self._visible_events.append(
            VisibleEvent("baseline_interface", deepcopy(dict(interface)))
        )
        self._stage = SessionStage.BASELINE_PRESENTED

    def record_baseline(self, raw_text: str | None, *, transport_error: bool = False) -> ParseResult:
        self._require(SessionStage.BASELINE_PRESENTED)
        result = (
            parse_display_choice(
                raw_text,
                displayed_label_to_canonical=self._display_mapping,
                transport_error=transport_error,
            )
            if self._display_mapping is not None
            else parse_choice(raw_text, transport_error=transport_error)
        )
        self._baseline = result
        self._stage = (
            SessionStage.BASELINE_RECORDED
            if result.available
            else SessionStage.BASELINE_UNAVAILABLE
        )
        return result

    def assign(self, arm: EnforcementArm, schedule: ChoiceCategory) -> None:
        self._require(SessionStage.BASELINE_RECORDED)
        if not self._baseline or not self._baseline.available:
            raise ValueError("a valid baseline choice is required for assignment")
        if schedule is ChoiceCategory.UNAVAILABLE:
            raise ValueError("an execution schedule must be L or H")
        if arm is EnforcementArm.SELF_CONTINGENT and schedule is not self._baseline.category:
            raise ValueError("self-contingent execution must apply the baseline choice")
        self._arm = arm
        self._received_schedule = schedule
        self._stage = SessionStage.ASSIGNED

    def execute(
        self,
        executor: Callable[[str, ChoiceCategory], Mapping[str, Any]],
        *,
        execution_interface: Mapping[str, Any] | None = None,
    ) -> Mapping[str, Any]:
        self._require(SessionStage.ASSIGNED)
        if self._received_schedule is None:
            raise RuntimeError("assigned schedule missing")
        interface = dict(execution_interface or {"payload_id": self._item_id})
        if interface.get("payload_id") != self._item_id:
            raise ValueError("execution interface payload_id must equal item_id")
        if _contains_role_leak(interface):
            raise ValueError("execution interface leaks an enforcement-role cue")
        self._execution_attempted = True
        self._stage = SessionStage.EXECUTION_ATTEMPTED
        self._visible_events.append(
            VisibleEvent("execution_interface", deepcopy(interface))
        )
        try:
            record = deepcopy(dict(executor(self._item_id, self._received_schedule)))
            if _contains_role_leak(record):
                raise ValueError("execution record leaks an enforcement-role field")
        except Exception as error:
            self._execution_error = {
                "type": type(error).__name__,
                "message": str(error),
            }
            self._stage = SessionStage.EXECUTION_FAILED
            raise
        self._execution_record = deepcopy(record)
        self._visible_events.append(
            VisibleEvent("execution_record", deepcopy(record))
        )
        self._stage = SessionStage.EXECUTED
        return deepcopy(record)

    def present_followup(self, interface: Mapping[str, Any]) -> None:
        self._require(SessionStage.EXECUTED)
        if interface.get("payload_id") != self._followup_item_id:
            raise ValueError("follow-up interface payload_id must equal followup_item_id")
        if _contains_role_leak(interface):
            raise ValueError("follow-up interface leaks an enforcement-role cue")
        self._visible_events.append(
            VisibleEvent("followup_interface", deepcopy(dict(interface)))
        )
        self._stage = SessionStage.FOLLOWUP_PRESENTED

    def record_followup(
        self,
        raw_text: str | None,
        *,
        transport_error: bool = False,
    ) -> ParseResult:
        self._require(SessionStage.FOLLOWUP_PRESENTED)
        result = (
            parse_display_choice(
                raw_text,
                displayed_label_to_canonical=self._display_mapping,
                transport_error=transport_error,
            )
            if self._display_mapping is not None
            else parse_choice(raw_text, transport_error=transport_error)
        )
        self._followup = result
        self._stage = SessionStage.COMPLETE
        return result

    def audit_record(self) -> dict[str, Any]:
        return {
            "session_id": self._session_id,
            "item_id": self._item_id,
            "followup_item_id": self._followup_item_id,
            "stage": self._stage.value,
            "baseline": asdict(self._baseline) if self._baseline else None,
            "followup": asdict(self._followup) if self._followup else None,
            "arm": self._arm.value if self._arm else None,
            "received_schedule": (
                self._received_schedule.value if self._received_schedule else None
            ),
            "execution_record": deepcopy(self._execution_record or {}),
            "execution_attempted": self._execution_attempted,
            "execution_error": deepcopy(self._execution_error),
            "visible_events": [asdict(event) for event in self._visible_events],
        }

    def visible_text(self) -> str:
        return "\n".join(str(asdict(event)) for event in self._visible_events)

    def _require(self, expected: SessionStage) -> None:
        if self._stage is not expected:
            raise RuntimeError(
                f"invalid transition: expected {expected.value}, found {self._stage.value}"
            )
