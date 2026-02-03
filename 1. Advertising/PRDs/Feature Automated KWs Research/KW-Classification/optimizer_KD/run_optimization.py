#!/usr/bin/env python3
"""
Run Prompt Optimization Agent
=============================

This script runs the iterative prompt optimizer on a specified module.

Usage:
    # Basic usage with defaults
    python optimizer/run_optimization.py

    # Specify module and paths
    python optimizer/run_optimization.py --module m02 --prompt prompts/modules/m02_own_brand.md

    # With options
    python optimizer/run_optimization.py --module m02 --max-iterations 5 --target-accuracy 0.9 --max-tests 20
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / ".env")

from optimizer.prompt_optimizer import PromptOptimizer


def find_prompt_file(module: str) -> str:
    """Find the prompt file for a module."""
    prompts_dir = project_root / "prompts"

    # Check different possible locations
    candidates = [
        prompts_dir / "modules" / f"{module}.md",
        prompts_dir / f"{module}.md",
    ]

    # Also check with glob patterns
    for pattern_dir in [prompts_dir / "modules", prompts_dir]:
        if pattern_dir.exists():
            matches = list(pattern_dir.glob(f"{module}*.md"))
            if matches:
                return str(matches[0])

    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    raise FileNotFoundError(f"No prompt file found for module {module}")


def find_dataset_file(module: str) -> str:
    """Find the dataset file for a module."""
    datasets_dir = project_root / "datasets"

    # Check different possible locations
    candidates = [
        datasets_dir / f"{module}_dataset.jsonl",
        datasets_dir / f"{module}.jsonl",
    ]

    # Also check with glob patterns
    if datasets_dir.exists():
        matches = list(datasets_dir.glob(f"{module}*.jsonl"))
        if matches:
            return str(matches[0])

    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    raise FileNotFoundError(f"No dataset file found for module {module}")


def list_available_files():
    """List available prompts and datasets."""
    print("\nAvailable prompts:")
    prompts_dir = project_root / "prompts"
    if prompts_dir.exists():
        for p in prompts_dir.rglob("*.md"):
            print(f"  {p.relative_to(project_root)}")

    print("\nAvailable datasets:")
    datasets_dir = project_root / "datasets"
    if datasets_dir.exists():
        for d in datasets_dir.glob("*.jsonl"):
            print(f"  {d.relative_to(project_root)}")


def main():
    parser = argparse.ArgumentParser(
        description="Run prompt optimization agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python optimizer/run_optimization.py --module m02
    python optimizer/run_optimization.py --module m02 --max-iterations 5 --target-accuracy 0.9
    python optimizer/run_optimization.py --prompt path/to/prompt.md --dataset path/to/data.jsonl
        """
    )

    parser.add_argument(
        "--module", "-m",
        type=str,
        default="m02",
        help="Module to optimize (e.g., m02, m04, m05). Default: m02"
    )

    parser.add_argument(
        "--prompt", "-p",
        type=str,
        help="Path to prompt file (auto-detected if not specified)"
    )

    parser.add_argument(
        "--dataset", "-d",
        type=str,
        help="Path to dataset JSONL file (auto-detected if not specified)"
    )

    parser.add_argument(
        "--max-iterations", "-i",
        type=int,
        default=3,
        help="Maximum optimization iterations. Default: 3"
    )

    parser.add_argument(
        "--target-accuracy", "-t",
        type=float,
        default=0.85,
        help="Target accuracy to stop optimization. Default: 0.85"
    )

    parser.add_argument(
        "--max-tests", "-n",
        type=int,
        default=None,
        help="Limit number of test cases. Default: all"
    )

    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o",
        help="Model for classification. Default: gpt-4o"
    )

    parser.add_argument(
        "--optimizer-model",
        type=str,
        default="o3-mini",
        help="Model for prompt optimization. Default: o3-mini"
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output path for results (auto-generated if not specified)"
    )

    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress verbose output"
    )

    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List available prompts and datasets"
    )

    args = parser.parse_args()

    # List files if requested
    if args.list:
        list_available_files()
        return 0

    # Find prompt and dataset files
    try:
        prompt_path = args.prompt or find_prompt_file(args.module)
        dataset_path = args.dataset or find_dataset_file(args.module)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        list_available_files()
        sys.exit(1)

    print(f"\n{'='*60}")
    print("PROMPT OPTIMIZATION AGENT")
    print(f"{'='*60}")
    print(f"Module: {args.module}")
    print(f"Prompt: {prompt_path}")
    print(f"Dataset: {dataset_path}")
    print(f"Max iterations: {args.max_iterations}")
    print(f"Target accuracy: {args.target_accuracy:.0%}")
    print(f"Model: {args.model}")
    print(f"Optimizer: {args.optimizer_model}")
    if args.max_tests:
        print(f"Max tests: {args.max_tests}")
    print(f"{'='*60}\n")

    # Run optimizer
    optimizer = PromptOptimizer(
        module=args.module,
        model=args.model,
        optimizer_model=args.optimizer_model,
        verbose=not args.quiet
    )

    result = optimizer.optimize(
        prompt_path=prompt_path,
        dataset_path=dataset_path,
        max_iterations=args.max_iterations,
        target_accuracy=args.target_accuracy,
        max_tests=args.max_tests
    )

    # Save results
    output_path = optimizer.save_result(result, args.output)

    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Success: {result.success}")
    print(f"Iterations: {result.total_iterations}")
    print(f"Best iteration: {result.best_iteration}")
    print(f"Original accuracy: {result.original_accuracy:.1%}")
    print(f"Best accuracy: {result.best_accuracy:.1%}")
    print(f"Improvement: +{(result.best_accuracy - result.original_accuracy)*100:.1f}%")
    print(f"\nResults saved to: {output_path}")

    # Show per-iteration progress
    print(f"\nIteration Progress:")
    for ir in result.iteration_results:
        status = "+" if ir.accuracy > result.original_accuracy else "="
        print(f"  {ir.iteration}: {ir.accuracy:.1%} {status}")

    # Show top improvements suggested
    if result.iteration_results:
        last_iter = result.iteration_results[-1]
        if last_iter.improvements:
            print(f"\nTop Improvement Suggestions:")
            for imp in last_iter.improvements[:5]:
                print(f"  - [{imp.get('rule_id', 'unknown')}] {imp.get('suggestion', '')[:80]}...")

    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())
