#!/usr/bin/env python3
"""
Sync Local Experiments to Braintrust

Uploads pending local experiments to Braintrust and updates the registry.
"""

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import PROJECT_NAME, load_api_key
from experiment_registry import ExperimentRegistry

try:
    import braintrust
except ImportError:
    print("Error: braintrust not installed. Run: pip install braintrust")
    sys.exit(1)


def load_csv_results(csv_path: str) -> list:
    """Load results from CSV file."""
    results = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Parse JSON fields
            try:
                input_data = json.loads(row.get("input", "{}"))
            except json.JSONDecodeError:
                input_data = {"raw": row.get("input", "")}

            try:
                output_data = json.loads(row.get("output", "{}"))
            except json.JSONDecodeError:
                output_data = {"raw": row.get("output", "")}

            try:
                expected_data = json.loads(row.get("expected", "{}"))
            except json.JSONDecodeError:
                expected_data = {"raw": row.get("expected", "")}

            try:
                metadata = json.loads(row.get("metadata", "{}"))
            except json.JSONDecodeError:
                metadata = {}

            results.append({
                "input": input_data,
                "output": output_data,
                "expected": expected_data,
                "metadata": metadata,
                "keyword": row.get("Keyword", ""),
                "asin": row.get("ASIN", ""),
                "brand": row.get("Brand", ""),
            })

    return results


def upload_experiment(
    local_id: str,
    module_id: str,
    csv_path: str,
    accuracy: float,
    samples: int
) -> tuple:
    """Upload experiment to Braintrust."""
    load_api_key()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    experiment_name = f"root_{module_id}_{local_id}_{timestamp}"

    print(f"  Loading CSV: {csv_path}")
    results = load_csv_results(csv_path)

    if not results:
        return None, "No results in CSV"

    print(f"  Uploading {len(results)} records to Braintrust...")

    experiment = braintrust.init(
        project=PROJECT_NAME,
        experiment=experiment_name,
        metadata={
            "module": module_id,
            "local_id": local_id,
            "source": "sync_upload",
            "timestamp": timestamp,
            "samples": samples,
            "accuracy": accuracy,
        }
    )

    for result in results:
        # Calculate score based on output vs expected
        output = result.get("output", {})
        expected = result.get("expected", {})

        # Simple match check for classifiers
        out_val = output.get("relevancy", output.get("classification", output.get("result")))
        exp_val = expected.get("relevancy", expected.get("classification", expected.get("result")))
        correct = str(out_val).lower() == str(exp_val).lower() if out_val and exp_val else out_val == exp_val

        experiment.log(
            input={
                "keyword": result.get("keyword", ""),
                "asin": result.get("asin", ""),
                **result.get("input", {}),
            },
            output=result.get("output", {}),
            expected=result.get("expected", {}),
            scores={"correct": 1.0 if correct else 0.0},
            metadata={
                "module": module_id,
                "local_id": local_id,
                **result.get("metadata", {}),
            }
        )

    experiment.summarize()

    braintrust_url = f"https://www.braintrust.dev/app/{PROJECT_NAME}/experiments/{experiment_name}"
    return experiment_name, braintrust_url


def sync_pending(limit: int = None, module_filter: str = None):
    """Sync all pending experiments to Braintrust."""
    registry = ExperimentRegistry()
    pending = registry.list_not_uploaded()

    if module_filter:
        pending = [p for p in pending if p.get("module_id") == module_filter]

    if limit:
        pending = pending[:limit]

    if not pending:
        print("No pending experiments to upload")
        return

    print(f"Found {len(pending)} pending experiments")
    print("=" * 60)

    success_count = 0
    error_count = 0

    for exp in pending:
        local_id = exp["local_id"]
        module_id = exp["module_id"]
        csv_path = exp.get("csv_path", "")

        print(f"\n{local_id} ({module_id})")

        if not csv_path or not Path(csv_path).exists():
            print(f"  SKIP: CSV not found at {csv_path}")
            error_count += 1
            continue

        try:
            bt_id, bt_url = upload_experiment(
                local_id=local_id,
                module_id=module_id,
                csv_path=csv_path,
                accuracy=exp.get("accuracy", 0),
                samples=exp.get("samples", 0)
            )

            if bt_url:
                registry.mark_uploaded(local_id, bt_id, bt_url)
                print(f"  SUCCESS: {bt_url}")
                success_count += 1
            else:
                print(f"  FAILED: {bt_id}")
                error_count += 1

        except Exception as e:
            print(f"  ERROR: {e}")
            registry.update_experiment(local_id, status="failed", notes=str(e))
            error_count += 1

    print("\n" + "=" * 60)
    print(f"SYNC COMPLETE: {success_count} uploaded, {error_count} errors")


def upload_single(local_id: str):
    """Upload a single experiment by local ID."""
    registry = ExperimentRegistry()
    exp = registry.get_experiment(local_id)

    if not exp:
        print(f"Experiment not found: {local_id}")
        return

    if exp.get("status") == "uploaded":
        print(f"Already uploaded: {exp.get('braintrust_url')}")
        return

    csv_path = exp.get("csv_path", "")
    if not csv_path or not Path(csv_path).exists():
        print(f"CSV not found: {csv_path}")
        return

    print(f"Uploading {local_id}...")

    try:
        bt_id, bt_url = upload_experiment(
            local_id=local_id,
            module_id=exp["module_id"],
            csv_path=csv_path,
            accuracy=exp.get("accuracy", 0),
            samples=exp.get("samples", 0)
        )

        if bt_url:
            registry.mark_uploaded(local_id, bt_id, bt_url)
            print(f"SUCCESS: {bt_url}")
        else:
            print(f"FAILED: {bt_id}")

    except Exception as e:
        print(f"ERROR: {e}")


def main():
    parser = argparse.ArgumentParser(description="Sync experiments to Braintrust")
    subparsers = parser.add_subparsers(dest="command")

    # Sync all pending
    sync_parser = subparsers.add_parser("sync", help="Sync pending experiments")
    sync_parser.add_argument("--limit", "-n", type=int, help="Max experiments to sync")
    sync_parser.add_argument("--module", "-m", help="Filter by module")

    # Upload single
    upload_parser = subparsers.add_parser("upload", help="Upload single experiment")
    upload_parser.add_argument("local_id", help="Local experiment ID")

    # Status
    status_parser = subparsers.add_parser("status", help="Show sync status")

    args = parser.parse_args()

    if args.command == "sync":
        sync_pending(limit=args.limit, module_filter=args.module)

    elif args.command == "upload":
        upload_single(args.local_id)

    elif args.command == "status":
        registry = ExperimentRegistry()
        stats = registry.get_stats()
        print("Sync Status")
        print("=" * 40)
        print(f"Total experiments: {stats['total']}")
        print(f"  local_only: {stats['by_status'].get('local_only', 0)}")
        print(f"  uploaded: {stats['by_status'].get('uploaded', 0)}")
        print(f"  failed: {stats['by_status'].get('failed', 0)}")

    else:
        parser.print_help()
        print("\nExamples:")
        print("  # Sync all pending experiments")
        print("  python scripts/sync_braintrust.py sync")
        print("")
        print("  # Sync only m12 experiments")
        print("  python scripts/sync_braintrust.py sync --module m12")
        print("")
        print("  # Upload specific experiment")
        print("  python scripts/sync_braintrust.py upload exp_20260116_123456_m12")
        print("")
        print("  # Check status")
        print("  python scripts/sync_braintrust.py status")


if __name__ == "__main__":
    main()
