# Paper 5 Leakage And Shortcut Audit

Audit date: June 16, 2026.

This note summarizes the action-level leakage audit over the two full Paper 5 causal-patching panels. It asks whether the apparent causal-preservation result can be explained by trivial action shortcuts:

- preserving the target's unpatched action;
- copying the donor source-B ordinary action;
- following the stale matched-reference counterfactual action.

The full generated reports are:

- `experiments/preservation_bench/runs/ast_causal_patch_schema_state_action_mismatch_full22/leakage_audit.md`
- `experiments/preservation_bench/runs/ast_causal_patch_attention_state_action_mismatch_full22/leakage_audit.md`

## Schema-State Action-Mismatch Rows

On all schema-state action-mismatch rows, copied attention followed the donor-specific source counterfactual more than raw donor-B action and much more than the stale matched reference:

```text
copied attention: cf=0.689 unpatched=0.770 donor_B=0.451 matched_ref=0.139
behavior distill: cf=0.361 unpatched=0.746 donor_B=0.434 matched_ref=0.197
frozen random:    cf=0.164 unpatched=0.762 donor_B=0.164 matched_ref=0.197
```

On the stricter subset where the source counterfactual action differs from the donor's ordinary source-B action, copied attention still favored the counterfactual over raw donor-B action:

```text
copied attention: n=67 cf=0.627 donor_B=0.194 matched_ref=0.179
behavior distill: n=67 cf=0.299 donor_B=0.433 matched_ref=0.254
frozen random:    n=67 cf=0.164 donor_B=0.164 matched_ref=0.209
```

This makes raw donor-action copying an insufficient explanation for the schema-state result.

However, schema-state action labels do not fully rule out target-action inertia. In these selected rows, source counterfactual action often equals the target's unpatched action. The audit therefore supports a bounded claim: schema-state patching rules out stale matched-reference leakage and raw donor-B action copying better than it rules out every possible action-inertia shortcut.

## Attention-State Action-Mismatch Rows

On attention-state action-mismatch rows, copied attention strongly exceeded unpatched-action and stale-reference agreement:

```text
copied attention: cf=0.864 unpatched=0.523 donor_B=0.852 matched_ref=0.085
behavior distill: cf=0.267 unpatched=0.347 donor_B=0.290 matched_ref=0.261
frozen random:    cf=0.312 unpatched=0.619 donor_B=0.301 matched_ref=0.142
```

This rules out stale matched-reference leakage and makes pure unpatched-action inertia implausible for the attention-state panel.

The attention-state panel does not cleanly separate source counterfactual action from the donor's ordinary source-B action: in action-mismatch rows, those actions are equal in 0.972 of cases. The current attention-state result is therefore a strong causal-intervention effect but not, by itself, a clean raw-donor-action leakage disambiguation.

## Attention-State Donor-Action-Mismatch Follow-Up

A follow-up full 22-source panel deliberately selected donors where the donor's ordinary source-B action differs from the source counterfactual action caused by patching that donor into source context A.

This produced 128 decoupled rows across 18 source seeds.

```text
source_full:      cf=1.000 donor_B=0.000 matched_ref=0.492 q_delta=0.0000
copied attention: cf=0.406 donor_B=0.508 matched_ref=0.438 q_delta=0.1386
behavior distill: cf=0.234 donor_B=0.242 matched_ref=0.266 q_delta=89.4973
frozen random:    cf=0.297 donor_B=0.172 matched_ref=0.234 q_delta=34.8843
```

Paired by source seed, copied attention exceeded behavior distillation on source-counterfactual action agreement by 0.259 with bootstrap interval [0.035, 0.484]. It also sharply reduced Q-delta error versus behavior distillation and frozen random. However, copied attention did not dominate the donor-B action label on discrete action agreement, and its action advantage over frozen random was not stable.

This makes the attention-state evidence more nuanced: copied attention preserves counterfactual geometry under the hard decoupled donor test, but action-level causal preservation is only partial.

## Interpretation

The leakage audit improves the Paper 5 claim in two ways:

- The schema-state panel provides the cleaner anti-leakage evidence against raw donor-action copying.
- The attention-state panel provides the stronger causal-preservation effect, while the donor-action-mismatch follow-up shows that this effect is much cleaner in Q geometry than in discrete action labels.

The paper should therefore claim a bounded result, not a complete shortcut-proof result.
