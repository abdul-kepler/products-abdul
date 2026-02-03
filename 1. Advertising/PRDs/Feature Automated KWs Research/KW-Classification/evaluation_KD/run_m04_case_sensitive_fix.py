#!/usr/bin/env python3
"""
M04 Case-Insensitive Matching Fix Experiment

Runs 15 iterations to fix the case-insensitive matching issue for competitor brand detection.
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o-mini"

# Samples that FAILED in evaluation - specifically case-sensitivity issues
M04_FAILING_SAMPLES = [
    {
        "keyword": "aglucky ice makers countertop",
        "own_brand": {"name": "GE Profile", "entities": ["GE Profile", "GE", "ge profile"]},
        "competitors": ["Frigidaire", "Scotsman", "Manitowoc", "Hoshizaki", "Samsung", "NewAir", "VEVOR", "Magic Chef", "Silonn", "Whirlpool", "AGLUCKY", "COWSAR", "COSTWAY", "ecozy"],
        "expected": "CB",  # "aglucky" should match "AGLUCKY"
    },
    {
        "keyword": "sweetcrispy countertop ice maker",
        "own_brand": {"name": "GE Profile", "entities": ["GE Profile", "GE", "ge profile"]},
        "competitors": ["Frigidaire", "Scotsman", "Manitowoc", "Sweetcrispy", "Samsung", "NewAir", "VEVOR", "Magic Chef"],
        "expected": "CB",  # "sweetcrispy" should match "Sweetcrispy"
    },
    {
        "keyword": "homwe silicone oven mitt",
        "own_brand": {"name": "KitchenAid", "entities": ["KitchenAid", "Kitchen Aid", "Kitchenaid"]},
        "competitors": ["Ove Glove", "HOMWE", "GORILLA GRIP", "Le Creuset", "All-Clad", "Homwe"],
        "expected": "CB",  # "homwe" should match "HOMWE" or "Homwe"
    },
    {
        "keyword": "le creuset oven mitt",
        "own_brand": {"name": "KitchenAid", "entities": ["KitchenAid", "Kitchen Aid", "Kitchenaid"]},
        "competitors": ["Ove Glove", "HOMWE", "GORILLA GRIP", "Le Creuset", "All-Clad"],
        "expected": "CB",  # "le creuset" should match "Le Creuset"
    },
    {
        "keyword": "silicone oven mitt",
        "own_brand": {"name": "KitchenAid", "entities": ["KitchenAid", "Kitchen Aid", "Kitchenaid"]},
        "competitors": ["Ove Glove", "HOMWE", "GORILLA GRIP", "Le Creuset", "All-Clad"],
        "expected": None,  # Generic - no brand
    },
    {
        "keyword": "wireless bluetooth speaker",
        "own_brand": {"name": "JBL", "entities": ["JBL", "jbl", "J B L"]},
        "competitors": ["Bose", "Sony", "Apple", "Samsung", "BOSE"],
        "expected": None,  # Generic - no brand
    },
    {
        "keyword": "bose speaker",
        "own_brand": {"name": "JBL", "entities": ["JBL", "jbl", "J B L"]},
        "competitors": ["Bose", "Sony", "Apple", "Samsung", "BOSE"],
        "expected": "CB",  # "bose" should match "Bose" or "BOSE"
    },
    {
        "keyword": "SONY earbuds",
        "own_brand": {"name": "JBL", "entities": ["JBL", "jbl", "J B L"]},
        "competitors": ["Bose", "Sony", "Apple", "Samsung"],
        "expected": "CB",  # "SONY" should match "Sony"
    },
]


def load_prompt() -> str:
    """Load M04 prompt template from file."""
    prompt_path = PROJECT_ROOT / "prompts" / "modules" / "m04_classify_competitor_brand_keywords.md"
    with open(prompt_path, 'r') as f:
        return f.read()


def fill_template(prompt: str, sample: dict) -> str:
    """Fill prompt template with sample data."""
    filled = prompt
    filled = filled.replace("{{keyword}}", sample.get("keyword", ""))
    filled = filled.replace("{{own_brand}}", json.dumps(sample.get("own_brand", {})))
    filled = filled.replace("{{competitor_entities}}", json.dumps(sample.get("competitors", [])))
    return filled


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


def evaluate_output(output: dict, sample: dict) -> dict:
    """Evaluate M04 output."""
    if not output.get("success"):
        return {"pass": False, "reason": "API error", "details": {}}

    result = output.get("output", {})

    # Handle different output field names
    classification = result.get("branding_scope_2", result.get("branding_scope", result.get("classification")))
    expected = sample.get("expected")

    # Normalize null/None
    if classification in [None, "null", "NULL", "", "none", "None"]:
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


def run_iteration(base_prompt: str, fix: str, samples: List[dict], iteration: int) -> dict:
    """Run one iteration of M04 experiment."""

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
        filled = fill_template(prompt, sample)
        output = call_gpt(filled)
        evaluation = evaluate_output(output, sample)

        results.append({
            "keyword": sample["keyword"],
            "expected": sample["expected"],
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


# Prompt modifications to test - using only [brand], [BRAND] placeholders
MODIFICATIONS = [
    # Iteration 1: Explicit lowercase instruction
    """
## CRITICAL: Case-Insensitive Brand Matching

**ALWAYS convert BOTH the keyword AND each competitor entity to lowercase before comparing.**

Step-by-step process:
1. Convert keyword to lowercase: "[brand] ice maker" -> "[brand] ice maker"
2. For EACH competitor in the list, convert to lowercase: "[BRAND]" -> "[brand]"
3. Check if lowercase keyword CONTAINS lowercase competitor

Example:
- Keyword: "[brand] ice maker" (lowercase: "[brand] ice maker")
- Competitor list: ["[BRAND]", "[Competitor]"]
- "[brand]".lower() = "[brand]"
- Check: "[brand] ice maker".contains("[brand]") = TRUE -> CB
""",

    # Iteration 2: Add explicit normalization step
    """
## MANDATORY: Normalize Case Before Matching

**Before ANY comparison, perform this normalization:**

```
normalized_keyword = keyword.lower()
for competitor in competitor_entities:
    normalized_competitor = competitor.lower()
    if normalized_competitor in normalized_keyword:
        return CB
```

**Common case mismatches to catch:**
- "[BRAND]" in list, "[brand]" in keyword -> MUST MATCH
- "[Competitor]" in list, "[COMPETITOR]" in keyword -> MUST MATCH
- "[Brand Name]" in list, "[brand name]" in keyword -> MUST MATCH
""",

    # Iteration 3: Step-by-step matching algorithm
    """
## STEP-BY-STEP BRAND MATCHING ALGORITHM

**You MUST follow these exact steps:**

**Step 1:** Normalize keyword
```
keyword_lower = keyword.toLowerCase()
```

**Step 2:** For each competitor, check for match
```
for competitor in competitor_entities:
    competitor_lower = competitor.toLowerCase()
    if keyword_lower.contains(competitor_lower):
        MATCH FOUND -> return CB
```

**Step 3:** If no matches found -> return null

**CRITICAL:** Case differences NEVER affect matching:
- "[BRAND]" matches "[brand]"
- "[Brand]" matches "[BRAND]"
- "[brand]" matches "[Brand]"
""",

    # Iteration 4: Add explicit examples with case variations
    """
## CASE SENSITIVITY EXAMPLES

**These are ALL matches (case-insensitive):**

| Keyword | Competitor List | Match? | Why |
|---------|-----------------|--------|-----|
| "[brand] product" | ["[BRAND]", "[Other]"] | CB | "[brand]" = "[BRAND]" |
| "[BRAND] product" | ["[brand]", "[Other]"] | CB | "[BRAND]" = "[brand]" |
| "[Brand] product" | ["[BRAND]", "[Other]"] | CB | "[Brand]" = "[BRAND]" |
| "generic product" | ["[Brand]", "[Other]"] | null | No brand present |

**NEVER miss a match due to case:**
- Lowercase keyword + Uppercase competitor = MATCH
- Uppercase keyword + Lowercase competitor = MATCH
- Mixed case = MATCH
""",

    # Iteration 5: Add pre-flight check
    """
## PRE-FLIGHT CASE NORMALIZATION CHECK

**Before outputting, verify you performed case-insensitive matching:**

[ ] Did I convert keyword to lowercase?
[ ] Did I convert EACH competitor to lowercase?
[ ] Did I check if lowercase keyword CONTAINS lowercase competitor?

If keyword contains ANY competitor (ignoring case), return CB.
If keyword contains NO competitor (after case normalization), return null.

**FAILURE MODE:** Returning null when "[brand]" is in keyword but "[BRAND]" is in list.
**FIX:** Always lowercase both sides before comparing.
""",

    # Iteration 6: Stronger emphasis
    """
## CRITICAL RULE: CASE DOES NOT MATTER

**This is the #1 cause of errors. Fix it by:**

1. ALWAYS lowercase the keyword first
2. ALWAYS lowercase each competitor before checking
3. NEVER skip a match because of case differences

**If you see "[brand]" in keyword and "[BRAND]" in competitor list:**
- This IS a match
- Return CB
- Do NOT return null

**If you return null when a competitor IS in the keyword (different case), you have FAILED.**
""",

    # Iteration 7: Add explicit algorithm with verification
    """
## BRAND MATCHING WITH VERIFICATION

**Algorithm:**
```python
def check_competitor(keyword, competitors):
    kw = keyword.lower()  # Step 1: lowercase keyword
    for c in competitors:
        cl = c.lower()     # Step 2: lowercase competitor
        if cl in kw:       # Step 3: substring check
            return "CB"    # MATCH FOUND
    return None           # No match
```

**Self-verification before output:**
1. What is keyword.lower()? "[brand] product" -> "[brand] product"
2. What is competitor.lower() for each? "[BRAND]" -> "[brand]"
3. Is "[brand]" in "[brand] product"? YES -> CB

**If your analysis finds a competitor but you return null, you made a case error.**
""",

    # Iteration 8: Add reasoning template
    """
## REASONING TEMPLATE FOR CASE-INSENSITIVE MATCHING

**Always structure your reasoning as:**

1. "Normalizing keyword '[keyword]' to lowercase: '[keyword_lower]'"
2. "Checking competitor '[Competitor]' (lowercase: '[competitor]')"
3. "Match found: '[competitor]' is in '[keyword_lower]'" OR "No match"
4. "Classification: CB" OR "Classification: null"

**Example reasoning:**
- "Normalizing '[brand] product' to lowercase: '[brand] product'"
- "Checking '[BRAND]' (lowercase: '[brand]')"
- "Match found: '[brand]' is in '[brand] product'"
- "Classification: CB"
""",

    # Iteration 9: Add explicit edge cases
    """
## EDGE CASES - ALL ARE CB

These ALL require CB because the competitor IS present (case-insensitive):

1. Keyword: "[brand] silicone product" | Competitors: ["[BRAND]", "[Other]"] -> CB
   - "[brand]" matches "[BRAND]"

2. Keyword: "[BRAND] oven mitt" | Competitors: ["[Brand]", "[Other]"] -> CB
   - "[BRAND]" matches "[Brand]"

3. Keyword: "[competitor] item" | Competitors: ["[COMPETITOR]", "[Other]"] -> CB
   - "[competitor]" matches "[COMPETITOR]"

**NEVER return null for these cases. The competitor IS present.**
""",

    # Iteration 10: Add failure prevention
    """
## PREVENTING CASE-SENSITIVITY FAILURES

**Common failures to avoid:**

FAILURE: keyword="[brand] product", competitors=["[BRAND]"], output=null
FIX: "[brand]" IS "[BRAND]" (case-insensitive) -> should be CB

FAILURE: keyword="[competitor] item", competitors=["[Competitor]"], output=null
FIX: "[competitor]" IS "[Competitor]" (case-insensitive) -> should be CB

**Prevention checklist:**
1. Am I comparing lowercase to lowercase?
2. Did I convert BOTH sides before comparing?
3. If keyword contains ANY form of a competitor name, did I return CB?
""",

    # Iteration 11: Add explicit matching function
    """
## EXPLICIT CASE-INSENSITIVE MATCHING

**Use this exact matching logic:**

For keyword K and competitor C:
- K_lower = K.lower()
- C_lower = C.lower()
- if C_lower is substring of K_lower: RETURN CB

**Apply to ALL competitors in list, stop at first match.**

Example walkthrough:
- K = "[brand] ice maker"
- K_lower = "[brand] ice maker"
- C1 = "[BRAND]" -> C1_lower = "[brand]"
- Is "[brand]" in "[brand] ice maker"? YES -> RETURN CB immediately

**Do NOT continue checking after finding a match. Return CB immediately.**
""",

    # Iteration 12: Add binary decision tree
    """
## BINARY DECISION TREE FOR BRAND MATCHING

```
START
  |
  v
Convert keyword to lowercase
  |
  v
For each competitor:
  |
  v
Convert competitor to lowercase
  |
  v
Is competitor_lower in keyword_lower?
  |
  +-- YES --> RETURN CB (stop here, done)
  |
  +-- NO --> Continue to next competitor
  |
  v
After checking ALL competitors:
No matches found --> RETURN null
```

**CRITICAL:** The "YES" branch goes directly to CB. Do not override with null.
""",

    # Iteration 13: Add test cases
    """
## TEST CASES FOR VALIDATION

Before outputting, mentally run these test cases:

Test 1: keyword="[brand] product", competitors=["[BRAND]"]
- "[brand]".lower() = "[brand]"
- "[BRAND]".lower() = "[brand]"
- "[brand]" in "[brand] product"? YES
- Expected: CB (NOT null)

Test 2: keyword="generic product", competitors=["[Brand]"]
- "generic product".lower() = "generic product"
- "[Brand]".lower() = "[brand]"
- "[brand]" in "generic product"? NO
- Expected: null

If your output differs from expected, you have a bug.
""",

    # Iteration 14: Final emphasis on the fix
    """
## FINAL FIX: CASE-INSENSITIVE STRING MATCHING

**The ONLY correct way to match brands:**

1. keyword_normalized = keyword.to_lowercase()
2. for each competitor in list:
   a. competitor_normalized = competitor.to_lowercase()
   b. if keyword_normalized.includes(competitor_normalized):
      return CB
3. return null (only if no matches found)

**The error you are fixing:**
- OLD (wrong): comparing "[brand]" to "[BRAND]" as different strings
- NEW (correct): comparing "[brand]" to "[brand]" after normalization

**Remember:** Case differences should NEVER cause a missed match.
""",

    # Iteration 15: Ultra-explicit instruction
    """
## ABSOLUTE RULE: IGNORE CASE COMPLETELY

**When comparing keyword to competitor list:**

1. PRETEND all text is already lowercase
2. "[BRAND]" and "[brand]" are THE SAME WORD
3. "[Competitor]" and "[COMPETITOR]" are THE SAME WORD

**Mental substitution:**
- See "[brand]" in keyword? Look for "[brand]" OR "[BRAND]" OR "[Brand]" in list
- See "[BRAND]" in list? It matches "[brand]" in keyword

**Final check before output:**
"Is there ANY competitor (in ANY case) that appears (in ANY case) in the keyword?"
- YES -> CB
- NO -> null

**DO NOT let case differences cause a null when a match exists.**
"""
]


def run_experiment(max_iterations: int = 15):
    """Run the full M04 case-insensitive fix experiment."""

    print("=" * 70)
    print("M04 CASE-INSENSITIVE MATCHING FIX EXPERIMENT")
    print(f"Model: {MODEL}")
    print(f"Samples: {len(M04_FAILING_SAMPLES)}")
    print(f"Max iterations: {max_iterations}")
    print("=" * 70)

    base_prompt = load_prompt()

    iteration_history = []

    # Iteration 0: Baseline (no fix)
    print(f"\n{'='*70}")
    print("ITERATION 0 (BASELINE)")
    print("=" * 70)

    baseline_result = run_iteration(base_prompt, "", M04_FAILING_SAMPLES, 0)

    print(f"\nResults: {baseline_result['passed']}/{baseline_result['total']} passed ({baseline_result['pass_rate']*100:.1f}%)")
    for r in baseline_result["results"]:
        status = "[OK]" if r["pass"] else "[FAIL]"
        print(f"  {status} '{r['keyword']}' - {r['reason']}")

    iteration_history.append({
        "iteration": 0,
        "fix": "(baseline - no modification)",
        "passed": baseline_result["passed"],
        "total": baseline_result["total"],
        "pass_rate": baseline_result["pass_rate"],
    })

    # Run iterations 1-15
    for i in range(1, min(max_iterations + 1, len(MODIFICATIONS) + 1)):
        print(f"\n{'='*70}")
        print(f"ITERATION {i}")
        print("=" * 70)

        fix = MODIFICATIONS[i - 1]
        print(f"Fix: {fix[:100]}...")

        result = run_iteration(base_prompt, fix, M04_FAILING_SAMPLES, i)

        print(f"\nResults: {result['passed']}/{result['total']} passed ({result['pass_rate']*100:.1f}%)")
        for r in result["results"]:
            status = "[OK]" if r["pass"] else "[FAIL]"
            print(f"  {status} '{r['keyword']}' - {r['reason']}")

        iteration_history.append({
            "iteration": i,
            "fix": fix[:200] + "..." if len(fix) > 200 else fix,
            "passed": result["passed"],
            "total": result["total"],
            "pass_rate": result["pass_rate"],
        })

        # Early stop if 100% pass rate
        if result["pass_rate"] >= 1.0:
            print(f"\n[SUCCESS] 100% pass rate achieved at iteration {i}!")
            break

    # Find best iteration
    best = max(iteration_history, key=lambda x: x["pass_rate"])

    # Summary
    print("\n" + "=" * 70)
    print("ITERATION SUMMARY")
    print("=" * 70)

    progression = []
    for h in iteration_history:
        rate = h["pass_rate"] * 100
        progression.append(rate)
        print(f"  Iter {h['iteration']}: {h['passed']}/{h['total']} ({rate:.1f}%)")

    print(f"\nBest: Iteration {best['iteration']} with {best['pass_rate']*100:.1f}%")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = PROJECT_ROOT / f"evaluation_KD/experiment_results/m04_case_fix_{timestamp}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    final_output = {
        "rubric": "Correct CB/null Classification",
        "baseline_pass_rate": iteration_history[0]["pass_rate"] * 100,
        "iterations": [
            {
                "iteration": h["iteration"],
                "change": h["fix"][:100] + "..." if len(h["fix"]) > 100 else h["fix"],
                "pass_rate": h["pass_rate"] * 100
            }
            for h in iteration_history[1:]
        ],
        "best_iteration": best["iteration"],
        "best_pass_rate": best["pass_rate"] * 100,
        "best_change_description": "Add explicit case-insensitive matching algorithm: convert BOTH keyword and each competitor to lowercase before substring comparison. Use [brand].lower() contains [BRAND].lower() pattern.",
        "progression": progression
    }

    with open(output_path, 'w') as f:
        json.dump(final_output, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    # Print final JSON output
    print("\n" + "=" * 70)
    print("FINAL RESULTS (JSON)")
    print("=" * 70)
    print(json.dumps(final_output, indent=2))

    return final_output


if __name__ == "__main__":
    run_experiment(15)
