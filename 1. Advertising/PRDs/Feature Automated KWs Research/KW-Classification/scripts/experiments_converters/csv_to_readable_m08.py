#!/usr/bin/env python3
"""
Convert M08 (AssignAttributeRanks) experiment CSV to human-readable format.

M08 output structure:
{
  "attribute_table": [
    {"attribute_type": "Variant", "attribute_value": "Deco Dot", "rank": 1},
    {"attribute_type": "UseCase", "attribute_value": "Everyday Use", "rank": 1},
    {"attribute_type": "Audience", "attribute_value": "Adults", "rank": 1},
    ...
  ]
}

Output format: Each attribute on separate row with rank, grouped by type.
"""

import csv
import json
import sys
from pathlib import Path


# Default output directory (relative to project root)
DEFAULT_OUTPUT_DIR = Path(__file__).parent.parent.parent / "experiment_results_readable"


def parse_json_safe(value: str) -> dict:
    """Safely parse JSON string, return empty dict on failure."""
    if not value or value == '""':
        return {}
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return {}


def convert_m08_csv(input_path: str, output_path: str = None) -> str:
    """
    Convert M08 experiment CSV to readable format.

    Args:
        input_path: Path to input CSV file
        output_path: Path to output CSV file (optional, saves to experiment_results_readable/)

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
    headers = [
        'ASIN / Brand',
        'Input Field', 'Input Value',
        'Attribute Type', 'Rank', 'Attribute Value'
    ]

    for row in rows:
        asin = row.get('ASIN', '')
        brand = row.get('Brand', '')

        # Parse JSON columns
        input_data = parse_json_safe(row.get('input', '{}'))
        output_data = parse_json_safe(row.get('output', '{}'))
        metadata = parse_json_safe(row.get('metadata', '{}'))

        # Get brand from metadata if not in Brand column
        if not brand:
            brand = metadata.get('brand_name', '')

        # Collect ALL input fields (including empty)
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

        # Parse attribute table from output
        attribute_table = output_data.get('attribute_table', [])

        # Group by type and sort by rank
        variants = sorted(
            [a for a in attribute_table if a.get('attribute_type') == 'Variant'],
            key=lambda x: x.get('rank', 999)
        )
        use_cases = sorted(
            [a for a in attribute_table if a.get('attribute_type') == 'UseCase'],
            key=lambda x: x.get('rank', 999)
        )
        audiences = sorted(
            [a for a in attribute_table if a.get('attribute_type') == 'Audience'],
            key=lambda x: x.get('rank', 999)
        )

        # Build attribute rows: type, rank, value
        attribute_rows = []
        for attr in variants:
            attribute_rows.append(('Variant', attr.get('rank', ''), attr.get('attribute_value', '')))
        for attr in use_cases:
            attribute_rows.append(('UseCase', attr.get('rank', ''), attr.get('attribute_value', '')))
        for attr in audiences:
            attribute_rows.append(('Audience', attr.get('rank', ''), attr.get('attribute_value', '')))

        # Determine max rows needed
        max_rows = max(len(input_fields), len(attribute_rows), 3)

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

            # Attribute columns
            if i < len(attribute_rows):
                attr_type, attr_rank, attr_value = attribute_rows[i]
            else:
                attr_type, attr_rank, attr_value = '', '', ''

            output_rows.append([col1, input_field, input_value, attr_type, attr_rank, attr_value])

        # Add separator row between products
        output_rows.append(['---', '', '', '', '', ''])

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
        print("Usage: python csv_to_readable_m08.py <input_csv> [output_csv]")
        print("\nConverts M08 (AssignAttributeRanks) experiment results to readable format.")
        print("\nExample:")
        print("  python csv_to_readable_m08.py experiment.csv")
        print("  python csv_to_readable_m08.py experiment.csv readable_output.csv")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    convert_m08_csv(input_path, output_path)


if __name__ == '__main__':
    main()
