# Paper 8 stage-1 reproducibility guide

## Scope

This directory is a release wrapper for Paper 8's local zero-call construction,
analytic identification, and conditional synthetic-sizing artifacts. It does not
contain or validate an empirical model experiment. The controlling zero-call
result reports zero provider calls, zero external spend, and no authorization to
collect provider data.

The wrapper deliberately excludes:

- raw or rendered external-model responses;
- `outputs/paper8_external_lanes/`;
- `subscription_calibration/`, its records, native artifacts, and transcripts;
- credentials, authentication state, provider runtime state, and network calls;
- superseded or interrupted synthesis artifacts as release evidence.

## One-command verification

Run from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 outputs/paper8_stage1_release_v0/verify_stage1_release.py
```

Here and below, `python3` must resolve to the documented reference Python 3.14.3
environment with NumPy 2.4.2; confirm the interpreter before verification rather
than relying on a directory-dependent shell `PATH`.

The verifier's orchestration and hash checks use the Python standard library.
Its mandatory amendment tests and deterministic dependence replay import NumPy,
so the current reference NumPy environment must be available. The verifier:

1. verifies every entry and the complete file set in
   `zero_call/zero_call_manifest.sha256`;
2. recomputes the 29-file scientific-source SHA-256 aggregate using the same
   canonical construction as `run_redesign_gate.py`;
3. requires that current source hashes equal the exact stored source map and
   aggregate `e0459b557e7e2c8b02d4565c554b9c09e82568c6271fcff15fe6e6096f3108d4`;
4. validates the stable trust-root structure: exact seed and schema, zero calls
   and spend, 84/84 required cells, B=384 blocks per macro cell, replicate
   floors, power/false-control criteria, selected-size status, request envelopes,
   and the abandoned broad-equivalence headline;
5. runs the combined `amendment_v1` suite and requires exactly 63 passing tests;
6. imports the exact local statistical-decision authority and requires its
   machine-readable policy to match the frozen `.05` paired H/L threshold,
   no-U primary, `.05/.05/.02` secondary equivalence margins, component-specific
   `SE<=1e-12` rule, simplex and strict-envelope checks, upstream-bound provenance
   limitation, exact terminal source/subtype-to-U policy, valid four-way
   arm-by-assigned-schedule decomposition, and mandatory U/flow reporting fields;
7. requires the stored dependence diagnostic to retain its closed non-gating
   schema, exact declared profiles and replicate counts, canonical assignment
   digest, and SHA-256
   `f1cfcece6e7df658109ee58812fe2883b5964d8c7b73be6d6811a7e1f3e190ef`;
8. deterministically replays that diagnostic with `--check`, under a hard
   600-second timeout, and requires exact byte identity;
9. rejects symlinks and raw/subscription-like paths in this release directory;
10. regenerates all 15 declared table/figure/provenance artifacts in a temporary
   directory and requires byte identity with the checked-in copies;
11. requires the rendered HTML to contain exactly six embedded SVG data payloads,
    with no relative figure reference or local file URI; and
12. verifies the self-excluding
   `paper8_stage1_release_manifest.sha256` over every intended non-cache release
   file. Missing, extra, mismatched, symlinked, private, or raw paths fail.

The amendment checks extend the release wrapper; they do not alter, reseal, or
supersede the `zero_call/zero_call_manifest.sha256` trust root.

## Amendment tests and deterministic replay

Run the combined authority and dependence suite directly with:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s outputs/paper8_stage1_release_v0/amendment_v1/tests \
  -p 'test_*.py'
```

The current required result is exactly 63 passing tests. The suite covers the
immutable eight-row assignment/terminal authority, closed 576-member allowed-set
membership, the byte-pinned canonical engine order, exact per-session arm and
yoked-exposure marginals, the bound uniform-policy digest, committed-reveal
selection reproduction, the closed L/H/U terminal-disposition taxonomy and
source/subtype mapping, exactly-once terminal joins, the amendment-frozen
statistical decision precedence and numerical boundaries, declared
dependence/failure profiles, and deterministic small-replicate checks. These
tests establish standalone amendment behavior, not production integration,
amended recertification, or collection authority.

The draft authority accepts the canonical assignment engine only when
`zero_call/binding_test/assignment.py` has SHA-256
`eeb51a912d9b0674030d7175251919fa318d7ab567db9ab84f9cd16f47e032a4`.
It then recomputes the closed 576-way projection locally rather than executing a
dynamically imported or preloaded module. This source binding is an internal
construction check, not proof that a future production runner used the authority.

The stored non-gating sensitivity result can be replayed without writing:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 \
  outputs/paper8_stage1_release_v0/amendment_v1/run_dependence_diagnostics.py \
  --check
```

The planned reference replay budget is roughly 70–90 seconds. Focused August 8
runs ranged from 79.819 seconds on an idle host to 312.531 seconds under severe
CPU contention, while reproducing the same SHA-256 bytes. The one-command
release verifier always runs the replay and enforces a finite 600-second
operational timeout. This wall-clock bound is not a scientific parameter and
does not alter the seed, DGP, replicate counts, estimands, or accepted bytes.
The replay covers six block-formation cells at 2,000 replicates each and eight
outcome profiles at 1,000 replicates each. Its required status is
`NON_GATING_SYNTHETIC_SCREEN`, `gate_effect` is `none`, and
`numerical_gate_eligible` is `false`; replay success cannot certify B=384,
authorize collection, or convert a sensitivity screen into empirical evidence.

## Stable scientific payload versus volatile metadata

The sealed zero-call manifest verifies the exact stored bytes. That is an
integrity check, not a claim that a fresh run will reproduce every byte.

For scientific equality, `verify_stage1_release.py` deliberately does not compare:

- `generated_date`, which is produced with `date.today()`;
- `test_suite.transcript`, including the variable `Ran ... tests in ...s` timing;
- filesystem modification times or console progress order.

It still requires the stable test result (`passed=true`, return code 0, and 120
tests) and independently checks the scientific source snapshot and trust-root
statistics. A future regenerated artifact should compare these stable fields,
not its wall-clock prose, to the sealed reference.

## Non-writing behavioral replay

The full 10,000/20,000-replicate certification writes the canonical JSON and
report, so do not run it in the sealed source directory merely to inspect the
package. A lower-cost, explicitly non-certifying and non-writing replay is:

```bash
PYTHONPATH=.:zero_call PYTHONDONTWRITEBYTECODE=1 \
  python3 zero_call/run_redesign_gate.py --smoke --workers 4
```

The smoke path exercises all 178 configured cells with 64 replicates, reruns the
test suite, checks source stability, and writes no final artifacts. Its numerical
rates are intentionally replicate-ineligible and must never replace the stored
certification.

## Deterministic release artifacts

The eight declared CSV tables, six SVG figures, and their provenance guide can be
checked without modifying the release:

```bash
python3 outputs/paper8_stage1_release_v0/generate_tables_figures.py --check
```

The command regenerates the declared outputs under a temporary directory and
byte-compares them. To intentionally rebuild those outputs after a reviewed
source change, omit `--check` and then rerun the full verifier before resealing.

The human-readable manuscript can be rendered locally with:

```bash
python3 outputs/paper8_stage1_release_v0/render_manuscript.py
```

This produces `output/html/binding_test_stage1.html` and
`output/pdf/binding_test_stage1.pdf`. The renderer requires the locally installed
`markdown` and `weasyprint` packages and makes no network request. `MANUSCRIPT.md`
remains the scientific source of authority; the rendered copies are presentation
artifacts sealed by the release manifest.

After all intended release edits and renders are complete, reseal and verify with:

```bash
python3 outputs/paper8_stage1_release_v0/seal_release.py
python3 outputs/paper8_stage1_release_v0/seal_release.py --verify
python3 outputs/paper8_stage1_release_v0/verify_stage1_release.py
```

The manifest excludes itself, rejects private/raw path classes and symlinks, and
requires canonical sorted SHA-256 rows.

For a complete independent regeneration, use a disposable clean checkout or copy,
pin the environment, run the README command without `--smoke`, and compare the
stable scientific projection. The full command overwrites
`zero_call/results/redesign_gate_results.json` and
`zero_call/REDESIGNED_GATE_REPORT.md` in the working copy.

## Reference environment and limitation

The environment observed during this release audit was Python 3.14.3 with NumPy
2.4.2. `requirements-reference.txt` pins the current NumPy reference, and
`environment-reference.txt` records the current Python version. These are current
references only. The stored artifact does not
prove that these exact versions generated the August 5 result, so the reference
must not be described as the original environment or a historical lock.

The full simulation and the mandatory amendment diagnostic depend on NumPy and use
independently seeded PCG64 streams. Environment-version reporting remains
informational rather than proof of the original environment, but NumPy must be
installed for the gated amendment tests and replay. Cross-version full
regeneration remains a caveat until an original environment record or independently
validated lock is available.

## What successful verification licenses

Successful verification establishes that the current local zero-call package is
the sealed package, its scientific sources match the result's prepublication
snapshot, and its stored synthetic trust-root claims are internally consistent.

It does not establish frontier-model behavior, item unsaturation, empirical choice
support, provider transport validity, dollar cost, a broad equivalence result, a
latent binary-choice effect, or a workload-control-specific mechanism.
