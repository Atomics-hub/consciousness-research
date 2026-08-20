#!/usr/bin/env python3
"""Create or verify the self-excluding Paper 8 Stage-1 release manifest."""

from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "paper8_stage1_release_manifest.sha256"
LINE = re.compile(r"^([0-9a-f]{64})  ([^\r\n]+)$")


def forbidden(relative: PurePosixPath) -> bool:
    parts = set(relative.parts)
    return bool(
        parts & {"subscription_calibration", "paper8_external_lanes", "records", "transcripts"}
        or relative.name.endswith("_raw.json")
        or relative.name.endswith("_response.md")
        or relative.name == "events.jsonl"
    )


def release_files() -> dict[str, Path]:
    files: dict[str, Path] = {}
    for path in ROOT.rglob("*"):
        if path.is_symlink():
            raise RuntimeError(f"symlink forbidden: {path}")
        if not path.is_file() or path == MANIFEST:
            continue
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        relative = PurePosixPath(path.relative_to(ROOT).as_posix())
        if forbidden(relative):
            raise RuntimeError(f"private/raw path forbidden: {relative}")
        files[relative.as_posix()] = path
    return dict(sorted(files.items()))


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def canonical_manifest() -> str:
    return "".join(f"{digest(path)}  {relative}\n" for relative, path in release_files().items())


def verify() -> None:
    expected = canonical_manifest()
    actual = MANIFEST.read_text(encoding="utf-8")
    if actual != expected:
        raise RuntimeError("release manifest is stale or malformed")
    lines = actual.splitlines()
    if any(LINE.fullmatch(line) is None for line in lines):
        raise RuntimeError("release manifest contains a malformed row")
    print(f"PASS release seal: {len(lines)} files")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true")
    arguments = parser.parse_args()
    try:
        if arguments.verify:
            verify()
        else:
            rendered = canonical_manifest()
            MANIFEST.write_text(rendered, encoding="utf-8", newline="\n")
            print(f"WROTE release seal: {len(rendered.splitlines())} files")
    except (OSError, RuntimeError, UnicodeError) as error:
        print(f"FAIL release seal: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
