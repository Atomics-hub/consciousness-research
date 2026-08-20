"""Tests for the redesigned identified observable-outcome analysis."""

from dataclasses import replace
import json
import unittest

from zero_call.binding_test.estimands import (
    CATEGORIES,
    BinaryBoundsResult,
    CategoryContrastResult,
    ConfidenceInterval,
    Observation,
)
from zero_call.binding_test.redesign_estimands import (
    INFERENCE_ROLE,
    ClaimScope,
    ModelTargetStratum,
    analyze_redesigned_outcomes,
    decide_observable_probability_vector,
    decide_observed_disposition_reallocation,
    decide_secondary_binary_sensitivity,
    observed_arm_probabilities,
    observed_model_target_strata,
)


def _scope(
    *strata: tuple[str, str],
) -> ClaimScope:
    declared = strata or (("model", "target"),)
    return ClaimScope(
        population=(
            "eligible randomized sessions in the frozen model x target x item "
            "panel"
        ),
        claim_scope=(
            "assignment effect on the observed follow-up L/H/U distribution "
            "within that panel"
        ),
        generalization_limit=(
            "no claim about untested models, targets, latent choices, or mechanism"
        ),
        declared_strata=tuple(
            ModelTargetStratum(model, target) for model, target in declared
        ),
    )


def _category_result(
    contrasts: dict[str, float],
    *,
    radius: float,
) -> CategoryContrastResult:
    intervals = {
        category: ConfidenceInterval(
            estimate=contrasts[category],
            lower=max(-1.0, contrasts[category] - radius),
            upper=min(1.0, contrasts[category] + radius),
        )
        for category in CATEGORIES
    }
    return CategoryContrastResult(
        contrasts=dict(contrasts),
        intervals=intervals,
        simultaneous_critical_radius=radius,
        alpha=0.05,
        bootstrap_replicates=10,
        seed=7,
        n_blocks=4,
        n_by_arm={"self": 4, "yoke": 4},
    )


def _equal_distribution_with_five_percent_u() -> tuple[Observation, ...]:
    rows: list[Observation] = []
    # Every block has identical arm distributions.  Bootstrap resampling then
    # has exactly zero radius.  Decimal arithmetic makes the binary endpoints
    # approximately +/- .05, exercising conservative boundary handling.
    categories = ("H",) * 9 + ("L",) * 10 + ("U",)
    for block_index in range(4):
        for arm in ("self", "yoke"):
            rows.extend(
                Observation(f"b{block_index}", arm, category)
                for category in categories
            )
    return tuple(rows)


class RedesignedEstimandTests(unittest.TestCase):
    def test_scope_is_explicit_structured_and_nonempty(self) -> None:
        scope = _scope()
        self.assertIn("eligible randomized", scope.population)
        self.assertIn("observed follow-up", scope.claim_scope)
        self.assertEqual(
            scope.declared_strata,
            (ModelTargetStratum("model", "target"),),
        )
        with self.assertRaises(ValueError):
            ClaimScope("", "claim", "limit", scope.declared_strata)
        with self.assertRaises(ValueError):
            ClaimScope("population", " ", "limit", scope.declared_strata)
        with self.assertRaises(ValueError):
            ClaimScope("population", "claim", "limit", ())
        with self.assertRaises(ValueError):
            ClaimScope(
                "population",
                "claim",
                "limit",
                scope.declared_strata + scope.declared_strata,
            )
        json.dumps(scope.to_dict(), allow_nan=False)

    def test_arm_probabilities_and_observed_strata_are_explicit(self) -> None:
        rows = (
            Observation("b1", "self", "H", "m2", "t"),
            Observation("b1", "self", "U", "m2", "t"),
            Observation("b1", "yoke", "L", "m2", "t"),
            Observation("b1", "yoke", "U", "m2", "t"),
            Observation("b2", "self", "H", "m1", "t"),
            Observation("b2", "yoke", "L", "m1", "t"),
        )
        probabilities = observed_arm_probabilities(rows)
        self.assertEqual(set(probabilities), {"self", "yoke"})
        self.assertEqual(set(probabilities["self"]), set(CATEGORIES))
        self.assertAlmostEqual(sum(probabilities["self"].values()), 1.0)
        self.assertAlmostEqual(sum(probabilities["yoke"].values()), 1.0)
        self.assertEqual(
            observed_model_target_strata(rows),
            (
                ModelTargetStratum("m1", "t"),
                ModelTargetStratum("m2", "t"),
            ),
        )

    def test_vector_equivalence_and_change_are_simultaneous_and_provisional(self) -> None:
        margins = {"L": 0.05, "H": 0.05, "U": 0.02}
        equivalent = _category_result(
            {"L": 0.0, "H": 0.0, "U": 0.0}, radius=0.01
        )
        changed = _category_result(
            {"L": -0.07, "H": 0.07, "U": 0.0}, radius=0.01
        )
        equivalent_decision = decide_observable_probability_vector(
            equivalent, margins=margins
        )
        changed_decision = decide_observable_probability_vector(
            changed, margins=margins
        )
        self.assertEqual(
            equivalent_decision.status, "provisional_equivalent"
        )
        self.assertEqual(equivalent_decision.equivalent_components, CATEGORIES)
        self.assertEqual(equivalent_decision.inference_role, INFERENCE_ROLE)
        self.assertTrue(equivalent_decision.simultaneous)
        self.assertEqual(changed_decision.status, "provisional_changed")
        self.assertEqual(changed_decision.changed_components, ("L", "H"))
        self.assertEqual(changed_decision.components["L"].direction, "decrease")
        self.assertEqual(changed_decision.components["H"].direction, "increase")
        json.dumps(changed_decision.to_dict(), allow_nan=False)

    def test_exact_vector_boundaries_are_provisionally_indeterminate(self) -> None:
        boundary = _category_result(
            {"L": -0.05, "H": 0.05, "U": 0.0}, radius=0.0
        )
        decision = decide_observable_probability_vector(
            boundary, margins={"L": 0.05, "H": 0.05, "U": 0.02}
        )
        self.assertEqual(decision.status, "provisional_indeterminate")
        self.assertEqual(decision.indeterminate_components, ("L", "H"))
        self.assertEqual(
            decision.components["L"].status, "provisional_indeterminate"
        )
        self.assertEqual(
            decision.components["H"].status, "provisional_indeterminate"
        )

    def test_observed_reallocation_uses_strict_paired_bounds(self) -> None:
        on_boundary = _category_result(
            {"L": -0.05, "H": 0.05, "U": 0.0}, radius=0.0
        )
        above = _category_result(
            {"L": -0.07, "H": 0.07, "U": 0.0}, radius=0.01
        )
        self.assertEqual(
            decide_observed_disposition_reallocation(
                on_boundary, minimum_effect=0.05
            ).status,
            "provisional_not_demonstrated",
        )
        self.assertEqual(
            decide_observed_disposition_reallocation(
                above, minimum_effect=0.05
            ).status,
            "provisional_positive_reallocation",
        )

    def test_availability_only_co_movement_is_not_reallocation(self) -> None:
        availability_only = _category_result(
            {"L": 0.07, "H": 0.07, "U": -0.14}, radius=0.01
        )
        decision = decide_observed_disposition_reallocation(
            availability_only, minimum_effect=0.05
        )
        self.assertEqual(decision.status, "provisional_not_demonstrated")
        self.assertIsNone(decision.direction)
        self.assertAlmostEqual(decision.u_interval.estimate, -0.14)

    def test_choice_dependent_availability_can_mimic_reallocation(self) -> None:
        # Adversarial interpretation check: unchanged latent choice rates plus
        # arm-dependent missingness by latent choice can yield this exact
        # observed H-up/L-down vector while total U stays unchanged.
        adversarial = _category_result(
            {"L": -0.07, "H": 0.07, "U": 0.0}, radius=0.01
        )
        decision = decide_observed_disposition_reallocation(
            adversarial, minimum_effect=0.05
        )
        self.assertEqual(
            decision.status, "provisional_positive_reallocation"
        )
        self.assertIn("not latent choice responsiveness", decision.interpretation_limit)
        self.assertNotIn("choice responsiveness", decision.rationale)

    def test_exact_reverse_is_provisional_negative_reallocation(self) -> None:
        reverse = _category_result(
            {"L": 0.07, "H": -0.07, "U": 0.0}, radius=0.01
        )
        decision = decide_observed_disposition_reallocation(
            reverse, minimum_effect=0.05
        )
        self.assertEqual(
            decision.status, "provisional_negative_reallocation"
        )
        self.assertEqual(decision.direction, "H_decrease_L_increase")

    def test_malformed_category_results_are_rejected(self) -> None:
        valid = _category_result(
            {"L": -0.07, "H": 0.07, "U": 0.0}, radius=0.01
        )
        malformed = {
            "nonfinite": replace(
                valid,
                intervals={
                    **valid.intervals,
                    "H": ConfidenceInterval(0.07, float("nan"), 0.08),
                },
            ),
            "unordered": replace(
                valid,
                intervals={
                    **valid.intervals,
                    "H": ConfidenceInterval(0.07, 0.08, 0.06),
                },
            ),
            "estimate_not_contained": replace(
                valid,
                intervals={
                    **valid.intervals,
                    "H": ConfidenceInterval(0.07, 0.071, 0.08),
                },
            ),
            "contrast_mismatch": replace(
                valid, contrasts={"L": -0.07, "H": 0.08, "U": 0.0}
            ),
            "noncompositional": replace(
                valid,
                contrasts={"L": -0.06, "H": 0.07, "U": 0.0},
                intervals={
                    "L": ConfidenceInterval(-0.06, -0.07, -0.05),
                    "H": valid.intervals["H"],
                    "U": valid.intervals["U"],
                },
            ),
            "radius_mismatch": replace(
                valid,
                intervals={
                    **valid.intervals,
                    "H": ConfidenceInterval(0.07, 0.059, 0.08),
                },
            ),
            "unsupported_method": replace(valid, method="unverified intervals"),
        }
        for name, result in malformed.items():
            with self.subTest(name=name), self.assertRaises((TypeError, ValueError)):
                decide_observable_probability_vector(
                    result, margins={"L": 0.05, "H": 0.05, "U": 0.02}
                )

    def test_malformed_binary_bounds_are_rejected(self) -> None:
        valid = BinaryBoundsResult(
            identified_lower=-0.10,
            identified_upper=0.10,
            expanded_lower=-0.12,
            expanded_upper=0.12,
            simultaneous_critical_radius=0.02,
            alpha=0.05,
            bootstrap_replicates=10,
            seed=0,
            n_blocks=2,
            n_by_arm={"self": 20, "yoke": 20},
        )
        malformed = {
            "nonfinite": replace(valid, expanded_upper=float("inf")),
            "unordered": replace(
                valid, identified_lower=0.20, identified_upper=0.10
            ),
            "radius_mismatch": replace(valid, expanded_lower=-0.11),
            "unsupported_method": replace(valid, method="unverified bounds"),
        }
        for name, result in malformed.items():
            with self.subTest(name=name), self.assertRaises((TypeError, ValueError)):
                decide_secondary_binary_sensitivity(result, delta=0.05)

    def test_binary_boundary_is_provisionally_indeterminate(self) -> None:
        result = BinaryBoundsResult(
            identified_lower=-0.04999999999999999,
            identified_upper=0.04999999999999999,
            expanded_lower=-0.04999999999999999,
            expanded_upper=0.04999999999999999,
            simultaneous_critical_radius=0.0,
            alpha=0.05,
            bootstrap_replicates=10,
            seed=0,
            n_blocks=2,
            n_by_arm={"self": 20, "yoke": 20},
        )
        decision = decide_secondary_binary_sensitivity(result, delta=0.05)
        self.assertEqual(decision.status, "provisional_indeterminate")

    def test_binary_indeterminacy_cannot_block_provisional_observable_equivalence(self) -> None:
        analysis = analyze_redesigned_outcomes(
            _equal_distribution_with_five_percent_u(),
            scope=_scope(),
            category_margins={"L": 0.05, "H": 0.05, "U": 0.02},
            minimum_observed_reallocation=0.05,
            binary_sensitivity_delta=0.05,
            bootstrap_replicates=40,
            seed=13,
        )
        self.assertEqual(
            analysis.observable_distribution_decision.status,
            "provisional_equivalent",
        )
        self.assertEqual(
            analysis.identified_observable_claim.status,
            "provisional_observable_equivalence",
        )
        self.assertTrue(
            analysis.identified_observable_claim.
            provisional_negative_equivalence_supported
        )
        primary_claim = analysis.identified_observable_claim
        self.assertFalse(
            primary_claim.secondary_binary_sensitivity_used_in_primary_claim
        )
        self.assertEqual(
            analysis.secondary_binary_sensitivity.decision.status,
            "provisional_indeterminate",
        )
        self.assertFalse(
            analysis.secondary_binary_sensitivity.
            can_block_identified_observable_claim
        )
        self.assertEqual(
            analysis.observed_disposition_reallocation.status,
            "provisional_not_demonstrated",
        )
        encoded = analysis.to_json(sort_keys=True)
        decoded = json.loads(encoded)
        self.assertEqual(decoded["inference_role"], INFERENCE_ROLE)
        self.assertEqual(
            decoded["observable_multinomial"]["observed_strata"],
            [{"model_family": "model", "target_family": "target"}],
        )
        self.assertNotIn("_established", encoded)

    def test_declared_coverage_must_exactly_match_observed_strata(self) -> None:
        rows = _equal_distribution_with_five_percent_u()
        overbroad = _scope(("model", "target"), ("unseen", "target"))
        with self.assertRaisesRegex(ValueError, "declared_but_unobserved"):
            analyze_redesigned_outcomes(
                rows,
                scope=overbroad,
                category_margins={"L": 0.05, "H": 0.05, "U": 0.02},
                minimum_observed_reallocation=0.05,
                binary_sensitivity_delta=0.05,
                bootstrap_replicates=4,
            )

    def test_invalid_margins_and_thresholds_are_rejected(self) -> None:
        result = _category_result(
            {"L": 0.0, "H": 0.0, "U": 0.0}, radius=0.01
        )
        with self.assertRaises(ValueError):
            decide_observable_probability_vector(
                result, margins={"L": 0.05, "H": 0.05}
            )
        with self.assertRaises(ValueError):
            decide_observable_probability_vector(
                result, margins={"L": 0.05, "H": 0.05, "U": 0.0}
            )
        with self.assertRaises(ValueError):
            decide_observed_disposition_reallocation(
                result, minimum_effect=float("nan")
            )


if __name__ == "__main__":
    unittest.main()
