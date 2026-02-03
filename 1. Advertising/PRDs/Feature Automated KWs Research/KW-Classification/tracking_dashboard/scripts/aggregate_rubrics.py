#!/usr/bin/env python3
"""
Aggregate rubric-level statistics from judge results.

For each module, shows pass rate per rubric per model.
This helps identify which rubrics are problematic.
"""

import json
import yaml
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from typing import Dict, List

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
JUDGE_RESULTS_DIR = PROJECT_ROOT / "evaluation_KD" / "evaluation_experimentV5" / "judge_results"
DASHBOARDS_DIR = SCRIPT_DIR.parent / "dashboards"

# Model name normalization
MODEL_ALIASES = {
    'gpt-4o-mini': 'gpt-4o-mini',
    'gpt-4o': 'gpt-4o',
    'gpt-5': 'gpt-5',
    'gemini-2.0-flash': 'gemini-2.0-flash',
    'gemini-2.5-pro': 'gemini-2.5-pro',
    'claude-sonnet-4-20250514': 'claude-sonnet-4',
    'claude-sonnet-4': 'claude-sonnet-4',
}


def normalize_model(model: str) -> str:
    """Normalize model name."""
    return MODEL_ALIASES.get(model, model)


def normalize_module(module: str) -> str:
    """Extract base module name (m01, m02, etc.)."""
    # m01_v1_gemini -> m01
    parts = module.lower().split('_')
    return parts[0]


def process_judge_files() -> Dict:
    """
    Process all judge result files and aggregate rubric statistics.

    Returns structure:
    {
        'm01': {
            'rubrics': {
                'M01_brand_extracted': {
                    'criterion': 'Brand Extracted',
                    'is_primary': True,
                    'results': {
                        'gpt-4o-mini': {'pass': 10, 'fail': 2, 'total': 12, 'pass_rate': 83.3},
                        'gpt-5': {...},
                    }
                },
                'M01_no_hallucination': {...}
            }
        },
        'm02': {...}
    }
    """
    # Primary rubrics (same as in aggregate_results.py)
    PRIMARY_RUBRICS = {
        'M01_brand_extracted', 'M01a_has_variations', 'M02_correct_classification',
        'M04_correct_classification', 'M05_correct_classification',
        'M06_hierarchy_correct', 'M07_attributes_from_listing', 'M08_ranks_assigned',
        'M09_captures_core_purpose', 'M10_invalid_correctly_flagged',
        'M11_critical_not_missed', 'M12_correct_classification',
        'M13_same_type_correct', 'M14_same_use_correct',
        'M15_substitute_correct', 'M16_complementary_correct',
    }

    modules_data = defaultdict(lambda: {'rubrics': defaultdict(lambda: {
        'criterion': '',
        'is_primary': False,
        'results': defaultdict(lambda: {'pass': 0, 'fail': 0, 'error': 0, 'total': 0})
    })})

    for judge_file in sorted(JUDGE_RESULTS_DIR.glob('*.json')):
        try:
            with open(judge_file) as f:
                data = json.load(f)

            module = normalize_module(data.get('module', 'unknown'))
            model = normalize_model(data.get('model', 'unknown'))
            evaluations = data.get('evaluations', [])

            for ev in evaluations:
                rubric_id = ev.get('rubric_id', '')
                criterion = ev.get('criterion', '')
                verdict = ev.get('verdict', '').upper()

                if not rubric_id:
                    continue

                rubric_data = modules_data[module]['rubrics'][rubric_id]
                rubric_data['criterion'] = criterion
                rubric_data['is_primary'] = rubric_id in PRIMARY_RUBRICS

                results = rubric_data['results'][model]
                results['total'] += 1

                if verdict == 'PASS':
                    results['pass'] += 1
                elif verdict == 'FAIL':
                    results['fail'] += 1
                else:
                    results['error'] += 1

        except Exception as e:
            print(f"Error processing {judge_file.name}: {e}")
            continue

    # Calculate pass rates
    for module, mdata in modules_data.items():
        for rubric_id, rdata in mdata['rubrics'].items():
            for model, results in rdata['results'].items():
                if results['total'] > 0:
                    results['pass_rate'] = round(results['pass'] / results['total'] * 100, 1)
                else:
                    results['pass_rate'] = 0

    return dict(modules_data)


def generate_rubrics_summary(modules_data: Dict) -> Dict:
    """Generate summary statistics."""
    # All models across all evaluations
    all_models = set()
    for module, mdata in modules_data.items():
        for rubric_id, rdata in mdata['rubrics'].items():
            all_models.update(rdata['results'].keys())

    # Count rubrics
    total_rubrics = sum(len(mdata['rubrics']) for mdata in modules_data.values())
    primary_rubrics = sum(
        1 for mdata in modules_data.values()
        for rdata in mdata['rubrics'].values()
        if rdata.get('is_primary')
    )

    # Find worst performing rubrics (by average pass rate across models)
    worst_rubrics = []
    for module, mdata in modules_data.items():
        for rubric_id, rdata in mdata['rubrics'].items():
            pass_rates = [r['pass_rate'] for r in rdata['results'].values() if r['total'] > 0]
            if pass_rates:
                avg_pass_rate = sum(pass_rates) / len(pass_rates)
                worst_rubrics.append({
                    'module': module,
                    'rubric_id': rubric_id,
                    'criterion': rdata['criterion'],
                    'avg_pass_rate': round(avg_pass_rate, 1),
                    'is_primary': rdata['is_primary'],
                })

    worst_rubrics.sort(key=lambda x: x['avg_pass_rate'])

    return {
        'total_modules': len(modules_data),
        'total_rubrics': total_rubrics,
        'primary_rubrics': primary_rubrics,
        'secondary_rubrics': total_rubrics - primary_rubrics,
        'models': sorted(all_models),
        'worst_rubrics': worst_rubrics[:20],
        'generated_at': datetime.now().isoformat(),
    }


def save_rubrics_data(modules_data: Dict, summary: Dict):
    """Save rubrics data for dashboard."""
    # Convert defaultdicts to regular dicts for JSON serialization
    clean_data = {}
    for module, mdata in modules_data.items():
        clean_data[module] = {
            'rubrics': {}
        }
        for rubric_id, rdata in mdata['rubrics'].items():
            clean_data[module]['rubrics'][rubric_id] = {
                'criterion': rdata['criterion'],
                'is_primary': rdata['is_primary'],
                'results': dict(rdata['results'])
            }

    js_content = f'''/**
 * Rubrics data for dashboard
 * Auto-generated by aggregate_rubrics.py
 * Generated: {datetime.now().isoformat()}
 */

const rubricsData = {{
  modules: {json.dumps(clean_data, indent=2)},
  summary: {json.dumps(summary, indent=2)}
}};
'''

    output_file = DASHBOARDS_DIR / 'rubrics_data.js'
    with open(output_file, 'w') as f:
        f.write(js_content)

    print(f"Saved rubrics data to {output_file}")
    return output_file


def main():
    print("=" * 60)
    print("Aggregating Rubric Statistics")
    print("=" * 60)

    modules_data = process_judge_files()
    summary = generate_rubrics_summary(modules_data)

    print(f"\nModules: {summary['total_modules']}")
    print(f"Total rubrics: {summary['total_rubrics']}")
    print(f"  Primary: {summary['primary_rubrics']}")
    print(f"  Secondary: {summary['secondary_rubrics']}")
    print(f"Models: {', '.join(summary['models'])}")

    print("\n--- Worst Performing Rubrics ---")
    for r in summary['worst_rubrics'][:10]:
        primary_mark = '*' if r['is_primary'] else ' '
        print(f"  {primary_mark} {r['module'].upper():5} {r['rubric_id']:35} {r['avg_pass_rate']:5.1f}%")

    save_rubrics_data(modules_data, summary)

    print("\n" + "=" * 60)
    print("Done!")


if __name__ == "__main__":
    main()
