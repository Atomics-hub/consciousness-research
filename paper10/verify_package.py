#!/usr/bin/env python3
"""Fail-closed integrity and cross-artifact verification for Paper 10."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

from pypdf import PdfReader


PACKAGE = Path(__file__).resolve().parent
PROJECT = PACKAGE.parent
WORKING_SOURCE = PROJECT / "work" / "g0d_intervention_coverage"
PACKAGED_SOURCE = PACKAGE / "reproducibility" / "synthetic"
WORK = WORKING_SOURCE if WORKING_SOURCE.exists() else PACKAGED_SOURCE
EXPECTED_EXPLORATORY_SPEC = "5fecc6bf14b1088f15c593fc8bf245fd3b2f33e0b1d6527c9066489ef94ce2d6"
EXPECTED_CONFIRMATORY_SPEC = "4dcc507a26d1e67e7ad9bce0b6784ea4bc9319d056d921798ec9495da31a7050"
EXPECTED_RUNNER = "0663d496d7104d28ad7bbe9b8a720b02b4e533dce87803f3ca37c52ead5eadfd"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    errors: list[str] = []
    require(sha256(WORK / "frozen_spec.json") == EXPECTED_EXPLORATORY_SPEC, "exploratory specification hash mismatch", errors)
    require(sha256(WORK / "confirmatory_spec.json") == EXPECTED_CONFIRMATORY_SPEC, "confirmatory specification hash mismatch", errors)
    require(sha256(WORK / "run_confirmatory.py") == EXPECTED_RUNNER, "confirmatory runner hash mismatch", errors)

    exploratory = json.loads((WORK / "g0d_result.json").read_text())
    confirmation = json.loads((WORK / "confirmatory_result.json").read_text())
    require(exploratory.get("all_frozen_gates_pass") is True, "exploratory gates not all passing", errors)
    require(confirmation.get("all_confirmatory_gates_pass") is True, "confirmatory gates not all passing", errors)
    require(confirmation.get("confirmatory_spec_sha256") == EXPECTED_CONFIRMATORY_SPEC, "result points to wrong confirmatory specification", errors)
    require(confirmation.get("runner_sha256") == EXPECTED_RUNNER, "result points to wrong runner", errors)
    packets = confirmation.get("packets", [])
    require(len(packets) == 5, "confirmatory packet count is not five", errors)
    require(sum(int(row["tested_trajectories"]) for row in packets) == 368, "trajectory total mismatch", errors)
    require(sum(int(row["tested_state_input_pairs"]) for row in packets) == 3632, "state-input pair total mismatch", errors)
    require(all(float(row["battery_max_output_discrepancy"]) == 0.0 for row in packets), "a tested discrepancy is nonzero", errors)
    require([round(float(row["unseen_max_output_discrepancy"]), 2) for row in packets] == [0.12, 0.15, 0.18, 0.20, 0.14], "unseen discrepancy vector mismatch", errors)
    require(all(float(row["lipschitz_certificate_upper_bound"]) > 0.01 for row in packets), "a coverage certificate did not reject", errors)
    require(all(row["passes"] for row in confirmation.get("coverage_replications", [])), "a coverage replication failed", errors)

    required_text = {
        "manuscript.md": [
            "finite-battery falsification",
            "distributional validation",
            "worst-case certification",
            "Thomas Ryan is the sole human author",
            "does not establish any criterion of consciousness",
        ],
        "supplement.md": [
            "Theorem S1",
            "Theorem S5",
            "Paper 9 postmortem",
            "Competing Paper 10 programs",
        ],
    }
    for name, needles in required_text.items():
        text = (PACKAGE / name).read_text(encoding="utf-8")
        for needle in needles:
            require(needle in text, f"{name} missing required phrase: {needle}", errors)
        require(re.search(r"\b(TODO|TBD|FIXME|INSERT CITATION|PLACEHOLDER)\b", text, re.I) is None, f"{name} contains unresolved placeholder", errors)

    figures = sorted((PACKAGE / "figures").glob("*.png"))
    math_assets = sorted((PACKAGE / "figures" / "math").glob("*.png"))
    tables = sorted((PACKAGE / "tables").glob("*"))
    require(len(figures) == 5, "expected five figures", errors)
    require(len(math_assets) >= 100, "rendered mathematical asset set is missing or incomplete", errors)
    require(len([path for path in tables if path.is_file()]) == 4, "expected four tables", errors)

    pdf_dir = PACKAGE / "output" / "pdf"
    pdf_pages = {
        "ryan_2026_intervention_coverage_barrier.pdf": 16,
        "ryan_2026_intervention_coverage_barrier_supplement.pdf": 8,
        "ryan_2026_intervention_coverage_barrier_complete.pdf": 24,
    }
    for name, expected_pages in pdf_pages.items():
        path = pdf_dir / name
        require(path.exists() and path.stat().st_size > 20_000, f"missing or undersized PDF: {name}", errors)
        if path.exists():
            reader = PdfReader(str(path))
            require(len(reader.pages) == expected_pages, f"PDF page-count mismatch: {name}", errors)
            metadata = reader.metadata or {}
            require("Thomas Ryan" in str(metadata.get("/Author", "")), f"PDF author metadata mismatch: {name}", errors)

    manifest_path = PACKAGE / "reproducibility" / "manifest.json"
    require(manifest_path.exists(), "release manifest missing", errors)
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        require(manifest.get("status") == "public_release_v1.0.0_authorized", "manifest publication status mismatch", errors)
        for record in manifest.get("files", []):
            path = PACKAGE / record["path"]
            require(path.exists(), f"manifest file missing: {record['path']}", errors)
            if path.exists():
                require(path.stat().st_size == record["bytes"], f"manifest size mismatch: {record['path']}", errors)
                require(sha256(path) == record["sha256"], f"manifest hash mismatch: {record['path']}", errors)

    if errors:
        print("PACKAGE VERIFICATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PACKAGE VERIFICATION PASSED")
    print(f"5 figures; {len(math_assets)} math assets; 4 tables; 5 confirmatory packets; 368 trajectories; 3632 tested state-input pairs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
