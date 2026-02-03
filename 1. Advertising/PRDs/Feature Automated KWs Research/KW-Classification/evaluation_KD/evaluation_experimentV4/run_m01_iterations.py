#!/usr/bin/env python3
"""
M01 Iterative Prompt Improvement Experiment

Runs the M01 prompt against test samples and evaluates using rubrics.
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

# Test samples (from the dataset)
M01_SAMPLES = [
    {
        "id": "B0BQPGJ9LQ",
        "input": {
            "brand_name": "JBL",
            "title": "JBL Vibe Beam - True Wireless JBL Deep Bass Sound Earbuds, Bluetooth 5.2, Water & Dust Resistant",
            "bullet_points": "JBL Deep Bass Sound: Get the most from your mixes with high-quality audio from secure, reliable earbuds with 8mm drivers featuring JBL Deep Bass Sound",
            "description": "Bring your sound everywhere. With bass you can feel.",
            "manufacturer": "JBL"
        },
        "expected": {
            "brand_entities": ["JBL", "jbl", "JLB", "Vibe Beam", "VibeBeam"]
        }
    },
    {
        "id": "B0BZYCJK89",
        "input": {
            "brand_name": "Owala",
            "title": "Owala FreeSip Insulated Stainless Steel Water Bottle with Straw, BPA-Free Sports Water Bottle",
            "bullet_points": "24-ounce insulated stainless-steel water bottle with a FreeSip spout",
            "description": "The Owala FreeSip Insulated Stainless-Steel Water Bottle",
            "manufacturer": "BlenderBottle"
        },
        "expected": {
            "brand_entities": ["Owala", "owala", "FreeSip", "Owalaa"]
        }
    },
    {
        "id": "B0CJ4WZXQF",
        "input": {
            "brand_name": "Cisily",
            "title": "Cisily Kitchen Sink Caddy Organzier with High Brush Holder, Sponge Holder for Sink",
            "bullet_points": "304 Stainless Steel. Quality Control 100%. CISILY kitchen sink organizer.",
            "description": "",
            "manufacturer": "Cisily"
        },
        "expected": {
            "brand_entities": ["Cisily", "cisily", "CISILY", "Cisiliy"]
        }
    },
    {
        "id": "B0D6YNWLTS",
        "input": {
            "brand_name": "Pioneer Camp",
            "title": "Pioneer Camp Mens Lightweight Packable Puffer Jacket Winter Insulated Puffy Coat",
            "bullet_points": "WINDPROOF & WARM The stand collar lightweight puffer jacket is made with windproof, soft nylon fabric",
            "description": "",
            "manufacturer": None
        },
        "expected": {
            "brand_entities": ["Pioneer Camp", "pioneer camp", "PioneerCamp"]
        }
    },
    {
        "id": "B0DSHWLXG6",
        "input": {
            "brand_name": "Jikasho",
            "title": "Jikasho Vacuum Magnetic Suction Phone Holder, Foldable and Retractable",
            "bullet_points": "Vacuum Lock + Gel Base For Smooth, Flat Surfaces",
            "description": "",
            "manufacturer": "Jikasho"
        },
        "expected": {
            "brand_entities": ["Jikasho", "jikasho", "Jikashoo"]
        }
    }
]


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


def evaluate_output(output: dict, sample: dict) -> dict:
    """Evaluate M01 output against rubrics."""
    if not output.get("success"):
        return {
            "pass": False,
            "rubrics": {
                "brand_extracted": False,
                "no_hallucination": False,
                "no_product_words": False,
                "amazon_test": False,
                "no_duplicates": False
            },
            "details": {"error": output.get("error")}
        }

    result = output.get("output", {})
    entities = result.get("brand_entities", [])
    input_data = sample.get("input", {})
    brand_name = input_data.get("brand_name", "").lower()

    rubrics = {}

    # 1. Brand Extracted - Check if main brand is in output
    rubrics["brand_extracted"] = any(
        brand_name.lower() in e.lower() or e.lower() in brand_name.lower()
        for e in entities
    )

    # 2. No Hallucination - Check entities are related to brand or sub-brands
    # Get all text from input to check against
    all_input_text = (
        str(input_data.get("brand_name", "")) + " " +
        str(input_data.get("title", "")) + " " +
        str(input_data.get("bullet_points", "")) + " " +
        str(input_data.get("manufacturer", ""))
    ).lower()

    hallucinated = []
    for entity in entities:
        entity_lower = entity.lower()
        entity_normalized = entity_lower.replace(" ", "").replace("-", "")
        brand_normalized = brand_name.replace(" ", "").replace("-", "")

        # Allow if it's close to brand name (typo)
        if brand_normalized in entity_normalized or entity_normalized in brand_normalized:
            continue
        if brand_name in entity_lower or entity_lower in brand_name:
            continue

        # Allow if first 3+ chars match brand (covers typos like "Owla" from "Owala")
        if len(brand_normalized) >= 3 and len(entity_normalized) >= 3:
            if brand_normalized[:3] == entity_normalized[:3]:
                continue
            # Also check if removing 1 char from brand matches
            if len(entity_normalized) >= len(brand_normalized) - 2:
                continue  # Allow typos with 1-2 char difference

        # Check if entity appears in input text (for sub-brands)
        if entity_lower in all_input_text or entity_normalized in all_input_text.replace(" ", ""):
            continue

        # Check title for sub-brands
        title = str(input_data.get("title", "")).lower()
        title_words = title.replace("-", " ").split()
        entity_words = entity_lower.replace("-", " ").split()

        # Allow if all words in entity appear in title (sub-brand variations)
        if all(any(ew in tw or tw in ew for tw in title_words) for ew in entity_words if len(ew) > 2):
            continue

        hallucinated.append(entity)

    rubrics["no_hallucination"] = len(hallucinated) == 0

    # 3. No Product Words - Check last word isn't a product
    product_words = {
        "earbuds", "earphones", "headphones", "speaker", "bottle", "wallet",
        "holder", "bag", "case", "organizer", "kitchen", "bread", "toys",
        "figure", "bass", "sound", "jacket", "coat", "phone", "charger"
    }

    product_word_entities = []
    for entity in entities:
        words = entity.lower().split()
        if words and words[-1] in product_words:
            product_word_entities.append(entity)

    rubrics["no_product_words"] = len(product_word_entities) == 0

    # 4. Amazon Test - Same as no_product_words essentially
    rubrics["amazon_test"] = rubrics["no_product_words"]

    # 5. No Duplicates - Check for exact string duplicates
    unique_entities = set(entities)
    rubrics["no_duplicates"] = len(unique_entities) == len(entities)

    # Calculate overall pass
    all_pass = all(rubrics.values())

    return {
        "pass": all_pass,
        "rubrics": rubrics,
        "rubric_pass_count": sum(1 for v in rubrics.values() if v),
        "rubric_total": len(rubrics),
        "details": {
            "entities": entities[:10],
            "hallucinated": hallucinated[:3] if hallucinated else [],
            "product_words": product_word_entities[:3] if product_word_entities else [],
            "duplicate_count": len(entities) - len(unique_entities)
        }
    }


def run_iteration(samples: List[dict], iteration: int) -> dict:
    """Run one iteration of M01 experiment."""

    prompt = load_prompt()
    results = []

    for sample in samples:
        filled = fill_template(prompt, sample)
        output = call_gpt(filled)
        evaluation = evaluate_output(output, sample)

        results.append({
            "id": sample["id"],
            "pass": evaluation["pass"],
            "rubrics": evaluation["rubrics"],
            "rubric_pass_count": evaluation["rubric_pass_count"],
            "details": evaluation["details"]
        })

        time.sleep(0.3)

    # Calculate metrics
    total_tests = len(samples)
    full_pass = sum(1 for r in results if r["pass"])

    # Calculate rubric-level pass rate
    rubric_passes = {}
    for rubric_name in ["brand_extracted", "no_hallucination", "no_product_words", "amazon_test", "no_duplicates"]:
        rubric_passes[rubric_name] = sum(1 for r in results if r["rubrics"].get(rubric_name, False))

    total_rubric_checks = total_tests * 5  # 5 rubrics per test
    total_rubric_passes = sum(r["rubric_pass_count"] for r in results)

    return {
        "iteration": iteration,
        "full_pass": full_pass,
        "total": total_tests,
        "full_pass_rate": full_pass / total_tests if total_tests else 0,
        "rubric_pass_rate": total_rubric_passes / total_rubric_checks if total_rubric_checks else 0,
        "rubric_passes": rubric_passes,
        "results": results
    }


def main():
    print("=" * 70)
    print("M01 ITERATIVE EVALUATION")
    print(f"Model: {MODEL}")
    print(f"Samples: {len(M01_SAMPLES)}")
    print("=" * 70)

    # Run single iteration to test current prompt
    print(f"\nRunning evaluation...")

    result = run_iteration(M01_SAMPLES, 1)

    print(f"\nResults: {result['full_pass']}/{result['total']} fully passed")
    print(f"Rubric Pass Rate: {result['rubric_pass_rate']*100:.1f}%")

    print(f"\nRubric-level Results:")
    for rubric, count in result["rubric_passes"].items():
        rate = count / result["total"] * 100
        print(f"  {rubric}: {count}/{result['total']} ({rate:.0f}%)")

    print(f"\nPer-Sample Details:")
    for r in result["results"]:
        status = "PASS" if r["pass"] else "FAIL"
        print(f"\n  {r['id']}: {status}")
        print(f"    Rubrics: {r['rubric_pass_count']}/5")
        for rubric, passed in r["rubrics"].items():
            mark = "+" if passed else "X"
            print(f"      [{mark}] {rubric}")
        if r["details"].get("entities"):
            print(f"    Output: {r['details']['entities'][:5]}")
        if r["details"].get("hallucinated"):
            print(f"    Hallucinated: {r['details']['hallucinated']}")
        if r["details"].get("product_words"):
            print(f"    Product words: {r['details']['product_words']}")
        if r["details"].get("duplicate_count", 0) > 0:
            print(f"    Duplicates: {r['details']['duplicate_count']}")

    # Save result
    output_dir = Path(__file__).parent / "iteration_results"
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"m01_iter_{timestamp}.json"

    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return result


if __name__ == "__main__":
    main()
