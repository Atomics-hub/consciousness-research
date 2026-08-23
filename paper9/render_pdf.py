#!/usr/bin/env python3
"""Render the Paper 9 Markdown manuscript with stable PDF metadata."""

from __future__ import annotations

import importlib.util
import argparse
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate


ROOT = Path(__file__).resolve().parent
BASE_RENDERER = ROOT / "pdf_renderer_base.py"


def load_renderer():
    spec = importlib.util.spec_from_file_location("base_pdf_renderer", BASE_RENDERER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("manuscript.md"))
    parser.add_argument("--output", type=Path, default=Path("ryan_2026_stress_testing_local_neural_dynamics_equivalence.pdf"))
    parser.add_argument("--title", default="Stress-Testing Local Neural-Dynamics Equivalence in a Connectome-Constrained Visual System")
    parser.add_argument("--subject", default="Paper 9 internal preprint draft")
    args = parser.parse_args()
    renderer = load_renderer()
    input_path = args.input if args.input.is_absolute() else ROOT / args.input
    output_path = args.output if args.output.is_absolute() else ROOT / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    styles = renderer.make_styles()
    page_width = letter[0] - 1.4 * inch
    story = renderer.build_story(input_path, styles, page_width)
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title=args.title,
        author="Thomas Ryan",
        subject=args.subject,
        keywords="connectome, neural dynamics, compositional equivalence, Drosophila, perturbation effects",
    )
    doc.build(story, onFirstPage=renderer.add_page_number, onLaterPages=renderer.add_page_number)
    print(output_path)


if __name__ == "__main__":
    main()
