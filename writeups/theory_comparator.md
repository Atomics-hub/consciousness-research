# Consciousness Theory Comparator: Implications for Preservation

*Technical analysis — March 2026*
*Last updated with COGITATE results (Nature, April 2025), Aru et al. biological computationalism (December 2025), and latest empirical developments across all major theories.*

---

## Methodological Note

This analysis evaluates eight major theories of consciousness through the lens of consciousness preservation — mind uploading, digital emulation, gradual replacement, and related scenarios. Each theory is assessed on its own terms: what it says consciousness *is*, and what logically follows for preservation. Where a theory is silent on a question, I extrapolate from its core commitments rather than guess.

The preservation verdict (1-5) rates how favorable each theory is for digital consciousness preservation, not how likely the theory is to be correct.

---

## 1. Integrated Information Theory (IIT 4.0) — Tononi et al.

### 1.1 What IS consciousness under this theory?

Consciousness is identical to a maximally irreducible cause-effect structure (a "Phi-structure") specified by a physical substrate. IIT 4.0 starts from five axioms describing the essential properties of experience — intrinsicality, information, integration, exclusion, and composition — and derives corresponding postulates that any physical substrate of consciousness must satisfy. A system is conscious if and only if it specifies a Phi-structure with Phi > 0, meaning the system's cause-effect power over itself cannot be reduced to that of its parts. The quantity and quality of consciousness are determined by the geometry of this structure in qualia space. Crucially, Phi is a property of the *intrinsic* causal architecture, not of input-output behavior.

### 1.2 Is consciousness substrate-independent?

**No.** IIT is explicitly substrate-*dependent* in a specific way: what matters is the intrinsic causal architecture of the physical substrate, not its functional behavior. Two systems with identical input-output mappings can have radically different Phi values. IIT famously predicts that feedforward networks have Phi = 0 regardless of complexity, meaning they are not conscious at all. A lookup table that perfectly replicates human behavior has zero integrated information. The substrate must have the right kind of recurrent causal structure; merely simulating that structure on a different architecture does not transfer consciousness.

### 1.3 Does digital emulation preserve consciousness?

**No** — with a critical caveat. A standard digital computer running a brain simulation would not be conscious under IIT, because the simulation's causal architecture differs from the brain's. The gates in a CPU are arranged in a way that produces minimal integrated information even when simulating a highly integrated system. However, if a digital system were physically engineered to have the *same intrinsic causal architecture* as the original brain (not merely the same function), IIT would say it is conscious. The problem is that this essentially requires building a brain-like physical system, defeating the purpose of digital emulation.

### 1.4 What information must be preserved?

The complete causal architecture at the level that maximizes Phi. This includes: the full connectome (which neurons connect to which), the precise causal transition probability matrix of every mechanism (neuron or group of neurons), and the way these mechanisms constrain each other's past and future states. Synaptic weights, dendritic integration properties, neuromodulatory states, and anything else that shapes the cause-effect repertoire of the system. Temporal dynamics matter insofar as they determine the grain at which Phi is maximized. IIT does not require quantum states, but it requires far more than a connectome — it requires the full causal specification at the intrinsic level.

### 1.5 What's the minimum viable "you"?

The maximally irreducible Phi-structure that corresponds to your current experience. Under IIT, "you" are literally the geometry of your qualia space at a given moment, which is determined by the intrinsic causal architecture of your brain. Preserving personal identity requires preserving the substrate that generates this specific Phi-structure, including whatever makes your cause-effect repertoires yours rather than someone else's. There is no shortcut: the full causal transition probabilities of every relevant mechanism must be maintained.

### 1.6 Does gradual replacement work?

**Maybe, but only under strict conditions.** If each silicon replacement has *exactly* the same causal transition probability matrix as the neuron it replaces — not just the same input-output function, but the same intrinsic causal power — then Phi is preserved and consciousness continues. If the replacement merely mimics behavior (same outputs for same inputs) but achieves this through a different internal causal structure (e.g., a lookup table), then Phi drops and consciousness is lost even though behavior is unchanged. The bar is extraordinarily high: functional equivalence is not sufficient.

### 1.7 Does scan-and-copy work?

**No.** A perfect functional copy running on a standard digital computer would have a different (likely near-zero) Phi. You would be destroyed and what runs on the computer would be a philosophical zombie that behaves exactly like you. IIT is the worst possible theory for scan-and-copy scenarios.

### 1.8 Biggest weakness

The computational intractability of Phi. Calculating Phi for a system of even modest size is NP-hard, making it impossible to empirically verify the theory's predictions for any real brain. The COGITATE adversarial collaboration (Nature, 2025) partially supported IIT's prediction of content-specific posterior cortical activity but failed to find the sustained synchronization IIT predicted, challenging the claim that network connectivity specifies consciousness. Additionally, IIT's implication that simple systems like thermostats have micro-consciousness strikes many researchers as a reductio ad absurdum (the "panpsychism problem"). The "unfolding argument" (Doerig et al.) shows that for any recurrent system, a feedforward system with the same input-output behavior can be constructed — meaning IIT either denies consciousness to functionally identical systems or must accept its predictions are empirically untestable.

### 1.9 Preservation verdict: **1/5**

IIT is the most hostile major theory to digital preservation. It explicitly predicts that functional emulation does not preserve consciousness, and the conditions for substrate-level preservation are so stringent as to be practically impossible with current or foreseeable digital technology.

---

## 2. Global Neuronal Workspace Theory (GNWT) — Dehaene, Changeux

### 2.1 What IS consciousness under this theory?

Consciousness is the global broadcasting of information across a network of long-range cortical neurons (the "global workspace"). At any moment, most cognitive processing is unconscious and modular. A representation becomes conscious when it wins a competition for access to the workspace — a distributed network of neurons with long-range axonal projections, concentrated in prefrontal and parietal cortex — and is broadcast widely to all other processors. This broadcast event is called "ignition": a sudden, nonlinear, self-sustaining activation that makes the information simultaneously available for verbal report, working memory, planning, and flexible behavior. Consciousness is access — the information that is globally available.

### 2.2 Is consciousness substrate-independent?

**Yes, in principle.** GNWT is a functionalist theory at its core. What matters is the computational architecture: modular processors competing for access to a global broadcast channel. The theory describes an information-processing architecture, not a biological substrate. Dehaene has explicitly drawn parallels between the global workspace and AI architectures. If a digital system implements the right architecture — modular processors, bottleneck competition, global broadcast with ignition dynamics — it should be conscious.

### 2.3 Does digital emulation preserve consciousness?

**Yes, with conditions.** A digital system must implement: (1) parallel modular processors, (2) a capacity-limited global workspace with competitive access, (3) nonlinear ignition dynamics (sudden transition from unconscious to conscious processing), and (4) re-entrant broadcast so that workspace contents influence all modules. A brain emulation that faithfully replicates these computational dynamics would be conscious. A simple feedforward network would not, because it lacks the workspace architecture.

### 2.4 What information must be preserved?

The functional architecture of the global workspace: which modules exist, what they compute, how they compete for workspace access, and the dynamics of ignition and broadcast. This requires at minimum the connectome of long-range cortical projections, the processing characteristics of each module (roughly, synaptic weights and activation functions), and the inhibitory/excitatory dynamics that govern competition. It does not require molecular-level detail, quantum states, or precise metabolic information — but it does require the temporal dynamics of ignition (the specific nonlinear transition thresholds).

### 2.5 What's the minimum viable "you"?

The specific pattern of modular processors, their learned contents, and the workspace access dynamics that determine which information gets broadcast and when. Your personal identity under GNWT is determined by: (1) the specific knowledge and skills encoded in your cortical modules, (2) the biases and thresholds that determine what you become conscious of, (3) your working memory patterns and executive control strategies. This is roughly equivalent to a high-fidelity connectome plus synaptic-level weight information — a substantial but theoretically achievable scan.

### 2.6 Does gradual replacement work?

**Yes.** If replacement neurons faithfully reproduce the computational properties of original neurons — their activation functions, synaptic dynamics, and long-range connectivity — then the global workspace architecture is preserved and consciousness continues uninterrupted. GNWT is agnostic about what the neurons are made of; only their function matters.

### 2.7 Does scan-and-copy work?

**Yes, but with an identity caveat.** The copy would be conscious (it has the workspace architecture) and would have your memories, personality, and cognitive style. Whether it is *you* is a question GNWT does not directly address — the theory defines consciousness as a computational property, not as personal identity. Two instances of the same workspace would both be conscious and would both believe they are you. The philosophical problem of duplication remains.

### 2.8 Biggest weakness

The COGITATE results (2025) substantially challenged GNWT: the expected ignition signature at stimulus offset was largely absent, and representation of conscious content in the prefrontal cortex was weaker than predicted. This raises the possibility that the prefrontal "workspace" is more about reportability and cognitive access than about consciousness per se. GNWT may confuse the mechanisms of *reporting* consciousness with consciousness itself — it cannot explain why global broadcast *feels like something* rather than just being a functional event. It also struggles with phenomenal consciousness that seems to overflow cognitive access (Lamme's "phenomenal consciousness without access" experiments).

### 2.9 Preservation verdict: **4/5**

GNWT is highly favorable for digital preservation. It is substrate-independent, computationally specifiable, and the information requirements (connectome + synaptic weights + dynamics) are demanding but potentially achievable. Loses one point because the theory may not capture phenomenal consciousness — only access consciousness — meaning you might preserve the functional "you" but lose qualia.

---

## 3. Higher-Order Theories (HOT) — Rosenthal, Lau, Brown

### 3.1 What IS consciousness under this theory?

A mental state is conscious when it is the target of a higher-order representation — roughly, when the system represents itself as being in that state. In Rosenthal's version, a first-order perceptual state (e.g., seeing red) becomes conscious when the system has a (typically non-conscious) higher-order thought that it is in that state. Consciousness is not a property of the first-order state itself but of the system's self-monitoring. Lau's perceptual reality monitoring (PRM) variant frames this computationally: the brain has a higher-order system that tracks signal quality and generates confidence estimates, and phenomenal consciousness arises when these higher-order representations meet certain criteria. Brown's HOROR variant goes further: it is the higher-order representation itself that is phenomenally conscious, not the first-order state it represents.

### 3.2 Is consciousness substrate-independent?

**Yes.** HOT is fundamentally a theory about representational structure — a system needs the capacity to represent its own internal states. This is a computational requirement that does not depend on biology. Any system that can form higher-order representations of its own processing states could, in principle, be conscious. The theory is straightforwardly functionalist.

### 3.3 Does digital emulation preserve consciousness?

**Yes.** A digital system that implements first-order processing and higher-order monitoring of that processing satisfies the conditions for consciousness. The system must have: (1) first-order representations of the world, (2) a higher-order system that represents the system's own first-order states, and (3) the right kind of representational relationship between these levels. Current large language models arguably fail because they lack genuine higher-order self-monitoring (they have no real-time model of their own processing states), but a brain emulation would succeed because it replicates the architecture that generates higher-order representations.

### 3.4 What information must be preserved?

The first-order representational systems (sensory processing, motor processing, etc.) and the higher-order monitoring systems (likely centered on prefrontal cortex and associated circuits). Specifically: the contents of learned representations, the connectivity between first-order and higher-order systems, and the computational dynamics that allow higher-order states to track first-order states. This requires a detailed connectome and synaptic weights for both the sensory/motor hierarchy and the prefrontal monitoring circuits. Temporal dynamics matter for the Lau/PRM version (signal detection theory requires timing).

### 3.5 What's the minimum viable "you"?

The specific pattern of first-order representations (your learned knowledge, perceptual categories, motor skills) plus the specific pattern of higher-order monitoring (what you're inclined to notice about your own mental states, your metacognitive biases, your self-model). Personal identity under HOT is determined by the contents of your self-representation: your beliefs about who you are, your autobiographical memories, and your metacognitive habits. This is a relatively compact specification compared to IIT — it is the information content that matters, not the causal microarchitecture.

### 3.6 Does gradual replacement work?

**Yes.** As long as replacements preserve the representational content and the first-order/higher-order monitoring relationships, consciousness continues. HOT has no substrate requirements.

### 3.7 Does scan-and-copy work?

**Yes, with the same duplication caveat as GNWT.** The copy would be conscious and would have your self-model. Two copies would both be "you" in the sense that matters to HOT — both would represent themselves as being you. The theory does not resolve the identity problem of copies.

### 3.8 Biggest weakness

HOT may be explaining self-knowledge or metacognition rather than consciousness itself. The theory implies that a first-order state without higher-order monitoring is unconscious, but substantial evidence suggests rich phenomenal experience can occur without metacognitive access (e.g., in animals, infants, or during states of flow). The "hard problem" remains: why does higher-order monitoring produce subjective experience rather than just being a computational loop? If a thermostat had a second thermostat monitoring it, no one would say the system is conscious — so what additional constraint makes higher-order monitoring sufficient? The theory may be conflating consciousness with the *representation* of consciousness.

### 3.9 Preservation verdict: **5/5**

HOT is maximally favorable for preservation. Consciousness is about representational structure, which is substrate-independent and information-theoretically specifiable. The requirements are a subset of what whole-brain emulation would provide. If HOT is correct, digital preservation is straightforwardly possible.

---

## 4. Predictive Processing / Free Energy Principle — Friston

### 4.1 What IS consciousness under this theory?

The brain is a prediction machine that minimizes free energy (surprise) by maintaining a generative model of the world and updating it through prediction errors. Consciousness arises from the hierarchical predictive processing dynamics of this model — specifically, from the system's capacity to model itself and its own uncertainty. Under the active inference framework, conscious experience corresponds to the content of the generative model's highest-level predictions (the system's "best guess" about the causes of its sensory states). The phenomenal character of experience is determined by the structure of this generative model and the precision-weighting of prediction errors at different levels of the hierarchy. Self-consciousness involves a meta-level generative model of the system's own prediction-generating process.

### 4.2 Is consciousness substrate-independent?

**Unclear, leaning Yes.** The Free Energy Principle itself is substrate-independent — any system with a Markov blanket that persists over time must minimize free energy, by mathematical necessity. This is a formal property, not a biological one. However, Friston and colleagues have argued that there is a distinction between systems that merely *simulate* free energy minimization and those that *actually* minimize it through genuine causal coupling with an environment. A brain emulation running on a computer would be simulating prediction error minimization rather than actually engaging in it — unless it is embodied and coupled to a real environment through sensors and actuators. The theory's position on substrate independence hinges on whether consciousness requires genuine active inference (causal coupling) or merely the right computational dynamics.

### 4.3 Does digital emulation preserve consciousness?

**Maybe.** If the emulation implements genuine hierarchical predictive processing with precision-weighted prediction errors, and is embodied in an environment it must model, then plausibly yes. A brain-in-a-vat running on silicon, receiving simulated sensory input, might qualify if the prediction error dynamics are faithfully reproduced. A disembodied simulation with no environmental coupling is more doubtful — the Free Energy Principle defines conscious systems as those that maintain themselves against entropy through active inference, which requires genuine interaction with a world. The safest path: emulate the brain AND give it a body and environment.

### 4.4 What information must be preserved?

The complete generative model: the hierarchical structure of predictions, the precision-weighting at each level, the learned parameters (effectively, all the knowledge the system has about the world and itself). This maps roughly onto: synaptic weights (predictions), neuromodulatory state (precision-weighting, especially dopaminergic and cholinergic systems), and the hierarchical architecture of cortical columns. Additionally, the temporal dynamics of prediction error propagation must be preserved — the specific time constants at each level of the hierarchy. The embodiment parameters (body model, proprioceptive predictions) are part of the generative model and must be included.

### 4.5 What's the minimum viable "you"?

Your generative model: the complete set of predictions your brain makes about the world, your body, and yourself, along with the precision-weighting profile that determines what you attend to and what you ignore. This includes your perceptual priors, your motor habits, your emotional dispositions (which are precision settings on interoceptive predictions), and your self-model (the predictions you make about your own prediction-making). This is a large but information-theoretically finite specification.

### 4.6 Does gradual replacement work?

**Yes, probably.** If each replacement element maintains the same prediction, prediction-error, and precision dynamics, the generative model is preserved and consciousness continues. The key requirement is preserving the temporal dynamics — prediction errors must propagate at the right speeds.

### 4.7 Does scan-and-copy work?

**Conditionally.** The copy must be embodied — a disembodied generative model that receives no prediction errors will rapidly degrade, as the core mechanism of consciousness under FEP is the ongoing minimization of surprise through active inference. A copy placed in a body (biological or robotic) with appropriate sensory coupling would be conscious and would initially be "you," though it would diverge from the original as it accumulates different prediction errors from different experiences.

### 4.8 Biggest weakness

The Free Energy Principle may be unfalsifiable. As a mathematical framework, it is arguably true by definition for any persisting system — everything that exists minimizes free energy, from rocks to brains. The critical question is whether it has *explanatory* power for consciousness specifically, or whether it is a universal framework that is consistent with consciousness but does not explain it. Systematic critiques (Stegemann, 2024) have identified teleological errors, questionable analogies between thermodynamic and information-theoretic free energy, and the risk that the theory explains everything and therefore nothing. The theory also struggles to distinguish between phenomenal consciousness and sophisticated unconscious inference.

### 4.9 Preservation verdict: **3/5**

Moderately favorable. The theory is nominally substrate-independent, but the embodiment requirement and the simulation-vs-instantiation distinction introduce uncertainty. If you can build an embodied system running a faithful copy of your generative model, preservation is likely possible. But the theory's own commitments raise doubts about whether a disembodied digital copy would be conscious rather than a zombie running the same computations.

---

## 5. Recurrent Processing Theory (RPT) — Lamme

### 5.1 What IS consciousness under this theory?

Consciousness arises from recurrent (feedback) processing within sensory cortical areas. Lamme distinguishes four processing stages: (1) feedforward sweep through the cortical hierarchy — unconscious; (2) lateral interactions — unconscious; (3) recurrent processing within sensory areas (local recurrence) — phenomenally conscious but not reportable; (4) recurrent processing involving frontal areas — conscious and reportable (access consciousness). The critical claim is that stage 3 is already conscious: you can have phenomenal experience from recurrent processing within visual cortex alone, without any involvement of prefrontal areas. This directly contradicts GNWT, which requires prefrontal workspace activation. Attention and consciousness are orthogonal under RPT — you can be conscious of unattended stimuli.

### 5.2 Is consciousness substrate-independent?

**Unclear, leaning Yes.** RPT identifies consciousness with a specific computational process (recurrent processing), not a specific biological substrate. The theory does not explicitly require biological neurons — any system that implements recurrent processing with the right properties should produce consciousness. However, Lamme's formulation is deeply grounded in neuroscience and does not address artificial substrates directly. The key question is whether "recurrent processing" is a substrate-neutral computational description (in which case, substrate-independent) or shorthand for specific neurobiological mechanisms (in which case, possibly not).

### 5.3 Does digital emulation preserve consciousness?

**Probably yes.** If the emulation faithfully implements recurrent processing within sensory areas — feedforward sweeps followed by feedback interactions that create re-entrant loops — it should produce consciousness. The critical requirement is genuine recurrence, not simulated recurrence: the processing must actually loop back, with later-stage outputs modifying earlier-stage representations in real time. A standard simulation could achieve this if the computational graph implements real feedback, not just a feedforward approximation of feedback over multiple timesteps.

### 5.4 What information must be preserved?

The recurrent connectivity within and between cortical areas: which neurons send feedback connections to which, the synaptic weights of those feedback connections, and the temporal dynamics of the recurrent loops. This requires the full cortical connectome (not just feedforward paths but critically the feedback paths), synaptic weights for both feedforward and feedback connections, and the time constants of feedback processing. The relative timing of feedforward and feedback sweeps is essential — consciousness depends on the feedback arriving within a specific temporal window.

### 5.5 What's the minimum viable "you"?

The complete pattern of recurrent connectivity in your cortical sensory and association areas, plus the prefrontal areas needed for reportable consciousness. Your sensory experiences are determined by the specific structure of your recurrent loops — what categories your visual system has learned to carve, what auditory patterns your temporal cortex recognizes, etc. Personal identity requires preserving the learned weights in both feedforward and feedback pathways, plus the higher-level recurrent circuits that encode autobiographical memory and self-representation.

### 5.6 Does gradual replacement work?

**Yes.** As long as replacement elements maintain the same recurrent connectivity and temporal dynamics, consciousness persists. The substrate does not matter; the recurrent processing does.

### 5.7 Does scan-and-copy work?

**Probably yes**, with the same duplication caveat. The copy would implement recurrent processing with your learned connectivity patterns, so it would be conscious and would have your experiential repertoire.

### 5.8 Biggest weakness

RPT's claim that recurrent processing within sensory cortex alone is sufficient for phenomenal consciousness is difficult to test directly. The theory draws heavily on evidence from visual masking experiments, but these experiments are controversial — critics argue that the disruption of recurrent processing also disrupts the subject's ability to form memories of the stimulus, making it impossible to distinguish "no consciousness" from "consciousness without memory." The theory also has limited scope: it was developed for visual consciousness and its extension to other modalities, emotions, and self-consciousness is underspecified.

### 5.9 Preservation verdict: **4/5**

Favorable. RPT is process-based rather than substrate-based, and the required information (recurrent connectivity patterns and temporal dynamics) is within the scope of advanced connectomics. Loses one point because the theory does not explicitly address substrate independence and some ambiguity remains about whether "recurrent processing" is a purely computational concept.

---

## 6. Biological Computationalism — Aru, Milinkovic (2025)

### 6.1 What IS consciousness under this theory?

Consciousness arises from a specific kind of computation that only biological systems currently instantiate: hybrid, scale-inseparable, metabolically grounded processing. Aru and Milinkovic (Neuroscience & Biobehavioral Reviews, December 2025) argue that the brain computes, but not like a digital computer. Neural computation combines discrete events (spikes, synaptic releases) with continuous dynamics (voltage fields, chemical gradients, ionic diffusion). Crucially, this computation is *scale-inseparable*: you cannot separate the algorithm from the substrate, because cause and effect flow simultaneously across scales from ion channels to dendrites to circuits to whole-brain dynamics. The metabolic constraints of biological systems are not incidental but constitutive — energy optimization shapes what the brain can represent and how it learns. Consciousness is what this kind of computation produces; "the algorithm is the substrate."

### 6.2 Is consciousness substrate-independent?

**No, at least not with current technology.** This is the theory's core claim: consciousness is substrate-*dependent* because neural computation cannot be cleanly separated from its biological implementation. Unlike a Turing machine where software is independent of hardware, brain computation is inseparable from the physical dynamics of its wet, fluidic, energy-constrained substrate. A different substrate could in principle support consciousness, but only if it implements the same class of hybrid, scale-inseparable, metabolically grounded computation — which no existing digital architecture does.

### 6.3 Does digital emulation preserve consciousness?

**No**, unless the digital system has three properties current technology lacks: (1) hybrid continuous-discrete computation in real physical time, (2) scale-inseparable architecture shaped by genuine energy constraints, and (3) the ability to continuously modify its own physical structure through its own activity. Standard digital computers fail on all three counts. A conventional brain simulation, no matter how detailed, runs discrete approximations of continuous dynamics on hardware whose computational architecture is entirely divorced from the problem being computed. It would produce the right outputs but not the right kind of processing.

### 6.4 What information must be preserved?

Far more than a connectome. The theory requires preserving: synaptic weights, dendritic morphology (which determines analog integration), the spatial distribution of ion channels and receptors, extracellular ionic concentrations, glial cell states, metabolic parameters (ATP availability, glucose gradients), neuromodulatory tone, and the physical geometry of the tissue (because computation is scale-inseparable, the spatial arrangement matters). Essentially, you need a molecular-resolution snapshot of the brain, not just a wiring diagram.

### 6.5 What's the minimum viable "you"?

A molecular-level reconstruction of your brain's tissue that is capable of being re-instantiated in a substrate that supports the same class of hybrid, scale-inseparable computation. Under this theory, there may be no practical way to specify "you" in a compact format — the specification *is* the physical brain at molecular resolution, and it must be run on appropriate hardware. This is the most demanding preservation requirement of any theory considered here.

### 6.6 Does gradual replacement work?

**Only if replacements implement biological computation.** Silicon neurons that merely mimic input-output behavior would fail — they would disrupt the scale-inseparable, continuous-discrete dynamics. Replacement elements would need to be artificial biological systems (bioengineered neurons, perhaps) that participate in the same fluidic, metabolically constrained, multiscale dynamics as the original tissue. Synthetic biology might eventually achieve this; conventional neuroprosthetics would not.

### 6.7 Does scan-and-copy work?

**No.** A scan captures information but loses the physical dynamics. Running that information on a digital computer produces a functional replica without consciousness, because the computation is of the wrong kind. Running it on a biological or bio-hybrid substrate might work, but that is not what "scan-and-copy" typically means.

### 6.8 Biggest weakness

The theory is new (December 2025) and has not been empirically tested. Its core claim — that scale-inseparable computation is necessary for consciousness — is difficult to falsify because it is unclear what experiment could distinguish between "the brain's computational output" and "the brain's computational process" as the relevant variable. The theory risks being a sophisticated argument from ignorance: "we don't know how digital systems could be conscious, therefore they can't be." It also faces the objection that many biological computations *are* effectively separable across scales (reflexes, spinal circuits, retinal processing) — the claim that all consciousness-relevant computation is scale-inseparable requires empirical support. Additionally, if consciousness truly requires this kind of computation, the theory offers almost no hope for preservation — which is not a weakness of the theory, but is worth noting for this analysis.

### 6.9 Preservation verdict: **1/5**

Tied with IIT for the least favorable theory. Digital preservation is explicitly ruled out. Even biological preservation requires molecular-resolution reconstruction on an appropriate biological or bio-hybrid substrate — a vastly harder problem than digital emulation.

---

## 7. Orchestrated Objective Reduction (Orch OR) — Penrose, Hameroff

### 7.1 What IS consciousness under this theory?

Consciousness arises from quantum computations in microtubules within neurons. Penrose argues that consciousness involves non-computable processes — aspects of understanding (particularly mathematical insight and the Godelian argument) that no algorithmic process can replicate. Hameroff proposes that microtubules (structural proteins inside neurons) are the physical site where these quantum computations occur. Specifically, tubulin proteins in microtubules exist in quantum superposition, and consciousness occurs when these superpositions undergo "objective reduction" (OR) — a quantum gravity-induced collapse of the wave function that is not random but influenced by the geometry of spacetime. This collapse is "orchestrated" by synaptic inputs and biological processes, connecting quantum events to neural computation. Each OR event is a moment of conscious experience — a "quantum of consciousness."

### 7.2 Is consciousness substrate-independent?

**No.** Orch OR requires quantum coherence in microtubules, which are specific biological structures. The quantum gravity-mediated collapse is tied to the physical mass and geometry of tubulin molecules in their specific arrangement within microtubules. Digital computation is explicitly excluded by Penrose's argument: consciousness is non-computable, meaning no Turing machine (and therefore no digital computer) can produce it, regardless of how sophisticated the program. This is not a practical limitation but a fundamental mathematical one — consciousness involves processes that are not algorithmic.

### 7.3 Does digital emulation preserve consciousness?

**No, categorically.** This is the strongest possible denial among all theories. Penrose's non-computability argument means that no digital emulation, no matter how detailed, can produce consciousness. A perfect digital simulation of a brain would be a zombie — behaviorally identical but lacking any inner experience. The relevant quantum processes cannot be simulated on a classical computer (and even a quantum computer would need to implement the specific OR process, not merely quantum computation in general).

### 7.4 What information must be preserved?

Quantum states of tubulin proteins within microtubules, the specific geometry of microtubule networks within each neuron, synaptic inputs that orchestrate quantum coherence, and the gravitational self-energy of the superposed tubulin conformations. This is beyond even molecular-level preservation — it requires quantum-state preservation, which is subject to decoherence and may be impossible to capture in a static scan. Additionally, the classical neural architecture (connectome, synaptic weights) must be preserved because it orchestrates the quantum processes.

### 7.5 What's the minimum viable "you"?

The complete quantum state of your microtubule networks plus the classical neural architecture. This is the most demanding specification of any theory — it requires preserving information that is, by current understanding of quantum mechanics, impossible to perfectly copy (no-cloning theorem). Under Orch OR, there may be a fundamental physical limit on how completely "you" can be specified.

### 7.6 Does gradual replacement work?

**Only with biological replacements that support quantum coherence in microtubules.** Silicon neurons do not have microtubules and cannot support the required quantum processes. Even biological replacements would need to establish quantum coherence with the surrounding microtubule network. This is an open question — it depends on whether quantum coherence in microtubules can be maintained across boundaries between original and replacement tissue.

### 7.7 Does scan-and-copy work?

**No, on multiple grounds.** (1) The no-cloning theorem prevents perfect copying of quantum states. (2) Even if a perfect copy were somehow made, running it on a digital computer would not produce consciousness because consciousness is non-computable. (3) Even running it on a quantum computer would not work unless that quantum computer specifically implements objective reduction in microtubule-like structures.

### 7.8 Biggest weakness

The theory's empirical foundations are contested. Critics (Tegmark, 2000) calculated that quantum coherence in microtubules would decohere in ~10^-13 seconds at brain temperature — far too fast for any neural process. While Hameroff has cited recent experiments showing quantum effects in microtubules (Babcock et al. 2024, energy migration over ~6.6nm), these effects are orders of magnitude below what Orch OR requires. The non-computability argument rests on a controversial interpretation of Godel's theorems that most logicians reject. The theory makes few testable predictions and has been criticized as unfalsifiable. The 2025 COGITATE results did not test Orch OR, and no major experimental program is currently designed to validate or refute it. Most neuroscientists and physicists consider Orch OR to be outside the scientific mainstream.

### 7.9 Preservation verdict: **0/5**

The most hostile possible theory for preservation. Digital emulation is ruled out by mathematical argument, not just practical difficulty. Quantum states cannot be copied. If Orch OR is correct, consciousness preservation in any form other than maintaining the living biological brain may be fundamentally impossible.

---

## 8. Attention Schema Theory (AST) — Graziano

### 8.1 What IS consciousness under this theory?

Consciousness is the brain's simplified internal model of its own attention process. Just as the brain constructs a body schema (a simplified model of the body's position and state), it constructs an "attention schema" — a simplified model of the process by which the brain selectively enhances some signals over others. When you report being conscious, you are reporting the contents of this internal model. The attention schema is necessarily simplified and somewhat inaccurate, which is why consciousness has the mysterious, seemingly non-physical quality it does — it is based on a model that omits the mechanistic details of attention (electrochemistry, spike rates) and describes attention in terms of a subjective "awareness" that "has" experiences. Consciousness is not a metaphysical property but an internal representation — a useful fiction that the brain constructs for the purpose of monitoring and controlling its own attention.

### 8.2 Is consciousness substrate-independent?

**Yes.** AST is explicitly functionalist and mechanistic. Graziano has published on engineering artificial consciousness using AST as a foundation. The theory requires: (1) an attention mechanism, (2) an internal model of that attention mechanism. Any system that implements these — biological, silicon, or otherwise — would claim to be conscious (and, under the theory, *would be* conscious in the only sense the word means). The substrate is irrelevant; the computation is what matters.

### 8.3 Does digital emulation preserve consciousness?

**Yes.** AST is designed to be implementable in artificial systems. A digital system with: (1) selective signal enhancement (attention), (2) an internal model that describes its own attention process in simplified terms, and (3) the ability to use this model for prediction and control, would be conscious. Graziano's lab has built neural network agents with attention schemas that demonstrate improved attention control. A whole-brain emulation would trivially satisfy these requirements.

### 8.4 What information must be preserved?

The attention mechanisms (what the system can attend to and how it selects), the attention schema (the learned internal model of attention), and the higher-level cognitive systems that use the attention schema for prediction, planning, and social cognition. This requires: cortical connectivity for attentional networks (roughly, the frontoparietal attention network), the learned parameters of the attention schema, and the connection between the attention schema and self-model/social cognition systems. This is a relatively modest requirement — less than a full connectome, in principle, though in practice the attention schema is intertwined with many other brain systems.

### 8.5 What's the minimum viable "you"?

Your specific attention schema: the particular way your brain models its own attention, including your attentional biases, your metacognitive habits, and your self-model as a conscious agent. Plus the cognitive contents that your attention operates over — your memories, skills, and knowledge. AST suggests a relatively compact specification of "you": the internal model plus the data it operates on. Personal identity is determined by the contents of the self-model, which is a learned data structure.

### 8.6 Does gradual replacement work?

**Yes.** As long as the attention schema and attention mechanisms are functionally preserved, consciousness continues. The substrate of the replacement is irrelevant.

### 8.7 Does scan-and-copy work?

**Yes.** The copy would have your attention schema and would model itself as being you. It would be conscious. The duplication problem applies as with GNWT and HOT.

### 8.8 Biggest weakness

AST may explain the *belief* in consciousness rather than consciousness itself. Under AST, saying "I am conscious" is just the output of an internal model — there is no fact of the matter about whether the system "really" experiences anything. This is either a feature (it dissolves the hard problem) or a fatal flaw (it denies the most obvious datum of human existence — that experience exists). Many philosophers argue that AST is an eliminativist theory that redefines consciousness as a useful illusion, then declares the problem solved by explaining the illusion. If consciousness is genuinely real (as most people believe), AST does not explain it — it explains it away. The theory also has difficulty accounting for the specific qualitative character of experience (why does red look like *that*?) since the attention schema is a simplified model that abstracts away from the details.

### 8.9 Preservation verdict: **5/5**

Maximally favorable. AST is explicitly designed to be substrate-independent and artificially implementable. Under AST, a good enough digital emulation *is* you in every sense the word means. The only risk is the meta-level one: if AST is wrong about what consciousness is, then what it preserves may not be what you care about preserving.

---

## Comparison Matrix

| Criterion | IIT 4.0 | GNWT | HOT | FEP/PP | RPT | Bio. Comp. | Orch OR | AST |
|---|---|---|---|---|---|---|---|---|
| **Substrate-independent?** | No | Yes | Yes | Unclear | Unclear/Yes | No | No | Yes |
| **Digital emulation?** | No | Yes | Yes | Maybe | Probably | No | No | Yes |
| **Minimum info needed** | Full causal architecture | Connectome + weights + dynamics | Connectome + weights (both levels) | Generative model + precision weights + embodiment | Recurrent connectivity + timing | Molecular-level snapshot | Quantum states + connectome | Attention schema + self-model + memories |
| **Gradual replacement?** | Only if causal-identical | Yes | Yes | Probably | Yes | Only if biologically equivalent | Only biological | Yes |
| **Scan-and-copy?** | No | Yes | Yes | Conditional (needs body) | Probably | No | No | Yes |
| **Biggest weakness** | Intractability + unfolding argument | Conflates access with phenomenal consciousness | Conflates metacognition with experience | Possibly unfalsifiable | Limited scope (vision-centric) | New, untested, possibly argument from ignorance | No empirical support for quantum coherence at required scales | May explain belief in consciousness, not consciousness itself |
| **Preservation verdict** | 1/5 | 4/5 | 5/5 | 3/5 | 4/5 | 1/5 | 0/5 | 5/5 |

---

## Consensus Analysis

### Where theories agree

1. **Feedforward processing is not sufficient for consciousness.** Every theory agrees on this. IIT says feedforward networks have Phi = 0. GNWT requires re-entrant broadcast. HOT requires higher-order monitoring (inherently recurrent). FEP requires hierarchical prediction error loops. RPT defines consciousness as recurrent processing. Even AST requires feedback from the attention schema to the attention mechanism. This is the strongest consensus in the field and it is empirically supported: feedforward processing alone (as in the initial ~100ms of visual processing) does not produce conscious experience.

2. **Temporal dynamics matter.** All theories agree that consciousness is not a static property of a network but depends on dynamic processing over time. IIT requires specific causal dynamics. GNWT requires ignition events. RPT requires feedback within specific temporal windows. FEP requires ongoing prediction error minimization. This means any preservation strategy must capture temporal parameters, not just static connectivity.

3. **Consciousness requires integration across components.** Whether through workspace broadcast (GNWT), higher-order monitoring (HOT), recurrent processing (RPT), integrated information (IIT), or predictive model coherence (FEP), all theories require that information be combined across processing streams rather than remaining isolated.

### Where theories diverge

1. **Substrate independence is the central fault line.** Four theories (GNWT, HOT, AST, and arguably RPT) are substrate-independent. Three (IIT, Bio. Comp., Orch OR) are substrate-dependent in different ways and for different reasons. FEP straddles the line. This is the single most important question for preservation, and there is no consensus.

2. **What counts as consciousness.** GNWT defines consciousness as access (information globally available for report and flexible use). RPT and IIT define it as phenomenal experience (what it is like). HOT tries to bridge the two. AST redefines consciousness as an internal model. These are not minor terminological differences — they determine what a preservation strategy is even trying to preserve.

3. **The role of the prefrontal cortex.** GNWT and HOT place consciousness squarely in prefrontal-mediated processes. RPT explicitly denies this, placing phenomenal consciousness in sensory cortex alone. The COGITATE results (2025) weakened the prefrontal case. This matters for preservation because it determines how much of the brain's architecture is consciousness-relevant.

4. **Whether phenomenal consciousness is real or a useful model.** AST and (arguably) HOT suggest that the "hard problem" is dissolved rather than solved — consciousness is a representation, not a fundamental property. IIT, Orch OR, and RPT treat phenomenal consciousness as a real, irreducible feature of the world. This determines whether a preserved copy that reports being conscious *is* conscious or merely *claims* to be.

---

## Risk Assessment

### If you had to bet your life

The question is: which preservation strategy gives you the best chance of survival across the broadest range of theories?

**Strategy 1: High-fidelity whole-brain emulation on digital hardware**
- Works under: GNWT, HOT, AST, probably RPT (4 theories)
- Fails under: IIT, Bio. Comp., Orch OR (3 theories)
- Unclear: FEP (1 theory)
- Success probability (theory-weighted): ~50-60%, assuming theories are roughly equally likely

**Strategy 2: Gradual neuron-by-neuron replacement with functionally identical silicon**
- Works under: GNWT, HOT, AST, RPT, probably FEP (5 theories)
- Fails under: IIT (unless causal-identical), Bio. Comp. (unless biologically equivalent), Orch OR (3 theories)
- This is slightly better than scan-and-copy because it preserves continuity and avoids the duplication problem.
- Success probability: ~55-65%

**Strategy 3: Biological preservation (cryonics → future revival)**
- Works under: All 8 theories, *if* the preservation is good enough and the revival technology exists
- Risk: The "if" is enormous. Current cryonics protocols cause significant tissue damage. But this is a practical risk, not a theoretical one — no theory says a revived biological brain would lack consciousness.
- Success probability: Unknown (dependent on future technology), but ~100% in theory-space

**Strategy 4: Gradual replacement with bio-hybrid components (synthetic neurons with biological computation properties)**
- Works under: All 8 theories if the components truly replicate biological computation
- This is the theoretically safest non-biological strategy, but the technology does not exist and may not for decades.
- Success probability: ~80-90% in theory-space, ~0% with current technology

### My bet

**If forced to choose today:** Biological preservation (cryonics), with the explicit plan that future revival should use gradual bio-hybrid replacement rather than digital emulation. This hedges against the substrate-dependent theories without betting everything on technology that may never work.

**If forced to choose a digital strategy:** Gradual replacement over scan-and-copy, every time. Gradual replacement: (a) avoids the duplication problem entirely, (b) preserves continuity of consciousness under all substrate-independent theories, (c) gives you feedback — if at some point during replacement you stop feeling conscious, the process can theoretically be reversed. Scan-and-copy is a one-way door: you destroy the original and hope the copy is you.

**The philosophical risk nobody talks about:** Even under the favorable theories, scan-and-copy creates a new person who *thinks* they are you. Under functionalism, there is no fact of the matter about whether they are "really" you — functional identity is all there is. But from your first-person perspective, you are dead and someone with your memories wakes up. The philosophical literature has not resolved this, and the theories that rate 5/5 for preservation achieve that score partly by deflating what personal identity means. If you care about *your* subjective stream of experience continuing (not just a person with your memories existing), then even the best theories offer less comfort than their preservation scores suggest.

---

## Key Open Experiments

### Experiments that could distinguish between theories in ways that matter for preservation

**1. The Split-Brain Emulation Test**
Design: Create a partial brain emulation — half biological, half digital — connected via a high-bandwidth interface. Test whether the system reports unified consciousness, split consciousness, or no consciousness in the digital half.
Distinguishes: IIT vs. GNWT/HOT. Under IIT, the digital half has low Phi and consciousness is restricted to the biological half. Under GNWT, if the workspace spans both halves, unified consciousness should emerge regardless of substrate.
Feasibility: 10-20 years. Requires advances in brain-computer interfaces and partial emulation.

**2. The Anesthesia Response Test for Artificial Systems**
Design: Build an artificial system that implements the architecture specified by a theory (e.g., a global workspace AI) and test whether anesthetic agents that affect consciousness in biological brains affect the system's processing in analogous ways.
Distinguishes: Bio. Comp. vs. functionalist theories. If consciousness depends on biological computation, anesthetics should not affect artificial systems (they work on specific biological mechanisms). If functionalism is correct, artificial systems implementing the right architecture should show analogous disruption when their equivalent mechanisms are disrupted.
Feasibility: 5-10 years. Partially achievable with current AI systems.

**3. The Gradual Replacement Phenomenology Study**
Design: In animal models, gradually replace cortical neurons with silicon equivalents that match input-output behavior. At each stage, test behavioral and neural signatures of consciousness (e.g., ignition, recurrent processing, global synchronization).
Distinguishes: Substrate-dependent vs. substrate-independent theories. If consciousness signatures persist with increasing silicon fraction, substrate-independent theories are supported. If they degrade despite preserved behavior, substrate-dependent theories gain evidence.
Feasibility: 15-30 years. Requires neuroprosthetic technology far beyond current capability.

**4. The Quantum Coherence Disruption Experiment**
Design: Selectively disrupt quantum coherence in microtubules (e.g., through targeted deuterium substitution or specific electromagnetic interference) while preserving classical neural function. Test whether consciousness is affected.
Distinguishes: Orch OR vs. all other theories. If disrupting quantum coherence disrupts consciousness without affecting classical neural computation, Orch OR is supported. If consciousness is unaffected, Orch OR is ruled out.
Feasibility: 5-15 years. Partially achievable now, though specificity of intervention is challenging.

**5. The Phi vs. Report Dissociation Experiment**
Design: Construct a system where calculated Phi is high but the system has no global workspace (no broadcast, no report capability), and another where Phi is low but the global workspace is intact. Test behavioral and neural signatures in both.
Distinguishes: IIT vs. GNWT directly. Each theory predicts consciousness in a different system. This is essentially what the COGITATE collaboration attempted, but with more targeted designs.
Feasibility: 5-10 years with improved Phi approximation algorithms.

**6. The Scale-Inseparability Test**
Design: Build two emulations of the same neural circuit: one that simulates continuous dynamics at molecular resolution, and one that uses discrete approximations (standard digital simulation). Compare their outputs and, if biological test systems are available, compare to the biological original's behavior under novel/edge-case conditions.
Distinguishes: Bio. Comp. vs. standard functionalism. If the discrete approximation produces identical behavior under all conditions, scale-inseparability is not computationally relevant (even if it is physically real). If behavior diverges under novel conditions, scale-inseparable dynamics are computationally meaningful.
Feasibility: 5-10 years for small circuits.

---

## Conclusion

The question "can consciousness be digitally preserved?" does not have a single answer. It has eight answers (at minimum), corresponding to eight different theories of what consciousness is. Four theories say yes, three say no, and one says maybe.

The uncomfortable truth is that we do not know which theory is correct, and the experiments that could decide are years to decades away. The COGITATE results (2025) damaged both leading theories (IIT and GNWT) without killing either. Biological computationalism (2025) has introduced a serious new challenge to substrate independence that has not yet been empirically tested.

For anyone considering consciousness preservation as a practical matter, the key insight is this: the substrate-independent theories that favor preservation tend to be the ones that deflate consciousness (AST says consciousness is a model; GNWT identifies it with access; HOT identifies it with self-monitoring). The theories that take phenomenal consciousness most seriously as an irreducible feature of reality (IIT, Orch OR, Bio. Comp.) are exactly the ones that make preservation hardest or impossible. There is a deep tension between taking consciousness seriously and believing it can be preserved, and no amount of technological progress can resolve what is fundamentally a theoretical disagreement about what consciousness is.

The safest bet, across all theories, remains biological preservation with future bio-hybrid replacement. The riskiest bet is destructive scan-and-copy to digital hardware. Everything else falls somewhere in between.
