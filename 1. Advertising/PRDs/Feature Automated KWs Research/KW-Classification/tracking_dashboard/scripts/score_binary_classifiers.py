#!/usr/bin/env python3
"""
Score binary classifiers directly from CSV results.
No LLM judge needed - just compare expected vs actual values.

Now processes ALL CSV files and stores metrics per experiment with version/model/dataset info.

Usage:
    python score_binary_classifiers.py          # Score all binary modules
    python score_binary_classifiers.py m02      # Score specific module
"""

import csv
import json
import math
import re
import sys
from pathlib import Path

# Binary classifier module configs
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
        'expected_field': 'relevancy',
        'output_field': 'violates_constraint',
        'positive_expected': 'N',
        'positive_output': True,
        'null_is_negative': True,
        'labels': {'tp': 'Violates', 'tn': 'OK', 'fp': 'OK→Violates', 'fn': 'Violates→OK'},
    },
    'm13': {
        'name': 'Product Type Check',
        'folder': 'M13_ProductTypeCheck',
        'expected_field': 'same_type',
        'output_field': ['same_product_type', 'same_type'],  # GPT-4o-mini uses same_product_type, GPT-5 uses same_type
        'labels': {'tp': 'Match', 'tn': 'Diff', 'fp': 'Diff→Match', 'fn': 'Match→Diff'},
    },
    'm14': {
        'name': 'Primary Use Check (Relevancy)',
        'folder': 'M14_PrimaryUseCheckSameType',
        'json_field': 'relevancy',
        'positive_expected': 'R',
        'positive_output': 'R',
        'labels': {'tp': 'R', 'tn': 'N', 'fp': 'N→R', 'fn': 'R→N'},
    },
    'm15': {
        'name': 'Substitute Check (Relevancy)',
        'folder': 'M15_SubstituteCheck',
        'json_field': 'relevancy',
        'positive_expected': 'S',
        'positive_output': 'S',
        'null_is_negative': True,
        'labels': {'tp': 'S', 'tn': 'not-S', 'fp': 'null→S', 'fn': 'S→not-S'},
    },
    'm16': {
        'name': 'Complementary Check (Relevancy)',
        'folder': 'M16_ComplementaryCheck',
        'json_field': 'relevancy',
        'positive_expected': 'C',
        'positive_output': 'C',
        'labels': {'tp': 'C', 'tn': 'N', 'fp': 'N→C', 'fn': 'C→N'},
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
    """Parse JSON string and extract field value.

    field_name can be a string or a list of strings (tries each in order).
    """
    if not json_str:
        return None
    try:
        data = json.loads(json_str)
        # Support list of field names (try each in order)
        if isinstance(field_name, list):
            for fname in field_name:
                val = data.get(fname)
                if val is not None:
                    return val
            return None
        return data.get(field_name)
    except (json.JSONDecodeError, TypeError):
        return None


def extract_experiment_info(csv_path: Path) -> dict:
    """Extract prompt_version, model, dataset from meta.json or filename."""
    meta_path = csv_path.with_suffix('.meta.json')
    info = {
        'source_file': csv_path.name,
        'prompt_version': 'v1',
        'model': 'unknown',
        'dataset': '',
    }

    # Try to load meta.json
    if meta_path.exists():
        try:
            with open(meta_path) as f:
                meta = json.load(f)
            info['model'] = meta.get('model') or 'unknown'  # Handle null values
            info['dataset'] = meta.get('dataset_name') or ''
            # Extract version from experiment name like "M02_V2_..." or prompt_version
            exp_name = meta.get('braintrust_experiment_name', '')
            ver_match = re.search(r'[_\s]v(\d+)[_\s]', exp_name, re.I)
            if ver_match:
                info['prompt_version'] = f'v{ver_match.group(1)}'
        except Exception:
            pass

    # Fallback: extract from filename
    # Pattern: M02_ClassifyOwnBrand_v1_150126_1.csv or M02_V2_ClassifyOwnBrand_v2_200126_gemini.csv
    filename = csv_path.stem

    # Extract version
    ver_match = re.search(r'[_]v(\d+)[_]', filename, re.I)
    if ver_match and info['prompt_version'] == 'v1':
        info['prompt_version'] = f'v{ver_match.group(1)}'

    # Extract model from filename (e.g., _gemini20flash, _gpt4o)
    model_patterns = [
        (r'gemini[-_]?2\.?0[-_]?flash', 'gemini-2.0-flash'),
        (r'gemini20flash', 'gemini-2.0-flash'),
        (r'gpt[-_]?4o[-_]?mini', 'gpt-4o-mini'),
        (r'gpt4omini', 'gpt-4o-mini'),
        (r'gpt[-_]?4o', 'gpt-4o'),
        (r'gpt4o', 'gpt-4o'),
        (r'gpt[-_]?5', 'gpt-5'),
        (r'gpt5', 'gpt-5'),
    ]
    if info['model'] == 'unknown':
        for pattern, model_name in model_patterns:
            if re.search(pattern, filename, re.I):
                info['model'] = model_name
                break
        else:
            # Default to gpt-4o-mini if no model found
            info['model'] = 'gpt-4o-mini'

    # Extract dataset date (e.g., 150126, 200126)
    date_match = re.search(r'[_](\d{6})[_]', filename)
    if date_match and not info['dataset']:
        info['dataset'] = date_match.group(1)

    return info


def generate_run_id(module_id: str, info: dict) -> str:
    """Generate unique run ID like m02_v1_gpt4omini or m02_v2_gemini."""
    version = info['prompt_version']
    model_short = info['model'].replace('-', '').replace('.', '').replace(' ', '')[:10]
    return f"{module_id}_{version}_{model_short}"


def score_csv(csv_path, config):
    """Score a single CSV file."""
    tp = tn = fp = fn = 0
    skipped = 0
    duplicates = 0
    skip_none = config.get('skip_none_expected', False)
    null_is_negative = config.get('null_is_negative', False)
    positive_expected = config.get('positive_expected')
    positive_output = config.get('positive_output')

    # Track seen inputs to avoid counting duplicates
    seen_inputs = set()

    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Deduplicate based on input field
            input_val = row.get('input', '')
            if input_val in seen_inputs:
                duplicates += 1
                continue
            seen_inputs.add(input_val)
            try:
                exp_field = config.get('expected_field') or config.get('json_field')
                out_field = config.get('output_field') or config.get('json_field')

                if 'output' in row and 'expected' in row:
                    exp_val = parse_json_field(row.get('expected'), exp_field)
                    act_val = parse_json_field(row.get('output'), out_field)
                else:
                    skipped += 1
                    continue

                if skip_none and exp_val is None and not null_is_negative:
                    skipped += 1
                    continue

                if positive_expected is not None:
                    exp_pos = (exp_val == positive_expected)
                elif null_is_negative and exp_val is None:
                    exp_pos = False
                else:
                    exp_pos = is_positive(exp_val)

                if positive_output is not None:
                    act_pos = (act_val == positive_output)
                else:
                    act_pos = is_positive(act_val)

                if exp_pos and act_pos:
                    if isinstance(exp_val, str) and isinstance(act_val, str):
                        if exp_val.lower().strip() == act_val.lower().strip():
                            tp += 1
                        else:
                            fn += 1
                    else:
                        tp += 1
                elif not exp_pos and not act_pos:
                    tn += 1
                elif not exp_pos and act_pos:
                    fp += 1
                else:
                    fn += 1

            except Exception:
                skipped += 1

    total = tp + tn + fp + fn
    if total == 0:
        return None, f"No records processed (skipped: {skipped}, duplicates: {duplicates})"

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
        'skipped': skipped,
        'duplicates': duplicates
    }, None


def main():
    results_dir = Path(__file__).parent.parent.parent / 'experiment_results'
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

        csv_files = sorted(folder.glob('*.csv'), key=lambda f: f.stat().st_mtime, reverse=True)
        if not csv_files:
            print(f'{module_id}: No CSV files found')
            continue

        print(f'\n{module_id.upper()}: {config["name"]}')
        print(f'  Found {len(csv_files)} CSV file(s)')

        # Process ALL CSV files
        for csv_file in csv_files:
            info = extract_experiment_info(csv_file)
            run_id = generate_run_id(module_id, info)

            print(f'\n  [{run_id}] {csv_file.name}')
            print(f'    Version: {info["prompt_version"]}, Model: {info["model"]}, Dataset: {info["dataset"]}')

            metrics, error = score_csv(csv_file, config)

            if error:
                print(f'    ERROR: {error}')
                continue

            # Add experiment info to metrics
            metrics['source_file'] = info['source_file']
            metrics['prompt_version'] = info['prompt_version']
            metrics['model'] = info['model']
            metrics['dataset'] = info['dataset']
            metrics['module'] = module_id

            # Add labels and notes
            if 'labels' in config:
                metrics['labels'] = config['labels']
            if 'note' in config:
                metrics['note'] = config['note']

            all_results[run_id] = metrics

            # Display metrics
            print(f'    Records: {metrics["total"]} (skipped: {metrics["skipped"]}, duplicates: {metrics["duplicates"]})')
            print(f'    TP={metrics["tp"]:4d}  FP={metrics["fp"]:4d}')
            print(f'    FN={metrics["fn"]:4d}  TN={metrics["tn"]:4d}')
            print(f'    Acc={metrics["accuracy"]:.1f}%  F1={metrics["f1"]:.1f}%  MCC={metrics["mcc"]:+.3f}')

    # Summary
    print('\n' + '=' * 70)
    print('SUMMARY - All Experiments')
    print('=' * 70)
    print(f'{"Run ID":<30} {"Ver":<4} {"Model":<15} {"Acc":>6} {"F1":>6} {"MCC":>7} {"N":>5}')
    print('-' * 70)
    for run_id, r in sorted(all_results.items()):
        print(f'{run_id:<30} {r["prompt_version"]:<4} {r["model"]:<15} {r["accuracy"]:>5.1f}% {r["f1"]:>5.1f}% {r["mcc"]:>+.3f} {r["total"]:>5}')

    # Save to file
    output_file = Path(__file__).parent.parent / 'dashboards' / 'binary_metrics.json'
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f'\nSaved {len(all_results)} entries to: {output_file}')

    return all_results


if __name__ == '__main__':
    main()
