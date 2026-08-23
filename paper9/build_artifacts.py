#!/usr/bin/env python3
"""Build Paper 9 tables and figures directly from frozen JSON artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "results"
OUT = ROOT
FIG = OUT / "figures"
TAB = OUT / "tables"


def load(name: str):
    return json.loads((DATA / name).read_text())


def write_csv(path: Path, rows: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def style_ax(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#d7dde5", linewidth=0.6, alpha=0.7)


def build_workflow():
    fig, ax = plt.subplots(figsize=(11, 3.3))
    ax.axis("off")
    boxes = [
        (0.02, "Source model", "45,669 neurons\n1,513,231 edges"),
        (0.22, "Local gate", "held-out derivatives\n1% frozen margin"),
        (0.42, "Ordinary ladder", "25%, 50%, 100%\n24 trajectories"),
        (0.62, "Causal gate", "+0.01 block impulse\ntwo solver steps"),
        (0.82, "Hostile control", "matched local error\nstop before holdout"),
    ]
    colors = ["#e8f1fa", "#eef7ed", "#fff4df", "#f4ecfa", "#fbeaea"]
    for i, (x, title, body) in enumerate(boxes):
        rect = FancyBboxPatch((x, .30), .16, .46, boxstyle="round,pad=.015,rounding_size=.02",
                              facecolor=colors[i], edgecolor="#34495e", linewidth=1.1)
        ax.add_patch(rect)
        ax.text(x + .08, .64, title, ha="center", va="center", fontsize=10, fontweight="bold")
        ax.text(x + .08, .45, body, ha="center", va="center", fontsize=8.5, linespacing=1.35)
        if i < len(boxes) - 1:
            ax.add_patch(FancyArrowPatch((x + .165, .53), (boxes[i + 1][0] - .005, .53),
                                         arrowstyle="-|>", mutation_scale=12, color="#6b7280"))
    ax.text(.5, .12, "Exact shams, wrong controls, topology checks, and predeclared kill rules at every stage",
            ha="center", fontsize=9, color="#374151")
    fig.tight_layout()
    fig.savefig(FIG / "fig1_staged_design.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def build_local():
    obj = load("d1b_local_calibration.json")
    families = ["timescale", "two_state", "shunt"]
    blocks = ["Mi1", "T4a", "T5a"]
    vals = np.zeros((3, 3))
    rows = []
    for i, fam in enumerate(families):
        source = obj["selected_shunt"]["blocks"] if fam == "shunt" else obj["frozen_families"][fam]
        for j, block in enumerate(blocks):
            rec = source[block]
            vals[i, j] = 100 * rec["aggregate"]["nrmse"]
            rows.append({"family": fam, "block": block, "local_nrmse_percent": vals[i, j],
                         "passes_complete_gate": rec["passes"]})
    write_csv(TAB / "table_local_calibration.csv", rows)
    fig, ax = plt.subplots(figsize=(6.7, 3.5))
    im = ax.imshow(vals, cmap="YlOrRd", vmin=0, vmax=2)
    for i in range(3):
        for j in range(3):
            ax.text(j, i, f"{vals[i,j]:.3f}%\n{'PASS' if vals[i,j] <= 1 else 'FAIL'}",
                    ha="center", va="center", fontsize=9, color="black")
    ax.set_xticks(range(3), blocks)
    ax.set_yticks(range(3), ["Timescale", "Two-state", "Shunt"])
    ax.set_title("Checkpoint 007 local derivative calibration")
    cbar = fig.colorbar(im, ax=ax, shrink=.8)
    cbar.set_label("NRMSE (%)")
    fig.tight_layout()
    fig.savefig(FIG / "fig2_local_calibration.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def global_rows():
    rows = []
    for checkpoint, filename in [("008", "d1b_global_holdout.json"), ("009", "d1b_global_replication.json")]:
        obj = load(filename)
        for block, families in obj["outcomes"].items():
            for family, ladder in families.items():
                for rec in ladder:
                    row = {"checkpoint": checkpoint, "block": block, "family": family,
                           "classification": rec["classification"]}
                    if "fraction" in rec:
                        row.update({"fraction": rec["fraction"],
                                    "block_nrmse_percent": 100 * rec["ordinary"]["block_nrmse"],
                                    "all_node_nrmse_percent": 100 * rec["ordinary"]["all_node_nrmse"],
                                    "decoder_nrmse_percent": 100 * rec["decoder"]["nrmse"]})
                    else:
                        row.update({"fraction": "", "block_nrmse_percent": "",
                                    "all_node_nrmse_percent": "", "decoder_nrmse_percent": ""})
                    rows.append(row)
    return rows


def build_global():
    rows = global_rows()
    write_csv(TAB / "table_global_ladder.csv", rows)
    full = [r for r in rows if r["fraction"] == 1.0 and r["classification"] == "G1"]
    labels = [f"{r['checkpoint']} {r['block']}\n{r['family'].replace('_','-')}" for r in full]
    neural = [r["block_nrmse_percent"] for r in full]
    decoder = [r["decoder_nrmse_percent"] for r in full]
    x = np.arange(len(full))
    fig, ax = plt.subplots(figsize=(11, 5.2))
    ax.bar(x - .19, neural, .38, label="Replaced-block response", color="#4c78a8")
    ax.bar(x + .19, decoder, .38, label="Frozen decoder", color="#f58518")
    ax.axhline(1, color="#b91c1c", linestyle="--", linewidth=1.2, label="Frozen 1% margin")
    ax.set_xticks(x, labels, rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("NRMSE (%)")
    ax.set_title("Full-block replacement remained below ordinary and decoder margins")
    ax.legend(frameon=False, ncol=3, loc="upper left")
    style_ax(ax)
    fig.tight_layout()
    fig.savefig(FIG / "fig3_global_full_replacement.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def causal_rows():
    specs = [
        ("008", ".02", "d1b_causal_holdout_008.json"),
        ("008", ".01", "d1b_causal_holdout_008_dt001.json"),
        ("009", ".02", "d1b_causal_replication.json"),
        ("009", ".01", "d1b_causal_solver_dt001.json"),
    ]
    rows = []
    for checkpoint, dt, filename in specs:
        obj = load(filename)
        for block, families in obj["outcomes"].items():
            for family, rec in families.items():
                if rec["classification"] == "NOT_TESTED":
                    continue
                rows.append({
                    "checkpoint": checkpoint, "dt": dt, "block": block, "family": family,
                    "classification": rec["classification"],
                    "ordinary_nrmse_percent": 100 * rec["ordinary_nrmse"],
                    "neural_effect_nrmse_percent": 100 * rec["neural_effect"]["effect_nrmse"],
                    "block_effect_nrmse_percent": 100 * rec["neural_effect"]["block_effect_nrmse"],
                    "decoder_effect_nrmse_percent": 100 * rec["decoder_effect"]["effect_nrmse"],
                    "neural_effect_cosine": rec["neural_effect"]["effect_cosine"],
                })
    return rows


def build_causal():
    rows = causal_rows()
    write_csv(TAB / "table_causal_effects.csv", rows)
    mi1 = [r for r in rows if r["block"] == "Mi1" and r["family"] == "timescale"]
    labels = [f"CP {r['checkpoint']}\ndt={r['dt']}" for r in mi1]
    x = np.arange(len(mi1))
    fig, ax = plt.subplots(figsize=(7.6, 4.5))
    ax.bar(x - .2, [r["neural_effect_nrmse_percent"] for r in mi1], .4,
           label="Network effect", color="#54a24b")
    ax.bar(x + .2, [r["decoder_effect_nrmse_percent"] for r in mi1], .4,
           label="Decoder effect", color="#e45756")
    ax.axhline(1, color="#b91c1c", linestyle="--", linewidth=1.2, label="1% effect margin")
    ax.set_xticks(x, labels)
    ax.set_ylabel("Effect NRMSE (%)")
    ax.set_title("Replicated Mi1 timescale discrepancy was gain-like and solver-robust at the decoder")
    ax.legend(frameon=False)
    style_ax(ax)
    fig.tight_layout()
    fig.savefig(FIG / "fig4_causal_gain.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def build_decision():
    labels = ["Eligible ordinary\nladder cells", "Ordinary failures\n(G2)",
              "Initial causal\nflags", "Cross-checkpoint +\nsolver-robust seams", "Matched-error\nconfirmations"]
    vals = [45, 0, 5, 1, 0]
    colors = ["#4c78a8", "#59a14f", "#f28e2b", "#e15759", "#76b7b2"]
    fig, ax = plt.subplots(figsize=(8.4, 4.4))
    bars = ax.bar(range(len(vals)), vals, color=colors)
    ax.set_xticks(range(len(vals)), labels)
    ax.set_ylabel("Count")
    ax.set_title("Adversarial filtering reduced an apparent causal signal to no confirmatory result")
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width()/2, val + .7, str(val), ha="center", fontweight="bold")
    ax.set_ylim(0, 50)
    style_ax(ax)
    fig.tight_layout()
    fig.savefig(FIG / "fig5_decision_funnel.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def build_summary():
    d1b_local = load("d1b_local_calibration.json")
    g8 = load("d1b_global_holdout.json")
    g9 = load("d1b_global_replication.json")
    d1c = load("d1c_matched_calibration.json")
    summary = {
        "local_status": d1b_local["status"],
        "global_checkpoint_008": g8["classification_counts"],
        "global_checkpoint_009": g9["classification_counts"],
        "eligible_ordinary_cells": g8["classification_counts"]["G1"] + g9["classification_counts"]["G1"],
        "ordinary_composition_failures": g8["classification_counts"]["G2"] + g9["classification_counts"]["G2"],
        "d1c_status": d1c["status"],
        "d1c_selected_shunt": d1c.get("selected_shunt"),
    }
    (TAB / "results_summary.json").write_text(json.dumps(summary, indent=2) + "\n")


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    TAB.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
    build_workflow()
    build_local()
    build_global()
    build_causal()
    build_decision()
    build_summary()
    print(f"Built figures in {FIG}")
    print(f"Built tables in {TAB}")


if __name__ == "__main__":
    main()
