#!/usr/bin/env python3
"""Assemble the self-contained Paper 10 reproducibility snapshot and checksums."""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
PROJECT = PACKAGE.parent
SOURCE = PROJECT / "work" / "g0d_intervention_coverage"
REPRO = PACKAGE / "reproducibility"
SYNTHETIC = REPRO / "synthetic"
AUDIT = REPRO / "audit"

SYNTHETIC_FILES = [
    "README.md",
    "frozen_spec.json",
    "confirmatory_spec.json",
    "intervention_coverage.py",
    "run_confirmatory.py",
    "g0d_result.json",
    "confirmatory_result.json",
    "test_intervention_coverage.py",
    "test_confirmatory_result.py",
]

AUDIT_FILES = {
    PROJECT / "outputs" / "paper10_evidence_ledger.md": "evidence_ledger.md",
    PROJECT / "outputs" / "paper10_e0a_no_go_report.md": "paper9_postmortem_no_go.md",
    PROJECT / "outputs" / "paper10_intervention_basis_g0_report.md": "intervention_basis_no_go.md",
    PROJECT / "outputs" / "paper10_intervention_coverage_g0_report.md": "intervention_coverage_selection_report.md",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def copy_snapshot() -> None:
    SYNTHETIC.mkdir(parents=True, exist_ok=True)
    AUDIT.mkdir(parents=True, exist_ok=True)
    for name in SYNTHETIC_FILES:
        source = SOURCE / name
        if not source.exists():
            raise FileNotFoundError(source)
        shutil.copy2(source, SYNTHETIC / name)
    for source, destination in AUDIT_FILES.items():
        if not source.exists():
            raise FileNotFoundError(source)
        shutil.copy2(source, AUDIT / destination)


def write_repro_readme() -> None:
    text = """# Paper 10 reproducibility snapshot

This directory is a mechanical snapshot assembled from the frozen Paper 10
working artifacts. `synthetic/` contains the executable construction,
specifications, results, and tests. `audit/` contains decision reports and the
evidence ledger.

From this directory, run:

```bash
python3 -m unittest discover -s synthetic -p 'test_*.py' -v
python3 synthetic/intervention_coverage.py
python3 synthetic/run_confirmatory.py
```

Re-running the scripts overwrites deterministic result JSONs. It does not create
an independent experiment or a new preregistration event. SHA-256 values prove
artifact identity only. Thomas Ryan authorized the public v1.0.0 release on
29 August 2026 and remains the accountable operator.
"""
    (REPRO / "README.md").write_text(text, encoding="utf-8")


def package_files() -> list[Path]:
    excluded_names = {"manifest.json", "SHA256SUMS"}
    paths = []
    for path in PACKAGE.rglob("*"):
        if not path.is_file() or path.name in excluded_names:
            continue
        if "tmp" in path.parts or "__pycache__" in path.parts or ".DS_Store" == path.name:
            continue
        paths.append(path)
    return sorted(paths, key=lambda path: path.relative_to(PACKAGE).as_posix())


def write_manifest() -> None:
    files = package_files()
    records = [
        {
            "path": path.relative_to(PACKAGE).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in files
    ]
    manifest = {
        "schema_version": "1.0",
        "package": "paper10-intervention-coverage-barrier",
        "version": "1.0.0",
        "author": "Thomas Ryan",
        "status": "public_release_v1.0.0_authorized",
        "assembled_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "claim_ceiling": "No claim about consciousness, identity, survival, biological replaceability, substrate independence, emulation impossibility, or failure of a specific replacement.",
        "non_independence": "Hashes, unit tests, repeated seeds, deterministic reruns, and AI agreement are not independent scientific evidence.",
        "files": records,
    }
    (REPRO / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    sums = "".join(f"{record['sha256']}  {record['path']}\n" for record in records)
    (REPRO / "SHA256SUMS").write_text(sums, encoding="utf-8")
    print(f"assembled {len(records)} files")


def main() -> None:
    copy_snapshot()
    write_repro_readme()
    write_manifest()


if __name__ == "__main__":
    main()
