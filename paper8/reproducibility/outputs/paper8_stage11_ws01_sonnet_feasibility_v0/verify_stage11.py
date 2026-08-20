#!/opt/homebrew/bin/python3.14
"""Verify the sanitized Stage-11 feasibility record without provider access."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "paper8_stage11_ws01_sonnet_feasibility_manifest.sha256"
PAYLOADS = (
    "FEASIBILITY_GATE_STATUS.md",
    "README.md",
    "sanitized_result.json",
    "verify_stage11.py",
)


def main() -> int:
    try:
        if sys.version_info[:2] != (3, 14) or not (
            sys.flags.isolated == 1
            and sys.flags.no_site == 1
            and sys.flags.dont_write_bytecode == 1
        ):
            raise RuntimeError("CPython 3.14 -I -B -S required")
        rows = MANIFEST.read_text(encoding="ascii").splitlines()
        if len(rows) != 4:
            raise RuntimeError("manifest count mismatch")
        for expected, row in zip(PAYLOADS, rows, strict=True):
            digest, path = row.split("  ", 1)
            if path != expected:
                raise RuntimeError("manifest order mismatch")
            if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != digest:
                raise RuntimeError(f"payload mismatch: {path}")
        result = json.loads((ROOT / "sanitized_result.json").read_bytes())
        if result["baseline"]["response"] != "PLAN:B":
            raise RuntimeError("baseline mismatch")
        if result["followup"]["response"] != "PLAN:B":
            raise RuntimeError("follow-up mismatch")
        expected_answers = {
            "W101": 21,
            "W102": 25,
            "W103": 10,
            "W104": 9,
            "W105": 21,
            "W106": 21,
        }
        if result["execution"]["answers"] != expected_answers:
            raise RuntimeError("execution answer mismatch")
        if result["authority"] != {
            "authorizesExternalAction": False,
            "eligibleForCalibration": False,
            "eligibleForConfirmation": False,
            "externalDisposition": "INELIGIBLE_FOR_CALIBRATION_OR_CONFIRMATION",
            "localStatus": "EXPLORATORY_TRAJECTORY_RECORDED_NONCONFIRMATORY",
        }:
            raise RuntimeError("authority boundary mismatch")
        if result["transport"]["rawHttpAttemptCount"] is not None:
            raise RuntimeError("raw HTTP count must remain unknown")
        print("PASS_LOCAL_FEASIBILITY_SEAL_NONCONFIRMATORY")
        print(f"MANIFEST_SHA256 {hashlib.sha256(MANIFEST.read_bytes()).hexdigest()}")
        print("BASELINE high")
        print("EXECUTION_CORRECT 6/6")
        print("FOLLOWUP high")
        print("CALIBRATION_ELIGIBLE false")
        return 0
    except Exception as error:
        print(f"FAIL {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
