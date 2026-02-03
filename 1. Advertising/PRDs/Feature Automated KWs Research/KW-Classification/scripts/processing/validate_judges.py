#!/usr/bin/env python3
"""
Judge Validation Script

Validates judge accuracy by comparing judge verdicts with ground truth.

A good judge should:
- PASS when model output is CORRECT (matches expected)
- FAIL when model output is WRONG (doesn't match expected)

Metrics:
- Precision: Of all PASS verdicts, how many were actually correct?
- Recall: Of all correct predictions, how many did judge PASS?
- F1: Harmonic mean of precision and recall
- Agreement: Overall % where judge verdict matches actual correctness

Usage:
    python validate_judges.py --module m12b --results-file results.jsonl --v3
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional
from collections import defaultdict

import openai
from dotenv import load_dotenv

# Load environment
load_dotenv(Path(__file__).parent.parent.parent.parent / ".env")

# Import from run_judge.py
from run_judge import (
    load_judge_prompt,
    build_judge_input,
    run_judge,
    _get_predicted_class,
    _normalize_expected_class,
    RESULTS_DIR
)


def get_actual_correctness(record: dict, module: str) -> bool:
    """Determine if model prediction actually matches expected."""
    out = record.get("output", {})
    exp = record.get("expected", {})

    module_lower = module.lower()

    # Classification modules (M02, M04, M12b, M13, M14, M15, M16)
    if module_lower in ["m02", "m04", "m12b", "m13", "m14", "m15", "m16"]:
        predicted = _get_predicted_class(out)
        expected = _normalize_expected_class(exp)
        return predicted.upper() == expected.upper()

    # Boolean modules
    if module_lower in ["m12", "m13", "m14", "m15", "m16"]:
        for field in ["same_type", "same_use", "is_substitute", "is_complementary", "violates_constraint"]:
            if field in exp:
                pred_val = out.get(field, False) if isinstance(out, dict) else False
                exp_val = exp.get(field, False)
                return bool(pred_val) == bool(exp_val)

    # Extraction modules - use F1 overlap
    if module_lower in ["m01", "m01a", "m01b", "m05", "m06", "m07", "m08", "m09", "m11"]:
        pred_items = _extract_items(out, module_lower)
        exp_items = _extract_items(exp, module_lower)

        if not exp_items:
            return len(pred_items) == 0

        pred_set = set(str(x).lower() for x in pred_items)
        exp_set = set(str(x).lower() for x in exp_items)

        overlap = len(pred_set & exp_set)
        precision = overlap / len(pred_set) if pred_set else 0
        recall = overlap / len(exp_set) if exp_set else 0

        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        return f1 >= 0.5

    return False


def _extract_items(data: dict, module: str) -> list:
    """Extract list items from output/expected based on module."""
    if not isinstance(data, dict):
        return []

    field_map = {
        "m01": ["entities", "brand_entities"],
        "m01a": ["variations"],
        "m01b": ["related_terms", "terms"],
        "m05": ["keywords", "non_branded"],
        "m06": ["taxonomy"],
        "m07": ["variants", "attributes"],
        "m08": ["rankings", "attribute_table"],
        "m09": ["primary_use", "use"],
        "m11": ["hard_constraints", "constraints"],
    }

    fields = field_map.get(module, [])
    for field in fields:
        if field in data:
            val = data[field]
            if isinstance(val, list):
                return val
            elif isinstance(val, dict):
                return list(val.keys())
            elif isinstance(val, str):
                return [val]
    return []


def validate_judges(
    module: str,
    results_file: Path,
    use_v2: bool = False,
    use_v3: bool = False,
    samples: int = 50,
    verbose: bool = False
) -> dict:
    """Run validation and return metrics."""

    print(f"Loading judge for module: {module}")
    judge_prompt = load_judge_prompt(module, use_v2=use_v2, use_v3=use_v3)

    print(f"Loading results from: {results_file}")
    results = []
    with open(results_file) as f:
        for line in f:
            results.append(json.loads(line))

    samples_to_validate = min(samples, len(results))
    print(f"Validating {samples_to_validate} samples...\n")

    true_positive = 0
    true_negative = 0
    false_positive = 0
    false_negative = 0

    validation_results = []

    for i, record in enumerate(results[:samples_to_validate]):
        inp = record.get("input", {})
        identifier = inp.get("keyword", inp.get("title", f"record_{i}"))[:40]

        print(f"[{i+1}/{samples_to_validate}] Validating: {identifier}...")

        try:
            actual_correct = get_actual_correctness(record, module)

            judge_input = build_judge_input(judge_prompt, record, module)
            judge_result = run_judge(judge_input)

            judge_verdict = judge_result.get("verdict", "FAIL")
            judge_pass = judge_verdict == "PASS"

            if judge_pass and actual_correct:
                true_positive += 1
                status = "✓ TP"
            elif not judge_pass and not actual_correct:
                true_negative += 1
                status = "✓ TN"
            elif judge_pass and not actual_correct:
                false_positive += 1
                status = "⚠ FP (judge too lenient)"
            else:
                false_negative += 1
                status = "⚠ FN (judge too strict)"

            print(f"  {status} | Judge: {judge_verdict} | Actual: {'CORRECT' if actual_correct else 'WRONG'}")

            if verbose:
                print(f"    Score: {judge_result.get('total_score', 0)}/100")

            validation_results.append({
                "identifier": identifier,
                "actual_correct": actual_correct,
                "judge_verdict": judge_verdict,
                "judge_score": judge_result.get("total_score", 0),
                "match": (judge_pass == actual_correct),
                "category": status.split()[1]
            })

        except Exception as e:
            print(f"  Error: {e}")
            continue

        print()

    total = true_positive + true_negative + false_positive + false_negative

    precision = true_positive / (true_positive + false_positive) if (true_positive + false_positive) > 0 else 0
    recall = true_positive / (true_positive + false_negative) if (true_positive + false_negative) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    agreement = (true_positive + true_negative) / total if total > 0 else 0
    specificity = true_negative / (true_negative + false_positive) if (true_negative + false_positive) > 0 else 0

    metrics = {
        "total_samples": total,
        "confusion_matrix": {
            "true_positive": true_positive,
            "true_negative": true_negative,
            "false_positive": false_positive,
            "false_negative": false_negative
        },
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "specificity": specificity,
        "agreement": agreement
    }

    return {
        "module": module,
        "judge_version": "v3" if use_v3 else ("v2" if use_v2 else "v1"),
        "metrics": metrics,
        "results": validation_results
    }


def print_summary(validation: dict):
    """Print validation summary."""
    metrics = validation["metrics"]
    cm = metrics["confusion_matrix"]

    print("=" * 60)
    print(f"JUDGE VALIDATION SUMMARY: {validation['module'].upper()} ({validation['judge_version']})")
    print("=" * 60)

    print("\nConfusion Matrix:")
    print(f"                    | Model CORRECT | Model WRONG |")
    print(f"  ------------------+---------------+-------------|")
    print(f"  Judge PASS        |      {cm['true_positive']:3d} (TP) |    {cm['false_positive']:3d} (FP) |")
    print(f"  Judge FAIL        |      {cm['false_negative']:3d} (FN) |    {cm['true_negative']:3d} (TN) |")

    print(f"\nMetrics:")
    print(f"  Precision:   {metrics['precision']:.1%}  (of PASS verdicts, how many correct)")
    print(f"  Recall:      {metrics['recall']:.1%}  (of correct outputs, how many PASS)")
    print(f"  F1 Score:    {metrics['f1']:.1%}")
    print(f"  Specificity: {metrics['specificity']:.1%}  (of wrong outputs, how many FAIL)")
    print(f"  Agreement:   {metrics['agreement']:.1%}  (overall judge accuracy)")

    print(f"\nInterpretation:")
    if metrics['agreement'] >= 0.9:
        print("  Excellent judge - highly accurate")
    elif metrics['agreement'] >= 0.8:
        print("  Good judge - mostly accurate")
    elif metrics['agreement'] >= 0.7:
        print("  Acceptable judge - some misalignment")
    else:
        print("  Poor judge - needs improvement")

    if cm['false_positive'] > cm['false_negative']:
        print("  Judge is TOO LENIENT (passes wrong outputs)")
    elif cm['false_negative'] > cm['false_positive']:
        print("  Judge is TOO STRICT (fails correct outputs)")


def main():
    parser = argparse.ArgumentParser(description="Validate LLM Judge accuracy against ground truth")
    parser.add_argument("--module", "-m", required=True, help="Module to validate")
    parser.add_argument("--results-file", "-r", required=True, help="Path to results JSONL file")
    parser.add_argument("--samples", "-n", type=int, default=50, help="Number of samples")
    parser.add_argument("--output", "-o", help="Output file for validation results")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--v2", action="store_true", help="Use v2 judge")
    parser.add_argument("--v3", action="store_true", help="Use v3 judge")
    args = parser.parse_args()

    results_file = Path(args.results_file)
    if not results_file.exists():
        print(f"Error: Results file not found: {results_file}")
        return

    validation = validate_judges(
        module=args.module,
        results_file=results_file,
        use_v2=args.v2,
        use_v3=args.v3,
        samples=args.samples,
        verbose=args.verbose
    )

    print_summary(validation)

    output_file = args.output or RESULTS_DIR / f"validation_{args.module}_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(validation, f, indent=2)

    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
