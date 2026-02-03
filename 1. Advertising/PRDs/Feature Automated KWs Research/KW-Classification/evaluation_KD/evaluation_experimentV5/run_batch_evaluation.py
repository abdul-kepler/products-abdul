#!/usr/bin/env python3
"""
Batch Evaluation Script - Automatically evaluate all unevaluated experiments.

Finds CSV files in experiment_results/ that don't have corresponding judge results
and runs LLM-as-a-Judge evaluation on them.

Usage:
    python run_batch_evaluation.py                    # Evaluate all missing
    python run_batch_evaluation.py --limit 20         # Limit samples per experiment
    python run_batch_evaluation.py --module m13       # Filter by module
    python run_batch_evaluation.py --dry-run          # Show what would be evaluated
"""

import argparse
import csv
import json
import os
import re
import sys
import yaml
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Tuple

from openai import OpenAI

# Paths
SCRIPT_DIR = Path(__file__).parent
EVALUATION_KD_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = EVALUATION_KD_DIR.parent
EXPERIMENT_DATA_DIR = PROJECT_ROOT / "experiment_results"
OUTPUT_DIR = SCRIPT_DIR / "judge_results"
CONFIG_DIR = EVALUATION_KD_DIR / "config"
ALL_RUNS_FILE = PROJECT_ROOT / "tracking_dashboard" / "data" / "all_runs.yaml"

# Module folder to rubrics mapping
MODULE_RUBRICS_MAP = {
    'M01': 'M01',
    'M01A': 'M01a',
    'M01B': 'M01b',
    'M02': 'M02',
    'M02B': 'M02',
    'M04': 'M04',
    'M04B': 'M04',
    'M05': 'M05',
    'M05B': 'M05',
    'M06': 'M06',
    'M07': 'M07',
    'M08': 'M08',
    'M09': 'M09',
    'M10': 'M10',
    'M11': 'M11',
    'M12': 'M12',
    'M12B': 'M12',  # Uses same rubrics as M12
    'M13': 'M13',
    'M14': 'M14',
    'M15': 'M15',
    'M16': 'M16',
}

# Model name mapping (from filename to display name)
MODEL_MAP = {
    'gpt4omini': 'gpt-4o-mini',
    'gpt4o': 'gpt-4o',
    'gpt5': 'gpt-5',
    'gemini20flash': 'gemini-2.0-flash',
    'gemini25pro': 'gemini-2.5-pro',
    'claudesonnet420250514': 'claude-sonnet-4',
    'claudesonnet': 'claude-sonnet-4',
}

DEFAULT_RUBRICS_VERSION = "v5"


def load_env():
    """Load API key from .env file."""
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip().strip('"').strip("'")


def parse_csv_filename(filename: str) -> Dict[str, str]:
    """
    Parse experiment info from CSV filename.

    Example: M13_V1_ProductTypeCheck_v1_220126_gemini20flash.csv
    Returns: {module: 'm13', version: 'v1', model: 'gemini-2.0-flash', date: '220126'}
    """
    stem = Path(filename).stem

    # Extract module (M01, M01A, M12B, etc.)
    module_match = re.match(r'(M\d+[AB]?)', stem)
    module_base = module_match.group(1) if module_match else 'UNKNOWN'

    # Extract version
    version_match = re.search(r'[_-][vV](\d+)[_-]', stem)
    version = f"v{version_match.group(1)}" if version_match else 'v1'

    # Extract date
    date_match = re.search(r'(\d{6})(?:_|$)', stem)
    date = date_match.group(1) if date_match else ''

    # Extract model
    model = 'unknown'
    for model_key, model_name in MODEL_MAP.items():
        if model_key in stem.lower():
            model = model_name
            break

    return {
        'module_base': module_base,
        'module': module_base.lower(),
        'version': version,
        'model': model,
        'date': date,
        'filename': filename,
    }


def get_evaluated_experiments() -> set:
    """Get set of already evaluated experiment identifiers."""
    evaluated = set()

    # Check all_runs.yaml
    if ALL_RUNS_FILE.exists():
        with open(ALL_RUNS_FILE) as f:
            data = yaml.safe_load(f) or {}
        for run_id, run in data.get('runs', {}).items():
            csv_file = run.get('csv_file', '')
            if csv_file:
                evaluated.add(Path(csv_file).stem)

    # Also check judge_results directory
    if OUTPUT_DIR.exists():
        for judge_file in OUTPUT_DIR.glob("*_judge_*.json"):
            try:
                with open(judge_file) as f:
                    judge_data = json.load(f)
                data_source = judge_data.get('data_source', '')
                if data_source:
                    evaluated.add(Path(data_source).stem)
            except:
                pass

    return evaluated


def find_unevaluated_csvs(module_filter: Optional[str] = None) -> List[Tuple[Path, Dict]]:
    """Find all CSV files that haven't been evaluated yet."""
    evaluated = get_evaluated_experiments()
    unevaluated = []

    for csv_path in EXPERIMENT_DATA_DIR.glob("*/*.csv"):
        stem = csv_path.stem

        # Skip if already evaluated
        if stem in evaluated:
            continue

        # Parse filename
        info = parse_csv_filename(csv_path.name)

        # Filter by module if specified
        if module_filter:
            if info['module'] != module_filter.lower():
                continue

        # Check if rubrics exist for this module
        if info['module_base'] not in MODULE_RUBRICS_MAP:
            print(f"  ⚠ Skipping {csv_path.name}: No rubrics mapping for {info['module_base']}")
            continue

        unevaluated.append((csv_path, info))

    # Sort by module, then date
    unevaluated.sort(key=lambda x: (x[1]['module'], x[1]['date']))
    return unevaluated


def load_rubrics(version: str = DEFAULT_RUBRICS_VERSION) -> dict:
    """Load rubrics from versioned yaml file."""
    version_num = version.replace("v", "").replace("V", "")
    rubrics_file = CONFIG_DIR / f"rubrics_v{version_num}.yaml"

    if not rubrics_file.exists():
        print(f"ERROR: Rubrics file not found: {rubrics_file}")
        return {}

    with open(rubrics_file) as f:
        data = yaml.safe_load(f)

    rubrics_data = {}
    for rubric_id, rubric in data.get('rubrics', {}).items():
        module = rubric.get('module', '')

        rubric_entry = {
            'id': rubric_id,
            'criterion': rubric.get('criterion', ''),
            'check': rubric.get('check', ''),
            'fail': rubric.get('fail_definition', '').strip(),
            'pass': rubric.get('pass_definition', '').strip()
        }

        # Handle shared rubrics like "M12-M16"
        if '-' in module:
            # Parse range like "M12-M16" -> [M12, M13, M14, M15, M16]
            parts = module.split('-')
            if len(parts) == 2:
                start = int(parts[0].replace('M', ''))
                end = int(parts[1].replace('M', ''))
                for i in range(start, end + 1):
                    mod_key = f"M{i}"
                    if mod_key not in rubrics_data:
                        rubrics_data[mod_key] = []
                    rubrics_data[mod_key].append(rubric_entry)
        else:
            if module not in rubrics_data:
                rubrics_data[module] = []
            rubrics_data[module].append(rubric_entry)

    return rubrics_data


def load_csv_data(csv_path: Path) -> List[dict]:
    """Load data from CSV file."""
    records = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            record = {'raw': row}

            # Parse JSON fields
            for field in ['input', 'output', 'expected']:
                if field in row and row[field]:
                    try:
                        record[field] = json.loads(row[field])
                    except json.JSONDecodeError:
                        record[field] = row[field]

            # Extract sample_id
            if 'expected' in record and isinstance(record['expected'], dict):
                record['sample_id'] = record['expected'].get('sample_id', row.get('id', ''))
            else:
                record['sample_id'] = row.get('id', row.get('ASIN', ''))

            records.append(record)

    return records


def create_judge_prompt(rubric: dict, input_data: dict, expected: dict, output: dict) -> str:
    """Create the judge prompt for evaluation."""
    return f"""You are evaluating an LLM module output against a specific rubric criterion.

## Rubric
- **Criterion**: {rubric['criterion']}
- **Check**: {rubric['check']}
- **PASS conditions**:
{rubric['pass']}
- **FAIL conditions**:
{rubric['fail']}

## Input Data
{json.dumps(input_data, indent=2)}

## Expected Output
{json.dumps(expected, indent=2)}

## Actual Module Output
{json.dumps(output, indent=2)}

## Task
Evaluate whether the module output meets the rubric criterion.

Think step by step:
1. What does the rubric require?
2. What did the module output?
3. Does the output meet the PASS conditions or FAIL conditions?

Return ONLY a JSON object with this exact format:
{{"verdict": "PASS" or "FAIL", "reasoning": "Brief explanation of your decision"}}
"""


def run_judge(client: OpenAI, rubric: dict, input_data: dict, expected: dict, output: dict, model: str) -> dict:
    """Run the LLM judge for a single rubric evaluation."""
    prompt = create_judge_prompt(rubric, input_data, expected, output)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0
        )
        result = json.loads(response.choices[0].message.content)
        return {
            'verdict': result.get('verdict', 'ERROR'),
            'reasoning': result.get('reasoning', ''),
            'tokens': response.usage.total_tokens if response.usage else 0
        }
    except Exception as e:
        return {
            'verdict': 'ERROR',
            'reasoning': str(e),
            'tokens': 0
        }


def evaluate_single_csv(
    csv_path: Path,
    info: Dict,
    all_rubrics: dict,
    client: OpenAI,
    limit: int = 50,
    judge_model: str = "gpt-4o-mini"
) -> dict:
    """Evaluate a single CSV file."""

    module_base = info['module_base']
    rubrics_key = MODULE_RUBRICS_MAP.get(module_base)
    rubrics = all_rubrics.get(rubrics_key, [])

    if not rubrics:
        print(f"  ⚠ No rubrics found for {rubrics_key}")
        return {}

    print(f"\n{'='*60}")
    print(f"EVALUATING: {csv_path.name}")
    print(f"{'='*60}")
    print(f"  Module: {info['module']} | Version: {info['version']} | Model: {info['model']}")
    print(f"  Rubrics: {rubrics_key} ({len(rubrics)} criteria)")

    # Load data
    data = load_csv_data(csv_path)
    if not data:
        print(f"  ✗ No data found in CSV")
        return {}

    data = data[:limit]
    print(f"  Samples: {len(data)}")

    # Run evaluations
    all_evaluations = []
    summary = {'pass': 0, 'fail': 0, 'error': 0}

    for idx, record in enumerate(data):
        sample_id = record.get('sample_id', f'sample_{idx}')
        print(f"\n  Sample {idx + 1}/{len(data)}: {sample_id[:30]}...")

        input_data = record.get('input', {})
        expected = record.get('expected', {})
        output = record.get('output', {})

        for rubric in rubrics:
            result = run_judge(client, rubric, input_data, expected, output, judge_model)
            verdict = result['verdict']

            if verdict == 'PASS':
                summary['pass'] += 1
                print(f"    ✓ {rubric['criterion'][:40]}")
            elif verdict == 'FAIL':
                summary['fail'] += 1
                print(f"    ✗ {rubric['criterion'][:40]}")
            else:
                summary['error'] += 1
                print(f"    ⚠ {rubric['criterion'][:40]} - ERROR")

            all_evaluations.append({
                'sample_id': sample_id,
                'rubric_id': rubric['id'],
                'criterion': rubric['criterion'],
                'verdict': verdict,
                'reasoning': result['reasoning'],
                'input': input_data,
                'expected': expected,
                'output': output,
            })

    # Calculate pass rate
    total = summary['pass'] + summary['fail']
    pass_rate = (summary['pass'] / total * 100) if total > 0 else 0

    print(f"\n  SUMMARY: PASS={summary['pass']} FAIL={summary['fail']} ERROR={summary['error']}")
    print(f"  Pass Rate: {pass_rate:.1f}%")

    # Save results
    OUTPUT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    output_data = {
        'experiment': 'V5',
        'module': f"{info['module']}_{info['version']}",
        'model': info['model'],
        'prompt_version': info['version'],
        'rubrics_version': DEFAULT_RUBRICS_VERSION,
        'timestamp': datetime.now().isoformat(),
        'data_source': str(csv_path),
        'summary': summary,
        'pass_rate': pass_rate,
        'evaluations': all_evaluations,
    }

    # Create output filename matching CSV pattern
    output_file = OUTPUT_DIR / f"{csv_path.stem}_judge_{timestamp}.json"
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"  ✓ Saved: {output_file.name}")

    return output_data


def main():
    parser = argparse.ArgumentParser(description="Batch evaluate unevaluated experiments")
    parser.add_argument("--limit", "-l", type=int, default=50,
                        help="Number of samples per experiment (default: 50)")
    parser.add_argument("--module", "-m", type=str, default=None,
                        help="Filter by module (e.g., m13)")
    parser.add_argument("--judge-model", type=str, default="gpt-4o-mini",
                        help="Model for LLM judge (default: gpt-4o-mini)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be evaluated without running")
    parser.add_argument("--rubrics-version", "-v", type=str, default=DEFAULT_RUBRICS_VERSION,
                        help=f"Rubric version (default: {DEFAULT_RUBRICS_VERSION})")
    args = parser.parse_args()

    print("=" * 70)
    print("🔍 BATCH EVALUATION - Find & Evaluate Unevaluated Experiments")
    print("=" * 70)

    # Find unevaluated CSVs
    unevaluated = find_unevaluated_csvs(args.module)

    print(f"\nFound {len(unevaluated)} unevaluated experiments:")
    for csv_path, info in unevaluated:
        print(f"  • {info['module']}_{info['version']}_{info['model']}: {csv_path.name}")

    if args.dry_run:
        print("\n[DRY RUN - No evaluations performed]")
        return

    if not unevaluated:
        print("\n✓ All experiments have been evaluated!")
        return

    # Load rubrics
    all_rubrics = load_rubrics(args.rubrics_version)
    if not all_rubrics:
        print("ERROR: Could not load rubrics")
        return

    # Initialize OpenAI
    load_env()
    client = OpenAI()

    # Evaluate each CSV
    results = {}
    for csv_path, info in unevaluated:
        try:
            result = evaluate_single_csv(
                csv_path, info, all_rubrics, client,
                limit=args.limit,
                judge_model=args.judge_model
            )
            if result:
                results[csv_path.stem] = result.get('pass_rate', -1)
        except Exception as e:
            print(f"\n  ✗ ERROR: {e}")
            results[csv_path.stem] = -1

    # Final summary
    print("\n" + "=" * 70)
    print("📊 BATCH EVALUATION COMPLETE")
    print("=" * 70)

    for name, rate in results.items():
        status = f"{rate:.1f}%" if rate >= 0 else "ERROR"
        print(f"  {name}: {status}")

    print(f"\n✓ Evaluated {len(results)} experiments")
    print(f"\nRun 'python tracking_dashboard/scripts/update_all.py' to update dashboard")


if __name__ == "__main__":
    main()
