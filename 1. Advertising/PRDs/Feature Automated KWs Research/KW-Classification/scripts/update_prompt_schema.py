#!/usr/bin/env python3
"""
Update a Braintrust prompt with JSON schema for structured outputs.

Usage:
    python scripts/update_prompt_schema.py m08_v2
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import PROJECT_ID, PROJECT_NAME, load_api_key, SCHEMAS_DIR

try:
    from braintrust_api import Braintrust as BraintrustAPI
except ImportError:
    print("Error: Run: pip install braintrust-api")
    sys.exit(1)


# Schema mapping
SCHEMA_CONFIGS = {
    # M01 variants
    "m01": {
        "schema_file": "m01_extract_own_brand_entities_schema.json",
        "prompt_slug": "extract-own-brand-entities",
    },
    "m01a": {
        "schema_file": "m01a_extract_own_brand_variations_schema.json",
        "prompt_slug": "extract-own-brand-variations",
    },
    "m01b": {
        "schema_file": "m01b_extract_brand_related_terms_schema.json",
        "prompt_slug": "extract-brand-related-terms",
    },
    # M02 variants
    "m02": {
        "schema_file": "m02_classify_own_brand_keywords_schema.json",
        "prompt_slug": "classify-own-brand-keywords",
    },
    "m02_v6": {
        "schema_file": "m02_classify_own_brand_keywords_schema.json",
        "prompt_slug": "m02_v6",
    },
    "m02b": {
        "schema_file": "m02b_classify_own_brand_keywords_schema.json",
        "prompt_slug": "classify-own-brand-keywords-path-b",
    },
    # M04 variants
    "m04": {
        "schema_file": "m04_classify_competitor_brand_keywords_schema.json",
        "prompt_slug": "classify-competitor-brand-keywords",
    },
    "m04b": {
        "schema_file": "m04b_classify_competitor_brand_keywords_schema.json",
        "prompt_slug": "classify-competitor-brand-keywords-path-b",
    },
    # M05 variants
    "m05": {
        "schema_file": "m05_classify_nonbranded_keywords_schema.json",
        "prompt_slug": "classify-nonbranded-keywords",
    },
    "m05b": {
        "schema_file": "m05b_classify_nonbranded_keywords_schema.json",
        "prompt_slug": "classify-nonbranded-keywords-path-b",
    },
    # M03
    "m03": {
        "schema_file": "m03_generate_competitor_entities_schema.json",
        "prompt_slug": "generate-competitor-entities",
    },
    # M06 variants
    "m06": {
        "schema_file": "m06_generate_product_type_taxonomy_schema.json",
        "prompt_slug": "generate-product-type-taxonomy",
    },
    "m06_v2": {
        "schema_file": "m06_generate_product_type_taxonomy_schema.json",
        "prompt_slug": "m06_v2",
    },
    # M07
    "m07": {
        "schema_file": "m07_extract_product_attributes_schema.json",
        "prompt_slug": "extract-product-attributes",
    },
    # M08 variants
    "m08": {
        "schema_file": "m08_assign_attribute_ranks_schema.json",
        "prompt_slug": "assign-attribute-ranks",
    },
    "m08_v2": {
        "schema_file": "m08_v2_assign_attribute_ranks_schema.json",
        "prompt_slug": "m08_v2",
    },
    # M09-M11 (V1.1)
    "m09": {
        "schema_file": "m09_identify_primary_intended_use_schema_v1.1.json",
        "prompt_slug": "identify-primary-intended-use-v1-1",
    },
    "m10": {
        "schema_file": "m10_validate_primary_intended_use_schema_v1.1.json",
        "prompt_slug": "validate-primary-intended-use-v1-1",
    },
    "m11": {
        "schema_file": "m11_identify_hard_constraints_schema_v1.1.json",
        "prompt_slug": "identify-hard-constraints-v1-1",
    },
    # M12-M16 (V1.1)
    "m12": {
        "schema_file": "m12_hard_constraint_violation_check_schema_v1.1.json",
        "prompt_slug": "hard-constraint-violation-check-v1-1",
    },
    "m12b": {
        "schema_file": "m12b_combined_classification_schema_v1.1.json",
        "prompt_slug": "combined-classification-v1-1",
    },
    "m13": {
        "schema_file": "m13_product_type_check_schema_v1.1.json",
        "prompt_slug": "product-type-check-v1-1",
    },
    "m14": {
        "schema_file": "m14_primary_use_check_same_type_schema_v1.1.json",
        "prompt_slug": "primary-use-check-same-type-v1-1",
    },
    "m15": {
        "schema_file": "m15_substitute_check_schema_v1.1.json",
        "prompt_slug": "substitute-check-v1-1",
    },
    "m16": {
        "schema_file": "m16_complementary_check_schema_v1.1.json",
        "prompt_slug": "complementary-check-v1-1",
    },
}


def update_prompt_with_schema(client: BraintrustAPI, module_id: str):
    """Update prompt with JSON schema for structured output."""
    if module_id not in SCHEMA_CONFIGS:
        print(f"Error: No schema config for {module_id}")
        print(f"Available: {list(SCHEMA_CONFIGS.keys())}")
        return None

    config = SCHEMA_CONFIGS[module_id]
    schema_path = SCHEMAS_DIR / config["schema_file"]

    if not schema_path.exists():
        print(f"Error: Schema file not found: {schema_path}")
        return None

    # Load schema
    with open(schema_path) as f:
        schema_data = json.load(f)

    # Find existing prompt
    prompts = list(client.prompts.list(project_id=PROJECT_ID))
    existing = next((p for p in prompts if p.slug == config["prompt_slug"]), None)

    if not existing:
        print(f"Error: Prompt not found: {config['prompt_slug']}")
        return None

    print(f"Found prompt: {existing.name} (ID: {existing.id})")

    # Get current prompt data
    prompt_detail = client.prompts.retrieve(prompt_id=existing.id)
    current_data = prompt_detail.prompt_data

    # Convert Pydantic model to dict if needed
    if hasattr(current_data, 'model_dump'):
        current_data = current_data.model_dump(exclude_none=True)
    elif hasattr(current_data, 'dict'):
        current_data = current_data.dict()

    def remove_nulls(obj):
        """Recursively remove null values from dict/list."""
        if isinstance(obj, dict):
            return {k: remove_nulls(v) for k, v in obj.items() if v is not None}
        elif isinstance(obj, list):
            return [remove_nulls(item) for item in obj if item is not None]
        return obj

    current_data = remove_nulls(current_data)

    # Update options with response_format
    new_options = current_data.get("options", {}) or {}
    new_options["params"] = new_options.get("params", {}) or {}
    new_options["params"]["response_format"] = schema_data

    # Update prompt
    try:
        updated = client.prompts.update(
            prompt_id=existing.id,
            prompt_data={
                "prompt": current_data.get("prompt", {}),
                "options": new_options,
            },
        )
        print(f"✓ Updated prompt with JSON schema")
        print(f"  Schema: {config['schema_file']}")
        return updated
    except Exception as e:
        print(f"✗ Error updating prompt: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Update prompt with JSON schema")
    parser.add_argument("module", help="Module ID (e.g., m08_v2)")
    parser.add_argument("--list", action="store_true", help="List available modules")

    args = parser.parse_args()

    if args.list:
        print("Available modules with schemas:")
        for mid in SCHEMA_CONFIGS:
            print(f"  {mid}")
        return

    # Load API key
    try:
        api_key = load_api_key()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    client = BraintrustAPI(api_key=api_key)

    print(f"Project: {PROJECT_NAME}")
    print(f"Updating: {args.module}")
    print()

    update_prompt_with_schema(client, args.module)


if __name__ == "__main__":
    main()
