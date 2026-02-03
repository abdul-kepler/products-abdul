#!/usr/bin/env python3
"""Deduplicate progress_history.yaml - keep entry with best match_rate."""

import yaml
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

def main():
    history_file = DATA_DIR / "progress_history.yaml"

    with open(history_file) as f:
        history = yaml.safe_load(f) or {'runs': []}

    runs = history.get('runs', [])
    print(f"Before: {len(runs)} entries")

    # Deduplicate: keep entry with highest match_rate for each run_id
    run_map = {}
    for run in runs:
        run_id = run.get('run_id')
        if not run_id:
            continue

        existing = run_map.get(run_id)
        if not existing:
            run_map[run_id] = run
        else:
            # Keep the one with higher match_rate
            existing_mr = existing.get('match_rate', 0) or 0
            new_mr = run.get('match_rate', 0) or 0
            if new_mr > existing_mr:
                run_map[run_id] = run
                print(f"  Replaced {run_id}: match_rate {existing_mr} -> {new_mr}")

    # Convert back to list
    deduped_runs = list(run_map.values())
    print(f"After: {len(deduped_runs)} entries")
    print(f"Removed: {len(runs) - len(deduped_runs)} duplicates")

    # Save
    history['runs'] = deduped_runs
    with open(history_file, 'w') as f:
        yaml.dump(history, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print(f"Saved to {history_file}")

if __name__ == "__main__":
    main()
