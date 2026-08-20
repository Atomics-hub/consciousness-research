"""Tests for nominal estimands, partial identification, and simulations."""

from dataclasses import asdict
import json
import unittest

from zero_call.binding_test.estimands import (
    CATEGORIES,
    BinaryBoundsResult,
    CategoryContrastResult,
    ConfidenceInterval,
    Observation,
    binary_high_choice_bounds,
    category_probability_contrasts,
    decide_binary,
    decide_broad_invariance,
    decide_observable_distribution,
    estimate_binary_bounds,
    estimate_category_contrasts,
    subset_observations,
)
from zero_call.binding_test.simulation import (
    SCENARIOS,
    generate_synthetic_outcomes,
    run_monte_carlo_decision_grid,
    scenario_probabilities,
)


def _manual_rows() -> tuple[Observation, ...]:
    rows = []
    # Aggregate self: H=.50, L=.25, U=.25; yoke: H=.25, L=.50, U=.25.
    self_categories = ("H", "H", "L", "U")
    yoke_categories = ("H", "L", "L", "U")
    for block_index in range(4):
        rows.append(Observation(f"b{block_index}", "self", self_categories[block_index]))
        rows.append(Observation(f"b{block_index}", "yoke", yoke_categories[block_index]))
    return tuple(rows)


class EstimandTests(unittest.TestCase):
    def test_three_category_contrasts_are_nominal_and_sum_to_zero(self) -> None:
        contrasts = category_probability_contrasts(_manual_rows())
        self.assertEqual(set(contrasts), set(CATEGORIES))
        self.assertAlmostEqual(contrasts["H"], 0.25)
        self.assertAlmostEqual(contrasts["L"], -0.25)
        self.assertAlmostEqual(contrasts["U"], 0.0)
        self.assertAlmostEqual(sum(contrasts.values()), 0.0)

    def test_binary_bounds_assign_u_only_to_worst_and_best_cases(self) -> None:
        lower, upper = binary_high_choice_bounds(_manual_rows())
        self.assertAlmostEqual(lower, 0.0)  # .50 - (.25 + .25)
        self.assertAlmostEqual(upper, 0.50)  # (.50 + .25) - .25

    def test_seeded_simultaneous_category_bootstrap_is_reproducible(self) -> None:
        data = generate_synthetic_outcomes(
            "positive", seed=21, n_blocks_per_model_target=8
        )
        first = estimate_category_contrasts(
            data.observations, bootstrap_replicates=120, seed=991
        )
        second = estimate_category_contrasts(
            data.observations, bootstrap_replicates=120, seed=991
        )
        self.assertEqual(first, second)
        self.assertEqual(set(first.intervals), set(CATEGORIES))
        self.assertTrue(all(interval.lower <= interval.estimate <= interval.upper for interval in first.intervals.values()))
        self.assertIn("planning-grade", first.method)
        json.dumps(asdict(first))

    def test_binary_expansion_contains_identified_region(self) -> None:
        data = generate_synthetic_outcomes(
            "positive", seed=33, n_blocks_per_model_target=8
        )
        result = estimate_binary_bounds(
            data.observations, bootstrap_replicates=120, seed=71
        )
        self.assertLessEqual(result.expanded_lower, result.identified_lower)
        self.assertGreaterEqual(result.expanded_upper, result.identified_upper)
        self.assertIn("block bootstrap", result.method)
        json.dumps(result.to_dict())

    def test_binary_decisions_are_two_sided(self) -> None:
        def result(lower: float, upper: float) -> BinaryBoundsResult:
            return BinaryBoundsResult(
                identified_lower=lower,
                identified_upper=upper,
                expanded_lower=lower,
                expanded_upper=upper,
                simultaneous_critical_radius=0.0,
                alpha=0.05,
                bootstrap_replicates=1,
                seed=0,
                n_blocks=2,
                n_by_arm={"self": 2, "yoke": 2},
            )

        self.assertEqual(decide_binary(result(.21, .30), delta=.20).direction, "positive")
        self.assertEqual(decide_binary(result(-.30, -.21), delta=.20).direction, "negative")
        self.assertEqual(decide_binary(result(-.10, .10), delta=.20).status, "invariant")
        self.assertEqual(decide_binary(result(-.10, .25), delta=.20).status, "indeterminate")
        self.assertEqual(decide_binary(result(-.20, .20), delta=.20).status, "indeterminate")

    def test_observable_distribution_decisions_use_all_three_intervals(self) -> None:
        def category_result(intervals: dict[str, ConfidenceInterval]) -> CategoryContrastResult:
            return CategoryContrastResult(
                contrasts={key: value.estimate for key, value in intervals.items()},
                intervals=intervals,
                simultaneous_critical_radius=.01,
                alpha=.05,
                bootstrap_replicates=10,
                seed=0,
                n_blocks=4,
                n_by_arm={"self": 4, "yoke": 4},
            )

        margins = {"L": .10, "H": .10, "U": .05}
        invariant = category_result({
            "L": ConfidenceInterval(0, -.02, .02),
            "H": ConfidenceInterval(0, -.02, .02),
            "U": ConfidenceInterval(0, -.01, .01),
        })
        changed = category_result({
            "L": ConfidenceInterval(-.15, -.18, -.12),
            "H": ConfidenceInterval(.15, .12, .18),
            "U": ConfidenceInterval(0, -.01, .01),
        })
        uncertain = category_result({
            "L": ConfidenceInterval(-.08, -.13, -.03),
            "H": ConfidenceInterval(.08, .03, .13),
            "U": ConfidenceInterval(0, -.01, .01),
        })
        self.assertEqual(decide_observable_distribution(invariant, margins=margins).status, "invariant")
        self.assertEqual(decide_observable_distribution(changed, margins=margins).status, "changed")
        self.assertEqual(decide_observable_distribution(uncertain, margins=margins).status, "indeterminate")
        on_boundary = category_result({
            "L": ConfidenceInterval(-.10, -.10, -.05),
            "H": ConfidenceInterval(.10, .05, .10),
            "U": ConfidenceInterval(0, -.01, .01),
        })
        self.assertEqual(
            decide_observable_distribution(on_boundary, margins=margins).status,
            "indeterminate",
        )

    def test_broad_invariance_requires_both_components(self) -> None:
        invariant_binary = decide_binary(
            BinaryBoundsResult(0, 0, -.01, .01, .01, .05, 10, 0, 2, {"self": 2, "yoke": 2}),
            delta=.10,
        )
        observable = CategoryContrastResult(
            contrasts={category: 0 for category in CATEGORIES},
            intervals={category: ConfidenceInterval(0, -.01, .01) for category in CATEGORIES},
            simultaneous_critical_radius=.01,
            alpha=.05,
            bootstrap_replicates=10,
            seed=0,
            n_blocks=2,
            n_by_arm={"self": 2, "yoke": 2},
        )
        invariant_observable = decide_observable_distribution(
            observable, margins={category: .05 for category in CATEGORIES}
        )
        self.assertEqual(
            decide_broad_invariance(invariant_binary, invariant_observable).status,
            "invariant",
        )
        changed_observable = decide_observable_distribution(
            CategoryContrastResult(
                contrasts={"L": -.2, "H": .2, "U": 0},
                intervals={
                    "L": ConfidenceInterval(-.2, -.25, -.15),
                    "H": ConfidenceInterval(.2, .15, .25),
                    "U": ConfidenceInterval(0, -.01, .01),
                },
                simultaneous_critical_radius=.05,
                alpha=.05,
                bootstrap_replicates=10,
                seed=0,
                n_blocks=2,
                n_by_arm={"self": 2, "yoke": 2},
            ),
            margins={category: .05 for category in CATEGORIES},
        )
        self.assertEqual(
            decide_broad_invariance(invariant_binary, changed_observable).status,
            "not_established",
        )

    def test_synthetic_generator_supports_all_required_scenarios(self) -> None:
        for scenario in SCENARIOS:
            data = generate_synthetic_outcomes(
                scenario,
                seed=7,
                n_blocks_per_model_target=2,
                sessions_per_arm_block=1,
            )
            self.assertTrue(data.observations)
            self.assertEqual(data.truth.scenario, scenario)
            json.dumps(data.to_dict())

    def test_positive_and_mechanism_alias_are_observationally_identical(self) -> None:
        kwargs = dict(seed=404, n_blocks_per_model_target=3, sessions_per_arm_block=2)
        positive = generate_synthetic_outcomes("positive", **kwargs)
        alias = generate_synthetic_outcomes("mechanism_alias", **kwargs)
        self.assertEqual(
            [row.category for row in positive.observations],
            [row.category for row in alias.observations],
        )
        self.assertTrue(all(row.mechanism_signal is None for row in positive.observations))
        self.assertTrue(all(row.mechanism_signal is not None for row in alias.observations))
        self.assertFalse(alias.truth.enforcement_mechanism_identified)

    def test_availability_only_preserves_latent_binary_mix(self) -> None:
        yoke = scenario_probabilities(
            "availability_only", arm="yoke", model_family="m", first_model="m"
        )
        self_arm = scenario_probabilities(
            "availability_only", arm="self", model_family="m", first_model="m"
        )
        self.assertAlmostEqual(yoke[1] / (yoke[0] + yoke[1]), .5)
        self.assertAlmostEqual(self_arm[1] / (self_arm[0] + self_arm[1]), .5)
        self.assertGreater(self_arm[2], yoke[2])

    def test_one_model_only_scenario_can_be_stratified(self) -> None:
        data = generate_synthetic_outcomes(
            "one_model_only",
            seed=19,
            n_blocks_per_model_target=4,
            sessions_per_arm_block=2,
            model_families=("affected", "unaffected"),
            target_families=("t",),
        )
        affected = subset_observations(data.observations, model_family="affected")
        unaffected = subset_observations(data.observations, model_family="unaffected")
        self.assertTrue(affected)
        self.assertTrue(unaffected)
        self.assertEqual(data.truth.affected_models, ("affected",))

    def test_invalid_category_and_incomplete_blocks_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Observation("b", "self", "M")
        rows = (
            Observation("b1", "self", "H"),
            Observation("b2", "self", "H"),
            Observation("b2", "yoke", "L"),
        )
        with self.assertRaises(ValueError):
            estimate_category_contrasts(rows, bootstrap_replicates=10)

    def test_blocks_cannot_cross_fixed_model_target_strata(self) -> None:
        rows = (
            Observation("b1", "self", "H", model_family="m1"),
            Observation("b1", "yoke", "L", model_family="m2"),
            Observation("b2", "self", "H", model_family="m1"),
            Observation("b2", "yoke", "L", model_family="m1"),
        )
        with self.assertRaises(ValueError):
            estimate_category_contrasts(rows, bootstrap_replicates=10)

    def test_monte_carlo_grid_is_seeded_serializable_and_exposes_counts(self) -> None:
        kwargs = dict(
            scenarios=("null", "equivalence_boundary", "one_model_only"),
            block_counts=(3,),
            followup_unavailability_levels=(.05, .15),
            simulation_replicates=3,
            bootstrap_replicates=12,
            sessions_per_arm_block=1,
            model_families=("m1", "m2"),
            target_families=("t",),
            master_seed=90,
        )
        first = run_monte_carlo_decision_grid(**kwargs)
        second = run_monte_carlo_decision_grid(**kwargs)
        self.assertEqual(first, second)
        self.assertEqual(len(first.cells), 6)
        for cell in first.cells:
            self.assertEqual(cell.simulation_replicates, 3)
            self.assertEqual(cell.bootstrap_replicates, 12)
            self.assertAlmostEqual(sum(cell.pooled_binary_rates.values()), 1.0)
            self.assertAlmostEqual(sum(cell.pooled_observable_rates.values()), 1.0)
            self.assertIsNotNone(
                cell.all_strata_same_direction_binary_responsive_rate
            )
            if cell.false_binary_categorical_rate is not None:
                self.assertEqual(
                    cell.binary_false_rate_within_tolerance,
                    cell.false_binary_categorical_rate <= .075,
                )
        json.dumps(first.to_dict())

    def test_alias_and_positive_monte_carlo_cells_match_observably(self) -> None:
        grid = run_monte_carlo_decision_grid(
            scenarios=("positive", "mechanism_alias"),
            block_counts=(3,),
            followup_unavailability_levels=(.10,),
            simulation_replicates=3,
            bootstrap_replicates=10,
            sessions_per_arm_block=1,
            model_families=("m",),
            target_families=("t",),
            master_seed=72,
            cross_stratum_certificates=False,
        )
        positive, alias = grid.cells
        self.assertEqual(positive.pooled_binary_rates, alias.pooled_binary_rates)
        self.assertEqual(positive.pooled_observable_rates, alias.pooled_observable_rates)

    def test_grid_covers_declared_unavailability_levels(self) -> None:
        grid = run_monte_carlo_decision_grid(
            scenarios=("availability_only",),
            block_counts=(2,),
            followup_unavailability_levels=(.05, .10, .15),
            simulation_replicates=1,
            bootstrap_replicates=2,
            sessions_per_arm_block=1,
            model_families=("m",),
            target_families=("t",),
            availability_shift=.10,
            cross_stratum_certificates=False,
        )
        self.assertEqual(
            [cell.followup_unavailability for cell in grid.cells],
            [.05, .10, .15],
        )
        self.assertTrue(
            all(cell.false_binary_categorical_rate is not None for cell in grid.cells)
        )

    def test_boundary_false_rate_counts_any_non_indeterminate_decision(self) -> None:
        grid = run_monte_carlo_decision_grid(
            scenarios=("equivalence_boundary",),
            block_counts=(3,),
            followup_unavailability_levels=(.05,),
            simulation_replicates=4,
            bootstrap_replicates=8,
            sessions_per_arm_block=1,
            model_families=("m",),
            target_families=("t",),
            cross_stratum_certificates=False,
        )
        cell = grid.cells[0]
        self.assertAlmostEqual(
            cell.false_binary_categorical_rate,
            1.0 - cell.pooled_binary_rates["indeterminate"],
        )
        self.assertAlmostEqual(
            cell.false_observable_categorical_rate,
            1.0 - cell.pooled_observable_rates["indeterminate"],
        )


if __name__ == "__main__":
    unittest.main()
