# Causal Patch Contrast Report

This report summarizes source activation interchange rows. It is a toy PreservationBench-AST analysis and does not measure consciousness, identity, survival, or AST truth.

## All Rows

| donor | condition | n | seeds | src flip | control=matched | donor action | matched-ref action | specificity gap | patch changed | shift match | q delta | report delta | unpatched A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| donor_action_mismatch | source_full | 128 | 18 | 0.969 | 0.492 | 1.000 | 0.492 | 0.508 | 0.969 | 1.000 | 0.000 | 0.000 | 1.000 |
| matched | source_full | 176 | 22 | 0.966 | 1.000 | 1.000 | 1.000 | 0.000 | 0.966 | 1.000 | 0.000 | 0.000 | 1.000 |
| donor_action_mismatch | b_source_align_attention_copy_long | 128 | 18 | 0.969 | 0.492 | 0.406 | 0.438 | -0.031 | 0.789 | 0.773 | 0.139 | 0.007 | 0.906 |
| matched | b_source_align_attention_copy_long | 176 | 22 | 0.966 | 1.000 | 0.875 | 0.875 | 0.000 | 0.886 | 0.909 | 0.158 | 0.005 | 0.909 |
| donor_action_mismatch | b_behavior_distill | 128 | 18 | 0.969 | 0.492 | 0.234 | 0.266 | -0.031 | 0.617 | 0.633 | 89.497 | 0.011 | 0.312 |
| matched | b_behavior_distill | 176 | 22 | 0.966 | 1.000 | 0.256 | 0.256 | 0.000 | 0.665 | 0.642 | 109.303 | 0.009 | 0.369 |
| donor_action_mismatch | b_frozen_random | 128 | 18 | 0.969 | 0.492 | 0.297 | 0.234 | 0.062 | 0.320 | 0.336 | 34.884 | 0.011 | 0.211 |
| matched | b_frozen_random | 176 | 22 | 0.966 | 1.000 | 0.267 | 0.267 | 0.000 | 0.324 | 0.335 | 32.854 | 0.009 | 0.199 |

## Matched Donors, Source-Action-Flip Rows Only

| donor | condition | n | seeds | src flip | control=matched | donor action | matched-ref action | specificity gap | patch changed | shift match | q delta | report delta | unpatched A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| matched | source_full | 170 | 22 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 |
| matched | b_source_align_attention_copy_long | 170 | 22 | 1.000 | 1.000 | 0.871 | 0.871 | 0.000 | 0.912 | 0.912 | 0.155 | 0.005 | 0.912 |
| matched | b_behavior_distill | 170 | 22 | 1.000 | 1.000 | 0.247 | 0.247 | 0.000 | 0.659 | 0.659 | 108.056 | 0.009 | 0.371 |
| matched | b_frozen_random | 170 | 22 | 1.000 | 1.000 | 0.276 | 0.276 | 0.000 | 0.324 | 0.324 | 32.896 | 0.009 | 0.206 |

## Paired Seed Deltas

`mean_delta` is copied-attention minus the listed baseline, after averaging rows within each source seed.

| donor | baseline | metric | seeds | mean delta | 95% bootstrap CI |
| --- | --- | --- | ---: | ---: | ---: |
| donor_action_mismatch | b_behavior_distill | target_interchange_action_agreement | 18 | 0.259 | [0.035, 0.484] |
| donor_action_mismatch | b_behavior_distill | target_patch_delta_q_mse_to_source | 18 | -89.074 | [-121.813, -61.687] |
| donor_action_mismatch | b_behavior_distill | target_patched_q_mse_to_source_cf | 18 | -63.170 | [-91.349, -41.236] |
| donor_action_mismatch | b_behavior_distill | target_patched_q_mse_to_matched_reference_cf | 18 | -73.908 | [-105.009, -47.480] |
| donor_action_mismatch | b_behavior_distill | target_patch_delta_self_report_l1_to_source | 18 | -0.004 | [-0.007, -0.002] |
| donor_action_mismatch | b_behavior_distill | target_unpatched_source_a_action_agreement | 18 | 0.588 | [0.479, 0.688] |
| donor_action_mismatch | b_frozen_random | target_interchange_action_agreement | 18 | 0.157 | [-0.104, 0.405] |
| donor_action_mismatch | b_frozen_random | target_patch_delta_q_mse_to_source | 18 | -31.711 | [-56.110, -13.269] |
| donor_action_mismatch | b_frozen_random | target_patched_q_mse_to_source_cf | 18 | -81.777 | [-114.982, -54.935] |
| donor_action_mismatch | b_frozen_random | target_patched_q_mse_to_matched_reference_cf | 18 | -94.167 | [-130.830, -64.298] |
| donor_action_mismatch | b_frozen_random | target_patch_delta_self_report_l1_to_source | 18 | -0.004 | [-0.007, -0.002] |
| donor_action_mismatch | b_frozen_random | target_unpatched_source_a_action_agreement | 18 | 0.718 | [0.576, 0.847] |
| matched | b_behavior_distill | target_interchange_action_agreement | 22 | 0.619 | [0.506, 0.733] |
| matched | b_behavior_distill | target_patch_delta_q_mse_to_source | 22 | -109.146 | [-154.108, -73.418] |
| matched | b_behavior_distill | target_patched_q_mse_to_source_cf | 22 | -88.539 | [-132.701, -56.249] |
| matched | b_behavior_distill | target_patched_q_mse_to_matched_reference_cf | 22 | -88.539 | [-131.511, -56.117] |
| matched | b_behavior_distill | target_patch_delta_self_report_l1_to_source | 22 | -0.004 | [-0.006, -0.002] |
| matched | b_behavior_distill | target_unpatched_source_a_action_agreement | 22 | 0.540 | [0.449, 0.619] |
| matched | b_frozen_random | target_interchange_action_agreement | 22 | 0.608 | [0.500, 0.716] |
| matched | b_frozen_random | target_patch_delta_q_mse_to_source | 22 | -32.696 | [-52.119, -16.949] |
| matched | b_frozen_random | target_patched_q_mse_to_source_cf | 22 | -112.201 | [-162.473, -73.194] |
| matched | b_frozen_random | target_patched_q_mse_to_matched_reference_cf | 22 | -112.201 | [-165.293, -73.493] |
| matched | b_frozen_random | target_patch_delta_self_report_l1_to_source | 22 | -0.004 | [-0.006, -0.002] |
| matched | b_frozen_random | target_unpatched_source_a_action_agreement | 22 | 0.710 | [0.602, 0.807] |
