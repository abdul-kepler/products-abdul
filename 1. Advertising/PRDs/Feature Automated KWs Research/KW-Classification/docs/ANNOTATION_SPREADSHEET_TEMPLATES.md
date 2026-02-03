# Annotation Spreadsheet Templates for 22 Modules

## Purpose

This document provides spreadsheet templates for human annotators to validate module outputs and calculate Cohen's Kappa inter-rater reliability.

---

## Module Overview (22 Total)

### Stage 1: Brand Entity Extraction (4 modules)
| Module | Name | Output Type |
|--------|------|-------------|
| M01 | Extract Own Brand Entities | Brand object |
| M01a | Extract Own Brand Variations | Variations array |
| M01b | Extract Brand Related Terms | Related terms array |
| M03 | Generate Competitor Entities | Competitors array |

### Stage 2: Brand Scope Classification (5 modules, including V3 variants)
| Module | Name | Output Type |
|--------|------|-------------|
| M02 | Classify Own Brand Keywords | OB/null |
| M02_V3 | Classify Own Brand Keywords V3 | OB/null (refined) |
| M04 | Classify Competitor Brand Keywords | CB/null |
| M04_V3 | Classify Competitor Brand Keywords V3 | CB/null (refined) |
| M05 | Classify Non-Branded Keywords | NB/null |
| M05_V3 | Classify Non-Branded Keywords V3 | NB/null (refined) |

### Stage 3: Product Foundation (6 modules)
| Module | Name | Output Type |
|--------|------|-------------|
| M06 | Generate Product Type Taxonomy | Taxonomy object |
| M07 | Extract Product Attributes | Attributes object |
| M08 | Assign Attribute Ranks | Ranked attribute table |
| M09 | Identify Primary Intended Use | Use phrase |
| M10 | Validate Primary Intended Use | Validated use |
| M11 | Identify Hard Constraints | Constraints object |

### Stage 4: Relevance Classification (5 modules)
| Module | Name | Output Type |
|--------|------|-------------|
| M12 (Constraint) | Hard Constraint Violation Check | N/null |
| M12 (Decision) | Keyword Classification Decision | R/S/C/N |
| M13 | Product Type Check | same_type: true/false |
| M14 | Primary Use Check (Same Type) | R/N |
| M15 | Substitute Check | S/null |
| M16 | Complementary Check | C/N |

---

## Spreadsheet Template: Stage 1 - Brand Entity Extraction

### M01: Extract Own Brand Entities

| Column | Description | Values |
|--------|-------------|--------|
| A: Row ID | Unique identifier | 1, 2, 3... |
| B: ASIN | Product identifier | B0XXXXXXXXX |
| C: Product Title | Product title text | String |
| D: LLM Output - Brand Name | Model's extracted brand | String |
| E: LLM Output - Category | Model's extracted category | String |
| F: Annotator A - Brand Name | Annotator A's answer | String |
| G: Annotator A - Category | Annotator A's answer | String |
| H: Annotator B - Brand Name | Annotator B's answer | String |
| I: Annotator B - Category | Annotator B's answer | String |
| J: Brand Match (A-B) | Inter-annotator agreement | 1=Match, 0=Mismatch |
| K: Category Match (A-B) | Inter-annotator agreement | 1=Match, 0=Mismatch |
| L: Notes | Disagreement resolution | String |

**Cohen's Kappa Formula for M01:**
```
κ = (P_o - P_e) / (1 - P_e)

P_o = Observed agreement = (J column sum) / N
P_e = Expected agreement by chance
```

---

### M01a: Extract Own Brand Variations

| Column | Description | Values |
|--------|-------------|--------|
| A: Row ID | Unique identifier | 1, 2, 3... |
| B: ASIN | Product identifier | B0XXXXXXXXX |
| C: Brand Name | Input brand name | String |
| D: LLM Output - Variations | Model's variations list | Comma-separated |
| E: Annotator A - Variations | Annotator A's list | Comma-separated |
| F: Annotator B - Variations | Annotator B's list | Comma-separated |
| G: Overlap Score (A-B) | Jaccard similarity | 0.0-1.0 |
| H: Notes | Disagreement resolution | String |

**Jaccard Similarity for List Comparison:**
```
J(A,B) = |A ∩ B| / |A ∪ B|
```

---

### M01b: Extract Brand Related Terms

| Column | Description | Values |
|--------|-------------|--------|
| A: Row ID | Unique identifier | 1, 2, 3... |
| B: ASIN | Product identifier | B0XXXXXXXXX |
| C: Brand Name | Input brand name | String |
| D: LLM Output - Related Terms | Model's terms list | Comma-separated |
| E: Annotator A - Related Terms | Annotator A's list | Comma-separated |
| F: Annotator B - Related Terms | Annotator B's list | Comma-separated |
| G: Overlap Score (A-B) | Jaccard similarity | 0.0-1.0 |
| H: Notes | Disagreement resolution | String |

---

### M03: Generate Competitor Entities

| Column | Description | Values |
|--------|-------------|--------|
| A: Row ID | Unique identifier | 1, 2, 3... |
| B: ASIN | Product identifier | B0XXXXXXXXX |
| C: Category | Product category | String |
| D: LLM Output - Competitors | Model's competitor list | JSON array |
| E: Annotator A - Competitors | Annotator A's list | JSON array |
| F: Annotator B - Competitors | Annotator B's list | JSON array |
| G: Precision (A-B) | Overlap precision | 0.0-1.0 |
| H: Recall (A-B) | Overlap recall | 0.0-1.0 |
| I: Notes | Disagreement resolution | String |

---

## Spreadsheet Template: Stage 2 - Brand Scope Classification

### M02/M02_V3: Classify Own Brand Keywords

| Column | Description | Values |
|--------|-------------|--------|
| A: Row ID | Unique identifier | 1, 2, 3... |
| B: ASIN | Product identifier | B0XXXXXXXXX |
| C: Keyword | Search keyword | String |
| D: Own Brand | Brand entity JSON | JSON object |
| E: LLM Output | Model's classification | OB / null |
| F: LLM Matched Term | Term that triggered OB | String |
| G: LLM Confidence | Model's confidence | 0.0-1.0 |
| H: Annotator A | Classification | OB / null |
| I: Annotator A Reasoning | Why this classification | String |
| J: Annotator B | Classification | OB / null |
| K: Annotator B Reasoning | Why this classification | String |
| L: Agreement (A-B) | Match | 1=Match, 0=Mismatch |
| M: Notes | Resolution | String |

**Rules Applied (Reference RUBRIC_M02):**
- Rule 1: Exact brand name match
- Rule 2: Brand variation match
- Rule 3: Related term match
- Rule 4: Product line match

---

### M04/M04_V3: Classify Competitor Brand Keywords

| Column | Description | Values |
|--------|-------------|--------|
| A: Row ID | Unique identifier | 1, 2, 3... |
| B: ASIN | Product identifier | B0XXXXXXXXX |
| C: Keyword | Search keyword | String |
| D: Own Brand | Brand entity JSON | JSON object |
| E: Competitors | Competitors array | JSON array |
| F: LLM Output | Model's classification | CB / null |
| G: LLM Matched Competitor | Which competitor matched | String |
| H: LLM Confidence | Model's confidence | 0.0-1.0 |
| I: Annotator A | Classification | CB / null |
| J: Annotator A Competitor | Which competitor | String |
| K: Annotator B | Classification | CB / null |
| L: Annotator B Competitor | Which competitor | String |
| M: Agreement (A-B) | Match | 1=Match, 0=Mismatch |
| N: Notes | Resolution | String |

**Rules Applied (Reference RUBRIC_M04):**
- Rule 1: Own brand safety check (→ null)
- Rule 3: Exact competitor name match
- Rule 4: Competitor variation match
- Rule 6: Related terms match
- Rule 8: Partial word rejection (false positive)
- Rule 10: Hidden brand detection

---

### M05/M05_V3: Classify Non-Branded Keywords

| Column | Description | Values |
|--------|-------------|--------|
| A: Row ID | Unique identifier | 1, 2, 3... |
| B: ASIN | Product identifier | B0XXXXXXXXX |
| C: Keyword | Search keyword | String |
| D: Own Brand | Brand entity JSON | JSON object |
| E: Competitors | Competitors array | JSON array |
| F: LLM Output | Model's classification | NB / null |
| G: LLM Source (if null) | Why not NB | String |
| H: LLM Confidence | Model's confidence | 0.0-1.0 |
| I: Annotator A | Classification | NB / null |
| J: Annotator A Source | If null, what brand? | String |
| K: Annotator B | Classification | NB / null |
| L: Annotator B Source | If null, what brand? | String |
| M: Agreement (A-B) | Match | 1=Match, 0=Mismatch |
| N: Notes | Resolution | String |

**Rules Applied (Reference RUBRIC_M05):**
- Rules 3-5: Own brand checks
- Rules 6-7: Competitor checks
- Rules 8-12: Hidden brand detection
- Rules 13-15: Brand pattern detection
- Rules 16-17: PPC term filtering
- Rule 18: Non-branded confirmation

---

## Spreadsheet Template: Stage 3 - Product Foundation

### M06: Generate Product Type Taxonomy

| Column | Description | Values |
|--------|-------------|--------|
| A: Row ID | Unique identifier | 1, 2, 3... |
| B: ASIN | Product identifier | B0XXXXXXXXX |
| C: Product Title | Product title | String |
| D: LLM Level 1 | Primary category | String |
| E: LLM Level 2 | Subcategory | String |
| F: LLM Level 3 | Sub-subcategory | String |
| G: Annotator A Level 1 | Primary category | String |
| H: Annotator A Level 2 | Subcategory | String |
| I: Annotator B Level 1 | Primary category | String |
| J: Annotator B Level 2 | Subcategory | String |
| K: Level 1 Match (A-B) | Agreement | 1=Match, 0=Mismatch |
| L: Level 2 Match (A-B) | Agreement | 1=Match, 0=Mismatch |
| M: Notes | Resolution | String |

---

### M07: Extract Product Attributes

| Column | Description | Values |
|--------|-------------|--------|
| A: Row ID | Unique identifier | 1, 2, 3... |
| B: ASIN | Product identifier | B0XXXXXXXXX |
| C: Product Title | Product title | String |
| D: LLM Variants | Extracted variants | Comma-separated |
| E: LLM Use Cases | Extracted use cases | Comma-separated |
| F: LLM Audiences | Extracted audiences | Comma-separated |
| G: Annotator A Variants | Annotator's variants | Comma-separated |
| H: Annotator A Use Cases | Annotator's use cases | Comma-separated |
| I: Annotator A Audiences | Annotator's audiences | Comma-separated |
| J: Annotator B Variants | Annotator's variants | Comma-separated |
| K: Annotator B Use Cases | Annotator's use cases | Comma-separated |
| L: Annotator B Audiences | Annotator's audiences | Comma-separated |
| M: Variants Jaccard (A-B) | Similarity | 0.0-1.0 |
| N: Use Cases Jaccard (A-B) | Similarity | 0.0-1.0 |
| O: Audiences Jaccard (A-B) | Similarity | 0.0-1.0 |
| P: Notes | Resolution | String |

---

### M08: Assign Attribute Ranks

| Column | Description | Values |
|--------|-------------|--------|
| A: Row ID | Unique identifier | 1, 2, 3... |
| B: ASIN | Product identifier | B0XXXXXXXXX |
| C: Attribute | Attribute value | String |
| D: Attribute Type | Variant/UseCase/Audience | String |
| E: LLM Rank | Model's rank | 1, 2, 3, 4 |
| F: Annotator A Rank | Annotator A's rank | 1, 2, 3, 4 |
| G: Annotator B Rank | Annotator B's rank | 1, 2, 3, 4 |
| H: Exact Match (A-B) | Same rank | 1=Match, 0=Mismatch |
| I: Within 1 Rank (A-B) | Within ±1 | 1=Yes, 0=No |
| J: Notes | Resolution | String |

**Weighted Kappa for Ordinal Ranks:**
Use weighted Cohen's Kappa with linear or quadratic weights for rank comparisons.

---

### M09: Identify Primary Intended Use

| Column | Description | Values |
|--------|-------------|--------|
| A: Row ID | Unique identifier | 1, 2, 3... |
| B: ASIN | Product identifier | B0XXXXXXXXX |
| C: Product Title | Product title | String |
| D: LLM Primary Use | Model's use phrase | String (3-6 words) |
| E: LLM Confidence | Model's confidence | 0.0-1.0 |
| F: Annotator A Use | Annotator A's phrase | String (3-6 words) |
| G: Annotator B Use | Annotator B's phrase | String (3-6 words) |
| H: Semantic Match (A-B) | Same meaning | 1=Match, 0=Mismatch |
| I: Notes | Resolution | String |

**Semantic Matching Guidelines:**
- Phrases must convey the SAME primary function
- Word order and exact wording can differ
- Examples of matches: "portable hydration" ≈ "beverage storage on-the-go"

---

### M10: Validate Primary Intended Use

| Column | Description | Values |
|--------|-------------|--------|
| A: Row ID | Unique identifier | 1, 2, 3... |
| B: ASIN | Product identifier | B0XXXXXXXXX |
| C: Input Use (from M09) | Proposed use | String |
| D: LLM Validated Use | Model's validation | String |
| E: LLM Changes Made | What changed | String |
| F: Annotator A Validated | Annotator A's validation | String |
| G: Annotator B Validated | Annotator B's validation | String |
| H: Agreement (A-B) | Same result | 1=Match, 0=Mismatch |
| I: Notes | Resolution | String |

---

### M11: Identify Hard Constraints

| Column | Description | Values |
|--------|-------------|--------|
| A: Row ID | Unique identifier | 1, 2, 3... |
| B: ASIN | Product identifier | B0XXXXXXXXX |
| C: Product Title | Product title | String |
| D: LLM Constraints | Model's constraints | JSON object |
| E: Annotator A Constraints | Annotator A's constraints | JSON object |
| F: Annotator B Constraints | Annotator B's constraints | JSON object |
| G: Constraint Keys Match (A-B) | Same attributes identified | 1=Match, 0=Mismatch |
| H: Constraint Values Match (A-B) | Same values | 1=Match, 0=Mismatch |
| I: Notes | Resolution | String |

**Example Constraint JSON:**
```json
{"size": "32oz", "compatibility": "iPhone 15", "connectivity": "Bluetooth"}
```

---

## Spreadsheet Template: Stage 4 - Relevance Classification

### M12 (Constraint): Hard Constraint Violation Check

| Column | Description | Values |
|--------|-------------|--------|
| A: Row ID | Unique identifier | 1, 2, 3... |
| B: ASIN | Product identifier | B0XXXXXXXXX |
| C: Keyword | Search keyword | String |
| D: Hard Constraints | Product constraints | JSON object |
| E: LLM Output | Violation detected | N / null |
| F: LLM Violated Constraint | Which constraint | String |
| G: LLM Confidence | Model's confidence | 0.0-1.0 |
| H: Annotator A | Classification | N / null |
| I: Annotator A Constraint | Which constraint | String |
| J: Annotator B | Classification | N / null |
| K: Annotator B Constraint | Which constraint | String |
| L: Agreement (A-B) | Match | 1=Match, 0=Mismatch |
| M: Notes | Resolution | String |

**Rules Applied (Reference RUBRIC_M12):**
- Rules 1-4: Constraint violation (size, material, color, demographic)
- Rule 5: No constraint violation
- Range handling: Check if keyword range includes/excludes product value

---

### M12 (Decision): Keyword Classification Decision

| Column | Description | Values |
|--------|-------------|--------|
| A: Row ID | Unique identifier | 1, 2, 3... |
| B: ASIN | Product identifier | B0XXXXXXXXX |
| C: Keyword | Search keyword | String |
| D: All Context | Summary of M06-M11 outputs | String |
| E: LLM Classification | Final classification | R / S / C / N |
| F: LLM Confidence | Model's confidence | 0.0-1.0 |
| G: LLM Reasoning | Why this class | String |
| H: Annotator A | Classification | R / S / C / N |
| I: Annotator A Reasoning | Why | String |
| J: Annotator B | Classification | R / S / C / N |
| K: Annotator B Reasoning | Why | String |
| L: Agreement (A-B) | Match | 1=Match, 0=Mismatch |
| M: Notes | Resolution | String |

---

### M13: Product Type Check

| Column | Description | Values |
|--------|-------------|--------|
| A: Row ID | Unique identifier | 1, 2, 3... |
| B: ASIN | Product identifier | B0XXXXXXXXX |
| C: Keyword | Search keyword | String |
| D: Product Taxonomy | From M06 | JSON object |
| E: LLM same_type | Model's decision | true / false |
| F: LLM keyword_product_type | Extracted type | String |
| G: LLM Confidence | Model's confidence | 0.0-1.0 |
| H: Annotator A same_type | Annotator A | true / false |
| I: Annotator A type | Extracted type | String |
| J: Annotator B same_type | Annotator B | true / false |
| K: Annotator B type | Extracted type | String |
| L: Agreement (A-B) | Match | 1=Match, 0=Mismatch |
| M: Notes | Resolution | String |

---

### M14: Primary Use Check (Same Type)

| Column | Description | Values |
|--------|-------------|--------|
| A: Row ID | Unique identifier | 1, 2, 3... |
| B: ASIN | Product identifier | B0XXXXXXXXX |
| C: Keyword | Search keyword | String |
| D: Validated Use | From M10 | String |
| E: LLM same_primary_use | Model's decision | true / false |
| F: LLM Classification | Result | R / N |
| G: LLM Confidence | Model's confidence | 0.0-1.0 |
| H: Annotator A same_use | Annotator A | true / false |
| I: Annotator A Classification | Result | R / N |
| J: Annotator B same_use | Annotator B | true / false |
| K: Annotator B Classification | Result | R / N |
| L: Agreement (A-B) | Match | 1=Match, 0=Mismatch |
| M: Notes | Resolution | String |

---

### M15: Substitute Check

| Column | Description | Values |
|--------|-------------|--------|
| A: Row ID | Unique identifier | 1, 2, 3... |
| B: ASIN | Product identifier | B0XXXXXXXXX |
| C: Keyword | Search keyword | String |
| D: Validated Use | From M10 | String |
| E: LLM same_primary_use | Same primary use? | true / false |
| F: LLM Classification | Result | S / null |
| G: LLM Confidence | Model's confidence | 0.0-1.0 |
| H: Annotator A same_use | Annotator A | true / false |
| I: Annotator A Classification | Result | S / null |
| J: Annotator B same_use | Annotator B | true / false |
| K: Annotator B Classification | Result | S / null |
| L: Agreement (A-B) | Match | 1=Match, 0=Mismatch |
| M: Notes | Resolution | String |

---

### M16: Complementary Check

| Column | Description | Values |
|--------|-------------|--------|
| A: Row ID | Unique identifier | 1, 2, 3... |
| B: ASIN | Product identifier | B0XXXXXXXXX |
| C: Keyword | Search keyword | String |
| D: Product Type | From M06 | String |
| E: LLM used_together | Model's decision | true / false |
| F: LLM Classification | Result | C / N |
| G: LLM relationship_type | Relationship type | String |
| H: LLM Confidence | Model's confidence | 0.0-1.0 |
| I: Annotator A used_together | Annotator A | true / false |
| J: Annotator A Classification | Result | C / N |
| K: Annotator A relationship | Relationship type | String |
| L: Annotator B used_together | Annotator B | true / false |
| M: Annotator B Classification | Result | C / N |
| N: Annotator B relationship | Relationship type | String |
| O: Agreement (A-B) | Match | 1=Match, 0=Mismatch |
| P: Notes | Resolution | String |

---

## Cohen's Kappa Calculation Guide

### Formula
```
κ = (P_o - P_e) / (1 - P_e)

P_o = Observed agreement (proportion of matching annotations)
P_e = Expected agreement by chance
```

### Interpretation
| κ Value | Interpretation |
|---------|----------------|
| < 0.20 | Poor agreement |
| 0.21 - 0.40 | Fair agreement |
| 0.41 - 0.60 | Moderate agreement |
| 0.61 - 0.80 | Substantial agreement |
| 0.81 - 1.00 | Almost perfect agreement |

### Target for Module Validation
**κ ≥ 0.60** is required to validate that a rubric is sufficiently clear and consistent.

If κ < 0.60:
1. Identify disagreement patterns
2. Refine rubric rules
3. Re-annotate and recalculate

---

## Annotation Workflow

### Step 1: Prepare Data
1. Export sample of ASIN-keyword pairs (N=50-100 per module)
2. Populate Columns A-D with input data
3. Run LLM module to populate LLM output columns

### Step 2: Independent Annotation
1. Annotator A completes their columns without seeing Annotator B's work
2. Annotator B completes their columns without seeing Annotator A's work
3. Use rubric documents for reference

### Step 3: Calculate Agreement
1. Compute agreement column (L or similar)
2. Calculate Cohen's Kappa
3. Identify systematic disagreements

### Step 4: Resolution (if κ < 0.60)
1. Discuss disagreements
2. Update rubric with clarifications
3. Re-annotate ambiguous cases

### Step 5: Documentation
1. Record final κ value
2. Note any rubric updates
3. Archive annotated spreadsheet

---

## File Naming Convention

```
{module_id}_{version}_annotation_{date}.xlsx

Examples:
- m02_v3_annotation_2025-01-09.xlsx
- m12_constraint_annotation_2025-01-09.xlsx
- m16_complementary_annotation_2025-01-09.xlsx
```

---

## References

- `RUBRIC_M02_OWN_BRAND.md` - Rules for M02 annotation
- `RUBRIC_M04_COMPETITOR_BRAND.md` - Rules for M04 annotation
- `RUBRIC_M05_NONBRANDED.md` - Rules for M05 annotation
- `RUBRIC_M12_RELEVANCE_CLASSIFICATION.md` - Rules for M12-M16 annotation
- `Game_plan1` - Overall validation strategy
