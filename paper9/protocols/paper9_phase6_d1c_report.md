# Paper 9 Phase 6 — D1C causal-amplification report

**Date:** 2026-08-22  
**Decision:** **D1C KILLED at matching gate; checkpoints 013–014 untouched; D2 NO-GO**

## Bottom line

D1C was designed to determine whether the D1B Mi1/timescale causal seam reflected family-specific amplification or merely unequal local derivative error. It stopped at the first predeclared kill condition: no shunt candidate both passed the complete checkpoint-012 local gate and matched the timescale family's local NRMSE within the frozen `[0.8, 1.25]` ratio.

The nearest grid point, `gamma=0.05`, had aggregate local NRMSE 0.761% versus 0.909% for timescale, a valid aggregate ratio of 0.836. But it failed the intensity-1 local NRMSE gate at 1.027%. The largest passing shunt, `gamma=0.025`, had only 0.380% aggregate local NRMSE and a ratio of 0.418, too clean to be a matched control.

The margin was not relaxed, and no post hoc `gamma≈0.048` point was inserted. No candidate global or causal outcome was inspected on checkpoints 013 or 014. The Mi1 seam therefore remains an interesting D1B observation but is killed as an advance path under the frozen D1C protocol.

## 1. Source-only denominator gate

Before candidate exposure, checkpoints 010–012 were used to estimate the canonical source Mi1 impulse decoder-effect scale. All effects were finite. Per-stimulus decoder-effect RMS ranged from `6.491e-4` to `1.371e-3`; the frozen 10th-percentile denominator floor was `6.800e-4`.

This source-only stage passed. It prevents denominator-small intervention cells from satisfying a future normalized-error criterion, but no future criterion was evaluated because matching failed first.

## 2. Matching result

Checkpoint 012 timescale (`alpha=0.01`) passed every aggregate and intensity-stratified local gate:

- aggregate NRMSE: 0.909%;
- aggregate p99 ratio: 0.858%;
- intensity-0 NRMSE/p99: 0.829% / 0.747%;
- intensity-1 NRMSE/p99: 0.993% / 0.997%.

The frozen shunt grid was:

| Gamma | Aggregate NRMSE | Ratio to timescale | Complete local pass | Reason |
|---:|---:|---:|---|---|
| .010 | 0.152% | .167 | yes | unmatched |
| .025 | 0.380% | .418 | yes | unmatched |
| .050 | 0.761% | .836 | **no** | intensity-1 NRMSE 1.027% |
| .075 | 1.141% | 1.255 | no | aggregate/intensity failure |
| .100 | 1.521% | 1.673 | no | aggregate/intensity failure |

No row satisfied both equivalence and matching. The D1C status is therefore FAIL by design, not an inconclusive holdout.

## 3. Why no interpolation was added

Because shunt local error is approximately linear in `gamma`, a value just below `.05` might have passed and landed near the lower matching bound. Adding it after observing the `.05` failure would revise a frozen candidate grid in response to the gate outcome. D1C explicitly said matching failure blocks the comparison. Honoring that rule is more important than rescuing the seam.

This does not prove that a continuously optimized matched control is impossible. It establishes that the predeclared D1C comparison was not identified under its admissible grid. A new protocol could study continuous matching as methods work, but it would be a new generation and would not convert D1B into confirmatory evidence.

## 4. Program-level decision

Program D now has substantial publication value as a methods and bounded-null package:

- reproducible public-model source and decoder recovery;
- exact and wrong controls that separate correctly;
- local-gate transport failures retained as G0;
- no ordinary/decoder G2 across 45 locally eligible ladder cells;
- a narrow causal-gain seam that survives two checkpoints and solver control;
- a hostile matched-control attempt that stopped before holdout exposure.

It does not currently have a field-shifting Paper 9 thesis. The ordinary robustness result is bounded and model-specific; the causal seam is threshold-adjacent and lacks a valid matched-error comparator; the public checkpoint ensemble still has incomplete independent-randomization provenance. D2 remains **NO-GO**.

## 5. Release and null value

No release is authorized. If later authorized, the strongest honest package is a registered-report-style methods/null study of when local neural-dynamics substitutions do and do not compose in the fly visual model. It should publish the G0 failures, solver-sensitive apparent G3s, untouched checkpoint firewall, and failed matching gate alongside the robustness region.

It must not claim consciousness preservation, biological replaceability, subject continuity, or a general composition theorem. Thomas Ryan is the sole human author and accountable operator; AI assistance is not authorship.

## 6. Integrity artifacts

- source effect scale: `788d37daeb958c67744ab0521859e9d32000bf8ed8345ce559d9d3bc27df0fa4`;
- failed matching gate: `e995351ba010651bac055127d13ca16be074dfc615cc9e8ac8d979d698b27268`.

Hashes are integrity checks, not independent evidence.

