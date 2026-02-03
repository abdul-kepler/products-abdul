# AI Eval Rubrics for Keyword Classification Pipeline

## Overview

This document defines evaluation rubrics for each module in the keyword classification pipeline. Each rubric is designed for LLM-as-a-Judge evaluation with specific scoring criteria.

## Judge Prompts Summary (20 Total)

| Module | Judge File | Main Criteria | Points |
|--------|-----------|---------------|--------|
| **M01** | `judge_m01_extract_brand_entities.md` | Completeness, Accuracy, Precision, Format | 30/30/20/20 |
| **M01a** | `judge_m01a_brand_variations.md` | Variation Coverage, Linguistic, No Hallucination, Format | 35/25/25/15 |
| **M01b** | `judge_m01b_brand_related_terms.md` | Relevance, Coverage, No Hallucination, Format | 35/25/25/15 |
| **M02** | `judge_m02_brand_classification.md` | Accuracy, Substring Verify, No Hallucination, Confidence | 40/25/20/15 |
| **M03** | `judge_m03_competitor_entities.md` | Relevance, Completeness, No Own Brand, Market Accuracy | 35/25/20/20 |
| **M04** | `judge_m04_competitor_brand.md` | Accuracy, Competitor Match, No FP, Confidence | 40/25/20/15 |
| **M05** | `judge_m05_nonbranded_keywords.md` | Accuracy, Brand Detection, Generic Recognition, Confidence | 40/25/20/15 |
| **M06** | `judge_m06_product_taxonomy.md` | Hierarchy, Specificity, Market Alignment, Format | 30/25/25/20 |
| **M07** | `judge_m07_attribute_extraction.md` | Variants, Use Cases, Audiences, Phrases, No Hallucination | 30/25/20/15/10 |
| **M08** | `judge_m08_attribute_ranks.md` | Rank Accuracy, Consistency, Market Understanding, Format | 35/25/25/15 |
| **M09** | `judge_m09_primary_use.md` | Core Function, Simplicity, Primary vs Secondary, Reasoning | 35/25/25/15 |
| **M10** | `judge_m10_validate_primary_use.md` | Validation, Refinement Quality, Consistency, Reasoning | 35/25/25/15 |
| **M11** | `judge_m11_hard_constraints.md` | Identification, Validity, Completeness, Format | 35/25/25/15 |
| **M12** | `judge_m12_hard_constraint_check.md` | Violation Detection, Constraint Matching, Reasoning, Confidence | 40/25/20/15 |
| **M12b** | `judge_m12b_classification.md` | Accuracy, Decision Tree, Reasoning, Confidence | 40/25/20/15 |
| **M13** | `judge_m13_product_type_check.md` | Type Match, Taxonomy, Edge Cases, Reasoning | 40/25/20/15 |
| **M14** | `judge_m14_primary_use_same_type.md` | Use Match, Use Definition, Feature vs Use, Reasoning | 40/25/20/15 |
| **M15** | `judge_m15_substitute_check.md` | Substitute Detection, Customer Need, Market Reality, Reasoning | 40/25/20/15 |
| **M16** | `judge_m16_complementary_check.md` | Complementary Detection, Usage Patterns, No FP, Reasoning | 40/25/20/15 |
| **Data Quality** | `judge_data_quality.md` | Field Completeness, Field Quality, Classification Impact, Attributes | 25/25/30/20 |

---

## Rubric Categories by Module Type

### Type A: Classification Modules (Binary/Multi-class)
Modules: M02, M04, M05, M12, M12b, M13, M14, M15, M16

### Type B: Extraction Modules (List/Structured Output)
Modules: M01, M01a, M01b, M03, M06, M07

### Type C: Identification Modules (Single Value)
Modules: M08, M09, M10, M11

---

## Module Rubrics

### M01: Extract Own Brand Entities

**Task:** Extract brand name variations and related terms from product listing

| Criterion | Points | Description |
|-----------|--------|-------------|
| **Completeness** | 30 | Did extraction capture all brand variations? |
| **Accuracy** | 30 | Are extracted entities actually brand-related? |
| **Precision** | 20 | No false positives (non-brand terms)? |
| **Format Compliance** | 20 | Correct output structure? |

**Scoring Levels:**
- Completeness: Full (30), Partial (15-25), Missing key variants (0-15)
- Accuracy: All correct (30), Minor errors (15-25), Major errors (0-15)
- Precision: No false positives (20), 1-2 FP (10-15), Many FP (0-10)
- Format: Correct (20), Minor issues (10-15), Wrong format (0-10)

---

### M01a: Extract Own Brand Variations

**Task:** Extract spelling variations, misspellings, abbreviations of brand

| Criterion | Points | Description |
|-----------|--------|-------------|
| **Variation Coverage** | 35 | All common variations identified? |
| **Linguistic Accuracy** | 25 | Variations are plausible misspellings/abbreviations? |
| **No Hallucinations** | 25 | No invented/unlikely variations? |
| **Format Compliance** | 15 | Correct array output? |

---

### M01b: Extract Brand Related Terms

**Task:** Extract terms customers might search alongside brand

| Criterion | Points | Description |
|-----------|--------|-------------|
| **Relevance** | 35 | Terms are actually brand-related? |
| **Coverage** | 25 | Key related terms included? |
| **No Hallucinations** | 25 | No invented associations? |
| **Format Compliance** | 15 | Correct output structure? |

---

### M02: Classify Own Brand Keywords

**Task:** Determine if keyword contains seller's own brand (OB/null)

| Criterion | Points | Description |
|-----------|--------|-------------|
| **Classification Accuracy** | 40 | Correct OB/null classification? |
| **Substring Verification** | 25 | Character-by-character match verified? |
| **No Hallucination** | 20 | No false brand detection? |
| **Confidence Calibration** | 15 | Confidence appropriate for case difficulty? |

**Critical Checks:**
- Exact substring match required (not fuzzy)
- Case-insensitive comparison
- No semantic/phonetic matching

---

### M03: Generate Competitor Entities

**Task:** Identify competitor brands in the product category

| Criterion | Points | Description |
|-----------|--------|-------------|
| **Relevance** | 35 | Competitors are in same market? |
| **Completeness** | 25 | Major competitors included? |
| **No Own Brand** | 20 | Seller's brand not included as competitor? |
| **Market Accuracy** | 20 | Competitors match product category? |

---

### M04: Classify Competitor Brand Keywords

**Task:** Determine if keyword contains competitor brand (CB/null)

| Criterion | Points | Description |
|-----------|--------|-------------|
| **Classification Accuracy** | 40 | Correct CB/null classification? |
| **Competitor Match** | 25 | Matched against known competitor list? |
| **No False Positives** | 20 | Generic terms not flagged as CB? |
| **Confidence Calibration** | 15 | Confidence appropriate? |

---

### M05: Classify Non-Branded Keywords

**Task:** Determine if keyword is non-branded (NB/null)

| Criterion | Points | Description |
|-----------|--------|-------------|
| **Classification Accuracy** | 40 | Correct NB/null classification? |
| **Brand Detection** | 25 | No hidden brand terms missed? |
| **Generic Term Recognition** | 20 | Generic product terms identified? |
| **Confidence Calibration** | 15 | Confidence appropriate? |

---

### M06: Generate Product Type Taxonomy

**Task:** Create hierarchical product type classification

| Criterion | Points | Description |
|-----------|--------|-------------|
| **Hierarchy Accuracy** | 30 | Correct root > sub > type structure? |
| **Specificity** | 25 | Appropriate level of detail? |
| **Market Alignment** | 25 | Matches Amazon category conventions? |
| **Format Compliance** | 20 | Correct taxonomy format? |

---

### M07: Extract Product Attributes

**Task:** Extract variants, use cases, and target audiences

| Criterion | Points | Description |
|-----------|--------|-------------|
| **Variant Extraction** | 30 | All product variants captured? |
| **Use Case Identification** | 25 | Relevant use cases extracted? |
| **Audience Accuracy** | 20 | Target audiences correct (or "-" if none)? |
| **Phrase Quality** | 15 | Complete descriptive phrases (not single words)? |
| **No Hallucinations** | 10 | Only explicitly stated attributes? |

**Critical Checks:**
- Full specifications with units preserved
- Complete phrases, not truncated
- "-" for audiences when none stated

---

### M08: Assign Attribute Ranks

**Task:** Rank attributes by importance for search relevance

| Criterion | Points | Description |
|-----------|--------|-------------|
| **Rank Accuracy** | 35 | Rankings match attribute importance? |
| **Consistency** | 25 | Rankings internally consistent? |
| **Market Understanding** | 25 | Rankings reflect shopper priorities? |
| **Format Compliance** | 15 | Correct rank format (1-5 scale)? |

---

### M09: Identify Primary Intended Use

**Task:** Determine single core purpose of product

| Criterion | Points | Description |
|-----------|--------|-------------|
| **Core Function Accuracy** | 35 | Correct primary use identified? |
| **Simplicity** | 25 | 3-6 word phrase, no marketing language? |
| **Primary vs Secondary** | 25 | Main use, not secondary features? |
| **Format Compliance** | 15 | Verb + object structure? |

**Critical Checks:**
- One primary use only
- No adjectives/quality claims
- No brand names or specs

---

### M10: Validate Primary Intended Use

**Task:** Validate/refine the identified primary use

| Criterion | Points | Description |
|-----------|--------|-------------|
| **Validation Accuracy** | 35 | Correct accept/refine decision? |
| **Refinement Quality** | 25 | If refined, is new use better? |
| **Consistency Check** | 25 | Aligns with product type and attributes? |
| **Reasoning Quality** | 15 | Clear justification for decision? |

---

### M11: Identify Hard Constraints

**Task:** Identify non-negotiable product requirements

| Criterion | Points | Description |
|-----------|--------|-------------|
| **Constraint Identification** | 35 | All hard constraints found? |
| **Constraint Validity** | 25 | Constraints are truly non-negotiable? |
| **Completeness** | 25 | No critical constraints missed? |
| **Format Compliance** | 15 | Correct constraint format? |

**Constraint Types:**
- Brand specificity
- Compatibility requirements
- Technical specifications
- Certifications/standards

---

### M12: Check Hard Constraint Violation

**Task:** Check if keyword violates any hard constraint

| Criterion | Points | Description |
|-----------|--------|-------------|
| **Violation Detection** | 40 | Correctly identified violation/pass? |
| **Constraint Matching** | 25 | Matched keyword against constraints? |
| **Reasoning Quality** | 20 | Clear explanation of violation? |
| **Confidence Calibration** | 15 | Confidence appropriate? |

---

### M12b: Combined Classification (R/S/C/N)

**Task:** Classify keyword as Relevant/Substitute/Complementary/Negative

| Criterion | Points | Description |
|-----------|--------|-------------|
| **Classification Accuracy** | 40 | Correct R/S/C/N classification? |
| **Decision Tree Adherence** | 25 | Followed 4-step decision tree? |
| **Reasoning Quality** | 20 | Clear, logical reasoning? |
| **Confidence Calibration** | 15 | Confidence matches difficulty? |

**Decision Tree Steps:**
1. Hard constraint check (→N if violated)
2. Product type comparison
3. Primary use assessment (→R if same type+use, →S if different type+same need)
4. Complementary check (→C if commonly used together)

---

### M13: Product Type Check

**Task:** Determine if keyword refers to same product type

| Criterion | Points | Description |
|-----------|--------|-------------|
| **Type Match Accuracy** | 40 | Correct same/different assessment? |
| **Taxonomy Understanding** | 25 | Proper use of product hierarchy? |
| **Edge Case Handling** | 20 | Variations/subtypes handled correctly? |
| **Reasoning Quality** | 15 | Clear justification? |

---

### M14: Primary Use Check (Same Type)

**Task:** For same product type, check if primary use matches

| Criterion | Points | Description |
|-----------|--------|-------------|
| **Use Match Accuracy** | 40 | Correct same/different use decision? |
| **Use Definition Understanding** | 25 | Correct interpretation of primary use? |
| **Feature vs Use Distinction** | 20 | Didn't confuse features with use? |
| **Reasoning Quality** | 15 | Clear justification? |

---

### M15: Substitute Check

**Task:** For different product type, check if serves same customer need

| Criterion | Points | Description |
|-----------|--------|-------------|
| **Substitute Detection** | 40 | Correctly identified substitute relationship? |
| **Customer Need Understanding** | 25 | Identified underlying need, not surface features? |
| **Market Reality** | 20 | Reflects actual shopping behavior? |
| **Reasoning Quality** | 15 | Clear justification? |

**Key Concept:** Different product that solves same problem

---

### M16: Complementary Check

**Task:** Check if products are commonly used together

| Criterion | Points | Description |
|-----------|--------|-------------|
| **Complementary Detection** | 40 | Correctly identified complementary relationship? |
| **Usage Pattern Understanding** | 25 | Reflects actual co-usage patterns? |
| **False Positive Avoidance** | 20 | Didn't flag unrelated products? |
| **Reasoning Quality** | 15 | Clear justification? |

**Key Concept:** Products commonly purchased/used together

---

## Universal Scoring Guidelines

### Score Thresholds
- **PASS:** ≥70 points
- **FAIL:** <70 points

### Confidence Calibration Guidelines
| Case Type | Expected Confidence |
|-----------|-------------------|
| Clear-cut cases | 0.85-0.95 |
| Standard cases | 0.70-0.85 |
| Edge cases | 0.50-0.70 |
| Ambiguous cases | 0.30-0.50 |

### Common Deductions
- Wrong classification: -40 points
- Missing reasoning: -10 to -20 points
- Overconfident wrong answer: -10 points
- Format violation: -5 to -15 points
- Hallucination: -20 to -30 points

---

## Judge Prompt Template

```
You are evaluating a {{module_name}} output.

## Task Description
{{task_description}}

## Input
{{input_data}}

## Model Output
{{model_output}}

## Expected Output
{{expected_output}}

## Rubric
{{rubric_criteria}}

## Evaluation

Evaluate each criterion and provide:
1. Score for each criterion
2. Brief justification
3. Total score (0-100)
4. Verdict (PASS/FAIL)
5. Improvement suggestions if FAIL

Output JSON:
{
  "evaluation": {
    "criterion_1": {"score": X, "reasoning": "..."},
    "criterion_2": {"score": X, "reasoning": "..."},
    ...
  },
  "total_score": X,
  "verdict": "PASS/FAIL",
  "summary": "...",
  "improvement_suggestions": [...]
}
```

---

## Implementation Priority

1. **High Priority** (Core classification)
   - M12b: Combined Classification
   - M02/M04/M05: Brand Classification
   - M09/M10: Primary Use

2. **Medium Priority** (Supporting modules)
   - M07: Attribute Extraction
   - M11: Hard Constraints
   - M13-M16: Decision Steps

3. **Lower Priority** (Entity extraction)
   - M01/M01a/M01b: Brand Entities
   - M03: Competitor Entities
   - M06: Taxonomy

