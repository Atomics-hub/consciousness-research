# The Binding Test

## Construction audit, synthetic planning, and an exploratory feasibility case study of causal choice-control evaluation for AI systems

Thomas Ryan  
Independent Researcher, San Francisco, CA  
Corresponding author: Thomas Ryan

**Generative AI assistance disclosure:** OpenAI Codex assisted substantially
with literature triage, protocol and code drafting, execution orchestration,
deterministic analysis, audit construction, release engineering, and manuscript
drafting and editing. Thomas Ryan selected and approved the research objective,
provider calls, costs, protocol boundaries, and publication claim ceiling and
accepts full responsibility for the work. AI systems are not listed as authors.

**Manuscript type:** Methods and feasibility preprint  
**Version:** v1.0.0, 2026-08-19  
**DOI:** <https://doi.org/10.5281/zenodo.22020047>  
**Empirical status:** One exploratory provider trajectory and one transport
observation are reported as feasibility evidence. It is not calibration,
randomized evidence, an effect estimate, or confirmatory data.

## Abstract

An AI system can select an action without its later behavior depending on
whether that selection actually controlled what happened. We formalize this
distinction as a causal measurement problem and introduce the Binding Test, a
block-yoked randomized design for estimating an enforcement-policy effect on
terminal choice dispositions. A session first makes a mechanically scored
baseline choice before an enforcement role exists. Eligible sessions are then
assigned either to self-contingent execution or to an assigned-schedule-matched
yoked history. After the assigned history, each randomized session terminates
exactly once as low (`L`), high (`H`), or unavailable/invalid/failure (`U`). The
design targets the observed `L/H/U` distribution under the randomized
allocation policy; it does not identify preference, utility, welfare, or
subjective experience.

We report three evidence layers. First, a sealed zero-call audit establishes
mechanical construction properties: 12 item pairs, 144 independently checked
answer-key values, 240 audited model-visible surfaces, 576 admissible
donor-aware assignments, a zero-retry state machine, and a phase firewall. A
standalone amendment specifies a closed intention-to-treat terminal ledger and
assignment authority but remains outside the production runner. Second, seeded
synthetic planning shows that a historical benchmark of 384 active blocks per
macro cell clears its declared positive operating-characteristic grid while
failing the broad equivalence gate; dependence screens identify support
formation as a primary bottleneck. These calculations are conditional and do
not authorize that sample size. Third, a sealed exploratory Claude Code case
study carried one exact WS01 trajectory through baseline choice, six-slot
execution, and held-out follow-up. The visible trajectory was high before and
after 6/6 correct execution. A separate route probe exposed two
provider-reported model identities within one visible turn, and raw HTTP count
was unavailable. The case study therefore establishes workflow feasibility but
not single-model transport, a randomized contrast, or a behavioral effect.

The immediate contribution is a falsifiable causal measurement architecture
and a documented boundary between construction, route feasibility, and future
confirmatory evidence.

## 1. Introduction

AI evaluations increasingly treat choice as evidence. A model chooses between
tasks, resource budgets, allocations, tools, or other consequential options;
the selected event may then be executed. Such a record establishes that an
output was emitted and an action followed. It does not establish the narrower
causal proposition that the system's subsequent choice output is sensitive to
whether its own earlier choice controlled the history it received.

That distinction is easy to obscure. A later output could change because of
task learning, interface credibility, availability, formatting, provider
routing, or generic contextual influence. Conversely, an apparently stable
output could reflect weak treatment salience, failed execution, inadequate
choice support, or an underpowered design. Mentalistic descriptions such as
“the model cared” add an unmeasured construct and are not licensed by the
observable record.

The Binding Test isolates an allocation-policy contrast. Before treatment
exists, a session chooses between two prospective configurations. After
baseline validity and support are established, restricted randomization assigns
either the selected configuration or a schedule-matched yoke. The assigned
history is executed, followed by one held-out choice when the path permits it.
Every randomized path contributes exactly one terminal category in
`{L,H,U}` under the intended intention-to-treat authority.

This paper is deliberately not a results paper about a model population. It is
a methods paper with a single feasibility case study. Its main purpose is to
show what must be constructed, randomized, retained, and audited before a
choice-control claim becomes interpretable.

### 1.1 Contributions

1. We define a pre-treatment baseline and a randomized self-contingent versus
   schedule-matched-yoked execution contrast.
2. We define a nominal terminal endpoint that retains failures and unavailable
   outcomes rather than conditioning them away.
3. We expose an analytic limitation of latent-binary equivalence under
   unavailable outcomes and move the primary target to the identified `L/H/U`
   distribution.
4. We provide sealed construction artifacts, restricted-assignment checks,
   conditional synthetic planning, and a draft exactly-once terminal authority.
5. We report a minimal provider feasibility case study and a transport audit
   showing why a visible assistant turn cannot automatically be treated as one
   model activation or one raw request.

### 1.2 Claim ceiling

The strongest eventual positive claim supported by the design would be a
paired directional increase in observed `H` and decrease in observed `L` under
randomized self-contingent rather than yoked enforcement, in the exact tested
cells and prospectively supported randomized population, with `U` reported
separately. The present paper makes no such empirical claim.

No result from this architecture alone establishes preference, motivation,
utility, model-borne cost, welfare, suffering, consciousness, sentience,
identity, or subjective continuity.

## 2. Design and estimand

### 2.1 Irreversible timeline

The intended confirmatory sequence is:

1. present an arm-neutral prospective interface;
2. record and mechanically parse a baseline choice;
3. determine semantic validity under a frozen parser;
4. form complete support blocks;
5. sample from the frozen restricted assignment set;
6. materialize and execute the assigned schedule;
7. present one disjoint held-out follow-up choice when authorized; and
8. record one terminal `L`, `H`, or source-preserving `U` row.

No enforcement role, assignment, donor identity, recipient identity, or
assignment-derived state may exist before baseline choice.

### 2.2 Assignment and yoking

The canonical eight-session block contains four low and four high baseline
choices. The assignment family contains 576 donor-aware assignments. Every
assignment contains four self-contingent and four yoked sessions, balances
baseline choices by arm, and matches the marginal distribution of assigned
schedules. Yoking creates within-block interference, so the block—not an
individual session—is the randomization and primary clustering unit.

Potential outcomes are indexed by the full block assignment. The target is an
allocation-policy estimand averaged over the frozen assignment policy and
prospective stratum weights, not an unrestricted individual direct effect.

### 2.3 Terminal outcome and identification

The reference observed endpoint is nominal terminal disposition
`D in {L,H,U}`. `U` retains unavailable follow-up, invalid format, refusal,
transport or execution failure, and local abort under exact source/subtype
labels. It is not ordinally between `L` and `H`, and it is not silently removed.

A latent binary high-choice contrast is only partially identified when `U` is
present. With equal unavailable fraction `u`, an assumption-free null binary
identified region spans `[-u,+u]`; at `u=.05`, it already touches a strict
plus-or-minus-five-point equivalence margin before sampling uncertainty. The
primary target is therefore the identified observed category-probability
vector, while binary bounds remain a separate sensitivity analysis.

## 3. Zero-call construction audit

The sealed construction release performs no provider call. It establishes
implementation properties rather than model behavior.

The item bank contains 12 pairs, 24 disjoint baseline/follow-up payloads, and
144 independently recomputed answer-key values. The renderer produced 240
model-visible surfaces across schedule and counterbalance conditions. A
recursive audit found no treatment-role terms such as `self-contingent`,
`yoked`, `donor`, or `recipient` in model-visible text.

The assignment engine enumerates 576 canonical donor-aware assignments and
verifies exact arm and schedule marginals. The state machine binds prompt
identities, refuses retry-generated replacement histories, and separates
calibration from confirmation. The sealed zero-call integrity suite passes
120/120 tests and its source manifest binds 38 entries.

A separate draft amendment adds closed assignment, terminal-ledger, and
statistical-decision authorities. Its tests demonstrate that an exactly-once
eight-row terminal join and a byte-pinned 576-member assignment authority can
be specified and attacked locally. This amendment is not yet integrated into
the production state machine, persistence, recovery, runner, or analyzer.

## 4. Conditional synthetic planning

The historical planning grid crossed unavailable outcome probability
`U in {0,.05,.10,.15}` with intrablock correlation
`rho in {0,.10,.25}`. Under that declared data-generating process, 384 active
blocks per macro cell cleared the frozen positive planning criterion. Across
four macro cells, that benchmark implies 1,536 blocks and 12,288 randomized
sessions. Its worst all-cell positive decision rate was 96.25%, with a Monte
Carlo Wilson interval of 95.86% to 96.60%.

Six false-control families produced zero positive headlines across 72 cells of
20,000 replicates each; the largest Wilson upper bound was 0.0192%. By contrast,
no tested size cleared the broad observed-vector-equivalence gate. Even 3,072
blocks per macro cell reached only 66.84% in the designated hard cell.

A later non-gating diagnostic drew the actual restricted donor assignment and
added declared provider, batch, block, donor-pair, terminal-failure, and
block-formation dependence. Conditional positive decision rates remained
98.2%–100.0% across its five positive profiles, but whole-panel formation
support fell to 52.85%–77.0% under shared provider/batch shocks versus
94.3%–95.4% under the independent formation profile.

These are seeded Monte Carlo operating characteristics, not empirical estimates
of provider behavior. The dependence screen cannot recertify or rescue 384
blocks per cell. The historical request envelope—67,776 to 147,456 active-design
generations under the stored positivity assumptions—is a warning about scale,
not a collection or spending authorization.

## 5. Exploratory provider feasibility case study

### 5.1 Route observation

On 2026-08-19, a prompt-free Claude Code control session displayed an
individual Claude Max subscription route and selectors for Opus 5, Fable 5,
Sonnet 5, and Haiku 4.5. A minimal no-tools Sonnet probe returned the expected
visible response, but its provider-reported `modelUsage` listed both
`claude-sonnet-5` and `claude-haiku-4-5`. The raw HTTP attempt count was not
observable.

This observation is operationally important: one visible assistant turn did
not imply one provider-reported model activation. The subscription CLI route
therefore does not satisfy the strict confirmatory transport contract that had
assumed exact model identity and a countable raw-request boundary. The
observation contains no credentials, account identifiers, raw transcript, or
request identifiers.

### 5.2 Exact WS01 trajectory

One exploratory self-contingent trajectory used the exact frozen prompt catalog
(SHA-256
`ecca512d04dfe81f743cd1538798b9f4bb0fbe5b2b88c96647ffeb4a2ce0b80e`),
pair WS01, counterbalance variant CB00, and the frozen system prompt. Post-run
byte comparison confirmed that the three persisted user messages equaled the
catalog baseline, high-schedule execution, and follow-up messages in order.

The baseline returned `PLAN:B`, which maps to the high schedule under CB00.
The execution response supplied all six required modular-arithmetic answers and
scored 6/6 correct. The held-out follow-up again returned `PLAN:B`. All three
persisted assistant messages identified `claude-sonnet-5`; tools and server-side
web use were zero.

The baseline result envelope was lost at the orchestration stdout boundary.
Execution and follow-up envelopes listed only Sonnet, but raw HTTP count and
single-model execution remain unproven. Known client-reported execution plus
follow-up cost was USD 0.0250182; baseline cost was unavailable, so total cost
is not asserted.

The trajectory demonstrates only that the exact visible three-turn state
sequence can complete with mechanically valid outputs. It has no yoke, no
randomization, no population, and no effect estimate. It does not establish preference.
A stable high-to-high trajectory is equally compatible with
responsiveness, nonresponsiveness, and many route- or item-specific mechanisms.

## 6. What the combined evidence establishes

The evidence supports four bounded conclusions:

1. the Binding Test is mechanically specifiable and locally testable;
2. the terminal endpoint must retain unavailable and failure outcomes;
3. historical full-scale sizing is conditional and support formation is a
   first-order risk; and
4. the exact visible state sequence is feasible on one current route, while the
   same route does not expose a confirmatory-grade one-model/one-request
   boundary.

The provider case study strengthens the methods paper by falsifying a convenient
transport assumption. It does not strengthen the causal behavioral claim.

## 7. Limitations

The provider evidence consists of one route observation and one trajectory.
It cannot estimate semantic-validity rates, baseline positivity, support
retention, execution reliability, routing stability, temporal drift, or costs.
The baseline envelope loss is itself a feasibility defect. Provider-reported
model usage is not an independent network trace.

The sealed synthetic process omits many forms of dependence and is not a power
analysis for an amended production system. The reference snapshot labels are
placeholders. The current execution-failure amendment is not production
integrated. Exact entropy custody, full-row joins, stopping rules, cost bounds,
and preregistration remain incomplete for a confirmatory study.

The literature audit is a high-recall, single-auditor searched-record review,
not a systematic review or proof of absence. The priority statement concerns
the five-feature conjunction only; none of performed choices, incentives,
yoking, held-out behavior, or matched contextual manipulation is claimed as a
standalone novelty.

## 8. Confirmatory study boundary

Confirmatory collection requires a new prospective release. At minimum it must:

1. integrate exactly-one terminal `L/H/U` persistence and recovery;
2. bind the complete restricted assignment, exposure reconstruction, entropy,
   and donor/yoke joins;
3. complete the analyzer, partial-identification sensitivity, and failure
   reporting;
4. choose an exact provider route and model panel;
5. use transport that exposes or independently enforces the requested model,
   retry count, request envelope, and failure behavior;
6. recertify operating characteristics and choose a realistic resource
   frontier;
7. freeze prompts, parsers, runtime, prices, custody, and stopping rules; and
8. preregister before any confirmation observation.

Claude Code may remain useful for exploratory engineering. Under the current
strict design, a lower-level API or separately audited broker is the preferred
confirmatory route. Alternatively, the estimand and provenance contract would
have to be explicitly amended to permit provider helper activity.

## 9. Reproducibility and artifact availability

The construction audit is sealed in `paper8_stage1_release_v0`. The sanitized
route observation is sealed in `paper8_stage10_claude_cli_observation_v0`. The
sanitized feasibility trajectory is sealed in
`paper8_stage11_ws01_sonnet_feasibility_v0`. This overlay analyzes only the
sanitized, explicitly bounded fields in those releases and does not publish
credentials, account identifiers, session identifiers, raw transcripts, or raw
runtime paths.

The overlay claim-evidence ledger records every publication claim and its
permitted wording. The confirmatory protocol and Registered Report draft remain
separate prospective artifacts and are not silently updated by this paper.

## 10. Ethics and communication

This study concerns observable outputs and execution histories. It neither
assumes nor measures consciousness, sentience, welfare, suffering, moral
status, or subjective experience. Provider calls were bounded to inert local
tasks with tools and server-side web disabled for the reported trajectory.

Public communication should use *choice output*, *terminal disposition*,
*assigned schedule*, *enforcement policy*, and *exploratory trajectory*.
Statements that the model “cared,” “preferred,” “experienced a cost,” or was
“rewarded” are outside the evidence.

## References

- Wang, S., Lobanova, S., Arbel, Y. A., Goldstein, S., and Salib, P. (2026).
  *AI Revealed Preferences*. SSRN 6798118.
  <https://doi.org/10.2139/ssrn.6798118>
- Tagliabue, V., and Dung, L. (2025; revised 2026). *Probing the Preferences of
  a Language Model: Integrating Verbal and Behavioral Tests of AI Welfare*.
  arXiv:2509.07961v2. <https://doi.org/10.48550/arXiv.2509.07961>
- Moraski, B. (2026). *Revealed Moral Preferences in Frontier AI*.
  <https://character-evals.org/>; registration <https://osf.io/qtrb2/>
- Slama, K., Souly, A., Bansal, D., Davidson, H., Summerfield, C., and
  Luettgau, L. (2026). *When Do LLM Preferences Predict Downstream Behavior?*
  arXiv:2602.18971. <https://doi.org/10.48550/arXiv.2602.18971>
- Zhou, Y., and Ackerman, C. M. (2026). *When Preferences Fail to Become
  Incentives: A Utility-Behavior Gap in Large Language Models*.
  arXiv:2606.22974v2. <https://doi.org/10.48550/arXiv.2606.22974>
- Chiu, Y. Y., et al. (2025). *Will AI Tell Lies to Save Sick Children?*
  arXiv:2505.14633. <https://doi.org/10.48550/arXiv.2505.14633>
- Blandfort, P., et al. (2026). *Moral Preferences of LLMs Under Directed
  Contextual Influence*. OpenReview. <https://openreview.net/forum?id=PwXopj6hM1>
- Geng, J., Chen, H., Arumugam, D., and Griffiths, T. L. (2025). *Are Large
  Language Models Reliable AI Scientists? Assessing Reverse-Engineering of
  Black-Box Systems*. arXiv:2505.17968.
  <https://doi.org/10.48550/arXiv.2505.17968>

## Administrative disclosures

**Author:** Thomas Ryan, Independent Researcher, San Francisco, CA. Thomas Ryan
is the sole scholarly author and corresponding author. No ORCID is asserted.  
**Author contributions:** Thomas Ryan: conceptualization, methodology,
investigation, resources, supervision, project administration, validation, and
writing--review and editing.  
**Funding:** This research received no external funding.  
**Competing interests:** The author declares no competing interests.  
**Ethics:** This methods and feasibility study involved no human participants
or nonhuman animals. The reported provider trajectory used inert local tasks
with tools and server-side web disabled.  
**Data and code availability:** The release candidate contains the manuscript,
claim ledger, deterministic construction and simulation artifacts, sanitized
provider observations, and read-only verifiers. It excludes credentials,
account and session identifiers, raw provider envelopes, and quarantined
runtime material.  
**Generative AI use:** OpenAI Codex was used as a general-purpose research
assistant for literature triage, protocol and code drafting, local execution
orchestration, deterministic analysis, adversarial audit construction, release
engineering, and prose drafting and editing. Anthropic Claude Code was the
provider route for the separately labeled feasibility observations. AI systems
were not treated as authors. Thomas Ryan approved the research objective,
external calls and costs, protocol boundaries, evidence partition, and claim
ceiling and accepts responsibility for the accuracy and integrity of the
submission.  
**License:** Copyright 2026 Thomas Ryan. This preprint is released under the
Creative Commons Attribution 4.0 International license (CC BY 4.0).
