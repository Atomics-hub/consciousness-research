"""
EEG complexity measures relevant to consciousness research.

Computes four classes of measures that correlate with conscious states:

1. LEMPEL-ZIV COMPLEXITY (LZc)
   How compressible is the brain signal? Higher LZc = more complex = more
   likely conscious. Drops dramatically under anesthesia, in vegetative states,
   and during deep sleep. Used by Casali et al. (2013) and Schartner et al. (2015).

2. PERTURBATIONAL COMPLEXITY INDEX (PCI) APPROXIMATION
   The gold standard for consciousness measurement uses TMS-EEG: you zap the
   brain and measure how far the perturbation spreads. Here we approximate this
   from resting EEG using spontaneous signal complexity — not a true PCI, but
   correlates with it. Real PCI requires TMS+EEG hardware.

3. SPECTRAL ENTROPY
   Shannon entropy of the power spectrum. A flat spectrum (white noise) has
   maximum entropy; a single dominant frequency (like alpha during eyes-closed
   rest) has low entropy. Conscious states show intermediate entropy —
   structured but not periodic.

4. CONNECTIVITY MEASURES
   Phase Locking Value (PLV) and coherence between channels. Consciousness
   requires large-scale integration across brain regions. Loss of consciousness
   (anesthesia, coma) shows breakdown of frontoparietal connectivity.

Data format: supports OpenBCI CSV and standard BDF/EDF files.
"""

import numpy as np
from scipy import signal, stats
from pathlib import Path
import warnings

import mne


# -- Data Loading --

def load_openbci_csv(filepath, sfreq=250.0, ch_names=None):
    """Load OpenBCI data from CSV format.

    OpenBCI default CSV has columns: sample_index, ch1..ch8, accel_x/y/z, timestamp.
    Data is in microvolts. Standard 8-channel setup uses Fp1, Fp2, C3, C4, P7, P8, O1, O2.
    """
    filepath = Path(filepath)
    data = np.loadtxt(filepath, delimiter=",", skiprows=5, usecols=range(1, 9))
    # OpenBCI outputs in microvolts, MNE expects volts
    data = data * 1e-6

    if ch_names is None:
        ch_names = ["Fp1", "Fp2", "C3", "C4", "P7", "P8", "O1", "O2"]

    info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types="eeg")
    raw = mne.io.RawArray(data.T, info)
    raw.set_montage("standard_1020", on_missing="ignore")
    return raw


def load_eeg_file(filepath, **kwargs):
    """Load EEG data from BDF, EDF, or OpenBCI CSV.

    Returns an MNE Raw object. Handles format detection automatically.
    """
    filepath = Path(filepath)
    suffix = filepath.suffix.lower()

    if suffix == ".bdf":
        return mne.io.read_raw_bdf(filepath, preload=True, **kwargs)
    elif suffix == ".edf":
        return mne.io.read_raw_edf(filepath, preload=True, **kwargs)
    elif suffix == ".csv":
        return load_openbci_csv(filepath, **kwargs)
    elif suffix in (".fif", ".fif.gz"):
        return mne.io.read_raw_fif(filepath, preload=True, **kwargs)
    else:
        raise ValueError(f"Unsupported format: {suffix}. Use .bdf, .edf, .csv, or .fif")


# -- Preprocessing --

def preprocess(raw, l_freq=1.0, h_freq=45.0, notch_freq=60.0):
    """Standard EEG preprocessing pipeline.

    - Bandpass filter 1-45 Hz (removes DC drift and muscle artifacts)
    - Notch filter at line frequency (60 Hz US / 50 Hz EU)
    - Re-reference to average

    Returns a copy; does not modify the input.
    """
    raw = raw.copy()
    raw.filter(l_freq, h_freq, fir_design="firwin", verbose=False)
    if notch_freq:
        raw.notch_filter(notch_freq, verbose=False)
    raw.set_eeg_reference("average", verbose=False)
    return raw


# -- Lempel-Ziv Complexity --

def _binarize(signal_1d, threshold="median"):
    """Convert continuous signal to binary sequence for LZ analysis."""
    if threshold == "median":
        thresh = np.median(signal_1d)
    elif threshold == "mean":
        thresh = np.mean(signal_1d)
    else:
        thresh = threshold
    return (signal_1d > thresh).astype(int)


def lempel_ziv_complexity(binary_seq):
    """Compute Lempel-Ziv complexity of a binary sequence.

    Counts the number of distinct "words" found when parsing the sequence
    left to right. Normalized by the theoretical maximum for a random binary
    sequence of the same length: n / log2(n).

    Returns a value in [0, 1] where:
      ~0.0 = perfectly regular (e.g., 010101...)
      ~1.0 = maximally complex (random)
      0.3-0.5 = typical for waking EEG
      0.1-0.2 = typical for deep anesthesia
    """
    n = len(binary_seq)
    if n == 0:
        return 0.0

    s = binary_seq.tolist()
    i = 0
    complexity = 1
    prefix_len = 1
    component_len = 1

    while prefix_len + component_len <= n:
        # Check if current component is in the prefix
        if s[i + component_len - 1] == s[prefix_len + component_len - 1]:
            component_len += 1
        else:
            # New word found — max of prefix extension
            complexity += 1
            i += 1
            if i == prefix_len:
                prefix_len += component_len
                component_len = 1
                i = 0
            else:
                component_len = 1

    if component_len > 1:
        complexity += 1

    # Normalize by theoretical maximum for random binary sequence
    max_complexity = n / np.log2(n) if n > 1 else 1
    return complexity / max_complexity


def compute_lzc(raw, window_sec=5.0):
    """Compute Lempel-Ziv complexity for each channel over sliding windows.

    Returns dict with per-channel LZc values (mean and timecourse).
    """
    data = raw.get_data()
    sfreq = raw.info["sfreq"]
    ch_names = raw.ch_names
    window_samples = int(window_sec * sfreq)
    n_channels, n_samples = data.shape
    n_windows = n_samples // window_samples

    results = {}
    for ch_idx, ch_name in enumerate(ch_names):
        lzc_values = []
        for w in range(n_windows):
            start = w * window_samples
            end = start + window_samples
            segment = data[ch_idx, start:end]
            binary = _binarize(segment)
            lzc = lempel_ziv_complexity(binary)
            lzc_values.append(lzc)

        results[ch_name] = {
            "mean_lzc": float(np.mean(lzc_values)),
            "std_lzc": float(np.std(lzc_values)),
            "timecourse": lzc_values,
        }

    global_mean = np.mean([r["mean_lzc"] for r in results.values()])
    results["global_mean_lzc"] = float(global_mean)
    return results


# -- Spectral Entropy --

def spectral_entropy(signal_1d, sfreq, nperseg=None):
    """Compute spectral entropy of a signal.

    Shannon entropy of the normalized power spectral density.

    Returns value in [0, 1]:
      0 = single frequency (pure sine wave)
      1 = flat spectrum (white noise)
      ~0.6-0.8 = typical waking EEG
      Lower values during anesthesia (dominant slow oscillations)
    """
    if nperseg is None:
        nperseg = min(len(signal_1d), int(2 * sfreq))

    freqs, psd = signal.welch(signal_1d, fs=sfreq, nperseg=nperseg)

    # Restrict to 1-45 Hz (EEG-relevant range)
    mask = (freqs >= 1) & (freqs <= 45)
    psd = psd[mask]

    # Normalize to probability distribution
    psd_norm = psd / psd.sum()
    psd_norm = psd_norm[psd_norm > 0]  # avoid log(0)

    # Shannon entropy, normalized by max possible entropy
    entropy = -np.sum(psd_norm * np.log2(psd_norm))
    max_entropy = np.log2(len(psd_norm))
    return entropy / max_entropy if max_entropy > 0 else 0.0


def compute_spectral_entropy(raw, window_sec=5.0):
    """Compute spectral entropy for each channel over sliding windows."""
    data = raw.get_data()
    sfreq = raw.info["sfreq"]
    ch_names = raw.ch_names
    window_samples = int(window_sec * sfreq)
    n_channels, n_samples = data.shape
    n_windows = n_samples // window_samples

    results = {}
    for ch_idx, ch_name in enumerate(ch_names):
        se_values = []
        for w in range(n_windows):
            start = w * window_samples
            end = start + window_samples
            segment = data[ch_idx, start:end]
            se = spectral_entropy(segment, sfreq)
            se_values.append(se)

        results[ch_name] = {
            "mean_se": float(np.mean(se_values)),
            "std_se": float(np.std(se_values)),
            "timecourse": se_values,
        }

    global_mean = np.mean([r["mean_se"] for r in results.values()])
    results["global_mean_se"] = float(global_mean)
    return results


# -- PCI Approximation from Resting EEG --

def approximate_pci(raw, window_sec=5.0):
    """Approximate Perturbational Complexity Index from resting-state EEG.

    Real PCI (Casali et al., 2013) requires TMS-EEG: you deliver a TMS pulse
    and measure the spatiotemporal complexity of the evoked response. Values:
      PCI > 0.31 = conscious (awake, dreaming, locked-in)
      PCI < 0.31 = unconscious (anesthesia, vegetative state, NREM sleep)

    This approximation uses spontaneous EEG complexity as a proxy:
    1. Binarize the multichannel signal (above/below median)
    2. Concatenate channels into a spatiotemporal binary matrix
    3. Compute Lempel-Ziv complexity of the flattened matrix
    4. Normalize by data dimensions

    This is NOT equivalent to real PCI but correlates with it because
    both measure the brain's capacity for complex, integrated responses.
    """
    data = raw.get_data()
    sfreq = raw.info["sfreq"]
    window_samples = int(window_sec * sfreq)
    n_channels, n_samples = data.shape
    n_windows = n_samples // window_samples

    pci_values = []
    for w in range(n_windows):
        start = w * window_samples
        end = start + window_samples
        segment = data[:, start:end]

        # Binarize each channel independently (above/below median)
        binary_matrix = np.zeros_like(segment, dtype=int)
        for ch in range(n_channels):
            binary_matrix[ch] = _binarize(segment[ch])

        # Flatten spatiotemporal matrix and compute LZ complexity
        # Row-major order: time flows within each channel, then next channel
        flat = binary_matrix.flatten()
        lzc = lempel_ziv_complexity(flat)
        pci_values.append(lzc)

    return {
        "mean_pci_approx": float(np.mean(pci_values)),
        "std_pci_approx": float(np.std(pci_values)),
        "timecourse": pci_values,
        "note": "Approximation from resting EEG. Real PCI requires TMS-EEG.",
    }


# -- Connectivity Measures --

def phase_locking_value(sig1, sig2, sfreq, band=(8, 13)):
    """Compute Phase Locking Value (PLV) between two signals in a frequency band.

    PLV measures the consistency of phase difference between two signals.
    Range [0, 1]:
      1 = perfectly phase-locked (strong functional connection)
      0 = random phase relationship (no connection)

    High PLV in frontoparietal alpha/beta bands is a signature of
    conscious processing. PLV drops under anesthesia and in disorders
    of consciousness.
    """
    # Bandpass filter to target frequency band
    sos = signal.butter(4, band, btype="bandpass", fs=sfreq, output="sos")
    filtered1 = signal.sosfilt(sos, sig1)
    filtered2 = signal.sosfilt(sos, sig2)

    # Extract instantaneous phase via Hilbert transform
    phase1 = np.angle(signal.hilbert(filtered1))
    phase2 = np.angle(signal.hilbert(filtered2))

    # PLV = magnitude of mean phase difference vector
    phase_diff = phase1 - phase2
    plv = np.abs(np.mean(np.exp(1j * phase_diff)))
    return plv


def compute_connectivity(raw, bands=None):
    """Compute PLV and coherence between all channel pairs.

    Analyzes connectivity in standard EEG frequency bands:
      - Delta (1-4 Hz): sleep, unconsciousness
      - Theta (4-8 Hz): memory, drowsiness
      - Alpha (8-13 Hz): relaxed wakefulness, eyes closed
      - Beta (13-30 Hz): active thinking, consciousness marker
      - Gamma (30-45 Hz): binding, higher cognition

    Returns connectivity matrices (channel x channel) for each band.
    """
    if bands is None:
        bands = {
            "delta": (1, 4),
            "theta": (4, 8),
            "alpha": (8, 13),
            "beta": (13, 30),
            "gamma": (30, 45),
        }

    data = raw.get_data()
    sfreq = raw.info["sfreq"]
    ch_names = raw.ch_names
    n_channels = len(ch_names)

    results = {}
    for band_name, band_range in bands.items():
        plv_matrix = np.zeros((n_channels, n_channels))
        coh_matrix = np.zeros((n_channels, n_channels))

        for i in range(n_channels):
            for j in range(i + 1, n_channels):
                # PLV
                plv = phase_locking_value(data[i], data[j], sfreq, band_range)
                plv_matrix[i, j] = plv
                plv_matrix[j, i] = plv

                # Coherence (magnitude-squared coherence, averaged over band)
                freqs, cxy = signal.coherence(
                    data[i], data[j], fs=sfreq, nperseg=int(2 * sfreq)
                )
                band_mask = (freqs >= band_range[0]) & (freqs <= band_range[1])
                if band_mask.any():
                    coh_matrix[i, j] = np.mean(cxy[band_mask])
                    coh_matrix[j, i] = coh_matrix[i, j]

        # Diagonal = 1 (self-connection)
        np.fill_diagonal(plv_matrix, 1.0)
        np.fill_diagonal(coh_matrix, 1.0)

        results[band_name] = {
            "plv_matrix": plv_matrix,
            "coherence_matrix": coh_matrix,
            "mean_plv": float(plv_matrix[np.triu_indices(n_channels, k=1)].mean()),
            "mean_coherence": float(
                coh_matrix[np.triu_indices(n_channels, k=1)].mean()
            ),
        }

    return results


# -- Summary & Visualization --

def consciousness_summary(raw, window_sec=5.0):
    """Compute all consciousness-relevant measures and print a summary."""
    print("=" * 60)
    print("  EEG Consciousness Complexity Analysis")
    print("=" * 60)
    print(f"  Channels: {raw.ch_names}")
    print(f"  Duration: {raw.times[-1]:.1f} seconds")
    print(f"  Sampling rate: {raw.info['sfreq']} Hz")
    print()

    # LZc
    print("  1. Lempel-Ziv Complexity (LZc)")
    print("     Higher = more complex = more likely conscious")
    print("     Typical: awake ~0.3-0.5, anesthesia ~0.1-0.2")
    lzc = compute_lzc(raw, window_sec)
    print(f"     Global mean LZc: {lzc['global_mean_lzc']:.4f}")
    for ch in raw.ch_names:
        print(f"       {ch}: {lzc[ch]['mean_lzc']:.4f} +/- {lzc[ch]['std_lzc']:.4f}")
    print()

    # Spectral entropy
    print("  2. Spectral Entropy")
    print("     Diversity of frequency content. Higher = richer dynamics.")
    print("     Drops under anesthesia (dominated by slow oscillations)")
    se = compute_spectral_entropy(raw, window_sec)
    print(f"     Global mean SE: {se['global_mean_se']:.4f}")
    for ch in raw.ch_names:
        print(f"       {ch}: {se[ch]['mean_se']:.4f} +/- {se[ch]['std_se']:.4f}")
    print()

    # PCI approximation
    print("  3. PCI Approximation (from resting EEG)")
    print("     Real PCI threshold: >0.31 = conscious, <0.31 = unconscious")
    print("     This is an approximation — real PCI requires TMS-EEG hardware")
    pci = approximate_pci(raw, window_sec)
    print(f"     Approx PCI: {pci['mean_pci_approx']:.4f} +/- {pci['std_pci_approx']:.4f}")
    print()

    # Connectivity
    print("  4. Connectivity (PLV and Coherence)")
    print("     Consciousness requires large-scale integration.")
    print("     Loss of consciousness -> frontoparietal connectivity drops.")
    conn = compute_connectivity(raw)
    for band_name, band_data in conn.items():
        print(
            f"     {band_name:6s}: mean PLV = {band_data['mean_plv']:.4f}, "
            f"mean coherence = {band_data['mean_coherence']:.4f}"
        )
    print()

    return {"lzc": lzc, "spectral_entropy": se, "pci_approx": pci, "connectivity": conn}


def generate_synthetic_eeg(duration_sec=30, sfreq=250, n_channels=8, state="awake"):
    """Generate synthetic EEG for testing when no real data is available.

    Simulates different consciousness states:
      - "awake": mixed frequencies, high complexity
      - "anesthesia": dominated by delta/slow oscillations, low complexity
      - "sleep": alpha dropout, theta/delta increase
    """
    ch_names = ["Fp1", "Fp2", "C3", "C4", "P7", "P8", "O1", "O2"][:n_channels]
    n_samples = int(duration_sec * sfreq)
    t = np.arange(n_samples) / sfreq
    rng = np.random.default_rng(42)

    data = np.zeros((n_channels, n_samples))

    if state == "awake":
        # Mix of all frequency bands with moderate noise
        for ch in range(n_channels):
            phase_offsets = rng.uniform(0, 2 * np.pi, 5)
            data[ch] = (
                0.5 * np.sin(2 * np.pi * 2 * t + phase_offsets[0])     # delta
                + 0.8 * np.sin(2 * np.pi * 6 * t + phase_offsets[1])   # theta
                + 2.0 * np.sin(2 * np.pi * 10 * t + phase_offsets[2])  # alpha
                + 1.5 * np.sin(2 * np.pi * 20 * t + phase_offsets[3])  # beta
                + 0.3 * np.sin(2 * np.pi * 40 * t + phase_offsets[4])  # gamma
                + 1.5 * rng.normal(0, 1, n_samples)                     # noise
            ) * 1e-5  # scale to ~10 uV

    elif state == "anesthesia":
        # Dominated by slow oscillations, little high-frequency content
        for ch in range(n_channels):
            phase_offsets = rng.uniform(0, 2 * np.pi, 2)
            data[ch] = (
                5.0 * np.sin(2 * np.pi * 1.5 * t + phase_offsets[0])  # strong delta
                + 2.0 * np.sin(2 * np.pi * 3 * t + phase_offsets[1])  # slow
                + 0.5 * rng.normal(0, 1, n_samples)                    # less noise
            ) * 1e-5

    elif state == "sleep":
        # Theta/delta dominant, reduced alpha/beta
        for ch in range(n_channels):
            phase_offsets = rng.uniform(0, 2 * np.pi, 3)
            data[ch] = (
                3.0 * np.sin(2 * np.pi * 2 * t + phase_offsets[0])    # delta
                + 2.0 * np.sin(2 * np.pi * 5 * t + phase_offsets[1])  # theta
                + 0.3 * np.sin(2 * np.pi * 12 * t + phase_offsets[2]) # weak alpha
                + 1.0 * rng.normal(0, 1, n_samples)
            ) * 1e-5

    info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types="eeg")
    raw = mne.io.RawArray(data, info, verbose=False)
    return raw


# -- Main --

def main():
    import sys

    if len(sys.argv) > 1:
        # Load real EEG data
        filepath = sys.argv[1]
        print(f"Loading EEG data from {filepath}")
        raw = load_eeg_file(filepath)
        raw = preprocess(raw)
        consciousness_summary(raw)
    else:
        # Demo with synthetic data
        print("No EEG file provided — running demo with synthetic data.")
        print("Usage: python eeg_complexity.py <path_to_eeg_file>")
        print("Supported formats: .bdf, .edf, .csv (OpenBCI), .fif")
        print()

        for state in ["awake", "anesthesia", "sleep"]:
            print(f"\n{'#'*60}")
            print(f"  Simulated state: {state.upper()}")
            print(f"{'#'*60}")
            raw = generate_synthetic_eeg(duration_sec=30, state=state)
            raw = preprocess(raw)
            consciousness_summary(raw)


if __name__ == "__main__":
    main()
