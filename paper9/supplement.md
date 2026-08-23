# Supplementary Information

## S1. Scope and evidential status

This package reports an exploratory, staged computational study. D0, D1A, D1B, and D1C were separated by written designs, but no D2 confirmatory experiment was opened. All checkpoint, direction, block, fraction, and solver observations are nested within public pretrained-model artifacts whose complete randomization provenance is unavailable. The supplement therefore reports descriptive gates, not population-level hypothesis tests.

## S2. Evidence classification

| Statement | Class | Support | Ceiling |
|---|---|---|---|
| The pinned source contains 45,669 neurons, 1,513,231 edges, 64 types, 721 columns, and 734 fitted parameters | Fact | Source paper and inspected model | Fact about this artifact |
| Exact shams were zero and topology digests unchanged | Fact | Frozen result JSONs | Execution-path validation only |
| No G2 occurred among 45 eligible ladder cells | Fact | Complete fixed grid on checkpoints 008–009 | Descriptive grid result; cells not independent |
| Eligible substitutions define an ordinary-response robustness region | Inference | Local pass plus ordinary/decoder G1 grid | Bounded to model, candidates, stimuli, checkpoints, margins |
| Mi1 timescale substitution altered causal gain | Inference | Cross-checkpoint/solver decoder-effect NRMSE; cosine ~1 | Exploratory, fixed-interface, no matched-error confirmation |
| Local equivalence generally composes | Speculation | Not identified | Prohibited claim |
| Connectomes are biologically sufficient or insufficient | Speculation | Not tested | Prohibited claim |
| Consciousness or identity is preserved | Speculation | Not measured | Prohibited claim |

## S3. Source-grounded margins

| Quantity | Source q10 standardized difference | One quarter | Frozen margin |
|---|---:|---:|---:|
| Local block velocity | 30.805% | 7.701% | 1.000% |
| Central block response | 19.488% | 4.872% | 1.000% |
| Frozen decoder output | 72.354% | 18.089% | 1.000% |

The source ensemble contextualized but did not loosen the authored 1% ceiling. Checkpoint differences reflect model-artifact variation and are not biological repeatability.

## S4. Local calibration

| Family | Added capacity | Mi1 | T4a | T5a | Decision |
|---|---|---:|---:|---:|---|
| Timescale (`alpha=.01`) | no state; one shared coefficient | .908% | .716% | .956% | eligible all blocks |
| Two-state (`beta=.25`, `tau=.1`) | one scalar state/node; two shared coefficients | .985% | .613% | 1.864% | T5a killed |
| Shunt (`gamma=.01`) | no state; one shared coefficient | .169% | .035% | .522% | eligible all blocks |
| Wrong shunt (`gamma=1`) | same form | failed | failed | failed | negative control separated |

Values are aggregate derivative NRMSE. The actual gate also required both intensities and p99 ratios to pass.

## S5. Global breadth accounting

| Checkpoint | G0 | G1 | G2 | Largest eligible full-block response | Largest eligible full decoder |
|---|---:|---:|---:|---:|---:|
| 008 | 2 | 21 | 0 | .235% | .441% |
| 009 | 1 | 24 | 0 | .305% | .403% |

G0 cells were retained as local failures and excluded from preservation/failure interpretation. Full ladder data are in `tables/table_global_ladder.csv`.

## S6. Causal seam and solver veto

| Checkpoint | `dt` | Ordinary NRMSE | Network-effect NRMSE | Mi1 block-effect NRMSE | Decoder-effect NRMSE | Effect cosine |
|---|---:|---:|---:|---:|---:|---:|
| 008 | .02 | .0275% | 1.484% | 1.753% | 2.331% | ~1.000 |
| 008 | .01 | .0127% | .932% | .837% | 2.754% | ~1.000 |
| 009 | .02 | .0275% | 1.326% | 1.185% | 1.897% | ~1.000 |
| 009 | .01 | .0127% | 1.020% | .809% | 2.025% | ~1.000 |

T4a timescale and two-state causal flags vanished at the smaller step. T5a timescale did not replicate across checkpoints. Only Mi1 × timescale remained cross-checkpoint and solver-robust, and only the decoder effect exceeded 1% in every cell.

## S7. D1C matched-error stopping result

The matching target was timescale aggregate local NRMSE .909%. An admissible shunt required a complete local pass and an error ratio in [.8, 1.25].

| `gamma` | Shunt NRMSE | Ratio | Complete pass | Outcome |
|---:|---:|---:|---|---|
| .010 | .152% | .167 | yes | unmatched |
| .025 | .380% | .418 | yes | unmatched |
| .050 | .761% | .836 | no | intensity-1 NRMSE 1.027% |
| .075 | 1.141% | 1.255 | no | local failure |
| .100 | 1.521% | 1.673 | no | local failure |

No post-outcome interpolation was permitted. The failed matching gate ended the generation, leaving checkpoints 013–014 untouched.

## S8. Deviations and error log

1. An early checkpoint-001 timescale candidate (`alpha=.02`) failed local transport after passing the preceding checkpoint and was killed; the margin was not relaxed.
2. An initial causal intervention hook had incorrect timing. The exact sham exposed the defect. The hook was corrected before accepting results, and the final exact errors were zero.
3. Several initial `dt=.02` causal flags were killed by the `dt=.01` solver veto.
4. D1C had an apparent near-match at `gamma=.05`, but it failed the complete local gate. No interpolated rescue candidate was added.
5. No D2 confirmatory stage was opened.

## S9. Statistical audit

- Independent unit intended: independently trained checkpoint.
- Actual limitation: public checkpoint metadata do not establish complete independent seed/randomization provenance.
- Nested observations: nodes, columns, frames, directions, intensities, replacement fractions, dynamics families, causal cells, and solver steps.
- Inferential p-values: none.
- Multiplicity correction: not applicable because no inferential family is claimed; the full frozen grid is reported.
- Missingness/exclusion: G0 cells were not dropped but classified as locally uninterpretable; crashes/nonfinite states would have counted as failures.
- Null interpretation: zero G2 in a fixed exploratory grid, not a universal null or frequency estimate.
- Hashes/tests: integrity and path-validation evidence only.

## S10. Ethics and authorship

No living animals or human participants were used. The model is not a fly individual. Thomas Ryan is the sole human author and accountable operator. AI assistance is disclosed in the manuscript and does not constitute authorship or independent replication.

