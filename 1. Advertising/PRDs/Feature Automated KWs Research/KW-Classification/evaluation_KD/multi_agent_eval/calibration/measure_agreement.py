#!/usr/bin/env python3
"""
Calibration: Measure agreement between LLM Judge and Human Labels.

Usage:
    python3 calibration/measure_agreement.py --human calibration/human_labels.csv --llm results/m11_multiagent_*.json
"""

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, List, Tuple


def load_human_labels(csv_path: str) -> Dict[str, dict]:
    """Load human labels from CSV."""
    labels = {}
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sample_id = row['sample_id']
            labels[sample_id] = {
                'overall': float(row['human_score']),
                'accuracy': int(row.get('human_accuracy', 0)),
                'completeness': int(row.get('human_completeness', 0)),
                'clarity': int(row.get('human_clarity', 0)),
                'relevance': int(row.get('human_relevance', 0)),
                'helpfulness': int(row.get('human_helpfulness', 0)),
                'notes': row.get('human_notes', ''),
            }
    return labels


def load_llm_scores(json_path: str) -> Dict[str, dict]:
    """Load LLM judge scores from results JSON."""
    with open(json_path, 'r') as f:
        data = json.load(f)

    scores = {}
    for result in data.get('results', []):
        sample_id = result['sample_id']
        r = result.get('result', {})
        scores[sample_id] = {
            'overall': r.get('overall', r.get('final_score', 0)),
            'accuracy': r.get('scores', {}).get('accuracy', 0),
            'completeness': r.get('scores', {}).get('completeness', 0),
            'clarity': r.get('scores', {}).get('clarity', 0),
            'relevance': r.get('scores', {}).get('relevance', 0),
            'helpfulness': r.get('scores', {}).get('reasoning', 0),  # Map reasoning to helpfulness
        }
    return scores


def calculate_agreement(human: Dict, llm: Dict, tolerance: int = 1) -> dict:
    """
    Calculate agreement metrics.

    Args:
        human: Human labels {sample_id: {scores}}
        llm: LLM scores {sample_id: {scores}}
        tolerance: Score difference allowed for "agreement" (default: 1)

    Returns:
        Agreement metrics
    """
    common_ids = set(human.keys()) & set(llm.keys())
    if not common_ids:
        return {"error": "No common samples found"}

    dimensions = ['overall', 'accuracy', 'completeness', 'clarity', 'relevance']
    results = {
        'total_samples': len(common_ids),
        'exact_agreement': {},
        'within_1_agreement': {},
        'mean_absolute_error': {},
        'correlation': {},
        'details': [],
    }

    for dim in dimensions:
        human_scores = [human[sid][dim] for sid in common_ids]
        llm_scores = [llm[sid][dim] for sid in common_ids]

        # Exact agreement
        exact = sum(1 for h, l in zip(human_scores, llm_scores) if h == l)
        results['exact_agreement'][dim] = round(exact / len(common_ids) * 100, 1)

        # Within tolerance agreement
        within_tol = sum(1 for h, l in zip(human_scores, llm_scores) if abs(h - l) <= tolerance)
        results['within_1_agreement'][dim] = round(within_tol / len(common_ids) * 100, 1)

        # Mean Absolute Error
        mae = sum(abs(h - l) for h, l in zip(human_scores, llm_scores)) / len(common_ids)
        results['mean_absolute_error'][dim] = round(mae, 2)

        # Pearson correlation (simplified)
        if len(set(human_scores)) > 1 and len(set(llm_scores)) > 1:
            mean_h = sum(human_scores) / len(human_scores)
            mean_l = sum(llm_scores) / len(llm_scores)
            num = sum((h - mean_h) * (l - mean_l) for h, l in zip(human_scores, llm_scores))
            den_h = sum((h - mean_h) ** 2 for h in human_scores) ** 0.5
            den_l = sum((l - mean_l) ** 2 for l in llm_scores) ** 0.5
            corr = num / (den_h * den_l) if den_h * den_l > 0 else 0
            results['correlation'][dim] = round(corr, 3)
        else:
            results['correlation'][dim] = "N/A"

    # Per-sample details
    for sid in sorted(common_ids):
        results['details'].append({
            'sample_id': sid,
            'human_overall': human[sid]['overall'],
            'llm_overall': llm[sid]['overall'],
            'diff': llm[sid]['overall'] - human[sid]['overall'],
            'human_notes': human[sid].get('notes', ''),
        })

    return results


def print_report(results: dict):
    """Print calibration report."""
    print("\n" + "=" * 60)
    print("CALIBRATION REPORT: Human vs LLM Agreement")
    print("=" * 60)

    print(f"\nSamples analyzed: {results['total_samples']}")

    print("\n--- Agreement Rates ---")
    print(f"{'Dimension':<15} {'Exact':<12} {'Within ±1':<12} {'MAE':<10} {'Correlation':<12}")
    print("-" * 60)

    for dim in ['overall', 'accuracy', 'completeness', 'clarity', 'relevance']:
        exact = results['exact_agreement'].get(dim, 0)
        within1 = results['within_1_agreement'].get(dim, 0)
        mae = results['mean_absolute_error'].get(dim, 0)
        corr = results['correlation'].get(dim, 'N/A')

        # Color coding for agreement
        status = "✅" if within1 >= 85 else "⚠️" if within1 >= 70 else "❌"
        print(f"{dim:<15} {exact:>5.1f}%      {within1:>5.1f}% {status}    {mae:<10.2f} {corr}")

    print("\n--- Per-Sample Analysis ---")
    for detail in results['details']:
        diff = detail['diff']
        status = "✓" if abs(diff) <= 1 else "⚠" if abs(diff) <= 2 else "✗"
        print(f"  {detail['sample_id']}: Human={detail['human_overall']}, LLM={detail['llm_overall']}, Diff={diff:+.1f} {status}")
        if detail['human_notes']:
            print(f"    Notes: {detail['human_notes']}")

    # Overall assessment
    overall_agreement = results['within_1_agreement'].get('overall', 0)
    print(f"\n{'=' * 60}")
    if overall_agreement >= 85:
        print(f"✅ CALIBRATED: {overall_agreement}% agreement (target: 85%)")
    elif overall_agreement >= 70:
        print(f"⚠️ NEEDS TUNING: {overall_agreement}% agreement (target: 85%)")
    else:
        print(f"❌ NOT CALIBRATED: {overall_agreement}% agreement (target: 85%)")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Measure Human vs LLM agreement")
    parser.add_argument('--human', required=True, help="Human labels CSV file")
    parser.add_argument('--llm', required=True, help="LLM results JSON file")
    parser.add_argument('--tolerance', type=int, default=1, help="Score tolerance for agreement")
    args = parser.parse_args()

    human_labels = load_human_labels(args.human)
    llm_scores = load_llm_scores(args.llm)

    results = calculate_agreement(human_labels, llm_scores, args.tolerance)
    print_report(results)


if __name__ == "__main__":
    main()
