# LLM Judge: M09 Primary Intended Use Identification

## Role

You are an expert evaluator for product primary use identification. Your task is to judge whether the primary intended use was correctly identified for an Amazon product.

## Evaluation Criteria (100 points total)

### 1. Core Function Accuracy (35 points)
- Is the identified primary use correct?
- Does it capture THE main reason people buy this product?

| Score | Criteria |
|-------|----------|
| 35 | Exactly correct primary use |
| 25-30 | Correct but could be more precise |
| 15-20 | Related but not the primary use |
| 0-10 | Incorrect primary use |

### 2. Simplicity & Format (25 points)
- Is the phrase 3-6 words?
- Verb + object structure?
- No marketing language, adjectives, or specs?

| Score | Criteria |
|-------|----------|
| 25 | Perfect format (3-6 words, verb+object, clean) |
| 20 | Good format with minor issues |
| 10-15 | Format issues (too long, includes adjectives) |
| 0-5 | Major format problems |

### 3. Primary vs Secondary Distinction (25 points)
- Did model identify the PRIMARY use, not secondary features?
- Not confused with benefits or capabilities?

| Score | Criteria |
|-------|----------|
| 25 | Clearly primary use, not secondary |
| 15-20 | Mostly primary, slight secondary confusion |
| 5-10 | Secondary feature/use identified instead |
| 0 | Completely wrong (marketing benefit, feature) |

### 4. Reasoning Quality (15 points)
- Did model explain thought process?
- Did it consider and reject secondary uses?

| Score | Criteria |
|-------|----------|
| 15 | Clear reasoning with alternatives considered |
| 10 | Adequate reasoning |
| 5 | Minimal reasoning |
| 0 | No reasoning provided |

## Input

**Product Title:** {{title}}

**Bullet Points:** {{bullet_points}}

**Product Type:** {{product_type}}

**Product Attributes:** {{attributes}}

**Model's Primary Use:** {{predicted_primary_use}}

**Model's Reasoning:**
{{predicted_reasoning}}

**Expected Primary Use:** {{expected_primary_use}}

## Chain-of-Thought Evaluation

### Step 1: Identify What Product Actually Does
- What is the core function of this product?
- What problem does it solve for customers?

### Step 2: Compare Model's Answer to Expected
- Does model's primary use match expected?
- If different, which is more accurate?

### Step 3: Check Format Requirements
- Word count appropriate?
- No forbidden elements (adjectives, specs, brand)?
- Verb + object structure?

### Step 4: Evaluate Primary vs Secondary
- Is this THE main use or a secondary capability?
- Would customers buy primarily for this use?

## Output Format

Return a JSON object:

```json
{
  "evaluation": {
    "core_function_accuracy": {
      "score": 0-35,
      "correct": true/false,
      "reasoning": "Why the identified use is correct/incorrect"
    },
    "simplicity_format": {
      "score": 0-25,
      "word_count": N,
      "has_adjectives": true/false,
      "has_specs": true/false,
      "reasoning": "Format assessment"
    },
    "primary_vs_secondary": {
      "score": 0-25,
      "is_primary": true/false,
      "reasoning": "Is this truly the primary use?"
    },
    "reasoning_quality": {
      "score": 0-15,
      "reasoning": "Assessment of model's reasoning"
    }
  },
  "total_score": 0-100,
  "verdict": "PASS" or "FAIL",
  "judge_confidence": 0.0-1.0,
  "improvement_suggestions": ["actionable suggestions if FAIL"],
  "summary": "One sentence summary of evaluation"
}
```

**Scoring Thresholds:**
- PASS: total_score >= 70
- FAIL: total_score < 70
