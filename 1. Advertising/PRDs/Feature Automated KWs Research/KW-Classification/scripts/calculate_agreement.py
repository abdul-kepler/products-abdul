#!/usr/bin/env python3
"""
Calculate Inter-Annotator Agreement

Computes Cohen's Kappa and other agreement metrics for completed annotation files.
Supports all 22 modules with module-specific evaluation logic.
"""

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
ANNOTATION_TASKS_DIR = PROJECT_ROOT / "annotation_tasks"


def cohens_kappa(labels_a: List[str], labels_b: List[str]) -> Tuple[float, Dict]:
    """
    Calculate Cohen's Kappa for two annotators.

    Returns:
        Tuple of (kappa score, detailed stats)
    """
    if len(labels_a) != len(labels_b):
        raise ValueError("Label lists must have same length")

    n = len(labels_a)
    if n == 0:
        return 0.0, {"error": "No samples"}

    # Get all unique labels
    all_labels = sorted(set(labels_a) | set(labels_b))

    # Build confusion matrix
    confusion = {}
    for label in all_labels:
        confusion[label] = {l: 0 for l in all_labels}

    for a, b in zip(labels_a, labels_b):
        confusion[a][b] += 1

    # Calculate observed agreement (P_o)
    agreements = sum(1 for a, b in zip(labels_a, labels_b) if a == b)
    p_o = agreements / n

    # Calculate expected agreement by chance (P_e)
    counts_a = Counter(labels_a)
    counts_b = Counter(labels_b)

    p_e = sum(
        (counts_a.get(label, 0) / n) * (counts_b.get(label, 0) / n)
        for label in all_labels
    )

    # Calculate Kappa
    if p_e == 1.0:
        kappa = 1.0 if p_o == 1.0 else 0.0
    else:
        kappa = (p_o - p_e) / (1 - p_e)

    return kappa, {
        "n": n,
        "observed_agreement": p_o,
        "expected_agreement": p_e,
        "agreements": agreements,
        "disagreements": n - agreements,
        "labels": all_labels,
        "confusion_matrix": confusion,
        "counts_a": dict(counts_a),
        "counts_b": dict(counts_b),
    }


def jaccard_similarity(set_a: set, set_b: set) -> float:
    """Calculate Jaccard similarity for set comparison."""
    if not set_a and not set_b:
        return 1.0
    union = set_a | set_b
    if not union:
        return 1.0
    intersection = set_a & set_b
    return len(intersection) / len(union)


def interpret_kappa(kappa: float) -> str:
    """Interpret Cohen's Kappa value."""
    if kappa < 0:
        return "Poor (worse than chance)"
    elif kappa < 0.20:
        return "Slight"
    elif kappa < 0.40:
        return "Fair"
    elif kappa < 0.60:
        return "Moderate"
    elif kappa < 0.80:
        return "Substantial"
    else:
        return "Almost Perfect"


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

    return value


def parse_list_field(value: str) -> set:
    """Parse comma-separated or JSON list field."""
    if not value:
        return set()

    value = value.strip()

    # Try JSON array
    if value.startswith("["):
        try:
            items = json.loads(value)
            return set(str(item).strip().lower() for item in items if item)
        except json.JSONDecodeError:
            pass

    # Comma-separated
    return set(item.strip().lower() for item in value.split(",") if item.strip())


def analyze_annotation_csv(csv_path: Path, verbose: bool = False) -> Dict:
    """Analyze completed annotation CSV and calculate agreement metrics."""

    results = {
        "file": str(csv_path),
        "module": None,
        "total_rows": 0,
        "annotated_rows": 0,
        "metrics": {},
        "errors": [],
    }

    # Detect module from filename
    filename = csv_path.stem.upper()
    for module in ["M01A", "M01B", "M01", "M02B", "M02", "M03", "M04B", "M04",
                   "M05B", "M05", "M06", "M07", "M08", "M09", "M10", "M11",
                   "M12B", "M12", "M13", "M14", "M15", "M16"]:
        if module in filename:
            results["module"] = module.lower()
            break

    # Load data
    rows = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        for row in reader:
            rows.append(row)

    results["total_rows"] = len(rows)
    results["headers"] = headers

    if not rows:
        results["errors"].append("No data rows found")
        return results

    # Detect annotation columns
    annotator_a_cols = [h for h in headers if "annotator_a" in h.lower()]
    annotator_b_cols = [h for h in headers if "annotator_b" in h.lower()]

    if not annotator_a_cols or not annotator_b_cols:
        results["errors"].append("No annotator columns found")
        return results

    # Find main classification columns (not reasoning)
    main_a_col = None
    main_b_col = None

    for col in annotator_a_cols:
        if "reasoning" not in col.lower() and "notes" not in col.lower():
            main_a_col = col
            break

    for col in annotator_b_cols:
        if "reasoning" not in col.lower() and "notes" not in col.lower():
            main_b_col = col
            break

    if not main_a_col or not main_b_col:
        results["errors"].append("Cannot find main annotation columns")
        return results

    results["annotation_columns"] = {
        "annotator_a": main_a_col,
        "annotator_b": main_b_col,
    }

    # Extract labels
    labels_a = []
    labels_b = []
    annotated_count = 0

    for row in rows:
        val_a = row.get(main_a_col, "").strip()
        val_b = row.get(main_b_col, "").strip()

        # Only count rows where both annotators provided labels
        if val_a and val_b:
            labels_a.append(normalize_label(val_a))
            labels_b.append(normalize_label(val_b))
            annotated_count += 1

    results["annotated_rows"] = annotated_count

    if annotated_count == 0:
        results["errors"].append("No completed annotations found")
        return results

    # Calculate Cohen's Kappa
    kappa, stats = cohens_kappa(labels_a, labels_b)

    results["metrics"] = {
        "cohens_kappa": round(kappa, 4),
        "interpretation": interpret_kappa(kappa),
        "observed_agreement": round(stats["observed_agreement"], 4),
        "expected_agreement": round(stats["expected_agreement"], 4),
        "agreements": stats["agreements"],
        "disagreements": stats["disagreements"],
        "labels_found": stats["labels"],
        "distribution_a": stats["counts_a"],
        "distribution_b": stats["counts_b"],
    }

    if verbose:
        results["confusion_matrix"] = stats["confusion_matrix"]

    return results


def print_report(analysis: Dict, verbose: bool = False):
    """Print formatted agreement report."""
    print()
    print("=" * 60)
    print("INTER-ANNOTATOR AGREEMENT REPORT")
    print("=" * 60)

    print(f"\nFile: {Path(analysis['file']).name}")
    print(f"Module: {analysis.get('module', 'Unknown').upper()}")
    print(f"Total rows: {analysis['total_rows']}")
    print(f"Annotated rows: {analysis['annotated_rows']}")

    if analysis.get("errors"):
        print(f"\nErrors:")
        for error in analysis["errors"]:
            print(f"  - {error}")
        return

    cols = analysis.get("annotation_columns", {})
    print(f"\nColumns compared:")
    print(f"  Annotator A: {cols.get('annotator_a')}")
    print(f"  Annotator B: {cols.get('annotator_b')}")

    metrics = analysis.get("metrics", {})

    print("\n" + "-" * 40)
    print("AGREEMENT METRICS")
    print("-" * 40)

    kappa = metrics.get("cohens_kappa", 0)
    print(f"\nCohen's Kappa: {kappa:.4f}")
    print(f"Interpretation: {metrics.get('interpretation', 'N/A')}")

    print(f"\nObserved Agreement: {metrics.get('observed_agreement', 0):.2%}")
    print(f"Expected Agreement: {metrics.get('expected_agreement', 0):.2%}")

    print(f"\nAgreements: {metrics.get('agreements', 0)}")
    print(f"Disagreements: {metrics.get('disagreements', 0)}")

    print(f"\nLabels found: {', '.join(metrics.get('labels_found', []))}")

    print("\nDistribution - Annotator A:")
    for label, count in sorted(metrics.get("distribution_a", {}).items()):
        print(f"  {label}: {count}")

    print("\nDistribution - Annotator B:")
    for label, count in sorted(metrics.get("distribution_b", {}).items()):
        print(f"  {label}: {count}")

    if verbose and "confusion_matrix" in analysis:
        print("\n" + "-" * 40)
        print("CONFUSION MATRIX")
        print("-" * 40)

        labels = metrics.get("labels_found", [])
        matrix = analysis["confusion_matrix"]

        # Header
        print(f"\n{'':>12}", end="")
        for label in labels:
            print(f"{label:>10}", end="")
        print("  (Annotator B)")

        # Rows
        for label_a in labels:
            print(f"{label_a:>12}", end="")
            for label_b in labels:
                val = matrix.get(label_a, {}).get(label_b, 0)
                print(f"{val:>10}", end="")
            print()

        print("(Annotator A)")

    print("\n" + "=" * 60)

    # Kappa interpretation guide
    print("\nKappa Interpretation Guide:")
    print("  < 0.00: Poor (worse than chance)")
    print("  0.00 - 0.20: Slight agreement")
    print("  0.21 - 0.40: Fair agreement")
    print("  0.41 - 0.60: Moderate agreement")
    print("  0.61 - 0.80: Substantial agreement")
    print("  0.81 - 1.00: Almost perfect agreement")


def list_annotation_files():
    """List available annotation files."""
    if not ANNOTATION_TASKS_DIR.exists():
        print("No annotation_tasks directory found")
        return

    files = list(ANNOTATION_TASKS_DIR.glob("*.csv"))

    if not files:
        print("No annotation CSV files found")
        return

    print("Available annotation files:")
    print("-" * 60)

    for csv_file in sorted(files):
        # Quick check for annotations
        with open(csv_file, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        total = len(rows)
        annotated = 0

        headers = rows[0].keys() if rows else []
        a_col = next((h for h in headers if "annotator_a" in h.lower() and "reasoning" not in h.lower()), None)
        b_col = next((h for h in headers if "annotator_b" in h.lower() and "reasoning" not in h.lower()), None)

        if a_col and b_col:
            for row in rows:
                if row.get(a_col, "").strip() and row.get(b_col, "").strip():
                    annotated += 1

        status = "✓" if annotated > 0 else "○"
        print(f"  {status} {csv_file.name}")
        print(f"      Rows: {total} | Annotated: {annotated}")


def main():
    parser = argparse.ArgumentParser(
        description="Calculate inter-annotator agreement metrics"
    )
    subparsers = parser.add_subparsers(dest="command")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze annotation file")
    analyze_parser.add_argument("file", type=Path, help="Annotation CSV file")
    analyze_parser.add_argument("--verbose", "-v", action="store_true", help="Show confusion matrix")
    analyze_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # List command
    subparsers.add_parser("list", help="List annotation files")

    # Batch command
    batch_parser = subparsers.add_parser("batch", help="Analyze all files")
    batch_parser.add_argument("--verbose", "-v", action="store_true")

    args = parser.parse_args()

    if args.command == "analyze":
        file_path = args.file
        if not file_path.is_absolute():
            # Check annotation_tasks dir
            if (ANNOTATION_TASKS_DIR / file_path).exists():
                file_path = ANNOTATION_TASKS_DIR / file_path

        if not file_path.exists():
            print(f"File not found: {file_path}")
            return

        analysis = analyze_annotation_csv(file_path, verbose=args.verbose)

        if args.json:
            print(json.dumps(analysis, indent=2, default=str))
        else:
            print_report(analysis, verbose=args.verbose)

    elif args.command == "list":
        list_annotation_files()

    elif args.command == "batch":
        if not ANNOTATION_TASKS_DIR.exists():
            print("No annotation_tasks directory")
            return

        files = list(ANNOTATION_TASKS_DIR.glob("*.csv"))
        if not files:
            print("No annotation files found")
            return

        print(f"Analyzing {len(files)} files...")
        print("=" * 60)

        summary = []

        for csv_file in sorted(files):
            analysis = analyze_annotation_csv(csv_file)

            if analysis.get("metrics"):
                summary.append({
                    "file": csv_file.name,
                    "module": analysis.get("module", "?"),
                    "annotated": analysis["annotated_rows"],
                    "kappa": analysis["metrics"].get("cohens_kappa", 0),
                    "interpretation": analysis["metrics"].get("interpretation", "N/A"),
                })

        # Print summary table
        print(f"\n{'File':<40} {'Module':<8} {'N':<6} {'Kappa':<8} {'Interpretation'}")
        print("-" * 80)

        for item in summary:
            if item["annotated"] > 0:
                print(f"{item['file']:<40} {item['module']:<8} {item['annotated']:<6} {item['kappa']:<8.4f} {item['interpretation']}")
            else:
                print(f"{item['file']:<40} {item['module']:<8} {'(no annotations)'}")

    else:
        parser.print_help()
        print("\nExamples:")
        print("  # List annotation files")
        print("  python scripts/calculate_agreement.py list")
        print()
        print("  # Analyze single file")
        print("  python scripts/calculate_agreement.py analyze M12_annotation_20260116.csv")
        print()
        print("  # Analyze with confusion matrix")
        print("  python scripts/calculate_agreement.py analyze M12_annotation.csv --verbose")
        print()
        print("  # Analyze all files")
        print("  python scripts/calculate_agreement.py batch")


if __name__ == "__main__":
    main()
