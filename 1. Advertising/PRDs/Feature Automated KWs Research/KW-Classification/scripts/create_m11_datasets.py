#!/usr/bin/env python3
"""
Create M11 (IdentifyHardConstraints) synthetic datasets.

M11 requires:
- title, bullet_points, description (from M06 input)
- taxonomy (from M06 output)
- product_attributes (from M07 output)
- attribute_table (from M08 output)
- validated_use (from M10 output)
"""

import json
import csv
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
EXPERIMENT_RESULTS = PROJECT_ROOT / "experiment_results"
SYNTHETIC_DIR = PROJECT_ROOT / "datasets" / "synthetic"

# Module directories
M06_DIR = EXPERIMENT_RESULTS / "M06_GenerateProductTypeTaxonomy"
M07_DIR = EXPERIMENT_RESULTS / "M07_ExtractProductAttributes"
M08_DIR = EXPERIMENT_RESULTS / "M08_AssignAttributeRanks"
M10_DIR = EXPERIMENT_RESULTS / "M10_ValidatePrimaryIntendedUse"


def load_experiment_csv(filepath: Path) -> dict:
    """Load experiment CSV and return dict keyed by ASIN."""
    results = {}
    with open(filepath, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            asin = row['ASIN']
            # Clean ASIN (remove prefix like M10_sd01_)
            if '_' in asin and asin.startswith('M'):
                parts = asin.split('_')
                clean_asin = parts[-1]
            else:
                clean_asin = asin

            results[clean_asin] = {
                'input': json.loads(row['input']) if row['input'] else {},
                'output': json.loads(row['output']) if row['output'] else {},
                'brand': row.get('Brand', '')
            }
    return results


def find_experiment_file(directory: Path, sd_num: int, pattern_suffix: str) -> Path | None:
    """Find experiment file for given sd number."""
    sd_str = f"sd{sd_num:02d}"
    for f in directory.glob(f"*_{sd_str}_*{pattern_suffix}*.csv"):
        if 'readable' not in f.name:
            return f
    return None


def create_m11_datasets():
    """Create M11 datasets from M06, M07, M08, M10 results."""

    for sd_num in range(1, 23):
        sd_str = f"sd{sd_num:02d}"
        print(f"Processing {sd_str}...", end=" ")

        # Find experiment files
        m06_file = find_experiment_file(M06_DIR, sd_num, "gpt4omini_synthetic")
        m07_file = find_experiment_file(M07_DIR, sd_num, "gpt4omini_synthetic")
        m08_file = find_experiment_file(M08_DIR, sd_num, "gpt4omini_synthetic")
        m10_file = find_experiment_file(M10_DIR, sd_num, "gpt4omini_synthetic")

        if not all([m06_file, m07_file, m08_file, m10_file]):
            print(f"Missing files for {sd_str}")
            missing = []
            if not m06_file: missing.append("M06")
            if not m07_file: missing.append("M07")
            if not m08_file: missing.append("M08")
            if not m10_file: missing.append("M10")
            print(f"  Missing: {', '.join(missing)}")
            continue

        # Load data
        m06_data = load_experiment_csv(m06_file)
        m07_data = load_experiment_csv(m07_file)
        m08_data = load_experiment_csv(m08_file)
        m10_data = load_experiment_csv(m10_file)

        # Create M11 dataset
        records = []
        for asin in m06_data:
            if asin not in m07_data or asin not in m08_data or asin not in m10_data:
                continue

            m06_input = m06_data[asin]['input']
            m06_output = m06_data[asin]['output']
            m07_output = m07_data[asin]['output']
            m08_output = m08_data[asin]['output']
            m10_output = m10_data[asin]['output']

            # Get validated_use from M10
            validated_use = m10_output.get('validated_use', '')

            # Get taxonomy from M06
            taxonomy = m06_output.get('taxonomy', [])

            # Get attribute_table from M08
            attribute_table = m08_output.get('attribute_table', [])

            # Get product_attributes from M07
            product_attributes = {
                'variants': m07_output.get('variants', []),
                'use_cases': m07_output.get('use_cases', []),
                'audiences': m07_output.get('audiences', [])
            }

            record = {
                'id': f"M11_{sd_str}_{asin}",
                'input': {
                    'title': m06_input.get('title', ''),
                    'bullet_points': m06_input.get('bullet_points', ''),
                    'description': m06_input.get('description', ''),
                    'validated_use': validated_use,
                    'taxonomy': taxonomy,
                    'attribute_table': attribute_table,
                    'product_attributes': product_attributes
                },
                'expected': {
                    'hard_constraints': []
                },
                'metadata': {
                    'module_id': 'Module_11',
                    'asin': asin,
                    'sd_dataset': sd_str,
                    'source': 'synthetic_from_m06_m07_m08_m10'
                }
            }
            records.append(record)

        # Write dataset
        output_file = SYNTHETIC_DIR / f"m11_{sd_str}_identify_hard_constraints.jsonl"
        with open(output_file, 'w', encoding='utf-8') as f:
            for record in records:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')

        print(f"{len(records)} records")

    print("\nDone!")


if __name__ == "__main__":
    create_m11_datasets()
