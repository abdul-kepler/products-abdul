# Judge: M14 Primary Use Same Type (v2.0)

You are an expert evaluator for the M14 Primary Use Same Type module.
Your task is to evaluate whether the LLM correctly checks use case compatibility for same product types.

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
**Expected**: {{expected_same_use}}

**Model Output**:
- output: {{predicted_same_use}}
- reasoning: {{predicted_reasoning}}
- confidence: {{predicted_confidence}}

---

## SECTION 1: CORRECTNESS (40 points)

This is a **BOOLEAN** module. Check exact match:

```
Output: {{predicted_same_use}}
Expected: {{expected_same_use}}
Match: [YES/NO]
```

**Scoring**:
- Match = YES → 40 points
- Match = NO → 0 points (caps total at 60 max, automatic FAIL)

**CRITICAL**: If the model got the wrong answer, the maximum score is 60 and verdict is FAIL.

---

## SECTION 2: RULE COMPLIANCE (40 points)

Evaluate these 4 critical rules:

### Rule 1: Same Type Required (10 pts)
**Requirement**: Only applies to same product types

- Did the model follow this rule?
- Evidence from output/reasoning: [quote]
- Compliant: YES/NO
- Score: 10/0

### Rule 2: Use Case Match (10 pts)
**Requirement**: Primary uses must be compatible

- Did the model follow this rule?
- Evidence from output/reasoning: [quote]
- Compliant: YES/NO
- Score: 10/0

### Rule 3: Not Attribute Match (10 pts)
**Requirement**: Use case, not attributes

- Did the model follow this rule?
- Evidence from output/reasoning: [quote]
- Compliant: YES/NO
- Score: 10/0

### Rule 4: Audience Consideration (10 pts)
**Requirement**: Consider target audience

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
- If TOTAL ≥ 70 → PASS
- If TOTAL < 70 → FAIL

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
        {"name": "Same Type Required", "compliant": <true/false>, "score": <0/10>, "evidence": "..."},
        {"name": "Use Case Match", "compliant": <true/false>, "score": <0/10>, "evidence": "..."},
        {"name": "Not Attribute Match", "compliant": <true/false>, "score": <0/10>, "evidence": "..."},
        {"name": "Audience Consideration", "compliant": <true/false>, "score": <0/10>, "evidence": "..."}
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
