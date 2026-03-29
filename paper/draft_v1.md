# What Must Be Preserved? Mapping Theories of Consciousness to Engineering Requirements for Mind Preservation

**Authors:** [Name Redacted]

**Date:** March 2026

**Preprint — not yet peer reviewed**

---

## Abstract

The engineering of consciousness preservation — whether through whole-brain emulation, cryonic revival, or brain-computer interfaces — proceeds largely without reference to theories of consciousness. This is a remarkable omission. The choice of what must be preserved in a brain depends entirely on what generates consciousness, and the major theories disagree on this question by many orders of magnitude in their engineering implications. We evaluate eight empirically active theories of consciousness — Integrated Information Theory (IIT 4.0), Global Neuronal Workspace Theory (GNWT), Higher-Order Thought theory (HOT), Predictive Processing / Free Energy Principle, Recurrent Processing Theory (RPT), Biological Computationalism, Orchestrated Objective Reduction (Orch OR), and Attention Schema Theory (AST) — against nine preservation-relevant criteria, and derive specific engineering requirements from each theory's core postulates. We find that the theories split 4-3-1 on substrate independence, the single most consequential question for preservation. Required information content ranges from approximately 1-10 TB under AST to physically impossible under Orch OR. Required compute spans from 10^15 FLOPS (achievable today) to formally uncomputable. Despite these disagreements, all eight theories converge on three requirements: temporal dynamics must be preserved, integration across components is necessary, and feedforward-only architectures are ruled out. Cross-theory risk analysis reveals that gradual biological replacement is the only preservation strategy that no theory definitively excludes, though it remains technologically distant. We identify a "deflation paradox": theories most favorable to preservation (AST, HOT) are those that deflate consciousness to a functional property, while theories that take phenomenal experience most seriously (IIT, Orch OR) make preservation hardest or impossible. We argue that the primary bottleneck for consciousness preservation is not engineering but theory — resolving which theory of consciousness is correct would collapse the engineering requirements to a tractable problem.

---

## 1. Introduction

Consciousness preservation is an engineering problem with a philosophical dependency. We are building toward whole-brain emulation (Sandberg and Bostrom, 2008), developing brain-computer interfaces with increasing bandwidth (Musk and Neuralink, 2019), and preserving brains through vitrification and aldehyde-stabilized cryopreservation with the explicit hope of future revival or digital reconstruction (McIntyre and Bhatt, 2018). Yet these efforts proceed under an assumption that is rarely made explicit: that we know what must be preserved.

We do not. The question of what constitutes consciousness — and therefore what physical substrate or information pattern must be maintained for a person to continue existing — remains open. More critically, the major theories of consciousness give answers that differ not merely in philosophical nuance but in concrete engineering specifications, spanning many orders of magnitude in required scanning resolution, data volume, and computational power.

Consider a thought experiment. You have access to a perfectly preserved brain and unlimited technology. What do you scan? Under Global Neuronal Workspace Theory (Dehaene et al., 2011), you need the connectome plus synaptic weights plus the dynamics of ignition — roughly 2 PB of processed data at 10 nm scanning resolution. Under Attention Schema Theory (Graziano, 2013), you may need only the attention control circuits and self-model — perhaps 1-10 TB at 1 micrometer resolution. Under Orchestrated Objective Reduction (Penrose and Hameroff, 1996), you need the quantum states of 8.6 x 10^18 tubulin dimers, which the no-cloning theorem renders physically impossible to capture. These are not minor variations. They are the difference between a tractable engineering project and a physical impossibility.

### The Gap in the Literature

Three important bodies of work exist at the intersection of consciousness theory and preservation engineering, but none bridges the gap we address here.

Sandberg and Bostrom (2008) produced the definitive roadmap for whole-brain emulation, establishing the engineering requirements at multiple fidelity levels (spiking models at ~10^18 FLOPS through metabolome-level simulation at ~10^25 FLOPS). Their analysis is thorough on the engineering side but largely agnostic about theory — it presents fidelity levels as options without asking which level consciousness actually requires.

Butlin et al. (2023) systematically mapped theories of consciousness to indicator properties for artificial systems, asking "which AI systems might be conscious?" Their framework is relevant but addresses a different question: they identify theory-specific markers of consciousness in existing systems, not the engineering requirements for preserving an existing consciousness in a new substrate.

Chalmers (2010) argued philosophically for the possibility of mind uploading, primarily from a functionalist framework. His analysis assumes that functional organization is what matters — an assumption that begs the central question, since several major theories reject functionalism.

No existing work does what this paper does: systematically derive specific, quantitative engineering requirements from each major theory's stated postulates, then compare these requirements to identify points of consensus, critical disagreements, and the theory-dependent risks of each preservation strategy.

### Why These Eight Theories

We selected theories that satisfy three criteria: (1) they are empirically active, with ongoing experimental programs designed to test their predictions; (2) they have published formal or semi-formal frameworks that permit derivation of preservation implications; and (3) they make distinct predictions for at least some preservation-relevant questions. This excludes purely philosophical positions (property dualism, panprotopsychism) that lack engineering-relevant specificity, and informal proposals that have not been developed to the point where preservation implications can be derived.

The eight theories span the space of possible answers to the key questions. On substrate independence: four say yes (GNWT, HOT, AST, RPT), three say no (IIT, Biological Computationalism, Orch OR), and one is ambiguous (Predictive Processing). On what must be preserved: they range from abstract computational architecture to full molecular state to quantum coherence. This coverage ensures that our analysis is not biased toward any particular answer.

The remainder of this paper proceeds as follows. Section 2 describes our methods for deriving engineering requirements from theoretical postulates. Section 3 presents the theory-by-theory analysis. Section 4 compares across theories, introducing the engineering bridge table and identifying the key fault lines. Section 5 assesses preservation strategies against the full theory space. Section 6 discusses implications, limitations, and future directions.

---

## 2. Methods

### 2.1 Theory Selection

Theories were selected from those with active empirical research programs as of early 2026. We required each theory to have foundational publications with sufficient formal specificity to derive preservation implications. The COGITATE adversarial collaboration (Melloni et al., 2023; results published in Nature, 2025) tested predictions of IIT and GNWT directly, confirming that both theories generate empirically distinguishable predictions. The remaining theories have empirical programs at various stages of maturity.

### 2.2 Assessment Criteria

Each theory was evaluated on nine criteria chosen to capture the engineering-relevant dimensions of consciousness preservation:

1. **Core ontological claim** — what the theory says consciousness *is*
2. **Substrate independence** — whether the theory permits consciousness on non-biological substrates
3. **Digital emulation viability** — whether a software simulation preserves consciousness
4. **Required information for preservation** — what physical parameters must be captured
5. **Minimum viable identity** — the smallest specification that constitutes "you"
6. **Gradual replacement compatibility** — whether neuron-by-neuron replacement preserves continuity
7. **Scan-and-copy compatibility** — whether destructive scanning followed by digital instantiation preserves the person
8. **Key theoretical weakness** — the most significant empirical or conceptual vulnerability
9. **Overall preservation favorability** — a summary rating from 0 (impossible) to 5 (straightforward)

### 2.3 Derivation of Engineering Requirements

For each theory, we derived engineering requirements through the following procedure. First, we identified the theory's core postulates — the minimal set of claims from which its account of consciousness follows. Second, we asked: what physical parameters must be captured to instantiate or preserve a system satisfying these postulates? Third, we translated these parameters into engineering specifications: scanning resolution, data volume, computational cost, and storage requirements.

Where a theory provides formal specifications (e.g., IIT's transition probability matrices, GNWT's ignition dynamics), the derivation is direct. Where a theory specifies computational requirements without formal detail (e.g., HOT's "higher-order representations"), we extrapolated from the theory's stated neural correlates and the known biophysics of those circuits. All derivations are shown explicitly in Section 3.

Engineering numbers (neuron counts, synapse counts, per-synapse parameter sizes) are drawn from established sources: 86 billion neurons (Azevedo et al., 2009), ~10^14 synapses, ~20 bytes per synapse for Hodgkin-Huxley-level parameterization (Sandberg and Bostrom, 2008), and 1.4 PB per mm^3 for nanoscale electron microscopy data (Shapson-Coe et al., 2024).

### 2.4 Limitations

This approach has three significant limitations. First, theories of consciousness were not designed to answer preservation questions, so some derivations require extrapolation beyond what theorists have explicitly stated. We flag these cases. Second, our engineering estimates inherit substantial uncertainty from neuroscience — the number of functionally distinct synapse types, the role of glial cells, and the relevance of extracellular dynamics are all active research questions. Third, we treat the eight theories as equally plausible for the purpose of cross-theory comparison. We do not attempt to assign probabilities to theories, though we note empirical developments that bear on their relative standing.

---

## 3. Theory-by-Theory Analysis

### 3.1 Integrated Information Theory (IIT 4.0)

**Core claim.** Consciousness is identical to a maximally irreducible cause-effect structure (Tononi et al., 2023). A system is conscious if and only if it specifies a structure in qualia space with integrated information (Phi) greater than zero, meaning the system's cause-effect power over itself cannot be decomposed into the cause-effect power of its parts. The quantity and quality of experience are determined by the geometry of this Phi-structure. Critically, Phi is a property of the intrinsic causal architecture of a physical system, not of its input-output behavior.

**Substrate independence: No.** This follows directly from IIT's postulates. Two systems with identical input-output behavior can have different Phi values if their internal causal architectures differ. IIT famously predicts that feedforward networks have Phi = 0 regardless of computational complexity, and that a lookup table perfectly replicating human behavior would be unconscious. A standard digital computer simulating a brain would have near-zero Phi because the causal architecture of the CPU (serial gate operations) differs fundamentally from the brain's (massively recurrent, parallel causal structure). Consciousness could exist on a non-biological substrate, but only if that substrate physically instantiates the same intrinsic causal architecture — not merely the same function.

**Preservation requirements.** IIT requires the complete causal specification of the system at the level that maximizes Phi. This means: the full transition probability matrix (TPM) of every mechanism (neuron or neuronal group) — not just connectivity, but the precise probability distribution over future states given past states, including nonlinear dynamics, neuromodulatory modulation, and state-dependent interactions. At 86 billion neurons with ~10^14 synapses, estimating ~100 bytes per synapse for full causal parameterization yields ~10 PB of scan data. But the verification problem is worse: computing Phi requires evaluating all possible bipartitions of the system to find the minimum information partition. For N elements, this grows super-exponentially as ~2^(2^N) (Barrett and Seth, 2011; Tegmark, 2016). For even 40 binary elements, exact Phi computation is already infeasible. For 86 billion neurons, it is formally uncomputable on any conceivable classical computer. Simulation at the electrophysiology level requires ~10^22 FLOPS (Sandberg and Bostrom, 2008), but one could never verify that the simulation preserves Phi.

**Gradual replacement: Conditionally possible.** Each replacement element must have the exact same causal TPM as the original — not merely the same input-output function, but the same intrinsic causal power. A silicon neuron that mimics behavior through a lookup table would reduce Phi even if behavior is preserved. The bar is not functional equivalence but causal-structural identity.

**Scan-and-copy: No.** A functional copy on a standard computer would have near-zero Phi. IIT predicts the copy would be a philosophical zombie — behaviorally identical but unconscious.

**Key weakness.** Phi is computationally intractable, making the theory's predictions empirically unverifiable for real brains. The COGITATE collaboration (2025) partially supported IIT's prediction of content-specific posterior cortical activity but did not find the sustained synchronization IIT predicted. The "unfolding argument" (Doerig et al., 2019) demonstrates that for any recurrent network, a feedforward network with identical input-output behavior can be constructed, challenging IIT to explain how empirical evidence could ever distinguish its predictions from functionalist alternatives.

**Preservation verdict: 1/5.**

### 3.2 Global Neuronal Workspace Theory (GNWT)

**Core claim.** Consciousness is the global broadcasting of information across a distributed network of long-range cortical neurons — the "global workspace" (Baars, 1988; Dehaene et al., 2011). A representation becomes conscious when it wins a competition for workspace access and triggers "ignition" — a sudden, nonlinear, self-sustaining activation mediated by NMDA-dependent recurrent loops, primarily in prefrontal and parietal cortex, that broadcasts the information to all other cognitive modules simultaneously.

**Substrate independence: Yes.** GNWT is a functionalist theory. It describes an information-processing architecture: modular processors, a capacity-limited bottleneck, competitive access, and global broadcast. Dehaene has explicitly drawn parallels to AI architectures. Any physical system implementing this architecture — biological or digital — should support consciousness.

**Preservation requirements.** GNWT requires preserving the full connectome, synaptic weights, and ignition dynamics. Scanning resolution: ~10 nm to resolve individual synapses (demonstrated by Shapson-Coe et al. (2024) for 1 mm^3 of cortex). Data: ~2 PB for the processed connectome (10^14 synapses at ~20 bytes per synapse). Compute: 10^18 FLOPS for spiking-level simulation, scaling to 10^22 FLOPS at the electrophysiology (Hodgkin-Huxley) level, consistent with the Blue Brain Project's scaling from 31,000 neurons at ~1 PFLOPS (Markram et al., 2006). BCI bandwidth for gradual replacement: ~10^7 neurons/s at 10 kHz per neuron. Feasibility timeline: 2060-2080.

**Gradual replacement: Yes.** Replacement neurons need only reproduce the computational properties — activation functions, synaptic dynamics, long-range connectivity — of the originals. GNWT is agnostic about substrate.

**Scan-and-copy: Yes, with caveats.** The copy would be conscious and would have the original's memories and cognitive style. The duplication problem (two instances both believing they are "you") remains unaddressed by the theory.

**Key weakness.** The COGITATE results (2025) found weaker-than-predicted prefrontal involvement during conscious perception, challenging the claim that the prefrontal workspace is the seat of consciousness. GNWT may conflate access consciousness (information available for report and flexible use) with phenomenal consciousness (what it is like to have an experience). If so, a preservation strategy based on GNWT might preserve the functional "you" while losing qualia.

**Preservation verdict: 4/5.**

### 3.3 Higher-Order Thought Theory (HOT)

**Core claim.** A mental state is conscious when the system represents itself as being in that state (Rosenthal, 2005). Consciousness is not a property of first-order perceptual states but of the system's higher-order monitoring of those states. In Lau and Rosenthal's (2011) formulation, the brain has a higher-order system — primarily in prefrontal cortex — that tracks signal quality and generates confidence estimates. Phenomenal consciousness arises when higher-order representations meet certain quality criteria. Brown, Lau, and LeDoux (2019) developed this further: it is the higher-order representation itself that constitutes conscious experience, not the first-order state it targets.

**Substrate independence: Yes.** HOT is a theory about representational structure. A system needs the capacity to form higher-order representations of its own internal states. This is a computational requirement with no substrate dependency.

**Preservation requirements.** HOT requires preserving the first-order processing systems (sensory cortices) and the higher-order monitoring systems (prefrontal cortex, ~15-20% of cortical neurons). Because only a subset of the brain is directly consciousness-relevant, HOT permits a mixed-resolution scanning approach: ~10 nm for the ~10-15 billion neurons in PFC and sensory targets, coarser models for the remaining ~70 billion. This reduces data requirements to approximately 200 TB - 1 PB and compute to 10^17 - 10^20 FLOPS. BCI bandwidth for gradual replacement: ~10^6 neurons/s — one order of magnitude closer to current technology than GNWT. Feasibility timeline: 2055-2075.

**Gradual replacement: Yes.** Replacements need only preserve representational content and the first-order/higher-order monitoring relationships.

**Scan-and-copy: Yes.** The copy would have the original's self-model and would be conscious. Same duplication caveat.

**Key weakness.** HOT may explain metacognition rather than consciousness. The theory implies that first-order states without higher-order monitoring are unconscious, but evidence for rich phenomenal experience without metacognitive access (in animals, infants, flow states) is substantial. The hard problem persists: why does higher-order monitoring produce subjective experience rather than just being a computational loop?

**Preservation verdict: 5/5.**

### 3.4 Predictive Processing / Free Energy Principle

**Core claim.** The brain is a hierarchical prediction machine that minimizes free energy (prediction error) by maintaining a generative model of the world (Friston, 2010; Clark, 2013). Consciousness arises from the precision-weighted predictive processing dynamics of this model — specifically, from the system's capacity to model itself and its own uncertainty. Phenomenal character is determined by the structure of the generative model and the precision-weighting of prediction errors across hierarchical levels.

**Substrate independence: Unclear.** The Free Energy Principle is a mathematical framework that applies substrate-independently — any system with a Markov blanket that persists over time must minimize free energy. However, Friston and colleagues distinguish between systems that *simulate* free energy minimization and those that *actually* minimize it through genuine causal coupling with an environment. A disembodied digital brain may simulate prediction error minimization without genuinely performing active inference. The theory's position hinges on whether consciousness requires genuine embodied interaction or merely the right computational dynamics.

**Preservation requirements.** The complete generative model must be preserved: hierarchical predictions (synaptic weights), precision weights (neuromodulatory state — dopaminergic, cholinergic, noradrenergic, serotonergic systems), and the body model (interoceptive predictions, proprioception). Neuromodulatory receptor density maps at ~10 micrometer resolution add ~1 PB to the base connectome. Total: ~5 PB. Compute: 10^18 - 10^21 FLOPS. Additionally, the emulation must be embodied — coupled to an environment through sensors and actuators — for the theory to unambiguously predict consciousness. Feasibility timeline: 2060-2080.

**Gradual replacement: Probably yes.** Each replacement must maintain prediction, prediction-error, and precision dynamics. The key constraint is preserving temporal dynamics — prediction errors must propagate at the correct speeds through the hierarchy.

**Scan-and-copy: Conditionally.** The copy must be embodied. A disembodied generative model receiving no prediction errors would rapidly degrade. A copy placed in a body with appropriate sensory coupling would initially be "you" but would diverge through different experiences.

**Key weakness.** The Free Energy Principle may be unfalsifiable. As a mathematical framework, it is arguably true by definition for any persisting system. Systematic critiques (Andrews, 2021) have identified teleological reasoning and questioned whether the theory has genuine explanatory power for consciousness specifically, or is merely a universal framework compatible with consciousness. The theory does not clearly distinguish phenomenal consciousness from sophisticated unconscious inference.

**Preservation verdict: 3/5.**

### 3.5 Recurrent Processing Theory (RPT)

**Core claim.** Consciousness arises from recurrent (feedback) processing within sensory cortical areas (Lamme, 2000, 2006). Lamme distinguishes processing stages: feedforward sweep (unconscious), lateral interactions (unconscious), local recurrent processing within sensory areas (phenomenally conscious but not reportable), and recurrent processing involving frontal areas (conscious and reportable). The critical claim is that recurrent processing in sensory cortex alone — without prefrontal involvement — is already phenomenally conscious. This directly contradicts GNWT's requirement for prefrontal workspace activation.

**Substrate independence: Leaning yes.** RPT identifies consciousness with a computational process — recurrent processing — rather than a biological substrate. Lamme's formulation is neuroscience-grounded and does not directly address artificial substrates, but the theory's logic permits substrate independence if "recurrent processing" is treated as a substrate-neutral computational description.

**Preservation requirements.** RPT requires the full cortical connectome with emphasis on feedback (top-down) connections, synaptic weights for both feedforward and feedback pathways, and precise temporal dynamics. The timing of feedback signals is critical: the V1-V2 feedback loop operates on ~15 ms timescales, and consciousness depends on feedback arriving within a specific temporal window. This demands 0.1 ms temporal resolution (100 kHz simulation rate), potentially 10x more demanding than GNWT's 10 kHz. Data: ~2 PB (comparable to GNWT) plus ~1 TB of temporal calibration data (axonal conduction velocities, myelination thickness). Compute: 10^18 - 10^20 FLOPS, potentially less if only sensory cortices require full recurrent fidelity. Feasibility timeline: 2060-2080.

**Gradual replacement: Yes.** Recurrent connectivity and temporal dynamics must be preserved; the substrate does not matter.

**Scan-and-copy: Probably yes.** The copy implements recurrent processing with the original's learned connectivity patterns.

**Key weakness.** RPT's claim that recurrent processing within sensory cortex alone is sufficient for phenomenal consciousness is difficult to test. The theory was developed primarily for visual consciousness, and its extension to other modalities, emotions, and self-consciousness remains underspecified.

**Preservation verdict: 4/5.**

### 3.6 Biological Computationalism

**Core claim.** Consciousness arises from a specific kind of computation that only biological systems currently instantiate: hybrid, scale-inseparable, metabolically grounded processing (Aru and Milinkovic, 2025). The brain computes, but not like a digital computer. Neural computation combines discrete events (spikes) with continuous dynamics (voltage fields, chemical gradients). Crucially, this computation is scale-inseparable: cause and effect flow simultaneously across scales from ion channels to dendrites to circuits to whole-brain dynamics. The metabolic constraints of biological systems are constitutive, not incidental. Consciousness is what this kind of computation produces; "the algorithm is the substrate."

**Substrate independence: No.** This is the theory's core claim. Neural computation cannot be cleanly separated from its biological implementation. A different substrate could support consciousness only if it implements the same class of hybrid, scale-inseparable, metabolically grounded computation — which no existing digital architecture does.

**Preservation requirements.** Far more than a connectome. The theory requires preserving: synaptic weights, dendritic morphology, spatial distribution of ion channels and receptors (~200 functionally distinct channel types), extracellular ionic concentrations at ~1 micrometer^3 resolution (~100 PB), glial cell states (~170 billion cells at ~1.5 KB each = ~255 TB), and metabolic parameters. Scanning resolution: ~1 nm (cryo-EM level). Raw scan data: ~1-3 ZB. Processed molecular state: ~10-100 PB. Compute for simulation at metabolome level: ~10^25 FLOPS (Sandberg and Bostrom, 2008). Feasibility timeline: 2080-2100+, if ever.

**Gradual replacement: Only with biological replacements.** Silicon neurons that mimic input-output behavior would disrupt the scale-inseparable, continuous-discrete dynamics. Replacement elements would need to be synthetic biological systems — bioengineered neurons participating in the same fluidic, metabolically constrained, multiscale dynamics.

**Scan-and-copy: No.** A scan captures information but loses the physical dynamics. Running that information on a digital computer produces a functional replica without consciousness, because the computation is of the wrong kind.

**Key weakness.** The theory is new (December 2025) and empirically untested. Its core claim — that scale-inseparable computation is necessary for consciousness — is difficult to falsify. It risks being an argument from ignorance: "we don't know how digital systems could be conscious, therefore they can't be." Many biological computations *are* effectively separable across scales (reflexes, retinal processing), so the claim that all consciousness-relevant computation is scale-inseparable requires evidence that does not yet exist.

**Preservation verdict: 1/5.**

### 3.7 Orchestrated Objective Reduction (Orch OR)

**Core claim.** Consciousness arises from quantum computations in microtubules within neurons (Penrose and Hameroff, 1996). Penrose argues that consciousness involves non-computable processes — aspects of mathematical understanding that no algorithm can replicate. Hameroff proposes that tubulin proteins in microtubules exist in quantum superposition, and consciousness occurs when these superpositions undergo "objective reduction" (OR) — a quantum gravity-induced wave function collapse. Each OR event is a discrete moment of conscious experience.

**Substrate independence: No.** Orch OR requires quantum coherence in microtubules, specific biological structures. Penrose's non-computability argument further entails that no Turing machine — and therefore no digital computer — can produce consciousness. This is not a practical limitation but a claimed mathematical one.

**Preservation requirements: Physically impossible.** The brain contains ~8.6 x 10^18 tubulin dimers (10^4 microtubules per neuron, 10^8 tubulins per neuron, 86 billion neurons). Each tubulin is at minimum a qubit. The quantum state of 8.6 x 10^18 qubits requires a density matrix with 2^(8.6 x 10^18) entries — a number exceeding any meaningful physical quantity. The no-cloning theorem (Wootters and Zurek, 1982) prohibits creating identical copies of arbitrary unknown quantum states. Quantum state tomography requires many identical copies of the same state, which biological systems cannot provide. Quantum decoherence in biological tissue occurs on ~10^-13 s timescales (Tegmark, 2000), far faster than any conceivable measurement. Classical simulation of 10^18 qubits requires 2^(10^18) operations — a number with ~3 x 10^17 digits.

**Gradual replacement: Only with biological structures supporting quantum coherence.** Silicon neurons lack microtubules and cannot support the required quantum processes.

**Scan-and-copy: No, on multiple grounds.** The no-cloning theorem prevents quantum state copying. Non-computability prevents digital reproduction. Even a quantum computer would need to implement objective reduction in microtubule-like structures specifically.

**Key weakness.** Tegmark (2000) calculated that quantum decoherence in microtubules at brain temperature occurs in ~10^-13 seconds — far too fast for neural processes. While recent experiments show quantum effects in microtubules (energy migration over ~6.6 nm), these effects are orders of magnitude below Orch OR's requirements. The non-computability argument rests on a controversial interpretation of Godel's theorems that most logicians reject. Most neuroscientists and physicists consider Orch OR outside the scientific mainstream. The 2025 COGITATE results did not test Orch OR, and no major experimental program is currently designed to validate or refute it.

**Preservation verdict: 0/5.**

### 3.8 Attention Schema Theory (AST)

**Core claim.** Consciousness is the brain's simplified internal model of its own attention process (Graziano, 2013, 2017). The brain constructs an "attention schema" — a simplified model of how it selectively enhances some signals over others — analogous to the body schema it constructs for proprioception. When you report being conscious, you are reporting the contents of this model. The attention schema necessarily omits mechanistic details (electrochemistry, spike rates) and instead describes attention in terms of a subjective "awareness," which is why consciousness seems mysterious. Consciousness is not a metaphysical property but an internal representation — a useful model the brain constructs for monitoring and controlling attention.

**Substrate independence: Yes.** AST is explicitly functionalist. Graziano has published on engineering artificial consciousness using AST as a foundation (Graziano, 2017; Webb et al., 2021). Any system implementing an attention mechanism plus an internal model of that mechanism would be conscious.

**Preservation requirements.** AST has the most modest requirements of any theory. The attention schema itself is a low-dimensional model — plausibly ~10^4-10^5 parameters, comparable in complexity to the body schema. The self-model (autobiographical memory, personality, semantic knowledge) adds ~10^12-10^13 parameters at ~1-10 TB. The relevant neural circuits — prefrontal attention control (~2-4 billion neurons), parietal attention maps (~1-2 billion neurons), memory systems (~1 billion neurons), self-model circuits (~1-2 billion neurons) — total 5-10 billion neurons, perhaps 5-10% of the brain. Scanning resolution: ~1 micrometer (regional connectivity, achievable with diffusion MRI or expansion microscopy). Compute: 10^15 - 10^18 FLOPS, comparable to current large AI models at the lower end. BCI bandwidth: ~10^5 neurons/s at 1 kHz — zero orders of magnitude gap in channel count from current technology, though write capability remains the bottleneck. Feasibility timeline: 2040-2060.

**Gradual replacement: Yes.** The attention schema and attention mechanisms need only be functionally preserved. Substrate is irrelevant.

**Scan-and-copy: Yes.** The copy would have the original's attention schema and self-model. It would be conscious in the only sense AST recognizes.

**Key weakness.** AST may explain the *belief* in consciousness rather than consciousness itself. Under AST, "I am conscious" is the output of an internal model, and there is no further fact of the matter about whether the system "really" experiences anything. This is either a feature (it dissolves the hard problem) or a fatal flaw (it denies the most obvious datum of human existence — that experience exists). AST has difficulty accounting for the specific qualitative character of experience. If consciousness is genuinely real and not merely a representation, AST does not explain it — it explains it away.

**Preservation verdict: 5/5.**

---

## 4. Cross-Theory Comparison

### 4.1 Engineering Bridge Table

The table below maps each theory to its specific engineering requirements. This is the paper's primary quantitative contribution. All numbers are derived from the theory-specific analyses in Section 3 using the sources and methodology described in Section 2.

| Theory | Required Fidelity | Scanning Resolution | Data Size (processed) | Compute (FLOPS) | Storage | BCI Bandwidth (gradual) | Feasibility Timeline |
|--------|-------------------|--------------------:|----------------------:|----------------:|--------:|------------------------:|---------------------:|
| **IIT 4.0** | Full causal architecture (every element's TPM) | ~5 nm | ~100 EB | Verification: ~2^(2^N); Simulation: 10^22 | ~100 EB | Infeasible (must be simultaneous) | >2100 / never |
| **GNWT** | Connectome + weights + ignition dynamics | ~10 nm | ~2 PB | 10^18 - 10^22 | ~2 PB | ~10^7 neurons/s @ 10 kHz | 2060-2080 |
| **HOT** | Connectome + weights (PFC + sensory targets) | ~10 nm (partial) | ~500 TB | 10^17 - 10^20 | ~500 TB | ~10^6 neurons/s @ 10 kHz | 2055-2075 |
| **Predictive Processing** | Generative model + precision weights + body model | ~10-100 nm | ~5 PB | 10^18 - 10^21 | ~5 PB | ~10^7 neurons/s @ 1 kHz | 2060-2080 |
| **RPT** | Recurrent connectivity + sub-ms timing | ~10 nm | ~2 PB | 10^18 - 10^20 | ~2 PB | ~10^7 neurons/s @ 100 kHz | 2060-2080 |
| **Bio. Comp.** | Molecular-level snapshot | ~1 nm | ~10-100 PB | 10^25 | ~100 PB | Infeasible (current paradigms) | 2080-2100+ |
| **Orch OR** | Quantum states of microtubules + connectome | Sub-nm + quantum state tomography | N/A (no-cloning) | 2^(10^18) | N/A | Physically impossible | Never |
| **AST** | Attention schema + self-model + episodic memory | ~1 um | ~1-10 TB | 10^15 - 10^18 | ~1-10 TB | ~10^5 neurons/s @ 1 kHz | 2040-2060 |

Several features of this table deserve emphasis.

First, the data size column spans roughly 10 orders of magnitude — from ~1 TB (AST) to ~100 EB (IIT) to formally infinite (Orch OR). The theories do not disagree on small matters. They disagree on whether consciousness preservation is a straightforward engineering problem, an extremely difficult one, or a physical impossibility.

Second, the compute column has an even wider span. AST's lower bound (10^15 FLOPS) is achievable on current high-end hardware. GNWT's upper bound (10^22 FLOPS) requires roughly 10,000x current exascale systems. Orch OR's requirement (2^(10^18) operations) is not a large number — it is a number that cannot be meaningfully written, computed, or compared to any physical quantity.

Third, feasibility timelines cluster into three groups: near-term under favorable theories (2040-2060 for AST), mid-century under moderate theories (2055-2080 for GNWT/HOT/RPT/PP), and never under hostile theories (IIT verification, Orch OR). The difference between the most and least favorable theories is not decades but the distinction between possible and impossible.

### 4.2 Points of Consensus

Despite their disagreements, all eight theories converge on three engineering requirements.

**Temporal dynamics must be preserved.** No theory treats consciousness as a static property of a network. IIT requires specific causal dynamics that determine the grain at which Phi is maximized. GNWT requires ignition events with specific temporal profiles. RPT requires feedback processing within precise temporal windows (~100-300 ms post-stimulus). Predictive Processing requires ongoing prediction error minimization at hierarchically organized timescales. Even AST, the most minimal theory, requires a dynamic process of attention modulation and schema updating. This consensus has a direct engineering implication: any preservation strategy that captures only a static snapshot — connectivity without dynamics — is insufficient under every theory. Temporal parameters (synaptic time constants, conduction velocities, oscillatory frequencies) must be preserved or inferrable from the preserved structure.

**Integration across components is necessary.** All theories require that information be combined across processing streams rather than remaining isolated. IIT defines consciousness as integrated information. GNWT requires global broadcast across modules. HOT requires monitoring relationships across representational levels. RPT requires recurrent interactions across cortical layers. Predictive Processing requires hierarchical coordination of predictions. AST requires the attention schema to integrate information about the attention mechanism. This rules out preservation strategies that capture individual neurons or circuits in isolation — the relationships between components are as critical as the components themselves.

**Feedforward-only systems are ruled out.** Every theory requires some form of recurrence or feedback. IIT assigns Phi = 0 to feedforward networks. GNWT requires re-entrant broadcast. HOT requires bidirectional monitoring. RPT defines consciousness as recurrent processing. Predictive Processing requires top-down predictions meeting bottom-up errors. AST requires feedback from the schema to the attention mechanism. This is the strongest consensus in the field, and it is empirically supported: feedforward processing in the initial ~100 ms of visual processing does not produce conscious experience.

### 4.3 The Substrate Independence Fault Line

The most consequential disagreement across theories is substrate independence. Four theories (GNWT, HOT, AST, RPT) are substrate-independent: they define consciousness in terms of computational or functional properties that can, in principle, be instantiated on any physical substrate. Three theories (IIT, Biological Computationalism, Orch OR) are substrate-dependent, though for different reasons: IIT because intrinsic causal architecture matters, not function; Biological Computationalism because the algorithm is inseparable from the substrate; Orch OR because quantum coherence in specific biological structures is required. One theory (Predictive Processing) straddles the line, with the answer depending on whether consciousness requires genuine embodied active inference or merely the right computational dynamics.

This fault line determines whether digital preservation is even conceivable. Under the four substrate-independent theories, a sufficiently detailed digital emulation of a brain is conscious and is, in the relevant sense, the original person. Under the three substrate-dependent theories, no amount of digital emulation suffices — the copy would be a behavioral replica without inner experience. These are not positions that can be split or compromised. Either the substrate matters or it does not.

What would resolve this question? The most direct experiment would be a neural prosthesis test: replace a small population of neurons in a conscious animal with artificial neurons that are functionally identical but physically different, and measure whether consciousness-relevant behaviors and neural signatures are preserved. If a silicon replacement of cortical neurons preserves the animal's visual awareness (as assessed by, e.g., binocular rivalry paradigms or no-report paradigms), substrate independence receives strong support. If identical function on a different substrate produces measurably different consciousness-relevant signatures, substrate dependence gains evidence. Current neural prostheses (retinal implants, cochlear implants) are too crude to test this — they restore function but do not replace individual neurons with the fidelity required to distinguish the theories.

### 4.4 The Deflation Paradox

Our analysis reveals a tension that, to our knowledge, has not been previously identified in the preservation literature. We call it the deflation paradox.

The theories most favorable to consciousness preservation — AST and HOT — are precisely those that deflate consciousness to a functional property or internal model. Under AST, consciousness is "just" the brain's simplified model of its own attention. Under HOT, consciousness is "just" the brain's higher-order monitoring of its own states. These theories make preservation easy because they reduce consciousness to information processing, which is substrate-independent and information-theoretically compact.

The theories that take phenomenal consciousness most seriously — IIT, Biological Computationalism, and Orch OR — are precisely those that make preservation hardest or impossible. IIT identifies consciousness with the intrinsic causal structure of the physical substrate, making emulation insufficient. Biological Computationalism makes consciousness inseparable from the biological medium. Orch OR ties consciousness to quantum physics in a way that prevents copying entirely.

This is not a coincidence. There is a deep structural relationship between how seriously a theory takes the irreducibility of subjective experience and how difficult it makes preservation. Theories that identify consciousness with something beyond functional organization — with the intrinsic nature of the physical substrate, with the specific character of biological computation, with quantum processes — necessarily make that something harder to replicate or transfer. Theories that reduce consciousness to functional organization make it transferable but, their critics argue, fail to capture what makes consciousness consciousness.

The deflation paradox presents a genuine dilemma for anyone investing in consciousness preservation. If you believe your conscious experience is real, irreducible, and not merely a functional property — if you take the hard problem seriously — then the theories most aligned with your intuitions are the ones that say preservation is impossible. If you are comfortable with the idea that consciousness is "just" a computational pattern, preservation is straightforward — but you must accept that what you are preserving is a pattern, not an ineffable essence.

---

## 5. Risk Analysis

### 5.1 Preservation Strategies Against Theory Space

We assess four preservation strategies against all eight theories.

**Strategy 1: Whole-brain emulation on digital hardware.** A brain is preserved, destructively scanned, and simulated on a digital computer. This succeeds under GNWT, HOT, AST, and probably RPT (4 theories). It fails under IIT, Biological Computationalism, and Orch OR (3 theories). It is unclear under Predictive Processing (1 theory), where success may require embodiment. Cross-theory survival probability, treating theories as equally likely: ~50-60%.

**Strategy 2: Gradual neuron-by-neuron replacement with functionally identical silicon.** Biological neurons are incrementally replaced with artificial neurons that reproduce their computational behavior while the subject remains conscious. This succeeds under GNWT, HOT, AST, RPT, and probably Predictive Processing (5 theories). It fails under Orch OR (1 theory) and likely fails under Biological Computationalism (1 theory). It conditionally succeeds under IIT only if replacements are causal-structurally identical, not merely functionally identical (1 theory). Cross-theory survival probability: ~55-65%.

**Strategy 3: Biological preservation (cryonics followed by future revival).** The brain is cryopreserved, with the hope that future technology can repair damage and restore biological function. If revival succeeds, this works under all 8 theories, because a revived biological brain satisfies every theory's requirements. The risk is entirely practical — whether cryopreservation actually preserves the relevant information and whether revival technology will ever exist — not theoretical. Cross-theory survival probability: ~100% in theory-space, unknown in practice.

**Strategy 4: Gradual replacement with bio-hybrid components.** Neurons are replaced with synthetic biological elements (bioengineered neurons, artificial cells) that implement the same class of computation as biological neurons, including continuous-discrete dynamics and metabolic grounding. This succeeds under 7 of 8 theories (all except Orch OR, which requires quantum coherence that even synthetic biology may not replicate). Cross-theory survival probability: ~80-90% in theory-space, ~0% with current technology.

### 5.2 Why Gradual Replacement Dominates

Across the theory space, gradual biological replacement emerges as the dominant strategy. It is the only approach that no theory definitively rules out (even IIT and Biological Computationalism allow it under specific conditions). It avoids the philosophical problems of scan-and-copy by maintaining continuity of the physical system. And it sidesteps the duplication problem entirely — there is never a moment when two copies of the person exist.

However, gradual replacement is also the most technologically distant strategy. It requires brain-wide, single-neuron-resolution bidirectional BCI, which is 7+ orders of magnitude beyond current technology in simultaneous neuron count (Stevenson and Kording, 2011). At historical doubling rates for electrode count (~7-8 years per doubling), this gap closes in ~170 years. Even with aggressive acceleration, ~70 years is optimistic. The dominant strategy is the least feasible one.

### 5.3 The Continuity Problem

There is a philosophical risk that cross-theory analysis reveals but does not resolve. Even under theories that permit scan-and-copy (GNWT, HOT, AST, RPT), the copy is a new person who has the original's memories, personality, and cognitive style. It sincerely believes it is the original. But the original's stream of consciousness ends at the moment of destructive scanning.

This is not a problem that better scanning or more compute can solve. It is a conceptual problem about the nature of personal identity. Under a psychological continuity view of identity, the copy *is* you — identity consists in psychological connections, and the copy has all of them. Under a biological continuity view, the copy is a new person who inherits your psychology. Under a four-dimensionalist view, the original and copy are different temporal worms that share a common initial segment.

No theory of consciousness resolves this question, because it is a question about identity, not about consciousness. A preservation strategy could succeed at preserving consciousness (the copy is conscious, has your experiences, has your memories) while failing to preserve *you* (your particular stream of subjective experience terminates). This distinction is the reason gradual replacement, despite its engineering difficulty, has philosophical advantages over scan-and-copy: it maintains the physical continuity that biological and four-dimensionalist views of identity require.

---

## 6. Discussion

### 6.1 The Primary Bottleneck Is Theory, Not Engineering

The central finding of this analysis is that the engineering requirements for consciousness preservation are not merely uncertain — they are uncertain by 10+ orders of magnitude, and this uncertainty is entirely determined by which theory of consciousness is correct. Under AST, the engineering challenge is comparable to building a large AI model: ~1-10 TB of data, ~10^15-10^18 FLOPS, scanning at ~1 micrometer resolution — all within striking distance of current technology. Under IIT, the verification problem is formally intractable regardless of technological progress. Under Orch OR, preservation violates known physics.

This has a practical implication: investments in consciousness preservation engineering are premature until the theory question is better resolved. A scanning facility designed for 10 nm EM is wasted if AST is correct (1 micrometer suffices). A 10^22 FLOPS computer is wasted if Biological Computationalism is correct (the computation must be biological). The most cost-effective intervention for anyone who cares about consciousness preservation is funding consciousness research — specifically, experiments that discriminate between substrate-independent and substrate-dependent theories.

### 6.2 Experiments That Would Resolve the Question

The substrate independence question could be addressed by several experimental programs:

1. **Neural prosthesis with consciousness readout.** Replace a small cortical area with silicon neurons that are functionally identical to the originals, in an animal model with established consciousness indicators (e.g., binocular rivalry, no-report paradigms). If consciousness-relevant signatures are preserved, substrate independence gains strong support.

2. **Organoid consciousness assessment.** Brain organoids grown from human stem cells are developing increasingly complex neural architectures. If organoid-based neural tissue can be shown to support consciousness indicators, this supports Biological Computationalism's claim that the biological substrate matters. If organoids *with identical architecture but different molecular composition* show different consciousness signatures, substrate dependence is supported.

3. **IIT vs. GNWT adversarial tests.** COGITATE (2025) was a first step. Future adversarial collaborations that specifically test substrate-dependent predictions (IIT) against substrate-independent predictions (GNWT) on the same paradigms would directly address the fault line.

4. **Quantum decoherence measurements in neural tissue.** Direct measurement of quantum coherence times in microtubules under physiological conditions would either support or definitively refute Orch OR. If decoherence times are confirmed at ~10^-13 s (Tegmark's estimate), Orch OR is ruled out for practical purposes, removing one theory from the hostile column.

### 6.3 Implications for Current Preservation Efforts

For cryonics organizations (Alcor, Until Labs): the analysis supports continued investment in brain preservation quality, since biological revival is the only strategy that works under all theories. The marginal value of improving preservation quality (reducing cryoprotectant damage, improving perfusion completeness) is higher than the marginal value of better scanning technology, because better preservation keeps more strategies open.

For connectomics projects (Google/Harvard, E11 Bio PRISM): the connectome is necessary under 6 of 8 theories (all except Orch OR and arguably AST). Continued investment in scanning throughput and automated proofreading is well-justified regardless of which theory turns out to be correct.

For BCI development (Neuralink, Paradromics): the 7+ order-of-magnitude gap between current BCI bandwidth and gradual-replacement requirements means that BCI development is not on any plausible critical path for consciousness preservation this century. BCI bandwidth may be the most important long-term bottleneck, but it is not the binding constraint today.

### 6.4 Limitations

This analysis has several limitations beyond those noted in Section 2.4. We do not assign probabilities to theories, though some (GNWT, Predictive Processing) have substantially more empirical support than others (Orch OR). We treat theories as monolithic, though internal variations exist (e.g., Lau's PRM variant of HOT differs from Rosenthal's classical version in ways that affect preservation implications). We focus on information-theoretic and computational requirements and do not address cost, which may be the binding constraint in practice (a full human connectome scan could cost billions of dollars even if the technology exists). Finally, we assume that current theories exhaust the relevant possibility space, which they almost certainly do not — a future theory of consciousness may have preservation implications that differ from all eight theories considered here.

### 6.5 Future Directions

Three extensions of this work would be valuable. First, a formal decision-theoretic analysis that assigns probabilities to theories (based on empirical evidence and expert survey) and computes expected utility for each preservation strategy. Second, an engineering-side analysis that maps each theory's requirements to specific technology roadmaps, identifying the theory-conditional critical path to preservation for each strategy. Third, a deeper analysis of the deflation paradox, exploring whether it represents a genuine philosophical constraint or an artifact of how current theories are formulated.

---

## 7. Conclusion

We have systematically mapped eight major theories of consciousness to their specific engineering requirements for consciousness preservation. The exercise reveals three findings.

First, the engineering requirements vary by 10+ orders of magnitude depending on which theory is correct — from ~1 TB and 10^15 FLOPS (AST) to formally impossible (Orch OR). This is not a typical case of scientific uncertainty reducing engineering precision by a factor of two or three. The theories disagree on whether the problem is tractable.

Second, despite this disagreement, there is genuine consensus: all eight theories require temporal dynamics, integration across components, and recurrent processing. Any preservation strategy must capture these features. Static connectome snapshots are insufficient under every theory.

Third, the theories reveal a structural paradox. The theories most compatible with preservation are those that deflate consciousness to a functional property. The theories that take subjective experience most seriously make preservation hardest. This means that confidence in the possibility of consciousness preservation requires, implicitly, a deflationary view of what consciousness is. Anyone who believes both that consciousness is a deep, irreducible feature of reality and that it can be straightforwardly digitally preserved holds a position that no current theory supports.

The practical recommendation is clear: the primary bottleneck for consciousness preservation is not scanning resolution, not compute, and not storage. It is the theory of consciousness. Resolving which theory is correct — particularly whether consciousness is substrate-independent — would collapse the engineering requirements from a 10+ order-of-magnitude uncertainty range to a tractable specification. Until that resolution, the most robust strategy is biological preservation (cryonics with the highest achievable quality), because it is the only approach that keeps all doors open regardless of which theory proves correct. Investments in consciousness theory research, and specifically in experiments that discriminate between substrate-dependent and substrate-independent theories, have higher expected value for consciousness preservation than any engineering investment currently being made.

---

## References

Andrews, M. (2021). The math is not the territory: Navigating the free energy principle. *Biology & Philosophy*, 36(5), 30.

Aru, J., and Milinkovic, D. (2025). Biological computationalism and the nature of neural computation. *Neuroscience & Biobehavioral Reviews*, 169, 105563.

Azevedo, F. A. C., Carvalho, L. R. B., Grinberg, L. T., Farfel, J. M., Ferretti, R. E. L., Leite, R. E. P., Filho, W. J., Lent, R., and Herculano-Houzel, S. (2009). Equal numbers of neuronal and nonneuronal cells make the human brain an isometrically scaled-up primate brain. *Journal of Comparative Neurology*, 513(5), 532-541.

Baars, B. J. (1988). *A Cognitive Theory of Consciousness*. Cambridge University Press.

Barrett, A. B., and Seth, A. K. (2011). Practical measures of integrated information for time-series data. *PLOS Computational Biology*, 7(1), e1001052.

Brown, R., Lau, H., and LeDoux, J. E. (2019). Understanding the higher-order approach to consciousness. *Trends in Cognitive Sciences*, 23(9), 754-768.

Butlin, P., Long, R., Elmoznino, E., Bengio, Y., Birch, J., Constant, A., Deane, G., Fleming, S. M., Frith, C., Ji, X., Kanai, R., Klein, C., Lindsay, G., Michel, M., Mudrik, L., Peters, M. A. K., Schwitzgebel, E., Simon, J., and VanRullen, R. (2023). Consciousness in artificial intelligence: Insights from the science of consciousness. *arXiv preprint*, arXiv:2308.08708.

Chalmers, D. J. (2010). The singularity: A philosophical analysis. *Journal of Consciousness Studies*, 17(9-10), 7-65.

Clark, A. (2013). Whatever next? Predictive brains, situated agents, and the future of cognitive science. *Behavioral and Brain Sciences*, 36(3), 181-204.

Dehaene, S., Lau, H., and Kouider, S. (2017). What is consciousness, and could machines have it? *Science*, 358(6362), 486-492.

Dehaene, S., and Changeux, J.-P. (2011). Experimental and theoretical approaches to conscious processing. *Neuron*, 70(2), 200-227.

Doerig, A., Schurger, A., Hess, K., and Herzog, M. H. (2019). The unfolding argument: Why IIT and other causal structure theories cannot explain consciousness. *Consciousness and Cognition*, 72, 49-59.

Friston, K. (2010). The free-energy principle: A unified brain theory? *Nature Reviews Neuroscience*, 11(2), 127-138.

Graziano, M. S. A. (2013). *Consciousness and the Social Brain*. Oxford University Press.

Graziano, M. S. A. (2017). The attention schema theory: A foundation for engineering artificial consciousness. *Frontiers in Robotics and AI*, 4, 60.

Lamme, V. A. F. (2000). The distinct modes of vision offered by feedforward and recurrent processing. *Trends in Neurosciences*, 23(11), 571-579.

Lamme, V. A. F. (2006). Towards a true neural stance on consciousness. *Trends in Cognitive Sciences*, 10(11), 494-501.

Lau, H., and Rosenthal, D. (2011). Empirical support for higher-order theories of conscious awareness. *Trends in Cognitive Sciences*, 15(8), 365-373.

Markram, H. (2006). The Blue Brain Project. *Nature Reviews Neuroscience*, 7(2), 153-160.

McIntyre, R. L., and Fahy, G. M. (2015). Aldehyde-stabilized cryopreservation. *Cryobiology*, 71(3), 448-458.

Melloni, L., Mudrik, L., Pitts, M., Bendtz, K., Ferrante, O., Gorska, U., Hirschhorn, R., Khalaf, A., Kosciessa, J., Kozma, C., et al. (2023). An adversarial collaboration to critically evaluate theories of consciousness. *bioRxiv*. (Results published in *Nature*, 2025.)

Musk, E., and Neuralink (2019). An integrated brain-machine interface platform with thousands of channels. *Journal of Medical Internet Research*, 21(10), e16194.

Penrose, R., and Hameroff, S. R. (1996). Orchestrated reduction of quantum coherence in brain microtubules: A model for consciousness. *Mathematics and Computers in Simulation*, 40(3-4), 453-480.

Rosenthal, D. M. (2005). *Consciousness and Mind*. Oxford University Press.

Sandberg, A., and Bostrom, N. (2008). *Whole Brain Emulation: A Roadmap*. Technical Report 2008-3, Future of Humanity Institute, University of Oxford.

Shapson-Coe, A., Januszewski, M., Berger, D. R., Pope, A., Wu, Y., Blakely, T., Schalek, R. L., Li, P. H., Wang, S., Maitin-Shepard, J., et al. (2024). A petavoxel fragment of human cerebral cortex reconstructed at nanoscale resolution. *Science*, 384(6696), eadk4858.

Stevenson, I. H., and Kording, K. P. (2011). How advances in neural recording affect data analysis. *Nature Neuroscience*, 14(2), 139-142.

Tegmark, M. (2000). Importance of quantum decoherence in brain processes. *Physical Review E*, 61(4), 4194-4206.

Tegmark, M. (2016). Improved measures of integrated information. *PLOS Computational Biology*, 12(11), e1005123.

Tononi, G., Boly, M., Massimini, M., and Koch, C. (2016). Integrated information theory: An updated account. *Archives Italiennes de Biologie*, 154, 56-67.

Tononi, G., Albantakis, L., Boly, M., Massimini, M., and Koch, C. (2023). Integrated information theory (IIT) 4.0: Formulating the properties of phenomenal existence in physical terms. *PLOS Computational Biology*, 19(10), e1011465.

Webb, T. W., Kean, H. H., and Graziano, M. S. A. (2021). Effects of awareness and attention in a neural network agent. *Proceedings of the National Academy of Sciences*, 118(13), e2021535118.

Wootters, W. K., and Zurek, W. H. (1982). A single quantum cannot be cloned. *Nature*, 299(5886), 802-803.
