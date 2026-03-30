# Audit Report v6 -- Final Meticulous Pass

**Date:** March 27, 2026
**Auditor:** Claude (sixth audit pass)
**Paper:** draft_v1.md
**Previous audits found and fixed:** 26 errors across 5 audits (7, 5, 5, 5, 4)

---

## Errors Found: 2

---

### Error 1: Missing closing parenthesis (GRAMMAR, Line 223)

**Line 223 (Section 3.8, AST Preservation requirements):**

> "The relevant neural circuits (prefrontal attention control (~2-4 billion neurons), parietal attention maps (~1-2 billion neurons), memory systems (~1 billion neurons), self-model circuits (~1-2 billion neurons), total 5-10 billion neurons, perhaps 5-10% of the brain."

The opening parenthesis after "circuits" is never closed. The inner parentheses (around neuron counts) each open and close correctly, but the outer parenthesis that begins with "(prefrontal attention control" remains unclosed at the end of the sentence. Should end with "...5-10% of the brain)." (adding a closing parenthesis before the period).

**Fix:** Change `perhaps 5-10% of the brain.` to `perhaps 5-10% of the brain).`

---

### Error 2: Semicolon before noun phrase fragment (GRAMMAR, Line 219)

**Line 219 (Section 3.8, AST Core claim):**

> The brain constructs an "attention schema"; a simplified model of how it selectively enhances some signals over others

The semicolon separates a complete clause from a noun phrase fragment serving as an appositive to "attention schema." A semicolon requires independent clauses on both sides. "A simplified model of how it selectively enhances some signals over others" is a noun phrase, not an independent clause. This was flagged in the v5 audit (Error 1, specifically line 219) but was not fixed.

**Fix:** Change the semicolon to a colon: `"attention schema": a simplified model` (the colon introduces a definition/elaboration). Alternatively, use a dash: `"attention schema" -- a simplified model`.

---

## Borderline Item (Not Counted as Error)

**Line 258:** `spans roughly 10 orders of magnitude (Figure 1); from ~1 TB (AST) to ~100 EB (IIT)`

The v5 audit noted this as "could go either way." Strictly, the part after the semicolon is a prepositional phrase fragment, not an independent clause, so a colon would be more precise. However, the sentence reads naturally and the meaning is clear. Noted for author judgment.

---

## Complete Verification Record

### 1. Citation Cross-Reference (31 citations, 31 references)

Every in-text citation was matched against the References section. Every References entry was checked for a corresponding in-text citation.

| # | In-text citation | Reference entry | Match |
|---|---|---|---|
| 1 | Albantakis et al., 2023 | Line 392 | OK |
| 2 | Andrews, 2021 | Line 394 | OK |
| 3 | Azevedo et al., 2009 | Line 396 | OK |
| 4 | Baars, 1988 | Line 398 | OK |
| 5 | Barrett and Seth, 2011 | Line 400 | OK |
| 6 | Brown, Lau, and LeDoux, 2019 | Line 402 | OK |
| 7 | Butlin et al., 2023 | Line 404 | OK |
| 8 | Chalmers, 2010 | Line 406 | OK |
| 9 | Clark, 2013 | Line 408 | OK |
| 10 | COGITATE Consortium, 2025 | Line 410 | OK |
| 11 | Dehaene and Changeux, 2011 | Line 412 | OK |
| 12 | Doerig et al., 2019 | Line 414 | OK |
| 13 | Friston, 2010 | Line 416 | OK |
| 14 | Graziano, 2013 | Line 418 | OK |
| 15 | Graziano, 2017 | Line 420 | OK |
| 16 | Hameroff and Penrose, 1996 | Line 422 | OK |
| 17 | Lamme and Roelfsema, 2000 | Line 424 | OK |
| 18 | Lamme, 2006 | Line 426 | OK |
| 19 | Lau and Rosenthal, 2011 | Line 428 | OK |
| 20 | Markram, 2006 | Line 430 | OK |
| 21 | McIntyre and Fahy, 2015 | Line 432 | OK |
| 22 | Milinkovic and Aru, 2025 | Line 434 | OK |
| 23 | Musk and Neuralink, 2019 | Line 436 | OK |
| 24 | Rosenthal, 2005 | Line 438 | OK |
| 25 | Sandberg and Bostrom, 2008 | Line 440 | OK |
| 26 | Shapson-Coe et al., 2024 | Line 442 | OK |
| 27 | Stevenson and Kording, 2011 | Line 444 | OK |
| 28 | Tegmark, 2000 | Line 446 | OK |
| 29 | Tegmark, 2016 | Line 448 | OK |
| 30 | Wilterson and Graziano, 2021 | Line 450 | OK |
| 31 | Wootters and Zurek, 1982 | Line 452 | OK |

- Zero orphan references.
- Zero missing references.
- Author names consistent between in-text and reference list.
- References in strict alphabetical order (A through W).

### 2. Number Cross-Check (8 theories x 4 fields = 32 comparisons)

| # | Theory | Field | Section 3 value | Section 4 table value | Match |
|---|---|---|---|---|---|
| 1 | IIT | Data size | ~100 EB | ~100 EB | OK |
| 2 | IIT | Compute | 10^22 (simulation) | Simulation: 10^22 | OK |
| 3 | IIT | Preservation score | 1/5 | N/A (not in table) | OK |
| 4 | IIT | Substrate independence | No | substrate-dependent (S4.3) | OK |
| 5 | GNWT | Data size | ~2 PB | ~2 PB | OK |
| 6 | GNWT | Compute | 10^18 - 10^22 | 10^18 - 10^22 | OK |
| 7 | GNWT | Preservation score | 4/5 | N/A | OK |
| 8 | GNWT | Substrate independence | Yes | substrate-independent (S4.3) | OK |
| 9 | HOT | Data size | ~200 TB - 1 PB | ~200 TB - 1 PB | OK |
| 10 | HOT | Compute | 10^17 - 10^20 | 10^17 - 10^20 | OK |
| 11 | HOT | Preservation score | 5/5 | N/A | OK |
| 12 | HOT | Substrate independence | Yes | substrate-independent (S4.3) | OK |
| 13 | PP | Data size | ~5 PB | ~5 PB | OK |
| 14 | PP | Compute | 10^18 - 10^21 | 10^18 - 10^21 | OK |
| 15 | PP | Preservation score | 3/5 | N/A | OK |
| 16 | PP | Substrate independence | Unclear | straddles the line (S4.3) | OK |
| 17 | RPT | Data size | ~2 PB | ~2 PB | OK |
| 18 | RPT | Compute | 10^18 - 10^20 | 10^18 - 10^20 | OK |
| 19 | RPT | Preservation score | 4/5 | N/A | OK |
| 20 | RPT | Substrate independence | Leaning yes | substrate-independent (S4.3) | OK |
| 21 | Bio. Comp. | Data size | ~10-100 PB | ~10-100 PB | OK |
| 22 | Bio. Comp. | Compute | ~10^25 | 10^25 | OK |
| 23 | Bio. Comp. | Preservation score | 1/5 | N/A | OK |
| 24 | Bio. Comp. | Substrate independence | No | substrate-dependent (S4.3) | OK |
| 25 | Orch OR | Data size | N/A (no-cloning) | N/A (no-cloning) | OK |
| 26 | Orch OR | Compute | 2^(10^18) | 2^(10^18) | OK |
| 27 | Orch OR | Preservation score | 0/5 | N/A | OK |
| 28 | Orch OR | Substrate independence | No | substrate-dependent (S4.3) | OK |
| 29 | AST | Data size | ~1-10 TB | ~1-10 TB | OK |
| 30 | AST | Compute | 10^15 - 10^18 | 10^15 - 10^18 | OK |
| 31 | AST | Preservation score | 5/5 | N/A | OK |
| 32 | AST | Substrate independence | Yes | substrate-independent (S4.3) | OK |

All 32 comparisons match.

### 3. Semicolon Check (all semicolons outside Notation table)

| Line | Semicolon text | Correct? | Reason |
|---|---|---|---|
| 40 | "programs; (2) they have published" | Yes | Complex list with internal commas |
| 111 | "Barrett and Seth, 2011; Tegmark, 2016" | Yes | Citation separator |
| 123 | "Baars, 1988; Dehaene and Changeux, 2011" | Yes | Citation separator |
| 155 | "Friston, 2010; Clark, 2013" | Yes | Citation separator |
| 171 | "Lamme and Roelfsema, 2000; Lamme, 2006" | Yes | Citation separator |
| 219 | `"attention schema"; a simplified model` | **NO** | Fragment after semicolon (Error 2) |
| 221 | "Graziano, 2017; Wilterson and Graziano, 2021" | Yes | Citation separator |
| 229 | "does not explain it; it explains it away" | Yes | Two independent clauses |
| 243 | "~2^(2^N); Simulation: 10^22" | Yes | Table cell separator |
| 258 | "magnitude (Figure 1); from ~1 TB" | Borderline | Fragment, but noted as borderline |
| 260 | "not a large number; it is a number" | Yes | Two independent clauses |
| 270 | "in isolation; the relationships" | Yes | Two independent clauses |
| 276 | "not function; Biological Computationalism" | Yes | Complex list items |
| 276 | "from the substrate; Orch OR because" | Yes | Complex list items |
| 280 | "emulation suffices; the copy would be" | Yes | Two independent clauses |
| 282 | "test this; they restore function" | Yes | Two independent clauses |
| 326 | "copy *is* you; identity consists" | Yes | Two independent clauses |
| 336 | "not merely uncertain; they are uncertain" | Yes | Two independent clauses |
| 362 | "certainly do not; a future theory" | Yes | Two independent clauses |

### 4. Formatting Check

- Em dashes (---): Zero found. Clean.
- Figures numbered sequentially 1-5: Verified (lines 252, 254, 278, 294, 306).
- Figure filenames match figure numbers: fig1 = Figure 1, fig2 = Figure 2, fig3 = Figure 3, fig4 = Figure 4, fig5 = Figure 5. All match.
- References alphabetical: Verified A (Albantakis) through W (Wootters). Correct.
- No stray formatting issues found.

### 5. Grammar/Spelling Check

- Every sentence read. No misspellings found.
- "panprotopsychism" (line 40): correct philosophical term.
- No missing words, no doubled words, no broken sentences.
- One missing closing parenthesis found (Error 1, line 223).

### 6. Logical Consistency Check

- Abstract claims all verified against body and conclusion.
- "4-3-1" substrate independence split: correct (4 yes, 3 no, 1 ambiguous).
- "Three things came out of it" in conclusion: all three match body content.
- Section headings match their content.
- No contradictions between sections.

---

## Summary

Two errors remain, both on lines already flagged by v5 but not fixed during that round's corrections. One is a missing closing parenthesis (line 223), the other is a semicolon before a noun phrase fragment (line 219). The paper's factual content, citations, numbers, cross-references, and logical structure are clean.

| # | Error | Severity | Line |
|---|---|---|---|
| 1 | Missing closing parenthesis in AST preservation requirements | GRAMMAR | 223 |
| 2 | Semicolon before noun phrase fragment (unfixed from v5) | GRAMMAR | 219 |
