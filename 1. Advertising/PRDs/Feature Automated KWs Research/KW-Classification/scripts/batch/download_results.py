#!/usr/bin/env python3
"""
Download results from completed OpenAI batch jobs.

Usage:
    python scripts/batch/download_results.py <batch_dir>
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


def download_batch_results(batch_id: str, output_path: Path) -> dict:
    """Download results for a completed batch."""

    # Get batch info
    batch = client.batches.retrieve(batch_id)

    if batch.status != "completed":
        return {
            "status": "not_ready",
            "batch_status": batch.status,
            "message": f"Batch is {batch.status}, not completed"
        }

    if not batch.output_file_id:
        return {
            "status": "no_output",
            "message": "Batch completed but no output file"
        }

    # Download output file
    file_content = client.files.content(batch.output_file_id)

    # Save to file
    with open(output_path, "wb") as f:
        f.write(file_content.read())

    # Count results
    results_count = 0
    with open(output_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                results_count += 1

    # Download error file if exists
    errors_count = 0
    if batch.error_file_id:
        error_path = output_path.with_suffix(".errors.jsonl")
        error_content = client.files.content(batch.error_file_id)
        with open(error_path, "wb") as f:
            f.write(error_content.read())

        with open(error_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    errors_count += 1

    return {
        "status": "downloaded",
        "output_file": str(output_path),
        "results_count": results_count,
        "errors_count": errors_count,
        "request_counts": {
            "total": batch.request_counts.total if batch.request_counts else 0,
            "completed": batch.request_counts.completed if batch.request_counts else 0,
            "failed": batch.request_counts.failed if batch.request_counts else 0,
        }
    }


def main():
    """Main entry point."""

    if len(sys.argv) < 2:
        print("Usage: python download_results.py <batch_dir>")
        sys.exit(1)

    batch_dir = Path(sys.argv[1])
    manifest_file = batch_dir / "upload_manifest.json"

    if not manifest_file.exists():
        print(f"Error: Upload manifest not found: {manifest_file}")
        sys.exit(1)

    # Load manifest
    with open(manifest_file, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    results = manifest.get("results", [])
    batches = [r for r in results if "batch_id" in r]

    if not batches:
        print("No batch IDs found in manifest.")
        sys.exit(1)

    # Create results directory
    results_dir = batch_dir / "results"
    results_dir.mkdir(exist_ok=True)

    print("=" * 70)
    print("DOWNLOAD BATCH RESULTS")
    print("=" * 70)
    print(f"Directory: {batch_dir}")
    print(f"Results dir: {results_dir}")
    print(f"Batches: {len(batches)}")
    print()

    # Download each batch
    download_results = []

    for batch_info in batches:
        module = batch_info["file"].replace("_batch.jsonl", "")
        batch_id = batch_info["batch_id"]

        print(f"Processing {module}...", end=" ")

        output_path = results_dir / f"{module}_results.jsonl"

        try:
            result = download_batch_results(batch_id, output_path)
            result["module"] = module
            result["batch_id"] = batch_id
            download_results.append(result)

            if result["status"] == "downloaded":
                print(f"✓ {result['results_count']} results")
            else:
                print(f"⏳ {result['message']}")

        except Exception as e:
            print(f"✗ Error: {e}")
            download_results.append({
                "module": module,
                "batch_id": batch_id,
                "status": "error",
                "error": str(e)
            })

    # Summary
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    downloaded = [r for r in download_results if r["status"] == "downloaded"]
    not_ready = [r for r in download_results if r["status"] == "not_ready"]
    errors = [r for r in download_results if r["status"] == "error"]

    total_results = sum(r.get("results_count", 0) for r in downloaded)
    total_errors = sum(r.get("errors_count", 0) for r in downloaded)

    print(f"Downloaded: {len(downloaded)}/{len(batches)} batches")
    print(f"Total results: {total_results}")

    if total_errors > 0:
        print(f"Total errors: {total_errors}")

    if not_ready:
        print()
        print("Not ready (still processing):")
        for r in not_ready:
            print(f"  {r['module']}: {r.get('batch_status', 'unknown')}")

    if errors:
        print()
        print("Errors:")
        for r in errors:
            print(f"  {r['module']}: {r.get('error', 'unknown')}")

    # Save download report
    report = {
        "timestamp": datetime.now().isoformat(),
        "results_dir": str(results_dir),
        "downloads": download_results,
        "summary": {
            "downloaded": len(downloaded),
            "not_ready": len(not_ready),
            "errors": len(errors),
            "total_results": total_results,
            "total_errors": total_errors
        }
    }

    report_file = batch_dir / "download_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\nDownload report saved: {report_file}")

    if downloaded:
        print()
        print("=" * 70)
        print("NEXT STEPS")
        print("=" * 70)
        print("Evaluate results against expected outputs:")
        print(f"  python scripts/batch/evaluate_results.py {batch_dir}")


if __name__ == "__main__":
    main()
