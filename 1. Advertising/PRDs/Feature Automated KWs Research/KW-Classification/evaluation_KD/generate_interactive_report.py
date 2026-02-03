#!/usr/bin/env python3
"""Generate interactive rubrics HTML report with embedded prompts."""

import os
import json
import html

# Prompt file mapping
PROMPT_FILES = {
    'M01': 'prompts/modules/m01_extract_own_brand_entities.md',
    'M01a': 'prompts/modules/m01a_extract_own_brand_variations.md',
    'M01b': 'prompts/modules/m01b_extract_brand_related_terms.md',
    'M02': 'prompts/modules/m02b_classify_own_brand_keywords.md',
    'M03': 'prompts/modules/m03_generate_competitor_entities.md',
    'M04': 'prompts/modules/m04b_classify_competitor_brand_keywords.md',
    'M05': 'prompts/modules/m05b_classify_nonbranded_keywords.md',
    'M06': 'prompts/modules/m06_v2_generate_product_type_taxonomy.md',
    'M07': 'prompts/modules/m07_extract_product_attributes.md',
    'M08': 'prompts/modules/m08_assign_attribute_ranks.md',
    'M09': 'prompts/modules/m09_identify_primary_intended_use_v1.1.md',
    'M10': 'prompts/modules/m10_validate_primary_intended_use_v1.1.md',
    'M11': 'prompts/modules/m11_identify_hard_constraints_v1.1.md',
    'M12': 'prompts/modules/m12b_combined_classification_v1.1.md',
    'M13': 'prompts/modules/m13_product_type_check_v1.1.md',
    'M14': 'prompts/modules/m14_primary_use_check_same_type_v1.1.md',
    'M15': 'prompts/modules/m15_substitute_check_v1.1.md',
    'M16': 'prompts/modules/m16_complementary_check_v1.1.md',
}

MODULE_DESCRIPTIONS = {
    'M01': 'Extract Own Brand Entities',
    'M01a': 'Generate Brand Variations',
    'M01b': 'Extract Brand Related Terms',
    'M02': 'Detect Brand in Keyword',
    'M03': 'Generate Competitor Entities',
    'M04': 'Classify Competitor Brand Keywords',
    'M05': 'Classify Non-Branded Keywords',
    'M06': 'Generate Product Type Taxonomy',
    'M07': 'Extract Product Attributes',
    'M08': 'Assign Attribute Ranks',
    'M09': 'Identify Primary Intended Use',
    'M10': 'Validate Primary Intended Use',
    'M11': 'Identify Hard Constraints',
    'M12': 'Combined Classification',
    'M13': 'Product Type Check',
    'M14': 'Primary Use Check (Same Type)',
    'M15': 'Substitute Check',
    'M16': 'Complementary Check',
}

RUBRIC_DATA = {
    'M01': [
        {'id': 'M01_brand_extracted', 'criterion': 'Brand Extracted', 'check': 'Brand extracted from title or listing_brand field', 'codeBased': False, 'fail': '- Empty output when title contains brand name\n- Empty output when listing_brand field has value', 'pass': '- brand_name matches brand found in title OR listing_brand field'},
        {'id': 'M01_no_hallucination', 'criterion': 'No Hallucination', 'check': 'Base brand must come from input; typos must be variations of that brand', 'codeBased': False, 'fail': '- Output contains a completely different brand not related to input (e.g., "Sony" when input brand is "JBL")\n- Brand name invented from scratch, not derived from input brand', 'pass': '- All base brands traceable to input data (e.g., brand_name, title, manufacturer)\n- Typos/variations are clearly derived from the input brand (e.g., "JLB", "jbl" from "JBL")'},
        {'id': 'M01_no_product_words', 'criterion': 'No Product Words', 'check': 'No generic product/feature words in brand output', 'codeBased': False, 'fail': '- Brand contains generic product words (e.g., Wireless, Bluetooth, Speaker, Headphones, Charger, etc.)\n- Product category used as brand name', 'pass': '- Output contains only actual brand/trademark names\n- No generic descriptors or product types'},
        {'id': 'M01_amazon_test_applied', 'criterion': 'Amazon Test Applied', 'check': 'Entity is a brand you search FOR, not a product you search TO BUY', 'codeBased': False, 'fail': '- Searching the entity on Amazon returns a product category, not a brand (e.g., "Wireless Earbuds" → shows earbuds listings, not a brand page)', 'pass': '- Searching the entity on Amazon returns brand-specific results (e.g., "JBL" → shows JBL brand page/products, "Sony" → shows Sony products)\n- The entity is something customers search FOR to find products, not something they search TO BUY directly'},
        {'id': 'M01_no_duplicates', 'criterion': 'No Duplicates', 'check': 'No exact duplicate strings in list', 'codeBased': False, 'fail': '- Exact same string appears more than once (e.g., "JBL", "JBL")', 'pass': '- Each string in list is unique\n- Case variations are different entries, not duplicates (e.g., "JBL" and "jbl" are both valid)'},
    ],
    'M01a': [
        {'id': 'M01a_has_variations', 'criterion': 'Has Variations', 'check': 'Multiple brand variations generated', 'codeBased': False, 'fail': '- Only 1 variation returned\n- Empty list', 'pass': '- Multiple variations generated'},
        {'id': 'M01a_no_unrelated_terms', 'criterion': 'No Unrelated Terms', 'check': 'All variations are misspellings/typos of the SAME brand only', 'codeBased': False, 'fail': '- Contains different brand names (e.g., "Sony" in JBL variations)\n- Contains product words (e.g., "Earbuds", "Speaker")\n- Contains sub-brand names (should be in M01b)', 'pass': '- All items are typos/case variations/misspellings of the input brand_name only'},
        {'id': 'M01a_count_in_range', 'criterion': '8-12 Count', 'check': 'Exactly 8-12 variations', 'codeBased': False, 'fail': '- Fewer than 8 variations\n- More than 12 variations', 'pass': '- Exactly 8-12 variations in the list'},
        {'id': 'M01a_first_is_canonical', 'criterion': 'First is Canonical', 'check': 'First variation matches input brand_name exactly', 'codeBased': False, 'fail': '- First item differs from input brand_name\n- First item has typos, spacing changes, or case changes', 'pass': '- variations[0] === brand_name (exact match)'},
    ],
    'M01b': [
        {'id': 'M01b_sub_brands_found', 'criterion': 'Sub-brands Found', 'check': 'Sub-brands, product lines, brand-owned tech extracted from listing', 'codeBased': False, 'fail': '- Sub-brand mentioned in title/bullets not captured\n- Product line name in listing not captured', 'pass': '- sub_brands array contains product families, series names, brand-owned tech mentioned in listing'},
        {'id': 'M01b_no_universal_standards', 'criterion': 'No Universal Standards', 'check': 'No universal/industry standards listed as brand-specific', 'codeBased': False, 'fail': '- Universal standards included as brand-specific (e.g., Bluetooth, USB-C, WiFi, HDMI, NFC, Qi, etc.)', 'pass': '- Only proprietary brand-owned terms included\n- No industry-wide standards or protocols'},
        {'id': 'M01b_manufacturer_null_when_same', 'criterion': 'Manufacturer Null When Same', 'check': 'Manufacturer=null when same as brand', 'codeBased': False, 'fail': '- Returned manufacturer when = brand_name', 'pass': '- Returns null when manufacturer matches brand'},
        {'id': 'M01b_searchable_standards_default_empty', 'criterion': 'Searchable Standards Empty', 'check': 'searchable_standards empty unless customers actively search for standard by name', 'codeBased': False, 'fail': '- Technical standards included (e.g., ENFit, USB-C, Bluetooth)\n- Standards customers don\'t search for by name', 'pass': '- Empty array (most products)\n- Only brand-like standards people search: Gore-Tex, Dolby Atmos, THX'},
    ],
    'M02': [
        {'id': 'M02_correct_classification', 'criterion': 'Correct Classification', 'check': 'OB when keyword contains brand from variations_own, null otherwise', 'codeBased': False, 'fail': '- OB returned but keyword has no match in variations_own or related_terms_own\n- null returned but keyword contains exact term from variations_own', 'pass': '- OB only when keyword contains term from variations_own/related_terms_own\n- null when no match found (passes to M03)'},
        {'id': 'M02_brand_match_found', 'criterion': 'Brand Match Found', 'check': 'Brand from variations_own detected in keyword when present', 'codeBased': False, 'fail': '- Missed brand that exists in variations_own input', 'pass': '- Brand correctly detected by matching against variations_own list'},
        {'id': 'M02_no_false_positives', 'criterion': 'No False Positives', 'check': 'No generic words flagged as brand', 'codeBased': False, 'fail': '- Generic words flagged as brand (e.g., "wireless", "bluetooth", "speaker")', 'pass': '- Only actual brand/trademark names matched'},
        {'id': 'M02_case_insensitive', 'criterion': 'Case Insensitive', 'check': 'Brand matching ignores uppercase/lowercase differences', 'codeBased': False, 'fail': '- Case difference caused missed match (e.g., "jbl" in keyword didn\'t match "JBL" in variations_own)', 'pass': '- Brand matched regardless of case (e.g., "jbl", "JBL", "Jbl" all match)'},
        {'id': 'M02_word_boundary_respected', 'criterion': 'Word Boundary Respected', 'check': 'Partial matches rejected (jbl ≠ jblue)', 'codeBased': False, 'fail': '- "jbl" incorrectly matched "jblue"\n- Substring match accepted', 'pass': '- Only whole word matches accepted'},
        {'id': 'M02_no_similar_brand_confusion', 'criterion': 'No Similar Brand Confusion', 'check': 'Similar-looking brands rejected (jlab ≠ JBL)', 'codeBased': False, 'fail': '- Confused similar-sounding brands\n- "jlab" matched as "JBL"', 'pass': '- Different brands correctly rejected'},
    ],
    'M03': [
        {'id': 'M03_competitors_relevant', 'criterion': 'Competitors Relevant', 'check': 'All competitors sell products in same category as ASIN', 'codeBased': False, 'fail': '- Brands from different product categories\n- Generic retailers included (e.g., Amazon, Walmart, Target)\n- Own brand included in competitors list', 'pass': '- All brands sell similar products to the ASIN\n- No unrelated brands or retailers'},
        {'id': 'M03_competitor_count', 'criterion': 'Competitor Count', 'check': '5-10 distinct competitor brands included', 'codeBased': False, 'fail': '- Fewer than 5 distinct brands\n- More than 10 distinct brands', 'pass': '- 5-10 unique competitor brand names'},
        {'id': 'M03_no_hallucinated_brands', 'criterion': 'No Hallucinated Brands', 'check': 'All competitor brands are verifiable real brands', 'codeBased': False, 'fail': '- Brand names that don\'t exist\n- Misspelled brand names presented as separate brands', 'pass': '- All brands can be found on Amazon/Google as real companies'},
    ],
    'M04': [
        {'id': 'M04_correct_classification', 'criterion': 'Correct Classification', 'check': 'CB when competitor brand in keyword, null otherwise', 'codeBased': False, 'fail': '- CB returned but no competitor brand in keyword\n- null returned but keyword contains competitor brand', 'pass': '- CB only when keyword contains term from competitors list\n- null when no match (passes to M05)'},
        {'id': 'M04_own_brand_excluded', 'criterion': 'Own Brand Excluded', 'check': 'Own brand terms never trigger CB classification', 'codeBased': False, 'fail': '- Own brand term classified as CB\n- Own brand variation matched as competitor', 'pass': '- Own brand terms return null, not CB'},
        {'id': 'M04_word_boundary_respected', 'criterion': 'Word Boundary Respected', 'check': 'Partial/substring matches rejected - only full words match', 'codeBased': False, 'fail': '- Substring incorrectly matched (e.g., "kitchen" to "KitchenAid", "good" to "Good Grips")', 'pass': '- Only complete word/phrase matches accepted\n- Generic words not confused with brands'},
        {'id': 'M04_known_brands_detected', 'criterion': 'Known Brands Detected', 'check': 'Recognizable brands caught even if not in competitors list', 'codeBased': False, 'fail': '- Known brand missed because not in provided list (e.g., Homwe, Beats, Iron Flask)', 'pass': '- Known brands detected using category knowledge\n- Brand recognized regardless of whether in competitors input'},
        {'id': 'M04_character_ip_recognized', 'criterion': 'Character/IP Recognized', 'check': 'Licensed character and franchise names detected as brands', 'codeBased': False, 'fail': '- Character/franchise keyword returned null (e.g., "batman action figure", "disney princess", "marvel toys")', 'pass': '- Licensed characters/franchises classified as CB (e.g., Batman, Disney, Marvel, Star Wars)'},
    ],
    'M05': [
        {'id': 'M05_correct_classification', 'criterion': 'Correct Classification', 'check': 'NB only when keyword has zero brand references', 'codeBased': False, 'fail': '- NB returned but keyword contains a brand\n- null returned for truly generic keyword', 'pass': '- NB only for pure generic keywords (e.g., "wireless bluetooth earbuds")\n- null when any brand detected'},
        {'id': 'M05_hidden_brands_detected', 'criterion': 'Hidden Brands Detected', 'check': 'Brands not in provided lists are still caught', 'codeBased': False, 'fail': '- Hidden brand missed (e.g., Beats, Echo, Iron Flask not in list but returned NB)', 'pass': '- Known brands caught regardless of whether in competitors list'},
        {'id': 'M05_typo_variations_caught', 'criterion': 'Typo Variations Caught', 'check': 'Spacing and typo variations recognized as brands', 'codeBased': False, 'fail': '- Brand typo/spacing missed (e.g., "camel back" not recognized as CamelBak, "hydro flask" not matched)', 'pass': '- Common typos and spacing variations detected as brands'},
        {'id': 'M05_product_lines_recognized', 'criterion': 'Product Lines Recognized', 'check': 'Trademarked product line names caught as brands', 'codeBased': False, 'fail': '- Product line returned NB (e.g., "airpods case", "quietcomfort headphones")', 'pass': '- Trademarked product lines classified as branded (e.g., AirPods, QuietComfort, Galaxy)'},
        {'id': 'M05_ppc_terms_filtered', 'criterion': 'PPC Terms Filtered', 'check': 'ASIN codes and PPC match-type terms return null', 'codeBased': False, 'fail': '- PPC meta-term returned NB (e.g., ASIN codes, "close-match", "loose-match")', 'pass': '- ASINs and PPC meta-terms return null (not valid product keywords)'},
    ],
    'M06': [
        {'id': 'M06_hierarchy_correct', 'criterion': 'Hierarchy Correct', 'check': 'Rank 1 = most specific type, higher ranks = broader categories', 'codeBased': False, 'fail': '- Rank 1 is broader than Rank 2 (e.g., "Earbuds" at Rank 1, "True Wireless Earbuds" at Rank 2)\n- General category before specific type', 'pass': '- Rank 1 is most specific: e.g., Rank 1: "Pencil Eyeliner" → Rank 2: "Eyeliner" → Rank 3: "Eye Makeup"\n- Each rank is a TRUE parent of the previous (test: "Is Rank 1 a TYPE OF Rank 2?")'},
        {'id': 'M06_product_type_accurate', 'criterion': 'Product Type Accurate', 'check': 'Rank 1 accurately describes what the product IS', 'codeBased': False, 'fail': '- Rank 1 doesn\'t match the actual product\n- Would confuse a shopper about what they\'re buying', 'pass': '- Rank 1 is what you\'d call this product in conversation'},
        {'id': 'M06_synonyms_merged', 'criterion': 'Synonyms Merged', 'check': 'Terms with same meaning merged on same rank with " / " separator', 'codeBased': False, 'fail': '- Synonyms on different ranks (e.g., "Stroller" at Rank 2, "Baby Stroller" at Rank 1 - these mean the same thing)\n- Translations not merged (e.g., "Soy Sauce" and "Kecap Manis" on separate ranks)', 'pass': '- Synonyms merged: e.g., "Pencil Eyeliner / Eyeliner Pencil" on same rank\n- Test: "Do both terms refer to the same product?" If yes → same rank with " / "'},
        {'id': 'M06_no_excluded_terms', 'criterion': 'No Excluded Terms', 'check': 'No adjectives, features, materials, colors, sizes in taxonomy ranks', 'codeBased': False, 'fail': '- Adjectives in rank (e.g., "Premium", "Best", "Waterproof")\n- Materials as separate rank (e.g., "Stainless Steel" as its own rank)\n- Features in rank (e.g., "Bluetooth", "Wireless", "LED")\n- Colors, sizes, audiences in rank (e.g., "Black", "32oz", "Men\'s")', 'pass': '- Only product type/category nouns in ranks\n- Materials/features excluded or combined with product type (e.g., "Stainless Steel Water Bottle" not "Stainless Steel" → "Water Bottle")'},
    ],
    'M07': [
        {'id': 'M07_attributes_from_listing', 'criterion': 'Attributes From Listing', 'check': 'Variants, use cases derived from title, bullets, description, or Keepa hints', 'codeBased': False, 'fail': '- Attribute not mentioned in any input field\n- Completely invented attributes', 'pass': '- Each attribute traceable to title, bullets, description, or Keepa data'},
        {'id': 'M07_no_fabricated_use_cases', 'criterion': 'No Fabricated Use Cases', 'check': 'Use cases supported by product\'s actual function', 'codeBased': False, 'fail': '- Use case physically impossible for this product\n- Use case contradicts product description', 'pass': '- Use cases match what product can actually do based on listing'},
        {'id': 'M07_audiences_explicit_or_dash', 'criterion': 'Audiences Explicit or Dash', 'check': 'Audiences from listing OR ["-"] when no specific audience mentioned', 'codeBased': False, 'fail': '- Generic terms like "Everyone", "Adults", "Users", "People"\n- Audiences not mentioned in listing', 'pass': '- ["-"] when listing doesn\'t specify audience\n- Specific audiences only when explicitly stated (e.g., "Men\'s", "For Nurses")'},
        {'id': 'M07_specs_preserve_units', 'criterion': 'Specs Preserve Units', 'check': 'Full specs with numbers and units preserved', 'codeBased': False, 'fail': '- Truncated specs, missing units\n- "32" instead of "32oz"', 'pass': '- Full specifications preserved (e.g., "32oz", "Bluetooth 5.2")'},
    ],
    'M08': [
        {'id': 'M08_important_ranked_high', 'criterion': 'Important Ranked High', 'check': 'Title attributes = rank 1-2, bullet attributes = rank 2-3, description = rank 3-4', 'codeBased': False, 'fail': '- Title attribute ranked 3 or lower\n- Generic attribute ranked above title attribute', 'pass': '- Title attributes = rank 1-2\n- First bullet attributes = rank 2-3\n- Description-only = rank 3-4'},
        {'id': 'M08_unique_ranks_per_type', 'criterion': 'Unique Ranks Per Type', 'check': 'Each attribute_type has unique sequential ranks (no duplicates)', 'codeBased': False, 'fail': '- Duplicate rank within same type (e.g., two Variants both with rank=2)\n- Gaps in sequence (e.g., Variants with ranks 1,2,4 - missing 3)\n- Non-sequential ordering (e.g., ranks 3,1,2 instead of 1,2,3)', 'pass': '- Each attribute_type has its own independent rank sequence starting at 1\n- No duplicate ranks within same type (e.g., Variants: 1,2,3 and UseCases: 1,2 - both start at 1, that\'s correct)\n- Sequential integers with no gaps'},
        {'id': 'M08_title_attributes_ranked_high', 'criterion': 'Title Attributes Ranked High', 'check': 'Attributes appearing in title get rank 1-2 within their type', 'codeBased': False, 'fail': '- Title attribute ranked 3 or lower', 'pass': '- Title attributes ranked 1-2 within their attribute_type'},
    ],
    'M09': [
        {'id': 'M09_captures_core_purpose', 'criterion': 'Captures Core Purpose', 'check': 'Answers: "What is the ONE thing this product does?"', 'codeBased': False, 'fail': '- Describes a feature, not core function\n- Lists multiple uses instead of single primary', 'pass': '- Describes core function (verb + object)\n- Passes test: "If product could only do ONE thing, what would it be?"'},
        {'id': 'M09_no_marketing_language', 'criterion': 'No Marketing Language', 'check': 'No adjectives, quality claims, or marketing words', 'codeBased': False, 'fail': '- Includes adjectives (e.g., "premium", "comfortable", "amazing")\n- Includes quality claims (e.g., "best", "enhanced")', 'pass': '- Simple verb+noun structure\n- No descriptive adjectives'},
        {'id': 'M09_word_count_3_to_6', 'criterion': 'Word Count 3-6', 'check': 'Exactly 3-6 words in primary_use', 'codeBased': False, 'fail': '- Fewer than 3 words\n- More than 6 words', 'pass': '- Exactly 3-6 words'},
        {'id': 'M09_no_brand_tech_names', 'criterion': 'No Brand/Tech Names', 'check': 'No brand names or technology specs in output', 'codeBased': False, 'fail': '- Contains brand (e.g., "JBL", "Nike")\n- Contains tech (e.g., "Bluetooth", "WiFi", "USB-C")', 'pass': '- Generic functional description only\n- No specific brands or technologies'},
    ],
    'M10': [
        {'id': 'M10_invalid_correctly_flagged', 'criterion': 'Invalid Correctly Flagged', 'check': 'Correctly flags: adjectives, tech names, wrong word count, marketing language', 'codeBased': False, 'fail': '- Missed adjective (e.g., "premium", "comfortable")\n- Missed tech name (e.g., "Bluetooth")\n- Missed word count violation\n- Missed marketing language', 'pass': '- All violations from M09 checklist flagged in issues_found array'},
        {'id': 'M10_fix_improves_output', 'criterion': 'Fix Improves Output', 'check': 'Corrected validated_use passes all M09 criteria', 'codeBased': False, 'fail': '- Fixed output still has adjectives/tech names\n- Fixed output wrong word count\n- Fix is worse than original', 'pass': '- validated_use: 3-6 words, no adjectives, no tech, describes core function'},
    ],
    'M11': [
        {'id': 'M11_only_true_constraints', 'criterion': 'Only True Constraints', 'check': 'Only attributes that make product PHYSICALLY UNABLE to function when removed', 'codeBased': False, 'fail': '- Quality levels marked hard (e.g., "Deep Bass", "500F rating")\n- Durability features marked hard (e.g., "Waterproof")\n- Convenience features marked hard', 'pass': '- Device compatibility (e.g., "iPhone 15 fit" for case)\n- Essential safety (e.g., "Heat Resistant" for oven mitt)'},
        {'id': 'M11_critical_not_missed', 'criterion': 'Critical Not Missed', 'check': 'Device compatibility and essential safety constraints not missed', 'codeBased': False, 'fail': '- Phone case missing device fit constraint\n- Oven mitt missing heat resistance constraint', 'pass': '- Device-specific fit captured for accessories\n- Essential safety properties captured'},
        {'id': 'M11_never_categories_excluded', 'criterion': 'NEVER Categories Excluded', 'check': 'No tech versions, durability, performance specs marked as hard', 'codeBased': False, 'fail': '- Tech versions marked hard (e.g., Bluetooth 5.2, WiFi 6, USB 3.0)\n- Durability features marked hard (e.g., Waterproof, Rustproof)\n- Performance specs marked hard (e.g., 32hr battery, 26lbs/day)', 'pass': '- NEVER categories excluded from hard constraints'},
        {'id': 'M11_expected_distribution', 'criterion': 'Expected Distribution', 'check': 'Most products have 0 hard constraints, accessories may have 1', 'codeBased': False, 'fail': '- Standalone products with 2+ hard constraints (e.g., earbuds, water bottles, trays shouldn\'t have multiple)\n- Generic products with any hard constraints when none are truly required for function', 'pass': '- 0 constraints for standalone products (e.g., earbuds, bottles, trays, makeup, toys, jackets)\n- 1 constraint for compatibility-dependent accessories (e.g., phone cases need device fit, cables need connector type, oven mitts need heat rating)'},
        {'id': 'M11_three_step_test_applied', 'criterion': '3-Step Test Applied', 'check': 'All 3 tests applied: (1) Complete Removal, (2) Mechanism vs Quality, (3) Validated Use Alignment', 'codeBased': False, 'fail': '- Step 1 missing: No analysis of "would product still work if attribute completely removed?"\n- Step 2 missing: No distinction between mechanism (how it works) vs quality (how well it works)\n- Step 3 missing: No check if validated_use specifically requires this attribute', 'pass': '- Step 1 shown: "If [attribute] removed entirely, does product still function?" (e.g., earbuds without Bluetooth = non-functional)\n- Step 2 shown: "Is this HOW it works (mechanism) or HOW WELL (quality)?" (e.g., "Deep Bass" = quality, "Bluetooth" = mechanism)\n- Step 3 shown: "Does validated_use require this specific attribute?" (e.g., "portable audio" doesn\'t require specific Bluetooth version)'},
    ],
    'M12': [
        {'id': 'M12_correct_classification', 'criterion': 'Correct Classification', 'check': 'Classification follows decision tree: Hard Constraint → Product Type → Primary Use → Complementary', 'codeBased': False, 'fail': '- R assigned but hard constraint violated (should be N)\n- N assigned but keyword describes same primary use as product (should be S)\n- N assigned but keyword product is commonly used together with ASIN (should be C)', 'pass': '- R (Relevant): Keyword asks for same product type AND serves same primary use (e.g., "wireless earbuds" for wireless earbuds product)\n- S (Substitute): Different product type but same primary use - buyer could choose either (e.g., "headphones" for earbuds - both for personal audio)\n- C (Complementary): Different type, different use, but commonly purchased/used together (e.g., "earbuds case" for earbuds)\n- N (Negative): None of above - unrelated product OR hard constraint violated (e.g., "iPhone case" for earbuds)'},
        {'id': 'M12_decision_path_followed', 'criterion': 'Decision Path Followed', 'check': 'Steps followed in order: (1) Hard constraint → (2) Product type → (3a/3b) Use check → (4) Complementary', 'codeBased': False, 'fail': '- Jumped to classification without checking hard constraints first\n- Skipped product type check', 'pass': '- Reasoning shows each step evaluated in order\n- Early termination only at valid exit points'},
    ],
    'M13': [
        {'id': 'M13_same_type_correct', 'criterion': 'Same Type Correct', 'check': 'Correctly identifies if keyword asks for same base product type as ASIN taxonomy', 'codeBased': False, 'fail': '- Said "different type" but keyword is synonym or variation (e.g., earphones vs earbuds are SAME type)\n- Said "same type" but fundamentally different product (e.g., earbuds vs speakers are DIFFERENT types)', 'pass': '- YES (same type) when: keyword product would be shelved in same store section as ASIN (e.g., "bluetooth earphones" for earbuds product - both in earbuds section)\n- NO (different type) when: keyword product belongs in different store section (e.g., "speaker" for earbuds - speaker section vs earbuds section)'},
        {'id': 'M13_modifiers_stripped', 'criterion': 'Modifiers Stripped', 'check': 'Core product noun extracted, modifiers ignored', 'codeBased': False, 'fail': '- Adjectives caused "different type" decision (e.g., "hiking water bottle" marked different from "water bottle")\n- Material differences caused "different type" (e.g., "stainless steel tumbler" vs "plastic tumbler" marked as different types)', 'pass': '- Comparison based only on the BASE PRODUCT NOUN, ignoring all modifiers\n- These modifier types are stripped before comparison: material (e.g., stainless steel, plastic), use-case (e.g., hiking, office), brand (e.g., Nike, Yeti), color (e.g., black, blue), size (e.g., large, 32oz)\n- Example: "large stainless steel hiking water bottle" → compares as "water bottle"'},
        {'id': 'M13_synonyms_recognized', 'criterion': 'Synonyms Recognized', 'check': 'Common synonyms recognized as same type', 'codeBased': False, 'fail': '- Marked synonyms as different types (e.g., earphones≠earbuds, ice machine≠ice maker)', 'pass': '- Synonyms correctly recognized as same product type'},
    ],
    'M14': [
        {'id': 'M14_same_use_correct', 'criterion': 'Same Use Correct', 'check': 'Keyword\'s implied use matches ASIN\'s validated_use', 'codeBased': False, 'fail': '- Said "different use" but both products solve the same problem (e.g., paper tray vs bamboo tray - both for serving food)\n- Said "same use" but products solve different problems (e.g., bed pillow for sleeping vs throw pillow for decoration)', 'pass': '- YES (same use): Ask "what problem does each solve?" - if same answer, it\'s same use (e.g., "wireless earbuds" and "bluetooth earphones" both solve "personal audio listening")\n- NO (different use): Products solve fundamentally different problems (e.g., "gaming headset" solves "gaming communication" vs "earbuds" solves "portable music listening")'},
        {'id': 'M14_superficial_differences_ignored', 'criterion': 'Superficial Differences Ignored', 'check': 'Material/form/character/brand differences don\'t change primary use classification', 'codeBased': False, 'fail': '- Superficial differences treated as different use (e.g., paper tray vs bamboo tray, liquid eyeliner vs pencil eyeliner, Bumblebee vs Optimus Prime toy)', 'pass': '- Same primary use recognized despite material/form/character differences'},
    ],
    'M15': [
        {'id': 'M15_substitute_correct', 'criterion': 'Substitute Correct', 'check': 'Different product type that satisfies same customer need = Substitute', 'codeBased': False, 'fail': '- Marked N but customer could reasonably buy either for same need (e.g., tumbler vs bottle - both solve "carry drinks on the go")\n- Marked S but products serve different needs (e.g., coffee mug for desk use vs water bottle for portable use)', 'pass': '- S when: Different product types BUT customer shopping for one could reasonably choose the other\n- Test: "If I need [core need], would I consider both products?" If yes → S\n- Examples of S: water bottle↔tumbler (portable hydration), earbuds↔wired headphones (personal audio), puffer jacket↔winter coat (cold weather warmth)\n- NOT S when: Different contexts even if similar category (e.g., desk mug vs travel bottle)'},
        {'id': 'M15_sixty_percent_overlap', 'criterion': '60% Overlap Rule', 'check': 'Near-substitutes with significant use overlap classified as S', 'codeBased': False, 'fail': '- Too strict on near-substitutes: marked N when products share ≥60% of use cases (e.g., travel mug vs water bottle, bone conduction vs earbuds)', 'pass': '- Apply 60% test: "What % of use cases would BOTH products satisfy?"\n- ≥60% overlap → classify as S (Substitute)\n- Examples: travel mug↔water bottle (80% overlap - both portable, differ on hot drinks focus) → S\n- Examples: bone conduction↔earbuds (70% overlap - both personal audio, differ on ear coverage) → S\n- <60% overlap → pass to M16 for complementary check'},
    ],
    'M16': [
        {'id': 'M16_complementary_correct', 'criterion': 'Complementary Correct', 'check': 'One product maintains, stores, displays, or enhances the other = C', 'codeBased': False, 'fail': '- C assigned but products have no direct usage relationship (just same category)\n- N assigned but one product clearly supports/maintains the other (e.g., case for earbuds should be C)', 'pass': '- C when keyword product DIRECTLY supports the ASIN in one of these ways:\n  • Maintenance: cleans/cares for it (e.g., cleaning brush for bottle, lens wipes for glasses)\n  • Storage: holds/protects it (e.g., case for earbuds, sleeve for laptop)\n  • Display: shows/presents it (e.g., stand for watch, holder for phone)\n  • Accessory: attaches to/works with it (e.g., ear tips for earbuds, strap for bottle)\n  • Workflow: used in same task sequence (e.g., pillowcase for pillow, lid for container)'},
        {'id': 'M16_amazon_bundle_test', 'criterion': 'Amazon Bundle Test', 'check': '"Would Amazon show these as Frequently Bought Together?"', 'codeBased': False, 'fail': '- C for products Amazon wouldn\'t bundle\n- Products only share category, not actual usage', 'pass': '- Products commonly purchased together\n- One directly supports/maintains the other'},
        {'id': 'M16_same_category_not_complementary', 'criterion': 'Same Category != Complementary', 'check': 'Products in same category but different functions are NOT complementary', 'codeBased': False, 'fail': '- Same category marked as complementary (e.g., ice maker + sorbet maker, eyeliner + setting powder, puffer jacket + thermal socks)', 'pass': '- Same-category different-function correctly classified as N'},
        {'id': 'M16_relationship_type_identified', 'criterion': 'Relationship Type Identified', 'check': 'For C classification: Maintenance/Storage/Display/Accessory/Workflow/Same-Occasion specified', 'codeBased': False, 'fail': '- No relationship_type for C classification\n- relationship_type is vague or wrong', 'pass': '- Specific relationship type identified from: Maintenance, Storage, Display, Accessory, Workflow, Same-Occasion, Organization'},
    ],
}

def read_prompt(filepath):
    """Read prompt file content."""
    if not filepath or not os.path.exists(filepath):
        return None
    with open(filepath, 'r') as f:
        return f.read()

def escape_js_string(s):
    """Escape string for JavaScript."""
    if not s:
        return ''
    return s.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')

def generate_html():
    """Generate the interactive HTML report."""

    # Read all prompts
    prompts = {}
    for module_id, filepath in PROMPT_FILES.items():
        if filepath:
            content = read_prompt(filepath)
            if content:
                prompts[module_id] = escape_js_string(content)
            else:
                prompts[module_id] = f'Prompt file not found: {filepath}'
        else:
            prompts[module_id] = 'This module uses dynamic prompt generation or is located in experiment_results.'

    # Generate module list HTML
    modules_html = ''
    for module_id in ['M01', 'M01a', 'M01b', 'M02', 'M03', 'M04', 'M05', 'M06', 'M07', 'M08', 'M09', 'M10', 'M11', 'M12', 'M13', 'M14', 'M15', 'M16']:
        rubrics = RUBRIC_DATA.get(module_id, [])
        desc = MODULE_DESCRIPTIONS.get(module_id, '')

        rubrics_html = ''
        for r in rubrics:
            code_class = ' code-based' if r['codeBased'] else ''
            rubrics_html += f'''<div class="rubric-item{code_class}"><span class="rubric-id">{r['id']}</span><span class="rubric-check">→ {r['check']}</span></div>\n'''

        modules_html += f'''
            <div class="module" data-module="{module_id}">
                <div class="module-header">
                    <div class="module-arrow"></div>
                    <span class="module-name" onclick="openSplitView('{module_id}', event)">{module_id}</span>
                    <span class="module-title">{desc}</span>
                    <span class="module-count">{len(rubrics)}</span>
                </div>
                <div class="rubrics-list">
                    {rubrics_html}
                </div>
            </div>
'''

    # Generate prompts JS object
    prompts_js = 'const modulePrompts = {\n'
    for module_id, content in prompts.items():
        prompts_js += f'    "{module_id}": `{content}`,\n'
    prompts_js += '};\n'

    # Generate rubrics JS object
    rubrics_js = json.dumps(RUBRIC_DATA, indent=2)

    # Generate descriptions JS object
    descriptions_js = json.dumps(MODULE_DESCRIPTIONS, indent=2)

    html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KW Classification - Interactive Rubrics</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8f9fa; color: #333; }}
        .header {{ background: #fff; padding: 15px 20px; border-bottom: 1px solid #e0e0e0; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
        .header h1 {{ font-size: 18px; color: #1a1a1a; }}
        .header .stats {{ font-size: 13px; color: #666; }}
        .main {{ display: flex; height: calc(100vh - 52px); }}
        .sidebar {{ width: 320px; background: #fff; border-right: 1px solid #e0e0e0; overflow-y: auto; flex-shrink: 0; }}
        .sidebar.split-mode {{ width: 260px; }}
        .module {{ border-bottom: 1px solid #e8e8e8; }}
        .module-header {{ padding: 12px 15px; cursor: pointer; display: flex; align-items: center; gap: 10px; transition: background 0.2s; }}
        .module-header:hover {{ background: #f5f5f5; }}
        .module-header.active {{ background: #e3f2fd; }}
        .module-arrow {{ width: 0; height: 0; border-left: 5px solid transparent; border-right: 5px solid transparent; border-top: 6px solid #999; transition: transform 0.2s; }}
        .module.open .module-arrow {{ transform: rotate(180deg); }}
        .module-name {{ font-weight: 600; color: #1976d2; cursor: pointer; padding: 2px 6px; border-radius: 3px; }}
        .module-name:hover {{ background: #e3f2fd; }}
        .module-title {{ color: #555; font-size: 13px; flex: 1; }}
        .module-count {{ background: #e8e8e8; padding: 2px 8px; border-radius: 10px; font-size: 11px; color: #666; }}
        .rubrics-list {{ display: none; background: #fafafa; padding: 5px 0; }}
        .module.open .rubrics-list {{ display: block; }}
        .rubric-item {{ padding: 8px 15px 8px 35px; font-size: 12px; border-left: 2px solid transparent; }}
        .rubric-item:hover {{ background: #f0f0f0; }}
        .rubric-id {{ color: #00796b; font-family: monospace; }}
        .rubric-check {{ color: #0277bd; margin-left: 8px; }}
        .rubric-item.code-based .rubric-id::after {{ content: "CODE"; background: #fff3e0; color: #e65100; padding: 1px 4px; border-radius: 3px; font-size: 9px; margin-left: 6px; }}
        .split-container {{ display: none; flex: 1; }}
        .split-container.active {{ display: flex; }}
        .prompt-panel {{ flex: 0.42; background: #fff; border-right: 1px solid #e0e0e0; overflow-y: auto; padding: 20px; }}
        .prompt-panel h2 {{ color: #1976d2; margin-bottom: 15px; font-size: 16px; position: sticky; top: 0; background: #fff; padding: 10px 0; border-bottom: 1px solid #e8e8e8; }}
        .prompt-content {{ font-family: 'Monaco', 'Menlo', 'Consolas', monospace; font-size: 12px; line-height: 1.6; white-space: pre-wrap; color: #333; }}
        .rubric-panel {{ flex: 0.58; background: #f8f9fa; overflow-y: auto; padding: 20px; }}
        .rubric-panel h2 {{ color: #00796b; margin-bottom: 15px; font-size: 16px; position: sticky; top: 0; background: #f8f9fa; padding: 10px 0; border-bottom: 1px solid #e8e8e8; }}
        .rubric-card {{ background: #fff; border-radius: 6px; padding: 15px; margin-bottom: 12px; border-left: 3px solid #00796b; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
        .rubric-card.code-based {{ border-left-color: #e65100; }}
        .rubric-card-header {{ display: flex; justify-content: space-between; margin-bottom: 10px; }}
        .rubric-card-id {{ font-family: monospace; color: #00796b; font-size: 13px; }}
        .rubric-card-badge {{ background: #fff3e0; color: #e65100; padding: 2px 8px; border-radius: 3px; font-size: 10px; }}
        .rubric-card-criterion {{ color: #1a1a1a; font-weight: 600; margin-bottom: 8px; }}
        .rubric-card-check {{ color: #0277bd; font-size: 13px; margin-bottom: 12px; padding: 8px; background: #f5f5f5; border-radius: 4px; }}
        .rubric-card-section {{ margin-bottom: 10px; }}
        .rubric-card-label {{ color: #7b1fa2; font-size: 11px; text-transform: uppercase; margin-bottom: 4px; font-weight: 600; }}
        .rubric-card-label.pass {{ color: #2e7d32; }}
        .rubric-card-label.fail {{ color: #c62828; }}
        .rubric-card-content {{ font-size: 12px; color: #444; white-space: pre-wrap; background: #fafafa; padding: 8px; border-radius: 4px; border: 1px solid #e8e8e8; }}
        .close-split {{ position: fixed; top: 60px; right: 15px; background: #e0e0e0; border: none; color: #333; padding: 5px 12px; border-radius: 4px; cursor: pointer; z-index: 100; }}
        .close-split:hover {{ background: #d0d0d0; }}
        .welcome {{ flex: 1; display: flex; align-items: center; justify-content: center; color: #888; flex-direction: column; gap: 10px; }}
        .welcome.hidden {{ display: none; }}
        .welcome-icon {{ font-size: 48px; opacity: 0.3; }}
        ::-webkit-scrollbar {{ width: 10px; }}
        ::-webkit-scrollbar-track {{ background: #f0f0f0; }}
        ::-webkit-scrollbar-thumb {{ background: #c0c0c0; border-radius: 5px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: #a0a0a0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>KW Classification - Interactive Rubrics v2.2</h1>
        <div class="stats">67 rubrics across 18 modules | Click module name to view prompt + rubrics</div>
    </div>
    <div class="main">
        <div class="sidebar" id="sidebar">
            {modules_html}
        </div>
        <div class="welcome" id="welcome">
            <div class="welcome-icon">&#128203;</div>
            <div>Click on a module name (e.g., <strong style="color:#4fc1ff">M01</strong>) to view prompt + rubrics side by side</div>
            <div style="font-size: 12px;">Or click the arrow to expand/collapse rubric list</div>
        </div>
        <div class="split-container" id="splitContainer">
            <button class="close-split" onclick="closeSplitView()">&#10005; Close</button>
            <div class="prompt-panel" id="promptPanel">
                <h2 id="promptTitle">Prompt</h2>
                <div class="prompt-content" id="promptContent">Loading...</div>
            </div>
            <div class="rubric-panel" id="rubricPanel">
                <h2 id="rubricTitle">Rubrics</h2>
                <div id="rubricContent"></div>
            </div>
        </div>
    </div>
    <script>
        document.querySelectorAll('.module-header').forEach(header => {{
            header.addEventListener('click', (e) => {{
                if (e.target.classList.contains('module-name')) return;
                header.parentElement.classList.toggle('open');
            }});
        }});

        {prompts_js}
        const rubricData = {rubrics_js};
        const moduleDescriptions = {descriptions_js};

        function openSplitView(moduleId, event) {{
            event.stopPropagation();
            document.getElementById('welcome').classList.add('hidden');
            document.getElementById('splitContainer').classList.add('active');
            document.getElementById('sidebar').classList.add('split-mode');
            document.querySelectorAll('.module-header').forEach(h => h.classList.remove('active'));
            document.querySelector('[data-module="' + moduleId + '"] .module-header').classList.add('active');
            document.getElementById('promptTitle').textContent = moduleId + ': ' + moduleDescriptions[moduleId];
            document.getElementById('promptContent').textContent = modulePrompts[moduleId] || 'Prompt not available';
            const rubrics = rubricData[moduleId] || [];
            document.getElementById('rubricTitle').textContent = 'Rubrics (' + rubrics.length + ')';
            let html = '';
            rubrics.forEach(r => {{
                html += '<div class="rubric-card ' + (r.codeBased ? 'code-based' : '') + '">' +
                    '<div class="rubric-card-header"><span class="rubric-card-id">' + r.id + '</span>' +
                    (r.codeBased ? '<span class="rubric-card-badge">CODE-BASED</span>' : '') + '</div>' +
                    '<div class="rubric-card-criterion">' + r.criterion + '</div>' +
                    '<div class="rubric-card-check">Check: ' + r.check + '</div>' +
                    '<div class="rubric-card-section"><div class="rubric-card-label fail">FAIL when:</div>' +
                    '<div class="rubric-card-content">' + r.fail + '</div></div>' +
                    '<div class="rubric-card-section"><div class="rubric-card-label pass">PASS when:</div>' +
                    '<div class="rubric-card-content">' + r.pass + '</div></div></div>';
            }});
            document.getElementById('rubricContent').innerHTML = html;
        }}

        function closeSplitView() {{
            document.getElementById('welcome').classList.remove('hidden');
            document.getElementById('splitContainer').classList.remove('active');
            document.getElementById('sidebar').classList.remove('split-mode');
            document.querySelectorAll('.module-header').forEach(h => h.classList.remove('active'));
        }}
    </script>
</body>
</html>'''

    return html_template

if __name__ == '__main__':
    os.chdir('/Users/katerynadavidenko/AI-Projects/KW-Classification')
    html_content = generate_html()
    output_path = 'evaluation/interactive_rubrics.html'
    with open(output_path, 'w') as f:
        f.write(html_content)
    print(f'Generated {output_path}')
