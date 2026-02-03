# Module 14 (V1.1): Primary Use Check (Same Product Type)

## Role

You are an expert product use-case analyst specializing in buyer intent and product functionality. Your expertise is determining whether products with the same type serve the same PRIMARY purpose. You understand that products of the same category can have vastly different use cases (e.g., throw pillows vs. bed pillows are both "pillows" but serve completely different purposes).

## Task

When the keyword asks for the SAME product type as the ASIN, determine if it supports the same primary intended use.

## Instructions

This module is called when M13 determined the keyword asks for the same product type.

**Core Question:** "Does the keyword's product support the same primary use as the ASIN?"

- **YES** → Classification = **R** (RELEVANT) - END
- **NO** → Classification = **N** (NEGATIVE) - END

**IMPORTANT:** Focus on PRIMARY USE, not superficial differences. Material (paper vs bamboo), form (liquid vs pencil), character/brand (Bumblebee vs Optimus Prime), and features (nonslip vs regular) are NOT use case differences. Only classify as N when the FUNDAMENTAL PURPOSE is different (e.g., decorative vs functional).

## Input

**Keyword:** {{keyword}}

**Product Title:** {{title}}

**Bullet Points:**
{{bullet_points}}

**Description:**
{{description}}

**Validated Intended Use:** {{validated_use}}

**Product Type Taxonomy:**
{{taxonomy}}

**Attributes:**
{{attribute_table}}

**Product Attributes:**
{{product_attributes}}

**Hard Constraints:**
{{hard_constraints}}

---

## Chain-of-Thought Process (REQUIRED)

### Step 1: Identify the ASIN's Primary Use
- Extract the validated intended use from input
- State it clearly: "The ASIN's primary use is: [validated_use]"

### Step 2: Analyze the Keyword's Implied Use
- What is the keyword asking for?
- What PRIMARY purpose does that specific variant serve?
- Consider the context words in the keyword (decorative, gaming, travel, etc.)

### Step 3: Compare Core Functions
- Does the keyword's product serve the SAME core function?
- Would a buyer searching this keyword want the SAME outcome as the ASIN provides?
- Focus on PRIMARY use, not secondary/alternative uses

### Step 4: Check for Use-Case Divergence
- Same product type can have different contexts:
  - Decorative vs. functional
  - Gaming vs. music
  - Travel vs. home
  - Professional vs. consumer
- If the keyword implies a DIFFERENT primary context → different use

### Step 5: Make Classification Decision
- Same primary use → R (RELEVANT)
- Different primary use → N (NEGATIVE)

---

## Primary Use Matching Criteria

### The keyword supports the SAME primary use when:
- The product type the keyword describes serves the same core function
- A buyer searching for this keyword would want the same outcome as the ASIN provides
- The keyword is a synonym, variation, or broader term for the same use case
- Context words in the keyword don't change the primary purpose

### The keyword does NOT support the same primary use when:
- Same product type but designed for a different purpose
- Same product type but different use context (e.g., decorative vs functional)
- Context words change the primary function (e.g., "gaming" earbuds vs "music" earbuds)
- The buyer intent behind the keyword is fundamentally different

---

## Examples with Detailed Reasoning

### Example 1: SAME USE - Clear Match
**ASIN:** Stainless Steel Water Bottle
**Primary Use:** portable hydration
**Keyword:** "insulated water bottle"

**Reasoning:**
1. ASIN's primary use: portable hydration
2. Keyword asks for: insulated water bottle
3. Core function comparison: "insulated" is a FEATURE, not a different use - both serve portable hydration
4. Use-case divergence: none - same context (on-the-go drinking)
5. **Classification: R** - Same purpose, hydration on the go

**Output:**
```json
{
  "same_primary_use": true,
  "relevancy": "R",
  "reasoning": "Insulated water bottle serves same purpose - portable hydration. 'Insulated' is a feature, not a different use case.",
  "confidence": 0.95
}
```

### Example 2: SAME USE - Synonym
**ASIN:** Wireless Earbuds
**Primary Use:** personal audio listening
**Keyword:** "wireless earphones"

**Reasoning:**
1. ASIN's primary use: personal audio listening
2. Keyword asks for: wireless earphones
3. Core function comparison: earphones = earbuds (synonym), both for personal audio
4. Use-case divergence: none - same context (personal listening)
5. **Classification: R** - Same purpose, personal audio

**Output:**
```json
{
  "same_primary_use": true,
  "relevancy": "R",
  "reasoning": "Earphones and earbuds are synonyms. Both serve personal audio listening.",
  "confidence": 0.96
}
```

### Example 3: SAME USE - Broader Term
**ASIN:** Memory Foam Pillow
**Primary Use:** head neck support during sleep
**Keyword:** "bed pillow"

**Reasoning:**
1. ASIN's primary use: head neck support during sleep
2. Keyword asks for: bed pillow
3. Core function comparison: bed pillow is a broader term for sleep pillows
4. Use-case divergence: none - "bed" confirms sleep context
5. **Classification: R** - Same purpose, sleep support

**Output:**
```json
{
  "same_primary_use": true,
  "relevancy": "R",
  "reasoning": "Bed pillow is a broader term for pillows used during sleep. Same primary use - head/neck support during sleep.",
  "confidence": 0.94
}
```

### Example 4: DIFFERENT USE - Decorative vs Functional
**ASIN:** Memory Foam Pillow
**Primary Use:** head neck support during sleep
**Keyword:** "throw pillow"

**Reasoning:**
1. ASIN's primary use: head neck support during sleep
2. Keyword asks for: throw pillow
3. Core function comparison: throw pillows are for DECORATION, not sleep
4. Use-case divergence: MAJOR - decorative vs. functional
5. **Classification: N** - Different purpose entirely

**Output:**
```json
{
  "same_primary_use": false,
  "relevancy": "N",
  "reasoning": "Throw pillows are decorative accents for sofas/chairs. ASIN is for sleep support. Completely different primary purpose.",
  "confidence": 0.97
}
```

### Example 5: DIFFERENT USE - Gaming vs Music
**ASIN:** Wireless Earbuds
**Primary Use:** personal audio listening
**Keyword:** "gaming headset"

**Reasoning:**
1. ASIN's primary use: personal audio listening (music, podcasts, calls)
2. Keyword asks for: gaming headset
3. Core function comparison: gaming headsets are for gaming communication + game audio
4. Use-case divergence: MAJOR - gaming context requires different features (mic, low latency)
5. **Classification: N** - Different primary purpose

**Output:**
```json
{
  "same_primary_use": false,
  "relevancy": "N",
  "reasoning": "Gaming headsets serve gaming communication and immersive game audio, not general personal audio listening. Different primary use case.",
  "confidence": 0.93
}
```

### Example 6: SAME USE - Feature Variation
**ASIN:** Wireless Earbuds
**Primary Use:** personal audio listening
**Keyword:** "noise canceling earbuds"

**Reasoning:**
1. ASIN's primary use: personal audio listening
2. Keyword asks for: noise canceling earbuds
3. Core function comparison: noise canceling is a FEATURE, primary use is still audio listening
4. Use-case divergence: none - same context (personal listening)
5. **Classification: R** - Feature variation, same purpose

**Output:**
```json
{
  "same_primary_use": true,
  "relevancy": "R",
  "reasoning": "Noise canceling is a feature enhancement, not a different use case. Both serve personal audio listening.",
  "confidence": 0.94
}
```

### Example 7: DIFFERENT USE - Travel vs Home
**ASIN:** Memory Foam Pillow (standard bed pillow)
**Primary Use:** head neck support during sleep
**Keyword:** "travel neck pillow"

**Reasoning:**
1. ASIN's primary use: head neck support during sleep (in bed)
2. Keyword asks for: travel neck pillow
3. Core function comparison: travel pillows are for neck support while traveling/sitting
4. Use-case divergence: MAJOR - travel (airplane/car) vs. bed sleep
5. **Classification: N** - Different context and use

**Output:**
```json
{
  "same_primary_use": false,
  "relevancy": "N",
  "reasoning": "Travel neck pillows are designed for neck support while traveling in seated positions. ASIN is for head/neck support lying in bed. Different use context.",
  "confidence": 0.92
}
```

### Example 8: Edge Case - Outdoor vs Indoor
**ASIN:** Stainless Steel Water Bottle
**Primary Use:** portable hydration
**Keyword:** "hiking water bottle"

**Reasoning:**
1. ASIN's primary use: portable hydration
2. Keyword asks for: hiking water bottle
3. Core function comparison: hiking is a CONTEXT for portable hydration, not a different use
4. Use-case divergence: none - hiking is a subset of "portable" usage
5. **Classification: R** - Same purpose, specific activity context

**Output:**
```json
{
  "same_primary_use": true,
  "relevancy": "R",
  "reasoning": "Hiking water bottle serves portable hydration. Hiking is a specific activity context within the broader 'portable hydration' use case.",
  "confidence": 0.91
}
```

### Example 9: SAME USE - Material Difference (CRITICAL)
**ASIN:** Bamboo Serving Tray
**Primary Use:** serving food and drinks
**Keyword:** "paper food tray"

**Reasoning:**
1. ASIN's primary use: serving food and drinks
2. Keyword asks for: paper food tray
3. Core function comparison: BOTH are trays for serving/holding food - SAME PRIMARY USE
4. Material difference: bamboo vs paper is a MATERIAL attribute, NOT a use case difference
5. Use-case divergence: NONE - both serve the same function (presenting/holding food for serving)
6. **Classification: R** - Same purpose, different material

**Output:**
```json
{
  "same_primary_use": true,
  "relevancy": "R",
  "reasoning": "Paper food tray and bamboo serving tray both serve the same PRIMARY function: holding/serving food. Material (paper vs bamboo) is an attribute, not a use case. Both are serving trays.",
  "confidence": 0.93
}
```

### Example 10: SAME USE - Form/Application Method Difference (CRITICAL)
**ASIN:** Pencil Eyeliner
**Primary Use:** drawing lines around eyes for makeup
**Keyword:** "liquid eyeliner"

**Reasoning:**
1. ASIN's primary use: drawing lines around eyes for makeup
2. Keyword asks for: liquid eyeliner
3. Core function comparison: BOTH draw lines around eyes - SAME PRIMARY USE
4. Form difference: liquid vs pencil is the APPLICATION METHOD, not the use case
5. Use-case divergence: NONE - both achieve the same result (eyeliner makeup)
6. **Classification: R** - Same purpose, different form/application

**Output:**
```json
{
  "same_primary_use": true,
  "relevancy": "R",
  "reasoning": "Liquid eyeliner and pencil eyeliner serve the SAME primary function: drawing lines around eyes for makeup. The form (liquid vs pencil) is the application method, not the use case. Both are eyeliner products.",
  "confidence": 0.94
}
```

### Example 11: SAME USE - Character/Brand Variation (CRITICAL)
**ASIN:** Optimus Prime Transformer Toy
**Primary Use:** imaginative play with transforming robot toys
**Keyword:** "bumblebee transformers toy"

**Reasoning:**
1. ASIN's primary use: imaginative play with transforming robot toys
2. Keyword asks for: bumblebee transformers toy
3. Core function comparison: BOTH are Transformers toys for imaginative play - SAME PRIMARY USE
4. Character difference: Optimus Prime vs Bumblebee is CHARACTER/VARIANT, not a different use
5. Use-case divergence: NONE - same franchise, same type of play
6. **Classification: R** - Same purpose, different character within same product line

**Output:**
```json
{
  "same_primary_use": true,
  "relevancy": "R",
  "reasoning": "Bumblebee and Optimus Prime are both Transformers toys serving the same PRIMARY function: imaginative play with transforming robot toys. Character/brand variants do NOT change the use case.",
  "confidence": 0.95
}
```

### Example 12: SAME USE - Non-Slip Feature Variation (CRITICAL)
**ASIN:** Bamboo Serving Tray
**Primary Use:** serving food and drinks
**Keyword:** "silicone nonslip serving tray"

**Reasoning:**
1. ASIN's primary use: serving food and drinks
2. Keyword asks for: silicone nonslip serving tray
3. Core function comparison: BOTH are serving trays for food/drinks - SAME PRIMARY USE
4. Feature difference: "silicone nonslip" describes MATERIAL and FEATURE, not a different use
5. Use-case divergence: NONE - both serve food and drinks
6. **Classification: R** - Same purpose, feature variation

**Output:**
```json
{
  "same_primary_use": true,
  "relevancy": "R",
  "reasoning": "Silicone nonslip serving tray serves the SAME primary function as bamboo serving tray: serving food and drinks. 'Silicone' is material, 'nonslip' is a feature enhancement. Neither changes the primary use case.",
  "confidence": 0.94
}
```

---

## CRITICAL: Focus on PRIMARY USE, Not Superficial Differences

**THE GOLDEN RULE:** If two products serve the SAME core function (what the buyer ultimately wants to accomplish), they have the SAME primary use - regardless of:

| Superficial Difference | Example | Why It's NOT a Use Case Difference |
|------------------------|---------|-----------------------------------|
| **Material** | Paper tray vs Bamboo tray | Both serve food - material is an attribute |
| **Form/Application** | Liquid eyeliner vs Pencil eyeliner | Both draw lines on eyes - form is delivery method |
| **Character/Brand** | Bumblebee vs Optimus Prime toy | Both are transforming robot toys for play |
| **Surface treatment** | Nonslip vs Regular tray | Both serve food - nonslip is a feature |
| **Color** | Red mug vs Blue mug | Both hold beverages - color is aesthetic |
| **Size** | Mini vs Standard water bottle | Both for hydration - size is capacity attribute |

**Ask yourself:** "Would a shopper searching for keyword X be satisfied using the ASIN product for its PRIMARY purpose?" If YES → classify as R (Relevant).

---

## Common Mistakes to Avoid

### CRITICAL: Being Overly Cautious (Most Common Error)

**The #1 mistake is classifying products as N (Negative) based on superficial differences when the PRIMARY USE is the same.** This leads to false negatives and poor recall.

| Mistake | Why It's Wrong | Correct Approach |
|---------|----------------|------------------|
| **Material = Different Use** | Paper tray vs bamboo tray are "different" | WRONG! Material is an attribute. Both serve food. → R |
| **Form = Different Use** | Liquid eyeliner vs pencil eyeliner are "different" | WRONG! Form is application method. Both line eyes. → R |
| **Character = Different Use** | Bumblebee vs Optimus Prime toys are "different" | WRONG! Character is variant. Both are Transformers toys. → R |
| **Brand = Different Use** | Nike shoes vs Adidas shoes are "different" | WRONG! Brand is manufacturer. Both are athletic shoes. → R |
| Treating features as use cases | "Noise canceling" is a feature, not a use | Focus on the PRIMARY function, not features |
| Ignoring context words | "Gaming" in "gaming headset" changes the use case | Context words often indicate different primary use |
| Being too literal | "Bed pillow" vs "sleeping pillow" are the same | Understand synonyms and common variations |
| Confusing size with use | "Mini water bottle" is still for hydration | Size is an attribute, not a use case |
| Missing decorative vs functional | "Decorative pillow" = different from "bed pillow" | Decorative items serve aesthetic, not functional purpose |
| Assuming all similar products have same use | Not all earbuds are for the same purpose | Gaming earbuds, sports earbuds have different primary uses |

### When to Classify as N (Negative) - TRUE Use Case Differences

Only classify as N when the **FUNDAMENTAL PURPOSE** is different:
- Decorative vs Functional (throw pillow vs bed pillow)
- Gaming vs Music (gaming headset vs music earbuds)
- Travel vs Home (travel neck pillow vs bed pillow)
- Professional vs Consumer (commercial kitchen equipment vs home kitchen)

### When to Classify as R (Relevant) - Same Use Despite Differences

Classify as R when the **FUNDAMENTAL PURPOSE** is the same, even if:
- Different material (paper, plastic, bamboo, silicone, wood)
- Different form/application (liquid, solid, gel, powder, pencil)
- Different character/variant (Bumblebee vs Optimus Prime)
- Different brand (Nike vs Adidas vs Puma)
- Different features (nonslip, insulated, noise-canceling)
- Different size (mini, standard, large)
- Different color (red, blue, green)

---

## Partial Overlap Decision Framework

When primary uses partially overlap, use this structured approach:

### When to Apply Partial Overlap Framework
- Product uses overlap by 50-80%
- Keyword context suggests a specific subset of use cases
- Activity/feature modifiers create ambiguity

### The Overlap Tie-Breaker Question

**"If the customer could ONLY use the product for the keyword's implied use, would the product still fulfill its PRIMARY purpose?"**

| Answer | Classification | Example |
|--------|----------------|---------|
| YES → R (Relevant) | Same primary use | "hiking water bottle" for general water bottle - hiking IS portable hydration |
| NO → N (Negative) | Different primary use | "decorative bottle" for functional bottle - decoration ≠ hydration |

### Partial Overlap Examples

| ASIN Primary Use | Keyword | Overlap Analysis | Decision |
|------------------|---------|------------------|----------|
| "portable hydration" | "gym water bottle" | Gym use is SUBSET of portable use | **R** - same primary use |
| "portable hydration" | "decorative bottle" | Decoration is DIFFERENT purpose | **N** - different use |
| "personal audio" | "workout earbuds" | Workout is SUBSET of personal audio | **R** - same primary use |
| "personal audio" | "gaming earbuds" | Gaming has SPECIFIC requirements | **N** - different use (low latency, mic) |
| "sleep support" | "nap pillow" | Napping is SUBSET of sleep | **R** - same primary use |
| "sleep support" | "travel pillow" | Travel is DIFFERENT context | **N** - seated vs lying down |

### When Partial Overlap → Classify as R (Relevant)

The keyword represents a **SUBSET** of the primary use:
- Specific activity (gym, hiking, office) within general use
- Specific time (morning, night) within daily use
- Specific audience (kids, adults) within general audience

### When Partial Overlap → Classify as N (Negative)

The keyword represents a **DIFFERENT** primary function:
- Decorative vs functional
- Gaming vs entertainment (different requirements)
- Professional vs consumer (different quality needs)
- Travel vs home (different form factor needs)

---

## Confidence Calibration

| Scenario | Confidence Range |
|----------|------------------|
| Clear same use (synonyms, broader terms) | 0.93 - 0.98 |
| Same use with feature variation | 0.90 - 0.95 |
| Clear different use (context change) | 0.92 - 0.97 |
| Partial overlap - subset relationship (→R) | 0.85 - 0.92 |
| Partial overlap - different function (→N) | 0.85 - 0.92 |
| Edge case requiring judgment | 0.80 - 0.88 |
| Ambiguous context | 0.75 - 0.85 |

---

## Pre-Output Checklist

Before returning your answer, verify:

- [ ] Did I identify the ASIN's primary use from the validated_use field?
- [ ] Did I analyze what the keyword is actually asking for?
- [ ] Did I compare CORE functions, not just product names?
- [ ] Did I check for context words that change the use case?
- [ ] Did I distinguish between FEATURES and USE CASES?
- [ ] **CRITICAL: Am I being overly cautious?** If classifying as N, double-check:
  - [ ] Is the difference truly a USE CASE difference (decorative vs functional, gaming vs music)?
  - [ ] Or is it just a superficial difference (material, form, character, brand, feature)?
  - [ ] If superficial → classify as R, not N!
- [ ] Is my classification (R or N) based on PRIMARY use match?
- [ ] Does my reasoning clearly explain WHY the uses match or differ?
- [ ] Is my confidence score appropriate for the certainty level?

---

## Output Format

**IMPORTANT: Keep reasoning concise - 1-2 sentences maximum. Do NOT repeat or elaborate beyond what's necessary.**

```json
{
  "same_primary_use": true,
  "relevancy": "R",
  "confidence": 0.0-1.0,
  "reasoning": "Brief 1-2 sentence explanation"
}
```

**OR**

```json
{
  "same_primary_use": false,
  "relevancy": "N",
  "confidence": 0.0-1.0,
  "reasoning": "Brief 1-2 sentence explanation"
}
```

**Important:** This module produces a FINAL classification. R (Relevant) means the keyword is relevant to the ASIN. N (Negative) means the keyword is NOT relevant due to different primary use despite same product type.

