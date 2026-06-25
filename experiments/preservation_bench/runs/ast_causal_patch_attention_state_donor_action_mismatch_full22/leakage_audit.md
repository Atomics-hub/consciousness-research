# Causal Patch Leakage And Shortcut Audit

Rows: `experiments/preservation_bench/runs/ast_causal_patch_attention_state_donor_action_mismatch_full22/causal_patch_rows.jsonl`
Patch path: `attention_state`

This report checks whether causal-patch action agreement can be explained by simple action-level shortcuts: preserving the target's unpatched action, copying the donor source-B action, or following the stale matched-reference counterfactual action.

The strongest anti-leakage row subset is `source_cf_differs_from_donor_source_b_action`: on those rows, the donor's ordinary source-B action is not the same as the source counterfactual caused by the patch.

## all_rows

| donor | condition | n | seeds | cf action | unpatched action | donor-B action | matched-ref action | cf-vs-unpatched gap | cf-vs-donor-B gap | cf-vs-matched-ref gap | cf=donor-B | cf=unpatched | patch changed |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| donor_action_mismatch | source_full | 128 | 18 | 1.000 | 0.031 | 0.000 | 0.492 | 0.969 | 1.000 | 0.508 | 0.000 | 0.031 | 0.969 |
| matched | source_full | 176 | 22 | 1.000 | 0.034 | 0.955 | 1.000 | 0.966 | 0.045 | 0.000 | 0.955 | 0.034 | 0.966 |
| donor_action_mismatch | b_source_align_attention_copy_long | 128 | 18 | 0.406 | 0.211 | 0.508 | 0.438 | 0.195 | -0.102 | -0.031 | 0.000 | 0.055 | 0.789 |
| matched | b_source_align_attention_copy_long | 176 | 22 | 0.875 | 0.114 | 0.881 | 0.875 | 0.761 | -0.006 | 0.000 | 0.955 | 0.062 | 0.886 |
| donor_action_mismatch | b_behavior_distill | 128 | 18 | 0.234 | 0.383 | 0.242 | 0.266 | -0.148 | -0.008 | -0.031 | 0.000 | 0.289 | 0.617 |
| matched | b_behavior_distill | 176 | 22 | 0.256 | 0.335 | 0.239 | 0.256 | -0.080 | 0.017 | 0.000 | 0.955 | 0.352 | 0.665 |
| donor_action_mismatch | b_frozen_random | 128 | 18 | 0.297 | 0.680 | 0.172 | 0.234 | -0.383 | 0.125 | 0.062 | 0.000 | 0.242 | 0.320 |
| matched | b_frozen_random | 176 | 22 | 0.267 | 0.676 | 0.250 | 0.267 | -0.409 | 0.017 | 0.000 | 0.955 | 0.182 | 0.324 |

## source_cf_differs_from_donor_source_b_action

| donor | condition | n | seeds | cf action | unpatched action | donor-B action | matched-ref action | cf-vs-unpatched gap | cf-vs-donor-B gap | cf-vs-matched-ref gap | cf=donor-B | cf=unpatched | patch changed |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| donor_action_mismatch | source_full | 128 | 18 | 1.000 | 0.031 | 0.000 | 0.492 | 0.969 | 1.000 | 0.508 | 0.000 | 0.031 | 0.969 |
| matched | source_full | 8 | 7 | 1.000 | 0.125 | 0.000 | 1.000 | 0.875 | 1.000 | 0.000 | 0.000 | 0.125 | 0.875 |
| donor_action_mismatch | b_source_align_attention_copy_long | 128 | 18 | 0.406 | 0.211 | 0.508 | 0.438 | 0.195 | -0.102 | -0.031 | 0.000 | 0.055 | 0.789 |
| matched | b_source_align_attention_copy_long | 8 | 7 | 0.375 | 0.500 | 0.500 | 0.375 | -0.125 | -0.125 | 0.000 | 0.000 | 0.125 | 0.500 |
| donor_action_mismatch | b_behavior_distill | 128 | 18 | 0.234 | 0.383 | 0.242 | 0.266 | -0.148 | -0.008 | -0.031 | 0.000 | 0.289 | 0.617 |
| matched | b_behavior_distill | 8 | 7 | 0.500 | 0.625 | 0.125 | 0.500 | -0.125 | 0.375 | 0.000 | 0.000 | 0.375 | 0.375 |
| donor_action_mismatch | b_frozen_random | 128 | 18 | 0.297 | 0.680 | 0.172 | 0.234 | -0.383 | 0.125 | 0.062 | 0.000 | 0.242 | 0.320 |
| matched | b_frozen_random | 8 | 7 | 0.375 | 0.875 | 0.000 | 0.375 | -0.500 | 0.375 | 0.000 | 0.000 | 0.250 | 0.125 |

## source_cf_differs_from_target_unpatched_action

| donor | condition | n | seeds | cf action | unpatched action | donor-B action | matched-ref action | cf-vs-unpatched gap | cf-vs-donor-B gap | cf-vs-matched-ref gap | cf=donor-B | cf=unpatched | patch changed |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| donor_action_mismatch | source_full | 124 | 18 | 1.000 | 0.000 | 0.000 | 0.508 | 1.000 | 1.000 | 0.492 | 0.000 | 0.000 | 1.000 |
| matched | source_full | 170 | 22 | 1.000 | 0.000 | 0.959 | 1.000 | 1.000 | 0.041 | 0.000 | 0.959 | 0.000 | 1.000 |
| donor_action_mismatch | b_source_align_attention_copy_long | 121 | 18 | 0.413 | 0.207 | 0.496 | 0.430 | 0.207 | -0.083 | -0.017 | 0.000 | 0.000 | 0.793 |
| matched | b_source_align_attention_copy_long | 165 | 22 | 0.867 | 0.055 | 0.879 | 0.867 | 0.812 | -0.012 | 0.000 | 0.958 | 0.000 | 0.945 |
| donor_action_mismatch | b_behavior_distill | 91 | 17 | 0.242 | 0.451 | 0.198 | 0.275 | -0.209 | 0.044 | -0.033 | 0.000 | 0.000 | 0.549 |
| matched | b_behavior_distill | 114 | 22 | 0.193 | 0.316 | 0.175 | 0.193 | -0.123 | 0.018 | 0.000 | 0.956 | 0.000 | 0.684 |
| donor_action_mismatch | b_frozen_random | 97 | 18 | 0.113 | 0.619 | 0.227 | 0.165 | -0.505 | -0.113 | -0.052 | 0.000 | 0.000 | 0.381 |
| matched | b_frozen_random | 144 | 22 | 0.153 | 0.653 | 0.146 | 0.153 | -0.500 | 0.007 | 0.000 | 0.958 | 0.000 | 0.347 |
