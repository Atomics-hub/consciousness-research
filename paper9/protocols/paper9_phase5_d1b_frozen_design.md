# Paper 9 Phase 5 — D1B frozen breadth-gate design

**Frozen:** 2026-08-22, before candidate outcomes from checkpoints 005–009  
**Status:** exploratory breadth gate; D2 remains **NO-GO**  
**Claim symmetry:** robustness and composition failure receive equal evidential weight

## 1. Question and claim ceiling

D1B asks whether the D1A compositional-robustness region survives a broader, adversarial test across an ON motion-output block (T4a), an OFF motion-output block (T5a), and an upstream ON-pathway block (Mi1), under a twelve-direction motion battery, a frozen pretrained flow decoder, and three substitute families.

This is an in-silico test of a public connectome-constrained model. It cannot establish facts about fly consciousness, biological replacement, personal identity, or preservation of a subject. A positive result is limited to a computational composition failure within the frozen model and interfaces. A null is limited to a measured robustness region.

## 2. Frozen checkpoint firewall

| Checkpoint | Permitted role | Candidate exposure |
|---|---|---|
| 005 | source-ensemble margin estimation and decoder smoke test | none |
| 006 | source-ensemble margin estimation | none |
| 007 | third source member, then local candidate calibration | calibration only |
| 008 | ordinary-response, direction-tuning, and fixed-decoder holdout | first global holdout |
| 009 | replication plus perturbation-effect holdout | final exploratory holdout |

Checkpoints are trained-model replicates, but their independent-randomization provenance remains incomplete. Neurons, columns, frames, directions, and stimuli are nested observations, not independent replicates.

## 3. Frozen blocks and motion battery

- Blocks: T4a, T5a, and Mi1; each contains 721 nodes in the pinned connectome.
- Replacement fractions: 0%, 25%, 50%, and 100%, using the existing deterministic spatially balanced mask rule.
- Motion: `MovingEdge`, angles `0, 30, ..., 330` degrees, both intensities `0` and `1`, offsets `[-10, 11]`, speed `19`, height `80`, `t_pre=t_post=0.5`, `dt=0.02`, and `post_pad_mode="continue"` (24 trajectories).
- No direction, contrast, block, checkpoint, or failed run may be dropped after outcome inspection.

T4a and T5a are direction-selective output blocks associated with ON and OFF motion pathways; Mi1 is an upstream/intermediate ON-pathway block. These labels describe the source annotations, not newly measured biology.

## 4. Frozen substitute families and capacity ledger

1. **Exact sham:** source equation through the substitution route. It must be bit-exact under the tested execution path.
2. **State-dependent timescale:** the D1A family frozen at `alpha=0.01`; no additional state, one shared fixed coefficient, no fitted per-node parameters.
3. **Two-state adaptation:** the D1A family frozen at `beta=0.25`, `tau=0.1`; one additional scalar state per replaced node, two shared fixed coefficients, no fitted per-node parameters.
4. **Conductance-inspired shunt:** a third structurally distinct family. For selected nodes only, add

   `gamma * sigmoid((activity - theta) / scale) * (E_rev - activity)`

   to the source activity velocity, with frozen `theta=0`, `scale=1`, `E_rev=1`. It adds no state and has one calibrated shared coefficient, `gamma`; it is not asserted to be a biophysical conductance model. Calibration grid: `0.0001, 0.00025, 0.0005, 0.001, 0.0025, 0.005, 0.01, 0.025, 0.05, 0.1`. Wrong control: `gamma=1`.

The selected `gamma` is the largest grid value passing all three block-level local gates on checkpoint 007. If no value passes, the family is killed. If its aggregate local derivative NRMSE is less than one quarter of the applicable local margin in every block, it is killed as identity-by-epsilon even if it passes.

No candidate may access checkpoint identity, node identity, source derivatives at runtime, per-node adapters, lookup tables, or a refitted decoder.

## 5. Source-grounded margins

Margins are computed before candidate calibration from source checkpoints 005–007 only.

For each block and source checkpoint, form central-column response traces for all 24 motion trajectories and source-equation velocity traces over every node in the block. For each checkpoint pair, compute standardized RMSE after centering each trace and scaling it by its own RMS. Let `q10_response` and `q10_velocity` be the 10th percentiles across checkpoint-pair × block × trajectory comparisons. Exact-sham numerical error is also recorded.

- Local derivative margin: `min(0.01, 0.25 * q10_velocity)`, with a floor of `10 * exact_sham_local_error`.
- Block-response margin: `min(0.01, 0.25 * q10_response)`, with a floor of `10 * exact_sham_response_error`.
- Decoder margin: `min(0.01, 0.25 * q10_decoder)`, where `q10_decoder` uses standardized pairwise pretrained-decoder output differences over the same source movies, with a floor of `10 * exact_sham_decoder_error`.
- Neural perturbation-effect margin: the frozen block-response margin. Decoder perturbation-effect margin: the frozen decoder margin. No separate effect margin is estimated from the same interventions being judged.

If checkpoint-coordinate nonidentifiability makes any pairwise quantity uninterpretable, the corresponding authored 1% ceiling remains in force and the limitation is reported; it is not replaced by a looser margin. No margin may be changed after candidate/global outcomes.

## 6. Frozen measurements

### Local equivalence

For each family × block, report derivative NRMSE and p99 absolute-error ratio under source-clamped trajectories. A local pass requires both to be at or below the frozen local margin for every intensity and for the aggregate battery. Maximum pointwise error is descriptive and cannot rescue or veto the declared gate.

### Ordinary and directional responses

For locally passing candidates at every replacement fraction, report all-node NRMSE, replaced-block NRMSE, unreplaced-node NRMSE, central-column traces, twelve-direction tuning curves separately by intensity, preferred-direction shift, tuning-vector cosine, direction-selectivity magnitude change, finiteness, and terminal error.

### Fixed-decoder endpoint

Recover the pretrained decoder belonging to the same source checkpoint, set evaluation mode, freeze every parameter, and apply it unchanged to source, exact-sham, candidate, and wrong-control activity. Report decoded-flow NRMSE, vector cosine, endpoint-error change against the dataset target if shape-compatible, and direction-stratified errors. A decoder refit is prohibited in the primary gate.

### Perturbation effects

On checkpoint 009, for candidates that pass checkpoint-008 local and ordinary gates, apply a `+0.01` activity impulse to the replaced block at frame 25 under preregistered angle/intensity cells `(0,0)`, `(90,1)`, `(180,0)`, and `(270,1)`. Compare within-system perturbed-minus-base vectors using effect NRMSE, block-effect NRMSE, cosine, sign agreement, and decoder-effect NRMSE. Exact sham must be zero.

### Numerical controls

Repeat decisive checkpoint-009 cells at `dt=0.01` using a freshly rendered compatible stimulus. A claimed failure is killed if it reverses or falls below its margin under this control. Topology digests must remain unchanged. Crashes and nonfinite states count as failures, not exclusions.

## 7. Outcome classification

Each checkpoint × block × family × fraction is classified:

- **G0:** local gate fails; global results are diagnostic only.
- **G1:** local pass and ordinary, decoder, and causal endpoints remain within their practical margins.
- **G2:** local pass plus ordinary-response or fixed-decoder deviation above its margin, stable and solver-robust.
- **G3:** local and ordinary/decoder pass but perturbation-effect deviation exceeds its margin, stable and solver-robust.

No pooled average can hide a block, intensity, direction, or checkpoint failure.

## 8. Advance and kill rules

Advance toward a D2 design only if one of these high-bar outcomes occurs:

1. **Composition-failure route:** G2 or G3 replicates on checkpoints 008 and 009 in at least two blocks or two informative substitute families, with exact/wrong controls behaving, in-support trajectories, and solver robustness.
2. **Robustness-frontier route:** at least two informative families pass locally across all three blocks and both checkpoints, with all frozen ordinary, decoder, and perturbation endpoints remaining within margin. This supports a bounded robustness theorem-candidate, not general compositionality.

Kill or redesign D1B if the decoder cannot be recovered unchanged; source-grounded margins cannot be defined without coordinate laundering; every passing candidate is identity-by-epsilon; wrong controls do not separate; exact shams are nonzero; failures are numerical/out-of-support; only one checkpoint supports the result; or runtime exceeds the zero-spend local envelope.

## 9. Release boundary and null value

Release is not authorized. If later authorized, exploratory and confirmatory artifacts must remain separated. D1B code, frozen design, manifests, raw summaries, exclusions, crashes, and nulls should be releasable. Thomas Ryan is the sole human author and accountable operator; AI assistance is not authorship.

A clean G1 result across the frozen breadth is publishable as a quantified robustness frontier for connectome-constrained dynamics substitution. G0-heavy results identify the local-equivalence class as too restrictive. Decoder-only or causal-only dissociations remain useful interface-sensitivity results. A total failure of measurement controls is a reproducibility/methods result, not evidence for either scientific thesis.
