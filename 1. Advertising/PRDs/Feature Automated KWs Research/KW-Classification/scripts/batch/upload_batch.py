#!/usr/bin/env python3
"""
Upload batch request files to OpenAI Batch API.

Creates batch jobs for all JSONL files in a directory.

Usage:
    python scripts/batch/upload_batch.py <batch_dir>
    python scripts/batch/upload_batch.py batch_requests/20260112_1200
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def upload_batch_file(filepath: Path) -> dict:
    """Upload a JSONL file to OpenAI and create a batch job."""

    # Step 1: Upload file
    print(f"  Uploading file: {filepath.name}...", end=" ")

    with open(filepath, "rb") as f:
        file_response = client.files.create(
            file=f,
            purpose="batch"
        )

    file_id = file_response.id
    print(f"file_id={file_id}")

    # Step 2: Create batch
    print(f"  Creating batch job...", end=" ")

    batch_response = client.batches.create(
        input_file_id=file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={
            "source_file": filepath.name,
            "created_at": datetime.now().isoformat()
        }
    )

    batch_id = batch_response.id
    print(f"batch_id={batch_id}")

    return {
        "file": filepath.name,
        "file_id": file_id,
        "batch_id": batch_id,
        "status": batch_response.status,
        "created_at": datetime.now().isoformat()
    }


def main():
    """Main entry point."""

    if len(sys.argv) < 2:
        print("Usage: python upload_batch.py <batch_dir>")
        print("Example: python upload_batch.py batch_requests/20260112_1200")
        sys.exit(1)

    batch_dir = Path(sys.argv[1])

    if not batch_dir.exists():
        print(f"Error: Directory not found: {batch_dir}")
        sys.exit(1)

    # Find all JSONL files
    jsonl_files = sorted(batch_dir.glob("*_batch.jsonl"))

    if not jsonl_files:
        print(f"Error: No *_batch.jsonl files found in {batch_dir}")
        sys.exit(1)

    print("=" * 70)
    print("BATCH UPLOAD")
    print("=" * 70)
    print(f"Directory: {batch_dir}")
    print(f"Files to upload: {len(jsonl_files)}")
    print()

    # Upload each file
    results = []

    for filepath in jsonl_files:
        module_id = filepath.stem.replace("_batch", "")
        print(f"Processing {module_id}:")

        try:
            result = upload_batch_file(filepath)
            results.append(result)
            print(f"  ✓ Batch created successfully")
        except Exception as e:
            print(f"  ✗ Error: {e}")
            results.append({
                "file": filepath.name,
                "error": str(e),
                "status": "failed"
            })

        print()

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    successful = [r for r in results if "batch_id" in r]
    failed = [r for r in results if "error" in r]

    print(f"Uploaded: {len(successful)}/{len(results)} files")

    if successful:
        print()
        print("Batch IDs:")
        for r in successful:
            module = r["file"].replace("_batch.jsonl", "")
            print(f"  {module}: {r['batch_id']}")

    if failed:
        print()
        print("Failed uploads:")
        for r in failed:
            print(f"  {r['file']}: {r['error']}")

    # Save upload manifest
    upload_manifest = {
        "timestamp": datetime.now().isoformat(),
        "source_dir": str(batch_dir),
        "results": results
    }

    manifest_file = batch_dir / "upload_manifest.json"
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(upload_manifest, f, indent=2)

    print(f"\nUpload manifest saved: {manifest_file}")

    # Print next steps
    print()
    print("=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("1. Check batch status:")
    print(f"   python scripts/batch/check_batch_status.py {batch_dir}")
    print("2. Download results when complete:")
    print(f"   python scripts/batch/download_results.py {batch_dir}")


if __name__ == "__main__":
    main()
