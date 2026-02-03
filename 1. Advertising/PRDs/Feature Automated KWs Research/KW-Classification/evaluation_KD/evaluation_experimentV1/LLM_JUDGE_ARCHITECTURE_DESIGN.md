# LLM-as-a-Judge Evaluation Architecture

**Purpose:** Design and validate the LLM-as-a-Judge evaluation architecture for the keyword tagging system before large-scale implementation.

**Type:** Exploratory / Architectural (not a delivery milestone)

---

## 1. Executive Summary

This document defines the judge architecture, roles, and validation strategy for evaluating our 19-module keyword classification pipeline. Based on academic research (LLM-as-a-Judge survey papers) and practical implementation, we recommend a **multi-role judge system** with human validation via Cohen's Kappa.

**Key Decisions:**
- Binary rubrics (PASS/FAIL) over Likert scales
- 68 rubrics across 19 modules (3-5 per module)
- GPT-4o-mini as primary judge (cost-effective, sufficient accuracy)
- Human annotation for inter-rater reliability validation
- Structured failure analysis for prompt improvement

---

## 2. Current Implementation Scope

| Metric | Value |
|--------|-------|
| ASINs (Products) | 10 |
| Unique Keywords | 102 |
| Pipeline Modules | 19 |
| Evaluation Rubrics | 68 |
| Total Evaluations | 990 |
| Overall Pass Rate | 70.5% |

### Dataset Gaps Identified

| Gap | Current | Impact |
|-----|---------|--------|
| X (Excluded) | 0 samples | Cannot validate constraint detection |
| S (Substitute) | ~4 samples | Substitute classification undertested |
| N (Not Relevant) | ~5 samples | Negative cases undertested |

**Action Required:** Add 45-60 keywords across X, S, N categories before production evaluation.

---

## 3. Judge Architecture & Roles

### 3.1 Defined Judge Roles

| Role | Purpose | Implementation Status |
|------|---------|----------------------|
| **Rubric Scorer** | Binary PASS/FAIL evaluation against explicit criteria | ✅ Implemented |
| **Failure Bucketing** | Categorize failures by root cause | ✅ Implemented (via reasoning analysis) |
| **Data Quality Auditor** | Identify dataset gaps and imbalances | ✅ Implemented |
| **Cohen's Kappa Support** | Provide structured data for human validation | ✅ Implemented |
| **Synthetic Data Assistant** | Generate edge cases for sparse categories | ⏳ Recommended |

### 3.2 Judge Role Details

#### Role 1: Rubric Scorer
**Purpose:** Evaluate each module output against binary criteria.

**Implementation:**
- 68 rubrics with explicit Pass_Conditions and Fail_Conditions
- Binary judgment (PASS/FAIL) for higher inter-rater reliability
- Detailed reasoning captured for failure analysis

**Why Binary (not Likert):**
- Academic research shows binary judgments achieve higher annotator agreement
- Forces clear decisions rather than ambiguous middle scores
- Directly actionable: FAIL = needs fixing, PASS = working

#### Role 2: Failure Bucketing
**Purpose:** Categorize failures to prioritize fixes.

**Current Failure Buckets:**

| Bucket | Modules Affected | Root Cause |
|--------|------------------|------------|
| Output Format Mismatch | M08, M10 | Prompt doesn't enforce structure |
| Missing Hierarchy Levels | M06 | Incomplete taxonomy generation |
| Reasoning Gaps | M12 | Decision not explained |
| Count Violations | M03 | Not generating required quantity |
| Feature Contamination | M09, M10 | Adjectives/features in output |

#### Role 3: Data Quality Auditor
**Purpose:** Identify dataset gaps before evaluation.

**Findings:**
- Category imbalances (X=0, S=7%, N sparse)
- Limited ASIN diversity (10 products)
- Uneven module coverage (30-100 samples per module)

#### Role 4: Cohen's Kappa Support
**Purpose:** Enable human validation of judge reliability.

**Implementation:**
- Curated 76-sample dataset (balanced 50/50 PASS/FAIL)
- Dev + Test only (no Train to prevent inflation)
- Stratified across all 19 modules and scenarios
- Structured CSV with annotator columns

#### Role 5: Synthetic Data Assistant (Recommended)
**Purpose:** Generate edge cases for sparse categories.

**Use Cases:**
- Generate X (constraint violation) keywords
- Generate S (substitute) scenarios
- Generate N (not relevant) negative cases

---

## 4. Academic Research Integration

### 4.1 Key Principles from LLM-as-a-Judge Research

| Principle | Research Finding | Our Implementation |
|-----------|------------------|-------------------|
| **Binary > Likert** | Binary judgments have higher inter-rater reliability | All 68 rubrics use PASS/FAIL |
| **Explicit Criteria** | Ambiguous rubrics cause judge inconsistency | Detailed Pass/Fail conditions for each rubric |
| **Reference-Based** | Judges perform better with ground truth | Expected outputs provided in evaluation |
| **Reasoning Capture** | Explanations improve debuggability | LLM_Judge_Reasoning column in all outputs |
| **Dataset Splits** | Prevent contamination between train/eval | Train (0%), Dev (57%), Test (43%) splits |
| **Balanced Eval Sets** | Include both easy and hard cases | 50/50 PASS/FAIL in Kappa dataset |

### 4.2 Applicable Approaches Extracted

**High Value (Implemented):**
1. Binary rubric scoring with explicit criteria
2. Structured failure categorization
3. Human-in-the-loop validation via Cohen's Kappa
4. Reasoning capture for failure analysis

**Medium Value (Recommended):**
1. Synthetic data generation for sparse categories
2. Multi-judge ensemble for ambiguous cases
3. Confidence scoring for borderline judgments

**Low Value (Rejected):**
1. Likert scale scoring (lower agreement, harder to action)
2. Single holistic score (loses granular signal)
3. Unsupervised judge (no ground truth reference)

---

## 5. Cohen's Kappa Validation Strategy

### 5.1 Purpose
Validate that our rubrics are clear, unambiguous, and consistently interpretable before large-scale use.

### 5.2 Dataset Design

| Property | Value | Rationale |
|----------|-------|-----------|
| Sample Size | 76 | Sufficient for reliable Kappa |
| Source | Dev (50) + Test (26) | No Train to prevent inflation |
| Balance | 38 PASS / 38 FAIL | Surface disagreements |
| Coverage | 19 modules, 19 scenarios | Representative |
| Selection | 50% edge cases, 50% representative | Test both easy and hard |

### 5.3 Process

```
1. Distribute identical dataset to 2+ annotators
         ↓
2. Independent annotation (no discussion)
         ↓
3. Calculate Cohen's Kappa
         ↓
4. If κ < 0.60: Revise ambiguous rubrics
   If κ ≥ 0.60: Proceed to production
         ↓
5. Document disagreements for rubric refinement
```

### 5.4 Interpretation Scale

| Kappa | Interpretation | Action |
|-------|----------------|--------|
| < 0.40 | Poor/Fair | Major rubric revision needed |
| 0.40-0.60 | Moderate | Some rubric clarification needed |
| 0.60-0.80 | Substantial | Ready for production (target) |
| > 0.80 | Almost Perfect | Excellent rubric quality |

---

## 6. Recommendations

### 6.1 What to Implement

| Priority | Recommendation | Effort | Impact |
|----------|----------------|--------|--------|
| **P0** | Run Cohen's Kappa validation | 1 week | Validates entire approach |
| **P0** | Add X, S, N test data (45-60 keywords) | 1 week | Fixes critical gaps |
| **P1** | Fix critical module prompts (M10, M08, M06) | 2-3 days each | Improves 3 worst modules |
| **P1** | Implement synthetic data generation for edge cases | 1 week | Scales test coverage |
| **P2** | Add confidence scoring to judge | 3 days | Identifies borderline cases |
| **P2** | Multi-judge ensemble for M10, M11 (worst performers) | 1 week | Reduces false positives |

### 6.2 What to Discard (Non-Goals)

| Rejected Approach | Reason |
|-------------------|--------|
| Likert scale scoring | Lower inter-rater agreement, harder to action |
| Single holistic evaluation | Loses granular module-level signal |
| Fully automated (no human validation) | Can't validate judge reliability |
| Real-time judge in production | Latency/cost concerns; batch evaluation sufficient |
| Fine-tuning judge model | Overkill for current scale; prompt engineering sufficient |

---

## 7. Evaluation Files Reference

| File | Rows | Purpose |
|------|------|---------|
| `cohen_kappa_experiment_dataset.csv` | 76 | Curated set for human validation |
| `human_judge_evaluation_sheet.csv` | 990 | Full evaluation with annotator columns |
| `rubrics_reference.csv` | 68 | All rubric definitions |
| `rubric_summary_20260114.csv` | 68 | Pass/fail rates by rubric |
| `full_evaluation_spreadsheet_20260114.csv` | 990 | Detailed row-by-row analysis |
| `module_performance_summary.csv` | 19 | Module-level performance |
| `dataset_category_balance.csv` | 21 | Category distribution |
| `COHEN_KAPPA_INSTRUCTIONS.md` | - | Annotator guide |

---

## 8. Module Performance Summary

### Good (≥80% pass rate) - 7 modules
M12B (95%), M05 (89%), M14 (88%), M01A (88%), M13 (87%), M16 (83%), M02 (80%)

### Needs Work (50-79%) - 7 modules
M01B (78%), M09 (78%), M01 (76%), M12 (65%), M07 (63%), M04 (55%), M06 (50%)

### Critical (<50%) - 5 modules
M15 (47%), M03 (46%), M08 (39%), M11 (37%), M10 (13%)

---

## 9. Next Steps

### Immediate (Week 1)
- [ ] Distribute Cohen's Kappa dataset to annotators
- [ ] Add 45-60 keywords for X, S, N categories
- [ ] Complete human annotation

### Short-term (Week 2-3)
- [ ] Calculate Kappa, refine rubrics if κ < 0.60
- [ ] Fix M10, M08, M06 prompts (critical modules)
- [ ] Re-run evaluation after fixes

### Medium-term (Week 4+)
- [ ] Implement synthetic data generation
- [ ] Scale to additional ASINs
- [ ] Production integration planning

---

## 10. Conclusion

The LLM-as-a-Judge architecture is **validated and ready for human annotation**. Key architectural decisions (binary rubrics, explicit criteria, structured failure analysis) align with academic best practices.

**Critical Path:** Cohen's Kappa validation must pass (κ ≥ 0.60) before large-scale implementation.

**Risk:** Dataset gaps (X, S, N categories) must be addressed to ensure comprehensive evaluation coverage.
