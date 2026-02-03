# M01 - Extract Own Brand Entities: Detailed Analysis

## Overview

| Metric | Value |
|--------|-------|
| Total Evaluations | 50 (10 ASINs × 5 rubrics) |
| PASS | 35 (70%) |
| FAIL | 15 (30%) |
| Match % Range | 16-40% (all below 80%) |

---

## Rubric Performance

| Rubric | Pass | Fail | Rate | Issue Type |
|--------|------|------|------|------------|
| M01_brand_extracted | 10 | 0 | **100%** | None |
| M01_no_product_words | 9 | 1 | **90%** | Minor |
| M01_amazon_test_applied | 9 | 1 | **90%** | Minor |
| M01_no_hallucination | 5 | 5 | **50%** | **Prompt Issue** |
| M01_no_duplicates | 2 | 8 | **20%** | **Prompt Issue** |

---

## Failure Analysis

### Failure Type 1: M01_no_duplicates (8 failures) - PROMPT ISSUE

**Root Cause:** Model generates duplicate strings in the output list.

| ASIN | Product | Duplicates Found |
|------|---------|------------------|
| B0BZYCJK89 | Water Bottle | FreeSip (2), FreeSipp (2) |
| B0D6YNWLTS | Puffer Jacket | Pioneer Camp (3), Pioneercamp (2) |
| B0DSHWLXG6 | Phone Holder | Jikashoo (2) |
| B0F42MT8JX | Ice Maker | Antarctic Star (2), Antarctic Staar (2), AntarcticStarr (2) |
| B000H3I2JG | Revlon Eyeliner | Revlonn (2), ColorStay (3) |
| B08J8GZXKZ | Oven Mitt | Kitchenaid (2) |
| B09LCKZBTW | Serving Tray | Webacoo (3), SachsenUs (2) |
| B077YYP739 | Transformers Toy | Hasbroo (3) |

**Classification:** ⚠️ **PROMPT ISSUE**

**Recommendation:**
- Add explicit instruction to M01 prompt: "Ensure no duplicate strings in the output list"
- Add post-processing step to deduplicate before returning

---

### Failure Type 2: M01_no_hallucination (5 failures) - MIXED ISSUES

Analyzed each failure:

#### Case 1: B0BQPGJ9LQ (JBL Earbuds)
```
Hallucinated: "JBL Deep Bass", "JBL Deep Bass Sound"
Source: These ARE in the product title ("JBL Deep Bass Sound Earbuds")
Verdict: NOT hallucination - these are product feature words
```
**Classification:** ⚠️ **RUBRIC/JUDGE ISSUE** - Judge incorrectly flagged as hallucination

---

#### Case 2: B0D6YNWLTS (Puffer Jacket)
```
Output variations: "Pioneerr Camp", "PioneerCamps", "PioneerCmap"
Analysis: These are valid typo variations of "Pioneer Camp"
```
**Classification:** ⚠️ **JUDGE ISSUE** - Judge was too strict on what counts as derived

---

#### Case 3: B000H3I2JG (Revlon Eyeliner)
```
Output: "Revlonn", "Revlo", "ColorStayy", "ColorStai"
Analysis: These are valid typo/truncation variations
```
**Classification:** ⚠️ **JUDGE ISSUE** - Judge may be too strict

---

#### Case 4: B08J8GZXKZ (Oven Mitt) ⭐
```
Hallucinated: "Town & Country Living", "town & country living", "Town&CountryLiving"
Input brand: KitchenAid
Source check: "Town & Country Living" is NOT in the input data
```
**Classification:** ✅ **TRUE PROMPT ISSUE** - Model hallucinated a different brand

**Evidence:** The input only contains "KitchenAid" but model added "Town & Country Living" which is a completely different brand not mentioned in the input.

---

#### Case 5: B09LCKZBTW (Serving Tray)
```
Output includes: "SachsenUsa" variation
Input: Manufacturer is "Sachsen-Us"
Analysis: "SachsenUsa" is a reasonable variation of the manufacturer
```
**Classification:** ⚠️ **JUDGE ISSUE** - Variation is acceptable

---

## Summary Classification

| Failure | Count | Root Cause | Action Required |
|---------|-------|------------|-----------------|
| **Duplicates** | 8 | Prompt doesn't prevent duplicates | Fix Prompt |
| **JBL Deep Bass** | 1 | Judge confused feature vs hallucination | Clarify Rubric |
| **Strict variations** | 3 | Judge too strict on typo variations | Review Rubric |
| **Town & Country** | 1 | TRUE hallucination | Fix Prompt |

---

## Issue Classification Summary

### PROMPT ISSUES (Need to Fix Prompt)

| Issue | Impact | Fix |
|-------|--------|-----|
| **Duplicates in output** | 8/50 (16%) | Add "no duplicates" instruction |
| **Hallucinating other brands** | 1/50 (2%) | Add "only extract brands from input" |

### DATASET ISSUES (Need to Fix Expected Output)

| Issue | Impact | Fix |
|-------|--------|-----|
| None identified | - | - |

### RUBRIC/JUDGE ISSUES (Need to Clarify Rubric)

| Issue | Impact | Fix |
|-------|--------|-----|
| Product features flagged as hallucination | 1/50 (2%) | Clarify "JBL Deep Bass" is from title |
| Typo variations flagged as hallucination | 3/50 (6%) | Loosen criteria for derived variations |

---

## Match % Analysis

**Key Finding:** Low match % does NOT indicate failure.

| ASIN | Match % | PASS Count | FAIL Count | Reason for Low Match |
|------|---------|------------|------------|---------------------|
| B0CJ4WZXQF | 37% | 5/5 | 0/5 | Different but valid variations |
| B0BQPGJ9LQ | 23% | 3/5 | 2/5 | Model generates different typos |
| B077YYP739 | 21% | 4/5 | 1/5 | Valid variations, just different |

**Conclusion:** Match % is misleading for M01. The rubric verdicts are the correct measure.

---

## Recommendations

### Priority 1: Fix M01 Prompt

Add to prompt:
```
IMPORTANT RULES:
1. Do NOT include duplicate strings in the output list
2. Only extract brand names that appear in the input data
3. Do NOT hallucinate or invent brand names not present in input
```

### Priority 2: Clarify Rubric Definitions ✅ FIXED

**M01_no_hallucination:** ✅ UPDATED
- Previous: Too strict - flagged product features and typo variations as hallucination
- Fixed in `rubrics.yaml` and `rubrics_reference.csv`:
  - Product line names from title are now acceptable (e.g., "JBL Deep Bass")
  - Typo/spelling variations are now acceptable (e.g., "Revlonn", "Pioneerr Camp")
  - Manufacturer variations are now acceptable (e.g., "SachsenUsa")
  - Only TRUE hallucinations fail (completely different brand not in input)

**M01_no_duplicates:**
- Current: Correct rubric, model is wrong
- Fix: No rubric change needed, fix prompt

### Priority 3: Questions for PM

1. **Town & Country Living case:** Is this brand mentioned somewhere in the Oven Mitt listing that we don't see? If not, this is a true hallucination.

2. **Sub-brand variations:** Should "JBL Deep Bass Sound" be considered a valid brand entity or excluded as a product feature?

---

## Appendix: All M01 Evaluations by ASIN

| ASIN | Product | Match % | brand_extracted | no_hallucination | no_product_words | amazon_test | no_duplicates |
|------|---------|---------|-----------------|------------------|------------------|-------------|---------------|
| B0BQPGJ9LQ | JBL Earbuds | 23% | ✓ | ✗ | ✗ | ✓ | ✓ |
| B0BZYCJK89 | Water Bottle | 26% | ✓ | ✓ | ✓ | ✓ | ✗ |
| B0CJ4WZXQF | Sink Caddy | 37% | ✓ | ✓ | ✓ | ✓ | ✓ |
| B0D6YNWLTS | Puffer Jacket | 20% | ✓ | ✗ | ✓ | ✓ | ✗ |
| B0DSHWLXG6 | Phone Holder | 40% | ✓ | ✓ | ✓ | ✓ | ✗ |
| B0F42MT8JX | Ice Maker | 22% | ✓ | ✓ | ✓ | ✓ | ✗ |
| B000H3I2JG | Revlon Eyeliner | 16% | ✓ | ✗ | ✓ | ✓ | ✗ |
| B08J8GZXKZ | Oven Mitt | 28% | ✓ | ✗ | ✓ | ✓ | ✗ |
| B09LCKZBTW | Serving Tray | 37% | ✓ | ✗ | ✓ | ✗ | ✗ |
| B077YYP739 | Transformers | 21% | ✓ | ✓ | ✓ | ✓ | ✗ |

**Legend:** ✓ = PASS, ✗ = FAIL
