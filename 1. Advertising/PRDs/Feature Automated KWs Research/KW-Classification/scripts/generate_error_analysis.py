#!/usr/bin/env python3
"""
Generate error analysis markdown files from experiment results.

Creates files similar to brand_scope_errors_full.md for any module.

Usage:
    python scripts/generate_error_analysis.py --module m02b
    python scripts/generate_error_analysis.py --module m12b --csv-file specific_file.csv
    python scripts/generate_error_analysis.py --all
"""

import argparse
import csv
import json
from pathlib import Path
from datetime import datetime
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "experiment_results"
DOCS_DIR = PROJECT_ROOT / "docs"

# Module configurations
MODULE_CONFIG = {
    "m02b": {
        "folder": "M02B_ClassifyOwnBrandKeywords_PathB",
        "output_key": "branding_scope_1",
        "positive_value": "OB",
        "name": "Classify Own Brand Keywords (Path B)",
        "context_keys": ["variations_own", "related_terms_own"],
    },
    "m04b": {
        "folder": "M04B_ClassifyCompetitorBrandKeywords_PathB",
        "output_key": "branding_scope_2",
        "positive_value": "CB",
        "name": "Classify Competitor Brand Keywords (Path B)",
        "context_keys": ["competitor_entities"],
    },
    "m05b": {
        "folder": "M05B_ClassifyNonBrandedKeywords_PathB",
        "output_key": "branding_scope_3",
        "positive_value": "NB",
        "name": "Classify Non-Branded Keywords (Path B)",
        "context_keys": ["brand_entities", "competitor_entities"],
    },
    "m09": {
        "folder": "M09_IdentifyPrimaryIntendedUse",
        "output_key": "primary_use",
        "positive_value": None,  # String comparison
        "name": "Identify Primary Intended Use",
        "context_keys": ["taxonomy", "title"],
        "comparison_type": "string",
    },
    "m10": {
        "folder": "M10_ValidatePrimaryIntendedUse",
        "output_key": "validated_use",
        "positive_value": None,  # String comparison
        "name": "Validate Primary Intended Use",
        "context_keys": ["primary_use", "keyword"],
        "comparison_type": "string",
    },
    "m12": {
        "folder": "M12_HardConstraintViolationCheck",
        "output_key": "relevancy",
        "positive_value": "N",  # N = violation detected
        "name": "Hard Constraint Violation Check",
        "context_keys": ["hard_constraints", "keyword"],
    },
    "m12b": {
        "folder": "M12B_CombinedClassification",
        "output_key": "relevancy",
        "positive_value": None,  # Multi-class: R, N, C, S
        "name": "Combined Classification",
        "context_keys": ["keyword", "taxonomy", "validated_use"],
        "comparison_type": "multiclass",
        "classes": ["R", "N", "C", "S"],  # Relevant, Not Relevant, Complementary, Substitute
    },
    "m13": {
        "folder": "M13_ProductTypeCheck",
        "output_key": "same_type",
        "positive_value": True,
        "name": "Product Type Check",
        "context_keys": ["keyword", "taxonomy"],
    },
    "m14": {
        "folder": "M14_PrimaryUseCheckSameType",
        "output_key": "relevancy",
        "positive_value": "R",
        "name": "Primary Use Check (Same Type)",
        "context_keys": ["keyword", "validated_use"],
        "classes": ["R", "N"],  # Relevant (same use), Not relevant
    },
    "m15": {
        "folder": "M15_SubstituteCheck",
        "output_key": "relevancy",
        "positive_value": "S",
        "name": "Substitute Check",
        "context_keys": ["keyword", "taxonomy", "validated_use"],
        "classes": ["S", "Null"],  # Substitute, Not substitute
    },
    "m16": {
        "folder": "M16_ComplementaryCheck",
        "output_key": "relevancy",
        "positive_value": "C",
        "name": "Complementary Check",
        "context_keys": ["keyword", "taxonomy", "validated_use"],
        "classes": ["C", "N"],  # Complementary, Not complementary
    },
}


def find_latest_csv(folder_path: Path) -> Path | None:
    """Find the most recent CSV file in a folder."""
    csv_files = list(folder_path.glob("*.csv"))
    if not csv_files:
        return None
    # Sort by modification time, newest first
    csv_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return csv_files[0]


def parse_json_field(value: str) -> Any:
    """Parse a JSON field, returning None if empty or invalid."""
    if not value or value.strip() == "":
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def get_nested_value(obj: dict, key: str) -> Any:
    """Get a value from a nested dict, supporting dot notation."""
    if obj is None:
        return None
    keys = key.split(".")
    for k in keys:
        if isinstance(obj, dict):
            obj = obj.get(k)
        else:
            return None
    return obj


def compare_values(expected: Any, output: Any, comparison_type: str = "exact") -> bool:
    """Compare expected and output values."""
    if comparison_type == "string":
        # Fuzzy string comparison for things like primary_use
        if expected is None and output is None:
            return True
        if expected is None or output is None:
            return False
        exp_str = str(expected).lower().strip()
        out_str = str(output).lower().strip()
        # Check for exact match or containment
        return exp_str == out_str or exp_str in out_str or out_str in exp_str
    elif comparison_type == "multiclass":
        # Exact comparison for multiclass
        return expected == output
    else:
        # Exact comparison
        return expected == output


def analyze_errors(csv_path: Path, config: dict) -> dict:
    """Analyze errors in experiment results."""
    output_key = config["output_key"]
    positive_value = config["positive_value"]
    comparison_type = config.get("comparison_type", "exact")
    context_keys = config.get("context_keys", [])
    classes = config.get("classes", [])

    errors = {"fp": [], "fn": [], "other": [], "by_class": {}}
    confusion_matrix = {}  # For multiclass: {expected: {output: count}}
    total = 0
    correct = 0

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            total += 1

            # Parse JSON fields
            input_data = parse_json_field(row.get("input", ""))
            output_data = parse_json_field(row.get("output", ""))
            expected_data = parse_json_field(row.get("expected", ""))

            # Get the key values
            expected_val = get_nested_value(expected_data, output_key) if expected_data else None
            output_val = get_nested_value(output_data, output_key) if output_data else None
            reasoning = get_nested_value(output_data, "reasoning") if output_data else ""

            # For M12B and others, check nested structure
            if output_key == "relevancy" and output_val is None and output_data:
                output_val = output_data.get("relevancy")

            # Normalize "Null" string to None for comparison
            if expected_val == "Null":
                expected_val = None
            if output_val == "Null":
                output_val = None

            # Track confusion matrix for multiclass
            if comparison_type == "multiclass":
                if expected_val not in confusion_matrix:
                    confusion_matrix[expected_val] = {}
                if output_val not in confusion_matrix[expected_val]:
                    confusion_matrix[expected_val][output_val] = 0
                confusion_matrix[expected_val][output_val] += 1

            # Check if correct
            is_correct = compare_values(expected_val, output_val, comparison_type)

            if is_correct:
                correct += 1
                continue

            # Build error record
            error = {
                "keyword": row.get("Keyword") or get_nested_value(input_data, "keyword"),
                "asin": row.get("ASIN") or get_nested_value(input_data, "asin"),
                "brand": row.get("Brand"),
                "expected": expected_val,
                "output": output_val,
                "reasoning": reasoning or "",
                "context": {},
            }

            # Add context
            for ctx_key in context_keys:
                ctx_val = get_nested_value(input_data, ctx_key) if input_data else None
                if ctx_val is not None:
                    error["context"][ctx_key] = ctx_val

            # Classify error type
            if comparison_type == "multiclass":
                # Group by expected->output transition
                key = f"{expected_val}_to_{output_val}"
                if key not in errors["by_class"]:
                    errors["by_class"][key] = []
                errors["by_class"][key].append(error)
            elif comparison_type == "string":
                errors["other"].append(error)
            elif positive_value is not None:
                if output_val == positive_value and expected_val != positive_value:
                    errors["fp"].append(error)  # False Positive
                elif output_val != positive_value and expected_val == positive_value:
                    errors["fn"].append(error)  # False Negative
                else:
                    errors["other"].append(error)
            else:
                errors["other"].append(error)

    return {
        "total": total,
        "correct": correct,
        "errors": errors,
        "accuracy": correct / total if total > 0 else 0,
        "confusion_matrix": confusion_matrix,
        "classes": classes,
    }


def format_context(context: dict, max_length: int = 200) -> str:
    """Format context for display."""
    if not context:
        return ""

    parts = []
    for key, val in context.items():
        if isinstance(val, list):
            val_str = str(val)[:max_length]
        elif isinstance(val, dict):
            val_str = json.dumps(val)[:max_length]
        else:
            val_str = str(val)[:max_length]
        parts.append(f"{key}: {val_str}")

    return "\n".join(parts)


def generate_markdown(module_id: str, config: dict, analysis: dict, csv_path: Path) -> str:
    """Generate markdown error report."""
    lines = []
    comparison_type = config.get("comparison_type", "exact")

    # Header
    lines.append(f"# {config['name']} Error Analysis")
    lines.append("")
    lines.append(f"> Module: {module_id.upper()}")
    lines.append(f"> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"> Source: {csv_path.name}")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Total records:** {analysis['total']}")
    lines.append(f"- **Correct:** {analysis['correct']}")
    lines.append(f"- **Errors:** {analysis['total'] - analysis['correct']}")
    lines.append(f"- **Accuracy:** {analysis['accuracy']:.2%}")
    lines.append("")

    # Confusion matrix for multiclass
    if comparison_type == "multiclass" and analysis.get("confusion_matrix"):
        lines.append("## Confusion Matrix")
        lines.append("")
        cm = analysis["confusion_matrix"]
        all_classes = sorted(set(list(cm.keys()) + [c for v in cm.values() for c in v.keys()]))

        # Header row
        lines.append("| Expected \\ Output | " + " | ".join(all_classes) + " |")
        lines.append("| --- | " + " | ".join(["---"] * len(all_classes)) + " |")

        # Data rows
        for exp_class in all_classes:
            row = [exp_class]
            for out_class in all_classes:
                count = cm.get(exp_class, {}).get(out_class, 0)
                row.append(str(count))
            lines.append("| " + " | ".join(row) + " |")
        lines.append("")

    errors = analysis["errors"]

    # Multiclass errors by transition
    if errors.get("by_class"):
        lines.append("## Errors by Classification")
        lines.append("")

        for transition, errs in sorted(errors["by_class"].items(), key=lambda x: -len(x[1])):
            exp, out = transition.split("_to_")
            lines.append(f"### {exp} → {out}: {len(errs)} errors")
            lines.append("")

            for i, err in enumerate(errs[:20], 1):  # Limit to 20 per type
                lines.append(f"#### #{i}")
                lines.append(f"**Keyword:** `{err['keyword']}`")
                if err.get("asin"):
                    lines.append(f"**ASIN:** {err['asin']}")
                lines.append(f"**Expected:** {err['expected']}")
                lines.append(f"**Model Output:** {err['output']}")
                lines.append(f"**Reasoning:** {err['reasoning'][:500] if err['reasoning'] else 'N/A'}")
                if err["context"]:
                    ctx = format_context(err["context"])
                    lines.append(f"**Context:**")
                    lines.append(f"```")
                    lines.append(ctx)
                    lines.append(f"```")
                lines.append("")

            if len(errs) > 20:
                lines.append(f"*... and {len(errs) - 20} more errors*")
                lines.append("")

    # False Positives
    if errors["fp"]:
        lines.append(f"## FALSE POSITIVES (FP): {len(errors['fp'])} errors")
        lines.append("")
        lines.append(f"Model incorrectly predicted **{config['positive_value']}** when expected **null/other**")
        lines.append("")

        for i, err in enumerate(errors["fp"], 1):
            lines.append(f"### FP #{i}")
            lines.append(f"**Keyword:** `{err['keyword']}`")
            if err.get("asin"):
                lines.append(f"**ASIN:** {err['asin']}")
            lines.append(f"**Expected:** {err['expected']}")
            lines.append(f"**Model Output:** {err['output']}")
            lines.append(f"**Reasoning:** {err['reasoning'][:500] if err['reasoning'] else 'N/A'}")
            if err["context"]:
                ctx = format_context(err["context"])
                lines.append(f"**Context:**")
                lines.append(f"```")
                lines.append(ctx)
                lines.append(f"```")
            lines.append("")

    # False Negatives
    if errors["fn"]:
        lines.append(f"## FALSE NEGATIVES (FN): {len(errors['fn'])} errors")
        lines.append("")
        lines.append(f"Model incorrectly predicted **null/other** when expected **{config['positive_value']}**")
        lines.append("")

        for i, err in enumerate(errors["fn"], 1):
            lines.append(f"### FN #{i}")
            lines.append(f"**Keyword:** `{err['keyword']}`")
            if err.get("asin"):
                lines.append(f"**ASIN:** {err['asin']}")
            lines.append(f"**Expected:** {err['expected']}")
            lines.append(f"**Model Output:** {err['output']}")
            lines.append(f"**Reasoning:** {err['reasoning'][:500] if err['reasoning'] else 'N/A'}")
            if err["context"]:
                ctx = format_context(err["context"])
                lines.append(f"**Context:**")
                lines.append(f"```")
                lines.append(ctx)
                lines.append(f"```")
            lines.append("")

    # Other Errors (for string comparisons)
    if errors["other"]:
        lines.append(f"## OTHER ERRORS: {len(errors['other'])} errors")
        lines.append("")

        for i, err in enumerate(errors["other"][:50], 1):  # Limit to 50
            lines.append(f"### Error #{i}")
            lines.append(f"**Keyword:** `{err['keyword']}`")
            if err.get("asin"):
                lines.append(f"**ASIN:** {err['asin']}")
            lines.append(f"**Expected:** {err['expected']}")
            lines.append(f"**Model Output:** {err['output']}")
            lines.append(f"**Reasoning:** {err['reasoning'][:500] if err['reasoning'] else 'N/A'}")
            if err["context"]:
                ctx = format_context(err["context"])
                lines.append(f"**Context:**")
                lines.append(f"```")
                lines.append(ctx)
                lines.append(f"```")
            lines.append("")

        if len(errors["other"]) > 50:
            lines.append(f"*... and {len(errors['other']) - 50} more errors*")
            lines.append("")

    return "\n".join(lines)


def process_module(module_id: str, csv_file: str | None = None) -> None:
    """Process a single module and generate error report."""
    module_id = module_id.lower()

    if module_id not in MODULE_CONFIG:
        print(f"Error: Unknown module '{module_id}'")
        print(f"Available modules: {', '.join(MODULE_CONFIG.keys())}")
        return

    config = MODULE_CONFIG[module_id]
    folder_path = RESULTS_DIR / config["folder"]

    if not folder_path.exists():
        print(f"Error: Results folder not found: {folder_path}")
        return

    # Find CSV file
    if csv_file:
        csv_path = folder_path / csv_file
        if not csv_path.exists():
            print(f"Error: CSV file not found: {csv_path}")
            return
    else:
        csv_path = find_latest_csv(folder_path)
        if not csv_path:
            print(f"Error: No CSV files found in {folder_path}")
            return

    print(f"Processing {module_id.upper()} from {csv_path.name}...")

    # Analyze errors
    analysis = analyze_errors(csv_path, config)

    print(f"  Total: {analysis['total']}, Correct: {analysis['correct']}, Errors: {analysis['total'] - analysis['correct']}")
    print(f"  Accuracy: {analysis['accuracy']:.2%}")
    print(f"  FP: {len(analysis['errors']['fp'])}, FN: {len(analysis['errors']['fn'])}, Other: {len(analysis['errors']['other'])}")

    # Generate markdown
    markdown = generate_markdown(module_id, config, analysis, csv_path)

    # Save to docs folder
    output_file = DOCS_DIR / f"{module_id}_errors.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(markdown)

    print(f"  Saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Generate error analysis markdown files")
    parser.add_argument("--module", "-m", help="Module ID (e.g., m02b, m12b)")
    parser.add_argument("--csv-file", help="Specific CSV file to use")
    parser.add_argument("--all", action="store_true", help="Process all modules")
    parser.add_argument("--list", action="store_true", help="List available modules")
    args = parser.parse_args()

    if args.list:
        print("Available modules:")
        for mod_id, config in MODULE_CONFIG.items():
            print(f"  {mod_id}: {config['name']}")
        return

    if args.all:
        for module_id in MODULE_CONFIG.keys():
            process_module(module_id)
            print()
    elif args.module:
        process_module(args.module, args.csv_file)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
