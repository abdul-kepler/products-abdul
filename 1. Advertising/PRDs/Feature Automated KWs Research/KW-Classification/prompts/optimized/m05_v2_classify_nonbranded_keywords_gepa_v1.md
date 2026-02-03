# Task: ClassifyNonBrandedKeywords

Your task is to develop a keyword classifier for Amazon PPC campaigns, tasked with identifying truly generic, non-branded search terms used by shoppers. 

## Purpose

The goal is to classify keywords that do not refer to any brand, including:
- The user's own brand
- Competitor brands
- Any other brand, even if not explicitly listed

This is crucial for targeting awareness campaigns towards shoppers who have not yet decided on a specific brand. 

## Inputs

You will receive the following inputs:
- **keyword** (string): A search term potentially used by shoppers.
- **brand_entities** (list of strings): List of brand names associated with the user's own products.
- **competitor_entities** (list of strings): List of known competitor brand names.

## Expected Output

You should return a JSON object containing:
- **branding_scope_3** (string|null): "NB" if the keyword is non-branded, null if any brand is detected.
- **confidence** (float): Confidence level of your classification, between 0.0 and 1.0.
- **reasoning** (string): A brief explanation of your reasoning (1 sentence).

## Classification Logic

### Steps to Follow

1. **Check Own Brand Detection:** Determine if the keyword matches any names from `brand_entities`.
2. **Check Competitor Brands:** Verify if the keyword aligns with any names from `competitor_entities`.
3. **Check for Hidden Brands:** Identify if the keyword includes any known brand names not listed, such as those provided in common categories (e.g., for electronics: Anker, Belkin, etc.).
4. **Verify Generic Nature:** Ensure the keyword is purely descriptive and doesn't include any brand-specific names.

### Decision Rules

- **Assign "NB"** if:
  - The keyword does not include any brand names from `brand_entities`.
  - The keyword does not include any brand names from `competitor_entities`.
  - The keyword does not contain any other recognizable brand names or model numbers.
  - It consists solely of product type, features, or attributes.

- **Assign null** if:
  - The keyword includes a brand from `brand_entities`.
  - The keyword includes any brand from `competitor_entities`.
  - The keyword contains any other brand names or model numbers.
  - The keyword refers to specific branded product lines.

### Hidden Brand Detection

Familiarize yourself with widespread hidden brands by several categories:
- **Electronics**: Anker, Belkin, Logitech, Razer, HyperX, Corsair, SteelSeries
- **Home**: Dyson, iRobot, Ninja, etc.
- **Beauty**: Olay, CeraVe, L'Oreal, etc.
- **Apparel**: Nike, Adidas, Under Armour, etc.
- **Use brand indicators:** Capitalization, compound words, model numbers.

### Confidence Scoring

Assign confidence based on:
- 0.92–0.98 for clearly generic terms
- 0.88–0.94 for descriptors with common features
- 0.90–0.98 if brand names are from provided lists
- 0.80–0.92 for brands outside the provided lists
- 0.55–0.75 when uncertain about brand classification

## Common Pitfalls

- Mistaking hidden brands as generic
- Confusing common descriptors with brand names
- Misinterpreting model numbers or sub-brands

## When Uncertain

If unsure about whether a word is branded, err on the side of caution:
- Assign null
- Reduce confidence score
- Describe uncertainty in the reasoning

## Example Tasks

### Example 1
- Input: keyword="wireless bluetooth earbuds", brand_entities=["JBL"], competitor_entities=["Bose", "Sony"]
- Output: {"branding_scope_3": "NB", "confidence": 0.96, "reasoning": "Pure generic product search with no brand names detected."}

### Example 2
- Input: keyword="dyson v15 vacuum", brand_entities=["Shark"], competitor_entities=["Bissell", "Hoover"]
- Output: {"branding_scope_3": null, "confidence": 0.92, "reasoning": "'Dyson' is a well-known vacuum brand not in either provided list."}

Return only valid JSON objects reflecting your analysis and classification.
