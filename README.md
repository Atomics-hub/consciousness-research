# What Must Be Preserved? Mapping Theories of Consciousness to Engineering Requirements for Mind Preservation

**Thomas Ryan** - Independent Researcher, San Francisco, CA

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19374628.svg)](https://doi.org/10.5281/zenodo.19374628)

## Abstract

The engineering of consciousness preservation (whether through whole-brain emulation, cryonic revival, or brain-computer interfaces) proceeds largely without reference to theories of consciousness. This is a remarkable omission. The choice of what must be preserved in a brain depends entirely on what generates consciousness, and the major theories disagree on this question by many orders of magnitude in their engineering implications.

This paper evaluates eight major theories of consciousness, including Integrated Information Theory (IIT 4.0), Global Neuronal Workspace Theory (GNWT), Higher-Order Thought theory (HOT), Predictive Processing / Free Energy Principle, Recurrent Processing Theory (RPT), Biological Computationalism, Orchestrated Objective Reduction (Orch OR), and Attention Schema Theory (AST), against nine preservation-relevant criteria. It derives specific engineering requirements from each theory's core postulates.

**Key findings:**

- The theories split **4-3-1** on substrate independence, the single most consequential question for preservation
- Required information content ranges from **~1-10 TB** (AST) to **physically impossible** (Orch OR)
- Required compute spans from **10^15 FLOPS** (achievable today) to **formally uncomputable**
- All eight theories converge on three requirements: temporal dynamics must be preserved, integration across components is necessary, and feedforward-only architectures are ruled out
- Biological preservation (cryonics with future revival) is the **only strategy compatible with all eight theories**
- A **"deflation paradox"** emerges: theories most favorable to preservation deflate consciousness to a functional property, while theories that take phenomenal experience most seriously make preservation hardest or impossible

## Paper

**[Read the paper on Zenodo](https://doi.org/10.5281/zenodo.19374628)**

The PDF is also available in this repo: [`paper/ryan_2026_what_must_be_preserved.pdf`](paper/ryan_2026_what_must_be_preserved.pdf)

## Paper 2

`paper2/` contains an exploratory follow-up preprint and runnable pilot experiment:

**An Exploratory Transplant Assay for Attention Schema Theory in a Toy Neural Agent**

**[Read Paper 2 on Zenodo](https://doi.org/10.5281/zenodo.19738204)**

The associated code is in `experiments/ast_preservation/`. See [`experiments/ast_preservation/README.md`](experiments/ast_preservation/README.md) for reproduction commands and limitations.

## Paper 3

`paper3/` contains a preprint-scale benchmark follow-up:

**The Preservation Benchmark: Testing Functional Continuity Across Substrate Transfer**

**[Read Paper 3 on Zenodo](https://doi.org/10.5281/zenodo.20480505)**

The PDF is available in this repo: [`paper3/ryan_2026_preservation_benchmark_ast_v0.pdf`](paper3/ryan_2026_preservation_benchmark_ast_v0.pdf)

The associated benchmark code is in `experiments/preservation_bench/`. See [`experiments/preservation_bench/README.md`](experiments/preservation_bench/README.md) for reproduction commands, validation rules, and limitations.

Stable release snapshot: [`paper3-v1.0.0`](https://github.com/Atomics-hub/consciousness-research/releases/tag/paper3-v1.0.0)

## Paper 4

`paper4/` contains a recurrent and perturbation stress-test follow-up:

**History-Dependent Functional Continuity Under Delayed and Counterfactual Source-State Probes**

**[Read Paper 4 on Zenodo](https://doi.org/10.5281/zenodo.20705654)**

The PDF is available in this repo: [`paper4/ryan_2026_history_dependent_functional_continuity.pdf`](paper4/ryan_2026_history_dependent_functional_continuity.pdf)

The associated benchmark code is in `experiments/preservation_bench/`. See [`experiments/preservation_bench/README.md`](experiments/preservation_bench/README.md) for reproduction commands, validation rules, and limitations.

Stable release snapshot: [`paper4-v1.0.0`](https://github.com/Atomics-hub/consciousness-research/releases/tag/paper4-v1.0.0)

## Paper 5

`paper5/` contains a causal-intervention follow-up:

**Causal Preservation Under Substrate Transfer: Interchange Intervention Tests for Source-Specific Functional Continuity**

**[Read Paper 5 on Zenodo](https://doi.org/10.5281/zenodo.20852042)**

The PDF is available in this repo: [`paper5/ryan_2026_causal_preservation_under_substrate_transfer.pdf`](paper5/ryan_2026_causal_preservation_under_substrate_transfer.pdf)

The associated benchmark code is in `experiments/preservation_bench/`. See [`paper5/reproducibility_checklist.md`](paper5/reproducibility_checklist.md) for causal-patching reproduction commands, validation checks, and limitations.

Stable release snapshot: [`paper5-v1.0.0`](https://github.com/Atomics-hub/consciousness-research/releases/tag/paper5-v1.0.0)

## Paper 6

`paper6/` contains a blinded scaffold-lesion follow-up on persistent coding agents:

**The Scaffold Continuity Trap: A Blinded Scaffold-Lesion Test in Persistent Coding Agents**

**[Read Paper 6 on Zenodo](https://doi.org/10.5281/zenodo.21342748)**

The PDF is available in this repo: [`paper6/ryan_2026_scaffold_continuity_trap.pdf`](paper6/ryan_2026_scaffold_continuity_trap.pdf)

The public package includes the manuscript, figures, result tables, release notes, and a reproducibility note. Coordinator-private scaffolding, hidden keys, blind packet archives, and runner return materials are intentionally excluded from the public repository.

Stable release snapshot: [`paper6-v1.0.0`](https://github.com/Atomics-hub/consciousness-research/releases/tag/paper6-v1.0.0)

## Paper 8

`paper8/` contains the Binding Test methods and exploratory-feasibility
preprint together with its complete public reproducibility package:

**The Binding Test: Construction Audit, Synthetic Planning, and an Exploratory
Feasibility Case Study of Causal Choice-Control Evaluation for AI Systems**

**[Read Paper 8 on Zenodo](https://doi.org/10.5281/zenodo.22020047)**

The PDF is available in this repo:
[`paper8/ryan_2026_binding_test_methods_feasibility.pdf`](paper8/ryan_2026_binding_test_methods_feasibility.pdf)

The exact unpacked 108-payload reproducibility archive is available under
[`paper8/reproducibility/`](paper8/reproducibility/). See
[`paper8/README.md`](paper8/README.md) for scope and claim limitations.

## Repository Contents

```
paper/              Full paper (markdown source, PDF, build script)
paper/figures/      All 8 figures (PNG + PDF)
paper2/             Exploratory AST transplant-assay follow-up
paper3/             PreservationBench AST v0 benchmark preprint
paper4/             Recurrent and perturbation stress-test follow-up
paper5/             Causal-preservation and interchange-intervention follow-up
paper6/             Blinded scaffold-lesion follow-up for persistent coding agents
paper8/             Binding Test methods, PDF, and reproducibility release
experiments/        Experiment code and saved results
writeups/           Supporting analyses
  ├── theory_comparator.md        8-theory comparison matrix
  ├── engineering_bridge_table.md  Theory → engineering requirements mapping
  ├── engineering_feasibility.md   Compute/scanning/storage analysis
  └── landscape_map.md            Companies, labs, people, funding
notes/              Deep research notes
  ├── neuroscience_state_of_field_2026.md
  ├── wbe_preservation_state_2026.md
  ├── philosophy_ai_consciousness_2026.md
  └── synthesis_and_open_problems.md
```

## Citation

Paper 1:

```bibtex
@article{ryan2026preserved,
  title={What Must Be Preserved? Mapping Theories of Consciousness to Engineering Requirements for Mind Preservation},
  author={Ryan, Thomas},
  year={2026},
  doi={10.5281/zenodo.19374628},
  publisher={Zenodo}
}
```

Paper 2:

```bibtex
@article{ryan2026asttransplant,
  title={An Exploratory Transplant Assay for Attention Schema Theory in a Toy Neural Agent},
  author={Ryan, Thomas},
  year={2026},
  doi={10.5281/zenodo.19738204},
  publisher={Zenodo}
}
```

Paper 3:

```bibtex
@article{ryan2026preservationbench,
  title={The Preservation Benchmark: Testing Functional Continuity Across Substrate Transfer},
  author={Ryan, Thomas},
  year={2026},
  doi={10.5281/zenodo.20480505},
  publisher={Zenodo},
}
```

Paper 4:

```bibtex
@article{ryan2026historydependentcontinuity,
  title={History-Dependent Functional Continuity Under Delayed and Counterfactual Source-State Probes},
  author={Ryan, Thomas},
  year={2026},
  doi={10.5281/zenodo.20705654},
  publisher={Zenodo}
}
```

Paper 5:

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

Paper 6:

```bibtex
@article{ryan2026scaffoldcontinuitytrap,
  title={The Scaffold Continuity Trap: A Blinded Scaffold-Lesion Test in Persistent Coding Agents},
  author={Ryan, Thomas},
  year={2026},
  doi={10.5281/zenodo.21342748},
  publisher={Zenodo},
  note={Version v1.0.0}
}
```

## License

This work is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
