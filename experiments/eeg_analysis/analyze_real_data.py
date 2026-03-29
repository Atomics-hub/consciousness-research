"""
Analyze real EEG data from the PhysioNet Sleep-EDF database using
consciousness complexity measures.

Compares Wake vs N2 (light sleep) vs N3/N4 (deep sleep) vs REM states
across four measures: Lempel-Ziv complexity, spectral entropy,
PCI approximation, and connectivity (PLV/coherence).

Dataset: Sleep-EDF Expanded (Kemp et al., 2000)
  - https://physionet.org/content/sleep-edfx/1.0.0/
  - 2 EEG channels: Fpz-Cz, Pz-Oz (100 Hz)
  - Sleep stage annotations: W, N1, N2, N3, N4, REM
"""

import sys
from pathlib import Path
import numpy as np
from scipy import signal as sp_signal, stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mne

sys.path.insert(0, str(Path(__file__).parent))
from eeg_complexity import (
    lempel_ziv_complexity,
    _binarize,
    spectral_entropy,
)

DATA_DIR = Path(__file__).parent / "data"
FIG_DIR = Path(__file__).parent / "figures"
FIG_DIR.mkdir(exist_ok=True)

SUBJECTS = [
    {
        "psg": DATA_DIR / "SC4001E0-PSG.edf",
        "hyp": DATA_DIR / "SC4001EC-Hypnogram.edf",
        "id": "SC4001",
    },
    {
        "psg": DATA_DIR / "SC4011E0-PSG.edf",
        "hyp": DATA_DIR / "SC4011EH-Hypnogram.edf",
        "id": "SC4011",
    },
]

STATE_MAP = {
    "Sleep stage W": "Wake",
    "Sleep stage R": "REM",
    "Sleep stage 1": "N1",
    "Sleep stage 2": "N2",
    "Sleep stage 3": "N3",
    "Sleep stage 4": "N3",  # merge N3+N4 per AASM
}

STATES_OF_INTEREST = ["Wake", "N2", "N3", "REM"]
STATE_COLORS = {"Wake": "#e74c3c", "N1": "#e67e22", "N2": "#3498db", "N3": "#2c3e50", "REM": "#9b59b6"}

EPOCH_SEC = 30  # standard sleep epoch length
WINDOW_SEC = 5.0  # analysis window within each epoch


def load_subject(psg_path, hyp_path):
    raw = mne.io.read_raw_edf(str(psg_path), preload=True, verbose=False)
    annot = mne.read_annotations(str(hyp_path))
    raw.set_annotations(annot, verbose=False)

    eeg_picks = ["EEG Fpz-Cz", "EEG Pz-Oz"]
    raw.pick(eeg_picks, verbose=False)

    raw.filter(0.5, 45.0, fir_design="firwin", verbose=False)
    raw.set_eeg_reference("average", verbose=False)
    return raw


def extract_epochs_by_state(raw, epoch_sec=EPOCH_SEC, max_per_state=40):
    sfreq = raw.info["sfreq"]
    epoch_samples = int(epoch_sec * sfreq)
    annotations = raw.annotations
    data = raw.get_data()
    n_samples = data.shape[1]

    state_epochs = {s: [] for s in STATES_OF_INTEREST}
    state_counts = {s: 0 for s in STATES_OF_INTEREST}

    for ann in annotations:
        desc = ann["description"]
        if desc not in STATE_MAP:
            continue
        state = STATE_MAP[desc]
        if state not in STATES_OF_INTEREST:
            continue

        onset_sample = int(ann["onset"] * sfreq)
        duration_samples = int(ann["duration"] * sfreq)

        n_epochs_in_ann = duration_samples // epoch_samples
        for i in range(n_epochs_in_ann):
            if state_counts[state] >= max_per_state:
                break
            start = onset_sample + i * epoch_samples
            end = start + epoch_samples
            if end > n_samples:
                break
            epoch_data = data[:, start:end]
            state_epochs[state].append(epoch_data)
            state_counts[state] += 1

    for s in list(state_epochs.keys()):
        if len(state_epochs[s]) == 0:
            del state_epochs[s]

    return state_epochs, sfreq


def compute_epoch_measures(epoch_data, sfreq, window_sec=WINDOW_SEC):
    n_channels, n_samples = epoch_data.shape
    window_samples = int(window_sec * sfreq)
    n_windows = n_samples // window_samples

    lzc_vals = []
    se_vals = []
    for ch in range(n_channels):
        for w in range(n_windows):
            start = w * window_samples
            end = start + window_samples
            seg = epoch_data[ch, start:end]
            lzc_vals.append(lempel_ziv_complexity(_binarize(seg)))
            se_vals.append(spectral_entropy(seg, sfreq))

    # PCI approximation: spatiotemporal LZc
    pci_vals = []
    for w in range(n_windows):
        start = w * window_samples
        end = start + window_samples
        seg = epoch_data[:, start:end]
        binary_matrix = np.zeros_like(seg, dtype=int)
        for ch in range(n_channels):
            binary_matrix[ch] = _binarize(seg[ch])
        pci_vals.append(lempel_ziv_complexity(binary_matrix.flatten()))

    # Connectivity: coherence between the two channels
    # PLV saturates with only 2 channels; coherence is more informative
    bands = {"alpha": (8, 13), "beta": (13, 30)}
    coh_vals = {}
    for band_name, band_range in bands.items():
        freqs, cxy = sp_signal.coherence(
            epoch_data[0], epoch_data[1], fs=sfreq, nperseg=int(2 * sfreq)
        )
        band_mask = (freqs >= band_range[0]) & (freqs <= band_range[1])
        coh_vals[band_name] = float(np.mean(cxy[band_mask])) if band_mask.any() else 0.0

    return {
        "lzc": np.mean(lzc_vals),
        "se": np.mean(se_vals),
        "pci": np.mean(pci_vals),
        "coh_alpha": coh_vals["alpha"],
        "coh_beta": coh_vals["beta"],
    }


def run_analysis():
    all_state_measures = {s: {m: [] for m in ["lzc", "se", "pci", "coh_alpha", "coh_beta"]}
                          for s in STATES_OF_INTEREST}

    for subj in SUBJECTS:
        if not subj["psg"].exists():
            print(f"  Skipping {subj['id']}: files not found")
            continue
        print(f"  Loading {subj['id']}...")
        raw = load_subject(subj["psg"], subj["hyp"])
        epochs, sfreq = extract_epochs_by_state(raw)

        for state, epoch_list in epochs.items():
            print(f"    {state}: {len(epoch_list)} epochs")
            for epoch_data in epoch_list:
                measures = compute_epoch_measures(epoch_data, sfreq)
                for m, v in measures.items():
                    all_state_measures[state][m].append(v)

    # Remove states with no data
    all_state_measures = {s: v for s, v in all_state_measures.items() if len(v["lzc"]) > 0}
    return all_state_measures


def stat_tests(measures):
    print("\n" + "=" * 70)
    print("  STATISTICAL COMPARISONS (Mann-Whitney U)")
    print("=" * 70)

    states = sorted(measures.keys())
    measure_names = {"lzc": "Lempel-Ziv Complexity", "se": "Spectral Entropy",
                     "pci": "PCI Approximation", "coh_alpha": "Alpha Coherence",
                     "coh_beta": "Beta Coherence"}

    pairs = []
    for i in range(len(states)):
        for j in range(i + 1, len(states)):
            pairs.append((states[i], states[j]))

    results = {}
    for m_key, m_name in measure_names.items():
        print(f"\n  {m_name}:")
        results[m_key] = {}
        for s1, s2 in pairs:
            d1 = measures[s1][m_key]
            d2 = measures[s2][m_key]
            if len(d1) < 2 or len(d2) < 2:
                continue
            u_stat, p_val = stats.mannwhitneyu(d1, d2, alternative="two-sided")
            sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else "ns"
            print(f"    {s1} vs {s2}: U={u_stat:.0f}, p={p_val:.4f} {sig}"
                  f"  (median {np.median(d1):.4f} vs {np.median(d2):.4f})")
            results[m_key][(s1, s2)] = p_val
    return results


def plot_results(measures):
    states = [s for s in STATES_OF_INTEREST if s in measures]
    measure_keys = ["lzc", "se", "pci", "coh_alpha", "coh_beta"]
    measure_labels = ["Lempel-Ziv\nComplexity", "Spectral\nEntropy",
                      "PCI\nApproximation", "Alpha\nCoherence", "Beta\nCoherence"]

    # Box plots for each measure
    fig, axes = plt.subplots(1, 5, figsize=(18, 5))
    fig.suptitle("EEG Consciousness Measures Across Sleep Stages\n(PhysioNet Sleep-EDF)",
                 fontsize=14, fontweight="bold")

    for ax, m_key, m_label in zip(axes, measure_keys, measure_labels):
        data_list = [measures[s][m_key] for s in states]
        colors = [STATE_COLORS[s] for s in states]

        bp = ax.boxplot(data_list, tick_labels=states, patch_artist=True, widths=0.6)
        for patch, color in zip(bp["boxes"], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)

        ax.set_ylabel(m_label)
        ax.set_xlabel("Sleep Stage")
        ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    fig.savefig(FIG_DIR / "sleep_stage_comparison.png", dpi=150, bbox_inches="tight")
    print(f"\n  Saved: {FIG_DIR / 'sleep_stage_comparison.png'}")

    # Bar plot with error bars
    fig2, axes2 = plt.subplots(1, 5, figsize=(18, 5))
    fig2.suptitle("Mean EEG Measures by Consciousness State (with SEM)\n(PhysioNet Sleep-EDF)",
                  fontsize=14, fontweight="bold")

    for ax, m_key, m_label in zip(axes2, measure_keys, measure_labels):
        means = [np.mean(measures[s][m_key]) for s in states]
        sems = [stats.sem(measures[s][m_key]) if len(measures[s][m_key]) > 1 else 0 for s in states]
        colors = [STATE_COLORS[s] for s in states]
        bars = ax.bar(states, means, yerr=sems, capsize=4, color=colors, alpha=0.7, edgecolor="black")
        ax.set_ylabel(m_label)
        ax.set_xlabel("Sleep Stage")
        ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    fig2.savefig(FIG_DIR / "sleep_stage_bars.png", dpi=150, bbox_inches="tight")
    print(f"  Saved: {FIG_DIR / 'sleep_stage_bars.png'}")

    # Complexity trajectory (if we have enough Wake data to show transition)
    fig3, ax3 = plt.subplots(figsize=(10, 4))
    for state in states:
        vals = measures[state]["lzc"]
        ax3.plot(vals, "o-", label=state, color=STATE_COLORS[state], alpha=0.7, markersize=3)
    ax3.set_xlabel("Epoch index")
    ax3.set_ylabel("Lempel-Ziv Complexity")
    ax3.set_title("LZc Per Epoch by State")
    ax3.legend()
    ax3.grid(alpha=0.3)
    fig3.savefig(FIG_DIR / "lzc_trajectory.png", dpi=150, bbox_inches="tight")
    print(f"  Saved: {FIG_DIR / 'lzc_trajectory.png'}")

    plt.close("all")


def print_summary(measures):
    print("\n" + "=" * 70)
    print("  SUMMARY OF FINDINGS")
    print("=" * 70)

    states = [s for s in STATES_OF_INTEREST if s in measures]
    measure_names = {"lzc": "Lempel-Ziv Complexity", "se": "Spectral Entropy",
                     "pci": "PCI Approximation", "coh_alpha": "Alpha Coherence",
                     "coh_beta": "Beta Coherence"}

    print(f"\n  {'State':<8}", end="")
    for m_name in measure_names.values():
        print(f"  {m_name:>22}", end="")
    print()
    print("  " + "-" * 128)

    for state in states:
        print(f"  {state:<8}", end="")
        for m_key in measure_names:
            vals = measures[state][m_key]
            mean = np.mean(vals)
            std = np.std(vals)
            print(f"  {mean:>10.4f} +/- {std:<7.4f}", end="")
        print()

    print("\n  Expected pattern (from consciousness research literature):")
    print("    - LZc / SE / PCI: Wake > REM > N2 > N3 (complexity drops with depth of unconsciousness)")
    print("    - Coherence: needs 3+ channels for meaningful results (2-channel data saturates)")
    print("      (With only 2 channels + average re-reference, signals become mirror images)")
    print()

    # Check if our data matches expected ordering
    if "Wake" in measures and "N3" in measures:
        wake_lzc = np.mean(measures["Wake"]["lzc"])
        n3_lzc = np.mean(measures["N3"]["lzc"])
        if wake_lzc > n3_lzc:
            print("  RESULT: Wake LZc > N3 LZc -- CONSISTENT with consciousness theory")
        else:
            print("  RESULT: Wake LZc <= N3 LZc -- INCONSISTENT (check data quality)")

    if "Wake" in measures and "N3" in measures:
        wake_se = np.mean(measures["Wake"]["se"])
        n3_se = np.mean(measures["N3"]["se"])
        if wake_se > n3_se:
            print("  RESULT: Wake SE > N3 SE -- CONSISTENT with consciousness theory")
        else:
            print("  RESULT: Wake SE <= N3 SE -- INCONSISTENT (check data quality)")


def main():
    print("=" * 70)
    print("  SLEEP-EDF EEG CONSCIOUSNESS ANALYSIS")
    print("  Dataset: PhysioNet Sleep-EDF Expanded (Kemp et al., 2000)")
    print("  States: Wake, N2 (light sleep), N3 (deep sleep), REM")
    print("=" * 70)

    print("\n[1/4] Loading and preprocessing data...")
    measures = run_analysis()

    print("\n[2/4] Computing statistics...")
    stat_tests(measures)

    print("\n[3/4] Generating plots...")
    plot_results(measures)

    print("\n[4/4] Summary...")
    print_summary(measures)


if __name__ == "__main__":
    main()
