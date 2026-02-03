#!/usr/bin/env python3
"""
Error Analysis System for Baseline Evaluation

Supports three module types:
1. Binary Classifiers (M02, M04, M05, M12-M16) - Confusion Matrix, FP/FN
2. List Extractors (M01, M01a, M01b, M03) - Precision/Recall, Missing/Extra items
3. Structured Outputs (M06, M07, M08) - Field-level comparison

Three analysis modes:
A) Automated LLM Judge analysis
B) Pattern detection & clustering
C) Export for manual review
"""

import json
import os
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
import csv


# ============================================================
# Data Classes
# ============================================================

@dataclass
class BinaryError:
    """Error from binary classifier."""
    module: str
    record_id: str
    keyword: str
    expected: Any
    actual: Any
    error_type: str  # FP, FN
    confidence: Optional[float] = None
    reasoning: Optional[str] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class ListError:
    """Error from list extractor."""
    module: str
    record_id: str
    input_text: str
    expected_items: list
    actual_items: list
    missing_items: list  # In expected but not in actual
    extra_items: list    # In actual but not in expected
    precision: float
    recall: float
    metadata: dict = field(default_factory=dict)


@dataclass
class StructuredError:
    """Error from structured output."""
    module: str
    record_id: str
    input_text: str
    field_errors: dict  # {field_name: {expected, actual, match}}
    metadata: dict = field(default_factory=dict)


# ============================================================
# Module Configuration
# ============================================================

MODULE_TYPES = {
    # Binary Classifiers - output single classification
    "m02": {"type": "binary", "field": "branding_scope_1", "positive": "OB"},
    "m02b": {"type": "binary", "field": "branding_scope_1", "positive": "OB"},
    "m04": {"type": "binary", "field": "branding_scope_2", "positive": "CB"},
    "m04b": {"type": "binary", "field": "branding_scope_2", "positive": "CB"},
    "m05": {"type": "binary", "field": "branding_scope_3", "positive": "NB"},
    "m05b": {"type": "binary", "field": "branding_scope_3", "positive": "NB"},
    "m12": {"type": "binary", "field": "violates_constraint", "positive": True},
    "m12b": {"type": "binary", "field": "classification", "expected_field": "relevancy", "positive": "R"},
    "m13": {"type": "binary", "field": "same_product_type", "expected_field": "same_type", "positive": True},
    "m14": {"type": "binary", "field": "classification", "expected_field": "relevancy", "positive": "R"},
    "m15": {"type": "binary", "field": "classification", "expected_field": "relevancy", "positive": "S"},  # S = Substitute
    "m16": {"type": "binary", "field": "classification", "expected_field": "relevancy", "positive": "C"},  # C = Complement

    # List Extractors - output lists of items (use fuzzy matching)
    "m01": {"type": "list", "field": "brand_entities", "fuzzy": True},
    "m01a": {"type": "list", "field": "variations", "fuzzy": True},
    "m01b": {"type": "list", "field": "sub_brands", "fuzzy": True},
    "m03": {"type": "list", "field": "competitor_entities", "fuzzy": True},

    # List of dicts - taxonomy, attributes, etc.
    "m06": {"type": "list_of_dicts", "field": "taxonomy", "key_field": "product_type"},
    "m07": {"type": "list", "field": "variants", "fuzzy": True},
    "m08": {"type": "list_of_dicts", "field": "attribute_table", "key_field": "attribute"},
    "m11": {"type": "list", "field": "hard_constraints", "fuzzy": True},

    # Text comparison - simple string match
    "m09": {"type": "text", "field": "primary_use"},
    "m10": {"type": "text", "field": "validated_use"},
}


# ============================================================
# Binary Classifier Analysis
# ============================================================

class BinaryClassifierAnalyzer:
    """Analyze errors from binary classification modules."""

    def __init__(self, module: str, config: dict):
        self.module = module
        self.field = config["field"]  # Output field from model
        self.expected_field = config.get("expected_field", self.field)  # Expected field in dataset
        self.positive = config["positive"]

        # Confusion matrix
        self.tp = 0  # True Positive
        self.tn = 0  # True Negative
        self.fp = 0  # False Positive
        self.fn = 0  # False Negative

        self.errors: list[BinaryError] = []
        self.all_results: list[dict] = []

    def add_result(self, record: dict, actual_output: dict):
        """Add a single result to analysis."""
        expected = record.get("expected", {}).get(self.expected_field)
        actual = actual_output.get(self.field)

        # Normalize for comparison
        exp_positive = expected == self.positive or expected is True
        act_positive = actual == self.positive or actual is True

        result = {
            "record": record,
            "expected": expected,
            "actual": actual,
            "correct": expected == actual
        }
        self.all_results.append(result)

        # Update confusion matrix
        if exp_positive and act_positive:
            self.tp += 1
        elif not exp_positive and not act_positive:
            self.tn += 1
        elif not exp_positive and act_positive:
            self.fp += 1
            self._add_error(record, expected, actual, "FP", actual_output)
        else:  # exp_positive and not act_positive
            self.fn += 1
            self._add_error(record, expected, actual, "FN", actual_output)

    def _add_error(self, record: dict, expected: Any, actual: Any,
                   error_type: str, output: dict):
        """Record an error."""
        error = BinaryError(
            module=self.module,
            record_id=record.get("id", "unknown"),
            keyword=record.get("input", {}).get("keyword", str(record.get("input", {}))),
            expected=expected,
            actual=actual,
            error_type=error_type,
            confidence=output.get("confidence"),
            reasoning=output.get("reasoning"),
            metadata=record.get("metadata", {})
        )
        self.errors.append(error)

    def get_metrics(self) -> dict:
        """Calculate metrics."""
        total = self.tp + self.tn + self.fp + self.fn
        accuracy = (self.tp + self.tn) / total if total > 0 else 0

        precision = self.tp / (self.tp + self.fp) if (self.tp + self.fp) > 0 else 0
        recall = self.tp / (self.tp + self.fn) if (self.tp + self.fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

        return {
            "total": total,
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "confusion_matrix": {
                "tp": self.tp,
                "tn": self.tn,
                "fp": self.fp,
                "fn": self.fn
            },
            "error_counts": {
                "fp": self.fp,
                "fn": self.fn,
                "total_errors": self.fp + self.fn
            }
        }

    def get_errors_by_type(self) -> dict[str, list[BinaryError]]:
        """Group errors by type."""
        result = {"FP": [], "FN": []}
        for error in self.errors:
            result[error.error_type].append(error)
        return result


# ============================================================
# List Extractor Analysis
# ============================================================

class ListExtractorAnalyzer:
    """Analyze errors from list extraction modules."""

    def __init__(self, module: str, config: dict):
        self.module = module
        self.field = config["field"]
        self.errors: list[ListError] = []
        self.all_results: list[dict] = []

        self.total_precision = 0
        self.total_recall = 0
        self.count = 0

    def add_result(self, record: dict, actual_output: dict):
        """Add a single result to analysis."""
        expected_items = self._normalize_list(record.get("expected", {}).get(self.field, []))
        actual_items = self._normalize_list(actual_output.get(self.field, []))

        # Calculate set operations
        expected_set = set(expected_items)
        actual_set = set(actual_items)

        missing = list(expected_set - actual_set)
        extra = list(actual_set - expected_set)
        correct = expected_set & actual_set

        # Calculate metrics
        precision = len(correct) / len(actual_set) if actual_set else 1.0
        recall = len(correct) / len(expected_set) if expected_set else 1.0

        self.total_precision += precision
        self.total_recall += recall
        self.count += 1

        result = {
            "record": record,
            "expected": expected_items,
            "actual": actual_items,
            "precision": precision,
            "recall": recall,
            "correct": len(missing) == 0 and len(extra) == 0
        }
        self.all_results.append(result)

        # Record error if not perfect
        if missing or extra:
            error = ListError(
                module=self.module,
                record_id=record.get("id", "unknown"),
                input_text=str(record.get("input", {}))[:200],
                expected_items=expected_items,
                actual_items=actual_items,
                missing_items=missing,
                extra_items=extra,
                precision=precision,
                recall=recall,
                metadata=record.get("metadata", {})
            )
            self.errors.append(error)

    def _normalize_list(self, items: Any) -> list:
        """Normalize items to list of lowercase strings."""
        if isinstance(items, str):
            items = [items]
        if not isinstance(items, list):
            return []
        return [str(item).lower().strip() for item in items]

    def get_metrics(self) -> dict:
        """Calculate aggregate metrics."""
        avg_precision = self.total_precision / self.count if self.count > 0 else 0
        avg_recall = self.total_recall / self.count if self.count > 0 else 0
        avg_f1 = 2 * avg_precision * avg_recall / (avg_precision + avg_recall) if (avg_precision + avg_recall) > 0 else 0

        # Count error types
        missing_only = sum(1 for e in self.errors if e.missing_items and not e.extra_items)
        extra_only = sum(1 for e in self.errors if e.extra_items and not e.missing_items)
        both = sum(1 for e in self.errors if e.missing_items and e.extra_items)

        return {
            "total": self.count,
            "avg_precision": avg_precision,
            "avg_recall": avg_recall,
            "avg_f1": avg_f1,
            "error_counts": {
                "missing_only": missing_only,
                "extra_only": extra_only,
                "both": both,
                "total_errors": len(self.errors)
            }
        }

    def get_most_missed_items(self, top_n: int = 10) -> list[tuple[str, int]]:
        """Get most frequently missed items."""
        missed_counts = defaultdict(int)
        for error in self.errors:
            for item in error.missing_items:
                missed_counts[item] += 1
        return sorted(missed_counts.items(), key=lambda x: -x[1])[:top_n]

    def get_most_extra_items(self, top_n: int = 10) -> list[tuple[str, int]]:
        """Get most frequently hallucinated items."""
        extra_counts = defaultdict(int)
        for error in self.errors:
            for item in error.extra_items:
                extra_counts[item] += 1
        return sorted(extra_counts.items(), key=lambda x: -x[1])[:top_n]


# ============================================================
# Structured Output Analysis
# ============================================================

class StructuredOutputAnalyzer:
    """Analyze errors from structured output modules."""

    def __init__(self, module: str, config: dict):
        self.module = module
        self.fields = config["fields"]
        self.errors: list[StructuredError] = []
        self.all_results: list[dict] = []
        self.field_accuracy = {f: {"correct": 0, "total": 0} for f in self.fields}

    def add_result(self, record: dict, actual_output: dict):
        """Add a single result to analysis."""
        expected = record.get("expected", {})
        field_errors = {}
        has_error = False

        for field in self.fields:
            exp_val = expected.get(field)
            act_val = actual_output.get(field)
            match = self._compare_values(exp_val, act_val)

            self.field_accuracy[field]["total"] += 1
            if match:
                self.field_accuracy[field]["correct"] += 1
            else:
                has_error = True
                field_errors[field] = {"expected": exp_val, "actual": act_val}

        result = {
            "record": record,
            "expected": expected,
            "actual": actual_output,
            "correct": not has_error
        }
        self.all_results.append(result)

        if has_error:
            error = StructuredError(
                module=self.module,
                record_id=record.get("id", "unknown"),
                input_text=str(record.get("input", {}))[:200],
                field_errors=field_errors,
                metadata=record.get("metadata", {})
            )
            self.errors.append(error)

    def _compare_values(self, expected: Any, actual: Any) -> bool:
        """Compare two values, handling different types."""
        if expected is None and actual is None:
            return True
        if expected is None or actual is None:
            return False
        if isinstance(expected, list) and isinstance(actual, list):
            return set(str(x).lower() for x in expected) == set(str(x).lower() for x in actual)
        return str(expected).lower().strip() == str(actual).lower().strip()

    def get_metrics(self) -> dict:
        """Calculate metrics per field."""
        metrics = {"total": len(self.all_results)}

        for field, counts in self.field_accuracy.items():
            accuracy = counts["correct"] / counts["total"] if counts["total"] > 0 else 0
            metrics[f"{field}_accuracy"] = accuracy

        overall = sum(c["correct"] for c in self.field_accuracy.values())
        total = sum(c["total"] for c in self.field_accuracy.values())
        metrics["overall_field_accuracy"] = overall / total if total > 0 else 0
        metrics["error_count"] = len(self.errors)

        return metrics


# ============================================================
# Text Output Analysis (M09, M10)
# ============================================================

class TextAnalyzer:
    """Analyze text output modules with fuzzy string matching."""

    def __init__(self, module: str, config: dict):
        self.module = module
        self.field = config["field"]
        self.errors: list[StructuredError] = []
        self.all_results: list[dict] = []
        self.exact_matches = 0
        self.fuzzy_matches = 0
        self.count = 0

    def add_result(self, record: dict, actual_output: dict):
        """Add a single result to analysis."""
        expected = record.get("expected", {}).get(self.field, "")
        actual = actual_output.get(self.field, "")

        # Normalize for comparison
        exp_norm = str(expected).lower().strip() if expected else ""
        act_norm = str(actual).lower().strip() if actual else ""

        # Check exact match
        exact = exp_norm == act_norm

        # Fuzzy match - check if main words overlap
        fuzzy = False
        if not exact and exp_norm and act_norm:
            exp_words = set(exp_norm.split())
            act_words = set(act_norm.split())
            overlap = len(exp_words & act_words) / max(len(exp_words), 1)
            fuzzy = overlap >= 0.5

        self.count += 1
        if exact:
            self.exact_matches += 1
        elif fuzzy:
            self.fuzzy_matches += 1

        result = {
            "record": record,
            "expected": expected,
            "actual": actual,
            "correct": exact,
            "fuzzy_match": fuzzy
        }
        self.all_results.append(result)

        if not exact:
            error = StructuredError(
                module=self.module,
                record_id=record.get("id", "unknown"),
                input_text=str(record.get("input", {}))[:200],
                field_errors={self.field: {"expected": expected, "actual": actual, "fuzzy": fuzzy}},
                metadata=record.get("metadata", {})
            )
            self.errors.append(error)

    def get_metrics(self) -> dict:
        """Calculate metrics."""
        return {
            "total": self.count,
            "accuracy": self.exact_matches / self.count if self.count > 0 else 0,
            "exact_matches": self.exact_matches,
            "fuzzy_matches": self.fuzzy_matches,
            "fuzzy_accuracy": (self.exact_matches + self.fuzzy_matches) / self.count if self.count > 0 else 0,
            "error_count": len(self.errors)
        }


# ============================================================
# List of Dicts Analysis (M06, M08)
# ============================================================

class ListOfDictsAnalyzer:
    """Analyze list of dict outputs like taxonomy and attributes."""

    def __init__(self, module: str, config: dict):
        self.module = module
        self.field = config["field"]
        self.key_field = config.get("key_field", "value")
        self.errors: list[ListError] = []
        self.all_results: list[dict] = []
        self.total_precision = 0
        self.total_recall = 0
        self.count = 0

    def add_result(self, record: dict, actual_output: dict):
        """Add a single result to analysis."""
        expected_list = record.get("expected", {}).get(self.field, [])
        actual_list = actual_output.get(self.field, [])

        # Extract key values from dicts
        expected_keys = self._extract_keys(expected_list)
        actual_keys = self._extract_keys(actual_list)

        # Calculate set operations
        expected_set = set(expected_keys)
        actual_set = set(actual_keys)

        missing = list(expected_set - actual_set)
        extra = list(actual_set - expected_set)
        correct = expected_set & actual_set

        # Calculate metrics
        precision = len(correct) / len(actual_set) if actual_set else (1.0 if not expected_set else 0.0)
        recall = len(correct) / len(expected_set) if expected_set else (1.0 if not actual_set else 0.0)

        self.total_precision += precision
        self.total_recall += recall
        self.count += 1

        result = {
            "record": record,
            "expected": expected_list,
            "actual": actual_list,
            "precision": precision,
            "recall": recall,
            "correct": len(missing) == 0 and len(extra) == 0
        }
        self.all_results.append(result)

        # Record error if not perfect
        if missing or extra:
            error = ListError(
                module=self.module,
                record_id=record.get("id", "unknown"),
                input_text=str(record.get("input", {}))[:200],
                expected_items=list(expected_keys),
                actual_items=list(actual_keys),
                missing_items=missing,
                extra_items=extra,
                precision=precision,
                recall=recall,
                metadata=record.get("metadata", {})
            )
            self.errors.append(error)

    def _extract_keys(self, items: list) -> list:
        """Extract key values from list of dicts."""
        keys = []
        for item in items:
            if isinstance(item, dict):
                val = item.get(self.key_field, item.get("value", str(item)))
                keys.append(str(val).lower().strip())
            else:
                keys.append(str(item).lower().strip())
        return keys

    def get_metrics(self) -> dict:
        """Calculate aggregate metrics."""
        avg_precision = self.total_precision / self.count if self.count > 0 else 0
        avg_recall = self.total_recall / self.count if self.count > 0 else 0
        avg_f1 = 2 * avg_precision * avg_recall / (avg_precision + avg_recall) if (avg_precision + avg_recall) > 0 else 0

        return {
            "total": self.count,
            "avg_precision": avg_precision,
            "avg_recall": avg_recall,
            "avg_f1": avg_f1,
            "error_counts": {
                "total_errors": len(self.errors)
            }
        }


# ============================================================
# Main Error Analyzer
# ============================================================

class ErrorAnalyzer:
    """Main error analyzer coordinating all analysis types."""

    def __init__(self, output_dir: str = "experiment_results/error_analysis"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.analyzers: dict[str, Any] = {}

    def create_analyzer(self, module: str):
        """Create appropriate analyzer for module type."""
        config = MODULE_TYPES.get(module.lower())
        if not config:
            raise ValueError(f"Unknown module: {module}")

        module_type = config["type"]
        if module_type == "binary":
            return BinaryClassifierAnalyzer(module, config)
        elif module_type == "list":
            return ListExtractorAnalyzer(module, config)
        elif module_type == "structured":
            return StructuredOutputAnalyzer(module, config)
        elif module_type == "text":
            return TextAnalyzer(module, config)
        elif module_type == "list_of_dicts":
            return ListOfDictsAnalyzer(module, config)
        else:
            raise ValueError(f"Unknown module type: {module_type}")

    def analyze_batch_results(self, batch_dir: str, module: str) -> dict:
        """Analyze results from a batch processing run."""
        batch_path = Path(batch_dir)

        # Find results file for module - check results/ subdirectory first
        results_path = batch_path / "results"
        search_path = results_path if results_path.exists() else batch_path

        results_file = search_path / f"{module}_results.jsonl"
        if not results_file.exists():
            # Try uppercase
            results_file = search_path / f"{module.upper()}_results.jsonl"
        if not results_file.exists():
            # Try to find in combined results
            results_file = search_path / "results.jsonl"

        if not results_file.exists():
            raise FileNotFoundError(f"Results file not found for {module}")

        # Load original dataset for expected values
        dataset_patterns = [
            f"datasets/{module}_*.jsonl",
            f"datasets/{module.lower()}_*.jsonl"
        ]
        dataset_file = None
        for pattern in dataset_patterns:
            matches = list(Path(".").glob(pattern))
            if matches:
                dataset_file = matches[0]
                break

        if not dataset_file:
            raise FileNotFoundError(f"Dataset not found for {module}")

        # Load dataset as dict by index (to match batch custom_id format)
        # Use open() instead of read_text().splitlines() to avoid Unicode line separator issues
        dataset = {}
        with open(dataset_file) as f:
            for idx, line in enumerate(f):
                if line.strip():
                    record = json.loads(line)
                    # Use zero-padded index to match batch custom_id format (e.g., "00000")
                    record_id = str(idx).zfill(5)
                    dataset[record_id] = record

        # Create analyzer and process results
        analyzer = self.create_analyzer(module)
        self.analyzers[module] = analyzer

        parse_errors = 0
        with open(results_file) as f:
            for line in f:
                if line.strip():
                    result = json.loads(line)
                    custom_id = result.get("custom_id", "")
                    record_id = custom_id.replace(f"{module}_", "")

                    if record_id in dataset:
                        record = dataset[record_id]
                        output_str = result.get("response", {}).get("body", {}).get("choices", [{}])[0].get("message", {}).get("content", "{}")

                        # Handle truncated/invalid JSON from LLM
                        try:
                            if isinstance(output_str, str):
                                output = json.loads(output_str)
                            else:
                                output = output_str
                            analyzer.add_result(record, output)
                        except json.JSONDecodeError:
                            # Skip truncated responses (e.g., max_tokens reached)
                            parse_errors += 1
                            continue

        metrics = analyzer.get_metrics()
        if parse_errors > 0:
            metrics["parse_errors"] = parse_errors
        return metrics

    def export_errors_csv(self, module: str, output_file: Optional[str] = None) -> str:
        """Export errors to CSV for manual review."""
        analyzer = self.analyzers.get(module)
        if not analyzer:
            raise ValueError(f"No analyzer found for {module}. Run analyze_batch_results first.")

        if output_file is None:
            output_file = self.output_dir / f"{module}_errors.csv"

        if isinstance(analyzer, BinaryClassifierAnalyzer):
            with open(output_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=[
                    "module", "record_id", "keyword", "expected", "actual",
                    "error_type", "confidence", "reasoning"
                ])
                writer.writeheader()
                for error in analyzer.errors:
                    writer.writerow({
                        "module": error.module,
                        "record_id": error.record_id,
                        "keyword": error.keyword,
                        "expected": error.expected,
                        "actual": error.actual,
                        "error_type": error.error_type,
                        "confidence": error.confidence,
                        "reasoning": error.reasoning[:500] if error.reasoning else ""
                    })

        elif isinstance(analyzer, ListExtractorAnalyzer):
            with open(output_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=[
                    "module", "record_id", "input", "expected", "actual",
                    "missing", "extra", "precision", "recall"
                ])
                writer.writeheader()
                for error in analyzer.errors:
                    writer.writerow({
                        "module": error.module,
                        "record_id": error.record_id,
                        "input": error.input_text[:200],
                        "expected": "; ".join(error.expected_items),
                        "actual": "; ".join(error.actual_items),
                        "missing": "; ".join(error.missing_items),
                        "extra": "; ".join(error.extra_items),
                        "precision": f"{error.precision:.2f}",
                        "recall": f"{error.recall:.2f}"
                    })

        elif isinstance(analyzer, StructuredOutputAnalyzer):
            with open(output_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=[
                    "module", "record_id", "input", "field", "expected", "actual"
                ])
                writer.writeheader()
                for error in analyzer.errors:
                    for field, details in error.field_errors.items():
                        writer.writerow({
                            "module": error.module,
                            "record_id": error.record_id,
                            "input": error.input_text[:200],
                            "field": field,
                            "expected": str(details["expected"])[:200],
                            "actual": str(details["actual"])[:200]
                        })

        return str(output_file)

    def generate_report(self, modules: list[str] = None) -> str:
        """Generate markdown report for all analyzed modules."""
        if modules is None:
            modules = list(self.analyzers.keys())

        report = []
        report.append("# Error Analysis Report")
        report.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append(f"\n**Modules Analyzed:** {len(modules)}")

        # Summary table
        report.append("\n## Summary\n")
        report.append("| Module | Type | Total | Accuracy | Errors | FP | FN |")
        report.append("|--------|------|-------|----------|--------|----|----|")

        for module in modules:
            analyzer = self.analyzers.get(module)
            if not analyzer:
                continue

            metrics = analyzer.get_metrics()
            module_type = MODULE_TYPES.get(module, {}).get("type", "?")

            if isinstance(analyzer, BinaryClassifierAnalyzer):
                cm = metrics["confusion_matrix"]
                report.append(
                    f"| {module.upper()} | {module_type} | {metrics['total']} | "
                    f"{metrics['accuracy']:.1%} | {cm['fp'] + cm['fn']} | {cm['fp']} | {cm['fn']} |"
                )
            elif isinstance(analyzer, ListExtractorAnalyzer):
                ec = metrics["error_counts"]
                report.append(
                    f"| {module.upper()} | {module_type} | {metrics['total']} | "
                    f"P:{metrics['avg_precision']:.1%} R:{metrics['avg_recall']:.1%} | "
                    f"{ec['total_errors']} | {ec['extra_only']} | {ec['missing_only']} |"
                )
            else:
                report.append(
                    f"| {module.upper()} | {module_type} | {metrics['total']} | "
                    f"{metrics['overall_field_accuracy']:.1%} | {metrics['error_count']} | - | - |"
                )

        # Detailed sections for each module
        for module in modules:
            analyzer = self.analyzers.get(module)
            if not analyzer:
                continue

            report.append(f"\n---\n\n## {module.upper()}")
            metrics = analyzer.get_metrics()

            if isinstance(analyzer, BinaryClassifierAnalyzer):
                cm = metrics["confusion_matrix"]
                report.append(f"\n### Confusion Matrix\n")
                report.append("```")
                report.append(f"              Predicted")
                report.append(f"              Pos    Neg")
                report.append(f"Actual Pos    {cm['tp']:<6} {cm['fn']:<6}  (FN)")
                report.append(f"       Neg    {cm['fp']:<6} {cm['tn']:<6}")
                report.append(f"              (FP)")
                report.append("```")

                report.append(f"\n### Metrics\n")
                report.append(f"- **Accuracy:** {metrics['accuracy']:.1%}")
                report.append(f"- **Precision:** {metrics['precision']:.1%}")
                report.append(f"- **Recall:** {metrics['recall']:.1%}")
                report.append(f"- **F1 Score:** {metrics['f1']:.1%}")

                # Sample errors
                errors_by_type = analyzer.get_errors_by_type()
                for error_type in ["FP", "FN"]:
                    errors = errors_by_type[error_type][:5]
                    if errors:
                        report.append(f"\n### Sample {error_type} Errors ({len(errors_by_type[error_type])} total)\n")
                        for e in errors:
                            report.append(f"- **{e.keyword}**")
                            report.append(f"  - Expected: `{e.expected}`, Got: `{e.actual}`")
                            if e.reasoning:
                                report.append(f"  - Reasoning: {e.reasoning[:150]}...")

            elif isinstance(analyzer, ListExtractorAnalyzer):
                report.append(f"\n### Metrics\n")
                report.append(f"- **Avg Precision:** {metrics['avg_precision']:.1%}")
                report.append(f"- **Avg Recall:** {metrics['avg_recall']:.1%}")
                report.append(f"- **Avg F1:** {metrics['avg_f1']:.1%}")

                missed = analyzer.get_most_missed_items(5)
                if missed:
                    report.append(f"\n### Most Frequently Missed Items\n")
                    for item, count in missed:
                        report.append(f"- `{item}` ({count} times)")

                extra = analyzer.get_most_extra_items(5)
                if extra:
                    report.append(f"\n### Most Frequently Hallucinated Items\n")
                    for item, count in extra:
                        report.append(f"- `{item}` ({count} times)")

        report_text = "\n".join(report)

        # Save report
        report_file = self.output_dir / f"error_report_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
        report_file.write_text(report_text)

        return report_text


# ============================================================
# CLI Interface
# ============================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Analyze errors from batch results")
    parser.add_argument("--batch-dir", "-b", required=True, help="Directory with batch results")
    parser.add_argument("--modules", "-m", nargs="+", help="Modules to analyze (default: all)")
    parser.add_argument("--export-csv", action="store_true", help="Export errors to CSV")
    parser.add_argument("--output-dir", "-o", default="experiment_results/error_analysis")

    args = parser.parse_args()

    analyzer = ErrorAnalyzer(output_dir=args.output_dir)

    # Determine modules to analyze
    if args.modules:
        modules = args.modules
    else:
        # Find all result files in batch dir - check results/ subdirectory first
        batch_path = Path(args.batch_dir)
        results_path = batch_path / "results"
        search_path = results_path if results_path.exists() else batch_path
        modules = []
        for f in search_path.glob("*_results.jsonl"):
            module = f.stem.replace("_results", "").lower()
            if module in MODULE_TYPES:
                modules.append(module)

    print(f"Analyzing modules: {modules}")

    for module in modules:
        try:
            print(f"\nAnalyzing {module}...")
            metrics = analyzer.analyze_batch_results(args.batch_dir, module)
            print(f"  Metrics: {json.dumps(metrics, indent=2)}")

            if args.export_csv:
                csv_file = analyzer.export_errors_csv(module)
                print(f"  Exported: {csv_file}")
        except Exception as e:
            print(f"  Error: {e}")

    # Generate report
    report = analyzer.generate_report(modules)
    print(f"\n{'='*60}")
    print(report)


if __name__ == "__main__":
    main()
