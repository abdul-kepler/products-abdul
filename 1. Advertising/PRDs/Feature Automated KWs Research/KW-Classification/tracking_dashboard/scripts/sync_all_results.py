#!/usr/bin/env python3
"""
Sync All Results - Unified synchronization of ALL experiment results to dashboard.

Handles:
- Judge results (LLM-as-a-Judge evaluations) from evaluation_experimentV5/
- CSV experiment results with meta.json from experiment_results/
- ALL modules including M01 (entity extraction) and binary classifiers

Usage:
    python sync_all_results.py              # Sync all new results
    python sync_all_results.py --dry-run    # Show what would be synced
    python sync_all_results.py --force      # Re-sync all (ignore existing)
"""

import json
import yaml
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
DATA_DIR = PROJECT_DIR / "data"
DASHBOARDS_DIR = PROJECT_DIR / "dashboards"

# Source directories
EVAL_DIR = PROJECT_DIR.parent / "evaluation_KD" / "evaluation_experimentV5"
JUDGE_RESULTS_DIR = EVAL_DIR / "judge_results"
EXPERIMENT_RESULTS_DIR = PROJECT_DIR.parent / "experiment_results"

# Module folder mapping
MODULE_FOLDERS = {
    'm01': 'M01_ExtractOwnBrandEntities',
    'm01a': 'M01A_ExtractOwnBrandVariations_PathB',
    'm01b': 'M01B_ExtractBrandRelatedTerms_PathB',
    'm02': 'M02_ClassifyOwnBrandKeywords',
    'm02b': 'M02B_ClassifyOwnBrandKeywords_PathB',
    'm04': 'M04_ClassifyCompetitorBrandKeywords',
    'm04b': 'M04B_ClassifyCompetitorBrandKeywords_PathB',
    'm05': 'M05_ClassifyNonBrandedKeywords',
    'm05b': 'M05B_ClassifyNonBrandedKeywords_PathB',
    'm06': 'M06_GenerateProductTypeTaxonomy',
    'm07': 'M07_ExtractProductAttributes',
    'm08': 'M08_AssignAttributeRanks',
    'm09': 'M09_IdentifyPrimaryIntendedUse',
    'm10': 'M10_ValidatePrimaryIntendedUse',
    'm11': 'M11_IdentifyHardConstraints',
    'm12': 'M12_HardConstraintViolationCheck',
    'm12b': 'M12B_HardConstraintViolationCheck_PathB',
    'm13': 'M13_ProductTypeCheck',
    'm14': 'M14_PrimaryUseCheckSameType',
    'm15': 'M15_SubstituteCheck',
    'm16': 'M16_ComplementaryCheck',
}

# Primary rubric for each module - used to calculate match_rate (main task success metric)
# Must match actual rubric_id values from judge result JSON files
PRIMARY_RUBRIC_MAP = {
    'm01': 'M01_brand_extracted',
    'm01a': 'M01a_has_variations',
    'm01b': 'M01b_sub_brands_found',
    'm02': 'M02_correct_classification',
    'm02b': 'M02_correct_classification',  # Shared rubrics with m02
    'm04': 'M04_correct_classification',
    'm04b': 'M04_correct_classification',  # Shared rubrics with m04
    'm05': 'M05_correct_classification',
    'm05b': 'M05_correct_classification',  # Shared rubrics with m05
    'm06': 'M06_product_type_accurate',
    'm07': 'M07_attributes_from_listing',
    'm08': 'M08_ranks_assigned',
    'm09': 'M09_captures_core_purpose',
    'm10': 'M10_invalid_correctly_flagged',
    'm11': 'M11_constraints_non_negotiable',
    'm12': 'M12_correct_classification',
    'm12b': 'M12_correct_classification',  # Shared rubrics with m12
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


def calculate_match_rate(evaluations: List, module: str) -> float:
    """Calculate match_rate based on primary rubric pass rate."""
    primary_rubric = get_primary_rubric(module)
    if not primary_rubric:
        return 0.0

    match_count = sum(1 for ev in evaluations
                     if ev.get('verdict') == 'PASS' and
                     ev.get('rubric_id', '') == primary_rubric)
    total_count = sum(1 for ev in evaluations
                     if ev.get('rubric_id', '') == primary_rubric)
    return (match_count / total_count * 100) if total_count > 0 else 0.0


def load_progress_history() -> Dict:
    """Load existing progress history."""
    history_file = DATA_DIR / "progress_history.yaml"
    if history_file.exists():
        with open(history_file) as f:
            return yaml.safe_load(f) or {'runs': []}
    return {'runs': []}


def save_progress_history(history: Dict):
    """Save progress history."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    history_file = DATA_DIR / "progress_history.yaml"
    with open(history_file, 'w') as f:
        yaml.dump(history, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


def get_existing_run_ids(history: Dict) -> Set[str]:
    """Get set of existing run IDs."""
    return {r.get('run_id') for r in history.get('runs', []) if r.get('run_id')}


def normalize_model_name(model: str) -> str:
    """Normalize model name for consistent display."""
    model = model.lower().replace('-', '').replace('.', '').replace(' ', '')
    mappings = {
        'gpt4omini': 'gpt-4o-mini',
        'gpt4o': 'gpt-4o',
        'gpt5': 'gpt-5',
        'gemini20flash': 'gemini-2.0-flash',
        'gemini20flashexp': 'gemini-2.0-flash',
    }
    return mappings.get(model, model)


def extract_version_from_string(s: str) -> str:
    """Extract version like v1, v2, v3 from string."""
    match = re.search(r'[_\s]v(\d+)[_\s]', s, re.I)
    if match:
        return f'v{match.group(1)}'
    match = re.search(r'_V(\d+)_', s)
    if match:
        return f'v{match.group(1)}'
    return 'v1'


def sync_judge_results(history: Dict, existing_ids: Set[str], dry_run: bool = False) -> int:
    """Sync judge results from evaluation_experimentV5/judge_results/."""
    if not JUDGE_RESULTS_DIR.exists():
        print(f"  Judge results dir not found: {JUDGE_RESULTS_DIR}")
        return 0

    new_count = 0
    json_files = sorted(JUDGE_RESULTS_DIR.glob("*_judge_*.json"))

    for json_file in json_files:
        # Skip invalid files
        if 'invalid' in str(json_file).lower():
            continue

        run_id = json_file.stem

        # Check if already exists
        if run_id in existing_ids:
            continue

        try:
            with open(json_file) as f:
                data = json.load(f)

            # Handle both old and new formats
            evaluations = data.get('evaluations', [])

            if 'metadata' in data:
                meta = data['metadata']
                summary = data.get('summary', {})
                module = meta.get('module', run_id.split('_judge')[0])
                prompt_version = meta.get('prompt_version', 'v1')
                model = meta.get('model', 'unknown')
                timestamp = meta.get('timestamp', datetime.now().isoformat())
                data_source = meta.get('data_source', '')
                pass_rate = meta.get('pass_rate', 0)
                match_rate = meta.get('match_rate', data.get('match_rate', 0))
            else:
                # New format - metadata at top level
                summary = data.get('summary', {})
                module = data.get('module', run_id.split('_judge')[0])
                prompt_version = extract_version_from_string(module) or 'v1'
                model = normalize_model_name(data.get('model', 'unknown'))
                timestamp = data.get('timestamp', datetime.now().isoformat())
                data_source = data.get('data_source', '')
                pass_rate = data.get('pass_rate', 0)
                match_rate = data.get('match_rate', 0)

            # Calculate pass rate if not provided
            total = summary.get('pass', 0) + summary.get('fail', 0) + summary.get('error', 0)
            if total > 0 and pass_rate == 0:
                pass_rate = summary.get('pass', 0) / total * 100

            # Calculate match_rate from evaluations if not provided
            if match_rate == 0 and evaluations:
                match_rate = calculate_match_rate(evaluations, module)

            run_entry = {
                'run_id': run_id,
                'module': module.split('_')[0] if '_' in module else module,  # m01_v5 -> m01
                'prompt_version': prompt_version,
                'model': model,
                'pass_rate': round(pass_rate, 1),
                'match_rate': round(match_rate, 1) if match_rate else 0,
                'summary': summary,
                'timestamp': timestamp,
                'data_source': data_source,
                'source_type': 'judge',
                'rubrics_version': data.get('rubrics_version', 'v5'),
            }

            if dry_run:
                print(f"    [DRY-RUN] Would add: {run_id}")
            else:
                history['runs'].append(run_entry)
                print(f"    + {run_id} (pass_rate: {pass_rate:.1f}%)")

            new_count += 1
            existing_ids.add(run_id)

        except Exception as e:
            print(f"    ! Error parsing {json_file.name}: {e}")

    return new_count


# Modules that can be scored directly from CSV (binary classifiers)
BINARY_MODULES = {'m02', 'm02b', 'm04', 'm04b', 'm05', 'm05b', 'm12', 'm12b', 'm13', 'm14', 'm15', 'm16'}


def sync_experiment_results(history: Dict, existing_ids: Set[str], dry_run: bool = False) -> int:
    """Sync experiment results from experiment_results/ folders.

    Only syncs BINARY CLASSIFIER modules since they can be scored without LLM judge.
    Non-binary modules (M01, M06-M11) need LLM-as-a-Judge evaluation, so only judge results matter.
    """
    if not EXPERIMENT_RESULTS_DIR.exists():
        print(f"  Experiment results dir not found: {EXPERIMENT_RESULTS_DIR}")
        return 0

    new_count = 0

    for module_id, folder_name in MODULE_FOLDERS.items():
        # Skip non-binary modules - they need judge evaluation
        if module_id not in BINARY_MODULES:
            continue

        folder = EXPERIMENT_RESULTS_DIR / folder_name
        if not folder.exists():
            continue

        # Find all CSV files with meta.json
        for csv_file in sorted(folder.glob("*.csv"), key=lambda f: f.stat().st_mtime, reverse=True):
            meta_file = csv_file.with_suffix('.meta.json')

            # Generate run_id from filename
            # M01_V5_ExtractOwnBrandEntities_v5_210126_gpt4omini.csv -> m01_v5_gpt4omini_210126
            filename = csv_file.stem

            # Extract version and model from filename
            version = extract_version_from_string(filename)

            # Extract model
            model = 'gpt-4o-mini'  # default
            model_patterns = [
                (r'gpt[-_]?5', 'gpt-5'),
                (r'gpt[-_]?4o[-_]?mini|gpt4omini', 'gpt-4o-mini'),
                (r'gpt[-_]?4o|gpt4o', 'gpt-4o'),
                (r'gemini[-_]?2\.?0[-_]?flash|gemini20flash', 'gemini-2.0-flash'),
            ]
            for pattern, model_name in model_patterns:
                if re.search(pattern, filename, re.I):
                    model = model_name
                    break

            # Extract date from filename (e.g., 210126)
            date_match = re.search(r'_(\d{6})_', filename)
            date_str = date_match.group(1) if date_match else ''

            # Create unique run_id
            model_short = model.replace('-', '').replace('.', '')[:10]
            run_id = f"{module_id}_{version}_{model_short}_{date_str}".rstrip('_')

            if run_id in existing_ids:
                continue

            # Load meta.json if exists
            meta = {}
            if meta_file.exists():
                try:
                    with open(meta_file) as f:
                        meta = json.load(f)
                except Exception:
                    pass

            # Count records in CSV
            records_count = meta.get('records_count', 0)
            if records_count == 0:
                try:
                    with open(csv_file) as f:
                        records_count = sum(1 for _ in f) - 1  # minus header
                except Exception:
                    pass

            run_entry = {
                'run_id': run_id,
                'module': module_id,
                'prompt_version': version,
                'model': model,
                'records_count': records_count,
                'dataset_name': meta.get('dataset_name', ''),
                'dataset_version': meta.get('dataset_version', ''),
                'timestamp': meta.get('downloaded_at', datetime.fromtimestamp(csv_file.stat().st_mtime).isoformat()),
                'source_file': csv_file.name,
                'source_type': 'experiment',
            }

            if dry_run:
                print(f"    [DRY-RUN] Would add: {run_id} ({records_count} records)")
            else:
                history['runs'].append(run_entry)
                print(f"    + {run_id} ({records_count} records)")

            new_count += 1
            existing_ids.add(run_id)

    return new_count


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Sync All Results")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be synced without making changes")
    parser.add_argument("--force", action="store_true", help="Re-sync all results (ignore existing)")
    args = parser.parse_args()

    print("=" * 60)
    print("🔄 Sync All Results")
    print("=" * 60)
    print(f"Sources:")
    print(f"  Judge results: {JUDGE_RESULTS_DIR}")
    print(f"  Experiments:   {EXPERIMENT_RESULTS_DIR}")
    print(f"Target:")
    print(f"  Data dir:      {DATA_DIR}")

    if args.dry_run:
        print("\n⚠️  DRY-RUN MODE - No changes will be made")

    # Load existing history
    history = load_progress_history()
    existing_ids = get_existing_run_ids(history) if not args.force else set()

    print(f"\nExisting runs: {len(existing_ids)}")

    # Sync judge results
    print("\n📊 Syncing Judge Results...")
    judge_count = sync_judge_results(history, existing_ids, args.dry_run)

    # Sync experiment results
    print("\n📁 Syncing Experiment Results...")
    exp_count = sync_experiment_results(history, existing_ids, args.dry_run)

    # Save
    if not args.dry_run and (judge_count > 0 or exp_count > 0):
        save_progress_history(history)

    # Summary
    print("\n" + "=" * 60)
    print("📈 Summary")
    print("=" * 60)
    print(f"  Judge results added:      {judge_count}")
    print(f"  Experiment results added: {exp_count}")
    print(f"  Total runs in history:    {len(history.get('runs', []))}")

    if args.dry_run:
        print("\n⚠️  DRY-RUN: No changes were made. Run without --dry-run to apply.")
    elif judge_count > 0 or exp_count > 0:
        print("\n✅ Sync complete! Run 'update_dashboard.py' to regenerate dashboards.")
    else:
        print("\n✅ Already up to date!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
