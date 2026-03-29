# Consciousness Preservation Landscape Map

*Last updated: 2026-03-27*

A practical reference for understanding who is doing what in consciousness preservation, brain-computer interfaces, connectomics, and whole brain emulation. The question: where are the gaps, and where could a systems/security engineer plug in?

---

## 1. Preservation-Adjacent Companies

### Until Labs (formerly Cradle)
- **Website:** https://www.untillabs.com/
- **What they do:** Reversible cryopreservation. Near-term: organ cryopreservation for transplant (hearts, lungs, livers currently must reach recipients within 4-12 hours). Long-term: whole-body reversible cryopreservation.
- **Founded by:** Laura Deming (longevity VC pioneer) and Hunter C. Davis (chief scientist)
- **Funding:** $48M seed (2024) + $58M Series A (Sept 2025) = **$106M+ total**. Series A led by Founders Fund, with Lux Capital and Field Ventures.
- **Key result:** Recovered electrical activity in cryopreserved and rewarmed rodent neural tissue slices (Feb 2024). This was the proof of concept.
- **Roadmap:** Preserved synaptic function in neural samples -> large-animal organ cryopreservation -> human organ preservation clinical trials -> reversible whole-body cryopreservation in animal models.
- **Open problems:** Scaling from tissue slices to whole organs. Rewarming uniformly without thermal stress. Cryoprotectant toxicity at whole-organ scale.
- **Relevance:** The most well-funded company directly working on reversible preservation. If they solve organ cryopreservation, the path to whole-body becomes clearer.

### Nectome
- **Website:** https://nectome.com/
- **What they do:** Brain preservation via aldehyde-stabilized cryopreservation (ASC). Not reversible — the bet is that future technology can extract information from a preserved connectome.
- **Key people:** Borys Wrobel, Aurelia Song (also CSO at Eon Systems)
- **Funding:** ~$1M from Y Combinator (2018), undisclosed additional funding
- **Controversy:** MIT cut ties in 2018 after reports the technology would require physician-assisted death. The company pivoted to post-mortem preservation.
- **2026 status:** Published bioRxiv preprint (March 2026) — "Ultrastructural preservation of a whole large mammal brain with a protocol compatible with human physician-assisted death." Preserved a pig brain with intact membranes, visible mitochondria, and preserved synapses when perfusion initiated within 14 minutes of death.
- **Next step:** Planning to invite terminally ill patients in Oregon (where physician-assisted death is legal) to undergo the preservation protocol. Patients would donate brain and body for research.
- **Open problems:** No one knows how to read information from a preserved brain. No reversal path. Ethical and regulatory challenges are massive.
- **Relevance:** The preservation side may be nearly solved for their approach. The information extraction side is entirely unsolved and is where CS/engineering talent matters.

### Alcor Life Extension Foundation
- **Website:** https://www.alcor.org/
- **What they do:** Cryonics — long-term cryopreservation of legally deceased patients at -196C in liquid nitrogen.
- **Location:** Scottsdale, Arizona
- **Key people:** Max More (former president), Patrick Harris (current president)
- **Members/patients:** ~1,000 members, ~248 patients as of early 2026. November 2025 broke their all-time record for new member signups.
- **Funding:** Membership dues cover ~1/3 of budget. Donations and case income cover the rest. Major gift from Rothblatt family in 2025 (one of largest individual donations ever).
- **2025-2026 updates:** Full website rebuild, new member portal, in-house CT scanner operational, DART standby/stabilization/transport network expanded (new traveling surgeon, portable washout system). European expansion underway with Dr. Trond Hegle. Alcor Canada received official charity status.
- **Cost:** $200K whole body, $80K neuro (brain only)
- **Open problems:** No demonstrated reversal. Quality of preservation varies depending on response time. Organizational sustainability over centuries.

### Cryonics Institute
- **Website:** https://cryonics.org/
- **What they do:** Same as Alcor — cryopreservation of legally deceased patients. Nonprofit, member-owned.
- **Location:** Clinton Township, Michigan
- **Key people:** Dennis Kowalski (president)
- **Members/patients:** ~1,995 members, ~276 patients (as of Oct 2025)
- **Cost:** $28,000 minimum (unchanged since 1976 — would be ~$170K inflation-adjusted)
- **2025-2026 updates:** Partnered with Suspended Animation, Inc. to offer whole-body Field Cryoprotection (FCP) — replacing blood with cryoprotectant at the patient's location rather than during cold transport.
- **Open problems:** Same as Alcor. Lower cost means potentially lower preservation quality, though this is debated.

### Tomorrow Bio
- **Website:** https://www.tomorrow.bio/
- **What they do:** Cryonics services in Europe, expanding to US.
- **Location:** Berlin, Germany
- **Founded by:** Dr. Emil Kendziorra and Fernando Azevedo Pinheiro (2020)
- **Members/patients:** 800+ members, 20 humans and 10 pets preserved. Nearly 400 new members in 2024 alone — **fastest-growing cryonics organization globally.**
- **Contract value:** >EUR160M total across all member contracts
- **Funding:** EUR5M seed round (May 2025), co-led by Blast.Club and Truventuro. Angel investors and HNW individuals.
- **2025-2026 updates:** Expanding SST (Standby, Stabilization, Transport) volunteer teams across Europe and US. Building more ambulances. US bases planned in New York, California, Florida. 2026 Quality Improvement Plan focuses on faster logistics, new cryoprotectants, and rewarming research.
- **Open problems:** Same as all cryonics: no reversal. Additionally, operating across European jurisdictions with varying legal frameworks is complex.

### Sparks Brain Preservation (formerly Oregon Cryonics)
- **Website:** https://sparksbrain.org/
- **What they do:** Brain-only preservation. Focus on highest-quality brain preservation using aldehyde fixation + cryopreservation. Different approach from whole-body cryonics.
- **Location:** Salem, Oregon (purpose-built 20,000 sq ft facility completed 2025)
- **Key people:** Jordan Sparks, D.M.D. (executive director)
- **Stats:** 41 members, 20 patient brains preserved, 11 pet animals. Have practiced procedures on hundreds of donated human bodies. Access to 156 donated human brains.
- **Funding:** ~$7M facility construction
- **Partner:** Apex Neuroscience (research entity)
- **Relevance:** More research-oriented than traditional cryonics orgs. Aldehyde fixation arguably better preserves ultrastructure than straight cryopreservation, at the cost of irreversibility.

### Other Cryonics Organizations
- **KrioRus** (Russia) — 103 patients. Status uncertain given geopolitical situation.
- **Shandong Yinfeng** (China) — 29 patients. First and only cryonics organization in China.
- **Southern Cryonics** (Australia) — 4 patients as of 2025. Small but growing.

### Global Cryopreservation Stats
~500-650 individuals cryopreserved worldwide as of mid-2025.

---

## 2. Brain-Computer Interface Companies

### Neuralink
- **Website:** https://neuralink.com/
- **What they do:** Invasive BCI — N1 implant with 1,024 electrodes on 64 ultra-thin threads, inserted by surgical robot.
- **Funding:** $363M+ (2021 round). Valued at ~$5B+ as of 2024.
- **PRIME trial status (2025-2026):**
  - 5+ US patients implanted (including paralyzed veteran "RJ" at Miami, April 2025)
  - 7 UK patients implanted at UCLH's National Hospital for Neurology and Neurosurgery (Oct-Dec 2025)
  - Expanding to Canada, Germany, UAE. Goal: 20-30 new participants globally by end of 2025.
- **Key results:** Patients control computers/smartphones with thoughts. Mind-controlled robotic arm demonstrated (position, gestures, precision grip from brain signals alone).
- **Engineering roles:** Actively hiring software engineers (Python, C++, C, Rust). Roles include BCI application development, real-time signal processing, surgical robot software. Linux and embedded systems experience valued.
- **Open problems:** Thread retraction (occurred in first patient, mitigated in subsequent). Long-term biocompatibility. Scaling channel count. Battery life. Wireless bandwidth.
- **Relevance to preservation:** Not directly preservation-focused, but the highest-bandwidth bidirectional brain interface could eventually be relevant for brain state readout.

### Synchron
- **Website:** https://synchron.com/
- **What they do:** Minimally invasive BCI — Stentrode device deployed via blood vessels (endovascular approach, no open brain surgery). Stent-like mesh with electrodes sits in the motor cortex's blood vessel.
- **Key people:** Dr. Tom Oxley (CEO, co-founder)
- **Funding:** $145M+ total
- **COMMAND trial results (2024):** All 6 patients met primary safety endpoint — no device-related serious adverse events at 12 months. 100% accurate deployment. Brain signals successfully captured and converted to digital outputs for computer control.
- **FDA status:** Working toward pivotal trial for premarket approval. In ongoing FDA discussions about endpoints. Pivotal trial expected to take a couple years before submission.
- **Open problems:** Lower spatial resolution than penetrating electrodes (records from outside blood vessel walls). Channel count limited. Trade-off: much safer implantation but less signal.

### Precision Neuroscience
- **Website:** https://precisionneuro.io/
- **What they do:** Layer 7 Cortical Interface — thin-film electrode array placed on brain surface (subdural), no penetration. Up to 1,024 platinum electrodes per array.
- **Key people:** Michael Mager (co-founder, formerly at Neuralink), Ben Rapoport (co-founder, neurosurgeon)
- **Funding:** $93M+ total
- **Clinical progress:** FDA 510(k) clearance (April 2025) for recording, monitoring, and stimulating on brain surface for up to 30 days. Tested in 68+ patients at 4+ major US institutions as of Jan 2026.
- **2026 results:** Johns Hopkins researchers achieved real-time 2D cursor control and speech classification in 4 patients.
- **Partnership:** Medtronic partnership (Jan 2026) to integrate Layer 7 with StealthStation surgical navigation platform.
- **Open problems:** Currently cleared for 30-day implantation only (not permanent). Lower resolution than penetrating arrays for single-neuron recording.

### BISC (Biological Interface System to Cortex)
- **Key paper:** Nature Electronics, Dec 2025 — "A wireless subdural-contained brain-computer interface with 65,536 electrodes and 1,024 channels"
- **Team:** Columbia University (Ken Shepard, senior author), New York Presbyterian, Stanford, UPenn
- **What it is:** Single silicon chip, 50 um thick, 3 mm^3 total. Slides between brain and skull like wet tissue paper. 65,536 electrodes, 1,024 simultaneous recording channels, 16,384 stimulation channels. Wireless power and data.
- **Status:** Academic/research stage. Short-term intraoperative human studies underway.
- **Significance:** Highest electrode density of any BCI by far. If this can become a chronic implant, it could be transformative.

### Paradromics
- **Website:** https://www.paradromics.com/
- **What they do:** Connexus BCI — penetrating microelectrode array focused on speech restoration. 200+ bits/second information transfer in pre-clinical models.
- **Key people:** Matt Angle (CEO)
- **FDA status:** IDE approval (Nov 2025) for Connect-One Early Feasibility Study. First company to receive IDE for speech restoration with fully implantable BCI.
- **Trial sites:** UC Davis, Mass General, University of Michigan
- **Trial plan:** 2 patients initially, Q1 2026. 7.5mm wide device inserted 1.5mm into brain.
- **Open problems:** Very early clinical stage. Small trial size.

### Blackrock Neurotech
- **Website:** https://blackrockneurotech.com/
- **What they do:** Utah Array — the gold standard penetrating microelectrode array. Up to 128 silicon electrodes. Only FDA-cleared high-channel microelectrode platform for single-neuron recording in BCI applications.
- **History:** Based on technology invented by Richard Normann at University of Utah. In human use since 2004. Has been used in most major BCI research studies.
- **2025-2026 updates:** Partnered with Cognixion for AR-enabled BCI headset (Axon-R, May 2025). Expanding in-home trials for paralyzed users. Developing "Neuralace" — flexible lattice for less invasive cortical coverage.
- **Open problems:** Utah arrays degrade over time (chronic immune response). Rigid silicon doesn't conform to brain curvature. Limited to 128 channels per array.
- **Relevance:** The workhorse of invasive BCI research. Most published BCI results use Blackrock hardware.

### Other Notable BCI Efforts
- **OpenBCI** (https://openbci.com/) — Open-source non-invasive EEG hardware and software. Good entry point for hobbyists/researchers.
- **Cognixion** — AR headset BCI (partnered with Blackrock)
- **Microsoft Research** — BCI project aiming to make BCI accessible to general population
- **Alljoined** — Startup at intersection of BCI and ML, hiring interns for EEG/deep learning work

---

## 3. Connectomics & Emulation Labs

### FlyWire / Princeton Connectome
- **Website:** https://flywire.ai/
- **What they did:** Complete connectome of an adult female Drosophila (fruit fly) brain. Published in Nature, October 2024.
- **Scale:** 139,255 proofread neurons, 50+ million synapses, 8,453 cell types identified (4,581 newly discovered). 98% of neurons typed.
- **Consortium:** 127 institutions. 33 person-years of proofreading contributed by researchers and citizen scientists.
- **Data access:** Codex (Connectome Data Explorer) — free, 10,000+ registered users, thousands of searches daily.
- **2025 update:** Flatiron Institute won FlyWire's Ventral Nerve Cord Matching Challenge (aligning neural networks between male and female flies).
- **Relevance:** This is the foundational dataset that enabled Eon Systems' fly brain emulation. Proves that community-driven connectomics at organism scale is possible.

### MICrONS / Allen Institute
- **Website:** https://www.microns-explorer.org/
- **What they did:** Functional connectomics of mouse visual cortex. Published in Nature special issue, April 2025.
- **Scale:** ~75,000 neurons imaged with calcium imaging (functional activity), co-registered with EM reconstruction of 200,000+ cells, 500 million synapses, 4km of axons from 1 cubic millimeter of mouse brain. 1.4 petabytes of data.
- **Consortium:** Allen Institute, Baylor College of Medicine, Princeton. Funded by IARPA MICrONS program.
- **Significance:** First dataset combining functional recording with dense connectivity at this scale in mammalian cortex. You can see what neurons do AND how they're wired.
- **Data access:** Open access via MICrONS Explorer.

### Google Connectomics + Lichtman Lab (Harvard)
- **Website:** https://research.google/teams/connectomics/
- **What they did:** H01 dataset — 1.4 petabyte volume of a small sample of human cerebral cortex (half a grain of rice). Published in Science, 2024.
- **Scale:** ~16,000 neurons, 32,000 glia, 8,000 blood vessel cells (~57,000 cells total), 150 million synapses.
- **Key people:** Jeff Lichtman (Harvard), Viren Jain (Google)
- **Method:** 5,000+ slices at 30nm thickness, 326 days of image acquisition with multibeam scanning electron microscope.
- **Discoveries:** Rare axons connected by up to 50 synapses (previously unseen). Interactive viewer accessed 100,000+ times.
- **Open problems:** This was a tiny fragment. Scaling to whole human brain at this resolution would take millions of years with current technology.

### E11 Bio
- **Website:** https://www.e11.bio/
- **What they do:** Building PRISM — a scalable connectomics platform combining protein barcoding, expansion microscopy, and AI-driven segmentation. Goal: reduce connectomics cost by 95% by eliminating human proofreading.
- **Location:** Alameda, California
- **Structure:** Focused Research Organization (FRO) under Convergent Research (incubator funded by Eric Schmidt, Wendy Schmidt, Ken Griffin via Schmidt Futures).
- **Scaling goal:** 10x increase in barcode diversity and image volume per year. Entire mouse connectome target within 5 years.
- **2025 milestone:** Initial preprint with beta methods, followed by periodic release of increasingly large optical connectomic data.
- **Data:** Brain circuit mapping dataset hosted on AWS Open Data.
- **Relevance:** If PRISM works at scale, it dramatically accelerates the path from organism to connectome. The AI segmentation pipeline is where CS/ML engineers contribute.

### Eon Systems
- **Website:** https://eon.systems/
- **What they do:** Whole brain emulation. Currently: fly brain. Next: mouse brain. Long-term: human mind upload.
- **Key people:** Michael Andregg (CEO, 3x founder), Aurelia Song (CSO, also at Nectome, studied under Marvin Minsky at MIT), Philip Shiu (first fly brain upload, featured in Nature), Dr. Alex Wissner-Gross (co-founder)
- **Funding:** $3.5M seed, led by Protocol Labs with participation from Larry Page's family office.
- **Key result (2024-2025):** First whole-brain emulation in a simulated body producing multiple behaviors. Used FlyWire connectome (125,000 neurons, 50M synaptic connections) + NeuroMechFly v2 framework + MuJoCo physics. The digital fly responds to light, navigates, grooms, walks, and feeds — no hand-coded behaviors, just brain structure producing function. 91% accuracy matching biological fly's neural responses.
- **Roadmap:** Mouse brain emulation (70M neurons) within 2 years. Then human.
- **Hiring:** https://eon.systems/careers — they need engineers.
- **Open problems:** Mouse brain is 500x more neurons than fly. Computational cost scales super-linearly. No complete mouse connectome exists yet (E11 Bio is working on it). Unknown whether connectome alone is sufficient — what about neuromodulators, glial cells, epigenetic state?
- **Relevance:** THE company to watch if you believe connectome-based emulation is the path. Most directly working on the "can we run a brain in software" question.

### OpenWorm
- **Website:** https://openworm.org/
- **What they do:** Open-source simulation of C. elegans (302 neurons, ~7,000 synapses). The simplest organism with a nervous system.
- **Status:** Active but slow-moving. 20+ publications. Components include Sibernetic (physics), c302 (neural model), owmeta (data). Docker container available.
- **2024 update:** BAAIWorm (from BAAI, not OpenWorm directly) built on OpenWorm tools to create a biophysically detailed model that replicates zigzag movement. DevoWorm (sub-project) sponsored 2 Google Summer of Code students in 2024. C. elegans Connectome Toolbox released for managing multiple connectomics datasets.
- **Open problems:** Even with 302 neurons fully mapped since 1986, we still can't perfectly simulate C. elegans behavior. This is a cautionary tale — connectome alone may not be sufficient.
- **Relevance:** Best entry point for hands-on WBE work. Open source, small scale, welcoming community. GitHub: https://github.com/openworm

### Blue Brain Project / Open Brain Institute
- **Website:** https://bluebrain.epfl.ch/ (historical), OBI launching 2025
- **What they did:** Digital reconstruction of mouse brain at Blue Brain Project (EPFL, 2005-2024). Delivered fully open-source reference model of mouse brain with detailed neocortical reconstructions and simulation tools.
- **Status:** Blue Brain Project concluded December 2024 as Swiss National Research Infrastructure.
- **Successor:** Open Brain Institute (OBI) launched March 18, 2025. Independent nonprofit foundation. First Virtual Labs opened March 28, 2025.
- **Key people:** Henry Markram (founder of Blue Brain), Georges Khazen (CEO of OBI). 37 key former BBP members hired.
- **What OBI does:** AI-powered Virtual Labs for building and simulating digital brains — from molecular pathways to whole brains, across species, ages, disease states.
- **Relevance:** The simulation infrastructure they built is the closest thing to "SimBrain." Their tools and models are open source.

### Carboncopies Foundation
- **Website:** https://carboncopies.org/
- **What they do:** Nonprofit advancing whole brain emulation (WBE). Research coordination, workshops, roadmapping, software platform development.
- **Key people:** Dr. Randal Koene (founder)
- **Research initiatives:**
  - **BrainGenix:** Software platform specifically designed for WBE research. GitHub: https://github.com/carboncopies
  - **WBE Roadmap update:** Working group updating the 2008 Future of Humanity Institute WBE roadmap.
  - **Brain Emulation Challenge:** Workshop series (Feb 2025: "Functionalizing Brain Data, Ground-Truthing, and the Role of Artificial Data")
  - **Memory Decoding Challenge:** Satellite event at SfN 2025 — exceeded room capacity.
- **Relevance:** The coordination hub for WBE. If you want to understand the technical roadmap and meet people in the field, this is where to start.

### Brain Preservation Foundation
- **Website:** https://www.brainpreservation.org/
- **What they do:** Nonprofit promoting brain preservation research. Ran the Brain Preservation Prize.
- **Key people:** Kenneth Hayworth (co-founder, neuroscientist at HHMI Janelia)
- **Prize status:** Small Mammal Prize won by 21st Century Medicine (Feb 2016). Large Mammal Prize won by 21st Century Medicine (March 2018). Both using aldehyde-stabilized cryopreservation. Current prize focused on connectome imaged at FIBSEM resolution on human brain.
- **2025 status:** 1,700 subscribers. "Preserving Hope" initiative investigating making preservation a medically-supervised end-of-life choice.
- **Relevance:** Important advocacy and prize-based incentive organization. Less technical work, more ecosystem building.

---

## 4. Key Academic Labs

### Consciousness Measurement / Theory

**Giulio Tononi — University of Wisconsin-Madison**
- Theory: Integrated Information Theory (IIT). Consciousness = integrated information (phi). Currently at IIT 4.0.
- 2025: Major adversarial collaboration result published in Nature (April 2025) — COGITATE study pitted IIT vs Global Neuronal Workspace Theory. 256 participants, fMRI + MEG + iEEG. Result: 2/3 IIT predictions passed pre-registration threshold. Sustained synchronization within posterior cortex contradicted one IIT claim. Mixed verdict for both theories.
- 2025: Published comprehensive "Integrated Information Theory: A Consciousness-First Approach to What Exists" on arXiv.
- Relevance: IIT makes specific predictions about what physical systems are conscious. If correct, it constrains what a "consciousness-preserving upload" must preserve.

**Anil Seth — University of Sussex**
- Theory: Predictive processing / controlled hallucination model. Consciousness as prediction about bodily/sensory states.
- Centre: Sussex Centre for Consciousness Science
- 2025-2026: Published "Conscious artificial intelligence and biological naturalism" in Behavioral and Brain Sciences. Won 2025 Berggruen Prize Essay Competition with "The Mythology of Conscious AI." Published work on hemispherotomy and cortical islands of deep sleep.
- Relevance: Seth argues consciousness requires specific biological substrate properties. This matters for whether digital emulation can be conscious vs. merely functional.

**Stanislas Dehaene — College de France**
- Theory: Global Neuronal Workspace Theory (GNWT). Consciousness = information broadcast across brain-wide workspace via ignition in prefrontal-parietal network.
- 2025: COGITATE adversarial collaboration challenged GNWT — lack of ignition at stimulus offset, limited representation in prefrontal cortex. Theory needs refinement.
- Relevance: If GNWT is correct, preservation/emulation needs to capture the broadcast architecture, not just local circuits.

**Christof Koch — Allen Institute (former president)**
- Key figure bridging IIT theory and experimental neuroscience. Collaborated with Tononi. Led Allen Institute's consciousness-related work.
- Now working more independently after stepping down from Allen Institute leadership.

### Connectomics Tools Labs

**Lichtman Lab — Harvard**
- Jeff Lichtman. The lab behind the Google/Harvard human cortex fragment. Pioneer in serial-section electron microscopy for connectomics.

**Sebastian Seung — Princeton**
- Led FlyWire project. Developed the citizen science / AI-assisted proofreading approach to connectomics. Author of "Connectome" (2012). Key figure bridging computational neuroscience and connectomics.

**Viren Jain — Google**
- Leads Google Connectomics team. Developed the computational pipeline for segmenting EM volumes at petascale.

### Brain Preservation Science Labs

**Greg Bhatt / 21st Century Medicine**
- Won both Brain Preservation Foundation prizes. Developed aldehyde-stabilized cryopreservation (ASC). Now part of the broader cryobiology research community.

**Kenneth Hayworth — HHMI Janelia Farm**
- Co-founder of Brain Preservation Foundation. Working on automated tape-collecting lathe ultramicrotome (ATUM) for brain sectioning.

---

## 5. Nonprofits & Organizations

### Allen Institute for Brain Science
- **Website:** https://alleninstitute.org/
- **Location:** Seattle, WA
- **What they do:** Large-scale brain mapping. Allen Brain Cell (ABC) Atlas — ~9M cells mapped with MERFISH, 5,000+ cell clusters, ~300 major cell types in whole mouse brain. MICrONS consortium partner. Open data philosophy.
- **2025-2026:** Cell Types Workshop (2025), Computational Cell Types Workshop (2026). Continued ABC Atlas expansion with new modalities and species.
- **Funding:** Paul Allen estate / Vulcan. Operates at ~$100M+ annual budget.
- **Relevance:** The single most important source of open brain data. Their cell type atlases are foundational for any emulation effort.

### ASSC (Association for the Scientific Study of Consciousness)
- **Website:** https://theassc.org/
- **ASSC 28:** Heraklion, Crete — July 6-9, 2025
- **ASSC 29:** Santiago, Chile — June 30 - July 3, 2026. Satellite workshop on neurophenomenology (July 4-5).
- **Relevance:** The premier consciousness science conference. Where theories get tested and debated. Good place to meet researchers.

### Open Brain Institute (OBI)
- Successor to Blue Brain Project (see Section 3 above). Launched March 2025. Global nonprofit for digital brain simulation.

### Convergent Research / Schmidt Futures
- **Website:** https://www.convergentresearch.org/
- Incubator for Focused Research Organizations (FROs). Funds E11 Bio (connectomics). Backed by Eric Schmidt, Wendy Schmidt, Ken Griffin.

---

## 6. Where Could a Security Researcher / CS Engineer Contribute?

### Direct Fit: Open-Source Tools That Need Building

1. **Connectomics Analysis Pipelines**
   - PyTorch Connectomics (https://github.com/PytorchConnectomics) — Python-based tools for EM segmentation and synapse detection. Needs contributors, especially for performance optimization and new architectures.
   - webKnossos — 3D annotation tool for connectomics. Open source.
   - Connectome Mapper 3 (https://github.com/connectomicslab/connectomemapper3) — BIDS-compatible processing pipeline. Needs maintenance.
   - FlyWire Codex tools — the data explorer tools around the fly connectome.

2. **Brain Simulation Frameworks**
   - **OpenWorm** (https://github.com/openworm) — Best starting point. Python, C++, Docker. Small enough to understand, complex enough to matter. Components: Sibernetic (fluid dynamics in C++), c302 (neural network models in Python), owmeta (data framework). Active but under-resourced.
   - **BrainGenix** (https://github.com/carboncopies) — Carboncopies' WBE platform. Needs engineers. Python/C++.
   - **Open Brain Institute** virtual labs — building simulation infrastructure. Recently launched, likely needs developers.

3. **EEG/Neural Signal Processing**
   - OpenBCI software stack — open-source EEG hardware + software. Could use better real-time processing, artifact rejection, and BCI algorithms.
   - MNE-Python (https://github.com/mne-tools/mne-python) — Major open-source EEG/MEG analysis toolkit. Active, well-maintained, but always needs contributors for performance-critical code.

4. **Data Infrastructure**
   - E11 Bio's datasets are on AWS Open Data. The connectomics field needs better tooling for exploring, querying, and analyzing petascale brain datasets. This is a storage, indexing, and retrieval problem — pure CS.

### Companies/Labs Hiring CS/Engineering (Not Just Neuroscientists)

| Organization | Roles for Engineers | Skills Match |
|---|---|---|
| **Neuralink** | Software Engineer (BCI Applications) | C/C++/Rust, Python, Linux, embedded systems, real-time |
| **Blackrock Neurotech** | BCI Software team | Python, C++, data acquisition, real-time systems |
| **Eon Systems** | Engineering (see careers page) | Simulation, systems programming, ML |
| **E11 Bio** | Light sheet microscopy scientist, but also need software | ML/CV for segmentation, data pipelines |
| **Precision Neuroscience** | Various engineering | Embedded, signal processing |
| **Synchron** | Software engineering | Medical device software |
| **Paradromics** | Engineering | Signal processing, embedded |
| **Allen Institute** | Software engineering, data engineering | Python, data infrastructure, visualization |

### Problems That Map to Security/Systems Engineering Skillset

1. **Reverse engineering biological systems** — The same pattern-recognition and systems-thinking used to find kernel UAFs applies to understanding neural circuits. Connectomics is fundamentally about reverse engineering a system from its structure.

2. **Finding bugs in simulation frameworks** — Brain simulations are complex software systems. They have race conditions, numerical instability, and edge cases. Someone who found the io_uring SQE_MIXED OOB read can find bugs in neural simulators that produce incorrect results.

3. **Performance engineering for simulation** — Simulating 125K neurons (fly) is tractable. 70M (mouse) and 86B (human) are not without massive engineering effort. GPU optimization, memory management, distributed computing — all systems engineering problems.

4. **Data integrity and validation** — Connectomics datasets are petabyte-scale. Ensuring data quality, detecting errors in automated segmentation, building validation pipelines — this is the same mindset as fuzzing and invariant checking.

5. **Building reliable infrastructure** — Cryonics organizations need monitoring systems (temperature alerts, equipment failure detection), secure member portals, long-term data preservation systems. These are engineering problems.

6. **Security of BCI systems** — Brain-computer interfaces are embedded systems that need security auditing. As BCIs become wireless and connected, attack surface analysis becomes critical. This is literally security research applied to neurotechnology.

### Conferences to Attend

| Conference | When | Where | Focus |
|---|---|---|---|
| **ASSC 29** | June 30 - July 3, 2026 | Santiago, Chile | Consciousness science |
| **Carboncopies WBE Workshops** | Recurring (online) | Virtual | Whole brain emulation |
| **SfN (Society for Neuroscience)** | Annual, Nov | Varies (US) | Broad neuroscience |
| **IEEE Brain** | Annual | Varies | Neural engineering, BCI |
| **Bernstein Conference** | Annual, Sept | Germany | Computational neuroscience |
| **Global Cryonics Summit** | 2026 | TBD | Cryonics community |
| **NeurIPS / ICML** (neuro-AI tracks) | Annual | Varies | ML applied to neuroscience |

### Communities to Join

1. **Carboncopies Slack/Discord** — WBE community. Active discussions. Start here.
2. **OpenWorm Slack** — https://openworm.org/ — Contributor community for C. elegans simulation.
3. **FlyWire community** — Via flywire.ai. Citizen science connectomics.
4. **LessWrong / EA Forum** — Active discussion on brain preservation, consciousness, WBE from an effective altruism perspective.
5. **Cryonics Society forums** — https://cryonicssociety.org/
6. **BCI-related subreddits and Discord servers** — r/BCI, OpenBCI forums

### Concrete Next Steps (Not "Read More Papers")

1. **Contribute to OpenWorm** — Fork the repo, run the simulation, find bugs or improve performance. This is the lowest barrier entry to WBE.

2. **Build a tool on top of FlyWire data** — The complete fly connectome is publicly available. Build analysis tools, visualization, or run your own simulations using the connectome data. The Codex API exists.

3. **Apply to Eon Systems** — They're a small team doing the most ambitious WBE work. They need engineers, not just neuroscientists. Your systems background in C/C++/Rust and experience with complex systems is directly relevant.

4. **Attend a Carboncopies workshop** — Next one TBD but they run them regularly. Present yourself as an engineer interested in building WBE infrastructure.

5. **Audit BCI security** — Pick an open-source BCI platform (OpenBCI, or any published BCI protocol) and do a security audit. Publish findings. This establishes credibility at the intersection of security and neurotechnology.

6. **Build a connectomics data tool** — The field is drowning in petabyte-scale data with inadequate tooling. A performant, well-engineered data explorer / query tool for connectomics datasets would be genuinely useful.

7. **Work on E11 Bio's AI segmentation problem** — Their PRISM pipeline needs ML engineers who can build self-proofreading segmentation models. This is computer vision + systems engineering.

---

## 7. Funding Landscape

### Major Funders

| Funder | Focus | Scale |
|---|---|---|
| **NIH BRAIN Initiative** | Connectomics, neural tools, BCI | $321M in FY2025 (down from $402M in FY2024). Cures Act funding expires after FY2026, but base funding continues. |
| **Templeton World Charity Foundation** | Consciousness science | $30M "Accelerating Research on Consciousness" initiative. Funds adversarial collaborations between competing theories. $1.125M in registered reports grants. |
| **Schmidt Futures / Convergent Research** | Connectomics (E11 Bio), FROs | Undisclosed but large (Eric Schmidt, Ken Griffin backed) |
| **Allen Institute** (Paul Allen estate) | Brain mapping, cell atlases | ~$100M+/year operating budget |
| **Founders Fund (Peter Thiel)** | Cryopreservation | Led Until Labs $58M Series A |
| **Lux Capital** | Cryopreservation, BCI | Participated in Until Labs round |
| **Protocol Labs** | Whole brain emulation | Led Eon Systems $3.5M seed |
| **Larry Page (family office)** | Whole brain emulation | Participated in Eon Systems seed |
| **Y Combinator** | Various (Nectome in 2018) | Small checks |
| **IARPA** | Connectomics (MICrONS) | Significant government funding |
| **Simons Foundation** | Computational neuroscience | Flatiron Institute, connectomics competitions |

### FTX/SBF Legacy
FTX Future Fund had funded several consciousness/WBE-related projects before collapse. Some of these projects lost funding mid-stream. The void has been partially filled by Open Philanthropy and Templeton but not fully.

### Is This Space Growing or Contracting?

**Growing in aggregate, but shifting:**

- **Cryopreservation: GROWING.** Until Labs raising $100M+ signals serious VC interest. Tomorrow Bio's fastest-ever membership growth. Multiple new organizations (Sparks, Southern Cryonics).
- **BCI: RAPIDLY GROWING.** Multiple companies in FDA clinical trials simultaneously (Neuralink, Synchron, Paradromics, Precision). Hundreds of millions in VC funding. 550+ job postings.
- **Connectomics: GROWING but government funding declining.** NIH BRAIN Initiative cut 20% in FY2025. Compensated by private/philanthropic funding (Schmidt, Allen, Simons). The science is accelerating (fly connectome complete, mouse visual cortex done, human fragment mapped).
- **Whole brain emulation: EARLY BUT GROWING.** Eon Systems' fly brain result is a genuine milestone. Small funding ($3.5M) but backed by notable investors. Carboncopies workshops seeing record attendance.
- **Consciousness science: STABLE.** Templeton's $30M initiative is the anchor. Academic interest high (COGITATE study, adversarial collaborations). No major new funding sources but no contraction either.

### Total Funding Estimate (2024-2026)

Rough estimates across the preservation + consciousness ecosystem:
- Government (NIH BRAIN, IARPA, NSF): ~$400M/year
- Private/philanthropic (Allen, Templeton, Schmidt, Simons): ~$200M/year
- Venture capital (Until, BCI companies): ~$500M cumulative 2024-2026
- Cryonics orgs (operational revenue): ~$10M/year

**Total: roughly $1.5-2B flowing through this space over 2024-2026**, though the vast majority goes to BCI and connectomics, not directly to preservation or consciousness research.

---

## Summary: The State of Play

The field is at an inflection point. Three things happened in 2024-2025 that changed the landscape:

1. **The fly connectome was completed** (FlyWire, Oct 2024) and immediately **emulated in a virtual body** (Eon Systems, 2025). For the first time, we went from scan to functional emulation for a complete brain.

2. **Until Labs raised $100M+** for reversible cryopreservation, making this a VC-funded engineering problem rather than a fringe science curiosity.

3. **Multiple BCIs entered human clinical trials** simultaneously, creating a pipeline for increasingly high-bandwidth brain interfaces.

The gap between "preserve a brain" and "extract useful information from it" remains enormous. The gap between "map a connectome" and "emulate it functionally" is shrinking rapidly (fly = done, mouse = years away, human = decades away at minimum).

For a systems engineer: the highest-leverage contributions are in (1) simulation/emulation infrastructure, (2) connectomics data tooling, and (3) BCI security. The field is engineering-bottlenecked, not neuroscience-bottlenecked. They have more data than they can process and more theories than they can test computationally.
