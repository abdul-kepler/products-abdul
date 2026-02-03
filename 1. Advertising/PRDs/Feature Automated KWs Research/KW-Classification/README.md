# KW Classification v1.1

LLM-based keyword classification pipeline for e-commerce product relevance scoring.

## Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│  STAGE 1: Brand Entity Extraction (M01-M03)                                         │
│  ┌─────────────────────────┐     ┌────────────────────────────────────────────────┐ │
│  │ Path A: M01 = M03       │ OR  │ Path B: M01a + M01b                            │ │
│  │ (brand entities)        │     │ (brand variations (footprints) + related terms)│ │
│  └─────────────────────────┘     └────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌────────────────────────────────────────────────────────────────────────────────────┐
│  STAGE 2: Brand Scope Classification (M02/M04/M05)                                 │
│  ┌─────────────────────────┐     ┌─────────────────────────────────────┐           │
│  │ Path A: M02, M04, M05   │ OR  │ Path B: M02b, M04b, M05b            │           │
│  └─────────────────────────┘     └─────────────────────────────────────┘           │
│  Output: OB (Own Brand) / CB (Competitor Brand) / NB (Non-Branded)                 │
└────────────────────────────────────────────────────────────────────────────────────┘
                                   
                                   
                                   
┌────────────────────────────────────────────────────────────────────────────────────┐
│  STAGE 3: Product Definition & Taxonomy (M06-M11)                                  │
│  M06: Product type taxonomy                                                        │
│  M07: Product attributes extraction                                                │
│  M08: Attribute importance ranking                                                 │
│  M09: Primary intended use identification                                          │
│  M10: Intended use validation                                                      │
│  M11: Hard constraints identification                                              │
└────────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│  STAGE 4: Relevance Classification (M12-M16)                                      │
│     ┌─────────────────────────┐        ┌─────────────────────────────────────┐    │
│     │ Path A: M12 → M13-M16   │   OR   │ Path B: M12b only                   │    │
│     │ (step-by-step checks)   │        │ (combined classification)           │    │
│     └─────────────────────────┘        └─────────────────────────────────────┘    │
│    Output: R (Relevant) / S (Substitute) / C (Complementary) / N (Not Rel.)       │
└───────────────────────────────────────────────────────────────────────────────────┘
```

## Stage Details

### Stage 1: Brand Entity Extraction (M01-M03)
Extract brand entities for your product and known competitors.

| Path | Modules     | Description |
|------|-------------|-------------|
| **A** | M01 = M03   | Extract own brand entities + competitor entities |
| **B** | M01a + M01b | Extract brand variations + brand-related terms |

### Stage 2: Brand Scope Classification (M02/M04/M05)
Classify keywords by brand ownership.

| Path | Modules         | When to use |
|------|-----------------|-------------|
| **A** | M02, M04, M05   | After Path A (M01 + M03) |
| **B** | M02b M04b, M05b | After Path B (M01a + M01b) |

**Output categories:**
- **OB** (Own Brand) - Keywords containing your brand terms
- **CB** (Competitor Brand) - Keywords with known/hidden competitor brands
- **NB** (Non-Branded) - Generic search terms without brand affiliation

### Stage 3: Product Definition & Taxonomy (M06-M11)
Build product understanding for relevance matching.

| Module | Purpose |
|--------|---------|
| M06 | Generate product type taxonomy |
| M07 | Extract product attributes |
| M08 | Rank attributes by importance |
| M09 | Identify primary intended use |
| M10 | Validate intended use |
| M11 | Identify hard constraints (must-have requirements) |

### Stage 4: Relevance Classification (M12-M16)
Determine keyword relevance using data from Stage 3. Brand scope from Stage 2 is not used here — focus is purely on product relevance.

| Path | Modules | Description |
|------|---------|-------------|
| **A** | M12 → M13 → M14 → M15 → M16 | Step-by-step validation checks |
| **B** | M12b only | Combined single-pass classification |

**Output categories:**
- **R** (Relevant) - Exact product match
- **S** (Substitute) - Alternative product serving same purpose
- **C** (Complementary) - Product that pairs well with main product
- **N** (Not Relevant) - No meaningful relationship

## Quick Start

```bash
# 1. Clone and setup
git clone <repo-url>
cd kw-classification-v1.1

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API keys
cp .env.example .env
# Edit .env with your keys

# 5. Verify setup
python -c "from scripts.config import validate_project_structure; print('OK' if validate_project_structure() else 'Check paths')"
```

## Find Scripts & Docs Fast

- Start here: `docs/SCRIPTS_INDEX.md` (full scripts catalog + checklist), `docs/SCRIPTS_GUIDE.md` (workflow scripts), `docs/RESOURCE_MAPPING.md` (prompts/datasets map), `BRAINTRUST_MAP.md` (Braintrust IDs).
- Script folders: `scripts/batch/`, `scripts/analysis/`, `scripts/upload/`, `scripts/testing/`, `scripts/processing/`, `scripts/dspy_optimize/`, `scripts/data_import/`.
- Quick search: `rg --files scripts` or `rg -n "keyword" scripts docs`.
- Before writing a new script: search first, check `docs/SCRIPTS_INDEX.md`, and extend existing scripts when possible.

## Project Structure

```
kw-classification-v1.1/
├── prompts/
│   ├── modules/        # M01-M16 classification prompts
│   ├── judges/         # LLM-as-Judge evaluation prompts
│   ├── json_schemas/   # Output format definitions
│   └── backups/        # Prompt version backups
├── datasets/           # Training/evaluation data (JSONL)
├── scorers/            # LLM judge implementations
├── evaluation/         # LLM-as-Judge framework (67 rubrics)
│   ├── config/         # Rubrics YAML & judge templates
│   ├── judges/         # Judge system implementation
│   └── *.html          # Interactive evaluation reports
├── Examples/           # Product taxonomy examples
├── scripts/
│   ├── config.py               # Module configurations (22 modules)
│   ├── orchestrator.py         # Run LLM experiments
│   ├── experiment_registry.py  # Track experiment metadata
│   ├── sync_braintrust.py      # Upload experiments to Braintrust
│   ├── generate_annotation_csv.py  # Create annotation tasks
│   ├── calculate_agreement.py  # Compute Cohen's Kappa
│   ├── merge_annotations.py    # Merge & create gold datasets
│   ├── batch/          # OpenAI Batch API scripts
│   │   ├── generate_batch_requests.py  # Prepare JSONL batch files (golden)
│   │   ├── upload_batch.py             # Upload to OpenAI Batch API
│   │   ├── check_batch_status.py       # Monitor batch progress
│   │   ├── download_results.py         # Download completed results
│   │   ├── evaluate_results.py         # Evaluate against expected
│   │   ├── generate_synthetic_batch.py # Prepare JSONL batch files (synthetic)
│   │   ├── upload_synthetic_batch.py   # Upload synthetic batches
│   │   ├── check_synthetic_status.py   # Monitor synthetic batch progress
│   │   └── download_synthetic_results.py # Download synthetic results
│   ├── analysis/       # Error analysis & reporting
│   │   ├── error_analyzer.py     # Automated metrics (P/R/F1)
│   │   ├── pattern_detector.py   # Error pattern detection
│   │   ├── llm_judge_analyzer.py # LLM-as-Judge evaluation
│   │   ├── cohens_kappa.py       # Inter-rater reliability
│   │   ├── braintrust_uploader.py# Upload to Braintrust
│   │   ├── path_comparator.py    # Path A vs B comparison
│   │   ├── baseline_report.py    # Full baseline report
│   │   └── run_analysis.py       # Combined analysis runner
│   ├── upload/         # Braintrust upload scripts
│   ├── testing/        # Local evaluation scripts
│   └── processing/     # Data validation tools
├── batch_requests/     # Batch API request/response files
│   └── synthetic/      # Synthetic batch runs
├── docs/               # Documentation & rubrics
├── experiment_results/ # LLM evaluation outputs
│   └── .registry.json  # Experiment tracking metadata
├── annotation_tasks/   # CSV files for human annotators
├── validated_data/     # Merged annotations & gold datasets
├── .env.example        # API key template
└── requirements.txt    # Python dependencies
```

### User-Created Folders (`_KD` suffix)

Folders and files with `_KD` suffix were created for extended evaluation analysis and experimentation. These are separate from the core pipeline code.

```
kw-classification-v1.1/
├── evaluation_KD/                    # Extended LLM-as-Judge evaluation framework
│   ├── config/
│   │   ├── rubrics_v1.yaml           # Original evaluation rubrics (67 rubrics)
│   │   ├── rubrics_v2.yaml           # Improved rubrics with M01 fixes
│   │   └── judge_prompt_template.md  # Judge prompt template
│   ├── evaluation_experimentV1/      # Baseline evaluation results
│   │   ├── dashboards/               # Interactive HTML dashboards
│   │   │   ├── MODULE_ANALYSIS_DASHBOARD.html  # Pass/Fail rates by module
│   │   │   ├── MATCH_RATE_DASHBOARD.html       # Expected vs Actual comparison
│   │   │   └── interactive_rubrics.html        # Rubric browser
│   │   ├── full_evaluation_analysis_by_module/ # Per-module evaluation CSVs
│   │   ├── rubric_summaries/         # Aggregated rubric performance
│   │   ├── cohen_kappa/              # Inter-rater reliability analysis
│   │   └── *.csv                     # Evaluation spreadsheets
│   ├── evaluation_experimentV2/      # V2 rubrics evaluation (structure ready)
│   ├── multi_agent_eval/             # Adversarial Debate Evaluation System
│   │   ├── agents/                   # 4 evaluation agents (Critic, Defender, Judge, Meta-Judge)
│   │   ├── pipeline/                 # Orchestrator, aggregator, retry handler
│   │   ├── prompts/                  # Agent prompts (generic + module-specific)
│   │   ├── config/                   # Agent config, Likert rubrics
│   │   ├── results/                  # Evaluation output JSON files
│   │   ├── dashboards/               # Generated HTML dashboards
│   │   ├── run_eval.py               # CLI entry point
│   │   ├── generate_dashboard.py     # Dashboard generator
│   │   └── Adversarial_Debate_Evaluation_System.md  # Full documentation
│   ├── judge_results/                # LLM Judge raw output (JSON per module)
│   ├── *.py                          # Evaluation scripts (generate reports, run judge)
│   └── *.md                          # Architecture & workflow documentation
│
├── optimizer_KD/                     # Prompt optimization framework
│   ├── prompt_optimizer.py           # Core optimization logic
│   ├── html_report.py                # Generate optimization reports
│   ├── run_optimization.py           # Run optimization experiments
│   └── results/                      # Optimization experiment outputs
│
├── docs/
│   ├── academic-research_KD/         # LLM-as-a-Judge academic research
│   │   ├── llm-as-a-judge-research.md
│   │   └── llm-judge-approaches-research.md
│   ├── asin_coverage_analysis_KD.md  # Dataset ASIN coverage analysis
│   └── pipeline_trace_report_KD.md   # Pipeline execution tracing
```

**Key Dashboards:**
- `MODULE_ANALYSIS_DASHBOARD.html` - LLM Judge pass/fail decisions per module/rubric
- `MATCH_RATE_DASHBOARD.html` - Expected vs Actual output comparison (280 samples across 19 modules)

---

## LLM-as-Judge Evaluation Framework

Automated prompt improvement using Claude Code agents. Runs 15-iteration experiments to validate fixes.

**Agents** (`.claude/agents/`):
- **Orchestrator** - Coordinates workflow
- **Evaluation Runner** - Runs LLM judge evaluations
- **Prompt Analyzer** - Analyzes prompt requirements
- **Rubric Validator** - Classifies issues (Prompt/Model/Judge)
- **Suggestion Generator** - Documents improvement suggestions
- **Dashboard Generator** - Generates HTML reports
- **Prompt Improver** - Runs iteration experiments with temp copies

**Issue Types**: Prompt Issue (fix prompt) | Model Issue (document) | Judge Issue (fix rubric)

**Validated Results**:
| Module | Rubric | Improvement |
|--------|--------|-------------|
| M01 | No Duplicate Entities | 40% → 80% |
| M04 | CB Classification | 50% → 87.5% |

**Files**: `evaluation_KD/evaluation_experimentV4/dashboards/IMPROVEMENT_SUGGESTIONS.html`

---

## Multi-Agent Adversarial Debate Evaluation

Advanced evaluation system using 4 specialized LLM agents in an adversarial debate structure with Likert scoring (0-5). Reduces single-judge bias and improves reliability.

**Pipeline:**
```
Input → [Input Filter] → [Critic] → [Defender] → [Judge] → [Meta-Judge] → Score
         (injection      (find       (rebut       (score     (detect
          detection)     weaknesses)  claims)      debate)    sycophancy)
```

**Agents:**
| Agent | Role | Temperature |
|-------|------|-------------|
| **Input Filter** | Detect prompt injection attempts | 0.0 |
| **Critic** | Find 3+ weaknesses with evidence | 0.7 |
| **Defender** | Rebut each weakness, concede if valid | 0.5 |
| **Judge** | Score both sides, produce Likert scores | 0.3 |
| **Meta-Judge** | Detect sycophantic judging, trigger retry | 0.2 |

**Features:**
- Module-specific critic prompts (M01, M11 with custom categories)
- 3-run aggregation with median scores for robustness
- Confidence levels (HIGH/MEDIUM/LOW) based on score variance
- Auto-generated HTML dashboards with full debate transcripts

**Usage:**
```bash
# Run evaluation (3 runs with Meta-Judge)
python3 evaluation_KD/multi_agent_eval/run_eval.py --module m01 --limit 10

# Single run (faster, no Meta-Judge)
python3 evaluation_KD/multi_agent_eval/run_eval.py --module m01 --limit 10 --single-run

# Generate dashboard
python3 evaluation_KD/multi_agent_eval/generate_dashboard.py \
    evaluation_KD/multi_agent_eval/results/m01_multiagent_aggregated_*.json \
    -o evaluation_KD/multi_agent_eval/dashboards/m01_results.html --open
```

**Documentation:** `evaluation_KD/multi_agent_eval/Adversarial_Debate_Evaluation_System.md`

---

## 16 Classification Modules

| Phase | Module   | Purpose |
|-|----------|---------|
| **1. Brand** | M01      | Extract own brand entities |
| | M01a     | Generate brand variations |
| | M01b     | Extract brand-related terms |
| | M02/M02b | Classify own brand keywords |
| | M03      | Generate competitor entities |
| | M04/M04b | Classify competitor keywords |
| | M05/M05b | Classify non-branded keywords |
| **2. Product** |          |     | 
| | M06      |  Generate product taxonomy |
| | M07      | Extract product attributes |
| | M08      | Rank attribute importance |
| **3. Foundation** |          |  |
| | M09      | Identify primary intended use |    
| | M10      | Validate intended use |
| | M11      | Identify hard constraints |
| **4. Classification** |          |  |
| |   M12    | Check constraint violations   |
| | M12b     | Final R/S/C/N decision |
| | M13-M16  | Supporting checks |

## Usage

### Run Experiments & Human Annotation

```bash
# 1. Run LLM experiment for module M12
python scripts/orchestrator.py run m12

# 2. Generate annotation CSV for human validators
python scripts/generate_annotation_csv.py generate m12 --sample 100

# 3. After annotators complete their work, calculate agreement
python scripts/calculate_agreement.py analyze annotation_tasks/M12_annotation_*.csv

# 4. Merge annotations and create gold dataset
python scripts/merge_annotations.py merge annotation_tasks/M12_annotation_*.csv
python scripts/merge_annotations.py gold validated_data/M12_validated_*.csv

# 5. Upload experiment to Braintrust
python scripts/sync_braintrust.py sync --module m12
```

See `docs/SCRIPTS_GUIDE.md` for complete workflow documentation.

### Batch Processing (Recommended for Baseline)

Use OpenAI Batch API for cost-effective baseline evaluation (50% discount, 24hr completion):

```bash
# 1. Prepare batch files (all modules)
python scripts/batch/generate_batch_requests.py

# Or generate for specific modules
python scripts/batch/generate_batch_requests.py m02 m04 m05

# 2. Upload to OpenAI Batch API
python scripts/batch/upload_batch.py batch_requests/20260127_1200

# 3. Check status (run periodically)
python scripts/batch/check_batch_status.py batch_requests/20260127_1200

# 4. Download results when complete
python scripts/batch/download_results.py batch_requests/20260127_1200

# 5. Evaluate against expected values
python scripts/batch/evaluate_results.py batch_requests/20260127_1200
```

### Synthetic Batch Processing (Optimized Prompts)

Synthetic datasets live in `datasets/synthetic` and run with optimized prompts in `prompts/optimized`.

```bash
# 1. Generate synthetic batch files
python scripts/batch/generate_synthetic_batch.py --all

# Or specific modules
python scripts/batch/generate_synthetic_batch.py m01 m01a m01b m06 m07

# 2. Upload
python scripts/batch/upload_synthetic_batch.py batch_requests/synthetic/20260127_1200

# 3. Check status
python scripts/batch/check_synthetic_status.py batch_requests/synthetic/20260127_1200

# 4. Download results
python scripts/batch/download_synthetic_results.py batch_requests/synthetic/20260127_1200
```

### Error Analysis

After batch results are downloaded:

```bash
# Run full analysis pipeline (metrics + patterns + LLM judge)
python scripts/analysis/run_analysis.py --batch-dir batch_requests/20260112

# Skip LLM Judge (faster, free)
python scripts/analysis/run_analysis.py --batch-dir batch_requests/20260112 --skip-judge

# Generate comprehensive baseline report
python scripts/analysis/baseline_report.py --batch-dir batch_requests/20260112

# Compare Path A vs Path B results
python scripts/analysis/path_comparator.py --batch-dir batch_requests/20260112

# Calculate Cohen's Kappa (model vs ground truth)
python scripts/analysis/cohens_kappa.py --mode model-vs-truth \
    --results1 batch_requests/20260112/m02_results.jsonl \
    --dataset datasets/m02_dataset.jsonl
```

### Run Local Tests

```bash
# Test single module
python scripts/testing/run_local_tests_v2.py --module m02

# Test with LLM judge
python scripts/testing/run_llm_judge_eval.py --module m02

# Run all judges
python scripts/testing/run_all_judges.py
```

### Upload to Braintrust

```bash
# Upload prompts
python scripts/upload/upload_prompts.py

# Upload datasets
python scripts/upload/upload_datasets.py

# Upload batch results as experiments
python scripts/analysis/braintrust_uploader.py \
    --batch-dir batch_requests/20260112 \
    --project amazon-keyword-classification \
    --tags baseline gpt-4o-mini
```

### Validate Data

```bash
# Check dataset quality
python scripts/processing/validate_datasets.py

# Validate judge outputs
python scripts/processing/validate_judges.py
```

## Configuration

Edit `scripts/config.py` to customize:
- `PROJECT_ID` - Braintrust project ID
- `DEFAULT_MODEL` - LLM model (default: gpt-4o-mini)
- `MODULES` - Module definitions and settings

## API Keys Required

| Key | Purpose | Get it from |
|-----|---------|-------------|
| `BRAINTRUST_API_KEY` | Evaluation platform | [braintrust.dev](https://braintrust.dev) |
| `OPENAI_API_KEY` | Run LLM modules | [platform.openai.com](https://platform.openai.com) |
| `ANTHROPIC_API_KEY` | Optional, for Claude | [console.anthropic.com](https://console.anthropic.com) |

## Documentation

| Document | Description |
|----------|-------------|
| `docs/SCRIPTS_GUIDE.md` | **Experiment & annotation workflow scripts** |
| `docs/RESOURCE_MAPPING.md` | Prompts/datasets mapping & lookup helpers |
| `docs/MODULE_REFERENCE.md` | Full module documentation with data flow |
| `docs/BASELINE_TESTING_GUIDE.md` | Baseline testing process & analysis tools |
| `docs/MODULE_RUBRICS.md` | Evaluation criteria per module |
| `docs/DATASET_FIELD_MAPPING.md` | Data schema reference |
| `docs/ANNOTATION_SPREADSHEET_TEMPLATES.md` | Human annotation templates |
| `docs/MODULE_EVALUATION_METRICS.md` | Metrics definitions (P/R/F1/Kappa) |
| `docs/PIPELINE_ANALYSIS.md` | Pipeline architecture analysis |
| `docs/academic-research/` | LLM-as-a-Judge academic research |
| `evaluation/JUDGE_RUBRICS_AND_SETUP.md` | 67 evaluation rubrics setup guide |
| `evaluation/LLM_JUDGE_ARCHITECTURE_PLAN.md` | Judge system architecture |

---

*Last updated: January 27, 2026*
