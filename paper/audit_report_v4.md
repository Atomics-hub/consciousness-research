# Audit Report v4 -- Final Pre-PDF Gate

**Date:** March 27, 2026
**Auditor:** Claude (fourth audit pass)
**Paper:** draft_v1.md
**Previous audits found and fixed:** 17 errors across 3 audits

---

## Errors Found: 5

---

### Error 1: Abstract contradicts body on which strategy no theory excludes (SUBSTANTIVE)

**Line 14 (Abstract):**
> "Cross-theory risk analysis reveals that gradual biological replacement is the only preservation strategy that no theory definitively excludes"

**Lines 312-318 (Section 5.1-5.2):**
The body states that **biological preservation (cryonics followed by future revival)** "works under all 8 theories" and is "the only approach that works under all eight theories." Gradual bio-hybrid replacement is compatible with only 7 of 8 theories (all except Orch OR). The conclusion (line 380) correctly identifies cryonics as the universal strategy.

The abstract attributes the "no theory excludes" property to gradual biological replacement, but the body attributes it to cryonics. These are different strategies (Strategy 3 vs Strategy 4 in Section 5.1).

**Fix:** Change the abstract to say "biological preservation (cryonics) is the only preservation strategy that no theory definitively excludes" or rephrase to accurately reflect the body's analysis. If the intent was to highlight gradual replacement's advantages, qualify with "among non-cryonic strategies" as the body does on line 318.

---

### Error 2: Pronoun inconsistency -- "our" in single-authored paper (MINOR)

**Line 42:**
> "This coverage ensures that our analysis is not biased toward any particular answer."

**Line 44:**
> "Section 2 describes our methods for deriving engineering requirements from theoretical postulates."

The paper is single-authored (Thomas Ryan) and uses "I" throughout (lines 36, 56, 70, 286, 362, 386, etc.). These two instances of "our" break the pronoun consistency. Should be "my" or "the" in both cases.

---

### Error 3: Semicolons used as parenthetical delimiters (STYLE -- 4 instances)

Semicolons are being used where commas (or em dashes, if they were permitted) belong -- as paired delimiters around parenthetical phrases. Semicolons cannot function as parenthetical pairs; they join independent clauses.

**Line 288:**
> "The theories most favorable to consciousness preservation; AST and HOT; are precisely those that deflate consciousness"

Should be: "The theories most favorable to consciousness preservation, AST and HOT, are precisely those..."

**Line 290:**
> "The theories that take phenomenal consciousness most seriously; IIT, Biological Computationalism, and Orch OR; are precisely those that make preservation hardest"

Should be: "The theories that take phenomenal consciousness most seriously, IIT, Biological Computationalism, and Orch OR, are precisely those..."

**Line 292:**
> "Theories that identify consciousness with something beyond functional organization; with the intrinsic nature of the physical substrate, with the specific character of biological computation, with quantum processes; necessarily make that something harder"

Should be: "...beyond functional organization, with the intrinsic nature of the physical substrate, the specific character of biological computation, and quantum processes, necessarily make..."

**Line 376:**
> "All eight theories; from the most permissive to the most hostile; agree that consciousness requires"

Should be: "All eight theories, from the most permissive to the most hostile, agree that consciousness requires"

Note: Line 258 ("the data size column spans roughly 10 orders of magnitude; from ~1 TB...") and line 260 ("it is a number; it is a number...") use semicolons correctly as clause joiners, not parenthetical delimiters. Line 374 similarly uses a semicolon acceptably before an elaboration. These are fine.

---

### Error 4: Bio. Comp. storage in table uses upper bound only (MINOR)

**Line 248 (Table):**
> Storage: ~100 PB

**Line 191 (Section 3.6):**
> "Processed molecular state: ~10-100 PB"

The table reports "~100 PB" but the section says "~10-100 PB". The table should say "~10-100 PB" to match, or at minimum "~100 PB" should be noted as the upper bound. All other theories' table entries match their section text exactly.

---

### Error 5: "Empirically active" criterion tension with Orch OR (MINOR)

**Line 14 (Abstract):**
> "I evaluate eight empirically active theories of consciousness"

**Line 50 (Section 2.1):**
> "Theories were selected from those with active empirical research programs as of early 2026."

**Line 213 (Section 3.7, Orch OR):**
> "no major experimental program is currently designed to validate or refute it"

The abstract and methods describe all eight theories as "empirically active" with "active empirical research programs," but the Orch OR section explicitly states that no major experimental program currently tests it. This is an internal contradiction. Consider softening the selection criterion language (e.g., "eight theories with published formal frameworks and varying degrees of empirical engagement") or noting Orch OR as an exception included for coverage of the theory space.

---

## Items Verified Clean

### Citations
- All 30 unique in-text citations have matching References entries.
- All 31 References entries are cited at least once in the text. (Azevedo et al. 2009 is cited on line 74.)
- Author name consistency verified for all citations between in-text and References.
- No "et al." misuse (all et al. citations have 3+ authors).
- References are in correct alphabetical order.

### Numbers and Internal Consistency
- Engineering bridge table numbers match Section 3 for IIT, GNWT, HOT, PP, RPT, AST, and Orch OR (Bio. Comp. storage noted as Error 4).
- Preservation scores (0-5) consistent across all sections.
- Substrate independence verdicts consistent: abstract (4-3-1), Section 1 (line 42), Section 3 individual verdicts, Section 4.3.
- Conclusion claims match body.

### Formatting
- Zero em dashes confirmed (grep found none).
- Figures numbered 1-5 in order of appearance. All five figure references in text match their corresponding captions.
- Notation and Definitions table: all 12 entries verified for accuracy. FLOPS figure (~2 x 10^18 for current exascale) is current. PB/EB/ZB definitions correct.
- No stray double spaces found.
- No blank line formatting issues.

### Factual Claims Verified Against Sources
- Azevedo et al. 2009: 86 billion neurons. Correct. Published in J. Comp. Neurol. 513(5), 532-541. Correct.
- Shapson-Coe et al. 2024: 1.4 PB for 1 mm^3, published in Science 384(6696). Correct.
- Wootters and Zurek 1982: Nature 299(5886), 802-803. Correct.
- COGITATE 2025: Nature 642(8066), 133-142, DOI 10.1038/s41586-025-08888-1. Correct.
- Milinkovic and Aru 2025: Neuroscience and Biobehavioral Reviews 181, 106524. Correct. Online December 2025; "December 2025" claim on line 197 is accurate.
- Musk and Neuralink 2019: JMIR 21(10), e16194. Correct.

### Writing
- No spelling errors found.
- No doubled or missing words found.
- No broken sentences found.
- Grammar clean throughout.

### Logical
- Abstract matches body (except Error 1).
- No contradictions between sections (except Errors 1 and 5).
- No unsupported claims beyond those noted.
