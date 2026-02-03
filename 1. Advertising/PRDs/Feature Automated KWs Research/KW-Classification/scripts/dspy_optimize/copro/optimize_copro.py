#!/usr/bin/env python3
"""
COPRO optimizer - iteratively optimizes the instruction/prompt itself.

Unlike MIPROv2 which selects few-shot examples, COPRO focuses on
rewriting and improving the instruction text.

Usage:
    python optimize_copro.py m02                           # optimize M02 with COPRO
    python optimize_copro.py m02 --breadth 5 --depth 3     # more exploration
    python optimize_copro.py --list                        # list available modules
"""

import argparse
import json
from pathlib import Path

import dspy
from dspy.clients.lm import LM
from dspy.clients.openai import OpenAIProvider
from dspy.teleprompt import COPRO

import sys
from pathlib import Path

# Add parent folder for shared module_config, and mipro for base_runner
SCRIPT_DIR = Path(__file__).resolve().parent
PARENT_DIR = SCRIPT_DIR.parent
MIPRO_DIR = PARENT_DIR / "mipro"
sys.path.insert(0, str(PARENT_DIR))
sys.path.insert(0, str(MIPRO_DIR))

from module_config import get_config, list_modules, list_classifier_modules, PROJECT_ROOT
from base_runner import load_examples, simple_metric, build_signature, convert_null_to_string

# Load env
from dotenv import load_dotenv
import os

ENV_PATH = PROJECT_ROOT / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)


def build_signature_with_instruction(input_keys: list, output_keys: list, instruction: str):
    """Build a DSPy Signature with an initial instruction for COPRO to optimize."""
    ns = {"__doc__": instruction}
    for k in input_keys:
        ns[k] = dspy.InputField()
    for k in output_keys:
        ns[k] = dspy.OutputField()
    return type("Sig", (dspy.Signature,), ns)


def run_copro(
    module_name: str,
    config: dict,
    provider: str,
    train_size: int,
    dev_size: int,
    breadth: int,
    depth: int,
    temperature: float,
):
    """Run COPRO optimization."""

    prompt_path = config["prompt"]
    dataset_path = config["dataset"]
    input_keys = config["input_keys"]
    output_keys = config["output_keys"]
    positive_values = config["positive_values"]
    balance_field = config.get("balance_field")

    prompt_text = prompt_path.read_text()

    # Load examples WITHOUT guidelines as input (COPRO optimizes instruction, not input)
    all_examples = load_examples(
        dataset_path, input_keys, output_keys,
        None, balance_field, positive_values  # No constant_inputs!
    )

    train = all_examples[:train_size] if train_size else all_examples
    dev = all_examples[train_size:train_size + dev_size] if dev_size else []

    print(f"  Train: {len(train)}, Dev: {len(dev)}")

    # Configure LM
    dspy.configure(
        lm=LM(
            model=provider,
            provider=OpenAIProvider(),
            response_format={"type": "json_object"},
            num_retries=5,
            timeout=120,
            temperature=temperature,
        ),
    )

    # Build signature WITH prompt as instruction - COPRO will optimize this!
    Sig = build_signature_with_instruction(input_keys, output_keys, prompt_text)
    print(f"  Initial instruction length: {len(prompt_text)} chars")

    metric = simple_metric(output_keys, positive_values)

    # Create program
    program = dspy.Predict(Sig)

    # COPRO optimizer
    print(f"\n  Running COPRO with breadth={breadth}, depth={depth}...")
    opt = COPRO(
        metric=metric,
        breadth=breadth,  # Number of instruction candidates per iteration
        depth=depth,      # Number of optimization iterations
        init_temperature=1.0,  # Higher = more creative instructions
    )

    # Compile with COPRO
    # COPRO uses trainset for evaluation, eval_kwargs for additional Evaluate params
    compiled = opt.compile(program, trainset=train, eval_kwargs={})

    # Extract results
    best_instruction = ""
    if hasattr(compiled, 'signature') and hasattr(compiled.signature, 'instructions'):
        best_instruction = compiled.signature.instructions

    # Save results
    out_dir = PROJECT_ROOT / "artifacts" / "dspy_copro" / module_name / provider
    out_dir.mkdir(parents=True, exist_ok=True)

    # Build output
    output = {
        "module": module_name,
        "provider": provider,
        "optimizer": "COPRO",
        "breadth": breadth,
        "depth": depth,
        "train_size": len(train),
        "dev_size": len(dev),
        "original_prompt": prompt_text,
        "optimized_instruction": best_instruction,
        "input_keys": input_keys,
        "output_keys": output_keys,
    }

    (out_dir / "copro_result.json").write_text(
        json.dumps(output, indent=2, ensure_ascii=False)
    )

    # Also save raw state
    if hasattr(compiled, 'dump_state'):
        state = compiled.dump_state()
        (out_dir / "compiled_raw.json").write_text(
            json.dumps(state, indent=2, default=str)
        )

    print(f"\n[ok] saved to {out_dir}")
    print(f"\n  Optimized instruction:")
    print(f"  {best_instruction[:200]}..." if len(best_instruction) > 200 else f"  {best_instruction}")

    return compiled


def main():
    parser = argparse.ArgumentParser(
        description="COPRO optimizer - improves instruction text",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python optimize_copro.py m02                    # Optimize M02 with COPRO
    python optimize_copro.py m02 --breadth 5        # More candidate instructions
    python optimize_copro.py m02 --depth 3          # More iterations
    python optimize_copro.py --list                 # List all available modules
        """
    )

    parser.add_argument("module", nargs="?", help="Module to optimize (e.g., m02, m13)")
    parser.add_argument("--list", "-l", action="store_true", help="List available modules")
    parser.add_argument("--provider", default="gpt-4o-mini", help="LLM provider (default: gpt-4o-mini)")
    parser.add_argument("--train-size", type=int, default=30, help="Train set size (default: 30)")
    parser.add_argument("--dev-size", type=int, default=10, help="Validation set size (default: 10)")
    parser.add_argument("--breadth", type=int, default=3, help="Instruction candidates per iteration (default: 3)")
    parser.add_argument("--depth", type=int, default=2, help="Optimization iterations (default: 2)")
    parser.add_argument("--temperature", type=float, default=0.2, help="Temperature (default: 0.2)")

    args = parser.parse_args()

    if args.list:
        print("Available modules:")
        for module in list_modules():
            config = get_config(module)
            print(f"  {module:8} - {config['name']}")
        return

    if not args.module:
        parser.error("Module name required. Use --list to see available modules.")

    config = get_config(args.module)

    print(f"=" * 60)
    print(f"COPRO Optimizer: {args.module} ({config['name']})")
    print(f"=" * 60)
    print(f"  Dataset:  {config['dataset'].name}")
    print(f"  Prompt:   {config['prompt'].name}")
    print(f"  Breadth:  {args.breadth} (candidates per iteration)")
    print(f"  Depth:    {args.depth} (iterations)")
    print(f"=" * 60)

    run_copro(
        module_name=args.module,
        config=config,
        provider=args.provider,
        train_size=args.train_size,
        dev_size=args.dev_size,
        breadth=args.breadth,
        depth=args.depth,
        temperature=args.temperature,
    )


if __name__ == "__main__":
    main()
