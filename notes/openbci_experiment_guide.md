# OpenBCI 16-Channel Consciousness Research: Experiment Guide

## Hardware Overview

**Board:** OpenBCI Cyton + Daisy (16 channels, 24-bit ADC, 125 Hz sample rate per channel)
**Headwear:** Ultracortex Mark IV or Electrode Cap (gel electrodes recommended for research-grade signal quality)
**Reference:** Earlobe (A1/A2 linked) or mastoid
**Ground:** AFz or Fpz

The Cyton handles channels 1-8, the Daisy handles channels 9-16. Use the y-splitter cable to gang the SRB (reference) pins together across both boards.

---

## Channel Montage Configurations

### Full 10-20 Coverage (16 channels)

Recommended default montage for consciousness research, maximizing spatial coverage:

```
Channels 1-8 (Cyton):   Fp1, Fp2, C3, C4, P3, P4, O1, O2
Channels 9-16 (Daisy):  F3, F4, F7, F8, T3, T4, P7, P8
Reference: Linked earlobes (A1+A2)
Ground: AFz
```

This gives you frontal, central, parietal, occipital, and temporal coverage -- enough for most consciousness-related measures.

### Consciousness-Optimized Montage (alternative)

If you want to emphasize midline sites (important for DMN correlates and meditation research):

```
Channels 1-8 (Cyton):   Fz, Cz, Pz, Oz, Fp1, Fp2, O1, O2
Channels 9-16 (Daisy):  F3, F4, C3, C4, P3, P4, T7, T8
Reference: Linked earlobes (A1+A2)
Ground: AFz
```

Midline electrodes (Fz, Cz, Pz, Oz) are critical for detecting frontal theta, posterior alpha, and midline connectivity changes associated with DMN activity and meditation states.

### Motor Imagery / BCI Montage

For motor imagery classification experiments:

```
Channels 1-8 (Cyton):   FC3, FC4, C3, Cz, C4, CP3, CP4, Pz
Channels 9-16 (Daisy):  F3, F4, P3, P4, O1, O2, T7, T8
Reference: Linked earlobes
Ground: AFz
```

Concentrates coverage around the motor cortex (C3/C4/Cz) for mu rhythm detection.

---

## Software Stack

### Core Acquisition

| Software | Purpose | Install |
|----------|---------|---------|
| **OpenBCI GUI** | Visual streaming, impedance check, basic recording | Download from [openbci.com](https://openbci.com/downloads) |
| **BrainFlow** | Programmatic data acquisition (Python/C++/Java/C#) | `pip install brainflow` |
| **Lab Streaming Layer (LSL)** | Time-synchronized multi-stream recording | `pip install pylsl` |

### Analysis

| Library | Purpose | Install |
|---------|---------|---------|
| **MNE-Python** | EEG preprocessing, filtering, epoching, source estimation | `pip install mne` |
| **AntroPy** | Entropy and complexity measures (Numba-accelerated) | `pip install antropy` |
| **NeuroKit2** | Higher-level complexity analysis, EEG feature extraction | `pip install neurokit2` |
| **SciPy** | Signal processing, spectral analysis | `pip install scipy` |
| **YASA** | Automated sleep staging from EEG | `pip install yasa` |
| **FOOOF / specparam** | Parameterize neural power spectra (aperiodic + peaks) | `pip install specparam` |

### Stimulus Presentation

| Software | Purpose | Install |
|---------|---------|---------|
| **PsychoPy** | Visual/auditory stimulus presentation with precise timing | `pip install psychopy` or standalone |
| **pygame** | Lightweight alternative for simple paradigms | `pip install pygame` |

### Full Install (one shot)

```bash
pip install brainflow pylsl mne antropy neurokit2 scipy yasa specparam psychopy matplotlib
```

### BrainFlow Quick Start

```python
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter

params = BrainFlowInputParams()
params.serial_port = '/dev/cu.usbserial-XXXXXXXX'  # find with ls /dev/cu.usb*

board = BoardShim(BoardIds.CYTON_DAISY_BOARD.value, params)
board.prepare_session()
board.start_stream()

# Record for N seconds
import time
time.sleep(60)

data = board.get_board_data()  # numpy array: rows = channels, cols = samples
board.stop_stream()
board.release_session()

eeg_channels = BoardShim.get_eeg_channels(BoardIds.CYTON_DAISY_BOARD.value)
eeg_data = data[eeg_channels, :]  # 16 x N_samples, units: microvolts

# Save raw
DataFilter.write_file(data, 'session_raw.csv', 'w')
```

### Streaming to LSL (for multi-tool integration)

Use [openbci-brainflow-lsl](https://github.com/marles77/openbci-brainflow-lsl) or write your own:

```python
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from pylsl import StreamInfo, StreamOutlet
import numpy as np

params = BrainFlowInputParams()
params.serial_port = '/dev/cu.usbserial-XXXXXXXX'
board = BoardShim(BoardIds.CYTON_DAISY_BOARD.value, params)

info = StreamInfo('OpenBCI', 'EEG', 16, 125, 'float32', 'openbci_cyton_daisy')
outlet = StreamOutlet(info)

board.prepare_session()
board.start_stream()

eeg_channels = BoardShim.get_eeg_channels(BoardIds.CYTON_DAISY_BOARD.value)

while True:
    data = board.get_board_data()
    if data.shape[1] > 0:
        for i in range(data.shape[1]):
            outlet.push_sample(data[eeg_channels, i].tolist())
```

---

## Experiment 1: Meditation vs. Resting State (Complexity Differences)

### Background

Meditation increases neural complexity (higher Lempel-Ziv complexity, sample entropy, Higuchi fractal dimension) compared to mind-wandering. Frontal theta increases and posterior alpha power changes are well-documented. Focused attention meditation shows the strongest effects.

### Protocol

```
1. Resting baseline, eyes closed      5 min
2. Resting baseline, eyes open        5 min
3. Meditation block 1                10 min
4. Rest break                         2 min
5. Mind-wandering block               5 min  (instructed: let thoughts wander)
6. Meditation block 2                10 min
7. Resting baseline, eyes closed      5 min
```

Mark condition transitions with event markers (key press or LSL marker stream).

### Montage

Use the consciousness-optimized montage (midline sites). Fz and FCz are critical for frontal theta; Pz and Oz for posterior alpha.

### Analysis

```python
import mne
import antropy as ant
import numpy as np
from scipy.signal import welch

# Load data (assuming you saved as CSV from BrainFlow)
# Preprocess with MNE: bandpass 1-45 Hz, notch 60 Hz
raw = mne.io.read_raw_brainvision('session.vhdr')  # or construct from array
raw.filter(1, 45)
raw.notch_filter(60)

data = raw.get_data()  # channels x samples
sfreq = raw.info['sfreq']

# Per-channel complexity measures
for ch_idx in range(data.shape[0]):
    signal = data[ch_idx]

    # Lempel-Ziv complexity (binarize around median)
    lzc = ant.lziv_complexity(signal, normalize=True)

    # Sample entropy
    se = ant.sample_entropy(signal)

    # Spectral entropy
    spe = ant.spectral_entropy(signal, sf=sfreq, method='welch', normalize=True)

    # Higuchi fractal dimension
    hfd = ant.higuchi_fd(signal)

    print(f"Ch {ch_idx}: LZc={lzc:.3f}, SampEn={se:.3f}, SpEn={spe:.3f}, HFD={hfd:.3f}")

# Power spectral density by band
def bandpower(signal, sf, band):
    freqs, psd = welch(signal, sf, nperseg=2*sf)
    idx = np.logical_and(freqs >= band[0], freqs <= band[1])
    return np.trapz(psd[idx], freqs[idx])

bands = {'delta': (1,4), 'theta': (4,8), 'alpha': (8,13), 'beta': (13,30), 'gamma': (30,45)}
for name, band in bands.items():
    power = bandpower(data[0], sfreq, band)
    print(f"{name}: {power:.4f}")
```

### Expected Results

- **Meditation vs rest:** Higher Lempel-Ziv complexity (0.05-0.15 increase, normalized), higher frontal theta power, potentially decreased or reorganized posterior alpha
- **Experienced meditators:** Larger effects. If you're new to meditation, effects may be subtle initially
- **Best discriminators:** Sample entropy and gamma-band power show highest accuracy (0.83-0.98 in published studies with experienced meditators)

---

## Experiment 2: Sleep Onset Detection (Consciousness Transitions)

### Background

The wake-to-sleep transition (hypnagogia, NREM N1) involves progressive alpha dropout, emergence of theta rhythms, vertex sharp waves, and slow eye movements. This is a consciousness state transition you can study on yourself. The Hori classification divides sleep onset into 9 substages.

### Protocol

```
1. Evening session, comfortable reclined position
2. Baseline awake, eyes closed             5 min
3. Allow natural sleep onset              30-60 min
4. Set gentle alarm or have someone wake you after N1/N2
5. Record subjective hypnagogic experiences immediately on waking
```

Use a voice recorder or phone to capture dream reports immediately upon waking.

### Montage

Standard 10-20 coverage. Include Fp1/Fp2 for eye movement detection (EOG proxy), O1/O2 for alpha, and C3/C4 for vertex waves and sleep spindles.

### Analysis

```python
import yasa
import mne
import numpy as np

raw = mne.io.read_raw_brainvision('sleep_session.vhdr')
raw.filter(0.5, 45)

# YASA automated sleep staging (needs central + occipital channels minimum)
sls = yasa.SleepStaging(raw, eeg_name='C4')  # or whichever channel label
hypno = sls.predict()  # array of stage labels per 30s epoch
confidence = sls.predict_proba()

# Plot hypnogram
yasa.plot_hypnogram(hypno)

# Detect sleep spindles (N2 marker)
sp = yasa.spindles_detect(raw.get_data(picks='C4')[0], sf=125)
if sp is not None:
    print(sp.summary())

# Track alpha power over time (alpha dropout = sleep onset)
from scipy.signal import spectrogram
f, t, Sxx = spectrogram(raw.get_data(picks='O1')[0], fs=125, nperseg=250, noverlap=125)
alpha_mask = (f >= 8) & (f <= 13)
alpha_power_over_time = Sxx[alpha_mask].mean(axis=0)
```

### Expected Results

- Clear alpha power drop at sleep onset (alpha dropout)
- Transition from alpha-dominant (8-13 Hz) to theta-dominant (4-8 Hz)
- N2 onset marked by sleep spindles (12-15 Hz bursts) and K-complexes
- Subjective hypnagogic imagery correlates with N1 stage
- 16 channels is enough for reliable automated sleep staging

### Practical Tips

- Gel electrodes are strongly recommended for sleep recording (dry electrodes shift with movement)
- Record at least 30 minutes to capture full N1-N2 transition
- The OpenBCI's 125 Hz sample rate is adequate for sleep staging (clinical PSG uses 256 Hz but 125 Hz captures all relevant features up to ~60 Hz)

---

## Experiment 3: Binocular Rivalry (Consciousness Switching)

### Background

Binocular rivalry occurs when each eye sees a different image -- perception alternates between the two rather than fusing them. This is a direct window into consciousness: the same physical stimulus is always present, but conscious experience switches. EEG signatures include changes in steady-state visual evoked potentials (SSVEPs) and shifts in posterior alpha/gamma.

### Setup

You need a way to present different images to each eye:

- **Red-blue anaglyph glasses** ($2-5) -- simplest approach. Show a red pattern to one eye, blue to the other
- **VR headset** -- more precise. Use a Quest or similar to present independent images to each eye
- **Mirror stereoscope** -- most precise for research, can be built from two mirrors and a divider

### Protocol

```
1. Baseline, fixation cross                    2 min
2. Binocular rivalry stimulus                 5 min
   - Present orthogonal gratings (e.g., vertical left eye, horizontal right eye)
   - Subject presses left/right key to report dominant percept
   - Record key presses as event markers
3. Rest                                        2 min
4. Repeat rivalry block                       5 min
5. Control: same grating to both eyes          2 min
```

### Stimulus Code (PsychoPy, anaglyph method)

```python
from psychopy import visual, core, event

win = visual.Window(fullscr=True, color='black')

# Red grating (left eye through red filter)
grating_left = visual.GratingStim(win, tex='sin', mask='gauss',
    size=8, sf=2, ori=0, color=[1, -1, -1])  # red only

# Blue grating (right eye through blue filter)
grating_right = visual.GratingStim(win, tex='sin', mask='gauss',
    size=8, sf=2, ori=90, color=[-1, -1, 1])  # blue only

fixation = visual.TextStim(win, text='+', height=0.5)

clock = core.Clock()
responses = []

while clock.getTime() < 300:  # 5 minutes
    grating_left.draw()
    grating_right.draw()
    fixation.draw()
    win.flip()

    keys = event.getKeys(keyList=['left', 'right', 'escape'], timeStamped=clock)
    for key, t in keys:
        if key == 'escape':
            core.quit()
        responses.append((key, t))
        # Send LSL marker here for EEG synchronization
```

### Analysis

- Epoch EEG data around perceptual switches (key presses)
- Compare 500ms before vs after reported switch
- Look for: posterior alpha desynchronization, gamma increase at switch, P300-like component

### Expected Results

- Perceptual switches every 2-5 seconds on average
- EEG shows alpha power changes in occipital/parietal regions preceding conscious switch by ~200-500ms
- With frequency-tagged stimuli (e.g., 7.5 Hz flicker left, 12 Hz right), you can track SSVEP amplitude to objectively measure which stimulus dominates consciousness

---

## Experiment 4: Flow State Detection

### Background

Flow states are characterized by increased frontal theta (Fz, FCz), moderate frontocentral alpha, and changes in the theta/beta ratio. The "transient hypofrontality hypothesis" predicts reduced prefrontal beta activity during flow.

### Protocol

```
1. Resting baseline, eyes open                3 min
2. Easy task (well below skill level)          5 min
3. Flow-inducing task (skill-matched)         15 min
4. Difficult task (above skill level)          5 min
5. Resting baseline                            3 min
6. Flow Short Scale questionnaire              2 min
```

Good flow-inducing tasks for solo use:
- **Tetris** (adjustable difficulty)
- **Mental arithmetic** (calibrated to your level -- not too easy, not too hard)
- **Coding** (working on an engaging problem)
- **Music performance** (if you play an instrument)

### Montage

Standard or consciousness-optimized. Frontal channels (Fz, F3, F4, Fp1, Fp2) are most important.

### Analysis

```python
import mne
import numpy as np
from scipy.signal import welch

# Compare 30-second windows across conditions
# Key metrics:
# 1. Frontal theta (4-8 Hz) at Fz -- should increase in flow
# 2. Frontocentral alpha (8-13 Hz) -- moderate levels in flow
# 3. Theta/beta ratio at frontal sites
# 4. Frontal alpha asymmetry (F4 alpha - F3 alpha) -- approach motivation

def theta_beta_ratio(signal, sf):
    freqs, psd = welch(signal, sf, nperseg=2*sf)
    theta = np.trapz(psd[(freqs >= 4) & (freqs <= 8)], freqs[(freqs >= 4) & (freqs <= 8)])
    beta = np.trapz(psd[(freqs >= 13) & (freqs <= 30)], freqs[(freqs >= 13) & (freqs <= 30)])
    return theta / beta if beta > 0 else 0
```

### Expected Results

- Frontal theta increases 20-40% during flow vs easy/hard tasks
- Alpha power is moderate (not suppressed as in difficult task, not dominant as in rest)
- Theta/beta ratio highest during flow
- Effects are clearest in participants who self-report high flow scores

---

## Experiment 5: Attention and Awareness Dissociation

### Background

Attention and awareness are dissociable. You can attend to something without being aware of it (subliminal priming) and be aware of something without attending to it (inattentional blindness paradigm). EEG markers differ: attention modulates early ERPs (N1, P1), while awareness correlates with later components (P3b, late positivity).

### Protocol: Attentional Blink

```
1. Rapid serial visual presentation (RSVP) at 10 Hz
2. Two targets embedded in stream of distractors
3. Subject reports both targets
4. When T2 appears 200-500ms after T1, it's often missed (attentional blink)
5. Compare EEG for seen vs unseen T2 (same stimulus, different awareness)
```

### Protocol: Inattentional Blindness (simpler)

```
1. Primary task: count specific events in a visual stream
2. Unexpected stimulus appears (e.g., colored flash in periphery)
3. After block: ask if subject noticed anything unusual
4. Compare EEG for noticed vs unnoticed unexpected stimuli
```

### Expected Results

- Seen targets: clear P300 component (positive peak at 300-500ms over Pz)
- Unseen targets: N1/P1 present (attention was deployed) but P300 absent (awareness was not)
- This dissociation is one of the strongest EEG markers of conscious access

---

## Experiment 6: Lempel-Ziv Complexity Across States (Spontaneous PCI Proxy)

### Background

The full Perturbational Complexity Index (PCI) requires TMS, which you don't have. But spontaneous Lempel-Ziv complexity (LZs) of resting EEG tracks consciousness level and can be computed from your 16-channel data. Higher LZs = more conscious/complex brain state. This has been validated against PCI and clinical consciousness assessments.

Key paper: Casali et al. (2013) introduced PCI. Subsequent work showed spontaneous complexity measures correlate with PCI and can distinguish consciousness states without TMS.

### Protocol

Record across multiple consciousness states:

```
State 1: Alert wakefulness, eyes open           5 min
State 2: Relaxed wakefulness, eyes closed        5 min
State 3: Drowsy (after sleep deprivation)        5 min
State 4: Meditation (any practiced technique)   10 min
State 5: Post-exercise (elevated arousal)        5 min
State 6: Sleep onset (if possible)             variable

Optional enhanced states:
- After caffeine (200mg, wait 30 min)
- During focused cognitive task
- During creative/divergent thinking task
```

### Analysis: Multi-Channel Lempel-Ziv Complexity

```python
import antropy as ant
import numpy as np
import mne

raw = mne.io.read_raw_brainvision('multi_state.vhdr')
raw.filter(1, 45)
raw.notch_filter(60)

data = raw.get_data()
sfreq = raw.info['sfreq']

def multichannel_lzc(data_segment):
    """Compute LZc per channel and average (spontaneous complexity proxy)."""
    lzc_values = []
    for ch in range(data_segment.shape[0]):
        lzc = ant.lziv_complexity(data_segment[ch], normalize=True)
        lzc_values.append(lzc)
    return np.mean(lzc_values), np.array(lzc_values)

# Compute LZc in sliding windows (e.g., 10-second windows)
window_samples = int(10 * sfreq)
step_samples = int(5 * sfreq)  # 50% overlap

lzc_timeseries = []
for start in range(0, data.shape[1] - window_samples, step_samples):
    segment = data[:, start:start + window_samples]
    mean_lzc, per_channel = multichannel_lzc(segment)
    lzc_timeseries.append(mean_lzc)

# Compare across conditions (segment by event markers)
# Expected ordering: sleep onset < drowsy < relaxed < alert < meditation/caffeine
```

### Expected Results

Based on published literature:

| State | Expected LZc (normalized) | Notes |
|-------|--------------------------|-------|
| Deep sleep (N3) | 0.3-0.5 | Lowest complexity |
| Drowsy / N1 | 0.5-0.6 | Transitional |
| Relaxed wakefulness | 0.6-0.7 | Baseline |
| Alert wakefulness | 0.65-0.75 | Slightly higher than relaxed |
| Meditation | 0.7-0.85 | Higher than baseline in experienced meditators |
| Psychedelics (literature) | 0.8-0.95 | Highest recorded in healthy subjects |

These are approximate ranges -- your absolute values will depend on preprocessing, electrode impedances, and individual variation. Focus on within-session relative differences.

---

## EEG Markers of Consciousness: What 16 Channels Can Measure

### Spectral Measures

| Measure | What it tracks | Channels needed | Your coverage |
|---------|---------------|-----------------|---------------|
| Alpha power (8-13 Hz) | Cortical idling, DMN correlate | O1, O2, Pz | Full |
| Frontal theta (4-8 Hz) | Cognitive control, meditation depth, flow | Fz, F3, F4 | Full |
| Gamma (30-45 Hz) | Binding, conscious perception | Widespread | Full |
| Alpha asymmetry | Approach/withdrawal motivation | F3 vs F4 | Full |
| Theta/alpha ratio | Drowsiness, consciousness level | Frontal/occipital | Full |

### Complexity Measures

| Measure | What it tracks | Min channels | Your coverage |
|---------|---------------|-------------|---------------|
| Lempel-Ziv complexity | Overall brain state complexity | 1 (better with more) | Full |
| Sample entropy | Signal regularity/predictability | 1 per channel | Full |
| Multiscale entropy | Complexity across timescales | 1 per channel | Full |
| Higuchi fractal dimension | Signal self-similarity | 1 per channel | Full |
| Spectral entropy | Spectral flatness | 1 per channel | Full |

### Connectivity Measures

| Measure | What it tracks | Min channels | Your coverage |
|---------|---------------|-------------|---------------|
| Phase-locking value (PLV) | Inter-regional synchronization | 2+ | Full |
| Coherence | Frequency-domain connectivity | 2+ | Full |
| Weighted symbolic mutual info | Information transfer | 2+ | Full |
| Granger causality | Directed connectivity | 2+ | Full (16 channels = 120 pairs) |

### ERP Components

| Component | What it tracks | Key channels | Your coverage |
|-----------|---------------|-------------|---------------|
| P300 (P3b) | Conscious access, stimulus evaluation | Pz, P3, P4 | Full |
| N400 | Semantic processing | Cz, Pz | Full |
| MMN (mismatch negativity) | Pre-attentive change detection | Fz, Cz | Full |
| VAN (visual awareness negativity) | Visual consciousness | Posterior | Full |

### Default Mode Network Proxy

You cannot directly image the DMN with EEG (it's defined by fMRI). But EEG correlates exist:
- Posterior alpha power (Pz, O1, O2) positively correlates with DMN activity in posterior cingulate cortex
- Frontal alpha has a more complex relationship (subpopulations show opposite correlations)
- Alpha-band connectivity between Pz and Fz tracks DMN integration
- Self-referential thought (mind-wandering) shows enhanced posterior alpha

---

## BCI Paradigms (16 Channels)

### Motor Imagery (MI)

- **What:** Imagine moving left hand vs right hand
- **Signal:** Mu rhythm (8-12 Hz) desynchronization contralateral to imagined movement at C3/C4
- **16 channels:** More than enough. Most MI-BCIs use 2-8 channels over motor cortex
- **Accuracy:** 70-90% binary classification with CSP + LDA after training
- **Software:** BrainFlow + MNE + scikit-learn, or use [MetaBCI](https://github.com/TBC-TJU/MetaBCI)

### P300 Speller

- **What:** Visual oddball paradigm. Rare target flashes elicit P300
- **Signal:** Positive peak at ~300ms over Pz after target stimulus
- **16 channels:** Excellent coverage. P300 is strongest at Pz but distributed
- **Accuracy:** 90-95% character accuracy with 16 channels
- **Use:** Can build a full keyboard interface

### SSVEP (Steady-State Visual Evoked Potentials)

- **What:** Flickering stimuli at different frequencies (e.g., 7, 10, 12, 15 Hz). Looking at one locks occipital EEG to that frequency
- **Signal:** Power peak at stimulus frequency and harmonics in O1/O2/Oz
- **16 channels:** O1/O2 is sufficient, extra channels help reject artifacts
- **Accuracy:** Highest of all BCI paradigms -- up to 99% with good electrode contact
- **Use:** Fastest BCI typing (40+ characters/min demonstrated)

### Connection to Consciousness Research

BCI paradigms are directly relevant to consciousness preservation:

1. **Decoding mental content from EEG** -- MI and SSVEP demonstrate that internal mental states map to measurable neural signatures. This is the foundation for any neural interface
2. **Neural signatures are person-specific** -- BCI models trained on one person don't transfer well to another. The patterns are individual
3. **16 channels is the practical floor** for reliable BCI. Below this, accuracy drops significantly for complex tasks
4. **Real-time processing pipeline** -- building a working BCI forces you to solve the same signal processing challenges needed for any consciousness monitoring system

---

## Key Papers

### Consciousness Theory and Measurement

1. **Casali et al. (2013)** "A theoretically based index of consciousness independent of sensory processing and behavior." *Science Translational Medicine*. -- Introduced PCI. Showed TMS-EEG complexity reliably discriminates consciousness levels.

2. **Schartner et al. (2015)** "Complexity of multi-dimensional spontaneous EEG decreases during propofol induced general anaesthesia." *PLoS ONE*. -- Validated spontaneous LZc as consciousness marker without TMS.

3. **Schartner et al. (2017)** "Increased spontaneous MEG signal diversity for psychoactive doses of ketamine, LSD and psilocybin." *Scientific Reports*. -- Showed psychedelics produce the highest-ever recorded signal diversity in healthy humans.

4. **Tononi et al. (2016)** "Integrated information theory: from consciousness to its physical substrate." *Nature Reviews Neuroscience*. -- The theoretical framework (IIT) underlying PCI.

### EEG Complexity and Meditation

5. **Kakumanu et al. (2018)** "Non-Linear EEG measures in meditation." *Frontiers in Human Neuroscience*. -- Review of complexity measures applied to meditation EEG.

6. **Vivot et al. (2020)** "Increased signal diversity/complexity of spontaneous EEG in ketamine-induced psychedelic state." *PLoS ONE*. -- Consumer-relevant demonstration of LZc tracking altered states.

7. **Determining states of consciousness in the EEG** (2022). *Neuroscience of Consciousness*. -- Used spectral, complexity, and criticality features to classify consciousness states from EEG.

### Sleep and Consciousness Transitions

8. **Lacaux et al. (2024)** "Embracing sleep-onset complexity." *Trends in Neurosciences*. -- Recent review of hypnagogia as a consciousness state transition, with EEG markers.

### BCI

9. **Lotte et al. (2018)** "A review of classification algorithms for EEG-based brain-computer interfaces." *Journal of Neural Engineering*. -- Comprehensive guide to BCI classification methods.

### Consumer EEG Validation

10. **Ratti et al. (2017)** "Comparison of medical and consumer wireless EEG systems for use in clinical trials." *Frontiers in Human Neuroscience*. -- Validates that consumer-grade EEG (including OpenBCI) produces research-usable data.

---

## Open-Source Projects and Resources

| Project | Description | Link |
|---------|-------------|------|
| **NeuroTechX/awesome-bci** | Curated BCI resource list | [GitHub](https://github.com/NeuroTechX/awesome-bci) |
| **OpenBCI GUI** | Official streaming/recording app | [GitHub](https://github.com/openbci) |
| **openbci-brainflow-lsl** | BrainFlow to LSL bridge | [GitHub](https://github.com/marles77/openbci-brainflow-lsl) |
| **OpenGalea** | Open-source MR+BCI (OpenBCI + Quest 3) | [GitHub](https://github.com/Caerii/OpenGalea) |
| **MetaBCI** | Open-source BCI platform (MI, P300, SSVEP) | [GitHub](https://github.com/TBC-TJU/MetaBCI) |
| **MNE-Python** | EEG/MEG analysis and visualization | [mne.tools](https://mne.tools) |
| **AntroPy** | Entropy and complexity for time-series | [GitHub](https://github.com/raphaelvallat/antropy) |
| **YASA** | Automated sleep staging | [GitHub](https://github.com/raphaelvallat/yasa) |
| **NeuroKit2** | Neurophysiological signal processing | [GitHub](https://github.com/neuropsychology/NeuroKit) |
| **EBRAINS PCI Tool** | Lempel-Ziv PCI computation | [EBRAINS](https://ebrains.eu/tools/lempel-ziv-perturbational-complexity-index) |
| **Perceptual Consciousness Project** | OpenBCI consciousness biofeedback | [OpenBCI Community](https://openbci.com/community/perceptual-consciousness-project-wearable-openbci-brain-state-biofeedback-systems/) |

---

## Practical Tips

### Signal Quality

- **Impedance:** Keep below 20 kOhm. Use Ten20 paste for gel electrodes. Check impedance in OpenBCI GUI before every session
- **Artifacts:** Blinks (Fp1/Fp2), jaw clenching (T7/T8), neck tension (posterior channels). Use ICA decomposition in MNE to remove
- **Environment:** Record in a quiet room. Turn off fluorescent lights (60 Hz noise). Keep phone and other electronics away
- **Grounding:** A proper ground electrode (AFz) dramatically reduces common-mode noise

### Session Hygiene

- Record at least 5 minutes of baseline before any experiment
- Don't move during recording. Use chin rest for seated experiments
- Caffeine and sleep deprivation affect all consciousness measures -- standardize or control for these
- Record at the same time of day for longitudinal comparisons
- Always save raw data. You can always re-analyze later with better methods

### Data Management

```
~/Documents/consciousness-research/
  data/
    raw/           # Raw BrainFlow CSV or EDF files
    processed/     # Filtered, epoched MNE files
    results/       # Analysis outputs, figures
  scripts/         # Analysis scripts
  notes/           # This file, session notes
  protocols/       # Experiment protocol documents
```

### Progressive Experiment Sequence

Recommended order for getting started:

1. **Week 1-2:** Set up hardware, check signal quality, run OpenBCI GUI, practice electrode placement. Record resting state baselines across multiple sessions.

2. **Week 3-4:** Experiment 1 (Meditation vs Rest). This is the simplest paradigm and will teach you the analysis pipeline.

3. **Week 5-6:** Experiment 6 (Multi-state complexity). Record across as many states as possible. Build your personal complexity baseline.

4. **Week 7-8:** Experiment 4 (Flow state). Requires a good task paradigm -- spend time finding what induces flow for you.

5. **Week 9-12:** Experiment 2 (Sleep onset) or Experiment 3 (Binocular rivalry). These are more complex setups.

6. **Ongoing:** Experiment 5 (Attention/awareness dissociation). Requires PsychoPy stimulus programming.

### What 16 Channels Cannot Do

Be realistic about limitations:

- **Source localization:** 16 channels gives very coarse spatial resolution. You can distinguish frontal from posterior activity, but not specific cortical areas. 64+ channels needed for reliable source estimation
- **Deep brain structures:** EEG cannot directly measure hippocampal, thalamic, or brainstem activity. You see cortical surface signals only
- **Single-trial classification:** Most consciousness measures need averaging across seconds to minutes. Real-time single-trial classification is possible for BCI but noisy for consciousness measures
- **Full PCI:** Requires TMS perturbation, which you don't have. Spontaneous LZc is a useful proxy but not identical
- **Sub-millimeter neural patterns:** EEG measures population-level activity of millions of neurons. Individual neuron or small-circuit dynamics are invisible
