import json
import unittest
from pathlib import Path

import numpy as np

import intervention_coverage as ic


ROOT = Path(__file__).resolve().parent


class InterventionCoverageTests(unittest.TestCase):
    def setUp(self):
        self.spec = json.loads((ROOT / "frozen_spec.json").read_text())

    def test_distance_to_set_linf(self):
        samples = np.asarray([[0.0, 0.0], [1.0, 1.0]])
        points = np.asarray([[0.25, 0.5], [0.9, 0.8]])
        actual = ic.distance_to_set(points, samples)
        np.testing.assert_allclose(actual, [0.5, 0.2])

    def test_equivalent_linear_realizations(self):
        result = ic.linear_controls()
        self.assertLessEqual(
            result["similarity_realization_max_abs_markov_error"],
            self.spec["tolerances"]["exact"],
        )
        self.assertEqual(
            result["delayed_mismatch_first_nonzero_index"],
            result["delayed_mismatch_matched_markov_count"],
        )

    def test_reachable_unseen_counterexample(self):
        result = ic.stateful_counterexample(self.spec)
        self.assertTrue(result["battery_indistinguishable"])
        self.assertTrue(result["unseen_witness_passes_minimum"])
        self.assertFalse(result["certificate_passes"])

    def test_frozen_shams(self):
        result = ic.sham_controls(self.spec)
        self.assertTrue(result["exact_replacement_passes"])
        self.assertTrue(result["hidden_unobservable_passes"])
        self.assertTrue(result["unreachable_mismatch_passes"])
        self.assertTrue(result["wrong_interface_fails_as_required"])
        self.assertTrue(result["non_normal_passes"])

    def test_full_gate(self):
        result = ic.run()
        self.assertTrue(result["all_frozen_gates_pass"])


if __name__ == "__main__":
    unittest.main()
