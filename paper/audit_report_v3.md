# Audit Report v3 -- draft_v1.md

**Date:** 2026-03-27
**Auditor:** Claude (third pass)
**Scope:** Full line-by-line review -- citations, numbers, writing quality, logical consistency
**Previous audits:** v1 found 7 priority + 4 secondary errors; v2 found 5 errors. All 12 were fixed.

---

## Summary

Found **5 errors**, ranging from a citation formatting mistake that misattributes a paper to a logical contradiction between two subsections.

---

## Error 1: Combined citation misattributes Lamme (2006) to Lamme and Roelfsema

**Location:** Line 150 (Section 3.5 RPT, Core claim)

**Current text:**
> Consciousness arises from recurrent (feedback) processing within sensory cortical areas (Lamme and Roelfsema, 2000, 2006).

**Problem:** The combined citation format "(Lamme and Roelfsema, 2000, 2006)" implies both the 2000 and 2006 papers share the same authors. The 2000 paper is by Lamme and Roelfsema, but the 2006 paper ("Towards a true neural stance on consciousness," *Trends in Cognitive Sciences*) is by Lamme alone. The reference list on line 405 correctly shows Lamme (2006) as a single-author paper, but the in-text citation misattributes it.

**Fix:** Change to "(Lamme and Roelfsema, 2000; Lamme, 2006)".

---

## Error 2: Predictive Processing scanning resolution in table does not match text

**Location:** Line 225 (Table, Section 4.1) vs. line 138 (Section 3.4)

**Problem:** The engineering bridge table lists Predictive Processing's scanning resolution as "~10-100 nm." However, the text in Section 3.4 states that neuromodulatory receptor density maps require "~10 micrometer resolution" (10 micrometer = 10,000 nm). The table's upper bound of 100 nm is 100x smaller than the resolution stated in the text. The table likely conflates the connectome-level resolution (~10 nm, inherited from GNWT's requirement) with the neuromodulatory component, but the neuromodulatory scanning is at 10 um, not 100 nm.

**Fix:** Either change the table entry to "~10 nm - 10 um" (reflecting the range from connectome to neuromodulatory scanning), or change it to "~10 nm" (if the connectome sets the resolution floor and the neuromodulatory maps are at coarser resolution and thus not the bottleneck). The current "~10-100 nm" is incorrect either way.

---

## Error 3: Section 5.2 contradicts Section 5.1 on gradual replacement under Orch OR

**Location:** Line 296-297 (Section 5.2) vs. line 293 (Section 5.1, Strategy 4)

**Section 5.1 says (Strategy 4, bio-hybrid gradual replacement):**
> This succeeds under 7 of 8 theories (all except Orch OR, which requires quantum coherence that even synthetic biology may not replicate). Cross-theory survival probability: ~80-90%

**Section 5.2 says:**
> Across the theory space, gradual biological replacement emerges as the dominant strategy. It is the only approach that no theory definitively rules out

**Problem:** Section 5.1 explicitly states that Orch OR may exclude Strategy 4 (bio-hybrid gradual replacement), giving it 7/8 theories. Section 5.2 then claims this same strategy is "the only approach that no theory definitively rules out." These contradict each other. Strategy 3 (cryonics/biological revival) is the one that works under all 8 theories per Section 5.1. The abstract (line 14) also claims "gradual biological replacement is the only preservation strategy that no theory definitively excludes," inheriting the same contradiction.

**Fix:** Either (a) qualify Section 5.2 to say "the only *active* preservation strategy that *at most one* theory rules out" or similar, or (b) acknowledge that cryonics (Strategy 3) is the only strategy compatible with all 8 theories while gradual replacement is the dominant *active intervention* strategy. The abstract should be updated to match.

---

## Error 4: Inconsistent use of first person ("I" vs. "we") throughout the paper

**Location:** Throughout

**Problem:** The paper alternates between "I" and "we" with no clear pattern:

- "I" is used in: line 14 (abstract: "I evaluate"), line 36 ("I systematically derive"), line 40 ("I selected"), line 341 ("I do not assign"), line 365 (acknowledgments)
- "we" is used in: line 28 ("we address here"), line 52 ("We required"), line 70 ("we derived"), line 72 ("we extrapolated"), line 78 ("we treat"), line 265 ("Our analysis"), line 283 ("We assess"), line 359 ("we assume" in Section 6.4)

This is a single-author paper. Academic convention allows either "I" or the editorial "we," but not both in the same paper. The inconsistency is distracting.

**Fix:** Choose one and apply consistently. Given the personal tone of the acknowledgments and the single-author attribution, "I" is the more natural choice.

---

## Error 5: Figure numbering does not follow order of appearance

**Location:** Lines 231-285 (Sections 4.1 through 5.1)

**Problem:** Figures appear in the following order in the paper:

1. Figure 2 (line 231) -- engineering requirements
2. Figure 5 (line 233) -- timeline
3. Figure 1 (line 257) -- substrate fault line
4. Figure 4 (line 273) -- deflation paradox
5. Figure 3 (line 285) -- risk matrix

Academic convention requires figures to be numbered in the order they first appear. The current numbering is completely scrambled. A reader encountering "Figure 2" before "Figure 1" will assume they missed something.

**Fix:** Renumber figures to match their order of appearance: current Figure 2 becomes Figure 1, current Figure 5 becomes Figure 2, current Figure 1 becomes Figure 3, current Figure 4 becomes Figure 4, current Figure 3 becomes Figure 5. Update all in-text references, image filenames or alt-text, and captions accordingly.

---

## Items Verified as Correct (no errors found)

### Citations
- All 31 in-text citations have matching reference entries
- All 31 reference entries are cited in the text (no orphans)
- No "et al." used for 1-2 author papers
- Author names match between in-text and reference entries for all citations
- No em dashes found anywhere in the document
- Parenthetical citations are formatted consistently
- References are in alphabetical order by first author surname

### Numbers and consistency
- GNWT: all numbers match between Section 3.2 and table (data, compute, BCI, timeline)
- HOT: table value (~500 TB) falls within text range (200 TB - 1 PB); all other values match
- RPT: all numbers match between Section 3.5 and table
- Bio Comp: all numbers match between Section 3.6 and table
- Orch OR: all N/A and impossibility entries are consistent
- AST: all numbers match between Section 3.8 and table
- IIT: data size discrepancy (10 PB minimal vs. 100 EB realistic) is explained in text; table uses the realistic estimate. Scanning resolution (~5 nm) not derived in text but is a reasonable inference.
- Preservation scores (0-5) are consistent across all sections
- Substrate independence verdicts match between Section 3 and Section 4.3 (with the minor note that RPT says "Leaning yes" in Section 3.5 but is grouped with the definitive "yes" theories in Section 4.3 -- this is a judgment call, not an error)
- FLOPS ranges are internally consistent
- Feasibility timelines match between text and table

### Factual claims (verified via web search)
- COGITATE Consortium (2025) results accurately characterized for both IIT and GNWT
- E11 Bio PRISM is a real connectomics platform (confirmed)
- Until Labs is a real cryonics/cryopreservation company (confirmed)
- Google/Harvard connectomics collaboration is real (confirmed; this is the Shapson-Coe et al. 2024 work)
- COGITATE DOI, journal, and volume confirmed correct

### Writing quality
- No doubled words found
- No missing words detected
- No spelling errors found
- No grammatically broken sentences from semicolon replacements
- Semicolon usage is consistently appropriate throughout
- All five figures (fig1-fig5) exist in the figures/ directory

### Logical soundness
- Abstract accurately summarizes the paper's content (aside from the Strategy 3/4 issue in Error 3)
- Section 3 analyses logically follow from each theory's stated postulates
- Conclusion is consistent with the body
- No unsupported claims beyond the acknowledged limitations

### Acknowledgments
- Tone is personal but appropriate for a preprint by an independent researcher
- The claim about consciousness solving "basically all the problems humans face" is strong but is clearly framed as personal motivation, not a paper finding
- Honest about the author's background (systems security, not neuroscience)

---

## Minor Notes (not errors, but worth considering before PDF)

1. **Section 2.2 lists 9 assessment criteria, but Section 3 uses only 7 as explicit headings.** Criteria 3 (Digital emulation viability) and 5 (Minimum viable identity) are addressed implicitly within other headings but never appear as labeled subsections. This could confuse a reader who tries to find all 9 criteria in Section 3.

2. **IIT scanning resolution (~5 nm) in the table is not derived in the text.** GNWT's ~10 nm is derived from Shapson-Coe et al., but IIT's ~5 nm is stated only in the table with no textual justification.

3. **Section 1's roadmap (line 44) mentions Sections 2-6 but omits Section 7 (Conclusion).** This is a minor omission -- conclusions are conventionally understood to follow -- but adding "and Section 7 concludes" would be cleaner.
