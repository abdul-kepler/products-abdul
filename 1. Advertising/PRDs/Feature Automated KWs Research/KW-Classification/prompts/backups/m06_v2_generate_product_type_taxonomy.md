# Product Taxonomy Classification Prompt

## Overview
This prompt classifies products into hierarchical taxonomy using a three-phase approach:
1. **Phase 1:** Analyze product information → Build logical hierarchy
2. **Phase 2:** Validate, Add, Tweak & Update using search terms
3. **Phase 3:** Apply rules → Final refinement

---

## Prompt

```
You are a Product Taxonomy Classifier. Your task is to create an accurate hierarchical product type taxonomy using a three-phase approach.

## INPUTS

**Product Information:**
- Title: {{title}}
- Bullet Points: {{bullet_points}}
- Description: {{description}}
- Product Type: {{product_type}}
- Category Root: {{category_root}}
- Category Sub: {{category_sub}}

**Search Terms:**
{{search_terms}}

---

## PHASE 1: ANALYZE PRODUCT INFORMATION (Build Logical Hierarchy)

### Step 1.1: Identify the Core Product Type
- Read the title, bullet points, description carefully
- Determine: What exactly IS this product?
- This becomes your Rank 1 (most specific product type)

### Step 1.2: Build Logical Hierarchy Upward
Starting from the core product type, ask repeatedly:
> "What is [Current Product Type] a type of?"

Build the hierarchy from specific to broad:
- Rank 1: [Most Specific - the actual product]
- Rank 2: [What is Rank 1 a type of?]
- Rank 3: [What is Rank 2 a type of?]
- Continue until you reach a logical stopping point

### Step 1.3: Extract ONLY Product Types
When building hierarchy, include ONLY product type/category terms.

**EXCLUDE all of the following:**
- Adjectives (waterproof, portable, premium, best, lightweight)
- Features (Bluetooth, rechargeable, LED, 32GB, wireless)
- Benefits (comfortable, durable, easy-to-use)
- Colors (black, red, blue, pink)
- Size/Variants (large, small, 32oz, pack of 2, XL)
- Use Cases (for travel, for running, for camping, for kids)
- Audience (men's, women's, kids', for beginners, professional)
- Materials (silicone, leather, stainless steel, plastic, wood)
- Brand Names (Nike, Apple, Samsung)
- Qualifiers (best, cheap, top rated, affordable, new, latest)
- Year/Model (2024, v2, gen 3)

### Step 1.4: Output of Phase 1
Document your initial logical hierarchy:
```
Initial Hierarchy (from Product Info):
- Rank 1: [specific product type]
- Rank 2: [broader category]
- Rank 3: [even broader category]
- Rank 4: [broadest category if applicable]
```

---

## PHASE 2: VALIDATE, ADD, TWEAK & UPDATE USING SEARCH TERMS

Phase 2 is NOT just validation - it actively improves the hierarchy by:
- Validating existing levels
- ADDING missing levels found in search terms
- TWEAKING terminology to match buyer language
- UPDATING hierarchy if gaps or better terms are found
- MERGING synonyms/translations into same rank

### Step 2.1: Extract ALL Product Types from Search Terms
- Scan ALL search terms thoroughly
- Extract every product type term (exclude adjectives, features, colors, etc.)
- List all unique product types found
- Note: These are what buyers ACTUALLY search for

### Step 2.2: Validate Each Hierarchy Level
For each rank in your Phase 1 hierarchy, check if it appears in search terms:

| Result | Action |
|--------|--------|
| **Exact match found** | Keep this rank as-is |
| **Synonym/translation found** | MERGE into same rank with " / " separator |
| **Better term found** | Replace with search term version |
| **Not found at all** | Flag for Phase 3 review |

### Step 2.3: ADD Missing Levels from Search Terms
**CRITICAL:** Check if search terms contain product types that should be in your hierarchy but are missing.

Example scenarios:
- Your hierarchy: Baby Stroller → [gap] → ?
- Search terms contain: "baby products", "baby essentials"
- Action: ADD "Baby Products" as a broader level if it passes Phase 3 rules

Another example:
- Your hierarchy: Pencil Eyeliner → Eyeliner → Eye Makeup
- Search terms also contain: "eye cosmetics"
- Action: Consider if "Eye Cosmetics" should merge with "Eye Makeup" as synonym

### Step 2.4: MERGE Synonyms, Translations & Same-Meaning Terms
**IMPORTANT RULE:** Terms that mean the SAME thing (actual or implied) must be on the SAME rank, separated by " / "

**What counts as same meaning:**
- Synonyms: "Cell Phone / Mobile Phone"
- Translations: "Soy Sauce / Kecap Manis"
- Implied same meaning: "Stroller / Baby Stroller" (stroller implies baby stroller)
- Regional variations: "Flashlight / Torch"
- Alternate names: "Couch / Sofa"
- Common abbreviations: "Television / TV"

**How to format:**
```
Rank 1: "Pencil Eyeliner / Eyeliner Pencil"  (same product, different word order)
Rank 2: "Soy Sauce / Kecap Manis"  (product + translation)
Rank 1: "Cell Phone / Mobile Phone / Smartphone"  (synonyms)
```

**TEST:** If Term A and Term B refer to the same product/category and one doesn't contain the other as a subset, they belong on the SAME rank.

### Step 2.5: Check Hierarchy is TRUE Hierarchy (Not Synonyms)
**CRITICAL CHECK:** Before finalizing ranks, verify each level is a TRUE parent-child relationship, NOT synonyms.

**TRUE Hierarchy (different ranks):**
- Pencil Eyeliner → Eyeliner → Eye Makeup
  - Pencil Eyeliner IS A TYPE OF Eyeliner ✓
  - Eyeliner IS A TYPE OF Eye Makeup ✓

**NOT TRUE Hierarchy (should be SAME rank):**
- Baby Stroller → Stroller ✗ WRONG
  - "Stroller" and "Baby Stroller" mean the same thing
  - Should be: "Stroller / Baby Stroller" on ONE rank

**The Test:** Ask "Is [Rank 1] a TYPE OF [Rank 2], where [Rank 2] includes OTHER types too?"
- Is Pencil Eyeliner a type of Eyeliner? YES (there's also liquid eyeliner, gel eyeliner) ✓
- Is Baby Stroller a type of Stroller? NO (all strollers are baby strollers) → SAME RANK

### Step 2.6: Output of Phase 2
Document your updated hierarchy:
```
Updated Hierarchy (after Search Term analysis):
- Rank 1: [confirmed / merged synonyms with " / "]
- Rank 2: [confirmed / added / merged / removed]
- Rank 3: [confirmed / added / merged / removed]
- Rank 4: [confirmed / added / removed]

Changes Made:
- Merged "X" and "Y" into Rank 1 (synonyms)
- Added "Z" as Rank 3 (found in search terms, fits hierarchy)
- Replaced "A" with "B" (buyer's language)
- Removed "C" (not in search terms, flagged for Phase 3)
```

---

## PHASE 3: APPLY RULES (Final Refinement)

### Rule 1: Strict Subset Hierarchy
Each rank must be a PROPER SUBSET of the next rank (true parent-child).
- Rank 1 ⊂ Rank 2 ⊂ Rank 3 ⊂ Rank 4
- If terms are synonyms (same meaning), they go on SAME rank with " / "
- If any rank breaks this rule, merge or reorder

### Rule 2: Two-Question Test
For each rank (starting from Rank 2), apply BOTH questions:

| Question | What It Means |
|----------|---------------|
| **Q1: Search Intent** | Can someone looking to BUY this specific product search this broader category? |
| **Q2: Discovery Intent** | Can someone EXPLORING this broader category end up buying this specific product? |

- **Both YES** → Keep this rank
- **Either NO** → Remove this rank

**Critical Examples:**
- Vacuum Cleaner → Appliances: **FAIL Q1 & Q2** (no one searches "appliances" for vacuum)
- Pencil Eyeliner → Eyeliner → Eye Makeup: **PASS** (people search "eye makeup" and can buy eyeliner)
- Syringe Adapter → Adapter: **FAIL Q2** (someone exploring "adapters" won't find medical syringes)
- Pizza → Italian Food → Food: **PASS** (people exploring "food" or "Italian food" can buy pizza)

### Rule 3: No Artificial Intermediate Categories
Don't keep categories that aren't naturally searched.
- **BAD:** Dog Leash → Dog Walking Supplies → Dog Supplies
- **GOOD:** Dog Leash → Dog Supplies
- **Test:** Would someone actually type this into a search bar?

### Rule 4: No Vague Umbrella Terms
Remove terms like "Gear," "Stuff," "Items," "Things," "Products," "Accessories" UNLESS:
- They appear in search terms, AND
- They pass the Two-Question Test

### Rule 5: Search Terms Override Assumptions
If your logical hierarchy term was NOT found in search terms AND fails the Two-Question Test:
- **Remove it** - The hierarchy should not go this deep
- **Do not invent categories** that neither appear in search terms nor pass the Two-Question Test

### Rule 6: Single Level is Valid
If no broader category passes both the search term validation AND the Two-Question Test, the product has a single-level taxonomy. This is correct - do not force additional levels.

Examples of valid single-level products:
- Water Bottle (Drinkware fails Q2)
- Refrigerator (Appliances fails Q1 & Q2)
- Microwave (Kitchen Appliances fails Q1 & Q2)

### Rule 7: Use Buyer's Language
Always use terminology from search terms over assumed terms.
- Example: You said "Athletic Footwear" but search terms show "Athletic Shoes" → Use "Athletic Shoes"

### Rule 8: Synonyms/Translations on Same Rank
Terms with same meaning MUST be on same rank with " / " separator:
- Synonyms: "Couch / Sofa"
- Translations: "Soy Sauce / Kecap Manis"
- Implied same: "Stroller / Baby Stroller"
- Regional: "Flashlight / Torch"
- Abbreviations: "Television / TV"

---

## DECISION FLOWCHART FOR EACH HIERARCHY LEVEL

```
For each potential rank:

┌─────────────────────────────────────────────────────────────┐
│ Is this term a SYNONYM of another rank?                     │
│ (Same meaning, translation, implied same, regional variant) │
└─────────────────────────┬───────────────────────────────────┘
                          │
              ┌───────────┴───────────┐
              │                       │
             YES                      NO
              │                       │
              ▼                       ▼
┌─────────────────────────┐ ┌─────────────────────────────────┐
│ MERGE with that rank    │ │ Is it a TRUE parent-child       │
│ using " / " separator   │ │ hierarchy?                      │
└─────────────────────────┘ │ (Rank 1 IS A TYPE OF Rank 2)    │
                            └─────────────┬───────────────────┘
                                          │
                                ┌─────────┴─────────┐
                               YES                  NO
                                │                   │
                                ▼                   ▼
                  ┌─────────────────────┐ ┌─────────────────────┐
                  │ Keep as separate    │ │ MERGE into same     │
                  │ rank                │ │ rank with " / "     │
                  └──────────┬──────────┘ └─────────────────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ Does term appear in │
                  │ search terms?       │
                  └──────────┬──────────┘
                             │
                   ┌─────────┴─────────┐
                  YES                  NO
                   │                   │
                   ▼                   ▼
        ┌──────────────┐    ┌─────────────────────┐
        │ KEEP rank    │    │ Apply Two-Question  │
        └──────────────┘    │ Test (Q1 + Q2)      │
                            └──────────┬──────────┘
                                       │
                             ┌─────────┴─────────┐
                            PASS               FAIL
                             │                   │
                             ▼                   ▼
                   ┌──────────────┐    ┌──────────────┐
                   │ KEEP rank   │    │ REMOVE rank  │
                   └──────────────┘    └──────────────┘
```

---

## OUTPUT FORMAT

Return ONLY valid JSON in this exact format:

```json
{
  "taxonomy": [
    { "rank": 1, "product_type": "[Most Specific - can include ' / ' for synonyms]" },
    { "rank": 2, "product_type": "[Broader Category - can include ' / ' for synonyms]" },
    { "rank": 3, "product_type": "[Even Broader - can include ' / ' for synonyms]" }
  ],
  "phase_1_initial_hierarchy": {
    "rank_1": "[Initial term from product info]",
    "rank_2": "[Initial term from product info]",
    "rank_3": "[Initial term from product info]",
    "rank_4": "[Initial term from product info or null]"
  },
  "phase_2_search_analysis": {
    "product_types_in_search_terms": ["list of all product types extracted from search terms"],
    "rank_1": {
      "status": "FOUND|SYNONYM_MERGED|REPLACED|NOT_FOUND",
      "search_term_matches": ["matching terms"],
      "action": "kept|merged|replaced|flagged",
      "synonyms_merged": ["terms merged with / separator"]
    },
    "rank_2": {
      "status": "FOUND|SYNONYM_MERGED|REPLACED|ADDED|NOT_FOUND",
      "search_term_matches": ["matching terms"],
      "action": "kept|merged|replaced|added|flagged",
      "synonyms_merged": ["terms merged with / separator"]
    },
    "rank_3": {
      "status": "FOUND|SYNONYM_MERGED|REPLACED|ADDED|NOT_FOUND",
      "search_term_matches": ["matching terms"],
      "action": "kept|merged|replaced|added|removed",
      "synonyms_merged": ["terms merged with / separator"]
    },
    "levels_added": ["any new levels added from search terms"],
    "levels_merged": ["any levels merged as synonyms"]
  },
  "phase_3_rules_applied": {
    "synonym_check": {
      "merges_made": ["Term A / Term B merged at Rank X (reason)"]
    },
    "rank_2": { "Q1_pass": true, "Q2_pass": true, "kept": true },
    "rank_3": { "Q1_pass": true, "Q2_pass": true, "kept": true },
    "rank_4": { "Q1_pass": false, "Q2_pass": false, "kept": false, "removal_reason": "[why it failed]" }
  },
  "search_terms_analysis": {
    "product_types_extracted": ["[list of product type terms found in search terms]"],
    "excluded_terms": ["[terms excluded with reason - e.g., 'waterproof (adjective)']"]
  }
}
```

---

## EXAMPLES

### Example 1: Pencil Eyeliner (3 Levels with Synonym Merge)

**Input:**
- Title: "Waterproof Pencil Eyeliner - Black, Long-lasting Formula"
- Product Type: "Eyeliner"
- Category: "Beauty > Makeup > Eyes"
- Search Terms: "pencil eyeliner, eyeliner pencil, eye liner, black eyeliner, waterproof eyeliner, eye makeup, makeup for eyes, eyeliner for beginners, best eyeliner, eye cosmetics"

**Phase 1 - Product Info Analysis:**
- Core product: Pencil Eyeliner
- Initial hierarchy: Pencil Eyeliner → Eyeliner → Eye Makeup → Makeup

**Phase 2 - Search Term Analysis:**
- "Pencil Eyeliner" → FOUND ✓
- "Eyeliner Pencil" → FOUND (same meaning, different word order) → MERGE with Rank 1
- "Eyeliner" / "Eye Liner" → FOUND ✓ (merge as synonyms)
- "Eye Makeup" / "Eye Cosmetics" → BOTH FOUND → MERGE as synonyms
- "Makeup" → Only as "makeup for eyes" (use-case) → Flag

**Phase 3 - Rules Applied:**
- Rank 1: "Pencil Eyeliner / Eyeliner Pencil" (merged - same product)
- Rank 2: "Eyeliner / Eye Liner" (merged - same meaning)
- Rank 3: "Eye Makeup / Eye Cosmetics" (merged - synonyms) Q1 ✓ Q2 ✓
- Rank 4: "Makeup" - REMOVED (too broad, fails Q2)

**Output:**
```json
{
  "taxonomy": [
    { "rank": 1, "product_type": "Pencil Eyeliner / Eyeliner Pencil" },
    { "rank": 2, "product_type": "Eyeliner / Eye Liner" },
    { "rank": 3, "product_type": "Eye Makeup / Eye Cosmetics" }
  ],
  "phase_1_initial_hierarchy": {
    "rank_1": "Pencil Eyeliner",
    "rank_2": "Eyeliner",
    "rank_3": "Eye Makeup",
    "rank_4": "Makeup"
  },
  "phase_2_search_analysis": {
    "product_types_in_search_terms": ["pencil eyeliner", "eyeliner pencil", "eyeliner", "eye liner", "eye makeup", "eye cosmetics"],
    "rank_1": {
      "status": "SYNONYM_MERGED",
      "search_term_matches": ["pencil eyeliner", "eyeliner pencil"],
      "action": "merged",
      "synonyms_merged": ["Pencil Eyeliner", "Eyeliner Pencil"]
    },
    "rank_2": {
      "status": "SYNONYM_MERGED",
      "search_term_matches": ["eyeliner", "eye liner"],
      "action": "merged",
      "synonyms_merged": ["Eyeliner", "Eye Liner"]
    },
    "rank_3": {
      "status": "SYNONYM_MERGED",
      "search_term_matches": ["eye makeup", "eye cosmetics"],
      "action": "merged",
      "synonyms_merged": ["Eye Makeup", "Eye Cosmetics"]
    },
    "levels_added": [],
    "levels_merged": ["Rank 1: Pencil Eyeliner + Eyeliner Pencil", "Rank 2: Eyeliner + Eye Liner", "Rank 3: Eye Makeup + Eye Cosmetics"]
  },
  "phase_3_rules_applied": {
    "synonym_check": {
      "merges_made": [
        "Pencil Eyeliner / Eyeliner Pencil at Rank 1 (same product, word order)",
        "Eyeliner / Eye Liner at Rank 2 (same meaning, spacing)",
        "Eye Makeup / Eye Cosmetics at Rank 3 (synonyms)"
      ]
    },
    "rank_2": { "Q1_pass": true, "Q2_pass": true, "kept": true },
    "rank_3": { "Q1_pass": true, "Q2_pass": true, "kept": true },
    "rank_4": { "Q1_pass": false, "Q2_pass": false, "kept": false, "removal_reason": "Too broad - fails Q2: someone browsing 'makeup' unlikely to discover eyeliner" }
  },
  "search_terms_analysis": {
    "product_types_extracted": ["pencil eyeliner", "eyeliner pencil", "eyeliner", "eye liner", "eye makeup", "eye cosmetics"],
    "excluded_terms": ["waterproof (adjective)", "black (color)", "long-lasting (benefit)", "for beginners (audience)", "best (qualifier)"]
  }
}
```

---

### Example 2: Baby Stroller (Synonym Merge - NOT Hierarchy)

**Input:**
- Title: "Lightweight Baby Stroller - Foldable, Travel-Friendly"
- Product Type: "Stroller"
- Category: "Baby > Strollers & Accessories"
- Search Terms: "baby stroller, stroller, lightweight stroller, travel stroller, umbrella stroller, foldable stroller, stroller for infant, baby pram, pram, baby products, pushchair"

**Phase 1 - Product Info Analysis:**
- Core product: Baby Stroller
- Initial hierarchy: Baby Stroller → Stroller → Baby Gear → Baby Products

**Phase 2 - Search Term Analysis:**
- "Baby Stroller" → FOUND ✓
- "Stroller" → FOUND ✓
- BUT WAIT: Is "Baby Stroller → Stroller" a true hierarchy?
  - Test: Is Baby Stroller a TYPE OF Stroller where Stroller includes OTHER types?
  - Answer: NO - all strollers are baby strollers. They mean the SAME thing.
  - Action: MERGE "Stroller / Baby Stroller / Baby Pram / Pram / Pushchair" into ONE rank
- "Baby Gear" → NOT FOUND ✗
- "Baby Products" → FOUND ✓ → Can be Rank 2

**Phase 3 - Rules Applied:**
- Rank 1: "Stroller / Baby Stroller / Baby Pram / Pram / Pushchair" (all synonyms merged)
- Rank 2: "Baby Products" → Q1 ✓ Q2 ✓ → Keep (someone browsing baby products can find strollers)

**Output:**
```json
{
  "taxonomy": [
    { "rank": 1, "product_type": "Stroller / Baby Stroller / Baby Pram / Pram / Pushchair" },
    { "rank": 2, "product_type": "Baby Products" }
  ],
  "phase_1_initial_hierarchy": {
    "rank_1": "Baby Stroller",
    "rank_2": "Stroller",
    "rank_3": "Baby Gear",
    "rank_4": "Baby Products"
  },
  "phase_2_search_analysis": {
    "product_types_in_search_terms": ["baby stroller", "stroller", "umbrella stroller", "travel stroller", "baby pram", "pram", "baby products", "pushchair"],
    "rank_1": {
      "status": "SYNONYM_MERGED",
      "search_term_matches": ["baby stroller", "stroller", "baby pram", "pram", "pushchair"],
      "action": "merged",
      "synonyms_merged": ["Stroller", "Baby Stroller", "Baby Pram", "Pram", "Pushchair"]
    },
    "rank_2": {
      "status": "FOUND",
      "search_term_matches": ["baby products"],
      "action": "kept",
      "synonyms_merged": []
    },
    "levels_added": [],
    "levels_merged": ["Original Rank 1 (Baby Stroller) + Rank 2 (Stroller) merged - they mean the same thing"]
  },
  "phase_3_rules_applied": {
    "synonym_check": {
      "merges_made": [
        "Stroller / Baby Stroller / Baby Pram / Pram / Pushchair at Rank 1 (all refer to same product - regional variations and synonyms)"
      ]
    },
    "rank_2": { "Q1_pass": true, "Q2_pass": true, "kept": true },
    "rank_3": { "Q1_pass": false, "Q2_pass": false, "kept": false, "removal_reason": "Baby Gear not in search terms + vague umbrella term" }
  },
  "search_terms_analysis": {
    "product_types_extracted": ["stroller", "baby stroller", "umbrella stroller", "travel stroller", "baby pram", "pram", "pushchair", "baby products"],
    "excluded_terms": ["lightweight (adjective)", "foldable (feature)", "travel-friendly (benefit)", "for infant (audience)"]
  }
}
```

---

### Example 3: Soy Sauce (Translation Merge)

**Input:**
- Title: "Premium Soy Sauce - Naturally Brewed, 500ml"
- Product Type: "Soy Sauce"
- Category: "Food > Condiments > Asian Sauces"
- Search Terms: "soy sauce, kecap manis, asian sauce, cooking sauce, soya sauce, condiments, shoyu, tamari"

**Phase 1 - Product Info Analysis:**
- Core product: Soy Sauce
- Initial hierarchy: Soy Sauce → Asian Sauce → Condiments → Food

**Phase 2 - Search Term Analysis:**
- "Soy Sauce" → FOUND ✓
- "Soya Sauce" → FOUND (alternate spelling) → MERGE
- "Kecap Manis" → FOUND (Indonesian translation) → MERGE
- "Shoyu" → FOUND (Japanese term) → MERGE
- "Tamari" → FOUND (Japanese variant) → Could merge or keep separate (it's a specific type)
- "Asian Sauce" → FOUND ✓
- "Condiments" → FOUND ✓
- "Cooking Sauce" → FOUND but too broad

**Phase 3 - Rules Applied:**
- Rank 1: "Soy Sauce / Soya Sauce / Kecap Manis / Shoyu" (merged translations/synonyms)
- Rank 2: "Asian Sauce" Q1 ✓ Q2 ✓
- Rank 3: "Condiments" Q1 ✓ Q2 ✓
- Rank 4: "Food" - Too broad, fails Q2

**Output:**
```json
{
  "taxonomy": [
    { "rank": 1, "product_type": "Soy Sauce / Soya Sauce / Kecap Manis / Shoyu" },
    { "rank": 2, "product_type": "Asian Sauce" },
    { "rank": 3, "product_type": "Condiments" }
  ],
  "phase_1_initial_hierarchy": {
    "rank_1": "Soy Sauce",
    "rank_2": "Asian Sauce",
    "rank_3": "Condiments",
    "rank_4": "Food"
  },
  "phase_2_search_analysis": {
    "product_types_in_search_terms": ["soy sauce", "kecap manis", "asian sauce", "cooking sauce", "soya sauce", "condiments", "shoyu", "tamari"],
    "rank_1": {
      "status": "SYNONYM_MERGED",
      "search_term_matches": ["soy sauce", "soya sauce", "kecap manis", "shoyu"],
      "action": "merged",
      "synonyms_merged": ["Soy Sauce", "Soya Sauce", "Kecap Manis", "Shoyu"]
    },
    "rank_2": {
      "status": "FOUND",
      "search_term_matches": ["asian sauce"],
      "action": "kept",
      "synonyms_merged": []
    },
    "rank_3": {
      "status": "FOUND",
      "search_term_matches": ["condiments"],
      "action": "kept",
      "synonyms_merged": []
    },
    "levels_added": [],
    "levels_merged": ["Soy Sauce + Soya Sauce + Kecap Manis + Shoyu at Rank 1"]
  },
  "phase_3_rules_applied": {
    "synonym_check": {
      "merges_made": [
        "Soy Sauce / Soya Sauce / Kecap Manis / Shoyu at Rank 1 (translations and alternate spellings)"
      ]
    },
    "rank_2": { "Q1_pass": true, "Q2_pass": true, "kept": true },
    "rank_3": { "Q1_pass": true, "Q2_pass": true, "kept": true },
    "rank_4": { "Q1_pass": false, "Q2_pass": false, "kept": false, "removal_reason": "Food is too broad - fails Q2" }
  },
  "search_terms_analysis": {
    "product_types_extracted": ["soy sauce", "soya sauce", "kecap manis", "shoyu", "tamari", "asian sauce", "condiments"],
    "excluded_terms": ["premium (adjective)", "naturally brewed (feature)", "500ml (size)", "cooking (use case)"]
  }
}
```

---

### Example 4: Cell Phone Case (Multiple Synonyms)

**Input:**
- Title: "iPhone 15 Pro Case - Shockproof, Clear Design"
- Product Type: "Phone Case"
- Category: "Electronics > Cell Phone Accessories"
- Search Terms: "iphone case, phone case, cell phone case, mobile phone case, smartphone case, iphone 15 case, phone cover, mobile cover, phone accessories"

**Phase 1 - Product Info Analysis:**
- Core product: iPhone Case
- Initial hierarchy: iPhone Case → Phone Case → Phone Accessories

**Phase 2 - Search Term Analysis:**
- Multiple terms for same product found:
  - "iPhone Case" / "iPhone 15 Case" → specific but "iPhone 15" is model variant
  - "Phone Case" / "Cell Phone Case" / "Mobile Phone Case" / "Smartphone Case" / "Phone Cover" / "Mobile Cover" → ALL SAME MEANING
- "Phone Accessories" → FOUND ✓

**Phase 3 - Rules Applied:**
- Rank 1: Merge all synonyms for the case itself
- Rank 2: "Phone Accessories" Q1 ✓ Q2 ✓

**Output:**
```json
{
  "taxonomy": [
    { "rank": 1, "product_type": "Phone Case / Cell Phone Case / Mobile Phone Case / Smartphone Case / Phone Cover / Mobile Cover" },
    { "rank": 2, "product_type": "Phone Accessories" }
  ],
  "phase_1_initial_hierarchy": {
    "rank_1": "iPhone Case",
    "rank_2": "Phone Case",
    "rank_3": "Phone Accessories",
    "rank_4": null
  },
  "phase_2_search_analysis": {
    "product_types_in_search_terms": ["iphone case", "phone case", "cell phone case", "mobile phone case", "smartphone case", "phone cover", "mobile cover", "phone accessories"],
    "rank_1": {
      "status": "SYNONYM_MERGED",
      "search_term_matches": ["phone case", "cell phone case", "mobile phone case", "smartphone case", "phone cover", "mobile cover"],
      "action": "merged",
      "synonyms_merged": ["Phone Case", "Cell Phone Case", "Mobile Phone Case", "Smartphone Case", "Phone Cover", "Mobile Cover"]
    },
    "rank_2": {
      "status": "FOUND",
      "search_term_matches": ["phone accessories"],
      "action": "kept",
      "synonyms_merged": []
    },
    "levels_added": [],
    "levels_merged": ["iPhone Case merged with Phone Case and all synonyms at Rank 1 - iPhone Case is just a brand-specific version"]
  },
  "phase_3_rules_applied": {
    "synonym_check": {
      "merges_made": [
        "Phone Case / Cell Phone Case / Mobile Phone Case / Smartphone Case / Phone Cover / Mobile Cover at Rank 1 (all synonyms referring to same product type)"
      ]
    },
    "rank_2": { "Q1_pass": true, "Q2_pass": true, "kept": true }
  },
  "search_terms_analysis": {
    "product_types_extracted": ["phone case", "cell phone case", "mobile phone case", "smartphone case", "phone cover", "mobile cover", "phone accessories"],
    "excluded_terms": ["iphone 15 (brand + model)", "shockproof (feature)", "clear (adjective)", "design (generic)"]
  }
}
```

---

### Example 5: Water Bottle (Single Level - No Synonyms)

**Input:**
- Title: "Stainless Steel Water Bottle 32oz - Insulated, Leak-Proof"
- Product Type: "Water Bottle"
- Category: "Sports & Outdoors > Sports Water Bottles"
- Search Terms: "water bottle, insulated water bottle, stainless steel water bottle, gym water bottle, sports bottle, metal water bottle, 32 oz water bottle, drink bottle"

**Phase 1 - Product Info Analysis:**
- Core product: Water Bottle
- Initial hierarchy: Water Bottle → Drinkware → Kitchen & Dining

**Phase 2 - Search Term Analysis:**
- "Water Bottle" → FOUND ✓
- "Drink Bottle" → FOUND (synonym) → MERGE
- "Sports Bottle" → FOUND but this is a USE-CASE variant, not pure synonym → Could merge
- "Drinkware" → NOT FOUND ✗
- "Kitchen & Dining" → NOT FOUND ✗

**Phase 3 - Rules Applied:**
- Rank 1: "Water Bottle / Drink Bottle" (merged synonyms)
- Rank 2: Drinkware - NOT FOUND + fails Q2 → REMOVE
- Single level taxonomy is valid

**Output:**
```json
{
  "taxonomy": [
    { "rank": 1, "product_type": "Water Bottle / Drink Bottle" }
  ],
  "phase_1_initial_hierarchy": {
    "rank_1": "Water Bottle",
    "rank_2": "Drinkware",
    "rank_3": "Kitchen & Dining",
    "rank_4": null
  },
  "phase_2_search_analysis": {
    "product_types_in_search_terms": ["water bottle", "drink bottle", "sports bottle"],
    "rank_1": {
      "status": "SYNONYM_MERGED",
      "search_term_matches": ["water bottle", "drink bottle"],
      "action": "merged",
      "synonyms_merged": ["Water Bottle", "Drink Bottle"]
    },
    "rank_2": {
      "status": "NOT_FOUND",
      "search_term_matches": [],
      "action": "flagged",
      "synonyms_merged": []
    },
    "levels_added": [],
    "levels_merged": ["Water Bottle + Drink Bottle at Rank 1"]
  },
  "phase_3_rules_applied": {
    "synonym_check": {
      "merges_made": [
        "Water Bottle / Drink Bottle at Rank 1 (synonyms)"
      ]
    },
    "rank_2": { "Q1_pass": false, "Q2_pass": false, "kept": false, "removal_reason": "Drinkware not in search terms + fails Q2: no one explores 'drinkware' to find water bottles" }
  },
  "search_terms_analysis": {
    "product_types_extracted": ["water bottle", "drink bottle", "sports bottle"],
    "excluded_terms": ["stainless steel (material)", "insulated (feature)", "leak-proof (feature)", "gym (use case)", "metal (material)", "32 oz (size)"]
  }
}
```

---

## CRITICAL REMINDERS

1. **Phase 1 builds the logical hierarchy** - Use product info to understand what the product IS
2. **Phase 2 ACTIVELY improves hierarchy** - Validate, ADD missing levels, TWEAK terminology, UPDATE structure, MERGE synonyms
3. **Phase 3 applies quality rules** - Two-Question Test is the final filter
4. **SYNONYMS/TRANSLATIONS = SAME RANK** - Use " / " separator for terms with same meaning
5. **TRUE HIERARCHY TEST:** Ask "Is X a TYPE OF Y, where Y includes OTHER types too?"
6. **If not in search terms AND fails Two-Question Test → REMOVE**
7. **Single level is valid** - Don't force hierarchy levels that don't exist
8. **Use buyer's language** - If search terms use different words, use THEIR words
9. **ADD levels from search terms** - If search terms reveal valid broader categories, add them
10. **Output ONLY the JSON** - No additional text before or after

Now analyze the provided inputs and generate the taxonomy.
```

---

## Input Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{title}}` | Product title | "Waterproof Pencil Eyeliner - Black" |
| `{{bullet_points}}` | Product bullet points | "Long-lasting formula..." |
| `{{description}}` | Product description | "This eyeliner provides..." |
| `{{product_type}}` | Seller-provided product type | "Eyeliner" |
| `{{category_root}}` | Root category | "Beauty" |
| `{{category_sub}}` | Sub category | "Makeup > Eyes" |
| `{{search_terms}}` | Comma-separated search terms | "eyeliner, eye makeup, pencil liner..." |

---

## Synonym/Same-Meaning Rules

| Type | Example | Format |
|------|---------|--------|
| **Synonyms** | Couch, Sofa | "Couch / Sofa" |
| **Translations** | Soy Sauce, Kecap Manis | "Soy Sauce / Kecap Manis" |
| **Implied Same** | Stroller, Baby Stroller | "Stroller / Baby Stroller" |
| **Regional Variations** | Flashlight, Torch | "Flashlight / Torch" |
| **Alternate Spellings** | Soy Sauce, Soya Sauce | "Soy Sauce / Soya Sauce" |
| **Abbreviations** | Television, TV | "Television / TV" |
| **Word Order** | Pencil Eyeliner, Eyeliner Pencil | "Pencil Eyeliner / Eyeliner Pencil" |

**TEST:** If both terms refer to the same product/category and one is NOT a subset of the other → SAME RANK with " / "

---

## Three-Phase Process Summary

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 1: PRODUCT INFO ANALYSIS                                             │
│  ─────────────────────────────────────────────────────────────────────────  │
│  • Read title, description, category                                        │
│  • Identify core product type (Rank 1)                                      │
│  • Build logical hierarchy upward: "What is X a type of?"                   │
│  • Output: Initial hierarchy (may have 2-4 levels)                          │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 2: SEARCH TERM ANALYSIS (Validate, Add, Tweak, Update, Merge)        │
│  ─────────────────────────────────────────────────────────────────────────  │
│  • Extract all product types from search terms                              │
│  • VALIDATE: Is each hierarchy level in search terms?                       │
│  • ADD: Are there valid broader categories in search terms to add?          │
│  • TWEAK: Replace terms with buyer's language from search terms             │
│  • UPDATE: Fill gaps if search terms reveal missing intermediate levels     │
│  • MERGE: Combine synonyms/translations with " / " on same rank             │
│  • Output: Updated hierarchy with merges and additions                      │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 3: RULES APPLICATION                                                 │
│  ─────────────────────────────────────────────────────────────────────────  │
│  • Verify TRUE hierarchy (not synonyms incorrectly ranked)                  │
│  • Apply Two-Question Test (Q1 + Q2) to flagged levels                      │
│  • Remove artificial categories and vague umbrella terms                    │
│  • Final synonym merge check                                                │
│  • Output: Final taxonomy (JSON)                                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Rules Summary

| Rule | Description |
|------|-------------|
| 1 | Strict subset hierarchy (Rank 1 ⊂ Rank 2 ⊂ Rank 3) - TRUE parent-child only |
| 2 | Two-Question Test: Q1 (search intent) + Q2 (discovery intent) |
| 3 | No artificial intermediate categories |
| 4 | No vague umbrella terms unless validated in search terms |
| 5 | Search terms override assumptions |
| 6 | Single level is valid |
| 7 | Use buyer's language from search terms |
| 8 | **Synonyms/Translations/Same-meaning = SAME RANK with " / "** |

---

## Exclusion List (Never Include in Taxonomy)

| Category | Examples |
|----------|----------|
| Adjectives | waterproof, portable, premium, lightweight, durable |
| Features | Bluetooth, rechargeable, LED, 32GB, wireless, foldable |
| Benefits | comfortable, easy-to-use, long-lasting, fast |
| Colors | black, red, blue, pink, white, silver |
| Size/Variants | large, small, 32oz, XL, pack of 2, twin pack |
| Use Cases | for travel, for running, for camping, for office |
| Audience | men's, women's, kids', for beginners, professional |
| Materials | silicone, leather, stainless steel, plastic, wood, metal |
| Brand Names | Nike, Apple, Samsung, Sony, iPhone, any brand |
| Qualifiers | best, cheap, top rated, affordable, new, latest, premium |
| Year/Model | 2024, v2, gen 3, new model, latest version, iPhone 15 |
