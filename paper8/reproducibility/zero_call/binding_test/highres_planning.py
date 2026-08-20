"""High-resolution planning for the redesigned identified-outcome analysis.

The primary simulated decisions concern only the observed nominal disposition
``D in {L,H,U}``: an opposing ``H``-up/``L``-down reallocation, its exact
reverse, or equivalence of the complete observed vector.  Worst/best-case
latent-binary bounds are retained as a pooled, non-blocking secondary metric.

``B`` always means active canonical blocks *per macro cell*.  The frozen panel
has four macro cells (two exact snapshots by two targets), each split equally
over 24 fine item-pair-by-presentation strata.  Consequently every candidate
``B`` is divisible by 24.  Bootstrap resampling is performed inside fine
strata, and the four-cell primary rates require every macro cell to pass.

This is zero-call planning only.  Outcome decisions use the repository's
planning bootstrap, and Wilson intervals cover finite Monte Carlo error only.
No result from this module is a formal power certification.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math
import random
from statistics import NormalDist
from typing import Iterable, Mapping, Sequence

from .estimands import (
    CATEGORIES,
    CategoryContrastResult,
    Observation,
    estimate_binary_bounds,
    estimate_category_contrasts,
)
from .redesign_estimands import (
    decide_observable_probability_vector,
    decide_observed_disposition_reallocation,
    decide_secondary_binary_sensitivity,
)


REQUIRED_SCENARIOS: tuple[str, ...] = (
    "null",
    "positive",
    "negative",
    "availability_only",
    "one_model_only",
    "mechanism_alias",
)
HIGHRES_SCENARIOS: tuple[str, ...] = REQUIRED_SCENARIOS + (
    "positive_boundary",
    "negative_boundary",
    "positive_mid",
    "negative_mid",
    "one_macro_cell_only",
)
FINE_STRATA_PER_MACRO_CELL = 24
CANONICAL_SESSIONS_PER_ARM_BLOCK = 4
CANONICAL_SESSIONS_PER_BLOCK = 8
FROZEN_CATEGORY_MARGINS = {"L": 0.05, "H": 0.05, "U": 0.02}
FROZEN_MINIMUM_REALLOCATION = 0.05
FROZEN_ALPHA = 0.05
FROZEN_SEQUENTIAL_Q_LOW_RANGE = (1, 3)
FROZEN_SEQUENTIAL_Q_HIGH_RANGE = (6, 6)
FROZEN_TOOL_PAIR_Q_CAP_ITEMS: tuple[tuple[str, int, int], ...] = (
    ("TB01", 2, 6),
    ("TB02", 2, 6),
    ("TB03", 3, 6),
    ("TB04", 1, 6),
    ("TB05", 2, 6),
    ("TB06", 2, 6),
)

POOLED_METRICS: tuple[str, ...] = (
    "observed_positive_reallocation",
    "observed_negative_reallocation",
    "observable_equivalent",
    "observable_changed",
    "primary_indeterminate",
    "secondary_binary_responsive",
    "secondary_binary_invariant",
    "secondary_binary_indeterminate",
)

ALL_MACRO_CELL_METRICS: tuple[str, ...] = (
    "observed_positive_reallocation_all_macro_cells",
    "observed_negative_reallocation_all_macro_cells",
    "observable_equivalence_all_macro_cells",
    "observable_change_all_macro_cells",
    "primary_other_or_indeterminate",
    "one_model_only_pattern",
    "one_macro_cell_only_pattern",
)
# Compatibility name for consumers that use "all strata" generically.  These
# rates specifically aggregate the four prospectively declared macro cells.
ALL_STRATA_METRICS = ALL_MACRO_CELL_METRICS

PLANNING_METHOD = (
    "seeded synthetic Monte Carlo over four macro cells and 24 equal-weight "
    "fine strata per cell; Dirichlet-multinomial block-arm ICC sensitivity; "
    "planning-grade within-fine-stratum block bootstrap; Wilson intervals "
    "quantify Monte Carlo error only"
)


@dataclass(frozen=True, slots=True)
class HighResolutionConfig:
    """Immutable configuration for a replayable redesigned planning grid."""

    scenarios: tuple[str, ...] = REQUIRED_SCENARIOS
    block_counts_per_macro_cell: tuple[int, ...] = (24, 96)
    followup_unavailability_levels: tuple[float, ...] = (0.05, 0.15)
    block_icc_levels: tuple[float, ...] = (0.0, 0.20)
    simulation_replicates: int = 3
    bootstrap_replicates: int = 16
    model_families: tuple[str, str] = ("snapshot_a", "snapshot_b")
    target_families: tuple[str, str] = (
        "work_score_allocation",
        "tool_budget_allocation",
    )
    tool_target_families: tuple[str, ...] = ("tool_budget_allocation",)
    category_margin_items: tuple[tuple[str, float], ...] = (
        ("L", 0.05),
        ("H", 0.05),
        ("U", 0.02),
    )
    minimum_observed_reallocation: float = 0.05
    positive_effect_size: float = 0.15
    mid_effect_size: float = 0.1055
    availability_shift: float = 0.10
    binary_sensitivity_delta: float = 0.05
    alpha: float = 0.05
    monte_carlo_confidence: float = 0.95
    master_seed: int = 20260805
    assumed_semantic_validity_probability: float = 0.90
    assumed_high_probability_given_valid: float = 0.10
    global_support_assurance: float = 0.95
    minimum_blocks_per_fine_stratum: int = 4
    sequential_q_low_range: tuple[int, int] = FROZEN_SEQUENTIAL_Q_LOW_RANGE
    sequential_q_high_range: tuple[int, int] = FROZEN_SEQUENTIAL_Q_HIGH_RANGE
    tool_pair_q_cap_items: tuple[tuple[str, int, int], ...] = (
        FROZEN_TOOL_PAIR_Q_CAP_ITEMS
    )

    def __post_init__(self) -> None:
        if not self.scenarios or any(value not in HIGHRES_SCENARIOS for value in self.scenarios):
            raise ValueError(f"scenarios must be a non-empty subset of {HIGHRES_SCENARIOS}")
        _require_unique("scenarios", self.scenarios)
        if not self.block_counts_per_macro_cell or any(
            value < FINE_STRATA_PER_MACRO_CELL
            or value % FINE_STRATA_PER_MACRO_CELL != 0
            for value in self.block_counts_per_macro_cell
        ):
            raise ValueError("block counts per macro cell must be positive multiples of 24")
        _require_unique("block_counts_per_macro_cell", self.block_counts_per_macro_cell)
        if not self.followup_unavailability_levels or any(
            not 0.0 <= value < 1.0 for value in self.followup_unavailability_levels
        ):
            raise ValueError("follow-up unavailability levels must lie in [0, 1)")
        _require_unique("followup_unavailability_levels", self.followup_unavailability_levels)
        if not self.block_icc_levels or any(
            not 0.0 <= value < 1.0 for value in self.block_icc_levels
        ):
            raise ValueError("block ICC levels must lie in [0, 1)")
        _require_unique("block_icc_levels", self.block_icc_levels)
        if self.simulation_replicates < 1 or self.bootstrap_replicates < 1:
            raise ValueError("simulation and bootstrap replicates must be positive")
        if len(self.model_families) != 2 or len(self.target_families) != 2:
            raise ValueError("the redesigned panel requires exactly two models and two targets")
        _require_unique("model_families", self.model_families)
        _require_unique("target_families", self.target_families)
        _require_unique("tool_target_families", self.tool_target_families)
        if not set(self.tool_target_families).issubset(self.target_families):
            raise ValueError("tool target families must be declared target families")
        margins = dict(self.category_margin_items)
        if len(margins) != len(self.category_margin_items) or set(margins) != set(CATEGORIES):
            raise ValueError(f"category margins must provide exactly {CATEGORIES}")
        if any(not 0.0 < float(value) <= 1.0 for value in margins.values()):
            raise ValueError("category margins must lie in (0, 1]")
        if margins != FROZEN_CATEGORY_MARGINS:
            raise ValueError("category margins must equal the frozen L=.05, H=.05, U=.02 values")
        for label, value in (
            ("minimum_observed_reallocation", self.minimum_observed_reallocation),
            ("positive_effect_size", self.positive_effect_size),
            ("mid_effect_size", self.mid_effect_size),
            ("availability_shift", self.availability_shift),
            ("binary_sensitivity_delta", self.binary_sensitivity_delta),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{label} must lie in [0, 1]")
        if not 0.0 < self.alpha < 1.0 or not 0.0 < self.monte_carlo_confidence < 1.0:
            raise ValueError("alpha and Monte Carlo confidence must lie in (0, 1)")
        if not math.isclose(self.alpha, FROZEN_ALPHA, rel_tol=0.0, abs_tol=1e-12):
            raise ValueError("alpha must equal the frozen .05 value")
        if not math.isclose(
            self.minimum_observed_reallocation,
            FROZEN_MINIMUM_REALLOCATION,
            rel_tol=0.0,
            abs_tol=1e-12,
        ):
            raise ValueError("minimum observed reallocation must equal the frozen .05 value")
        if not 0.0 < self.assumed_semantic_validity_probability <= 1.0:
            raise ValueError("semantic-validity probability must lie in (0, 1]")
        if not 0.0 < self.assumed_high_probability_given_valid < 1.0:
            raise ValueError("conditional high probability must lie in (0, 1)")
        if not 0.0 < self.global_support_assurance < 1.0:
            raise ValueError("global support assurance must lie in (0, 1)")
        if self.minimum_blocks_per_fine_stratum < 4:
            raise ValueError("minimum blocks per fine stratum must be at least four")
        _validate_integer_range("sequential_q_low_range", self.sequential_q_low_range)
        _validate_integer_range("sequential_q_high_range", self.sequential_q_high_range)
        if self.sequential_q_low_range != FROZEN_SEQUENTIAL_Q_LOW_RANGE:
            raise ValueError("sequential_q_low_range is frozen at (1, 3)")
        if self.sequential_q_high_range != FROZEN_SEQUENTIAL_Q_HIGH_RANGE:
            raise ValueError("sequential_q_high_range is frozen at (6, 6)")
        if self.tool_pair_q_cap_items != FROZEN_TOOL_PAIR_Q_CAP_ITEMS:
            raise ValueError("tool_pair_q_cap_items must match the frozen item bank")
        # Validate probability feasibility at the most demanding requested cell.
        for scenario in self.scenarios:
            for unavailable in self.followup_unavailability_levels:
                for model in self.model_families:
                    for target in self.target_families:
                        _scenario_probabilities(
                            scenario,
                            arm="self",
                            model=model,
                            target=target,
                            unavailable=unavailable,
                            config=self,
                        )

    @property
    def category_margins(self) -> dict[str, float]:
        return {key: float(value) for key, value in self.category_margin_items}

    @property
    def macro_cell_count(self) -> int:
        return len(self.model_families) * len(self.target_families)

    @property
    def required_fine_strata(self) -> int:
        return self.macro_cell_count * FINE_STRATA_PER_MACRO_CELL

    @property
    def per_fine_support_assurance(self) -> float:
        return 1.0 - (1.0 - self.global_support_assurance) / self.required_fine_strata

    def to_dict(self) -> dict[str, object]:
        result = asdict(self)
        result["category_margins"] = self.category_margins
        result["macro_cell_count"] = self.macro_cell_count
        result["required_fine_strata"] = self.required_fine_strata
        result["per_fine_support_assurance"] = self.per_fine_support_assurance
        return result


@dataclass(frozen=True, slots=True)
class MonteCarloRate:
    successes: int
    replicates: int
    estimate: float
    standard_error: float
    interval_lower: float
    interval_upper: float
    maximum_half_width: float
    confidence_level: float
    interval_method: str = "Wilson score interval for Monte Carlo frequency only"

    def to_dict(self) -> dict[str, int | float | str]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ResourcePlan:
    blocks_per_macro_cell: int
    macro_cell_count: int
    fine_strata_per_macro_cell: int
    required_fine_strata: int
    blocks_per_fine_stratum: int
    retained_blocks: int
    retained_sessions: int
    attempted_sessions_per_fine_stratum: int
    attempted_sessions: int
    assumed_semantic_validity_probability: float
    assumed_high_probability_given_valid: float
    global_support_assurance: float
    allocated_per_fine_support_assurance: float
    achieved_per_fine_support_lower_bound: float
    union_bound_global_support_lower_bound: float
    independence_joint_support_probability: float
    work_blocks: int
    tool_blocks: int
    baseline_attempt_requests: int
    randomized_execution_requests: int
    randomized_followup_requests: int
    sequential_q_low_range: tuple[int, int]
    sequential_q_high_range: tuple[int, int]
    tool_pair_q_cap_items: tuple[tuple[str, int, int], ...]
    tool_continuation_requests_range: tuple[int, int]
    known_generation_requests_range: tuple[int, int]
    within_fine_stratum_support_model: str = (
        "independent, stationary Bernoulli baseline-attempt validity and H/L "
        "outcomes within each fine stratum; binomial-tail planning assumption"
    )
    cross_fine_stratum_dependence_policy: str = (
        "no cross-stratum independence is assumed for the reported global "
        "lower bound; per-stratum failure bounds are combined by a union bound"
    )
    failed_execution_request_cap: int = 0
    failed_execution_followup_policy: str = (
        "terminal zero-retry failure; no follow-up request after failed execution"
    )
    complete_generation_request_cap: bool = True
    request_scope: str = (
        "active-dose randomized design only; excludes any zero-dose calibration "
        "or falsification-control sessions"
    )
    complete_provider_cost_envelope: bool = False
    dollar_cost: None = None
    cost_note: str = (
        "The active-design generation-request cap is complete under terminal "
        "zero-retry failure and exact equal-weight item-bank q caps; "
        "dollar cost remains undefined until snapshots, prices, token caps, tool fees, "
        "and provider billing semantics are frozen. Zero-dose sessions are excluded."
    )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class HighResolutionCell:
    scenario: str
    blocks_per_macro_cell: int
    blocks_per_fine_stratum: int
    followup_unavailability: float
    block_icc: float
    block_arm_cluster_size: int
    design_effect_proxy: float
    fine_strata_supported: bool
    simulation_replicates: int
    bootstrap_replicates: int
    pooled_fixed_panel_rates: dict[str, MonteCarloRate]
    all_macro_cell_rates: dict[str, MonteCarloRate]
    resource_plan: ResourcePlan
    secondary_binary_can_block_primary: bool = False
    enforcement_mechanism_identified: bool = False
    planning_inference_status: str = "planning_only/provisional"
    formal_power_claim_supported: bool = False

    @property
    def pooled_rates(self) -> dict[str, MonteCarloRate]:
        return self.pooled_fixed_panel_rates

    @property
    def all_strata_rates(self) -> dict[str, MonteCarloRate]:
        return self.all_macro_cell_rates

    def to_dict(self) -> dict[str, object]:
        result = asdict(self)
        result["pooled_rates"] = result["pooled_fixed_panel_rates"]
        result["all_strata_rates"] = result["all_macro_cell_rates"]
        return result


@dataclass(frozen=True, slots=True)
class HighResolutionGrid:
    config: HighResolutionConfig
    cells: tuple[HighResolutionCell, ...]
    method: str = PLANNING_METHOD
    planning_inference_status: str = "planning_only/provisional"
    formal_power_claim_supported: bool = False
    caveats: tuple[str, ...] = (
        "Primary decisions concern observed L/H/U dispositions, not latent binary choice.",
        "Pooled fixed-panel rates are secondary; four-cell headlines require every macro cell.",
        "Outcome intervals use a planning bootstrap, not final confirmatory inference.",
        "Monte Carlo intervals cover simulated decision frequencies only.",
        "The block ICC is a sensitivity parameter, not an empirical estimate.",
        "Attempt caps depend on declared semantic-validity and minority-choice lower bounds.",
        "Mechanism-alias and positive scenarios are observationally identical by construction.",
    )

    def to_dict(self) -> dict[str, object]:
        return {
            "config": self.config.to_dict(),
            "cells": [cell.to_dict() for cell in self.cells],
            "method": self.method,
            "planning_inference_status": self.planning_inference_status,
            "formal_power_claim_supported": self.formal_power_claim_supported,
            "caveats": self.caveats,
        }

    def to_json(self, **kwargs: object) -> str:
        return json.dumps(self.to_dict(), **kwargs)


@dataclass(frozen=True, slots=True)
class SampleSizeScreen:
    scenario: str
    followup_unavailability: float
    scope: str
    metric: str
    minimum_rate_or_lower_bound: float
    maximum_monte_carlo_half_width: float
    used_interval_lower_bound: bool
    block_icc_levels: tuple[float, ...]
    selected_blocks_per_macro_cell: int | None
    resource_plan: ResourcePlan | None
    passed: bool
    planning_only: bool = True
    rationale: str = (
        "A screen across all requested ICC sensitivities, not formal power certification."
    )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _require_unique(label: str, values: Sequence[object]) -> None:
    if len(set(values)) != len(values):
        raise ValueError(f"{label} values must be unique")


def _validate_integer_range(label: str, values: tuple[int, int]) -> None:
    if len(values) != 2 or any(
        not isinstance(value, int) or value < 0 for value in values
    ) or values[0] > values[1]:
        raise ValueError(f"{label} must be an ordered pair of nonnegative integers")


def _derived_seed(master_seed: int, *parts: object) -> int:
    material = "|".join(("binding-highres-v2", str(master_seed), *(str(p) for p in parts)))
    return int.from_bytes(hashlib.sha256(material.encode()).digest()[:16], "big")


def _logsumexp(values: Sequence[float]) -> float:
    anchor = max(values)
    return anchor + math.log(sum(math.exp(value - anchor) for value in values))


def _binomial_lower_tail(n: int, maximum_successes: int, p: float) -> float:
    if maximum_successes < 0:
        return 0.0
    if maximum_successes >= n or p == 0.0:
        return 1.0
    if p == 1.0:
        return 0.0
    logs = [
        math.lgamma(n + 1)
        - math.lgamma(k + 1)
        - math.lgamma(n - k + 1)
        + k * math.log(p)
        + (n - k) * math.log1p(-p)
        for k in range(maximum_successes + 1)
    ]
    return min(1.0, math.exp(_logsumexp(logs)))


def support_probability_lower_bound(
    attempted_sessions: int,
    blocks: int,
    p_high_given_valid: float,
    *,
    semantic_validity_probability: float = 1.0,
) -> float:
    """Union-bound probability of at least ``4B`` valid H and ``4B`` valid L."""

    if attempted_sessions < 0 or blocks < 1:
        raise ValueError("attempts must be nonnegative and blocks positive")
    if not 0.0 < p_high_given_valid < 1.0:
        raise ValueError("p_high_given_valid must lie in (0, 1)")
    if not 0.0 < semantic_validity_probability <= 1.0:
        raise ValueError("semantic validity probability must lie in (0, 1]")
    required = 4 * blocks
    if attempted_sessions < 2 * required:
        return 0.0
    p_high = semantic_validity_probability * p_high_given_valid
    p_low = semantic_validity_probability * (1.0 - p_high_given_valid)
    failure_upper = _binomial_lower_tail(attempted_sessions, required - 1, p_high)
    failure_upper += _binomial_lower_tail(attempted_sessions, required - 1, p_low)
    return max(0.0, min(1.0, 1.0 - failure_upper))


def retention_probability_for_blocks(
    attempted_sessions: int,
    blocks: int,
    p_high: float,
) -> float:
    """Backward-compatible exact-validity support probability."""

    return support_probability_lower_bound(
        attempted_sessions,
        blocks,
        p_high,
        semantic_validity_probability=1.0,
    )


def minimum_attempts_for_blocks(
    blocks: int,
    p_high: float,
    *,
    assurance: float = 0.90,
    semantic_validity_probability: float = 1.0,
) -> int:
    """Smallest raw-attempt cap whose support lower bound meets assurance."""

    if blocks < 1 or not 0.0 < p_high < 1.0 or not 0.0 < assurance < 1.0:
        raise ValueError("invalid blocks, p_high, or assurance")
    if not 0.0 < semantic_validity_probability <= 1.0:
        raise ValueError("semantic validity probability must lie in (0, 1]")
    lower = CANONICAL_SESSIONS_PER_BLOCK * blocks
    probability = lambda n: support_probability_lower_bound(
        n,
        blocks,
        p_high,
        semantic_validity_probability=semantic_validity_probability,
    )
    if probability(lower) >= assurance:
        return lower
    minority_raw_probability = semantic_validity_probability * min(p_high, 1.0 - p_high)
    upper = max(lower + 1, math.ceil(4 * blocks / minority_raw_probability))
    while probability(upper) < assurance:
        upper *= 2
    while lower + 1 < upper:
        middle = (lower + upper) // 2
        if probability(middle) >= assurance:
            upper = middle
        else:
            lower = middle
    return upper


def _resource_plan(config: HighResolutionConfig, blocks_per_macro: int) -> ResourcePlan:
    blocks_per_fine = blocks_per_macro // FINE_STRATA_PER_MACRO_CELL
    attempts_per_fine = minimum_attempts_for_blocks(
        blocks_per_fine,
        config.assumed_high_probability_given_valid,
        assurance=config.per_fine_support_assurance,
        semantic_validity_probability=config.assumed_semantic_validity_probability,
    )
    achieved_fine = support_probability_lower_bound(
        attempts_per_fine,
        blocks_per_fine,
        config.assumed_high_probability_given_valid,
        semantic_validity_probability=config.assumed_semantic_validity_probability,
    )
    retained_blocks = blocks_per_macro * config.macro_cell_count
    retained_sessions = CANONICAL_SESSIONS_PER_BLOCK * retained_blocks
    attempted_sessions = attempts_per_fine * config.required_fine_strata
    tool_blocks = (
        blocks_per_macro
        * len(config.model_families)
        * len(config.tool_target_families)
    )
    work_blocks = retained_blocks - tool_blocks
    pair_schedule_sum = sum(
        q_low + q_high for _pair_id, q_low, q_high in config.tool_pair_q_cap_items
    )
    if pair_schedule_sum % len(config.tool_pair_q_cap_items):
        raise AssertionError("equal pair weighting must yield an integral mean q cap")
    # Every canonical tool block has four low-schedule and four high-schedule
    # executions.  Equal block counts over the six pairs and four variants make
    # the item-bank average exact rather than a min/max envelope.
    exact_tool_continuations_per_block = (
        4 * pair_schedule_sum // len(config.tool_pair_q_cap_items)
    )
    exact_tool_continuations = tool_blocks * exact_tool_continuations_per_block
    exact_generation_requests = (
        attempted_sessions + 2 * retained_sessions + exact_tool_continuations
    )
    union_global = max(
        0.0,
        1.0 - config.required_fine_strata * (1.0 - achieved_fine),
    )
    return ResourcePlan(
        blocks_per_macro_cell=blocks_per_macro,
        macro_cell_count=config.macro_cell_count,
        fine_strata_per_macro_cell=FINE_STRATA_PER_MACRO_CELL,
        required_fine_strata=config.required_fine_strata,
        blocks_per_fine_stratum=blocks_per_fine,
        retained_blocks=retained_blocks,
        retained_sessions=retained_sessions,
        attempted_sessions_per_fine_stratum=attempts_per_fine,
        attempted_sessions=attempted_sessions,
        assumed_semantic_validity_probability=config.assumed_semantic_validity_probability,
        assumed_high_probability_given_valid=config.assumed_high_probability_given_valid,
        global_support_assurance=config.global_support_assurance,
        allocated_per_fine_support_assurance=config.per_fine_support_assurance,
        achieved_per_fine_support_lower_bound=achieved_fine,
        union_bound_global_support_lower_bound=union_global,
        independence_joint_support_probability=achieved_fine ** config.required_fine_strata,
        work_blocks=work_blocks,
        tool_blocks=tool_blocks,
        baseline_attempt_requests=attempted_sessions,
        randomized_execution_requests=retained_sessions,
        randomized_followup_requests=retained_sessions,
        sequential_q_low_range=config.sequential_q_low_range,
        sequential_q_high_range=config.sequential_q_high_range,
        tool_pair_q_cap_items=config.tool_pair_q_cap_items,
        tool_continuation_requests_range=(
            exact_tool_continuations,
            exact_tool_continuations,
        ),
        known_generation_requests_range=(
            exact_generation_requests,
            exact_generation_requests,
        ),
        failed_execution_request_cap=retained_sessions,
    )


def resource_plan_for_blocks(
    config: HighResolutionConfig,
    blocks_per_macro_cell: int,
) -> ResourcePlan:
    """Return the support-assured request plan for one declared candidate size."""

    if not isinstance(config, HighResolutionConfig):
        raise TypeError("config must be a HighResolutionConfig")
    if (
        not isinstance(blocks_per_macro_cell, int)
        or isinstance(blocks_per_macro_cell, bool)
        or blocks_per_macro_cell < FINE_STRATA_PER_MACRO_CELL
        or blocks_per_macro_cell % FINE_STRATA_PER_MACRO_CELL != 0
    ):
        raise ValueError("blocks per macro cell must be a positive multiple of 24")
    return _resource_plan(config, blocks_per_macro_cell)


def _scenario_effect(
    scenario: str,
    model: str,
    target: str,
    config: HighResolutionConfig,
) -> float:
    if scenario in {"positive", "mechanism_alias"}:
        return config.positive_effect_size
    if scenario == "negative":
        return -config.positive_effect_size
    if scenario == "positive_boundary":
        return config.minimum_observed_reallocation
    if scenario == "negative_boundary":
        return -config.minimum_observed_reallocation
    if scenario == "positive_mid":
        return config.mid_effect_size
    if scenario == "negative_mid":
        return -config.mid_effect_size
    if scenario == "one_model_only" and model == config.model_families[0]:
        return config.positive_effect_size
    if (
        scenario == "one_macro_cell_only"
        and model == config.model_families[0]
        and target == config.target_families[0]
    ):
        return config.positive_effect_size
    return 0.0


def _scenario_probabilities(
    scenario: str,
    *,
    arm: str,
    model: str,
    target: str,
    unavailable: float,
    config: HighResolutionConfig,
) -> tuple[float, float, float]:
    base = (1.0 - unavailable) / 2.0
    if scenario == "availability_only" and arm == "self":
        self_u = unavailable + config.availability_shift
        if self_u > 1.0:
            raise ValueError("availability shift makes P(U) exceed one")
        available = (1.0 - self_u) / 2.0
        return available, available, self_u
    effect = _scenario_effect(scenario, model, target, config) if arm == "self" else 0.0
    probabilities = (base - effect, base + effect, unavailable)
    if any(value < 0.0 or value > 1.0 for value in probabilities):
        raise ValueError("effect is infeasible at a requested U rate")
    return probabilities


def _draw_category(rng: random.Random, probabilities: tuple[float, float, float]) -> str:
    draw = rng.random()
    cumulative = 0.0
    for category, probability in zip(CATEGORIES, probabilities):
        cumulative += probability
        if draw < cumulative:
            return category
    return "U"


def _overdispersed_probabilities(
    rng: random.Random,
    probabilities: tuple[float, float, float],
    block_icc: float,
) -> tuple[float, float, float]:
    if block_icc == 0.0:
        return probabilities
    concentration = (1.0 / block_icc) - 1.0
    weights = tuple(
        rng.gammavariate(probability * concentration, 1.0) if probability else 0.0
        for probability in probabilities
    )
    total = sum(weights)
    if total <= 0.0:
        chosen = _draw_category(rng, probabilities)
        return tuple(float(category == chosen) for category in CATEGORIES)  # type: ignore[return-value]
    return tuple(value / total for value in weights)  # type: ignore[return-value]


def _generate_outcomes(
    scenario: str,
    *,
    seed: int,
    blocks_per_macro: int,
    unavailable: float,
    block_icc: float,
    config: HighResolutionConfig,
) -> tuple[Observation, ...]:
    rng = random.Random(seed)
    rows: list[Observation] = []
    blocks_per_fine = blocks_per_macro // FINE_STRATA_PER_MACRO_CELL
    for model in config.model_families:
        for target in config.target_families:
            for fine_index in range(FINE_STRATA_PER_MACRO_CELL):
                fine = f"fine-{fine_index:02d}"
                for block_index in range(blocks_per_fine):
                    block_id = f"{model}|{target}|{fine}|block-{block_index:05d}"
                    for arm in ("self", "yoke"):
                        nominal = _scenario_probabilities(
                            scenario,
                            arm=arm,
                            model=model,
                            target=target,
                            unavailable=unavailable,
                            config=config,
                        )
                        probabilities = _overdispersed_probabilities(rng, nominal, block_icc)
                        for _ in range(CANONICAL_SESSIONS_PER_ARM_BLOCK):
                            rows.append(
                                Observation(
                                    block_id=block_id,
                                    arm=arm,
                                    category=_draw_category(rng, probabilities),
                                    model_family=model,
                                    target_family=target,
                                    mechanism_signal=(
                                        arm == "self" if scenario == "mechanism_alias" else None
                                    ),
                                )
                            )
    return tuple(rows)


def _fine_stratified_rows(rows: Iterable[Observation]) -> tuple[Observation, ...]:
    """Relabel bootstrap strata to macro-cell×fine-stratum without changing data."""

    relabeled = []
    for row in rows:
        parts = row.block_id.split("|")
        if len(parts) != 4:
            raise ValueError("generated block ID does not encode its fine stratum")
        fine = parts[2]
        relabeled.append(
            Observation(
                block_id=row.block_id,
                arm=row.arm,
                category=row.category,
                model_family=f"{row.model_family}|{row.target_family}|{fine}",
                target_family="fixed_fine_panel",
                mechanism_signal=row.mechanism_signal,
            )
        )
    return tuple(relabeled)


def _primary_flags(
    result: CategoryContrastResult,
    config: HighResolutionConfig,
) -> dict[str, bool]:
    reallocation = decide_observed_disposition_reallocation(
        result,
        minimum_effect=config.minimum_observed_reallocation,
    )
    vector = decide_observable_probability_vector(
        result,
        margins=config.category_margins,
    )
    return {
        "positive": reallocation.status == "provisional_positive_reallocation",
        "negative": reallocation.status == "provisional_negative_reallocation",
        "equivalent": vector.status == "provisional_equivalent",
        "changed": vector.status == "provisional_changed",
        "indeterminate": vector.status == "provisional_indeterminate",
    }


def _increment(counts: dict[str, int], flags: Mapping[str, bool]) -> None:
    for key, value in flags.items():
        counts[key] += int(value)


def _mc_rate(successes: int, replicates: int, confidence: float) -> MonteCarloRate:
    estimate = successes / replicates
    standard_error = math.sqrt(estimate * (1.0 - estimate) / replicates)
    z = NormalDist().inv_cdf(0.5 + confidence / 2.0)
    z2 = z * z
    denominator = 1.0 + z2 / replicates
    center = (estimate + z2 / (2.0 * replicates)) / denominator
    radius = z * math.sqrt(
        estimate * (1.0 - estimate) / replicates + z2 / (4.0 * replicates**2)
    ) / denominator
    lower, upper = max(0.0, center - radius), min(1.0, center + radius)
    return MonteCarloRate(
        successes,
        replicates,
        estimate,
        standard_error,
        lower,
        upper,
        max(estimate - lower, upper - estimate),
        confidence,
    )


def run_high_resolution_grid(config: HighResolutionConfig | None = None) -> HighResolutionGrid:
    """Run scenario × B-per-macro × U × block-ICC planning cells."""

    config = config or HighResolutionConfig()
    resources = {
        blocks: _resource_plan(config, blocks)
        for blocks in config.block_counts_per_macro_cell
    }
    cells: list[HighResolutionCell] = []
    for scenario in config.scenarios:
        probability_scenario = "positive" if scenario == "mechanism_alias" else scenario
        for blocks in config.block_counts_per_macro_cell:
            blocks_per_fine = blocks // FINE_STRATA_PER_MACRO_CELL
            supported = blocks_per_fine >= config.minimum_blocks_per_fine_stratum
            for unavailable in config.followup_unavailability_levels:
                for block_icc in config.block_icc_levels:
                    pooled_counts = {key: 0 for key in POOLED_METRICS}
                    macro_counts = {key: 0 for key in ALL_MACRO_CELL_METRICS}
                    for replicate in range(config.simulation_replicates):
                        common = (
                            probability_scenario,
                            blocks,
                            f"{unavailable:.10f}",
                            f"{block_icc:.10f}",
                            replicate,
                        )
                        if not supported:
                            pooled_counts["primary_indeterminate"] += 1
                            pooled_counts["secondary_binary_indeterminate"] += 1
                            macro_counts["primary_other_or_indeterminate"] += 1
                            continue
                        rows = _generate_outcomes(
                            scenario,
                            seed=_derived_seed(config.master_seed, *common, "data"),
                            blocks_per_macro=blocks,
                            unavailable=unavailable,
                            block_icc=block_icc,
                            config=config,
                        )
                        pooled_rows = _fine_stratified_rows(rows)
                        pooled_result = estimate_category_contrasts(
                            pooled_rows,
                            alpha=config.alpha,
                            bootstrap_replicates=config.bootstrap_replicates,
                            seed=_derived_seed(config.master_seed, *common, "pooled", "category"),
                        )
                        pooled_primary = _primary_flags(pooled_result, config)
                        binary = decide_secondary_binary_sensitivity(
                            estimate_binary_bounds(
                                pooled_rows,
                                alpha=config.alpha,
                                bootstrap_replicates=config.bootstrap_replicates,
                                seed=_derived_seed(config.master_seed, *common, "pooled", "binary"),
                            ),
                            delta=config.binary_sensitivity_delta,
                        )
                        _increment(
                            pooled_counts,
                            {
                                "observed_positive_reallocation": pooled_primary["positive"],
                                "observed_negative_reallocation": pooled_primary["negative"],
                                "observable_equivalent": pooled_primary["equivalent"],
                                "observable_changed": pooled_primary["changed"],
                                "primary_indeterminate": pooled_primary["indeterminate"],
                                "secondary_binary_responsive": binary.status == "provisional_responsive",
                                "secondary_binary_invariant": binary.status == "provisional_invariant",
                                "secondary_binary_indeterminate": binary.status == "provisional_indeterminate",
                            },
                        )
                        macro_flags: dict[tuple[str, str], dict[str, bool]] = {}
                        for model in config.model_families:
                            for target in config.target_families:
                                macro_rows = _fine_stratified_rows(
                                    row
                                    for row in rows
                                    if row.model_family == model and row.target_family == target
                                )
                                result = estimate_category_contrasts(
                                    macro_rows,
                                    alpha=config.alpha,
                                    bootstrap_replicates=config.bootstrap_replicates,
                                    seed=_derived_seed(
                                        config.master_seed, *common, "macro", model, target
                                    ),
                                )
                                macro_flags[(model, target)] = _primary_flags(
                                    result,
                                    config,
                                )
                        values = tuple(macro_flags.values())
                        positive_all = all(value["positive"] for value in values)
                        negative_all = all(value["negative"] for value in values)
                        equivalent_all = all(value["equivalent"] for value in values)
                        changed_all = all(value["changed"] for value in values)
                        first_model = config.model_families[0]
                        first_target = config.target_families[0]
                        one_model_pattern = all(
                            macro_flags[(first_model, target)]["positive"]
                            for target in config.target_families
                        ) and all(
                            not flags["positive"]
                            for (model, _), flags in macro_flags.items()
                            if model != first_model
                        )
                        one_cell_pattern = macro_flags[(first_model, first_target)]["positive"] and all(
                            not flags["positive"]
                            for key, flags in macro_flags.items()
                            if key != (first_model, first_target)
                        )
                        _increment(
                            macro_counts,
                            {
                                "observed_positive_reallocation_all_macro_cells": positive_all,
                                "observed_negative_reallocation_all_macro_cells": negative_all,
                                "observable_equivalence_all_macro_cells": equivalent_all,
                                "observable_change_all_macro_cells": changed_all,
                                "primary_other_or_indeterminate": not (
                                    positive_all or negative_all or equivalent_all
                                ),
                                "one_model_only_pattern": one_model_pattern,
                                "one_macro_cell_only_pattern": one_cell_pattern,
                            },
                        )
                    cells.append(
                        HighResolutionCell(
                            scenario=scenario,
                            blocks_per_macro_cell=blocks,
                            blocks_per_fine_stratum=blocks_per_fine,
                            followup_unavailability=unavailable,
                            block_icc=block_icc,
                            block_arm_cluster_size=CANONICAL_SESSIONS_PER_ARM_BLOCK,
                            design_effect_proxy=1.0 + 3.0 * block_icc,
                            fine_strata_supported=supported,
                            simulation_replicates=config.simulation_replicates,
                            bootstrap_replicates=config.bootstrap_replicates,
                            pooled_fixed_panel_rates={
                                key: _mc_rate(
                                    pooled_counts[key],
                                    config.simulation_replicates,
                                    config.monte_carlo_confidence,
                                )
                                for key in POOLED_METRICS
                            },
                            all_macro_cell_rates={
                                key: _mc_rate(
                                    macro_counts[key],
                                    config.simulation_replicates,
                                    config.monte_carlo_confidence,
                                )
                                for key in ALL_MACRO_CELL_METRICS
                            },
                            resource_plan=resources[blocks],
                        )
                    )
    return HighResolutionGrid(config=config, cells=tuple(cells))


def screen_minimum_blocks(
    grid: HighResolutionGrid,
    *,
    scenario: str,
    followup_unavailability: float,
    metric: str,
    scope: str = "all_macro_cells",
    minimum_rate_or_lower_bound: float = 0.90,
    maximum_monte_carlo_half_width: float = 0.05,
    use_interval_lower_bound: bool = True,
    block_icc_levels: Iterable[float] | None = None,
) -> SampleSizeScreen:
    """Screen the minimum B that clears every requested ICC sensitivity cell."""

    if scope not in {"pooled", "all_macro_cells", "all_strata"}:
        raise ValueError("scope must be pooled or all_macro_cells")
    normalized_scope = "all_macro_cells" if scope == "all_strata" else scope
    metrics = POOLED_METRICS if normalized_scope == "pooled" else ALL_MACRO_CELL_METRICS
    if metric not in metrics:
        raise ValueError(f"metric must be one of {metrics}")
    if not 0.0 <= minimum_rate_or_lower_bound <= 1.0 or not 0.0 <= maximum_monte_carlo_half_width <= 1.0:
        raise ValueError("screen thresholds must lie in [0, 1]")
    requested = tuple(
        grid.config.block_icc_levels if block_icc_levels is None else block_icc_levels
    )
    if not requested or not set(requested).issubset(grid.config.block_icc_levels):
        raise ValueError("requested ICCs must be a non-empty grid subset")
    matching = [
        cell
        for cell in grid.cells
        if cell.scenario == scenario
        and cell.followup_unavailability == followup_unavailability
        and cell.block_icc in requested
    ]
    if not matching:
        raise ValueError("requested scenario/U/ICC cells are absent")
    for blocks in sorted({cell.blocks_per_macro_cell for cell in matching}):
        block_cells = [cell for cell in matching if cell.blocks_per_macro_cell == blocks]
        if {cell.block_icc for cell in block_cells} != set(requested):
            raise ValueError("grid is incomplete for requested ICC sensitivity")
        if not all(cell.fine_strata_supported for cell in block_cells):
            continue
        passed = True
        for cell in block_cells:
            rates = cell.pooled_fixed_panel_rates if normalized_scope == "pooled" else cell.all_macro_cell_rates
            rate = rates[metric]
            criterion = rate.interval_lower if use_interval_lower_bound else rate.estimate
            passed &= criterion >= minimum_rate_or_lower_bound
            passed &= rate.maximum_half_width <= maximum_monte_carlo_half_width
        if passed:
            return SampleSizeScreen(
                scenario,
                followup_unavailability,
                normalized_scope,
                metric,
                minimum_rate_or_lower_bound,
                maximum_monte_carlo_half_width,
                use_interval_lower_bound,
                requested,
                blocks,
                block_cells[0].resource_plan,
                True,
            )
    return SampleSizeScreen(
        scenario,
        followup_unavailability,
        normalized_scope,
        metric,
        minimum_rate_or_lower_bound,
        maximum_monte_carlo_half_width,
        use_interval_lower_bound,
        requested,
        None,
        None,
        False,
    )


def strong_run_configuration(*, master_seed: int = 20260805) -> HighResolutionConfig:
    """Return the frozen heavyweight screening grid, including the negative range.

    The full candidate sequence extends through 3,072 blocks per macro cell so
    the much harder observable-equivalence target is not inferred from positive
    reallocation sensitivity.  With 250 outer replicates this is still below
    the 10,000/20,000-replicate numerical-certification gate and remains a
    screening run.
    """

    return HighResolutionConfig(
        scenarios=HIGHRES_SCENARIOS,
        block_counts_per_macro_cell=(
            24, 48, 72, 96, 120, 144, 168, 192, 288, 384, 576, 768,
            1152, 1536, 1920, 2304, 3072
        ),
        followup_unavailability_levels=(0.0, 0.05, 0.10, 0.15),
        block_icc_levels=(0.0, 0.10, 0.25),
        simulation_replicates=250,
        bootstrap_replicates=500,
        master_seed=master_seed,
    )
