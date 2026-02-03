#!/usr/bin/env python3
"""
Score multi-class classifiers (M12B Combined Classification).
Calculates accuracy, per-class F1, macro F1, and confusion matrix.
"""

import csv
import json
import glob
import re
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
RESULTS_DIR = SCRIPT_DIR.parent.parent / "experiment_results"
DASHBOARDS_DIR = SCRIPT_DIR.parent / "dashboards"

# M12B classes
CLASSES = ['R', 'N', 'S', 'C']
CLASS_NAMES = {
    'R': 'Relevant',
    'N': 'Not Relevant',
    'S': 'Substitute',
    'C': 'Complementary'
}


def extract_experiment_info(csv_path: Path) -> dict:
    """Extract model info from filename or meta.json."""
    meta_path = csv_path.with_suffix('.meta.json')
    info = {
        'source_file': csv_path.name,
        'model': 'unknown',
        'prompt_version': 'v1',
    }

    if meta_path.exists():
        try:
            with open(meta_path) as f:
                meta = json.load(f)
            info['model'] = meta.get('model') or 'unknown'
        except:
            pass

    # Fallback to filename
    if info['model'] == 'unknown':
        filename = csv_path.stem.lower()
        model_patterns = [
            (r'gemini[-_]?2\.?0[-_]?flash', 'gemini-2.0-flash'),
            (r'gemini20flash', 'gemini-2.0-flash'),
            (r'gpt[-_]?4o[-_]?mini', 'gpt-4o-mini'),
            (r'gpt4omini', 'gpt-4o-mini'),
            (r'gpt[-_]?5', 'gpt-5'),
            (r'gpt5', 'gpt-5'),
            (r'claude', 'claude-sonnet-4'),
        ]
        for pattern, model_name in model_patterns:
            if re.search(pattern, filename):
                info['model'] = model_name
                break

    return info


def calculate_per_class_metrics(confusion: dict, cls: str) -> dict:
    """Calculate precision, recall, F1 for one class (one-vs-all)."""
    tp = confusion.get((cls, cls), 0)
    fp = sum(confusion.get((other, cls), 0) for other in CLASSES if other != cls)
    fn = sum(confusion.get((cls, other), 0) for other in CLASSES if other != cls)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    return {
        'tp': tp,
        'fp': fp,
        'fn': fn,
        'precision': round(precision * 100, 1),
        'recall': round(recall * 100, 1),
        'f1': round(f1 * 100, 1),
    }


def score_csv(csv_path: Path) -> dict:
    """Score a single M12B CSV file."""
    confusion = defaultdict(int)  # (expected, actual) -> count
    seen_inputs = set()
    total = 0
    correct = 0

    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Dedup
            input_val = row.get('input', '')
            if input_val in seen_inputs:
                continue
            seen_inputs.add(input_val)

            try:
                exp_data = json.loads(row.get('expected', '{}'))
                act_data = json.loads(row.get('output', '{}'))

                exp_val = exp_data.get('relevancy')
                act_val = act_data.get('relevancy')

                if exp_val not in CLASSES or act_val not in CLASSES:
                    continue

                confusion[(exp_val, act_val)] += 1
                total += 1

                if exp_val == act_val:
                    correct += 1

            except:
                continue

    if total == 0:
        return None

    # Overall accuracy
    accuracy = correct / total * 100

    # Per-class metrics
    per_class = {}
    f1_scores = []
    for cls in CLASSES:
        metrics = calculate_per_class_metrics(confusion, cls)
        per_class[cls] = metrics
        f1_scores.append(metrics['f1'])

    # Macro F1 (average of per-class F1)
    macro_f1 = sum(f1_scores) / len(f1_scores)

    # Build confusion matrix as nested dict for JSON
    conf_matrix = {}
    for exp_cls in CLASSES:
        conf_matrix[exp_cls] = {}
        for act_cls in CLASSES:
            conf_matrix[exp_cls][act_cls] = confusion.get((exp_cls, act_cls), 0)

    # Class distribution
    expected_dist = {cls: sum(confusion.get((cls, act), 0) for act in CLASSES) for cls in CLASSES}
    actual_dist = {cls: sum(confusion.get((exp, cls), 0) for exp in CLASSES) for cls in CLASSES}

    return {
        'total': total,
        'correct': correct,
        'accuracy': round(accuracy, 1),
        'macro_f1': round(macro_f1, 1),
        'per_class': per_class,
        'confusion_matrix': conf_matrix,
        'expected_distribution': expected_dist,
        'actual_distribution': actual_dist,
    }


def main():
    print("=" * 60)
    print("M12B Multi-Class Scoring")
    print("=" * 60)

    # Find all M12B CSV files
    m12b_dir = RESULTS_DIR / "M12B_CombinedClassification"
    if not m12b_dir.exists():
        print(f"Directory not found: {m12b_dir}")
        return

    csv_files = sorted(m12b_dir.glob("*.csv"), key=lambda f: f.stat().st_mtime, reverse=True)
    print(f"Found {len(csv_files)} CSV files\n")

    all_results = {}

    for csv_file in csv_files:
        info = extract_experiment_info(csv_file)
        model = info['model']

        print(f"\n{model}: {csv_file.name}")

        metrics = score_csv(csv_file)
        if not metrics:
            print("  No valid records")
            continue

        metrics['model'] = model
        metrics['source_file'] = info['source_file']

        # Use model as key (latest file wins)
        all_results[model] = metrics

        # Print summary
        print(f"  Total: {metrics['total']}, Accuracy: {metrics['accuracy']:.1f}%, Macro F1: {metrics['macro_f1']:.1f}%")
        print(f"  Per-class F1: R={metrics['per_class']['R']['f1']:.1f}%, N={metrics['per_class']['N']['f1']:.1f}%, S={metrics['per_class']['S']['f1']:.1f}%, C={metrics['per_class']['C']['f1']:.1f}%")

    # Summary table
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"{'Model':<20} {'N':>5} {'Acc':>7} {'MacroF1':>8} {'R-F1':>6} {'N-F1':>6} {'S-F1':>6} {'C-F1':>6}")
    print("-" * 60)

    for model in sorted(all_results.keys()):
        r = all_results[model]
        pc = r['per_class']
        print(f"{model:<20} {r['total']:>5} {r['accuracy']:>6.1f}% {r['macro_f1']:>7.1f}% {pc['R']['f1']:>5.1f}% {pc['N']['f1']:>5.1f}% {pc['S']['f1']:>5.1f}% {pc['C']['f1']:>5.1f}%")

    # Save to JS file
    js_content = f"""/**
 * M12B Multi-class metrics data
 * Auto-generated by score_multiclass.py
 * Generated: {datetime.now().isoformat()}
 */

const m12bMetricsData = {{
  classes: {json.dumps(CLASSES)},
  classNames: {json.dumps(CLASS_NAMES)},
  results: {json.dumps(all_results, indent=2)}
}};
"""

    output_file = DASHBOARDS_DIR / "m12b_metrics_data.js"
    with open(output_file, 'w') as f:
        f.write(js_content)

    print(f"\nSaved to: {output_file}")

    return all_results


if __name__ == "__main__":
    main()
