#!/usr/bin/env python3
"""
LLM-as-a-Judge Evaluation for Module Outputs.

Uses GPT-4o mini to evaluate module outputs against rubrics.
Reasoning-first (CoT) structure: judge explains reasoning before verdict.

Usage:
    python evaluation/run_llm_judge.py --module m01 --limit 5
    python evaluation/run_llm_judge.py --module m01 --rubric M01_no_product_words
"""

import argparse
import json
import os
import sys
import yaml
from pathlib import Path
from datetime import datetime
from typing import Optional

# OpenAI API
from openai import OpenAI

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATASETS_DIR = PROJECT_ROOT / "datasets"
RESULTS_DIR = PROJECT_ROOT / "batch_requests" / "20260112_2127" / "results"
CONFIG_DIR = SCRIPT_DIR / "config"

# Default rubric version (latest)
DEFAULT_RUBRICS_VERSION = "v2"


def get_rubrics_file(version: str = None) -> Path:
    """Get the rubrics file path for a specific version."""
    version = version or DEFAULT_RUBRICS_VERSION
    # Support both "v2" and "2" formats
    version_num = version.replace("v", "").replace("V", "")
    rubrics_file = CONFIG_DIR / f"rubrics_v{version_num}.yaml"
    return rubrics_file


def list_available_rubric_versions() -> list:
    """List all available rubric versions."""
    versions = []
    for f in CONFIG_DIR.glob("rubrics_v*.yaml"):
        version = f.stem.replace("rubrics_v", "")
        versions.append(f"v{version}")
    return sorted(versions)


def load_rubrics_from_yaml(version: str = None):
    """Load rubrics from versioned yaml file and convert to simpler format.

    Args:
        version: Rubric version (e.g., "v1", "v2", "2"). Defaults to latest.

    Returns:
        dict: Module -> list of rubrics
    """
    rubrics_file = get_rubrics_file(version)

    if not rubrics_file.exists():
        available = list_available_rubric_versions()
        print(f"ERROR: Rubrics file not found: {rubrics_file}")
        print(f"Available versions: {', '.join(available)}")
        return None

    print(f"INFO: Loading rubrics from {rubrics_file.name}")

    with open(rubrics_file) as f:
        data = yaml.safe_load(f)

    # Print version info
    yaml_version = data.get('version', 'unknown')
    print(f"INFO: Rubrics version {yaml_version}")

    rubrics_data = {}
    yaml_rubrics = data.get('rubrics', {})

    for rubric_id, rubric in yaml_rubrics.items():
        module = rubric.get('module', '')
        if module not in rubrics_data:
            rubrics_data[module] = []

        # Convert to simpler format
        simple_rubric = {
            'id': rubric_id,
            'criterion': rubric.get('criterion', ''),
            'check': rubric.get('check', ''),
            'fail': rubric.get('fail_definition', '').strip(),
            'pass': rubric.get('pass_definition', '').strip()
        }
        rubrics_data[module].append(simple_rubric)

    # Print coverage summary
    total_rubrics = sum(len(r) for r in rubrics_data.values())
    print(f"INFO: Loaded {len(rubrics_data)} modules, {total_rubrics} rubrics")

    return rubrics_data

# Load environment variables
def load_env():
    """Load API key from .env file."""
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip().strip('"').strip("'")

load_env()

# Module rubrics (from generate_interactive_report.py)
RUBRIC_DATA = {
    'M01': [
        {'id': 'M01_brand_extracted', 'criterion': 'Brand Extracted', 'check': 'Brand extracted from title or listing_brand field', 'fail': '- Empty output when title contains brand name\n- Empty output when listing_brand field has value', 'pass': '- brand_name matches brand found in title OR listing_brand field'},
        {'id': 'M01_no_hallucination', 'criterion': 'No Hallucination', 'check': 'Base brand must come from input; typos must be variations of that brand', 'fail': '- Output contains a completely different brand not related to input (e.g., "Sony" when input brand is "JBL")\n- Brand name invented from scratch, not derived from input brand', 'pass': '- All base brands traceable to input data (e.g., brand_name, title, manufacturer)\n- Typos/variations are clearly derived from the input brand (e.g., "JLB", "jbl" from "JBL")'},
        {'id': 'M01_no_product_words', 'criterion': 'No Product Words', 'check': 'No generic product/feature words in brand output', 'fail': '- Brand contains generic product words (e.g., Wireless, Bluetooth, Speaker, Headphones, Charger, etc.)\n- Product category used as brand name', 'pass': '- Output contains only actual brand/trademark names\n- No generic descriptors or product types'},
        {'id': 'M01_amazon_test_applied', 'criterion': 'Amazon Test Applied', 'check': 'Entity is a brand you search FOR, not a product you search TO BUY', 'fail': '- Searching the entity on Amazon returns a product category, not a brand (e.g., "Wireless Earbuds" → shows earbuds listings, not a brand page)', 'pass': '- Searching the entity on Amazon returns brand-specific results (e.g., "JBL" → shows JBL brand page/products, "Sony" → shows Sony products)\n- The entity is something customers search FOR to find products, not something they search TO BUY directly'},
        {'id': 'M01_no_duplicates', 'criterion': 'No Duplicates', 'check': 'No exact duplicate strings in list', 'fail': '- Exact same string appears more than once (e.g., "JBL", "JBL")', 'pass': '- Each string in list is unique\n- Case variations are different entries, not duplicates (e.g., "JBL" and "jbl" are both valid)'},
    ],
    'M01a': [
        {'id': 'M01a_has_variations', 'criterion': 'Has Variations', 'check': 'Multiple brand variations generated', 'fail': '- Only 1 variation returned\n- Empty list', 'pass': '- Multiple variations generated'},
        {'id': 'M01a_no_unrelated_terms', 'criterion': 'No Unrelated Terms', 'check': 'All variations are misspellings/typos of the SAME brand only', 'fail': '- Contains different brand names (e.g., "Sony" in JBL variations)\n- Contains product words (e.g., "Earbuds", "Speaker")\n- Contains sub-brand names (should be in M01b)', 'pass': '- All items are typos/case variations/misspellings of the input brand_name only'},
        {'id': 'M01a_count_in_range', 'criterion': '8-12 Count', 'check': 'Exactly 8-12 variations', 'fail': '- Fewer than 8 variations\n- More than 12 variations', 'pass': '- Exactly 8-12 variations in the list'},
        {'id': 'M01a_first_is_canonical', 'criterion': 'First is Canonical', 'check': 'First variation matches input brand_name exactly', 'fail': '- First item differs from input brand_name\n- First item has typos, spacing changes, or case changes', 'pass': '- variations[0] === brand_name (exact match)'},
    ],
    'M01b': [
        {'id': 'M01b_sub_brands_found', 'criterion': 'Sub-brands Found', 'check': 'Sub-brands, product lines, brand-owned tech extracted from listing', 'fail': '- Sub-brand mentioned in title/bullets not captured\n- Product line name in listing not captured', 'pass': '- sub_brands array contains product families, series names, brand-owned tech mentioned in listing'},
        {'id': 'M01b_no_universal_standards', 'criterion': 'No Universal Standards', 'check': 'No universal/industry standards listed as brand-specific', 'fail': '- Universal standards included as brand-specific (e.g., Bluetooth, USB-C, WiFi, HDMI, NFC, Qi, etc.)', 'pass': '- Only proprietary brand-owned terms included\n- No industry-wide standards or protocols'},
        {'id': 'M01b_manufacturer_null_when_same', 'criterion': 'Manufacturer Null When Same', 'check': 'Manufacturer=null when same as brand', 'fail': '- Returned manufacturer when = brand_name', 'pass': '- Returns null when manufacturer matches brand'},
        {'id': 'M01b_searchable_standards_default_empty', 'criterion': 'Searchable Standards Empty', 'check': 'searchable_standards empty unless customers actively search for standard by name', 'fail': '- Technical standards included (e.g., ENFit, USB-C, Bluetooth)\n- Standards customers don\'t search for by name', 'pass': '- Empty array (most products)\n- Only brand-like standards people search: Gore-Tex, Dolby Atmos, THX'},
    ],
    'M02': [
        {'id': 'M02_correct_classification', 'criterion': 'Correct Classification', 'check': 'OB when keyword contains brand from variations_own, null otherwise', 'fail': '- OB returned but keyword has no match in variations_own or related_terms_own\n- null returned but keyword contains exact term from variations_own', 'pass': '- OB only when keyword contains term from variations_own/related_terms_own\n- null when no match found (passes to M03)'},
        {'id': 'M02_brand_match_found', 'criterion': 'Brand Match Found', 'check': 'Brand from variations_own detected in keyword when present', 'fail': '- Missed brand that exists in variations_own input', 'pass': '- Brand correctly detected by matching against variations_own list'},
        {'id': 'M02_no_false_positives', 'criterion': 'No False Positives', 'check': 'No generic words flagged as brand', 'fail': '- Generic words flagged as brand (e.g., "wireless", "bluetooth", "speaker")', 'pass': '- Only actual brand/trademark names matched'},
        {'id': 'M02_case_insensitive', 'criterion': 'Case Insensitive', 'check': 'Brand matching ignores uppercase/lowercase differences', 'fail': '- Case difference caused missed match (e.g., "jbl" in keyword didn\'t match "JBL" in variations_own)', 'pass': '- Brand matched regardless of case (e.g., "jbl", "JBL", "Jbl" all match)'},
        {'id': 'M02_word_boundary_respected', 'criterion': 'Word Boundary Respected', 'check': 'Partial matches rejected (jbl ≠ jblue)', 'fail': '- "jbl" incorrectly matched "jblue"\n- Substring match accepted', 'pass': '- Only whole word matches accepted'},
    ],
    'M03': [
        {'id': 'M03_competitors_relevant', 'criterion': 'Competitors Relevant', 'check': 'All competitors sell products in same category as ASIN', 'fail': '- Brands from different product categories\n- Generic retailers included (e.g., Amazon, Walmart, Target)\n- Own brand included in competitors list', 'pass': '- All brands sell similar products to the ASIN\n- No unrelated brands or retailers'},
        {'id': 'M03_competitor_count', 'criterion': 'Competitor Count', 'check': '5-10 distinct competitor brands included', 'fail': '- Fewer than 5 distinct brands\n- More than 10 distinct brands', 'pass': '- 5-10 unique competitor brand names'},
        {'id': 'M03_no_hallucinated_brands', 'criterion': 'No Hallucinated Brands', 'check': 'Base competitor brands are verifiable real brands (typos/misspellings of real brands are valid per prompt requirements)', 'fail': '- Completely fabricated brand names that don\'t exist as real companies\n- Brand names invented from scratch with no real-world counterpart', 'pass': '- All BASE brands are real companies findable on Amazon/Google\n- Typos/misspellings of real brands are VALID (e.g., "Aple" for Apple, "Sonny" for Sony) - prompt requires these'},
    ],
    'M04': [
        {'id': 'M04_correct_classification', 'criterion': 'Correct Classification', 'check': 'CB when competitor brand in keyword (case-insensitive), null for generic keywords', 'fail': '- CB returned but keyword contains NO brand from competitor list\n- null returned but keyword clearly contains a competitor brand name', 'pass': '- CB when keyword contains brand from competitors list (case-insensitive: "le creuset" = "Le Creuset")\n- null for generic keywords with no brand names (e.g., "silicone oven mitt", "bluetooth earbuds")'},
        {'id': 'M04_own_brand_excluded', 'criterion': 'Own Brand Excluded', 'check': 'The own_brand specified in INPUT is never classified as CB', 'fail': '- ONLY FAIL if the exact own_brand from input appears in keyword AND output is CB\n- e.g., if own_brand="KitchenAid" and keyword="kitchenaid oven mitt" returns CB → FAIL', 'pass': '- PASS if own_brand is NOT in the keyword\n- PASS if own_brand is in keyword but output is null\n- PASS if keyword contains OTHER brands (competitors) that return CB - that is CORRECT behavior\n- IMPORTANT: Le Creuset, HOMWE, OXO are NOT own brand if own_brand="KitchenAid"'},
        {'id': 'M04_case_insensitive_matching', 'criterion': 'Case Insensitive Matching', 'check': 'Brand matching ignores case differences', 'fail': '- Missed match due to case difference (e.g., "oxo" not matching "OXO")\n- IMPORTANT: "homwe" = "HOMWE" = "Homwe" - these are the SAME brand, not substrings', 'pass': '- Case variations correctly matched: "le creuset" = "Le Creuset" = "LE CREUSET"\n- "oxo" matches "OXO", "sony" matches "Sony"'},
        {'id': 'M04_known_brands_detected', 'criterion': 'Known Brands Detected', 'check': 'Well-known brands detected even if not in provided list', 'fail': '- Obvious well-known brand in keyword missed (e.g., Sony, Bose, Apple not detected)', 'pass': '- Common well-known brands detected using category knowledge\n- Brand recognition works beyond just the provided competitor list'},
    ],
    'M05': [
        {'id': 'M05_correct_classification', 'criterion': 'Correct Classification', 'check': 'NB only when keyword has zero brand references', 'fail': '- NB returned but THE KEYWORD ITSELF contains a brand name\n- null returned for truly generic keyword that has no brands', 'pass': '- NB for pure generic keywords (e.g., "wireless bluetooth earbuds", "electronics", "headphones")\n- null when THE KEYWORD contains any brand (not just because brands exist in competitor list)'},
        {'id': 'M05_hidden_brands_detected', 'criterion': 'Hidden Brands Detected', 'check': 'Hidden brands IN THE KEYWORD are caught even if not in provided lists', 'fail': '- THE KEYWORD contains a hidden brand like "beats earbuds" or "echo speaker" but returned NB\n- IMPORTANT: Only fail if the brand appears IN THE KEYWORD, not just in competitor list', 'pass': '- If keyword contains hidden brand (e.g., "beats headphones"), it returns null\n- If keyword is generic with no brands IN IT (e.g., "wireless earbuds"), NB is correct'},
        {'id': 'M05_typo_variations_caught', 'criterion': 'Typo Variations Caught', 'check': 'Brand typos/spacing IN THE KEYWORD are recognized', 'fail': '- THE KEYWORD contains a brand typo like "camel back water bottle" but returned NB\n- IMPORTANT: Only fail if typo appears IN THE KEYWORD, not in competitor list', 'pass': '- If keyword contains typo (e.g., "hydro flask bottle"), it returns null\n- Generic keywords without brand typos correctly return NB'},
        {'id': 'M05_product_lines_recognized', 'criterion': 'Product Lines Recognized', 'check': 'Trademarked product lines IN THE KEYWORD are caught as brands', 'fail': '- THE KEYWORD contains a product line like "airpods case" but returned NB\n- IMPORTANT: Only fail if product line appears IN THE KEYWORD', 'pass': '- If keyword contains product line (e.g., "quietcomfort earbuds"), it returns null\n- Generic keywords without product lines correctly return NB'},
    ],
    'M06': [
        {'id': 'M06_three_level_hierarchy', 'criterion': 'Three-Level Hierarchy', 'check': 'Output has EXACTLY 3 levels: Product Type > Category > Department', 'fail': '- Missing levels (only 1 or 2 levels returned)\n- More than 3 levels returned\n- Empty/blank levels', 'pass': '- EXACTLY 3 levels present\n- Level 1: Specific product type (e.g., "True Wireless Earbuds")\n- Level 2: Category (e.g., "Headphones")\n- Level 3: Department (e.g., "Electronics")\n- Order is specific-to-broad'},
        {'id': 'M06_product_type_focused', 'criterion': 'Product Type Focused', 'check': 'Taxonomy describes WHAT the product IS, not features', 'fail': '- Feature-based taxonomy (e.g., "Wireless Products" instead of product type)\n- Marketing terms in taxonomy', 'pass': '- Taxonomy describes product category/type\n- Features like "wireless", "insulated" in Level 1 are acceptable if they describe the product type'},
        {'id': 'M06_no_brands_in_taxonomy', 'criterion': 'No Brands in Taxonomy', 'check': 'No brand names appear in any taxonomy level', 'fail': '- Brand name in any level (e.g., "JBL Earbuds" instead of "True Wireless Earbuds")\n- Product line names that are brand-specific', 'pass': '- Pure category names without brand mentions\n- Generic product type terminology (e.g., "Puffer Jacket" not "North Face Jacket")'},
        {'id': 'M06_appropriate_specificity', 'criterion': 'Appropriate Specificity', 'check': 'Level 1 is specific enough to identify the product', 'fail': '- Level 1 too generic (e.g., "Electronics" for earbuds, "Kitchen Item" for oven mitt)\n- Level 1 too specific (including model numbers)', 'pass': '- Level 1 identifies the specific product type (e.g., "True Wireless Earbuds", "Insulated Water Bottle", "Kitchen Sink Caddy")\n- Matches what you would see in Amazon product categories'},
    ],
    'M07': [
        {'id': 'M07_attributes_from_listing', 'criterion': 'Attributes From Listing', 'check': 'All attributes extracted are verifiable from the input listing', 'fail': '- Attribute values not found in title/bullets/description\n- Invented/hallucinated attribute values', 'pass': '- Each attribute value can be traced to input data\n- No fabricated specifications'},
        {'id': 'M07_key_attributes_captured', 'criterion': 'Key Attributes Captured', 'check': 'Important product attributes are extracted', 'fail': '- Missing obvious key attributes (size, color, material when mentioned)\n- Only trivial attributes captured', 'pass': '- Core attributes captured (material, size, color, capacity, etc.)\n- Attributes relevant to purchase decisions included'},
        {'id': 'M07_correct_format', 'criterion': 'Correct Format', 'check': 'Output in expected key-value format', 'fail': '- Missing attributes field\n- Attributes not in key-value pairs\n- Malformed JSON', 'pass': '- Attributes returned as key-value pairs\n- Proper JSON structure'},
        {'id': 'M07_no_duplicate_attributes', 'criterion': 'No Duplicate Attributes', 'check': 'No repeated attribute keys', 'fail': '- Same attribute key appears multiple times\n- Redundant attributes with different names', 'pass': '- Each attribute key is unique\n- No redundant information'},
    ],
    'M08': [
        {'id': 'M08_ranks_assigned', 'criterion': 'Ranks Assigned', 'check': 'All attributes have unique sequential rank values within their type', 'fail': '- Attributes missing rank values\n- Duplicate ranks within same type (two Variants both rank 1)\n- Non-sequential ranks (1, 2, 4 - skipped 3)', 'pass': '- Every attribute has a rank starting from 1\n- Ranks are unique and sequential within each type (Variant, UseCase, Audience)\n- If 6 Variants exist, ranks 1-6 are valid'},
        {'id': 'M08_ranks_logical', 'criterion': 'Ranks Logical', 'check': 'Higher ranks for more important purchase decision factors', 'fail': '- Trivial attributes ranked higher than essential ones\n- Illogical ranking (e.g., color ranked higher than core function)', 'pass': '- Core functional attributes ranked 4-5\n- Optional/aesthetic attributes ranked lower\n- Ranking reflects buying decision importance'},
        {'id': 'M08_rank_distribution', 'criterion': 'Rank Distribution', 'check': 'Ranks are distributed, not all same value', 'fail': '- All attributes have same rank\n- No differentiation between importance levels', 'pass': '- Range of ranks used (not all 5s or all 3s)\n- Clear hierarchy of importance shown'},
    ],
    'M09': [
        {'id': 'M09_word_count', 'criterion': 'Word Count 3-6', 'check': 'Primary use phrase is 3-6 words', 'fail': '- Fewer than 3 words\n- More than 6 words', 'pass': '- Phrase contains 3-6 words'},
        {'id': 'M09_describes_function', 'criterion': 'Describes Function', 'check': 'Phrase describes what product DOES, not what it IS', 'fail': '- Just product name (e.g., "water bottle")\n- Features instead of use (e.g., "insulated stainless steel")', 'pass': '- Describes primary purpose/function (e.g., "portable hydration", "personal audio listening")\n- Answers "what does this product do for the user?"'},
        {'id': 'M09_no_adjectives', 'criterion': 'No Adjectives/Marketing', 'check': 'No quality/marketing words in phrase', 'fail': '- Contains adjectives: premium, comfortable, efficient, best, etc.\n- Marketing language: enhanced, superior, advanced', 'pass': '- Pure functional description\n- No quality claims or marketing terms'},
        {'id': 'M09_single_core_action', 'criterion': 'Single Core Action', 'check': 'Describes ONE primary use, not multiple', 'fail': '- Multiple uses combined (e.g., "cutting and slicing")\n- List of functions', 'pass': '- Single unified purpose described\n- One core action/function'},
    ],
    'M10': [
        {'id': 'M10_output_clean', 'criterion': 'Output Clean', 'check': 'validated_use has no adjectives/features/marketing', 'fail': '- validated_use still contains adjectives (premium, comfortable, efficient, etc.)\n- Features or materials remain in output (memory foam, stainless steel, etc.)\n- Marketing language present (enhanced, superior, advanced)', 'pass': '- validated_use is clean 3-6 word phrase describing function\n- No adjectives, features, or marketing terms'},
        {'id': 'M10_word_count', 'criterion': 'Word Count 3-6', 'check': 'validated_use phrase is 3-6 words', 'fail': '- Fewer than 3 words\n- More than 6 words', 'pass': '- Phrase contains 3-6 words'},
        {'id': 'M10_describes_function', 'criterion': 'Describes Function', 'check': 'validated_use describes what product DOES, not what it IS', 'fail': '- Just product name (e.g., "water bottle")\n- Features instead of use (e.g., "insulated stainless steel")', 'pass': '- Describes primary purpose/function (e.g., "portable hydration", "personal audio listening")\n- Answers "what does this product do for the user?"'},
    ],
    'M11': [
        {'id': 'M11_constraint_count', 'criterion': 'Constraint Count Reasonable', 'check': 'Most consumer products should have 0 hard constraints', 'fail': '- 2+ hard constraints for typical consumer product\n- IMPORTANT: These are NEVER hard constraints: quality features, durability, performance specs, materials, convenience features', 'pass': '- 0 hard constraints for: earbuds, water bottles, jackets, organizers, phone holders, most kitchen items\n- 1 hard constraint ONLY for: device-specific cases (must fit specific phone), safety items (oven mitt needs heat resistance)\n- Empty array [] is CORRECT for most products'},
        {'id': 'M11_constraints_non_negotiable', 'criterion': 'Constraints Non-Negotiable', 'check': 'Check the OUTPUT hard_constraints array - only device compatibility or safety items are valid', 'fail': '- OUTPUT hard_constraints array contains quality features (Deep Bass, Battery, Waterproof)\n- OUTPUT hard_constraints array contains durability features (Rustproof)\n- OUTPUT hard_constraints array contains materials (Stainless Steel)\n- OUTPUT hard_constraints array contains product mechanisms (Vacuum suction, Magnetic)\n- IMPORTANT: Only check what is IN the OUTPUT hard_constraints array, not the input attributes', 'pass': '- OUTPUT hard_constraints is empty [] → PASS (correct for most products)\n- OUTPUT hard_constraints contains only device compatibility or safety items → PASS\n- IMPORTANT: If hard_constraints=[] in output, this criterion PASSES'},
        {'id': 'M11_constraints_from_listing', 'criterion': 'Constraints From Listing', 'check': 'If any constraints listed, they must be verifiable from listing', 'fail': '- Invented constraints not mentioned in listing\n- Generic constraints that apply to any product', 'pass': '- Empty array is valid (and expected for most products)\n- If constraint listed, it must be traceable to specific listing data'},
    ],
    'M12': [
        {'id': 'M12_violation_detection', 'criterion': 'Violation Detection', 'check': 'Correctly identifies if keyword violates hard constraints', 'fail': '- Violation missed when keyword contradicts constraint\n- False positive - violation claimed when keyword is compatible', 'pass': '- Correctly identifies violations (e.g., keyword specifies incompatible value)\n- Correctly passes when no violation'},
        {'id': 'M12_x_classification_correct', 'criterion': 'X Classification Correct', 'check': 'Returns X only when genuine violation exists', 'fail': '- Returns X without clear constraint violation\n- Returns null when obvious violation exists', 'pass': '- X returned only when keyword explicitly violates hard constraint\n- null returned when no violation or no hard constraints'},
        {'id': 'M12_reasoning_accurate', 'criterion': 'Reasoning Accurate', 'check': 'Reasoning explains the violation (or lack thereof)', 'fail': '- Reasoning doesn\'t match conclusion\n- Missing explanation of why violation exists/doesn\'t exist', 'pass': '- Clear reasoning connecting constraint to keyword\n- Explains why violation does/doesn\'t occur'},
    ],
    'M12b': [
        {'id': 'M12b_valid_classification', 'criterion': 'Valid Classification', 'check': 'Output is one of R, S, C, N', 'fail': '- Invalid classification value\n- Missing classification field', 'pass': '- classification field contains R, S, C, or N'},
        {'id': 'M12b_decision_tree_followed', 'criterion': 'Decision Tree Followed', 'check': 'Classification follows the module decision tree logic', 'fail': '- Wrong classification for the scenario\n- Skipped decision tree steps', 'pass': '- R: same type + same use\n- S: different type + same use\n- C: different type + complementary\n- N: none of the above'},
        {'id': 'M12b_reasoning_provided', 'criterion': 'Reasoning Provided', 'check': 'Output includes reasoning for classification', 'fail': '- No reasoning field\n- Reasoning empty or minimal', 'pass': '- Reasoning explains why this classification was chosen\n- Connects keyword analysis to decision'},
    ],
    'M13': [
        {'id': 'M13_same_type_detection', 'criterion': 'Same Type Detection', 'check': 'Correctly identifies if keyword asks for same product type', 'fail': '- Same type called different (e.g., "water bottle" keyword for water bottle ASIN marked different)\n- Different type called same', 'pass': '- Correctly identifies when keyword asks for same product type as ASIN\n- Correctly identifies when keyword asks for different product type'},
        {'id': 'M13_taxonomy_used', 'criterion': 'Taxonomy Used', 'check': 'Uses product type taxonomy for comparison', 'fail': '- Ignores taxonomy when making decision\n- Only looks at surface keywords without type analysis', 'pass': '- References product type from taxonomy\n- Compares keyword product type to ASIN product type'},
        {'id': 'M13_variation_handling', 'criterion': 'Variation Handling', 'check': 'Variations of same type counted as same (e.g., plastic bottle vs metal bottle)', 'fail': '- Material variations marked as different product type\n- Size/color variations marked as different type', 'pass': '- Same product type with different attributes = same type\n- Only genuinely different product categories = different type'},
    ],
    'M14': [
        {'id': 'M14_same_type_only', 'criterion': 'Same Type Only', 'check': 'Module only handles same product type cases', 'fail': '- Processing a different product type case\n- Wrong module invoked', 'pass': '- Input is correctly for same product type scenario\n- Proceeds with primary use comparison'},
        {'id': 'M14_use_comparison', 'criterion': 'Use Comparison', 'check': 'Compares primary use of keyword product to ASIN', 'fail': '- Ignores validated_use in comparison\n- Compares features instead of use', 'pass': '- Uses validated_use for comparison\n- Determines if keyword product serves same primary use'},
        {'id': 'M14_r_or_n_correct', 'criterion': 'R or N Correct', 'check': 'Returns R when same use, N when different use', 'fail': '- R returned but uses are different\n- N returned but uses are same', 'pass': '- R (Relevant) when keyword product serves same primary use\n- N (Not relevant) when keyword product serves different use'},
    ],
    'M15': [
        {'id': 'M15_different_type_only', 'criterion': 'Different Type Only', 'check': 'Module only handles different product type cases', 'fail': '- Processing a same product type case\n- Wrong module invoked', 'pass': '- Input is correctly for different product type scenario\n- Proceeds with substitute analysis'},
        {'id': 'M15_substitute_criteria', 'criterion': 'Substitute Criteria', 'check': 'Applies 60% overlap rule for substitutes', 'fail': '- Ignores primary use comparison\n- Too strict (requires 100% match) or too loose', 'pass': '- S when ≥60% primary use overlap\n- Considers if buyer could choose either for same need'},
        {'id': 'M15_s_or_pass_correct', 'criterion': 'S or Pass Correct', 'check': 'Returns S when substitute, passes to M16 otherwise', 'fail': '- S returned for clearly non-substitute\n- Passed to M16 when obvious substitute', 'pass': '- S when different type but same primary use\n- Passes to M16 when different primary use'},
    ],
    'M16': [
        {'id': 'M16_complementary_check', 'criterion': 'Complementary Check', 'check': 'Determines if products are commonly used together', 'fail': '- C returned for unrelated products\n- N returned for obvious companions', 'pass': '- C when products are commonly purchased/used together\n- e.g., phone case for phone, cleaning brush for water bottle'},
        {'id': 'M16_c_or_n_correct', 'criterion': 'C or N Correct', 'check': 'Returns C for complements, N for unrelated', 'fail': '- Wrong classification for the relationship\n- Missing reasoning for decision', 'pass': '- C (Complementary) when keyword product accompanies ASIN\n- N (Not relevant) when no relationship exists'},
        {'id': 'M16_companion_reasoning', 'criterion': 'Companion Reasoning', 'check': 'Explains the complementary relationship (or lack thereof)', 'fail': '- No explanation of why products are/aren\'t complementary\n- Reasoning doesn\'t match conclusion', 'pass': '- Clear reasoning about usage relationship\n- Explains how products are used together (or aren\'t)'},
    ],
}

# Try to load rubrics from default version (source of truth)
# Falls back to hardcoded RUBRIC_DATA if yaml not found
_yaml_rubrics = load_rubrics_from_yaml(DEFAULT_RUBRICS_VERSION)
if _yaml_rubrics:
    RUBRIC_DATA = _yaml_rubrics

# Module file mappings
MODULE_FILES = {
    'm01': {
        'dataset': 'm01_extract_own_brand_entities.jsonl',
        'results': 'm01_results.jsonl',
        'rubrics': 'M01',
    },
    'm01a': {
        'dataset': 'm01a_extract_own_brand_variations.jsonl',
        'results': 'm01a_results.jsonl',
        'rubrics': 'M01a',
    },
    'm01b': {
        'dataset': 'm01b_extract_brand_related_terms.jsonl',
        'results': 'm01b_results.jsonl',
        'rubrics': 'M01b',
    },
    'm02': {
        'dataset': 'm02_classify_own_brand_keywords.jsonl',
        'results': 'm02_results.jsonl',
        'rubrics': 'M02',
    },
    'm03': {
        'dataset': 'm03_generate_competitor_entities.jsonl',
        'results': 'm03_results.jsonl',
        'rubrics': 'M03',
    },
    'm04': {
        'dataset': 'm04_classify_competitor_brand_keywords.jsonl',
        'results': 'm04_results.jsonl',
        'rubrics': 'M04',
    },
    'm05': {
        'dataset': 'm05_classify_nonbranded_keywords.jsonl',
        'results': 'm05_results.jsonl',
        'rubrics': 'M05',
    },
    'm06': {
        'dataset': 'm06_generate_product_type_taxonomy.jsonl',
        'results': 'm06_results.jsonl',
        'rubrics': 'M06',
    },
    'm07': {
        'dataset': 'm07_extract_product_attributes.jsonl',
        'results': 'm07_results.jsonl',
        'rubrics': 'M07',
    },
    'm08': {
        'dataset': 'm08_assign_attribute_ranks.jsonl',
        'results': 'm08_results.jsonl',
        'rubrics': 'M08',
    },
    'm09': {
        'dataset': 'm09_identify_primary_intended_use_v1.1.jsonl',
        'results': 'm09_results.jsonl',
        'rubrics': 'M09',
    },
    'm10': {
        'dataset': 'm10_validate_primary_intended_use_v1.1.jsonl',
        'results': 'm10_results.jsonl',
        'rubrics': 'M10',
    },
    'm11': {
        'dataset': 'm11_identify_hard_constraints_v1.1.jsonl',
        'results': 'm11_results.jsonl',
        'rubrics': 'M11',
    },
    'm12': {
        'dataset': 'm12_check_hard_constraint_v1.1.jsonl',
        'results': 'm12_results.jsonl',
        'rubrics': 'M12',
    },
    'm12b': {
        'dataset': 'm12b_combined_classification_v1.1.jsonl',
        'results': 'm12b_results.jsonl',
        'rubrics': 'M12b',
    },
    'm13': {
        'dataset': 'm13_check_product_type_v1.1.jsonl',
        'results': 'm13_results.jsonl',
        'rubrics': 'M13',
    },
    'm14': {
        'dataset': 'm14_check_primary_use_same_type_v1.1.jsonl',
        'results': 'm14_results.jsonl',
        'rubrics': 'M14',
    },
    'm15': {
        'dataset': 'm15_check_substitute_v1.1.jsonl',
        'results': 'm15_results.jsonl',
        'rubrics': 'M15',
    },
    'm16': {
        'dataset': 'm16_check_complementary_v1.1.jsonl',
        'results': 'm16_results.jsonl',
        'rubrics': 'M16',
    },
}


def load_jsonl(file_path: Path) -> list[dict]:
    """Load records from a JSONL file."""
    records = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def load_dataset(module: str) -> list[dict]:
    """Load dataset as ordered list (preserves all records including multiple keywords per ASIN)."""
    config = MODULE_FILES[module]
    file_path = DATASETS_DIR / config['dataset']
    records = load_jsonl(file_path)

    # Add record_id to each record for display purposes
    for i, r in enumerate(records):
        r['_record_id'] = r.get('id') or r.get('metadata', {}).get('asin', f'record_{i}')
        # For keyword-based datasets, include keyword in display
        if 'keyword' in r.get('input', {}):
            r['_record_id'] = f"{r['_record_id']}:{r['input']['keyword'][:20]}"

    return records


def load_results(module: str) -> dict[str, dict]:
    """Load batch results indexed by custom_id index."""
    config = MODULE_FILES[module]
    file_path = RESULTS_DIR / config['results']
    records = load_jsonl(file_path)

    # Index by custom_id index (e.g., m01_00000 -> 0)
    indexed = {}
    for r in records:
        custom_id = r.get('custom_id', '')
        # Extract index from custom_id (e.g., "m01_00000" -> 0)
        if '_' in custom_id:
            idx = int(custom_id.split('_')[1])
            # Parse the output JSON from the response
            content = r.get('response', {}).get('body', {}).get('choices', [{}])[0].get('message', {}).get('content', '{}')
            try:
                output = json.loads(content)
            except json.JSONDecodeError:
                output = {'error': 'Failed to parse output'}
            indexed[idx] = {
                'custom_id': custom_id,
                'output': output,
                'raw': r,
            }
    return indexed


def create_judge_prompt(rubric: dict, input_data: dict, expected: dict, module_output: dict) -> str:
    """Create the judge prompt for evaluation."""

    prompt = f"""You are an expert evaluator for LLM outputs. Your task is to evaluate whether the module output passes or fails the given rubric criterion.

## Rubric
**Criterion:** {rubric['criterion']}
**Check:** {rubric['check']}

**PASS conditions:**
{rubric['pass']}

**FAIL conditions:**
{rubric['fail']}

## Input Data
```json
{json.dumps(input_data, indent=2)}
```

## Module Output (to evaluate)
```json
{json.dumps(module_output, indent=2)}
```

## Expected Output (ground truth reference)
```json
{json.dumps(expected, indent=2)}
```

## Instructions
1. First, analyze the module output against the rubric criterion
2. Explain your reasoning step by step
3. Then provide your verdict: PASS or FAIL

Respond in this exact format:

**Reasoning:**
[Your step-by-step analysis here]

**Verdict:** [PASS or FAIL]
"""
    return prompt


def run_judge(
    client: OpenAI,
    rubric: dict,
    input_data: dict,
    expected: dict,
    module_output: dict,
    model: str = "gpt-4o-mini"
) -> dict:
    """Run the LLM judge for a single evaluation."""

    prompt = create_judge_prompt(rubric, input_data, expected, module_output)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert evaluator. Be precise and objective in your assessments."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=1000,
        )

        content = response.choices[0].message.content

        # Parse verdict from response
        verdict = "UNKNOWN"
        if "**Verdict:** PASS" in content or "**Verdict:**PASS" in content:
            verdict = "PASS"
        elif "**Verdict:** FAIL" in content or "**Verdict:**FAIL" in content:
            verdict = "FAIL"

        return {
            'rubric_id': rubric['id'],
            'criterion': rubric['criterion'],
            'verdict': verdict,
            'reasoning': content,
            'tokens_used': response.usage.total_tokens if response.usage else 0,
        }

    except Exception as e:
        return {
            'rubric_id': rubric['id'],
            'criterion': rubric['criterion'],
            'verdict': 'ERROR',
            'reasoning': str(e),
            'tokens_used': 0,
        }


def run_evaluation(
    module: str,
    rubric_id: Optional[str] = None,
    limit: int = 5,
    model: str = "gpt-4o-mini",
    rubrics_version: str = DEFAULT_RUBRICS_VERSION
) -> dict:
    """Run the full evaluation for a module."""

    print(f"\n{'='*60}")
    print(f"LLM-as-a-Judge Evaluation")
    print(f"{'='*60}")
    print(f"Module: {module.upper()}")
    print(f"Model: {model}")
    print(f"Rubrics: {rubrics_version}")
    print(f"Limit: {limit} samples")

    # Load data
    print("\nLoading data...")
    dataset = load_dataset(module)  # Returns list, not dict
    results = load_results(module)

    # Get rubrics
    config = MODULE_FILES[module]
    rubrics = RUBRIC_DATA.get(config['rubrics'], [])

    if rubric_id:
        rubrics = [r for r in rubrics if r['id'] == rubric_id]
        if not rubrics:
            print(f"ERROR: Rubric '{rubric_id}' not found")
            return {}

    print(f"Dataset records: {len(dataset)}")
    print(f"Result records: {len(results)}")
    print(f"Rubrics: {len(rubrics)}")

    # Initialize OpenAI client
    client = OpenAI()

    # Match dataset records with results by index (1:1 alignment)
    dataset_list = dataset[:limit]

    all_evaluations = []
    summary = {'pass': 0, 'fail': 0, 'error': 0}

    for idx, record in enumerate(dataset_list):
        # Get record ID (already computed in load_dataset)
        record_id = record.get('_record_id', f'sample_{idx}')
        print(f"\n--- Sample {idx + 1}/{len(dataset_list)}: {record_id} ---")

        # Get corresponding result
        result = results.get(idx, {})
        if not result:
            print(f"  No result found for index {idx}")
            continue

        module_output = result.get('output', {})

        for rubric in rubrics:
            print(f"  Evaluating: {rubric['criterion']}...", end=" ")

            eval_result = run_judge(
                client=client,
                rubric=rubric,
                input_data=record.get('input', {}),
                expected=record.get('expected', {}),
                module_output=module_output,
                model=model,
            )

            eval_result['sample_id'] = record_id
            eval_result['sample_idx'] = idx
            all_evaluations.append(eval_result)

            verdict = eval_result['verdict']
            print(verdict)

            if verdict == 'PASS':
                summary['pass'] += 1
            elif verdict == 'FAIL':
                summary['fail'] += 1
            else:
                summary['error'] += 1

    # Calculate metrics
    total = summary['pass'] + summary['fail']
    pass_rate = (summary['pass'] / total * 100) if total > 0 else 0

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Total evaluations: {len(all_evaluations)}")
    print(f"PASS: {summary['pass']}")
    print(f"FAIL: {summary['fail']}")
    print(f"ERROR: {summary['error']}")
    print(f"Pass Rate: {pass_rate:.1f}%")
    print(f"{'='*60}")

    # Save results
    output = {
        'module': module,
        'model': model,
        'rubrics_version': rubrics_version,
        'timestamp': datetime.now().isoformat(),
        'summary': summary,
        'pass_rate': pass_rate,
        'evaluations': all_evaluations,
    }

    output_dir = PROJECT_ROOT / "evaluation" / "judge_results"
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"{module}_judge_{timestamp}.json"

    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_file}")

    return output


def main():
    parser = argparse.ArgumentParser(description="LLM-as-a-Judge Evaluation")
    parser.add_argument("--module", "-m", type=str, default="m01",
                        choices=list(MODULE_FILES.keys()) + ["all"],
                        help="Module to evaluate (or 'all' for all modules)")
    parser.add_argument("--rubric", "-r", type=str, default=None,
                        help="Specific rubric ID to evaluate")
    parser.add_argument("--limit", "-l", type=int, default=5,
                        help="Number of samples to evaluate")
    parser.add_argument("--model", type=str, default="gpt-4o-mini",
                        help="Model to use for evaluation")
    parser.add_argument("--rubrics-version", "-v", type=str, default=DEFAULT_RUBRICS_VERSION,
                        help=f"Rubric version to use (default: {DEFAULT_RUBRICS_VERSION})")
    parser.add_argument("--list-rubrics", action="store_true",
                        help="List available rubrics for module")
    parser.add_argument("--list-versions", action="store_true",
                        help="List available rubric versions")

    args = parser.parse_args()

    # List available rubric versions
    if args.list_versions:
        versions = list_available_rubric_versions()
        print(f"\nAvailable rubric versions: {', '.join(versions)}")
        print(f"Default: {DEFAULT_RUBRICS_VERSION}")
        return

    # Load rubrics for specified version
    global RUBRIC_DATA
    loaded_rubrics = load_rubrics_from_yaml(args.rubrics_version)
    if loaded_rubrics:
        RUBRIC_DATA = loaded_rubrics

    # List rubrics for module
    if args.list_rubrics:
        config = MODULE_FILES.get(args.module)
        if config:
            rubrics = RUBRIC_DATA.get(config['rubrics'], [])
            print(f"\nRubrics for {args.module.upper()} (version {args.rubrics_version}):")
            for r in rubrics:
                print(f"  - {r['id']}: {r['criterion']}")
        return

    # Run all modules
    if args.module == "all":
        print(f"\n{'='*60}")
        print(f"RUNNING ALL MODULES (M01-M16)")
        print(f"Rubrics Version: {args.rubrics_version}")
        print(f"{'='*60}\n")

        all_results = {}
        for module in MODULE_FILES.keys():
            print(f"\n{'='*60}")
            print(f"MODULE: {module.upper()}")
            print(f"{'='*60}")
            try:
                result = run_evaluation(
                    module=module,
                    rubric_id=args.rubric,
                    limit=args.limit,
                    model=args.model,
                    rubrics_version=args.rubrics_version,
                )
                all_results[module] = result.get('pass_rate', 0)
            except Exception as e:
                print(f"ERROR: {e}")
                all_results[module] = -1

        # Print summary
        print(f"\n{'='*60}")
        print("ALL MODULES SUMMARY")
        print(f"{'='*60}")
        for module, rate in all_results.items():
            status = f"{rate:.1f}%" if rate >= 0 else "ERROR"
            print(f"  {module.upper()}: {status}")
        return

    # Run single module
    run_evaluation(
        module=args.module,
        rubric_id=args.rubric,
        limit=args.limit,
        model=args.model,
        rubrics_version=args.rubrics_version,
    )


if __name__ == "__main__":
    main()
