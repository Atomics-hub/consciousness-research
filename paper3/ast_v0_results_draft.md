# AST v0 Results Draft

This draft is written from the validated core replication run:

```text
experiments/preservation_bench/runs/ast_competence_v2_core_10seed/
```

The integrated manuscript draft is `paper3/manuscript.md`.

The run attempted 10 independent source seeds. Eight source agents passed the preregistered validation gate, which required self-report correlation at or above 0.50, at least 20 self queries, and goals found at or above 0.10. Two source agents were rejected before transfer analysis because they found too few goals during source evaluation. All condition means and paired contrasts below use only the eight validated source seeds.

## Results

### Source Validation

The validation gate separated usable source agents from source agents that had learned only part of the task. Eight of ten attempted sources passed validation. The two rejected seeds both had strong self-report behavior but found too few goals, with goals found equal to 0.030 against the 0.100 threshold. These rejected seeds were retained in the run records but excluded from transfer contrasts. This validation step matters because the benchmark asks whether source capacities survive transfer; when the source does not show the relevant source capacity, target failure cannot be interpreted as transfer failure.

Among validated sources, the full source agent achieved mean reward -0.630, goals found 0.686, self-report correlation 0.837, identity probe accuracy 1.000, goal-attention mass 0.165, and source-action agreement 1.000 by definition. Source ablations behaved as expected. Removing the schema module eliminated self-report correlation while leaving identity probes intact. Removing the self-model eliminated identity probe accuracy while leaving report behavior largely intact. Removing attention caused the largest source-side control drop, with reward falling to -9.933 and goals found to 0.219. These ablations support the intended separation among report, identity, and attention-control channels.

### Frozen Copy And Long Repair

The strict frozen cross-substrate copy preserved source-specific identity probes but failed to recouple most active behavior. It retained identity probe accuracy at 1.000, but its mean self-report correlation was 0.003, goals found was 0.099, and source-action agreement was 0.092. This is the basic negative profile the benchmark is meant to expose: copied source state can remain detectable without remaining functionally active in the target substrate.

Long source-alignment repair improved report relative to frozen copy, but did not restore source-like control. Mean self-report correlation increased from 0.003 to 0.294, with a paired mean difference of 0.291 and a 95 percent bootstrap CI from 0.114 to 0.478. However, goals found remained low at 0.182, and source-action agreement remained low at 0.168. Identity probes stayed at 1.000. This condition shows partial report repair with preserved copied provenance, but not broad preservation-relevant functional continuity.

### Copied Attention

Copying and freezing the source attention module produced the strongest combined transfer profile. The copied-attention condition preserved identity probes at 1.000, reached mean self-report correlation 0.796, restored goals found to 0.628, and recovered source-action agreement to 0.849. Compared with long repair, copied attention improved self-report by 0.501, with a 95 percent bootstrap CI from 0.357 to 0.655. It also improved source-action agreement by 0.681, with a 95 percent CI from 0.593 to 0.770.

This is not a clean cross-architecture preservation success, because copying the attention module deliberately narrows the substrate gap. The useful result is more specific: in this AST-derived task, preserving the attention interface is sufficient to recover the most source-like combined profile observed in the benchmark. That makes attention/interface coupling the leading bottleneck in the current setup.

### Report Bridge Without Control

The attention-adapter bridge recovered report behavior without restoring source-like control. This condition kept the target attention substrate but added a residual source-facing interface adapter. It achieved the highest mean self-report correlation among target-transfer conditions at 0.892, but goals found remained low at 0.116 and source-action agreement remained low at 0.191. Compared with copied attention, the bridge had slightly higher self-report but much lower source-action agreement, with a paired mean difference of -0.658 and a 95 percent CI from -0.790 to -0.510.

This dissociation is important. A target can be made report-like without becoming control-like. A benchmark that only measured self-report would overstate this condition. PreservationBench instead shows that report continuity, task competence continuity, and source-action continuity can come apart.

### Proxy Control Without Source-Like Action

The control-adapter bridge showed the opposite failure mode. It drove reward and goal-attention mass far above the source baseline, with mean reward 16.452 and goal-attention mass 0.672. However, it did not restore source-like goals found or source-action agreement. Mean goals found was only 0.163, and source-action agreement was 0.307. Self-report correlation was 0.527, below both copied attention and the attention-adapter bridge.

Compared with copied attention, the control adapter had higher reward by 18.090 and higher goal-attention mass by 0.517, but lower source-action agreement by -0.542 and lower self-report by -0.268. This pattern looks like optimization of the attention-reward proxy rather than preservation of source-like task control. In a preservation benchmark, that is a useful negative result: high reward alone can be misleading when the reward channel can be exploited without restoring the source's functional organization.

### Behavior-Only And Random Controls

Behavior-only distillation and frozen random controls failed copied identity probes, as intended. Behavior distillation reached self-report correlation 0.123 and source-action agreement 0.192, while identity probe accuracy remained 0.000. Frozen random had self-report correlation -0.057, source-action agreement 0.012, and identity probe accuracy 0.000. These controls support the interpretation that identity-probe success in copied conditions reflects copied source state rather than independent relearning or random target structure.

### Summary Profile

The core result is not that a target condition preserves consciousness, identity, or personhood. The core result is that PreservationBench separates preservation-relevant channels that can otherwise be conflated:

- copied identity can survive without report or control recoupling
- report behavior can be recoupled without source-like control
- reward and attention proxies can be optimized without source-like goals found or action agreement
- copied attention recovers the strongest combined profile, but only by narrowing the substrate gap

This is the profile-level output that the benchmark is designed to produce.

## Discussion

### What The Benchmark Adds

The main contribution of AST v0 is diagnostic rather than metaphysical. The experiment does not test consciousness preservation. It tests whether specified preservation-relevant functions survive a controlled substrate transfer. In this toy setting, different preservation channels split apart in ways that a single behavioral score would hide.

The frozen-copy result shows that copied provenance-sensitive state can remain intact while failing to recouple to active behavior. The attention-adapter result shows that report-like behavior can be recovered without source-like control. The control-adapter result shows that reward and attention proxies can be optimized without restoring source-like action. The copied-attention result shows that the current architecture can recover a strong combined continuity profile, but only when the substrate gap is narrowed by copying the attention module itself.

Together, these findings support the benchmark framing: preservation claims should not be evaluated by one score. They need profiles that distinguish identity probes, report dynamics, control dynamics, memory overlap, source-specific action agreement, and adaptation costs.

### Interpretation For Attention Schema Theory

The AST-derived task was designed so that attention, attention-schema report, and self-model identity probes can be measured separately. The source ablations support this separation: schema ablation destroys report, self-model ablation destroys identity probes, and attention ablation harms control. This makes the task a useful toy validation tier for AST-style preservation questions.

The transfer results suggest that attention/interface coupling is the practical bottleneck in the current implementation. Copying schema and self-model state preserves source identity probes, but that state is mostly inert when the target attention interface is not source-like. Repairing the interface improves report somewhat. Adding a source-facing bridge can recover report strongly. But broad source-like control only appears when the attention module itself is copied.

This should not be interpreted as evidence that AST preservation requires literal attention-module copying in real systems. It is a toy-engineering result: under this architecture, the copied schema and self-model depend on a particular attention interface, and cross-substrate transfer breaks that interface.

### Why The Proxy Failure Matters

The control-adapter condition is one of the most useful results. It improves reward dramatically and concentrates attention on goals, yet it does not recover source-like goals found or source-action agreement. This means the task reward channel can be driven by proxy behavior that does not match source control. For preservation research, that is a warning sign. A target can look improved on a headline objective while failing the continuity properties that motivated the transfer.

This motivates reporting preservation profiles rather than reward alone. If the paper makes one practical methodological point, it should be this: preservation-relevant benchmarking needs controls that catch proxy success, behavioral mimicry, and inert copied state.

### Seed Count Decision

The current result is strong enough for a preprint-scale AST v0 pilot. The reduced core replication used 10 attempted source seeds and 8 validated source seeds, with paired evaluation across conditions. The major qualitative dissociations replicated from the earlier 5-seed pilot.

For a larger journal-style version, the next run should attempt 20 to 30 source seeds with the frozen core condition family and likely 200 paired evaluation episodes per condition. That would improve power and reduce uncertainty around seed-variable reward effects. It should not be a blocker for drafting the current paper. The paper can present the current run as a validated toy benchmark pilot and state that larger benchmark releases should scale seed count.

### Limitations

The task is a toy grid-world, not a general mind-preservation test. The source validation rate shows that even this small environment has seed-sensitive learning dynamics. The target conditions are engineered diagnostics rather than realistic upload procedures. Identity probes are source-specific functional fingerprints, not personal identity. Memory overlap is diagnostic and not yet a behavioral autobiographical memory task. The reward channel can be exploited, which is itself informative but limits any simple interpretation of reward as preservation success.

The copied-attention condition deliberately narrows the substrate gap, so it should not be described as a clean cross-architecture transfer win. It is evidence about the bottleneck, not evidence that preservation is easy.

### Paper Claim

The safest claim is:

> In an AST-derived toy transfer benchmark, copied source state, report behavior, reward optimization, and source-like control can dissociate. PreservationBench exposes these dissociations by evaluating a profile of source validation, copied identity probes, report continuity, task competence, attention diagnostics, and source-action agreement across matched transfer controls.

The paper should avoid claiming that any condition preserves consciousness or personal identity.

## Figure Captions

Generated figure files:

```text
experiments/preservation_bench/runs/ast_competence_v2_core_10seed/paper_figures/source_validation_flow.png
experiments/preservation_bench/runs/ast_competence_v2_core_10seed/preservation_profile_core.png
experiments/preservation_bench/runs/ast_competence_v2_core_10seed/paper_figures/focused_transfer_metrics.png
```

**Figure 1. Source validation flow.** Ten independent source seeds were trained. Eight passed the source validation gate and two were rejected for low goals found. Rejected seeds were retained in run records but excluded from transfer contrasts.

**Figure 2. Normalized preservation profile.** Values are normalized relative to the source and frozen-random baseline for each metric. Raw means remain the primary result. The profile shows copied-attention recovery, report-only bridge recovery, and proxy optimization by the control adapter.

**Figure 3. Focused transfer metrics.** Raw condition means with bootstrap 95 percent CIs across validated source seeds for self-report correlation, goals found, source-action agreement, and identity probe accuracy. Copied attention has the strongest combined functional profile; the attention bridge is report-like without source-like control; the control bridge optimizes reward-related attention without recovering source-like action.
