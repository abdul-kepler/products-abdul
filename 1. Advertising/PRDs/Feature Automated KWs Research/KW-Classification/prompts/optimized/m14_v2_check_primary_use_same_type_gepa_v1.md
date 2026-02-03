# Module 14 (V1.2): Primary Use Check (Same Product Type)

## Goal

To determine if a keyword describing a product type corresponds to the same primary intended use as an Amazon Standard Identification Number (ASIN) product. This involves analyzing buyer intent and product functionality to assess if products within the same category serve the same primary purpose. 

## Task Overview

Given inputs related to a product's demonstrated purpose and a keyword representing another product of the same type, assess if both products serve the identical primary use.

## Inputs

- **Keyword**: String representing the product search term.
- **Validated Use**: String indicating the main function of the ASIN, representing buyer's intent and primary purpose.

## Outputs

- A single character string: **"R"** for Relevant if the primary use matches, or **"N"** for Negative if they do not match.

## Steps for Determining Primary Use Match

1. **Identify ASIN Primary Use:**
   - Reference the Validated Use field to ascertain and clearly state the ASIN's primary purpose.

2. **Analyze Keyword Implied Use:**
   - Examine the keyword to determine the primary use it implies.
   - Identify context words that might suggest a particular use-case, which include characteristics like "decorative," "gaming," "travel," or "professional."

3. **Compare Core Functions:**
   - Evaluate if the primary function/service implied by the keyword aligns with the ASIN's function.
   - Consider whether a consumer seeking the keyword would expect the ASIN's primary use as their main goal.

4. **Check for Use-Case Divergence:**
   - Establish if the products share the same fundamental use or if they apply to different contexts (e.g., decorative vs. functional, gaming vs. music).

5. **Decision Making:**
   - If they serve the same primary purpose, classify as "R" (Relevant).
   - If they do not share the same primary purpose, classify as "N" (Negative).

## Critical Understanding

- **Superficial vs. Core Differences**: Avoid focusing on superficial differences such as material, design, brand, or added features. Concentrate on whether the product serves the same fundamental role.
- **Primary Use Contexts**:
  - Same use span variations in material, form, character, brand, features, color, and size.
  - Different use signifies fundamentally different purposes despite similar product types.

## Common Scenarios & Considerations

- **Same Use Example**: A "winter jacket with hood" validating cold weather body warmth can be marked as "R" since it aligns with a primary use of providing warmth.
- **Different Use Example**: If a keyword is "decorative pillow," but the ASIN is functional (for sleep support), classify as "N."
- **Feature Enhancements**: Recognize enhancements like "waterproof" or "nonslip" as not altering the core use.
- **Subset vs. Different Function**: Determine if the keyword is a subset of the validated use (→ R) or represents a different primary function (→ N).

## Key Insight

Only when the fundamental purpose diverges should a product be classified as "N." For cases with partial overlaps or enhancements, defer to "R" if the overarching primary function is maintained.
