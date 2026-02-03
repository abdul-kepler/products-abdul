#!/usr/bin/env python3
"""
Local test for M02b, M04b, M05b prompts (Path B - uses M01a/M01b outputs).
Tests format and structure only - no evaluation.
"""

import json
import random
import sys
from pathlib import Path
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

MODULES = {
    "m02b": {
        "name": "ClassifyOwnBrandKeywords_PathB",
        "prompt_file": "m02b_classify_own_brand_keywords.md",
        "schema_file": "m02b_classify_own_brand_keywords_schema.json",
        "dataset_file": "m02b_classify_own_brand_keywords.jsonl",
    },
    "m04b": {
        "name": "ClassifyCompetitorBrandKeywords_PathB",
        "prompt_file": "m04b_classify_competitor_brand_keywords.md",
        "schema_file": "m04b_classify_competitor_brand_keywords_schema.json",
        "dataset_file": "m04b_classify_competitor_brand_keywords.jsonl",
    },
    "m05b": {
        "name": "ClassifyNonBrandedKeywords_PathB",
        "prompt_file": "m05b_classify_nonbranded_keywords.md",
        "schema_file": "m05b_classify_nonbranded_keywords_schema.json",
        "dataset_file": "m05b_classify_nonbranded_keywords.jsonl",
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


def fill_template(template: str, inputs: dict) -> str:
    """Fill mustache-style template with inputs."""
    result = template
    for key, value in inputs.items():
        placeholder = "{{" + key + "}}"
        # Convert objects/arrays to JSON string
        if isinstance(value, (dict, list)):
            value_str = json.dumps(value, ensure_ascii=False)
        else:
            value_str = str(value) if value else ""
        result = result.replace(placeholder, value_str)
    return result


def call_openai(prompt: str, schema: dict, model: str = "gpt-4o-mini", temperature: float = 0.0) -> dict:
    """Call OpenAI API with structured output."""
    client = openai.OpenAI()
    json_schema = schema.get("json_schema", schema)

    # Wrap schema if needed
    if "name" in json_schema and "schema" in json_schema:
        response_format = {"type": "json_schema", "json_schema": json_schema}
    else:
        response_format = {"type": "json_schema", "json_schema": {
            "name": "response",
            "strict": True,
            "schema": json_schema
        }}

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": prompt}],
        temperature=temperature,
        response_format=response_format,
    )

    return json.loads(response.choices[0].message.content)


def test_module(module_id: str, num_samples: int = 15) -> dict:
    """Test a module with random samples."""
    config = MODULES[module_id]
    print(f"\n{'='*70}")
    print(f"Testing {module_id.upper()} - {config['name']}")
    print(f"{'='*70}")

    # Load files
    prompt_path = BASE_DIR / "prompts" / config["prompt_file"]
    schema_path = BASE_DIR / "prompts" / config["schema_file"]
    dataset_path = BASE_DIR / "datasets" / config["dataset_file"]

    with open(prompt_path) as f:
        prompt_template = f.read()
    with open(schema_path) as f:
        schema = json.load(f)

    records = load_jsonl(dataset_path)
    print(f"Total records: {len(records)}")

    # Select random samples
    samples = random.sample(records, min(num_samples, len(records)))
    print(f"Testing {len(samples)} random samples\n")

    results = {"success": 0, "errors": 0, "samples": []}

    for i, record in enumerate(samples, 1):
        inputs = record.get("input", {})
        keyword = inputs.get("keyword", "N/A")
        expected = record.get("expected", {})

        print(f"[{i}/{len(samples)}] Keyword: '{keyword}'")

        # Show input structure
        print(f"  Input keys: {list(inputs.keys())}")

        # For M04/M05 show competitors count
        if "competitors" in inputs:
            print(f"  Competitors: {len(inputs['competitors'])}")
        if "own_brand" in inputs:
            print(f"  Own brand: {inputs['own_brand'].get('name', 'N/A')}")

        try:
            # Fill template and call API
            filled_prompt = fill_template(prompt_template, inputs)
            output = call_openai(filled_prompt, schema)

            # Show output
            print(f"  Output: {json.dumps(output, ensure_ascii=False)}")
            print(f"  Expected: {json.dumps(expected, ensure_ascii=False)}")

            # Check if structure is valid
            if "branding_scope" in output or "branding_scope_1" in output:
                print(f"  Status: ✓ Valid structure")
                results["success"] += 1
            else:
                print(f"  Status: ⚠ Missing branding_scope")
                results["errors"] += 1

            results["samples"].append({
                "keyword": keyword,
                "output": output,
                "expected": expected,
                "status": "success"
            })

        except Exception as e:
            print(f"  Status: ✗ Error: {e}")
            results["errors"] += 1
            results["samples"].append({
                "keyword": keyword,
                "error": str(e),
                "status": "error"
            })

        print()

    return results


def main():
    print("=" * 70)
    print("LOCAL PROMPT TEST - Format & Structure")
    print("=" * 70)

    # Parse args
    num_samples = 15
    modules_to_test = ["m02b", "m04b", "m05b"]

    if len(sys.argv) > 1:
        try:
            num_samples = int(sys.argv[1])
        except ValueError:
            modules_to_test = sys.argv[1:]

    all_results = {}

    for module_id in modules_to_test:
        if module_id not in MODULES:
            print(f"Unknown module: {module_id}")
            continue

        results = test_module(module_id, num_samples)
        all_results[module_id] = results

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    for module_id, results in all_results.items():
        total = results["success"] + results["errors"]
        print(f"{module_id.upper()}: {results['success']}/{total} success, {results['errors']} errors")

    print("\nDone!")


if __name__ == "__main__":
    main()
