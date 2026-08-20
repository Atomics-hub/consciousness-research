"""Integrity checks for redesign-report status metadata."""

from types import SimpleNamespace
import unittest

from zero_call import run_redesign_gate


class RedesignRunnerTests(unittest.TestCase):
    def test_phase_firewall_metadata_is_explicit_and_non_numerical(self) -> None:
        firewall = run_redesign_gate._phase_firewall_metadata()
        self.assertEqual(firewall["status"], "PASS")
        self.assertEqual(firewall["confirmatory_phase"], "confirmatory")
        self.assertEqual(firewall["calibration_phase"], "calibration")
        self.assertEqual(
            firewall["required_design_and_observation_bindings"],
            (
                "study_phase",
                "protocol_run_id",
                "protocol_manifest_digest",
            ),
        )
        self.assertEqual(
            firewall["protocol_manifest_digest_algorithm"], "SHA-256"
        )
        self.assertFalse(firewall["calibration_records_confirmatory_eligible"])
        self.assertFalse(firewall["numerical_rules_changed"])
        self.assertIn("before block analysis", firewall["enforcement"])

    def test_overall_verdict_uses_frozen_spec_vocabulary(self) -> None:
        self.assertEqual(
            run_redesign_gate._overall_verdict(
                SimpleNamespace(confirmatory_size_identified=True)
            ),
            "CONFIRMATORY_SIZE_IDENTIFIED",
        )
        for size_status in (
            "CONFIRMATORY_SIZE_NOT_IDENTIFIED",
            "CONFIRMATORY_SIZE_INELIGIBLE",
        ):
            with self.subTest(size_status=size_status):
                self.assertEqual(
                    run_redesign_gate._overall_verdict(
                        SimpleNamespace(
                            confirmatory_size_identified=False,
                            size_status=size_status,
                        )
                    ),
                    "REDESIGN_INCOMPLETE",
                )

    def test_selected_size_metadata_follows_whole_grid_status(self) -> None:
        passed = run_redesign_gate._selected_size_metadata(
            SimpleNamespace(
                confirmatory_size_identified=True,
                size_status="CONFIRMATORY_SIZE_IDENTIFIED",
            ),
            supplemental_power_cells_clear=True,
        )
        self.assertTrue(passed["positive_15"]["whole_design_certified"])
        self.assertEqual(
            passed["positive_15"]["status"],
            "whole_design_trust_root_certified",
        )
        self.assertFalse(passed["positive_1055"]["whole_design_certified"])
        self.assertEqual(
            passed["positive_1055"]["status"],
            "supplemental_power_only_clears_all_12",
        )
        self.assertTrue(
            passed["positive_1055"]["all_12_power_cells_clear"]
        )

        failed = run_redesign_gate._selected_size_metadata(
            SimpleNamespace(
                confirmatory_size_identified=False,
                size_status="CONFIRMATORY_SIZE_NOT_IDENTIFIED",
            ),
            supplemental_power_cells_clear=False,
        )
        self.assertFalse(failed["positive_15"]["whole_design_certified"])
        self.assertEqual(
            failed["positive_15"]["status"],
            "confirmatory_size_not_identified",
        )
        self.assertEqual(
            failed["positive_1055"]["status"],
            "supplemental_power_only_does_not_clear_all_12",
        )


if __name__ == "__main__":
    unittest.main()
