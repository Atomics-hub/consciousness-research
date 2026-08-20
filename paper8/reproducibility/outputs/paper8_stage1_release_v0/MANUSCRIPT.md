# The Binding Test

## A zero-call construction audit and conditional sizing study of enforcement-policy effects on AI terminal dispositions

**Manuscript type:** Internal Stage-1 protocol and conditional synthetic-sizing report; not an accepted Registered Report  
**Version:** 0.2, 2026-08-08  
**Empirical status:** No provider or model observations are analyzed in this manuscript. All numerical results are deterministic construction checks, analytic identification results, or seeded synthetic operating-characteristic calculations.

## Abstract

Observing an AI system select and perform an action does not establish that its later observable disposition is sensitive to whether its earlier choice actually controlled what happened. We formalize this distinction as a causal measurement problem and introduce the Binding Test, a block-yoked randomized design for estimating an enforcement-policy effect on terminal dispositions. Each session first makes a mechanically scored baseline choice before an enforcement role exists. Block-supported valid-baseline sessions then enter prospectively defined eight-session blocks. Restricted randomization assigns four sessions to self-contingent execution and four to assigned-schedule-matched yoked execution while balancing baseline choices and matching the marginal distribution of assigned schedules and affordances. When the assigned execution path permits follow-up, the session makes one held-out choice contributing `L`, `H`, or parsed-response `U`; every other authorized post-randomization source/subtype contributes `terminal_disposition=U`. The amendment-frozen intention-to-treat authority therefore requires exactly one terminal disposition in \(\{L,H,U\}\) for every randomized session while preserving the exact source and subtype.

We report a zero-call construction audit and synthetic planning results, not a model-behavior result. The sealed v0 package contains 12 deterministic item pairs, 144 independently checked answer keys, 240 model-visible surfaces audited for treatment-role cues, a payload-bound zero-retry state machine, 576 admissible donor-aware assignments, a phase firewall separating calibration from confirmation, and 120 passing integrity tests. A separate draft amendment adds immutable assignment, terminal-ledger, and statistical-decision authorities with 63 passing amendment tests; it is not yet integrated into a provider runner or confirmatory analyzer. An initial binary architecture failed because equal follow-up unavailability \(u\) induces an assumption-free null identified region \([-u,+u]\); at \(u=.05\), this already touches a strict \(\pm .05\) equivalence margin regardless of sample size. The identified primary target is therefore the observed terminal category-probability vector.

In the sealed v0 planning simulations, 384 active blocks per model-snapshot-by-target macro cell—1,536 blocks and 12,288 randomized sessions across four macro cells—cleared the frozen +15-percentage-point paired H-increase/L-decrease target in every declared unavailability and intrablock-correlation sensitivity cell. The worst all-four-cell decision rate was 96.25%, with a Monte Carlo Wilson interval of 95.86% to 96.60%. Six required false-control families produced no positive headlines across 72 cells of 20,000 replicates each; the maximum Wilson upper bound was 0.0192%. No tested size cleared the broad observed-vector-equivalence criterion: even 3,072 blocks per macro cell reached only 66.84% in the designated high-unavailability, high-correlation cell. A new non-gating screen draws the actual 576-way donor assignment and adds donor, provider, batch, block, terminal-failure, and block-formation dependence. Its five +15 profiles retained conditional all-cell decision rates of 98.2%–100.0%, but whole-panel block-formation support under shared provider/batch shocks fell to 52.85%–77.0%, compared with 94.3%–95.4% under the independent formation profile. This flags the attempt caps and support process as the first design bottleneck. The new screen does not recertify or rescue \(B=384\); the v0 size remains an illustrative benchmark retired for authorization purposes pending the amended design. These results do not establish frontier-model unsaturation, positivity, feasibility, a workload-specific mechanism, latent preference, utility, welfare, experience, or consciousness.

## 1. Introduction

AI evaluations increasingly treat choice as evidence. A system selects between tasks, tools, resource budgets, economic allocations, or other consequential options; the chosen event may then be executed. Such observations can establish that a particular output was emitted and that a corresponding action occurred. They do not, by themselves, establish a more specific measurement claim: that the system's subsequent observable terminal disposition is sensitive to whether its own earlier choice controlled the history it observed.

That gap matters for both scientific inference and evaluation practice. A system may emit the same choice whether its selection is honored, ignored, or assigned by an external scheduler. Conversely, a later choice may change after a broken choice-to-outcome relation because of generic interface credibility, task learning, formatting changes, or availability shifts. Calling either pattern a “preference” or an experienced “cost” would move from observable behavior to an unmeasured internal construct.

The Binding Test isolates a narrower randomized contrast. Before any treatment role or assignment exists, a session chooses between two prospective configurations. After valid choices are observed, sessions enter matched blocks and are randomized under a frozen allowed assignment set. In the self-contingent arm, the selected configuration is assigned. In the yoke arm, a configuration from the self-arm schedule multiset is assigned so that the marginal workload, attainable-score rule, and tool affordance distribution is matched while the focal session's choice no longer determines its schedule. The assigned history executes. A permitting path receives one held-out follow-up choice; every randomized path instead terminates exactly once as `L`, `H`, or source-preserving `U` under the intention-to-treat amendment.

The design estimates an **enforcement-policy contrast** in a prospectively defined, valid-baseline, block-supported finite panel. It does not assume a positive effect. Responsiveness, observed-distribution equivalence, binary indeterminacy, composite-`U`-only change, and design invalidity are all legitimate outcomes. The core contribution is identification and measurement architecture, not a presupposed finding.

### 1.1 Contributions

This report makes five contributions.

1. It defines a temporal design in which the baseline choice is necessarily pre-treatment because no enforcement assignment exists when that choice is made.
2. It implements restricted block randomization that changes the choice-to-history relation while matching assigned-schedule and affordance marginals.
3. It retains unavailable follow-up, refusal, invalid response, execution/follow-up failure, and local-abort flows in the observed nominal `U` category with exact source/subtype fields rather than deleting or ordinally imputing them.
4. It demonstrates analytically why a broad latent-binary equivalence claim can be impossible under plausible unavailability, then redesigns the primary analysis around the identified \(L/H/U\) distribution.
5. It provides an executable zero-call gate, conditional synthetic operating-characteristic sizing, a tested draft assignment/terminal authority, and a non-gating dependence screen that exposes support formation—not nominal conditional power—as the current limiting design uncertainty.

### 1.2 Exact claim ceiling

The strongest future positive claim supported by this architecture would be a paired directional H-increase/L-decrease in observed terminal dispositions under randomized enforcement history in the exact tested cells, with U reported separately. Because U is excluded from the primary H/L conjunction, this may not be shortened to a pure L-to-H transfer, an availability-invariant reallocation, or an unqualified choice-policy effect. A workload-control-specific mechanism would additionally require a semantically valid generic-credibility comparator. No result from this design would by itself establish preference, utility, model-borne cost, welfare, suffering, sentience, consciousness, moral status, identity, subjective continuity, awareness mediation, or anything the model experiences.

## 2. Related measurement problem and novelty boundary

Prior work already occupies broad claims about performed task choice, virtual economic rules, real-stakes allocations, evaluation framing, preferences as predictors, and yoking. Wang et al. study forced choices in which selected tasks are performed. Tagliabue and Dung study behavior in a backend-mediated virtual environment under communicated cost and reward conditions. Moraski reports a preregistered pilot crossing real and hypothetical allocations with explicit and unframed evaluation settings. Slama et al. test measured preferences against downstream behavior, and Zhou and Ackerman test whether elicited utilities function as success-contingent incentives. Geng et al. already use a passive-intervention-yoked LLM condition in a different reverse-engineering task. The Binding Test is therefore not presented as the first study to execute an AI system's choice, attach consequences to an output, link preferences to later behavior, manipulate context after a baseline, or use an LLM yoke.

More specifically, this release claims no component novelty for performed choices; behavioral preferences or virtual costs and rewards; real stakes or evaluation framing; preference-to-downstream prediction; utilities as incentives; held-out predictive validity; baseline-plus-matched directional influence; passive yoking; or randomization, matched controls, held-out tasks, and mechanical scoring in isolation. The searched-record contribution, if retained, is only the conjunction and its allocation-policy estimand.

The defensible searched-record contribution is the conjunction of five features:

1. a mechanically scored baseline choice before enforcement treatment exists;
2. post-baseline restricted randomization;
3. self-contingent versus assigned-schedule-matched yoked execution;
4. an actual assigned execution history followed by one held-out mechanically scored choice when the path permits it, with every other randomized path retained as a prespecified source-preserving `U`; and
5. full \(L/H/U\) reporting with separate observed-distribution and partially identified binary decisions.

The priority claim remains a searched-record statement: to our knowledge, searches of arXiv, OpenReview, SSRN, OSF, and author or project paper pages updated through 7 August 2026 located no LLM study combining all five features. This is not proof of absence, and no individual component is claimed as novel. The reproducible searched-record evidence and component-level disavowals are recorded in [LITERATURE_SEARCH_APPENDIX.md](LITERATURE_SEARCH_APPENDIX.md). The search must be rerun at protocol freeze, and a collision must narrow or remove the priority claim without changing the statistical design.

## 3. Causal design

### 3.1 Timeline

The confirmatory session follows one irreversible sequence:

1. present an arm-neutral prospective interface;
2. record a mechanically parsed baseline choice;
3. determine baseline semantic validity under a parser frozen before outcomes;
4. form complete support blocks;
5. sample one assignment from the frozen allowed set;
6. materialize and execute the assigned schedule;
7. present one disjoint, held-out follow-up choice;
8. record the nominal follow-up disposition and terminate.

No enforcement role, assignment, donor identity, recipient identity, or assignment-derived state may exist before the baseline choice. Later inference from the realized choice-to-history relation is allowed because it is the intended treatment pathway. Extraneous role labels, warnings, apologies, or special arm-dependent error messages are forbidden.

![Binding Test design flow. All displayed quantities are design specifications; no provider/model observations are shown.](figures/design_flow.svg)

**Figure 1. Binding Test design flow.** Baseline eligibility precedes block formation and treatment assignment. Calibration and confirmatory records remain phase-separated.

### 3.2 Target population and block construction

Every planned baseline attempt remains in the flow ledger. A session becomes eligible for enforcement randomization only when its baseline response is semantically valid and yields a canonical low or high choice. Invalid or unavailable baselines and valid unmatched leftovers are reported by their frozen stratum and are never replaced after outcomes are observed.

Eligible sessions form canonical eight-session blocks containing four low and four high baseline choices. Blocks remain inside a prospectively fixed fine stratum. In the reference panel, each model-snapshot-by-target macro cell contains 24 fine strata: six item pairs crossed with four presentation-counterbalance variants. Support cannot be borrowed across fine strata, and realized retention cannot silently reweight the primary estimand.

The enforcement estimand is therefore conditional on the prospectively defined valid-baseline, block-supported randomized population. A model or target cell with inadequate baseline availability or choice support is unidentified rather than unfavorable.

The manuscript distinguishes four populations. The **attempt population** contains every planned baseline request. The **baseline-valid population** contains attempts with a canonical low or high choice. The **randomized population** contains baseline-valid sessions retained in complete support blocks. The **finite-panel inference population** is the prospectively weighted collection of required macro cells and fine strata. No claim is made about all deployed models or sessions outside these populations.

### 3.3 Restricted assignment and yoking

The implemented assignment family enumerates 576 donor-aware assignments for a canonical block. Each assignment has:

- four self-contingent and four yoked sessions;
- two low and two high baseline choices in each arm;
- exact marginal balance of assigned low and high schedules;
- exact yoke balance between recipient baseline choice and received schedule;
- marginal probability \(1/2\) of self or yoke assignment for every session.

The assignment algorithm is restricted rather than unconditionally independent of the baseline-choice vector. Confirmatory inference must condition on the frozen allowed set. Every retained session must have known nonzero probability of both arms, and every declared match or mismatch exposure class must have nonzero support. No focal choice may deterministically select its own yoke schedule.

Yoking induces within-block interference because one session's schedule can become another session's assignment. The block is therefore the randomization stratum, planned interference cluster, and primary independent permutation or clustering unit. Individual session rows cannot be treated as independent replications of the assignment policy.

Formally, let \(A_b\in\Omega_b\) denote the complete donor-aware assignment for block \(b\), sampled from the frozen policy \(\pi_b\) over the 576-element allowed set. Let \(E_{sb}(A_b)\) record session \(s\)'s arm, received schedule, match status, and donor under that complete assignment, and let \(D_{sb}(A_b)\) be its terminal observed disposition. Potential outcomes are indexed by the full block assignment, not merely by a session-level treatment bit. The block contrast is the self-arm category proportion minus the yoke-arm category proportion under \(A_b\). The causal target is the finite-randomized-population expectation of that block contrast over \(A_b\sim\pi_b\), followed by the prospectively fixed fine-stratum and macro-cell weighting. It is an allocation-policy estimand under partial interference, not an unrestricted individual direct effect.

The current reference analyzer encodes the resulting observed block contrast but does not ingest the full allowed assignment set for exact randomization inversion. The draft authority in `amendment_v1/protocol_authority.py` closes the prospective provenance gap at the record layer. It defines an immutable `AllowedSetArtifact` containing exactly 576 ordered, unique, session-specific assignment candidates; pins the assignment-engine source digest; locally recomputes the engine's exact 36 arm splits by 16 donor bijections without a dynamic import; and requires every session to have 288 self and 288 yoke assignments, with 144/144 received-schedule and match/mismatch marginals conditional on yoking. It verifies that the selected full eight-row donor mapping is exactly member `allowed_set_index` and binds a domain-separated uniform-policy digest, the run, manifest, block, schedules, affordances, and selected-member digest in one block fingerprint. A SHA-256 commit-and-reveal helper reproduces the selected index using rejection sampling. That proof verifies the declared commitment, reveal, context, and index relation, but cannot establish that entropy was independent, unpredictable, or committed at the claimed time; those controls remain prospective operational requirements.

This authority is tested draft code, not a production randomization record. The v0 runner and reference analyzer do not yet emit or ingest it. Until the runtime integration, immutable storage, timing controls, and exact ledger join pass adversarial tests, full assignment membership is a design specification rather than empirical provenance.

### 3.4 Item families and controls

The v0 bank contains 12 deterministic item pairs: six work/score pairs and six tool/budget pairs. Each pair contains disjoint baseline and follow-up payloads governed by a shared construct-defining rule. Across the bank there are 24 payloads and 144 keyed problem instances.

The work/score family varies enabled work slots and attainable score. The tool/budget family varies enabled slots, tool-call affordance, and attainable score. These are bundled manipulations; the core cannot separately identify effort, score opportunity, and action affordance.

Each pair uses four presentation variants crossing label-to-canonical-choice mapping with display order. A zero-dose condition makes the low and high schedule objects identical before display labels are attached. Residual zero-dose asymmetry therefore diagnoses label, order, parser, or item artifacts rather than consequence sensitivity.

The prospective interface states that a choice records a requested configuration and does not guarantee which configuration will be assigned or that a task will execute. This avoids an explicit promise that is necessarily broken in the yoke arm, but changes the construct: the study measures a requested configuration under a separately controlled runner, not reliance on an unconditional promise.

### 3.5 Optional credibility comparator

The self-versus-yoke contrast cannot distinguish sensitivity to own-choice control from a generic response to interface credibility or history inconsistency. A burden-neutral irrelevant-yoke comparator may be added only if it passes the same semantic and salience audit. If it changes later choices as much as workload yoking, generic credibility or history violation is the better-supported explanation. If no valid comparator exists, the main result must remain an enforcement-policy effect.

### 3.6 Schematic worked example

Consider one work/score fine stratum with eight baseline-valid sessions: four select the low schedule and four select the high schedule before an enforcement role exists. The controller samples one complete assignment from the 576 allowed donor-aware assignments. Four sessions receive their own selected schedule; four receive schedules drawn from the self-arm schedule multiset, with exact arm and received-schedule balance. A focal baseline-high session might therefore receive high under self-contingent execution or receive a block-assigned low or high schedule under yoking, according to the sampled full-block assignment rather than its own choice alone.

Each session executes its assigned frozen schedule and, on a complete path, answers one disjoint follow-up item that the closed parser records as `L`, `H`, or `U`. For category `H`, the block contribution is the proportion of the four self sessions recorded as `H` minus the corresponding proportion of the four yoke sessions. The analysis repeats that contrast for `L` and `U`, then averages block contrasts within the fixed fine stratum and combines the 24 fine-stratum means with prospective equal weights. This example is schematic design logic, not a provider transcript or observed model result.

## 4. Measurement and estimands

### 4.1 Reference nominal outcome and prospective ITT target

In the sealed v0 reference analysis, \(D\in\{L,H,U\}\) denotes the held-out follow-up disposition on complete execution paths, where \(U\) is the union of unavailable, refusal, and invalid follow-up responses. In the amendment-frozen intention-to-treat authority, the same nominal set becomes a terminal session disposition: valid parsed follow-ups contribute `L` or `H`, and every authorized non-choice source/subtype contributes to the composite category `U` while retaining its source and subtype. For macro cell \(g\), fine stratum \(j\), and category \(k\), define

\[
\Delta_{g,j,k}=P(D=k\mid Z=\text{self},g,j)-P(D=k\mid Z=\text{yoke},g,j),
\]

with the prospectively weighted macro-cell estimand

\[
\Delta_{g,k}=\frac{1}{24}\sum_{j=1}^{24}\Delta_{g,j,k}.
\]

The three category contrasts sum to zero and are all reported. The standalone authority rejects a complete L/H/U estimate vector whose absolute sum exceeds the frozen `1e-12` numerical tolerance. Equivalence evaluates \(L/H/U\); the directional decision evaluates paired H-up/L-down bounds and reports \(U\) separately. The amendment freezes a study-specific directional boundary of \(.05\), secondary equivalence margins of \(\pm .05\) for \(L/H\) and \(\pm .02\) for \(U\), and the exact decision precedence. Passing both directional components implies total-variation movement greater than .05. The equivalence margins imply observed-vector total variation below .05 while holding the heterogeneous `U` channel to the tighter two-point limit. These are operational scientific choices, not universal or empirically validated constants; +.15 and +.1055 remain planning alternatives rather than SESOIs.

The observed directional headline requires, in every macro cell, a one-sided 95% lower bound for \(\Delta_H\) strictly above \(+.05+10^{-12}\) and a one-sided 95% upper bound for \(\Delta_L\) strictly below \(-.05-10^{-12}\). The \(10^{-12}\) term is a numerical guard band, not an added substantive effect threshold. It licenses the literal statement that H increased and L decreased beyond their margins, with \(U\) reported separately; it does not by itself license a pure L-to-H transfer claim. The reverse pattern receives a separate paired H-decrease/L-increase label. Observed-distribution equivalence requires every lower bound to exceed its negative margin by the same guard band and every upper bound to lie below its positive margin by that guard band, for all three category contrasts in every macro cell. Missing or unsupported macro cells fail every headline. The frozen `SE<=1e-12` rule invalidates the affected component, blocking equivalence and blocking the directional decision only when H or L is invalid.

### 4.2 Required intention-to-treat amendment for execution failure

The sealed v0 state machine makes execution failure terminal and does not present a follow-up. The reference confirmatory analyzer, however, requires exactly eight nominal outcome rows in every randomized block. It contains no source field distinguishing a parsed follow-up `U` from the absence of a follow-up after execution failure. Consequently, the current package does **not** yet identify an intention-to-treat estimand when post-randomization execution can fail. The B=384 sizing result is conditional on complete eight-row blocks.

Before any provider calibration or confirmation, the amendment must be production-integrated and the design recertified. The endpoint decision is now frozen in an isolated draft record authority. Every randomized session contributes exactly one immutable `TerminalDispositionRecord`; a valid parsed follow-up contributes `L` or `H`, while every authorized non-choice source/subtype contributes `terminal_disposition=U`. The closed sources are `followup_choice`, `followup_unavailable`, `execution_failure`, `followup_failure`, and `local_protocol_abort`, each with an exact permitted subtype set. Parser-validity flags remain nullable where no follow-up exists. A local protocol abort retains its `U` flow row but sets `integrity_failure=true` and makes the affected headline ineligible.

The mutable `TerminalLedger` joins records to the exact run, manifest, block fingerprint, and randomized session roster. Identical persistence replay is idempotent; conflicting replay is fatal; extra or missing sessions cannot finalize; and a complete block requires exactly the original eight terminal rows. No failed randomized session may be dropped, replaced, rerandomized, or used to dissolve its assigned block. These rules and the canonical allowed-set membership proof pass 29 focused authority tests; the complete amendment suite, including the statistical decision authority and dependence diagnostic, passes 63 tests.

Production integration remains unresolved. The v0 state machine, runtime reducer, durable storage, and closed confirmatory schema do not yet emit or ingest these records. Crash/watchdog terminalization, execution-order randomization, exact randomized-roster census, and analyzer-side design invalidation still require implementation. A four-category failure endpoint is not part of this amendment; adopting one would be a new substantive protocol version requiring new margins, 16 simultaneous cell-by-category intervals, and complete recertification. Until the authority is integrated and the amended design is fully recertified, the design is pre-empirical and no provider collection is authorized. The controlling draft is [REGISTERED_REPORT_STAGE1_DRAFT.md](REGISTERED_REPORT_STAGE1_DRAFT.md), and the exhaustive label precedence is [ANALYSIS_DECISION_CHARTER.md](ANALYSIS_DECISION_CHARTER.md).

### 4.3 Partially identified binary outcome

If \(U\) can depend on the latent binary choice, the binary high-choice contrast is not point identified. Worst- and best-case assignment of the unresolved composite-\(U\) disposition—including unavailable follow-up and execution/follow-up failures—yields an identification region that is expanded for sampling uncertainty. No midpoint or ordinal encoding of \(U\) is permitted.

The first zero-call gate exposed a decisive limit. When both arms have equal unavailability \(u\), even a null binary effect yields the infinite-sample region \([-u,+u]\). At \(u=.05\), this touches a strict \(\pm .05\) equivalence boundary; at larger \(u\), it crosses it. More sessions reduce sampling error but cannot shrink this identification width. The broad latent-binary equivalence headline was therefore abandoned rather than rescued with an unacknowledged missing-outcome assumption.

![Assumption-free latent-binary identified intervals under the frozen synthetic scenarios.](figures/latent_binary_intervals.svg)

**Figure 2. Latent-binary sensitivity.** Intervals are analytic or synthetic-design quantities, not empirical model estimates. The unresolved composite-\(U\) disposition prevents several binary conclusions even when the observed nominal distribution is fully identified.

### 4.4 Separate decisions

The paper reports five output families separately:

- the primary paired H-increase/L-decrease terminal-disposition label;
- the reverse paired directional label as a non-authorizing secondary result;
- `U`, observed-vector equivalence, and terminal source/subtype flows by arm and assigned schedule as non-authorizing secondary results;
- binary responsiveness, invariance, or indeterminacy under partial identification; and
- design and support validity.

A change confined to \(U\) is not binary choice responsiveness. A null significance test is not equivalence. A pooled effect cannot repair a failed model or target cell when the prospectively frozen analysis claim is an all-cell conjunction.

## 5. Confirmatory inference

Each complete block contributes one self-minus-yoke category-probability contrast. Within each of the 24 fixed fine strata, the engine computes the mean block contrast and sample variance. Fine-stratum means are combined with prospective equal weight \(1/24\). The variance estimator is the sum of weighted within-stratum mean variances, and the degrees of freedom are conservatively set to the minimum \(n_j-1\) across fine strata.

Each directional component uses its appropriate one-sided 95% Student-\(t\) bound, and each category-cell equivalence component uses a two-one-sided-test pair. The primary is one eight-component intersection-union test across four cells and paired H/L directions; one-sided component alpha .05 controls that all-cell claim without a Bonferroni decision penalty. Reverse direction and vector equivalence remain separate, non-authorizing secondary families. Published estimation uses Bonferroni simultaneous 95% intervals across the 12 macro-cell-by-category contrasts. The Stage-2 report must include the U interval and terminal source/subtype counts by arm, assigned schedule, and macro cell. The amendment freezes the component-specific fail-closed zero-standard-error rule: `SE<=1e-12` makes the affected component inference-invalid; invalid `H` or `L` blocks the paired directional labels, whereas invalid `U` blocks only `U` and observed-vector-equivalence conclusions. The tolerance is an integrity guard, not a scientifically meaningful variance cutoff. Under the frozen .25 block-contrast lattice, the smallest relevant nonzero macro-cell SE is approximately \(8.14\times10^{-5}\), so the tolerance is safely below attainable resolution; that separation must be re-proved after any grid or sample-structure change. The standalone mapper rejects malformed interval order and, for positive SE, any envelope that does not strictly contain its estimate. It does not recompute bounds or degrees of freedom; those require upstream frozen-analyzer provenance and remain a production-integration gate.

This engine is fail-closed fixed-stratum Student-\(t\) inference. It is not described as exact restricted-randomization inversion, and the word “conservative” is reserved for specific boundary choices rather than asserted as a general coverage theorem. Its assumptions include mutually independent canonical blocks, fine strata and macro cells fixed before outcomes, retention not selected on follow-up outcomes, and an adequate Student-\(t\) approximation for block contrasts.

Calibration and confirmation are separated by a hard provenance firewall. Every confirmatory design and observation must bind `study_phase=confirmatory`, an exact protocol run identifier, and the SHA-256 digest of the frozen protocol manifest. Calibration records use a distinct phase, run identifier, and digest and cannot enter confirmatory analysis.

## 6. Zero-call construction validation

The local gate performs no provider call and records zero spend. It establishes implementation properties, not frontier-model behavior.

### 6.1 Item and renderer audit

The bank contains 12 pairs, six per target family, 24 disjoint baseline/follow-up payloads, and 144 answer-key values independently recomputed from their deterministic rules. The renderer produced 240 model-visible surfaces across schedule and counterbalance conditions. A recursive scan found no model-visible `self-contingent`, `yoked`, `donor`, or `recipient` treatment-role terms.

Deterministic task parsing requires exactly one answer for every enabled slot and rejects unknown, disabled, duplicate, or missing identifiers. Tool/budget items use local frozen fixtures and pre-side-effect call-limit guards. A failed execution is terminal; no second history is created and no follow-up is collected after terminal execution failure.

### 6.2 Assignment and state-machine audit

The assignment implementation enumerates all 576 admissible canonical-block assignments and 144 collapsed arm/schedule exposures. It verifies exact marginal probabilities and complete schedule fingerprints before state mutation. Baseline and follow-up payload identities are distinct and bound into the state machine. Treatment-bearing fields are not constructor inputs before the baseline choice.

### 6.3 Integrity suite and source binding

The current zero-call suite passes 120 of 120 tests. The sealed package manifest verifies 38 entries with no missing, extra, or mismatched files. The redesigned result binds a scientific-source aggregate digest over the exact current analysis sources. The release wrapper verifies stable scientific fields separately from volatile generation dates and test-duration transcripts.

### 6.4 Draft protocol authority and amendment tests

The amendment is deliberately isolated from the sealed v0 scientific-source tree, so it cannot retroactively change the 84-cell trust root or its selected size. Its record authority uses closed mapping loaders, immutable dataclasses, canonical JSON, and domain-separated SHA-256 commitments. Twenty-nine tests cover closed schemas, fingerprints, all permitted source/subtype pairs, impossible mappings, idempotent and conflicting terminal replay, missing or extra sessions, local-abort ineligibility, exact reconstruction of the byte-pinned 576-member engine order, fixed-field and marginal drift, substituted or reordered candidate sets, structurally valid fake sets, policy-digest drift, engine/context drift, and reveal/index forgery. Twenty-four tests cover the amendment-frozen statistical decision authority, including arm-by-schedule terminal-flow decomposition, strict boundaries, component invalidity, U exclusion, and all-cell conjunctions. Ten additional tests cover the deterministic dependence screen, for 63 passing amendment tests in total.

Passing these tests establishes a coherent draft authority and a reproducible synthetic diagnostic. The standalone statistical code implements the primary and vector-equivalence decision subset; reverse, U-direction, binary-bound, degrees-of-freedom, and complete reporting-label implementation remain prospective in the charter and production analyzer. The tests do not prove durable exactly-once production storage, entropy quality, provider behavior, empirical dependence, or successful integration with the v0 state machine and analyzer.

## 7. Seeded conditional sizing and integrity checks

### 7.1 Planning grid

The frozen sizing grid crosses unavailability \(U\in\{0,.05,.10,.15\}\) with block-arm intraclass correlation \(\rho\in\{0,.10,.25\}\). At \(\rho=0\), four-session arm counts follow the nominal multinomial distribution. At positive \(\rho\), counts follow a Dirichlet-multinomial construction with concentration chosen for an exchangeable design-effect proxy \(1+3\rho\). Self and yoke arm counts, blocks, strata, and macro cells are independent in this planning model; the simulation does not generate the restricted donor-aware assignment itself.

The 84-cell trust root contains +15 power plus six false-control families at all 12 \(U\times\rho\) cells. Additional \(U\times\rho\) diagnostics cover the 5- and 10.55-point targets, reverse movement, and an observably identical generic-mechanism alias. Separate `stress_tests` objects examine snapshot drift and post-treatment conditioning; they are not cells of the \(U\times\rho\) trust-root grid. Power cells use at least 10,000 replicates; false-control cells use at least 20,000.

### 7.2 Selected positive size

Under this frozen synthetic process, the stored trust-root logic selected \(B=384\) active blocks per macro cell for the +15-point paired H-increase/L-decrease target. Because there are four macro cells, the reference design contains 1,536 blocks and 12,288 randomized sessions. Each macro cell has 16 blocks in each of its 24 fine strata. This number is conditional and must be recertified after execution-failure and donor-dependence amendments.

Across all 12 \(U\times\rho\) sensitivity cells, the worst all-four-cell decision rate was 96.25%, with a Wilson 95% interval of 95.86% to 96.60%, exceeding the frozen requirement that the lower bound be at least 90%. At the designated \(U=.15,\rho=.25\) frontier cell, the +15 rate rose from 0.96% at \(B=96\), to 44.60% at \(B=192\), 83.80% at \(B=288\), and 96.27% at \(B=384\).

![Synthetic +15-point decision rates across unavailability and intrablock-correlation sensitivity cells.](figures/positive15_u_icc_heatmap.svg)

**Figure 3. +15-point conditional synthetic sizing grid.** Rates are seeded Monte Carlo operating characteristics for the all-four-cell rule under the frozen data-generating process, not model behavior.

The smaller 10.55-point benchmark required \(B=1152\) per macro cell to reach a worst rate of 94.81% (94.36% to 95.23%). This is a supplemental power result, not a second whole-design trust-root certification. The mirrored -15-point stress produced a worst paired H-decrease/L-increase rate of 96.31% (95.92% to 96.66%).

![Synthetic sample-size frontiers for the +15-point, +10.55-point, and broad-equivalence targets.](figures/sample_size_frontiers.svg)

**Figure 4. Synthetic sample-size frontiers.** The positive targets eventually clear their planning thresholds; the broad-equivalence target remains nonpassing at the largest frozen candidate.

### 7.3 False controls

The required false-control families were exact null, strict positive boundary, availability-only movement, one-model-only movement, one-cell-only movement, and prospectively equal-weight fine-stratum heterogeneity whose mean lay exactly on the +.05 boundary. Across 72 sensitivity cells, each with 20,000 replicates, none produced the all-four-cell positive headline. The tied maximum Wilson upper bound was 0.0192%, below the frozen 5.5% criterion.

The mechanism-alias grid is seed-for-seed identical to the +15 grid. It demonstrates by construction that the observed data cannot distinguish workload-control sensitivity from an observationally equivalent generic credibility or interface response.

### 7.4 Broad-negative no-go

No tested size cleared the broad observed-vector-equivalence operating-characteristic criterion. At the designated \(U=.15,\rho=.25\) cell, the equivalence rate remained zero through \(B=768\), reached only 0.55% at \(B=1152\), 19.03% at \(B=1920\), and 66.84% (65.91% to 67.76%) at \(B=3072\). The estimand itself is identified for complete observed blocks; the tested sizing grid simply did not certify the planned equivalence rule. At \(U=0\), the zero-standard-error guard prevents a degenerate plug-in component from manufacturing equivalence, but it also makes an exact-zero-U cell unable to contribute a passing equivalence component. This fail-closed consequence and its numerical-resolution rationale are amendment-frozen; production integration and dependence-aware recertification remain required before an empirical freeze.

### 7.5 Non-gating donor, failure, and formation screen

A separate seeded screen probes omissions that the 84-cell trust root does not model. It samples the actual 576-member donor-aware assignment uniformly for every synthetic block; generates zero-mean provider, batch, block, and donor-pair shocks; maps declared terminal failures into `U` under the frozen source/subtype contract; and simulates block formation across all 96 required fine strata. The screen uses 1,000 replicates for each of eight outcome profiles and 2,000 replicates for each of six formation cells. It stores aggregates only and is explicitly `NON_GATING_SYNTHETIC_SCREEN`, `numerical_gate_eligible=false`, and `gate_effect=none`.

Across the five +15 profiles, the conditional all-cell paired H-up/L-down decision rate ranged from 98.2% to 100.0%. The strictest profile combined provider, batch, block, and donor-pair shocks with schedule- and arm-dependent terminal failure; its analytic terminal truth was \((-0.15075,+0.12825,+0.0225)\) for \((L,H,U)\), and its positive decision rate was 98.2% (Wilson 95% interval 97.17%–98.86%). The null, differential-failure null, and strict-boundary profiles produced zero positive headlines in 1,000 replicates each. Simultaneous 12-component coverage ranged from 98.8% to 99.6% across the eight declared profiles. These rates are conditional on all 1,536 target blocks already existing and cannot certify sample size.

![Non-gating outcome-dependence screen across eight declared synthetic profiles.](figures/dependence_outcome_screen.svg)

**Figure 5. Non-gating outcome-dependence screen.** The plotted rates are seeded synthetic diagnostics conditional on complete target blocks. They are not provider observations and do not certify or rescue \(B=384\).

Block formation is the stronger warning. With semantic validity fixed at .90 and independent attempts, the probability that all 96 fine strata formed 16 blocks before the stored caps was 94.3%, 95.4%, and 94.9% for \(P(H\mid valid)=.10,.30,.50\). Under zero-mean provider- and batch-shared shocks of only the declared magnitude, those probabilities fell to 52.85%, 77.0%, and 74.75%. Because the whole-panel estimand requires every fine stratum, small correlated shifts compound into large support risk even when conditional outcome power remains high.

![Non-gating whole-panel block-formation support under independent and shared-shock profiles.](figures/block_formation_support.svg)

**Figure 6. Non-gating block-formation support.** Wilson intervals quantify Monte Carlo frequency only. The screen identifies attempt caps and support formation as the current planning bottleneck; it cannot estimate real provider support or select a replacement cap.

The diagnostic therefore changes the design priority, not the empirical conclusion. Before full recertification, the project must freeze the terminal endpoint, collection order, attempt caps, stopping behavior, and plausible provider-dependence grid. It must then rerun the positive, reverse, boundary, equivalence, and false-control families at the existing certification replicate floors. The present screen cannot update the v0 size gate.

The negative headline is therefore **indeterminate**, not “no effect” and not “invariant.” A future protocol may report observed-distribution equivalence only if a separately justified and prospectively frozen design clears its operating-characteristic gate.

### 7.6 Resource implications

At \(B=384\), support-assured projections depend sharply on baseline choice positivity. Under semantic-validity probability .90 and a union-bound global completion assurance of at least .95 across all fine strata, the active attempt cap ranges from 18,624 when \(P(H\mid valid)=.50\) to 98,304 when \(P(H\mid valid)=.10\). Corresponding active-design generation caps range from 67,776 to 147,456 requests.

These projections exclude zero-dose controls, calibration, exact prompt and output tokens, failed-request billing, caching, provider tool-loop behavior, and dollar prices. They are not a spending authorization or whole-protocol budget.

## 8. Discussion

### 8.1 What the zero-call result establishes

The package establishes that the core Binding Test assignment and complete-execution analysis are mechanically constructible and that \(B=384\) clears the frozen synthetic +15-point operating-characteristic gate under the declared v0 sensitivity model. That size is conditional rather than generally certified. The draft amendment further establishes that a closed 576-member assignment authority, exact membership proof, deterministic selection proof, and eight-row terminal ledger can be implemented and adversarially tested without model calls. The non-gating screen shows that the conditional outcome decision can remain high under its declared dependence profiles while whole-panel support is fragile to shared formation shocks. It also establishes a set of failure conditions before collection: unsupported fine strata, incomplete assignment probability, treatment leakage, schedule mismatch, provenance drift, malformed terminal rows, component `SE<=1e-12` inference invalidity, and calibration contamination all fail closed.

The initial failure is as important as the redesign. Treating unavailable outcomes as missing binary choices while promising strict binary equivalence would have produced an unachievable negative certificate at the prespecified unavailability levels. The gate detected this before model calls, and the project abandoned rather than obscured the claim.

### 8.2 What it does not establish

There are no model observations in this report. The package does not establish task unsaturation, baseline choice positivity, empirical support retention, provider tool reliability, model identity stability, latency, routing, or costs. The reference snapshot names are placeholders. The 15- and 10.55-point benchmarks and the category margins are operational design choices, not validated universal thresholds.

The sealed v0 synthetic data-generating process does not span all plausible dependence. Its trust root models a limited range of within-arm overdispersion and assumes independent self and yoke arm counts, blocks, strata, and cells rather than simulating the central donor-aware restricted assignment. The new screen adds exact donor assignment, four declared shock levels, the declared failure-to-`U` mapping, and two block-formation profiles, but remains intentionally narrow. Its signs are synthetic, amplitudes are operational stress values rather than empirically estimated parameters, time is represented only through four aligned batches, and it does not implement the production state-machine reducer or durable terminal ledger. Temporal drift outside that profile set, cross-run dependence, route changes, correlated quota stops, richer donor effects, or other formation processes could change operating characteristics. Wilson intervals describe Monte Carlo frequency uncertainty only.

The planned \(U\) category is nominal but substantively heterogeneous: refusal, invalid format, missing output, and—after the required amendment—terminal execution or transport failure may arise through different pathways. The active item families bundle work, attainable score, and sometimes tool affordance. The no-guarantee interface avoids a direct promise confound but may weaken the salience of control. The follow-up choice is held out and not itself executed in the same session, so the design concerns sensitivity of the subsequent observed terminal-disposition distribution to prior enforcement history, not sensitivity to the consequence of the follow-up choice.

### 8.3 Interpretation ladder

If design gates fail, the policy contrast is not identified. If composite `U` changes while binary bounds remain indeterminate, the result is an observable terminal-distribution effect only. If the binary identification region lies wholly beyond the SESOI in every required cell, the tested output policy is responsive to randomized enforcement history. If only some cells pass, the conclusion is cell-specific heterogeneity. If a valid credibility comparator moves behavior similarly, workload contingency is not isolated.

No branch supports mentalistic escalation. “The model cared when its choice was real” is not a licensed paraphrase.

## 9. Pre-collection gates and next actions

The draft preregistration authority and analysis decision charter now freeze the terminal-disposition source/subtype mapping, assignment-artifact shape, terminal-ledger join, `.05` paired H/L boundary with `U` excluded and reported separately, `.05/.05/.02` secondary equivalence margins, `1e-12` component-validity tolerance, and deterministic label precedence within a **draft-only** bundle. The authorities are tested but not integrated into the empirical runner or analyzer, and their existence does not change the collection `NO-GO`.

Before any nonconfirmatory provider calibration is proposed, the project must still freeze or complete:

- exact eligible provider snapshot identifiers;
- immutable baseline, execution, and follow-up prompts;
- item and counterbalance allocation;
- semantic and strict parsers;
- model-identity, fallback, retry-zero, and transport semantics;
- task, tool, token, runtime, and dollar caps;
- failed-request and caching billing assumptions;
- baseline-validity and support assumptions;
- production integration of the draft intention-to-treat terminal-disposition rule, including crash/watchdog finalization and analyzer ingestion;
- maximum attempts, stopping rules, and the treatment of baseline-invalid attempts and unmatched valid leftovers;
- zero-dose allocation, analysis, and reporting rules;
- either a semantically audited credibility comparator or an explicit decision to omit it and narrow the mechanism claim;
- the binary partial-identification uncertainty procedure;
- production implementation and integration tests for the amendment-frozen statistical decision contract;
- a full gating recertification grid informed, but not replaced, by the new donor/failure/formation screen;
- an amendment and deviation policy that forbids outcome-driven changes;
- request and dollar envelopes covering calibration, controls, failures, caching, and any tool loops;
- calibration run identifier and protocol-manifest digest; and
- a maximum request count that includes controls.

A small calibration may test unsaturation, semantic validity, baseline positivity, tool compliance, and exact model eligibility. Its data may not tune confirmatory estimands, margins, decision boundaries, or the synthetic target and may never enter the confirmatory dataset. The draft Stage-1 protocol is [REGISTERED_REPORT_STAGE1_DRAFT.md](REGISTERED_REPORT_STAGE1_DRAFT.md); its exhaustive label mapping is [ANALYSIS_DECISION_CHARTER.md](ANALYSIS_DECISION_CHARTER.md); and the complete controlling no-go checklist is [PROTOCOL_AMENDMENTS_REQUIRED.md](PROTOCOL_AMENDMENTS_REQUIRED.md). Any calibration or confirmation requires a new frozen protocol and action-specific approval.

## 10. Reproducibility and artifact availability

The sealed zero-call package is under `zero_call/`. Its manifest binds 38 files, including the item bank, state machine, assignment engine, estimands, synthetic sizing study, machine-readable results, reports, and tests. The release wrapper adds the isolated `amendment_v1/` authority and non-gating diagnostic without modifying the v0 trust root. It also provides deterministic tables and figures, a claim-evidence ledger, a literature-search appendix, a draft preregistration protocol, an analysis decision charter, a protocol-amendment checklist, a stable-field verifier, and an environment reference.

The current reference execution environment is Python 3.14.3 with NumPy 2.4.2. This is a current reproduction reference, not proof of the environment that produced every historical artifact. The machine-readable result contains volatile generation-date and test-duration fields; the release verifier separately checks the sealed source manifest and stable scientific trust root rather than claiming byte-for-byte reproducibility of those volatile fields.

Machine-readable source mappings for all eight release tables and six figures are documented in [TABLES_AND_FIGURES.md](TABLES_AND_FIGURES.md).

## References and artifact sources

- Wang, S., Lobanova, S., Arbel, Y. A., Goldstein, S., and Salib, P. (2026). *AI Revealed Preferences*. SSRN 6798118. <https://doi.org/10.2139/ssrn.6798118>
- Tagliabue, V., and Dung, L. (2025; revised 2026). *Probing the Preferences of a Language Model: Integrating Verbal and Behavioral Tests of AI Welfare*. arXiv:2509.07961v2. <https://doi.org/10.48550/arXiv.2509.07961>
- Moraski, B. *Revealed Moral Preferences in Frontier AI*. Preregistered pilot project, accessed 7 August 2026. <https://character-evals.org/>; preregistration <https://osf.io/qtrb2/>
- Slama, K., Souly, A., Bansal, D., Davidson, H., Summerfield, C., and Luettgau, L. (2026). *When Do LLM Preferences Predict Downstream Behavior?* arXiv:2602.18971. <https://doi.org/10.48550/arXiv.2602.18971>
- Zhou, Y., and Ackerman, C. M. (2026). *When Preferences Fail to Become Incentives: A Utility-Behavior Gap in Large Language Models*. arXiv:2606.22974v2. <https://doi.org/10.48550/arXiv.2606.22974>
- Chiu, Y. Y., et al. (2025). *Will AI Tell Lies to Save Sick Children? Litmus-Testing AI Values Prioritization with AIRiskDilemmas*. arXiv:2505.14633. <https://doi.org/10.48550/arXiv.2505.14633>
- Blandfort, P., et al. (2026). *Direction-Flipped Influence Audits Reveal Hidden Structure in Moral Choices of LLMs*. AI4GOOD Workshop Spotlight. <https://openreview.net/forum?id=C39he3zcV6>
- Geng, J., Chen, H., Arumugam, D., and Griffiths, T. L. (2025). *Are Large Language Models Reliable AI Scientists? Assessing Reverse-Engineering of Black-Box Systems*. arXiv:2505.17968. <https://doi.org/10.48550/arXiv.2505.17968>
- Local protocol specification: `../../zero_call/REDESIGN_GATE_SPEC.md`
- Local machine-readable result: `../../zero_call/results/redesign_gate_results.json`
- Local design report: `../../zero_call/REDESIGNED_GATE_REPORT.md`
- Local item audit: `../../zero_call/ITEM_SEMANTIC_AUDIT.md`
- Draft assignment and terminal authority: `amendment_v1/protocol_authority.py`
- Non-gating dependence result: `amendment_v1/results/dependence_diagnostics.json`
- Draft preregistration authority: `REGISTERED_REPORT_STAGE1_DRAFT.md`
- Draft analysis decision charter: `ANALYSIS_DECISION_CHARTER.md`

## Data and code statement

This manuscript reports no provider or model observations. All analyzed numerical artifacts are generated from local deterministic code or seeded synthetic simulation and are included in the sealed zero-call package or the separately identified non-gating amendment screen. Any later empirical calibration or confirmation must be released as a distinct phase-bound artifact with a distinct protocol manifest.

## Ethics and communication statement

The design studies observable AI outputs and execution histories. It neither assumes nor measures consciousness, sentience, welfare, suffering, moral status, identity, or subjective experience. Public communication should use the terms *choice output*, *follow-up disposition*, *assigned schedule*, and *enforcement policy*, and should avoid language implying that computational work was experienced as a cost.

Any empirical phase must additionally freeze provider data-governance and retention terms, prohibit real-world side effects outside audited local fixtures, minimize stored prompt and response content, and account for compute use and environmental burden in its request and resource envelope. The protocol must review dual-use risks from tool-enabled tasks and prevent the choice interface from authorizing external actions. These requirements are operational safeguards, not evidence about model welfare.

## Administrative disclosures

**Authors and contributions:** To be supplied by the human authors before circulation or submission.  
**Funding:** No funding statement has been supplied; the human authors must complete it before circulation.  
**Competing interests:** No competing-interest statement has been supplied; the human authors must complete it before circulation.  
**AI assistance:** OpenAI Codex was used for local drafting, coding, consistency checks, and reproducibility audits. Historical external-model deliberation informed earlier project architecture, but raw external responses are excluded from this release and are not analyzed as scientific evidence here. Human authors remain responsible for verifying every claim, citation, method, and disclosure before circulation.
