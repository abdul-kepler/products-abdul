#!/usr/bin/env python3
"""
Run judges for all modules and validate them.
Excludes M03 (replaced by M01) and M10 (hard_constraints issues).
"""

import subprocess
import sys
from pathlib import Path

# Modules to process (excluding M03 and M10)
MODULES = [
    "m01", "m01a", "m01b", "m02", "m04", "m05", "m06",
    "m07", "m08", "m09", "m11", "m12", "m12b", "m13",
    "m14", "m15", "m16"
]

RESULTS_DIR = Path(__file__).parent.parent / "experiment_results"
VENV_ACTIVATE = "source /home/kostya/PycharmProjects/PythonProject/dspy_prompt_optimizers/.venv_braintrust/bin/activate"


def find_latest_experiment(module: str) -> Path:
    """Find latest experiment results for a module."""
    pattern = f"{module}_results_*.jsonl"
    files = sorted(RESULTS_DIR.glob(pattern), reverse=True)
    if not files:
        raise FileNotFoundError(f"No experiment results for {module}")
    return files[0]


def run_judge(module: str, results_file: Path, samples: int = 10):
    """Run judge for a module."""
    cmd = f"{VENV_ACTIVATE} && python scripts/run_judge.py --module {module} --results-file {results_file} --samples {samples}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=RESULTS_DIR.parent)
    return result.returncode == 0, result.stdout, result.stderr


def main():
    print("=" * 70)
    print("RUNNING ALL JUDGES")
    print("=" * 70)

    results = {}

    for module in MODULES:
        print(f"\n{'='*50}")
        print(f"Processing {module.upper()}")
        print("=" * 50)

        try:
            exp_file = find_latest_experiment(module)
            print(f"Experiment: {exp_file.name}")

            success, stdout, stderr = run_judge(module, exp_file.name)

            if success:
                # Extract summary from output
                lines = stdout.split('\n')
                for i, line in enumerate(lines):
                    if 'PASS:' in line or 'Average Score' in line:
                        print(line)
                results[module] = "✅ SUCCESS"
            else:
                print(f"❌ FAILED: {stderr[:200]}")
                results[module] = "❌ FAILED"

        except FileNotFoundError as e:
            print(f"⚠️ SKIPPED: {e}")
            results[module] = "⚠️ NO DATA"
        except Exception as e:
            print(f"❌ ERROR: {e}")
            results[module] = f"❌ ERROR: {e}"

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for module, status in results.items():
        print(f"  {module.upper():6} : {status}")


if __name__ == "__main__":
    main()
