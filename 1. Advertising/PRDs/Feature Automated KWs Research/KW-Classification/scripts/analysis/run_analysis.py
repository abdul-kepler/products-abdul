#!/usr/bin/env python3
"""
Main Error Analysis Runner

Runs all three analysis modes on batch results:
A) Automated metrics and error extraction
B) Pattern detection
C) LLM Judge evaluation (optional, costs $)

Usage:
    # Full analysis on batch results
    python scripts/analysis/run_analysis.py --batch-dir batch_requests/20260112_2127

    # Specific modules only
    python scripts/analysis/run_analysis.py --batch-dir batch_requests/20260112_2127 --modules m02 m04 m05

    # Skip LLM Judge (faster, no cost)
    python scripts/analysis/run_analysis.py --batch-dir batch_requests/20260112_2127 --skip-judge

    # Only run on errors from specific module
    python scripts/analysis/run_analysis.py --errors-file experiment_results/m02_errors.json --module m02
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

try:
    from .error_analyzer import ErrorAnalyzer, MODULE_TYPES
    from .pattern_detector import PatternDetector
    from .llm_judge_analyzer import LLMJudgeAnalyzer
except ImportError:
    from error_analyzer import ErrorAnalyzer, MODULE_TYPES
    from pattern_detector import PatternDetector
    from llm_judge_analyzer import LLMJudgeAnalyzer


def run_full_analysis(batch_dir: str, modules: list[str] = None,
                      skip_judge: bool = False, judge_sample: int = 20,
                      output_dir: str = None):
    """Run complete analysis pipeline."""

    batch_path = Path(batch_dir)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")

    if output_dir is None:
        output_dir = f"experiment_results/analysis_{timestamp}"
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"{'='*60}")
    print(f"ERROR ANALYSIS PIPELINE")
    print(f"{'='*60}")
    print(f"Batch dir: {batch_dir}")
    print(f"Output dir: {output_dir}")
    print(f"Skip LLM Judge: {skip_judge}")

    # Discover modules if not specified
    # Check both root and results/ subdirectory
    if modules is None:
        modules = []
        results_path = batch_path / "results"
        search_path = results_path if results_path.exists() else batch_path
        for f in search_path.glob("*_results.jsonl"):
            module = f.stem.replace("_results", "")
            if module.lower() in MODULE_TYPES:
                modules.append(module.lower())
        print(f"Discovered modules: {modules}")

    if not modules:
        print("ERROR: No modules found to analyze")
        return

    # ============================================================
    # PHASE A: Automated Metrics & Error Extraction
    # ============================================================
    print(f"\n{'='*60}")
    print("PHASE A: Automated Metrics")
    print(f"{'='*60}")

    analyzer = ErrorAnalyzer(output_dir=str(output_path))
    all_errors = {}

    for module in modules:
        print(f"\n[{module.upper()}]")
        try:
            metrics = analyzer.analyze_batch_results(batch_dir, module)
            print(f"  Accuracy: {metrics.get('accuracy', metrics.get('avg_precision', 0)):.1%}")

            # Export errors to CSV and JSON
            csv_file = analyzer.export_errors_csv(module)
            print(f"  Errors CSV: {csv_file}")

            # Store errors for further analysis
            module_analyzer = analyzer.analyzers.get(module)
            if module_analyzer:
                errors_list = []
                for e in module_analyzer.errors:
                    error_dict = {
                        "record_id": e.record_id,
                        "module": module
                    }
                    if hasattr(e, 'keyword'):
                        error_dict["keyword"] = e.keyword
                        error_dict["expected"] = e.expected
                        error_dict["actual"] = e.actual
                        error_dict["error_type"] = e.error_type
                        error_dict["confidence"] = e.confidence
                        error_dict["reasoning"] = e.reasoning
                    elif hasattr(e, 'missing_items'):
                        error_dict["input"] = e.input_text
                        error_dict["missing_items"] = e.missing_items
                        error_dict["extra_items"] = e.extra_items
                    all_errors[module] = errors_list
                    errors_list.append(error_dict)

                # Save errors JSON
                errors_json = output_path / f"{module}_errors.json"
                with open(errors_json, "w") as f:
                    json.dump(errors_list, f, indent=2)

        except Exception as ex:
            print(f"  ERROR: {ex}")

    # Generate summary report
    report = analyzer.generate_report(modules)
    print(f"\nSummary report saved")

    # ============================================================
    # PHASE B: Pattern Detection
    # ============================================================
    print(f"\n{'='*60}")
    print("PHASE B: Pattern Detection")
    print(f"{'='*60}")

    for module in modules:
        errors_file = output_path / f"{module}_errors.json"
        if not errors_file.exists():
            continue

        with open(errors_file) as f:
            errors = json.load(f)

        if len(errors) < 5:
            print(f"\n[{module.upper()}] Skipped - only {len(errors)} errors")
            continue

        print(f"\n[{module.upper()}] Analyzing {len(errors)} errors...")

        detector = PatternDetector()
        detector.load_errors(errors)
        patterns = detector.detect_all_patterns()

        print(f"  Detected {len(patterns)} patterns:")
        for p in patterns[:3]:
            print(f"    - [{p.severity}] {p.name}: {p.affected_count} errors")

        # Save pattern report
        pattern_report = output_path / f"{module}_patterns.md"
        with open(pattern_report, "w") as f:
            f.write(detector.generate_report())

        pattern_json = output_path / f"{module}_patterns.json"
        detector.export_patterns(str(pattern_json))

    # ============================================================
    # PHASE C: LLM Judge (Optional)
    # ============================================================
    if not skip_judge:
        print(f"\n{'='*60}")
        print("PHASE C: LLM Judge Evaluation")
        print(f"{'='*60}")
        print(f"Sample size per module: {judge_sample}")

        for module in modules:
            errors_file = output_path / f"{module}_errors.json"
            if not errors_file.exists():
                continue

            with open(errors_file) as f:
                errors = json.load(f)

            if len(errors) == 0:
                continue

            # Only judge binary classifier errors for now
            if MODULE_TYPES.get(module, {}).get("type") != "binary":
                print(f"\n[{module.upper()}] Skipped - not binary classifier")
                continue

            print(f"\n[{module.upper()}] Judging {min(len(errors), judge_sample)} errors...")

            judge = LLMJudgeAnalyzer()
            judge.judge_errors_batch(module, errors, max_errors=judge_sample)

            summary = judge.get_summary()
            print(f"  Categories: {summary['categories']}")
            print(f"  Recommendations: {summary['recommendations']}")

            # Save judge results
            judge_file = output_path / f"{module}_judge_results.json"
            judge.export_results(str(judge_file))

    # ============================================================
    # Final Summary
    # ============================================================
    print(f"\n{'='*60}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*60}")
    print(f"Output directory: {output_path}")
    print(f"\nGenerated files:")
    for f in sorted(output_path.glob("*")):
        print(f"  - {f.name}")


def main():
    parser = argparse.ArgumentParser(description="Run error analysis pipeline")
    parser.add_argument("--batch-dir", "-b", help="Directory with batch results")
    parser.add_argument("--errors-file", "-e", help="Single errors JSON file to analyze")
    parser.add_argument("--modules", "-m", nargs="+", help="Modules to analyze")
    parser.add_argument("--module", help="Single module (use with --errors-file)")
    parser.add_argument("--skip-judge", action="store_true", help="Skip LLM Judge phase")
    parser.add_argument("--judge-sample", type=int, default=20, help="Sample size for LLM Judge")
    parser.add_argument("--output-dir", "-o", help="Output directory")

    args = parser.parse_args()

    if args.batch_dir:
        run_full_analysis(
            batch_dir=args.batch_dir,
            modules=args.modules,
            skip_judge=args.skip_judge,
            judge_sample=args.judge_sample,
            output_dir=args.output_dir
        )
    elif args.errors_file and args.module:
        # Single file analysis
        with open(args.errors_file) as f:
            errors = json.load(f)

        print(f"Analyzing {len(errors)} errors from {args.errors_file}")

        # Pattern detection
        detector = PatternDetector()
        detector.load_errors(errors)
        patterns = detector.detect_all_patterns()
        print(detector.generate_report())

        # LLM Judge if not skipped
        if not args.skip_judge:
            print("\nRunning LLM Judge...")
            judge = LLMJudgeAnalyzer()
            judge.judge_errors_batch(args.module, errors, args.judge_sample)
            print(f"\nJudge Summary: {judge.get_summary()}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
