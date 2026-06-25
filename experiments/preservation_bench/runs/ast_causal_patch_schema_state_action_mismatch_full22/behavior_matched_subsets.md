# Behavior-Matched Causal Patch Subsets

This report asks whether behavior distillation still fails causal intervention on rows where it matches the ordinary source-A action.

| donor | subset | pairs | seeds | behavior ordinary | behavior causal | copied ordinary | copied causal | copied-behavior causal | copied-behavior q-delta | copied-behavior patched-Q |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| action_mismatch | all_pairs | 122 | 19 | 0.516 | 0.361 | 0.730 | 0.689 | 0.328 | -1.010 | -9.804 |
| action_mismatch | behavior_unpatched_matches_source_a | 63 | 16 | 1.000 | 0.571 | 0.794 | 0.714 | 0.143 | -0.977 | -4.437 |
| action_mismatch | both_unpatched_match_source_a | 50 | 15 | 1.000 | 0.620 | 1.000 | 0.840 | 0.220 | -0.958 | -4.475 |
| action_mismatch | behavior_matches_source_a_and_source_patch_flips | 13 | 7 | 1.000 | 0.000 | 0.538 | 0.308 | 0.308 | -0.854 | -4.585 |
| matched | all_pairs | 176 | 22 | 0.517 | 0.250 | 0.778 | 0.642 | 0.392 | -1.826 | -8.882 |
| matched | behavior_unpatched_matches_source_a | 91 | 21 | 1.000 | 0.209 | 0.846 | 0.626 | 0.418 | -1.793 | -5.404 |
| matched | both_unpatched_match_source_a | 77 | 19 | 1.000 | 0.234 | 1.000 | 0.571 | 0.338 | -1.908 | -5.613 |
| matched | behavior_matches_source_a_and_source_patch_flips | 61 | 15 | 1.000 | 0.049 | 0.803 | 0.443 | 0.393 | -1.712 | -5.051 |
| same_action | all_pairs | 175 | 22 | 0.514 | 0.394 | 0.777 | 0.771 | 0.377 | -1.505 | -8.733 |
| same_action | behavior_unpatched_matches_source_a | 90 | 21 | 1.000 | 0.656 | 0.844 | 0.844 | 0.189 | -1.311 | -4.816 |
| same_action | both_unpatched_match_source_a | 76 | 19 | 1.000 | 0.632 | 1.000 | 0.947 | 0.316 | -1.352 | -4.877 |
| same_action | behavior_matches_source_a_and_source_patch_flips | 0 | 0 | nan | nan | nan | nan | nan | nan | nan |
