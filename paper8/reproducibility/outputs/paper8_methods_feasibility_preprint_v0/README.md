# Paper 8 methods and feasibility preprint overlay

This directory is a new, non-destructive publication overlay. It does not edit
or reseal any prior stage.

The proposed paper reports three explicitly separated evidence layers:

1. a sealed zero-call construction audit and analytic identification result;
2. seeded synthetic planning calculations; and
3. a single sealed, exploratory provider trajectory plus a transport
   observation.

The third layer is a feasibility case study only. It is not calibration,
randomized evidence, an effect estimate, or confirmatory data.

## Publication claim

The paper may claim that the Binding Test is a mechanically specified design
for estimating whether later AI choice outputs change when an earlier choice
controls an assigned history rather than being paired with a schedule-matched
yoke. The current artifacts establish local construction and one successful
end-to-end visible trajectory. They do not establish that any model is
responsive to the randomized enforcement policy.

## Contents

- `MANUSCRIPT.md` — submission-oriented methods/feasibility manuscript.
- `CLAIM_EVIDENCE_LEDGER.md` — claims, evidence boundaries, and prohibited
  paraphrases for this overlay.
- `LITERATURE_DELTA_2026-08-19.md` — submission-date collision-search update.
- `CITATION.cff` — sole-author citation metadata.
- `ZENODO_METADATA.md` and `zenodo_metadata.json` — upload-ready metadata with
  the reserved, unpublished version DOI
  metadata and exact Papers 1–7 reference relations.
- `PUBLIC_ARTIFACT_INDEX.md` — public archive contents and exclusions.
- `COVER_NOTE.md` — general preprint or venue cover note.
- `LICENSE.md` — CC BY 4.0 release terms.
- `SHIP_CHECKLIST.md` — remaining author, rendering, archive, and submission
  work.
- `build_public_release.py` and `verify_public_release.py` — deterministic
  sanitized release builder and verifier.
- `render_preprint.py` — deterministic local HTML/PDF presentation renderer.
- `verify_preprint.py` — read-only consistency and lineage verifier.
- `paper8_methods_feasibility_preprint_manifest.sha256` — self-excluding payload
  manifest, created only after the package is final.

## Controlling sealed inputs

- Stage 1 construction release: `../paper8_stage1_release_v0/`
- Stage 10 transport observation: `../paper8_stage10_claude_cli_observation_v0/`
- Stage 11 feasibility trajectory: `../paper8_stage11_ws01_sonnet_feasibility_v0/`

The confirmatory study remains a separate future release. Claude Code on the
observed subscription route is suitable for exploratory engineering but is not
currently accepted as the strict confirmatory transport because one visible
turn exposed more than one provider-reported model activation and raw HTTP
attempt count remained unavailable.
