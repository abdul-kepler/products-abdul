#!/usr/bin/env python3
"""
Test M07 v2 Prompt

Compare v1 vs v2 prompt performance on M07 ExtractProductAttributes.
Tests the key rubrics:
- specs_preserve_units: Must copy specs verbatim
- attributes_from_listing: Must extract only from listing
- audiences_explicit_or_dash: Must use ["-"] for generic products
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

from openai import OpenAI

# Paths
PROMPTS_DIR = PROJECT_ROOT / "prompts" / "modules"
DATASETS_DIR = PROJECT_ROOT / "datasets"
RESULTS_DIR = PROJECT_ROOT / "experiment_results"

client = OpenAI()


def load_prompt(filename: str) -> str:
    """Load prompt from file."""
    with open(PROMPTS_DIR / filename, "r", encoding="utf-8") as f:
        return f.read()


def load_samples(n: int = 10) -> List[Dict]:
    """Load M07 test samples."""
    samples = []
    dataset_file = DATASETS_DIR / "m07_extract_product_attributes.jsonl"

    with open(dataset_file, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= n:
                break
            if line.strip():
                samples.append(json.loads(line))

    return samples


def fill_template(template: str, input_data: dict) -> str:
    """Fill placeholders in prompt template."""
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
    """Call LLM and parse response."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=2000
        )
        content = response.choices[0].message.content

        # Extract JSON
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
    """Evaluate M07 output against rubrics."""
    results = {
        "specs_preserve_units": {"pass": True, "issues": []},
        "attributes_from_listing": {"pass": True, "issues": []},
        "audiences_explicit_or_dash": {"pass": True, "issues": []},
    }

    variants = output.get("variants", [])
    audiences = output.get("audiences", [])

    # Combine input text for checking
    title = input_data.get("title", "")
    bullets = input_data.get("bullet_points", "")
    desc = input_data.get("description", "")
    listing_text = f"{title} {bullets} {desc}".lower()

    # Check audiences_explicit_or_dash
    target_audience = input_data.get("target_audience", "")
    has_explicit_audience = bool(target_audience) or any(
        marker in title.lower() for marker in ["men's", "mens", "women's", "womens", "kids", "children"]
    )

    banned_audiences = [
        "adults", "music lovers", "fitness enthusiasts", "outdoor enthusiasts",
        "homeowners", "commuters", "travelers", "tech-savvy", "energy-conscious"
    ]

    if not has_explicit_audience:
        # Should be ["-"]
        if audiences != ["-"] and audiences != []:
            for aud in audiences:
                if aud != "-":
                    aud_lower = aud.lower()
                    is_banned = any(banned in aud_lower for banned in banned_audiences)
                    if is_banned:
                        results["audiences_explicit_or_dash"]["pass"] = False
                        results["audiences_explicit_or_dash"]["issues"].append(
                            f"Generic audience '{aud}' used for non-targeted product"
                        )

    # Check attributes_from_listing - look for invented terms
    invented_terms = ["compact", "metallic finish", "lightweight", "durable", "sleek"]
    for var in variants:
        var_lower = var.lower()
        for term in invented_terms:
            if term in var_lower and term not in listing_text:
                results["attributes_from_listing"]["pass"] = False
                results["attributes_from_listing"]["issues"].append(
                    f"'{var}' contains '{term}' not found in listing"
                )

    return results


def run_test(prompt_version: str, samples: List[Dict]) -> Dict:
    """Run test with specified prompt version."""
    prompt_file = f"m07_extract_product_attributes{'_v2' if prompt_version == 'v2' else ''}.md"
    template = load_prompt(prompt_file)

    print(f"\n{'='*60}")
    print(f"Testing M07 {prompt_version.upper()} Prompt")
    print(f"{'='*60}")

    results = {
        "version": prompt_version,
        "samples_tested": len(samples),
        "rubric_scores": {
            "specs_preserve_units": {"pass": 0, "fail": 0},
            "attributes_from_listing": {"pass": 0, "fail": 0},
            "audiences_explicit_or_dash": {"pass": 0, "fail": 0},
        },
        "details": []
    }

    for i, sample in enumerate(samples):
        input_data = sample.get("input", {})
        expected = sample.get("expected", {})

        # Get identifier
        title = input_data.get("title", "")[:50]
        print(f"\n[{i+1}/{len(samples)}] {title}...")

        # Fill and call
        filled_prompt = fill_template(template, input_data)
        output = call_llm(filled_prompt)

        if "error" in output:
            print(f"  ERROR: {output['error']}")
            continue

        # Evaluate
        eval_result = evaluate_output(output, input_data, expected)

        detail = {
            "sample_idx": i,
            "title": title,
            "output": {
                "variants": output.get("variants", [])[:5],
                "audiences": output.get("audiences", []),
            },
            "evaluation": eval_result
        }
        results["details"].append(detail)

        # Update scores
        for rubric, result in eval_result.items():
            if result["pass"]:
                results["rubric_scores"][rubric]["pass"] += 1
                print(f"  ✓ {rubric}")
            else:
                results["rubric_scores"][rubric]["fail"] += 1
                print(f"  ✗ {rubric}: {result['issues'][:1]}")

    return results


def print_summary(v1_results: Dict, v2_results: Dict):
    """Print comparison summary."""
    print(f"\n{'='*60}")
    print("COMPARISON SUMMARY")
    print(f"{'='*60}")

    rubrics = ["specs_preserve_units", "attributes_from_listing", "audiences_explicit_or_dash"]

    print(f"\n{'Rubric':<35} {'V1 Pass%':>10} {'V2 Pass%':>10} {'Δ':>8}")
    print("-" * 65)

    for rubric in rubrics:
        v1_pass = v1_results["rubric_scores"][rubric]["pass"]
        v1_total = v1_pass + v1_results["rubric_scores"][rubric]["fail"]
        v1_rate = (v1_pass / v1_total * 100) if v1_total > 0 else 0

        v2_pass = v2_results["rubric_scores"][rubric]["pass"]
        v2_total = v2_pass + v2_results["rubric_scores"][rubric]["fail"]
        v2_rate = (v2_pass / v2_total * 100) if v2_total > 0 else 0

        delta = v2_rate - v1_rate
        delta_str = f"+{delta:.1f}%" if delta > 0 else f"{delta:.1f}%"

        print(f"{rubric:<35} {v1_rate:>9.1f}% {v2_rate:>9.1f}% {delta_str:>8}")

    print("-" * 65)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Test M07 v1 vs v2 prompts")
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

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = RESULTS_DIR / f"m07_v1_vs_v2_{timestamp}.json"

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
