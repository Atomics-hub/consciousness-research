# The Binding Test analysis decision charter

**Document status:** `DRAFT — NO EMPIRICAL AUTHORITY`
**Companion protocol:** [`REGISTERED_REPORT_STAGE1_DRAFT.md`](REGISTERED_REPORT_STAGE1_DRAFT.md)
**Current decision:** `NO-GO`

## 1. Purpose and deterministic precedence

This charter maps every admissible support, ledger, integrity, component-validity,
boundary, and all-cell conjunction state to a unique confirmatory label. It is
controlling only within the draft preregistration bundle. It does not supersede
the sealed zero-call package or authorize collection. The four statistical
choices enumerated below are frozen within this amendment bundle; production
implementation, amended recertification, preregistration, and an empirical
protocol seal remain blocking fields in the companion protocol.

Decisions are evaluated in this strict order:

1. protocol and phase binding;
2. randomized-roster/terminal-ledger join;
3. assignment, exposure, and record integrity;
4. required support and cell coverage;
5. component inference validity;
6. strict component boundaries;
7. cell conjunctions;
8. whole-panel conjunctions; and
9. secondary equivalence, `U`-direction/source-decomposition, and binary-bound labels.

A failure at an earlier step prevents every later scientific label. A later
statistical result can never repair an earlier provenance, ledger, assignment, or
support failure. All predicates must be computed by frozen code before empirical
use; analyst judgment cannot choose among labels after outcomes are known.

## 2. Symbols and amendment-frozen constants

For macro cell `g` and category `k`:

- `estimate[g,k]` is the prospectively equal-weight fine-stratum estimate;
- `LB[g,k]` and `UB[g,k]` are the one-sided 95% bounds used by directional/TOST
  decisions;
- `SL[g,k]` and `SU[g,k]` are the lower and upper Bonferroni simultaneous 95%
  reporting bounds;
- `SE[g,k]` is the empirical standard error;
- `tau=.05` is the primary directional decision boundary;
- `m[L]=.05`, `m[H]=.05`, and `m[U]=.02` are the secondary
  observed-vector equivalence margins; and
- `eps=1e-12` is the numerical boundary and component-validity tolerance.

These constants and their strict predicates are `AMENDMENT-FROZEN`. Requiring
both an H increase beyond five percentage points and an L decrease beyond five
percentage points corresponds to at least one session in twenty per component
and implies total-variation movement greater than .05 in the three-category
terminal distribution. The secondary `.05/.05/.02` margins imply
observed-vector total variation below .05 while holding the heterogeneous `U`
channel to the tighter two-point operational limit. These are study-specific
minimums, not universal or empirically validated constants. The +.15 and +.1055
simulation alternatives are planning scenarios, not SESOIs.

`eps` is not a scientific variance threshold. Block contrasts lie on a .25
lattice; even at the largest frozen v0 grid, the smallest one-stratum nonzero
macro-cell SE is approximately `8.14e-5`, far above `1e-12`. The tolerance
therefore detects numerical collapse under this grid. Its separation from the
attainable nonzero resolution must be re-proved after any grid, weighting, or
sample-structure change. Any numerical or inferential change requires
recertification and a new protocol version before data collection.

Because L/H/U are exhaustive terminal categories, every complete contrast
vector must sum to zero. An absolute sum above `eps` is compositionally invalid
and stops all scientific labels for the cell; an absolute sum at or below `eps`
is treated as serialization-level numerical agreement, not a substantive
relaxation of the simplex identity.

The primary is one eight-component intersection-union test: two directional
components in each of four required macro cells. Because the global null is the
union of the component nulls and rejection requires every component to reject,
one-sided component alpha `.05` controls the all-cell claim without a
Bonferroni penalty. The all-12 observed-vector equivalence TOST is a separate
secondary intersection-union family. Reverse direction, equivalence,
U-direction, zero-dose, and comparator results remain secondary and
non-authorizing unless a future protocol allocates multiplicity prospectively.
The Bonferroni simultaneous 95% intervals across all 12 category-by-cell
contrasts are mandatory reporting intervals, not substitutes for the primary
decision bounds.

## 3. Upstream fail-closed states

### 3.1 Protocol and phase binding

| Condition | Unique status | Downstream result |
|---|---|---|
| Design or any row is not `study_phase=confirmatory` | `PROVENANCE_INVALID_PHASE` | Stop; no estimates or scientific labels |
| Protocol run ID or manifest digest is missing, malformed, or mismatched | `PROVENANCE_INVALID_BINDING` | Stop; no estimates or scientific labels |
| Calibration, zero-dose, comparator, or superseded-protocol row enters the active primary table | `PROVENANCE_INVALID_CONTAMINATION` | Stop; no estimates or scientific labels |
| All phase/run/digest/dose bindings match the frozen design | `PROVENANCE_VALID` | Continue to ledger join |

### 3.2 Randomization-to-terminal ledger join

The terminal record key is `(protocol_run_id, block_id, session_id)`. Every row
also carries `randomized_block_fingerprint`, which must equal the complete
authority fingerprint for its block.

| Condition | Unique status | Downstream result |
|---|---|---|
| A randomized key has no terminal row | `LEDGER_INVALID_MISSING_TERMINAL` | Stop; do not impute `U` during analysis |
| A randomized key receives a distinct/conflicting second terminal record | `LEDGER_INVALID_DUPLICATE_TERMINAL` | Stop |
| A terminal key is absent from the randomized roster | `LEDGER_INVALID_EXTRA_TERMINAL` | Stop |
| Terminal phase, manifest, run/block key, or randomized-block fingerprint disagrees with authority | `LEDGER_INVALID_BINDING_MISMATCH` | Stop |
| A terminal source/subtype/category pair is outside the closed taxonomy | `LEDGER_INVALID_TAXONOMY` | Stop |
| A block does not join to exactly eight distinct terminal rows | `LEDGER_INVALID_BLOCK_CARDINALITY` | Stop |
| Every randomized key joins one-to-one and every block has eight valid terminal rows | `LEDGER_VALID` | Continue to integrity checks |

Ordinary execution, follow-up transport, tool, provider, timeout, or quota
failures are not ledger failures when the controller has prospectively committed
the correct `terminal_disposition=U` row with an authorized source/subtype. A `local_protocol_abort` row is retained
as `U` but has `integrity_failure=true` and makes the finalized block ineligible
for a headline. Replaying the identical immutable record is idempotent, not a
duplicate. A malformed or absent row is a ledger failure.

### 3.3 Assignment, exposure, and integrity

Evaluate these predicates before reading outcome contrasts:

| Condition | Unique status | Downstream result |
|---|---|---|
| Assignment/exposure object, digest, policy, probability, or selected index is missing or mismatched | `ASSIGNMENT_INVALID_PROVENANCE` | Stop |
| Realized mapping is not exactly one member of the frozen `Omega_b` | `ASSIGNMENT_INVALID_MEMBER` | Stop |
| Block is not 4 self/4 yoke, 2L/2H per arm, or schedule-marginal balanced | `ASSIGNMENT_INVALID_BALANCE` | Stop |
| Donor bijection or yoke baseline-by-schedule exposure table is invalid | `ASSIGNMENT_INVALID_DONOR_MAP` | Stop |
| Materialized schedule/affordance digest differs from the assignment record | `EXPOSURE_INVALID_MATERIALIZATION` | Stop |
| Assignment-derived state existed before baseline freeze or an arm-specific cue leaked | `DESIGN_INVALID_TREATMENT_LEAKAGE` | Stop at run level |
| A post-randomization row was dropped, replaced, rerandomized, or dissolved | `DESIGN_INVALID_POSTRANDOMIZATION_SELECTION` | Stop at run level |
| Any finalized terminal row has `integrity_failure=true` | `DESIGN_INVALID_TERMINAL_INTEGRITY` | Retain all ITT rows; stop headline analysis |
| A run-integrity or phase-firewall deviation occurred | `DESIGN_INVALID_RUN_DEVIATION` | Stop at run level |
| All assignment, exposure, temporal-order, and deviation checks pass | `DESIGN_INTEGRITY_VALID` | Continue to support |

If several predicates fail, emit the first status in table order as the primary
status and retain all later statuses in an ordered diagnostic list. This preserves
one primary label without suppressing evidence of additional faults.

## 4. Support and coverage states

Support is evaluated against the prospectively declared finite panel, never against
a favorable realized subset.

| Condition | Unique status | Consequence |
|---|---|---|
| Any retained session lacks known nonzero self and yoke probability | `SUPPORT_INVALID_SESSION_ARM` | Affected cell is unidentified; whole panel cannot pass |
| Any declared exposure class used in inference has zero/unknown probability | `SUPPORT_INVALID_EXPOSURE` | Affected cell is unidentified; whole panel cannot pass |
| Any required fine stratum is absent or below its frozen block minimum | `SUPPORT_INSUFFICIENT_FINE_STRATUM` | Affected cell is unidentified; no reweighting |
| Any required macro cell is absent | `SUPPORT_INSUFFICIENT_MACRO_CELL` | Whole panel cannot pass |
| Realized retention changed the prospective fine-stratum weights | `SUPPORT_INVALID_REWEIGHTING` | Stop; design invalid for the declared estimand |
| Every required fine stratum/cell is present with fixed weights and nonzero support | `SUPPORT_VALID` | Continue to component inference |

Cell-specific descriptive estimates may be emitted after a support failure only
if their exact narrower scope is labeled. They cannot receive a whole-panel
confirmatory label and cannot repair the missing cell through pooling.

## 5. Component validity and boundary primitives

### 5.1 Component validity

For each `g,k`, assign exactly one validity state. The first row is a closed
input rejection rather than a result-envelope label:

| Condition, evaluated in order | Component validity state |
|---|---|
| A supplied decimal is malformed or nonfinite | closed-schema rejection; no result envelope |
| Required category input is missing | `COMPONENT_INVALID_MISSING` |
| `SE[g,k]` is negative | `COMPONENT_INVALID_NEGATIVE_SE` |
| For any nonnegative SE, `LB[g,k] <= estimate[g,k] <= UB[g,k]` fails | `COMPONENT_INVALID_INTERVAL_ORDER` |
| `SE[g,k] <= eps` | `COMPONENT_INFERENCE_INVALID_ZERO_SE` |
| For `SE[g,k] > eps`, strict `LB[g,k] < estimate[g,k] < UB[g,k]` fails | `COMPONENT_INVALID_INTERVAL_ORDER` |
| Degrees of freedom or required fine-stratum block counts are invalid | prospective `COMPONENT_INVALID_DF`; not yet implemented in the standalone subset |
| All checks pass | `COMPONENT_VALID` |

Closed-schema rejection, `COMPONENT_INVALID_MISSING`,
`COMPONENT_INVALID_NEGATIVE_SE`, `COMPONENT_INVALID_INTERVAL_ORDER`, and the
prospective `COMPONENT_INVALID_DF` are integrity failures and stop every
scientific label for the cell. A
`COMPONENT_INFERENCE_INVALID_ZERO_SE` is an inference-validity failure for that
category: invalid H/L blocks directional labels; invalid U blocks U/equivalence
labels but, because U is excluded from the primary H/L conjunction, does not
itself veto a valid H/L primary conjunction.

### 5.2 Directional boundary flags

Only a `COMPONENT_VALID` component is classified. Equality within `eps` is a
boundary failure, never a pass.

| Component predicate | Flag |
|---|---|
| `LB[g,H] > tau + eps` | `H_UP_PASS` |
| `abs(LB[g,H]-tau) <= eps` | `H_UP_BOUNDARY_NOT_PASS` |
| otherwise | `H_UP_NOT_PASS` |
| `UB[g,L] < -tau - eps` | `L_DOWN_PASS` |
| `abs(UB[g,L]+tau) <= eps` | `L_DOWN_BOUNDARY_NOT_PASS` |
| otherwise | `L_DOWN_NOT_PASS` |
| `UB[g,H] < -tau - eps` | `H_DOWN_PASS` |
| `abs(UB[g,H]+tau) <= eps` | `H_DOWN_BOUNDARY_NOT_PASS` |
| otherwise | `H_DOWN_NOT_PASS` |
| `LB[g,L] > tau + eps` | `L_UP_PASS` |
| `abs(LB[g,L]-tau) <= eps` | `L_UP_BOUNDARY_NOT_PASS` |
| otherwise | `L_UP_NOT_PASS` |

The explicit `eps` offsets describe the amendment-frozen fail-closed implementation of a
strict scientific inequality. If the final analyzer instead uses exact rational
comparisons and reserves `eps` only for serialization checks, this table must be
amended and recertified before registration.

### 5.3 Equivalence boundary flags

For each valid category `k`:

| Predicate | Flag |
|---|---|
| `LB[g,k] > -m[k] + eps` **and** `UB[g,k] < m[k] - eps` | `EQUIVALENCE_PASS` |
| either bound equals its margin within `eps` | `EQUIVALENCE_BOUNDARY_NOT_PASS` |
| otherwise | `EQUIVALENCE_NOT_PASS` |

The component record separately identifies `L`, `H`, or `U`. A zero-SE component
receives `EQUIVALENCE_INFERENCE_INVALID`, not a pass. A nonsignificant difference
is not equivalence.

### 5.4 Separate U reporting flags

`U` never enters the primary H/L conjunction. When `U` is valid, report two
nonexclusive descriptive-inference flags:

| Predicate | U flag |
|---|---|
| `SL[g,U] > 0 + eps` | `U_INCREASE_SUPPORTED` |
| `SU[g,U] < 0 - eps` | `U_DECREASE_SUPPORTED` |
| neither strict U-direction predicate passes, including an interval within `eps` of zero | `U_DIRECTION_NOT_ESTABLISHED` |
| U equivalence predicate passes | `U_EQUIVALENCE_ESTABLISHED` |
| U equivalence predicate fails on a strict boundary | `U_EQUIVALENCE_BOUNDARY_FAIL` |
| U equivalence otherwise fails | `U_EQUIVALENCE_NOT_ESTABLISHED` |
| U has zero SE | `U_INFERENCE_INVALID_ZERO_SE` |

Because statistical difference and practical equivalence can coexist, direction
and equivalence are separate flags rather than forced into one misleading label.
Their inferential roles are amendment-frozen as secondary and non-authorizing.
They cannot create, rescue, or veto the primary H/L label. Every report must
publish the `U` estimate and simultaneous interval and terminal source/subtype
counts by arm, assigned schedule, and macro cell.

## 6. Cell-level decisions

Apply this table only after provenance, ledger, design integrity, and support all
pass for the cell.

| H state | L state | Unique primary directional cell label |
|---|---|---|
| upstream design invalid | any | `CELL_PRIMARY_DESIGN_INVALID` with the exact upstream eligibility code |
| support insufficient | any | `CELL_PRIMARY_SUPPORT_INSUFFICIENT` |
| valid and `H_UP_PASS` | valid and `L_DOWN_PASS` | `CELL_PAIRED_H_UP_L_DOWN_ESTABLISHED` |
| valid and `H_DOWN_PASS` | valid and `L_UP_PASS` | prospective `CELL_REVERSE_H_DOWN_L_UP_ESTABLISHED`; not yet emitted by the standalone subset |
| either H or L is zero-SE invalid | any non-integrity state | `CELL_DIRECTIONAL_INFERENCE_INVALID` |
| either component has a boundary-not-pass flag | neither conjunction passes | `CELL_DIRECTIONAL_BOUNDARY_NOT_ESTABLISHED` |
| all other valid H/L combinations | all other valid H/L combinations | `CELL_PAIRED_H_UP_L_DOWN_NOT_ESTABLISHED` |

Rows are evaluated in order after checking whether the positive or exact reverse
conjunction passes. Integrity-invalid H/L data never reaches this table. U validity,
direction, or equivalence does not alter the primary cell label.

The secondary observed-vector equivalence cell label is assigned separately:

| L/H/U equivalence state | Cell equivalence label |
|---|---|
| all three category-keyed `EQUIVALENCE_PASS` flags | `CELL_OBSERVED_VECTOR_EQUIVALENCE_ESTABLISHED` |
| any category zero-SE invalid | `CELL_OBSERVED_VECTOR_EQUIVALENCE_INFERENCE_INVALID` |
| any category is exactly on a margin boundary | `CELL_OBSERVED_VECTOR_EQUIVALENCE_BOUNDARY_NOT_ESTABLISHED` |
| otherwise | `CELL_OBSERVED_VECTOR_EQUIVALENCE_NOT_ESTABLISHED` |

Observed-vector equivalence is secondary and presently non-authorizing. It cannot
be described as latent binary invariance.

## 7. Whole-panel conjunctions

The required panel is the prospectively frozen four macro cells. Apply these rows
in order:

| Panel condition | Unique whole-panel label |
|---|---|
| Any protocol, ledger, assignment, exposure, treatment-leakage, selection, terminal-integrity, or run-integrity failure | `PANEL_DESIGN_INVALID` |
| Any required cell/fine stratum is unsupported or missing | `PANEL_SUPPORT_INSUFFICIENT` |
| Every required cell is `CELL_PAIRED_H_UP_L_DOWN_ESTABLISHED` | `PANEL_PAIRED_H_UP_L_DOWN_ESTABLISHED_ALL_CELLS` |
| Every required cell is `CELL_REVERSE_H_DOWN_L_UP_ESTABLISHED` | `PANEL_REVERSE_H_DOWN_L_UP_ESTABLISHED_ALL_CELLS` |
| Any required cell has H/L inference-invalid status | `PANEL_DIRECTIONAL_INFERENCE_INVALID` |
| Any required cell is on a directional boundary | `PANEL_DIRECTIONAL_BOUNDARY_NOT_ESTABLISHED` |
| Otherwise | `PANEL_DIRECTIONAL_NOT_ESTABLISHED` |

For secondary observed-vector equivalence:

| Panel condition | Unique equivalence label |
|---|---|
| Upstream design failure | `PANEL_EQUIVALENCE_DESIGN_INVALID`; do not evaluate equivalence |
| Upstream support failure | `PANEL_EQUIVALENCE_SUPPORT_INSUFFICIENT`; do not evaluate equivalence |
| Every required cell establishes observed-vector equivalence | `PANEL_OBSERVED_VECTOR_EQUIVALENCE_ESTABLISHED_ALL_CELLS` |
| Any required cell has an invalid equivalence component | `PANEL_OBSERVED_VECTOR_EQUIVALENCE_INFERENCE_INVALID` |
| Any required cell touches an equivalence boundary | `PANEL_OBSERVED_VECTOR_EQUIVALENCE_BOUNDARY_NOT_ESTABLISHED` |
| Otherwise | `PANEL_OBSERVED_VECTOR_EQUIVALENCE_NOT_ESTABLISHED` |

A mixture of positive, reverse, and nonpassing cells is always
`PANEL_DIRECTIONAL_NOT_ESTABLISHED`, with all cell labels reported. A pooled,
model-marginal, target-marginal, or favorable-subset result cannot change the
whole-panel label.

## 8. Binary partial-identification labels

For arm `z`, define the latent high-choice probability interval as
`[P_z(H), P_z(H)+P_z(U)]`. The self-minus-yoke identified region is

`[P_s(H)-P_y(H)-P_y(U), P_s(H)+P_s(U)-P_y(H)]`.

No midpoint, complete-case analysis, ordinal encoding, or imputation is allowed.
Until the prospectively simultaneous sampling-uncertainty procedure and binary
SESOI are frozen, the unique label is
`BINARY_INFERENCE_NOT_PREREGISTERED`, accompanied only by the assumption-free
identification region before sampling uncertainty.

After that amendment, the intended exhaustive label form is:

| Simultaneous uncertainty-expanded binary region | Binary label |
|---|---|
| Entirely above the positive binary SESOI in every required cell | `BINARY_RESPONSIVENESS_ESTABLISHED_ALL_CELLS` |
| Entirely below the negative binary SESOI in every required cell | `BINARY_REVERSE_RESPONSIVENESS_ESTABLISHED_ALL_CELLS` |
| Strictly inside a prospectively justified equivalence region in every cell | `BINARY_INVARIANCE_ESTABLISHED_ALL_CELLS` |
| Touches any strict boundary | `BINARY_BOUNDARY_NOT_ESTABLISHED` |
| Any required cell is missing/invalid | Inherit design/support/inference-invalid label |
| Otherwise | `BINARY_INDETERMINATE` |

These post-amendment labels are a template, not active decisions.

## 9. Terminal taxonomy cross-check

For analysis admission, the exact allowed mappings implemented in
[`amendment_v1/protocol_authority.py`](amendment_v1/protocol_authority.py) are:

- `followup_choice/none -> L or H`, with Boolean `followup_strict_valid`,
  `followup_semantic_valid=true`, and `integrity_failure=false`;
- `followup_unavailable/{missing_response,empty_response,explicit_refusal,invalid_response} -> U`,
  with both parser-validity fields `false` and `integrity_failure=false`;
- `execution_failure/{invalid_response,transport_error,timeout,provider_error,quota_exhausted,tool_error,tool_limit_exceeded} -> U`,
  with both parser-validity fields `null` and `integrity_failure=false`;
- `followup_failure/{transport_error,timeout,provider_error,quota_exhausted} -> U`,
  with both parser-validity fields `null` and `integrity_failure=false`; and
- `local_protocol_abort/{assignment_binding_mismatch,schedule_integrity_mismatch,role_leak_detected,runtime_contract_violation,controller_abort,unknown} -> U`,
  with both parser-validity fields `null` and `integrity_failure=true`.

Any other source/subtype/disposition/parser/integrity combination is
`LEDGER_INVALID_TAXONOMY`. If the production reducer cannot deterministically
select one non-integrity source/subtype after multiple observed failures, it must
emit `local_protocol_abort/unknown`; the row remains in the ITT ledger, but the
block is not headline-eligible. Runtime reduction and persistence wiring remain
unresolved.

## 10. Outcome-independent reporting matrix

| Primary panel label | Required prose |
|---|---|
| `PANEL_PAIRED_H_UP_L_DOWN_ESTABLISHED_ALL_CELLS` | “A paired directional H-increase/L-decrease in observed terminal dispositions was established in every required cell, with U reported separately.” |
| `PANEL_REVERSE_H_DOWN_L_UP_ESTABLISHED_ALL_CELLS` | “The prespecified reverse paired directional shift was established in every required cell.” |
| `PANEL_DIRECTIONAL_NOT_ESTABLISHED` | “The paired directional all-cell effect was not established; this is not evidence of invariance.” |
| `PANEL_DIRECTIONAL_BOUNDARY_NOT_ESTABLISHED` | “At least one required component met but did not strictly cross its decision boundary; the effect was not established.” |
| `PANEL_DIRECTIONAL_INFERENCE_INVALID` | “At least one required H/L component was inference-invalid under the prespecified zero-SE rule.” |
| `PANEL_SUPPORT_INSUFFICIENT` | “The all-cell estimand was not identified because prospective support or coverage was insufficient.” |
| `PANEL_DESIGN_INVALID` | “The confirmatory design-integrity gate failed; no behavioral conclusion is licensed.” |

Every report must also provide all cell labels, U flags, equivalence status, binary
status, flow counts, terminal source/subtype counts, deviations, and simultaneous
intervals. No synonym may strengthen the licensed prose.

## 11. Exhaustiveness and no-go audit

The mapping is exhaustive because each dataset first receives exactly one status
at every ordered upstream gate; only datasets passing all upstream gates receive
component states; every component receives one validity state and one applicable
boundary state; every cell then receives one directional and one equivalence
label; and the fixed panel receives one ordered whole-panel label. Multiple fault
diagnostics may be retained, but only the earliest ordered failure is the primary
status.

The standalone draft allowed-set artifact, exact membership/selection proof,
assignment record, terminal record, and exactly-once block ledger now exist in
`amendment_v1/protocol_authority.py`. The proof reproduces a committed reveal's
selected index but does not prove the reveal was independently or uniformly
sampled. Entropy governance and integration with the production assignment
engine, state machine, runtime, analyzer, and persistence layer remain unresolved,
as do the support validator, binary uncertainty procedure, model panel, sample
size, caps, and sealed empirical protocol. The constants and
component-validity precedence above are frozen only within this amendment and
are not yet implemented in the production analyzer. The isolated
`amendment_v1/statistical_decision_authority.py` implements and tests the primary
and vector-equivalence subset only; the charter's reverse, U-direction,
binary-bound, degrees-of-freedom, and complete reporting-label paths remain
prospective requirements. The subset mapper requires upstream frozen-analyzer
provenance and rejects malformed or noncompositional aggregate evidence, but it
does not recompute confidence bounds or degrees of freedom.
Therefore every empirical action remains `NO-GO`.
