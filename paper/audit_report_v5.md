# Audit Report v5 -- Character-Level Final Pass

**Date:** March 27, 2026
**Auditor:** Claude (fifth audit pass)
**Paper:** draft_v1.md
**Previous audits found and fixed:** 22 errors across 4 audits (7, 5, 5, 5)

---

## Errors Found: 4

---

### Error 1: Systemic semicolon misuse -- fragments and parenthetical delimiters (STYLE, 15+ instances)

The paper has a pervasive pattern of using semicolons in two grammatically incorrect ways: (a) before noun phrases / fragments that elaborate on the preceding clause, and (b) as paired delimiters around appositives (where commas belong). Semicolons require independent clauses on both sides.

The v4 audit caught 4 of these (lines 288, 290, 292, 376). Lines 288 and 290 were fixed. **Lines 292 and 376 remain unfixed.** Additionally, the v4 audit missed at least 13 more instances of the same pattern:

**Unfixed from v4:**
- Line 292: "beyond functional organization**;** with the intrinsic nature...quantum processes**;** necessarily make" -- paired parenthetical delimiters, should be commas
- Line 376: "All eight theories**;** from the most permissive to the most hostile**;** agree" -- paired parenthetical delimiters, should be commas

**Newly identified (before fragments/appositives):**
- Line 123: "cortical neurons**;** the 'global workspace'" -- appositive, should be comma
- Line 193: "biological systems**;** bioengineered neurons that participate" -- elaboration, should be colon
- Line 207: "2^(8.6 x 10^18) entries**;** a number exceeding" -- appositive, should be comma
- Line 207: "2^(10^18) operations**;** a number with ~3 x 10^17 digits" -- appositive, should be comma
- Line 213: "~10^-13 seconds**;** far too fast for neural processes" -- fragment, should be comma
- Line 219: "attention schema'**;** a simplified model...others**;** analogous" -- paired parenthetical, should be commas
- Line 219: "internal representation**;** a useful model" -- appositive, should be comma or colon
- Line 223: "low-dimensional model**;** plausibly ~10^4-10^5 parameters" -- fragment, should be comma
- Line 223: "neural circuits**;** prefrontal...neurons)**;** total 5-10 billion" -- paired parenthetical, should be commas or colon
- Line 229: "human existence**;** that experience exists" -- fragment, should be colon
- Line 268: "static snapshot**;** connectivity without dynamics**;** is insufficient" -- paired parenthetical, should be commas
- Line 312: "entirely practical**;** whether cryopreservation...exist**;** not theoretical" -- paired parenthetical, should be commas
- Line 336: "~1 micrometer resolution**;** all within striking distance" -- fragment, should be comma
- Line 338: "consciousness research**;** specifically, experiments" -- fragment, should be comma or colon
- Line 374: "10+ orders of magnitude**;** from ~1 TB" -- fragment, should be colon
- Line 380: "biological preservation**;** cryonics at the highest...quality**;** because" -- paired parenthetical, should be commas

**Fix:** Replace all semicolons before fragments/appositives with commas (or colons where the semicolon introduces an explanatory elaboration). Replace all paired parenthetical semicolons with commas.

**Note:** The following semicolons are correctly used and should NOT be changed:
- Line 40 (numbered list separators)
- Line 97 ("destroyed; only the copy persists" -- two independent clauses)
- Line 111, 155, 171, 221 (citation separators within parentheses)
- Line 258 could go either way but "from ~1 TB..." is arguably a fragment
- Line 260 ("not a large number; it is a number" -- two independent clauses)
- Line 270 ("in isolation; the relationships" -- two independent clauses)
- Line 276 (complex list: "IIT because...; Biological Computationalism because...; Orch OR because...")
- Line 280 ("suffices; the copy would be" -- two independent clauses)
- Line 282 ("this; they restore function" -- two independent clauses)
- Line 326 ("you; identity consists" -- two independent clauses)
- Line 229 ("does not explain it; it explains it away" -- two independent clauses)
- Line 336 ("not merely uncertain; they are uncertain" -- two independent clauses)
- Line 362 ("do not; a future theory" -- two independent clauses)

---

### Error 2: HOT data size mismatch between Section 3 and table (MINOR)

**Line 143 (Section 3.3):**
> "This reduces data requirements to approximately 200 TB - 1 PB"

**Line 245 (Table):**
> Data Size (processed): ~500 TB

The table reports a single midpoint value (~500 TB) while the section gives a range (200 TB - 1 PB). All other theories that have ranges in Section 3 also show ranges in the table (e.g., Bio. Comp. shows "~10-100 PB" in both, AST shows "~1-10 TB" in both). HOT should be consistent.

**Fix:** Change the table's Data Size for HOT from "~500 TB" to "~200 TB - 1 PB" to match Section 3. Also update the Storage column from "~500 TB" to "~200 TB - 1 PB" for consistency.

---

### Error 3: Figure filenames do not match figure numbers (MINOR)

The five figures are numbered sequentially in the text (Figure 1 through Figure 5), which is correct. However, the underlying filenames are mismatched, suggesting the figures were reordered at some point without renaming the files:

| Text label | Filename referenced |
|---|---|
| Figure 1 | `fig2_engineering_requirements.png` |
| Figure 2 | `fig5_timeline.png` |
| Figure 3 | `fig1_substrate_fault_line.png` |
| Figure 4 | `fig4_deflation_paradox.png` |
| Figure 5 | `fig3_risk_matrix.png` |

Only Figure 4 / `fig4_*` matches. This will cause confusion for anyone working with the figure files directly, and could lead to errors if figures are referenced by filename rather than caption.

**Fix:** Rename figure files to match their text numbers: `fig1_engineering_requirements.png`, `fig2_timeline.png`, `fig3_substrate_fault_line.png`, `fig4_deflation_paradox.png`, `fig5_risk_matrix.png`. Update the markdown image paths accordingly.

---

### Error 4: Section 5.2 title implies gradual replacement is the top strategy, but text says cryonics is (MINOR)

**Line 316 (Section heading):**
> "### 5.2 Why Gradual Replacement Dominates"

**Line 318 (Section body):**
> "biological preservation (cryonics with future revival) is the only approach that works under all eight theories"

The section title says "gradual replacement dominates," but the first substantive claim in the section is that cryonics is the only universal strategy. The section then explains that gradual bio-hybrid replacement is the strongest *non-cryonic* option. The title is misleading -- a reader skimming headings would conclude gradual replacement is the top-ranked strategy overall, when the text actually ranks cryonics first.

**Fix:** Change heading to "### 5.2 Strategy Ranking" or "### 5.2 Why Cryonics Wins and Gradual Replacement Is Second" or simply "### 5.2 Dominant Strategies" to avoid implying gradual replacement beats cryonics.

---

## Items Verified Clean

### Citations (full cross-reference)
- 31 unique in-text citations identified and matched one-to-one with 31 References entries.
- Zero orphan references (in list but never cited).
- Zero missing references (cited but not in list).
- Author order matches between in-text and References for all 31 citations.
- No "et al." misuse: all et al. citations (Albantakis, Azevedo, Shapson-Coe, Doerig, Butlin) have 3+ authors in References.
- References are in strict alphabetical order by first author's last name (verified A through W).

### Numbers (complete cross-check, all 8 theories)

**Preservation scores (Section 3 verdict vs. body):**
1. IIT: 1/5 (line 119) -- consistent
2. GNWT: 4/5 (line 135) -- consistent
3. HOT: 5/5 (line 151) -- consistent
4. PP: 3/5 (line 167) -- consistent
5. RPT: 4/5 (line 183) -- consistent
6. Bio. Comp.: 1/5 (line 199) -- consistent
7. Orch OR: 0/5 (line 215) -- consistent
8. AST: 5/5 (line 231) -- consistent

**Data sizes (Section 3 vs. Table):**
1. IIT: ~100 EB vs. ~100 EB -- match
2. GNWT: ~2 PB vs. ~2 PB -- match
3. HOT: 200 TB - 1 PB vs. ~500 TB -- **mismatch (Error 2)**
4. PP: ~5 PB vs. ~5 PB -- match
5. RPT: ~2 PB vs. ~2 PB -- match
6. Bio. Comp.: ~10-100 PB vs. ~10-100 PB -- match
7. Orch OR: N/A vs. N/A -- match
8. AST: ~1-10 TB vs. ~1-10 TB -- match

**FLOPS (Section 3 vs. Table):**
1. IIT: 10^22 (simulation) vs. 10^22 -- match
2. GNWT: 10^18 - 10^22 vs. 10^18 - 10^22 -- match
3. HOT: 10^17 - 10^20 vs. 10^17 - 10^20 -- match
4. PP: 10^18 - 10^21 vs. 10^18 - 10^21 -- match
5. RPT: 10^18 - 10^20 vs. 10^18 - 10^20 -- match
6. Bio. Comp.: 10^25 vs. 10^25 -- match
7. Orch OR: 2^(10^18) vs. 2^(10^18) -- match
8. AST: 10^15 - 10^18 vs. 10^15 - 10^18 -- match

**Substrate independence (Section 3 vs. Section 4.3):**
1. IIT: No vs. No -- match
2. GNWT: Yes vs. Yes -- match
3. HOT: Yes vs. Yes -- match
4. PP: Unclear vs. straddles the line -- match
5. RPT: Leaning yes vs. substrate-independent -- match (counted as yes)
6. Bio. Comp.: No vs. No -- match
7. Orch OR: No vs. No -- match
8. AST: Yes vs. Yes -- match
9. Abstract's "4-3-1" split: verified correct

**Abstract-specific claims vs. body:**
- "1-10 TB under AST": matches line 223
- "physically impossible under Orch OR": matches line 207
- "10^15 FLOPS to formally uncomputable": matches lines 223 (AST) and 207 (Orch OR)
- "three requirements" consensus: matches Section 4.2
- "cryonics is the only strategy compatible with all eight": matches lines 312-313, 318, 380
- "gradual bio-hybrid replacement compatible with 7 of 8": matches line 314
- "deflation paradox": matches Section 4.4

### Text quality
- Zero em dashes found.
- Zero spelling errors found ("panprotopsychism" on line 40 is the correct term).
- Zero doubled words found.
- Zero missing words / grammatically incomplete sentences found.
- Figures 1-5 appear in sequential order of first mention (lines 252, 254, 278, 294, 304-306).

### Logical consistency
- Abstract matches conclusion: verified.
- Section 5.2 correctly identifies cryonics as the only strategy working under all 8 theories: verified (line 318).
- No contradictions between sections found (beyond Error 4's misleading heading).

---

## Summary

Four errors remain, but only one is substantive in nature (the systemic semicolon misuse). The other three are minor presentation issues. The paper's factual content, citations, numbers, and logical structure are clean. After fixing these four issues, the paper should be at zero errors.

| # | Error | Severity | Lines |
|---|---|---|---|
| 1 | Semicolons before fragments / as parenthetical delimiters (15+ instances, including 2 unfixed from v4) | STYLE | 123, 193, 207, 213, 219, 223, 229, 268, 292, 312, 336, 338, 374, 376, 380 |
| 2 | HOT data size mismatch (200 TB-1 PB in text vs. ~500 TB in table) | MINOR | 143, 245 |
| 3 | Figure filenames don't match figure numbers (4 of 5 mismatched) | MINOR | 252, 254, 278, 306 |
| 4 | Section 5.2 heading implies gradual replacement is #1, but text says cryonics is | MINOR | 316-318 |
