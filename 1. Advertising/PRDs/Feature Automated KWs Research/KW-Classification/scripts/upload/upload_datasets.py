#!/usr/bin/env python3
"""
Upload datasets (M01-M16) to Braintrust.

File naming convention: {module}_v{version}_{action}_{object}.jsonl
Example: m12_v1_check_hard_constraint.jsonl

Usage:
    # Upload all datasets
    python scripts/upload/upload_datasets.py

    # Upload specific module
    python scripts/upload/upload_datasets.py --module m01

    # Upload range of modules (M01-M08)
    python scripts/upload/upload_datasets.py --range m01 m08

    # Dry run - show what would be uploaded without actually uploading
    python scripts/upload/upload_datasets.py --dry-run

    # List available datasets
    python scripts/upload/upload_datasets.py --list
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent  # scripts/upload -> scripts -> project root
DATASETS_DIR = PROJECT_ROOT / "datasets"
ENV_FILE = PROJECT_ROOT / ".env"

# Import project settings from config
sys.path.insert(0, str(SCRIPT_DIR.parent))
from config import PROJECT_NAME, PROJECT_ID, load_api_key

# V1.1 Modules (M01-M16) with their dataset configurations
# Naming convention:
#   name: PascalCase matching file action_object (e.g., ExtractOwnBrandEntities)
#   description: Brief description without version prefix
V1_1_MODULES = {
    # M01-M08: Brand and Product Classification Modules
    "m01": {
        "name": "ExtractOwnBrandEntities",
        "file_pattern": "single/m01_v1_extract_own_brand_entities.jsonl",
        "description": "Extract brand entities from product data (brand name, typos, sub-brands)",
    },
    "m01a": {
        "name": "ExtractOwnBrandVariations",
        "file_pattern": "single/m01a_v1_extract_own_brand_variations.jsonl",
        "description": "Generate brand name search variations (typos, truncations, phonetic)",
    },
    "m01b": {
        "name": "ExtractBrandRelatedTerms",
        "file_pattern": "single/m01b_v1_extract_brand_related_terms.jsonl",
        "description": "Extract product lines, technologies, and manufacturer from listing",
    },
    "m02": {
        "name": "ClassifyOwnBrandKeywords",
        "file_pattern": "single/m02_v1_classify_own_brand_keywords.jsonl",
        "description": "Classify if keyword matches own brand (OB classification)",
    },
    "m03": {
        "name": "GenerateCompetitorEntities",
        "file_pattern": "single/m03_v1_generate_competitor_entities.jsonl",
        "description": "Generate competitor brand entities for the product category",
    },
    "m04": {
        "name": "ClassifyCompetitorBrandKeywords",
        "file_pattern": "single/m04_v1_classify_competitor_brand_keywords.jsonl",
        "description": "Classify if keyword is competitor brand (CB classification)",
    },
    "m05": {
        "name": "ClassifyNonBrandedKeywords",
        "file_pattern": "single/m05_v1_classify_nonbranded_keywords.jsonl",
        "description": "Classify if keyword is non-branded (NB classification)",
    },
    # Path B: Uses M01a/M01b outputs instead of M01/M03
    "m02b": {
        "name": "ClassifyOwnBrandKeywordsPathB",
        "file_pattern": "single/m02b_v1_classify_own_brand_keywords.jsonl",
        "description": "Classify if keyword matches own brand using variations context (Path B)",
    },
    "m04b": {
        "name": "ClassifyCompetitorBrandKeywordsPathB",
        "file_pattern": "single/m04b_v1_classify_competitor_brand_keywords.jsonl",
        "description": "Classify if keyword is competitor brand using variations context (Path B)",
    },
    "m05b": {
        "name": "ClassifyNonBrandedKeywordsPathB",
        "file_pattern": "single/m05b_v1_classify_nonbranded_keywords.jsonl",
        "description": "Classify if keyword is non-branded using variations context (Path B)",
    },
    "m06": {
        "name": "GenerateProductTypeTaxonomy",
        "file_pattern": "single/m06_v1_generate_product_type_taxonomy.jsonl",
        "description": "Generate product type taxonomy (category hierarchy)",
    },
    "m07": {
        "name": "ExtractProductAttributes",
        "file_pattern": "single/m07_v1_extract_product_attributes.jsonl",
        "description": "Extract product attributes from listing data",
    },
    "m08": {
        "name": "AssignAttributeRanks",
        "file_pattern": "single/m08_v1_assign_attribute_ranks.jsonl",
        "description": "Assign importance ranks to product attributes",
    },
    # M09-M16: Intent and Classification Modules
    "m09": {
        "name": "IdentifyPrimaryIntendedUse",
        "file_pattern": "single/m09_v1_identify_primary_intended_use.jsonl",
        "description": "Determine the single core reason the product exists",
    },
    "m10": {
        "name": "ValidatePrimaryIntendedUse",
        "file_pattern": "single/m10_v1_validate_primary_intended_use.jsonl",
        "description": "Validate and clean the primary intended use phrase",
    },
    "m11": {
        "name": "IdentifyHardConstraints",
        "file_pattern": "single/m11_v1_identify_hard_constraints.jsonl",
        "description": "Identify non-negotiable product attributes (hard constraints)",
    },
    "m12": {
        "name": "CheckHardConstraint",
        "file_pattern": "single/m12_v1_check_hard_constraint.jsonl",
        "description": "Check if keyword violates any hard constraint",
    },
    "m12b": {
        "name": "CombinedClassification",
        "file_pattern": "single/m12b_v1_combined_classification.jsonl",
        "description": "Combined keyword classification with structured reasoning (R/S/C/N)",
    },
    "m13": {
        "name": "CheckProductType",
        "file_pattern": "single/m13_v1_check_product_type.jsonl",
        "description": "Check if keyword asks for same product type",
    },
    "m14": {
        "name": "CheckPrimaryUseSameType",
        "file_pattern": "single/m14_v1_check_primary_use_same_type.jsonl",
        "description": "Check if same-type product supports same primary use",
    },
    "m15": {
        "name": "CheckSubstitute",
        "file_pattern": "single/m15_v1_check_substitute.jsonl",
        "description": "Check if different product type can substitute for target",
    },
    "m16": {
        "name": "CheckComplementary",
        "file_pattern": "single/m16_v1_check_complementary.jsonl",
        "description": "Check if products are used together (complementary)",
    },
}


def load_api_key():
    """Load Braintrust API key from environment or .env file."""
    api_key = os.getenv("BRAINTRUST_API_KEY")
    if api_key:
        return api_key

    # Try multiple .env file locations
    env_files = [
        ENV_FILE,
        BRAINTRUST_DIR / ".env",
        BRAINTRUST_DIR.parent / ".env",  # Root project .env
    ]

    for env_file in env_files:
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("BRAINTRUST_API_KEY="):
                        api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                        os.environ["BRAINTRUST_API_KEY"] = api_key
                        return api_key

    raise ValueError(
        f"BRAINTRUST_API_KEY not found. Set it in environment or in one of: {env_files}"
    )


def load_jsonl(file_path: Path) -> list[dict]:
    """Load records from a JSONL file."""
    records = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"  Warning: Failed to parse line {line_num}: {e}")
    return records


def get_available_datasets() -> dict:
    """Get list of available V1.1 dataset files."""
    available = {}
    for module_id, config in V1_1_MODULES.items():
        file_path = DATASETS_DIR / config["file_pattern"]
        if file_path.exists():
            available[module_id] = {
                **config,
                "path": file_path,
                "size": file_path.stat().st_size,
            }
    return available


def upload_dataset(module_id: str, config: dict, dry_run: bool = False) -> tuple[bool, int]:
    """
    Upload a single V1.1 dataset to Braintrust.

    Returns:
        Tuple of (success, record_count)
    """
    import braintrust

    file_path = config["path"]
    # Format: M09_IdentifyPrimaryIntendedUse_V1.1
    dataset_name = f"{module_id.upper()}_{config['name']}_V1.1"

    # Load records
    records = load_jsonl(file_path)
    record_count = len(records)

    print(f"\n{'='*60}")
    print(f"Dataset: {dataset_name}")
    print(f"{'='*60}")
    print(f"  File: {file_path.name}")
    print(f"  Records: {record_count}")
    print(f"  Description: {config['description']}")

    if record_count == 0:
        print(f"  SKIP: No records found")
        return False, 0

    if dry_run:
        print(f"  [DRY RUN] Would upload {record_count} records")
        # Show sample record
        if records:
            print(f"  Sample input keys: {list(records[0].get('input', {}).keys())}")
            print(f"  Sample expected keys: {list(records[0].get('expected', {}).keys())}")
        return True, record_count

    # Upload to Braintrust
    try:
        dataset = braintrust.init_dataset(
            project=PROJECT_NAME,
            name=dataset_name,
            description=config["description"],
        )

        for i, record in enumerate(records):
            # Generate ID if not present
            record_id = record.get("id")
            if not record_id:
                # Create ID from metadata
                metadata = record.get("metadata", {})
                asin = metadata.get("asin", f"record_{i}")
                keyword = record.get("input", {}).get("keyword", "")
                if keyword:
                    record_id = f"{module_id}_{asin}_{keyword[:30]}"
                else:
                    record_id = f"{module_id}_{asin}_{i}"

            dataset.insert(
                id=record_id,
                input=record.get("input", {}),
                expected=record.get("expected"),
                metadata={
                    **record.get("metadata", {}),
                    "module_id": module_id,
                    "version": "v1.1",
                },
            )

        # Flush to ensure all records are uploaded
        dataset.flush()

        print(f"  OK: Uploaded {record_count} records")
        return True, record_count

    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False, 0


def main():
    parser = argparse.ArgumentParser(description="Upload V1.1 datasets to Braintrust")
    parser.add_argument("--module", "-m", type=str, help="Upload specific module (e.g., m09, m12)")
    parser.add_argument("--range", "-r", nargs=2, metavar=("START", "END"), help="Upload range of modules (e.g., m01 m08)")
    parser.add_argument("--list", "-l", action="store_true", help="List available datasets")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Show what would be uploaded")
    args = parser.parse_args()

    # Get available datasets
    available = get_available_datasets()

    # List mode
    if args.list:
        print("Available V1.1 datasets:")
        print(f"{'='*60}")
        for module_id in sorted(available.keys()):
            config = available[module_id]
            size_kb = config["size"] / 1024
            print(f"  {module_id}: {config['name']}")
            print(f"         File: {config['file_pattern']}")
            print(f"         Size: {size_kb:.1f} KB")
            print()
        print(f"Total: {len(available)} datasets available")
        return

    # Load API key
    print("Loading Braintrust API key...")
    load_api_key()

    print("=" * 60)
    print("Braintrust V1.1 - Upload Datasets")
    print("=" * 60)
    print(f"Project: {PROJECT_NAME}")
    print(f"Datasets dir: {DATASETS_DIR}")

    # Determine which modules to upload
    if args.module:
        module_id = args.module.lower()
        if not module_id.startswith("m"):
            module_id = f"m{module_id.zfill(2)}"

        if module_id not in available:
            print(f"\nERROR: Dataset for {module_id} not found")
            print(f"Available: {sorted(available.keys())}")
            sys.exit(1)

        modules_to_upload = {module_id: available[module_id]}
    elif args.range:
        # Filter modules by range (e.g., m01 to m08)
        start, end = args.range[0].lower(), args.range[1].lower()
        if not start.startswith("m"):
            start = f"m{start.zfill(2)}"
        if not end.startswith("m"):
            end = f"m{end.zfill(2)}"

        modules_to_upload = {}
        for module_id in sorted(available.keys()):
            # Simple string comparison works for m01, m01a, m01b, m02, etc.
            base_id = module_id.rstrip('ab')  # Get base module (m01a -> m01)
            if start <= base_id <= end:
                modules_to_upload[module_id] = available[module_id]

        if not modules_to_upload:
            print(f"\nERROR: No datasets found in range {start} to {end}")
            print(f"Available: {sorted(available.keys())}")
            sys.exit(1)
    else:
        modules_to_upload = available

    print(f"Modules to upload: {sorted(modules_to_upload.keys())}")

    if args.dry_run:
        print("\n[DRY RUN MODE]")

    # Upload each dataset
    uploaded = 0
    total_records = 0
    results = []

    for module_id in sorted(modules_to_upload.keys()):
        config = modules_to_upload[module_id]
        success, count = upload_dataset(module_id, config, dry_run=args.dry_run)
        if success:
            uploaded += 1
            total_records += count
            results.append((module_id, config["name"], count, "OK"))
        else:
            results.append((module_id, config["name"], 0, "FAILED"))

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"{'Module':<8} {'Name':<30} {'Records':<10} Status")
    print("-" * 60)
    for module_id, name, count, status in results:
        print(f"{module_id:<8} {name:<30} {count:<10} {status}")
    print("-" * 60)
    print(f"Uploaded: {uploaded}/{len(modules_to_upload)} datasets")
    print(f"Total records: {total_records}")
    print(f"{'='*60}")

    if not args.dry_run:
        print(f"\nView at: https://www.braintrust.dev/app/KCC/p/{PROJECT_NAME}/datasets")


if __name__ == "__main__":
    main()
