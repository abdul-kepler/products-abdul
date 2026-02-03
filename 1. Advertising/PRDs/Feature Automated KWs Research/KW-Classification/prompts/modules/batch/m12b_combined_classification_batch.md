# Module 12 Batch: Keyword Classification Decision (Batch Version)

## Task

Classify each keyword's relationship to the product using a structured decision tree. For each keyword, output one of four classifications: **R** (Relevant), **S** (Substitute), **C** (Complementary), or **N** (Negative).

## Decision Rules

Apply these rules IN ORDER to each keyword. Stop at the first matching rule.

**Rule 1: HARD CONSTRAINT CHECK**
- IF keyword violates any hard constraint → **RETURN N (Negative)** and STOP
- OTHERWISE → continue to Rule 2

**Rule 2: SAME PRODUCT TYPE + SAME USE**
- IF keyword asks for the SAME product type AND supports the SAME primary use → **RETURN R (Relevant)** and STOP
- OTHERWISE → continue to Rule 3

**Rule 3: SAME PRODUCT TYPE + DIFFERENT USE**
- IF keyword asks for the SAME product type BUT different primary use → **RETURN N (Negative)** and STOP
- OTHERWISE → continue to Rule 4

**Rule 4: SUBSTITUTE CHECK (Different Product Type)**
- IF keyword describes a DIFFERENT product type that serves the SAME CUSTOMER NEED → **RETURN S (Substitute)** and STOP
- Think broadly: would a customer considering this product also consider the keyword's product?
- Examples: travel mug↔water bottle (both: hydration), speaker↔earbuds (both: audio)
- OTHERWISE → continue to Rule 5

**Rule 5: COMPLEMENTARY CHECK**
- IF keyword is for a product commonly USED TOGETHER with this product → **RETURN C (Complementary)** and STOP
- OTHERWISE → **RETURN N (Negative)**

## Input

**Keywords:**
{{keywords}}

**Product Title:** {{title}}

**Bullet Points:**
{{bullet_points}}

**Description:**
{{description}}

**Primary Intended Use:** {{validated_use}}

**Product Type Taxonomy:**
{{taxonomy}}

**Attributes:**
{{attribute_table}}

**Hard Constraints:**
{{hard_constraints}}

## Classification Definitions

### **Relevant (R)**
Keywords that describe the **same product type** as the ASIN and support the **same primary intended use**.

| Example ASIN | Keyword | Why Relevant |
|--------------|---------|--------------|
| Stainless Steel Water Bottle | insulated water bottle | Same product type, same use (portable hydration) |
| Wireless Bluetooth Earbuds | wireless earphones | Same product type, same use (personal audio listening) |
| Memory Foam Pillow | bed pillow | Same product type, same use (head/neck support during sleep) |

### **Substitute (S)**
Keywords that describe a **different product type** but satisfy the **same primary intended use** or **the same underlying customer need** as the ASIN.

| Example ASIN | Keyword | Why Substitute |
|--------------|---------|----------------|
| Stainless Steel Water Bottle | plastic tumbler | Different product type, but still satisfies portable hydration |
| Stainless Steel Water Bottle | travel mug | Different product type, but customer need is the same: carrying drinks |
| Wireless Bluetooth Earbuds | wired headphones | Different product type, but still satisfies personal audio listening |
| Wireless Bluetooth Earbuds | bluetooth speaker | Different product type, but same need: listening to audio |
| Memory Foam Pillow | buckwheat pillow | Different product type, but still satisfies head/neck support during sleep |
| Puffer Jacket | long winter coat | Different product type, but same need: cold weather body warmth |
| Puffer Jacket | sweater | Different product type, but same need: warmth |
| Oven Mitt | heat resistant towel | Different product type, but same need: heat protection when cooking |

**Critical insight:** Think about what the CUSTOMER WANTS to accomplish. If both products solve the same customer problem, they are substitutes. Ask: "Would someone shopping for the ASIN also consider buying the keyword's product instead?"

### **Complementary (C)**
Keywords that describe a **different product** that is **commonly used together** with the ASIN.

| Example ASIN | Keyword | Why Complementary |
|--------------|---------|-------------------|
| Stainless Steel Water Bottle | bottle cleaning brush | Used to maintain/clean the bottle |
| Wireless Bluetooth Earbuds | earbud carrying case | Used to store/protect the earbuds |
| Memory Foam Pillow | silk pillowcase | Used as a cover for the pillow |

### **Negative (N)**
Keywords that fall into any of the following conditions:
- **Violates a hard constraint** — incompatible specification makes purchase pointless
- **Same product type but different primary use** — cannot serve customer's need
- **Different product type, different use, and not used together** — unrelated

| Example ASIN | Keyword | Why Negative |
|--------------|---------|--------------|
| Stainless Steel Water Bottle (32oz) | 64oz water jug | Hard constraint violation (size incompatibility) |
| Wireless Bluetooth Earbuds | gaming headset with mic | Same category but different primary use (gaming communication vs. music listening) |
| Memory Foam Pillow | throw pillow | Same product type but different use (decoration vs. sleep support) |

## Batch Processing Instructions

1. Process each keyword in the `keywords` array independently
2. Apply the full decision tree to each keyword
3. Return results in the same order as the input keywords
4. Maintain consistent evaluation criteria across all keywords

## Output Format

Return a JSON object with a `results` array containing one object per keyword:

```json
{
  "results": [
    {
      "keyword": "insulated water bottle",
      "relevancy": "R",
      "reasoning": {
        "step1_hard_constraint": {
          "violated": false,
          "violated_constraint": null,
          "explanation": "Keyword does not specify any conflicting attribute values"
        },
        "step2_product_type": {
          "same_type": true,
          "keyword_product_type": "water bottle",
          "explanation": "Keyword asks for water bottle which matches product taxonomy"
        },
        "step3_primary_use": {
          "same_use": true,
          "explanation": "Both serve portable hydration purpose"
        },
        "step4_complementary": null,
        "decision_path": "Rule1→Rule2→R"
      },
      "confidence": 0.95
    },
    {
      "keyword": "plastic tumbler",
      "relevancy": "S",
      "reasoning": {
        "step1_hard_constraint": {
          "violated": false,
          "violated_constraint": null,
          "explanation": "No hard constraint violation"
        },
        "step2_product_type": {
          "same_type": false,
          "keyword_product_type": "tumbler",
          "explanation": "Tumbler is a different product type than water bottle"
        },
        "step3_substitute": {
          "same_customer_need": true,
          "explanation": "Both serve portable hydration, customer would consider either"
        },
        "step4_complementary": null,
        "decision_path": "Rule1→Rule4→S"
      },
      "confidence": 0.90
    },
    {
      "keyword": "bottle cleaning brush",
      "relevancy": "C",
      "reasoning": {
        "step1_hard_constraint": {
          "violated": false,
          "violated_constraint": null,
          "explanation": "No hard constraint violation"
        },
        "step2_product_type": {
          "same_type": false,
          "keyword_product_type": "cleaning brush",
          "explanation": "Cleaning brush is a different product type"
        },
        "step3_substitute": {
          "same_customer_need": false,
          "explanation": "Brush serves cleaning purpose, not hydration"
        },
        "step4_complementary": {
          "used_together": true,
          "explanation": "Cleaning brush is commonly used to maintain water bottles"
        },
        "decision_path": "Rule1→Rule4→Rule5→C"
      },
      "confidence": 0.92
    },
    {
      "keyword": "desk lamp",
      "relevancy": "N",
      "reasoning": {
        "step1_hard_constraint": {
          "violated": false,
          "violated_constraint": null,
          "explanation": "No hard constraint violation"
        },
        "step2_product_type": {
          "same_type": false,
          "keyword_product_type": "lamp",
          "explanation": "Lamp is a completely different product category"
        },
        "step3_substitute": {
          "same_customer_need": false,
          "explanation": "Lamp serves lighting purpose, unrelated to hydration"
        },
        "step4_complementary": {
          "used_together": false,
          "explanation": "Desk lamp is not commonly used together with water bottles"
        },
        "decision_path": "Rule1→Rule4→Rule5→N"
      },
      "confidence": 0.98
    }
  ]
}
```

**Notes:**
- `decision_path` shows the exact steps taken through the decision tree (e.g., "Step1→Step2→Step3a→R")
- Steps not evaluated should be `null` (e.g., `step4_complementary` is `null` if classification was determined earlier)
- For Step 3, use `step3_primary_use` (same product type path) OR `step3_substitute` (different product type path), not both
- `confidence` is 0.0-1.0 based on how clear the classification is
- Maintain the exact order of keywords from input to output
