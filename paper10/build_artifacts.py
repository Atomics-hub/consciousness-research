#!/usr/bin/env python3
"""Build Paper 10 figures and tables from frozen machine-readable results."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import mathtext
from matplotlib.font_manager import FontProperties
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
from matplotlib.ticker import LogFormatterMathtext, LogLocator


ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent
WORKING_SOURCE = PROJECT / "work" / "g0d_intervention_coverage"
PACKAGED_SOURCE = ROOT / "reproducibility" / "synthetic"
WORK = WORKING_SOURCE if WORKING_SOURCE.exists() else PACKAGED_SOURCE
FIG = ROOT / "figures"
TAB = ROOT / "tables"
MATH = FIG / "math"
MATH_DPI = 320
MATH_FONT_SIZE = 10.0


# Paul Tol's colorblind-safe bright palette, with neutral ink and grid colors.
BLUE = "#4477AA"
GREEN = "#228833"
YELLOW = "#CCBB44"
RED = "#CC3311"
PURPLE = "#AA3377"
GREY = "#667085"
INK = "#172033"
GRID = "#D9E0E8"


def load(name: str) -> dict:
    return json.loads((WORK / name).read_text())


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def style_axis(ax) -> None:
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#5F6B7A")
    ax.tick_params(colors=INK, labelsize=9)
    ax.grid(axis="y", color=GRID, linewidth=0.7, alpha=0.85)
    ax.set_axisbelow(True)


def save_figure(fig, name: str) -> None:
    fig.savefig(FIG / name, dpi=320, bbox_inches="tight", pad_inches=0.08, facecolor="white")
    plt.close(fig)


def math_asset_name(expression: str) -> str:
    normalized = " ".join(expression.strip().split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest() + ".png"


def build_math_assets() -> None:
    """Render every explicit Markdown math expression as a transparent PNG."""

    MATH.mkdir(parents=True, exist_ok=True)
    expressions: set[str] = set()
    for source in (ROOT / "manuscript.md", ROOT / "supplement.md"):
        text = source.read_text(encoding="utf-8")
        expressions.update(match.group(1).strip() for match in re.finditer(r"\$\$([^$]+?)\$\$", text, re.DOTALL))
        without_display = re.sub(r"\$\$[^$]+?\$\$", "", text, flags=re.DOTALL)
        expressions.update(match.group(1).strip() for match in re.finditer(r"(?<!\$)\$([^$\n]+?)\$(?!\$)", without_display))

    expected_names = {math_asset_name(expression) for expression in expressions}
    for existing in MATH.glob("*.png"):
        if existing.name not in expected_names:
            existing.unlink()

    properties = FontProperties(family="DejaVu Sans", size=MATH_FONT_SIZE)
    for expression in sorted(expressions):
        output = MATH / math_asset_name(expression)
        mathtext.math_to_image(
            f"${expression}$",
            output,
            prop=properties,
            dpi=MATH_DPI,
            format="png",
            color=INK,
        )


def build_claim_ladder() -> None:
    fig, ax = plt.subplots(figsize=(8.4, 4.65))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    battery = FancyBboxPatch(
        (0.025, 0.37), 0.205, 0.29,
        boxstyle="round,pad=.018,rounding_size=.018",
        facecolor="#EAF2F8", edgecolor=BLUE, linewidth=1.5,
    )
    ax.add_patch(battery)
    ax.text(0.1275, 0.565, "Finite intervention\nbattery", ha="center", va="center", fontsize=11.2, fontweight="bold")
    ax.text(0.1275, 0.445, "Observed discrepancies\non tested trajectories", ha="center", va="center", fontsize=9.1)

    boxes = [
        (0.315, 0.71, "Falsification", "One counterexample is decisive.\nA pass is battery-bounded.", "#FCEBE8", RED),
        (0.315, 0.39, "Distributional validation", "Needs an intervention law,\nsampling design, and error probability.", "#FFF5D6", YELLOW),
        (0.315, 0.07, "Worst-case certification", "Needs justified structure or global\nregularity plus domain coverage.", "#EAF6EE", GREEN),
    ]
    for x, y, title, body, fill, edge in boxes:
        box = FancyBboxPatch(
            (x, y), 0.285, 0.20,
            boxstyle="round,pad=.016,rounding_size=.016",
            facecolor=fill, edgecolor=edge, linewidth=1.4,
        )
        ax.add_patch(box)
        ax.text(x + 0.1425, y + 0.138, title, ha="center", va="center", fontsize=10.2, fontweight="bold")
        ax.text(x + 0.1425, y + 0.065, body, ha="center", va="center", fontsize=8.55)
        ax.add_patch(FancyArrowPatch((0.235, 0.515), (x - 0.008, y + 0.10), arrowstyle="-|>", mutation_scale=11, color=GREY, linewidth=1.05))

    assumptions = FancyBboxPatch(
        (0.68, 0.105), 0.29, 0.70,
        boxstyle="round,pad=.018,rounding_size=.018",
        facecolor="#F6F0F7", edgecolor=PURPLE, linewidth=1.5,
    )
    ax.add_patch(assumptions)
    ax.text(0.825, 0.72, "Required claim metadata", ha="center", fontsize=11.1, fontweight="bold")
    items = [
        "interface and observable",
        "intervention domain",
        "horizon and norm",
        "reachable-state scope",
        "candidate-inclusive coverage",
        "regularity / model class",
        "probability law, if used",
        "abstention or fail-closed rule",
    ]
    for index, item in enumerate(items):
        ax.text(0.715, 0.63 - 0.065 * index, f"• {item}", ha="left", va="center", fontsize=9.0)
    ax.add_patch(FancyArrowPatch((0.61, 0.17), (0.67, 0.30), arrowstyle="-|>", mutation_scale=11, color=GREY, linewidth=1.05))
    ax.add_patch(FancyArrowPatch((0.61, 0.49), (0.67, 0.49), arrowstyle="-|>", mutation_scale=11, color=GREY, linewidth=1.05))
    fig.subplots_adjust(left=0.01, right=0.99, top=0.98, bottom=0.02)
    save_figure(fig, "fig1_claim_ladder.png")


def build_stateful_counterexample() -> None:
    spec = load("frozen_spec.json")
    result = load("g0d_result.json")["stateful_piecewise_linear_counterexample"]
    cfg = spec["stateful_counterexample"]
    rng = np.random.default_rng(int(cfg["seed"]))
    inputs = rng.uniform(
        -float(cfg["input_bound"]),
        float(cfg["input_bound"]),
        size=(int(cfg["number_of_test_trajectories"]), int(cfg["horizon"])),
    )
    pairs = []
    for trajectory in inputs:
        states = np.zeros(len(trajectory) + 1)
        for time, value in enumerate(trajectory):
            pairs.append((states[time], value))
            states[time + 1] = float(cfg["source_decay"]) * states[time] + value
    pairs = np.asarray(pairs)
    center = np.asarray(result["center"])
    radius = float(result["support_radius"])
    fill_witness = np.asarray(result["fill_distance_witness"])

    fig, ax = plt.subplots(figsize=(8.0, 5.45))
    ax.scatter(pairs[:, 0], pairs[:, 1], s=14, alpha=0.48, color=BLUE, edgecolors="none", label="512 tested state-input pairs")
    ax.scatter(center[0], center[1], s=105, marker="*", color=RED, edgecolors="white", linewidths=0.5, zorder=5, label="Reachable unseen witness")
    ax.add_patch(Rectangle(
        (center[0] - radius, center[1] - radius), 2 * radius, 2 * radius,
        fill=False, edgecolor=RED, linewidth=1.7, linestyle="--", label="Bump support",
    ))
    ax.scatter(fill_witness[0], fill_witness[1], s=75, marker="X", color=PURPLE, edgecolors="white", linewidths=0.5, zorder=5, label="Approximate fill-distance witness")
    ax.set_xlabel("Source state")
    ax.set_ylabel("Intervention input")
    ax.set_title("A finite battery can miss a reachable switching region", pad=10)
    ax.set_xlim(-0.68, 0.90)
    ax.set_ylim(-0.50, 0.55)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(color=GRID, linewidth=0.65, alpha=0.75)
    ax.set_axisbelow(True)
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", bbox_to_anchor=(0.5, 0.01), ncol=2, frameon=False, fontsize=8.7, handletextpad=0.5, columnspacing=1.4)
    fig.subplots_adjust(left=0.11, right=0.98, top=0.90, bottom=0.21)
    save_figure(fig, "fig2_stateful_counterexample.png")


def build_coverage_comparison() -> None:
    exploratory = load("g0d_result.json")["coverage_comparison"]
    confirmation = load("confirmatory_result.json")["coverage_replications"]
    random_values = [row["median_random_fill_distance_approx"] for row in confirmation]
    regular_values = [row["regular_fill_distance_approx"] for row in confirmation]

    fig, axes = plt.subplots(1, 2, figsize=(8.5, 4.45), gridspec_kw={"width_ratios": [1.14, 0.86]})
    ax = axes[0]
    x = np.arange(len(confirmation))
    ax.bar(x - 0.18, regular_values, 0.36, label="Regular coverage", color=BLUE)
    ax.bar(x + 0.18, random_values, 0.36, label="Median random", color=YELLOW)
    ax.set_xticks(x, [f"R{i+1}" for i in range(len(x))])
    ax.set_ylabel("Approximate fill distance")
    ax.set_title("A  Frozen replications", loc="left", fontsize=10.5, fontweight="bold", pad=8)
    ax.set_ylim(0, 0.245)
    style_axis(ax)

    ax = axes[1]
    values = [
        exploratory["regular_fill_distance_approx"],
        exploratory["random_fill_distance_median_approx"],
    ]
    bars = ax.bar([0, 1], values, color=[BLUE, YELLOW], width=0.62)
    q05, q95 = exploratory["random_fill_distance_q05_q95_approx"]
    ax.errorbar(1, values[1], yerr=[[values[1] - q05], [q95 - values[1]]], color=INK, capsize=5, linewidth=1.2, zorder=4)
    ax.set_xticks([0, 1], ["8 x 8 regular\n(n=64)", "Random median\n(n=64, 100 runs)"])
    ax.set_ylabel("Approximate fill distance")
    ax.set_title("B  Exploratory construction", loc="left", fontsize=10.5, fontweight="bold", pad=8)
    ax.set_ylim(0, 0.315)
    ax.text(bars[0].get_x() + bars[0].get_width() / 2, values[0] + 0.009, f"{values[0]:.3f}", ha="center", fontsize=8.7)
    ax.text(1, q95 + 0.012, f"median {values[1]:.3f}\n90% range", ha="center", va="bottom", fontsize=8.3)
    style_axis(ax)
    handles = [
        Rectangle((0, 0), 1, 1, facecolor=BLUE, edgecolor="none", label="Regular coverage"),
        Rectangle((0, 0), 1, 1, facecolor=YELLOW, edgecolor="none", label="Median random"),
    ]
    fig.suptitle("Space-filling design reduces, but does not eliminate, unseen uncertainty", fontsize=12.2, fontweight="bold", y=0.98)
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0.895), ncol=2, frameon=False, fontsize=9, columnspacing=1.8)
    fig.subplots_adjust(left=0.09, right=0.985, top=0.75, bottom=0.18, wspace=0.36)
    save_figure(fig, "fig3_coverage_comparison.png")


def build_confirmation() -> None:
    packets = load("confirmatory_result.json")["packets"]
    labels = [row["packet_id"] for row in packets]
    unseen = [row["unseen_max_output_discrepancy"] for row in packets]
    bound = [row["lipschitz_certificate_upper_bound"] for row in packets]
    x = np.arange(len(labels))

    fig, ax = plt.subplots(figsize=(8.2, 4.85))
    ax.scatter(x - 0.08, unseen, s=58, marker="o", color=RED, edgecolors="white", linewidths=0.6, zorder=4)
    ax.scatter(x + 0.08, bound, s=62, marker="D", color=PURPLE, edgecolors="white", linewidths=0.6, zorder=4)
    for xpos, low, high in zip(x, unseen, bound):
        ax.plot([xpos, xpos], [low, high], color="#B7C0CC", linewidth=1.1, zorder=1)
    ax.axhline(0.05, color=RED, linestyle="--", linewidth=1.15)
    ax.axhline(0.01, color=INK, linestyle=":", linewidth=1.15)
    ax.set_yscale("log")
    ax.set_ylim(0.008, 3.2)
    ax.set_xticks(x, labels)
    ax.set_ylabel("Maximum output discrepancy")
    ax.set_title("Passing the tested battery did not produce a worst-case certificate", pad=12)
    ax.yaxis.set_major_locator(LogLocator(base=10, numticks=5))
    ax.yaxis.set_major_formatter(LogFormatterMathtext(base=10))
    ax.grid(axis="y", which="major", color=GRID, linewidth=0.75, alpha=0.9)
    ax.grid(False, which="minor")
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_axisbelow(True)
    for xpos, value in zip(x + 0.08, bound):
        ax.annotate(f"{value:.2f}", (xpos, value), textcoords="offset points", xytext=(0, 7), ha="center", fontsize=8.1, color=PURPLE)
    for xpos, value in zip(x - 0.08, unseen):
        ax.annotate(f"{value:.2f}", (xpos, value), textcoords="offset points", xytext=(0, -13), ha="center", fontsize=8.1, color=RED)

    legend_handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=RED, markeredgecolor="white", markersize=8, label="Reachable unseen witness"),
        Line2D([0], [0], marker="D", color="none", markerfacecolor=PURPLE, markeredgecolor="white", markersize=7.5, label="Sound coverage upper bound"),
        Line2D([0], [0], color=RED, linestyle="--", linewidth=1.2, label="Unseen-divergence gate (0.05)"),
        Line2D([0], [0], color=INK, linestyle=":", linewidth=1.2, label="Equivalence threshold (0.01)"),
    ]
    fig.legend(handles=legend_handles, loc="upper center", bbox_to_anchor=(0.5, 0.87), ncol=2, frameon=False, fontsize=8.6, columnspacing=1.6)
    fig.text(
        0.5, 0.93, "Tested battery discrepancy: 0.000 in C01-C05",
        ha="center", va="center", fontsize=9.5, fontweight="bold", color=GREEN,
        bbox={"boxstyle": "round,pad=0.35", "facecolor": "#EAF6EE", "edgecolor": GREEN, "linewidth": 0.8},
    )
    fig.subplots_adjust(left=0.11, right=0.98, top=0.72, bottom=0.14)
    save_figure(fig, "fig4_confirmatory_packets.png")


def build_dimensional_burden() -> None:
    rows = load("g0d_result.json")["dimensional_burden"]
    dimensions = [row["dimension"] for row in rows]
    necessary = [row["necessary_evaluation_lower_bound_unit_cube"] for row in rows]
    fig, ax = plt.subplots(figsize=(8.0, 4.65))
    ax.plot(dimensions, necessary, marker="o", markersize=6, linewidth=2.2, color=PURPLE)
    for d, n in zip(dimensions, necessary):
        label = rf"$10^{{{int(round(np.log10(n)))}}}$" if n >= 1000 else f"{n:,}"
        ax.annotate(label, (d, n), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=9.0)
    ax.set_yscale("log")
    ax.set_ylim(4, 3e12)
    ax.set_xticks(dimensions)
    ax.set_xlabel("Declared domain dimension")
    ax.set_ylabel("Necessary evaluations (lower bound)")
    fig.suptitle("Worst-case coverage scales exponentially without stronger structure", fontsize=12.2, fontweight="bold", y=0.97)
    fig.text(0.5, 0.895, "K = 1; target uniform error = 0.05 on the unit cube", ha="center", va="center", fontsize=9.2, color=GREY)
    style_axis(ax)
    ax.grid(axis="y", which="major", color=GRID, linewidth=0.75, alpha=0.9)
    ax.grid(False, which="minor")
    fig.subplots_adjust(left=0.105, right=0.98, top=0.80, bottom=0.15)
    save_figure(fig, "fig5_dimensional_burden.png")


def build_tables() -> None:
    exploratory = load("g0d_result.json")
    confirmation = load("confirmatory_result.json")
    packet_rows = []
    for row in confirmation["packets"]:
        packet_rows.append({
            "packet_id": row["packet_id"],
            "tested_trajectories": row["tested_trajectories"],
            "tested_state_input_pairs": row["tested_state_input_pairs"],
            "battery_max_discrepancy": row["battery_max_output_discrepancy"],
            "unseen_max_discrepancy": row["unseen_max_output_discrepancy"],
            "approximate_fill_distance": row["approximate_fill_distance"],
            "certificate_upper_bound": row["lipschitz_certificate_upper_bound"],
            "packet_pass": row["packet_pass"],
        })
    write_csv(TAB / "table_confirmatory_packets.csv", packet_rows)
    write_csv(TAB / "table_dimensional_burden.csv", exploratory["dimensional_burden"])
    write_csv(TAB / "table_coverage_replications.csv", confirmation["coverage_replications"])
    summary = {
        "exploratory_all_gates_pass": exploratory["all_frozen_gates_pass"],
        "confirmatory_all_gates_pass": confirmation["all_confirmatory_gates_pass"],
        "confirmatory_spec_sha256": confirmation["confirmatory_spec_sha256"],
        "exploratory_spec_sha256": exploratory["frozen_spec_sha256"],
        "confirmatory_packet_count": len(confirmation["packets"]),
        "claim_ceiling": confirmation["claim_ceiling"],
    }
    (TAB / "results_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")


def main() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    TAB.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.titlesize": 12,
        "axes.titleweight": "semibold",
        "axes.labelsize": 10,
        "axes.labelcolor": INK,
        "text.color": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "legend.fontsize": 9,
    })
    build_claim_ladder()
    build_stateful_counterexample()
    build_coverage_comparison()
    build_confirmation()
    build_dimensional_burden()
    build_math_assets()
    build_tables()
    print(f"Built {len(list(FIG.glob('*.png')))} figures, {len(list(MATH.glob('*.png')))} math assets, and {len(list(TAB.iterdir()))} tables")


if __name__ == "__main__":
    main()
