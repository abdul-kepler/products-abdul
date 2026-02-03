# Prompt Improvements Analysis

**Date:** 2026-01-20
**Analyst:** Claude Code (Opus 4.5)

---

## Executive Summary

Analysis of judge results from `/evaluation_KD/evaluation_experimentV5/judge_results/` reveals specific failure patterns for each module. This document tracks improvement recommendations and their implementation status.

---

## Module Status Overview

| Module | Current Pass Rate | Target | MCC | Status |
|--------|------------------|--------|-----|--------|
| M01 | 57.3% | 90% | - | Needs V4 |
| M01A | 40% | 90% | - | Needs V3 |
| M01B | 75% | 90% | - | OK (rubric issue?) |
| M02 | 100% | 90% | 0.684 | OK |
| M02B | - | 90% | 0.703 | OK |
| M04 | 60% | 90% | 0.625 | Needs V2 |
| M04B | - | 90% | 0.438 | Needs V2 |
| M05 | - | 90% | 0.813 | OK |
| M05B | - | 90% | 0.835 | OK |

---

## M01: ExtractOwnBrandEntities

### Current Version: V3
### Pass Rate: 57.3% (43/75)

### Failure Patterns

1. **Product Line Splitting** (8 failures)
   - Problem: "Vibe Beam" extracted as separate "Vibe" and "vibe"
   - Root cause: Prompt doesn't handle multi-word product lines correctly
   - Fix: Add explicit rule for multi-word product lines from title

2. **Duplicate Entities** (8 failures)
   - Problem: "Vibe" and "vibe" both in output
   - Root cause: Case normalization not applied before deduplication
   - Fix: Add explicit case-insensitive deduplication step

3. **Hallucinated Typos** (7 failures)
   - Problem: "Vibbe", "Vieb" not valid single-edit typos
   - Root cause: Model generating multi-edit typos
   - Fix: Strengthen anti-hallucination constraint

4. **Amazon Test Failures** (8 failures)
   - Problem: Generic words like standalone "Vibe" included
   - Root cause: Not testing each word of multi-word entities
   - Fix: Emphasize testing LAST word of every entity

### Recommended Changes for V4

```markdown
## NEW: Multi-Word Product Line Handling

When a product title contains a MULTI-WORD product line like "Vibe Beam":

1. Extract the FULL product line: "Vibe Beam" (not just "Vibe")
2. Add lowercase: "vibe beam"
3. Generate typos for the FULL form: "Vibe Beem", "Vibe Beaam"
4. DO NOT extract individual words separately

**Example:**
- Title: "JBL Vibe Beam Earbuds"
- CORRECT: ["JBL", "jbl", "Vibe Beam", "vibe beam", "VibeBeem"]
- WRONG: ["JBL", "jbl", "Vibe", "vibe", "Beam", "beam"]

## NEW: Deduplication (Case-Insensitive)

Before output, normalize and deduplicate:
1. Create lowercase set of all entities
2. If lowercase collision → keep only ONE form (prefer original case)
3. Example: ["Vibe", "vibe", "VIBE"] → keep only ["Vibe"]
```

---

## M01A: ExtractOwnBrandVariations

### Current Version: V2
### Pass Rate: 40% (16/40)

### Failure Patterns

1. **Implausible Typos** (15 failures)
   - Problem: "JLB", "JBK", "JNL" for "JBL"
   - Root cause: Random letter swaps not on QWERTY keyboard
   - Fix: Constrain to ONLY adjacent QWERTY keys

2. **Count Validation Issues** (6 failures)
   - Problem: Judge marks 10 as failing "8-12" check
   - Root cause: Possible rubric issue OR judge interpretation
   - Fix: Verify rubric, ensure exactly 10 is valid

### Recommended Changes for V3

```markdown
## STRICT QWERTY Adjacency Table

Use ONLY these adjacent keys for typos:

| Key | Adjacent Keys |
|-----|--------------|
| Q | W, A |
| W | Q, E, A, S |
| E | W, R, S, D |
| R | E, T, D, F |
| T | R, Y, F, G |
| ... (full table) |

**Example for "JBL":**
- J adjacent: H, K, U, N, M
- B adjacent: V, G, H, N
- L adjacent: K, O, P

Valid typos: "JVL" (B→V), "JBK" ❌ (K is adjacent to L, not B)
```

---

## M01B: ExtractBrandRelatedTerms

### Current Version: V1
### Pass Rate: 75% (60/80)

### Failure Patterns

1. **Sub-brand False Negatives** (15 failures)
   - Problem: Judge expects sub-brands where none exist
   - Example: "Pioneer Camp" jacket has no sub-brand → judge expects one
   - Root cause: Rubric may be too aggressive

### Analysis

This appears to be a **rubric issue**, not a prompt issue. Products like:
- "Pioneer Camp Mens Puffer Jacket" → No sub-brand exists
- "Cisily Vacuum" → No sub-brand exists
- "Jikasho Phone Holder" → No sub-brand exists

The prompt correctly returns empty `sub_brands: []` for these.

### Recommendation

**Rubric needs adjustment** - not the prompt.
- Modify `M01b_sub_brands_found` to accept empty arrays for products without sub-brands

---

## M04: ClassifyCompetitorBrandKeywords

### Current Version: V1
### Pass Rate: 60% (36/60)
### Binary MCC: 0.625

### Failure Patterns

1. **Case-Insensitive Matching** (9 failures)
   - Problem: "oxo" not matching "OXO"
   - Root cause: Model not normalizing to lowercase before comparison
   - Fix: Add EXPLICIT lowercase normalization step

2. **Classification Confusion** (10 failures)
   - Problem: When OXO is in competitor list but keyword is "oxo oven mitts"
   - Root cause: Model treating OXO as not-competitor because it's a "product brand"
   - Fix: Clarify that competitor list is AUTHORITATIVE

### Recommended Changes for V2

```markdown
## MANDATORY Lowercase Normalization

**BEFORE any matching, you MUST:**

1. Convert keyword to lowercase: "OXO Oven Mitts" → "oxo oven mitts"
2. Convert each competitor entity to lowercase: "OXO" → "oxo"
3. Check if lowercase keyword CONTAINS lowercase competitor

**The comparison is ALWAYS lowercase vs lowercase!**

## Competitor List is AUTHORITATIVE

If a brand appears in `competitor_entities`, it IS a competitor - period.
- Don't second-guess the list
- Don't apply "is this really a competitor?" logic
- Trust the provided list completely
```

---

## M04B: ClassifyCompetitorBrandKeywords (Path B)

### Binary MCC: 0.438 (LOW)
### Recall: 24.2% (VERY LOW)

### Analysis

Same issues as M04 but worse performance. The low recall indicates the model is being too conservative and returning `null` when it should return `CB`.

### Recommended Changes

Apply same fixes as M04 V2.

---

## M05/M05B: ClassifyNonBrandedKeywords

### Pass Rate: - (not in judge results)
### Binary MCC: 0.813 / 0.835 (GOOD)

These modules are performing well. No immediate changes needed.

---

## Implementation Plan

### Phase 1: Create Improved Prompts (Priority Order)

1. **M04_V2** - Fix case-insensitive matching (highest impact)
2. **M01_V4** - Fix product line handling and deduplication
3. **M01A_V3** - Fix QWERTY adjacency typos

### Phase 2: Upload to Braintrust

✅ **COMPLETED (2026-01-20)**

```bash
# Uploaded successfully:
python scripts/upload/upload_prompts.py --file prompts/modules/single/m04_v2_classify_competitor_brand_keywords.md  # ✅
python scripts/upload/upload_prompts.py --file prompts/modules/single/m01_v4_extract_own_brand_entities.md  # ✅

# Pending:
# python scripts/upload/upload_prompts.py --file prompts/modules/single/m01a_v3_extract_own_brand_variations.md
```

**Braintrust Slugs:**
- M04_V2: `m04-v2-classify-competitor-brand-keywords`
- M01_V4: `m01-v4-extract-own-brand-entities`

### Phase 3: Run Experiments

| Prompt | Dataset | Model | Expected Improvement |
|--------|---------|-------|---------------------|
| M04_V2 | 150126 | gpt-4o-mini | +15-20% pass rate |
| M01_V4 | 150126 | gpt-4o-mini | +20-25% pass rate |
| M01A_V3 | 150126 | gpt-4o-mini | +30-40% pass rate |

### Phase 4: Evaluate & Iterate

1. Run LLM-as-a-Judge evaluation
2. Analyze new failures
3. Iterate on prompts

---

## Appendix: File Locations

### Prompts
- `/prompts/modules/single/m01_v3_extract_own_brand_entities.md` (current)
- `/prompts/modules/single/m01a_v2_extract_own_brand_variations.md` (current)
- `/prompts/modules/single/m04_v1_classify_competitor_brand_keywords.md` (current)

### Judge Results
- `/evaluation_KD/evaluation_experimentV5/judge_results/`

### Experiment Results (CSV)
- `/experiment_results/M01_ExtractOwnBrandEntities/`
- `/experiment_results/M04_ClassifyCompetitorBrandKeywords/`

### Scripts
- `/scripts/upload/upload_prompts.py` - Upload to Braintrust
- `/scripts/braintrust_download.py` - Download from Braintrust
