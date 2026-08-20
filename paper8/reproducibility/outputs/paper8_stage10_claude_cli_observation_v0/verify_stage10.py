#!/opt/homebrew/bin/python3.14
"""Local byte and semantic verifier for the sanitized Stage-10 observation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "paper8_stage10_claude_cli_observation_manifest.sha256"
PAYLOADS = (
    "OBSERVATION_GATE_STATUS.md",
    "README.md",
    "sanitized_observation.json",
    "verify_stage10.py",
)


def fail(message: str) -> None:
    raise RuntimeError(message)


def main() -> int:
    try:
        if __name__ != "__main__" or sys.version_info[:2] != (3, 14):
            fail("direct CPython 3.14 entry required")
        if not (
            sys.flags.isolated == 1
            and sys.flags.no_site == 1
            and sys.flags.dont_write_bytecode == 1
        ):
            fail("-I -B -S required")
        rows = MANIFEST.read_text(encoding="ascii").splitlines()
        if len(rows) != len(PAYLOADS):
            fail("manifest row count mismatch")
        observed = []
        for row in rows:
            digest, path = row.split("  ", 1)
            if path not in PAYLOADS or path in observed:
                fail("manifest closure mismatch")
            data = (ROOT / path).read_bytes()
            if hashlib.sha256(data).hexdigest() != digest:
                fail(f"payload mismatch: {path}")
            observed.append(path)
        if tuple(observed) != PAYLOADS:
            fail("manifest order mismatch")
        record = json.loads((ROOT / "sanitized_observation.json").read_bytes())
        if record["decision"] != {
            "authorizesExternalAction": False,
            "externalDisposition": "NO_GO_MULTI_MODEL_USAGE_AND_RAW_HTTP_COUNT_UNRESOLVED",
            "localStatus": "OBSERVATION_RECORDED_NONAUTHENTICATING",
            "rawHttpAttemptCount": None,
            "singleModelActivationProven": False,
        }:
            fail("decision boundary mismatch")
        models = [row["model"] for row in record["probe"]["modelUsage"]]
        if models != ["claude-haiku-4-5-20251001", "claude-sonnet-5"]:
            fail("model usage mismatch")
        if record["probe"]["numTurns"] != 1 or len(models) != 2:
            fail("multi-model observation mismatch")
        if any(record["retention"].values()):
            fail("sensitive retention must remain false")
        print("PASS_LOCAL_OBSERVATION_SEAL_NONAUTHORIZING")
        print(f"MANIFEST_SHA256 {hashlib.sha256(MANIFEST.read_bytes()).hexdigest()}")
        print("VISIBLE_TURNS 1")
        print("MODEL_USAGE_ENTRIES 2")
        print("RAW_HTTP_ATTEMPTS unknown")
        print("EXTERNAL_ACTIONS_PERMITTED 0")
        return 0
    except Exception as error:
        print(f"FAIL {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
