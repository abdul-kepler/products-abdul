# Instruction to Classify Keyword Relationship to Product

## Task Objective

Your goal is to classify the keyword's relationship to the product by using a structured decision tree. The classification results can be one of four categories: **R** (Relevant), **S** (Substitute), **C** (Complementary), or **N** (Negative). Follow the structured decision rules to arrive at the classification and provide a clear reasoning for each step.

## Decision Rules

Apply the decision rules in the following order, stopping at the first matching rule:

**Rule 1: HARD CONSTRAINT CHECK**
- Determine if the keyword violates any hard constraints associated with the product.
  - If it violates → **RETURN N (Negative)** and STOP.
  - If not → continue to Rule 2.

**Rule 2: SAME PRODUCT TYPE + SAME USE**
- Check if the keyword describes the **same product type** and supports the **same primary use**.
  - If so → **RETURN R (Relevant)** and STOP.
  - If not → continue to Rule 3.

**Rule 3: SAME PRODUCT TYPE + DIFFERENT USE**
- Evaluate if the keyword asks for the **same product type** but different primary use.
  - If so → **RETURN N (Negative)** and STOP.
  - If not → continue to Rule 4.

**Rule 4: SUBSTITUTE CHECK (Different Product Type)**
- Assess if the keyword describes a **different product type** that serves the **same customer need**.
  - If so → **RETURN S (Substitute)** and STOP.
  - Otherwise → continue to Rule 5.

**Rule 5: COMPLEMENTARY CHECK**
- Determine if the keyword is associated with a product that is **commonly used together** with this product.
  - If so → **RETURN C (Complementary)** and STOP.
  - If none of the above, return **N (Negative)**. 

## Input Structure

When provided with the following details, categorize the keyword:

- **Keyword**: The phrase to be classified.
- **Product Title**: Descriptive name of the product.
- **Validated Use**: Primary intended use of the product.

## Classification Definitions

### Relevant (R)
Keywords that denote the **same product type** and support the **same primary use**.

### Substitute (S)
Keywords describing a **different product type** that still satisfies the **same primary purpose** or **customer need**.

### Complementary (C)
Keywords relating to a **different product** commonly used in conjunction with the product.

### Negative (N)
Keywords that either violate hard constraints, align with the same product type but different use, or are unrelated in terms of both type and use.

## Output Format

Return a detailed JSON object illustrating reasoning at each step:

```json
{
  "step1_hard_constraint": {
    "violated": false,
    "violated_constraint": null,
    "reasoning": "Explanation of hard constraint decision."
  },
  "step2_product_type": {
    "same_type": boolean,
    "keyword_product_type": "Type identified from the keyword",
    "reasoning": "Explanation about product type classification."
  },
  "step3_primary_use": {
    "same_use": boolean,
    "reasoning": "Explanation about the primary use classification."
  },
  "step4_complementary": null, 
  "relevancy": "R/S/C/N", 
  "confidence": 0.0-1.0 // Confidence score in the classification
}
```

Faillurrians are related to facts such as product types and usage scopes. Apply contextual knowledge and examples to assess product relationships.
