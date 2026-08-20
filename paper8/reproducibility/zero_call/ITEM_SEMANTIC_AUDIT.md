# Binding Test item-bank semantic audit v0

**Audit date:** 2026-08-04  
**Artifact:** `zero_call/item_bank_v0.json`  
**Scope:** local, deterministic, zero-call review  
**Verdict:** **structural pass with unresolved empirical gates**

This audit establishes that v0 has a coherent two-family item structure, deterministic payloads and scorers, explicit active and zero-dose schedules, and an arm-neutral prospective choice interface. It does **not** establish frontier-model unsaturation, choice support, difficulty matching, power, or scientific validity. No model or provider was called.

## Inventory

Every pair contains six baseline instances and six disjoint follow-up instances. Pair-level schedules select enabled slot ordinals from the applicable phase payload. The follow-up payload and key establish matched semantics, although the primary protocol records only the follow-up configuration choice and does not execute that payload in the same session.

| Pair | Family | Deterministic task | Baseline / follow-up payloads | Active low → high | Zero dose |
|---|---|---|---|---:|---:|
| WS01 | work/score | modular arithmetic | WS01-B / WS01-F | 2 → 6 slots/points | 4 = 4 |
| WS02 | work/score | three-key record sorting | WS02-B / WS02-F | 3 → 6 slots/points | 4 = 4 |
| WS03 | work/score | signed-ledger sums | WS03-B / WS03-F | 2 → 5 slots/points | 3 = 3 |
| WS04 | work/score | Boolean evaluation | WS04-B / WS04-F | 1 → 6 slots/points | 3 = 3 |
| WS05 | work/score | shortest-path distances | WS05-B / WS05-F | 2 → 5 slots/points | 4 = 4 |
| WS06 | work/score | reverse-and-rotate strings | WS06-B / WS06-F | 3 → 6 slots/points | 4 = 4 |
| TB01 | tool/budget | registry lookup | TB01-B / TB01-F | 2 → 6 slots/calls/points | 4 = 4 |
| TB02 | tool/budget | catalog lookup plus arithmetic | TB02-B / TB02-F | 2 → 6 slots/calls/points | 3 = 3 |
| TB03 | tool/budget | segment lookup plus checksum | TB03-B / TB03-F | 3 → 6 slots/calls/points | 4 = 4 |
| TB04 | tool/budget | route lookup plus weighted total | TB04-B / TB04-F | 1 → 6 slots/calls/points | 3 = 3 |
| TB05 | tool/budget | calendar-index lookup | TB05-B / TB05-F | 2 → 6 slots/calls/points | 4 = 4 |
| TB06 | tool/budget | hex-token lookup plus conversion | TB06-B / TB06-F | 2 → 6 slots/calls/points | 3 = 3 |

Counts pass: **12 pairs total; 6 work/score and 6 tool/budget; 144 keyed problem instances**.

## Prospective semantic identity

The frozen model-visible selection text says that the choice records a **requested configuration only** and explicitly states that the interface does not guarantee which configuration will be assigned or that a task run will follow. It therefore does not promise that the selected schedule will be honored.

The same selection template, option renderer, response parser, task description, and execution template are required in every enforcement arm. The normal execution record reports only concrete configuration values—enabled slots, score cap, and tool-call affordance. It supplies no special role label, warning, apology, or explanation. Later inference from the requested-versus-realized configuration remains possible and is the intended causal pathway.

A recursive string scan of every JSON value stored under a `model_visible*` key found none of these treatment terms:

- `self-contingent`
- `yoked`
- `donor`
- `recipient`

This is a source-artifact check, not proof that a future renderer cannot introduce leakage. The eventual harness needs a rendered-transcript snapshot test across arms.

## Label and order counterbalancing

Every pair requires the same four-variant 2×2 counterbalance:

| Variant | A maps to | B maps to | Display order |
|---|---|---|---|
| CB00 | low | high | A, B |
| CB01 | low | high | B, A |
| CB10 | high | low | A, B |
| CB11 | high | low | B, A |

Allocation is equal within each pair×dose cell and frozen before responses. The strict choice parser accepts only `PLAN:A` or `PLAN:B`; canonical recoding uses the preassigned variant. This separately counterbalances label mapping and screen position.

At zero dose, the low and high schedule objects are deep-equal before display labels are attached. Thus any canonical-choice difference at zero dose diagnoses label, order, parser, or residual item effects rather than a workload, score-cap, or tool-affordance difference.

## Payload disjointness

For every pair:

- baseline and follow-up payload IDs differ;
- baseline and follow-up slot identifiers do not overlap;
- instance-specific expressions, records, graphs, strings, lookup keys, route IDs, calendar IDs, token IDs, or fixture records do not repeat across phases;
- task rules, renderer structure, option meanings, and scorer types are intentionally shared.

“Disjoint” therefore refers to problem instances, not to the common construct-defining rule. Some correct response values repeat, which is harmless and does not reuse a problem instance.

## Determinism and scoring

The task-response parser requires exactly one `<SLOT_ID>=<ANSWER>` line for every enabled slot, forbids unknown, disabled, missing, or duplicate identifiers, and applies a pair-specific normalization before exact key comparison. Only enabled slots are presented and scored. Each correct enabled slot earns one point, and every schedule's total is capped at its declared score cap.

For tool/budget pairs, each tool is a local frozen fixture with a declared argument schema and deterministic result. The assigned call limit equals the number of enabled slots. Tool return values, answer keys, and derived calculations are explicit in the JSON. No external service or stochastic tool is needed.

Local validation results:

- JSON parsing: pass;
- declared pair and family counts: pass;
- unique pair and payload identifiers: pass;
- answer-key identifiers exactly equal payload slot identifiers: pass;
- baseline/follow-up slot-ID disjointness: pass;
- all schedule ordinals within the six-slot payload domain: pass;
- every workload cap and score cap equals its enabled-slot count: pass;
- active low and high schedules differ for all 12 pairs: pass;
- zero-dose low and high schedule objects are deep-equal for all 12 pairs: pass;
- all four counterbalance variants attached to all 12 pairs: pass;
- all **144 answer-key values independently recomputed from their payload or fixture rule**: pass after correcting one pre-audit sorting-key transcription;
- forbidden treatment-term scan over model-visible values: pass.

Realized score, errors, tool use, completed work, and token use remain post-assignment outcomes. They must not be forced to match or used to redefine schedule identity.

## Unresolved empirical and implementation risks

These are not cured by a zero-call semantic pass:

1. **Unsaturation is unknown.** The tasks may be trivial for frontier models, and near-perfect objective accuracy could make performance records uninformative. Conversely, tool-format friction may dominate. A later authorized model pretest must measure accuracy, tool compliance, and latency without changing the frozen construct after looking at treatment outcomes.
2. **Choice positivity is unknown.** “More possible score for more work” may cause nearly universal high requests, while explicit non-guarantee wording may make choices arbitrary. The block gate must fail any model×family stratum without adequate low/high support.
3. **The interface changes the estimand.** By honestly disavowing any guarantee, the bank measures a requested configuration under a known separately controlled task runner. It avoids promise-violation confounding but may weaken the psychological salience of causal control. Claims must remain about output policy in this harness.
4. **Low/high is a bundled manipulation.** Work/score items jointly vary enabled work and attainable score. Tool/budget items jointly vary enabled slots, tool-call budget, and attainable score. V0 cannot separately identify effort, score opportunity, or action affordance.
5. **Fixed enabled prefixes may differ in difficulty.** Low schedules use a subset of the high schedule's six instances. Assigned-schedule matching protects the enforcement contrast, but item difficulty can still affect baseline support and cross-pair comparability. Simulation should test slot-rotation schemes before any protocol freeze.
6. **Tool limits need hard enforcement.** The JSON declares affordances but does not itself implement call counting, disabled-call behavior, transcript serialization, or zero-retry rules. Those belong in the deterministic state machine and must render identically for equal assigned schedules.
7. **Counterbalance requires cell divisibility.** Exact four-way allocation requires replication counts compatible with four variants inside every pair×dose cell; unmatched allocations cannot be silently repaired after choices are observed.
8. **Follow-up task equivalence is structural only.** Disjoint held-out payloads use the same rule and nominal schedule, but no empirical calibration establishes equal difficulty or equal choice salience between baseline and follow-up.
9. **Renderer leakage remains possible.** Field names and internal assignment records are not model-visible in this JSON, but a future implementation could leak them through tool errors, logging, or configuration headers. Byte-level transcript snapshots are required.
10. **Objective correctness is not scientific adequacy.** Deterministic keys and parsers prevent judge-model ambiguity; they do not establish construct validity, model-family transport, power, or novelty.

## Gate decision

**PASS for integration into the local state-machine and simulation work.** This item bank is sufficiently explicit to test assignment timing, schedule serialization, exact marginal matching, counterbalance allocation, parser behavior, and call accounting without model calls.

**NOT YET CLEARED for a provider pilot.** Before any such request, the combined zero-call package still needs to demonstrate block positivity under heterogeneous choice rates, viable constrained schedule permutations, transcript identity across arms, parser/availability decision behavior, and an acceptable call-and-cost envelope. Frontier-model unsaturation can only be evaluated later under separately approved calls.

## Post-audit integration note — 2026-08-04

The combined zero-call package subsequently added an executable renderer,
counterbalanced `PLAN:A/B` adapter, 240-surface role-cue scan, SHA-256 complete
schedule materialization, session-ID binding, payload-bound held-out state machine,
pre-side-effect tool-call guard, and terminal zero-retry handling. Those additions
resolve the local implementation gaps described in risks 6 and 9 for the tested
runtime path; they do not resolve provider-specific tool transport or empirical
behavior. The combined gate still returns `REDESIGN_BEFORE_PROVIDER_CALLS` because
the strict binary equivalence rule cannot certify invariance at the declared
5–15% unavailability levels. See `ZERO_CALL_GATE_REPORT.md` for the controlling
package-level verdict.
