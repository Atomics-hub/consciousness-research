# Paper 9 Program D staged protocol

**Date:** 2026-08-20  
**Status:** Stage D0 passed; D1A measurement gate passed; D1B breadth gate recommended  
**Working title:** *When Local Neural Equivalence Fails to Compose: Cell-Type Substitution in a Connectome-Constrained Visual System*

## 1. Research question

In a fixed, biologically anchored connectome model, does local dynamical equivalence on held-out trajectories imply preservation of global neural responses, decoded behavior, and perturbation-effect structure when alternative neuron dynamics are substituted by cell-type block?

The program tests composition, not consciousness. The fixed-connectome model is an experimental object, not a fly individual.

## 2. Source system

Use the public [Lappalainen et al. fly visual-system model](https://www.nature.com/articles/s41586-024-07939-3) and [MIT-licensed `flyvis` code](https://github.com/TuragaLab/flyvis). Pin the repository and checkpoint manifest before generating results. The version inspected during Phase 3 exposed a `NetworkDynamics` extension interface and was associated with commit `92b3845cc426dd309a1a0e1b3890156c42e14021`; Stage D0 must verify rather than assume this remains the selected revision.

The source model has 45,669 neurons and 1,513,231 fixed connectome edges, grouped into 64 cell types and 721 retinotopic columns, with 734 fitted parameters. Its default dynamics are passive leaky non-spiking point neurons with instantaneous graded-release synapses.

## 3. Estimands

For source checkpoint `s`, cell-type block `b`, substitute family `d`, and replacement fraction `r`, define:

- `L(s,b,d)`: held-out local-equivalence error over clamped input/state trajectories;
- `N(s,b,d,r)`: global neural-response deviation;
- `B(s,b,d,r)`: optic-flow or task-output deviation;
- `C(s,b,d,r)`: perturbation-effect deviation;
- `S(s,b,d,r)`: numerical stability and support diagnostics.

The primary composition estimand is the change in `N/B/C` across the replacement ladder among substitutes that pass a frozen `L` margin. A positive composition failure requires a local pass, stable in-support global trajectories, and a global deviation exceeding a frozen practical margin. Statistical significance alone is insufficient.

## 4. Stage D0 — feasibility and source-validity gate

No full training occurs in D0.

**Current status (2026-08-21):** All D0 implementation and qualitative source-response checks passed. The official archive was acquired under hard caps and verified; three checkpoints reproduced L1 OFF preference; checkpoint 000 passed exact-sham and 1% substitution screens. Confirmatory independence remains unresolved because per-run randomization provenance is incomplete.

1. Create an isolated supported Python environment; do not use an unsafe duplicate-OpenMP override.
2. Pin code revision, environment lock, pretrained checkpoint IDs, file hashes, and dataset/stimulus versions.
3. Reproduce at least one documented neural response and one decoded output from a pretrained checkpoint.
4. Confirm at least three independently trained public checkpoints are usable. Treat checkpoint/training seed—not neuron or cell type—as the main replication unit.
5. Implement an exact re-expression of the default dynamics through the extension interface. It must match the source within a frozen numerical tolerance.
6. Demonstrate cell-type-masked mixed dynamics while preserving node/edge topology and parameter provenance.
7. Benchmark baseline, exact sham, and 1% substitution on local CPU and Apple acceleration if supported. Record peak memory, wall time, determinism, and numerical discrepancies.
8. Run a final targeted exact-prior-art query over the chosen dynamics families and cell-type blocks.

### D0 advance criteria

Advance only if source reproduction, exact sham, mixed assignment, three-checkpoint availability, and zero-spend runtime all pass. Any core-framework rewrite that changes connectome computation triggers an independent validation requirement and defaults to no-go.

## 5. Stage D1 — exploratory calibration

**D1A update (2026-08-21):** State-dependent and two-state candidates were tested across checkpoints 000–004. Exact and wrong controls behaved correctly. Locally passing candidates preserved ordinary, directional, and impulse-effect endpoints within the exploratory margins; the first frozen transport candidate failed locally and was killed. No local-pass/global-fail result was observed. Do not advance to D2; follow the Phase 4 D1 report's breadth gate first.

### Cell-type blocks

Begin with a preregistered small set in the motion pathway: T4/T5 plus upstream cell types supported by the source paper and connectome annotations. Select blocks before examining substitution outcomes. Do not search all 64 cell types and report winners.

### Substitute families

Use at least three controls/families:

1. **Exact sham:** mathematically identical dynamics through the replacement pathway.
2. **Alternative low-order dynamics:** an adaptive-leak or two-state surrogate calibrated locally.
3. **Wrong-dynamics control:** parameter-count-matched dynamics expected to fail local equivalence.

A conductance-inspired surrogate may be explored only if it can be calibrated without an unconstrained per-neuron adapter. The early fly visual system is graded/non-spiking in the source model, so a spiking substitution is not automatically more biological.

### Local calibration corpus

Clamp each candidate block with presynaptic drive trajectories drawn from:

- naturalistic optic-flow movies;
- flashes, moving edges, gratings, and contrast/frequency sweeps;
- controlled amplitude and temporal-frequency extrapolations;
- source-state perturbations within declared support.

Partition by whole stimulus trajectory, not time point. Training/calibration, local-validation, and global-evaluation stimuli must be disjoint. Freeze the local margin using measurement repeatability, source-ensemble variation, and exact-sham numerical noise—not observed global outcomes.

### Replacement ladder

Evaluate 0%, 25%, 50%, and 100% replacement within each selected cell-type block. Fractions use deterministic, spatially balanced column selections fixed before outcomes. Include at least one randomized column assignment as a robustness analysis.

### Global endpoints

- cell-type response correlations and tuning curves;
- T4/T5 direction selectivity;
- optic-flow decoder error or the source model’s documented task output;
- impulse, ablation, and stimulus-intervention effect vectors;
- local Jacobian/effect-sign agreement where estimable;
- recurrent stability, state-support coverage, and numerical integration sensitivity.

### Decisive controls

- exact replacement sham;
- zero-replacement baseline;
- topology-preserving wrong-dynamics control;
- wrong-cell-type substitution;
- decoder-only refit control, reported separately and excluded from the primary preservation estimand;
- local-pass/global-fail synthetic sentinel from the Phase 3 composition fixture;
- source-conditioned capacity ledger for parameters, adapters, initial state, interfaces, checkpoint identity, and calibration exposure;
- integration-step and solver sensitivity;
- in-support/out-of-support stratification.

Stage D1 is explicitly exploratory. It selects workable dynamics families, equivalence margins, stimuli, block definitions, effect summaries, and compute ceilings. It cannot provide confirmatory p-values or the final Paper 9 claim.

## 6. Stage D2 — confirmatory experiment

Start D2 only with a timestamped preregistration and immutable D1-to-D2 separation. Freeze:

- repository commit and environment;
- checkpoint manifest and inclusion rules;
- cell-type blocks and replacement assignments;
- substitute equations, parameter bounds, and fitting procedure;
- local-equivalence margins;
- stimuli and perturbations;
- global practical-equivalence/failure margins;
- primary outcome hierarchy;
- exclusion, missingness, numerical-failure, and multiplicity rules;
- seeds and analysis code hash.

Use held-out pretrained checkpoints or newly trained checkpoints only if local zero-spend compute permits a frozen training protocol. Checkpoint is the independent unit. Repeated stimuli, neurons, columns, and perturbations are nested measurements, not independent replicates.

### Primary decision rule

For a substitute declared locally equivalent, classify each checkpoint/block/fraction as:

- **G0:** local equivalence fails—global preservation is uninterpretable;
- **G1:** local pass and global practical equivalence;
- **G2:** local pass and global neural/behavior failure;
- **G3:** local pass and global perturbation-effect failure despite ordinary-output pass.

Require replication across at least three source checkpoints and more than one substitute family before a general composition claim. Report the entire ladder and every assigned path, including crashes and local failures.

## 7. Kill criteria

Stop or redesign before confirmatory work if any occurs:

1. source checkpoints do not reproduce held-out documented biology or task outputs;
2. fewer than three independently trained checkpoints are usable;
3. cell-type-conditional substitution requires changing topology or unvalidated core computation;
4. local equivalence requires per-neuron source fingerprints or adapter capacity comparable to the source dynamics;
5. apparent global divergence vanishes under solver/step-size controls;
6. divergence is explained entirely by out-of-support states or numerical instability;
7. a refitted decoder removes the effect and the intended claim concerns internal preservation rather than fixed-interface function;
8. no substitute both passes the local gate and differs mechanistically enough to make the test informative;
9. measured runtime exceeds the zero-spend ceiling;
10. exact prior art establishes the same fixed-connectome, locally matched, blockwise substitution and global causal test.

## 8. Ethics and interpretation

This is an in-silico experiment using public model artifacts. It does not manipulate living animals. The main ethical risks are anthropomorphic or consciousness overclaiming, misrepresenting model substitution as biological replacement, and treating connectome availability as consent or identity evidence. Mitigate these through the claim ceiling, explicit computational-model language, and no subject-preservation terminology.

Thomas Ryan is the sole human author and accountable operator. AI assistance must be disclosed according to venue policy and must not be listed as an author.

## 9. Null-result value

Every gated null is publishable if the protocol is followed:

- **Source reproduction fails:** a reproducibility audit of the public biological model.
- **No alternative passes locally:** evidence that the declared local equivalence class is too strict or poorly posed.
- **All local-pass substitutes preserve globally:** an empirical robustness region for the tested connectome model.
- **Global changes track support violations only:** a boundary-of-validity map for local calibration.
- **Neural effects occur without output effects:** a behavior/causal dissociation with direct relevance to preservation metrics.
- **No effect across the ladder:** an upper bound on substitution sensitivity under frozen margins and checkpoints.

## 10. Release plan

1. Release D0 environment lock, pinned-source manifest, reproduction notebook/script, and benchmark report regardless of outcome.
2. Freeze and archive D1 exploratory decisions separately; label all D1 figures exploratory.
3. Timestamp the D2 preregistration before confirmatory checkpoints or outcomes are accessed.
4. Release code, stimulus manifests, checkpoint identifiers/hashes where licensing permits, assigned replacement paths, raw summary arrays, exclusions, crashes, and full null results.
5. Publish no consciousness probability, biological replacement claim, or fly-subject inference.
6. Keep generated hashes and tests described as integrity checks, never independent replication.

No external release is authorized by this protocol.
