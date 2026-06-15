# Paper 4 Results Summary

Boundary: toy functional benchmark only. This is not a consciousness, identity, survival, biological preservation, or whole-agent equivalence result.

## Recurrent Sweep

| Run | Policy family | Delay | Seeds | Target/base warm | Warm improvement | Hidden improvement | Report improvement | Report failures |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Selected source-policy delay 4 | `source-selected` | 4 | 22 | 0.858/0.205 | 0.653 | 0.0964 | 0.0030 |  |
| Unselected source-policy delay 4 | `source-unselected` | 4 | 22 | 0.869/0.205 | 0.665 | 0.0964 | 0.0027 | 2 |
| Unselected source-policy delay 8 | `source-unselected` | 8 | 22 | 0.869/0.188 | 0.682 | 0.0961 | 0.0030 | 2 |
| Shifted-policy delay 4 | `shifted-policy` | 4 | 22 | 0.949/0.193 | 0.756 | 0.1000 | 0.0023 | 3 |
| Random-policy delay 4 | `random-policy` | 4 | 22 | 0.903/0.210 | 0.693 | 0.0998 | 0.0024 | 1 |
| Random-policy delay 8 | `random-policy` | 8 | 22 | 0.903/0.153 | 0.750 | 0.1005 | 0.0025 | 3 |
| Random-policy delay 12 | `random-policy` | 12 | 22 | 0.903/0.193 | 0.710 | 0.1013 | 0.0026 | 2 |
| Random-policy history 16 delay 12 | `random-policy` | 12 | 22 | 0.915/0.188 | 0.727 | 0.1008 | 0.0025 | 0 |
| Random-policy history 16 delay 12 altseed | `random-policy-alt` | 12 | 22 | 0.875/0.159 | 0.716 | 0.1000 | 0.0022 | 3 |
| Scripted-cycle delay 8 | `scripted-cycle` | 8 | 22 | 0.881/0.199 | 0.682 | 0.1007 | 0.0027 | 0 |
| Scripted-cycle stride 2 delay 8 | `scripted-cycle` | 8 | 22 | 0.915/0.165 | 0.750 | 0.1010 | 0.0023 | 1 |
| Scripted-cycle stride 2 delay 12 | `scripted-cycle` | 12 | 22 | 0.898/0.210 | 0.688 | 0.1009 | 0.0022 | 3 |
| Scripted-cycle stride 2 history 16 delay 12 | `scripted-cycle` | 12 | 22 | 0.875/0.170 | 0.705 | 0.1027 | 0.0023 | 2 |

## Perturbation Layer

| Condition | Perturbed action agreement | Attention delta | Q delta MSE | Self-report delta |
| --- | ---: | ---: | ---: | ---: |
| `source_full` | 1.000 | 0.0000 | 0.0000 | 0.0000 |
| `b_source_align_attention_copy_long` | 0.850 | 0.0000 | 0.0208 | 0.0015 |
| `b_source_align_control_adapter_long` | 0.477 | 0.0133 | 1.7609 | 0.0034 |
| `b_source_align_attention_adapter_long` | 0.414 | 0.0049 | 2.1640 | 0.0020 |
| `b_source_align_repair_copy_long` | 0.393 | 0.0057 | 2.2759 | 0.0019 |
| `b_behavior_distill` | 0.384 | 0.0046 | 3.2996 | 0.0019 |
| `b_frozen_random` | 0.214 | 0.0045 | 3.4243 | 0.0019 |

## Working Interpretation

Copied attention is consistently separated from frozen random on warm-action agreement and source-hidden-state distance across selected, deterministic unselected, shifted-policy, random-policy, and scripted-cycle histories. The report channel is positive but trajectory-sensitive, so the paper should argue for history-dependent functional continuity under bounded toy conditions, not consciousness preservation.
