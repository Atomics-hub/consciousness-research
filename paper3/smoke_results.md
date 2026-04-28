# AST Checkpoint Smoke Results

This is a plumbing check, not a Paper 3 result. It evaluates static conditions from the existing Paper 2 checkpoint with the new PreservationBench log-first evaluator.

Command:

```bash
KMP_DUPLICATE_LIB_OK=TRUE OMP_NUM_THREADS=1 python3 \
  experiments/preservation_bench/run_ast_checkpoint_eval.py \
  --config experiments/preservation_bench/configs/ast_checkpoint_smoke.json
```

Summary from 20 paired evaluation episodes:

| condition | reward | self_report_corr | identity_probe_accuracy | memory_overlap |
| --- | --- | --- | --- | --- |
| source_full | -19.894 | 0.934 | 1.000 | 1.000 |
| source_attention_ablated | -27.355 | 0.000 | 1.000 | 1.000 |
| source_schema_ablated | -20.845 | 0.000 | 1.000 | 1.000 |
| source_self_model_ablated | -19.797 | 0.916 | 0.000 | 0.000 |
| a_to_a_copy | -28.992 | 0.205 | 1.000 | 1.000 |
| b_frozen_copy | -21.412 | 0.036 | 1.000 | 1.000 |
| b_frozen_random | -21.892 | -0.035 | 0.000 | 0.000 |

Interpretation:

- The new evaluator can produce raw episode logs, episode summaries, seed summaries, and manifests.
- Copied self-model and memory payloads pass source-specific identity probes.
- The frozen cross-architecture copy does not preserve strong self-report behavior.
- The random frozen control fails identity probes, as expected.
- This reproduces the Paper 2 pattern in benchmark form: copied state can survive as provenance-sensitive information while failing to recouple as functional report behavior.

Limitations:

- Single checkpoint only.
- No independent training seeds yet.
- No behavior-distillation or full-retrain controls yet.
- This should remain a smoke result until the multiseed protocol exists.

## Repair Smoke

This second smoke adds a small 1000-step fine-tune budget for adapter-only copied repair, fully trainable copied repair, and trainable random repair.

| condition | reward | goals_found | distractor_capture_rate | self_report_corr | identity_probe_accuracy | memory_overlap |
| --- | --- | --- | --- | --- | --- | --- |
| source_full | -20.074 | 0.000 | 0.001 | 0.942 | 1.000 | 1.000 |
| b_frozen_copy | -21.087 | 0.000 | 0.000 | -0.133 | 1.000 | 1.000 |
| b_adapter_repair_copy | -20.724 | 0.000 | 0.000 | 0.061 | 1.000 | 1.000 |
| b_trainable_copy | -20.724 | 0.000 | 0.000 | 0.140 | 0.000 | 1.000 |
| b_behavior_distill | -20.992 | 0.000 | 0.001 | -0.110 | 0.000 | 0.000 |
| b_frozen_random | -20.857 | 0.000 | 0.000 | 0.030 | 0.000 | 0.000 |
| b_trainable_random | -20.857 | 0.000 | 0.000 | -0.004 | 0.000 | 0.000 |

Early read:

- Adapter-only repair improves frozen-copy behavior while preserving identity probes.
- Fully trainable copied repair improves behavior but loses the source-specific identity fingerprint.
- Behavior-only distillation does not pass identity probes and does not recover report behavior in this smoke.
- Memory overlap alone is not enough: `b_trainable_copy` still has copied memory overlap but fails identity probes.
- This supports a key Paper 3 distinction between repair, provenance, and functional recoupling.

## Two-Seed Training Smoke

This smoke trains two tiny source agents from independent seeds with only 5000 source steps. It is a plumbing check for independent training seeds, not a substantive benchmark result.

| training_seed_index | condition | reward | goals_found | distractor_capture_rate | self_report_corr | identity_probe_accuracy | memory_overlap |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | source_full | -21.092 | 0.000 | 0.001 | 0.904 | 1.000 | 0.000 |
| 0 | source_schema_ablated | -21.091 | 0.000 | 0.001 | 0.000 | 1.000 | 0.000 |
| 0 | b_frozen_copy | -22.327 | 0.000 | 0.000 | 0.043 | 1.000 | 0.000 |
| 0 | b_adapter_repair_copy | -22.326 | 0.000 | 0.000 | 0.115 | 1.000 | 0.000 |
| 0 | b_behavior_distill | -21.981 | 0.000 | 0.001 | -0.114 | 0.000 | 0.000 |
| 0 | b_frozen_random | -21.731 | 0.000 | 0.001 | -0.035 | 0.000 | 0.000 |
| 1 | source_full | -20.804 | 0.000 | 0.000 | 1.000 | 1.000 | 1.000 |
| 1 | source_schema_ablated | -20.804 | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 |
| 1 | b_frozen_copy | -21.499 | 0.000 | 0.001 | -0.179 | 1.000 | 1.000 |
| 1 | b_adapter_repair_copy | -22.083 | 0.000 | 0.000 | -0.062 | 1.000 | 1.000 |
| 1 | b_behavior_distill | -20.817 | 0.000 | 0.000 | 0.155 | 0.000 | 0.000 |
| 1 | b_frozen_random | -21.374 | 0.000 | 0.001 | -0.022 | 0.000 | 0.000 |

Paired contrast smoke:

| metric | contrast | n | mean_a | mean_b | mean_diff |
| --- | --- | --- | --- | --- | --- |
| self_report_corr | source_full - source_schema_ablated | 2 | 0.952 | 0.000 | 0.952 |
| self_report_corr | b_adapter_repair_copy - b_frozen_copy | 2 | 0.027 | -0.068 | 0.095 |
| identity_probe_accuracy | b_adapter_repair_copy - b_behavior_distill | 2 | 1.000 | 0.000 | 1.000 |
| reward | b_adapter_repair_copy - b_behavior_distill | 2 | -22.204 | -21.399 | -0.805 |

Early read:

- The scaffold can train independent source seeds and aggregate seed-level condition rows.
- The paired contrast analyzer works on source-seed-level summaries.
- The multiseed runner now writes per-seed manifests and skips completed seeds on resume.
- Source validation gates pass for both smoke seeds using the report-quality gate.
- The source agents are too undertrained for meaningful reward claims.
- Identity probes separate copied payloads from behavior-only distillation across both seeds.
- Memory overlap depends on whether the short source run actually stored goal memories, so it stays diagnostic only.

## Five-Seed Pilot

This pilot trained five independent source agents for 50000 steps each, evaluated 11 conditions with 100 paired evaluation episodes, and wrote 55 seed-level condition summaries. All five source agents passed the report-quality validation gate.

Mean condition profile:

| condition | reward | self_report_corr | identity_probe_accuracy | memory_overlap |
| --- | --- | --- | --- | --- |
| source_full | -21.218 | 0.905 | 1.000 | 1.000 |
| source_schema_ablated | -23.130 | 0.000 | 1.000 | 1.000 |
| source_attention_ablated | -22.163 | 0.000 | 1.000 | 1.000 |
| source_self_model_ablated | -21.584 | 0.907 | 0.000 | 0.000 |
| a_to_a_copy | -22.386 | 0.085 | 1.000 | 1.000 |
| b_frozen_copy | -22.092 | -0.115 | 1.000 | 1.000 |
| b_adapter_repair_copy | -23.086 | 0.005 | 1.000 | 1.000 |
| b_behavior_distill | -22.479 | 0.228 | 0.000 | 0.000 |
| b_frozen_random | -22.099 | -0.028 | 0.000 | 0.000 |
| b_trainable_random | -23.037 | 0.268 | 0.000 | 0.000 |
| b_full_retrain | -25.081 | 0.533 | 0.000 | 0.000 |

Selected paired contrasts:

| metric | contrast | n | mean_diff | 95 percent CI |
| --- | --- | --- | --- | --- |
| self_report_corr | source_full - source_schema_ablated | 5 | 0.905 | 0.848 to 0.951 |
| self_report_corr | b_adapter_repair_copy - b_frozen_copy | 5 | 0.120 | 0.011 to 0.208 |
| self_report_corr | b_adapter_repair_copy - b_behavior_distill | 5 | -0.223 | -0.289 to -0.166 |
| identity_probe_accuracy | b_adapter_repair_copy - b_frozen_random | 5 | 1.000 | 1.000 to 1.000 |
| identity_probe_accuracy | b_adapter_repair_copy - b_behavior_distill | 5 | 1.000 | 1.000 to 1.000 |
| reward | b_adapter_repair_copy - b_frozen_copy | 5 | -0.994 | -2.881 to 0.611 |
| reward | b_adapter_repair_copy - b_full_retrain | 5 | 1.996 | 0.203 to 3.789 |

Early read:

- The validation gate, resumable runner, paired evaluation, and contrast analysis all work at 5 seeds.
- Source report behavior is robustly schema-dependent in this setup.
- Copied payload conditions preserve identity probes and memory overlap across all five seeds.
- Behavior-only and random controls fail identity probes across all five seeds.
- Adapter-only repair modestly improves self-report over frozen copy, but does not restore source-level report behavior.
- Behavior-only distillation can produce more report-like behavior than copied repair while still failing identity probes. This is exactly why Paper 3 needs separate axes for behavior, provenance, and copied-state continuity.
- Reward remains weak and noisy. It should not be a headline metric until source task competence improves.
- With only five seeds, none of this should be framed as a final statistical result.

## Competence V2 Five-Seed Pilot

This pilot uses the smaller competence v2 arena: 7 by 7 grid, full observation window, two goals, one distractor, 60000 source steps, 6000 repair steps, and 100 paired evaluation episodes. Source validation required self-report correlation at or above 0.50, at least 20 self queries, and goals found at or above 0.10. The run was resumed after the initial pass to add `b_source_align_repair_copy`, which freezes the copied schema and self-model while training the target-side attention, adapters, and head to match source attention, reports, features, identity state, and Q-values. Later resumes added `b_source_align_repair_copy_long`, which uses a 24000-step source-alignment budget while sharing the same target-init and finetune seeds as the short source-alignment condition; `b_source_align_policy_copy_long`, which also copies and freezes the source policy head; `b_source_align_attention_copy_long`, which copies and freezes the source attention module and initializes adapters to identity before long source-alignment; `b_source_align_attention_copy_trainable_long`, which copies source attention but leaves it trainable; `b_source_align_attention_copy_random_adapter_long`, which copies and freezes source attention but leaves adapters randomly initialized; `b_source_align_identity_adapter_long`, which keeps target attention but identity-initializes adapters; `b_source_align_attention_adapter_long`, which keeps target transformer attention but adds a residual source-facing interface adapter; and `b_source_align_control_adapter_long`, which keeps that bridge while adding explicit control and attention-mass losses. The copied-attention conditions are coupling diagnostics because they deliberately narrow the substrate gap. The attention-adapter and control-adapter conditions are bridge diagnostics because they keep the target attention substrate but change the source-facing interface.

Four of five source seeds passed validation. Seed 2 found goals well but failed the self-report gate, so it is useful as a rejected-source example rather than a transfer result.

Source validation:

| training_seed_index | passed | reward | goals_found | self_report_corr | note |
| --- | --- | --- | --- | --- | --- |
| 0 | yes | -4.838 | 0.580 | 1.000 | passed |
| 1 | yes | 2.692 | 1.250 | 0.940 | passed |
| 2 | no | 1.816 | 1.000 | 0.038 | failed self-report gate |
| 3 | yes | 0.824 | 0.110 | 0.979 | passed |
| 4 | yes | 2.344 | 0.250 | 0.792 | passed |

Validated-seed mean condition profile:

| condition | n | reward | goals_found | self_report_corr | identity_probe_accuracy | goal_attention_mass | source_attention_l1 | source_feature_mse | source_action_agreement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| source_full | 4 | 0.255 | 0.547 | 0.928 | 1.000 | 0.275 | 0.000 | 0.000 | 1.000 |
| source_schema_ablated | 4 | -1.677 | 0.463 | 0.000 | 1.000 | 0.252 | 0.000 | 0.000 | 0.803 |
| source_attention_ablated | 4 | -9.432 | 0.255 | 0.000 | 1.000 | 0.027 | 0.037 | 0.068 | 0.207 |
| source_self_model_ablated | 4 | -1.202 | 0.448 | 0.921 | 0.000 | 0.278 | 0.000 | 0.000 | 0.820 |
| b_frozen_copy | 4 | -9.869 | 0.045 | -0.083 | 1.000 | 0.031 | 0.037 | 0.312 | 0.059 |
| b_adapter_repair_copy | 4 | -9.797 | 0.172 | -0.108 | 1.000 | 0.026 | 0.037 | 10.304 | 0.018 |
| b_source_align_repair_copy | 4 | -9.929 | 0.138 | 0.176 | 1.000 | 0.029 | 0.037 | 0.100 | 0.135 |
| b_source_align_repair_copy_long | 4 | -7.693 | 0.090 | 0.247 | 1.000 | 0.111 | 0.036 | 0.078 | 0.071 |
| b_source_align_policy_copy_long | 4 | -10.281 | 0.040 | 0.157 | 1.000 | 0.057 | 0.037 | 0.105 | 0.071 |
| b_source_align_attention_copy_long | 4 | -1.084 | 0.505 | 0.798 | 1.000 | 0.269 | 0.000 | 0.004 | 0.771 |
| b_source_align_attention_adapter_long | 4 | -11.544 | 0.075 | 0.818 | 1.000 | 0.025 | 0.015 | 0.074 | 0.099 |
| b_source_align_control_adapter_long | 4 | 15.258 | 0.120 | 0.573 | 1.000 | 0.635 | 0.024 | 0.080 | 0.249 |
| b_source_align_attention_copy_trainable_long | 4 | -1.398 | 0.472 | 0.776 | 1.000 | 0.261 | 0.001 | 0.004 | 0.779 |
| b_source_align_attention_copy_random_adapter_long | 4 | -2.365 | 0.482 | 0.776 | 1.000 | 0.254 | 0.000 | 0.008 | 0.771 |
| b_source_align_identity_adapter_long | 4 | -8.465 | 0.138 | 0.299 | 1.000 | 0.073 | 0.035 | 0.079 | 0.104 |
| b_behavior_distill | 4 | -10.883 | 0.085 | 0.142 | 0.000 | 0.031 | 0.037 | 2.202 | 0.063 |
| b_frozen_random | 4 | -10.214 | 0.115 | -0.016 | 0.000 | 0.028 | 0.037 | 0.287 | 0.085 |

Selected validation-aware paired contrasts:

| metric | contrast | n | mean_diff | 95 percent CI | p | Holm significant |
| --- | --- | --- | --- | --- | --- | --- |
| self_report_corr | source_full - source_schema_ablated | 4 | 0.928 | 0.838 to 0.989 | 0.1249 | no |
| self_report_corr | b_adapter_repair_copy - b_frozen_copy | 4 | -0.025 | -0.115 to 0.042 | 0.8809 | no |
| self_report_corr | b_source_align_repair_copy - b_frozen_copy | 4 | 0.259 | 0.114 to 0.371 | 0.1249 | no |
| self_report_corr | b_source_align_repair_copy_long - b_frozen_copy | 4 | 0.331 | 0.205 to 0.456 | 0.1249 | no |
| self_report_corr | b_source_align_repair_copy_long - b_source_align_repair_copy | 4 | 0.071 | -0.051 to 0.157 | 0.2440 | no |
| self_report_corr | b_source_align_policy_copy_long - b_source_align_repair_copy_long | 4 | -0.090 | -0.248 to 0.066 | 0.4968 | no |
| self_report_corr | b_source_align_attention_copy_long - b_source_align_repair_copy_long | 4 | 0.550 | 0.459 to 0.621 | 0.1249 | no |
| self_report_corr | b_source_align_attention_adapter_long - b_source_align_repair_copy_long | 4 | 0.570 | 0.398 to 0.671 | 0.1249 | no |
| self_report_corr | b_source_align_control_adapter_long - b_source_align_repair_copy_long | 4 | 0.325 | -0.021 to 0.609 | 0.2567 | no |
| self_report_corr | b_source_align_control_adapter_long - b_source_align_attention_copy_long | 4 | -0.225 | -0.586 to -0.012 | 0.2460 | no |
| self_report_corr | b_source_align_attention_copy_trainable_long - b_source_align_repair_copy_long | 4 | 0.528 | 0.412 to 0.614 | 0.1249 | no |
| self_report_corr | b_source_align_attention_copy_random_adapter_long - b_source_align_repair_copy_long | 4 | 0.529 | 0.460 to 0.599 | 0.1249 | no |
| self_report_corr | b_source_align_identity_adapter_long - b_source_align_repair_copy_long | 4 | 0.052 | -0.124 to 0.258 | 0.7569 | no |
| self_report_corr | b_source_align_attention_adapter_long - b_source_align_attention_copy_long | 4 | 0.020 | -0.061 to 0.100 | 0.6366 | no |
| self_report_corr | b_source_align_attention_copy_trainable_long - b_source_align_attention_copy_long | 4 | -0.022 | -0.049 to 0.005 | 0.5017 | no |
| self_report_corr | b_source_align_attention_copy_trainable_long - b_source_align_attention_copy_random_adapter_long | 4 | -0.001 | -0.048 to 0.047 | 0.7577 | no |
| self_report_corr | b_source_align_attention_copy_long - b_source_align_attention_copy_random_adapter_long | 4 | 0.021 | -0.008 to 0.051 | 0.5019 | no |
| self_report_corr | b_source_align_attention_copy_long - b_source_align_identity_adapter_long | 4 | 0.499 | 0.294 to 0.714 | 0.1249 | no |
| self_report_corr | b_source_align_policy_copy_long - b_frozen_copy | 4 | 0.240 | 0.162 to 0.319 | 0.1249 | no |
| self_report_corr | b_source_align_attention_copy_long - b_frozen_copy | 4 | 0.881 | 0.666 to 1.048 | 0.1249 | no |
| self_report_corr | b_source_align_repair_copy - b_behavior_distill | 4 | 0.034 | -0.119 to 0.188 | 0.8760 | no |
| self_report_corr | b_source_align_repair_copy_long - b_behavior_distill | 4 | 0.106 | -0.031 to 0.249 | 0.3769 | no |
| self_report_corr | b_source_align_policy_copy_long - b_behavior_distill | 4 | 0.015 | -0.174 to 0.185 | 1.0000 | no |
| self_report_corr | b_source_align_attention_copy_long - b_behavior_distill | 4 | 0.656 | 0.428 to 0.861 | 0.1249 | no |
| self_report_corr | b_adapter_repair_copy - b_behavior_distill | 4 | -0.250 | -0.337 to -0.162 | 0.1249 | no |
| identity_probe_accuracy | b_adapter_repair_copy - b_frozen_random | 4 | 1.000 | 1.000 to 1.000 | 0.1249 | no |
| identity_probe_accuracy | b_source_align_repair_copy - b_frozen_random | 4 | 1.000 | 1.000 to 1.000 | 0.1249 | no |
| identity_probe_accuracy | b_source_align_repair_copy_long - b_frozen_random | 4 | 1.000 | 1.000 to 1.000 | 0.1249 | no |
| identity_probe_accuracy | b_source_align_policy_copy_long - b_frozen_random | 4 | 1.000 | 1.000 to 1.000 | 0.1249 | no |
| identity_probe_accuracy | b_source_align_attention_copy_long - b_frozen_random | 4 | 1.000 | 1.000 to 1.000 | 0.1249 | no |
| identity_probe_accuracy | b_source_align_attention_adapter_long - b_frozen_random | 4 | 1.000 | 1.000 to 1.000 | 0.1249 | no |
| identity_probe_accuracy | b_source_align_attention_copy_trainable_long - b_frozen_random | 4 | 1.000 | 1.000 to 1.000 | 0.1249 | no |
| identity_probe_accuracy | b_source_align_attention_copy_random_adapter_long - b_frozen_random | 4 | 1.000 | 1.000 to 1.000 | 0.1249 | no |
| identity_probe_accuracy | b_source_align_identity_adapter_long - b_frozen_random | 4 | 1.000 | 1.000 to 1.000 | 0.1249 | no |
| identity_probe_accuracy | b_source_align_repair_copy - b_behavior_distill | 4 | 1.000 | 1.000 to 1.000 | 0.1249 | no |
| identity_probe_accuracy | b_source_align_repair_copy_long - b_behavior_distill | 4 | 1.000 | 1.000 to 1.000 | 0.1249 | no |
| identity_probe_accuracy | b_source_align_policy_copy_long - b_behavior_distill | 4 | 1.000 | 1.000 to 1.000 | 0.1249 | no |
| identity_probe_accuracy | b_source_align_attention_copy_long - b_behavior_distill | 4 | 1.000 | 1.000 to 1.000 | 0.1249 | no |
| identity_probe_accuracy | b_source_align_attention_copy_trainable_long - b_behavior_distill | 4 | 1.000 | 1.000 to 1.000 | 0.1249 | no |
| identity_probe_accuracy | b_source_align_attention_copy_random_adapter_long - b_behavior_distill | 4 | 1.000 | 1.000 to 1.000 | 0.1249 | no |
| identity_probe_accuracy | b_source_align_identity_adapter_long - b_behavior_distill | 4 | 1.000 | 1.000 to 1.000 | 0.1249 | no |
| identity_probe_accuracy | b_adapter_repair_copy - b_behavior_distill | 4 | 1.000 | 1.000 to 1.000 | 0.1249 | no |
| reward | b_adapter_repair_copy - b_frozen_copy | 4 | 0.072 | -0.594 to 0.624 | 0.8809 | no |
| reward | b_source_align_repair_copy - b_frozen_copy | 4 | -0.060 | -0.747 to 0.556 | 0.8789 | no |
| reward | b_source_align_repair_copy_long - b_frozen_copy | 4 | 2.176 | -0.684 to 5.423 | 0.3732 | no |
| reward | b_source_align_repair_copy_long - b_source_align_repair_copy | 4 | 2.236 | -1.055 to 5.990 | 0.5019 | no |
| reward | b_source_align_policy_copy_long - b_source_align_repair_copy_long | 4 | -2.588 | -7.868 to 1.664 | 0.4964 | no |
| reward | b_source_align_attention_copy_long - b_source_align_repair_copy_long | 4 | 6.609 | 5.250 to 7.967 | 0.1249 | no |
| reward | b_source_align_attention_adapter_long - b_source_align_repair_copy_long | 4 | -3.851 | -7.354 to -0.552 | 0.2537 | no |
| reward | b_source_align_control_adapter_long - b_source_align_repair_copy_long | 4 | 22.951 | 8.580 to 30.929 | 0.1249 | no |
| reward | b_source_align_control_adapter_long - b_source_align_attention_copy_long | 4 | 16.342 | 2.712 to 24.112 | 0.2460 | no |
| reward | b_source_align_attention_copy_trainable_long - b_source_align_repair_copy_long | 4 | 6.295 | 5.156 to 7.608 | 0.1249 | no |
| reward | b_source_align_attention_copy_random_adapter_long - b_source_align_repair_copy_long | 4 | 5.328 | 4.416 to 5.937 | 0.1249 | no |
| reward | b_source_align_identity_adapter_long - b_source_align_repair_copy_long | 4 | -0.772 | -2.357 to 0.076 | 0.7440 | no |
| reward | b_source_align_attention_adapter_long - b_source_align_attention_copy_long | 4 | -10.460 | -12.485 to -8.533 | 0.1249 | no |
| reward | b_source_align_attention_copy_trainable_long - b_source_align_attention_copy_long | 4 | -0.314 | -0.770 to 0.191 | 0.3700 | no |
| reward | b_source_align_attention_copy_trainable_long - b_source_align_attention_copy_random_adapter_long | 4 | 0.966 | 0.278 to 1.989 | 0.1249 | no |
| reward | b_source_align_attention_copy_long - b_source_align_attention_copy_random_adapter_long | 4 | 1.281 | 0.195 to 2.526 | 0.2460 | no |
| reward | b_source_align_attention_copy_long - b_source_align_identity_adapter_long | 4 | 7.381 | 5.174 to 9.588 | 0.1249 | no |
| reward | b_source_align_policy_copy_long - b_frozen_copy | 4 | -0.412 | -2.132 to 1.057 | 0.7472 | no |
| reward | b_source_align_attention_copy_long - b_frozen_copy | 4 | 8.785 | 5.608 to 11.346 | 0.1249 | no |
| reward | b_source_align_repair_copy - b_behavior_distill | 4 | 0.955 | 0.257 to 1.788 | 0.2460 | no |
| reward | b_source_align_repair_copy_long - b_behavior_distill | 4 | 3.190 | -0.184 to 7.312 | 0.2460 | no |
| reward | b_source_align_policy_copy_long - b_behavior_distill | 4 | 0.602 | -0.459 to 1.382 | 0.3799 | no |
| reward | b_source_align_attention_copy_long - b_behavior_distill | 4 | 9.799 | 5.752 to 13.235 | 0.1249 | no |
| reward | b_adapter_repair_copy - b_behavior_distill | 4 | 1.086 | 0.542 to 1.783 | 0.1249 | no |
| goal_attention_mass | b_source_align_attention_copy_long - b_source_align_repair_copy_long | 4 | 0.158 | -0.000 to 0.317 | 0.3807 | no |
| goal_attention_mass | b_source_align_attention_adapter_long - b_source_align_repair_copy_long | 4 | -0.086 | -0.162 to -0.010 | 0.2537 | no |
| goal_attention_mass | b_source_align_control_adapter_long - b_source_align_repair_copy_long | 4 | 0.524 | 0.158 to 0.739 | 0.2460 | no |
| goal_attention_mass | b_source_align_control_adapter_long - b_source_align_attention_copy_long | 4 | 0.365 | 0.074 to 0.637 | 0.2460 | no |
| goal_attention_mass | b_source_align_attention_copy_trainable_long - b_source_align_repair_copy_long | 4 | 0.151 | -0.008 to 0.310 | 0.3807 | no |
| goal_attention_mass | b_source_align_attention_adapter_long - b_source_align_attention_copy_long | 4 | -0.244 | -0.374 to -0.114 | 0.1249 | no |
| source_action_agreement | b_source_align_attention_copy_long - b_source_align_repair_copy_long | 4 | 0.700 | 0.596 to 0.819 | 0.1249 | no |
| source_action_agreement | b_source_align_attention_adapter_long - b_source_align_repair_copy_long | 4 | 0.027 | -0.007 to 0.089 | 1.0000 | no |
| source_action_agreement | b_source_align_control_adapter_long - b_source_align_repair_copy_long | 4 | 0.177 | -0.003 to 0.358 | 0.3732 | no |
| source_action_agreement | b_source_align_control_adapter_long - b_source_align_attention_copy_long | 4 | -0.523 | -0.621 to -0.416 | 0.1249 | no |
| source_action_agreement | b_source_align_attention_copy_trainable_long - b_source_align_repair_copy_long | 4 | 0.707 | 0.572 to 0.815 | 0.1249 | no |
| source_action_agreement | b_source_align_attention_adapter_long - b_source_align_attention_copy_long | 4 | -0.673 | -0.735 to -0.596 | 0.1249 | no |
| source_attention_l1 | b_source_align_attention_copy_long - b_source_align_repair_copy_long | 4 | -0.036 | -0.038 to -0.033 | 0.1249 | no |
| source_attention_l1 | b_source_align_attention_adapter_long - b_source_align_repair_copy_long | 4 | -0.020 | -0.034 to -0.008 | 0.1249 | no |
| source_attention_l1 | b_source_align_control_adapter_long - b_source_align_attention_copy_long | 4 | 0.023 | 0.008 to 0.034 | 0.1249 | no |
| source_attention_l1 | b_source_align_attention_copy_trainable_long - b_source_align_repair_copy_long | 4 | -0.034 | -0.038 to -0.031 | 0.1249 | no |
| source_attention_l1 | b_source_align_attention_adapter_long - b_source_align_attention_copy_long | 4 | 0.015 | 0.005 to 0.024 | 0.1249 | no |
| source_feature_mse | b_source_align_attention_copy_long - b_source_align_repair_copy_long | 4 | -0.075 | -0.096 to -0.054 | 0.1249 | no |
| source_feature_mse | b_source_align_attention_adapter_long - b_source_align_repair_copy_long | 4 | -0.004 | -0.007 to -0.001 | 0.2537 | no |
| source_feature_mse | b_source_align_control_adapter_long - b_source_align_attention_copy_long | 4 | 0.077 | 0.050 to 0.104 | 0.1249 | no |
| source_feature_mse | b_source_align_attention_copy_trainable_long - b_source_align_repair_copy_long | 4 | -0.074 | -0.097 to -0.054 | 0.1249 | no |
| source_feature_mse | b_source_align_attention_adapter_long - b_source_align_attention_copy_long | 4 | 0.070 | 0.051 to 0.091 | 0.1249 | no |

Early read:

- The competence v2 task is a better AST v0 basis than the first sparse-reward pilot.
- Source self-report is strong and schema-dependent in the four validated seeds.
- Source attention ablation causes the largest reward drop, which is useful for the benchmark profile.
- Copied identity and memory payloads still separate cleanly from behavior-only and random controls.
- Frozen copied transfer and adapter-only repair still do not recouple self-report behavior in the target substrate.
- Source-alignment repair improves self-report over frozen copy while preserving copied identity, but it remains far below source-level report continuity and does not recover task reward.
- Longer source-alignment improves mean self-report and reward relative to short source-alignment, but the reward gain is seed-variable and goals found do not improve.
- Copying and freezing the source policy head during long source-alignment does not help in this setup. It preserves identity but lowers mean reward and self-report relative to long source-alignment without the copied policy.
- Copying and freezing the source attention module with identity-initialized adapters produces the strongest transfer profile so far: near-source reward, strong self-report, preserved identity, and restored goals found. This suggests attention/interface coupling is the current leading bottleneck.
- Copying source attention and leaving it trainable remains close to the frozen copied-attention condition while preserving identity probes. The copied attention initialization is still doing useful work even when the module can adapt.
- Copying and freezing source attention remains strong with randomly initialized adapters, so the copied-attention effect is not mainly explained by identity adapter initialization.
- Identity-initialized adapters without copied attention do not recover reward or report behavior. That makes the target attention/front-end the likeliest bottleneck in the current design.
- The source-facing attention-adapter bridge recovers strong self-report and preserves copied identity but fails reward and goal recovery. This is a useful dissociation: report-interface recoupling can be made to look source-like without restoring task-control continuity.
- The attention-control diagnostics make the dissociation explicit. Copied-attention conditions recover near-source goal attention mass and source action agreement. The adapter bridge has high self-report but low goal attention mass and low source action agreement, so it is report-like without being control-like.
- The control-adapter bridge drives reward and goal-attention mass far above source, while goals found, source action agreement, and report continuity remain below the copied-attention family. This looks like attention-reward proxy optimization, not source-like task-control preservation.
- The new preservation-profile figure makes this visible: the control adapter overshoots reward and goal-attention mass but stays weak on goals found and source-action agreement.
- The copied-attention result should not be framed as a clean cross-architecture transfer success, because it intentionally narrows the target substrate gap.
- Behavior-only distillation can produce some report-like behavior while failing identity probes, which supports the benchmark's split between behavior, provenance, and copied-state continuity.
- The result remains a pilot, not a final statistical result. The next work should freeze this condition family and replicate the core contrasts at 8 to 10 seeds before adding more transfer variants.

## Competence V2 Core 10-Seed Replication

This reduced replication used `ast_competence_v2_core_10seed.json`. It attempted 10 independent source seeds and retained the core condition family: source ablations, frozen copy, long source-alignment repair, copied attention, attention adapter, control adapter, behavior distillation, and frozen random. Eight of ten source seeds passed validation. Seeds 3 and 5 were rejected because goals found was 0.030, below the 0.100 gate, despite strong self-report.

Validated-seed mean condition profile:

| condition | n | reward | goals_found | self_report_corr | identity_probe_accuracy | goal_attention_mass | source_action_agreement |
| --- | --- | --- | --- | --- | --- | --- | --- |
| source_full | 8 | -0.630 | 0.686 | 0.837 | 1.000 | 0.165 | 1.000 |
| source_schema_ablated | 8 | -0.920 | 0.676 | 0.000 | 1.000 | 0.143 | 0.888 |
| source_attention_ablated | 8 | -9.933 | 0.219 | 0.000 | 1.000 | 0.028 | 0.298 |
| source_self_model_ablated | 8 | -1.406 | 0.619 | 0.844 | 0.000 | 0.162 | 0.796 |
| b_frozen_copy | 8 | -10.322 | 0.099 | 0.003 | 1.000 | 0.030 | 0.092 |
| b_source_align_repair_copy_long | 8 | -6.057 | 0.182 | 0.294 | 1.000 | 0.135 | 0.168 |
| b_source_align_attention_copy_long | 8 | -1.638 | 0.628 | 0.796 | 1.000 | 0.156 | 0.849 |
| b_source_align_attention_adapter_long | 8 | -9.263 | 0.116 | 0.892 | 1.000 | 0.082 | 0.191 |
| b_source_align_control_adapter_long | 8 | 16.452 | 0.163 | 0.527 | 1.000 | 0.672 | 0.307 |
| b_behavior_distill | 8 | -10.304 | 0.146 | 0.123 | 0.000 | 0.029 | 0.192 |
| b_frozen_random | 8 | -10.178 | 0.163 | -0.057 | 0.000 | 0.027 | 0.012 |

Selected validation-aware paired contrasts:

| metric | contrast | n | mean_diff | 95 percent CI | p | Holm significant |
| --- | --- | --- | --- | --- | --- | --- |
| self_report_corr | source_full - source_schema_ablated | 8 | 0.837 | 0.708 to 0.953 | 0.0063 | no |
| self_report_corr | b_source_align_attention_copy_long - b_source_align_repair_copy_long | 8 | 0.501 | 0.357 to 0.655 | 0.0063 | no |
| self_report_corr | b_source_align_attention_adapter_long - b_source_align_repair_copy_long | 8 | 0.597 | 0.446 to 0.748 | 0.0063 | no |
| self_report_corr | b_source_align_control_adapter_long - b_source_align_attention_copy_long | 8 | -0.268 | -0.399 to -0.144 | 0.0138 | no |
| reward | b_source_align_attention_copy_long - b_frozen_copy | 8 | 8.684 | 3.745 to 14.035 | 0.0143 | no |
| reward | b_source_align_control_adapter_long - b_source_align_attention_copy_long | 8 | 18.090 | 6.188 to 27.399 | 0.0216 | no |
| goal_attention_mass | b_source_align_control_adapter_long - b_source_align_attention_copy_long | 8 | 0.517 | 0.311 to 0.659 | 0.0138 | no |
| source_action_agreement | b_source_align_attention_copy_long - b_source_align_repair_copy_long | 8 | 0.681 | 0.593 to 0.770 | 0.0063 | no |
| source_action_agreement | b_source_align_control_adapter_long - b_source_align_attention_copy_long | 8 | -0.542 | -0.708 to -0.362 | 0.0063 | no |
| identity_probe_accuracy | b_source_align_attention_copy_long - b_behavior_distill | 8 | 1.000 | 1.000 to 1.000 | 0.0063 | no |

Early read:

- The reduced replication supports the pilot pattern at validated n = 8.
- Source self-report remains schema-dependent, and identity probes still separate copied-payload transfer from behavior-only and random controls.
- Long source-alignment repair improves report over frozen copy, but does not restore source-level goals found or source-action agreement.
- Copied-attention transfer has the strongest combined profile: near-source goals found, strong self-report, copied identity, and high source-action agreement.
- The attention-adapter bridge has the strongest self-report mean, but low goals found and low source-action agreement. It is report-like without being source-control-like.
- The control-adapter bridge drives reward and goal-attention mass far above source, but remains weak on goals found and source-action agreement. This replicates the proxy-control failure mode.
- The copied-attention result is still not a clean cross-architecture success because it narrows the substrate gap. The useful result is the dissociation structure, not a claim that preservation is solved.
