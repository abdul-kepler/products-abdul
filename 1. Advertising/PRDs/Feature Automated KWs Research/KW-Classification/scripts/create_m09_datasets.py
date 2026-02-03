#!/usr/bin/env python3
"""
Create M09 synthetic datasets from M06, M07, M08 results.

M09 inputs:
- title, bullet_points, description (from original dataset)
- taxonomy (from M06 output)
- attribute_table (from M08 output)
- product_attributes (from M07 output - variants, use_cases, audiences)
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
        # Find column indices
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


def create_m09_datasets():
    """Create M09 datasets for all SD files."""

    m06_dir = EXPERIMENT_RESULTS / "M06_GenerateProductTypeTaxonomy"
    m07_dir = EXPERIMENT_RESULTS / "M07_ExtractProductAttributes"
    m08_dir = EXPERIMENT_RESULTS / "M08_AssignAttributeRanks"

    total_records = 0

    for sd_num in range(1, 23):
        sd_str = f"sd{sd_num:02d}"

        # Find experiment files
        m06_files = list(m06_dir.glob(f"*_{sd_str}_*_gpt4omini_synthetic.csv"))
        m07_files = list(m07_dir.glob(f"*_{sd_str}_*_gpt4omini_synthetic.csv"))
        m08_files = list(m08_dir.glob(f"*_{sd_str}_*_gpt4omini_synthetic.csv"))

        if not m06_files or not m07_files or not m08_files:
            print(f"⚠ SD{sd_num:02d}: Missing experiment results")
            continue

        # Load results
        m06_data = load_experiment_csv(m06_files[0])
        m07_data = load_experiment_csv(m07_files[0])
        m08_data = load_experiment_csv(m08_files[0])

        # Create M09 dataset
        output_file = SYNTHETIC_DIR / f"m09_sd{sd_num:02d}_identify_primary_intended_use.jsonl"
        records_written = 0

        with open(output_file, 'w', encoding='utf-8') as f:
            for asin in m06_data:
                if asin not in m07_data or asin not in m08_data:
                    continue

                m06_output = m06_data[asin]['output']
                m07_output = m07_data[asin]['output']
                m08_input = m08_data[asin]['input']
                m08_output = m08_data[asin]['output']

                # Get taxonomy
                taxonomy = m06_output.get('taxonomy', [])

                # Get attribute_table from M08 output
                attribute_table = m08_output.get('attribute_table', [])

                # Get product_attributes from M07
                product_attributes = {
                    'variants': m07_output.get('variants', []),
                    'use_cases': m07_output.get('use_cases', []),
                    'audiences': m07_output.get('audiences', [])
                }

                # Build M09 input
                m09_input = {
                    'title': m08_input.get('title', ''),
                    'bullet_points': m08_input.get('bullet_points', ''),
                    'description': m08_input.get('description', ''),
                    'taxonomy': taxonomy,
                    'attribute_table': attribute_table,
                    'product_attributes': product_attributes
                }

                record = {
                    'id': f"M9_{sd_str}_{asin}",
                    'input': m09_input,
                    'expected': {}  # No expected output for synthetic
                }

                f.write(json.dumps(record, ensure_ascii=False) + '\n')
                records_written += 1

        total_records += records_written
        print(f"✓ SD{sd_num:02d}: {records_written} records")

    print(f"\nTotal: {total_records} records across 22 datasets")


if __name__ == "__main__":
    create_m09_datasets()
