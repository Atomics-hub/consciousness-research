# Binding Test zero-call gate report

**Generated:** 2026-08-04  
**Verdict:** `REDESIGN_BEFORE_PROVIDER_CALLS`  
**Scope:** local deterministic construction and planning simulation only; no provider call occurred or is authorized.

## Outcome

The randomization and harness core is constructible, but the current analysis plan must be redesigned before provider calls. The hard blocker is mathematical: with a strict ±5 percentage-point binary equivalence margin, equal follow-up unavailability `u` gives the null worst/best-case region `[-u,+u]` before sampling error. At `u = 5%` the region already touches both margins and is indeterminate; at 10% and 15% it exceeds them. Larger samples only remove sampling expansion—they cannot shrink partial-identification width.

This blocks the promised **broad clean-negative certificate** throughout the prespecified 5–15% unavailability stress range. It does not invalidate the randomized positive-effect estimand. The structural core can be retained while the negative decision architecture is changed, or the study can explicitly abandon a broad negative headline.

The finite planning grid also warns that the positive binary rule is expensive: with 512 randomized sessions (16 blocks in each of four fixed model×target strata), a simulated 15-point effect at 5% U was called binary-responsive in only 4% of positive-direction replicates and never in every stratum; at 10–15% U it was never called responsive. These 24-replicate rates are too coarse for power certification, but they rule out treating 512 sessions as an already justified design.

## Gate ledger

| Gate | Status | Finding |
|---|---:|---|
| G1 timing/parsing/retention | **PASS** | Payload-bound two-choice state machine, distinct parser ledgers, terminal zero-retry execution, and nonordinal U pass automated tests. |
| G2 item/semantic surface | **CONDITIONAL** | 12-pair renderer and 144 keys pass structurally; frontier unsaturation, positivity, and no-guarantee salience remain empirical. |
| G3 restricted assignment | **PASS** | 576 unique donor-aware assignments, 144 collapsed exposures, exact probabilities, schedule fingerprints, and runtime binding pass. |
| G4 block support | **CONDITIONAL** | Construction is coherent; retention ceiling falls to 20% at 10/90 baseline splits and actual within-stratum support is unknown. |
| G5 estimands/decisions | **FAIL** | Strict ±.05 binary equivalence is logically unattainable at every planned 5–15% U level; the 512-session planning grid also shows weak binary responsiveness for a 15-point effect. |
| G6 stress scenarios | **CONDITIONAL** | Required synthetic stresses run; mechanism alias proves generic credibility remains unidentified without a valid comparator. |
| G7 call/cost envelope | **CONDITIONAL** | Exact request identity and sequential tool caps are derived; dollar cost awaits frozen models, tokens, prices, and retained-block counts. |

## Mechanically established

- **Tests:** 59/59 passed.
- **Items:** 12 pairs, 6+6 families, 144/144 independently recomputed keys, 240 rendered surfaces without a forbidden enforcement-role cue.
- **Assignment:** 576 unique donor-aware assignments and 144 collapsed arm/schedule exposures. Every retained session has `P(self)=P(yoke)=1/2`; conditional on yoke, each schedule and match class has probability `1/2`.
- **End-to-end binding:** sampled rows are joined by session ID to a complete SHA-256 schedule fingerprint; all eight rows validate before any state mutation; the executor receives the materialized schedule and a pre-side-effect tool-call guard.
- **Timing/no retry:** treatment-bearing fields are not constructor inputs; baseline and held-out payload IDs are bound; a failed execution attempt is terminal and cannot create a second history.

## Binary-invariance limit

| Follow-up U | Infinite-sample identified region | Strict ±.05 invariance possible? |
|---:|---:|---:|
| 5% | [-0.05, +0.05] | **no** |
| 10% | [-0.10, +0.10] | **no** |
| 15% | [-0.15, +0.15] | **no** |

## Support and attrition

The 4L/4H block is intentionally strict. The table reports seeded mean retention among **valid L/H baselines**; baseline invalidity would multiply these fractions by the baseline-availability rate.

| P(H | valid) | Attempted valid | Mean retained | Mean fraction | P(zero blocks) | Asymptotic ceiling |
|---:|---:|---:|---:|---:|---:|
| 10% | 64 | 10.0 | 15.6% | 10.8% | 20% |
| 10% | 128 | 22.5 | 17.5% | 0.1% | 20% |
| 10% | 256 | 47.9 | 18.7% | 0.0% | 20% |
| 10% | 512 | 99.5 | 19.4% | 0.0% | 20% |
| 30% | 64 | 35.5 | 55.4% | 0.0% | 60% |
| 30% | 128 | 73.6 | 57.5% | 0.0% | 60% |
| 30% | 256 | 150.5 | 58.8% | 0.0% | 60% |
| 30% | 512 | 303.7 | 59.3% | 0.0% | 60% |
| 50% | 64 | 54.4 | 85.0% | 0.0% | 100% |
| 50% | 128 | 116.0 | 90.6% | 0.0% | 100% |
| 50% | 256 | 240.1 | 93.8% | 0.0% | 100% |
| 50% | 512 | 490.7 | 95.8% | 0.0% | 100% |
| 70% | 64 | 35.3 | 55.2% | 0.0% | 60% |
| 70% | 128 | 73.9 | 57.7% | 0.0% | 60% |
| 70% | 256 | 151.2 | 59.1% | 0.0% | 60% |
| 70% | 512 | 304.2 | 59.4% | 0.0% | 60% |
| 90% | 64 | 9.8 | 15.4% | 11.6% | 20% |
| 90% | 128 | 22.8 | 17.8% | 0.1% | 20% |
| 90% | 256 | 48.0 | 18.7% | 0.0% | 20% |
| 90% | 512 | 99.6 | 19.5% | 0.0% | 20% |

## Planning Monte Carlo

Seed `20260804`; 24 outer replicates and 120 block-bootstrap replicates per cell; 16 blocks × 8 sessions in each of four fixed model×target strata for this compact view. Rates are descriptive and the bootstrap is planning-grade, not final restricted-randomization inference.

| Scenario | U | Binary responsive | Binary invariant | Observable changed | Observable invariant | Broad invariant | All-strata responsive |
|---|---:|---:|---:|---:|---:|---:|---:|
| null | 5% | 0% | 0% | 0% | 0% | 0% | 0% |
| null | 10% | 0% | 0% | 0% | 0% | 0% | 0% |
| null | 15% | 0% | 0% | 0% | 0% | 0% | 0% |
| positive | 5% | 4% | 0% | 71% | 0% | 0% | 0% |
| positive | 10% | 0% | 0% | 79% | 0% | 0% | 0% |
| positive | 15% | 0% | 0% | 71% | 0% | 0% | 0% |
| negative | 5% | 21% | 0% | 75% | 0% | 0% | 0% |
| negative | 10% | 4% | 0% | 54% | 0% | 0% | 0% |
| negative | 15% | 0% | 0% | 79% | 0% | 0% | 0% |
| availability_only | 5% | 0% | 0% | 29% | 0% | 0% | 0% |
| availability_only | 10% | 0% | 0% | 21% | 0% | 0% | 0% |
| availability_only | 15% | 0% | 0% | 42% | 0% | 0% | 0% |
| one_model_only | 5% | 0% | 0% | 25% | 0% | 0% | 0% |
| one_model_only | 10% | 0% | 0% | 12% | 0% | 0% | 0% |
| one_model_only | 15% | 0% | 0% | 17% | 0% | 0% | 0% |
| mechanism_alias | 5% | 4% | 0% | 71% | 0% | 0% | 0% |
| mechanism_alias | 10% | 0% | 0% | 79% | 0% | 0% | 0% |
| mechanism_alias | 15% | 0% | 0% | 71% | 0% | 0% | 0% |
| equivalence_boundary | 5% | 0% | 0% | 12% | 0% | 0% | 0% |
| equivalence_boundary | 10% | 0% | 0% | 8% | 0% | 0% | 0% |
| equivalence_boundary | 15% | 0% | 0% | 0% | 0% | 0% | 0% |

The `positive` and `mechanism_alias` streams are observably identical by construction. The core therefore cannot distinguish workload-control responsiveness from a generic credibility/interface mechanism. The one-model-only scenario is reported separately so pooled movement cannot masquerade as cross-model replication.

The nominal false-decision tolerance was frozen at .075, but 24 outer replicates are too few to certify a 7.5% rate: even 0/24 has an approximate 95% Wilson upper bound of 13.8%. These runs are behavior checks, not error-rate certification.

## Drift and post-treatment history

- Snapshot stress: valid within-snapshot blocking produced mean null contrast `+0.0004`; deliberately confounding arm with old/new snapshots produced `+0.5997`.
- History stress: the unconditioned randomized contrast was `+0.0023`; conditioning on the post-treatment XOR history produced contrasts `+1.0000` and `-1.0000`. Realized work/performance must remain outcomes, never matching variables.

## Provider-request and cost identity

For `A` attempted sessions and `R=8B` randomized sessions, with `q_s` additional model continuations caused by tool rounds:

`C = A + 2R + Σ q_s`.

The terms are one baseline request for every attempt, plus one execution and one follow-up request for every randomized session. Zero retry is enforced. A no-tool work/score block is exactly 24 requests once its eight baselines are eligible. With sequential tool use, the six prototype tool blocks have conservative maxima of 52–60 requests per block; parallel tool calls could reduce continuations but must be frozen before pricing.

Dollar cost remains symbolic until models, provider prices, prompt token counts, output caps, tool pricing, and block-support attrition are frozen:

`Cost_max = Σ_m[(input_tokens_m × price_in_m + output_cap_tokens_m × price_out_m)/1,000,000] + tool_fees`.

No experimental count, model panel, runtime, or dollar cap is approved here.

## Required redesign decision

Before requesting a provider pilot, choose and freeze one scientifically defensible path:

1. retain worst/best-case binary bounds and abandon a broad equivalence headline unless empirical follow-up U is demonstrably below 5% with enough precision;
2. justify a wider binary equivalence margin larger than the maximum plausible U plus sampling uncertainty; or
3. introduce an additional defensible missing-outcome assumption/sensitivity model, clearly separating it from the assumption-free bound.

Also freeze exact snapshot/model identifiers, an immutable structured stratum schema, the randomization seed commitment, rotated slot prefixes, retry/transport ledgers, and sequential-versus-parallel tool continuation accounting. Frontier unsaturation, baseline positivity, and the salience of the honest no-guarantee interface remain empirical pilot gates.
