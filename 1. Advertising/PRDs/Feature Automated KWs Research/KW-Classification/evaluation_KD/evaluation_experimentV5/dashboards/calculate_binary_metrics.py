#!/usr/bin/env python3
"""
Calculate binary classification metrics from judge results.
Extracts TP/TN/FP/FN and calculates Accuracy, Precision, Recall, F1, MCC.
"""

import json
import math
from pathlib import Path
from collections import Counter

# Binary classifier modules
BINARY_MODULES = ['m02', 'm02b', 'm04', 'm04b', 'm05', 'm05b', 'm12', 'm12b', 'm13', 'm14', 'm15', 'm16']

def calculate_mcc(tp, tn, fp, fn):
    """Matthews Correlation Coefficient - best for imbalanced data."""
    numerator = (tp * tn) - (fp * fn)
    denominator = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    if denominator == 0:
        return 0
    return numerator / denominator

def is_positive(value):
    """Check if value represents a 'positive' classification."""
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        # Empty string = negative, any value = positive
        return bool(value.strip())
    return bool(value)

def get_record_key(ev):
    """Get unique key for a record (keyword or input hash)."""
    inp = ev.get('input', {})
    # Try keyword first (for classifiers)
    if 'keyword' in inp:
        return inp['keyword']
    # Fall back to string representation of input
    return str(sorted(inp.items()))

def analyze_judge_file(filepath):
    """Analyze a single judge results file."""
    with open(filepath) as f:
        data = json.load(f)

    evaluations = data.get('evaluations', [])
    if not evaluations:
        return None

    # Group by unique record key, only keep main classification rubric
    samples = {}
    for ev in evaluations:
        record_key = get_record_key(ev)
        rubric_id = ev.get('rubric_id', '').lower()

        # Only use classification rubric for metrics
        is_main_rubric = any(x in rubric_id for x in ['correct_classification', 'classification'])

        if is_main_rubric:
            samples[record_key] = ev

    tp = tn = fp = fn = 0
    details = {'tp': [], 'tn': [], 'fp': [], 'fn': []}

    for sample_id, ev in samples.items():
        expected = ev.get('expected', {})
        output = ev.get('output', {})

        # Find the classification field (first key in expected)
        if not expected:
            continue

        field = list(expected.keys())[0]
        exp_val = expected.get(field)
        out_val = output.get(field)

        exp_positive = is_positive(exp_val)
        out_positive = is_positive(out_val)

        if exp_positive and out_positive:
            # Check if values match (for multi-class)
            if isinstance(exp_val, str) and isinstance(out_val, str):
                if exp_val.lower() == out_val.lower():
                    tp += 1
                    details['tp'].append(sample_id)
                else:
                    fp += 1  # Wrong positive class
                    details['fp'].append(sample_id)
            else:
                tp += 1
                details['tp'].append(sample_id)
        elif not exp_positive and not out_positive:
            tn += 1
            details['tn'].append(sample_id)
        elif not exp_positive and out_positive:
            fp += 1
            details['fp'].append(sample_id)
        else:  # exp_positive and not out_positive
            fn += 1
            details['fn'].append(sample_id)

    return tp, tn, fp, fn, details

def calculate_metrics(tp, tn, fp, fn):
    """Calculate all metrics from confusion matrix."""
    total = tp + tn + fp + fn
    if total == 0:
        return None

    accuracy = (tp + tn) / total * 100
    precision = tp / (tp + fp) * 100 if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) * 100 if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    mcc = calculate_mcc(tp, tn, fp, fn)

    return {
        'tp': tp,
        'tn': tn,
        'fp': fp,
        'fn': fn,
        'total': total,
        'accuracy': round(accuracy, 1),
        'precision': round(precision, 1),
        'recall': round(recall, 1),
        'f1': round(f1, 1),
        'mcc': round(mcc, 3)
    }

def main():
    judge_dir = Path(__file__).parent.parent / 'judge_results'

    results = {}

    for module in BINARY_MODULES:
        # Find latest judge file for this module
        module_files = sorted(judge_dir.glob(f'{module}_judge_*.json'), reverse=True)

        if not module_files:
            print(f'{module}: No judge results found')
            continue

        latest_file = module_files[0]
        print(f'{module}: Analyzing {latest_file.name}')

        result = analyze_judge_file(latest_file)
        if result is None:
            print(f'  No data found')
            continue

        tp, tn, fp, fn, details = result
        metrics = calculate_metrics(tp, tn, fp, fn)

        if metrics:
            results[module] = metrics
            print(f'  TP={tp} TN={tn} FP={fp} FN={fn} (total={tp+tn+fp+fn})')
            print(f'  Accuracy={metrics["accuracy"]}% Precision={metrics["precision"]}% Recall={metrics["recall"]}%')
            print(f'  F1={metrics["f1"]}% MCC={metrics["mcc"]}')
        else:
            print(f'  Could not calculate metrics')

    # Output as JS
    print('\n// Add to modules_data.js:')
    print('const binaryMetrics = ' + json.dumps(results, indent=2) + ';')

    # Also write to file
    output_file = Path(__file__).parent / 'binary_metrics.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f'\nSaved to {output_file}')

    return results

if __name__ == '__main__':
    main()
