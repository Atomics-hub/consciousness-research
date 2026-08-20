#!/usr/bin/env python3
"""Verify the generated Paper 8 DOI-reserved public release candidate."""

from __future__ import annotations

import hashlib
import json
import re
import zipfile
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parent
REPOSITORY = ROOT.parents[1]
RELEASE = REPOSITORY / "outputs" / "paper8_public_release_v1.0.0"
PUBLIC_PDF = "ryan_2026_binding_test_methods_feasibility.pdf"
PUBLIC_ZIP = "paper8_reproducibility_package_v1.0.0.zip"
EXPECTED_FILES = {
    PUBLIC_PDF,
    PUBLIC_ZIP,
    "SHA256SUMS",
    "UPLOAD_FILES.txt",
    "ZENODO_METADATA.md",
    "zenodo_metadata.json",
}
FORBIDDEN_PATTERNS = (
    re.compile(rb"/" + rb"Users/"),
    re.compile(rb"sk-" + rb"(?:ant|proj)-[A-Za-z0-9_-]{12,}"),
    re.compile(rb"ghp" + rb"_[A-Za-z0-9]{20,}"),
    re.compile(rb"github" + rb"_pat_[A-Za-z0-9_]{20,}"),
    re.compile(rb"AK" + rb"IA[0-9A-Z]{16}"),
    re.compile(rb"-----BEGIN " + rb"[A-Z ]*PRIVATE KEY-----"),
    re.compile(rb"Authorization:" + rb"\s*Bearer\s+", re.IGNORECASE),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    actual = {path.name for path in RELEASE.iterdir() if path.is_file()}
    if actual != EXPECTED_FILES:
        raise RuntimeError(f"public release closure mismatch: {sorted(actual)}")
    if any(path.is_symlink() for path in RELEASE.iterdir()):
        raise RuntimeError("public release contains a symlink")

    sums: dict[str, str] = {}
    for line in (RELEASE / "SHA256SUMS").read_text(encoding="ascii").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  ([A-Za-z0-9_.-]+)", line)
        if match is None:
            raise RuntimeError("malformed SHA256SUMS row")
        digest, name = match.groups()
        sums[name] = digest
    for name, expected in sums.items():
        if sha256(RELEASE / name) != expected:
            raise RuntimeError(f"public release digest mismatch: {name}")

    pdf = (RELEASE / PUBLIC_PDF).read_bytes()
    if not pdf.startswith(b"%PDF-") or len(pdf) < 50_000:
        raise RuntimeError("public PDF structure or size invalid")

    zip_path = RELEASE / PUBLIC_ZIP
    with zipfile.ZipFile(zip_path) as archive:
        names = archive.namelist()
        if names != sorted(names) or len(names) != len(set(names)):
            raise RuntimeError("archive inventory is not sorted and unique")
        required_prefixes = {
            "zero_call/",
            "outputs/paper8_stage1_release_v0/",
            "outputs/paper8_stage10_claude_cli_observation_v0/",
            "outputs/paper8_stage11_ws01_sonnet_feasibility_v0/",
            "outputs/paper8_methods_feasibility_preprint_v0/",
            "binding_calibration/frozen_prompt_catalog.json",
        }
        for required in required_prefixes:
            if required.endswith("/") and not any(
                name.startswith(required) for name in names
            ):
                raise RuntimeError(f"archive prefix missing: {required}")
            if not required.endswith("/") and required not in names:
                raise RuntimeError(f"archive payload missing: {required}")
        for name in names:
            pure = PurePosixPath(name)
            if pure.is_absolute() or ".." in pure.parts or name.endswith("/"):
                raise RuntimeError(f"unsafe archive path: {name}")
            data = archive.read(name)
            for pattern in FORBIDDEN_PATTERNS:
                if pattern.search(data):
                    raise RuntimeError(f"forbidden archive content: {name}")

    metadata = json.loads((RELEASE / "zenodo_metadata.json").read_text())
    if metadata["creators"] != [
        {
            "family_name": "Ryan",
            "given_names": "Thomas",
            "role": "Researcher",
            "affiliation": "Independent Researcher, San Francisco, CA",
        }
    ]:
        raise RuntimeError("creator metadata drift")
    if (
        metadata["doi"] != "10.5281/zenodo.22020047"
        or metadata["status"] != "upload-ready-doi-reserved"
    ):
        raise RuntimeError("unexpected DOI state")
    if metadata["external_causal_result"] is not False:
        raise RuntimeError("causal-result ceiling drift")

    print("STATUS PASS_PUBLIC_RELEASE_CANDIDATE_DOI_RESERVED")
    print(f"PDF_SHA256 {sums[PUBLIC_PDF]}")
    print(f"ZIP_SHA256 {sums[PUBLIC_ZIP]}")
    print(f"ZIP_PAYLOADS {len(names)}")
    print("UPLOAD_FILES 2")
    print("DOI_RESERVED true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
