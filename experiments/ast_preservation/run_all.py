#!/usr/bin/env python3
"""Run all four phases of the experiment sequentially."""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def run_phase(name, module_name):
    print(f"\n{'#' * 60}")
    print(f"# {name}")
    print(f"{'#' * 60}\n")

    start = time.time()
    module = __import__(module_name)
    module.main()
    elapsed = time.time() - start
    print(f"\n{name} completed in {elapsed:.1f}s")
    return elapsed


def main():
    total_start = time.time()

    # Phase 1-4 must run sequentially (each depends on previous)
    times = {}

    import run_phase1_train
    start = time.time()
    run_phase1_train.main()
    times["Phase 1: Training"] = time.time() - start

    import run_phase2_ablation
    start = time.time()
    run_phase2_ablation.main()
    times["Phase 2: Ablation"] = time.time() - start

    import run_phase3_transplant
    start = time.time()
    run_phase3_transplant.main()
    times["Phase 3: Transplant"] = time.time() - start

    import run_phase4_iit
    start = time.time()
    run_phase4_iit.main()
    times["Phase 4: Phi-star side analysis"] = time.time() - start

    total = time.time() - total_start

    print("\n" + "=" * 60)
    print("ALL PHASES COMPLETE")
    print("=" * 60)
    for phase, t in times.items():
        print(f"  {phase}: {t:.1f}s")
    print(f"  Total: {total:.1f}s")
    print(f"\nResults in: experiments/ast_preservation/results/")
    print("Next: run analysis/generate_figures.py, then paper2/build_pdf.py")


if __name__ == "__main__":
    main()
