#!/usr/bin/env python3
"""
Universal converter for all experiment results to human-readable CSV format.

Features:
- Auto-detects module type from folder/filename
- Module-specific formatting for each output structure
- Organizes output into folders by module
- Batch processing of all experiments

Usage:
    python convert_all_experiments.py                    # Convert all experiments
    python convert_all_experiments.py M01               # Convert only M01 experiments
    python convert_all_experiments.py path/to/file.csv  # Convert single file
"""

import csv
import json
import sys
import re
from pathlib import Path
from typing import Callable

PROJECT_ROOT = Path(__file__).parent.parent.parent
EXPERIMENT_DIR = PROJECT_ROOT / "experiment_results"
OUTPUT_DIR = PROJECT_ROOT / "experiment_results_readable"


def parse_json_safe(value: str, as_dict: bool = True) -> dict | list:
    """Safely parse JSON string."""
    if not value or value == '""':
        return {} if as_dict else []
    try:
        result = json.loads(value)
        if as_dict and isinstance(result, list):
            return {'items': result}  # Wrap list in dict
        return result
    except json.JSONDecodeError:
        return {} if as_dict else []


# ============================================================================
# Module-specific formatters
# ============================================================================

def format_m01(row: dict) -> list[list[str]]:
    """M01: ExtractOwnBrandEntities - brand_entities list."""
    asin = row.get('ASIN', '')
    brand = get_brand(row)
    input_data = parse_json_safe(row.get('input', '{}'))
    output_data = parse_json_safe(row.get('output', '{}'))

    # Input fields
    input_fields = [
        ('brand_name', input_data.get('brand_name', '—')),
        ('product_data', str(input_data.get('product_data', {}))[:100] + '...' if input_data.get('product_data') else '—'),
    ]

    # Output: brand_entities list
    entities = output_data.get('brand_entities', [])
    if isinstance(entities, list):
        output_fields = [('entity', e) for e in entities]
    else:
        output_fields = []

    return build_rows(asin, brand, input_fields, output_fields,
                      ['ASIN / Brand', 'Input Field', 'Input Value', 'Output Type', 'Entity'])


def format_m01a(row: dict) -> list[list[str]]:
    """M01A: ExtractOwnBrandVariations - variations list."""
    asin = row.get('ASIN', '')
    brand = get_brand(row)
    input_data = parse_json_safe(row.get('input', '{}'))
    output_data = parse_json_safe(row.get('output', '{}'))

    input_fields = [
        ('brand_name', input_data.get('brand_name', '—')),
    ]

    variations = output_data.get('variations', [])
    if isinstance(variations, list):
        output_fields = [('variation', v) for v in variations]
    else:
        output_fields = []

    return build_rows(asin, brand, input_fields, output_fields,
                      ['ASIN / Brand', 'Input Field', 'Input Value', 'Type', 'Variation'])


def format_m01b(row: dict) -> list[list[str]]:
    """M01B: ExtractBrandRelatedTerms - manufacturer and sub_brands in separate columns."""
    asin = row.get('ASIN', '')
    brand = get_brand(row)
    input_data = parse_json_safe(row.get('input', '{}'))
    output_data = parse_json_safe(row.get('output', '{}'))

    # Get manufacturer (can be dict with 'name' or string)
    manufacturer = output_data.get('manufacturer', '')
    if isinstance(manufacturer, dict):
        manufacturer = manufacturer.get('name', '') or manufacturer.get('short', '')
    elif isinstance(manufacturer, list):
        manufacturer = manufacturer[0] if manufacturer else ''

    # Get sub_brands list
    sub_brands = output_data.get('sub_brands', [])
    if not isinstance(sub_brands, list):
        sub_brands = [sub_brands] if sub_brands else []

    headers = ['ASIN / Brand', 'Brand Name', 'Manufacturer', 'Sub-brand']
    rows = []

    # Clean ASIN
    display_asin = clean_asin(asin)

    # First row: ASIN, brand_name, manufacturer, first sub_brand
    rows.append([
        display_asin,
        input_data.get('brand_name', '—'),
        manufacturer or '—',
        sub_brands[0] if sub_brands else '—'
    ])

    # Second row: URL
    rows.append([
        f"https://www.amazon.com/dp/{display_asin}" if display_asin else '',
        '',
        '',
        sub_brands[1] if len(sub_brands) > 1 else ''
    ])

    # Third row: Brand
    rows.append([
        brand,
        '',
        '',
        sub_brands[2] if len(sub_brands) > 2 else ''
    ])

    # Additional rows for remaining sub_brands
    for i in range(3, len(sub_brands)):
        rows.append(['', '', '', sub_brands[i]])

    # Separator
    rows.append(['---', '', '', ''])

    return headers, rows


def get_brand(row: dict) -> str:
    """Get brand from Brand column, metadata, or input."""
    brand = row.get('Brand', '')
    if brand:
        return brand
    # Try metadata
    metadata = parse_json_safe(row.get('metadata', '{}'))
    if metadata.get('brand_name'):
        return metadata['brand_name']
    # Try input
    input_data = parse_json_safe(row.get('input', '{}'))
    if input_data.get('brand_name'):
        return input_data['brand_name']
    return ''


def format_m06(row: dict) -> list[list[str]]:
    """M06: GenerateProductTypeTaxonomy - taxonomy hierarchy."""
    asin = row.get('ASIN', '')
    brand = get_brand(row)
    input_data = parse_json_safe(row.get('input', '{}'))
    output_data = parse_json_safe(row.get('output', '{}'))

    # Priority input fields (no truncation for bullet_points and description)
    priority = ['title', 'category_root', 'category_sub', 'product_type', 'bullet_points', 'description']
    no_truncate = ['bullet_points', 'description']
    input_fields = []
    for field in priority:
        if field in input_data:
            val = input_data[field]
            if not val:
                display = '—'
            elif field in no_truncate:
                display = str(val)  # Full text
            else:
                display = str(val)[:100]
            input_fields.append((field, display))

    # Taxonomy output - can be list or dict
    taxonomy = output_data.get('taxonomy', [])
    output_fields = []

    if isinstance(taxonomy, list):
        # List format: [{level: 1, product_type: "...", rank: 1}, ...]
        sorted_tax = sorted(taxonomy, key=lambda x: (x.get('level', 0), x.get('rank', 0)))
        for item in sorted_tax:
            level = item.get('level', '')
            product_type = item.get('product_type', '')
            if product_type:
                output_fields.append((f"L{level}", product_type))
    elif isinstance(taxonomy, dict):
        # Dict format: {L1: "...", L2: "..."}
        for level in ['L1', 'L2', 'L3', 'L4', 'L5']:
            val = taxonomy.get(level, '')
            if val:
                output_fields.append((level, val))

    return build_rows(asin, brand, input_fields, output_fields,
                      ['ASIN / Brand', 'Input Field', 'Input Value', 'Level', 'Product Type'])


def format_m07(row: dict) -> list[list[str]]:
    """M07: ExtractProductAttributes - audiences, use_cases, variants."""
    asin = row.get('ASIN', '')
    brand = get_brand(row)
    input_data = parse_json_safe(row.get('input', '{}'))
    output_data = parse_json_safe(row.get('output', '{}'))

    # ALL input fields in logical order
    field_order = [
        'title', 'category_root', 'category_sub', 'product_type',
        'description', 'bullet_points', 'color', 'size', 'material',
        'style', 'item_form', 'model', 'number_of_items',
        'included_components', 'specific_uses', 'target_audience'
    ]
    no_truncate = ['bullet_points', 'description']
    input_fields = []
    for field in field_order:
        if field in input_data:
            val = input_data[field]
            if val and val != '""':
                display = str(val) if field in no_truncate else str(val)[:100]
                input_fields.append((field, display))

    # Output fields
    output_fields = []
    for output_type in ['audiences', 'use_cases', 'variants']:
        items = output_data.get(output_type, [])
        if isinstance(items, list):
            for item in items:
                if item and item != '-':
                    output_fields.append((output_type, str(item)))

    return build_rows(asin, brand, input_fields, output_fields,
                      ['ASIN / Brand', 'Input Field', 'Input Value', 'Attribute Type', 'Attribute Value'])


def format_m08(row: dict) -> list[list[str]]:
    """M08: AssignAttributeRanks - attribute_table with ranks in separate columns."""
    asin = row.get('ASIN', '')
    brand = get_brand(row)
    input_data = parse_json_safe(row.get('input', '{}'))
    output_data = parse_json_safe(row.get('output', '{}'))

    # ALL input fields - M08 gets different inputs depending on pipeline
    input_fields = []

    # Basic product fields
    basic_fields = [
        'title', 'category_root', 'category_sub', 'product_type',
        'description', 'bullet_points', 'color', 'size', 'material',
        'style', 'item_form', 'model', 'number_of_items',
        'included_components', 'specific_uses', 'target_audience'
    ]
    no_truncate = ['bullet_points', 'description']
    for field in basic_fields:
        if field in input_data:
            val = input_data[field]
            if val and val != '""':
                display = str(val) if field in no_truncate else str(val)[:100]
                input_fields.append((field, display))

    # M07 outputs (audiences, use_cases, variants)
    for field in ['audiences', 'use_cases', 'variants']:
        val = input_data.get(field, [])
        if isinstance(val, list):
            for item in val:
                if item and item != '-':
                    input_fields.append((field, str(item)[:80]))

    # Taxonomy from M06
    taxonomy = input_data.get('taxonomy', [])
    if isinstance(taxonomy, list):
        for item in taxonomy:
            if isinstance(item, dict):
                level = item.get('level', '')
                pt = item.get('product_type', '')
                if pt:
                    input_fields.append((f'taxonomy_L{level}', pt))

    # Parse attribute table - separate type, rank, value
    attribute_table = output_data.get('attribute_table', [])
    output_attrs = []  # (type, rank, value)
    for attr_type in ['Variant', 'UseCase', 'Audience']:
        attrs = sorted(
            [a for a in attribute_table if a.get('attribute_type') == attr_type],
            key=lambda x: x.get('rank', 999)
        )
        for attr in attrs:
            output_attrs.append((
                attr_type,
                str(attr.get('rank', '')),
                attr.get('attribute_value', '')
            ))

    # Build rows with 6 columns
    headers = ['ASIN / Brand', 'Input Field', 'Input Value', 'Type', 'Rank', 'Attribute Value']
    rows = []
    max_rows = max(len(input_fields), len(output_attrs), 3)

    # Clean ASIN
    display_asin = clean_asin(asin)

    for i in range(max_rows):
        # Column 1: ASIN, URL, Brand
        if i == 0:
            col1 = display_asin
        elif i == 1:
            col1 = f"https://www.amazon.com/dp/{display_asin}" if display_asin else ''
        elif i == 2:
            col1 = brand
        else:
            col1 = ''

        # Columns 2-3: Input
        if i < len(input_fields):
            in_field, in_value = input_fields[i]
        else:
            in_field, in_value = '', ''

        # Columns 4-6: Output (type, rank, value)
        if i < len(output_attrs):
            out_type, out_rank, out_value = output_attrs[i]
        else:
            out_type, out_rank, out_value = '', '', ''

        rows.append([col1, in_field, in_value, out_type, out_rank, out_value])

    # Separator
    rows.append(['---', '', '', '', '', ''])

    return headers, rows


def format_m09(row: dict) -> list[list[str]]:
    """M09: IdentifyPrimaryIntendedUse - primary_use, confidence, reasoning."""
    asin = row.get('ASIN', '')
    brand = get_brand(row)
    input_data = parse_json_safe(row.get('input', '{}'))
    output_data = parse_json_safe(row.get('output', '{}'))

    input_fields = []
    no_truncate = ['bullet_points', 'description']

    # Basic fields
    for field in ['title', 'description', 'bullet_points']:
        val = input_data.get(field)
        if val and val != '""':
            display = str(val) if field in no_truncate else str(val)[:100]
            input_fields.append((field, display))

    # Product attributes (nested dict)
    prod_attrs = input_data.get('product_attributes', {})
    if isinstance(prod_attrs, dict):
        for k in ['category_root', 'category_sub', 'product_type']:
            if prod_attrs.get(k):
                input_fields.append((k, str(prod_attrs[k])[:80]))

    # Taxonomy
    taxonomy = input_data.get('taxonomy', [])
    if isinstance(taxonomy, list):
        for item in taxonomy:
            if isinstance(item, dict) and item.get('product_type'):
                input_fields.append((f"taxonomy_L{item.get('level', '')}", item['product_type']))

    # Attribute table summary
    attr_table = input_data.get('attribute_table', [])
    if isinstance(attr_table, list):
        for attr in attr_table[:10]:  # First 10
            if isinstance(attr, dict):
                input_fields.append((attr.get('attribute_type', ''), attr.get('attribute_value', '')))

    output_fields = [
        ('primary_use', output_data.get('primary_use', '—')),
        ('confidence', str(output_data.get('confidence', '—'))),
        ('reasoning', str(output_data.get('reasoning', '—'))[:150]),
    ]

    return build_rows(asin, brand, input_fields, output_fields,
                      ['ASIN / Brand', 'Input Field', 'Input Value', 'Output Field', 'Output Value'])


def format_m10(row: dict) -> list[list[str]]:
    """M10: ValidatePrimaryIntendedUse - validated_use, was_corrected."""
    asin = row.get('ASIN', '')
    brand = get_brand(row)
    input_data = parse_json_safe(row.get('input', '{}'))
    output_data = parse_json_safe(row.get('output', '{}'))

    input_fields = []
    no_truncate = ['bullet_points', 'description']

    # Basic fields
    for field in ['title', 'description', 'bullet_points', 'primary_use']:
        val = input_data.get(field)
        if val and val != '""':
            display = str(val) if field in no_truncate else str(val)[:100]
            input_fields.append((field, display))

    # Product attributes (nested dict)
    prod_attrs = input_data.get('product_attributes', {})
    if isinstance(prod_attrs, dict):
        for k in ['category_root', 'category_sub', 'product_type']:
            if prod_attrs.get(k):
                input_fields.append((k, str(prod_attrs[k])[:80]))

    # Taxonomy
    taxonomy = input_data.get('taxonomy', [])
    if isinstance(taxonomy, list):
        for item in taxonomy:
            if isinstance(item, dict) and item.get('product_type'):
                input_fields.append((f"taxonomy_L{item.get('level', '')}", item['product_type']))

    # Attribute table summary
    attr_table = input_data.get('attribute_table', [])
    if isinstance(attr_table, list):
        for attr in attr_table[:10]:  # First 10
            if isinstance(attr, dict):
                input_fields.append((attr.get('attribute_type', ''), attr.get('attribute_value', '')))

    output_fields = [
        ('validated_use', output_data.get('validated_use', '—')),
        ('was_corrected', str(output_data.get('was_corrected', '—'))),
        ('confidence', str(output_data.get('confidence', '—'))),
        ('reasoning', str(output_data.get('reasoning', '—'))[:150]),
    ]

    return build_rows(asin, brand, input_fields, output_fields,
                      ['ASIN / Brand', 'Input Field', 'Input Value', 'Output Field', 'Output Value'])


def format_m11(row: dict) -> list[list[str]]:
    """M11: IdentifyHardConstraints - hard_constraints list."""
    asin = row.get('ASIN', '')
    brand = get_brand(row)
    input_data = parse_json_safe(row.get('input', '{}'))
    output_data = parse_json_safe(row.get('output', '{}'))

    input_fields = []
    no_truncate = ['bullet_points', 'description']

    # Basic fields including validated_use from M10
    for field in ['title', 'description', 'bullet_points', 'validated_use']:
        val = input_data.get(field)
        if val and val != '""':
            display = str(val) if field in no_truncate else str(val)[:100]
            input_fields.append((field, display))

    # Product attributes (nested dict)
    prod_attrs = input_data.get('product_attributes', {})
    if isinstance(prod_attrs, dict):
        for k in ['category_root', 'category_sub', 'product_type']:
            if prod_attrs.get(k):
                input_fields.append((k, str(prod_attrs[k])[:80]))

    # Taxonomy
    taxonomy = input_data.get('taxonomy', [])
    if isinstance(taxonomy, list):
        for item in taxonomy:
            if isinstance(item, dict) and item.get('product_type'):
                input_fields.append((f"taxonomy_L{item.get('level', '')}", item['product_type']))

    # Attribute table summary
    attr_table = input_data.get('attribute_table', [])
    if isinstance(attr_table, list):
        for attr in attr_table[:10]:  # First 10
            if isinstance(attr, dict):
                input_fields.append((attr.get('attribute_type', ''), attr.get('attribute_value', '')))

    # Hard constraints output
    constraints = output_data.get('hard_constraints', [])
    output_fields = []
    if isinstance(constraints, list):
        for c in constraints:
            if isinstance(c, dict):
                output_fields.append(('constraint', f"{c.get('attribute', '')}: {c.get('value', '')}"))
            else:
                output_fields.append(('constraint', str(c)))

    output_fields.append(('confidence', str(output_data.get('confidence', '—'))))
    if output_data.get('reasoning'):
        output_fields.append(('reasoning', str(output_data.get('reasoning', ''))[:150]))

    return build_rows(asin, brand, input_fields, output_fields,
                      ['ASIN / Brand', 'Input Field', 'Input Value', 'Output Type', 'Output Value'])


def format_generic(row: dict) -> list[list[str]]:
    """Generic formatter for unknown modules."""
    asin = row.get('ASIN', '')
    brand = get_brand(row)
    input_data = parse_json_safe(row.get('input', '{}'))
    output_data = parse_json_safe(row.get('output', '{}'))

    input_fields = [(k, str(v)[:80]) for k, v in list(input_data.items())[:5]]
    output_fields = [(k, str(v)[:80]) for k, v in list(output_data.items())[:10]]

    return build_rows(asin, brand, input_fields, output_fields,
                      ['ASIN / Brand', 'Input Field', 'Input Value', 'Output Field', 'Output Value'])


def clean_asin(asin: str) -> str:
    """Extract clean ASIN from prefixed ID like M9_sd01_B082XKDYY9 -> B082XKDYY9."""
    if not asin:
        return ''
    # If ASIN contains underscore prefix (M9_sd01_B...), extract last part
    if '_' in asin and asin.startswith('M'):
        parts = asin.split('_')
        # Last part should be the actual ASIN (starts with B usually)
        return parts[-1] if parts else asin
    return asin


def build_rows(asin: str, brand: str, input_fields: list, output_fields: list,
               headers: list) -> tuple[list, list[list[str]]]:
    """Build output rows with ASIN/URL/Brand in first column."""
    rows = []
    max_rows = max(len(input_fields), len(output_fields), 3)

    # Clean ASIN - remove module prefix if present
    display_asin = clean_asin(asin)

    for i in range(max_rows):
        # First column: ASIN, URL, Brand
        if i == 0:
            col1 = display_asin
        elif i == 1:
            col1 = f"https://www.amazon.com/dp/{display_asin}" if display_asin else ''
        elif i == 2:
            col1 = brand
        else:
            col1 = ''

        # Input columns
        if i < len(input_fields):
            in_field, in_value = input_fields[i]
        else:
            in_field, in_value = '', ''

        # Output columns
        if i < len(output_fields):
            out_field, out_value = output_fields[i]
        else:
            out_field, out_value = '', ''

        rows.append([col1, in_field, in_value, out_field, out_value])

    # Separator row
    rows.append(['---', '', '', '', ''])

    return headers, rows


# Module formatter mapping
FORMATTERS: dict[str, Callable] = {
    'M01': format_m01,
    'M01A': format_m01a,
    'M01B': format_m01b,
    'M06': format_m06,
    'M07': format_m07,
    'M08': format_m08,
    'M09': format_m09,
    'M10': format_m10,
    'M11': format_m11,
}


def detect_module(filepath: Path) -> str:
    """Detect module from filepath."""
    name = filepath.parent.name if filepath.parent.name.startswith('M') else filepath.name
    match = re.match(r'(M\d+[AB]?)', name, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return 'GENERIC'


def convert_file(input_path: Path, output_dir: Path = None) -> Path:
    """Convert a single experiment file to readable format."""
    module = detect_module(input_path)
    formatter = FORMATTERS.get(module, format_generic)

    # Determine output path
    if output_dir is None:
        output_dir = OUTPUT_DIR

    # Create module subfolder
    module_folder = output_dir / input_path.parent.name
    module_folder.mkdir(parents=True, exist_ok=True)

    output_path = module_folder / f"{input_path.stem}_readable.csv"

    # Read and convert
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        print(f"  Skip (empty): {input_path.name}")
        return None

    all_output_rows = []
    headers = None

    for row in rows:
        h, formatted_rows = formatter(row)
        if headers is None:
            headers = h
        all_output_rows.extend(formatted_rows)

    # Write output
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(all_output_rows)

    print(f"  {module}: {input_path.name} -> {output_path.name} ({len(rows)} products)")
    return output_path


def convert_all(module_filter: str = None):
    """Convert all experiment files."""
    print("=" * 70)
    print("CONVERT EXPERIMENTS TO READABLE FORMAT")
    print("=" * 70)
    print(f"Source: {EXPERIMENT_DIR}")
    print(f"Output: {OUTPUT_DIR}")
    print()

    converted = 0
    skipped = 0

    for folder in sorted(EXPERIMENT_DIR.iterdir()):
        if not folder.is_dir():
            continue

        # Filter by module if specified
        if module_filter:
            if not folder.name.upper().startswith(module_filter.upper()):
                continue

        csv_files = list(folder.glob('*.csv'))
        if not csv_files:
            continue

        print(f"\n{folder.name}:")

        for csv_file in sorted(csv_files):
            result = convert_file(csv_file)
            if result:
                converted += 1
            else:
                skipped += 1

    print()
    print("=" * 70)
    print(f"Converted: {converted} files")
    print(f"Skipped: {skipped} files")
    print(f"Output: {OUTPUT_DIR}")


def main():
    if len(sys.argv) < 2:
        # Convert all
        convert_all()
    elif sys.argv[1].endswith('.csv'):
        # Convert single file
        convert_file(Path(sys.argv[1]))
    else:
        # Filter by module
        convert_all(sys.argv[1])


if __name__ == '__main__':
    main()
