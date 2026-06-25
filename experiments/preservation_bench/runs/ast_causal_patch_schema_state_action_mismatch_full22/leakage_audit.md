# Causal Patch Leakage And Shortcut Audit

Rows: `experiments/preservation_bench/runs/ast_causal_patch_schema_state_action_mismatch_full22/causal_patch_rows.jsonl`
Patch path: `schema_state`

This report checks whether causal-patch action agreement can be explained by simple action-level shortcuts: preserving the target's unpatched action, copying the donor source-B action, or following the stale matched-reference counterfactual action.

The strongest anti-leakage row subset is `source_cf_differs_from_donor_source_b_action`: on those rows, the donor's ordinary source-B action is not the same as the source counterfactual caused by the patch.

## all_rows

| donor | condition | n | seeds | cf action | unpatched action | donor-B action | matched-ref action | cf-vs-unpatched gap | cf-vs-donor-B gap | cf-vs-matched-ref gap | cf=donor-B | cf=unpatched | patch changed |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| action_mismatch | source_full | 122 | 19 | 1.000 | 0.836 | 0.451 | 0.000 | 0.164 | 0.549 | 1.000 | 0.451 | 0.836 | 0.164 |
| matched | source_full | 176 | 22 | 1.000 | 0.324 | 0.318 | 1.000 | 0.676 | 0.682 | 0.000 | 0.318 | 0.324 | 0.676 |
| same_action | source_full | 175 | 22 | 1.000 | 1.000 | 0.406 | 0.326 | 0.000 | 0.594 | 0.674 | 0.406 | 1.000 | 0.000 |
| action_mismatch | b_source_align_attention_copy_long | 122 | 19 | 0.689 | 0.770 | 0.451 | 0.139 | -0.082 | 0.238 | 0.549 | 0.451 | 0.672 | 0.230 |
| matched | b_source_align_attention_copy_long | 176 | 22 | 0.642 | 0.733 | 0.364 | 0.642 | -0.091 | 0.278 | 0.000 | 0.318 | 0.432 | 0.267 |
| same_action | b_source_align_attention_copy_long | 175 | 22 | 0.771 | 0.869 | 0.377 | 0.383 | -0.097 | 0.394 | 0.389 | 0.406 | 0.777 | 0.131 |
| action_mismatch | b_behavior_distill | 122 | 19 | 0.361 | 0.746 | 0.434 | 0.197 | -0.385 | -0.074 | 0.164 | 0.451 | 0.418 | 0.254 |
| matched | b_behavior_distill | 176 | 22 | 0.250 | 0.676 | 0.415 | 0.250 | -0.426 | -0.165 | 0.000 | 0.318 | 0.295 | 0.324 |
| same_action | b_behavior_distill | 175 | 22 | 0.394 | 0.720 | 0.377 | 0.223 | -0.326 | 0.017 | 0.171 | 0.406 | 0.514 | 0.280 |
| action_mismatch | b_frozen_random | 122 | 19 | 0.164 | 0.762 | 0.164 | 0.197 | -0.598 | 0.000 | -0.033 | 0.451 | 0.197 | 0.238 |
| matched | b_frozen_random | 176 | 22 | 0.193 | 0.727 | 0.159 | 0.193 | -0.534 | 0.034 | 0.000 | 0.318 | 0.182 | 0.273 |
| same_action | b_frozen_random | 175 | 22 | 0.166 | 0.731 | 0.131 | 0.200 | -0.566 | 0.034 | -0.034 | 0.406 | 0.143 | 0.269 |

## source_cf_differs_from_donor_source_b_action

| donor | condition | n | seeds | cf action | unpatched action | donor-B action | matched-ref action | cf-vs-unpatched gap | cf-vs-donor-B gap | cf-vs-matched-ref gap | cf=donor-B | cf=unpatched | patch changed |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| action_mismatch | source_full | 67 | 18 | 1.000 | 0.776 | 0.000 | 0.000 | 0.224 | 1.000 | 1.000 | 0.000 | 0.776 | 0.224 |
| matched | source_full | 120 | 22 | 1.000 | 0.317 | 0.000 | 1.000 | 0.683 | 1.000 | 0.000 | 0.000 | 0.317 | 0.683 |
| same_action | source_full | 104 | 22 | 1.000 | 1.000 | 0.000 | 0.442 | 0.000 | 1.000 | 0.558 | 0.000 | 1.000 | 0.000 |
| action_mismatch | b_source_align_attention_copy_long | 67 | 18 | 0.627 | 0.761 | 0.194 | 0.179 | -0.134 | 0.433 | 0.448 | 0.000 | 0.567 | 0.239 |
| matched | b_source_align_attention_copy_long | 120 | 22 | 0.617 | 0.750 | 0.208 | 0.617 | -0.133 | 0.408 | 0.000 | 0.000 | 0.408 | 0.250 |
| same_action | b_source_align_attention_copy_long | 104 | 22 | 0.769 | 0.885 | 0.106 | 0.500 | -0.115 | 0.663 | 0.269 | 0.000 | 0.760 | 0.115 |
| action_mismatch | b_behavior_distill | 67 | 18 | 0.299 | 0.731 | 0.433 | 0.254 | -0.433 | -0.134 | 0.045 | 0.000 | 0.358 | 0.269 |
| matched | b_behavior_distill | 120 | 22 | 0.225 | 0.700 | 0.467 | 0.225 | -0.475 | -0.242 | 0.000 | 0.000 | 0.225 | 0.300 |
| same_action | b_behavior_distill | 104 | 22 | 0.346 | 0.683 | 0.317 | 0.308 | -0.337 | 0.029 | 0.038 | 0.000 | 0.490 | 0.317 |
| action_mismatch | b_frozen_random | 67 | 18 | 0.164 | 0.716 | 0.164 | 0.209 | -0.552 | 0.000 | -0.045 | 0.000 | 0.209 | 0.284 |
| matched | b_frozen_random | 120 | 22 | 0.208 | 0.700 | 0.158 | 0.208 | -0.492 | 0.050 | 0.000 | 0.000 | 0.192 | 0.300 |
| same_action | b_frozen_random | 104 | 22 | 0.173 | 0.673 | 0.115 | 0.183 | -0.500 | 0.058 | -0.010 | 0.000 | 0.173 | 0.327 |

## source_cf_differs_from_target_unpatched_action

| donor | condition | n | seeds | cf action | unpatched action | donor-B action | matched-ref action | cf-vs-unpatched gap | cf-vs-donor-B gap | cf-vs-matched-ref gap | cf=donor-B | cf=unpatched | patch changed |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| action_mismatch | source_full | 20 | 11 | 1.000 | 0.000 | 0.250 | 0.000 | 1.000 | 0.750 | 1.000 | 0.250 | 0.000 | 1.000 |
| matched | source_full | 119 | 19 | 1.000 | 0.000 | 0.311 | 1.000 | 1.000 | 0.689 | 0.000 | 0.311 | 0.000 | 1.000 |
| action_mismatch | b_source_align_attention_copy_long | 40 | 17 | 0.300 | 0.550 | 0.325 | 0.400 | -0.250 | -0.025 | -0.100 | 0.275 | 0.000 | 0.450 |
| matched | b_source_align_attention_copy_long | 100 | 21 | 0.380 | 0.540 | 0.370 | 0.380 | -0.160 | 0.010 | 0.000 | 0.290 | 0.000 | 0.460 |
| same_action | b_source_align_attention_copy_long | 39 | 17 | 0.256 | 0.692 | 0.256 | 0.436 | -0.436 | 0.000 | -0.179 | 0.359 | 0.000 | 0.308 |
| action_mismatch | b_behavior_distill | 71 | 19 | 0.113 | 0.775 | 0.451 | 0.324 | -0.662 | -0.338 | -0.211 | 0.394 | 0.000 | 0.225 |
| matched | b_behavior_distill | 124 | 22 | 0.081 | 0.685 | 0.460 | 0.081 | -0.605 | -0.379 | 0.000 | 0.250 | 0.000 | 0.315 |
| same_action | b_behavior_distill | 85 | 20 | 0.118 | 0.788 | 0.329 | 0.247 | -0.671 | -0.212 | -0.129 | 0.376 | 0.000 | 0.212 |
| action_mismatch | b_frozen_random | 98 | 17 | 0.031 | 0.776 | 0.133 | 0.235 | -0.745 | -0.102 | -0.204 | 0.459 | 0.000 | 0.224 |
| matched | b_frozen_random | 144 | 22 | 0.042 | 0.694 | 0.132 | 0.042 | -0.653 | -0.090 | 0.000 | 0.326 | 0.000 | 0.306 |
| same_action | b_frozen_random | 150 | 22 | 0.053 | 0.713 | 0.113 | 0.187 | -0.660 | -0.060 | -0.133 | 0.427 | 0.000 | 0.287 |

## action_mismatch_rows

| donor | condition | n | seeds | cf action | unpatched action | donor-B action | matched-ref action | cf-vs-unpatched gap | cf-vs-donor-B gap | cf-vs-matched-ref gap | cf=donor-B | cf=unpatched | patch changed |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| action_mismatch | source_full | 122 | 19 | 1.000 | 0.836 | 0.451 | 0.000 | 0.164 | 0.549 | 1.000 | 0.451 | 0.836 | 0.164 |
| action_mismatch | b_source_align_attention_copy_long | 122 | 19 | 0.689 | 0.770 | 0.451 | 0.139 | -0.082 | 0.238 | 0.549 | 0.451 | 0.672 | 0.230 |
| action_mismatch | b_behavior_distill | 122 | 19 | 0.361 | 0.746 | 0.434 | 0.197 | -0.385 | -0.074 | 0.164 | 0.451 | 0.418 | 0.254 |
| action_mismatch | b_frozen_random | 122 | 19 | 0.164 | 0.762 | 0.164 | 0.197 | -0.598 | 0.000 | -0.033 | 0.451 | 0.197 | 0.238 |
