# Paper 9: Stress-Testing Local Neural-Dynamics Equivalence

This directory contains the public preprint and reproducibility release for:

**Stress-Testing Local Neural-Dynamics Equivalence in a Connectome-Constrained Visual System**

- Author: Thomas Ryan
- Affiliation: Independent Researcher, San Francisco, California, USA
- Version: v1.0.0
- Publication date: 23 August 2026
- License: CC BY 4.0
- Zenodo DOI: [10.5281/zenodo.22070302](https://doi.org/10.5281/zenodo.22070302)

## Result in one paragraph

Alternative neuron dynamics were required to pass a frozen source-clamped local-equivalence gate before replacing Mi1, T4a, or T5a blocks inside a public connectome-constrained fly visual model. All 45 locally eligible ordinary-response ladder cells preserved block activity and the unchanged pretrained decoder within the frozen 1% margins. Causal probes found one small cross-checkpoint, solver-robust Mi1 timescale gain discrepancy, but a preregistered matched-error follow-up stopped before confirmatory holdout exposure because no comparator satisfied its complete local gate. The study is exploratory methods/null work. It does not establish connectome sufficiency, biological replaceability, consciousness preservation, personal identity, or a general composition theorem.

## Contents

- `ryan_2026_stress_testing_local_neural_dynamics_equivalence.pdf` - main preprint
- `ryan_2026_paper9_supplement.pdf` - supplementary information
- `manuscript.md` and `supplement.md` - editable sources
- `figures/` - five publication figures
- `tables/` - source-derived summary tables
- `results/` - frozen D1B/D1C JSON result artifacts
- `code/` - primary stage scripts retained with their original project-relative imports
- `protocols/` - frozen designs and stage reports
- `novelty_and_claim_audit.md` - hostile priority and claim audit
- `REPRODUCIBILITY.md` - environment, source, and hash manifest
- `PACKAGE_MANIFEST.md` - release-candidate hashes

The public result JSONs and figure/table builder are sufficient to reconstruct every plotted value without redistributing the upstream pretrained model archive.

## Rebuild figures and tables

Install Python with `numpy` and `matplotlib`, then run from `paper9/`:

```sh
python3 build_artifacts.py
```

The full neural simulations additionally require the pinned upstream `flyvis` source and pretrained artifacts described in `REPRODUCIBILITY.md`. The archived stage scripts retain their original project-relative imports to preserve the executed code state.

## Audit

With `Pillow` and `pypdf` installed:

```sh
python3 audit_release.py
```

Expected result:

```text
PASS: hashes, classifications, tables, figures, claim boundaries, and PDFs verified
```

## Authorship and AI assistance

Thomas Ryan is the sole human author and accountable operator. AI systems assisted with literature triage, protocol stress-testing, code drafting, artifact checking, figure generation, and manuscript drafting. AI systems are not authors and do not provide independent validation.

## License

Unless an upstream component states otherwise, Paper 9 text, tables, and original figures are released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The upstream `flyvis` software and pretrained artifacts remain governed by their own terms and are not redistributed here.
