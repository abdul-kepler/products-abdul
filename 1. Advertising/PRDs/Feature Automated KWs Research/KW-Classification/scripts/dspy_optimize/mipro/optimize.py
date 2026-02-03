#!/usr/bin/env python3
"""
Unified MIPRO optimizer for all modules.

Usage:
    python optimize.py m02                    # optimize M02
    python optimize.py m02 --preset lite      # quick test
    python optimize.py --list                 # list available modules
    python optimize.py m02 --train-size 50 --dev-size 15 --max-demos 4
"""

import argparse
import sys
from pathlib import Path

# Add parent directory for shared module_config
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from base_runner import run_module, PROJECT_ROOT
from module_config import get_config, list_modules, list_classifier_modules


def main():
    parser = argparse.ArgumentParser(
        description="MIPRO optimizer for classification modules",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Presets:
    lite   - train=15, dev=5, demos=2    (quick test)
    light  - train=40, dev=10, demos=4   (default)
    medium - train=80, dev=20, demos=6   (balanced)
    full   - train=150, dev=50, demos=8  (production)

Examples:
    python optimize.py m02                    # Optimize M02 with defaults
    python optimize.py m02 --preset lite      # Quick test
    python optimize.py m02 --train-size 100   # Custom training size
    python optimize.py --list                 # List all modules
        """
    )

    parser.add_argument("module", nargs="?", help="Module to optimize (e.g., m02, m13)")
    parser.add_argument("--list", "-l", action="store_true", help="List available modules")
    parser.add_argument("--preset", "-p", choices=["lite", "light", "medium", "full"],
                        help="Optimization preset")
    parser.add_argument("--provider", default="gpt-4o-mini", help="LLM provider")
    parser.add_argument("--train-size", type=int, help="Training set size")
    parser.add_argument("--dev-size", type=int, help="Validation set size")
    parser.add_argument("--max-demos", type=int, help="Max few-shot demos")
    parser.add_argument("--temperature", type=float, default=0.2, help="Temperature")
    parser.add_argument("--threads", type=int, default=6, help="Parallel threads")

    args = parser.parse_args()

    # List modules
    if args.list:
        print("Available modules:")
        for module in list_modules():
            config = get_config(module)
            print(f"  {module:8} - {config['name']}")
        return

    # Require module if not listing
    if not args.module:
        parser.error("Module name required. Use --list to see available modules.")

    # Apply presets (defaults if not set by CLI)
    presets = {
        "lite":   {"train": 15,  "dev": 5,  "demos": 2},
        "light":  {"train": 40,  "dev": 10, "demos": 4},
        "medium": {"train": 80,  "dev": 20, "demos": 6},
        "full":   {"train": 150, "dev": 50, "demos": 8},
    }

    preset = presets.get(args.preset or "light")
    train_size = args.train_size or preset["train"]
    dev_size = args.dev_size or preset["dev"]
    max_demos = args.max_demos or preset["demos"]

    # Get module config
    config = get_config(args.module)

    print(f"=" * 60)
    print(f"MIPRO Optimizer: {args.module} ({config['name']})")
    print(f"=" * 60)
    print(f"  Dataset:  {config['dataset'].name}")
    print(f"  Prompt:   {config['prompt'].name}")
    print(f"  Provider: {args.provider}")
    print(f"  Train:    {train_size}")
    print(f"  Dev:      {dev_size}")
    print(f"  Demos:    {max_demos}")
    print(f"=" * 60)

    # Run optimization
    run_module(
        module_name=args.module,
        dataset_path=config["dataset"],
        prompt_path=config["prompt"],
        input_keys=config["input_keys"],
        output_keys=config["output_keys"],
        provider=args.provider,
        train_size=train_size,
        dev_size=dev_size,
        max_demos=max_demos,
        sleep=0.0,
        temperature=args.temperature,
        positive_values=config.get("positive_values"),
        balance_field=config.get("balance_field"),
        num_threads=args.threads,
    )


if __name__ == "__main__":
    main()
