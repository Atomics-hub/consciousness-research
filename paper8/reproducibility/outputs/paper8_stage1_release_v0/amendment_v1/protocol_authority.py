"""Fail-closed protocol authority for the Binding Test ITT amendment.

This module uses the Python standard library and the sealed local ``zero_call``
assignment enumerator.  It separates the immutable, pre-outcome randomization
authority from the exactly-once terminal-disposition ledger.  It performs no
provider call and contains no response payload fields.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass, fields
import hashlib
from itertools import combinations, permutations
import json
from pathlib import Path
import re
from typing import Final


BLOCK_SCHEMA_VERSION: Final = "binding-randomized-block-v1"
TERMINAL_SCHEMA_VERSION: Final = "binding-terminal-disposition-v1"
ALLOWED_SET_SCHEMA_VERSION: Final = "binding-allowed-set-artifact-v1"
ASSIGNMENT_PROJECTION_SCHEMA: Final = "session-specific-full-assignment-row-v1"
SELECTION_PROOF_VERSION: Final = "binding-selection-proof-v1"
CANONICAL_ALLOWED_SET_VERSION: Final = "canonical-donor-aware-576-v1"
CANONICAL_ASSIGNMENT_ENGINE_VERSION: Final = "zero-call-binding-test-assignment-v1"
CONFIRMATORY_PHASE: Final = "confirmatory"
ALLOWED_SET_SIZE: Final = 576
BLOCK_SIZE: Final = 8

_ALLOWED_SET_MEMBER_DOMAIN: Final = "paper8.allowed-set-member.v1"
_ALLOWED_SET_AGGREGATE_DOMAIN: Final = "paper8.allowed-set-aggregate.v1"
_ASSIGNMENT_POLICY_DOMAIN: Final = "paper8.assignment-policy.v1"
_RANDOMNESS_COMMITMENT_DOMAIN: Final = "paper8.randomness-commitment.v1"
_SELECTION_INDEX_DOMAIN: Final = "paper8.selection-index.v1"

_REPOSITORY_ROOT: Final = Path(__file__).resolve().parents[3]
_ZERO_CALL_ROOT: Final = _REPOSITORY_ROOT / "zero_call"
_ASSIGNMENT_ENGINE_SOURCE: Final = (
    _ZERO_CALL_ROOT / "binding_test" / "assignment.py"
)
_CANONICAL_ASSIGNMENT_ENGINE_SHA256: Final = (
    "eeb51a912d9b0674030d7175251919fa318d7ab567db9ab84f9cd16f47e032a4"
)

CHOICES: Final = ("L", "H")
TERMINAL_DISPOSITIONS: Final = ("L", "H", "U")
ARMS: Final = ("self", "yoke")
DOSES: Final = ("active", "zero_dose")

DISPOSITION_SOURCES: Final = (
    "followup_choice",
    "followup_unavailable",
    "execution_failure",
    "followup_failure",
    "local_protocol_abort",
)

SOURCE_SUBTYPES: Final[dict[str, tuple[str, ...]]] = {
    "followup_choice": ("none",),
    "followup_unavailable": (
        "missing_response",
        "empty_response",
        "explicit_refusal",
        "invalid_response",
    ),
    "execution_failure": (
        "invalid_response",
        "transport_error",
        "timeout",
        "provider_error",
        "quota_exhausted",
        "tool_error",
        "tool_limit_exceeded",
    ),
    "followup_failure": (
        "transport_error",
        "timeout",
        "provider_error",
        "quota_exhausted",
    ),
    "local_protocol_abort": (
        "assignment_binding_mismatch",
        "schedule_integrity_mismatch",
        "role_leak_detected",
        "runtime_contract_violation",
        "controller_abort",
        "unknown",
    ),
}

_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_ENTROPY_REVEAL = re.compile(r"[0-9a-f]{64}\Z")


class ProtocolAuthorityError(ValueError):
    """Base class for fail-closed protocol-authority errors."""


class ClosedSchemaError(ProtocolAuthorityError):
    """A mapping did not have the exact frozen field set."""


class TerminalConflictError(ProtocolAuthorityError):
    """A terminal key was replayed with different content."""


class IncompleteTerminalLedgerError(ProtocolAuthorityError):
    """A ledger could not be finalized to exactly the randomized sessions."""


def canonical_json(value: object) -> str:
    """Return the single canonical JSON encoding used by every commitment."""

    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def canonical_sha256(value: object) -> str:
    """Hash a value after canonical JSON encoding."""

    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def canonical_assignment_engine_digest() -> str:
    """Verify and return the pinned SHA-256 of the assignment implementation."""

    if (
        not _ASSIGNMENT_ENGINE_SOURCE.is_file()
        or _ASSIGNMENT_ENGINE_SOURCE.is_symlink()
    ):
        raise ProtocolAuthorityError(
            f"canonical assignment engine missing or unsafe: {_ASSIGNMENT_ENGINE_SOURCE}"
        )
    observed = hashlib.sha256(_ASSIGNMENT_ENGINE_SOURCE.read_bytes()).hexdigest()
    if observed != _CANONICAL_ASSIGNMENT_ENGINE_SHA256:
        raise ProtocolAuthorityError(
            "zero_call/binding_test/assignment.py does not match the pinned "
            "canonical assignment engine digest"
        )
    return _CANONICAL_ASSIGNMENT_ENGINE_SHA256


def _text(name: str, value: object, *, forbid_pipe: bool = False) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProtocolAuthorityError(f"{name} must be a non-empty string")
    if value != value.strip():
        raise ProtocolAuthorityError(f"{name} must not have surrounding whitespace")
    if forbid_pipe and "|" in value:
        raise ProtocolAuthorityError(f"{name} must not contain '|'")
    return value


def _digest(name: str, value: object) -> str:
    text = _text(name, value)
    if _SHA256.fullmatch(text) is None:
        raise ProtocolAuthorityError(f"{name} must be a lowercase SHA-256 digest")
    return text


def _integer(name: str, value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ProtocolAuthorityError(f"{name} must be an integer")
    return value


def _nullable_bool(name: str, value: object) -> bool | None:
    if value is not None and not isinstance(value, bool):
        raise ProtocolAuthorityError(f"{name} must be bool or null")
    return value


def _exact_fields(
    name: str,
    record: object,
    expected: set[str],
) -> Mapping[str, object]:
    if not isinstance(record, Mapping):
        raise ClosedSchemaError(f"{name} must be a mapping")
    supplied = set(record)
    missing = sorted(expected - supplied)
    extra = sorted(supplied - expected, key=str)
    if missing or extra:
        raise ClosedSchemaError(
            f"{name} fields must match exactly; missing={missing}, extra={extra}"
        )
    if not all(isinstance(key, str) for key in record):
        raise ClosedSchemaError(f"{name} field names must be strings")
    return record


@dataclass(frozen=True, slots=True)
class AssignmentRow:
    """One immutable session assignment inside a randomized block."""

    session_id: str
    baseline_choice: str
    arm: str
    received_schedule: str
    donor_session_id: str
    execution_order_index: int
    schedule_digest: str
    affordance_digest: str

    def __post_init__(self) -> None:
        _text("session_id", self.session_id)
        _text("donor_session_id", self.donor_session_id)
        if self.baseline_choice not in CHOICES:
            raise ProtocolAuthorityError(f"baseline_choice must be one of {CHOICES}")
        if self.arm not in ARMS:
            raise ProtocolAuthorityError(f"arm must be one of {ARMS}")
        if self.received_schedule not in CHOICES:
            raise ProtocolAuthorityError(f"received_schedule must be one of {CHOICES}")
        index = _integer("execution_order_index", self.execution_order_index)
        if not 0 <= index < BLOCK_SIZE:
            raise ProtocolAuthorityError("execution_order_index must be in [0, 7]")
        _digest("schedule_digest", self.schedule_digest)
        _digest("affordance_digest", self.affordance_digest)

    def to_mapping(self) -> dict[str, object]:
        return {
            "session_id": self.session_id,
            "baseline_choice": self.baseline_choice,
            "arm": self.arm,
            "received_schedule": self.received_schedule,
            "donor_session_id": self.donor_session_id,
            "execution_order_index": self.execution_order_index,
            "schedule_digest": self.schedule_digest,
            "affordance_digest": self.affordance_digest,
        }

    @classmethod
    def from_mapping(cls, record: object) -> AssignmentRow:
        expected = {field.name for field in fields(cls)}
        value = _exact_fields("assignment row", record, expected)
        return cls(**{name: value[name] for name in expected})  # type: ignore[arg-type]


def _assignment_projection(
    assignments: tuple[AssignmentRow, ...],
) -> list[dict[str, object]]:
    """Project every assignment field; candidates are block/session specific."""

    return [row.to_mapping() for row in assignments]


def _validate_assignment_projection(
    assignments: object,
    *,
    name: str,
) -> tuple[AssignmentRow, ...]:
    if not isinstance(assignments, tuple) or not all(
        isinstance(row, AssignmentRow) for row in assignments
    ):
        raise ProtocolAuthorityError(
            f"{name} must be a tuple of AssignmentRow objects"
        )
    if len(assignments) != BLOCK_SIZE:
        raise ProtocolAuthorityError(f"{name} must contain exactly 8 rows")
    session_ids = tuple(row.session_id for row in assignments)
    if session_ids != tuple(sorted(session_ids)):
        raise ProtocolAuthorityError(f"{name} rows must be ordered by session_id")
    if len(set(session_ids)) != BLOCK_SIZE:
        raise ProtocolAuthorityError(f"{name} session IDs must be unique")
    if {row.execution_order_index for row in assignments} != set(range(BLOCK_SIZE)):
        raise ProtocolAuthorityError(
            f"{name} execution_order_index values must be an exact permutation of 0..7"
        )
    if Counter(row.baseline_choice for row in assignments) != Counter(
        {"L": 4, "H": 4}
    ):
        raise ProtocolAuthorityError(f"{name} baseline support must be exactly 4L/4H")
    if Counter(row.arm for row in assignments) != Counter({"self": 4, "yoke": 4}):
        raise ProtocolAuthorityError(f"{name} arms must be exactly 4 self/4 yoke")

    self_rows = tuple(row for row in assignments if row.arm == "self")
    yoke_rows = tuple(row for row in assignments if row.arm == "yoke")
    if Counter(row.baseline_choice for row in self_rows) != Counter(
        {"L": 2, "H": 2}
    ):
        raise ProtocolAuthorityError(
            f"{name} self arm must contain exactly 2L/2H baselines"
        )
    if any(
        row.received_schedule != row.baseline_choice
        or row.donor_session_id != row.session_id
        for row in self_rows
    ):
        raise ProtocolAuthorityError(
            f"{name} self rows must receive their own baseline schedules"
        )
    donors = {row.session_id: row for row in self_rows}
    if Counter(row.donor_session_id for row in yoke_rows) != Counter(donors.keys()):
        raise ProtocolAuthorityError(
            f"{name} yoke rows must use every self donor exactly once"
        )
    for row in yoke_rows:
        donor = donors[row.donor_session_id]
        if row.received_schedule != donor.baseline_choice:
            raise ProtocolAuthorityError(
                f"{name} yoke received schedule must equal the donor baseline"
            )
        if row.schedule_digest != donor.schedule_digest:
            raise ProtocolAuthorityError(
                f"{name} yoke schedule digest must equal its donor schedule digest"
            )
        if row.affordance_digest != donor.affordance_digest:
            raise ProtocolAuthorityError(
                f"{name} yoke affordance digest must equal its donor affordance digest"
            )
    expected_exposures = Counter(
        {("L", "L"): 1, ("L", "H"): 1, ("H", "L"): 1, ("H", "H"): 1}
    )
    actual_exposures = Counter(
        (row.baseline_choice, row.received_schedule) for row in yoke_rows
    )
    if actual_exposures != expected_exposures:
        raise ProtocolAuthorityError(
            f"{name} yoke baseline/received-schedule exposures must contain each L/H cell once"
        )
    for choice in CHOICES:
        schedule_digests = {
            row.schedule_digest
            for row in assignments
            if row.received_schedule == choice
        }
        affordance_digests = {
            row.affordance_digest
            for row in assignments
            if row.received_schedule == choice
        }
        if len(schedule_digests) != 1 or len(affordance_digests) != 1:
            raise ProtocolAuthorityError(
                f"{name} must have one exact schedule and affordance digest per received schedule"
            )
    return assignments


def assignment_member_digest(assignments: tuple[AssignmentRow, ...]) -> str:
    """Hash the complete session-specific eight-row candidate projection."""

    rows = _validate_assignment_projection(
        assignments,
        name="allowed-set candidate",
    )
    return canonical_sha256(
        {
            "domain": _ALLOWED_SET_MEMBER_DOMAIN,
            "projection_schema": ASSIGNMENT_PROJECTION_SCHEMA,
            "assignments": _assignment_projection(rows),
        }
    )


def _fixed_candidate_contract(
    candidates: tuple[tuple[AssignmentRow, ...], ...],
) -> tuple[
    tuple[str, ...],
    dict[str, str],
    dict[str, int],
    dict[str, tuple[str, str]],
]:
    """Recover and verify fields that are not randomized by the 576-way policy.

    Baseline and execution order are fixed per session.  Schedule and
    affordance digests are fixed per materialized L/H schedule, even when a
    session's received schedule differs across allowed assignments.
    """

    first = candidates[0]
    expected_sessions = tuple(row.session_id for row in first)
    baseline_by_session = {row.session_id: row.baseline_choice for row in first}
    execution_by_session = {
        row.session_id: row.execution_order_index for row in first
    }
    material_by_schedule: dict[str, tuple[str, str]] = {}
    for row in first:
        material = (row.schedule_digest, row.affordance_digest)
        existing = material_by_schedule.setdefault(row.received_schedule, material)
        if existing != material:
            raise ProtocolAuthorityError(
                "first allowed-set candidate has inconsistent schedule material digests"
            )
    if set(material_by_schedule) != set(CHOICES):
        raise ProtocolAuthorityError(
            "allowed-set candidates must materialize both L and H schedules"
        )

    for index, candidate in enumerate(candidates):
        sessions = tuple(row.session_id for row in candidate)
        if sessions != expected_sessions:
            raise ProtocolAuthorityError(
                "every allowed-set candidate must bind the same ordered eight session IDs"
            )
        for row in candidate:
            if row.baseline_choice != baseline_by_session[row.session_id]:
                raise ProtocolAuthorityError(
                    f"allowed-set candidate {index} changed fixed per-session baseline_choice"
                )
            if row.execution_order_index != execution_by_session[row.session_id]:
                raise ProtocolAuthorityError(
                    f"allowed-set candidate {index} changed fixed per-session execution_order_index"
                )
            expected_material = material_by_schedule[row.received_schedule]
            if (row.schedule_digest, row.affordance_digest) != expected_material:
                raise ProtocolAuthorityError(
                    f"allowed-set candidate {index} changed fixed schedule material digests"
                )
    return (
        expected_sessions,
        baseline_by_session,
        execution_by_session,
        material_by_schedule,
    )


def _canonical_engine_candidate_projections(
    block_id: str,
    template: tuple[AssignmentRow, ...],
) -> tuple[tuple[AssignmentRow, ...], ...]:
    """Recompute the byte-pinned engine's closed, exact 576-way enumeration.

    This is a local projection of the pinned algorithm, not a dynamic import;
    preloaded or monkeypatched ``binding_test.assignment`` modules therefore
    cannot influence the authority decision.  The loop order intentionally
    mirrors the pinned source: sorted L/H IDs, lexicographic 2-of-4 self-arm
    combinations, then lexicographic permutations of sorted self donors.
    """

    _text("block_id", block_id)
    canonical_assignment_engine_digest()
    baseline_by_session = {
        row.session_id: row.baseline_choice for row in template
    }
    execution_by_session = {
        row.session_id: row.execution_order_index for row in template
    }
    material_by_schedule: dict[str, tuple[str, str]] = {}
    for row in template:
        material_by_schedule[row.received_schedule] = (
            row.schedule_digest,
            row.affordance_digest,
        )
    low_ids = sorted(
        session_id
        for session_id, choice in baseline_by_session.items()
        if choice == "L"
    )
    high_ids = sorted(
        session_id
        for session_id, choice in baseline_by_session.items()
        if choice == "H"
    )
    if len(low_ids) != 4 or len(high_ids) != 4:
        raise ProtocolAuthorityError(
            "canonical assignment projection requires exactly four L and four H baselines"
        )

    projected: list[tuple[AssignmentRow, ...]] = []
    all_session_ids = tuple(sorted(baseline_by_session))
    for self_low in combinations(low_ids, 2):
        for self_high in combinations(high_ids, 2):
            self_ids = tuple(sorted(self_low + self_high))
            self_id_set = set(self_ids)
            yoke_ids = tuple(
                session_id
                for session_id in all_session_ids
                if session_id not in self_id_set
            )
            for donor_order in permutations(self_ids):
                cell_counts = Counter(
                    (
                        baseline_by_session[recipient_id],
                        baseline_by_session[donor_id],
                    )
                    for recipient_id, donor_id in zip(
                        yoke_ids,
                        donor_order,
                        strict=True,
                    )
                )
                if cell_counts != Counter(
                    {("L", "L"): 1, ("L", "H"): 1, ("H", "L"): 1, ("H", "H"): 1}
                ):
                    continue
                donor_by_recipient = dict(
                    zip(yoke_ids, donor_order, strict=True)
                )
                rows: list[AssignmentRow] = []
                for session_id in all_session_ids:
                    if session_id in self_id_set:
                        arm = "self"
                        donor_session_id = session_id
                    else:
                        arm = "yoke"
                        donor_session_id = donor_by_recipient[session_id]
                    received_schedule = baseline_by_session[donor_session_id]
                    rows.append(
                        AssignmentRow(
                            session_id=session_id,
                            baseline_choice=baseline_by_session[session_id],
                            arm=arm,
                            received_schedule=received_schedule,
                            donor_session_id=donor_session_id,
                            execution_order_index=execution_by_session[session_id],
                            schedule_digest=material_by_schedule[received_schedule][0],
                            affordance_digest=material_by_schedule[received_schedule][1],
                        )
                    )
                projected.append(tuple(rows))
    if len(projected) != ALLOWED_SET_SIZE:
        raise ProtocolAuthorityError(
            "closed canonical assignment contract did not project exactly 576 candidates"
        )
    if len(set(map(canonical_json, map(_assignment_projection, projected)))) != ALLOWED_SET_SIZE:
        raise ProtocolAuthorityError(
            "closed canonical assignment contract did not produce 576 unique candidates"
        )
    return tuple(projected)


@dataclass(frozen=True, slots=True)
class AllowedSetArtifact:
    """Closed, ordered authority for all 576 session-specific candidates.

    Each candidate is the full eight-row AssignmentRow projection, including
    session IDs, baselines, arms, schedules, donor IDs, execution order, and
    schedule/affordance digests.  Candidate order is meaningful and is bound by
    the domain-separated aggregate digest.
    """

    protocol_run_id: str
    protocol_manifest_digest: str
    block_id: str
    allowed_set_version: str
    assignment_engine_version: str
    assignment_engine_digest: str
    candidates: tuple[tuple[AssignmentRow, ...], ...]
    candidate_projection_schema: str = ASSIGNMENT_PROJECTION_SCHEMA
    allowed_set_size: int = ALLOWED_SET_SIZE
    schema_version: str = ALLOWED_SET_SCHEMA_VERSION
    allowed_set_digest: str = ""

    def __post_init__(self) -> None:
        if self.schema_version != ALLOWED_SET_SCHEMA_VERSION:
            raise ProtocolAuthorityError(
                f"schema_version must equal {ALLOWED_SET_SCHEMA_VERSION!r}"
            )
        if self.candidate_projection_schema != ASSIGNMENT_PROJECTION_SCHEMA:
            raise ProtocolAuthorityError(
                f"candidate_projection_schema must equal {ASSIGNMENT_PROJECTION_SCHEMA!r}"
            )
        _text("protocol_run_id", self.protocol_run_id)
        _digest("protocol_manifest_digest", self.protocol_manifest_digest)
        _text("block_id", self.block_id)
        if self.allowed_set_version != CANONICAL_ALLOWED_SET_VERSION:
            raise ProtocolAuthorityError(
                f"allowed_set_version must equal {CANONICAL_ALLOWED_SET_VERSION!r}"
            )
        if self.assignment_engine_version != CANONICAL_ASSIGNMENT_ENGINE_VERSION:
            raise ProtocolAuthorityError(
                "assignment_engine_version does not name the sealed zero-call enumerator"
            )
        _digest("assignment_engine_digest", self.assignment_engine_digest)
        expected_engine_digest = canonical_assignment_engine_digest()
        if self.assignment_engine_digest != expected_engine_digest:
            raise ProtocolAuthorityError(
                "assignment_engine_digest does not match zero_call/binding_test/assignment.py"
            )
        if _integer("allowed_set_size", self.allowed_set_size) != ALLOWED_SET_SIZE:
            raise ProtocolAuthorityError("allowed_set_size must equal 576")
        if not isinstance(self.candidates, tuple) or len(self.candidates) != ALLOWED_SET_SIZE:
            raise ProtocolAuthorityError(
                "allowed-set artifact must contain exactly 576 ordered candidates"
            )

        canonical_candidates: list[str] = []
        member_digests: list[str] = []
        for index, candidate in enumerate(self.candidates):
            rows = _validate_assignment_projection(
                candidate,
                name=f"allowed-set candidate {index}",
            )
            projection = _assignment_projection(rows)
            canonical_candidates.append(canonical_json(projection))
            member_digests.append(assignment_member_digest(rows))

        (
            expected_sessions,
            _baseline_by_session,
            _execution_by_session,
            _material_by_schedule,
        ) = _fixed_candidate_contract(self.candidates)

        for session_id in expected_sessions:
            rows = tuple(
                next(row for row in candidate if row.session_id == session_id)
                for candidate in self.candidates
            )
            self_count = sum(row.arm == "self" for row in rows)
            yoke_rows = tuple(row for row in rows if row.arm == "yoke")
            if self_count != 288 or len(yoke_rows) != 288:
                raise ProtocolAuthorityError(
                    f"session {session_id!r} must have exact 288/288 self/yoke marginal support"
                )
            if Counter(row.received_schedule for row in yoke_rows) != Counter(
                {"L": 144, "H": 144}
            ):
                raise ProtocolAuthorityError(
                    f"session {session_id!r} must receive L/H exactly 144/144 conditional on yoke"
                )
            if Counter(
                row.received_schedule == row.baseline_choice for row in yoke_rows
            ) != Counter({True: 144, False: 144}):
                raise ProtocolAuthorityError(
                    f"session {session_id!r} must have exact 144/144 yoke match/mismatch support"
                )
        if len(set(canonical_candidates)) != ALLOWED_SET_SIZE:
            raise ProtocolAuthorityError(
                "allowed-set candidates must be exactly 576 unique projections"
            )

        expected_candidates = _canonical_engine_candidate_projections(
            self.block_id,
            self.candidates[0],
        )
        if self.candidates != expected_candidates:
            mismatch_index = next(
                index
                for index, (actual, expected) in enumerate(
                    zip(self.candidates, expected_candidates, strict=True)
                )
                if actual != expected
            )
            raise ProtocolAuthorityError(
                "allowed-set candidates do not equal the sealed engine's exact "
                f"canonical set/order at index {mismatch_index}"
            )

        expected_digest = self._aggregate_digest(tuple(member_digests))
        if self.allowed_set_digest != "":
            _digest("allowed_set_digest", self.allowed_set_digest)
            if self.allowed_set_digest != expected_digest:
                raise ProtocolAuthorityError("allowed-set aggregate digest mismatch")
        else:
            object.__setattr__(self, "allowed_set_digest", expected_digest)

    def _aggregate_digest(self, member_digests: tuple[str, ...]) -> str:
        return canonical_sha256(
            {
                "domain": _ALLOWED_SET_AGGREGATE_DOMAIN,
                "schema_version": self.schema_version,
                "candidate_projection_schema": self.candidate_projection_schema,
                "protocol_run_id": self.protocol_run_id,
                "protocol_manifest_digest": self.protocol_manifest_digest,
                "block_id": self.block_id,
                "allowed_set_version": self.allowed_set_version,
                "allowed_set_size": self.allowed_set_size,
                "assignment_engine_version": self.assignment_engine_version,
                "assignment_engine_digest": self.assignment_engine_digest,
                "ordered_member_digests": list(member_digests),
            }
        )

    @property
    def member_digests(self) -> tuple[str, ...]:
        return tuple(assignment_member_digest(candidate) for candidate in self.candidates)

    def member_digest_at(self, index: int) -> str:
        value = _integer("allowed_set_index", index)
        if not 0 <= value < ALLOWED_SET_SIZE:
            raise ProtocolAuthorityError("allowed_set_index must be in [0, 575]")
        return assignment_member_digest(self.candidates[value])

    def to_mapping(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "candidate_projection_schema": self.candidate_projection_schema,
            "protocol_run_id": self.protocol_run_id,
            "protocol_manifest_digest": self.protocol_manifest_digest,
            "block_id": self.block_id,
            "allowed_set_version": self.allowed_set_version,
            "allowed_set_size": self.allowed_set_size,
            "assignment_engine_version": self.assignment_engine_version,
            "assignment_engine_digest": self.assignment_engine_digest,
            "candidates": [
                _assignment_projection(candidate) for candidate in self.candidates
            ],
            "allowed_set_digest": self.allowed_set_digest,
        }

    def to_json(self) -> str:
        return canonical_json(self.to_mapping())

    @classmethod
    def from_mapping(cls, record: object) -> AllowedSetArtifact:
        expected = {field.name for field in fields(cls)}
        value = _exact_fields("allowed-set artifact", record, expected)
        _digest("allowed_set_digest", value["allowed_set_digest"])
        raw_candidates = value["candidates"]
        if not isinstance(raw_candidates, list):
            raise ClosedSchemaError("allowed-set candidates must be a JSON list")
        candidates: list[tuple[AssignmentRow, ...]] = []
        for index, raw_candidate in enumerate(raw_candidates):
            if not isinstance(raw_candidate, list):
                raise ClosedSchemaError(
                    f"allowed-set candidate {index} must be a JSON list"
                )
            candidates.append(
                tuple(AssignmentRow.from_mapping(row) for row in raw_candidate)
            )
        kwargs = {name: value[name] for name in expected}
        kwargs["candidates"] = tuple(candidates)
        return cls(**kwargs)  # type: ignore[arg-type]


def compute_assignment_policy_digest(artifact: AllowedSetArtifact) -> str:
    """Bind the exact uniform 1/576 selection policy to one allowed set."""

    if not isinstance(artifact, AllowedSetArtifact):
        raise TypeError("artifact must be an AllowedSetArtifact")
    return canonical_sha256(
        {
            "domain": _ASSIGNMENT_POLICY_DOMAIN,
            "policy": "uniform-over-exact-ordered-allowed-set",
            "selection_proof_version": SELECTION_PROOF_VERSION,
            "protocol_run_id": artifact.protocol_run_id,
            "protocol_manifest_digest": artifact.protocol_manifest_digest,
            "block_id": artifact.block_id,
            "allowed_set_version": artifact.allowed_set_version,
            "allowed_set_digest": artifact.allowed_set_digest,
            "allowed_set_size": artifact.allowed_set_size,
            "assignment_probability_numerator": 1,
            "assignment_probability_denominator": artifact.allowed_set_size,
            "assignment_engine_version": artifact.assignment_engine_version,
            "assignment_engine_digest": artifact.assignment_engine_digest,
        }
    )


@dataclass(frozen=True, slots=True)
class RandomizedBlockRecord:
    """Complete immutable authority for one randomized canonical block."""

    study_phase: str
    protocol_run_id: str
    protocol_manifest_digest: str
    block_id: str
    macro_cell_id: str
    model_snapshot: str
    target_family: str
    fine_stratum: str
    pair_id: str
    dose: str
    variant_id: str
    allowed_set_version: str
    allowed_set_digest: str
    allowed_set_size: int
    allowed_set_index: int
    assignment_probability_numerator: int
    assignment_probability_denominator: int
    assignment_policy_digest: str
    assignment_engine_version: str
    assignment_engine_digest: str
    allowed_set_member_digest: str
    randomness_commitment: str
    assignments: tuple[AssignmentRow, ...]
    schema_version: str = BLOCK_SCHEMA_VERSION
    record_fingerprint: str = ""

    def __post_init__(self) -> None:
        if self.schema_version != BLOCK_SCHEMA_VERSION:
            raise ProtocolAuthorityError(
                f"schema_version must equal {BLOCK_SCHEMA_VERSION!r}"
            )
        if self.study_phase != CONFIRMATORY_PHASE:
            raise ProtocolAuthorityError("study_phase must be 'confirmatory'")
        _text("protocol_run_id", self.protocol_run_id)
        _digest("protocol_manifest_digest", self.protocol_manifest_digest)
        _text("block_id", self.block_id)
        model = _text("model_snapshot", self.model_snapshot, forbid_pipe=True)
        target = _text("target_family", self.target_family, forbid_pipe=True)
        pair = _text("pair_id", self.pair_id, forbid_pipe=True)
        variant = _text("variant_id", self.variant_id, forbid_pipe=True)
        if self.dose not in DOSES:
            raise ProtocolAuthorityError(f"dose must be one of {DOSES}")

        expected_cell = f"model_snapshot={model}|target_family={target}"
        if self.macro_cell_id != expected_cell:
            raise ProtocolAuthorityError(
                "macro_cell_id must be the canonical model_snapshot/target_family cell"
            )
        expected_fine = f"pair_id={pair}|dose={self.dose}|variant_id={variant}"
        if self.fine_stratum != expected_fine:
            raise ProtocolAuthorityError(
                "fine_stratum must canonically bind pair_id, dose, and variant_id"
            )

        _text("allowed_set_version", self.allowed_set_version)
        _digest("allowed_set_digest", self.allowed_set_digest)
        if _integer("allowed_set_size", self.allowed_set_size) != ALLOWED_SET_SIZE:
            raise ProtocolAuthorityError("allowed_set_size must equal 576")
        index = _integer("allowed_set_index", self.allowed_set_index)
        if not 0 <= index < ALLOWED_SET_SIZE:
            raise ProtocolAuthorityError("allowed_set_index must be in [0, 575]")
        if _integer(
            "assignment_probability_numerator", self.assignment_probability_numerator
        ) != 1:
            raise ProtocolAuthorityError("assignment probability numerator must equal 1")
        if _integer(
            "assignment_probability_denominator",
            self.assignment_probability_denominator,
        ) != ALLOWED_SET_SIZE:
            raise ProtocolAuthorityError(
                "assignment probability denominator must equal 576"
            )
        _digest("assignment_policy_digest", self.assignment_policy_digest)
        _text("assignment_engine_version", self.assignment_engine_version)
        _digest("assignment_engine_digest", self.assignment_engine_digest)
        _digest("allowed_set_member_digest", self.allowed_set_member_digest)
        _digest("randomness_commitment", self.randomness_commitment)
        _validate_assignment_projection(self.assignments, name="randomized block")

        expected_fingerprint = canonical_sha256(self._fingerprint_payload())
        if self.record_fingerprint:
            _digest("record_fingerprint", self.record_fingerprint)
            if self.record_fingerprint != expected_fingerprint:
                raise ProtocolAuthorityError("randomized block fingerprint mismatch")
        else:
            object.__setattr__(self, "record_fingerprint", expected_fingerprint)

    def _fingerprint_payload(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "study_phase": self.study_phase,
            "protocol_run_id": self.protocol_run_id,
            "protocol_manifest_digest": self.protocol_manifest_digest,
            "block_id": self.block_id,
            "macro_cell_id": self.macro_cell_id,
            "model_snapshot": self.model_snapshot,
            "target_family": self.target_family,
            "fine_stratum": self.fine_stratum,
            "pair_id": self.pair_id,
            "dose": self.dose,
            "variant_id": self.variant_id,
            "allowed_set_version": self.allowed_set_version,
            "allowed_set_digest": self.allowed_set_digest,
            "allowed_set_size": self.allowed_set_size,
            "allowed_set_index": self.allowed_set_index,
            "assignment_probability_numerator": self.assignment_probability_numerator,
            "assignment_probability_denominator": self.assignment_probability_denominator,
            "assignment_policy_digest": self.assignment_policy_digest,
            "assignment_engine_version": self.assignment_engine_version,
            "assignment_engine_digest": self.assignment_engine_digest,
            "allowed_set_member_digest": self.allowed_set_member_digest,
            "randomness_commitment": self.randomness_commitment,
            "assignments": [row.to_mapping() for row in self.assignments],
        }

    def to_mapping(self) -> dict[str, object]:
        return {**self._fingerprint_payload(), "record_fingerprint": self.record_fingerprint}

    def to_json(self) -> str:
        return canonical_json(self.to_mapping())

    @classmethod
    def from_mapping(cls, record: object) -> RandomizedBlockRecord:
        expected = {field.name for field in fields(cls)}
        value = _exact_fields("randomized block record", record, expected)
        raw_assignments = value["assignments"]
        if not isinstance(raw_assignments, list):
            raise ClosedSchemaError("randomized block assignments must be a JSON list")
        _digest("record_fingerprint", value["record_fingerprint"])
        kwargs = {name: value[name] for name in expected}
        kwargs["assignments"] = tuple(
            AssignmentRow.from_mapping(row) for row in raw_assignments
        )
        return cls(**kwargs)  # type: ignore[arg-type]


def verify_block_membership(
    record: RandomizedBlockRecord,
    artifact: AllowedSetArtifact,
) -> tuple[AssignmentRow, ...]:
    """Fail closed unless the record is exactly artifact candidate[index]."""

    if not isinstance(record, RandomizedBlockRecord):
        raise TypeError("record must be a RandomizedBlockRecord")
    if not isinstance(artifact, AllowedSetArtifact):
        raise TypeError("artifact must be an AllowedSetArtifact")
    bindings = (
        ("protocol_run_id", record.protocol_run_id, artifact.protocol_run_id),
        (
            "protocol_manifest_digest",
            record.protocol_manifest_digest,
            artifact.protocol_manifest_digest,
        ),
        ("block_id", record.block_id, artifact.block_id),
        (
            "allowed_set_version",
            record.allowed_set_version,
            artifact.allowed_set_version,
        ),
        ("allowed_set_size", record.allowed_set_size, artifact.allowed_set_size),
        (
            "allowed_set_digest",
            record.allowed_set_digest,
            artifact.allowed_set_digest,
        ),
        (
            "assignment_engine_version",
            record.assignment_engine_version,
            artifact.assignment_engine_version,
        ),
        (
            "assignment_engine_digest",
            record.assignment_engine_digest,
            artifact.assignment_engine_digest,
        ),
    )
    for name, supplied, expected in bindings:
        if supplied != expected:
            raise ProtocolAuthorityError(
                f"randomized block {name} does not match allowed-set artifact"
            )
    expected_policy_digest = compute_assignment_policy_digest(artifact)
    if record.assignment_policy_digest != expected_policy_digest:
        raise ProtocolAuthorityError(
            "randomized block assignment_policy_digest does not bind the exact "
            "uniform 1/576 artifact selection policy"
        )

    candidate = artifact.candidates[record.allowed_set_index]
    member_digest = artifact.member_digest_at(record.allowed_set_index)
    if record.allowed_set_member_digest != member_digest:
        raise ProtocolAuthorityError(
            "randomized block allowed_set_member_digest does not match candidate index"
        )
    if _assignment_projection(record.assignments) != _assignment_projection(candidate):
        raise ProtocolAuthorityError(
            "randomized block assignments are not the full candidate projection at index"
        )
    return candidate


def _validated_entropy_reveal(entropy_reveal: object) -> str:
    if not isinstance(entropy_reveal, str) or _ENTROPY_REVEAL.fullmatch(
        entropy_reveal
    ) is None:
        raise ProtocolAuthorityError(
            "entropy_reveal must be exactly 32 bytes encoded as 64 lowercase hex characters"
        )
    return entropy_reveal


def compute_randomness_commitment(entropy_reveal: str) -> str:
    """Commit to an opaque 256-bit entropy reveal before selection."""

    reveal = _validated_entropy_reveal(entropy_reveal)
    return canonical_sha256(
        {
            "domain": _RANDOMNESS_COMMITMENT_DOMAIN,
            "selection_proof_version": SELECTION_PROOF_VERSION,
            "entropy_reveal": reveal,
        }
    )


def derive_allowed_set_index(
    entropy_reveal: str,
    artifact: AllowedSetArtifact,
) -> int:
    """Derive an index with SHA-256 rejection sampling over committed context.

    Reproduction proves the reveal/commitment/context/index relationship.  It
    does not itself prove that the reveal was sampled independently or uniformly.
    """

    reveal = _validated_entropy_reveal(entropy_reveal)
    if not isinstance(artifact, AllowedSetArtifact):
        raise TypeError("artifact must be an AllowedSetArtifact")
    rejection_limit = (1 << 256) - ((1 << 256) % artifact.allowed_set_size)
    counter = 0
    while True:
        digest = canonical_sha256(
            {
                "domain": _SELECTION_INDEX_DOMAIN,
                "selection_proof_version": SELECTION_PROOF_VERSION,
                "entropy_reveal": reveal,
                "counter": counter,
                "protocol_run_id": artifact.protocol_run_id,
                "protocol_manifest_digest": artifact.protocol_manifest_digest,
                "block_id": artifact.block_id,
                "allowed_set_version": artifact.allowed_set_version,
                "allowed_set_digest": artifact.allowed_set_digest,
                "allowed_set_size": artifact.allowed_set_size,
                "assignment_engine_version": artifact.assignment_engine_version,
                "assignment_engine_digest": artifact.assignment_engine_digest,
            }
        )
        value = int(digest, 16)
        if value < rejection_limit:
            return value % artifact.allowed_set_size
        counter += 1


def verify_selection_proof(
    record: RandomizedBlockRecord,
    artifact: AllowedSetArtifact,
    entropy_reveal: str,
) -> int:
    """Verify membership plus committed-reveal deterministic index selection."""

    verify_block_membership(record, artifact)
    expected_commitment = compute_randomness_commitment(entropy_reveal)
    if record.randomness_commitment != expected_commitment:
        raise ProtocolAuthorityError(
            "entropy reveal does not match randomized block randomness_commitment"
        )
    derived_index = derive_allowed_set_index(entropy_reveal, artifact)
    if record.allowed_set_index != derived_index:
        raise ProtocolAuthorityError(
            "randomized block index does not match deterministic selection proof"
        )
    return derived_index


@dataclass(frozen=True, slots=True)
class TerminalDispositionRecord:
    """Exactly one privacy-safe terminal outcome for one randomized session."""

    study_phase: str
    protocol_run_id: str
    protocol_manifest_digest: str
    block_id: str
    session_id: str
    randomized_block_fingerprint: str
    terminal_disposition: str
    disposition_source: str
    failure_subtype: str
    followup_strict_valid: bool | None
    followup_semantic_valid: bool | None
    integrity_failure: bool
    schema_version: str = TERMINAL_SCHEMA_VERSION
    record_fingerprint: str = ""

    def __post_init__(self) -> None:
        if self.schema_version != TERMINAL_SCHEMA_VERSION:
            raise ProtocolAuthorityError(
                f"schema_version must equal {TERMINAL_SCHEMA_VERSION!r}"
            )
        if self.study_phase != CONFIRMATORY_PHASE:
            raise ProtocolAuthorityError("study_phase must be 'confirmatory'")
        _text("protocol_run_id", self.protocol_run_id)
        _digest("protocol_manifest_digest", self.protocol_manifest_digest)
        _text("block_id", self.block_id)
        _text("session_id", self.session_id)
        _digest("randomized_block_fingerprint", self.randomized_block_fingerprint)
        if self.terminal_disposition not in TERMINAL_DISPOSITIONS:
            raise ProtocolAuthorityError(
                f"terminal_disposition must be one of {TERMINAL_DISPOSITIONS}"
            )
        if self.disposition_source not in DISPOSITION_SOURCES:
            raise ProtocolAuthorityError(
                f"disposition_source must be one of {DISPOSITION_SOURCES}"
            )
        if self.failure_subtype not in SOURCE_SUBTYPES[self.disposition_source]:
            raise ProtocolAuthorityError(
                "failure_subtype is not permitted for disposition_source"
            )
        strict = _nullable_bool("followup_strict_valid", self.followup_strict_valid)
        semantic = _nullable_bool(
            "followup_semantic_valid", self.followup_semantic_valid
        )
        if not isinstance(self.integrity_failure, bool):
            raise ProtocolAuthorityError("integrity_failure must be bool")

        if self.disposition_source == "followup_choice":
            if self.terminal_disposition not in CHOICES:
                raise ProtocolAuthorityError("followup_choice must terminate as L or H")
            if strict is None or semantic is not True:
                raise ProtocolAuthorityError(
                    "followup_choice requires boolean strict validity and semantic validity true"
                )
        elif self.disposition_source == "followup_unavailable":
            if self.terminal_disposition != "U":
                raise ProtocolAuthorityError(
                    "followup_unavailable must terminate as U"
                )
            if strict is not False or semantic is not False:
                raise ProtocolAuthorityError(
                    "followup_unavailable requires strict/semantic validity false"
                )
        else:
            if self.terminal_disposition != "U":
                raise ProtocolAuthorityError(
                    "post-randomization failure or abort must terminate as U"
                )
            if strict is not None or semantic is not None:
                raise ProtocolAuthorityError(
                    "non-followup terminal sources require null parser-validity fields"
                )
        if strict is True and semantic is not True:
            raise ProtocolAuthorityError(
                "strict follow-up validity implies semantic follow-up validity"
            )
        expected_integrity = self.disposition_source == "local_protocol_abort"
        if self.integrity_failure is not expected_integrity:
            raise ProtocolAuthorityError(
                "integrity_failure must be true exactly for local_protocol_abort"
            )

        expected_fingerprint = canonical_sha256(self._fingerprint_payload())
        if self.record_fingerprint:
            _digest("record_fingerprint", self.record_fingerprint)
            if self.record_fingerprint != expected_fingerprint:
                raise ProtocolAuthorityError("terminal disposition fingerprint mismatch")
        else:
            object.__setattr__(self, "record_fingerprint", expected_fingerprint)

    @property
    def key(self) -> tuple[str, str, str]:
        return (self.protocol_run_id, self.block_id, self.session_id)

    def _fingerprint_payload(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "study_phase": self.study_phase,
            "protocol_run_id": self.protocol_run_id,
            "protocol_manifest_digest": self.protocol_manifest_digest,
            "block_id": self.block_id,
            "session_id": self.session_id,
            "randomized_block_fingerprint": self.randomized_block_fingerprint,
            "terminal_disposition": self.terminal_disposition,
            "disposition_source": self.disposition_source,
            "failure_subtype": self.failure_subtype,
            "followup_strict_valid": self.followup_strict_valid,
            "followup_semantic_valid": self.followup_semantic_valid,
            "integrity_failure": self.integrity_failure,
        }

    def to_mapping(self) -> dict[str, object]:
        return {**self._fingerprint_payload(), "record_fingerprint": self.record_fingerprint}

    def to_json(self) -> str:
        return canonical_json(self.to_mapping())

    @classmethod
    def from_mapping(cls, record: object) -> TerminalDispositionRecord:
        expected = {field.name for field in fields(cls)}
        value = _exact_fields("terminal disposition record", record, expected)
        _digest("record_fingerprint", value["record_fingerprint"])
        return cls(**{name: value[name] for name in expected})  # type: ignore[arg-type]


class TerminalLedger:
    """Exactly-once terminal ledger joined to one randomized block authority."""

    __slots__ = ("_block", "_expected", "_records", "_finalized_records")

    def __init__(self, block: RandomizedBlockRecord) -> None:
        if not isinstance(block, RandomizedBlockRecord):
            raise TypeError("block must be a RandomizedBlockRecord")
        self._block = block
        self._expected = {row.session_id: row for row in block.assignments}
        self._records: dict[str, TerminalDispositionRecord] = {}
        self._finalized_records: tuple[TerminalDispositionRecord, ...] | None = None

    @property
    def block(self) -> RandomizedBlockRecord:
        return self._block

    @property
    def is_finalized(self) -> bool:
        return self._finalized_records is not None

    @property
    def records(self) -> tuple[TerminalDispositionRecord, ...]:
        return tuple(self._records[key] for key in sorted(self._records))

    def record(
        self, terminal: TerminalDispositionRecord
    ) -> TerminalDispositionRecord:
        if not isinstance(terminal, TerminalDispositionRecord):
            raise TypeError("terminal must be a TerminalDispositionRecord")
        expected_key_prefix = (self._block.protocol_run_id, self._block.block_id)
        if terminal.key[:2] != expected_key_prefix:
            raise ProtocolAuthorityError("terminal run/block key does not match authority")
        if terminal.study_phase != self._block.study_phase:
            raise ProtocolAuthorityError("terminal study phase does not match authority")
        if terminal.protocol_manifest_digest != self._block.protocol_manifest_digest:
            raise ProtocolAuthorityError(
                "terminal protocol manifest does not match authority"
            )
        if terminal.randomized_block_fingerprint != self._block.record_fingerprint:
            raise ProtocolAuthorityError(
                "terminal randomized-block fingerprint does not match authority"
            )
        if terminal.session_id not in self._expected:
            raise ProtocolAuthorityError("terminal session is not in randomized authority")

        existing = self._records.get(terminal.session_id)
        if existing is not None:
            if existing == terminal:
                return existing
            raise TerminalConflictError(
                "terminal key replayed with conflicting immutable content"
            )
        if self.is_finalized:
            raise TerminalConflictError("cannot append a new terminal after finalization")
        self._records[terminal.session_id] = terminal
        return terminal

    def finalize(self) -> tuple[TerminalDispositionRecord, ...]:
        if self._finalized_records is not None:
            return self._finalized_records
        expected = set(self._expected)
        supplied = set(self._records)
        missing = sorted(expected - supplied)
        extra = sorted(supplied - expected)
        if missing or extra or len(self._records) != BLOCK_SIZE:
            raise IncompleteTerminalLedgerError(
                "terminal ledger must join exactly to all 8 randomized sessions; "
                f"missing={missing}, extra={extra}, rows={len(self._records)}"
            )
        self._finalized_records = tuple(
            self._records[session_id] for session_id in sorted(expected)
        )
        return self._finalized_records

    @property
    def headline_eligible(self) -> bool:
        records = self._require_finalized()
        return not any(record.integrity_failure for record in records)

    @property
    def integrity_failure_sessions(self) -> tuple[str, ...]:
        records = self._require_finalized()
        return tuple(
            record.session_id for record in records if record.integrity_failure
        )

    def _require_finalized(self) -> tuple[TerminalDispositionRecord, ...]:
        if self._finalized_records is None:
            raise IncompleteTerminalLedgerError(
                "terminal ledger must be finalized before headline eligibility"
            )
        return self._finalized_records


__all__ = [
    "ALLOWED_SET_SIZE",
    "AssignmentRow",
    "BLOCK_SCHEMA_VERSION",
    "ClosedSchemaError",
    "DISPOSITION_SOURCES",
    "IncompleteTerminalLedgerError",
    "ProtocolAuthorityError",
    "RandomizedBlockRecord",
    "SOURCE_SUBTYPES",
    "TERMINAL_SCHEMA_VERSION",
    "TerminalConflictError",
    "TerminalDispositionRecord",
    "TerminalLedger",
    "canonical_assignment_engine_digest",
    "canonical_json",
    "canonical_sha256",
    "compute_assignment_policy_digest",
    "compute_randomness_commitment",
    "derive_allowed_set_index",
    "verify_block_membership",
    "verify_selection_proof",
]
