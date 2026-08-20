# Paper 8: The Binding Test

This directory contains the public source and reproducibility release for:

**The Binding Test: Construction Audit, Synthetic Planning, and an Exploratory
Feasibility Case Study of Causal Choice-Control Evaluation for AI Systems**

- Author: Thomas Ryan
- Version: v1.0.0
- Zenodo DOI: [10.5281/zenodo.22020047](https://doi.org/10.5281/zenodo.22020047)
- License: CC BY 4.0

The paper reports a sealed zero-call construction audit, seeded synthetic
planning calculations, and separately labeled exploratory provider-route
feasibility observations. It does not report a confirmatory causal effect.

## Contents

- `ryan_2026_binding_test_methods_feasibility.pdf` — publication PDF
- `reproducibility/` — exact unpacked contents of the v1.0.0 Zenodo
  reproducibility archive (108 payloads)
- `reproducibility/outputs/paper8_methods_feasibility_preprint_v0/` — final
  manuscript source, citation metadata, release scripts, and verification tools
- `reproducibility/zero_call/` — construction-audit implementation, tests,
  sealed outputs, and manifests

The canonical archived release is the Zenodo record. The GitHub copy is
provided for source browsing and development history.

## Local test command

From `paper8/reproducibility/`, run:

```sh
PYTHONPATH=.:zero_call python3 -B -m unittest discover -s zero_call/tests
```

The release was checked with Python 3.14: 120 tests passed.
