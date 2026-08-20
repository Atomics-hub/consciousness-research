# Required protocol amendments before any provider collection

**Status date:** 2026-08-08  
**Current decision:** **NO-GO**  
**Scope of “provider collection”:** any calibration, pilot, confirmation, or other request that could elicit a model response or create an empirical provider/model observation.

This checklist is controlling for the transition from the zero-call construction study to any empirical phase. It records unresolved design and release gates; it is not an execution plan or spending authorization. **No provider collection is authorized until every mandatory item below has a documented `PASS`, the amended protocol is sealed, and the specific proposed run receives a separate action-specific approval.** A general authorization, an earlier approval hash, or completion of the zero-call package cannot substitute for those conditions.

The current `B=384` result is a conditional complete-block sizing benchmark. It is not an empirical sample-size authorization and must not be used as one until the amended design is recertified.

## Pass rule and evidence record

Every mandatory item must have all four fields in the final gate record:

1. **Frozen decision:** the exact rule or object being adopted, including version or digest.
2. **Implementing artifact:** the code, schema, protocol section, or search log that enforces the decision.
3. **Verification evidence:** a passing test, deterministic audit, or human sign-off that can detect noncompliance.
4. **Disposition:** `PASS`, `FAIL`, or `BLOCKED`; silence and “planned” count as `FAIL`.

Any post-seal change to an estimand, endpoint mapping, item, prompt, parser, assignment rule, margin, decision rule, analysis, simulation process, provider identity, stopping rule, or budget returns the affected gates to `FAIL` and requires a new protocol digest.

## Draft progress record — not a gate disposition

The following work narrows several design gaps, but it is not production integration, a complete empirical protocol freeze, recertification, or gate passage. The implementation artifacts under `amendment_v1/` and the two Stage-1 planning authorities are explicitly **DRAFT**. The endpoint and enumerated statistical decisions are frozen within that amendment bundle only. Passing local tests do not make any gate below a `PASS` under the four-part rule above.

| Gate | Current draft progress | Evidence | Remaining blocker to `PASS` |
|---|---|---|---|
| 1. Intention-to-treat terminal disposition | **Amendment-frozen and tested standalone; NOT PASS.** A closed draft authority maps every authorized source/subtype to exactly one `terminal_disposition`, retains `disposition_source` and `failure_subtype`, flags local protocol aborts through `integrity_failure`, and defines an exactly-once eight-row ledger. | `amendment_v1/protocol_authority.py`; `amendment_v1/tests/test_protocol_authority.py`; combined amendment suite. | Integrate and test the authority in the production state machine, runner, persistence, recovery, schema, analyzer, and sealed empirical manifest; recertify the resulting design. |
| 2. Full assignment/exposure/interference schema | **Tested standalone draft; NOT PASS.** The draft verifies the byte-pinned assignment source, recomputes the exact ordered 576-member canonical set, enforces exact session arm/yoke-exposure marginals, and binds the full eight-row assignment, selected index/member digest, uniform-policy digest, engine, commitment, and reveal-based selection proof. | Same draft authority and tests. | Integrate the exact object and terminal-row joins into production; freeze the complete exposure map and estimand implementation; govern reveal generation, timing, custody, and audit. The proof reproduces the commitment/context/index relation but does not prove that entropy was independently or uniformly generated. |
| 3. Statistical decision rules | **Amendment-frozen and machine-tested; NOT PASS.** The authority freezes the `.05` paired H/L boundary, exclusion and separate reporting of `U`, `.05/.05/.02` secondary equivalence margins, `SE<=1e-12` component invalidity, strict boundary precedence, and the primary/vector-equivalence label subset. | `amendment_v1/statistical_decision_authority.py`; its focused tests; `REGISTERED_REPORT_STAGE1_DRAFT.md`; `ANALYSIS_DECISION_CHARTER.md`. | Implement the charter's remaining reverse, U-direction, binary-bound, degrees-of-freedom, and reporting-label paths; integrate all rules in the production analyzer and reporting pipeline; recertify the amended design; preregister it; and seal the empirical protocol. |
| 4. Synthetic recertification | **Non-gating diagnostic completed; NOT PASS.** A seeded synthetic screen exercises the restricted assignment, shared shocks, and stochastic block formation. | `amendment_v1/dependence_diagnostics.py`; `amendment_v1/results/dependence_diagnostics.json`; diagnostic tests in the 63-test combined amendment suite. | The artifact declares `gate_effect=none` and `numerical_gate_eligible=false`; it is not a sample-size or power certification. Complete the amended DGP grid, terminal-failure mechanisms, temporal/provider stressors, resource frontiers, selection logic, Monte Carlo uncertainty, and sealed trust root. |

## Gate 1 — Intention-to-treat terminal disposition

- [x] **Choose and freeze the primary post-randomization endpoint.** Every randomized session has one nominal terminal disposition in `{L,H,U}`. Parsed follow-up choices contribute `L/H`; every authorized non-choice source/subtype contributes `terminal_disposition=U` while retaining non-ordinal source/subtype fields. A fourth primary failure category is rejected for this amendment and would require a new estimand, margins, multiplicity plan, and recertification.
- [x] **Freeze an exhaustive terminal-failure taxonomy and mapping.** The closed source/subtype mapping in `amendment_v1/protocol_authority.py` is the amendment authority. `local_protocol_abort` retains a `U` row and sets `integrity_failure=true`; missing or ambiguous rows may not be imputed by the analyst. Production reducer integration remains unchecked below.
- [ ] **Guarantee exactly one terminal analysis row for every randomized session.** The row must retain the original randomized assignment even when execution never starts, stops partway, or no follow-up is presented.
- [ ] **Forbid outcome-dependent removal.** A failed randomized session may not be dropped, replaced, rerandomized, used to dissolve its assigned block, or converted into a new baseline attempt. Block analysis must follow the frozen intention-to-treat rule.
- [ ] **Amend and test the state machine and closed schema.** Terminal execution/transport paths must emit the required analysis record, `disposition_source`, and `failure_subtype`. Tests must cover every terminal branch, duplicate events, malformed events, crash recovery, and the invariant of eight terminal records per randomized eight-session block.
- [ ] **State the estimand population precisely.** Preserve separate counts for attempted, baseline-valid, randomized, and finite-panel inference populations, including invalid baselines and unmatched valid leftovers. The primary enforcement-policy estimand is over the prospectively supported randomized population, not all attempted sessions or all deployed models.

**Fail condition:** any randomized session can disappear from the primary dataset or lack a deterministic terminal category.

## Gate 2 — Full assignment, exposure, and interference schema

- [ ] **Freeze the complete block assignment object.** For each block preserve `A_b`, the allowed set `Omega_b` (or its exact digest and version), assignment policy `pi_b`, selection probability, randomization seed/material, and the realized donor-aware mapping.
- [ ] **Freeze the session exposure map.** Each terminal row must preserve block, macro cell, fine stratum, baseline choice, arm, received schedule, match/mismatch status, donor identity or donor slot, counterbalance variant, item pair, and all assignment-derived affordances needed to reconstruct `E_sb(A_b)`.
- [ ] **Verify assignment support before collection.** Every retained session must have known nonzero probability of both self and yoke assignment; every declared exposure class used in inference must have nonzero support. The 4-self/4-yoke, 2-low/2-high-per-arm, schedule-marginal, and yoke-balance invariants must be machine-checked.
- [ ] **Freeze the interference estimand.** Define potential terminal dispositions under the full donor-aware assignment, compute block self-minus-yoke category contrasts, average over the frozen assignment policy, and then apply the prospectively fixed fine-stratum and macro-cell weights. Label this an allocation-policy estimand under partial interference, not an unrestricted individual direct effect.
- [ ] **Retain auditability of the randomization.** The confirmatory artifact must permit reconstruction of the realized full assignment and exposure mapping without consulting mutable runtime state or confidential provider transcripts.

**Fail condition:** inference can be reproduced only from a session-level treatment bit, or the realized donor/yoke relationships cannot be reconstructed.

## Gate 3 — Statistical decision rules

- [x] **Freeze directional wording and the role of `U`.** In every required macro cell, the H lower bound must be strictly above `+.05+eps` and the L upper bound strictly below `-.05-eps`. The licensed claim is only “paired H-increase/L-decrease in observed terminal dispositions, with U reported separately.”
- [x] **Freeze exclusion of `U` from the primary conjunction.** `Delta_U` cannot create, rescue, or veto the H/L primary but must always be reported with its simultaneous interval and terminal source/subtype decomposition. Pure L-to-H, availability-invariant, conditional-choice, or unqualified choice-policy wording is forbidden.
- [x] **Freeze the zero-standard-error rule.** `SE<=1e-12` makes that component inference-invalid. Invalid H/L blocks directional labels; invalid U blocks U/vector-equivalence labels but not an otherwise valid H/L primary. Equality and the epsilon boundary neighborhood never pass. The tolerance is an integrity guard below attainable frozen-grid resolution and must be re-proved after any grid/sample change.
- [x] **Freeze margins and SESOI rationale.** `tau=.05` is the study-specific H/L boundary; `.05/.05/.02` are secondary L/H/U equivalence margins. The paired primary implies total-variation movement above .05; the equivalence margins hold observed-vector total variation below .05 and U within two points. +15 and +10.55 remain planning alternatives, not scientific constants.
- [ ] **Freeze binary-bound uncertainty.** Specify the confidence procedure for the partially identified binary contrast, the worst/best assignment of `U`, simultaneous multiplicity correction, strict-boundary behavior, and the rule for indeterminate results. No midpoint, ordinal encoding, or complete-case imputation of `U` is permitted.
- [ ] **Freeze missing-cell and support behavior.** Any unsupported required fine stratum or macro cell must fail every whole-panel headline. Realized retention may not silently reweight the estimand.

**Fail condition:** the same observed vector can receive different headline labels under undocumented handling of `U`, component `SE<=1e-12` inference invalidity, missing cells, or equality at a margin.

## Gate 4 — Synthetic recertification of the amended design

- [ ] **Replace the independent-arm planning shortcut with the actual restricted assignment.** Simulate the 576-element donor-aware assignment policy, shared schedules, and induced self/yoke cross-arm dependence at the block level.
- [ ] **Model terminal failures under the amended endpoint.** Include arm-dependent, schedule-dependent, donor/recipient-correlated, and block-correlated execution and transport failures, plus follow-up refusal/invalidity. Exercise the exact frozen `disposition_source` and `failure_subtype` mapping.
- [ ] **Add provider and temporal dependence.** Include provider/batch-wide shocks, snapshot or route changes, temporal autocorrelation/drift, and common tool or transport outages across blocks and macro cells.
- [ ] **Simulate block formation rather than only complete active blocks.** Generate attempts, semantic-validity rates, choice positivity, fine-stratum support, unmatched leftovers, stopping behavior, and request consumption. Confirm that no outcome-dependent replacement or reweighting occurs.
- [ ] **Exercise plausible joint mechanisms.** Include unavailability/failure rates beyond the original marginal `U × ICC` grid, schedule- and arm-dependent availability, cross-arm donor-yoke effects, heterogeneity across fine strata, and stress cases at decision boundaries.
- [ ] **Rerun every positive, reverse, equivalence, and false-control family.** Retain Monte Carlo replicate floors, report Wilson uncertainty, and add false controls targeted to the new failure and dependence mechanisms. A generic-mechanism alias must remain incapable of supporting a workload-specific mechanism claim.
- [ ] **Recompute resource frontiers.** Report active blocks, attempts, sessions, requests, tool calls, tokens, runtime, and dollars under the amended stopping and failure processes. The original `B=384` benchmark remains retired for authorization purposes unless the amended grid selects and verifies it anew.
- [ ] **Seal the recertification trust root.** Bind source digests, seed derivation, environment information, simulation configuration, all required cells, replicate counts, selected-size logic, and machine-readable results.

**Fail condition:** any headline or sample-size choice relies only on complete blocks, independent self/yoke arm counts, or a failure-free provider process.

## Gate 5 — Calibration, model eligibility, controls, and stopping

- [ ] **Freeze exact provider/model eligibility.** Record the exact eligible snapshot identifier, provider routing/fallback policy, context/tool capabilities, and an administrative or prompt-free catalog check showing an exact selector-to-canonical-identity match. Aliases that can silently fall back or walk down are prohibited.
- [ ] **Freeze identity verification and fail-closed behavior.** A missing, mismatched, mutable, or unverified model identity must stop before prompt release. No retry, selector substitution, or resume is allowed after an ambiguous dispatch without a newly sealed action.
- [ ] **Freeze immutable experimental materials.** Bind the exact baseline, execution, and follow-up prompts; item bank; counterbalance and allocation tables; tool definitions; semantic parser; strict parser; schema; runner; and assignment engine to the protocol manifest.
- [ ] **Predeclare calibration scope.** Give calibration its own run identifier, manifest, maximum attempts, cells, measurements, and stopping rule. Calibration may assess exact model eligibility, unsaturation, semantic validity, baseline choice positivity, tool compliance, latency, transport, and budget assumptions only.
- [ ] **Maintain the phase firewall.** Calibration observations may not tune confirmatory estimands, margins, decision boundaries, item semantics, synthetic targets, or enter the confirmatory dataset. Any scientifically material change prompted by calibration requires an amended protocol, new recertification where affected, and a new digest.
- [ ] **Freeze maximum attempts and stopping.** Specify attempt caps by model, target, fine stratum, calibration/confirmation phase, and whole run; define support-failure stopping; define treatment of unmatched valid baselines; forbid replacement after outcome observation; and specify deterministic behavior when quotas or budgets halt the run.
- [ ] **Freeze zero-dose allocation and analysis.** State its prospective fraction/count, randomization and counterbalance rules, estimand or diagnostic, multiplicity/reporting treatment, stopping behavior, and whether it contributes to support or headline decisions.
- [ ] **Either freeze a valid credibility comparator or omit it.** If included, predeclare its burden neutrality, semantic/salience audit, allocation, analysis, and interpretation. If omitted, the claim ceiling remains an enforcement-policy effect and cannot become a workload-control-specific mechanism claim.

**Fail condition:** a model alias, calibration result, quota event, leftover session, control allocation, or comparator can alter the confirmatory sample or interpretation through an unfrozen decision.

## Gate 6 — Budgets, retries, deviations, and approvals

- [ ] **Freeze resource envelopes.** Set hard caps for provider requests, generated and submitted tokens, tool calls, task work, wall-clock/runtime, concurrent sessions, and dollars, separately for calibration, confirmation, controls, and the whole project.
- [ ] **Resolve billing assumptions.** Document prices and date, failed-request billing, cache reads/writes, tool-loop charging, retries, cancellation, taxes/credits if relevant, and how uncertain charges are conservatively bounded.
- [ ] **Freeze retry and transport semantics.** State retry-zero behavior or an exact bounded retry policy before dispatch; define idempotency and duplicate handling; require ambiguous dispatch to halt; and ensure a quota or watchdog stop yields terminal records without silently continuing.
- [ ] **Freeze a deviation and amendment policy.** Classify protocol deviations, require contemporaneous logging, prohibit silent repair, define which deviations invalidate a block/cell/run, and require a new version and digest for prospective amendments. Deviations may be reported but cannot be post hoc transformed into exclusions that favor a headline.
- [ ] **Require stage-specific, action-specific approval.** A sealed calibration package and a later sealed confirmation package require separate approvals that name the exact action digest, protocol digest, run identifier, caps, and ordered risk acknowledgements. Prior or general approval is not reusable.

**Fail condition:** the run can exceed a cap, retry or resume ambiguously, or change analysis/collection behavior without a logged and prospectively approved amendment.

## Gate 7 — Reproducible literature and novelty audit

- [ ] **Rerun the literature search at protocol freeze.** Record the search date, databases and gray-literature sources, complete queries, filters, forward/backward citation chasing, and exact searched cutoff.
- [ ] **Archive a screening log.** For every plausible collision, record stable identifier/URL, full citation, version/date, inclusion decision, and a concise reason keyed to the five-feature conjunction claimed by the manuscript.
- [ ] **Verify the named adjacent works from primary sources.** Confirm bibliographic metadata and the scope of Wang et al., Tagliabue and Dung, Moraski, and any later located work; do not rely on search-result snippets or secondary summaries.
- [ ] **Keep novelty language conditional.** The maximum permitted statement is that no study combining the frozen five features was located in the documented searched record through the cutoff. It is not proof of absence or unrestricted priority.
- [ ] **Predeclare collision handling.** A collision narrows or removes the novelty statement without changing the estimand, endpoint, or statistical design. Any substantive design change returns the relevant gates to `FAIL`.

**Fail condition:** a priority or novelty claim appears without a reproducible search artifact and primary-source screening record.

## Gate 8 — Release verification and seal

- [ ] **Reconcile every manuscript claim to evidence.** Update the claim–evidence ledger for the intention-to-treat limitation, full-assignment policy estimand, conditional nature of sizing, binary indeterminacy, literature status, and exact no-go conditions.
- [ ] **Regenerate all release tables and figures.** Run the deterministic generator in a disposable location or check mode and verify byte identity against every checked-in table and figure. Resolve numbering, captions, and language so no figure or table calls conditional sizing a general certification.
- [ ] **Run the full local verification suite.** Verify the sealed zero-call manifest and scientific-source aggregate, all stable trust-root fields, amended state-machine/schema/analyzer tests, recertification outputs, internal links, and prohibited-path/symlink checks.
- [ ] **Complete release documentation.** The release index must enumerate every included artifact. The manuscript must include author/status metadata, funding, conflicts of interest, AI-assistance disclosure, data/code statement, and an ethics statement covering provider data governance, compute/resource costs, real-world tool restrictions, and dual-use communication risk.
- [ ] **Create a self-excluding release manifest only after all edits finish.** It must cover the exact intended release file set, exclude itself by rule, contain no raw external-model responses, subscription records, credentials, authentication state, or native transcripts, and pass the release verifier.
- [ ] **Record independent sign-off.** A final hostile review must confirm that all mandatory rows are `PASS`, citations and numerical claims trace to sealed evidence, the claim ceiling is preserved, and no unresolved blocker is hidden in prose.

**Fail condition:** the release cannot be reconstructed from its index and manifests, regenerated artifacts differ, a prohibited artifact is included, or a scientific claim lacks a sealed evidence path.

## Final go/no-go record

The empirical transition remains **NO-GO** unless the final record shows all of the following. Drafts, passing unit tests, and non-gating diagnostics are evidence of progress, not substitutes for the required final disposition.

| Mandatory gate | Current status (2026-08-08) | Required PASS | Evidence / remaining blocker |
|---|---|---:|---|
| 1. Intention-to-treat terminal disposition | `AMENDMENT-FROZEN / NOT PASS` | `PASS` | Standalone authority is tested; production state-machine, runner, persistence, recovery, schema, analyzer, and manifest integration remain unresolved. |
| 2. Full assignment/exposure/interference schema | `AMENDMENT-FROZEN / NOT PASS` | `PASS` | The byte-pinned canonical 576-member artifact, exact session marginals, uniform-policy digest, and membership/selection proof are tested; production joins, full exposure reconstruction, estimand integration, and entropy governance remain unresolved. |
| 3. Statistical decision rules | `AMENDMENT-FROZEN / NOT PASS` | `PASS` | The four delegated statistical choices are machine-tested; production analyzer/report integration, amended recertification, the binary-uncertainty procedure, preregistration, and the empirical protocol seal remain unresolved. |
| 4. Amended synthetic recertification | `NON-GATING DIAGNOSTIC / NOT PASS` | `PASS` | A seeded diagnostic exists with `gate_effect=none`; it does not recertify `B=384`, a stopping rule, or a resource envelope. |
| 5. Calibration/model/control/stopping freeze | `UNRESOLVED / NOT PASS` | `PASS` | Exact eligible identities, immutable materials, calibration scope, support/attempt stopping, zero-dose allocation, and comparator disposition remain unresolved. |
| 6. Budgets/retries/deviations/approval package | `UNRESOLVED / NOT PASS` | `PASS` | Provider/request/token/tool/runtime/dollar caps, billing assumptions, retry semantics, deviation policy, and a future action-specific approval package remain unresolved. |
| 7. Reproducible literature audit | `PARTIAL / NOT PASS` | `PASS` | A primary-source appendix exists, but the search must be rerun and its screening log frozen at protocol freeze with final collision handling. |
| 8. Release verification and seal | `INTERNAL STAGE-1 WRAPPER / EMPIRICAL NOT PASS` | `PASS` | This internal wrapper inventories, regenerates, verifies, and seals the draft progress artifacts, but they are not production-integrated or sealed as a complete empirical protocol; required human administrative disclosures also remain incomplete for circulation. |

Passing these gates establishes only that a bounded empirical proposal is ready for separate review. It does **not** itself authorize a provider request. Calibration and confirmation remain distinct phases; each requires a newly sealed, action-specific approval, and calibration data can never enter the confirmatory dataset.
