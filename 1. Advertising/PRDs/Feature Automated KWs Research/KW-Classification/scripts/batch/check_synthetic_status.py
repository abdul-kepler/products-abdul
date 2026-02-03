#!/usr/bin/env python3
"""
Check status of uploaded synthetic batches.

Usage:
    python scripts/batch/check_synthetic_status.py <batch_dir>
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


def check_batch_status(batch_id: str) -> dict:
    """Check status of a batch."""
    batch = client.batches.retrieve(batch_id)
    return {
        "batch_id": batch.id,
        "status": batch.status,
        "request_counts": {
            "total": batch.request_counts.total,
            "completed": batch.request_counts.completed,
            "failed": batch.request_counts.failed,
        },
        "output_file_id": batch.output_file_id,
        "error_file_id": batch.error_file_id,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python check_synthetic_status.py <batch_dir>")
        sys.exit(1)

    batch_dir = Path(sys.argv[1])
    upload_log = batch_dir / "upload_log.json"

    if not upload_log.exists():
        print(f"No upload_log.json in {batch_dir}")
        sys.exit(1)

    log_data = json.loads(upload_log.read_text())
    batches = log_data.get("batches", [])

    print("=" * 70)
    print("BATCH STATUS CHECK")
    print("=" * 70)
    print(f"Directory: {batch_dir}")
    print(f"Batches: {len(batches)}")
    print()

    statuses = []
    completed = 0
    in_progress = 0
    failed = 0

    for batch_info in batches:
        batch_id = batch_info.get("batch_id")
        if not batch_id:
            continue

        try:
            status = check_batch_status(batch_id)
            statuses.append(status)

            icon = {"completed": "✓", "in_progress": "⏳", "failed": "✗"}.get(status["status"], "?")
            counts = status["request_counts"]
            print(f"{icon} {batch_info['file']}: {status['status']} ({counts['completed']}/{counts['total']})")

            if status["status"] == "completed":
                completed += 1
            elif status["status"] in ("in_progress", "validating", "finalizing"):
                in_progress += 1
            elif status["status"] == "failed":
                failed += 1

        except Exception as e:
            print(f"✗ {batch_info['file']}: Error - {e}")

    print()
    print("=" * 70)
    print(f"Completed: {completed}, In Progress: {in_progress}, Failed: {failed}")

    # Save status
    status_file = batch_dir / "status.json"
    status_file.write_text(json.dumps({
        "checked_at": datetime.now().isoformat(),
        "completed": completed,
        "in_progress": in_progress,
        "failed": failed,
        "statuses": statuses,
    }, indent=2))

    if completed > 0 and in_progress == 0:
        print()
        print("All batches completed! Download results:")
        print(f"  python scripts/batch/download_synthetic_results.py {batch_dir}")


if __name__ == "__main__":
    main()
