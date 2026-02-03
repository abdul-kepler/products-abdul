#!/usr/bin/env python3
"""
Convert M11 experiment CSV with JSON columns to human-readable CSV format.
Similar to M09 format but showing hard_constraints output.

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
PROJECT_ROOT = Path(__file__).parent.parent.parent
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "experiment_results_readable" / "M11_IdentifyHardConstraints"


def convert_m11_csv(input_path: str, output_path: str = None) -> str:
    """
    Convert M11 experiment CSV to readable format (similar to M09).

    Args:
        input_path: Path to input CSV file
        output_path: Path to output CSV file (optional)

    Returns:
        Path to output file
    """
    input_path = Path(input_path)

    if output_path is None:
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
    headers = ['ASIN / Brand', 'Input Field', 'Input Value', 'Output Field', 'Output Value']

    for row in rows:
        asin = row.get('ASIN', '')
        brand = row.get('Brand', '')

        # Extract clean ASIN from record_id if needed (M11_sd01_B082XKDYY9 -> B082XKDYY9)
        if '_' in asin:
            parts = asin.split('_')
            clean_asin = parts[-1] if len(parts) > 0 else asin
        else:
            clean_asin = asin

        # Parse JSON columns
        input_data = parse_json_safe(row.get('input', '{}'))
        output_data = parse_json_safe(row.get('output', '{}'))

        # Collect input fields in order
        input_fields = []

        # Title first (truncated to 100 chars)
        title = input_data.get('title', '')
        if title:
            input_fields.append(('title', title[:100]))

        # Validated use
        validated_use = input_data.get('validated_use', '')
        if validated_use:
            input_fields.append(('validated_use', validated_use))

        # Taxonomy
        taxonomy = input_data.get('taxonomy', [])
        if isinstance(taxonomy, list):
            for i, item in enumerate(taxonomy[:3], 1):
                if isinstance(item, dict):
                    pt = item.get('product_type', '')
                    if pt:
                        input_fields.append((f'taxonomy_L{i}', pt))

        # Attribute table - variants
        attr_table = input_data.get('attribute_table', [])
        if isinstance(attr_table, list):
            for item in attr_table:
                if isinstance(item, dict):
                    attr_type = item.get('attribute_type', '')
                    attr_value = item.get('attribute_value', '')
                    if attr_type and attr_value:
                        input_fields.append((attr_type, attr_value))

        # Collect output fields - only hard_constraints
        output_fields = []
        hard_constraints = output_data.get('hard_constraints', [])
        if isinstance(hard_constraints, list):
            if hard_constraints:
                for hc in hard_constraints:
                    output_fields.append(('hard_constraint', str(hc)))
            else:
                output_fields.append(('hard_constraint', '(none)'))
        else:
            output_fields.append(('hard_constraint', str(hard_constraints) if hard_constraints else '(none)'))

        # Determine max rows needed for this product
        max_rows = max(len(input_fields), len(output_fields), 3)

        # Build rows for this product
        for i in range(max_rows):
            # First column: ASIN, URL, Brand (only first 3 rows)
            if i == 0:
                col1 = clean_asin
            elif i == 1:
                col1 = f"https://www.amazon.com/dp/{clean_asin}"
            elif i == 2:
                col1 = brand if brand else ''
            else:
                col1 = ''

            # Input columns
            if i < len(input_fields):
                input_field, input_value = input_fields[i]
            else:
                input_field, input_value = '', ''

            # Output columns
            if i < len(output_fields):
                output_field, output_value = output_fields[i]
            else:
                output_field, output_value = '', ''

            output_rows.append([col1, input_field, input_value, output_field, output_value])

        # Add empty separator row between products
        output_rows.append(['---', '', '', '', ''])

    # Write output CSV
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(output_rows)

    print(f"✓ {input_path.name} → {output_path.name} ({len(rows)} products)")

    return str(output_path)


def convert_all_m11_synthetic():
    """Convert all M11 synthetic experiment files."""
    m11_dir = PROJECT_ROOT / "experiment_results" / "M11_IdentifyHardConstraints"

    csv_files = sorted(m11_dir.glob("*gpt4omini_synthetic.csv"))

    print(f"Converting {len(csv_files)} M11 synthetic CSV files...")
    print(f"Output: {DEFAULT_OUTPUT_DIR}")
    print()

    for csv_file in csv_files:
        convert_m11_csv(str(csv_file))

    print()
    print("Done!")


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == '--all':
            convert_all_m11_synthetic()
        else:
            input_path = sys.argv[1]
            output_path = sys.argv[2] if len(sys.argv) > 2 else None
            convert_m11_csv(input_path, output_path)
    else:
        print("Usage:")
        print("  python csv_to_readable_m11.py <input_csv> [output_csv]")
        print("  python csv_to_readable_m11.py --all")
        print()
        print("Options:")
        print("  --all    Convert all M11 synthetic CSV files")
        sys.exit(1)


if __name__ == '__main__':
    main()
