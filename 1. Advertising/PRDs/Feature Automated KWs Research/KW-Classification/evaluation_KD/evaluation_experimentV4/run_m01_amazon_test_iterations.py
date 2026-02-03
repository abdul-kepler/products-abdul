#!/usr/bin/env python3
"""
M01 Amazon Test Iterative Prompt Improvement

Runs M01 prompt against 20 samples and evaluates the Amazon Test rubric.
"""

import os
import sys
import json
import csv
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

# CSV data path
CSV_PATH = PROJECT_ROOT / "experiment_results" / "20260115_v1_01" / "M01_ExtractOwnBrandEntities" / "M01_ExtractOwnBrandEntities_V1.csv"


def load_samples(limit: int = 20) -> List[dict]:
    """Load samples from CSV."""
    samples = []
    with open(CSV_PATH, 'r') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= limit:
                break
            inp = json.loads(row['input'])
            samples.append({
                'id': row['ASIN'],
                'input': inp,
                'expected': json.loads(row['expected']) if row.get('expected') else {}
            })
    return samples


def load_prompt() -> str:
    """Load the M01 prompt."""
    prompt_path = PROJECT_ROOT / "prompts" / "modules" / "m01_extract_own_brand_entities.md"
    with open(prompt_path, 'r') as f:
        return f.read()


def fill_template(prompt: str, sample: dict) -> str:
    """Fill the prompt template with sample data."""
    filled = prompt
    input_data = sample.get("input", {})
    filled = filled.replace("{{brand_name}}", str(input_data.get("brand_name", "")))
    filled = filled.replace("{{title}}", str(input_data.get("title", "")))
    filled = filled.replace("{{bullet_points}}", str(input_data.get("bullet_points", "")))
    filled = filled.replace("{{description}}", str(input_data.get("description", "")))
    filled = filled.replace("{{manufacturer}}", str(input_data.get("manufacturer", "")))
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


def evaluate_amazon_test(output: dict, sample: dict) -> dict:
    """
    Evaluate the Amazon Test rubric specifically.

    FAIL conditions:
    - Standalone generic word that is purchasable (wallet, bottle, earbuds, toys)
    - Generic phrase ending in purchasable product
    - Manufacturer included when different from brand_name

    PASS conditions:
    - All entities are brand/trademark names or trademarked product lines
    - No manufacturer contamination when manufacturer != brand_name
    """
    if not output.get("success"):
        return {
            "pass": False,
            "reason": "API error",
            "details": output.get("error")
        }

    result = output.get("output", {})
    entities = result.get("brand_entities", [])
    input_data = sample.get("input", {})
    brand_name = input_data.get("brand_name", "")
    manufacturer = input_data.get("manufacturer", "")
    title = input_data.get("title", "")

    # Common product words that fail Amazon test
    product_words = {
        "earbuds", "earphones", "headphones", "speaker", "speakers", "bottle", "bottles",
        "wallet", "wallets", "holder", "holders", "bag", "bags", "case", "cases",
        "organizer", "organizers", "kitchen", "bread", "toys", "toy", "figure", "figures",
        "bass", "sound", "jacket", "jackets", "coat", "coats", "phone", "phones",
        "charger", "chargers", "caddy", "tray", "trays", "maker", "makers",
        "sponge", "brush", "crusher", "syringe", "adapter", "pouch", "pouches"
    }

    # Feature words
    feature_words = {
        "wireless", "waterproof", "deep", "slim", "rfid", "insulated", "stainless",
        "portable", "foldable", "magnetic", "vacuum", "bluetooth"
    }

    failures = []

    # Check each entity
    for entity in entities:
        entity_lower = entity.lower()
        words = entity_lower.split()
        last_word = words[-1] if words else ""

        # Check 1: Entity ends with product word
        if last_word in product_words:
            failures.append(f"'{entity}' ends with product word '{last_word}'")
            continue

        # Check 2: Entity ends with feature word
        if last_word in feature_words:
            failures.append(f"'{entity}' ends with feature word '{last_word}'")
            continue

        # Check 3: Standalone generic word
        if len(words) == 1 and entity_lower in product_words:
            failures.append(f"'{entity}' is standalone purchasable product")
            continue

        # Check 4: Manufacturer contamination
        if manufacturer and manufacturer != brand_name and manufacturer.lower() != brand_name.lower():
            manufacturer_lower = manufacturer.lower()
            # Check if entity contains manufacturer (not brand)
            if manufacturer_lower in entity_lower or entity_lower in manufacturer_lower:
                # But make sure it's not the brand
                brand_lower = brand_name.lower()
                if brand_lower not in entity_lower and entity_lower not in brand_lower:
                    failures.append(f"'{entity}' is manufacturer (not brand)")
                    continue

    passed = len(failures) == 0

    return {
        "pass": passed,
        "entity_count": len(entities),
        "failure_count": len(failures),
        "failures": failures[:5],  # Limit to 5 for display
        "entities": entities[:10]
    }


def run_iteration(samples: List[dict], iteration_name: str = "") -> dict:
    """Run one iteration of evaluation."""
    prompt = load_prompt()
    results = []

    for i, sample in enumerate(samples):
        filled = fill_template(prompt, sample)
        output = call_gpt(filled)
        evaluation = evaluate_amazon_test(output, sample)

        results.append({
            "id": sample["id"],
            "pass": evaluation["pass"],
            "entity_count": evaluation.get("entity_count", 0),
            "failures": evaluation.get("failures", []),
            "entities": evaluation.get("entities", [])
        })

        # Show progress
        status = "PASS" if evaluation["pass"] else "FAIL"
        print(f"  [{i+1}/{len(samples)}] {sample['id']}: {status}", end="")
        if not evaluation["pass"] and evaluation.get("failures"):
            print(f" - {evaluation['failures'][0][:50]}...", end="")
        print()

        time.sleep(0.3)

    # Calculate pass rate
    pass_count = sum(1 for r in results if r["pass"])
    pass_rate = pass_count / len(samples) * 100 if samples else 0

    return {
        "iteration": iteration_name,
        "pass_count": pass_count,
        "total": len(samples),
        "pass_rate": pass_rate,
        "results": results
    }


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", "-l", type=int, default=20, help="Number of samples")
    parser.add_argument("--name", "-n", type=str, default="baseline", help="Iteration name")
    args = parser.parse_args()

    print("=" * 70)
    print("M01 AMAZON TEST EVALUATION")
    print(f"Model: {MODEL}")
    print(f"Samples: {args.limit}")
    print(f"Iteration: {args.name}")
    print("=" * 70)

    samples = load_samples(args.limit)
    print(f"\nLoaded {len(samples)} samples\n")

    result = run_iteration(samples, args.name)

    print(f"\n" + "=" * 70)
    print(f"AMAZON TEST PASS RATE: {result['pass_rate']:.1f}%")
    print(f"Passed: {result['pass_count']}/{result['total']}")
    print("=" * 70)

    # Show failures summary
    failures = [r for r in result["results"] if not r["pass"]]
    if failures:
        print(f"\nFailed samples ({len(failures)}):")
        for f in failures[:10]:
            print(f"  {f['id']}: {f['failures'][:2]}")

    # Save result
    output_dir = Path(__file__).parent / "iteration_results"
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"m01_amazon_test_{args.name}_{timestamp}.json"

    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"\nResults saved to: {output_path}")
    return result


if __name__ == "__main__":
    main()
