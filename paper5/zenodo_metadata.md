# Zenodo Metadata For Paper 5

## Files

Recommended Zenodo upload:

- `paper5/ryan_2026_causal_preservation_under_substrate_transfer.pdf`

Recommended not to upload the code zip to the preprint record if you want the PDF preview to stay prominent. Preserve code, configs, generated figures, and result artifacts through a GitHub release snapshot instead.

## Basic Information

Resource type: Publication / Preprint

Title: Causal Preservation Under Substrate Transfer: Interchange Intervention Tests for Source-Specific Functional Continuity

Publication date: 2026-06-25

DOI: 10.5281/zenodo.20852042

Concept DOI for all versions: 10.5281/zenodo.20852041

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

This preprint adds a causal-intervention layer to PreservationBench-AST. Earlier PreservationBench papers showed that copied provenance, report continuity, task competence, proxy reward, source-like control, recurrent history dependence, and perturbation response can dissociate after substrate transfer. This paper asks a sharper question: when a target resembles a source from the outside, does it preserve the source's behaviorally relevant causal mechanisms, or only match selected behavioral and report surfaces?

The paper introduces causal-preservation tests using interchange interventions. For paired source histories A and B, source activation interventions are first selected for source-side causal leverage. Source-B schema-state or attention-state activations are then patched into source or target context A, and the patched target is compared with the source's own counterfactual response. The evaluated conditions are source_full, copied source attention, behavior-only distillation, and frozen random target state.

In the 22-validated-source schema-state panel, copied attention follows donor-specific source counterfactuals better than behavior distillation and frozen random controls under forced action-mismatch donors. Copied attention reaches 0.689 donor-specific action agreement with a 0.549 specificity gap, compared with 0.361 and 0.164 for behavior distillation and frozen random. In the attention-state panel, copied attention reaches 0.864 donor-specific agreement under both matched and action-mismatch donors, while behavior distillation reaches 0.188 and 0.267.

A harder attention-state donor-action-mismatch follow-up decouples the source counterfactual action from the donor's ordinary source-B action. This weakens copied attention's discrete action advantage but preserves a large Q-geometry advantage over behavior distillation and frozen random controls. A bidirectional target-to-source attention follow-up then patches each condition's target-B attention activations back into source context A. Copied-attention target state recovers the source's counterfactual action in 0.938 of rows, compared with 0.210 for behavior distillation and 0.199 for frozen random.

The bounded conclusion is that causal intervention tests can separate source-specific mechanism preservation from ordinary behavior matching in this toy benchmark. The result does not measure consciousness, personal identity, survival, biological preservation, whole-agent equivalence, or whether Attention Schema Theory is true.

## Keywords

mind preservation; causal preservation; functional continuity; substrate transfer; Attention Schema Theory; artificial consciousness; self-model; attention; neural agents; benchmark; PreservationBench; causal abstraction; interchange interventions; activation patching; source-state continuity; model transfer; behavior distillation

## Related Works

- References: `10.5281/zenodo.19374628`
- References: `10.5281/zenodo.19738204`
- References: `10.5281/zenodo.20480505`
- References: `10.5281/zenodo.20705654`
- Is supplemented by: `https://github.com/Atomics-hub/consciousness-research/releases/tag/paper5-v1.0.0`

## Software

Repository URL: `https://github.com/Atomics-hub/consciousness-research`

Programming language: Python

Development status: Concept

Stable release snapshot: `https://github.com/Atomics-hub/consciousness-research/releases/tag/paper5-v1.0.0`

## Suggested Citation

Ryan, T. (2026). *Causal Preservation Under Substrate Transfer: Interchange Intervention Tests for Source-Specific Functional Continuity* (v1.0.0). Zenodo. https://doi.org/10.5281/zenodo.20852042

## BibTeX

```bibtex
@article{ryan2026causalpreservation,
  title={Causal Preservation Under Substrate Transfer: Interchange Intervention Tests for Source-Specific Functional Continuity},
  author={Ryan, Thomas},
  year={2026},
  doi={10.5281/zenodo.20852042},
  publisher={Zenodo},
  note={Version v1.0.0}
}
```
