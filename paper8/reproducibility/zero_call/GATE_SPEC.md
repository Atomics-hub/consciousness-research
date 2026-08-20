# Binding Test local zero-call gate specification

**Frozen before gate-result generation:** 2026-08-04  
**Scope:** local construction, deterministic audit, and seeded simulation only. No
provider, paid API, credential, external-account, recruited-human, or public action
is authorized by this gate.

## Status vocabulary

- `PASS`: the local artifact mechanically establishes the declared property.
- `CONDITIONAL`: the artifact is coherent, but the property requires observations
  from a separately approved provider pilot or a later frozen protocol choice.
- `FAIL`: the local artifact violates a hard construction requirement.

The overall result is `REDESIGN_BEFORE_PROVIDER_CALLS` if any hard construction
gate fails. Otherwise it is `CONDITIONAL_GO_FOR_A_PILOT_PROPOSAL`, not approval to
run a pilot. A pilot proposal must still name the model snapshots, attempted and
randomized session counts, item allocation, call/token/tool caps, runtime, provider
retention, and dollar cap.

## G1 — timing, parsing, and retention

Pass only if automated tests establish all of the following:

1. no enforcement arm or received schedule can be assigned before a semantically
   valid canonical baseline choice;
2. invalid, refusal, missing, and transport-failed baselines enter `U` and cannot
   be randomized;
3. strict-format and semantic-validity ledgers remain distinct;
4. `U` is never assigned an ordinal score;
5. exactly one executed history and one non-executed held-out follow-up are allowed;
6. model-visible records reject enforcement-role labels, including nested fields
   and free-text values.

## G2 — item-bank construction and semantic surface

The machine-checkable portion passes only if the bank has exactly 12
baseline/follow-up pairs: six work/score and six tool/budget; deterministic payloads
and answer keys; both canonical schedules; counterbalanced display order/labels;
and zero-dose controls in both families. Prospective choice interfaces may not use
`self-contingent`, `yoke`, `donor`, `recipient`, `treatment`, or equivalent role
labels. Given the same canonical item and received schedule, self and yoke sessions
must expose byte-equivalent normal execution/follow-up surfaces.

Frontier-model unsaturation and semantic equivalence cannot be established without
provider observations. They remain `CONDITIONAL` even if the structural audit
passes. Structural adequacy must not be reported as empirical non-ceiling evidence.

## G3 — restricted assignment

The canonical inferential block contains eight valid baselines, exactly four `L`
and four `H`. The complete allowed set must:

- assign four sessions to each enforcement arm;
- place two `L` and two `H` baselines in each arm;
- execute each self session's selected schedule;
- copy each of the four complete self-schedule records to exactly one yoke session;
- give the yoke recipient-choice × received-schedule table one observation in each
  of its four cells (exact zero association, two matches, two mismatches);
- contain 576 equally likely donor-aware joint assignments. Collapsing donor
  identity leaves 144 arm-plus-schedule exposure assignments; these are not to be
  confused.

Enumeration must show, for every retained session, `P(self)=P(yoke)=1/2` and,
conditional on yoke assignment, probability `1/2` for each received schedule and
`1/2` for each match class.

## G4 — block formation and support attrition

Blocks must be formed deterministically within every prospectively frozen stratum;
support may never be borrowed across strata. Invalid baselines and unmatched valid
remainders must be ledgered, not replaced. Synthetic baseline-high rates are
`10%, 30%, 50%, 70%, 90%`; attempted counts are `64, 128, 256, 512` per stratum.
Report realized seeded retention and the large-sample ceiling
`2 * min(p_H, 1-p_H)`.

There is no locally justified universal retention cutoff. Adequacy at the actual
model × target × item/dose × presentation strata is therefore `CONDITIONAL`; a
zero- or one-choice empirical stratum is non-identifying and cannot be repaired by
semantically manipulating the options after seeing its choices.

## G5 — estimands and decision rules

The fully observed primary vector is the arm contrast for each mutually exclusive
follow-up category `(L, H, U)`, computed non-ordinally. Candidate simultaneous
equivalence margins are `(0.05, 0.05, 0.02)`. A distributional-change decision
requires at least one simultaneous 95% interval to lie wholly beyond its two-sided
margin. Distributional invariance requires all three simultaneous intervals to lie
inside their corresponding margins; all other outcomes are indeterminate.

The separate binary-high contrast treats `U` as missing and reports worst/best-case
bounds. Its sampling-expanded identified region must lie wholly above `+0.05` or
below `-0.05` for responsiveness, or wholly inside `[-0.05,+0.05]` for invariance.
Otherwise it is indeterminate. No midpoint imputation is permitted.

Planning simulations use block resampling and are not a substitute for the final
restricted-randomization analysis. With nominal 95% simultaneous intervals, the
Monte Carlo tolerance for a false categorical decision in a boundary/null check is
0.075. Any simulation-replicate count and seed must be written into the results.

## G6 — required stress scenarios

The report must include null, positive and negative differences, equivalence-boundary,
generic-credibility alias, one-model-only effect, post-treatment history divergence,
5%, 10%, and 15% follow-up unavailability, and snapshot drift. It must explicitly
show that the core contrast cannot distinguish workload-control response from a
generic credibility/interface effect with the same observable data-generating
distribution. That limitation is not a construction failure; it caps the mechanism
claim unless an optional comparator later passes its own semantic gate.

## G7 — call and cost envelope

Every attempted session spends one baseline generation. Only randomized sessions
spend one execution generation and one follow-up generation. If `A` sessions are
attempted, `R=8B` enter `B` canonical blocks, and execution uses `q_s` additional
model continuations for tool rounds, the exact generation-request identity is

`C = A + 2R + sum(q_s for randomized sessions s)`.

For a tool/budget block with schedule caps `q_L` and `q_H`, exact assigned-schedule
balance gives the conservative block cap

`C_block,max = 24 + 4(q_L + q_H)`,

while a no-tool work/score block costs exactly 24 generation requests once its
eight baseline-eligible sessions exist. Baseline calls spent on unmatched or
invalid attempts remain in `A`. Dollar cost cannot be stated until model-specific
input/output-token prices, prompt lengths, output caps, and tool prices are frozen;
the report must provide the symbolic cost identity and must not silently reuse the
superseded 300/360-response budget.
