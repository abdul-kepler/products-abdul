# Scripts Index

This is the canonical index of scripts in this repo. Use it before writing a new script.

## Before Writing a New Script (Checklist)

- Search first: `rg --files scripts` and `rg -n "keyword" scripts docs`.
- Check this index for an existing script with the same goal.
- Prefer extending an existing script over creating a new one.
- If you must add a new script, document it here and in `README.md`.

## Naming & Placement Conventions

- Use a verb-first filename that describes the action: `generate_`, `run_`, `upload_`, `download_`, `validate_`, `convert_`, `sync_`, `analyze_`.
- Place scripts in the most specific folder that fits the purpose:
  - `scripts/batch/` for OpenAI Batch API runs.
  - `scripts/analysis/` for metrics, error analysis, and reporting.
  - `scripts/upload/` for Braintrust uploads.
  - `scripts/testing/` for local tests and evaluation helpers.
  - `scripts/processing/` for validation and data quality checks.
  - `scripts/data_import/` for dataset generation/import.
  - `scripts/dspy_optimize/` for optimizer workflows.
  - `scripts/experiments_converters/` for result conversion/export.
- Avoid creating new top-level scripts if a folder category already exists.
- Use consistent CLI style: `python scripts/…/script.py [args]`.

## Core Workflow

| Script | Purpose | Notes |
|---|---|---|
| `scripts/orchestrator.py` | Run LLM experiments for modules. | Primary entry point for experiments. |
| `scripts/experiment_registry.py` | Track local experiment metadata. | Keeps `.registry.json` in `experiment_results/`. |
| `scripts/sync_braintrust.py` | Upload local experiments to Braintrust. | Uploads CSV results to Braintrust. |

## Batch Processing (Golden Datasets)

| Script | Purpose | Notes |
|---|---|---|
| `scripts/batch/generate_batch_requests.py` | Create batch JSONL files for modules. | Uses golden datasets in `datasets/`. |
| `scripts/batch/upload_batch.py` | Upload batch files to OpenAI Batch API. | Takes a batch dir path. |
| `scripts/batch/check_batch_status.py` | Check batch status. | Reads `upload_log.json`. |
| `scripts/batch/download_results.py` | Download completed batch results. | Saves results under the batch dir. |
| `scripts/batch/evaluate_results.py` | Evaluate batch results vs expected. | Creates evaluation summaries. |
| `scripts/batch/generate_pipeline_batch.py` | Create batch files for M08->M11 pipeline. | Specialized pipeline runner. |

## Batch Processing (Synthetic Datasets)

| Script | Purpose | Notes |
|---|---|---|
| `scripts/batch/generate_synthetic_batch.py` | Create batch JSONL files for synthetic datasets. | Uses `datasets/synthetic` + `prompts/optimized`. |
| `scripts/batch/upload_synthetic_batch.py` | Upload synthetic batch files. | Uses `batch_requests/synthetic/...`. |
| `scripts/batch/check_synthetic_status.py` | Check synthetic batch status. | Reads `upload_log.json`. |
| `scripts/batch/download_synthetic_results.py` | Download synthetic batch results. | Creates experiment outputs. |

## Analysis

| Script | Purpose | Notes |
|---|---|---|
| `scripts/analysis/run_analysis.py` | Main analysis runner. | Metrics + patterns + LLM-judge. |
| `scripts/analysis/error_analyzer.py` | Error analysis metrics (P/R/F1). | Produces error summaries. |
| `scripts/analysis/pattern_detector.py` | Error pattern detection. | Option B analysis. |
| `scripts/analysis/llm_judge_analyzer.py` | LLM judge analysis. | Option A analysis. |
| `scripts/analysis/path_comparator.py` | Compare Path A vs Path B. | Uses batch results. |
| `scripts/analysis/baseline_report.py` | Generate baseline report. | Full report output. |
| `scripts/analysis/cohens_kappa.py` | Cohen's kappa calculator. | For agreement analysis. |
| `scripts/analysis/braintrust_uploader.py` | Upload batch results to Braintrust. | For batch-based experiments. |
| `scripts/analysis/generate_error_csvs.py` | Generate FP/FN CSVs by module. | Helps manual review. |
| `scripts/analysis/generate_enhanced_error_analysis.py` | Enhanced error analysis CSVs. | Extended error outputs. |
| `scripts/analysis/build_gepa_feedback_dataset.py` | Build GEPA feedback dataset. | Uses LLM-judge results. |
| `scripts/generate_error_analysis.py` | Create error analysis markdown. | Top-level convenience script. |

## Annotation Workflow

| Script | Purpose | Notes |
|---|---|---|
| `scripts/generate_annotation_csv.py` | Create annotation tasks. | Outputs to `annotation_tasks/`. |
| `scripts/calculate_agreement.py` | Compute inter-annotator agreement. | Cohen's kappa. |
| `scripts/merge_annotations.py` | Merge annotations, produce gold. | Writes to `validated_data/`. |

## Braintrust & Resource Mapping

| Script | Purpose | Notes |
|---|---|---|
| `scripts/braintrust_upload.py` | Upload prompts/datasets to Braintrust. | Low-level helper. |
| `scripts/braintrust_download.py` | Download experiments from Braintrust. | For local analysis. |
| `scripts/braintrust_list.py` | List Braintrust resources. | Inventory helper. |
| `scripts/braintrust_sync.py` | Match local files to Braintrust experiments. | Updates mappings. |
| `scripts/export_braintrust_prompts.py` | Export prompts + mappings. | Creates local mapping file. |
| `scripts/mapping_loader.py` | Central mapping access. | Use in scripts to avoid hardcoding IDs. |
| `scripts/update_prompt_schema.py` | Update prompt schema in Braintrust. | Structured outputs. |

## Data Import & Dataset Maintenance

| Script | Purpose | Notes |
|---|---|---|
| `scripts/data_import/generate_datasets_from_csv.py` | Build M06/M07 datasets from CSV. | Dataset generation. |
| `scripts/data_import/generate_sd_datasets.py` | Generate SD synthetic datasets from CSV. | Synthetic dataset creation. |
| `scripts/data_import/regenerate_m01_dataset.py` | Regenerate M01 dataset. | Uses prompt rules. |
| `scripts/regenerate_m01_with_llm.py` | Regenerate M01 using GPT-4o. | Produces expected outputs. |
| `scripts/analyze_mismatches.py` | Compare expected vs actual outputs. | Debug tool. |
| `scripts/audit_resources.py` | Audit local resources vs Braintrust. | Mapping health check. |

## DSPy Optimization

| Script | Purpose | Notes |
|---|---|---|
| `scripts/dspy_optimize/module_config.py` | Shared module config for optimizers. | MIPRO/COPRO/GEPA. |
| `scripts/dspy_optimize/compare_optimizers.py` | Compare optimizer results. | Report helper. |
| `scripts/dspy_optimize/extract_optimized.py` | Extract optimized prompts. | Pulls artifacts. |
| `scripts/dspy_optimize/mipro/optimize.py` | Run MIPRO optimizer. | Unified MIPRO runner. |
| `scripts/dspy_optimize/mipro/base_runner.py` | MIPRO shared runner utilities. | Internal module. |
| `scripts/dspy_optimize/copro/optimize_copro.py` | Run COPRO optimizer. | Prompt-instruction optimizer. |
| `scripts/dspy_optimize/gepa/optimize_gepa.py` | Run GEPA optimizer. | Text generation optimizer. |
| `scripts/dspy_optimize/gepa/evaluator.py` | GEPA evaluator. | LLM-as-judge evaluator. |

## Experiment Result Converters

| Script | Purpose | Notes |
|---|---|---|
| `scripts/experiments_converters/convert_all_experiments.py` | Convert all experiment CSVs to readable format. | Bulk converter. |
| `scripts/experiments_converters/csv_to_readable.py` | Convert generic CSV to readable. | JSON column expansion. |
| `scripts/experiments_converters/csv_to_readable_m08.py` | Convert M08 CSV to readable. | M08-specific formatting. |

## Local Testing

| Script | Purpose | Notes |
|---|---|---|
| `scripts/testing/run_local_tests_v2.py` | Run local tests with updated prompts. | Module-scoped tests. |
| `scripts/testing/run_llm_judge_eval.py` | Run LLM judge eval. | Evaluates M12b outputs. |
| `scripts/testing/run_all_judges.py` | Run judges for all modules. | Validates judges. |
| `scripts/testing/run_balanced_baseline.py` | Balanced baseline run. | Sampled distribution. |
| `scripts/testing/run_full_experiments.py` | Run all 22 modules. | Full baseline. |
| `scripts/testing/test_prompts_local.py` | Local prompt tests. | Path B prompt checks. |
| `scripts/testing/test_m06_v3.py` | M06 prompt comparison. | Targeted test. |
| `scripts/testing/test_m07_v2.py` | M07 prompt comparison. | Targeted test. |
| `scripts/testing/test_m08_v2.py` | M08 prompt comparison. | Targeted test. |
| `scripts/testing/test_m11_v2.py` | M11 prompt comparison. | Targeted test. |

## Validation

| Script | Purpose | Notes |
|---|---|---|
| `scripts/processing/validate_datasets.py` | Validate datasets vs prompt variables. | Input coverage check. |
| `scripts/processing/validate_judges.py` | Validate judge outputs. | Schema validation. |

## Common Confusions (Avoid Duplicates)

- `scripts/sync_braintrust.py` uploads local experiments to Braintrust, while `scripts/braintrust_sync.py` matches local files to Braintrust experiments and updates mappings.
- `scripts/braintrust_upload.py` is a helper; `scripts/upload/upload_prompts.py` and `scripts/upload/upload_datasets.py` are higher-level wrappers.
- `scripts/batch/generate_batch_requests.py` is the main batch generator; `scripts/batch/generate_pipeline_batch.py` is a special M08->M11 pipeline; `scripts/batch/generate_synthetic_batch.py` is for synthetic datasets.
- Error analysis exists in multiple forms: `scripts/generate_error_analysis.py` (markdown) and `scripts/analysis/*.py` (CSV + metrics).
