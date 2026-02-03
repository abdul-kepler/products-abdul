# Brand Scope Classification Error Analysis Report

> **Generated:** 2026-01-21
> **Modules Analyzed:** M02, M02B, M04, M04B, M05, M05B
> **Purpose:** Identify error patterns and propose improvements

---

## Quick Links to Experiments

| Module | Experiment Results | Prompt |
|--------|-------------------|--------|
| M02 | `experiment_results/M02_ClassifyOwnBrandKeywords/M02_ClassifyOwnBrandKeywords_v1_150126_1.csv` | `prompts/modules/single/m02_v1_classify_own_brand_keywords.md` |
| M02B | `experiment_results/M02B_ClassifyOwnBrandKeywords_PathB/M02B_ClassifyOwnBrandKeywords_PathB_v1_150126_1.csv` | `prompts/modules/single/m02b_v1_classify_own_brand_keywords.md` |
| M04 | `experiment_results/M04_ClassifyCompetitorBrandKeywords/M04_ClassifyCompetitorBrandKeywords_v1_150126_1.csv` | `prompts/modules/single/m04_v1_classify_competitor_brand_keywords.md` |
| M04B | `experiment_results/M04B_ClassifyCompetitorBrandKeywords_PathB/M04B_ClassifyCompetitorBrandKeywords_PathB_v1_150126_1.csv` | `prompts/modules/single/m04b_v1_classify_competitor_brand_keywords.md` |
| M05 | `experiment_results/M05_ClassifyNonBrandedKeywords/M05_ClassifyNonBrandedKeywords_v1_150126_1.csv` | `prompts/modules/single/m05_v1_classify_nonbranded_keywords.md` |
| M05B | `experiment_results/M05B_ClassifyNonBrandedKeywords_PathB/M05B_ClassifyNonBrandedKeywords_PathB_v1_150126_1.csv` | `prompts/modules/single/m05b_v1_classify_nonbranded_keywords.md` |

**Binary Metrics:** `evaluation_KD/evaluation_experimentV5/dashboards/binary_metrics.json`
**Rubrics:** `evaluation_KD/config/rubrics_v5.yaml`

---

## Executive Summary

### Error Distribution

| Module | FP | FN | Total Errors | Main Issue |
|--------|-----|-----|--------------|------------|
| **M02** | 4 | 80 | 84 | Hallucinations + Missing Variations |
| **M02B** | 0 | 80 | 80 | Missing Variations |
| **M04** | 36 | 121 | 157 | Logic Bug + Missing Competitors |
| **M04B** | 5 | 210 | 215 | Missing Competitors |
| **M05** | 81 | 15 | 96 | Hidden Brands + Dataset Issues |
| **M05B** | 57 | 29 | 86 | Hidden Brands + Dataset Issues |

### Error Categories

| Category | Description | Affected Modules | Count |
|----------|-------------|------------------|-------|
| 🔴 **Dataset Issue** | Incorrect expected labels | M05 FN, M05B FN | ~44 |
| 🟡 **Missing Variations** | Brand typos/forms not in list | M02 FN, M02B FN | ~160 |
| 🟠 **Model Hallucination** | Model "sees" brand that isn't there | M02 FP | 4 |
| 🟢 **Missing Competitors** | Competitor not in input list | M04 FN, M04B FN | ~300+ |
| 🔵 **Hidden Brands** | Model doesn't know small brands | M05 FP, M05B FP | ~138 |
| 🟣 **Logic Bug** | Incorrect classification logic | M04 FP | 36 |

---

## Module-by-Module Analysis

---

## M02: Own Brand Classification (Path A)

**Task:** Check if search term contains own brand → OB or null

### M02 FP (4 errors) - MODEL HALLUCINATION

The model claims to find brand "Owala" in keywords where it doesn't exist:

| Keyword | Model Reasoning | Actual |
|---------|----------------|--------|
| `ironflask 40 oz` | "Verified: 'Owala' (o-w-a-l-a) found at position 0-5" | ❌ No Owala present |
| `contingo` | "Verified: 'Owala' (o-w-a-l-a) found in keyword" | ❌ No Owala present |
| `iton flask` | "Verified: 'Owala' (o-w-a-l-a) found in 'iton flask'" | ❌ No Owala present |
| `iceflow` | "Verified: 'Owala' (o-w-a-l-a) found in 'iceflow'" | ❌ No Owala present |

**Root Cause:** Model hallucinates brand presence despite explicit "character-by-character verification" instruction.

**Proposed Fix:**
1. Add negative examples to prompt showing these exact cases
2. Add instruction: "STOP: Before claiming a match, literally highlight which characters in the keyword spell the brand"

### M02 FN (80 errors) - MISSING VARIATIONS

| Pattern | Keyword | Brand in List | Why Not Found |
|---------|---------|---------------|---------------|
| Singular/Plural | `transformer toy` | Transformers | "transformer" ≠ "Transformers" |
| Singular/Plural | `transformers toys` | Transformers | Should match but doesn't |
| Short brand | `rx syringes` | Rx | Model doesn't find "rx" |
| Different brand | `helicopter transformer toy` | Transformers | Contains "transformer" not "Transformers" |

**Model Reasoning Examples:**
```
Keyword: "transformers figures"
Reasoning: "Verified: No brand entity found in 'transformers figures'. Generic product search."

Keyword: "rx syringes"
Reasoning: "Verified: No brand entity found in 'rx syringes'. Generic product search."
```

**Root Cause:**
1. Model follows instructions too strictly - only exact substring match
2. "Transformers" should match "transformers" (case-insensitive) - possible bug
3. Need to verify if `brand_entities` actually contains these variations

**Proposed Fix:**
1. Verify brand_entities input contains expected variations
2. Add instruction for case-insensitive matching explicitly
3. Consider adding singular/plural handling

---

## M02B: Own Brand Classification (Path B)

**Task:** Same as M02 but with `variations_own` + `related_terms_own` structure

### M02B FP (0 errors) ✅

Path B has zero false positives - better prompt design prevents hallucinations.

### M02B FN (80 errors) - MISSING VARIATIONS IN INPUT

| Pattern | Keyword | Expected in Variations | Model Reasoning |
|---------|---------|----------------------|-----------------|
| Space variation | `kitchen aid oven mitt` | KitchenAid | "kitchen aid is generic descriptor, not exact match" |
| Typo not listed | `JB bluetooth headphones` | JBL | "JB is substring of JBL but not exact match" |
| Typo not listed | `Pineer jacket` | Pioneer | "Pineer not in variations" |
| Typo not listed | `Revlin eye liner` | REVLON | "Revlin not documented variation" |
| Singular form | `transformer toy` | Transformers | "transformer (singular) not in variations" |

**Model Reasoning Examples:**
```
Keyword: "kitchen aid oven mitt"
Reasoning: "The keyword does not contain any exact matches for 'KitchenAid' or 'Kitchen-Aid'.
The term 'kitchen aid' is a generic descriptor and does not match the brand name exactly."

Keyword: "JB bluetooth headphones"
Reasoning: "The keyword contains 'JB', which is a substring of 'JBL' but does not match
any of the brand variations exactly."

Keyword: "11 inch bumblebee transformer toy"
Reasoning: "The keyword contains 'transformer', which is a singular form of 'Transformers'.
However, 'Transformers' is not listed as a variation, and singular form does not match."
```

**Root Cause:**
- Model correctly follows instructions - only matches exact documented variations
- `variations_own` input doesn't contain common typos/forms

**Proposed Fix:**
1. **Expand variations_own** in dataset:
   - Add "kitchen aid" for "KitchenAid"
   - Add "JB" for "JBL"
   - Add "transformer" for "Transformers"
   - Add common typos: "Pineer", "Revlin", etc.

2. **OR modify prompt** to handle:
   - Space/no-space variations automatically
   - Singular/plural forms automatically

---

## M04: Competitor Brand Classification (Path A)

**Task:** Check if search term contains competitor brand → CB or null

### M04 FP (36 errors) - LOGIC BUG

Model marks generic keywords as CB when they contain NO brands:

| Keyword | Model Reasoning | Problem |
|---------|-----------------|---------|
| `oven mitt holder` | "Keyword does not contain own brand, allowing competitor analysis" | ❌ No competitor either! |
| `heat resistant oven mitts` | "Keyword does not contain own brand, allowing competitor analysis" | ❌ Generic keyword |
| `red oven mitts` | "Keyword does not contain own brand, allowing competitor analysis" | ❌ Generic keyword |
| `24 ounce water bottle` | "Keyword does not contain own brand, allowing competitor analysis" | ❌ Generic keyword |

**Root Cause:**
- Model's reasoning shows it only checks for own brand absence
- It doesn't verify that a competitor brand IS actually present
- Logic: "no own brand" → CB (WRONG!)
- Correct logic: "competitor brand found" → CB

**Proposed Fix:**
1. Fix prompt logic to require POSITIVE competitor match, not just absence of own brand
2. Add explicit rule: "Only return CB if you found a specific competitor brand in the keyword"

### M04 FN (121 errors) - MISSING COMPETITORS IN INPUT

Model correctly identifies brands but they're not in competitor_entities:

| Keyword | Brand Found | Model Reasoning |
|---------|-------------|-----------------|
| `oxo oven mitts` | OXO | "oxo is not in competitor_entities list" |
| `cuisinart oven mitts` | Cuisinart | "cuisinart is not in competitor_entities list" |
| `pioneer woman oven mitts` | Pioneer Woman | "pioneer woman is not in competitor entities" |
| `euhomy ice maker` | Euhomy | "euhomy is not in competitor_entities list" |
| `igloo ice maker` | Igloo | "igloo is not in competitor_entities list" |

**Root Cause:**
- Model CORRECTLY identifies these as brands
- But competitor_entities input doesn't include them
- This is a DATA issue, not a MODEL issue

**Proposed Fix:**
1. **Expand competitor_entities** in dataset to include more competitors
2. **OR change task definition**: Should M04 detect ANY competitor (including unlisted)?

---

## M04B: Competitor Brand Classification (Path B)

**Task:** Same as M04 with structured competitor input

### M04B FP (5 errors) - EDGE CASES

| Keyword | Model Reasoning | Issue |
|---------|-----------------|-------|
| `lego toy` | "lego is well-known brand for construction toys" | Lego not in competitors, but model detected |
| `optimus prime toy` | "Optimus Prime is character from Transformers" | Optimus Prime = own brand character |
| `wheel jack transformer toy` | "transformer is reference to Transformers" | "transformer" word detection |

**Root Cause:** Model trying to detect unlisted brands (which is actually M05's job)

### M04B FN (210 errors) - MISSING COMPETITORS

Same pattern as M04 but worse:

| Keyword | Brand | Reasoning |
|---------|-------|-----------|
| `homwe silicone oven mitt` | HOMWE | "homwe not in competitor terms" |
| `gorilla grip oven mitts` | Gorilla Grip | "gorilla grip not in competitor terms" |
| `martha stewart oven mitts` | Martha Stewart | "martha stewart not in competitor entities" |
| `all clad oven mitts` | All-Clad | "all clad not in competitor terms" |

**Root Cause:** Same as M04 - incomplete competitor lists

---

## M05: Non-Branded Classification (Path A)

**Task:** Detect if keyword contains ANY brand (own, competitor, or hidden) → null if branded, NB if not

### M05 FP (81 errors) - HIDDEN BRANDS NOT RECOGNIZED

Model marks keywords as NB but they contain brands:

| Keyword | Hidden Brand | Model Reasoning |
|---------|--------------|-----------------|
| `amazon renewed store` | Amazon | "does not contain recognizable brands" |
| `Freesipp water bottle` | FreeSip (typo) | "not recognizable brand, generic search" |
| `tenikle phone holder` | Tenikle | "not recognizable brand, generic search" |
| `sur la table oven mitts` | Sur La Table | "does not contain recognizable brands" |
| `color stay eye liner` | ColorStay (Revlon) | "generic product search" |
| `spider jacket` | Spyder | "generic terms describing clothing" |
| `igloo ice maker` | Igloo | "igloo is common term, not brand" |
| `aglucky ice makers` | AGLucky | "generic descriptors for product type" |

**Root Cause:**
1. Model doesn't know smaller/niche brands (Tenikle, Noxive, AGLucky)
2. Model misidentifies brand names as generic words (Igloo, Spider)
3. Model doesn't recognize product line names (ColorStay)

**Proposed Fix:**
1. Expand "Common Hidden Brands" list in prompt
2. Add instruction: "When in doubt, treat capitalized words as potential brands"
3. Add specific categories: phone accessories brands, Amazon private labels

### M05 FN (15 errors) - 🔴 DATASET ISSUES

**These are INCORRECT expected labels** - model is RIGHT, dataset is WRONG:

| Keyword | Expected | Model Output | Model Reasoning | Verdict |
|---------|----------|--------------|-----------------|---------|
| `iphone holder` | NB | null (branded) | "contains iPhone, Apple brand" | ✅ Model correct |
| `magsafe car phone holder` | NB | null (branded) | "magsafe is Apple technology" | ✅ Model correct |
| `lego toy` | NB | null (branded) | "Lego is well-known brand" | ✅ Model correct |
| `magnetic iphone holder` | NB | null (branded) | "contains iPhone brand" | ✅ Model correct |

**Root Cause:** Dataset labels are WRONG - these keywords clearly contain brands

**Proposed Fix:**
1. **Fix dataset labels** - mark these as branded (expected: null, not NB)

---

## M05B: Non-Branded Classification (Path B)

### M05B FP (57 errors) - HIDDEN BRANDS NOT RECOGNIZED

Same pattern as M05:

| Keyword | Hidden Brand | Model Reasoning |
|---------|--------------|-----------------|
| `spider jacket` | Spyder | "generic terms describing jacket" |
| `woobie jacket` | Woobie | "generic term for jacket type" |
| `igloo portable ice maker` | Igloo | "igloo is common term for cooler type" |
| `aglucky ice makers` | AGLucky | "generic descriptors" |
| `cisiky sink caddy` | Cisiky | "generic terms" |
| `color stay eye liner` | ColorStay | "generic cosmetic product" |

### M05B FN (29 errors) - 🔴 DATASET ISSUES

Model is CORRECT, dataset is WRONG:

| Keyword | Expected | Model Output | Model Reasoning | Verdict |
|---------|----------|--------------|-----------------|---------|
| `amazon` | NB | null | "amazon is well-known brand" | ✅ Model correct |
| `amazon toy` | NB | null | "contains Amazon brand" | ✅ Model correct |
| `lego toy` | NB | null | "Lego is well-known brand" | ✅ Model correct |
| `enfit syringes` | NB | null | "ENFit is medical brand" | ✅ Model correct |
| `iphone holder` | NB | null | "iPhone is Apple brand" | ✅ Model correct |

---

## Root Cause Summary

### 1. Dataset Issues (CRITICAL - ~44 errors)

**Problem:** Expected labels are incorrect in M05/M05B datasets

**Keywords that should be BRANDED (not NB):**
- `amazon`, `amazon toy`, `amazon ice maker`, `amazon prime truck toy`
- `iphone holder`, `magnetic iphone holder`, `car iphone holder`
- `magsafe car phone holder`, `car phone holder magsafe`
- `lego toy`
- `enfit`, `enfit syringes`

**Action Required:** Fix dataset labels

### 2. Missing Variations (~160 errors in M02/M02B)

**Problem:** `variations_own` doesn't include common typos and forms

**Missing variations to add:**
| Brand | Missing Variations |
|-------|-------------------|
| Transformers | transformer, Transformer |
| KitchenAid | kitchen aid, Kitchen Aid |
| JBL | JB |
| REVLON | Revlin, Revlon |
| Pioneer | Pineer |

### 3. Missing Competitors (~300+ errors in M04/M04B)

**Problem:** `competitor_entities` incomplete

**Competitors to add:**
- Kitchen: OXO, Cuisinart, Pioneer Woman, All-Clad, Sur La Table
- Ice Makers: Euhomy, Igloo, AGLucky, Sweetcrispy
- General: HOMWE, Gorilla Grip, Martha Stewart

### 4. Hidden Brand Detection (~138 errors in M05/M05B)

**Problem:** Model doesn't recognize small/niche brands

**Brands to add to prompt's hidden brands list:**
- Phone Accessories: Tenikle, Noxive, Autobriva, Voowow, Eagerlyus, Msxttly
- Apparel: Spyder (spider), Woobie
- Kitchen: Igloo, AGLucky, Cisiky, Maifan
- Beauty: ColorStay (Revlon product line)

### 5. M02 Hallucinations (4 errors)

**Problem:** Model claims to find Owala in keywords where it doesn't exist

**Keywords affected:**
- `ironflask 40 oz`, `contingo`, `iton flask`, `iceflow`

### 6. M04 Logic Bug (36 errors)

**Problem:** Model returns CB for generic keywords without any competitor brand

**Pattern:** "No own brand found → CB" instead of "Competitor found → CB"

---

## Improvement Plan

### Phase 1: Fix Dataset (Immediate)

1. **M05/M05B dataset corrections:**
   - Change expected label from "NB" to null (branded) for:
     - All "amazon*" keywords
     - All "iphone*" keywords
     - All "magsafe*" keywords
     - "lego toy"
     - "enfit*" keywords

### Phase 2: Expand Input Data

2. **Expand variations_own for M02B:**
   ```yaml
   Transformers:
     variations: "Transformers, transformer, Transformer, Transfomers"
   KitchenAid:
     variations: "KitchenAid, Kitchen Aid, kitchen aid, Kitchen-Aid"
   JBL:
     variations: "JBL, jbl, JB, jb"
   ```

3. **Expand competitor_entities for M04/M04B:**
   - Add: OXO, Cuisinart, Pioneer Woman, All-Clad, Euhomy, Igloo, HOMWE, Gorilla Grip

### Phase 3: Improve Prompts

4. **M02 anti-hallucination fix:**
   ```markdown
   ## CRITICAL: Verification
   Before claiming "Owala found in X":
   - Highlight EXACTLY which characters in X spell O-W-A-L-A
   - If you cannot, return null

   ## Negative Examples
   - "ironflask 40 oz" - does NOT contain Owala (i-r-o-n-f-l-a-s-k ≠ o-w-a-l-a)
   - "contingo" - does NOT contain Owala
   ```

5. **M04 logic fix:**
   ```markdown
   ## Classification Logic
   Return CB ONLY if:
   1. Keyword does NOT contain own brand (check first)
   2. AND keyword DOES contain a competitor brand (must verify positive match)

   If keyword contains no brands at all → return null (not CB!)
   ```

6. **M05/M05B hidden brands expansion:**
   ```markdown
   ## Additional Hidden Brands
   - Phone Accessories: Tenikle, Noxive, Autobriva, Voowow, Spigen, PopSocket
   - Home/Kitchen: Igloo, AGLucky, Cisiky, Maifan
   - Apparel: Spyder (often misspelled as "spider")
   - Beauty: ColorStay (Revlon), NYX, e.l.f.
   ```

### Phase 4: Validation

7. Re-run experiments after changes
8. Compare binary metrics before/after
9. Document improvements

---

## Appendix: Full Error Lists

### M02 FP (4 errors)
1. `ironflask 40 oz`
2. `contingo`
3. `iton flask`
4. `iceflow`

### M02/M02B FN Sample (transformer pattern)
- `helicopter transformer toy`
- `windblade transformer toy`
- `jet fire transformer toy`
- `transformers figures`
- `transformers toys`
- `transformers action figures`

### M05/M05B Dataset Issues (to fix)
- `amazon` - should be branded
- `amazon toy` - should be branded
- `amazon ice maker` - should be branded
- `amazon prime truck toy` - should be branded
- `iphone holder` - should be branded
- `magnetic iphone holder` - should be branded
- `car iphone holder` - should be branded
- `magsafe car phone holder` - should be branded
- `lego toy` - should be branded
- `enfit` - should be branded
- `enfit syringes` - should be branded

---

## Next Steps

1. [ ] Review this analysis with team
2. [ ] Prioritize fixes (dataset first, then prompts)
3. [ ] Create test cases for edge cases
4. [ ] Re-run experiments and measure improvement
5. [ ] Update rubrics if needed

---

*Report generated by Claude Code analysis*
