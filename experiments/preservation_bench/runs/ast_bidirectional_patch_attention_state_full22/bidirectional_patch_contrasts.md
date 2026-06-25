# Bidirectional Patch Contrasts

Target-B activations are patched back into source context A and compared with the source-B-to-source-A source counterfactual.

## Condition Summary

| condition | n | seeds | src flip | action agreement | shift match | q-delta error | patched-Q error | donor attention L1 | donor feature MSE |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| source_full | 176 | 22 | 0.955 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| b_source_align_attention_copy_long | 176 | 22 | 0.955 | 0.938 | 0.972 | 0.164 | 0.164 | 0.000 | 0.001 |
| b_behavior_distill | 176 | 22 | 0.955 | 0.210 | 0.767 | 38.063 | 38.063 | 0.035 | 1.869 |
| b_frozen_random | 176 | 22 | 0.955 | 0.199 | 0.761 | 47.177 | 47.177 | 0.035 | 0.223 |

## Paired Seed Deltas

| baseline | metric | seeds | copied-minus-baseline | 95% CI |
| --- | --- | ---: | ---: | --- |
| b_behavior_distill | source_with_donor_interchange_action_agreement | 22 | 0.727 | [0.631, 0.818] |
| b_behavior_distill | source_with_donor_delta_q_mse_to_source | 22 | -37.898 | [-52.053, -24.912] |
| b_behavior_distill | source_with_donor_q_mse_to_source_cf | 22 | -37.898 | [-52.012, -25.171] |
| b_behavior_distill | source_with_donor_delta_self_report_l1_to_source | 22 | -0.009 | [-0.011, -0.006] |
| b_frozen_random | source_with_donor_interchange_action_agreement | 22 | 0.739 | [0.648, 0.824] |
| b_frozen_random | source_with_donor_delta_q_mse_to_source | 22 | -47.012 | [-63.835, -31.946] |
| b_frozen_random | source_with_donor_q_mse_to_source_cf | 22 | -47.012 | [-63.182, -32.217] |
| b_frozen_random | source_with_donor_delta_self_report_l1_to_source | 22 | -0.009 | [-0.011, -0.006] |
