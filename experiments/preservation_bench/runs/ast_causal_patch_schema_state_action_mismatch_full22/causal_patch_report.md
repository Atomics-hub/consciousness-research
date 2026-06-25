# Paper 5 Causal Patching Smoke

This is a toy PreservationBench-AST causal-patching smoke. It patches one source recurrent vector from context B into context A and asks whether each condition follows the source counterfactual response. It does not measure consciousness, survival, personal identity, or AST truth.

## Run

- study_id: `preservation_bench_ast_causal_patch_schema_state_action_mismatch_full22`
- vector_path: `schema_state`
- source_run_dir: `experiments/preservation_bench/runs/ast_competence_v2_core_10seed`
- selected source seeds: `[0, 1, 2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 20, 21, 25, 26, 27, 28]`
- candidate pairs per seed: `80`
- selected pairs per seed: `8`

## Summary

| condition | n | source flip | interchange action | shift match | delta q mse to source | delta report l1 to source | patched q mse to source cf |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| source_full/action_mismatch | 122 | 0.164 | 1.000 | 1.000 | 0.0000 | 0.0000 | 0.0000 |
| b_source_align_attention_copy_long/action_mismatch | 122 | 0.164 | 0.689 | 0.754 | 0.1694 | 0.0084 | 0.1959 |
| b_behavior_distill/action_mismatch | 122 | 0.164 | 0.361 | 0.664 | 1.1794 | 0.0326 | 9.9997 |
| b_frozen_random/action_mismatch | 122 | 0.164 | 0.164 | 0.713 | 0.0762 | 0.0123 | 92.1405 |
| source_full | 176 | 0.676 | 1.000 | 1.000 | 0.0000 | 0.0000 | 0.0000 |
| b_source_align_attention_copy_long | 176 | 0.676 | 0.642 | 0.568 | 0.1571 | 0.0069 | 0.1936 |
| b_behavior_distill | 176 | 0.676 | 0.250 | 0.443 | 1.9835 | 0.0372 | 9.0754 |
| b_frozen_random | 176 | 0.676 | 0.193 | 0.347 | 0.2459 | 0.0192 | 102.5170 |
| source_full/same_action | 175 | 0.000 | 1.000 | 1.000 | 0.0000 | 0.0000 | 0.0000 |
| b_source_align_attention_copy_long/same_action | 175 | 0.000 | 0.771 | 0.869 | 0.1642 | 0.0068 | 0.2044 |
| b_behavior_distill/same_action | 175 | 0.000 | 0.394 | 0.720 | 1.6690 | 0.0324 | 8.9374 |
| b_frozen_random/same_action | 175 | 0.000 | 0.166 | 0.731 | 0.0511 | 0.0105 | 102.3705 |

## Interpretation Gate

- `source_full` is the within-source positive control: it should have perfect interchange agreement by construction, while the selected source pairs report whether patching had a real source-side effect.
- Target rows use direct hidden-state identity patching. This is appropriate for copied schema/attention conditions but intentionally harsh for behavior-only and random controls.
- A green result requires copied attention to separate from behavior distillation and frozen random on source-counterfactual agreement or source-delta distance, while behavior-only remains ordinary-behavior plausible but causally weaker.
