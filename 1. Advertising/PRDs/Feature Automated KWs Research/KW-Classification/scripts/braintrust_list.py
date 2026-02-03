#!/usr/bin/env python3
"""
List resources from Braintrust project.

Usage:
    python scripts/braintrust_list.py --all
    python scripts/braintrust_list.py --prompts
    python scripts/braintrust_list.py --datasets
    python scripts/braintrust_list.py --experiments
    python scripts/braintrust_list.py --scorers
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))
from config import PROJECT_ID, PROJECT_NAME, load_api_key

try:
    import braintrust
except ImportError:
    print("Error: braintrust package not installed. Run: pip install braintrust")
    sys.exit(1)


def list_prompts():
    """List all prompts in the project."""
    print("\n" + "=" * 60)
    print("PROMPTS")
    print("=" * 60)

    try:
        # Initialize client
        client = braintrust.api.projects.retrieve(PROJECT_ID)
        prompts = braintrust.api.prompts.list(project_id=PROJECT_ID)

        print(f"\n{'Slug':<45} {'ID':<40}")
        print("-" * 85)

        for prompt in prompts:
            print(f"{prompt.slug:<45} {prompt.id:<40}")

        print(f"\nTotal: {len(list(prompts))} prompts")

    except Exception as e:
        print(f"Error listing prompts: {e}")
        # Fallback: list local prompts
        print("\nLocal prompts (from files):")
        prompts_dir = Path(__file__).parent.parent / "prompts" / "modules"
        if prompts_dir.exists():
            for f in sorted(prompts_dir.glob("*.md")):
                print(f"  - {f.stem}")


def list_datasets():
    """List all datasets in the project."""
    print("\n" + "=" * 60)
    print("DATASETS")
    print("=" * 60)

    try:
        datasets = braintrust.api.datasets.list(project_id=PROJECT_ID)

        print(f"\n{'Name':<50} {'ID':<40}")
        print("-" * 90)

        for ds in datasets:
            print(f"{ds.name:<50} {ds.id:<40}")

        print(f"\nTotal: {len(list(datasets))} datasets")

    except Exception as e:
        print(f"Error listing datasets: {e}")
        # Fallback: list local datasets
        print("\nLocal datasets (from files):")
        datasets_dir = Path(__file__).parent.parent / "datasets"
        if datasets_dir.exists():
            for f in sorted(datasets_dir.glob("*.jsonl")):
                # Count records
                with open(f) as fh:
                    count = sum(1 for _ in fh)
                print(f"  - {f.stem} ({count} records)")


def list_experiments():
    """List experiments in the project."""
    print("\n" + "=" * 60)
    print("EXPERIMENTS")
    print("=" * 60)

    try:
        experiments = braintrust.api.experiments.list(project_id=PROJECT_ID)

        print(f"\n{'Name':<40} {'ID':<40} {'Created':<20}")
        print("-" * 100)

        for exp in experiments:
            created = exp.created[:10] if hasattr(exp, 'created') else 'N/A'
            print(f"{exp.name:<40} {exp.id:<40} {created:<20}")

        print(f"\nTotal: {len(list(experiments))} experiments")

    except Exception as e:
        print(f"Error listing experiments: {e}")
        # Fallback: list local experiment results
        print("\nLocal experiment results:")
        results_dir = Path(__file__).parent.parent / "experiment_results"
        if results_dir.exists():
            files = sorted(results_dir.glob("*.jsonl"))[:10]  # Last 10
            for f in files:
                print(f"  - {f.name}")
            if len(list(results_dir.glob("*.jsonl"))) > 10:
                print(f"  ... and more")


def list_scorers():
    """List scorers (functions) in the project."""
    print("\n" + "=" * 60)
    print("SCORERS (Functions)")
    print("=" * 60)

    try:
        functions = braintrust.api.functions.list(project_id=PROJECT_ID)

        print(f"\n{'Name':<40} {'ID':<40} {'Type':<15}")
        print("-" * 95)

        for func in functions:
            func_type = func.function_type if hasattr(func, 'function_type') else 'scorer'
            print(f"{func.name:<40} {func.id:<40} {func_type:<15}")

        print(f"\nTotal: {len(list(functions))} functions")

    except Exception as e:
        print(f"Error listing scorers: {e}")
        # Fallback: list local scorer files
        print("\nLocal scorer files:")
        scorers_dir = Path(__file__).parent.parent / "scorers"
        if scorers_dir.exists():
            for f in sorted(scorers_dir.glob("*.py")):
                print(f"  - {f.name}")


def export_to_json(output_file: str = None):
    """Export all resource IDs to JSON file."""
    if output_file is None:
        output_file = f"braintrust_resources_{datetime.now().strftime('%Y%m%d_%H%M')}.json"

    resources = {
        "project": {
            "id": PROJECT_ID,
            "name": PROJECT_NAME,
        },
        "prompts": [],
        "datasets": [],
        "experiments": [],
        "scorers": [],
    }

    try:
        # Prompts
        for p in braintrust.api.prompts.list(project_id=PROJECT_ID):
            resources["prompts"].append({
                "id": p.id,
                "slug": p.slug,
                "name": p.name if hasattr(p, 'name') else p.slug,
            })

        # Datasets
        for ds in braintrust.api.datasets.list(project_id=PROJECT_ID):
            resources["datasets"].append({
                "id": ds.id,
                "name": ds.name,
            })

        # Experiments
        for exp in braintrust.api.experiments.list(project_id=PROJECT_ID):
            resources["experiments"].append({
                "id": exp.id,
                "name": exp.name,
            })

        # Scorers
        for func in braintrust.api.functions.list(project_id=PROJECT_ID):
            resources["scorers"].append({
                "id": func.id,
                "name": func.name,
            })

        # Save to file
        output_path = Path(__file__).parent.parent / output_file
        with open(output_path, 'w') as f:
            json.dump(resources, f, indent=2)

        print(f"\nExported to: {output_path}")
        print(f"  - {len(resources['prompts'])} prompts")
        print(f"  - {len(resources['datasets'])} datasets")
        print(f"  - {len(resources['experiments'])} experiments")
        print(f"  - {len(resources['scorers'])} scorers")

    except Exception as e:
        print(f"Error exporting: {e}")


def main():
    parser = argparse.ArgumentParser(description="List Braintrust resources")
    parser.add_argument("--prompts", action="store_true", help="List prompts")
    parser.add_argument("--datasets", action="store_true", help="List datasets")
    parser.add_argument("--experiments", action="store_true", help="List experiments")
    parser.add_argument("--scorers", action="store_true", help="List scorers/functions")
    parser.add_argument("--all", action="store_true", help="List all resources")
    parser.add_argument("--export", type=str, nargs="?", const="", help="Export to JSON file")

    args = parser.parse_args()

    # Load API key
    try:
        api_key = load_api_key()
        os.environ["BRAINTRUST_API_KEY"] = api_key
    except ValueError as e:
        print(f"Error: {e}")
        print("Set BRAINTRUST_API_KEY in .env file or environment")
        sys.exit(1)

    print(f"Project: {PROJECT_NAME}")
    print(f"ID: {PROJECT_ID}")

    if args.export is not None:
        export_to_json(args.export if args.export else None)
        return

    if args.all:
        list_prompts()
        list_datasets()
        list_experiments()
        list_scorers()
    else:
        if args.prompts:
            list_prompts()
        if args.datasets:
            list_datasets()
        if args.experiments:
            list_experiments()
        if args.scorers:
            list_scorers()

    if not any([args.prompts, args.datasets, args.experiments, args.scorers, args.all]):
        parser.print_help()


if __name__ == "__main__":
    main()
