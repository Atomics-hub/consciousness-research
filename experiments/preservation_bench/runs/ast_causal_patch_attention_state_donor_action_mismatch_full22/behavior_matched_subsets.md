# Behavior-Matched Causal Patch Subsets

This report asks whether behavior distillation still fails causal intervention on rows where it matches the ordinary source-A action.

| donor | subset | pairs | seeds | behavior ordinary | behavior causal | copied ordinary | copied causal | copied-behavior causal | copied-behavior q-delta | copied-behavior patched-Q |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| donor_action_mismatch | all_pairs | 128 | 18 | 0.312 | 0.234 | 0.906 | 0.406 | 0.172 | -89.359 | -63.989 |
| donor_action_mismatch | behavior_unpatched_matches_source_a | 40 | 15 | 1.000 | 0.375 | 0.925 | 0.350 | -0.025 | -56.360 | -57.548 |
| donor_action_mismatch | both_unpatched_match_source_a | 37 | 14 | 1.000 | 0.378 | 1.000 | 0.351 | -0.027 | -53.335 | -53.218 |
| donor_action_mismatch | behavior_matches_source_a_and_source_patch_flips | 39 | 15 | 1.000 | 0.385 | 0.923 | 0.333 | -0.051 | -57.414 | -58.407 |
| matched | all_pairs | 176 | 22 | 0.369 | 0.256 | 0.909 | 0.875 | 0.619 | -109.146 | -88.539 |
| matched | behavior_unpatched_matches_source_a | 65 | 20 | 1.000 | 0.154 | 0.923 | 0.923 | 0.769 | -79.194 | -80.841 |
| matched | both_unpatched_match_source_a | 60 | 19 | 1.000 | 0.167 | 1.000 | 0.933 | 0.767 | -78.076 | -79.246 |
| matched | behavior_matches_source_a_and_source_patch_flips | 63 | 20 | 1.000 | 0.143 | 0.937 | 0.921 | 0.778 | -79.424 | -79.683 |
