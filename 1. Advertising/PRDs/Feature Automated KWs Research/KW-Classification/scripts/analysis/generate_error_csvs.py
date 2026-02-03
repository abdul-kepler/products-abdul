#!/usr/bin/env python3
"""
Generate CSV files with FP and FN cases for each module.
Output: ASIN, Brand, Keyword, Output, Expected, Reasoning, Error Type
"""

import json
import csv
import re
from pathlib import Path
from typing import Optional

# Configuration for each module
MODULE_CONFIG = {
    "m02": {
        "dataset": "m02_classify_own_brand_keywords.jsonl",
        "results": "m02_results.jsonl",
        "positive_class": "OB",
        "output_field": "branding_scope_1",  # Model outputs branding_scope_1
        "expected_field": "branding_scope_1",  # OB or None
        "reasoning_field": "reasoning"
    },
    "m02b": {
        "dataset": "m02b_classify_own_brand_keywords.jsonl",
        "results": "m02b_results.jsonl",
        "positive_class": "OB",
        "output_field": "branding_scope_1",  # Model outputs branding_scope_1
        "expected_field": "branding_scope_1",  # OB or None
        "reasoning_field": "reasoning"
    },
    "m04": {
        "dataset": "m04_classify_competitor_brand_keywords.jsonl",
        "results": "m04_results.jsonl",
        "positive_class": "CB",
        "output_field": "branding_scope_2",  # Model outputs branding_scope_2
        "expected_field": "branding_scope_2",  # CB or None
        "reasoning_field": "reasoning"
    },
    "m04b": {
        "dataset": "m04b_classify_competitor_brand_keywords.jsonl",
        "results": "m04b_results.jsonl",
        "positive_class": "CB",
        "output_field": "branding_scope_2",  # Model outputs branding_scope_2
        "expected_field": "branding_scope_2",  # CB or None
        "reasoning_field": "reasoning"
    },
    "m05": {
        "dataset": "m05_classify_nonbranded_keywords.jsonl",
        "results": "m05_results.jsonl",
        "positive_class": "NB",
        "output_field": "branding_scope_3",  # Model outputs branding_scope_3
        "expected_field": "branding_scope_3",  # NB or None
        "reasoning_field": "reasoning"
    },
    "m05b": {
        "dataset": "m05b_classify_nonbranded_keywords.jsonl",
        "results": "m05b_results.jsonl",
        "positive_class": "NB",
        "output_field": "branding_scope_3",  # Model outputs branding_scope_3
        "expected_field": "branding_scope_3",  # NB or None
        "reasoning_field": "reasoning"
    },
    "m12": {
        "dataset": "m12_check_hard_constraint_v1.1.jsonl",
        "results": "m12_results.jsonl",
        "positive_class": "True",
        "output_field": "violates_constraint",
        "expected_field": "violates_constraint",
        "reasoning_field": "reasoning"
    },
    "m12b": {
        "dataset": "m12b_combined_classification_v1.1.jsonl",
        "results": "m12b_results.jsonl",
        "positive_class": None,  # Multiclass
        "output_field": "classification",
        "expected_field": "relevancy",
        "reasoning_field": None  # Multiple reasoning fields
    },
    "m13": {
        "dataset": "m13_check_product_type_v1.1.jsonl",
        "results": "m13_results.jsonl",
        "positive_class": "True",
        "output_field": "same_product_type",
        "expected_field": "same_type",  # True or False
        "reasoning_field": "reasoning"
    },
    "m14": {
        "dataset": "m14_check_primary_use_same_type_v1.1.jsonl",
        "results": "m14_results.jsonl",
        "positive_class": "R",
        "output_field": "classification",
        "expected_field": "relevancy",
        "reasoning_field": "reasoning"
    },
    "m15": {
        "dataset": "m15_check_substitute_v1.1.jsonl",
        "results": "m15_results.jsonl",
        "positive_class": "S",
        "output_field": "classification",
        "expected_field": "relevancy",
        "reasoning_field": "reasoning"
    },
    "m16": {
        "dataset": "m16_check_complementary_v1.1.jsonl",
        "results": "m16_results.jsonl",
        "positive_class": "C",
        "output_field": "classification",
        "expected_field": "relevancy",
        "reasoning_field": "reasoning"
    }
}


def extract_reasoning(result_content: dict, module: str) -> str:
    """Extract reasoning from result based on module type."""
    if module == "m12b":
        # M12b has multiple reasoning fields
        reasons = []
        for step in ["step1_hard_constraint", "step2_product_type", "step3_primary_use", "step4_complementary"]:
            if step in result_content and result_content[step]:
                r = result_content[step].get("reasoning", "")
                if r:
                    reasons.append(f"{step}: {r}")
        return " | ".join(reasons)
    else:
        return result_content.get("reasoning", "") or result_content.get("explanation", "")


def normalize_value(value) -> str:
    """Normalize value for comparison."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "True" if value else "False"
    return str(value).strip()


def generate_error_csv(module: str, datasets_dir: Path, results_dir: Path, output_dir: Path):
    """Generate CSV with FP and FN cases for a module."""

    config = MODULE_CONFIG.get(module)
    if not config:
        print(f"  No config for {module}, skipping")
        return

    dataset_file = datasets_dir / config["dataset"]
    results_file = results_dir / config["results"]

    if not dataset_file.exists():
        print(f"  Dataset not found: {dataset_file}")
        return
    if not results_file.exists():
        print(f"  Results not found: {results_file}")
        return

    # Load dataset - build index by custom_id pattern
    dataset_map = {}
    with open(dataset_file, 'r') as f:
        for idx, line in enumerate(f):
            data = json.loads(line)
            custom_id = f"{module}_{idx:05d}"
            dataset_map[custom_id] = data

    # Process results
    errors = []
    total = 0

    with open(results_file, 'r') as f:
        for line in f:
            total += 1
            result_data = json.loads(line)
            custom_id = result_data.get("custom_id", "")

            # Get dataset entry
            dataset_entry = dataset_map.get(custom_id)
            if not dataset_entry:
                continue

            # Extract expected value
            expected_raw = dataset_entry.get("expected", {}).get(config["expected_field"])
            expected = normalize_value(expected_raw)

            # Extract predicted value from response
            try:
                content = result_data["response"]["body"]["choices"][0]["message"]["content"]
                result_content = json.loads(content)
                predicted_raw = result_content.get(config["output_field"])
                predicted = normalize_value(predicted_raw)
                reasoning = extract_reasoning(result_content, module)
            except Exception as e:
                predicted = "PARSE_ERROR"
                reasoning = f"Error: {e}"
                result_content = {}

            # Determine error type
            positive_class = config["positive_class"]

            if module == "m12b":
                # Multiclass - any mismatch is an error
                if predicted != expected:
                    error_type = f"MISMATCH ({expected}→{predicted})"
                    errors.append({
                        "custom_id": custom_id,
                        "dataset_entry": dataset_entry,
                        "predicted": predicted,
                        "expected": expected,
                        "reasoning": reasoning,
                        "error_type": error_type,
                        "result_content": result_content
                    })
            else:
                # Binary classification
                is_positive_expected = (expected == positive_class)
                is_positive_predicted = (predicted == positive_class)

                if is_positive_predicted and not is_positive_expected:
                    error_type = "FP"  # False Positive
                    errors.append({
                        "custom_id": custom_id,
                        "dataset_entry": dataset_entry,
                        "predicted": predicted,
                        "expected": expected,
                        "reasoning": reasoning,
                        "error_type": error_type,
                        "result_content": result_content
                    })
                elif not is_positive_predicted and is_positive_expected:
                    error_type = "FN"  # False Negative
                    errors.append({
                        "custom_id": custom_id,
                        "dataset_entry": dataset_entry,
                        "predicted": predicted,
                        "expected": expected,
                        "reasoning": reasoning,
                        "error_type": error_type,
                        "result_content": result_content
                    })

    if not errors:
        print(f"  {module}: No errors found")
        return

    # Write CSV
    output_file = output_dir / f"{module}_errors.csv"

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            "Error_Type", "ASIN", "Brand_Name", "Keyword",
            "Output", "Expected", "Reasoning", "Custom_ID"
        ])

        for error in errors:
            entry = error["dataset_entry"]
            inp = entry.get("input", {})
            meta = entry.get("metadata", {})

            # Extract fields
            asin = meta.get("asin", inp.get("asin", ""))
            brand_name = meta.get("brand_name", inp.get("brand_name", inp.get("own_brand", "")))
            keyword = inp.get("keyword", inp.get("search_keyword", ""))

            # Clean reasoning for CSV
            reasoning = error["reasoning"].replace("\n", " ").replace("\r", " ")
            if len(reasoning) > 500:
                reasoning = reasoning[:500] + "..."

            writer.writerow([
                error["error_type"],
                asin,
                brand_name,
                keyword,
                error["predicted"],
                error["expected"],
                reasoning,
                error["custom_id"]
            ])

    print(f"  {module}: {len(errors)} errors → {output_file.name}")

    # Also create summary
    if module == "m12b":
        # Group by error pattern
        patterns = {}
        for e in errors:
            p = e["error_type"]
            patterns[p] = patterns.get(p, 0) + 1
        print(f"    Patterns: {patterns}")
    else:
        fp_count = sum(1 for e in errors if e["error_type"] == "FP")
        fn_count = sum(1 for e in errors if e["error_type"] == "FN")
        print(f"    FP: {fp_count}, FN: {fn_count}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate error CSV files for analysis")
    parser.add_argument("--batch-dir", "-b", required=True, help="Batch directory")
    parser.add_argument("--datasets-dir", "-d", default="datasets", help="Datasets directory")
    parser.add_argument("--modules", "-m", nargs="*", help="Specific modules to process")

    args = parser.parse_args()

    batch_path = Path(args.batch_dir)
    datasets_path = Path(args.datasets_dir)
    results_path = batch_path / "results"
    output_path = batch_path / "error_analysis"
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"Batch: {batch_path}")
    print(f"Datasets: {datasets_path}")
    print(f"Output: {output_path}")
    print("=" * 60)

    modules = args.modules or list(MODULE_CONFIG.keys())

    for module in modules:
        print(f"\nProcessing {module}...")
        generate_error_csv(module, datasets_path, results_path, output_path)

    print("\n" + "=" * 60)
    print("Done! CSV files created in:", output_path)


if __name__ == "__main__":
    main()
