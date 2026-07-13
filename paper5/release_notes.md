# Paper 5 Release Notes

## Release

Tag: `paper5-v1.0.0`

Title: Paper 5 preprint v1.0.0 - Causal preservation under substrate transfer

## Paper

**Causal Preservation Under Substrate Transfer: Interchange Intervention Tests for Source-Specific Functional Continuity**

Zenodo DOI: https://doi.org/10.5281/zenodo.20852042

This release packages the Paper 5 preprint and the code/results state used for the PreservationBench-AST causal-patching and bidirectional attention-state intervention suite.

The paper asks whether copied-attention transfer preserves behaviorally relevant source-causal mechanisms, or only matches behavior/report surfaces. The benchmark remains a toy functional benchmark. It is not a consciousness test, personal-identity test, survival claim, biological preservation claim, Attention Schema Theory truth claim, or whole-agent equivalence result.

## Core Result

The main result is a bounded causal-preservation profile across schema-state, attention-state, donor-action-mismatch, and bidirectional target-to-source intervention panels.

- schema-state action-mismatch donors: copied attention reaches 0.689 donor-specific action agreement with a 0.549 specificity gap; behavior distillation reaches 0.361 and 0.164; frozen random reaches 0.164 and -0.033
- attention-state action-mismatch donors: copied attention reaches 0.864 donor-specific action agreement with a 0.778 specificity gap; behavior distillation reaches 0.267 and 0.006; frozen random reaches 0.312 and 0.170
- behavior-matched subset checks: behavior distillation can match ordinary source-A action locally while failing causal intervention; schema matched rows are 0.209 behavior vs 0.626 copied attention, and attention matched rows are 0.108 behavior vs 0.923 copied attention
- donor-action-mismatch follow-up: copied attention keeps a strong Q-geometry advantage under source-counterfactual/donor-action decoupling, while its discrete action advantage is modest and explicitly limited
- bidirectional target-to-source attention patch: copied-attention target-B activations recover the source counterfactual action in 0.938 of rows, compared with 0.210 for behavior distillation and 0.199 for frozen random

The result supports the bounded conclusion that causal intervention tests can distinguish source-specific mechanism preservation from ordinary behavior matching in this toy benchmark.

## Included Assets

- `paper5/ryan_2026_causal_preservation_under_substrate_transfer.pdf`
- `paper5/manuscript.md`
- `paper5/figures/`
- `paper5/README.md`
- `paper5/evidence_gate.md`
- `paper5/completion_audit.md`
- `paper5/citation_audit.md`
- `paper5/leakage_audit.md`
- `paper5/causal_patching_smoke.md`
- `paper5/reproducibility_checklist.md`
- `paper5/zenodo_metadata.md`
- `experiments/preservation_bench/`

## Reproduction Entry Points

Schema-state full panel:

```bash
KMP_DUPLICATE_LIB_OK=TRUE OMP_NUM_THREADS=1 python3 -B \
  experiments/preservation_bench/run_ast_causal_patch_probe.py \
  --config experiments/preservation_bench/configs/ast_causal_patch_schema_state_action_mismatch_full22.json
```

Attention-state full panel:

```bash
KMP_DUPLICATE_LIB_OK=TRUE OMP_NUM_THREADS=1 python3 -B \
  experiments/preservation_bench/run_ast_causal_patch_probe.py \
  --config experiments/preservation_bench/configs/ast_causal_patch_attention_state_action_mismatch_full22.json
```

Attention-state donor-action-mismatch follow-up:

```bash
KMP_DUPLICATE_LIB_OK=TRUE OMP_NUM_THREADS=1 python3 -B \
  experiments/preservation_bench/run_ast_causal_patch_probe.py \
  --config experiments/preservation_bench/configs/ast_causal_patch_attention_state_donor_action_mismatch_full22.json
```

Bidirectional attention-state panel:

```bash
KMP_DUPLICATE_LIB_OK=TRUE OMP_NUM_THREADS=1 python3 -B \
  experiments/preservation_bench/run_ast_bidirectional_patch_probe.py \
  --config experiments/preservation_bench/configs/ast_bidirectional_patch_attention_state_full22.json
```

See `paper5/reproducibility_checklist.md` for analyzers, figures, row counts, and expected checks.

## License

Creative Commons Attribution 4.0 International.
