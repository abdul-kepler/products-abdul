#!/usr/bin/env python3
"""
Evaluate batch results against expected outputs.

Compares model outputs with ground truth from datasets.

Usage:
    python scripts/batch/evaluate_results.py <batch_dir>
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATASETS_DIR = PROJECT_ROOT / "datasets"

# Module configurations with expected output field mappings
# output_field: field name in actual (LLM output) JSON
# expected_field: field name in expected JSON (if different from output_field)
# compare_type: bool, classification, exact, list, list_of_dicts
MODULE_CONFIGS = {
    "m01": {"output_field": "brand_entities", "compare_type": "list"},
    "m01a": {"output_field": "variations", "compare_type": "list"},
    "m01b": {"output_field": "sub_brands", "compare_type": "list"},  # Has multiple fields, check main one
    "m02": {"output_field": "branding_scope_1", "compare_type": "exact"},
    "m02_v2": {"output_field": "branding_scope_1", "compare_type": "exact"},
    "m02b": {"output_field": "branding_scope_1", "compare_type": "exact"},
    "m02b_v2": {"output_field": "branding_scope_1", "compare_type": "exact"},
    "m03": {"output_field": "competitor_entities", "compare_type": "list"},
    "m04": {"output_field": "branding_scope_2", "compare_type": "exact"},
    "m04b": {"output_field": "branding_scope_2", "compare_type": "exact"},
    "m05": {"output_field": "branding_scope_3", "compare_type": "exact"},
    "m05_v2": {"output_field": "branding_scope_3", "compare_type": "exact"},
    "m05b": {"output_field": "branding_scope_3", "compare_type": "exact"},
    "m05b_v2": {"output_field": "branding_scope_3", "compare_type": "exact"},
    # V3 modules with unified format
    "m02_v3": {"output_field": "branding_scope_1", "compare_type": "exact"},
    "m04_v3": {"output_field": "branding_scope_2", "compare_type": "exact"},
    "m05_v3": {"output_field": "branding_scope_3", "compare_type": "exact"},
    # V4 modules with fixed own_brand_entities
    "m04_v4": {"output_field": "branding_scope_2", "compare_type": "exact"},
    "m05_v4": {"output_field": "branding_scope_3", "compare_type": "exact"},
    # V5 modules with anti-hallucination prompt improvements
    "m05_v5": {"output_field": "branding_scope_3", "compare_type": "exact"},
    "m06": {"output_field": "taxonomy", "compare_type": "list_of_dicts"},
    "m07": {"output_field": "variants", "compare_type": "list"},  # Has multiple fields
    "m08": {"output_field": "attribute_table", "compare_type": "list_of_dicts"},
    "m09": {"output_field": "primary_use", "compare_type": "exact"},
    "m10": {"output_field": "validated_use", "compare_type": "exact"},
    "m11": {"output_field": "hard_constraints", "compare_type": "list"},
    "m12": {"output_field": None, "compare_type": "m12_special"},  # Special: relevancy->violates_constraint mapping
    "m12b": {"output_field": "classification", "expected_field": "relevancy", "compare_type": "classification"},
    "m13": {"output_field": "same_product_type", "expected_field": "same_type", "compare_type": "bool"},
    "m14": {"output_field": "classification", "expected_field": "relevancy", "compare_type": "classification"},
    "m15": {"output_field": "classification", "expected_field": "relevancy", "compare_type": "classification"},
    "m16": {"output_field": "classification", "expected_field": "relevancy", "compare_type": "classification"},
}

# Dataset filename mapping
DATASET_FILES = {
    "m01": "m01_extract_own_brand_entities.jsonl",
    "m01a": "m01a_extract_own_brand_variations.jsonl",
    "m01b": "m01b_extract_brand_related_terms.jsonl",
    "m02": "m02_classify_own_brand_keywords.jsonl",
    "m02b": "m02b_classify_own_brand_keywords.jsonl",
    "m03": "m03_generate_competitor_entities.jsonl",
    "m04": "m04_classify_competitor_brand_keywords.jsonl",
    "m04b": "m04b_classify_competitor_brand_keywords.jsonl",
    "m05": "m05_classify_nonbranded_keywords.jsonl",
    "m05b": "m05b_classify_nonbranded_keywords.jsonl",
    "m06": "m06_generate_product_type_taxonomy.jsonl",
    "m07": "m07_extract_product_attributes.jsonl",
    "m08": "m08_assign_attribute_ranks.jsonl",
    "m09": "m09_identify_primary_intended_use_v1.1.jsonl",
    "m10": "m10_validate_primary_intended_use_v1.1.jsonl",
    "m11": "m11_identify_hard_constraints_v1.1.jsonl",
    "m12": "m12_check_hard_constraint_v1.1.jsonl",
    "m12b": "m12b_combined_classification_v1.1.jsonl",
    "m13": "m13_check_product_type_v1.1.jsonl",
    "m14": "m14_check_primary_use_same_type_v1.1.jsonl",
    "m15": "m15_check_substitute_v1.1.jsonl",
    "m16": "m16_check_complementary_v1.1.jsonl",
}


def load_dataset(filepath: Path) -> list[dict]:
    """Load JSONL dataset."""
    records = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def load_batch_results(filepath: Path) -> dict:
    """Load batch results into a dict keyed by custom_id."""
    results = {}
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                record = json.loads(line)
                custom_id = record.get("custom_id", "")
                results[custom_id] = record
    return results


def extract_model_output(batch_result: dict) -> dict | None:
    """Extract the model's JSON output from batch result."""
    try:
        response = batch_result.get("response", {})
        body = response.get("body", {})
        choices = body.get("choices", [])

        if not choices:
            return None

        content = choices[0].get("message", {}).get("content", "")
        return json.loads(content)

    except (json.JSONDecodeError, KeyError, IndexError):
        return None


def compare_bool(expected: bool, actual: bool) -> bool:
    """Compare boolean values."""
    return expected == actual


def compare_classification(expected: str, actual: str) -> bool:
    """Compare classification values (R/NR, S/NS, C/NC, True/False)."""
    # Normalize values
    expected = str(expected).upper().strip()
    actual = str(actual).upper().strip()

    # Handle various classification schemes
    positive_values = {"R", "S", "C", "TRUE", "YES", "1"}
    negative_values = {"NR", "NS", "NC", "N", "FALSE", "NO", "0"}

    expected_positive = expected in positive_values
    actual_positive = actual in positive_values

    return expected_positive == actual_positive


def compare_exact(expected, actual) -> bool:
    """Compare exact string values."""
    if expected is None and actual is None:
        return True
    if expected is None or actual is None:
        return False
    return str(expected).strip().lower() == str(actual).strip().lower()


def compare_list(expected: list, actual: list) -> tuple[bool, dict]:
    """Compare two lists using set-based precision/recall.

    Returns:
        tuple: (is_exact_match, metrics_dict)
    """
    if expected is None:
        expected = []
    if actual is None:
        actual = []

    # Normalize to lowercase strings for comparison
    def normalize(item):
        if isinstance(item, str):
            return item.strip().lower()
        return str(item).strip().lower()

    expected_set = set(normalize(x) for x in expected)
    actual_set = set(normalize(x) for x in actual)

    # Calculate metrics
    true_positives = len(expected_set & actual_set)
    false_positives = len(actual_set - expected_set)
    false_negatives = len(expected_set - actual_set)

    precision = true_positives / len(actual_set) if actual_set else (1.0 if not expected_set else 0.0)
    recall = true_positives / len(expected_set) if expected_set else (1.0 if not actual_set else 0.0)
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    is_exact = expected_set == actual_set

    return is_exact, {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "exact_match": is_exact,
        "expected_count": len(expected_set),
        "actual_count": len(actual_set),
        "missing": list(expected_set - actual_set)[:5],
        "extra": list(actual_set - expected_set)[:5]
    }


def compare_m12_special(expected_dict: dict, actual_dict: dict) -> bool:
    """Special comparison for M12 - maps relevancy to violates_constraint.

    Dataset uses: relevancy = "Null" (no violation) or "N" (violation -> Not relevant)
    LLM outputs: violates_constraint = false/true
    """
    expected_relevancy = expected_dict.get("relevancy", "") if isinstance(expected_dict, dict) else ""
    actual_violates = actual_dict.get("violates_constraint", None) if isinstance(actual_dict, dict) else None

    # Map dataset values to boolean
    # "Null" = no violation detected = violates_constraint should be false
    # "N" = violation detected = violates_constraint should be true
    if str(expected_relevancy).lower() == "null":
        expected_violates = False
    elif str(expected_relevancy).upper() == "N":
        expected_violates = True
    else:
        expected_violates = None

    return expected_violates == actual_violates


def compare_list_of_dicts(expected: list, actual: list, key_field: str = None) -> tuple[bool, dict]:
    """Compare lists of dictionaries.

    For structured lists like taxonomy, compares by key field or full structure.
    """
    if expected is None:
        expected = []
    if actual is None:
        actual = []

    # Convert dicts to comparable tuples
    def dict_to_tuple(d):
        if isinstance(d, dict):
            return tuple(sorted((k, str(v).lower() if isinstance(v, str) else v) for k, v in d.items()))
        return (str(d).lower(),)

    expected_tuples = set(dict_to_tuple(x) for x in expected)
    actual_tuples = set(dict_to_tuple(x) for x in actual)

    true_positives = len(expected_tuples & actual_tuples)
    precision = true_positives / len(actual_tuples) if actual_tuples else (1.0 if not expected_tuples else 0.0)
    recall = true_positives / len(expected_tuples) if expected_tuples else (1.0 if not actual_tuples else 0.0)
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    is_exact = expected_tuples == actual_tuples

    return is_exact, {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "exact_match": is_exact,
        "expected_count": len(expected),
        "actual_count": len(actual)
    }


def evaluate_module(module_id: str, results_file: Path, dataset: list[dict]) -> dict:
    """Evaluate results for a single module."""

    config = MODULE_CONFIGS.get(module_id)
    if not config:
        return {"error": f"Unknown module: {module_id}"}

    output_field = config["output_field"]
    expected_field = config.get("expected_field", output_field)  # Use output_field if not specified
    compare_type = config["compare_type"]

    # Load results
    batch_results = load_batch_results(results_file)

    correct = 0
    total = 0
    errors = []
    details = []

    for idx, record in enumerate(dataset):
        custom_id = f"{module_id}_{idx:05d}"
        batch_result = batch_results.get(custom_id)

        if not batch_result:
            errors.append({"index": idx, "error": "Missing result"})
            continue

        # Check for API error
        if batch_result.get("error"):
            errors.append({"index": idx, "error": batch_result["error"]})
            continue

        # Extract model output
        model_output = extract_model_output(batch_result)
        if not model_output:
            errors.append({"index": idx, "error": "Failed to parse model output"})
            continue

        # Get expected and actual values
        # Check multiple possible field names for expected output
        expected = record.get("expected_output", record.get("expected", record.get("output", {})))
        if isinstance(expected, dict):
            expected_value = expected.get(expected_field)  # Use expected_field for dataset
        else:
            expected_value = expected

        actual_value = model_output.get(output_field) if output_field else None  # Use output_field for LLM output

        # Compare based on type
        total += 1
        list_metrics = None

        if compare_type == "bool":
            is_correct = compare_bool(expected_value, actual_value)
        elif compare_type == "classification":
            is_correct = compare_classification(str(expected_value) if expected_value else "",
                                                str(actual_value) if actual_value else "")
        elif compare_type == "exact":
            is_correct = compare_exact(expected_value, actual_value)
        elif compare_type == "list":
            is_correct, list_metrics = compare_list(expected_value, actual_value)
        elif compare_type == "list_of_dicts":
            is_correct, list_metrics = compare_list_of_dicts(expected_value, actual_value)
        elif compare_type == "m12_special":
            # Special handling for M12 schema mismatch
            is_correct = compare_m12_special(expected, model_output)
        else:
            is_correct = expected_value == actual_value

        if is_correct:
            correct += 1
        else:
            detail = {
                "index": idx,
                "expected": expected_value,
                "actual": actual_value
            }
            if list_metrics:
                detail["metrics"] = list_metrics
            details.append(detail)

    accuracy = (correct / total * 100) if total > 0 else 0.0

    # Assign grade
    if accuracy >= 90:
        grade = "A"
    elif accuracy >= 80:
        grade = "B"
    elif accuracy >= 70:
        grade = "C"
    elif accuracy >= 60:
        grade = "D"
    else:
        grade = "F"

    return {
        "module": module_id,
        "correct": correct,
        "total": total,
        "accuracy": round(accuracy, 2),
        "grade": grade,
        "errors_count": len(errors),
        "errors": errors[:10],  # Limit error details
        "mismatches": details[:20]  # Limit mismatch details
    }


def main():
    """Main entry point."""

    if len(sys.argv) < 2:
        print("Usage: python evaluate_results.py <batch_dir>")
        sys.exit(1)

    batch_dir = Path(sys.argv[1])
    results_dir = batch_dir / "results"

    if not results_dir.exists():
        print(f"Error: Results directory not found: {results_dir}")
        print("Run download_results.py first.")
        sys.exit(1)

    # Find result files
    result_files = sorted(results_dir.glob("*_results.jsonl"))

    if not result_files:
        print(f"Error: No *_results.jsonl files found in {results_dir}")
        sys.exit(1)

    print("=" * 80)
    print("BATCH RESULTS EVALUATION")
    print("=" * 80)
    print(f"Results directory: {results_dir}")
    print(f"Modules to evaluate: {len(result_files)}")
    print()

    # Evaluate each module
    evaluations = []

    print(f"{'Module':<10} {'Correct':<10} {'Total':<10} {'Accuracy':<12} {'Grade'}")
    print("-" * 80)

    for result_file in result_files:
        module_id = result_file.stem.replace("_results", "")

        # Load dataset
        dataset_file = DATASET_FILES.get(module_id)
        if not dataset_file:
            print(f"{module_id:<10} Unknown module - skipped")
            continue

        dataset_path = DATASETS_DIR / dataset_file
        if not dataset_path.exists():
            print(f"{module_id:<10} Dataset not found - skipped")
            continue

        dataset = load_dataset(dataset_path)
        evaluation = evaluate_module(module_id, result_file, dataset)
        evaluations.append(evaluation)

        if "error" in evaluation:
            print(f"{module_id:<10} {evaluation['error']}")
        else:
            print(f"{module_id:<10} {evaluation['correct']:<10} {evaluation['total']:<10} {evaluation['accuracy']:.1f}%{' '*6} {evaluation['grade']}")

    # Summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    valid_evals = [e for e in evaluations if "error" not in e]

    total_correct = sum(e["correct"] for e in valid_evals)
    total_records = sum(e["total"] for e in valid_evals)
    overall_accuracy = (total_correct / total_records * 100) if total_records > 0 else 0

    print(f"Modules evaluated: {len(valid_evals)}")
    print(f"Total correct: {total_correct}/{total_records}")
    print(f"Overall accuracy: {overall_accuracy:.1f}%")

    # Grade distribution
    grades = defaultdict(int)
    for e in valid_evals:
        grades[e["grade"]] += 1

    print(f"\nGrade distribution:")
    for grade in ["A", "B", "C", "D", "F"]:
        if grades[grade] > 0:
            print(f"  {grade}: {grades[grade]} modules")

    # Low performers
    low_performers = [e for e in valid_evals if e["accuracy"] < 70]
    if low_performers:
        print(f"\nLow performers (< 70%):")
        for e in sorted(low_performers, key=lambda x: x["accuracy"]):
            print(f"  {e['module']}: {e['accuracy']:.1f}%")

    # Save evaluation report
    report = {
        "timestamp": datetime.now().isoformat(),
        "batch_dir": str(batch_dir),
        "evaluations": evaluations,
        "summary": {
            "modules_evaluated": len(valid_evals),
            "total_correct": total_correct,
            "total_records": total_records,
            "overall_accuracy": round(overall_accuracy, 2),
            "grade_distribution": dict(grades)
        }
    }

    report_file = batch_dir / "evaluation_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\nEvaluation report saved: {report_file}")


if __name__ == "__main__":
    main()
