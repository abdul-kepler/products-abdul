#!/usr/bin/env python3
"""
Cohen's Kappa Calculator

Calculates inter-rater reliability between:
- Model predictions vs Ground Truth
- Path A vs Path B predictions
- Multiple models/annotators

Supports:
- Binary classification (OB/null, CB/null, NB/null)
- Multi-class classification (R/S/C/N)
- Weighted Kappa for ordinal data
"""

import json
import argparse
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class KappaResult:
    """Result of Kappa calculation."""
    kappa: float
    observed_agreement: float
    expected_agreement: float
    interpretation: str
    confusion_matrix: dict
    n_samples: int


def interpret_kappa(kappa: float) -> str:
    """Interpret Kappa value using Landis & Koch scale."""
    if kappa < 0:
        return "Poor (less than chance)"
    elif kappa < 0.20:
        return "Slight"
    elif kappa < 0.40:
        return "Fair"
    elif kappa < 0.60:
        return "Moderate"
    elif kappa < 0.80:
        return "Substantial"
    else:
        return "Almost Perfect"


def calculate_cohens_kappa(labels1: list, labels2: list) -> KappaResult:
    """
    Calculate Cohen's Kappa between two sets of labels.

    Args:
        labels1: First rater's labels
        labels2: Second rater's labels

    Returns:
        KappaResult with kappa value and statistics
    """
    if len(labels1) != len(labels2):
        raise ValueError(f"Label lists must have same length: {len(labels1)} vs {len(labels2)}")

    n = len(labels1)
    if n == 0:
        raise ValueError("Cannot calculate Kappa for empty label lists")

    # Get all unique labels
    all_labels = sorted(set(labels1) | set(labels2))

    # Build confusion matrix
    confusion = {l1: {l2: 0 for l2 in all_labels} for l1 in all_labels}
    for l1, l2 in zip(labels1, labels2):
        confusion[l1][l2] += 1

    # Calculate observed agreement (Po)
    observed_agreement = sum(confusion[l][l] for l in all_labels) / n

    # Calculate expected agreement (Pe)
    label_counts1 = Counter(labels1)
    label_counts2 = Counter(labels2)

    expected_agreement = sum(
        (label_counts1[l] / n) * (label_counts2[l] / n)
        for l in all_labels
    )

    # Calculate Kappa
    if expected_agreement == 1.0:
        kappa = 1.0  # Perfect agreement
    else:
        kappa = (observed_agreement - expected_agreement) / (1 - expected_agreement)

    return KappaResult(
        kappa=kappa,
        observed_agreement=observed_agreement,
        expected_agreement=expected_agreement,
        interpretation=interpret_kappa(kappa),
        confusion_matrix=confusion,
        n_samples=n
    )


def calculate_weighted_kappa(labels1: list, labels2: list,
                             weights: Optional[dict] = None) -> KappaResult:
    """
    Calculate weighted Cohen's Kappa for ordinal data.

    Uses quadratic weights by default.
    """
    if len(labels1) != len(labels2):
        raise ValueError("Label lists must have same length")

    n = len(labels1)
    all_labels = sorted(set(labels1) | set(labels2))
    k = len(all_labels)

    # Create label to index mapping
    label_to_idx = {l: i for i, l in enumerate(all_labels)}

    # Build weight matrix (quadratic weights by default)
    if weights is None:
        weights = {}
        for l1 in all_labels:
            for l2 in all_labels:
                i, j = label_to_idx[l1], label_to_idx[l2]
                # Quadratic weights
                weights[(l1, l2)] = 1 - ((i - j) ** 2) / ((k - 1) ** 2) if k > 1 else 1

    # Build confusion matrix
    confusion = {l1: {l2: 0 for l2 in all_labels} for l1 in all_labels}
    for l1, l2 in zip(labels1, labels2):
        confusion[l1][l2] += 1

    # Calculate weighted observed agreement
    weighted_observed = sum(
        weights.get((l1, l2), 0) * confusion[l1][l2]
        for l1 in all_labels
        for l2 in all_labels
    ) / n

    # Calculate weighted expected agreement
    label_counts1 = Counter(labels1)
    label_counts2 = Counter(labels2)

    weighted_expected = sum(
        weights.get((l1, l2), 0) * (label_counts1[l1] / n) * (label_counts2[l2] / n)
        for l1 in all_labels
        for l2 in all_labels
    )

    # Calculate weighted Kappa
    if weighted_expected == 1.0:
        kappa = 1.0
    else:
        kappa = (weighted_observed - weighted_expected) / (1 - weighted_expected)

    return KappaResult(
        kappa=kappa,
        observed_agreement=weighted_observed,
        expected_agreement=weighted_expected,
        interpretation=interpret_kappa(kappa),
        confusion_matrix=confusion,
        n_samples=n
    )


def load_predictions_from_results(results_file: str, label_field: str = "actual") -> dict:
    """
    Load predictions from batch results file.

    Returns dict mapping record_id to label.
    """
    predictions = {}

    with open(results_file) as f:
        for line in f:
            record = json.loads(line)
            custom_id = record.get("custom_id", "")

            # Parse response
            response = record.get("response", {})
            body = response.get("body", {})
            choices = body.get("choices", [])

            if choices:
                content = choices[0].get("message", {}).get("content", "")
                try:
                    parsed = json.loads(content)
                    label = parsed.get(label_field)
                    predictions[custom_id] = label
                except json.JSONDecodeError:
                    predictions[custom_id] = content.strip()

    return predictions


def load_ground_truth(dataset_file: str, label_field: str = "expected") -> dict:
    """
    Load ground truth labels from dataset.

    Returns dict mapping record_id to label.
    """
    ground_truth = {}

    with open(dataset_file) as f:
        for line in f:
            record = json.loads(line)
            record_id = record.get("custom_id", record.get("id", ""))
            label = record.get(label_field)
            ground_truth[record_id] = label

    return ground_truth


def compare_model_vs_ground_truth(results_file: str, dataset_file: str,
                                   pred_field: str, truth_field: str) -> KappaResult:
    """Compare model predictions against ground truth."""
    predictions = load_predictions_from_results(results_file, pred_field)
    ground_truth = load_ground_truth(dataset_file, truth_field)

    # Match by record ID
    common_ids = set(predictions.keys()) & set(ground_truth.keys())

    labels1 = [str(predictions[rid]) for rid in common_ids]
    labels2 = [str(ground_truth[rid]) for rid in common_ids]

    return calculate_cohens_kappa(labels1, labels2)


def compare_two_models(results_file1: str, results_file2: str,
                       pred_field: str = "actual") -> KappaResult:
    """Compare predictions from two different models/runs."""
    pred1 = load_predictions_from_results(results_file1, pred_field)
    pred2 = load_predictions_from_results(results_file2, pred_field)

    # Match by record ID
    common_ids = set(pred1.keys()) & set(pred2.keys())

    labels1 = [str(pred1[rid]) for rid in common_ids]
    labels2 = [str(pred2[rid]) for rid in common_ids]

    return calculate_cohens_kappa(labels1, labels2)


def format_confusion_matrix(confusion: dict) -> str:
    """Format confusion matrix as table."""
    labels = sorted(confusion.keys())

    # Header
    lines = []
    header = "Actual\\Pred | " + " | ".join(f"{l:>8}" for l in labels)
    lines.append(header)
    lines.append("-" * len(header))

    # Rows
    for l1 in labels:
        row = f"{l1:>10} | " + " | ".join(f"{confusion[l1][l2]:>8}" for l2 in labels)
        lines.append(row)

    return "\n".join(lines)


def generate_report(result: KappaResult, title: str = "Cohen's Kappa Analysis") -> str:
    """Generate markdown report."""
    report = []
    report.append(f"# {title}\n")
    report.append(f"**Samples:** {result.n_samples}\n")
    report.append(f"\n## Results\n")
    report.append(f"| Metric | Value |")
    report.append(f"|--------|-------|")
    report.append(f"| Cohen's Kappa | {result.kappa:.4f} |")
    report.append(f"| Interpretation | {result.interpretation} |")
    report.append(f"| Observed Agreement | {result.observed_agreement:.4f} |")
    report.append(f"| Expected Agreement | {result.expected_agreement:.4f} |")

    report.append(f"\n## Confusion Matrix\n")
    report.append("```")
    report.append(format_confusion_matrix(result.confusion_matrix))
    report.append("```")

    return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(description="Calculate Cohen's Kappa")
    parser.add_argument("--mode", "-m", choices=["model-vs-truth", "model-vs-model", "labels"],
                        required=True, help="Comparison mode")
    parser.add_argument("--results1", "-r1", help="First results file")
    parser.add_argument("--results2", "-r2", help="Second results file (for model-vs-model)")
    parser.add_argument("--dataset", "-d", help="Dataset file with ground truth")
    parser.add_argument("--labels1", help="JSON file with first label set")
    parser.add_argument("--labels2", help="JSON file with second label set")
    parser.add_argument("--pred-field", default="actual", help="Field name for predictions")
    parser.add_argument("--truth-field", default="expected", help="Field name for ground truth")
    parser.add_argument("--weighted", "-w", action="store_true", help="Use weighted Kappa")
    parser.add_argument("--output", "-o", help="Output file for report")

    args = parser.parse_args()

    if args.mode == "model-vs-truth":
        if not args.results1 or not args.dataset:
            parser.error("model-vs-truth requires --results1 and --dataset")
        result = compare_model_vs_ground_truth(
            args.results1, args.dataset, args.pred_field, args.truth_field
        )
        title = "Model vs Ground Truth"

    elif args.mode == "model-vs-model":
        if not args.results1 or not args.results2:
            parser.error("model-vs-model requires --results1 and --results2")
        result = compare_two_models(args.results1, args.results2, args.pred_field)
        title = "Model A vs Model B"

    elif args.mode == "labels":
        if not args.labels1 or not args.labels2:
            parser.error("labels mode requires --labels1 and --labels2")
        with open(args.labels1) as f:
            labels1 = json.load(f)
        with open(args.labels2) as f:
            labels2 = json.load(f)

        if args.weighted:
            result = calculate_weighted_kappa(labels1, labels2)
        else:
            result = calculate_cohens_kappa(labels1, labels2)
        title = "Label Comparison"

    # Print results
    print(f"\n{'='*60}")
    print(f"COHEN'S KAPPA ANALYSIS")
    print(f"{'='*60}")
    print(f"Samples: {result.n_samples}")
    print(f"Kappa: {result.kappa:.4f}")
    print(f"Interpretation: {result.interpretation}")
    print(f"Observed Agreement: {result.observed_agreement:.4f}")
    print(f"Expected Agreement: {result.expected_agreement:.4f}")
    print(f"\nConfusion Matrix:")
    print(format_confusion_matrix(result.confusion_matrix))

    if args.output:
        report = generate_report(result, title)
        with open(args.output, "w") as f:
            f.write(report)
        print(f"\nReport saved to: {args.output}")


if __name__ == "__main__":
    main()
