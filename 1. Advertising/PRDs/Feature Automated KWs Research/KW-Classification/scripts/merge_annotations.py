#!/usr/bin/env python3
"""
Merge Annotations

Combines annotator responses and creates final validated datasets.
Handles disagreement resolution and generates gold standard labels.
"""

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
ANNOTATION_TASKS_DIR = PROJECT_ROOT / "annotation_tasks"
VALIDATED_DIR = PROJECT_ROOT / "validated_data"


def normalize_label(value: str) -> str:
    """Normalize label for comparison."""
    if not value:
        return ""
    value = str(value).strip().lower()

    # Boolean normalization
    if value in ("true", "yes", "1", "t", "y"):
        return "true"
    if value in ("false", "no", "0", "f", "n"):
        return "false"

    # Classification labels
    if value in ("r", "relevant"):
        return "R"
    if value in ("s", "substitute"):
        return "S"
    if value in ("c", "complementary"):
        return "C"
    if value in ("n", "not relevant", "irrelevant", "none", "null"):
        return "N"
    if value in ("ob", "own brand", "own_brand"):
        return "OB"
    if value in ("cb", "competitor brand", "competitor_brand"):
        return "CB"
    if value in ("nb", "non-branded", "non_branded"):
        return "NB"

    return value.upper() if len(value) <= 2 else value


def find_annotation_columns(headers: List[str]) -> Dict[str, str]:
    """Find annotator columns in headers."""
    result = {
        "annotator_a_main": None,
        "annotator_b_main": None,
        "annotator_a_reasoning": None,
        "annotator_b_reasoning": None,
        "llm_main": None,
        "agreement": None,
        "notes": None,
    }

    for h in headers:
        h_lower = h.lower()

        if "annotator_a" in h_lower:
            if "reasoning" in h_lower:
                result["annotator_a_reasoning"] = h
            elif result["annotator_a_main"] is None:
                result["annotator_a_main"] = h

        elif "annotator_b" in h_lower:
            if "reasoning" in h_lower:
                result["annotator_b_reasoning"] = h
            elif result["annotator_b_main"] is None:
                result["annotator_b_main"] = h

        elif h_lower.startswith("llm_") and "reasoning" not in h_lower:
            if result["llm_main"] is None:
                result["llm_main"] = h

        elif h_lower == "agreement":
            result["agreement"] = h

        elif h_lower == "notes":
            result["notes"] = h

    return result


def resolve_disagreement(
    label_a: str,
    label_b: str,
    llm_label: str,
    strategy: str = "majority"
) -> tuple:
    """
    Resolve disagreement between annotators.

    Strategies:
    - majority: Use LLM as tiebreaker when A and B disagree
    - conservative: Mark as uncertain/needs_review when disagreement
    - annotator_a: Always prefer annotator A
    - annotator_b: Always prefer annotator B

    Returns:
        Tuple of (final_label, resolution_method)
    """
    norm_a = normalize_label(label_a)
    norm_b = normalize_label(label_b)
    norm_llm = normalize_label(llm_label)

    # Perfect agreement
    if norm_a == norm_b:
        return norm_a, "agreement"

    # Disagreement - apply strategy
    if strategy == "majority":
        # Use LLM as tiebreaker
        if norm_a == norm_llm:
            return norm_a, "majority_a_llm"
        elif norm_b == norm_llm:
            return norm_b, "majority_b_llm"
        else:
            # All three disagree - default to A
            return norm_a, "default_a"

    elif strategy == "conservative":
        return "NEEDS_REVIEW", "disagreement"

    elif strategy == "annotator_a":
        return norm_a, "prefer_a"

    elif strategy == "annotator_b":
        return norm_b, "prefer_b"

    return norm_a, "default"


def merge_annotation_file(
    csv_path: Path,
    strategy: str = "majority",
    output_dir: Optional[Path] = None,
    include_disagreements_only: bool = False
) -> Optional[Path]:
    """
    Merge annotations from completed annotation file.

    Creates a validated dataset with:
    - final_label: The resolved label
    - resolution: How the label was determined
    - annotator_agreement: Whether annotators agreed
    """

    # Load data
    rows = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        for row in reader:
            rows.append(row)

    if not rows:
        print(f"Error: No data in {csv_path}")
        return None

    # Find columns
    cols = find_annotation_columns(headers)

    if not cols["annotator_a_main"] or not cols["annotator_b_main"]:
        print(f"Error: Cannot find annotator columns")
        print(f"  Found: {cols}")
        return None

    print(f"Source: {csv_path}")
    print(f"Rows: {len(rows)}")
    print(f"Strategy: {strategy}")
    print(f"Columns:")
    print(f"  Annotator A: {cols['annotator_a_main']}")
    print(f"  Annotator B: {cols['annotator_b_main']}")
    print(f"  LLM: {cols['llm_main']}")

    # Process rows
    merged_rows = []
    stats = {
        "total": 0,
        "annotated": 0,
        "agreements": 0,
        "disagreements": 0,
        "resolution_methods": {},
    }

    for row in rows:
        label_a = row.get(cols["annotator_a_main"], "").strip()
        label_b = row.get(cols["annotator_b_main"], "").strip()
        llm_label = row.get(cols["llm_main"], "").strip() if cols["llm_main"] else ""

        stats["total"] += 1

        # Skip rows without both annotations
        if not label_a or not label_b:
            continue

        stats["annotated"] += 1

        # Check agreement
        norm_a = normalize_label(label_a)
        norm_b = normalize_label(label_b)
        agreed = norm_a == norm_b

        if agreed:
            stats["agreements"] += 1
        else:
            stats["disagreements"] += 1

        # Skip if only showing disagreements and they agreed
        if include_disagreements_only and agreed:
            continue

        # Resolve
        final_label, resolution = resolve_disagreement(
            label_a, label_b, llm_label, strategy
        )

        stats["resolution_methods"][resolution] = stats["resolution_methods"].get(resolution, 0) + 1

        # Build merged row
        merged_row = dict(row)
        merged_row["final_label"] = final_label
        merged_row["resolution"] = resolution
        merged_row["annotator_agreement"] = "1" if agreed else "0"

        merged_rows.append(merged_row)

    if not merged_rows:
        print("Error: No completed annotations to merge")
        return None

    # Setup output
    if output_dir is None:
        output_dir = VALIDATED_DIR

    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = csv_path.stem.replace("_annotation", "")
    suffix = "_disagreements" if include_disagreements_only else "_validated"
    output_filename = f"{stem}{suffix}_{timestamp}.csv"
    output_path = output_dir / output_filename

    # Write output
    output_headers = headers + ["final_label", "resolution", "annotator_agreement"]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=output_headers)
        writer.writeheader()
        writer.writerows(merged_rows)

    print(f"\nOutput: {output_path}")
    print(f"Merged rows: {len(merged_rows)}")

    # Print stats
    print("\n" + "-" * 40)
    print("MERGE STATISTICS")
    print("-" * 40)
    print(f"Total rows: {stats['total']}")
    print(f"Annotated: {stats['annotated']}")
    print(f"Agreements: {stats['agreements']} ({stats['agreements']/stats['annotated']*100:.1f}%)" if stats['annotated'] else "")
    print(f"Disagreements: {stats['disagreements']}")

    print("\nResolution methods:")
    for method, count in sorted(stats["resolution_methods"].items()):
        print(f"  {method}: {count}")

    return output_path


def create_gold_dataset(
    csv_path: Path,
    output_dir: Optional[Path] = None,
    format: str = "jsonl"
) -> Optional[Path]:
    """
    Create gold standard dataset from validated/merged file.

    Extracts only the essential fields needed for training/evaluation.
    """

    rows = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        for row in reader:
            rows.append(row)

    if not rows:
        print(f"Error: No data in {csv_path}")
        return None

    # Check for final_label column
    if "final_label" not in headers:
        print("Error: No 'final_label' column. Run merge first.")
        return None

    print(f"Source: {csv_path}")
    print(f"Rows: {len(rows)}")

    # Setup output
    if output_dir is None:
        output_dir = VALIDATED_DIR

    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = csv_path.stem.replace("_validated", "").replace("_disagreements", "")
    output_filename = f"{stem}_gold_{timestamp}.{format}"
    output_path = output_dir / output_filename

    # Extract gold records
    gold_records = []

    for row in rows:
        final_label = row.get("final_label", "").strip()

        if not final_label or final_label == "NEEDS_REVIEW":
            continue

        # Build minimal gold record
        gold_record = {
            "asin": row.get("asin", ""),
            "keyword": row.get("keyword", ""),
            "brand": row.get("brand_name", row.get("brand", "")),
            "label": final_label,
            "agreement": row.get("annotator_agreement", ""),
            "resolution": row.get("resolution", ""),
        }

        # Include additional context if available
        for key in ["product_title", "hard_constraints", "validated_use", "product_taxonomy"]:
            if key in row and row[key]:
                gold_record[key] = row[key]

        gold_records.append(gold_record)

    if not gold_records:
        print("Error: No valid gold records")
        return None

    # Write output
    if format == "jsonl":
        with open(output_path, "w", encoding="utf-8") as f:
            for record in gold_records:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
    else:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=gold_records[0].keys())
            writer.writeheader()
            writer.writerows(gold_records)

    print(f"Output: {output_path}")
    print(f"Gold records: {len(gold_records)}")

    return output_path


def list_files():
    """List available files for merging."""
    print("Annotation tasks:")
    print("-" * 60)

    if ANNOTATION_TASKS_DIR.exists():
        for f in sorted(ANNOTATION_TASKS_DIR.glob("*.csv")):
            print(f"  {f.name}")
    else:
        print("  (no annotation_tasks directory)")

    print("\nValidated data:")
    print("-" * 60)

    if VALIDATED_DIR.exists():
        for f in sorted(VALIDATED_DIR.glob("*")):
            print(f"  {f.name}")
    else:
        print("  (no validated_data directory)")


def main():
    parser = argparse.ArgumentParser(
        description="Merge annotations and create validated datasets"
    )
    subparsers = parser.add_subparsers(dest="command")

    # Merge command
    merge_parser = subparsers.add_parser("merge", help="Merge annotator responses")
    merge_parser.add_argument("file", type=Path, help="Annotation CSV file")
    merge_parser.add_argument(
        "--strategy", "-s",
        choices=["majority", "conservative", "annotator_a", "annotator_b"],
        default="majority",
        help="Disagreement resolution strategy"
    )
    merge_parser.add_argument("--output", "-o", type=Path, help="Output directory")
    merge_parser.add_argument(
        "--disagreements-only",
        action="store_true",
        help="Output only disagreements for review"
    )

    # Gold command
    gold_parser = subparsers.add_parser("gold", help="Create gold standard dataset")
    gold_parser.add_argument("file", type=Path, help="Validated CSV file")
    gold_parser.add_argument(
        "--format", "-f",
        choices=["jsonl", "csv"],
        default="jsonl",
        help="Output format"
    )
    gold_parser.add_argument("--output", "-o", type=Path, help="Output directory")

    # List command
    subparsers.add_parser("list", help="List available files")

    args = parser.parse_args()

    if args.command == "merge":
        file_path = args.file
        if not file_path.is_absolute():
            if (ANNOTATION_TASKS_DIR / file_path).exists():
                file_path = ANNOTATION_TASKS_DIR / file_path

        if not file_path.exists():
            print(f"File not found: {file_path}")
            return

        merge_annotation_file(
            csv_path=file_path,
            strategy=args.strategy,
            output_dir=args.output,
            include_disagreements_only=args.disagreements_only,
        )

    elif args.command == "gold":
        file_path = args.file
        if not file_path.is_absolute():
            if (VALIDATED_DIR / file_path).exists():
                file_path = VALIDATED_DIR / file_path

        if not file_path.exists():
            print(f"File not found: {file_path}")
            return

        create_gold_dataset(
            csv_path=file_path,
            output_dir=args.output,
            format=args.format,
        )

    elif args.command == "list":
        list_files()

    else:
        parser.print_help()
        print("\nWorkflow:")
        print("  1. Generate annotation CSV:  generate_annotation_csv.py generate m12")
        print("  2. Annotators fill in columns")
        print("  3. Calculate agreement:      calculate_agreement.py analyze file.csv")
        print("  4. Merge annotations:        merge_annotations.py merge file.csv")
        print("  5. Create gold dataset:      merge_annotations.py gold file.csv")
        print()
        print("Examples:")
        print("  # Merge with majority voting (LLM as tiebreaker)")
        print("  python scripts/merge_annotations.py merge M12_annotation.csv")
        print()
        print("  # Merge conservatively (mark disagreements for review)")
        print("  python scripts/merge_annotations.py merge M12_annotation.csv --strategy conservative")
        print()
        print("  # Export only disagreements for review")
        print("  python scripts/merge_annotations.py merge M12_annotation.csv --disagreements-only")
        print()
        print("  # Create gold standard JSONL")
        print("  python scripts/merge_annotations.py gold M12_validated.csv")


if __name__ == "__main__":
    main()
