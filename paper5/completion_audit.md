# Paper 5 Completion Audit

Audit date: June 16, 2026.

This audit checks whether the current Paper 5 package supports a bounded, evidence-backed causal-preservation claim rather than merely adding another PreservationBench stress test.

## Claim Ceiling

Supported claim:

> In a toy PreservationBench-AST substrate-transfer benchmark, copied source attention preserves source-specific causal response geometry under schema-state and attention-state interchange interventions better than behavior-only distillation and frozen random controls. The attention-state variable also passes a same-dimensional bidirectional target-to-source causal-role check.

Explicitly unsupported claims:

- consciousness;
- survival or personal identity;
- biological preservation;
- Attention Schema Theory truth;
- copied attention as sufficient preservation outside this toy architecture;
- general representation alignment.

## Requirement Audit

| Requirement | Evidence | Status |
| --- | --- | --- |
| Paper 5 is about causal preservation, not another AST stress test | `manuscript.md` frames source-specific interchange interventions; `evidence_gate.md` locks the causal-preservation claim. | Passed |
| Within-source patching works as positive control | Schema, attention, donor-action-mismatch, and bidirectional panels report `source_full` positive controls with 1.000 source-counterfactual agreement in the relevant cells. | Passed |
| Copied attention follows source counterfactuals above behavior distillation and frozen random | Schema action-mismatch: 0.689 vs 0.361 and 0.164. Attention action-mismatch: 0.864 vs 0.267 and 0.312. Bidirectional: 0.938 vs 0.210 and 0.199. | Passed |
| Behavior-only distillation can match ordinary behavior locally but fail causal intervention | Behavior-matched subsets: schema matched donors behavior 0.209 vs copied 0.626; attention matched donors behavior 0.108 vs copied 0.923. | Passed, bounded |
| Leakage and shortcut risks are audited honestly | `leakage_audit.md` documents stale-reference, unpatched-action, donor-B action, and donor-action-mismatch checks; manuscript reports the mixed donor-action-mismatch limitation. | Passed |
| Bidirectional/target-to-source gate is no longer only future work | `run_ast_bidirectional_patch_probe.py`, bidirectional configs, 704-row full run, Figures 8-9, Table 8, and Section 5.9 are present. | Passed |
| Concrete reproducible artifacts exist | Runner scripts, configs, run outputs, contrast reports, figures, manuscript, evidence gate, reproducibility checklist, and rendered PDF are present. | Passed |
| Claim ceiling avoids consciousness/survival/personal-identity claims | Manuscript, README, evidence gate, checklist, and release reminder explicitly deny those claims. | Passed |
| Release boundary is preserved | `release_reminder.md` states no public posting, Zenodo deposition, or GitHub release without explicit approval. | Passed |

## Main Result Anchors

Schema-state action-mismatch donors:

```text
copied_attention interchange_action=0.689 specificity_gap=0.549
behavior_distill interchange_action=0.361 specificity_gap=0.164
frozen_random    interchange_action=0.164 specificity_gap=-0.033
```

Attention-state action-mismatch donors:

```text
copied_attention interchange_action=0.864 specificity_gap=0.778
behavior_distill interchange_action=0.267 specificity_gap=0.006
frozen_random    interchange_action=0.312 specificity_gap=0.170
```

Bidirectional target-to-source attention patch:

```text
source_full       action_agreement=1.000 q_delta_error=0.0000
copied_attention action_agreement=0.938 q_delta_error=0.1642
behavior_distill action_agreement=0.210 q_delta_error=38.0626
frozen_random    action_agreement=0.199 q_delta_error=47.1765
```

## Current Verification

Latest local checks:

```text
py_compile_ok
json_ok files=23
schema_rows=1892
attention_rows=2108
attention_donor_action_mismatch_rows=1216
bidirectional_attention_rows=704
ascii_scan_ok files=9
pdf_pages=21
pdf_text_contains_table8_figure8_figure9
visual_render_check_ok_for_bidirectional_pages
stale_bidirectional_future_work_scan_ok
```

## Residual Risks

These are not claimed as solved in Paper 5:

- non-identity bidirectional alignment or learned stitching;
- stronger behavior-only baselines trained on richer ordinary trajectories while withholding intervention labels;
- larger source panels or independent master seeds;
- causal variables beyond schema-state and attention-state activations.

The current paper is therefore complete as a bounded toy benchmark result, not as a general preservation theory.
