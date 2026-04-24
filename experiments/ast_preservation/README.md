# AST Preservation Pilot

This directory contains the code and saved artifacts for Paper 2:

**An Exploratory Transplant Assay for Attention Schema Theory in a Toy Neural Agent**

The experiment is a single-seed exploratory pilot. It should be read as a test of a narrow engineering question: whether a frozen copy of an AST-style attention schema and self-model preserves supervised self-report behavior after transfer to a different neural architecture. It is not a test of whether the agent is conscious.

## Environment

Tested locally with:

- Python 3.14.3
- PyTorch 2.11.0
- NumPy 2.4.2
- SciPy 1.17.1
- Matplotlib 3.10.8
- Markdown 3.10.2
- WeasyPrint 68.1

Install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r experiments/ast_preservation/requirements.txt
```

On macOS, if the scientific stack raises a duplicate OpenMP runtime error, prefix the command with:

```bash
KMP_DUPLICATE_LIB_OK=TRUE OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 experiments/ast_preservation/run_all.py
```

## Reproduce

From the repository root:

```bash
python3 experiments/ast_preservation/run_all.py
python3 experiments/ast_preservation/analysis/generate_figures.py
python3 paper2/build_pdf.py
```

`run_all.py` runs the four phases sequentially:

1. Train the source Substrate A agent.
2. Evaluate ablations.
3. Run the frozen schema/self-model transplant assay.
4. Run the exploratory Phi-star side analysis.

Outputs:

- Checkpoints: `experiments/ast_preservation/checkpoints/`
- JSON results: `experiments/ast_preservation/results/`
- Figures: `paper2/figures/`
- PDF: `paper2/ryan_2026_preservation_test_ast.pdf`

The checked-in artifacts include the saved checkpoint and result JSONs used in the current draft.

## Important Caveats

- The experiment uses one trained source checkpoint and one global seed (`Config.seed = 42`).
- Episode-level tests estimate conditional performance for that checkpoint; they do not establish robustness across independent training seeds.
- Self-report is directly supervised with an attention-reconstruction loss, so the ablation is a supervised report-pathway test, not evidence of emergent metacognition.
- The schema-ablated condition emits a uniform self-report by construction.
- Copied schema/self-model modules are frozen during transplant fine-tuning, while the random control is trainable. This tests strict frozen direct portability, not all possible forms of schema transfer.
- The self-model fingerprint probes verify exact copied serialized state; they are not behavioral autobiographical memory tests.
- The theory-of-mind probe failed at this scale.
- The Phi-star analysis is an exploratory approximation under sparse state coverage, not a validated IIT 3.0 comparison.
