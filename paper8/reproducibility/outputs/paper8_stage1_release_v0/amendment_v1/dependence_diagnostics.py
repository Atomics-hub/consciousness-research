"""Deterministic, non-gating dependence diagnostics for the Binding Test.

This module is deliberately separate from the sealed zero-call certification.
It simulates a small, declared set of dependence, terminal-failure, and block-
formation stresses.  It cannot certify a sample size or authorize collection.

Only aggregate diagnostics are returned.  No provider client, credential,
network operation, runtime transcript, or empirical model response is used.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any, Iterable, Mapping

import numpy as np


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
ZERO_CALL_ROOT = REPOSITORY_ROOT / "zero_call"
if str(ZERO_CALL_ROOT) not in sys.path:
    sys.path.insert(0, str(ZERO_CALL_ROOT))

from binding_test.assignment import (  # noqa: E402
    CANONICAL_ALLOWED_ASSIGNMENT_COUNT,
    CanonicalBlock,
    Session,
    enumerate_allowed_assignments,
    form_canonical_blocks,
)
from binding_test.confirmatory import _student_t_quantile  # noqa: E402
from protocol_authority import SOURCE_SUBTYPES  # noqa: E402


MASTER_SEED = 20260808
SCHEMA_VERSION = "binding-test-dependence-diagnostic-v1"
STATUS = "NON_GATING_SYNTHETIC_SCREEN"
GATE_EFFECT = "none"
CATEGORIES = ("L", "H", "U")
ARMS = ("self", "yoke")
SCHEDULES = ("L", "H")
MACRO_CELL_COUNT = 4
FINE_STRATA_PER_MACRO_CELL = 24
BLOCKS_PER_MACRO_CELL = 384
BLOCKS_PER_FINE_STRATUM = 16
TOTAL_FINE_STRATA = MACRO_CELL_COUNT * FINE_STRATA_PER_MACRO_CELL
TOTAL_BLOCKS = MACRO_CELL_COUNT * BLOCKS_PER_MACRO_CELL
SESSIONS_PER_BLOCK = 8
SESSIONS_PER_ARM = 4
OUTCOME_BATCH_COUNT = 4
OUTCOME_BATCH_BLOCKS_PER_FINE = 4
FORMATION_ATTEMPT_BATCH_SIZE = 32
FORMATION_TARGET_PER_CHOICE = 4 * BLOCKS_PER_FINE_STRATUM
FOLLOWUP_UNAVAILABILITY = 0.10
ALPHA = 0.05
POSITIVE_THRESHOLD = 0.05
EQUIVALENCE_MARGINS = (0.05, 0.05, 0.02)
BOUNDARY_TOLERANCE = 1e-12
MONTE_CARLO_CONFIDENCE = 0.95
DEFAULT_OUTCOME_REPLICATES = 1_000
DEFAULT_FORMATION_REPLICATES = 2_000

FORMATION_CAPS: dict[float, int] = {0.10: 1024, 0.30: 331, 0.50: 194}
FORMATION_PROFILES = ("independent", "provider_batch")

# Each tuple is (H/L reallocation amplitude, U amplitude, failure amplitude).
# H/L and U signs are independent.  For a base q=(L,H,U), a level contributes
# (-a*S_HL - b*S_U/2, +a*S_HL - b*S_U/2, +b*S_U).
DEPENDENCE_AMPLITUDES: dict[str, tuple[float, float, float]] = {
    "provider": (0.015, 0.010, 0.003),
    "batch": (0.025, 0.020, 0.005),
    "block": (0.040, 0.030, 0.007),
    "donor_pair": (0.040, 0.020, 0.005),
}
DEPENDENCE_PROFILES: dict[str, tuple[str, ...]] = {
    "independent": (),
    "donor_only": ("donor_pair",),
    "shared_shocks": ("provider", "batch", "block"),
    "joint": ("provider", "batch", "block", "donor_pair"),
}

SCENARIO_PROBABILITIES: dict[str, dict[str, tuple[float, float, float]]] = {
    "null": {
        "self": (0.45, 0.45, FOLLOWUP_UNAVAILABILITY),
        "yoke": (0.45, 0.45, FOLLOWUP_UNAVAILABILITY),
    },
    "positive_15": {
        "self": (0.30, 0.60, FOLLOWUP_UNAVAILABILITY),
        "yoke": (0.45, 0.45, FOLLOWUP_UNAVAILABILITY),
    },
    "positive_boundary": {
        "self": (0.40, 0.50, FOLLOWUP_UNAVAILABILITY),
        "yoke": (0.45, 0.45, FOLLOWUP_UNAVAILABILITY),
    },
}

FAILURE_PROFILES: dict[str, dict[str, dict[str, float]]] = {
    "none": {
        "self": {"L": 0.0, "H": 0.0},
        "yoke": {"L": 0.0, "H": 0.0},
    },
    "symmetric": {
        "self": {"L": 0.05, "H": 0.05},
        "yoke": {"L": 0.05, "H": 0.05},
    },
    "differential": {
        "self": {"L": 0.06, "H": 0.08},
        "yoke": {"L": 0.04, "H": 0.05},
    },
}

OUTCOME_PROFILES: tuple[tuple[str, str, str, str], ...] = (
    ("positive15_independent_none", "positive_15", "independent", "none"),
    ("positive15_donor_symmetric", "positive_15", "donor_only", "symmetric"),
    ("positive15_shared_symmetric", "positive_15", "shared_shocks", "symmetric"),
    ("positive15_joint_symmetric", "positive_15", "joint", "symmetric"),
    ("positive15_joint_differential", "positive_15", "joint", "differential"),
    ("null_joint_symmetric", "null", "joint", "symmetric"),
    ("null_joint_differential", "null", "joint", "differential"),
    ("boundary_joint_symmetric", "positive_boundary", "joint", "symmetric"),
)

CLAIM_CEILING = (
    "Seeded, non-gating sensitivity results under the eight declared synthetic "
    "dependence/failure profiles and two block-formation profiles only. They "
    "may flag sensitivity of the complete-block B=384 benchmark but cannot "
    "estimate provider dependence, validate the unamended terminal-row schema "
    "or state machine, certify or rescue B=384, authorize collection or spend, "
    "or support mechanism, latent-choice, preference, welfare, or population-"
    "generalization claims."
)


@dataclass(frozen=True, slots=True)
class TerminalRecord:
    """One synthetic terminal disposition from one randomized session."""

    session_id: str
    arm: str
    received_schedule: str
    donor_session_id: str
    category: str
    disposition_source: str
    failure_subtype: str


@dataclass(frozen=True, slots=True)
class AssignmentTable:
    arm_self: np.ndarray
    schedule_high: np.ndarray
    pair_slot: np.ndarray
    donor_index: np.ndarray
    self_index: np.ndarray
    yoke_index: np.ndarray
    session_ids: tuple[str, ...]
    donor_ids: tuple[tuple[str, ...], ...]
    digest: str


def _derived_seed(*parts: object) -> int:
    material = "|".join(("binding-dependence-diagnostic-v1", *(str(x) for x in parts)))
    return int.from_bytes(hashlib.sha256(material.encode("utf-8")).digest()[:16], "big")


def _rng(*parts: object) -> np.random.Generator:
    return np.random.Generator(np.random.PCG64(_derived_seed(MASTER_SEED, *parts)))


def _sign(rng: np.random.Generator, size: int | tuple[int, ...] | None = None) -> np.ndarray | float:
    draw = rng.integers(0, 2, size=size, dtype=np.int8)
    value = draw.astype(np.float64) * 2.0 - 1.0 if isinstance(draw, np.ndarray) else float(draw * 2 - 1)
    return value


@lru_cache(maxsize=1)
def assignment_table() -> AssignmentTable:
    sessions = tuple(
        Session(
            session_id=f"session-{index}",
            stratum="synthetic-fine-stratum",
            baseline_choice="L" if index < 4 else "H",
        )
        for index in range(SESSIONS_PER_BLOCK)
    )
    block = CanonicalBlock(
        block_id="synthetic-canonical-block",
        stratum="synthetic-fine-stratum",
        sessions=sessions,
    )
    allowed = enumerate_allowed_assignments(block)
    if len(allowed) != CANONICAL_ALLOWED_ASSIGNMENT_COUNT:
        raise AssertionError("canonical assignment enumeration did not return 576 rows")

    ids = tuple(session.session_id for session in sessions)
    id_index = {session_id: index for index, session_id in enumerate(ids)}
    arm_self = np.empty((len(allowed), SESSIONS_PER_BLOCK), dtype=bool)
    schedule_high = np.empty_like(arm_self)
    pair_slot = np.empty((len(allowed), SESSIONS_PER_BLOCK), dtype=np.int8)
    donor_index = np.empty((len(allowed), SESSIONS_PER_BLOCK), dtype=np.int8)
    self_index = np.empty((len(allowed), SESSIONS_PER_ARM), dtype=np.int8)
    yoke_index = np.empty_like(self_index)
    donor_ids: list[tuple[str, ...]] = []
    serializable: list[list[tuple[object, ...]]] = []

    for assignment_index, assignment in enumerate(allowed):
        rows = tuple(assignment.sessions)
        self_donors = tuple(sorted(row.session_id for row in rows if row.arm == "self"))
        slot_for_donor = {donor: slot for slot, donor in enumerate(self_donors)}
        donor_ids.append(self_donors)
        serializable.append([])
        for row_index, row in enumerate(rows):
            arm_self[assignment_index, row_index] = row.arm == "self"
            schedule_high[assignment_index, row_index] = row.received_schedule == "H"
            pair_slot[assignment_index, row_index] = slot_for_donor[row.donor_session_id]
            donor_index[assignment_index, row_index] = id_index[row.donor_session_id]
            serializable[-1].append(
                (
                    row.session_id,
                    row.baseline_choice,
                    row.arm,
                    row.received_schedule,
                    row.donor_session_id,
                )
            )
        for slot, donor in enumerate(self_donors):
            members = [
                row_index
                for row_index, row in enumerate(rows)
                if row.donor_session_id == donor
            ]
            if len(members) != 2:
                raise AssertionError("each donor pair must contain one self and one yoke row")
            self_member = [index for index in members if rows[index].arm == "self"]
            yoke_member = [index for index in members if rows[index].arm == "yoke"]
            if len(self_member) != 1 or len(yoke_member) != 1:
                raise AssertionError("donor pair arm composition is malformed")
            self_index[assignment_index, slot] = self_member[0]
            yoke_index[assignment_index, slot] = yoke_member[0]

    encoded = json.dumps(serializable, sort_keys=True, separators=(",", ":"))
    for array in (arm_self, schedule_high, pair_slot, donor_index, self_index, yoke_index):
        array.setflags(write=False)
    return AssignmentTable(
        arm_self=arm_self,
        schedule_high=schedule_high,
        pair_slot=pair_slot,
        donor_index=donor_index,
        self_index=self_index,
        yoke_index=yoke_index,
        session_ids=ids,
        donor_ids=tuple(donor_ids),
        digest=hashlib.sha256(encoded.encode("utf-8")).hexdigest(),
    )


def _wilson(successes: int, replicates: int) -> dict[str, object]:
    if type(successes) is not int or type(replicates) is not int:
        raise TypeError("Wilson counts must be integers")
    if replicates < 1 or not 0 <= successes <= replicates:
        raise ValueError("invalid Wilson counts")
    estimate = successes / replicates
    z = 1.959963984540054
    z2 = z * z
    denominator = 1.0 + z2 / replicates
    center = (estimate + z2 / (2.0 * replicates)) / denominator
    radius = z * math.sqrt(
        estimate * (1.0 - estimate) / replicates
        + z2 / (4.0 * replicates * replicates)
    ) / denominator
    return {
        "successes": successes,
        "replicates": replicates,
        "estimate": estimate,
        "interval_lower": max(0.0, center - radius),
        "interval_upper": min(1.0, center + radius),
        "confidence_level": MONTE_CARLO_CONFIDENCE,
        "interval_method": "Wilson score interval for Monte Carlo frequency only",
    }


def _nearest_rank_quantiles(values: Iterable[int]) -> dict[str, int]:
    ordered = sorted(int(value) for value in values)
    if not ordered:
        raise ValueError("quantiles require at least one value")
    def quantile(probability: float) -> int:
        return ordered[max(0, math.ceil(probability * len(ordered)) - 1)]
    return {
        "minimum": ordered[0],
        "p05": quantile(0.05),
        "p50": quantile(0.50),
        "p95": quantile(0.95),
        "maximum": ordered[-1],
    }


def formation_probability_bounds(high_probability: float, profile: str) -> dict[str, tuple[float, float]]:
    if high_probability not in FORMATION_CAPS:
        raise ValueError("high_probability must be one of the three declared values")
    if profile not in FORMATION_PROFILES:
        raise ValueError("unknown formation profile")
    if profile == "independent":
        return {"semantic_validity": (0.90, 0.90), "high_given_valid": (high_probability, high_probability)}
    return {
        "semantic_validity": (0.83, 0.97),
        "high_given_valid": (high_probability - 0.05, high_probability + 0.05),
    }


def _simulate_formation_replicate(
    profile: str,
    high_probability: float,
    replicate: int,
) -> dict[str, int | bool]:
    cap = FORMATION_CAPS[high_probability]
    rng = _rng("formation", profile, f"{high_probability:.2f}", replicate)
    high_counts = np.zeros(TOTAL_FINE_STRATA, dtype=np.int16)
    low_counts = np.zeros_like(high_counts)
    invalid_counts = np.zeros_like(high_counts)
    attempt_counts = np.full(TOTAL_FINE_STRATA, cap, dtype=np.int16)
    stopped = np.zeros(TOTAL_FINE_STRATA, dtype=bool)

    if profile == "provider_batch":
        provider_valid = float(_sign(rng))
        provider_high = float(_sign(rng))
    elif profile == "independent":
        provider_valid = 0.0
        provider_high = 0.0
    else:
        raise ValueError("unknown formation profile")

    for offset in range(0, cap, FORMATION_ATTEMPT_BATCH_SIZE):
        active = np.flatnonzero(~stopped)
        if not len(active):
            break
        width = min(FORMATION_ATTEMPT_BATCH_SIZE, cap - offset)
        if profile == "provider_batch":
            batch_valid = float(_sign(rng))
            batch_high = float(_sign(rng))
            validity_probability = 0.90 + 0.03 * provider_valid + 0.04 * batch_valid
            conditional_high_probability = (
                high_probability + 0.02 * provider_high + 0.03 * batch_high
            )
        else:
            validity_probability = 0.90
            conditional_high_probability = high_probability
        if not (0.0 <= validity_probability <= 1.0 and 0.0 <= conditional_high_probability <= 1.0):
            raise AssertionError("formation probabilities left [0,1]")

        valid = rng.random((len(active), width)) < validity_probability
        high = valid & (rng.random((len(active), width)) < conditional_high_probability)
        low = valid & ~high
        invalid = ~valid
        local_high = np.cumsum(high, axis=1)
        local_low = np.cumsum(low, axis=1)
        local_invalid = np.cumsum(invalid, axis=1)
        cumulative_high = high_counts[active, None] + local_high
        cumulative_low = low_counts[active, None] + local_low
        hits = (cumulative_high >= FORMATION_TARGET_PER_CHOICE) & (
            cumulative_low >= FORMATION_TARGET_PER_CHOICE
        )
        hit_any = np.any(hits, axis=1)
        first_hit = np.argmax(hits, axis=1)

        used = np.where(hit_any, first_hit + 1, width).astype(np.int64)
        local_rows = np.arange(len(active))
        local_columns = used - 1
        high_counts[active] += local_high[local_rows, local_columns]
        low_counts[active] += local_low[local_rows, local_columns]
        invalid_counts[active] += local_invalid[local_rows, local_columns]
        completed_strata = active[hit_any]
        stopped[completed_strata] = True
        attempt_counts[completed_strata] = offset + used[hit_any]

    complete_blocks = np.minimum(
        np.minimum(high_counts // 4, low_counts // 4),
        BLOCKS_PER_FINE_STRATUM,
    )
    unmatched_valid = high_counts + low_counts - SESSIONS_PER_BLOCK * complete_blocks
    return {
        "all_strata_supported": bool(np.all(complete_blocks == BLOCKS_PER_FINE_STRATUM)),
        "supported_strata": int(np.count_nonzero(complete_blocks == BLOCKS_PER_FINE_STRATUM)),
        "total_attempts": int(attempt_counts.sum()),
        "semantic_invalid": int(invalid_counts.sum()),
        "unmatched_valid": int(unmatched_valid.sum()),
        "retained_blocks": int(complete_blocks.sum()),
    }


def run_formation_cell(
    profile: str,
    high_probability: float,
    replicates: int,
    *,
    chunk_size: int = 64,
) -> dict[str, object]:
    if type(replicates) is not int or replicates < 1:
        raise ValueError("replicates must be a positive integer")
    if type(chunk_size) is not int or chunk_size < 1:
        raise ValueError("chunk_size must be positive")
    bounds = formation_probability_bounds(high_probability, profile)
    rows: list[dict[str, int | bool]] = []
    for start in range(0, replicates, chunk_size):
        for replicate in range(start, min(replicates, start + chunk_size)):
            rows.append(_simulate_formation_replicate(profile, high_probability, replicate))
    successes = sum(bool(row["all_strata_supported"]) for row in rows)
    return {
        "profile": profile,
        "high_probability_given_valid": high_probability,
        "semantic_validity_probability": 0.90,
        "attempt_cap_per_fine_stratum": FORMATION_CAPS[high_probability],
        "attempt_batch_size": FORMATION_ATTEMPT_BATCH_SIZE,
        "target_blocks_per_fine_stratum": BLOCKS_PER_FINE_STRATUM,
        "required_fine_strata": TOTAL_FINE_STRATA,
        "probability_bounds": bounds,
        "outer_replicates": replicates,
        "whole_panel_support_rate": _wilson(successes, replicates),
        "supported_strata_quantiles": _nearest_rank_quantiles(row["supported_strata"] for row in rows),
        "total_attempts_quantiles": _nearest_rank_quantiles(row["total_attempts"] for row in rows),
        "semantic_invalid_quantiles": _nearest_rank_quantiles(row["semantic_invalid"] for row in rows),
        "unmatched_valid_quantiles": _nearest_rank_quantiles(row["unmatched_valid"] for row in rows),
        "retained_blocks_quantiles": _nearest_rank_quantiles(row["retained_blocks"] for row in rows),
        "stopping_rule": (
            "within each fine stratum, stop at the first attempt with at least 64 valid L "
            "and 64 valid H; otherwise halt at the exact cap; never borrow, replace, or extend"
        ),
    }


def analytic_terminal_truth(scenario: str, failure_profile: str) -> tuple[float, float, float]:
    if scenario not in SCENARIO_PROBABILITIES:
        raise ValueError("unknown scenario")
    if failure_profile not in FAILURE_PROFILES:
        raise ValueError("unknown failure profile")
    arm_probabilities: dict[str, tuple[float, float, float]] = {}
    for arm in ARMS:
        average_failure = sum(FAILURE_PROFILES[failure_profile][arm].values()) / 2.0
        q = SCENARIO_PROBABILITIES[scenario][arm]
        arm_probabilities[arm] = (
            (1.0 - average_failure) * q[0],
            (1.0 - average_failure) * q[1],
            average_failure + (1.0 - average_failure) * q[2],
        )
    return tuple(
        float(arm_probabilities["self"][index] - arm_probabilities["yoke"][index])
        for index in range(3)
    )


def _truth_roles(truth: tuple[float, float, float]) -> dict[str, str]:
    positive = truth[1] - POSITIVE_THRESHOLD > BOUNDARY_TOLERANCE and (
        -POSITIVE_THRESHOLD - truth[0] > BOUNDARY_TOLERANCE
    )
    reverse = -POSITIVE_THRESHOLD - truth[1] > BOUNDARY_TOLERANCE and (
        truth[0] - POSITIVE_THRESHOLD > BOUNDARY_TOLERANCE
    )
    equivalent = all(
        margin - abs(value) > BOUNDARY_TOLERANCE
        for value, margin in zip(truth, EQUIVALENCE_MARGINS)
    )
    return {
        "positive_all_cells": "power" if positive else "false_control",
        "reverse_all_cells": "power" if reverse else "false_control",
        "equivalence_all_cells": "power" if equivalent else "false_control",
    }


def map_terminal_disposition(
    *,
    failed: bool,
    followup_category: str,
    failure_type_draw: float,
) -> tuple[str, str, str]:
    if followup_category not in CATEGORIES:
        raise ValueError("followup_category must be L, H, or U")
    if not 0.0 <= failure_type_draw < 1.0:
        raise ValueError("failure_type_draw must lie in [0,1)")
    if failed:
        subtype = (
            "provider_error"
            if failure_type_draw < 0.75
            else "transport_error"
        )
        result = ("U", "execution_failure", subtype)
    elif followup_category == "U":
        result = ("U", "followup_unavailable", "invalid_response")
    else:
        result = (followup_category, "followup_choice", "none")
    if result[2] not in SOURCE_SUBTYPES[result[1]]:
        raise AssertionError("synthetic disposition pair is outside protocol authority")
    return result


def outcome_probability_bounds(scenario: str, dependence_profile: str) -> dict[str, float]:
    if scenario not in SCENARIO_PROBABILITIES:
        raise ValueError("unknown scenario")
    if dependence_profile not in DEPENDENCE_PROFILES:
        raise ValueError("unknown dependence profile")
    enabled = DEPENDENCE_PROFILES[dependence_profile]
    total_a = sum(DEPENDENCE_AMPLITUDES[level][0] for level in enabled)
    total_b = sum(DEPENDENCE_AMPLITUDES[level][1] for level in enabled)
    values = []
    for probabilities in SCENARIO_PROBABILITIES[scenario].values():
        values.extend(
            (
                probabilities[0] - total_a - total_b / 2.0,
                probabilities[0] + total_a + total_b / 2.0,
                probabilities[1] - total_a - total_b / 2.0,
                probabilities[1] + total_a + total_b / 2.0,
                probabilities[2] - total_b,
                probabilities[2] + total_b,
            )
        )
    return {"minimum": min(values), "maximum": max(values)}


def failure_probability_bounds(failure_profile: str, dependence_profile: str) -> dict[str, float]:
    if failure_profile not in FAILURE_PROFILES:
        raise ValueError("unknown failure profile")
    enabled = DEPENDENCE_PROFILES[dependence_profile]
    shift = 0.0 if failure_profile == "none" else sum(
        DEPENDENCE_AMPLITUDES[level][2] for level in enabled
    )
    bases = [
        FAILURE_PROFILES[failure_profile][arm][schedule]
        for arm in ARMS
        for schedule in SCHEDULES
    ]
    return {"minimum": min(bases) - shift, "maximum": max(bases) + shift}


@lru_cache(maxsize=1)
def _block_coordinates() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    macro = np.repeat(np.arange(MACRO_CELL_COUNT), BLOCKS_PER_MACRO_CELL)
    within_macro = np.tile(np.arange(BLOCKS_PER_MACRO_CELL), MACRO_CELL_COUNT)
    fine = within_macro // BLOCKS_PER_FINE_STRATUM
    rank = within_macro % BLOCKS_PER_FINE_STRATUM
    batch = rank // OUTCOME_BATCH_BLOCKS_PER_FINE
    return macro, fine, batch


@lru_cache(maxsize=1)
def _critical_values() -> tuple[float, float]:
    df = BLOCKS_PER_FINE_STRATUM - 1
    return (
        _student_t_quantile(1.0 - ALPHA, df),
        _student_t_quantile(
            1.0 - ALPHA / (2.0 * MACRO_CELL_COUNT * len(CATEGORIES)), df
        ),
    )


def _level_shifts(
    rng: np.random.Generator,
    dependence_profile: str,
    sampled_pair_slot: np.ndarray,
    batch_ids: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    enabled = set(DEPENDENCE_PROFILES[dependence_profile])
    row_shape = sampled_pair_slot.shape
    hl = np.zeros(row_shape, dtype=np.float64)
    unavailable = np.zeros(row_shape, dtype=np.float64)
    failure = np.zeros(row_shape, dtype=np.float64)

    for level in DEPENDENCE_AMPLITUDES:
        if level not in enabled:
            continue
        a, b, f = DEPENDENCE_AMPLITUDES[level]
        if level == "provider":
            hl_sign = float(_sign(rng))
            u_sign = float(_sign(rng))
            f_sign = float(_sign(rng))
        elif level == "batch":
            hl_values = np.asarray(_sign(rng, OUTCOME_BATCH_COUNT))
            u_values = np.asarray(_sign(rng, OUTCOME_BATCH_COUNT))
            f_values = np.asarray(_sign(rng, OUTCOME_BATCH_COUNT))
            hl_sign = hl_values[batch_ids, None]
            u_sign = u_values[batch_ids, None]
            f_sign = f_values[batch_ids, None]
        elif level == "block":
            hl_sign = np.asarray(_sign(rng, TOTAL_BLOCKS))[:, None]
            u_sign = np.asarray(_sign(rng, TOTAL_BLOCKS))[:, None]
            f_sign = np.asarray(_sign(rng, TOTAL_BLOCKS))[:, None]
        elif level == "donor_pair":
            hl_values = np.asarray(_sign(rng, (TOTAL_BLOCKS, SESSIONS_PER_ARM)))
            u_values = np.asarray(_sign(rng, (TOTAL_BLOCKS, SESSIONS_PER_ARM)))
            f_values = np.asarray(_sign(rng, (TOTAL_BLOCKS, SESSIONS_PER_ARM)))
            hl_sign = np.take_along_axis(hl_values, sampled_pair_slot, axis=1)
            u_sign = np.take_along_axis(u_values, sampled_pair_slot, axis=1)
            f_sign = np.take_along_axis(f_values, sampled_pair_slot, axis=1)
        else:
            raise AssertionError(level)
        hl += a * hl_sign
        unavailable += b * u_sign
        failure += f * f_sign
    return hl, unavailable, failure


def _simulate_outcome_replicate(
    scenario: str,
    dependence_profile: str,
    failure_profile: str,
    replicate: int,
) -> dict[str, object]:
    table = assignment_table()
    rng = _rng("outcome", scenario, dependence_profile, failure_profile, replicate)
    assignment_indices = rng.integers(
        0, CANONICAL_ALLOWED_ASSIGNMENT_COUNT, size=TOTAL_BLOCKS
    )
    arm_self = table.arm_self[assignment_indices]
    schedule_high = table.schedule_high[assignment_indices]
    pair_slot = table.pair_slot[assignment_indices]
    _macro, _fine, batch_ids = _block_coordinates()
    hl_shift, u_shift, failure_shift = _level_shifts(
        rng, dependence_profile, pair_slot, batch_ids
    )

    self_q = SCENARIO_PROBABILITIES[scenario]["self"]
    yoke_q = SCENARIO_PROBABILITIES[scenario]["yoke"]
    q_l = np.where(arm_self, self_q[0], yoke_q[0])
    q_h = np.where(arm_self, self_q[1], yoke_q[1])
    q_u = np.where(arm_self, self_q[2], yoke_q[2])
    p_l = q_l - hl_shift - u_shift / 2.0
    p_h = q_h + hl_shift - u_shift / 2.0
    p_u = q_u + u_shift
    if (
        np.any(p_l < 0.0)
        or np.any(p_h < 0.0)
        or np.any(p_u < 0.0)
        or not np.allclose(p_l + p_h + p_u, 1.0, atol=1e-12)
    ):
        raise AssertionError("outcome probability stress left the simplex")

    failure_base = np.empty_like(p_l)
    declared_failure = FAILURE_PROFILES[failure_profile]
    for arm_name, arm_value in (("self", True), ("yoke", False)):
        for schedule_name, schedule_value in (("L", False), ("H", True)):
            mask = (arm_self == arm_value) & (schedule_high == schedule_value)
            failure_base[mask] = declared_failure[arm_name][schedule_name]
    failure_probability = failure_base + (
        0.0 if failure_profile == "none" else failure_shift
    )
    if np.any(failure_probability < 0.0) or np.any(failure_probability > 1.0):
        raise AssertionError("failure probability stress left [0,1]")

    failed = rng.random(p_l.shape) < failure_probability
    followup_draw = rng.random(p_l.shape)
    followup_category = np.where(
        followup_draw < p_l,
        0,
        np.where(followup_draw < p_l + p_h, 1, 2),
    ).astype(np.int8)
    terminal_category = followup_category.copy()
    terminal_category[failed] = 2
    subtype_draw = rng.random(p_l.shape)
    provider_error = failed & (subtype_draw < 0.75)
    transport_error = failed & ~provider_error

    indicators = np.stack(
        tuple(terminal_category == index for index in range(len(CATEGORIES))),
        axis=2,
    ).astype(np.float64)
    self_count = np.sum(indicators * arm_self[:, :, None], axis=1)
    yoke_count = np.sum(indicators * (~arm_self)[:, :, None], axis=1)
    block_contrasts = self_count / SESSIONS_PER_ARM - yoke_count / SESSIONS_PER_ARM
    reshaped = block_contrasts.reshape(
        MACRO_CELL_COUNT,
        FINE_STRATA_PER_MACRO_CELL,
        BLOCKS_PER_FINE_STRATUM,
        len(CATEGORIES),
    )
    fine_means = reshaped.mean(axis=2)
    fine_variances = reshaped.var(axis=2, ddof=1)
    estimates = fine_means.mean(axis=1)
    variances = fine_variances.sum(axis=1) / (
        FINE_STRATA_PER_MACRO_CELL**2 * BLOCKS_PER_FINE_STRATUM
    )
    standard_errors = np.sqrt(np.maximum(0.0, variances))
    critical, simultaneous_critical = _critical_values()
    lower = np.clip(estimates - critical * standard_errors, -1.0, 1.0)
    upper = np.clip(estimates + critical * standard_errors, -1.0, 1.0)
    valid = standard_errors > BOUNDARY_TOLERANCE
    positive_cells = (
        valid[:, 0]
        & valid[:, 1]
        & (lower[:, 1] - POSITIVE_THRESHOLD > BOUNDARY_TOLERANCE)
        & (-POSITIVE_THRESHOLD - upper[:, 0] > BOUNDARY_TOLERANCE)
    )
    reverse_cells = (
        valid[:, 0]
        & valid[:, 1]
        & (-POSITIVE_THRESHOLD - upper[:, 1] > BOUNDARY_TOLERANCE)
        & (lower[:, 0] - POSITIVE_THRESHOLD > BOUNDARY_TOLERANCE)
    )
    margins = np.asarray(EQUIVALENCE_MARGINS)
    equivalent_cells = np.all(
        valid
        & (lower + margins[None, :] > BOUNDARY_TOLERANCE)
        & (margins[None, :] - upper > BOUNDARY_TOLERANCE),
        axis=1,
    )
    truth = np.asarray(analytic_terminal_truth(scenario, failure_profile))
    simultaneous_lower = np.clip(
        estimates - simultaneous_critical * standard_errors, -1.0, 1.0
    )
    simultaneous_upper = np.clip(
        estimates + simultaneous_critical * standard_errors, -1.0, 1.0
    )
    coverage = bool(
        np.all(simultaneous_lower <= truth[None, :])
        and np.all(simultaneous_upper >= truth[None, :])
    )

    source_counts: dict[str, dict[str, int]] = {}
    for arm_name, arm_value in (("self", True), ("yoke", False)):
        for schedule_name, schedule_value in (("L", False), ("H", True)):
            mask = (arm_self == arm_value) & (schedule_high == schedule_value)
            key = f"{arm_name}|{schedule_name}"
            source_counts[key] = {
                "sessions": int(np.count_nonzero(mask)),
                "execution_failure": int(np.count_nonzero(failed & mask)),
                "provider_error": int(np.count_nonzero(provider_error & mask)),
                "transport_error": int(np.count_nonzero(transport_error & mask)),
                "followup_unavailable": int(
                    np.count_nonzero((~failed) & (followup_category == 2) & mask)
                ),
                "followup_choice": int(
                    np.count_nonzero((~failed) & (followup_category != 2) & mask)
                ),
            }

    self_rows = table.self_index[assignment_indices]
    yoke_rows = table.yoke_index[assignment_indices]
    row_index = np.arange(TOTAL_BLOCKS)[:, None]
    self_categories = terminal_category[row_index, self_rows]
    yoke_categories = terminal_category[row_index, yoke_rows]
    paired_agreement = int(np.count_nonzero(self_categories == yoke_categories))
    shifted_agreement = int(
        np.count_nonzero(self_categories == np.roll(yoke_categories, shift=1, axis=1))
    )
    return {
        "estimates": estimates,
        "variances": variances,
        "positive_all_cells": bool(np.all(positive_cells)),
        "reverse_all_cells": bool(np.all(reverse_cells)),
        "equivalence_all_cells": bool(np.all(equivalent_cells)),
        "simultaneous_coverage_all_12": coverage,
        "source_counts": source_counts,
        "paired_agreement": paired_agreement,
        "shifted_agreement": shifted_agreement,
        "pair_comparisons": TOTAL_BLOCKS * SESSIONS_PER_ARM,
    }


def _merge_source_counts(
    target: dict[str, dict[str, int]],
    source: Mapping[str, Mapping[str, int]],
) -> None:
    for cell, counts in source.items():
        if cell not in target:
            target[cell] = {key: 0 for key in counts}
        if set(target[cell]) != set(counts):
            raise AssertionError("terminal-source key drift")
        for key, value in counts.items():
            target[cell][key] += int(value)


def _matrix_to_json(matrix: np.ndarray) -> list[list[float | None]]:
    rows: list[list[float | None]] = []
    for row in matrix:
        rows.append([float(value) if math.isfinite(float(value)) else None for value in row])
    return rows


def run_outcome_cell(
    label: str,
    scenario: str,
    dependence_profile: str,
    failure_profile: str,
    replicates: int,
    *,
    chunk_size: int = 32,
) -> dict[str, object]:
    declared = {row[0]: row[1:] for row in OUTCOME_PROFILES}
    if label not in declared or declared[label] != (
        scenario,
        dependence_profile,
        failure_profile,
    ):
        raise ValueError("outcome cell must be one of the exact eight declared profiles")
    if type(replicates) is not int or replicates < 2:
        raise ValueError("outcome replicates must be an integer >=2")
    if type(chunk_size) is not int or chunk_size < 1:
        raise ValueError("chunk_size must be positive")
    outcome_bounds = outcome_probability_bounds(scenario, dependence_profile)
    failure_bounds = failure_probability_bounds(failure_profile, dependence_profile)
    if outcome_bounds["minimum"] < 0.0 or outcome_bounds["maximum"] > 1.0:
        raise AssertionError("declared outcome profile is infeasible")
    if failure_bounds["minimum"] < 0.0 or failure_bounds["maximum"] > 1.0:
        raise AssertionError("declared failure profile is infeasible")

    estimates = np.empty((replicates, MACRO_CELL_COUNT, len(CATEGORIES)))
    reported_variances = np.empty_like(estimates)
    decisions = {
        "positive_all_cells": 0,
        "reverse_all_cells": 0,
        "equivalence_all_cells": 0,
        "simultaneous_coverage_all_12": 0,
    }
    source_counts: dict[str, dict[str, int]] = {}
    paired_agreement = 0
    shifted_agreement = 0
    pair_comparisons = 0
    for start in range(0, replicates, chunk_size):
        for replicate in range(start, min(replicates, start + chunk_size)):
            row = _simulate_outcome_replicate(
                scenario, dependence_profile, failure_profile, replicate
            )
            estimates[replicate] = row["estimates"]
            reported_variances[replicate] = row["variances"]
            for metric in decisions:
                decisions[metric] += int(bool(row[metric]))
            _merge_source_counts(source_counts, row["source_counts"])
            paired_agreement += int(row["paired_agreement"])
            shifted_agreement += int(row["shifted_agreement"])
            pair_comparisons += int(row["pair_comparisons"])

    empirical_variance = estimates.var(axis=0, ddof=1)
    empirical_sd = np.sqrt(np.maximum(0.0, empirical_variance))
    mean_reported_variance = reported_variances.mean(axis=0)
    mean_reported_se = np.sqrt(np.maximum(0.0, reported_variances)).mean(axis=0)
    variance_ratio = np.divide(
        empirical_variance,
        mean_reported_variance,
        out=np.full_like(empirical_variance, np.nan),
        where=mean_reported_variance > 0.0,
    )
    correlation_by_category: dict[str, list[list[float | None]]] = {}
    for category_index, category in enumerate(CATEGORIES):
        matrix = np.corrcoef(estimates[:, :, category_index], rowvar=False)
        correlation_by_category[category] = _matrix_to_json(matrix)

    terminal_sources: dict[str, dict[str, object]] = {}
    for cell, counts in sorted(source_counts.items()):
        sessions = counts["sessions"]
        terminal_sources[cell] = {
            **counts,
            "execution_failure_rate": counts["execution_failure"] / sessions,
            "followup_unavailable_rate": counts["followup_unavailable"] / sessions,
            "followup_choice_rate": counts["followup_choice"] / sessions,
        }

    truth = analytic_terminal_truth(scenario, failure_profile)
    return {
        "label": label,
        "scenario": scenario,
        "dependence_profile": dependence_profile,
        "failure_profile": failure_profile,
        "blocks_per_macro_cell": BLOCKS_PER_MACRO_CELL,
        "blocks_per_fine_stratum": BLOCKS_PER_FINE_STRATUM,
        "outer_replicates": replicates,
        "outcome_probability_bounds": outcome_bounds,
        "failure_probability_bounds": failure_bounds,
        "analytic_terminal_truth_L_H_U": list(truth),
        "truth_roles": _truth_roles(truth),
        "decision_rates": {metric: _wilson(count, replicates) for metric, count in decisions.items()},
        "empirical_standard_deviation": empirical_sd.tolist(),
        "mean_reported_standard_error": mean_reported_se.tolist(),
        "mean_reported_variance": mean_reported_variance.tolist(),
        "empirical_to_reported_variance_ratio": _matrix_to_json(variance_ratio),
        "macro_estimate_correlation_by_category": correlation_by_category,
        "terminal_sources_by_arm_schedule": terminal_sources,
        "donor_pair_agreement": {
            "pair_comparisons": pair_comparisons,
            "paired_agreements": paired_agreement,
            "cyclic_nonpair_agreements": shifted_agreement,
            "paired_rate": paired_agreement / pair_comparisons,
            "cyclic_nonpair_rate": shifted_agreement / pair_comparisons,
            "excess_agreement": (paired_agreement - shifted_agreement) / pair_comparisons,
        },
    }


def simulate_one_terminal_block(
    *,
    assignment_index: int,
    scenario: str,
    dependence_profile: str,
    failure_profile: str,
    seed_label: str = "sentinel",
) -> tuple[TerminalRecord, ...]:
    """Return exactly eight records for a deterministic schema/mapping audit."""

    if not 0 <= assignment_index < CANONICAL_ALLOWED_ASSIGNMENT_COUNT:
        raise ValueError("assignment_index must lie in [0,576)")
    table = assignment_table()
    rng = _rng("terminal-block", seed_label, assignment_index, scenario, dependence_profile, failure_profile)
    arms = table.arm_self[assignment_index][None, :]
    schedules = table.schedule_high[assignment_index][None, :]
    pairs = table.pair_slot[assignment_index][None, :]
    enabled = DEPENDENCE_PROFILES[dependence_profile]
    hl = np.zeros((1, SESSIONS_PER_BLOCK))
    unavailable = np.zeros_like(hl)
    failure_shift = np.zeros_like(hl)
    for level in enabled:
        a, b, f = DEPENDENCE_AMPLITUDES[level]
        width = SESSIONS_PER_ARM if level == "donor_pair" else 1
        h_sign = np.asarray(_sign(rng, (1, width)))
        u_sign = np.asarray(_sign(rng, (1, width)))
        f_sign = np.asarray(_sign(rng, (1, width)))
        if level == "donor_pair":
            h_sign = np.take_along_axis(h_sign, pairs, axis=1)
            u_sign = np.take_along_axis(u_sign, pairs, axis=1)
            f_sign = np.take_along_axis(f_sign, pairs, axis=1)
        hl += a * h_sign
        unavailable += b * u_sign
        failure_shift += f * f_sign
    q_self = SCENARIO_PROBABILITIES[scenario]["self"]
    q_yoke = SCENARIO_PROBABILITIES[scenario]["yoke"]
    p_l = np.where(arms, q_self[0], q_yoke[0]) - hl - unavailable / 2.0
    p_h = np.where(arms, q_self[1], q_yoke[1]) + hl - unavailable / 2.0
    failure_probability = np.empty_like(p_l)
    for arm_name, arm_value in (("self", True), ("yoke", False)):
        for schedule_name, schedule_value in (("L", False), ("H", True)):
            mask = (arms == arm_value) & (schedules == schedule_value)
            failure_probability[mask] = FAILURE_PROFILES[failure_profile][arm_name][schedule_name]
    if failure_profile != "none":
        failure_probability += failure_shift
    failed = rng.random(p_l.shape) < failure_probability
    draw = rng.random(p_l.shape)
    followup = np.where(draw < p_l, 0, np.where(draw < p_l + p_h, 1, 2))
    type_draw = rng.random(p_l.shape)
    records: list[TerminalRecord] = []
    donor_ids = table.donor_ids[assignment_index]
    for row_index, session_id in enumerate(table.session_ids):
        category, source, subtype = map_terminal_disposition(
            failed=bool(failed[0, row_index]),
            followup_category=CATEGORIES[int(followup[0, row_index])],
            failure_type_draw=float(type_draw[0, row_index]),
        )
        pair = int(table.pair_slot[assignment_index, row_index])
        records.append(
            TerminalRecord(
                session_id=session_id,
                arm="self" if bool(arms[0, row_index]) else "yoke",
                received_schedule="H" if bool(schedules[0, row_index]) else "L",
                donor_session_id=donor_ids[pair],
                category=category,
                disposition_source=source,
                failure_subtype=subtype,
            )
        )
    if len(records) != SESSIONS_PER_BLOCK:
        raise AssertionError("terminal block must contain exactly eight rows")
    return tuple(records)


TOP_LEVEL_KEYS = {
    "schema_version",
    "generated_date",
    "status",
    "gate_effect",
    "numerical_gate_eligible",
    "master_seed",
    "scope",
    "claim_ceiling",
    "assignment_audit",
    "design",
    "dgp",
    "formation_diagnostics",
    "outcome_diagnostics",
    "method",
    "rng_method",
}
FORMATION_RESULT_KEYS = {
    "profile",
    "high_probability_given_valid",
    "semantic_validity_probability",
    "attempt_cap_per_fine_stratum",
    "attempt_batch_size",
    "target_blocks_per_fine_stratum",
    "required_fine_strata",
    "probability_bounds",
    "outer_replicates",
    "whole_panel_support_rate",
    "supported_strata_quantiles",
    "total_attempts_quantiles",
    "semantic_invalid_quantiles",
    "unmatched_valid_quantiles",
    "retained_blocks_quantiles",
    "stopping_rule",
}
OUTCOME_RESULT_KEYS = {
    "label",
    "scenario",
    "dependence_profile",
    "failure_profile",
    "blocks_per_macro_cell",
    "blocks_per_fine_stratum",
    "outer_replicates",
    "outcome_probability_bounds",
    "failure_probability_bounds",
    "analytic_terminal_truth_L_H_U",
    "truth_roles",
    "decision_rates",
    "empirical_standard_deviation",
    "mean_reported_standard_error",
    "mean_reported_variance",
    "empirical_to_reported_variance_ratio",
    "macro_estimate_correlation_by_category",
    "terminal_sources_by_arm_schedule",
    "donor_pair_agreement",
}
WILSON_KEYS = {
    "successes",
    "replicates",
    "estimate",
    "interval_lower",
    "interval_upper",
    "confidence_level",
    "interval_method",
}


def _require_exact_keys(value: Mapping[str, object], expected: set[str], label: str) -> None:
    if set(value) != expected:
        raise ValueError(
            f"{label} keys must match exactly; missing={sorted(expected-set(value))}, "
            f"extra={sorted(set(value)-expected)}"
        )


def _validate_wilson(value: Mapping[str, object], label: str) -> None:
    _require_exact_keys(value, WILSON_KEYS, label)
    recomputed = _wilson(int(value["successes"]), int(value["replicates"]))
    if dict(value) != recomputed:
        raise ValueError(f"{label} is inconsistent with its counts")


def validate_result(result: Mapping[str, object]) -> None:
    if not isinstance(result, Mapping):
        raise TypeError("result must be a mapping")
    _require_exact_keys(result, TOP_LEVEL_KEYS, "result")
    if result["schema_version"] != SCHEMA_VERSION:
        raise ValueError("schema version mismatch")
    if result["status"] != STATUS or result["gate_effect"] != GATE_EFFECT:
        raise ValueError("diagnostic must remain explicitly non-gating")
    if result["numerical_gate_eligible"] is not False:
        raise ValueError("diagnostic can never be numerical-gate eligible")
    if result["master_seed"] != MASTER_SEED:
        raise ValueError("master seed mismatch")

    formations = result["formation_diagnostics"]
    outcomes = result["outcome_diagnostics"]
    if not isinstance(formations, list) or not isinstance(outcomes, list):
        raise TypeError("diagnostic collections must be lists")
    expected_formations = {
        (profile, high) for profile in FORMATION_PROFILES for high in FORMATION_CAPS
    }
    observed_formations = set()
    for index, row in enumerate(formations):
        if not isinstance(row, Mapping):
            raise TypeError("formation result must be a mapping")
        _require_exact_keys(row, FORMATION_RESULT_KEYS, f"formation[{index}]")
        key = (row["profile"], row["high_probability_given_valid"])
        if key in observed_formations:
            raise ValueError("duplicate formation diagnostic")
        observed_formations.add(key)
        rate = row["whole_panel_support_rate"]
        if not isinstance(rate, Mapping):
            raise TypeError("formation Wilson rate must be a mapping")
        _validate_wilson(rate, f"formation[{index}].whole_panel_support_rate")
    if observed_formations != expected_formations:
        raise ValueError("formation diagnostic coverage is incomplete")

    declared_outcomes = {label: rest for label, *rest in OUTCOME_PROFILES}
    observed_labels = set()
    for index, row in enumerate(outcomes):
        if not isinstance(row, Mapping):
            raise TypeError("outcome result must be a mapping")
        _require_exact_keys(row, OUTCOME_RESULT_KEYS, f"outcome[{index}]")
        label = row["label"]
        if label in observed_labels or label not in declared_outcomes:
            raise ValueError("duplicate or unexpected outcome diagnostic")
        observed_labels.add(label)
        expected = declared_outcomes[label]
        actual = [row["scenario"], row["dependence_profile"], row["failure_profile"]]
        if actual != expected:
            raise ValueError("outcome profile coordinates mismatch")
        rates = row["decision_rates"]
        if not isinstance(rates, Mapping) or set(rates) != {
            "positive_all_cells",
            "reverse_all_cells",
            "equivalence_all_cells",
            "simultaneous_coverage_all_12",
        }:
            raise ValueError("outcome decision-rate coverage mismatch")
        for metric, rate in rates.items():
            if not isinstance(rate, Mapping):
                raise TypeError("outcome Wilson rate must be a mapping")
            _validate_wilson(rate, f"outcome[{index}].{metric}")
    if observed_labels != set(declared_outcomes):
        raise ValueError("outcome diagnostic coverage is incomplete")


def run_diagnostics(
    *,
    outcome_replicates: int = DEFAULT_OUTCOME_REPLICATES,
    formation_replicates: int = DEFAULT_FORMATION_REPLICATES,
    chunk_size: int = 32,
) -> dict[str, object]:
    if type(outcome_replicates) is not int or outcome_replicates < 2:
        raise ValueError("outcome_replicates must be an integer >=2")
    if type(formation_replicates) is not int or formation_replicates < 1:
        raise ValueError("formation_replicates must be a positive integer")
    if type(chunk_size) is not int or chunk_size < 1:
        raise ValueError("chunk_size must be positive")
    table = assignment_table()
    formation_rows = [
        run_formation_cell(
            profile,
            high_probability,
            formation_replicates,
            chunk_size=chunk_size,
        )
        for profile in FORMATION_PROFILES
        for high_probability in FORMATION_CAPS
    ]
    outcome_rows = [
        run_outcome_cell(
            label,
            scenario,
            dependence,
            failure,
            outcome_replicates,
            chunk_size=chunk_size,
        )
        for label, scenario, dependence, failure in OUTCOME_PROFILES
    ]
    result: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "generated_date": "2026-08-08",
        "status": STATUS,
        "gate_effect": GATE_EFFECT,
        "numerical_gate_eligible": False,
        "master_seed": MASTER_SEED,
        "scope": "local seeded synthetic dependence and feasibility diagnostics only",
        "claim_ceiling": CLAIM_CEILING,
        "assignment_audit": {
            "allowed_assignment_count": CANONICAL_ALLOWED_ASSIGNMENT_COUNT,
            "sampling_policy": "exact discrete uniform over allowed_set_index 0..575",
            "selection_probability": f"1/{CANONICAL_ALLOWED_ASSIGNMENT_COUNT}",
            "canonical_assignment_table_sha256": table.digest,
            "donor_rule": "each self donor supplies exactly one yoke recipient in every block",
        },
        "design": {
            "macro_cells": MACRO_CELL_COUNT,
            "fine_strata_per_macro_cell": FINE_STRATA_PER_MACRO_CELL,
            "required_fine_strata": TOTAL_FINE_STRATA,
            "blocks_per_macro_cell": BLOCKS_PER_MACRO_CELL,
            "blocks_per_fine_stratum": BLOCKS_PER_FINE_STRATUM,
            "sessions_per_block": SESSIONS_PER_BLOCK,
            "outcome_batches": OUTCOME_BATCH_COUNT,
            "outcome_replicates_per_cell": outcome_replicates,
            "formation_replicates_per_cell": formation_replicates,
            "alpha": ALPHA,
            "positive_threshold": POSITIVE_THRESHOLD,
            "equivalence_margins_L_H_U": list(EQUIVALENCE_MARGINS),
        },
        "dgp": {
            "formation_profiles": list(FORMATION_PROFILES),
            "formation_caps_by_high_probability": {
                f"{key:.2f}": value for key, value in FORMATION_CAPS.items()
            },
            "formation_provider_batch_shifts": {
                "semantic_validity_provider": 0.03,
                "semantic_validity_batch": 0.04,
                "high_given_valid_provider": 0.02,
                "high_given_valid_batch": 0.03,
            },
            "dependence_amplitudes_HL_U_failure": {
                level: list(values) for level, values in DEPENDENCE_AMPLITUDES.items()
            },
            "dependence_profiles": {
                key: list(value) for key, value in DEPENDENCE_PROFILES.items()
            },
            "scenario_probabilities_conditional_on_no_failure": {
                scenario: {arm: list(values) for arm, values in arms.items()}
                for scenario, arms in SCENARIO_PROBABILITIES.items()
            },
            "failure_probabilities_by_arm_schedule": FAILURE_PROFILES,
            "failure_mapping": {
                "primary_category": "U",
                "disposition_source": "execution_failure",
                "subtype_probabilities": {
                    "provider_error": 0.75,
                    "transport_error": 0.25,
                },
                "followup_after_failure": False,
                "terminal_rows_per_randomized_session": 1,
            },
            "outcome_profiles": [
                {
                    "label": label,
                    "scenario": scenario,
                    "dependence_profile": dependence,
                    "failure_profile": failure,
                }
                for label, scenario, dependence, failure in OUTCOME_PROFILES
            ],
        },
        "formation_diagnostics": formation_rows,
        "outcome_diagnostics": outcome_rows,
        "method": (
            "non-gating end-point and feasibility screen using actual uniform 576-way donor-aware "
            "assignments, zero-mean Rademacher probability shocks, composite-U terminal failure, "
            "fixed-stratum block t decisions, and stochastic pre-randomization block formation"
        ),
        "rng_method": (
            "independent NumPy Generator(PCG64) stream per logical outer replicate, seeded by "
            "SHA-256 over the fixed master seed and scientific coordinates; operational chunk "
            "size is excluded and cannot change output"
        ),
    }
    validate_result(result)
    return result


def serialize_result(result: Mapping[str, object]) -> str:
    validate_result(result)
    return json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"


def block_formation_sentinel() -> dict[str, object]:
    """Exercise the actual block former on one exact 4L/4H plus attrition set."""

    sessions = tuple(
        Session(f"valid-L-{index}", "sentinel", "L") for index in range(5)
    ) + tuple(
        Session(f"valid-H-{index}", "sentinel", "H") for index in range(4)
    ) + (Session("invalid-0", "sentinel", "U"),)
    result = form_canonical_blocks(sessions)
    return {
        "blocks": len(result.blocks),
        "retained_sessions": result.retained_session_count,
        "attrited_sessions": result.attrited_session_count,
        "accounts_for_all_sessions": result.accounts_for_all_sessions,
        "attrition_reasons": sorted(record.reason for record in result.attrition),
    }


__all__ = [
    "CLAIM_CEILING",
    "DEFAULT_FORMATION_REPLICATES",
    "DEFAULT_OUTCOME_REPLICATES",
    "DEPENDENCE_PROFILES",
    "FORMATION_CAPS",
    "FORMATION_PROFILES",
    "GATE_EFFECT",
    "MASTER_SEED",
    "OUTCOME_PROFILES",
    "SCHEMA_VERSION",
    "STATUS",
    "TerminalRecord",
    "analytic_terminal_truth",
    "assignment_table",
    "block_formation_sentinel",
    "failure_probability_bounds",
    "formation_probability_bounds",
    "map_terminal_disposition",
    "outcome_probability_bounds",
    "run_diagnostics",
    "run_formation_cell",
    "run_outcome_cell",
    "serialize_result",
    "simulate_one_terminal_block",
    "validate_result",
]
