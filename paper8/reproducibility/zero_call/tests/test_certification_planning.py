"""Tests for vectorized final-inference numerical certification."""

from dataclasses import replace
import json
import unittest

import numpy as np

from zero_call.binding_test.certification_planning import (
    CONFIRMATORY_SIZE_IDENTIFIED,
    CONFIRMATORY_SIZE_INELIGIBLE,
    CONFIRMATORY_SIZE_NOT_IDENTIFIED,
    FALSE_CELL_MIN_REPLICATES,
    FROZEN_CANDIDATE_BLOCKS_PER_MACRO_CELL,
    FROZEN_CERTIFICATION_SENSITIVITY_GRID,
    FROZEN_POSITIVE_SIZE_GATING_REQUIREMENTS,
    HETEROGENEOUS_COUNTERBALANCE_OFFSETS,
    HETEROGENEOUS_FINE_STRATUM_EFFECTS,
    HETEROGENEOUS_PAIR_EFFECTS,
    POWER_CELL_MIN_REPLICATES,
    SCENARIOS,
    CertificationConfig,
    CertificationResult,
    _certify_confirmatory_size_from_replayed,
    _gate_assessments,
    _strict_above,
    _strict_below,
    _wilson,
    block_contrast_distribution,
    block_contrast_moments,
    certify_confirmatory_size,
    gate_replicate_requirements,
    run_certification,
    run_certification_grid,
)


def _config(scenario: str, **overrides: object) -> CertificationConfig:
    values: dict[str, object] = {
        "scenario": scenario,
        "blocks_per_macro_cell": 96,
        "followup_unavailability": 0.05,
        "block_icc": 0.0,
        "outer_replicates": 48,
        "master_seed": 1701,
        "batch_size": 24,
    }
    values.update(overrides)
    return CertificationConfig(**values)  # type: ignore[arg-type]


def _synthetic_positive_size_grid(
    *,
    eligible: bool = True,
    blocks_per_macro_cell: int = 96,
    failing_key: tuple[str, float, float] | None = None,
) -> tuple[CertificationResult, ...]:
    """Build internally coherent Wilson summaries without a 72-cell long run."""

    template = run_certification(
        _config("null", outer_replicates=1, batch_size=1)
    )
    results: list[CertificationResult] = []
    for scenario, selected_metric, role in FROZEN_POSITIVE_SIZE_GATING_REQUIREMENTS:
        required = (
            POWER_CELL_MIN_REPLICATES
            if role == "power"
            else FALSE_CELL_MIN_REPLICATES
        )
        outer_replicates = required if eligible else required - 1
        for grid_index, (unavailability, block_icc) in enumerate(
            FROZEN_CERTIFICATION_SENSITIVITY_GRID
        ):
            config = _config(
                scenario,
                blocks_per_macro_cell=blocks_per_macro_cell,
                followup_unavailability=unavailability,
                block_icc=block_icc,
                outer_replicates=outer_replicates,
                batch_size=1 + grid_index,
            )
            rates = {
                metric: _wilson(0, outer_replicates, 0.95)
                for metric in template.rates
            }
            selected_successes = outer_replicates if role == "power" else 0
            if failing_key == (scenario, unavailability, block_icc):
                selected_successes = 0 if role == "power" else outer_replicates
            rates[selected_metric] = _wilson(
                selected_successes, outer_replicates, 0.95
            )
            assessments = _gate_assessments(config, rates)
            cell_eligible = all(
                assessment.replicate_eligible for assessment in assessments
            )
            cell_passed = (
                all(bool(assessment.passed) for assessment in assessments)
                if cell_eligible
                else None
            )
            macro_rates = {
                cell_id: {
                    metric: _wilson(0, outer_replicates, 0.95)
                    for metric in cell_metrics
                }
                for cell_id, cell_metrics in template.macro_cell_rates.items()
            }
            results.append(
                replace(
                    template,
                    config=config,
                    rates=rates,
                    macro_cell_rates=macro_rates,
                    gate_assessments=assessments,
                    numerical_gate_eligible=cell_eligible,
                    numerical_gate_passed=cell_passed,
                )
            )
    return tuple(results)


class CertificationPlanningTests(unittest.TestCase):
    def test_frozen_config_requires_24_strata_four_blocks_and_exact_rules(self) -> None:
        config = _config("positive")
        self.assertEqual(config.scenario, "positive_15")
        self.assertEqual(config.blocks_per_fine_stratum, 4)
        self.assertEqual(len(config.macro_cells), 4)
        self.assertEqual(config.positive_threshold, 0.05)
        self.assertEqual(config.equivalence_margins, {"L": 0.05, "H": 0.05, "U": 0.02})
        invalid = (
            {"blocks_per_macro_cell": 95},
            {"blocks_per_macro_cell": 72},
            {"followup_unavailability": 0.07},
            {"block_icc": 0.20},
            {"alpha": 0.10},
            {"positive_threshold": 0.0},
            {"equivalence_margin_items": (("L", 0.1), ("H", 0.05), ("U", 0.02))},
            {"target_families": ("work", "tool")},
            {"availability_shift": 0.2},
            {"monte_carlo_confidence": 0.9},
        )
        for override in invalid:
            with self.assertRaises(ValueError):
                _config("positive_15", **override)

    def test_cached_block_distribution_is_nominal_and_icc_inflates_variance(self) -> None:
        probabilities = (0.425, 0.525, 0.05)
        support, mass = block_contrast_distribution(probabilities, probabilities, 0.0)
        self.assertAlmostEqual(float(mass.sum()), 1.0)
        np.testing.assert_allclose(support.sum(axis=1), 0.0, atol=1e-12)
        center0, variance0 = block_contrast_moments(probabilities, probabilities, 0.0)
        center25, variance25 = block_contrast_moments(probabilities, probabilities, 0.25)
        np.testing.assert_allclose(center0, 0.0, atol=1e-12)
        np.testing.assert_allclose(center25, 0.0, atol=1e-12)
        self.assertTrue(np.all(variance25 > variance0))

    def test_seeded_replay_is_exact_and_json_finite(self) -> None:
        config = _config("positive_1055", block_icc=0.10)
        first = run_certification(config)
        second = run_certification(config)
        self.assertEqual(first, second)
        decoded = json.loads(first.to_json(sort_keys=True))
        self.assertEqual(decoded["config"]["scenario"], "positive_1055")
        self.assertIn("Wilson", decoded["rates"]["positive_all_cells"]["interval_method"])
        self.assertFalse(decoded["binary_can_gate"])
        self.assertIn("never", decoded["binary_sensitivity_role"])

    def test_mechanism_alias_has_identical_observable_random_stream(self) -> None:
        positive = run_certification(_config("positive_15"))
        alias = run_certification(_config("mechanism_alias"))
        self.assertEqual(positive.rates, alias.rates)
        self.assertEqual(positive.macro_cell_rates, alias.macro_cell_rates)
        self.assertEqual(positive.distribution_audit, alias.distribution_audit)
        self.assertFalse(alias.mechanism_identified)

    def test_one_cell_effect_never_becomes_an_all_four_headline(self) -> None:
        result = run_certification(
            _config(
                "one_cell_only",
                blocks_per_macro_cell=384,
                outer_replicates=160,
                batch_size=80,
            )
        )
        first_cell = result.config.macro_cells[0]
        self.assertEqual(result.macro_cell_rates[first_cell]["positive"].estimate, 1.0)
        self.assertEqual(result.rates["positive_exactly_one_cell"].estimate, 1.0)
        self.assertEqual(result.rates["positive_all_cells"].estimate, 0.0)
        self.assertEqual(result.gate_assessments[0].role, "false_control")

    def test_one_model_pattern_is_reported_without_all_cell_claim(self) -> None:
        result = run_certification(
            _config(
                "one_model_only",
                blocks_per_macro_cell=384,
                outer_replicates=120,
                batch_size=60,
            )
        )
        self.assertEqual(result.rates["positive_first_model_only_pattern"].estimate, 1.0)
        self.assertEqual(result.rates["positive_all_cells"].estimate, 0.0)

    def test_strict_point05_boundaries_are_false_control_cells(self) -> None:
        positive = _config("positive_boundary")
        negative = _config("negative_boundary")
        self.assertEqual(
            gate_replicate_requirements(positive),
            {"positive_all_cells": FALSE_CELL_MIN_REPLICATES},
        )
        self.assertEqual(
            gate_replicate_requirements(negative),
            {"reverse_all_cells": FALSE_CELL_MIN_REPLICATES},
        )
        result = run_certification(positive)
        for audit in result.distribution_audit:
            self.assertAlmostEqual(audit.true_contrasts[0], -0.05)
            self.assertAlmostEqual(audit.true_contrasts[1], 0.05)
        self.assertFalse(result.numerical_gate_eligible)
        self.assertIsNone(result.numerical_gate_passed)

    def test_replicate_thresholds_distinguish_power_and_false_cells(self) -> None:
        power = _config("positive_15", outer_replicates=9_999)
        boundary = _config("positive_boundary", outer_replicates=19_999)
        null = _config("null", outer_replicates=10_000)
        self.assertEqual(
            gate_replicate_requirements(power),
            {"positive_all_cells": POWER_CELL_MIN_REPLICATES},
        )
        self.assertEqual(
            gate_replicate_requirements(boundary),
            {"positive_all_cells": FALSE_CELL_MIN_REPLICATES},
        )
        self.assertEqual(
            gate_replicate_requirements(null),
            {
                "positive_all_cells": FALSE_CELL_MIN_REPLICATES,
                "reverse_all_cells": FALSE_CELL_MIN_REPLICATES,
                "equivalence_all_cells": POWER_CELL_MIN_REPLICATES,
            },
        )
        screened = run_certification(_config("positive_15", outer_replicates=24))
        self.assertFalse(screened.numerical_gate_eligible)
        self.assertIsNone(screened.gate_assessments[0].passed)

    def test_availability_only_moves_l_h_together_and_binary_never_gates(self) -> None:
        result = run_certification(_config("availability_only", outer_replicates=32))
        for audit in result.distribution_audit:
            self.assertAlmostEqual(audit.true_contrasts[0], -0.05)
            self.assertAlmostEqual(audit.true_contrasts[1], -0.05)
            self.assertAlmostEqual(audit.true_contrasts[2], 0.10)
        self.assertFalse(result.binary_can_gate)
        for audit in result.distribution_audit:
            np.testing.assert_allclose(
                audit.latent_binary_high_contrast_bounds,
                (-0.10, 0.10),
                rtol=0.0,
                atol=1e-12,
            )
            self.assertIn("worst/best", audit.latent_binary_sensitivity_method)
        self.assertEqual(
            {assessment.metric for assessment in result.gate_assessments},
            {"positive_all_cells", "equivalence_all_cells"},
        )

    def test_zero_u_zero_standard_error_guard_blocks_equivalence(self) -> None:
        result = run_certification(
            _config(
                "null",
                followup_unavailability=0.0,
                blocks_per_macro_cell=384,
                outer_replicates=80,
                batch_size=40,
            )
        )
        self.assertEqual(result.rates["equivalence_all_cells"].estimate, 0.0)

    def test_heterogeneous_fixed_panel_targets_equal_weight_boundary(self) -> None:
        self.assertEqual(len(HETEROGENEOUS_PAIR_EFFECTS), 6)
        self.assertEqual(len(HETEROGENEOUS_COUNTERBALANCE_OFFSETS), 4)
        self.assertEqual(len(HETEROGENEOUS_FINE_STRATUM_EFFECTS), 24)
        self.assertAlmostEqual(
            sum(HETEROGENEOUS_FINE_STRATUM_EFFECTS) / 24,
            0.05,
        )
        self.assertLess(min(HETEROGENEOUS_FINE_STRATUM_EFFECTS), 0.0)
        self.assertGreater(max(HETEROGENEOUS_FINE_STRATUM_EFFECTS), 0.20)

        result = run_certification(
            _config(
                "fine_stratum_heterogeneity",
                followup_unavailability=0.15,
                block_icc=0.25,
                outer_replicates=16,
                batch_size=7,
            )
        )
        self.assertEqual(
            gate_replicate_requirements(result.config),
            {"positive_all_cells": FALSE_CELL_MIN_REPLICATES},
        )
        self.assertEqual(result.gate_assessments[0].role, "false_control")
        self.assertFalse(result.numerical_gate_eligible)

        for audit in result.distribution_audit:
            fine = audit.fine_stratum_distributions
            self.assertEqual(len(fine), 24)
            self.assertEqual(len({row.fine_stratum for row in fine}), 24)
            self.assertAlmostEqual(sum(row.prospective_weight for row in fine), 1.0)
            observed_effects = tuple(row.true_contrasts[1] for row in fine)
            np.testing.assert_allclose(
                observed_effects,
                HETEROGENEOUS_FINE_STRATUM_EFFECTS,
                rtol=0.0,
                atol=1e-12,
            )
            np.testing.assert_allclose(
                [row.true_contrasts[0] for row in fine],
                -np.asarray(HETEROGENEOUS_FINE_STRATUM_EFFECTS),
                rtol=0.0,
                atol=1e-12,
            )
            self.assertGreater(
                len({row.self_probabilities for row in fine}),
                12,
                "the engine must retain distinct per-stratum generators",
            )
            for row in (fine[0], fine[-1]):
                center, _variance = block_contrast_moments(
                    row.self_probabilities,
                    row.yoke_probabilities,
                    result.config.block_icc,
                )
                np.testing.assert_allclose(
                    center,
                    row.true_contrasts,
                    rtol=0.0,
                    atol=1e-12,
                )
            equal_weight_truth = np.mean(
                np.asarray([row.true_contrasts for row in fine]), axis=0
            )
            np.testing.assert_allclose(
                audit.true_contrasts,
                equal_weight_truth,
                rtol=0.0,
                atol=1e-12,
            )
            np.testing.assert_allclose(
                audit.true_contrasts,
                (-0.05, 0.05, 0.0),
                rtol=0.0,
                atol=1e-12,
            )
            self.assertIn("equal-1/24", audit.probability_summary)

    def test_heterogeneous_boundary_never_becomes_power_by_float_roundoff(self) -> None:
        for unavailable in (0.0, 0.05, 0.10, 0.15):
            for block_icc in (0.0, 0.10, 0.25):
                config = _config(
                    "fine_stratum_heterogeneity",
                    followup_unavailability=unavailable,
                    block_icc=block_icc,
                    outer_replicates=2,
                    batch_size=1,
                )
                self.assertEqual(
                    gate_replicate_requirements(config),
                    {"positive_all_cells": FALSE_CELL_MIN_REPLICATES},
                )
                assessment = run_certification(config).gate_assessments[0]
                self.assertEqual(assessment.role, "false_control")
                self.assertEqual(
                    assessment.required_replicates,
                    FALSE_CELL_MIN_REPLICATES,
                )

    def test_heterogeneous_per_stratum_streams_are_batch_invariant(self) -> None:
        common = {
            "followup_unavailability": 0.15,
            "block_icc": 0.25,
            "outer_replicates": 73,
        }
        single = run_certification(
            _config("fine_stratum_heterogeneity", batch_size=1, **common)
        )
        chunked = run_certification(
            _config("fine_stratum_heterogeneity", batch_size=17, **common)
        )
        whole = run_certification(
            _config("fine_stratum_heterogeneity", batch_size=73, **common)
        )
        self.assertEqual(single.rates, chunked.rates)
        self.assertEqual(single.rates, whole.rates)
        self.assertEqual(single.macro_cell_rates, chunked.macro_cell_rates)
        self.assertEqual(single.macro_cell_rates, whole.macro_cell_rates)
        self.assertEqual(single.distribution_audit, whole.distribution_audit)
        self.assertEqual(single.gate_assessments, chunked.gate_assessments)
        self.assertEqual(single.gate_assessments, whole.gate_assessments)
        self.assertEqual(
            single.numerical_gate_eligible, whole.numerical_gate_eligible
        )
        self.assertEqual(single.numerical_gate_passed, whole.numerical_gate_passed)

    def test_exact_frozen_candidate_sequence_is_enforced_and_serialized(self) -> None:
        self.assertEqual(
            FROZEN_CANDIDATE_BLOCKS_PER_MACRO_CELL,
            (
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
            ),
        )
        for noncandidate in (216, 312, 3096):
            with self.assertRaisesRegex(ValueError, "exact frozen candidate"):
                _config("positive_15", blocks_per_macro_cell=noncandidate)

    def test_strict_helpers_apply_the_confirmatory_one_e_minus_12_policy(self) -> None:
        above = _strict_above(
            np.asarray((0.05, 0.05 + 0.5e-12, 0.05 + 2.0e-12)),
            0.05,
        )
        below = _strict_below(
            np.asarray((-0.05, -0.05 - 0.5e-12, -0.05 - 2.0e-12)),
            -0.05,
        )
        np.testing.assert_array_equal(above, (False, False, True))
        np.testing.assert_array_equal(below, (False, False, True))

    def test_whole_design_size_gate_passes_only_exact_declared_metrics(self) -> None:
        grid = _synthetic_positive_size_grid()
        null_cells = [
            result for result in grid if result.config.scenario == "null"
        ]
        self.assertTrue(null_cells)
        self.assertTrue(
            all(result.numerical_gate_passed is False for result in null_cells),
            "synthetic null equivalence power intentionally fails",
        )

        decision = _certify_confirmatory_size_from_replayed(grid)
        self.assertTrue(decision.numerical_gate_eligible)
        self.assertTrue(decision.numerical_gate_passed)
        self.assertTrue(decision.confirmatory_size_identified)
        self.assertEqual(decision.size_status, CONFIRMATORY_SIZE_IDENTIFIED)
        self.assertEqual(decision.expected_grid_cells, 84)
        self.assertEqual(decision.observed_grid_cells, 84)
        self.assertEqual(
            decision.required_gating_scenario_metrics,
            FROZEN_POSITIVE_SIZE_GATING_REQUIREMENTS,
        )
        self.assertEqual(
            decision.required_sensitivity_grid,
            FROZEN_CERTIFICATION_SENSITIVITY_GRID,
        )
        self.assertEqual(
            {cell.metric for cell in decision.cell_assessments},
            {"positive_all_cells"},
        )
        self.assertEqual(
            {cell.role for cell in decision.cell_assessments},
            {"power", "false_control"},
        )
        decoded = json.loads(decision.to_json(sort_keys=True))
        self.assertEqual(decoded["size_status"], CONFIRMATORY_SIZE_IDENTIFIED)
        self.assertEqual(
            decoded["frozen_candidate_blocks_per_macro_cell"][-1], 3072
        )
        self.assertIn("mechanism_alias", decoded["non_gating_diagnostic_scenarios"])

    def test_whole_design_size_gate_has_honest_ineligible_and_fail_states(self) -> None:
        screened = _certify_confirmatory_size_from_replayed(
            _synthetic_positive_size_grid(eligible=False)
        )
        self.assertFalse(screened.numerical_gate_eligible)
        self.assertIsNone(screened.numerical_gate_passed)
        self.assertFalse(screened.confirmatory_size_identified)
        self.assertEqual(screened.size_status, CONFIRMATORY_SIZE_INELIGIBLE)

        failed = _certify_confirmatory_size_from_replayed(
            _synthetic_positive_size_grid(
                failing_key=("positive_15", 0.15, 0.25)
            )
        )
        self.assertTrue(failed.numerical_gate_eligible)
        self.assertFalse(failed.numerical_gate_passed)
        self.assertFalse(failed.confirmatory_size_identified)
        self.assertEqual(failed.size_status, CONFIRMATORY_SIZE_NOT_IDENTIFIED)

    def test_whole_design_size_gate_rejects_malformed_coverage_and_results(self) -> None:
        grid = list(_synthetic_positive_size_grid())
        with self.assertRaisesRegex(ValueError, "duplicate"):
            _certify_confirmatory_size_from_replayed((*grid, grid[0]))
        with self.assertRaisesRegex(ValueError, "exact frozen"):
            _certify_confirmatory_size_from_replayed(grid[:-1])

        mixed_size = list(grid)
        mixed_size[0] = replace(
            mixed_size[0],
            config=replace(mixed_size[0].config, blocks_per_macro_cell=120),
        )
        with self.assertRaisesRegex(ValueError, "mixed blocks_per_macro_cell"):
            _certify_confirmatory_size_from_replayed(mixed_size)

        mixed_panel = list(grid)
        mixed_panel[0] = replace(
            mixed_panel[0],
            config=replace(
                mixed_panel[0].config,
                model_snapshots=("other_snapshot_a", "other_snapshot_b"),
            ),
        )
        with self.assertRaisesRegex(ValueError, "mixed model-snapshot"):
            _certify_confirmatory_size_from_replayed(mixed_panel)

        out_of_scope = list(grid)
        out_of_scope[0] = replace(
            out_of_scope[0],
            config=replace(out_of_scope[0].config, scenario="mechanism_alias"),
        )
        with self.assertRaisesRegex(ValueError, "out-of-scope"):
            _certify_confirmatory_size_from_replayed(out_of_scope)

        corrupt = list(grid)
        corrupt_rates = dict(corrupt[0].rates)
        corrupt_rates["positive_all_cells"] = replace(
            corrupt_rates["positive_all_cells"], interval_lower=0.123
        )
        corrupt[0] = replace(corrupt[0], rates=corrupt_rates)
        with self.assertRaisesRegex(ValueError, "Wilson interval is inconsistent"):
            _certify_confirmatory_size_from_replayed(corrupt)

    def test_public_size_trust_root_replays_and_rejects_coherent_forgery(self) -> None:
        real_grid = tuple(
            run_certification(
                _config(
                    scenario,
                    followup_unavailability=unavailability,
                    block_icc=block_icc,
                    outer_replicates=1,
                    batch_size=1,
                )
            )
            for scenario, _metric, _role in FROZEN_POSITIVE_SIZE_GATING_REQUIREMENTS
            for unavailability, block_icc in FROZEN_CERTIFICATION_SENSITIVITY_GRID
        )
        decision = certify_confirmatory_size(real_grid)
        self.assertFalse(decision.numerical_gate_eligible)
        self.assertIsNone(decision.numerical_gate_passed)
        self.assertEqual(decision.size_status, CONFIRMATORY_SIZE_INELIGIBLE)

        forged_grid = list(real_grid)
        observed = forged_grid[0]
        forged_rates = dict(observed.rates)
        original = observed.rates["positive_all_cells"]
        forged_successes = 1 - original.successes
        forged_rates["positive_all_cells"] = _wilson(
            forged_successes,
            original.replicates,
            original.confidence_level,
        )
        forged_grid[0] = replace(
            observed,
            rates=forged_rates,
            gate_assessments=_gate_assessments(observed.config, forged_rates),
        )
        with self.assertRaisesRegex(ValueError, "mandatory deterministic replay"):
            certify_confirmatory_size(forged_grid)

    def test_grid_and_scenario_coverage(self) -> None:
        with self.assertRaises(ValueError):
            run_certification_grid(())
        configs = tuple(_config(scenario, outer_replicates=2, batch_size=2) for scenario in SCENARIOS)
        results = run_certification_grid(configs)
        self.assertEqual({result.config.scenario for result in results}, set(SCENARIOS))


if __name__ == "__main__":
    unittest.main()
