# Paper 10 - The Intervention-Coverage Barrier

**Author:** Thomas Ryan, Independent Researcher  
**Status:** Public preprint v1.0.0; not peer reviewed  
**License:** CC BY 4.0
**Publication date:** 29 August 2026  
**Zenodo DOI:** [10.5281/zenodo.22166381](https://doi.org/10.5281/zenodo.22166381)

## Result in one sentence

A finite intervention battery can decisively falsify neural replacement fidelity, but success on that battery cannot by itself certify uniform fidelity over a continuous domain; a distributional claim needs an explicit intervention law, and a worst-case claim needs justified structure or a sound regularity-and-coverage certificate.

## Claim ceiling

This package does not show that any specific neural replacement fails, that whole-brain emulation is impossible, or that consciousness, identity, survival, biological replaceability, or substrate independence is preserved or lost.

## Package map

```text
manuscript.md                 Main paper source
supplement.md                 Proofs, audit trail, complete tables, and lineage
figures/                      Five source-backed figures plus generated math assets
tables/                       Machine-readable result tables
output/pdf/                   Main, supplement, and combined PDFs
reproducibility/              Checksums and release manifest
reproducibility/synthetic/    Frozen specifications, code, results, and tests
reproducibility/audit/        Evidence ledger and program-selection audits
render_pdf.py                 Deterministic ReportLab renderer
build_artifacts.py            Figure and table builder
verify_package.py             Package integrity and consistency checks
zenodo_metadata.json          Public deposit metadata and lineage identifiers
```

## Reproduce

Use Python 3 with NumPy, Matplotlib, Pillow, and ReportLab available.

The manuscript sources use `$...$` for inline mathematics and `$$...$$` for display equations. `build_artifacts.py` renders those expressions into high-resolution transparent assets before the PDF build, while leaving literal hashes and software identifiers as code.

```bash
python3 -m unittest discover -s paper10/reproducibility/synthetic -p 'test_*.py' -v
python3 paper10/reproducibility/synthetic/intervention_coverage.py
python3 paper10/reproducibility/synthetic/run_confirmatory.py
MPLBACKEND=Agg MPLCONFIGDIR=/tmp/paper10-mpl python3 paper10/build_artifacts.py
python3 paper10/render_pdf.py
python3 paper10/verify_package.py
```

Re-running the result generators overwrites deterministic result JSONs. It does not create a new independent confirmation or a new preregistration event. The pre-execution specification, its hash, and repository history carry the audit boundary.

## Frozen identities

- Exploratory specification SHA-256: `5fecc6bf14b1088f15c593fc8bf245fd3b2f33e0b1d6527c9066489ef94ce2d6`
- Confirmatory specification SHA-256: `4dcc507a26d1e67e7ad9bce0b6784ea4bc9319d056d921798ec9495da31a7050`
- Confirmatory runner SHA-256: `0663d496d7104d28ad7bbe9b8a720b02b4e533dce87803f3ca37c52ead5eadfd`

These hashes establish artifact identity only. Passing tests, repeated seeds, and AI agreement are non-independent process evidence.

## Authorship and AI disclosure

Thomas Ryan is the sole human author and accountable operator. AI systems assisted with literature triage, adversarial prior-art review, protocol design, code drafting, deterministic execution, figure generation, manuscript drafting, and checks. AI systems are not authors or independent validators. Thomas Ryan authorized the public v1.0.0 release on 29 August 2026.

## Publication state

The archival v1.0.0 record is [10.5281/zenodo.22166381](https://doi.org/10.5281/zenodo.22166381). The matching source package is under [`paper10/`](https://github.com/Atomics-hub/consciousness-research/tree/main/paper10), with tag [`paper10-v1.0.0`](https://github.com/Atomics-hub/consciousness-research/releases/tag/paper10-v1.0.0).
