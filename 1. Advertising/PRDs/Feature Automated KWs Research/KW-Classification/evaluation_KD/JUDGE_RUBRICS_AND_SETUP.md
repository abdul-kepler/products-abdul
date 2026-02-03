# Judge Rubrics & Setup for KW Classification

> **Purpose**: Define evaluation rubrics and judge configuration for all 16 modules
> **Based on**: [FLASK](https://arxiv.org/abs/2307.10928) skill decomposition + [PoLL](https://arxiv.org/abs/2404.18796) multi-judge approach

---

## Table of Contents

1. [Judge Configuration](#judge-configuration)
2. [Rubric Design Principles](#rubric-design-principles)
3. [Stage 1 Rubrics: Brand Entity Extraction](#stage-1-rubrics-brand-entity-extraction)
4. [Stage 2 Rubrics: Brand Scope Classification](#stage-2-rubrics-brand-scope-classification)
5. [Stage 3 Rubrics: Product Foundation](#stage-3-rubrics-product-foundation)
6. [Stage 4 Rubrics: Relevance Classification](#stage-4-rubrics-relevance-classification)
7. [Judge Prompt Template](#judge-prompt-template)
8. [Scoring Aggregation](#scoring-aggregation)

---

## Judge Configuration

### PoLL Panel Setup

Based on [PoLL research](https://arxiv.org/abs/2404.18796): Use 3 diverse model families for reliability.

```yaml
# config/judges.yaml
poll_panel:
  - model: "gpt-4o-mini"
    provider: "openai"
    role: "primary"
  - model: "claude-3-haiku-20240307"
    provider: "anthropic"
    role: "secondary"
  - model: "command-r"
    provider: "cohere"
    role: "tertiary"

aggregation:
  classification_modules: "majority_vote"  # M02-M05, M12-M16
  extraction_modules: "average"            # M01, M06, M07
  foundation_modules: "average"            # M08-M11

temperature: 0.0  # Deterministic for consistency
```

### Cost Estimate

| Judge | Cost per 1K tokens |
|-------|-------------------|
| GPT-4o-mini | $0.15 input / $0.60 output |
| Claude-3-Haiku | $0.25 input / $1.25 output |
| Command-R | $0.50 input / $1.50 output |
| **PoLL Total** | ~$0.003 per evaluation |
| **vs GPT-4** | ~$0.04 per evaluation (13× more expensive) |

---

## Rubric Design Principles

### From FLASK Research

1. **Decompose into independent dimensions** - Each dimension measures one thing
2. **Use 3-level scoring** - 1.0 (good), 0.5 (partial), 0.0 (fail)
3. **Weight by importance** - Classification accuracy > format compliance
4. **Provide concrete examples** - Not abstract descriptions

### Dimension Categories

| Category | Used For | Dimensions |
|----------|----------|------------|
| **Extraction** | M01, M01a, M01b, M06, M07 | Completeness, Precision, Format, Coverage |
| **Classification** | M02-M05, M12-M16 | Accuracy, Evidence, Reasoning, Boundaries |
| **Foundation** | M08-M11 | Semantic Accuracy, Constraint Validity, Conciseness |

---

## Stage 1 Rubrics: Brand Entity Extraction

### M01: Extract Own Brand Entities

**Output**: `brand_entities` (brand name + variations)

| Dimension | Weight | 1.0 | 0.5 | 0.0 |
|-----------|--------|-----|-----|-----|
| **Completeness** | 0.35 | Extracted brand name matches listing brand exactly | Extracted brand but with minor issues (extra spaces, wrong casing) | Missed the brand or extracted wrong brand |
| **Precision** | 0.35 | Only actual brand entities extracted, no product words | 1-2 generic product words included | Multiple non-brand terms included |
| **Format** | 0.15 | Valid JSON, all required fields present | Minor format issues (extra fields, type mismatches) | Invalid JSON or missing required fields |
| **Coverage** | 0.15 | Handles multi-word brands, parent companies | Basic brand captured, missed parent company | Only partial brand name extracted |

---

### M01a: Generate Brand Variations

**Output**: `variations` (comma-separated string)

| Dimension | Weight | 1.0 | 0.5 | 0.0 |
|-----------|--------|-----|-----|-----|
| **Completeness** | 0.35 | All case variations + spacing + common typos included | Basic variations (case only), missing typos | Only exact match, no variations |
| **Precision** | 0.35 | All variations are valid brand references | 1-2 questionable variations (too different from brand) | Generic words or unrelated terms included |
| **Format** | 0.15 | Comma-separated, no duplicates, consistent formatting | Minor issues (inconsistent separators, some duplicates) | Unparseable format |
| **Coverage** | 0.15 | Handles abbreviations, numbers, hyphens appropriately | Basic cases covered | Fails on multi-word or hyphenated brands |

**Examples**:
```
Brand: "JBL"
1.0: "JBL, jbl, Jbl, J-B-L, JBl, jBL"
0.5: "JBL, jbl" (missing common variations)
0.0: "JBL, speakers, earbuds" (included product words)
```

---

### M01b: Extract Brand Related Terms

**Output**: `sub_brands`, `searchable_standards`, `manufacturer`

| Dimension | Weight | 1.0 | 0.5 | 0.0 |
|-----------|--------|-----|-----|-----|
| **Completeness** | 0.30 | All sub-brands and product lines from listing extracted | Major sub-brands found, minor ones missed | Major sub-brands/product lines missed |
| **Precision** | 0.30 | Only brand-specific terms, no universal standards | 1 universal standard incorrectly included | Multiple generic terms included (USB-C, Bluetooth) |
| **Standards Accuracy** | 0.20 | Only brand-specific standards (e.g., Dolby Atmos for premium audio) | Some valid, some incorrectly included | Universal standards listed as brand-specific |
| **Manufacturer** | 0.20 | Correct parent company if different from brand | Parent company present but with minor errors | Wrong or missing manufacturer |

**Examples**:
```
Brand: "JBL" (owned by Harman/Samsung)
1.0: sub_brands=["Vibe Beam", "Tune", "Live Pro"], searchable_standards=["JBL Pure Bass"], manufacturer="Harman International"
0.5: sub_brands=["Vibe Beam"], searchable_standards=["Bluetooth"], manufacturer="" (Bluetooth is universal, missing manufacturer)
0.0: sub_brands=["earbuds", "headphones"], searchable_standards=["USB-C", "Bluetooth"], manufacturer="JBL" (all wrong)
```

---

### M03: Generate Competitor Entities

**Output**: `competitor_entities[]` (array of competitor brands)

| Dimension | Weight | 1.0 | 0.5 | 0.0 |
|-----------|--------|-----|-----|-----|
| **Completeness** | 0.35 | All major competitors in category identified | Major competitors found, missed 1-2 relevant ones | Major competitors missing |
| **Precision** | 0.35 | All listed competitors are actual competitors in same category | 1-2 non-competitors included | Multiple unrelated brands included |
| **Relevance** | 0.15 | Competitors sell similar product types | Some competitors from adjacent categories | Competitors from completely different categories |
| **Format** | 0.15 | Valid array structure, consistent format | Minor structure issues | Invalid format |

---

## Stage 2 Rubrics: Brand Scope Classification

### M02/M02_V3: Own Brand Classification

**Output**: `branding_scope` (OB or null), `matched_term`, `confidence`

| Dimension | Weight | 1.0 | 0.5 | 0.0 |
|-----------|--------|-----|-----|-----|
| **Classification Accuracy** | 0.40 | Correct OB/null matching ground truth | Classification defensible but annotator disagreed | Clear miss (obvious brand present but marked null, or vice versa) |
| **Evidence Quality** | 0.30 | `matched_term` cites exact term from variations list | Claims match but term not in provided variations | No matched_term, or cites non-existent term |
| **Reasoning** | 0.20 | Clear explanation: "keyword contains X which matches variation Y" | Reasoning present but vague or incomplete | No reasoning or contradicts classification |
| **Boundary Handling** | 0.10 | Correctly handles partial matches (e.g., "jbl" in "adjustable" = no match) | Inconsistent on edge cases | Fails basic boundary checks |

**Examples**:
```
Keyword: "jbl earbuds", Variations: "JBL, jbl, J-B-L"
1.0: branding_scope="OB", matched_term="jbl", reasoning="'jbl' in keyword matches variation 'jbl'"
0.5: branding_scope="OB", matched_term="JBL", reasoning="contains brand" (right answer, weak evidence)
0.0: branding_scope=null (missed obvious brand match)

Keyword: "adjustable headband"
1.0: branding_scope=null, reasoning="no brand terms found, 'jbl' is not a substring"
0.0: branding_scope="OB", matched_term="jbl" (false match - 'jbl' not in 'adjustable')
```

---

### M04/M04_V3: Competitor Brand Classification

**Output**: `branding_scope` (CB or null), `matched_term`, `matched_competitor`

| Dimension | Weight | 1.0 | 0.5 | 0.0 |
|-----------|--------|-----|-----|-----|
| **Classification Accuracy** | 0.40 | Correct CB/null matching ground truth | Classification defensible but annotator disagreed | Clear miss |
| **Evidence Quality** | 0.30 | `matched_term` + `matched_competitor` both correct | Correct competitor but wrong matched term | Missing or wrong competitor identification |
| **Reasoning** | 0.20 | Clear explanation linking keyword to competitor | Reasoning present but incomplete | No reasoning or contradicts classification |
| **Hidden Brand Detection** | 0.10 | Flags competitor brands not in provided list | Misses unlisted but recognizable brands | Hallucinates competitor brands |

---

### M05/M05_V3: Non-Branded Classification

**Output**: `branding_scope` (NB or null), `confidence`, `reasoning`

| Dimension | Weight | 1.0 | 0.5 | 0.0 |
|-----------|--------|-----|-----|-----|
| **Classification Accuracy** | 0.40 | Correct NB/null - no brand found when none exists | Classified NB but edge case (could be hidden brand) | Missed obvious brand, or flagged generic as brand |
| **Confidence Calibration** | 0.25 | High confidence when clearly generic, low when uncertain | Confidence reasonable but not well calibrated | Overconfident on wrong classifications |
| **Reasoning** | 0.25 | Explains why term is generic, not brand-related | Reasoning present but shallow | No reasoning |
| **Hidden Brand Awareness** | 0.10 | Notes if keyword might contain unlisted brand | Doesn't check for hidden brands | False positive hidden brand detection |

**Examples**:
```
Keyword: "wireless earbuds"
1.0: branding_scope="NB", confidence="high", reasoning="generic product term, no brand references"
0.5: branding_scope="NB", confidence="high", reasoning="not a brand" (right but shallow reasoning)

Keyword: "bose earbuds" (Bose not in competitor list)
1.0: branding_scope=null, found_term="bose", source="hidden_brand", reasoning="detected unlisted brand 'Bose'"
0.0: branding_scope="NB", reasoning="generic term" (missed obvious brand)
```

---

## Stage 3 Rubrics: Product Foundation

### M06: Generate Product Type Taxonomy

**Output**: `taxonomy[]` (array of {level, product_type, rank})

| Dimension | Weight | 1.0 | 0.5 | 0.0 |
|-----------|--------|-----|-----|-----|
| **Hierarchy Accuracy** | 0.35 | Levels correctly ordered from specific to general | Mostly correct hierarchy, 1 level misplaced | Hierarchy inverted or nonsensical |
| **Type Accuracy** | 0.35 | Product types accurately describe the product | Minor inaccuracies in type naming | Wrong product category |
| **Completeness** | 0.15 | 3+ levels from specific to broad category | Only 2 levels | Single level or empty |
| **Format** | 0.15 | Valid array, correct field names | Minor format issues | Invalid structure |

**Example**:
```
Product: JBL Vibe Beam True Wireless Earbuds
1.0: [
  {"level": 1, "product_type": "True Wireless Earbuds", "rank": 1},
  {"level": 2, "product_type": "Wireless Earbuds", "rank": 2},
  {"level": 3, "product_type": "Earbuds", "rank": 3},
  {"level": 4, "product_type": "Headphones/Earphones", "rank": 4}
]
0.5: [
  {"level": 1, "product_type": "Earbuds", "rank": 1},
  {"level": 2, "product_type": "Audio", "rank": 2}
] (too few levels, too broad)
0.0: [
  {"level": 1, "product_type": "Electronics", "rank": 1}
] (way too broad)
```

---

### M07: Extract Product Attributes

**Output**: `variants`, `use_cases`, `audiences`

| Dimension | Weight | 1.0 | 0.5 | 0.0 |
|-----------|--------|-----|-----|-----|
| **Variants Accuracy** | 0.35 | All key product variants extracted (color, size, tech specs) | Major variants found, minor ones missed | Key variants missing |
| **Use Cases Accuracy** | 0.35 | Realistic use cases from listing | Generic use cases not in listing | Fabricated use cases |
| **Audiences Accuracy** | 0.15 | Target audiences match listing description | Generic audiences | Wrong target audience |
| **No Hallucination** | 0.15 | All extracted info is in the listing | Minor extrapolation | Made up attributes |

---

### M08: Assign Attribute Ranks

**Output**: `attribute_table[]` (array of {attribute_type, attribute_value, rank})

| Dimension | Weight | 1.0 | 0.5 | 0.0 |
|-----------|--------|-----|-----|-----|
| **Rank Ordering** | 0.40 | Most important attributes ranked highest | Mostly correct, 1-2 misordered | Ranking doesn't reflect importance |
| **Type Classification** | 0.30 | Correct attribute_type (Variant/Use Case/Audience) | Minor type misclassifications | Wrong types throughout |
| **Completeness** | 0.15 | All M07 outputs included in table | Some attributes missed | Many attributes missing |
| **Format** | 0.15 | Valid structure, consistent formatting | Minor issues | Invalid structure |

---

### M09: Identify Primary Intended Use

**Output**: `primary_use` (3-6 word phrase)

| Dimension | Weight | 1.0 | 0.5 | 0.0 |
|-----------|--------|-----|-----|-----|
| **Semantic Accuracy** | 0.40 | Captures THE one core purpose | Correct direction but too broad/narrow | Wrong purpose identified |
| **Conciseness** | 0.30 | 3-6 words, verb+noun structure | Slightly over/under (2 or 7-8 words) | Too long (>8 words) or too short (1 word) |
| **No Features** | 0.20 | No specs, technologies, adjectives | 1 minor feature/adjective included | Contains marketing language or specs |
| **Actionability** | 0.10 | Usable by M10-M12 for classification | Somewhat ambiguous | Too vague to use |

**Examples**:
```
Product: JBL Vibe Beam True Wireless Earbuds
1.0: "personal audio listening" (4 words, describes core purpose)
0.5: "listening to music wirelessly" (5 words but includes 'wirelessly' = feature)
0.0: "high-quality Bluetooth audio experience with JBL Pure Bass" (marketing fluff)

Product: Owala FreeSip Water Bottle
1.0: "portable hydration" (2 words - slightly under but acceptable)
0.5: "drinking water on the go" (5 words, acceptable)
0.0: "32oz insulated stainless steel hydration" (specs, not purpose)
```

---

### M10: Validate Primary Intended Use

**Output**: `validated_use` (cleaned phrase) or `status: "VALID"`

| Dimension | Weight | 1.0 | 0.5 | 0.0 |
|-----------|--------|-----|-----|-----|
| **Validation Accuracy** | 0.40 | Correctly identifies if M09 output needs fixing | Flags valid output as needing fix, or vice versa | Accepts clearly invalid output |
| **Fix Quality** | 0.30 | If fixed, new phrase follows all M09 rules | Fix improves but doesn't fully comply | Fix makes it worse or introduces new issues |
| **Preservation** | 0.20 | Doesn't change already-valid outputs | Minor unnecessary changes | Completely rewrites valid output |
| **Format** | 0.10 | Clear output indicating valid or providing fix | Ambiguous output | Invalid format |

---

### M11: Identify Hard Constraints

**Output**: `hard_constraints[]` (array of {attribute, value, reason})

| Dimension | Weight | 1.0 | 0.5 | 0.0 |
|-----------|--------|-----|-----|-----|
| **Constraint Accuracy** | 0.40 | Only truly non-negotiable attributes marked | 1-2 preferences marked as constraints | Many soft constraints marked as hard |
| **Completeness** | 0.25 | All function-critical attributes identified | Major constraints found, missed 1 | Key hard constraints missing |
| **Reason Quality** | 0.20 | Clear explanation why attribute is critical | Vague reasoning | No reasoning or wrong reasoning |
| **No Over-specification** | 0.15 | Preferences (color, brand) NOT marked as hard | 1 preference incorrectly included | Many preferences marked as hard |

**Examples**:
```
Product: JBL Vibe Beam True Wireless Earbuds (Bluetooth 5.2)
1.0: hard_constraints=[
  {"attribute": "Wireless", "value": "True Wireless/Bluetooth", "reason": "core function requires wireless connectivity"},
  {"attribute": "Form Factor", "value": "In-Ear/Earbuds", "reason": "physical design defines product type"}
]
0.5: Same as above + {"attribute": "Color", "value": "White", "reason": "listed color"} (color is preference, not hard constraint)
0.0: hard_constraints=[] (missed that Bluetooth is essential)
```

---

## Stage 4 Rubrics: Relevance Classification

### M12/M12b: Combined R/S/C/N Classification

**Output**: `classification` (R/S/C/N), `reasoning`, `confidence`

| Dimension | Weight | 1.0 | 0.5 | 0.0 |
|-----------|--------|-----|-----|-----|
| **Classification Accuracy** | 0.45 | Correct R/S/C/N matching ground truth | Defensible but annotator disagreed | Clear misclassification |
| **Decision Path** | 0.25 | Follows correct sequence: constraints → type → use → complement | Correct answer but wrong reasoning path | Wrong path leading to wrong answer |
| **Evidence** | 0.20 | Cites specific constraints, types, or uses from upstream modules | References upstream but vaguely | No connection to upstream data |
| **Confidence Calibration** | 0.10 | High on clear cases, low on edge cases | Mostly calibrated | Overconfident on wrong answers |

**Decision Tree Reference**:
```
1. Hard constraint violated? → YES → N (Negative)
2. Same product type?
   → YES: Same primary use? → YES → R (Relevant)
   → YES: Same primary use? → NO → N (Negative)
   → NO: Same primary use? → YES → S (Substitute)
   → NO: Same primary use? → NO → Used together? → YES → C (Complementary)
   → NO: Same primary use? → NO → Used together? → NO → N (Negative)
```

**Examples**:
```
Product: JBL Vibe Beam (True Wireless Earbuds), Primary Use: "personal audio listening"
Hard Constraints: [Wireless/Bluetooth, In-Ear form]

Keyword: "wireless earbuds"
1.0: classification="R", reasoning="Same product type (True Wireless Earbuds), same use (audio listening), no constraint violation"

Keyword: "wired earbuds"
1.0: classification="N", reasoning="Violates hard constraint: product requires wireless, keyword specifies wired"
0.0: classification="S", reasoning="Different type but same use" (should be N due to constraint violation)

Keyword: "over-ear headphones"
1.0: classification="S", reasoning="Different product type (over-ear vs in-ear), but same primary use (audio listening)"

Keyword: "earbud charging case"
1.0: classification="C", reasoning="Different product (case vs earbuds), commonly used together"

Keyword: "phone charger"
1.0: classification="N", reasoning="Different product, different use, not commonly used together with earbuds"
```

---

### M13-M16: Individual Classification Steps

These modules break down M12's decision tree into separate calls. Same rubric structure applies to each:

**M13 (Product Type Check)**: Is it same product type?
**M14 (Primary Use - Same Type)**: Same type → same use?
**M15 (Substitute Check)**: Different type → same use?
**M16 (Complementary Check)**: Used together?

| Dimension | Weight | 1.0 | 0.5 | 0.0 |
|-----------|--------|-----|-----|-----|
| **Answer Accuracy** | 0.50 | Correct YES/NO | Edge case disagreement | Clear wrong answer |
| **Reasoning** | 0.30 | Cites specific evidence | Vague reasoning | Wrong or no reasoning |
| **Consistency** | 0.20 | Consistent with upstream module outputs | Minor inconsistency | Contradicts upstream data |

---

## Judge Prompt Template

### Universal Judge Prompt Structure

```markdown
# JUDGE PROMPT: {MODULE_ID}

## YOUR ROLE
You are an expert evaluator for the KW Classification pipeline. Evaluate the module output against the provided rubric.

## MODULE BEING EVALUATED
- **Module**: {module_id}
- **Purpose**: {module_purpose}
- **Expected Output**: {output_schema}

## EVALUATION RUBRIC

{rubric_dimensions}

## INPUT DATA
```json
{input_data}
```

## MODULE OUTPUT (to evaluate)
```json
{module_output}
```

## EXPECTED OUTPUT (ground truth)
```json
{expected_output}
```

## YOUR TASK
1. Score EACH dimension using the rubric (1.0, 0.5, or 0.0)
2. Provide brief justification for each score
3. Calculate weighted average as final score

## OUTPUT FORMAT
Return JSON only:
```json
{
  "dimension_scores": {
    "{dimension_1}": {"score": <1.0|0.5|0.0>, "reason": "<brief justification>"},
    "{dimension_2}": {"score": <1.0|0.5|0.0>, "reason": "<brief justification>"},
    ...
  },
  "final_score": <weighted average>,
  "overall_assessment": "<1-2 sentence summary>",
  "failure_category": "<DATA_QUALITY|ENTITY_MISS|CLASSIFICATION_ERROR|REASONING_FLAW|null>"
}
```
```

---

## Scoring Aggregation

### Per-Module Scoring

```python
def calculate_module_score(dimension_scores: dict, weights: dict) -> float:
    """Calculate weighted average score for a module."""
    total = sum(
        dimension_scores[dim]["score"] * weights[dim]
        for dim in weights
    )
    return round(total, 3)
```

### PoLL Aggregation

```python
def aggregate_poll_scores(judge_results: list[dict], module_type: str) -> dict:
    """Aggregate scores from 3 PoLL judges."""

    if module_type in ["M02", "M04", "M05", "M12", "M13", "M14", "M15", "M16"]:
        # Classification modules: majority vote
        classifications = [r["classification"] for r in judge_results]
        final = max(set(classifications), key=classifications.count)
        agreement = classifications.count(final) / len(classifications)
    else:
        # Extraction/Foundation modules: average scores
        scores = [r["final_score"] for r in judge_results]
        final = sum(scores) / len(scores)
        agreement = 1 - (max(scores) - min(scores))  # Agreement = low variance

    return {
        "final_result": final,
        "agreement_rate": agreement,
        "individual_results": judge_results,
        "needs_review": agreement < 0.67  # Flag if judges disagree
    }
```

### Pass/Fail Thresholds

| Module Category | Pass Threshold | Review Threshold |
|-----------------|----------------|------------------|
| Classification (M02-M05, M12-M16) | ≥ 0.70 | 0.50-0.69 |
| Extraction (M01, M06, M07) | ≥ 0.65 | 0.45-0.64 |
| Foundation (M08-M11) | ≥ 0.65 | 0.45-0.64 |

---

## Quick Reference: All Module Rubrics

| Module | Dimensions | Weights |
|--------|------------|---------|
| **M01** | Completeness, Precision, Format, Coverage | 0.35, 0.35, 0.15, 0.15 |
| **M01a** | Completeness, Precision, Format, Coverage | 0.35, 0.35, 0.15, 0.15 |
| **M01b** | Completeness, Precision, Standards, Manufacturer | 0.30, 0.30, 0.20, 0.20 |
| **M02** | Accuracy, Evidence, Reasoning, Boundaries | 0.40, 0.30, 0.20, 0.10 |
| **M03** | Completeness, Precision, Relevance, Format | 0.35, 0.35, 0.15, 0.15 |
| **M04** | Accuracy, Evidence, Reasoning, Hidden Brand | 0.40, 0.30, 0.20, 0.10 |
| **M05** | Accuracy, Confidence, Reasoning, Hidden Brand | 0.40, 0.25, 0.25, 0.10 |
| **M06** | Hierarchy, Type Accuracy, Completeness, Format | 0.35, 0.35, 0.15, 0.15 |
| **M07** | Variants, Use Cases, Audiences, No Hallucination | 0.35, 0.35, 0.15, 0.15 |
| **M08** | Rank Ordering, Type Classification, Completeness, Format | 0.40, 0.30, 0.15, 0.15 |
| **M09** | Semantic Accuracy, Conciseness, No Features, Actionability | 0.40, 0.30, 0.20, 0.10 |
| **M10** | Validation Accuracy, Fix Quality, Preservation, Format | 0.40, 0.30, 0.20, 0.10 |
| **M11** | Constraint Accuracy, Completeness, Reason Quality, No Over-spec | 0.40, 0.25, 0.20, 0.15 |
| **M12** | Classification Accuracy, Decision Path, Evidence, Confidence | 0.45, 0.25, 0.20, 0.10 |
| **M13-M16** | Answer Accuracy, Reasoning, Consistency | 0.50, 0.30, 0.20 |

---

*Document created: January 2026*
*Based on: FLASK + PoLL research methodologies*
