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

The associated code is in `experiments/ast_preservation/`. See [`experiments/ast_preservation/README.md`](experiments/ast_preservation/README.md) for reproduction commands and limitations.

## Repository Contents

```
paper/              Full paper (markdown source, PDF, build script)
paper/figures/      All 8 figures (PNG + PDF)
paper2/             Exploratory AST transplant-assay follow-up
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

```bibtex
@article{ryan2026preserved,
  title={What Must Be Preserved? Mapping Theories of Consciousness to Engineering Requirements for Mind Preservation},
  author={Ryan, Thomas},
  year={2026},
  doi={10.5281/zenodo.19374628},
  publisher={Zenodo}
}
```

## License

This work is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
