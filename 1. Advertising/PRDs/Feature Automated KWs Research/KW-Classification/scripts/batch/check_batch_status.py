#!/usr/bin/env python3
"""
Check status of OpenAI batch jobs.

Usage:
    # Check all batches from upload manifest:
    python scripts/batch/check_batch_status.py <batch_dir>

    # Check specific batch ID:
    python scripts/batch/check_batch_status.py --batch-id <batch_id>
"""

import json
import sys
import os
import argparse
from pathlib import Path
from datetime import datetime

from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def check_batch_status(batch_id: str) -> dict:
    """Check status of a single batch."""
    batch = client.batches.retrieve(batch_id)

    return {
        "batch_id": batch.id,
        "status": batch.status,
        "created_at": datetime.fromtimestamp(batch.created_at).isoformat() if batch.created_at else None,
        "completed_at": datetime.fromtimestamp(batch.completed_at).isoformat() if batch.completed_at else None,
        "failed_at": datetime.fromtimestamp(batch.failed_at).isoformat() if batch.failed_at else None,
        "request_counts": {
            "total": batch.request_counts.total if batch.request_counts else 0,
            "completed": batch.request_counts.completed if batch.request_counts else 0,
            "failed": batch.request_counts.failed if batch.request_counts else 0,
        },
        "output_file_id": batch.output_file_id,
        "error_file_id": batch.error_file_id,
        "errors": batch.errors.data if batch.errors else None,
        "metadata": batch.metadata
    }


def format_status_row(module: str, status: dict) -> str:
    """Format a status row for display."""
    batch_id = status["batch_id"][:20] + "..." if len(status["batch_id"]) > 20 else status["batch_id"]
    state = status["status"]

    counts = status["request_counts"]
    total = counts["total"]
    completed = counts["completed"]
    failed = counts["failed"]

    if total > 0:
        progress = f"{completed}/{total}"
        pct = f"({100*completed/total:.0f}%)"
    else:
        progress = "-"
        pct = ""

    # Status emoji
    emoji = {
        "validating": "⏳",
        "in_progress": "🔄",
        "completed": "✓",
        "failed": "✗",
        "expired": "⏰",
        "cancelling": "🚫",
        "cancelled": "🚫"
    }.get(state, "?")

    return f"{module:<10} {batch_id:<25} {state:<12} {emoji} {progress:<10} {pct}"


def main():
    """Main entry point."""

    parser = argparse.ArgumentParser(description="Check OpenAI batch status")
    parser.add_argument("batch_dir", nargs="?", help="Directory with upload_manifest.json")
    parser.add_argument("--batch-id", help="Check specific batch ID")
    args = parser.parse_args()

    if args.batch_id:
        # Check single batch
        print(f"Checking batch: {args.batch_id}")
        status = check_batch_status(args.batch_id)
        print(json.dumps(status, indent=2))
        return

    if not args.batch_dir:
        print("Usage: python check_batch_status.py <batch_dir>")
        print("       python check_batch_status.py --batch-id <batch_id>")
        sys.exit(1)

    batch_dir = Path(args.batch_dir)
    manifest_file = batch_dir / "upload_manifest.json"

    if not manifest_file.exists():
        print(f"Error: Upload manifest not found: {manifest_file}")
        print("Run upload_batch.py first to create batches.")
        sys.exit(1)

    # Load manifest
    with open(manifest_file, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    results = manifest.get("results", [])
    batches = [r for r in results if "batch_id" in r]

    if not batches:
        print("No batch IDs found in manifest.")
        sys.exit(1)

    print("=" * 80)
    print("BATCH STATUS CHECK")
    print("=" * 80)
    print(f"Directory: {batch_dir}")
    print(f"Batches: {len(batches)}")
    print()

    # Check each batch
    statuses = []
    header = f"{'Module':<10} {'Batch ID':<25} {'Status':<12}   {'Progress':<10}"
    print(header)
    print("-" * 80)

    for batch_info in batches:
        module = batch_info["file"].replace("_batch.jsonl", "")
        batch_id = batch_info["batch_id"]

        try:
            status = check_batch_status(batch_id)
            statuses.append({"module": module, **status})
            print(format_status_row(module, status))
        except Exception as e:
            print(f"{module:<10} Error: {e}")

    # Summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    completed = [s for s in statuses if s["status"] == "completed"]
    in_progress = [s for s in statuses if s["status"] == "in_progress"]
    failed = [s for s in statuses if s["status"] == "failed"]
    other = [s for s in statuses if s["status"] not in ["completed", "in_progress", "failed"]]

    total_requests = sum(s["request_counts"]["total"] for s in statuses)
    completed_requests = sum(s["request_counts"]["completed"] for s in statuses)
    failed_requests = sum(s["request_counts"]["failed"] for s in statuses)

    print(f"Batches: {len(completed)} completed, {len(in_progress)} in progress, {len(failed)} failed")
    print(f"Requests: {completed_requests}/{total_requests} completed, {failed_requests} failed")

    if completed and all(s["status"] == "completed" for s in statuses):
        print()
        print("✓ All batches completed!")
        print()
        print("Next step - download results:")
        print(f"  python scripts/batch/download_results.py {batch_dir}")

    # Save status report
    status_report = {
        "timestamp": datetime.now().isoformat(),
        "statuses": statuses,
        "summary": {
            "completed": len(completed),
            "in_progress": len(in_progress),
            "failed": len(failed),
            "total_requests": total_requests,
            "completed_requests": completed_requests,
            "failed_requests": failed_requests
        }
    }

    status_file = batch_dir / "status_report.json"
    with open(status_file, "w", encoding="utf-8") as f:
        json.dump(status_report, f, indent=2)

    print(f"\nStatus report saved: {status_file}")


if __name__ == "__main__":
    main()
