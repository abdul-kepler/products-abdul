# Module 12 (V1.1): Keyword Classification Decision

## Task

Classify the keyword's relationship to the product using a structured decision tree. Output one of four classifications: **R** (Relevant), **S** (Substitute), **C** (Complementary), or **N** (Negative).

## Decision Rules

Apply these rules IN ORDER. Stop at the first matching rule.

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

**Keyword:** {{keyword}}

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

## Examples

### Example 1: RELEVANT (R)
**Product:** Stainless Steel Water Bottle (32oz)
**Primary Use:** portable hydration
**Keyword:** "insulated water bottle"

**Reasoning:**
- Step 1: No hard constraint violation ✓
- Step 2: Same product type (water bottle) → Step 3a
- Step 3a: Same primary use (portable hydration) → **R**

---

### Example 2: NEGATIVE - Hard Constraint (N)
**Product:** Stainless Steel Water Bottle (32oz)
**Hard Constraints:** [Size: 32oz]
**Keyword:** "64oz water jug"

**Reasoning:**
- Step 1: Violates hard constraint (64oz ≠ 32oz) → **N**

---

### Example 3: NEGATIVE - Different Use (N)
**Product:** Memory Foam Pillow
**Primary Use:** head neck support during sleep
**Keyword:** "throw pillow"

**Reasoning:**
- Step 1: No hard constraint violation ✓
- Step 2: Same product type (pillow) → Step 3a
- Step 3a: Different primary use (decoration vs sleep support) → **N**

---

### Example 4: SUBSTITUTE (S)
**Product:** Stainless Steel Water Bottle
**Primary Use:** portable hydration
**Keyword:** "plastic tumbler"

**Reasoning:**
- Step 1: No hard constraint violation ✓
- Step 2: Different product type (tumbler ≠ bottle) → Step 3b
- Step 3b: Same primary use (portable hydration) → **S**

---

### Example 4b: SUBSTITUTE (S)
**Product:** Wireless Bluetooth Earbuds
**Primary Use:** personal audio listening
**Keyword:** "wired headphones"

**Reasoning:**
- Step 1: No hard constraint violation ✓
- Step 2: Different product type (headphones ≠ earbuds) → Step 3b
- Step 3b: Same primary use (personal audio listening) → **S**

**Key insight:** Customer wants to listen to audio. Both earbuds and headphones serve that need, making headphones a substitute.

---

### Example 4c: SUBSTITUTE (S)
**Product:** Memory Foam Pillow
**Primary Use:** head neck support during sleep
**Keyword:** "buckwheat pillow"

**Reasoning:**
- Step 1: No hard constraint violation ✓
- Step 2: Different product type (buckwheat pillow uses different material/construction) → Step 3b
- Step 3b: Same primary use (head/neck support during sleep) → **S**

**Key insight:** Both products serve the same sleep support purpose, even though they use different materials.

---

### Example 5: COMPLEMENTARY (C)
**Product:** Wireless Bluetooth Earbuds
**Primary Use:** personal audio listening
**Keyword:** "earbud carrying case"

**Reasoning:**
- Step 1: No hard constraint violation ✓
- Step 2: Different product type (case ≠ earbuds) → Step 3b
- Step 3b: Different primary use (storage ≠ listening) → Step 4
- Step 4: Used together (case stores earbuds) → **C**

---

### Example 6: NEGATIVE - Unrelated (N)
**Product:** Memory Foam Pillow
**Primary Use:** head neck support during sleep
**Keyword:** "desk lamp"

**Reasoning:**
- Step 1: No hard constraint violation ✓
- Step 2: Different product type (lamp ≠ pillow) → Step 3b
- Step 3b: Different primary use (lighting ≠ sleep support) → Step 4
- Step 4: Not used together → **N**

## Output Format

Return a JSON object with structured reasoning at each step:

```json
{
  "step1_hard_constraint": {
    "violated": false,
    "violated_constraint": null,
    "reasoning": "Keyword does not specify any conflicting attribute values"
  },
  "step2_product_type": {
    "same_type": true,
    "keyword_product_type": "water bottle",
    "reasoning": "Keyword asks for water bottle which matches product taxonomy"
  },
  "step3_primary_use": {
    "same_use": true,
    "reasoning": "Both serve portable hydration purpose"
  },
  "step4_complementary": null,
  "relevancy": "R",
  "confidence": 0.95
}
```

**Notes:**
- `step4_complementary` is `null` if you reached a classification before Step 4
- `confidence` is 0.0-1.0 based on how clear the classification is
- Always fill in reasoning for each step you evaluated