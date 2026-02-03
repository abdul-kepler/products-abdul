#!/usr/bin/env python3
"""
Generate M06 and M07 v2 datasets from CSV file.

This script parses the "Competitors - ASIN Data.csv" file and creates
new v2 dataset files for M06 (product type taxonomy) and M07 (product attributes).

The expected fields will be left empty/placeholder for manual annotation.
"""

import csv
import json
from pathlib import Path
from typing import Dict, List, Any, Optional


def clean_bullet_points(row: Dict[str, str]) -> str:
    """Extract and format bullet points from CSV row."""
    bullet_points = []
    for i in range(1, 11):
        feature = row.get(f"Description & Features: Feature {i}", "").strip()
        if feature:
            bullet_points.append(feature)
    return "\n".join(bullet_points)


def extract_product_type(row: Dict[str, str]) -> str:
    """Extract product type from CSV row (Type column)."""
    return row.get("Type", "").strip() or "UNKNOWN"


def parse_csv_row_for_m06(row: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """Parse a CSV row into M06 dataset format."""
    asin = row.get("ASIN", "").strip()
    if not asin:
        return None

    title = row.get("Title", "").strip()
    if not title:
        return None

    bullet_points = clean_bullet_points(row)
    description = row.get("Description & Features: Description", "").strip()
    product_type = extract_product_type(row)
    category_root = row.get("Categories: Root", "").strip()
    category_sub = row.get("Categories: Sub", "").strip()
    brand = row.get("Brand", "").strip()

    return {
        "id": f"M6_{asin}",
        "input": {
            "title": title,
            "bullet_points": bullet_points,
            "description": description,
            "product_type": product_type,
            "category_root": category_root,
            "category_sub": category_sub
        },
        "expected": {
            "taxonomy": []
        },
        "metadata": {
            "module_id": "Module_06",
            "asin": asin,
            "brand_name": brand,
            "split": "train"
        }
    }


def parse_csv_row_for_m07(row: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """Parse a CSV row into M07 dataset format."""
    asin = row.get("ASIN", "").strip()
    if not asin:
        return None

    title = row.get("Title", "").strip()
    if not title:
        return None

    bullet_points = clean_bullet_points(row)
    description = row.get("Description & Features: Description", "").strip()
    product_type = extract_product_type(row)
    category_root = row.get("Categories: Root", "").strip()
    category_sub = row.get("Categories: Sub", "").strip()
    brand = row.get("Brand", "").strip()

    # Additional fields for M07
    color = row.get("Color", "").strip()
    size = row.get("Size", "").strip()
    material = row.get("Material", "").strip()
    style = row.get("Style", "").strip()
    target_audience = row.get("Target Audience", "").strip()
    specific_uses = row.get("Specific Uses", "").strip()
    model = row.get("Model", "").strip()
    item_form = row.get("Item Form", "").strip()
    number_of_items = row.get("Number of Items", "").strip()
    included_components = row.get("Included Components", "").strip()

    return {
        "id": f"M7_{asin}",
        "input": {
            "title": title,
            "bullet_points": bullet_points,
            "description": description,
            "product_type": product_type,
            "category_root": category_root,
            "category_sub": category_sub,
            "color": color,
            "size": size,
            "material": material,
            "style": style,
            "target_audience": target_audience,
            "specific_uses": specific_uses,
            "model": model,
            "item_form": item_form,
            "number_of_items": number_of_items,
            "included_components": included_components
        },
        "expected": {
            "variants": [],
            "use_cases": [],
            "audiences": []
        },
        "metadata": {
            "module_id": "Module_07",
            "asin": asin,
            "brand_name": brand,
            "split": "train"
        }
    }


def generate_datasets(csv_path: str, output_dir: str, skip_existing: bool = True):
    """
    Generate M06 v2 and M07 v2 datasets from CSV file.

    Args:
        csv_path: Path to the CSV file
        output_dir: Directory to write output JSONL files
        skip_existing: Skip ASINs that already exist in v1 datasets
    """
    csv_path = Path(csv_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not csv_path.exists():
        print(f"Error: CSV file not found: {csv_path}")
        return

    # Load existing ASINs from v1 datasets to avoid duplicates
    existing_asins = set()
    if skip_existing:
        v1_m06 = output_dir / "m06_generate_product_type_taxonomy.jsonl"
        v1_m07 = output_dir / "m07_extract_product_attributes.jsonl"

        for v1_file in [v1_m06, v1_m07]:
            if v1_file.exists():
                with open(v1_file, 'r') as f:
                    for line in f:
                        data = json.loads(line)
                        asin = data.get("metadata", {}).get("asin", "")
                        if asin:
                            existing_asins.add(asin)

        if existing_asins:
            print(f"Found {len(existing_asins)} existing ASINs in v1 datasets")

    # Parse CSV
    m06_entries = []
    m07_entries = []
    skipped = 0

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            asin = row.get("ASIN", "").strip()

            # Skip if ASIN already exists in v1
            if skip_existing and asin in existing_asins:
                skipped += 1
                continue

            # Parse for M06
            m06_entry = parse_csv_row_for_m06(row)
            if m06_entry:
                m06_entries.append(m06_entry)

            # Parse for M07
            m07_entry = parse_csv_row_for_m07(row)
            if m07_entry:
                m07_entries.append(m07_entry)

    print(f"Parsed {len(m06_entries)} new ASINs from CSV")
    if skip_existing:
        print(f"Skipped {skipped} ASINs (already in v1)")

    # Write M06 v2 dataset
    m06_output = output_dir / "m06_generate_product_type_taxonomy_v2.jsonl"
    with open(m06_output, 'w', encoding='utf-8') as f:
        for entry in m06_entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"M06 v2: {len(m06_entries)} entries -> {m06_output}")

    # Write M07 v2 dataset
    m07_output = output_dir / "m07_extract_product_attributes_v2.jsonl"
    with open(m07_output, 'w', encoding='utf-8') as f:
        for entry in m07_entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"M07 v2: {len(m07_entries)} entries -> {m07_output}")

    return m06_entries, m07_entries


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate M06/M07 v2 datasets from CSV"
    )
    parser.add_argument(
        "--csv", "-c",
        default="/home/kostya/Downloads/Competitors - ASIN Data.csv",
        help="Path to CSV file"
    )
    parser.add_argument(
        "--output", "-o",
        default="datasets",
        help="Output directory for JSONL files"
    )
    parser.add_argument(
        "--include-existing",
        action="store_true",
        help="Include ASINs that already exist in v1 datasets"
    )

    args = parser.parse_args()

    generate_datasets(
        csv_path=args.csv,
        output_dir=args.output,
        skip_existing=not args.include_existing
    )


if __name__ == "__main__":
    main()
