#!/usr/bin/env python3
"""
Run local tests with updated prompts (v2).
Includes post-processing deduplication.
"""

import json
import time
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load API key
for env_path in [
    Path(__file__).parent.parent.parent.parent / ".env",
    Path(__file__).parent.parent.parent / ".env",
]:
    if env_path.exists():
        load_dotenv(env_path)
        break

import openai

BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "Local tests/v2"

MODULES = {
    "m01": {
        "name": "ExtractOwnBrandEntities",
        "prompt_file": "m01_extract_own_brand_entities.md",
        "schema_file": "m01_extract_own_brand_entities_schema.json",
        "dataset_file": "m01_extract_own_brand_entities.jsonl",
        "model": "gpt-4o-mini",
        "temperature": 0.0,
        "output_key": "brand_entities",
    },
    "m01a": {
        "name": "ExtractOwnBrandVariations",
        "prompt_file": "m01a_extract_own_brand_variations.md",
        "schema_file": "m01a_extract_own_brand_variations_schema.json",
        "dataset_file": "m01a_extract_own_brand_variations.jsonl",
        "model": "gpt-4o-mini",
        "temperature": 0.0,
        "output_key": "variations",
    },
    "m01b": {
        "name": "ExtractBrandRelatedTerms",
        "prompt_file": "m01b_extract_brand_related_terms.md",
        "schema_file": "m01b_extract_brand_related_terms_schema.json",
        "dataset_file": "m01b_extract_brand_related_terms.jsonl",
        "model": "gpt-4o-mini",
        "temperature": 0.0,
        "output_key": None,  # Multiple fields
    },
}


def load_jsonl(filepath: Path) -> list:
    records = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def deduplicate_list(items: list) -> list:
    """Remove duplicates while preserving order."""
    return list(dict.fromkeys(items))


def fill_template(template: str, inputs: dict) -> str:
    result = template
    for key, value in inputs.items():
        placeholder = "{{" + key + "}}"
        result = result.replace(placeholder, str(value) if value else "")
    return result


def call_openai(prompt: str, schema: dict, model: str, temperature: float) -> dict:
    client = openai.OpenAI()
    json_schema = schema.get("json_schema", schema)

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": prompt}],
        temperature=temperature,
        response_format={"type": "json_schema", "json_schema": json_schema},
    )

    return json.loads(response.choices[0].message.content)


def run_module_tests(module_id: str) -> dict:
    config = MODULES[module_id]
    print(f"\n{'='*60}")
    print(f"Running {module_id.upper()} - {config['name']}")
    print(f"{'='*60}")

    # Load files
    prompt_path = BASE_DIR / "prompts" / config["prompt_file"]
    schema_path = BASE_DIR / "prompts" / config["schema_file"]
    dataset_path = BASE_DIR / "datasets" / config["dataset_file"]

    with open(prompt_path) as f:
        prompt_template = f.read()
    with open(schema_path) as f:
        schema = json.load(f)

    records = load_jsonl(dataset_path)
    print(f"Loaded {len(records)} records")

    results = []
    stats = {"total": len(records), "success": 0, "errors": 0, "deduped": 0}

    for i, record in enumerate(records):
        asin = record.get("id")
        brand = record.get("input", {}).get("brand_name", "?")

        try:
            filled_prompt = fill_template(prompt_template, record.get("input", {}))
            output = call_openai(filled_prompt, schema, config["model"], config["temperature"])

            # Post-processing: deduplicate lists
            original_count = 0
            deduped_count = 0

            if config["output_key"]:
                # Single list field (m01, m01a)
                if config["output_key"] in output and isinstance(output[config["output_key"]], list):
                    original = output[config["output_key"]]
                    original_count = len(original)
                    output[config["output_key"]] = deduplicate_list(original)
                    deduped_count = len(output[config["output_key"]])
            else:
                # M01b - multiple fields
                for field in ["sub_brands", "searchable_standards"]:
                    if field in output and isinstance(output[field], list):
                        original = output[field]
                        original_count += len(original)
                        output[field] = deduplicate_list(original)
                        deduped_count += len(output[field])

            if original_count > deduped_count:
                stats["deduped"] += 1

            results.append({
                "id": asin,
                "brand_name": brand,
                "output": output,
            })
            stats["success"] += 1

            # Progress
            if (i + 1) % 20 == 0:
                print(f"  Progress: {i+1}/{len(records)}")

        except Exception as e:
            print(f"  ERROR {asin}: {e}")
            stats["errors"] += 1

        # Rate limiting
        time.sleep(0.3)

    # Save results
    output_file = OUTPUT_DIR / f"{module_id}_outputs.jsonl"
    with open(output_file, "w", encoding="utf-8") as f:
        for result in results:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")

    print(f"\nCompleted: {stats['success']}/{stats['total']} success, {stats['errors']} errors")
    print(f"Deduplication applied to {stats['deduped']} records")
    print(f"Saved to: {output_file}")

    return stats


def main():
    print("=" * 60)
    print("LOCAL TESTS v2 - Updated Prompts")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    modules_to_run = sys.argv[1:] if len(sys.argv) > 1 else ["m01", "m01a", "m01b"]

    total_stats = {"success": 0, "errors": 0, "deduped": 0}

    for module_id in modules_to_run:
        if module_id not in MODULES:
            print(f"Unknown module: {module_id}")
            continue

        stats = run_module_tests(module_id)
        total_stats["success"] += stats["success"]
        total_stats["errors"] += stats["errors"]
        total_stats["deduped"] += stats["deduped"]

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total success: {total_stats['success']}")
    print(f"Total errors: {total_stats['errors']}")
    print(f"Records with deduplication: {total_stats['deduped']}")
    print(f"\nOutputs saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
