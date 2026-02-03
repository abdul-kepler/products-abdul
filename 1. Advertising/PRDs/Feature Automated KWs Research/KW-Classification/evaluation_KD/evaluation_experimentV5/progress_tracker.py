#!/usr/bin/env python3
"""
Progress Tracker for Prompt/Model Versions.
Tracks evaluation results across different prompt versions and models.
"""

import json
import re
import yaml
from pathlib import Path
from datetime import datetime
from typing import Optional

SCRIPT_DIR = Path(__file__).parent
RESULTS_DIR = SCRIPT_DIR / "judge_results"
HISTORY_FILE = SCRIPT_DIR / "progress_history.yaml"

# Primary rubric for each module - used to calculate "primary_rate" (main task success metric)
# None means no primary rate calculation for that module
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
    base_module = re.sub(r'_sd$|_gd$', '', base_module)
    return PRIMARY_RUBRIC_MAP.get(base_module)


def parse_version_from_filename(filename: str) -> dict:
    """
    Parse prompt version and model from CSV filename.

    Examples:
    - M01_ExtractOwnBrandEntities_v1_150126_1.csv → prompt_version=v1, model=default
    - M01_ExtractOwnBrandEntities_v2_190126_1.csv → prompt_version=v2, model=default
    - M01_V2_ExtractOwnBrandEntities_v3_190126_1.csv → prompt_version=v3, model=default
    - M01_V3_ExtractOwnBrandEntities_v3_190126_gpt5.csv → prompt_version=v3, model=gpt-5
    """
    result = {
        'prompt_version': 'v1',
        'model_hint': None,
        'dataset_version': None
    }

    # Extract version from filename patterns
    # Pattern 1: _v{N}_ in the middle
    version_match = re.search(r'_v(\d+)_', filename)
    if version_match:
        result['prompt_version'] = f"v{version_match.group(1)}"

    # Pattern 2: _V{N}_ prefix (dataset version like M01_V2_)
    dataset_match = re.search(r'_V(\d+)_', filename)
    if dataset_match:
        result['dataset_version'] = f"v{dataset_match.group(1)}"

    # Pattern 3: Model suffix like _gpt5.csv, _gpt4o.csv
    model_match = re.search(r'_(gpt\d+[a-z]*)\.csv$', filename, re.IGNORECASE)
    if model_match:
        model_name = model_match.group(1).lower()
        # Normalize model names
        if model_name == 'gpt5':
            result['model_hint'] = 'gpt-5'
        elif model_name == 'gpt4o':
            result['model_hint'] = 'gpt-4o'
        elif model_name == 'gpt4omini':
            result['model_hint'] = 'gpt-4o-mini'
        else:
            result['model_hint'] = model_name

    return result


def load_history() -> dict:
    """Load existing progress history."""
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE) as f:
            return yaml.safe_load(f) or {'runs': []}
    return {'runs': []}


def save_history(history: dict):
    """Save progress history."""
    with open(HISTORY_FILE, 'w') as f:
        yaml.dump(history, f, default_flow_style=False, sort_keys=False)


def add_run_to_history(result_file: Path) -> dict:
    """
    Add a judge result to progress history.
    Returns the run entry that was added.
    """
    with open(result_file) as f:
        data = json.load(f)

    # Parse version info from data_source
    data_source = data.get('data_source', '')
    filename = Path(data_source).name if data_source else ''
    version_info = parse_version_from_filename(filename)

    # Determine model (from result or filename hint)
    model = data.get('model', 'gpt-4o-mini')
    if version_info['model_hint']:
        model = version_info['model_hint']

    # Calculate primary rate (main task success metric) using module-specific rubric
    evaluations = data.get('evaluations', [])
    module_name = data.get('module', 'unknown')
    primary_rubric = get_primary_rubric(module_name)

    match_rate = 0
    if primary_rubric:
        match_count = sum(1 for ev in evaluations
                        if ev.get('verdict') == 'PASS' and
                        ev.get('rubric_id', '') == primary_rubric)
        total_count = sum(1 for ev in evaluations
                        if ev.get('rubric_id', '') == primary_rubric)
        match_rate = (match_count / total_count * 100) if total_count > 0 else 0

    run_entry = {
        'run_id': result_file.stem,
        'module': data.get('module', 'unknown'),
        'prompt_version': version_info['prompt_version'],
        'dataset_version': version_info.get('dataset_version'),
        'model': model,
        'rubrics_version': data.get('rubrics_version', 'v5'),
        'timestamp': data.get('timestamp', datetime.now().isoformat()),
        'data_source': filename,
        'summary': data.get('summary', {}),
        'pass_rate': round(data.get('pass_rate', 0), 1),
        'match_rate': round(match_rate, 1),
        'total_evaluations': len(evaluations),
    }

    # Load existing history
    history = load_history()

    # Check if run already exists
    existing_ids = {r.get('run_id') for r in history.get('runs', [])}
    if run_entry['run_id'] not in existing_ids:
        history['runs'].append(run_entry)
        save_history(history)
        print(f"Added run: {run_entry['run_id']}")
    else:
        print(f"Run already exists: {run_entry['run_id']}")

    return run_entry


def rebuild_history_from_results():
    """
    Rebuild entire progress history from all judge result files.
    """
    print(f"Rebuilding history from {RESULTS_DIR}...")

    history = {'runs': []}

    for result_file in sorted(RESULTS_DIR.glob("*_judge_*.json")):
        try:
            with open(result_file) as f:
                data = json.load(f)

            data_source = data.get('data_source', '')
            filename = Path(data_source).name if data_source else ''
            version_info = parse_version_from_filename(filename)

            model = data.get('model', 'gpt-4o-mini')
            if version_info['model_hint']:
                model = version_info['model_hint']

            # Calculate primary rate using module-specific rubric
            evaluations = data.get('evaluations', [])
            module_name = data.get('module', 'unknown')
            primary_rubric = get_primary_rubric(module_name)

            match_rate = 0
            if primary_rubric:
                match_count = sum(1 for ev in evaluations
                               if ev.get('verdict') == 'PASS' and
                               ev.get('rubric_id', '') == primary_rubric)
                total_match = sum(1 for ev in evaluations
                                if ev.get('rubric_id', '') == primary_rubric)
                match_rate = (match_count / total_match * 100) if total_match > 0 else 0

            run_entry = {
                'run_id': result_file.stem,
                'module': data.get('module', 'unknown'),
                'prompt_version': version_info['prompt_version'],
                'dataset_version': version_info.get('dataset_version'),
                'model': model,
                'rubrics_version': data.get('rubrics_version', 'v5'),
                'timestamp': data.get('timestamp'),
                'data_source': filename,
                'summary': data.get('summary', {}),
                'pass_rate': round(data.get('pass_rate', 0), 1),
                'match_rate': round(match_rate, 1),
                'total_evaluations': len(evaluations),
            }

            history['runs'].append(run_entry)
            print(f"  Added: {result_file.name} → {version_info['prompt_version']}, {model}")

        except Exception as e:
            print(f"  Error processing {result_file.name}: {e}")

    # Sort by timestamp
    history['runs'].sort(key=lambda x: x.get('timestamp', ''))

    save_history(history)
    print(f"\nSaved {len(history['runs'])} runs to {HISTORY_FILE}")
    return history


def get_progress_summary(module: str = None) -> dict:
    """
    Get progress summary grouped by module and prompt version.
    """
    history = load_history()
    runs = history.get('runs', [])

    if module:
        runs = [r for r in runs if r.get('module') == module]

    # Group by module + prompt_version
    progress = {}
    for run in runs:
        mod = run.get('module', 'unknown')
        ver = run.get('prompt_version', 'v1')
        model = run.get('model', 'unknown')

        key = f"{mod}_{ver}_{model}"

        # Keep latest run for each combination
        if key not in progress or run.get('timestamp', '') > progress[key].get('timestamp', ''):
            progress[key] = run

    return progress


def print_progress_table(module: str = None):
    """Print progress table to console."""
    progress = get_progress_summary(module)

    if not progress:
        print("No progress data found.")
        return

    print("\n" + "="*80)
    print("PROGRESS SUMMARY")
    print("="*80)
    print(f"{'Module':<10} {'Version':<8} {'Model':<12} {'Pass%':<8} {'Match%':<8} {'Date'}")
    print("-"*80)

    for key, run in sorted(progress.items()):
        mod = run.get('module', '?')
        ver = run.get('prompt_version', '?')
        model = run.get('model', '?')
        pass_rate = run.get('pass_rate', 0)
        match_rate = run.get('match_rate', 0)
        ts = run.get('timestamp', '')[:10]

        print(f"{mod:<10} {ver:<8} {model:<12} {pass_rate:<8.1f} {match_rate:<8.1f} {ts}")

    print("="*80)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Track evaluation progress")
    parser.add_argument("--rebuild", action="store_true", help="Rebuild history from all results")
    parser.add_argument("--add", type=str, help="Add specific result file to history")
    parser.add_argument("--show", type=str, nargs='?', const='all', help="Show progress (optionally for specific module)")

    args = parser.parse_args()

    if args.rebuild:
        rebuild_history_from_results()
    elif args.add:
        add_run_to_history(Path(args.add))
    elif args.show:
        module = None if args.show == 'all' else args.show
        print_progress_table(module)
    else:
        # Default: rebuild and show
        rebuild_history_from_results()
        print_progress_table()
