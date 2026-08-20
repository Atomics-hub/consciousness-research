#!/usr/bin/env python3
"""Run or byte-check the isolated non-gating dependence diagnostic."""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import time

from dependence_diagnostics import (
    DEFAULT_FORMATION_REPLICATES,
    DEFAULT_OUTCOME_REPLICATES,
    run_diagnostics,
    serialize_result,
)


ROOT = Path(__file__).resolve().parent
RESULT_PATH = ROOT / "results" / "dependence_diagnostics.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--outcome-replicates",
        type=int,
        default=DEFAULT_OUTCOME_REPLICATES,
    )
    parser.add_argument(
        "--formation-replicates",
        type=int,
        default=DEFAULT_FORMATION_REPLICATES,
    )
    parser.add_argument("--chunk-size", type=int, default=32)
    parser.add_argument(
        "--check",
        action="store_true",
        help="recompute and compare with the stored bytes without writing",
    )
    arguments = parser.parse_args()

    started = time.perf_counter()
    result = run_diagnostics(
        outcome_replicates=arguments.outcome_replicates,
        formation_replicates=arguments.formation_replicates,
        chunk_size=arguments.chunk_size,
    )
    serialized = serialize_result(result)
    digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    elapsed = time.perf_counter() - started

    if arguments.check:
        if not RESULT_PATH.is_file() or RESULT_PATH.is_symlink():
            raise SystemExit("stored diagnostic result is missing or unsafe")
        stored = RESULT_PATH.read_text(encoding="utf-8")
        if stored != serialized:
            raise SystemExit("stored diagnostic result differs from deterministic replay")
        print(
            f"PASS dependence diagnostic replay: sha256={digest} "
            f"elapsed_seconds={elapsed:.3f}"
        )
        return 0

    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary = RESULT_PATH.with_name(RESULT_PATH.name + ".tmp")
    try:
        temporary.write_text(serialized, encoding="utf-8")
        os.replace(temporary, RESULT_PATH)
    finally:
        temporary.unlink(missing_ok=True)
    print(
        f"wrote {RESULT_PATH} sha256={digest} elapsed_seconds={elapsed:.3f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
