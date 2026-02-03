#!/usr/bin/env python3
"""
Sampled Evaluation - Run LLM-as-Judge on 10 ASINs with up to 10 keywords per category.

Categories:
- OB: Own Brand (M02)
- CB: Competitor Brand (M04)
- NB: Non-Branded → R/S/C/N (M05 + M13-M16)
- R: Relevant (M14)
- S: Substitute (M15)
- C: Complementary (M16)
- N: Not Relevant (M14/M16)

Usage:
    python evaluation/run_sampled_evaluation.py
"""

import json
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import random

from openai import OpenAI

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATASETS_DIR = PROJECT_ROOT / "datasets"
RESULTS_DIR = PROJECT_ROOT / "batch_requests" / "20260112_2127" / "results"
OUTPUT_DIR = SCRIPT_DIR / "sampled_results"

# Load environment
def load_env():
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip().strip('"').strip("'")

load_env()

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

# Category to module mapping
CATEGORY_MODULES = {
    "OB": {"module": "m02", "field": "branding_scope_1", "value": "OB"},
    "CB": {"module": "m04", "field": "branding_scope_2", "value": "CB"},
    "NB": {"module": "m05", "field": "branding_scope_3", "value": "NB"},
    "R": {"module": "m14", "field": "relevancy", "value": "R"},
    "S": {"module": "m15", "field": "relevancy", "value": "S"},
    "C": {"module": "m16", "field": "relevancy", "value": "C"},
    "N": {"module": "m16", "field": "relevancy", "value": "N"},  # N can come from M14 or M16
}

# Module files
MODULE_FILES = {
    "m02": "m02_classify_own_brand_keywords.jsonl",
    "m04": "m04_classify_competitor_brand_keywords.jsonl",
    "m05": "m05_classify_nonbranded_keywords.jsonl",
    "m13": "m13_check_product_type_v1.1.jsonl",
    "m14": "m14_check_primary_use_same_type_v1.1.jsonl",
    "m15": "m15_check_substitute_v1.1.jsonl",
    "m16": "m16_check_complementary_v1.1.jsonl",
}

# Rubrics for each module
RUBRIC_DATA = {
    "M02": [
        {'id': 'M02_correct_classification', 'criterion': 'Correct Classification',
         'check': 'OB when keyword contains brand from variations_own, null otherwise',
         'fail': '- OB returned but keyword has no match in variations_own or related_terms_own\n- null returned but keyword contains exact term from variations_own',
         'pass': '- OB only when keyword contains term from variations_own/related_terms_own\n- null when no match found'},
    ],
    "M04": [
        {'id': 'M04_correct_classification', 'criterion': 'Correct Classification',
         'check': 'CB when competitor brand in keyword, null otherwise',
         'fail': '- CB returned but no competitor brand in keyword\n- null returned but keyword contains competitor brand',
         'pass': '- CB only when keyword contains term from competitors list\n- null when no match'},
    ],
    "M05": [
        {'id': 'M05_correct_classification', 'criterion': 'Correct Classification',
         'check': 'NB only when keyword has zero brand references',
         'fail': '- NB returned but THE KEYWORD ITSELF contains a brand name\n- null returned for truly generic keyword',
         'pass': '- NB for pure generic keywords\n- null when THE KEYWORD contains any brand'},
    ],
    "M14": [
        {'id': 'M14_correct_classification', 'criterion': 'Correct Classification',
         'check': 'R when keyword product has same primary use as ASIN, N otherwise',
         'fail': '- R returned but uses are clearly different\n- N returned but uses are clearly the same',
         'pass': '- R when primary use matches\n- N when primary use differs'},
    ],
    "M15": [
        {'id': 'M15_correct_classification', 'criterion': 'Correct Classification',
         'check': 'S when keyword product can substitute for ASIN (different type, same use)',
         'fail': '- S returned but products cannot substitute for each other\n- Not S but products are clear substitutes',
         'pass': '- S only when product can replace ASIN for same task\n- Not S when products serve different purposes'},
    ],
    "M16": [
        {'id': 'M16_correct_classification', 'criterion': 'Correct Classification',
         'check': 'C when keyword product is complementary (used together with ASIN)',
         'fail': '- C returned but products are not used together\n- N returned but products are clearly complementary',
         'pass': '- C when products are commonly used together\n- N when no complementary relationship'},
    ],
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


def sample_keywords_by_category(max_per_category: int = 10) -> dict:
    """Sample keywords by category for each ASIN."""

    samples = defaultdict(lambda: defaultdict(list))

    # Load datasets and categorize
    for category, config in CATEGORY_MODULES.items():
        module = config["module"]
        field = config["field"]
        value = config["value"]

        filepath = DATASETS_DIR / MODULE_FILES[module]
        records = load_jsonl(filepath)

        for idx, record in enumerate(records):
            asin = get_asin_from_record(record)
            if asin not in FULL_COVERAGE_ASINS:
                continue

            expected = record.get('expected', {})
            if expected.get(field) == value:
                keyword = get_keyword_from_record(record)
                if keyword:
                    samples[asin][category].append({
                        'keyword': keyword,
                        'record': record,
                        'record_idx': idx,
                        'module': module,
                    })

    # Also check M14 for N classifications
    filepath = DATASETS_DIR / MODULE_FILES["m14"]
    records = load_jsonl(filepath)
    for idx, record in enumerate(records):
        asin = get_asin_from_record(record)
        if asin not in FULL_COVERAGE_ASINS:
            continue
        expected = record.get('expected', {})
        if expected.get('relevancy') == 'N':
            keyword = get_keyword_from_record(record)
            if keyword:
                samples[asin]["N"].append({
                    'keyword': keyword,
                    'record': record,
                    'record_idx': idx,
                    'module': 'm14',
                })

    # Sample up to max_per_category
    sampled = defaultdict(dict)
    for asin in FULL_COVERAGE_ASINS:
        for category in ["OB", "CB", "R", "S", "C", "N"]:
            category_samples = samples[asin][category]
            if len(category_samples) > max_per_category:
                category_samples = random.sample(category_samples, max_per_category)
            sampled[asin][category] = category_samples

    return sampled


def load_results_for_module(module: str) -> dict:
    """Load results indexed by record index."""
    results_file = RESULTS_DIR / f"{module}_results.jsonl"
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


def create_judge_prompt(rubric: dict, input_data: dict, expected: dict, module_output: dict) -> str:
    """Create judge prompt."""
    return f"""You are an expert evaluator for LLM outputs. Evaluate whether the module output passes or fails the rubric.

## Rubric
**Criterion:** {rubric['criterion']}
**Check:** {rubric['check']}

**PASS conditions:**
{rubric['pass']}

**FAIL conditions:**
{rubric['fail']}

## Input Data
```json
{json.dumps(input_data, indent=2)}
```

## Module Output (to evaluate)
```json
{json.dumps(module_output, indent=2)}
```

## Expected Output (ground truth)
```json
{json.dumps(expected, indent=2)}
```

## Instructions
1. Analyze the module output against the rubric
2. Explain your reasoning
3. Provide verdict: PASS or FAIL

Respond in this format:

**Reasoning:**
[Your analysis]

**Verdict:** [PASS or FAIL]
"""


def run_judge(client: OpenAI, rubric: dict, input_data: dict, expected: dict, module_output: dict) -> dict:
    """Run LLM judge."""
    prompt = create_judge_prompt(rubric, input_data, expected, module_output)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert evaluator. Be precise and objective."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=1000,
        )

        content = response.choices[0].message.content
        verdict = "UNKNOWN"
        if "**Verdict:** PASS" in content or "**Verdict:**PASS" in content:
            verdict = "PASS"
        elif "**Verdict:** FAIL" in content or "**Verdict:**FAIL" in content:
            verdict = "FAIL"

        return {
            'verdict': verdict,
            'reasoning': content,
            'tokens': response.usage.total_tokens if response.usage else 0,
        }
    except Exception as e:
        return {'verdict': 'ERROR', 'reasoning': str(e), 'tokens': 0}


def run_sampled_evaluation(max_per_category: int = 10):
    """Run evaluation on sampled keywords."""

    print("=" * 70)
    print("SAMPLED EVALUATION - 10 ASINs x 10 Keywords per Category")
    print("=" * 70)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Sample keywords
    print("\nSampling keywords...")
    samples = sample_keywords_by_category(max_per_category)

    # Print sample summary
    print("\n" + "-" * 70)
    print("SAMPLE SUMMARY")
    print("-" * 70)
    print(f"{'ASIN':<12} | {'Product':<18} | OB | CB |  R |  S |  C |  N | Total")
    print("-" * 70)

    total_by_cat = defaultdict(int)
    for asin in FULL_COVERAGE_ASINS:
        counts = {cat: len(samples[asin][cat]) for cat in ["OB", "CB", "R", "S", "C", "N"]}
        total = sum(counts.values())
        for cat, count in counts.items():
            total_by_cat[cat] += count
        print(f"{asin} | {ASIN_NAMES[asin]:<18} | {counts['OB']:2d} | {counts['CB']:2d} | {counts['R']:2d} | {counts['S']:2d} | {counts['C']:2d} | {counts['N']:2d} | {total:3d}")

    total_all = sum(total_by_cat.values())
    print("-" * 70)
    print(f"{'TOTAL':<12} | {'':<18} | {total_by_cat['OB']:2d} | {total_by_cat['CB']:2d} | {total_by_cat['R']:2d} | {total_by_cat['S']:2d} | {total_by_cat['C']:2d} | {total_by_cat['N']:2d} | {total_all:3d}")

    # Load results for each module
    print("\nLoading module results...")
    module_results = {}
    for module in MODULE_FILES.keys():
        module_results[module] = load_results_for_module(module)
        print(f"  {module}: {len(module_results[module])} results loaded")

    # Initialize OpenAI client
    client = OpenAI()

    # Run evaluations
    print("\n" + "=" * 70)
    print("RUNNING EVALUATIONS")
    print("=" * 70)

    all_results = []
    summary_by_category = defaultdict(lambda: {'pass': 0, 'fail': 0, 'error': 0, 'total': 0})
    summary_by_asin = defaultdict(lambda: {'pass': 0, 'fail': 0, 'error': 0, 'total': 0})

    for asin in FULL_COVERAGE_ASINS:
        print(f"\n--- {asin} ({ASIN_NAMES[asin]}) ---")

        for category in ["OB", "CB", "R", "S", "C", "N"]:
            category_samples = samples[asin][category]
            if not category_samples:
                continue

            print(f"\n  Category: {category} ({len(category_samples)} samples)")

            # Get rubric for this category's module
            module = CATEGORY_MODULES.get(category, {}).get('module', 'm14')
            rubric_key = module.upper()
            rubrics = RUBRIC_DATA.get(rubric_key, [])

            if not rubrics:
                print(f"    No rubrics found for {rubric_key}")
                continue

            for i, sample in enumerate(category_samples):
                keyword = sample['keyword']
                record = sample['record']
                record_idx = sample['record_idx']
                sample_module = sample['module']

                # Get module output
                output = module_results.get(sample_module, {}).get(record_idx, {})

                if not output:
                    print(f"    [{i+1}] \"{keyword[:30]}...\" - NO RESULT")
                    continue

                # Run judge for first rubric
                rubric = rubrics[0]
                result = run_judge(
                    client=client,
                    rubric=rubric,
                    input_data=record.get('input', {}),
                    expected=record.get('expected', {}),
                    module_output=output
                )

                verdict = result['verdict']
                icon = "✓" if verdict == "PASS" else "✗" if verdict == "FAIL" else "?"
                print(f"    [{i+1}] {icon} \"{keyword[:35]}\" → {verdict}")

                # Track results
                all_results.append({
                    'asin': asin,
                    'category': category,
                    'keyword': keyword,
                    'module': sample_module,
                    'verdict': verdict,
                    'reasoning': result['reasoning'],
                })

                summary_by_category[category]['total'] += 1
                summary_by_asin[asin]['total'] += 1

                if verdict == 'PASS':
                    summary_by_category[category]['pass'] += 1
                    summary_by_asin[asin]['pass'] += 1
                elif verdict == 'FAIL':
                    summary_by_category[category]['fail'] += 1
                    summary_by_asin[asin]['fail'] += 1
                else:
                    summary_by_category[category]['error'] += 1
                    summary_by_asin[asin]['error'] += 1

    # Print summary
    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)

    print("\nBy Category:")
    print(f"{'Category':<10} | {'Pass':>6} | {'Fail':>6} | {'Error':>6} | {'Total':>6} | {'Pass Rate':>10}")
    print("-" * 60)

    for category in ["OB", "CB", "R", "S", "C", "N"]:
        s = summary_by_category[category]
        rate = (s['pass'] / s['total'] * 100) if s['total'] > 0 else 0
        print(f"{category:<10} | {s['pass']:>6} | {s['fail']:>6} | {s['error']:>6} | {s['total']:>6} | {rate:>9.1f}%")

    total = {'pass': 0, 'fail': 0, 'error': 0, 'total': 0}
    for s in summary_by_category.values():
        for k in total:
            total[k] += s[k]

    rate = (total['pass'] / total['total'] * 100) if total['total'] > 0 else 0
    print("-" * 60)
    print(f"{'TOTAL':<10} | {total['pass']:>6} | {total['fail']:>6} | {total['error']:>6} | {total['total']:>6} | {rate:>9.1f}%")

    print("\nBy ASIN:")
    print(f"{'ASIN':<12} | {'Product':<15} | {'Pass':>5} | {'Fail':>5} | {'Rate':>8}")
    print("-" * 55)

    for asin in FULL_COVERAGE_ASINS:
        s = summary_by_asin[asin]
        rate = (s['pass'] / s['total'] * 100) if s['total'] > 0 else 0
        print(f"{asin} | {ASIN_NAMES[asin][:15]:<15} | {s['pass']:>5} | {s['fail']:>5} | {rate:>7.1f}%")

    # Save results
    OUTPUT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = OUTPUT_DIR / f"sampled_eval_{timestamp}.json"

    with open(output_file, 'w') as f:
        json.dump({
            'timestamp': timestamp,
            'summary_by_category': dict(summary_by_category),
            'summary_by_asin': dict(summary_by_asin),
            'total': total,
            'results': all_results,
        }, f, indent=2)

    print(f"\nResults saved to: {output_file}")
    print("=" * 70)

    return all_results


if __name__ == "__main__":
    run_sampled_evaluation(max_per_category=10)
