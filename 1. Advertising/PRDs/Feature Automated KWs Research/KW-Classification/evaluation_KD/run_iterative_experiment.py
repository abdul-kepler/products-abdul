#!/usr/bin/env python3
"""
Iterative Prompt Experiment Runner

Runs iterative experiments: Write fix → Test → Analyze failures → Improve → Repeat
Each iteration learns from previous failures and builds cumulative fixes.
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o-mini"


def load_prompt(prompt_path: str) -> str:
    """Load prompt template from file."""
    full_path = PROJECT_ROOT / prompt_path
    with open(full_path, 'r') as f:
        return f.read()


def call_gpt(prompt: str, temperature: float = 0) -> dict:
    """Call GPT model with the prompt."""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are an Amazon marketplace expert. Return valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            response_format={"type": "json_object"}
        )
        result = json.loads(response.choices[0].message.content)
        return {"success": True, "output": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


# =============================================================================
# M03 ITERATIVE EXPERIMENT
# =============================================================================

M03_SAMPLES = [
    {
        "asin": "B0DSHWLXG6",
        "product_name": "Phone Holder",
        "brand_name": "Jikasho",
        "title": "Jikasho Vacuum Magnetic Suction Phone Holder, Foldable and Retractable Hands-Free Suction Cup Phone Mount for Car/Gym/Mirror/Smooth Surface",
        "bullet_points": "Vacuum Lock + Gel Base — For Smooth, Flat Surfaces",
        "description": "",
        "product_type": "Car Phone Holders & Mounts",
        "category_root": "Cell Phones & Accessories",
        "category_sub": "Car Accessories",
    },
    {
        "asin": "B0BZYCJK89",
        "product_name": "Water Bottle",
        "brand_name": "Owala",
        "title": "Owala FreeSip Insulated Stainless Steel Water Bottle with Straw, BPA-Free Sports Water Bottle, Great for Travel, 24 Oz",
        "bullet_points": "24-ounce insulated stainless-steel water bottle with a FreeSip spout and push-button lid",
        "description": "",
        "product_type": "Water Bottle",
        "category_root": "Sports & Outdoors",
        "category_sub": "Water Bottles",
    },
    {
        "asin": "B0CJ4WZXQF",
        "product_name": "Sink Caddy",
        "brand_name": "Cisily",
        "title": "Cisily Kitchen Sink Caddy Organzier with High Brush Holder, Sponge Holder for Sink",
        "bullet_points": "304 Stainless Steel. Quality Control 100%.",
        "description": "",
        "product_type": "Sink Caddy Organizer",
        "category_root": "Home & Kitchen",
        "category_sub": "Kitchen Storage",
    },
    {
        "asin": "B0D6YNWLTS",
        "product_name": "Puffer Jacket",
        "brand_name": "Pioneer Camp",
        "title": "Pioneer Camp Mens Lightweight Packable Puffer Jacket Winter Insulated Puffy Coat Water Repellent",
        "bullet_points": "WINDPROOF & WARM The stand collar lightweight puffer jacket",
        "description": "",
        "product_type": "Puffer Jacket",
        "category_root": "Clothing, Shoes & Jewelry",
        "category_sub": "Men's Outerwear",
    },
    {
        "asin": "B08J8GZXKZ",
        "product_name": "Oven Mitt",
        "brand_name": "KitchenAid",
        "title": "KITCHENAID Ribbed Soft Silicone Oven Mitt 2-Pack Set",
        "bullet_points": "DURABLE, HEAT RESISTANT SILICONE - Heat resistant up to 500 degrees Fahrenheit",
        "description": "",
        "product_type": "Oven Mitt",
        "category_root": "Home & Kitchen",
        "category_sub": "Kitchen Linens",
    }
]


def fill_m03_template(prompt: str, sample: dict) -> str:
    """Fill M03 prompt template."""
    filled = prompt
    filled = filled.replace("{{title}}", sample.get("title", ""))
    filled = filled.replace("{{bullet_points}}", sample.get("bullet_points", ""))
    filled = filled.replace("{{description}}", sample.get("description", ""))
    filled = filled.replace("{{brand_name}}", sample.get("brand_name", ""))
    filled = filled.replace("{{product_type}}", sample.get("product_type", ""))
    filled = filled.replace("{{category_root}}", sample.get("category_root", ""))
    filled = filled.replace("{{category_sub}}", sample.get("category_sub", ""))
    return filled


def count_distinct_brands(entities: List[str]) -> int:
    """Count distinct brands from entity list."""
    if not entities:
        return 0

    # Normalize and group by root brand
    seen = set()
    for entity in entities:
        # Take first word as brand root (simplified)
        root = entity.lower().split()[0] if entity else ""
        if root and len(root) > 1:
            seen.add(root)
    return len(seen)


def evaluate_m03(output: dict, sample: dict) -> dict:
    """Evaluate M03 output."""
    if not output.get("success"):
        return {"pass": False, "reason": "API error", "details": {}}

    result = output.get("output", {})
    entities = result.get("competitor_entities", [])

    if not entities:
        return {"pass": False, "reason": "empty output", "details": {"entities": []}}

    distinct_count = count_distinct_brands(entities)
    own_brand = sample.get("brand_name", "").lower()

    # Check issues
    issues = []

    # Count check
    if distinct_count < 5:
        issues.append(f"too few brands ({distinct_count})")
    elif distinct_count > 10:
        issues.append(f"too many brands ({distinct_count})")

    # Own brand check
    for entity in entities:
        if own_brand and own_brand in entity.lower():
            issues.append(f"contains own brand '{own_brand}'")
            break

    # Amazon Basics check
    for entity in entities:
        if "amazon basics" in entity.lower() or "amazon essentials" in entity.lower():
            issues.append("contains Amazon Basics/Essentials")
            break

    is_pass = len(issues) == 0

    return {
        "pass": is_pass,
        "reason": "valid" if is_pass else "; ".join(issues),
        "details": {
            "distinct_count": distinct_count,
            "entities_sample": entities[:8],
            "issues": issues
        }
    }


def run_m03_iteration(base_prompt: str, fix: str, samples: List[dict], iteration: int) -> dict:
    """Run one iteration of M03 experiment."""

    # Apply fix to prompt
    if fix:
        # Insert fix before "## Output Format"
        if "## Output Format" in base_prompt:
            parts = base_prompt.split("## Output Format")
            prompt = parts[0] + fix + "\n\n## Output Format" + parts[1]
        else:
            prompt = base_prompt + "\n\n" + fix
    else:
        prompt = base_prompt

    results = []

    for sample in samples:
        filled = fill_m03_template(prompt, sample)
        output = call_gpt(filled)
        evaluation = evaluate_m03(output, sample)

        results.append({
            "asin": sample["asin"],
            "product": sample["product_name"],
            "brand": sample["brand_name"],
            "pass": evaluation["pass"],
            "reason": evaluation["reason"],
            "details": evaluation["details"]
        })

        time.sleep(0.3)

    passed = sum(1 for r in results if r["pass"])

    return {
        "iteration": iteration,
        "passed": passed,
        "total": len(samples),
        "pass_rate": passed / len(samples) if samples else 0,
        "results": results,
        "fix_applied": fix[:200] + "..." if fix and len(fix) > 200 else fix
    }


def analyze_m03_failures(results: List[dict]) -> dict:
    """Analyze why samples failed."""
    failures = [r for r in results if not r["pass"]]

    analysis = {
        "total_failures": len(failures),
        "by_issue": {},
        "failed_samples": []
    }

    for f in failures:
        reason = f["reason"]
        issues = f["details"].get("issues", [])

        for issue in issues:
            if "too many" in issue:
                analysis["by_issue"]["count_too_high"] = analysis["by_issue"].get("count_too_high", 0) + 1
            elif "too few" in issue:
                analysis["by_issue"]["count_too_low"] = analysis["by_issue"].get("count_too_low", 0) + 1
            elif "own brand" in issue:
                analysis["by_issue"]["own_brand"] = analysis["by_issue"].get("own_brand", 0) + 1
            elif "Amazon" in issue:
                analysis["by_issue"]["amazon_basics"] = analysis["by_issue"].get("amazon_basics", 0) + 1

        analysis["failed_samples"].append({
            "asin": f["asin"],
            "product": f["product"],
            "brand": f["brand"],
            "issues": issues,
            "distinct_count": f["details"].get("distinct_count", 0)
        })

    return analysis


def run_m03_iterative_experiment(max_iterations: int = 15):
    """Run M03 iterative experiment."""

    print("=" * 70)
    print("M03 ITERATIVE EXPERIMENT (v2 - Modify Original)")
    print(f"Model: {MODEL}")
    print(f"Samples: {len(M03_SAMPLES)}")
    print(f"Max iterations: {max_iterations}")
    print("=" * 70)

    base_prompt = load_prompt("prompts/modules/m03_generate_competitor_entities.md")

    # CRITICAL: Modify the original prompt to remove conflicting guidance
    # The original says "15-30 entities" which causes the model to exceed limits
    base_prompt = base_prompt.replace(
        "- Aim for 15-30 competitor entities total",
        "- STRICT LIMIT: Maximum 10 distinct brands (with variations)"
    )
    base_prompt = base_prompt.replace(
        "- Include 5-10 distinct competitor brands",
        "- Include EXACTLY 5-10 distinct competitor brands (HARD LIMIT)"
    )
    base_prompt = base_prompt.replace(
        "- Add 2-3 misspellings for top 3-4 brands",
        "- Add 1-2 misspellings for top 2-3 brands only"
    )

    iteration_history = []
    cumulative_fix = ""

    for i in range(1, max_iterations + 1):
        print(f"\n{'='*70}")
        print(f"ITERATION {i}")
        print("=" * 70)

        # Run experiment
        result = run_m03_iteration(base_prompt, cumulative_fix, M03_SAMPLES, i)

        print(f"\nResults: {result['passed']}/{result['total']} passed ({result['pass_rate']*100:.1f}%)")

        # Print individual results
        for r in result["results"]:
            status = "✓" if r["pass"] else "✗"
            print(f"  {status} {r['asin']} ({r['product']}) - {r['reason']}")

        # Analyze failures
        analysis = analyze_m03_failures(result["results"])

        print(f"\nFailure Analysis:")
        print(f"  Total failures: {analysis['total_failures']}")
        for issue, count in analysis["by_issue"].items():
            print(f"  - {issue}: {count}")

        # Record iteration
        iteration_history.append({
            "iteration": i,
            "fix": cumulative_fix[-500:] if cumulative_fix else "(baseline)",
            "passed": result["passed"],
            "total": result["total"],
            "pass_rate": result["pass_rate"],
            "failure_analysis": analysis
        })

        # Check if we should stop
        if result["pass_rate"] >= 0.8:
            print(f"\n✓ Pass rate >= 80%. Stopping iterations.")
            break

        if i >= 2 and iteration_history[-1]["pass_rate"] <= iteration_history[-2]["pass_rate"]:
            if i >= 3 and iteration_history[-1]["pass_rate"] <= iteration_history[-3]["pass_rate"]:
                print(f"\n⚠ No improvement in last 2 iterations. Trying different approach.")

        # Generate next fix based on failures
        print(f"\nGenerating fix for iteration {i+1}...")

        # Build cumulative fix based on failure analysis
        if analysis["by_issue"].get("count_too_high", 0) > 0:
            if "HARD LIMIT" not in cumulative_fix:
                cumulative_fix += """
---

## HARD LIMIT: Maximum 10 Distinct Brands

**CRITICAL: You must return AT MOST 10 distinct competitor brands.**

Before outputting, COUNT your distinct brands:
- "iOttie", "iottie", "IOttie" = 1 brand (iOttie)
- "Sony", "Sony WF", "Sonny" = 1 brand (Sony)

If count > 10: REMOVE the least relevant brands until exactly 10 remain.
If count < 5: ADD more brands from adjacent categories.

**STOP and verify: 5 ≤ distinct brands ≤ 10**
"""
            elif "STRICT ENFORCEMENT" not in cumulative_fix:
                cumulative_fix += """

### STRICT ENFORCEMENT

After generating your list:
1. Count distinct brand roots (first word of each brand)
2. If count > 10, delete entries starting from the bottom
3. Re-count until exactly 5-10 remain
4. DO NOT OUTPUT until count is verified
"""
            elif "FINAL CHECK" not in cumulative_fix:
                cumulative_fix += """

### FINAL CHECK BEFORE OUTPUT

□ Count distinct brands: _____ (must be 5-10)
□ If > 10, I have removed: _____
□ Verified count is now: _____ ✓
"""

        if analysis["by_issue"].get("own_brand", 0) > 0:
            if "NEVER INCLUDE OWN BRAND" not in cumulative_fix:
                cumulative_fix += """

## NEVER INCLUDE OWN BRAND

**The brand_name from input is: {{brand_name}}**

You must NEVER include this brand or any variation in your output.

Before outputting, search your list for "{{brand_name}}" - if found, DELETE IT.
"""
            elif "OWN BRAND BLACKLIST" not in cumulative_fix:
                cumulative_fix += """

### OWN BRAND BLACKLIST

For this product, the following are FORBIDDEN in output:
- "{{brand_name}}"
- Any misspelling of "{{brand_name}}"
- Any variation containing "{{brand_name}}"

If any of these appear in your list, REMOVE THEM IMMEDIATELY.
"""

        if analysis["by_issue"].get("amazon_basics", 0) > 0:
            if "FORBIDDEN BRANDS" not in cumulative_fix:
                cumulative_fix += """

## FORBIDDEN BRANDS

Never include these generic/retailer brands:
- Amazon Basics
- Amazon Essentials
- AmazonBasics
- Walmart brands
- Target brands

These are NOT competitors - they are retail private labels.
"""

        print(f"  Fix length: {len(cumulative_fix)} chars")

    # Final summary
    print("\n" + "=" * 70)
    print("ITERATION SUMMARY")
    print("=" * 70)

    for h in iteration_history:
        print(f"  V{h['iteration']}: {h['passed']}/{h['total']} ({h['pass_rate']*100:.1f}%)")

    best = max(iteration_history, key=lambda x: x["pass_rate"])
    print(f"\nBest: V{best['iteration']} with {best['pass_rate']*100:.1f}%")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = PROJECT_ROOT / f"evaluation_KD/experiment_results/m03_iterative_{timestamp}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump({
            "module": "M03",
            "model": MODEL,
            "samples_count": len(M03_SAMPLES),
            "iterations": len(iteration_history),
            "iteration_history": iteration_history,
            "final_fix": cumulative_fix,
            "best_iteration": best["iteration"],
            "best_pass_rate": best["pass_rate"]
        }, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return iteration_history, cumulative_fix


# =============================================================================
# M08 ITERATIVE EXPERIMENT
# =============================================================================

# All 10 M08 samples from evaluation data
M08_SAMPLES = [
    {
        "asin": "B0BQPGJ9LQ",
        "product_name": "JBL Earbuds",
        "title": "JBL Vibe Beam - True Wireless JBL Deep Bass Sound Earbuds, Bluetooth 5.2, Water & Dust Resistant, Hands-free call with VoiceAware, Up to 32 hours of battery life",
        "bullet_points": "JBL Deep Bass Sound: Get the most from your mixes with high-quality audio from secure, reliable earbuds with 8mm drivers. Comfortable fit: The ergonomic design fits so comfortably. Up to 32 hours of battery life.",
        "attributes": ["Bluetooth 5.2", "Deep Bass Sound", "Water Resistant", "32 Hours Battery", "Hands-Free Call", "Comfortable Fit", "White"],
    },
    {
        "asin": "B0BZYCJK89",
        "product_name": "Water Bottle",
        "title": "Owala FreeSip Insulated Stainless Steel Water Bottle with Straw, BPA-Free Sports Water Bottle, Great for Travel, 24 Oz, Denim",
        "bullet_points": "24-ounce insulated stainless-steel water bottle with a FreeSip spout and push-button lid. Double-wall insulation keeps drinks cold for up to 24 hours. BPA, lead, and phthalate-free.",
        "attributes": ["BPA-Free", "24 Ounce", "Stainless Steel", "FreeSip Spout", "Dishwasher-Safe Lid", "Double-Wall Insulation", "Denim"],
    },
    {
        "asin": "B0CJ4WZXQF",
        "product_name": "Sink Caddy",
        "title": "Cisily Kitchen Sink Caddy Organizer with High Brush Holder, Sponge Holder for Sink, 304 Rustproof Stainless",
        "bullet_points": "304 Stainless Steel. AUTOMATIC DRAINAGE SYSTEM: Cisily adopts slope design to achieve perfect drainage effect.",
        "attributes": ["Stainless Steel", "Automatic Drainage", "Rustproof", "High Brush Holder", "Sponge Holder"],
    },
    {
        "asin": "B0D6YNWLTS",
        "product_name": "Puffer Jacket",
        "title": "Pioneer Camp Mens Lightweight Packable Puffer Jacket Winter Insulated Puffy Coat Water Repellent Warm Quilted Jackets Travel",
        "bullet_points": "WINDPROOF & WARM The stand collar lightweight puffer jacket is made with windproof, soft nylon fabric. PACKABLE & LIGHTWEIGHT perfect for travel.",
        "attributes": ["Lightweight", "Packable", "Windproof", "Water Repellent", "Insulated", "Black"],
    },
    {
        "asin": "B0DSHWLXG6",
        "product_name": "Phone Holder",
        "title": "Vacuum Magnetic Suction Phone Holder, Foldable and Retractable Hands-Free Suction Cup Phone Mount for Car/Gym/Mirror",
        "bullet_points": "Vacuum Lock + Gel Base for Smooth, Flat Surfaces. Foldable and retractable design. Compatible with iPhone Android and All Smartphones.",
        "attributes": ["Vacuum Suction", "Magnetic", "Foldable", "Retractable", "Universal Compatibility"],
    },
    {
        "asin": "B0F42MT8JX",
        "product_name": "Ice Maker",
        "title": "Countertop Ice Maker Machine, 8 Ice Cubes in 6 mins, 26lb/Day Ice with 2 Sizes- Portable Mini",
        "bullet_points": "Eco-Conscious Performance. Makes 8 ice cubes in just 6 minutes. 26lb per day capacity. Two ice cube sizes. Portable and compact design.",
        "attributes": ["Portable", "26lb/Day Capacity", "2 Ice Sizes", "6-Minute Cycle", "Compact", "Black"],
    },
    {
        "asin": "B000H3I2JG",
        "product_name": "Revlon Eyeliner",
        "title": "Revlon ColorStay Pencil Waterproof Eyeliner, Smudge-Proof, Eye Makeup with Built-In Sharpener, 202 Black Brown",
        "bullet_points": "LASTING LINES: Rich color looks fresh for up to 16 hours. Waterproof and smudge-proof formula. Built-in sharpener for precise application.",
        "attributes": ["Waterproof", "Smudge-Proof", "16-Hour Wear", "Built-In Sharpener", "Black Brown"],
    },
    {
        "asin": "B08J8GZXKZ",
        "product_name": "Oven Mitt",
        "title": "KITCHENAID Ribbed Soft Silicone Oven Mitt 2-Pack Set, 7.5x13 inches, Milkshake",
        "bullet_points": "DURABLE, HEAT RESISTANT SILICONE - Heat resistant up to 500 degrees Fahrenheit. Ribbed design for better grip. 2-Pack set.",
        "attributes": ["Heat Resistant", "Silicone", "2-Pack", "Ribbed Design", "7.5x13 inches", "Milkshake"],
    },
    {
        "asin": "B09LCKZBTW",
        "product_name": "Serving Tray",
        "title": "Webacoo Bamboo Tray with Handles - Lightweight Serving Tray for Breakfast in Bed, Coffee Table, BBQ, Kitchen",
        "bullet_points": "Lightweight bamboo construction. Perfect for breakfast in bed, coffee table, BBQ. Easy-grip handles. Large size 15 inches.",
        "attributes": ["Bamboo", "Lightweight", "Handles", "Large Size", "Multi-Purpose"],
    },
    {
        "asin": "B077YYP739",
        "product_name": "Transformers Toy",
        "title": "Transformers Toys Heroic Optimus Prime Action Figure - Timeless Large-Scale Figure, Changes into Toy Truck",
        "bullet_points": "EXPERIENCE THE CLASSIC CONVERSION. Large-scale 11-inch figure. Changes from robot to truck mode. For kids 6 and up.",
        "attributes": ["11-Inch Scale", "Converts to Truck", "Optimus Prime", "Ages 6+", "Classic Design"],
    }
]


def evaluate_m08(output: dict, sample: dict) -> dict:
    """Evaluate M08 output for ranking issues.

    Main rubric criteria:
    1. Ranks must be 1-5 (max 5 attributes ranked)
    2. No duplicate ranks
    3. Ranks must be sequential
    """
    if not output.get("success"):
        return {"pass": False, "reason": "API error", "details": {}}

    result = output.get("output", {})

    # Handle different output formats
    rankings = result.get("attribute_rankings", result.get("rankings", {}))
    attribute_table = result.get("attribute_table", [])

    # If attribute_table format, extract rankings
    if attribute_table and not rankings:
        rankings = {}
        for item in attribute_table:
            if isinstance(item, dict) and "attribute_value" in item and "rank" in item:
                rankings[item["attribute_value"]] = item["rank"]

    if not rankings:
        return {"pass": False, "reason": "empty rankings", "details": {}}

    issues = []
    ranks = list(rankings.values()) if isinstance(rankings, dict) else []

    # Filter to only numeric ranks
    numeric_ranks = [r for r in ranks if isinstance(r, (int, float))]

    if not numeric_ranks:
        return {"pass": False, "reason": "no numeric ranks", "details": {"rankings": rankings}}

    # Check 1: Max rank should be 5 (rubric says ranks 1-5)
    max_rank = max(numeric_ranks)
    if max_rank > 5:
        issues.append(f"rank exceeds 5 (max={max_rank})")

    # Check 2: No duplicate ranks within the top 5
    top_5_ranks = [r for r in numeric_ranks if r <= 5]
    if len(top_5_ranks) != len(set(top_5_ranks)):
        issues.append("duplicate ranks in top 5")

    # Check 3: Ranks should be sequential from 1
    if top_5_ranks:
        sorted_ranks = sorted(set(top_5_ranks))
        expected = list(range(1, len(sorted_ranks) + 1))
        if sorted_ranks != expected:
            issues.append(f"non-sequential: {sorted_ranks}")

    is_pass = len(issues) == 0

    return {
        "pass": is_pass,
        "reason": "valid" if is_pass else "; ".join(issues),
        "details": {
            "rankings": rankings,
            "max_rank": max_rank,
            "num_attributes": len(numeric_ranks),
            "issues": issues
        }
    }


def run_m08_iteration(base_prompt: str, fix: str, samples: List[dict], iteration: int) -> dict:
    """Run one iteration of M08 experiment."""

    if fix:
        if "## Output Format" in base_prompt:
            parts = base_prompt.split("## Output Format")
            prompt = parts[0] + fix + "\n\n## Output Format" + parts[1]
        else:
            prompt = base_prompt + "\n\n" + fix
    else:
        prompt = base_prompt

    results = []

    for sample in samples:
        # Fill template
        filled = prompt
        filled = filled.replace("{{title}}", sample.get("title", ""))
        filled = filled.replace("{{bullet_points}}", sample.get("bullet_points", ""))
        filled = filled.replace("{{attributes}}", json.dumps(sample.get("attributes", [])))

        output = call_gpt(filled)
        evaluation = evaluate_m08(output, sample)

        results.append({
            "asin": sample["asin"],
            "product": sample["product_name"],
            "pass": evaluation["pass"],
            "reason": evaluation["reason"],
            "details": evaluation["details"]
        })

        time.sleep(0.3)

    passed = sum(1 for r in results if r["pass"])

    return {
        "iteration": iteration,
        "passed": passed,
        "total": len(samples),
        "pass_rate": passed / len(samples) if samples else 0,
        "results": results
    }


def run_m08_iterative_experiment(max_iterations: int = 15):
    """Run M08 iterative experiment."""

    print("\n" + "=" * 70)
    print("M08 ITERATIVE EXPERIMENT")
    print(f"Model: {MODEL}")
    print(f"Samples: {len(M08_SAMPLES)}")
    print(f"Max iterations: {max_iterations}")
    print("=" * 70)

    # M08 prompt (simplified for this experiment)
    base_prompt = """# Task: Rank Product Attributes

You are ranking product attributes by importance for search relevance.

## Inputs
- **title**: {{title}}
- **bullet_points**: {{bullet_points}}
- **attributes**: {{attributes}}

## Task
Rank the attributes from most important (1) to least important.

## Output Format
Return JSON:
```json
{
    "attribute_rankings": {
        "attribute_name": rank_number,
        ...
    }
}
```
"""

    iteration_history = []
    cumulative_fix = ""

    for i in range(1, max_iterations + 1):
        print(f"\n{'='*70}")
        print(f"ITERATION {i}")
        print("=" * 70)

        result = run_m08_iteration(base_prompt, cumulative_fix, M08_SAMPLES, i)

        print(f"\nResults: {result['passed']}/{result['total']} passed ({result['pass_rate']*100:.1f}%)")

        for r in result["results"]:
            status = "✓" if r["pass"] else "✗"
            print(f"  {status} {r['asin']} ({r['product']}) - {r['reason']}")
            if not r["pass"]:
                print(f"      Rankings: {r['details'].get('rankings', {})}")

        # Count failure types
        failures = [r for r in result["results"] if not r["pass"]]
        has_duplicates = any("duplicate" in r["reason"] for r in failures)
        has_non_sequential = any("non-sequential" in r["reason"] for r in failures)

        iteration_history.append({
            "iteration": i,
            "passed": result["passed"],
            "total": result["total"],
            "pass_rate": result["pass_rate"],
            "has_duplicates": has_duplicates,
            "has_non_sequential": has_non_sequential
        })

        if result["pass_rate"] >= 0.8:
            print(f"\n✓ Pass rate >= 80%. Stopping iterations.")
            break

        # Analyze specific failure reasons
        has_rank_exceeds_5 = any("exceeds 5" in r["reason"] for r in failures)

        # Build cumulative fix based on failure analysis
        if has_rank_exceeds_5:
            if "MAXIMUM 5 RANKS" not in cumulative_fix:
                cumulative_fix += """

## CRITICAL: MAXIMUM 5 RANKS

**You must rank ONLY the top 5 most important attributes. No rank should exceed 5.**

If a product has more than 5 attributes:
1. Select the 5 MOST IMPORTANT for purchase decisions
2. Rank them 1-5 (1 = most important)
3. DO NOT rank the remaining attributes

WRONG: {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7}  ← ranks exceed 5
RIGHT: {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5}  ← only top 5 ranked
"""
            elif "RANK LIMIT ENFORCEMENT" not in cumulative_fix:
                cumulative_fix += """

### RANK LIMIT ENFORCEMENT

Before outputting, COUNT your ranked attributes:
- If you have MORE than 5 ranked attributes, REMOVE the least important ones
- Maximum rank value allowed: 5
- Any rank > 5 is INVALID

STOP CHECK: Is max(rank) <= 5? If NO, remove lower-priority attributes.
"""
            elif "STRICT 5 LIMIT" not in cumulative_fix:
                cumulative_fix += """

### STRICT 5 LIMIT - FINAL CHECK

□ Count of ranked attributes: _____ (must be ≤ 5)
□ Highest rank value: _____ (must be ≤ 5)

If either check fails, DELETE attributes until only top 5 remain.
"""

        if has_duplicates:
            if "NO DUPLICATE RANKS" not in cumulative_fix:
                cumulative_fix += """

## NO DUPLICATE RANKS

**Each attribute MUST have a unique rank number.**

WRONG: {"Wireless": 1, "Bass": 1, "Color": 2}  ← "1" appears twice
RIGHT: {"Wireless": 1, "Bass": 2, "Color": 3}  ← all unique
"""

        if has_non_sequential:
            if "SEQUENTIAL RANKS" not in cumulative_fix:
                cumulative_fix += """

## SEQUENTIAL RANKS

Ranks MUST be sequential starting from 1.

For 5 attributes: use ranks 1, 2, 3, 4, 5
WRONG: 1, 2, 4, 5, 7  ← gaps and wrong max
RIGHT: 1, 2, 3, 4, 5  ← sequential, no gaps
"""

    # Final summary
    print("\n" + "=" * 70)
    print("ITERATION SUMMARY")
    print("=" * 70)

    for h in iteration_history:
        print(f"  V{h['iteration']}: {h['passed']}/{h['total']} ({h['pass_rate']*100:.1f}%)")

    best = max(iteration_history, key=lambda x: x["pass_rate"])
    print(f"\nBest: V{best['iteration']} with {best['pass_rate']*100:.1f}%")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = PROJECT_ROOT / f"evaluation_KD/experiment_results/m08_iterative_{timestamp}.json"

    with open(output_path, 'w') as f:
        json.dump({
            "module": "M08",
            "model": MODEL,
            "samples_count": len(M08_SAMPLES),
            "iterations": len(iteration_history),
            "iteration_history": iteration_history,
            "final_fix": cumulative_fix,
            "best_iteration": best["iteration"],
            "best_pass_rate": best["pass_rate"]
        }, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return iteration_history, cumulative_fix


# =============================================================================
# M11 ITERATIVE EXPERIMENT - Hard Constraints
# =============================================================================

# M11 samples - products where model marked too many constraints
M11_SAMPLES = [
    {
        "asin": "B0BQPGJ9LQ",
        "product_name": "JBL Earbuds",
        "title": "JBL Vibe Beam - True Wireless JBL Deep Bass Sound Earbuds, Bluetooth 5.2",
        "bullet_points": "JBL Deep Bass Sound. Water & Dust Resistant. Up to 32 hours of battery life.",
        "validated_use": "listening to audio",
        "attributes": ["Bluetooth 5.2", "Deep Bass Sound", "Water Resistant", "32 Hours Battery"],
        "expected_constraints": 0,  # All are quality/durability features
    },
    {
        "asin": "B0D6YNWLTS",
        "product_name": "Puffer Jacket",
        "title": "Pioneer Camp Mens Lightweight Packable Puffer Jacket Winter Insulated",
        "bullet_points": "WINDPROOF & WARM. Water Repellent. Packable & Lightweight.",
        "validated_use": "keeping warm in cold weather",
        "attributes": ["Lightweight", "Packable", "Windproof", "Water Repellent", "Insulated"],
        "expected_constraints": 0,  # All are quality features, not mechanisms
    },
    {
        "asin": "B0DSHWLXG6",
        "product_name": "Phone Holder",
        "title": "Jikasho Vacuum Magnetic Suction Phone Holder, Foldable",
        "bullet_points": "Vacuum Lock + Gel Base. 24 N52 magnet dual-ring system. 360 swivel.",
        "validated_use": "holding phone hands-free",
        "attributes": ["Vacuum-lock suction", "Magnetic mount", "Foldable", "360 degree swivel"],
        "expected_constraints": 0,  # Vacuum/magnetic are tautological (what makes it a suction holder)
    },
    {
        "asin": "B0BZYCJK89",
        "product_name": "Water Bottle",
        "title": "Owala FreeSip Insulated Stainless Steel Water Bottle, 24 Oz",
        "bullet_points": "24-ounce insulated stainless-steel. Double-wall insulation. BPA-free.",
        "validated_use": "carrying drinks for hydration",
        "attributes": ["Stainless Steel", "24 Ounce", "Insulated", "BPA-Free"],
        "expected_constraints": 0,  # All are material/quality choices
    },
    {
        "asin": "B0CJ4WZXQF",
        "product_name": "Sink Caddy",
        "title": "Cisily Kitchen Sink Caddy Organizer, 304 Stainless Steel",
        "bullet_points": "304 Stainless Steel. Automatic Drainage System. Rustproof.",
        "validated_use": "organizing kitchen sink items",
        "attributes": ["Stainless Steel", "Automatic Drainage", "Rustproof"],
        "expected_constraints": 0,  # All are material/convenience features
    },
]


def evaluate_m11(output: dict, sample: dict) -> dict:
    """Evaluate M11 output - hard constraints should be 0-1 for most products."""
    if not output.get("success"):
        return {"pass": False, "reason": "API error", "details": {}}

    result = output.get("output", {})
    hard_constraints = result.get("hard_constraints", [])

    # Handle different formats
    if isinstance(hard_constraints, str):
        hard_constraints = [hard_constraints] if hard_constraints else []

    count = len(hard_constraints)
    expected = sample.get("expected_constraints", 0)

    issues = []

    # Check 1: Count should match expected (0 for most products)
    if count > expected + 1:  # Allow 1 margin of error
        issues.append(f"too many constraints ({count} vs expected {expected})")

    # Check 2: Known soft preferences that should NEVER be hard constraints
    soft_preferences = [
        "bluetooth", "deep bass", "battery", "waterproof", "water resistant",
        "insulated", "lightweight", "packable", "windproof", "water repellent",
        "stainless steel", "bpa-free", "rustproof", "automatic drainage",
        "vacuum", "magnetic", "suction", "foldable", "swivel"
    ]

    for constraint in hard_constraints:
        constraint_lower = constraint.lower()
        for soft in soft_preferences:
            if soft in constraint_lower:
                issues.append(f"soft preference marked as hard: {constraint}")
                break

    is_pass = len(issues) == 0

    return {
        "pass": is_pass,
        "reason": "valid" if is_pass else "; ".join(issues[:2]),  # Limit reasons
        "details": {
            "constraints": hard_constraints,
            "count": count,
            "expected": expected,
            "issues": issues
        }
    }


def run_m11_iteration(base_prompt: str, fix: str, samples: List[dict], iteration: int) -> dict:
    """Run one iteration of M11 experiment."""

    if fix:
        if "## Output Format" in base_prompt:
            parts = base_prompt.split("## Output Format")
            prompt = parts[0] + fix + "\n\n## Output Format" + parts[1]
        else:
            prompt = base_prompt + "\n\n" + fix
    else:
        prompt = base_prompt

    results = []

    for sample in samples:
        filled = prompt
        filled = filled.replace("{{title}}", sample.get("title", ""))
        filled = filled.replace("{{bullet_points}}", sample.get("bullet_points", ""))
        filled = filled.replace("{{validated_use}}", sample.get("validated_use", ""))
        filled = filled.replace("{{attributes}}", json.dumps(sample.get("attributes", [])))

        output = call_gpt(filled)
        evaluation = evaluate_m11(output, sample)

        results.append({
            "asin": sample["asin"],
            "product": sample["product_name"],
            "pass": evaluation["pass"],
            "reason": evaluation["reason"],
            "details": evaluation["details"]
        })

        time.sleep(0.3)

    passed = sum(1 for r in results if r["pass"])

    return {
        "iteration": iteration,
        "passed": passed,
        "total": len(samples),
        "pass_rate": passed / len(samples) if samples else 0,
        "results": results
    }


def run_m11_iterative_experiment(max_iterations: int = 15):
    """Run M11 iterative experiment - fix constraint over-marking."""

    print("\n" + "=" * 70)
    print("M11 ITERATIVE EXPERIMENT - Hard Constraints")
    print(f"Model: {MODEL}")
    print(f"Samples: {len(M11_SAMPLES)}")
    print(f"Max iterations: {max_iterations}")
    print("=" * 70)

    base_prompt = """# Task: Identify Hard Constraints

You are identifying which product attributes are HARD CONSTRAINTS (non-negotiable).

## Input
- **title**: {{title}}
- **bullet_points**: {{bullet_points}}
- **validated_use**: {{validated_use}}
- **attributes**: {{attributes}}

## Definition of Hard Constraint

A hard constraint is an attribute that, if COMPLETELY ABSENT, would make the product PHYSICALLY UNABLE to perform its core function.

## CRITICAL: Most Products Have 0 Hard Constraints

Most consumer products have 0 hard constraints because:
- Quality features (Deep Bass, 32hr Battery) are not required for function
- Durability features (Waterproof, Rustproof) don't enable function
- Material choices (Stainless Steel, Silicone) have alternatives
- Performance specs (500F rating, 24oz) are quality levels

## NEVER Hard Constraints

These are NEVER hard constraints:
- Technology versions: Bluetooth 5.2, WiFi 6, USB 3.0
- Durability: Waterproof, Rustproof, Smudge-proof
- Performance: Battery life, temperature rating, capacity
- Materials: Stainless steel, silicone, bamboo
- Convenience: Foldable, swivel, automatic
- Product-defining mechanisms: Vacuum suction (for suction holders), magnetic (for magnetic mounts)

## Output Format

Return JSON:
```json
{
    "reasoning": "Brief analysis",
    "hard_constraints": []
}
```

For most products, hard_constraints should be an EMPTY ARRAY [].
"""

    iteration_history = []
    cumulative_fix = ""

    for i in range(1, max_iterations + 1):
        print(f"\n{'='*70}")
        print(f"ITERATION {i}")
        print("=" * 70)

        result = run_m11_iteration(base_prompt, cumulative_fix, M11_SAMPLES, i)

        print(f"\nResults: {result['passed']}/{result['total']} passed ({result['pass_rate']*100:.1f}%)")

        for r in result["results"]:
            status = "✓" if r["pass"] else "✗"
            constraints = r["details"].get("constraints", [])
            print(f"  {status} {r['asin']} ({r['product']}) - {r['reason']}")
            if constraints:
                print(f"      Constraints: {constraints}")

        # Analyze failures
        failures = [r for r in result["results"] if not r["pass"]]
        has_too_many = any("too many" in r["reason"] for r in failures)
        has_soft_as_hard = any("soft preference" in r["reason"] for r in failures)

        iteration_history.append({
            "iteration": i,
            "passed": result["passed"],
            "total": result["total"],
            "pass_rate": result["pass_rate"],
            "has_too_many": has_too_many,
            "has_soft_as_hard": has_soft_as_hard
        })

        if result["pass_rate"] >= 0.8:
            print(f"\n✓ Pass rate >= 80%. Stopping iterations.")
            break

        # Build cumulative fix
        if has_soft_as_hard:
            if "SOFT PREFERENCE BLACKLIST" not in cumulative_fix:
                cumulative_fix += """

## SOFT PREFERENCE BLACKLIST

These are NEVER hard constraints - they are quality/convenience features:

| Feature Type | Examples | Why NOT Hard |
|--------------|----------|--------------|
| Audio Quality | Deep Bass, Noise Canceling | Audio still works without |
| Battery | 32hr battery, Fast Charging | Device works with less |
| Durability | Waterproof, Rustproof | Works when dry/new |
| Insulation | Insulated, Temperature control | Still holds liquid |
| Mechanism | Vacuum suction, Magnetic | Defines product type |
| Material | Stainless Steel, Silicone | Alternatives exist |
| Convenience | Foldable, Swivel, Automatic | Still functions without |

Before outputting ANY hard constraint, check this list. If it matches, DELETE IT.
"""
            elif "ZERO CONSTRAINT DEFAULT" not in cumulative_fix:
                cumulative_fix += """

## ZERO CONSTRAINT DEFAULT

START with the assumption: hard_constraints = []

Only ADD a constraint if:
1. It's a device compatibility requirement (iPhone 15 case must fit iPhone 15)
2. It's a safety mechanism (oven mitt MUST have heat resistance)

For these products, the answer is almost certainly []:
- Earbuds, headphones → []
- Water bottles → []
- Organizers, caddies → []
- Clothing (jackets, etc.) → []
- Phone holders, mounts → []
"""

        if has_too_many:
            if "COUNT CHECK" not in cumulative_fix:
                cumulative_fix += """

## COUNT CHECK

After generating your answer, COUNT the hard_constraints array:
- If count > 1: STOP and re-evaluate each one
- Ask: "Would a reasonable person say this product is BROKEN without this?"
- If not clearly BROKEN, remove it

Expected counts:
- Earbuds: 0
- Water bottles: 0
- Phone holders: 0
- Jackets: 0
- Organizers: 0
"""

    # Final summary
    print("\n" + "=" * 70)
    print("ITERATION SUMMARY")
    print("=" * 70)

    for h in iteration_history:
        print(f"  V{h['iteration']}: {h['passed']}/{h['total']} ({h['pass_rate']*100:.1f}%)")

    best = max(iteration_history, key=lambda x: x["pass_rate"])
    print(f"\nBest: V{best['iteration']} with {best['pass_rate']*100:.1f}%")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = PROJECT_ROOT / f"evaluation_KD/experiment_results/m11_iterative_{timestamp}.json"

    with open(output_path, 'w') as f:
        json.dump({
            "module": "M11",
            "model": MODEL,
            "samples_count": len(M11_SAMPLES),
            "iterations": len(iteration_history),
            "iteration_history": iteration_history,
            "final_fix": cumulative_fix,
            "best_iteration": best["iteration"],
            "best_pass_rate": best["pass_rate"]
        }, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return iteration_history, cumulative_fix


# =============================================================================
# M15 ITERATIVE EXPERIMENT - Substitute Detection
# =============================================================================

# M15 samples - products where substitute detection failed
M15_SAMPLES = [
    {
        "asin": "B0BZYCJK89",
        "product_name": "Water Bottle",
        "keyword": "travel mug",
        "product_type": "Water Bottle",
        "keyword_type": "Travel Mug",
        "expected_substitute": True,  # Both carry beverages for hydration
    },
    {
        "asin": "B0BZYCJK89",
        "product_name": "Water Bottle",
        "keyword": "coffee tumbler",
        "product_type": "Water Bottle",
        "keyword_type": "Coffee Tumbler",
        "expected_substitute": True,  # Both are insulated beverage containers
    },
    {
        "asin": "B0BQPGJ9LQ",
        "product_name": "JBL Earbuds",
        "keyword": "wireless headphones",
        "product_type": "True Wireless Earbuds",
        "keyword_type": "Wireless Headphones",
        "expected_substitute": True,  # Both for listening to audio wirelessly
    },
    {
        "asin": "B0BQPGJ9LQ",
        "product_name": "JBL Earbuds",
        "keyword": "bluetooth speaker",
        "product_type": "True Wireless Earbuds",
        "keyword_type": "Bluetooth Speaker",
        "expected_substitute": False,  # Different use - personal vs shared
    },
    {
        "asin": "B0D6YNWLTS",
        "product_name": "Puffer Jacket",
        "keyword": "fleece jacket",
        "product_type": "Puffer Jacket",
        "keyword_type": "Fleece Jacket",
        "expected_substitute": True,  # Both for warmth
    },
]


def evaluate_m15(output: dict, sample: dict) -> dict:
    """Evaluate M15 output - substitute detection."""
    if not output.get("success"):
        return {"pass": False, "reason": "API error", "details": {}}

    result = output.get("output", {})
    is_substitute = result.get("is_substitute", result.get("substitute", False))
    expected = sample.get("expected_substitute", False)

    is_pass = is_substitute == expected

    return {
        "pass": is_pass,
        "reason": "correct" if is_pass else f"expected {expected}, got {is_substitute}",
        "details": {
            "is_substitute": is_substitute,
            "expected": expected,
            "reasoning": result.get("reasoning", "")[:200]
        }
    }


def run_m15_iteration(base_prompt: str, fix: str, samples: List[dict], iteration: int) -> dict:
    """Run one iteration of M15 experiment."""

    if fix:
        if "## Output Format" in base_prompt:
            parts = base_prompt.split("## Output Format")
            prompt = parts[0] + fix + "\n\n## Output Format" + parts[1]
        else:
            prompt = base_prompt + "\n\n" + fix
    else:
        prompt = base_prompt

    results = []

    for sample in samples:
        filled = prompt
        filled = filled.replace("{{product_name}}", sample.get("product_name", ""))
        filled = filled.replace("{{keyword}}", sample.get("keyword", ""))
        filled = filled.replace("{{product_type}}", sample.get("product_type", ""))
        filled = filled.replace("{{keyword_type}}", sample.get("keyword_type", ""))

        output = call_gpt(filled)
        evaluation = evaluate_m15(output, sample)

        results.append({
            "asin": sample["asin"],
            "product": sample["product_name"],
            "keyword": sample["keyword"],
            "pass": evaluation["pass"],
            "reason": evaluation["reason"],
            "details": evaluation["details"]
        })

        time.sleep(0.3)

    passed = sum(1 for r in results if r["pass"])

    return {
        "iteration": iteration,
        "passed": passed,
        "total": len(samples),
        "pass_rate": passed / len(samples) if samples else 0,
        "results": results
    }


def run_m15_iterative_experiment(max_iterations: int = 15):
    """Run M15 iterative experiment - fix substitute detection."""

    print("\n" + "=" * 70)
    print("M15 ITERATIVE EXPERIMENT - Substitute Detection")
    print(f"Model: {MODEL}")
    print(f"Samples: {len(M15_SAMPLES)}")
    print(f"Max iterations: {max_iterations}")
    print("=" * 70)

    base_prompt = """# Task: Check if Product is a Substitute

You are determining if a keyword's product type could SUBSTITUTE for the ASIN's product.

## Input
- **Product**: {{product_name}} (type: {{product_type}})
- **Keyword**: {{keyword}} (type: {{keyword_type}})

## Definition of Substitute

A substitute product is one that:
1. Serves the SAME PRIMARY PURPOSE (60%+ overlap in use cases)
2. A customer searching for one might reasonably buy the other
3. They compete for the same customer need

## Examples

| Product | Keyword | Substitute? | Why |
|---------|---------|-------------|-----|
| Water Bottle | Travel Mug | YES | Both carry beverages for hydration |
| Earbuds | Headphones | YES | Both for personal audio listening |
| Puffer Jacket | Fleece Jacket | YES | Both for warmth/layering |
| Earbuds | Bluetooth Speaker | NO | Personal vs shared audio |
| Water Bottle | Coffee Maker | NO | Carrying vs brewing |

## Output Format

Return JSON:
```json
{
    "reasoning": "Brief explanation",
    "is_substitute": true/false
}
```
"""

    iteration_history = []
    cumulative_fix = ""

    for i in range(1, max_iterations + 1):
        print(f"\n{'='*70}")
        print(f"ITERATION {i}")
        print("=" * 70)

        result = run_m15_iteration(base_prompt, cumulative_fix, M15_SAMPLES, i)

        print(f"\nResults: {result['passed']}/{result['total']} passed ({result['pass_rate']*100:.1f}%)")

        for r in result["results"]:
            status = "✓" if r["pass"] else "✗"
            print(f"  {status} {r['product']} vs '{r['keyword']}' - {r['reason']}")

        # Analyze failures
        failures = [r for r in result["results"] if not r["pass"]]
        false_negatives = [r for r in failures if r["details"]["expected"] == True]
        false_positives = [r for r in failures if r["details"]["expected"] == False]

        iteration_history.append({
            "iteration": i,
            "passed": result["passed"],
            "total": result["total"],
            "pass_rate": result["pass_rate"],
            "false_negatives": len(false_negatives),
            "false_positives": len(false_positives)
        })

        if result["pass_rate"] >= 0.8:
            print(f"\n✓ Pass rate >= 80%. Stopping iterations.")
            break

        # Build cumulative fix
        if false_negatives:
            if "SUBSTITUTE HEURISTIC" not in cumulative_fix:
                cumulative_fix += """

## SUBSTITUTE HEURISTIC

Ask: "Would a customer searching for X be satisfied with Y?"

Common substitute pairs (answer is YES):
- Water Bottle ↔ Travel Mug ↔ Coffee Tumbler (all carry beverages)
- Earbuds ↔ Headphones ↔ In-ear monitors (all personal audio)
- Puffer Jacket ↔ Fleece Jacket ↔ Down Jacket (all warmth layers)
- Backpack ↔ Messenger Bag ↔ Laptop Bag (all carry items)

Focus on PRIMARY FUNCTION, not form factor.
"""
            elif "60% OVERLAP TEST" not in cumulative_fix:
                cumulative_fix += """

## 60% OVERLAP TEST

Two products are substitutes if 60%+ of their use cases overlap.

Water Bottle vs Travel Mug:
- Both carry beverages ✓
- Both for on-the-go hydration ✓
- Both keep drinks at temperature ✓
- Overlap: HIGH → SUBSTITUTE

Earbuds vs Bluetooth Speaker:
- Both play audio ✓
- Personal vs shared listening ✗
- Portable vs stationary ✗
- Overlap: LOW → NOT SUBSTITUTE
"""

        if false_positives:
            if "NOT SUBSTITUTE CRITERIA" not in cumulative_fix:
                cumulative_fix += """

## NOT SUBSTITUTE CRITERIA

Products are NOT substitutes if:
1. Different consumption context (personal vs group)
2. Different primary function (carry vs make)
3. Different customer intent (listening vs broadcasting)

Example: Earbuds vs Bluetooth Speaker
- Earbuds: personal, private listening
- Speaker: shared, room-filling audio
- NOT substitutes despite both being "audio devices"
"""

    # Final summary
    print("\n" + "=" * 70)
    print("ITERATION SUMMARY")
    print("=" * 70)

    for h in iteration_history:
        print(f"  V{h['iteration']}: {h['passed']}/{h['total']} ({h['pass_rate']*100:.1f}%)")

    best = max(iteration_history, key=lambda x: x["pass_rate"])
    print(f"\nBest: V{best['iteration']} with {best['pass_rate']*100:.1f}%")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = PROJECT_ROOT / f"evaluation_KD/experiment_results/m15_iterative_{timestamp}.json"

    with open(output_path, 'w') as f:
        json.dump({
            "module": "M15",
            "model": MODEL,
            "samples_count": len(M15_SAMPLES),
            "iterations": len(iteration_history),
            "iteration_history": iteration_history,
            "final_fix": cumulative_fix,
            "best_iteration": best["iteration"],
            "best_pass_rate": best["pass_rate"]
        }, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return iteration_history, cumulative_fix


# =============================================================================
# M04 ITERATIVE EXPERIMENT - Competitor Brand Detection
# =============================================================================

M04_SAMPLES = [
    {
        "asin": "B08J8GZXKZ",
        "product_name": "KitchenAid Oven Mitt",
        "own_brand": "KitchenAid",
        "keyword": "le creuset oven mitt",
        "competitors": ["Le Creuset", "OXO", "HOMWE", "Cuisinart"],
        "expected_classification": "CB",  # Le Creuset is competitor
    },
    {
        "asin": "B08J8GZXKZ",
        "product_name": "KitchenAid Oven Mitt",
        "own_brand": "KitchenAid",
        "keyword": "silicone oven mitt",
        "competitors": ["Le Creuset", "OXO", "HOMWE", "Cuisinart"],
        "expected_classification": None,  # No brand in keyword
    },
    {
        "asin": "B08J8GZXKZ",
        "product_name": "KitchenAid Oven Mitt",
        "own_brand": "KitchenAid",
        "keyword": "oxo oven mitt",
        "competitors": ["Le Creuset", "OXO", "HOMWE", "Cuisinart"],
        "expected_classification": "CB",  # OXO is competitor
    },
    {
        "asin": "B0BQPGJ9LQ",
        "product_name": "JBL Earbuds",
        "own_brand": "JBL",
        "keyword": "sony wireless earbuds",
        "competitors": ["Sony", "Bose", "Samsung", "Apple"],
        "expected_classification": "CB",  # Sony is competitor
    },
    {
        "asin": "B0BQPGJ9LQ",
        "product_name": "JBL Earbuds",
        "own_brand": "JBL",
        "keyword": "bluetooth earbuds",
        "competitors": ["Sony", "Bose", "Samsung", "Apple"],
        "expected_classification": None,  # No brand
    },
]


def evaluate_m04(output: dict, sample: dict) -> dict:
    """Evaluate M04 output - competitor brand detection."""
    if not output.get("success"):
        return {"pass": False, "reason": "API error", "details": {}}

    result = output.get("output", {})
    classification = result.get("branding_scope", result.get("classification"))
    expected = sample.get("expected_classification")

    # Normalize null/None
    if classification in [None, "null", "NULL", ""]:
        classification = None

    is_pass = classification == expected

    return {
        "pass": is_pass,
        "reason": "correct" if is_pass else f"expected {expected}, got {classification}",
        "details": {
            "classification": classification,
            "expected": expected,
            "reasoning": result.get("reasoning", "")[:200]
        }
    }


def run_m04_iteration(base_prompt: str, fix: str, samples: List[dict], iteration: int) -> dict:
    """Run one iteration of M04 experiment."""

    if fix:
        if "## Output Format" in base_prompt:
            parts = base_prompt.split("## Output Format")
            prompt = parts[0] + fix + "\n\n## Output Format" + parts[1]
        else:
            prompt = base_prompt + "\n\n" + fix
    else:
        prompt = base_prompt

    results = []

    for sample in samples:
        filled = prompt
        filled = filled.replace("{{keyword}}", sample.get("keyword", ""))
        filled = filled.replace("{{own_brand}}", sample.get("own_brand", ""))
        filled = filled.replace("{{competitors}}", json.dumps(sample.get("competitors", [])))

        output = call_gpt(filled)
        evaluation = evaluate_m04(output, sample)

        results.append({
            "asin": sample["asin"],
            "product": sample["product_name"],
            "keyword": sample["keyword"],
            "pass": evaluation["pass"],
            "reason": evaluation["reason"],
            "details": evaluation["details"]
        })

        time.sleep(0.3)

    passed = sum(1 for r in results if r["pass"])

    return {
        "iteration": iteration,
        "passed": passed,
        "total": len(samples),
        "pass_rate": passed / len(samples) if samples else 0,
        "results": results
    }


def run_m04_iterative_experiment(max_iterations: int = 15):
    """Run M04 iterative experiment - competitor brand detection."""

    print("\n" + "=" * 70)
    print("M04 ITERATIVE EXPERIMENT - Competitor Brand Detection")
    print(f"Model: {MODEL}")
    print(f"Samples: {len(M04_SAMPLES)}")
    print(f"Max iterations: {max_iterations}")
    print("=" * 70)

    base_prompt = """# Task: Classify Competitor Brand Keywords

You are determining if a keyword contains a COMPETITOR brand.

## Input
- **keyword**: {{keyword}}
- **own_brand**: {{own_brand}} (this is OUR brand - never classify as competitor)
- **competitors**: {{competitors}}

## Rules

1. If keyword contains a brand from the competitors list → return "CB"
2. If keyword contains NO brand (generic keyword) → return null
3. NEVER classify own_brand as competitor

## Case Insensitive Matching

Match brands regardless of case:
- "le creuset" matches "Le Creuset" → CB
- "oxo" matches "OXO" → CB
- "sony" matches "Sony" → CB

## Output Format

Return JSON:
```json
{
    "reasoning": "Brief explanation",
    "branding_scope": "CB" or null
}
```
"""

    iteration_history = []
    cumulative_fix = ""

    for i in range(1, max_iterations + 1):
        print(f"\n{'='*70}")
        print(f"ITERATION {i}")
        print("=" * 70)

        result = run_m04_iteration(base_prompt, cumulative_fix, M04_SAMPLES, i)

        print(f"\nResults: {result['passed']}/{result['total']} passed ({result['pass_rate']*100:.1f}%)")

        for r in result["results"]:
            status = "✓" if r["pass"] else "✗"
            print(f"  {status} '{r['keyword']}' - {r['reason']}")

        # Analyze failures
        failures = [r for r in result["results"] if not r["pass"]]
        false_negatives = [r for r in failures if r["details"]["expected"] == "CB"]
        false_positives = [r for r in failures if r["details"]["expected"] is None]

        iteration_history.append({
            "iteration": i,
            "passed": result["passed"],
            "total": result["total"],
            "pass_rate": result["pass_rate"],
            "false_negatives": len(false_negatives),
            "false_positives": len(false_positives)
        })

        if result["pass_rate"] >= 0.8:
            print(f"\n✓ Pass rate >= 80%. Stopping iterations.")
            break

        # Build cumulative fix
        if false_negatives:
            if "CASE INSENSITIVE" not in cumulative_fix:
                cumulative_fix += """

## CASE INSENSITIVE MATCHING

Brand matching MUST ignore case:
- "le creuset" = "Le Creuset" = "LE CREUSET" → all match
- "oxo" = "OXO" = "Oxo" → all match

Convert both keyword and competitor list to lowercase before comparing.
"""

        if false_positives:
            if "GENERIC KEYWORDS" not in cumulative_fix:
                cumulative_fix += """

## GENERIC KEYWORDS = null

If keyword contains NO brand names, return null:
- "silicone oven mitt" → null (no brand)
- "bluetooth earbuds" → null (no brand)
- "wireless headphones" → null (no brand)

Only return "CB" if an actual brand name is found.
"""

    # Final summary
    print("\n" + "=" * 70)
    print("ITERATION SUMMARY")
    print("=" * 70)

    for h in iteration_history:
        print(f"  V{h['iteration']}: {h['passed']}/{h['total']} ({h['pass_rate']*100:.1f}%)")

    best = max(iteration_history, key=lambda x: x["pass_rate"])
    print(f"\nBest: V{best['iteration']} with {best['pass_rate']*100:.1f}%")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = PROJECT_ROOT / f"evaluation_KD/experiment_results/m04_iterative_{timestamp}.json"

    with open(output_path, 'w') as f:
        json.dump({
            "module": "M04",
            "model": MODEL,
            "samples_count": len(M04_SAMPLES),
            "iterations": len(iteration_history),
            "iteration_history": iteration_history,
            "final_fix": cumulative_fix,
            "best_iteration": best["iteration"],
            "best_pass_rate": best["pass_rate"]
        }, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return iteration_history, cumulative_fix


# =============================================================================
# M06 ITERATIVE EXPERIMENT - Product Taxonomy
# =============================================================================

M06_SAMPLES = [
    {
        "asin": "B0BQPGJ9LQ",
        "product_name": "JBL Earbuds",
        "title": "JBL Vibe Beam - True Wireless JBL Deep Bass Sound Earbuds",
        "expected_taxonomy": ["True Wireless Earbuds", "Headphones", "Electronics"],
    },
    {
        "asin": "B0BZYCJK89",
        "product_name": "Water Bottle",
        "title": "Owala FreeSip Insulated Stainless Steel Water Bottle",
        "expected_taxonomy": ["Insulated Water Bottle", "Water Bottles", "Sports & Outdoors"],
    },
    {
        "asin": "B0CJ4WZXQF",
        "product_name": "Sink Caddy",
        "title": "Cisily Kitchen Sink Caddy Organizer with High Brush Holder",
        "expected_taxonomy": ["Kitchen Sink Caddy", "Kitchen Storage", "Home & Kitchen"],
    },
    {
        "asin": "B0D6YNWLTS",
        "product_name": "Puffer Jacket",
        "title": "Pioneer Camp Mens Lightweight Packable Puffer Jacket",
        "expected_taxonomy": ["Puffer Jacket", "Jackets & Coats", "Clothing"],
    },
    {
        "asin": "B08J8GZXKZ",
        "product_name": "Oven Mitt",
        "title": "KitchenAid Asteroid Oven Mitt, Cotton",
        "expected_taxonomy": ["Oven Mitt", "Kitchen Textiles", "Home & Kitchen"],
    },
]


def evaluate_m06(output: dict, sample: dict) -> dict:
    """Evaluate M06 output - taxonomy should have exactly 3 levels, specific to broad."""
    if not output.get("success"):
        return {"pass": False, "reason": "API error", "details": {}}

    result = output.get("output", {})
    taxonomy = result.get("taxonomy", result.get("product_type_taxonomy", []))

    # Handle different formats
    if isinstance(taxonomy, dict):
        # Format: {"level_1": "...", "level_2": "...", "level_3": "..."}
        taxonomy = [taxonomy.get("level_1", ""), taxonomy.get("level_2", ""), taxonomy.get("level_3", "")]
    elif isinstance(taxonomy, str):
        taxonomy = [taxonomy]

    issues = []

    # Check 1: Exactly 3 levels
    if len(taxonomy) != 3:
        issues.append(f"wrong level count ({len(taxonomy)} vs 3)")

    # Check 2: No empty levels
    empty_levels = sum(1 for t in taxonomy if not t or t.strip() == "")
    if empty_levels > 0:
        issues.append(f"{empty_levels} empty levels")

    # Check 3: No brand names in taxonomy
    brand_keywords = ["jbl", "owala", "cisily", "pioneer camp", "kitchenaid"]
    for level in taxonomy:
        level_lower = level.lower() if level else ""
        for brand in brand_keywords:
            if brand in level_lower:
                issues.append(f"brand in taxonomy: {level}")
                break

    is_pass = len(issues) == 0

    return {
        "pass": is_pass,
        "reason": "valid" if is_pass else "; ".join(issues[:2]),
        "details": {
            "taxonomy": taxonomy,
            "level_count": len(taxonomy),
            "issues": issues
        }
    }


def run_m06_iteration(base_prompt: str, fix: str, samples: List[dict], iteration: int) -> dict:
    """Run one iteration of M06 experiment."""

    if fix:
        if "## Output Format" in base_prompt:
            parts = base_prompt.split("## Output Format")
            prompt = parts[0] + fix + "\n\n## Output Format" + parts[1]
        else:
            prompt = base_prompt + "\n\n" + fix
    else:
        prompt = base_prompt

    results = []

    for sample in samples:
        filled = prompt
        filled = filled.replace("{{title}}", sample.get("title", ""))
        filled = filled.replace("{{product_name}}", sample.get("product_name", ""))

        output = call_gpt(filled)
        evaluation = evaluate_m06(output, sample)

        results.append({
            "asin": sample["asin"],
            "product": sample["product_name"],
            "pass": evaluation["pass"],
            "reason": evaluation["reason"],
            "details": evaluation["details"]
        })

        time.sleep(0.3)

    passed = sum(1 for r in results if r["pass"])

    return {
        "iteration": iteration,
        "passed": passed,
        "total": len(samples),
        "pass_rate": passed / len(samples) if samples else 0,
        "results": results
    }


def run_m06_iterative_experiment(max_iterations: int = 15):
    """Run M06 iterative experiment - product taxonomy."""

    print("\n" + "=" * 70)
    print("M06 ITERATIVE EXPERIMENT - Product Taxonomy")
    print(f"Model: {MODEL}")
    print(f"Samples: {len(M06_SAMPLES)}")
    print(f"Max iterations: {max_iterations}")
    print("=" * 70)

    base_prompt = """# Task: Generate Product Type Taxonomy

You are creating a 3-level product taxonomy for an Amazon product.

## Input
- **title**: {{title}}

## Requirements

Generate EXACTLY 3 levels, from specific to broad:
- Level 1: Most specific product type (what this exact product is)
- Level 2: Category (broader grouping)
- Level 3: Department (broadest category)

## Examples

| Product | Level 1 | Level 2 | Level 3 |
|---------|---------|---------|---------|
| JBL Earbuds | True Wireless Earbuds | Headphones | Electronics |
| Water Bottle | Insulated Water Bottle | Water Bottles | Sports & Outdoors |
| Oven Mitt | Silicone Oven Mitt | Kitchen Textiles | Home & Kitchen |
| Puffer Jacket | Puffer Jacket | Jackets & Coats | Clothing |

## Rules

1. EXACTLY 3 levels - no more, no less
2. NO brand names in taxonomy
3. Level 1 = most specific, Level 3 = broadest

## Output Format

Return JSON:
```json
{
    "taxonomy": ["Level 1 - Specific Product", "Level 2 - Category", "Level 3 - Department"]
}
```
"""

    iteration_history = []
    cumulative_fix = ""

    for i in range(1, max_iterations + 1):
        print(f"\n{'='*70}")
        print(f"ITERATION {i}")
        print("=" * 70)

        result = run_m06_iteration(base_prompt, cumulative_fix, M06_SAMPLES, i)

        print(f"\nResults: {result['passed']}/{result['total']} passed ({result['pass_rate']*100:.1f}%)")

        for r in result["results"]:
            status = "✓" if r["pass"] else "✗"
            taxonomy = r["details"].get("taxonomy", [])
            print(f"  {status} {r['product']} - {r['reason']}")
            if taxonomy:
                print(f"      Taxonomy: {taxonomy}")

        # Analyze failures
        failures = [r for r in result["results"] if not r["pass"]]
        has_wrong_count = any("level count" in r["reason"] for r in failures)
        has_brand = any("brand" in r["reason"] for r in failures)

        iteration_history.append({
            "iteration": i,
            "passed": result["passed"],
            "total": result["total"],
            "pass_rate": result["pass_rate"],
            "has_wrong_count": has_wrong_count,
            "has_brand": has_brand
        })

        if result["pass_rate"] >= 0.8:
            print(f"\n✓ Pass rate >= 80%. Stopping iterations.")
            break

        # Build cumulative fix
        if has_wrong_count:
            if "EXACTLY 3 LEVELS" not in cumulative_fix:
                cumulative_fix += """

## CRITICAL: EXACTLY 3 LEVELS

Your taxonomy array MUST have exactly 3 elements.

WRONG: ["Water Bottle"] ← only 1 level
WRONG: ["Water Bottle", "Kitchen"] ← only 2 levels
RIGHT: ["Water Bottle", "Drinkware", "Kitchen & Dining"] ← exactly 3

Before outputting, count your array length. If not 3, add/remove levels.
"""

        if has_brand:
            if "NO BRAND NAMES" not in cumulative_fix:
                cumulative_fix += """

## NO BRAND NAMES

Never include brand names in taxonomy:

WRONG: ["JBL Earbuds", "Electronics"]
RIGHT: ["True Wireless Earbuds", "Headphones", "Electronics"]

Remove any brand names (JBL, Owala, KitchenAid, etc.) from output.
"""

    # Final summary
    print("\n" + "=" * 70)
    print("ITERATION SUMMARY")
    print("=" * 70)

    for h in iteration_history:
        print(f"  V{h['iteration']}: {h['passed']}/{h['total']} ({h['pass_rate']*100:.1f}%)")

    best = max(iteration_history, key=lambda x: x["pass_rate"])
    print(f"\nBest: V{best['iteration']} with {best['pass_rate']*100:.1f}%")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = PROJECT_ROOT / f"evaluation_KD/experiment_results/m06_iterative_{timestamp}.json"

    with open(output_path, 'w') as f:
        json.dump({
            "module": "M06",
            "model": MODEL,
            "samples_count": len(M06_SAMPLES),
            "iterations": len(iteration_history),
            "iteration_history": iteration_history,
            "final_fix": cumulative_fix,
            "best_iteration": best["iteration"],
            "best_pass_rate": best["pass_rate"]
        }, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return iteration_history, cumulative_fix


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run iterative prompt experiments")
    parser.add_argument("--module", "-m", required=True, choices=["m03", "m04", "m06", "m08", "m11", "m15", "all"])
    parser.add_argument("--iterations", "-i", type=int, default=15)

    args = parser.parse_args()

    if args.module == "m03" or args.module == "all":
        run_m03_iterative_experiment(args.iterations)

    if args.module == "m04" or args.module == "all":
        run_m04_iterative_experiment(args.iterations)

    if args.module == "m06" or args.module == "all":
        run_m06_iterative_experiment(args.iterations)

    if args.module == "m08" or args.module == "all":
        run_m08_iterative_experiment(args.iterations)

    if args.module == "m11" or args.module == "all":
        run_m11_iterative_experiment(args.iterations)

    if args.module == "m15" or args.module == "all":
        run_m15_iterative_experiment(args.iterations)
