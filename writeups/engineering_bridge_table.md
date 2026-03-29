# Engineering Bridge Table: Consciousness Theories to Implementation Requirements

## Summary Table

| Theory | Required Fidelity | Scanning Resolution | Raw Data Size | Compute (FLOPS) | Storage (processed) | BCI Bandwidth for Gradual | Feasibility Timeline |
|--------|-------------------|--------------------:|---------------|-----------------|---------------------|---------------------------|---------------------|
| **IIT 4.0** | Full causal architecture (every element's TPM) | ~5 nm (sub-synaptic, all causal micro-states) | ~10^20 bytes (100 EB) | Verification: super-exp (~2^(2^n)); Simulation: 10^22 | ~10 EB | Infeasible (requires full causal graph) | >2100 / possibly never |
| **GNWT** | Connectome + weights + ignition dynamics | ~10 nm (synapse-level EM) | ~1 ZB raw; ~2 PB processed | 10^18 - 10^22 | ~2 PB | ~10^7 neurons/s @ 10 kHz | 2060-2080 |
| **HOT** | Connectome + weights (PFC + sensory targets) | ~10 nm (same as GNWT for relevant areas) | ~200 TB - 1 PB | 10^17 - 10^20 | ~500 TB | ~10^6 neurons/s @ 10 kHz | 2055-2075 |
| **Predictive Processing** | Generative model + precision weights + body model | ~10-100 nm (connectivity + neuromodulatory) | ~5 PB | 10^18 - 10^21 | ~5 PB | ~10^7 neurons/s @ 1 kHz | 2060-2080 |
| **RPT** | Recurrent connectivity + sub-ms timing | ~10 nm + temporal: 0.1 ms | ~2 PB + temporal calibration | 10^18 - 10^20 | ~2 PB | ~10^7 neurons/s @ 100 kHz | 2060-2080 |
| **Biological Computationalism** | Molecular-level snapshot | ~1 nm (protein conformations) | ~1-3 ZB | 10^25 | ~10-100 PB | Infeasible with current paradigms | 2080-2100+ |
| **Orch OR** | Quantum states of microtubules + connectome | Sub-nm + quantum state tomography | Formally infinite (no-cloning) | 10^25+ (quantum sim) | N/A (no-cloning) | Physically impossible | Never (under known physics) |
| **AST** | Attention schema + self-model + episodic memory | ~1 um (regional connectivity) | ~1-10 TB | 10^15 - 10^18 | ~1-10 TB | ~10^5 neurons/s @ 1 kHz | 2040-2060 |

---

## Detailed Derivations by Theory

### 1. IIT 4.0 (Integrated Information Theory)

**What "full causal architecture" means in engineering terms:**

IIT 4.0 requires specifying the complete Transition Probability Matrix (TPM) of the system -- every element's causal contribution to every other element across all possible states. This is not merely the connectome; it is the full causal specification including nonlinear dynamics, neuromodulation, and state-dependent interactions.

**Scanning Resolution:**
- Must capture every causally relevant micro-state, including synaptic weights, ion channel states, receptor densities, and neuromodulatory tone
- Minimum ~5 nm to resolve receptor subtypes and post-synaptic density structure
- Effectively requires sub-synaptic resolution across the entire brain

**Data Size (full causal specification):**
- 86 billion neurons, ~100 trillion (10^14) synapses
- Each synapse requires: weight (4 bytes), ~20 parameters for causal transition probabilities (receptor types, plasticity state, neuromodulatory sensitivity) = ~100 bytes/synapse
- Synaptic data: 10^14 x 100 bytes = 10^16 bytes (10 PB)
- Causal TPM for verification: For N binary elements, the TPM has N x 2^N entries. Even for a reduced "macro" grain of 10^5 macro-elements, the TPM is 10^5 x 2^(10^5), which is unrepresentable
- Practical estimate for scan data alone: ~10^20 bytes (100 EB)

**Compute for Phi verification:**
- Computing Phi requires finding the Minimum Information Partition (MIP), which involves evaluating all possible bipartitions
- For N elements, the number of bipartitions is the Bell number B(N), which grows super-exponentially
- Complexity class: super-exponential, specifically ~2^(2^N) for exact Phi computation
- For even 40 binary elements, this is already computationally infeasible (cited in Tegmark 2016, Barrett & Seth 2011)
- For 86 billion neurons: formally uncomputable with any conceivable classical computer
- Even with proposed approximations (e.g., tensor network / MPS methods), scaling to realistic neural systems remains intractable

**Compute for simulation at this fidelity:**
- Sandberg & Bostrom electrophysiology level: 10^22 FLOPS
- IIT requires more than electrophysiology (full causal dynamics), so ~10^22 FLOPS minimum for simulation alone

**Sources:**
- Tononi et al., "Integrated information theory (IIT) 4.0," PLOS Computational Biology (2023): [PMC10581496](https://pmc.ncbi.nlm.nih.gov/articles/PMC10581496/)
- Barrett & Seth, "Practical measures of integrated information," PLOS Computational Biology (2011)
- Tegmark, "Improved measures of integrated information," PLOS Computational Biology (2016)

---

### 2. GNWT (Global Neuronal Workspace Theory)

**What "connectome + weights + ignition dynamics" means:**

GNWT requires the full connectome (which neurons connect to which), synaptic weights, and the ability to simulate ignition -- the nonlinear, NMDA-mediated amplification event where workspace neurons in PFC/parietal cortex broadcast information globally.

**Scanning Resolution:**
- Synapse-level connectivity requires ~10 nm voxels (electron microscopy resolution)
- The Google/Harvard 2024 study achieved this: 1 mm^3 at ~6 nm resolution, yielding 57,000 cells, 150M synapses, 1.4 PB of raw data
- Scaling to whole brain (1.26 x 10^6 mm^3): ~1.6 ZB raw imaging data

**Data Size (parameters per synapse x synapse count):**
- Parameters per synapse for Hodgkin-Huxley-level simulation:
  - Synaptic weight: 4 bytes
  - Receptor type (AMPA/NMDA/GABA): 1 byte
  - Time constants (rise, decay): 8 bytes
  - Short-term plasticity state: 4 bytes
  - Location on dendrite: 4 bytes
  - Total: ~21 bytes/synapse, round to ~20 bytes
- 10^14 synapses x 20 bytes = 2 x 10^15 bytes = **2 PB processed connectome**
- Per neuron state (HH model): ~200 bytes (membrane potential, ion channel gates, Ca2+ concentration, compartments)
- 86 x 10^9 neurons x 200 bytes = 17 TB neuron state data
- Total processed model: **~2 PB**

**FLOPS for simulation:**
- Hodgkin-Huxley single-compartment: ~1,200 FLOPS per neuron per 0.1 ms timestep (estimated from: 4 ODEs per channel type x ~5 channel types x ~10 operations per ODE x 6 integration steps)
- At 10 kHz simulation rate (0.1 ms timestep): 1,200 FLOPS/neuron/step x 10,000 steps/s = 1.2 x 10^7 FLOPS/neuron/s
- 86 x 10^9 neurons x 1.2 x 10^7 = **~10^18 FLOPS** (spiking neural network level)
- Multi-compartment HH (100 compartments/neuron): **~10^20 FLOPS**
- With full electrophysiology (ion channel kinetics, synaptic dynamics, dendritic processing): **~10^22 FLOPS** (Sandberg & Bostrom electrophysiology estimate)

**Blue Brain Project comparison:**
- Blue Brain simulated ~31,000 neurons (one neocortical column) with ~37 million synapses at HH detail
- This is 31,000 / 86,000,000,000 = 3.6 x 10^-7 of the brain (0.000036%)
- Scaling factor to whole brain: ~2.8 million x
- Blue Brain used ~1 PFLOPS (10^15) for this column; naive scaling: ~2.8 x 10^21 FLOPS for full brain
- Consistent with Sandberg & Bostrom 10^22 estimate

**Sources:**
- Sandberg & Bostrom, "Whole Brain Emulation: A Roadmap" (2008), FHI Technical Report
- Markram et al., "The Blue Brain Project," Nature Reviews Neuroscience (2006)
- Shapson-Coe et al., "A petavoxel fragment of human cerebral cortex," Science (2024): [DOI](https://www.science.org/doi/10.1126/science.adk4858)
- Dehaene, Lau & Kouider, "What is consciousness, and could machines have it?" Science (2017)

---

### 3. HOT (Higher-Order Thought Theory)

**What "first-order + higher-order monitoring systems" means:**

HOT requires only that the higher-order monitoring circuits (primarily PFC) and their target first-order representations (sensory cortices) are faithfully captured. Non-consciousness-relevant areas (cerebellum, basal ganglia motor loops, spinal cord) may not need full fidelity.

**Potential subset estimation:**
- PFC: ~15-20% of cortical neurons, ~4 billion neurons
- Sensory cortices being monitored: ~20-30% of cortex, ~6 billion neurons
- Long-range connectivity between them: critical, full resolution needed
- Supporting circuitry (thalamus, basal ganglia): ~5 billion neurons at reduced resolution
- Total high-fidelity requirement: ~10-15 billion neurons (~15% of brain)
- Remaining ~70 billion neurons: could use coarser models (integrate-and-fire, ~10 bytes/neuron)

**Scanning Resolution:**
- High-fidelity regions: ~10 nm (same as GNWT)
- Low-fidelity regions: ~100 nm - 1 um sufficient
- Mixed-resolution scanning reduces raw data by ~5-10x vs full GNWT scan

**Data Size:**
- High-fidelity: 15 x 10^9 neurons, proportional synapses (~20 x 10^12) x 20 bytes = 400 TB
- Low-fidelity: 70 x 10^9 neurons x 100 bytes = 7 TB
- Total: **~400 TB - 1 PB**

**FLOPS:**
- High-fidelity HH simulation of 15B neurons: ~10^17 - 10^19 FLOPS
- Low-fidelity remaining: ~10^15 FLOPS
- Total: **~10^17 - 10^20 FLOPS** (depending on compartmental detail)

**Sources:**
- Rosenthal, "Consciousness and Mind" (2005)
- Lau & Rosenthal, "Empirical support for higher-order theories of conscious awareness," Trends in Cognitive Sciences (2011)
- Brown, Lau & LeDoux, "Understanding the Higher-Order Approach to Consciousness," Trends in Cognitive Sciences (2019)

---

### 4. Predictive Processing / Free Energy Principle

**What "generative model + precision weights + embodiment" means:**

The brain is modeled as a hierarchical Bayesian inference engine. Consciousness arises from the precision-weighted prediction error minimization across a deep generative model.

**Hierarchical predictive model parameters:**
- Cortical hierarchy: ~6 levels (V1 -> V2 -> V4 -> IT -> PFC -> meta-cognitive)
- Each level has prediction units and error units
- Parameters: ~10^14 synaptic weights (same as connectome) PLUS:
  - Precision weights (gain modulation): 1 parameter per prediction error unit
  - Neuromodulatory state: dopamine, serotonin, norepinephrine, acetylcholine concentrations at ~1 mm^3 spatial resolution
  - Brain volume ~1.26 x 10^6 mm^3, 4 neuromodulators x 4 bytes = 16 bytes per voxel = ~20 MB neuromodulatory map
  - But effective precision modulation at synaptic level: 10^14 x 4 bytes = 400 TB additional
- Total parameter count: ~2x the connectome weights = **~4-5 PB**

**Neuromodulatory state (precision weighting):**
- ~200 types of neuromodulatory receptors across the brain
- Receptor density maps at ~10 um resolution: 1.26 x 10^12 voxels x 200 types x 4 bytes = ~1 PB
- Tonic neuromodulator levels: negligible by comparison
- Total neuromodulatory data: **~1 PB**

**Embodiment (body model):**
- Interoceptive model: ~500 million visceral afferents, proprioceptors, etc.
- Musculoskeletal model: ~600 muscles x kinematic parameters = negligible
- Autonomic nervous system state: ~10^8 neurons in enteric/autonomic systems
- Virtual body simulation: ~10^14 FLOPS (relatively small addition)
- Body model data: **~100 GB - 1 TB**

**Scanning Resolution:**
- Connectivity: ~10-100 nm for synapses
- Neuromodulatory receptor maps: ~10 um (achievable with immunohistochemistry + light microscopy)
- Mixed resolution approach practical

**FLOPS for simulation:**
- Predictive coding updates are essentially matrix operations on hierarchical representations
- At synaptic grain: comparable to GNWT, ~10^18 - 10^21 FLOPS
- With precision-weighted updates adding ~2x overhead: ~10^18 - 10^21

**Sources:**
- Friston, "The free-energy principle: a unified brain theory?" Nature Reviews Neuroscience (2010)
- Clark, "Whatever next? Predictive brains, situated agents, and the future of cognitive science," Behavioral and Brain Sciences (2013)

---

### 5. RPT (Recurrent Processing Theory)

**What "recurrent connectivity + temporal dynamics" means:**

RPT (Lamme) holds that consciousness arises from recurrent (feedback) processing within sensory cortices. The key requirement beyond GNWT is precise temporal dynamics -- the timing of feedback signals must be preserved at sub-millisecond resolution.

**Temporal resolution requirements:**
- Feedforward sweep: ~60-100 ms post-stimulus
- Recurrent processing onset: ~100-150 ms post-stimulus
- The critical window for conscious recurrent processing: ~100-300 ms
- V1-V2 signal transmission: ~15 ms
- To faithfully reproduce recurrent timing: **0.1 ms temporal resolution** (10 kHz minimum, ideally 100 kHz for sub-ms dynamics)

**Scanning Resolution:**
- Same as GNWT for connectivity: ~10 nm
- Additionally requires: axonal conduction velocity calibration (myelination thickness, axon diameter)
- Axon diameter measurement: ~10 nm resolution sufficient
- Temporal calibration adds ~10 bytes per axonal segment, ~10^11 segments = ~1 TB additional data

**Data Size:**
- Base connectome (same as GNWT): ~2 PB
- Temporal calibration data: ~1 TB
- Total: **~2 PB**

**FLOPS:**
- Similar to GNWT but temporal precision may require 100 kHz simulation (10x more steps)
- Spiking network at 100 kHz: ~10^19 FLOPS
- HH at 100 kHz: ~10^20 - 10^21 FLOPS
- Potentially less total if only sensory cortices need full recurrent fidelity: ~10^18 - 10^20

**Sources:**
- Lamme, "The distinct modes of vision offered by feedforward and recurrent processing," Trends in Neurosciences (2000)
- Lamme, "Towards a true neural stance on consciousness," Trends in Cognitive Sciences (2006)

---

### 6. Biological Computationalism

**What "molecular-level snapshot" means:**

This view holds that consciousness depends on the specific biological substrate -- not just connectivity and weights, but the actual molecular machinery: protein conformations, ion channel distributions, glial cell states, extracellular ionic environment.

**Scanning Resolution:**
- Protein conformations: ~0.1-1 nm (cryo-EM level)
- Ion channel gating states: ~0.5 nm
- Effectively sub-nanometer across the entire brain volume

**Ion channel distributions:**
- ~60 major ion channel types in the brain (40 Kv + 10 Nav + 10 Cav)
- Including splice variants and accessory subunits: ~200 functionally distinct channel types
- Average channel density: ~1,000-10,000 channels per neuron
- 86 x 10^9 neurons x 5,000 channels x 200 bytes per channel state = **86 TB** for ion channel state alone
- Spatial distribution across membrane: increases to ~1 PB with positional data

**Glial cells:**
- ~85-170 billion glial cells (roughly 1:1 with neurons, recent estimates)
- Types: astrocytes (~40%), oligodendrocytes (~40%), microglia (~10%), NG2 cells (~10%)
- State information per astrocyte:
  - Intracellular Ca2+ dynamics (multiple compartments): ~1 KB
  - Gap junction coupling state: ~100 bytes
  - Glutamate/GABA transporter state: ~200 bytes
  - Metabolic state (lactate, glucose): ~100 bytes
  - Total: ~1.5 KB per glial cell
- 170 x 10^9 x 1.5 KB = **~255 TB** for glial state

**Extracellular concentrations:**
- Key ions: Na+, K+, Ca2+, Cl-, H+ (pH), glutamate, GABA, neuromodulators (~20 species)
- Spatial resolution needed: ~1 um^3 (diffusion length scale)
- Brain volume: 1.26 x 10^6 mm^3 = 1.26 x 10^15 um^3
- 20 species x 4 bytes each x 1.26 x 10^15 voxels = **~100 PB**

**Total data size estimate:**
- Raw scan data at 1 nm resolution: ~2,800 EB (2.8 ZB) per the nanoscale connectome estimate
- Processed molecular state: ion channels (1 PB) + glial (255 TB) + extracellular (100 PB) + connectome (2 PB) + protein states (~100 PB)
- Total processed: **~200 PB - 1 ZB** depending on resolution
- Raw scan data: **~1-3 ZB**

**FLOPS:**
- Sandberg & Bostrom metabolome level: **10^25 FLOPS**
- This accounts for molecular dynamics of key signaling pathways
- Full molecular dynamics of all proteins: would exceed 10^30 FLOPS (impractical even in principle near-term)

**Sources:**
- Sandberg & Bostrom, "Whole Brain Emulation: A Roadmap" (2008)
- Bhatt et al., "Toward the Human Nanoscale Connectome," LNCS (2023): [Springer](https://link.springer.com/chapter/10.1007/978-3-031-36021-3_66)
- Human Protein Atlas: [proteinatlas.org](https://www.proteinatlas.org/news/2024-05-22/a-single-cubic-millimeter-of-human-brain-has-generated-1-4-petabytes-of-data)

---

### 7. Orch OR (Orchestrated Objective Reduction)

**What "quantum states + connectome" means:**

Penrose-Hameroff Orch OR proposes that consciousness arises from quantum computations in microtubules within neurons. Preserving consciousness requires preserving the quantum state of these structures.

**Tubulin count:**
- ~10^4 microtubules per neuron (10,000)
- ~10^8 tubulin dimers per neuron (100 million)
- 86 x 10^9 neurons x 10^8 tubulins = **8.6 x 10^18 tubulin dimers** in the brain
- Each tubulin dimer has multiple quantum degrees of freedom (dipole orientation, pi-electron delocalization)
- Quantum state specification: each tubulin is at minimum a qubit, potentially a qu-dit with d~10-100 states
- Full quantum state: 8.6 x 10^18 qubits minimum -> density matrix has 2^(8.6 x 10^18) entries
- This is a number so large it exceeds any meaningful physical quantity

**No-cloning theorem implications:**
- The no-cloning theorem (Wootters & Zurek, 1982) states: it is impossible to create an identical copy of an arbitrary unknown quantum state
- This means: you cannot scan the quantum state of microtubules without destroying it
- Quantum state tomography can characterize a state, but requires many identical copies of the same state -- which biological microtubules cannot provide
- Even partial measurement collapses the quantum state, fundamentally altering the system

**Is this physically possible to measure?**
- **No.** Under known physics, faithful quantum state capture of ~10^18 qubits in a warm, wet biological environment is impossible for multiple independent reasons:
  1. No-cloning prevents non-destructive copying
  2. Quantum decoherence in biological tissue occurs on ~10^-13 s timescales (Tegmark 2000), far faster than any measurement
  3. The Hilbert space dimension (2^(10^18)) exceeds the number of particles in the observable universe (~10^80)
  4. No known scanning technology can measure quantum coherence in individual tubulin dimers in situ

**FLOPS for quantum simulation:**
- Simulating N qubits classically requires O(2^N) operations
- For 10^18 qubits: 2^(10^18) FLOPS -- a number with ~3 x 10^17 digits
- Even on a hypothetical quantum computer: 10^18 logical qubits with error correction would require ~10^21+ physical qubits
- Current quantum computers: ~1,000 logical qubits (2025)

**Sources:**
- Penrose & Hameroff, "Orchestrated reduction of quantum coherence in brain microtubules," Mathematics and Computers in Simulation (1996)
- Tegmark, "Importance of quantum decoherence in brain processes," Physical Review E (2000)
- Wootters & Zurek, "A single quantum cannot be cloned," Nature (1982)

---

### 8. AST (Attention Schema Theory)

**What "attention schema + self-model + memories" means:**

Graziano's AST proposes consciousness is the brain's simplified internal model of its own attention process. This is potentially the most compact representation because it does not require capturing every neuron -- only the functional model the brain uses to describe its own attention.

**Minimum parameter count:**
- The attention schema is a simplified, low-dimensional model -- analogous to the body schema
- Body schema: ~10^3-10^4 parameters (joint angles, limb positions, etc.)
- Attention schema: plausibly similar order -- ~10^4-10^5 parameters describing:
  - What is being attended to (object/location representations)
  - Intensity/salience of attention
  - Attribution of attention to self vs others (theory of mind)
- Self-model: autobiographical memory + personality traits + body model
  - Episodic memory: estimates of ~10^9 distinct memories, each ~10^3-10^4 parameters = ~10^12-10^13 parameters (~4-40 TB at 4 bytes each)
  - Semantic knowledge: ~10^9 concepts x ~10^3 associations = ~10^12 parameters (~4 TB)
- Total functional model: **~10^12-10^13 parameters = 1-10 TB**

**Could this be a subset of a full brain scan?**
- Yes. AST suggests you need:
  - Prefrontal attention control circuits: ~2-4 billion neurons
  - Parietal attention maps: ~1-2 billion neurons
  - Sensory representations being attended: variable
  - Memory systems (hippocampus, medial temporal lobe): ~1 billion neurons
  - Self-model circuits: medial PFC, TPJ, precuneus: ~1-2 billion neurons
- Total: ~5-10 billion neurons, ~5-10% of the brain
- Resolution: regional connectivity at ~1 um may suffice (not synaptic-level)

**Scanning Resolution:**
- Regional connectivity mapping: ~1 um (diffusion MRI or expansion microscopy)
- Key circuits (PFC, parietal): ~100 nm - 1 um
- Memory engrams: unclear resolution needed; potentially extractable from functional imaging

**FLOPS:**
- If modeled as a neural network with 10^13 parameters: ~10^15-10^16 FLOPS (comparable to current large AI models)
- Full neural simulation of 10B neurons at spiking level: ~10^17-10^18 FLOPS
- Range: **10^15 - 10^18 FLOPS**

**Sources:**
- Graziano, "Consciousness and the Social Brain" (2013)
- Graziano, "The Attention Schema Theory: A Foundation for Engineering Artificial Consciousness," Frontiers in Robotics and AI (2017): [Frontiers](https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2017.00060/full)
- Webb et al., "The attention schema theory in a neural network agent," PNAS (2021)

---

## BCI Bandwidth Requirements for Gradual Replacement

For gradual (non-destructive) consciousness transfer, each theory implies a required rate of neuron read/write at sufficient fidelity to maintain continuity.

### Current BCI State of the Art (2025)

| System | Electrodes | Raw Bandwidth | Effective Neural Read | Write Capability |
|--------|-----------|---------------|----------------------|------------------|
| Neuralink N1 | 1,024 | 200 Mbps raw | ~1,024 neurons @ 20 kHz | Stimulation only (not synaptic-level write) |
| Paradromics | 65,000+ | 30 Gbps | ~65,000 neurons | Read only |
| Utah Array | 128 | ~10 Mbps | ~128 neurons | Limited stimulation |

**Key limitation:** Current BCIs read ~10^3-10^5 neurons. The brain has 86 x 10^9 neurons. The gap is **6-8 orders of magnitude** in channel count alone, and current BCIs cannot write at synaptic resolution.

### Required BCI Bandwidth Per Theory

| Theory | Neurons to Replace | Read Fidelity | Write Fidelity | Required Bandwidth | Time at 10^5 neurons/s | Time at 10^9 neurons/s |
|--------|-------------------|---------------|----------------|-------------------|----------------------|----------------------|
| **IIT 4.0** | 86 x 10^9 (all, simultaneously) | Full causal state | Full causal state | N/A (must be simultaneous) | Infeasible | Infeasible |
| **GNWT** | 86 x 10^9 | Spike timing + weights | Synapse-level | ~10^7 neurons/s @ 10 kHz per neuron = 10^11 samples/s | 860,000 s (~10 days) | 86 s |
| **HOT** | ~10 x 10^9 | Spike timing + weights (PFC+sensory) | Synapse-level (PFC) | ~10^6 neurons/s @ 10 kHz = 10^10 samples/s | 100,000 s (~28 hrs) | 10 s |
| **Pred. Processing** | 86 x 10^9 | Spikes + neuromodulatory | Spikes + precision | ~10^7 neurons/s @ 1 kHz = 10^10 samples/s | 860,000 s (~10 days) | 86 s |
| **RPT** | ~20 x 10^9 (sensory cortices) | Spikes @ 100 kHz | Spikes @ 100 kHz | ~10^7 neurons/s @ 100 kHz = 10^12 samples/s | 200,000 s (~2 days) | 20 s |
| **Bio. Comp.** | 86 x 10^9 + 170 x 10^9 glial | Molecular state | Molecular state | ~10^8 cells/s @ molecular fidelity | Infeasible | ~2,560 s (~43 min) |
| **Orch OR** | 86 x 10^9 (quantum states) | Quantum state (impossible) | Quantum state (impossible) | N/A (no-cloning) | Impossible | Impossible |
| **AST** | ~5-10 x 10^9 | Regional activity + memories | Circuit-level | ~10^5 neurons/s @ 1 kHz = 10^8 samples/s | 50,000-100,000 s (~14-28 hrs) | 5-10 s |

### Scaling Gap Analysis

| Theory | Current Best (neurons) | Required (neurons/s) | Gap (orders of magnitude) | Years to Close (at ~10x/decade BCI scaling) |
|--------|----------------------|---------------------|---------------------------|---------------------------------------------|
| **IIT 4.0** | 10^5 | N/A (simultaneous) | Undefined | Never (architectural impossibility) |
| **GNWT** | 10^5 | 10^7 | 2 OOM | ~20 years (2045) for read; write unknown |
| **HOT** | 10^5 | 10^6 | 1 OOM | ~10 years (2035) for read; write unknown |
| **Pred. Processing** | 10^5 | 10^7 | 2 OOM | ~20 years (2045) for read; write unknown |
| **RPT** | 10^5 | 10^7 | 2 OOM + 10x temporal | ~25 years (2050) |
| **Bio. Comp.** | 10^5 | 10^8 (molecular) | 3 OOM + fidelity gap | ~40+ years (2065+) |
| **Orch OR** | 10^5 | N/A | Infinite | Never |
| **AST** | 10^5 | 10^5 | 0 OOM (channel count) | ~5-10 years for read (2030-2035); write is bottleneck |

**Note on write capability:** All gradual replacement estimates assume bidirectional read/write at the required fidelity. Current BCIs can only write via electrical stimulation (affecting ~10^3-10^4 neurons crudely). Synaptic-level write capability does not exist and has no clear development pathway. This is the dominant bottleneck for all theories except Orch OR (which is blocked by physics).

---

## Cross-Cutting Observations

### Orders of Magnitude Summary (vs current capability)

| Requirement | Current State | AST | HOT | GNWT/RPT/PP | Bio. Comp. | IIT 4.0 | Orch OR |
|-------------|--------------|-----|-----|-------------|------------|---------|---------|
| Scanning resolution | ~6 nm (EM, small volumes) | ~1 um (exists) | ~10 nm (exists, not at scale) | ~10 nm (exists, not at scale) | ~1 nm (cryo-EM, not at brain scale) | ~5 nm (not at scale) | Sub-nm quantum (impossible) |
| Volume scanned | 1 mm^3 | ~10 cm^3 | ~200 cm^3 | ~1,260 cm^3 | ~1,260 cm^3 | ~1,260 cm^3 | ~1,260 cm^3 |
| Volume gap | - | 10^2x | 10^5x | 10^6x | 10^6x | 10^6x | N/A |
| Storage | 1.4 PB for 1 mm^3 | 1-10 TB | ~500 TB | ~2 PB | ~100+ PB | ~100 EB | N/A |
| Compute (available) | ~10^18 (Frontier, 2023) | 10^15-18 (achievable) | 10^17-20 | 10^18-22 | 10^25 | 10^22+ (sim only) | 2^(10^18) |
| Compute gap | - | 0 OOM | 0-2 OOM | 0-4 OOM | 7 OOM | 4+ OOM | Infinite |

### Key Takeaways

1. **AST is the most tractable theory** for consciousness preservation engineering, requiring 3-6 orders of magnitude less data and compute than connectome-level theories.

2. **GNWT, RPT, HOT, and Predictive Processing** cluster together in requirements, all needing synapse-level connectomics and 10^18-10^22 FLOPS. The main differentiator is whether the full brain or a subset is needed (HOT wins here).

3. **Biological Computationalism** adds ~3 orders of magnitude in data and compute over connectome-level theories due to molecular state capture.

4. **IIT 4.0's verification problem** (computing Phi) is formally intractable regardless of scanning or compute advances. Simulation is feasible at the electrophysiology level, but you could never verify the emulation preserves integrated information.

5. **Orch OR is ruled out** by the no-cloning theorem under known physics. If quantum states of microtubules are genuinely required for consciousness, non-destructive consciousness preservation is physically impossible.

6. **The dominant bottleneck** across all theories is not compute or storage (which follow Moore's Law variants) but scanning at scale (whole-brain EM) and BCI write capability (which has no clear scaling law).

---

## Methodology Notes

- Neuron count: 86 billion (Azevedo et al., 2009)
- Synapse count: 100-500 trillion; we use 10^14 as conservative estimate
- Glial cell count: ~85-170 billion (Azevedo et al., 2009; von Bartheld et al., 2016)
- FLOPS estimates: Sandberg & Bostrom (2008) for spiking (10^18), electrophysiology (10^22), metabolome (10^25)
- Scanning data: Google/Harvard 2024 (1.4 PB per mm^3 at nanoscale EM)
- Current supercomputer: Frontier ~1.2 x 10^18 FLOPS (2023)
- Current BCI: Neuralink N1 (1,024 channels, 200 Mbps), Paradromics (65,000 channels, 30 Gbps)
- Estimates marked as derived show the calculation; estimates from literature cite the source
- "Feasibility timeline" assumes continued exponential scaling in compute (~10x/decade), scanning throughput (~10x/5 years for EM), and BCI channel count (~10x/decade)
