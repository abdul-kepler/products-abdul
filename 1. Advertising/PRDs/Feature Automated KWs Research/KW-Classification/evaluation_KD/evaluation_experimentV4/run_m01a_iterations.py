#!/usr/bin/env python3
"""
M01A Iterative Prompt Improvement Experiment

Runs the M01A prompt against test samples and evaluates using rubrics.
Tracks progress across iterations.
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o-mini"

# Test samples for M01A - brand variations (expanded for robustness)
M01A_SAMPLES = [
    {"id": "B08J8GZXKZ", "input": {"brand_name": "KitchenAid"}},
    {"id": "B0C9SPJ9ZQ", "input": {"brand_name": "Rx Crush"}},
    {"id": "B0CVQJY9C6", "input": {"brand_name": "Rx Crush"}},
    {"id": "B0BH98GL8Z", "input": {"brand_name": "Rx Crush"}},
    {"id": "B0B5W8B389", "input": {"brand_name": "Rx Crush"}},
    {"id": "B0BZYCJK89", "input": {"brand_name": "Owala"}},
    {"id": "B0BQPGJ9LQ", "input": {"brand_name": "JBL"}},
    {"id": "B0CJ4WZXQF", "input": {"brand_name": "Cisily"}},
    {"id": "B0D6YNWLTS", "input": {"brand_name": "Pioneer Camp"}},
    {"id": "B0DSHWLXG6", "input": {"brand_name": "Jikasho"}},
    {"id": "B0F42MT8JX", "input": {"brand_name": "Antarctic Star"}},
    {"id": "B000H3I2JG", "input": {"brand_name": "REVLON"}},
    {"id": "B09LCKZBTW", "input": {"brand_name": "WEBACOO"}},
    {"id": "B077YYP739", "input": {"brand_name": "Transformers"}},
    {"id": "B0D1XD1ZV3", "input": {"brand_name": "Apple"}},
    {"id": "B0875RKTQF", "input": {"brand_name": "iOttie"}},
    {"id": "B07XYRS34W", "input": {"brand_name": "THERMOS"}},
    {"id": "B01N06UEH4", "input": {"brand_name": "OXO"}},
    {"id": "B0DRDVV2GY", "input": {"brand_name": "The North Face"}},
    {"id": "B07JBJWP2W", "input": {"brand_name": "Anker"}},
]


def load_prompt() -> str:
    """Load the M01A prompt."""
    prompt_path = PROJECT_ROOT / "prompts" / "modules" / "m01a_extract_own_brand_variations.md"
    with open(prompt_path, 'r') as f:
        return f.read()


def fill_template(prompt: str, sample: dict) -> str:
    """Fill the prompt template with sample data."""
    filled = prompt
    input_data = sample.get("input", {})
    filled = filled.replace("{{brand_name}}", str(input_data.get("brand_name", "")))
    return filled


def call_gpt(prompt: str) -> dict:
    """Call GPT model with the prompt."""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are an Amazon PPC specialist. Return valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )
        result = json.loads(response.choices[0].message.content)
        return {"success": True, "output": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


def evaluate_no_unrelated_terms(variations: list, brand_name: str) -> dict:
    """
    Evaluate M01A output for "No Unrelated Terms" rubric.

    A variation is VALID if it's a plausible reference to the brand:
    - Canonical form
    - Case/spacing variant
    - Keyboard typo (adjacent keys)
    - Phonetic/spelling error
    - Truncation
    """
    if not variations:
        return {"pass": False, "reason": "No variations provided"}

    brand_lower = brand_name.lower()
    brand_no_space = brand_lower.replace(" ", "").replace("-", "")
    brand_words = brand_lower.split()

    invalid_variations = []

    # Common product/category words that are definitely NOT brand references
    product_words = {
        "bottle", "water", "speaker", "earbuds", "headphones", "phone",
        "case", "holder", "kitchen", "sink", "organizer", "jacket",
        "wireless", "bluetooth", "stainless", "steel", "plastic"
    }

    # Competitor brand names that should not appear
    competitor_brands = {
        "samsung", "apple", "sony", "bose", "lg", "google", "amazon",
        "microsoft", "dell", "hp", "lenovo", "asus", "acer"
    }

    for var in variations:
        var_lower = var.lower()
        var_no_space = var_lower.replace(" ", "").replace("-", "")
        var_words = var_lower.replace("-", " ").split()

        # Check 1: Is it exactly a product word?
        if var_lower in product_words:
            invalid_variations.append((var, "product_word"))
            continue

        # Check 2: Is it a competitor brand?
        if var_lower in competitor_brands:
            invalid_variations.append((var, "competitor_brand"))
            continue

        # Check 3: Is variation plausibly related to brand?
        # Allow if:
        # a) Contains significant portion of brand characters
        # b) Starts with same letters
        # c) Is a truncation of a multi-word brand
        # d) Is a keyboard typo (different by 1-2 characters per word)

        is_valid = False

        # a) Exact match or case variation (also remove periods for abbreviations)
        var_clean = var_no_space.replace(".", "")
        brand_clean = brand_no_space.replace(".", "")
        if var_clean == brand_clean:
            is_valid = True
        # b) First word truncation for multi-word brands
        elif len(brand_words) > 1 and var_lower == brand_words[0]:
            is_valid = True
        # c) Starts with same 2+ characters
        elif len(var_no_space) >= 2 and len(brand_no_space) >= 2:
            if var_no_space[:2] == brand_no_space[:2]:
                is_valid = True
        # d) Check character-level similarity (typos)
        # Allow if edit distance is reasonable (within 30% of length)
        if not is_valid:
            max_edits = max(2, len(brand_clean) // 3)
            edits = levenshtein_distance(var_clean, brand_clean)
            if edits <= max_edits:
                is_valid = True

        # e) For multi-word brands, check each word
        if not is_valid and len(brand_words) > 1 and len(var_words) > 1:
            # Check if most words are similar
            similar_words = 0
            for vw in var_words:
                for bw in brand_words:
                    if vw == bw or levenshtein_distance(vw, bw) <= 2:
                        similar_words += 1
                        break
            if similar_words >= len(brand_words) - 1:
                is_valid = True

        if not is_valid:
            invalid_variations.append((var, "unrelated"))

    passed = len(invalid_variations) == 0
    return {
        "pass": passed,
        "invalid_count": len(invalid_variations),
        "invalid_variations": invalid_variations[:5],
        "total_variations": len(variations)
    }


def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate Levenshtein edit distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    prev_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        curr_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = prev_row[j + 1] + 1
            deletions = curr_row[j] + 1
            substitutions = prev_row[j] + (c1 != c2)
            curr_row.append(min(insertions, deletions, substitutions))
        prev_row = curr_row

    return prev_row[-1]


def evaluate_count_in_range(variations: list) -> dict:
    """Check if 8-12 unique variations."""
    unique = list(set(variations))
    count = len(unique)
    passed = 8 <= count <= 12
    return {
        "pass": passed,
        "count": count,
        "unique_count": len(unique),
        "duplicates": len(variations) - len(unique)
    }


def evaluate_first_is_canonical(variations: list, brand_name: str) -> dict:
    """Check if first item is correct spelling."""
    if not variations:
        return {"pass": False, "reason": "No variations"}

    first = variations[0]
    # Allow case insensitive match
    passed = first.lower().replace(" ", "") == brand_name.lower().replace(" ", "")
    return {
        "pass": passed,
        "first": first,
        "expected": brand_name
    }


def evaluate_output(output: dict, sample: dict) -> dict:
    """Evaluate M01A output against all rubrics."""
    if not output.get("success"):
        return {
            "pass": False,
            "rubrics": {
                "no_unrelated_terms": {"pass": False},
                "count_in_range": {"pass": False},
                "first_is_canonical": {"pass": False}
            },
            "error": output.get("error")
        }

    result = output.get("output", {})
    variations = result.get("variations", [])
    brand_name = sample["input"]["brand_name"]

    rubrics = {
        "no_unrelated_terms": evaluate_no_unrelated_terms(variations, brand_name),
        "count_in_range": evaluate_count_in_range(variations),
        "first_is_canonical": evaluate_first_is_canonical(variations, brand_name)
    }

    all_pass = all(r["pass"] for r in rubrics.values())

    return {
        "pass": all_pass,
        "rubrics": rubrics,
        "variations": variations
    }


def run_iteration(samples: List[dict], iteration: int) -> dict:
    """Run one iteration of M01A experiment."""

    prompt = load_prompt()
    results = []

    for sample in samples:
        filled = fill_template(prompt, sample)
        output = call_gpt(filled)
        evaluation = evaluate_output(output, sample)

        results.append({
            "id": sample["id"],
            "brand": sample["input"]["brand_name"],
            "pass": evaluation["pass"],
            "rubrics": evaluation["rubrics"],
            "variations": evaluation.get("variations", [])
        })

        time.sleep(0.3)

    # Calculate metrics
    total_tests = len(samples)
    full_pass = sum(1 for r in results if r["pass"])

    # Calculate rubric-level pass rates
    rubric_passes = {}
    for rubric_name in ["no_unrelated_terms", "count_in_range", "first_is_canonical"]:
        rubric_passes[rubric_name] = sum(1 for r in results if r["rubrics"].get(rubric_name, {}).get("pass", False))

    return {
        "iteration": iteration,
        "full_pass": full_pass,
        "total": total_tests,
        "full_pass_rate": full_pass / total_tests if total_tests else 0,
        "rubric_passes": rubric_passes,
        "rubric_pass_rates": {k: v/total_tests for k, v in rubric_passes.items()},
        "results": results
    }


def main():
    print("=" * 70)
    print("M01A ITERATIVE EVALUATION - No Unrelated Terms")
    print(f"Model: {MODEL}")
    print(f"Samples: {len(M01A_SAMPLES)}")
    print("=" * 70)

    # Run single iteration to test current prompt
    print(f"\nRunning evaluation...")

    result = run_iteration(M01A_SAMPLES, 1)

    print(f"\nResults: {result['full_pass']}/{result['total']} fully passed")
    print(f"Full Pass Rate: {result['full_pass_rate']*100:.1f}%")

    print(f"\nRubric-level Results:")
    for rubric, count in result["rubric_passes"].items():
        rate = count / result["total"] * 100
        print(f"  {rubric}: {count}/{result['total']} ({rate:.0f}%)")

    print(f"\nPer-Sample Details:")
    for r in result["results"]:
        status = "PASS" if r["pass"] else "FAIL"
        print(f"\n  {r['id']} ({r['brand']}): {status}")
        for rubric, data in r["rubrics"].items():
            mark = "+" if data["pass"] else "X"
            print(f"    [{mark}] {rubric}")
            if not data["pass"] and "invalid_variations" in data:
                print(f"        Invalid: {data['invalid_variations']}")
        if r["variations"]:
            print(f"    Output: {r['variations'][:6]}...")

    # Save result
    output_dir = Path(__file__).parent / "iteration_results"
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"m01a_iter_{timestamp}.json"

    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return result


if __name__ == "__main__":
    main()
