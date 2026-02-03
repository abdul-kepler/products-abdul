#!/usr/bin/env python3
"""
GEPA Optimizer for Text Generation Modules.

Uses evolutionary optimization with LLM reflection to improve prompts.

Supported modules:
- M09: Identify Primary Intended Use
- M10: Validate Primary Intended Use
- M01: Extract Own Brand Entities
- M01a: Extract Own Brand Variations
- M01b: Extract Brand Related Terms
- M06: Generate Product Type Taxonomy
- M07: Extract Product Attributes
- M08: Assign Attribute Ranks

Usage:
    python optimize_gepa.py m09
    python optimize_gepa.py m10 --budget 100 --reflection-model gpt-4o
    python optimize_gepa.py m01 --task-model gpt-4o-mini
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime

import gepa
from dotenv import load_dotenv

# Add parent directory for shared module_config
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from module_config import get_config, list_textgen_modules, PROJECT_ROOT
from evaluator import get_evaluator, MODULE_EVALUATORS

# Project paths
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts" / "dspy_gepa"

# Load environment
ENV_PATH = PROJECT_ROOT / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)

# At least one API key should be set
if not any([os.getenv("OPENAI_API_KEY"), os.getenv("GEMINI_API_KEY"), os.getenv("ANTHROPIC_API_KEY")]):
    raise RuntimeError("No API key set. Set OPENAI_API_KEY, GEMINI_API_KEY, or ANTHROPIC_API_KEY")




def load_dataset(path: Path, input_template: str, output_key: str, limit: int = None):
    """Load dataset and convert to GEPA format."""
    examples = []

    for i, line in enumerate(path.open()):
        if limit and i >= limit:
            break

        if not line.strip():
            continue

        rec = json.loads(line)
        inp = rec.get("input", {})
        exp = rec.get("expected", {})

        # Build input string from template
        try:
            input_str = input_template.format(**{k: inp.get(k, "") or "" for k in inp.keys()})
        except KeyError:
            # Fallback: just dump the input
            input_str = json.dumps(inp, ensure_ascii=False)

        # Get expected output - always serialize to JSON for consistent parsing
        # For modules with multiple output keys (M07, M08), dump entire expected object
        if output_key in ("variants", "attribute_table"):
            # M07 has variants/use_cases/audiences, M08 has attribute_table
            expected = json.dumps(exp, ensure_ascii=False)
        else:
            expected = exp.get(output_key, "")
            if isinstance(expected, (list, dict)):
                expected = json.dumps(expected, ensure_ascii=False)
            elif isinstance(expected, bool):
                # Boolean values need to be wrapped in JSON object for evaluator
                expected = json.dumps({output_key: expected}, ensure_ascii=False)
            elif expected is None:
                expected = json.dumps({output_key: None}, ensure_ascii=False)
            elif isinstance(expected, str):
                # Scalar string values (like "R", "S", "C", "N") need to be wrapped in JSON object
                expected = json.dumps({output_key: expected}, ensure_ascii=False)

        examples.append({
            "input": input_str,
            "answer": expected,
            "additional_context": {},
        })

    return examples


def run_optimization(
    module_id: str,
    task_model: str = "openai/gpt-4o-mini",
    reflection_model: str = "openai/gpt-4o",
    judge_model: str = "gpt-4o",
    judge_rounds: int = 1,
    judge_agg: str = "mean",
    hybrid_weight: float = 0.3,
    train_size: int = 20,
    val_size: int = 5,
    budget: int = 50,
    run_dir: str = None,
):
    """Run GEPA optimization for a text generation module."""

    module_id = module_id.lower()

    # Use shared config
    try:
        config = get_config(module_id)
    except ValueError as e:
        available = list_textgen_modules()
        raise ValueError(f"Unknown module: {module_id}. Text generation modules: {available}")

    print(f"\n{'='*60}")
    print(f"GEPA Text Generation Optimizer")
    print(f"{'='*60}")
    print(f"Module:       {module_id} ({config['name']})")
    print(f"Task LM:      {task_model}")
    print(f"Reflection:   {reflection_model}")
    print(f"Judge:        {judge_model}")
    print(f"Judge rounds: {judge_rounds} ({judge_agg})")
    print(f"Hybrid wgt:   {hybrid_weight}")
    print(f"Train/Val:    {train_size}/{val_size}")
    print(f"Budget:       {budget} metric calls")
    print(f"{'='*60}\n")

    # Load prompt as seed
    prompt_text = config["prompt"].read_text()
    seed_candidate = {"system_prompt": prompt_text}

    print(f"Loaded seed prompt: {len(prompt_text)} chars")

    # Load dataset
    all_examples = load_dataset(
        config["dataset"],
        config["input_template"],
        config["output_key"],
        limit=train_size + val_size,
    )

    print(f"Loaded {len(all_examples)} examples")

    # Split train/val
    if len(all_examples) < train_size + val_size:
        train_size = max(1, len(all_examples) - val_size)
        print(f"  Adjusted train_size to {train_size}")

    trainset = all_examples[:train_size]
    valset = all_examples[train_size:train_size + val_size]

    print(f"  Train: {len(trainset)}, Val: {len(valset)}")

    # Get evaluator
    evaluator = get_evaluator(
        module_id,
        judge_model=judge_model,
        judge_rounds=judge_rounds,
        judge_agg=judge_agg,
        hybrid_weight=hybrid_weight,
    )
    print(f"\nUsing LLM-as-Judge evaluator ({judge_model})")

    # Setup output directory
    if run_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = ARTIFACTS_DIR / module_id / task_model.replace("/", "_") / timestamp

    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"Output dir: {run_dir}")

    # Run GEPA optimization
    print(f"\nStarting GEPA optimization...")
    print(f"  (This uses evolutionary search with LLM reflection)\n")

    result = gepa.optimize(
        seed_candidate=seed_candidate,
        trainset=trainset,
        valset=valset,
        task_lm=task_model,
        reflection_lm=reflection_model,
        evaluator=evaluator,
        max_metric_calls=budget,
        run_dir=str(run_dir),
        display_progress_bar=True,
        skip_perfect_score=True,
    )

    # Extract results from GEPA
    # GEPA returns: candidates (list), val_aggregate_scores (list)
    candidates = result.candidates
    scores = result.val_aggregate_scores

    # Find best candidate
    if scores:
        best_idx = scores.index(max(scores))
        best_candidate = candidates[best_idx]
        final_score = scores[best_idx]
        initial_score = scores[0] if len(scores) > 0 else None
    else:
        best_candidate = candidates[0] if candidates else seed_candidate
        final_score = 0.0
        initial_score = None

    best_prompt = best_candidate.get("system_prompt", "")

    # Save results
    output = {
        "module": module_id,
        "module_name": config["name"],
        "task_model": task_model,
        "reflection_model": reflection_model,
        "judge_model": judge_model,
        "budget": budget,
        "train_size": len(trainset),
        "val_size": len(valset),
        "initial_prompt_length": len(prompt_text),
        "optimized_prompt_length": len(best_prompt),
        "optimized_prompt": best_prompt,
        "timestamp": datetime.now().isoformat(),
    }

    # Add scores if available
    if final_score is not None:
        output["final_score"] = final_score
    if initial_score is not None:
        output["initial_score"] = initial_score
        output["improvement"] = final_score - initial_score if final_score else None

    # Save optimized result
    output_path = run_dir / "optimized.json"
    output_path.write_text(json.dumps(output, indent=2, ensure_ascii=False))

    # Also save to standard location (latest)
    latest_dir = ARTIFACTS_DIR / module_id / task_model.replace("/", "_") / "latest"
    latest_dir.mkdir(parents=True, exist_ok=True)
    (latest_dir / "optimized.json").write_text(json.dumps(output, indent=2, ensure_ascii=False))

    print(f"\n{'='*60}")
    print(f"GEPA Optimization Complete!")
    print(f"{'='*60}")
    print(f"  Module:    {module_id}")
    if final_score is not None:
        print(f"  Score:     {final_score:.3f}")
    if initial_score is not None and final_score is not None:
        print(f"  Improve:   {final_score - initial_score:+.3f}")
    print(f"  Prompt:    {len(best_prompt)} chars")
    print(f"  Output:    {output_path}")
    print(f"{'='*60}\n")

    return output


def main():
    parser = argparse.ArgumentParser(
        description="GEPA optimizer for text generation modules",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Presets:
    lite   - train=10, val=3, budget=30    (quick test)
    light  - train=20, val=5, budget=50    (default)
    medium - train=30, val=10, budget=100  (balanced)
    full   - train=50, val=15, budget=200  (production)

Examples:
    python optimize_gepa.py m09 --preset lite
    python optimize_gepa.py m01a --train-size 15 --budget 40
        """
    )
    parser.add_argument("module", help=f"Module ID: {list_textgen_modules()}")
    parser.add_argument("--preset", "-p", choices=["lite", "light", "medium", "full"],
                        help="Optimization preset")
    parser.add_argument("--task-model", default="openai/gpt-4o-mini", help="Task LLM")
    parser.add_argument("--reflection-model", default="openai/gpt-4o", help="Reflection LLM")
    parser.add_argument("--judge-model", default="gpt-4o", help="Judge LLM for evaluation")
    parser.add_argument("--judge-rounds", type=int, default=1, help="Number of judge rounds (default: 1)")
    parser.add_argument("--judge-agg", choices=["mean", "median"], default="mean", help="Judge aggregation (default: mean)")
    parser.add_argument("--hybrid-weight", type=float, default=0.3, help="LLM fallback weight for structured modules")
    parser.add_argument("--train-size", type=int, help="Training examples")
    parser.add_argument("--val-size", type=int, help="Validation examples")
    parser.add_argument("--budget", type=int, help="Max metric calls")
    parser.add_argument("--run-dir", help="Output directory (auto-generated if not set)")

    args = parser.parse_args()

    # Apply presets
    presets = {
        "lite":   {"train": 10, "val": 3,  "budget": 30},
        "light":  {"train": 20, "val": 5,  "budget": 50},
        "medium": {"train": 30, "val": 10, "budget": 100},
        "full":   {"train": 50, "val": 15, "budget": 200},
    }

    preset = presets.get(args.preset or "light")
    train_size = args.train_size or preset["train"]
    val_size = args.val_size or preset["val"]
    budget = args.budget or preset["budget"]

    run_optimization(
        module_id=args.module,
        task_model=args.task_model,
        reflection_model=args.reflection_model,
        judge_model=args.judge_model,
        judge_rounds=args.judge_rounds,
        judge_agg=args.judge_agg,
        hybrid_weight=args.hybrid_weight,
        train_size=train_size,
        val_size=val_size,
        budget=budget,
        run_dir=args.run_dir,
    )


if __name__ == "__main__":
    main()
