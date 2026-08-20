#!/usr/bin/env python3
"""Create or verify the self-excluding SHA-256 manifest for zero_call/."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "zero_call_manifest.sha256"


def package_files() -> tuple[Path, ...]:
    return tuple(
        sorted(
            (
                path
                for path in ROOT.rglob("*")
                if path.is_file()
                and path != MANIFEST
                and "__pycache__" not in path.parts
                and path.suffix != ".pyc"
            ),
            key=lambda path: path.relative_to(ROOT).as_posix(),
        )
    )


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def create() -> None:
    lines = [
        f"{digest(path)}  {path.relative_to(ROOT).as_posix()}"
        for path in package_files()
    ]
    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"sealed {len(lines)} files in {MANIFEST}")


def verify() -> bool:
    expected = {}
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        checksum, relative = line.split("  ", 1)
        if relative in expected:
            raise ValueError(f"duplicate manifest path: {relative}")
        expected[relative] = checksum
    actual_paths = {path.relative_to(ROOT).as_posix(): path for path in package_files()}
    missing = sorted(set(expected) - set(actual_paths))
    extra = sorted(set(actual_paths) - set(expected))
    mismatched = sorted(
        relative
        for relative in set(expected) & set(actual_paths)
        if digest(actual_paths[relative]) != expected[relative]
    )
    ok = not missing and not extra and not mismatched
    print(
        f"verify={ok} entries={len(expected)} missing={len(missing)} "
        f"extra={len(extra)} mismatched={len(mismatched)}"
    )
    if not ok:
        print(f"missing={missing}")
        print(f"extra={extra}")
        print(f"mismatched={mismatched}")
    return ok


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    arguments = parser.parse_args()
    if arguments.verify:
        return 0 if verify() else 1
    create()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
