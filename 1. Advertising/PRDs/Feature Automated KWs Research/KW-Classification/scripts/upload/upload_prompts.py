#!/usr/bin/env python3
"""
Upload prompts to Braintrust with mapping support.

File naming convention: {module}_v{version}_{action}_{object}.md
Example: m12_v1_check_hard_constraint.md

Usage:
    # Upload all prompts
    python scripts/upload/upload_prompts.py

    # Upload specific module
    python scripts/upload/upload_prompts.py --module m01

    # Upload by local file path
    python scripts/upload/upload_prompts.py --file prompts/modules/single/m08_v1_assign_attribute_ranks.md

    # List available modules
    python scripts/upload/upload_prompts.py --list

    # Show current mappings
    python scripts/upload/upload_prompts.py --show-mapping
"""

import argparse
import json
import sys
import yaml
from pathlib import Path
from datetime import datetime

# Add scripts folder to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    PROJECT_NAME,
    PROJECT_ROOT,
    PROMPTS_DIR,
    SCHEMAS_DIR,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    load_api_key,
)
from mapping_loader import MappingLoader, get_mappings

import braintrust

# Legacy mapping file (for backwards compatibility)
LEGACY_MAPPING_FILE = PROJECT_ROOT / "evaluation_KD" / "evaluation_experimentV5" / "prompt_mappings.yaml"


# ============ Mapping Functions ============

def load_mapping() -> dict:
    """Load prompt mappings from legacy YAML file."""
    if not LEGACY_MAPPING_FILE.exists():
        return {"prompts": [], "legacy_prompt_ids": [], "prompts_to_delete": []}

    with open(LEGACY_MAPPING_FILE, "r") as f:
        return yaml.safe_load(f) or {"prompts": []}


def save_mapping(mapping: dict):
    """Save prompt mappings to legacy YAML file."""
    mapping["version"] = "1.0"
    mapping["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(LEGACY_MAPPING_FILE, "w") as f:
        yaml.dump(mapping, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print(f"  Updated legacy mapping: {LEGACY_MAPPING_FILE}")


def update_resource_mappings(prompt_key: str, updates: dict):
    """Update central resource_mappings.yaml via MappingLoader."""
    try:
        loader = get_mappings()
        loader.update_prompt(prompt_key, updates)
        print(f"  Updated resource_mappings.yaml: {prompt_key}")
    except Exception as e:
        print(f"  Warning: Could not update resource_mappings.yaml: {e}")


def find_mapping_by_file(mapping: dict, local_file: str) -> dict | None:
    """Find existing mapping by local file path."""
    local_file_norm = str(local_file).replace(str(PROJECT_ROOT) + "/", "")

    for p in mapping.get("prompts", []):
        if p.get("local_file") == local_file_norm:
            return p
    return None


def find_mapping_by_slug(mapping: dict, slug: str) -> dict | None:
    """Find existing mapping by Braintrust slug."""
    for p in mapping.get("prompts", []):
        if p.get("braintrust_slug") == slug:
            return p
    return None


def update_or_add_mapping(mapping: dict, new_entry: dict):
    """Update existing mapping entry or add new one."""
    local_file = new_entry.get("local_file")

    for i, p in enumerate(mapping.get("prompts", [])):
        if p.get("local_file") == local_file:
            mapping["prompts"][i] = new_entry
            return

    if "prompts" not in mapping:
        mapping["prompts"] = []
    mapping["prompts"].append(new_entry)


def show_mapping():
    """Display current prompt mappings from central resource_mappings.yaml."""
    try:
        loader = get_mappings()
        loader.print_summary()

        print("\n" + "="*80)
        print("PROMPT MAPPINGS (from resource_mappings.yaml)")
        print("="*80)

        print(f"\n{'Key':<20} {'Braintrust ID':<38} {'Local File'}")
        print("-"*100)

        for key in loader.list_prompts():
            prompt = loader.get_prompt(key)
            bt_id = prompt.get("braintrust_id", "")
            bt_display = bt_id if bt_id else "---"
            local = prompt.get("local_file", "")[:45]
            print(f"{key:<20} {bt_display:<38} {local}")

    except Exception as e:
        print(f"Error loading mappings: {e}")
        mapping = load_mapping()
        prompts = mapping.get("prompts", [])
        print(f"\nLegacy mappings: {len(prompts)} prompts")

        to_delete = mapping.get("prompts_to_delete", [])
        if to_delete:
            print(f"\n⚠️  Prompts to delete from Braintrust:")
            for p in to_delete:
                print(f"  - {p.get('braintrust_id')}: {p.get('reason')}")


# V1.1 modules with their specific file names
# Naming convention:
#   name: PascalCase matching file action_object (e.g., ExtractOwnBrandEntities)
#   slug: kebab-case matching file action-object (e.g., extract-own-brand-entities)
#   description: Brief description without version prefix
V1_1_MODULES = {
    # ===== M01-M08: Brand and Keyword Classification =====
    "m01": {
        "name": "ExtractOwnBrandEntities",
        "slug": "extract-own-brand-entities",
        "prompt_file": "m01_v1_extract_own_brand_entities.md",
        "schema_file": "m01_extract_own_brand_entities_schema.json",
        "type": "extraction",
        "description": "Extract brand entities from product data (brand name, typos, sub-brands)",
        "model": "gpt-4o",
        "temperature": 0.0,
        "max_tokens": 1024,
    },
    "m01a": {
        "name": "ExtractOwnBrandVariations",
        "slug": "extract-own-brand-variations",
        "prompt_file": "m01a_v1_extract_own_brand_variations.md",
        "schema_file": "m01a_extract_own_brand_variations_schema.json",
        "type": "generation",
        "description": "Generate brand name search variations (typos, truncations, phonetic)",
        "model": "gpt-4o-mini",
        "temperature": 0.3,
        "max_tokens": 512,
    },
    "m01b": {
        "name": "ExtractBrandRelatedTerms",
        "slug": "extract-brand-related-terms",
        "prompt_file": "m01b_v1_extract_brand_related_terms.md",
        "schema_file": "m01b_extract_brand_related_terms_schema.json",
        "type": "extraction",
        "description": "Extract product lines, technologies, and manufacturer from listing",
        "model": "gpt-4o-mini",
        "temperature": 0.0,
        "max_tokens": 1024,
    },
    "m02": {
        "name": "ClassifyOwnBrandKeywords",
        "slug": "classify-own-brand-keywords",
        "prompt_file": "m02_v1_classify_own_brand_keywords.md",
        "schema_file": "m02_classify_own_brand_keywords_schema.json",
        "type": "binary_classifier",
        "description": "Classify if keyword matches own brand (OB classification)",
        "model": "gpt-4o-mini",
        "temperature": 0.0,
        "max_tokens": 512,
    },
    "m03": {
        "name": "GenerateCompetitorEntities",
        "slug": "generate-competitor-entities",
        "prompt_file": "m03_v1_generate_competitor_entities.md",
        "schema_file": "m03_generate_competitor_entities_schema.json",
        "type": "extraction",
        "description": "Generate competitor brand entities for the product category",
        "model": "gpt-4o-mini",
        "temperature": 0.3,
        "max_tokens": 2048,
    },
    "m04": {
        "name": "ClassifyCompetitorBrandKeywords",
        "slug": "classify-competitor-brand-keywords",
        "prompt_file": "m04_v1_classify_competitor_brand_keywords.md",
        "schema_file": "m04_classify_competitor_brand_keywords_schema.json",
        "type": "binary_classifier",
        "description": "Classify if keyword is competitor brand (CB classification)",
        "model": "gpt-4o",
        "temperature": 0.0,
        "max_tokens": 512,
    },
    "m05": {
        "name": "ClassifyNonBrandedKeywords",
        "slug": "classify-nonbranded-keywords",
        "prompt_file": "m05_v1_classify_nonbranded_keywords.md",
        "schema_file": "m05_classify_nonbranded_keywords_schema.json",
        "type": "binary_classifier",
        "description": "Classify if keyword is non-branded (NB classification)",
        "model": "gpt-4o-mini",
        "temperature": 0.0,
        "max_tokens": 512,
    },
    # ===== Path B: Uses M01a/M01b outputs instead of M01/M03 =====
    "m02b": {
        "name": "ClassifyOwnBrandKeywordsPathB",
        "slug": "classify-own-brand-keywords-path-b",
        "prompt_file": "m02b_v1_classify_own_brand_keywords.md",
        "schema_file": "m02b_classify_own_brand_keywords_schema.json",
        "type": "binary_classifier",
        "description": "Classify if keyword matches own brand using variations context (Path B)",
        "model": "gpt-4o-mini",
        "temperature": 0.0,
        "max_tokens": 512,
    },
    "m04b": {
        "name": "ClassifyCompetitorBrandKeywordsPathB",
        "slug": "classify-competitor-brand-keywords-path-b",
        "prompt_file": "m04b_v1_classify_competitor_brand_keywords.md",
        "schema_file": "m04b_classify_competitor_brand_keywords_schema.json",
        "type": "binary_classifier",
        "description": "Classify if keyword is competitor brand using variations context (Path B)",
        "model": "gpt-4o-mini",
        "temperature": 0.0,
        "max_tokens": 512,
    },
    "m05b": {
        "name": "ClassifyNonBrandedKeywordsPathB",
        "slug": "classify-nonbranded-keywords-path-b",
        "prompt_file": "m05b_v1_classify_nonbranded_keywords.md",
        "schema_file": "m05b_classify_nonbranded_keywords_schema.json",
        "type": "binary_classifier",
        "description": "Classify if keyword is non-branded using variations context (Path B)",
        "model": "gpt-4o-mini",
        "temperature": 0.0,
        "max_tokens": 512,
    },
    "m06": {
        "name": "GenerateProductTypeTaxonomy",
        "slug": "generate-product-type-taxonomy",
        "prompt_file": "m06_v1_generate_product_type_taxonomy.md",
        "schema_file": "m06_generate_product_type_taxonomy_schema.json",
        "type": "extraction",
        "description": "Generate product type taxonomy (category hierarchy)",
        "model": "gpt-4o-mini",
        "temperature": 0.0,
        "max_tokens": 1024,
    },
    "m07": {
        "name": "ExtractProductAttributes",
        "slug": "extract-product-attributes",
        "prompt_file": "m07_v1_extract_product_attributes.md",
        "schema_file": "m07_extract_product_attributes_schema.json",
        "type": "extraction",
        "description": "Extract product attributes from listing data",
        "model": "gpt-4o-mini",
        "temperature": 0.0,
        "max_tokens": 2048,
    },
    "m08": {
        "name": "AssignAttributeRanks",
        "slug": "assign-attribute-ranks",
        "prompt_file": "m08_v1_assign_attribute_ranks.md",
        "schema_file": "m08_assign_attribute_ranks_schema.json",
        "type": "ranking",
        "description": "Assign importance ranks to product attributes",
        "model": "gpt-4o-mini",
        "temperature": 0.0,
        "max_tokens": 2048,
    },
    # ===== M09-M16: Product Foundation and Keyword Classification =====
    "m09": {
        "name": "IdentifyPrimaryIntendedUse",
        "slug": "identify-primary-intended-use",
        "prompt_file": "m09_v1_identify_primary_intended_use.md",
        "schema_file": "m09_identify_primary_intended_use_schema_v1.1.json",
        "type": "extraction",
        "description": "Determine the single core reason the product exists",
        "model": "gpt-4o-mini",
        "temperature": 0.0,
        "max_tokens": 512,
    },
    "m10": {
        "name": "ValidatePrimaryIntendedUse",
        "slug": "validate-primary-intended-use",
        "prompt_file": "m10_v1_validate_primary_intended_use.md",
        "schema_file": "m10_validate_primary_intended_use_schema_v1.1.json",
        "type": "validation",
        "description": "Validate and clean the primary intended use phrase",
        "model": "gpt-4o-mini",
        "temperature": 0.0,
        "max_tokens": 512,
    },
    "m11": {
        "name": "IdentifyHardConstraints",
        "slug": "identify-hard-constraints",
        "prompt_file": "m11_v1_identify_hard_constraints.md",
        "schema_file": "m11_identify_hard_constraints_schema_v1.1.json",
        "type": "extraction",
        "description": "Identify non-negotiable product attributes (hard constraints)",
        "model": "gpt-4o-mini",
        "temperature": 0.0,
        "max_tokens": 1024,
    },
    "m12": {
        "name": "CheckHardConstraint",
        "slug": "check-hard-constraint",
        "prompt_file": "m12_v1_check_hard_constraint.md",
        "schema_file": "m12_hard_constraint_violation_check_schema_v1.1.json",
        "type": "classifier",
        "description": "Check if keyword violates any hard constraint",
        "model": "gpt-4o-mini",
        "temperature": 0.0,
        "max_tokens": 512,
    },
    "m12b": {
        "name": "CombinedClassification",
        "slug": "combined-classification",
        "prompt_file": "m12b_v1_combined_classification.md",
        "schema_file": "m12b_combined_classification_schema_v1.1.json",
        "type": "classifier",
        "description": "Combined keyword classification with structured reasoning (R/S/C/N)",
        "model": "gpt-4o-mini",
        "temperature": 0.0,
        "max_tokens": 2000,
    },
    "m13": {
        "name": "CheckProductType",
        "slug": "check-product-type",
        "prompt_file": "m13_v1_check_product_type.md",
        "schema_file": "m13_product_type_check_schema_v1.1.json",
        "type": "classifier",
        "description": "Check if keyword asks for same product type",
        "model": "gpt-4o-mini",
        "temperature": 0.0,
        "max_tokens": 512,
    },
    "m14": {
        "name": "CheckPrimaryUseSameType",
        "slug": "check-primary-use-same-type",
        "prompt_file": "m14_v1_check_primary_use_same_type.md",
        "schema_file": "m14_primary_use_check_same_type_schema_v1.1.json",
        "type": "classifier",
        "description": "Check if same-type product supports same primary use",
        "model": "gpt-4o-mini",
        "temperature": 0.0,
        "max_tokens": 512,
    },
    "m15": {
        "name": "CheckSubstitute",
        "slug": "check-substitute",
        "prompt_file": "m15_v1_check_substitute.md",
        "schema_file": "m15_substitute_check_schema_v1.1.json",
        "type": "classifier",
        "description": "Check if different product type can substitute for target",
        "model": "gpt-4o-mini",
        "temperature": 0.0,
        "max_tokens": 512,
    },
    "m16": {
        "name": "CheckComplementary",
        "slug": "check-complementary",
        "prompt_file": "m16_v1_check_complementary.md",
        "schema_file": "m16_complementary_check_schema_v1.1.json",
        "type": "classifier",
        "description": "Check if products are used together (complementary)",
        "model": "gpt-4o-mini",
        "temperature": 0.0,
        "max_tokens": 512,
    },
}


def load_prompt_and_schema(module_config: dict) -> tuple[str, dict]:
    """Load prompt markdown and JSON schema for a V1.1 module."""
    prompt_path = PROMPTS_DIR / "single" / module_config["prompt_file"]
    schema_path = SCHEMAS_DIR / "single" / module_config["schema_file"]

    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    with open(prompt_path, "r") as f:
        prompt = f.read()

    with open(schema_path, "r") as f:
        schema_data = json.load(f)

    return prompt, schema_data


def upload_module(module_id: str, project, mapping: dict = None) -> dict | None:
    """Upload a single V1.1 module to Braintrust.

    Returns mapping entry dict on success, None on failure.
    """
    module_config = V1_1_MODULES.get(module_id)
    if not module_config:
        print(f"  Unknown module: {module_id}")
        return None

    prompt_name = f"{module_id.upper()}_{module_config['name']}"
    prompt_slug = module_config["slug"]
    local_file = f"prompts/modules/single/{module_config['prompt_file']}"
    schema_file = f"prompts/json_schemas/single/{module_config['schema_file']}"

    # Check for existing mapping
    existing = None
    if mapping:
        existing = find_mapping_by_file(mapping, local_file)
        if existing:
            print(f"  Found existing mapping: {existing.get('braintrust_id')}")

    print(f"\n{'='*60}")
    print(f"Uploading: {prompt_name}")
    print(f"  File: {local_file}")
    print(f"  Slug: {prompt_slug}")
    print(f"{'='*60}")

    try:
        prompt, schema_data = load_prompt_and_schema(module_config)
    except FileNotFoundError as e:
        print(f"  SKIP: {e}")
        return None

    # Extract the actual schema from the wrapper if needed
    json_schema = schema_data.get("json_schema", schema_data)

    model = module_config.get("model", DEFAULT_MODEL)
    if not model.startswith("openai/") and not model.startswith("anthropic/"):
        model = f"openai/{model}"

    temperature = module_config.get("temperature", DEFAULT_TEMPERATURE)
    max_tokens = module_config.get("max_tokens", DEFAULT_MAX_TOKENS)

    # Use json_schema response format
    response_format = {
        "type": "json_schema",
        "json_schema": json_schema
    }

    prompt_obj = project.prompts.create(
        name=prompt_name,
        slug=prompt_slug,
        description=module_config["description"],
        messages=[
            {"role": "system", "content": prompt}
        ],
        model=model,
        params={
            "temperature": temperature,
            "max_tokens": max_tokens,
            "response_format": response_format
        },
        metadata={
            "version": "v1.1",
            "type": module_config["type"],
            "module_id": module_id,
            "local_file": local_file,
        },
        if_exists="replace"
    )

    # Get prompt ID
    prompt_id = getattr(prompt_obj, 'id', None)
    if not prompt_id:
        try:
            loaded = braintrust.load_prompt(project=PROJECT_NAME, slug=prompt_slug)
            prompt_id = loaded.id
        except:
            if existing and existing.get("braintrust_id") and existing.get("braintrust_id") != "unknown":
                prompt_id = existing.get("braintrust_id")
            else:
                prompt_id = "unknown"

    print(f"  OK: {prompt_name}")
    print(f"      ID: {prompt_id}")
    print(f"      Type: {module_config['type']}")
    print(f"      Model: {model}, Temp: {temperature}")

    # Update central resource_mappings.yaml
    update_resource_mappings(module_id, {
        "local_file": local_file,
        "schema_file": schema_file,
        "braintrust_id": prompt_id if prompt_id != "unknown" else None,
        "braintrust_slug": prompt_slug,
        "braintrust_name": prompt_name,
    })

    # Return mapping entry (for legacy file)
    return {
        "module": module_id,
        "local_file": local_file,
        "schema_file": schema_file,
        "braintrust_slug": prompt_slug,
        "braintrust_id": prompt_id,
        "braintrust_name": prompt_name,
        "prompt_version": "v1",
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
    }


def list_available_modules() -> list:
    """List V1.1 modules with both prompt and schema files."""
    available = []
    for module_id, config in V1_1_MODULES.items():
        prompt_path = PROMPTS_DIR / "single" / config["prompt_file"]
        schema_path = SCHEMAS_DIR / "single" / config["schema_file"]
        if prompt_path.exists() and schema_path.exists():
            available.append(module_id)
    return available


def main():
    parser = argparse.ArgumentParser(description="Upload prompts to Braintrust with mapping support")
    parser.add_argument("--module", "-m", type=str, help="Upload specific module (e.g., m10)")
    parser.add_argument("--file", "-f", type=str, help="Upload specific prompt file")
    parser.add_argument("--list", "-l", action="store_true", help="List available modules")
    parser.add_argument("--show-mapping", action="store_true", help="Show current mappings")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Show what would be uploaded")
    args = parser.parse_args()

    # Show mapping mode
    if args.show_mapping:
        show_mapping()
        return

    # List mode
    if args.list:
        available = list_available_modules()
        print("Available modules with prompts and schemas:")
        for m in available:
            cfg = V1_1_MODULES[m]
            print(f"  {m}: {cfg['name']} ({cfg['type']})")
            print(f"       Prompt: {cfg['prompt_file']}")
        print(f"\nTotal: {len(available)} modules ready for upload")
        return

    # Need either --module, --file, or run all
    if not args.module and not args.file and not args.dry_run:
        # If no specific option, upload all
        pass

    # Load API key and mapping
    load_api_key()
    mapping = load_mapping()

    print("="*60)
    print("Braintrust - Upload Prompts (with mapping)")
    print("="*60)
    print(f"Project: {PROJECT_NAME}")
    print(f"Mapping: {LEGACY_MAPPING_FILE}")

    # Handle --file option
    if args.file:
        prompt_path = Path(args.file)
        if not prompt_path.is_absolute():
            prompt_path = PROJECT_ROOT / prompt_path

        # Find corresponding module config by matching filename
        stem = prompt_path.stem
        module_id = None
        for mid, cfg in V1_1_MODULES.items():
            if cfg["prompt_file"] == prompt_path.name or stem in cfg["prompt_file"]:
                module_id = mid
                break

        if not module_id:
            print(f"ERROR: Could not find module config for file: {prompt_path.name}")
            print(f"Tip: Use --module flag instead, or add the file to V1_1_MODULES config")
            return

        modules_to_upload = [module_id]
    elif args.module:
        module_id = args.module.lower()
        if not module_id.startswith("m"):
            module_id = f"m{module_id.zfill(2)}"
        modules_to_upload = [module_id]
    else:
        modules_to_upload = list_available_modules()

    print(f"Modules to upload: {modules_to_upload}")

    if args.dry_run:
        print("\n[DRY RUN] Would upload:")
        for m in modules_to_upload:
            cfg = V1_1_MODULES.get(m, {})
            print(f"  {m}: {cfg.get('name', 'Unknown')}")
            print(f"       File: {cfg.get('prompt_file', 'Unknown')}")
        return

    # Connect to Braintrust
    project = braintrust.projects.create(name=PROJECT_NAME)

    # Upload each module
    uploaded = 0
    results = []
    for module_id in modules_to_upload:
        result = upload_module(module_id, project, mapping)
        if result:
            uploaded += 1
            update_or_add_mapping(mapping, result)
            results.append((module_id, result.get("braintrust_name"), "OK"))
        else:
            results.append((module_id, "---", "FAILED"))

    # Save mapping if any uploads succeeded
    if uploaded > 0:
        save_mapping(mapping)

    # Publish changes
    project.publish()

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"{'Module':<10} {'Name':<40} Status")
    print("-"*60)
    for module_id, name, status in results:
        print(f"{module_id:<10} {name:<40} {status}")
    print("-"*60)
    print(f"Uploaded: {uploaded}/{len(modules_to_upload)} prompts")
    print(f"{'='*60}")
    print(f"\nView at: https://www.braintrust.dev/app/KCC/p/{PROJECT_NAME}/prompts")


if __name__ == "__main__":
    main()
