#!/usr/bin/env python3
"""
Path A vs Path B Comparator

Compares results between Path A and Path B pipelines:
- M02 vs M02b (Own Brand classification)
- M04 vs M04b (Competitor Brand classification)
- M05 vs M05b (Non-Branded classification)

Analyzes:
- Agreement rate between paths
- Cases where only one path is correct
- Cohen's Kappa between paths
- Per-case comparison for debugging
"""

import json
import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from .cohens_kappa import calculate_cohens_kappa, KappaResult
except ImportError:
    from cohens_kappa import calculate_cohens_kappa, KappaResult


# Path mappings
PATH_PAIRS = {
    "own_brand": {
        "path_a": "m02",
        "path_b": "m02b",
        "label_a": "own_brand",
        "label_b": "branding_scope_1",
        "description": "Own Brand Classification"
    },
    "competitor_brand": {
        "path_a": "m04",
        "path_b": "m04b",
        "label_a": "competitor_brand",
        "label_b": "branding_scope_2",
        "description": "Competitor Brand Classification"
    },
    "non_branded": {
        "path_a": "m05",
        "path_b": "m05b",
        "label_a": "non_branded",
        "label_b": "branding_scope_3",
        "description": "Non-Branded Classification"
    }
}


@dataclass
class ComparisonResult:
    """Result of path comparison."""
    task_name: str
    total_cases: int
    both_correct: int
    both_wrong: int
    only_a_correct: int
    only_b_correct: int
    agreement_rate: float
    kappa: Optional[KappaResult]
    disagreement_cases: list[dict]


def load_results(results_file: str) -> dict:
    """Load batch results, keyed by custom_id."""
    results = {}
    with open(results_file) as f:
        for line in f:
            record = json.loads(line)
            custom_id = record.get("custom_id", "")

            response = record.get("response", {})
            body = response.get("body", {})
            choices = body.get("choices", [])

            if choices:
                content = choices[0].get("message", {}).get("content", "")
                try:
                    parsed = json.loads(content)
                    results[custom_id] = parsed
                except json.JSONDecodeError:
                    results[custom_id] = {"raw": content}

    return results


def load_dataset(dataset_file: str) -> dict:
    """Load dataset with ground truth labels."""
    dataset = {}
    with open(dataset_file) as f:
        for line in f:
            record = json.loads(line)
            # Extract keyword from custom_id for matching
            custom_id = record.get("custom_id", "")
            keyword = record.get("keyword", "")
            dataset[custom_id] = record
            # Also index by keyword for cross-path matching
            if keyword:
                dataset[f"keyword:{keyword.lower()}"] = record
    return dataset


def normalize_label(label) -> str:
    """Normalize label for comparison."""
    if label is None:
        return "null"
    return str(label).strip().upper()


def extract_keyword_from_id(custom_id: str) -> str:
    """Extract keyword from custom_id format."""
    # Format: module_keyword or module_asin_keyword
    parts = custom_id.split("_", 2)
    if len(parts) >= 2:
        return parts[-1].lower()
    return custom_id.lower()


def compare_paths(
    results_a_file: str,
    results_b_file: str,
    dataset_a_file: str,
    dataset_b_file: str,
    label_field_a: str,
    label_field_b: str,
    task_name: str
) -> ComparisonResult:
    """Compare Path A and Path B results."""

    # Load all data
    results_a = load_results(results_a_file)
    results_b = load_results(results_b_file)
    dataset_a = load_dataset(dataset_a_file)
    dataset_b = load_dataset(dataset_b_file)

    print(f"Path A: {len(results_a)} results")
    print(f"Path B: {len(results_b)} results")

    # Match records by keyword
    keyword_to_a = {}
    keyword_to_b = {}

    for custom_id, output in results_a.items():
        keyword = extract_keyword_from_id(custom_id)
        keyword_to_a[keyword] = {
            "custom_id": custom_id,
            "output": output,
            "dataset": dataset_a.get(custom_id, {})
        }

    for custom_id, output in results_b.items():
        keyword = extract_keyword_from_id(custom_id)
        keyword_to_b[keyword] = {
            "custom_id": custom_id,
            "output": output,
            "dataset": dataset_b.get(custom_id, {})
        }

    # Find common keywords
    common_keywords = set(keyword_to_a.keys()) & set(keyword_to_b.keys())
    print(f"Common keywords: {len(common_keywords)}")

    # Compare
    both_correct = 0
    both_wrong = 0
    only_a_correct = 0
    only_b_correct = 0
    disagreement_cases = []

    labels_a = []
    labels_b = []

    for keyword in common_keywords:
        data_a = keyword_to_a[keyword]
        data_b = keyword_to_b[keyword]

        # Get ground truth
        gt_a = data_a["dataset"].get(label_field_a)
        gt_b = data_b["dataset"].get(label_field_b)

        # Get predictions
        pred_a = data_a["output"].get(label_field_a)
        pred_b = data_b["output"].get(label_field_b)

        # Normalize for comparison
        gt_norm = normalize_label(gt_a)  # Should be same for both
        pred_a_norm = normalize_label(pred_a)
        pred_b_norm = normalize_label(pred_b)

        # Track for Kappa
        labels_a.append(pred_a_norm)
        labels_b.append(pred_b_norm)

        # Check correctness
        a_correct = pred_a_norm == gt_norm
        b_correct = pred_b_norm == gt_norm

        if a_correct and b_correct:
            both_correct += 1
        elif not a_correct and not b_correct:
            both_wrong += 1
            disagreement_cases.append({
                "keyword": keyword,
                "ground_truth": gt_norm,
                "path_a": pred_a_norm,
                "path_b": pred_b_norm,
                "type": "both_wrong"
            })
        elif a_correct:
            only_a_correct += 1
            disagreement_cases.append({
                "keyword": keyword,
                "ground_truth": gt_norm,
                "path_a": pred_a_norm,
                "path_b": pred_b_norm,
                "type": "only_a_correct"
            })
        else:
            only_b_correct += 1
            disagreement_cases.append({
                "keyword": keyword,
                "ground_truth": gt_norm,
                "path_a": pred_a_norm,
                "path_b": pred_b_norm,
                "type": "only_b_correct"
            })

    total = len(common_keywords)
    agreement_rate = (both_correct + both_wrong) / total if total > 0 else 0

    # Calculate Kappa
    kappa = None
    if labels_a and labels_b:
        try:
            kappa = calculate_cohens_kappa(labels_a, labels_b)
        except Exception as e:
            print(f"Warning: Could not calculate Kappa: {e}")

    return ComparisonResult(
        task_name=task_name,
        total_cases=total,
        both_correct=both_correct,
        both_wrong=both_wrong,
        only_a_correct=only_a_correct,
        only_b_correct=only_b_correct,
        agreement_rate=agreement_rate,
        kappa=kappa,
        disagreement_cases=disagreement_cases
    )


def generate_report(result: ComparisonResult) -> str:
    """Generate markdown comparison report."""
    report = []
    report.append(f"# Path A vs Path B: {result.task_name}\n")
    report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    report.append(f"**Total Cases:** {result.total_cases}\n")

    # Summary table
    report.append("\n## Agreement Summary\n")
    report.append("| Category | Count | Percentage |")
    report.append("|----------|-------|------------|")

    pct = lambda x: f"{x/result.total_cases*100:.1f}%" if result.total_cases > 0 else "N/A"
    report.append(f"| Both Correct | {result.both_correct} | {pct(result.both_correct)} |")
    report.append(f"| Both Wrong | {result.both_wrong} | {pct(result.both_wrong)} |")
    report.append(f"| Only Path A Correct | {result.only_a_correct} | {pct(result.only_a_correct)} |")
    report.append(f"| Only Path B Correct | {result.only_b_correct} | {pct(result.only_b_correct)} |")

    # Accuracy comparison
    report.append("\n## Accuracy Comparison\n")
    acc_a = (result.both_correct + result.only_a_correct) / result.total_cases if result.total_cases > 0 else 0
    acc_b = (result.both_correct + result.only_b_correct) / result.total_cases if result.total_cases > 0 else 0
    report.append(f"- **Path A Accuracy:** {acc_a:.1%}")
    report.append(f"- **Path B Accuracy:** {acc_b:.1%}")
    report.append(f"- **Agreement Rate:** {result.agreement_rate:.1%}")

    # Kappa
    if result.kappa:
        report.append("\n## Inter-Path Agreement (Cohen's Kappa)\n")
        report.append(f"- **Kappa:** {result.kappa.kappa:.4f}")
        report.append(f"- **Interpretation:** {result.kappa.interpretation}")

    # Disagreement analysis
    if result.disagreement_cases:
        report.append("\n## Disagreement Analysis\n")

        # Group by type
        by_type = defaultdict(list)
        for case in result.disagreement_cases:
            by_type[case["type"]].append(case)

        if by_type["only_a_correct"]:
            report.append("\n### Cases Where Only Path A is Correct\n")
            report.append("| Keyword | Ground Truth | Path A | Path B |")
            report.append("|---------|--------------|--------|--------|")
            for case in by_type["only_a_correct"][:10]:
                report.append(f"| `{case['keyword'][:30]}` | {case['ground_truth']} | {case['path_a']} | {case['path_b']} |")
            if len(by_type["only_a_correct"]) > 10:
                report.append(f"\n*...and {len(by_type['only_a_correct'])-10} more*\n")

        if by_type["only_b_correct"]:
            report.append("\n### Cases Where Only Path B is Correct\n")
            report.append("| Keyword | Ground Truth | Path A | Path B |")
            report.append("|---------|--------------|--------|--------|")
            for case in by_type["only_b_correct"][:10]:
                report.append(f"| `{case['keyword'][:30]}` | {case['ground_truth']} | {case['path_a']} | {case['path_b']} |")
            if len(by_type["only_b_correct"]) > 10:
                report.append(f"\n*...and {len(by_type['only_b_correct'])-10} more*\n")

        if by_type["both_wrong"]:
            report.append("\n### Cases Where Both Paths are Wrong\n")
            report.append("| Keyword | Ground Truth | Path A | Path B |")
            report.append("|---------|--------------|--------|--------|")
            for case in by_type["both_wrong"][:10]:
                report.append(f"| `{case['keyword'][:30]}` | {case['ground_truth']} | {case['path_a']} | {case['path_b']} |")
            if len(by_type["both_wrong"]) > 10:
                report.append(f"\n*...and {len(by_type['both_wrong'])-10} more*\n")

    # Recommendations
    report.append("\n## Recommendations\n")
    if result.only_a_correct > result.only_b_correct * 1.5:
        report.append("- Path A significantly outperforms Path B. Consider investigating Path B prompt/schema.")
    elif result.only_b_correct > result.only_a_correct * 1.5:
        report.append("- Path B significantly outperforms Path A. Consider adopting Path B approach.")
    else:
        report.append("- Both paths perform similarly. May benefit from ensemble approach.")

    if result.both_wrong > 0.1 * result.total_cases:
        report.append(f"- {result.both_wrong} cases ({result.both_wrong/result.total_cases*100:.1f}%) wrong on both paths - review these for labeling issues or hard cases.")

    return "\n".join(report)


def compare_batch_directory(batch_dir: str, output_dir: str = None) -> dict:
    """Compare all Path A vs Path B pairs in batch directory."""

    batch_path = Path(batch_dir)
    results = {}

    if output_dir is None:
        output_dir = str(batch_path / "path_comparison")
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for task_name, config in PATH_PAIRS.items():
        path_a = config["path_a"]
        path_b = config["path_b"]

        results_a = batch_path / f"{path_a}_results.jsonl"
        results_b = batch_path / f"{path_b}_results.jsonl"
        dataset_a = batch_path / f"{path_a}_batch.jsonl"
        dataset_b = batch_path / f"{path_b}_batch.jsonl"

        # Check if files exist
        if not results_a.exists() or not results_b.exists():
            print(f"Skipping {task_name}: results files not found")
            continue

        if not dataset_a.exists():
            dataset_a = Path(f"datasets/{path_a}_dataset.jsonl")
        if not dataset_b.exists():
            dataset_b = Path(f"datasets/{path_b}_dataset.jsonl")

        print(f"\n{'='*60}")
        print(f"Comparing {task_name.upper()}: {path_a} vs {path_b}")
        print(f"{'='*60}")

        result = compare_paths(
            results_a_file=str(results_a),
            results_b_file=str(results_b),
            dataset_a_file=str(dataset_a),
            dataset_b_file=str(dataset_b),
            label_field_a=config["label_a"],
            label_field_b=config["label_b"],
            task_name=config["description"]
        )

        results[task_name] = result

        # Generate and save report
        report = generate_report(result)
        report_file = output_path / f"{task_name}_comparison.md"
        with open(report_file, "w") as f:
            f.write(report)
        print(f"Report saved: {report_file}")

        # Save JSON
        json_file = output_path / f"{task_name}_comparison.json"
        with open(json_file, "w") as f:
            json.dump({
                "task": task_name,
                "total_cases": result.total_cases,
                "both_correct": result.both_correct,
                "both_wrong": result.both_wrong,
                "only_a_correct": result.only_a_correct,
                "only_b_correct": result.only_b_correct,
                "agreement_rate": result.agreement_rate,
                "kappa": result.kappa.kappa if result.kappa else None,
                "disagreement_cases": result.disagreement_cases
            }, f, indent=2)

    return results


def main():
    parser = argparse.ArgumentParser(description="Compare Path A vs Path B results")
    parser.add_argument("--batch-dir", "-b", help="Batch directory with results")
    parser.add_argument("--task", "-t", choices=list(PATH_PAIRS.keys()),
                        help="Specific task to compare")
    parser.add_argument("--results-a", help="Path A results file")
    parser.add_argument("--results-b", help="Path B results file")
    parser.add_argument("--dataset-a", help="Path A dataset file")
    parser.add_argument("--dataset-b", help="Path B dataset file")
    parser.add_argument("--output", "-o", help="Output directory")

    args = parser.parse_args()

    if args.batch_dir:
        results = compare_batch_directory(args.batch_dir, args.output)

        # Print summary
        print(f"\n{'='*60}")
        print("COMPARISON SUMMARY")
        print(f"{'='*60}")
        for task_name, result in results.items():
            acc_a = (result.both_correct + result.only_a_correct) / result.total_cases if result.total_cases > 0 else 0
            acc_b = (result.both_correct + result.only_b_correct) / result.total_cases if result.total_cases > 0 else 0
            winner = "A" if acc_a > acc_b else "B" if acc_b > acc_a else "TIE"
            print(f"  {task_name}: Path A {acc_a:.1%} vs Path B {acc_b:.1%} [{winner}]")

    elif args.results_a and args.results_b and args.task:
        config = PATH_PAIRS[args.task]
        result = compare_paths(
            results_a_file=args.results_a,
            results_b_file=args.results_b,
            dataset_a_file=args.dataset_a or f"datasets/{config['path_a']}_dataset.jsonl",
            dataset_b_file=args.dataset_b or f"datasets/{config['path_b']}_dataset.jsonl",
            label_field_a=config["label_a"],
            label_field_b=config["label_b"],
            task_name=config["description"]
        )
        print(generate_report(result))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
