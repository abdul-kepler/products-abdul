#!/usr/bin/env python3
"""
Test M11 v2 Prompt

Compare v1 vs v2 prompt performance on M11 IdentifyHardConstraints.
Key issue: Model marks durability features (Water Repellent, Insulated) as hard constraints.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

from openai import OpenAI

PROMPTS_DIR = PROJECT_ROOT / "prompts" / "modules"
DATASETS_DIR = PROJECT_ROOT / "datasets"
RESULTS_DIR = PROJECT_ROOT / "experiment_results"

client = OpenAI()

# NEVER categories - these should NEVER be hard constraints
NEVER_CONSTRAINTS = [
    # Weather/Environment
    "water repellent", "water resistant", "waterproof", "insulated",
    "windproof", "dustproof", "shockproof",
    # Performance
    "battery", "hour", "deep bass", "fast", "quick",
    # Material
    "stainless steel", "silicone", "bamboo", "nylon", "cotton",
    # Quality
    "premium", "sturdy", "durable", "long-lasting", "hospital grade",
    # Durability
    "rustproof", "smudge-proof", "scratch-resistant",
]


def load_prompt(filename: str) -> str:
    with open(PROMPTS_DIR / filename, "r", encoding="utf-8") as f:
        return f.read()


def load_samples(n: int = 10) -> List[Dict]:
    samples = []
    dataset_file = DATASETS_DIR / "m11_identify_hard_constraints_v1.1.jsonl"

    if not dataset_file.exists():
        # Try alternative name
        dataset_file = DATASETS_DIR / "m11_identify_hard_constraints.jsonl"

    with open(dataset_file, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= n:
                break
            if line.strip():
                samples.append(json.loads(line))

    return samples


def fill_template(template: str, input_data: dict) -> str:
    result = template
    for key, value in input_data.items():
        placeholder = "{{" + key + "}}"
        if isinstance(value, (list, dict)):
            value_str = json.dumps(value, indent=2, ensure_ascii=False)
        else:
            value_str = str(value) if value else ""
        result = result.replace(placeholder, value_str)
    return result


def call_llm(prompt: str) -> Dict:
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=2000
        )
        content = response.choices[0].message.content

        if "```json" in content:
            start = content.find("```json") + 7
            end = content.find("```", start)
            json_str = content[start:end].strip()
        elif "{" in content:
            start = content.find("{")
            end = content.rfind("}") + 1
            json_str = content[start:end]
        else:
            return {"error": "No JSON found", "raw": content[:500]}

        return json.loads(json_str)
    except Exception as e:
        return {"error": str(e)}


def evaluate_output(output: Dict, input_data: Dict, expected: Dict) -> Dict:
    """Evaluate M11 output against rubrics."""
    results = {
        "zero_or_one_constraints": {"pass": True, "issues": []},
        "no_never_categories": {"pass": True, "issues": []},
        "matches_expected": {"pass": True, "issues": []},
    }

    hard_constraints = output.get("hard_constraints", [])
    expected_constraints = expected.get("hard_constraints", [])

    # Check 1: Should be 0-1 constraints
    if len(hard_constraints) > 1:
        results["zero_or_one_constraints"]["pass"] = False
        results["zero_or_one_constraints"]["issues"].append(
            f"Found {len(hard_constraints)} constraints (expected 0-1)"
        )

    # Check 2: No NEVER categories
    for constraint in hard_constraints:
        constraint_lower = constraint.lower()
        for never in NEVER_CONSTRAINTS:
            if never in constraint_lower:
                results["no_never_categories"]["pass"] = False
                results["no_never_categories"]["issues"].append(
                    f"'{constraint}' is in NEVER category (matched: {never})"
                )
                break

    # Check 3: Matches expected
    expected_set = set([c.lower() for c in expected_constraints])
    actual_set = set([c.lower() for c in hard_constraints])

    if expected_set != actual_set:
        results["matches_expected"]["pass"] = False
        if expected_set and not actual_set:
            results["matches_expected"]["issues"].append(f"Expected {expected_constraints}, got []")
        elif actual_set and not expected_set:
            results["matches_expected"]["issues"].append(f"Expected [], got {hard_constraints}")
        else:
            results["matches_expected"]["issues"].append(
                f"Expected {expected_constraints}, got {hard_constraints}"
            )

    return results


def run_test(prompt_version: str, samples: List[Dict]) -> Dict:
    if prompt_version == "v1":
        prompt_file = "m11_identify_hard_constraints_v1.1.md"
    else:
        prompt_file = "m11_identify_hard_constraints_v2.md"

    template = load_prompt(prompt_file)

    print(f"\n{'='*60}")
    print(f"Testing M11 {prompt_version.upper()} Prompt")
    print(f"{'='*60}")

    results = {
        "version": prompt_version,
        "samples_tested": len(samples),
        "rubric_scores": {
            "zero_or_one_constraints": {"pass": 0, "fail": 0},
            "no_never_categories": {"pass": 0, "fail": 0},
            "matches_expected": {"pass": 0, "fail": 0},
        },
        "details": []
    }

    for i, sample in enumerate(samples):
        input_data = sample.get("input", {})
        expected = sample.get("expected", {})

        title = input_data.get("title", "")[:50]
        print(f"\n[{i+1}/{len(samples)}] {title}...")

        filled_prompt = fill_template(template, input_data)
        output = call_llm(filled_prompt)

        if "error" in output:
            print(f"  ERROR: {output['error']}")
            continue

        eval_result = evaluate_output(output, input_data, expected)

        hard_constraints = output.get("hard_constraints", [])
        expected_constraints = expected.get("hard_constraints", [])

        detail = {
            "sample_idx": i,
            "title": title,
            "expected_constraints": expected_constraints,
            "actual_constraints": hard_constraints,
            "evaluation": eval_result
        }
        results["details"].append(detail)

        for rubric, result in eval_result.items():
            if result["pass"]:
                results["rubric_scores"][rubric]["pass"] += 1
                print(f"  ✓ {rubric}")
            else:
                results["rubric_scores"][rubric]["fail"] += 1
                print(f"  ✗ {rubric}: {result['issues'][:1]}")

    return results


def print_summary(v1_results: Dict, v2_results: Dict):
    print(f"\n{'='*60}")
    print("COMPARISON SUMMARY")
    print(f"{'='*60}")

    rubrics = ["zero_or_one_constraints", "no_never_categories", "matches_expected"]

    print(f"\n{'Rubric':<25} {'V1 Pass%':>10} {'V2 Pass%':>10} {'Δ':>8}")
    print("-" * 55)

    for rubric in rubrics:
        v1_pass = v1_results["rubric_scores"][rubric]["pass"]
        v1_total = v1_pass + v1_results["rubric_scores"][rubric]["fail"]
        v1_rate = (v1_pass / v1_total * 100) if v1_total > 0 else 0

        v2_pass = v2_results["rubric_scores"][rubric]["pass"]
        v2_total = v2_pass + v2_results["rubric_scores"][rubric]["fail"]
        v2_rate = (v2_pass / v2_total * 100) if v2_total > 0 else 0

        delta = v2_rate - v1_rate
        delta_str = f"+{delta:.1f}%" if delta > 0 else f"{delta:.1f}%"

        print(f"{rubric:<25} {v1_rate:>9.1f}% {v2_rate:>9.1f}% {delta_str:>8}")

    print("-" * 55)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Test M11 v1 vs v2 prompts")
    parser.add_argument("--samples", "-n", type=int, default=10, help="Number of samples")
    parser.add_argument("--version", "-v", choices=["v1", "v2", "both"], default="both")
    args = parser.parse_args()

    samples = load_samples(args.samples)
    print(f"Loaded {len(samples)} test samples")

    v1_results = None
    v2_results = None

    if args.version in ["v1", "both"]:
        v1_results = run_test("v1", samples)

    if args.version in ["v2", "both"]:
        v2_results = run_test("v2", samples)

    if v1_results and v2_results:
        print_summary(v1_results, v2_results)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = RESULTS_DIR / f"m11_v1_vs_v2_{timestamp}.json"

    with open(output_file, "w") as f:
        json.dump({
            "timestamp": timestamp,
            "samples": args.samples,
            "v1": v1_results,
            "v2": v2_results,
        }, f, indent=2)

    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
