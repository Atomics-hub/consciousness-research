"""Planning-only support and provider-request envelope calculations.

Nothing in this module authorizes provider activity or estimates dollar cost.
The block-retention simulation exposes the price of exact 4L/4H support before
any empirical baseline rate is known.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import random
from statistics import mean


@dataclass(frozen=True, slots=True)
class RetentionSummary:
    attempted: int
    p_high: float
    replicates: int
    mean_retained: float
    mean_retained_fraction: float
    p05_retained: int
    median_retained: int
    p95_retained: int
    probability_zero_blocks: float
    asymptotic_fraction_ceiling: float

    def to_dict(self) -> dict[str, int | float]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RequestEnvelope:
    attempted_sessions: int
    randomized_sessions: int
    work_blocks: int
    tool_blocks: int
    baseline_requests: int
    execution_and_followup_requests: int
    maximum_tool_continuation_requests: int
    maximum_generation_requests: int

    def to_dict(self) -> dict[str, int]:
        return asdict(self)


def retained_sessions(n_low: int, n_high: int) -> int:
    """Return sessions retained by the frozen exact 4L/4H construction."""

    if n_low < 0 or n_high < 0:
        raise ValueError("choice counts cannot be negative")
    return 8 * min(n_low // 4, n_high // 4)


def simulate_retention(
    attempted: int,
    p_high: float,
    *,
    replicates: int = 2_000,
    master_seed: int = 20260804,
) -> RetentionSummary:
    """Seeded Bernoulli planning simulation for one valid-baseline stratum."""

    if attempted <= 0:
        raise ValueError("attempted must be positive")
    if not 0.0 <= p_high <= 1.0:
        raise ValueError("p_high must be in [0, 1]")
    if replicates <= 0:
        raise ValueError("replicates must be positive")

    material = f"binding-retention-v1|{master_seed}|{attempted}|{p_high:.8f}"
    derived_seed = int.from_bytes(hashlib.sha256(material.encode()).digest()[:16], "big")
    rng = random.Random(derived_seed)
    retained: list[int] = []
    for _ in range(replicates):
        n_high = sum(rng.random() < p_high for _ in range(attempted))
        retained.append(retained_sessions(attempted - n_high, n_high))

    ordered = sorted(retained)

    def quantile_index(probability: float) -> int:
        return round((len(ordered) - 1) * probability)

    return RetentionSummary(
        attempted=attempted,
        p_high=p_high,
        replicates=replicates,
        mean_retained=mean(retained),
        mean_retained_fraction=mean(retained) / attempted,
        p05_retained=ordered[quantile_index(0.05)],
        median_retained=ordered[quantile_index(0.50)],
        p95_retained=ordered[quantile_index(0.95)],
        probability_zero_blocks=sum(value == 0 for value in retained) / replicates,
        asymptotic_fraction_ceiling=2 * min(p_high, 1 - p_high),
    )


def request_envelope(
    *,
    attempted_sessions: int,
    work_blocks: int,
    tool_blocks: int,
    q_low: int = 0,
    q_high: int = 0,
) -> RequestEnvelope:
    """Return the exact base request count and a tool-continuation cap.

    ``q_low`` and ``q_high`` are maximum *additional model continuations* for
    the two tool schedules, not generic task units or local function calls.
    Each canonical tool block executes four copies of each schedule.
    """

    values = (attempted_sessions, work_blocks, tool_blocks, q_low, q_high)
    if any(value < 0 for value in values):
        raise ValueError("request-envelope inputs cannot be negative")
    randomized_sessions = 8 * (work_blocks + tool_blocks)
    if randomized_sessions > attempted_sessions:
        raise ValueError("randomized sessions cannot exceed attempted sessions")

    baseline_requests = attempted_sessions
    execution_and_followup = 2 * randomized_sessions
    tool_continuations = 4 * tool_blocks * (q_low + q_high)
    return RequestEnvelope(
        attempted_sessions=attempted_sessions,
        randomized_sessions=randomized_sessions,
        work_blocks=work_blocks,
        tool_blocks=tool_blocks,
        baseline_requests=baseline_requests,
        execution_and_followup_requests=execution_and_followup,
        maximum_tool_continuation_requests=tool_continuations,
        maximum_generation_requests=(
            baseline_requests + execution_and_followup + tool_continuations
        ),
    )
