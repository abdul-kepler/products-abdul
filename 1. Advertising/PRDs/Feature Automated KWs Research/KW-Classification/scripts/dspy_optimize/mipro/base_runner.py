#!/usr/bin/env python3
"""
Shared DSPy optimizer runner (per-module wrappers import this).
"""

import argparse
import json
import os
from pathlib import Path
from typing import List

import dspy
from dspy.teleprompt import MIPROv2
from dotenv import load_dotenv

import sys
# Add parent directory for shared module_config
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

PROJECT_ROOT = Path(__file__).resolve().parents[3]  # /scripts/dspy_optimize/mipro/.. -> project root
ENV_PATH = PROJECT_ROOT / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)

# Check for at least one API key (OpenAI, Gemini, or Anthropic)
if not any([os.getenv("OPENAI_API_KEY"), os.getenv("GEMINI_API_KEY"), os.getenv("ANTHROPIC_API_KEY")]):
    raise RuntimeError("No API key set. Add OPENAI_API_KEY, GEMINI_API_KEY, or ANTHROPIC_API_KEY to .env")


def convert_null_to_string(obj: dict, output_keys: List[str]) -> dict:
    """Convert null values in output fields to string 'NULL' for DSPy compatibility."""
    result = obj.copy()
    for key in output_keys:
        if key in result and result[key] is None:
            result[key] = "NULL"  # DSPy-friendly string
    return result


def load_examples(
    path: Path,
    input_keys: List[str],
    output_keys: List[str],
    constant_inputs: dict | None = None,
    balance_field: str | None = None,
    positive_values: dict | None = None,
):
    """
    Load examples from JSONL file.

    Args:
        path: Path to JSONL file
        input_keys: List of input field names
        output_keys: List of output field names
        constant_inputs: Dict of constant inputs to add to all examples
        balance_field: If set, balance examples by this field (e.g., "branding_scope_1")
        positive_values: Dict mapping field to set of positive values for balancing
    """
    records = []
    constant_inputs = constant_inputs or {}
    positive_values = positive_values or {}

    for line in path.open():
        if not line.strip():
            continue
        rec = json.loads(line)
        inp = rec.get("input", {})
        exp = rec.get("expected", {})

        # Convert null -> "NULL" string for DSPy compatibility
        exp = convert_null_to_string(exp, output_keys)

        example = dspy.Example(**constant_inputs, **inp, **exp).with_inputs(*input_keys)
        records.append(example)

    # Balance dataset if requested
    if balance_field and records:
        pos_vals = positive_values.get(balance_field, set())

        def is_positive(r):
            val = getattr(r, balance_field, "NULL")
            if isinstance(val, str):
                val_lower = val.lower().strip()
                # Check against positive values
                if pos_vals and val_lower in pos_vals:
                    return True
                # Boolean-like positive
                if val_lower in ("true", "yes"):
                    return True
                # Null-like values (NOT "n" - that's a real classification value!)
                if val_lower in ("null", "none", "", "false", "no"):
                    return False
                # If we have positive_values defined, anything not in it is negative
                # e.g., "n" for M12b is negative because it's not in {"r", "s", "c"}
                if pos_vals:
                    return False
                # Otherwise non-null is positive
                return True
            if isinstance(val, bool):
                return val
            return val is not None

        positive = [r for r in records if is_positive(r)]
        negative = [r for r in records if not is_positive(r)]

        # Take equal amounts, INTERLEAVE (not shuffle) for balanced demos
        import random
        random.seed(42)
        min_count = min(len(positive), len(negative))
        if min_count > 0:
            pos_sample = random.sample(positive, min_count)
            neg_sample = random.sample(negative, min_count)

            # Interleave: [pos1, neg1, pos2, neg2, ...]
            # This ensures DSPy bootstrap picks balanced demos
            balanced = []
            for p, n in zip(pos_sample, neg_sample):
                balanced.append(p)
                balanced.append(n)

            print(f"  Balanced dataset: {len(positive)} positive, {len(negative)} negative -> {len(balanced)} interleaved")
            return balanced

    return records


def build_signature(input_keys: List[str], output_keys: List[str]):
    ns = {}
    for k in input_keys:
        ns[k] = dspy.InputField()
    for k in output_keys:
        ns[k] = dspy.OutputField()
    return type("Sig", (dspy.Signature,), ns)


def normalize_value(v, positive_values: set | None = None):
    """
    Normalize values for comparison.

    Args:
        v: Value to normalize
        positive_values: Set of strings that should be treated as "positive" (e.g., {"ob", "cb", "nb"})
                        If None, returns normalized string without mapping to positive/negative
    """
    if v is None:
        return "negative"  # Use string for consistent comparison

    if isinstance(v, bool):
        return "positive" if v else "negative"

    if isinstance(v, str):
        v_lower = v.lower().strip()

        # Null/negative variants -> "negative"
        if v_lower in ("null", "none", "", "n/a", "no", "false"):
            return "negative"

        # If we have positive_values defined, map to canonical form
        if positive_values:
            if v_lower in positive_values:
                return "positive"
            # Common truthy values
            if v_lower in ("yes", "true"):
                return "positive"

        return v_lower

    return v


def simple_metric(output_keys: List[str], positive_values: dict | None = None):
    """
    Create a metric function for comparing outputs.

    Args:
        output_keys: List of output field names to compare
        positive_values: Dict mapping field name to set of positive values
                        e.g., {"branding_scope_1": {"ob"}} for M02
                        If None, does exact comparison after basic normalization
    """
    positive_values = positive_values or {}

    def _metric(ex, pred, trace=None):
        score = 0
        for k in output_keys:
            pos_vals = positive_values.get(k)
            expected = normalize_value(getattr(ex, k, None), pos_vals)
            actual = normalize_value(getattr(pred, k, None), pos_vals)
            if expected == actual:
                score += 1
        return score / len(output_keys)
    return _metric


def run_module(
    module_name: str,
    dataset_path: Path,
    prompt_path: Path,
    input_keys: List[str],
    output_keys: List[str],
    provider: str,
    train_size: int,
    dev_size: int,
    max_demos: int,
    sleep: float,
    temperature: float,
    seed_examples: List[dict] | None = None,
    positive_values: dict | None = None,  # e.g., {"branding_scope_1": {"ob"}}
    balance_field: str | None = None,  # e.g., "branding_scope_1" to balance OB/NULL
    num_threads: int = 6,  # Reduce parallelism to avoid rate limits
):
    prompt_text = prompt_path.read_text()
    # extend inputs with guidelines to avoid passing 'instructions' to OpenAI
    input_keys_ext = input_keys + ["guidelines"]
    constant_inputs = {"guidelines": prompt_text}
    all_examples = load_examples(dataset_path, input_keys_ext, output_keys, constant_inputs, balance_field, positive_values)

    # prepend curated seed examples if provided
    if seed_examples:
        seed_objs = []
        for ex in seed_examples:
            inp = {**constant_inputs, **ex["input"]}
            exp = ex["expected"]
            seed = dspy.Example(**inp, **exp).with_inputs(*input_keys_ext)
            seed_objs.append(seed)
        all_examples = seed_objs + all_examples
    # Ensure we have enough data for both train and dev
    total_available = len(all_examples)
    min_dev = max(1, dev_size) if dev_size else 0  # At least 1 for validation

    if total_available < train_size + min_dev:
        # Not enough data - adjust train_size to leave room for dev
        adjusted_train = max(1, total_available - min_dev)
        print(f"  Warning: Only {total_available} examples available, adjusting train from {train_size} to {adjusted_train}")
        train_size = adjusted_train

    train = all_examples[:train_size] if train_size else all_examples
    dev = all_examples[train_size:train_size + dev_size] if dev_size else []

    # Final safety check
    if dev_size and len(dev) == 0:
        print(f"  Error: No dev examples! Need more data or smaller train_size.")
        raise ValueError(f"Dataset too small: {total_available} examples, need at least {train_size + 1} for train+dev")

    print(f"  Train: {len(train)}, Dev: {len(dev)}")

    # DSPy LM uses LiteLLM under the hood - supports OpenAI, Gemini, Anthropic, etc.
    # Model format: "openai/gpt-4o-mini", "gemini/gemini-1.5-flash", "anthropic/claude-3-haiku"
    dspy.configure(
        lm=dspy.LM(
            model=provider,
            response_format={"type": "json_object"},
            num_retries=5,
            temperature=temperature,
        ),
    )

    Sig = build_signature(input_keys_ext, output_keys)
    metric = simple_metric(output_keys, positive_values)

    program = dspy.Predict(Sig)
    opt = MIPROv2(
        metric=metric,
        max_bootstrapped_demos=max_demos,
        max_labeled_demos=max_demos,
        num_threads=num_threads,  # Reduce parallelism to avoid rate limits
    )

    compiled = opt.compile(program, trainset=train, valset=dev)

    # Find best program WITH demos from candidate_programs
    best_program = compiled
    best_score = getattr(compiled, 'score', 0) or 0

    if hasattr(compiled, 'candidate_programs') and compiled.candidate_programs:
        for prog_dict in compiled.candidate_programs:
            if isinstance(prog_dict, dict) and 'program' in prog_dict:
                p = prog_dict['program']
                score = prog_dict.get('score', 0)
                demo_count = len(p.demos) if hasattr(p, 'demos') else 0
                # Prefer programs with demos and same/better score
                if demo_count > 0 and score >= best_score:
                    if not hasattr(best_program, 'demos') or len(best_program.demos) == 0:
                        best_program = p
                        best_score = score

    out_dir = PROJECT_ROOT / "artifacts" / "dspy_mipro" / module_name / provider
    out_dir.mkdir(parents=True, exist_ok=True)

    # Build clean output: strip guidelines from demos, save it once
    state = best_program.dump_state()

    # Clean demos: remove verbose 'guidelines' field (save separately)
    clean_demos = []
    for demo in state.get("demos", []):
        clean_demo = {k: v for k, v in demo.items() if k != "guidelines"}
        clean_demos.append(clean_demo)

    # Build optimized output
    optimized_output = {
        "module": module_name,
        "provider": provider,
        "score": best_score,
        "guidelines": prompt_text,  # Save once
        "instruction": state.get("signature", {}).get("instructions", ""),
        "demos": clean_demos,  # Without guidelines
        "input_keys": input_keys,
        "output_keys": output_keys,
    }

    (out_dir / "optimized.json").write_text(json.dumps(optimized_output, indent=2, ensure_ascii=False))

    # Also save raw state for debugging
    (out_dir / "compiled_raw.json").write_text(json.dumps(state, indent=2, default=str))

    print(f"\n[ok] saved to {out_dir}")
    print(f"    score: {best_score}")
    print(f"    demos: {len(clean_demos)}")
    print(f"    instruction: {optimized_output['instruction'][:80]}...")


def build_argparser():
    p = argparse.ArgumentParser()
    p.add_argument("--provider", default="gpt-4o-mini")
    p.add_argument("--train-size", type=int, default=40)
    p.add_argument("--dev-size", type=int, default=10)
    p.add_argument("--max-demos", type=int, default=4)
    p.add_argument("--sleep", type=float, default=0.0)
    p.add_argument("--temperature", type=float, default=0.2)
    return p
