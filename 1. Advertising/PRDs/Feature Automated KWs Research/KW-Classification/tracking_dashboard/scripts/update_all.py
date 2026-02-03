#!/usr/bin/env python3
"""
Update All - Orchestrator for Dashboard Data Pipeline

Runs all aggregation and generation scripts in the correct order:
1. aggregate_results.py    - Collect judge results → all_runs.yaml
2. aggregate_known_issues.py - Extract errors → known_issues.yaml
3. generate_dashboard_data.py - Generate JS files → dashboards/*.js

Usage:
    python update_all.py              # Full pipeline
    python update_all.py --verbose    # Detailed output
    python update_all.py --skip-js    # Skip JS generation (data only)
    python update_all.py --dry-run    # Show what would run
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Tuple

# Paths
SCRIPT_DIR = Path(__file__).parent
TRACKING_DASHBOARD = SCRIPT_DIR.parent
DATA_DIR = TRACKING_DASHBOARD / "data"
DASHBOARDS_DIR = TRACKING_DASHBOARD / "dashboards"

# Scripts to run in order
SCRIPTS = [
    ('aggregate_results.py', 'Collecting judge results'),
    ('aggregate_known_issues.py', 'Extracting known issues'),
    ('calculate_costs.py', 'Calculating experiment costs'),
    ('aggregate_rubrics.py', 'Aggregating rubric statistics'),
    ('generate_improvement_analysis.py', 'Generating improvement analysis'),
    ('generate_dashboard_data.py', 'Generating dashboard JS files'),
]


def run_script(script_name: str, verbose: bool = False, dry_run: bool = False) -> Tuple[bool, str]:
    """
    Run a script and return success status and output.
    """
    script_path = SCRIPT_DIR / script_name

    if not script_path.exists():
        return False, f"Script not found: {script_path}"

    cmd = [sys.executable, str(script_path)]
    if verbose:
        cmd.append('--verbose')

    if dry_run:
        return True, f"Would run: {' '.join(cmd)}"

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=SCRIPT_DIR.parent.parent,  # Project root
        )

        output = result.stdout
        if result.returncode != 0:
            output += f"\nSTDERR:\n{result.stderr}"
            return False, output

        return True, output

    except Exception as e:
        return False, f"Error running {script_name}: {e}"


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Run full dashboard data pipeline")
    parser.add_argument('--verbose', '-v', action='store_true', help="Verbose output")
    parser.add_argument('--skip-js', action='store_true', help="Skip JS file generation")
    parser.add_argument('--dry-run', action='store_true', help="Show what would run without executing")
    args = parser.parse_args()

    print("=" * 70)
    print("🚀 Dashboard Data Pipeline")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Data dir: {DATA_DIR}")
    print(f"Output dir: {DASHBOARDS_DIR}")
    print()

    scripts_to_run = SCRIPTS.copy()
    if args.skip_js:
        scripts_to_run = [s for s in scripts_to_run if s[0] != 'generate_dashboard_data.py']

    results = []

    for script_name, description in scripts_to_run:
        print(f"▶ {description}...")
        print(f"  Running: {script_name}")

        success, output = run_script(script_name, args.verbose, args.dry_run)
        results.append((script_name, success, output))

        if success:
            print(f"  ✓ Completed")
            if args.verbose:
                # Show key lines from output
                for line in output.split('\n'):
                    if line.strip() and ('✓' in line or '✗' in line or 'Generated' in line or 'Saved' in line):
                        print(f"    {line.strip()}")
        else:
            print(f"  ✗ Failed!")
            print(f"  Output:\n{output}")
            break

        print()

    # Summary
    print("=" * 70)
    successful = sum(1 for _, s, _ in results if s)
    failed = len(results) - successful

    if failed == 0:
        print(f"✅ Pipeline completed successfully! ({successful}/{len(scripts_to_run)} scripts)")

        # Show generated files
        print("\n📁 Generated files:")
        for yaml_file in DATA_DIR.glob("*.yaml"):
            size = yaml_file.stat().st_size
            print(f"  - {yaml_file.name} ({size:,} bytes)")

        for js_file in DASHBOARDS_DIR.glob("*_data.js"):
            size = js_file.stat().st_size
            print(f"  - dashboards/{js_file.name} ({size:,} bytes)")

        print(f"\n🌐 Dashboard URL:")
        print(f"  file://{DASHBOARDS_DIR}/tracking_dashboard.html")
        print(f"  Or: python -m http.server 8030 --directory {DASHBOARDS_DIR}")
    else:
        print(f"❌ Pipeline failed! ({successful}/{len(scripts_to_run)} scripts completed)")
        print("  Check the error output above.")
        sys.exit(1)

    print("=" * 70)


if __name__ == "__main__":
    main()
