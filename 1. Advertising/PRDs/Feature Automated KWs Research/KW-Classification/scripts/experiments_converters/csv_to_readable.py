#!/usr/bin/env python3
"""
Convert experiment CSV with JSON columns to human-readable CSV format.

Input:  CSV with JSON in 'input' and 'output' columns
Output: CSV with each field/value on separate row, ASIN+URL+Brand shown once per product
"""

import csv
import json
import sys
from pathlib import Path


def parse_json_safe(value: str) -> dict:
    """Safely parse JSON string, return empty dict on failure."""
    if not value or value == '""':
        return {}
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return {}


# Default output directory (relative to project root)
DEFAULT_OUTPUT_DIR = Path(__file__).parent.parent.parent / "experiment_results_readable"


def convert_experiment_csv(input_path: str, output_path: str = None) -> str:
    """
    Convert experiment CSV to readable format.

    Args:
        input_path: Path to input CSV file
        output_path: Path to output CSV file (optional, saves to experiment_results_readable/)

    Returns:
        Path to output file
    """
    input_path = Path(input_path)

    if output_path is None:
        # Save to experiment_results_readable/ folder in project root
        DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_path = DEFAULT_OUTPUT_DIR / f"{input_path.stem}_readable.csv"
    else:
        output_path = Path(output_path)

    # Read input CSV
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Prepare output
    output_rows = []
    headers = ['ASIN / Brand', 'Input Field', 'Input Value', 'Output Type', 'Output Value']

    for row in rows:
        asin = row.get('ASIN', '')
        brand = row.get('Brand', '')

        # Parse JSON columns
        input_data = parse_json_safe(row.get('input', '{}'))
        output_data = parse_json_safe(row.get('output', '{}'))

        # Collect ALL input fields (including empty), with priority ordering
        priority_fields = ['title', 'category_root', 'category_sub', 'product_type', 'bullet_points']

        # First add priority fields in order
        input_fields = []
        for field in priority_fields:
            if field in input_data:
                value = input_data[field]
                display_value = str(value) if value and value != '""' else '—'
                input_fields.append((field, display_value))

        # Then add remaining fields
        for field, value in input_data.items():
            if field not in priority_fields:
                display_value = str(value) if value and value != '""' else '—'
                input_fields.append((field, display_value))

        # Collect output fields
        output_fields = []
        for output_type in ['audiences', 'use_cases', 'variants']:
            items = output_data.get(output_type, [])
            if isinstance(items, list):
                for item in items:
                    if item and item != '-':
                        output_fields.append((output_type, str(item)))

        # Determine max rows needed for this product
        max_rows = max(len(input_fields), len(output_fields), 3)  # min 3 for ASIN, URL, Brand

        # Build rows for this product
        for i in range(max_rows):
            # First column: ASIN, URL, Brand (only first 3 rows)
            if i == 0:
                col1 = asin
            elif i == 1:
                col1 = f"https://www.amazon.com/dp/{asin}"
            elif i == 2:
                col1 = brand
            else:
                col1 = ''

            # Input columns
            if i < len(input_fields):
                input_field, input_value = input_fields[i]
            else:
                input_field, input_value = '', ''

            # Output columns
            if i < len(output_fields):
                output_type, output_value = output_fields[i]
            else:
                output_type, output_value = '', ''

            output_rows.append([col1, input_field, input_value, output_type, output_value])

        # Add empty separator row between products
        output_rows.append(['---', '', '', '', ''])

    # Write output CSV
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(output_rows)

    print(f"Converted: {input_path}")
    print(f"Output:    {output_path}")
    print(f"Products:  {len(rows)}")

    return str(output_path)


def main():
    if len(sys.argv) < 2:
        print("Usage: python csv_to_readable.py <input_csv> [output_csv]")
        print("\nExample:")
        print("  python csv_to_readable.py experiment.csv")
        print("  python csv_to_readable.py experiment.csv readable_output.csv")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    convert_experiment_csv(input_path, output_path)


if __name__ == '__main__':
    main()
