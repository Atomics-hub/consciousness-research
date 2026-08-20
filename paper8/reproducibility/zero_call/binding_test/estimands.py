"""Planning estimands and decision rules for the Binding Test.

The module deliberately treats ``U`` (unavailable/refusal/invalid) as a
nominal outcome category.  It is never assigned a score or placed between
``L`` and ``H``.  Two analyses are therefore kept separate:

* a fully observed vector of probability contrasts for ``L``, ``H``, and
  ``U``; and
* a binary high-choice contrast whose value is only partially identified
  when ``U`` occurs.

Bootstrap intervals below are deterministic, seeded, block-resampled
*planning* intervals.  They are useful for zero-call design simulations, but
they are not a substitute for the protocol's final restricted-randomization
or other confirmatory analysis.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import math
import random
from typing import Iterable, Iterator, Mapping, Sequence


CATEGORIES: tuple[str, str, str] = ("L", "H", "U")
ARMS: tuple[str, str] = ("self", "yoke")
PLANNING_BOOTSTRAP_METHOD = (
    "planning-grade unstudentized max-deviation block bootstrap; "
    "not final confirmatory inference"
)


@dataclass(frozen=True)
class Observation:
    """One fully retained follow-up outcome from an eligible session.

    Parameters
    ----------
    block_id:
        Identifier of the randomization/interference block.  Bootstrap
        resampling always keeps all rows from a block together.
    arm:
        ``"self"`` for self-contingent enforcement or ``"yoke"`` for the
        assigned-schedule-matched yoke.
    category:
        Exactly one of ``"L"``, ``"H"``, or ``"U"``.  ``U`` is nominal.
    model_family, target_family:
        Optional fixed-panel labels for subgroup analysis.
    mechanism_signal:
        Optional simulation-only marker.  Estimands never condition on it.
    """

    block_id: str
    arm: str
    category: str
    model_family: str = "model"
    target_family: str = "target"
    mechanism_signal: bool | None = None

    def __post_init__(self) -> None:
        if not self.block_id:
            raise ValueError("block_id must be a non-empty string")
        if self.arm not in ARMS:
            raise ValueError(f"arm must be one of {ARMS}; got {self.arm!r}")
        if self.category not in CATEGORIES:
            raise ValueError(
                f"category must be one of {CATEGORIES}; got {self.category!r}"
            )


@dataclass(frozen=True)
class ConfidenceInterval:
    """A bounded interval around a scalar contrast."""

    estimate: float
    lower: float
    upper: float


@dataclass(frozen=True)
class CategoryContrastResult:
    """Fully observed non-ordinal category-probability contrasts.

    Every contrast is ``P(D=a | self) - P(D=a | yoke)``.  ``intervals`` are
    simultaneous across all three categories by construction.
    """

    contrasts: dict[str, float]
    intervals: dict[str, ConfidenceInterval]
    simultaneous_critical_radius: float
    alpha: float
    bootstrap_replicates: int
    seed: int
    n_blocks: int
    n_by_arm: dict[str, int]
    method: str = PLANNING_BOOTSTRAP_METHOD

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-compatible nested dictionary."""

        return asdict(self)

    def to_json(self, **kwargs: object) -> str:
        """Serialize the result without custom JSON encoders."""

        return json.dumps(self.to_dict(), **kwargs)


@dataclass(frozen=True)
class BinaryBoundsResult:
    """Worst/best-case binary high-choice contrast and uncertainty band.

    ``identified_lower`` and ``identified_upper`` are the sample's sharp
    worst/best-case endpoints when every ``U`` may hide either binary choice.
    The ``expanded_*`` endpoints add simultaneous planning uncertainty from a
    block bootstrap.  Decisions use the expanded region only.
    """

    identified_lower: float
    identified_upper: float
    expanded_lower: float
    expanded_upper: float
    simultaneous_critical_radius: float
    alpha: float
    bootstrap_replicates: int
    seed: int
    n_blocks: int
    n_by_arm: dict[str, int]
    method: str = PLANNING_BOOTSTRAP_METHOD

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    def to_json(self, **kwargs: object) -> str:
        return json.dumps(self.to_dict(), **kwargs)


@dataclass(frozen=True)
class DecisionResult:
    """A JSON-compatible decision label with auditable supporting fields."""

    status: str
    direction: str | None = None
    components: tuple[str, ...] = ()
    rationale: str = ""

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class PlanningAnalysis:
    """Complete zero-call planning analysis for one declared population."""

    category_contrasts: CategoryContrastResult
    binary_bounds: BinaryBoundsResult
    observable_decision: DecisionResult
    binary_decision: DecisionResult
    broad_invariance_decision: DecisionResult

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    def to_json(self, **kwargs: object) -> str:
        return json.dumps(self.to_dict(), **kwargs)


def _validated_rows(observations: Iterable[Observation]) -> tuple[Observation, ...]:
    rows = tuple(observations)
    if not rows:
        raise ValueError("at least one observation is required")
    if not all(isinstance(row, Observation) for row in rows):
        raise TypeError("all observations must be Observation instances")

    arm_counts = {arm: sum(row.arm == arm for row in rows) for arm in ARMS}
    if any(count == 0 for count in arm_counts.values()):
        raise ValueError("both self and yoke arms must contain observations")

    blocks: dict[str, set[str]] = {}
    block_strata: dict[str, set[tuple[str, str]]] = {}
    for row in rows:
        blocks.setdefault(row.block_id, set()).add(row.arm)
        block_strata.setdefault(row.block_id, set()).add(
            (row.model_family, row.target_family)
        )
    if len(blocks) < 2:
        raise ValueError("block bootstrap requires at least two blocks")
    incomplete = sorted(block for block, arms in blocks.items() if arms != set(ARMS))
    if incomplete:
        raise ValueError(
            "each bootstrap block must contain both arms; incomplete blocks: "
            + ", ".join(incomplete[:5])
        )
    mixed_strata = sorted(
        block for block, strata in block_strata.items() if len(strata) != 1
    )
    if mixed_strata:
        raise ValueError(
            "a block cannot cross model/target strata; mixed blocks: "
            + ", ".join(mixed_strata[:5])
        )
    return rows


def _validate_bootstrap(alpha: float, bootstrap_replicates: int) -> None:
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie strictly between 0 and 1")
    if bootstrap_replicates < 1:
        raise ValueError("bootstrap_replicates must be positive")


def _arm_category_probabilities(
    observations: Sequence[Observation],
) -> dict[str, dict[str, float]]:
    counts = {
        arm: {category: 0 for category in CATEGORIES}
        for arm in ARMS
    }
    totals = {arm: 0 for arm in ARMS}
    for row in observations:
        counts[row.arm][row.category] += 1
        totals[row.arm] += 1
    if any(total == 0 for total in totals.values()):
        raise ValueError("a bootstrap sample omitted an arm")
    return {
        arm: {
            category: counts[arm][category] / totals[arm]
            for category in CATEGORIES
        }
        for arm in ARMS
    }


def category_probability_contrasts(
    observations: Sequence[Observation],
) -> dict[str, float]:
    """Return all three fully observed ``self - yoke`` contrasts.

    No numeric encoding of the categories is constructed.  The three entries
    necessarily sum to zero up to floating-point error.
    """

    probabilities = _arm_category_probabilities(observations)
    return {
        category: probabilities["self"][category]
        - probabilities["yoke"][category]
        for category in CATEGORIES
    }


def binary_high_choice_bounds(
    observations: Sequence[Observation],
) -> tuple[float, float]:
    """Return sharp worst/best-case bounds for the binary high contrast.

    For each arm, the high-choice probability lies between observed ``H`` and
    observed ``H + U``.  Subtracting arm intervals gives

    ``[H_self - (H_yoke + U_yoke), (H_self + U_self) - H_yoke]``.
    """

    probabilities = _arm_category_probabilities(observations)
    lower = probabilities["self"]["H"] - (
        probabilities["yoke"]["H"] + probabilities["yoke"]["U"]
    )
    upper = (
        probabilities["self"]["H"] + probabilities["self"]["U"]
    ) - probabilities["yoke"]["H"]
    return lower, upper


def _block_bootstrap_samples(
    observations: Sequence[Observation],
    *,
    bootstrap_replicates: int,
    seed: int,
) -> Iterator[tuple[Observation, ...]]:
    groups: dict[str, list[Observation]] = {}
    for row in observations:
        groups.setdefault(row.block_id, []).append(row)
    block_stratum = {
        block_id: (rows[0].model_family, rows[0].target_family)
        for block_id, rows in groups.items()
    }
    strata: dict[tuple[str, str], list[str]] = {}
    for block_id, stratum in block_stratum.items():
        strata.setdefault(stratum, []).append(block_id)
    for block_ids in strata.values():
        block_ids.sort()

    rng = random.Random(seed)
    for _ in range(bootstrap_replicates):
        # Model and target families are fixed design strata.  Resampling blocks
        # within, rather than across, each stratum preserves the finite-panel
        # composition while keeping all rows from a block together.
        selected: list[str] = []
        for stratum in sorted(strata):
            block_ids = strata[stratum]
            selected.extend(rng.choices(block_ids, k=len(block_ids)))
        yield tuple(row for block in selected for row in groups[block])


def _upper_empirical_quantile(values: Sequence[float], probability: float) -> float:
    """Conservative upper empirical quantile with no interpolation."""

    if not values:
        raise ValueError("cannot take a quantile of an empty sequence")
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, math.ceil(probability * len(ordered)) - 1))
    return ordered[index]


def estimate_category_contrasts(
    observations: Iterable[Observation],
    *,
    alpha: float = 0.05,
    bootstrap_replicates: int = 2_000,
    seed: int = 0,
) -> CategoryContrastResult:
    """Estimate category contrasts with a simultaneous block-bootstrap band.

    The critical radius is the ``1-alpha`` quantile of the largest absolute
    bootstrap deviation across ``L``, ``H``, and ``U``.  Applying the same
    radius to all three point estimates yields a simultaneous, unstudentized
    planning band.  Values are clipped to the logically possible contrast
    range ``[-1, 1]``.
    """

    rows = _validated_rows(observations)
    _validate_bootstrap(alpha, bootstrap_replicates)
    point = category_probability_contrasts(rows)
    samples = _block_bootstrap_samples(
        rows, bootstrap_replicates=bootstrap_replicates, seed=seed
    )
    max_deviations = []
    for sample in samples:
        draw = category_probability_contrasts(sample)
        max_deviations.append(
            max(abs(draw[category] - point[category]) for category in CATEGORIES)
        )
    radius = _upper_empirical_quantile(max_deviations, 1.0 - alpha)
    intervals = {
        category: ConfidenceInterval(
            estimate=point[category],
            lower=max(-1.0, point[category] - radius),
            upper=min(1.0, point[category] + radius),
        )
        for category in CATEGORIES
    }
    return CategoryContrastResult(
        contrasts=point,
        intervals=intervals,
        simultaneous_critical_radius=radius,
        alpha=alpha,
        bootstrap_replicates=bootstrap_replicates,
        seed=seed,
        n_blocks=len({row.block_id for row in rows}),
        n_by_arm={arm: sum(row.arm == arm for row in rows) for arm in ARMS},
    )


def estimate_binary_bounds(
    observations: Iterable[Observation],
    *,
    alpha: float = 0.05,
    bootstrap_replicates: int = 2_000,
    seed: int = 0,
) -> BinaryBoundsResult:
    """Expand worst/best-case binary bounds using a block bootstrap.

    Both bound endpoints are covered simultaneously using the maximum
    absolute endpoint deviation in each block-bootstrap replicate.  The lower
    endpoint expands downward and the upper endpoint expands upward.  This is
    intentionally conservative and planning-grade.
    """

    rows = _validated_rows(observations)
    _validate_bootstrap(alpha, bootstrap_replicates)
    point_lower, point_upper = binary_high_choice_bounds(rows)
    samples = _block_bootstrap_samples(
        rows, bootstrap_replicates=bootstrap_replicates, seed=seed
    )
    max_deviations = []
    for sample in samples:
        draw_lower, draw_upper = binary_high_choice_bounds(sample)
        max_deviations.append(
            max(
                abs(draw_lower - point_lower),
                abs(draw_upper - point_upper),
            )
        )
    radius = _upper_empirical_quantile(max_deviations, 1.0 - alpha)
    return BinaryBoundsResult(
        identified_lower=point_lower,
        identified_upper=point_upper,
        expanded_lower=max(-1.0, point_lower - radius),
        expanded_upper=min(1.0, point_upper + radius),
        simultaneous_critical_radius=radius,
        alpha=alpha,
        bootstrap_replicates=bootstrap_replicates,
        seed=seed,
        n_blocks=len({row.block_id for row in rows}),
        n_by_arm={arm: sum(row.arm == arm for row in rows) for arm in ARMS},
    )


def decide_binary(
    result: BinaryBoundsResult,
    *,
    delta: float,
) -> DecisionResult:
    """Apply the prespecified two-sided binary decision rule.

    Responsiveness requires the *entire uncertainty-expanded identified
    region* above ``+delta`` or below ``-delta``.  Invariance requires that
    region wholly inside ``[-delta, +delta]``.  All other cases are
    indeterminate.
    """

    if not 0.0 <= delta <= 1.0:
        raise ValueError("delta must lie between 0 and 1")
    lower, upper = result.expanded_lower, result.expanded_upper
    if lower > delta:
        return DecisionResult(
            status="responsive",
            direction="positive",
            rationale="expanded binary region lies wholly above +delta",
        )
    if upper < -delta:
        return DecisionResult(
            status="responsive",
            direction="negative",
            rationale="expanded binary region lies wholly below -delta",
        )
    if lower > -delta and upper < delta:
        return DecisionResult(
            status="invariant",
            rationale="expanded binary region lies wholly inside equivalence bounds",
        )
    return DecisionResult(
        status="indeterminate",
        rationale="expanded binary region crosses at least one decision boundary",
    )


def decide_observable_distribution(
    result: CategoryContrastResult,
    *,
    margins: Mapping[str, float],
) -> DecisionResult:
    """Decide change/equivalence for the fully observed nominal distribution.

    Invariance requires simultaneous intervals for all three category
    contrasts to lie inside their own two-sided margins.  A change requires
    at least one interval wholly beyond its margin in either direction.
    Otherwise the distribution decision is indeterminate.
    """

    if set(margins) != set(CATEGORIES):
        raise ValueError(f"margins must provide exactly {CATEGORIES}")
    if any(not 0.0 <= float(margins[category]) <= 1.0 for category in CATEGORIES):
        raise ValueError("all category margins must lie between 0 and 1")

    changed: list[str] = []
    changed_directions: list[str] = []
    all_inside = True
    for category in CATEGORIES:
        interval = result.intervals[category]
        margin = float(margins[category])
        if interval.lower > margin:
            changed.append(category)
            changed_directions.append(f"{category}:+")
        elif interval.upper < -margin:
            changed.append(category)
            changed_directions.append(f"{category}:-")
        if interval.lower <= -margin or interval.upper >= margin:
            all_inside = False

    if changed:
        return DecisionResult(
            status="changed",
            components=tuple(changed_directions),
            rationale="at least one simultaneous category interval lies beyond its margin",
        )
    if all_inside:
        return DecisionResult(
            status="invariant",
            components=CATEGORIES,
            rationale="all simultaneous category intervals lie inside their margins",
        )
    return DecisionResult(
        status="indeterminate",
        rationale="no category clears a change margin and not all clear equivalence",
    )


def decide_broad_invariance(
    binary_decision: DecisionResult,
    observable_decision: DecisionResult,
) -> DecisionResult:
    """Certify broad invariance if and only if both component rules pass."""

    if (
        binary_decision.status == "invariant"
        and observable_decision.status == "invariant"
    ):
        return DecisionResult(
            status="invariant",
            components=("binary", "observable_distribution"),
            rationale="both required invariance decisions passed",
        )
    return DecisionResult(
        status="not_established",
        components=(binary_decision.status, observable_decision.status),
        rationale="broad invariance requires binary and observable invariance",
    )


def analyze_planning_outcomes(
    observations: Iterable[Observation],
    *,
    binary_delta: float,
    category_margins: Mapping[str, float],
    alpha: float = 0.05,
    bootstrap_replicates: int = 2_000,
    seed: int = 0,
) -> PlanningAnalysis:
    """Run both co-primary planning analyses with the same bootstrap seed."""

    rows = tuple(observations)
    category = estimate_category_contrasts(
        rows,
        alpha=alpha,
        bootstrap_replicates=bootstrap_replicates,
        seed=seed,
    )
    binary = estimate_binary_bounds(
        rows,
        alpha=alpha,
        bootstrap_replicates=bootstrap_replicates,
        seed=seed,
    )
    observable_decision = decide_observable_distribution(
        category, margins=category_margins
    )
    binary_decision = decide_binary(binary, delta=binary_delta)
    return PlanningAnalysis(
        category_contrasts=category,
        binary_bounds=binary,
        observable_decision=observable_decision,
        binary_decision=binary_decision,
        broad_invariance_decision=decide_broad_invariance(
            binary_decision, observable_decision
        ),
    )


def subset_observations(
    observations: Iterable[Observation],
    *,
    model_family: str | None = None,
    target_family: str | None = None,
) -> tuple[Observation, ...]:
    """Select a fixed model/target stratum without changing any outcomes."""

    return tuple(
        row
        for row in observations
        if (model_family is None or row.model_family == model_family)
        and (target_family is None or row.target_family == target_family)
    )
