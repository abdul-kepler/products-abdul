#!/usr/bin/env python3
"""
Generate Improvement Analysis - Automatic suggestion generation from judge results.

This script analyzes rubric_breakdown from all_runs.yaml and generates:
1. Automatic suggestions based on low-performing rubrics
2. Tracks "applied" improvements by comparing versions
3. Outputs improvement_analysis.yaml for dashboard consumption

Usage:
    python generate_improvement_analysis.py              # Generate analysis
    python generate_improvement_analysis.py --verbose    # Detailed output
"""

import yaml
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any, Optional

# Paths
SCRIPT_DIR = Path(__file__).parent
TRACKING_DASHBOARD = SCRIPT_DIR.parent
DATA_DIR = TRACKING_DASHBOARD / "data"

# Input/Output files
ALL_RUNS_FILE = DATA_DIR / "all_runs.yaml"
IMPROVEMENT_ANALYSIS_FILE = DATA_DIR / "improvement_analysis.yaml"

# Thresholds for automatic suggestions
CRITICAL_THRESHOLD = 50.0   # Below this = High priority suggestion
WARNING_THRESHOLD = 70.0    # Below this = Medium priority suggestion
GOOD_THRESHOLD = 85.0       # Below this = Low priority suggestion

# Human-readable rubric names (for display)
RUBRIC_DISPLAY_NAMES = {
    'M01_brand_extracted': 'Brand Extracted',
    'M01_no_hallucination': 'No Hallucinated Brand',
    'M01_no_product_words': 'No Product Words in Brand',
    'M01_amazon_test_applied': 'Amazon Test Applied',
    'M01_no_duplicates': 'No Duplicate Entities',
    'M01a_has_variations': 'Has Variations',
    'M01a_variations_valid': 'Variations Valid',
    'M01a_no_duplicates': 'No Duplicates',
    'M02_correct_classification': 'Correct Classification',
    'M04_correct_classification': 'Correct Classification',
    'M05_correct_classification': 'Correct Classification',
    'M06_hierarchy_correct': 'Hierarchy Correct',
    'M06_levels_appropriate': 'Levels Appropriate',
    'M07_attributes_from_listing': 'Attributes From Listing',
    'M07_no_hallucination': 'No Hallucination',
    'M08_ranks_assigned': 'Ranks Assigned',
    'M08_ranks_logical': 'Ranks Logical',
    'M09_captures_core_purpose': 'Captures Core Purpose',
    'M10_invalid_correctly_flagged': 'Invalid Correctly Flagged',
    'M11_critical_not_missed': 'Critical Not Missed',
    'M12_correct_classification': 'Correct Classification',
    'M13_same_type_correct': 'Same Type Correct',
    'M14_same_use_correct': 'Same Use Correct',
    'M15_substitute_correct': 'Substitute Correct',
    'M16_complementary_correct': 'Complementary Correct',
}

# Suggestion templates based on rubric patterns
SUGGESTION_TEMPLATES = {
    'no_hallucination': "Add stricter validation rules to prevent extracting non-existent entities",
    'no_duplicates': "Add deduplication step in post-processing or prompt instructions",
    'correct_classification': "Add more examples of edge cases in the prompt",
    'brand_extracted': "Add explicit examples of brand extraction patterns",
    'amazon_test': "Strengthen Amazon Test instructions with step-by-step guidance",
    'from_listing': "Add rule to only use information explicitly present in the listing",
    'hierarchy': "Add examples of correct hierarchy structures",
    'ranks': "Add clearer ranking criteria with examples",
    'default': "Review and improve prompt instructions for this criterion",
}


def load_yaml_file(filepath: Path) -> dict:
    """Load YAML file, return empty dict if not exists."""
    if not filepath.exists():
        return {}
    with open(filepath) as f:
        return yaml.safe_load(f) or {}


def get_suggestion_template(rubric_id: str) -> str:
    """Get appropriate suggestion template based on rubric ID."""
    rubric_lower = rubric_id.lower()

    for key, template in SUGGESTION_TEMPLATES.items():
        if key in rubric_lower:
            return template

    return SUGGESTION_TEMPLATES['default']


def get_priority(pass_rate: float) -> str:
    """Determine priority based on pass rate."""
    if pass_rate < CRITICAL_THRESHOLD:
        return 'high'
    elif pass_rate < WARNING_THRESHOLD:
        return 'medium'
    elif pass_rate < GOOD_THRESHOLD:
        return 'low'
    return 'none'


def generate_suggestions(rubric_breakdown: dict, module: str) -> List[dict]:
    """
    Generate automatic suggestions based on rubric breakdown.

    Returns list of suggestions for rubrics below GOOD_THRESHOLD.
    """
    suggestions = []

    for rubric_id, stats in rubric_breakdown.items():
        pass_rate = stats.get('pass_rate', 0)
        priority = get_priority(pass_rate)

        if priority == 'none':
            continue

        display_name = RUBRIC_DISPLAY_NAMES.get(rubric_id, rubric_id)
        suggestion_text = get_suggestion_template(rubric_id)

        suggestions.append({
            'rubric_id': rubric_id,
            'rubric_name': display_name,
            'pass_rate': pass_rate,
            'priority': priority,
            'suggestion': suggestion_text,
            'status': 'pending',
        })

    # Sort by priority (high first) then by pass_rate (lowest first)
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    suggestions.sort(key=lambda x: (priority_order.get(x['priority'], 3), x['pass_rate']))

    return suggestions


def compare_versions(prev_breakdown: dict, curr_breakdown: dict) -> List[dict]:
    """
    Compare rubric breakdowns between versions to identify improvements.

    Returns list of improvements (rubrics that got better).
    """
    improvements = []

    for rubric_id, curr_stats in curr_breakdown.items():
        curr_rate = curr_stats.get('pass_rate', 0)
        prev_rate = prev_breakdown.get(rubric_id, {}).get('pass_rate', 0)

        if curr_rate > prev_rate:
            delta = curr_rate - prev_rate
            improvements.append({
                'rubric_id': rubric_id,
                'rubric_name': RUBRIC_DISPLAY_NAMES.get(rubric_id, rubric_id),
                'previous_rate': prev_rate,
                'current_rate': curr_rate,
                'improvement': f"+{delta:.1f}%",
            })

    # Sort by improvement amount (biggest first)
    improvements.sort(key=lambda x: x['current_rate'] - x['previous_rate'], reverse=True)

    return improvements


def extract_version_number(version_str: str) -> int:
    """Extract numeric version from string like 'v1', 'v2', etc."""
    if not version_str:
        return 0
    try:
        return int(version_str.lower().replace('v', ''))
    except ValueError:
        return 0


def build_improvement_analysis(all_runs: dict, verbose: bool = False) -> dict:
    """
    Build improvement analysis from all_runs data.

    Structure:
    {
        "m01": {
            "versions": {
                "v1": {
                    "models": {
                        "gpt-4o-mini": {
                            "run_id": "...",
                            "pass_rate": 57.33,
                            "rubric_breakdown": {...},
                            "suggestions": [...],
                            "improvements_from_prev": [...]
                        }
                    }
                }
            }
        }
    }
    """
    runs = all_runs.get('runs', {})

    # Group runs by module -> version -> model
    grouped = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for run_id, run in runs.items():
        module = run.get('module', '').lower()
        version = run.get('prompt_version', 'v1').lower()
        model = run.get('model', 'unknown')

        if not module or not run.get('rubric_breakdown'):
            continue

        grouped[module][version][model].append({
            'run_id': run_id,
            'run': run,
        })

    # Build analysis structure
    analysis = {'modules': {}}

    for module in sorted(grouped.keys()):
        module_data = {'versions': {}}
        versions = grouped[module]

        # Sort versions numerically
        sorted_versions = sorted(versions.keys(), key=extract_version_number)

        prev_version_data = {}  # model -> rubric_breakdown

        for version in sorted_versions:
            version_data = {'models': {}}
            models = versions[version]

            for model, run_list in models.items():
                # Take the latest run for this model (by timestamp)
                run_list.sort(key=lambda x: x['run'].get('timestamp', ''), reverse=True)
                latest = run_list[0]
                run = latest['run']

                rubric_breakdown = run.get('rubric_breakdown', {})

                # Generate suggestions
                suggestions = generate_suggestions(rubric_breakdown, module)

                # Compare with previous version (same model)
                improvements = []
                if model in prev_version_data:
                    improvements = compare_versions(
                        prev_version_data[model],
                        rubric_breakdown
                    )

                version_data['models'][model] = {
                    'run_id': latest['run_id'],
                    'pass_rate': run.get('pass_rate', 0),
                    'match_rate': run.get('match_rate', 0),
                    'total_samples': run.get('total_samples', 0),
                    'timestamp': run.get('timestamp', ''),
                    'rubric_breakdown': rubric_breakdown,
                    'suggestions': suggestions,
                    'improvements_from_prev': improvements,
                }

                # Store for next version comparison
                prev_version_data[model] = rubric_breakdown

            module_data['versions'][version] = version_data

        analysis['modules'][module] = module_data

    return analysis


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate improvement analysis from judge results")
    parser.add_argument('--verbose', '-v', action='store_true', help="Verbose output")
    args = parser.parse_args()

    print("=" * 60)
    print("📊 Generate Improvement Analysis")
    print("=" * 60)

    # Load all_runs
    if not ALL_RUNS_FILE.exists():
        print(f"  ✗ {ALL_RUNS_FILE} not found!")
        print("    Run aggregate_results.py first.")
        return

    all_runs = load_yaml_file(ALL_RUNS_FILE)
    runs = all_runs.get('runs', {})
    print(f"  Loaded {len(runs)} runs from all_runs.yaml")

    # Check for rubric_breakdown
    runs_with_breakdown = sum(1 for r in runs.values() if r.get('rubric_breakdown'))
    print(f"  Runs with rubric_breakdown: {runs_with_breakdown}")

    if runs_with_breakdown == 0:
        print("\n⚠️  No runs have rubric_breakdown!")
        print("   Re-run aggregate_results.py to add rubric_breakdown to existing runs.")
        return

    # Build analysis
    analysis = build_improvement_analysis(all_runs, args.verbose)

    # Add metadata
    analysis['version'] = '1.0'
    analysis['generated_at'] = datetime.now().isoformat()
    analysis['thresholds'] = {
        'critical': CRITICAL_THRESHOLD,
        'warning': WARNING_THRESHOLD,
        'good': GOOD_THRESHOLD,
    }

    # Save
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(IMPROVEMENT_ANALYSIS_FILE, 'w') as f:
        yaml.dump(analysis, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    # Summary
    modules = analysis.get('modules', {})
    total_suggestions = 0
    for mod_data in modules.values():
        for ver_data in mod_data.get('versions', {}).values():
            for model_data in ver_data.get('models', {}).values():
                total_suggestions += len(model_data.get('suggestions', []))

    print(f"\n✅ Generated improvement_analysis.yaml")
    print(f"   - Modules: {len(modules)}")
    print(f"   - Total suggestions: {total_suggestions}")
    print(f"   - Output: {IMPROVEMENT_ANALYSIS_FILE}")

    if args.verbose:
        print("\n📋 Module Summary:")
        for module, mod_data in sorted(modules.items()):
            versions = list(mod_data.get('versions', {}).keys())
            print(f"  {module}: {len(versions)} versions ({', '.join(versions)})")


if __name__ == "__main__":
    main()
