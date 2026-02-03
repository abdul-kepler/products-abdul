#!/usr/bin/env python3
"""
Dashboard Update Orchestrator

Runs all necessary scripts to update the dashboard with new experiment results.

Usage:
    python update_dashboard.py              # Full update
    python update_dashboard.py --quick      # Skip binary metrics (faster)
    python update_dashboard.py --serve      # Update and start HTTP server
"""

import subprocess
import sys
import json
import yaml
from pathlib import Path
from datetime import datetime

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
DATA_DIR = PROJECT_DIR / "data"
DASHBOARDS_DIR = PROJECT_DIR / "dashboards"

# Kate's evaluation folder (where judge_results are)
KATE_EVAL_DIR = PROJECT_DIR.parent / "evaluation_KD" / "evaluation_experimentV5"
JUDGE_RESULTS_DIR = KATE_EVAL_DIR / "judge_results"

# Experiment results (CSV files from models)
EXPERIMENT_RESULTS_DIR = PROJECT_DIR.parent / "experiment_results"


def run_script(script_name: str, *args) -> bool:
    """Run a Python script and return success status."""
    script_path = SCRIPT_DIR / script_name
    if not script_path.exists():
        print(f"  ✗ Script not found: {script_path}")
        return False

    cmd = [sys.executable, str(script_path)] + list(args)
    print(f"  Running: {script_name} {' '.join(args)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            print(f"  ✗ Error: {result.stderr[:200]}")
            return False
        return True
    except subprocess.TimeoutExpired:
        print(f"  ✗ Timeout")
        return False
    except Exception as e:
        print(f"  ✗ Exception: {e}")
        return False


def update_progress_history() -> int:
    """Update progress_history.yaml with new judge results."""
    print("\n📊 Updating progress history...")

    history_file = DATA_DIR / "progress_history.yaml"

    # Load existing history
    if history_file.exists():
        with open(history_file) as f:
            history = yaml.safe_load(f) or {}
    else:
        history = {}

    existing_runs = {r.get('run_id') for r in history.get('runs', [])}

    # Find new judge results
    new_count = 0
    if JUDGE_RESULTS_DIR.exists():
        for json_file in sorted(JUDGE_RESULTS_DIR.glob("*_judge_*.json")):
            run_id = json_file.stem
            if run_id not in existing_runs:
                # Parse and add to history
                try:
                    with open(json_file) as f:
                        data = json.load(f)

                    # Extract metadata
                    meta = data.get('metadata', {})
                    summary = data.get('summary', {})

                    total = summary.get('pass', 0) + summary.get('fail', 0) + summary.get('error', 0)
                    pass_rate = (summary.get('pass', 0) / total * 100) if total > 0 else 0

                    run_entry = {
                        'run_id': run_id,
                        'module': meta.get('module', run_id.split('_judge')[0]),
                        'prompt_version': meta.get('prompt_version', 'v1'),
                        'model': meta.get('model', 'unknown'),
                        'pass_rate': round(pass_rate, 1),
                        'match_rate': meta.get('match_rate', 0),
                        'summary': summary,
                        'timestamp': meta.get('timestamp', datetime.now().isoformat()),
                        'data_source': meta.get('data_source', ''),
                    }

                    if 'runs' not in history:
                        history['runs'] = []
                    history['runs'].append(run_entry)
                    new_count += 1
                    print(f"    + Added: {run_id}")

                except Exception as e:
                    print(f"    ✗ Error parsing {json_file.name}: {e}")

    # Save updated history
    if new_count > 0:
        with open(history_file, 'w') as f:
            yaml.dump(history, f, default_flow_style=False, sort_keys=False)
        print(f"  ✓ Added {new_count} new runs to progress_history.yaml")
    else:
        print(f"  ✓ No new judge results found")

    return new_count


def update_binary_metrics() -> bool:
    """Update binary_metrics.json from CSV results."""
    print("\n📈 Updating binary metrics...")
    return run_script("score_binary_classifiers.py")


def generate_modules_data() -> bool:
    """Generate modules_data.js from progress_history and binary_metrics."""
    print("\n📦 Generating modules_data.js...")

    # Load progress history
    history_file = DATA_DIR / "progress_history.yaml"
    if history_file.exists():
        with open(history_file) as f:
            history = yaml.safe_load(f) or {}
        progress_data = history.get('runs', [])
    else:
        progress_data = []

    # Load other data files
    suggestions_data = []
    suggestions_file = DATA_DIR / "improvement_suggestions.json"
    if suggestions_file.exists():
        with open(suggestions_file) as f:
            suggestions_data = json.load(f)

    applied_data = {}
    applied_file = DATA_DIR / "applied_improvements.yaml"
    if applied_file.exists():
        with open(applied_file) as f:
            applied_data = yaml.safe_load(f) or {}

    improvement_history = {}
    history_file = DATA_DIR / "improvement_history.yaml"
    if history_file.exists():
        with open(history_file) as f:
            improvement_history = yaml.safe_load(f) or {}

    # Load binary metrics
    binary_metrics = {}
    metrics_file = DASHBOARDS_DIR / "binary_metrics.json"
    if metrics_file.exists():
        with open(metrics_file) as f:
            binary_metrics = json.load(f)

    # Generate modules_data.js
    js_content = '''/**
 * Shared data for module dashboards
 * Auto-generated by update_dashboard.py
 * Generated: ''' + datetime.now().isoformat() + '''
 */

const progressData = ''' + json.dumps(progress_data, indent=2) + ''';

const suggestionsData = ''' + json.dumps(suggestions_data, indent=2) + ''';

const appliedData = ''' + json.dumps(applied_data, indent=2) + ''';

const improvementHistory = ''' + json.dumps(improvement_history, indent=2) + ''';

const MODULE_FOLDER_MAP = {
    'm01': 'M01_ExtractOwnBrandEntities',
    'm01a': 'M01A_ExtractOwnBrandVariations_PathB',
    'm01b': 'M01B_ExtractBrandRelatedTerms_PathB',
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
    'm13': 'M13_ProductTypeCheck',
    'm14': 'M14_PrimaryUseCheckSameType',
    'm15': 'M15_SubstituteCheck',
    'm16': 'M16_ComplementaryCheck',
};

// Binary classification metrics for classifier modules
const binaryMetrics = ''' + json.dumps(binary_metrics, indent=2) + ''';
'''

    output_file = DASHBOARDS_DIR / "modules_data.js"
    with open(output_file, 'w') as f:
        f.write(js_content)

    print(f"  ✓ Generated {output_file}")
    print(f"    - {len(progress_data)} progress runs")
    print(f"    - {len(binary_metrics)} binary metrics")
    return True


def regenerate_dashboards() -> bool:
    """Regenerate HTML dashboards."""
    print("\n🎨 Regenerating dashboards...")
    success = run_script("generate_progress_dashboard.py", "--no-open")
    return success


def start_server(port: int = 8030):
    """Start HTTP server."""
    print(f"\n🌐 Starting server on http://localhost:{port}/")
    import os
    os.chdir(DASHBOARDS_DIR)
    subprocess.run([sys.executable, "-m", "http.server", str(port)])


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Update Dashboard")
    parser.add_argument("--quick", action="store_true", help="Skip binary metrics update")
    parser.add_argument("--serve", action="store_true", help="Start HTTP server after update")
    parser.add_argument("--port", type=int, default=8030, help="Server port")
    parser.add_argument("--sync-judge", action="store_true", help="Sync new judge results to progress_history (use with caution)")
    args = parser.parse_args()

    print("=" * 60)
    print("🚀 Dashboard Update Orchestrator")
    print("=" * 60)
    print(f"Project: {PROJECT_DIR}")
    print(f"Data:    {DATA_DIR}")
    print(f"Output:  {DASHBOARDS_DIR}")

    # Step 1: Update progress history from judge results (OPTIONAL)
    if args.sync_judge:
        new_runs = update_progress_history()
    else:
        print("\n📊 Skipping judge sync (use --sync-judge to enable)")

    # Step 2: Update binary metrics (optional)
    if not args.quick:
        update_binary_metrics()
    else:
        print("\n📈 Skipping binary metrics (--quick mode)")

    # Step 3: Generate modules_data.js
    generate_modules_data()

    # Step 4: Regenerate dashboards
    regenerate_dashboards()

    print("\n" + "=" * 60)
    print("✅ Dashboard update complete!")
    print("=" * 60)
    print(f"\nOpen: http://localhost:{args.port}/tracking_dashboard.html")
    print(f"      http://localhost:{args.port}/modules/m12.html")

    if args.serve:
        start_server(args.port)


if __name__ == "__main__":
    main()
