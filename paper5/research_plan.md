# Paper 5 Research Plan

Working direction prepared 2026-06-15.

## Current Arc

Paper 1 mapped consciousness theories to preservation requirements.
Paper 2 tested a narrow AST-style transplant assay.
Paper 3 introduced PreservationBench-AST and showed that copied provenance, report, task competence, proxy reward, and source-like control dissociate.
Paper 4 hardened the strongest Paper 3 condition with recurrent delayed histories, counterfactual histories, and perturbation probes.

The next paper should not be another stress-family extension unless it changes the epistemic status of the result. Paper 5 needs a sharper claim about mechanism.

## Landscape Read

The current field has several adjacent tracks:

- AI-consciousness indicator frameworks derive theory-linked properties from RPT, GWT, HOT, predictive processing, AST, and related views. These are useful, but they mostly ask whether a system has indicators at a time, not whether those indicators remain source-specific and causally active after transfer.
- Responsible AI-consciousness work emphasizes uncertainty, over-attribution risk, under-attribution risk, and careful public claims. This supports a cautious benchmark style: test mechanisms, avoid consciousness or survival claims.
- COGITATE-style adversarial theory testing shows that even leading theories such as IIT and GNWT are empirically fragile, and that the field needs quantitative theory-testing frameworks rather than loose analogies.
- WBE fidelity work argues for standardized functional tests of emulation quality, but usually treats fidelity as behavioral correspondence across a repertoire. PreservationBench can strengthen this by making fidelity causal and intervention-based.
- Mechanistic interpretability and causal abstraction work provide a usable vocabulary for the next step: not just "does target behavior match source?", but "do source and target share behaviorally relevant causal variables under interchange interventions?"
- Agent memory benchmarks are moving beyond simple recall toward long-horizon, multi-source, procedural, habitual, and non-declarative memory. This supports broadening beyond report and short-horizon probe behavior, but memory alone is not the novelty.
- Embodied global-workspace-agent work shows that theory-derived architectures can be concretely implemented and ablated, but still does not make substrate transfer the central intervention.

## White Space

The white space is:

> Causal preservation: whether a target preserves the source's behaviorally relevant causal mechanisms after substrate transfer, not merely source-like behavior, source-like report, or copied-state fingerprints.

This is stronger than Papers 3-4 because it attacks the main caveat directly:

- Paper 3/4 show that copied attention remains source-like.
- A critic can still say: "You copied a major module, so of course internal distances look good."
- Paper 5 should ask whether we can identify, align, intervene on, and validate source causal variables in the target.

## Recommended Paper 5

Working title:

**Causal Preservation Under Substrate Transfer: Interchange Intervention Tests for Source-Specific Functional Continuity**

Core question:

> After transfer, does the target implement source-relevant causal variables that can be aligned with the source and patched under counterfactual interventions?

Defensible claim target:

> In a toy AST-derived preservation benchmark, behaviorally similar target conditions diverge sharply under causal interchange tests. Some conditions preserve surface behavior or report while failing causal preservation; copied source attention preserves more source-causal structure but remains limited by reduced substrate gap; adapter-only or larger-gap transfer becomes the key open frontier.

Stronger version if results support it:

> A target can be behaviorally competent and report-like while lacking source-aligned causal variables. Causal preservation therefore adds a necessary benchmark layer beyond behavior, report, identity probes, and perturbation response.

Do not claim:

- consciousness was measured;
- personal identity was preserved;
- survival was shown;
- AST is true;
- causal preservation is sufficient for consciousness.

## Experiment Design

### Conditions

Use the existing Paper 3/4 condition family first:

- `source_full`
- `b_source_align_attention_copy_long`
- `b_source_align_attention_adapter_long`
- `b_source_align_control_adapter_long`
- `b_source_align_repair_copy_long`
- `b_behavior_distill`
- `b_frozen_copy`
- `b_frozen_random`

### Causal Variables

Start with variables already present in the AST scaffold:

- attention weights / goal attention;
- schema hidden state;
- self-report latent;
- policy Q/logit state;
- source identity/self-model probe state;
- recurrent hidden state after history.

### Interventions

Use held-out paired episodes and source histories. For two source contexts A and B:

1. Run source on A and B.
2. Run target on A.
3. Patch source variable from B into the aligned target variable during A.
4. Ask whether the target output follows the source's counterfactual output from B.

Run both directions where possible:

- source-to-target patching;
- target-to-source patching;
- within-source positive control;
- random/behavior-only negative controls.

### Alignment Methods

First-pass methods:

- identity alignment for copied modules;
- linear probe / ridge map for compatible latents;
- Procrustes or CCA alignment for hidden states;
- simple learned affine bridge.

Stretch method:

- Model Alignment Search / causal-abstraction-style alignment for behaviorally relevant subspaces.

### Metrics

Primary:

- Interchange intervention accuracy for action;
- Interchange intervention accuracy for report;
- source-causal delta agreement;
- patch effect size over no-patch baseline;
- bidirectional consistency;
- seed-level bootstrap intervals.

Secondary:

- intervention locality;
- source-hidden-state distance after patch;
- attention-delta distance after patch;
- Q/logit-delta distance after patch;
- failure clusters by seed and condition.

## 7-Day Proof

Goal: prove whether this is a real Paper 5 lane before building a full manuscript.

Minimal prototype:

1. Pick existing validated sources from the Paper 3/4 run.
2. Implement one causal patch path for schema hidden state or attention state.
3. Compare four conditions:
   - `source_full`
   - `b_source_align_attention_copy_long`
   - `b_behavior_distill`
   - `b_frozen_random`
4. Run held-out A/B contexts over 5-10 validated source seeds.
5. Report source-level interchange accuracy and effect sizes.

Green result:

- within-source patching works as positive control;
- copied-attention target follows source counterfactuals substantially above frozen random and behavior distillation;
- behavior distillation may match ordinary behavior but fails intervention transfer.

Elite result:

- an adapter-only or larger-substrate-gap target preserves causal variables above behavior-only and random controls.

Kill result:

- within-source patching fails;
- patching produces no stable counterfactual effect;
- behavior-only distillation scores as well as copied attention under causal intervention;
- alignment performance is dominated by trivial output leakage.

## 30-Day Prototype

If the 7-day proof passes:

1. Generalize patching to attention, schema hidden, report, and policy variables.
2. Run the full 22 validated-source condition family.
3. Add source lesions:
   - attention lesion;
   - schema lesion;
   - self-model lesion;
   - policy/logit lesion.
4. Add adversarial controls:
   - behavior-matched distillation;
   - output-logit imitation;
   - random aligned subspace;
   - shuffled-source patches.
5. Produce a causal preservation profile.
6. Draft Paper 5 around the distinction between behavioral preservation and causal preservation.

## Candidate Alternatives

### Alternative A: Gradual Replacement Benchmark

Question:

> Does gradual module replacement preserve source-like function better than one-shot scan-and-copy under matched final architecture?

Why it matters:

- Directly attacks the philosophical distinction between gradual replacement and scan-copy.
- Closely tied to Paper 1's cross-theory preservation strategy analysis.

Risk:

- In artificial neural systems, final parameters may dominate path unless the experiment is carefully designed.
- Could become an optimization-path paper rather than a consciousness-preservation paper.

Verdict:

Strong Paper 6 candidate. Keep it in reserve unless causal preservation prototype fails.

### Alternative B: Cross-Theory PreservationBench

Question:

> Do AST, GWT, HOT, and RPT-style indicator mechanisms show different transfer failure profiles?

Why it matters:

- Broadens beyond AST.
- More directly connects to the consciousness-indicator field.

Risk:

- Large implementation burden.
- Could become shallow if each theory gets only a toy implementation.

Verdict:

Strong long-term direction, but too broad for the next paper unless scoped to one extra theory, probably GWT.

### Alternative C: WBE Fidelity Bridge

Question:

> Can PreservationBench define intervention-based fidelity tests for brain emulation?

Why it matters:

- Directly bridges to whole-brain emulation and biological preservation.

Risk:

- Without biological data, this becomes mostly conceptual.

Verdict:

Better as a framing section inside Paper 5 or a later review/methods paper.

## Decision

Paper 5 should pursue causal preservation.

Reason:

- It is the cleanest next step from Papers 3-4.
- It directly answers the strongest caveat.
- It borrows serious machinery from causal abstraction and model alignment rather than inventing loose new language.
- It can be prototyped quickly on existing runs.
- If it works, it gives the project a more defensible claim: preservation is not behavior, not report, not identity fingerprint, and not perturbation robustness alone; it is causal mechanism survival under controlled intervention.

## Source Pointers

- Butlin et al. 2023, "Consciousness in Artificial Intelligence: Insights from the Science of Consciousness" — https://doi.org/10.48550/arXiv.2308.08708
- Butlin and Lappas 2025, "Principles for Responsible AI Consciousness Research" — https://doi.org/10.48550/arXiv.2501.07290
- COGITATE Consortium 2025, "Adversarial testing of global neuronal workspace and integrated information theories of consciousness" — https://doi.org/10.1038/s41586-025-08888-1
- Linssen and Koene 2025, "Functional Tests Guide Complex Fidelity Tradeoffs in Whole-Brain Emulation" — https://doi.org/10.55613/jeet.v35i1.152
- Zanichelli et al. 2025, "State of Brain Emulation Report 2025" — https://doi.org/10.48550/arXiv.2510.15745
- Jin et al. 2026, "Whole-Brain Connectomic Graph Model Enables Whole-Body Locomotion Control in Fruit Fly" — https://doi.org/10.48550/arXiv.2602.17997
- Geiger et al. 2023/2024, "Causal Abstraction: A Theoretical Foundation for Mechanistic Interpretability" — https://doi.org/10.48550/arXiv.2301.04709
- Geiger et al. 2024, "Finding Alignments Between Interpretable Causal Variables and Distributed Neural Representations" — https://arxiv.org/abs/2303.02536
- Model Alignment Search — https://arxiv.org/abs/2501.06164
- Dossa et al. 2024, "Design and evaluation of a global workspace agent embodied in a realistic multimodal environment" — https://doi.org/10.3389/fncom.2024.1352685
- Cheng et al. 2026, "LifeBench: A Benchmark for Long-Horizon Multi-Source Memory" — https://arxiv.org/abs/2603.03781
