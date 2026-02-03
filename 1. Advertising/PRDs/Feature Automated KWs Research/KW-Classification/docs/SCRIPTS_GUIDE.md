# Scripts Guide

This guide documents the automation scripts for running LLM experiments and human annotation validation.

---

## Script Finder (Start Here)

- Primary workflow: `scripts/orchestrator.py`, `scripts/experiment_registry.py`, `scripts/sync_braintrust.py`
- Full catalog + checklist: `docs/SCRIPTS_INDEX.md`
- Batch runs: `scripts/batch/` (golden + synthetic)
- Analysis: `scripts/analysis/`
- Uploads & Braintrust: `scripts/upload/`, `scripts/braintrust_*.py`, `scripts/mapping_loader.py`
- Optimization: `scripts/dspy_optimize/`
- Quick search: `rg --files scripts` or `rg -n "keyword" scripts docs`

---

## Directory Structure

```
project/
├── scripts/
│   ├── config.py                    # Module configurations
│   ├── orchestrator.py              # Run LLM experiments
│   ├── experiment_registry.py       # Track experiment metadata
│   ├── sync_braintrust.py           # Upload to Braintrust
│   ├── braintrust_sync.py            # Match local runs to Braintrust
│   ├── braintrust_upload.py          # Upload helpers
│   ├── braintrust_download.py        # Download helpers
│   ├── generate_annotation_csv.py   # Create annotation tasks
│   ├── calculate_agreement.py       # Compute Cohen's Kappa
│   └── merge_annotations.py         # Merge & create gold datasets
│   ├── batch/                        # OpenAI Batch API scripts
│   ├── analysis/                     # Error analysis & reporting
│   ├── upload/                       # Braintrust uploads
│   ├── processing/                   # Data validation tools
│   ├── testing/                      # Local evaluation scripts
│   ├── dspy_optimize/                # Prompt optimization workflows
│   ├── data_import/                  # Dataset import tools
│   └── experiments_converters/       # Results conversion helpers
│
├── experiment_results/              # LLM experiment outputs
│   ├── M01_ExtractOwnBrandEntities/
│   ├── M02_ClassifyOwnBrandKeywords/
│   ├── ...
│   └── .registry.json               # Experiment tracking
│
├── annotation_tasks/                # CSV files for human annotators
│   └── M12_annotation_20260116.csv
│
└── validated_data/                  # Merged annotations & gold datasets
    ├── M12_validated_20260116.csv
    └── M12_gold_20260116.jsonl
```

---

## Batch Processing Scripts (Golden + Synthetic)

**Golden datasets (default):**

```bash
# Generate batch files (all modules)
python scripts/batch/generate_batch_requests.py

# Or specific modules
python scripts/batch/generate_batch_requests.py m02 m04 m05

# Upload / monitor / download
python scripts/batch/upload_batch.py batch_requests/20260127_1200
python scripts/batch/check_batch_status.py batch_requests/20260127_1200
python scripts/batch/download_results.py batch_requests/20260127_1200
python scripts/batch/evaluate_results.py batch_requests/20260127_1200
```

**Synthetic datasets (optimized prompts):**

```bash
python scripts/batch/generate_synthetic_batch.py --all
python scripts/batch/upload_synthetic_batch.py batch_requests/synthetic/20260127_1200
python scripts/batch/check_synthetic_status.py batch_requests/synthetic/20260127_1200
python scripts/batch/download_synthetic_results.py batch_requests/synthetic/20260127_1200
```

See `docs/BASELINE_TESTING_GUIDE.md` for analysis workflows after download.

---

## Part 1: LLM Experiment Workflow

### Overview

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Datasets   │ --> │ Orchestrator │ --> │ experiment_     │
│  (JSONL)    │     │              │     │ results/*.csv   │
└─────────────┘     └──────────────┘     └─────────────────┘
                           │                      │
                           v                      v
                    ┌──────────────┐     ┌─────────────────┐
                    │  Registry    │     │ sync_braintrust │
                    │  .json       │     │ --> Braintrust  │
                    └──────────────┘     └─────────────────┘
```

### 1.1 orchestrator.py

Run LLM experiments against datasets for any of the 22 modules.

**Basic Usage:**

```bash
# Run single module
python scripts/orchestrator.py run m12

# Run with custom sample size
python scripts/orchestrator.py run m12 --samples 100

# Run all enabled modules
python scripts/orchestrator.py run --all

# List available modules
python scripts/orchestrator.py list

# Dry run (show what would be executed)
python scripts/orchestrator.py run m12 --dry-run
```

**Options:**

| Flag | Description |
|------|-------------|
| `--samples N` | Number of samples to process (default: all) |
| `--all` | Run all enabled modules |
| `--upload` | Upload results to Braintrust after run |
| `--dry-run` | Show plan without executing |
| `--model MODEL` | Override default model |

**Output:**

- CSV file: `experiment_results/{MODULE_NAME}/{MODULE}_v1_{timestamp}.csv`
- Registry entry: `.registry.json` updated with experiment metadata

### 1.2 experiment_registry.py

Tracks all experiments with local IDs and Braintrust mappings.

**Commands:**

```bash
# List all experiments
python scripts/experiment_registry.py list

# Filter by module
python scripts/experiment_registry.py list --module m12

# Show pending uploads
python scripts/experiment_registry.py pending

# Show statistics
python scripts/experiment_registry.py stats

# Show single experiment details
python scripts/experiment_registry.py show exp_20260116_123456_m12

# Clean up entries for deleted files
python scripts/experiment_registry.py cleanup
```

**Registry Format (.registry.json):**

```json
{
  "experiments": {
    "exp_20260116_123456_m12": {
      "local_id": "exp_20260116_123456_m12",
      "module_id": "m12",
      "csv_path": "/path/to/results.csv",
      "created_at": "2026-01-16T12:34:56",
      "status": "local_only",
      "accuracy": 0.85,
      "samples": 100,
      "braintrust_id": null,
      "braintrust_url": null
    }
  }
}
```

### 1.3 sync_braintrust.py

Upload local experiments to Braintrust for tracking and comparison.

**Commands:**

```bash
# Sync all pending experiments
python scripts/sync_braintrust.py sync

# Sync specific module only
python scripts/sync_braintrust.py sync --module m12

# Sync with limit
python scripts/sync_braintrust.py sync --limit 5

# Upload single experiment
python scripts/sync_braintrust.py upload exp_20260116_123456_m12

# Check sync status
python scripts/sync_braintrust.py status
```

**Braintrust Naming Convention:**

```
root_{module_id}_{module_name}_{timestamp}
Example: root_m12_HardConstraintViolationCheck_20260116_123456
```

---

## Part 2: Human Annotation Workflow

### Overview

```
┌─────────────────┐     ┌───────────────┐     ┌─────────────────┐
│ experiment_     │ --> │ generate_     │ --> │ annotation_     │
│ results/*.csv   │     │ annotation    │     │ tasks/*.csv     │
└─────────────────┘     └───────────────┘     └─────────────────┘
                                                      │
                              ┌────────────────────────┘
                              v
                    ┌───────────────────┐
                    │ Annotator A & B   │
                    │ fill in columns   │
                    └───────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         v                    v                    v
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ calculate_      │  │ merge_          │  │ validated_      │
│ agreement.py    │  │ annotations.py  │  │ data/*.jsonl    │
│ (Cohen's Kappa) │  │ (resolve)       │  │ (gold dataset)  │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### 2.1 generate_annotation_csv.py

Creates CSV files formatted for human annotators.

**Commands:**

```bash
# List modules with available experiment results
python scripts/generate_annotation_csv.py list

# Generate annotation CSV for single module
python scripts/generate_annotation_csv.py generate m12

# Generate with sampling
python scripts/generate_annotation_csv.py generate m12 --sample 100

# Generate with fixed seed (reproducible)
python scripts/generate_annotation_csv.py generate m12 --sample 100 --seed 42

# Generate without shuffling
python scripts/generate_annotation_csv.py generate m12 --no-shuffle

# Generate from specific source file
python scripts/generate_annotation_csv.py generate m12 --source /path/to/file.csv

# Batch generate for all modules
python scripts/generate_annotation_csv.py batch --all --sample 50
```

**Output Format:**

Each module has specific columns. Example for M12:

| Column | Description |
|--------|-------------|
| row_id | Unique row identifier |
| asin | Product ASIN |
| keyword | Search keyword |
| brand_name | Brand name |
| hard_constraints | Product constraints |
| llm_violates | LLM's violation decision |
| llm_confidence | LLM confidence score |
| llm_reasoning | LLM reasoning text |
| annotator_a_violates | **Annotator A fills this** |
| annotator_a_reasoning | **Annotator A fills this** |
| annotator_b_violates | **Annotator B fills this** |
| annotator_b_reasoning | **Annotator B fills this** |
| agreement | Auto-calculated after merge |
| notes | Resolution notes |

### 2.2 calculate_agreement.py

Computes inter-annotator agreement using Cohen's Kappa.

**Commands:**

```bash
# List annotation files
python scripts/calculate_agreement.py list

# Analyze single file
python scripts/calculate_agreement.py analyze M12_annotation.csv

# Analyze with confusion matrix
python scripts/calculate_agreement.py analyze M12_annotation.csv --verbose

# Output as JSON
python scripts/calculate_agreement.py analyze M12_annotation.csv --json

# Batch analyze all files
python scripts/calculate_agreement.py batch
```

**Output Example:**

```
============================================================
INTER-ANNOTATOR AGREEMENT REPORT
============================================================

File: M12_annotation_20260116.csv
Module: M12
Total rows: 100
Annotated rows: 95

----------------------------------------
AGREEMENT METRICS
----------------------------------------

Cohen's Kappa: 0.8234
Interpretation: Almost Perfect

Observed Agreement: 91.58%
Expected Agreement: 51.23%

Agreements: 87
Disagreements: 8

Labels found: N, R, S
```

**Kappa Interpretation:**

| Kappa | Interpretation |
|-------|----------------|
| < 0.00 | Poor (worse than chance) |
| 0.00 - 0.20 | Slight |
| 0.21 - 0.40 | Fair |
| 0.41 - 0.60 | Moderate |
| 0.61 - 0.80 | Substantial |
| 0.81 - 1.00 | Almost Perfect |

### 2.3 merge_annotations.py

Merges annotator responses and creates validated datasets.

**Commands:**

```bash
# List available files
python scripts/merge_annotations.py list

# Merge with majority voting (LLM as tiebreaker)
python scripts/merge_annotations.py merge M12_annotation.csv

# Merge with conservative strategy (mark disagreements)
python scripts/merge_annotations.py merge M12_annotation.csv --strategy conservative

# Export only disagreements for review
python scripts/merge_annotations.py merge M12_annotation.csv --disagreements-only

# Create gold standard dataset (JSONL)
python scripts/merge_annotations.py gold M12_validated.csv

# Create gold standard dataset (CSV)
python scripts/merge_annotations.py gold M12_validated.csv --format csv
```

**Resolution Strategies:**

| Strategy | Description |
|----------|-------------|
| `majority` | If A≠B, use LLM as tiebreaker. Default. |
| `conservative` | Mark all disagreements as NEEDS_REVIEW |
| `annotator_a` | Always prefer Annotator A |
| `annotator_b` | Always prefer Annotator B |

**Output Columns Added:**

| Column | Description |
|--------|-------------|
| final_label | Resolved label |
| resolution | How it was resolved (agreement, majority_a_llm, etc.) |
| annotator_agreement | 1 if agreed, 0 if disagreed |

---

## Part 3: Complete Workflow Example

### Step 1: Run LLM Experiment

```bash
# Run M12 module on full dataset
python scripts/orchestrator.py run m12

# Output: experiment_results/M12_HardConstraintViolationCheck/M12_*.csv
```

### Step 2: Generate Annotation Task

```bash
# Create annotation CSV with 100 sampled records
python scripts/generate_annotation_csv.py generate m12 --sample 100 --seed 42

# Output: annotation_tasks/M12_annotation_20260116_123456.csv
```

### Step 3: Human Annotation

1. Share `M12_annotation_*.csv` with Annotator A and B
2. Each annotator fills their columns independently
3. Collect completed file

### Step 4: Calculate Agreement

```bash
# Check inter-annotator reliability
python scripts/calculate_agreement.py analyze annotation_tasks/M12_annotation_*.csv -v

# Target: Kappa > 0.60 (Substantial agreement)
```

### Step 5: Resolve & Merge

```bash
# If Kappa is acceptable, merge annotations
python scripts/merge_annotations.py merge annotation_tasks/M12_annotation_*.csv

# Output: validated_data/M12_validated_*.csv
```

### Step 6: Create Gold Dataset

```bash
# Generate gold standard for training/evaluation
python scripts/merge_annotations.py gold validated_data/M12_validated_*.csv

# Output: validated_data/M12_gold_*.jsonl
```

### Step 7: Upload to Braintrust (Optional)

```bash
# Sync experiment to Braintrust
python scripts/sync_braintrust.py sync --module m12
```

---

## Configuration

### scripts/config.py

Module definitions are in `config.py`. Each module has:

```python
"m12": {
    "name": "CheckHardConstraint",
    "slug": "check-hard-constraint",
    "type": "classifier",
    "dataset": "datasets/single/m12_v1_check_hard_constraint.jsonl",
    "prompt": "prompts/modules/single/m12_v1_check_hard_constraint.md",
    "enabled": True,  # Set False to exclude from --all runs
}
```

### Environment Variables

```bash
# Required for Braintrust upload
export BRAINTRUST_API_KEY="your-api-key"

# Optional: Override default model
export DEFAULT_MODEL="gpt-4o-mini"
```

---

## Supported Modules (22 Total)

| ID | Name | Type |
|----|------|------|
| m01 | ExtractOwnBrandEntities | extraction |
| m01a | ExtractOwnBrandVariations | extraction |
| m01b | ExtractBrandRelatedTerms | extraction |
| m02 | ClassifyOwnBrandKeywords | classification |
| m02b | ClassifyOwnBrandKeywords_PathB | classification |
| m03 | GenerateCompetitorEntities | extraction (disabled) |
| m04 | ClassifyCompetitorBrandKeywords | classification |
| m04b | ClassifyCompetitorBrandKeywords_PathB | classification |
| m05 | ClassifyNonBrandedKeywords | classification |
| m05b | ClassifyNonBrandedKeywords_PathB | classification |
| m06 | GenerateProductTypeTaxonomy | extraction |
| m07 | ExtractProductAttributes | extraction |
| m08 | AssignAttributeRanks | ranking |
| m09 | IdentifyPrimaryIntendedUse | extraction |
| m10 | ValidatePrimaryIntendedUse | validation |
| m11 | IdentifyHardConstraints | extraction |
| m12 | HardConstraintViolationCheck | classification |
| m12b | CombinedClassification | classification |
| m13 | ProductTypeCheck | classification |
| m14 | PrimaryUseCheckSameType | classification |
| m15 | SubstituteCheck | classification |
| m16 | ComplementaryCheck | classification |

---

## Troubleshooting

### No experiment results found

```bash
# Check if experiments exist
ls experiment_results/

# Run the module first
python scripts/orchestrator.py run m12
```

### Low Kappa score

- Review disagreements: `merge_annotations.py merge file.csv --disagreements-only`
- Check annotation guidelines are clear
- Consider additional annotator training

### Braintrust upload fails

```bash
# Check API key is set
echo $BRAINTRUST_API_KEY

# Check status
python scripts/sync_braintrust.py status
```

### Registry out of sync

```bash
# Clean up missing files
python scripts/experiment_registry.py cleanup
```
