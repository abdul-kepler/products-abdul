#!/usr/bin/env python3
"""
Remove duplicate entries from progress_history.yaml.
Keep the entry with highest pass_rate for each unique combination of:
- module (base name without version suffix)
- prompt_version
- model
- data_source (basename only)
"""

import yaml
from pathlib import Path
from collections import defaultdict
import re

DATA_FILE = Path(__file__).parent.parent / "data" / "progress_history.yaml"


def normalize_module(module: str) -> str:
    """Get base module name without version/model suffixes."""
    # m01_v3_gemini -> m01
    # m01_v4_gpt4omini -> m01
    base = re.sub(r'_v\d+.*$', '', module.lower())
    base = re.sub(r'_gemini.*$', '', base)
    base = re.sub(r'_gpt.*$', '', base)
    base = re.sub(r'_sd$|_gd$', '', base)
    return base


def get_dataset_key(data_source: str) -> str:
    """Get consistent key from data_source path."""
    if not data_source:
        return ''
    # Get basename without path
    basename = Path(data_source).stem  # Remove .csv
    return basename


def main():
    print(f"Reading {DATA_FILE}...")

    with open(DATA_FILE) as f:
        data = yaml.safe_load(f)

    runs = data.get('runs', [])
    print(f"Total entries: {len(runs)}")

    # Group by unique key
    groups = defaultdict(list)
    for entry in runs:
        module = normalize_module(entry.get('module', ''))
        version = entry.get('prompt_version', 'v1')
        model = entry.get('model', '')
        dataset = get_dataset_key(entry.get('data_source', ''))

        key = (module, version, model, dataset)
        groups[key].append(entry)

    # Find duplicates and keep best
    cleaned = []
    removed = []

    for key, entries in groups.items():
        if len(entries) == 1:
            cleaned.append(entries[0])
        else:
            # Multiple entries - keep the one with highest pass_rate
            # If same pass_rate, keep the latest timestamp
            sorted_entries = sorted(entries,
                key=lambda x: (x.get('pass_rate', 0), x.get('timestamp', '')),
                reverse=True
            )
            best = sorted_entries[0]
            cleaned.append(best)

            # Track removed entries
            for e in sorted_entries[1:]:
                removed.append({
                    'run_id': e.get('run_id'),
                    'module': e.get('module'),
                    'pass_rate': e.get('pass_rate'),
                    'kept': best.get('run_id')
                })

    print(f"\nDuplicates found: {len(removed)}")
    if removed:
        print("\nRemoved entries:")
        for r in removed:
            print(f"  - {r['run_id']} ({r['module']}, {r['pass_rate']}%) -> kept {r['kept']}")

    # Sort cleaned by module, then by timestamp desc
    cleaned.sort(key=lambda x: (
        normalize_module(x.get('module', '')),
        x.get('timestamp', '')
    ), reverse=True)

    # Regroup by base module for display
    by_module = defaultdict(list)
    for entry in cleaned:
        base = normalize_module(entry.get('module', ''))
        by_module[base].append(entry)

    print(f"\nCleaned entries by module:")
    for module in sorted(by_module.keys()):
        entries = by_module[module]
        print(f"  {module}: {len(entries)} entries")

    # Save
    data['runs'] = cleaned

    with open(DATA_FILE, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print(f"\nSaved {len(cleaned)} entries to {DATA_FILE}")
    return 0


if __name__ == "__main__":
    exit(main())
