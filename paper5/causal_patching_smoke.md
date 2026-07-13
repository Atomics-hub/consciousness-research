# Paper 5 Causal Patching Smoke

This note tracks the first concrete Paper 5 proof path: schema-state interchange interventions in the toy PreservationBench-AST substrate-transfer setting.

## Claim Under Test

After substrate transfer, does a target preserve behaviorally relevant source-causal state, or does it only match source-like behavior/report from the outside?

This smoke does not test consciousness, personal identity, survival, biological preservation, or AST truth. It only tests a toy causal mechanism in the existing benchmark.

## Minimal Design

- Source pool: validated Paper 3/4 source checkpoints from `experiments/preservation_bench/runs/ast_competence_v2_core_10seed`.
- Conditions: `source_full`, `b_source_align_attention_copy_long`, `b_behavior_distill`, `b_frozen_random`.
- Patch path: source schema activation at the probe, before report/self-model/policy readout.
- Selection: choose source A/B history pairs using source-only patch effect, then replay targets on the selected A contexts.
- Intervention: replace the condition's context-A schema activation with the source context-B schema activation before report/self-model/policy readout.
- Primary comparison: does the patched target follow the source counterfactual response for context A with B's source hidden state?

## Command

```bash
KMP_DUPLICATE_LIB_OK=TRUE OMP_NUM_THREADS=1 python3 \
  experiments/preservation_bench/run_ast_causal_patch_probe.py \
  --config experiments/preservation_bench/configs/ast_causal_patch_schema_state_smoke.json
```

## Outputs

Expected outputs:

- `experiments/preservation_bench/runs/ast_causal_patch_schema_state_smoke/manifest.json`
- `experiments/preservation_bench/runs/ast_causal_patch_schema_state_smoke/causal_patch_rows.jsonl`
- `experiments/preservation_bench/runs/ast_causal_patch_schema_state_smoke/causal_patch_summary.json`
- `experiments/preservation_bench/runs/ast_causal_patch_schema_state_smoke/causal_patch_report.md`

## Interpretation Gate

Green criteria for this smoke:

- `source_full` has a nonzero source-side patch effect and perfect within-source interchange agreement.
- `b_source_align_attention_copy_long` separates from `b_behavior_distill` and `b_frozen_random` on source-counterfactual agreement or source-delta distance.
- `b_behavior_distill` can remain plausible on ordinary behavior while looking weaker under intervention.

Kill criteria:

- source-side patching has no stable effect;
- target patching produces no stable counterfactual response;
- behavior-only distillation matches copied attention under the causal intervention;
- the signal is explainable by trivial output leakage rather than hidden-state interchange.

## Current Result

Run completed locally on 2026-06-15 with one validated source seed, 80 source-only candidate A/B pairs, and the top 8 selected source patch pairs.

Exact summary lines:

```text
b_behavior_distill                     n=8 source_flip=0.625 interchange_action=0.625 shift_match=0.375 delta_q_to_source=1.2711 delta_report_to_source=0.0431
b_frozen_random                        n=8 source_flip=0.625 interchange_action=0.125 shift_match=0.250 delta_q_to_source=0.1397 delta_report_to_source=0.0231
b_source_align_attention_copy_long     n=8 source_flip=0.625 interchange_action=0.750 shift_match=0.375 delta_q_to_source=0.0614 delta_report_to_source=0.0079
source_full                            n=8 source_flip=0.625 interchange_action=1.000 shift_match=1.000 delta_q_to_source=0.0000 delta_report_to_source=0.0000
```

Initial read:

- The within-source positive control works for this selected set: 5/8 source patches changed the source action, and `source_full` has perfect interchange agreement.
- Copied attention is the best target condition in this smoke: 0.750 source-counterfactual action agreement, with much lower Q-delta error and report-delta error than behavior distillation.
- Behavior distillation is not a clean negative on action agreement in this tiny sample, but it badly misses the source counterfactual Q/report delta geometry.
- Frozen random remains the clearest negative control on action agreement and patched Q distance to the source counterfactual.

This is a green first smoke for a schema-state causal-patching lane, not a manuscript-level result. It needs multiseed replication, stronger target patch-action movement checks, and leakage controls before Paper 5 can make a stable claim.

Additional exploratory note: direct `schema_hidden` and `last_modulation` recurrent-state patches ran successfully but produced weaker source-side effects in the first bounded configs. The schema activation path is the better first proof target.

## Multiseed Schema-State Smoke
Run completed locally on 2026-06-15 with 4 validated source seeds, 80 source-only candidate A/B pairs per seed, and the top 8 selected source patch pairs per seed. This is still a smoke, but it is the first check of source-level heterogeneity.
Command:
```bash
KMP_DUPLICATE_LIB_OK=TRUE OMP_NUM_THREADS=1 python3 \
  experiments/preservation_bench/run_ast_causal_patch_probe.py \
  --config experiments/preservation_bench/configs/ast_causal_patch_schema_state_multiseed_smoke.json
```
Exact pooled summary:
```text
b_behavior_distill                     n=32 source_flip=0.406 interchange_action=0.219 shift_match=0.344 delta_q_to_source=4.5253 delta_report_to_source=0.0325
b_frozen_random                        n=32 source_flip=0.406 interchange_action=0.062 shift_match=0.406 delta_q_to_source=0.0477 delta_report_to_source=0.0139
b_source_align_attention_copy_long     n=32 source_flip=0.406 interchange_action=0.781 shift_match=0.656 delta_q_to_source=0.2631 delta_report_to_source=0.0034
source_full                            n=32 source_flip=0.406 interchange_action=1.000 shift_match=1.000 delta_q_to_source=0.0000 delta_report_to_source=0.0000
```
Source-flip-only view, restricted to rows where the source patch changed the source action:
```text
b_behavior_distill                     n=13 interchange_action=0.231 shift_match=0.000 delta_q_to_source=1.2723 delta_report_to_source=0.0318
b_frozen_random                        n=13 interchange_action=0.000 shift_match=0.385 delta_q_to_source=0.0682 delta_report_to_source=0.0179
b_source_align_attention_copy_long     n=13 interchange_action=0.462 shift_match=0.154 delta_q_to_source=0.0312 delta_report_to_source=0.0058
source_full                            n=13 interchange_action=1.000 shift_match=1.000 delta_q_to_source=0.0000 delta_report_to_source=0.0000
```
Seed-level result:
```text
seed 0
  source_full                            source_flip=1.000 interchange=1.000 delta_q=0.0000 delta_report=0.0000
  b_source_align_attention_copy_long     source_flip=1.000 interchange=0.625 delta_q=0.0468 delta_report=0.0073
  b_behavior_distill                     source_flip=1.000 interchange=0.375 delta_q=1.8120 delta_report=0.0388
  b_frozen_random                        source_flip=1.000 interchange=0.000 delta_q=0.0899 delta_report=0.0243
seed 1
  source_full                            source_flip=0.000 interchange=1.000 delta_q=0.0000 delta_report=0.0000
  b_source_align_attention_copy_long     source_flip=0.000 interchange=1.000 delta_q=0.0135 delta_report=0.0014
  b_behavior_distill                     source_flip=0.000 interchange=0.000 delta_q=0.2714 delta_report=0.0282
  b_frozen_random                        source_flip=0.000 interchange=0.000 delta_q=0.0083 delta_report=0.0050
seed 2
  source_full                            source_flip=0.000 interchange=1.000 delta_q=0.0000 delta_report=0.0000
  b_source_align_attention_copy_long     source_flip=0.000 interchange=1.000 delta_q=0.9555 delta_report=0.0000
  b_behavior_distill                     source_flip=0.000 interchange=0.250 delta_q=15.3435 delta_report=0.0403
  b_frozen_random                        source_flip=0.000 interchange=0.250 delta_q=0.0308 delta_report=0.0159
seed 4
  source_full                            source_flip=0.625 interchange=1.000 delta_q=0.0000 delta_report=0.0000
  b_source_align_attention_copy_long     source_flip=0.625 interchange=0.500 delta_q=0.0367 delta_report=0.0050
  b_behavior_distill                     source_flip=0.625 interchange=0.250 delta_q=0.6745 delta_report=0.0226
  b_frozen_random                        source_flip=0.625 interchange=0.000 delta_q=0.0618 delta_report=0.0102
```
Interpretation: copied attention remains the best target in the pooled result and in the source-flip-only subset. The more important discovery is source heterogeneity: seeds 0 and 4 have action-relevant schema-state interventions, while seeds 1 and 2 do not under this selection path. Paper 5 should therefore avoid a single pooled causal-preservation claim and instead model causal leverage per source seed. Behavior distillation is weak under intervention: it has low action agreement in the pooled run and much larger Q/report delta errors than copied attention.
Next required controls: shuffled donor schema states, same-action donor states, and behavior-distill ordinary-behavior matching before causal intervention.

## Donor-Control Smoke

Run completed locally on 2026-06-15 with 4 validated source seeds, 80 source-only candidate A/B pairs per seed, the top 8 selected source patch pairs per seed, and three donor modes:

- `matched`: original selected source-B donor.
- `shuffled_selected`: donor rotated among selected source-B contexts.
- `same_action`: donor chosen so the source patch does not change the source action.

Command:

```bash
KMP_DUPLICATE_LIB_OK=TRUE OMP_NUM_THREADS=1 python3 -B \
  experiments/preservation_bench/run_ast_causal_patch_probe.py \
  --config experiments/preservation_bench/configs/ast_causal_patch_schema_state_controls_smoke.json
```

Exact pooled summary:

```text
b_behavior_distill                                           n=32 source_flip=0.375 interchange_action=0.312 shift_match=0.375 delta_q_to_source=4.6912 delta_report_to_source=0.0314
b_behavior_distill/same_action                               n=32 source_flip=0.000 interchange_action=0.188 shift_match=0.750 delta_q_to_source=4.5600 delta_report_to_source=0.0306
b_behavior_distill/shuffled_selected                         n=32 source_flip=0.312 interchange_action=0.375 shift_match=0.438 delta_q_to_source=4.6894 delta_report_to_source=0.0314
b_frozen_random                                              n=32 source_flip=0.375 interchange_action=0.156 shift_match=0.438 delta_q_to_source=0.0386 delta_report_to_source=0.0139
b_frozen_random/same_action                                  n=32 source_flip=0.000 interchange_action=0.125 shift_match=0.500 delta_q_to_source=0.0384 delta_report_to_source=0.0102
b_frozen_random/shuffled_selected                            n=32 source_flip=0.312 interchange_action=0.125 shift_match=0.375 delta_q_to_source=0.0316 delta_report_to_source=0.0130
b_source_align_attention_copy_long                           n=32 source_flip=0.375 interchange_action=0.625 shift_match=0.719 delta_q_to_source=0.2433 delta_report_to_source=0.0045
b_source_align_attention_copy_long/same_action               n=32 source_flip=0.000 interchange_action=0.906 shift_match=0.969 delta_q_to_source=0.2559 delta_report_to_source=0.0045
b_source_align_attention_copy_long/shuffled_selected         n=32 source_flip=0.312 interchange_action=0.719 shift_match=0.719 delta_q_to_source=0.2451 delta_report_to_source=0.0045
source_full                                                  n=32 source_flip=0.375 interchange_action=1.000 shift_match=1.000 delta_q_to_source=0.0000 delta_report_to_source=0.0000
source_full/same_action                                      n=32 source_flip=0.000 interchange_action=1.000 shift_match=1.000 delta_q_to_source=0.0000 delta_report_to_source=0.0000
source_full/shuffled_selected                                n=32 source_flip=0.312 interchange_action=1.000 shift_match=1.000 delta_q_to_source=0.0000 delta_report_to_source=0.0000
```

Control read:

- The discrete action-agreement headline is fragile. In this donor-control run, copied attention is best pooled on matched donors, but on source-flip-only matched rows behavior distillation can equal or exceed copied attention on the single action label. That means Paper 5 should not headline raw action interchange alone.
- The stronger signal is causal-response geometry. Copied attention remains much closer to the source counterfactual Q/report deltas than behavior distillation across matched, shuffled, and same-action donor modes.
- Same-action donors are valuable. When source patches are chosen not to change source action, copied attention mostly avoids spurious action changes (`target_patch_action_changed=0.031`, `shift_match=0.969`), while behavior distillation changes action more often (`target_patch_action_changed=0.250`, `shift_match=0.750`) and remains far from source Q/report deltas.
- The shuffled-selected control is currently weak as a negative control because shuffled donors often preserve the matched reference action (`source_control_matches_matched_reference_action=0.875`). The next control should force action-mismatched donors when possible.

Updated Paper 5 claim candidate:

> Copied source attention does not reliably win every discrete action-interchange slice, but it preserves source-counterfactual response geometry and avoids spurious no-effect donor responses better than behavior-only distillation. Discrete behavior can therefore be an unstable and sometimes misleading proxy for causal preservation; Paper 5 should evaluate source-specific causal geometry and source-level causal leverage, not only action agreement.

This is a better result than the first smoke because it exposes a failure mode in the metric itself. The paper should treat that as a finding, not as a nuisance.

## Action-Mismatch Donor-Control Smoke

Run completed locally on 2026-06-15 with 4 validated source seeds, 80 source-only candidate A/B pairs per seed, the top 8 selected source patch pairs per seed, and three donor modes:

- `matched`: original selected source-B donor.
- `action_mismatch`: donor chosen so the donor-specific source counterfactual action differs from the original matched source counterfactual action, when such a donor exists.
- `same_action`: donor chosen so the source patch does not change the source action.

Command:

```bash
KMP_DUPLICATE_LIB_OK=TRUE OMP_NUM_THREADS=1 python3 -B \
  experiments/preservation_bench/run_ast_causal_patch_probe.py \
  --config experiments/preservation_bench/configs/ast_causal_patch_schema_state_action_mismatch_controls_smoke.json
```

Exact pooled summary:

```text
b_behavior_distill/action_mismatch                           n=11 source_flip=0.000 interchange_action=0.182 shift_match=1.000 delta_q_to_source=1.1525 delta_report_to_source=0.0280
b_behavior_distill                                           n=32 source_flip=0.344 interchange_action=0.250 shift_match=0.406 delta_q_to_source=4.5434 delta_report_to_source=0.0324
b_behavior_distill/same_action                               n=32 source_flip=0.000 interchange_action=0.156 shift_match=0.750 delta_q_to_source=4.6028 delta_report_to_source=0.0315
b_frozen_random/action_mismatch                              n=11 source_flip=0.000 interchange_action=0.000 shift_match=0.455 delta_q_to_source=0.0307 delta_report_to_source=0.0114
b_frozen_random                                              n=32 source_flip=0.344 interchange_action=0.062 shift_match=0.531 delta_q_to_source=0.0362 delta_report_to_source=0.0129
b_frozen_random/same_action                                  n=32 source_flip=0.000 interchange_action=0.062 shift_match=0.500 delta_q_to_source=0.0308 delta_report_to_source=0.0118
b_source_align_attention_copy_long/action_mismatch           n=11 source_flip=0.000 interchange_action=0.727 shift_match=0.909 delta_q_to_source=0.0834 delta_report_to_source=0.0061
b_source_align_attention_copy_long                           n=32 source_flip=0.344 interchange_action=0.781 shift_match=0.656 delta_q_to_source=0.2675 delta_report_to_source=0.0038
b_source_align_attention_copy_long/same_action               n=32 source_flip=0.000 interchange_action=0.906 shift_match=0.969 delta_q_to_source=0.2879 delta_report_to_source=0.0038
source_full/action_mismatch                                  n=11 source_flip=0.000 interchange_action=1.000 shift_match=1.000 delta_q_to_source=0.0000 delta_report_to_source=0.0000
source_full                                                  n=32 source_flip=0.344 interchange_action=1.000 shift_match=1.000 delta_q_to_source=0.0000 delta_report_to_source=0.0000
source_full/same_action                                      n=32 source_flip=0.000 interchange_action=1.000 shift_match=1.000 delta_q_to_source=0.0000 delta_report_to_source=0.0000
```

Contrast report:

```bash
python3 experiments/preservation_bench/analyze_causal_patch_contrasts.py \
  experiments/preservation_bench/runs/ast_causal_patch_schema_state_action_mismatch_controls_smoke/causal_patch_rows.jsonl \
  --output-json experiments/preservation_bench/runs/ast_causal_patch_schema_state_action_mismatch_controls_smoke/causal_patch_contrasts.json \
  --output-md experiments/preservation_bench/runs/ast_causal_patch_schema_state_action_mismatch_controls_smoke/causal_patch_contrasts.md
```

Key row-level checks from `causal_patch_contrasts.md`:

```text
source_full/action_mismatch                         n=11 donor_action=1.000 matched_ref_action=0.000 specificity_gap=1.000
b_source_align_attention_copy_long/action_mismatch  n=11 donor_action=0.727 matched_ref_action=0.273 specificity_gap=0.455
b_behavior_distill/action_mismatch                  n=11 donor_action=0.182 matched_ref_action=0.455 specificity_gap=-0.273
b_frozen_random/action_mismatch                     n=11 donor_action=0.000 matched_ref_action=0.000 specificity_gap=0.000
```

Paired seed deltas, copied attention minus behavior distillation:

```text
matched donors:         action agreement +0.531; q-delta error -4.276; patched-Q-to-source-CF -5.122; report-delta error -0.029
action-mismatch donors: action agreement +0.567; q-delta error -1.109; patched-Q-to-source-CF -6.561; report-delta error -0.022
```

Paired seed deltas, copied attention minus frozen random:

```text
matched donors:         action agreement +0.719; patched-Q-to-source-CF -170.725; report-delta error -0.009
action-mismatch donors: action agreement +0.750; patched-Q-to-source-CF -72.176; report-delta error -0.006
```

Control read:

- The forced action-mismatch control found 11 usable rows, all from the source-action-relevant seeds 0 and 4. This small `n` is a limitation, but it is also informative: action-mismatched donors only exist where the selected matched source intervention changed the source action.
- Within `action_mismatch`, `source_full` behaves as expected: it follows the donor-specific source counterfactual and never the original matched reference action. This validates the control construction.
- Copied attention has a positive action specificity gap under forced mismatches: it follows the actual donor-specific counterfactual more often than the original matched reference (`0.727` versus `0.273`). Behavior distillation shows the opposite pattern (`0.182` versus `0.455`).
- Copied attention also stays much closer than behavior distillation to source counterfactual Q/report geometry. Against behavior distillation, copied attention improves donor action agreement by `+0.567`, reduces Q-delta error by `1.109`, reduces absolute patched-Q-to-source-CF error by `6.561`, and reduces report-delta error by `0.022` on the two action-mismatch seeds.
- Frozen random remains a useful negative for absolute source-counterfactual state: copied attention is `72.176` lower on patched-Q-to-source-CF error under action-mismatch donors. Frozen random can look artificially close on Q-delta error when both source and target deltas are small, so Paper 5 should report both delta geometry and absolute counterfactual state distance.
- In this selected causal subset, behavior distillation is not a strong ordinary-behavior match (`target_unpatched_source_a_action_agreement=0.375` pooled; `0.182` on action-mismatch rows). The current evidence therefore supports a narrower claim than "behavior looks good but causality fails." The cleaner claim is that causal selection exposes behavior-only brittleness and that copied source attention better preserves source-specific intervention geometry.

Updated claim candidate:

> Schema-state interchange interventions expose a causal-preservation signal that is not captured by raw behavior or single action labels. In this bounded AST toy setting, copied source attention preserves donor-specific counterfactual geometry and intervention specificity better than behavior-only distillation and frozen random controls, but discrete action agreement is fragile and source causal leverage is heterogeneous across seeds.

This is the first result that feels Paper-5-worthy rather than just Paper-4-plus-one-more-stress-test. The finding is not that copied attention "wins" every action slice. The finding is sharper: the benchmark itself reveals why action-only preservation metrics are inadequate, and it provides a positive control plus donor-mismatch test for source-specific causal mechanism survival.

## Full 22-Source Action-Mismatch Panel

Run completed locally on 2026-06-15 with all 22 validated source seeds from `experiments/preservation_bench/runs/ast_competence_v2_core_10seed`, 80 source-only candidate A/B pairs per seed, the top 8 selected source patch pairs per seed, and `matched`, `action_mismatch`, and `same_action` donor controls.

Command:

```bash
KMP_DUPLICATE_LIB_OK=TRUE OMP_NUM_THREADS=1 python3 -B \
  experiments/preservation_bench/run_ast_causal_patch_probe.py \
  --config experiments/preservation_bench/configs/ast_causal_patch_schema_state_action_mismatch_full22.json
```

Run artifacts:

- `experiments/preservation_bench/runs/ast_causal_patch_schema_state_action_mismatch_full22/causal_patch_rows.jsonl`
- `experiments/preservation_bench/runs/ast_causal_patch_schema_state_action_mismatch_full22/causal_patch_summary.json`
- `experiments/preservation_bench/runs/ast_causal_patch_schema_state_action_mismatch_full22/causal_patch_contrasts.md`
- `paper5/figures/fig1_action_mismatch_specificity_full22.png`
- `paper5/figures/fig2_paired_seed_deltas_full22.png`
- `paper5/figures/fig3_source_leverage_full22.png`

Exact pooled summary:

```text
b_behavior_distill/action_mismatch                           n=122 source_flip=0.164 interchange_action=0.361 shift_match=0.664 delta_q_to_source=1.1794 delta_report_to_source=0.0326
b_behavior_distill                                           n=176 source_flip=0.676 interchange_action=0.250 shift_match=0.443 delta_q_to_source=1.9835 delta_report_to_source=0.0372
b_behavior_distill/same_action                               n=175 source_flip=0.000 interchange_action=0.394 shift_match=0.720 delta_q_to_source=1.6690 delta_report_to_source=0.0324
b_frozen_random/action_mismatch                              n=122 source_flip=0.164 interchange_action=0.164 shift_match=0.713 delta_q_to_source=0.0762 delta_report_to_source=0.0123
b_frozen_random                                              n=176 source_flip=0.676 interchange_action=0.193 shift_match=0.347 delta_q_to_source=0.2459 delta_report_to_source=0.0192
b_frozen_random/same_action                                  n=175 source_flip=0.000 interchange_action=0.166 shift_match=0.731 delta_q_to_source=0.0511 delta_report_to_source=0.0105
b_source_align_attention_copy_long/action_mismatch           n=122 source_flip=0.164 interchange_action=0.689 shift_match=0.754 delta_q_to_source=0.1694 delta_report_to_source=0.0084
b_source_align_attention_copy_long                           n=176 source_flip=0.676 interchange_action=0.642 shift_match=0.568 delta_q_to_source=0.1571 delta_report_to_source=0.0069
b_source_align_attention_copy_long/same_action               n=175 source_flip=0.000 interchange_action=0.771 shift_match=0.869 delta_q_to_source=0.1642 delta_report_to_source=0.0068
source_full/action_mismatch                                  n=122 source_flip=0.164 interchange_action=1.000 shift_match=1.000 delta_q_to_source=0.0000 delta_report_to_source=0.0000
source_full                                                  n=176 source_flip=0.676 interchange_action=1.000 shift_match=1.000 delta_q_to_source=0.0000 delta_report_to_source=0.0000
source_full/same_action                                      n=175 source_flip=0.000 interchange_action=1.000 shift_match=1.000 delta_q_to_source=0.0000 delta_report_to_source=0.0000
```

Contrast report command:

```bash
python3 experiments/preservation_bench/analyze_causal_patch_contrasts.py \
  experiments/preservation_bench/runs/ast_causal_patch_schema_state_action_mismatch_full22/causal_patch_rows.jsonl \
  --output-json experiments/preservation_bench/runs/ast_causal_patch_schema_state_action_mismatch_full22/causal_patch_contrasts.json \
  --output-md experiments/preservation_bench/runs/ast_causal_patch_schema_state_action_mismatch_full22/causal_patch_contrasts.md
```

Figure command:

```bash
python3 experiments/preservation_bench/plot_causal_patch_results.py \
  --contrasts experiments/preservation_bench/runs/ast_causal_patch_schema_state_action_mismatch_full22/causal_patch_contrasts.json \
  --rows experiments/preservation_bench/runs/ast_causal_patch_schema_state_action_mismatch_full22/causal_patch_rows.jsonl \
  --output-dir paper5/figures
```

Key full-panel read:

- The result scaled. Matched donors cover 22 source seeds and 176 rows per condition; action-mismatch donors cover 19 source seeds and 122 rows per condition.
- Within-source positive control works: `source_full` has 1.000 donor-specific action agreement for matched, same-action, and action-mismatch donor modes.
- Copied attention beats behavior distillation and frozen random on donor-specific interchange action agreement under matched donors (`0.642` vs `0.250` and `0.193`) and action-mismatch donors (`0.689` vs `0.361` and `0.164`).
- The action-mismatch specificity gap is the cleanest causal-preservation signal: copied attention has `0.689` donor action agreement, `0.139` stale matched-reference agreement, and a `+0.549` specificity gap; behavior distillation has `+0.164`; frozen random has `-0.033`.
- Source-seed paired deltas support the row-level result. Under action-mismatch donors, copied attention exceeds behavior distillation by `+0.324` action agreement with 95% bootstrap CI `[0.182, 0.473]`, reduces Q-delta error by `0.941` with CI `[-1.280, -0.627]`, reduces patched-Q-to-source-CF error by `8.772` with CI `[-15.202, -3.978]`, and reduces report-delta error by `0.025` with CI `[-0.027, -0.022]`.
- Against frozen random, copied attention improves action agreement by `+0.489` under action-mismatch donors and reduces patched-Q-to-source-CF error by `88.064`. Q-delta error alone is not a clean frozen-random separator under action-mismatch donors, because frozen random can have small deltas while being far from the absolute source counterfactual state.
- Source causal leverage is heterogeneous: 10/22 validated source seeds had matched source action flip rate `1.000`, 9/22 had partial flip rates, and 3/22 had no action flips under this schema-state selection path. This should be treated as a finding and visualized, not averaged away.

Current full-panel claim:

> In a 22-source toy AST substrate-transfer panel, schema-state interchange interventions reveal source-specific causal preservation in copied attention beyond behavior-only distillation and frozen random controls. The strongest evidence is not raw action agreement alone, but donor-specific action-mismatch specificity plus source-counterfactual Q/report geometry. The result remains bounded: it tests one toy causal variable, not consciousness, survival, personal identity, biological preservation, or AST truth.

## Full 22-Source Attention-State Panel

Run completed locally on 2026-06-15 with all 22 validated source seeds from `experiments/preservation_bench/runs/ast_competence_v2_core_10seed`. This path patches source-B attention weights and attended features into source or target context A before schema, self-model, and policy readout.

Command:

```bash
KMP_DUPLICATE_LIB_OK=TRUE OMP_NUM_THREADS=1 python3 -B \
  experiments/preservation_bench/run_ast_causal_patch_probe.py \
  --config experiments/preservation_bench/configs/ast_causal_patch_attention_state_action_mismatch_full22.json
```

Run artifacts:

- `experiments/preservation_bench/runs/ast_causal_patch_attention_state_action_mismatch_full22/causal_patch_rows.jsonl`
- `experiments/preservation_bench/runs/ast_causal_patch_attention_state_action_mismatch_full22/causal_patch_summary.json`
- `experiments/preservation_bench/runs/ast_causal_patch_attention_state_action_mismatch_full22/causal_patch_contrasts.md`
- `paper5/figures/attention_state/fig1_action_mismatch_specificity_full22.png`
- `paper5/figures/attention_state/fig2_paired_seed_deltas_full22.png`
- `paper5/figures/attention_state/fig3_source_leverage_full22.png`

Exact pooled summary:

```text
b_behavior_distill/action_mismatch                           n=176 source_flip=0.506 interchange_action=0.267 shift_match=0.625 delta_q_to_source=96.9758 delta_report_to_source=0.0057
b_behavior_distill                                           n=176 source_flip=0.955 interchange_action=0.188 shift_match=0.619 delta_q_to_source=111.0710 delta_report_to_source=0.0083
b_behavior_distill/same_action                               n=175 source_flip=0.000 interchange_action=0.120 shift_match=0.343 delta_q_to_source=91.7151 delta_report_to_source=0.0054
b_frozen_random/action_mismatch                              n=176 source_flip=0.506 interchange_action=0.312 shift_match=0.409 delta_q_to_source=10.2535 delta_report_to_source=0.0057
b_frozen_random                                              n=176 source_flip=0.955 interchange_action=0.216 shift_match=0.369 delta_q_to_source=29.9075 delta_report_to_source=0.0083
b_frozen_random/same_action                                  n=175 source_flip=0.000 interchange_action=0.257 shift_match=0.663 delta_q_to_source=7.5355 delta_report_to_source=0.0054
b_source_align_attention_copy_long/action_mismatch           n=176 source_flip=0.506 interchange_action=0.864 shift_match=0.903 delta_q_to_source=0.1268 delta_report_to_source=0.0053
b_source_align_attention_copy_long                           n=176 source_flip=0.955 interchange_action=0.864 shift_match=0.892 delta_q_to_source=0.1117 delta_report_to_source=0.0053
b_source_align_attention_copy_long/same_action               n=175 source_flip=0.000 interchange_action=0.914 shift_match=0.840 delta_q_to_source=0.1152 delta_report_to_source=0.0054
source_full/action_mismatch                                  n=176 source_flip=0.506 interchange_action=1.000 shift_match=1.000 delta_q_to_source=0.0000 delta_report_to_source=0.0000
source_full                                                  n=176 source_flip=0.955 interchange_action=1.000 shift_match=1.000 delta_q_to_source=0.0000 delta_report_to_source=0.0000
source_full/same_action                                      n=175 source_flip=0.000 interchange_action=1.000 shift_match=1.000 delta_q_to_source=0.0000 delta_report_to_source=0.0000
```

Contrast and figure commands:

```bash
python3 experiments/preservation_bench/analyze_causal_patch_contrasts.py \
  experiments/preservation_bench/runs/ast_causal_patch_attention_state_action_mismatch_full22/causal_patch_rows.jsonl \
  --output-json experiments/preservation_bench/runs/ast_causal_patch_attention_state_action_mismatch_full22/causal_patch_contrasts.json \
  --output-md experiments/preservation_bench/runs/ast_causal_patch_attention_state_action_mismatch_full22/causal_patch_contrasts.md

python3 experiments/preservation_bench/plot_causal_patch_results.py \
  --contrasts experiments/preservation_bench/runs/ast_causal_patch_attention_state_action_mismatch_full22/causal_patch_contrasts.json \
  --rows experiments/preservation_bench/runs/ast_causal_patch_attention_state_action_mismatch_full22/causal_patch_rows.jsonl \
  --output-dir paper5/figures/attention_state
```

Key full-panel read:

- The attention-state source positive control is stronger than schema-state: matched source action flip rate is `0.955`, with no null source seeds.
- Copied attention cleanly separates from behavior distillation and frozen random under matched donors: `0.864` interchange action agreement versus `0.188` and `0.216`.
- Copied attention also cleanly separates under action-mismatch donors: `0.864` donor action agreement versus `0.267` and `0.312`.
- Action-mismatch specificity is strong: copied attention has `0.864` donor action agreement, `0.085` stale matched-reference agreement, and a `+0.778` specificity gap. Behavior distillation has only `+0.006`; frozen random has `+0.170`.
- Source-seed paired deltas under action-mismatch donors: copied attention exceeds behavior distillation by `+0.597` action agreement with 95% bootstrap CI `[0.375, 0.790]`, reduces Q-delta error by `96.849`, and reduces patched-Q-to-source-CF error by `100.007`.
- This second path strengthens the Paper 5 claim because it tests a different causal variable. Schema-state patching shows subtle source-specific counterfactual geometry and heterogeneous source leverage; attention-state patching shows a high-leverage source causal bottleneck preserved by copied attention.

Updated two-path claim:

> In a 22-source toy AST substrate-transfer panel, copied attention preserves source-specific causal response geometry under both schema-state and attention-state interchange interventions better than behavior-only distillation and frozen random controls. The attention-state path gives a strong high-leverage positive result; the schema-state path gives a subtler donor-specific geometry result. Both remain bounded toy causal-mechanism results, not consciousness, survival, personal identity, biological preservation, or AST truth claims.

## Full 22-Source Attention-State Donor-Action-Mismatch Follow-Up

Run completed locally on 2026-06-16 with all 22 validated source seeds from `experiments/preservation_bench/runs/ast_competence_v2_core_10seed`. This follow-up deliberately searched for attention-state donors where the donor's ordinary source-B action differs from the patched source-counterfactual action.

Command:

```bash
KMP_DUPLICATE_LIB_OK=TRUE OMP_NUM_THREADS=1 python3 -B \
  experiments/preservation_bench/run_ast_causal_patch_probe.py \
  --config experiments/preservation_bench/configs/ast_causal_patch_attention_state_donor_action_mismatch_full22.json
```

Run artifacts:

- `experiments/preservation_bench/runs/ast_causal_patch_attention_state_donor_action_mismatch_full22/causal_patch_rows.jsonl`
- `experiments/preservation_bench/runs/ast_causal_patch_attention_state_donor_action_mismatch_full22/causal_patch_summary.json`
- `experiments/preservation_bench/runs/ast_causal_patch_attention_state_donor_action_mismatch_full22/causal_patch_contrasts.md`
- `experiments/preservation_bench/runs/ast_causal_patch_attention_state_donor_action_mismatch_full22/behavior_matched_subsets.md`
- `experiments/preservation_bench/runs/ast_causal_patch_attention_state_donor_action_mismatch_full22/leakage_audit.md`

Exact pooled summary:

```text
b_behavior_distill/donor_action_mismatch                     n=128 source_flip=0.969 interchange_action=0.234 shift_match=0.633 delta_q_to_source=89.4973 delta_report_to_source=0.0109
b_behavior_distill                                           n=176 source_flip=0.966 interchange_action=0.256 shift_match=0.642 delta_q_to_source=109.3033 delta_report_to_source=0.0093
b_frozen_random/donor_action_mismatch                        n=128 source_flip=0.969 interchange_action=0.297 shift_match=0.336 delta_q_to_source=34.8843 delta_report_to_source=0.0109
b_frozen_random                                              n=176 source_flip=0.966 interchange_action=0.267 shift_match=0.335 delta_q_to_source=32.8539 delta_report_to_source=0.0093
b_source_align_attention_copy_long/donor_action_mismatch     n=128 source_flip=0.969 interchange_action=0.406 shift_match=0.773 delta_q_to_source=0.1386 delta_report_to_source=0.0065
b_source_align_attention_copy_long                           n=176 source_flip=0.966 interchange_action=0.875 shift_match=0.909 delta_q_to_source=0.1578 delta_report_to_source=0.0052
source_full/donor_action_mismatch                            n=128 source_flip=0.969 interchange_action=1.000 shift_match=1.000 delta_q_to_source=0.0000 delta_report_to_source=0.0000
source_full                                                  n=176 source_flip=0.966 interchange_action=1.000 shift_match=1.000 delta_q_to_source=0.0000 delta_report_to_source=0.0000
```

Key follow-up read:

- The decoupled donor control found 128 rows across 18 source seeds per condition.
- Source positive control remained valid: source_full followed the source counterfactual with `1.000` agreement while raw donor-B action agreement was `0.000`.
- Copied attention remained far closer on Q-delta geometry than behavior distillation or frozen random (`0.1386` versus `89.4973` and `34.8843`).
- Copied attention exceeded behavior distillation on source-counterfactual action agreement (`0.406` versus `0.234`), with source-seed paired delta `+0.259` and 95% bootstrap CI `[0.035, 0.484]`.
- The discrete action result is much weaker than the original attention-state action-mismatch panel. Copied attention does not dominate the raw donor-B action label (`0.508`) and its action advantage over frozen random is not stable.
- On behavior-distill ordinary-action-matched decoupled rows, behavior distillation reaches `0.375` causal action agreement and copied attention reaches `0.350`, so this slice is a limitation rather than a green behavior-matched result.

Updated shortcut-audit claim:

> The attention-state mechanism preserves source-counterfactual geometry under a hard donor-action decoupling test, but discrete action preservation is only partial. This makes the strongest Paper 5 claim geometry-first, not action-label-first.

## Full 22-Source Bidirectional Attention-State Follow-Up

Run completed locally on 2026-06-16 with all 22 validated source seeds from `experiments/preservation_bench/runs/ast_competence_v2_core_10seed`. This follow-up reverses the main patch direction: it obtains target-B attention activations from each condition, patches those activations back into source context A, and compares the resulting source response with the source's own B-to-A counterfactual.

Command:

```bash
KMP_DUPLICATE_LIB_OK=TRUE OMP_NUM_THREADS=1 python3 -B \
  experiments/preservation_bench/run_ast_bidirectional_patch_probe.py \
  --config experiments/preservation_bench/configs/ast_bidirectional_patch_attention_state_full22.json
```

Run artifacts:

- `experiments/preservation_bench/runs/ast_bidirectional_patch_attention_state_full22/bidirectional_patch_rows.jsonl`
- `experiments/preservation_bench/runs/ast_bidirectional_patch_attention_state_full22/bidirectional_patch_summary.json`
- `experiments/preservation_bench/runs/ast_bidirectional_patch_attention_state_full22/bidirectional_patch_contrasts.md`
- `paper5/figures/bidirectional_attention/fig8_bidirectional_attention_patch_full22.png`
- `paper5/figures/bidirectional_attention/fig9_bidirectional_paired_deltas_full22.png`

Exact pooled summary:

```text
source_full                                      n=176 source_flip=0.955 action=1.000 q_delta=0.0000 donor_attn_l1=0.0000
b_source_align_attention_copy_long               n=176 source_flip=0.955 action=0.938 q_delta=0.1642 donor_attn_l1=0.0002
b_behavior_distill                               n=176 source_flip=0.955 action=0.210 q_delta=38.0626 donor_attn_l1=0.0351
b_frozen_random                                  n=176 source_flip=0.955 action=0.199 q_delta=47.1765 donor_attn_l1=0.0351
```

Contrast commands:

```bash
python3 experiments/preservation_bench/analyze_bidirectional_patch_contrasts.py \
  --rows experiments/preservation_bench/runs/ast_bidirectional_patch_attention_state_full22/bidirectional_patch_rows.jsonl \
  --output-json experiments/preservation_bench/runs/ast_bidirectional_patch_attention_state_full22/bidirectional_patch_contrasts.json \
  --output-md experiments/preservation_bench/runs/ast_bidirectional_patch_attention_state_full22/bidirectional_patch_contrasts.md

python3 experiments/preservation_bench/plot_bidirectional_patch_results.py \
  --contrasts experiments/preservation_bench/runs/ast_bidirectional_patch_attention_state_full22/bidirectional_patch_contrasts.json \
  --output-dir paper5/figures/bidirectional_attention
```

Key bidirectional read:

- The within-source positive control passes: source_full has `1.000` source-counterfactual action agreement and zero Q-delta error.
- Copied-attention target-B activations can substitute back into source-A: action agreement `0.938`, Q-delta error `0.1642`.
- Behavior-distilled and frozen-random target activations do not play the same source causal role: action agreement `0.210` and `0.199`, Q-delta error `38.0626` and `47.1765`.
- Source-seed paired copied-minus-behavior action delta is `+0.727` with 95% bootstrap CI `[0.631, 0.818]`.
- Source-seed paired copied-minus-frozen action delta is `+0.739` with 95% bootstrap CI `[0.648, 0.824]`.

Updated bidirectional claim:

> In the identity-aligned attention-state path, copied-attention target state is not only accepted by the target's own downstream readout; it can be patched back into the source and recover the source's counterfactual response. This supports a bounded same-variable causal-role preservation claim, while leaving non-identity alignment and learned stitching as future stress tests.
