# Paper 9 Phase 6 — D1C frozen causal-amplification gate

**Frozen:** 2026-08-22, before inspecting checkpoints 010–014  
**Status:** targeted exploratory falsification; D2 remains **NO-GO**

## 1. Target and alternative explanation

D1B found one cross-checkpoint, solver-robust G3 seam: full Mi1 replacement by the `alpha=0.01` state-dependent-timescale family preserved ordinary responses but changed fixed-decoder impulse-effect magnitude. D1C asks whether that deviation is specific causal amplification or merely the expected consequence of comparing candidates with unequal local derivative error.

The seam is killed if a locally error-matched shunt behaves similarly, if amplification is small, if the result depends on one impulse amplitude/time, if source effects are denominator-small, or if it fails untouched checkpoints.

## 2. Checkpoint firewall

| Checkpoint | Role |
|---|---|
| 010–011 | source-only canonical effect scale/variability |
| 012 | third source-only member, then Mi1 local-error matching calibration |
| 013 | untouched multiamplitude/multitime holdout |
| 014 | untouched replication and `dt=.01` solver veto |

No checkpoint may change roles after outcomes.

## 3. Frozen systems and matching

- Target family: timescale, `alpha=0.01`, center unchanged from D1A.
- Matched control: Mi1 shunt with `theta=0`, `scale=1`, `E_rev=1`; select the gamma from `0.01, 0.025, 0.05, 0.075, 0.1` whose checkpoint-012 aggregate local derivative NRMSE is closest to timescale while both NRMSE and p99 ratio pass 1%.
- Matching gate: shunt/timescale local-NRMSE ratio must lie in `[0.8, 1.25]`. Otherwise D1C is blocked rather than comparing unmatched candidates.
- Exact sham: timescale route with `alpha=0`.
- Wrong control: shunt `gamma=1`.
- Full Mi1 replacement only. No block search.

Both informative candidates have no extra state, one calibrated/frozen shared coefficient, no per-node parameters, no checkpoint identity, and no source lookup.

## 4. Ordinary and local eligibility

Use the frozen 24-trajectory twelve-direction motion battery from D1B. On checkpoints 013 and 014, each candidate must independently pass 1% aggregate and intensity-stratified local NRMSE and p99 gates, 1% Mi1 ordinary-response NRMSE, and 1% fixed-decoder ordinary-output NRMSE. Failure is G0/G2 and ends causal interpretation for that checkpoint.

## 5. Causal battery

Use the four D1B angle/intensity trajectories `(0,0)`, `(90,1)`, `(180,0)`, `(270,1)`. Cross:

- impulse amplitudes: `0.0025, 0.005, 0.01, 0.02`;
- impulse times: `0.3, 0.5, 0.7 s` after simulated sequence start;
- integration step: primary `.02`; solver veto `.01` on checkpoint 014 with physical times preserved.

This yields 12 intervention cells per system/checkpoint, each containing all four stimulus trajectories. Compute within-system perturbed-minus-base neural and frozen-decoder effects.

For each cell report:

- neural and decoder effect NRMSE and cosine;
- Mi1 effect NRMSE;
- signed decoder gain `dot(candidate_effect, source_effect) / dot(source_effect, source_effect)`;
- decoder absolute error RMS;
- source decoder-effect RMS;
- causal amplification ratio `decoder-effect NRMSE / local derivative NRMSE`.

Exact sham must be zero. Cells with source decoder-effect RMS below the 10th percentile of canonical source-only effect RMS from checkpoints 010–012 are denominator-weak and cannot satisfy the primary success rule.

## 6. Frozen success and kill rules

For each untouched checkpoint, a timescale intervention cell is a **strong amplification cell** only if:

1. it is not denominator-weak;
2. decoder-effect NRMSE is at least 2%;
3. causal amplification is at least 3×;
4. decoder effect cosine is at least 0.99 (isolating gain rather than direction change);
5. its amplification is at least 1.5× the matched shunt's amplification in the same cell.

D1C passes only if at least 9 of 12 cells are strong on checkpoint 013, at least 9 of 12 are strong on checkpoint 014 at `dt=.02`, and at least 9 of 12 remain strong on checkpoint 014 at `dt=.01`. All exact shams must be zero, both candidates must remain locally/ordinarily eligible, and the wrong control must fail locally or produce larger causal deviations.

Kill the seam if matching fails; either informative candidate fails local/ordinary eligibility; fewer than 9 cells pass on any required run; the source denominator floor removes more than 3 cells; the shunt matches the timescale effect after local-error matching; the result reverses at `.01`; or the only distinction is crossing the inherited 1% margin without the 2% and 3× safeguards.

## 7. Decision ceiling

A D1C pass would justify designing—not running—a confirmatory D2 focused on interface-level causal gain under locally matched dynamics. It would not establish general composition failure, biological causal replacement, consciousness, identity, or subject preservation. A D1C failure kills the Mi1 seam and leaves D1B as an ordinary-response robustness/methods null.

No release, publication, external contact, paid service, or external mutation is authorized. Thomas Ryan remains the sole human author and accountable operator; AI assistance is not authorship.
