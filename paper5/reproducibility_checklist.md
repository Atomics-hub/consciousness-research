# Paper 5 Reproducibility Checklist

Working checklist for the Paper 5 causal-preservation draft.

This checklist supports a bounded toy benchmark claim only. It does not support claims about consciousness, survival, personal identity, biological preservation, or AST truth.

## Source Run

Validated source checkpoint root:

```text
experiments/preservation_bench/runs/ast_competence_v2_core_10seed
```

Validated train seed indices used by the causal-patching full panels:

```text
0, 1, 2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 20, 21, 25, 26, 27, 28
```

## Schema-State Full Panel

Run:

```bash
KMP_DUPLICATE_LIB_OK=TRUE OMP_NUM_THREADS=1 python3 -B \
  experiments/preservation_bench/run_ast_causal_patch_probe.py \
  --config experiments/preservation_bench/configs/ast_causal_patch_schema_state_action_mismatch_full22.json
```

Analyze:

```bash
python3 experiments/preservation_bench/analyze_causal_patch_contrasts.py \
  experiments/preservation_bench/runs/ast_causal_patch_schema_state_action_mismatch_full22/causal_patch_rows.jsonl \
  --output-json experiments/preservation_bench/runs/ast_causal_patch_schema_state_action_mismatch_full22/causal_patch_contrasts.json \
  --output-md experiments/preservation_bench/runs/ast_causal_patch_schema_state_action_mismatch_full22/causal_patch_contrasts.md

python3 experiments/preservation_bench/analyze_causal_patch_behavior_matched.py \
  experiments/preservation_bench/runs/ast_causal_patch_schema_state_action_mismatch_full22/causal_patch_rows.jsonl \
  --output-json experiments/preservation_bench/runs/ast_causal_patch_schema_state_action_mismatch_full22/behavior_matched_subsets.json \
  --output-md experiments/preservation_bench/runs/ast_causal_patch_schema_state_action_mismatch_full22/behavior_matched_subsets.md

python3 experiments/preservation_bench/analyze_causal_patch_leakage.py \
  experiments/preservation_bench/runs/ast_causal_patch_schema_state_action_mismatch_full22/causal_patch_rows.jsonl \
  --output-json experiments/preservation_bench/runs/ast_causal_patch_schema_state_action_mismatch_full22/leakage_audit.json \
  --output-md experiments/preservation_bench/runs/ast_causal_patch_schema_state_action_mismatch_full22/leakage_audit.md
```

Plot:

```bash
python3 experiments/preservation_bench/plot_causal_patch_results.py \
  --contrasts experiments/preservation_bench/runs/ast_causal_patch_schema_state_action_mismatch_full22/causal_patch_contrasts.json \
  --rows experiments/preservation_bench/runs/ast_causal_patch_schema_state_action_mismatch_full22/causal_patch_rows.jsonl \
  --output-dir paper5/figures
```

Expected checks:

- `causal_patch_rows.jsonl` has 1,892 rows.
- Matched donor copied-attention interchange action agreement is 0.642.
- Action-mismatch copied-attention specificity gap is 0.549.
- Action-mismatch copied-attention minus behavior-distill paired action delta is 0.324 with 95% bootstrap CI [0.182, 0.473].
- On behavior-distill ordinary-action-matched schema rows, matched-donor causal action agreement is 0.209 for behavior distillation and 0.626 for copied attention.
- On schema action-mismatch rows where donor source-B action differs from the source counterfactual action, copied attention has source-counterfactual agreement 0.627 versus donor-B action agreement 0.194.

## Attention-State Full Panel

Run:

```bash
KMP_DUPLICATE_LIB_OK=TRUE OMP_NUM_THREADS=1 python3 -B \
  experiments/preservation_bench/run_ast_causal_patch_probe.py \
  --config experiments/preservation_bench/configs/ast_causal_patch_attention_state_action_mismatch_full22.json
```

Analyze:

```bash
python3 experiments/preservation_bench/analyze_causal_patch_contrasts.py \
  experiments/preservation_bench/runs/ast_causal_patch_attention_state_action_mismatch_full22/causal_patch_rows.jsonl \
  --output-json experiments/preservation_bench/runs/ast_causal_patch_attention_state_action_mismatch_full22/causal_patch_contrasts.json \
  --output-md experiments/preservation_bench/runs/ast_causal_patch_attention_state_action_mismatch_full22/causal_patch_contrasts.md

python3 experiments/preservation_bench/analyze_causal_patch_behavior_matched.py \
  experiments/preservation_bench/runs/ast_causal_patch_attention_state_action_mismatch_full22/causal_patch_rows.jsonl \
  --output-json experiments/preservation_bench/runs/ast_causal_patch_attention_state_action_mismatch_full22/behavior_matched_subsets.json \
  --output-md experiments/preservation_bench/runs/ast_causal_patch_attention_state_action_mismatch_full22/behavior_matched_subsets.md

python3 experiments/preservation_bench/analyze_causal_patch_leakage.py \
  experiments/preservation_bench/runs/ast_causal_patch_attention_state_action_mismatch_full22/causal_patch_rows.jsonl \
  --output-json experiments/preservation_bench/runs/ast_causal_patch_attention_state_action_mismatch_full22/leakage_audit.json \
  --output-md experiments/preservation_bench/runs/ast_causal_patch_attention_state_action_mismatch_full22/leakage_audit.md
```

Plot:

```bash
python3 experiments/preservation_bench/plot_causal_patch_results.py \
  --contrasts experiments/preservation_bench/runs/ast_causal_patch_attention_state_action_mismatch_full22/causal_patch_contrasts.json \
  --rows experiments/preservation_bench/runs/ast_causal_patch_attention_state_action_mismatch_full22/causal_patch_rows.jsonl \
  --output-dir paper5/figures/attention_state
```

Expected checks:

- `causal_patch_rows.jsonl` has 2,108 rows.
- Matched donor copied-attention interchange action agreement is 0.864.
- Action-mismatch copied-attention specificity gap is 0.778.
- Action-mismatch copied-attention minus behavior-distill paired action delta is 0.597 with 95% bootstrap CI [0.375, 0.790].
- On behavior-distill ordinary-action-matched attention rows, matched-donor causal action agreement is 0.108 for behavior distillation and 0.923 for copied attention.
- On attention action-mismatch rows, copied attention has source-counterfactual agreement 0.864 versus stale matched-reference agreement 0.085, but source-counterfactual and donor source-B ordinary actions coincide in 0.972 of rows.

## Attention-State Donor-Action-Mismatch Panel

Run:

```bash
KMP_DUPLICATE_LIB_OK=TRUE OMP_NUM_THREADS=1 python3 -B \
  experiments/preservation_bench/run_ast_causal_patch_probe.py \
  --config experiments/preservation_bench/configs/ast_causal_patch_attention_state_donor_action_mismatch_full22.json
```

Analyze:

```bash
python3 experiments/preservation_bench/analyze_causal_patch_contrasts.py \
  experiments/preservation_bench/runs/ast_causal_patch_attention_state_donor_action_mismatch_full22/causal_patch_rows.jsonl \
  --output-json experiments/preservation_bench/runs/ast_causal_patch_attention_state_donor_action_mismatch_full22/causal_patch_contrasts.json \
  --output-md experiments/preservation_bench/runs/ast_causal_patch_attention_state_donor_action_mismatch_full22/causal_patch_contrasts.md

python3 experiments/preservation_bench/analyze_causal_patch_behavior_matched.py \
  experiments/preservation_bench/runs/ast_causal_patch_attention_state_donor_action_mismatch_full22/causal_patch_rows.jsonl \
  --output-json experiments/preservation_bench/runs/ast_causal_patch_attention_state_donor_action_mismatch_full22/behavior_matched_subsets.json \
  --output-md experiments/preservation_bench/runs/ast_causal_patch_attention_state_donor_action_mismatch_full22/behavior_matched_subsets.md

python3 experiments/preservation_bench/analyze_causal_patch_leakage.py \
  experiments/preservation_bench/runs/ast_causal_patch_attention_state_donor_action_mismatch_full22/causal_patch_rows.jsonl \
  --output-json experiments/preservation_bench/runs/ast_causal_patch_attention_state_donor_action_mismatch_full22/leakage_audit.json \
  --output-md experiments/preservation_bench/runs/ast_causal_patch_attention_state_donor_action_mismatch_full22/leakage_audit.md

python3 experiments/preservation_bench/plot_causal_patch_donor_action_mismatch.py \
  --contrasts experiments/preservation_bench/runs/ast_causal_patch_attention_state_donor_action_mismatch_full22/causal_patch_contrasts.json \
  --leakage experiments/preservation_bench/runs/ast_causal_patch_attention_state_donor_action_mismatch_full22/leakage_audit.json \
  --output-dir paper5/figures/attention_state_donor_action_mismatch
```

Expected checks:

- `causal_patch_rows.jsonl` has 1,216 rows.
- Donor-action-mismatch donors are available for 128 rows across 18 source seeds per condition.
- On those decoupled rows, source counterfactual action and donor source-B ordinary action differ by construction.
- Copied attention reaches 0.406 source-counterfactual action agreement versus 0.234 for behavior distillation and 0.297 for frozen random.
- Copied attention Q-delta error is 0.1386 versus 89.4973 for behavior distillation and 34.8843 for frozen random.
- Source-seed paired copied-minus-behavior action delta is 0.259 with 95% bootstrap CI [0.035, 0.484].
- On behavior-distill ordinary-action-matched decoupled rows, behavior distillation reaches 0.375 causal action agreement and copied attention reaches 0.350, so this slice is a limitation rather than a green behavior-matched result.
- `paper5/figures/attention_state_donor_action_mismatch/fig7_attention_donor_action_mismatch.png` exists.

## Bidirectional Target-To-Source Attention Panel

Run:

```bash
KMP_DUPLICATE_LIB_OK=TRUE OMP_NUM_THREADS=1 python3 -B \
  experiments/preservation_bench/run_ast_bidirectional_patch_probe.py \
  --config experiments/preservation_bench/configs/ast_bidirectional_patch_attention_state_full22.json
```

Analyze and plot:

```bash
python3 experiments/preservation_bench/analyze_bidirectional_patch_contrasts.py \
  --rows experiments/preservation_bench/runs/ast_bidirectional_patch_attention_state_full22/bidirectional_patch_rows.jsonl \
  --output-json experiments/preservation_bench/runs/ast_bidirectional_patch_attention_state_full22/bidirectional_patch_contrasts.json \
  --output-md experiments/preservation_bench/runs/ast_bidirectional_patch_attention_state_full22/bidirectional_patch_contrasts.md

python3 experiments/preservation_bench/plot_bidirectional_patch_results.py \
  --contrasts experiments/preservation_bench/runs/ast_bidirectional_patch_attention_state_full22/bidirectional_patch_contrasts.json \
  --output-dir paper5/figures/bidirectional_attention
```

Expected checks:

- `bidirectional_patch_rows.jsonl` has 704 rows.
- Source-full positive control has 1.000 source-counterfactual action agreement and 0.0000 Q-delta error.
- Copied attention reaches 0.938 source-counterfactual action agreement with Q-delta error 0.1642.
- Behavior distillation reaches 0.210 source-counterfactual action agreement with Q-delta error 38.0626.
- Frozen random reaches 0.199 source-counterfactual action agreement with Q-delta error 47.1765.
- Source-seed paired copied-minus-behavior action delta is 0.727 with 95% bootstrap CI [0.631, 0.818].
- `paper5/figures/bidirectional_attention/fig8_bidirectional_attention_patch_full22.png` exists.
- `paper5/figures/bidirectional_attention/fig9_bidirectional_paired_deltas_full22.png` exists.

## Verification

```bash
python3 -m py_compile \
  experiments/preservation_bench/run_ast_causal_patch_probe.py \
  experiments/preservation_bench/run_ast_bidirectional_patch_probe.py \
  experiments/preservation_bench/analyze_causal_patch_contrasts.py \
  experiments/preservation_bench/analyze_causal_patch_behavior_matched.py \
  experiments/preservation_bench/analyze_causal_patch_leakage.py \
  experiments/preservation_bench/analyze_bidirectional_patch_contrasts.py \
  experiments/preservation_bench/plot_causal_patch_donor_action_mismatch.py \
  experiments/preservation_bench/plot_bidirectional_patch_results.py \
  experiments/preservation_bench/plot_causal_patch_results.py

python3 -m json.tool \
  experiments/preservation_bench/configs/ast_causal_patch_schema_state_action_mismatch_full22.json >/dev/null

python3 -m json.tool \
  experiments/preservation_bench/configs/ast_causal_patch_attention_state_action_mismatch_full22.json >/dev/null

python3 -m json.tool \
  experiments/preservation_bench/configs/ast_causal_patch_attention_state_donor_action_mismatch_full22.json >/dev/null

python3 -m json.tool \
  experiments/preservation_bench/configs/ast_bidirectional_patch_attention_state_full22.json >/dev/null

/Users/guts/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  paper5/render_manuscript_pdf.py \
  --input paper5/manuscript.md \
  --output output/pdf/paper5_causal_preservation_draft.pdf

pdftoppm -png \
  output/pdf/paper5_causal_preservation_draft.pdf \
  tmp/pdfs/paper5_render/page
```

Current local verification status on 2026-06-16:

```text
py_compile_ok
json_ok files=23
schema_rows=1892
attention_rows=2108
attention_donor_action_mismatch_rows=1216
bidirectional_attention_rows=704
ascii_scan_ok
pdf_pages=21
pdf_rendered_pngs=21
visual_render_check_ok
leakage_audit_ok
```

Release-readiness record preserved in `paper5/release_reminder.md`.
