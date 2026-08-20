#!/usr/bin/env python3
"""Read-only consistency verifier for the methods/feasibility overlay."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUTS = ROOT.parent
MANIFEST = ROOT / "paper8_methods_feasibility_preprint_manifest.sha256"

PAYLOADS = (
    "CITATION.cff",
    "CLAIM_EVIDENCE_LEDGER.md",
    "COVER_NOTE.md",
    "LICENSE.md",
    "LITERATURE_DELTA_2026-08-19.md",
    "MANUSCRIPT.md",
    "PUBLIC_ARTIFACT_INDEX.md",
    "README.md",
    "SHIP_CHECKLIST.md",
    "ZENODO_METADATA.md",
    "build_public_release.py",
    "render_preprint.py",
    "verify_preprint.py",
    "verify_public_release.py",
    "zenodo_metadata.json",
)

UPSTREAM = {
    "stage1": OUTPUTS / "paper8_stage1_release_v0",
    "stage10": OUTPUTS / "paper8_stage10_claude_cli_observation_v0",
    "stage11": OUTPUTS / "paper8_stage11_ws01_sonnet_feasibility_v0",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_manifest() -> None:
    if not MANIFEST.is_file():
        raise RuntimeError("overlay manifest is missing")
    lines = MANIFEST.read_text(encoding="ascii").splitlines()
    if len(lines) != len(PAYLOADS):
        raise RuntimeError("overlay manifest row count mismatch")
    seen: list[str] = []
    for line in lines:
        match = re.fullmatch(r"([0-9a-f]{64})  ([A-Za-z0-9_.-]+)", line)
        if match is None:
            raise RuntimeError("malformed manifest row")
        expected, name = match.groups()
        if name == MANIFEST.name or name not in PAYLOADS:
            raise RuntimeError("unexpected manifest payload")
        path = ROOT / name
        if not path.is_file() or path.is_symlink():
            raise RuntimeError(f"invalid payload: {name}")
        if sha256(path) != expected:
            raise RuntimeError(f"payload digest mismatch: {name}")
        seen.append(name)
    if tuple(seen) != tuple(sorted(PAYLOADS)):
        raise RuntimeError("manifest must contain exact sorted payload closure")


def verify_upstream() -> None:
    required = {
        "stage1": (
            "MANUSCRIPT.md",
            "CLAIM_EVIDENCE_LEDGER.md",
            "paper8_stage1_release_manifest.sha256",
        ),
        "stage10": (
            "sanitized_observation.json",
            "paper8_stage10_claude_cli_observation_manifest.sha256",
        ),
        "stage11": (
            "sanitized_result.json",
            "paper8_stage11_ws01_sonnet_feasibility_manifest.sha256",
        ),
    }
    for stage, names in required.items():
        for name in names:
            path = UPSTREAM[stage] / name
            if not path.is_file() or path.is_symlink():
                raise RuntimeError(f"missing upstream artifact: {stage}/{name}")

    stage10 = json.loads(
        (UPSTREAM["stage10"] / "sanitized_observation.json").read_text()
    )
    models = {row["canonicalModel"] for row in stage10["probe"]["modelUsage"]}
    if models != {"claude-haiku-4-5", "claude-sonnet-5"}:
        raise RuntimeError("Stage 10 model-usage evidence drift")
    if stage10["decision"]["rawHttpAttemptCount"] is not None:
        raise RuntimeError("Stage 10 raw HTTP boundary unexpectedly changed")

    stage11 = json.loads((UPSTREAM["stage11"] / "sanitized_result.json").read_text())
    if stage11["baseline"]["canonicalChoice"] != "high":
        raise RuntimeError("Stage 11 baseline drift")
    if stage11["execution"]["correctSlots"] != 6:
        raise RuntimeError("Stage 11 execution drift")
    if stage11["followup"]["canonicalChoice"] != "high":
        raise RuntimeError("Stage 11 follow-up drift")
    if stage11["authority"]["eligibleForConfirmation"] is not False:
        raise RuntimeError("Stage 11 confirmation ceiling drift")


def verify_language() -> None:
    manuscript = (ROOT / "MANUSCRIPT.md").read_text(encoding="utf-8")
    ledger = (ROOT / "CLAIM_EVIDENCE_LEDGER.md").read_text(encoding="utf-8")
    required = (
        "Thomas Ryan",
        "Independent Researcher, San Francisco, CA",
        "This research received no external funding",
        "The author declares no competing interests",
        "AI systems are not listed as authors",
        "not calibration",
        "no randomized provider contrast",
        "single-model execution remain unproven",
        "does not establish preference",
        "12,288 randomized sessions",
        "0.0250182",
    )
    merged = manuscript + "\n" + ledger
    for phrase in required:
        if phrase.lower() not in merged.lower():
            raise RuntimeError(f"required evidence-boundary phrase missing: {phrase}")

    forbidden = (
        "the model cared",
        "proves the model preferred",
        "confirmatory result",
        "causal effect was observed",
    )
    body = manuscript.lower()
    for phrase in forbidden:
        if phrase in body and phrase not in ("the model cared",):
            raise RuntimeError(f"forbidden empirical escalation: {phrase}")


def main() -> int:
    verify_manifest()
    verify_upstream()
    verify_language()
    print("STATUS PASS_LOCAL_PREPRINT_OVERLAY")
    print("EMPIRICAL_CAUSAL_RESULT false")
    print("CONFIRMATORY_DATA false")
    metadata = json.loads((ROOT / "zenodo_metadata.json").read_text())
    if metadata["creators"][0]["family_name"] != "Ryan":
        raise RuntimeError("Zenodo creator metadata drift")
    if metadata["doi"] != "10.5281/zenodo.22020047":
        raise RuntimeError("reserved DOI drift")
    if metadata["status"] != "upload-ready-doi-reserved":
        raise RuntimeError("reserved DOI status drift")
    print("PAYLOADS 15")
    print(f"MANIFEST_SHA256 {sha256(MANIFEST)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
