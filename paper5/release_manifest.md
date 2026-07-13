# Paper 5 Release Manifest

This manifest lists the scoped Paper 5 files intended for a clean `paper5-v1.0.0` GitHub release snapshot.

Zenodo record is already published:

- Version DOI: https://doi.org/10.5281/zenodo.20852042
- Record URL: https://zenodo.org/records/20852042

Do not create a public release from the current dirty worktree without staging only the intended Paper 5 files.

## Zenodo Preprint File

- `paper5/ryan_2026_causal_preservation_under_substrate_transfer.pdf`

## Paper 5 Documentation

- `paper5/README.md`
- `paper5/manuscript.md`
- `paper5/research_plan.md`
- `paper5/evidence_gate.md`
- `paper5/completion_audit.md`
- `paper5/citation_audit.md`
- `paper5/leakage_audit.md`
- `paper5/causal_patching_smoke.md`
- `paper5/reproducibility_checklist.md`
- `paper5/release_notes.md`
- `paper5/release_reminder.md`
- `paper5/zenodo_metadata.md`
- `paper5/zenodo_upload_checklist.md`
- `paper5/render_manuscript_pdf.py`
- `paper5/figures/`

## Experiment Code

- `experiments/preservation_bench/run_ast_causal_patch_probe.py`
- `experiments/preservation_bench/run_ast_bidirectional_patch_probe.py`
- `experiments/preservation_bench/analyze_causal_patch_contrasts.py`
- `experiments/preservation_bench/analyze_causal_patch_behavior_matched.py`
- `experiments/preservation_bench/analyze_causal_patch_leakage.py`
- `experiments/preservation_bench/analyze_bidirectional_patch_contrasts.py`
- `experiments/preservation_bench/plot_causal_patch_results.py`
- `experiments/preservation_bench/plot_causal_patch_donor_action_mismatch.py`
- `experiments/preservation_bench/plot_bidirectional_patch_results.py`

## Configs

- `experiments/preservation_bench/configs/ast_causal_patch_schema_state_action_mismatch_full22.json`
- `experiments/preservation_bench/configs/ast_causal_patch_attention_state_action_mismatch_full22.json`
- `experiments/preservation_bench/configs/ast_causal_patch_attention_state_donor_action_mismatch_full22.json`
- `experiments/preservation_bench/configs/ast_bidirectional_patch_attention_state_smoke.json`
- `experiments/preservation_bench/configs/ast_bidirectional_patch_attention_state_full22.json`

## Compact Result Runs

- `experiments/preservation_bench/runs/ast_causal_patch_schema_state_action_mismatch_full22/`
- `experiments/preservation_bench/runs/ast_causal_patch_attention_state_action_mismatch_full22/`
- `experiments/preservation_bench/runs/ast_causal_patch_attention_state_donor_action_mismatch_full22/`
- `experiments/preservation_bench/runs/ast_bidirectional_patch_attention_state_full22/`

Current local sizes:

```text
paper5: 2.4M
schema full run: 4.6M
attention full run: 5.2M
attention donor-action-mismatch run: 3.0M
bidirectional attention run: 1.4M
```

## Suggested Scoped Staging Command

```bash
git add \
  paper5 \
  experiments/preservation_bench/run_ast_causal_patch_probe.py \
  experiments/preservation_bench/run_ast_bidirectional_patch_probe.py \
  experiments/preservation_bench/analyze_causal_patch_contrasts.py \
  experiments/preservation_bench/analyze_causal_patch_behavior_matched.py \
  experiments/preservation_bench/analyze_causal_patch_leakage.py \
  experiments/preservation_bench/analyze_bidirectional_patch_contrasts.py \
  experiments/preservation_bench/plot_causal_patch_results.py \
  experiments/preservation_bench/plot_causal_patch_donor_action_mismatch.py \
  experiments/preservation_bench/plot_bidirectional_patch_results.py \
  experiments/preservation_bench/configs/ast_causal_patch_schema_state_action_mismatch_full22.json \
  experiments/preservation_bench/configs/ast_causal_patch_attention_state_action_mismatch_full22.json \
  experiments/preservation_bench/configs/ast_causal_patch_attention_state_donor_action_mismatch_full22.json \
  experiments/preservation_bench/configs/ast_bidirectional_patch_attention_state_smoke.json \
  experiments/preservation_bench/configs/ast_bidirectional_patch_attention_state_full22.json \
  experiments/preservation_bench/runs/ast_causal_patch_schema_state_action_mismatch_full22 \
  experiments/preservation_bench/runs/ast_causal_patch_attention_state_action_mismatch_full22 \
  experiments/preservation_bench/runs/ast_causal_patch_attention_state_donor_action_mismatch_full22 \
  experiments/preservation_bench/runs/ast_bidirectional_patch_attention_state_full22
```

## Suggested Release Flow

1. Stage only the files in this manifest.
2. Commit with a Paper 5 release message.
3. Push the branch.
4. Create tag `paper5-v1.0.0`.
5. Create a GitHub release using `paper5/release_notes.md`.
6. Confirm the Zenodo supplementary URL resolves to the new release.
