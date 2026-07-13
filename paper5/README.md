# Paper 5: Causal Preservation Under Substrate Transfer

Published preprint package for the fifth consciousness-preservation paper.

**Title:** Causal Preservation Under Substrate Transfer: Interchange Intervention Tests for Source-Specific Functional Continuity

**Status:** published on Zenodo, not yet peer reviewed

**Zenodo DOI:** https://doi.org/10.5281/zenodo.20852042

**GitHub release snapshot:** https://github.com/Atomics-hub/consciousness-research/releases/tag/paper5-v1.0.0

## Claim

In a toy PreservationBench-AST substrate-transfer benchmark, copied source attention preserves source-specific causal response geometry under schema-state and attention-state interchange interventions better than behavior-only distillation and frozen random controls. A bidirectional attention-state follow-up shows that copied-attention target activations can substitute back into the source far better than behavior-only or frozen-random target activations.

This is a bounded benchmark result. It does not measure consciousness, personal identity, survival, biological preservation, or whether Attention Schema Theory is true.

## Main Artifacts

- `manuscript.md`: current Paper 5 draft.
- `ryan_2026_causal_preservation_under_substrate_transfer.pdf`: Zenodo-ready preprint PDF.
- `evidence_gate.md`: claim lock, proof status, and remaining kill tests.
- `completion_audit.md`: requirement-by-requirement completion and claim-ceiling audit.
- `citation_audit.md`: checked bibliography trail and source URLs.
- `leakage_audit.md`: shortcut/leakage interpretation audit over the full panels.
- `causal_patching_smoke.md`: experiment log and interpretation trail.
- `reproducibility_checklist.md`: commands and expected checks for the full-panel runs.
- `release_reminder.md`: internal readiness-review reminder and release gate.
- `release_notes.md`: GitHub release notes draft for `paper5-v1.0.0`.
- `release_manifest.md`: scoped files intended for a clean Paper 5 release snapshot.
- `zenodo_metadata.md`: Zenodo form metadata.
- `zenodo_upload_checklist.md`: manual upload checklist.
- `render_manuscript_pdf.py`: local ReportLab renderer for review PDFs.
- `../output/pdf/paper5_causal_preservation_draft.pdf`: current rendered review PDF.
- `figures/`: schema-state figures.
- `figures/attention_state/`: attention-state figures.
- `figures/attention_state_donor_action_mismatch/`: hard donor-action decoupling figure.
- `figures/bidirectional_attention/`: target-to-source attention-patching figures.

## Main Runs

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

Bidirectional attention-state panel:

```bash
KMP_DUPLICATE_LIB_OK=TRUE OMP_NUM_THREADS=1 python3 -B \
  experiments/preservation_bench/run_ast_bidirectional_patch_probe.py \
  --config experiments/preservation_bench/configs/ast_bidirectional_patch_attention_state_full22.json
```

## Key Results

Schema-state action-mismatch donors:

```text
copied attention:  interchange_action=0.689 specificity_gap=0.549
behavior distill:  interchange_action=0.361 specificity_gap=0.164
frozen random:     interchange_action=0.164 specificity_gap=-0.033
```

Attention-state action-mismatch donors:

```text
copied attention:  interchange_action=0.864 specificity_gap=0.778
behavior distill:  interchange_action=0.267 specificity_gap=0.006
frozen random:     interchange_action=0.312 specificity_gap=0.170
```

Attention-state donor-action-mismatch follow-up:

```text
copied attention:  interchange_action=0.406 q_delta_error=0.1386
behavior distill:  interchange_action=0.234 q_delta_error=89.4973
frozen random:     interchange_action=0.297 q_delta_error=34.8843
```

Bidirectional target-to-source attention follow-up:

```text
copied attention:  action_agreement=0.938 q_delta_error=0.1642
behavior distill:  action_agreement=0.210 q_delta_error=38.0626
frozen random:     action_agreement=0.199 q_delta_error=47.1765
```

Behavior-matched subset check:

```text
schema matched donors:    behavior=0.209 copied_attention=0.626
attention matched donors: behavior=0.108 copied_attention=0.923
```

These subset rows keep only cases where behavior distillation matches the ordinary source-A action, then test whether it follows the source counterfactual under intervention.

## Publication

Published on Zenodo: June 25, 2026.

Record URL: https://zenodo.org/records/20852042

The Zenodo record lists `paper5-v1.0.0` as the supplementary GitHub release snapshot:

https://github.com/Atomics-hub/consciousness-research/releases/tag/paper5-v1.0.0

## Release Snapshot

The release snapshot preserves the scoped Paper 5 files listed in `release_manifest.md`, including the preprint PDF, causal-patching scripts, run configs, compact result artifacts, figures, and release notes.

Non-identity alignment, stronger behavior-only baselines, larger source pools, and additional causal variables are future robustness tests. They are not claimed as completed here.
