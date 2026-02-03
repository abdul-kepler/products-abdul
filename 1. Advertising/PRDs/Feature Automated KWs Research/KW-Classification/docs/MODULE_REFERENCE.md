# Module Reference v1.1

## Executive Summary

This pipeline classifies **Amazon Advertising Search Terms** to determine their relevance to a product listing. The goal is to help Amazon sellers understand which search terms are worth bidding on.

### Why This Pipeline Exists

**The Problem:** Initial attempts to classify search terms using 2-3 monolithic prompts failed. The LLM couldn't consistently handle:
- Brand detection (own brand vs competitor vs non-branded)
- Product type matching
- Use case relevance
- Substitute/complementary product identification

**The Solution:** Break the complex classification into a pipeline of specialized modules where each module:
- Has a single, well-defined responsibility
- Produces consistent, verifiable outputs
- Builds on previous modules' outputs

---

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SEARCH TERM CLASSIFICATION PIPELINE                       │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  STAGE 1: BRAND ENTITY EXTRACTION                                           │
│  Purpose: Build comprehensive brand dictionaries for classification         │
│                                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐                              │
│  │   M01    │    │   M01a   │    │   M01b   │                              │
│  │ Extract  │    │ Generate │    │ Extract  │                              │
│  │  Brand   │    │Variations│    │ Related  │                              │
│  │ Entities │    │ (typos)  │    │  Terms   │                              │
│  └──────────┘    └──────────┘    └──────────┘                              │
│       │                               │                                     │
│       │         Same process for      │                                     │
│       │         competitor ASINs      │                                     │
│       ▼               (M03)           ▼                                     │
│  brand_entities ──────────────▶ variations + sub_brands + manufacturer     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STAGE 2: BRAND SCOPE CLASSIFICATION                                        │
│  Purpose: Classify each search term's branding scope (OB/CB/NB)            │
│                                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐                              │
│  │   M02    │    │   M04    │    │   M05    │                              │
│  │   Own    │    │Competitor│    │   Non-   │                              │
│  │  Brand   │    │  Brand   │    │ Branded  │                              │
│  │  (OB)    │    │  (CB)    │    │  (NB)    │                              │
│  └──────────┘    └──────────┘    └──────────┘                              │
│       │               │               │                                     │
│       └───────────────┴───────────────┘                                     │
│                       │                                                     │
│                       ▼                                                     │
│              brand_scope: OB | CB | NB                                      │
│              + hidden brand detection                                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STAGE 3: PRODUCT FOUNDATION                                                │
│  Purpose: Extract product attributes for relevance matching                 │
│                                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐                              │
│  │   M06    │───▶│   M07    │───▶│   M08    │                              │
│  │ Taxonomy │    │ Extract  │    │  Rank    │                              │
│  │(hierarchy)│    │Attributes│    │Attributes│                              │
│  └──────────┘    └──────────┘    └──────────┘                              │
│       │                               │                                     │
│       ▼                               ▼                                     │
│  taxonomy[]                    attribute_table[]                            │
│                                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐                              │
│  │   M09    │───▶│   M10    │───▶│   M11    │                              │
│  │ Primary  │    │ Validate │    │  Hard    │                              │
│  │   Use    │    │   Use    │    │Constraints│                              │
│  └──────────┘    └──────────┘    └──────────┘                              │
│       │               │               │                                     │
│       ▼               ▼               ▼                                     │
│  primary_use    validated_use   hard_constraints[]                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STAGE 4: RELEVANCE CLASSIFICATION                                          │
│  Purpose: Determine search term relevance (R/S/C/N)                         │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────┐       │
│  │                    M12: Decision Tree                            │       │
│  │                                                                  │       │
│  │  Step 1: Hard Constraint Check ────▶ Violated? ───▶ N           │       │
│  │                │                                                 │       │
│  │                ▼ (not violated)                                  │       │
│  │  Step 2: Product Type Check                                      │       │
│  │                │                                                 │       │
│  │       ┌───────┴───────┐                                         │       │
│  │       ▼               ▼                                         │       │
│  │  Same Type       Different Type                                  │       │
│  │       │               │                                         │       │
│  │       ▼               ▼                                         │       │
│  │  Step 3a:        Step 3b:                                       │       │
│  │  Same Use? ──▶R  Same Use? ──▶S                                 │       │
│  │  Diff Use? ──▶N  Diff Use? ──▶ Step 4                           │       │
│  │                        │                                        │       │
│  │                        ▼                                        │       │
│  │                   Step 4: Complementary?                        │       │
│  │                   Used together? ──▶ C                          │       │
│  │                   Not related? ──▶ N                            │       │
│  └─────────────────────────────────────────────────────────────────┘       │
│                                                                             │
│  Output: classification = R | S | C | N                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Classification Output Values

| Value | Name | Definition | Example |
|-------|------|------------|---------|
| **R** | Relevant | Same product type AND same primary use | "wireless earbuds" for JBL earbuds |
| **S** | Substitute | Different product type BUT same primary use | "headphones" for earbuds (both: audio listening) |
| **C** | Complementary | Different product, commonly used together | "earbud case" for earbuds |
| **N** | Negative | Violates constraint, different use, or unrelated | "wired earbuds" for wireless-only product |

---

## Stage 1: Brand Entity Extraction

### Purpose
Build comprehensive brand dictionaries that will be used to detect branded search terms. This stage processes BOTH the own product AND competitor products using the same modules.

### Why M01 → M01a → M01b?
The original M01 tried to extract everything at once, which led to inconsistent results. Breaking it into sub-modules:
- **M01**: Extract raw brand entities from listing
- **M01a**: Generate search variations (typos, truncations, phonetic spellings)
- **M01b**: Extract related terms (sub-brands, product lines, manufacturer)

### Data Flow
```
Product Listing ──▶ M01 ──▶ brand_entities
                     │
                     ▼
               M01a ──▶ variations (comma-separated)
                     │       "JBL, J-B-L, jbl, Jbl"
                     │
                     ▼
               M01b ──▶ sub_brands, searchable_standards, manufacturer
                            "Vibe Beam, Tune, Live Pro"
```

### M01a: Generate Brand Variations
**Purpose:** Generate search-friendly variations of brand names that users might type

**Output:**
```json
{
  "brand_name": "JBL",
  "variations": "JBL, J-B-L, jbl, Jbl, jBL"
}
```

**Variation Types:**
- Case variations: JBL, jbl, Jbl
- Spacing/hyphenation: J-B-L, J B L
- Common typos: JLB, JBK
- Phonetic spellings (for non-English brands)
- Truncations: JB (if commonly used)

### M01b: Extract Related Terms
**Purpose:** Extract brand-associated terms that indicate brand presence

**Output:**
```json
{
  "sub_brands": ["Vibe Beam", "Tune", "Live Pro"],
  "searchable_standards": ["Dolby Atmos"],
  "manufacturer": "Harman International"
}
```

**Important Rules:**
- `sub_brands`: Product lines, series names, model families
- `searchable_standards`: Brand-specific technologies (NOT universal standards)
  - INCLUDE: Dolby Atmos (brand-specific)
  - EXCLUDE: ENFit (ISO standard), USB-C (universal), Bluetooth (universal)
- `manufacturer`: Parent company if different from brand name

### M03: Competitor Entity Extraction
**Note:** M03 follows the same process as M01 but for competitor ASINs. In practice, we run M01 → M01a → M01b on each competitor ASIN to build their brand dictionaries.

---

## Stage 2: Brand Scope Classification

### Purpose
Determine if a search term contains brand references:
- **OB (Own Brand)**: Contains own brand terms
- **CB (Competitor Brand)**: Contains competitor brand terms
- **NB (Non-Branded)**: Generic, no brand references

### V3 Format (Dynamic Competitors)
The v3 modules use a dynamic array format instead of fixed slots:

```json
{
  "keyword": "jbl earbuds",
  "own_brand": {
    "name": "JBL",
    "variations": "JBL, J-B-L, jbl",
    "related_terms": "Vibe Beam, Tune, Live Pro"
  },
  "competitors": [
    {
      "name": "Apple",
      "variations": "Apple, apple, APPLE",
      "related_terms": "AirPods, AirPod, EarPods"
    },
    {
      "name": "Sony",
      "variations": "Sony, SONY, sony",
      "related_terms": "WF-1000XM, LinkBuds"
    }
  ]
}
```

### Hidden Brand Detection
Stage 2 modules should also detect brands NOT provided in the input. If a search term contains a recognizable brand that wasn't in the competitor list, flag it.

### M02_v3: Own Brand Classification
**Input:** keyword, own_brand (with variations + related_terms)
**Output:**
```json
{
  "branding_scope": "OB" | null,
  "matched_term": "jbl",
  "match_type": "variation",
  "confidence": "high"
}
```

### M04_v3: Competitor Brand Classification
**Input:** keyword, competitors[]
**Output:**
```json
{
  "branding_scope": "CB" | null,
  "matched_term": "airpods",
  "matched_competitor": "Apple",
  "confidence": "high"
}
```

### M05_v3: Non-Branded Classification
**Input:** keyword, own_brand, competitors[]
**Output:**
```json
{
  "branding_scope": "NB" | null,
  "confidence": "high",
  "reasoning": "Generic product term with no brand references",
  "found_term": null,
  "source": null
}
```

---

## Stage 3: Product Foundation

### Purpose
Extract product characteristics needed to determine search term relevance:
- What type of product is this?
- What are its key attributes?
- What is its primary purpose?
- Which attributes are non-negotiable?

### M06: Product Type Taxonomy
**Purpose:** Create hierarchical product classification

**Output:**
```json
{
  "taxonomy": [
    {"level": 1, "product_type": "True Wireless Earbuds", "rank": 1},
    {"level": 2, "product_type": "Wireless Earphones", "rank": 2},
    {"level": 3, "product_type": "Earphones", "rank": 3}
  ]
}
```

### M07: Extract Product Attributes
**Purpose:** Identify variants, use cases, and target audiences

**Output:**
```json
{
  "variants": ["Bluetooth 5.2", "32hr Battery", "White", "In-Ear"],
  "use_cases": ["Daily Entertainment", "Commuting", "Sports"],
  "audiences": ["Music Lovers", "Commuters"]
}
```

### M08: Rank Attributes
**Purpose:** Prioritize attributes by importance for keyword matching

**Output:**
```json
{
  "attribute_table": [
    {"attribute_type": "Variant", "attribute_value": "In-Ear", "rank": 1},
    {"attribute_type": "Variant", "attribute_value": "Bluetooth 5.2", "rank": 2},
    {"attribute_type": "Use Case", "attribute_value": "Daily Entertainment", "rank": 1}
  ]
}
```

### M09: Identify Primary Intended Use
**Purpose:** Determine the ONE core reason this product exists

**Rules:**
- 3-6 words only
- Describe what product DOES, not how well
- NO features, specifications, technologies
- NO adjectives, marketing language
- ONE core purpose only

**Examples:**
| Product | Primary Use |
|---------|-------------|
| Water Bottle | portable hydration |
| Earbuds | audio listening |
| Oven Mitt | heat protection when cooking |
| Phone Mount | phone mounting |

### M10: Validate Primary Intended Use
**Purpose:** Clean up the primary use phrase if needed

**Input:** All M09 inputs + primary_use from M09
**Logic:**
- If phrase is valid → return unchanged
- If phrase violates rules → fix and return corrected version

**Output:** `validated_use` - the clean phrase (M11 doesn't know if it was corrected)

### M11: Identify Hard Constraints
**Purpose:** Find attributes that are NON-NEGOTIABLE for product function

**Question:** "If this attribute's value is different, would the product become IMPOSSIBLE to use for its intended function?"

**Examples:**
| Product | Attribute | Hard Constraint? | Why |
|---------|-----------|-----------------|-----|
| Bluetooth Earbuds | Bluetooth | YES | Wireless function requires it |
| Bluetooth Earbuds | White color | NO | Color doesn't affect function |
| iPhone 15 Case | iPhone 15 compatibility | YES | Won't fit other phones |
| 32oz Water Bottle | 32oz capacity | YES | Size is the requirement |

**Output:**
```json
{
  "hard_constraints": [
    {"attribute": "Bluetooth", "value": "Bluetooth 5.2", "reason": "wireless function"}
  ]
}
```

---

## Stage 4: Relevance Classification (M12-M16)

### Purpose
Using all data from Stage 3, classify search terms as R/S/C/N.

### M12: Combined Decision Tree
**Replaces:** Sequential M13 → M14 → M15 → M16 calls
**Advantage:** Single LLM call with full context, better accuracy

**Decision Steps:**

1. **Hard Constraint Check**
   - Does keyword imply an attribute that violates a hard constraint?
   - Example: "wired earbuds" violates Bluetooth constraint → N

2. **Product Type Check**
   - Is the keyword asking for the same product type?
   - Same type → Step 3a
   - Different type → Step 3b

3a. **Primary Use (Same Type)**
   - Same product type, same primary use → **R (Relevant)**
   - Same product type, different use → **N (Negative)**

3b. **Substitute Check (Different Type)**
   - Different product type, but same primary use → **S (Substitute)**
   - Different type, different use → Step 4

4. **Complementary Check**
   - Products commonly used together → **C (Complementary)**
   - Not related → **N (Negative)**

### M13-M16: Individual Steps (Deprecated)
These modules exist for backwards compatibility but M12 is preferred:
- M13: CheckProductType
- M14: CheckPrimaryUseSameType
- M15: CheckSubstitute
- M16: CheckComplementary

---

## Data Dependencies Graph

### Module Input/Output Summary

| Module | Input | Output |
|--------|-------|--------|
| **M01** | brand_name, title, bullets, description, manufacturer | `brand_entities` |
| **M01a** | brand_name | `variations` |
| **M01b** | brand_name, title, bullets, description, manufacturer | `sub_brands`, `searchable_standards`, `manufacturer` |
| **M03** | title, bullets, description, brand_name, product_type, categories, known_competitors | `competitor_entities` |
| **M02_v3** | keyword, variations_own, related_terms_own | `branding_scope_1` (OB) |
| **M04_v3** | keyword, competitors[] | `branding_scope_2` (CB) |
| **M05_v3** | keyword, own_brand, competitors[] | `branding_scope_3` (NB) |
| **M06** | title, bullets, description, product_type, categories | `taxonomy` |
| **M07** | title, bullets, description, product_type, categories, product_attributes | `variants`, `use_cases`, `audiences` |
| **M08** | title, bullets, description, **taxonomy**, **variants**, **use_cases**, **audiences** | `attribute_table` |
| **M09** | title, bullets, description, **taxonomy**, **attribute_table**, product_attributes | `primary_use` |
| **M10** | M09 inputs + **primary_use** | `validated_use` |
| **M11** | title, bullets, description, **validated_use**, **taxonomy**, **attribute_table**, product_attributes | `hard_constraints` |
| **M12-16** | keyword, title, bullets, description, **validated_use**, **taxonomy**, **attribute_table**, product_attributes, **hard_constraints** | `relevancy` (R/S/C/N) |

### Visual Data Flow

```
                         PRODUCT LISTING (ASIN)
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
┌───────────────┐         ┌───────────────┐         ┌───────────────┐
│    M01        │         │     M06       │         │     M07       │
│ brand_entities│         │   taxonomy    │         │variants/cases │
└───────┬───────┘         └───────┬───────┘         └───────┬───────┘
        │                         │                         │
        ▼                         │                         │
┌───────────────┐                 │                         │
│    M01a       │                 │                         │
│  variations   │                 │                         │
└───────┬───────┘                 │                         │
        │                         │                         │
        ▼                         │                         │
┌───────────────┐                 │                         │
│    M01b       │                 │                         │
│  sub_brands   │                 │                         │
│  standards    │                 │                         │
│  manufacturer │                 │                         │
└───────┬───────┘                 │                         │
        │                         │                         │
        │                         └──────────┬──────────────┘
        │                                    │
        │                                    ▼
        │                            ┌───────────────┐
        │                            │     M08       │
        │                            │attribute_table│◀── taxonomy + variants
        │                            └───────┬───────┘     + use_cases + audiences
        │                                    │
        │                                    ▼
        │                            ┌───────────────┐
        │                            │     M09       │
        │                            │  primary_use  │◀── taxonomy + attribute_table
        │                            └───────┬───────┘
        │                                    │
        │                                    ▼
        │                            ┌───────────────┐
        │                            │     M10       │
        │                            │ validated_use │◀── M09 inputs + primary_use
        │                            └───────┬───────┘
        │                                    │
        │                                    ▼
        │                            ┌───────────────┐
        │                            │     M11       │
        │                            │hard_constraints│◀── validated_use + taxonomy
        │                            └───────┬───────┘     + attribute_table
        │                                    │
        ▼                                    │
┌─────────────────────────────────┐          │
│  BRAND SCOPE CLASSIFICATION     │          │
│                                 │          │
│  own_brand = {                  │          │
│    variations (M01a),           │          │
│    related_terms (M01b)         │          │
│  }                              │          │
│  competitors[] = same for each  │          │
│                                 │          │
│  keyword ──▶ M02 ──▶ OB?       │          │
│          ──▶ M04 ──▶ CB?       │          │
│          ──▶ M05 ──▶ NB?       │          │
│                 │               │          │
│                 ▼               │          │
│         brand_scope: OB|CB|NB   │          │
└─────────────────┬───────────────┘          │
                  │                          │
                  └──────────┬───────────────┘
                             │
                             ▼
              ┌─────────────────────────────────┐
              │   RELEVANCE CLASSIFICATION      │
              │                                 │
              │   keyword + validated_use +     │
              │   taxonomy + attribute_table +  │
              │   hard_constraints              │
              │              │                  │
              │              ▼                  │
              │   M12 (or M13→M14→M15→M16)      │
              │              │                  │
              │              ▼                  │
              │      R / S / C / N              │
              └─────────────────────────────────┘
```

### Key Dependencies

**Product Foundation (Stage 3):**
1. **M08** cannot run until M06 + M07 complete (needs taxonomy + attributes)
2. **M09** cannot run until M08 completes (needs attribute_table)
3. **M10** cannot run until M09 completes (needs primary_use)
4. **M11** cannot run until M10 completes (needs validated_use)
5. **M12-M16** cannot run until M11 completes (needs hard_constraints)

**Brand Scope Classification (Stage 2) - Two Approaches:**
6. **M02/M04/M05** (Variant A) can run independently once M01 completes for own + competitors
7. **M02_V3/M04_V3/M05_V3** (Variant B) can run independently once M01a + M01b complete for own + competitors (no M01)

---

## Two Data Flow Variants

We are testing two approaches for Brand Entity Extraction + Brand Scope Classification:

### Variant A: Original (M01 → M02/M04/M05)

```
┌─────────────────────────────────────────────────────────────────────┐
│  BRAND ENTITY EXTRACTION (Simple)                                   │
│                                                                     │
│  Product Listing ──▶ M01 ──▶ brand_entities                        │
│                        │                                            │
│                        │    (single extraction step)                │
│                        │                                            │
│                        ▼                                            │
│                  brand_entities = {                                 │
│                    brand_name,                                      │
│                    variations,                                      │
│                    related_terms                                    │
│                  }                                                  │
└─────────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│  BRAND SCOPE CLASSIFICATION (Original)                              │
│                                                                     │
│  keyword + brand_entities ──▶ M02 ──▶ OB?                          │
│                           ──▶ M04 ──▶ CB?                          │
│                           ──▶ M05 ──▶ NB?                          │
│                                  │                                  │
│                                  ▼                                  │
│                          brand_scope: OB|CB|NB                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Variant B: V3 (M01a + M01b → M02_V3/M04_V3/M05_V3)

```
┌─────────────────────────────────────────────────────────────────────┐
│  BRAND ENTITY EXTRACTION (V3 - No M01)                              │
│                                                                     │
│  brand_name ──▶ M01a ──▶ variations                                │
│                          (typos, case, phonetic)                    │
│                                                                     │
│  brand_name + listing ──▶ M01b ──▶ sub_brands                      │
│                                    searchable_standards             │
│                                    manufacturer                     │
│                                                                     │
│  own_brand = {                                                      │
│    name: "JBL",                                                     │
│    variations: "JBL, J-B-L, jbl" (from M01a),                      │
│    related_terms: "Vibe Beam, Tune" (from M01b)                    │
│  }                                                                  │
└─────────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│  BRAND SCOPE CLASSIFICATION (V3 - Dynamic Competitors)              │
│                                                                     │
│  Input format:                                                      │
│  {                                                                  │
│    keyword: "jbl earbuds",                                         │
│    own_brand: { name, variations, related_terms },                 │
│    competitors: [                                                   │
│      { name: "Apple", variations: "...", related_terms: "..." },   │
│      { name: "Sony", variations: "...", related_terms: "..." }     │
│    ]                                                                │
│  }                                                                  │
│                                                                     │
│  keyword ──▶ M02_V3 ──▶ OB? (checks own_brand only)                │
│          ──▶ M04_V3 ──▶ CB? (checks competitors[])                 │
│          ──▶ M05_V3 ──▶ NB? (confirms no brand found)              │
│                   │                                                 │
│                   ▼                                                 │
│           brand_scope: OB|CB|NB                                     │
│           + matched_term, confidence                                │
└─────────────────────────────────────────────────────────────────────┘
```

### Key Differences

| Aspect | Variant A (Original) | Variant B (V3) |
|--------|---------------------|----------------|
| Extraction steps | M01 only | M01a + M01b (no M01) |
| Variations | Basic | Extended (typos, phonetic) |
| Competitor format | Fixed slots | Dynamic array |
| Input complexity | Simpler | More structured |
| Output detail | Basic scope | + matched_term, confidence |

---

## File Naming Convention

```
braintrust_integration/v1.1/
├── prompts/
│   ├── m09_identify_primary_intended_use_v1.1.md
│   └── m09_identify_primary_intended_use_schema_v1.1.json
├── datasets/
│   └── m09_identify_primary_intended_use_v1.1.jsonl
└── docs/
    └── MODULE_REFERENCE.md
```

---

## Common Metadata Fields

| Field | Description | Example |
|-------|-------------|---------|
| `module_id` | Module identifier | "Module_09" |
| `asin` | Amazon ASIN | "B0BQPGJ9LQ" |
| `brand_name` | Product brand | "JBL" |
| `split` | Dataset split | "train" / "test" |
| `version` | Data version | "v1.1" |

---

## Test ASINs (v1.1)

| ASIN | Brand | Product |
|------|-------|---------|
| B0BQPGJ9LQ | JBL | Vibe Beam Earbuds |
| B0BZYCJK89 | Owala | FreeSip Water Bottle |
| B0CJ4WZXQF | Cisily | Kitchen Sink Caddy |
| B0D6YNWLTS | Pioneer Camp | Puffer Jacket |
| B0DSHWLXG6 | Jikasho | Phone Mount |
| B0F42MT8JX | Antarctic Star | Ice Maker |
| B000H3I2JG | REVLON | Eyeliner Pencil |
| B08J8GZXKZ | KitchenAid | Oven Mitt |
| B09LCKZBTW | WEBACOO | Bamboo Serving Tray |
| B077YYP739 | Transformers | Optimus Prime Toy |

---

## Change Log

### January 12, 2026

**Path B Schema Fix:**
- Fixed field name mismatch in M02b, M04b, M05b schemas and prompts
- Schemas were outputting `branding_scope` but datasets expected `branding_scope_1/2/3`
- Files updated:
  - `prompts/json_schemas/single/m02b_classify_own_brand_keywords_schema.json` → `branding_scope_1`
  - `prompts/json_schemas/single/m04b_classify_competitor_brand_keywords_schema.json` → `branding_scope_2`
  - `prompts/json_schemas/single/m05b_classify_nonbranded_keywords_schema.json` → `branding_scope_3`
  - Corresponding prompt files updated to match

**Analysis Tools Created:**
- `scripts/analysis/error_analyzer.py` - Automated metrics
- `scripts/analysis/pattern_detector.py` - Error pattern detection
- `scripts/analysis/llm_judge_analyzer.py` - LLM-as-Judge
- `scripts/analysis/cohens_kappa.py` - Cohen's Kappa calculator
- `scripts/analysis/braintrust_uploader.py` - Braintrust upload
- `scripts/analysis/path_comparator.py` - Path A vs B comparison
- `scripts/analysis/baseline_report.py` - Report generator

---

*Last updated: January 12, 2026*
