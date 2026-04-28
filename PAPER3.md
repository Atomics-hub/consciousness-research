# Paper 3 Working Charter

## Working Title

**The Preservation Benchmark: Testing Functional Continuity Across Substrate Transfer**

Alternate titles:

- Functional Continuity Across Substrate Transfer
- A Benchmark Suite for Preservation-Relevant Functional Continuity
- What Survives the Move? A Benchmark for Preservation Claims
- ContinuityBench: A Substrate Transfer Benchmark for Toy Agents

Working repo name: **PreservationBench**
Working paper name: **The Preservation Benchmark**

## Core Thesis

Paper 1 mapped theories of consciousness to preservation requirements. Paper 2 tested one narrow AST-style transplant assay. Paper 3 should make the bigger move: propose and pilot a benchmark framework for testing what survives when an agent is copied, transplanted, adapted, compressed, or moved into a new architecture.

The claim is not that a benchmark can detect consciousness or prove personal survival. The claim is that any serious preservation proposal should be able to say which functional, mnemonic, self-model, preference, report, and control capacities survive transfer under controlled conditions.

## One-Sentence Pitch

This paper turns substrate-transfer and mind-preservation debates into a benchmarkable engineering problem: train an agent, move candidate mind-relevant machinery into a target substrate, and measure which kinds of preservation-relevant functional continuity survive.

## Safest Novelty Claim

To my knowledge, no existing benchmark explicitly evaluates preservation-relevant functional continuity across substrate transfer. Prior work evaluates static AI consciousness indicators, agent memory persistence, model or component transfer, continual learning, or biological emulation fidelity. The proposed benchmark differs by making substrate transfer the central intervention and scoring whether theory-specified consciousness-relevant and identity-relevant functions remain active across that transfer under copied-state and relearning controls.

Avoid claiming:

- first AI consciousness benchmark
- first agent identity benchmark
- first model transplant method
- first mind-uploading validation proposal
- a benchmark for personhood or survival

## Claim Ladder

1. This does not test consciousness.
2. It tests whether specified functional invariants survive transfer.
3. Those invariants are preservation-relevant under some theories.
4. Passing the benchmark would not prove survival.
5. Failing it would identify concrete engineering obstacles for functionalist preservation programs.

## Core Definitions

- **Substrate transfer:** moving mind-relevant organization from one implementation into another while testing whether relevant capacities remain active.
- **Functional continuity:** persistence of causal roles, control relations, memory access, self-model use, attention dynamics, report dynamics, and policy-relevant internal organization across transfer.
- **Preservation-relevant functional continuity:** functional continuity for properties that matter to preservation theories, including psychological connectedness, autobiographical memory, self-model integrity, metacognitive access, agency, temporal integration, and source-specific dispositions.
- **Causal continuity:** the target state is caused by extraction, copying, adaptation, or replacement from the source, rather than by ordinary independent retraining.
- **Phenomenal continuity:** continuity of subjective experience itself. This benchmark should not claim to measure it directly.
- **Benchmark-positive result:** evidence that source-specific functional organization survives transfer and remains behaviorally or mechanistically active in the target.
- **Benchmark-negative result:** evidence that copied state survives only as inert information, or that performance depends on relearning rather than preserved organization.

## Theory Scope

The benchmark can be useful for:

- psychological-continuity views
- functionalism
- Attention Schema Theory
- higher-order theories
- global workspace theories
- recurrent processing theories
- predictive-processing views

The benchmark is weaker or incomplete for:

- IIT-style substrate-sensitive interpretations
- biological-continuity views
- biological computationalism
- quantum or microphysical theories
- views that require uninterrupted first-person phenomenal continuity

The paper should be explicit that the benchmark is theory-indexed, not theory-neutral.

## Benchmark Axes

### 1. Substrate Gap

- same architecture, new initialization
- same family, different peripheral mappings
- different architecture
- different representation space
- different body, sensor, or action interface

### 2. Copied Payload

- full agent
- attention or schema module
- self-model or identity module
- memory store
- preference vector
- recurrent state
- workspace state
- policy head
- combinations of the above

### 3. Adaptation Regime

- frozen copied state
- copied but trainable
- adapter-only tuning
- supervised source-alignment adapter
- full fine-tuning
- behavior-only distillation
- full retrain from scratch

### 4. Evaluation Domain

- same environment distribution
- shifted environment distribution
- delayed query setting
- changed sensor or body mapping
- social or partner setting
- hidden provenance probes

## Benchmark Output

The benchmark should report a profile, not one consciousness score.

- **Task competence continuity:** reward, success rate, recovery speed.
- **Memory continuity:** source-specific recall, temporal order, context binding.
- **Preference continuity:** stable choices under equivalent options.
- **Self-model continuity:** source-specific fingerprint probes and behavioral use of those probes.
- **Report continuity:** report accuracy, calibration, stability.
- **Attention and world-model continuity:** attention-map similarity, predictive accuracy, object persistence.
- **Temporal continuity:** recurrence dependence, delay robustness, hidden-state reuse.
- **Causal use:** performance drop when copied modules are ablated after transfer.
- **Adaptation cost:** steps required to recover a fixed fraction of source performance.

## Minimum Viable Paper 3

The first publishable version should be bigger than Paper 2, but still runnable locally.

Build **PreservationBench-AST v0**:

1. Keep the Paper 2 AST environment as the first task family.
2. Preserve Paper 2 as a frozen reproduction path.
3. Add a benchmark harness beside it under `experiments/preservation_bench`.
4. Run 20 to 30 independent source seeds if compute allows. The expanded AST v0 run now uses 30 attempted source seeds.
5. Pair all conditions on the same evaluation episode seeds.
6. Compare copied-state transfer against random, frozen-random, behavior-distillation, architecture-matched, and full-retrain controls.
7. Analyze at the training-seed level, not the episode level.
8. Report raw metrics, paired differences, CIs, effect sizes, and a preservation profile figure.

Primary conditions for v0:

- source full agent
- source attention ablated
- source schema ablated
- source self-model ablated
- A->A architecture-matched copy
- A->B frozen copied schema and self-model
- A->B adapter-only repair with copied schema and self-model frozen
- A->B copied-trainable repair
- A->B frozen random bundle
- A->B trainable random control
- A->B behavior-only distillation
- B full retrain

Primary metrics for v0:

- reward
- goals found
- distractor capture rate
- self-report correlation
- other-report correlation, only if validated above floor
- identity probe accuracy
- memory overlap, diagnostic only
- adaptation steps to threshold
- frozen parameter count and trainable parameter count

## Stronger V1 Direction

After the AST v0 is stable, add a broader ContinuityBench suite:

- attention and report task for AST
- confidence task for higher-order theories
- delayed binding task for global workspace style broadcast
- delayed match or masked sequence task for recurrence
- remapping task for predictive processing
- autobiographical continuity task for memory, preferences, and source identity

That becomes the bigger swing: not an eight-theory consciousness scoreboard, but a battery for preservation-relevant transfer channels.

## High-Risk Overclaims

Avoid:

- "This benchmark tests consciousness preservation."
- "A successful transfer proves the copy is the same person."
- "Gradual replacement and scan-copy are empirically equivalent."
- "Self-model fingerprint preservation equals identity preservation."
- "AST friendliness means preservation is easy."
- "Failure of a toy transplant refutes AST or functionalism."
- "Functional indistinguishability settles phenomenal consciousness."
- "A benchmark can resolve the hard problem."

Prefer:

- "preservation-relevant functional continuity"
- "substrate-transfer assay"
- "benchmark profile"
- "toy validation tier"
- "necessary but not sufficient evidence"
- "copied state versus relearning"
- "theory-indexed evidence"
- "functional invariants"

## Paper Structure

1. Introduction: the gap between preservation thought experiments and tests.
2. Background: Paper 1 theory map, Paper 2 AST assay, adjacent benchmarks.
3. Definitions: functional continuity, causal continuity, psychological continuity, phenomenal continuity.
4. Benchmark desiderata: what preservation-relevant testing must separate.
5. PreservationBench specification: tasks, transfer protocols, controls, metrics.
6. AST v0 implementation: agents, substrates, payloads, seeds, evaluation.
7. Results: continuity profiles across payloads and adaptation regimes.
8. Discussion: what benchmark success and failure can show.
9. Limitations: toy agents, functionalist scope, lack of phenomenal ground truth.
10. Next steps: richer tasks, social probes, memory systems, heterogeneous substrates.

## Immediate Build Plan

1. Create Paper 3 docs: protocol, stats plan, literature map.
2. Create the `experiments/preservation_bench` scaffold.
3. Add a stable seed registry helper.
4. Add paired-difference stats helpers before running new experiments.
5. Port AST evaluation into a log-first runner.
6. Add condition registration for v0 controls.
7. Run a 2-seed smoke test.
8. Run a 5 to 8 seed pilot for variance and power.
9. Choose the final seed count.
10. Freeze the protocol before final results.

## Current Implementation Status

Completed in the first Paper 3 pass:

- created the Paper 3 charter, protocol, stats plan, literature map, and smoke results notes
- created the `experiments/preservation_bench` scaffold
- added stable seed registry generation with paired evaluation seeds
- added log-first AST episode evaluation
- added seed-summary and paired-contrast analysis tools
- added checkpoint smoke evaluation from the Paper 2 AST checkpoint
- added adapter-only repair, copied-trainable repair, random controls, and behavior-only distillation smoke conditions
- added a two-source-seed training smoke runner
- added source validation gates and per-seed resumable manifests
- added full-retrain condition support and a 5-seed pilot config
- added preservation-profile figure generation from seed summaries
- ran the first 5-seed pilot and confirmed all source seeds passed validation
- added competence smoke configs with stricter goal-success validation
- added competence v2 5-seed config using the improved small-arena task
- added validation-aware summary and contrast analysis for excluding failed source seeds
- ran the competence v2 5-seed pilot: 4 of 5 source seeds passed validation
- added and ran `b_source_align_repair_copy`, a copied-state repair condition trained to match source attention, reports, features, identity state, and Q-values
- confirmed source-alignment repair improves target self-report relative to frozen copy while preserving identity probes, but still does not restore source-level task or report behavior
- added `b_source_align_repair_copy_long` with a 24000-step alignment budget and matched target-init/finetune seeds against the short source-alignment condition
- confirmed the longer alignment condition improves mean reward and self-report while preserving identity probes, but effects are seed-variable and still far below source continuity
- added and ran `b_source_align_policy_copy_long`, which copies and freezes the source policy head during long source-alignment repair
- confirmed copied-policy long repair preserves identity but underperforms long source-alignment on reward and self-report, so a frozen copied policy head is not the missing coupling mechanism in this setup
- added and ran `b_source_align_attention_copy_long`, which copies and freezes the source attention module, initializes adapters to identity, and uses the long source-alignment budget
- confirmed copied-attention long repair nearly closes the reward and report gap while preserving identity probes, making attention/interface coupling the current leading bottleneck
- added and ran `b_source_align_attention_copy_random_adapter_long`, which keeps copied frozen attention but uses randomly initialized trainable adapters
- confirmed copied attention remains strong even without identity-initialized adapters, so adapter initialization is not the main explanation for the recovery
- added and ran `b_source_align_identity_adapter_long`, which keeps target transformer attention but initializes adapters to identity
- confirmed identity adapters alone do not recover reward or report behavior, strengthening the read that the attention/front-end is the bottleneck
- added and ran `b_source_align_attention_copy_trainable_long`, which copies source attention but leaves it trainable during long source-alignment
- confirmed trainable copied attention remains close to the frozen copied-attention condition while preserving identity probes, so the copied attention initialization survives even when the module can adapt
- added and ran `b_source_align_attention_adapter_long`, which keeps target transformer attention but adds a residual source-facing interface adapter instead of copying source attention
- confirmed the adapter bridge recovers strong self-report and preserves identity, but fails task control and goal recovery. This separates report-interface recoupling from attention-control continuity
- added attention-control diagnostics: goal attention mass, distractor attention mass, source attention distance, source feature distance, and source action agreement
- confirmed copied-attention conditions recover source-like goal attention and source action agreement, while the adapter bridge does not. The adapter bridge is therefore report-like without being control-like
- added and ran `b_source_align_control_adapter_long`, which keeps the target attention substrate and residual source-facing interface while adding explicit control and attention-mass losses
- confirmed the control adapter drives very high reward and goal-attention mass while preserving copied identity, but it does not restore source-like goals found, source action agreement, or full report continuity. This is a proxy-control failure mode, not a preservation win
- regenerated the normalized preservation-profile figure with reward, goals found, goal-attention mass, self-report, source-action agreement, and identity probes
- added `ast_competence_v2_core_10seed.json`, a reduced replication config with the source ablations, frozen copy, long repair, copied attention, attention adapter, control adapter, behavior distillation, and frozen random controls
- ran the core 10-seed replication: 8 of 10 source seeds passed validation, with seeds 3 and 5 rejected for low goals found
- confirmed the pilot pattern replicated in the reduced 10-seed run: copied-attention transfer recovers the strongest combined report, goals-found, and source-action profile; attention-adapter transfer recovers report without source-like control; control-adapter transfer drives reward and goal-attention proxy mass without restoring source-like goals found or source action agreement
- added `plot_core_figures.py` and generated focused paper figures for source validation flow and core transfer metrics
- drafted the AST v0 Results and Discussion text in `paper3/ast_v0_results_draft.md`
- created the main manuscript draft at `paper3/manuscript.md`
- generated trackable manuscript figures under `paper3/figures/`
- added `ast_competence_v2_core_30seed.json`, extending the same core seed scheme to 30 attempted source seeds while reusing the first 10 completed seeds
- ran the expanded 30-seed core replication: 22 of 30 source seeds passed validation, with rejected seeds 3, 5, 17, 19, 22, 23, 24, and 29
- confirmed the expanded pattern at validated n = 22: copied attention remains the strongest combined profile, the attention bridge remains report-like without source-like control, and the control bridge still shows proxy-control failure
- regenerated manuscript figures, result text, and the PDF around the expanded seed count

Next build targets:

1. Final reviewer-style prose pass on the expanded n = 22 manuscript.
2. Rebuild and visually audit the PDF.
3. Run a final citation and reproducibility audit.
4. Prepare Zenodo/GitHub release metadata when the manuscript is stable.
