#!/usr/bin/env python3
"""
Calculate experiment costs based on token usage.

Reads CSV files and extracts token counts from metrics column,
then calculates costs using model pricing.
"""

import csv
import json
import yaml
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
EXPERIMENT_RESULTS_DIR = PROJECT_ROOT / "experiment_results"
DATA_DIR = SCRIPT_DIR.parent / "data"
DASHBOARDS_DIR = SCRIPT_DIR.parent / "dashboards"

# Model pricing per million tokens (input, output)
MODEL_PRICING = {
    'gpt-4o-mini': {'input': 0.15, 'output': 0.60},
    'gpt-4o': {'input': 2.50, 'output': 10.00},
    'gpt-5': {'input': 1.25, 'output': 10.00},
    'gemini-2.0-flash': {'input': 0.10, 'output': 0.40},
    'gemini-2.5-pro': {'input': 1.25, 'output': 5.00},
    'claude-sonnet-4-20250514': {'input': 3.00, 'output': 15.00},
    'claude-sonnet-4': {'input': 3.00, 'output': 15.00},
}

# Correction multiplier for estimated costs (based on comparison with actual billing)
# Token averages are from GPT-4o-mini which had shorter prompts
# Real prompts for Claude/GPT-5 tend to be ~2x longer
ESTIMATION_MULTIPLIER = 2.0

# Model name normalization
MODEL_ALIASES = {
    'gpt4omini': 'gpt-4o-mini',
    'gpt4o': 'gpt-4o',
    'gpt5': 'gpt-5',
    'gemini20flash': 'gemini-2.0-flash',
    'gemini25pro': 'gemini-2.5-pro',
    'claudesonnet420250514': 'claude-sonnet-4-20250514',
    'claudesonnet4': 'claude-sonnet-4',
}


def normalize_model(model: str) -> str:
    """Normalize model name to standard format."""
    model_lower = model.lower().replace('-', '').replace('.', '').replace(' ', '')
    return MODEL_ALIASES.get(model_lower, model)


def extract_model_from_filename(filename: str) -> str:
    """Extract model name from CSV filename."""
    filename_lower = filename.lower()

    if 'gpt4omini' in filename_lower or 'gpt-4o-mini' in filename_lower:
        return 'gpt-4o-mini'
    if 'gpt5' in filename_lower or 'gpt-5' in filename_lower:
        return 'gpt-5'
    if 'gpt4o' in filename_lower or 'gpt-4o' in filename_lower:
        return 'gpt-4o'
    if 'gemini20flash' in filename_lower or 'gemini-2.0-flash' in filename_lower:
        return 'gemini-2.0-flash'
    if 'gemini25pro' in filename_lower or 'gemini-2.5-pro' in filename_lower:
        return 'gemini-2.5-pro'
    if 'claude' in filename_lower or 'sonnet' in filename_lower:
        return 'claude-sonnet-4'

    return 'unknown'


def extract_module_from_path(csv_path: Path) -> str:
    """Extract module name from file path."""
    folder_name = csv_path.parent.name
    # M01_ExtractOwnBrandEntities -> m01
    if folder_name.startswith('M'):
        parts = folder_name.split('_')
        return parts[0].lower()
    return 'unknown'


def calculate_cost(prompt_tokens: int, completion_tokens: int, model: str) -> float:
    """Calculate cost for given token counts and model."""
    normalized = normalize_model(model)
    pricing = MODEL_PRICING.get(normalized)

    if not pricing:
        return 0.0

    input_cost = (prompt_tokens / 1_000_000) * pricing['input']
    output_cost = (completion_tokens / 1_000_000) * pricing['output']

    return input_cost + output_cost


def process_csv_file(csv_path: Path) -> Optional[Dict]:
    """Process a single CSV file and extract cost information."""
    if not csv_path.exists():
        return None

    total_prompt_tokens = 0
    total_completion_tokens = 0
    total_estimated_cost = 0.0
    records_with_tokens = 0
    records_with_cost = 0
    total_records = 0

    try:
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                total_records += 1
                metrics_str = row.get('metrics', '')

                if not metrics_str:
                    continue

                try:
                    metrics = json.loads(metrics_str)
                    if not isinstance(metrics, dict):
                        continue

                    # Extract tokens
                    prompt_tokens = metrics.get('prompt_tokens', 0) or 0
                    completion_tokens = metrics.get('completion_tokens', 0) or 0
                    estimated_cost = metrics.get('estimated_cost', 0) or 0

                    if prompt_tokens or completion_tokens:
                        total_prompt_tokens += prompt_tokens
                        total_completion_tokens += completion_tokens
                        records_with_tokens += 1

                    if estimated_cost:
                        total_estimated_cost += estimated_cost
                        records_with_cost += 1

                except (json.JSONDecodeError, TypeError, AttributeError):
                    continue

        # Try to get model from meta.json or filename
        meta_path = csv_path.with_suffix('.meta.json')
        model = 'unknown'

        if meta_path.exists():
            try:
                with open(meta_path) as f:
                    meta = json.load(f)
                if isinstance(meta, dict):
                    model = meta.get('model', 'unknown') or 'unknown'
            except:
                pass

        if model == 'unknown':
            model = extract_model_from_filename(csv_path.name) or 'unknown'

        model = normalize_model(model) if model else 'unknown'

        # Calculate cost from tokens if we have them
        calculated_cost = calculate_cost(total_prompt_tokens, total_completion_tokens, model)

        # Use estimated_cost if available, otherwise calculated
        final_cost = total_estimated_cost if records_with_cost > 0 else calculated_cost

        return {
            'file': csv_path.name,
            'module': extract_module_from_path(csv_path),
            'model': model,
            'total_records': total_records,
            'records_with_tokens': records_with_tokens,
            'prompt_tokens': total_prompt_tokens,
            'completion_tokens': total_completion_tokens,
            'total_tokens': total_prompt_tokens + total_completion_tokens,
            'estimated_cost': round(total_estimated_cost, 4),
            'calculated_cost': round(calculated_cost, 4),
            'final_cost': round(final_cost, 4),
        }

    except Exception as e:
        print(f"Error processing {csv_path}: {e}")
        return None


def calculate_module_averages() -> Dict[str, Dict]:
    """Calculate average tokens per record for each module from files with token data."""
    module_stats = {}

    for module_dir in EXPERIMENT_RESULTS_DIR.iterdir():
        if not module_dir.is_dir():
            continue

        module = module_dir.name.split('_')[0].lower()
        if module not in module_stats:
            module_stats[module] = {'prompt_tokens': 0, 'completion_tokens': 0, 'records': 0}

        for csv_file in module_dir.glob('*.csv'):
            try:
                with open(csv_file, newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        metrics_str = row.get('metrics', '')
                        if metrics_str:
                            try:
                                metrics = json.loads(metrics_str)
                                prompt = metrics.get('prompt_tokens', 0)
                                completion = metrics.get('completion_tokens', 0)
                                if prompt > 0:
                                    module_stats[module]['prompt_tokens'] += prompt
                                    module_stats[module]['completion_tokens'] += completion
                                    module_stats[module]['records'] += 1
                            except:
                                pass
            except:
                pass

    # Calculate averages
    averages = {}
    for module, stats in module_stats.items():
        if stats['records'] > 0:
            averages[module] = {
                'avg_prompt': stats['prompt_tokens'] / stats['records'],
                'avg_completion': stats['completion_tokens'] / stats['records'],
                'avg_total': (stats['prompt_tokens'] + stats['completion_tokens']) / stats['records'],
            }

    return averages


def aggregate_costs():
    """Aggregate costs from all experiment CSV files."""
    all_costs = []

    # First calculate module averages for estimation
    module_averages = calculate_module_averages()

    # Process all CSV files in experiment_results
    for module_dir in sorted(EXPERIMENT_RESULTS_DIR.iterdir()):
        if not module_dir.is_dir():
            continue

        for csv_file in sorted(module_dir.glob('*.csv')):
            result = process_csv_file(csv_file)
            if result:
                # If no token data, estimate based on module averages
                if result['total_tokens'] == 0 and result['total_records'] > 0:
                    module = result['module']
                    if module in module_averages:
                        avg = module_averages[module]
                        # Apply estimation multiplier since averages are from shorter prompts
                        result['prompt_tokens'] = int(avg['avg_prompt'] * result['total_records'] * ESTIMATION_MULTIPLIER)
                        result['completion_tokens'] = int(avg['avg_completion'] * result['total_records'] * ESTIMATION_MULTIPLIER)
                        result['total_tokens'] = result['prompt_tokens'] + result['completion_tokens']
                        result['calculated_cost'] = round(calculate_cost(
                            result['prompt_tokens'], result['completion_tokens'], result['model']
                        ), 4)
                        result['final_cost'] = result['calculated_cost']
                        result['is_estimated'] = True
                    else:
                        result['is_estimated'] = True
                else:
                    result['is_estimated'] = False

                # Include all experiments with records
                if result['total_records'] > 0:
                    all_costs.append(result)

    return all_costs


def generate_cost_summary(costs: list) -> dict:
    """Generate summary statistics from cost data."""
    # Group by model
    by_model = {}
    for c in costs:
        model = c['model']
        if model not in by_model:
            by_model[model] = {
                'experiments': 0,
                'experiments_estimated': 0,
                'total_tokens': 0,
                'prompt_tokens': 0,
                'completion_tokens': 0,
                'total_cost': 0.0,
            }
        by_model[model]['experiments'] += 1
        if c.get('is_estimated', False):
            by_model[model]['experiments_estimated'] += 1
        by_model[model]['total_tokens'] += c['total_tokens']
        by_model[model]['prompt_tokens'] += c['prompt_tokens']
        by_model[model]['completion_tokens'] += c['completion_tokens']
        by_model[model]['total_cost'] += c['final_cost']

    # Group by module
    by_module = {}
    for c in costs:
        module = c['module']
        if module not in by_module:
            by_module[module] = {
                'experiments': 0,
                'total_tokens': 0,
                'total_cost': 0.0,
            }
        by_module[module]['experiments'] += 1
        by_module[module]['total_tokens'] += c['total_tokens']
        by_module[module]['total_cost'] += c['final_cost']

    # Total
    total_cost = sum(c['final_cost'] for c in costs)
    total_tokens = sum(c['total_tokens'] for c in costs)

    return {
        'by_model': by_model,
        'by_module': by_module,
        'total_experiments': len(costs),
        'total_tokens': total_tokens,
        'total_cost': round(total_cost, 2),
        'generated_at': datetime.now().isoformat(),
    }


def save_costs_data(costs: list, summary: dict):
    """Save costs data for dashboard."""
    # Save as JavaScript
    js_content = f'''/**
 * Cost data for dashboard
 * Auto-generated by calculate_costs.py
 * Generated: {datetime.now().isoformat()}
 */

const costData = {{
  experiments: {json.dumps(costs, indent=2)},
  summary: {json.dumps(summary, indent=2)},
  pricing: {json.dumps(MODEL_PRICING, indent=2)}
}};
'''

    output_file = DASHBOARDS_DIR / 'cost_data.js'
    with open(output_file, 'w') as f:
        f.write(js_content)

    print(f"Saved cost data to {output_file}")
    return output_file


def main():
    print("=" * 60)
    print("Calculating Experiment Costs")
    print("=" * 60)

    costs = aggregate_costs()
    print(f"\nProcessed {len(costs)} experiments with token data")

    summary = generate_cost_summary(costs)

    print("\n--- Cost by Model ---")
    for model, data in sorted(summary['by_model'].items()):
        print(f"  {model:25} {data['experiments']:3} exp, {data['total_tokens']:>12,} tokens, ${data['total_cost']:.2f}")

    print(f"\n--- Total ---")
    print(f"  Experiments: {summary['total_experiments']}")
    print(f"  Tokens: {summary['total_tokens']:,}")
    print(f"  Cost: ${summary['total_cost']:.2f}")

    save_costs_data(costs, summary)

    print("\n" + "=" * 60)
    print("Done!")


if __name__ == "__main__":
    main()
