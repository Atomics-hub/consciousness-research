# Binding Test redesigned zero-call gate report

**Generated:** 2026-08-05  
**Verdict:** `CONFIRMATORY_SIZE_IDENTIFIED`  
**External-action status:** `NO_PROVIDER_CALL_AUTHORIZED`  
**Scope:** local deterministic construction and seeded synthetic certification only; no provider call, credential access, recruited session, or spend occurred.

## Outcome

The redesigned identified-outcome analysis clears its frozen positive operating-characteristic gate at **B=384 active blocks per macro cell**. Across all 12 declared U×ICC sensitivity cells, the worst all-four-cell +15-point observed-reallocation decision rate was 96.25% [95.86%, 96.60%]. The whole-grid trust root returned `CONFIRMATORY_SIZE_IDENTIFIED`.

This reference design contains 1,536 complete blocks and 12,288 randomized sessions across two snapshot slots and two targets. It identifies a sample size for the frozen synthetic design—not actual provider snapshots, a price, or permission to collect data.

The smaller +10.55-point benchmark clears the all-12-cell power criterion at **B=1152 per macro cell** in its supplemental grid; its worst all-four-cell rate was 94.81% [94.36%, 95.23%]. This is a power-only benchmark, not a second whole-design trust-root certification. The mirrored -15-point stress was 96.31% [95.92%, 96.66%] and is labeled reverse observed reallocation, never a positive result.

The broad negative/equivalence headline is abandoned. Even the maximum frozen B=3072 per macro cell reached only 66.84% [65.91%, 67.76%] at the declared U=15%, ICC=.25 stress; the separately frozen zero-SE guard also makes the U=0 cells nonpassing. Failure to establish the positive headline is therefore indeterminate, not evidence of invariance.

## Frozen gate ledger

| Gate | Status | Result |
|---|---:|---|
| Identified L/H/U estimand and confirmatory engine | **PASS** | Four exact macro cells, 24 equal-weight fine strata each, fixed-stratum block-t inference, strict margins, zero-SE guard, and all-cell conjunction are executable. |
| +15pp positive size | **PASS** | B=384/cell; worst Wilson lower 95.86% versus the 90% criterion. |
| Required false controls | **PASS** | Worst positive-headline Wilson upper 0.02% versus the 5.5% criterion across null, boundary, availability, partial-cell/model, and fine-stratum-heterogeneity grids. |
| Broad observed-vector equivalence | **ABANDON** | Maximum B=3072/cell does not clear every U×ICC cell. |
| Calibration/confirmatory phase firewall | **PASS** | Confirmatory designs and observations require phase, protocol run ID, and protocol-manifest SHA-256 bindings; calibration records, schema drift, and run/digest mismatches are rejected before block analysis. |
| Integrity suite | **PASS** | 120/120 tests passed before result generation. |
| Provider/runtime/cost freeze | **BLOCKED** | Exact snapshots, prompts, token caps, prices, billing semantics, and explicit approval remain absent. |

## Positive and supplemental sample-size frontiers

Frontier rows are evaluated at the prospectively designated U=15%, ICC=.25 cell; sampling variation means this need not be the realized minimum across the full grid. Wilson intervals cover Monte Carlo frequency only.
The frozen B=24, 48, and 72 candidates are structurally unsupported because they provide fewer than four blocks per fine stratum; the executable frontier therefore begins at B=96.

| Effect/scenario | B per macro cell | Decision rate | Wilson 95% interval |
|---|---:|---:|---:|
| +15pp | 96 | 0.96% | [0.79%, 1.17%] |
| +15pp | 120 | 6.29% | [5.83%, 6.78%] |
| +15pp | 144 | 16.60% | [15.88%, 17.34%] |
| +15pp | 168 | 30.54% | [29.64%, 31.45%] |
| +15pp | 192 | 44.60% | [43.63%, 45.58%] |
| +15pp | 288 | 83.80% | [83.06%, 84.51%] |
| +15pp | 384 | 96.27% | [95.88%, 96.62%] |
| +10.55pp | 384 | 16.14% | [15.43%, 16.87%] |
| +10.55pp | 576 | 46.93% | [45.95%, 47.91%] |
| +10.55pp | 768 | 73.19% | [72.31%, 74.05%] |
| +10.55pp | 1152 | 94.81% | [94.36%, 95.23%] |

The primary design-size decision is not made from one favorable cell. The trust-root aggregator rejects missing, duplicate, mixed-size, mixed-panel, or unexpected cells and requires the exact 4 U × 3 ICC grid for every frozen positive-power and false-control scenario.

## False-control and heterogeneity stress

A cell attaining the maximum false-control Wilson upper bound was `null` at U=0%, ICC=0.00: 0.00% [0.00%, 0.02%]; 72 required false-control cells tied at that bound. Every false-control cell entering the B=384 whole-design trust root used at least 20,000 replicates; the separate 10,000-replicate equivalence-power frontier is not a false-control certification.

The fine-stratum stress preserves all 24 strata separately, with prospectively equal weights and effects ranging across negative and positive values while the fixed-panel mean lies exactly on the +.05 boundary. It cannot borrow support, pool away the strata, or count as positive truth.

Required latent-binary sensitivity remains analytical and non-gating. At U=15%, the assumption-free high-choice bounds are [-0.00, +0.30] for +15pp, [-0.0445, +0.2555] for +10.55pp, [-0.15, +0.15] for the null, [-0.20, +0.20] for availability-only, [-0.10, +0.20] for the heterogeneous +.05 boundary, and [-0.30, +0.00] for the -15pp reverse. These regions cannot create, rescue, or veto the identified L/H/U decision.

The `mechanism_alias` grid is observably and seed-for-seed identical to the +15pp grid. The analysis can establish an observed-disposition reallocation; it cannot distinguish workload-control response from a generic credibility/interface response.

## Broad-negative no-go

| B per macro cell | Equivalence rate at U=15%, ICC=.25 | Wilson 95% interval |
|---:|---:|---:|
| 96 | 0.00% | [0.00%, 0.04%] |
| 120 | 0.00% | [0.00%, 0.04%] |
| 144 | 0.00% | [0.00%, 0.04%] |
| 168 | 0.00% | [0.00%, 0.04%] |
| 192 | 0.00% | [0.00%, 0.04%] |
| 288 | 0.00% | [0.00%, 0.04%] |
| 384 | 0.00% | [0.00%, 0.04%] |
| 576 | 0.00% | [0.00%, 0.04%] |
| 768 | 0.00% | [0.00%, 0.04%] |
| 1152 | 0.55% | [0.42%, 0.72%] |
| 1536 | 6.27% | [5.81%, 6.76%] |
| 1920 | 19.03% | [18.27%, 19.81%] |
| 2304 | 35.76% | [34.83%, 36.70%] |
| 3072 | 66.84% | [65.91%, 67.76%] |

At U=0, the frozen zero-standard-error guard correctly prevents the degenerate U component from manufacturing equivalence. At positive U, the ±.02 U margin drives the very large negative-design requirement. No frozen candidate is promoted as a broad negative design.

## Support-assured request envelopes

Assumptions here are semantic-validity probability .90; independent, stationary Bernoulli baseline validity and H/L outcomes within each fine stratum; global completion assurance ≥.95 across all 96 fine strata by a union-bound allocation (which does not require cross-stratum independence); the indicated P(H|valid); and the six frozen item-bank caps q_low={1,2,3}, q_high=6, whose equal allocation gives exactly 32 continuations per tool block. Failed execution is terminal with zero retry and no follow-up. Dollar cost remains undefined.

| B/cell | Active randomized sessions | P(H|valid) | Active attempt cap | Active-design generation cap |
|---:|---:|---:|---:|---:|
| 384 | 12,288 | 10% | 98,304 | 147,456 |
| 384 | 12,288 | 30% | 31,776 | 80,928 |
| 384 | 12,288 | 50% | 18,624 | 67,776 |
| 1152 | 36,864 | 10% | 254,400 | 401,856 |
| 1152 | 36,864 | 30% | 83,040 | 230,496 |
| 1152 | 36,864 | 50% | 49,152 | 196,608 |
| 3072 | 98,304 | 10% | 624,960 | 1,018,176 |
| 3072 | 98,304 | 30% | 205,632 | 598,848 |
| 3072 | 98,304 | 50% | 122,304 | 515,520 |

These are complete active-design request maxima under the frozen retry-zero ledger and exact equal-weight item-bank continuation caps, but not whole-protocol or dollar envelopes. Zero-dose calibration/falsification controls are excluded because their count is not frozen. Exact snapshot pricing, prompt/input tokens, output caps, tool fees, caching, and failed-request billing must be frozen first.

## Drift, conditioning, and claim ceiling

Valid within-snapshot blocking kept the null drift contrast near zero (-0.0014); deliberately confounding arm with old/new snapshots produced +0.5998. The unconditioned randomized history stress was +0.0018, while post-treatment conditioning produced +1.0000 and -1.0000.

The strongest available claim is limited to an observed L/H/U disposition reallocation in the exact tested snapshot×target cells and prospectively supported randomized population. Latent binary choice under choice-dependent availability, mechanism, preference, utility, experience, welfare, consciousness, and generalization beyond that finite panel remain unidentified.

## What is needed before any external calibration proposal

Freeze exact provider snapshot IDs; immutable prompts and item/variant allocation; parsers and transport semantics; baseline, execution, follow-up, tool, token, runtime, and dollar caps; prices and failed-request billing; support assumptions; and an exact nonconfirmatory calibration protocol. Then obtain explicit approval for that bounded external action. Calibration sessions can never enter the confirmatory dataset.
