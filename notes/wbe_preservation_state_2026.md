# Whole Brain Emulation & Brain Preservation: State of the Field (March 2026)

Research compiled March 27, 2026. Sources cited inline.

---

## 1. Connectomics Progress

### Completed Connectomes

**C. elegans** (302 neurons): The original connectome, first mapped by White et al. in 1986, has been refined multiple times. Still the only organism where we have a complete wiring diagram AND functional recordings of a substantial fraction of neurons simultaneously (~50% of nervous system neurons at single-cell resolution).

**Drosophila melanogaster** (139,255 neurons, ~50 million synapses): The FlyWire consortium published the first complete adult fruit fly brain connectome in October 2024 as a nine-paper package in Nature. This was a 10+ year effort by 146 labs at 122 institutions. Key stats:
- 8,453 cell types identified, 4,581 newly discovered
- AI did the heavy lifting; without it, the project would have taken ~50,000 person-years
- Since 2019, human proofreaders contributed 33 person-years of corrections to AI segmentations
- The connectome is publicly available at [flywire.ai](https://flywire.ai/)

This is the largest complete connectome of any adult animal to date. Three orders of magnitude more neurons than C. elegans.

### Mammalian Connectomics (Partial)

**MICrONS — Mouse Visual Cortex** (1 mm³, ~200,000 cells, 0.5 billion synapses): The MICrONS (Machine Intelligence from Cortical Networks) project published its flagship paper in Nature in April 2025. Led by the Allen Institute, Baylor College of Medicine, and Princeton, it combined:
- Dense calcium imaging of ~75,000 neurons in awake mouse viewing visual stimuli
- Electron microscopy reconstruction of the same tissue: 200,000+ cells, 0.5 billion synapses, 4 km of axons
- First dataset to combine functional recordings with synaptic-resolution structural data at this scale
- Key finding: neurons with similar response properties preferentially connect, within and across brain areas

Data publicly available at [microns-explorer.org](https://www.microns-explorer.org/).

**Google/Harvard Human Cortex Fragment** (1 mm³, 57,000 cells, 150 million synapses): Published in Science, May 2024 ("A petavoxel fragment of human cerebral cortex reconstructed at nanoscale resolution"). Key details:
- Tissue from temporal cortex of an epilepsy patient (half the size of a rice grain)
- 1,400 terabytes of imaging data
- 230 mm of blood vessels mapped
- Revealed never-before-seen structures: rare axons connected by up to 50 synapses (typical is 1), mysterious axonal whorls (unknown if pathological or normal variation)
- Interactive viewer accessed 100,000+ times
- Ten years of neuroscience work at Google

**What it revealed**: The sheer complexity was staggering — and this is 1/1,000,000th of a human brain. The finding of multi-synaptic connections challenges simple models of neural connectivity. The unknown whorled structures remind us how much basic neuroanatomy we still don't understand.

### Zebrafish (Emerging Complete Connectome)

Larval zebrafish (~100,000 neurons) is the next target for a complete vertebrate connectome. In 2025:
- A correlated light-and-EM dataset captured 180,000+ segmented soma, 40,000+ molecularly annotated neurons, and 30 million synapses in a 7-day-old larval zebrafish
- Google's ZAPBench (ICLR 2025): whole-brain recording of ~70,000 neurons with a connectome being generated from the same specimen — first time structure AND function will be available for an entire vertebrate brain
- Full connectome expected ready in 2026

### What's Next

- **Whole mouse brain connectome**: E11 Bio estimates this is achievable in ~5 years for ~$100M using their PRISM technology (barcoding + expansion microscopy). Without new tech, it would cost more than the Human Genome Project. A Wellcome Trust report suggests a 10-15 year timeline.
- **Nature Methods named EM-based connectomics "Method of the Year 2025"**
- The field has "outpaced Moore's law" — volumes accessible at synaptic resolution have increased 1,000x over 20 years

---

## 2. Scanning Technology

### Electron Microscopy (EM)

Still the gold standard for synaptic-resolution connectomics (10-20 nm resolution). Current systems:

- **Serial section EM (ssEM)**: The workhorse. Tissue is sliced into ~30-40 nm sections, each imaged. Used for Google/Harvard human fragment and FlyWire.
- **Focused Ion Beam SEM (FIB-SEM)**: Higher z-resolution (~8 nm isotropic) but slower. Used by Janelia/HHMI for smaller volumes.
- **FAST-EM**: Uses 64 parallel electron beams. Dwell times as short as 400 ns with good signal-to-noise. Significant speed improvement.
- **SmartEM** (2025): AI-guided acquisition — scans quickly first, then rescans critical areas at higher resolution. Up to 7x speedup without sacrificing accuracy.

### Expansion Microscopy (ExM)

Physically swells tissue 4-20x, allowing standard light microscopes to achieve effective resolutions of ~60 nm. Key 2024-2025 advances:

- **Ultrastructural membrane ExM (umExM)**: Can now visualize cell membranes, previously very difficult to label in intact tissue
- **Multiplexed protein imaging**: Iteratively label, image, strip, re-label — reveals many different proteins in a single sample at sub-diffraction resolution
- **ExA-SPIM**: Images native volumes of 67x17x12 mm³ at ~0.5 μm resolution without physical sectioning. Over 100 teravoxels per scan.

### LICONN (Light-Microscopy-Based Connectomics)

Published in Nature 2025 by Danzl, Tavakoli, Lyudchik et al. (ISTA) with Google Research. **First technology beyond EM capable of synapse-level connectomic reconstruction.** Combines:
- Engineered hydrogel embedding + expansion
- Deep-learning-based segmentation
- Direct molecular information at each synapse (neurotransmitter type, pre/post distinction)
- Multimodal: structure + molecular identity simultaneously

This is potentially transformative — EM gives you structure but not molecular identity. LICONN gives you both at synapse resolution using light microscopy.

### E11 Bio's PRISM

Protein-barcode Reconstruction by Iterative Staining with Molecular annotations. Each cell expresses a unique combination of barcode proteins, combined with expansion microscopy. Claims potential for 100x cost reduction in whole-brain connectomics.

### The Bottlenecks

1. **Human proofreading**: >95% of total project costs. AI segmentation is good but not perfect. This is the dominant bottleneck.
2. **Scanning speed**: EM throughput defines project size. Datasets take weeks to years. FAST-EM and SmartEM are helping.
3. **Data storage**: Connectomic volumes are at petabyte scale. A whole mouse brain would be exascale. Data transfer is becoming a limiting factor.
4. **Analysis**: Raw images must be segmented, proofread, synapse-detected, and annotated. The computational pipeline is massive.

---

## 3. Simulation and Emulation

### C. elegans Simulations

**OpenWorm**: Long-running open-source project. Has produced basic locomotion in a simulated worm body. Still not a complete, validated emulation — many simplifications.

**BAAIWorm** (Nature Computational Science, December 2024): Builds on OpenWorm's data but achieves more biophysically detailed neural model. Replicates the characteristic zigzag movement. Integrates brain, body, and environment in a closed loop.

**Other platforms**: NeuroSimWorm, Digital Twin, Worminator, Sim-CE — the C. elegans simulation ecosystem has grown substantially. Multiple independent groups can now run closed-loop simulations reproducing specific behaviors.

Despite having a complete connectome since 1986, C. elegans emulation is STILL not fully solved — highlighting that the connectome alone is not sufficient.

### Drosophila Simulations

**Eon Systems** (2024): Demonstrated the world's first embodied whole-brain emulation. Built a leaky integrate-and-fire (LIF) model from the FlyWire connectome (~140,000 neurons, ~50 million synapses) with inferred neurotransmitter identities. Embedded in a NeuroMechFly v2 body simulation (MuJoCo physics, 87 independent joints from X-ray microtomography scan). Claimed 95% accuracy predicting motor behavior. Their stated roadmap: fly → mouse (70M neurons) → human.

**Key caveat**: LIF is the simplest possible neuron model. Real neurons have complex dendritic computation, neuromodulation, etc. The 95% accuracy claim is for specific motor behaviors, not general cognition.

**Lappalainen et al. and Shiu et al.** (Nature, 2024): Two independent papers demonstrating large-scale efforts to reconstruct and simulate functional components of the fly brain. Signals a shift from "map it" to "run it."

### Blue Brain Project

Ran from 2005 to end of 2024 at EPFL. Transitioned to an independent not-for-profit foundation in 2025. Achievements:
- ~300 publications, 1 petabyte of data
- 260+ public repositories
- 5,000+ reconstructed morphologies, 100k+ electrophysiological recordings
- Detailed model of thalamic microcircuit: 14,000 neurons, 6 million synapses
- Mouse cortex model completed (computationally) in 2019
- Key limitation: models became "too heavy" for available supercomputers

### Compute Requirements (from State of Brain Emulation Report 2025)

Using the simplest possible neuron model (point neuron, leaky integrate-and-fire):
- **Mouse brain** (~70 million neurons): ~20 GPUs
- **Human brain** (~86 billion neurons): ~20,000 GPUs

But this is deeply misleading. These are for the simplest model. Real neurons are not point processes. And the primary bottleneck for mammalian-scale simulations is **memory capacity and interconnect bandwidth**, not raw compute — GPUs spend most of their time moving data, not computing.

For biophysically detailed multi-compartment models (what Blue Brain was doing), requirements are orders of magnitude higher.

**Timeline estimates** (from technological trend analysis):
- Mouse whole-brain simulation (cellular level): ~2034
- Marmoset: ~2044
- Human: likely post-2044

---

## 4. Brain Preservation

### Aldehyde-Stabilized Cryopreservation (ASC)

Developed by 21st Century Medicine (Robert McIntyre, Greg Fahy). Published 2015. The technique:
1. Perfuse glutaraldehyde (chemical fixative) through brain vasculature — crosslinks all proteins in place
2. Perfuse sodium dodecyl sulfate (BBB modifier)
3. Perfuse ethylene glycol cryoprotectant to 65% w/v
4. Vitrify at -135°C for indefinite storage

**Results**: Won both Brain Preservation Foundation prizes — Small Mammal (Feb 2016) and Large Mammal (March 2018). Preservation was "uniformly excellent" — neuronal processes easily traceable, synapses crisp. The connectome appears fully preserved at EM-visible resolution.

**Critical limitation**: ASC is a one-way trip. Glutaraldehyde crosslinks proteins irreversibly. The brain is dead — fixed like a histology sample. You're preserving the structure for future scanning, not for revival. This is by design: the goal is information preservation, not biological reversibility.

**Human application**: Has NOT been demonstrated to this quality level in a human brain. The BPF does not endorse offering ASC to patients. No company currently offers ASC-based preservation to humans.

### Vitrification (Reversible Approach)

**Cradle (formerly Cradle Health)**: Founded by Laura Deming with $48M in funding. Goal: reversible whole-body cryopreservation.
- February 2024: Recovered electrical activity in cryopreserved and rewarmed rat brain cerebellar slices using VMPnoX cryoprotectant
- Published in PNAS 2025: "Functional recovery of the adult murine hippocampus after cryopreservation by vitrification"
- Next steps: demonstrate preserved synaptic function, long-term potentiation, then whole organ, then whole organism

**State of the art for organs**: As of September 2025, a rat kidney has been cryopreserved, rewarmed, and transplanted with virtually no functional damage. No larger organ has been functionally rewarmed and transplanted. Key remaining challenges: cryoprotectant toxicity, irreversible damage during thawing/rewarming.

### Brain Preservation Foundation

Founded by Kenneth Hayworth (neuroscientist, Janelia/HHMI). Both technology prizes now awarded. The Foundation acknowledges that future prizes may target features beyond what's currently observable by FIB-SEM — the "synaptome" and "epigenome" may need preservation too. This is a tacit admission that we don't yet know if what ASC preserves is sufficient.

### The 2024 Frontiers Paper

"Structural brain preservation: a potential bridge to future medical technologies" (Frontiers in Medical Technology, 2024). Argues that structural preservation via ASC-like methods could preserve enough information for future reconstruction, positioning it as a medical procedure rather than speculative cryonics. This represents a shift toward mainstream scientific framing.

---

## 5. Cryonics

### Current Providers and Scale

As of mid-2025, ~500-650 individuals cryopreserved globally. Annual preservations: 30-40.

| Provider | Patients | Members | Location |
|----------|----------|---------|----------|
| Alcor | 248 | 1,500+ | Scottsdale, AZ |
| Cryonics Institute | 250+ | ~2,000 | Clinton Township, MI |
| KrioRus | 103 | — | Moscow (status uncertain post-2022) |
| Tomorrow Bio | 20 humans, 10 pets | 800+ | Berlin, Germany |
| Shandong Yinfeng | 29 | — | Jinan, China |
| Southern Cryonics | 4 | — | Australia |

### New Entrants and Growth

**Tomorrow Bio**: Fastest-growing cryonics organization. ~400 new members in 2024. Raised €5M seed in 2025 for US expansion (NY, CA, FL). Offers a €50/month subscription model. Total contract value claimed >€160M.

**Cradle**: Not a storage provider but a research company. $48M funding, focused on developing reversible cryopreservation technology. If they succeed, it transforms the field from "speculative long-term storage" to "medical procedure."

**Alcor developments (2024)**: Established first full-time in-house R&D department. Dr. Nick Llewellyn hired as Director of R&D. Eight new team members. Response times at new lows. Working on intermediate temperature storage (ITS) and field cryopreservation protocols.

### What the Science Actually Says

**For information preservation**: The evidence is mixed and depends heavily on protocol quality.
- ASC demonstrably preserves connectome-level structure (won BPF prizes)
- Standard cryonics (Alcor/CI) uses vitrification without prior fixation — structural preservation is less validated at the synaptic level
- Ice crystal formation during imperfect vitrification can destroy fine structure
- Ischemic delay before preservation (often hours) causes significant degradation
- No experiment has demonstrated that cryopreserved mammalian brain tissue retains enough information to reconstruct the original neural computation

**For revival**: No whole mammalian brain has been revived from cryopreservation. Cradle's 2024-2025 results (electrical activity recovery in rat brain slices) are the closest evidence, but this is tissue slices, not whole brains, and "electrical activity" is not "functional neural computation."

**The honest assessment**: Cryonics is a bet that (a) the information is preserved, (b) future technology can extract it, and (c) future society will bother. The scientific case for (a) is strongest with ASC-like protocols, weakest with standard cryonics after long ischemic delays.

---

## 6. The Fidelity Question

This is the crux of the entire enterprise: what do you actually need to capture?

### Level 1: Connectome Only (Network Topology)

What: Which neurons connect to which, at what synapses.
Resolution needed: ~10-20 nm (EM resolution).
Status: Achievable now for small brains, approaching for mouse.

**Problem**: C. elegans has had a complete connectome since 1986. We STILL cannot fully predict its behavior from the connectome alone. The worm uses the same 302 neurons for radically different behaviors depending on neuromodulatory state. The connectome is necessary but not sufficient.

### Level 2: Connectome + Synaptic Weights

What: Connection topology PLUS the strength/sign of each synapse.
Resolution needed: EM + molecular markers or functional inference.
Status: Partially achievable. LICONN can distinguish excitatory vs. inhibitory. Calcium imaging can give functional correlates. But absolute synaptic weights are not directly measurable at scale.

**Problem**: Synaptic weights change constantly (synaptic plasticity is how learning works). A snapshot may not capture the functionally relevant state. Also, many synapses have complex short-term dynamics (facilitation, depression) not captured by a single weight.

### Level 3: Molecular State

What: Receptor densities, ion channel distributions, intracellular signaling cascades, gene expression state of each neuron.
Resolution needed: Single-cell transcriptomics + proteomics + EM.
Status: Single-cell RNA sequencing can profile gene expression. Spatial transcriptomics is improving. But comprehensive molecular profiling at the scale of a whole brain is not yet feasible.

**Problem**: This is an enormous amount of information. A single neuron expresses thousands of genes, has dozens of receptor types at different densities across its dendritic tree. Whether all of this matters depends on your theory of what computation the brain is doing.

### Level 4: Full Biophysical State

What: Every molecule's position, every ion concentration, every membrane potential at a given instant.
Resolution needed: Essentially atomic.
Status: Physically impossible to capture for a whole brain with foreseeable technology.

### What Theories of Consciousness Imply

**Global Neuronal Workspace Theory (GNWT)**: Consciousness = broadcast of information to a "global workspace" of interconnected cortical areas. Implies Level 1-2 might suffice — you need the network structure and approximate functional properties, but the specific molecular details may be less critical. The key is the architecture of information flow.

**Integrated Information Theory (IIT)**: Consciousness = integrated information (Φ) in a system with appropriate causal structure. IIT has a surprising and controversial implication for WBE: **a digital simulation of a brain may be intelligent but NOT conscious**, because IIT requires specific causal structure (not just functional equivalence). A feed-forward simulation on a von Neumann architecture would have different Φ than the biological original, even if it produces identical outputs.

The adversarial collaboration results (Nature, April 2025) found that 2/3 of IIT's predictions passed pre-registered thresholds, while 0/3 of GNWT's did — giving IIT a slight empirical edge, though the results are far from conclusive.

**Predictive Processing / Free Energy Principle**: Consciousness relates to a system's model of itself and its predictions about sensory input. Implies Level 2-3 fidelity — you need functional dynamics, not just structure.

**The uncomfortable truth**: We don't have a validated theory of consciousness. Without one, we cannot definitively answer the fidelity question. This is not a mere gap in neuroscience — it may be the hardest problem in all of science.

---

## 7. Key Papers and Breakthroughs (2023-2026)

### 2024

1. **FlyWire Consortium** — "Neuronal wiring diagram of an adult brain" (Nature, Oct 2024). Complete adult Drosophila connectome. Nine companion papers. The single biggest milestone in connectomics history by neuron count.

2. **Shapson-Coe, Januszewski et al.** — "A petavoxel fragment of human cerebral cortex reconstructed at nanoscale resolution" (Science, May 2024). Google/Harvard 1 mm³ human cortex. 57,000 cells, 150M synapses, 1.4 PB data.

3. **Eon Systems** — First embodied whole-brain emulation (Drosophila). LIF model from FlyWire connectome controlling a physics-simulated body. Proof of concept that connectome-derived models can produce realistic behavior.

4. **BAAIWorm** — Integrative data-driven C. elegans model (Nature Computational Science, Dec 2024). Most biophysically detailed worm simulation to date.

5. **Cradle Health** — First recovery of electrical activity in vitrified mammalian brain tissue (preprint 2024, PNAS 2025).

### 2025

6. **MICrONS Consortium** — "Functional connectomics spanning multiple areas of mouse visual cortex" (Nature, April 2025). 1 mm³ mouse cortex, 200k cells, 0.5B synapses, combined with functional recordings of 75k neurons. The largest combined structure-function dataset in any mammal.

7. **LICONN** — "Light-microscopy-based connectomic reconstruction of mammalian brain tissue" (Nature, 2025). First non-EM method achieving synapse-level connectomics, with simultaneous molecular information.

8. **State of Brain Emulation Report 2025** (Zanichelli, Schons, Freeman et al., arXiv). 175-page comprehensive assessment with 45+ expert contributors. The most thorough status update since Sandberg & Bostrom 2008.

9. **SmartEM** — AI-guided electron microscopy (Nature Methods, 2025). 7x speedup in connectomic imaging.

10. **IIT vs. GNWT adversarial collaboration results** (Nature, April 2025). First rigorous empirical test between leading consciousness theories.

11. **Nature Methods names EM-based connectomics "Method of the Year 2025"**

12. **ZAPBench / Zebrafish connectome** — Google/Janelia/Harvard whole-brain activity dataset + connectome for same individual larval zebrafish. First vertebrate with both. Full connectome expected 2026.

### 2026

13. **Larval zebrafish full connectome** — Expected to complete in 2026, creating the first complete vertebrate brain connectome.

---

## 8. Timeline Estimates

### Near-term (2026-2030)

- **Complete larval zebrafish connectome**: 2026 (in progress)
- **Validated whole-brain emulation of C. elegans**: Possible but not guaranteed — multiple groups converging
- **Functional fly brain emulation** (beyond simple motor behavior): 2027-2030
- **Mouse visual system connectome** (beyond MICrONS 1 mm³): Ongoing expansion

### Medium-term (2030-2040)

- **Whole mouse brain connectome**: ~2030-2035 (E11 Bio: 5 years from ~2025; Wellcome Trust: 10-15 years; community estimate varies)
- **Mouse brain cellular-level simulation**: ~2034 (technology trend projection)
- **Reversible whole-organ cryopreservation**: Possible if Cradle's approach scales
- **Human brain connectomics**: Larger fragments, but whole-brain remains distant

### Long-term (2040+)

- **Marmoset whole-brain simulation**: ~2044
- **Human whole-brain simulation**: Post-2044, likely post-2050
- **Human-scale WBE**: No credible estimate puts this before mid-century at the earliest

### Expert Consensus

From the State of Brain Emulation Report 2025:
- The field has shifted from "is this possible?" to "how quickly can we converge on methods that work?"
- But community estimates give only ~1% chance that mind uploading happens before AGI
- The critical gap is between our ability to reconstruct structure (improving fast) and our ability to record/infer function (improving slowly)
- We need better methods to infer functional properties from structural and molecular data
- No experiment has achieved whole-brain recording (>95% of neurons, >95% of volume, single-spike resolution) in ANY organism during ANY behavior

### The Honest Bottom Line

We are in a golden age of connectomics. The structural mapping problem is being solved faster than anyone predicted a decade ago. But:

1. **Structure ≠ function**: Having the wiring diagram doesn't mean you can run it. C. elegans proves this.
2. **The fidelity question is unanswered**: We don't know what resolution is "enough" because we don't understand consciousness.
3. **Compute is not the bottleneck people think**: For simple models, a mouse brain fits on 20 GPUs today. The problem is that simple models are wrong. Biophysically accurate models are orders of magnitude more expensive.
4. **Brain preservation works for structure**: ASC preserves connectome-level detail. But we don't know if that's sufficient.
5. **Cryonics remains a Pascal's Wager**: The information-theoretic argument is sound — if the structure is preserved, the information exists. But "the information exists" and "we can extract and use it" are very different claims.
6. **The timeline for human WBE is measured in decades, not years**: Even optimistic estimates don't put it before 2050. Pessimistic ones say never, on philosophical grounds (consciousness might require biological substrate, per IIT).

The most productive near-term path: focus on model organisms (zebrafish, fly, mouse), develop better structure-to-function inference methods, and settle the theoretical question of what fidelity is required. The field needs a validated theory of consciousness as much as it needs better microscopes.

---

## Key Researchers and Institutions

- **Viren Jain** (Google Research) — connectomics, led Google/Harvard cortex mapping, LICONN collaboration
- **Jeff Lichtman** (Harvard) — connectomics, Google/Harvard cortex mapping
- **Sebastian Seung** (Princeton) — FlyWire, MICrONS, EyeWire
- **Moritz Helmstaedter** (Max Planck) — connectomics scaling, SmartEM
- **Philip Shiu** (Eon Systems) — embodied fly brain emulation
- **Robert McIntyre** (21st Century Medicine / Nectome) — ASC
- **Laura Deming** (Cradle) — reversible cryopreservation
- **Kenneth Hayworth** (Brain Preservation Foundation) — brain preservation advocacy/standards
- **Henry Markram** (EPFL) — Blue Brain Project
- **Johann Danzl** (ISTA) — LICONN
- **Giulio Tononi** (U. Wisconsin) — Integrated Information Theory
- **Stanislas Dehaene** (College de France) — Global Neuronal Workspace Theory
- **Randal Koene** (Carboncopies Foundation) — WBE roadmapping
- **Maximilian Schons** — State of Brain Emulation Report 2025

## Key Institutions

- Allen Institute for Brain Science (MICrONS, mouse brain atlas)
- Google Research (connectomics pipelines, LICONN, ZAPBench)
- HHMI Janelia Research Campus (FIB-SEM, zebrafish, fly connectomics)
- Princeton Neuroscience Institute (FlyWire, MICrONS)
- MRC Laboratory of Molecular Biology, Cambridge (fly connectomics)
- EPFL Blue Brain Project (neural simulation)
- E11 Bio (PRISM, scalable connectomics)
- Eon Systems (embodied brain emulation)
- Carboncopies Foundation (WBE coordination/reports)
- Brain Preservation Foundation (preservation standards)
- Cradle (reversible cryopreservation R&D)

---

## Sources

- [Harvard Gazette: The brain as we've never seen it](https://news.harvard.edu/gazette/story/2024/05/the-brain-as-weve-never-seen-it/)
- [Google Research: Ten years of neuroscience at Google](https://research.google/blog/ten-years-of-neuroscience-at-google-yields-maps-of-human-brain/)
- [Princeton: Mapping an entire fly brain](https://www.princeton.edu/news/2024/10/02/mapping-entire-fly-brain-step-toward-understanding-diseases-human-brain)
- [FlyWire connectome collection (Nature)](https://www.nature.com/collections/hgcfafejia)
- [Allen Institute: MICrONS](https://alleninstitute.org/news/revealing-the-largest-wiring-diagram-and-functional-map-of-the-brain-through-microns/)
- [MICrONS: Functional connectomics (Nature 2025)](https://www.nature.com/articles/s41586-025-08790-w)
- [Nature Methods: Method of the Year 2025 — EM connectomics](https://www.nature.com/articles/s41592-025-02988-6)
- [LICONN: Light-microscopy connectomics (Nature 2025)](https://www.nature.com/articles/s41586-025-08985-1)
- [State of Brain Emulation Report 2025 (arXiv)](https://arxiv.org/abs/2510.15745)
- [State of Brain Emulation Report 2025 (overview site)](https://brainemulation.mxschons.com/)
- [E11 Bio Roadmap](https://www.e11.bio/blog/roadmap)
- [Eon Systems: Embodied brain emulation](https://eon.systems/updates/embodied-brain-emulation)
- [BAAIWorm (Nature Computational Science 2024)](https://www.nature.com/articles/s43588-024-00738-w)
- [Blue Brain Project](https://bluebrain.epfl.ch/)
- [Brain Preservation Foundation](https://www.brainpreservation.org/)
- [ASC original paper (PubMed)](https://pubmed.ncbi.nlm.nih.gov/26408851/)
- [Structural brain preservation (Frontiers 2024)](https://www.frontiersin.org/journals/medical-technology/articles/10.3389/fmedt.2024.1400615/full)
- [Cradle: Functional recovery after vitrification (PNAS 2025)](https://www.pnas.org/doi/10.1073/pnas.2516848123)
- [Cradle emerges with $48M](https://longevity.technology/news/cradle-emerges-with-48m-to-build-reversible-cryonics-technology/)
- [Tomorrow Bio US expansion](https://www.eu-startups.com/2025/05/cryo-now-heal-later-europes-first-cryonics-lab-tomorrow-bio-eyes-u-s-expansion-with-e5-million-in-fresh-funding/)
- [Who Funds Cryo? 2025 Money Map](https://www.regeneration.ai/p/who-funds-cryo-the-2025-money-map)
- [IIT vs GNWT adversarial collaboration (Nature 2025)](https://www.nature.com/articles/s41586-025-08888-1)
- [Synaptic-resolution connectomics review (Nature Reviews Neuroscience 2025)](https://www.nature.com/articles/s41583-025-00998-z)
- [Comparative imaging methods for mammalian connectomics (Cell Reports Methods 2025)](https://www.cell.com/cell-reports-methods/fulltext/S2667-2375(25)00024-4)
- [Future projections for mammalian whole-brain simulations (ScienceDirect 2024)](https://www.sciencedirect.com/science/article/pii/S016801022400138X)
- [SmartEM: AI-guided EM (Nature Methods 2025)](https://www.nature.com/articles/s41592-025-02930-w)
- [ZAPBench / Zebrafish (Google Research)](https://research.google/blog/improving-brain-models-with-zapbench/)
- [Zebrafish connectomic resource (bioRxiv 2025)](https://www.biorxiv.org/content/10.1101/2025.06.10.658982v1)
- [Berkeley News: Fly brain on a laptop](https://news.berkeley.edu/2024/10/02/researchers-simulate-an-entire-fly-brain-on-a-laptop-is-a-human-brain-next/)
- [MIT News: Expansion microscopy advances](https://news.mit.edu/2025/seeing-more-expansion-microscopy-0303)
- [Alcor R&D](https://www.alcor.org/research-development/)
- [Carboncopies Foundation](https://carboncopies.org/)
