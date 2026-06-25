# Paper 5 Evidence Gate

This note states what the current Paper 5 package proves, what it does not prove, and what would still kill the claim.

## Claim Lock

In this toy PreservationBench-AST substrate-transfer setting, copied source attention preserves source-specific causal response geometry under schema-state and attention-state interchange interventions better than behavior-only distillation and frozen random controls. The attention-state variable also passes a same-dimensional bidirectional target-to-source causal-role check.

The key evidence is not ordinary task behavior. The key evidence is intervention behavior: when source-B internal state is patched into source-A or target-A context, copied attention follows the source counterfactual substantially more than behavior distillation does.

The bidirectional follow-up asks the reverse question: when each condition's target-B attention state is patched back into source-A, does the source recover its own B-to-A counterfactual? Copied attention does; behavior distillation and frozen random mostly do not.

## Sharpest Current Results

The behavior-matched subset is the sharpest ordinary-behavior versus causal-intervention contrast.

It keeps rows where behavior distillation already matches the ordinary source-A action, then asks whether the model follows the source counterfactual after intervention.

```text
schema matched donors:    behavior_distill=0.209 copied_attention=0.626
attention matched donors: behavior_distill=0.108 copied_attention=0.923
```

This is the core Paper 5 distinction: behavior matching can hold on the ordinary trajectory while causal preservation fails under intervention.

The bidirectional target-to-source attention pass is the sharpest same-variable causal-role result. It asks whether target-B state can substitute for source-B state inside the source:

```text
source_full       action_agreement=1.000 q_delta_error=0.0000
copied_attention action_agreement=0.938 q_delta_error=0.1642
behavior_distill action_agreement=0.210 q_delta_error=38.0626
frozen_random    action_agreement=0.199 q_delta_error=47.1765
```

## Full-Panel Anchors

Schema-state action-mismatch donors:

```text
copied_attention interchange_action=0.689 specificity_gap=0.549
behavior_distill interchange_action=0.361 specificity_gap=0.164
frozen_random    interchange_action=0.164 specificity_gap=-0.033
```

Attention-state action-mismatch donors:

```text
copied_attention interchange_action=0.864 specificity_gap=0.778
behavior_distill interchange_action=0.267 specificity_gap=0.006
frozen_random    interchange_action=0.312 specificity_gap=0.170
```

Bidirectional target-to-source attention patch:

```text
source_full       action_agreement=1.000 q_delta_error=0.0000
copied_attention action_agreement=0.938 q_delta_error=0.1642
behavior_distill action_agreement=0.210 q_delta_error=38.0626
frozen_random    action_agreement=0.199 q_delta_error=47.1765
```

## What This Proves

- Interchange interventions can separate ordinary behavioral matching from causal-mechanism preservation in this benchmark.
- Copied attention preserves more source-specific counterfactual structure than behavior distillation in the tested source panels.
- The effect survives a behavior-matched subset check, which makes output-level matching an insufficient explanation.
- A leakage audit rules out stale matched-reference leakage and, for the schema-state panel, makes raw donor-B action copying an insufficient explanation.
- A hard attention-state donor-action-mismatch follow-up preserves copied attention's Q-geometry advantage, but shows that its discrete action advantage is only partial on that decoupled slice.
- A bidirectional target-to-source attention pass shows that copied-attention target activations can substitute for source attention state under the same toy alignment, unlike behavior-distilled or frozen-random target activations.

## What This Does Not Prove

- It does not prove consciousness.
- It does not prove survival or personal identity.
- It does not prove Attention Schema Theory is true.
- It does not prove copied attention is sufficient for preservation outside this toy architecture.
- It does not solve general representation alignment; the bidirectional pass uses same-dimensional identity attention alignment.
- It does not rule out stronger behavior-distillation methods that explicitly train on intervention data.

## Residual Risks And Future Stress Tests

These do not block the bounded Paper 5 claim, but they would be the next ways to attack or generalize it:

- Non-identity bidirectional alignment or learned stitching where dimensions allow it.
- Stronger behavior-only baselines trained on richer ordinary trajectories but not intervention labels.
- Additional causal variables beyond schema-state and attention-state activations.
- Larger source panels or repeated master seeds to test whether the source-specific gap is stable.

The donor-action-mismatch panel is already included in the main results as a limitation-first robustness audit. Render, citation, figure, and table audits should be rerun if the manuscript, references, or result presentation change.
