# Paper 4

Working title:

**History-Dependent Functional Continuity Under Delayed and Counterfactual Source-State Probes**

This directory contains the Paper 4 protocol, generated assets, and manuscript draft.

## Current Claim

In the PreservationBench-AST toy domain, copied attention/source-state machinery remains separated from frozen random target state across recurrent stress families, perturbation probes, delayed report probes, and non-source-policy histories.

This is not a consciousness, identity, survival, biological preservation, or whole-agent equivalence claim.

## Generate Assets

From the repository root:

```bash
.venv/bin/python paper4/generate_assets.py
```

Generated outputs:

- `paper4/tables/paper4_results_summary.json`
- `paper4/tables/paper4_results_summary.md`
- `paper4/figures/fig1_recurrent_stress_sweep.png`
- `paper4/figures/fig2_perturbation_layer.png`

Compact source contrast snapshots are stored in `paper4/source_contrasts/`. The full local run directories are intentionally not required for the release build.

## Build PDF

```bash
.venv/bin/python paper4/build_pdf.py
```

Output:

- `paper4/ryan_2026_history_dependent_functional_continuity.pdf`

## Status

Published on Zenodo 2026-06-15: https://doi.org/10.5281/zenodo.20705654.
