#!/usr/bin/env python3
"""
Score binary classifiers directly from CSV results.
No LLM judge needed - just compare expected vs actual values.

Usage:
    python score_binary_classifiers.py          # Score all binary modules
    python score_binary_classifiers.py m02      # Score specific module
"""

import csv
import json
import math
import sys
from pathlib import Path

# Binary classifier module configs
# Note: Some modules have different field names in expected vs output
# Labels explain what TP/TN/FP/FN mean for each module
BINARY_MODULES = {
    'm02': {
        'name': 'Classify Own Brand Keywords',
        'folder': 'M02_ClassifyOwnBrandKeywords',
        'json_field': 'branding_scope_1',
        'labels': {'tp': 'OB', 'tn': 'Null', 'fp': 'Null→OB', 'fn': 'OB→Null'},
    },
    'm02b': {
        'name': 'Classify Own Brand (Path B)',
        'folder': 'M02B_ClassifyOwnBrandKeywords_PathB',
        'json_field': 'branding_scope_1',
        'labels': {'tp': 'OB', 'tn': 'Null', 'fp': 'Null→OB', 'fn': 'OB→Null'},
    },
    'm04': {
        'name': 'Classify Competitor Keywords',
        'folder': 'M04_ClassifyCompetitorBrandKeywords',
        'json_field': 'branding_scope_2',
        'labels': {'tp': 'CB', 'tn': 'Null', 'fp': 'Null→CB', 'fn': 'CB→Null'},
    },
    'm04b': {
        'name': 'Classify Competitor (Path B)',
        'folder': 'M04B_ClassifyCompetitorBrandKeywords_PathB',
        'json_field': 'branding_scope_2',
        'labels': {'tp': 'CB', 'tn': 'Null', 'fp': 'Null→CB', 'fn': 'CB→Null'},
    },
    'm05': {
        'name': 'Classify Non-Branded Keywords',
        'folder': 'M05_ClassifyNonBrandedKeywords',
        'json_field': 'branding_scope_3',
        'labels': {'tp': 'NB', 'tn': 'Branded', 'fp': 'Brand→NB', 'fn': 'NB→Brand'},
    },
    'm05b': {
        'name': 'Classify Non-Branded (Path B)',
        'folder': 'M05B_ClassifyNonBrandedKeywords_PathB',
        'json_field': 'branding_scope_3',
        'labels': {'tp': 'NB', 'tn': 'Branded', 'fp': 'Brand→NB', 'fn': 'NB→Brand'},
    },
    'm12': {
        'name': 'Hard Constraint Violation Check',
        'folder': 'M12_HardConstraintViolationCheck',
        'expected_field': 'relevancy',  # N means violation expected
        'output_field': 'violates_constraint',  # True/False
        'positive_expected': 'N',  # Expected=N means positive (violation)
        'positive_output': True,  # Output=True means positive (violation)
        'null_is_negative': True,  # Expected=null means negative (no violation)
        'labels': {'tp': 'Violates', 'tn': 'OK', 'fp': 'OK→Violates', 'fn': 'Violates→OK'},
    },
    'm13': {
        'name': 'Product Type Check',
        'folder': 'M13_ProductTypeCheck',
        'expected_field': 'same_type',
        'output_field': 'same_product_type',
        'labels': {'tp': 'Match', 'tn': 'Diff', 'fp': 'Diff→Match', 'fn': 'Match→Diff'},
    },
    'm14': {
        'name': 'Primary Use Check (Relevancy)',
        'folder': 'M14_PrimaryUseCheckSameType',
        'json_field': 'relevancy',
        'labels': {'tp': 'R', 'tn': '-', 'fp': '-', 'fn': 'R→Other'},
        'note': 'All expected=R',
    },
    'm15': {
        'name': 'Substitute Check (Relevancy)',
        'folder': 'M15_SubstituteCheck',
        'json_field': 'relevancy',
        'positive_expected': 'S',  # Expected=S means positive
        'positive_output': 'S',  # Output=S means positive
        'null_is_negative': True,  # Expected=null means negative (not a substitute)
        'labels': {'tp': 'S', 'tn': 'not-S', 'fp': 'null→S', 'fn': 'S→not-S'},
    },
    'm16': {
        'name': 'Complementary Check (Relevancy)',
        'folder': 'M16_ComplementaryCheck',
        'json_field': 'relevancy',
        'labels': {'tp': 'C', 'tn': '-', 'fp': '-', 'fn': 'C→N'},
        'note': 'Expected=C, outputs C or N',
    },
}

def calculate_mcc(tp, tn, fp, fn):
    """Matthews Correlation Coefficient."""
    numerator = (tp * tn) - (fp * fn)
    denominator = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    if denominator == 0:
        return 0
    return numerator / denominator

def is_positive(value):
    """Check if value is positive (non-null, non-empty)."""
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        value = value.strip().lower()
        if not value or value in ('null', 'none', '', 'false', '0'):
            return False
        return True
    return bool(value)

def parse_json_field(json_str, field_name):
    """Parse JSON string and extract field value."""
    if not json_str:
        return None
    try:
        data = json.loads(json_str)
        return data.get(field_name)
    except (json.JSONDecodeError, TypeError):
        return None

def find_csv_files(folder_path):
    """Find all CSV files in folder."""
    return sorted(folder_path.glob('*.csv'), key=lambda f: f.stat().st_mtime, reverse=True)

def count_output_distribution(csv_path, config):
    """Count output distribution when no ground truth available."""
    out_field = config.get('output_field') or config.get('json_field')
    positive = 0
    negative = 0
    total = 0

    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += 1
            if 'output' in row:
                out_val = parse_json_field(row.get('output'), out_field)
                if is_positive(out_val):
                    positive += 1
                else:
                    negative += 1

    return {
        'tp': positive,  # Output positive (no ground truth to verify)
        'tn': negative,  # Output negative (no ground truth to verify)
        'fp': 0,
        'fn': 0,
        'total': total,
        'accuracy': None,
        'precision': None,
        'recall': None,
        'f1': None,
        'mcc': None,
        'skipped': 0,
        'output_positive': positive,
        'output_negative': negative,
    }, None

def score_csv(csv_path, config):
    """Score a single CSV file."""
    tp = tn = fp = fn = 0
    skipped = 0
    skip_none = config.get('skip_none_expected', False)
    null_is_negative = config.get('null_is_negative', False)
    positive_expected = config.get('positive_expected')  # e.g., 'N', 'S'
    positive_output = config.get('positive_output')  # e.g., True, 'S'

    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []

        for i, row in enumerate(reader):
            try:
                # Get field names - may be different for expected vs output
                exp_field = config.get('expected_field') or config.get('json_field')
                out_field = config.get('output_field') or config.get('json_field')

                # Parse JSON columns
                if 'output' in row and 'expected' in row:
                    exp_val = parse_json_field(row.get('expected'), exp_field)
                    act_val = parse_json_field(row.get('output'), out_field)
                else:
                    skipped += 1
                    continue

                # Skip records with None expected if configured (and not treating null as negative)
                if skip_none and exp_val is None and not null_is_negative:
                    skipped += 1
                    continue

                # Determine if expected/actual are positive
                if positive_expected is not None:
                    # Use specific value comparison
                    exp_pos = (exp_val == positive_expected)
                elif null_is_negative and exp_val is None:
                    exp_pos = False
                else:
                    exp_pos = is_positive(exp_val)

                if positive_output is not None:
                    # Use specific value comparison
                    act_pos = (act_val == positive_output)
                else:
                    act_pos = is_positive(act_val)

                # Classification - with string match check for same-type comparison
                if exp_pos and act_pos:
                    # Both positive - for strings, also check exact match
                    if isinstance(exp_val, str) and isinstance(act_val, str):
                        if exp_val.lower().strip() == act_val.lower().strip():
                            tp += 1
                        else:
                            fn += 1  # Different positive values = FN
                    else:
                        tp += 1
                elif not exp_pos and not act_pos:
                    tn += 1
                elif not exp_pos and act_pos:
                    fp += 1
                else:  # exp_pos and not act_pos
                    fn += 1

            except Exception as e:
                skipped += 1

    total = tp + tn + fp + fn
    if total == 0:
        return None, f"No records processed (skipped: {skipped})"

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
        'mcc': round(mcc, 3),
        'skipped': skipped
    }, None

def main():
    results_dir = Path(__file__).parent.parent.parent.parent / 'experiment_results'

    modules_to_score = sys.argv[1:] if len(sys.argv) > 1 else list(BINARY_MODULES.keys())

    all_results = {}

    for module_id in modules_to_score:
        if module_id not in BINARY_MODULES:
            print(f'{module_id}: Unknown module, skipping')
            continue

        config = BINARY_MODULES[module_id]
        folder = results_dir / config['folder']

        if not folder.exists():
            print(f'{module_id}: Folder not found: {folder}')
            continue

        csv_files = find_csv_files(folder)
        if not csv_files:
            print(f'{module_id}: No CSV files found')
            continue

        # Use the latest CSV file
        latest_csv = csv_files[0]
        print(f'\n{module_id.upper()}: {config["name"]}')
        print(f'  File: {latest_csv.name}')

        # Check if module has no ground truth
        if config.get('no_ground_truth'):
            metrics, error = count_output_distribution(latest_csv, config)
        else:
            metrics, error = score_csv(latest_csv, config)

        if error:
            print(f'  ERROR: {error}')
            continue

        # Add labels and notes to metrics
        if 'labels' in config:
            metrics['labels'] = config['labels']
        if 'note' in config:
            metrics['note'] = config['note']
        if 'total_records' in config:
            metrics['total_records'] = config['total_records']

        all_results[module_id] = metrics

        # Get labels for display
        labels = config.get('labels', {})
        tp_lbl = f"({labels.get('tp', '')})" if labels.get('tp') else ""
        tn_lbl = f"({labels.get('tn', '')})" if labels.get('tn') else ""
        fp_lbl = f"({labels.get('fp', '')})" if labels.get('fp') else ""
        fn_lbl = f"({labels.get('fn', '')})" if labels.get('fn') else ""

        print(f'  Records: {metrics["total"]} (skipped: {metrics["skipped"]})')

        # Different display for modules without ground truth
        if config.get('no_ground_truth'):
            print(f'  Output Distribution (NO GROUND TRUTH):')
            print(f'    Positive{tp_lbl}={metrics["output_positive"]:4d}')
            print(f'    Negative{tn_lbl}={metrics["output_negative"]:4d}')
            print(f'  Metrics: N/A (no ground truth to calculate)')
        else:
            print(f'  Confusion Matrix:')
            print(f'    TP{tp_lbl}={metrics["tp"]:4d}  FP{fp_lbl}={metrics["fp"]:4d}')
            print(f'    FN{fn_lbl}={metrics["fn"]:4d}  TN{tn_lbl}={metrics["tn"]:4d}')
            print(f'  Metrics:')
            print(f'    Accuracy:  {metrics["accuracy"]:5.1f}%')
            print(f'    Precision: {metrics["precision"]:5.1f}%')
            print(f'    Recall:    {metrics["recall"]:5.1f}%')
            print(f'    F1 Score:  {metrics["f1"]:5.1f}%')
            print(f'    MCC:       {metrics["mcc"]:+.3f}')

    # Output summary
    print('\n' + '='*60)
    print('SUMMARY')
    print('='*60)
    for m, r in sorted(all_results.items()):
        if r.get('accuracy') is not None:
            print(f'{m:6s}: Acc={r["accuracy"]:5.1f}%  F1={r["f1"]:5.1f}%  MCC={r["mcc"]:+.3f}  (n={r["total"]})')
        else:
            print(f'{m:6s}: Output: +{r.get("output_positive", 0)} / -{r.get("output_negative", 0)}  (n={r["total"]}, NO GROUND TRUTH)')

    # Output as JS
    print('\n// Update in modules_data.js:')
    print('const binaryMetrics = ' + json.dumps(all_results, indent=2) + ';')

    # Save to file
    output_file = Path(__file__).parent / 'binary_metrics.json'
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f'\nSaved to: {output_file}')

    return all_results

if __name__ == '__main__':
    main()
