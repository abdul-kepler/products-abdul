#!/usr/bin/env python3
"""
Balanced Baseline Test - 20% samples with proportional distribution.

Runs tests on ALL modules with balanced sampling where possible.
- If dataset > 20 records: use 20% of records
- If dataset <= 20 records: use all records
For binary classifiers: 50/50 split of positive/negative cases.
For extraction modules: diverse samples from different products.
"""

import json
import random
import sys
import os
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
from typing import Optional
from dotenv import load_dotenv

# Load environment
PROJECT_ROOT = Path(__file__).parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

import openai

# Directories
DATASETS_DIR = PROJECT_ROOT / "datasets"
PROMPTS_DIR = PROJECT_ROOT / "prompts" / "modules"
SCHEMAS_DIR = PROJECT_ROOT / "prompts" / "json_schemas"
RESULTS_DIR = PROJECT_ROOT / "experiment_results"

# Module configurations - UPDATED with correct file names
MODULES = {
    "m01": {
        "name": "ExtractOwnBrandEntities",
        "dataset": "m01_extract_own_brand_entities.jsonl",
        "prompt": "m01_extract_own_brand_entities.md",
        "schema": "m01_extract_own_brand_entities_schema.json",
        "type": "extraction",
        "compare_key": None,
    },
    "m01a": {
        "name": "ExtractOwnBrandVariations",
        "dataset": "m01a_extract_own_brand_variations.jsonl",
        "prompt": "m01a_extract_own_brand_variations.md",
        "schema": "m01a_extract_own_brand_variations_schema.json",
        "type": "extraction",
        "compare_key": None,
    },
    "m01b": {
        "name": "ExtractBrandRelatedTerms",
        "dataset": "m01b_extract_brand_related_terms.jsonl",
        "prompt": "m01b_extract_brand_related_terms.md",
        "schema": "m01b_extract_brand_related_terms_schema.json",
        "type": "extraction",
        "compare_key": None,
    },
    "m03": {
        "name": "GenerateCompetitorEntities",
        "dataset": "m03_generate_competitor_entities.jsonl",
        "prompt": "m03_generate_competitor_entities.md",
        "schema": "m03_generate_competitor_entities_schema.json",
        "type": "extraction",
        "compare_key": None,
    },
    "m02": {
        "name": "ClassifyOwnBrandKeywords",
        "dataset": "m02_classify_own_brand_keywords.jsonl",
        "prompt": "m02_classify_own_brand_keywords.md",
        "schema": "m02_classify_own_brand_keywords_schema.json",
        "type": "binary",
        "compare_key": "branding_scope_1",
        "positive_value": "OB",
    },
    "m02b": {
        "name": "ClassifyOwnBrandKeywords_PathB",
        "dataset": "m02b_classify_own_brand_keywords.jsonl",
        "prompt": "m02b_classify_own_brand_keywords.md",
        "schema": "m02b_classify_own_brand_keywords_schema.json",
        "type": "binary",
        "compare_key": "branding_scope_1",
        "positive_value": "OB",
    },
    "m04": {
        "name": "ClassifyCompetitorBrandKeywords",
        "dataset": "m04_classify_competitor_brand_keywords.jsonl",
        "prompt": "m04_classify_competitor_brand_keywords.md",
        "schema": "m04_classify_competitor_brand_keywords_schema.json",
        "type": "binary",
        "compare_key": "branding_scope_2",
        "positive_value": "CB",
    },
    "m04b": {
        "name": "ClassifyCompetitorBrandKeywords_PathB",
        "dataset": "m04b_classify_competitor_brand_keywords.jsonl",
        "prompt": "m04b_classify_competitor_brand_keywords.md",
        "schema": "m04b_classify_competitor_brand_keywords_schema.json",
        "type": "binary",
        "compare_key": "branding_scope_2",
        "positive_value": "CB",
    },
    "m05": {
        "name": "ClassifyNonbrandedKeywords",
        "dataset": "m05_classify_nonbranded_keywords.jsonl",
        "prompt": "m05_classify_nonbranded_keywords.md",
        "schema": "m05_classify_nonbranded_keywords_schema.json",
        "type": "binary",
        "compare_key": "branding_scope_3",
        "positive_value": "NB",
    },
    "m05b": {
        "name": "ClassifyNonBrandedKeywords_PathB",
        "dataset": "m05b_classify_nonbranded_keywords.jsonl",
        "prompt": "m05b_classify_nonbranded_keywords.md",
        "schema": "m05b_classify_nonbranded_keywords_schema.json",
        "type": "binary",
        "compare_key": "branding_scope_3",
        "positive_value": "NB",
    },
    "m06": {
        "name": "GenerateProductTypeTaxonomy",
        "dataset": "m06_generate_product_type_taxonomy.jsonl",
        "prompt": "m06_generate_product_type_taxonomy.md",
        "schema": "m06_generate_product_type_taxonomy_schema.json",
        "type": "extraction",
        "compare_key": None,
    },
    "m07": {
        "name": "ExtractProductAttributes",
        "dataset": "m07_extract_product_attributes.jsonl",
        "prompt": "m07_extract_product_attributes.md",
        "schema": "m07_extract_product_attributes_schema.json",
        "type": "extraction",
        "compare_key": None,
    },
    "m08": {
        "name": "AssignAttributeRanks",
        "dataset": "m08_assign_attribute_ranks.jsonl",
        "prompt": "m08_assign_attribute_ranks.md",
        "schema": "m08_assign_attribute_ranks_schema.json",
        "type": "extraction",
        "compare_key": None,
    },
    "m09": {
        "name": "IdentifyPrimaryIntendedUse",
        "dataset": "m09_identify_primary_intended_use_v1.1.jsonl",
        "prompt": "m09_identify_primary_intended_use_v1.1.md",
        "schema": "m09_identify_primary_intended_use_schema_v1.1.json",
        "type": "extraction",
        "compare_key": None,
    },
    "m10": {
        "name": "ValidatePrimaryIntendedUse",
        "dataset": "m10_validate_primary_intended_use_v1.1.jsonl",
        "prompt": "m10_validate_primary_intended_use_v1.1.md",
        "schema": "m10_validate_primary_intended_use_schema_v1.1.json",
        "type": "extraction",
        "compare_key": None,
    },
    "m11": {
        "name": "IdentifyHardConstraints",
        "dataset": "m11_identify_hard_constraints_v1.1.jsonl",
        "prompt": "m11_identify_hard_constraints_v1.1.md",
        "schema": "m11_identify_hard_constraints_schema_v1.1.json",
        "type": "extraction",
        "compare_key": None,
    },
    "m12": {
        "name": "CheckHardConstraint",
        "dataset": "m12_check_hard_constraint_v1.1.jsonl",
        "prompt": "m12_hard_constraint_violation_check_v1.1.md",
        "schema": "m12_hard_constraint_violation_check_schema_v1.1.json",
        "type": "binary",
        "compare_key": "relevancy",  # Key in expected
        "output_key": "classification",  # Key in model output
        "positive_value": "N",
    },
    "m12b": {
        "name": "CombinedClassification",
        "dataset": "m12b_combined_classification_v1.1.jsonl",
        "prompt": "m12b_combined_classification_v1.1.md",
        "schema": "m12_keyword_classification_decision_schema_v1.1.json",
        "type": "multiclass",
        "compare_key": "relevancy",  # Key in expected
        "output_key": "classification",  # Key in model output
        "classes": ["R", "S", "C", "N"],
    },
    "m13": {
        "name": "CheckProductType",
        "dataset": "m13_check_product_type_v1.1.jsonl",
        "prompt": "m13_product_type_check_v1.1.md",
        "schema": "m13_product_type_check_schema_v1.1.json",
        "type": "binary",
        "compare_key": "same_type",  # Key in expected
        "output_key": "same_product_type",  # Key in model output
        "positive_value": True,
    },
    "m14": {
        "name": "CheckPrimaryUseSameType",
        "dataset": "m14_check_primary_use_same_type_v1.1.jsonl",
        "prompt": "m14_primary_use_check_same_type_v1.1.md",
        "schema": "m14_primary_use_check_same_type_schema_v1.1.json",
        "type": "binary",
        "compare_key": "relevancy",  # Key in expected
        "output_key": "classification",  # Key in model output
        "positive_value": "R",
    },
    "m15": {
        "name": "CheckSubstitute",
        "dataset": "m15_check_substitute_v1.1.jsonl",
        "prompt": "m15_substitute_check_v1.1.md",
        "schema": "m15_substitute_check_schema_v1.1.json",
        "type": "binary",
        "compare_key": "relevancy",  # Key in expected
        "output_key": "classification",  # Key in model output
        "positive_value": "S",
    },
    "m16": {
        "name": "CheckComplementary",
        "dataset": "m16_check_complementary_v1.1.jsonl",
        "prompt": "m16_complementary_check_v1.1.md",
        "schema": "m16_complementary_check_schema_v1.1.json",
        "type": "binary",
        "compare_key": "relevancy",  # Key in expected
        "output_key": "classification",  # Key in model output
        "positive_value": "C",
    },
}


def load_jsonl(filepath: Path) -> list[dict]:
    """Load records from JSONL file."""
    records = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def get_balanced_samples(records: list[dict], config: dict, percentage: float = 0.2) -> list[dict]:
    """Get balanced samples based on module type.

    Args:
        records: All records from dataset
        config: Module configuration
        percentage: Percentage of records to use (default 20%)

    Rule: If dataset > 20 records, use percentage. Otherwise use all.
    """
    total_records = len(records)

    if total_records <= 20:
        total_target = total_records  # Use all
        print(f"    Using all {total_records} records (dataset <= 20)")
    else:
        total_target = max(int(total_records * percentage), 1)  # Use percentage
        print(f"    Using {total_target}/{total_records} records ({percentage*100:.0f}%)")

    mod_type = config.get("type", "extraction")
    compare_key = config.get("compare_key")

    if mod_type == "extraction":
        # For extraction modules - just take diverse samples
        # Group by product (asin) and take samples from different products
        by_product = defaultdict(list)
        for r in records:
            asin = r.get("metadata", {}).get("asin", r.get("input", {}).get("asin", "unknown"))
            by_product[asin].append(r)

        samples = []
        product_list = list(by_product.keys())
        random.shuffle(product_list)

        # Take at least one from each product, up to target
        for asin in product_list:
            if len(samples) >= total_target:
                break
            samples.append(random.choice(by_product[asin]))

        return samples

    elif mod_type == "binary":
        positive_value = config.get("positive_value")

        # Split by positive/negative
        positive = []
        negative = []

        for r in records:
            exp = r.get("expected", {})
            val = exp.get(compare_key)
            if val == positive_value:
                positive.append(r)
            else:
                negative.append(r)

        # Try to get 50/50 split, but respect availability
        half = total_target // 2

        pos_count = min(half, len(positive))
        neg_count = min(half, len(negative))

        # If one side is short, add more from the other
        if pos_count < half and len(negative) > neg_count:
            neg_count = min(total_target - pos_count, len(negative))
        if neg_count < half and len(positive) > pos_count:
            pos_count = min(total_target - neg_count, len(positive))

        random.shuffle(positive)
        random.shuffle(negative)

        samples = positive[:pos_count] + negative[:neg_count]
        random.shuffle(samples)

        print(f"    Balanced: {pos_count} positive ({positive_value}), {neg_count} negative")
        return samples

    elif mod_type == "multiclass":
        classes = config.get("classes", [])

        # Group by class
        by_class = defaultdict(list)
        for r in records:
            exp = r.get("expected", {})
            val = exp.get(compare_key)
            by_class[val].append(r)

        # Calculate proportional samples
        per_class = max(total_target // len(classes), 1)
        samples = []

        class_counts = {}
        for cls in classes:
            available = by_class.get(cls, [])
            take = min(per_class, len(available))
            random.shuffle(available)
            samples.extend(available[:take])
            class_counts[cls] = take

        random.shuffle(samples)
        print(f"    Multiclass distribution: {class_counts}")
        return samples

    # Fallback
    random.shuffle(records)
    return records[:total_target]


def fill_template(template: str, inputs: dict) -> str:
    """Fill mustache-style template with inputs."""
    result = template
    for key, value in inputs.items():
        placeholder = "{{" + key + "}}"
        if isinstance(value, (dict, list)):
            value_str = json.dumps(value, ensure_ascii=False)
        else:
            value_str = str(value) if value is not None else ""
        result = result.replace(placeholder, value_str)
    return result


def call_openai(prompt: str, schema: dict, model: str = "gpt-4o-mini", temperature: float = 0.0, max_tokens: int = 2000) -> dict:
    """Call OpenAI API with structured output.

    Args:
        prompt: The system prompt with filled placeholders
        schema: JSON schema for structured output
        model: OpenAI model to use
        temperature: Sampling temperature
        max_tokens: Maximum tokens in response (prevents repetition loops)
    """
    client = openai.OpenAI()

    json_schema = schema.get("json_schema", schema)

    if "name" in json_schema and "schema" in json_schema:
        response_format = {"type": "json_schema", "json_schema": json_schema}
    else:
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "response",
                "strict": True,
                "schema": json_schema
            }
        }

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": prompt}],
        temperature=temperature,
        response_format=response_format,
        max_tokens=max_tokens,
    )

    # Check if response was truncated
    finish_reason = response.choices[0].finish_reason
    content = response.choices[0].message.content

    if finish_reason == "length":
        # Response was truncated - JSON may be incomplete
        raise ValueError(f"Response truncated (max_tokens={max_tokens}). Content length: {len(content)}")

    return json.loads(content)


def compare_results(output: dict, expected: dict, config: dict) -> tuple[bool, str]:
    """Compare output with expected result."""
    mod_type = config.get("type", "extraction")
    compare_key = config.get("compare_key")

    if mod_type == "extraction":
        # For extraction modules - check if output has required keys
        # and the structure/type of values matches (not exact values)
        expected_keys = list(expected.keys())
        output_keys = list(output.keys())

        # Check if main keys exist
        has_keys = all(k in output for k in expected_keys)

        if not has_keys:
            return False, f"missing_keys: {set(expected_keys) - set(output_keys)}"

        # Check if types match (list vs scalar vs null)
        type_matches = 0
        for k in expected_keys:
            exp_val = expected.get(k)
            out_val = output.get(k)

            # Both null/None - match
            if exp_val is None and out_val is None:
                type_matches += 1
            # Both lists
            elif isinstance(exp_val, list) and isinstance(out_val, list):
                type_matches += 1
            # Both dicts
            elif isinstance(exp_val, dict) and isinstance(out_val, dict):
                type_matches += 1
            # Both strings
            elif isinstance(exp_val, str) and isinstance(out_val, str):
                type_matches += 1
            # Any non-null value when expected is non-null
            elif exp_val is not None and out_val is not None:
                type_matches += 1

        if type_matches == len(expected_keys):
            return True, "structure_match"
        else:
            return True, f"partial_match ({type_matches}/{len(expected_keys)} keys)"

    elif mod_type in ["binary", "multiclass"]:
        # Use output_key if specified (for schema/dataset key mapping)
        output_key = config.get("output_key", compare_key)
        out_val = output.get(output_key)
        exp_val = expected.get(compare_key)

        # Handle special case: M12 outputs null when no violation, dataset has 'Null' string
        if exp_val == "Null" and out_val is None:
            return True, "exact_match (Null/null)"
        if exp_val == "Null" and out_val == "Null":
            return True, "exact_match"

        # Normalize values for comparison
        if isinstance(exp_val, bool):
            out_val = out_val if isinstance(out_val, bool) else str(out_val).lower() == "true"

        if out_val == exp_val:
            return True, "exact_match"
        else:
            return False, f"mismatch: got {out_val}, expected {exp_val}"

    return False, "unknown_type"


def test_module(module_id: str, config: dict, model: str = "gpt-4o-mini", sample_pct: float = 0.2) -> dict:
    """Test a single module with balanced samples (pct% or all if <=20)."""
    print(f"\n{'='*60}")
    print(f"Testing {module_id.upper()} - {config['name']}")
    print(f"{'='*60}")

    # Load files
    dataset_path = DATASETS_DIR / config["dataset"]
    prompt_path = PROMPTS_DIR / config["prompt"]
    schema_path = SCHEMAS_DIR / config["schema"]

    # Check files exist
    if not dataset_path.exists():
        print(f"  ERROR: Dataset not found: {dataset_path}")
        return {"error": "dataset_not_found", "accuracy": 0}
    if not prompt_path.exists():
        print(f"  ERROR: Prompt not found: {prompt_path}")
        return {"error": "prompt_not_found", "accuracy": 0}
    if not schema_path.exists():
        print(f"  ERROR: Schema not found: {schema_path}")
        return {"error": "schema_not_found", "accuracy": 0}

    # Load data
    records = load_jsonl(dataset_path)
    print(f"  Total records: {len(records)}")

    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt_template = f.read()
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    # Get balanced samples
    samples = get_balanced_samples(records, config, percentage=sample_pct)
    print(f"  Testing {len(samples)} samples")

    # Run tests
    results = {
        "module": module_id,
        "name": config["name"],
        "total": len(samples),
        "correct": 0,
        "errors": 0,
        "details": [],
    }

    for i, record in enumerate(samples):
        inputs = record.get("input", {})
        expected = record.get("expected", {})
        keyword = inputs.get("keyword", inputs.get("asin", f"sample_{i}"))

        try:
            # Fill and call
            filled_prompt = fill_template(prompt_template, inputs)
            output = call_openai(filled_prompt, schema, model=model)

            # Compare
            is_correct, reason = compare_results(output, expected, config)

            if is_correct:
                results["correct"] += 1
                status = "✓"
            else:
                status = "✗"

            # Progress indicator
            if (i + 1) % 10 == 0 or i == len(samples) - 1:
                acc = results["correct"] / (i + 1) * 100
                print(f"  [{i+1}/{len(samples)}] Running accuracy: {acc:.1f}%")

            results["details"].append({
                "keyword": str(keyword)[:50],
                "correct": is_correct,
                "reason": reason,
                "output": output,
                "expected": expected,
            })

        except Exception as e:
            results["errors"] += 1
            print(f"  [{i+1}] ERROR: {e}")
            results["details"].append({
                "keyword": str(keyword)[:50],
                "correct": False,
                "reason": f"error: {str(e)}",
                "error": str(e),
            })

    # Calculate accuracy
    if results["total"] > 0:
        results["accuracy"] = round(results["correct"] / results["total"] * 100, 1)
    else:
        results["accuracy"] = 0

    # Assign grade
    acc = results["accuracy"]
    if acc >= 95:
        results["grade"] = "A"
    elif acc >= 80:
        results["grade"] = "B"
    elif acc >= 70:
        results["grade"] = "C"
    elif acc >= 60:
        results["grade"] = "D"
    else:
        results["grade"] = "F"

    print(f"\n  Result: {results['correct']}/{results['total']} correct ({results['accuracy']}%) - Grade {results['grade']}")

    return results


def main():
    print("=" * 70)
    print("BALANCED BASELINE TEST - 20% Samples (or all if <=20)")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Model: gpt-4o-mini")
    print(f"Temperature: 0")
    print(f"Rule: 20% of records if >20, otherwise all records")

    # Parse args - default: test ALL modules
    modules_to_test = list(MODULES.keys())
    sample_percentage = 0.2  # Default 20%

    args = sys.argv[1:]
    filtered_args = []

    for arg in args:
        if arg.startswith("--pct="):
            sample_percentage = float(arg.split("=")[1])
        else:
            filtered_args.append(arg)

    if filtered_args:
        modules_to_test = filtered_args

    print(f"Modules to test: {modules_to_test}")
    print(f"Sample percentage: {sample_percentage * 100:.0f}%")

    # Set seed for reproducibility
    random.seed(42)

    # Run tests
    all_results = []

    for module_id in modules_to_test:
        if module_id not in MODULES:
            print(f"\nWARNING: Unknown module {module_id}, skipping")
            continue

        config = MODULES[module_id]
        result = test_module(module_id, config, sample_pct=sample_percentage)
        all_results.append(result)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    total_correct = sum(r.get("correct", 0) for r in all_results)
    total_samples = sum(r.get("total", 0) for r in all_results)
    overall_accuracy = round(total_correct / total_samples * 100, 1) if total_samples > 0 else 0

    print(f"\n{'Module':<8} {'Name':<35} {'Correct':<10} {'Total':<8} {'Accuracy':<10} Grade")
    print("-" * 80)

    for r in all_results:
        if "error" in r and r.get("accuracy", 0) == 0:
            print(f"{r['module']:<8} {r.get('name', 'N/A'):<35} {'ERROR':<10} {'-':<8} {'-':<10} -")
        else:
            print(f"{r['module']:<8} {r['name']:<35} {r['correct']:<10} {r['total']:<8} {r['accuracy']:<10} {r['grade']}")

    print("-" * 80)
    print(f"{'TOTAL':<8} {'':<35} {total_correct:<10} {total_samples:<8} {overall_accuracy:<10}")

    # Grade distribution
    grades = Counter(r.get("grade", "-") for r in all_results if "grade" in r)
    print(f"\nGrade Distribution: {dict(grades)}")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    results_file = RESULTS_DIR / f"balanced_baseline_{timestamp}.json"

    summary = {
        "timestamp": datetime.now().isoformat(),
        "description": f"Balanced baseline test - {sample_percentage*100:.0f}% samples (or all if <=20 records)",
        "model": "gpt-4o-mini",
        "temperature": 0,
        "sample_percentage": sample_percentage,
        "sampling_rule": f"{sample_percentage*100:.0f}% if >20 records, else all",
        "total_modules": len(all_results),
        "overall_accuracy": overall_accuracy,
        "total_correct": total_correct,
        "total_samples": total_samples,
        "results": [
            {
                "module": r["module"],
                "name": r.get("name"),
                "accuracy": r.get("accuracy", 0),
                "correct": r.get("correct", 0),
                "total": r.get("total", 0),
                "grade": r.get("grade", "-"),
            }
            for r in all_results
        ],
        "grade_distribution": {
            "A": [r["module"] for r in all_results if r.get("grade") == "A"],
            "B": [r["module"] for r in all_results if r.get("grade") == "B"],
            "C": [r["module"] for r in all_results if r.get("grade") == "C"],
            "D": [r["module"] for r in all_results if r.get("grade") == "D"],
            "F": [r["module"] for r in all_results if r.get("grade") == "F"],
        },
    }

    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\nResults saved to: {results_file}")

    return summary


if __name__ == "__main__":
    main()
