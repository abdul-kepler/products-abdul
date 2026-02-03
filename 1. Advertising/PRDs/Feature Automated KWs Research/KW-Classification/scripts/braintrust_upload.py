#!/usr/bin/env python3
"""
Upload prompts and datasets to Braintrust.

Usage:
    python scripts/braintrust_upload.py --prompts m02_v3 m04_v3 m05_v3
    python scripts/braintrust_upload.py --datasets m02_v3 m04_v4 m05_v4
    python scripts/braintrust_upload.py --all-v4
"""

import argparse
import json
import os
import sys
import re
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))
from config import PROJECT_ID, PROJECT_NAME, load_api_key

try:
    import braintrust
    from braintrust_api import Braintrust as BraintrustAPI
except ImportError as e:
    print(f"Error: {e}")
    print("Run: pip install braintrust braintrust-api")
    sys.exit(1)

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
PROMPTS_DIR = PROJECT_ROOT / "prompts" / "modules" / "single"
DATASETS_DIR = PROJECT_ROOT / "datasets" / "single"

# Prompt to dataset mapping
# Note: PROMPTS_DIR and DATASETS_DIR now include "single/" subdirectory
PROMPT_CONFIGS = {
    # M01A v2
    "m01a_v2": {
        "prompt_file": "m01a_v2_extract_own_brand_variations.md",
        "dataset_file": "m01a_v2_extract_own_brand_variations.jsonl",
        "name": "M01A_V2_ExtractOwnBrandVariations",
    },
    # M06-M08 modules
    "m06_v1": {
        "prompt_file": "m06_v2_generate_product_type_taxonomy.md",
        "dataset_file": "m06_v1_generate_product_type_taxonomy.jsonl",
        "name": "M06_V1_GenerateProductTypeTaxonomy",
    },
    # m06_sd_1 DEPRECATED - merged into m06_v1 (2026-01-25)
    "m07_sd_1": {
        "prompt_file": "m07_v2_extract_product_attributes.md",
        "dataset_file": "m07_sd1_extract_product_attributes.jsonl",
        "name": "M07_SD1_ExtractProductAttributes",
    },
    "m08_v2": {
        "prompt_file": "m08_v2_assign_attribute_ranks.md",
        "dataset_file": "m08_v1_assign_attribute_ranks.jsonl",
        "name": "M08_V2_AssignAttributeRanks",
    },
    "m08_sd_1": {
        "prompt_file": "m08_v2_assign_attribute_ranks.md",
        "dataset_file": "m08_sd1_assign_attribute_ranks.jsonl",
        "name": "M08_SD1_AssignAttributeRanks",
    },
}


def parse_prompt_file(filepath: Path) -> dict:
    """Parse markdown prompt file into system/examples/user template."""
    content = filepath.read_text()

    result = {
        "system": "",
        "examples": [],
        "user_template": "",
    }

    # Extract SYSTEM_INSTRUCTIONS
    if "<!-- SYSTEM_INSTRUCTIONS -->" in content:
        start = content.find("<!-- SYSTEM_INSTRUCTIONS -->") + len("<!-- SYSTEM_INSTRUCTIONS -->")
        end = content.find("<!-- /SYSTEM_INSTRUCTIONS -->")
        if end > start:
            result["system"] = content[start:end].strip()

    # Extract EXAMPLES
    example_users = re.findall(r'<!-- EXAMPLE_USER -->(.*?)<!-- /EXAMPLE_USER -->', content, re.DOTALL)
    example_assistants = re.findall(r'<!-- EXAMPLE_ASSISTANT -->(.*?)<!-- /EXAMPLE_ASSISTANT -->', content, re.DOTALL)

    for user, assistant in zip(example_users, example_assistants):
        result["examples"].append({
            "user": user.strip(),
            "assistant": assistant.strip(),
        })

    # Extract USER_INPUT template
    if "<!-- USER_INPUT -->" in content:
        start = content.find("<!-- USER_INPUT -->") + len("<!-- USER_INPUT -->")
        end = content.find("<!-- /USER_INPUT -->")
        if end > start:
            result["user_template"] = content[start:end].strip()

    return result


def upload_prompt(client: BraintrustAPI, module_id: str, config: dict):
    """Upload a prompt to Braintrust using API."""
    prompt_path = PROMPTS_DIR / config["prompt_file"]

    if not prompt_path.exists():
        print(f"  ✗ Prompt file not found: {prompt_path}")
        return None

    parsed = parse_prompt_file(prompt_path)

    # Build messages for Braintrust prompt
    messages = [
        {"role": "system", "content": parsed["system"]}
    ]

    # Add examples
    for ex in parsed["examples"]:
        messages.append({"role": "user", "content": ex["user"]})
        messages.append({"role": "assistant", "content": ex["assistant"]})

    # Add user template with placeholders
    messages.append({"role": "user", "content": parsed["user_template"]})

    try:
        # Create prompt using API
        prompt = client.prompts.create(
            project_id=PROJECT_ID,
            slug=module_id,
            name=config["name"],
            prompt_data={
                "prompt": {
                    "type": "chat",
                    "messages": messages,
                },
                "options": {
                    "model": "gpt-4o-mini",
                    "params": {
                        "temperature": 0,
                    },
                },
            },
        )
        print(f"  ✓ Prompt created: {module_id} -> {prompt.id}")
        return prompt
    except Exception as e:
        # Try to update existing prompt
        try:
            # Find existing prompt
            prompts = list(client.prompts.list(project_id=PROJECT_ID))
            existing = next((p for p in prompts if p.slug == module_id), None)

            if existing:
                prompt = client.prompts.update(
                    prompt_id=existing.id,
                    name=config["name"],
                    prompt_data={
                        "prompt": {
                            "type": "chat",
                            "messages": messages,
                        },
                        "options": {
                            "model": "gpt-4o-mini",
                            "params": {
                                "temperature": 0,
                            },
                        },
                    },
                )
                print(f"  ✓ Prompt updated: {module_id} -> {existing.id}")
                return prompt
            else:
                print(f"  ✗ Error creating prompt {module_id}: {e}")
                return None
        except Exception as e2:
            print(f"  ✗ Error creating/updating prompt {module_id}: {e2}")
            return None


def upload_dataset(module_id: str, config: dict):
    """Upload a dataset to Braintrust using SDK."""
    dataset_path = DATASETS_DIR / config["dataset_file"]

    if not dataset_path.exists():
        print(f"  ✗ Dataset file not found: {dataset_path}")
        return None

    # Load dataset records
    records = []
    with open(dataset_path) as f:
        for line in f:
            record = json.loads(line)
            records.append({
                "input": record.get("input", {}),
                "expected": record.get("expected", {}),
                "metadata": record.get("metadata", {}),
                "id": record.get("id", ""),
            })

    try:
        # Initialize dataset using SDK
        dataset = braintrust.init_dataset(
            project=PROJECT_NAME,
            name=config["name"],
            description=f"Dataset for {module_id}",
        )

        # Insert records
        for record in records:
            dataset.insert(
                input=record["input"],
                expected=record["expected"],
                metadata=record["metadata"],
                id=record["id"],
            )

        # Flush to save
        dataset.flush()

        print(f"  ✓ Dataset uploaded: {module_id} ({len(records)} records)")
        return dataset
    except Exception as e:
        print(f"  ✗ Error uploading dataset {module_id}: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Upload prompts and datasets to Braintrust")
    parser.add_argument("--prompts", nargs="+", help="Module IDs for prompts to upload")
    parser.add_argument("--datasets", nargs="+", help="Module IDs for datasets to upload")
    parser.add_argument("--list", action="store_true", help="List available modules")

    args = parser.parse_args()

    # Load API key
    try:
        api_key = load_api_key()
        os.environ["BRAINTRUST_API_KEY"] = api_key
    except ValueError as e:
        print(f"Error: {e}")
        print("Set BRAINTRUST_API_KEY in .env file or environment")
        sys.exit(1)

    if args.list:
        print("Available modules:")
        for mid, config in PROMPT_CONFIGS.items():
            print(f"  {mid}: {config['name']}")
        return

    # Initialize API client
    client = BraintrustAPI(api_key=api_key)

    print(f"Project: {PROJECT_NAME}")
    print(f"ID: {PROJECT_ID}")
    print()

    # Determine what to upload
    prompt_modules = args.prompts or []
    dataset_modules = args.datasets or []

    # Upload prompts
    if prompt_modules:
        print("=" * 50)
        print("UPLOADING PROMPTS")
        print("=" * 50)
        for mid in prompt_modules:
            if mid in PROMPT_CONFIGS:
                upload_prompt(client, mid, PROMPT_CONFIGS[mid])
            else:
                print(f"  ✗ Unknown module: {mid}")

    # Upload datasets
    if dataset_modules:
        print()
        print("=" * 50)
        print("UPLOADING DATASETS")
        print("=" * 50)
        for mid in dataset_modules:
            if mid in PROMPT_CONFIGS:
                upload_dataset(mid, PROMPT_CONFIGS[mid])
            else:
                print(f"  ✗ Unknown module: {mid}")

    if not prompt_modules and not dataset_modules:
        parser.print_help()


if __name__ == "__main__":
    main()
