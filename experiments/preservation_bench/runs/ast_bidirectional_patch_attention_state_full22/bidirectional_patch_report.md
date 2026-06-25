# Paper 5 Bidirectional Patch Probe

This bounded probe patches target-B activations back into source context A and compares the resulting source response with the source-B-to-source-A counterfactual. It tests whether target activations can play the source variable's causal role in the source, not only whether source activations drive the target.

It does not measure consciousness, survival, personal identity, biological preservation, or AST truth.

## Run

- study_id: `preservation_bench_ast_bidirectional_patch_attention_state_full22`
- vector_path: `attention_state`
- source_run_dir: `experiments/preservation_bench/runs/ast_competence_v2_core_10seed`
- selected source seeds: `[0, 1, 2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 20, 21, 25, 26, 27, 28]`
- candidate pairs per seed: `80`
- selected pairs per seed: `8`

## Summary

| condition | n | source flip | action agreement | shift match | q-delta error | patched-Q error | donor attention L1 | donor feature MSE |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| source_full | 176 | 0.955 | 1.000 | 1.000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| b_source_align_attention_copy_long | 176 | 0.955 | 0.938 | 0.972 | 0.1642 | 0.1642 | 0.0002 | 0.0011 |
| b_behavior_distill | 176 | 0.955 | 0.210 | 0.767 | 38.0626 | 38.0626 | 0.0351 | 1.8687 |
| b_frozen_random | 176 | 0.955 | 0.199 | 0.761 | 47.1765 | 47.1765 | 0.0351 | 0.2230 |
