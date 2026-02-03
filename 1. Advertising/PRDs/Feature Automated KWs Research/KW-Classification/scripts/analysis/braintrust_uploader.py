#!/usr/bin/env python3
"""
Braintrust Experiment Uploader

Uploads batch results to Braintrust for tracking and comparison.

Features:
- Upload experiment results with metrics
- Tag experiments for filtering
- Compare with previous baselines
- Track prompt versions
"""

import json
import os
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional

import braintrust

# Load environment
env_file = Path(".env")
if env_file.exists():
    for line in env_file.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            os.environ[key.strip()] = value.strip().strip('"')


# Module metadata - label_field must match the expected output field in datasets
MODULE_INFO = {
    "m01": {"name": "Brand Entities", "type": "list", "label_field": "brand_entities", "output_field": "brand_entities"},
    "m01a": {"name": "Brand Variations", "type": "list", "label_field": "variations", "output_field": "variations"},
    "m01b": {"name": "Brand Related Terms", "type": "list", "label_field": "sub_brands", "output_field": "sub_brands"},
    "m02": {"name": "Own Brand (Path A)", "type": "binary", "label_field": "branding_scope_1", "output_field": "branding_scope_1"},
    "m02b": {"name": "Own Brand (Path B)", "type": "binary", "label_field": "branding_scope_1", "output_field": "branding_scope_1"},
    "m03": {"name": "Competitor Entities", "type": "list", "label_field": "competitor_entities", "output_field": "competitor_entities"},
    "m04": {"name": "Competitor Brand (Path A)", "type": "binary", "label_field": "branding_scope_2", "output_field": "branding_scope_2"},
    "m04b": {"name": "Competitor Brand (Path B)", "type": "binary", "label_field": "branding_scope_2", "output_field": "branding_scope_2"},
    "m05": {"name": "Non-Branded (Path A)", "type": "binary", "label_field": "branding_scope_3", "output_field": "branding_scope_3"},
    "m05b": {"name": "Non-Branded (Path B)", "type": "binary", "label_field": "branding_scope_3", "output_field": "branding_scope_3"},
    "m06": {"name": "Taxonomy", "type": "list", "label_field": "taxonomy", "output_field": "taxonomy"},
    "m07": {"name": "Variants", "type": "list", "label_field": "variants", "output_field": "variants"},
    "m08": {"name": "Attributes", "type": "list", "label_field": "attribute_table", "output_field": "attribute_table"},
    "m09": {"name": "Primary Use", "type": "text", "label_field": "primary_use", "output_field": "primary_use"},
    "m10": {"name": "Validated Use", "type": "text", "label_field": "validated_use", "output_field": "validated_use"},
    "m11": {"name": "Hard Constraints", "type": "list", "label_field": "hard_constraints", "output_field": "hard_constraints"},
    "m12": {"name": "Constraint Violation", "type": "binary", "label_field": "violates_constraint", "output_field": "violates_constraint"},
    "m12b": {"name": "Keyword Relevancy", "type": "multi", "label_field": "relevancy", "output_field": "relevancy"},
    "m13": {"name": "Same Product Type", "type": "binary", "label_field": "same_type", "output_field": "same_type"},
    "m14": {"name": "Same Primary Use", "type": "binary", "label_field": "relevancy", "output_field": "relevancy"},
    "m15": {"name": "Substitute Check", "type": "binary", "label_field": "relevancy", "output_field": "relevancy"},
    "m16": {"name": "Complementary Check", "type": "binary", "label_field": "relevancy", "output_field": "relevancy"},
}


def load_batch_results(results_file: str) -> list[dict]:
    """Load results from batch JSONL file."""
    results = []
    with open(results_file) as f:
        for line in f:
            record = json.loads(line)
            results.append(record)
    return results


def load_dataset(dataset_file: str, module: str = None) -> dict:
    """Load dataset and return as dict keyed by index (matching batch custom_id format)."""
    dataset = {}
    with open(dataset_file) as f:
        for idx, line in enumerate(f):
            if line.strip():
                record = json.loads(line)
                # Use zero-padded index to match batch custom_id format
                # e.g., "m02_00000" -> "00000"
                index_key = str(idx).zfill(5)
                dataset[index_key] = record
    return dataset


def parse_batch_response(record: dict) -> tuple[str, Optional[dict]]:
    """Parse batch API response record."""
    custom_id = record.get("custom_id", "")
    response = record.get("response", {})
    body = response.get("body", {})
    choices = body.get("choices", [])

    if not choices:
        return custom_id, None

    content = choices[0].get("message", {}).get("content", "")
    try:
        parsed = json.loads(content)
        return custom_id, parsed
    except json.JSONDecodeError:
        return custom_id, {"raw": content}


def calculate_metrics(expected: any, actual: any, module_type: str) -> tuple[dict, dict]:
    """Calculate metrics based on module type.

    Returns:
        tuple: (scores dict with numeric values only, metadata dict with other info)
    """
    scores = {}
    metadata = {}

    if module_type == "binary":
        correct = str(expected).lower().strip() == str(actual).lower().strip() if expected is not None and actual is not None else expected == actual
        scores["correct"] = 1.0 if correct else 0.0

        # Determine error type (non-numeric, goes in metadata)
        if not correct:
            if actual and not expected:
                metadata["error_type"] = "FP"
            elif expected and not actual:
                metadata["error_type"] = "FN"
            else:
                metadata["error_type"] = "mismatch"

    elif module_type == "multi":
        correct = str(expected) == str(actual)
        scores["correct"] = 1.0 if correct else 0.0

    elif module_type == "text":
        # Text comparison - normalized
        exp_norm = str(expected).lower().strip() if expected else ""
        act_norm = str(actual).lower().strip() if actual else ""
        correct = exp_norm == act_norm
        scores["correct"] = 1.0 if correct else 0.0

    elif module_type == "list":
        if isinstance(expected, list) and isinstance(actual, list):
            expected_set = set(str(e).lower() for e in expected)
            actual_set = set(str(a).lower() for a in actual)

            if expected_set:
                precision = len(expected_set & actual_set) / len(actual_set) if actual_set else 0.0
                recall = len(expected_set & actual_set) / len(expected_set)
                f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

                scores["precision"] = float(precision)
                scores["recall"] = float(recall)
                scores["f1"] = float(f1)
                metadata["missing_count"] = len(expected_set - actual_set)
                metadata["extra_count"] = len(actual_set - expected_set)
            else:
                scores["correct"] = 1.0 if not actual_set else 0.0
        else:
            scores["correct"] = 0.0

    return scores, metadata


def upload_experiment(
    project_name: str,
    experiment_name: str,
    results_file: str,
    dataset_file: str,
    module: str,
    tags: list[str] = None,
    metadata: dict = None
):
    """Upload batch results as Braintrust experiment."""

    module_info = MODULE_INFO.get(module.lower(), {
        "name": module,
        "type": "binary",
        "label_field": "expected"
    })

    print(f"Uploading experiment: {experiment_name}")
    print(f"Module: {module_info['name']} ({module_info['type']})")

    # Load data
    results = load_batch_results(results_file)
    dataset = load_dataset(dataset_file, module)

    print(f"Loaded {len(results)} results, {len(dataset)} dataset records")

    # Initialize Braintrust
    experiment = braintrust.init(
        project=project_name,
        experiment=experiment_name,
        metadata={
            "module": module,
            "module_name": module_info["name"],
            "module_type": module_info["type"],
            "timestamp": datetime.now().isoformat(),
            "tags": tags or [],
            **(metadata or {})
        }
    )

    # Process and log results
    total_logged = 0
    errors = []

    for record in results:
        custom_id, output = parse_batch_response(record)

        # Extract index from custom_id (e.g., "m02_00000" -> "00000")
        index_key = custom_id.replace(f"{module}_", "").replace(f"{module.upper()}_", "")
        if index_key not in dataset:
            continue

        input_record = dataset[index_key]
        label_field = module_info["label_field"]
        # Expected value is in the 'expected' dict of the dataset record
        expected_dict = input_record.get("expected", {})
        expected = expected_dict.get(label_field, input_record.get(label_field))

        # Get actual output - use output_field for model output
        output_field = module_info.get("output_field", label_field)
        if output is None:
            actual = None
        elif module_info["type"] == "list":
            actual = output.get(output_field, output.get("items", []))
        else:
            actual = output.get(output_field, output.get("result"))

        # Calculate metrics
        scores, score_metadata = calculate_metrics(expected, actual, module_info["type"])

        # Build input for logging
        log_input = {
            "custom_id": custom_id,
        }

        # Try to get keyword from different places
        input_data = input_record.get("input", {})
        if isinstance(input_data, dict):
            log_input["keyword"] = input_data.get("keyword", "")
        else:
            log_input["keyword"] = str(input_data)[:100]

        # Add relevant context fields from input or metadata
        for field in ["asin", "title", "brand", "product_type", "category"]:
            if field in input_record:
                log_input[field] = input_record[field]
            elif isinstance(input_data, dict) and field in input_data:
                log_input[field] = input_data[field]
            elif "metadata" in input_record and field in input_record["metadata"]:
                log_input[field] = input_record["metadata"][field]

        # Log to Braintrust
        experiment.log(
            input=log_input,
            output=output,
            expected=expected,
            scores=scores,
            metadata={
                "record_id": custom_id,
                "module": module,
                **score_metadata
            }
        )

        total_logged += 1

        if scores.get("correct", scores.get("f1", 1.0)) < 1.0:
            errors.append({
                "custom_id": custom_id,
                "expected": expected,
                "actual": actual,
                **scores,
                **score_metadata
            })

    # Summarize
    summary = experiment.summarize()

    # Construct experiment URL
    experiment_url = f"https://www.braintrust.dev/app/{project_name}/experiments/{experiment_name}"

    print(f"\n{'='*60}")
    print(f"UPLOAD COMPLETE")
    print(f"{'='*60}")
    print(f"Total logged: {total_logged}")
    print(f"Errors: {len(errors)}")
    print(f"Experiment URL: {experiment_url}")

    return experiment_url, errors


def upload_batch_directory(
    batch_dir: str,
    project_name: str,
    experiment_prefix: str = None,
    modules: list[str] = None,
    tags: list[str] = None
):
    """Upload all results from a batch directory."""

    batch_path = Path(batch_dir)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")

    if experiment_prefix is None:
        experiment_prefix = f"batch_{batch_path.name}"

    results = {}

    # Check for results/ subdirectory
    results_path = batch_path / "results"
    search_path = results_path if results_path.exists() else batch_path

    # Find all result files
    for results_file in search_path.glob("*_results.jsonl"):
        module = results_file.stem.replace("_results", "").lower()

        if modules and module not in [m.lower() for m in modules]:
            continue

        # Find corresponding dataset - search in datasets/ directory
        dataset_file = None
        for pattern in [f"datasets/{module}_*.jsonl", f"datasets/{module.upper()}_*.jsonl"]:
            matches = list(Path(".").glob(pattern))
            if matches:
                dataset_file = matches[0]
                break

        if dataset_file is None:
            print(f"Warning: No dataset found for {module}, skipping")
            continue

        experiment_name = f"{experiment_prefix}_{module}_{timestamp}"

        try:
            url, errors = upload_experiment(
                project_name=project_name,
                experiment_name=experiment_name,
                results_file=str(results_file),
                dataset_file=str(dataset_file),
                module=module,
                tags=tags
            )
            results[module] = {"url": url, "errors": len(errors)}
        except Exception as e:
            print(f"Error uploading {module}: {e}")
            results[module] = {"error": str(e)}

    return results


def main():
    parser = argparse.ArgumentParser(description="Upload batch results to Braintrust")
    parser.add_argument("--batch-dir", "-b", help="Directory with batch results")
    parser.add_argument("--results-file", "-r", help="Single results file")
    parser.add_argument("--dataset-file", "-d", help="Dataset file (for single upload)")
    parser.add_argument("--module", "-m", help="Module name (for single upload)")
    parser.add_argument("--modules", nargs="+", help="Modules to upload (for batch dir)")
    parser.add_argument("--project", "-p", default="amazon-keyword-classification",
                        help="Braintrust project name")
    parser.add_argument("--experiment", "-e", help="Experiment name or prefix")
    parser.add_argument("--tags", "-t", nargs="+", help="Tags for experiment")

    args = parser.parse_args()

    if args.batch_dir:
        results = upload_batch_directory(
            batch_dir=args.batch_dir,
            project_name=args.project,
            experiment_prefix=args.experiment,
            modules=args.modules,
            tags=args.tags
        )
        print(f"\n{'='*60}")
        print("ALL UPLOADS SUMMARY")
        print(f"{'='*60}")
        for module, result in results.items():
            if "url" in result:
                print(f"  {module}: {result['errors']} errors - {result['url']}")
            else:
                print(f"  {module}: FAILED - {result['error']}")

    elif args.results_file and args.dataset_file and args.module:
        experiment_name = args.experiment or f"{args.module}_{datetime.now().strftime('%Y%m%d_%H%M')}"
        upload_experiment(
            project_name=args.project,
            experiment_name=experiment_name,
            results_file=args.results_file,
            dataset_file=args.dataset_file,
            module=args.module,
            tags=args.tags
        )
    else:
        parser.print_help()
        print("\nExamples:")
        print("  # Upload all results from batch directory")
        print("  python braintrust_uploader.py --batch-dir batch_requests/20260112_2127")
        print("")
        print("  # Upload specific modules with tags")
        print("  python braintrust_uploader.py --batch-dir batch_requests/20260112_2127 \\")
        print("      --modules m02 m04 m05 --tags baseline path-a")
        print("")
        print("  # Upload single result file")
        print("  python braintrust_uploader.py -r results.jsonl -d dataset.jsonl -m m02")


if __name__ == "__main__":
    main()
