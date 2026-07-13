# Paper 4 Protocol

Working title: **History-Dependent Functional Continuity Under Delayed and Counterfactual Source-State Probes**

Author: Thomas Ryan

Created: 2026-06-01

## Boundary

This paper is a toy functional benchmark paper. It does not test consciousness, personal identity, survival, biological preservation, whole-brain emulation, moral status, or whole-agent equivalence.

The narrow claim under test is:

> In a toy AST-derived agent, copied attention/source-state machinery preserves source-like history-dependent responses better than frozen random target state under delayed, perturbed, and non-source-policy probes.

## Relationship To Paper 3

Paper 3 introduced PreservationBench-AST v0 and showed a profile result:

- frozen copied schema/self-model preserved source-specific identity probes but did not recouple report or control;
- long source-alignment repair improved report without restoring source-like control;
- attention and control bridges separated report, reward proxy, and source-like action;
- copied source attention gave the strongest combined profile, while narrowing the substrate gap.

Paper 4 should not repeat Paper 3. It should ask whether the copied-attention result is brittle clean-episode mimicry or whether it survives harder source-relative probes.

## Main Question

When source history is replayed into target conditions, does the target preserve the source's delayed internal and behavioral response profile?

The key escalation over Paper 3 is that evaluation is no longer only clean paired episodes. Paper 4 uses:

- observation perturbations;
- delayed report probes;
- deterministic unselected histories;
- shifted-policy histories;
- random-policy histories;
- scripted-cycle histories;
- longer histories and longer report delays;
- alternate random master seeds;
- report-failure inspection.

## Primary Condition

Target condition:

- `b_source_align_attention_copy_long`

Baseline:

- `b_frozen_random`

Secondary comparison families:

- source reference;
- long source-alignment repair;
- attention bridge;
- control bridge;
- behavior-only distillation.

## Primary Metrics

Recurrent stress metrics:

- warm-action agreement with source;
- schema hidden-state MSE to source at the probe;
- history-delta self-report L1 distance to source;
- report-delta failure count and failure seeds.

Perturbation metrics:

- perturbed-action agreement;
- action-shift match;
- attention-delta L1 to source;
- feature-delta MSE to source;
- Q-delta MSE to source;
- self-report-delta L1 to source.

## Evidence Gates

A Paper 4 claim can be made only if copied attention:

1. beats frozen random on warm-action agreement in every full22 recurrent family;
2. beats frozen random on hidden-state MSE in every full22 recurrent family;
3. has positive report-delta improvement in every full22 recurrent family;
4. remains strongest or near-strongest in the expanded22 perturbation layer;
5. survives at least one alternate random master seed;
6. reports failure seeds rather than hiding them.

The current generated summary passes all six gates for the bounded claim.

## Forbidden Claims

Do not claim:

- consciousness transferred;
- personal identity survived;
- biological preservation is solved;
- whole-brain emulation would work;
- copied attention is sufficient for consciousness;
- hidden-state similarity is phenomenal continuity;
- report similarity is selfhood.

Allowed wording:

- "history-dependent functional continuity";
- "source-relative stress robustness";
- "toy AST-derived benchmark";
- "copied attention/source-state machinery stayed separated from frozen random";
- "report channel remained positive but trajectory-sensitive."

## Current Asset Sources

Generated Paper 4 assets:

- `paper4/generate_assets.py`
- `paper4/tables/paper4_results_summary.json`
- `paper4/tables/paper4_results_summary.md`
- `paper4/figures/fig1_recurrent_stress_sweep.png`
- `paper4/figures/fig2_perturbation_layer.png`
- `paper4/source_contrasts/`

The public release build uses compact source contrast snapshots under `paper4/source_contrasts/`. The original full local run directories are listed below for provenance but are intentionally not required for rebuilding Paper 4 assets.

Primary recurrent source runs:

- `experiments/preservation_bench/runs/ast_recurrent_delayed_report_hard_full22/`
- `experiments/preservation_bench/runs/ast_recurrent_delayed_report_hard_unselected_full22/`
- `experiments/preservation_bench/runs/ast_recurrent_delayed_report_hard_unselected_delay8_full22/`
- `experiments/preservation_bench/runs/ast_recurrent_delayed_report_hard_shifted_policy_full22/`
- `experiments/preservation_bench/runs/ast_recurrent_delayed_report_hard_random_policy_full22/`
- `experiments/preservation_bench/runs/ast_recurrent_delayed_report_hard_random_policy_delay8_full22/`
- `experiments/preservation_bench/runs/ast_recurrent_delayed_report_hard_random_policy_delay12_full22/`
- `experiments/preservation_bench/runs/ast_recurrent_delayed_report_hard_random_policy_history16_delay12_full22/`
- `experiments/preservation_bench/runs/ast_recurrent_delayed_report_hard_random_policy_history16_delay12_altseed2_full22/`
- `experiments/preservation_bench/runs/ast_recurrent_delayed_report_hard_scripted_cycle_delay8_full22/`
- `experiments/preservation_bench/runs/ast_recurrent_delayed_report_hard_scripted_cycle_stride2_delay8_full22/`
- `experiments/preservation_bench/runs/ast_recurrent_delayed_report_hard_scripted_cycle_stride2_delay12_full22/`
- `experiments/preservation_bench/runs/ast_recurrent_delayed_report_hard_scripted_cycle_stride2_history16_delay12_full22/`

Primary perturbation source run:

- `experiments/preservation_bench/runs/ast_perturbation_core_condition_expanded22_cached/`

## Next Experimental Push

The next meaningful experiment should not be "more of the same" unless it closes a clear critique. Best next candidates:

1. Add a new full22 recurrent family where history is generated by target-policy replay rather than source, random, shifted, or scripted-cycle actions.
2. Add longer delay families only if actual delay completion remains 100 percent or is explicitly modeled.
3. Add a cross-condition "source-state lesion after copied-attention transfer" probe to test whether the preserved signal collapses when copied state is selectively corrupted.
4. Add a small independent architecture variant to reduce the "copied attention narrows the substrate gap" critique.

## Devil's Advocate

The strongest critique is that copied attention is not a clean substrate-transfer result. It is partly a source-module carryover result. That is exactly why the paper should frame the result as bottleneck identification and history-dependent functional continuity, not as clean uploading.

The second critique is that hidden-state similarity can be mechanically preserved when the copied module is reused. The response is to pair hidden-state metrics with warm-action agreement, perturbation response deltas, non-source-policy histories, random master seed changes, and report-failure inspection.

The third critique is that the whole domain is too toy. That critique is correct. The paper should argue that the toy domain is useful because the ground truth interventions are controllable, not because it proves anything about minds.
