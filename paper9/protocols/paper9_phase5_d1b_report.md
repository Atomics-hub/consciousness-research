# Paper 9 Phase 5 — D1B breadth-gate report

**Date:** 2026-08-22  
**Decision:** **D1B measurement PASS; D2 NO-GO; targeted D1C seam only**

## Bottom line

D1B substantially broadened Program D without finding an ordinary-response composition failure. Across T4a, T5a, and upstream Mi1; twelve motion directions and two contrasts; three substitute families; full replacement ladders; and two untouched checkpoints, every locally eligible ordinary-response and fixed-decoder cell remained within the frozen 1% margins. Checkpoint 008 yielded 21 G1, 2 G0, and 0 G2 ladder cells; checkpoint 009 yielded 24 G1, 1 G0, and 0 G2.

A narrower causal seam emerged. Full Mi1 replacement with the state-dependent-timescale family preserved ordinary activity and decoded motion but changed the magnitude of an activity-impulse effect at the fixed decoder. This G3 classification replicated on checkpoints 008 and 009 and survived halving the integration step. At `dt=0.01`, decoder-effect NRMSE was 2.754% on checkpoint 008 and 2.025% on checkpoint 009, while neural-effect NRMSE was 0.932% and 1.020%, respectively. Effect cosines were 1.0 to reported precision, so this is a gain/magnitude deviation, not an effect-direction reversal.

This does **not** clear the frozen advance bar. The solver-robust cross-checkpoint G3 overlap is only one block × one family, and the effect is small and close to an authored threshold. D2 remains closed. The only justified continuation is a hostile D1C test of whether the seam exceeds what local-error magnitude alone predicts.

## 1. Frozen design and firewall

The full design was written before candidate outcomes in `paper9_phase5_d1b_frozen_design.md`.

| Checkpoint | Frozen role |
|---|---|
| 005–006 | source-only variability and margin estimation |
| 007 | third source-only member, then local-only candidate calibration |
| 008 | first global twelve-direction and decoder holdout; later causal replication |
| 009 | global replication, causal holdout, and solver control |

The battery comprised 24 `MovingEdge` trajectories: angles 0–330° in 30° steps, intensities 0 and 1, speed 19, and `dt=0.02`. T4a, T5a, and Mi1 each contained 721 retinotopic nodes. Fractions were 25%, 50%, and 100% with deterministic spatially balanced selection.

The fixed flow decoder was recovered from each checkpoint, placed in evaluation mode, and frozen. It has 7,427 parameters and reads the source model's 34 declared output channels. The synthetic moving-edge set has no task flow target; the endpoint therefore measures preservation of each checkpoint's unchanged pretrained-decoder output, not accuracy against an invented target.

## 2. Source-grounded margins

Source-only checkpoints 005–007 were compared before any candidate calibration. Pairwise standardized variation was much larger than the predeclared authored ceiling:

| Quantity | 10th-percentile source difference | One quarter | Selected margin |
|---|---:|---:|---:|
| local block velocity | 30.805% | 7.701% | **1.000%** |
| central block response | 19.488% | 4.872% | **1.000%** |
| pretrained decoder output | 72.354% | 18.089% | **1.000%** |

Thus source variation contextualized but did not relax the D1A threshold. These checkpoint differences are model uncertainty, not biological repeatability or proof of independent randomization.

## 3. Local calibration and capacity

The state-dependent-timescale family remained frozen at `alpha=0.01`. The two-state family remained frozen at `beta=0.25`, `tau=0.1`, with one charged adaptation scalar per replaced node. The new conductance-inspired shunt used a shared fixed equation and selected `gamma=0.01` on checkpoint 007; it has no added state or per-node parameter. It was not killed as identity-by-epsilon because T5a local derivative NRMSE was 0.522%, more than one quarter of the 1% margin. The wrong `gamma=1` shunt failed locally in every block.

Checkpoint-007 local results were:

| Family | Mi1 | T4a | T5a |
|---|---:|---:|---:|
| timescale | 0.908% pass | 0.716% pass | 0.956% pass |
| two-state | 0.985% pass | 0.613% pass | **1.864% fail** |
| shunt | 0.169% pass | 0.035% pass | 0.522% pass |

The two-state family again failed T5a on both global checkpoints under the intensity-stratified gate. It also failed Mi1 on checkpoint 008 (1.080%) but passed Mi1 on checkpoint 009 (0.943%). G0 cells were never interpreted as preservation or composition evidence.

## 4. Ordinary and fixed-decoder breadth results

### Checkpoint 008

- classification counts: 21 G1, 2 G0, 0 G2;
- largest eligible full-replacement block-response NRMSE: 0.235% (T4a two-state);
- largest eligible full-replacement decoder NRMSE: 0.441% (T4a two-state);
- wrong-control decoder NRMSE: 1.554–2.703%;
- exact sham error: zero;
- topology unchanged and all evaluated outputs finite.

### Checkpoint 009

- classification counts: 24 G1, 1 G0, 0 G2;
- largest eligible full-replacement block-response NRMSE: 0.305% (T4a two-state);
- largest eligible full-replacement decoder NRMSE: 0.403% (Mi1 timescale);
- wrong-control decoder NRMSE: 1.632–2.792%;
- exact sham error: zero;
- topology unchanged and all evaluated outputs finite.

Errors generally increased with replacement fraction, but no eligible 25%, 50%, or 100% cell crossed its ordinary or fixed-decoder margin. This supports a bounded ordinary-response robustness region across the tested blocks, candidates, stimuli, and checkpoints.

## 5. Causal-effect results

At frame 25 (`0.5 s`) a `+0.01` activity impulse was applied to the entire replaced block under frozen angle/intensity cells `(0,0)`, `(90,1)`, `(180,0)`, and `(270,1)`. Effects were computed within system before source–candidate comparison.

### Initial `dt=0.02` results

On checkpoint 009, four of eight eligible pairs crossed at least one 1% effect margin: timescale in Mi1, T4a, and T5a, plus T4a two-state. On checkpoint 008, only Mi1 timescale crossed. Exact neural and decoder effect errors were zero.

### Solver veto at `dt=0.01`

Halving the step preserved the physical impulse time at frame 50. T4a timescale and T4a two-state fell below margin and were killed as solver-sensitive. T5a timescale remained G3 on checkpoint 009 but was G1 on checkpoint 008, so it did not replicate across checkpoints.

The only cross-checkpoint, solver-robust G3 was Mi1 timescale:

| Checkpoint | `dt` | ordinary NRMSE | neural-effect NRMSE | Mi1-effect NRMSE | decoder-effect NRMSE | neural cosine |
|---|---:|---:|---:|---:|---:|---:|
| 008 | .02 | 0.0275% | 1.484% | 1.753% | 2.331% | 1.000 |
| 008 | .01 | 0.0127% | 0.932% | 0.837% | **2.754%** | 1.000 |
| 009 | .02 | 0.0275% | 1.326% | 1.185% | 1.897% | 1.000 |
| 009 | .01 | 0.0127% | **1.020%** | 0.809% | **2.025%** | 1.000 |

The ordinary NRMSE values in this table are for the four-trajectory causal subset. The relevant fixed-decoder effect deviation is stable, but its geometry is nearly collinear with the source effect. The defensible description is altered causal gain at a fixed interface, not altered causal organization.

## 6. Decision against frozen advance rules

### Composition-failure route: fail

The frozen rule required a solver-robust G2/G3 result across checkpoints 008 and 009 in at least two blocks or two informative families. Only Mi1 × timescale replicated. D2 is therefore **NO-GO**.

### Robustness-frontier route: fail at the strict all-endpoint bar

The shunt family passed locally and remained G1 across all three blocks and both checkpoints, but it is only one family. Timescale produced the Mi1 G3 seam; two-state failed T5a locally. Thus the frozen requirement of at least two informative families across all blocks and endpoints was not met.

### What survives

1. A strong ordinary-response null: no G2 among 45 locally eligible ladder cells across two checkpoints.
2. A methods result: local, ordinary, fixed-decoder, and causal gates separate meaningfully; exact and wrong controls behave.
3. A narrow hypothesis: source-clamped local equivalence and ordinary-output preservation may underconstrain causal gain at an upstream-to-decoder interface.

## 7. D1C kill-focused continuation

Do not widen claims or add more blocks indiscriminately. A bounded D1C should target the Mi1/timescale seam and attempt to kill it:

1. match timescale and shunt candidates on local derivative NRMSE within Mi1 rather than compare unequal perturbation strengths;
2. freeze a causal amplification estimand: decoder-effect NRMSE divided by local derivative NRMSE, plus signed gain ratio and absolute effect error;
3. require at least 3× amplification and at least 2% decoder-effect deviation to avoid threshold theater;
4. vary impulse amplitude and time to test linearity, saturation, and dependence on a single frame;
5. use untouched checkpoints 010–014 with a source-only effect-variability stage before candidate exposure;
6. include a matched-error shunt, exact sham, wrong control, and ordinary-output gate;
7. kill the seam if family differences disappear after local-error matching, amplification is below 3×, effect deviations are dominated by tiny source denominators, or fewer than three untouched checkpoints replicate.

This D1C is exploratory. It is justified because it can distinguish a genuine interface-level causal sensitivity from an expected first-order consequence of a 1% local mismatch. It is not authorization for D2.

## 8. Claim ceiling, ethics, and authorship

All evidence is computational and uses a public model. It does not test consciousness, biological replacement, fly experience, identity, or subject preservation. Checkpoint hashes and deterministic agreement are integrity checks, not independent evidence. Thomas Ryan remains the sole human author and accountable operator; AI assistance is not authorship.

## 9. Integrity artifacts

| Artifact | SHA-256 |
|---|---|
| source ensemble/margins | `bf75b64246b03d74a0e2a4d4c95d5814acc1b890d07914ab943498973647d8b4` |
| local calibration | `e6cc59d71a575a506887f98049d7bf7c54edb11f40be079a90078269fb68c5b2` |
| checkpoint-008 global | `3fb0c10d5b87ecad9611b8dacb391a0c6e329b2b06ff215b3fcb2371c3b275ea` |
| checkpoint-009 global | `e0eacb7d4ba5bd62ba46bcabbf973632b48e1abd8d2cb300f9f047277b1f66ac` |
| checkpoint-008 causal `.02` | `c82943c693812a9caa7381bf95a014100c5bf72e3d6ffbd4bb927d91057c5e15` |
| checkpoint-008 causal `.01` | `a432f2301aef88265b41882b8f0eb77df36ecdc407c051bd1f4786f65a8cb1bd` |
| checkpoint-009 causal `.02` | `f8d3b13077b2267848dd3f662f9b5f57435101027a825951407162e6e7159bfe` |
| checkpoint-009 causal `.01` | `6fa0ff3a30cdbe0971987c83d80f314d8bd46e92ee4d812fcac3b40feb2baa12` |

These hashes establish artifact integrity only.
