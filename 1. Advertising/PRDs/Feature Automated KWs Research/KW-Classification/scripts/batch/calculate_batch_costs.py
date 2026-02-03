#!/usr/bin/env python3
"""
Calculate token usage and costs for OpenAI batch requests.

Usage:
    python scripts/batch/calculate_batch_costs.py <batch_dir>
    python scripts/batch/calculate_batch_costs.py --all
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

from openai import OpenAI
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Pricing per 1M tokens (Batch API = 50% off regular price)
# gpt-4o-mini batch pricing as of Jan 2025
PRICING = {
    "gpt-4o-mini": {
        "input": 0.075,   # $0.075 per 1M input tokens
        "output": 0.30,   # $0.30 per 1M output tokens
    },
    "gpt-4o": {
        "input": 1.25,    # $1.25 per 1M input tokens
        "output": 5.00,   # $5.00 per 1M output tokens
    },
}


def get_batch_token_usage(batch_id: str, output_file_id: str) -> dict:
    """Download batch results and calculate total token usage."""
    try:
        content = client.files.content(output_file_id)

        total_prompt = 0
        total_completion = 0
        total_requests = 0

        for line in content.text.strip().split("\n"):
            if not line.strip():
                continue
            result = json.loads(line)
            usage = result.get("response", {}).get("body", {}).get("usage", {})
            total_prompt += usage.get("prompt_tokens", 0)
            total_completion += usage.get("completion_tokens", 0)
            total_requests += 1

        return {
            "requests": total_requests,
            "prompt_tokens": total_prompt,
            "completion_tokens": total_completion,
            "total_tokens": total_prompt + total_completion,
        }
    except Exception as e:
        return {"error": str(e)}


def calculate_cost(prompt_tokens: int, completion_tokens: int, model: str = "gpt-4o-mini") -> float:
    """Calculate cost in USD."""
    pricing = PRICING.get(model, PRICING["gpt-4o-mini"])
    input_cost = (prompt_tokens / 1_000_000) * pricing["input"]
    output_cost = (completion_tokens / 1_000_000) * pricing["output"]
    return input_cost + output_cost


def process_batch_directory(batch_dir: Path) -> dict:
    """Process all batches in a directory."""
    upload_log_path = batch_dir / "upload_log.json"

    if not upload_log_path.exists():
        print(f"No upload_log.json in {batch_dir}")
        return {}

    upload_log = json.loads(upload_log_path.read_text())
    batches = upload_log.get("batches", [])

    results = {
        "directory": str(batch_dir),
        "processed_at": datetime.now().isoformat(),
        "model": "gpt-4o-mini",
        "batches": [],
        "totals": {
            "completed": 0,
            "in_progress": 0,
            "failed": 0,
            "requests": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "cost_usd": 0.0,
        }
    }

    print(f"Processing {len(batches)} batches...")
    print()

    for b in batches:
        batch_id = b.get("batch_id")
        filename = b.get("file")

        try:
            batch = client.batches.retrieve(batch_id)
            status = batch.status

            batch_result = {
                "file": filename,
                "batch_id": batch_id,
                "status": status,
                "requests": batch.request_counts.total if batch.request_counts else 0,
            }

            if status == "completed":
                results["totals"]["completed"] += 1

                if batch.output_file_id:
                    usage = get_batch_token_usage(batch_id, batch.output_file_id)

                    if "error" not in usage:
                        batch_result.update(usage)
                        cost = calculate_cost(usage["prompt_tokens"], usage["completion_tokens"])
                        batch_result["cost_usd"] = cost

                        results["totals"]["requests"] += usage["requests"]
                        results["totals"]["prompt_tokens"] += usage["prompt_tokens"]
                        results["totals"]["completion_tokens"] += usage["completion_tokens"]
                        results["totals"]["total_tokens"] += usage["total_tokens"]
                        results["totals"]["cost_usd"] += cost

                        print(f"✓ {filename}: {usage['total_tokens']:,} tokens, ${cost:.4f}")
                    else:
                        print(f"⚠ {filename}: {usage['error']}")
            elif status == "in_progress":
                results["totals"]["in_progress"] += 1
                print(f"⏳ {filename}: in progress")
            elif status == "failed":
                results["totals"]["failed"] += 1
                print(f"✗ {filename}: failed")
            else:
                print(f"? {filename}: {status}")

            results["batches"].append(batch_result)

        except Exception as e:
            print(f"✗ {filename}: {e}")

    return results


def main():
    if len(sys.argv) < 2:
        print("Usage: python calculate_batch_costs.py <batch_dir>")
        print("       python calculate_batch_costs.py --all")
        sys.exit(1)

    batch_dirs = []

    if sys.argv[1] == "--all":
        synthetic_dir = PROJECT_ROOT / "batch_requests" / "synthetic"
        batch_dirs = sorted([d for d in synthetic_dir.iterdir() if d.is_dir() and (d / "upload_log.json").exists()])
    else:
        batch_dirs = [Path(sys.argv[1])]

    all_results = []
    grand_totals = {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "cost_usd": 0.0,
        "completed": 0,
        "in_progress": 0,
    }

    for batch_dir in batch_dirs:
        print("=" * 70)
        print(f"BATCH DIRECTORY: {batch_dir.name}")
        print("=" * 70)

        results = process_batch_directory(batch_dir)

        if results:
            all_results.append(results)
            grand_totals["prompt_tokens"] += results["totals"]["prompt_tokens"]
            grand_totals["completion_tokens"] += results["totals"]["completion_tokens"]
            grand_totals["total_tokens"] += results["totals"]["total_tokens"]
            grand_totals["cost_usd"] += results["totals"]["cost_usd"]
            grand_totals["completed"] += results["totals"]["completed"]
            grand_totals["in_progress"] += results["totals"]["in_progress"]

            # Save results to directory
            cost_log = batch_dir / "cost_log.json"
            cost_log.write_text(json.dumps(results, indent=2))

        print()

    # Print summary
    print("=" * 70)
    print("GRAND TOTALS")
    print("=" * 70)
    print(f"Batches completed:    {grand_totals['completed']}")
    print(f"Batches in progress:  {grand_totals['in_progress']}")
    print(f"Prompt tokens:        {grand_totals['prompt_tokens']:,}")
    print(f"Completion tokens:    {grand_totals['completion_tokens']:,}")
    print(f"Total tokens:         {grand_totals['total_tokens']:,}")
    print(f"Estimated cost:       ${grand_totals['cost_usd']:.4f}")
    print()
    print("Pricing (gpt-4o-mini batch):")
    print("  Input:  $0.075 / 1M tokens")
    print("  Output: $0.30 / 1M tokens")


if __name__ == "__main__":
    main()
