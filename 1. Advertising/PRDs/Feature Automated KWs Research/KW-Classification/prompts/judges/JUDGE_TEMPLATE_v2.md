# Unified Judge Template v2.0

## Overview

This template defines a consistent 3-section evaluation structure for all module judges.
Each judge evaluates LLM outputs across three dimensions:

| Section | Points | Purpose | Failure Mode |
|---------|--------|---------|--------------|
| **CORRECTNESS** | 40 | Output matches expected | If NO → automatic FAIL (cap at 60 pts) |
| **RULE COMPLIANCE** | 40 | Prompt rules followed | -10 pts per violation |
| **REASONING QUALITY** | 20 | Logic is sound | Subjective assessment |

**PASS Threshold**: ≥70 points
**Automatic FAIL**: Correctness section fails OR total <70 pts

---

## Section 1: CORRECTNESS (40 points)

### For Boolean Modules (M04, M12, M13, M14, M15, M16)
```
Does the boolean output match the expected value?
- Output: {output_value}
- Expected: {expected_value}
- Match: YES/NO

Score: 40 if YES, 0 if NO
```

### For Classification Modules (M02, M12b)
```
Does the classification label match expected?
- Output: {output_classification}
- Expected: {expected_classification}
- Match: EXACT/PARTIAL/NONE

Score:
- EXACT match: 40 pts
- PARTIAL (correct category but wrong sub-label): 20 pts
- NONE: 0 pts
```

### For Extraction Modules (M01, M01a, M01b, M06, M07, M08, M09, M11)
```
How well does extracted data overlap with expected?

Metrics:
- Precision: |output ∩ expected| / |output|
- Recall: |output ∩ expected| / |expected|
- F1: 2 * (P * R) / (P + R)

Score: F1 * 40 pts

Thresholds:
- F1 ≥ 0.8: Full credit (32-40 pts)
- F1 ≥ 0.5: Partial credit (20-32 pts)
- F1 < 0.5: Low credit (0-20 pts)
```

---

## Section 2: RULE COMPLIANCE (40 points)

Each module has 4 critical rules extracted from its prompt.
**Scoring: 10 pts per rule, -10 pts per violation**

### Rule Compliance Template
```
Rule 1: [Rule Name]
- Description: [What the rule requires]
- Evidence: [Quote from output showing compliance/violation]
- Compliant: YES/NO
- Score: 10/0

Rule 2: [Rule Name]
...

Rule 3: [Rule Name]
...

Rule 4: [Rule Name]
...

Total Rule Compliance: X/40
```

### Module-Specific Rules

#### M01: Extract Brand Entities
1. **Include Original Brand** - Must include the exact brand from input
2. **Generate Variations** - Must include spelling/case variations
3. **No Unrelated Terms** - No generic terms or competitor brands
4. **Reasonable Count** - 3-10 variations, not excessive

#### M01a: Brand Variations
1. **Case Variations** - Include uppercase, lowercase, title case
2. **Common Misspellings** - Include likely typos
3. **Abbreviations** - Include shortened forms if applicable
4. **No Invented Brands** - All variations must be plausible

#### M01b: Brand Related Terms
1. **Brand Association** - Terms must be associated with brand
2. **Search Intent** - Terms people would actually search
3. **Not Competitor Terms** - No competitor brand terms
4. **Relevant to Product** - Related to brand's product category

#### M02: Brand Classification
1. **Correct Label** - OWN/COMPETITOR/NONE correctly applied
2. **Brand Detection** - Correctly identifies if brand present
3. **Case Insensitive** - Brand matching ignores case
4. **Partial Match** - Handles brand variations correctly

#### M04: Competitor Brand Check
1. **Competitor Identification** - Correctly identifies competitor brands
2. **Not Own Brand** - Own brand not flagged as competitor
3. **Market Segment** - Considers same market segment
4. **Brand Variations** - Handles brand spelling variations

#### M05: Non-Branded Keywords
1. **No Brand Terms** - Output excludes all brand terms
2. **Generic Terms Only** - Only generic product terms remain
3. **Preserve Intent** - Search intent preserved
4. **No Over-Filtering** - Doesn't remove valid generic terms

#### M06: Product Taxonomy
1. **Hierarchy Levels** - Correct parent-child relationships
2. **Primary Type First** - Most specific type at level 1
3. **Amazon Categories** - Aligns with Amazon taxonomy
4. **No Duplicates** - Each type appears once

#### M07: Attribute Extraction
1. **Correct Categories** - Attributes in right category (color, size, etc.)
2. **From Product Data** - Extracted from actual product info
3. **No Hallucination** - No invented attributes
4. **Complete Extraction** - Major attributes captured

#### M08: Attribute Ranks
1. **Relevance Ordering** - Most relevant attributes ranked higher
2. **Use Case Alignment** - Ranks match product use case
3. **No Duplicate Ranks** - Each rank used once
4. **Reasonable Distribution** - Ranks spread appropriately

#### M09: Primary Use
1. **Single Primary Use** - One main use identified
2. **From Product Data** - Based on actual product features
3. **User Perspective** - What buyer would use it for
4. **Not Too Broad** - Specific enough to be useful

#### M11: Hard Constraints
1. **Deal-Breakers Only** - Only true hard constraints
2. **From Product Specs** - Based on actual specifications
3. **Measurable** - Constraints can be verified
4. **Not Preferences** - Not soft preferences

#### M12: Hard Constraint Check
1. **Constraint Violation** - Correctly identifies violations
2. **All Constraints Checked** - Checks all listed constraints
3. **Keyword Analysis** - Analyzes keyword requirements
4. **Clear Reasoning** - Explains why violated or not

#### M12b: Final Classification
1. **Correct R/S/C/N Label** - Classification matches evidence
2. **Evidence-Based** - Classification supported by analysis
3. **Confidence Appropriate** - Confidence matches certainty
4. **Complete Reasoning** - All factors considered

#### M13: Product Type Check
1. **Brand Implies Type** - Brand-only keywords → product type
2. **Variants ≠ Types** - Size/color don't change type
3. **Function Modifiers** - "fruit tray" = "serving tray"
4. **Taxonomy Level 1** - Compare at highest taxonomy level

#### M14: Primary Use Same Type
1. **Same Type Required** - Only applies to same product types
2. **Use Case Match** - Primary uses must be compatible
3. **Not Attribute Match** - Use case, not attributes
4. **Audience Consideration** - Consider target audience

#### M15: Substitute Check
1. **Same Primary Use** - Must serve same primary function
2. **Interchangeable** - Customer would accept as alternative
3. **Same Category** - Within same product category
4. **Quality Tier** - Similar quality/price tier

#### M16: Complementary Check
1. **Co-Purchase Pattern** - Would be bought together
2. **Different Primary Use** - Different main functions
3. **Same Category ≠ Complementary** - Being in same category doesn't make complementary
4. **Actual Bundle Logic** - Would Amazon bundle these?

---

## Section 3: REASONING QUALITY (20 points)

### Evaluation Criteria

```
3a. Chain of Thought (8 pts)
- Clear logical progression: 0-4 pts
- Evidence referenced: 0-4 pts

3b. Evidence Usage (8 pts)
- Quotes from input data: 0-4 pts
- Relevant evidence selected: 0-4 pts

3c. Confidence Calibration (4 pts)
- Confidence matches certainty: 0-2 pts
- Uncertainty acknowledged when appropriate: 0-2 pts
```

### Scoring Guide
- **20 pts**: Excellent reasoning with clear logic and strong evidence
- **15 pts**: Good reasoning with minor gaps
- **10 pts**: Adequate reasoning but missing key elements
- **5 pts**: Weak reasoning with significant gaps
- **0 pts**: No reasoning or completely illogical

---

## Final Verdict Calculation

```python
def calculate_verdict(correctness, rule_compliance, reasoning):
    total = correctness + rule_compliance + reasoning

    # Automatic FAIL if correctness fails
    if correctness == 0:
        return "FAIL", min(total, 60), "Incorrect output"

    # PASS/FAIL based on total
    if total >= 70:
        return "PASS", total, "Meets threshold"
    else:
        return "FAIL", total, "Below threshold"
```

---

## Output Format

```json
{
  "evaluation": {
    "correctness": {
      "score": 40,
      "output_value": "...",
      "expected_value": "...",
      "match": true,
      "details": "..."
    },
    "rule_compliance": {
      "score": 30,
      "rules": [
        {"name": "Rule 1", "compliant": true, "score": 10, "evidence": "..."},
        {"name": "Rule 2", "compliant": true, "score": 10, "evidence": "..."},
        {"name": "Rule 3", "compliant": true, "score": 10, "evidence": "..."},
        {"name": "Rule 4", "compliant": false, "score": 0, "evidence": "..."}
      ]
    },
    "reasoning_quality": {
      "score": 15,
      "chain_of_thought": 6,
      "evidence_usage": 6,
      "confidence_calibration": 3
    }
  },
  "total_score": 85,
  "verdict": "PASS",
  "summary": "...",
  "improvement_suggestions": ["..."]
}
```

---

## Usage Instructions

1. **Identify Module Type**: Boolean, Classification, or Extraction
2. **Check Correctness First**: If output ≠ expected, cap at 60 pts max
3. **Evaluate 4 Rules**: Use module-specific rules from this template
4. **Assess Reasoning**: Score chain of thought, evidence, confidence
5. **Calculate Total**: Sum all sections
6. **Determine Verdict**: ≥70 = PASS, <70 or wrong answer = FAIL
