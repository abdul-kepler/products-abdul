#!/usr/bin/env python3
"""
Generate Dashboard Data - Level 3 Data Generator

Converts aggregated YAML data into JavaScript files for the dashboard.
This script reads from Level 2 (data/*.yaml) and generates Level 3 (dashboards/*.js).

The dashboard is completely independent - it only reads these .js files.

Usage:
    python generate_dashboard_data.py              # Generate all JS files
    python generate_dashboard_data.py --verbose    # Detailed output
"""

import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Paths
SCRIPT_DIR = Path(__file__).parent
TRACKING_DASHBOARD = SCRIPT_DIR.parent
DATA_DIR = TRACKING_DASHBOARD / "data"
DASHBOARDS_DIR = TRACKING_DASHBOARD / "dashboards"

# Input files (Level 2)
ALL_RUNS_FILE = DATA_DIR / "all_runs.yaml"
KNOWN_ISSUES_FILE = DATA_DIR / "known_issues.yaml"
IMPROVEMENT_HISTORY_FILE = DATA_DIR / "improvement_history.yaml"
APPLIED_IMPROVEMENTS_FILE = DATA_DIR / "applied_improvements.yaml"
IMPROVEMENT_ANALYSIS_FILE = DATA_DIR / "improvement_analysis.yaml"

# Output files (Level 3)
MODULES_DATA_JS = DASHBOARDS_DIR / "modules_data.js"
KNOWN_ISSUES_JS = DASHBOARDS_DIR / "known_issues_data.js"
IMPROVEMENT_ANALYSIS_JS = DASHBOARDS_DIR / "improvement_analysis_data.js"


# Module folder mapping for experiment_results paths
MODULE_FOLDER_MAP = {
    'm01': 'M01_ExtractOwnBrandEntities',
    'm01a': 'M01A_ExtractOwnBrandVariations',
    'm01b': 'M01B_ExtractBrandRelatedTerms',
    'm02': 'M02_ClassifyOwnBrandKeywords',
    'm02b': 'M02B_ClassifyOwnBrandKeywords_PathB',
    'm04': 'M04_ClassifyCompetitorBrandKeywords',
    'm04b': 'M04B_ClassifyCompetitorBrandKeywords_PathB',
    'm05': 'M05_ClassifyNonBrandedKeywords',
    'm05b': 'M05B_ClassifyNonBrandedKeywords_PathB',
    'm06': 'M06_GenerateProductTypeTaxonomy',
    'm07': 'M07_ExtractProductAttributes',
    'm08': 'M08_AssignAttributeRanks',
    'm09': 'M09_IdentifyPrimaryIntendedUse',
    'm10': 'M10_ValidatePrimaryIntendedUse',
    'm11': 'M11_IdentifyHardConstraints',
    'm12': 'M12_HardConstraintViolationCheck',
    'm12b': 'M12B_CombinedClassification',
    'm13': 'M13_ProductTypeCheck',
    'm14': 'M14_PrimaryUseCheckSameType',
    'm15': 'M15_SubstituteCheck',
    'm16': 'M16_ComplementaryCheck',
}


def load_yaml_file(filepath: Path) -> dict:
    """Load YAML file, return empty dict if not exists."""
    if not filepath.exists():
        return {}
    with open(filepath) as f:
        return yaml.safe_load(f) or {}


def transform_runs_for_dashboard(all_runs: dict) -> List[dict]:
    """
    Transform all_runs.yaml format to dashboard-compatible progressData format.

    Dashboard expects:
    - module: "m01_v1" (combined module + version for filtering)
    - All other fields flat
    """
    runs = all_runs.get('runs', {})
    progress_data = []

    for run_id, run in runs.items():
        # Create dashboard-compatible entry
        entry = {
            'run_id': run_id,
            'module': f"{run['module']}_{run['prompt_version']}",  # Combined for filtering
            'module_base': run['module'],
            'prompt_version': run['prompt_version'],
            'model': run['model'],
            'module_type': run.get('module_type', 'unknown'),

            # Metrics
            'pass_rate': run.get('pass_rate', 0),
            'match_rate': run.get('match_rate', 0),
            'total_evaluations': run.get('total_samples', 0),
            'summary': run.get('summary', {}),

            # Braintrust metadata
            'dataset_name': run.get('dataset_name', ''),
            'dataset_id': run.get('dataset_id', ''),
            'prompt_id': run.get('prompt_id', ''),
            'braintrust_id': run.get('braintrust_experiment_id', ''),
            'temperature': run.get('temperature', 0),

            # Source files
            'data_source': run.get('csv_file', ''),
            'judge_file': run.get('judge_file', ''),

            # Timestamps
            'timestamp': run.get('timestamp', ''),
            'created': run.get('timestamp', ''),
        }

        progress_data.append(entry)

    # Sort by module, then version, then timestamp
    progress_data.sort(key=lambda x: (x['module_base'], x['prompt_version'], x['timestamp']))

    return progress_data


def extract_binary_metrics(all_runs: dict) -> Dict[str, Any]:
    """
    Extract binary metrics from runs into separate dict for dashboard.

    Key format: run_id (e.g., m02_v1_gpt4omini_220126)
    """
    runs = all_runs.get('runs', {})
    binary_metrics = {}

    for run_id, run in runs.items():
        metrics = run.get('binary_metrics')
        # Include if metrics exist (regardless of module_type)
        if metrics:
            binary_metrics[run_id] = metrics

    return binary_metrics


def generate_modules_data_js(verbose: bool = False) -> bool:
    """Generate modules_data.js from all data sources."""

    print("📦 Generating modules_data.js...")

    # Load all data sources
    all_runs = load_yaml_file(ALL_RUNS_FILE)
    improvement_history = load_yaml_file(IMPROVEMENT_HISTORY_FILE)
    applied_improvements = load_yaml_file(APPLIED_IMPROVEMENTS_FILE)

    # Transform for dashboard
    progress_data = transform_runs_for_dashboard(all_runs)
    binary_metrics = extract_binary_metrics(all_runs)

    if verbose:
        print(f"  - Progress data entries: {len(progress_data)}")
        print(f"  - Binary metrics entries: {len(binary_metrics)}")
        print(f"  - Improvement history: {len(improvement_history)}")
        print(f"  - Applied improvements: {len(applied_improvements)}")

    # Generate JavaScript content
    js_content = f'''/**
 * Shared data for module dashboards
 * Auto-generated by generate_dashboard_data.py
 * Generated: {datetime.now().isoformat()}
 *
 * Data sources:
 *   - all_runs.yaml -> progressData, binaryMetrics
 *   - improvement_history.yaml -> improvementHistory
 *   - applied_improvements.yaml -> appliedData
 *
 * Usage in HTML:
 *   <script src="modules_data.js"></script>
 *   <script>
 *     const m01Runs = progressData.filter(d => d.module_base === 'm01');
 *   </script>
 */

// All evaluation runs (judge results)
const progressData = {json.dumps(progress_data, indent=2)};

// Suggestions data (from improvement_suggestions.json if exists)
const suggestionsData = [];

// Applied improvements by module/version
const appliedData = {json.dumps(applied_improvements, indent=2)};

// Improvement history by module
const improvementHistory = {json.dumps(improvement_history, indent=2)};

// Module folder mapping for experiment_results paths
const MODULE_FOLDER_MAP = {json.dumps(MODULE_FOLDER_MAP, indent=2)};

// Binary classification metrics (for classifier modules)
const binaryMetrics = {json.dumps(binary_metrics, indent=2)};

// Summary statistics
const dashboardStats = {{
  totalRuns: {len(progress_data)},
  lastUpdated: "{datetime.now().isoformat()}",
  modules: {json.dumps(list(set(r['module_base'] for r in progress_data)))},
  models: {json.dumps(list(set(r['model'] for r in progress_data)))}
}};
'''

    # Write to file
    DASHBOARDS_DIR.mkdir(parents=True, exist_ok=True)
    with open(MODULES_DATA_JS, 'w') as f:
        f.write(js_content)

    print(f"  ✓ Generated {MODULES_DATA_JS}")
    print(f"    - {len(progress_data)} runs")
    print(f"    - {len(binary_metrics)} binary metrics")

    return True


def generate_known_issues_js(verbose: bool = False) -> bool:
    """Generate known_issues_data.js from known_issues.yaml."""

    print("📦 Generating known_issues_data.js...")

    known_issues = load_yaml_file(KNOWN_ISSUES_FILE)

    if not known_issues:
        print("  ⚠ No known_issues.yaml found, creating empty file")
        known_issues = {}

    # Extract modules dict for flat access (knownIssuesData.m02 instead of knownIssuesData.modules.m02)
    modules_data = known_issues.get('modules', {})

    js_content = f'''/**
 * Known Issues Data for Module Dashboards
 * Auto-generated by generate_dashboard_data.py
 * Generated: {datetime.now().isoformat()}
 *
 * Access: knownIssuesData['m02'] or knownIssuesData.m02
 */

const knownIssuesData = {json.dumps(modules_data, indent=2)};
'''

    with open(KNOWN_ISSUES_JS, 'w') as f:
        f.write(js_content)

    print(f"  ✓ Generated {KNOWN_ISSUES_JS}")

    return True


def generate_improvement_analysis_js(verbose: bool = False) -> bool:
    """Generate improvement_analysis_data.js from improvement_analysis.yaml."""

    print("📦 Generating improvement_analysis_data.js...")

    improvement_analysis = load_yaml_file(IMPROVEMENT_ANALYSIS_FILE)

    if not improvement_analysis:
        print("  ⚠ No improvement_analysis.yaml found")
        print("    Run generate_improvement_analysis.py first.")
        return False

    modules = improvement_analysis.get('modules', {})
    thresholds = improvement_analysis.get('thresholds', {})

    if verbose:
        print(f"  - Modules: {len(modules)}")

    js_content = f'''/**
 * Improvement Analysis Data for Module Dashboards
 * Auto-generated by generate_dashboard_data.py
 * Generated: {datetime.now().isoformat()}
 *
 * Structure:
 *   improvementAnalysis.modules.m01.versions.v1.models['gpt-4o-mini']
 *     -> rubric_breakdown, suggestions, improvements_from_prev
 *
 * Usage:
 *   const m01Data = improvementAnalysis.modules.m01;
 *   const versions = Object.keys(m01Data.versions);
 *   const models = Object.keys(m01Data.versions.v1.models);
 */

const improvementAnalysis = {{
  modules: {json.dumps(modules, indent=2)},
  thresholds: {json.dumps(thresholds, indent=2)},
  generatedAt: "{datetime.now().isoformat()}"
}};
'''

    with open(IMPROVEMENT_ANALYSIS_JS, 'w') as f:
        f.write(js_content)

    print(f"  ✓ Generated {IMPROVEMENT_ANALYSIS_JS}")
    print(f"    - {len(modules)} modules")

    return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate dashboard JavaScript files")
    parser.add_argument('--verbose', '-v', action='store_true', help="Verbose output")
    args = parser.parse_args()

    print("=" * 60)
    print("🎨 Generate Dashboard Data")
    print("=" * 60)
    print(f"  Data dir: {DATA_DIR}")
    print(f"  Output dir: {DASHBOARDS_DIR}")

    # Check if source files exist
    if not ALL_RUNS_FILE.exists():
        print(f"\n⚠️  {ALL_RUNS_FILE} not found!")
        print("   Run aggregate_results.py first.")
        return

    # Generate JavaScript files
    generate_modules_data_js(args.verbose)
    generate_known_issues_js(args.verbose)
    generate_improvement_analysis_js(args.verbose)

    print("\n" + "=" * 60)
    print("✅ Dashboard data generation complete!")
    print("=" * 60)
    print(f"\nOpen dashboard: file://{DASHBOARDS_DIR}/tracking_dashboard.html")
    print(f"Or run: python -m http.server 8030 --directory {DASHBOARDS_DIR}")


if __name__ == "__main__":
    main()
