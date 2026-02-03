# Judge: M01 Extract Brand Entities (v2.0)

You are an expert evaluator for the M01 Extract Brand Entities module.
Your task is to evaluate whether the LLM correctly extracts brand name variations from product title.

## Evaluation Structure

You must evaluate across THREE sections:
1. **CORRECTNESS** (40 pts) - Does output match expected?
2. **RULE COMPLIANCE** (40 pts) - Are prompt rules followed?
3. **REASONING QUALITY** (20 pts) - Is reasoning sound?

**PASS Threshold**: ≥55 points (lower threshold for extraction - partial matches are valuable)
**Automatic FAIL**: Correctness=0 OR total<55

---

## Input Data

**Keyword**: {{keyword}}
**Product Title**: {{title}}
**Product Taxonomy**: {{taxonomy}}
**Expected**: {{expected_entities}}

**Model Output**:
- output: {{predicted_entities}}
- reasoning: {{predicted_reasoning}}
- confidence: {{predicted_confidence}}

---

## SECTION 1: CORRECTNESS (40 points)

This is an **EXTRACTION** module. Use TIERED SCORING with key element priority:

```
Output: {{predicted_entities}}
Expected: {{expected_entities}}
```

### Tiered Scoring Approach:

**Tier 1: Primary Element Check (25 pts)**
The original brand name (exact match from input brand_name field) is the MOST important element. Check if it's captured:
- Primary element present in output (exact or close variation) → 25 points
- Primary element missing → 0 points (caps total at 75 max)

**Tier 2: Coverage Bonus (15 pts)**
For additional elements beyond the primary:
- ≥50% of expected elements captured → +10-15 points
- 25-50% of expected elements captured → +5-10 points
- <25% of expected elements captured → +0-5 points

**IMPORTANT - Relaxed Matching**:
- Case-insensitive comparison
- Allow minor variations (e.g., "Nike" matches "nike", "NIKE")
- Semantic equivalents count (e.g., "water bottle" ≈ "bottle for water")

**Scoring Summary**:
- Primary + Good coverage (≥50%) → 35-40 points (PASS)
- Primary + Some coverage (25-50%) → 30-35 points (PASS)
- Primary + Low coverage (<25%) → 25-30 points (PASS if rules/reasoning good)
- No primary element → 0-15 points (FAIL regardless of other scores)

**CRITICAL**:
- If primary element is captured → can still PASS with rule compliance + reasoning
- If primary element is missing → automatic FAIL (max 75 pts possible)

**EXTRACTION-SPECIFIC PASS THRESHOLD**: ≥55 points (lower than boolean/classification)
For extraction tasks, we use a lower threshold because:
- Partial matches are valuable
- Capturing the primary element is the main goal
- Minor variations/extra elements should not cause FAIL

---

## SECTION 2: RULE COMPLIANCE (40 points)

Evaluate these 4 critical rules:

### Rule 1: Include Original Brand (10 pts)
**Requirement**: Must include the exact brand from input

- Did the model follow this rule?
- Evidence from output/reasoning: [quote]
- Compliant: YES/NO
- Score: 10/0

### Rule 2: Generate Variations (10 pts)
**Requirement**: Must include spelling/case variations

- Did the model follow this rule?
- Evidence from output/reasoning: [quote]
- Compliant: YES/NO
- Score: 10/0

### Rule 3: No Unrelated Terms (10 pts)
**Requirement**: No generic terms or competitor brands

- Did the model follow this rule?
- Evidence from output/reasoning: [quote]
- Compliant: YES/NO
- Score: 10/0

### Rule 4: Reasonable Count (10 pts)
**Requirement**: 3-10 variations, not excessive

- Did the model follow this rule?
- Evidence from output/reasoning: [quote]
- Compliant: YES/NO
- Score: 10/0

**Total Rule Compliance**: [sum]/40

---

## SECTION 3: REASONING QUALITY (20 points)

### 3a. Chain of Thought (8 pts)
- Clear logical progression
- Steps are traceable
- Score: 0-8

### 3b. Evidence Usage (8 pts)
- References specific input data
- Selects relevant evidence
- Score: 0-8

### 3c. Confidence Calibration (4 pts)
- Confidence matches certainty
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
- If TOTAL ≥ 55 → PASS
- If TOTAL < 55 → FAIL

---

## Output Format

Return your evaluation as JSON:

```json
{
  "evaluation": {
    "correctness": {
      "score": <0-40>,
      "output_value": "<output>",
      "expected_value": "<expected>",
      "match": <true/false>
    },
    "rule_compliance": {
      "score": <0-40>,
      "rules": [
        {"name": "Include Original Brand", "compliant": <true/false>, "score": <0/10>, "evidence": "..."},
        {"name": "Generate Variations", "compliant": <true/false>, "score": <0/10>, "evidence": "..."},
        {"name": "No Unrelated Terms", "compliant": <true/false>, "score": <0/10>, "evidence": "..."},
        {"name": "Reasonable Count", "compliant": <true/false>, "score": <0/10>, "evidence": "..."}
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
  "improvement_suggestions": ["..."]
}
```
