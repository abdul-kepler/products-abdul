# Evaluation Reports - Presentation Guide

## Overview

This guide helps present the LLM-as-Judge evaluation results to management. Each CSV file serves a specific purpose and highlights different aspects of model performance.

---

## 1. Dataset Category Balance (`dataset_category_balance.csv`)

**Purpose:** Shows how balanced our test data is across different classification categories.

**Key Points to Highlight:**

| Issue | Finding | Impact |
|-------|---------|--------|
| No X (Excluded) samples | 0 samples with constraint violations | Cannot validate M12 constraint detection |
| S (Substitute) sparse | Only 7% of M12b data | Substitute classification undertested |
| R (Relevant) skewed | 95.2% in M14 | Model mostly sees positive cases |
| NB dominates | 81.2% in M05 | May bias toward non-branded classification |

**Recommendation:** Need to add more diverse test cases, especially:
- Keywords that violate hard constraints (X)
- Substitute product scenarios (S)
- Negative cases for M14 (N)

---

## 2. Rubric Summary (`rubric_summary_*.csv`)

**Purpose:** Shows pass/fail rates for each evaluation criterion across all modules.

**Key Columns:**
- Module, Rubric ID, Criterion
- Total Evaluations, Pass, Fail, Pass Rate
- Failure Analysis (common issues)

**Overall Performance:** 70.3% pass rate (822 PASS / 347 FAIL)

**Top Performing (100% pass rate):**
- M01a_has_variations, M01a_first_is_canonical
- M02_correct_classification, M02_no_false_positives, M02_word_boundary_respected
- M07_correct_format, M09_word_count
- M12b_valid_classification, M12b_reasoning_provided
- M14_use_comparison, M16_companion_reasoning

**Critical Issues (<30% pass rate):**

| Rubric | Pass Rate | Root Cause |
|--------|-----------|------------|
| M08_ranks_assigned | 0.0% | Output format doesn't match expected rank structure |
| M10_output_clean | 0.0% | Validated use contains adjectives/features |
| M10_describes_function | 10.0% | Output describes product, not function |
| M06_three_level_hierarchy | 8.3% | Missing taxonomy levels |
| M12_reasoning_accurate | 15.0% | Reasoning doesn't explain decision |
| M03_competitor_count | 26.3% | Not generating 5-10 competitors |
| M07_key_attributes_captured | 25.0% | Missing important attributes |
| M02_brand_match_found | 25.0% | Failing to detect brands in keywords |

**Recommendation:** Focus prompt engineering on M06, M08, M10 modules first - they have systemic issues.

---

## 3. Full Evaluation Spreadsheet (`full_evaluation_spreadsheet_*.csv`)

**Purpose:** Detailed row-by-row evaluation data for deep-dive analysis.

**Key Columns:**
- Module, ASIN, Keyword
- Prompt Name, Prompt Description
- Input Data (full context)
- Expected Output, Actual Output
- Match % (similarity between expected and actual)
- Rubric ID, Criterion
- LLM Judge Verdict (PASS/FAIL)
- LLM Judge Reasoning

**How to Use:**
1. Filter by `Verdict = FAIL` to see all failures
2. Filter by Module to analyze specific pipeline stages
3. Sort by `Match %` to find worst mismatches
4. Read `Reasoning` column to understand why judge failed it

**Key Metrics:**
- Total rows: 990
- PASS: 698 (70.5%)
- FAIL: 292 (29.5%)

---

## 4. Rubrics Reference (`rubrics_reference.csv`)

**Purpose:** Documentation of all 68 evaluation criteria used by the LLM judge.

**Key Columns:**
- Module, Module Description
- Rubric ID, Criterion
- Check (what is being evaluated)
- Pass Conditions (what constitutes success)
- Fail Conditions (what constitutes failure)

**How to Use:**
- Reference when reviewing failures
- Use to understand what each rubric measures
- Share with prompt engineers for optimization

---

## Complete Module Performance

### All 19 Modules (sorted by pass rate)

| Module | Module Name | Pass | Fail | Rate | Status |
|--------|-------------|------|------|------|--------|
| M12B | Combined Classification | 57 | 3 | **95.0%** | ✅ Good |
| M05 | Classify Non-Branded Keywords | 71 | 9 | **88.8%** | ✅ Good |
| M14 | Check Primary Use (Same Type) | 53 | 7 | **88.3%** | ✅ Good |
| M01A | Extract Own Brand Variations | 70 | 10 | **87.5%** | ✅ Good |
| M13 | Check Product Type | 52 | 8 | **86.7%** | ✅ Good |
| M16 | Check Complementary | 50 | 10 | **83.3%** | ✅ Good |
| M02 | Classify Own Brand Keywords | 80 | 20 | **80.0%** | ✅ Good |
| M01B | Extract Brand Related Terms | 62 | 18 | 77.5% | ⚠️ Needs Work |
| M09 | Identify Primary Intended Use | 31 | 9 | 77.5% | ⚠️ Needs Work |
| M01 | Extract Own Brand Entities | 76 | 24 | 76.0% | ⚠️ Needs Work |
| M12 | Check Hard Constraint Violation | 39 | 21 | 65.0% | ⚠️ Needs Work |
| M07 | Extract Product Attributes | 30 | 18 | 62.5% | ⚠️ Needs Work |
| M04 | Classify Competitor Brand Keywords | 44 | 36 | 55.0% | ⚠️ Needs Work |
| M06 | Generate Product Type Taxonomy | 24 | 24 | 50.0% | ⚠️ Needs Work |
| M15 | Check Substitute | 28 | 32 | 46.7% | ❌ Critical |
| M03 | Generate Competitor Entities | 26 | 31 | 45.6% | ❌ Critical |
| M08 | Assign Attribute Ranks | 14 | 22 | **38.9%** | ❌ Critical |
| M11 | Identify Hard Constraints | 11 | 19 | **36.7%** | ❌ Critical |
| M10 | Validate Primary Intended Use | 4 | 26 | **13.3%** | ❌ Critical |

### Summary by Status

| Status | Count | Modules |
|--------|-------|---------|
| ✅ Good (≥80%) | 7 | M01A, M02, M05, M12B, M13, M14, M16 |
| ⚠️ Needs Work (50-79%) | 7 | M01, M01B, M04, M06, M07, M09, M12 |
| ❌ Critical (<50%) | 5 | M03, M08, M10, M11, M15 |

---

## Executive Summary Slide

```
┌─────────────────────────────────────────────────────────────────┐
│                 KEYWORD CLASSIFICATION EVALUATION                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Overall Pass Rate:  70.3%  (822/1169 evaluations)              │
│                                                                  │
│  ✅ GOOD (7 modules ≥80%)        ❌ CRITICAL (5 modules <50%)    │
│  ─────────────────────           ────────────────────────        │
│  • M12B Combined Class (95%)     • M10 Validate Use (13%)        │
│  • M05 Non-Branded (89%)         • M11 Hard Constraints (37%)    │
│  • M14 Same Type Use (88%)       • M08 Attribute Ranks (39%)     │
│  • M01A Brand Variations (88%)   • M03 Competitors (46%)         │
│  • M13 Product Type (87%)        • M15 Substitute (47%)          │
│  • M16 Complementary (83%)                                       │
│  • M02 Own Brand (80%)                                           │
│                                                                  │
│  ⚠️  NEEDS WORK (7 modules 50-79%)                               │
│  ─────────────────────────────────                               │
│  M01 (76%), M01B (78%), M04 (55%), M06 (50%),                   │
│  M07 (63%), M09 (78%), M12 (65%)                                │
│                                                                  │
│  📋 PRIORITY FIXES                                               │
│  ─────────────                                                   │
│  1. M10 - Validate Use prompt (13% pass rate)                    │
│  2. M11 - Hard Constraints logic (37% pass rate)                 │
│  3. M08 - Attribute Ranking format (39% pass rate)               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Presentation Order

1. **Start with Dataset Balance** - Set context about test data quality
2. **Show Rubric Summary** - High-level performance overview
3. **Drill into Full Spreadsheet** - Show specific failure examples
4. **Reference Rubrics** - Explain evaluation criteria if asked

---

## Files Location

All files are in: `evaluation/evaluation_reports/`

| File | Description |
|------|-------------|
| `dataset_category_balance.csv` | Test data distribution |
| `rubric_summary_20260114_*.csv` | Per-rubric pass/fail stats |
| `full_evaluation_spreadsheet_20260114_*.csv` | Detailed evaluation data |
| `rubrics_reference.csv` | Rubric definitions |

---

## Questions Manager May Ask

**Q: Why is overall pass rate only 70%?**
A: Three modules (M06, M08, M10) have systemic prompt issues causing near-0% pass rates. Fixing these would significantly improve overall score.

**Q: Which modules are production-ready?**
A: M02 (Own Brand), M05 (Non-Branded), M12b (Combined Classification), M13-M16 (Relevancy) are performing well (>70%).

**Q: What's blocking us?**
A: 1) Prompt template issues in M06/M08/M10, 2) Missing test data for edge cases (X, S categories).

**Q: How long to fix?**
A: Prompt fixes: 1-2 days per module. Dataset augmentation: depends on data availability.
