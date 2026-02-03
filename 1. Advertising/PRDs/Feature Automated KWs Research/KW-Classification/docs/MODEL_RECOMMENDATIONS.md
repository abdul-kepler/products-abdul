# Model Recommendations for Search Term Classification Pipeline

## Executive Summary

This document provides model selection recommendations for the v1.1 Search Term Classification Pipeline. Each module has distinct requirements based on task complexity, accuracy needs, and cost considerations.

**Key Insight:** The pipeline's modular design allows for mixed model deployment - using stronger models for complex reasoning tasks (M06, M09-M11, M12) while using faster/cheaper models for pattern-matching tasks (M01-M05).

---

## Model Selection Matrix

| Task Type | Modules | Best Accuracy | Best Cost/Speed | Reasoning Model? |
|-----------|---------|---------------|-----------------|------------------|
| Brand Entity Extraction | M01, M01a, M01b, M03 | gpt-4o-mini | gemini-2.0-flash-exp | No |
| Brand Classification | M02-M05 | gpt-4o-mini | gemini-2.0-flash-exp | No |
| Taxonomy Generation | M06 | gpt-4o | gpt-4.1 | Consider o3-mini |
| Attribute Extraction | M07, M08 | gpt-4o-mini | gemini-1.5-flash | No |
| Primary Use Identification | M09, M10, M11 | gpt-4o | gpt-4.1-mini | Consider o3-mini |
| Relevance Classification | M12-M16 | gpt-4o | gpt-4.1 | Yes (o3-mini) |

---

## Detailed Analysis by Task Type

### 1. Brand Entity Extraction (M01, M01a, M01b, M03)

**Task Characteristics:**
- Extract brand names from listing text
- Generate search variations (typos, case, phonetic)
- Identify sub-brands, product lines, manufacturer
- Pattern recognition focused, not reasoning heavy

**Recommended Models:**

| Priority | Model | Temperature | Why |
|----------|-------|-------------|-----|
| **Production** | gpt-4o-mini | 0.3 | Best balance of accuracy and cost for text extraction |
| **Budget** | gemini-2.0-flash-exp | 0.3 | Fast, cost-effective, handles structured extraction well |
| **Premium** | gpt-4o | 0.2 | Overkill for this task, only if budget allows |

**Temperature Rationale:** Low temperature (0.3) ensures consistent extraction without creativity variations.

**Model-Specific Adjustments:**
- **Gemini models:** Add explicit JSON formatting instructions; Gemini sometimes adds markdown code blocks
- **OpenAI models:** Works well with standard prompts

**NOT Recommended:**
- Reasoning models (o1, o3-mini) - unnecessary overhead for pattern matching
- gpt-4.1 - new model, not yet proven for extraction tasks

---

### 2. Brand Classification (M02-M05)

**Task Characteristics:**
- String matching against brand dictionaries
- Rule-based classification (OB/CB/NB)
- Hidden brand detection
- Clear decision boundaries

**Recommended Models:**

| Priority | Model | Temperature | Why |
|----------|-------|-------------|-----|
| **Production** | gpt-4o-mini | 0.1 | Deterministic task needs consistent outputs |
| **Budget** | gemini-2.0-flash-exp | 0.1 | Excellent for rule-following tasks |
| **High Accuracy** | gemini-1.5-pro | 0.1 | Better hidden brand detection |

**Temperature Rationale:** Very low temperature (0.1) for maximum consistency in classification outputs.

**Critical Considerations:**
- Classification tasks benefit from explicit decision trees in prompts
- Gemini models excel at following structured rules
- Hidden brand detection may benefit from larger context window (gemini-1.5-pro)

**NOT Recommended:**
- Reasoning models - classification is deterministic, not reasoning
- gpt-4o - cost inefficient for this task

---

### 3. Taxonomy Generation (M06) - HIGH PRIORITY

**Task Characteristics:**
- Create hierarchical product classification
- Requires domain knowledge (e-commerce categories)
- Must understand product type relationships
- Needs consistent hierarchy logic (L1 most specific -> L3 most general)

**Recommended Models:**

| Priority | Model | Temperature | Why |
|----------|-------|-------------|-----|
| **Production** | gpt-4o | 0.4 | Strong domain knowledge, reliable hierarchy |
| **Budget** | gpt-4.1 | 0.4 | Good balance, latest model may have improved categorization |
| **Premium** | o3-mini | N/A | Best for complex hierarchical reasoning |
| **Alternative** | gemini-1.5-pro | 0.4 | Strong at structured outputs |

**Temperature Rationale:** Moderate temperature (0.4) allows flexibility in category naming while maintaining structure.

**Why This Task is Special:**
1. **Domain Knowledge Critical:** Model must understand e-commerce product taxonomies
2. **Hierarchy Logic:** L1 (most specific) -> L3 (most general) requires consistent reasoning
3. **Edge Cases:** Products that span categories (e.g., "phone mount for car" - is it phone accessory or car accessory?)

**When to Use Reasoning Models (o3-mini):**
- Products with ambiguous categorization
- Multi-function products
- Novel product types not well-represented in training data

**Prompt Adjustments by Model:**

**For gpt-4o/gpt-4.1:**
```
Provide hierarchy from MOST SPECIFIC (Level 1) to MOST GENERAL (Level 3).
Level 1: The exact product type as described
Level 2: The broader category this product belongs to
Level 3: The general department/category
```

**For gemini-1.5-pro:**
```
OUTPUT FORMAT: JSON only, no markdown code blocks.
{
  "taxonomy": [
    {"level": 1, "product_type": "...", "rank": 1},
    ...
  ]
}
```

**For o3-mini (reasoning):**
```
Think step-by-step about the product hierarchy:
1. What is this product at its most specific level?
2. What broader category does it belong to?
3. What general department would this be in?
```

---

### 4. Attribute Extraction and Ranking (M07, M08)

**Task Characteristics:**
- Extract variants, use cases, audiences from listing
- Rank attributes by importance for keyword matching
- Structured output with multiple categories

**Recommended Models:**

| Priority | Model | Temperature | Why |
|----------|-------|-------------|-----|
| **Production** | gpt-4o-mini | 0.3 | Good extraction capabilities, cost-effective |
| **Budget** | gemini-1.5-flash | 0.3 | Fast, handles structured extraction |
| **High Accuracy** | gpt-4o | 0.3 | Better at nuanced ranking |

**Temperature Rationale:** Low-moderate temperature (0.3) for consistent extraction with slight flexibility.

**M08 Ranking Considerations:**
- Ranking requires understanding relative importance
- May benefit from few-shot examples showing ranking logic
- gpt-4o significantly better at nuanced ranking decisions

---

### 5. Primary Use Identification (M09, M10, M11) - HIGH PRIORITY

**Task Characteristics:**
- M09: Identify ONE core purpose (3-6 words)
- M10: Validate/correct the primary use phrase
- M11: Identify hard constraints (non-negotiable attributes)
- Requires semantic understanding and abstraction

**Recommended Models:**

| Priority | Model | Temperature | Why |
|----------|-------|-------------|-----|
| **Production** | gpt-4o | 0.3 | Best semantic understanding |
| **Budget** | gpt-4.1-mini | 0.3 | Cost-effective with good reasoning |
| **Premium** | o3-mini | N/A | Best for abstract reasoning |
| **Alternative** | gemini-1.5-pro | 0.3 | Good at following strict rules |

**Temperature Rationale:** Low temperature (0.3) - creative phrasing not needed, consistency is key.

**Why This Is Complex:**

**M09 Challenges:**
- Must abstract from features to PURPOSE
- "wireless earbuds with ANC" -> "audio listening" (NOT "noise-canceling listening")
- Requires understanding what product DOES vs HOW WELL it does it

**M11 Challenges:**
- Distinguishing "nice-to-have" from "must-have" attributes
- Example: Bluetooth is essential for wireless earbuds; color is not
- Requires counterfactual reasoning: "Would product work without this?"

**Model-Specific Prompt Adjustments:**

**For M09 with gpt-4o:**
```
Strip away ALL features, specifications, and modifiers.
Focus ONLY on the core action this product enables.
BAD: "noise-canceling audio listening" (includes feature)
GOOD: "audio listening" (pure purpose)
```

**For M11 with o3-mini:**
```
For each attribute, ask: "If this attribute were DIFFERENT, would the
product become COMPLETELY UNUSABLE for its primary purpose?"

Reasoning chain:
1. List all product attributes
2. For each, test the counterfactual
3. Only include those where the answer is YES
```

---

### 6. Relevance Classification (M12-M16) - HIGH PRIORITY

**Task Characteristics:**
- Multi-step decision tree
- Combines all previous module outputs
- Must follow explicit logic path
- R/S/C/N classification with reasoning

**Recommended Models:**

| Priority | Model | Temperature | Why |
|----------|-------|-------------|-----|
| **Production** | gpt-4o | 0.2 | Reliable decision tree following |
| **Budget** | gpt-4.1 | 0.2 | Good reasoning capabilities |
| **Premium** | o3-mini | N/A | Best for multi-step reasoning |
| **Fast** | gemini-2.0-flash-exp | 0.2 | Good for simple cases |

**Temperature Rationale:** Very low temperature (0.2) for deterministic classification.

**When to Use o3-mini:**
- Complex edge cases (product spans categories)
- When M12 confidence is low
- For generating training data / golden labels

**Decision Tree Implementation by Model:**

**Standard Models (gpt-4o, gpt-4.1):**
```
Follow this decision tree EXACTLY:
1. Hard Constraint Check: Does keyword violate any hard constraint?
   - YES -> N (Negative)
   - NO -> Continue to Step 2
[... explicit steps ...]
```

**Reasoning Models (o3-mini):**
```
Analyze this classification step-by-step:

Given:
- Keyword: {keyword}
- Product: {product}
- Primary Use: {validated_use}
- Hard Constraints: {hard_constraints}

Think through:
1. Could this keyword imply something that violates our hard constraints?
2. Is this the same product type or different?
3. Would both products serve the same primary purpose?
4. Are these products commonly used together?

Conclude with classification and confidence.
```

---

## Cost vs Accuracy Tradeoff Analysis

### Cost Comparison (relative, per 1M tokens input)

| Model | Input Cost | Output Cost | Speed | Notes |
|-------|------------|-------------|-------|-------|
| gpt-4o | $2.50 | $10.00 | Medium | Best overall accuracy |
| gpt-4o-mini | $0.15 | $0.60 | Fast | Best value for simple tasks |
| gpt-4.1 | $2.00 | $8.00 | Medium | Latest, good for reasoning |
| gpt-4.1-mini | $0.40 | $1.60 | Fast | Good budget reasoning |
| o1 | $15.00 | $60.00 | Slow | Deep reasoning, expensive |
| o1-mini | $3.00 | $12.00 | Medium | Good reasoning, moderate cost |
| o3-mini | ~$1.10 | ~$4.40 | Medium | Best reasoning value |
| gemini-2.0-flash-exp | ~$0.075 | ~$0.30 | Very Fast | Cheapest option |
| gemini-1.5-pro | ~$1.25 | ~$5.00 | Medium | Strong alternative |
| gemini-1.5-flash | ~$0.075 | ~$0.30 | Very Fast | Budget option |

### Recommended Configurations

**Budget Configuration (Lowest Cost):**
```yaml
brand_extraction: gemini-2.0-flash-exp
brand_classification: gemini-2.0-flash-exp
taxonomy: gpt-4o-mini  # Don't cheap out here
attributes: gemini-1.5-flash
primary_use: gpt-4o-mini
relevance: gpt-4o-mini
```
*Estimated cost: ~$0.50 per 1000 classifications*

**Balanced Configuration (Best Value):**
```yaml
brand_extraction: gpt-4o-mini
brand_classification: gpt-4o-mini
taxonomy: gpt-4o  # Critical for accuracy
attributes: gpt-4o-mini
primary_use: gpt-4o-mini
relevance: gpt-4.1-mini
```
*Estimated cost: ~$1.50 per 1000 classifications*

**Premium Configuration (Maximum Accuracy):**
```yaml
brand_extraction: gpt-4o-mini
brand_classification: gpt-4o-mini
taxonomy: o3-mini  # Use reasoning for hierarchy
attributes: gpt-4o
primary_use: gpt-4o
relevance: o3-mini  # Multi-step reasoning
```
*Estimated cost: ~$5.00 per 1000 classifications*

---

## Reasoning Models: When to Use

### o1, o1-mini, o3-mini Comparison

| Model | Best For | Avoid For | Cost Level |
|-------|----------|-----------|------------|
| o3-mini | Complex reasoning, edge cases | Simple extraction | $$ |
| o1-mini | Very complex problems | Anything simpler | $$$ |
| o1 | Research, hardest problems | Production use | $$$$ |

### Tasks That Benefit from Reasoning Models

1. **M06 (Taxonomy):** When product type is ambiguous
2. **M11 (Hard Constraints):** Counterfactual reasoning benefits from step-by-step
3. **M12 (Relevance):** Complex edge cases with multiple considerations

### Tasks That DON'T Need Reasoning Models

1. **M01-M01b:** Pattern extraction, not reasoning
2. **M02-M05:** Rule-based classification
3. **M07-M08:** Attribute extraction

### Hybrid Approach

Use reasoning models selectively:
```python
# Pseudo-code for hybrid approach
if classification_confidence < 0.8:
    # Re-run with reasoning model
    result = o3_mini.classify(keyword)
else:
    # Keep original result
    result = gpt4o_mini_result
```

---

## Temperature and Sampling Settings

### Temperature Guidelines by Task Type

| Task Type | Temperature | Top-P | Rationale |
|-----------|-------------|-------|-----------|
| Brand Extraction | 0.3 | 0.95 | Consistent extraction |
| Classification | 0.1 | 0.90 | Deterministic outputs |
| Taxonomy | 0.4 | 0.95 | Some flexibility in naming |
| Attribute Extraction | 0.3 | 0.95 | Consistent extraction |
| Primary Use | 0.3 | 0.90 | Controlled abstraction |
| Relevance | 0.2 | 0.90 | Deterministic decision |

### Model-Specific Settings

**OpenAI Models:**
- Use `response_format: { type: "json_object" }` for JSON outputs
- `presence_penalty: 0` (don't discourage repetition for structured outputs)
- `frequency_penalty: 0`

**Gemini Models:**
- Always specify `"Output ONLY valid JSON, no markdown code blocks"`
- May need post-processing to strip ```json``` wrappers
- Use `harm_category` settings if getting blocks

**Reasoning Models (o1, o3-mini):**
- Temperature is not applicable (fixed)
- Use clear step-by-step instructions
- Expect longer latency

---

## Special Recommendations for M06 (Taxonomy)

M06 is the most critical module for accuracy. User emphasized this.

### Why M06 Is Hard

1. **Domain Knowledge:** Model must understand e-commerce categories
2. **Consistency:** Same product type should always map to same hierarchy
3. **Granularity:** Knowing when to stop (3 levels, not more)
4. **Edge Cases:** Multi-function products, novel products

### Recommended M06 Configuration

**Production (Balanced):**
```yaml
model: gpt-4o
temperature: 0.4
system_prompt: |
  You are an expert e-commerce product taxonomist. Create consistent,
  Amazon-style product hierarchies.
```

**High Stakes (Maximum Accuracy):**
```yaml
model: o3-mini
# No temperature (reasoning model)
system_prompt: |
  Think step-by-step to create a product hierarchy:

  1. What is the most specific, accurate product type name?
  2. What broader category contains this product type?
  3. What department-level category is this under?

  Use Amazon-style category naming conventions.
```

### M06 Evaluation Criteria

When comparing models, evaluate:
1. **Consistency:** Same product -> same taxonomy across runs
2. **Specificity:** Level 1 should be very specific
3. **Generality:** Level 3 should be broad enough to group related products
4. **Naming:** Use standard e-commerce terms

### M06 Few-Shot Examples

Include these in prompts:

```json
{
  "product": "JBL Vibe Beam True Wireless Earbuds",
  "taxonomy": [
    {"level": 1, "product_type": "True Wireless Earbuds", "rank": 1},
    {"level": 2, "product_type": "Wireless Earphones", "rank": 2},
    {"level": 3, "product_type": "Headphones & Earbuds", "rank": 3}
  ]
}

{
  "product": "Owala FreeSip 24oz Water Bottle",
  "taxonomy": [
    {"level": 1, "product_type": "Insulated Water Bottle", "rank": 1},
    {"level": 2, "product_type": "Water Bottles", "rank": 2},
    {"level": 3, "product_type": "Drinkware", "rank": 3}
  ]
}
```

---

## Implementation Recommendations

### Phase 1: Baseline (Start Here)

Use single model across pipeline for simplicity:
```yaml
all_modules: gpt-4o-mini
temperature: 0.3 (except classification: 0.1)
```

### Phase 2: Optimized Mix

After baseline metrics, upgrade critical modules:
```yaml
brand_extraction: gpt-4o-mini
brand_classification: gpt-4o-mini
taxonomy: gpt-4o  # Upgrade
attributes: gpt-4o-mini
primary_use: gpt-4o-mini
relevance: gpt-4.1-mini  # Upgrade
```

### Phase 3: Hybrid with Reasoning

Add reasoning model for edge cases:
```yaml
# Same as Phase 2, plus:
fallback_model: o3-mini  # Use when confidence < threshold
```

### Evaluation Strategy

For each model configuration, measure:
1. **Accuracy:** % correct classifications (against golden labels)
2. **Consistency:** Same input -> same output (run 3x)
3. **Latency:** P50, P95 response times
4. **Cost:** Total API cost per 1000 classifications

---

## Summary Table

| Module | Recommended Model | Temperature | Reasoning Model Benefit |
|--------|-------------------|-------------|------------------------|
| M01 | gpt-4o-mini | 0.3 | None |
| M01a | gpt-4o-mini | 0.3 | None |
| M01b | gpt-4o-mini | 0.3 | None |
| M02-M05 | gpt-4o-mini | 0.1 | None |
| **M06** | **gpt-4o** | **0.4** | **o3-mini for edge cases** |
| M07-M08 | gpt-4o-mini | 0.3 | Slight |
| **M09-M11** | **gpt-4o** | **0.3** | **o3-mini beneficial** |
| **M12-M16** | **gpt-4.1** | **0.2** | **o3-mini for complex cases** |

---

*Document created: January 9, 2026*
*Pipeline version: v1.1*
