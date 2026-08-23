#!/usr/bin/env python3
"""Fail-closed audit for the Paper 9 internal release candidate."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from PIL import Image
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "results"
MANUSCRIPT = ROOT / "manuscript.md"


def sha256(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def require(condition: bool, message: str):
    if not condition:
        raise AssertionError(message)


def main():
    expected_hashes = {
        "d1b_source_ensemble.json": "bf75b64246b03d74a0e2a4d4c95d5814acc1b890d07914ab943498973647d8b4",
        "d1b_local_calibration.json": "e6cc59d71a575a506887f98049d7bf7c54edb11f40be079a90078269fb68c5b2",
        "d1b_global_holdout.json": "3fb0c10d5b87ecad9611b8dacb391a0c6e329b2b06ff215b3fcb2371c3b275ea",
        "d1b_global_replication.json": "e0eacb7d4ba5bd62ba46bcabbf973632b48e1abd8d2cb300f9f047277b1f66ac",
        "d1b_causal_holdout_008.json": "c82943c693812a9caa7381bf95a014100c5bf72e3d6ffbd4bb927d91057c5e15",
        "d1b_causal_holdout_008_dt001.json": "a432f2301aef88265b41882b8f0eb77df36ecdc407c051bd1f4786f65a8cb1bd",
        "d1b_causal_replication.json": "f8d3b13077b2267848dd3f662f9b5f57435101027a825951407162e6e7159bfe",
        "d1b_causal_solver_dt001.json": "6fa0ff3a30cdbe0971987c83d80f314d8bd46e92ee4d812fcac3b40feb2baa12",
        "d1c_source_effect_scale.json": "788d37daeb958c67744ab0521859e9d32000bf8ed8345ce559d9d3bc27df0fa4",
        "d1c_matched_calibration.json": "e995351ba010651bac055127d13ca16be074dfc615cc9e8ac8d979d698b27268",
    }
    for name, expected in expected_hashes.items():
        require(sha256(DATA / name) == expected, f"hash mismatch: {name}")

    g8 = json.loads((DATA / "d1b_global_holdout.json").read_text())
    g9 = json.loads((DATA / "d1b_global_replication.json").read_text())
    require(g8["classification_counts"] == {"G0": 2, "G1": 21, "G2": 0}, "CP008 counts")
    require(g9["classification_counts"] == {"G0": 1, "G1": 24, "G2": 0}, "CP009 counts")

    local = json.loads((DATA / "d1b_local_calibration.json").read_text())
    require(local["frozen_families"]["two_state"]["T5a"]["passes"] is False, "T5a two-state gate")
    require(local["selected_shunt"]["gamma"] == 0.01, "selected shunt gamma")

    d1c = json.loads((DATA / "d1c_matched_calibration.json").read_text())
    require(d1c["status"] == "FAIL", "D1C must remain failed")
    require(d1c["selected_shunt"] is None, "D1C must not have selected a shunt")

    with (ROOT / "tables/table_global_ladder.csv").open() as handle:
        global_rows = list(csv.DictReader(handle))
    require(len(global_rows) == 48, f"expected 48 global ladder rows, found {len(global_rows)}")

    figures = sorted((ROOT / "figures").glob("fig*.png"))
    require(len(figures) == 5, "expected five main figures")
    for figure in figures:
        with Image.open(figure) as image:
            require(image.width >= 1200 and image.height >= 800, f"low-resolution figure: {figure.name}")

    text = MANUSCRIPT.read_text()
    required_phrases = [
        "no ordinary composition failure occurred",
        "checkpoints 013–014 remained unexposed",
        "does not establish connectome sufficiency",
        "Thomas Ryan is the sole human author",
        "AI systems are not authors",
    ]
    for phrase in required_phrases:
        require(phrase in text, f"missing claim boundary: {phrase}")

    forbidden = ["field-shifting result", "proves that", "consciousness was preserved", "AI co-author"]
    for phrase in forbidden:
        require(phrase.lower() not in text.lower(), f"forbidden manuscript phrase: {phrase}")

    pdf_path = ROOT / "ryan_2026_stress_testing_local_neural_dynamics_equivalence.pdf"
    pdf = PdfReader(str(pdf_path))
    require(len(pdf.pages) == 9, f"unexpected main PDF page count: {len(pdf.pages)}")
    pdf_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    for token in ["turn33search", "turn34view", "PLACEHOLDER", "[missing image"]:
        require(token not in pdf_text, f"PDF contains internal/placeholder token: {token}")
    require("Thomas Ryan" in pdf_text and "References" in pdf_text, "PDF text extraction incomplete")
    require(pdf.metadata.title.startswith("Stress-Testing"), "incorrect PDF title metadata")

    supplement = PdfReader(str(ROOT / "ryan_2026_paper9_supplement.pdf"))
    require(len(supplement.pages) >= 2, "supplement PDF unexpectedly short")

    print("PASS: hashes, classifications, tables, figures, claim boundaries, and PDFs verified")


if __name__ == "__main__":
    main()
