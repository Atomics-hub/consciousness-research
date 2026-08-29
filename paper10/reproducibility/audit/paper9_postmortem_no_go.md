# Paper 10 E0-A Reconstruction Decision

**Author and accountable operator:** Thomas Ryan  
**AI role:** research assistance only; not an author  
**Decision date:** 27 August 2026  
**Decision:** NO-GO for the Causal Compression Frontier in its current formulation

## Outcome

The public Creamer raw-text package does not reproduce the saved historical empirical stimulus-triggered-average matrices within the tolerances frozen before aggregate comparison. This activates the E0-A kill rule. No model ladder, target-grouped development analysis, or confirmatory packet is opened.

This is not a judgment that the Creamer or Randi biological findings are false. It is a narrower reproducibility finding: the inspected public text export, public preprocessing code, reconstructed historical loader order, and saved 2024 aggregate artifacts do not form a sufficiently equivalent end-to-end analysis chain for Paper 10 to attribute later model differences to biological-description content rather than pipeline drift.

## Frozen test

The reconstruction used all 110 public recording directories and the preprocessing/STAM equations in the public Creamer lineage. Tolerances were frozen before the full comparison in [`reconstruction_tolerances.json`](../work/g0a_causal_compression_audit/reconstruction_tolerances.json):

- exact `156 × 156` dimensions and exact cell-identity sequence;
- at least 0.99 finite-mask agreement in each split;
- at least 0.98 Pearson agreement with each saved matrix;
- at most 0.05 normalized RMSE in each split;
- at most 0.02 absolute deviation in train–test correlation; and
- at most 0.03 absolute deviation from the saved connectome-relative score.

All gates were conjunctive. They were intentionally set to require near-reproduction, not qualitative resemblance.

## Version archaeology

The saved paper artifacts entered the public repository on 3 October 2024 at commit `3d4dc2e6a7794205ace85cde5e0fc8f7f45ec922`. The first inspected public refit code, commit `45d9e111f23525444b0f2e8077661ba6199b8696` from 16 January 2025, reverse-sorted recording paths and assigned the first 80 animals to training and the final 30 to test. Commit `494c5c516d0cb589e6b5cee4aa932b970f842722` changed that loader to ascending order on 21 January 2025.

Using the later ascending order produced only 135 aggregate neuron identities and failed the expected shape immediately. Restoring the pre-change reverse ordering restored the `156 × 156` shape. The relevant numeric preprocessing and empirical-STAM source regions are identical between the inspected January and June 2025 trees, so the order change—not an equation change—explains that first discrepancy.

Even with the restored split, the identities were not exact. The reconstructed aggregates contained `IL2R` and `RMFL`, whereas the saved model/artifacts contained `RID` and `RIS`. There were 154 common identities. Direct positional matrix comparison would therefore be invalid after the first shifted identity; the final audit reindexed both axes by neuron identity and masked the diagonal, matching the quick-start scoring convention.

## Decisive results

| Frozen gate | Required | Reconstructed result | Outcome |
|---|---:|---:|---|
| Matrix shape | `156 × 156` in both splits | `156 × 156` | Pass |
| Cell-identity sequence | Exact | 154 common; two rebuilt-only and two saved-only | Fail |
| Train finite-mask agreement | ≥ 0.99 | 0.993928 | Pass |
| Test finite-mask agreement | ≥ 0.99 | 0.840530 | Fail |
| Train Pearson agreement | ≥ 0.98 | 0.902761 | Fail |
| Test Pearson agreement | ≥ 0.98 | 0.530543 | Fail |
| Train NRMSE | ≤ 0.05 | 0.429116 | Fail |
| Test NRMSE | ≤ 0.05 | 1.056644 | Fail |
| Train–test correlation deviation | ≤ 0.02 | `|0.186889 − 0.160906| = 0.025983` | Fail |
| Connectome-relative-score deviation | ≤ 0.03 | `|0.960643 − 0.919493| = 0.041150` | Fail |

The saved artifacts restricted to the same 154 identities retain a connectome-relative score of `0.918740`, close to the frozen full-artifact reference of `0.919493`. That makes an indexing mistake an implausible explanation for the final failure. The strongest disagreement is in the held-out 30-animal test matrix, where both missingness structure and values differ substantially.

The machine-readable result is [`historical_aggregate_reconstruction.json`](../work/g0a_causal_compression_audit/historical_aggregate_reconstruction.json). The first ascending-order failure and the superseded unaligned diagnostic are retained rather than overwritten.

## Numerical-hygiene audit

Conversion completed for all 110 recordings, with processed shapes spanning 272–5,727 frames and 80–281 recorded columns. Seventy-nine recordings emitted at least one warning. The captured totals include 80,535 exponential overflows, 47,999 divide-by-zero warnings, 47,998 invalid divisions, 30,351 invalid multiplications, and 140 squared-value overflows. Thirteen distinct photobleach-correction warnings caused one or more neuron traces to be set to missing.

Many warnings arise inside an optimizer and do not by themselves prove corrupt output. They do show that environment- or optimizer-dependent fallback behavior is a plausible source of drift and must not be silently treated as biologically meaningful. The complete per-recording record is in [`conversion_manifest.json`](../work/g0a_causal_compression_audit/imported/conversion_manifest.json).

## Interpretation and claim ceiling

Established fact: this reconstructed public end-to-end path fails the prospectively frozen reproduction gate.

Supported inference: the current public lineage is not a trustworthy foundation for comparing model-ladder rungs at the effect sizes Paper 10 would need to interpret. Preprocessing, export, labeling, optimizer behavior, or an undocumented historical step could each contribute.

Not established: which component caused the mismatch; that the underlying recordings or published biological conclusions are wrong; that another unpublished or differently versioned pipeline could not reproduce the artifacts; or any claim about consciousness in *C. elegans*.

## Binding decision and null value

The Causal Compression Frontier is killed as the Paper 10 flagship under the frozen E0-A rule. Tolerances will not be loosened, identities will not be silently intersected for the main analysis, and the saved aggregates will not be substituted for raw-derived outcomes to keep the program alive.

The null retains publication value as a compact reproducibility/data-lineage methods result if Thomas later chooses to develop it, but it does not meet the field-shifting Paper 10 bar by itself.

## Portfolio consequence

No Paper 10 thesis is selected at this point. Predictive Amplification already failed the standalone novelty gate, and CCF now fails the raw-to-aggregate reproducibility gate. The next highest-causal-leverage reserve is **State-Transport Equivalence in Fly Vision**, but it remains a G0 candidate rather than a selected direction. It must first survive a hostile prior-art and mechanism audit showing that the proposed state intervention is biologically grounded and that the question does not collapse to a generic parameter-sensitivity result. Open-loop versus closed-loop equivalence and consciousness-metric invariance remain secondary reserves.

No confirmatory outcomes were exposed, no external system was mutated, nobody was contacted, and no money was spent.
