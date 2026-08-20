from __future__ import annotations

import unittest

from binding_test.stress import (
    binary_invariance_limit,
    simulate_post_treatment_history_divergence,
    simulate_snapshot_drift,
)


class StressTests(unittest.TestCase):
    def test_five_percent_u_touches_margin_and_cannot_pass_strict_invariance(self) -> None:
        below = binary_invariance_limit(.049, .05)
        boundary = binary_invariance_limit(.05, .05)
        above = binary_invariance_limit(.15, .05)
        self.assertTrue(below.strict_invariance_possible)
        self.assertFalse(boundary.strict_invariance_possible)
        self.assertFalse(above.strict_invariance_possible)

    def test_snapshot_blocking_removes_time_confounding_in_expectation(self) -> None:
        result = simulate_snapshot_drift(replicates=200, blocks=20)
        self.assertLess(result.valid_absolute_bias, .03)
        self.assertGreater(result.invalid_absolute_bias, .50)

    def test_post_treatment_conditioning_creates_spurious_effect(self) -> None:
        result = simulate_post_treatment_history_divergence(sessions=20_000)
        self.assertLess(abs(result.primary_randomized_contrast), .03)
        self.assertGreater(result.mean_absolute_conditioned_contrast, .95)


if __name__ == "__main__":
    unittest.main()
