# Final Review: AI Writing Detection + Fact Check

## GOAL 1: AI WRITING DETECTION SCAN

### Overall Assessment

The paper reads well. The conclusion (Section 7) and acknowledgments are clearly human-voiced -- direct, opinionated, no hedging. The introduction is strong. The theory sections (3.1-3.8) are the most vulnerable area because they follow a rigid template, but that's partly intentional structure. The middle sections (4, 5, 6) have the most flaggable passages.

### Flagged Passages

---

**FLAG 1: "Several features of this table deserve emphasis." (Line 252)**

Classic AI transition. No human says "deserve emphasis." A human just emphasizes them.

Rewrite: "Three things stand out."

---

**FLAG 2: "This consensus has a direct engineering implication" (Line 272, in temporal dynamics paragraph)**

Overly formal connector phrase. The sentence works without the throat-clearing.

Rewrite: Cut "This consensus has a direct engineering implication:" and just start with "Any preservation strategy that captures only a static snapshot..."

---

**FLAG 3: "This rules out preservation strategies that capture individual neurons or circuits in isolation; the relationships between components are as critical as the components themselves." (Line 274)**

The second clause ("the relationships between components are as critical as the components themselves") is a generic truism that sounds like a textbook summary. The point is already made by the first clause.

Rewrite: "This rules out any preservation strategy that captures neurons or circuits in isolation."

---

**FLAG 4: "This is the strongest consensus in the field, and it is empirically supported" (Line 276)**

"Strongest consensus in the field" is the kind of authoritative-sounding but vague claim AI loves. What field? How measured?

Rewrite: "Every theory agrees on this, and the experimental data backs it up"

---

**FLAG 5: "This fault line determines whether digital preservation is even conceivable (Figure 5)." (Line 284)**

Minor, but "this fault line determines" is a stiff transition. The paragraph that follows is fine.

Rewrite: "Whether digital preservation is even conceivable depends entirely on this split (Figure 5)."

---

**FLAG 6: "What would resolve this question?" (Line 286)**

This rhetorical question followed by a long answer is a very common AI pattern (pose question, then answer it in a structured way). In this case the content is good enough that it's borderline. Consider cutting the question and just leading with: "The most direct experiment would be..."

---

**FLAG 7: The entire Section 4.4 opening paragraph (Lines 289-291)**

"The analysis reveals a tension that, to my knowledge, has not been previously identified in the preservation literature. I call it the deflation paradox."

This is fine content-wise but "the analysis reveals a tension" is stiff. The second sentence redeems it.

Rewrite: "There is a tension here that I haven't seen anyone point out. I call it the deflation paradox."

---

**FLAG 8: "This is not a coincidence. There is a deep structural relationship between..." (Line 296)**

"Deep structural relationship" is AI phrasing. The point is good but the language is inflated.

Rewrite: "This isn't a coincidence. There is a direct link between how seriously a theory takes the irreducibility of subjective experience and how difficult it makes preservation."

---

**FLAG 9: "The deflation paradox presents a genuine dilemma for anyone investing in consciousness preservation (Figure 6)." (Line 300)**

"Presents a genuine dilemma" is textbook AI hedging. Just state the dilemma.

Rewrite: "This is a real problem for anyone investing in consciousness preservation (Figure 6)."

---

**FLAG 10: "This has a practical implication: investments in consciousness preservation engineering are premature until the theory question is better resolved." (Line 342)**

"This has a practical implication" is throat-clearing. Just state the implication.

Rewrite: "The practical consequence: investments in consciousness preservation engineering are premature until the theory question is better resolved."

---

**FLAG 11: "Three extensions of this work would be valuable." (Section 6.5, Line 370)**

Generic AI closer. Sounds like a grant application.

Rewrite: "Three things I'd want to see next." (Or just cut the intro sentence and start listing.)

---

**FLAG 12: Repetitive structure in Section 3 theory analyses**

Every theory section follows: Core claim > Substrate independence > Preservation requirements > Gradual replacement > Scan-and-copy > Key weakness > Preservation verdict. This is intentional and fine as parallel structure. However, the opening sentence pattern is slightly repetitive:

- 3.1: "Consciousness is identical to..."
- 3.2: "Consciousness is the global broadcasting of..."
- 3.3: "A mental state is conscious when..."
- 3.4: "The brain is a hierarchical prediction machine..."
- 3.5: "Consciousness arises from recurrent (feedback) processing..."
- 3.6: "Consciousness arises from a specific kind of computation..."
- 3.7: "Consciousness arises from quantum computations..."
- 3.8: "Consciousness is the brain's simplified internal model..."

Three sections start with "Consciousness arises from..." (3.5, 3.6, 3.7). This is noticeable. Vary the phrasing:
- 3.5 could start: "Recurrent (feedback) processing within sensory cortical areas is what produces consciousness..."
- 3.6 could start: "Only biological systems currently instantiate the kind of computation that produces consciousness..."

---

**FLAG 13: "Suspiciously balanced" check**

The paper does NOT have this problem. The author clearly favors some theories over others: AST and HOT get 5/5, Orch OR gets 0/5 and is called "outside the scientific mainstream." Bio Comp gets called out for "argument from ignorance" risk. The deflation paradox section takes a clear position. The conclusion is opinionated. This reads like someone with actual views, not an AI trying to be fair to everyone.

---

**FLAG 14: Section 5.1 strategy descriptions**

These four paragraphs are well-structured but slightly formulaic: each ends with "Cross-theory survival probability: ~X%." This is fine since it's a deliberate comparison format, but the phrase "Cross-theory survival probability" appears 4 times in quick succession. Consider varying: "Survival odds across the theory space" or "If you weight all theories equally" for some instances.

---

### Passages That Sound Human (No Changes Needed)

- The entire introduction (Section 1) -- direct, punchy, has a clear voice
- "This is a remarkable omission." (Line 15) -- an actual opinion
- The thought experiment in paragraph 3 of the intro -- specific, concrete
- "philosophical zombie" usage in IIT section -- shows familiarity
- The entire conclusion (Section 7) -- "Three things came out of it," "No current theory lets you have it both ways" -- this is clearly a human
- The acknowledgments section -- unmistakably personal
- Key weakness sections throughout -- these have bite ("most logicians reject," "outside the scientific mainstream," "argument from ignorance")

---

## GOAL 2: FACT CHECK

### Engineering Bridge Table vs Section 3

| Theory | Table Value | Section 3 Value | Match? |
|--------|-----------|----------------|--------|
| IIT data | ~100 EB | ~100 EB (line 112) | YES |
| IIT compute | 2^(2^N) verification, 10^22 sim | super-exponential verification, 10^22 sim (line 112) | YES (table uses simplified notation) |
| GNWT data | ~2 PB | ~2 PB (line 128) | YES |
| GNWT compute | 10^18 - 10^22 | 10^18 - 10^22 (line 128) | YES |
| GNWT BCI | ~10^7 neurons/s @ 10 kHz | ~10^7 neurons/s at 10 kHz (line 128) | YES |
| HOT data | ~200 TB - 1 PB | ~200 TB - 1 PB (line 144) | YES |
| HOT compute | 10^17 - 10^20 | 10^17 - 10^20 (line 144) | YES |
| HOT BCI | ~10^6 neurons/s @ 10 kHz | ~10^6 neurons/s (line 144) | YES (table adds "@ 10 kHz" which section doesn't specify -- minor gap but not a contradiction) |
| PP data | ~5 PB | ~5 PB (line 160) | YES |
| PP compute | 10^18 - 10^21 | 10^18 - 10^21 (line 160) | YES |
| PP BCI | ~10^7 neurons/s @ 1 kHz | Not specified in section | MISSING SOURCE -- table has a value that Section 3.4 never states |
| RPT data | ~2 PB | ~2 PB (line 176) | YES |
| RPT compute | 10^18 - 10^20 | 10^18 - 10^20 (line 176) | YES |
| RPT BCI | ~10^7 neurons/s @ 100 kHz | Not specified in section | MISSING SOURCE -- table has a value that Section 3.5 never derives |
| Bio Comp data | ~10-100 PB | ~10-100 PB (line 192) | YES |
| Bio Comp compute | 10^25 | ~10^25 (line 192) | YES |
| Orch OR data | N/A | N/A (line 208) | YES |
| Orch OR compute | 2^(10^18) | 2^(10^18) (line 208) | YES |
| AST data | ~1-10 TB | ~1-10 TB (line 224) | YES |
| AST compute | 10^15 - 10^18 | 10^15 - 10^18 (line 224) | YES |
| AST BCI | ~10^5 neurons/s @ 1 kHz | ~10^5 neurons/s at 1 kHz (line 224) | YES |

**ISSUE: PP and RPT BCI bandwidth values appear in the table but are not derived in their respective Section 3 analyses.** The table claims ~10^7 neurons/s @ 1 kHz for PP and ~10^7 neurons/s @ 100 kHz for RPT, but neither Section 3.4 nor Section 3.5 mentions BCI bandwidth. These values should either be derived in the text or removed from the table.

### Preservation Scores

| Theory | Section 3 Score | Referenced Elsewhere | Match? |
|--------|----------------|---------------------|--------|
| IIT | 1/5 | Figure 5 description | YES |
| GNWT | 4/5 | Figure 5 description | YES |
| HOT | 5/5 | Figure 5 description | YES |
| PP | 3/5 | Figure 5 description | YES |
| RPT | 4/5 | Figure 5 description | YES |
| Bio Comp | 1/5 | Figure 5 description | YES |
| Orch OR | 0/5 | Figure 5 description | YES |
| AST | 5/5 | Figure 5 description | YES |

All match.

### Figure Numbers

Figures 1 through 8 appear in sequential order of first image placement. However:

**ISSUE: Line 307 references Figure 8 before Figure 7 in the text.** "I assess four preservation strategies against all eight theories (Figure 8). Figure 7 maps these strategies..." The text mentions Figure 8 first, even though the images appear in 7-then-8 order. This is confusing. Swap the sentence order so Figure 7 is introduced first.

### Em Dashes

No unicode em dashes found anywhere in the document. Clean.

### We/Our Usage

- Line 21: "We are building toward whole-brain emulation" -- general humanity "we," acceptable
- Line 23: "We do not." -- general humanity "we," acceptable
- Line 198: "we don't know" -- inside a paraphrased argument ("we don't know how digital systems could be conscious, therefore they can't be"), acceptable
- Line 388: Uses "I" -- correct

No authorial "we" found. Clean.

### Other Issues Found

1. **Section header formatting inconsistency (Line 84):** "## Notation and Definitions" is a top-level section header but has no section number. Every other section is numbered (1-7). This should either be "## 2.5 Notation and Definitions" (subsection of Methods) or given its own section number.

2. **Line 128 BCI bandwidth:** States "~10^7 neurons/s at 10 kHz per neuron" -- the "per neuron" clarification is useful but inconsistent with the table format which just says "@ 10 kHz." Minor formatting inconsistency.

3. **Line 307 cross-reference:** As noted above, Figure 8 is referenced before Figure 7. Should read: "Figure 7 maps four preservation strategies on two dimensions: technical feasibility with current technology and cross-theory compatibility. Figure 8 provides a detailed compatibility assessment of each strategy against all eight theories."

4. **HOT BCI frequency:** Table says "@ 10 kHz" but Section 3.3 doesn't specify sampling frequency for BCI. Should either add it to the section text or note it's inferred from GNWT's requirements.

5. **Scanning resolution for IIT:** Table says "~5 nm" but Section 3.1 doesn't specify a scanning resolution number. Section 3.1 talks about TPMs and causal architecture but never gives a nm figure. This value appears only in the table.

---

## Summary of Required Changes

### Must Fix (Factual/Structural)
1. Add BCI bandwidth derivations for PP and RPT in Sections 3.4 and 3.5, or note in the table that these are inferred
2. Add scanning resolution derivation for IIT in Section 3.1, or note basis in table
3. Fix Figure 7/8 reference order on line 307
4. Number the "Notation and Definitions" section (or make it a subsection of Methods)
5. Add HOT BCI sampling frequency to Section 3.3 text

### Should Fix (AI Detection)
1. Line 252: "Several features of this table deserve emphasis" -> "Three things stand out"
2. Line 272: Cut "This consensus has a direct engineering implication:"
3. Line 274: Trim the truism in the second clause
4. Line 276: "This is the strongest consensus in the field" -> "Every theory agrees on this"
5. Lines 289-291: "The analysis reveals a tension" -> "There is a tension here"
6. Line 296: "deep structural relationship" -> "direct link"
7. Line 300: "presents a genuine dilemma" -> "is a real problem"
8. Line 342: "This has a practical implication:" -> "The practical consequence:"
9. Line 370: "Three extensions of this work would be valuable" -> "Three things I'd want to see next"
10. Vary "Consciousness arises from" openings in 3.5, 3.6, 3.7

### Optional (Polish)
1. Vary "Cross-theory survival probability" phrasing in Section 5.1
2. Line 286: Cut rhetorical question "What would resolve this question?"
