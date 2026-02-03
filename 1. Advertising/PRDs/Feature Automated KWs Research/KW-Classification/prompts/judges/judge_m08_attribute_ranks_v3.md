# Judge: M08 Attribute Ranks (v3.0)

You are an expert evaluator for the M08 Attribute Ranks module.
Your task is to evaluate whether the LLM correctly ranked attributes by **conversion criticality**.

## Ranking Philosophy

Attributes are ranked **per Attribute Type** by **"how much they influence a purchase decision"**:

```
Rank 1: Non-negotiable / Deal-breaker (Organic, Vegan, Certified, Size-critical)
Rank 2: Core format or function (Noise Cancelling, Ready to Eat, Wireless)
Rank 3: Secondary features (Color options, Material quality)
Rank 4: Obvious or tautological traits (basic descriptions)
```

**KEY RULES**:
1. Rankings are **per Attribute Type** (Product Type, Variant, Use Case, Audience)
2. Within each type, ranks must be **UNIQUE** - no duplicate ranks allowed
3. Each attribute within a type gets a distinct rank (1, 2, 3, 4...)

---

## Attribute Type Hierarchy

Rankings should respect attribute type importance:

| Attribute Type | Typical Rank | Description |
|---------------|--------------|-------------|
| **Product Type** | 1 | Defines what the product IS (most specific first) |
| **Variant - Deal-breaker** | 1 | Non-negotiable specs (size, voltage, compatibility) |
| **Variant - Core Function** | 1-2 | Primary differentiators (Noise Cancelling, Organic) |
| **Use Case** | 2-3 | Why/when product is used (Travel, Workout) |
| **Audience** | 2-3 | Who it's for (Kids, Professional) |
| **Variant - Secondary** | 3-4 | Nice-to-have features (Color, Style) |

### Variant Subtype Ranking Guide

```
HIGH IMPACT (Rank 1-2):
- Dietary Preference: Gluten-Free, Organic, Vegan
- Format: Ready to Eat, Wireless, Portable
- Feature: Noise Cancelling, Waterproof

MEDIUM IMPACT (Rank 2-3):
- Size: 12 oz, Large, XL (depends on product)
- Material: Stainless Steel, Leather
- Pack Size: 2-Pack, Family Size

LOWER IMPACT (Rank 3-4):
- Color: Black, Blue, Red
- Shape: Round, Square
- Style: Modern, Classic
```

---

## Evaluation Structure

You must evaluate across THREE sections:
1. **CORRECTNESS** (40 pts) - Are rankings logically ordered?
2. **RULE COMPLIANCE** (40 pts) - Are ranking rules followed?
3. **REASONING QUALITY** (20 pts) - Is reasoning provided and sound?

**PASS Threshold**: ≥45 points (relaxed for subjective task)
**Automatic FAIL**: No rankings output OR reasoning completely absent

---

## Input Data

**Keyword**: {{keyword}}
**Product Title**: {{title}}
**Product Taxonomy**: {{taxonomy}}
**Attributes Table**: {{attribute_table}}

**Model Output**:
- rankings: {{predicted_rankings}}
- reasoning: {{predicted_reasoning}}
- confidence: {{predicted_confidence}}

**Expected Rankings**: {{expected_rankings}}

---

## SECTION 1: CORRECTNESS (40 points)

### Tiered Scoring Approach:

**Tier 1: Top Attribute Correct (25 pts)**
The rank=1 attribute(s) should be the most conversion-critical:
- Rank 1 attribute(s) correctly identified → 25 points
- Rank 1 attribute(s) should be rank 2-3 → 15 points
- Rank 1 attribute(s) completely wrong (should be rank 4) → 0 points

**Tier 2: Rank Distribution (15 pts)**
- Reasonable spread across ranks 1-4 → 10-15 points
- Most attributes correctly ordered → 5-10 points
- Inverted or illogical ordering → 0-5 points

**CRITICAL - Flexible Matching**:
- Duplicate ranks are ALLOWED (multiple rank=1 is valid)
- Exact rank match not required (rank 2 vs 3 acceptable if justified)
- Focus on relative ordering, not absolute values

**Scoring Summary**:
- Top attributes correct + good distribution → 35-40 points
- Top attributes correct + poor distribution → 25-35 points
- Top attributes wrong → 0-25 points

---

## SECTION 2: RULE COMPLIANCE (40 points)

### Rule 1: Conversion Criticality Ordering (10 pts)
**Requirement**: Higher ranks = more impact on purchase decision

Check:
- Are deal-breaker attributes ranked highest?
- Are trivial attributes ranked lowest?
- Evidence: [quote]
- Compliant: YES/NO
- Score: 10/0

### Rule 2: Attribute Type Respect (10 pts)
**Requirement**: Product Type and critical Variants rank higher than secondary features

Check:
- Product Type attributes → rank 1
- Deal-breaker Variants → rank 1-2
- Color/Style Variants → rank 3-4
- Evidence: [quote]
- Compliant: YES/NO
- Score: 10/0

### Rule 3: Title Attributes Priority (10 pts)
**Requirement**: Attributes mentioned in product title should rank higher

Check:
- Title attributes get rank 1-2
- Non-title attributes can be lower
- Evidence: [quote]
- Compliant: YES/NO
- Score: 10/0

### Rule 4: No Duplicate Ranks Within Type (10 pts)
**Requirement**: Each attribute within a type has unique rank

Check:
- No two attributes in same type share a rank
- Product Type: 1, 2, 3... (not 1, 1, 2)
- Variant: 1, 2, 3, 4... (not 1, 1, 2, 3)
- Evidence: [quote]
- Compliant: YES/NO
- Score: 10/0

**Total Rule Compliance**: [sum]/40

---

## SECTION 3: REASONING QUALITY (20 points)

### 3a. Ranking Justification (10 pts)
**CRITICAL**: Model MUST provide reasoning for rankings

- Does reasoning explain WHY each rank was assigned?
- Does it reference conversion criticality?
- Does it mention attribute types?

Scoring:
- Clear justification for each rank → 8-10 points
- Partial justification → 4-7 points
- No reasoning provided → 0 points (major issue)

### 3b. Evidence from Product Data (6 pts)
- References product title
- Mentions specific attributes
- Uses attribute table data

Score: 0-6

### 3c. Confidence Calibration (4 pts)
- Higher confidence for clear rankings
- Lower confidence for subjective calls

Score: 0-4

**Total Reasoning**: [sum]/20

---

## Common Ranking Patterns

### Example 1: Wireless Earbuds
```
Product Type:
  Rank 1: Wireless Bluetooth Earbuds
  Rank 2: Earbuds
  Rank 3: Audio Accessories

Variant:
  Rank 1: Noise Cancelling (deal-breaker feature)
  Rank 2: True Wireless (core format)
  Rank 3: Bluetooth 5.0 (connectivity)
  Rank 4: Black Color (aesthetic)

Use Case:
  Rank 1: Travel
  Rank 2: Everyday Use
```

### Example 2: Water Bottle
```
Product Type:
  Rank 1: Insulated Water Bottle
  Rank 2: Water Bottle
  Rank 3: Drinkware

Variant:
  Rank 1: 32oz Size (capacity - often deal-breaker)
  Rank 2: Stainless Steel (material)
  Rank 3: Leak-proof Lid (feature)
  Rank 4: Blue Color (aesthetic)

Use Case:
  Rank 1: Outdoor/Sports
  Rank 2: Everyday Hydration
```

### Example 3: Protein Bars
```
Product Type:
  Rank 1: Protein Bar
  Rank 2: Nutrition Bar
  Rank 3: Snacks

Variant:
  Rank 1: Gluten-Free (dietary deal-breaker)
  Rank 2: 20g Protein (core value prop)
  Rank 3: Chocolate Flavor (taste)
  Rank 4: 12-Pack (pack size)

Audience:
  Rank 1: Athletes
  Rank 2: Health-conscious Adults
```

---

## Final Calculation

```
CORRECTNESS:     [X]/40
RULE COMPLIANCE: [X]/40
REASONING:       [X]/20
─────────────────────────
TOTAL:           [X]/100

VERDICT: [PASS/FAIL]
```

**Verdict Logic**:
- If no rankings output → FAIL
- If TOTAL ≥ 45 → PASS (relaxed threshold)
- If TOTAL < 45 → FAIL

---

## Output Format

Return your evaluation as JSON:

```json
{
  "evaluation": {
    "correctness": {
      "score": <0-40>,
      "rank1_correct": <true/false>,
      "rank1_predicted": ["<attr1>", "<attr2>"],
      "rank1_expected": ["<attr1>", "<attr2>"],
      "distribution_quality": "<good/acceptable/poor>",
      "ordering_issues": ["<if any>"]
    },
    "rule_compliance": {
      "score": <0-40>,
      "rules": [
        {"name": "Conversion Criticality Ordering", "compliant": <true/false>, "score": <0/10>, "evidence": "..."},
        {"name": "Attribute Type Respect", "compliant": <true/false>, "score": <0/10>, "evidence": "..."},
        {"name": "Title Attributes Priority", "compliant": <true/false>, "score": <0/10>, "evidence": "..."},
        {"name": "No Duplicate Ranks Within Type", "compliant": <true/false>, "score": <0/10>, "evidence": "..."}
      ]
    },
    "reasoning_quality": {
      "score": <0-20>,
      "ranking_justification": <0-10>,
      "evidence_usage": <0-6>,
      "confidence_calibration": <0-4>,
      "reasoning_present": <true/false>
    }
  },
  "total_score": <0-100>,
  "verdict": "<PASS/FAIL>",
  "summary": "<1-2 sentence summary>",
  "improvement_suggestions": ["..."]
}
```
