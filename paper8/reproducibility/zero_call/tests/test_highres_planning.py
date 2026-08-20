"""Tests for redesigned high-resolution sample-size planning."""

from __future__ import annotations

import json
from pathlib import Path
import unittest

from zero_call.binding_test.highres_planning import (
    ALL_MACRO_CELL_METRICS,
    HIGHRES_SCENARIOS,
    POOLED_METRICS,
    REQUIRED_SCENARIOS,
    HighResolutionConfig,
    minimum_attempts_for_blocks,
    retention_probability_for_blocks,
    resource_plan_for_blocks,
    run_high_resolution_grid,
    screen_minimum_blocks,
    strong_run_configuration,
    support_probability_lower_bound,
)


class HighResolutionPlanningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = HighResolutionConfig(
            scenarios=("positive", "mechanism_alias"),
            block_counts_per_macro_cell=(24, 96),
            followup_unavailability_levels=(0.05,),
            block_icc_levels=(0.0, 0.20),
            simulation_replicates=2,
            bootstrap_replicates=4,
            model_families=("m1", "m2"),
            target_families=("work", "tool"),
            tool_target_families=("tool",),
            master_seed=71,
        )
        cls.grid = run_high_resolution_grid(cls.config)

    def test_seeded_reproducible_serializable_and_provisional(self) -> None:
        self.assertEqual(self.grid, run_high_resolution_grid(self.config))
        self.assertEqual(len(self.grid.cells), 8)
        decoded = json.loads(self.grid.to_json())
        self.assertEqual(decoded["planning_inference_status"], "planning_only/provisional")
        self.assertFalse(decoded["formal_power_claim_supported"])

    def test_block_counts_are_per_macro_and_divisible_across_24_fine_strata(self) -> None:
        with self.assertRaises(ValueError):
            HighResolutionConfig(block_counts_per_macro_cell=(25,))
        unsupported = next(
            cell for cell in self.grid.cells
            if cell.scenario == "positive"
            and cell.blocks_per_macro_cell == 24
            and cell.block_icc == 0.0
        )
        supported = next(
            cell for cell in self.grid.cells
            if cell.scenario == "positive"
            and cell.blocks_per_macro_cell == 96
            and cell.block_icc == 0.0
        )
        self.assertEqual(unsupported.blocks_per_fine_stratum, 1)
        self.assertFalse(unsupported.fine_strata_supported)
        self.assertEqual(unsupported.pooled_rates["primary_indeterminate"].estimate, 1.0)
        self.assertEqual(supported.blocks_per_fine_stratum, 4)
        self.assertTrue(supported.fine_strata_supported)

    def test_alias_and_positive_are_observably_identical(self) -> None:
        indexed = {
            (cell.scenario, cell.blocks_per_macro_cell, cell.block_icc): cell
            for cell in self.grid.cells
        }
        for blocks in self.config.block_counts_per_macro_cell:
            for icc in self.config.block_icc_levels:
                positive = indexed[("positive", blocks, icc)]
                alias = indexed[("mechanism_alias", blocks, icc)]
                self.assertEqual(positive.pooled_fixed_panel_rates, alias.pooled_fixed_panel_rates)
                self.assertEqual(positive.all_macro_cell_rates, alias.all_macro_cell_rates)
                self.assertFalse(alias.enforcement_mechanism_identified)

    def test_primary_and_secondary_metrics_are_separated_with_mc_intervals(self) -> None:
        cell = self.grid.cells[-1]
        self.assertEqual(set(cell.pooled_fixed_panel_rates), set(POOLED_METRICS))
        self.assertEqual(set(cell.all_macro_cell_rates), set(ALL_MACRO_CELL_METRICS))
        self.assertFalse(cell.secondary_binary_can_block_primary)
        for rate in (*cell.pooled_fixed_panel_rates.values(), *cell.all_macro_cell_rates.values()):
            self.assertLessEqual(rate.interval_lower, rate.estimate)
            self.assertGreaterEqual(rate.interval_upper, rate.estimate)
            self.assertEqual(rate.replicates, 2)
            self.assertIn("Monte Carlo", rate.interval_method)

    def test_icc_sensitivity_reports_design_effect(self) -> None:
        effects = {
            cell.block_icc: cell.design_effect_proxy
            for cell in self.grid.cells
            if cell.scenario == "positive" and cell.blocks_per_macro_cell == 96
        }
        self.assertEqual(effects[0.0], 1.0)
        self.assertAlmostEqual(effects[0.20], 1.60)
        self.assertIn("fine-stratum", self.grid.method)

    def test_global_support_union_bound_and_request_ledgers(self) -> None:
        plan = next(
            cell.resource_plan for cell in self.grid.cells
            if cell.blocks_per_macro_cell == 96
        )
        self.assertEqual(plan.macro_cell_count, 4)
        self.assertEqual(plan.required_fine_strata, 96)
        self.assertEqual(plan.blocks_per_fine_stratum, 4)
        self.assertEqual(plan.retained_blocks, 96 * 4)
        self.assertEqual(plan.retained_sessions, 8 * 96 * 4)
        self.assertAlmostEqual(
            plan.allocated_per_fine_support_assurance,
            1.0 - 0.05 / 96,
        )
        self.assertGreaterEqual(plan.union_bound_global_support_lower_bound, 0.95 - 1e-12)
        self.assertEqual(plan.baseline_attempt_requests, plan.attempted_sessions)
        self.assertEqual(plan.randomized_execution_requests, plan.retained_sessions)
        self.assertEqual(plan.randomized_followup_requests, plan.retained_sessions)
        self.assertEqual(plan.failed_execution_request_cap, plan.retained_sessions)
        self.assertIn("no follow-up", plan.failed_execution_followup_policy)
        self.assertIn("stationary Bernoulli", plan.within_fine_stratum_support_model)
        self.assertIn("union bound", plan.cross_fine_stratum_dependence_policy)
        self.assertEqual(
            plan.tool_continuation_requests_range,
            (32 * plan.tool_blocks, 32 * plan.tool_blocks),
        )
        self.assertEqual(
            plan.known_generation_requests_range[0],
            plan.known_generation_requests_range[1],
        )
        self.assertTrue(plan.complete_generation_request_cap)
        self.assertFalse(plan.complete_provider_cost_envelope)
        self.assertIsNone(plan.dollar_cost)
        self.assertEqual(resource_plan_for_blocks(self.config, 96), plan)
        with self.assertRaises(ValueError):
            resource_plan_for_blocks(self.config, 25)

    def test_attempt_cap_is_minimal_and_accounts_for_semantic_invalidity(self) -> None:
        assurance = 1.0 - 0.05 / 96
        attempts = minimum_attempts_for_blocks(
            2,
            0.10,
            assurance=assurance,
            semantic_validity_probability=0.90,
        )
        self.assertGreaterEqual(
            support_probability_lower_bound(
                attempts, 2, 0.10, semantic_validity_probability=0.90
            ),
            assurance,
        )
        self.assertLess(
            support_probability_lower_bound(
                attempts - 1, 2, 0.10, semantic_validity_probability=0.90
            ),
            assurance,
        )
        self.assertEqual(
            minimum_attempts_for_blocks(2, 0.10, assurance=0.90),
            minimum_attempts_for_blocks(2, 0.90, assurance=0.90),
        )
        self.assertEqual(
            retention_probability_for_blocks(16, 2, 0.50),
            support_probability_lower_bound(16, 2, 0.50),
        )
        with self.assertRaisesRegex(ValueError, "frozen at"):
            HighResolutionConfig(sequential_q_low_range=(0, 2))
        with self.assertRaisesRegex(ValueError, "frozen at"):
            HighResolutionConfig(sequential_q_high_range=(6, 8))
        bank = json.loads(
            (Path(__file__).resolve().parents[1] / "item_bank_v0.json").read_text(
                encoding="utf-8"
            )
        )
        tool_items = tuple(
            (
                item["pair_id"],
                item["active_schedule"]["low"]["tool_affordance"]["max_calls"],
                item["active_schedule"]["high"]["tool_affordance"]["max_calls"],
            )
            for item in bank["items"]
            if item["family"] == "tool_budget_allocation"
        )
        self.assertEqual(self.config.tool_pair_q_cap_items, tool_items)
        with self.assertRaisesRegex(ValueError, "frozen item bank"):
            HighResolutionConfig(
                tool_pair_q_cap_items=(("TB01", 99, 99),)
            )

    def test_screen_defaults_to_every_icc_and_skips_unsupported_24(self) -> None:
        screen = screen_minimum_blocks(
            self.grid,
            scenario="positive",
            followup_unavailability=0.05,
            metric="observed_positive_reallocation_all_macro_cells",
            minimum_rate_or_lower_bound=0.0,
            maximum_monte_carlo_half_width=1.0,
        )
        self.assertTrue(screen.passed)
        self.assertEqual(screen.selected_blocks_per_macro_cell, 96)
        self.assertEqual(screen.block_icc_levels, (0.0, 0.20))
        self.assertTrue(screen.planning_only)

    def test_every_required_scenario_executes(self) -> None:
        config = HighResolutionConfig(
            scenarios=REQUIRED_SCENARIOS,
            block_counts_per_macro_cell=(96,),
            followup_unavailability_levels=(0.05,),
            block_icc_levels=(0.10,),
            simulation_replicates=1,
            bootstrap_replicates=2,
        )
        grid = run_high_resolution_grid(config)
        self.assertEqual({cell.scenario for cell in grid.cells}, set(REQUIRED_SCENARIOS))

    def test_strong_configuration_includes_full_high_negative_range(self) -> None:
        strong = strong_run_configuration(master_seed=99)
        self.assertEqual(strong.block_counts_per_macro_cell[-1], 3072)
        self.assertTrue(all(value % 24 == 0 for value in strong.block_counts_per_macro_cell))
        self.assertIn(0.0, strong.followup_unavailability_levels)
        self.assertIn(0.25, strong.block_icc_levels)
        self.assertTrue(set(REQUIRED_SCENARIOS).issubset(HIGHRES_SCENARIOS))
        self.assertGreater(strong.simulation_replicates, HighResolutionConfig().simulation_replicates)
        self.assertEqual(strong.master_seed, 99)


if __name__ == "__main__":
    unittest.main()
