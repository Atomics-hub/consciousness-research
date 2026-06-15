# Paper 4 Release Notes

## Release

Tag: `paper4-v1.0.0`

Title: Paper 4 preprint v1.0.0 - History-dependent functional continuity stress tests

## Paper

**History-Dependent Functional Continuity Under Delayed and Counterfactual Source-State Probes**

Zenodo DOI: https://doi.org/10.5281/zenodo.20705654

This release packages the Paper 4 preprint and the code/results state used for the PreservationBench-AST recurrent and perturbation stress-test suite.

The paper asks whether the copied-attention condition from Paper 3 was merely a clean-episode shortcut or whether it preserves source-like history-dependent responses under delayed, counterfactual, and perturbation probes. The benchmark remains a toy functional benchmark. It is not a consciousness test, personal-identity test, survival claim, biological preservation claim, or whole-agent equivalence result.

## Core Result

The copied-attention condition is evaluated against frozen random target state across thirteen 22-seed validated-source recurrent stress families and one 22-seed perturbation family.

- recurrent warm-action improvement over frozen random ranged from 0.653 to 0.756
- recurrent hidden-state MSE improvement ranged from 0.0961 to 0.1027
- recurrent report-delta improvement remained positive but smaller, ranging from 0.0022 to 0.0030
- copied attention reached 0.850 perturbed-action agreement versus 0.214 for frozen random in the perturbation layer
- report continuity remains the fragile channel, and the copied-attention condition narrows the substrate gap by design

## Included Assets

- `paper4/ryan_2026_history_dependent_functional_continuity.pdf`
- `paper4/manuscript.md`
- `paper4/figures/`
- `paper4/tables/`
- `paper4/source_contrasts/`
- `paper4/protocol.md`
- `experiments/preservation_bench/`

## Reproduction Entry Point

```bash
.venv/bin/python paper4/generate_assets.py
.venv/bin/python paper4/build_pdf.py
```

The full local run directories are large and are not required for the release build. The paper uses compact contrast snapshots in `paper4/source_contrasts/`, with original source run paths documented in `paper4/protocol.md`.

## License

Creative Commons Attribution 4.0 International.
