# Behavior-Matched Causal Patch Subsets

This report asks whether behavior distillation still fails causal intervention on rows where it matches the ordinary source-A action.

| donor | subset | pairs | seeds | behavior ordinary | behavior causal | copied ordinary | copied causal | copied-behavior causal | copied-behavior q-delta | copied-behavior patched-Q |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| action_mismatch | all_pairs | 176 | 22 | 0.369 | 0.267 | 0.869 | 0.864 | 0.597 | -96.849 | -100.007 |
| action_mismatch | behavior_unpatched_matches_source_a | 65 | 19 | 1.000 | 0.246 | 0.938 | 0.938 | 0.692 | -100.720 | -113.156 |
| action_mismatch | both_unpatched_match_source_a | 61 | 18 | 1.000 | 0.262 | 1.000 | 0.951 | 0.689 | -95.154 | -109.182 |
| action_mismatch | behavior_matches_source_a_and_source_patch_flips | 33 | 14 | 1.000 | 0.152 | 0.909 | 0.879 | 0.727 | -126.439 | -136.284 |
| matched | all_pairs | 176 | 22 | 0.369 | 0.188 | 0.869 | 0.864 | 0.676 | -110.959 | -89.092 |
| matched | behavior_unpatched_matches_source_a | 65 | 19 | 1.000 | 0.108 | 0.938 | 0.923 | 0.815 | -92.176 | -97.450 |
| matched | both_unpatched_match_source_a | 61 | 18 | 1.000 | 0.115 | 1.000 | 0.934 | 0.820 | -78.288 | -86.592 |
| matched | behavior_matches_source_a_and_source_patch_flips | 61 | 19 | 1.000 | 0.082 | 0.934 | 0.918 | 0.836 | -90.606 | -96.300 |
| same_action | all_pairs | 175 | 22 | 0.371 | 0.120 | 0.869 | 0.914 | 0.794 | -91.600 | -96.471 |
| same_action | behavior_unpatched_matches_source_a | 65 | 19 | 1.000 | 0.246 | 0.938 | 0.908 | 0.662 | -110.633 | -123.274 |
| same_action | both_unpatched_match_source_a | 61 | 18 | 1.000 | 0.246 | 1.000 | 0.918 | 0.672 | -106.154 | -121.361 |
| same_action | behavior_matches_source_a_and_source_patch_flips | 0 | 0 | nan | nan | nan | nan | nan | nan | nan |
