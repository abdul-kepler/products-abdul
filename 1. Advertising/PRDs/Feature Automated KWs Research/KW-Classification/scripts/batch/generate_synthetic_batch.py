#!/usr/bin/env python3
"""
Generate OpenAI Batch API requests for synthetic datasets using optimized prompts.

Usage:
    python scripts/batch/generate_synthetic_batch.py m01 m01a m01b m06 m07
    python scripts/batch/generate_synthetic_batch.py --all
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
SYNTHETIC_DIR = PROJECT_ROOT / "datasets" / "synthetic"
OPTIMIZED_DIR = PROJECT_ROOT / "prompts" / "optimized"
SCHEMAS_DIR = PROJECT_ROOT / "prompts" / "json_schemas" / "single"
BATCH_OUTPUT_DIR = PROJECT_ROOT / "batch_requests" / "synthetic"

# Module configurations
MODULES = {
    "m01": {
        "name": "ExtractOwnBrandEntities",
        "prompt_pattern": "m01_v*_extract_own_brand_entities_gepa_*.md",
        "schema": "m01_extract_own_brand_entities_schema.json",
        "dataset_pattern": "m01_sd*_extract_own_brand_entities.jsonl",
        "input_template": """Brand Name: {brand_name}
Title: {title}
Bullet Points: {bullet_points}
Description: {description}
Manufacturer: {manufacturer}""",
    },
    "m01a": {
        "name": "ExtractOwnBrandVariations",
        "prompt_pattern": "m01a_v*_extract_own_brand_variations_gepa_*.md",
        "schema": "m01a_extract_own_brand_variations_schema.json",
        "dataset_pattern": "m01a_sd*_extract_own_brand_variations.jsonl",
        "input_template": """Brand Name: {brand_name}""",
    },
    "m01b": {
        "name": "ExtractBrandRelatedTerms",
        "prompt_pattern": "m01b_v*_extract_brand_related_terms_gepa_*.md",
        "schema": "m01b_extract_brand_related_terms_schema.json",
        "dataset_pattern": "m01b_sd*_extract_brand_related_terms.jsonl",
        "input_template": """Brand Name: {brand_name}
Title: {title}
Bullet Points: {bullet_points}
Description: {description}
Manufacturer: {manufacturer}""",
    },
    "m06": {
        "name": "GenerateProductTypeTaxonomy",
        "prompt_pattern": "m06_v*_generate_product_type_taxonomy_gepa_*.md",
        "schema": "m06_generate_product_type_taxonomy_schema.json",
        "dataset_pattern": "m06_sd*_generate_product_type_taxonomy.jsonl",
        "input_template": """Title: {title}
Bullet Points: {bullet_points}
Description: {description}
Product Type: {product_type}
Category Root: {category_root}
Category Sub: {category_sub}""",
    },
    "m07": {
        "name": "ExtractProductAttributes",
        "prompt_pattern": "m07_v*_extract_product_attributes_gepa_*.md",
        "schema": "m07_extract_product_attributes_schema.json",
        "dataset_pattern": "m07_sd*_extract_product_attributes.jsonl",
        "input_template": """Title: {title}
Bullet Points: {bullet_points}
Description: {description}
Product Type: {product_type}
Category: {category_root} > {category_sub}
Color: {color}
Size: {size}
Material: {material}""",
    },
    "m08": {
        "name": "AssignAttributeRanks",
        "prompt_pattern": "m08_v*_assign_attribute_ranks_gepa_*.md",
        "schema": "m08_assign_attribute_ranks_schema.json",
        "dataset_pattern": "m08_sd*_assign_attribute_ranks.jsonl",
        "input_template": """Title: {title}
Bullet Points: {bullet_points}
Description: {description}
Taxonomy: {taxonomy}
Variants: {variants}
Use Cases: {use_cases}
Audiences: {audiences}""",
    },
    "m09": {
        "name": "IdentifyPrimaryIntendedUse",
        "prompt_pattern": "m09_v*_identify_primary_intended_use_gepa_*.md",
        "schema": "m09_identify_primary_intended_use_schema_v1.1.json",
        "dataset_pattern": "m09_sd*_identify_primary_intended_use.jsonl",
        "input_template": """Title: {title}
Bullet Points: {bullet_points}
Description: {description}
Taxonomy: {taxonomy}
Attribute Table: {attribute_table}
Product Attributes: {product_attributes}""",
    },
    "m10": {
        "name": "ValidatePrimaryIntendedUse",
        "prompt_pattern": "m10_v*_validate_primary_intended_use_gepa_*.md",
        "schema": "m10_validate_primary_intended_use_schema_v1.1.json",
        "dataset_pattern": "m10_sd*_validate_primary_intended_use.jsonl",
        "input_template": """Primary Use: {primary_use}
Title: {title}
Bullet Points: {bullet_points}
Description: {description}
Taxonomy: {taxonomy}
Attribute Table: {attribute_table}
Product Attributes: {product_attributes}""",
    },
    "m11": {
        "name": "IdentifyHardConstraints",
        "prompt_pattern": "m11_v*_identify_hard_constraints_gepa_*.md",
        "schema": "m11_identify_hard_constraints_schema_v1.1.json",
        "dataset_pattern": "m11_sd*_identify_hard_constraints.jsonl",
        "input_template": """Validated Intended Use: {validated_use}
Title: {title}
Bullet Points: {bullet_points}
Description: {description}
Taxonomy: {taxonomy}
Attribute Table: {attribute_table}
Product Attributes: {product_attributes}""",
    },
}


def find_latest_prompt(pattern: str) -> Path | None:
    """Find the latest version of optimized prompt."""
    matches = list(OPTIMIZED_DIR.glob(pattern))
    if not matches:
        return None
    # Sort by version number
    return sorted(matches, reverse=True)[0]


def load_prompt(filepath: Path) -> str:
    """Load prompt from file."""
    return filepath.read_text(encoding="utf-8")


def load_schema(filepath: Path) -> dict:
    """Load JSON schema."""
    return json.loads(filepath.read_text(encoding="utf-8"))


def load_synthetic_datasets(pattern: str) -> list[tuple[str, list[dict]]]:
    """Load all synthetic datasets matching pattern. Returns list of (filename, records)."""
    datasets = []
    for filepath in sorted(SYNTHETIC_DIR.glob(pattern)):
        records = []
        for line in filepath.read_text(encoding="utf-8").strip().split("\n"):
            if line.strip():
                records.append(json.loads(line))
        datasets.append((filepath.name, records))
    return datasets


def fill_input_template(template: str, record: dict) -> str:
    """Fill input template with record values."""
    result = template
    input_data = record.get("input", {})

    # Find all placeholders
    placeholders = re.findall(r'\{(\w+)\}', template)

    for key in placeholders:
        value = input_data.get(key, "")
        if value is None:
            value = ""
        elif isinstance(value, (list, dict)):
            value = json.dumps(value, ensure_ascii=False)
        result = result.replace(f"{{{key}}}", str(value))

    return result


def create_batch_request(
    custom_id: str,
    system_prompt: str,
    user_input: str,
    schema: dict,
    model: str = "gpt-4o-mini",
) -> dict:
    """Create OpenAI Batch API request."""

    # Prepare response format
    json_schema = schema.get("json_schema", schema)
    if "name" not in json_schema:
        json_schema = {
            "name": "response",
            "strict": True,
            "schema": json_schema
        }

    return {
        "custom_id": custom_id,
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
            "temperature": 0.0,
            "max_tokens": 2000,
            "response_format": {"type": "json_schema", "json_schema": json_schema},
        }
    }


def generate_module_batches(module_id: str, config: dict, output_dir: Path) -> dict:
    """Generate batch files for a module's synthetic datasets."""

    # Find prompt
    prompt_path = find_latest_prompt(config["prompt_pattern"])
    if not prompt_path:
        return {"module": module_id, "status": "error", "error": f"Prompt not found: {config['prompt_pattern']}"}

    # Load schema
    schema_path = SCHEMAS_DIR / config["schema"]
    if not schema_path.exists():
        return {"module": module_id, "status": "error", "error": f"Schema not found: {schema_path}"}

    prompt = load_prompt(prompt_path)
    schema = load_schema(schema_path)

    # Load synthetic datasets
    datasets = load_synthetic_datasets(config["dataset_pattern"])
    if not datasets:
        return {"module": module_id, "status": "error", "error": f"No datasets found: {config['dataset_pattern']}"}

    # Generate batch files
    total_records = 0
    batch_files = []

    for dataset_name, records in datasets:
        # Extract sd number from filename
        sd_match = re.search(r'_sd(\d+)_', dataset_name)
        sd_num = sd_match.group(1) if sd_match else "00"

        output_file = output_dir / f"{module_id}_sd{sd_num}_batch.jsonl"

        with open(output_file, "w", encoding="utf-8") as f:
            for idx, record in enumerate(records):
                record_id = record.get("id", f"{idx:05d}")
                custom_id = f"{module_id}_sd{sd_num}_{record_id}"

                user_input = fill_input_template(config["input_template"], record)

                batch_request = create_batch_request(
                    custom_id=custom_id,
                    system_prompt=prompt,
                    user_input=user_input,
                    schema=schema,
                )

                f.write(json.dumps(batch_request, ensure_ascii=False) + "\n")

        total_records += len(records)
        batch_files.append(str(output_file))

    return {
        "module": module_id,
        "name": config["name"],
        "status": "success",
        "prompt": prompt_path.name,
        "datasets": len(datasets),
        "records": total_records,
        "batch_files": batch_files,
    }


def main():
    """Main entry point."""
    args = sys.argv[1:]

    # Determine modules
    if "--all" in args:
        modules_to_process = list(MODULES.keys())
    elif args:
        modules_to_process = [m for m in args if m in MODULES]
    else:
        modules_to_process = list(MODULES.keys())

    if not modules_to_process:
        print(f"Error: No valid modules. Available: {list(MODULES.keys())}")
        sys.exit(1)

    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_dir = BATCH_OUTPUT_DIR / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("SYNTHETIC BATCH GENERATION")
    print("=" * 70)
    print(f"Output: {output_dir}")
    print(f"Modules: {modules_to_process}")
    print()

    results = []
    total_records = 0
    all_batch_files = []

    for module_id in modules_to_process:
        config = MODULES[module_id]
        print(f"Processing {module_id} ({config['name']})...", end=" ")

        result = generate_module_batches(module_id, config, output_dir)
        results.append(result)

        if result["status"] == "success":
            print(f"✓ {result['datasets']} datasets, {result['records']} records")
            total_records += result["records"]
            all_batch_files.extend(result["batch_files"])
        else:
            print(f"✗ {result['error']}")

    # Summary
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    successful = [r for r in results if r["status"] == "success"]
    print(f"Modules: {len(successful)}/{len(results)}")
    print(f"Total records: {total_records}")
    print(f"Batch files: {len(all_batch_files)}")

    # Save manifest
    manifest = {
        "timestamp": timestamp,
        "modules": modules_to_process,
        "total_records": total_records,
        "results": results,
        "batch_files": all_batch_files,
    }

    manifest_file = output_dir / "manifest.json"
    manifest_file.write_text(json.dumps(manifest, indent=2))
    print(f"Manifest: {manifest_file}")

    # Next steps
    print()
    print("=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print(f"Upload batches:")
    print(f"  python scripts/batch/upload_synthetic_batch.py {output_dir}")

    return output_dir


if __name__ == "__main__":
    main()
