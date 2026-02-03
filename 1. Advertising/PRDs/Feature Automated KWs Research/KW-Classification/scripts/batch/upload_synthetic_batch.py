#!/usr/bin/env python3
"""
Upload synthetic batch files to OpenAI Batch API.

Usage:
    python scripts/batch/upload_synthetic_batch.py <batch_dir>
    python scripts/batch/upload_synthetic_batch.py batch_requests/synthetic/20260127_1200
"""

import json
import sys
import os
import time
from pathlib import Path
from datetime import datetime

from openai import OpenAI
from dotenv import load_dotenv

# Load environment
PROJECT_ROOT = Path(__file__).parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def upload_batch_file(filepath: Path) -> dict:
    """Upload a batch file and create batch job."""

    # Upload file
    print(f"  Uploading {filepath.name}...", end=" ")
    with open(filepath, "rb") as f:
        file_obj = client.files.create(file=f, purpose="batch")
    print(f"file_id={file_obj.id}")

    # Create batch
    print(f"  Creating batch...", end=" ")
    batch = client.batches.create(
        input_file_id=file_obj.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={"source": filepath.name}
    )
    print(f"batch_id={batch.id}")

    return {
        "file": filepath.name,
        "file_id": file_obj.id,
        "batch_id": batch.id,
        "status": batch.status,
        "created_at": datetime.now().isoformat(),
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python upload_synthetic_batch.py <batch_dir>")
        sys.exit(1)

    batch_dir = Path(sys.argv[1])
    if not batch_dir.exists():
        print(f"Error: Directory not found: {batch_dir}")
        sys.exit(1)

    # Find all batch files
    batch_files = sorted(batch_dir.glob("*_batch.jsonl"))
    if not batch_files:
        print(f"No batch files found in {batch_dir}")
        sys.exit(1)

    print("=" * 70)
    print("UPLOAD SYNTHETIC BATCHES TO OPENAI")
    print("=" * 70)
    print(f"Directory: {batch_dir}")
    print(f"Files: {len(batch_files)}")
    print()

    results = []

    for filepath in batch_files:
        try:
            result = upload_batch_file(filepath)
            results.append(result)
            # Small delay to avoid rate limits
            time.sleep(0.5)
        except Exception as e:
            print(f"  Error: {e}")
            results.append({
                "file": filepath.name,
                "status": "error",
                "error": str(e),
            })

    # Save upload results
    upload_log = batch_dir / "upload_log.json"
    upload_log.write_text(json.dumps({
        "uploaded_at": datetime.now().isoformat(),
        "total_files": len(batch_files),
        "successful": len([r for r in results if r.get("batch_id")]),
        "batches": results,
    }, indent=2))

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    successful = [r for r in results if r.get("batch_id")]
    print(f"Uploaded: {len(successful)}/{len(batch_files)}")
    print(f"Log: {upload_log}")

    print()
    print("Batch IDs:")
    for r in results:
        if r.get("batch_id"):
            print(f"  {r['file']}: {r['batch_id']}")

    print()
    print("Check status:")
    print("  python scripts/batch/check_synthetic_status.py", batch_dir)


if __name__ == "__main__":
    main()
