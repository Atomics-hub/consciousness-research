# Literature search appendix: exact-conjunction priority audit

**Search date:** 2026-08-07  
**Record cutoff:** records visible on the searched services by the end of 2026-08-07 (America/Los_Angeles)  
**Status:** provisional searched-record result; not a systematic review and not proof of absence

## 1. Question and result

The audit asked whether a located study of a large language model already combined all five of the following features:

1. a mechanically scored baseline choice recorded before an enforcement treatment exists;
2. post-baseline prospective assignment to an own-choice-contingent history or a yoked history;
3. a yoke that matches assigned schedule and relevant affordance marginals across arms, so the intended contrast is whether the focal system's own earlier choice controlled what happened;
4. execution of the assigned history followed by a held-out, mechanically scored choice in the same session; and
5. full nominal `L/H/U` reporting with separate observed-distribution and partially identified binary decisions.

No record located in the source set below contained that full conjunction. This is the only priority statement supported by this audit. It is a **provisional result about a finite searched record**, not proof that no such work exists. It is not a legal-priority opinion, a claim to have identified the chronologically first study, or a systematic-review conclusion. Unindexed manuscripts, private projects, newly posted records, terminology mismatches, and gray literature remain material collision risks.

The audit also found close component-level precedents that sharply limit the permissible wording. In particular, the searched record already includes performed-task choices, virtual costs and rewards, real on-chain allocations, preference-to-downstream-behavior tests, success-contingent utility incentives, value-based prediction of held-out behavior, baseline-plus-matched directional manipulations, and a passive-intervention-yoked condition. The paper therefore cannot claim novelty for any of those components by itself.

## 2. Sources, scope, and reproducible query families

The searched source set was arXiv, OpenReview, SSRN, OSF, and official project pages. Search-result snippets and citation chains were used for discovery only; inclusion and positioning below were checked against a primary record page, paper, registration, or official project page. The arXiv search covered `cs.AI`, `cs.CL`, and `cs.LG`, with cross-listed records retained. OpenReview was searched across its general paper index and relevant 2025–2026 venue/workshop records, including ICLR, TMLR, and AI4GOOD. SSRN was searched across title, abstract, and keyword records. OSF and linked project pages were searched for registrations and documented gray-literature studies.

The following literal query families record the concepts used in the audit. Where a service did not support Boolean syntax, the quoted phrases and unquoted terms were entered as separate searches, and returned titles/abstracts were manually screened.

| ID | Literal query family | Purpose |
|---|---|---|
| Q1 | `"large language model" AND (preference OR utility OR value) AND ("downstream behavior" OR incentive OR consequence)` | Preference-to-behavior and incentive-transfer precedents |
| Q2 | `(LLM OR "language model") AND (preference OR choice) AND ("task performance" OR allocation OR "real stakes" OR "virtual environment")` | Performed-task, allocation, and implemented-consequence studies |
| Q3 | `(LLM OR "language model") AND (yoked OR "passive intervention" OR "matched control")` | Yoking and matched-exposure precedents |
| Q4 | `("baseline choice" OR "stated preference") AND ("follow-up choice" OR "revealed preference" OR downstream) AND (LLM OR "language model")` | Two-stage and held-out behavioral designs |
| Q5 | `("self-contingent" OR "choice-contingent" OR "action-contingent") AND (yoke OR yoked) AND (follow-up OR downstream)` | Direct exact-conjunction collision search |
| Q6 | `"assigned-schedule-matched"`; `"post-baseline" AND yoked AND LLM`; `"own choice" AND yoked AND "language model"` | Terminology-specific exact-collision search |
| Q7 | Exact titles and author surnames for every candidate listed in Section 3 | Primary-record and version verification |

Source-specific rerun terms were:

- **arXiv (`cs.AI`, `cs.CL`, `cs.LG`):** Q1–Q6, plus `preference behavior LLM`, `utility incentive language model`, `moral values held-out behavior`, and `black-box intervention yoked LLM`.
- **OpenReview:** `LLM preferences downstream behavior`, `baseline matched influence moral choices`, `stated revealed preferences`, `yoked intervention language model`, and exact-title searches for candidate workshop or review records.
- **SSRN:** `AI revealed preferences`, `language model revealed preferences`, `AI preference task performance`, and `real stakes language model`.
- **OSF and official project pages:** `language model preferences preregistration`, `AI real stakes allocation`, `revealed moral preferences frontier AI`, and exact project-title/registration-identifier checks.

Records were retained if they instantiated any part of the five-feature conjunction or directly constrained the paper's interpretation. Generic work on human preferences, recommender systems, or RLHF preference labels was not treated as a collision unless it experimentally studied an LLM's own choices, downstream behavior, intervention process, or assigned history. Secondary summaries were not used as evidence for the positioning claims.

## 3. Included records and positioning

| Primary record | Identifier, URL, and DOI | Why included / overlap | What remains different from the five-part conjunction |
|---|---|---|---|
| Sam Wang, Sofiia Lobanova, Yonathan A. Arbel, Simon Goldstein, and Peter Salib, *AI Revealed Preferences* (2026) | SSRN 6798118; [record](https://ssrn.com/abstract=6798118); [SSRN landing page](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6798118); [DOI](https://doi.org/10.2139/ssrn.6798118). | Runs forced-choice experiments in which the selected tasks are actually performed. It directly occupies performed-task choice and a broad “make the choice real” contribution. | The audited record does not describe post-baseline randomization to own-choice-contingent versus assigned-schedule-matched yoked histories followed by a held-out choice. |
| Valen Tagliabue and Leonard Dung, *Probing the Preferences of a Language Model: Integrating Verbal and Behavioral Tests of AI Welfare* (2025; revised 2026) | arXiv:2509.07961v2; [record](https://arxiv.org/abs/2509.07961); [DOI](https://doi.org/10.48550/arXiv.2509.07961) | Compares verbal and behavioral preference measures in a persistent backend-mediated virtual environment under communicated cost and reward conditions. It occupies virtual economic-rule exposure and behavioral preference measurement. | It does not supply the audited exact own-choice-versus-yoke allocation-policy contrast or its later mechanically scored choice endpoint. Its welfare interpretation is also not adopted here. |
| Boden Moraski, *Revealed Moral Preferences in Frontier AI*; linked OSF public preregistration qtrb2 | [official project page](https://character-evals.org/), accessed 7 August 2026; [OSF registration qtrb2](https://osf.io/qtrb2/). No DOI was displayed on the audited project or registration record. | The official preregistered pilot reports real USDC allocations and a real-versus-hypothetical by evaluation-framing design. It occupies real monetary/on-chain stakes, allocation choice, and broad stakes-by-evaluation-context framing. | Trials are presented as independent allocation trials, not a post-baseline restricted randomization to own-choice-contingent versus matched-yoked histories with a later held-out choice. |
| Katarina Slama, Alexandra Souly, Dishank Bansal, Henry Davidson, Christopher Summerfield, and Lennart Luettgau, *When Do LLM Preferences Predict Downstream Behavior?* (2026) | arXiv:2602.18971v1; [record](https://arxiv.org/abs/2602.18971); [DOI](https://doi.org/10.48550/arXiv.2602.18971) | Measures preferences and then tests downstream donation advice, refusal behavior, BoolQ performance, and complex agentic-task performance. It directly occupies the broad “do measured preferences predict downstream behavior?” question. | It does not randomize the enforcement relation between a focal model's own baseline choice and a matched later execution history. |
| Yujun Zhou and Christopher M. Ackerman, *When Preferences Fail to Become Incentives: A Utility–Behavior Gap in Large Language Models* (2026) | arXiv:2606.22974v2; [record](https://arxiv.org/abs/2606.22974); [DOI](https://doi.org/10.48550/arXiv.2606.22974) | Elicits model-specific utilities and compares high-utility, low-utility, and no-outcome incentives tied to performance on writing tasks. This is the closest conceptual collision for linking elicited choices, success-contingent consequences, and later task behavior. | It does not compare self-contingent execution with a randomized assigned-schedule-matched yoke. The consequence content differs across high- and low-utility incentive conditions rather than holding the assigned-history distribution fixed while changing causal ownership. |
| Yu Ying Chiu, Zhilin Wang, Sharan Maiya, Yejin Choi, Kyle Fish, Sydney Levine, and Evan Hubinger, *Will AI Tell Lies to Save Sick Children? Litmus-Testing AI Values Prioritization with AIRiskDilemmas* (2025) | arXiv:2505.14633v1; [record](https://arxiv.org/abs/2505.14633); [DOI](https://doi.org/10.48550/arXiv.2505.14633) | Uses aggregate choice-derived value priorities to predict seen risky behavior in AIRiskDilemmas and unseen risky behavior in HarmBench. It occupies a broad held-out predictive-validity claim for value-choice measures. | It does not assign and execute own-choice-contingent versus matched-yoked histories after a baseline choice. Prediction across tasks is not the same estimand as the randomized enforcement-policy contrast. |
| Phil Blandfort, Tushar Karayil, Alex McKenzie, Urja Pawar, Robert Graham, and Dmitrii Krasheninnikov, *Direction-Flipped Influence Audits Reveal Hidden Structure in Moral Choices of LLMs* (2026) | AI4GOOD Workshop 2026 Spotlight; [OpenReview record](https://openreview.net/forum?id=C39he3zcV6). No DOI was displayed on the audited OpenReview record. | Compares baseline prompts with matched direction-flipped cues aimed toward either choice and adds cue-recognition probes. It occupies baseline-plus-matched-manipulation and directionally paired influence auditing. | The manipulation is contextual influence, not execution of a history whose causal dependence on the focal model's own earlier choice is randomized against a yoke. |
| Jiayi Geng, Howard Chen, Dilip Arumugam, and Thomas L. Griffiths, *Are Large Language Models Reliable AI Scientists? Assessing Reverse-Engineering of Black-Box Systems* (2025) | arXiv:2505.17968v1; [record](https://arxiv.org/abs/2505.17968); [DOI](https://doi.org/10.48550/arXiv.2505.17968) | Compares observation-only, active-intervention, and passive-intervention-yoked LLM conditions in black-box reverse engineering. By passing intervention data from one LLM to another, it separates exposure to intervention data from engaging in intervention generation. It therefore occupies yoking as a design component. | The target is black-box system identification, not a baseline/follow-up choice policy; there is no own-choice-contingent enforcement history with assigned schedule/affordance margins and the paper's held-out choice endpoint. |

## 4. Exact-conjunction assessment

The nearest records collide with different subsets of the design:

- Wang and Tagliabue–Dung establish performed choices and implemented virtual consequences.
- Moraski establishes real on-chain allocations under real/hypothetical and evaluation-framing variation.
- Slama and Chiu establish preference-to-downstream-behavior and held-out predictive-validity programs.
- Zhou–Ackerman establishes a two-stage utility-elicitation and success-contingent incentive test and is the closest conceptual collision.
- Blandfort et al. establish baseline-plus-matched direction-flipped manipulation.
- Geng et al. establish a passive-intervention yoke that distinguishes receiving the same intervention information from generating the intervention.

None of those differences should be minimized. In particular, the Geng design means that “uses a yoke to separate exposure from agency” is not available as an unqualified novelty claim, and Zhou–Ackerman means that “tests whether preferred consequences motivate later performance” is not available either.

The residual searched-record statement is narrower:

> In the arXiv, OpenReview, SSRN, OSF, and official-project records searched through 2026-08-07, no located LLM study combined a pre-treatment mechanically scored baseline choice; post-baseline prospective assignment to own-choice-contingent versus assigned-schedule/affordance-matched yoked execution; execution of that assigned history followed by a held-out mechanically scored follow-up choice; and full nominal `L/H/U` reporting with separate observed-distribution and partially identified binary decisions.

This wording concerns the **combination and estimand**, not the individual ingredients. “No located study” must not be shortened to “no prior study,” “the first,” “unprecedented,” or “novel” without the search qualifier. A direct collision found later must narrow or remove the priority sentence even if the experimental design itself is retained.

## 5. Component novelty disavowals

The manuscript should explicitly disavow each of the following standalone novelty claims:

- first to make an LLM perform a selected task;
- first to study behavioral preferences, virtual costs, virtual rewards, or persistent virtual economic rules;
- first to attach real money, on-chain transfers, or other implemented consequences to an LLM allocation;
- first to compare real with hypothetical stakes or explicit with unframed evaluation context;
- first to ask whether measured LLM preferences predict downstream advice, refusal, task performance, or risky behavior;
- first to use elicited utilities as success-contingent incentives for later work;
- first to use a baseline plus matched direction-flipped manipulations;
- first to use a yoke to distinguish intervention exposure from engaging in intervention generation;
- first to use randomization, matched controls, held-out tasks, or mechanically scored choices in isolation; or
- evidence that model outputs reveal preference, utility, motivation, cost-bearing, welfare, consciousness, or subjective experience.

The defensible target is an observable **allocation-policy effect in a specified harness**: whether later choice outputs differ when the focal system's own earlier choice controlled its assigned history rather than when it received an assigned-schedule-matched yoked history. Even that target remains provisional until the literature search is rerun and the execution-failure and interference details of the protocol are frozen.

## 6. Limitations and update rule

This was a high-recall, single-auditor priority search, not a PRISMA-style systematic review. It did not use dual independent screening, a registered review protocol, exhaustive multilingual searching, or guaranteed coverage of private, withdrawn, paywalled, or poorly indexed work. Search interfaces rank and update results, and exact terminology for yoking, contingency, and follow-up behavior varies across fields.

The search must be rerun at protocol freeze and again immediately before external submission. At minimum, the rerun should repeat Q1–Q7, check current versions and citation graphs of all eight included records, and search new arXiv, OpenReview, SSRN, OSF, and official-project records posted since 2026-08-07. Every newly located near collision should be entered in an append-only priority ledger with its search date, primary URL, overlap, and effect on permissible wording.
