# Keyword Classification Pipeline - Evaluation Report

**Date:** January 14, 2026
**Prepared for:** Management Review
**Status:** Evaluation Framework Complete, Ready for Human Annotation

---

## 1. Dataset Analysis

### 1.1 Current Dataset Overview

| Metric | Value |
|--------|-------|
| Total Evaluation Samples | 990 |
| Unique ASINs (Products) | 10 |
| Pipeline Modules | 19 |
| Evaluation Rubrics | 68 |

### 1.2 Dataset Gaps Identified

Our analysis revealed gaps that affect evaluation coverage:

| Category | Current State | Impact | Severity |
|----------|---------------|--------|----------|
| **X (Excluded/Constraint Violation)** | 0 samples | Cannot validate M12 constraint detection | Critical |
| **S (Substitute)** | Only 7% of M12b data | Substitute classification undertested | High |
| **N (Not Relevant)** | Very sparse | Negative cases undertested in M13-M16 | High |

### 1.3 Data Gaps Summary

```
CRITICAL GAPS (Must Address):
├── No constraint violation test cases (X category)
├── Insufficient substitute product scenarios
└── Missing negative cases for relevancy modules

MODERATE GAPS:
├── Limited ASIN diversity (only 10 products)
├── Uneven distribution across categories
└── Some modules have minimal test coverage
```

---

## 2. Evaluation Methodology

### 2.1 Research Foundation

Our evaluation framework is built on **academic best practices** from LLM-as-a-Judge research, combined with practical knowledge from evaluation courses:

#### Key Academic Principles Applied:

| Principle | Source | Our Implementation |
|-----------|--------|-------------------|
| **Binary Rubrics** | Academic research shows binary (PASS/FAIL) judgments have higher inter-rater reliability than Likert scales | All 68 rubrics use binary PASS/FAIL |
| **Explicit Criteria** | Clear pass/fail conditions reduce judge ambiguity | Each rubric has detailed Pass_Conditions and Fail_Conditions |
| **Dataset Splits** | Prevent data leakage between training and evaluation | Train (15%), Dev (45%), Test (40%) splits |
| **Balanced Evaluation Sets** | Include both easy and tricky cases | 50/50 PASS/FAIL balance in Kappa dataset |
| **Cohen's Kappa** | Standard measure for inter-rater reliability | Curated 76-sample dataset for Kappa experiment |

#### Why Binary Rubrics?

1. **Higher Agreement**: Research shows binary judgments achieve higher inter-annotator agreement than 5-point scales
2. **Clearer Decisions**: Forces clear pass/fail decision rather than ambiguous middle scores
3. **Actionable Results**: Easy to identify what needs fixing (FAIL) vs what works (PASS)
4. **Statistical Validity**: Cohen's Kappa is well-defined for binary classification

### 2.2 Dataset Split Strategy

Following evaluation best practices, we structured our data to prevent contamination:

| Split | % | Samples | Purpose |
|-------|---|---------|---------|
| **Train** | 0%* | 0 | Few-shot examples for LLM judge prompts |
| **Dev** | 57% | 568 | Iterative prompt tuning and validation |
| **Test** | 43% | 422 | Final hold-out evaluation (use once) |

*Note: Train samples were reassigned to Dev to ensure M04 coverage. New training examples needed.

---

## 3. Rubric Development & LLM Judge Results

### 3.1 Rubrics Created

We developed **68 evaluation rubrics** across all 19 pipeline modules:

| Module | Module Name | Rubrics | Description |
|--------|-------------|---------|-------------|
| M01 | Extract Own Brand Entities | 5 | Brand extraction from listings |
| M01a | Extract Own Brand Variations | 4 | Typo/case variations |
| M01b | Extract Brand Related Terms | 4 | Sub-brands, product lines |
| M02 | Classify Own Brand Keywords | 5 | OB classification |
| M03 | Generate Competitor Entities | 3 | Competitor brand generation |
| M04 | Classify Competitor Brand Keywords | 4 | CB classification |
| M05 | Classify Non-Branded Keywords | 4 | NB classification |
| M06 | Generate Product Type Taxonomy | 4 | 3-level hierarchy |
| M07 | Extract Product Attributes | 4 | Key attribute extraction |
| M08 | Assign Attribute Ranks | 3 | Importance ranking 1-5 |
| M09 | Identify Primary Intended Use | 4 | 3-6 word use phrase |
| M10 | Validate Primary Intended Use | 3 | Clean and validate use |
| M11 | Identify Hard Constraints | 3 | Non-negotiable constraints |
| M12 | Check Hard Constraint Violation | 3 | Constraint violation check |
| M12b | Combined Classification | 3 | Final R/S/C/N/X classification |
| M13 | Check Product Type | 3 | Product type match |
| M14 | Check Primary Use (Same Type) | 3 | Use case comparison |
| M15 | Check Substitute | 3 | Substitute detection |
| M16 | Check Complementary | 3 | Complementary detection |

### 3.2 LLM-as-Judge Execution Results

We ran GPT-4o-mini as an automated judge across all 990 evaluation samples:

**Overall Results:**
- **Total Evaluations:** 990
- **PASS:** 698 (70.5%)
- **FAIL:** 292 (29.5%)

### 3.3 Module Performance Summary

| Status | Modules | Pass Rate |
|--------|---------|-----------|
| **Good (≥80%)** | M12B, M05, M14, M01A, M13, M16, M02 | 80-95% |
| **Needs Work (50-79%)** | M01B, M09, M01, M12, M07, M04, M06 | 50-77% |
| **Critical (<50%)** | M15, M03, M08, M11, M10 | 13-47% |

### 3.4 Critical Rubric Failures & Recommendations

Based on LLM Judge reasoning analysis, here are the key issues and suggestions:

| Module | Rubric | Pass Rate | Issue | Recommendation |
|--------|--------|-----------|-------|----------------|
| **M10** | output_clean | 0% | Validated use contains adjectives/features | Rewrite prompt to explicitly strip adjectives |
| **M10** | describes_function | 10% | Output describes product, not function | Add examples showing function vs product description |
| **M08** | ranks_assigned | 0% | Output format doesn't match expected rank structure | Fix output parsing or restructure prompt |
| **M06** | three_level_hierarchy | 8% | Missing taxonomy levels | Enforce 3-level structure in prompt template |
| **M11** | constraints_non_negotiable | 27% | Soft preferences listed as hard constraints | Add clearer distinction examples |
| **M03** | competitor_count | 26% | Not generating 5-10 competitors | Add explicit count requirement |
| **M12** | reasoning_accurate | 15% | Reasoning doesn't explain decision | Require step-by-step reasoning |

### 3.5 Detailed Analysis Available

For row-by-row analysis of each evaluation:
- **File:** `full_evaluation_spreadsheet_20260114_134323.csv`
- **Contents:** Input data, expected output, actual output, rubric criteria, LLM verdict, and detailed reasoning
- **Use Case:** Deep-dive into specific failures to understand root causes

---

## 4. Cohen's Kappa Evaluation Setup

### 4.1 Purpose

Cohen's Kappa measures **inter-rater reliability** between human annotators. This validates whether our rubrics are:
- Clear and unambiguous
- Consistently interpretable
- Reliable for production use

**Target:** κ ≥ 0.60 (Substantial Agreement)

### 4.2 Dataset for Kappa Experiment

We created a curated dataset following academic best practices:

**File:** `cohen_kappa_experiment_dataset.csv`

| Property | Value | Rationale |
|----------|-------|-----------|
| **Total Samples** | 76 | Sufficient for reliable Kappa calculation |
| **Dataset Source** | Dev (50) + Test (26) | NO Train data to prevent artificial inflation |
| **Verdict Balance** | PASS: 38, FAIL: 38 | Perfect 50/50 to surface disagreements |
| **Module Coverage** | 19/19 (100%) | All pipeline modules represented |
| **Scenario Coverage** | 19/19 (100%) | All evaluation scenarios covered |

### 4.3 Selection Criteria Applied

| Criterion | Implementation |
|-----------|----------------|
| **Tricky/Edge Cases** | 38 samples where LLM Judge marked FAIL (ambiguous, difficult) |
| **Representative Cases** | 38 samples with clear PASS to verify consistency |
| **No Train Data** | Excludes few-shot examples to prevent artificially high agreement |
| **Stratified Sampling** | Equal representation across all modules and scenarios |

### 4.4 Annotator Instructions

Complete instructions provided in `COHEN_KAPPA_INSTRUCTIONS.md`:
- Column definitions and workflow
- Rating guidelines (PASS/FAIL criteria)
- Consensus process for disagreements
- Python script for Kappa calculation

---

## 5. Next Steps

### Immediate Actions (Before Annotation)

| # | Action | Priority | Owner | Status |
|---|--------|----------|-------|--------|
| 1 | Add X (Excluded) test cases to source data | Critical | Data Team | Pending |
| 2 | Add more S (Substitute) samples | High | Data Team | Pending |
| 3 | Add N (Not Relevant) negative cases | High | Data Team | Pending |
| 4 | Create Train split with few-shot examples | Medium | ML Team | Pending |

### Annotation Phase

| # | Action | Timeline |
|---|--------|----------|
| 1 | Distribute `cohen_kappa_experiment_dataset.csv` to 2+ annotators | Week 1 |
| 2 | Annotators complete independent evaluation | Week 1-2 |
| 3 | Calculate Cohen's Kappa | Week 2 |
| 4 | Review disagreements, refine rubrics if needed | Week 2 |

### Post-Annotation

| # | Action | Depends On |
|---|--------|------------|
| 1 | If κ < 0.60: Revise ambiguous rubrics | Kappa results |
| 2 | If κ ≥ 0.60: Proceed with full evaluation | Kappa results |
| 3 | Fix critical module prompts (M10, M08, M06) | Prompt engineering |
| 4 | Re-run LLM judge after prompt fixes | Prompt fixes |
| 5 | Final reliability characterization on Test set | All above |

---

## 6. Files Reference

| File | Purpose |
|------|---------|
| `cohen_kappa_experiment_dataset.csv` | 76 curated samples for Kappa experiment |
| `human_judge_evaluation_sheet.csv` | Full 990-sample evaluation sheet |
| `rubrics_reference.csv` | All 68 rubric definitions |
| `rubric_summary_20260114_*.csv` | Pass/fail rates by rubric |
| `full_evaluation_spreadsheet_20260114_*.csv` | Detailed row-by-row analysis |
| `module_performance_summary.csv` | Module-level performance |
| `dataset_category_balance.csv` | Category distribution analysis |
| `COHEN_KAPPA_INSTRUCTIONS.md` | Annotator instructions |

---

## 7. Summary

**What We've Built:**
- Comprehensive evaluation framework with 68 binary rubrics across 19 modules
- LLM-as-Judge pipeline with detailed reasoning capture
- Curated Cohen's Kappa dataset following academic best practices
- Complete annotator materials ready for distribution

**Key Findings:**
- Overall pass rate: 70.5%
- 7 modules performing well (≥80%)
- 5 modules need critical attention (<50%)
- Dataset imbalances identified for remediation

**Recommendation:**
Proceed with Cohen's Kappa annotation while parallel work addresses data gaps and critical module fixes.
