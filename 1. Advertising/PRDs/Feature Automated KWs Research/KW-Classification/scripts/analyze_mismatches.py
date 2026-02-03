#!/usr/bin/env python3
"""
Analyze mismatches between expected and actual LLM outputs.
Helps identify patterns in errors - dataset issues, prompt problems, or edge cases.

Usage:
    python scripts/analyze_mismatches.py batch_requests/20260114_1427 m05_v5
"""

import argparse
import json
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent


def load_dataset(module_id: str) -> list:
    """Load dataset for module."""
    datasets_dir = PROJECT_ROOT / "datasets"

    # Try different naming patterns
    patterns = [
        f"{module_id}_*.jsonl",
        f"{module_id.replace('_', '-')}*.jsonl",
    ]

    for pattern in patterns:
        files = list(datasets_dir.glob(pattern))
        if files:
            # Get the versioned one if available
            files.sort(key=lambda x: x.name, reverse=True)
            dataset_file = files[0]
            break
    else:
        # Fallback to specific mapping
        dataset_map = {
        }
        if module_id in dataset_map:
            dataset_file = datasets_dir / dataset_map[module_id]
        else:
            print(f"Dataset not found for {module_id}")
            return []

    print(f"Loading dataset: {dataset_file.name}")
    records = []
    with open(dataset_file) as f:
        for line in f:
            records.append(json.loads(line))
    return records


def load_results(batch_dir: Path, module_id: str) -> list:
    """Load LLM results."""
    results_file = batch_dir / "results" / f"{module_id}_results.jsonl"
    if not results_file.exists():
        print(f"Results not found: {results_file}")
        return []

    results = []
    with open(results_file) as f:
        for line in f:
            results.append(json.loads(line))
    return results


def load_evaluation(batch_dir: Path) -> dict:
    """Load evaluation report."""
    eval_file = batch_dir / "evaluation_report.json"
    if not eval_file.exists():
        print(f"Evaluation not found: {eval_file}")
        return {}

    with open(eval_file) as f:
        return json.load(f)


def extract_llm_output(result: dict) -> dict:
    """Extract the actual LLM output from result."""
    try:
        response = result.get("response", {})
        body = response.get("body", {})
        choices = body.get("choices", [])
        if choices:
            content = choices[0].get("message", {}).get("content", "")
            if content:
                return json.loads(content)
    except (json.JSONDecodeError, KeyError, IndexError):
        pass
    return {}


def analyze_mismatches(batch_dir: Path, module_id: str):
    """Analyze mismatches in detail."""

    # Load data
    dataset = load_dataset(module_id)
    results = load_results(batch_dir, module_id)
    evaluation = load_evaluation(batch_dir)

    if not dataset or not results:
        return

    # Get mismatches
    module_eval = None
    for ev in evaluation.get("evaluations", []):
        if ev["module"] == module_id:
            module_eval = ev
            break

    if not module_eval:
        print(f"No evaluation found for {module_id}")
        return

    mismatches = module_eval.get("mismatches", [])

    print(f"\n{'='*80}")
    print(f"MISMATCH ANALYSIS: {module_id}")
    print(f"{'='*80}")
    print(f"Total records: {len(dataset)}")
    print(f"Accuracy: {module_eval['accuracy']}%")
    print(f"Mismatches: {len(mismatches)}")

    # Categorize mismatches
    false_negatives = []  # Expected NB, got null
    false_positives = []  # Expected null, got NB

    for mm in mismatches:
        idx = mm["index"]
        expected = mm["expected"]
        actual = mm["actual"]

        if expected == "NB" and actual is None:
            false_negatives.append(idx)
        elif expected is None and actual == "NB":
            false_positives.append(idx)

    print(f"\nFalse Negatives (expected NB, got null): {len(false_negatives)}")
    print(f"False Positives (expected null, got NB): {len(false_positives)}")

    # Detailed analysis
    print(f"\n{'='*80}")
    print("FALSE NEGATIVES - LLM missed these as non-branded")
    print(f"{'='*80}")

    for idx in false_negatives[:10]:  # Show first 10
        if idx < len(dataset) and idx < len(results):
            record = dataset[idx]
            result = results[idx]
            llm_output = extract_llm_output(result)

            keyword = record.get("input", {}).get("keyword", "N/A")
            own_brands = record.get("input", {}).get("own_brand_entities", [])
            competitor_brands = record.get("input", {}).get("competitor_brand_entities", [])

            print(f"\n[Index {idx}]")
            print(f"  Keyword: {keyword}")
            print(f"  Own Brands: {own_brands[:5]}...")
            print(f"  Competitor Brands: {competitor_brands[:5]}...")
            print(f"  Expected: NB")
            print(f"  LLM Output: {llm_output}")
            print(f"  LLM Reasoning: {llm_output.get('reasoning', 'N/A')[:200]}")

    print(f"\n{'='*80}")
    print("FALSE POSITIVES - LLM incorrectly classified as non-branded")
    print(f"{'='*80}")

    for idx in false_positives[:10]:  # Show first 10
        if idx < len(dataset) and idx < len(results):
            record = dataset[idx]
            result = results[idx]
            llm_output = extract_llm_output(result)

            keyword = record.get("input", {}).get("keyword", "N/A")
            own_brands = record.get("input", {}).get("own_brand_entities", [])
            competitor_brands = record.get("input", {}).get("competitor_brand_entities", [])
            expected_scope = record.get("expected", {}).get("branding_scope_1")

            print(f"\n[Index {idx}]")
            print(f"  Keyword: {keyword}")
            print(f"  Own Brands: {own_brands[:5]}...")
            print(f"  Competitor Brands: {competitor_brands[:5]}...")
            print(f"  Expected (dataset): {expected_scope}")
            print(f"  LLM Output: {llm_output.get('branding_scope_1')}")
            print(f"  LLM Reasoning: {llm_output.get('reasoning', 'N/A')[:200]}")

    # Pattern analysis
    print(f"\n{'='*80}")
    print("PATTERN ANALYSIS")
    print(f"{'='*80}")

    # Check for common patterns in mismatches
    fn_keywords = []
    fp_keywords = []

    for idx in false_negatives:
        if idx < len(dataset):
            fn_keywords.append(dataset[idx].get("input", {}).get("keyword", ""))

    for idx in false_positives:
        if idx < len(dataset):
            fp_keywords.append(dataset[idx].get("input", {}).get("keyword", ""))

    print(f"\nFalse Negative Keywords:")
    for kw in fn_keywords[:15]:
        print(f"  - {kw}")

    print(f"\nFalse Positive Keywords:")
    for kw in fp_keywords[:15]:
        print(f"  - {kw}")

    # Check if dataset labels might be wrong
    print(f"\n{'='*80}")
    print("POTENTIAL DATASET ISSUES")
    print(f"{'='*80}")

    issues = []
    for idx in false_positives:
        if idx < len(dataset):
            record = dataset[idx]
            keyword = record.get("input", {}).get("keyword", "").lower()
            own_brands = [b.lower() for b in record.get("input", {}).get("own_brand_entities", [])]
            competitor_brands = [b.lower() for b in record.get("input", {}).get("competitor_brand_entities", [])]

            # Check if keyword actually contains any brand
            contains_own = any(brand in keyword for brand in own_brands if brand)
            contains_competitor = any(brand in keyword for brand in competitor_brands if brand)

            if not contains_own and not contains_competitor:
                issues.append({
                    "index": idx,
                    "keyword": keyword,
                    "expected": record.get("expected", {}).get("branding_scope_1"),
                    "issue": "Expected null but keyword appears generic (no brand match)"
                })

    if issues:
        print(f"\nFound {len(issues)} potential dataset labeling issues:")
        for issue in issues[:10]:
            print(f"  [{issue['index']}] '{issue['keyword']}' - {issue['issue']}")
    else:
        print("\nNo obvious dataset issues detected.")


def main():
    parser = argparse.ArgumentParser(description="Analyze LLM mismatches")
    parser.add_argument("batch_dir", help="Batch directory path")
    parser.add_argument("module_id", help="Module ID (e.g., m05_v5)")

    args = parser.parse_args()

    batch_dir = Path(args.batch_dir)
    if not batch_dir.exists():
        print(f"Batch directory not found: {batch_dir}")
        return

    analyze_mismatches(batch_dir, args.module_id)


if __name__ == "__main__":
    main()
