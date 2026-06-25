# Causal Patch Leakage And Shortcut Audit

Rows: `experiments/preservation_bench/runs/ast_causal_patch_attention_state_action_mismatch_full22/causal_patch_rows.jsonl`
Patch path: `attention_state`

This report checks whether causal-patch action agreement can be explained by simple action-level shortcuts: preserving the target's unpatched action, copying the donor source-B action, or following the stale matched-reference counterfactual action.

The strongest anti-leakage row subset is `source_cf_differs_from_donor_source_b_action`: on those rows, the donor's ordinary source-B action is not the same as the source counterfactual caused by the patch.

## all_rows

| donor | condition | n | seeds | cf action | unpatched action | donor-B action | matched-ref action | cf-vs-unpatched gap | cf-vs-donor-B gap | cf-vs-matched-ref gap | cf=donor-B | cf=unpatched | patch changed |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| action_mismatch | source_full | 176 | 22 | 1.000 | 0.494 | 0.972 | 0.000 | 0.506 | 0.028 | 1.000 | 0.972 | 0.494 | 0.506 |
| matched | source_full | 176 | 22 | 1.000 | 0.045 | 0.977 | 1.000 | 0.955 | 0.023 | 0.000 | 0.977 | 0.045 | 0.955 |
| same_action | source_full | 175 | 22 | 1.000 | 1.000 | 0.971 | 0.046 | 0.000 | 0.029 | 0.954 | 0.971 | 1.000 | 0.000 |
| action_mismatch | b_source_align_attention_copy_long | 176 | 22 | 0.864 | 0.523 | 0.852 | 0.085 | 0.341 | 0.011 | 0.778 | 0.972 | 0.511 | 0.477 |
| matched | b_source_align_attention_copy_long | 176 | 22 | 0.864 | 0.131 | 0.875 | 0.864 | 0.733 | -0.011 | 0.000 | 0.977 | 0.074 | 0.869 |
| same_action | b_source_align_attention_copy_long | 175 | 22 | 0.914 | 0.840 | 0.897 | 0.051 | 0.074 | 0.017 | 0.863 | 0.971 | 0.869 | 0.160 |
| action_mismatch | b_behavior_distill | 176 | 22 | 0.267 | 0.347 | 0.290 | 0.261 | -0.080 | -0.023 | 0.006 | 0.972 | 0.250 | 0.653 |
| matched | b_behavior_distill | 176 | 22 | 0.188 | 0.381 | 0.205 | 0.188 | -0.193 | -0.017 | 0.000 | 0.977 | 0.341 | 0.619 |
| same_action | b_behavior_distill | 175 | 22 | 0.120 | 0.343 | 0.131 | 0.234 | -0.223 | -0.011 | -0.114 | 0.971 | 0.371 | 0.657 |
| action_mismatch | b_frozen_random | 176 | 22 | 0.312 | 0.619 | 0.301 | 0.142 | -0.307 | 0.011 | 0.170 | 0.972 | 0.176 | 0.381 |
| matched | b_frozen_random | 176 | 22 | 0.216 | 0.665 | 0.210 | 0.216 | -0.449 | 0.006 | 0.000 | 0.977 | 0.142 | 0.335 |
| same_action | b_frozen_random | 175 | 22 | 0.257 | 0.663 | 0.280 | 0.154 | -0.406 | -0.023 | 0.103 | 0.971 | 0.183 | 0.337 |

## source_cf_differs_from_donor_source_b_action

| donor | condition | n | seeds | cf action | unpatched action | donor-B action | matched-ref action | cf-vs-unpatched gap | cf-vs-donor-B gap | cf-vs-matched-ref gap | cf=donor-B | cf=unpatched | patch changed |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| action_mismatch | source_full | 5 | 2 | 1.000 | 0.200 | 0.000 | 0.000 | 0.800 | 1.000 | 1.000 | 0.000 | 0.200 | 0.800 |
| matched | source_full | 4 | 4 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| same_action | source_full | 5 | 2 | 1.000 | 1.000 | 0.000 | 0.200 | 0.000 | 1.000 | 0.800 | 0.000 | 1.000 | 0.000 |
| action_mismatch | b_source_align_attention_copy_long | 5 | 2 | 0.400 | 0.000 | 0.000 | 0.200 | 0.400 | 0.400 | 0.200 | 0.000 | 0.000 | 1.000 |
| matched | b_source_align_attention_copy_long | 4 | 4 | 0.250 | 0.250 | 0.750 | 0.250 | 0.000 | -0.500 | 0.000 | 0.000 | 0.000 | 0.750 |
| same_action | b_source_align_attention_copy_long | 5 | 2 | 0.800 | 0.800 | 0.200 | 0.200 | 0.000 | 0.600 | 0.600 | 0.000 | 0.600 | 0.200 |
| action_mismatch | b_behavior_distill | 5 | 2 | 0.000 | 0.200 | 0.800 | 0.200 | -0.200 | -0.800 | -0.200 | 0.000 | 0.200 | 0.800 |
| matched | b_behavior_distill | 4 | 4 | 0.000 | 0.500 | 0.750 | 0.000 | -0.500 | -0.750 | 0.000 | 0.000 | 0.250 | 0.500 |
| same_action | b_behavior_distill | 5 | 2 | 0.200 | 0.400 | 0.600 | 0.200 | -0.200 | -0.400 | 0.000 | 0.000 | 0.200 | 0.600 |
| action_mismatch | b_frozen_random | 5 | 2 | 0.600 | 1.000 | 0.200 | 0.200 | -0.400 | 0.400 | 0.400 | 0.000 | 0.600 | 0.000 |
| matched | b_frozen_random | 4 | 4 | 0.250 | 1.000 | 0.000 | 0.250 | -0.750 | 0.250 | 0.000 | 0.000 | 0.250 | 0.000 |
| same_action | b_frozen_random | 5 | 2 | 0.000 | 0.200 | 0.800 | 0.400 | -0.200 | -0.800 | -0.400 | 0.000 | 0.000 | 0.800 |

## source_cf_differs_from_target_unpatched_action

| donor | condition | n | seeds | cf action | unpatched action | donor-B action | matched-ref action | cf-vs-unpatched gap | cf-vs-donor-B gap | cf-vs-matched-ref gap | cf=donor-B | cf=unpatched | patch changed |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| action_mismatch | source_full | 89 | 20 | 1.000 | 0.000 | 0.955 | 0.000 | 1.000 | 0.045 | 1.000 | 0.955 | 0.000 | 1.000 |
| matched | source_full | 168 | 22 | 1.000 | 0.000 | 0.976 | 1.000 | 1.000 | 0.024 | 0.000 | 0.976 | 0.000 | 1.000 |
| action_mismatch | b_source_align_attention_copy_long | 86 | 20 | 0.756 | 0.058 | 0.733 | 0.140 | 0.698 | 0.023 | 0.616 | 0.942 | 0.000 | 0.942 |
| matched | b_source_align_attention_copy_long | 163 | 22 | 0.853 | 0.061 | 0.865 | 0.853 | 0.791 | -0.012 | 0.000 | 0.975 | 0.000 | 0.939 |
| same_action | b_source_align_attention_copy_long | 23 | 12 | 0.739 | 0.174 | 0.739 | 0.043 | 0.565 | 0.000 | 0.696 | 0.913 | 0.000 | 0.826 |
| action_mismatch | b_behavior_distill | 132 | 22 | 0.242 | 0.348 | 0.265 | 0.295 | -0.106 | -0.023 | -0.053 | 0.970 | 0.000 | 0.652 |
| matched | b_behavior_distill | 116 | 22 | 0.138 | 0.431 | 0.155 | 0.138 | -0.293 | -0.017 | 0.000 | 0.974 | 0.000 | 0.569 |
| same_action | b_behavior_distill | 110 | 22 | 0.045 | 0.400 | 0.073 | 0.245 | -0.355 | -0.027 | -0.200 | 0.964 | 0.000 | 0.600 |
| action_mismatch | b_frozen_random | 145 | 22 | 0.200 | 0.572 | 0.207 | 0.172 | -0.372 | -0.007 | 0.028 | 0.986 | 0.000 | 0.428 |
| matched | b_frozen_random | 151 | 22 | 0.126 | 0.649 | 0.126 | 0.126 | -0.523 | 0.000 | 0.000 | 0.980 | 0.000 | 0.351 |
| same_action | b_frozen_random | 143 | 22 | 0.168 | 0.664 | 0.196 | 0.182 | -0.497 | -0.028 | -0.014 | 0.965 | 0.000 | 0.336 |

## action_mismatch_rows

| donor | condition | n | seeds | cf action | unpatched action | donor-B action | matched-ref action | cf-vs-unpatched gap | cf-vs-donor-B gap | cf-vs-matched-ref gap | cf=donor-B | cf=unpatched | patch changed |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| action_mismatch | source_full | 176 | 22 | 1.000 | 0.494 | 0.972 | 0.000 | 0.506 | 0.028 | 1.000 | 0.972 | 0.494 | 0.506 |
| action_mismatch | b_source_align_attention_copy_long | 176 | 22 | 0.864 | 0.523 | 0.852 | 0.085 | 0.341 | 0.011 | 0.778 | 0.972 | 0.511 | 0.477 |
| action_mismatch | b_behavior_distill | 176 | 22 | 0.267 | 0.347 | 0.290 | 0.261 | -0.080 | -0.023 | 0.006 | 0.972 | 0.250 | 0.653 |
| action_mismatch | b_frozen_random | 176 | 22 | 0.312 | 0.619 | 0.301 | 0.142 | -0.307 | 0.011 | 0.170 | 0.972 | 0.176 | 0.381 |
