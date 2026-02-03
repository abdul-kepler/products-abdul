#!/usr/bin/env python3
"""
Create M10 synthetic datasets from M09 results.

M10 inputs:
- primary_use (from M09 output)
- title, bullet_points, description (from original)
- taxonomy (from M06)
- attribute_table (from M08)
- product_attributes (from M07)
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
EXPERIMENT_RESULTS = PROJECT_ROOT / "experiment_results"
SYNTHETIC_DIR = PROJECT_ROOT / "datasets" / "synthetic"

def load_experiment_csv(filepath: Path) -> dict[str, dict]:
    """Load experiment results and index by ASIN."""
    results = {}
    with open(filepath, encoding='utf-8') as f:
        header = f.readline().strip().split(',')
        asin_idx = header.index('ASIN')
        output_idx = header.index('output')
        input_idx = header.index('input')

        for line in f:
            if not line.strip():
                continue
            # Parse CSV line (handle JSON with commas)
            parts = []
            in_quotes = False
            current = ""
            for char in line:
                if char == '"':
                    in_quotes = not in_quotes
                    current += char
                elif char == ',' and not in_quotes:
                    parts.append(current)
                    current = ""
                else:
                    current += char
            parts.append(current.rstrip('\n'))

            if len(parts) > max(asin_idx, output_idx, input_idx):
                asin = parts[asin_idx]
                try:
                    output = json.loads(parts[output_idx].strip('"').replace('""', '"'))
                    input_data = json.loads(parts[input_idx].strip('"').replace('""', '"'))
                except json.JSONDecodeError:
                    continue
                results[asin] = {'output': output, 'input': input_data}
    return results


def create_m10_datasets():
    """Create M10 datasets for all SD files."""

    m09_dir = EXPERIMENT_RESULTS / "M09_IdentifyPrimaryIntendedUse"

    total_records = 0

    for sd_num in range(1, 23):
        sd_str = f"sd{sd_num:02d}"

        # Find M09 experiment files
        m09_files = list(m09_dir.glob(f"*_{sd_str}_*_gpt4omini_synthetic.csv"))

        if not m09_files:
            print(f"⚠ SD{sd_num:02d}: Missing M09 experiment results")
            continue

        # Load M09 results
        m09_data = load_experiment_csv(m09_files[0])

        # Create M10 dataset
        output_file = SYNTHETIC_DIR / f"m10_sd{sd_num:02d}_validate_primary_intended_use.jsonl"
        records_written = 0

        with open(output_file, 'w', encoding='utf-8') as f:
            for asin, data in m09_data.items():
                m09_output = data['output']
                m09_input = data['input']

                # Get primary_use from M09 output
                primary_use = m09_output.get('primary_use', '')

                if not primary_use:
                    continue

                # Build M10 input
                m10_input = {
                    'primary_use': primary_use,
                    'title': m09_input.get('title', ''),
                    'bullet_points': m09_input.get('bullet_points', ''),
                    'description': m09_input.get('description', ''),
                    'taxonomy': m09_input.get('taxonomy', []),
                    'attribute_table': m09_input.get('attribute_table', []),
                    'product_attributes': m09_input.get('product_attributes', {})
                }

                record = {
                    'id': f"M10_{sd_str}_{asin}",
                    'input': m10_input,
                    'expected': {}
                }

                f.write(json.dumps(record, ensure_ascii=False) + '\n')
                records_written += 1

        total_records += records_written
        print(f"✓ SD{sd_num:02d}: {records_written} records")

    print(f"\nTotal: {total_records} records across 22 datasets")


if __name__ == "__main__":
    create_m10_datasets()
