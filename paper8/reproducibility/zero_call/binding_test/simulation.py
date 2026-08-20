"""Seeded synthetic outcome generators for Binding Test zero-call planning.

These scenarios test whether the analysis pipeline behaves sensibly; they do
not assert that any provider or model will exhibit the simulated behavior.
The ``mechanism_alias`` scenario intentionally has the same observable arm
distribution as ``positive`` while assigning the effect to a perfectly
collinear generic mechanism signal.  It encodes the design's mechanism
non-identifiability without a valid comparator.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import random
from typing import Iterable, Mapping, Sequence

from .estimands import (
    ARMS,
    CATEGORIES,
    Observation,
    analyze_planning_outcomes,
    subset_observations,
)


SCENARIOS: tuple[str, ...] = (
    "null",
    "positive",
    "negative",
    "availability_only",
    "one_model_only",
    "mechanism_alias",
    "equivalence_boundary",
)


@dataclass(frozen=True)
class ScenarioTruth:
    """Design truth used to generate a synthetic dataset."""

    scenario: str
    effect_direction: str
    enforcement_mechanism_identified: bool
    affected_models: tuple[str, ...]
    interpretation: str


@dataclass(frozen=True)
class SyntheticDataset:
    """A replayable synthetic dataset and its simulation-only truth labels."""

    observations: tuple[Observation, ...]
    truth: ScenarioTruth
    seed: int
    n_blocks_per_model_target: int
    sessions_per_arm_block: int

    def subset(
        self,
        *,
        model_family: str | None = None,
        target_family: str | None = None,
    ) -> tuple[Observation, ...]:
        return tuple(
            row
            for row in self.observations
            if (model_family is None or row.model_family == model_family)
            and (target_family is None or row.target_family == target_family)
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    def to_json(self, **kwargs: object) -> str:
        return json.dumps(self.to_dict(), **kwargs)


@dataclass(frozen=True)
class MonteCarloDecisionCell:
    """Decision frequencies for one scenario × block-count × U-rate cell.

    ``followup_unavailability`` is the common arm rate except in the
    ``availability_only`` stress case, where it is the yoke/base rate and the
    self arm adds the declared availability shift.
    """

    scenario: str
    blocks_per_model_target: int
    followup_unavailability: float
    simulation_replicates: int
    bootstrap_replicates: int
    sessions_per_arm_block: int
    alpha: float
    binary_delta: float
    category_margins: dict[str, float]
    pooled_binary_rates: dict[str, float]
    pooled_binary_direction_rates: dict[str, float]
    pooled_observable_rates: dict[str, float]
    pooled_broad_invariance_rate: float
    all_strata_same_direction_binary_responsive_rate: float | None
    all_strata_binary_invariant_rate: float | None
    all_strata_observable_invariant_rate: float | None
    all_strata_broad_invariant_rate: float | None
    false_binary_categorical_rate: float | None
    false_observable_categorical_rate: float | None
    false_categorical_tolerance: float
    binary_false_rate_within_tolerance: bool | None
    observable_false_rate_within_tolerance: bool | None


@dataclass(frozen=True)
class MonteCarloGrid:
    """A replayable collection of planning-grade Monte Carlo cells."""

    master_seed: int
    scenarios: tuple[str, ...]
    block_counts: tuple[int, ...]
    followup_unavailability_levels: tuple[float, ...]
    simulation_replicates: int
    bootstrap_replicates: int
    cross_stratum_certificates: bool
    cells: tuple[MonteCarloDecisionCell, ...]
    method: str = (
        "seeded synthetic Monte Carlo with planning-grade stratified block "
        "bootstrap; not final confirmatory inference"
    )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    def to_json(self, **kwargs: object) -> str:
        return json.dumps(self.to_dict(), **kwargs)


def _validate_probability_vector(probabilities: Sequence[float]) -> None:
    if len(probabilities) != len(CATEGORIES):
        raise ValueError("probability vector must have L, H, and U entries")
    if any(value < 0.0 or value > 1.0 for value in probabilities):
        raise ValueError("category probabilities must lie between 0 and 1")
    if abs(sum(probabilities) - 1.0) > 1e-9:
        raise ValueError("category probabilities must sum to one")


def scenario_probabilities(
    scenario: str,
    *,
    arm: str,
    model_family: str,
    first_model: str,
    effect_size: float = 0.30,
    availability_shift: float = 0.20,
    base_unavailability: float = 0.04,
) -> tuple[float, float, float]:
    """Return nominal ``(P(L), P(H), P(U))`` for one scenario cell.

    ``availability_only`` preserves the latent 50/50 L/H mix among available
    outcomes while changing only the probability of becoming unavailable.
    ``mechanism_alias`` deliberately returns the same observable probabilities
    as ``positive``.
    """

    if scenario not in SCENARIOS:
        raise ValueError(f"scenario must be one of {SCENARIOS}; got {scenario!r}")
    if arm not in ARMS:
        raise ValueError(f"arm must be one of {ARMS}; got {arm!r}")
    if not 0.0 <= base_unavailability < 1.0:
        raise ValueError("base_unavailability must lie in [0, 1)")
    maximum_shift = (1.0 - base_unavailability) / 2.0
    effect_scenarios = {
        "positive",
        "negative",
        "one_model_only",
        "mechanism_alias",
        "equivalence_boundary",
    }
    if scenario in effect_scenarios and not 0.0 <= effect_size <= maximum_shift:
        raise ValueError(
            "effect_size must be no larger than half the available mass "
            f"({maximum_shift:.6f})"
        )
    if not 0.0 <= availability_shift <= 1.0:
        raise ValueError("availability_shift must lie between 0 and 1")
    if scenario == "availability_only" and base_unavailability + availability_shift > 1.0:
        raise ValueError("base_unavailability + availability_shift cannot exceed one")

    base_u = base_unavailability
    base_h = (1.0 - base_u) / 2.0
    base_l = base_h
    active = arm == "self"

    if scenario == "availability_only":
        unavailable = base_u + (availability_shift if active else 0.0)
        available = 1.0 - unavailable
        probabilities = (available / 2.0, available / 2.0, unavailable)
    else:
        signed_effect = 0.0
        if active and scenario in {
            "positive",
            "mechanism_alias",
            "equivalence_boundary",
        }:
            signed_effect = effect_size
        elif active and scenario == "negative":
            signed_effect = -effect_size
        elif active and scenario == "one_model_only" and model_family == first_model:
            signed_effect = effect_size
        probabilities = (
            base_l - signed_effect,
            base_h + signed_effect,
            base_u,
        )

    _validate_probability_vector(probabilities)
    return probabilities


def _draw_category(
    rng: random.Random,
    probabilities: tuple[float, float, float],
) -> str:
    draw = rng.random()
    cumulative = 0.0
    for category, probability in zip(CATEGORIES, probabilities):
        cumulative += probability
        if draw < cumulative:
            return category
    return "U"  # Floating-point guard; probabilities were already validated.


def _truth_for(scenario: str, model_families: tuple[str, ...]) -> ScenarioTruth:
    first_model = model_families[0]
    if scenario == "null":
        return ScenarioTruth(
            scenario=scenario,
            effect_direction="none",
            enforcement_mechanism_identified=False,
            affected_models=(),
            interpretation="No arm effect on any observed category.",
        )
    if scenario == "positive":
        return ScenarioTruth(
            scenario=scenario,
            effect_direction="positive",
            enforcement_mechanism_identified=False,
            affected_models=model_families,
            interpretation=(
                "Positive observable self-versus-yoke effect; the generator does "
                "not by itself identify a workload-control-specific mechanism."
            ),
        )
    if scenario == "negative":
        return ScenarioTruth(
            scenario=scenario,
            effect_direction="negative",
            enforcement_mechanism_identified=False,
            affected_models=model_families,
            interpretation="Negative observable self-versus-yoke effect.",
        )
    if scenario == "availability_only":
        return ScenarioTruth(
            scenario=scenario,
            effect_direction="availability_only",
            enforcement_mechanism_identified=False,
            affected_models=model_families,
            interpretation=(
                "Treatment changes availability while preserving the latent "
                "L/H mix among available outcomes."
            ),
        )
    if scenario == "one_model_only":
        return ScenarioTruth(
            scenario=scenario,
            effect_direction="positive_one_model",
            enforcement_mechanism_identified=False,
            affected_models=(first_model,),
            interpretation="Only the first fixed model family has an arm effect.",
        )
    if scenario == "equivalence_boundary":
        return ScenarioTruth(
            scenario=scenario,
            effect_direction="positive_boundary",
            enforcement_mechanism_identified=False,
            affected_models=model_families,
            interpretation=(
                "The category-probability shift is exactly the supplied effect "
                "size, used by the grid as the strict decision boundary."
            ),
        )
    return ScenarioTruth(
        scenario=scenario,
        effect_direction="positive_alias",
        enforcement_mechanism_identified=False,
        affected_models=model_families,
        interpretation=(
            "Observable probabilities equal the positive scenario, but a generic "
            "mechanism signal is perfectly collinear with arm; mechanism is aliased."
        ),
    )


def generate_synthetic_outcomes(
    scenario: str,
    *,
    seed: int,
    n_blocks_per_model_target: int = 40,
    sessions_per_arm_block: int = 4,
    model_families: Iterable[str] = ("model_a", "model_b", "model_c"),
    target_families: Iterable[str] = ("work_score", "tool_budget"),
    effect_size: float = 0.30,
    availability_shift: float = 0.20,
    base_unavailability: float = 0.04,
) -> SyntheticDataset:
    """Generate a balanced, block-clustered synthetic planning dataset.

    Every block contains both arms, so resampling blocks preserves treatment
    support.  Model and target families are fixed labels rather than samples
    from a superpopulation.  Reusing the same seed and arguments reproduces
    the dataset byte-for-byte after JSON serialization.
    """

    if scenario not in SCENARIOS:
        raise ValueError(f"scenario must be one of {SCENARIOS}; got {scenario!r}")
    if n_blocks_per_model_target < 2:
        raise ValueError("n_blocks_per_model_target must be at least two")
    if sessions_per_arm_block < 1:
        raise ValueError("sessions_per_arm_block must be positive")
    models = tuple(model_families)
    targets = tuple(target_families)
    if not models or not targets:
        raise ValueError("at least one model and target family are required")
    if len(set(models)) != len(models) or len(set(targets)) != len(targets):
        raise ValueError("model and target family labels must be unique")

    rng = random.Random(seed)
    first_model = models[0]
    rows: list[Observation] = []
    for model in models:
        for target in targets:
            for block_index in range(n_blocks_per_model_target):
                block_id = f"{model}|{target}|{block_index:04d}"
                for arm in ARMS:
                    probabilities = scenario_probabilities(
                        scenario,
                        arm=arm,
                        model_family=model,
                        first_model=first_model,
                        effect_size=effect_size,
                        availability_shift=availability_shift,
                        base_unavailability=base_unavailability,
                    )
                    for _ in range(sessions_per_arm_block):
                        rows.append(
                            Observation(
                                block_id=block_id,
                                arm=arm,
                                category=_draw_category(rng, probabilities),
                                model_family=model,
                                target_family=target,
                                mechanism_signal=(
                                    arm == "self"
                                    if scenario == "mechanism_alias"
                                    else None
                                ),
                            )
                        )

    return SyntheticDataset(
        observations=tuple(rows),
        truth=_truth_for(scenario, models),
        seed=seed,
        n_blocks_per_model_target=n_blocks_per_model_target,
        sessions_per_arm_block=sessions_per_arm_block,
    )


def _derived_seed(master_seed: int, *parts: object) -> int:
    material = "|".join((str(master_seed), *(str(part) for part in parts)))
    return int.from_bytes(hashlib.sha256(material.encode("utf-8")).digest()[:16], "big")


def _rates(counts: Mapping[str, int], denominator: int) -> dict[str, float]:
    return {key: counts[key] / denominator for key in sorted(counts)}


def _increment(counts: dict[str, int], key: str) -> None:
    counts[key] = counts.get(key, 0) + 1


def run_monte_carlo_decision_grid(
    *,
    scenarios: Iterable[str] = SCENARIOS,
    block_counts: Iterable[int] = (8, 16),
    followup_unavailability_levels: Iterable[float] = (0.05, 0.10, 0.15),
    simulation_replicates: int = 12,
    bootstrap_replicates: int = 80,
    sessions_per_arm_block: int = 4,
    model_families: Iterable[str] = ("model_a", "model_b"),
    target_families: Iterable[str] = ("work_score", "tool_budget"),
    binary_delta: float = 0.05,
    category_margins: Mapping[str, float] | None = None,
    positive_effect_size: float = 0.30,
    availability_shift: float = 0.20,
    alpha: float = 0.05,
    false_categorical_tolerance: float = 0.075,
    master_seed: int = 20260804,
    cross_stratum_certificates: bool = True,
) -> MonteCarloGrid:
    """Estimate decision rates across a deterministic planning grid.

    The default grid covers every required estimand-level stress scenario,
    two declared block counts, and 5%/10%/15% follow-up unavailability.  The
    optional cross-stratum calculation applies the protocol's strict rule:
    responsiveness must clear in *every* fixed model×target stratum in the
    same direction; invariance must clear in every stratum.

    ``equivalence_boundary`` uses the smallest of the binary, L, and H margins
    as its true positive shift.  A categorical response/change at that exact
    strict boundary is counted as a false categorical decision.  Under
    ``null``, responsiveness and observable change are counted as false.
    Under ``availability_only``, binary responsiveness is false, while an
    observable distribution change is a true result.  These bookkeeping rates
    are diagnostics, not calibrated final error guarantees.
    """

    scenario_names = tuple(scenarios)
    block_values = tuple(block_counts)
    u_values = tuple(followup_unavailability_levels)
    models = tuple(model_families)
    targets = tuple(target_families)
    margins = dict(category_margins or {"L": 0.05, "H": 0.05, "U": 0.02})

    if not scenario_names or any(name not in SCENARIOS for name in scenario_names):
        raise ValueError(f"scenarios must be a non-empty subset of {SCENARIOS}")
    if not block_values or any(value < 2 for value in block_values):
        raise ValueError("every block count must be at least two")
    if not u_values or any(not 0.0 <= value < 1.0 for value in u_values):
        raise ValueError("follow-up unavailability levels must lie in [0, 1)")
    if simulation_replicates < 1 or bootstrap_replicates < 1:
        raise ValueError("simulation and bootstrap replicate counts must be positive")
    if sessions_per_arm_block < 1:
        raise ValueError("sessions_per_arm_block must be positive")
    if not models or not targets:
        raise ValueError("at least one model and target family are required")
    if set(margins) != set(CATEGORIES):
        raise ValueError(f"category_margins must provide exactly {CATEGORIES}")
    if not 0.0 <= false_categorical_tolerance <= 1.0:
        raise ValueError("false_categorical_tolerance must lie between 0 and 1")

    boundary_effect = min(binary_delta, margins["L"], margins["H"])
    cells: list[MonteCarloDecisionCell] = []
    for scenario in scenario_names:
        for blocks in block_values:
            for unavailability in u_values:
                binary_counts = {
                    "responsive": 0,
                    "invariant": 0,
                    "indeterminate": 0,
                }
                binary_direction_counts = {"positive": 0, "negative": 0, "none": 0}
                observable_counts = {"changed": 0, "invariant": 0, "indeterminate": 0}
                broad_invariant_count = 0
                all_strata_responsive_count = 0
                all_strata_binary_invariant_count = 0
                all_strata_observable_invariant_count = 0
                all_strata_broad_invariant_count = 0
                false_binary_count = 0
                false_observable_count = 0

                # Positive and mechanism-alias use matched random streams so
                # equal-observable cells are exactly comparable, not merely
                # asymptotically similar.
                probability_scenario = (
                    "positive" if scenario == "mechanism_alias" else scenario
                )
                for replicate in range(simulation_replicates):
                    data_seed = _derived_seed(
                        master_seed,
                        probability_scenario,
                        blocks,
                        f"{unavailability:.8f}",
                        replicate,
                        "data",
                    )
                    bootstrap_seed = _derived_seed(
                        master_seed,
                        probability_scenario,
                        blocks,
                        f"{unavailability:.8f}",
                        replicate,
                        "bootstrap",
                    )
                    effect_size = (
                        boundary_effect
                        if scenario == "equivalence_boundary"
                        else positive_effect_size
                    )
                    dataset = generate_synthetic_outcomes(
                        scenario,
                        seed=data_seed,
                        n_blocks_per_model_target=blocks,
                        sessions_per_arm_block=sessions_per_arm_block,
                        model_families=models,
                        target_families=targets,
                        effect_size=effect_size,
                        availability_shift=availability_shift,
                        base_unavailability=unavailability,
                    )
                    pooled = analyze_planning_outcomes(
                        dataset.observations,
                        binary_delta=binary_delta,
                        category_margins=margins,
                        alpha=alpha,
                        bootstrap_replicates=bootstrap_replicates,
                        seed=bootstrap_seed,
                    )
                    _increment(binary_counts, pooled.binary_decision.status)
                    _increment(
                        binary_direction_counts,
                        pooled.binary_decision.direction or "none",
                    )
                    _increment(observable_counts, pooled.observable_decision.status)
                    broad_invariant_count += (
                        pooled.broad_invariance_decision.status == "invariant"
                    )

                    if scenario == "equivalence_boundary":
                        false_binary_count += (
                            pooled.binary_decision.status != "indeterminate"
                        )
                    elif scenario in {"null", "availability_only"}:
                        false_binary_count += pooled.binary_decision.status == "responsive"
                    if scenario == "equivalence_boundary":
                        false_observable_count += (
                            pooled.observable_decision.status != "indeterminate"
                        )
                    elif scenario == "null":
                        false_observable_count += pooled.observable_decision.status == "changed"

                    if cross_stratum_certificates:
                        stratum_analyses = []
                        for model in models:
                            for target in targets:
                                rows = subset_observations(
                                    dataset.observations,
                                    model_family=model,
                                    target_family=target,
                                )
                                stratum_analyses.append(
                                    analyze_planning_outcomes(
                                        rows,
                                        binary_delta=binary_delta,
                                        category_margins=margins,
                                        alpha=alpha,
                                        bootstrap_replicates=bootstrap_replicates,
                                        seed=bootstrap_seed,
                                    )
                                )
                        directions = {
                            analysis.binary_decision.direction
                            for analysis in stratum_analyses
                        }
                        all_strata_responsive_count += (
                            all(
                                analysis.binary_decision.status == "responsive"
                                for analysis in stratum_analyses
                            )
                            and len(directions) == 1
                            and None not in directions
                        )
                        all_strata_binary_invariant_count += all(
                            analysis.binary_decision.status == "invariant"
                            for analysis in stratum_analyses
                        )
                        all_strata_observable_invariant_count += all(
                            analysis.observable_decision.status == "invariant"
                            for analysis in stratum_analyses
                        )
                        all_strata_broad_invariant_count += all(
                            analysis.broad_invariance_decision.status == "invariant"
                            for analysis in stratum_analyses
                        )

                false_binary_rate = (
                    false_binary_count / simulation_replicates
                    if scenario in {"null", "availability_only", "equivalence_boundary"}
                    else None
                )
                false_observable_rate = (
                    false_observable_count / simulation_replicates
                    if scenario in {"null", "equivalence_boundary"}
                    else None
                )
                cells.append(
                    MonteCarloDecisionCell(
                        scenario=scenario,
                        blocks_per_model_target=blocks,
                        followup_unavailability=unavailability,
                        simulation_replicates=simulation_replicates,
                        bootstrap_replicates=bootstrap_replicates,
                        sessions_per_arm_block=sessions_per_arm_block,
                        alpha=alpha,
                        binary_delta=binary_delta,
                        category_margins=margins.copy(),
                        pooled_binary_rates=_rates(binary_counts, simulation_replicates),
                        pooled_binary_direction_rates=_rates(
                            binary_direction_counts, simulation_replicates
                        ),
                        pooled_observable_rates=_rates(
                            observable_counts, simulation_replicates
                        ),
                        pooled_broad_invariance_rate=(
                            broad_invariant_count / simulation_replicates
                        ),
                        all_strata_same_direction_binary_responsive_rate=(
                            all_strata_responsive_count / simulation_replicates
                            if cross_stratum_certificates
                            else None
                        ),
                        all_strata_binary_invariant_rate=(
                            all_strata_binary_invariant_count / simulation_replicates
                            if cross_stratum_certificates
                            else None
                        ),
                        all_strata_observable_invariant_rate=(
                            all_strata_observable_invariant_count / simulation_replicates
                            if cross_stratum_certificates
                            else None
                        ),
                        all_strata_broad_invariant_rate=(
                            all_strata_broad_invariant_count / simulation_replicates
                            if cross_stratum_certificates
                            else None
                        ),
                        false_binary_categorical_rate=false_binary_rate,
                        false_observable_categorical_rate=false_observable_rate,
                        false_categorical_tolerance=false_categorical_tolerance,
                        binary_false_rate_within_tolerance=(
                            false_binary_rate <= false_categorical_tolerance
                            if false_binary_rate is not None
                            else None
                        ),
                        observable_false_rate_within_tolerance=(
                            false_observable_rate <= false_categorical_tolerance
                            if false_observable_rate is not None
                            else None
                        ),
                    )
                )

    return MonteCarloGrid(
        master_seed=master_seed,
        scenarios=scenario_names,
        block_counts=block_values,
        followup_unavailability_levels=u_values,
        simulation_replicates=simulation_replicates,
        bootstrap_replicates=bootstrap_replicates,
        cross_stratum_certificates=cross_stratum_certificates,
        cells=tuple(cells),
    )
