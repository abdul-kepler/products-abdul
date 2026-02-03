# Module Evaluation Metrics Guide

**Created:** 2026-01-09
**Purpose:** Define what metrics matter for each module type

---

## Quick Reference Matrix

| Module | Output Type | Primary Metric | Secondary Metrics | Target κ |
|--------|------------|----------------|-------------------|----------|
| M01/M01a/M01b | List | Coverage | Precision, Recall | 0.70+ |
| M02/M02_V3 | Classification | Accuracy | F1, Precision | **0.80+** |
| M03 | List | Coverage | Relevance | 0.60+ |
| M04/M04_V3 | Classification | Accuracy | F1, Precision | **0.80+** |
| M05/M05_V3 | Classification | Accuracy | F1 | 0.75+ |
| M06 | Structured | Structure Match | Depth Accuracy | 0.65+ |
| M07 | Lists | Coverage | Category Accuracy | 0.60+ |
| M08 | Ranked List | Rank Correlation | Top-3 Accuracy | 0.65+ |
| M09-M10 | Text | Semantic Match | Consistency | 0.70+ |
| M11 | List | Recall | Precision | 0.75+ |
| M12-M16 | Classification | Accuracy | Per-class F1 | **0.75+** |

---

## Detailed Module Metrics

### M01 Family: Brand Extraction

#### M01 - Extract Own Brand Entities
```
Input: {brand_name, title, bullets, description, manufacturer}
Output: {brand_entities: ["Brand", "variant1", "variant2", ...]}
```

**Metrics to evaluate:**

| Metric | Formula | Target | Why |
|--------|---------|--------|-----|
| **Canonical Coverage** | 1 if brand_name in output else 0 | 100% | MUST include the main brand |
| **Variation Recall** | len(expected ∩ output) / len(expected) | ≥60% | Most expected variations present |
| **Precision** | len(expected ∩ output) / len(output) | ≥70% | Not too many garbage entries |
| **Exact Match** | 1 if output == expected | N/A | Too strict, not useful |

**Scoring logic (implemented):**
```python
# Pass if:
# 1. Overlap ≥ 50% of expected variations, OR
# 2. Canonical brand name is present in output
```

---

#### M01a - Extract Own Brand Variations
```
Input: {brand_name, title}
Output: {variations: "Brand, brand, Brand-, ..."}
```

**Metrics:**
- **Canonical Present**: Main brand name in variations
- **Typo Coverage**: Common misspellings included
- **No False Positives**: No competitor brands mixed in

---

#### M01b - Extract Brand Related Terms
```
Input: {brand_name, title, bullets, description}
Output: {sub_brands: [], searchable_standards: [], manufacturer: ""}
```

**Metrics:**
- **Sub-brand Recall**: Known sub-brands found
- **Standards Accuracy**: Correct certifications identified
- **Manufacturer Match**: Parent company correct

---

### M02 Family: Own Brand Classification

#### M02/M02_V3 - Classify Own Brand Keywords
```
Input: {keyword, variations_own, related_terms_own}
Output: {branding_scope: "OB" | null, matched_term, confidence}
```

**This is a CRITICAL module - highest accuracy needed!**

**Metrics:**

| Metric | Formula | Target | Why |
|--------|---------|--------|-----|
| **Accuracy** | (TP + TN) / Total | ≥85% | Overall correctness |
| **OB Precision** | TP_OB / (TP_OB + FP_OB) | ≥90% | False positives hurt ad spend |
| **OB Recall** | TP_OB / (TP_OB + FN_OB) | ≥80% | Don't miss own brand keywords |
| **F1 Score** | 2 * (P * R) / (P + R) | ≥85% | Balanced metric |
| **Confidence Calibration** | Brier Score | <0.15 | Confidence reflects accuracy |

**Confusion Matrix to track:**
```
                  Actual
              OB       null
Predicted OB   TP       FP    ← FP = "jlab" marked as JBL (BAD!)
          null FN       TN    ← FN = missed "j b l" (less bad)
```

**Error Types:**
- **False Positive (FP)**: Wrong brand classified as own → WASTED AD SPEND
- **False Negative (FN)**: Own brand missed → MISSED OPPORTUNITY

---

### M04 Family: Competitor Classification

#### M04/M04_V3 - Classify Competitor Brand Keywords
```
Input: {keyword, own_brand, competitors[]}
Output: {branding_scope: "CB" | null, matched_term, matched_competitor}
```

**Metrics:**

| Metric | Target | Notes |
|--------|--------|-------|
| **Accuracy** | ≥85% | |
| **CB Precision** | ≥85% | Avoid false competitor flags |
| **CB Recall** | ≥80% | Catch competitor references |
| **Known Brand Detection** | ≥90% | Brands not in provided list |
| **IP/Character Detection** | ≥85% | Disney, Batman, etc. |

**Special checks:**
- Partial word rejection: "kitchen" ≠ KitchenAid
- Partial phrase rejection: "good" ≠ Good Grips
- Own brand exclusion: Never classify own brand as competitor

---

### M05 Family: Non-Branded Classification

#### M05/M05_V3 - Classify Non-Branded Keywords
```
Input: {keyword, variations_own, related_terms_own}
Output: {branding_scope: "NB" | null, found_term, source}
```

**Metrics:**

| Metric | Target | Notes |
|--------|--------|-------|
| **Accuracy** | ≥80% | |
| **NB Precision** | ≥85% | Don't miss hidden brands |
| **Generic Detection** | ≥90% | "silicone oven mitts" = generic |

---

### M06-M08: Product Analysis

#### M06 - Generate Product Type Taxonomy
```
Output: {taxonomy: {level_1, level_2, level_3}}
```

**Metrics:**
- **Level 1 Accuracy**: Correct top-level category
- **Hierarchy Validity**: Logical parent-child relationships
- **Depth Appropriateness**: Not too shallow/deep

#### M07 - Extract Product Attributes
```
Output: {variants: [], use_cases: [], audiences: []}
```

**Metrics:**
- **Coverage**: Key attributes captured
- **Category Accuracy**: Attributes in correct buckets
- **Relevance**: Attributes actually mentioned in listing

#### M08 - Assign Attribute Ranks
```
Output: {attribute_table: [{attribute, rank}, ...]}
```

**Metrics:**
- **Top-3 Accuracy**: Highest 3 ranks correct
- **Rank Correlation**: Spearman's ρ with expected
- **Completeness**: All attributes ranked

---

### M09-M11: Use and Constraints

#### M09 - Identify Primary Intended Use
```
Output: {primary_use: "string", confidence, reasoning}
```

**Metrics:**
- **Semantic Similarity**: Cosine similarity with expected
- **Intent Capture**: Core function identified
- **Specificity**: Not too vague ("good product")

#### M10 - Validate Primary Intended Use
```
Output: {validated_use, action: "ACCEPT"|"REVISE"|"REJECT"}
```

**Metrics:**
- **Action Accuracy**: Correct decision
- **Revision Quality**: If revised, is it better?
- **Consistency**: Same input → same output

#### M11 - Identify Hard Constraints
```
Output: {hard_constraints: ["constraint1", ...]}
```

**Metrics:**
- **Constraint Recall**: Missing a real constraint = BAD
- **Precision**: False constraints = annoying but less bad
- **Completeness**: All constraint types covered

---

### M12-M16: Classification Decision Tree

These modules make the final relevancy classification (R, S, C, N).

**Shared Metrics:**

| Metric | Target | Impact |
|--------|--------|--------|
| **Overall Accuracy** | ≥80% | Business metric |
| **R Precision** | ≥85% | False R = bad PPC targeting |
| **R Recall** | ≥80% | Missed R = lost opportunity |
| **N Precision** | ≥90% | False N = waste filtering good KWs |

**Per-Module Focus:**

| Module | Focus Question | Key Error to Avoid |
|--------|----------------|-------------------|
| M12 | Hard constraint violated? | False N (wrongly exclude) |
| M13 | Same product type? | False negative (miss synonyms) |
| M14 | Same use, same type? | Over-strict matching |
| M15 | Substitute product? | Miss near-substitutes |
| M16 | Complementary? | Over-broad C classification |

---

## Cohen's Kappa Targets by Module Priority

| Priority | Modules | Target κ | Rationale |
|----------|---------|----------|-----------|
| **Critical** | M02, M02_V3, M04, M04_V3 | 0.80+ | Direct ad spend impact |
| **High** | M05, M05_V3, M12-M16 | 0.75+ | Affects targeting decisions |
| **Medium** | M01, M09, M10, M11 | 0.70+ | Supports other modules |
| **Lower** | M01a, M01b, M03, M06-M08 | 0.60+ | Internal pipeline steps |

---

## Braintrust Scorer Configuration

For each module type, use these scorer types:

```python
# Classification modules (M02, M04, M05, M12-M16)
Scorer("ExactMatch", fields=["classification"])
Scorer("Precision", class_labels=["OB", "CB", "NB", "R", "S", "C", "N"])
Scorer("Recall", class_labels=["OB", "CB", "NB", "R", "S", "C", "N"])
Scorer("F1", class_labels=["OB", "CB", "NB", "R", "S", "C", "N"])

# List modules (M01, M03, M07)
Scorer("SetOverlap", normalize=True)
Scorer("ContainsExpected", key="canonical_brand")

# Ranked modules (M08)
Scorer("RankCorrelation", method="spearman")

# Text modules (M09, M10)
Scorer("SemanticSimilarity", model="text-embedding-3-small")
```

---

## Current Experiment Results (to update)

| Module | Samples | Accuracy | F1 | Notes |
|--------|---------|----------|-----|-------|
| M01 | 50 | TBD | - | List overlap metric |
| M01a | 50 | TBD | - | |
| M01b | 50 | TBD | - | |
| M02 | 50 | TBD | TBD | |
| M02_V3 | 50 | TBD | TBD | |
| ... | ... | ... | ... | |

*Results will be filled in after experiments complete*

---

## Action Items Based on Metrics

| Metric Result | Action |
|--------------|--------|
| Accuracy < 70% | Major prompt rewrite needed |
| Precision < Recall | Add negative examples to prompt |
| Recall < Precision | Add more positive examples |
| Confidence uncalibrated | Add confidence calibration section |
| κ < 0.60 | Consider different model or approach |
