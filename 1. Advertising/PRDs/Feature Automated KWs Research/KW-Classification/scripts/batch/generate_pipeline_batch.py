#!/usr/bin/env python3
"""
Generate batch files for M08→M09→M10→M11 pipeline.

Takes outputs from M06/M07 batches and creates inputs for subsequent modules.

Pipeline:
  M06 (taxonomy) + M07 (attributes) → M08 (ranked attributes)
  M08 → M09 (primary_use)
  M09 → M10 (validated_use)
  M10 → M11 (hard_constraints)

Usage:
    # After M06/M07 batches complete:
    python generate_pipeline_batch.py m08 <m06_m07_results_dir>

    # After M08 batches complete:
    python generate_pipeline_batch.py m09 <m08_results_dir>

    # After M09 batches complete:
    python generate_pipeline_batch.py m10 <m09_results_dir>

    # After M10 batches complete:
    python generate_pipeline_batch.py m11 <m10_results_dir>
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent
SYNTHETIC_DIR = PROJECT_ROOT / "datasets" / "synthetic"
LABELED_DIR = PROJECT_ROOT / "datasets" / "synthetic_labeled"
PROMPTS_DIR = PROJECT_ROOT / "prompts"
SCHEMAS_DIR = PROMPTS_DIR / "json_schemas" / "single"
OPTIMIZED_DIR = PROMPTS_DIR / "optimized"
BATCH_DIR = PROJECT_ROOT / "batch_requests" / "pipeline"

# Module configurations
MODULES = {
    "m08": {
        "name": "AssignAttributeRanks",
        "schema": "m08_assign_attribute_ranks_schema.json",
        "prompt_pattern": "m08_v*_assign_attribute_ranks*.md",
        "requires": ["m06", "m07"],  # Needs M06 taxonomy + M07 attributes
    },
    "m09": {
        "name": "IdentifyPrimaryIntendedUse",
        "schema": "m09_identify_primary_intended_use_schema.json",
        "prompt_pattern": "m09_v*_identify_primary_intended_use*.md",
        "requires": ["m08"],  # Needs M08 attribute_table
    },
    "m10": {
        "name": "ValidatePrimaryIntendedUse",
        "schema": "m10_validate_primary_intended_use_schema.json",
        "prompt_pattern": "m10_v*_validate_primary_intended_use*.md",
        "requires": ["m09"],  # Needs M09 primary_use
    },
    "m11": {
        "name": "IdentifyHardConstraints",
        "schema": "m11_identify_hard_constraints_schema.json",
        "prompt_pattern": "m11_v*_identify_hard_constraints*.md",
        "requires": ["m10"],  # Needs M10 validated_use
    },
}


def find_prompt(module_id: str) -> str:
    """Find and read the optimized prompt for a module."""
    pattern = MODULES[module_id]["prompt_pattern"]

    # Try optimized first
    matches = list(OPTIMIZED_DIR.glob(pattern))
    if not matches:
        # Fall back to single prompts
        single_dir = PROMPTS_DIR / "modules" / "single"
        matches = list(single_dir.glob(f"{module_id}_*.md"))

    if matches:
        prompt_file = sorted(matches, reverse=True)[0]
        return prompt_file.read_text()

    raise FileNotFoundError(f"No prompt found for {module_id}")


def load_schema(module_id: str) -> dict:
    """Load JSON schema for a module."""
    schema_path = SCHEMAS_DIR / MODULES[module_id]["schema"]
    if schema_path.exists():
        return json.loads(schema_path.read_text())
    return {}


def load_synthetic_data(sd_num: str) -> dict[str, dict]:
    """Load original synthetic data by ASIN."""
    records = {}

    # Find any synthetic file for this sd_num
    for pattern in [f"m06_sd{sd_num}_*.jsonl", f"m07_sd{sd_num}_*.jsonl"]:
        for f in SYNTHETIC_DIR.glob(pattern):
            for line in f.read_text().strip().split("\n"):
                if line.strip():
                    record = json.loads(line)
                    asin = record.get("id", "")
                    if asin and asin not in records:
                        records[asin] = record

    return records


def load_labeled_results(module_id: str, sd_num: str) -> dict[str, dict]:
    """Load labeled results (model outputs) for a module."""
    results = {}

    pattern = f"{module_id}_sd{sd_num}_*.jsonl"
    for f in LABELED_DIR.glob(pattern):
        for line in f.read_text().strip().split("\n"):
            if line.strip():
                record = json.loads(line)
                asin = record.get("id", "")
                # The 'expected' field contains the model output
                if asin and record.get("expected"):
                    results[asin] = record["expected"]

    return results


def build_m08_input(asin: str, original: dict, m06_output: dict, m07_output: dict) -> dict:
    """Build M08 input from M06 taxonomy and M07 attributes."""
    product_data = original.get("input", {})

    return {
        "title": product_data.get("title", ""),
        "description": product_data.get("description", ""),
        "bullet_points": product_data.get("bullet_points", ""),
        "taxonomy": m06_output.get("taxonomy", []),
        "audiences": m07_output.get("audiences", []),
        "use_cases": m07_output.get("use_cases", []),
        "variants": m07_output.get("variants", []),
    }


def build_m09_input(asin: str, original: dict, m06_output: dict, m08_output: dict) -> dict:
    """Build M09 input from M06 taxonomy and M08 attribute_table."""
    product_data = original.get("input", {})

    return {
        "title": product_data.get("title", ""),
        "description": product_data.get("description", ""),
        "bullet_points": product_data.get("bullet_points", ""),
        "product_attributes": {
            "category_root": product_data.get("category_root", ""),
            "category_sub": product_data.get("category_sub", ""),
            "product_type": product_data.get("product_type", ""),
        },
        "taxonomy": m06_output.get("taxonomy", []),
        "attribute_table": m08_output.get("attribute_table", []),
    }


def build_m10_input(asin: str, original: dict, m06_output: dict, m08_output: dict, m09_output: dict) -> dict:
    """Build M10 input from M09 primary_use."""
    base = build_m09_input(asin, original, m06_output, m08_output)
    base["primary_use"] = m09_output.get("primary_use", "")
    return base


def build_m11_input(asin: str, original: dict, m06_output: dict, m08_output: dict, m10_output: dict) -> dict:
    """Build M11 input from M10 validated_use."""
    product_data = original.get("input", {})

    return {
        "title": product_data.get("title", ""),
        "description": product_data.get("description", ""),
        "bullet_points": product_data.get("bullet_points", ""),
        "product_attributes": {
            "category_root": product_data.get("category_root", ""),
            "category_sub": product_data.get("category_sub", ""),
            "product_type": product_data.get("product_type", ""),
        },
        "taxonomy": m06_output.get("taxonomy", []),
        "attribute_table": m08_output.get("attribute_table", []),
        "validated_use": m10_output.get("validated_use", ""),
    }


def create_batch_request(custom_id: str, prompt: str, input_data: dict, schema: dict) -> dict:
    """Create a single batch request."""
    user_content = prompt + "\n\n## Input\n```json\n" + json.dumps(input_data, indent=2) + "\n```"

    request = {
        "custom_id": custom_id,
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "user", "content": user_content}
            ],
            "temperature": 0,
            "max_tokens": 4096,
        }
    }

    if schema:
        request["body"]["response_format"] = {
            "type": "json_schema",
            "json_schema": schema.get("json_schema", schema),
        }

    return request


def generate_m08_batches(output_dir: Path):
    """Generate M08 batch files from M06/M07 results."""
    print("Generating M08 batches from M06/M07 results...")

    prompt = find_prompt("m08")
    schema = load_schema("m08")

    # Find all sd numbers from labeled M06 results
    sd_nums = set()
    for f in LABELED_DIR.glob("m06_sd*_*.jsonl"):
        match = re.search(r"sd(\d+)", f.name)
        if match:
            sd_nums.add(match.group(1))

    total_records = 0

    for sd_num in sorted(sd_nums):
        print(f"  Processing sd{sd_num}...", end=" ")

        # Load data
        original_data = load_synthetic_data(sd_num)
        m06_results = load_labeled_results("m06", sd_num)
        m07_results = load_labeled_results("m07", sd_num)

        if not m06_results or not m07_results:
            print("skip (missing M06/M07)")
            continue

        # Generate batch requests
        requests = []
        for asin in original_data:
            if asin in m06_results and asin in m07_results:
                input_data = build_m08_input(
                    asin,
                    original_data[asin],
                    m06_results[asin],
                    m07_results[asin]
                )

                request = create_batch_request(
                    f"m08_sd{sd_num}_{asin}",
                    prompt,
                    input_data,
                    schema
                )
                requests.append(request)

        if requests:
            batch_file = output_dir / f"m08_sd{sd_num}_batch.jsonl"
            with open(batch_file, "w") as f:
                for req in requests:
                    f.write(json.dumps(req) + "\n")

            print(f"{len(requests)} records")
            total_records += len(requests)
        else:
            print("skip (no matching records)")

    return total_records


def generate_m09_batches(output_dir: Path):
    """Generate M09 batch files from M08 results."""
    print("Generating M09 batches from M08 results...")

    prompt = find_prompt("m09")
    schema = load_schema("m09")

    # Find all sd numbers from labeled M08 results
    sd_nums = set()
    for f in LABELED_DIR.glob("m08_sd*_*.jsonl"):
        match = re.search(r"sd(\d+)", f.name)
        if match:
            sd_nums.add(match.group(1))

    total_records = 0

    for sd_num in sorted(sd_nums):
        print(f"  Processing sd{sd_num}...", end=" ")

        # Load data
        original_data = load_synthetic_data(sd_num)
        m06_results = load_labeled_results("m06", sd_num)
        m08_results = load_labeled_results("m08", sd_num)

        if not m06_results or not m08_results:
            print("skip (missing M06/M08)")
            continue

        # Generate batch requests
        requests = []
        for asin in original_data:
            if asin in m06_results and asin in m08_results:
                input_data = build_m09_input(
                    asin,
                    original_data[asin],
                    m06_results[asin],
                    m08_results[asin]
                )

                request = create_batch_request(
                    f"m09_sd{sd_num}_{asin}",
                    prompt,
                    input_data,
                    schema
                )
                requests.append(request)

        if requests:
            batch_file = output_dir / f"m09_sd{sd_num}_batch.jsonl"
            with open(batch_file, "w") as f:
                for req in requests:
                    f.write(json.dumps(req) + "\n")

            print(f"{len(requests)} records")
            total_records += len(requests)
        else:
            print("skip (no matching records)")

    return total_records


def generate_m10_batches(output_dir: Path):
    """Generate M10 batch files from M09 results."""
    print("Generating M10 batches from M09 results...")

    prompt = find_prompt("m10")
    schema = load_schema("m10")

    # Find all sd numbers from labeled M09 results
    sd_nums = set()
    for f in LABELED_DIR.glob("m09_sd*_*.jsonl"):
        match = re.search(r"sd(\d+)", f.name)
        if match:
            sd_nums.add(match.group(1))

    total_records = 0

    for sd_num in sorted(sd_nums):
        print(f"  Processing sd{sd_num}...", end=" ")

        # Load data
        original_data = load_synthetic_data(sd_num)
        m06_results = load_labeled_results("m06", sd_num)
        m08_results = load_labeled_results("m08", sd_num)
        m09_results = load_labeled_results("m09", sd_num)

        if not m06_results or not m08_results or not m09_results:
            print("skip (missing dependencies)")
            continue

        # Generate batch requests
        requests = []
        for asin in original_data:
            if asin in m06_results and asin in m08_results and asin in m09_results:
                input_data = build_m10_input(
                    asin,
                    original_data[asin],
                    m06_results[asin],
                    m08_results[asin],
                    m09_results[asin]
                )

                request = create_batch_request(
                    f"m10_sd{sd_num}_{asin}",
                    prompt,
                    input_data,
                    schema
                )
                requests.append(request)

        if requests:
            batch_file = output_dir / f"m10_sd{sd_num}_batch.jsonl"
            with open(batch_file, "w") as f:
                for req in requests:
                    f.write(json.dumps(req) + "\n")

            print(f"{len(requests)} records")
            total_records += len(requests)
        else:
            print("skip (no matching records)")

    return total_records


def generate_m11_batches(output_dir: Path):
    """Generate M11 batch files from M10 results."""
    print("Generating M11 batches from M10 results...")

    prompt = find_prompt("m11")
    schema = load_schema("m11")

    # Find all sd numbers from labeled M10 results
    sd_nums = set()
    for f in LABELED_DIR.glob("m10_sd*_*.jsonl"):
        match = re.search(r"sd(\d+)", f.name)
        if match:
            sd_nums.add(match.group(1))

    total_records = 0

    for sd_num in sorted(sd_nums):
        print(f"  Processing sd{sd_num}...", end=" ")

        # Load data
        original_data = load_synthetic_data(sd_num)
        m06_results = load_labeled_results("m06", sd_num)
        m08_results = load_labeled_results("m08", sd_num)
        m10_results = load_labeled_results("m10", sd_num)

        if not m06_results or not m08_results or not m10_results:
            print("skip (missing dependencies)")
            continue

        # Generate batch requests
        requests = []
        for asin in original_data:
            if asin in m06_results and asin in m08_results and asin in m10_results:
                input_data = build_m11_input(
                    asin,
                    original_data[asin],
                    m06_results[asin],
                    m08_results[asin],
                    m10_results[asin]
                )

                request = create_batch_request(
                    f"m11_sd{sd_num}_{asin}",
                    prompt,
                    input_data,
                    schema
                )
                requests.append(request)

        if requests:
            batch_file = output_dir / f"m11_sd{sd_num}_batch.jsonl"
            with open(batch_file, "w") as f:
                for req in requests:
                    f.write(json.dumps(req) + "\n")

            print(f"{len(requests)} records")
            total_records += len(requests)
        else:
            print("skip (no matching records)")

    return total_records


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_pipeline_batch.py <module>")
        print()
        print("Modules: m08, m09, m10, m11")
        print()
        print("Pipeline order:")
        print("  1. Run M06/M07 synthetic batches")
        print("  2. Download results → creates labeled datasets")
        print("  3. python generate_pipeline_batch.py m08")
        print("  4. Upload & run M08 batches, download results")
        print("  5. python generate_pipeline_batch.py m09")
        print("  6. Upload & run M09 batches, download results")
        print("  7. python generate_pipeline_batch.py m10")
        print("  8. Upload & run M10 batches, download results")
        print("  9. python generate_pipeline_batch.py m11")
        sys.exit(1)

    module = sys.argv[1].lower()

    if module not in MODULES:
        print(f"Unknown module: {module}")
        print(f"Available: {', '.join(MODULES.keys())}")
        sys.exit(1)

    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_dir = BATCH_DIR / f"{module}_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print(f"GENERATE {module.upper()} PIPELINE BATCHES")
    print("=" * 70)
    print(f"Output: {output_dir}")
    print()

    # Generate batches
    generators = {
        "m08": generate_m08_batches,
        "m09": generate_m09_batches,
        "m10": generate_m10_batches,
        "m11": generate_m11_batches,
    }

    total = generators[module](output_dir)

    print()
    print("=" * 70)
    print(f"Total records: {total}")
    print(f"Batch files: {output_dir}")
    print()
    print("Next steps:")
    print(f"  python scripts/batch/upload_synthetic_batch.py {output_dir}")


if __name__ == "__main__":
    main()
