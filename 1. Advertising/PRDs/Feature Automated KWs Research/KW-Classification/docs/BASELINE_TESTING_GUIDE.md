# Baseline Testing Guide for Prompt Pipeline V1.1

**Created:** 2026-01-09
**Status:** Active
**Purpose:** Document the baseline testing process for evaluating and improving prompts

---

## Pipeline Architecture

### CRITICAL: Two Pipeline Variants

The system has **two different pipeline architectures** that agents often confuse:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PIPELINE 1: ORIGINAL (V1.1)                      │
│                    Uses: M01 → M02, M03, M04, M05                   │
└─────────────────────────────────────────────────────────────────────┘

   M01 (Extract Own Brand Entities)
          │
          ▼
   ┌──────┴──────┬───────────────┐
   │             │               │
   M02           M04            M05
   (Own Brand)  (Competitor   (Non-Branded)
                 Keywords)               
                

┌─────────────────────────────────────────────────────────────────────┐
│                    PIPELINE 2: V3 (SIMPLIFIED)                      │
│                    Uses: M01a + M01b → M02b, M04b, M05b             │
└─────────────────────────────────────────────────────────────────────┘

   M01a (Extract Own Brand Variations)
          │
          ├───────────────────────────────┐
          │                               │
   M01b (Extract Brand Related Terms)     │
          │                               │
          ▼                               ▼
   ┌──────┴──────┬───────────────┐
   │             │               │
   M02b         M04b            M05b
   (Own Brand)   (Competitor)    (Non-Branded)
```

### Key Differences

| Aspect | Pipeline V1.1 (Original) | Pipeline V3                                           |
|--------|--------------------------|-------------------------------------------------------|
| Brand Extraction | M01 single module | M01a + M01b combined                                  |
| Input to M02 | `brand_entities` from M01 | `variations_own` + `related_terms_own` from M01a+M01b |
| Competitor Generation | M03 generates competitors | Competitors provided externally                       |
| Modules | M01 → M02, M03 → M04, M05 | M01a+M01b → M02b, M04b, M05b                          |

### Dataset Metadata

V3 datasets include source indicator:
```json
{
  "metadata": {
    "v3_source": "M01a+M01b"
  }
}
```

---

## Existing Datasets

All datasets are located in:
```
/braintrust_integration/v1.1/datasets/
```

### Dataset Inventory

| Module | File | Test Cases | Status |
|--------|------|------------|--------|
| M01 | m01_extract_own_brand_entities.jsonl | 99 | Ready |
| M01a | m01a_extract_own_brand_variations.jsonl | 99 | Ready |
| M01b | m01b_extract_brand_related_terms.jsonl | 99 | Ready |
| M02 | m02_classify_own_brand_keywords.jsonl | 916 | Ready |
| M03 | m03_generate_competitor_entities.jsonl | 19 | Ready |
| M04 | m04_classify_competitor_brand_keywords.jsonl | 1759 | Ready |
| M05 | m05_classify_nonbranded_keywords.jsonl | 1759 | Ready |
| M06 | m06_generate_product_type_taxonomy.jsonl | 12 | Ready |
| M07 | m07_extract_product_attributes.jsonl | 12 | Ready |
| M08 | m08_assign_attribute_ranks.jsonl | 12 | Ready |
| M09 | m09_identify_primary_intended_use_v1.1.jsonl | 10 | Ready |
| M10 | m10_validate_primary_intended_use_v1.1.jsonl | 10 | Ready |
| M11 | m11_identify_hard_constraints_v1.1.jsonl | 10 | Ready |
| M12 | m12_check_hard_constraint_v1.1.jsonl | 443 | Ready |
| M13 | m13_check_product_type_v1.1.jsonl | 439 | Ready |
| M14 | m14_check_primary_use_same_type_v1.1.jsonl | 229 | Ready |
| M15 | m15_check_substitute_v1.1.jsonl | 210 | Ready |
| M16 | m16_check_complementary_v1.1.jsonl | 179 | Ready |

**Total:** 10,760 test cases across all modules

---

## Baseline Testing Process

### Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    BASELINE TESTING PIPELINE                     │
└─────────────────────────────────────────────────────────────────┘

     ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
     │  1. Dataset  │─────▶│  2. LLM Run  │─────▶│  3. Human    │
     │   (EXISTS)   │      │ (Braintrust) │      │   Annotation │
     └──────────────┘      └──────────────┘      └──────────────┘
            │                     │                     │
            ▼                     ▼                     ▼
     ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
     │ ✅ 10,760    │      │ LLM outputs  │      │ Expert human │
     │ test cases   │      │ per module   │      │ decisions    │
     │ ready        │      │              │      │              │
     └──────────────┘      └──────────────┘      └──────────────┘
                                  │                     │
                                  └──────────┬──────────┘
                                             ▼
                               ┌──────────────────────┐
                               │  4. Cohen's Kappa    │
                               │     Calculation      │
                               └──────────────────────┘
                                             │
                                             ▼
                               ┌──────────────────────┐
                               │  5. Analysis &       │
                               │     Improvement      │
                               └──────────────────────┘
```

### Step 1: Dataset (COMPLETED)

Datasets already exist in `/braintrust_integration/v1.1/datasets/`

Dataset format (JSONL):
```json
{
  "id": "M2_B0BQPGJ9LQ__ipod headphones",
  "input": {
    "keyword": "ipod headphones",
    "variations_own": "JBL, J-B-L, JBL-, JBL., JBLl",
    "related_terms_own": "Vibe Beam"
  },
  "expected": {
    "branding_scope_1": null
  },
  "metadata": {
    "module_id": "Module_02",
    "asin": "B0BQPGJ9LQ",
    "keyword": "ipod headphones",
    "brand_name": "JBL",
    "product_type": "HEADPHONES",
    "v3_source": "M01a+M01b"
  }
}
```

### Step 2: LLM Run (Braintrust)

Run prompts through Braintrust:

```bash
# Activate environment
source .venv_braintrust/bin/activate

# Set API key
export BRAINTRUST_API_KEY=$(grep BRAINTRUST_API_KEY braintrust_integration/.env | cut -d= -f2)

# Run evaluation for a specific module
python braintrust_integration/run_module_experiment.py \
  --module M02 \
  --dataset datasets/single/m02_v1_classify_own_brand_keywords.jsonl \
  --experiment "M02_Baseline_v1"
```

### Step 3: Human Annotation

Use spreadsheet templates from `ANNOTATION_SPREADSHEET_TEMPLATES.md`

**Google Sheets structure:**

| test_id | keyword | variations_own | LLM_branding | LLM_matched | Human_branding | Human_matched | Agreement | Notes |
|---------|---------|----------------|--------------|-------------|----------------|---------------|-----------|-------|
| M02_001 | jbl headphones | JBL,J-B-L | OB | jbl | OB | jbl | ✓ | |
| M02_002 | jlab earbuds | JBL,J-B-L | OB | jlab | null | - | ✗ | False positive |

**Annotation rules:**
1. Annotator does NOT see LLM output on first pass
2. Makes independent decision
3. Then compares with LLM
4. Records disagreements

### Step 4: Cohen's Kappa Calculation

**Formula:**
```
κ = (Po - Pe) / (1 - Pe)

where:
Po = observed agreement (actual % matches)
Pe = expected agreement (expected % by chance)
```

**Python code:**
```python
from sklearn.metrics import cohen_kappa_score

def calculate_kappa(llm_decisions, human_decisions):
    """
    llm_decisions: list of LLM outputs (e.g., ["OB", None, "OB", None])
    human_decisions: list of human annotations (same format)
    """
    label_map = {"OB": 1, "CB": 2, "NB": 3, None: 0, "null": 0}

    llm_encoded = [label_map.get(d, 0) for d in llm_decisions]
    human_encoded = [label_map.get(d, 0) for d in human_decisions]

    kappa = cohen_kappa_score(llm_encoded, human_encoded)
    return kappa
```

**Kappa interpretation:**

| Kappa (κ) | Interpretation | Action |
|-----------|----------------|--------|
| < 0.20 | Poor | Prompt needs major rework |
| 0.20-0.40 | Fair | Significant improvements needed |
| 0.41-0.60 | Moderate | Targeted improvements needed |
| **0.61-0.80** | **Good** | **Target level** |
| 0.81-1.00 | Excellent | Prompt is in good shape |

### Step 5: Analysis & Improvement

**Confusion Matrix:**
```
                    Human Decision
                    OB    null
LLM Decision  OB    TP    FP
              null  FN    TN

Metrics:
- Precision = TP / (TP + FP)
- Recall = TP / (TP + FN)
- F1 = 2 * (P * R) / (P + R)
```

**Error Analysis Table:**

| Error Type | Example | Root Cause | Fix |
|------------|---------|------------|-----|
| False Positive | jlab→OB | Similar brands | Add to "NOT matches" examples |
| False Negative | owalaa→null | Typo not listed | Expand variations |
| Boundary Error | jblspeaker→OB | No space | Clarify word boundary rules |

---

## Current Status

### Completed

- [x] All 22 module prompts created (V1.1)
- [x] V3 variants for M02, M04, M05 created (Path B: M02b, M04b, M05b)
- [x] Datasets for all modules created (10,760 test cases)
- [x] Prompt improvements applied to M08, M09, M10, M12-M16
- [x] Annotation spreadsheet templates created
- [x] **Path B schema fix** - Fixed field name mismatch (`branding_scope` → `branding_scope_1/2/3`)
- [x] Batch processing scripts created (`scripts/batch/`)
- [x] Error analysis pipeline created (`scripts/analysis/`)
- [x] Cohen's Kappa calculator created
- [x] Braintrust uploader created
- [x] Path A vs Path B comparator created
- [x] Baseline report generator created

### In Progress

- [ ] Main batch running (22 modules, 11,193 records) - `batch_requests/20260112_2127/`
- [ ] Path B fixed batch running (3 modules, 4,434 records) - `batch_requests/20260112_2250_path_b_fixed/`

### Pending

- [ ] Download batch results when complete
- [ ] Run full error analysis pipeline
- [ ] Generate baseline report
- [ ] Human annotation pass for disagreements
- [ ] Kappa calculation (LLM vs Human)
- [ ] Prompt refinements based on results
- [ ] Upload final results to Braintrust

---

## Quick Reference Commands

```bash
# Activate Braintrust environment
source .venv_braintrust/bin/activate

# Set API key
export BRAINTRUST_API_KEY=$(grep BRAINTRUST_API_KEY braintrust_integration/.env | cut -d= -f2)

# Upload prompts to Braintrust
python braintrust_integration/upload_all_modules_v5.py

# Push scorers
cd braintrust_integration/scorers && braintrust push --if-exists replace braintrust_scorers.py

# Run experiment
python braintrust_integration/run_module_experiment.py --module <MODULE> --dataset <DATASET>

# Count test cases
wc -l braintrust_integration/v1.1/datasets/*.jsonl
```

---

## Batch Processing Scripts

Scripts for running OpenAI Batch API (50% discount, 24hr completion):

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/batch/generate_batch_requests.py` | Prepare batch JSONL files | `python scripts/batch/generate_batch_requests.py m02 m04 m05` |
| `scripts/batch/upload_batch.py` | Upload to OpenAI Batch API | `python scripts/batch/upload_batch.py --batch-dir batch_requests/xxx` |
| `scripts/batch/check_batch_status.py` | Check batch status | `python scripts/batch/check_batch_status.py --batch-dir batch_requests/xxx` |
| `scripts/batch/download_results.py` | Download completed results | `python scripts/batch/download_results.py --batch-dir batch_requests/xxx` |
| `scripts/batch/evaluate_results.py` | Evaluate against expected | `python scripts/batch/evaluate_results.py --batch-dir batch_requests/xxx` |

### Batch Processing Workflow

```bash
# 1. Prepare batch files
python scripts/batch/generate_batch_requests.py m02 m04 m05

# 2. Upload to OpenAI
python scripts/batch/upload_batch.py --batch-dir batch_requests/20260112

# 3. Check status (wait for completion)
python scripts/batch/check_batch_status.py --batch-dir batch_requests/20260112

# 4. Download results
python scripts/batch/download_results.py --batch-dir batch_requests/20260112

# 5. Evaluate
python scripts/batch/evaluate_results.py --batch-dir batch_requests/20260112
```

---

## Error Analysis Pipeline

After batch results are downloaded, use the analysis scripts in `scripts/analysis/`:

### Analysis Options

| Script | Purpose | Type |
|--------|---------|------|
| `error_analyzer.py` | Automated metrics (Precision, Recall, F1, Confusion Matrix) | Option A |
| `pattern_detector.py` | Pattern detection in errors (length, words, confidence) | Option B |
| `llm_judge_analyzer.py` | LLM-as-Judge evaluation (costs $) | Option C |
| `run_analysis.py` | Run all three analysis modes | Combined |

### Full Analysis Pipeline

```bash
# Run complete analysis pipeline
python scripts/analysis/run_analysis.py --batch-dir batch_requests/20260112

# Skip LLM Judge (faster, free)
python scripts/analysis/run_analysis.py --batch-dir batch_requests/20260112 --skip-judge

# Specific modules only
python scripts/analysis/run_analysis.py --batch-dir batch_requests/20260112 --modules m02 m04 m05
```

### Individual Analysis Tools

```bash
# Pattern detection only
python scripts/analysis/pattern_detector.py --errors-file experiment_results/m02_errors.json

# LLM Judge only
python scripts/analysis/llm_judge_analyzer.py --errors-file m02_errors.json --module m02 --max-errors 20
```

---

## Additional Analysis Tools

### Cohen's Kappa Calculator (`scripts/analysis/cohens_kappa.py`)

Calculate inter-rater reliability:

```bash
# Model vs Ground Truth
python scripts/analysis/cohens_kappa.py --mode model-vs-truth \
    --results1 batch_requests/xxx/m02_results.jsonl \
    --dataset datasets/single/m02_v1_classify_own_brand_keywords.jsonl

# Model A vs Model B
python scripts/analysis/cohens_kappa.py --mode model-vs-model \
    --results1 results_gpt4.jsonl \
    --results2 results_gpt4o.jsonl

# Custom labels
python scripts/analysis/cohens_kappa.py --mode labels \
    --labels1 human_labels.json \
    --labels2 llm_labels.json
```

**Kappa Interpretation:**

| Kappa (κ) | Interpretation | Action |
|-----------|----------------|--------|
| < 0.20 | Poor | Prompt needs major rework |
| 0.20-0.40 | Fair | Significant improvements needed |
| 0.41-0.60 | Moderate | Targeted improvements needed |
| **0.61-0.80** | **Good** | **Target level** |
| 0.81-1.00 | Excellent | Prompt is in good shape |

### Braintrust Uploader (`scripts/analysis/braintrust_uploader.py`)

Upload batch results to Braintrust for tracking:

```bash
# Upload all results from batch directory
python scripts/analysis/braintrust_uploader.py \
    --batch-dir batch_requests/20260112 \
    --project amazon-keyword-classification \
    --tags baseline gpt-4o-mini

# Upload specific modules
python scripts/analysis/braintrust_uploader.py \
    --batch-dir batch_requests/20260112 \
    --modules m02 m04 m05 \
    --tags path-a baseline
```

### Path A vs Path B Comparator (`scripts/analysis/path_comparator.py`)

Compare results between pipeline variants:

```bash
# Compare all path pairs (M02/M02b, M04/M04b, M05/M05b)
python scripts/analysis/path_comparator.py --batch-dir batch_requests/20260112

# Generates:
# - path_comparison/own_brand_comparison.md
# - path_comparison/competitor_brand_comparison.md
# - path_comparison/non_branded_comparison.md
```

**Path Pairs:**

| Task | Path A | Path B |
|------|--------|--------|
| Own Brand | M02 | M02b |
| Competitor Brand | M04 | M04b |
| Non-Branded | M05 | M05b |

### Baseline Report Generator (`scripts/analysis/baseline_report.py`)

Generate comprehensive baseline evaluation report:

```bash
# Generate full report
python scripts/analysis/baseline_report.py --batch-dir batch_requests/20260112

# Output both Markdown and JSON
python scripts/analysis/baseline_report.py --batch-dir batch_requests/20260112 --format both
```

**Report Contents:**
- Executive Summary (overall accuracy)
- Per-module metrics table
- Binary classifier details (Precision, Recall, F1)
- List extractor details (Avg Precision, Recall)
- Path A vs Path B comparison
- Error summary
- Recommendations

---

## Files Reference

| Type | Location |
|------|----------|
| **Prompts** | `prompts/modules/*.md` |
| **JSON Schemas** | `prompts/json_schemas/*.json` |
| **Datasets** | `datasets/*.jsonl` |
| **Batch Scripts** | `scripts/batch/` |
| **Analysis Scripts** | `scripts/analysis/` |
| **Scorers** | `scorers/` |
| **Templates** | `docs/ANNOTATION_SPREADSHEET_TEMPLATES.md` |
| **Module Reference** | `docs/MODULE_REFERENCE.md` |
| **This Guide** | `docs/BASELINE_TESTING_GUIDE.md` |

### Analysis Scripts Detail

| Script | Description |
|--------|-------------|
| `scripts/analysis/__init__.py` | Package exports |
| `scripts/analysis/error_analyzer.py` | Automated metrics & error extraction |
| `scripts/analysis/pattern_detector.py` | Error pattern detection |
| `scripts/analysis/llm_judge_analyzer.py` | LLM-as-Judge evaluation |
| `scripts/analysis/run_analysis.py` | Combined analysis runner |
| `scripts/analysis/cohens_kappa.py` | Cohen's Kappa calculator |
| `scripts/analysis/braintrust_uploader.py` | Braintrust experiment uploader |
| `scripts/analysis/path_comparator.py` | Path A vs Path B comparator |
| `scripts/analysis/baseline_report.py` | Baseline report generator |

---

*Last updated: January 12, 2026*
