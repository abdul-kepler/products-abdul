# Cohen's Kappa Human Evaluation Guide

## Purpose

This guide explains how to conduct human evaluation for calculating Cohen's Kappa inter-rater reliability between multiple judges.

---

## CSV Files for Human Judges

### 1. `cohen_kappa_experiment_dataset.csv` (72 samples) - USE THIS FOR KAPPA

**Purpose:** Curated dataset for Cohen's Kappa inter-rater reliability experiment.

**Selection Criteria Applied:**
- **No Train Data:** Only Dev (39) and Test (33) samples - prevents artificial inflation
- **Tricky/Edge Cases:** 36 samples where LLM Judge marked FAIL (ambiguous, difficult)
- **Representative PASS Cases:** 36 samples to verify judge correctness
- **Perfectly Balanced:** Exactly 50/50 PASS/FAIL to surface disagreements
- **Full Scenario Coverage:** 18 scenarios represented (4 samples each)

**Critical Rules:**
1. All annotators MUST evaluate this IDENTICAL dataset independently
2. NEVER use Train examples (few-shots) for Kappa - leads to artificially high agreement
3. Do not discuss answers until all annotations are complete

### 2. `human_judge_evaluation_sheet.csv` (Full - 990 samples)

Complete evaluation sheet. Use for comprehensive analysis after Kappa experiment.

### 3. `human_judge_evaluation_SAMPLED.csv` (57 samples)

Quick reference sample. Not for Kappa calculation.

---

## CSV Column Structure

### Pre-filled Columns (Context)

| Column | Description |
|--------|-------------|
| Sample_ID | Unique identifier |
| **Dataset_Split** | Train/Dev/Test - prevents data leakage when using examples in prompts |
| **Scenario** | Evaluation scenario (e.g., "Brand Extraction", "Competitor Classification") |
| **Constraint_Type** | "Hard Constraint" for M11/M12, empty otherwise |
| Module | Module ID (M01-M16) |
| Module_Description | What the module does |
| ASIN | Amazon product ID |
| Product_Name | Product name |
| Input_Data | Full input context for the model |
| Model_Output | What the model produced |
| Rubric_ID | Evaluation criterion ID |
| Rubric_Criterion | What is being evaluated |
| **Check** | What specifically to verify (e.g., "Brand extracted from title or listing_brand field") |
| Pass_Conditions | What constitutes PASS |
| Fail_Conditions | What constitutes FAIL |

### Dataset Split Guidelines (Best Practice Ratios)

| Split | % | Samples | Purpose |
|-------|---|---------|---------|
| **Train** | ~15% | 117 | Select 5-10 high-quality few-shot examples for judge prompt |
| **Dev** | ~45% | 451 | Iteratively test and refine judge prompt against human labels |
| **Test** | ~43% | 422 | Hold-out set - use ONLY ONCE at the end for final reliability |

**Critical Rules:**
- **Train**: Only source for few-shot examples in prompts
- **Dev**: Use for all prompt development and tuning iterations
- **Test**: NEVER look at during development; single final evaluation only

### Constraint Type Column

| Value | Description |
|-------|-------------|
| `Hard Constraint` | M11/M12 samples - constraint identification/violation |
| *(empty)* | Non-constraint related samples |

### Annotator Columns (To Be Filled by Humans)

| Column | Who Fills | Description |
|--------|-----------|-------------|
| **Annotator_1_Label** | Annotator 1 | PASS or FAIL |
| **Annotator_1_Reasoning** | Annotator 1 | Why this label was chosen |
| **Annotator_2_Label** | Annotator 2 | PASS or FAIL |
| **Annotator_2_Reasoning** | Annotator 2 | Why this label was chosen |
| **Final_Consensus_Label** | Both | Agreed label after discussion |

### LLM Judge Results (Pre-filled for Reference)

| Column | Description |
|--------|-------------|
| LLM_Judge_Verdict | PASS or FAIL from automated LLM judge |
| LLM_Judge_Reasoning | LLM's explanation for its verdict |

---

## Instructions for Human Judges

### Step 1: Open the CSV File
- Open `human_judge_evaluation_SAMPLED.csv` in Excel/Google Sheets
- Each row is ONE evaluation task

### Step 2: For Each Row, Evaluate
1. **Read Input_Data** - Understand what the model was given
2. **Read Model_Output** - See what the model produced
3. **Read Rubric_Criterion** - Understand what you're evaluating
4. **Read Pass_Conditions** - Know what PASS means
5. **Read Fail_Conditions** - Know what FAIL means
6. **Enter Your Assessment:**
   - `Annotator_1_Label` (or Annotator_2): Enter **PASS** or **FAIL**
   - `Annotator_1_Reasoning`: Explain WHY you chose this label

### Step 3: Important Rules
- Evaluate INDEPENDENTLY first - don't discuss with other annotators
- Use ONLY the Pass/Fail conditions provided
- ALWAYS provide reasoning - this is required, not optional
- Be consistent across similar cases

### Step 4: Consensus Round (After Independent Evaluation)
1. Compare Annotator_1_Label vs Annotator_2_Label
2. For disagreements, discuss and agree on final label
3. Fill in `Final_Consensus_Label` with agreed decision
4. Fill in `Judge_Reasoning` explaining the consensus rationale

---

## Rating Guidelines

### PASS Criteria
- Model output meets ALL pass conditions
- No fail conditions are triggered
- Output is useful and correct

### FAIL Criteria
- ANY fail condition is triggered
- Model output misses key requirements
- Output contains errors or hallucinations

### Confidence Levels
- **High**: Very clear case, no doubt
- **Medium**: Mostly clear, minor uncertainty
- **Low**: Difficult case, could go either way

---

## After Judging: Calculate Cohen's Kappa

### Step 1: Collect Completed Sheets
Get the CSV files back from both judges.

### Step 2: Run Calculation Script

```python
import pandas as pd
import numpy as np

def calculate_cohens_kappa(rater1, rater2):
    """Calculate Cohen's Kappa manually."""
    rater1 = [str(x).upper() for x in rater1]
    rater2 = [str(x).upper() for x in rater2]

    categories = sorted(list(set(rater1) | set(rater2)))
    n = len(rater1)

    matrix = np.zeros((len(categories), len(categories)))
    cat_to_idx = {cat: i for i, cat in enumerate(categories)}

    for r1, r2 in zip(rater1, rater2):
        matrix[cat_to_idx[r1], cat_to_idx[r2]] += 1

    Po = np.trace(matrix) / n
    row_marginals = matrix.sum(axis=1) / n
    col_marginals = matrix.sum(axis=0) / n
    Pe = np.sum(row_marginals * col_marginals)

    if Pe == 1:
        return 1.0 if Po == 1 else 0.0

    return (Po - Pe) / (1 - Pe)

# Load completed evaluation
df = pd.read_csv('human_judge_evaluation_SAMPLED.csv')

# Calculate Kappa between annotators
kappa = calculate_cohens_kappa(
    df['Annotator_1_Label'].tolist(),
    df['Annotator_2_Label'].tolist()
)

# Simple agreement
agree = sum(1 for a1, a2 in zip(df['Annotator_1_Label'], df['Annotator_2_Label'])
            if str(a1).upper() == str(a2).upper())
agreement_pct = agree / len(df) * 100

print(f"Simple Agreement: {agreement_pct:.1f}%")
print(f"Cohen's Kappa: {kappa:.4f}")
```

---

## Interpretation Scale (Landis & Koch, 1977)

| Kappa Value | Interpretation |
|-------------|----------------|
| < 0.00 | Poor (worse than chance) |
| 0.00 - 0.20 | Slight |
| 0.21 - 0.40 | Fair |
| 0.41 - 0.60 | Moderate |
| 0.61 - 0.80 | Substantial |
| 0.81 - 1.00 | Almost Perfect |

**Target:** κ ≥ 0.60 (Substantial agreement)

---

## Best Practices

### 1. Judge Selection
- Select judges with domain knowledge
- Minimum 2 judges required
- 3+ judges recommended for reliability

### 2. Training
- Review rubrics together before starting
- Do 5-10 practice evaluations
- Discuss edge cases

### 3. Sample Size
- Minimum: 30 samples per module
- Recommended: 50+ for reliable estimates
- Use stratified sampling across modules

### 4. Blind Evaluation
- Judges should NOT see each other's ratings
- Judges should NOT see LLM judge results
- Each judge works independently

### 5. Resolving Disagreements
- After Kappa calculation, review disagreements
- Discuss with judges to understand reasoning
- Use for rubric refinement (not score changes)

---

## Workflow Summary

```
1. Distribute CSV files to judges (independently)
        ↓
2. Judges evaluate all samples (PASS/FAIL + Confidence)
        ↓
3. Collect completed CSV files
        ↓
4. Calculate Cohen's Kappa
        ↓
5. Review disagreements for insights
        ↓
6. Report: Agreement %, Kappa, Interpretation
```

---

## Files Location

```
evaluation/evaluation_reports/
├── human_judge_evaluation_sheet.csv      # Full (990 samples)
├── human_judge_evaluation_SAMPLED.csv    # Sampled (86 samples)
├── rubrics_reference.csv                 # Rubric definitions
└── COHEN_KAPPA_INSTRUCTIONS.md           # This guide
```
