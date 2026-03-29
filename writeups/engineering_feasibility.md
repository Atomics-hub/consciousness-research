# Consciousness Preservation: Engineering Feasibility Analysis

**Date:** 2026-03-27
**Status:** Working document

---

## 1. Compute Requirements for Brain Simulation

### 1.1 Fidelity Levels and Their Costs

The compute requirements for brain simulation span roughly 10 orders of magnitude depending on the fidelity level chosen. The fundamental question — "how detailed does the simulation need to be?" — remains unanswered, but we can bound the engineering requirements at each level.

#### Level 1: Point-Neuron / Spiking Network Models (LIF/Izhikevich)

- **Cost per neuron per timestep:** ~5-20 FLOPS (leaky integrate-and-fire: 4-5 FLOPS)
- **Timestep:** 0.1-1 ms
- **Parameters per neuron:** ~10-20
- **Memory per neuron:** ~100 bytes
- **86B neurons at 10 kHz update rate:**
  - Compute: ~10^13-10^14 FLOPS (10-100 TFLOPS)
  - Memory: ~10 TB (neurons) + synaptic state
  - Synaptic lookups dominate: 100T synapses x ~8 bytes each = ~800 TB just for weight storage

This is the level at which Fudan University's Digital Twin Brain operated in 2024. Their 14,012-GPU cluster simulated 86B neurons with 47.8T synapses at 1/65th to 1/119th real-time speed (depending on firing rate). This used simplified point-neuron models, not biophysically detailed ones.

**Verdict:** Technically achievable today at sub-real-time on exascale hardware. Real-time plausible by ~2028-2030. But almost certainly insufficient for consciousness — it captures network topology and spike timing but discards the biophysics that likely matters.

#### Level 2: Hodgkin-Huxley Single-Compartment Models

- **Cost per neuron per timestep:** ~1,200 FLOPS (Sandberg & Bostrom 2008, via Izhikevich 2004)
- **Timestep:** 25 μs (0.025 ms) — must be shorter for HH stability
- **Parameters per neuron:** ~100-1,000
- **Memory per neuron:** ~1-10 KB
- **86B neurons at 40 kHz update rate:**
  - Compute: 86×10^9 × 1,200 × 40,000 = ~4×10^18 FLOPS = **4 ExaFLOPS**
  - Memory: ~86 TB (neuron state) + ~800 TB (synaptic weights) = **~1 PB**

This matches the commonly cited estimate of 1-10 ExaFLOPS for whole-brain HH simulation. Current exascale machines (El Capitan: 1.8 ExaFLOPS HPL, 2.88 peak) are within striking distance for single-compartment HH, but HPL performance is generous — real neurosim workloads are memory-bound, not compute-bound.

**Verdict:** Hardware exists in principle. Memory bandwidth is the actual bottleneck (see Section 1.3). Real-time simulation likely requires purpose-built hardware or 10x current exascale. Plausible ~2030-2035.

#### Level 3: Multi-Compartment Models (1,000+ compartments/neuron)

The Blue Brain Project used this approach for neocortical columns: morphologically detailed neurons with separate dendritic, somatic, and axonal compartments, each running HH-type equations.

- **Compartments per neuron:** 200-2,000 (Blue Brain used ~200-1,000 per cell type)
- **Cost per compartment per timestep:** ~1,200 FLOPS
- **Timestep:** 25 μs
- **86B neurons × 1,000 compartments:**
  - Compute: 86×10^9 × 10^3 × 1,200 × 40,000 = ~4×10^21 FLOPS = **4 ZettaFLOPS**
  - Memory: ~86 PB (compartment state) + synaptic weights
  - This is ~1,000× the single-compartment case

Blue Brain's actual achievement: simulated ~31,000 neurons with ~37M synapses using multi-compartmental models on Blue Gene supercomputers. CoreNEURON optimized this to 4-7x less memory and 2-7x less execution time vs the original NEURON simulator.

Scaling from 31K to 86B neurons: a factor of ~2.8 million. Blue Brain used ~22.8 TFLOPS. Naive scaling: ~64 ExaFLOPS. But the relationship isn't purely linear due to communication overhead scaling superlinearly.

**Verdict:** 3-4 orders of magnitude beyond current hardware. Not feasible until ~2040+ even with aggressive Moore's Law assumptions (which are slowing). May require neuromorphic or purpose-built architectures.

#### Level 4: Molecular-Level Simulation

This means simulating individual ion channels, receptor proteins, second-messenger cascades, and gene expression.

- **Atoms per ion channel:** ~100,000-200,000 (fully solvated)
- **Ion channels per neuron:** ~1,000-10,000
- **MD timestep:** ~1-2 femtoseconds
- **Operations per atom per timestep:** ~10,000
- **Single ion channel, 1 μs simulated:** ~10^18 operations

To simulate all ion channels on a single neuron for 1 second of biological time:
- ~5,000 channels × 10^18 ops/channel/μs × 10^6 μs = ~5×10^27 FLOPS per neuron
- 86B neurons: ~4×10^38 FLOPS

This is roughly 10^20 times current exascale. Completely infeasible and likely always will be at full molecular fidelity. The only path is coarse-graining: replacing molecular dynamics with fitted kinetic rate equations (which is what HH models already do for ion channels).

**Verdict:** Full molecular simulation of a brain is a non-starter. The question is: can you get away with HH-level abstractions of molecular dynamics? For ion channels, probably yes — that's literally what Hodgkin and Huxley showed in 1952. For protein signaling cascades that affect synaptic plasticity and memory consolidation — much less clear.

### 1.2 What Projects Have Actually Achieved

| Project | Year | Neurons | Synapses | Model Type | Hardware | Real-Time Factor |
|---------|------|---------|----------|------------|----------|-----------------|
| Blue Brain | 2005-2024 | 31,000 | 37M | Multi-compartment HH | Blue Gene, 22.8 TFLOPS | Sub-real-time |
| OpenWorm | Ongoing | 302 | ~8,000 | Multi-compartment HH | Commodity | ~Real-time |
| Fudan Digital Twin Brain | 2024 | 86B | 47.8T | Point-neuron (LIF-like) | 14,012 GPUs | 1/65 to 1/119 |
| FlyWire/Eon Systems | 2024 | 139,255 | 50M | Connectome-derived spiking | Laptop / 12 Loihi 2 chips | Real-time+ |
| NEST (Fugaku) | 2023 | 520M | 5.8T | Point-neuron | Fugaku, 442 PFLOPS | 1/5.2 (improved) |

Key observation: the fly brain (139K neurons, 50M synapses) ran on a laptop with spiking models derived from the full connectome, and predicted real neural responses accurately. But the fly brain is ~600,000x smaller than the human brain by neuron count and ~2,000,000x smaller by synapse count.

### 1.3 Memory Bandwidth: Why FLOPS Alone Is Misleading

Neural simulation is fundamentally memory-bound, not compute-bound. Each timestep requires:
1. Read synaptic weights for all active connections
2. Update neuron state variables
3. Deliver spikes to postsynaptic targets (random memory access pattern)

The spike delivery step is the killer. Synaptic events arrive at essentially random memory locations — this is a scatter/gather pattern that defeats cache hierarchies. With 100T synapses and average firing rates of ~1-10 Hz:

- Synaptic events per second: ~10^14 to 10^15
- Each requiring ~8-64 bytes of memory access
- Required bandwidth: ~1-64 PB/s

Current hardware bandwidth:
- Single H100: 3.35 TB/s HBM bandwidth
- Single B200: 8 TB/s HBM bandwidth
- El Capitan (full system): ~hundreds of PB/s aggregate, but inter-node bandwidth is orders of magnitude lower
- Fugaku: ~1 TB/s per node, 40.8 GB/s inter-node

The fundamental mismatch: neurosimulation needs ~PB/s of random-access memory bandwidth. Current architectures provide ~TB/s of sequential bandwidth per node and ~GB/s between nodes. The spike routing problem alone requires purpose-built interconnects or neuromorphic architectures that co-locate compute with memory.

**This is arguably the hardest engineering bottleneck for brain-scale simulation.** FLOPS are scaling faster than memory bandwidth (the "memory wall"), and the gap is widening.

### 1.4 Current and Projected Hardware

| System | Year | Peak FLOPS | HBM/node | Nodes |
|--------|------|-----------|----------|-------|
| El Capitan | 2024 | 2.88 ExaFLOPS | AMD MI300A, 128GB HBM3 | ~11K |
| Frontier | 2022 | 1.7 ExaFLOPS | AMD MI250X, 128GB HBM2e | 9,408 |
| Aurora | 2024 | ~2 ExaFLOPS | Intel GPU Max, 128GB HBM2e | 10,624 |
| JUPITER | 2025 | ~1 ExaFLOPS | NVIDIA GH200 | ~6,000 |

Projected 2030-2035:
- 10-100 ExaFLOPS systems are plausible with continued GPU scaling
- NVIDIA's roadmap (Rubin, post-Blackwell): ~2x perf/generation, ~2-year cadence
- B200: 4,500 TFLOPS FP8, 192 GB HBM3e, 8 TB/s bandwidth
- Memory bandwidth scaling: ~1.5-2x per generation, but this is slower than compute scaling

By 2035, a 10-100 ExaFLOPS cluster with ~10 PB of fast memory is plausible. This is sufficient for single-compartment HH whole-brain simulation if the memory bandwidth problem is solved (neuromorphic co-processing, near-memory compute, or novel architectures).

---

## 2. Scanning Technology Requirements

### 2.1 Resolution Requirements

| Information Target | Required Resolution | Technology |
|-------------------|---------------------|------------|
| Connectome (wiring diagram) | ~30 nm (synapse identification) | Serial-section EM |
| Synaptic weights (vesicle counts, PSD size) | ~5-10 nm | High-res EM |
| Ion channel distributions | ~1-5 nm | Immuno-EM, expansion microscopy |
| Full molecular state | ~0.1-1 nm (atomic) | Currently impossible in situ |

### 2.2 Electron Microscopy Throughput

The Google/Harvard 1 mm^3 cortex map (published Science, May 2024):
- **Volume:** 1 mm^3 of human temporal cortex
- **Data size:** 1.4 petabytes
- **Contents:** ~57,000 cells (16,000 neurons, 32,000 glia, 8,000 blood vessel cells), 150 million synapses, 230 mm of blood vessels
- **Sectioning:** ~5,000 serial sections, each 34 nm thick
- **Imaging:** Multi-beam SEM
- **Image acquisition time:** 326 days
- **Total project duration:** ~10 years (including development, analysis, proofreading)

#### Extrapolation to Full Brain

Human brain volume: ~1,200,000 mm^3 (1,200 cm^3).

Naive linear extrapolation from 1 mm^3:
- **Raw data:** 1.4 PB × 1.2×10^6 = **1.68 zettabytes** (1.68 × 10^6 PB)
- **Scan time:** 326 days × 1.2×10^6 = **~1,070 years** with one microscope setup

With SmartEM (Lichtman lab, 2025) achieving 5-7x speedup:
- **Scan time:** ~150-210 years with one setup
- **With 100 parallel microscopes:** ~1.5-2.1 years
- **With 1,000 parallel microscopes:** ~2-3 months

The microscopes exist. The parallelization is an engineering and funding problem, not a physics problem. Cost is the constraint: each high-end multi-beam SEM costs $2-5M. A 1,000-microscope facility would cost $2-5B in hardware alone.

### 2.3 Alternative Scanning Approaches

**LICONN (Light-microscopy-based connectomics, Nature 2025):**
- Uses expansion microscopy + hydrogel embedding
- First technology beyond EM capable of synapse-resolution connectome reconstruction
- Runs on standard off-the-shelf microscopes
- Achieves nanoscale resolution via ~4x physical tissue expansion
- ~10x cheaper than EM per volume
- Molecular information (protein identity) is directly incorporated via fluorescent labeling
- Throughput: potentially 10-100x faster than EM due to parallelization ease

**E11 Bio PRISM (2024-2025):**
- Combines expansion microscopy, barcode-based cell identification, and AI segmentation
- Claims 100x cost reduction vs conventional connectomics
- Roadmap: ~10x data volume increase per year
- Target: complete mouse connectome within 5 years (~2030)
- Self-proofreading AI models trained on barcode ground truth
- Addresses the 95% cost bottleneck (human proofreading)

**Light-sheet microscopy** with tissue clearing (CLARITY, iDISCO):
- Much faster volumetric imaging than serial-section EM
- Resolution: ~200-500 nm (insufficient for synapses without expansion)
- Combined with expansion: potentially synapse-resolving

### 2.4 Data Storage

Estimates for a full human connectome at synapse resolution:

| Source | Estimate |
|--------|----------|
| Linear extrapolation from Harvard 1mm^3 | ~1.4 ZB raw imaging data |
| Compressed/segmented connectome graph | ~100-1,000 PB |
| Synaptome storage (nanoscale volumetric) | 4.2-33.6 PB (microscale) to 5.6M EB (nanoscale) |
| Geometric connectivity model | 10.6-369 PB |

The raw imaging data (~1.4 ZB) is the dominant term, but this is intermediate data — you scan, segment, extract the graph, and discard the raw images. The actual connectome graph (neuron IDs + synapse locations + weights) compresses to perhaps 100-1,000 PB.

For context: global data storage capacity in 2025 is ~120 ZB. A single human connectome at full resolution would consume ~1% of global storage.

### 2.5 The Proofreading Bottleneck

This is the sleeper bottleneck. After imaging, the raw EM data must be segmented (which neurons does each pixel belong to?) and then proofread (fixing segmentation errors). In the FlyWire project, 139,255 neurons were proofread by a distributed team over several years.

Historical proofreading costs per neuron:
- C. elegans (1980s): ~$16,500/neuron
- Drosophila (2024): ~$100/neuron
- Mouse cortex (current): ~$1,000/neuron

To proofread a human connectome at $1,000/neuron: 86B × $1,000 = $86 trillion. Obviously infeasible.

Required cost targets:
- Mouse connectome ($10/neuron): $700M — plausible with AI proofreading
- Human connectome ($0.01/neuron): $860M — requires fully automated proofreading

Recent progress on automated proofreading:
- **RoboEM (2024):** 400x lower cost than manual proofreading
- **Autoproof (2025):** Achieves 90% of guided proofreading value at 20% of cost; automated 200K fragment attachments (equivalent to 4 proofreader-years)
- **E11 Bio PRISM:** Self-proofreading via barcode ground truth

The trend is clear: AI proofreading is improving fast enough that this bottleneck may be solved within 5-10 years. This is one area where LLM-era AI capabilities directly accelerate the timeline.

---

## 3. Information Content of a Human Brain

### 3.1 Estimates by Level

#### Connectome Only (Graph Topology)

86B neurons, each connecting to ~1,000-10,000 others (average ~7,000 synapses per neuron for ~100T total synapses).

Encoding: each synapse = source neuron ID + target neuron ID.
- 86B neurons need ~37 bits per ID
- 100T synapses × 74 bits = ~925 TB uncompressed
- With compression (adjacency lists, delta encoding): ~100-300 TB

#### Connectome + Synaptic Weights

Salk Institute (2016) showed synapses encode ~4.7 bits of information via 26 discrete size categories.
- 100T synapses × 4.7 bits = ~59 TB of weight information
- Total with topology: ~160-360 TB

#### Connectome + Weights + Ion Channel Distributions

Each neuron expresses ~1,000-10,000 different ion channel proteins in varying densities across its membrane. The spatial distribution matters (dendritic vs somatic vs axonal).

If each compartment (say 1,000 per neuron) needs ~100 parameters for ion channel densities:
- 86B neurons × 1,000 compartments × 100 parameters × 32 bits = ~34 PB
- Plus connectome: ~35 PB total

#### Full Molecular State

Every protein, every mRNA, every signaling molecule, every phosphorylation state.
- Estimated ~10^14 proteins per cell × 86B neurons = ~10^24 molecular states
- At ~100 bits per molecule state: ~10^25 bits = ~1.25 EB
- Upper bound estimates: hundreds of PB to low EB range

### 3.2 Summary Table

| Level | Information Content | Storage Required |
|-------|-------------------|-----------------|
| Connectome topology only | ~10^14 bits | ~100-300 TB |
| + Synaptic weights | ~5×10^14 bits | ~200-400 TB |
| + Ion channel distributions | ~3×10^17 bits | ~35 PB |
| + Full molecular state | ~10^19-10^25 bits | ~1-1,000 EB |

### 3.3 Shannon Information vs Structurally Relevant Information

A critical distinction: the total information content of a brain at molecular resolution (~EB) vastly exceeds the information content that's structurally relevant for behavior and identity.

Much of the molecular state is:
1. **Redundant** — thousands of copies of the same protein performing the same function
2. **Homeostatic** — ion channel distributions can be inferred from cell type + activity history
3. **Reconstructable** — given the connectome and cell types, many molecular parameters can be estimated from developmental rules

The question "how much information do you actually need to capture" depends entirely on what constitutes identity — which brings us back to the unsolved theory-of-consciousness problem.

**Lower bound (optimistic):** If the connectome + synaptic weights is sufficient, you need ~200-400 TB. This is eminently storable — it's about 200-400 high-capacity hard drives.

**Upper bound (pessimistic):** If the full molecular state matters, you need ~1+ EB. This is a significant fraction of a major cloud provider's total storage but not physically impossible.

---

## 4. Preservation Approach Engineering

### 4.1 Vitrification (Until Labs / Cradle, Alcor)

**Mechanism:** Perfuse cryoprotectant agents (CPAs) through the vasculature, then cool rapidly to below glass transition temperature (~-130C). The goal is to solidify tissue without ice crystal formation (which destroys cell structure).

**What's preserved:**
- Gross tissue architecture
- Cell membranes (partially — CPA toxicity causes some damage)
- Extracellular matrix
- Large protein structures

**What's lost or damaged:**
- CPA toxicity causes protein denaturation and lipid damage
- Perfusion is never complete — some regions freeze rather than vitrify
- Thermal stress during cooling can cause fracturing
- Molecular-level information (protein conformations, signaling states) is scrambled

**Evidence for connectome preservation:**
- Alcor's position: vitrification preserves gross structure but connectome preservation hasn't been definitively demonstrated at scale
- Cradle/Until Labs (2024): recovered electrical activity in vitrified/rewarmed rat cerebellar slices using VMPnoX — but this is tissue slices, not whole brains
- Fahy et al. (2012): recovered full normal-strength electrical activity and LTP in vitrified rabbit hippocampal slices using VM3

**Revival challenges:**
- CPA removal without osmotic shock
- Repair of cryoprotectant-induced damage
- Re-establishing blood flow and cellular metabolism
- No whole-brain revival has been demonstrated in any mammal

**Until Labs status (2026):**
- $100M+ raised (Founders Fund, Lux Capital)
- Roadmap: organ cryopreservation for transplant (near-term) → whole-body animal models (long-term)
- Currently focused on kidneys and liver, not brains specifically

**Assessment:** Vitrification is the only approach that even theoretically allows biological revival. The evidence is encouraging for tissue-level preservation but the gap between "slice maintains electrical activity" and "whole brain is reversibly preserved" is enormous. The cryoprotectant toxicity problem is a hard chemistry problem with no clear solution path.

### 4.2 Aldehyde-Stabilized Cryopreservation (ASC)

**Mechanism:** Perfuse glutaraldehyde (fixative) + sodium dodecyl sulfate (BBB modifier), then perfuse ethylene glycol (cryoprotectant), then cool to cryogenic temperatures.

**What's preserved:**
- Connectome at synapse resolution — **demonstrated and verified**
- Protein positions (cross-linked in place by glutaraldehyde)
- Cell morphology including dendritic spines
- Likely: synaptic weight information (PSD size, vesicle pools)

**What's lost:**
- All biological function — permanently and irreversibly
- Molecular dynamics (protein conformations frozen in cross-linked state)
- Metabolic state
- Some molecular information (glutaraldehyde modifies protein surfaces)

**Evidence:**
- Won the Brain Preservation Foundation's Large Mammal Prize (2018): demonstrated "near-perfect" connectome preservation in pig brains via EM
- The only technique that has been shown to preserve the connectome of a whole mammalian brain with visual verification

**The irreversibility problem:** ASC-preserved tissue is dead in the deepest sense. Glutaraldehyde cross-links every protein it contacts. There is no conceivable biological revival path. The only path from an ASC-preserved brain to any form of continuation is: scan the preserved brain → extract the connectome → simulate it in software.

**Assessment:** ASC is the gold standard for provable information preservation. If you believe the connectome is sufficient for identity (a big "if"), ASC is the most reliable way to preserve it. But it's a one-way door to the simulation approach.

### 4.3 Chemical Fixation + Plastination

**Mechanism:** Fix with glutaraldehyde/formaldehyde, dehydrate, impregnate with polymer resin (epoxy, silicone, or polyester).

**What's preserved:**
- Macroscale tissue architecture
- Cell morphology
- Connectome (if fixation quality is high)
- Room-temperature stable — no ongoing cryogenic storage needed

**What's lost:**
- Same as ASC: all biological function, irreversible
- Water content (replaced by polymer)
- Some molecular information
- Extracellular space volume changes (though recoverable via algorithms)

**Assessment:** Similar to ASC in preservation quality but room-temperature stable. No revival path. Advantage: decades/centuries of stable storage without active cooling. Used routinely for research specimens. The fixation step is the same chemistry as ASC — if ASC preserves the connectome, so does properly executed plastination.

### 4.4 Gradual Neural Replacement via BCI

**Concept:** Instead of scan-and-simulate, progressively replace biological neurons with artificial ones while maintaining consciousness continuity (Ship of Theseus approach).

**Requirements:**
- Bidirectional interface to every neuron being replaced
- Real-time, low-latency artificial neuron that matches the biological one's input/output function
- Gradual handoff: artificial neuron must mirror biological behavior before the biological one is removed
- Koene/Wiley estimate: ~1,000 days for full replacement

**Bandwidth requirements:**
To monitor and replace a single neuron, you need to:
1. Record all synaptic inputs (~7,000 synapses, each at ~100 Hz average event rate)
2. Record the neuron's output (firing pattern at ~1-100 Hz)
3. Inject current/signals to verify the artificial neuron matches

Per neuron: ~700,000 synaptic events/s input + output = ~1M events/s
For all 86B neurons simultaneously: ~86×10^15 events/s

Even replacing neurons one at a time, you still need to interface with all ~7,000 pre- and post-synaptic partners of the target neuron simultaneously, which means BCI access to thousands of arbitrary neurons with single-synapse resolution.

**Assessment:** The most philosophically satisfying approach but the most technically distant. Requires advances in BCI bandwidth (Section 5), nanoscale surgical robots, and real-time single-neuron computational models — essentially all the hardest problems simultaneously. Not feasible this century with any known technology trajectory.

---

## 5. The Bandwidth Problem

### 5.1 Current BCI Read Bandwidth

| Technology | Electrodes/Channels | Neurons Simultaneously Recorded | Year |
|-----------|---------------------|-------------------------------|------|
| Utah Array (Blackrock) | 96-128 | ~100-200 | 2012+ |
| Neuralink N1 | 1,024 (active) / 3,072 (total) | ~hundreds | 2024-2025 |
| Neuropixels 2.0 | 5,120 sites / 384 simultaneous | ~hundreds per shank | 2021+ |
| Neuropixels Ultra | 6,144 sites / 384 simultaneous | ~2x yield vs NP 2.0 | 2025 |
| Paradromics | 421 | ~hundreds | 2025 |
| Multi-probe Neuropixels (research) | 8+ probes | ~thousands | 2025 |

**Best case today (research setting):** ~10,000 neurons recorded simultaneously using multiple Neuropixels probes in an animal model. In humans: ~200-1,000 neurons with Neuralink or intraoperative Neuropixels.

### 5.2 Required Bandwidth

For whole-brain emulation via scanning: not directly a BCI problem — you scan a dead/fixed brain.

For gradual neural replacement:
- **Minimum:** All 86 billion neurons, bidirectionally, with single-synapse resolution
- **Conservatively:** 86×10^9 read channels + 86×10^9 write channels
- **Data rate per channel:** ~30 kHz sampling (to capture spike waveforms) × 16 bits = 480 kbit/s
- **Total bandwidth:** ~86×10^9 × 480 kbit/s × 2 (bidirectional) = **~8.3×10^16 bit/s = ~10 PB/s**

### 5.3 The Gap

| Metric | Current (2025) | Required | Gap |
|--------|----------------|----------|-----|
| Simultaneous neurons | ~10,000 | 86,000,000,000 | ~10^7 (7 orders of magnitude) |
| Data rate | ~100 Mbit/s | ~10 PB/s | ~10^8 (8 orders of magnitude) |
| Spatial coverage | ~1 mm^3 | ~1,200,000 mm^3 | ~10^6 |
| Electrode density | ~1,000/mm^2 | every neuron in 3D | qualitatively different |

### 5.4 Scaling Curves and Projections

Electrode count has roughly doubled every 7-8 years since the 1950s (Stevenson & Kording, 2011). At this rate:

- 10,000 neurons (2025)
- 20,000 neurons (~2032)
- 40,000 neurons (~2040)
- 86 billion neurons: ~log2(86×10^9 / 10^4) × 7.5 years ≈ 23 doublings × 7.5 years ≈ **~170 years from now**

Even with acceleration to doubling every 3 years (aggressive):
- 23 doublings × 3 years = **~70 years from now** (2095)

With further acceleration to doubling every 2 years:
- 23 doublings × 2 years = **~46 years from now** (2071)

These projections assume the doubling trend continues indefinitely, which requires qualitative breakthroughs — not just scaling current electrode technology, but entirely new paradigms (neural dust, molecular-scale interfaces, engineered neurons with built-in readout, optogenetics at scale, etc.).

**Honest assessment:** No currently known scaling trend reaches 86B-neuron full-brain BCI within this century. The gradual-replacement approach requires a technology discontinuity — something fundamentally different from electrodes.

---

## 6. Critical Path Analysis

### 6.1 The Two Viable Paths

Given the analysis above, there are only two paths with any engineering plausibility this century:

**Path A: Preserve → Scan → Simulate**
1. Preserve the brain (vitrification or ASC)
2. Destructively scan it (serial-section EM or expansion microscopy)
3. Reconstruct the connectome computationally
4. Simulate the reconstructed brain

**Path B: Gradual Replacement via Advanced BCI**
1. Develop brain-wide, single-neuron-resolution BCI
2. Build real-time computational neuron models
3. Progressively replace biological neurons
4. Maintain continuous consciousness throughout

Path B requires solving every problem in Path A plus the BCI bandwidth problem plus the real-time replacement problem. Path A is strictly easier from an engineering standpoint, though it requires the philosophical concession that a simulation of your brain IS you.

### 6.2 Critical Path for Path A (Preserve → Scan → Simulate)

```
Year  Milestone                                          Current Status
----------------------------------------------------------------------
Now   Preservation (ASC/vitrification)                   AVAILABLE (ASC proven)
2025  AI-automated proofreading                          IN PROGRESS (RoboEM, Autoproof)
2026  Mouse connectome imaging begins                    STARTING (E11 Bio PRISM)
~2030 Complete mouse connectome (~70M neurons)            5 years out
~2030 First mouse brain simulation at HH level           Depends on connectome
~2032 10 ExaFLOPS compute available                      On track (hardware roadmap)
~2035 Human brain scanning begins                        Depends on cost reduction
~2040 Human connectome reconstructed                     Depends on scanning + proofreading
~2040 100 ExaFLOPS compute available                     Plausible
~2045 First human brain simulation (HH level)            Depends on everything above
```

### 6.3 Bottleneck Ranking

Ranked by "if this were solved tomorrow, how much would the timeline accelerate":

1. **Theory of consciousness / minimum viable fidelity** — The single most important unknown. If point-neuron models are sufficient, we might be 10-15 years away. If full molecular state is required, we're 100+ years away. This isn't an engineering problem — it's a science problem. No amount of compute or scanning helps if we don't know what to simulate.

2. **Scanning throughput + cost** — Currently the primary engineering bottleneck. A full human brain at EM resolution would take ~1,000 years with one microscope. Even with 1,000 microscopes and SmartEM acceleration, it's months to years and billions of dollars. LICONN/PRISM could reduce this by 10-100x.

3. **Automated proofreading/segmentation** — Currently 95%+ of connectomics cost. AI is solving this fast (RoboEM: 400x cost reduction). Likely solved within 5-10 years. This is the bottleneck where AI progress has the most direct impact.

4. **Compute (FLOPS + memory bandwidth)** — For HH single-compartment models, exascale hardware is within reach. For multi-compartment, 3-4 OOM gap. Memory bandwidth is the harder sub-problem (see Section 1.3). Purpose-built neuromorphic hardware could help but doesn't exist at scale.

5. **BCI bandwidth** — Only relevant for Path B (gradual replacement). 7+ orders of magnitude gap with no clear scaling path. This is not on any plausible critical path for this century.

6. **Data storage** — A full human connectome is ~100-1,000 PB post-processing. Large by current standards but not physically impossible. Cloud providers already manage EB-scale storage. This is a money problem, not a physics problem. **Not a real bottleneck.**

### 6.4 Minimum Viable Preservation Plan (Today)

Given current technology, the minimum viable plan for someone who wants to maximize their chances:

1. **Arrange for ASC or high-quality vitrification upon legal death.** ASC is superior for information preservation; vitrification is superior if you want any chance of biological revival. Until Labs and Alcor are the current options.

2. **Hope that within your storage period:**
   - Scanning technology improves to the point where a human brain can be destructively scanned (~2035-2045)
   - Automated proofreading makes connectome reconstruction feasible (~2030-2035)
   - Compute reaches the level needed for whole-brain simulation (~2035-2050)
   - Neuroscience determines the minimum fidelity level required (unknown timeline)

3. **Cost estimate for the full pipeline:**
   - Preservation: $28K-$200K (Alcor neuro vs whole-body)
   - Storage: $100-500/year indefinitely
   - Scanning (future): ~$1-10B at current cost curves, possibly $10-100M by 2045
   - Compute (future): ~$10-100M for dedicated simulation hardware
   - Total: preservation is cheap; the scan-and-simulate step is the expensive part

### 6.5 The Honest Summary

The engineering requirements for consciousness preservation are staggering but not physically impossible at any specific point in the pipeline. The actual blockers are:

- **We don't know what level of detail is needed** (theory gap)
- **Scanning a whole brain at synapse resolution takes ~1,000 microscope-years** (throughput gap, closing)
- **Memory bandwidth for real-time simulation is 3-4 OOM beyond current hardware** (architecture gap)
- **BCI bandwidth for gradual replacement is 7+ OOM beyond current technology** (physics gap)

The most encouraging recent developments (2024-2025):
- FlyWire: Complete fly brain connectome, functional simulation on a laptop
- LICONN/PRISM: 10-100x cheaper connectomics via light microscopy
- AI proofreading: 400x cost reduction (RoboEM)
- Until Labs: $100M+ for reversible cryopreservation
- SmartEM: 5-7x faster EM scanning
- State of Brain Emulation Report 2025: first comprehensive reassessment since 2008

The most discouraging realities:
- The fly brain has 139K neurons. The human brain has 86B. That's a factor of 618,000.
- Memory bandwidth is scaling slower than compute, and brain simulation is memory-bound.
- We have mapped exactly 0.0000083% of a single human brain at synapse resolution (1 mm^3 out of 1.2M mm^3).
- Nobody knows if the connectome is sufficient, or if you need the full molecular state.
- Fewer than 500 people globally work on brain emulation.

**Timeline estimate (60% confidence interval):**
- First insect-brain-scale emulation (sub-1M neurons): 2028-2035
- First mouse-brain-scale emulation: 2035-2050
- First human-brain-scale emulation: 2045-2070
- Whether that emulation constitutes "consciousness preservation": unknown, possibly unknowable

---

## References and Sources

### Brain Simulation and Compute
- [Blue Brain Project - Wikipedia](https://en.wikipedia.org/wiki/Blue_Brain_Project)
- [Future projections for mammalian whole-brain simulations (ScienceDirect, 2024)](https://www.sciencedirect.com/science/article/pii/S016801022400138X)
- [Fudan University Digital Twin Brain (Nature Computational Science, 2024)](https://www.nature.com/articles/s43588-024-00731-3)
- [Building Brains on a Computer (Asimov Press)](https://press.asimov.com/articles/brains)
- [ExaFlexHH: Exascale-ready HH simulation on FPGAs (Frontiers, 2024)](https://www.frontiersin.org/journals/neuroinformatics/articles/10.3389/fninf.2024.1330875/full)
- [NEST GPU simulation on Fugaku (TOP500)](https://www.top500.org/news/software-breakthrough-paves-the-way-for-full-brain-simulations-on-exascale-supercomputers/)
- [Sandberg & Bostrom WBE Roadmap (2008)](https://www.openphilanthropy.org/wp-content/uploads/SandbergandBostrom2008.pdf)
- [State of Brain Emulation Report 2025 (arXiv: 2510.15745)](https://arxiv.org/abs/2510.15745)
- [Brain performance in FLOPS - AI Impacts](https://aiimpacts.org/brain-performance-in-flops/)

### Connectomics and Scanning
- [Google/Harvard 1mm^3 cortex map (Science, 2024)](https://www.science.org/doi/10.1126/science.adk4858)
- [Harvard Gazette coverage](https://news.harvard.edu/gazette/story/2024/05/the-brain-as-weve-never-seen-it/)
- [FlyWire connectome (Nature, 2024)](https://www.nature.com/articles/s41586-024-07686-5)
- [LICONN: Light-microscopy connectomics (Nature, 2025)](https://www.nature.com/articles/s41586-025-08985-1)
- [E11 Bio PRISM Roadmap](https://www.e11.bio/blog/roadmap)
- [SmartEM: ML-guided electron microscopy (Nature Methods, 2025)](https://www.nature.com/articles/s41592-025-02929-3)
- [RoboEM automated proofreading (Nature Methods, 2024)](https://www.nature.com/articles/s41592-024-02226-5)
- [Autoproof: Automated segmentation proofreading (arXiv, 2025)](https://arxiv.org/abs/2509.26585)
- [Beam deflection TEM (Nature Communications, 2024)](https://www.nature.com/articles/s41467-024-50846-4)

### Brain Information Content
- [Salk Institute: Synapse information capacity ~4.7 bits](https://www.salk.edu/news-release/memory-capacity-of-brain-is-10-times-more-than-previously-thought/)
- [Nanoscale synaptome storage estimation (PMC, 2024)](https://pmc.ncbi.nlm.nih.gov/articles/PMC11423976/)
- [Big data challenges of connectomics (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4412267/)

### Preservation Approaches
- [Until Labs (Cradle) $48M launch](https://longevity.technology/news/cradle-emerges-with-48m-to-build-reversible-cryonics-technology/)
- [Until Labs $58M Series A](https://longevity.technology/news/cryopreservation-startup-lands-58m-to-pause-biological-time/)
- [ASC - Brain Preservation Foundation Prize](https://www.brainpreservation.org/21cm-aldehyde-stabilized-cryopreservation-eval-page/)
- [Structural brain preservation (Frontiers, 2024)](https://www.frontiersin.org/journals/medical-technology/articles/10.3389/fmedt.2024.1400615/full)
- [Alcor cryopreservation procedures](https://www.alcor.org/cryopreservation-procedures/)

### BCI and Neural Interfaces
- [Neuralink 2025 overview (MIT Technology Review)](https://www.technologyreview.com/2025/01/16/1110017/what-to-expect-from-neuralink-in-2025/)
- [Neuropixels Ultra (Neuron, 2025)](https://www.cell.com/neuron/fulltext/S0896-6273(25)00665-8)
- [Neuropixels 2.0 (Science, 2021)](https://www.science.org/doi/10.1126/science.abf4588)
- [BCIs in 2025 (Andersen Lab)](https://andersenlab.com/blueprint/bci-challenges-and-opportunities)

### Hardware
- [TOP500 November 2025](https://top500.org/lists/top500/2025/11/)
- [El Capitan (LLNL)](https://www.llnl.gov/article/53596/el-capitan-retains-title-worlds-fastest-supercomputer-latest-top500-list)
- [NVIDIA B200 vs H100 comparison](https://www.civo.com/blog/comparing-nvidia-b200-and-h100)

### Molecular Dynamics
- [MD simulations of ion channels (Trends in Biochemical Sciences, 2021)](https://www.cell.com/trends/biochemical-sciences/fulltext/S0968-0004(21)00073-6)
- [Anton 3: 20 microseconds MD before lunch](https://dl.acm.org/doi/pdf/10.1145/3458817.3487397)
- [Memory bandwidth as AI bottleneck (arXiv, 2024)](https://arxiv.org/html/2403.14123v1)

### Philosophy and Approaches
- [Chalmers - Mind Uploading philosophical analysis](https://consc.net/papers/uploading.pdf)
- [Gradual replacement analysis (arXiv)](https://arxiv.org/pdf/1504.06320)
- [OpenWorm - C. elegans simulation](https://en.wikipedia.org/wiki/OpenWorm)
- [Eon Systems - Fly brain emulation](https://eon.systems/updates/embodied-brain-emulation)
