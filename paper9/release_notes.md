# Paper 9 Release Notes

## Release

Tag: `paper9-v1.0.0`

Title: Paper 9 preprint v1.0.0 - Stress-testing local neural-dynamics equivalence

## Paper

**Stress-Testing Local Neural-Dynamics Equivalence in a Connectome-Constrained Visual System**

Zenodo DOI: [10.5281/zenodo.22070302](https://doi.org/10.5281/zenodo.22070302)

This release packages the Paper 9 methods/null preprint, supplementary information, frozen protocols, analysis scripts, result JSONs, figures, tables, and reproducibility audits.

## Core result

- three alternate dynamics families were evaluated in Mi1, T4a, and T5a blocks;
- local eligibility was enforced before global interpretation;
- 45 eligible ordinary ladder cells produced 45 G1, 0 G2 outcomes across two global checkpoints;
- unchanged-decoder NRMSE remained below the frozen 1% margin;
- a Mi1 timescale causal-gain discrepancy replicated across two checkpoints and two step sizes at the decoder;
- solver controls killed several initial apparent causal effects;
- the matched-error D1C follow-up failed its calibration gate and stopped before checkpoints 013-014 were exposed;
- no D2 confirmatory study was opened.

## Claim boundary

This is exploratory computational evidence from a public model. It is not evidence of biological neuron replaceability, general connectome sufficiency, consciousness preservation, personal identity, or subject continuity.

## Integrity

Run `python3 audit_release.py` inside `paper9/` to verify the ten primary result hashes, outcome counts, table rows, figure dimensions, claim boundaries, and PDFs.

## License

CC BY 4.0 for the Paper 9 text, tables, and original figures. Upstream software and model artifacts retain their original licenses and are not redistributed in this release.
