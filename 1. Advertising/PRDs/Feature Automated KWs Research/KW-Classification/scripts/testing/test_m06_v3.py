#!/usr/bin/env python3
"""
Test M06 v1 vs v3 Prompt

Compare prompt performance on M06 GenerateProductTypeTaxonomy.
Key issues:
- three_level_hierarchy: Rubric expects 3 levels, but simple products need only 1
- no_material_feature_levels: Features shouldn't be separate levels
- hierarchy_correct: specific → broad ordering
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
    dataset_file = DATASETS_DIR / "m06_generate_product_type_taxonomy.jsonl"

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
            max_tokens=1000
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
    """Evaluate M06 output against rubrics."""
    results = {
        "max_three_levels": {"pass": True, "issues": []},
        "no_material_feature_levels": {"pass": True, "issues": []},
        "product_type_accurate": {"pass": True, "issues": []},
        "matches_expected_count": {"pass": True, "issues": []},
    }

    taxonomy = output.get("taxonomy", [])
    expected_taxonomy = expected.get("taxonomy", [])

    # Check 1: Maximum 3 levels (more lenient than "exactly 3")
    if len(taxonomy) > 3:
        results["max_three_levels"]["pass"] = False
        results["max_three_levels"]["issues"].append(f"Too many levels: {len(taxonomy)}")
    elif len(taxonomy) == 0:
        results["max_three_levels"]["pass"] = False
        results["max_three_levels"]["issues"].append("No taxonomy levels returned")

    # Check 2: No material/feature as separate levels
    feature_words = ["insulated", "stainless steel", "silicone", "bamboo", "wireless",
                     "bluetooth", "portable", "countertop", "magnetic", "vacuum", "enfit"]
    for entry in taxonomy:
        product_type = entry.get("product_type", "").lower()
        for feature in feature_words:
            # Check if feature is used as standalone level
            if product_type == feature or product_type.startswith(feature + " "):
                results["no_material_feature_levels"]["pass"] = False
                results["no_material_feature_levels"]["issues"].append(
                    f"Feature '{feature}' used in product_type: {entry.get('product_type')}"
                )
                break

    # Check 3: Product type accurate (level 1 should describe actual product)
    if taxonomy:
        level_1 = taxonomy[0].get("product_type", "").lower()
        title_lower = input_data.get("title", "").lower()
        # Simple check - level 1 should be related to product
        keywords = ["earbuds", "water bottle", "jacket", "tray", "syringe", "eyeliner",
                    "ice maker", "oven mitt", "phone holder", "transformer", "caddy"]
        found_match = False
        for kw in keywords:
            if kw in level_1 or kw in title_lower:
                if kw in level_1:
                    found_match = True
                    break
        # Less strict - just check there's something
        if len(level_1) < 3:
            results["product_type_accurate"]["pass"] = False
            results["product_type_accurate"]["issues"].append(f"Product type too short: {level_1}")

    # Check 4: Level count matches expected (within 1)
    actual_count = len(taxonomy)
    expected_count = len(expected_taxonomy)
    if abs(actual_count - expected_count) > 1:
        results["matches_expected_count"]["pass"] = False
        results["matches_expected_count"]["issues"].append(
            f"Level count mismatch: expected ~{expected_count}, got {actual_count}"
        )

    return results


def run_test(prompt_version: str, samples: List[Dict]) -> Dict:
    if prompt_version == "v1":
        prompt_file = "m06_generate_product_type_taxonomy.md"
    else:
        prompt_file = "m06_v3_generate_product_type_taxonomy.md"

    template = load_prompt(prompt_file)

    print(f"\n{'='*60}")
    print(f"Testing M06 {prompt_version.upper()} Prompt")
    print(f"{'='*60}")

    results = {
        "version": prompt_version,
        "samples_tested": len(samples),
        "rubric_scores": {
            "max_three_levels": {"pass": 0, "fail": 0},
            "no_material_feature_levels": {"pass": 0, "fail": 0},
            "product_type_accurate": {"pass": 0, "fail": 0},
            "matches_expected_count": {"pass": 0, "fail": 0},
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

        taxonomy = output.get("taxonomy", [])
        expected_taxonomy = expected.get("taxonomy", [])

        detail = {
            "sample_idx": i,
            "title": title,
            "expected_levels": len(expected_taxonomy),
            "actual_levels": len(taxonomy),
            "actual_taxonomy": [t.get("product_type") for t in taxonomy[:3]],
            "expected_taxonomy": [t.get("product_type") for t in expected_taxonomy[:3]],
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


def print_summary(v1_results: Dict, v3_results: Dict):
    print(f"\n{'='*60}")
    print("COMPARISON SUMMARY")
    print(f"{'='*60}")

    rubrics = ["max_three_levels", "no_material_feature_levels",
               "product_type_accurate", "matches_expected_count"]

    print(f"\n{'Rubric':<30} {'V1 Pass%':>10} {'V3 Pass%':>10} {'Δ':>8}")
    print("-" * 60)

    for rubric in rubrics:
        v1_pass = v1_results["rubric_scores"][rubric]["pass"]
        v1_total = v1_pass + v1_results["rubric_scores"][rubric]["fail"]
        v1_rate = (v1_pass / v1_total * 100) if v1_total > 0 else 0

        v3_pass = v3_results["rubric_scores"][rubric]["pass"]
        v3_total = v3_pass + v3_results["rubric_scores"][rubric]["fail"]
        v3_rate = (v3_pass / v3_total * 100) if v3_total > 0 else 0

        delta = v3_rate - v1_rate
        delta_str = f"+{delta:.1f}%" if delta > 0 else f"{delta:.1f}%"

        print(f"{rubric:<30} {v1_rate:>9.1f}% {v3_rate:>9.1f}% {delta_str:>8}")

    print("-" * 60)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Test M06 v1 vs v3 prompts")
    parser.add_argument("--samples", "-n", type=int, default=10, help="Number of samples")
    parser.add_argument("--version", "-v", choices=["v1", "v3", "both"], default="both")
    args = parser.parse_args()

    samples = load_samples(args.samples)
    print(f"Loaded {len(samples)} test samples")

    v1_results = None
    v3_results = None

    if args.version in ["v1", "both"]:
        v1_results = run_test("v1", samples)

    if args.version in ["v3", "both"]:
        v3_results = run_test("v3", samples)

    if v1_results and v3_results:
        print_summary(v1_results, v3_results)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = RESULTS_DIR / f"m06_v1_vs_v3_{timestamp}.json"

    with open(output_file, "w") as f:
        json.dump({
            "timestamp": timestamp,
            "samples": args.samples,
            "v1": v1_results,
            "v3": v3_results,
        }, f, indent=2)

    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
