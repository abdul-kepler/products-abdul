#!/usr/bin/env python3
"""
Aggregate Known Issues - Extract and categorize errors from judge results.

For binary classifiers: categorizes False Positives (FP) and False Negatives (FN).
For extraction modules: categorizes by rubric failures.

Usage:
    python aggregate_known_issues.py              # Full aggregation
    python aggregate_known_issues.py --verbose    # Detailed output
    python aggregate_known_issues.py --module m02 # Specific module only
"""

import json
import yaml
import csv
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any
from collections import defaultdict

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
TRACKING_DASHBOARD = SCRIPT_DIR.parent
DATA_DIR = TRACKING_DASHBOARD / "data"

# Source paths
EVALUATION_KD = PROJECT_ROOT / "evaluation_KD" / "evaluation_experimentV5"
JUDGE_RESULTS_DIR = EVALUATION_KD / "judge_results"

# Output
KNOWN_ISSUES_FILE = DATA_DIR / "known_issues.yaml"

# Binary classifier configs (for FP/FN categorization)
BINARY_MODULES = {
    'm02': {'field': 'branding_scope_1', 'positive': 'OB'},
    'm02b': {'field': 'branding_scope_1', 'positive': 'OB'},
    'm04': {'field': 'branding_scope_2', 'positive': 'CB'},
    'm04b': {'field': 'branding_scope_2', 'positive': 'CB'},
    'm05': {'field': 'branding_scope_3', 'positive': 'NB'},
    'm05b': {'field': 'branding_scope_3', 'positive': 'NB'},
    'm12': {'field': 'violates_constraint', 'positive': True},
    'm12b': {'field': 'violates_constraint', 'positive': True},
    'm13': {'field': 'same_product_type', 'positive': True},
    'm14': {'field': 'relevancy', 'positive': 'R'},
    'm15': {'field': 'relevancy', 'positive': 'S'},
    'm16': {'field': 'relevancy', 'positive': 'C'},
}


def parse_json_safe(json_str: str) -> Optional[dict]:
    """Safely parse JSON string."""
    if not json_str:
        return None
    try:
        return json.loads(json_str)
    except:
        return None


def is_positive_value(value, positive_class) -> bool:
    """Check if value matches the positive class."""
    if value is None:
        return False
    if isinstance(positive_class, bool):
        return value == positive_class
    if isinstance(value, str):
        return value.strip().upper() == str(positive_class).upper()
    return bool(value)


def extract_binary_errors_from_csv(csv_path: Path, config: dict) -> Dict[str, List[dict]]:
    """
    Extract FP and FN errors from CSV for binary classifiers.

    Returns:
        {'false_positives': [...], 'false_negatives': [...]}
    """
    errors = {'false_positives': [], 'false_negatives': []}

    if not csv_path.exists():
        return errors

    field = config['field']
    positive = config['positive']

    try:
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                expected_json = parse_json_safe(row.get('expected', ''))
                output_json = parse_json_safe(row.get('output', ''))

                if not expected_json or not output_json:
                    continue

                expected_val = expected_json.get(field)
                output_val = output_json.get(field)

                exp_pos = is_positive_value(expected_val, positive)
                out_pos = is_positive_value(output_val, positive)

                # False Positive: expected negative, output positive
                if not exp_pos and out_pos:
                    errors['false_positives'].append({
                        'input': row.get('input', ''),
                        'expected': str(expected_val),
                        'output': str(output_val),
                        'sample_id': expected_json.get('sample_id', row.get('id', '')),
                    })

                # False Negative: expected positive, output negative
                elif exp_pos and not out_pos:
                    errors['false_negatives'].append({
                        'input': row.get('input', ''),
                        'expected': str(expected_val),
                        'output': str(output_val),
                        'sample_id': expected_json.get('sample_id', row.get('id', '')),
                    })

    except Exception as e:
        print(f"    ✗ Error reading CSV: {e}")

    return errors


def extract_errors_from_judge(judge_file: Path) -> Dict[str, Any]:
    """
    Extract errors from judge result file.

    For binary modules: extracts FP/FN from CSV.
    For other modules: extracts failed evaluations by rubric.
    """
    try:
        with open(judge_file) as f:
            judge_data = json.load(f)
    except Exception as e:
        return {'error': str(e)}

    # Extract module info
    module_raw = judge_data.get('module', '').lower()
    module_base = module_raw.split('_')[0] if '_' in module_raw else module_raw
    data_source = judge_data.get('data_source', '')

    result = {
        'module': module_base,
        'judge_file': judge_file.name,
        'pass_rate': judge_data.get('pass_rate', 0),
        'categories': [],
    }

    # For binary classifiers, extract from CSV
    if module_base in BINARY_MODULES and data_source:
        csv_path = Path(data_source)
        if not csv_path.exists():
            csv_path = PROJECT_ROOT / data_source

        config = BINARY_MODULES[module_base]
        errors = extract_binary_errors_from_csv(csv_path, config)

        if errors['false_positives']:
            result['categories'].append({
                'id': 'false_positive',
                'name': 'False Positives (FP)',
                'icon': '🔮',
                'color': '#ef4444',
                'count': len(errors['false_positives']),
                'description': 'Model incorrectly predicted positive when should be negative',
                'errors': errors['false_positives'][:20],  # Limit to 20 samples
            })

        if errors['false_negatives']:
            result['categories'].append({
                'id': 'false_negative',
                'name': 'False Negatives (FN)',
                'icon': '📝',
                'color': '#eab308',
                'count': len(errors['false_negatives']),
                'description': 'Model missed positive case (predicted negative)',
                'errors': errors['false_negatives'][:20],  # Limit to 20 samples
            })

    # For all modules, also extract rubric-based failures from evaluations
    evaluations = judge_data.get('evaluations', [])
    rubric_failures = defaultdict(list)

    for eval_item in evaluations:
        if eval_item.get('verdict') == 'FAIL':
            rubric_id = eval_item.get('rubric_id', eval_item.get('criterion', 'unknown'))
            rubric_failures[rubric_id].append({
                'sample_id': eval_item.get('sample_id', ''),
                'criterion': eval_item.get('criterion', ''),
                'reasoning': eval_item.get('reasoning', '')[:200],  # Truncate
                'expected': str(eval_item.get('expected', ''))[:100],
                'output': str(eval_item.get('output', ''))[:100],
            })

    # Add rubric failure categories (if not binary or in addition to FP/FN)
    for rubric_id, failures in rubric_failures.items():
        # Skip if already covered by FP/FN for binary modules
        if module_base in BINARY_MODULES and rubric_id in ['false_positive', 'false_negative']:
            continue

        result['categories'].append({
            'id': rubric_id,
            'name': rubric_id.replace('_', ' ').title(),
            'icon': '⚠️',
            'color': '#f97316',
            'count': len(failures),
            'description': f'Failed rubric: {rubric_id}',
            'errors': failures[:10],  # Limit samples
        })

    return result


def aggregate_known_issues(modules_filter: Optional[List[str]] = None, verbose: bool = False) -> dict:
    """
    Aggregate known issues from all judge results.

    Returns dict organized by module.
    """
    all_issues = {}

    if not JUDGE_RESULTS_DIR.exists():
        print(f"  ✗ Judge results directory not found: {JUDGE_RESULTS_DIR}")
        return all_issues

    judge_files = sorted(JUDGE_RESULTS_DIR.glob("*_judge_*.json"))
    print(f"  Found {len(judge_files)} judge result files")

    for judge_file in judge_files:
        result = extract_errors_from_judge(judge_file)

        if 'error' in result:
            if verbose:
                print(f"    ✗ {judge_file.name}: {result['error']}")
            continue

        module = result['module']

        # Filter if specified
        if modules_filter and module not in modules_filter:
            continue

        # Merge into module entry
        if module not in all_issues:
            all_issues[module] = {
                'module': module,
                'total_errors': 0,
                'categories': [],
                'judge_files': [],
            }

        # Add judge file
        all_issues[module]['judge_files'].append(judge_file.name)

        # Merge categories
        for cat in result.get('categories', []):
            existing_cat = None
            for ec in all_issues[module]['categories']:
                if ec['id'] == cat['id']:
                    existing_cat = ec
                    break

            if existing_cat:
                # Merge errors (avoid duplicates by sample_id)
                existing_ids = {e.get('sample_id') for e in existing_cat.get('errors', [])}
                for err in cat.get('errors', []):
                    if err.get('sample_id') not in existing_ids:
                        existing_cat['errors'].append(err)
                        existing_ids.add(err.get('sample_id'))
                existing_cat['count'] = len(existing_cat['errors'])
            else:
                all_issues[module]['categories'].append(cat)

        # Update total errors
        all_issues[module]['total_errors'] = sum(
            c['count'] for c in all_issues[module]['categories']
        )

        if verbose:
            print(f"    ✓ {module}: {result.get('pass_rate', 0)}% pass, {len(result.get('categories', []))} categories")

    return all_issues


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Aggregate known issues from judge results")
    parser.add_argument('--verbose', '-v', action='store_true', help="Verbose output")
    parser.add_argument('--module', '-m', help="Filter by module (e.g., m02)")
    args = parser.parse_args()

    print("=" * 60)
    print("📋 Aggregate Known Issues")
    print("=" * 60)

    modules_filter = [args.module] if args.module else None

    all_issues = aggregate_known_issues(modules_filter, args.verbose)

    print(f"\n📈 Summary:")
    for module, data in sorted(all_issues.items()):
        print(f"  {module}: {data['total_errors']} errors in {len(data['categories'])} categories")

    # Save to file
    output = {
        'version': '1.0',
        'last_updated': datetime.now().isoformat(),
        'modules': all_issues,
    }

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(KNOWN_ISSUES_FILE, 'w') as f:
        yaml.dump(output, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print(f"\n✅ Saved to {KNOWN_ISSUES_FILE}")


if __name__ == "__main__":
    main()
