from __future__ import annotations

from collections import Counter
from dataclasses import FrozenInstanceError
from functools import lru_cache
import hashlib
import itertools
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


MODULE_DIR = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
ZERO_CALL_ROOT = REPOSITORY_ROOT / "zero_call"
sys.path.insert(0, str(MODULE_DIR))
sys.path.insert(0, str(ZERO_CALL_ROOT))

from protocol_authority import (  # noqa: E402
    AllowedSetArtifact,
    AssignmentRow,
    CANONICAL_ALLOWED_SET_VERSION,
    CANONICAL_ASSIGNMENT_ENGINE_VERSION,
    ClosedSchemaError,
    IncompleteTerminalLedgerError,
    ProtocolAuthorityError,
    RandomizedBlockRecord,
    SOURCE_SUBTYPES,
    TerminalConflictError,
    TerminalDispositionRecord,
    TerminalLedger,
    assignment_member_digest,
    canonical_assignment_engine_digest,
    canonical_json,
    canonical_sha256,
    compute_assignment_policy_digest,
    compute_randomness_commitment,
    derive_allowed_set_index,
    verify_block_membership,
    verify_selection_proof,
)
from binding_test.assignment import (  # noqa: E402
    CanonicalBlock,
    Session,
    audit_assignment_probabilities,
    enumerate_allowed_assignments,
)


DIGESTS = {character: character * 64 for character in "0123456789abcdef"}
ASSIGNMENT_ENGINE_SOURCE = ZERO_CALL_ROOT / "binding_test" / "assignment.py"
ASSIGNMENT_ENGINE_DIGEST = hashlib.sha256(
    ASSIGNMENT_ENGINE_SOURCE.read_bytes()
).hexdigest()
BASELINE_BY_SESSION = {
    "s0": "L",
    "s1": "L",
    "s2": "H",
    "s3": "H",
    "s4": "L",
    "s5": "L",
    "s6": "H",
    "s7": "H",
}
EXECUTION_ORDER_BY_SESSION = {
    "s0": 3,
    "s1": 0,
    "s2": 5,
    "s3": 2,
    "s4": 7,
    "s5": 1,
    "s6": 6,
    "s7": 4,
}
MATERIAL_BY_SCHEDULE = {
    "L": (DIGESTS["1"], DIGESTS["3"]),
    "H": (DIGESTS["2"], DIGESTS["4"]),
}


def _engine_candidates_for(
    baseline_items: tuple[tuple[str, str], ...],
) -> tuple[tuple[AssignmentRow, ...], ...]:
    baseline_by_session = dict(baseline_items)
    stratum = "test-fine-stratum"
    block = CanonicalBlock(
        block_id="block-0001",
        stratum=stratum,
        sessions=tuple(
            Session(
                session_id=session_id,
                stratum=stratum,
                baseline_choice=baseline_by_session[session_id],
            )
            for session_id in sorted(baseline_by_session)
        ),
    )
    allowed = enumerate_allowed_assignments(block)
    audit_assignment_probabilities(block, allowed).assert_canonical()
    return tuple(
        tuple(
            AssignmentRow(
                session_id=row.session_id,
                baseline_choice=row.baseline_choice,
                arm=row.arm,
                received_schedule=row.received_schedule,
                donor_session_id=row.donor_session_id,
                execution_order_index=EXECUTION_ORDER_BY_SESSION[row.session_id],
                schedule_digest=MATERIAL_BY_SCHEDULE[row.received_schedule][0],
                affordance_digest=MATERIAL_BY_SCHEDULE[row.received_schedule][1],
            )
            for row in assignment.sessions
        )
        for assignment in allowed
    )


@lru_cache(maxsize=1)
def _canonical_candidates() -> tuple[tuple[AssignmentRow, ...], ...]:
    return _engine_candidates_for(tuple(sorted(BASELINE_BY_SESSION.items())))


def _assignment_rows() -> tuple[AssignmentRow, ...]:
    return _canonical_candidates()[251]


def _rows_with_execution_order(
    execution_order: tuple[int, ...],
) -> tuple[AssignmentRow, ...]:
    if len(execution_order) != 8:
        raise ValueError("execution_order must contain eight indices")
    return tuple(
        AssignmentRow(
            **{
                **row.to_mapping(),
                "execution_order_index": execution_order[index],
            }
        )
        for index, row in enumerate(_assignment_rows())
    )


@lru_cache(maxsize=1)
def _allowed_set_artifact() -> AllowedSetArtifact:
    return AllowedSetArtifact(
        protocol_run_id="binding-confirmatory-v1",
        protocol_manifest_digest=DIGESTS["a"],
        block_id="block-0001",
        allowed_set_version=CANONICAL_ALLOWED_SET_VERSION,
        assignment_engine_version=CANONICAL_ASSIGNMENT_ENGINE_VERSION,
        assignment_engine_digest=ASSIGNMENT_ENGINE_DIGEST,
        candidates=_canonical_candidates(),
    )


def _artifact_with(
    *,
    candidates: tuple[tuple[AssignmentRow, ...], ...] | None = None,
    **overrides: object,
) -> AllowedSetArtifact:
    source = _allowed_set_artifact()
    values: dict[str, object] = {
        "protocol_run_id": source.protocol_run_id,
        "protocol_manifest_digest": source.protocol_manifest_digest,
        "block_id": source.block_id,
        "allowed_set_version": source.allowed_set_version,
        "assignment_engine_version": source.assignment_engine_version,
        "assignment_engine_digest": source.assignment_engine_digest,
        "candidates": source.candidates if candidates is None else candidates,
    }
    values.update(overrides)
    return AllowedSetArtifact(**values)  # type: ignore[arg-type]


def _block(**overrides: object) -> RandomizedBlockRecord:
    artifact = _allowed_set_artifact()
    values: dict[str, object] = {
        "study_phase": "confirmatory",
        "protocol_run_id": "binding-confirmatory-v1",
        "protocol_manifest_digest": DIGESTS["a"],
        "block_id": "block-0001",
        "macro_cell_id": (
            "model_snapshot=model-a@2026-08-08|"
            "target_family=work_score_allocation"
        ),
        "model_snapshot": "model-a@2026-08-08",
        "target_family": "work_score_allocation",
        "fine_stratum": "pair_id=WS01|dose=active|variant_id=CB00",
        "pair_id": "WS01",
        "dose": "active",
        "variant_id": "CB00",
        "allowed_set_version": "canonical-donor-aware-576-v1",
        "allowed_set_digest": artifact.allowed_set_digest,
        "allowed_set_size": 576,
        "allowed_set_index": 251,
        "assignment_probability_numerator": 1,
        "assignment_probability_denominator": 576,
        "assignment_policy_digest": compute_assignment_policy_digest(artifact),
        "assignment_engine_version": artifact.assignment_engine_version,
        "assignment_engine_digest": artifact.assignment_engine_digest,
        "allowed_set_member_digest": artifact.member_digest_at(251),
        "randomness_commitment": DIGESTS["d"],
        "assignments": _assignment_rows(),
    }
    values.update(overrides)
    return RandomizedBlockRecord(**values)  # type: ignore[arg-type]


def _terminal(
    session_id: str,
    block: RandomizedBlockRecord,
    *,
    terminal_disposition: str = "H",
    disposition_source: str = "followup_choice",
    failure_subtype: str = "none",
    followup_strict_valid: bool | None = True,
    followup_semantic_valid: bool | None = True,
    integrity_failure: bool = False,
    **overrides: object,
) -> TerminalDispositionRecord:
    values: dict[str, object] = {
        "study_phase": block.study_phase,
        "protocol_run_id": block.protocol_run_id,
        "protocol_manifest_digest": block.protocol_manifest_digest,
        "block_id": block.block_id,
        "session_id": session_id,
        "randomized_block_fingerprint": block.record_fingerprint,
        "terminal_disposition": terminal_disposition,
        "disposition_source": disposition_source,
        "failure_subtype": failure_subtype,
        "followup_strict_valid": followup_strict_valid,
        "followup_semantic_valid": followup_semantic_valid,
        "integrity_failure": integrity_failure,
    }
    values.update(overrides)
    return TerminalDispositionRecord(**values)  # type: ignore[arg-type]


def _successful_terminals(
    block: RandomizedBlockRecord,
) -> tuple[TerminalDispositionRecord, ...]:
    return tuple(
        _terminal(
            row.session_id,
            block,
            terminal_disposition=row.baseline_choice,
            followup_strict_valid=(row.execution_order_index % 2 == 0),
        )
        for row in block.assignments
    )


class CanonicalAuthorityTests(unittest.TestCase):
    def test_canonical_json_and_sha_are_stable(self) -> None:
        left = {"z": [3, 2, 1], "a": {"x": True}}
        right = {"a": {"x": True}, "z": [3, 2, 1]}
        self.assertEqual(canonical_json(left), canonical_json(right))
        self.assertEqual(canonical_sha256(left), canonical_sha256(right))
        self.assertRegex(canonical_sha256(left), r"^[0-9a-f]{64}$")
        with self.assertRaises(ValueError):
            canonical_json({"bad": float("nan")})

    def test_assignment_row_is_frozen_and_loader_is_closed(self) -> None:
        row = _assignment_rows()[0]
        self.assertEqual(AssignmentRow.from_mapping(row.to_mapping()), row)
        with self.assertRaises(FrozenInstanceError):
            row.arm = "yoke"  # type: ignore[misc]
        missing = row.to_mapping()
        missing.pop("arm")
        with self.assertRaises(ClosedSchemaError):
            AssignmentRow.from_mapping(missing)
        with self.assertRaises(ClosedSchemaError):
            AssignmentRow.from_mapping({**row.to_mapping(), "extra": True})
        with self.assertRaises(ProtocolAuthorityError):
            AssignmentRow.from_mapping(
                {**row.to_mapping(), "execution_order_index": True}
            )

    def test_block_roundtrip_fingerprint_and_deep_immutability(self) -> None:
        block = _block()
        self.assertRegex(block.record_fingerprint, r"^[0-9a-f]{64}$")
        decoded = json.loads(block.to_json())
        self.assertEqual(RandomizedBlockRecord.from_mapping(decoded), block)
        self.assertEqual(len(block.assignments), 8)
        with self.assertRaises(FrozenInstanceError):
            block.block_id = "forged"  # type: ignore[misc]
        decoded["assignments"][0]["arm"] = "yoke"
        self.assertEqual(block.assignments[0].arm, "self")

    def test_block_loader_rejects_schema_and_fingerprint_drift(self) -> None:
        record = _block().to_mapping()
        missing = dict(record)
        missing.pop("pair_id")
        with self.assertRaises(ClosedSchemaError):
            RandomizedBlockRecord.from_mapping(missing)
        with self.assertRaises(ClosedSchemaError):
            RandomizedBlockRecord.from_mapping({**record, "extra": 1})
        forged = json.loads(canonical_json(record))
        forged["allowed_set_index"] = 7
        with self.assertRaisesRegex(ProtocolAuthorityError, "fingerprint mismatch"):
            RandomizedBlockRecord.from_mapping(forged)

    def test_block_binds_cell_stratum_allowed_set_and_probability(self) -> None:
        for override in (
            {"study_phase": "calibration"},
            {"macro_cell_id": "model_snapshot=wrong|target_family=work_score_allocation"},
            {"fine_stratum": "pair_id=WS02|dose=active|variant_id=CB00"},
            {"allowed_set_size": 575},
            {"allowed_set_index": 576},
            {"allowed_set_index": True},
            {"assignment_probability_numerator": 2},
            {"assignment_probability_denominator": 575},
            {"allowed_set_digest": "B" * 64},
            {"assignment_engine_version": ""},
            {"assignment_engine_digest": "E" * 64},
            {"allowed_set_member_digest": "not-a-digest"},
            {"randomness_commitment": "not-a-digest"},
        ):
            with self.subTest(override=override):
                with self.assertRaises(ProtocolAuthorityError):
                    _block(**override)

    def test_block_rejects_noncanonical_assignment_authority(self) -> None:
        rows = list(_assignment_rows())
        cases: list[tuple[str, tuple[AssignmentRow, ...]]] = []
        cases.append(("row count", tuple(rows[:-1])))
        cases.append(("ordering", tuple(reversed(rows))))
        cases.append(("duplicate session", tuple([rows[0], *rows[1:-1], rows[0]])))
        cases.append(
            (
                "execution order",
                tuple(
                    AssignmentRow(
                        **{
                            **row.to_mapping(),
                            "execution_order_index": 0,
                        }
                    )
                    for row in rows
                ),
            )
        )
        yoke_index = next(index for index, row in enumerate(rows) if row.arm == "yoke")
        forged_yoke = AssignmentRow(
            **{**rows[yoke_index].to_mapping(), "donor_session_id": "not-a-donor"}
        )
        cases.append(
            (
                "donor",
                tuple([*rows[:yoke_index], forged_yoke, *rows[yoke_index + 1 :]]),
            )
        )
        forged_digest = AssignmentRow(
            **{**rows[yoke_index].to_mapping(), "schedule_digest": DIGESTS["f"]}
        )
        cases.append(
            (
                "schedule digest",
                tuple([*rows[:yoke_index], forged_digest, *rows[yoke_index + 1 :]]),
            )
        )
        for label, authority in cases:
            with self.subTest(label=label):
                with self.assertRaises(ProtocolAuthorityError):
                    _block(assignments=authority)


class AllowedSetMembershipTests(unittest.TestCase):
    def test_closed_projection_does_not_trust_a_preloaded_engine_module(self) -> None:
        source = _allowed_set_artifact()
        values = {
            "protocol_run_id": "module-isolation-run",
            "protocol_manifest_digest": source.protocol_manifest_digest,
            "block_id": source.block_id,
            "allowed_set_version": source.allowed_set_version,
            "assignment_engine_version": source.assignment_engine_version,
            "assignment_engine_digest": source.assignment_engine_digest,
            "candidates": source.candidates,
        }
        with patch("builtins.__import__", side_effect=AssertionError("dynamic import")):
            rebuilt = AllowedSetArtifact(**values)
        self.assertEqual(rebuilt.candidates, source.candidates)

    def test_artifact_is_exact_engine_projection_with_canonical_marginals(self) -> None:
        artifact = _allowed_set_artifact()
        self.assertEqual(artifact.candidates, _canonical_candidates())
        self.assertEqual(canonical_assignment_engine_digest(), ASSIGNMENT_ENGINE_DIGEST)
        self.assertEqual(
            artifact.assignment_engine_version,
            CANONICAL_ASSIGNMENT_ENGINE_VERSION,
        )
        for session_id in sorted(BASELINE_BY_SESSION):
            rows = tuple(
                candidate[int(session_id[1:])] for candidate in artifact.candidates
            )
            self.assertEqual(Counter(row.arm for row in rows), {"self": 288, "yoke": 288})
            yoke_rows = tuple(row for row in rows if row.arm == "yoke")
            self.assertEqual(
                Counter(row.received_schedule for row in yoke_rows),
                {"L": 144, "H": 144},
            )
            self.assertEqual(
                Counter(
                    row.received_schedule == row.baseline_choice for row in yoke_rows
                ),
                {True: 144, False: 144},
            )

    def test_artifact_is_closed_roundtrippable_and_domain_bound(self) -> None:
        artifact = _allowed_set_artifact()
        self.assertEqual(len(artifact.candidates), 576)
        self.assertEqual(len(set(artifact.member_digests)), 576)
        self.assertEqual(
            AllowedSetArtifact.from_mapping(json.loads(artifact.to_json())),
            artifact,
        )
        missing = artifact.to_mapping()
        missing.pop("assignment_engine_version")
        with self.assertRaises(ClosedSchemaError):
            AllowedSetArtifact.from_mapping(missing)
        with self.assertRaises(ClosedSchemaError):
            AllowedSetArtifact.from_mapping(
                {**artifact.to_mapping(), "uncommitted_field": True}
            )
        with self.assertRaises(ProtocolAuthorityError):
            AllowedSetArtifact.from_mapping(
                {**artifact.to_mapping(), "allowed_set_digest": ""}
            )

    def test_valid_record_proves_full_projection_membership(self) -> None:
        artifact = _allowed_set_artifact()
        block = _block()
        candidate = verify_block_membership(block, artifact)
        self.assertEqual(candidate, artifact.candidates[block.allowed_set_index])
        self.assertEqual(
            block.allowed_set_member_digest,
            assignment_member_digest(candidate),
        )

    def test_candidate_tamper_reorder_and_context_drift_fail_closed(self) -> None:
        artifact = _allowed_set_artifact()
        tampered = json.loads(artifact.to_json())
        for row in tampered["candidates"][0]:
            if row["received_schedule"] == "L":
                row["affordance_digest"] = DIGESTS["5"]
        with self.assertRaisesRegex(ProtocolAuthorityError, "fixed schedule material"):
            AllowedSetArtifact.from_mapping(tampered)

        reordered_mapping = json.loads(artifact.to_json())
        reordered_mapping["candidates"][0], reordered_mapping["candidates"][1] = (
            reordered_mapping["candidates"][1],
            reordered_mapping["candidates"][0],
        )
        with self.assertRaisesRegex(ProtocolAuthorityError, "exact canonical set/order"):
            AllowedSetArtifact.from_mapping(reordered_mapping)

        reordered_candidates = list(artifact.candidates)
        reordered_candidates[0], reordered_candidates[1] = (
            reordered_candidates[1],
            reordered_candidates[0],
        )
        with self.assertRaisesRegex(ProtocolAuthorityError, "exact canonical set/order"):
            _artifact_with(candidates=tuple(reordered_candidates))

        stale_context_digest = json.loads(artifact.to_json())
        stale_context_digest["protocol_run_id"] = "different-run"
        with self.assertRaisesRegex(ProtocolAuthorityError, "aggregate digest"):
            AllowedSetArtifact.from_mapping(stale_context_digest)

    def test_missing_and_substituted_candidates_are_rejected_with_fresh_digest(self) -> None:
        artifact = _allowed_set_artifact()
        with self.assertRaisesRegex(ProtocolAuthorityError, "exactly 576"):
            _artifact_with(candidates=artifact.candidates[:-1])

        substituted = list(artifact.candidates)
        substituted[100] = substituted[101]
        with self.assertRaisesRegex(
            ProtocolAuthorityError,
            "288/288|144/144|576 unique|exact canonical set/order",
        ):
            _artifact_with(candidates=tuple(substituted))

    def test_fixed_baseline_execution_and_material_fields_cannot_drift(self) -> None:
        artifact = _allowed_set_artifact()

        alternate_baselines = dict(BASELINE_BY_SESSION)
        alternate_baselines["s0"], alternate_baselines["s2"] = (
            alternate_baselines["s2"],
            alternate_baselines["s0"],
        )
        baseline_drift = list(artifact.candidates)
        baseline_drift[100] = _engine_candidates_for(
            tuple(sorted(alternate_baselines.items()))
        )[100]

        execution_drift = list(artifact.candidates)
        candidate = list(execution_drift[100])
        left = candidate[0]
        right = candidate[1]
        candidate[0] = AssignmentRow(
            **{
                **left.to_mapping(),
                "execution_order_index": right.execution_order_index,
            }
        )
        candidate[1] = AssignmentRow(
            **{
                **right.to_mapping(),
                "execution_order_index": left.execution_order_index,
            }
        )
        execution_drift[100] = tuple(candidate)

        material_drift = list(artifact.candidates)
        material_drift[100] = tuple(
            AssignmentRow(
                **{
                    **row.to_mapping(),
                    "schedule_digest": (
                        DIGESTS["5"]
                        if row.received_schedule == "L"
                        else row.schedule_digest
                    ),
                    "affordance_digest": (
                        DIGESTS["6"]
                        if row.received_schedule == "L"
                        else row.affordance_digest
                    ),
                }
            )
            for row in material_drift[100]
        )

        for label, candidates, message in (
            ("baseline", baseline_drift, "fixed per-session baseline_choice"),
            ("execution", execution_drift, "fixed per-session execution_order_index"),
            ("material", material_drift, "fixed schedule material"),
        ):
            with self.subTest(label=label):
                with self.assertRaisesRegex(ProtocolAuthorityError, message):
                    _artifact_with(candidates=tuple(candidates))

    def test_per_session_arm_marginal_failure_is_rejected(self) -> None:
        artifact = _allowed_set_artifact()
        fixed_assignment = tuple(artifact.candidates[0] for _ in range(576))
        with self.assertRaisesRegex(ProtocolAuthorityError, "288/288 self/yoke"):
            _artifact_with(candidates=fixed_assignment)

    def test_structurally_valid_execution_permutation_fake_set_is_rejected(self) -> None:
        fake_candidates = tuple(
            _rows_with_execution_order(order)
            for order in itertools.islice(itertools.permutations(range(8)), 576)
        )
        self.assertEqual(len(fake_candidates), 576)
        self.assertEqual(len(set(fake_candidates)), 576)
        with self.assertRaisesRegex(
            ProtocolAuthorityError,
            "fixed per-session execution_order_index",
        ):
            _artifact_with(candidates=fake_candidates)

    def test_index_projection_and_nonmember_mismatches_fail_closed(self) -> None:
        artifact = _allowed_set_artifact()
        wrong_projection = _block(
            allowed_set_index=0,
            allowed_set_member_digest=artifact.member_digest_at(0),
            assignments=artifact.candidates[1],
        )
        with self.assertRaisesRegex(ProtocolAuthorityError, "full candidate projection"):
            verify_block_membership(wrong_projection, artifact)

        nonmember = _rows_with_execution_order((7, 6, 5, 4, 3, 2, 1, 0))
        nonmember_digest = assignment_member_digest(nonmember)
        self.assertNotIn(nonmember_digest, artifact.member_digests)
        forged_nonmember = _block(
            assignments=nonmember,
            allowed_set_member_digest=nonmember_digest,
        )
        with self.assertRaisesRegex(ProtocolAuthorityError, "member_digest"):
            verify_block_membership(forged_nonmember, artifact)

    def test_engine_and_artifact_context_must_match_exactly(self) -> None:
        artifact = _allowed_set_artifact()
        for forged in (
            _block(assignment_engine_version="canonical-assignment-engine-v2"),
            _block(assignment_engine_digest=DIGESTS["f"]),
        ):
            with self.subTest(forged=forged.assignment_engine_version):
                with self.assertRaisesRegex(ProtocolAuthorityError, "assignment_engine"):
                    verify_block_membership(forged, artifact)
        other_run_artifact = _artifact_with(protocol_run_id="different-run")
        with self.assertRaisesRegex(ProtocolAuthorityError, "protocol_run_id"):
            verify_block_membership(_block(), other_run_artifact)

    def test_assignment_policy_digest_is_derived_and_membership_bound(self) -> None:
        artifact = _allowed_set_artifact()
        expected = compute_assignment_policy_digest(artifact)
        self.assertEqual(_block().assignment_policy_digest, expected)
        wrong_policy = _block(assignment_policy_digest=DIGESTS["c"])
        with self.assertRaisesRegex(ProtocolAuthorityError, "assignment_policy_digest"):
            verify_block_membership(wrong_policy, artifact)
        other_context = _artifact_with(protocol_run_id="policy-context-run")
        self.assertNotEqual(
            compute_assignment_policy_digest(other_context),
            expected,
        )

    def test_committed_entropy_reproduces_index_but_not_entropy_quality(self) -> None:
        artifact = _allowed_set_artifact()
        reveal = "ab" * 32
        selected_index = derive_allowed_set_index(reveal, artifact)
        selected = artifact.candidates[selected_index]
        block = _block(
            allowed_set_index=selected_index,
            allowed_set_member_digest=artifact.member_digest_at(selected_index),
            assignments=selected,
            randomness_commitment=compute_randomness_commitment(reveal),
        )
        self.assertEqual(
            verify_selection_proof(block, artifact, reveal),
            selected_index,
        )
        with self.assertRaisesRegex(ProtocolAuthorityError, "commitment"):
            verify_selection_proof(block, artifact, "cd" * 32)

        other_index = (selected_index + 1) % 576
        wrong_selection = _block(
            allowed_set_index=other_index,
            allowed_set_member_digest=artifact.member_digest_at(other_index),
            assignments=artifact.candidates[other_index],
            randomness_commitment=compute_randomness_commitment(reveal),
        )
        with self.assertRaisesRegex(ProtocolAuthorityError, "deterministic selection"):
            verify_selection_proof(wrong_selection, artifact, reveal)
        with self.assertRaisesRegex(ProtocolAuthorityError, "64 lowercase hex"):
            compute_randomness_commitment("AB" * 32)


class TerminalDispositionTests(unittest.TestCase):
    def test_every_source_subtype_pair_has_a_valid_closed_mapping(self) -> None:
        block = _block()
        for source, subtypes in SOURCE_SUBTYPES.items():
            for subtype in subtypes:
                with self.subTest(source=source, subtype=subtype):
                    if source == "followup_choice":
                        record = _terminal("s0", block)
                    elif source == "followup_unavailable":
                        record = _terminal(
                            "s0",
                            block,
                            terminal_disposition="U",
                            disposition_source=source,
                            failure_subtype=subtype,
                            followup_strict_valid=False,
                            followup_semantic_valid=False,
                        )
                    elif source == "local_protocol_abort":
                        record = _terminal(
                            "s0",
                            block,
                            terminal_disposition="U",
                            disposition_source=source,
                            failure_subtype=subtype,
                            followup_strict_valid=None,
                            followup_semantic_valid=None,
                            integrity_failure=True,
                        )
                    else:
                        record = _terminal(
                            "s0",
                            block,
                            terminal_disposition="U",
                            disposition_source=source,
                            failure_subtype=subtype,
                            followup_strict_valid=None,
                            followup_semantic_valid=None,
                        )
                    self.assertEqual(
                        TerminalDispositionRecord.from_mapping(record.to_mapping()),
                        record,
                    )

    def test_terminal_schema_rejects_impossible_source_disposition_pairs(self) -> None:
        block = _block()
        invalid = (
            {"terminal_disposition": "U"},
            {
                "terminal_disposition": "H",
                "disposition_source": "execution_failure",
                "failure_subtype": "timeout",
                "followup_strict_valid": None,
                "followup_semantic_valid": None,
            },
            {
                "terminal_disposition": "U",
                "disposition_source": "followup_unavailable",
                "failure_subtype": "timeout",
                "followup_strict_valid": False,
                "followup_semantic_valid": False,
            },
            {
                "terminal_disposition": "U",
                "disposition_source": "followup_unavailable",
                "failure_subtype": "explicit_refusal",
                "followup_strict_valid": None,
                "followup_semantic_valid": None,
            },
            {"followup_semantic_valid": False},
            {"integrity_failure": True},
        )
        for override in invalid:
            with self.subTest(override=override):
                with self.assertRaises(ProtocolAuthorityError):
                    _terminal("s0", block, **override)

    def test_local_abort_requires_and_sets_integrity_failure(self) -> None:
        block = _block()
        with self.assertRaises(ProtocolAuthorityError):
            _terminal(
                "s0",
                block,
                terminal_disposition="U",
                disposition_source="local_protocol_abort",
                failure_subtype="controller_abort",
                followup_strict_valid=None,
                followup_semantic_valid=None,
            )
        valid = _terminal(
            "s0",
            block,
            terminal_disposition="U",
            disposition_source="local_protocol_abort",
            failure_subtype="controller_abort",
            followup_strict_valid=None,
            followup_semantic_valid=None,
            integrity_failure=True,
        )
        self.assertTrue(valid.integrity_failure)

    def test_terminal_loader_is_closed_and_fingerprint_bound(self) -> None:
        record = _terminal("s0", _block()).to_mapping()
        missing = dict(record)
        missing.pop("failure_subtype")
        with self.assertRaises(ClosedSchemaError):
            TerminalDispositionRecord.from_mapping(missing)
        with self.assertRaises(ClosedSchemaError):
            TerminalDispositionRecord.from_mapping({**record, "raw_text": "secret"})
        forged = dict(record)
        forged["terminal_disposition"] = "L"
        with self.assertRaisesRegex(ProtocolAuthorityError, "fingerprint mismatch"):
            TerminalDispositionRecord.from_mapping(forged)


class TerminalLedgerTests(unittest.TestCase):
    def test_exact_join_identical_replay_and_idempotent_finalize(self) -> None:
        block = _block()
        ledger = TerminalLedger(block)
        records = _successful_terminals(block)
        for record in records:
            self.assertIs(ledger.record(record), record)
            self.assertEqual(ledger.record(record), record)
        first = ledger.finalize()
        self.assertEqual(len(first), 8)
        self.assertIs(first, ledger.finalize())
        self.assertTrue(ledger.headline_eligible)
        self.assertEqual(ledger.integrity_failure_sessions, ())
        self.assertEqual(ledger.record(records[0]), records[0])

    def test_conflicting_replay_is_fatal(self) -> None:
        block = _block()
        ledger = TerminalLedger(block)
        original = _terminal("s0", block, terminal_disposition="H")
        conflict = _terminal("s0", block, terminal_disposition="L")
        ledger.record(original)
        with self.assertRaises(TerminalConflictError):
            ledger.record(conflict)

    def test_extra_and_authority_mismatch_are_rejected(self) -> None:
        block = _block()
        ledger = TerminalLedger(block)
        with self.assertRaisesRegex(ProtocolAuthorityError, "not in randomized"):
            ledger.record(_terminal("not-randomized", block))
        wrong_run = _terminal("s0", block, protocol_run_id="wrong-run")
        with self.assertRaisesRegex(ProtocolAuthorityError, "run/block"):
            ledger.record(wrong_run)
        wrong_digest = _terminal(
            "s0", block, protocol_manifest_digest=DIGESTS["e"]
        )
        with self.assertRaisesRegex(ProtocolAuthorityError, "manifest"):
            ledger.record(wrong_digest)
        other_block = _block(block_id="block-0002")
        with self.assertRaisesRegex(ProtocolAuthorityError, "fingerprint"):
            ledger.record(
                _terminal(
                    "s0",
                    block,
                    randomized_block_fingerprint=other_block.record_fingerprint,
                )
            )

    def test_finalize_requires_exactly_all_eight_rows(self) -> None:
        block = _block()
        ledger = TerminalLedger(block)
        for record in _successful_terminals(block)[:-1]:
            ledger.record(record)
        with self.assertRaisesRegex(IncompleteTerminalLedgerError, "exactly.*8"):
            ledger.finalize()
        with self.assertRaises(IncompleteTerminalLedgerError):
            _ = ledger.headline_eligible

    def test_local_abort_retains_row_but_invalidates_headline(self) -> None:
        block = _block()
        ledger = TerminalLedger(block)
        records = list(_successful_terminals(block))
        records[3] = _terminal(
            records[3].session_id,
            block,
            terminal_disposition="U",
            disposition_source="local_protocol_abort",
            failure_subtype="schedule_integrity_mismatch",
            followup_strict_valid=None,
            followup_semantic_valid=None,
            integrity_failure=True,
        )
        for record in records:
            ledger.record(record)
        self.assertEqual(len(ledger.finalize()), 8)
        self.assertFalse(ledger.headline_eligible)
        self.assertEqual(ledger.integrity_failure_sessions, ("s3",))

    def test_no_new_terminal_can_be_added_after_finalization(self) -> None:
        block = _block()
        ledger = TerminalLedger(block)
        records = _successful_terminals(block)
        for record in records:
            ledger.record(record)
        ledger.finalize()
        with self.assertRaises(TerminalConflictError):
            ledger.record(_terminal("s0", block, terminal_disposition="L"))


if __name__ == "__main__":
    unittest.main()
