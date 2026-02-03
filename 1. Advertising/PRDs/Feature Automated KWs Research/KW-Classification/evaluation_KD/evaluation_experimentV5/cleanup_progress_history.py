#!/usr/bin/env python3
"""Clean up progress_history.yaml: remove duplicates and fix model names."""

import yaml
from pathlib import Path
from collections import defaultdict

HISTORY_FILE = Path(__file__).parent / "progress_history.yaml"

# Correct models based on MODULE_CSV_MAP (what generated the experiment data)
CORRECT_MODELS = {
    'm01': 'gpt-5',          # V3 prompt + GPT-5
    'm01_v2': 'gpt-4o-mini', # V2 dataset, prompt v3
    'm01_v1': 'gpt-4o-mini', # V1 baseline
    'm01a': 'gpt-4o-mini',
    'm01a_v2': 'gpt-5',      # V2 prompt + GPT-5
    'm01b': 'gpt-4o-mini',
    'm02': 'gpt-4o-mini',
    'm02b': 'gpt-4o-mini',
    'm04': 'gpt-4o-mini',
    'm04b': 'gpt-4o-mini',
    'm05': 'gpt-4o-mini',
    'm05b': 'gpt-4o-mini',
    'm06_gd': 'gpt-4o-mini',
    'm06_sd': 'gpt-4o-mini',
    'm07_gd': 'gpt-4o-mini',
    'm07_sd': 'gpt-4o-mini',
    'm08': 'gpt-4o-mini',
    'm08_sd': 'gpt-4o-mini',
    'm08_v2': 'gpt-4o-mini',
    'm08_v2_sd': 'gpt-4o-mini',
    'm09': 'gpt-4o-mini',
    'm10': 'gpt-4o-mini',
    'm11': 'gpt-4o-mini',
    'm12': 'gpt-4o-mini',
    'm13': 'gpt-4o-mini',
    'm14': 'gpt-4o-mini',
    'm15': 'gpt-4o-mini',
    'm16': 'gpt-4o-mini',
}


def main():
    print("Loading progress_history.yaml...")
    with open(HISTORY_FILE, 'r') as f:
        history = yaml.safe_load(f)

    runs = history.get('runs', [])
    print(f"Total runs before cleanup: {len(runs)}")

    # Group runs by module
    module_runs = defaultdict(list)
    for run in runs:
        module = run.get('module', '')
        module_runs[module].append(run)

    print(f"\nModules found: {len(module_runs)}")

    # Show duplicates
    print("\n=== DUPLICATE ANALYSIS ===")
    for module, module_list in sorted(module_runs.items()):
        if len(module_list) > 1:
            print(f"  {module}: {len(module_list)} runs (keeping latest)")
            for r in module_list:
                print(f"    - {r['run_id']} | {r.get('model', '?')} | {r.get('pass_rate', '?')}%")

    # Keep only latest run per module
    cleaned_runs = []
    for module, module_list in module_runs.items():
        # Sort by timestamp descending (latest first)
        sorted_runs = sorted(module_list, key=lambda x: x.get('timestamp', ''), reverse=True)
        latest_run = sorted_runs[0]

        # Fix model based on CORRECT_MODELS
        correct_model = CORRECT_MODELS.get(module, latest_run.get('model', 'gpt-4o-mini'))
        original_model = latest_run.get('model', '?')
        if original_model != correct_model:
            print(f"  Fixing {module} model: {original_model} -> {correct_model}")
        latest_run['model'] = correct_model

        cleaned_runs.append(latest_run)

    # Sort by module name
    cleaned_runs.sort(key=lambda x: x.get('module', ''))

    print(f"\n=== CLEANUP SUMMARY ===")
    print(f"Runs before: {len(runs)}")
    print(f"Runs after: {len(cleaned_runs)}")
    print(f"Removed: {len(runs) - len(cleaned_runs)} duplicates")

    # Show final state
    print("\n=== FINAL MODULES ===")
    for run in cleaned_runs:
        print(f"  {run['module']:12} | {run['model']:12} | {run.get('pass_rate', '?'):.1f}%")

    # Backup original
    backup_file = HISTORY_FILE.with_suffix('.yaml.backup')
    print(f"\nBacking up to: {backup_file}")
    with open(backup_file, 'w') as f:
        yaml.dump(history, f, default_flow_style=False, allow_unicode=True)

    # Save cleaned
    cleaned_history = {'runs': cleaned_runs}
    print(f"Saving cleaned history...")
    with open(HISTORY_FILE, 'w') as f:
        yaml.dump(cleaned_history, f, default_flow_style=False, allow_unicode=True)

    print("\nDone!")


if __name__ == "__main__":
    main()
