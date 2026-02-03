#!/usr/bin/env python3
"""
Rule-Based Evaluation - Compare expected vs actual results without LLM judge.

Evaluates accuracy by comparing model outputs to ground truth expected values.
No API calls required.

Usage:
    python evaluation/run_rule_based_evaluation.py
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import random

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATASETS_DIR = PROJECT_ROOT / "datasets"
RESULTS_DIR = PROJECT_ROOT / "batch_requests" / "20260112_2127" / "results"
OUTPUT_DIR = SCRIPT_DIR / "evaluation_reports"

# 10 ASINs with full pipeline coverage
FULL_COVERAGE_ASINS = [
    "B0F42MT8JX",  # Ice Maker
    "B000H3I2JG",  # Revlon Eyeliner
    "B09LCKZBTW",  # Serving Tray
    "B08J8GZXKZ",  # Oven Mitt
    "B0CJ4WZXQF",  # Sink Caddy
    "B077YYP739",  # Transformers Toy
    "B0DSHWLXG6",  # Phone Holder
    "B0BZYCJK89",  # Water Bottle
    "B0BQPGJ9LQ",  # JBL Earbuds
    "B0D6YNWLTS",  # Puffer Jacket
]

ASIN_NAMES = {
    "B0F42MT8JX": "Ice Maker",
    "B000H3I2JG": "Revlon Eyeliner",
    "B09LCKZBTW": "Serving Tray",
    "B08J8GZXKZ": "Oven Mitt",
    "B0CJ4WZXQF": "Sink Caddy",
    "B077YYP739": "Transformers Toy",
    "B0DSHWLXG6": "Phone Holder",
    "B0BZYCJK89": "Water Bottle",
    "B0BQPGJ9LQ": "JBL Earbuds",
    "B0D6YNWLTS": "Puffer Jacket",
}

# Module configurations
MODULE_CONFIG = {
    "m02": {
        "dataset": "m02_classify_own_brand_keywords.jsonl",
        "results": "m02_results.jsonl",
        "expected_field": "branding_scope_1",
        "output_field": "branding_scope_1",
        "category": "OB",
    },
    "m04": {
        "dataset": "m04_classify_competitor_brand_keywords.jsonl",
        "results": "m04_results.jsonl",
        "expected_field": "branding_scope_2",
        "output_field": "branding_scope_2",
        "category": "CB",
    },
    "m05": {
        "dataset": "m05_classify_nonbranded_keywords.jsonl",
        "results": "m05_results.jsonl",
        "expected_field": "branding_scope_3",
        "output_field": "branding_scope_3",
        "category": "NB",
    },
    "m13": {
        "dataset": "m13_check_product_type_v1.1.jsonl",
        "results": "m13_results.jsonl",
        "expected_field": "same_type",
        "output_field": "same_product_type",  # Model outputs same_product_type
        "category": "same_type",
    },
    "m14": {
        "dataset": "m14_check_primary_use_same_type_v1.1.jsonl",
        "results": "m14_results.jsonl",
        "expected_field": "relevancy",
        "output_field": "classification",  # Model outputs classification (R/N)
        "category": "R",
    },
    "m15": {
        "dataset": "m15_check_substitute_v1.1.jsonl",
        "results": "m15_results.jsonl",
        "expected_field": "relevancy",
        "output_field": "classification",  # Model outputs classification (S/Null)
        "category": "S",
    },
    "m16": {
        "dataset": "m16_check_complementary_v1.1.jsonl",
        "results": "m16_results.jsonl",
        "expected_field": "relevancy",
        "output_field": "classification",  # Model outputs classification (C/N)
        "category": "C/N",
    },
}


def load_jsonl(filepath: Path) -> list[dict]:
    """Load JSONL file."""
    if not filepath.exists():
        return []
    records = []
    with open(filepath) as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records


def get_asin_from_record(record: dict) -> str:
    """Extract ASIN from record."""
    if 'metadata' in record and 'asin' in record['metadata']:
        return record['metadata']['asin']
    if 'id' in record:
        record_id = record['id']
        if '_' in record_id:
            parts = record_id.split('_')
            for part in parts[1:]:
                if part.startswith('B0') and len(part) >= 10:
                    return part[:10]
                if '__' in part:
                    subpart = part.split('__')[0]
                    if subpart.startswith('B'):
                        return subpart
        if record_id.startswith('B'):
            return record_id
    return None


def get_keyword_from_record(record: dict) -> str:
    """Extract keyword from record."""
    if 'input' in record and 'keyword' in record.get('input', {}):
        return record['input']['keyword']
    if 'metadata' in record and 'keyword' in record.get('metadata', {}):
        return record['metadata']['keyword']
    return None


def load_results_indexed(results_file: Path) -> dict:
    """Load results indexed by record index."""
    if not results_file.exists():
        return {}

    records = load_jsonl(results_file)
    indexed = {}
    for r in records:
        custom_id = r.get('custom_id', '')
        if '_' in custom_id:
            idx = int(custom_id.split('_')[1])
            content = r.get('response', {}).get('body', {}).get('choices', [{}])[0].get('message', {}).get('content', '{}')
            try:
                output = json.loads(content)
            except json.JSONDecodeError:
                output = {'error': 'Failed to parse'}
            indexed[idx] = output
    return indexed


def normalize_value(val):
    """Normalize values for comparison."""
    if val is None:
        return None
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        val = val.strip().lower()
        if val in ('null', 'none', ''):
            return None
        if val == 'true':
            return True
        if val == 'false':
            return False
        return val
    return val


def evaluate_module(module: str, max_per_asin: int = 10) -> dict:
    """Evaluate a single module's results against expected values."""

    config = MODULE_CONFIG[module]
    dataset_file = DATASETS_DIR / config['dataset']
    results_file = RESULTS_DIR / config['results']

    # Load data
    dataset = load_jsonl(dataset_file)
    results = load_results_indexed(results_file)

    # Track evaluations by ASIN
    evals_by_asin = defaultdict(list)

    for idx, record in enumerate(dataset):
        asin = get_asin_from_record(record)
        if asin not in FULL_COVERAGE_ASINS:
            continue

        # Get expected and actual values
        expected_val = record.get('expected', {}).get(config['expected_field'])

        result = results.get(idx, {})
        actual_val = result.get(config['output_field'])

        # Normalize for comparison
        expected_norm = normalize_value(expected_val)
        actual_norm = normalize_value(actual_val)

        # Determine match
        match = expected_norm == actual_norm

        keyword = get_keyword_from_record(record)

        evals_by_asin[asin].append({
            'keyword': keyword,
            'expected': expected_val,
            'actual': actual_val,
            'match': match,
            'idx': idx,
        })

    # Sample up to max_per_asin per ASIN
    sampled = {}
    for asin, evals in evals_by_asin.items():
        if len(evals) > max_per_asin:
            sampled[asin] = random.sample(evals, max_per_asin)
        else:
            sampled[asin] = evals

    return {
        'module': module,
        'category': config['category'],
        'total_records': len(dataset),
        'results_loaded': len(results),
        'evaluations_by_asin': sampled,
    }


def run_evaluation(max_per_asin: int = 10):
    """Run full rule-based evaluation."""

    print("=" * 80)
    print("RULE-BASED EVALUATION - Expected vs Actual Comparison")
    print("=" * 80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Max keywords per ASIN per module: {max_per_asin}")

    # Evaluate each module
    all_results = {}
    summary = defaultdict(lambda: {'correct': 0, 'incorrect': 0, 'total': 0})
    asin_summary = defaultdict(lambda: {'correct': 0, 'incorrect': 0, 'total': 0})

    for module in MODULE_CONFIG.keys():
        print(f"\n{'='*60}")
        print(f"Module: {module.upper()}")
        print(f"{'='*60}")

        result = evaluate_module(module, max_per_asin)
        all_results[module] = result

        print(f"Dataset records: {result['total_records']}")
        print(f"Results loaded: {result['results_loaded']}")

        module_correct = 0
        module_incorrect = 0

        for asin in FULL_COVERAGE_ASINS:
            evals = result['evaluations_by_asin'].get(asin, [])
            if not evals:
                continue

            correct = sum(1 for e in evals if e['match'])
            incorrect = len(evals) - correct

            module_correct += correct
            module_incorrect += incorrect

            asin_summary[asin]['correct'] += correct
            asin_summary[asin]['incorrect'] += incorrect
            asin_summary[asin]['total'] += len(evals)

            accuracy = (correct / len(evals) * 100) if evals else 0
            print(f"\n  {asin} ({ASIN_NAMES[asin]}): {correct}/{len(evals)} correct ({accuracy:.1f}%)")

            # Show sample mismatches
            mismatches = [e for e in evals if not e['match']][:3]
            for m in mismatches:
                print(f"    ✗ \"{m['keyword'][:30]}\" expected={m['expected']} got={m['actual']}")

        summary[module]['correct'] = module_correct
        summary[module]['incorrect'] = module_incorrect
        summary[module]['total'] = module_correct + module_incorrect

    # Print summary
    print("\n" + "=" * 80)
    print("EVALUATION SUMMARY")
    print("=" * 80)

    print("\nBy Module:")
    print(f"{'Module':<10} | {'Correct':>8} | {'Incorrect':>10} | {'Total':>8} | {'Accuracy':>10}")
    print("-" * 60)

    total_correct = 0
    total_incorrect = 0

    for module in MODULE_CONFIG.keys():
        s = summary[module]
        total_correct += s['correct']
        total_incorrect += s['incorrect']
        accuracy = (s['correct'] / s['total'] * 100) if s['total'] > 0 else 0
        print(f"{module.upper():<10} | {s['correct']:>8} | {s['incorrect']:>10} | {s['total']:>8} | {accuracy:>9.1f}%")

    total = total_correct + total_incorrect
    overall_accuracy = (total_correct / total * 100) if total > 0 else 0
    print("-" * 60)
    print(f"{'TOTAL':<10} | {total_correct:>8} | {total_incorrect:>10} | {total:>8} | {overall_accuracy:>9.1f}%")

    print("\nBy ASIN:")
    print(f"{'ASIN':<12} | {'Product':<16} | {'Correct':>8} | {'Incorrect':>10} | {'Accuracy':>10}")
    print("-" * 70)

    for asin in FULL_COVERAGE_ASINS:
        s = asin_summary[asin]
        accuracy = (s['correct'] / s['total'] * 100) if s['total'] > 0 else 0
        print(f"{asin} | {ASIN_NAMES[asin][:16]:<16} | {s['correct']:>8} | {s['incorrect']:>10} | {accuracy:>9.1f}%")

    # Save detailed results
    OUTPUT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = OUTPUT_DIR / f"rule_based_eval_{timestamp}.json"

    # Convert defaultdicts for JSON
    with open(output_file, 'w') as f:
        json.dump({
            'timestamp': timestamp,
            'summary_by_module': dict(summary),
            'summary_by_asin': dict(asin_summary),
            'total': {'correct': total_correct, 'incorrect': total_incorrect, 'total': total, 'accuracy': overall_accuracy},
            'details': {m: {
                'module': r['module'],
                'category': r['category'],
                'total_records': r['total_records'],
                'results_loaded': r['results_loaded'],
                'evaluations_by_asin': r['evaluations_by_asin'],
            } for m, r in all_results.items()},
        }, f, indent=2)

    print(f"\nDetailed results saved to: {output_file}")
    print("=" * 80)

    return all_results


if __name__ == "__main__":
    run_evaluation(max_per_asin=10)
