# Paper 8 stage-1 release index

## Release status

This is the canonical wrapper for the local Paper 8 internal Stage-1 methods
artifact: deterministic construction checks, analytic identification results, and
conditional synthetic sizing for The Binding Test. It is not an empirical
model-results release and does not grant permission for provider calls, spending,
preregistration, external circulation, or publication.

## Controlling scientific artifacts

The verifier treats these existing sealed artifacts as controlling:

- `zero_call/REDESIGN_GATE_SPEC.md` — frozen identified-outcome design and gate;
- `zero_call/item_bank_v0.json` and `zero_call/ITEM_SEMANTIC_AUDIT.md` — local
  deterministic item surface and its empirical limitations;
- `zero_call/binding_test/` — assignment, parsing, state, inference, planning,
  simulation, and runtime-binding code;
- `zero_call/tests/` — the 120-test integrity suite;
- `zero_call/results/redesign_gate_results.json` — machine-readable conditional
  synthetic sizing result;
- `zero_call/REDESIGNED_GATE_REPORT.md` — controlling human-readable result;
- `zero_call/zero_call_manifest.sha256` — self-excluding seal of the complete
  zero-call package.

Files in this wrapper:

- `RELEASE_INDEX.md` — canonical scope, inventory, claim ceiling, and exclusions;
- `MANUSCRIPT.md` — scientific manuscript source;
- `output/pdf/binding_test_stage1.pdf` and
  `output/html/binding_test_stage1.html` — rendered reading copies;
- `CLAIM_EVIDENCE_LEDGER.md` — claim-level evidence and wording controls;
- `LITERATURE_SEARCH_APPENDIX.md` — provisional searched-record audit;
- `PROTOCOL_AMENDMENTS_REQUIRED.md` — mandatory no-go gates before collection;
- `POST_GATE_STATUS.md` — supersession notice for earlier project syntheses;
- `REGISTERED_REPORT_STAGE1_DRAFT.md` — draft-only preregistration authority,
  amendment-frozen statistical choices, and remaining empirical-freeze fields;
- `ANALYSIS_DECISION_CHARTER.md` — exhaustive draft decision precedence and
  outcome-independent reporting labels;
- `references.bib` — machine-readable bibliography;
- `TABLES_AND_FIGURES.md` — visual/table provenance and source mappings;
- `amendment_v1/protocol_authority.py` — immutable randomized-block authority,
  byte-pinned canonical 576-member assignment-set membership and exact session
  marginals, bound uniform-policy and deterministic selection-proof helpers,
  strict terminal-disposition records with a closed source/subtype mapping, and
  exactly-once terminal ledger;
- `amendment_v1/tests/test_protocol_authority.py` — authority, membership,
  fingerprint, replay, conflict, and terminal-ledger forgery tests;
- `amendment_v1/statistical_decision_authority.py` — immutable amendment-frozen
  `.05` H/L primary, `.05/.05/.02` secondary equivalence, the declared U-reporting requirement,
  component-validity, support, and primary/vector-equivalence whole-panel
  decision subset;
- `amendment_v1/tests/test_statistical_decision_authority.py` — closed-schema,
  precedence, numerical-boundary, zero-SE, no-U-primary, failure-flow, and
  all-cell conjunction tests;
- `amendment_v1/dependence_diagnostics.py` — isolated seeded dependence,
  post-randomization-failure, and block-formation sensitivity implementation;
- `amendment_v1/run_dependence_diagnostics.py` — deterministic writer or
  non-writing `--check` runner for the stored sensitivity result;
- `amendment_v1/tests/test_dependence_diagnostics.py` — assignment,
  terminal-disposition/source-subtype, DGP-truth, schema, and chunk-invariance
  tests;
- `amendment_v1/results/dependence_diagnostics.json` — stored non-gating
  six-formation-cell/eight-outcome-profile synthetic sensitivity result;
- `tables/design_summary.csv`, `tables/positive15_u_icc.csv`,
  `tables/sample_size_frontier.csv`, `tables/false_controls.csv`,
  `tables/support_request_b384.csv`, and
  `tables/latent_binary_intervals.csv` — six deterministic zero-call tables;
- `tables/dependence_outcome_screen.csv` and
  `tables/block_formation_screen.csv` — two deterministic non-gating amendment
  diagnostic tables;
- `figures/design_flow.svg`, `figures/latent_binary_intervals.svg`,
  `figures/positive15_u_icc_heatmap.svg`, and
  `figures/sample_size_frontiers.svg` — four deterministic zero-call vector
  figures;
- `figures/dependence_outcome_screen.svg` and
  `figures/block_formation_support.svg` — two deterministic non-gating
  amendment diagnostic figures;
- `generate_tables_figures.py` — standard-library artifact generator and
  non-writing byte-comparison check;
- `render_manuscript.py` — local Markdown-to-HTML/PDF presentation renderer;
- `REPRODUCIBILITY.md` — verification and replay instructions;
- `environment-reference.txt` and `requirements-reference.txt` — current,
  explicitly non-historical reproduction references;
- `seal_release.py` — deterministic creator/verifier for the self-excluding
  release manifest;
- `verify_stage1_release.py` — standard-library integrity, trust-root, exact
  amendment-test-count, frozen statistical-policy, deterministic-diagnostic,
  generated-artifact, scope, and release-manifest verifier; and
- `paper8_stage1_release_manifest.sha256` — self-excluding final release seal.

## Headline result and claim ceiling

The synthetic trust root identifies B=384 active blocks per macro cell for the
frozen +15-point paired H-increase/L-decrease benchmark, with U reported
separately. Across four macro
cells this is 1,536 blocks and 12,288 randomized sessions before baseline-support
attempt inflation. The worst of the 12 power cells is 96.25%, with Wilson 95%
interval 95.86%–96.60%; the largest required false-control Wilson upper bound is
0.0192%.

This is a conditional sample-size/design result under frozen synthetic
assumptions. It is not evidence that any model exhibits the effect. The simulation
omits the central donor-yoke dependence, post-randomization execution failure,
provider-wide shocks, temporal dependence, and block-formation uncertainty.
Accordingly, B=384 is illustrative and cannot authorize collection. The broad
negative/equivalence headline is abandoned: failure to establish the positive
effect is indeterminate, not evidence of invariance.

The v0 state machine also has no follow-up after terminal execution failure while
the analyzer requires eight outcome rows. `PROTOCOL_AMENDMENTS_REQUIRED.md`
therefore records a current NO-GO. The strongest available future empirical claim
remains limited to a paired H-increase/L-decrease in observed terminal dispositions,
with U reported separately, in exact tested snapshot-by-target cells and a
prospectively supported randomized population,
after the amendment-frozen endpoint and statistical contract are
production-integrated and the amended design is recertified.
Latent binary choice, mechanism, preference, utility, experience, welfare,
consciousness, and generalization beyond the finite tested panel remain
unidentified.

The isolated `amendment_v1` authority supplies an implementable eight-row
assignment/terminal contract and tests, while the stored dependence diagnostic
screens declared donor, shared-shock, execution-failure, and block-formation
stresses. The diagnostic is deliberately stamped
`NON_GATING_SYNTHETIC_SCREEN`, `gate_effect=none`, and
`numerical_gate_eligible=false`. It neither changes the sealed zero-call trust
root nor recertifies B=384; protocol integration and prospective freeze remain
required before the NO-GO can be reconsidered.

## Deliberate exclusions

None of the following is part of this stage-1 release evidence boundary:

- any `outputs/paper8_external_lanes/` file, including raw JSON or rendered response;
- any `subscription_calibration/` file, record, ledger, native artifact, or transcript;
- the August 3 `outputs/paper8_artifact_manifest.sha256`, which predates the
  August 4–5 zero-call package and is a historical synthesis manifest rather than
  this release authority;
- files named `*_superseded*` or `*_interrupted*`;
- credentials, authentication material, provider-session state, or network data.

The earlier synthesis documents remain research-decision history. Where they still
describe binary responsiveness or a broad equivalence result as the Paper 8
headline, the redesigned gate report and this index supersede that language.

## Local release manifest

`paper8_stage1_release_manifest.sha256` is the required self-excluding release
seal. Entries use lowercase SHA-256, two spaces, and canonical relative paths.
The verifier requires exact coverage of every non-cache file in this release tree,
excluding the manifest itself, and rejects symlinks, malformed paths, or
private/raw path classes. Regenerate the manifest only after every intended release
edit and rendered artifact is final.
