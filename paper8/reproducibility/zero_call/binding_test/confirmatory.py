"""Final, fixed-stratum inference for the Binding Test.

This module is intentionally separate from the planning bootstrap in
``estimands.py``.  It analyzes four prospectively declared macro cells (the
Cartesian product of two exact model snapshots and two target families) and
the complete, prospectively fixed set of fine ``pair x dose x variant``
strata required in each cell.

For each nominal outcome category ``a in {L, H, U}``, the elementary datum is
the within-block contrast

``mean(1[D=a] | self) - mean(1[D=a] | yoke)``.

Block contrasts are first averaged within fine strata.  Macro-cell estimates
then give every required fine stratum exactly equal weight, irrespective of
how many complete blocks happened to be retained in that stratum.  The
variance is the corresponding stratified independent-block (Neyman-style)
variance: the sample variance of block contrasts divided by the number of
blocks in each stratum, combined using the squared prospective weights.

Exact restricted-randomization inversion is not possible from these outcome
rows alone because they do not contain the complete allowed assignment set
and all sharp-null potential outcomes.  The confirmatory construction here is
therefore labeled honestly: fixed-stratum Student-t inference using the
minimum stratum degrees of freedom, plus Bonferroni intervals across all 12
cell-by-category contrasts.  It assumes independent canonical blocks and a
valid t approximation for their contrasts.  It never uses a bootstrap.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, fields, is_dataclass
import hashlib
import json
import math
import re
from statistics import mean
from types import MappingProxyType
from typing import Iterable, Mapping


CATEGORIES: tuple[str, str, str] = ("L", "H", "U")
ARMS: tuple[str, str] = ("self", "yoke")
EXPECTED_MACRO_CELL_COUNT = 4
ROWS_PER_BLOCK = 8
ROWS_PER_ARM_BLOCK = 4
BOUNDARY_ABS_TOLERANCE = 1e-12
FROZEN_ALPHA = 0.05
FROZEN_POSITIVE_THRESHOLD = 0.05
FROZEN_EQUIVALENCE_MARGINS: Mapping[str, float] = MappingProxyType(
    {"L": 0.05, "H": 0.05, "U": 0.02}
)
FROZEN_TARGET_FAMILIES = ("work_score_allocation", "tool_budget_allocation")
FROZEN_VARIANT_IDS = ("CB00", "CB01", "CB10", "CB11")
FROZEN_PAIR_IDS: Mapping[str, tuple[str, ...]] = MappingProxyType(
    {
        "work_score_allocation": tuple(f"WS{index:02d}" for index in range(1, 7)),
        "tool_budget_allocation": tuple(f"TB{index:02d}" for index in range(1, 7)),
    }
)
FROZEN_FINE_STRATA_PER_CELL = 24
FROZEN_MIN_BLOCKS_PER_STRATUM = 4
CONFIRMATORY_STUDY_PHASE = "confirmatory"
CALIBRATION_STUDY_PHASE = "calibration"
RECOGNIZED_STUDY_PHASES = (
    CONFIRMATORY_STUDY_PHASE,
    CALIBRATION_STUDY_PHASE,
)

INFERENCE_METHOD = (
    "conservative fixed-prospective-stratum independent-block t inference; macro cells "
    "equal-weight required fine-stratum means; variance is the weighted "
    "sum of block-contrast sample variances/n; degrees of freedom are the "
    "minimum (n_stratum - 1); not exact randomization inversion"
)
SIMULTANEOUS_METHOD = (
    "conservative two-sided Student-t intervals with Bonferroni alpha/12 across the four "
    "exact macro cells x three nominal categories; familywise coverage "
    "requires independent canonical blocks and valid fixed-stratum t bounds"
)
POSITIVE_METHOD = (
    "intersection-union conjunction of per-cell one-sided Student-t bounds: "
    "the self-minus-yoke observed-disposition H lower bound is strictly above "
    "+.05 and the L upper bound is strictly below -.05; every exact macro "
    "cell must pass"
)
REVERSE_METHOD = (
    "intersection-union conjunction of per-cell one-sided Student-t bounds: "
    "the self-minus-yoke observed-disposition H upper bound is strictly below "
    "-.05 and the L lower bound is strictly above +.05; every exact macro "
    "cell must pass"
)
EQUIVALENCE_METHOD = (
    "intersection-union TOST using per-contrast 95% one-sided Student-t "
    "bounds (equivalently 90% two-sided intervals at alpha=.05); every "
    "L/H/U contrast in every exact macro cell must lie strictly inside its "
    "predeclared margin"
)
CLAIM_LIMIT = (
    "claims apply only to the four exact model-snapshot x target-family "
    "cells and their 24 prospectively required active pair x counterbalance "
    "fine strata; they do not "
    "generalize to other snapshots, targets, strata, or latent outcomes"
)


class _JsonRecord:
    """Dataclass mixin providing strict, standard-JSON serialization."""

    def to_dict(self) -> dict[str, object]:
        result = _jsonable(self)
        if not isinstance(result, dict):
            raise TypeError("JSON record did not serialize to an object")
        return result

    def to_json(self, **kwargs: object) -> str:
        options = {**kwargs, "allow_nan": False}
        return json.dumps(self.to_dict(), **options)


class FrozenMargins(Mapping[str, float]):
    """True immutable mapping; it is not a ``dict`` subclass."""

    __slots__ = ("_items",)

    def __init__(self, values: Mapping[str, float]) -> None:
        object.__setattr__(
            self,
            "_items",
            tuple((category, float(values[category])) for category in CATEGORIES),
        )

    def __getitem__(self, key: str) -> float:
        for category, value in self._items:
            if category == key:
                return value
        raise KeyError(key)

    def __iter__(self):  # type: ignore[no-untyped-def]
        return (category for category, _value in self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __setattr__(self, _name: str, _value: object) -> None:
        raise TypeError("confirmatory equivalence margins are frozen")

    def to_dict(self) -> dict[str, float]:
        return dict(self._items)


def _jsonable(value: object) -> object:
    """Recursively convert records and immutable mappings to JSON primitives."""

    if isinstance(value, FrozenMargins):
        return value.to_dict()
    if is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: _jsonable(getattr(value, field.name))
            for field in fields(value)
        }
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return tuple(_jsonable(item) for item in value)
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise TypeError(f"unsupported JSON value {type(value).__name__}")


def _nonempty_text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


def _sha256_digest(name: str, value: object) -> str:
    text = _nonempty_text(name, value)
    if not re.fullmatch(r"[0-9a-f]{64}", text):
        raise ValueError(f"{name} must be a lowercase SHA-256 digest")
    return text


def _study_phase(value: object) -> str:
    phase = _nonempty_text("study_phase", value)
    if phase not in RECOGNIZED_STUDY_PHASES:
        raise ValueError(
            f"study_phase must be one of {RECOGNIZED_STUDY_PHASES}"
        )
    return phase


def _finite_probability(name: str, value: object, *, positive: bool) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a finite number")
    try:
        number = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a finite number") from exc
    lower_ok = number > 0.0 if positive else number >= 0.0
    if not math.isfinite(number) or not lower_ok or number > 1.0:
        relation = "in (0, 1]" if positive else "in [0, 1]"
        raise ValueError(f"{name} must be {relation}")
    return number


def _strictly_above(value: float, boundary: float) -> bool:
    return value > boundary and not math.isclose(
        value, boundary, rel_tol=0.0, abs_tol=BOUNDARY_ABS_TOLERANCE
    )


def _strictly_below(value: float, boundary: float) -> bool:
    return value < boundary and not math.isclose(
        value, boundary, rel_tol=0.0, abs_tol=BOUNDARY_ABS_TOLERANCE
    )


def canonical_active_fine_strata(target_family: str) -> tuple[str, ...]:
    """Return the frozen 6-pair x 4-counterbalance active stratum IDs."""

    if target_family not in FROZEN_PAIR_IDS:
        raise ValueError(f"target_family must be one of {FROZEN_TARGET_FAMILIES}")
    return tuple(
        f"pair_id={pair_id}|dose=active|variant_id={variant_id}"
        for pair_id in FROZEN_PAIR_IDS[target_family]
        for variant_id in FROZEN_VARIANT_IDS
    )


def canonical_block_fingerprint(
    block_id: str,
    model_snapshot: str,
    target_family: str,
    fine_stratum: str,
    assignments: Iterable[tuple[str, str, str, str, str]],
) -> str:
    """Hash the complete non-outcome assignment ledger for one block.

    Each assignment is ``(session_id, baseline_choice, arm,
    received_schedule, donor_session_id)``.  The validator independently
    recomputes this digest and separately checks the canonical 4L/4H donor
    constraints; a prose verification flag is neither accepted nor used.
    """

    _nonempty_text("block_id", block_id)
    _nonempty_text("model_snapshot", model_snapshot)
    _nonempty_text("target_family", target_family)
    _nonempty_text("fine_stratum", fine_stratum)
    frozen = tuple(sorted(tuple(value) for value in assignments))
    if len(frozen) != ROWS_PER_BLOCK or any(len(value) != 5 for value in frozen):
        raise ValueError("a canonical fingerprint requires exactly eight five-field assignments")
    payload = {
        "schema": "binding-confirmatory-canonical-block-v1",
        "block_id": block_id,
        "model_snapshot": model_snapshot,
        "target_family": target_family,
        "fine_stratum": fine_stratum,
        "assignments": frozen,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode()).hexdigest()


@dataclass(frozen=True, order=True, slots=True)
class MacroCell(_JsonRecord):
    """One exact model-snapshot by target-family confirmatory cell."""

    model_snapshot: str
    target_family: str

    def __post_init__(self) -> None:
        _nonempty_text("model_snapshot", self.model_snapshot)
        _nonempty_text("target_family", self.target_family)
        if "|" in self.model_snapshot or "|" in self.target_family:
            raise ValueError("macro-cell labels cannot contain '|'")

    @property
    def cell_id(self) -> str:
        return (
            f"model_snapshot={self.model_snapshot}|"
            f"target_family={self.target_family}"
        )


@dataclass(frozen=True, slots=True)
class CellStrataRequirement(_JsonRecord):
    """The complete fine-stratum support frozen for one macro cell."""

    cell: MacroCell
    fine_strata: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.cell, MacroCell):
            raise TypeError("cell must be a MacroCell")
        if not isinstance(self.fine_strata, tuple) or not self.fine_strata:
            raise ValueError("fine_strata must be a non-empty tuple")
        for value in self.fine_strata:
            _nonempty_text("fine_stratum", value)
        if len(set(self.fine_strata)) != len(self.fine_strata):
            raise ValueError("fine_strata must be unique within a macro cell")
        expected = canonical_active_fine_strata(self.cell.target_family)
        if self.fine_strata != expected:
            raise ValueError(
                "fine_strata must be the canonical ordered 24 active "
                "pair x counterbalance strata for the target family"
            )


@dataclass(frozen=True, slots=True)
class ConfirmatoryDesign(_JsonRecord):
    """Prospectively fixed cells, fine strata, margins, and test thresholds."""

    study_phase: str
    protocol_run_id: str
    protocol_manifest_digest: str
    requirements: tuple[CellStrataRequirement, ...]
    equivalence_margins: Mapping[str, float]
    alpha: float = 0.05
    positive_threshold: float = FROZEN_POSITIVE_THRESHOLD
    min_blocks_per_stratum: int = FROZEN_MIN_BLOCKS_PER_STRATUM

    def __post_init__(self) -> None:
        _study_phase(self.study_phase)
        _nonempty_text("protocol_run_id", self.protocol_run_id)
        _sha256_digest(
            "protocol_manifest_digest", self.protocol_manifest_digest
        )
        if not isinstance(self.requirements, tuple):
            raise ValueError("requirements must be a tuple fixed before analysis")
        if len(self.requirements) != EXPECTED_MACRO_CELL_COUNT:
            raise ValueError("the confirmatory design must declare exactly four macro cells")
        if not all(isinstance(value, CellStrataRequirement) for value in self.requirements):
            raise TypeError("every requirement must be a CellStrataRequirement")

        cells = tuple(requirement.cell for requirement in self.requirements)
        if len(set(cells)) != len(cells):
            raise ValueError("macro cells must be unique")
        models = {cell.model_snapshot for cell in cells}
        targets = {cell.target_family for cell in cells}
        cartesian = {MacroCell(model, target) for model in models for target in targets}
        if len(models) != 2 or len(targets) != 2 or set(cells) != cartesian:
            raise ValueError(
                "the four macro cells must be the complete Cartesian product "
                "of exactly two model snapshots and two target families"
            )
        if targets != set(FROZEN_TARGET_FAMILIES):
            raise ValueError(
                "target families are frozen to work_score_allocation and "
                "tool_budget_allocation"
            )

        alpha = _finite_probability("alpha", self.alpha, positive=True)
        threshold = _finite_probability(
            "positive_threshold", self.positive_threshold, positive=True
        )
        if not math.isclose(alpha, FROZEN_ALPHA, rel_tol=0.0, abs_tol=1e-12):
            raise ValueError("confirmatory alpha is frozen at .05")
        if not math.isclose(
            threshold, FROZEN_POSITIVE_THRESHOLD, rel_tol=0.0, abs_tol=1e-12
        ):
            raise ValueError("confirmatory positive threshold is frozen at .05")
        if self.min_blocks_per_stratum != FROZEN_MIN_BLOCKS_PER_STRATUM:
            raise ValueError("minimum blocks per fine stratum is frozen at four")
        if set(self.equivalence_margins) != set(CATEGORIES):
            raise ValueError(f"equivalence_margins must provide exactly {CATEGORIES}")
        margins = {
            category: _finite_probability(
                f"equivalence_margins[{category}]",
                self.equivalence_margins[category],
                positive=True,
            )
            for category in CATEGORIES
        }
        if any(
            not math.isclose(
                margins[category], FROZEN_EQUIVALENCE_MARGINS[category],
                rel_tol=0.0, abs_tol=1e-12,
            )
            for category in CATEGORIES
        ):
            raise ValueError("confirmatory margins are frozen at L=.05, H=.05, U=.02")
        object.__setattr__(self, "equivalence_margins", FrozenMargins(margins))
        object.__setattr__(self, "alpha", FROZEN_ALPHA)
        object.__setattr__(self, "positive_threshold", FROZEN_POSITIVE_THRESHOLD)

    @property
    def cells(self) -> tuple[MacroCell, ...]:
        return tuple(requirement.cell for requirement in self.requirements)

    def fine_strata_for(self, cell: MacroCell) -> tuple[str, ...]:
        for requirement in self.requirements:
            if requirement.cell == cell:
                return requirement.fine_strata
        raise KeyError(cell.cell_id)


@dataclass(frozen=True, slots=True)
class ConfirmatoryObservation(_JsonRecord):
    """One observed nominal follow-up row from a canonical block."""

    study_phase: str
    protocol_run_id: str
    protocol_manifest_digest: str
    block_id: str
    session_id: str
    fine_stratum: str
    model_snapshot: str
    target_family: str
    arm: str
    category: str
    baseline_choice: str
    received_schedule: str
    donor_session_id: str
    canonical_block_fingerprint: str

    def __post_init__(self) -> None:
        _study_phase(self.study_phase)
        _nonempty_text("protocol_run_id", self.protocol_run_id)
        _sha256_digest(
            "protocol_manifest_digest", self.protocol_manifest_digest
        )
        _nonempty_text("block_id", self.block_id)
        _nonempty_text("session_id", self.session_id)
        _nonempty_text("fine_stratum", self.fine_stratum)
        _nonempty_text("model_snapshot", self.model_snapshot)
        _nonempty_text("target_family", self.target_family)
        _nonempty_text("donor_session_id", self.donor_session_id)
        if self.arm not in ARMS:
            raise ValueError(f"arm must be one of {ARMS}")
        if self.category not in CATEGORIES:
            raise ValueError(f"category must be one of {CATEGORIES}")
        if self.baseline_choice not in {"L", "H"}:
            raise ValueError("baseline_choice must be L or H")
        if self.received_schedule not in {"L", "H"}:
            raise ValueError("received_schedule must be L or H")
        _sha256_digest(
            "canonical_block_fingerprint", self.canonical_block_fingerprint
        )

    @classmethod
    def from_mapping(
        cls, record: Mapping[str, object]
    ) -> ConfirmatoryObservation:
        """Load one confirmatory row from an exact, closed mapping schema.

        Calibration rows are rejected at ingestion even though the record type
        recognizes that phase so the analyzer can also enforce the firewall on
        directly constructed observations.
        """

        if not isinstance(record, Mapping):
            raise TypeError("confirmatory observation record must be a mapping")
        field_names = tuple(field.name for field in fields(cls))
        expected = set(field_names)
        supplied = set(record)
        missing = sorted(expected - supplied)
        extra = sorted(supplied - expected, key=str)
        if missing or extra:
            raise ValueError(
                "confirmatory observation fields must match exactly; "
                f"missing={missing}, extra={extra}"
            )
        if record["study_phase"] == CALIBRATION_STUDY_PHASE:
            raise ValueError(
                "calibration records cannot be loaded as confirmatory observations"
            )
        values = {name: record[name] for name in field_names}
        return cls(**values)  # type: ignore[arg-type]

    @property
    def macro_cell(self) -> MacroCell:
        return MacroCell(self.model_snapshot, self.target_family)


@dataclass(frozen=True, slots=True)
class Interval(_JsonRecord):
    estimate: float
    lower: float
    upper: float
    confidence_level: float
    coverage_scope: str = "pointwise"
    familywise_confidence_level: float | None = None
    family_size: int = 1


@dataclass(frozen=True, slots=True)
class BlockCategoryContrast(_JsonRecord):
    """Auditable L/H/U contrasts from one complete 4-self/4-yoke block."""

    block_id: str
    cell: MacroCell
    fine_stratum: str
    canonical_block_fingerprint: str
    contrasts: dict[str, float]
    n_self: int = ROWS_PER_ARM_BLOCK
    n_yoke: int = ROWS_PER_ARM_BLOCK


@dataclass(frozen=True, slots=True)
class FineStratumEstimate(_JsonRecord):
    fine_stratum: str
    n_blocks: int
    contrasts: dict[str, float]
    block_variances: dict[str, float]
    mean_variances: dict[str, float]


@dataclass(frozen=True, slots=True)
class CategoryInference(_JsonRecord):
    category: str
    estimate: float
    variance: float
    standard_error: float
    degrees_of_freedom: int
    one_sided_lower: float
    one_sided_upper: float
    one_sided_confidence_level: float
    equivalence_interval: Interval
    equivalence_margin: float
    equivalence_status: str
    marginal_two_sided_interval: Interval
    simultaneous_interval: Interval
    inference_valid: bool
    guard_reason: str | None


@dataclass(frozen=True, slots=True)
class CellInference(_JsonRecord):
    cell: MacroCell
    claim_scope: str
    required_fine_strata: tuple[str, ...]
    blocks_by_fine_stratum: dict[str, int]
    equal_fine_stratum_weight: float
    fine_strata: tuple[FineStratumEstimate, ...]
    categories: dict[str, CategoryInference]
    positive_status: str
    reverse_status: str
    equivalence_status: str


@dataclass(frozen=True, slots=True)
class HeadlineDecision(_JsonRecord):
    status: str
    claim: str
    required_cells: tuple[str, ...]
    passing_cells: tuple[str, ...]
    nonpassing_cells: tuple[str, ...]
    method: str
    boundary_policy: str


@dataclass(frozen=True, slots=True)
class PooledCategoryEstimate(_JsonRecord):
    """Equal-cell pooled estimate, explicitly secondary and non-headline."""

    category: str
    estimate: float
    variance: float
    standard_error: float


@dataclass(frozen=True, slots=True)
class PooledSecondaryResult(_JsonRecord):
    role: str
    weighting: str
    categories: dict[str, PooledCategoryEstimate]


@dataclass(frozen=True, slots=True)
class ConfirmatoryAnalysis(_JsonRecord):
    design: ConfirmatoryDesign
    block_contrasts: tuple[BlockCategoryContrast, ...]
    cells: dict[str, CellInference]
    positive_headline: HeadlineDecision
    reverse_headline: HeadlineDecision
    equivalence_headline: HeadlineDecision
    pooled_secondary: PooledSecondaryResult
    inference_method: str
    simultaneous_method: str
    assumptions: tuple[str, ...]
    claim_limit: str = CLAIM_LIMIT


def _sample_variance(values: list[float]) -> float:
    if len(values) < 2:
        raise ValueError("at least two block contrasts are required for variance")
    center = mean(values)
    return sum((value - center) ** 2 for value in values) / (len(values) - 1)


def _beta_continued_fraction(a: float, b: float, x: float) -> float:
    """Continued fraction used by the regularized incomplete beta."""

    max_iterations = 300
    epsilon = 3e-14
    floor = 1e-300
    qab = a + b
    qap = a + 1.0
    qam = a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < floor:
        d = floor
    d = 1.0 / d
    result = d
    for iteration in range(1, max_iterations + 1):
        twice = 2 * iteration
        aa = iteration * (b - iteration) * x / (
            (qam + twice) * (a + twice)
        )
        d = 1.0 + aa * d
        if abs(d) < floor:
            d = floor
        c = 1.0 + aa / c
        if abs(c) < floor:
            c = floor
        d = 1.0 / d
        result *= d * c

        aa = -(a + iteration) * (qab + iteration) * x / (
            (a + twice) * (qap + twice)
        )
        d = 1.0 + aa * d
        if abs(d) < floor:
            d = floor
        c = 1.0 + aa / c
        if abs(c) < floor:
            c = floor
        d = 1.0 / d
        delta = d * c
        result *= delta
        if abs(delta - 1.0) <= epsilon:
            return result
    raise ArithmeticError("incomplete-beta continued fraction did not converge")


def _regularized_beta(x: float, a: float, b: float) -> float:
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    front = math.exp(
        math.lgamma(a + b)
        - math.lgamma(a)
        - math.lgamma(b)
        + a * math.log(x)
        + b * math.log1p(-x)
    )
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _beta_continued_fraction(a, b, x) / a
    return 1.0 - front * _beta_continued_fraction(b, a, 1.0 - x) / b


def _student_t_cdf(value: float, degrees_of_freedom: int) -> float:
    if degrees_of_freedom < 1:
        raise ValueError("degrees_of_freedom must be positive")
    if value == 0.0:
        return 0.5
    x = degrees_of_freedom / (degrees_of_freedom + value * value)
    tail_twice = _regularized_beta(x, degrees_of_freedom / 2.0, 0.5)
    if value > 0.0:
        return 1.0 - 0.5 * tail_twice
    return 0.5 * tail_twice


def _student_t_quantile(probability: float, degrees_of_freedom: int) -> float:
    """Numerically invert Student's t CDF without an optional dependency."""

    if not 0.5 < probability < 1.0:
        raise ValueError("only upper-half probabilities are supported")
    lower = 0.0
    upper = 1.0
    while _student_t_cdf(upper, degrees_of_freedom) < probability:
        upper *= 2.0
        if upper > 1e12:
            raise ArithmeticError("could not bracket Student-t quantile")
    for _ in range(100):
        midpoint = (lower + upper) / 2.0
        if _student_t_cdf(midpoint, degrees_of_freedom) < probability:
            lower = midpoint
        else:
            upper = midpoint
    return (lower + upper) / 2.0


def _bounded(value: float) -> float:
    """Intersect an interval endpoint with the known contrast space [-1, 1]."""

    return min(1.0, max(-1.0, value))


def _interval(
    estimate: float,
    standard_error: float,
    critical: float,
    confidence_level: float,
    *,
    coverage_scope: str = "pointwise",
    familywise_confidence_level: float | None = None,
    family_size: int = 1,
) -> Interval:
    return Interval(
        estimate=estimate,
        lower=_bounded(estimate - critical * standard_error),
        upper=_bounded(estimate + critical * standard_error),
        confidence_level=confidence_level,
        coverage_scope=coverage_scope,
        familywise_confidence_level=familywise_confidence_level,
        family_size=family_size,
    )


def _validate_and_contrast_blocks(
    observations: Iterable[ConfirmatoryObservation],
    design: ConfirmatoryDesign,
) -> tuple[
    tuple[BlockCategoryContrast, ...],
    dict[MacroCell, dict[str, list[BlockCategoryContrast]]],
]:
    rows = tuple(observations)
    if not rows:
        raise ValueError("at least one confirmatory observation is required")
    if not all(isinstance(row, ConfirmatoryObservation) for row in rows):
        raise TypeError("all rows must be ConfirmatoryObservation instances")
    session_ids = [row.session_id for row in rows]
    if len(set(session_ids)) != len(session_ids):
        raise ValueError("session_id values must be globally unique")

    by_block: dict[str, list[ConfirmatoryObservation]] = {}
    for row in rows:
        by_block.setdefault(row.block_id, []).append(row)

    expected_cells = set(design.cells)
    grouped: dict[MacroCell, dict[str, list[BlockCategoryContrast]]] = {
        cell: {fine: [] for fine in design.fine_strata_for(cell)}
        for cell in design.cells
    }
    block_results: list[BlockCategoryContrast] = []

    for block_id in sorted(by_block):
        block_rows = by_block[block_id]
        if len(block_rows) != ROWS_PER_BLOCK:
            raise ValueError(
                f"block {block_id!r} must contain exactly {ROWS_PER_BLOCK} rows"
            )
        cells = {row.macro_cell for row in block_rows}
        strata = {row.fine_stratum for row in block_rows}
        if len(cells) != 1 or len(strata) != 1:
            raise ValueError(
                f"block {block_id!r} cannot cross a macro cell or fine stratum"
            )
        cell = next(iter(cells))
        fine_stratum = next(iter(strata))
        if cell not in expected_cells:
            raise ValueError(f"block {block_id!r} belongs to an undeclared macro cell")
        required = set(design.fine_strata_for(cell))
        if fine_stratum not in required:
            raise ValueError(
                f"block {block_id!r} belongs to undeclared fine stratum "
                f"{fine_stratum!r} in {cell.cell_id}"
            )
        arm_counts = {
            arm: sum(row.arm == arm for row in block_rows) for arm in ARMS
        }
        if any(arm_counts[arm] != ROWS_PER_ARM_BLOCK for arm in ARMS):
            raise ValueError(
                f"block {block_id!r} must contain exactly four self and four yoke rows"
            )
        baseline_counts = {
            choice: sum(row.baseline_choice == choice for row in block_rows)
            for choice in ("L", "H")
        }
        if baseline_counts != {"L": 4, "H": 4}:
            raise ValueError(
                f"block {block_id!r} must have canonical 4L/4H baseline support"
            )
        self_rows = [row for row in block_rows if row.arm == "self"]
        yoke_rows = [row for row in block_rows if row.arm == "yoke"]
        self_baselines = {
            choice: sum(row.baseline_choice == choice for row in self_rows)
            for choice in ("L", "H")
        }
        if self_baselines != {"L": 2, "H": 2}:
            raise ValueError(
                f"block {block_id!r} self arm must contain exactly 2L/2H baselines"
            )
        if any(
            row.received_schedule != row.baseline_choice
            or row.donor_session_id != row.session_id
            for row in self_rows
        ):
            raise ValueError(
                f"block {block_id!r} self rows must receive their own baseline schedules"
            )
        donors = {row.session_id: row for row in self_rows}
        if {row.donor_session_id for row in yoke_rows} != set(donors):
            raise ValueError(
                f"block {block_id!r} yoke rows must use every self donor exactly once"
            )
        if len({row.donor_session_id for row in yoke_rows}) != len(yoke_rows):
            raise ValueError(f"block {block_id!r} repeats a yoke donor")
        if any(
            row.received_schedule != donors[row.donor_session_id].baseline_choice
            for row in yoke_rows
        ):
            raise ValueError(
                f"block {block_id!r} yoke received schedules must match donor baselines"
            )
        yoke_exposure_table = Counter(
            (row.baseline_choice, row.received_schedule) for row in yoke_rows
        )
        expected_exposure_table = Counter(
            {("L", "L"): 1, ("L", "H"): 1, ("H", "L"): 1, ("H", "H"): 1}
        )
        if yoke_exposure_table != expected_exposure_table:
            raise ValueError(
                f"block {block_id!r} yoke baseline x received-schedule table "
                "must contain one observation in each L/H cell"
            )
        assignments = tuple(
            (
                row.session_id,
                row.baseline_choice,
                row.arm,
                row.received_schedule,
                row.donor_session_id,
            )
            for row in block_rows
        )
        expected_fingerprint = canonical_block_fingerprint(
            block_id,
            cell.model_snapshot,
            cell.target_family,
            fine_stratum,
            assignments,
        )
        supplied_fingerprints = {
            row.canonical_block_fingerprint for row in block_rows
        }
        if supplied_fingerprints != {expected_fingerprint}:
            raise ValueError(
                f"block {block_id!r} canonical assignment fingerprint mismatch"
            )

        contrasts: dict[str, float] = {}
        for category in CATEGORIES:
            arm_means = {
                arm: sum(
                    row.category == category
                    for row in block_rows
                    if row.arm == arm
                )
                / ROWS_PER_ARM_BLOCK
                for arm in ARMS
            }
            contrasts[category] = arm_means["self"] - arm_means["yoke"]
        if not math.isclose(sum(contrasts.values()), 0.0, abs_tol=1e-12):
            raise AssertionError("nominal block contrasts must sum to zero")
        result = BlockCategoryContrast(
            block_id=block_id,
            cell=cell,
            fine_stratum=fine_stratum,
            canonical_block_fingerprint=expected_fingerprint,
            contrasts=contrasts,
        )
        block_results.append(result)
        grouped[cell][fine_stratum].append(result)

    for cell in design.cells:
        required = set(design.fine_strata_for(cell))
        observed = {
            fine for fine, blocks in grouped[cell].items() if blocks
        }
        if observed != required:
            missing = sorted(required - observed)
            raise ValueError(
                f"fixed fine-stratum coverage is incomplete in {cell.cell_id}; "
                f"missing={missing}"
            )
        for fine_stratum, blocks in grouped[cell].items():
            if len(blocks) < design.min_blocks_per_stratum:
                raise ValueError(
                    f"{cell.cell_id}/{fine_stratum} has {len(blocks)} blocks; "
                    f"at least {design.min_blocks_per_stratum} are required"
                )

    return tuple(block_results), grouped


def _enforce_confirmatory_firewall(
    observations: Iterable[ConfirmatoryObservation],
    design: ConfirmatoryDesign,
) -> tuple[ConfirmatoryObservation, ...]:
    """Reject cross-phase or cross-protocol data before block inspection."""

    rows = tuple(observations)
    if design.study_phase != CONFIRMATORY_STUDY_PHASE:
        raise ValueError(
            "calibration phase is forbidden in confirmatory analysis"
        )
    if not all(isinstance(row, ConfirmatoryObservation) for row in rows):
        raise TypeError("all rows must be ConfirmatoryObservation instances")
    for row in rows:
        if row.study_phase != CONFIRMATORY_STUDY_PHASE:
            raise ValueError(
                "calibration phase is forbidden in confirmatory analysis"
            )
        if row.protocol_run_id != design.protocol_run_id:
            raise ValueError(
                "confirmatory observation protocol_run_id mismatch"
            )
        if row.protocol_manifest_digest != design.protocol_manifest_digest:
            raise ValueError(
                "confirmatory observation protocol_manifest_digest mismatch"
            )
    return rows


def _cell_inference(
    cell: MacroCell,
    grouped: dict[str, list[BlockCategoryContrast]],
    design: ConfirmatoryDesign,
    simultaneous_contrasts: int,
) -> CellInference:
    required = design.fine_strata_for(cell)
    stratum_results: list[FineStratumEstimate] = []
    for fine_stratum in required:
        blocks = grouped[fine_stratum]
        contrasts = {
            category: mean(block.contrasts[category] for block in blocks)
            for category in CATEGORIES
        }
        block_variances = {
            category: _sample_variance(
                [block.contrasts[category] for block in blocks]
            )
            for category in CATEGORIES
        }
        mean_variances = {
            category: block_variances[category] / len(blocks)
            for category in CATEGORIES
        }
        stratum_results.append(
            FineStratumEstimate(
                fine_stratum=fine_stratum,
                n_blocks=len(blocks),
                contrasts=contrasts,
                block_variances=block_variances,
                mean_variances=mean_variances,
            )
        )

    weight = 1.0 / len(stratum_results)
    degrees_of_freedom = min(result.n_blocks - 1 for result in stratum_results)
    one_sided_critical = _student_t_quantile(
        1.0 - design.alpha, degrees_of_freedom
    )
    marginal_critical = _student_t_quantile(
        1.0 - design.alpha / 2.0, degrees_of_freedom
    )
    simultaneous_critical = _student_t_quantile(
        1.0 - design.alpha / (2.0 * simultaneous_contrasts),
        degrees_of_freedom,
    )

    category_results: dict[str, CategoryInference] = {}
    for category in CATEGORIES:
        estimate = sum(
            weight * result.contrasts[category] for result in stratum_results
        )
        variance = sum(
            weight * weight * result.mean_variances[category]
            for result in stratum_results
        )
        standard_error = math.sqrt(max(0.0, variance))
        inference_valid = standard_error > BOUNDARY_ABS_TOLERANCE
        lower = _bounded(estimate - one_sided_critical * standard_error)
        upper = _bounded(estimate + one_sided_critical * standard_error)
        margin = float(design.equivalence_margins[category])
        equivalent = (
            inference_valid
            and _strictly_above(lower, -margin)
            and _strictly_below(upper, margin)
        )
        category_results[category] = CategoryInference(
            category=category,
            estimate=estimate,
            variance=variance,
            standard_error=standard_error,
            degrees_of_freedom=degrees_of_freedom,
            one_sided_lower=lower,
            one_sided_upper=upper,
            one_sided_confidence_level=1.0 - design.alpha,
            equivalence_interval=Interval(
                estimate=estimate,
                lower=lower,
                upper=upper,
                confidence_level=1.0 - 2.0 * design.alpha,
                coverage_scope="pointwise TOST equivalence interval",
            ),
            equivalence_margin=margin,
            equivalence_status="equivalent" if equivalent else "not_established",
            marginal_two_sided_interval=_interval(
                estimate,
                standard_error,
                marginal_critical,
                1.0 - design.alpha,
            ),
            simultaneous_interval=_interval(
                estimate,
                standard_error,
                simultaneous_critical,
                1.0 - design.alpha / simultaneous_contrasts,
                coverage_scope="pointwise member of Bonferroni family",
                familywise_confidence_level=1.0 - design.alpha,
                family_size=simultaneous_contrasts,
            ),
            inference_valid=inference_valid,
            guard_reason=(
                None
                if inference_valid
                else "zero empirical standard error cannot establish a confirmatory claim"
            ),
        )

    h_valid = category_results["H"].inference_valid
    l_valid = category_results["L"].inference_valid
    h_passes = h_valid and _strictly_above(
        category_results["H"].one_sided_lower, design.positive_threshold
    )
    l_passes = l_valid and _strictly_below(
        category_results["L"].one_sided_upper, -design.positive_threshold
    )
    reverse_h_passes = h_valid and _strictly_below(
        category_results["H"].one_sided_upper, -design.positive_threshold
    )
    reverse_l_passes = l_valid and _strictly_above(
        category_results["L"].one_sided_lower, design.positive_threshold
    )
    positive_status = (
        "positive_observed_reallocation"
        if h_passes and l_passes
        else "not_established"
    )
    reverse_status = (
        "reverse_observed_reallocation"
        if reverse_h_passes and reverse_l_passes
        else "not_established"
    )
    equivalence_status = (
        "equivalent"
        if all(
            category_results[category].equivalence_status == "equivalent"
            for category in CATEGORIES
        )
        else "not_established"
    )
    return CellInference(
        cell=cell,
        claim_scope=(
            f"only exact model snapshot {cell.model_snapshot!r} and target "
            f"family {cell.target_family!r}, over the declared fine strata"
        ),
        required_fine_strata=required,
        blocks_by_fine_stratum={
            result.fine_stratum: result.n_blocks for result in stratum_results
        },
        equal_fine_stratum_weight=weight,
        fine_strata=tuple(stratum_results),
        categories=category_results,
        positive_status=positive_status,
        reverse_status=reverse_status,
        equivalence_status=equivalence_status,
    )


def analyze_confirmatory(
    observations: Iterable[ConfirmatoryObservation],
    *,
    design: ConfirmatoryDesign,
) -> ConfirmatoryAnalysis:
    """Run the complete four-cell confirmatory analysis.

    Headline positive and equivalence decisions are conjunctions: all four
    required cells must pass.  The pooled equal-cell estimates are supplied
    only as secondary summaries and cannot determine either headline.
    """

    if not isinstance(design, ConfirmatoryDesign):
        raise TypeError("design must be a ConfirmatoryDesign")
    rows = _enforce_confirmatory_firewall(observations, design)
    block_results, grouped = _validate_and_contrast_blocks(rows, design)
    simultaneous_contrasts = EXPECTED_MACRO_CELL_COUNT * len(CATEGORIES)
    cells = {
        cell.cell_id: _cell_inference(
            cell, grouped[cell], design, simultaneous_contrasts
        )
        for cell in design.cells
    }
    required_ids = tuple(cell.cell_id for cell in design.cells)

    positive_passing = tuple(
        cell_id
        for cell_id in required_ids
        if cells[cell_id].positive_status == "positive_observed_reallocation"
    )
    reverse_passing = tuple(
        cell_id
        for cell_id in required_ids
        if cells[cell_id].reverse_status == "reverse_observed_reallocation"
    )
    equivalence_passing = tuple(
        cell_id
        for cell_id in required_ids
        if cells[cell_id].equivalence_status == "equivalent"
    )
    positive_nonpassing = tuple(
        cell_id for cell_id in required_ids if cell_id not in positive_passing
    )
    reverse_nonpassing = tuple(
        cell_id for cell_id in required_ids if cell_id not in reverse_passing
    )
    equivalence_nonpassing = tuple(
        cell_id for cell_id in required_ids if cell_id not in equivalence_passing
    )

    positive_headline = HeadlineDecision(
        status=(
            "positive_observed_reallocation_established"
            if not positive_nonpassing
            else "not_established"
        ),
        claim=(
            "For assigned self-contingent minus assigned-schedule-matched yoke, "
            "observed follow-up disposition H is above +.05 and L is below -.05 "
            "in every required exact macro cell"
        ),
        required_cells=required_ids,
        passing_cells=positive_passing,
        nonpassing_cells=positive_nonpassing,
        method=POSITIVE_METHOD,
        boundary_policy=(
            "strict inequalities; equality within 1e-12 is nonpassing"
        ),
    )
    reverse_headline = HeadlineDecision(
        status=(
            "reverse_observed_reallocation_established"
            if not reverse_nonpassing
            else "not_established"
        ),
        claim=(
            "For assigned self-contingent minus assigned-schedule-matched yoke, "
            "observed follow-up disposition H is below -.05 and L is above +.05 "
            "in every required exact macro cell"
        ),
        required_cells=required_ids,
        passing_cells=reverse_passing,
        nonpassing_cells=reverse_nonpassing,
        method=REVERSE_METHOD,
        boundary_policy=(
            "strict inequalities; equality within 1e-12 is nonpassing"
        ),
    )
    equivalence_headline = HeadlineDecision(
        status=(
            "equivalence_established"
            if not equivalence_nonpassing
            else "not_established"
        ),
        claim=(
            "For assigned self-contingent minus assigned-schedule-matched yoke, "
            "the observed follow-up L/H/U disposition contrasts are strictly "
            "inside frozen margins L=.05, H=.05, U=.02 in every required exact "
            "macro cell"
        ),
        required_cells=required_ids,
        passing_cells=equivalence_passing,
        nonpassing_cells=equivalence_nonpassing,
        method=EQUIVALENCE_METHOD,
        boundary_policy=(
            "strict open margins; equality within 1e-12 is nonpassing"
        ),
    )

    pooled_categories: dict[str, PooledCategoryEstimate] = {}
    cell_weight = 1.0 / EXPECTED_MACRO_CELL_COUNT
    for category in CATEGORIES:
        category_cells = [cells[cell_id].categories[category] for cell_id in required_ids]
        estimate = sum(cell_weight * value.estimate for value in category_cells)
        variance = sum(
            cell_weight * cell_weight * value.variance for value in category_cells
        )
        pooled_categories[category] = PooledCategoryEstimate(
            category=category,
            estimate=estimate,
            variance=variance,
            standard_error=math.sqrt(max(0.0, variance)),
        )

    return ConfirmatoryAnalysis(
        design=design,
        block_contrasts=block_results,
        cells=cells,
        positive_headline=positive_headline,
        reverse_headline=reverse_headline,
        equivalence_headline=equivalence_headline,
        pooled_secondary=PooledSecondaryResult(
            role=(
                "secondary descriptive average only; cannot establish or "
                "rescue any all-cell headline"
            ),
            weighting="equal weight (1/4) for each prospectively required macro cell",
            categories=pooled_categories,
        ),
        inference_method=INFERENCE_METHOD,
        simultaneous_method=SIMULTANEOUS_METHOD,
        assumptions=(
            "canonical blocks are mutually independent",
            "fine strata and all four macro cells were fixed before outcomes",
            "block contrasts admit the stated fixed-stratum Student-t approximation",
            "block retention is not selected using follow-up outcomes",
            "Bonferroni provides familywise control if each constituent t bound is valid",
            "a zero empirical standard error is guarded and cannot establish positive, reverse, or equivalence claims",
        ),
    )


__all__ = [
    "ARMS",
    "BOUNDARY_ABS_TOLERANCE",
    "CALIBRATION_STUDY_PHASE",
    "CATEGORIES",
    "CellInference",
    "CellStrataRequirement",
    "ConfirmatoryAnalysis",
    "ConfirmatoryDesign",
    "ConfirmatoryObservation",
    "CONFIRMATORY_STUDY_PHASE",
    "FROZEN_ALPHA",
    "FROZEN_EQUIVALENCE_MARGINS",
    "FROZEN_POSITIVE_THRESHOLD",
    "FROZEN_TARGET_FAMILIES",
    "MacroCell",
    "analyze_confirmatory",
    "canonical_active_fine_strata",
    "canonical_block_fingerprint",
]
