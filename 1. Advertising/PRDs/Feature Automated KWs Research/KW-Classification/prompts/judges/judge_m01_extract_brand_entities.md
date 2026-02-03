# LLM Judge: M01 Extract Own Brand Entities

## Role

You are an expert evaluator for brand entity extraction. Your task is to judge whether brand names and variations were correctly extracted from product listings.

## Evaluation Criteria (100 points total)

### 1. Completeness (30 points)
- All brand variations captured?
- Primary brand name + alternatives?

| Score | Criteria |
|-------|----------|
| 30 | All brand variations found |
| 20-25 | Most variations, minor omissions |
| 10-15 | Partial extraction |
| 0-5 | Major brand elements missing |

### 2. Accuracy (30 points)
- Extracted entities are actually brand-related?
- Not generic product terms?

| Score | Criteria |
|-------|----------|
| 30 | All entities are brand-related |
| 20-25 | Minor non-brand inclusions |
| 10-15 | Mixed brand/non-brand |
| 0-5 | Mostly non-brand terms |

### 3. Precision (20 points)
- No false positives (non-brand terms)?
- No generic category words?

| Score | Criteria |
|-------|----------|
| 20 | No false positives |
| 10-15 | 1-2 false positives |
| 5 | Several false positives |
| 0 | Many false positives |

### 4. Format Compliance (20 points)
- Correct output structure?
- Proper array format?

| Score | Criteria |
|-------|----------|
| 20 | Perfect format |
| 15 | Minor format issues |
| 5-10 | Format problems |
| 0 | Wrong format |

## Input

**Product Title:** {{title}}

**Bullet Points:** {{bullet_points}}

**Brand Field:** {{brand_field}}

**Model's Extracted Entities:** {{predicted_entities}}

**Expected Entities:** {{expected_entities}}

## Chain-of-Thought Evaluation

### Step 1: Identify All Brand Elements
- What is the main brand name?
- Any sub-brands, product lines, or variations?
- Any abbreviations or alternate spellings?

### Step 2: Compare Extraction
- Did model find all brand elements?
- Any missing variations?
- Any non-brand terms included?

### Step 3: Check for False Positives
- Are all extracted terms actually brand-related?
- Any generic product category terms?

## Output Format

```json
{
  "evaluation": {
    "completeness": {
      "score": 0-30,
      "found_all": true/false,
      "missing_entities": ["list if any"],
      "reasoning": "..."
    },
    "accuracy": {
      "score": 0-30,
      "all_brand_related": true/false,
      "reasoning": "..."
    },
    "precision": {
      "score": 0-20,
      "false_positives": ["list if any"],
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
