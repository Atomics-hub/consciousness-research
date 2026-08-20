#!/usr/bin/env python3
"""Build a deterministic, sanitized Paper 8 public release candidate."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
import zipfile
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parent
REPOSITORY = ROOT.parents[1]
RELEASE = REPOSITORY / "outputs" / "paper8_public_release_v1.0.0"
SOURCE_PDF = (
    REPOSITORY / "output" / "pdf" / "paper8_binding_test_methods_feasibility_v0.pdf"
)
PUBLIC_PDF = "ryan_2026_binding_test_methods_feasibility.pdf"
PUBLIC_ZIP = "paper8_reproducibility_package_v1.0.0.zip"
CATALOG_SHA256 = "ecca512d04dfe81f743cd1538798b9f4bb0fbe5b2b88c96647ffeb4a2ce0b80e"
FIXED_ZIP_TIME = (2026, 8, 19, 0, 0, 0)

SEALED_ROOTS = (
    (REPOSITORY / "zero_call", "zero_call_manifest.sha256"),
    (
        REPOSITORY / "outputs" / "paper8_stage1_release_v0",
        "paper8_stage1_release_manifest.sha256",
    ),
    (
        REPOSITORY / "outputs" / "paper8_stage10_claude_cli_observation_v0",
        "paper8_stage10_claude_cli_observation_manifest.sha256",
    ),
    (
        REPOSITORY / "outputs" / "paper8_stage11_ws01_sonnet_feasibility_v0",
        "paper8_stage11_ws01_sonnet_feasibility_manifest.sha256",
    ),
    (ROOT, "paper8_methods_feasibility_preprint_manifest.sha256"),
)

FORBIDDEN_PATTERNS = (
    re.compile(rb"/" + rb"Users/"),
    re.compile(rb"sk-" + rb"(?:ant|proj)-[A-Za-z0-9_-]{12,}"),
    re.compile(rb"ghp" + rb"_[A-Za-z0-9]{20,}"),
    re.compile(rb"github" + rb"_pat_[A-Za-z0-9_]{20,}"),
    re.compile(rb"AK" + rb"IA[0-9A-Z]{16}"),
    re.compile(rb"-----BEGIN " + rb"[A-Z ]*PRIVATE KEY-----"),
    re.compile(rb"Authorization:" + rb"\s*Bearer\s+", re.IGNORECASE),
    re.compile(rb'"access_' + rb'token"\s*:\s*"[^" ]+"', re.IGNORECASE),
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def parse_manifest(root: Path, name: str) -> list[Path]:
    manifest = root / name
    if not manifest.is_file() or manifest.is_symlink():
        raise RuntimeError(f"invalid manifest: {manifest}")
    payloads: list[Path] = []
    for line in manifest.read_text(encoding="ascii").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  ([A-Za-z0-9_./-]+)", line)
        if match is None:
            raise RuntimeError(f"malformed manifest row: {manifest}")
        expected, relative = match.groups()
        pure = PurePosixPath(relative)
        if pure.is_absolute() or ".." in pure.parts or "\\" in relative:
            raise RuntimeError(f"unsafe manifest path: {relative}")
        path = root.joinpath(*pure.parts)
        if not path.is_file() or path.is_symlink():
            raise RuntimeError(f"invalid manifested file: {path}")
        mode = path.stat().st_mode
        if not stat.S_ISREG(mode) or path.stat().st_nlink != 1:
            raise RuntimeError(f"nonregular or linked payload: {path}")
        if sha256_file(path) != expected:
            raise RuntimeError(f"manifest digest mismatch: {path}")
        payloads.append(path)
    if len(payloads) != len(set(payloads)):
        raise RuntimeError(f"duplicate manifest path: {manifest}")
    return payloads + [manifest]


def archive_name(path: Path) -> str:
    relative = path.relative_to(REPOSITORY)
    return relative.as_posix()


def collect_payloads() -> list[tuple[str, bytes]]:
    collected: dict[str, bytes] = {}
    for root, manifest_name in SEALED_ROOTS:
        for path in parse_manifest(root, manifest_name):
            collected[archive_name(path)] = path.read_bytes()

    catalog = REPOSITORY / "binding_calibration" / "frozen_prompt_catalog.json"
    if not catalog.is_file() or catalog.is_symlink():
        raise RuntimeError("frozen prompt catalog missing")
    catalog_bytes = catalog.read_bytes()
    if sha256_bytes(catalog_bytes) != CATALOG_SHA256:
        raise RuntimeError("frozen prompt catalog digest mismatch")
    collected[archive_name(catalog)] = catalog_bytes

    for name, data in collected.items():
        for pattern in FORBIDDEN_PATTERNS:
            if pattern.search(data):
                raise RuntimeError(f"forbidden public-release content in {name}")

    return sorted(collected.items())


def write_zip(path: Path, payloads: list[tuple[str, bytes]]) -> None:
    temporary = path.with_suffix(".tmp")
    with zipfile.ZipFile(
        temporary,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
        strict_timestamps=True,
    ) as archive:
        for name, data in payloads:
            info = zipfile.ZipInfo(name, FIXED_ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o100644 & 0xFFFF) << 16
            info.create_system = 3
            archive.writestr(info, data)
    os.replace(temporary, path)


def main() -> int:
    if not SOURCE_PDF.is_file() or SOURCE_PDF.is_symlink():
        raise RuntimeError("rendered public PDF is missing")
    RELEASE.mkdir(parents=True, exist_ok=True)
    for child in RELEASE.iterdir():
        if child.is_file() and child.name in {
            PUBLIC_PDF,
            PUBLIC_ZIP,
            "SHA256SUMS",
            "UPLOAD_FILES.txt",
            "zenodo_metadata.json",
            "ZENODO_METADATA.md",
        }:
            child.unlink()

    public_pdf = RELEASE / PUBLIC_PDF
    shutil.copyfile(SOURCE_PDF, public_pdf)
    payloads = collect_payloads()
    public_zip = RELEASE / PUBLIC_ZIP
    write_zip(public_zip, payloads)

    shutil.copyfile(ROOT / "zenodo_metadata.json", RELEASE / "zenodo_metadata.json")
    shutil.copyfile(ROOT / "ZENODO_METADATA.md", RELEASE / "ZENODO_METADATA.md")
    upload_files = f"{PUBLIC_PDF}\n{PUBLIC_ZIP}\n"
    (RELEASE / "UPLOAD_FILES.txt").write_text(upload_files, encoding="ascii")

    sums = {
        PUBLIC_PDF: sha256_file(public_pdf),
        PUBLIC_ZIP: sha256_file(public_zip),
        "ZENODO_METADATA.md": sha256_file(RELEASE / "ZENODO_METADATA.md"),
        "zenodo_metadata.json": sha256_file(RELEASE / "zenodo_metadata.json"),
    }
    lines = [f"{digest}  {name}" for name, digest in sorted(sums.items())]
    (RELEASE / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="ascii")

    metadata = json.loads((RELEASE / "zenodo_metadata.json").read_text())
    if metadata["upload_files"] != [PUBLIC_PDF, PUBLIC_ZIP]:
        raise RuntimeError("metadata upload inventory mismatch")

    print("STATUS PUBLIC_RELEASE_CANDIDATE_BUILT_DOI_RESERVED")
    print(f"PDF_SHA256 {sums[PUBLIC_PDF]}")
    print(f"ZIP_SHA256 {sums[PUBLIC_ZIP]}")
    print(f"ZIP_PAYLOADS {len(payloads)}")
    print(f"RELEASE_DIRECTORY {RELEASE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
