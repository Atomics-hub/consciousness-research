"""Targeted stress demonstrations not represented by the nominal outcome grid."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import random
from statistics import mean
from typing import Any


@dataclass(frozen=True, slots=True)
class SnapshotDriftStress:
    replicates: int
    blocks: int
    old_snapshot_high_probability: float
    new_snapshot_high_probability: float
    mean_valid_blocked_contrast: float
    mean_invalid_time_confounded_contrast: float
    valid_absolute_bias: float
    invalid_absolute_bias: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PostTreatmentHistoryStress:
    sessions: int
    primary_randomized_contrast: float
    conditioned_history_zero_contrast: float
    conditioned_history_one_contrast: float
    mean_absolute_conditioned_contrast: float
    interpretation: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class BinaryInvarianceLimit:
    unavailability: float
    delta: float
    infinite_sample_lower: float
    infinite_sample_upper: float
    strict_invariance_possible: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _seed(master_seed: int, label: str) -> int:
    material = f"binding-stress-v1|{master_seed}|{label}".encode("utf-8")
    return int.from_bytes(hashlib.sha256(material).digest()[:16], "big")


def binary_invariance_limit(unavailability: float, delta: float = 0.05) -> BinaryInvarianceLimit:
    """Return the null binary region before sampling uncertainty.

    With equal arm unavailability ``u`` and equal observed high probabilities,
    worst/best-case binary assignment gives ``[-u,+u]``. The protocol's
    invariance rule is strict, so touching a margin is indeterminate.
    """

    if not 0 <= unavailability <= 1 or not 0 <= delta <= 1:
        raise ValueError("unavailability and delta must lie in [0,1]")
    lower, upper = -unavailability, unavailability
    return BinaryInvarianceLimit(
        unavailability=unavailability,
        delta=delta,
        infinite_sample_lower=lower,
        infinite_sample_upper=upper,
        strict_invariance_possible=lower > -delta and upper < delta,
    )


def simulate_snapshot_drift(
    *,
    replicates: int = 2_000,
    blocks: int = 40,
    sessions_per_arm_block: int = 4,
    old_high: float = 0.20,
    new_high: float = 0.80,
    master_seed: int = 20260804,
) -> SnapshotDriftStress:
    """Compare valid within-snapshot blocks with an invalid time-confounded design."""

    if blocks < 2 or blocks % 2:
        raise ValueError("blocks must be an even integer of at least two")
    rng = random.Random(_seed(master_seed, "snapshot"))
    valid: list[float] = []
    invalid: list[float] = []
    n_per_arm = blocks * sessions_per_arm_block
    for _ in range(replicates):
        self_high = 0
        yoke_high = 0
        for block in range(blocks):
            probability = old_high if block < blocks // 2 else new_high
            self_high += sum(
                rng.random() < probability for _ in range(sessions_per_arm_block)
            )
            yoke_high += sum(
                rng.random() < probability for _ in range(sessions_per_arm_block)
            )
        valid.append(self_high / n_per_arm - yoke_high / n_per_arm)

        # Deliberately invalid comparator: collect yoke under the old snapshot
        # and self under the new snapshot, with no real treatment effect.
        invalid_self = sum(rng.random() < new_high for _ in range(n_per_arm))
        invalid_yoke = sum(rng.random() < old_high for _ in range(n_per_arm))
        invalid.append(invalid_self / n_per_arm - invalid_yoke / n_per_arm)
    return SnapshotDriftStress(
        replicates=replicates,
        blocks=blocks,
        old_snapshot_high_probability=old_high,
        new_snapshot_high_probability=new_high,
        mean_valid_blocked_contrast=mean(valid),
        mean_invalid_time_confounded_contrast=mean(invalid),
        valid_absolute_bias=abs(mean(valid)),
        invalid_absolute_bias=abs(mean(invalid)),
    )


def simulate_post_treatment_history_divergence(
    *,
    sessions: int = 200_000,
    master_seed: int = 20260804,
) -> PostTreatmentHistoryStress:
    """Show collider bias from matching/conditioning on a realized history.

    Treatment ``Z`` and latent response type ``V`` are independent. The
    follow-up binary outcome equals ``V``, so the true randomized treatment
    contrast is zero. Realized history is ``Z XOR V`` and therefore diverges
    after treatment. Conditioning on either history value makes treatment
    nearly determine ``V``, creating a large spurious contrast.
    """

    if sessions < 100:
        raise ValueError("sessions must be at least 100")
    rng = random.Random(_seed(master_seed, "history"))
    cells: dict[tuple[int, int], list[int]] = {
        (z, history): [] for z in (0, 1) for history in (0, 1)
    }
    outcomes_by_z = {0: [], 1: []}
    for _ in range(sessions):
        z = int(rng.random() < 0.5)
        latent = int(rng.random() < 0.5)
        history = z ^ latent
        outcome = latent
        outcomes_by_z[z].append(outcome)
        cells[(z, history)].append(outcome)

    primary = mean(outcomes_by_z[1]) - mean(outcomes_by_z[0])
    conditional = {
        history: mean(cells[(1, history)]) - mean(cells[(0, history)])
        for history in (0, 1)
    }
    return PostTreatmentHistoryStress(
        sessions=sessions,
        primary_randomized_contrast=primary,
        conditioned_history_zero_contrast=conditional[0],
        conditioned_history_one_contrast=conditional[1],
        mean_absolute_conditioned_contrast=mean(abs(value) for value in conditional.values()),
        interpretation=(
            "The primary randomized contrast remains near zero; conditioning on "
            "the post-treatment realized history creates near-unit spurious effects."
        ),
    )
