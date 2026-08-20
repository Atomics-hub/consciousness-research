from __future__ import annotations

import unittest

from binding_test.planning import request_envelope, retained_sessions, simulate_retention


class RetentionTests(unittest.TestCase):
    def test_retained_sessions_uses_complete_4_by_4_blocks(self) -> None:
        self.assertEqual(retained_sessions(4, 4), 8)
        self.assertEqual(retained_sessions(9, 10), 16)
        self.assertEqual(retained_sessions(3, 100), 0)

    def test_seeded_retention_is_reproducible_and_symmetric(self) -> None:
        first = simulate_retention(128, 0.30, replicates=100)
        second = simulate_retention(128, 0.30, replicates=100)
        mirror = simulate_retention(128, 0.70, replicates=100)
        self.assertEqual(first, second)
        self.assertAlmostEqual(first.asymptotic_fraction_ceiling, 0.60)
        self.assertAlmostEqual(mirror.asymptotic_fraction_ceiling, 0.60)


class RequestEnvelopeTests(unittest.TestCase):
    def test_no_tool_block_uses_24_requests_after_eligibility(self) -> None:
        envelope = request_envelope(
            attempted_sessions=8,
            work_blocks=1,
            tool_blocks=0,
        )
        self.assertEqual(envelope.maximum_generation_requests, 24)

    def test_tool_block_cap_and_attrited_baselines(self) -> None:
        envelope = request_envelope(
            attempted_sessions=20,
            work_blocks=1,
            tool_blocks=1,
            q_low=1,
            q_high=3,
        )
        self.assertEqual(envelope.randomized_sessions, 16)
        self.assertEqual(envelope.maximum_tool_continuation_requests, 16)
        self.assertEqual(envelope.maximum_generation_requests, 68)

    def test_randomized_count_cannot_exceed_attempts(self) -> None:
        with self.assertRaises(ValueError):
            request_envelope(attempted_sessions=7, work_blocks=1, tool_blocks=0)


if __name__ == "__main__":
    unittest.main()
