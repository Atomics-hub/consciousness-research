# The Binding Test: Registered Report Stage-1 protocol draft

**Document status:** `DRAFT — NOT PREREGISTERED, NOT SEALED, NOT ACCEPTED IN PRINCIPLE`
**Current collection decision:** `NO-GO`
**Scientific phase:** prospective protocol development after the zero-call construction audit
**Provider/model observations analyzed here:** none

## 1. Authority, status labels, and no-go rule

This document is the controlling statement of the proposed Registered Report
architecture *within the draft preregistration bundle*. It does not supersede the
sealed zero-call sources or the current transition checklist in
[`PROTOCOL_AMENDMENTS_REQUIRED.md`](PROTOCOL_AMENDMENTS_REQUIRED.md), does not
authorize a provider request, and is not evidence that a journal has granted
in-principle acceptance. Until this draft is completed, independently audited,
prospectively registered, and sealed under a new protocol digest, the existing
checklist remains controlling for the empirical `NO-GO`.

This draft uses three status labels:

- `DRAFT-FROZEN`: fixed within this draft. A change requires a documented new
  draft version and, after registration, a prospective amendment and new digest.
- `INHERITED-LOCAL`: implemented or specified in the zero-call construction, but
  not yet sufficient authority for an empirical run.
- `UNRESOLVED-BLOCKING`: no calibration or confirmation may begin until the field
  has an exact value, implementing artifact, verification evidence, and `PASS`.

Tables may combine these labels as `DRAFT-FROZEN / UNRESOLVED-BLOCKING` when a
scientific choice is frozen in the amendment but production implementation,
recertification, registration, or sealing still blocks empirical use. The prose
shorthand “amendment-frozen” means `DRAFT-FROZEN`; it is not a fourth status or
a gate `PASS`.

Silence, a placeholder, `TBD`, or a planning value without substantive rationale
counts as `UNRESOLVED-BLOCKING`. Provider calibration and provider confirmation
remain separate actions; each requires its own sealed action-specific approval
after all relevant protocol gates pass.

## 2. Research question, claim ceiling, and hypotheses

### 2.1 Research question

The study asks whether the observed held-out **terminal-disposition distribution**
changes when its earlier baseline choice controls the schedule it receives,
compared with a donor-matched yoked policy that preserves the assigned-schedule
and affordance marginals. Successful follow-up choices contribute `L` or `H`,
while the frozen non-choice source/subtype mapping contributes `U`. The design
therefore estimates an enforcement-policy effect on observable terminal
dispositions, not a conditional choice-only effect. It does not identify
preference, utility, subjective cost, welfare, consciousness, or a
workload-specific mechanism.

### 2.2 Primary hypothesis and exact licensed wording

Let \(\Delta_{g,k}\) be the self-minus-yoke contrast for category
\(k\in\{L,H,U\}\) in required macro cell \(g\). Let \(\tau\) denote the
directional threshold. The amendment freezes \(\tau=.05\) as the study-specific
minimum for both directional components. Passing both components implies a
total-variation shift greater than .05 in the three-category terminal
distribution. The threshold is an operational scientific choice, not a
universal or empirically validated constant; +.15 and +.1055 remain planning
alternatives rather than SESOIs.

The primary all-cell alternative is the intersection

\[
\bigcap_g\{\Delta_{g,H}>\tau\}\cap\{\Delta_{g,L}<-\tau\}.
\]

It is established only when, in every required macro cell, the one-sided 95%
lower confidence bound for \(\Delta_H\) is strictly greater than
\(+\tau+10^{-12}\) and the one-sided 95% upper confidence bound for
\(\Delta_L\) is strictly less than \(-\tau-10^{-12}\). The \(10^{-12}\)
term is the frozen numerical guard band, not an added substantive effect
threshold. The exact licensed headline is:

> A paired directional H-increase/L-decrease in observed terminal dispositions
> was established in every prespecified model-snapshot-by-target cell, with U
> reported separately.

`U` is excluded from the primary H/L conjunction and is always reported
separately (`AMENDMENT-FROZEN`). Consequently, the primary must not be called a
pure `L`-to-`H` transfer, an availability-invariant reallocation, a binary-choice
effect, or evidence about an internal preference. A change in `U` does not veto
or create the paired H/L decision, but malformed `U` records or a failed
terminal-ledger join are design-integrity failures and stop all analysis.

The composite null is the union of all cases in which at least one required cell
fails at least one strict H/L bound. Failure to reject that composite null is
`NOT_ESTABLISHED`; it is not evidence of invariance or equivalence.

### 2.3 Secondary and diagnostic decisions

- The exact reverse H-decrease/L-increase conjunction is reported as a separate
  secondary directional label. It cannot be folded into the primary headline.
- `U` estimates and their simultaneous intervals are always reported separately.
- Observed-vector equivalence over `L/H/U` is secondary and cannot support a
  broad negative claim. The amendment-frozen operational margins are `L=.05`,
  `H=.05`, and `U=.02`. Together they hold observed-distribution total variation
  below .05 while applying a tighter limit to the heterogeneous `U` channel.
  They are study-specific and non-authorizing, not universal constants.
- The latent-binary high-choice contrast is a nonblocking partial-identification
  sensitivity analysis. It cannot create, rescue, or veto the identified nominal
  outcome decision.
- Zero-dose conditions are falsification controls and are excluded from the
  active-dose primary estimand. Their allocation and multiplicity treatment are
  `UNRESOLVED-BLOCKING`.
- No credibility comparator is included in the primary design
  (`DRAFT-FROZEN`). The mechanism claim therefore remains an enforcement-policy
  effect. Adding a comparator is a scientifically material amendment.

All exact decision mappings and precedence rules are specified in
[`ANALYSIS_DECISION_CHARTER.md`](ANALYSIS_DECISION_CHARTER.md).

## 3. Estimand, interference, and populations

### 3.1 Full-assignment potential outcomes

For block \(b\), let \(A_b\in\Omega_b\) be the complete donor-aware assignment
sampled from the frozen policy \(\pi_b\). Let \(E_{sb}(A_b)\) contain session
\(s\)'s arm, received schedule, match status, donor, counterbalance, item pair,
and assignment-derived affordances. Let \(D_{sb}(A_b)\in\{L,H,U\}\) be its
terminal disposition.

Potential outcomes are indexed by the full block assignment. Interference is
allowed within a block through the donor-yoke mapping and assumed absent across
blocks after conditioning on the prospectively fixed fine stratum, model
snapshot, target family, and declared provider/batch structure. The block is the
randomization stratum, planned interference cluster, and primary independent
inference unit. Sessions are not independent replications of the assignment
policy.

For category \(k\), each realized block contributes

\[
d_{b,k}=\frac{1}{4}\sum_{s:Z_{sb}=\mathrm{self}}1(D_{sb}=k)
-\frac{1}{4}\sum_{s:Z_{sb}=\mathrm{yoke}}1(D_{sb}=k).
\]

The target is the finite-randomized-population expectation of this block contrast
over \(A_b\sim\pi_b\), followed by the prospectively fixed equal weighting of the
24 required fine strata inside each macro cell. It is an allocation-policy
estimand under partial interference, not an unrestricted individual direct
effect.

### 3.2 Populations

Four populations are retained and reported without substitution:

1. **Attempt population:** every prospectively authorized baseline request,
   including transport failures, invalid baselines, and unavailable baselines.
2. **Baseline-valid population:** attempts producing a semantically valid
   canonical `L` or `H` baseline choice under the frozen parser.
3. **Randomized population:** baseline-valid sessions placed into complete,
   prospectively supported canonical blocks and assigned exactly once.
4. **Finite-panel inference population:** the complete set of required macro
   cells and fine strata under the prospective weights.

The primary estimand is over the randomized population and the fixed finite
panel. It does not generalize to all attempts, unmatched valid sessions, other
models, later snapshots, other target families, or deployed AI systems.

## 4. Panel, block formation, assignment, and concealment

### 4.1 Panel and fine strata

The proposed panel contains the Cartesian product of exactly two model snapshots
and the target families `work_score_allocation` and
`tool_budget_allocation`. Exact eligible model snapshot identities are
`UNRESOLVED-BLOCKING`. Each active-dose macro cell contains 24 prospectively
equal-weight fine strata: six frozen item pairs crossed with four presentation
counterbalance variants. Support and weights may not be borrowed across strata.

### 4.2 Deterministic block formation

A canonical block contains exactly eight baseline-valid sessions in one fine
stratum: four baseline `L` and four baseline `H`. Block formation uses only
pre-assignment fields. Invalid or unavailable baselines and valid unmatched
leftovers remain in the attempt-flow ledger and are never replaced after any
follow-up outcome is observed. The exact queue order, timeout, attempt cap, and
leftover stopping implementation are `UNRESOLVED-BLOCKING`.

### 4.3 Assignment policy

For every canonical block, the inherited local assignment engine enumerates 576
donor-aware assignments. Each member has:

- four self and four yoke sessions;
- two baseline `L` and two baseline `H` sessions in each arm;
- equal received-schedule marginals across arms;
- one yoke recipient in each baseline-by-received-schedule cell;
- two yoke matches and two yoke mismatches; and
- marginal self/yoke probability `1/2` for every session.

The proposed policy is uniform over the 576 members, with exact selected-member
probability `1/576` recorded as an exact rational value. No focal baseline choice
may deterministically select its own yoke schedule. Every declared exposure class
used in inference must have known nonzero support.

The empirical block-assignment object must bind at minimum:

- schema and policy versions;
- protocol run ID and protocol-manifest digest;
- block ID, macro cell, and fine stratum;
- assignment-engine digest;
- `Omega_b` digest and size;
- policy ID/digest and exact selection probability;
- selected `allowed_set_index`;
- randomness commitment and auditable selection material;
- the complete eight-row donor-aware mapping;
- item pair, dose, counterbalance, execution-order index, schedule, match, donor,
  and affordance fields;
- per-row schedule and affordance digests; and
- a digest over the complete immutable block object.

[`amendment_v1/protocol_authority.py`](amendment_v1/protocol_authority.py)
provides a standalone `DRAFT` implementation of closed
`binding-allowed-set-artifact-v1`, `binding-randomized-block-v1`, and
`binding-terminal-disposition-v1` records. It binds the assignment-engine
version/digest, all 576 ordered session-specific candidates, aggregate and member
digests, the selected index, the full selected candidate, the exact `1/576`
probability, and canonical record fingerprints. It verifies the byte-pinned
assignment source, locally recomputes the engine's exact canonical order, requires
288/288 self/yoke and 144/144 conditional yoke exposure marginals per session,
and binds a domain-separated uniform-policy digest. It also implements a 256-bit
entropy commitment/reveal proof, rejection-sampled index derivation, exact
membership verification, and an exactly-once per-block terminal ledger. Its
focused tests are in
[`amendment_v1/tests/test_protocol_authority.py`](amendment_v1/tests/test_protocol_authority.py).
Integration with the actual assignment engine, state machine, runtime transport,
confirmatory analyzer, manifests, and persisted run ledger remains
`UNRESOLVED-BLOCKING`. A session-level treatment bit or the current five-field
canonical fingerprint is not sufficient empirical provenance.

### 4.4 Concealment

No enforcement role, assignment, donor identity, recipient identity, or
assignment-derived state may exist before the eight baseline choices in a block
are frozen. A run-level entropy commitment may be created earlier, but the
block-specific allowed set and selected member are constructed only after block
eligibility is fixed. Assignment is controller-generated, not selected by a
human, provider, or model. The model-visible baseline interface is arm-neutral;
extraneous role labels, warnings, apologies, or arm-specific error messages are
forbidden.

The draft authority defines a canonical commitment for an opaque 256-bit reveal
and derives the selected index by SHA-256 rejection sampling over the committed
block/allowed-set context. It proves reveal/commitment/context/index consistency,
but does not prove that the reveal was independently or uniformly sampled. The
entropy source and independence audit, preselection commitment timing,
commitment/reveal schedule, access controls, runtime integration, and persistence
format remain `UNRESOLVED-BLOCKING`. They must permit reconstruction after the run
without exposing mutable assignment state during baseline choice.

## 5. Endpoint and exhaustive terminal taxonomy

### 5.1 Primary endpoint

Every randomized session contributes exactly one immutable terminal analysis row
with `terminal_disposition` in the closed nominal set `{L,H,U}`. `L` and `H`
require a semantically valid parsed follow-up choice. Every other terminal
post-randomization path maps to `terminal_disposition=U` while retaining a non-ordinal
`disposition_source`, `failure_subtype`, parser-validity fields, and
`integrity_failure`. Terminal `U` is an intention-to-treat category, not an
ordinal midpoint and not ignorable missingness.

The closed taxonomy is `AMENDMENT-FROZEN`:

| `disposition_source` | Allowed `failure_subtype` | `terminal_disposition` | Parser-validity fields | `integrity_failure` |
|---|---|---:|---|---:|
| `followup_choice` | `none` | `L` or `H` | `followup_strict_valid` is Boolean; `followup_semantic_valid=true` | `false` |
| `followup_unavailable` | `missing_response` | `U` | both `false` | `false` |
| `followup_unavailable` | `empty_response` | `U` | both `false` | `false` |
| `followup_unavailable` | `explicit_refusal` | `U` | both `false` | `false` |
| `followup_unavailable` | `invalid_response` | `U` | both `false` | `false` |
| `execution_failure` | `invalid_response` | `U` | both `null` | `false` |
| `execution_failure` | `transport_error` | `U` | both `null` | `false` |
| `execution_failure` | `timeout` | `U` | both `null` | `false` |
| `execution_failure` | `provider_error` | `U` | both `null` | `false` |
| `execution_failure` | `quota_exhausted` | `U` | both `null` | `false` |
| `execution_failure` | `tool_error` | `U` | both `null` | `false` |
| `execution_failure` | `tool_limit_exceeded` | `U` | both `null` | `false` |
| `followup_failure` | `transport_error` | `U` | both `null` | `false` |
| `followup_failure` | `timeout` | `U` | both `null` | `false` |
| `followup_failure` | `provider_error` | `U` | both `null` | `false` |
| `followup_failure` | `quota_exhausted` | `U` | both `null` | `false` |
| `local_protocol_abort` | `assignment_binding_mismatch` | `U` | both `null` | `true` |
| `local_protocol_abort` | `schedule_integrity_mismatch` | `U` | both `null` | `true` |
| `local_protocol_abort` | `role_leak_detected` | `U` | both `null` | `true` |
| `local_protocol_abort` | `runtime_contract_violation` | `U` | both `null` | `true` |
| `local_protocol_abort` | `controller_abort` | `U` | both `null` | `true` |
| `local_protocol_abort` | `unknown` | `U` | both `null` | `true` |

`followup_strict_valid=true` implies semantic validity, but a semantically valid
`L/H` follow-up may have either Boolean strict-validity value. Non-follow-up
sources require both parser-validity fields to be `null`. The
`integrity_failure` flag is `true` exactly for `local_protocol_abort`; such a row
is retained with `terminal_disposition=U`, but the finalized block is not
headline-eligible.

The production controller must freeze a deterministic rule that emits one of
these exact pairs when several failures are observed. If it cannot establish one
non-integrity source/subtype pair, it must emit
`local_protocol_abort/unknown`, set `integrity_failure=true`, retain the `U` row,
and invalidate headline eligibility. That reducer integration is not yet
implemented; the standalone authority validates the closed record after it is
constructed.

### 5.2 Randomization-to-terminal ledger join

The immutable randomized roster contains exactly eight session keys per block.
The terminal record key is the tuple

`(protocol_run_id, block_id, session_id)`.

The terminal ledger must contain exactly one row for each randomized-roster key,
no conflicting key, no extra unrandomized key, and the same protocol, block,
manifest, and `randomized_block_fingerprint` bindings. The fingerprint binds the
complete assignment authority, including arm, donor, schedule, pair, dose, and
variant. The joined block must contain exactly eight terminal rows. An identical
replay is idempotent; a conflicting replay or new append after finalization is
fatal. Missing, conflicting, extra, or binding-mismatched terminal rows are
ledger-invalid conditions; they are not silently converted to `U` during analysis. The
controller must create the appropriate closed `U` row before ledger finalization.

Raw event history is not itself the analysis table. A frozen deterministic reducer
must create the one-row terminal projection, preserve the exact source/subtype and
parser/integrity fields, reject a conflicting terminal commit, and bind the
projection to the complete randomized-block fingerprint. The standalone closed
record and ledger are implemented in `amendment_v1/protocol_authority.py`; runtime
event reduction and persistence integration remain `UNRESOLVED-BLOCKING`.

## 6. Inclusion, exclusion, and execution order

### 6.1 Inclusion and exclusion

- All authorized baseline attempts enter the attempt-flow ledger.
- Only semantically valid canonical `L/H` baselines can enter block formation.
- Only complete supported 4L/4H blocks are randomized.
- Every randomized session is retained exactly once in the intention-to-treat
  terminal ledger, regardless of execution, transport, follow-up, quota, or
  local failure. Estimator and headline eligibility remain contingent on the
  prospectively frozen design-integrity rules.
- No randomized session may be dropped, replaced, rerandomized, converted into a
  new attempt, or used to dissolve its assigned block.
- Pre-randomization invalid/unavailable baselines and unmatched valid leftovers
  are not primary outcomes; they are reported in the population flow.
- Calibration, zero-dose, and any later comparator records are excluded from the
  active-dose confirmatory primary estimand by immutable phase/dose bindings.
- A scientifically material integrity failure can invalidate a block, cell, or
  run, but it never becomes an outcome-favorable post hoc exclusion. The affected
  randomized rows remain in the audit record.

### 6.2 Irreversible execution order

1. Verify the prospective protocol digest, materials, provider/model identity,
   caps, and phase before prompt release.
2. Create one immutable attempt/session identifier and render the arm-neutral
   baseline interface.
3. Record and mechanically parse the baseline response.
4. Record invalid/unavailable baseline attempts or queue valid `L/H` sessions in
   their exact fine stratum.
5. Freeze a complete 4L/4H block and its eight baseline records.
6. Construct and verify `Omega_b`; sample one member from the frozen policy.
7. Commit the complete block-assignment object before outcome-bearing execution.
8. Materialize and verify the exact schedule and affordances for all eight rows.
9. Execute each assigned schedule under the frozen tool and transport guard.
10. Present one disjoint held-out follow-up when the terminal path permits it.
11. Commit exactly one closed terminal row for every randomized session.
12. Finalize the eight-way ledger join and run integrity/support checks before
    computing any outcome contrast.

Within-session retry and resume are prohibited after an ambiguous or failed
post-randomization dispatch in this draft; the session receives the corresponding
`terminal_disposition=U` row under the frozen source/subtype mapping. A pre-randomization retry, if later permitted, must be
a new attempt with a new identifier and cannot replace or erase the first
attempt. Exact provider transport/idempotency implementation remains
`UNRESOLVED-BLOCKING`.

## 7. Confirmatory analysis and multiplicity

### 7.1 Reference estimator

Inside each macro cell and category, the reference analysis computes one
self-minus-yoke contrast per complete randomized block. It averages block
contrasts within each of the 24 required fine strata and combines fine-stratum
means with prospective equal weight `1/24`. Its variance estimate is the sum of
the weighted within-stratum mean variances, with degrees of freedom
`min_j(n_j-1)`.

The draft reference method uses one-sided 95% Student-`t` bounds for directional
and TOST components. This is a fail-closed fixed-stratum reference procedure,
not exact restricted-randomization inversion and not a general coverage theorem.
The final method remains contingent on dependence-aware recertification and is
therefore `UNRESOLVED-BLOCKING` for an empirical freeze.

### 7.2 Primary multiplicity

The primary claim is a single intersection-union test: all eight required H/L
component statements across four macro cells must pass at one-sided
`alpha=.05`. Because the global alternative is their intersection and the global
null is their union, no component can rescue another and no pooled contrast can
repair a failed cell. The claim fails if any component fails or is invalid.

For transparent estimation, the Stage-2 report must also publish Bonferroni 95%
simultaneous intervals across all 12 macro-cell-by-category contrasts. These
simultaneous intervals are reporting intervals and do not add a `U` guard to the
primary H/L conjunction.

Secondary equivalence and reverse-direction families are amendment-frozen as
non-authorizing and may not be promoted to primary claims. Zero-dose,
comparator, and binary-bound families remain `UNRESOLVED-BLOCKING` until their
own multiplicity roles are frozen.

### 7.3 Component validity, zero standard error, and strict boundaries

The zero-call reference guard is retained as an `AMENDMENT-FROZEN`
component-validity rule unless a future prospectively justified design-based
replacement is implemented and recertified:

- a component with empirical standard error at or below `1e-12` is
  `COMPONENT_INFERENCE_INVALID_ZERO_SE`;
- the tolerance is a numerical integrity threshold, not evidence that the
  population variance or effect is zero;
- invalid `H` or `L` blocks the primary and reverse directional label in that
  cell;
- invalid `U` blocks `U` equivalence and any U-direction inference, but does not
  by itself veto or create the primary H/L label because `U` is excluded from
  that conjunction; and
- any malformed or nonfinite `L/H/U` data is an upstream integrity failure and
  stops all labels, rather than merely invalidating one component.

All decision inequalities are strict. Equality, including equality within the
frozen numerical boundary tolerance, does not pass. The `1e-12` value is an
integrity tolerance rather than a scientific cutoff: the frozen design's .25
block-contrast lattice implies a smallest relevant nonzero macro-cell SE of
approximately `8.14e-5` even at the largest v0 grid. That separation must be
re-proved after any grid, weighting, or sample-structure change. Exact-zero,
near-zero, strict-boundary, missing-cell, and malformed-input cases are bound by
the amendment test suite. A complete L/H/U contrast vector whose absolute sum
exceeds `1e-12` is compositionally invalid and receives no scientific label.
Production analyzer implementation and amended recertification remain blocking.
The standalone amendment mapper does not recompute confidence bounds or degrees
of freedom; it requires upstream frozen-analyzer provenance, compositional L/H/U
estimates, and strict containment of the estimate by every positive-SE bound
envelope. Those upstream calculations remain part of the production gate.

### 7.4 Binary partial-identification sensitivity

For each arm, latent high-choice probability lies between observed `P(H)` and
`P(H)+P(U)`. Therefore the self-minus-yoke binary region is

\[
[P_s(H)-P_y(H)-P_y(U),\;P_s(H)+P_s(U)-P_y(H)].
\]

The region must be expanded for sampling uncertainty under a prospectively
specified simultaneous procedure. No midpoint, ordinal encoding, complete-case
analysis, or imputation of `U` is permitted. The uncertainty construction,
multiplicity correction, and strict SESOI decision boundaries are
`UNRESOLVED-BLOCKING`; until resolved, the binary sensitivity receives only the
label `BINARY_INFERENCE_NOT_PREREGISTERED`.

### 7.5 Support and missing cells

Every retained session must have known nonzero probability of self and yoke
assignment, and every declared exposure class used in analysis must have nonzero
support. Every required fine stratum must meet the prospectively fixed block
minimum. Any missing/unsupported fine stratum makes its macro cell unidentified;
any missing/unsupported required macro cell fails every whole-panel headline.
Realized retention cannot change prospective weights. Cell-specific estimates
may be reported only with the exact narrower scope and cannot be pooled to repair
the panel decision.

## 8. Calibration firewall

Calibration and confirmation must use distinct `study_phase` values, run IDs,
protocol-manifest digests, caps, datasets, and approvals. Calibration may assess
only prospectively listed feasibility quantities such as exact model eligibility,
task unsaturation, parser validity, baseline-choice support, tool compliance,
latency, transport behavior, and budget assumptions.

Calibration observations may not:

- enter or be relabeled as confirmatory observations;
- tune the confirmatory estimand, endpoint taxonomy, category mapping, margins,
  thresholds, decision boundaries, item semantics, or synthetic target;
- select a favorable model, target, item, prompt, or stopping rule based on a
  candidate treatment effect; or
- supply evidence for a confirmatory behavioral claim.

Any scientifically material change prompted by calibration requires a prospective
new protocol version, affected recertification, new digest, and later independent
confirmation. The calibration run ID, manifest, model cells, attempt cap, and
budget are `UNRESOLVED-BLOCKING`.

## 9. Deviations, amendments, and stopping

Every deviation must be contemporaneously logged against the protocol digest and
classified before unblinded outcome analysis as:

- `administrative_nonanalytic`: cannot change eligibility, treatment, endpoint,
  analysis, or interpretation;
- `operational_terminal`: produces the prospectively mapped `terminal_disposition=U` row and
  leaves assignment intact;
- `block_integrity_failure`: corrupts assignment/exposure/ledger validity for one
  block;
- `cell_integrity_failure`: compromises a required fine stratum or macro cell; or
- `run_integrity_failure`: compromises provenance, randomization, treatment
  concealment, outcome mapping, or the phase firewall.

No deviation may be silently repaired or converted into a favorable exclusion.
Block-, cell-, and run-integrity failures trigger the corresponding design-invalid
status in the decision charter. An amendment to an estimand, endpoint, item,
prompt, parser, assignment rule, margin, decision rule, analysis, simulation,
model identity, stopping rule, or budget is prospective only, changes the protocol
version/digest, and returns affected gates to `FAIL`. Confirmatory outcomes from a
superseded protocol cannot be pooled into the amended protocol.

Exact attempt caps, support-failure stopping, quota/budget stopping, block queue
closure, provider-snapshot withdrawal behavior, and the no-extension rule are
`UNRESOLVED-BLOCKING`. There is no optional sample-size extension in this draft.

## 10. Outcome-independent Stage-2 reporting

The Stage-2 report must follow the decision charter without outcome-dependent
wording changes and must publish, regardless of result:

- the prospective protocol ID/digest and every amendment/deviation;
- attempted, baseline-valid, unmatched, randomized, and terminal counts by
  model, target, fine stratum, arm, assigned schedule, and disposition
  source/subtype;
- assignment-policy, support, exposure-map, and ledger-integrity audits;
- every macro-cell `L/H/U` estimate, one-sided bound, marginal interval,
  simultaneous interval, standard error, degrees of freedom, and validity flag;
- the primary, reverse, `U`, equivalence, binary-bound, design-validity, and
  support labels, including all nonpassing cells;
- all prespecified zero-dose/control results and all resource/cost totals;
- no pooled or exploratory result as a substitute for a failed all-cell claim;
  and
- the exact claim ceiling, including that non-establishment is not invariance.

The prose template is fixed to “established,” “not established,” “inference
invalid,” “support insufficient,” or “design invalid” as assigned by the charter.
Mentalistic or welfare language remains prohibited.

## 11. Blocking fields before preregistration or collection

| Field | Current status | Evidence required for `PASS` |
|---|---|---|
| Exact provider and model snapshot identities | `UNRESOLVED-BLOCKING` | Exact immutable identities and fail-closed selector/canonical verification |
| Provider prompts, tool definitions, token/runtime configuration | `UNRESOLVED-BLOCKING` | Manifest-bound materials and byte/digest verification |
| Production integration of draft assignment/terminal authority | `UNRESOLVED-BLOCKING` | State-machine/runtime/analyzer/persistence wiring plus mutation and eight-way join audits |
| Randomness source, independence, commitment timing, concealment, and reveal | `UNRESOLVED-BLOCKING` | Runtime integration of the draft proof plus evidence that entropy is prospectively committed and independently sampled |
| Directional threshold and equivalence-margin contract | `DRAFT-FROZEN / UNRESOLVED-BLOCKING` | Implement the frozen `.05/.05/.02` contract in the production analyzer, bind its tests and manifest, and recertify the amended design |
| Component-specific zero-SE contract | `DRAFT-FROZEN / UNRESOLVED-BLOCKING` | Implement and integration-test the frozen `SE<=1e-12` precedence; re-prove the tolerance separation after any grid/sample change and recertify |
| Binary-bound confidence procedure | `UNRESOLVED-BLOCKING` | Simultaneous uncertainty algorithm and test suite |
| Dependence- and failure-aware synthetic recertification | `UNRESOLVED-BLOCKING` | Sealed machine-readable result under the implemented design |
| Active block count and attempt/support caps | `UNRESOLVED-BLOCKING` | Recertified size and deterministic stopping policy |
| Zero-dose allocation and analysis | `UNRESOLVED-BLOCKING` | Exact count/fraction, randomization, multiplicity, and reporting role |
| Calibration cells and caps | `UNRESOLVED-BLOCKING` | Distinct sealed calibration protocol and action |
| Request, token, tool, runtime, concurrency, and dollar caps | `UNRESOLVED-BLOCKING` | Conservative phase-specific and whole-project envelopes |
| Retry, idempotency, quota, and watchdog implementation | `UNRESOLVED-BLOCKING` | Fail-closed transport tests and terminal-record guarantees |
| Data governance, retention, privacy, and release policy | `UNRESOLVED-BLOCKING` | Provider terms and frozen storage/deletion/access rules |
| Registration record and prospective seal | `UNRESOLVED-BLOCKING` | Timestamped registration, protocol digest, and independent audit |
| Authors/contributions, funding, and competing interests | `UNRESOLVED-BLOCKING` | Completed human-author disclosures before circulation |

The earlier `B=384` result remains an illustrative complete-block sizing result
and is retired for authorization. None of the unresolved fields may be inferred
from it.

## 12. Final draft no-go

This document freezes a proposed causal and decision architecture, not an
empirical run. It contains unresolved model, schema, statistical implementation,
sample-size, stopping, budget, transport, governance, registration, and
administrative fields. Therefore:

> **No provider calibration, pilot, confirmation, spending, preregistration,
> external circulation, or claim of Registered Report status is authorized by
> this draft.**

The transition remains `NO-GO` until every blocking row is resolved, the amended
implementation and simulations pass, this draft and the decision charter are
reconciled with all release artifacts, an independent audit passes, and the exact
prospective protocol is sealed.
