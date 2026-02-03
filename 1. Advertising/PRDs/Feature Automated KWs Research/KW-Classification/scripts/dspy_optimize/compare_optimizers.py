#!/usr/bin/env python3
"""
Compare optimizer results across GEPA, MIPRO, COPRO for a module.

Usage:
    python compare_optimizers.py m01a           # Compare all optimizers for m01a
    python compare_optimizers.py --all          # Compare all modules
    python compare_optimizers.py --summary      # Show summary table
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

# Paths
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[1]
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"

import sys
sys.path.insert(0, str(SCRIPT_DIR))
from module_config import MODULE_CONFIGS


def load_gepa_results(module: str) -> list[dict]:
    """Load all GEPA experiment results for a module."""
    results = []
    module_dir = ARTIFACTS_DIR / "dspy_gepa" / module

    if not module_dir.exists():
        return results

    for provider_dir in module_dir.iterdir():
        if not provider_dir.is_dir():
            continue

        for exp_dir in provider_dir.iterdir():
            if not exp_dir.is_dir():
                continue

            optimized_file = exp_dir / "optimized.json"
            if optimized_file.exists():
                try:
                    data = json.loads(optimized_file.read_text())
                    results.append({
                        "optimizer": "gepa",
                        "provider": provider_dir.name,
                        "experiment": exp_dir.name,
                        "path": str(optimized_file),
                        "score": data.get("final_score"),
                        "baseline": data.get("initial_score"),
                        "improvement": (data.get("final_score", 0) - data.get("initial_score", 0))
                                      if data.get("final_score") and data.get("initial_score") else None,
                        "train_size": data.get("train_size"),
                        "val_size": data.get("val_size"),
                        "prompt_chars": len(data.get("optimized_prompt", "")),
                    })
                except Exception as e:
                    pass

    return results


def load_mipro_results(module: str) -> list[dict]:
    """Load MIPRO results for a module."""
    results = []
    module_dir = ARTIFACTS_DIR / "dspy_mipro" / module

    if not module_dir.exists():
        return results

    for provider_dir in module_dir.iterdir():
        if not provider_dir.is_dir():
            continue

        optimized_file = provider_dir / "optimized.json"
        if optimized_file.exists():
            try:
                data = json.loads(optimized_file.read_text())
                results.append({
                    "optimizer": "mipro",
                    "provider": provider_dir.name,
                    "experiment": "latest",
                    "path": str(optimized_file),
                    "score": data.get("score"),
                    "baseline": None,
                    "improvement": None,
                    "demos_count": len(data.get("demos", [])),
                    "instruction_chars": len(data.get("instruction", "")),
                })
            except Exception as e:
                pass

    return results


def load_copro_results(module: str) -> list[dict]:
    """Load COPRO results for a module."""
    results = []
    module_dir = ARTIFACTS_DIR / "dspy_copro" / module

    if not module_dir.exists():
        return results

    for provider_dir in module_dir.iterdir():
        if not provider_dir.is_dir():
            continue

        result_file = provider_dir / "copro_result.json"
        if result_file.exists():
            try:
                data = json.loads(result_file.read_text())
                results.append({
                    "optimizer": "copro",
                    "provider": provider_dir.name,
                    "experiment": "latest",
                    "path": str(result_file),
                    "score": None,  # COPRO doesn't return score
                    "baseline": None,
                    "improvement": None,
                    "breadth": data.get("breadth"),
                    "depth": data.get("depth"),
                    "instruction_chars": len(data.get("optimized_instruction", "")),
                })
            except Exception as e:
                pass

    return results


def compare_module(module: str) -> dict:
    """Compare all optimizer results for a module."""
    gepa = load_gepa_results(module)
    mipro = load_mipro_results(module)
    copro = load_copro_results(module)

    all_results = gepa + mipro + copro

    # Find best
    best = None
    best_score = -1

    for r in all_results:
        score = r.get("score")
        if score is not None and score > best_score:
            best_score = score
            best = r

    return {
        "module": module,
        "name": MODULE_CONFIGS.get(module, {}).get("name", "Unknown"),
        "gepa": gepa,
        "mipro": mipro,
        "copro": copro,
        "total_experiments": len(all_results),
        "best": best,
        "best_score": best_score if best_score > -1 else None,
    }


def find_best_gepa_experiment(experiments: list) -> Optional[dict]:
    """Find the best GEPA experiment based on score and improvement."""
    if not experiments:
        return None

    # Filter out failed experiments (score=0 or None)
    valid = [e for e in experiments if e.get("score") and e["score"] > 0]
    if not valid:
        return None

    # Sort by: 1) highest score, 2) best improvement, 3) largest val_size
    def sort_key(e):
        score = e.get("score") or 0
        imp = e.get("improvement") or 0
        val = e.get("val_size") or 0
        return (score, imp, val)

    return max(valid, key=sort_key)


def print_module_comparison(result: dict):
    """Print comparison for a single module."""
    print(f"\n{'='*60}")
    print(f"Module: {result['module']} ({result['name']})")
    print(f"{'='*60}")

    if result["total_experiments"] == 0:
        print("  No experiments found.")
        return

    # Find best GEPA experiment
    best_gepa = find_best_gepa_experiment(result["gepa"])

    # GEPA experiments
    if result["gepa"]:
        print(f"\n  GEPA ({len(result['gepa'])} experiments):")
        for r in sorted(result["gepa"], key=lambda x: x.get("score") or 0, reverse=True):
            score = r.get("score")
            baseline = r.get("baseline")
            imp = r.get("improvement")

            score_str = f"{score:.3f}" if score is not None else "?"
            baseline_str = f"{baseline:.3f}" if baseline is not None else "?"
            imp_str = f"+{imp:.1%}" if imp and imp > 0 else f"{imp:.1%}" if imp else ""

            # Mark best experiment
            is_best = best_gepa and r["experiment"] == best_gepa["experiment"]
            marker = " ⭐ RECOMMENDED" if is_best else ""

            print(f"    {r['experiment']}: score={score_str} (baseline={baseline_str}) {imp_str}{marker}")

    # MIPRO experiments
    if result["mipro"]:
        print(f"\n  MIPRO ({len(result['mipro'])} experiments):")
        for r in result["mipro"]:
            score = r.get("score", "?")
            demos = r.get("demos_count", 0)
            print(f"    {r['provider']}: score={score} demos={demos}")

    # COPRO experiments
    if result["copro"]:
        print(f"\n  COPRO ({len(result['copro'])} experiments):")
        for r in result["copro"]:
            print(f"    {r['provider']}: breadth={r.get('breadth')}, depth={r.get('depth')}")

    # Best
    if result["best"] and result["best_score"] is not None:
        print(f"\n  🏆 BEST: {result['best']['optimizer'].upper()} score={result['best_score']:.3f}")


def print_summary_table():
    """Print summary table of all modules."""
    print("\n" + "="*80)
    print("OPTIMIZER COMPARISON SUMMARY")
    print("="*80)
    print(f"{'Module':<8} {'Name':<35} {'GEPA':<10} {'MIPRO':<10} {'COPRO':<10} {'Best':<8}")
    print("-"*80)

    for module in sorted(MODULE_CONFIGS.keys()):
        result = compare_module(module)

        # Get best scores
        gepa_best = max([r.get("score", 0) or 0 for r in result["gepa"]], default=None)
        mipro_best = max([r.get("score", 0) or 0 for r in result["mipro"]], default=None)
        copro_score = "N/A"

        gepa_str = f"{gepa_best:.2f}" if gepa_best else "-"
        mipro_str = f"{mipro_best:.0f}%" if mipro_best else "-"

        best_opt = result["best"]["optimizer"] if result["best"] else "-"

        name = result["name"][:33] + ".." if len(result["name"]) > 35 else result["name"]

        print(f"{module:<8} {name:<35} {gepa_str:<10} {mipro_str:<10} {copro_score:<10} {best_opt:<8}")

    print("="*80)
    print("Note: GEPA scores are 0-1, MIPRO scores are 0-100%")


def update_latest_to_best(module: str, optimizer: str = "gepa") -> bool:
    """Update 'latest' folder to contain the best experiment results."""
    import shutil

    result = compare_module(module)

    if optimizer == "gepa":
        experiments = [e for e in result["gepa"] if e["experiment"] != "latest"]
        best = find_best_gepa_experiment(experiments)

        if not best:
            print(f"No valid experiments found for {module}")
            return False

        # Find the directories
        best_path = Path(best["path"])
        exp_dir = best_path.parent
        provider_dir = exp_dir.parent
        latest_dir = provider_dir / "latest"

        # Check if latest already has the same content
        latest_json = latest_dir / "optimized.json"
        if latest_json.exists():
            try:
                current = json.loads(latest_json.read_text())
                current_score = current.get("final_score")
                current_baseline = current.get("initial_score")
                best_score = best.get("score")
                best_baseline = best.get("baseline")

                # Compare both score and baseline (to detect same improvement)
                if current_score == best_score and current_baseline == best_baseline:
                    imp = best.get("improvement", 0) or 0
                    print(f"✓ {module}: latest already has best result (score={best_score:.3f}, imp={imp:+.1%})")
                    return True
            except:
                pass

        # Copy best experiment to latest
        if latest_dir.exists():
            shutil.rmtree(latest_dir)

        shutil.copytree(exp_dir, latest_dir)
        print(f"✅ {module}: updated latest with {exp_dir.name}")
        print(f"   Score: {best.get('score'):.3f}, Improvement: {best.get('improvement', 0):.1%}")
        return True

    return False


def main():
    parser = argparse.ArgumentParser(
        description="Compare optimizer results across GEPA, MIPRO, COPRO",
    )
    parser.add_argument("module", nargs="?", help="Module to compare (e.g., m01a)")
    parser.add_argument("--all", "-a", action="store_true", help="Compare all modules")
    parser.add_argument("--summary", "-s", action="store_true", help="Show summary table")
    parser.add_argument("--fix-latest", "-f", action="store_true",
                        help="Update 'latest' symlink to best experiment")

    args = parser.parse_args()

    if args.fix_latest:
        if args.module:
            update_latest_to_best(args.module)
        elif args.all:
            print("Updating 'latest' folders to best experiments...\n")
            for module in sorted(MODULE_CONFIGS.keys()):
                update_latest_to_best(module)
        else:
            print("Specify module or --all with --fix-latest")
        return

    if args.summary or (not args.module and not args.all):
        print_summary_table()
        return

    if args.all:
        for module in sorted(MODULE_CONFIGS.keys()):
            result = compare_module(module)
            print_module_comparison(result)
    elif args.module:
        if args.module not in MODULE_CONFIGS:
            print(f"Unknown module: {args.module}")
            print(f"Available: {', '.join(sorted(MODULE_CONFIGS.keys()))}")
            return
        result = compare_module(args.module)
        print_module_comparison(result)


if __name__ == "__main__":
    main()
