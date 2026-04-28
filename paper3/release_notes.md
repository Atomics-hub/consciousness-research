# Paper 3 Release Notes

## Release

Tag: `paper3-v1.0.0`

Title: Paper 3 preprint v1.0.0 - PreservationBench AST v0

## Paper

**The Preservation Benchmark: Testing Functional Continuity Across Substrate Transfer**

This release packages the Paper 3 preprint and the code state used for the PreservationBench-AST v0 expanded core replication.

The paper introduces PreservationBench, a benchmark framework for testing preservation-relevant functional continuity after source state is copied, transplanted, adapted, or relearned in a target substrate. The AST v0 implementation is a toy neural-agent validation tier, not a consciousness test and not a personal-identity test.

## Core Result

The expanded core replication attempted 30 independent source seeds and retained 22 validated sources. The main result is a dissociation profile:

- frozen copied schema and self-model state preserved source-specific identity probes but did not recouple report or control
- source-alignment repair improved report but did not restore source-like control
- a source-facing attention bridge recovered report behavior without source-like action agreement
- a control bridge optimized reward and goal-attention proxy measures without restoring source-like control
- copied attention produced the strongest combined profile, but only by narrowing the substrate gap

## Included Assets

- `paper3/ryan_2026_preservation_benchmark_ast_v0.pdf`
- `paper3/manuscript.md`
- `paper3/figures/`
- `experiments/preservation_bench/`
- compact code/results artifact zip attached to the GitHub release

## Reproduction Entry Point

```bash
KMP_DUPLICATE_LIB_OK=TRUE OMP_NUM_THREADS=1 python3 \
  experiments/preservation_bench/run_ast_training_smoke.py \
  --config experiments/preservation_bench/configs/ast_competence_v2_core_30seed.json
```

The full local run directory is large and is not committed to git. The release artifact contains tracked code, configs, figures, and compact summary records sufficient to inspect the reported result.

## License

Creative Commons Attribution 4.0 International.
