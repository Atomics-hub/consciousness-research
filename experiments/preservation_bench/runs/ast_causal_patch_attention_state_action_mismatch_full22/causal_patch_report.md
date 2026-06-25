# Paper 5 Causal Patching Smoke

This is a toy PreservationBench-AST causal-patching smoke. It patches one source recurrent vector from context B into context A and asks whether each condition follows the source counterfactual response. It does not measure consciousness, survival, personal identity, or AST truth.

## Run

- study_id: `preservation_bench_ast_causal_patch_attention_state_action_mismatch_full22`
- vector_path: `attention_state`
- source_run_dir: `experiments/preservation_bench/runs/ast_competence_v2_core_10seed`
- selected source seeds: `[0, 1, 2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 20, 21, 25, 26, 27, 28]`
- candidate pairs per seed: `80`
- selected pairs per seed: `8`

## Summary

| condition | n | source flip | interchange action | shift match | delta q mse to source | delta report l1 to source | patched q mse to source cf |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| source_full/action_mismatch | 176 | 0.506 | 1.000 | 1.000 | 0.0000 | 0.0000 | 0.0000 |
| b_source_align_attention_copy_long/action_mismatch | 176 | 0.506 | 0.864 | 0.903 | 0.1268 | 0.0053 | 0.0835 |
| b_behavior_distill/action_mismatch | 176 | 0.506 | 0.267 | 0.625 | 96.9758 | 0.0057 | 100.0904 |
| b_frozen_random/action_mismatch | 176 | 0.506 | 0.312 | 0.409 | 10.2535 | 0.0057 | 125.2398 |
| source_full | 176 | 0.955 | 1.000 | 1.000 | 0.0000 | 0.0000 | 0.0000 |
| b_source_align_attention_copy_long | 176 | 0.955 | 0.864 | 0.892 | 0.1117 | 0.0053 | 0.0880 |
| b_behavior_distill | 176 | 0.955 | 0.188 | 0.619 | 111.0710 | 0.0083 | 89.1796 |
| b_frozen_random | 176 | 0.955 | 0.216 | 0.369 | 29.9075 | 0.0083 | 113.1253 |
| source_full/same_action | 175 | 0.000 | 1.000 | 1.000 | 0.0000 | 0.0000 | 0.0000 |
| b_source_align_attention_copy_long/same_action | 175 | 0.000 | 0.914 | 0.840 | 0.1152 | 0.0054 | 0.0937 |
| b_behavior_distill/same_action | 175 | 0.000 | 0.120 | 0.343 | 91.7151 | 0.0054 | 96.5645 |
| b_frozen_random/same_action | 175 | 0.000 | 0.257 | 0.663 | 7.5355 | 0.0054 | 120.7427 |

## Interpretation Gate

- `source_full` is the within-source positive control: it should have perfect interchange agreement by construction, while the selected source pairs report whether patching had a real source-side effect.
- Target rows use direct hidden-state identity patching. This is appropriate for copied schema/attention conditions but intentionally harsh for behavior-only and random controls.
- A green result requires copied attention to separate from behavior distillation and frozen random on source-counterfactual agreement or source-delta distance, while behavior-only remains ordinary-behavior plausible but causally weaker.
