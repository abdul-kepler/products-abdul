# Comprehensive Analysis: Low Match (<80%) Samples

## Executive Summary

Analyzed **400 samples** where Expected vs Actual Match < 80% (40.4% of all evaluations).

**Key Finding:** Low match percentage does NOT always indicate failure. Many cases (216 PASS vs 184 FAIL) show the model produced valid but different outputs.

---

## Issue Categories Identified

### 1. DATASET ISSUE - Wrong Expected Output (Critical)

**Affected Modules:** M04, M12b, M05

**Pattern:** Expected output is incorrect or doesn't match the rubric's intent.

| Module | Issue | Evidence |
|--------|-------|----------|
| **M04** | Expected=CB but keyword has no competitor brand | "oven mitts oxo" - OXO is a real brand but not in competitor list. Expected says CB, model returns null (correct behavior) |
| **M12b** | Expected=null but model correctly classifies as R | Keywords like "waterproof down jacket men" are clearly Relevant, but expected is null |
| **M05** | Inconsistent expected values | Same keyword type has different expected outputs |

**Impact:**
- M04: 36 samples affected, 39% pass rate due to wrong expected
- M12b: 60 samples with null expected but R/S/C actual (95% still pass!)

**Recommendation:**
- Review and fix expected outputs in dataset
- M04: Add OXO, Blue-Q to competitor list OR change expected to null
- M12b: Fill in missing expected classifications

---

### 2. RUBRIC ISSUE - Multiple Valid Outputs Acceptable

**Affected Modules:** M01, M01a, M12

**Pattern:** Different outputs are equally valid, but match % is calculated on exact string comparison.

| Module | Example | Why Both Are Valid |
|--------|---------|-------------------|
| **M01** | Expected: ["JBL", "JBL Vibe", "JLB"...] vs Actual: ["JBL", "jbl", "JLB"...] | Both extract the brand correctly, just different variations |
| **M01a** | 66% match but all variations are valid typos | Order and specific typos can differ |
| **M12** | Reasoning text differs but conclusion is same | Different wording, same decision |

**Impact:**
- M01: 50 samples, 70% pass despite 23% match
- M01a: 20 samples, 80% pass despite 66% match

**Recommendation:**
- Match % metric is misleading for list/set outputs
- Consider semantic similarity or set-based comparison
- Trust LLM Judge verdict over match % for these modules

---

### 3. PROMPT ISSUE - Model Output Format Wrong

**Affected Modules:** M08, M10, M06

**Pattern:** Model understands the task but outputs in wrong format/structure.

| Module | Expected Format | Actual Format | Issue |
|--------|-----------------|---------------|-------|
| **M08** | `{attr: rank}` structure | Missing ranks or wrong structure | Prompt doesn't enforce format |
| **M10** | "Listening to audio" (3-6 words, no adjectives) | "audio listening for music and calls" | Contains extra words, wrong structure |
| **M06** | 3-level hierarchy | Missing levels | Prompt doesn't enforce 3 levels |

**M10 Detailed Analysis:**

| ASIN | Expected | Actual | Issue |
|------|----------|--------|-------|
| JBL Earbuds | "Listening to audio" | "audio listening for music and calls" | Contains "for music and calls" - extra features |
| Water Bottle | "Carrying drinks for hydration" | "portable drink hydration storage" | "portable" is adjective, "storage" is noun not function |

**Impact:**
- M10: 30 samples, only 13% pass (26 FAIL)
- M08: 30 samples, 40% pass
- M06: 12 samples, 42% pass

**Recommendation:**
- M10: Add few-shot examples showing exact format
- M08: Restructure prompt to enforce `{attribute: rank}` output
- M06: Add explicit "MUST have exactly 3 levels" instruction

---

### 4. MODEL ERROR - Genuine Classification Mistakes

**Affected Modules:** M04, M15, M11

**Pattern:** Model makes incorrect classification decisions.

| Module | Error Type | Example |
|--------|------------|---------|
| **M04** | Missed known brand | "oxo oven mitts" - OXO is a known brand but not detected |
| **M15** | Wrong substitute detection | Incorrectly marking non-substitutes as S |
| **M11** | Over-identifying constraints | Listing preferences as hard constraints |

**M04 Known Brands Issue:**
```
Keyword: "oxo oven mitts"
Expected: CB (because OXO is a real brand)
Actual: null
Judge: FAIL - "OXO is a known kitchenware brand but not detected"
```

**Impact:**
- M04: 22 FAIL cases
- M15: 29 FAIL cases
- M11: 13 FAIL cases

**Recommendation:**
- M04: Enhance prompt to detect common brands beyond provided list
- M15: Improve substitute vs complementary distinction
- M11: Add clearer examples of hard vs soft constraints

---

### 5. VALID DIFFERENCE - Model Correct, Just Different

**Affected Modules:** M12b, M01, M12

**Pattern:** Model output is correct but uses different valid values.

| Module | Scenario | Verdict |
|--------|----------|---------|
| **M12b** | Model outputs R, expected is null (missing) | PASS - R is valid |
| **M01** | Different brand variations generated | PASS - all valid variations |
| **M12** | Different reasoning wording | PASS - same conclusion |

**Impact:**
- M12b: 57/60 PASS despite 0% match (95%)
- These are false "low match" alerts

**Recommendation:**
- No action needed - model is correct
- Improve expected outputs in dataset

---

## Summary Table by Issue Type

| Issue Type | Modules | Samples | Action Required |
|------------|---------|---------|-----------------|
| **Dataset Issue** | M04, M12b, M05 | ~108 | Fix expected outputs |
| **Rubric Issue** | M01, M01a, M12 | ~130 | Accept as valid; improve match metric |
| **Prompt Issue** | M08, M10, M06 | ~72 | Fix prompts (Priority!) |
| **Model Error** | M04, M15, M11 | ~64 | Improve prompts & examples |
| **Valid Difference** | M12b, M01 | ~26 | No action - model correct |

---

## Priority Actions

### P0 - Fix Dataset (Before next evaluation)
1. M04: Review expected=CB cases where model returns null
2. M12b: Fill missing expected classifications
3. M05: Standardize expected outputs

### P1 - Fix Prompts (Critical modules)
1. M10: Add explicit format examples (13% pass rate)
2. M08: Enforce rank structure (39% pass rate)
3. M06: Require 3-level hierarchy (50% pass rate)

### P2 - Enhance Model Detection
1. M04: Add common brand detection beyond provided list
2. M15: Improve substitute identification criteria
3. M11: Clarify hard constraint definition

### P3 - Improve Evaluation Metrics
1. Replace exact match % with semantic similarity for list outputs
2. Add set-based comparison for M01, M01a variations
3. Consider judge verdict as primary metric, not match %

---

## Conclusion

**Low match ≠ failure.** The 70.5% overall pass rate is accurate because:
- Many "low match" cases are valid alternative outputs (M01, M12b)
- Dataset has incorrect expected values (M04, M12b)
- Match % metric is inappropriate for list/set outputs

**Real issues to fix:**
1. M10 prompt (13% pass) - output format
2. M08 prompt (39% pass) - rank structure
3. M04 dataset - wrong expected values
4. M11 prompt (37% pass) - constraint definition
