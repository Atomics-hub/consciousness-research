# Paper 5 Causal Patching Smoke

This is a toy PreservationBench-AST causal-patching smoke. It patches one source recurrent vector from context B into context A and asks whether each condition follows the source counterfactual response. It does not measure consciousness, survival, personal identity, or AST truth.

## Run

- study_id: `preservation_bench_ast_causal_patch_attention_state_donor_action_mismatch_full22`
- vector_path: `attention_state`
- source_run_dir: `experiments/preservation_bench/runs/ast_competence_v2_core_10seed`
- selected source seeds: `[0, 1, 2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 20, 21, 25, 26, 27, 28]`
- candidate pairs per seed: `160`
- selected pairs per seed: `8`

## Summary

| condition | n | source flip | interchange action | shift match | delta q mse to source | delta report l1 to source | patched q mse to source cf |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| source_full/donor_action_mismatch | 128 | 0.969 | 1.000 | 1.000 | 0.0000 | 0.0000 | 0.0000 |
| b_source_align_attention_copy_long/donor_action_mismatch | 128 | 0.969 | 0.406 | 0.773 | 0.1386 | 0.0065 | 0.0822 |
| b_behavior_distill/donor_action_mismatch | 128 | 0.969 | 0.234 | 0.633 | 89.4973 | 0.0109 | 64.0713 |
| b_frozen_random/donor_action_mismatch | 128 | 0.969 | 0.297 | 0.336 | 34.8843 | 0.0109 | 82.5295 |
| source_full | 176 | 0.966 | 1.000 | 1.000 | 0.0000 | 0.0000 | 0.0000 |
| b_source_align_attention_copy_long | 176 | 0.966 | 0.875 | 0.909 | 0.1578 | 0.0052 | 0.1074 |
| b_behavior_distill | 176 | 0.966 | 0.256 | 0.642 | 109.3033 | 0.0093 | 88.6468 |
| b_frozen_random | 176 | 0.966 | 0.267 | 0.335 | 32.8539 | 0.0093 | 112.3082 |

## Interpretation Gate

- `source_full` is the within-source positive control: it should have perfect interchange agreement by construction, while the selected source pairs report whether patching had a real source-side effect.
- Target rows use direct hidden-state identity patching. This is appropriate for copied schema/attention conditions but intentionally harsh for behavior-only and random controls.
- A green result requires copied attention to separate from behavior distillation and frozen random on source-counterfactual agreement or source-delta distance, while behavior-only remains ordinary-behavior plausible but causally weaker.
