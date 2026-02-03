#!/usr/bin/env python3
"""
Audit all local resources vs Braintrust mappings.

Usage:
    python scripts/audit_resources.py
    python scripts/audit_resources.py --detailed
    python scripts/audit_resources.py --output audit_report.yaml
"""

import argparse
import yaml
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent

# Paths
PROMPTS_DIR = PROJECT_ROOT / "prompts" / "modules"
SCHEMAS_DIR = PROJECT_ROOT / "prompts" / "json_schemas"
DATASETS_DIR = PROJECT_ROOT / "datasets"
SCORERS_DIR = PROJECT_ROOT / "scorers"

PROMPT_MAPPING_FILE = PROJECT_ROOT / "evaluation_KD" / "evaluation_experimentV5" / "prompt_mappings.yaml"
EXPERIMENT_MAPPING_FILE = PROJECT_ROOT / "evaluation_KD" / "evaluation_experimentV5" / "experiment_mappings.yaml"


def load_yaml(path: Path) -> dict:
    """Load YAML file."""
    if not path.exists():
        return {}
    with open(path) as f:
        return yaml.safe_load(f) or {}


def get_local_prompts() -> list[dict]:
    """Get all local prompt files."""
    prompts = []
    for f in sorted(PROMPTS_DIR.glob("*.md")):
        stem = f.stem
        # Extract module ID
        parts = stem.split("_")
        module_id = parts[0]

        # Determine version
        version = "v1"
        if "_v2" in stem or "v2_" in stem:
            version = "v2"
        elif "_v3" in stem or "v3_" in stem:
            version = "v3"
        elif "_v6" in stem:
            version = "v6"

        prompts.append({
            "file": str(f.relative_to(PROJECT_ROOT)),
            "stem": stem,
            "module": module_id,
            "version": version,
        })
    return prompts


def get_local_schemas() -> list[dict]:
    """Get all local JSON schema files."""
    schemas = []
    for f in sorted(SCHEMAS_DIR.glob("*.json")):
        stem = f.stem.replace("_schema", "")
        parts = stem.split("_")
        module_id = parts[0]

        schemas.append({
            "file": str(f.relative_to(PROJECT_ROOT)),
            "stem": stem,
            "module": module_id,
        })
    return schemas


def get_local_datasets() -> list[dict]:
    """Get all local dataset files."""
    datasets = []
    for f in sorted(DATASETS_DIR.glob("*.jsonl")):
        stem = f.stem
        parts = stem.split("_")
        module_id = parts[0]

        # Count records
        with open(f) as fh:
            count = sum(1 for _ in fh)

        # Determine variant
        variant = None
        if "_sd_" in stem or "_sd1" in stem:
            variant = "sd"
        elif "_v2" in stem:
            variant = "v2"
        elif "_v3" in stem:
            variant = "v3"

        datasets.append({
            "file": str(f.relative_to(PROJECT_ROOT)),
            "stem": stem,
            "module": module_id,
            "variant": variant,
            "records": count,
        })
    return datasets


def get_local_scorers() -> list[dict]:
    """Get all local scorer files."""
    scorers = []
    for f in sorted(SCORERS_DIR.glob("*.py")):
        if f.name.startswith("__"):
            continue
        scorers.append({
            "file": str(f.relative_to(PROJECT_ROOT)),
            "name": f.stem,
        })
    return scorers


def get_mapped_prompts() -> list[dict]:
    """Get prompts from prompt_mappings.yaml."""
    mapping = load_yaml(PROMPT_MAPPING_FILE)
    return mapping.get("prompts", [])


def get_braintrust_datasets() -> list[dict]:
    """Get datasets from experiment_mappings.yaml."""
    mapping = load_yaml(EXPERIMENT_MAPPING_FILE)

    # Extract unique datasets
    datasets = {}
    for exp in mapping.get("experiments", []):
        ds_id = exp.get("dataset_id")
        if ds_id and ds_id not in datasets:
            datasets[ds_id] = {
                "braintrust_id": ds_id,
                "braintrust_name": exp.get("dataset_name"),
                "local_file": exp.get("local_file"),
                "module": exp.get("module"),
            }
    return list(datasets.values())


def get_braintrust_prompts_from_experiments() -> list[dict]:
    """Get unique prompt IDs from experiment_mappings.yaml."""
    mapping = load_yaml(EXPERIMENT_MAPPING_FILE)

    prompts = {}
    for exp in mapping.get("experiments", []):
        prompt_id = exp.get("prompt_id")
        if prompt_id and prompt_id != "null" and prompt_id not in prompts:
            prompts[prompt_id] = {
                "braintrust_id": prompt_id,
                "module": exp.get("module"),
                "experiment": exp.get("braintrust_name"),
            }
    return list(prompts.values())


def run_audit(detailed: bool = False) -> dict:
    """Run full audit."""
    # Gather local resources
    local_prompts = get_local_prompts()
    local_schemas = get_local_schemas()
    local_datasets = get_local_datasets()
    local_scorers = get_local_scorers()

    # Gather Braintrust mappings
    mapped_prompts = get_mapped_prompts()
    bt_datasets = get_braintrust_datasets()
    bt_prompts_from_exp = get_braintrust_prompts_from_experiments()

    # Build lookup sets
    mapped_prompt_files = {p.get("local_file") for p in mapped_prompts}
    bt_dataset_names = {d.get("braintrust_name") for d in bt_datasets}

    # Analyze gaps
    unmapped_prompts = [p for p in local_prompts if p["file"] not in mapped_prompt_files]

    # Match local datasets to Braintrust
    matched_datasets = []
    unmatched_datasets = []
    for ld in local_datasets:
        # Try to find matching Braintrust dataset
        matched = False
        for bd in bt_datasets:
            if bd.get("local_file") and ld["file"] in bd.get("local_file", ""):
                matched_datasets.append({**ld, "braintrust_id": bd["braintrust_id"], "braintrust_name": bd["braintrust_name"]})
                matched = True
                break
        if not matched:
            unmatched_datasets.append(ld)

    # Group by module
    prompts_by_module = defaultdict(list)
    for p in local_prompts:
        prompts_by_module[p["module"]].append(p)

    datasets_by_module = defaultdict(list)
    for d in local_datasets:
        datasets_by_module[d["module"]].append(d)

    report = {
        "audit_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "summary": {
            "local_prompts": len(local_prompts),
            "local_schemas": len(local_schemas),
            "local_datasets": len(local_datasets),
            "local_scorers": len(local_scorers),
            "mapped_prompts": len(mapped_prompts),
            "braintrust_datasets": len(bt_datasets),
            "braintrust_prompt_refs": len(bt_prompts_from_exp),
            "unmapped_prompts": len(unmapped_prompts),
            "unmatched_datasets": len(unmatched_datasets),
        },
        "unmapped_prompts": [p["file"] for p in unmapped_prompts],
        "unmatched_datasets": [d["file"] for d in unmatched_datasets],
    }

    if detailed:
        report["local_prompts"] = local_prompts
        report["local_datasets"] = local_datasets
        report["mapped_prompts"] = mapped_prompts
        report["braintrust_datasets"] = bt_datasets
        report["modules"] = {
            module: {
                "prompts": [p["file"] for p in prompts_by_module[module]],
                "datasets": [d["file"] for d in datasets_by_module[module]],
            }
            for module in sorted(set(list(prompts_by_module.keys()) + list(datasets_by_module.keys())))
        }

    return report


def print_report(report: dict):
    """Print audit report."""
    print("\n" + "=" * 80)
    print("RESOURCE AUDIT REPORT")
    print("=" * 80)
    print(f"Date: {report['audit_date']}")

    print("\n--- SUMMARY ---")
    s = report["summary"]
    print(f"Local Prompts:        {s['local_prompts']:3d}")
    print(f"Local Schemas:        {s['local_schemas']:3d}")
    print(f"Local Datasets:       {s['local_datasets']:3d}")
    print(f"Local Scorers:        {s['local_scorers']:3d}")
    print()
    print(f"Mapped Prompts:       {s['mapped_prompts']:3d}  (in prompt_mappings.yaml)")
    print(f"Braintrust Datasets:  {s['braintrust_datasets']:3d}  (in experiment_mappings.yaml)")
    print(f"Braintrust Prompt Refs: {s['braintrust_prompt_refs']:3d}  (referenced in experiments)")

    print("\n--- GAPS ---")
    print(f"⚠️  Unmapped Prompts:   {s['unmapped_prompts']:3d}")
    print(f"⚠️  Unmatched Datasets: {s['unmatched_datasets']:3d}")

    if report["unmapped_prompts"]:
        print("\n--- UNMAPPED PROMPTS (need Braintrust IDs) ---")
        for f in report["unmapped_prompts"]:
            print(f"  - {f}")

    if report["unmatched_datasets"]:
        print("\n--- UNMATCHED DATASETS (not in Braintrust or no local match) ---")
        for f in report["unmatched_datasets"]:
            print(f"  - {f}")

    print("\n" + "=" * 80)


def main():
    parser = argparse.ArgumentParser(description="Audit local vs Braintrust resources")
    parser.add_argument("--detailed", "-d", action="store_true", help="Include detailed breakdown")
    parser.add_argument("--output", "-o", type=str, help="Save report to YAML file")
    args = parser.parse_args()

    report = run_audit(detailed=args.detailed)

    if args.output:
        output_path = PROJECT_ROOT / args.output
        with open(output_path, "w") as f:
            yaml.dump(report, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        print(f"Report saved to: {output_path}")

    print_report(report)


if __name__ == "__main__":
    main()
