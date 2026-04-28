# PreservationBench Protocol v0

This is the working protocol for Paper 3. The goal is to turn Paper 2 from a single AST transplant assay into a small benchmark for preservation-relevant functional continuity.

## Purpose

PreservationBench asks whether copied internal machinery remains active and source-like after transfer into a target substrate. It does not ask whether the target is conscious. It does not decide personal identity. It tests measurable continuity properties that some theories of preservation treat as relevant.

## Main Question

When a source agent is moved into a target substrate, which theory-relevant capacities survive because source state was preserved, and which capacities reappear only because the target relearned or mimicked behavior?

## Design Principles

- Report a continuity profile, not a single score.
- Separate copied-state preservation from relearning.
- Pair every condition on the same evaluation episodes.
- Treat independently trained source seeds as the unit of inference.
- Include negative controls that should fail source-specific probes.
- Include competence controls so transfer failure is not confused with target incapacity.
- Label all consciousness and identity claims as theory-indexed.

## Benchmark Phases

| Phase | Goal | Output |
| --- | --- | --- |
| Phase 0: Harness | Shared config, seed registry, condition registry, metric registry | Reproducible runner |
| Phase 1: Source Training | Train Substrate A on benchmark tasks | Source checkpoints |
| Phase 2: Source Validation | Verify the source has measurable capacities | Source scorecard |
| Phase 3: Transfer | Move selected payloads into target substrates | Transferred agents |
| Phase 4: Controls | Separate copied-state continuity from relearning and leakage | Control scorecard |
| Phase 5: Evaluation | Matched-seed behavior, report, identity, and causal metrics | Preservation profile |
| Phase 6: Stress Tests | Sensor remaps, noise, delayed queries, changed interface | Robustness profile |

## V0 Scope

V0 should be AST-derived and local.

Tasks:

- attention control and self-report from Paper 2
- identity fingerprint probes from Paper 2
- behavioral autobiographical probes if they can be added cleanly
- delayed report or simple confidence task as a stretch

Substrates:

- A: original Paper 2 source architecture
- A-prime: architecture-matched copy
- B: Paper 2 target architecture with adapters
- D: feedforward or weakened negative control, stretch only

Transfer protocols:

- frozen direct transfer
- copied-trainable repair
- behavior-only distillation
- full retrain
- architecture-matched copy

## Conditions

Primary v0 conditions:

| Condition | Purpose |
| --- | --- |
| source_full | source reference |
| source_attention_ablated | validates attention dependence |
| source_schema_ablated | validates schema dependence |
| source_self_model_ablated | validates self-model dependence |
| a_to_a_copy | separates transfer from architecture gap |
| b_frozen_copy | strict copied-state transfer |
| b_adapter_repair_copy | copied state frozen, target interface repaired |
| b_source_align_repair_copy | copied state frozen, target interface source-aligned |
| b_source_align_repair_copy_long | copied state frozen, target interface source-aligned for a longer budget |
| b_source_align_policy_copy_long | copied state and policy head frozen, target interface source-aligned for a longer budget |
| b_source_align_attention_copy_long | copied attention, schema, and self-model frozen, target interface source-aligned for a longer budget |
| b_source_align_attention_adapter_long | target transformer attention with a residual source-facing interface adapter |
| b_source_align_control_adapter_long | target transformer attention with a residual source-facing interface adapter and explicit control losses |
| b_source_align_attention_copy_trainable_long | copied attention starts trainable, schema and self-model stay frozen, adapters start identity-initialized |
| b_source_align_attention_copy_random_adapter_long | copied attention, schema, and self-model frozen with random trainable adapters and a longer source-alignment budget |
| b_source_align_identity_adapter_long | copied schema and self-model frozen with target attention, identity-initialized adapters, and a longer source-alignment budget |
| b_trainable_copy | copied state with repair |
| b_frozen_random | freeze-matched negative control |
| b_trainable_random | relearning control |
| b_behavior_distill | behavioral mimic without copied state |
| b_full_retrain | target competence ceiling |

## Payloads

Preservation payloads should be explicit and auditable.

| Payload | Why It Matters |
| --- | --- |
| attention schema | AST-style report and attention modeling |
| self-model | source-specific identity and memory probes |
| episodic memory | continuity of stored source experience |
| recurrent state | temporal dynamics and context persistence |
| policy priors | stable action dispositions |
| adapters | interface between copied payload and target substrate |

## Metrics

Primary metrics:

- reward
- goals found
- distractor capture rate
- self-report correlation
- identity probe accuracy
- adaptation steps to threshold

Secondary metrics:

- other-report correlation, only if source validation passes
- memory overlap, diagnostic only
- goal attention mass
- source attention distance
- source feature distance
- training curve area under curve
- parameter and payload size
- frozen and trainable parameter counts

Exploratory metrics:

- Butlin-style indicator profile
- Phi-star side analysis
- hidden-state similarity
- mechanism probes

## Normalized Preservation Score

For descriptive profiles, use:

```text
NPS_m = (transfer_m - random_m) / (source_m - random_m)
```

Clamp only for visualization. Always report raw values too. For loss or distance metrics, invert the scale before normalization.

## Primary Contrasts

Primary contrasts should be named before final runs:

- source_full versus source_schema_ablated
- source_full versus source_attention_ablated
- b_frozen_copy versus b_frozen_random
- b_adapter_repair_copy versus b_frozen_copy
- b_source_align_repair_copy versus b_frozen_copy
- b_source_align_repair_copy_long versus b_frozen_copy
- b_source_align_repair_copy_long versus b_source_align_repair_copy
- b_source_align_policy_copy_long versus b_source_align_repair_copy_long
- b_source_align_attention_copy_long versus b_source_align_repair_copy_long
- b_source_align_attention_adapter_long versus b_source_align_repair_copy_long
- b_source_align_control_adapter_long versus b_source_align_repair_copy_long
- b_source_align_attention_copy_trainable_long versus b_source_align_repair_copy_long
- b_source_align_attention_copy_random_adapter_long versus b_source_align_repair_copy_long
- b_source_align_identity_adapter_long versus b_source_align_repair_copy_long
- b_source_align_attention_adapter_long versus b_source_align_attention_copy_long
- b_source_align_control_adapter_long versus b_source_align_attention_adapter_long
- b_source_align_control_adapter_long versus b_source_align_attention_copy_long
- b_source_align_attention_adapter_long versus b_source_align_attention_copy_trainable_long
- b_source_align_attention_adapter_long versus b_source_align_attention_copy_random_adapter_long
- b_source_align_attention_copy_trainable_long versus b_source_align_attention_copy_long
- b_source_align_attention_copy_trainable_long versus b_source_align_attention_copy_random_adapter_long
- b_source_align_attention_copy_long versus b_source_align_attention_copy_random_adapter_long
- b_source_align_attention_copy_long versus b_source_align_identity_adapter_long
- b_source_align_policy_copy_long versus b_frozen_copy
- b_source_align_attention_copy_long versus b_frozen_copy
- b_source_align_attention_adapter_long versus b_frozen_copy
- b_source_align_control_adapter_long versus b_frozen_copy
- b_source_align_attention_copy_trainable_long versus b_frozen_copy
- b_source_align_attention_copy_random_adapter_long versus b_frozen_copy
- b_source_align_identity_adapter_long versus b_frozen_copy
- b_source_align_repair_copy versus b_behavior_distill
- b_source_align_repair_copy_long versus b_behavior_distill
- b_source_align_policy_copy_long versus b_behavior_distill
- b_source_align_attention_copy_long versus b_behavior_distill
- b_source_align_attention_adapter_long versus b_behavior_distill
- b_source_align_control_adapter_long versus b_behavior_distill
- b_source_align_attention_copy_trainable_long versus b_behavior_distill
- b_source_align_attention_copy_random_adapter_long versus b_behavior_distill
- b_source_align_identity_adapter_long versus b_behavior_distill
- b_adapter_repair_copy versus b_behavior_distill
- b_trainable_copy versus b_trainable_random
- b_trainable_copy versus b_behavior_distill
- a_to_a_copy versus b_frozen_copy
- b_trainable_copy versus b_full_retrain, non-inferiority only with a fixed margin

## Success Criteria

A condition can support a preservation-relevant transfer claim only if:

- it beats matched random and freeze-matched controls on copy-sensitive metrics
- copied modules remain causally used after transfer
- source-specific probes pass in copied conditions and fail in independent controls
- task competence is above a validated floor
- gains cannot be explained by behavior-only distillation under the same adaptation budget

Negative results are publishable if the controls are clean. A result like "identity fingerprints survive but report dynamics do not recouple" is exactly the kind of profile this benchmark is meant to expose.

## Failure Modes To Preregister

- source agent fails validation threshold
- ToM remains at floor
- reward is floor-limited or too sparse
- report correlations become undefined because outputs are constant
- random control outperforms transfer
- copied state passes fingerprint probes but has no causal effect
- full retrain fails, making target competence unclear
- crashed runs or nondeterministic backend drift
- Phi-star state coverage is too sparse

## Claim Language

Use:

- "The benchmark measures preservation-relevant functional continuity."
- "The result is theory-indexed."
- "The result separates copied state from relearning under these controls."
- "This is necessary but not sufficient evidence for preservation claims."

Do not use:

- "The benchmark measures consciousness."
- "The transfer preserves identity."
- "The copied agent survived."
- "This proves scan-copy works."
