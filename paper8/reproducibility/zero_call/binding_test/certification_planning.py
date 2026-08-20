"""Efficient numerical certification for the final Binding Test analysis.

Unlike :mod:`highres_planning`, this module does **not** use the planning
bootstrap.  It simulates canonical block-arm nominal counts and applies the
same fixed-stratum estimator and min-df Student-t decision rules as
``binding_test.confirmatory``:

* four exact model-snapshot x target-family macro cells;
* 24 prospectively equal-weight fine strata per macro cell;
* complete four-self/four-yoke block-arm outcomes;
* a positive H-up/L-down or reverse all-four-cell conjunction;
* TOST equivalence for L/H/U in every macro cell; and
* strict boundaries at +/-.05 for H/L and +/-.02 for U equivalence.

For speed, each block arm is represented by its 15 possible multinomial (or
Dirichlet-multinomial) count triples.  The resulting discrete distribution of
block contrasts is cached.  A Monte Carlo batch then draws multinomial
frequencies of those contrast values for every fine stratum and obtains both
the sum and sum of squares analytically.  Runtime therefore scales primarily
with outer replicates and the small contrast support, rather than with the
number of blocks or sessions.

Wilson intervals quantify Monte Carlo error only.  A numerical gate is never
eligible below 20,000 outer replicates for a false-headline cell or 10,000 for
a power cell.  Latent-binary sensitivity is deliberately absent from gate
logic and can never create, rescue, or veto a result.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from functools import lru_cache
import hashlib
import json
import math
from statistics import NormalDist
import time
from typing import Iterable, Mapping

import numpy as np

from .confirmatory import (
    BOUNDARY_ABS_TOLERANCE,
    FROZEN_ALPHA,
    FROZEN_EQUIVALENCE_MARGINS,
    FROZEN_POSITIVE_THRESHOLD,
    FROZEN_TARGET_FAMILIES,
    _student_t_quantile,
    canonical_active_fine_strata,
)


CATEGORIES: tuple[str, str, str] = ("L", "H", "U")
FINE_STRATA_PER_MACRO_CELL = 24
MACRO_CELL_COUNT = 4
SESSIONS_PER_ARM_BLOCK = 4
MIN_BLOCKS_PER_FINE_STRATUM = 4
FALSE_CELL_MIN_REPLICATES = 20_000
POWER_CELL_MIN_REPLICATES = 10_000
FALSE_HEADLINE_MAX_WILSON_UPPER = 0.055
POWER_MIN_WILSON_LOWER = 0.90
SUPPORTED_UNAVAILABILITY = (0.0, 0.05, 0.10, 0.15)
SUPPORTED_BLOCK_ICC = (0.0, 0.10, 0.25)
FROZEN_CANDIDATE_BLOCKS_PER_MACRO_CELL: tuple[int, ...] = (
    24,
    48,
    72,
    96,
    120,
    144,
    168,
    192,
    288,
    384,
    576,
    768,
    1152,
    1536,
    1920,
    2304,
    3072,
)
FROZEN_CERTIFICATION_SENSITIVITY_GRID: tuple[tuple[float, float], ...] = tuple(
    (unavailability, block_icc)
    for unavailability in SUPPORTED_UNAVAILABILITY
    for block_icc in SUPPORTED_BLOCK_ICC
)

SCENARIOS: tuple[str, ...] = (
    "null",
    "positive_15",
    "negative_15",
    "positive_1055",
    "negative_1055",
    "positive_boundary",
    "negative_boundary",
    "availability_only",
    "one_model_only",
    "one_cell_only",
    "mechanism_alias",
    "fine_stratum_heterogeneity",
)

# Pair-major, counterbalance-minor fixed panel.  The six item-pair effects
# average +.05 and the four counterbalance offsets average zero, so the 24
# prospectively equal-weight effects average exactly the strict +.05 headline
# boundary.  Individual strata range from -.13 to +.23.  This deliberately
# adversarial panel is therefore a *false-headline* stress, not positive-power
# evidence, despite strong positive effects in some fine strata.
HETEROGENEOUS_PAIR_EFFECTS: tuple[float, ...] = (
    -0.10,
    -0.05,
    0.00,
    0.10,
    0.15,
    0.20,
)
HETEROGENEOUS_COUNTERBALANCE_OFFSETS: tuple[float, ...] = (
    -0.03,
    -0.01,
    0.01,
    0.03,
)
HETEROGENEOUS_FINE_STRATUM_EFFECTS: tuple[float, ...] = tuple(
    pair_effect + counterbalance_offset
    for pair_effect in HETEROGENEOUS_PAIR_EFFECTS
    for counterbalance_offset in HETEROGENEOUS_COUNTERBALANCE_OFFSETS
)

SCENARIO_ALIASES: dict[str, str] = {
    "positive": "positive_15",
    "negative": "negative_15",
    "positive_mid": "positive_1055",
    "negative_mid": "negative_1055",
    "one_macro_cell_only": "one_cell_only",
}

# Each tuple is (scenario, metric, truth role).  This is the complete positive
# confirmatory-size gate.  Other scenario assessments (notably null
# equivalence power) are reported by their individual cells but cannot enter
# this conjunction.  The mechanism alias is diagnostic and deliberately
# absent.
FROZEN_POSITIVE_SIZE_GATING_REQUIREMENTS: tuple[
    tuple[str, str, str], ...
] = (
    ("positive_15", "positive_all_cells", "power"),
    ("null", "positive_all_cells", "false_control"),
    ("positive_boundary", "positive_all_cells", "false_control"),
    ("availability_only", "positive_all_cells", "false_control"),
    ("one_cell_only", "positive_all_cells", "false_control"),
    ("one_model_only", "positive_all_cells", "false_control"),
    ("fine_stratum_heterogeneity", "positive_all_cells", "false_control"),
)
NON_GATING_DIAGNOSTIC_SCENARIOS: tuple[str, ...] = ("mechanism_alias",)
CONFIRMATORY_SIZE_IDENTIFIED = "CONFIRMATORY_SIZE_IDENTIFIED"
CONFIRMATORY_SIZE_NOT_IDENTIFIED = "CONFIRMATORY_SIZE_NOT_IDENTIFIED"
CONFIRMATORY_SIZE_INELIGIBLE = "CONFIRMATORY_SIZE_INELIGIBLE"

METHOD = (
    "vectorized Monte Carlo of cached multinomial/Dirichlet-multinomial "
    "four-session block-arm count distributions retained separately for all "
    "24 equal prospective fine strata per macro cell, including fixed "
    "heterogeneous panels; fixed-stratum block-contrast s2/n variance; "
    "minimum (blocks-per-fine-stratum - 1) Student-t degrees of freedom; "
    "all-four-cell intersection-union positive/reverse and TOST decisions; "
    "zero-standard-error components cannot establish a claim; no planning "
    "bootstrap and no exact-randomization claim"
)
RNG_METHOD = (
    "independent NumPy Generator(PCG64) streams for every macro-cell x "
    "fine-stratum, seeded by SHA-256 scientific configuration and logical "
    "stream coordinates; batch_size is excluded and affects memory only"
)
ICC_METHOD = (
    "independent Dirichlet-multinomial block-arm count sensitivity with "
    "concentration (1-rho)/rho; rho=0 uses an ordinary multinomial"
)


class _JsonRecord:
    def to_dict(self) -> dict[str, object]:
        return asdict(self)  # type: ignore[arg-type]

    def to_json(self, **kwargs: object) -> str:
        options = {**kwargs, "allow_nan": False}
        return json.dumps(self.to_dict(), **options)


def _canonical_scenario(scenario: str) -> str:
    if not isinstance(scenario, str):
        raise ValueError("scenario must be a string")
    canonical = SCENARIO_ALIASES.get(scenario, scenario)
    if canonical not in SCENARIOS:
        raise ValueError(f"scenario must be one of {SCENARIOS} or a documented alias")
    return canonical


def _canonical_supported(
    value: float, supported: tuple[float, ...], label: str
) -> float:
    for item in supported:
        if math.isclose(value, item, rel_tol=0.0, abs_tol=1e-12):
            return item
    raise ValueError(f"{label} must be one of {supported}")


@dataclass(frozen=True, slots=True)
class CertificationConfig(_JsonRecord):
    """One replayable scenario x B x U x ICC numerical-certification cell."""

    scenario: str
    blocks_per_macro_cell: int
    followup_unavailability: float
    block_icc: float
    outer_replicates: int
    master_seed: int = 20260805
    batch_size: int = 512
    model_snapshots: tuple[str, str] = ("snapshot_a", "snapshot_b")
    target_families: tuple[str, str] = FROZEN_TARGET_FAMILIES
    alpha: float = FROZEN_ALPHA
    positive_threshold: float = FROZEN_POSITIVE_THRESHOLD
    equivalence_margin_items: tuple[tuple[str, float], ...] = (
        ("L", 0.05),
        ("H", 0.05),
        ("U", 0.02),
    )
    availability_shift: float = 0.10
    monte_carlo_confidence: float = 0.95

    def __post_init__(self) -> None:
        canonical = _canonical_scenario(self.scenario)
        object.__setattr__(self, "scenario", canonical)
        if (
            isinstance(self.blocks_per_macro_cell, bool)
            or not isinstance(self.blocks_per_macro_cell, int)
        ):
            raise ValueError("blocks_per_macro_cell must be an integer")
        if self.blocks_per_macro_cell not in FROZEN_CANDIDATE_BLOCKS_PER_MACRO_CELL:
            raise ValueError(
                "blocks_per_macro_cell must be in the exact frozen candidate "
                f"sequence {FROZEN_CANDIDATE_BLOCKS_PER_MACRO_CELL}"
            )
        if self.blocks_per_fine_stratum < MIN_BLOCKS_PER_FINE_STRATUM:
            raise ValueError(
                "at least four blocks per fine stratum are required (B >= 96)"
            )
        unavailable = _canonical_supported(
            float(self.followup_unavailability),
            SUPPORTED_UNAVAILABILITY,
            "followup_unavailability",
        )
        block_icc = _canonical_supported(
            float(self.block_icc), SUPPORTED_BLOCK_ICC, "block_icc"
        )
        if (
            isinstance(self.outer_replicates, bool)
            or not isinstance(self.outer_replicates, int)
            or self.outer_replicates < 1
        ):
            raise ValueError("outer_replicates must be a positive integer")
        if (
            isinstance(self.batch_size, bool)
            or not isinstance(self.batch_size, int)
            or self.batch_size < 1
        ):
            raise ValueError("batch_size must be a positive integer")
        if isinstance(self.master_seed, bool) or not isinstance(self.master_seed, int):
            raise ValueError("master_seed must be an integer")
        if not isinstance(self.model_snapshots, tuple):
            raise ValueError("model_snapshots must be an immutable tuple")
        if len(set(self.model_snapshots)) != 2 or len(self.model_snapshots) != 2:
            raise ValueError("exactly two unique model snapshots are required")
        if not isinstance(self.target_families, tuple):
            raise ValueError("target_families must be an immutable tuple")
        if len(set(self.target_families)) != 2 or len(self.target_families) != 2:
            raise ValueError("exactly two unique target families are required")
        if self.target_families != FROZEN_TARGET_FAMILIES:
            raise ValueError(
                "target families and order are frozen to work_score_allocation, "
                "tool_budget_allocation"
            )
        if any(not isinstance(value, str) or not value.strip() for value in (*self.model_snapshots, *self.target_families)):
            raise ValueError("model snapshots and target families must be non-empty strings")
        if not math.isclose(float(self.alpha), FROZEN_ALPHA, rel_tol=0.0, abs_tol=1e-12):
            raise ValueError("certification alpha is frozen at .05")
        if not math.isclose(
            float(self.positive_threshold), FROZEN_POSITIVE_THRESHOLD,
            rel_tol=0.0, abs_tol=1e-12,
        ):
            raise ValueError("certification positive threshold is frozen at .05")
        frozen_margin_items = (("L", 0.05), ("H", 0.05), ("U", 0.02))
        if self.equivalence_margin_items != frozen_margin_items:
            raise ValueError(
                "equivalence_margin_items must be the frozen ordered immutable tuple"
            )
        margins = dict(self.equivalence_margin_items)
        if len(margins) != len(self.equivalence_margin_items) or set(margins) != set(CATEGORIES):
            raise ValueError(f"equivalence margins must provide exactly {CATEGORIES}")
        if any(not 0.0 < float(value) <= 1.0 for value in margins.values()):
            raise ValueError("equivalence margins must lie in (0, 1]")
        if any(
            not math.isclose(
                float(margins[category]), FROZEN_EQUIVALENCE_MARGINS[category],
                rel_tol=0.0, abs_tol=1e-12,
            )
            for category in CATEGORIES
        ):
            raise ValueError("certification margins are frozen at L=.05, H=.05, U=.02")
        if not math.isclose(float(self.availability_shift), 0.10, rel_tol=0.0, abs_tol=1e-12):
            raise ValueError("availability-only shift is frozen at .10")
        if not math.isclose(
            float(self.monte_carlo_confidence), 0.95, rel_tol=0.0, abs_tol=1e-12
        ):
            raise ValueError("Monte Carlo confidence is frozen at .95")
        object.__setattr__(self, "followup_unavailability", unavailable)
        object.__setattr__(self, "block_icc", block_icc)
        object.__setattr__(self, "alpha", FROZEN_ALPHA)
        object.__setattr__(self, "positive_threshold", FROZEN_POSITIVE_THRESHOLD)
        object.__setattr__(self, "availability_shift", 0.10)
        object.__setattr__(self, "monte_carlo_confidence", 0.95)

        # Validate every requested arm probability at construction time,
        # including all 24 members of any heterogeneous fixed panel.
        for macro_index in range(MACRO_CELL_COUNT):
            for fine_stratum_index in range(FINE_STRATA_PER_MACRO_CELL):
                for arm in ("self", "yoke"):
                    _scenario_probabilities(
                        self, macro_index, fine_stratum_index, arm
                    )

    @property
    def blocks_per_fine_stratum(self) -> int:
        return self.blocks_per_macro_cell // FINE_STRATA_PER_MACRO_CELL

    @property
    def equivalence_margins(self) -> dict[str, float]:
        return {category: float(value) for category, value in self.equivalence_margin_items}

    @property
    def macro_cells(self) -> tuple[str, ...]:
        return tuple(
            f"model_snapshot={model}|target_family={target}"
            for model in self.model_snapshots
            for target in self.target_families
        )


@dataclass(frozen=True, slots=True)
class WilsonRate(_JsonRecord):
    successes: int
    replicates: int
    estimate: float
    interval_lower: float
    interval_upper: float
    maximum_half_width: float
    confidence_level: float
    interval_method: str = "Wilson score interval for Monte Carlo frequency only"


@dataclass(frozen=True, slots=True)
class NumericalGateAssessment(_JsonRecord):
    claim: str
    role: str
    metric: str
    required_replicates: int
    observed_replicates: int
    replicate_eligible: bool
    criterion: str
    threshold: float
    wilson_value: float
    passed: bool | None


@dataclass(frozen=True, slots=True)
class FineStratumDistributionAudit(_JsonRecord):
    """One prospectively weighted fine-stratum generating distribution."""

    fine_stratum: str
    prospective_weight: float
    self_probabilities: tuple[float, float, float]
    yoke_probabilities: tuple[float, float, float]
    true_contrasts: tuple[float, float, float]
    contrast_support_size: int


@dataclass(frozen=True, slots=True)
class DistributionAudit(_JsonRecord):
    macro_cell: str
    probability_summary: str
    self_probabilities: tuple[float, float, float]
    yoke_probabilities: tuple[float, float, float]
    true_contrasts: tuple[float, float, float]
    latent_binary_high_contrast_bounds: tuple[float, float]
    latent_binary_sensitivity_method: str
    contrast_support_size: int
    fine_stratum_distributions: tuple[FineStratumDistributionAudit, ...]


@dataclass(frozen=True, slots=True)
class CertificationResult(_JsonRecord):
    config: CertificationConfig
    rates: dict[str, WilsonRate]
    macro_cell_rates: dict[str, dict[str, WilsonRate]]
    gate_assessments: tuple[NumericalGateAssessment, ...]
    numerical_gate_eligible: bool
    numerical_gate_passed: bool | None
    distribution_audit: tuple[DistributionAudit, ...]
    method: str = METHOD
    rng_method: str = RNG_METHOD
    icc_method: str = ICC_METHOD
    binary_sensitivity_role: str = (
        "analytical worst/best-case high-choice bounds are reported in every "
        "macro-cell distribution audit; secondary only and never a numerical gate"
    )
    binary_can_gate: bool = False
    mechanism_identified: bool = False
    claim_scope: str = (
        "only the four exact configured model-snapshot x target-family cells "
        "and their 24 prospectively equal-weight active-dose fine strata"
    )


@dataclass(frozen=True, slots=True)
class CertificationBenchmark(_JsonRecord):
    scenario: str
    blocks_per_macro_cell: int
    outer_replicates: int
    elapsed_seconds: float
    outer_replicates_per_second: float
    method: str = "wall-clock benchmark of run_certification on the current machine"


@dataclass(frozen=True, slots=True)
class PositiveSizeCertificationCell(_JsonRecord):
    """The one declared metric taken from one required sensitivity cell."""

    config: CertificationConfig
    metric: str
    role: str
    rate: WilsonRate
    required_replicates: int
    replicate_eligible: bool
    criterion: str
    threshold: float
    wilson_value: float
    passed: bool | None


@dataclass(frozen=True, slots=True)
class ConfirmatorySizeCertification(_JsonRecord):
    """Trust-root conjunction for one positive confirmatory design size.

    Exact scenario and U x ICC coverage is validated before this record can be
    constructed.  ``CONFIRMATORY_SIZE_IDENTIFIED`` is emitted only when every
    required cell has enough outer replicates and passes its declared metric.
    """

    blocks_per_macro_cell: int
    blocks_per_fine_stratum: int
    model_snapshots: tuple[str, str]
    target_families: tuple[str, str]
    frozen_candidate_blocks_per_macro_cell: tuple[int, ...]
    required_sensitivity_grid: tuple[tuple[float, float], ...]
    required_gating_scenario_metrics: tuple[tuple[str, str, str], ...]
    non_gating_diagnostic_scenarios: tuple[str, ...]
    expected_grid_cells: int
    observed_grid_cells: int
    cell_assessments: tuple[PositiveSizeCertificationCell, ...]
    numerical_gate_eligible: bool
    numerical_gate_passed: bool | None
    confirmatory_size_identified: bool
    size_status: str
    decision_scope: str = (
        "positive_15 all-four-cell power plus only the positive-headline false "
        "metric from each frozen false-control scenario across every frozen "
        "unavailability x block-ICC cell; equivalence sizing and mechanism "
        "alias diagnostics are non-gating"
    )


def _derived_seed(config: CertificationConfig) -> int:
    # Mechanism alias is observationally identical and deliberately receives
    # the identical random stream as the positive .15 scenario.
    probability_scenario = (
        "positive_15" if config.scenario == "mechanism_alias" else config.scenario
    )
    material = "|".join(
        (
            "binding-certification-v1",
            str(config.master_seed),
            probability_scenario,
            str(config.blocks_per_macro_cell),
            f"{config.followup_unavailability:.12f}",
            f"{config.block_icc:.12f}",
            repr(config.model_snapshots),
            repr(config.target_families),
        )
    )
    return int.from_bytes(hashlib.sha256(material.encode()).digest()[:16], "big")


def _derived_stream_seed(
    config: CertificationConfig,
    macro_index: int,
    fine_stratum_index: int,
) -> int:
    """Return a stable logical-stream seed independent of operational chunks."""

    material = "|".join(
        (
            "binding-certification-stream-v2",
            str(_derived_seed(config)),
            str(macro_index),
            str(fine_stratum_index),
        )
    )
    return int.from_bytes(hashlib.sha256(material.encode()).digest()[:16], "big")


def _scenario_effect(
    config: CertificationConfig,
    macro_index: int,
    fine_stratum_index: int,
) -> float:
    if not 0 <= macro_index < MACRO_CELL_COUNT:
        raise ValueError("macro_index is outside the four-cell panel")
    if not 0 <= fine_stratum_index < FINE_STRATA_PER_MACRO_CELL:
        raise ValueError("fine_stratum_index is outside the 24-stratum panel")
    scenario = config.scenario
    if scenario in {"positive_15", "mechanism_alias"}:
        return 0.15
    if scenario == "negative_15":
        return -0.15
    if scenario == "positive_1055":
        return 0.1055
    if scenario == "negative_1055":
        return -0.1055
    if scenario == "positive_boundary":
        return 0.05
    if scenario == "negative_boundary":
        return -0.05
    if scenario == "one_model_only" and macro_index < 2:
        return 0.15
    if scenario == "one_cell_only" and macro_index == 0:
        return 0.15
    if scenario == "fine_stratum_heterogeneity":
        return HETEROGENEOUS_FINE_STRATUM_EFFECTS[fine_stratum_index]
    return 0.0


def _scenario_probabilities(
    config: CertificationConfig,
    macro_index: int,
    fine_stratum_index: int,
    arm: str,
) -> tuple[float, float, float]:
    if arm not in {"self", "yoke"}:
        raise ValueError("arm must be self or yoke")
    unavailable = config.followup_unavailability
    base = (1.0 - unavailable) / 2.0
    if config.scenario == "availability_only" and arm == "self":
        self_u = unavailable + config.availability_shift
        probabilities = ((1.0 - self_u) / 2.0, (1.0 - self_u) / 2.0, self_u)
    else:
        effect = (
            _scenario_effect(config, macro_index, fine_stratum_index)
            if arm == "self"
            else 0.0
        )
        probabilities = (base - effect, base + effect, unavailable)
    if any(not math.isfinite(value) or value < 0.0 or value > 1.0 for value in probabilities):
        raise ValueError("scenario yields infeasible L/H/U probabilities")
    if not math.isclose(sum(probabilities), 1.0, abs_tol=1e-12):
        raise ValueError("scenario probabilities must sum to one")
    return probabilities


def _equal_weight_macro_probabilities(
    config: CertificationConfig,
    macro_index: int,
) -> tuple[
    tuple[float, float, float],
    tuple[float, float, float],
    tuple[float, float, float],
]:
    """Return equal-1/24 mean self, yoke, and contrast probabilities.

    This helper is the truth analogue of the final fixed-stratum estimator.
    In particular, heterogeneous strata are never collapsed to a single
    generating distribution before simulation; only their *truth summary* is
    averaged with the same prospective weights used by confirmatory inference.
    """

    self_panel = np.asarray(
        [
            _scenario_probabilities(config, macro_index, index, "self")
            for index in range(FINE_STRATA_PER_MACRO_CELL)
        ],
        dtype=np.float64,
    )
    yoke_panel = np.asarray(
        [
            _scenario_probabilities(config, macro_index, index, "yoke")
            for index in range(FINE_STRATA_PER_MACRO_CELL)
        ],
        dtype=np.float64,
    )
    self_mean = self_panel.mean(axis=0)
    yoke_mean = yoke_panel.mean(axis=0)
    contrast = self_mean - yoke_mean
    return (
        tuple(float(value) for value in self_mean),
        tuple(float(value) for value in yoke_mean),
        tuple(float(value) for value in contrast),
    )


@lru_cache(maxsize=1)
def _count_compositions() -> tuple[tuple[int, int, int], ...]:
    return tuple(
        (low, high, SESSIONS_PER_ARM_BLOCK - low - high)
        for low in range(SESSIONS_PER_ARM_BLOCK + 1)
        for high in range(SESSIONS_PER_ARM_BLOCK - low + 1)
    )


def _count_probability(
    counts: tuple[int, int, int],
    probabilities: tuple[float, float, float],
    block_icc: float,
) -> float:
    n = SESSIONS_PER_ARM_BLOCK
    log_coefficient = math.lgamma(n + 1) - sum(math.lgamma(value + 1) for value in counts)
    if block_icc == 0.0:
        log_probability = log_coefficient
        for count, probability in zip(counts, probabilities):
            if probability == 0.0:
                if count:
                    return 0.0
            elif count:
                log_probability += count * math.log(probability)
        return math.exp(log_probability)

    concentration = (1.0 - block_icc) / block_icc
    log_probability = (
        log_coefficient
        + math.lgamma(concentration)
        - math.lgamma(concentration + n)
    )
    for count, probability in zip(counts, probabilities):
        if probability == 0.0:
            if count:
                return 0.0
            continue
        alpha = probability * concentration
        log_probability += math.lgamma(alpha + count) - math.lgamma(alpha)
    return math.exp(log_probability)


@lru_cache(maxsize=256)
def _block_contrast_distribution_cached(
    self_probabilities: tuple[float, float, float],
    yoke_probabilities: tuple[float, float, float],
    block_icc: float,
) -> tuple[tuple[tuple[float, float, float], ...], tuple[float, ...]]:
    compositions = _count_compositions()
    self_mass = [
        _count_probability(counts, self_probabilities, block_icc)
        for counts in compositions
    ]
    yoke_mass = [
        _count_probability(counts, yoke_probabilities, block_icc)
        for counts in compositions
    ]
    combined: dict[tuple[int, int, int], float] = {}
    for self_counts, self_probability in zip(compositions, self_mass):
        if self_probability == 0.0:
            continue
        for yoke_counts, yoke_probability in zip(compositions, yoke_mass):
            if yoke_probability == 0.0:
                continue
            difference = tuple(
                self_value - yoke_value
                for self_value, yoke_value in zip(self_counts, yoke_counts)
            )
            combined[difference] = combined.get(difference, 0.0) + self_probability * yoke_probability
    ordered = sorted(combined)
    support = tuple(
        tuple(value / SESSIONS_PER_ARM_BLOCK for value in difference)
        for difference in ordered
    )
    masses = np.asarray([combined[difference] for difference in ordered], dtype=np.float64)
    masses /= masses.sum()
    # np.random.multinomial requires the final cumulative probability not to
    # exceed one through rounding.  Set the last mass from the remainder.
    masses[-1] = max(0.0, 1.0 - float(masses[:-1].sum()))
    masses /= masses.sum()
    return support, tuple(float(value) for value in masses)


def block_contrast_distribution(
    self_probabilities: Iterable[float],
    yoke_probabilities: Iterable[float],
    block_icc: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Return cached block-contrast support and probabilities.

    The rows of ``support`` are ``(Delta_L, Delta_H, Delta_U)`` and therefore
    sum to zero.  This public helper supports distribution and ICC audits.
    Returned arrays are copies and cannot mutate the cache.
    """

    self_p = tuple(float(value) for value in self_probabilities)
    yoke_p = tuple(float(value) for value in yoke_probabilities)
    if len(self_p) != 3 or len(yoke_p) != 3:
        raise ValueError("arm probability vectors must have three entries")
    for label, probabilities in (("self", self_p), ("yoke", yoke_p)):
        if any(not math.isfinite(value) or value < 0.0 for value in probabilities):
            raise ValueError(f"{label} probabilities must be finite and nonnegative")
        if not math.isclose(sum(probabilities), 1.0, abs_tol=1e-12):
            raise ValueError(f"{label} probabilities must sum to one")
    rho = _canonical_supported(float(block_icc), SUPPORTED_BLOCK_ICC, "block_icc")
    support, probabilities = _block_contrast_distribution_cached(self_p, yoke_p, rho)
    return np.asarray(support, dtype=np.float64).copy(), np.asarray(probabilities, dtype=np.float64).copy()


def block_contrast_moments(
    self_probabilities: Iterable[float],
    yoke_probabilities: Iterable[float],
    block_icc: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Return the mean vector and marginal variance of one block contrast."""

    support, probabilities = block_contrast_distribution(
        self_probabilities, yoke_probabilities, block_icc
    )
    center = probabilities @ support
    variance = probabilities @ ((support - center) ** 2)
    return center, variance


def _strict_above(values: np.ndarray, boundary: float) -> np.ndarray:
    return values - boundary > BOUNDARY_ABS_TOLERANCE


def _strict_below(values: np.ndarray, boundary: float) -> np.ndarray:
    return boundary - values > BOUNDARY_ABS_TOLERANCE


def _wilson(successes: int, replicates: int, confidence: float) -> WilsonRate:
    estimate = successes / replicates
    z = NormalDist().inv_cdf(0.5 + confidence / 2.0)
    z2 = z * z
    denominator = 1.0 + z2 / replicates
    center = (estimate + z2 / (2.0 * replicates)) / denominator
    radius = z * math.sqrt(
        estimate * (1.0 - estimate) / replicates
        + z2 / (4.0 * replicates * replicates)
    ) / denominator
    lower = max(0.0, center - radius)
    upper = min(1.0, center + radius)
    return WilsonRate(
        successes=int(successes),
        replicates=replicates,
        estimate=estimate,
        interval_lower=lower,
        interval_upper=upper,
        maximum_half_width=max(estimate - lower, upper - estimate),
        confidence_level=confidence,
    )


def _truth_roles(config: CertificationConfig) -> dict[str, str]:
    truths = []
    margins = np.asarray([config.equivalence_margins[category] for category in CATEGORIES])
    for macro_index in range(MACRO_CELL_COUNT):
        _self_p, _yoke_p, contrast = _equal_weight_macro_probabilities(
            config, macro_index
        )
        truths.append(contrast)
    contrasts = np.asarray(truths)
    threshold = config.positive_threshold
    positive = bool(
        np.all(_strict_above(contrasts[:, 1], threshold))
        and np.all(_strict_below(contrasts[:, 0], -threshold))
    )
    reverse = bool(
        np.all(_strict_below(contrasts[:, 1], -threshold))
        and np.all(_strict_above(contrasts[:, 0], threshold))
    )
    equivalent = bool(
        np.all(margins[None, :] - np.abs(contrasts) > BOUNDARY_ABS_TOLERANCE)
    )
    return {
        "positive_all_cells": "power" if positive else "false_control",
        "reverse_all_cells": "power" if reverse else "false_control",
        "equivalence_all_cells": "power" if equivalent else "false_control",
    }


def _relevant_gate_metrics(config: CertificationConfig) -> tuple[str, ...]:
    scenario = config.scenario
    if scenario == "null":
        return ("positive_all_cells", "reverse_all_cells", "equivalence_all_cells")
    if scenario in {"positive_15", "positive_1055", "mechanism_alias"}:
        return ("positive_all_cells",)
    if scenario in {"negative_15", "negative_1055"}:
        return ("reverse_all_cells",)
    if scenario in {"positive_boundary", "fine_stratum_heterogeneity"}:
        return ("positive_all_cells",)
    if scenario == "negative_boundary":
        return ("reverse_all_cells",)
    if scenario in {"one_model_only", "one_cell_only"}:
        return ("positive_all_cells",)
    if scenario == "availability_only":
        return ("positive_all_cells", "equivalence_all_cells")
    raise AssertionError(scenario)


def _gate_assessments(
    config: CertificationConfig,
    rates: Mapping[str, WilsonRate],
) -> tuple[NumericalGateAssessment, ...]:
    roles = _truth_roles(config)
    results = []
    for metric in _relevant_gate_metrics(config):
        role = roles[metric]
        rate = rates[metric]
        if role == "power":
            required = POWER_CELL_MIN_REPLICATES
            criterion = "Wilson 95% lower bound >= .90"
            threshold = POWER_MIN_WILSON_LOWER
            value = rate.interval_lower
            comparison = value >= threshold
        else:
            required = FALSE_CELL_MIN_REPLICATES
            criterion = "Wilson 95% upper bound <= .055"
            threshold = FALSE_HEADLINE_MAX_WILSON_UPPER
            value = rate.interval_upper
            comparison = value <= threshold
        eligible = config.outer_replicates >= required
        results.append(
            NumericalGateAssessment(
                claim=metric,
                role=role,
                metric=metric,
                required_replicates=required,
                observed_replicates=config.outer_replicates,
                replicate_eligible=eligible,
                criterion=criterion,
                threshold=threshold,
                wilson_value=value,
                passed=comparison if eligible else None,
            )
        )
    return tuple(results)


def gate_replicate_requirements(
    config: CertificationConfig,
) -> dict[str, int]:
    """Return frozen outer-replicate minima for this scenario's gate cells."""

    if not isinstance(config, CertificationConfig):
        raise TypeError("config must be a CertificationConfig")
    roles = _truth_roles(config)
    return {
        metric: (
            POWER_CELL_MIN_REPLICATES
            if roles[metric] == "power"
            else FALSE_CELL_MIN_REPLICATES
        )
        for metric in _relevant_gate_metrics(config)
    }


def run_certification(config: CertificationConfig) -> CertificationResult:
    """Run one efficient numerical-certification cell.

    Batch size controls peak memory only.  Scientific results replay exactly
    for a fixed scientific configuration and seed regardless of batch size.
    """

    if not isinstance(config, CertificationConfig):
        raise TypeError("config must be a CertificationConfig")
    rng_streams = tuple(
        tuple(
            np.random.Generator(
                np.random.PCG64(
                    _derived_stream_seed(config, macro_index, fine_stratum_index)
                )
            )
            for fine_stratum_index in range(FINE_STRATA_PER_MACRO_CELL)
        )
        for macro_index in range(MACRO_CELL_COUNT)
    )
    n_blocks = config.blocks_per_fine_stratum
    df = n_blocks - 1
    one_sided_critical = _student_t_quantile(1.0 - config.alpha, df)
    simultaneous_critical = _student_t_quantile(
        1.0 - config.alpha / (2.0 * MACRO_CELL_COUNT * len(CATEGORIES)), df
    )
    margins = np.asarray(
        [config.equivalence_margins[category] for category in CATEGORIES],
        dtype=np.float64,
    )

    distributions: list[tuple[tuple[np.ndarray, np.ndarray], ...]] = []
    true_contrasts = np.empty((MACRO_CELL_COUNT, len(CATEGORIES)), dtype=np.float64)
    audits: list[DistributionAudit] = []
    for macro_index, cell_id in enumerate(config.macro_cells):
        target_family = config.target_families[
            macro_index % len(config.target_families)
        ]
        fine_stratum_ids = canonical_active_fine_strata(target_family)
        fine_distributions: list[tuple[np.ndarray, np.ndarray]] = []
        fine_audits: list[FineStratumDistributionAudit] = []
        for fine_stratum_index, fine_stratum_id in enumerate(fine_stratum_ids):
            self_p = _scenario_probabilities(
                config, macro_index, fine_stratum_index, "self"
            )
            yoke_p = _scenario_probabilities(
                config, macro_index, fine_stratum_index, "yoke"
            )
            support, probabilities = block_contrast_distribution(
                self_p, yoke_p, config.block_icc
            )
            fine_distributions.append((support, probabilities))
            fine_true = tuple(
                float(self_value - yoke_value)
                for self_value, yoke_value in zip(self_p, yoke_p)
            )
            fine_audits.append(
                FineStratumDistributionAudit(
                    fine_stratum=fine_stratum_id,
                    prospective_weight=1.0 / FINE_STRATA_PER_MACRO_CELL,
                    self_probabilities=self_p,
                    yoke_probabilities=yoke_p,
                    true_contrasts=fine_true,
                    contrast_support_size=len(probabilities),
                )
            )
        distributions.append(tuple(fine_distributions))
        self_mean, yoke_mean, true_summary = _equal_weight_macro_probabilities(
            config, macro_index
        )
        true = np.asarray(true_summary, dtype=np.float64)
        true_contrasts[macro_index] = true
        audits.append(
            DistributionAudit(
                macro_cell=cell_id,
                probability_summary=(
                    "prospective equal-1/24 mean; generating distributions "
                    "are retained separately in fine_stratum_distributions"
                ),
                self_probabilities=self_mean,
                yoke_probabilities=yoke_mean,
                true_contrasts=tuple(float(value) for value in true),
                latent_binary_high_contrast_bounds=(
                    float(self_mean[1] - yoke_mean[1] - yoke_mean[2]),
                    float(self_mean[1] + self_mean[2] - yoke_mean[1]),
                ),
                latent_binary_sensitivity_method=(
                    "assumption-free worst/best case: observed Delta_H minus "
                    "yoke U, observed Delta_H plus self U"
                ),
                contrast_support_size=max(
                    fine.contrast_support_size for fine in fine_audits
                ),
                fine_stratum_distributions=tuple(fine_audits),
            )
        )

    overall_counts = {
        "positive_all_cells": 0,
        "reverse_all_cells": 0,
        "equivalence_all_cells": 0,
        "positive_any_cell": 0,
        "positive_exactly_one_cell": 0,
        "positive_first_model_only_pattern": 0,
        "simultaneous_coverage_all_12": 0,
    }
    macro_counts = {
        cell_id: {"positive": 0, "reverse": 0, "equivalent": 0}
        for cell_id in config.macro_cells
    }

    completed = 0
    while completed < config.outer_replicates:
        batch = min(config.batch_size, config.outer_replicates - completed)
        estimates = np.empty((batch, MACRO_CELL_COUNT, len(CATEGORIES)), dtype=np.float64)
        variances = np.empty_like(estimates)
        for macro_index, fine_distributions in enumerate(distributions):
            block_sums = np.empty(
                (batch, FINE_STRATA_PER_MACRO_CELL, len(CATEGORIES)),
                dtype=np.float64,
            )
            block_sum_squares = np.empty_like(block_sums)
            for fine_stratum_index, (support, probabilities) in enumerate(
                fine_distributions
            ):
                frequencies = rng_streams[macro_index][
                    fine_stratum_index
                ].multinomial(
                    n_blocks,
                    probabilities,
                    size=batch,
                )
                block_sums[:, fine_stratum_index, :] = frequencies @ support
                block_sum_squares[:, fine_stratum_index, :] = (
                    frequencies @ (support * support)
                )
            fine_means = block_sums / n_blocks
            centered_sums = block_sum_squares - block_sums * block_sums / n_blocks
            fine_variances = np.maximum(0.0, centered_sums / df)
            estimates[:, macro_index, :] = fine_means.mean(axis=1)
            variances[:, macro_index, :] = (
                fine_variances.sum(axis=1)
                / (FINE_STRATA_PER_MACRO_CELL**2 * n_blocks)
            )

        standard_errors = np.sqrt(np.maximum(0.0, variances))
        inference_valid = standard_errors > BOUNDARY_ABS_TOLERANCE
        lower = np.clip(estimates - one_sided_critical * standard_errors, -1.0, 1.0)
        upper = np.clip(estimates + one_sided_critical * standard_errors, -1.0, 1.0)
        positive_cells = inference_valid[:, :, 1] & inference_valid[:, :, 0] & _strict_above(lower[:, :, 1], config.positive_threshold) & _strict_below(
            upper[:, :, 0], -config.positive_threshold
        )
        reverse_cells = inference_valid[:, :, 1] & inference_valid[:, :, 0] & _strict_below(upper[:, :, 1], -config.positive_threshold) & _strict_above(
            lower[:, :, 0], config.positive_threshold
        )
        equivalent_cells = np.all(
            inference_valid
            & _strict_above(lower, -margins[None, None, :])
            & _strict_below(upper, margins[None, None, :]),
            axis=2,
        )

        positive_count = positive_cells.sum(axis=1)
        overall_counts["positive_all_cells"] += int(np.count_nonzero(positive_count == MACRO_CELL_COUNT))
        overall_counts["reverse_all_cells"] += int(np.count_nonzero(np.all(reverse_cells, axis=1)))
        overall_counts["equivalence_all_cells"] += int(np.count_nonzero(np.all(equivalent_cells, axis=1)))
        overall_counts["positive_any_cell"] += int(np.count_nonzero(positive_count > 0))
        overall_counts["positive_exactly_one_cell"] += int(np.count_nonzero(positive_count == 1))
        first_model_pattern = np.all(positive_cells[:, :2], axis=1) & ~np.any(
            positive_cells[:, 2:], axis=1
        )
        overall_counts["positive_first_model_only_pattern"] += int(np.count_nonzero(first_model_pattern))

        simultaneous_radius = simultaneous_critical * standard_errors
        simultaneous_lower = np.clip(estimates - simultaneous_radius, -1.0, 1.0)
        simultaneous_upper = np.clip(estimates + simultaneous_radius, -1.0, 1.0)
        covers = np.all(
            (simultaneous_lower <= true_contrasts[None, :, :])
            & (simultaneous_upper >= true_contrasts[None, :, :]),
            axis=(1, 2),
        )
        overall_counts["simultaneous_coverage_all_12"] += int(np.count_nonzero(covers))

        for macro_index, cell_id in enumerate(config.macro_cells):
            macro_counts[cell_id]["positive"] += int(np.count_nonzero(positive_cells[:, macro_index]))
            macro_counts[cell_id]["reverse"] += int(np.count_nonzero(reverse_cells[:, macro_index]))
            macro_counts[cell_id]["equivalent"] += int(np.count_nonzero(equivalent_cells[:, macro_index]))
        completed += batch

    rates = {
        metric: _wilson(successes, config.outer_replicates, config.monte_carlo_confidence)
        for metric, successes in overall_counts.items()
    }
    macro_rates = {
        cell_id: {
            metric: _wilson(successes, config.outer_replicates, config.monte_carlo_confidence)
            for metric, successes in counts.items()
        }
        for cell_id, counts in macro_counts.items()
    }
    assessments = _gate_assessments(config, rates)
    eligible = all(assessment.replicate_eligible for assessment in assessments)
    passed = (
        all(bool(assessment.passed) for assessment in assessments)
        if eligible
        else None
    )
    return CertificationResult(
        config=config,
        rates=rates,
        macro_cell_rates=macro_rates,
        gate_assessments=assessments,
        numerical_gate_eligible=eligible,
        numerical_gate_passed=passed,
        distribution_audit=tuple(audits),
        mechanism_identified=False,
    )


def _validated_wilson_rate(
    result: CertificationResult,
    metric: str,
) -> WilsonRate:
    """Validate the selected Monte Carlo rate rather than trusting summaries."""

    if metric not in result.rates:
        raise ValueError(
            f"certification result for {result.config.scenario!r} lacks {metric!r}"
        )
    rate = result.rates[metric]
    if not isinstance(rate, WilsonRate):
        raise TypeError("selected certification rate must be a WilsonRate")
    if type(rate.successes) is not int or type(rate.replicates) is not int:
        raise ValueError("Wilson successes and replicates must be exact integers")
    if not 0 <= rate.successes <= rate.replicates:
        raise ValueError("Wilson successes must lie between zero and replicates")
    if rate.replicates != result.config.outer_replicates:
        raise ValueError("Wilson replicates must equal config.outer_replicates")
    recomputed = _wilson(
        rate.successes,
        rate.replicates,
        result.config.monte_carlo_confidence,
    )
    if rate != recomputed:
        raise ValueError("stored Wilson interval is inconsistent with its counts")
    return rate


def _certify_confirmatory_size_from_replayed(
    results: Iterable[CertificationResult],
) -> ConfirmatorySizeCertification:
    """Conjoin an exact grid whose deterministic replay was already verified.

    Inputs must contain exactly one result for each frozen gating scenario at
    each of the four unavailability and three block-ICC values.  All results
    must use the same frozen candidate B and exact model-snapshot panel.
    Missing, duplicated, out-of-scope, or mixed-design cells are rejected.

    This trust root deliberately selects only the metric declared in
    :data:`FROZEN_POSITIVE_SIZE_GATING_REQUIREMENTS`.  For example, null-cell
    equivalence power remains separately reported and cannot veto a positive
    size that clears the null positive-false-headline control.

    This helper is deliberately private.  The public trust root below performs
    mandatory deterministic replay before it delegates to this conjunction.
    """

    frozen = tuple(results)
    if not frozen:
        raise ValueError("positive confirmatory-size certification grid is empty")
    if not all(isinstance(result, CertificationResult) for result in frozen):
        raise TypeError("all size-grid entries must be CertificationResult instances")

    requirement_by_scenario = {
        scenario: (metric, role)
        for scenario, metric, role in FROZEN_POSITIVE_SIZE_GATING_REQUIREMENTS
    }
    required_scenarios = set(requirement_by_scenario)
    seen: dict[tuple[str, float, float], CertificationResult] = {}
    for result in frozen:
        config = result.config
        if config.scenario not in required_scenarios:
            raise ValueError(
                "positive confirmatory-size grid contains an out-of-scope "
                f"scenario {config.scenario!r}"
            )
        key = (
            config.scenario,
            config.followup_unavailability,
            config.block_icc,
        )
        if key in seen:
            raise ValueError(f"duplicate positive size-grid cell {key!r}")
        seen[key] = result

    expected_keys = {
        (scenario, unavailability, block_icc)
        for scenario in required_scenarios
        for unavailability, block_icc in FROZEN_CERTIFICATION_SENSITIVITY_GRID
    }
    if set(seen) != expected_keys:
        missing = tuple(sorted(expected_keys - set(seen)))
        unexpected = tuple(sorted(set(seen) - expected_keys))
        raise ValueError(
            "positive confirmatory-size grid must have exact frozen scenario x "
            f"U x ICC coverage; missing={missing!r}, unexpected={unexpected!r}"
        )

    sizes = {result.config.blocks_per_macro_cell for result in frozen}
    if len(sizes) != 1:
        raise ValueError(f"mixed blocks_per_macro_cell values are forbidden: {sizes}")
    blocks_per_macro_cell = next(iter(sizes))
    if blocks_per_macro_cell not in FROZEN_CANDIDATE_BLOCKS_PER_MACRO_CELL:
        raise ValueError("whole-design B is outside the frozen candidate sequence")

    panels = {
        (result.config.model_snapshots, result.config.target_families)
        for result in frozen
    }
    if len(panels) != 1:
        raise ValueError("mixed model-snapshot or target-family panels are forbidden")
    model_snapshots, target_families = next(iter(panels))

    cell_assessments: list[PositiveSizeCertificationCell] = []
    for scenario, metric, expected_role in FROZEN_POSITIVE_SIZE_GATING_REQUIREMENTS:
        for unavailability, block_icc in FROZEN_CERTIFICATION_SENSITIVITY_GRID:
            result = seen[(scenario, unavailability, block_icc)]
            if result.binary_can_gate:
                raise ValueError("latent-binary sensitivity cannot enter the size gate")
            for relevant_metric in _relevant_gate_metrics(result.config):
                _validated_wilson_rate(result, relevant_metric)
            recomputed_assessments = _gate_assessments(
                result.config, result.rates
            )
            if result.gate_assessments != recomputed_assessments:
                raise ValueError("stored per-cell gate assessments are inconsistent")
            recomputed_cell_eligible = all(
                assessment.replicate_eligible
                for assessment in recomputed_assessments
            )
            recomputed_cell_passed = (
                all(bool(assessment.passed) for assessment in recomputed_assessments)
                if recomputed_cell_eligible
                else None
            )
            if (
                result.numerical_gate_eligible != recomputed_cell_eligible
                or result.numerical_gate_passed != recomputed_cell_passed
            ):
                raise ValueError("stored per-cell gate summary is inconsistent")
            actual_role = _truth_roles(result.config)[metric]
            if actual_role != expected_role:
                raise ValueError(
                    f"truth role drift for {scenario}/{metric}: expected "
                    f"{expected_role}, got {actual_role}"
                )
            rate = _validated_wilson_rate(result, metric)
            if expected_role == "power":
                required_replicates = POWER_CELL_MIN_REPLICATES
                criterion = "Wilson 95% lower bound >= .90"
                threshold = POWER_MIN_WILSON_LOWER
                wilson_value = rate.interval_lower
                comparison = wilson_value >= threshold
            else:
                required_replicates = FALSE_CELL_MIN_REPLICATES
                criterion = "Wilson 95% upper bound <= .055"
                threshold = FALSE_HEADLINE_MAX_WILSON_UPPER
                wilson_value = rate.interval_upper
                comparison = wilson_value <= threshold
            eligible = result.config.outer_replicates >= required_replicates
            cell_assessments.append(
                PositiveSizeCertificationCell(
                    config=result.config,
                    metric=metric,
                    role=expected_role,
                    rate=rate,
                    required_replicates=required_replicates,
                    replicate_eligible=eligible,
                    criterion=criterion,
                    threshold=threshold,
                    wilson_value=wilson_value,
                    passed=comparison if eligible else None,
                )
            )

    numerical_gate_eligible = all(
        assessment.replicate_eligible for assessment in cell_assessments
    )
    numerical_gate_passed = (
        all(bool(assessment.passed) for assessment in cell_assessments)
        if numerical_gate_eligible
        else None
    )
    if numerical_gate_passed is True:
        size_status = CONFIRMATORY_SIZE_IDENTIFIED
    elif numerical_gate_passed is False:
        size_status = CONFIRMATORY_SIZE_NOT_IDENTIFIED
    else:
        size_status = CONFIRMATORY_SIZE_INELIGIBLE

    return ConfirmatorySizeCertification(
        blocks_per_macro_cell=blocks_per_macro_cell,
        blocks_per_fine_stratum=(
            blocks_per_macro_cell // FINE_STRATA_PER_MACRO_CELL
        ),
        model_snapshots=model_snapshots,
        target_families=target_families,
        frozen_candidate_blocks_per_macro_cell=(
            FROZEN_CANDIDATE_BLOCKS_PER_MACRO_CELL
        ),
        required_sensitivity_grid=FROZEN_CERTIFICATION_SENSITIVITY_GRID,
        required_gating_scenario_metrics=(
            FROZEN_POSITIVE_SIZE_GATING_REQUIREMENTS
        ),
        non_gating_diagnostic_scenarios=NON_GATING_DIAGNOSTIC_SCENARIOS,
        expected_grid_cells=len(expected_keys),
        observed_grid_cells=len(frozen),
        cell_assessments=tuple(cell_assessments),
        numerical_gate_eligible=numerical_gate_eligible,
        numerical_gate_passed=numerical_gate_passed,
        confirmatory_size_identified=(numerical_gate_passed is True),
        size_status=size_status,
    )


def certify_confirmatory_size(
    results: Iterable[CertificationResult],
) -> ConfirmatorySizeCertification:
    """Replay and then conjoin the exact frozen positive-design grid.

    Internally coherent Wilson counts are not evidence that the declared seeded
    simulation produced them.  This public trust root therefore first validates
    the complete grid, then reruns every cell from its frozen configuration and
    requires full :class:`CertificationResult` equality.  The replay uses at
    most four local threads; RNG streams are independently derived per config,
    so worker scheduling cannot change scientific output.
    """

    frozen = tuple(results)
    # Cheap structural and arithmetic validation happens before the potentially
    # expensive replay.  Its decision is not returned unless replay also passes.
    certification = _certify_confirmatory_size_from_replayed(frozen)
    with ThreadPoolExecutor(max_workers=min(4, len(frozen))) as executor:
        replayed = tuple(
            executor.map(
                run_certification,
                (result.config for result in frozen),
            )
        )
    for observed, expected in zip(frozen, replayed, strict=True):
        if observed != expected:
            config = observed.config
            raise ValueError(
                "certification result differs from mandatory deterministic replay: "
                f"scenario={config.scenario!r}, "
                f"U={config.followup_unavailability}, ICC={config.block_icc}"
            )
    return certification


def run_certification_grid(
    configs: Iterable[CertificationConfig],
) -> tuple[CertificationResult, ...]:
    """Run a finite, explicitly supplied collection of certification cells."""

    frozen = tuple(configs)
    if not frozen:
        raise ValueError("at least one certification config is required")
    if not all(isinstance(config, CertificationConfig) for config in frozen):
        raise TypeError("all grid entries must be CertificationConfig instances")
    return tuple(run_certification(config) for config in frozen)


def benchmark_certification(config: CertificationConfig) -> CertificationBenchmark:
    """Wall-clock one certification cell without polluting replayable results."""

    started = time.perf_counter()
    run_certification(config)
    elapsed = time.perf_counter() - started
    return CertificationBenchmark(
        scenario=config.scenario,
        blocks_per_macro_cell=config.blocks_per_macro_cell,
        outer_replicates=config.outer_replicates,
        elapsed_seconds=elapsed,
        outer_replicates_per_second=config.outer_replicates / elapsed,
    )


__all__ = [
    "CONFIRMATORY_SIZE_IDENTIFIED",
    "CONFIRMATORY_SIZE_INELIGIBLE",
    "CONFIRMATORY_SIZE_NOT_IDENTIFIED",
    "FALSE_CELL_MIN_REPLICATES",
    "FINE_STRATA_PER_MACRO_CELL",
    "FROZEN_CANDIDATE_BLOCKS_PER_MACRO_CELL",
    "FROZEN_CERTIFICATION_SENSITIVITY_GRID",
    "FROZEN_POSITIVE_SIZE_GATING_REQUIREMENTS",
    "HETEROGENEOUS_COUNTERBALANCE_OFFSETS",
    "HETEROGENEOUS_FINE_STRATUM_EFFECTS",
    "HETEROGENEOUS_PAIR_EFFECTS",
    "MACRO_CELL_COUNT",
    "POWER_CELL_MIN_REPLICATES",
    "SCENARIOS",
    "SUPPORTED_BLOCK_ICC",
    "SUPPORTED_UNAVAILABILITY",
    "CertificationBenchmark",
    "CertificationConfig",
    "CertificationResult",
    "ConfirmatorySizeCertification",
    "FineStratumDistributionAudit",
    "NumericalGateAssessment",
    "PositiveSizeCertificationCell",
    "WilsonRate",
    "benchmark_certification",
    "block_contrast_distribution",
    "block_contrast_moments",
    "certify_confirmatory_size",
    "gate_replicate_requirements",
    "run_certification",
    "run_certification_grid",
]
