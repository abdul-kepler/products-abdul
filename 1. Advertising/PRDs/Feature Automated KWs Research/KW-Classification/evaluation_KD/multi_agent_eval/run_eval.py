#!/usr/bin/env python3
"""
Multi-Agent Evaluation CLI

Adversarial debate + Likert scoring (0-5) for LLM output evaluation.

Usage:
    # Full evaluation (3 runs with aggregation)
    python3 evaluation_KD/multi_agent_eval/run_eval.py --module m01 --limit 10

    # Single run (development/cost saving)
    python3 evaluation_KD/multi_agent_eval/run_eval.py --module m01 --single-run --limit 5

    # Compare with binary evaluation
    python3 evaluation_KD/multi_agent_eval/run_eval.py --module m01 --compare-binary

    # Verbose output
    python3 evaluation_KD/multi_agent_eval/run_eval.py --module m11 --limit 5 --verbose
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
SCRIPT_DIR = Path(__file__).parent
EVALUATION_KD_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = EVALUATION_KD_DIR.parent
sys.path.insert(0, str(EVALUATION_KD_DIR))

from dotenv import load_dotenv

from multi_agent_eval.pipeline.orchestrator import Orchestrator
from multi_agent_eval.pipeline.aggregator import Aggregator, SingleRunEvaluator


def make_json_safe(obj, seen=None):
    """
    Recursively copy an object making it JSON-serializable.
    Handles circular references by tracking seen objects.
    """
    if seen is None:
        seen = set()

    # Handle None
    if obj is None:
        return None

    # Handle primitive types
    if isinstance(obj, (bool, int, float, str)):
        return obj

    # Check for circular references
    obj_id = id(obj)
    if obj_id in seen:
        return "<circular reference>"
    seen.add(obj_id)

    try:
        # Handle dict
        if isinstance(obj, dict):
            return {str(k): make_json_safe(v, seen.copy()) for k, v in obj.items()}

        # Handle list/tuple
        if isinstance(obj, (list, tuple)):
            return [make_json_safe(item, seen.copy()) for item in obj]

        # Handle other types - convert to string
        return str(obj)
    except Exception:
        return f"<unserializable: {type(obj).__name__}>"


# Data paths
EXPERIMENT_DATA_DIR = PROJECT_ROOT / "experiment_results"
OUTPUT_DIR = SCRIPT_DIR / "results"
BINARY_RESULTS_DIR = EVALUATION_KD_DIR / "evaluation_experimentV5" / "judge_results"

# Module to CSV mapping (same as evaluation_experimentV5)
MODULE_CSV_MAP = {
    'm01': {
        'folder': 'M01_ExtractOwnBrandEntities',
        'file': 'M01_ExtractOwnBrandEntities_v1_150126_1.csv',
        'rubrics': 'M01',
    },
    'm01_v3': {
        'folder': 'M01_ExtractOwnBrandEntities',
        'file': 'M01_V2_ExtractOwnBrandEntities_v3_190126_1.csv',
        'rubrics': 'M01',
    },
    'm01a': {
        'folder': 'M01A_ExtractOwnBrandVariations',
        'file': 'M01A_ExtractOwnBrandVariations_v1_150126_1.csv',
        'rubrics': 'M01a',
    },
    'm01b': {
        'folder': 'M01B_ExtractBrandRelatedTerms',
        'file': 'M01B_ExtractBrandRelatedTerms_v1_150126_1.csv',
        'rubrics': 'M01b',
    },
    'm02': {
        'folder': 'M02_ClassifyOwnBrandKeywords',
        'file': 'M02_ClassifyOwnBrandKeywords_v1_150126_1.csv',
        'rubrics': 'M02',
    },
    'm04': {
        'folder': 'M04_ClassifyCompetitorBrandKeywords',
        'file': 'M04_ClassifyCompetitorBrandKeywords_v1_150126_1.csv',
        'rubrics': 'M04',
    },
    'm05': {
        'folder': 'M05_ClassifyNonBrandedKeywords',
        'file': 'M05_ClassifyNonBrandedKeywords_v1_150126_1.csv',
        'rubrics': 'M05',
    },
    'm06_gd': {
        'folder': 'M06_GenerateProductTypeTaxonomy',
        'file': 'M06_GenerateProductTypeTaxonomy_gd1_v1_150126_1.csv',
        'rubrics': 'M06',
    },
    'm07_gd': {
        'folder': 'M07_ExtractProductAttributes',
        'file': 'M07_ExtractProductAttributes_gd1_v1_150126_1.csv',
        'rubrics': 'M07',
    },
    'm08': {
        'folder': 'M08_AssignAttributeRanks',
        'file': 'M08_AssignAttributeRanks_v1_150126_1.csv',
        'rubrics': 'M08',
    },
    'm09': {
        'folder': 'M09_IdentifyPrimaryIntendedUse',
        'file': 'M09_IdentifyPrimaryIntendedUse_v1_150126_1.csv',
        'rubrics': 'M09',
    },
    'm10': {
        'folder': 'M10_ValidatePrimaryIntendedUse',
        'file': 'M10_ValidatePrimaryIntendedUse_v1_150126_1.csv',
        'rubrics': 'M10',
    },
    'm11': {
        'folder': 'M11_IdentifyHardConstraints',
        'file': 'M11_IdentifyHardConstraints_v1_150126_1.csv',
        'rubrics': 'M11',
    },
    'm12': {
        'folder': 'M12_HardConstraintViolationCheck',
        'file': 'M12_HardConstraintViolationCheck_v1_150126_1.csv',
        'rubrics': 'M12',
    },
    'm13': {
        'folder': 'M13_ProductTypeCheck',
        'file': 'M13_ProductTypeCheck_v1_150126_1.csv',
        'rubrics': 'M13',
    },
    'm14': {
        'folder': 'M14_PrimaryUseCheckSameType',
        'file': 'M14_PrimaryUseCheckSameType_v1_150126_1.csv',
        'rubrics': 'M14',
    },
    'm15': {
        'folder': 'M15_SubstituteCheck',
        'file': 'M15_SubstituteCheck_v1_150126_1.csv',
        'rubrics': 'M15',
    },
    'm16': {
        'folder': 'M16_ComplementaryCheck',
        'file': 'M16_ComplementaryCheck_v1_150126_1.csv',
        'rubrics': 'M16',
    },
}


def load_env():
    """Load environment variables."""
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        load_dotenv(env_file)


def load_csv_data(module: str) -> list[dict]:
    """Load data from experiment CSV file."""
    config = MODULE_CSV_MAP.get(module)
    if not config:
        print(f"ERROR: Unknown module {module}")
        return []

    csv_path = EXPERIMENT_DATA_DIR / config['folder'] / config['file']
    if not csv_path.exists():
        print(f"ERROR: CSV not found: {csv_path}")
        return []

    print(f"Loading data from {csv_path.name}")

    records = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            record = {
                'raw': row,
                'asin': row.get('ASIN', ''),
                'brand': row.get('Brand', ''),
            }

            # Parse JSON fields
            for field in ['input', 'output', 'expected']:
                if field in row and row[field]:
                    try:
                        record[field] = json.loads(row[field])
                    except json.JSONDecodeError:
                        record[field] = row[field]

            records.append(record)

    print(f"Loaded {len(records)} records")
    return records


def run_evaluation(
    module: str,
    limit: int = 10,
    single_run: bool = False,
    verbose: bool = False,
    model: Optional[str] = None,
) -> dict:
    """Run multi-agent evaluation on module data."""
    load_env()

    config = MODULE_CSV_MAP.get(module)
    if not config:
        print(f"ERROR: Unknown module {module}")
        return {}

    module_id = config['rubrics']

    print(f"\n{'='*60}")
    print(f"MULTI-AGENT EVALUATION")
    print(f"{'='*60}")
    print(f"Module: {module.upper()} ({module_id})")
    print(f"Mode: {'Single Run' if single_run else 'Aggregated (3 runs)'}")
    print(f"Limit: {limit} samples")
    print(f"{'='*60}\n")

    # Load data
    data = load_csv_data(module)
    if not data:
        return {}
    data = data[:limit]

    # Initialize evaluator
    if single_run:
        evaluator = SingleRunEvaluator(model=model, verbose=verbose)
    else:
        evaluator = Aggregator(num_runs=3, verbose=verbose, model=model)

    # Run evaluations
    all_results = []
    summary_stats = {
        'total': 0,
        'scores': {'accuracy': [], 'relevance': [], 'completeness': [], 'clarity': [], 'reasoning': []},
        'overalls': [],
        'confidence': {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'NONE': 0},
    }

    for idx, record in enumerate(data):
        asin = record.get('asin', f'sample_{idx}')
        print(f"\n--- Sample {idx + 1}/{len(data)}: {asin} ---")

        input_data = record.get('input', {})
        output_data = record.get('output', {})
        expected_data = record.get('expected', {})

        try:
            result = evaluator.evaluate(
                module_id=module_id,
                input_data=input_data,
                output_data=output_data,
                expected_data=expected_data,
            )

            overall = result.get('overall', 0)
            scores = result.get('scores', {})
            confidence = result.get('confidence', 'NONE') if not single_run else 'N/A'

            print(f"  Overall: {overall}/5 (Confidence: {confidence})")
            print(f"  Scores: {scores}")

            # Track stats
            summary_stats['total'] += 1
            summary_stats['overalls'].append(overall)

            for criterion, score in scores.items():
                if criterion in summary_stats['scores']:
                    summary_stats['scores'][criterion].append(score)

            if not single_run and confidence in summary_stats['confidence']:
                summary_stats['confidence'][confidence] += 1

            all_results.append({
                'sample_id': asin,
                'input_data': input_data,
                'output_data': output_data,
                'expected_data': expected_data,
                'result': result,
            })

        except Exception as e:
            print(f"  ERROR: {str(e)}")
            all_results.append({
                'sample_id': asin,
                'error': str(e),
            })

    # Calculate summary
    if summary_stats['overalls']:
        avg_overall = sum(summary_stats['overalls']) / len(summary_stats['overalls'])
        avg_scores = {
            k: sum(v) / len(v) if v else 0
            for k, v in summary_stats['scores'].items()
        }
    else:
        avg_overall = 0
        avg_scores = {}

    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Samples Evaluated: {summary_stats['total']}")
    print(f"Average Overall Score: {avg_overall:.2f}/5")
    print(f"Average Scores by Criterion:")
    for criterion, avg in avg_scores.items():
        print(f"  - {criterion}: {avg:.2f}")
    if not single_run:
        print(f"Confidence Distribution:")
        for level, count in summary_stats['confidence'].items():
            print(f"  - {level}: {count}")
    print(f"{'='*60}")

    # Save results
    OUTPUT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    mode = 'single' if single_run else 'aggregated'

    output_data = {
        'experiment': 'multi_agent_v1',
        'module': module,
        'module_id': module_id,
        'mode': mode,
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total': summary_stats['total'],
            'avg_overall': avg_overall,
            'avg_scores': avg_scores,
            'confidence': summary_stats['confidence'] if not single_run else None,
        },
        'results': all_results,
    }

    output_file = OUTPUT_DIR / f"{module}_multiagent_{mode}_{timestamp}.json"
    with open(output_file, 'w') as f:
        # Make data JSON-safe to avoid circular reference issues
        safe_data = make_json_safe(output_data)
        json.dump(safe_data, f, indent=2, default=str)

    print(f"\nResults saved to: {output_file}")

    return output_data


def compare_with_binary(module: str, limit: int = 10):
    """Compare multi-agent results with binary evaluation results."""
    print(f"\n{'='*60}")
    print(f"COMPARISON: Multi-Agent vs Binary Evaluation")
    print(f"{'='*60}")
    print(f"Module: {module.upper()}")
    print(f"{'='*60}\n")

    # Find latest binary results
    binary_files = list(BINARY_RESULTS_DIR.glob(f"{module}_judge_*.json"))
    if not binary_files:
        print(f"No binary evaluation results found for {module}")
        return

    latest_binary = max(binary_files, key=lambda p: p.stat().st_mtime)
    print(f"Binary results file: {latest_binary.name}")

    with open(latest_binary) as f:
        binary_data = json.load(f)

    # Run multi-agent evaluation
    multi_data = run_evaluation(module, limit=limit, single_run=True, verbose=False)

    if not multi_data:
        return

    # Compare results
    print(f"\n{'='*60}")
    print("COMPARISON RESULTS")
    print(f"{'='*60}")

    binary_pass_rate = binary_data.get('pass_rate', 0)
    multi_avg = multi_data.get('summary', {}).get('avg_overall', 0)

    # Map Likert to binary
    likert_pass_threshold = 3.0
    multi_pass_count = sum(
        1 for r in multi_data.get('results', [])
        if r.get('result', {}).get('overall', 0) >= likert_pass_threshold
    )
    multi_total = len(multi_data.get('results', []))
    multi_pass_rate = (multi_pass_count / multi_total * 100) if multi_total > 0 else 0

    print(f"\nBinary System:")
    print(f"  Pass Rate: {binary_pass_rate:.1f}%")

    print(f"\nMulti-Agent System:")
    print(f"  Average Likert Score: {multi_avg:.2f}/5")
    print(f"  Pass Rate (>= 3.0): {multi_pass_rate:.1f}%")

    print(f"\nAgreement:")
    diff = abs(binary_pass_rate - multi_pass_rate)
    print(f"  Pass Rate Difference: {diff:.1f}%")

    if diff < 10:
        print(f"  Status: HIGH AGREEMENT")
    elif diff < 20:
        print(f"  Status: MODERATE AGREEMENT")
    else:
        print(f"  Status: LOW AGREEMENT - investigate discrepancies")


def list_modules():
    """List available modules."""
    print("\nAvailable modules:")
    for mod, config in MODULE_CSV_MAP.items():
        csv_path = EXPERIMENT_DATA_DIR / config['folder'] / config['file']
        status = "+" if csv_path.exists() else "-"
        print(f"  {status} {mod}: {config['file']}")


def main():
    parser = argparse.ArgumentParser(
        description="Multi-Agent Evaluation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full evaluation (3 runs)
  python3 run_eval.py --module m11 --limit 10

  # Single run (faster, cheaper)
  python3 run_eval.py --module m01 --single-run --limit 5

  # Compare with binary system
  python3 run_eval.py --module m01 --compare-binary --limit 10

  # Verbose output
  python3 run_eval.py --module m11 --limit 3 --verbose
        """
    )

    parser.add_argument(
        "--module", "-m",
        type=str,
        default="m11",
        help="Module to evaluate (e.g., m01, m11, m16)"
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=10,
        help="Number of samples to evaluate"
    )
    parser.add_argument(
        "--single-run",
        action="store_true",
        help="Single run mode (skip aggregation and meta-judge)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Override model (default: from config)"
    )
    parser.add_argument(
        "--compare-binary",
        action="store_true",
        help="Compare results with binary evaluation"
    )
    parser.add_argument(
        "--list-modules",
        action="store_true",
        help="List available modules"
    )

    args = parser.parse_args()

    if args.list_modules:
        list_modules()
        return

    if args.compare_binary:
        compare_with_binary(args.module, args.limit)
        return

    run_evaluation(
        module=args.module,
        limit=args.limit,
        single_run=args.single_run,
        verbose=args.verbose,
        model=args.model,
    )


if __name__ == "__main__":
    main()
