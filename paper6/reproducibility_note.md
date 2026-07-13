# Paper 6 Reproducibility Note

This public repository contains the Paper 6 manuscript, the published Zenodo PDF, public figures, and aggregate result tables. It intentionally does not include the full coordinator workspace.

## Included

- Published PDF and Markdown manuscript source.
- Public SVG figures.
- Eligible-row and gate-outcome summaries.
- Zenodo metadata and release notes.

## Excluded

The following materials are excluded from the public repository:

- coordinator-private harness state;
- hidden keys and condition maps;
- blind packet archives;
- runner return packets and inbox staging directories;
- internal Codex workspace paths, command-center state, and local audit scratch outputs.

This boundary avoids publishing scaffolding that could contaminate later replications or expose local/private coordination context. The public paper reports aggregate eligible rows and gate outcomes rather than releasing the blinded packet machinery.

## Exact Published Artifact

The PDF in this folder matches the file published on Zenodo:

- DOI: `10.5281/zenodo.21342748`
- URL: `https://zenodo.org/records/21342748`
- MD5: `29d1375724f6ed354ce244344e052d19`
- SHA-256: `1ded94cf5c92ccbe51548f7d020c58b834b2e0cb26ea40ef1c59ba080b1af487`
