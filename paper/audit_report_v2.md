# Audit Report v2 -- draft_v1.md

**Date:** 2026-03-27
**Auditor:** Claude (second pass)
**Scope:** Citations, factual claims, writing quality, internal consistency

## Summary

Found **5 errors** ranging from a missing co-author on a reference to numerical inconsistencies between sections.

---

## Error 1: Missing co-author on Lamme (2000) reference

**Location:** Line 150 (in-text citation) and line 400 (reference entry)

**Problem:** The 2000 paper is by Lamme AND Roelfsema, not Lamme alone. The actual citation is:

> Lamme, V. A. F., & Roelfsema, P. R. (2000). The distinct modes of vision offered by feedforward and recurrent processing. *Trends in Neurosciences*, 23(11), 571-579.

Both the in-text citation "(Lamme, 2000)" and the reference list entry omit Roelfsema as co-author.

**Fix:** Change in-text to "(Lamme and Roelfsema, 2000)" and update the reference entry to include Roelfsema, P. R.

---

## Error 2: IIT data size inconsistency between Section 3.1 and Table (Section 4.1)

**Location:** Line 90 vs. line 222 (and line 237)

**Problem:** Section 3.1 derives IIT's data requirement as "~10 PB of scan data" from the calculation: 10^14 synapses x 100 bytes = 10^16 bytes = 10 PB. However, the engineering bridge table on line 222 states "~100 EB" for IIT's data size (processed), and line 237 repeats "~100 EB (IIT)."

100 EB = 10^20 bytes. 10 PB = 10^16 bytes. That is a 10,000x discrepancy with no explanation for the difference. If the table intends to capture something beyond the per-synapse parameterization (e.g., storing the full transition probability matrix for subsets), this needs to be explained in the text. As written, the text and table contradict each other.

**Fix:** Either update the table to match the text (~10 PB), or add explanation in Section 3.1 for why the full causal architecture requires ~100 EB (e.g., TPM storage for neuronal groups grows exponentially beyond per-synapse parameters). The IIT scanning resolution in the table (~5 nm) is also not derived anywhere in the text, while GNWT's ~10 nm is.

---

## Error 3: "Zero orders of magnitude gap" claim for AST BCI bandwidth

**Location:** Line 202

**Current text:**
> BCI bandwidth: ~10^5 neurons/s at 1 kHz; zero orders of magnitude gap in channel count from current technology, though write capability remains the bottleneck.

**Problem:** Neuralink's 2019 system had ~3,072 channels. The requirement here is 10^5 (100,000) neurons/s. That is approximately 1.5 orders of magnitude gap, not zero. Even the most generous current BCI channel counts (Utah arrays, Neuropixels) are in the low thousands, not 100,000.

**Fix:** Change "zero orders of magnitude" to "one to two orders of magnitude" or similar.

---

## Error 4: Repeated phrase in close proximity

**Location:** Lines 22 and 24

**Problem:** The exact phrase "the difference between a tractable engineering project and a physical impossibility" appears twice within three lines -- once at the end of a paragraph and again at the end of the very next paragraph. This reads as an accidental repetition rather than intentional emphasis.

**Fix:** Rephrase one of the two instances. For example, line 22 could end with something like: "It is the difference between feasible and physically impossible." This preserves the rhetorical force without verbatim repetition.

---

## Error 5: References not in alphabetical order

**Location:** Lines 369-422

**Problem:** Academic convention (and common sense for readers looking up citations) requires alphabetical ordering of references. The current order has multiple violations:

- Milinkovic and Aru (M) is listed 2nd, should be after Markram/McIntyre
- Albantakis et al. (A) is near the end, should be first or second
- Hameroff and Penrose (H) is between Musk and Rosenthal, should be after Graziano
- COGITATE Consortium (C) is between McIntyre and Musk, should be near Chalmers/Clark

**Fix:** Re-sort the entire references section alphabetically by first author's surname.

---

## Items Verified as Correct

The following items from the first audit's checklist were re-verified and confirmed correct:

- **86 billion neurons** (Azevedo et al., 2009) -- confirmed
- **~85 billion glial cells** (line 170) -- confirmed (Azevedo et al. found 84.6 +/- 9.8 billion non-neuronal cells)
- **10^14 synapses** -- standard estimate, correct
- **1.4 PB per mm^3** (Shapson-Coe et al., 2024) -- confirmed (1.4 PB for 1 mm^3 sample)
- **Phi complexity described as "super-exponentially"** in prose (line 90) -- correct (though table still uses `2^(2^N)` notation as a compact formula, which is acceptable in a table context)
- **No em dashes found** -- confirmed clean
- **Albantakis et al. 2023** used consistently for IIT 4.0 (not Tononi) -- confirmed
- **Hameroff and Penrose** used consistently (not Penrose and Hameroff) -- confirmed
- **Milinkovic and Aru** used consistently (not Aru et al.) -- confirmed
- **Wilterson and Graziano 2021** -- confirmed correct (PNAS 118(33), e2102421118)
- **No "et al." used for 2-author papers** -- confirmed (all et al. usages are for 3+ author papers)
- **All in-text citations have matching reference entries** -- confirmed
- **No orphan references** (every reference entry is cited in text) -- confirmed
- **All semicolon replacements are grammatically sound** -- confirmed
- **COGITATE Consortium 2025 reference** -- confirmed (Nature 642(8066), 133-142, DOI correct)
- **Andrews 2021** -- confirmed (Biology & Philosophy, 36(5), 30)
- **Wootters and Zurek 1982** -- confirmed (Nature, 299(5886), 802-803)
- **All other journal names, volumes, pages spot-checked** -- no errors found
