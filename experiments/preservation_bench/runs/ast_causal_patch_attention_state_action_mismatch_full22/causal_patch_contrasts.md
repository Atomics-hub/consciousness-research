# Causal Patch Contrast Report

This report summarizes source activation interchange rows. It is a toy PreservationBench-AST analysis and does not measure consciousness, identity, survival, or AST truth.

## All Rows

| donor | condition | n | seeds | src flip | control=matched | donor action | matched-ref action | specificity gap | patch changed | shift match | q delta | report delta | unpatched A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| action_mismatch | source_full | 176 | 22 | 0.506 | 0.000 | 1.000 | 0.000 | 1.000 | 0.506 | 1.000 | 0.000 | 0.000 | 1.000 |
| matched | source_full | 176 | 22 | 0.955 | 1.000 | 1.000 | 1.000 | 0.000 | 0.955 | 1.000 | 0.000 | 0.000 | 1.000 |
| same_action | source_full | 175 | 22 | 0.000 | 0.046 | 1.000 | 0.046 | 0.954 | 0.000 | 1.000 | 0.000 | 0.000 | 1.000 |
| action_mismatch | b_source_align_attention_copy_long | 176 | 22 | 0.506 | 0.000 | 0.864 | 0.085 | 0.778 | 0.477 | 0.903 | 0.127 | 0.005 | 0.869 |
| matched | b_source_align_attention_copy_long | 176 | 22 | 0.955 | 1.000 | 0.864 | 0.864 | 0.000 | 0.869 | 0.892 | 0.112 | 0.005 | 0.869 |
| same_action | b_source_align_attention_copy_long | 175 | 22 | 0.000 | 0.046 | 0.914 | 0.051 | 0.863 | 0.160 | 0.840 | 0.115 | 0.005 | 0.869 |
| action_mismatch | b_behavior_distill | 176 | 22 | 0.506 | 0.000 | 0.267 | 0.261 | 0.006 | 0.653 | 0.625 | 96.976 | 0.006 | 0.369 |
| matched | b_behavior_distill | 176 | 22 | 0.955 | 1.000 | 0.188 | 0.188 | 0.000 | 0.619 | 0.619 | 111.071 | 0.008 | 0.369 |
| same_action | b_behavior_distill | 175 | 22 | 0.000 | 0.046 | 0.120 | 0.234 | -0.114 | 0.657 | 0.343 | 91.715 | 0.005 | 0.371 |
| action_mismatch | b_frozen_random | 176 | 22 | 0.506 | 0.000 | 0.312 | 0.142 | 0.170 | 0.381 | 0.409 | 10.253 | 0.006 | 0.182 |
| matched | b_frozen_random | 176 | 22 | 0.955 | 1.000 | 0.216 | 0.216 | 0.000 | 0.335 | 0.369 | 29.907 | 0.008 | 0.182 |
| same_action | b_frozen_random | 175 | 22 | 0.000 | 0.046 | 0.257 | 0.154 | 0.103 | 0.337 | 0.663 | 7.535 | 0.005 | 0.183 |

## Matched Donors, Source-Action-Flip Rows Only

| donor | condition | n | seeds | src flip | control=matched | donor action | matched-ref action | specificity gap | patch changed | shift match | q delta | report delta | unpatched A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| matched | source_full | 168 | 22 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 |
| matched | b_source_align_attention_copy_long | 168 | 22 | 1.000 | 1.000 | 0.863 | 0.863 | 0.000 | 0.899 | 0.899 | 0.114 | 0.005 | 0.875 |
| matched | b_behavior_distill | 168 | 22 | 1.000 | 1.000 | 0.185 | 0.185 | 0.000 | 0.625 | 0.625 | 110.355 | 0.008 | 0.363 |
| matched | b_frozen_random | 168 | 22 | 1.000 | 1.000 | 0.226 | 0.226 | 0.000 | 0.345 | 0.345 | 28.183 | 0.008 | 0.190 |

## Paired Seed Deltas

`mean_delta` is copied-attention minus the listed baseline, after averaging rows within each source seed.

| donor | baseline | metric | seeds | mean delta | 95% bootstrap CI |
| --- | --- | --- | ---: | ---: | ---: |
| action_mismatch | b_behavior_distill | target_interchange_action_agreement | 22 | 0.597 | [0.375, 0.790] |
| action_mismatch | b_behavior_distill | target_patch_delta_q_mse_to_source | 22 | -96.849 | [-140.111, -60.386] |
| action_mismatch | b_behavior_distill | target_patched_q_mse_to_source_cf | 22 | -100.007 | [-137.086, -68.343] |
| action_mismatch | b_behavior_distill | target_patched_q_mse_to_matched_reference_cf | 22 | -64.496 | [-109.759, -28.553] |
| action_mismatch | b_behavior_distill | target_patch_delta_self_report_l1_to_source | 22 | -0.000 | [-0.003, 0.002] |
| action_mismatch | b_behavior_distill | target_unpatched_source_a_action_agreement | 22 | 0.500 | [0.386, 0.608] |
| action_mismatch | b_frozen_random | target_interchange_action_agreement | 22 | 0.551 | [0.358, 0.727] |
| action_mismatch | b_frozen_random | target_patch_delta_q_mse_to_source | 22 | -10.127 | [-19.113, -3.430] |
| action_mismatch | b_frozen_random | target_patched_q_mse_to_source_cf | 22 | -125.156 | [-170.174, -87.901] |
| action_mismatch | b_frozen_random | target_patched_q_mse_to_matched_reference_cf | 22 | -88.259 | [-140.121, -46.579] |
| action_mismatch | b_frozen_random | target_patch_delta_self_report_l1_to_source | 22 | -0.000 | [-0.003, 0.002] |
| action_mismatch | b_frozen_random | target_unpatched_source_a_action_agreement | 22 | 0.688 | [0.574, 0.795] |
| matched | b_behavior_distill | target_interchange_action_agreement | 22 | 0.676 | [0.562, 0.778] |
| matched | b_behavior_distill | target_patch_delta_q_mse_to_source | 22 | -110.959 | [-157.277, -73.735] |
| matched | b_behavior_distill | target_patched_q_mse_to_source_cf | 22 | -89.092 | [-131.260, -58.429] |
| matched | b_behavior_distill | target_patched_q_mse_to_matched_reference_cf | 22 | -89.092 | [-129.117, -57.457] |
| matched | b_behavior_distill | target_patch_delta_self_report_l1_to_source | 22 | -0.003 | [-0.005, -0.001] |
| matched | b_behavior_distill | target_unpatched_source_a_action_agreement | 22 | 0.500 | [0.392, 0.608] |
| matched | b_frozen_random | target_interchange_action_agreement | 22 | 0.648 | [0.551, 0.739] |
| matched | b_frozen_random | target_patch_delta_q_mse_to_source | 22 | -29.796 | [-48.677, -14.576] |
| matched | b_frozen_random | target_patched_q_mse_to_source_cf | 22 | -113.037 | [-160.256, -75.360] |
| matched | b_frozen_random | target_patched_q_mse_to_matched_reference_cf | 22 | -113.037 | [-163.387, -76.030] |
| matched | b_frozen_random | target_patch_delta_self_report_l1_to_source | 22 | -0.003 | [-0.005, -0.001] |
| matched | b_frozen_random | target_unpatched_source_a_action_agreement | 22 | 0.688 | [0.574, 0.790] |
| same_action | b_behavior_distill | target_interchange_action_agreement | 22 | 0.795 | [0.692, 0.892] |
| same_action | b_behavior_distill | target_patch_delta_q_mse_to_source | 22 | -91.417 | [-134.568, -57.350] |
| same_action | b_behavior_distill | target_patched_q_mse_to_source_cf | 22 | -96.308 | [-134.801, -63.975] |
| same_action | b_behavior_distill | target_patched_q_mse_to_matched_reference_cf | 22 | -66.403 | [-109.579, -33.574] |
| same_action | b_behavior_distill | target_patch_delta_self_report_l1_to_source | 22 | -0.000 | [-0.002, 0.002] |
| same_action | b_behavior_distill | target_unpatched_source_a_action_agreement | 22 | 0.498 | [0.390, 0.606] |
| same_action | b_frozen_random | target_interchange_action_agreement | 22 | 0.656 | [0.530, 0.778] |
| same_action | b_frozen_random | target_patch_delta_q_mse_to_source | 22 | -7.387 | [-12.981, -2.941] |
| same_action | b_frozen_random | target_patched_q_mse_to_source_cf | 22 | -120.433 | [-169.757, -80.265] |
| same_action | b_frozen_random | target_patched_q_mse_to_matched_reference_cf | 22 | -90.252 | [-140.989, -51.102] |
| same_action | b_frozen_random | target_patch_delta_self_report_l1_to_source | 22 | 0.000 | [-0.002, 0.002] |
| same_action | b_frozen_random | target_unpatched_source_a_action_agreement | 22 | 0.683 | [0.575, 0.790] |
