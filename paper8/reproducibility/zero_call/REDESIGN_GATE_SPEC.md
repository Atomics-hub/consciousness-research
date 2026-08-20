# Binding Test identified-outcome redesign gate

**Frozen before redesigned gate-result generation:** 2026-08-05  
**Scope:** local construction, deterministic audit, and seeded planning only.
Nothing in this specification authorizes a provider/model call, paid API,
credential use, external-account action, recruited-human activity, public release,
or confirmatory experiment.

## Decision forced by the first zero-call gate

The latent binary high-choice estimand is only partially identified when the
follow-up disposition is `U`. With a strict binary equivalence margin of ±.05,
the assumption-free null region is already `[-.05,+.05]` at 5% `U` before
sampling uncertainty. The redesigned primary analysis therefore treats the
fully observed nominal disposition `D in {L,H,U}` as the identified outcome.

The latent-binary worst/best-case region remains a required, nonblocking
sensitivity analysis. It cannot create or veto an identified `L/H/U` claim.
No midpoint, complete-case, or ordinal encoding of `U` is allowed.

## Population, cells, and prospective weights

The analysis population is limited to semantically valid-baseline sessions that
enter a complete canonical 4L/4H randomization block. Attrition before block
formation is reported separately and is never hidden in the randomized-population
claim.

The reference planning panel has four macro cells:

`exact model snapshot x target family`, with two snapshots and the two target
families `work_score_allocation` and `tool_budget_allocation`.

Within each macro cell, active-dose blocks are formed separately in the 24 fine
strata `six item pairs x four presentation-counterbalance variants`. Blocks,
support, or weights may not be borrowed across fine strata. The primary cell
estimand gives the 24 declared fine strata equal prospective weight. Realized
retention cannot silently reweight the estimand. Active block counts per macro
cell must therefore be divisible by 24.

Zero-dose sessions are falsification controls. They do not identify the mechanism
and are not pooled into the active-dose primary estimand.

## Identified estimands and language

For macro cell `g` and category `k in {L,H,U}`:

`Delta[g,k] = P(D=k | assigned self, g) - P(D=k | assigned yoke, g)`.

The terms `positive` and `negative` below refer only to an observed-disposition
reallocation. Even an opposing `H/L` pattern does not identify a latent binary
choice change when availability can depend on the latent choice. A mechanism
claim is also unavailable: the core self-versus-yoke contrast cannot distinguish
workload-control response from generic credibility or interface response.

The frozen component margins are:

- `L`: ±.05;
- `H`: ±.05;
- `U`: ±.02.

These are operational margins for this local gate, not claims that the values are
universally scientifically privileged.

## Confirmatory block-level inference

Each complete eight-session block contributes one self-minus-yoke difference in
each nominal category probability. The confirmatory engine must:

1. validate exactly four self and four yoke rows in every block;
2. keep blocks inside one declared macro cell and one declared fine stratum;
3. estimate every fine-stratum contrast from independent block contrasts;
4. combine the 24 fine-stratum estimates with prospective equal weights;
5. estimate uncertainty from between-block variation inside fine strata;
6. require every declared fine stratum and a prospectively frozen minimum number
   of four blocks per fine stratum;
7. use strict decision boundaries and reject nonfinite, malformed, duplicated, or
   compositionally impossible inputs;
8. emit an honest method/assumption label and machine-readable claim scope.

### Calibration/confirmatory phase firewall

No redesigned gate result containing this integrity status had been generated
when this clarification was added on 2026-08-05. It changes provenance admission,
not any estimand, margin, decision boundary, simulation DGP, or numerical target.
The next eligible publication must be regenerated from this source state.

Every confirmatory design and observation must carry all three immutable binding
fields: `study_phase`, `protocol_run_id`, and `protocol_manifest_digest`. The
manifest digest is a lowercase SHA-256 digest of the exact frozen protocol
manifest. Only `study_phase=confirmatory` is eligible for confirmatory analysis.
Calibration records use `study_phase=calibration`, a distinct protocol run ID,
and their own manifest digest; they must never be relabeled or pooled into the
confirmatory dataset.

The strict confirmatory mapping loader rejects missing or extra fields and rejects
every calibration-phase record. Independently of that ingestion boundary, the
analyzer must reject a calibration-phase design or observation and any observation
whose protocol run ID or manifest digest differs from the confirmatory design.
These checks occur before block validation, coverage checks, contrasts, or
inference.

### Zero-variance integrity clarification frozen before the final eligible run

No eligible redesigned gate result had been generated when this clarification
was added on 2026-08-05; preliminary screening code already enforced it. A
component whose empirical standard error is at or below `1e-12` cannot establish
a directional or equivalence claim. It is inference-invalid and therefore
indeterminate for every conjunction. In particular, an observed all-zero `U`
component cannot manufacture population equivalence merely because its plug-in
t interval collapses to a point. This is a conservative no-observed-variation
guard, not a claim that the true population variance or contrast is known to be
zero. The final eligible certification must be regenerated after this written
clarification.

The frozen reference construction is conservative fixed-stratum Student-t
inference, not a claim of exact randomization inversion. If `d[j,b,k]` is block
`b`'s self-minus-yoke contrast for category `k` inside fine stratum `j`, compute
the fine-stratum mean `dbar[j,k]` and sample variance `s2[j,k]`. With `J=24`
required fine strata and prospective weight `w=1/J`, the macro-cell estimate and
variance are

`DeltaHat[g,k] = sum_j w * dbar[j,k]`

and

`VHat[g,k] = sum_j w^2 * s2[j,k] / n[j]`.

Use the conservative degrees of freedom `min_j(n[j]-1)`. Positive and TOST
equivalence components use `t_(1-alpha,df)` one-sided bounds at `alpha=.05`.
The published simultaneous intervals use
`t_(1-alpha/(2*12),df)` for Bonferroni coverage across all four cells and three
categories. The assumptions are mutually independent canonical blocks, fine
strata and cells fixed before outcomes, retention independent of follow-up
outcomes, and an adequate Student-t approximation for block contrasts. Exact
restricted-randomization inversion would require the complete allowed assignment
and potential-outcome construction and is not asserted by this engine.

The four-cell headline is an intersection-union claim. The directional observed-
reallocation headline requires, in **every** macro cell, a one-sided 95% lower
bound for `Delta[H]` strictly above `+.05` and a one-sided 95% upper bound for
`Delta[L]` strictly below `-.05`. The exact reverse is labeled a reverse observed
reallocation, not silently folded into the positive headline.

The observable-equivalence headline requires, in **every** macro cell, strict
equivalence of `L/H` within ±.05 and `U` within ±.02. Any absent, unsupported, or
indeterminate cell makes the four-cell headline indeterminate. A pooled zero can
never repair cell heterogeneity.

For transparent estimation, publish conservative 95% simultaneous intervals over
all 12 macro-cell-by-category contrasts. Equal-weight fixed-panel averages and
model- or target-marginal averages are secondary and must be labeled with exactly
that narrower scope.

The planning bootstrap may be used only for zero-call behavior checks. Its output
must serialize `planning_only`/`provisional` and cannot use an unqualified
`established` label.

## High-resolution planning grid

### Final sensitivity-DGP clarification frozen before the final eligible run

No eligible redesigned gate result had been generated when these numerical DGP
details were written on 2026-08-05. The final certification grid is the Cartesian
product `U in {0,.05,.10,.15}` and block-arm ICC
`rho in {0,.10,.25}`. At `rho=0`, each four-session arm count follows the nominal
multinomial distribution. At `rho>0`, it follows a Dirichlet-multinomial with
base category probabilities `p` and total concentration `(1-rho)/rho`, giving
the exchangeable four-session design-effect proxy `1+3*rho`. Self and yoke arm
counts are generated independently, as are complete blocks, fine strata, and
macro cells in this numerical sensitivity model. These are planning stress
assumptions, not assertions about an eventual provider population.

For a homogeneous cell with baseline `b=(1-U)/2`, the yoke probabilities are
`(L,H,U)=(b,b,U)`. A signed reallocation effect `e` gives self probabilities
`(b-e,b+e,U)`. The frozen effects are `e` in `+/-.05`, `+/-.1055`, and `+/-.15`.
The availability-only stress instead gives self
`((1-U-.10)/2,(1-U-.10)/2,U+.10)`. The one-model and one-cell stresses apply
`e=.15` only to the first model's two cells or the first macro cell,
respectively. The mechanism alias has exactly the `e=.15` observable
probabilities and random stream but a deliberately nonidentified generic
mechanism label.

The fine-stratum heterogeneity stress crosses the six pair effects
`(-.10,-.05,0,.10,.15,.20)` with the four counterbalance offsets
`(-.03,-.01,.01,.03)` in pair-major order. Its 24 signed effects range from
`-.13` to `+.23` and have prospective equal-weight mean exactly `+.05`, so it is
a strict-boundary positive-headline false control. The whole positive-size trust
root requires exactly seven scenarios—`positive_15` power plus null, positive
boundary, availability-only, one-model-only, one-cell-only, and this
heterogeneity false control—at all 12 `U x rho` cells. The mechanism alias and
reverse/supplemental grids remain non-gating diagnostics.

Candidate active block counts per macro cell are:

`24, 48, 72, 96, 120, 144, 168, 192, 288, 384, 576, 768, 1152,
1536, 1920, 2304, 3072`.

Planning covers `U = 0%, 5%, 10%, 15%` and at least these data-generating cases:

- exact null;
- opposing `H/L` reallocations of ±.05 (strict boundary), ±.1055, and ±.15;
- availability-only movement;
- one-macro-cell-only and one-model-only movement;
- equal-observable generic-mechanism alias;
- item/fine-stratum heterogeneity;
- block overdispersion/ICC sensitivity;
- snapshot drift and invalid time-confounded collection.

The all-four-cell positive planning target is the ±.15 benchmark. A selected size
must have a Wilson 95% lower bound of at least .90 for its all-four-cell decision
rate at every declared `U` and design-effect sensitivity included in the selection
rule. The null, boundary, availability-only, and one-cell-only false-headline
Wilson upper bounds must not exceed .055.

The all-four-cell equivalence size is reported separately. It is never inferred
from positive power and is expected to be much larger because of the ±.02 `U`
margin. If no operationally plausible size clears the negative target, the broad
negative headline is abandoned; failure to establish a positive result is then
indeterminate, not evidence of invariance.

For a final numerical certification, use at least 20,000 outer replicates for
null/boundary false-headline cells and at least 10,000 for selected-size power
cells. Smaller grids are explicitly screening-grade and cannot clear the numerical
gate. Every seed, replicate count, interval engine, and design-effect setting is
written into the machine-readable result.

## Support and request accounting

For `B` active blocks per macro cell, `M` model snapshots, and `T=2` target
families, active randomized sessions are:

`R_active = 8 * B * M * T`.

Attempt counts are projected separately for each fine stratum using conservative
lower bounds for semantic-validity and minority-choice probabilities. A proposed
set of attempt caps must give at least .95 planned probability of completing
**all** required fine strata. The conservative reference calculation allocates
the .05 failure budget across the required fine strata by a union bound; it also
reports each per-stratum assurance and the resulting global lower bound. Merely
using .95 assurance separately in every fine stratum is insufficient. There is
no outcome-dependent extension, item rewriting, silent cell dropping, or support
borrowing.

The reference binomial-tail support calculation assumes independent, stationary
Bernoulli baseline-attempt validity and H/L outcomes within each fine stratum.
Its union-bound global lower bound does not require independence across fine
strata. These are planning assumptions that must be frozen or replaced before
any external calibration proposal.

Request accounting uses separate ledgers for baseline attempts, execution
attempts, tool continuations, and follow-up attempts. The successful-session
identity `A + 2R + sum(q_s)` is not used to erase billed failed attempts. Failed
execution is terminal, receives no second execution, and receives no follow-up.
Thus every randomized session contributes exactly one execution attempt, only a
successful execution contributes a follow-up attempt, and all tool continuations
before success or terminal failure remain ledgered. The all-success expression is
a conservative request maximum under the frozen per-schedule continuation caps,
not an assertion that every attempted request succeeded.

For this reference active-design request envelope, the item-bank sequential caps
are frozen as `(pair, q_low, q_high)`:
`(TB01,2,6)`, `(TB02,2,6)`, `(TB03,3,6)`, `(TB04,1,6)`,
`(TB05,2,6)`, and `(TB06,2,6)`; the work/score target has zero tool
continuations. Thus `q_low` ranges from 1 to 3, `q_high` is exactly 6, and the
equal prospective pair/variant allocation makes the all-success continuation
count exactly 32 per retained tool block. These caps and their item-bank linkage
are enforced by the planning configuration. Exact provider transport behavior,
parallel-call semantics, token caps, and billing still require a new freeze
before any external calibration proposal. Zero-dose calibration or falsification
controls have no frozen count and are excluded from this active-design envelope.

No dollar figure is valid until exact model snapshots, provider prices, token
caps, tool-loop transport, caching, failed-request billing, valid-baseline rate,
and support attrition are frozen.

## Redesigned gate verdicts

- `REDESIGN_INCOMPLETE`: any estimand, inference, replication, simulation, or
  integrity blocker remains.
- `CONDITIONAL_GO_FOR_CALIBRATION_PROPOSAL`: local construction passes and a
  bounded nonconfirmatory feasibility protocol may be proposed, but no external
  call is authorized.
- `CONFIRMATORY_SIZE_IDENTIFIED`: a numerical size clears all frozen operating-
  characteristic gates. This still does not authorize collection.

Before even a nonconfirmatory provider calibration proposal, the package must
have a clean test suite and manifest; exact snapshots and provider settings;
fixed prompts, parsers, retry-zero and transport rules; item/variant allocation;
baseline and follow-up request/token caps; a maximum runtime and dollar cap; and
explicit approval for that exact external action. Calibration sessions can never
enter the confirmatory dataset. Every calibration and confirmatory run must retain
its distinct phase, protocol run ID, and frozen protocol-manifest digest.

## Claim ceiling

The strongest positive claim available from the core is:

> In the exact tested snapshots, both tested target families, and prospectively
> defined valid-baseline block-supported randomized population, the observed
> follow-up disposition distribution reallocated from L toward H under assigned
> self-contingent versus assigned-schedule-matched yoked history beyond the
> declared margins.

The strongest redesigned negative claim is limited to observed dispositions:

> In those exact four macro cells and randomized population, the observed
> follow-up L/H/U distribution was equivalent within the declared category
> margins.

Neither statement establishes a latent binary-choice effect under choice-dependent
availability, a workload-specific mechanism, preference, utility, experience,
welfare, consciousness, or generalization beyond the tested finite panel.
