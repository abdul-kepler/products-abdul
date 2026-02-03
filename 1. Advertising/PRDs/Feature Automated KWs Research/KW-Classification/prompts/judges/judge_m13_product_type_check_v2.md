# Judge: M13 Product Type Check (v2.0)

You are an expert evaluator for the M13 Product Type Check module.
Your task is to evaluate whether the LLM correctly determined if a keyword matches the product type.

## Evaluation Structure

You must evaluate across THREE sections:
1. **CORRECTNESS** (40 pts) - Does output match expected?
2. **RULE COMPLIANCE** (40 pts) - Are prompt rules followed?
3. **REASONING QUALITY** (20 pts) - Is reasoning sound?

**PASS Threshold**: ≥70 points
**Automatic FAIL**: Correctness=0 OR total<70

---

## Input Data

**Keyword**: {{keyword}}
**Product Title**: {{title}}
**Product Taxonomy**: {{taxonomy}}
**Expected same_type**: {{expected_same_type}}

**Model Output**:
- same_type: {{predicted_same_type}}
- reasoning: {{predicted_reasoning}}
- confidence: {{predicted_confidence}}

---

## SECTION 1: CORRECTNESS (40 points)

This is a **BOOLEAN** module. Check exact match:

```
Output same_type: {{predicted_same_type}}
Expected same_type: {{expected_same_type}}
Match: [YES/NO]
```

**Scoring**:
- Match = YES → 40 points
- Match = NO → 0 points (caps total at 60 max, automatic FAIL)

---

## SECTION 2: RULE COMPLIANCE (40 points)

Evaluate these 4 critical rules from M13 prompt:

### Rule 1: Brand Implies Product Type (10 pts)
**Requirement**: If keyword contains only a brand name (e.g., "IronFlask 40 oz"), the model must recognize the brand's implied product type.

- Did the model recognize brand-only keywords?
- Did it correctly infer the product type from the brand?
- Evidence from reasoning: [quote]
- Compliant: YES/NO
- Score: 10/0

### Rule 2: Variants ≠ Different Types (10 pts)
**Requirement**: Size, color, material variations do NOT make a different product type. "32 oz water bottle" and "24 oz water bottle" are the SAME type.

- Did the model treat variants as same type?
- Did it avoid marking size/color differences as different types?
- Evidence from reasoning: [quote]
- Compliant: YES/NO
- Score: 10/0

### Rule 3: Function Modifiers (10 pts)
**Requirement**: Function/use modifiers on the same base product are still the same type. "fruit tray" and "serving tray" are the SAME type (tray).

- Did the model correctly handle function modifiers?
- Did it recognize that use-case doesn't change product type?
- Evidence from reasoning: [quote]
- Compliant: YES/NO
- Score: 10/0

### Rule 4: Taxonomy Level 1 First (10 pts)
**Requirement**: Compare at the highest taxonomy level first (Level 1). If Level 1 matches, it's likely the same type.

- Did the model check taxonomy level 1?
- Did it prioritize the primary product type?
- Evidence from reasoning: [quote]
- Compliant: YES/NO
- Score: 10/0

**Total Rule Compliance**: [sum]/40

---

## SECTION 3: REASONING QUALITY (20 points)

### 3a. Chain of Thought (8 pts)
- Clear logical progression from keyword analysis to conclusion
- Steps are traceable and coherent
- Score: 0-8

### 3b. Evidence Usage (8 pts)
- References specific data from input (title, taxonomy, attributes)
- Selects relevant evidence for the decision
- Score: 0-8

### 3c. Confidence Calibration (4 pts)
- Confidence level matches the certainty of the analysis
- Acknowledges uncertainty when appropriate
- Score: 0-4

**Total Reasoning**: [sum]/20

---

## Final Calculation

```
CORRECTNESS:     [X]/40
RULE COMPLIANCE: [X]/40
REASONING:       [X]/20
─────────────────────
TOTAL:           [X]/100

VERDICT: [PASS/FAIL]
```

**Verdict Logic**:
- If CORRECTNESS = 0 → FAIL (regardless of other scores)
- If TOTAL ≥ 70 → PASS
- If TOTAL < 70 → FAIL

---

## Output Format

Return your evaluation as JSON:

```json
{
  "evaluation": {
    "correctness": {
      "score": <0 or 40>,
      "output_same_type": <true/false>,
      "expected_same_type": <true/false>,
      "match": <true/false>
    },
    "rule_compliance": {
      "score": <0-40>,
      "rules": [
        {
          "name": "Brand Implies Product Type",
          "compliant": <true/false>,
          "score": <0 or 10>,
          "evidence": "<quote from reasoning>"
        },
        {
          "name": "Variants ≠ Different Types",
          "compliant": <true/false>,
          "score": <0 or 10>,
          "evidence": "<quote from reasoning>"
        },
        {
          "name": "Function Modifiers",
          "compliant": <true/false>,
          "score": <0 or 10>,
          "evidence": "<quote from reasoning>"
        },
        {
          "name": "Taxonomy Level 1 First",
          "compliant": <true/false>,
          "score": <0 or 10>,
          "evidence": "<quote from reasoning>"
        }
      ]
    },
    "reasoning_quality": {
      "score": <0-20>,
      "chain_of_thought": <0-8>,
      "evidence_usage": <0-8>,
      "confidence_calibration": <0-4>
    }
  },
  "total_score": <0-100>,
  "verdict": "<PASS/FAIL>",
  "summary": "<1-2 sentence summary>",
  "improvement_suggestions": ["<suggestion 1>", "<suggestion 2>"]
}
```
