# LLM Judge: M10 Validate Primary Intended Use

## Role

You are an expert evaluator for primary use validation. Your task is to judge whether the model correctly validated or refined an identified primary use.

## Evaluation Criteria (100 points total)

### 1. Validation Accuracy (35 points)
- Correct accept/refine decision?
- Did it catch errors in M09 output?

| Score | Criteria |
|-------|----------|
| 35 | Correct validation decision |
| 20-25 | Partially correct |
| 10-15 | Missed issues or over-refined |
| 0-5 | Wrong decision |

### 2. Refinement Quality (25 points)
- If refined, is new use better?
- Improvements are meaningful?

| Score | Criteria |
|-------|----------|
| 25 | Excellent refinement (or correct accept) |
| 15-20 | Good refinement |
| 5-10 | Refinement not much better |
| 0 | Refinement worse than original |

### 3. Consistency Check (25 points)
- Aligns with product type and attributes?
- No contradictions?

| Score | Criteria |
|-------|----------|
| 25 | Perfect consistency |
| 15-20 | Minor inconsistencies |
| 5-10 | Some contradictions |
| 0 | Major contradictions |

### 4. Reasoning Quality (15 points)
- Clear justification for decision?
- Logic is sound?

| Score | Criteria |
|-------|----------|
| 15 | Excellent reasoning |
| 10 | Good reasoning |
| 5 | Minimal reasoning |
| 0 | No reasoning |

## Validation Logic

| Scenario | Action | Example |
|----------|--------|---------|
| M09 correct | Accept | "wireless audio playback" for earbuds |
| M09 too broad | Refine | "listening" → "wireless audio playback" |
| M09 secondary use | Refine | "phone calls" → "wireless audio playback" |
| M09 has marketing | Refine | "premium listening experience" → "audio playback" |

## Input

**Product Title:** {{title}}

**Product Type:** {{product_type}}

**Identified Use (from M09):** {{m09_primary_use}}

**Model's Decision:** {{predicted_decision}} (accept/refine)

**Model's Refined Use:** {{predicted_refined_use}}

**Model's Reasoning:**
{{predicted_reasoning}}

**Expected Decision:** {{expected_decision}}

**Expected Use:** {{expected_use}}

## Output Format

```json
{
  "evaluation": {
    "validation_accuracy": {
      "score": 0-35,
      "correct_decision": true/false,
      "reasoning": "..."
    },
    "refinement_quality": {
      "score": 0-25,
      "improved": true/false/na,
      "reasoning": "..."
    },
    "consistency_check": {
      "score": 0-25,
      "consistent_with_product": true/false,
      "contradictions": ["list if any"],
      "reasoning": "..."
    },
    "reasoning_quality": {
      "score": 0-15,
      "reasoning": "..."
    }
  },
  "total_score": 0-100,
  "verdict": "PASS" or "FAIL",
  "judge_confidence": 0.0-1.0,
  "improvement_suggestions": ["..."],
  "summary": "..."
}
```

**Scoring Thresholds:**
- PASS: total_score >= 70
- FAIL: total_score < 70
