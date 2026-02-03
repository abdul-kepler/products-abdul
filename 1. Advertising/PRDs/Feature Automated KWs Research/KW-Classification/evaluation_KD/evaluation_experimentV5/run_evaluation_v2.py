#!/usr/bin/env python3
"""
Experiment V5 Evaluation Script.

Reads CSV datasets from experiment_results/ and runs LLM-as-a-Judge
evaluation using rubrics_v5.yaml.

Usage:
    python3 evaluation_experimentV5/run_evaluation_v2.py --module m01 --limit 10
    python3 evaluation_experimentV5/run_evaluation_v2.py --module all --limit 10
"""

import argparse
import csv
import json
import os
import sys
import yaml
from pathlib import Path
from datetime import datetime
from typing import Optional

from openai import OpenAI

# Import progress tracker for auto-history
try:
    from progress_tracker import add_run_to_history
except ImportError:
    add_run_to_history = None

# Paths
SCRIPT_DIR = Path(__file__).parent
EVALUATION_KD_DIR = SCRIPT_DIR.parent  # evaluation_KD folder
PROJECT_ROOT = EVALUATION_KD_DIR.parent  # Actual project root
EXPERIMENT_DATA_DIR = PROJECT_ROOT / "experiment_results"
OUTPUT_DIR = SCRIPT_DIR / "judge_results"
CONFIG_DIR = EVALUATION_KD_DIR / "config"

# Module to CSV file mapping - ALL MODULES M01-M16
MODULE_CSV_MAP = {
    # ==========================================================================
    # M01 Family - Extract Own Brand Entities
    # ==========================================================================
    # M01: v1 (baseline) -> v2 -> v3 (gpt-4o-mini) -> v3 (gpt-5, latest)
    'm01_v1': {
        'folder': 'M01_ExtractOwnBrandEntities',
        'file': 'M01_ExtractOwnBrandEntities_v1_150126_1.csv',  # V1 baseline
        'rubrics': 'M01',
        'prompt_version': 'v1',
        'model': 'gpt-4o-mini',
    },
    'm01_v2': {
        'folder': 'M01_ExtractOwnBrandEntities',
        'file': 'M01_ExtractOwnBrandEntities_v2_190126_1.csv',  # V2 prompt
        'rubrics': 'M01',
        'prompt_version': 'v2',
        'model': 'gpt-4o-mini',
    },
    'm01_v3': {
        'folder': 'M01_ExtractOwnBrandEntities',
        'file': 'M01_V2_ExtractOwnBrandEntities_v3_190126_1.csv',  # V3 prompt, gpt-4o-mini
        'rubrics': 'M01',
        'prompt_version': 'v3',
        'model': 'gpt-4o-mini',
    },
    'm01_v3_gpt5': {
        'folder': 'M01_ExtractOwnBrandEntities',
        'file': 'M01_V3_ExtractOwnBrandEntities_v3_190126_gpt5.csv',  # V3 prompt, gpt-5
        'rubrics': 'M01',
        'prompt_version': 'v3',
        'model': 'gpt-5',
        'display_module': 'm01_v3',  # Display as m01_v3 in progress history
    },
    'm01a': {
        'folder': 'M01A_ExtractOwnBrandVariations',
        'file': 'M01A_ExtractOwnBrandVariations_v1_150126_1.csv',
        'rubrics': 'M01a',
        'prompt_version': 'v1',
        'model': 'gpt-4o-mini',
    },
    'm01a_v2': {
        'folder': 'M01A_ExtractOwnBrandVariations',
        'file': 'M01A_V2_ExtractOwnBrandVariations_v2_190126_gpt5.csv',
        'rubrics': 'M01a',
        'prompt_version': 'v2',
        'model': 'gpt-5',
    },
    'm01a_v2_gemini': {
        'folder': 'M01A_ExtractOwnBrandVariations',
        'file': 'M01A_V2_ExtractOwnBrandVariations_v2_200126_gemini20flash.csv',
        'rubrics': 'M01a',
        'prompt_version': 'v2',
        'model': 'gemini-2.0-flash',
    },
    'm01b': {
        'folder': 'M01B_ExtractBrandRelatedTerms',
        'file': 'M01B_ExtractBrandRelatedTerms_v1_150126_1.csv',
        'rubrics': 'M01b',
        'prompt_version': 'v1',
        'model': 'gpt-4o-mini',
    },
    'm01b_v1_gemini': {
        'folder': 'M01B_ExtractBrandRelatedTerms',
        'file': 'M01B_V1_ExtractBrandRelatedTerms_v1_200126_gemini20flash.csv',
        'rubrics': 'M01b',
        'prompt_version': 'v1',
        'model': 'gemini-2.0-flash',
    },
    'm01_v3_gemini': {
        'folder': 'M01_ExtractOwnBrandEntities',
        'file': 'M01_V3_ExtractOwnBrandEntities_v3_200126_gemini20flash.csv',
        'rubrics': 'M01',
        'prompt_version': 'v3',
        'model': 'gemini-2.0-flash',
    },
    'm01_v4_gpt4omini': {
        'folder': 'M01_ExtractOwnBrandEntities',
        'file': 'M01_V4_ExtractOwnBrandEntities_v4_210126_gpt4omini.csv',
        'rubrics': 'M01',
        'prompt_version': 'v4',
        'model': 'gpt-4o-mini',
    },
    'm01_v4_gpt4o': {
        'folder': 'M01_ExtractOwnBrandEntities',
        'file': 'M01_V4_ExtractOwnBrandEntities_v4_210126_gpt4o.csv',
        'rubrics': 'M01',
        'prompt_version': 'v4',
        'model': 'gpt-4o',
    },
    'm01_v5_gpt4omini': {
        'folder': 'M01_ExtractOwnBrandEntities',
        'file': 'M01_V5_ExtractOwnBrandEntities_v5_210126_gpt4omini.csv',
        'rubrics': 'M01',
        'prompt_version': 'v5',
        'model': 'gpt-4o-mini',
    },
    'm01_v5_gpt5': {
        'folder': 'M01_ExtractOwnBrandEntities',
        'file': 'M01_V5_ExtractOwnBrandEntities_v5_210126_gpt5.csv',
        'rubrics': 'M01',
        'prompt_version': 'v5',
        'model': 'gpt-5',
    },

    # ==========================================================================
    # M02 Family - Classify Own Brand Keywords
    # ==========================================================================
    'm02': {
        'folder': 'M02_ClassifyOwnBrandKeywords',
        'file': 'M02_ClassifyOwnBrandKeywords_v1_150126_1.csv',
        'rubrics': 'M02',
        'prompt_version': 'v1',
        'model': 'gpt-4o-mini',
    },
    'm02b': {
        'folder': 'M02B_ClassifyOwnBrandKeywords_PathB',
        'file': 'M02B_ClassifyOwnBrandKeywords_PathB_v1_150126_1.csv',
        'rubrics': 'M02',  # Uses same rubrics as M02
        'prompt_version': 'v1',
        'model': 'gpt-4o-mini',
    },

    # ==========================================================================
    # M04 Family - Classify Competitor Brand Keywords
    # ==========================================================================
    'm04': {
        'folder': 'M04_ClassifyCompetitorBrandKeywords',
        'file': 'M04_ClassifyCompetitorBrandKeywords_v1_150126_1.csv',
        'rubrics': 'M04',
        'prompt_version': 'v1',
        'model': 'gpt-4o-mini',
    },
    'm04b': {
        'folder': 'M04B_ClassifyCompetitorBrandKeywords_PathB',
        'file': 'M04B_ClassifyCompetitorBrandKeywords_PathB_v1_150126_1.csv',
        'rubrics': 'M04',  # Uses same rubrics as M04
        'prompt_version': 'v1',
        'model': 'gpt-4o-mini',
    },

    # ==========================================================================
    # M05 Family - Classify Non-Branded Keywords
    # ==========================================================================
    'm05': {
        'folder': 'M05_ClassifyNonBrandedKeywords',
        'file': 'M05_ClassifyNonBrandedKeywords_v1_150126_1.csv',
        'rubrics': 'M05',
        'prompt_version': 'v1',
        'model': 'gpt-4o-mini',
    },
    'm05b': {
        'folder': 'M05B_ClassifyNonBrandedKeywords_PathB',
        'file': 'M05B_ClassifyNonBrandedKeywords_PathB_v1_150126_1.csv',
        'rubrics': 'M05',  # Uses same rubrics as M05
        'prompt_version': 'v1',
        'model': 'gpt-4o-mini',
    },

    # ==========================================================================
    # M06 - Generate Product Type Taxonomy
    # ==========================================================================
    'm06_gd': {
        'folder': 'M06_GenerateProductTypeTaxonomy',
        'file': 'M06_GenerateProductTypeTaxonomy_gd1_v1_150126_1.csv',
        'rubrics': 'M06',
        'prompt_version': 'v1',
        'model': 'gpt-4o-mini',
        'dataset_variant': 'gd1',
    },
    'm06_sd': {
        'folder': 'M06_GenerateProductTypeTaxonomy',
        'file': 'M06_GenerateProductTypeTaxonomy_sd1_v1_150126_1.csv',
        'rubrics': 'M06',
        'prompt_version': 'v1',
        'model': 'gpt-4o-mini',
        'dataset_variant': 'sd1',
    },

    # ==========================================================================
    # M07 - Extract Product Attributes
    # ==========================================================================
    'm07_gd': {
        'folder': 'M07_ExtractProductAttributes',
        'file': 'M07_ExtractProductAttributes_gd1_v1_150126_1.csv',
        'rubrics': 'M07',
        'prompt_version': 'v1',
        'model': 'gpt-4o-mini',
        'dataset_variant': 'gd1',
    },
    'm07_sd': {
        'folder': 'M07_ExtractProductAttributes',
        'file': 'M07_ExtractProductAttributes-sd1_v1_150126_1.csv',
        'rubrics': 'M07',
        'prompt_version': 'v1',
        'model': 'gpt-4o-mini',
        'dataset_variant': 'sd1',
    },

    # ==========================================================================
    # M08 - Assign Attribute Ranks
    # ==========================================================================
    'm08': {
        'folder': 'M08_AssignAttributeRanks',
        'file': 'M08_AssignAttributeRanks_v1_dg1_150126_1.csv',
        'rubrics': 'M08',
        'prompt_version': 'v1',
        'model': 'gpt-4o-mini',
    },
    'm08_sd': {
        'folder': 'M08_AssignAttributeRanks',
        'file': 'M08_AssignAttributeRanks_sd1_v1_150126_1.csv',
        'rubrics': 'M08',
        'prompt_version': 'v1',
        'model': 'gpt-4o-mini',
        'dataset_variant': 'sd1',
    },
    'm08_v2': {
        'folder': 'M08_AssignAttributeRanks',
        'file': 'M08_V2_AssignAttributeRanks_v1_gd1_150126_1.csv',
        'rubrics': 'M08',
        'prompt_version': 'v2',
        'model': 'gpt-4o-mini',
    },
    'm08_v2_sd': {
        'folder': 'M08_AssignAttributeRanks',
        'file': 'M08_V2_AssignAttributeRanks_sd1_v1_150126_1.csv',
        'rubrics': 'M08',
        'prompt_version': 'v2',
        'model': 'gpt-4o-mini',
        'dataset_variant': 'sd1',
    },

    # ==========================================================================
    # M09-M11 - Primary Use & Hard Constraints
    # ==========================================================================
    'm09': {
        'folder': 'M09_IdentifyPrimaryIntendedUse',
        'file': 'M09_IdentifyPrimaryIntendedUse_v1_150126_1.csv',
        'rubrics': 'M09',
        'prompt_version': 'v1',
        'model': 'gpt-4o-mini',
    },
    'm10': {
        'folder': 'M10_ValidatePrimaryIntendedUse',
        'file': 'M10_ValidatePrimaryIntendedUse_v1_150126_1.csv',
        'rubrics': 'M10',
        'prompt_version': 'v1',
        'model': 'gpt-4o-mini',
    },
    'm11': {
        'folder': 'M11_IdentifyHardConstraints',
        'file': 'M11_IdentifyHardConstraints_v1_150126_1.csv',
        'rubrics': 'M11',
        'prompt_version': 'v1',
        'model': 'gpt-4o-mini',
    },

    # ==========================================================================
    # M12-M16 - Product Checks
    # ==========================================================================
    'm12': {
        'folder': 'M12_HardConstraintViolationCheck',
        'file': 'M12_HardConstraintViolationCheck_v1_150126_1.csv',
        'rubrics': 'M12',
        'prompt_version': 'v1',
        'model': 'gpt-4o-mini',
    },
    'm13': {
        'folder': 'M13_ProductTypeCheck',
        'file': 'M13_ProductTypeCheck_v1_150126_1.csv',
        'rubrics': 'M13',
        'prompt_version': 'v1',
        'model': 'gpt-4o-mini',
    },
    'm14': {
        'folder': 'M14_PrimaryUseCheckSameType',
        'file': 'M14_PrimaryUseCheckSameType_v1_150126_1.csv',
        'rubrics': 'M14',
        'prompt_version': 'v1',
        'model': 'gpt-4o-mini',
    },
    'm15': {
        'folder': 'M15_SubstituteCheck',
        'file': 'M15_SubstituteCheck_v1_150126_1.csv',
        'rubrics': 'M15',
        'prompt_version': 'v1',
        'model': 'gpt-4o-mini',
    },
    'm16': {
        'folder': 'M16_ComplementaryCheck',
        'file': 'M16_ComplementaryCheck_v1_150126_1.csv',
        'rubrics': 'M16',
        'prompt_version': 'v1',
        'model': 'gpt-4o-mini',
    },
}

# Default rubric version
DEFAULT_RUBRICS_VERSION = "v5"


def load_env():
    """Load API key from .env file."""
    env_file = PROJECT_ROOT / ".env"  # PROJECT_ROOT is now actual project root
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip().strip('"').strip("'")


def load_rubrics(version: str = DEFAULT_RUBRICS_VERSION) -> dict:
    """Load rubrics from versioned yaml file."""
    version_num = version.replace("v", "").replace("V", "")
    rubrics_file = CONFIG_DIR / f"rubrics_v{version_num}.yaml"

    if not rubrics_file.exists():
        print(f"ERROR: Rubrics file not found: {rubrics_file}")
        return {}

    print(f"INFO: Loading rubrics from {rubrics_file.name}")

    with open(rubrics_file) as f:
        data = yaml.safe_load(f)

    yaml_version = data.get('version', 'unknown')
    print(f"INFO: Rubrics version {yaml_version}")

    rubrics_data = {}
    yaml_rubrics = data.get('rubrics', {})

    for rubric_id, rubric in yaml_rubrics.items():
        module = rubric.get('module', '')
        if module not in rubrics_data:
            rubrics_data[module] = []

        simple_rubric = {
            'id': rubric_id,
            'criterion': rubric.get('criterion', ''),
            'check': rubric.get('check', ''),
            'fail': rubric.get('fail_definition', '').strip(),
            'pass': rubric.get('pass_definition', '').strip()
        }
        rubrics_data[module].append(simple_rubric)

    total = sum(len(r) for r in rubrics_data.values())
    print(f"INFO: Loaded {len(rubrics_data)} modules, {total} rubrics")
    return rubrics_data


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

    print(f"INFO: Loading data from {csv_path.name}")

    records = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Parse JSON fields
            record = {
                'raw': row,
                'asin': row.get('ASIN', ''),
                'brand': row.get('Brand', ''),
            }

            # Parse input JSON
            if 'input' in row and row['input']:
                try:
                    record['input'] = json.loads(row['input'])
                except json.JSONDecodeError:
                    record['input'] = row['input']

            # Parse output JSON
            if 'output' in row and row['output']:
                try:
                    record['output'] = json.loads(row['output'])
                except json.JSONDecodeError:
                    record['output'] = row['output']

            # Parse expected JSON
            if 'expected' in row and row['expected']:
                try:
                    record['expected'] = json.loads(row['expected'])
                except json.JSONDecodeError:
                    record['expected'] = row['expected']

            # Handle M04 special format (no 'output' column, has Output_CB)
            if module == 'm04':
                record['output'] = {
                    'branding_scope_2': row.get('Output_CB'),
                    'reasoning': row.get('Reasoning', ''),
                }
                record['expected'] = {
                    'branding_scope_2': row.get('Expected CB'),
                }
                record['keyword'] = row.get('Keyword', '')

            # Handle M02 special format
            if module == 'm02':
                record['keyword'] = row.get('Keyword', '')
                if 'Output_OB' in row:
                    record['output']['output_ob'] = row.get('Output_OB')

            records.append(record)

    print(f"INFO: Loaded {len(records)} records")
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


def run_evaluation(
    module: str,
    rubric_id: Optional[str] = None,
    limit: int = 10,
    judge_model: str = "gpt-4o-mini",
    rubrics_version: str = DEFAULT_RUBRICS_VERSION
) -> dict:
    """Run the full evaluation for a module."""

    # Load rubrics first to get config
    all_rubrics = load_rubrics(rubrics_version)
    config = MODULE_CSV_MAP.get(module)
    if not config:
        print(f"ERROR: Unknown module {module}")
        return {}

    # experiment_model is from config (for documentation/labeling)
    # judge_model is for the actual LLM API call (always OpenAI compatible)
    experiment_model = config.get('model', 'unknown')

    print(f"\n{'='*60}")
    print(f"EXPERIMENT V2 EVALUATION")
    print(f"{'='*60}")
    print(f"Module: {module.upper()}")
    print(f"Experiment Model: {experiment_model}")
    print(f"Judge Model: {judge_model}")
    print(f"Rubrics: {rubrics_version}")
    print(f"Limit: {limit} samples")

    rubrics = all_rubrics.get(config['rubrics'], [])
    if rubric_id:
        rubrics = [r for r in rubrics if r['id'] == rubric_id]
        if not rubrics:
            print(f"ERROR: Rubric '{rubric_id}' not found")
            return {}

    print(f"Rubrics to evaluate: {len(rubrics)}")

    # Load data
    data = load_csv_data(module)
    if not data:
        return {}

    data = data[:limit]
    print(f"Samples to evaluate: {len(data)}")

    # Initialize OpenAI
    load_env()
    client = OpenAI()

    # Run evaluations
    all_evaluations = []
    summary = {'pass': 0, 'fail': 0, 'error': 0}

    for idx, record in enumerate(data):
        asin = record.get('asin', f'sample_{idx}')
        print(f"\n--- Sample {idx + 1}/{len(data)}: {asin} ---")

        input_data = record.get('input', {})
        expected = record.get('expected', {})
        output = record.get('output', {})

        for rubric in rubrics:
            print(f"  Evaluating: {rubric['criterion']}...", end=" ")

            result = run_judge(client, rubric, input_data, expected, output, judge_model)
            verdict = result['verdict']

            if verdict == 'PASS':
                summary['pass'] += 1
                print("✓ PASS")
            elif verdict == 'FAIL':
                summary['fail'] += 1
                print("✗ FAIL")
            else:
                summary['error'] += 1
                print("⚠ ERROR")

            all_evaluations.append({
                'sample_id': asin,
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

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"PASS: {summary['pass']}")
    print(f"FAIL: {summary['fail']}")
    print(f"ERROR: {summary['error']}")
    print(f"Pass Rate: {pass_rate:.1f}%")
    print(f"{'='*60}")

    # Save results
    OUTPUT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    output_data = {
        'experiment': 'V2',
        'module': module,
        'model': experiment_model,
        'rubrics_version': rubrics_version,
        'timestamp': datetime.now().isoformat(),
        'data_source': str(EXPERIMENT_DATA_DIR / config['folder'] / config['file']),
        'summary': summary,
        'pass_rate': pass_rate,
        'evaluations': all_evaluations,
    }

    output_file = OUTPUT_DIR / f"{module}_judge_{timestamp}.json"
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\nResults saved to: {output_file}")

    # Auto-add to progress history
    if add_run_to_history:
        print("Adding to progress history...")
        add_run_to_history(output_file)
    else:
        print("(progress_tracker not available - run 'python progress_tracker.py --rebuild' to update history)")

    return output_data


def main():
    parser = argparse.ArgumentParser(description="Experiment V2 Evaluation")
    parser.add_argument("--module", "-m", type=str, default="m01",
                        help="Module to evaluate (m01, m01_v1, m01a, m01b, m02, m04, or 'all')")
    parser.add_argument("--rubric", "-r", type=str, default=None,
                        help="Specific rubric ID to evaluate")
    parser.add_argument("--limit", "-l", type=int, default=10,
                        help="Number of samples to evaluate")
    parser.add_argument("--judge-model", type=str, default="gpt-4o-mini",
                        help="Model for LLM judge (default: gpt-4o-mini)")
    parser.add_argument("--rubrics-version", "-v", type=str, default=DEFAULT_RUBRICS_VERSION,
                        help=f"Rubric version (default: {DEFAULT_RUBRICS_VERSION})")
    parser.add_argument("--list-modules", action="store_true",
                        help="List available modules")

    args = parser.parse_args()

    if args.list_modules:
        print("\nAvailable modules:")
        for mod, config in MODULE_CSV_MAP.items():
            csv_path = EXPERIMENT_DATA_DIR / config['folder'] / config['file']
            status = "✓" if csv_path.exists() else "✗"
            print(f"  {status} {mod}: {config['file']}")
        return

    if args.module == "all":
        print(f"\n{'='*60}")
        print(f"RUNNING ALL MODULES")
        print(f"{'='*60}\n")

        all_results = {}
        for module in MODULE_CSV_MAP.keys():
            try:
                result = run_evaluation(
                    module=module,
                    rubric_id=args.rubric,
                    limit=args.limit,
                    judge_model=args.judge_model,
                    rubrics_version=args.rubrics_version,
                )
                all_results[module] = result.get('pass_rate', -1)
            except Exception as e:
                print(f"ERROR: {e}")
                all_results[module] = -1

        print(f"\n{'='*60}")
        print("ALL MODULES SUMMARY")
        print(f"{'='*60}")
        for module, rate in all_results.items():
            status = f"{rate:.1f}%" if rate >= 0 else "ERROR"
            print(f"  {module.upper()}: {status}")
        return

    run_evaluation(
        module=args.module,
        rubric_id=args.rubric,
        limit=args.limit,
        judge_model=args.judge_model,
        rubrics_version=args.rubrics_version,
    )


if __name__ == "__main__":
    main()
