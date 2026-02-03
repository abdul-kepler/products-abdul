#!/usr/bin/env python3
"""
Test M08 v2 Prompt

Compare v1 vs v2 prompt performance on M08 AssignAttributeRanks.
Tests the key rubrics:
- ranks_assigned: All input attributes must appear in output
- important_ranked_high: Function > Color
- audiences_handling: ["-"] means no Audience rows
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


def load_prompt(filename: str) -> str:
    with open(PROMPTS_DIR / filename, "r", encoding="utf-8") as f:
        return f.read()


def load_samples(n: int = 10) -> List[Dict]:
    samples = []
    dataset_file = DATASETS_DIR / "m08_assign_attribute_ranks.jsonl"

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
            max_tokens=3000
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


def evaluate_output(output: Dict, input_data: Dict) -> Dict:
    """Evaluate M08 output against rubrics."""
    results = {
        "all_attributes_ranked": {"pass": True, "issues": []},
        "color_not_rank_1": {"pass": True, "issues": []},
        "audiences_handled": {"pass": True, "issues": []},
        "unique_ranks": {"pass": True, "issues": []},
    }

    attribute_table = output.get("attribute_table", [])

    # Get input counts
    input_variants = input_data.get("variants", [])
    input_use_cases = input_data.get("use_cases", [])
    input_audiences = input_data.get("audiences", [])

    # Count outputs
    output_variants = [a for a in attribute_table if a.get("attribute_type") == "Variant"]
    output_use_cases = [a for a in attribute_table if a.get("attribute_type") == "UseCase"]
    output_audiences = [a for a in attribute_table if a.get("attribute_type") == "Audience"]

    # Check 1: All attributes ranked
    if len(output_variants) != len(input_variants):
        results["all_attributes_ranked"]["pass"] = False
        results["all_attributes_ranked"]["issues"].append(
            f"Variant count mismatch: input={len(input_variants)}, output={len(output_variants)}"
        )

    if len(output_use_cases) != len(input_use_cases):
        results["all_attributes_ranked"]["pass"] = False
        results["all_attributes_ranked"]["issues"].append(
            f"UseCase count mismatch: input={len(input_use_cases)}, output={len(output_use_cases)}"
        )

    # Check 2: Audiences handling
    audiences_is_dash = input_audiences == ["-"] or input_audiences == [] or input_audiences == ["-"]
    if audiences_is_dash:
        if len(output_audiences) > 0:
            results["audiences_handled"]["pass"] = False
            results["audiences_handled"]["issues"].append(
                f"Should have 0 Audience rows when input is ['-'], got {len(output_audiences)}"
            )
    else:
        if len(output_audiences) != len(input_audiences):
            results["audiences_handled"]["pass"] = False
            results["audiences_handled"]["issues"].append(
                f"Audience count mismatch: input={len(input_audiences)}, output={len(output_audiences)}"
            )

    # Check 3: Color not rank 1
    color_words = ["black", "white", "blue", "red", "green", "pink", "gray", "grey", "silver", "gold", "denim"]
    for var in output_variants:
        value = var.get("attribute_value", "").lower()
        rank = var.get("rank", 0)
        if any(color in value for color in color_words) and rank == 1:
            results["color_not_rank_1"]["pass"] = False
            results["color_not_rank_1"]["issues"].append(
                f"Color '{var.get('attribute_value')}' is rank 1"
            )

    # Check 4: Unique ranks per type
    for attr_type, attrs in [("Variant", output_variants), ("UseCase", output_use_cases), ("Audience", output_audiences)]:
        ranks = [a.get("rank") for a in attrs]
        if len(ranks) != len(set(ranks)):
            results["unique_ranks"]["pass"] = False
            results["unique_ranks"]["issues"].append(f"Duplicate ranks in {attr_type}: {ranks}")

    return results


def run_test(prompt_version: str, samples: List[Dict]) -> Dict:
    prompt_file = f"m08_assign_attribute_ranks{'_v2' if prompt_version == 'v2' else ''}.md"
    template = load_prompt(prompt_file)

    print(f"\n{'='*60}")
    print(f"Testing M08 {prompt_version.upper()} Prompt")
    print(f"{'='*60}")

    results = {
        "version": prompt_version,
        "samples_tested": len(samples),
        "rubric_scores": {
            "all_attributes_ranked": {"pass": 0, "fail": 0},
            "color_not_rank_1": {"pass": 0, "fail": 0},
            "audiences_handled": {"pass": 0, "fail": 0},
            "unique_ranks": {"pass": 0, "fail": 0},
        },
        "details": []
    }

    for i, sample in enumerate(samples):
        input_data = sample.get("input", {})
        title = input_data.get("title", "")[:50]
        print(f"\n[{i+1}/{len(samples)}] {title}...")

        filled_prompt = fill_template(template, input_data)
        output = call_llm(filled_prompt)

        if "error" in output:
            print(f"  ERROR: {output['error']}")
            continue

        eval_result = evaluate_output(output, input_data)

        detail = {
            "sample_idx": i,
            "title": title,
            "input_counts": {
                "variants": len(input_data.get("variants", [])),
                "use_cases": len(input_data.get("use_cases", [])),
                "audiences": input_data.get("audiences", []),
            },
            "output_counts": {
                "variants": len([a for a in output.get("attribute_table", []) if a.get("attribute_type") == "Variant"]),
                "use_cases": len([a for a in output.get("attribute_table", []) if a.get("attribute_type") == "UseCase"]),
                "audiences": len([a for a in output.get("attribute_table", []) if a.get("attribute_type") == "Audience"]),
            },
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

    rubrics = ["all_attributes_ranked", "color_not_rank_1", "audiences_handled", "unique_ranks"]

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

    parser = argparse.ArgumentParser(description="Test M08 v1 vs v2 prompts")
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
    output_file = RESULTS_DIR / f"m08_v1_vs_v2_{timestamp}.json"

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
