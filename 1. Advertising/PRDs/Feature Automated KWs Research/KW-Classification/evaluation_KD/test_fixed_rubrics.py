#!/usr/bin/env python3
"""
Test fixed rubrics on previously failing samples.
Verifies that the rubric corrections produce correct PASS/FAIL verdicts.
"""

import json
import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o-mini"

# Fixed rubrics for testing
FIXED_RUBRICS = {
    'M04': [
        {'id': 'M04_correct_classification', 'criterion': 'Correct Classification', 'check': 'CB when competitor brand in keyword (case-insensitive), null for generic keywords', 'fail': '- CB returned but keyword contains NO brand from competitor list\n- null returned but keyword clearly contains a competitor brand name', 'pass': '- CB when keyword contains brand from competitors list (case-insensitive: "le creuset" = "Le Creuset")\n- null for generic keywords with no brand names (e.g., "silicone oven mitt", "bluetooth earbuds")'},
        {'id': 'M04_own_brand_excluded', 'criterion': 'Own Brand Excluded', 'check': 'The own_brand specified in INPUT is never classified as CB', 'fail': '- ONLY FAIL if the exact own_brand from input appears in keyword AND output is CB\n- e.g., if own_brand="KitchenAid" and keyword="kitchenaid oven mitt" returns CB → FAIL', 'pass': '- PASS if own_brand is NOT in the keyword\n- PASS if own_brand is in keyword but output is null\n- PASS if keyword contains OTHER brands (competitors) that return CB - that is CORRECT behavior\n- IMPORTANT: Le Creuset, HOMWE, OXO are NOT own brand if own_brand="KitchenAid"'},
        {'id': 'M04_case_insensitive_matching', 'criterion': 'Case Insensitive Matching', 'check': 'Brand matching ignores case differences', 'fail': '- Missed match due to case difference (e.g., "oxo" not matching "OXO")\n- IMPORTANT: "homwe" = "HOMWE" = "Homwe" - these are the SAME brand, not substrings', 'pass': '- Case variations correctly matched: "le creuset" = "Le Creuset" = "LE CREUSET"\n- "oxo" matches "OXO", "sony" matches "Sony"'},
    ],
    'M06': [
        {'id': 'M06_three_level_hierarchy', 'criterion': 'Three-Level Hierarchy', 'check': 'Output has EXACTLY 3 levels: Product Type > Category > Department', 'fail': '- Missing levels (only 1 or 2 levels returned)\n- More than 3 levels returned\n- Empty/blank levels', 'pass': '- EXACTLY 3 levels present\n- Level 1: Specific product type (e.g., "True Wireless Earbuds")\n- Level 2: Category (e.g., "Headphones")\n- Level 3: Department (e.g., "Electronics")\n- Order is specific-to-broad'},
        {'id': 'M06_product_type_focused', 'criterion': 'Product Type Focused', 'check': 'Taxonomy describes WHAT the product IS, not features', 'fail': '- Feature-based taxonomy (e.g., "Wireless Products" instead of product type)\n- Marketing terms in taxonomy', 'pass': '- Taxonomy describes product category/type\n- Features like "wireless", "insulated" in Level 1 are acceptable if they describe the product type'},
    ],
    'M11': [
        {'id': 'M11_constraint_count', 'criterion': 'Constraint Count Reasonable', 'check': 'Most consumer products should have 0 hard constraints', 'fail': '- 2+ hard constraints for typical consumer product\n- IMPORTANT: These are NEVER hard constraints: quality features, durability, performance specs, materials, convenience features', 'pass': '- 0 hard constraints for: earbuds, water bottles, jackets, organizers, phone holders, most kitchen items\n- 1 hard constraint ONLY for: device-specific cases (must fit specific phone), safety items (oven mitt needs heat resistance)\n- Empty array [] is CORRECT for most products'},
        {'id': 'M11_constraints_non_negotiable', 'criterion': 'Constraints Non-Negotiable', 'check': 'Check the OUTPUT hard_constraints array - only device compatibility or safety items are valid', 'fail': '- OUTPUT hard_constraints array contains quality features (Deep Bass, Battery, Waterproof)\n- OUTPUT hard_constraints array contains durability features (Rustproof)\n- OUTPUT hard_constraints array contains materials (Stainless Steel)\n- OUTPUT hard_constraints array contains product mechanisms (Vacuum suction, Magnetic)\n- IMPORTANT: Only check what is IN the OUTPUT hard_constraints array, not the input attributes', 'pass': '- OUTPUT hard_constraints is empty [] → PASS (correct for most products)\n- OUTPUT hard_constraints contains only device compatibility or safety items → PASS\n- IMPORTANT: If hard_constraints=[] in output, this criterion PASSES'},
    ],
}

# Test cases - previously failing samples with their module outputs
TEST_CASES = {
    'M04': [
        {
            'name': 'le creuset oven mitt - should be CB',
            'input': {
                'keyword': 'le creuset oven mitt',
                'own_brand': 'KitchenAid',
                'competitor_entities': ['Le Creuset', 'OXO', 'HOMWE', 'Cuisinart']
            },
            'output': {
                'branding_scope_2': 'CB',
                'confidence': 0.95,
                'reasoning': 'Keyword contains "le creuset" which matches competitor entity "Le Creuset"'
            },
            'expected_verdicts': {
                'M04_correct_classification': 'PASS',  # CB is correct
                'M04_own_brand_excluded': 'PASS',  # Le Creuset is NOT own brand (KitchenAid is)
                'M04_case_insensitive_matching': 'PASS',  # Case match worked
            }
        },
        {
            'name': 'homwe silicone oven mitt - should be CB',
            'input': {
                'keyword': 'homwe silicone oven mitt',
                'own_brand': 'KitchenAid',
                'competitor_entities': ['Le Creuset', 'OXO', 'HOMWE', 'Cuisinart']
            },
            'output': {
                'branding_scope_2': 'CB',
                'confidence': 0.95,
                'reasoning': 'Keyword contains "homwe" which matches competitor entity "HOMWE"'
            },
            'expected_verdicts': {
                'M04_correct_classification': 'PASS',  # CB is correct
                'M04_own_brand_excluded': 'PASS',  # HOMWE is NOT own brand (KitchenAid is)
                'M04_case_insensitive_matching': 'PASS',  # homwe = HOMWE
            }
        },
        {
            'name': 'silicone oven mitt - should be null (generic)',
            'input': {
                'keyword': 'silicone oven mitt',
                'own_brand': 'KitchenAid',
                'competitor_entities': ['Le Creuset', 'OXO', 'HOMWE', 'Cuisinart']
            },
            'output': {
                'branding_scope_2': None,
                'confidence': 0.9,
                'reasoning': 'No competitor brand found in keyword'
            },
            'expected_verdicts': {
                'M04_correct_classification': 'PASS',  # null is correct for generic
                'M04_own_brand_excluded': 'PASS',  # No brand to exclude
                'M04_case_insensitive_matching': 'PASS',  # N/A but should pass
            }
        },
    ],
    'M06': [
        {
            'name': 'JBL Earbuds - 3 level taxonomy',
            'input': {
                'title': 'JBL Vibe Beam - True Wireless JBL Deep Bass Sound Earbuds'
            },
            'output': {
                'product_type_taxonomy': [
                    {'level': 1, 'value': 'True Wireless Earbuds'},
                    {'level': 2, 'value': 'Headphones'},
                    {'level': 3, 'value': 'Electronics'}
                ]
            },
            'expected_verdicts': {
                'M06_three_level_hierarchy': 'PASS',  # Exactly 3 levels, specific to broad
                'M06_product_type_focused': 'PASS',  # Describes product type
            }
        },
        {
            'name': 'Water Bottle - 1 level only (should fail)',
            'input': {
                'title': 'Owala FreeSip Insulated Stainless Steel Water Bottle'
            },
            'output': {
                'product_type_taxonomy': [
                    {'level': 1, 'value': 'Water Bottle'}
                ]
            },
            'expected_verdicts': {
                'M06_three_level_hierarchy': 'FAIL',  # Only 1 level, should be 3
                'M06_product_type_focused': 'PASS',  # Describes product type (just not enough levels)
            }
        },
    ],
    'M11': [
        {
            'name': 'JBL Earbuds - 0 constraints (correct)',
            'input': {
                'title': 'JBL Vibe Beam - True Wireless Earbuds, Bluetooth 5.2',
                'attributes': ['Bluetooth 5.2', 'Deep Bass Sound', 'Water Resistant', '32 Hours Battery']
            },
            'output': {
                'hard_constraints': [],
                'reasoning': 'Consumer electronics with no device-specific requirements'
            },
            'expected_verdicts': {
                'M11_constraint_count': 'PASS',  # 0 is correct
                'M11_constraints_non_negotiable': 'PASS',  # Empty is correct
            }
        },
        {
            'name': 'Phone Holder - 2 constraints (incorrect - should be 0)',
            'input': {
                'title': 'Jikasho Vacuum Magnetic Suction Phone Holder',
                'attributes': ['Vacuum-lock suction', 'Magnetic mount', 'Foldable', '360 degree swivel']
            },
            'output': {
                'hard_constraints': ['Vacuum-lock suction', 'Magnetic mount'],
                'reasoning': 'These mechanisms are essential'
            },
            'expected_verdicts': {
                'M11_constraint_count': 'FAIL',  # 2 is too many
                'M11_constraints_non_negotiable': 'FAIL',  # These are product-defining, not constraints
            }
        },
        {
            'name': 'Water Bottle - 0 constraints (correct)',
            'input': {
                'title': 'Owala FreeSip Insulated Stainless Steel Water Bottle, 24 Oz',
                'attributes': ['Stainless Steel', '24 Ounce', 'Insulated', 'BPA-Free']
            },
            'output': {
                'hard_constraints': [],
                'reasoning': 'Standard water bottle with no specific requirements'
            },
            'expected_verdicts': {
                'M11_constraint_count': 'PASS',  # 0 is correct
                'M11_constraints_non_negotiable': 'PASS',  # Empty is correct
            }
        },
    ],
}


def call_judge(rubric: dict, input_data: dict, output_data: dict) -> dict:
    """Call GPT to judge a sample against a rubric."""

    prompt = f"""You are evaluating an LLM output against a rubric criterion.

## Rubric
- **Criterion**: {rubric['criterion']}
- **Check**: {rubric['check']}
- **PASS conditions**: {rubric['pass']}
- **FAIL conditions**: {rubric['fail']}

## Input Data
{json.dumps(input_data, indent=2)}

## Module Output
{json.dumps(output_data, indent=2)}

## Task
Evaluate whether the module output meets the rubric criterion.

Return ONLY a JSON object:
{{"verdict": "PASS" or "FAIL", "reasoning": "Brief explanation"}}
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"verdict": "ERROR", "reasoning": str(e)}


def run_tests():
    """Run all test cases and report results."""

    print("=" * 70)
    print("TESTING FIXED RUBRICS")
    print("=" * 70)

    total_tests = 0
    passed_tests = 0

    for module, test_cases in TEST_CASES.items():
        print(f"\n{'='*70}")
        print(f"MODULE: {module}")
        print("=" * 70)

        for test in test_cases:
            print(f"\n  Test: {test['name']}")

            for rubric_id, expected_verdict in test['expected_verdicts'].items():
                # Find the rubric
                rubric = next((r for r in FIXED_RUBRICS[module] if r['id'] == rubric_id), None)
                if not rubric:
                    print(f"    ⚠ Rubric {rubric_id} not found")
                    continue

                # Call judge
                result = call_judge(rubric, test['input'], test['output'])
                actual_verdict = result.get('verdict', 'ERROR')

                total_tests += 1

                if actual_verdict == expected_verdict:
                    passed_tests += 1
                    status = "✓"
                else:
                    status = "✗"

                print(f"    {status} {rubric['criterion']}: {actual_verdict} (expected {expected_verdict})")
                if actual_verdict != expected_verdict:
                    print(f"      Reasoning: {result.get('reasoning', 'N/A')[:100]}")

    print("\n" + "=" * 70)
    print(f"RESULTS: {passed_tests}/{total_tests} tests passed ({100*passed_tests/total_tests:.1f}%)")
    print("=" * 70)

    return passed_tests, total_tests


if __name__ == "__main__":
    run_tests()
