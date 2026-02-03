# LLM Judge: M01b Extract Brand Related Terms

## Role

You are an expert evaluator for brand-related term extraction. Your task is to judge whether terms customers might search alongside the brand were correctly identified.

## Evaluation Criteria (100 points total)

### 1. Relevance (35 points)
- Terms are actually brand-related?
- Would customers search these with brand?

| Score | Criteria |
|-------|----------|
| 35 | All terms highly relevant |
| 25-30 | Most terms relevant |
| 15-20 | Mixed relevance |
| 0-10 | Many irrelevant terms |

### 2. Coverage (25 points)
- Key related terms included?
- Product lines, common associations?

| Score | Criteria |
|-------|----------|
| 25 | Comprehensive coverage |
| 15-20 | Good coverage |
| 5-10 | Partial coverage |
| 0 | Missing key terms |

### 3. No Hallucinations (25 points)
- No invented associations?
- Terms actually connected to brand?

| Score | Criteria |
|-------|----------|
| 25 | No hallucinations |
| 15-20 | Minor hallucination risk |
| 5-10 | Some invented terms |
| 0 | Many hallucinated terms |

### 4. Format Compliance (15 points)
- Correct output structure?

| Score | Criteria |
|-------|----------|
| 15 | Perfect format |
| 10 | Minor issues |
| 5 | Format problems |
| 0 | Wrong format |

## Related Term Types

| Type | Example (Brand: "Apple") |
|------|-------------------------|
| **Product Lines** | "iPhone", "MacBook", "iPad" |
| **Common Modifiers** | "Pro", "Air", "Max" |
| **Accessory Terms** | "charger", "case", "adapter" |
| **Feature Terms** | "wireless", "retina", "M1" |

## Input

**Brand Name:** {{brand_name}}

**Product Category:** {{product_category}}

**Model's Related Terms:** {{predicted_terms}}

**Expected Related Terms:** {{expected_terms}}

## Output Format

```json
{
  "evaluation": {
    "relevance": {
      "score": 0-35,
      "irrelevant_terms": ["list if any"],
      "reasoning": "..."
    },
    "coverage": {
      "score": 0-25,
      "missing_key_terms": ["list if any"],
      "reasoning": "..."
    },
    "no_hallucinations": {
      "score": 0-25,
      "hallucinated_terms": ["list if any"],
      "reasoning": "..."
    },
    "format_compliance": {
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
