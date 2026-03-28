"""
Visualize consciousness measures across simulated mental states.

Generates comparison plots showing how LZc, spectral entropy,
PCI approximation, and connectivity differ between awake, sleep,
and anesthesia states. Run with: python visualize_states.py
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from eeg_complexity import (
    generate_synthetic_eeg, preprocess, compute_lzc,
    compute_spectral_entropy, approximate_pci, compute_connectivity,
)

import warnings
warnings.filterwarnings("ignore")


def collect_measures(states=("awake", "sleep", "anesthesia"), n_channels=16):
    """Run all measures on synthetic data for each state."""
    results = {}
    for state in states:
        print(f"  Computing measures for {state}...")
        raw = generate_synthetic_eeg(duration_sec=60, n_channels=n_channels, state=state)
        raw = preprocess(raw)

        lzc = compute_lzc(raw)
        se = compute_spectral_entropy(raw)
        pci = approximate_pci(raw)
        conn = compute_connectivity(raw)

        results[state] = {
            "lzc": lzc["global_mean_lzc"],
            "se": se["global_mean_se"],
            "pci": pci["mean_pci_approx"],
            "lzc_per_ch": {ch: lzc[ch]["mean_lzc"] for ch in raw.ch_names},
            "se_per_ch": {ch: se[ch]["mean_se"] for ch in raw.ch_names},
            "lzc_timecourse": {ch: lzc[ch]["timecourse"] for ch in raw.ch_names},
            "conn": {band: data["mean_plv"] for band, data in conn.items()},
            "conn_matrices": {band: data["plv_matrix"] for band, data in conn.items()},
            "ch_names": raw.ch_names,
        }
    return results


def plot_bar_comparison(results, output_dir):
    """Bar chart comparing global measures across states."""
    states = list(results.keys())
    measures = {
        "Lempel-Ziv Complexity": [results[s]["lzc"] for s in states],
        "Spectral Entropy": [results[s]["se"] for s in states],
        "PCI Approximation": [results[s]["pci"] for s in states],
    }

    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    colors = {"awake": "#2ecc71", "sleep": "#3498db", "anesthesia": "#e74c3c"}
    bar_colors = [colors[s] for s in states]

    for ax, (name, values) in zip(axes, measures.items()):
        bars = ax.bar(states, values, color=bar_colors, edgecolor="white", linewidth=1.5)
        ax.set_title(name, fontsize=13, fontweight="bold")
        ax.set_ylim(0, max(values) * 1.3)
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                    f"{val:.3f}", ha="center", va="bottom", fontsize=11)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    fig.suptitle("Consciousness Complexity Measures by State", fontsize=15, fontweight="bold", y=1.02)
    plt.tight_layout()
    path = os.path.join(output_dir, "state_comparison.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path}")


def plot_connectivity_bands(results, output_dir):
    """PLV across frequency bands for each state."""
    states = list(results.keys())
    bands = list(results[states[0]]["conn"].keys())
    colors = {"awake": "#2ecc71", "sleep": "#3498db", "anesthesia": "#e74c3c"}

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(bands))
    width = 0.25

    for i, state in enumerate(states):
        values = [results[state]["conn"][b] for b in bands]
        ax.bar(x + i * width, values, width, label=state.capitalize(),
               color=colors[state], edgecolor="white", linewidth=1.5)

    ax.set_xticks(x + width)
    ax.set_xticklabels([b.capitalize() for b in bands], fontsize=11)
    ax.set_ylabel("Mean Phase Locking Value", fontsize=12)
    ax.set_title("Functional Connectivity (PLV) by Frequency Band", fontsize=14, fontweight="bold")
    ax.legend(fontsize=11)
    ax.set_ylim(0, 1.1)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    path = os.path.join(output_dir, "connectivity_bands.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path}")


def plot_lzc_timecourse(results, output_dir):
    """LZc timecourse showing stability/variability across states."""
    fig, axes = plt.subplots(3, 1, figsize=(12, 8), sharex=True, sharey=True)
    colors = {"awake": "#2ecc71", "sleep": "#3498db", "anesthesia": "#e74c3c"}

    for ax, (state, data) in zip(axes, results.items()):
        ch_names = data["ch_names"]
        for ch in ch_names[:4]:  # plot first 4 channels to avoid clutter
            tc = data["lzc_timecourse"][ch]
            ax.plot(tc, alpha=0.6, label=ch)
        ax.axhline(y=data["lzc"], color=colors[state], linestyle="--", linewidth=2,
                    label=f"Global mean: {data['lzc']:.3f}")
        ax.set_ylabel("LZc")
        ax.set_title(f"{state.capitalize()}", fontsize=12, fontweight="bold", color=colors[state])
        ax.legend(loc="upper right", fontsize=8, ncol=5)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    axes[-1].set_xlabel("Window (5-second epochs)")
    fig.suptitle("Lempel-Ziv Complexity Over Time", fontsize=14, fontweight="bold", y=1.01)
    plt.tight_layout()
    path = os.path.join(output_dir, "lzc_timecourse.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path}")


def plot_topographic_lzc(results, output_dir):
    """Channel-level LZc comparison (pseudo-topographic)."""
    states = list(results.keys())
    colors = {"awake": "#2ecc71", "sleep": "#3498db", "anesthesia": "#e74c3c"}

    ch_names = results[states[0]]["ch_names"]
    n_ch = len(ch_names)

    fig, ax = plt.subplots(figsize=(14, 6))
    x = np.arange(n_ch)
    width = 0.25

    for i, state in enumerate(states):
        values = [results[state]["lzc_per_ch"][ch] for ch in ch_names]
        ax.bar(x + i * width, values, width, label=state.capitalize(),
               color=colors[state], edgecolor="white", linewidth=1)

    ax.set_xticks(x + width)
    ax.set_xticklabels(ch_names, fontsize=9, rotation=45)
    ax.set_ylabel("Mean LZc", fontsize=12)
    ax.set_title("Lempel-Ziv Complexity per Channel", fontsize=14, fontweight="bold")
    ax.legend(fontsize=11)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    path = os.path.join(output_dir, "lzc_per_channel.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path}")


def main():
    output_dir = os.path.join(os.path.dirname(__file__), "figures")
    os.makedirs(output_dir, exist_ok=True)

    print("Generating consciousness measure visualizations...")
    print("  (Using synthetic EEG — 16 channels, 60 seconds per state)")
    print()

    results = collect_measures(n_channels=16)
    print()

    plot_bar_comparison(results, output_dir)
    plot_connectivity_bands(results, output_dir)
    plot_lzc_timecourse(results, output_dir)
    plot_topographic_lzc(results, output_dir)

    print("\nDone. All figures saved to experiments/eeg_analysis/figures/")
    print("\nKey findings from synthetic data:")
    for state, data in results.items():
        print(f"  {state:12s}: LZc={data['lzc']:.3f}  SE={data['se']:.3f}  PCI≈{data['pci']:.3f}")


if __name__ == "__main__":
    main()
