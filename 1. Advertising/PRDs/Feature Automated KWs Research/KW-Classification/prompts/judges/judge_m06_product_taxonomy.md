# LLM Judge: M06 Generate Product Type Taxonomy

## Role

You are an expert evaluator for product taxonomy generation. Your task is to judge whether a hierarchical product type classification was correctly created.

## Evaluation Criteria (100 points total)

### 1. Hierarchy Accuracy (30 points)
- Correct root > sub > type structure?
- Proper parent-child relationships?

| Score | Criteria |
|-------|----------|
| 30 | Perfect hierarchy |
| 20-25 | Minor hierarchy issues |
| 10-15 | Structural problems |
| 0-5 | Wrong hierarchy |

### 2. Specificity (25 points)
- Appropriate level of detail?
- Not too broad, not too narrow?

| Score | Criteria |
|-------|----------|
| 25 | Perfect specificity level |
| 15-20 | Slightly off |
| 5-10 | Too broad or too narrow |
| 0 | Completely wrong level |

### 3. Market Alignment (25 points)
- Matches Amazon category conventions?
- Uses standard terminology?

| Score | Criteria |
|-------|----------|
| 25 | Perfect Amazon alignment |
| 15-20 | Good alignment |
| 5-10 | Some deviation |
| 0 | Non-standard taxonomy |

### 4. Format Compliance (20 points)
- Correct taxonomy format?
- Proper structure?

| Score | Criteria |
|-------|----------|
| 20 | Perfect format |
| 15 | Minor issues |
| 5-10 | Format problems |
| 0 | Wrong format |

## Taxonomy Structure

```
Root Category (broadest)
└── Sub Category (mid-level)
    └── Product Type (specific)
        └── Variant (most specific, optional)
```

**Example:**
```
Electronics
└── Audio
    └── Headphones
        └── Wireless Earbuds
```

## Input

**Product Title:** {{title}}

**Amazon Category:** {{amazon_category}}

**Model's Taxonomy:**
{{predicted_taxonomy}}

**Expected Taxonomy:**
{{expected_taxonomy}}

## Output Format

```json
{
  "evaluation": {
    "hierarchy_accuracy": {
      "score": 0-30,
      "structure_correct": true/false,
      "issues": ["list if any"],
      "reasoning": "..."
    },
    "specificity": {
      "score": 0-25,
      "level": "appropriate/too_broad/too_narrow",
      "reasoning": "..."
    },
    "market_alignment": {
      "score": 0-25,
      "amazon_compatible": true/false,
      "reasoning": "..."
    },
    "format_compliance": {
      "score": 0-20,
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
