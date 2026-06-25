# Causal Patch Contrast Report

This report summarizes source activation interchange rows. It is a toy PreservationBench-AST analysis and does not measure consciousness, identity, survival, or AST truth.

## All Rows

| donor | condition | n | seeds | src flip | control=matched | donor action | matched-ref action | specificity gap | patch changed | shift match | q delta | report delta | unpatched A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| action_mismatch | source_full | 122 | 19 | 0.164 | 0.000 | 1.000 | 0.000 | 1.000 | 0.164 | 1.000 | 0.000 | 0.000 | 1.000 |
| matched | source_full | 176 | 22 | 0.676 | 1.000 | 1.000 | 1.000 | 0.000 | 0.676 | 1.000 | 0.000 | 0.000 | 1.000 |
| same_action | source_full | 175 | 22 | 0.000 | 0.326 | 1.000 | 0.326 | 0.674 | 0.000 | 1.000 | 0.000 | 0.000 | 1.000 |
| action_mismatch | b_source_align_attention_copy_long | 122 | 19 | 0.164 | 0.000 | 0.689 | 0.139 | 0.549 | 0.230 | 0.754 | 0.169 | 0.008 | 0.730 |
| matched | b_source_align_attention_copy_long | 176 | 22 | 0.676 | 1.000 | 0.642 | 0.642 | 0.000 | 0.267 | 0.568 | 0.157 | 0.007 | 0.778 |
| same_action | b_source_align_attention_copy_long | 175 | 22 | 0.000 | 0.326 | 0.771 | 0.383 | 0.389 | 0.131 | 0.869 | 0.164 | 0.007 | 0.777 |
| action_mismatch | b_behavior_distill | 122 | 19 | 0.164 | 0.000 | 0.361 | 0.197 | 0.164 | 0.254 | 0.664 | 1.179 | 0.033 | 0.516 |
| matched | b_behavior_distill | 176 | 22 | 0.676 | 1.000 | 0.250 | 0.250 | 0.000 | 0.324 | 0.443 | 1.984 | 0.037 | 0.517 |
| same_action | b_behavior_distill | 175 | 22 | 0.000 | 0.326 | 0.394 | 0.223 | 0.171 | 0.280 | 0.720 | 1.669 | 0.032 | 0.514 |
| action_mismatch | b_frozen_random | 122 | 19 | 0.164 | 0.000 | 0.164 | 0.197 | -0.033 | 0.238 | 0.713 | 0.076 | 0.012 | 0.139 |
| matched | b_frozen_random | 176 | 22 | 0.676 | 1.000 | 0.193 | 0.193 | 0.000 | 0.273 | 0.347 | 0.246 | 0.019 | 0.148 |
| same_action | b_frozen_random | 175 | 22 | 0.000 | 0.326 | 0.166 | 0.200 | -0.034 | 0.269 | 0.731 | 0.051 | 0.010 | 0.143 |

## Matched Donors, Source-Action-Flip Rows Only

| donor | condition | n | seeds | src flip | control=matched | donor action | matched-ref action | specificity gap | patch changed | shift match | q delta | report delta | unpatched A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| matched | source_full | 119 | 19 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 |
| matched | b_source_align_attention_copy_long | 119 | 19 | 1.000 | 1.000 | 0.521 | 0.521 | 0.000 | 0.378 | 0.378 | 0.149 | 0.008 | 0.739 |
| matched | b_behavior_distill | 119 | 19 | 1.000 | 1.000 | 0.227 | 0.227 | 0.000 | 0.328 | 0.328 | 1.610 | 0.038 | 0.513 |
| matched | b_frozen_random | 119 | 19 | 1.000 | 1.000 | 0.202 | 0.202 | 0.000 | 0.218 | 0.218 | 0.342 | 0.021 | 0.143 |

## Paired Seed Deltas

`mean_delta` is copied-attention minus the listed baseline, after averaging rows within each source seed.

| donor | baseline | metric | seeds | mean delta | 95% bootstrap CI |
| --- | --- | --- | ---: | ---: | ---: |
| action_mismatch | b_behavior_distill | target_interchange_action_agreement | 19 | 0.324 | [0.182, 0.473] |
| action_mismatch | b_behavior_distill | target_patch_delta_q_mse_to_source | 19 | -0.941 | [-1.280, -0.627] |
| action_mismatch | b_behavior_distill | target_patched_q_mse_to_source_cf | 19 | -8.772 | [-15.202, -3.978] |
| action_mismatch | b_behavior_distill | target_patched_q_mse_to_matched_reference_cf | 19 | -8.491 | [-14.530, -3.937] |
| action_mismatch | b_behavior_distill | target_patch_delta_self_report_l1_to_source | 19 | -0.025 | [-0.027, -0.022] |
| action_mismatch | b_behavior_distill | target_unpatched_source_a_action_agreement | 19 | 0.246 | [0.077, 0.417] |
| action_mismatch | b_frozen_random | target_interchange_action_agreement | 19 | 0.489 | [0.360, 0.614] |
| action_mismatch | b_frozen_random | target_patch_delta_q_mse_to_source | 19 | 0.076 | [-0.003, 0.171] |
| action_mismatch | b_frozen_random | target_patched_q_mse_to_source_cf | 19 | -88.064 | [-119.835, -63.625] |
| action_mismatch | b_frozen_random | target_patched_q_mse_to_matched_reference_cf | 19 | -87.863 | [-117.984, -63.572] |
| action_mismatch | b_frozen_random | target_patch_delta_self_report_l1_to_source | 19 | -0.004 | [-0.007, -0.002] |
| action_mismatch | b_frozen_random | target_unpatched_source_a_action_agreement | 19 | 0.527 | [0.358, 0.683] |
| matched | b_behavior_distill | target_interchange_action_agreement | 22 | 0.392 | [0.261, 0.523] |
| matched | b_behavior_distill | target_patch_delta_q_mse_to_source | 22 | -1.826 | [-3.319, -0.829] |
| matched | b_behavior_distill | target_patched_q_mse_to_source_cf | 22 | -8.882 | [-14.547, -4.769] |
| matched | b_behavior_distill | target_patched_q_mse_to_matched_reference_cf | 22 | -8.882 | [-14.366, -4.752] |
| matched | b_behavior_distill | target_patch_delta_self_report_l1_to_source | 22 | -0.030 | [-0.033, -0.027] |
| matched | b_behavior_distill | target_unpatched_source_a_action_agreement | 22 | 0.261 | [0.131, 0.398] |
| matched | b_frozen_random | target_interchange_action_agreement | 22 | 0.449 | [0.324, 0.574] |
| matched | b_frozen_random | target_patch_delta_q_mse_to_source | 22 | -0.089 | [-0.387, 0.118] |
| matched | b_frozen_random | target_patched_q_mse_to_source_cf | 22 | -102.323 | [-147.336, -66.658] |
| matched | b_frozen_random | target_patched_q_mse_to_matched_reference_cf | 22 | -102.323 | [-150.085, -67.744] |
| matched | b_frozen_random | target_patch_delta_self_report_l1_to_source | 22 | -0.012 | [-0.015, -0.010] |
| matched | b_frozen_random | target_unpatched_source_a_action_agreement | 22 | 0.631 | [0.506, 0.739] |
| same_action | b_behavior_distill | target_interchange_action_agreement | 22 | 0.377 | [0.239, 0.517] |
| same_action | b_behavior_distill | target_patch_delta_q_mse_to_source | 22 | -1.500 | [-2.900, -0.663] |
| same_action | b_behavior_distill | target_patched_q_mse_to_source_cf | 22 | -8.712 | [-14.210, -4.425] |
| same_action | b_behavior_distill | target_patched_q_mse_to_matched_reference_cf | 22 | -8.428 | [-13.830, -4.253] |
| same_action | b_behavior_distill | target_patch_delta_self_report_l1_to_source | 22 | -0.026 | [-0.029, -0.023] |
| same_action | b_behavior_distill | target_unpatched_source_a_action_agreement | 22 | 0.261 | [0.124, 0.398] |
| same_action | b_frozen_random | target_interchange_action_agreement | 22 | 0.602 | [0.477, 0.716] |
| same_action | b_frozen_random | target_patch_delta_q_mse_to_source | 22 | 0.112 | [0.023, 0.227] |
| same_action | b_frozen_random | target_patched_q_mse_to_source_cf | 22 | -101.932 | [-149.777, -65.271] |
| same_action | b_frozen_random | target_patched_q_mse_to_matched_reference_cf | 22 | -101.940 | [-149.196, -66.301] |
| same_action | b_frozen_random | target_patch_delta_self_report_l1_to_source | 22 | -0.004 | [-0.006, -0.002] |
| same_action | b_frozen_random | target_unpatched_source_a_action_agreement | 22 | 0.630 | [0.505, 0.744] |
