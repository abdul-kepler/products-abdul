#!/usr/bin/env python3
"""
Generate OpenAI Batch API request files for all modules.

Creates one JSONL file per module with all records from the dataset.
Each line is a batch request in OpenAI's format.

Usage:
    python scripts/batch/generate_batch_requests.py [module1 module2 ...]

    # Generate for all modules:
    python scripts/batch/generate_batch_requests.py

    # Generate for specific modules:
    python scripts/batch/generate_batch_requests.py m13 m14 m15
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATASETS_DIR = PROJECT_ROOT / "datasets"
PROMPTS_DIR = PROJECT_ROOT / "prompts" / "modules"
SCHEMAS_DIR = PROJECT_ROOT / "prompts" / "json_schemas"
BATCH_OUTPUT_DIR = PROJECT_ROOT / "batch_requests"

# Module configurations - maps module ID to files
MODULES = {
    "m01": {
        "name": "ExtractOwnBrandEntities",
        "dataset": "m01_extract_own_brand_entities.jsonl",
        "prompt": "m01_extract_own_brand_entities.md",
        "schema": "m01_extract_own_brand_entities_schema.json",
    },
    "m01a": {
        "name": "ExtractOwnBrandVariations",
        "dataset": "m01a_extract_own_brand_variations.jsonl",
        "prompt": "m01a_extract_own_brand_variations.md",
        "schema": "m01a_extract_own_brand_variations_schema.json",
    },
    "m01b": {
        "name": "ExtractBrandRelatedTerms",
        "dataset": "m01b_extract_brand_related_terms.jsonl",
        "prompt": "m01b_extract_brand_related_terms.md",
        "schema": "m01b_extract_brand_related_terms_schema.json",
    },
    "m02": {
        "name": "ClassifyOwnBrandKeywords",
        "dataset": "m02_classify_own_brand_keywords.jsonl",
        "prompt": "m02_classify_own_brand_keywords.md",
        "schema": "m02_classify_own_brand_keywords_schema.json",
    },
    "m02b": {
        "name": "ClassifyOwnBrandKeywords_PathB",
        "dataset": "m02b_classify_own_brand_keywords.jsonl",
        "prompt": "m02b_classify_own_brand_keywords.md",
        "schema": "m02b_classify_own_brand_keywords_schema.json",
    },
    "m03": {
        "name": "GenerateCompetitorEntities",
        "dataset": "m03_generate_competitor_entities.jsonl",
        "prompt": "m03_generate_competitor_entities.md",
        "schema": "m03_generate_competitor_entities_schema.json",
    },
    "m04": {
        "name": "ClassifyCompetitorBrandKeywords",
        "dataset": "m04_classify_competitor_brand_keywords.jsonl",
        "prompt": "m04_classify_competitor_brand_keywords.md",
        "schema": "m04_classify_competitor_brand_keywords_schema.json",
    },
    "m04b": {
        "name": "ClassifyCompetitorBrandKeywords_PathB",
        "dataset": "m04b_classify_competitor_brand_keywords.jsonl",
        "prompt": "m04b_classify_competitor_brand_keywords.md",
        "schema": "m04b_classify_competitor_brand_keywords_schema.json",
    },
    "m05": {
        "name": "ClassifyNonBrandedKeywords",
        "dataset": "m05_classify_nonbranded_keywords.jsonl",
        "prompt": "m05_classify_nonbranded_keywords.md",
        "schema": "m05_classify_nonbranded_keywords_schema.json",
    },
    "m05b": {
        "name": "ClassifyNonBrandedKeywords_PathB",
        "dataset": "m05b_classify_nonbranded_keywords.jsonl",
        "prompt": "m05b_classify_nonbranded_keywords.md",
        "schema": "m05b_classify_nonbranded_keywords_schema.json",
    },
    "m06": {
        "name": "GenerateProductTypeTaxonomy",
        "dataset": "m06_generate_product_type_taxonomy.jsonl",
        "prompt": "m06_generate_product_type_taxonomy.md",
        "schema": "m06_generate_product_type_taxonomy_schema.json",
    },
    "m07": {
        "name": "ExtractProductAttributes",
        "dataset": "m07_extract_product_attributes.jsonl",
        "prompt": "m07_extract_product_attributes.md",
        "schema": "m07_extract_product_attributes_schema.json",
    },
    "m08": {
        "name": "AssignAttributeRanks",
        "dataset": "m08_assign_attribute_ranks.jsonl",
        "prompt": "m08_assign_attribute_ranks.md",
        "schema": "m08_assign_attribute_ranks_schema.json",
    },
    "m09": {
        "name": "IdentifyPrimaryIntendedUse",
        "dataset": "m09_identify_primary_intended_use_v1.1.jsonl",
        "prompt": "m09_identify_primary_intended_use_v1.1.md",
        "schema": "m09_identify_primary_intended_use_schema_v1.1.json",
    },
    "m10": {
        "name": "ValidatePrimaryIntendedUse",
        "dataset": "m10_validate_primary_intended_use_v1.1.jsonl",
        "prompt": "m10_validate_primary_intended_use_v1.1.md",
        "schema": "m10_validate_primary_intended_use_schema_v1.1.json",
    },
    "m11": {
        "name": "IdentifyHardConstraints",
        "dataset": "m11_identify_hard_constraints_v1.1.jsonl",
        "prompt": "m11_identify_hard_constraints_v1.1.md",
        "schema": "m11_identify_hard_constraints_schema_v1.1.json",
    },
    "m12": {
        "name": "CheckHardConstraintViolation",
        "dataset": "m12_check_hard_constraint_v1.1.jsonl",
        "prompt": "m12_hard_constraint_violation_check_v1.1.md",
        "schema": "m12_hard_constraint_violation_check_schema_v1.1.json",
    },
    "m12b": {
        "name": "CombinedClassification",
        "dataset": "m12b_combined_classification_v1.1.jsonl",
        "prompt": "m12b_combined_classification_v1.1.md",
        "schema": "m12b_combined_classification_schema_v1.1.json",
    },
    "m13": {
        "name": "CheckProductType",
        "dataset": "m13_check_product_type_v1.1.jsonl",
        "prompt": "m13_product_type_check_v1.1.md",
        "schema": "m13_product_type_check_schema_v1.1.json",
    },
    "m14": {
        "name": "CheckPrimaryUseSameType",
        "dataset": "m14_check_primary_use_same_type_v1.1.jsonl",
        "prompt": "m14_primary_use_check_same_type_v1.1.md",
        "schema": "m14_primary_use_check_same_type_schema_v1.1.json",
    },
    "m15": {
        "name": "CheckSubstitute",
        "dataset": "m15_check_substitute_v1.1.jsonl",
        "prompt": "m15_substitute_check_v1.1.md",
        "schema": "m15_substitute_check_schema_v1.1.json",
    },
    "m16": {
        "name": "CheckComplementary",
        "dataset": "m16_check_complementary_v1.1.jsonl",
        "prompt": "m16_complementary_check_v1.1.md",
        "schema": "m16_complementary_check_schema_v1.1.json",
    },
}


def load_dataset(filepath: Path) -> list[dict]:
    """Load JSONL dataset."""
    records = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def load_prompt_template(filepath: Path) -> str:
    """Load prompt template from markdown file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def parse_structured_template(template: str) -> dict:
    """
    Parse template into structured components for proper OpenAI message format.

    Looks for markers:
    - <!-- SYSTEM_INSTRUCTIONS --> ... <!-- /SYSTEM_INSTRUCTIONS -->
    - <!-- EXAMPLES --> ... <!-- /EXAMPLES -->
    - <!-- USER_INPUT --> ... <!-- /USER_INPUT -->

    If markers not found, returns the entire template as legacy format.
    """
    import re

    result = {
        "system_instructions": None,
        "examples": [],
        "user_input": None,
        "is_structured": False
    }

    # Check for structured format markers
    system_match = re.search(
        r'<!-- SYSTEM_INSTRUCTIONS -->(.*?)<!-- /SYSTEM_INSTRUCTIONS -->',
        template,
        re.DOTALL
    )
    examples_match = re.search(
        r'<!-- EXAMPLES -->(.*?)<!-- /EXAMPLES -->',
        template,
        re.DOTALL
    )
    user_input_match = re.search(
        r'<!-- USER_INPUT -->(.*?)<!-- /USER_INPUT -->',
        template,
        re.DOTALL
    )

    if system_match and user_input_match:
        result["is_structured"] = True
        result["system_instructions"] = system_match.group(1).strip()
        result["user_input"] = user_input_match.group(1).strip()

        # Parse examples if present
        if examples_match:
            examples_text = examples_match.group(1).strip()
            # Parse individual examples: <!-- EXAMPLE_USER -->...<!-- /EXAMPLE_USER -->
            # <!-- EXAMPLE_ASSISTANT -->...<!-- /EXAMPLE_ASSISTANT -->
            example_pairs = re.findall(
                r'<!-- EXAMPLE_USER -->(.*?)<!-- /EXAMPLE_USER -->\s*'
                r'<!-- EXAMPLE_ASSISTANT -->(.*?)<!-- /EXAMPLE_ASSISTANT -->',
                examples_text,
                re.DOTALL
            )
            for user_ex, assistant_ex in example_pairs:
                result["examples"].append({
                    "user": user_ex.strip(),
                    "assistant": assistant_ex.strip()
                })

    return result


def load_schema(filepath: Path) -> dict:
    """Load JSON schema."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def fill_prompt_template(template: str, record: dict) -> str:
    """Replace placeholders in template with record values."""
    result = template

    # Find all placeholders like {{key}}
    import re
    placeholders = re.findall(r'\{\{(\w+)\}\}', template)

    for key in placeholders:
        placeholder = f"{{{{{key}}}}}"
        value = record.get(key) or record.get("input", {}).get(key)

        if value is None:
            value = "null"  # Explicit null for LLM clarity
        elif isinstance(value, list):
            # Always use JSON array format for consistency with examples
            value = json.dumps(value)
        elif isinstance(value, dict):
            # Compact JSON to match example format
            value = json.dumps(value)
        else:
            value = str(value) if value is not None else ""

        result = result.replace(placeholder, value)

    return result


def create_batch_request(
    custom_id: str,
    prompt: str,
    schema: dict,
    model: str = "gpt-4o-mini",
    temperature: float = 0.0,
    max_tokens: int = 2000,
    structured_components: dict = None
) -> dict:
    """
    Create a single batch request in OpenAI's format.

    If structured_components is provided, uses proper message structure:
    - System message: instructions only
    - Example messages with name field (example_user/example_assistant)
    - User message: actual data to classify

    Otherwise, uses legacy single system message (for backward compatibility).
    """

    # Prepare JSON schema for response_format
    json_schema = schema.get("json_schema", schema)

    if "name" in json_schema and "schema" in json_schema:
        response_format = {"type": "json_schema", "json_schema": json_schema}
    else:
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "response",
                "strict": True,
                "schema": json_schema
            }
        }

    # Build messages array
    if structured_components and structured_components.get("is_structured"):
        messages = []

        # 1. System message with instructions only
        messages.append({
            "role": "system",
            "content": structured_components["system_instructions"]
        })

        # 2. Few-shot examples with proper user/assistant roles
        for example in structured_components.get("examples", []):
            messages.append({
                "role": "user",
                "content": example["user"]
            })
            messages.append({
                "role": "assistant",
                "content": example["assistant"]
            })

        # 3. User message with actual data to classify
        messages.append({
            "role": "user",
            "content": structured_components["user_input"]
        })
    else:
        # Legacy: single system message (for templates without markers)
        messages = [{"role": "system", "content": prompt}]

    return {
        "custom_id": custom_id,
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "response_format": response_format,
        }
    }


def generate_module_batch(module_id: str, config: dict, output_dir: Path) -> dict:
    """Generate batch request file for a single module."""

    # Load files
    dataset_path = DATASETS_DIR / config["dataset"]
    prompt_path = PROMPTS_DIR / config["prompt"]
    schema_path = SCHEMAS_DIR / config["schema"]

    # Check files exist
    missing = []
    if not dataset_path.exists():
        missing.append(f"dataset: {dataset_path}")
    if not prompt_path.exists():
        missing.append(f"prompt: {prompt_path}")
    if not schema_path.exists():
        missing.append(f"schema: {schema_path}")

    if missing:
        return {
            "module": module_id,
            "status": "error",
            "error": f"Missing files: {', '.join(missing)}",
            "records": 0
        }

    # Load data
    records = load_dataset(dataset_path)
    prompt_template = load_prompt_template(prompt_path)
    schema = load_schema(schema_path)

    # Check if template uses structured format (with markers)
    template_structure = parse_structured_template(prompt_template)
    is_structured = template_structure["is_structured"]

    # Generate batch requests
    output_file = output_dir / f"{module_id}_batch.jsonl"

    with open(output_file, "w", encoding="utf-8") as f:
        for idx, record in enumerate(records):
            # Create custom_id: module_recordIndex
            custom_id = f"{module_id}_{idx:05d}"

            if is_structured:
                # New structured format: fill only user_input with record data
                filled_user_input = fill_prompt_template(
                    template_structure["user_input"], record
                )
                # Create structured components with filled user input
                structured = {
                    "is_structured": True,
                    "system_instructions": template_structure["system_instructions"],
                    "examples": template_structure["examples"],
                    "user_input": filled_user_input
                }
                batch_request = create_batch_request(
                    custom_id=custom_id,
                    prompt="",  # Not used in structured mode
                    schema=schema,
                    structured_components=structured
                )
            else:
                # Legacy format: fill entire template
                filled_prompt = fill_prompt_template(prompt_template, record)
                batch_request = create_batch_request(
                    custom_id=custom_id,
                    prompt=filled_prompt,
                    schema=schema
                )

            # Write as JSONL
            f.write(json.dumps(batch_request, ensure_ascii=False) + "\n")

    return {
        "module": module_id,
        "name": config["name"],
        "status": "success",
        "records": len(records),
        "output_file": str(output_file),
        "format": "structured" if is_structured else "legacy"
    }


def main():
    """Main entry point."""

    # Parse arguments
    args = sys.argv[1:]

    # Determine which modules to process
    if args:
        modules_to_process = [m for m in args if m in MODULES]
        if not modules_to_process:
            print(f"Error: No valid modules specified. Available: {list(MODULES.keys())}")
            sys.exit(1)
    else:
        modules_to_process = list(MODULES.keys())

    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_dir = BATCH_OUTPUT_DIR / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("BATCH REQUEST GENERATION")
    print("=" * 70)
    print(f"Output directory: {output_dir}")
    print(f"Modules to process: {len(modules_to_process)}")
    print()

    # Process each module
    results = []
    total_records = 0

    for module_id in modules_to_process:
        config = MODULES[module_id]
        print(f"Processing {module_id} ({config['name']})...", end=" ")

        result = generate_module_batch(module_id, config, output_dir)
        results.append(result)

        if result["status"] == "success":
            print(f"✓ {result['records']} records")
            total_records += result["records"]
        else:
            print(f"✗ {result['error']}")

    # Summary
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    successful = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] == "error"]

    print(f"Successful: {len(successful)}/{len(results)} modules")
    print(f"Total records: {total_records}")
    print(f"Output directory: {output_dir}")

    if failed:
        print()
        print("Failed modules:")
        for r in failed:
            print(f"  - {r['module']}: {r['error']}")

    # Save manifest
    manifest = {
        "timestamp": timestamp,
        "modules_processed": len(modules_to_process),
        "total_records": total_records,
        "results": results
    }

    manifest_file = output_dir / "manifest.json"
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"\nManifest saved: {manifest_file}")

    # Print next steps
    print()
    print("=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("1. Review generated batch files in:", output_dir)
    print("2. Upload batches to OpenAI:")
    print(f"   python scripts/batch/upload_batch.py {output_dir}")
    print("3. Check status:")
    print("   python scripts/batch/check_batch_status.py <batch_id>")


if __name__ == "__main__":
    main()
