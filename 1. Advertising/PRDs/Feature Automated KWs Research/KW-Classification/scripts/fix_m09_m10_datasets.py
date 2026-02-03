#!/usr/bin/env python3
"""Fix M09 and M10 datasets to include expected and metadata fields."""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
SYNTHETIC_DIR = PROJECT_ROOT / "datasets" / "synthetic"

def fix_m09_datasets():
    """Add expected and metadata to M09 datasets."""
    for sd_num in range(1, 23):
        sd_str = f"sd{sd_num:02d}"
        filepath = SYNTHETIC_DIR / f"m09_{sd_str}_identify_primary_intended_use.jsonl"

        if not filepath.exists():
            print(f"⚠ M09 {sd_str}: file not found")
            continue

        records = []
        with open(filepath, encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    # Extract ASIN from ID (M9_sd01_B082XKDYY9 -> B082XKDYY9)
                    asin = record['id'].split('_')[-1] if '_' in record['id'] else ''

                    # Add expected (empty structure for M09 output)
                    record['expected'] = {
                        'primary_use': '',
                        'confidence': 0.0,
                        'reasoning': ''
                    }

                    # Add metadata
                    record['metadata'] = {
                        'module_id': 'Module_09',
                        'asin': asin,
                        'sd_dataset': sd_str,
                        'source': 'synthetic_from_m06_m07_m08'
                    }
                    records.append(record)

        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            for record in records:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')

        print(f"✓ M09 {sd_str}: {len(records)} records fixed")


def fix_m10_datasets():
    """Add expected and metadata to M10 datasets."""
    for sd_num in range(1, 23):
        sd_str = f"sd{sd_num:02d}"
        filepath = SYNTHETIC_DIR / f"m10_{sd_str}_validate_primary_intended_use.jsonl"

        if not filepath.exists():
            print(f"⚠ M10 {sd_str}: file not found")
            continue

        records = []
        with open(filepath, encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    # Extract ASIN from ID (M10_sd01_B082XKDYY9 -> B082XKDYY9)
                    asin = record['id'].split('_')[-1] if '_' in record['id'] else ''

                    # Add expected (empty structure for M10 output)
                    record['expected'] = {
                        'validated_use': '',
                        'action': '',
                        'issues_found': [],
                        'confidence': 0.0,
                        'reasoning': ''
                    }

                    # Add metadata
                    record['metadata'] = {
                        'module_id': 'Module_10',
                        'asin': asin,
                        'sd_dataset': sd_str,
                        'source': 'synthetic_from_m06_m07_m08_m09'
                    }
                    records.append(record)

        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            for record in records:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')

        print(f"✓ M10 {sd_str}: {len(records)} records fixed")


if __name__ == "__main__":
    print("Fixing M09 datasets...")
    fix_m09_datasets()
    print("\nFixing M10 datasets...")
    fix_m10_datasets()
    print("\nDone!")
