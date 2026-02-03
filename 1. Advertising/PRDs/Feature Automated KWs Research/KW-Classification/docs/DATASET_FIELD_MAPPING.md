# Dataset Field Mapping v1.1

Complete field reference for all 22 modules in the Keyword Classification Pipeline.

---

## Table of Contents

1. [Brand Extraction Modules (M01-M01b, M03)](#brand-extraction-modules-m01-m01b)
2. [Brand Classification Modules (M02-M05b)](#brand-classification-modules-m02-m05b)
3. [Product Analysis Modules (M06-M08)](#product-analysis-modules-m06-m08)
4. [Use & Constraint Modules (M09-M11)](#use--constraint-modules-m09-m11)
5. [Relevancy Classification Modules (M12-M16)](#relevancy-classification-modules-m12-m16)
6. [Common Fields Reference](#common-fields-reference)
7. [Data Types & Formats](#data-types--formats)
8. [Supplementary Datasets](#supplementary-datasets)

---

## Brand Extraction Modules (M01-M01b, M03)

### M01: ExtractOwnBrandEntities

Extracts brand-related entities from product listing.

**Dataset:** `m01_extract_own_brand_entities.jsonl`

| Field | Location | Type | Description |
|-------|----------|------|-------------|
| `brand_name` | input | string | Primary brand name from Amazon catalog |
| `title` | input | string | Product title |
| `bullet_points` | input | string | Feature bullets (newline-separated) |
| `description` | input | string | Product description |
| `manufacturer` | input | string | Manufacturer name |
| `brand_entities` | expected | array[string] | List of brand-related terms to extract |

**Example Input:**
```json
{
  "input": {
    "brand_name": "KitchenAid",
    "title": "KitchenAid Asteroid Oven Mitt 2-Pack Set",
    "bullet_points": "HEAT RESISTANT – KitchenAid Silicone...",
    "description": "Perform your kitchen tasks safely...",
    "manufacturer": "Lifetime Brands"
  },
  "expected": {
    "brand_entities": ["KitchenAid", "Kitchen Aid"]
  }
}
```

---

### M01a: ExtractOwnBrandVariations

Generates search variations of brand name (typos, truncations, phonetic).

**Dataset:** `m01a_extract_own_brand_variations.jsonl`

| Field | Location | Type | Description |
|-------|----------|------|-------------|
| `brand_name` | input | string | Primary brand name |
| `variations` | expected | array[string] | Common misspellings, truncations, phonetic variations |

**Example Input:**
```json
{
  "input": {
    "brand_name": "KitchenAid"
  },
  "expected": {
    "variations": ["kitchenaid", "kitchen aid", "kitchenaide", "kitchn aid"]
  }
}
```

---

### M01b: ExtractBrandRelatedTerms

Extracts sub-brands, product lines, technologies, and manufacturer info.

**Dataset:** `m01b_extract_brand_related_terms.jsonl`

| Field | Location | Type | Description |
|-------|----------|------|-------------|
| `brand_name` | input | string | Primary brand name |
| `title` | input | string | Product title |
| `bullet_points` | input | string | Feature bullets |
| `description` | input | string | Product description |
| `manufacturer` | input | string | Manufacturer name |
| `sub_brands` | expected | array[string] | Product lines, technologies, sub-brands |
| `searchable_standards` | expected | array[string] | Industry standards (e.g., "FDA approved") |
| `manufacturer` | expected | string | Extracted manufacturer name |

**Example Input:**
```json
{
  "input": {
    "brand_name": "Sony",
    "title": "Sony WH-1000XM5 Wireless Headphones",
    "bullet_points": "LDAC Hi-Res Audio...",
    "description": "Industry-leading noise cancellation...",
    "manufacturer": "Sony Corporation"
  },
  "expected": {
    "sub_brands": ["WH-1000XM5", "LDAC"],
    "searchable_standards": ["Hi-Res Audio"],
    "manufacturer": "Sony Corporation"
  }
}
```

---

### M03: GenerateCompetitorEntities

Extracts competitor brand entities based on product context.

**Dataset:** `m03_generate_competitor_entities.jsonl`

| Field | Location | Type | Description |
|-------|----------|------|-------------|
| `brand_name` | input | string | Primary brand name (own brand) |
| `title` | input | string | Product title |
| `bullet_points` | input | string | Feature bullets |
| `description` | input | string | Product description |
| `product_type` | input | string | Amazon product type code |
| `category_root` | input | string | Root category |
| `category_sub` | input | string | Sub-category |
| `known_competitor_brands` | input | array[string] | Known competitors from catalog |
| `competitor_entities` | expected | array[string] | List of competitor brand names |

**Example Input:**
```json
{
  "input": {
    "brand_name": "KitchenAid",
    "title": "KitchenAid Oven Mitt 2-Pack",
    "bullet_points": "Heat resistant silicone...",
    "description": "Professional-grade oven mitts...",
    "product_type": "OVEN_MITT",
    "category_root": "Home & Kitchen",
    "category_sub": "Oven Mitts",
    "known_competitor_brands": ["OXO", "Le Creuset"]
  },
  "expected": {
    "competitor_entities": ["OXO", "Le Creuset", "Cuisinart"]
  }
}
```

---

## Brand Classification Modules (M02-M05b)

### M02: ClassifyOwnBrandKeywords (Path A)

Classifies if keyword matches own brand entities.

**Dataset:** `m02_classify_own_brand_keywords.jsonl`

| Field | Location | Type | Description |
|-------|----------|------|-------------|
| `keyword` | input | string | Search keyword to classify |
| `brand_entities` | input | array[string] | Brand entities from M01 |
| `branding_scope_1` | expected | boolean | `true` if keyword is own-brand |

**Example:**
```json
{
  "input": {
    "keyword": "kitchenaid oven mitts",
    "brand_entities": ["KitchenAid", "Kitchen Aid"]
  },
  "expected": {
    "branding_scope_1": true
  }
}
```

---

### M02b: ClassifyOwnBrandKeywords (Path B)

Path B uses variations + related terms instead of brand_entities.

**Dataset:** `m02b_classify_own_brand_keywords.jsonl`

| Field | Location | Type | Description |
|-------|----------|------|-------------|
| `keyword` | input | string | Search keyword to classify |
| `variations_own` | input | array[string] | Brand variations from M01a |
| `related_terms_own` | input | object | Related terms from M01b |
| `branding_scope_1` | expected | boolean | `true` if keyword is own-brand |

---

### M04: ClassifyCompetitorBrandKeywords (Path A)

Classifies if keyword matches competitor brand.

**Dataset:** `m04_classify_competitor_brand_keywords.jsonl`

| Field | Location | Type | Description |
|-------|----------|------|-------------|
| `keyword` | input | string | Search keyword to classify |
| `competitor_entities` | input | array[string] | Competitor brand entities |
| `own_brand` | input | string | Own brand name (to exclude) |
| `branding_scope_2` | expected | boolean | `true` if keyword is competitor-brand |

---

### M04b: ClassifyCompetitorBrandKeywords (Path B)

Path B uses structured competitor data.

**Dataset:** `m04b_classify_competitor_brand_keywords.jsonl`

| Field | Location | Type | Description |
|-------|----------|------|-------------|
| `keyword` | input | string | Search keyword to classify |
| `competitors` | input | array[object] | List of competitor objects with variations/terms |
| `own_brand` | input | string | Own brand name |
| `branding_scope_2` | expected | boolean | `true` if keyword is competitor-brand |

**Competitor Object Structure:**
```json
{
  "brand_name": "OXO",
  "variations": ["oxo", "o x o"],
  "related_terms": ["Good Grips"]
}
```

---

### M05: ClassifyNonBrandedKeywords (Path A)

Classifies if keyword is non-branded (generic).

**Dataset:** `m05_classify_nonbranded_keywords.jsonl`

| Field | Location | Type | Description |
|-------|----------|------|-------------|
| `keyword` | input | string | Search keyword to classify |
| `brand_entities` | input | array[string] | Own brand entities |
| `competitor_entities` | input | array[string] | Competitor brand entities |
| `branding_scope_3` | expected | boolean | `true` if keyword is non-branded |

---

### M05b: ClassifyNonBrandedKeywords (Path B)

Path B uses structured brand data.

**Dataset:** `m05b_classify_nonbranded_keywords.jsonl`

| Field | Location | Type | Description |
|-------|----------|------|-------------|
| `keyword` | input | string | Search keyword to classify |
| `own_brand` | input | object | Own brand with variations/terms |
| `competitors` | input | array[object] | Competitor objects |
| `branding_scope_3` | expected | boolean | `true` if keyword is non-branded |

---

## Product Analysis Modules (M06-M08)

### M06: GenerateProductTypeTaxonomy

Generates hierarchical product type taxonomy.

**Dataset:** `m06_generate_product_type_taxonomy.jsonl`

| Field | Location | Type | Description |
|-------|----------|------|-------------|
| `title` | input | string | Product title |
| `bullet_points` | input | string | Feature bullets |
| `description` | input | string | Product description |
| `product_type` | input | string | Amazon product type code |
| `category_root` | input | string | Root category (e.g., "Home & Kitchen") |
| `category_sub` | input | string | Sub-category (e.g., "Oven Mitts") |
| `taxonomy` | expected | array[object] | Hierarchical taxonomy |

**Taxonomy Object Structure:**
```json
{
  "level": 1,
  "product_type": "Oven Mitt",
  "rank": 1
}
```

**Example Expected:**
```json
{
  "taxonomy": [
    {"level": 1, "product_type": "Oven Mitt", "rank": 1},
    {"level": 2, "product_type": "Kitchen Safety Equipment", "rank": 2},
    {"level": 3, "product_type": "Kitchen Accessories", "rank": 3}
  ]
}
```

---

### M07: ExtractProductAttributes

Extracts product variants, use cases, and audiences.

**Dataset:** `m07_extract_product_attributes.jsonl`

| Field | Location | Type | Description |
|-------|----------|------|-------------|
| `title` | input | string | Product title |
| `bullet_points` | input | string | Feature bullets |
| `description` | input | string | Product description |
| `product_type` | input | string | Amazon product type |
| `category_root` | input | string | Root category |
| `category_sub` | input | string | Sub-category |
| `color` | input | string | Product color |
| `size` | input | string | Product size |
| `material` | input | string | Product material |
| `style` | input | string | Product style |
| `target_audience` | input | string | Target audience |
| `specific_uses` | input | string | Specific uses |
| `model` | input | string | Model number |
| `item_form` | input | string | Item form |
| `number_of_items` | input | string | Number of items |
| `included_components` | input | string | Included components |
| `variants` | expected | array[string] | Product variants/features |
| `use_cases` | expected | array[string] | Use cases |
| `audiences` | expected | array[string] | Target audiences |

---

### M08: AssignAttributeRanks

Assigns importance ranks to extracted attributes.

**Dataset:** `m08_assign_attribute_ranks.jsonl`

| Field | Location | Type | Description |
|-------|----------|------|-------------|
| `title` | input | string | Product title |
| `bullet_points` | input | string | Feature bullets |
| `description` | input | string | Product description |
| `taxonomy` | input | array[object] | From M06 |
| `variants` | input | array[string] | From M07 |
| `use_cases` | input | array[string] | From M07 |
| `audiences` | input | array[string] | From M07 |
| `attribute_table` | expected | array[object] | Ranked attributes |

**Attribute Table Object Structure:**
```json
{
  "attribute_type": "Use Case",
  "attribute_value": "Handling Hot Cookware",
  "rank": 1
}
```

**Attribute Types:**
- `Variant` - Product features/characteristics
- `Use Case` - How the product is used
- `Audience` - Target user groups

---

## Use & Constraint Modules (M09-M11)

### M09: IdentifyPrimaryIntendedUse

Determines the core purpose of the product.

**Dataset:** `m09_identify_primary_intended_use_v1.1.jsonl`

| Field | Location | Type | Description |
|-------|----------|------|-------------|
| `title` | input | string | Product title |
| `bullet_points` | input | string | Feature bullets |
| `description` | input | string | Product description |
| `taxonomy` | input | array[object] | From M06 |
| `attribute_table` | input | array[object] | From M08 |
| `product_attributes` | input | object | Raw product attributes |
| `primary_use` | expected | string | Single core use phrase |

**Example Expected:**
```json
{
  "primary_use": "Heat protection when handling hot cookware"
}
```

---

### M10: ValidatePrimaryIntendedUse

Validates and refines the primary use phrase.

**Dataset:** `m10_validate_primary_intended_use_v1.1.jsonl`

| Field | Location | Type | Description |
|-------|----------|------|-------------|
| `title` | input | string | Product title |
| `bullet_points` | input | string | Feature bullets |
| `description` | input | string | Product description |
| `taxonomy` | input | array[object] | From M06 |
| `attribute_table` | input | array[object] | From M08 |
| `product_attributes` | input | object | Raw product attributes |
| `primary_use` | input | string | From M09 |
| `validated_use` | expected | string | Cleaned/validated use phrase |

---

### M11: IdentifyHardConstraints

Identifies non-negotiable product attributes.

**Dataset:** `m11_identify_hard_constraints_v1.1.jsonl`

| Field | Location | Type | Description |
|-------|----------|------|-------------|
| `title` | input | string | Product title |
| `bullet_points` | input | string | Feature bullets |
| `description` | input | string | Product description |
| `validated_use` | input | string | From M10 |
| `taxonomy` | input | array[object] | From M06 |
| `attribute_table` | input | array[object] | From M08 |
| `product_attributes` | input | object | Raw product attributes |
| `hard_constraints` | expected | array[string] | Non-negotiable attributes |

**Example Expected:**
```json
{
  "hard_constraints": ["Heat Resistant up to 500°F", "Size: 7\"x13\""]
}
```

---

## Relevancy Classification Modules (M12-M16)

These modules classify keyword-to-product relevancy. All share similar input structure.

### Common Input Fields (M12-M16)

| Field | Type | Description |
|-------|------|-------------|
| `keyword` | string | Search keyword to classify |
| `title` | string | Product title |
| `bullet_points` | string | Feature bullets |
| `description` | string | Product description |
| `validated_use` | string | From M10 |
| `taxonomy` | array[object] | From M06 |
| `attribute_table` | array[object] | From M08 |
| `product_attributes` | object | Raw product attributes |
| `hard_constraints` | array[string] | From M11 |

---

### M12: HardConstraintViolationCheck

Checks if keyword violates any hard constraint.

**Dataset:** `m12_check_hard_constraint_v1.1.jsonl`

| Field | Location | Type | Description |
|-------|----------|------|-------------|
| *(common inputs)* | input | | See above |
| `relevancy` | expected | null/string | `null` if no violation, otherwise classification |

**Output Fields:**
- `violates_constraint`: boolean
- `violated_constraint`: string or null
- `relevancy`: null (continues to next module) or "N" (negative)
- `confidence`: float (0.0-1.0)
- `reasoning`: string

---

### M12b: CombinedClassification

Combined decision tree for full R/S/C/N classification.

**Dataset:** `m12b_combined_classification_v1.1.jsonl`

| Field | Location | Type | Description |
|-------|----------|------|-------------|
| *(common inputs)* | input | | See above |
| `relevancy` | expected | string | One of: R, S, C, N |

**Output Fields:**
- `step1_hard_constraint`: object with `violated`, `violated_constraint`, `reasoning`
- `step2_product_type`: object with `same_type`, `keyword_product_type`, `reasoning`
- `step3_primary_use`: object with `same_use`, `reasoning`
- `step4_complementary`: object with `used_together`, `relationship`, `reasoning`
- `relevancy`: "R" | "S" | "C" | "N"
- `confidence`: float (0.0-1.0)

**Classification Values:**
| Value | Meaning | Description |
|-------|---------|-------------|
| R | Relevant | Same product type, same primary use |
| S | Substitute | Different product type, same customer need |
| C | Complementary | Different product, commonly used together |
| N | Negative | Violates constraint, different use, or unrelated |

---

### M13: ProductTypeCheck

Checks if keyword asks for the same product type.

**Dataset:** `m13_check_product_type_v1.1.jsonl`

| Field | Location | Type | Description |
|-------|----------|------|-------------|
| *(common inputs)* | input | | See above |
| `same_type` | expected | boolean | `true` if same product type |

**Output Fields:**
- `same_type`: boolean
- `keyword_product_type`: string
- `reasoning`: string
- `confidence`: float

---

### M14: PrimaryUseCheckSameType

Checks if same-type product supports same primary use.

**Dataset:** `m14_check_primary_use_same_type_v1.1.jsonl`

| Field | Location | Type | Description |
|-------|----------|------|-------------|
| *(common inputs)* | input | | See above |
| `relevancy` | expected | string | "R" (relevant) or "N" (negative) |

**Output Fields:**
- `same_primary_use`: boolean
- `keyword_primary_use`: string
- `relevancy`: "R" | "N"
- `reasoning`: string
- `confidence`: float

---

### M15: SubstituteCheck

Checks if different product type serves same customer need.

**Dataset:** `m15_check_substitute_v1.1.jsonl`

| Field | Location | Type | Description |
|-------|----------|------|-------------|
| *(common inputs)* | input | | See above |
| `relevancy` | expected | string | "S" (substitute) or continues |

**Output Fields:**
- `is_substitute`: boolean
- `same_customer_need`: boolean
- `keyword_product_type`: string
- `relevancy`: "S" | null
- `reasoning`: string
- `confidence`: float

---

### M16: ComplementaryCheck

Checks if product is commonly used together with ASIN.

**Dataset:** `m16_check_complementary_v1.1.jsonl`

| Field | Location | Type | Description |
|-------|----------|------|-------------|
| *(common inputs)* | input | | See above |
| `relevancy` | expected | string | "C" (complementary) or "N" (negative) |

**Output Fields:**
- `used_together`: boolean
- `relationship`: string (how they're used together)
- `relevancy`: "C" | "N"
- `reasoning`: string
- `confidence`: float

---

## Common Fields Reference

### Metadata Fields

All datasets include metadata for tracking:

| Field | Type | Description |
|-------|------|-------------|
| `module_id` | string | Module identifier (e.g., "m12") |
| `asin` | string | Amazon ASIN |
| `brand_name` | string | Product brand |
| `split` | string | Data split: "train", "eval", "test" |
| `keyword` | string | (M02-M16) Search keyword |
| `product_type` | string | Amazon product type code |

### Product Attributes Object

Used in M09-M16:

```json
{
  "color": "Charcoal Grey",
  "size": "7\"x13\"",
  "material": "Silicone",
  "style": "Modern",
  "target_audience": "",
  "specific_uses": "",
  "model": "O2013117TDKA",
  "item_form": "",
  "number_of_items": "2",
  "included_components": "",
  "product_type": "OVEN_MITT",
  "category_root": "Home & Kitchen",
  "category_sub": "Oven Mitts"
}
```

---

## Data Types & Formats

### String Fields
- `bullet_points`: Newline-separated (`\n`) feature bullets
- `description`: Plain text, may be empty
- `keyword`: Lowercase search term

### Array Fields
- `brand_entities`: `["Brand", "brand", "BRAND"]`
- `taxonomy`: `[{level, product_type, rank}, ...]`
- `attribute_table`: `[{attribute_type, attribute_value, rank}, ...]`
- `hard_constraints`: `["Constraint 1", "Constraint 2"]`

### Boolean Expected Values
- `branding_scope_1`: Own brand match
- `branding_scope_2`: Competitor brand match
- `branding_scope_3`: Non-branded (generic)
- `same_type`: Product type match
- `violates_constraint`: Hard constraint violation

### Classification Expected Values
- `relevancy`: "R" | "S" | "C" | "N" | null

---

## Pipeline Stages & Module Dependencies

The pipeline has 4 stages with 2 paths (A and B) for different approaches:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  STAGE 1: Brand Entity Extraction                                           │
│                                                                             │
│  ┌─────────────────────────┐        ┌──────────────────────────────────┐    │
│  │ Path A:                 │   OR   │ Path B:                          │    │
│  │  M01 (own brand)        │        │  M01a (brand variations)         │    │
│  │  M03 (competitors)      │        │  M01b (brand related terms)      │    │
│  └─────────────────────────┘        └──────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STAGE 2: Brand Scope Classification → Output: OB / CB / NB                 │
│                                                                             │
│  ┌─────────────────────────┐        ┌──────────────────────────────────┐    │
│  │ Path A:                 │   OR   │ Path B:                          │    │
│  │  M02 (own brand)        │        │  M02b (own brand)                │    │
│  │  M04 (competitor)       │        │  M04b (competitor)               │    │
│  │  M05 (non-branded)      │        │  M05b (non-branded)              │    │
│  └─────────────────────────┘        └──────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    
                                    
                                    
                                    
┌─────────────────────────────────────────────────────────────────────────────┐
│  STAGE 3: Product Definition & Taxonomy (ASIN-level, run once per product)  │
│                                                                             │
│  M06 (taxonomy)      M07 (attributes) ──► M08 (attribute ranks)             │
│                                                │                            │
│                                                ▼                            │
│                                          M09 (primary use)                  │
│                                                │                            │
│                                                ▼                            │
│                                          M10 (validate use)                 │
│                                                │                            │
│                                                ▼                            │
│                                          M11 (hard constraints)             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STAGE 4: Relevance Classification → Output: R / S / C / N                  │
│                                                                             │
│  ┌─────────────────────────────────┐   ┌────────────────────────────────┐  │
│  │ Path A (step-by-step):          │   │ Path B (combined):             │  │
│  │  M12 (hard constraint check)    │   │  M12b (single-pass decision)   │  │
│  │   │                             │   │                                │  │
│  │   ▼                             │   │  Includes all checks:          │  │
│  │  M13 (product type check)       │   │  - Hard constraint             │  │
│  │   │                             │   │  - Product type                │  │
│  │   ▼                             │   │  - Primary use                 │  │
│  │  M14 (primary use same type)    │   │  - Substitute                  │  │
│  │   │                             │   │  - Complementary               │  │
│  │   ▼                             │OR │                                │  │
│  │  M15 (substitute check)         │   │                                │  │
│  │   │                             │   │                                │  │
│  │   ▼                             │   │                                │  │
│  │  M16 (complementary check)      │   │                                │  │
│  └─────────────────────────────────┘   └────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow Summary

| Stage | Input | Output | Scope |
|-------|-------|--------|-------|
| **Stage 1** | Product listing (title, bullets, description) | Brand entities or variations | Per ASIN |
| **Stage 2** | Keyword + Brand entities | OB / CB / NB classification | Per keyword |
| **Stage 3** | Product listing + attributes | Taxonomy, use, constraints | Per ASIN |
| **Stage 4** | Keyword + Stage 3 outputs | R / S / C / N classification | Per keyword |

### Path Selection Guide

| Use Case | Stage 1 | Stage 2 | Stage 4 |
|----------|---------|---------|---------|
| **Simple brand matching** | Path A (M01+M03) | Path A (M02/M04/M05) | Path A or B |
| **Fuzzy brand matching** | Path B (M01a+M01b) | Path B (M02b/M04b/M05b) | Path A or B |
| **Quick classification** | Either | Either | Path B (M12b) |
| **Detailed classification** | Either | Either | Path A (M12→M16) |

---

## Supplementary Datasets

Some modules have supplementary datasets (`_sd_1` suffix) with identical field structure:

| Main Dataset | Supplementary Dataset |
|-------------|----------------------|
| `m06_generate_product_type_taxonomy.jsonl` | `m06_generate_product_type_taxonomy_sd_1.jsonl` |
| `m07_extract_product_attributes.jsonl` | `m07_extract_product_attributes_sd_1.jsonl` |
| `m08_assign_attribute_ranks.jsonl` | `m08_assign_attribute_ranks_sd_1.jsonl` |

These supplementary datasets contain additional product samples for evaluation but use the same input/expected field structure as documented above.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v1.1.1 | 2026-01-16 | Added missing M03 GenerateCompetitorEntities documentation |
| v1.1 | 2026-01 | Added M12b combined classification, standardized relevancy field |
| v1.0 | 2025-12 | Initial 16-module pipeline |
