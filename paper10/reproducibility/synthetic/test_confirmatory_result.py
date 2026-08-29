import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent


class ConfirmatoryResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads((ROOT / "confirmatory_result.json").read_text())

    def test_frozen_spec_hash(self):
        self.assertEqual(
            self.result["confirmatory_spec_sha256"],
            "4dcc507a26d1e67e7ad9bce0b6784ea4bc9319d056d921798ec9495da31a7050",
        )

    def test_every_packet_is_conjunctive_pass(self):
        self.assertEqual(len(self.result["packets"]), 5)
        self.assertTrue(all(packet["packet_pass"] for packet in self.result["packets"]))
        self.assertTrue(self.result["primary_conjunctive_gate_passes"])

    def test_every_coverage_replication_passes(self):
        self.assertEqual(len(self.result["coverage_replications"]), 5)
        self.assertTrue(all(row["passes"] for row in self.result["coverage_replications"]))
        self.assertTrue(self.result["secondary_conjunctive_gate_passes"])

    def test_overall_gate(self):
        self.assertTrue(self.result["all_confirmatory_gates_pass"])


if __name__ == "__main__":
    unittest.main()
