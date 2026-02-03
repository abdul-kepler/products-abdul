#!/usr/bin/env python3
"""
Generate SD01-22 Synthetic Datasets from Keepa CSV Export.

Creates datasets for modules: M01, M01a, M01b, M06, M07, M08
Each SD dataset contains products from 5-8 themed product types.

Usage:
    python generate_sd_datasets.py --input <keepa_csv> --output-dir <dir>
"""

import csv
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict


# SD Dataset definitions: 22 themed groups (SD01-SD22) covering all 113 product types
SD_GROUPS = {
    "sd01": {
        "name": "Kitchen Tools",
        "types": ["KITCHEN_KNIFE", "CUTTING_BOARD", "FOOD_BLENDER", "COOKING_POT", "PRESSURE_COOKER"]
    },
    "sd02": {
        "name": "Hair Care & Styling",
        "types": ["SHAMPOO", "HAIR_DRYER", "HAIR_IRON", "COSMETIC_BRUSH", "NAIL_POLISH"]
    },
    "sd03": {
        "name": "Skincare & Beauty",
        "types": ["SKIN_MOISTURIZER", "SUNSCREEN", "PERSONAL_FRAGRANCE", "MASCARA", "TOOTHBRUSH"]
    },
    "sd04": {
        "name": "Health & Wellness",
        "types": ["NUTRITIONAL_SUPPLEMENT", "VITAMIN", "MEDICATION", "BLOOD_PRESSURE_MONITOR", "WOUND_DRESSING"]
    },
    "sd05": {
        "name": "Pets",
        "types": ["PET_TOY", "ANIMAL_COLLAR", "PET_APPAREL", "PET_FOOD", "PET_BED_MAT"]
    },
    "sd06": {
        "name": "Baby & Kids",
        "types": ["BABY_FORMULA", "PACIFIER", "BABY_BOTTLE", "BABY_COSTUME", "STROLLER"]
    },
    "sd07": {
        "name": "Clothing Essentials",
        "types": ["SHIRT", "SHOES", "HAT", "DRESS", "SOCKS"]
    },
    "sd08": {
        "name": "Active Wear & Sports",
        "types": ["SWIMWEAR", "PAJAMAS", "BACKPACK", "EXERCISE_MAT", "EXERCISE_BLOCK"]
    },
    "sd09": {
        "name": "Home Electronics",
        "types": ["ELECTRONIC_CABLE", "LAMP", "LIGHT_BULB", "POWER_BANK", "BATTERY"]
    },
    "sd10": {
        "name": "Home Decor",
        "types": ["RUG", "CHAIR", "BLANKET", "CURTAIN", "PICTURE_FRAME"]
    },
    "sd11": {
        "name": "Outdoor & Camping",
        "types": ["TENT", "FISHING_ROD", "FLASHLIGHT", "CANDLE", "PLANTER"]
    },
    "sd12": {
        "name": "Tools & Hardware",
        "types": ["DRILL", "WRENCH", "HAMMER_MALLET", "SCREWDRIVER", "TAPE_MEASURE"]
    },
    "sd13": {
        "name": "Automotive",
        "types": ["AUTO_PART", "VEHICLE_TIRE", "WIPER_BLADE", "VEHICLE_LIGHT_BULB", "AUTO_OIL"]
    },
    "sd14": {
        "name": "Office & Stationery",
        "types": ["PRINTER", "FILE_FOLDER", "WRITING_INSTRUMENT", "SCISSORS", "CALCULATOR"]
    },
    "sd15": {
        "name": "Garden & Lawn",
        "types": ["FERTILIZER", "HOSE_PIPE_FITTING", "LAWN_MOWER", "PLANT_SEED", "GRADUATED_CYLINDER"]
    },
    "sd16": {
        "name": "Food & Beverages",
        "types": ["SNACK_CHIP_AND_CRISP", "COFFEE", "CEREAL", "FOOD_STORAGE_CONTAINER", "RICE_COOKERS"]
    },
    "sd17": {
        "name": "Games & Toys",
        "types": ["BOARD_GAME", "TOY_BUILDING_BLOCK", "PUZZLES", "MUSICAL_INSTRUMENTS", "JUMP_ROPE"]
    },
    "sd18": {
        "name": "Home Cleaning & Care",
        "types": ["CLEANING_AGENT", "LAUNDRY_DETERGENT", "SEWING_MACHINE", "YARN", "CLOTHES_HANGER"]
    },
    # New SD groups to include all remaining product types
    "sd19": {
        "name": "Electronics & Smart Devices",
        "types": ["SECURITY_CAMERA", "SPEAKERS", "CELLULAR_PHONE", "REMOTE_CONTROL", "FLASH_DRIVE"]
    },
    "sd20": {
        "name": "Health & Medical Extended",
        "types": ["ORTHOPEDIC_BRACE", "INCONTINENCE_PROTECTOR", "PROTEIN_SUPPLEMENT_POWDER", "THERMOMETER", "FIRST_AID_KIT"]
    },
    "sd21": {
        "name": "Sports & Fitness Extended",
        "types": ["GOLF_CLUB", "BICYCLE", "DUMBBELL", "WATCH", "CLOCK"]
    },
    "sd22": {
        "name": "Home, Pets & Crafts Mixed",
        "types": ["PAINT", "EARRING", "LOCK", "ANIMAL_CARRIER", "LITTER_BOX", "VACUUM_CLEANER", "AIR_PURIFIER", "GLITTER"]
    }
}


def clean_bullet_points(row: Dict[str, str]) -> str:
    """Extract and format bullet points from CSV row."""
    bullet_points = []
    for i in range(1, 11):
        feature = row.get(f"Description & Features: Feature {i}", "").strip()
        if feature:
            bullet_points.append(feature)
    return "\n".join(bullet_points)


def parse_csv(csv_path: Path) -> Dict[str, List[Dict[str, Any]]]:
    """Parse CSV and group products by Type."""
    products_by_type = defaultdict(list)

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            product_type = row.get("Type", "").strip()
            if not product_type:
                continue

            asin = row.get("ASIN", "").strip()
            if not asin:
                continue

            product = {
                "asin": asin,
                "product_type": product_type,
                "title": row.get("Title", "").strip(),
                "description": row.get("Description & Features: Description", "").strip(),
                "bullet_points": clean_bullet_points(row),
                "brand": row.get("Brand", "").strip(),
                "manufacturer": row.get("Manufacturer", "").strip(),
                "category_root": row.get("Categories: Root", "").strip(),
                "category_sub": row.get("Categories: Sub", "").strip(),
                "color": row.get("Color", "").strip(),
                "size": row.get("Size", "").strip(),
                "material": row.get("Material", "").strip(),
                "style": row.get("Style", "").strip(),
                "model": row.get("Model", "").strip(),
                "item_form": row.get("Item Form", "").strip(),
                "target_audience": row.get("Target Audience", "").strip(),
                "specific_uses": row.get("Specific Uses", "").strip(),
                "number_of_items": row.get("Number of Items", "").strip(),
                "included_components": row.get("Included Components", "").strip(),
            }
            products_by_type[product_type].append(product)

    return products_by_type


def create_m01_entry(product: Dict[str, Any], sd_id: str) -> Dict[str, Any]:
    """Create M01 dataset entry (Extract Own Brand Entities)."""
    return {
        "id": f"M1_{sd_id}_{product['asin']}",
        "input": {
            "brand_name": product["brand"],
            "title": product["title"],
            "bullet_points": product["bullet_points"],
            "description": product["description"],
            "manufacturer": product["manufacturer"]
        },
        "expected": {
            "brand_entities": []  # To be annotated
        },
        "metadata": {
            "module_id": "Module_01",
            "asin": product["asin"],
            "brand_name": product["brand"],
            "product_type": product["product_type"],
            "source": "keepa",
            "sd_dataset": sd_id
        }
    }


def create_m01a_entry(product: Dict[str, Any], sd_id: str) -> Dict[str, Any]:
    """Create M01a dataset entry (Extract Own Brand Variations)."""
    return {
        "id": f"M1a_{sd_id}_{product['asin']}",
        "input": {
            "brand_name": product["brand"]
        },
        "expected": {
            "variations": []  # To be annotated
        },
        "metadata": {
            "module_id": "Module_01a",
            "asin": product["asin"],
            "brand_name": product["brand"],
            "product_type": product["product_type"],
            "source": "keepa",
            "sd_dataset": sd_id
        }
    }


def create_m01b_entry(product: Dict[str, Any], sd_id: str) -> Dict[str, Any]:
    """Create M01b dataset entry (Extract Brand Related Terms)."""
    return {
        "id": f"M1b_{sd_id}_{product['asin']}",
        "input": {
            "brand_name": product["brand"],
            "title": product["title"],
            "bullet_points": product["bullet_points"],
            "description": product["description"],
            "manufacturer": product["manufacturer"]
        },
        "expected": {
            "sub_brands": [],  # To be annotated
            "searchable_standards": [],  # To be annotated
            "manufacturer": None  # To be annotated: {"name": str, "short": str, "searchable": bool} or null
        },
        "metadata": {
            "module_id": "Module_01b",
            "asin": product["asin"],
            "brand_name": product["brand"],
            "product_type": product["product_type"],
            "source": "keepa",
            "sd_dataset": sd_id
        }
    }


def create_m06_entry(product: Dict[str, Any], sd_id: str) -> Dict[str, Any]:
    """Create M06 dataset entry (Generate Product Type Taxonomy)."""
    return {
        "id": f"M6_{sd_id}_{product['asin']}",
        "input": {
            "title": product["title"],
            "bullet_points": product["bullet_points"],
            "description": product["description"],
            "product_type": product["product_type"],
            "category_root": product["category_root"],
            "category_sub": product["category_sub"]
        },
        "expected": {
            "taxonomy": []  # To be annotated
        },
        "metadata": {
            "module_id": "Module_06",
            "asin": product["asin"],
            "brand_name": product["brand"],
            "split": "train",
            "sd_dataset": sd_id
        }
    }


def create_m07_entry(product: Dict[str, Any], sd_id: str) -> Dict[str, Any]:
    """Create M07 dataset entry (Extract Product Attributes)."""
    return {
        "id": f"M7_{sd_id}_{product['asin']}",
        "input": {
            "title": product["title"],
            "bullet_points": product["bullet_points"],
            "description": product["description"],
            "product_type": product["product_type"],
            "category_root": product["category_root"],
            "category_sub": product["category_sub"],
            "color": product["color"],
            "size": product["size"],
            "material": product["material"],
            "style": product["style"],
            "target_audience": product["target_audience"],
            "specific_uses": product["specific_uses"],
            "model": product["model"],
            "item_form": product["item_form"],
            "number_of_items": product["number_of_items"],
            "included_components": product["included_components"]
        },
        "expected": {
            "variants": [],
            "use_cases": [],
            "audiences": []
        },
        "metadata": {
            "module_id": "Module_07",
            "asin": product["asin"],
            "brand_name": product["brand"],
            "split": "train",
            "sd_dataset": sd_id
        }
    }


def create_m08_entry(product: Dict[str, Any], sd_id: str) -> Dict[str, Any]:
    """Create M08 dataset entry (Assign Attribute Ranks)."""
    return {
        "id": f"M8_{sd_id}_{product['asin']}",
        "input": {
            "title": product["title"],
            "bullet_points": product["bullet_points"],
            "description": product["description"],
            "taxonomy": [],  # To be filled from M06
            "variants": [],  # To be filled from M07
            "use_cases": [],  # To be filled from M07
            "audiences": []  # To be filled from M07
        },
        "expected": {
            "attribute_table": []
        },
        "metadata": {
            "module_id": "Module_08",
            "asin": product["asin"],
            "brand_name": product["brand"],
            "split": "train",
            "sd_dataset": sd_id,
            "has_m6_data": False,
            "has_m7_data": False
        }
    }


def write_jsonl(data: List[Dict], output_path: Path):
    """Write data to JSONL file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    print(f"  Written: {output_path} ({len(data)} entries)")


def generate_sd_datasets(csv_path: Path, output_dir: Path, max_per_type: int = 20):
    """Generate all SD datasets."""
    print(f"Parsing CSV: {csv_path}")
    products_by_type = parse_csv(csv_path)

    print(f"\nFound {len(products_by_type)} product types")
    print(f"Total products: {sum(len(p) for p in products_by_type.values())}")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    summary = []

    for sd_id, sd_config in SD_GROUPS.items():
        print(f"\n=== Generating {sd_id.upper()}: {sd_config['name']} ===")

        m01_data = []
        m01a_data = []
        m01b_data = []
        m06_data = []
        m07_data = []
        m08_data = []

        types_found = []
        types_missing = []

        for product_type in sd_config["types"]:
            products = products_by_type.get(product_type, [])

            if not products:
                types_missing.append(product_type)
                continue

            types_found.append(f"{product_type}({len(products)})")

            # Take up to max_per_type products
            for product in products[:max_per_type]:
                if product["brand"]:  # Only include products with brand
                    m01_data.append(create_m01_entry(product, sd_id))
                    m01a_data.append(create_m01a_entry(product, sd_id))
                    m01b_data.append(create_m01b_entry(product, sd_id))

                m06_data.append(create_m06_entry(product, sd_id))
                m07_data.append(create_m07_entry(product, sd_id))
                m08_data.append(create_m08_entry(product, sd_id))

        print(f"  Types found: {', '.join(types_found)}")
        if types_missing:
            print(f"  Types missing: {', '.join(types_missing)}")

        # Write datasets
        write_jsonl(m01_data, output_dir / f"m01_{sd_id}_extract_own_brand_entities.jsonl")
        write_jsonl(m01a_data, output_dir / f"m01a_{sd_id}_extract_own_brand_variations.jsonl")
        write_jsonl(m01b_data, output_dir / f"m01b_{sd_id}_extract_brand_related_terms.jsonl")
        write_jsonl(m06_data, output_dir / f"m06_{sd_id}_generate_product_type_taxonomy.jsonl")
        write_jsonl(m07_data, output_dir / f"m07_{sd_id}_extract_product_attributes.jsonl")
        write_jsonl(m08_data, output_dir / f"m08_{sd_id}_assign_attribute_ranks.jsonl")

        summary.append({
            "sd_id": sd_id,
            "name": sd_config["name"],
            "types": sd_config["types"],
            "types_found": len(types_found),
            "types_missing": len(types_missing),
            "m01_count": len(m01_data),
            "m01b_count": len(m01b_data),
            "m06_count": len(m06_data),
            "m07_count": len(m07_data),
            "m08_count": len(m08_data)
        })

    # Write summary
    summary_path = output_dir / "sd_datasets_summary.json"
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    print(f"\nSummary written to: {summary_path}")

    # Print summary table
    print("\n" + "=" * 90)
    print("SUMMARY")
    print("=" * 90)
    print(f"{'SD':<6} {'Name':<25} {'Types':<8} {'M01':<6} {'M01b':<6} {'M06':<6} {'M07':<6} {'M08':<6}")
    print("-" * 90)
    for s in summary:
        print(f"{s['sd_id']:<6} {s['name']:<25} {s['types_found']}/5    {s['m01_count']:<6} {s['m01b_count']:<6} {s['m06_count']:<6} {s['m07_count']:<6} {s['m08_count']:<6}")

    total_m01 = sum(s['m01_count'] for s in summary)
    total_m01b = sum(s['m01b_count'] for s in summary)
    total_m06 = sum(s['m06_count'] for s in summary)
    print("-" * 90)
    print(f"{'TOTAL':<6} {'':<25} {'':8} {total_m01:<6} {total_m01b:<6} {total_m06:<6} {total_m06:<6} {total_m06:<6}")


def main():
    parser = argparse.ArgumentParser(description="Generate SD1-18 Synthetic Datasets")
    parser.add_argument(
        "--input", "-i",
        type=Path,
        default=Path("SD/KeepaExport-2026-01-27-ProductViewer.csv"),
        help="Input Keepa CSV file"
    )
    parser.add_argument(
        "--output-dir", "-o",
        type=Path,
        default=Path("datasets/synthetic"),
        help="Output directory for datasets"
    )
    parser.add_argument(
        "--max-per-type",
        type=int,
        default=20,
        help="Maximum products per product type (default: 20)"
    )

    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}")
        return 1

    generate_sd_datasets(args.input, args.output_dir, args.max_per_type)
    return 0


if __name__ == "__main__":
    exit(main())
