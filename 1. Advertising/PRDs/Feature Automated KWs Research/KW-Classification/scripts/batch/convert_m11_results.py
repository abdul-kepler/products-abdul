#!/usr/bin/env python3
"""
Convert M11 batch results to experiment format (CSV + meta.json).
"""

import json
import csv
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent
RESULTS_DIR = PROJECT_ROOT / "batch_requests" / "synthetic" / "20260128_0122" / "results"
SYNTHETIC_DIR = PROJECT_ROOT / "datasets" / "synthetic"
EXPERIMENT_OUTPUT = PROJECT_ROOT / "experiment_results" / "M11_IdentifyHardConstraints"


def load_synthetic_dataset(sd_num: int) -> dict:
    """Load synthetic dataset and return dict keyed by record ID."""
    sd_str = f"sd{sd_num:02d}"
    filepath = SYNTHETIC_DIR / f"m11_{sd_str}_identify_hard_constraints.jsonl"

    records = {}
    if filepath.exists():
        with open(filepath, encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    records[record['id']] = record
    return records


def parse_batch_results(filepath: Path) -> dict:
    """Parse batch results file and return dict keyed by custom_id."""
    results = {}
    with open(filepath, encoding='utf-8') as f:
        for line in f:
            if line.strip():
                result = json.loads(line)
                custom_id = result['custom_id']

                response = result.get('response', {})
                body = response.get('body', {})
                choices = body.get('choices', [])

                if choices:
                    content = choices[0].get('message', {}).get('content', '{}')
                    try:
                        output = json.loads(content)
                    except json.JSONDecodeError:
                        output = {}
                else:
                    output = {}

                results[custom_id] = output
    return results


def convert_sd_results(sd_num: int):
    """Convert batch results for one sd dataset to experiment format."""
    sd_str = f"sd{sd_num:02d}"

    # Load results
    results_file = RESULTS_DIR / f"m11_{sd_str}_results.jsonl"
    if not results_file.exists():
        print(f"⚠ {sd_str}: results file not found")
        return

    batch_results = parse_batch_results(results_file)
    synthetic_data = load_synthetic_dataset(sd_num)

    if not batch_results:
        print(f"⚠ {sd_str}: no results found")
        return

    # Create output files
    timestamp = datetime.now().strftime("%d%m%y")
    base_name = f"M11_V3_{sd_str}_IdentifyHardConstraints_v3_{timestamp}_gpt4omini_synthetic"
    csv_file = EXPERIMENT_OUTPUT / f"{base_name}.csv"
    meta_file = EXPERIMENT_OUTPUT / f"{base_name}.meta.json"

    # Prepare CSV data
    rows = []
    for custom_id, output in batch_results.items():
        # Extract ASIN from custom_id (m11_sd01_M11_sd01_B082XKDYY9 -> M11_sd01_B082XKDYY9)
        parts = custom_id.split('_')
        if len(parts) >= 3:
            record_id = '_'.join(parts[2:])  # M11_sd01_B082XKDYY9
        else:
            record_id = custom_id

        # Get input from synthetic data
        input_data = {}
        if record_id in synthetic_data:
            input_data = synthetic_data[record_id].get('input', {})

        row = {
            'name': 'eval',
            'ASIN': record_id,
            'Brand': '',
            'GoldenDataset': 'False',
            'input': json.dumps(input_data, ensure_ascii=False),
            'output': json.dumps(output, ensure_ascii=False),
            'expected': '{}',
            'metrics': json.dumps({"synthetic": True, "sd": sd_str, "sd_dataset": ""}, ensure_ascii=False)
        }
        rows.append(row)

    # Write CSV
    fieldnames = ['name', 'ASIN', 'Brand', 'GoldenDataset', 'input', 'output', 'expected', 'metrics']
    with open(csv_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # Write meta.json
    meta = {
        "experiment_name": base_name,
        "created": datetime.now().isoformat(),
        "model": "gpt-4o-mini",
        "temperature": 0,
        "source": "openai_batch_api",
        "batch_type": "synthetic",
        "synthetic_dataset": sd_str.replace("sd", ""),
        "dataset_file": f"m11_{sd_str}_identify_hard_constraints.jsonl",
        "prompt_version": "v3",
        "response_format": {
            "type": "json_schema",
            "json_schema": {}
        },
        "records_count": len(rows),
        "downloaded_at": datetime.now().isoformat()
    }

    with open(meta_file, 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2)

    print(f"✓ {sd_str}: {len(rows)} records → {csv_file.name}")


def main():
    """Convert all M11 batch results."""
    print("Converting M11 batch results to experiment format...")
    print(f"Results dir: {RESULTS_DIR}")
    print(f"Output dir: {EXPERIMENT_OUTPUT}")
    print()

    EXPERIMENT_OUTPUT.mkdir(parents=True, exist_ok=True)

    total_records = 0
    for sd_num in range(1, 23):
        convert_sd_results(sd_num)

    # Count total
    csv_files = list(EXPERIMENT_OUTPUT.glob("*gpt4omini_synthetic.csv"))
    for f in csv_files:
        with open(f, encoding='utf-8') as csvf:
            total_records += sum(1 for _ in csvf) - 1  # minus header

    print()
    print(f"Done! {len(csv_files)} files, ~{total_records} total records")


if __name__ == "__main__":
    main()
