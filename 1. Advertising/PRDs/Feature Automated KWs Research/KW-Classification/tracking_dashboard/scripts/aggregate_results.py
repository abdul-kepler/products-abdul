#!/usr/bin/env python3
"""
Aggregate Results - Level 2 Aggregation Script

Collects all judge results and experiment metadata into a single all_runs.yaml file.
This script is IDEMPOTENT - running it multiple times produces the same result.

Key principles:
- Uses run_id as unique identifier (never duplicates)
- MERGE strategy - adds new runs, never overwrites existing
- Reads metadata from meta.json or experiment_mappings.yaml (fallback)

Usage:
    python aggregate_results.py              # Full aggregation
    python aggregate_results.py --dry-run    # Show what would be added
    python aggregate_results.py --verbose    # Detailed output
"""

import json
import yaml
import re
import csv
import math
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
TRACKING_DASHBOARD = PROJECT_ROOT / "tracking_dashboard"
DATA_DIR = TRACKING_DASHBOARD / "data"

# Source paths
EVALUATION_KD = PROJECT_ROOT / "evaluation_KD" / "evaluation_experimentV5"
JUDGE_RESULTS_DIR = EVALUATION_KD / "judge_results"
EXPERIMENT_RESULTS_DIR = PROJECT_ROOT / "experiment_results"
EXPERIMENT_MAPPINGS_FILE = EVALUATION_KD / "experiment_mappings.yaml"
RESOURCE_MAPPINGS_FILE = EVALUATION_KD / "resource_mappings.yaml"

# Output
ALL_RUNS_FILE = DATA_DIR / "all_runs.yaml"

# Binary classifier module configs (for calculating TP/TN/FP/FN)
BINARY_MODULES = {
    'm02': {
        'json_field': 'branding_scope_1',
        'labels': {'tp': 'OB', 'tn': 'Null', 'fp': 'Null→OB', 'fn': 'OB→Null'},
    },
    'm02b': {
        'json_field': 'branding_scope_1',
        'labels': {'tp': 'OB', 'tn': 'Null', 'fp': 'Null→OB', 'fn': 'OB→Null'},
    },
    'm04': {
        'json_field': 'branding_scope_2',
        'labels': {'tp': 'CB', 'tn': 'Null', 'fp': 'Null→CB', 'fn': 'CB→Null'},
    },
    'm04b': {
        'json_field': 'branding_scope_2',
        'labels': {'tp': 'CB', 'tn': 'Null', 'fp': 'Null→CB', 'fn': 'CB→Null'},
    },
    'm05': {
        'json_field': 'branding_scope_3',
        'labels': {'tp': 'NB', 'tn': 'Branded', 'fp': 'Brand→NB', 'fn': 'NB→Brand'},
    },
    'm05b': {
        'json_field': 'branding_scope_3',
        'labels': {'tp': 'NB', 'tn': 'Branded', 'fp': 'Brand→NB', 'fn': 'NB→Brand'},
    },
    'm12': {
        'expected_field': 'relevancy',
        'output_field': 'violates_constraint',
        'positive_expected': 'N',
        'positive_output': True,
        'null_is_negative': True,
        'labels': {'tp': 'Violates', 'tn': 'OK', 'fp': 'OK→Violates', 'fn': 'Violates→OK'},
    },
    'm12b': {
        'expected_field': 'relevancy',
        'output_field': 'violates_constraint',
        'positive_expected': 'N',
        'positive_output': True,
        'null_is_negative': True,
        'labels': {'tp': 'Violates', 'tn': 'OK', 'fp': 'OK→Violates', 'fn': 'Violates→OK'},
    },
    'm13': {
        'expected_field': 'same_type',
        'output_field': 'same_product_type',
        'labels': {'tp': 'Match', 'tn': 'Diff', 'fp': 'Diff→Match', 'fn': 'Match→Diff'},
    },
    'm14': {
        'json_field': 'relevancy',
        'labels': {'tp': 'R', 'tn': '-', 'fp': '-', 'fn': 'R→Other'},
    },
    'm15': {
        'json_field': 'relevancy',
        'positive_expected': 'S',
        'positive_output': 'S',
        'null_is_negative': True,
        'labels': {'tp': 'S', 'tn': 'not-S', 'fp': 'null→S', 'fn': 'S→not-S'},
    },
    'm16': {
        'json_field': 'relevancy',
        'labels': {'tp': 'C', 'tn': '-', 'fp': '-', 'fn': 'C→N'},
    },
}

# Primary rubric for each module - used to calculate "match_rate" (main task success metric)
# match_rate = pass rate for ONLY the primary rubric (vs pass_rate = all rubrics)
PRIMARY_RUBRIC_MAP = {
    'm01': 'M01_brand_extracted',
    'm01a': 'M01a_has_variations',
    'm01b': None,  # Sub-brands can legitimately be empty
    'm02': 'M02_correct_classification',
    'm02b': 'M02_correct_classification',
    'm04': 'M04_correct_classification',
    'm04b': 'M04_correct_classification',
    'm05': 'M05_correct_classification',
    'm05b': 'M05_correct_classification',
    'm06': 'M06_hierarchy_correct',
    'm07': 'M07_attributes_from_listing',
    'm08': 'M08_ranks_assigned',
    'm09': 'M09_captures_core_purpose',
    'm10': 'M10_invalid_correctly_flagged',
    'm11': 'M11_critical_not_missed',
    'm12': 'M12_correct_classification',
    'm12b': 'M12_correct_classification',
    'm13': 'M13_same_type_correct',
    'm14': 'M14_same_use_correct',
    'm15': 'M15_substitute_correct',
    'm16': 'M16_complementary_correct',
}


def get_primary_rubric(module: str) -> Optional[str]:
    """Get the primary rubric ID for a module."""
    # Normalize module name (remove version suffixes like _v2, _gemini)
    base_module = re.sub(r'_v\d+.*$', '', module.lower())
    base_module = re.sub(r'_gemini.*$', '', base_module)
    base_module = re.sub(r'_gpt.*$', '', base_module)
    base_module = re.sub(r'_sd\d*$|_gd\d*$', '', base_module)
    return PRIMARY_RUBRIC_MAP.get(base_module)


def calculate_match_rate(evaluations: list, module: str) -> float:
    """
    Calculate match_rate based on primary rubric for the module.

    match_rate = pass rate for ONLY the primary rubric evaluations
    (different from pass_rate which is across ALL rubrics)
    """
    primary_rubric = get_primary_rubric(module)
    if not primary_rubric:
        return 0.0

    # Filter evaluations for the primary rubric
    primary_evals = [ev for ev in evaluations if ev.get('rubric_id', '') == primary_rubric]

    if not primary_evals:
        return 0.0

    pass_count = sum(1 for ev in primary_evals if ev.get('verdict') == 'PASS')
    total_count = len(primary_evals)

    return (pass_count / total_count * 100) if total_count > 0 else 0.0


def calculate_rubric_breakdown(evaluations: list) -> dict:
    """
    Calculate pass rate for each rubric from evaluations.

    Returns dict like:
    {
        "M01_brand_extracted": {"pass": 13, "fail": 2, "total": 15, "pass_rate": 86.67},
        "M01_no_hallucination": {"pass": 9, "fail": 6, "total": 15, "pass_rate": 60.0},
        ...
    }
    """
    rubric_stats = {}

    for ev in evaluations:
        rubric_id = ev.get('rubric_id', 'unknown')
        verdict = ev.get('verdict', 'unknown')

        if rubric_id not in rubric_stats:
            rubric_stats[rubric_id] = {'pass': 0, 'fail': 0, 'total': 0}

        rubric_stats[rubric_id]['total'] += 1
        if verdict == 'PASS':
            rubric_stats[rubric_id]['pass'] += 1
        else:
            rubric_stats[rubric_id]['fail'] += 1

    # Calculate pass_rate for each rubric
    for rubric_id, stats in rubric_stats.items():
        if stats['total'] > 0:
            stats['pass_rate'] = round(stats['pass'] / stats['total'] * 100, 2)
        else:
            stats['pass_rate'] = 0.0

    return rubric_stats


# ============================================================================
# Binary Metrics Calculation Functions
# ============================================================================

def calculate_mcc(tp: int, tn: int, fp: int, fn: int) -> float:
    """Matthews Correlation Coefficient."""
    numerator = (tp * tn) - (fp * fn)
    denominator = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    if denominator == 0:
        return 0
    return numerator / denominator


def is_positive(value) -> bool:
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


def parse_json_field(json_str: str, field_name: str):
    """Parse JSON string and extract field value."""
    if not json_str:
        return None
    try:
        data = json.loads(json_str)
        return data.get(field_name)
    except (json.JSONDecodeError, TypeError):
        return None


def calculate_binary_metrics(csv_path: Path, config: dict) -> Optional[dict]:
    """
    Calculate binary classification metrics from CSV file.

    Returns dict with tp, tn, fp, fn, accuracy, precision, recall, f1, mcc.
    Returns None if CSV cannot be processed.
    """
    if not csv_path.exists():
        return None

    tp = tn = fp = fn = 0
    skipped = 0
    null_is_negative = config.get('null_is_negative', False)
    positive_expected = config.get('positive_expected')
    positive_output = config.get('positive_output')

    try:
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                try:
                    exp_field = config.get('expected_field') or config.get('json_field')
                    out_field = config.get('output_field') or config.get('json_field')

                    if 'output' in row and 'expected' in row:
                        exp_val = parse_json_field(row.get('expected'), exp_field)
                        act_val = parse_json_field(row.get('output'), out_field)
                    else:
                        skipped += 1
                        continue

                    # Determine expected positive
                    if positive_expected is not None:
                        exp_pos = (exp_val == positive_expected)
                    elif null_is_negative and exp_val is None:
                        exp_pos = False
                    else:
                        exp_pos = is_positive(exp_val)

                    # Determine actual positive
                    if positive_output is not None:
                        act_pos = (act_val == positive_output)
                    else:
                        act_pos = is_positive(act_val)

                    # Calculate confusion matrix
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

    except Exception as e:
        return None

    total = tp + tn + fp + fn
    if total == 0:
        return None

    # Calculate metrics
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
        'accuracy': round(accuracy, 2),
        'precision': round(precision, 2),
        'recall': round(recall, 2),
        'f1': round(f1, 2),
        'mcc': round(mcc, 3),
        'labels': config.get('labels', {}),
    }


# ============================================================================
# Utility Functions
# ============================================================================

def normalize_model_name(model: str) -> str:
    """Normalize model name for consistent run_id generation."""
    model_map = {
        'gpt-4o-mini': 'gpt4omini',
        'gpt-4o': 'gpt4o',
        'gpt-5': 'gpt5',
        'gemini-2.0-flash': 'gemini20flash',
        'gemini-2.5-pro': 'gemini25pro',
    }
    if not model:
        return 'unknown'
    return model_map.get(model, model.replace('-', '').replace('.', ''))


def generate_run_id(module: str, prompt_version: str, model: str, timestamp: str, existing_ids: set) -> str:
    """
    Generate unique run_id in format: module_version_model_date[_counter]

    Examples:
    - m02_v1_gpt4omini_220126
    - m02_v1_gpt4omini_220126_2 (if first already exists)
    """
    # Parse date from timestamp
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        date_str = dt.strftime('%d%m%y')
    except:
        date_str = datetime.now().strftime('%d%m%y')

    model_short = normalize_model_name(model)
    base_id = f"{module}_{prompt_version}_{model_short}_{date_str}"

    # Check if base_id exists, add counter if needed
    if base_id not in existing_ids:
        return base_id

    counter = 2
    while f"{base_id}_{counter}" in existing_ids:
        counter += 1
    return f"{base_id}_{counter}"


def load_experiment_mappings() -> dict:
    """Load experiment_mappings.yaml for metadata lookup."""
    if not EXPERIMENT_MAPPINGS_FILE.exists():
        return {}

    with open(EXPERIMENT_MAPPINGS_FILE) as f:
        data = yaml.safe_load(f) or {}

    # Index by local_file for quick lookup
    mappings = {}
    for exp in data.get('experiments', []):
        local_file = exp.get('local_file', '')
        if local_file:
            # Store by filename only (not full path)
            filename = Path(local_file).name
            mappings[filename] = exp

    return mappings


def load_resource_mappings() -> dict:
    """Load resource_mappings.yaml to get module types."""
    if not RESOURCE_MAPPINGS_FILE.exists():
        return {}

    with open(RESOURCE_MAPPINGS_FILE) as f:
        data = yaml.safe_load(f) or {}

    return data.get('prompts', {})


def find_meta_json(csv_path: str) -> Optional[dict]:
    """Find and load meta.json for a CSV file."""
    csv_file = Path(csv_path)
    if not csv_file.exists():
        # Try relative path from project root
        csv_file = PROJECT_ROOT / csv_path

    if not csv_file.exists():
        return None

    # Look for meta.json with same base name
    meta_file = csv_file.with_suffix('.meta.json')
    if meta_file.exists():
        with open(meta_file) as f:
            return json.load(f)

    return None


def extract_version_from_string(s: str) -> Optional[str]:
    """Extract version (v1, v2, etc.) from a string."""
    # Look for patterns like _v1, _v2, _V1, _V2, etc.
    match = re.search(r'[_-][vV](\d+)', s)
    if match:
        return f"v{match.group(1)}"
    return None


def extract_metadata_from_judge(judge_data: dict, exp_mappings: dict, res_mappings: dict) -> dict:
    """
    Extract metadata from judge result, enriching with mappings data.

    Priority:
    1. meta.json (if exists next to CSV)
    2. experiment_mappings.yaml
    3. Judge result fields (fallback)
    """
    data_source = judge_data.get('data_source', '')
    csv_filename = Path(data_source).name if data_source else ''

    # Try meta.json first
    meta = find_meta_json(data_source)

    # Fallback to experiment_mappings
    if not meta and csv_filename in exp_mappings:
        meta = exp_mappings[csv_filename]

    # Extract module from judge or meta
    module_raw = judge_data.get('module', '').lower()
    if not module_raw and meta:
        module_raw = meta.get('module', '')

    # Clean module (remove version and model suffix like m01_v1_gemini -> m01)
    # Pattern: m01, m01_v2, m01_v2_gemini, m01a, m01a_v2, etc.
    module_match = re.match(r'^(m\d+[ab]?)', module_raw)
    module_base = module_match.group(1) if module_match else module_raw.split('_')[0]

    # Get module type from resource_mappings
    module_type = 'unknown'
    if module_base in res_mappings:
        module_type = res_mappings[module_base].get('type', 'unknown')

    # Extract version - try multiple sources
    prompt_version = None

    # 1. From meta.json/mappings (if it looks like v1, v2, etc.)
    if meta:
        pv = meta.get('prompt_version', '')
        if pv and re.match(r'^v\d+$', str(pv)):
            prompt_version = pv

    # 2. From module field (m01_v2_gemini -> v2)
    if not prompt_version:
        prompt_version = extract_version_from_string(module_raw)

    # 3. From CSV filename (M01_V3_ExtractOwnBrand... -> v3)
    if not prompt_version and csv_filename:
        prompt_version = extract_version_from_string(csv_filename)

    # 4. Default to v1
    if not prompt_version:
        prompt_version = 'v1'

    # Build metadata dict
    result = {
        'module': module_base,
        'module_type': module_type,
        'prompt_version': prompt_version,
        'model': meta.get('model') if meta else judge_data.get('model', 'unknown'),
        'dataset_name': meta.get('dataset_name', '') if meta else '',
        'dataset_id': meta.get('dataset_id', '') if meta else '',
        'prompt_id': meta.get('prompt_id', '') if meta else '',
        'braintrust_experiment_id': meta.get('braintrust_experiment_id', '') if meta else '',
        'temperature': meta.get('temperature', 0) if meta else 0,
    }

    return result


def process_judge_result(judge_file: Path, existing_ids: set, exp_mappings: dict, res_mappings: dict) -> Optional[dict]:
    """Process a single judge result file and return run entry."""
    try:
        with open(judge_file) as f:
            judge_data = json.load(f)
    except Exception as e:
        print(f"  ✗ Error reading {judge_file.name}: {e}")
        return None

    # Extract metadata
    meta = extract_metadata_from_judge(judge_data, exp_mappings, res_mappings)

    # Get timestamp
    timestamp = judge_data.get('timestamp', datetime.now().isoformat())

    # Generate unique run_id
    run_id = generate_run_id(
        meta['module'],
        meta['prompt_version'],
        meta['model'],
        timestamp,
        existing_ids
    )

    # Build run entry
    summary = judge_data.get('summary', {})
    total = summary.get('pass', 0) + summary.get('fail', 0) + summary.get('error', 0)
    pass_rate = (summary.get('pass', 0) / total * 100) if total > 0 else 0

    # Calculate match_rate based on primary rubric for this module
    evaluations = judge_data.get('evaluations', [])
    match_rate = calculate_match_rate(evaluations, meta['module'])

    # Calculate rubric breakdown (pass rate per rubric)
    rubric_breakdown = calculate_rubric_breakdown(evaluations)

    # Calculate binary metrics if this is a binary classifier module
    binary_metrics = None
    data_source = judge_data.get('data_source', '')

    if meta['module'] in BINARY_MODULES and data_source:
        csv_path = Path(data_source)
        if not csv_path.exists():
            # Try relative to project root
            csv_path = PROJECT_ROOT / data_source

        if csv_path.exists():
            config = BINARY_MODULES[meta['module']]
            binary_metrics = calculate_binary_metrics(csv_path, config)

    run_entry = {
        'run_id': run_id,
        'module': meta['module'],
        'module_type': meta['module_type'],
        'prompt_version': meta['prompt_version'],
        'model': meta['model'],
        'dataset_name': meta['dataset_name'],
        'dataset_id': meta['dataset_id'],
        'prompt_id': meta['prompt_id'],
        'braintrust_experiment_id': meta['braintrust_experiment_id'],
        'temperature': meta['temperature'],

        # Judge results
        'pass_rate': round(pass_rate, 2),
        'match_rate': round(match_rate, 2),
        'summary': summary,
        'total_samples': total,

        # Rubric breakdown (pass rate per rubric)
        'rubric_breakdown': rubric_breakdown,

        # Binary metrics (calculated from CSV)
        'binary_metrics': binary_metrics,

        # Source files
        'judge_file': judge_file.name,
        'csv_file': Path(data_source).name if data_source else '',

        # Timestamps
        'timestamp': timestamp,
        'aggregated_at': datetime.now().isoformat(),
    }

    return run_entry


def load_existing_runs() -> dict:
    """Load existing all_runs.yaml."""
    if not ALL_RUNS_FILE.exists():
        return {'version': '1.0', 'runs': {}}

    with open(ALL_RUNS_FILE) as f:
        data = yaml.safe_load(f) or {}

    if 'runs' not in data:
        data['runs'] = {}

    return data


def create_content_hash(judge_file: Path) -> str:
    """Create a hash of judge file content for deduplication."""
    try:
        with open(judge_file) as f:
            data = json.load(f)

        # Key fields that identify unique run
        key_parts = [
            data.get('module', ''),
            data.get('model', ''),
            data.get('data_source', ''),
            str(data.get('summary', {})),
        ]
        return '|'.join(key_parts)
    except:
        return judge_file.name


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Aggregate judge results into all_runs.yaml")
    parser.add_argument('--dry-run', action='store_true', help="Show what would be added without saving")
    parser.add_argument('--verbose', '-v', action='store_true', help="Verbose output")
    parser.add_argument('--rebuild', action='store_true', help="Rebuild all runs from scratch (re-process all judge files)")
    args = parser.parse_args()

    print("=" * 60)
    print("📊 Aggregate Results")
    print("=" * 60)

    # Load existing runs (or start fresh if --rebuild)
    if args.rebuild:
        print("  🔄 Rebuild mode: starting fresh")
        all_runs = {'version': '1.0', 'runs': {}}
    else:
        all_runs = load_existing_runs()
    existing_ids = set(all_runs['runs'].keys())

    # Track content hashes to detect true duplicates
    existing_hashes = set()
    # Track CSV files to avoid duplicate experiments (same CSV = same experiment)
    existing_csvs = {}  # csv_file -> run_id (to allow replacement with newer)

    if not args.rebuild:
        for run_id, run_data in all_runs['runs'].items():
            judge_file = run_data.get('judge_file', '')
            if judge_file:
                existing_hashes.add(judge_file)
            csv_file = run_data.get('csv_file', '')
            if csv_file:
                existing_csvs[csv_file] = run_id

    print(f"  Existing runs: {len(existing_ids)}")
    print(f"  Existing CSVs: {len(existing_csvs)}")

    # Load mappings
    exp_mappings = load_experiment_mappings()
    res_mappings = load_resource_mappings()
    print(f"  Experiment mappings: {len(exp_mappings)}")
    print(f"  Resource mappings: {len(res_mappings)}")

    # Find all judge results
    if not JUDGE_RESULTS_DIR.exists():
        print(f"  ✗ Judge results directory not found: {JUDGE_RESULTS_DIR}")
        return

    judge_files = sorted(JUDGE_RESULTS_DIR.glob("*_judge_*.json"))
    print(f"  Judge result files: {len(judge_files)}")

    # Process each judge file
    new_runs = []
    skipped = 0

    print("\n📋 Processing judge results...")

    for judge_file in judge_files:
        # Skip if this exact judge file already processed
        if judge_file.name in existing_hashes:
            if args.verbose:
                print(f"  ⏭ Skip (exists): {judge_file.name}")
            skipped += 1
            continue

        run_entry = process_judge_result(judge_file, existing_ids, exp_mappings, res_mappings)

        if run_entry:
            csv_file = run_entry.get('csv_file', '')

            # Check if this CSV already exists - skip if so (to avoid duplicates)
            if csv_file and csv_file in existing_csvs:
                if args.verbose:
                    print(f"  ⏭ Skip (CSV exists): {judge_file.name} -> {csv_file}")
                skipped += 1
                continue

            new_runs.append(run_entry)
            existing_ids.add(run_entry['run_id'])
            existing_hashes.add(judge_file.name)
            if csv_file:
                existing_csvs[csv_file] = run_entry['run_id']

            if args.verbose:
                print(f"  ✓ Add: {run_entry['run_id']}")

    print(f"\n📈 Summary:")
    print(f"  Existing runs: {len(all_runs['runs'])}")
    print(f"  Skipped (duplicates): {skipped}")
    print(f"  New runs to add: {len(new_runs)}")

    if not new_runs:
        print("\n✅ No new runs to add. all_runs.yaml is up to date.")
        return

    # Add new runs
    for run in new_runs:
        all_runs['runs'][run['run_id']] = run

    all_runs['last_updated'] = datetime.now().isoformat()
    all_runs['total_runs'] = len(all_runs['runs'])

    if args.dry_run:
        print("\n🔍 Dry run - new runs that would be added:")
        for run in new_runs:
            print(f"  - {run['run_id']}: {run['module']} {run['prompt_version']} {run['model']} ({run['pass_rate']}%)")
        print("\n⚠️  Use without --dry-run to save changes")
    else:
        # Save
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(ALL_RUNS_FILE, 'w') as f:
            yaml.dump(all_runs, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

        print(f"\n✅ Saved {len(all_runs['runs'])} runs to {ALL_RUNS_FILE}")

        # Show new runs
        print("\n📋 New runs added:")
        for run in new_runs:
            print(f"  + {run['run_id']}: {run['pass_rate']}% pass rate")


if __name__ == "__main__":
    main()
