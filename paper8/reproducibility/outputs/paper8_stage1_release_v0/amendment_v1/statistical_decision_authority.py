"""Exact, fail-closed statistical decision authority for the draft amendment.

This isolated module evaluates aggregate confirmatory evidence only.  It does
not make provider calls, read transcripts, alter the sealed zero-call trust
root, or replace the production integration gates.  Scientific comparisons use
``Decimal`` values parsed from one canonical, non-exponent decimal-string
grammar.  The ``1e-12`` numerical-integrity guard classifies standard errors and
strict boundary neighborhoods, but is explicitly not a substantive effect-size
increment.  Changing the frozen grid or sample structure requires re-proving it.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, fields
from decimal import Decimal, InvalidOperation
from enum import Enum
import json
import re
from typing import Final, TypeVar


PANEL_INPUT_SCHEMA_VERSION: Final = "binding-statistical-panel-input-v1"
PANEL_RESULT_SCHEMA_VERSION: Final = "binding-statistical-panel-result-v1"
POLICY_SCHEMA_VERSION: Final = "binding-statistical-decision-policy-v1"
TERMINAL_FLOW_POLICY_SCHEMA_VERSION: Final = "binding-terminal-flow-policy-v1"
REQUIRED_MACRO_CELL_COUNT: Final = 4
PRIMARY_THRESHOLD: Final = "0.05"
EQUIVALENCE_MARGINS: Final[dict[str, str]] = {
    "L": "0.05",
    "H": "0.05",
    "U": "0.02",
}
NUMERICAL_INTEGRITY_EPSILON: Final = "0.000000000001"
NUMERICAL_INTEGRITY_RATIONALE: Final = (
    "The frozen grid uses quarter-point block contrasts and at most 128 blocks "
    "per fine stratum at B=3072; its smallest one-stratum nonzero macro-cell "
    "standard error is approximately 8.14e-5, so 1e-12 is below attainable "
    "genuine nonzero resolution. Any grid or sample-structure change requires "
    "a new proof and recertification."
)

_DECIMAL_PATTERN: Final = re.compile(
    r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]*[1-9])?\Z"
)


class DecisionAuthorityError(ValueError):
    """Base class for closed decision-authority failures."""


class ClosedSchemaError(DecisionAuthorityError):
    """A machine-readable record did not have the exact closed field set."""


class Category(str, Enum):
    L = "L"
    H = "H"
    U = "U"


class Arm(str, Enum):
    SELF = "self"
    YOKE = "yoke"


class AssignedSchedule(str, Enum):
    L = "L"
    H = "H"


class TerminalSource(str, Enum):
    FOLLOWUP_CHOICE = "followup_choice"
    FOLLOWUP_UNAVAILABLE = "followup_unavailable"
    EXECUTION_FAILURE = "execution_failure"
    FOLLOWUP_FAILURE = "followup_failure"
    LOCAL_PROTOCOL_ABORT = "local_protocol_abort"


class FailureSubtype(str, Enum):
    NONE = "none"
    MISSING_RESPONSE = "missing_response"
    EMPTY_RESPONSE = "empty_response"
    EXPLICIT_REFUSAL = "explicit_refusal"
    INVALID_RESPONSE = "invalid_response"
    TRANSPORT_ERROR = "transport_error"
    TIMEOUT = "timeout"
    PROVIDER_ERROR = "provider_error"
    QUOTA_EXHAUSTED = "quota_exhausted"
    TOOL_ERROR = "tool_error"
    TOOL_LIMIT_EXCEEDED = "tool_limit_exceeded"
    ASSIGNMENT_BINDING_MISMATCH = "assignment_binding_mismatch"
    SCHEDULE_INTEGRITY_MISMATCH = "schedule_integrity_mismatch"
    ROLE_LEAK_DETECTED = "role_leak_detected"
    RUNTIME_CONTRACT_VIOLATION = "runtime_contract_violation"
    CONTROLLER_ABORT = "controller_abort"
    UNKNOWN = "unknown"


class ProvenanceStatus(str, Enum):
    VALID = "PROVENANCE_VALID"
    INVALID_PHASE = "PROVENANCE_INVALID_PHASE"
    INVALID_BINDING = "PROVENANCE_INVALID_BINDING"
    INVALID_CONTAMINATION = "PROVENANCE_INVALID_CONTAMINATION"


class LedgerStatus(str, Enum):
    VALID = "LEDGER_VALID"
    INVALID_MISSING_TERMINAL = "LEDGER_INVALID_MISSING_TERMINAL"
    INVALID_DUPLICATE_TERMINAL = "LEDGER_INVALID_DUPLICATE_TERMINAL"
    INVALID_EXTRA_TERMINAL = "LEDGER_INVALID_EXTRA_TERMINAL"
    INVALID_BINDING_MISMATCH = "LEDGER_INVALID_BINDING_MISMATCH"
    INVALID_TAXONOMY = "LEDGER_INVALID_TAXONOMY"
    INVALID_BLOCK_CARDINALITY = "LEDGER_INVALID_BLOCK_CARDINALITY"


class AssignmentStatus(str, Enum):
    VALID = "ASSIGNMENT_VALID"
    INVALID_PROVENANCE = "ASSIGNMENT_INVALID_PROVENANCE"
    INVALID_MEMBER = "ASSIGNMENT_INVALID_MEMBER"
    INVALID_BALANCE = "ASSIGNMENT_INVALID_BALANCE"
    INVALID_DONOR_MAP = "ASSIGNMENT_INVALID_DONOR_MAP"
    INVALID_MATERIALIZATION = "EXPOSURE_INVALID_MATERIALIZATION"
    INVALID_TREATMENT_LEAKAGE = "DESIGN_INVALID_TREATMENT_LEAKAGE"
    INVALID_POSTRANDOMIZATION_SELECTION = (
        "DESIGN_INVALID_POSTRANDOMIZATION_SELECTION"
    )
    INVALID_RUN_DEVIATION = "DESIGN_INVALID_RUN_DEVIATION"


class SupportStatus(str, Enum):
    VALID = "SUPPORT_VALID"
    INVALID_SESSION_ARM = "SUPPORT_INVALID_SESSION_ARM"
    INVALID_EXPOSURE = "SUPPORT_INVALID_EXPOSURE"
    INSUFFICIENT_FINE_STRATUM = "SUPPORT_INSUFFICIENT_FINE_STRATUM"
    INSUFFICIENT_MACRO_CELL = "SUPPORT_INSUFFICIENT_MACRO_CELL"
    INVALID_REWEIGHTING = "SUPPORT_INVALID_REWEIGHTING"


class ComponentValidity(str, Enum):
    VALID = "COMPONENT_VALID"
    MISSING = "COMPONENT_INVALID_MISSING"
    INVALID_INTERVAL_ORDER = "COMPONENT_INVALID_INTERVAL_ORDER"
    INVALID_NEGATIVE_STANDARD_ERROR = "COMPONENT_INVALID_NEGATIVE_SE"
    INVALID_ZERO_STANDARD_ERROR = "COMPONENT_INFERENCE_INVALID_ZERO_SE"


class DirectionalFlag(str, Enum):
    H_UP_PASS = "H_UP_PASS"
    H_UP_BOUNDARY_NOT_PASS = "H_UP_BOUNDARY_NOT_PASS"
    H_UP_NOT_PASS = "H_UP_NOT_PASS"
    L_DOWN_PASS = "L_DOWN_PASS"
    L_DOWN_BOUNDARY_NOT_PASS = "L_DOWN_BOUNDARY_NOT_PASS"
    L_DOWN_NOT_PASS = "L_DOWN_NOT_PASS"


class EquivalenceFlag(str, Enum):
    PASS = "EQUIVALENCE_PASS"
    BOUNDARY_NOT_PASS = "EQUIVALENCE_BOUNDARY_NOT_PASS"
    NOT_PASS = "EQUIVALENCE_NOT_PASS"
    INFERENCE_INVALID = "EQUIVALENCE_INFERENCE_INVALID"


class CellEligibility(str, Enum):
    ELIGIBLE = "CELL_ELIGIBLE"
    DESIGN_INVALID_PROVENANCE = "CELL_DESIGN_INVALID_PROVENANCE"
    DESIGN_INVALID_LEDGER = "CELL_DESIGN_INVALID_LEDGER"
    DESIGN_INVALID_ASSIGNMENT = "CELL_DESIGN_INVALID_ASSIGNMENT"
    DESIGN_INVALID_TERMINAL_INTEGRITY = (
        "CELL_DESIGN_INVALID_TERMINAL_INTEGRITY"
    )
    SUPPORT_INSUFFICIENT = "CELL_SUPPORT_INSUFFICIENT"
    INFERENCE_INVALID_DATA = "CELL_INFERENCE_INVALID_DATA"


class CellPrimaryDecision(str, Enum):
    ESTABLISHED = "CELL_PAIRED_H_UP_L_DOWN_ESTABLISHED"
    NOT_ESTABLISHED = "CELL_PAIRED_H_UP_L_DOWN_NOT_ESTABLISHED"
    BOUNDARY_NOT_ESTABLISHED = "CELL_DIRECTIONAL_BOUNDARY_NOT_ESTABLISHED"
    INFERENCE_INVALID = "CELL_DIRECTIONAL_INFERENCE_INVALID"
    SUPPORT_INSUFFICIENT = "CELL_PRIMARY_SUPPORT_INSUFFICIENT"
    DESIGN_INVALID = "CELL_PRIMARY_DESIGN_INVALID"


class CellEquivalenceDecision(str, Enum):
    ESTABLISHED = "CELL_OBSERVED_VECTOR_EQUIVALENCE_ESTABLISHED"
    NOT_ESTABLISHED = "CELL_OBSERVED_VECTOR_EQUIVALENCE_NOT_ESTABLISHED"
    BOUNDARY_NOT_ESTABLISHED = (
        "CELL_OBSERVED_VECTOR_EQUIVALENCE_BOUNDARY_NOT_ESTABLISHED"
    )
    INFERENCE_INVALID = "CELL_OBSERVED_VECTOR_EQUIVALENCE_INFERENCE_INVALID"
    SUPPORT_INSUFFICIENT = "CELL_EQUIVALENCE_SUPPORT_INSUFFICIENT"
    DESIGN_INVALID = "CELL_EQUIVALENCE_DESIGN_INVALID"


class PanelPrimaryDecision(str, Enum):
    ESTABLISHED = "PANEL_PAIRED_H_UP_L_DOWN_ESTABLISHED_ALL_CELLS"
    NOT_ESTABLISHED = "PANEL_DIRECTIONAL_NOT_ESTABLISHED"
    BOUNDARY_NOT_ESTABLISHED = "PANEL_DIRECTIONAL_BOUNDARY_NOT_ESTABLISHED"
    INFERENCE_INVALID = "PANEL_DIRECTIONAL_INFERENCE_INVALID"
    SUPPORT_INSUFFICIENT = "PANEL_SUPPORT_INSUFFICIENT"
    DESIGN_INVALID = "PANEL_DESIGN_INVALID"


class PanelEquivalenceDecision(str, Enum):
    ESTABLISHED = "PANEL_OBSERVED_VECTOR_EQUIVALENCE_ESTABLISHED_ALL_CELLS"
    NOT_ESTABLISHED = "PANEL_OBSERVED_VECTOR_EQUIVALENCE_NOT_ESTABLISHED"
    BOUNDARY_NOT_ESTABLISHED = (
        "PANEL_OBSERVED_VECTOR_EQUIVALENCE_BOUNDARY_NOT_ESTABLISHED"
    )
    INFERENCE_INVALID = "PANEL_OBSERVED_VECTOR_EQUIVALENCE_INFERENCE_INVALID"
    SUPPORT_INSUFFICIENT = "PANEL_EQUIVALENCE_SUPPORT_INSUFFICIENT"
    DESIGN_INVALID = "PANEL_EQUIVALENCE_DESIGN_INVALID"


_TERMINAL_SOURCE_RULES: Final = (
    (
        TerminalSource.FOLLOWUP_CHOICE,
        (FailureSubtype.NONE,),
        (Category.L, Category.H),
    ),
    (
        TerminalSource.FOLLOWUP_UNAVAILABLE,
        (
            FailureSubtype.MISSING_RESPONSE,
            FailureSubtype.EMPTY_RESPONSE,
            FailureSubtype.EXPLICIT_REFUSAL,
            FailureSubtype.INVALID_RESPONSE,
        ),
        (Category.U,),
    ),
    (
        TerminalSource.EXECUTION_FAILURE,
        (
            FailureSubtype.INVALID_RESPONSE,
            FailureSubtype.TRANSPORT_ERROR,
            FailureSubtype.TIMEOUT,
            FailureSubtype.PROVIDER_ERROR,
            FailureSubtype.QUOTA_EXHAUSTED,
            FailureSubtype.TOOL_ERROR,
            FailureSubtype.TOOL_LIMIT_EXCEEDED,
        ),
        (Category.U,),
    ),
    (
        TerminalSource.FOLLOWUP_FAILURE,
        (
            FailureSubtype.TRANSPORT_ERROR,
            FailureSubtype.TIMEOUT,
            FailureSubtype.PROVIDER_ERROR,
            FailureSubtype.QUOTA_EXHAUSTED,
        ),
        (Category.U,),
    ),
    (
        TerminalSource.LOCAL_PROTOCOL_ABORT,
        (
            FailureSubtype.ASSIGNMENT_BINDING_MISMATCH,
            FailureSubtype.SCHEDULE_INTEGRITY_MISMATCH,
            FailureSubtype.ROLE_LEAK_DETECTED,
            FailureSubtype.RUNTIME_CONTRACT_VIOLATION,
            FailureSubtype.CONTROLLER_ABORT,
            FailureSubtype.UNKNOWN,
        ),
        (Category.U,),
    ),
)

_ALLOWED_SUBTYPES: Final = {
    source: frozenset(subtypes)
    for source, subtypes, _dispositions in _TERMINAL_SOURCE_RULES
}
_ALLOWED_DISPOSITIONS: Final = {
    source: frozenset(dispositions)
    for source, _subtypes, dispositions in _TERMINAL_SOURCE_RULES
}

_CATEGORY_ORDER: Final = {value: index for index, value in enumerate(Category)}
_ARM_ORDER: Final = {value: index for index, value in enumerate(Arm)}
_SCHEDULE_ORDER: Final = {
    value: index for index, value in enumerate(AssignedSchedule)
}
_SOURCE_ORDER: Final = {value: index for index, value in enumerate(TerminalSource)}


def canonical_json(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def _canonical_decimal(name: str, value: object) -> Decimal:
    if not isinstance(value, str) or _DECIMAL_PATTERN.fullmatch(value) is None:
        raise ClosedSchemaError(
            f"{name} must be a canonical non-exponent decimal string"
        )
    if value == "-0":
        raise ClosedSchemaError(f"{name} must encode zero as '0'")
    try:
        parsed = Decimal(value)
    except InvalidOperation as error:
        raise ClosedSchemaError(f"{name} is not a decimal") from error
    if not parsed.is_finite():
        raise ClosedSchemaError(f"{name} must be finite")
    return parsed


def _exact_fields(
    name: str,
    record: object,
    expected: set[str],
) -> Mapping[str, object]:
    if not isinstance(record, Mapping):
        raise ClosedSchemaError(f"{name} must be a mapping")
    supplied = set(record)
    missing = sorted(expected - supplied)
    extra = sorted(supplied - expected, key=str)
    if missing or extra or not all(isinstance(key, str) for key in record):
        raise ClosedSchemaError(
            f"{name} fields must match exactly; missing={missing}, extra={extra}"
        )
    return record


EnumT = TypeVar("EnumT", bound=Enum)


def _enum_value(enum_type: type[EnumT], name: str, value: object) -> EnumT:
    if not isinstance(value, str):
        raise ClosedSchemaError(f"{name} must be a string enum value")
    try:
        return enum_type(value)
    except ValueError as error:
        raise ClosedSchemaError(f"{name} has an unknown enum value") from error


def _text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ClosedSchemaError(f"{name} must be a nonempty trimmed string")
    return value


@dataclass(frozen=True, slots=True)
class TerminalFlowPolicy:
    """Closed ordered taxonomy and integrity semantics for terminal flows."""

    schema_version: str = TERMINAL_FLOW_POLICY_SCHEMA_VERSION
    source_rules: tuple = _TERMINAL_SOURCE_RULES
    local_protocol_abort_retains_composite_u_ledger_row: bool = True
    local_protocol_abort_marks_integrity_failure: bool = True
    local_protocol_abort_invalidates_affected_macro_cell_headline: bool = True
    local_protocol_abort_invalidates_all_cell_headline: bool = True
    valid_cell_decomposition_requires_valid_ledger_assignment_and_support: bool = True
    valid_cell_terminal_rows_per_complete_block: int = 8
    valid_cell_arm_order: tuple[Arm, ...] = tuple(Arm)
    valid_cell_assigned_schedule_order: tuple[AssignedSchedule, ...] = tuple(
        AssignedSchedule
    )
    valid_cell_rows_per_arm_assigned_schedule_per_complete_block: int = 2

    def __post_init__(self) -> None:
        actual = (
            self.schema_version,
            self.source_rules,
            self.local_protocol_abort_retains_composite_u_ledger_row,
            self.local_protocol_abort_marks_integrity_failure,
            self.local_protocol_abort_invalidates_affected_macro_cell_headline,
            self.local_protocol_abort_invalidates_all_cell_headline,
            self.valid_cell_decomposition_requires_valid_ledger_assignment_and_support,
            self.valid_cell_terminal_rows_per_complete_block,
            self.valid_cell_arm_order,
            self.valid_cell_assigned_schedule_order,
            self.valid_cell_rows_per_arm_assigned_schedule_per_complete_block,
        )
        expected = (
            TERMINAL_FLOW_POLICY_SCHEMA_VERSION,
            _TERMINAL_SOURCE_RULES,
            True,
            True,
            True,
            True,
            True,
            8,
            tuple(Arm),
            tuple(AssignedSchedule),
            2,
        )
        if actual != expected:
            raise DecisionAuthorityError(
                "terminal-flow policy fields are immutable constants"
            )

    def to_mapping(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "source_rules": [
                {
                    "source": source.value,
                    "allowed_subtypes": [subtype.value for subtype in subtypes],
                    "allowed_dispositions": [
                        disposition.value for disposition in dispositions
                    ],
                }
                for source, subtypes, dispositions in self.source_rules
            ],
            "local_protocol_abort_integrity": {
                "retains_composite_u_ledger_row": (
                    self.local_protocol_abort_retains_composite_u_ledger_row
                ),
                "marks_integrity_failure": (
                    self.local_protocol_abort_marks_integrity_failure
                ),
                "invalidates_affected_macro_cell_headline": (
                    self.local_protocol_abort_invalidates_affected_macro_cell_headline
                ),
                "invalidates_all_cell_headline": (
                    self.local_protocol_abort_invalidates_all_cell_headline
                ),
            },
            "valid_cell_decomposition": {
                "requires_valid_ledger_assignment_and_support": (
                    self.valid_cell_decomposition_requires_valid_ledger_assignment_and_support
                ),
                "terminal_rows_per_complete_block": (
                    self.valid_cell_terminal_rows_per_complete_block
                ),
                "arm_order": [arm.value for arm in self.valid_cell_arm_order],
                "assigned_schedule_order": [
                    schedule.value
                    for schedule in self.valid_cell_assigned_schedule_order
                ],
                "rows_per_arm_assigned_schedule_per_complete_block": (
                    self.valid_cell_rows_per_arm_assigned_schedule_per_complete_block
                ),
            },
        }


TERMINAL_FLOW_POLICY: Final = TerminalFlowPolicy()


@dataclass(frozen=True, slots=True)
class DecisionPolicy:
    """Immutable, machine-readable amendment-frozen scientific policy."""

    schema_version: str = POLICY_SCHEMA_VERSION
    required_macro_cell_count: int = REQUIRED_MACRO_CELL_COUNT
    categories: tuple[str, ...] = ("L", "H", "U")
    primary_direction: str = "paired_H_up_L_down"
    primary_threshold: str = PRIMARY_THRESHOLD
    primary_has_u_guard: bool = False
    primary_requires_separate_u_reporting: bool = True
    equivalence_margins: tuple[tuple[str, str], ...] = (
        ("L", "0.05"),
        ("H", "0.05"),
        ("U", "0.02"),
    )
    vector_equivalence_role: str = "secondary_non_authorizing"
    vector_equivalence_can_create_rescue_or_veto_primary: bool = False
    standard_error_rule: str = "finite_standard_error_at_or_below_epsilon_is_inference_invalid"
    positive_standard_error_rule: str = "every_finite_standard_error_strictly_above_epsilon_is_eligible"
    numerical_integrity_epsilon: str = NUMERICAL_INTEGRITY_EPSILON
    effect_and_margin_boundaries_use_epsilon_guard_bands: bool = True
    epsilon_is_substantive_effect_increment: bool = False
    grid_or_sample_change_requires_epsilon_reproof: bool = True
    complete_component_estimates_must_sum_to_zero_within_epsilon: bool = True
    positive_standard_error_requires_strict_estimate_within_bounds: bool = True
    component_bounds_recomputed_by_this_authority: bool = False
    degrees_of_freedom_recomputed_by_this_authority: bool = False
    upstream_frozen_analyzer_provenance_required: bool = True
    numerical_integrity_rationale: str = NUMERICAL_INTEGRITY_RATIONALE
    ordinary_failure_disposition: str = "U"
    local_abort_retains_u_row: bool = True
    local_abort_invalidates_affected_and_panel_headlines: bool = True
    mandatory_reporting_fields: tuple[str, ...] = (
        "U_simultaneous_interval_by_macro_cell",
        "terminal_source_subtype_counts_by_arm_assigned_schedule_macro_cell",
    )

    def __post_init__(self) -> None:
        actual = (
            self.schema_version,
            self.required_macro_cell_count,
            self.categories,
            self.primary_direction,
            self.primary_threshold,
            self.primary_has_u_guard,
            self.primary_requires_separate_u_reporting,
            self.equivalence_margins,
            self.vector_equivalence_role,
            self.vector_equivalence_can_create_rescue_or_veto_primary,
            self.standard_error_rule,
            self.positive_standard_error_rule,
            self.numerical_integrity_epsilon,
            self.effect_and_margin_boundaries_use_epsilon_guard_bands,
            self.epsilon_is_substantive_effect_increment,
            self.grid_or_sample_change_requires_epsilon_reproof,
            self.complete_component_estimates_must_sum_to_zero_within_epsilon,
            self.positive_standard_error_requires_strict_estimate_within_bounds,
            self.component_bounds_recomputed_by_this_authority,
            self.degrees_of_freedom_recomputed_by_this_authority,
            self.upstream_frozen_analyzer_provenance_required,
            self.numerical_integrity_rationale,
            self.ordinary_failure_disposition,
            self.local_abort_retains_u_row,
            self.local_abort_invalidates_affected_and_panel_headlines,
            self.mandatory_reporting_fields,
        )
        expected = (
            POLICY_SCHEMA_VERSION,
            REQUIRED_MACRO_CELL_COUNT,
            ("L", "H", "U"),
            "paired_H_up_L_down",
            PRIMARY_THRESHOLD,
            False,
            True,
            (("L", "0.05"), ("H", "0.05"), ("U", "0.02")),
            "secondary_non_authorizing",
            False,
            "finite_standard_error_at_or_below_epsilon_is_inference_invalid",
            "every_finite_standard_error_strictly_above_epsilon_is_eligible",
            NUMERICAL_INTEGRITY_EPSILON,
            True,
            False,
            True,
            True,
            True,
            False,
            False,
            True,
            NUMERICAL_INTEGRITY_RATIONALE,
            "U",
            True,
            True,
            (
                "U_simultaneous_interval_by_macro_cell",
                "terminal_source_subtype_counts_by_arm_assigned_schedule_macro_cell",
            ),
        )
        if actual != expected:
            raise DecisionAuthorityError("decision policy fields are immutable constants")

    def to_mapping(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "required_macro_cell_count": self.required_macro_cell_count,
            "categories": list(self.categories),
            "primary_direction": self.primary_direction,
            "primary_threshold": self.primary_threshold,
            "primary_has_u_guard": self.primary_has_u_guard,
            "primary_requires_separate_u_reporting": (
                self.primary_requires_separate_u_reporting
            ),
            "equivalence_margins": {
                category: margin for category, margin in self.equivalence_margins
            },
            "vector_equivalence_role": self.vector_equivalence_role,
            "vector_equivalence_can_create_rescue_or_veto_primary": (
                self.vector_equivalence_can_create_rescue_or_veto_primary
            ),
            "standard_error_rule": self.standard_error_rule,
            "positive_standard_error_rule": self.positive_standard_error_rule,
            "numerical_integrity_epsilon": self.numerical_integrity_epsilon,
            "effect_and_margin_boundaries_use_epsilon_guard_bands": (
                self.effect_and_margin_boundaries_use_epsilon_guard_bands
            ),
            "epsilon_is_substantive_effect_increment": (
                self.epsilon_is_substantive_effect_increment
            ),
            "grid_or_sample_change_requires_epsilon_reproof": (
                self.grid_or_sample_change_requires_epsilon_reproof
            ),
            "complete_component_estimates_must_sum_to_zero_within_epsilon": (
                self.complete_component_estimates_must_sum_to_zero_within_epsilon
            ),
            "positive_standard_error_requires_strict_estimate_within_bounds": (
                self.positive_standard_error_requires_strict_estimate_within_bounds
            ),
            "component_bounds_recomputed_by_this_authority": (
                self.component_bounds_recomputed_by_this_authority
            ),
            "degrees_of_freedom_recomputed_by_this_authority": (
                self.degrees_of_freedom_recomputed_by_this_authority
            ),
            "upstream_frozen_analyzer_provenance_required": (
                self.upstream_frozen_analyzer_provenance_required
            ),
            "numerical_integrity_rationale": self.numerical_integrity_rationale,
            "ordinary_failure_disposition": self.ordinary_failure_disposition,
            "local_abort_retains_u_row": self.local_abort_retains_u_row,
            "local_abort_invalidates_affected_and_panel_headlines": (
                self.local_abort_invalidates_affected_and_panel_headlines
            ),
            "mandatory_reporting_fields": list(self.mandatory_reporting_fields),
        }


POLICY: Final = DecisionPolicy()


@dataclass(frozen=True, slots=True)
class TerminalFlowCount:
    source: TerminalSource
    subtype: FailureSubtype
    disposition: Category
    arm: Arm
    assigned_schedule: AssignedSchedule
    count: int

    def __post_init__(self) -> None:
        if not isinstance(self.source, TerminalSource):
            raise TypeError("source must be TerminalSource")
        if not isinstance(self.subtype, FailureSubtype):
            raise TypeError("subtype must be FailureSubtype")
        if not isinstance(self.disposition, Category):
            raise TypeError("disposition must be Category")
        if not isinstance(self.arm, Arm):
            raise TypeError("arm must be Arm")
        if not isinstance(self.assigned_schedule, AssignedSchedule):
            raise TypeError("assigned_schedule must be AssignedSchedule")
        if type(self.count) is not int or self.count < 1:
            raise DecisionAuthorityError("terminal flow count must be a positive integer")
        if self.subtype not in _ALLOWED_SUBTYPES[self.source]:
            raise DecisionAuthorityError("failure subtype is not allowed for source")
        if self.disposition not in _ALLOWED_DISPOSITIONS[self.source]:
            raise DecisionAuthorityError(
                "terminal-flow disposition is not allowed for source"
            )

    @property
    def is_local_integrity_abort(self) -> bool:
        return self.source is TerminalSource.LOCAL_PROTOCOL_ABORT

    def to_mapping(self) -> dict[str, object]:
        return {
            "source": self.source.value,
            "subtype": self.subtype.value,
            "disposition": self.disposition.value,
            "arm": self.arm.value,
            "assigned_schedule": self.assigned_schedule.value,
            "count": self.count,
        }

    @classmethod
    def from_mapping(cls, record: object) -> TerminalFlowCount:
        expected = {field.name for field in fields(cls)}
        value = _exact_fields("terminal flow", record, expected)
        return cls(
            source=_enum_value(TerminalSource, "source", value["source"]),
            subtype=_enum_value(FailureSubtype, "subtype", value["subtype"]),
            disposition=_enum_value(Category, "disposition", value["disposition"]),
            arm=_enum_value(Arm, "arm", value["arm"]),
            assigned_schedule=_enum_value(
                AssignedSchedule,
                "assigned_schedule",
                value["assigned_schedule"],
            ),
            count=value["count"],  # type: ignore[arg-type]
        )


@dataclass(frozen=True, slots=True)
class ComponentEvidence:
    category: Category
    estimate: str
    lower_bound: str
    upper_bound: str
    standard_error: str

    def __post_init__(self) -> None:
        if not isinstance(self.category, Category):
            raise TypeError("category must be Category")
        for name in ("estimate", "lower_bound", "upper_bound"):
            parsed = _canonical_decimal(name, getattr(self, name))
            if parsed < Decimal("-1") or parsed > Decimal("1"):
                raise DecisionAuthorityError(f"{name} must lie in [-1,1]")
        _canonical_decimal("standard_error", self.standard_error)

    @property
    def estimate_decimal(self) -> Decimal:
        return Decimal(self.estimate)

    @property
    def lower_decimal(self) -> Decimal:
        return Decimal(self.lower_bound)

    @property
    def upper_decimal(self) -> Decimal:
        return Decimal(self.upper_bound)

    @property
    def standard_error_decimal(self) -> Decimal:
        return Decimal(self.standard_error)

    def to_mapping(self) -> dict[str, object]:
        return {
            "category": self.category.value,
            "estimate": self.estimate,
            "lower_bound": self.lower_bound,
            "upper_bound": self.upper_bound,
            "standard_error": self.standard_error,
        }

    @classmethod
    def from_mapping(cls, record: object) -> ComponentEvidence:
        expected = {field.name for field in fields(cls)}
        value = _exact_fields("component evidence", record, expected)
        return cls(
            category=_enum_value(Category, "category", value["category"]),
            estimate=value["estimate"],  # type: ignore[arg-type]
            lower_bound=value["lower_bound"],  # type: ignore[arg-type]
            upper_bound=value["upper_bound"],  # type: ignore[arg-type]
            standard_error=value["standard_error"],  # type: ignore[arg-type]
        )


def _flow_sort_key(flow: TerminalFlowCount) -> tuple[int, int, int, str, int]:
    return (
        _ARM_ORDER[flow.arm],
        _SCHEDULE_ORDER[flow.assigned_schedule],
        _SOURCE_ORDER[flow.source],
        flow.subtype.value,
        _CATEGORY_ORDER[flow.disposition],
    )


@dataclass(frozen=True, slots=True)
class MacroCellEvidence:
    macro_cell_id: str
    ledger_status: LedgerStatus
    assignment_status: AssignmentStatus
    support_status: SupportStatus
    terminal_row_count: int
    terminal_flows: tuple[TerminalFlowCount, ...]
    components: tuple[ComponentEvidence, ...]

    def __post_init__(self) -> None:
        _text("macro_cell_id", self.macro_cell_id)
        if not isinstance(self.ledger_status, LedgerStatus):
            raise TypeError("ledger_status must be LedgerStatus")
        if not isinstance(self.assignment_status, AssignmentStatus):
            raise TypeError("assignment_status must be AssignmentStatus")
        if not isinstance(self.support_status, SupportStatus):
            raise TypeError("support_status must be SupportStatus")
        if type(self.terminal_row_count) is not int or self.terminal_row_count < 0:
            raise DecisionAuthorityError("terminal_row_count must be a nonnegative integer")
        if not isinstance(self.terminal_flows, tuple) or not all(
            isinstance(flow, TerminalFlowCount) for flow in self.terminal_flows
        ):
            raise DecisionAuthorityError(
                "terminal_flows must be a tuple of TerminalFlowCount"
            )
        if tuple(sorted(self.terminal_flows, key=_flow_sort_key)) != self.terminal_flows:
            raise DecisionAuthorityError("terminal_flows must be in canonical order")
        flow_keys = {
            (
                flow.arm,
                flow.assigned_schedule,
                flow.source,
                flow.subtype,
                flow.disposition,
            )
            for flow in self.terminal_flows
        }
        if len(flow_keys) != len(self.terminal_flows):
            raise DecisionAuthorityError("terminal flow keys must be unique")
        if self.ledger_status is LedgerStatus.VALID and sum(
            flow.count for flow in self.terminal_flows
        ) != self.terminal_row_count:
            raise DecisionAuthorityError(
                "a valid ledger's terminal flows must sum to terminal_row_count"
            )
        if (
            self.ledger_status is LedgerStatus.VALID
            and self.assignment_status is AssignmentStatus.VALID
            and self.support_status is SupportStatus.VALID
        ):
            rows_per_block = (
                TERMINAL_FLOW_POLICY.valid_cell_terminal_rows_per_complete_block
            )
            if self.terminal_row_count < rows_per_block or (
                self.terminal_row_count % rows_per_block != 0
            ):
                raise DecisionAuthorityError(
                    "a fully valid macro cell's terminal_row_count must be a "
                    "positive multiple of eight"
                )
            expected_per_combination = self.terminal_row_count // (
                len(Arm) * len(AssignedSchedule)
            )
            combination_totals = {
                (arm, schedule): 0
                for arm in Arm
                for schedule in AssignedSchedule
            }
            for flow in self.terminal_flows:
                combination_totals[(flow.arm, flow.assigned_schedule)] += flow.count
            if any(
                total != expected_per_combination
                for total in combination_totals.values()
            ):
                raise DecisionAuthorityError(
                    "a fully valid macro cell must have exact terminal-row balance "
                    "across arm and assigned schedule"
                )
        if self.support_status is SupportStatus.VALID and self.terminal_row_count < 1:
            raise DecisionAuthorityError(
                "a supported macro cell must contain at least one terminal row"
            )
        if not isinstance(self.components, tuple) or not all(
            isinstance(component, ComponentEvidence) for component in self.components
        ):
            raise DecisionAuthorityError(
                "components must be a tuple of ComponentEvidence"
            )
        categories = tuple(component.category for component in self.components)
        if categories != tuple(sorted(categories, key=_CATEGORY_ORDER.__getitem__)):
            raise DecisionAuthorityError("components must be in canonical L/H/U order")
        if len(set(categories)) != len(categories):
            raise DecisionAuthorityError("component categories must be unique")
        if categories == tuple(Category):
            estimate_sum = sum(
                (component.estimate_decimal for component in self.components),
                start=Decimal("0"),
            )
            if abs(estimate_sum) > Decimal(NUMERICAL_INTEGRITY_EPSILON):
                raise DecisionAuthorityError(
                    "complete L/H/U component estimates must sum to zero within "
                    "the frozen numerical-integrity epsilon"
                )

    @property
    def has_local_integrity_abort(self) -> bool:
        return any(flow.is_local_integrity_abort for flow in self.terminal_flows)

    def to_mapping(self) -> dict[str, object]:
        return {
            "macro_cell_id": self.macro_cell_id,
            "ledger_status": self.ledger_status.value,
            "assignment_status": self.assignment_status.value,
            "support_status": self.support_status.value,
            "terminal_row_count": self.terminal_row_count,
            "terminal_flows": [flow.to_mapping() for flow in self.terminal_flows],
            "components": [component.to_mapping() for component in self.components],
        }

    @classmethod
    def from_mapping(cls, record: object) -> MacroCellEvidence:
        expected = {field.name for field in fields(cls)}
        value = _exact_fields("macro-cell evidence", record, expected)
        raw_flows = value["terminal_flows"]
        raw_components = value["components"]
        if not isinstance(raw_flows, list) or not isinstance(raw_components, list):
            raise ClosedSchemaError("terminal_flows and components must be JSON lists")
        return cls(
            macro_cell_id=value["macro_cell_id"],  # type: ignore[arg-type]
            ledger_status=_enum_value(
                LedgerStatus, "ledger_status", value["ledger_status"]
            ),
            assignment_status=_enum_value(
                AssignmentStatus,
                "assignment_status",
                value["assignment_status"],
            ),
            support_status=_enum_value(
                SupportStatus, "support_status", value["support_status"]
            ),
            terminal_row_count=value["terminal_row_count"],  # type: ignore[arg-type]
            terminal_flows=tuple(
                TerminalFlowCount.from_mapping(flow) for flow in raw_flows
            ),
            components=tuple(
                ComponentEvidence.from_mapping(component)
                for component in raw_components
            ),
        )


@dataclass(frozen=True, slots=True)
class PanelEvidence:
    required_macro_cell_ids: tuple[str, ...]
    provenance_status: ProvenanceStatus
    cells: tuple[MacroCellEvidence, ...]
    schema_version: str = PANEL_INPUT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.schema_version != PANEL_INPUT_SCHEMA_VERSION:
            raise DecisionAuthorityError(
                f"schema_version must equal {PANEL_INPUT_SCHEMA_VERSION!r}"
            )
        if not isinstance(self.required_macro_cell_ids, tuple) or len(
            self.required_macro_cell_ids
        ) != REQUIRED_MACRO_CELL_COUNT:
            raise DecisionAuthorityError("exactly four required macro-cell IDs are mandatory")
        for cell_id in self.required_macro_cell_ids:
            _text("required macro-cell ID", cell_id)
        if self.required_macro_cell_ids != tuple(sorted(self.required_macro_cell_ids)):
            raise DecisionAuthorityError("required macro-cell IDs must be sorted")
        if len(set(self.required_macro_cell_ids)) != REQUIRED_MACRO_CELL_COUNT:
            raise DecisionAuthorityError("required macro-cell IDs must be unique")
        if not isinstance(self.provenance_status, ProvenanceStatus):
            raise TypeError("provenance_status must be ProvenanceStatus")
        if not isinstance(self.cells, tuple) or not all(
            isinstance(cell, MacroCellEvidence) for cell in self.cells
        ):
            raise DecisionAuthorityError("cells must be a tuple of MacroCellEvidence")
        cell_ids = tuple(cell.macro_cell_id for cell in self.cells)
        if cell_ids != tuple(sorted(cell_ids)) or len(set(cell_ids)) != len(cell_ids):
            raise DecisionAuthorityError("supplied cells must have unique sorted IDs")
        if not set(cell_ids).issubset(self.required_macro_cell_ids):
            raise DecisionAuthorityError("supplied cell is outside the required panel")

    def to_mapping(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "required_macro_cell_ids": list(self.required_macro_cell_ids),
            "provenance_status": self.provenance_status.value,
            "cells": [cell.to_mapping() for cell in self.cells],
        }

    def to_json(self) -> str:
        return canonical_json(self.to_mapping())

    @classmethod
    def from_mapping(cls, record: object) -> PanelEvidence:
        expected = {field.name for field in fields(cls)}
        value = _exact_fields("panel evidence", record, expected)
        raw_ids = value["required_macro_cell_ids"]
        raw_cells = value["cells"]
        if not isinstance(raw_ids, list) or not all(
            isinstance(item, str) for item in raw_ids
        ):
            raise ClosedSchemaError("required_macro_cell_ids must be a JSON string list")
        if not isinstance(raw_cells, list):
            raise ClosedSchemaError("cells must be a JSON list")
        return cls(
            schema_version=value["schema_version"],  # type: ignore[arg-type]
            required_macro_cell_ids=tuple(raw_ids),
            provenance_status=_enum_value(
                ProvenanceStatus,
                "provenance_status",
                value["provenance_status"],
            ),
            cells=tuple(MacroCellEvidence.from_mapping(cell) for cell in raw_cells),
        )


@dataclass(frozen=True, slots=True)
class ComponentDecision:
    category: Category
    validity: ComponentValidity
    directional_flag: DirectionalFlag | None
    equivalence_flag: EquivalenceFlag

    def to_mapping(self) -> dict[str, object]:
        return {
            "category": self.category.value,
            "validity": self.validity.value,
            "directional_flag": (
                None if self.directional_flag is None else self.directional_flag.value
            ),
            "equivalence_flag": self.equivalence_flag.value,
        }


@dataclass(frozen=True, slots=True)
class CellDecision:
    macro_cell_id: str
    eligibility: CellEligibility
    components: tuple[ComponentDecision, ...]
    primary_decision: CellPrimaryDecision
    vector_equivalence_decision: CellEquivalenceDecision

    def to_mapping(self) -> dict[str, object]:
        return {
            "macro_cell_id": self.macro_cell_id,
            "eligibility": self.eligibility.value,
            "components": [component.to_mapping() for component in self.components],
            "primary_decision": self.primary_decision.value,
            "vector_equivalence_decision": self.vector_equivalence_decision.value,
        }


@dataclass(frozen=True, slots=True)
class PanelDecisionResult:
    required_macro_cell_ids: tuple[str, ...]
    provenance_status: ProvenanceStatus
    cells: tuple[CellDecision, ...]
    primary_decision: PanelPrimaryDecision
    vector_equivalence_decision: PanelEquivalenceDecision
    schema_version: str = PANEL_RESULT_SCHEMA_VERSION

    def to_mapping(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "policy": POLICY.to_mapping(),
            "required_macro_cell_ids": list(self.required_macro_cell_ids),
            "provenance_status": self.provenance_status.value,
            "cells": [cell.to_mapping() for cell in self.cells],
            "primary_decision": self.primary_decision.value,
            "vector_equivalence_decision": self.vector_equivalence_decision.value,
        }

    def to_json(self) -> str:
        return canonical_json(self.to_mapping())


def _component_validity(component: ComponentEvidence) -> ComponentValidity:
    if component.standard_error_decimal < 0:
        return ComponentValidity.INVALID_NEGATIVE_STANDARD_ERROR
    if not (
        component.lower_decimal
        <= component.estimate_decimal
        <= component.upper_decimal
    ):
        return ComponentValidity.INVALID_INTERVAL_ORDER
    if component.standard_error_decimal <= Decimal(NUMERICAL_INTEGRITY_EPSILON):
        return ComponentValidity.INVALID_ZERO_STANDARD_ERROR
    if not (
        component.lower_decimal
        < component.estimate_decimal
        < component.upper_decimal
    ):
        return ComponentValidity.INVALID_INTERVAL_ORDER
    return ComponentValidity.VALID


def _directional_flag(component: ComponentEvidence) -> DirectionalFlag | None:
    threshold = Decimal(PRIMARY_THRESHOLD)
    epsilon = Decimal(NUMERICAL_INTEGRITY_EPSILON)
    if component.category is Category.H:
        if component.lower_decimal > threshold + epsilon:
            return DirectionalFlag.H_UP_PASS
        if abs(component.lower_decimal - threshold) <= epsilon:
            return DirectionalFlag.H_UP_BOUNDARY_NOT_PASS
        return DirectionalFlag.H_UP_NOT_PASS
    if component.category is Category.L:
        if component.upper_decimal < -threshold - epsilon:
            return DirectionalFlag.L_DOWN_PASS
        if abs(component.upper_decimal + threshold) <= epsilon:
            return DirectionalFlag.L_DOWN_BOUNDARY_NOT_PASS
        return DirectionalFlag.L_DOWN_NOT_PASS
    return None


def _equivalence_flag(component: ComponentEvidence) -> EquivalenceFlag:
    margin = Decimal(EQUIVALENCE_MARGINS[component.category.value])
    epsilon = Decimal(NUMERICAL_INTEGRITY_EPSILON)
    if (
        component.lower_decimal > -margin + epsilon
        and component.upper_decimal < margin - epsilon
    ):
        return EquivalenceFlag.PASS
    if (
        abs(component.lower_decimal + margin) <= epsilon
        or abs(component.upper_decimal - margin) <= epsilon
    ):
        return EquivalenceFlag.BOUNDARY_NOT_PASS
    return EquivalenceFlag.NOT_PASS


def _component_decisions(cell: MacroCellEvidence) -> tuple[ComponentDecision, ...]:
    by_category = {component.category: component for component in cell.components}
    decisions: list[ComponentDecision] = []
    for category in Category:
        component = by_category.get(category)
        if component is None:
            decisions.append(
                ComponentDecision(
                    category=category,
                    validity=ComponentValidity.MISSING,
                    directional_flag=None,
                    equivalence_flag=EquivalenceFlag.INFERENCE_INVALID,
                )
            )
            continue
        validity = _component_validity(component)
        decisions.append(
            ComponentDecision(
                category=category,
                validity=validity,
                directional_flag=(
                    _directional_flag(component)
                    if validity is ComponentValidity.VALID
                    else None
                ),
                equivalence_flag=(
                    _equivalence_flag(component)
                    if validity is ComponentValidity.VALID
                    else EquivalenceFlag.INFERENCE_INVALID
                ),
            )
        )
    return tuple(decisions)


def _invalid_cell_decision(
    macro_cell_id: str,
    eligibility: CellEligibility,
    components: tuple[ComponentDecision, ...] = (),
) -> CellDecision:
    if eligibility in {
        CellEligibility.DESIGN_INVALID_PROVENANCE,
        CellEligibility.DESIGN_INVALID_LEDGER,
        CellEligibility.DESIGN_INVALID_ASSIGNMENT,
        CellEligibility.DESIGN_INVALID_TERMINAL_INTEGRITY,
    }:
        primary = CellPrimaryDecision.DESIGN_INVALID
        equivalence = CellEquivalenceDecision.DESIGN_INVALID
    elif eligibility is CellEligibility.SUPPORT_INSUFFICIENT:
        primary = CellPrimaryDecision.SUPPORT_INSUFFICIENT
        equivalence = CellEquivalenceDecision.SUPPORT_INSUFFICIENT
    else:
        primary = CellPrimaryDecision.INFERENCE_INVALID
        equivalence = CellEquivalenceDecision.INFERENCE_INVALID
    return CellDecision(
        macro_cell_id=macro_cell_id,
        eligibility=eligibility,
        components=components,
        primary_decision=primary,
        vector_equivalence_decision=equivalence,
    )


def _evaluate_cell(
    cell: MacroCellEvidence,
    provenance_status: ProvenanceStatus,
) -> CellDecision:
    if provenance_status is not ProvenanceStatus.VALID:
        return _invalid_cell_decision(
            cell.macro_cell_id,
            CellEligibility.DESIGN_INVALID_PROVENANCE,
        )
    if cell.ledger_status is not LedgerStatus.VALID:
        return _invalid_cell_decision(
            cell.macro_cell_id,
            CellEligibility.DESIGN_INVALID_LEDGER,
        )
    if cell.assignment_status is not AssignmentStatus.VALID:
        return _invalid_cell_decision(
            cell.macro_cell_id,
            CellEligibility.DESIGN_INVALID_ASSIGNMENT,
        )
    if cell.has_local_integrity_abort:
        return _invalid_cell_decision(
            cell.macro_cell_id,
            CellEligibility.DESIGN_INVALID_TERMINAL_INTEGRITY,
        )
    if cell.support_status is not SupportStatus.VALID:
        return _invalid_cell_decision(
            cell.macro_cell_id,
            CellEligibility.SUPPORT_INSUFFICIENT,
        )

    component_decisions = _component_decisions(cell)
    hard_invalid = {
        ComponentValidity.MISSING,
        ComponentValidity.INVALID_INTERVAL_ORDER,
        ComponentValidity.INVALID_NEGATIVE_STANDARD_ERROR,
    }
    if any(component.validity in hard_invalid for component in component_decisions):
        return _invalid_cell_decision(
            cell.macro_cell_id,
            CellEligibility.INFERENCE_INVALID_DATA,
            component_decisions,
        )

    by_category = {component.category: component for component in component_decisions}
    h = by_category[Category.H]
    low = by_category[Category.L]
    if (
        h.validity is ComponentValidity.INVALID_ZERO_STANDARD_ERROR
        or low.validity is ComponentValidity.INVALID_ZERO_STANDARD_ERROR
    ):
        primary = CellPrimaryDecision.INFERENCE_INVALID
    elif (
        h.directional_flag is DirectionalFlag.H_UP_PASS
        and low.directional_flag is DirectionalFlag.L_DOWN_PASS
    ):
        primary = CellPrimaryDecision.ESTABLISHED
    elif h.directional_flag is DirectionalFlag.H_UP_BOUNDARY_NOT_PASS or (
        low.directional_flag is DirectionalFlag.L_DOWN_BOUNDARY_NOT_PASS
    ):
        primary = CellPrimaryDecision.BOUNDARY_NOT_ESTABLISHED
    else:
        primary = CellPrimaryDecision.NOT_ESTABLISHED

    if any(
        component.validity is not ComponentValidity.VALID
        for component in component_decisions
    ):
        equivalence = CellEquivalenceDecision.INFERENCE_INVALID
    elif all(
        component.equivalence_flag is EquivalenceFlag.PASS
        for component in component_decisions
    ):
        equivalence = CellEquivalenceDecision.ESTABLISHED
    elif any(
        component.equivalence_flag is EquivalenceFlag.BOUNDARY_NOT_PASS
        for component in component_decisions
    ):
        equivalence = CellEquivalenceDecision.BOUNDARY_NOT_ESTABLISHED
    else:
        equivalence = CellEquivalenceDecision.NOT_ESTABLISHED

    return CellDecision(
        macro_cell_id=cell.macro_cell_id,
        eligibility=CellEligibility.ELIGIBLE,
        components=component_decisions,
        primary_decision=primary,
        vector_equivalence_decision=equivalence,
    )


def evaluate_panel(evidence: PanelEvidence) -> PanelDecisionResult:
    """Evaluate the four-cell panel under the immutable amendment-frozen policy."""

    if not isinstance(evidence, PanelEvidence):
        raise TypeError("evidence must be PanelEvidence")
    supplied = {cell.macro_cell_id: cell for cell in evidence.cells}
    cell_decisions: list[CellDecision] = []
    for cell_id in evidence.required_macro_cell_ids:
        cell = supplied.get(cell_id)
        if cell is None:
            cell_decisions.append(
                _invalid_cell_decision(
                    cell_id,
                    (
                        CellEligibility.DESIGN_INVALID_PROVENANCE
                        if evidence.provenance_status is not ProvenanceStatus.VALID
                        else CellEligibility.SUPPORT_INSUFFICIENT
                    ),
                )
            )
        else:
            cell_decisions.append(_evaluate_cell(cell, evidence.provenance_status))
    decisions = tuple(cell_decisions)

    primary_values = {decision.primary_decision for decision in decisions}
    equivalence_values = {
        decision.vector_equivalence_decision for decision in decisions
    }
    if evidence.provenance_status is not ProvenanceStatus.VALID or (
        CellPrimaryDecision.DESIGN_INVALID in primary_values
    ):
        primary = PanelPrimaryDecision.DESIGN_INVALID
        vector_equivalence = PanelEquivalenceDecision.DESIGN_INVALID
    else:
        if CellPrimaryDecision.SUPPORT_INSUFFICIENT in primary_values:
            primary = PanelPrimaryDecision.SUPPORT_INSUFFICIENT
        elif primary_values == {CellPrimaryDecision.ESTABLISHED}:
            primary = PanelPrimaryDecision.ESTABLISHED
        elif CellPrimaryDecision.INFERENCE_INVALID in primary_values:
            primary = PanelPrimaryDecision.INFERENCE_INVALID
        elif CellPrimaryDecision.BOUNDARY_NOT_ESTABLISHED in primary_values:
            primary = PanelPrimaryDecision.BOUNDARY_NOT_ESTABLISHED
        else:
            primary = PanelPrimaryDecision.NOT_ESTABLISHED

        if CellEquivalenceDecision.SUPPORT_INSUFFICIENT in equivalence_values:
            vector_equivalence = PanelEquivalenceDecision.SUPPORT_INSUFFICIENT
        elif equivalence_values == {CellEquivalenceDecision.ESTABLISHED}:
            vector_equivalence = PanelEquivalenceDecision.ESTABLISHED
        elif CellEquivalenceDecision.INFERENCE_INVALID in equivalence_values:
            vector_equivalence = PanelEquivalenceDecision.INFERENCE_INVALID
        elif CellEquivalenceDecision.BOUNDARY_NOT_ESTABLISHED in equivalence_values:
            vector_equivalence = PanelEquivalenceDecision.BOUNDARY_NOT_ESTABLISHED
        else:
            vector_equivalence = PanelEquivalenceDecision.NOT_ESTABLISHED

    return PanelDecisionResult(
        required_macro_cell_ids=evidence.required_macro_cell_ids,
        provenance_status=evidence.provenance_status,
        cells=decisions,
        primary_decision=primary,
        vector_equivalence_decision=vector_equivalence,
    )


__all__ = [
    "Arm",
    "AssignmentStatus",
    "AssignedSchedule",
    "Category",
    "CellEligibility",
    "CellEquivalenceDecision",
    "CellPrimaryDecision",
    "ClosedSchemaError",
    "ComponentEvidence",
    "ComponentValidity",
    "DecisionAuthorityError",
    "DecisionPolicy",
    "EQUIVALENCE_MARGINS",
    "EquivalenceFlag",
    "FailureSubtype",
    "LedgerStatus",
    "MacroCellEvidence",
    "NUMERICAL_INTEGRITY_EPSILON",
    "NUMERICAL_INTEGRITY_RATIONALE",
    "PANEL_INPUT_SCHEMA_VERSION",
    "PANEL_RESULT_SCHEMA_VERSION",
    "POLICY",
    "PRIMARY_THRESHOLD",
    "PanelDecisionResult",
    "PanelEquivalenceDecision",
    "PanelEvidence",
    "PanelPrimaryDecision",
    "ProvenanceStatus",
    "SupportStatus",
    "TERMINAL_FLOW_POLICY",
    "TERMINAL_FLOW_POLICY_SCHEMA_VERSION",
    "TerminalFlowPolicy",
    "TerminalFlowCount",
    "TerminalSource",
    "canonical_json",
    "evaluate_panel",
]
