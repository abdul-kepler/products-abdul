#!/usr/bin/env python3
"""
Download results from completed synthetic batches and create experiment results.

Creates:
1. Labeled synthetic datasets in datasets/synthetic_labeled/
2. Experiment results in experiment_results/ with proper format

Usage:
    python scripts/batch/download_synthetic_results.py <batch_dir>
"""

import csv
import json
import sys
import os
import re
from pathlib import Path
from datetime import datetime
from io import StringIO

from openai import OpenAI
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYNTHETIC_DIR = PROJECT_ROOT / "datasets" / "synthetic"
LABELED_DIR = PROJECT_ROOT / "datasets" / "synthetic_labeled"
EXPERIMENT_DIR = PROJECT_ROOT / "experiment_results"
SCHEMAS_DIR = PROJECT_ROOT / "prompts" / "json_schemas" / "single"
OPTIMIZED_DIR = PROJECT_ROOT / "prompts" / "optimized"

# Module configurations
MODULE_CONFIGS = {
    "m01": {
        "name": "ExtractOwnBrandEntities",
        "folder": "M01_ExtractOwnBrandEntities",
        "schema": "m01_extract_own_brand_entities_schema.json",
        "prompt_pattern": "m01_v*_extract_own_brand_entities_gepa_*.md",
    },
    "m01a": {
        "name": "ExtractOwnBrandVariations",
        "folder": "M01A_ExtractOwnBrandVariations",
        "schema": "m01a_extract_own_brand_variations_schema.json",
        "prompt_pattern": "m01a_v*_extract_own_brand_variations_gepa_*.md",
    },
    "m01b": {
        "name": "ExtractBrandRelatedTerms",
        "folder": "M01B_ExtractBrandRelatedTerms",
        "schema": "m01b_extract_brand_related_terms_schema.json",
        "prompt_pattern": "m01b_v*_extract_brand_related_terms_gepa_*.md",
    },
    "m06": {
        "name": "GenerateProductTypeTaxonomy",
        "folder": "M06_GenerateProductTypeTaxonomy",
        "schema": "m06_generate_product_type_taxonomy_schema.json",
        "prompt_pattern": "m06_v*_generate_product_type_taxonomy_gepa_*.md",
    },
    "m07": {
        "name": "ExtractProductAttributes",
        "folder": "M07_ExtractProductAttributes",
        "schema": "m07_extract_product_attributes_schema.json",
        "prompt_pattern": "m07_v*_extract_product_attributes_gepa_*.md",
    },
    "m08": {
        "name": "AssignAttributeRanks",
        "folder": "M08_AssignAttributeRanks",
        "schema": "m08_assign_attribute_ranks_schema.json",
        "prompt_pattern": "m08_v*_assign_attribute_ranks*.md",
    },
    "m09": {
        "name": "IdentifyPrimaryIntendedUse",
        "folder": "M09_IdentifyPrimaryIntendedUse",
        "schema": "m09_identify_primary_intended_use_schema.json",
        "prompt_pattern": "m09_v*_identify_primary_intended_use*.md",
    },
    "m10": {
        "name": "ValidatePrimaryIntendedUse",
        "folder": "M10_ValidatePrimaryIntendedUse",
        "schema": "m10_validate_primary_intended_use_schema.json",
        "prompt_pattern": "m10_v*_validate_primary_intended_use*.md",
    },
    "m11": {
        "name": "IdentifyHardConstraints",
        "folder": "M11_IdentifyHardConstraints",
        "schema": "m11_identify_hard_constraints_schema.json",
        "prompt_pattern": "m11_v*_identify_hard_constraints*.md",
    },
}


def download_batch_results(batch_id: str, output_file_id: str) -> list[dict]:
    """Download and parse batch results."""
    content = client.files.content(output_file_id)
    results = []

    for line in content.text.strip().split("\n"):
        if line.strip():
            results.append(json.loads(line))

    return results


def parse_model_output(response: dict) -> dict | None:
    """Extract model output from batch response."""
    try:
        body = response.get("response", {}).get("body", {})
        choices = body.get("choices", [])
        if choices:
            content = choices[0].get("message", {}).get("content", "")
            return json.loads(content)
    except:
        pass
    return None


def find_prompt_version(module_id: str) -> str:
    """Find the current prompt version for a module."""
    pattern = MODULE_CONFIGS[module_id]["prompt_pattern"]
    matches = list(OPTIMIZED_DIR.glob(pattern))
    if matches:
        # Extract version from filename like m01_v6_..._gepa_v1.md
        name = sorted(matches, reverse=True)[0].name
        match = re.search(r'_v(\d+)_', name)
        if match:
            return f"v{match.group(1)}"
    return "v1"


def load_schema(module_id: str) -> dict:
    """Load JSON schema for a module."""
    schema_path = SCHEMAS_DIR / MODULE_CONFIGS[module_id]["schema"]
    if schema_path.exists():
        return json.loads(schema_path.read_text())
    return {}


def process_module_batches(
    module_id: str,
    batch_results: dict[str, list[dict]],  # sd_num -> results
    output_dir: Path,
) -> dict:
    """Process all batch results for a module and create experiment files."""

    config = MODULE_CONFIGS[module_id]
    module_folder = EXPERIMENT_DIR / config["folder"]
    module_folder.mkdir(parents=True, exist_ok=True)

    prompt_version = find_prompt_version(module_id)
    schema = load_schema(module_id)
    date_str = datetime.now().strftime("%d%m%y")

    total_records = 0
    created_files = []

    for sd_num, results in batch_results.items():
        # Find original dataset
        pattern = f"{module_id}_sd{sd_num}_*.jsonl"
        dataset_files = list(SYNTHETIC_DIR.glob(pattern))
        if not dataset_files:
            continue

        dataset_file = dataset_files[0]

        # Load original records
        original_records = {}
        for line in dataset_file.read_text().strip().split("\n"):
            if line.strip():
                record = json.loads(line)
                original_records[record.get("id", "")] = record

        # Index results by record_id
        results_by_id = {}
        for result in results:
            custom_id = result.get("custom_id", "")
            # Parse: m01a_sd01_B0BQPGJ9LQ -> B0BQPGJ9LQ
            parts = custom_id.split("_")
            if len(parts) >= 3:
                record_id = "_".join(parts[2:])
                results_by_id[record_id] = result

        # Create CSV rows
        csv_rows = []
        for record_id, record in original_records.items():
            result = results_by_id.get(record_id)
            model_output = parse_model_output(result) if result else None

            if model_output:
                # Get clean ASIN from metadata, fallback to record_id
                metadata = record.get("metadata", {})
                clean_asin = metadata.get("asin", record_id)

                row = {
                    "name": "eval",
                    "ASIN": clean_asin,
                    "Brand": metadata.get("brand_name", ""),
                    "GoldenDataset": "False",  # Synthetic data
                    "input": json.dumps(record.get("input", {}), ensure_ascii=False),
                    "output": json.dumps(model_output, ensure_ascii=False),
                    "expected": json.dumps(record.get("expected", {}), ensure_ascii=False),
                    "metrics": json.dumps({"synthetic": True, "sd": sd_num, "sd_dataset": metadata.get("sd_dataset", "")}),
                }
                csv_rows.append(row)
                total_records += 1

        if not csv_rows:
            continue

        # Create experiment files
        exp_name = f"{module_id.upper()}_V{prompt_version[1:]}_sd{sd_num}_{config['name']}_{prompt_version}_{date_str}_gpt4omini_synthetic"
        csv_path = module_folder / f"{exp_name}.csv"
        meta_path = module_folder / f"{exp_name}.meta.json"

        # Write CSV
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "ASIN", "Brand", "GoldenDataset", "input", "output", "expected", "metrics"])
            writer.writeheader()
            writer.writerows(csv_rows)

        # Write meta
        meta = {
            "experiment_name": exp_name,
            "created": datetime.now().isoformat(),
            "model": "gpt-4o-mini",
            "temperature": 0,
            "source": "openai_batch_api",
            "batch_type": "synthetic",
            "synthetic_dataset": sd_num,
            "dataset_file": dataset_file.name,
            "prompt_version": prompt_version,
            "response_format": {
                "type": "json_schema",
                "json_schema": schema.get("json_schema", schema),
            },
            "records_count": len(csv_rows),
            "downloaded_at": datetime.now().isoformat(),
        }

        meta_path.write_text(json.dumps(meta, indent=2))
        created_files.append(str(csv_path))

        # Also save labeled dataset
        labeled_file = LABELED_DIR / dataset_file.name
        with open(labeled_file, "w", encoding="utf-8") as f:
            for record_id, record in original_records.items():
                result = results_by_id.get(record_id)
                model_output = parse_model_output(result) if result else None
                if model_output:
                    record["expected"] = model_output
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return {
        "module": module_id,
        "records": total_records,
        "files": created_files,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python download_synthetic_results.py <batch_dir>")
        sys.exit(1)

    batch_dir = Path(sys.argv[1])
    status_file = batch_dir / "status.json"
    upload_log_file = batch_dir / "upload_log.json"

    if not status_file.exists():
        print("Run check_synthetic_status.py first")
        sys.exit(1)

    status_data = json.loads(status_file.read_text())
    upload_log = json.loads(upload_log_file.read_text())
    statuses = status_data.get("statuses", [])

    # Create output directories
    LABELED_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("DOWNLOAD SYNTHETIC BATCH RESULTS")
    print("=" * 70)
    print(f"Labeled datasets: {LABELED_DIR}")
    print(f"Experiments: {EXPERIMENT_DIR}")
    print()

    # Group batches by module
    module_results: dict[str, dict[str, list]] = {}  # module -> {sd_num -> results}

    for status in statuses:
        if status.get("status") != "completed":
            continue

        batch_id = status["batch_id"]
        output_file_id = status.get("output_file_id")

        if not output_file_id:
            continue

        # Find batch info
        batch_info = next((b for b in upload_log["batches"] if b.get("batch_id") == batch_id), None)
        if not batch_info:
            continue

        filename = batch_info["file"]
        match = re.match(r"(m\d+[ab]?)_sd(\d+)_batch\.jsonl", filename)
        if not match:
            continue

        module_id = match.group(1)
        sd_num = match.group(2)

        print(f"Downloading {module_id}_sd{sd_num}...", end=" ")

        try:
            results = download_batch_results(batch_id, output_file_id)
            print(f"✓ {len(results)} results")

            if module_id not in module_results:
                module_results[module_id] = {}
            module_results[module_id][sd_num] = results

        except Exception as e:
            print(f"✗ Error: {e}")

    # Process each module
    print()
    print("Creating experiment files...")
    total_experiments = 0

    for module_id, batch_results in module_results.items():
        if module_id not in MODULE_CONFIGS:
            continue

        result = process_module_batches(module_id, batch_results, EXPERIMENT_DIR)
        print(f"  {module_id}: {result['records']} records, {len(result['files'])} files")
        total_experiments += len(result["files"])

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Modules processed: {len(module_results)}")
    print(f"Experiment files created: {total_experiments}")
    print(f"Labeled datasets: {LABELED_DIR}")

    # Save download log
    download_log = batch_dir / "download_log.json"
    download_log.write_text(json.dumps({
        "downloaded_at": datetime.now().isoformat(),
        "modules": list(module_results.keys()),
        "total_experiments": total_experiments,
    }, indent=2))


if __name__ == "__main__":
    main()
