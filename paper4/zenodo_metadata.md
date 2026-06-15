# Zenodo Metadata For Paper 4

## Files

Recommended Zenodo upload:

- `paper4/ryan_2026_history_dependent_functional_continuity.pdf`

Recommended not to upload the code zip to the preprint record if you want the PDF preview to stay prominent. Preserve code and generated assets through a GitHub release snapshot instead.

## Basic Information

Resource type: Publication / Preprint

Title: History-Dependent Functional Continuity Under Delayed and Counterfactual Source-State Probes

Publication date: 2026-06-15

DOI: 10.5281/zenodo.20705654

Version: v1.0.0

Publisher: Zenodo

Language: English

License: Creative Commons Attribution 4.0 International

Copyright: (c) 2026 Thomas Ryan.

## Authors / Creators

Ryan, Thomas

Role: Researcher

Affiliation: Independent Researcher, San Francisco, CA

## Description

This preprint extends PreservationBench-AST with delayed, counterfactual, and perturbation-based source-state probes. The paper asks whether the strongest prior copied-attention condition was merely a clean-episode shortcut or whether it preserved source-like history-dependent responses under harder stress families.

The copied-attention condition is evaluated against frozen random target state across thirteen 22-seed validated-source recurrent stress families and one 22-seed perturbation family. The recurrent families include selected source-policy histories, deterministic unselected histories, shifted-policy histories, random-policy histories, scripted-cycle histories, longer report delays, longer histories, and an alternate random master seed.

Across all thirteen recurrent families, copied attention remained separated from frozen random on warm-action agreement, source-hidden-state distance, and report-delta distance. Warm-action improvement ranged from 0.653 to 0.756, hidden-state MSE improvement ranged from 0.0961 to 0.1027, and report-delta improvement remained positive but smaller, ranging from 0.0022 to 0.0030. In the perturbation layer, copied attention reached 0.850 perturbed-action agreement versus 0.214 for frozen random and had near-zero attention-delta distance to source.

The result supports a bounded toy-benchmark conclusion: copied attention/source-state machinery preserves source-like history-dependent and perturbation-dependent response profiles better than frozen random target state. It does not measure consciousness, personal identity, survival, biological preservation, or whole-agent equivalence.

## Keywords

mind preservation; functional continuity; substrate transfer; Attention Schema Theory; artificial consciousness; self-model; attention; neural agents; benchmark; preservation benchmark; recurrent probes; perturbation probes; source-state continuity; model transfer; history dependence

## Related Works

- References: `10.5281/zenodo.19374628`
- References: `10.5281/zenodo.19738204`
- References: `10.5281/zenodo.20480505`
- Is supplemented by: `https://github.com/Atomics-hub/consciousness-research/releases/tag/paper4-v1.0.0`

## Software

Repository URL: `https://github.com/Atomics-hub/consciousness-research`

Programming language: Python

Development status: Concept

Stable release snapshot: `https://github.com/Atomics-hub/consciousness-research/releases/tag/paper4-v1.0.0`

## Suggested Citation

Ryan, T. (2026). *History-Dependent Functional Continuity Under Delayed and Counterfactual Source-State Probes* (v1.0.0). Zenodo. https://doi.org/10.5281/zenodo.20705654

## BibTeX

```bibtex
@article{ryan2026historydependentcontinuity,
  title={History-Dependent Functional Continuity Under Delayed and Counterfactual Source-State Probes},
  author={Ryan, Thomas},
  year={2026},
  doi={10.5281/zenodo.20705654},
  publisher={Zenodo},
  note={Version v1.0.0}
}
```
