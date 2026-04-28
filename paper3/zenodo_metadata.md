# Zenodo Metadata For Paper 3

## Files

Recommended Zenodo upload:

- `paper3/ryan_2026_preservation_benchmark_ast_v0.pdf`

Recommended not to upload the code zip to the preprint record if you want the PDF preview to stay prominent. The code is preserved through the GitHub release below.

## Basic Information

Resource type: Publication / Preprint

Title: The Preservation Benchmark: Testing Functional Continuity Across Substrate Transfer

Publication date: 2026-04-28

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

This preprint introduces PreservationBench, a benchmark framework for measuring preservation-relevant functional continuity after a source agent is copied, transplanted, adapted, or relearned in a target substrate. The benchmark is not a consciousness test and does not decide personal identity. It asks which source-specific functions remain active after transfer, and which apparent recoveries are better explained by relearning, behavioral mimicry, or proxy optimization.

As an initial validation tier, the paper implements PreservationBench-AST v0 in a toy neural agent inspired by Attention Schema Theory. A source agent is trained in a small grid-world task with attention control, self-report, and source-specific identity probes. Selected source modules are transferred into a target architecture under matched controls: frozen copied state, source-alignment repair, copied attention, source-facing attention and control bridges, behavior-only distillation, and frozen random controls.

In an expanded core replication, 30 independent source seeds were attempted and 22 passed source validation. Frozen copied schema and self-model state preserved source-specific identity-probe behavior but did not recouple report or control. Long source-alignment repair improved report but did not restore source-like task control. A source-facing attention bridge recovered report behavior without source-like action agreement. A control bridge drove reward and goal-attention mass above source levels but remained weak on goals found and source-action agreement, indicating proxy optimization rather than preserved control. Copying source attention yielded the strongest combined profile, with identity-probe preservation, high self-report, near-source goals found, and high source-action agreement, but this condition narrows the substrate gap.

## Keywords

mind preservation; functional continuity; substrate transfer; Attention Schema Theory; artificial consciousness; self-model; attention; neural agents; benchmark; preservation benchmark; computational neuroscience; philosophy of mind; whole-brain emulation; model transfer; identity probes; proxy optimization

## Related Works

- References: `10.5281/zenodo.19374628`
- References: `10.5281/zenodo.19738204`
- Is supplemented by: `https://github.com/Atomics-hub/consciousness-research/releases/tag/paper3-v1.0.0`

## Software

Repository URL: `https://github.com/Atomics-hub/consciousness-research`

Programming language: Python

Development status: Concept

Stable release snapshot: `https://github.com/Atomics-hub/consciousness-research/releases/tag/paper3-v1.0.0`

## Suggested Citation Before DOI Is Assigned

Ryan, T. (2026). *The Preservation Benchmark: Testing Functional Continuity Across Substrate Transfer* (v1.0.0). Zenodo.

## BibTeX Before DOI Is Assigned

```bibtex
@article{ryan2026preservationbench,
  title={The Preservation Benchmark: Testing Functional Continuity Across Substrate Transfer},
  author={Ryan, Thomas},
  year={2026},
  publisher={Zenodo},
  note={Version v1.0.0}
}
```
