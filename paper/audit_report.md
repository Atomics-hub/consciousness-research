# Fact-Check Audit Report: "What Must Be Preserved?"

**Auditor:** Claude (automated fact-check)
**Date:** 2026-03-27
**Paper:** draft_v1.md by Thomas Ryan

---

## Summary of Findings

- **Total citations in References:** 24
- **Citations with errors:** 5
- **Orphan references (in list but never cited):** 2
- **In-text citation format errors:** 2
- **Factual/quantitative errors found:** 3
- **Claims needing correction or qualification:** 4
- **Logical/argument issues:** 2

---

## Section 1: Introduction

### Claim: "Sandberg and Bostrom, 2008"
- **Verification:** CORRECT. Technical Report 2008-3, Future of Humanity Institute, University of Oxford.

### Claim: "Musk and Neuralink, 2019"
- **Verification:** CORRECT. "An integrated brain-machine interface platform with thousands of channels." JMIR, 21(10), e16194.

### Claim: "McIntyre and Fahy, 2015"
- **Verification:** CORRECT. "Aldehyde-stabilized cryopreservation." Cryobiology, 71(3), 448-458.

### In-text citation: "(Dehaene et al., 2011)"
- **Verification:** INCORRECT. The reference list has this as "Dehaene, S., and Changeux, J.-P. (2011)" -- a two-author paper. "et al." is inappropriate for two authors. Should be "(Dehaene and Changeux, 2011)".
- **Action required:** Change in-text citation to "(Dehaene and Changeux, 2011)".

### Claim: "~10^18 FLOPS" for spiking simulation (Sandberg and Bostrom)
- **Verification:** CORRECT. Sandberg & Bostrom give 10^18 for spiking neural network level.

### Claim: "8.6 x 10^18 tubulin dimers"
- **Verification:** CORRECT (math). The paper states "10^4 microtubules per neuron, 10^8 tubulins per neuron, 86 billion neurons." The multiplication is 10^8 tubulins/neuron x 8.6 x 10^10 neurons = 8.6 x 10^18. The per-neuron estimates of ~10^4 microtubules and ~10^8 tubulin dimers are consistent with published estimates (e.g., Hameroff and Penrose literature, and independently confirmed sources stating ~10,000 microtubules/neuron and ~100 million tubulin dimers/neuron).

### Citation: "(Penrose and Hameroff, 1996)"
- **Verification:** INCORRECT AUTHOR ORDER. The 1996 paper "Orchestrated reduction of quantum coherence in brain microtubules: A model for consciousness" in Mathematics and Computers in Simulation, 40(3-4), 453-480 lists **Hameroff, S. R., and Penrose, R.** as the author order, not Penrose and Hameroff. Multiple databases (PhilPapers, ScienceDirect, SCIRP) confirm Hameroff as first author.
- **Action required:** Change all instances of "Penrose and Hameroff, 1996" to "Hameroff and Penrose, 1996" in both text and references.

### Citation: "(Graziano, 2013)"
- **Verification:** CORRECT. *Consciousness and the Social Brain*, Oxford University Press, 2013.

### Claim: "Butlin et al. (2023)"
- **Verification:** CORRECT. arXiv:2308.08708. Full author list verified.

### Claim: "Chalmers (2010)" on mind uploading / singularity
- **Verification:** CORRECT. "The singularity: A philosophical analysis." JCS, 17(9-10), 7-65.

---

## Section 2: Methods

### Claim: "86 billion neurons (Azevedo et al., 2009)"
- **Verification:** CORRECT. Azevedo et al. found 86.1 +/- 8.1 billion NeuN-positive neurons. Published in J. Comp. Neurol., 513(5), 532-541.

### Claim: "~10^14 synapses"
- **Verification:** CORRECT. Standard estimate is ~10^14 (100 trillion) synapses in the adult human brain. Range in literature: 10^14 to 5 x 10^14. The "~" qualifier is appropriate.

### Claim: "~20 bytes per synapse for Hodgkin-Huxley-level parameterization (Sandberg and Bostrom, 2008)"
- **Verification:** PLAUSIBLE but not independently verified from the primary source (PDF is access-restricted). The number is consistent with what other analyses cite from the report.

### Claim: "1.4 PB per mm^3 for nanoscale electron microscopy data (Shapson-Coe et al., 2024)"
- **Verification:** CORRECT. Shapson-Coe et al. (2024), published in Science, 384(6696), eadk4858, reports that the 1 mm^3 cortical sample produced 1.4 petabytes of data.

### COGITATE reference: "(COGITATE Consortium, 2025)"
- **Verification:** CORRECT. Published in Nature, 642(8066), 133-142. DOI: 10.1038/s41586-025-08888-1. 256 participants confirmed.

---

## Section 3: Theory-by-Theory Analysis

### 3.1 IIT 4.0

#### Citation: "(Tononi et al., 2023)"
- **Verification:** NEEDS CORRECTION. The in-text citation says "Tononi et al., 2023" but the actual first author is **Albantakis, L.**, not Tononi. Tononi is the last/corresponding author. The References entry also incorrectly lists "Tononi, G., Albantakis, L., Boly, M., Massimini, M., and Koch, C." -- the actual author list is Albantakis, Barbosa, Findlay, Grasso, Haun, Marshall, Mayner, Zaeemzadeh, Boly, Juel, Sasai, Fujii, David, Hendren, Lang, and Tononi (16 authors).
- **Action required:** Change in-text to "(Albantakis et al., 2023)" and fix the References entry to list Albantakis as first author with correct author list (or use "et al." after first 3-6 authors per chosen style).

#### Claim: "Phi computation grows super-exponentially as ~2^(2^N)"
- **Verification:** NEEDS QUALIFICATION. The complexity of computing Phi involves evaluating all bipartitions. For N elements, the number of bipartitions is ~2^N (more precisely, the number of ways to partition into two non-empty subsets is 2^(N-1) - 1). The evaluation of each partition involves computing information quantities over state spaces of size 2^N, so the total complexity is roughly O(2^N * 2^N) = O(2^(2N)) or O(4^N) in the simplest formulation. Some formulations involving IIT 3.0's full constellation of concepts do approach double-exponential or worse, but the claim "~2^(2^N)" as stated is not precisely the standard characterization. Tegmark (2016) and Barrett & Seth (2011) discuss computational intractability, with Tegmark noting "super-exponential" growth. The phrase "super-exponentially as ~2^(2^N)" conflates the general characterization ("super-exponential") with a specific formula. The paper should either cite the specific derivation or use "super-exponential" without the precise formula.
- **Action required:** Either replace "~2^(2^N)" with simply "super-exponentially" or provide a more precise derivation with appropriate citation.

#### Claim: "10^22 FLOPS" for electrophysiology level (Sandberg and Bostrom)
- **Verification:** CORRECT. Sandberg & Bostrom give 10^22 FLOPS for the electrophysiology (Hodgkin-Huxley) level.

#### Citation: "(Barrett and Seth, 2011; Tegmark, 2016)"
- **Verification:** CORRECT. Barrett & Seth (2011) in PLOS Comp Bio, 7(1), e1001052. Tegmark (2016) in PLOS Comp Bio, 12(11), e1005123.

#### Citation: "(Doerig et al., 2019)"
- **Verification:** CORRECT. "The unfolding argument." Consciousness and Cognition, 72, 49-59. Author names confirmed: Doerig, Schurger, Hess, and Herzog.

### 3.2 GNWT

#### Citation: "(Baars, 1988)"
- **Verification:** CORRECT. *A Cognitive Theory of Consciousness*, Cambridge University Press.

#### Citation: "(Dehaene et al., 2011)" -- same error as Section 1
- **Verification:** INCORRECT. Should be "(Dehaene and Changeux, 2011)". See Section 1 note.

#### Claim: "~10^18 FLOPS for spiking-level simulation"
- **Verification:** CORRECT per Sandberg & Bostrom.

#### Claim: "10^22 FLOPS at the electrophysiology (Hodgkin-Huxley) level"
- **Verification:** CORRECT per Sandberg & Bostrom.

#### Claim: "Blue Brain Project's scaling from 31,000 neurons at ~1 PFLOPS (Markram et al., 2006)"
- **Verification:** NEEDS CORRECTION. (1) The reference is "Markram, H. (2006)" -- single author, not "Markram et al." The paper is solely by Henry Markram. The References list correctly shows single author but the in-text citation says "Markram et al., 2006." (2) The Blue Brain Project's initial neocortical column model contained ~31,000 neurons, which is correct. (3) The "~1 PFLOPS" for that column is not clearly stated in the 2006 paper itself. The BBP used an IBM Blue Gene/L, which was ~280 TFLOPS (not 1 PFLOPS). A PFLOPS machine was described as future aspiration. This claim may be extrapolated rather than directly stated.
- **Action required:** Fix "Markram et al., 2006" to "Markram, 2006" in text. Verify or qualify the "~1 PFLOPS" claim.

### 3.3 HOT

#### Citation: "(Rosenthal, 2005)"
- **Verification:** CORRECT. *Consciousness and Mind*, Oxford University Press.

#### Citation: "(Lau and Rosenthal, 2011)"
- **Verification:** CORRECT. "Empirical support for higher-order theories." Trends in Cognitive Sciences, 15(8), 365-373.

#### Citation: "(Brown, Lau, and LeDoux, 2019)"
- **Verification:** CORRECT. "Understanding the higher-order approach to consciousness." Trends in Cognitive Sciences, 23(9), 754-768.

### 3.4 Predictive Processing

#### Citation: "(Friston, 2010)"
- **Verification:** CORRECT. "The free-energy principle: A unified brain theory?" Nature Reviews Neuroscience, 11(2), 127-138.

#### Citation: "(Clark, 2013)"
- **Verification:** CORRECT. "Whatever next?" Behavioral and Brain Sciences, 36(3), 181-204.

#### Citation: "(Andrews, 2021)"
- **Verification:** CORRECT. "The math is not the territory." Biology & Philosophy, 36(5), 30.

### 3.5 RPT

#### Citation: "(Lamme, 2000)"
- **Verification:** CORRECT. "The distinct modes of vision offered by feedforward and recurrent processing." Trends in Neurosciences, 23(11), 571-579.

#### Citation: "(Lamme, 2006)"
- **Verification:** CORRECT. "Towards a true neural stance on consciousness." Trends in Cognitive Sciences, 10(11), 494-501.

### 3.6 Biological Computationalism

#### Citation: "(Milinkovic and Aru, 2025)"
- **Verification:** CORRECT. "On biological and artificial consciousness: A case for biological computationalism." Neuroscience and Biobehavioral Reviews, 181, 106524. DOI confirmed.

#### Claim: "~170 billion cells" for glial cells
- **Verification:** INCORRECT. The paper states in Section 3.6: "glial cell states (~170 billion cells at ~1.5 KB each = ~255 TB)." Azevedo et al. 2009 found ~84.6 billion nonneuronal cells, not 170 billion. The ~170 billion figure is the TOTAL cell count (neurons + non-neurons). Glial cells number approximately 85 billion, not 170 billion. The storage estimate of ~255 TB should be halved to ~128 TB if using the correct glial count.
- **Action required:** Change "~170 billion cells" to "~85 billion cells" and recalculate storage to "~128 TB".

#### Claim: "~10^25 FLOPS" for metabolome level
- **Verification:** CORRECT per Sandberg & Bostrom.

### 3.7 Orch OR

#### Citation: "Penrose and Hameroff, 1996"
- **Verification:** INCORRECT AUTHOR ORDER. See Section 1. Should be "Hameroff and Penrose, 1996".

#### Claim: "Tegmark (2000) calculated quantum decoherence at ~10^-13 seconds for microtubules"
- **Verification:** CORRECT. Tegmark (2000), Physical Review E, 61(4), 4194-4206, found decoherence timescales of ~10^-13 seconds for microtubules. The citation details in the References are correct.

#### Citation: "(Wootters and Zurek, 1982)"
- **Verification:** CORRECT. "A single quantum cannot be cloned." Nature, 299(5886), 802-803.

### 3.8 AST

#### Citation: "(Graziano, 2017)"
- **Verification:** CORRECT. "The attention schema theory: A foundation for engineering artificial consciousness." Frontiers in Robotics and AI, 4, 60.

#### Citation: "(Webb et al., 2021)"
- **Verification:** NEEDS CORRECTION. The References list "Webb, T. W., Kean, H. H., and Graziano, M. S. A. (2021). Effects of awareness and attention in a neural network agent. *Proceedings of the National Academy of Sciences*, 118(13), e2021535118."
  - The actual 2021 PNAS paper on attention schema in a neural network agent is by **Wilterson, A. I. W., and Graziano, M. S. A.** (2021), "The attention schema theory in a neural network agent: Controlling visuospatial attention using a descriptive model of attention," PNAS, 118(33), e2102421118.
  - Webb, Kean, and Graziano published "Effects of awareness on the control of attention" but in **J. Cogn. Neurosci., 28, 842-851 (2016)**, not PNAS 2021.
  - The cited title, authors, journal, year, volume, and article number are ALL wrong or garbled. This appears to be a fabricated/hallucinated reference combining elements of multiple real papers.
- **Action required:** Either cite Wilterson and Graziano (2021) PNAS e2102421118, or cite Webb, Kean, and Graziano (2016) J. Cogn. Neurosci. -- but be honest about which paper supports the specific claim being made. Do not use the current reference; it does not exist.

---

## Section 4: Cross-Theory Comparison

No new factual claims beyond those derived in Section 3. The engineering bridge table numbers are internally consistent with Section 3 derivations.

---

## Section 5: Risk Analysis

### Claim: "~7-8 years per doubling" for electrode count (Stevenson and Kording, 2011)
- **Verification:** CORRECT. Stevenson and Kording found neuron recording count doubles approximately every 7 years.

### Claim: "7+ orders of magnitude beyond current technology"
- **Verification:** PLAUSIBLE. Current best simultaneous neuron recording is ~10^3-10^4 (Neuralink N1: 1,024 electrodes; BISC: 65,536 electrodes recording 1,024 simultaneously). Gradual replacement requires ~10^7-10^10 neurons/s depending on theory. The gap is 3-7 orders of magnitude depending on baseline and target. "7+" is at the high end and defensible only for the most demanding theories.
- **Suggestion:** Consider qualifying as "3-7 orders of magnitude" or clarifying which theory drives the 7+ figure.

### Claim: "~170 years" to close gap at historical doubling rates
- **Verification:** APPROXIMATELY CORRECT given the assumptions. 7 orders of magnitude / (1 order per ~7 years per doubling, ~3.3 doublings per order) = ~7 * 23 years = ~161 years. This is rough but in the right ballpark. However, if the gap is closer to 3-4 orders of magnitude (using BISC as baseline and moderate theories), the timeline would be ~70-90 years.

---

## Section 6: Discussion

No new factual claims requiring verification beyond those already checked.

---

## References Section: Cross-Check

### References cited in text but missing from References list:
- None found. All in-text citations have corresponding References entries.

### References in list but never cited in text:
1. **Dehaene, Lau, and Kouider (2017).** "What is consciousness, and could machines have it?" Science, 358(6362), 486-492. This reference appears only in the References section and is never cited in the body text.
2. **Tononi, Boly, Massimini, and Koch (2016).** Listed as "Integrated information theory: An updated account. Archives Italiennes de Biologie, 154, 56-67." This is never cited in the text. Furthermore, this reference is INCORRECT -- the "updated account" in Archives Italiennes de Biologie is Tononi, G. (2012) (sole author), volume 150, pages 293-329. The 2016 paper by Tononi, Boly, Massimini, and Koch is "Integrated information theory: from consciousness to its physical substrate" in **Nature Reviews Neuroscience**, 17(7), 450-461 -- different journal, different title.
- **Action required:** Either cite these in the text or remove them from the References. Fix the Tononi 2016 entry -- it conflates two different papers (2012 Archives Italiennes sole-authored by Tononi, and 2016 Nature Reviews Neuroscience multi-authored).

### References with incorrect details:
1. **Hameroff/Penrose author order** -- see above.
2. **Tononi et al. 2023 (IIT 4.0)** -- wrong first author and incomplete author list.
3. **Tononi et al. 2016** -- wrong journal, wrong title, wrong year, wrong author count. Fabricated composite reference.
4. **Webb et al. 2021** -- fabricated reference. Paper does not exist as cited.

---

## Logical/Argument Assessment

### 1. Derivations from theory postulates to preservation requirements
- **Assessment:** Generally valid. The derivations follow logically from each theory's stated commitments. The IIT analysis correctly identifies that causal architecture matters, not just function. The GNWT analysis correctly identifies the connectome + dynamics requirement. The Orch OR analysis correctly identifies the no-cloning barrier. No straw-man representations detected in the theory descriptions.

### 2. Straw-man representations
- **Assessment:** Mostly fair. One minor concern: the treatment of Predictive Processing as "unclear" on substrate independence is defensible but slightly unfair. Friston and collaborators have been more explicit in recent work (2020s) that active inference is substrate-independent as a mathematical framework. The "unclear" designation is defensible for the 2010-2013 formulations cited, but the paper could acknowledge more recent positions.

### 3. The deflation paradox
- **Assessment:** The argument is logically sound as stated. The correlation between phenomenal seriousness and preservation difficulty is real and well-characterized. However, the argument has a subtle rhetorical issue: it frames the situation as a "paradox" when it is more accurately a straightforward implication. Theories that identify consciousness with substrate-specific properties necessarily make substrate transfer harder -- this is not paradoxical but expected. The term "deflation paradox" is catchy but slightly misleading. The observation itself is valuable and, to the author's credit, the paper acknowledges it may not have been previously noted in the preservation literature.

### 4. Preservation strategy success probabilities
- **Assessment:** The equal-weighting assumption (treating all 8 theories as equally likely) is explicitly acknowledged as a limitation, which is appropriate. However, the "cross-theory survival probability" numbers (e.g., "~50-60%" for digital emulation) are misleadingly precise given this assumption. Most researchers would assign much higher probability to GNWT/PP/HOT than to Orch OR. The numbers would shift substantially with any reasonable prior. The paper should note this more prominently or provide a sensitivity analysis.

---

## Priority Corrections (Must Fix Before arXiv)

1. **Webb et al. 2021 reference is fabricated.** This paper does not exist. Replace with the actual paper being referenced.
2. **Tononi et al. 2016 reference is a garbled composite.** Wrong journal, wrong title, wrong author count, wrong year. Fix or remove.
3. **Tononi et al. 2023 (IIT 4.0) has wrong first author.** Should be Albantakis et al. 2023.
4. **Hameroff/Penrose 1996 author order is reversed.** First author is Hameroff, not Penrose.
5. **Glial cell count of "~170 billion" is wrong.** The correct number is ~85 billion nonneuronal cells. 170 billion is the total cell count.
6. **"Dehaene et al., 2011" should be "Dehaene and Changeux, 2011"** (two-author paper).
7. **"Markram et al., 2006" should be "Markram, 2006"** (single-author paper).

## Secondary Corrections (Should Fix)

8. **Two orphan references** (Dehaene et al. 2017, Tononi et al. 2016) need to be either cited or removed.
9. **Phi complexity "~2^(2^N)"** should be softened to "super-exponential" unless a precise derivation is provided.
10. **"~1 PFLOPS" for Blue Brain 31,000 neuron simulation** needs verification or qualification.
11. **"7+ orders of magnitude" BCI gap** should be qualified to reflect range across theories.

---

## Items From Audit Checklist Not Found in Paper

The following items were in the audit request but are not claims made in this paper:
- "~57,000 cells, ~150 million synapses" for Google/Harvard map -- not stated (though Shapson-Coe 2024 is cited)
- "139,255 neurons, 54.5 million synapses" for FlyWire -- not mentioned
- "~4.7 bits per synapse" / Bartol et al. 2015 -- not mentioned
- Neuralink "1,024 electrodes" -- not mentioned
- BISC "65,536 electrodes" -- not mentioned
- "IIT 4.0 has 5 axioms and 5 postulates" -- not explicitly claimed (IIT 4.0 does have 5 axioms and corresponding postulates, which is correct per Albantakis et al. 2023)
- "COGITATE: 256 participants, six labs" -- 256 is confirmed correct; "six labs" not stated in paper

For the record: all of these claims, if they had been in the paper, would be factually correct based on verification.
