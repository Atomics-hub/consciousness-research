"""Identified observable-outcome analysis for the redesigned Binding Test.

The primary outcome is the observed nominal disposition ``D in {L, H, U}``.
No score is assigned to ``U`` and no latent choice is imputed.  The primary
estimand is therefore the complete randomized assignment contrast

``P(D=a | assigned self) - P(D=a | assigned yoke), a in {L, H, U}``.

Planning-only simultaneous intervals for that vector provisionally support
two distinct identified-outcome descriptions: a meaningful distributional
change, or equivalence of the observed distribution within category-specific
margins.  A separate observed-disposition reallocation label requires the
paired pattern ``H`` up and ``L`` down (or its exact reverse).  This rejects
simple availability co-movement, but choice-dependent availability can still
produce the paired pattern.  The label is explicitly not latent choice
responsiveness.  ``U`` remains nominal, reported, and unscored.

Worst/best-case bounds for a *latent* binary high choice remain available,
but only as secondary sensitivity analysis.  They are not part of the
primary decision function and cannot veto an identified observable-
distribution equivalence claim.

The interval engine is reused from :mod:`estimands`: it is a deterministic,
planning-grade block bootstrap, not the final confirmatory restricted-
randomization analysis.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
import math
from typing import Iterable, Mapping

from .estimands import (
    ARMS,
    CATEGORIES,
    PLANNING_BOOTSTRAP_METHOD,
    BinaryBoundsResult,
    CategoryContrastResult,
    ConfidenceInterval,
    Observation,
    estimate_binary_bounds,
    estimate_category_contrasts,
)


# Contrasts and margins live on [-1, 1].  Treat differences at ordinary
# floating-point roundoff as equality to a boundary, which is the conservative
# implementation of strict (open-set) decision rules.
BOUNDARY_ABS_TOLERANCE = 1e-12
COMPOSITION_ABS_TOLERANCE = 1e-9
INFERENCE_ROLE = "planning_only/provisional"
STRICT_BOUNDARY_POLICY = (
    "all decision inequalities are strict; values within 1e-12 of a boundary "
    "are treated as on the boundary and therefore do not pass"
)
SECONDARY_BINARY_ROLE = (
    "planning-only secondary assumption-free sensitivity for a latent binary "
    "high choice; never a gate on the identified observable-distribution claim"
)


class _JsonRecord:
    """Mixin for dataclass records with strict standard-JSON serialization."""

    def to_dict(self) -> dict[str, object]:
        return asdict(self)  # type: ignore[arg-type]

    def to_json(self, **kwargs: object) -> str:
        options = {"allow_nan": False, **kwargs}
        return json.dumps(self.to_dict(), **options)


def _require_nonempty_text(name: str, value: object) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")


@dataclass(frozen=True)
class ModelTargetStratum(_JsonRecord):
    """One prospectively declared model-family by target-family stratum."""

    model_family: str
    target_family: str

    def __post_init__(self) -> None:
        _require_nonempty_text("model_family", self.model_family)
        _require_nonempty_text("target_family", self.target_family)


@dataclass(frozen=True)
class ClaimScope(_JsonRecord):
    """Prospectively declared population and limits of the identified claim.

    ``population`` and ``claim_scope`` are deliberately mandatory: an
    analysis cannot silently generalize beyond the supplied randomized
    sessions.  The default contrast describes assignment (an ITT-style
    contrast), not receipt of a latent treatment state.
    """

    population: str
    claim_scope: str
    generalization_limit: str
    declared_strata: tuple[ModelTargetStratum, ...]
    assignment_contrast: str = (
        "assignment to self-contingent enforcement minus assignment to the "
        "schedule-matched yoke arm"
    )
    analysis_unit: str = "eligible randomized Binding Test session"
    outcome_definition: str = (
        "observed follow-up disposition D with nominal support {L, H, U}"
    )

    def __post_init__(self) -> None:
        for name in (
            "population",
            "claim_scope",
            "generalization_limit",
            "assignment_contrast",
            "analysis_unit",
            "outcome_definition",
        ):
            _require_nonempty_text(name, getattr(self, name))
        if not isinstance(self.declared_strata, tuple) or not self.declared_strata:
            raise ValueError("declared_strata must be a non-empty tuple")
        if not all(
            isinstance(stratum, ModelTargetStratum)
            for stratum in self.declared_strata
        ):
            raise TypeError(
                "declared_strata must contain only ModelTargetStratum instances"
            )
        declared_pairs = {
            (stratum.model_family, stratum.target_family)
            for stratum in self.declared_strata
        }
        if len(declared_pairs) != len(self.declared_strata):
            raise ValueError("declared_strata cannot contain duplicates")


@dataclass(frozen=True)
class ObservableMultinomialResult(_JsonRecord):
    """Observed arm probabilities and their simultaneous vector contrast."""

    categories: tuple[str, ...]
    observed_strata: tuple[ModelTargetStratum, ...]
    arm_probabilities: dict[str, dict[str, float]]
    contrast: CategoryContrastResult
    inference_role: str = INFERENCE_ROLE
    estimand: str = (
        "for every a in {L,H,U}, P(D=a | assigned self) - "
        "P(D=a | assigned yoke)"
    )
    category_scale: str = "nominal; U is observed and is not ordered or imputed"


@dataclass(frozen=True)
class ObservableComponentDecision(_JsonRecord):
    """Strict change/equivalence decision for one vector component."""

    category: str
    estimate: float
    lower: float
    upper: float
    margin: float
    status: str
    direction: str | None
    inference_role: str = INFERENCE_ROLE


@dataclass(frozen=True)
class ObservableVectorDecision(_JsonRecord):
    """Decision for the complete observed ``L/H/U`` contrast vector."""

    status: str
    components: dict[str, ObservableComponentDecision]
    changed_components: tuple[str, ...]
    equivalent_components: tuple[str, ...]
    indeterminate_components: tuple[str, ...]
    simultaneous: bool
    alpha: float
    boundary_policy: str
    rationale: str
    inference_role: str = INFERENCE_ROLE


@dataclass(frozen=True)
class ObservedDispositionReallocationDecision(_JsonRecord):
    """Paired observed-disposition reallocation with nominal ``U`` reported."""

    status: str
    direction: str | None
    h_interval: ConfidenceInterval
    l_interval: ConfidenceInterval
    u_interval: ConfidenceInterval
    minimum_effect: float
    simultaneous_interval_used: bool
    boundary_policy: str
    rationale: str
    interpretation_limit: str = (
        "an observed L/H reallocation only; not latent choice responsiveness "
        "and not a mechanism claim"
    )
    inference_role: str = INFERENCE_ROLE


@dataclass(frozen=True)
class ProvisionalDecision(_JsonRecord):
    """Generic planning-only decision used by secondary sensitivity outputs."""

    status: str
    direction: str | None = None
    components: tuple[str, ...] = ()
    rationale: str = ""
    inference_role: str = INFERENCE_ROLE


@dataclass(frozen=True)
class SecondaryBinarySensitivity(_JsonRecord):
    """Non-blocking partial-identification sensitivity for latent high choice."""

    bounds: BinaryBoundsResult
    decision: ProvisionalDecision
    analysis_role: str = SECONDARY_BINARY_ROLE
    can_block_identified_observable_claim: bool = field(default=False, init=False)
    inference_role: str = INFERENCE_ROLE


@dataclass(frozen=True)
class IdentifiedObservableClaim(_JsonRecord):
    """Primary claim derived solely from the observed multinomial decision."""

    status: str
    observable_distribution_status: str
    provisional_negative_equivalence_supported: bool
    basis: tuple[str, ...]
    secondary_binary_sensitivity_used_in_primary_claim: bool = field(
        default=False, init=False
    )
    rationale: str = ""
    inference_role: str = INFERENCE_ROLE


@dataclass(frozen=True)
class RedesignedAnalysis(_JsonRecord):
    """Complete revised analysis with a hard primary/secondary separation."""

    scope: ClaimScope
    observable_multinomial: ObservableMultinomialResult
    observable_distribution_decision: ObservableVectorDecision
    identified_observable_claim: IdentifiedObservableClaim
    observed_disposition_reallocation: ObservedDispositionReallocationDecision
    secondary_binary_sensitivity: SecondaryBinarySensitivity
    inference_role: str = INFERENCE_ROLE

    def __post_init__(self) -> None:
        expected = _primary_claim_from_observable(
            self.observable_distribution_decision
        )
        if self.identified_observable_claim != expected:
            raise ValueError(
                "identified_observable_claim must be determined only by the "
                "observable distribution decision"
            )
        if self.secondary_binary_sensitivity.can_block_identified_observable_claim:
            raise ValueError("secondary binary sensitivity must be non-blocking")
        if set(self.scope.declared_strata) != set(
            self.observable_multinomial.observed_strata
        ):
            raise ValueError(
                "declared scope strata must exactly match observed data strata"
            )


def _finite_unit_value(name: str, value: object, *, positive: bool) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a finite numeric value")
    try:
        numeric = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a finite numeric value") from exc
    lower_ok = numeric > 0.0 if positive else numeric >= 0.0
    if not math.isfinite(numeric) or not lower_ok or numeric > 1.0:
        relation = "strictly above 0 and" if positive else "between 0 and"
        raise ValueError(f"{name} must be {relation} 1")
    return numeric


def _finite_number(name: str, value: object) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a finite numeric value")
    try:
        numeric = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a finite numeric value") from exc
    if not math.isfinite(numeric):
        raise ValueError(f"{name} must be finite")
    return numeric


def _strictly_above(value: float, boundary: float) -> bool:
    return value > boundary and not math.isclose(
        value, boundary, rel_tol=0.0, abs_tol=BOUNDARY_ABS_TOLERANCE
    )


def _strictly_below(value: float, boundary: float) -> bool:
    return value < boundary and not math.isclose(
        value, boundary, rel_tol=0.0, abs_tol=BOUNDARY_ABS_TOLERANCE
    )


def _validated_margins(margins: Mapping[str, float]) -> dict[str, float]:
    if set(margins) != set(CATEGORIES):
        raise ValueError(f"margins must provide exactly {CATEGORIES}")
    return {
        category: _finite_unit_value(
            f"margin[{category}]", margins[category], positive=True
        )
        for category in CATEGORIES
    }


def _validate_planning_metadata(
    *,
    method: object,
    alpha: object,
    bootstrap_replicates: object,
    seed: object,
    n_blocks: object,
    n_by_arm: object,
) -> None:
    """Reject records without compatible simultaneous planning provenance."""

    if method != PLANNING_BOOTSTRAP_METHOD:
        raise ValueError(
            "unsupported interval provenance: expected the planning-grade "
            "simultaneous block-bootstrap method"
        )
    alpha_value = _finite_number("alpha", alpha)
    if not 0.0 < alpha_value < 1.0:
        raise ValueError("alpha must lie strictly between 0 and 1")
    if (
        isinstance(bootstrap_replicates, bool)
        or not isinstance(bootstrap_replicates, int)
        or bootstrap_replicates < 1
    ):
        raise ValueError("bootstrap_replicates must be a positive integer")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("seed must be an integer")
    if isinstance(n_blocks, bool) or not isinstance(n_blocks, int) or n_blocks < 2:
        raise ValueError("n_blocks must be an integer of at least two")
    if not isinstance(n_by_arm, Mapping) or set(n_by_arm) != set(ARMS):
        raise ValueError(f"n_by_arm must provide exactly {ARMS}")
    for arm in ARMS:
        count = n_by_arm[arm]
        if isinstance(count, bool) or not isinstance(count, int) or count < 1:
            raise ValueError(f"n_by_arm[{arm}] must be a positive integer")


def _validate_category_contrast_result(result: object) -> CategoryContrastResult:
    """Defensively validate a simultaneous multinomial contrast record."""

    if not isinstance(result, CategoryContrastResult):
        raise TypeError("result must be a CategoryContrastResult")
    if set(result.contrasts) != set(CATEGORIES):
        raise ValueError(f"result contrasts must provide exactly {CATEGORIES}")
    if set(result.intervals) != set(CATEGORIES):
        raise ValueError(f"result intervals must provide exactly {CATEGORIES}")
    _validate_planning_metadata(
        method=result.method,
        alpha=result.alpha,
        bootstrap_replicates=result.bootstrap_replicates,
        seed=result.seed,
        n_blocks=result.n_blocks,
        n_by_arm=result.n_by_arm,
    )
    radius = _finite_number(
        "simultaneous_critical_radius", result.simultaneous_critical_radius
    )
    if radius < 0.0 or radius > 2.0:
        raise ValueError("simultaneous_critical_radius must lie between 0 and 2")

    contrast_values: list[float] = []
    for category in CATEGORIES:
        contrast = _finite_number(
            f"contrasts[{category}]", result.contrasts[category]
        )
        interval = result.intervals[category]
        if not isinstance(interval, ConfidenceInterval):
            raise TypeError(
                f"intervals[{category}] must be a ConfidenceInterval"
            )
        estimate = _finite_number(
            f"intervals[{category}].estimate", interval.estimate
        )
        lower = _finite_number(f"intervals[{category}].lower", interval.lower)
        upper = _finite_number(f"intervals[{category}].upper", interval.upper)
        if not -1.0 <= lower <= upper <= 1.0:
            raise ValueError(
                f"intervals[{category}] must be ordered within [-1, 1]"
            )
        if not lower <= estimate <= upper:
            raise ValueError(
                f"intervals[{category}] must contain its estimate"
            )
        if not math.isclose(
            estimate,
            contrast,
            rel_tol=0.0,
            abs_tol=BOUNDARY_ABS_TOLERANCE,
        ):
            raise ValueError(
                f"interval estimate and contrast disagree for {category}"
            )
        expected_lower = max(-1.0, estimate - radius)
        expected_upper = min(1.0, estimate + radius)
        if not math.isclose(
            lower,
            expected_lower,
            rel_tol=0.0,
            abs_tol=BOUNDARY_ABS_TOLERANCE,
        ) or not math.isclose(
            upper,
            expected_upper,
            rel_tol=0.0,
            abs_tol=BOUNDARY_ABS_TOLERANCE,
        ):
            raise ValueError(
                f"intervals[{category}] are incompatible with the declared "
                "common simultaneous radius"
            )
        contrast_values.append(contrast)
    if not math.isclose(
        sum(contrast_values),
        0.0,
        rel_tol=0.0,
        abs_tol=COMPOSITION_ABS_TOLERANCE,
    ):
        raise ValueError("L/H/U probability contrasts must sum to zero")
    return result


def _validate_binary_bounds_result(result: object) -> BinaryBoundsResult:
    """Defensively validate ordered, expanded partial-identification bounds."""

    if not isinstance(result, BinaryBoundsResult):
        raise TypeError("result must be a BinaryBoundsResult")
    _validate_planning_metadata(
        method=result.method,
        alpha=result.alpha,
        bootstrap_replicates=result.bootstrap_replicates,
        seed=result.seed,
        n_blocks=result.n_blocks,
        n_by_arm=result.n_by_arm,
    )
    identified_lower = _finite_number(
        "identified_lower", result.identified_lower
    )
    identified_upper = _finite_number(
        "identified_upper", result.identified_upper
    )
    expanded_lower = _finite_number("expanded_lower", result.expanded_lower)
    expanded_upper = _finite_number("expanded_upper", result.expanded_upper)
    radius = _finite_number(
        "simultaneous_critical_radius", result.simultaneous_critical_radius
    )
    if radius < 0.0 or radius > 2.0:
        raise ValueError("simultaneous_critical_radius must lie between 0 and 2")
    if not (
        -1.0
        <= expanded_lower
        <= identified_lower
        <= identified_upper
        <= expanded_upper
        <= 1.0
    ):
        raise ValueError(
            "binary bounds must be finite, ordered, and nested within [-1, 1]"
        )
    expected_lower = max(-1.0, identified_lower - radius)
    expected_upper = min(1.0, identified_upper + radius)
    if not math.isclose(
        expanded_lower,
        expected_lower,
        rel_tol=0.0,
        abs_tol=BOUNDARY_ABS_TOLERANCE,
    ) or not math.isclose(
        expanded_upper,
        expected_upper,
        rel_tol=0.0,
        abs_tol=BOUNDARY_ABS_TOLERANCE,
    ):
        raise ValueError(
            "expanded binary bounds are incompatible with the declared "
            "simultaneous radius"
        )
    return result


def observed_arm_probabilities(
    observations: Iterable[Observation],
) -> dict[str, dict[str, float]]:
    """Return the complete observed multinomial distribution in each arm."""

    rows = tuple(observations)
    if not rows:
        raise ValueError("at least one observation is required")
    if not all(isinstance(row, Observation) for row in rows):
        raise TypeError("all observations must be Observation instances")
    totals = {arm: 0 for arm in ARMS}
    counts = {
        arm: {category: 0 for category in CATEGORIES}
        for arm in ARMS
    }
    for row in rows:
        totals[row.arm] += 1
        counts[row.arm][row.category] += 1
    if any(totals[arm] == 0 for arm in ARMS):
        raise ValueError("both self and yoke arms must contain observations")
    return {
        arm: {
            category: counts[arm][category] / totals[arm]
            for category in CATEGORIES
        }
        for arm in ARMS
    }


def observed_model_target_strata(
    observations: Iterable[Observation],
) -> tuple[ModelTargetStratum, ...]:
    """Return the exact model-by-target coverage represented in the rows."""

    rows = tuple(observations)
    if not rows:
        raise ValueError("at least one observation is required")
    if not all(isinstance(row, Observation) for row in rows):
        raise TypeError("all observations must be Observation instances")
    pairs = {
        ModelTargetStratum(row.model_family, row.target_family)
        for row in rows
    }
    return tuple(
        sorted(pairs, key=lambda item: (item.model_family, item.target_family))
    )


def _validate_declared_coverage(
    scope: ClaimScope,
    observed: tuple[ModelTargetStratum, ...],
) -> None:
    declared_pairs = {
        (item.model_family, item.target_family)
        for item in scope.declared_strata
    }
    observed_pairs = {
        (item.model_family, item.target_family)
        for item in observed
    }
    if declared_pairs != observed_pairs:
        unobserved_claims = sorted(declared_pairs - observed_pairs)
        undeclared_data = sorted(observed_pairs - declared_pairs)
        raise ValueError(
            "declared_strata must exactly equal observed model/target coverage; "
            f"declared_but_unobserved={unobserved_claims}, "
            f"observed_but_undeclared={undeclared_data}"
        )


def decide_observable_probability_vector(
    result: CategoryContrastResult,
    *,
    margins: Mapping[str, float],
) -> ObservableVectorDecision:
    """Apply simultaneous strict decisions to all observed categories.

    A component changes only if its entire interval is strictly outside its
    two-sided margin.  It is equivalent only if its entire interval is
    strictly inside.  Equality (including floating-point equality within
    :data:`BOUNDARY_ABS_TOLERANCE`) is indeterminate.
    """

    result = _validate_category_contrast_result(result)
    margin_map = _validated_margins(margins)

    components: dict[str, ObservableComponentDecision] = {}
    for category in CATEGORIES:
        interval = result.intervals[category]
        margin = margin_map[category]
        direction: str | None = None
        if _strictly_above(interval.lower, margin):
            status = "provisional_changed"
            direction = "increase"
        elif _strictly_below(interval.upper, -margin):
            status = "provisional_changed"
            direction = "decrease"
        elif _strictly_above(interval.lower, -margin) and _strictly_below(
            interval.upper, margin
        ):
            status = "provisional_equivalent"
        else:
            status = "provisional_indeterminate"
        components[category] = ObservableComponentDecision(
            category=category,
            estimate=interval.estimate,
            lower=interval.lower,
            upper=interval.upper,
            margin=margin,
            status=status,
            direction=direction,
        )

    changed = tuple(
        category
        for category in CATEGORIES
        if components[category].status == "provisional_changed"
    )
    equivalent = tuple(
        category
        for category in CATEGORIES
        if components[category].status == "provisional_equivalent"
    )
    indeterminate = tuple(
        category
        for category in CATEGORIES
        if components[category].status == "provisional_indeterminate"
    )
    if changed:
        status = "provisional_changed"
        rationale = (
            "the planning band provisionally places at least one simultaneous "
            "category interval strictly outside its equivalence margin"
        )
    elif len(equivalent) == len(CATEGORIES):
        status = "provisional_equivalent"
        rationale = (
            "the planning band provisionally places all simultaneous category "
            "intervals strictly inside their equivalence margins"
        )
    else:
        status = "provisional_indeterminate"
        rationale = (
            "the planning band supports neither a provisional change label nor "
            "provisional equivalence for every component"
        )
    return ObservableVectorDecision(
        status=status,
        components=components,
        changed_components=changed,
        equivalent_components=equivalent,
        indeterminate_components=indeterminate,
        simultaneous=True,
        alpha=result.alpha,
        boundary_policy=STRICT_BOUNDARY_POLICY,
        rationale=rationale,
    )


def decide_observed_disposition_reallocation(
    result: CategoryContrastResult,
    *,
    minimum_effect: float,
) -> ObservedDispositionReallocationDecision:
    """Describe an opposing observed ``H``/``L`` reallocation under assignment.

    A positive reallocation requires the simultaneous ``H`` lower bound strictly
    above ``+minimum_effect`` *and* the ``L`` upper bound strictly below
    ``-minimum_effect``.  The exact reverse is labeled a negative reallocation.
    Movement in ``U`` is kept visible but is neither scored nor used as a
    substitute for either disposition component.  Even a passing pattern is
    not evidence of latent choice responsiveness: choice-dependent availability
    can produce the same observed reallocation.
    """

    result = _validate_category_contrast_result(result)
    threshold = _finite_unit_value(
        "minimum_effect", minimum_effect, positive=False
    )
    h_interval = result.intervals["H"]
    l_interval = result.intervals["L"]
    u_interval = result.intervals["U"]
    positive = _strictly_above(
        h_interval.lower, threshold
    ) and _strictly_below(l_interval.upper, -threshold)
    negative = _strictly_below(
        h_interval.upper, -threshold
    ) and _strictly_above(l_interval.lower, threshold)
    if positive:
        status = "provisional_positive_reallocation"
        direction = "H_increase_L_decrease"
        rationale = (
            "simultaneous bounds place H strictly above +minimum_effect and "
            "L strictly below -minimum_effect in the observed dispositions"
        )
    elif negative:
        status = "provisional_negative_reallocation"
        direction = "H_decrease_L_increase"
        rationale = (
            "simultaneous bounds place H strictly below -minimum_effect and "
            "L strictly above +minimum_effect in the observed dispositions"
        )
    else:
        status = "provisional_not_demonstrated"
        direction = None
        rationale = (
            "simultaneous H and L bounds do not demonstrate an opposing "
            "observed-disposition reallocation; U remains nominal"
        )
    return ObservedDispositionReallocationDecision(
        status=status,
        direction=direction,
        h_interval=h_interval,
        l_interval=l_interval,
        u_interval=u_interval,
        minimum_effect=threshold,
        simultaneous_interval_used=True,
        boundary_policy=STRICT_BOUNDARY_POLICY,
        rationale=rationale,
    )


def decide_secondary_binary_sensitivity(
    result: BinaryBoundsResult,
    *,
    delta: float,
) -> ProvisionalDecision:
    """Apply strict decisions to latent binary bounds as secondary sensitivity."""

    result = _validate_binary_bounds_result(result)
    margin = _finite_unit_value("delta", delta, positive=False)
    lower, upper = result.expanded_lower, result.expanded_upper
    if _strictly_above(lower, margin):
        return ProvisionalDecision(
            status="provisional_responsive",
            direction="positive",
            rationale="secondary binary region lies strictly above +delta",
        )
    if _strictly_below(upper, -margin):
        return ProvisionalDecision(
            status="provisional_responsive",
            direction="negative",
            rationale="secondary binary region lies strictly below -delta",
        )
    if _strictly_above(lower, -margin) and _strictly_below(upper, margin):
        return ProvisionalDecision(
            status="provisional_invariant",
            rationale=(
                "secondary binary region lies strictly inside equivalence bounds"
            ),
        )
    return ProvisionalDecision(
        status="provisional_indeterminate",
        rationale=(
            "secondary binary region touches or crosses a decision boundary"
        ),
    )


def _primary_claim_from_observable(
    decision: ObservableVectorDecision,
) -> IdentifiedObservableClaim:
    if decision.status == "provisional_equivalent":
        return IdentifiedObservableClaim(
            status="provisional_observable_equivalence",
            observable_distribution_status=decision.status,
            provisional_negative_equivalence_supported=True,
            basis=CATEGORIES,
            rationale=(
                "the planning band provisionally supports equivalence only "
                "for the observed L/H/U distribution"
            ),
        )
    if decision.status == "provisional_changed":
        return IdentifiedObservableClaim(
            status="provisional_observable_change",
            observable_distribution_status=decision.status,
            provisional_negative_equivalence_supported=False,
            basis=CATEGORIES,
            rationale=(
                "the planning band provisionally supports a meaningful change "
                "in the observed L/H/U distribution"
            ),
        )
    return IdentifiedObservableClaim(
        status="provisional_indeterminate",
        observable_distribution_status=decision.status,
        provisional_negative_equivalence_supported=False,
        basis=CATEGORIES,
        rationale="the observed L/H/U vector is indeterminate",
    )


def analyze_redesigned_outcomes(
    observations: Iterable[Observation],
    *,
    scope: ClaimScope,
    category_margins: Mapping[str, float],
    minimum_observed_reallocation: float,
    binary_sensitivity_delta: float,
    alpha: float = 0.05,
    bootstrap_replicates: int = 2_000,
    seed: int = 0,
) -> RedesignedAnalysis:
    """Run the revised identified analysis and non-blocking sensitivity.

    The primary claim is a pure function of ``observable_decision``.  Binary
    bounds are calculated and reported afterwards; their status is never an
    input to :class:`IdentifiedObservableClaim`.
    """

    if not isinstance(scope, ClaimScope):
        raise TypeError("scope must be a ClaimScope")
    rows = tuple(observations)
    observed_strata = observed_model_target_strata(rows)
    _validate_declared_coverage(scope, observed_strata)
    contrast = estimate_category_contrasts(
        rows,
        alpha=alpha,
        bootstrap_replicates=bootstrap_replicates,
        seed=seed,
    )
    observable = ObservableMultinomialResult(
        categories=CATEGORIES,
        observed_strata=observed_strata,
        arm_probabilities=observed_arm_probabilities(rows),
        contrast=contrast,
    )
    observable_decision = decide_observable_probability_vector(
        contrast, margins=category_margins
    )
    reallocation_decision = decide_observed_disposition_reallocation(
        contrast, minimum_effect=minimum_observed_reallocation
    )

    binary_bounds = estimate_binary_bounds(
        rows,
        alpha=alpha,
        bootstrap_replicates=bootstrap_replicates,
        seed=seed,
    )
    binary_decision = decide_secondary_binary_sensitivity(
        binary_bounds, delta=binary_sensitivity_delta
    )
    binary_sensitivity = SecondaryBinarySensitivity(
        bounds=binary_bounds,
        decision=binary_decision,
    )
    return RedesignedAnalysis(
        scope=scope,
        observable_multinomial=observable,
        observable_distribution_decision=observable_decision,
        identified_observable_claim=_primary_claim_from_observable(
            observable_decision
        ),
        observed_disposition_reallocation=reallocation_decision,
        secondary_binary_sensitivity=binary_sensitivity,
    )
