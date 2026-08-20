from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import json
from pathlib import Path
import sys
import unittest


AMENDMENT_ROOT = Path(__file__).resolve().parents[1]
if str(AMENDMENT_ROOT) not in sys.path:
    sys.path.insert(0, str(AMENDMENT_ROOT))

from statistical_decision_authority import (  # noqa: E402
    Arm,
    AssignmentStatus,
    AssignedSchedule,
    Category,
    CellEligibility,
    CellEquivalenceDecision,
    CellPrimaryDecision,
    ClosedSchemaError,
    ComponentEvidence,
    ComponentValidity,
    DecisionAuthorityError,
    DecisionPolicy,
    EquivalenceFlag,
    FailureSubtype,
    LedgerStatus,
    MacroCellEvidence,
    NUMERICAL_INTEGRITY_EPSILON,
    NUMERICAL_INTEGRITY_RATIONALE,
    POLICY,
    PanelEquivalenceDecision,
    PanelEvidence,
    PanelPrimaryDecision,
    ProvenanceStatus,
    SupportStatus,
    TERMINAL_FLOW_POLICY,
    TerminalFlowCount,
    TerminalSource,
    evaluate_panel,
)


CELL_IDS = (
    "model-a|tool-budget",
    "model-a|work-score",
    "model-b|tool-budget",
    "model-b|work-score",
)


def _flows() -> tuple[TerminalFlowCount, ...]:
    return (
        TerminalFlowCount(
            TerminalSource.FOLLOWUP_CHOICE,
            FailureSubtype.NONE,
            Category.L,
            Arm.SELF,
            AssignedSchedule.L,
            20,
        ),
        TerminalFlowCount(
            TerminalSource.FOLLOWUP_UNAVAILABLE,
            FailureSubtype.INVALID_RESPONSE,
            Category.U,
            Arm.SELF,
            AssignedSchedule.L,
            2,
        ),
        TerminalFlowCount(
            TerminalSource.FOLLOWUP_CHOICE,
            FailureSubtype.NONE,
            Category.H,
            Arm.SELF,
            AssignedSchedule.H,
            20,
        ),
        TerminalFlowCount(
            TerminalSource.EXECUTION_FAILURE,
            FailureSubtype.TIMEOUT,
            Category.U,
            Arm.SELF,
            AssignedSchedule.H,
            2,
        ),
        TerminalFlowCount(
            TerminalSource.FOLLOWUP_CHOICE,
            FailureSubtype.NONE,
            Category.L,
            Arm.YOKE,
            AssignedSchedule.L,
            20,
        ),
        TerminalFlowCount(
            TerminalSource.FOLLOWUP_UNAVAILABLE,
            FailureSubtype.INVALID_RESPONSE,
            Category.U,
            Arm.YOKE,
            AssignedSchedule.L,
            2,
        ),
        TerminalFlowCount(
            TerminalSource.FOLLOWUP_CHOICE,
            FailureSubtype.NONE,
            Category.H,
            Arm.YOKE,
            AssignedSchedule.H,
            20,
        ),
        TerminalFlowCount(
            TerminalSource.EXECUTION_FAILURE,
            FailureSubtype.TIMEOUT,
            Category.U,
            Arm.YOKE,
            AssignedSchedule.H,
            2,
        ),
    )


def _positive_components(*, u_standard_error: str = "0.01") -> tuple[ComponentEvidence, ...]:
    return (
        ComponentEvidence(Category.L, "-0.1", "-0.15", "-0.06", "0.01"),
        ComponentEvidence(Category.H, "0.1", "0.06", "0.15", "0.01"),
        ComponentEvidence(Category.U, "0", "-0.01", "0.01", u_standard_error),
    )


def _equivalent_components() -> tuple[ComponentEvidence, ...]:
    return (
        ComponentEvidence(Category.L, "0", "-0.04", "0.04", "0.01"),
        ComponentEvidence(Category.H, "0", "-0.04", "0.04", "0.01"),
        ComponentEvidence(Category.U, "0", "-0.01", "0.01", "0.01"),
    )


def _replace_component(
    components: tuple[ComponentEvidence, ...],
    category: Category,
    **changes: str,
) -> tuple[ComponentEvidence, ...]:
    return tuple(
        replace(component, **changes) if component.category is category else component
        for component in components
    )


def _cell(
    cell_id: str,
    *,
    components: tuple[ComponentEvidence, ...] | None = None,
    terminal_flows: tuple[TerminalFlowCount, ...] | None = None,
    ledger_status: LedgerStatus = LedgerStatus.VALID,
    assignment_status: AssignmentStatus = AssignmentStatus.VALID,
    support_status: SupportStatus = SupportStatus.VALID,
) -> MacroCellEvidence:
    flows = _flows() if terminal_flows is None else terminal_flows
    return MacroCellEvidence(
        macro_cell_id=cell_id,
        ledger_status=ledger_status,
        assignment_status=assignment_status,
        support_status=support_status,
        terminal_row_count=sum(flow.count for flow in flows),
        terminal_flows=flows,
        components=_positive_components() if components is None else components,
    )


def _panel(
    *,
    cells: tuple[MacroCellEvidence, ...] | None = None,
    components: tuple[ComponentEvidence, ...] | None = None,
    provenance_status: ProvenanceStatus = ProvenanceStatus.VALID,
) -> PanelEvidence:
    supplied = (
        tuple(_cell(cell_id, components=components) for cell_id in CELL_IDS)
        if cells is None
        else cells
    )
    return PanelEvidence(
        required_macro_cell_ids=CELL_IDS,
        provenance_status=provenance_status,
        cells=supplied,
    )


class PolicyAndSchemaTests(unittest.TestCase):
    def test_policy_freezes_exact_decimal_scientific_rules(self) -> None:
        mapping = POLICY.to_mapping()
        self.assertEqual(mapping["primary_threshold"], "0.05")
        self.assertFalse(mapping["primary_has_u_guard"])
        self.assertTrue(mapping["primary_requires_separate_u_reporting"])
        self.assertEqual(
            mapping["equivalence_margins"],
            {"L": "0.05", "H": "0.05", "U": "0.02"},
        )
        self.assertEqual(
            mapping["vector_equivalence_role"],
            "secondary_non_authorizing",
        )
        self.assertFalse(
            mapping["vector_equivalence_can_create_rescue_or_veto_primary"]
        )
        self.assertEqual(
            mapping["standard_error_rule"],
            "finite_standard_error_at_or_below_epsilon_is_inference_invalid",
        )
        self.assertEqual(
            mapping["positive_standard_error_rule"],
            "every_finite_standard_error_strictly_above_epsilon_is_eligible",
        )
        self.assertEqual(
            mapping["numerical_integrity_epsilon"],
            NUMERICAL_INTEGRITY_EPSILON,
        )
        self.assertTrue(
            mapping["effect_and_margin_boundaries_use_epsilon_guard_bands"]
        )
        self.assertFalse(mapping["epsilon_is_substantive_effect_increment"])
        self.assertTrue(mapping["grid_or_sample_change_requires_epsilon_reproof"])
        self.assertTrue(
            mapping[
                "complete_component_estimates_must_sum_to_zero_within_epsilon"
            ]
        )
        self.assertTrue(
            mapping[
                "positive_standard_error_requires_strict_estimate_within_bounds"
            ]
        )
        self.assertFalse(mapping["component_bounds_recomputed_by_this_authority"])
        self.assertFalse(
            mapping["degrees_of_freedom_recomputed_by_this_authority"]
        )
        self.assertTrue(mapping["upstream_frozen_analyzer_provenance_required"])
        self.assertEqual(
            mapping["numerical_integrity_rationale"],
            NUMERICAL_INTEGRITY_RATIONALE,
        )
        self.assertEqual(
            mapping["mandatory_reporting_fields"],
            [
                "U_simultaneous_interval_by_macro_cell",
                "terminal_source_subtype_counts_by_arm_assigned_schedule_macro_cell",
            ],
        )
        with self.assertRaises(DecisionAuthorityError):
            DecisionPolicy(primary_threshold="0.06")

        terminal_policy = {
            "schema_version": "binding-terminal-flow-policy-v1",
            "source_rules": [
                {
                    "source": "followup_choice",
                    "allowed_subtypes": ["none"],
                    "allowed_dispositions": ["L", "H"],
                },
                {
                    "source": "followup_unavailable",
                    "allowed_subtypes": [
                        "missing_response",
                        "empty_response",
                        "explicit_refusal",
                        "invalid_response",
                    ],
                    "allowed_dispositions": ["U"],
                },
                {
                    "source": "execution_failure",
                    "allowed_subtypes": [
                        "invalid_response",
                        "transport_error",
                        "timeout",
                        "provider_error",
                        "quota_exhausted",
                        "tool_error",
                        "tool_limit_exceeded",
                    ],
                    "allowed_dispositions": ["U"],
                },
                {
                    "source": "followup_failure",
                    "allowed_subtypes": [
                        "transport_error",
                        "timeout",
                        "provider_error",
                        "quota_exhausted",
                    ],
                    "allowed_dispositions": ["U"],
                },
                {
                    "source": "local_protocol_abort",
                    "allowed_subtypes": [
                        "assignment_binding_mismatch",
                        "schedule_integrity_mismatch",
                        "role_leak_detected",
                        "runtime_contract_violation",
                        "controller_abort",
                        "unknown",
                    ],
                    "allowed_dispositions": ["U"],
                },
            ],
            "local_protocol_abort_integrity": {
                "retains_composite_u_ledger_row": True,
                "marks_integrity_failure": True,
                "invalidates_affected_macro_cell_headline": True,
                "invalidates_all_cell_headline": True,
            },
            "valid_cell_decomposition": {
                "requires_valid_ledger_assignment_and_support": True,
                "terminal_rows_per_complete_block": 8,
                "arm_order": ["self", "yoke"],
                "assigned_schedule_order": ["L", "H"],
                "rows_per_arm_assigned_schedule_per_complete_block": 2,
            },
        }
        self.assertEqual(TERMINAL_FLOW_POLICY.to_mapping(), terminal_policy)
        self.assertEqual(
            json.loads(json.dumps(TERMINAL_FLOW_POLICY.to_mapping())),
            terminal_policy,
        )
        with self.assertRaises(DecisionAuthorityError):
            replace(TERMINAL_FLOW_POLICY, schema_version="forged")

    def test_panel_input_roundtrips_through_closed_json_mapping(self) -> None:
        panel = _panel()
        decoded = json.loads(panel.to_json())
        self.assertEqual(PanelEvidence.from_mapping(decoded), panel)
        result = evaluate_panel(panel)
        self.assertEqual(json.loads(result.to_json()), result.to_mapping())

    def test_closed_loaders_reject_missing_extra_and_unknown_enum_fields(self) -> None:
        mapping = _panel().to_mapping()
        missing = dict(mapping)
        missing.pop("provenance_status")
        with self.assertRaises(ClosedSchemaError):
            PanelEvidence.from_mapping(missing)
        with self.assertRaises(ClosedSchemaError):
            PanelEvidence.from_mapping({**mapping, "extra": True})
        unknown = json.loads(json.dumps(mapping))
        unknown["provenance_status"] = "PROVENANCE_MAYBE"
        with self.assertRaises(ClosedSchemaError):
            PanelEvidence.from_mapping(unknown)
        component = _positive_components()[0].to_mapping()
        with self.assertRaises(ClosedSchemaError):
            ComponentEvidence.from_mapping({**component, "raw_data": "forbidden"})

    def test_panel_shape_order_and_immutability_are_fail_closed(self) -> None:
        panel = _panel()
        with self.assertRaises(FrozenInstanceError):
            panel.provenance_status = ProvenanceStatus.INVALID_PHASE  # type: ignore[misc]
        with self.assertRaises(DecisionAuthorityError):
            PanelEvidence(CELL_IDS[:-1], ProvenanceStatus.VALID, panel.cells[:-1])
        with self.assertRaises(DecisionAuthorityError):
            PanelEvidence(tuple(reversed(CELL_IDS)), ProvenanceStatus.VALID, panel.cells)
        with self.assertRaises(DecisionAuthorityError):
            PanelEvidence(CELL_IDS, ProvenanceStatus.VALID, tuple(reversed(panel.cells)))
        outside = _cell("model-z|outside")
        with self.assertRaises(DecisionAuthorityError):
            PanelEvidence(CELL_IDS, ProvenanceStatus.VALID, (outside,))


class TerminalTaxonomyTests(unittest.TestCase):
    def test_all_declared_ordinary_failure_subtypes_require_composite_u(self) -> None:
        ordinary = {
            TerminalSource.FOLLOWUP_UNAVAILABLE: (
                FailureSubtype.MISSING_RESPONSE,
                FailureSubtype.EMPTY_RESPONSE,
                FailureSubtype.EXPLICIT_REFUSAL,
                FailureSubtype.INVALID_RESPONSE,
            ),
            TerminalSource.EXECUTION_FAILURE: (
                FailureSubtype.INVALID_RESPONSE,
                FailureSubtype.TRANSPORT_ERROR,
                FailureSubtype.TIMEOUT,
                FailureSubtype.PROVIDER_ERROR,
                FailureSubtype.QUOTA_EXHAUSTED,
                FailureSubtype.TOOL_ERROR,
                FailureSubtype.TOOL_LIMIT_EXCEEDED,
            ),
            TerminalSource.FOLLOWUP_FAILURE: (
                FailureSubtype.TRANSPORT_ERROR,
                FailureSubtype.TIMEOUT,
                FailureSubtype.PROVIDER_ERROR,
                FailureSubtype.QUOTA_EXHAUSTED,
            ),
        }
        for source, subtypes in ordinary.items():
            for subtype in subtypes:
                with self.subTest(source=source, subtype=subtype):
                    flow = TerminalFlowCount(
                        source,
                        subtype,
                        Category.U,
                        Arm.SELF,
                        AssignedSchedule.L,
                        1,
                    )
                    self.assertEqual(
                        TerminalFlowCount.from_mapping(flow.to_mapping()),
                        flow,
                    )

    def test_valid_flow_decomposition_covers_arm_and_assigned_schedule(self) -> None:
        flows = _flows()
        totals: dict[tuple[Arm, AssignedSchedule], int] = {}
        for flow in flows:
            key = (flow.arm, flow.assigned_schedule)
            totals[key] = totals.get(key, 0) + flow.count
            self.assertEqual(TerminalFlowCount.from_mapping(flow.to_mapping()), flow)
        self.assertEqual(
            totals,
            {
                (Arm.SELF, AssignedSchedule.L): 22,
                (Arm.SELF, AssignedSchedule.H): 22,
                (Arm.YOKE, AssignedSchedule.L): 22,
                (Arm.YOKE, AssignedSchedule.H): 22,
            },
        )
        cell = _cell(CELL_IDS[0], terminal_flows=flows)
        self.assertEqual(cell.terminal_row_count, 88)

    def test_flow_loader_rejects_missing_or_unknown_arm_and_schedule(self) -> None:
        mapping = _flows()[0].to_mapping()
        for missing_field in ("arm", "assigned_schedule"):
            with self.subTest(missing=missing_field):
                malformed = dict(mapping)
                malformed.pop(missing_field)
                with self.assertRaises(ClosedSchemaError):
                    TerminalFlowCount.from_mapping(malformed)
        for field, value in (("arm", "other"), ("assigned_schedule", "U")):
            with self.subTest(field=field, value=value):
                with self.assertRaises(ClosedSchemaError):
                    TerminalFlowCount.from_mapping({**mapping, field: value})

    def test_terminal_taxonomy_rejects_wrong_subtype_or_non_u_failure(self) -> None:
        with self.assertRaises(DecisionAuthorityError):
            TerminalFlowCount(
                TerminalSource.EXECUTION_FAILURE,
                FailureSubtype.NONE,
                Category.U,
                Arm.SELF,
                AssignedSchedule.L,
                1,
            )
        with self.assertRaises(DecisionAuthorityError):
            TerminalFlowCount(
                TerminalSource.EXECUTION_FAILURE,
                FailureSubtype.TIMEOUT,
                Category.H,
                Arm.SELF,
                AssignedSchedule.L,
                1,
            )
        with self.assertRaises(DecisionAuthorityError):
            TerminalFlowCount(
                TerminalSource.FOLLOWUP_CHOICE,
                FailureSubtype.NONE,
                Category.U,
                Arm.SELF,
                AssignedSchedule.L,
                1,
            )

    def test_local_abort_row_is_retained_as_u_and_invalidates_panel(self) -> None:
        flows = (
            *_flows()[:-1],
            replace(_flows()[-1], count=1),
            TerminalFlowCount(
                TerminalSource.LOCAL_PROTOCOL_ABORT,
                FailureSubtype.RUNTIME_CONTRACT_VIOLATION,
                Category.U,
                Arm.YOKE,
                AssignedSchedule.H,
                1,
            ),
        )
        affected = _cell(CELL_IDS[0], terminal_flows=flows)
        self.assertEqual(affected.terminal_row_count, 88)
        self.assertTrue(affected.has_local_integrity_abort)
        cells = (affected, *tuple(_cell(cell_id) for cell_id in CELL_IDS[1:]))
        result = evaluate_panel(_panel(cells=cells))
        self.assertEqual(
            result.cells[0].eligibility,
            CellEligibility.DESIGN_INVALID_TERMINAL_INTEGRITY,
        )
        self.assertEqual(result.primary_decision, PanelPrimaryDecision.DESIGN_INVALID)
        self.assertEqual(
            result.vector_equivalence_decision,
            PanelEquivalenceDecision.DESIGN_INVALID,
        )

    def test_valid_ledger_requires_exact_count_and_canonical_unique_flows(self) -> None:
        flows = _flows()
        with self.assertRaises(DecisionAuthorityError):
            MacroCellEvidence(
                CELL_IDS[0],
                LedgerStatus.VALID,
                AssignmentStatus.VALID,
                SupportStatus.VALID,
                87,
                (replace(flows[0], count=19), *flows[1:]),
                _positive_components(),
            )
        with self.assertRaisesRegex(DecisionAuthorityError, "exact terminal-row balance"):
            MacroCellEvidence(
                CELL_IDS[0],
                LedgerStatus.VALID,
                AssignmentStatus.VALID,
                SupportStatus.VALID,
                88,
                (
                    replace(flows[0], count=21),
                    flows[1],
                    replace(flows[2], count=19),
                    *flows[3:],
                ),
                _positive_components(),
            )
        with self.assertRaises(DecisionAuthorityError):
            MacroCellEvidence(
                CELL_IDS[0],
                LedgerStatus.VALID,
                AssignmentStatus.VALID,
                SupportStatus.VALID,
                87,
                flows,
                _positive_components(),
            )
        with self.assertRaises(DecisionAuthorityError):
            MacroCellEvidence(
                CELL_IDS[0],
                LedgerStatus.VALID,
                AssignmentStatus.VALID,
                SupportStatus.VALID,
                88,
                tuple(reversed(flows)),
                _positive_components(),
            )
        duplicate = (flows[0], flows[0], *flows[2:])
        with self.assertRaises(DecisionAuthorityError):
            MacroCellEvidence(
                CELL_IDS[0],
                LedgerStatus.VALID,
                AssignmentStatus.VALID,
                SupportStatus.VALID,
                sum(flow.count for flow in duplicate),
                duplicate,
                _positive_components(),
            )


class ComponentDecisionTests(unittest.TestCase):
    def test_primary_is_strict_paired_h_up_l_down_with_no_u_guard(self) -> None:
        components = _replace_component(
            _positive_components(),
            Category.U,
            estimate="0",
            lower_bound="-0.6",
            upper_bound="0.6",
        )
        result = evaluate_panel(_panel(components=components))
        self.assertEqual(result.primary_decision, PanelPrimaryDecision.ESTABLISHED)
        self.assertEqual(
            result.vector_equivalence_decision,
            PanelEquivalenceDecision.NOT_ESTABLISHED,
        )
        self.assertFalse(POLICY.primary_has_u_guard)

    def test_exact_h_or_l_primary_threshold_equality_is_boundary_not_pass(self) -> None:
        cases = (
            (Category.H, {"lower_bound": "0.05"}),
            (Category.L, {"upper_bound": "-0.05"}),
        )
        for category, changes in cases:
            with self.subTest(category=category):
                components = _replace_component(
                    _positive_components(), category, **changes
                )
                result = evaluate_panel(_panel(components=components))
                self.assertEqual(
                    result.primary_decision,
                    PanelPrimaryDecision.BOUNDARY_NOT_ESTABLISHED,
                )

        guard_edges = (
            (Category.H, {"lower_bound": "0.050000000001"}),
            (Category.L, {"upper_bound": "-0.050000000001"}),
        )
        for category, changes in guard_edges:
            with self.subTest(category=category, guard_edge=True):
                result = evaluate_panel(
                    _panel(
                        components=_replace_component(
                            _positive_components(), category, **changes
                        )
                    )
                )
                self.assertEqual(
                    result.primary_decision,
                    PanelPrimaryDecision.BOUNDARY_NOT_ESTABLISHED,
                )

        beyond_edges = (
            (Category.H, {"lower_bound": "0.050000000001000000000001"}),
            (Category.L, {"upper_bound": "-0.050000000001000000000001"}),
        )
        for category, changes in beyond_edges:
            with self.subTest(category=category, beyond_guard=True):
                result = evaluate_panel(
                    _panel(
                        components=_replace_component(
                            _positive_components(), category, **changes
                        )
                    )
                )
                self.assertEqual(result.primary_decision, PanelPrimaryDecision.ESTABLISHED)

    def test_full_vector_equivalence_requires_all_three_strict_margins(self) -> None:
        result = evaluate_panel(_panel(components=_equivalent_components()))
        self.assertEqual(
            result.vector_equivalence_decision,
            PanelEquivalenceDecision.ESTABLISHED,
        )
        self.assertEqual(result.primary_decision, PanelPrimaryDecision.NOT_ESTABLISHED)

    def test_exact_l_h_or_u_equivalence_margin_is_boundary_not_pass(self) -> None:
        cases = (
            (Category.L, {"lower_bound": "-0.05"}),
            (Category.L, {"upper_bound": "0.05"}),
            (Category.H, {"lower_bound": "-0.05"}),
            (Category.H, {"upper_bound": "0.05"}),
            (Category.U, {"lower_bound": "-0.02"}),
            (Category.U, {"upper_bound": "0.02"}),
        )
        for category, changes in cases:
            with self.subTest(category=category, changes=changes):
                components = _replace_component(
                    _equivalent_components(), category, **changes
                )
                result = evaluate_panel(_panel(components=components))
                self.assertEqual(
                    result.vector_equivalence_decision,
                    PanelEquivalenceDecision.BOUNDARY_NOT_ESTABLISHED,
                )

        guard_edges = (
            (Category.L, {"lower_bound": "-0.049999999999"}),
            (Category.H, {"upper_bound": "0.049999999999"}),
            (Category.U, {"lower_bound": "-0.019999999999"}),
        )
        for category, changes in guard_edges:
            with self.subTest(category=category, guard_edge=True):
                result = evaluate_panel(
                    _panel(
                        components=_replace_component(
                            _equivalent_components(), category, **changes
                        )
                    )
                )
                self.assertEqual(
                    result.vector_equivalence_decision,
                    PanelEquivalenceDecision.BOUNDARY_NOT_ESTABLISHED,
                )

    def test_exact_zero_h_or_l_standard_error_blocks_primary(self) -> None:
        for category in (Category.H, Category.L):
            with self.subTest(category=category):
                components = _replace_component(
                    _positive_components(), category, standard_error="0"
                )
                result = evaluate_panel(_panel(components=components))
                self.assertEqual(
                    result.primary_decision,
                    PanelPrimaryDecision.INFERENCE_INVALID,
                )

    def test_exact_zero_u_standard_error_does_not_block_primary(self) -> None:
        result = evaluate_panel(_panel(components=_positive_components(u_standard_error="0")))
        self.assertEqual(result.primary_decision, PanelPrimaryDecision.ESTABLISHED)
        self.assertEqual(
            result.vector_equivalence_decision,
            PanelEquivalenceDecision.INFERENCE_INVALID,
        )
        u = result.cells[0].components[2]
        self.assertEqual(u.validity, ComponentValidity.INVALID_ZERO_STANDARD_ERROR)
        self.assertEqual(u.equivalence_flag, EquivalenceFlag.INFERENCE_INVALID)

    def test_standard_error_epsilon_edge_and_just_above_are_exact(self) -> None:
        invalid_values = ("0.000000000001", "0.0000000000001")
        for standard_error in invalid_values:
            with self.subTest(standard_error=standard_error):
                components = tuple(
                    replace(component, standard_error=standard_error)
                    for component in _positive_components()
                )
                result = evaluate_panel(_panel(components=components))
                self.assertEqual(
                    result.primary_decision,
                    PanelPrimaryDecision.INFERENCE_INVALID,
                )
                self.assertTrue(
                    all(
                        component.validity
                        is ComponentValidity.INVALID_ZERO_STANDARD_ERROR
                        for component in result.cells[0].components
                    )
                )

        above = "0.000000000001000000000001"
        components = tuple(
            replace(component, standard_error=above)
            for component in _positive_components()
        )
        result = evaluate_panel(_panel(components=components))
        self.assertEqual(result.primary_decision, PanelPrimaryDecision.ESTABLISHED)
        self.assertTrue(
            all(
                component.validity is ComponentValidity.VALID
                for component in result.cells[0].components
            )
        )

    def test_negative_standard_error_and_malformed_interval_fail_closed(self) -> None:
        negative = _replace_component(
            _positive_components(), Category.U, standard_error="-0.01"
        )
        result = evaluate_panel(_panel(components=negative))
        self.assertEqual(result.primary_decision, PanelPrimaryDecision.INFERENCE_INVALID)
        self.assertEqual(
            result.cells[0].components[2].validity,
            ComponentValidity.INVALID_NEGATIVE_STANDARD_ERROR,
        )

        malformed = _replace_component(
            _positive_components(),
            Category.U,
            lower_bound="0.1",
            upper_bound="-0.1",
        )
        result = evaluate_panel(_panel(components=malformed))
        self.assertEqual(result.primary_decision, PanelPrimaryDecision.INFERENCE_INVALID)
        self.assertEqual(
            result.cells[0].components[2].validity,
            ComponentValidity.INVALID_INTERVAL_ORDER,
        )

        strict_envelope_cases = (
            (Category.L, {"upper_bound": "-0.1"}),
            (Category.H, {"lower_bound": "0.1"}),
            (Category.U, {"lower_bound": "0", "upper_bound": "0"}),
        )
        for category, changes in strict_envelope_cases:
            with self.subTest(category=category, changes=changes):
                collapsed = _replace_component(
                    _positive_components(), category, **changes
                )
                collapsed_result = evaluate_panel(_panel(components=collapsed))
                by_category = {
                    component.category: component
                    for component in collapsed_result.cells[0].components
                }
                self.assertEqual(
                    by_category[category].validity,
                    ComponentValidity.INVALID_INTERVAL_ORDER,
                )
                self.assertEqual(
                    collapsed_result.primary_decision,
                    PanelPrimaryDecision.INFERENCE_INVALID,
                )

        zero_se_collapsed = _replace_component(
            _positive_components(),
            Category.U,
            lower_bound="0",
            upper_bound="0",
            standard_error=NUMERICAL_INTEGRITY_EPSILON,
        )
        zero_se_result = evaluate_panel(_panel(components=zero_se_collapsed))
        self.assertEqual(
            zero_se_result.cells[0].components[2].validity,
            ComponentValidity.INVALID_ZERO_STANDARD_ERROR,
        )

        malformed_zero_se = _replace_component(
            _positive_components(),
            Category.U,
            lower_bound="0.1",
            upper_bound="-0.1",
            standard_error=NUMERICAL_INTEGRITY_EPSILON,
        )
        malformed_zero_se_result = evaluate_panel(
            _panel(components=malformed_zero_se)
        )
        self.assertEqual(
            malformed_zero_se_result.cells[0].components[2].validity,
            ComponentValidity.INVALID_INTERVAL_ORDER,
        )
        self.assertEqual(
            malformed_zero_se_result.primary_decision,
            PanelPrimaryDecision.INFERENCE_INVALID,
        )
        self.assertEqual(
            malformed_zero_se_result.vector_equivalence_decision,
            PanelEquivalenceDecision.INFERENCE_INVALID,
        )

    def test_nonfinite_exponent_noncanonical_and_out_of_range_values_are_rejected(self) -> None:
        for bad in ("NaN", "Infinity", "1e-13", "+0.1", "0.010"):
            with self.subTest(bad=bad):
                with self.assertRaises(ClosedSchemaError):
                    ComponentEvidence(Category.U, "0", "-0.01", "0.01", bad)
        with self.assertRaises(DecisionAuthorityError):
            ComponentEvidence(Category.H, "1.1", "0", "1", "0.01")
        within_tolerance = _replace_component(
            _positive_components(),
            Category.U,
            estimate="0.000000000001",
        )
        self.assertIsInstance(
            _cell(CELL_IDS[0], components=within_tolerance),
            MacroCellEvidence,
        )
        outside_tolerance = _replace_component(
            _positive_components(),
            Category.U,
            estimate="0.000000000001000000000001",
        )
        with self.assertRaisesRegex(DecisionAuthorityError, "must sum to zero"):
            _cell(CELL_IDS[0], components=outside_tolerance)


class PanelPrecedenceTests(unittest.TestCase):
    def test_all_four_required_cells_must_establish_primary(self) -> None:
        result = evaluate_panel(_panel())
        self.assertEqual(len(result.cells), 4)
        self.assertTrue(
            all(
                cell.primary_decision is CellPrimaryDecision.ESTABLISHED
                for cell in result.cells
            )
        )
        self.assertEqual(result.primary_decision, PanelPrimaryDecision.ESTABLISHED)

    def test_one_nonpassing_cell_prevents_all_cell_primary(self) -> None:
        nonpassing = _replace_component(
            _positive_components(), Category.H, lower_bound="0.04"
        )
        cells = (
            _cell(CELL_IDS[0], components=nonpassing),
            *tuple(_cell(cell_id) for cell_id in CELL_IDS[1:]),
        )
        result = evaluate_panel(_panel(cells=cells))
        self.assertEqual(
            result.cells[0].primary_decision,
            CellPrimaryDecision.NOT_ESTABLISHED,
        )
        self.assertEqual(result.primary_decision, PanelPrimaryDecision.NOT_ESTABLISHED)

    def test_missing_or_unsupported_required_cell_is_support_insufficient(self) -> None:
        missing = _panel(cells=tuple(_cell(cell_id) for cell_id in CELL_IDS[:-1]))
        result = evaluate_panel(missing)
        self.assertEqual(result.primary_decision, PanelPrimaryDecision.SUPPORT_INSUFFICIENT)
        self.assertEqual(
            result.cells[-1].eligibility,
            CellEligibility.SUPPORT_INSUFFICIENT,
        )

        cells = (
            _cell(CELL_IDS[0], support_status=SupportStatus.INSUFFICIENT_FINE_STRATUM),
            *tuple(_cell(cell_id) for cell_id in CELL_IDS[1:]),
        )
        result = evaluate_panel(_panel(cells=cells))
        self.assertEqual(result.primary_decision, PanelPrimaryDecision.SUPPORT_INSUFFICIENT)
        self.assertEqual(
            result.vector_equivalence_decision,
            PanelEquivalenceDecision.SUPPORT_INSUFFICIENT,
        )

    def test_ledger_assignment_and_provenance_failures_precede_statistics(self) -> None:
        cases = (
            (
                "ledger",
                _cell(
                    CELL_IDS[0],
                    ledger_status=LedgerStatus.INVALID_MISSING_TERMINAL,
                ),
                ProvenanceStatus.VALID,
                CellEligibility.DESIGN_INVALID_LEDGER,
            ),
            (
                "assignment",
                _cell(
                    CELL_IDS[0],
                    assignment_status=AssignmentStatus.INVALID_MEMBER,
                ),
                ProvenanceStatus.VALID,
                CellEligibility.DESIGN_INVALID_ASSIGNMENT,
            ),
            (
                "provenance",
                _cell(CELL_IDS[0]),
                ProvenanceStatus.INVALID_BINDING,
                CellEligibility.DESIGN_INVALID_PROVENANCE,
            ),
        )
        for label, first, provenance, eligibility in cases:
            with self.subTest(label=label):
                cells = (first, *tuple(_cell(cell_id) for cell_id in CELL_IDS[1:]))
                result = evaluate_panel(
                    _panel(cells=cells, provenance_status=provenance)
                )
                self.assertEqual(result.cells[0].eligibility, eligibility)
                self.assertEqual(
                    result.primary_decision,
                    PanelPrimaryDecision.DESIGN_INVALID,
                )

    def test_missing_component_is_inference_invalid_not_silently_imputed(self) -> None:
        incomplete = _positive_components()[:2]
        result = evaluate_panel(_panel(components=incomplete))
        self.assertEqual(result.primary_decision, PanelPrimaryDecision.INFERENCE_INVALID)
        self.assertEqual(
            result.vector_equivalence_decision,
            PanelEquivalenceDecision.INFERENCE_INVALID,
        )
        self.assertEqual(
            result.cells[0].components[2].validity,
            ComponentValidity.MISSING,
        )


if __name__ == "__main__":
    unittest.main()
