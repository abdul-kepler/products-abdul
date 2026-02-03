# LLM-as-a-Judge Evaluation Workflow Instructions

This document describes the complete workflow we followed to build, run, and validate the LLM-as-a-Judge evaluation system for the keyword classification pipeline.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Phase 1: Rubric Development](#2-phase-1-rubric-development)
3. [Phase 2: LLM Judge Execution](#3-phase-2-llm-judge-execution)
4. [Phase 3: Results Analysis](#4-phase-3-results-analysis)
5. [Phase 4: Failure Analysis & Rubric Refinement](#5-phase-4-failure-analysis--rubric-refinement)
6. [Phase 5: Dataset Quality Audit](#6-phase-5-dataset-quality-audit)
7. [Phase 6: Cohen's Kappa Preparation](#7-phase-6-cohens-kappa-preparation)
8. [Phase 7: Documentation & Reporting](#8-phase-7-documentation--reporting)
9. [Files Generated](#9-files-generated)
10. [Lessons Learned](#10-lessons-learned)
11. [Phase 8: Dashboard Generation](#11-phase-8-dashboard-generation)
    - [11.8 Generating Improvement Suggestions (Experimental Approach)](#118-generating-improvement-suggestions-experimental-approach)

---

## 1. Overview

### Objective
Design and validate an LLM-as-a-Judge evaluation architecture for the 19-module keyword classification pipeline before large-scale implementation.

### Scope
- 10 ASINs (products)
- 102 unique keywords
- 19 pipeline modules (M01-M16)
- 68 evaluation rubrics
- 990 total evaluations

### Tools Used
- **LLM Judge:** GPT-4o-mini
- **Evaluation Script:** `run_llm_judge.py`
- **Analysis:** Python/Pandas

---

## 2. Phase 1: Rubric Development

### 2.1 Approach

We created **binary rubrics** (PASS/FAIL) rather than Likert scales based on academic research showing:
- Higher inter-rater reliability with binary judgments
- Clearer, more actionable results
- Better suited for Cohen's Kappa validation

### 2.2 Rubric Structure

Each rubric contains:

| Field | Description | Example |
|-------|-------------|---------|
| **Module** | Pipeline module ID | M01 |
| **Rubric ID** | Unique identifier | M01_brand_extracted |
| **Criterion** | What is being evaluated | Brand Extracted |
| **Check** | Specific verification | Brand extracted from title or listing_brand field |
| **Pass Conditions** | What constitutes PASS | brand_name matches brand found in title OR listing_brand field |
| **Fail Conditions** | What constitutes FAIL | Empty output when title contains brand name |

### 2.3 Rubrics Per Module

| Module | Count | Focus Areas |
|--------|-------|-------------|
| M01 | 5 | Brand extraction, hallucination, duplicates |
| M01a | 4 | Variations, count, canonical form |
| M01b | 4 | Sub-brands, standards, manufacturer |
| M02 | 5 | Classification, matching, boundaries |
| M03 | 3 | Competitor relevance, count, hallucination |
| M04 | 4 | Classification, brand detection |
| M05 | 4 | Non-branded detection, hidden brands |
| M06 | 4 | Taxonomy hierarchy, specificity |
| M07 | 4 | Attribute extraction, format |
| M08 | 3 | Rank assignment, logic, distribution |
| M09 | 4 | Use phrase, word count, function |
| M10 | 3 | Validation, clean output |
| M11 | 3 | Constraint identification |
| M12 | 3 | Violation detection, reasoning |
| M12b | 3 | Final classification, decision tree |
| M13-M16 | 3 each | Relevancy checks |

**Total: 68 rubrics**

### 2.4 How Rubrics Were Created

1. **Analyzed each module's prompt** to understand expected behavior
2. **Identified key quality dimensions** (accuracy, format, completeness)
3. **Defined explicit pass/fail conditions** with concrete examples
4. **Cross-referenced with expected outputs** in test dataset
5. **Iterated based on initial judge results**

---

## 3. Phase 2: LLM Judge Execution

### 3.1 Execution Process

```bash
# Run LLM judge for all modules
python evaluation/run_llm_judge.py --all-modules --samples 20
```

### 3.2 Judge Configuration

| Parameter | Value |
|-----------|-------|
| Model | GPT-4o-mini |
| Temperature | 0 (deterministic) |
| Samples per module | 20 |
| Output format | JSON with verdict + reasoning |

### 3.3 Output Structure

For each evaluation:
```json
{
  "rubric_id": "M01_brand_extracted",
  "verdict": "PASS|FAIL",
  "reasoning": "Step-by-step explanation..."
}
```

### 3.4 Results Summary

| Metric | Value |
|--------|-------|
| Total Evaluations | 990 |
| PASS | 698 (70.5%) |
| FAIL | 292 (29.5%) |

---

## 4. Phase 3: Results Analysis

### 4.1 Generated Reports

1. **`rubric_summary_*.csv`** - Pass/fail rates by rubric
2. **`module_performance_summary.csv`** - Module-level performance
3. **`full_evaluation_spreadsheet_*.csv`** - Row-by-row details
4. **`dataset_category_balance.csv`** - Category distribution

### 4.2 Module Performance Classification

| Status | Criteria | Modules |
|--------|----------|---------|
| **Good** | ≥80% pass | M12B, M05, M14, M01A, M13, M16, M02 |
| **Needs Work** | 50-79% | M01B, M09, M01, M12, M07, M04, M06 |
| **Critical** | <50% | M15, M03, M08, M11, M10 |

### 4.3 Critical Rubric Failures Identified

| Rubric | Pass Rate | Root Cause |
|--------|-----------|------------|
| M10_output_clean | 0% | Output contains adjectives |
| M08_ranks_assigned | 0% | Wrong output structure |
| M06_three_level_hierarchy | 8% | Missing taxonomy levels |
| M10_describes_function | 10% | Describes product not function |
| M12_reasoning_accurate | 15% | Reasoning gaps |

---

## 5. Phase 4: Failure Analysis & Rubric Refinement

### 5.1 Low Match Analysis

Analyzed all samples with Expected vs Actual Match < 80% (400 samples).

### 5.2 Issue Categories Identified

| Issue Type | Samples | Description |
|------------|---------|-------------|
| **Dataset Issue** | ~108 | Wrong expected outputs in test data |
| **Rubric Issue** | ~130 | Multiple valid outputs acceptable |
| **Prompt Issue** | ~72 | Model output format wrong |
| **Model Error** | ~64 | Genuine classification mistakes |
| **Valid Difference** | ~26 | Model correct, just different |

### 5.3 Key Findings

**Finding 1: Dataset has wrong expected values (M04)**
```
Keyword: "oven mitts oxo"
Expected: CB ← INCORRECT
Actual: null ← CORRECT (OXO not in competitor list)
```

**Finding 2: Match % misleading for list outputs (M01)**
```
Match: 23%
Verdict: PASS
Reason: Different brand variations are equally valid
```

**Finding 3: Prompt format issues (M10)**
```
Expected: "Listening to audio"
Actual: "audio listening for music and calls"
Issue: Prompt doesn't enforce strict format
```

### 5.4 Rubric Refinements Made

1. **Clarified M04 rubric** - Null is valid when brand not in competitor list
2. **Adjusted M01 evaluation** - Accept different valid variations
3. **Identified M10 as prompt issue** - Not rubric problem

---

## 6. Phase 5: Dataset Quality Audit

### 6.1 Dataset Gaps Identified

| Gap | Current | Impact |
|-----|---------|--------|
| X (Excluded) | 0 samples | Cannot test constraint violations |
| S (Substitute) | ~4 samples | Undertested |
| N (Not Relevant) | ~5 samples | Undertested |

### 6.2 Recommendations

Add 45-60 keywords:
- 15-20 X (constraint violation) keywords
- 15-20 S (substitute) keywords
- 15-20 N (not relevant) keywords

### 6.3 Dataset Split Strategy

Following academic best practices:

| Split | % | Purpose |
|-------|---|---------|
| Train | ~15% | Few-shot examples for prompts |
| Dev | ~45% | Iterative prompt tuning |
| Test | ~40% | Final hold-out evaluation |

---

## 7. Phase 6: Cohen's Kappa Preparation

### 7.1 Purpose

Validate inter-rater reliability between human annotators before production use.

### 7.2 Dataset Curation

Created `cohen_kappa_experiment_dataset.csv` with:

| Property | Value | Rationale |
|----------|-------|-----------|
| Samples | 76 | Sufficient for reliable Kappa |
| Source | Dev + Test only | No Train to prevent inflation |
| Balance | 38 PASS / 38 FAIL | Surface disagreements |
| Coverage | 19 modules, 19 scenarios | Representative |
| Selection | 50% edge cases | Include tricky cases |

### 7.3 Selection Criteria Applied

1. **No Train data** - Prevents artificially high agreement
2. **Balanced verdicts** - 50/50 PASS/FAIL
3. **Edge cases included** - LLM FAIL cases for difficulty
4. **Stratified sampling** - All modules/scenarios covered

### 7.4 Annotator Columns

| Column | Who Fills |
|--------|-----------|
| Annotator_1_Label | Human annotator 1 |
| Annotator_1_Reasoning | Why they chose that label |
| Annotator_2_Label | Human annotator 2 |
| Annotator_2_Reasoning | Why they chose that label |
| Final_Consensus_Label | Agreed after discussion |

### 7.5 Target Kappa

| Kappa | Interpretation | Action |
|-------|----------------|--------|
| < 0.40 | Poor/Fair | Major rubric revision |
| 0.40-0.60 | Moderate | Some clarification needed |
| **≥0.60** | **Substantial** | **Ready for production** |
| > 0.80 | Almost Perfect | Excellent quality |

---

## 8. Phase 7: Documentation & Reporting

### 8.1 Reports Created

1. **EVALUATION_REPORT_FOR_MANAGEMENT.md** - Executive summary
2. **LLM_JUDGE_ARCHITECTURE_DESIGN.md** - Technical architecture
3. **LOW_MATCH_ANALYSIS_INSIGHTS.md** - Detailed failure analysis
4. **COHEN_KAPPA_INSTRUCTIONS.md** - Annotator guide
5. **PRESENTATION_GUIDE.md** - How to present results

### 8.2 Key Metrics Documented

| Metric | Value |
|--------|-------|
| Overall Pass Rate | 70.5% |
| Good Modules (≥80%) | 7 |
| Critical Modules (<50%) | 5 |
| Total Rubrics | 68 |
| Kappa Dataset Size | 76 |

---

## 9. Files Generated

### Evaluation Data Files

| File | Rows | Purpose |
|------|------|---------|
| `cohen_kappa_experiment_dataset.csv` | 76 | Human annotation |
| `human_judge_evaluation_sheet.csv` | 990 | Full evaluation data |
| `rubrics_reference.csv` | 68 | Rubric definitions |
| `rubric_summary_*.csv` | 68 | Pass/fail by rubric |
| `full_evaluation_spreadsheet_*.csv` | 990 | Detailed analysis |
| `module_performance_summary.csv` | 19 | Module performance |
| `dataset_category_balance.csv` | 21 | Category distribution |
| `low_match_analysis.csv` | 400 | Low match samples |

### Documentation Files

| File | Purpose |
|------|---------|
| `EVALUATION_REPORT_FOR_MANAGEMENT.md` | Executive report |
| `LLM_JUDGE_ARCHITECTURE_DESIGN.md` | Architecture design |
| `LOW_MATCH_ANALYSIS_INSIGHTS.md` | Failure analysis |
| `COHEN_KAPPA_INSTRUCTIONS.md` | Annotator guide |
| `PRESENTATION_GUIDE.md` | Presentation guide |
| `EVALUATION_WORKFLOW_INSTRUCTIONS.md` | This document |

---

## 10. Lessons Learned

### What Worked Well

1. **Binary rubrics** - Clearer decisions, higher agreement potential
2. **Explicit pass/fail conditions** - Reduced judge ambiguity
3. **Reasoning capture** - Essential for debugging failures
4. **Stratified Kappa dataset** - Representative sample

### What Needed Iteration

1. **Dataset expected values** - Many incorrect, required fixes
2. **Match % metric** - Misleading for list outputs
3. **Prompt format enforcement** - M10, M08, M06 need stronger prompts

### Recommendations for Future

1. **Fix dataset first** - Before running large-scale evaluation
2. **Use semantic similarity** - Instead of exact match for lists
3. **Run Kappa early** - Validate rubrics before full evaluation
4. **Iterate prompts** - For critical modules (M10, M08, M06)

---

## Workflow Summary Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    EVALUATION WORKFLOW                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Phase 1: RUBRIC DEVELOPMENT                                    │
│  ├── Analyze module prompts                                     │
│  ├── Define 3-5 binary rubrics per module                       │
│  └── Document pass/fail conditions                              │
│           ↓                                                     │
│  Phase 2: LLM JUDGE EXECUTION                                   │
│  ├── Run GPT-4o-mini on all samples                            │
│  ├── Capture verdict + reasoning                                │
│  └── Generate raw results (990 evaluations)                     │
│           ↓                                                     │
│  Phase 3: RESULTS ANALYSIS                                      │
│  ├── Calculate pass rates by rubric/module                      │
│  ├── Identify critical modules (<50%)                           │
│  └── Generate summary reports                                   │
│           ↓                                                     │
│  Phase 4: FAILURE ANALYSIS                                      │
│  ├── Analyze low match samples (<80%)                           │
│  ├── Categorize issues (dataset/rubric/prompt/model)            │
│  └── Refine rubrics based on findings                           │
│           ↓                                                     │
│  Phase 5: DATASET AUDIT                                         │
│  ├── Identify category gaps (X, S, N)                           │
│  ├── Check ASIN diversity                                       │
│  └── Define data collection needs                               │
│           ↓                                                     │
│  Phase 6: KAPPA PREPARATION                                     │
│  ├── Curate balanced 76-sample dataset                          │
│  ├── Apply selection criteria (edge cases, no Train)            │
│  └── Prepare annotator instructions                             │
│           ↓                                                     │
│  Phase 7: DOCUMENTATION                                         │
│  ├── Management report                                          │
│  ├── Architecture design                                        │
│  └── Workflow instructions (this document)                      │
│           ↓                                                     │
│  Phase 8: DASHBOARD GENERATION                                  │
│  ├── Create MODULE_ANALYSIS_DASHBOARD.html                      │
│  ├── Create MATCH_RATE_DASHBOARD.html                           │
│  ├── Update data from evaluation results                        │
│  └── Add improvement suggestions with prompt fixes              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 11. Phase 8: Dashboard Generation

### 11.1 Overview

For each experiment version, generate interactive HTML dashboards to visualize evaluation results and provide actionable insights. Dashboards are stored in the `dashboards/` folder within each experiment version directory.

### 11.2 Dashboard Types

| Dashboard | File | Purpose |
|-----------|------|---------|
| **Module Analysis Dashboard** | `MODULE_ANALYSIS_DASHBOARD.html` | Detailed per-module evaluation analysis with charts, issue breakdowns, and improvement suggestions |
| **Match Rate Dashboard** | `MATCH_RATE_DASHBOARD.html` | Expected vs Actual output matching rates across all modules |

### 11.3 Module Analysis Dashboard Features

The main analysis dashboard includes:

1. **Sidebar Navigation**
   - Module list sorted by pass rate (worst-performing first)
   - Color-coded indicators (🔴 Critical, 🟡 Medium, 🟢 Good)
   - Issue count badge per module

2. **Module Detail View**
   - Pass rate chart with PASS/FAIL breakdown
   - Issue type distribution pie chart
   - Analysis summary by verdict
   - Sample-level detail cards

3. **Improvement Suggestions Section**
   - Prioritized by criticality (Critical, High, Medium, Low)
   - Issue analysis with expected vs actual outputs
   - Specific prompt change recommendations
   - Expected impact estimates

### 11.4 Creating Dashboards for New Experiment Versions

When running a new experiment version:

```bash
# 1. Create the experiment folder structure
mkdir -p evaluation_KD/evaluation_experimentV2
mkdir -p evaluation_KD/evaluation_experimentV2/dashboards

# 2. Copy dashboard templates from previous version
cp evaluation_KD/evaluation_experimentV1/dashboards/*.html \
   evaluation_KD/evaluation_experimentV2/dashboards/

# 3. Update data in dashboards with new experiment results
# Edit the JavaScript data sections in each HTML file
```

### 11.5 Dashboard Data Structure

Each dashboard contains embedded JavaScript data that must be updated with new experiment results:

**Module Analysis Dashboard:**
```javascript
const moduleData = {
    "M01": {
        passRate: 70,
        totalSamples: 10,
        issueTypes: { "Model Correct": 7, "Prompt Issue": 2, "Model Issue": 1 }
    },
    // ... more modules
};

const improvementSuggestions = [
    {
        module: "M10",
        criticality: "Critical",
        passRate: 13,
        issueType: "Prompt Issue",
        promptChange: "Add specific instructions...",
        impact: "Expected to improve from 13% to ~60%"
    },
    // ... more suggestions
];
```

**Match Rate Dashboard:**
```javascript
const moduleData = [
    { module: "M01", exact: 0, semantic: 7, mismatch: 3, total: 10 },
    // ... more modules
];
```

### 11.6 Data Sources for Dashboards

| Data Point | Source File |
|------------|-------------|
| Pass rates | `rubric_summary_*.csv` |
| Issue types | `full_evaluation_spreadsheet_*.csv` (Issue_Type column) |
| Sample counts | Unique "Input Data" values per module |
| Expected/Actual | Individual module CSV files |
| Match rates | `full_evaluation_analysis_by_module/*.csv` |

### 11.7 Experiment Version Folder Structure

Each experiment version should maintain this structure:

```
evaluation_experimentV{N}/
├── dashboards/
│   ├── MODULE_ANALYSIS_DASHBOARD.html
│   └── MATCH_RATE_DASHBOARD.html
├── full_evaluation_analysis_by_module/
│   ├── M01_full_evaluation_with_analysis.csv
│   └── ... (one per module)
├── cohen_kappa_experiment_dataset.csv
├── full_evaluation_spreadsheet_*.csv
├── rubric_summary_*.csv
└── EVALUATION_WORKFLOW_INSTRUCTIONS.md
```

### 11.8 Generating Improvement Suggestions (Iterative Experimental Approach)

Improvement suggestions in the dashboard must be **validated through iterative experiments**, not theoretical guesses. Each suggestion should be backed by actual test results showing improvement.

#### 11.8.1 Iterative Workflow Overview

The key principle is **iterative refinement**: write one fix, test it, analyze failures, improve the fix based on what you learned, and repeat until the pass rate is acceptable.

```
┌─────────────────────────────────────────────────────────────────┐
│                        ITERATION 1                               │
├─────────────────────────────────────────────────────────────────┤
│  1. IDENTIFY ISSUE                                               │
│     ├── Find failing samples with same issue type                │
│     ├── Read original module prompt                              │
│     └── Analyze why the rule is unclear to the model             │
│                                                                  │
│  2. WRITE FIX V1                                                 │
│     ├── Modify ONLY the specific rule causing the issue          │
│     ├── DO NOT add output examples (no sample KWs, ASINs)        │
│     └── Rewrite rule for clarity                                 │
│                                                                  │
│  3. RUN EXPERIMENT                                               │
│     ├── Run modified prompt on failing samples (10-20)           │
│     └── Record results                                           │
│                                                                  │
│  4. ANALYZE RESULTS                                              │
│     ├── Result: 3/7 passed (43%)                                 │
│     ├── Analyze WHY 4 samples still failed                       │
│     └── Finding: "Model returns null when taxonomy is missing"   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                        ITERATION 2                               │
├─────────────────────────────────────────────────────────────────┤
│  1. LEARN FROM V1 FAILURES                                       │
│     └── "V1 failed when taxonomy was missing"                    │
│                                                                  │
│  2. WRITE FIX V2 (cumulative)                                    │
│     ├── KEEP what worked in V1                                   │
│     └── ADD fix for the new failure pattern                      │
│                                                                  │
│  3. RUN EXPERIMENT (same samples)                                │
│     └── Result: 5/7 passed (71%)                                 │
│                                                                  │
│  4. ANALYZE REMAINING FAILURES                                   │
│     └── Finding: "Model adds adjectives from Use Case input"     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                        ITERATION 3                               │
├─────────────────────────────────────────────────────────────────┤
│  1. LEARN FROM V1 + V2                                           │
│     └── "Need to handle both null input AND adjective removal"   │
│                                                                  │
│  2. WRITE FIX V3 (cumulative)                                    │
│     ├── KEEP V1 + V2 improvements                                │
│     └── ADD adjective removal rule                               │
│                                                                  │
│  3. RUN EXPERIMENT                                               │
│     └── Result: 6/7 passed (86%) ✓                               │
│                                                                  │
│  4. DECISION: Pass rate acceptable → STOP                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                     ADD TO DASHBOARD                             │
├─────────────────────────────────────────────────────────────────┤
│  • Use V3 as the final validated fix                             │
│  • Document all iterations and learnings                         │
│  • Show before/after metrics                                     │
│  • Include exact prompt modification                             │
└─────────────────────────────────────────────────────────────────┘
```

#### 11.8.2 Key Principles

| Principle | Description |
|-----------|-------------|
| **Iterative refinement** | Write one fix → test → analyze failures → improve → repeat |
| **Cumulative fixes** | V2 includes V1 improvements + new fix; V3 includes V1+V2 + new fix |
| **Learn from failures** | Each iteration analyzes WHY samples still fail and addresses that |
| **Test on failing samples** | Use 10-20 samples that exhibited the specific issue |
| **Modify rules only** | Clarify/rewrite instructions; do not add output examples |
| **Stop when acceptable** | Continue until pass rate is acceptable OR no more improvement possible |
| **Document everything** | Record each iteration's results for future reference |

**Important Notes:**
- Each iteration **learns from previous failures** - analyze why samples still fail
- Fixes are **cumulative** - V2 includes V1 improvements + new fix
- Continue until pass rate is **acceptable** or no more improvement is possible
- If iteration shows **no improvement**, try a different approach rather than the same direction

#### 11.8.3 Example: M10 Null Output Issue (Iterative)

**Issue Identified:**
- 7 out of 10 M10 samples returned `null` instead of a use phrase
- Root cause: Prompt doesn't tell model what to do when validation is unclear

**ITERATION 1:**

*Write Fix V1:*
```
Add to prompt:
"If the primary use phrase cannot be validated, return a simplified
version by removing adjectives. Never return null."
```

*Run Experiment:*
```bash
python run_prompt_experiment.py --module m10 --iteration 1
```

*Results:*
```
V1: 5/7 passed (71%)
Failed samples: B0BZYCJK89 (Water Bottle), B000H3I2JG (Eyeliner)
```

*Analyze Failures:*
```
- B0BZYCJK89: Output "portable drink storage" - contains adjective "portable"
- B000H3I2JG: Output "eye definition" - too vague, not actionable
→ Learning: V1 doesn't handle adjective removal strictly enough
```

**ITERATION 2:**

*Write Fix V2 (cumulative - keep V1 + add new fix):*
```
Add to prompt (V1 + new):
"If the primary use phrase cannot be validated, return a simplified
version by removing adjectives. Never return null.

STRICT ADJECTIVE REMOVAL:
Words that MUST be removed: portable, wireless, premium, advanced.
After removing, add context from Use Case to maintain 3-6 words."
```

*Run Experiment:*
```bash
python run_prompt_experiment.py --module m10 --iteration 2
```

*Results:*
```
V2: 6/7 passed (86%) ✓
Only 1 failure remaining: B000H3I2JG (edge case - cosmetics category)
```

*Decision:* 86% pass rate is acceptable. Use V2 as final fix.

**Add to Dashboard:**
```javascript
{
    module: "M10",
    issue: "null output + format issue",
    iterations: 2,
    finalPassRate: "6/7 (86%)",
    iterationHistory: [
        { version: "V1", result: "5/7 (71%)", learning: "Adjective removal too weak" },
        { version: "V2", result: "6/7 (86%)", learning: "Final - acceptable" }
    ],
    promptChange: "Added null-handling + strict adjective removal rules",
    validated: true
}
```

#### 11.8.4 What NOT to Do

| Wrong Approach | Why It's Wrong |
|----------------|----------------|
| Add output examples to prompt | Examples may cause overfitting; rules should be generalizable |
| Test on random samples | Doesn't prove the fix solves the specific issue |
| Add suggestions without testing | Theoretical fixes may not work in practice |
| Test multiple variations in parallel | Can't learn from failures; use iterative approach instead |
| Skip analyzing why samples failed | Misses opportunity to improve in next iteration |
| Discard previous fix when it partially worked | Fixes are cumulative; keep what worked, add more |
| Stop after first iteration | Continue iterating until acceptable pass rate |

#### 11.8.5 Improvement Suggestion Data Structure

Each validated suggestion in the dashboard should include:

```javascript
{
    module: "M10",
    criticality: "Critical",
    issueType: "Prompt Issue",
    issueSummary: "Model returns null for 70% of samples",

    // Experiment details
    experimentModel: "gpt-4o-mini",
    failingSamplesCount: 7,
    samplesTestedIds: ["B0CJ4WZXQF", "B0D6YNWLTS", ...],

    // Iteration history (key for iterative approach)
    iterations: 2,
    iterationHistory: [
        {
            version: "V1",
            fix: "Added null-handling fallback",
            result: "5/7 (71%)",
            failedSamples: ["B0BZYCJK89", "B000H3I2JG"],
            learning: "Adjective removal not strict enough"
        },
        {
            version: "V2",
            fix: "V1 + strict adjective removal",
            result: "6/7 (86%)",
            failedSamples: ["B000H3I2JG"],
            learning: "Acceptable - edge case remaining"
        }
    ],

    // Final results
    beforePassRate: "70%",
    afterPassRate: "86%",
    improvement: "+16%",

    // The validated fix (final cumulative version)
    action: "ADD NEW SECTION",  // or "MODIFY EXISTING"
    location: "Before '## Output Format' section",
    fileName: "m10_validate_primary_intended_use_v1.1.md",
    promptChange: "## MANDATORY: Handle Null Input\n...[full text]...",

    validated: true,
    experimentDate: "2026-01-15"
}
```

#### 11.8.6 When to Stop Iterating

| Condition | Action |
|-----------|--------|
| Pass rate ≥ 80% | Stop - acceptable result |
| Pass rate improved but < 80% | Continue iterating |
| Pass rate didn't improve after 2 iterations | Try different approach |
| Remaining failures are edge cases | Stop - document edge cases |
| No pattern in remaining failures | Stop - may be model limitation |

---

## Next Steps

1. **Distribute Kappa dataset** to human annotators
2. **Calculate Cohen's Kappa** after annotation
3. **Fix critical module prompts** (M10, M08, M06)
4. **Add missing test data** (X, S, N categories)
5. **Re-run evaluation** after fixes
6. **Scale to more ASINs** for production
7. **Generate dashboards** for each new experiment version
