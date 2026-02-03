#!/usr/bin/env python3
"""
Baseline Report Generator

Generates comprehensive baseline report from batch results:
- Overall accuracy summary
- Per-module metrics
- Error analysis
- Path A vs Path B comparison
- Recommendations

Output: Markdown report suitable for documentation/stakeholders
"""

import json
import argparse
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from .error_analyzer import ErrorAnalyzer, MODULE_TYPES
    from .cohens_kappa import calculate_cohens_kappa
    from .path_comparator import PATH_PAIRS
except ImportError:
    from error_analyzer import ErrorAnalyzer, MODULE_TYPES
    from cohens_kappa import calculate_cohens_kappa
    from path_comparator import PATH_PAIRS


class BaselineReportGenerator:
    """Generate comprehensive baseline evaluation report."""

    def __init__(self, batch_dir: str, output_dir: str = None):
        self.batch_path = Path(batch_dir)
        self.output_path = Path(output_dir) if output_dir else self.batch_path / "reports"
        self.output_path.mkdir(parents=True, exist_ok=True)

        self.metrics = {}
        self.errors = {}
        self.comparisons = {}

    def analyze_all_modules(self) -> dict:
        """Run analysis on all available modules."""
        analyzer = ErrorAnalyzer(output_dir=str(self.output_path))

        # Check for results/ subdirectory
        results_path = self.batch_path / "results"
        search_path = results_path if results_path.exists() else self.batch_path

        for results_file in search_path.glob("*_results.jsonl"):
            module = results_file.stem.replace("_results", "").lower()

            if module not in MODULE_TYPES:
                continue

            print(f"Analyzing {module}...")

            try:
                metrics = analyzer.analyze_batch_results(str(self.batch_path), module)
                self.metrics[module] = metrics

                # Get errors
                module_analyzer = analyzer.analyzers.get(module)
                if module_analyzer:
                    self.errors[module] = len(module_analyzer.errors)
            except Exception as e:
                print(f"  Error: {e}")
                self.metrics[module] = {"error": str(e)}

        return self.metrics

    def compare_paths(self) -> dict:
        """Compare Path A vs Path B for branding modules."""
        for task_name, config in PATH_PAIRS.items():
            path_a = config["path_a"]
            path_b = config["path_b"]

            if path_a not in self.metrics or path_b not in self.metrics:
                continue

            acc_a = self.metrics[path_a].get("accuracy", 0)
            acc_b = self.metrics[path_b].get("accuracy", 0)

            self.comparisons[task_name] = {
                "path_a": path_a,
                "path_b": path_b,
                "accuracy_a": acc_a,
                "accuracy_b": acc_b,
                "winner": "A" if acc_a > acc_b else "B" if acc_b > acc_a else "TIE",
                "difference": abs(acc_a - acc_b)
            }

        return self.comparisons

    def generate_report(self) -> str:
        """Generate comprehensive markdown report."""
        report = []

        # Header
        report.append("# Baseline Evaluation Report")
        report.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append(f"\n**Batch Directory:** `{self.batch_path}`")

        # Executive Summary
        report.append("\n## Executive Summary\n")

        total_modules = len([m for m in self.metrics if "error" not in self.metrics[m]])
        avg_accuracy = sum(
            m.get("accuracy", m.get("avg_precision", 0))
            for m in self.metrics.values() if isinstance(m, dict) and "error" not in m
        ) / total_modules if total_modules > 0 else 0

        report.append(f"- **Modules Evaluated:** {total_modules}")
        report.append(f"- **Average Accuracy:** {avg_accuracy:.1%}")

        # Binary classifiers summary
        binary_modules = [m for m, cfg in MODULE_TYPES.items()
                         if cfg.get("type") == "binary" and m in self.metrics]
        if binary_modules:
            binary_avg = sum(self.metrics[m].get("accuracy", 0) for m in binary_modules) / len(binary_modules)
            report.append(f"- **Binary Classifier Avg:** {binary_avg:.1%}")

        # List extractors summary
        list_modules = [m for m, cfg in MODULE_TYPES.items()
                       if cfg.get("type") == "list" and m in self.metrics]
        if list_modules:
            list_avg = sum(self.metrics[m].get("avg_precision", 0) for m in list_modules) / len(list_modules)
            report.append(f"- **List Extractor Avg Precision:** {list_avg:.1%}")

        # Overall accuracy table
        report.append("\n## Module Performance Summary\n")
        report.append("| Module | Type | Primary Metric | Value | Errors |")
        report.append("|--------|------|----------------|-------|--------|")

        # Group by type - include all types
        for module_type in ["binary", "list", "list_of_dicts", "text", "multi", "structured"]:
            for module, metrics in sorted(self.metrics.items()):
                if isinstance(metrics, dict) and "error" not in metrics:
                    cfg = MODULE_TYPES.get(module, {})
                    if cfg.get("type") != module_type:
                        continue

                    name = cfg.get("name", module.upper())
                    mtype = cfg.get("type", "unknown")

                    if mtype == "binary":
                        metric_name = "Accuracy"
                        metric_value = metrics.get("accuracy", 0)
                    elif mtype in ["list", "list_of_dicts"]:
                        metric_name = "Avg Precision"
                        metric_value = metrics.get("avg_precision", 0)
                    elif mtype == "text":
                        metric_name = "Fuzzy Accuracy"
                        metric_value = metrics.get("fuzzy_accuracy", metrics.get("accuracy", 0))
                    else:
                        metric_name = "Accuracy"
                        metric_value = metrics.get("accuracy", 0)

                    errors = self.errors.get(module, "-")
                    report.append(f"| {module.upper()} | {mtype} | {metric_name} | {metric_value:.1%} | {errors} |")

        # Binary Classifier Details
        report.append("\n## Binary Classifier Details\n")
        for module in sorted(self.metrics.keys()):
            cfg = MODULE_TYPES.get(module, {})
            if cfg.get("type") != "binary":
                continue
            metrics = self.metrics[module]
            if "error" in metrics:
                continue

            name = cfg.get("name", module.upper())
            report.append(f"\n### {module.upper()} - {name}\n")

            report.append("| Metric | Value |")
            report.append("|--------|-------|")
            report.append(f"| Accuracy | {metrics.get('accuracy', 0):.1%} |")
            report.append(f"| Precision | {metrics.get('precision', 0):.1%} |")
            report.append(f"| Recall | {metrics.get('recall', 0):.1%} |")
            report.append(f"| F1 Score | {metrics.get('f1', 0):.1%} |")
            report.append(f"| False Positives | {metrics.get('false_positives', 0)} |")
            report.append(f"| False Negatives | {metrics.get('false_negatives', 0)} |")
            report.append(f"| Total Samples | {metrics.get('total', 0)} |")

        # List Extractor Details
        list_modules = [m for m in self.metrics if MODULE_TYPES.get(m, {}).get("type") == "list"]
        if list_modules:
            report.append("\n## List Extractor Details\n")
            for module in sorted(list_modules):
                cfg = MODULE_TYPES.get(module, {})
                metrics = self.metrics[module]
                if "error" in metrics:
                    continue

                name = cfg.get("name", module.upper())
                report.append(f"\n### {module.upper()} - {name}\n")

                report.append("| Metric | Value |")
                report.append("|--------|-------|")
                report.append(f"| Avg Precision | {metrics.get('avg_precision', 0):.1%} |")
                report.append(f"| Avg Recall | {metrics.get('avg_recall', 0):.1%} |")
                report.append(f"| Avg F1 | {metrics.get('avg_f1', 0):.1%} |")
                report.append(f"| Exact Match Rate | {metrics.get('exact_match_rate', 0):.1%} |")
                report.append(f"| Total Missing Items | {metrics.get('total_missing', 0)} |")
                report.append(f"| Total Extra Items | {metrics.get('total_extra', 0)} |")

        # Path A vs Path B Comparison
        if self.comparisons:
            report.append("\n## Path A vs Path B Comparison\n")
            report.append("| Task | Path A | Path B | Winner | Diff |")
            report.append("|------|--------|--------|--------|------|")
            for task_name, comp in self.comparisons.items():
                report.append(f"| {task_name} | {comp['accuracy_a']:.1%} | {comp['accuracy_b']:.1%} | {comp['winner']} | {comp['difference']:.1%} |")

            report.append("\n### Analysis\n")
            for task_name, comp in self.comparisons.items():
                if comp["winner"] == "A":
                    report.append(f"- **{task_name}:** Path A ({comp['path_a']}) outperforms Path B by {comp['difference']:.1%}")
                elif comp["winner"] == "B":
                    report.append(f"- **{task_name}:** Path B ({comp['path_b']}) outperforms Path A by {comp['difference']:.1%}")
                else:
                    report.append(f"- **{task_name}:** Both paths perform equally")

        # Error Summary
        if self.errors:
            report.append("\n## Error Summary\n")
            total_errors = sum(e for e in self.errors.values() if isinstance(e, int))
            report.append(f"**Total Errors Across All Modules:** {total_errors}\n")

            # Top error modules
            error_list = [(m, e) for m, e in self.errors.items() if isinstance(e, int) and e > 0]
            error_list.sort(key=lambda x: -x[1])

            if error_list:
                report.append("### Modules by Error Count\n")
                report.append("| Module | Errors | Error Rate |")
                report.append("|--------|--------|------------|")
                for module, error_count in error_list[:10]:
                    total = self.metrics.get(module, {}).get("total", 1)
                    error_rate = error_count / total if total > 0 else 0
                    report.append(f"| {module.upper()} | {error_count} | {error_rate:.1%} |")

        # Recommendations
        report.append("\n## Recommendations\n")

        # Find underperforming modules
        underperforming = []
        for module, metrics in self.metrics.items():
            if "error" in metrics:
                continue
            mtype = MODULE_TYPES.get(module, {}).get("type")
            if mtype == "binary":
                if metrics.get("accuracy", 1) < 0.85:
                    underperforming.append((module, metrics.get("accuracy", 0)))
            elif mtype == "list":
                if metrics.get("avg_precision", 1) < 0.7:
                    underperforming.append((module, metrics.get("avg_precision", 0)))

        if underperforming:
            report.append("\n### Priority Improvements\n")
            for module, score in sorted(underperforming, key=lambda x: x[1]):
                report.append(f"- **{module.upper()}** ({score:.1%}) - Review prompt and examples")
        else:
            report.append("\n### All modules meeting baseline thresholds.\n")

        # Path recommendations
        if self.comparisons:
            report.append("\n### Path Selection\n")
            for task_name, comp in self.comparisons.items():
                if comp["difference"] > 0.05:
                    winner = "Path A" if comp["winner"] == "A" else "Path B"
                    report.append(f"- **{task_name}:** Recommend {winner} (>{comp['difference']:.0%} improvement)")

        return "\n".join(report)

    def save_report(self, filename: str = "baseline_report.md"):
        """Save report to file."""
        report = self.generate_report()
        output_file = self.output_path / filename
        with open(output_file, "w") as f:
            f.write(report)
        return output_file

    def save_metrics_json(self, filename: str = "baseline_metrics.json"):
        """Save metrics to JSON for programmatic access."""
        data = {
            "timestamp": datetime.now().isoformat(),
            "batch_dir": str(self.batch_path),
            "metrics": self.metrics,
            "errors": self.errors,
            "comparisons": self.comparisons
        }
        output_file = self.output_path / filename
        with open(output_file, "w") as f:
            json.dump(data, f, indent=2, default=str)
        return output_file


def main():
    parser = argparse.ArgumentParser(description="Generate baseline evaluation report")
    parser.add_argument("--batch-dir", "-b", required=True, help="Batch results directory")
    parser.add_argument("--output-dir", "-o", help="Output directory for reports")
    parser.add_argument("--format", "-f", choices=["md", "json", "both"], default="both",
                        help="Output format")

    args = parser.parse_args()

    generator = BaselineReportGenerator(args.batch_dir, args.output_dir)

    print(f"{'='*60}")
    print("BASELINE REPORT GENERATOR")
    print(f"{'='*60}")
    print(f"Batch dir: {args.batch_dir}")
    print(f"Output dir: {generator.output_path}")

    # Run analysis
    print("\n[1/3] Analyzing modules...")
    generator.analyze_all_modules()

    print("\n[2/3] Comparing paths...")
    generator.compare_paths()

    print("\n[3/3] Generating report...")

    if args.format in ["md", "both"]:
        md_file = generator.save_report()
        print(f"\nMarkdown report: {md_file}")

    if args.format in ["json", "both"]:
        json_file = generator.save_metrics_json()
        print(f"JSON metrics: {json_file}")

    # Print summary to console
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")

    for module, metrics in sorted(generator.metrics.items()):
        if "error" in metrics:
            print(f"  {module.upper()}: ERROR - {metrics['error']}")
        else:
            mtype = MODULE_TYPES.get(module, {}).get("type", "unknown")
            if mtype == "binary":
                print(f"  {module.upper()}: {metrics.get('accuracy', 0):.1%} accuracy")
            else:
                print(f"  {module.upper()}: {metrics.get('avg_precision', 0):.1%} precision")


if __name__ == "__main__":
    main()
