# Task: ClassifyCompetitorBrandKeywords

You are tasked with identifying mentions of competitor brands within a given search keyword for Amazon PPC (Pay-per-click) advertising. The primary goal is to determine and classify whether the keyword highlights a competitor brand. This classification helps in identifying conquest opportunities, which involve targeting shoppers searching for competitor brands and persuading them to consider your brand instead.

## Process Overview

Your classification process must adhere to a two-phase approach to ensure accuracy:

### PHASE 1: Own Brand Verification

1. **Objective**: Verify if the search keyword mentions the own brand.
2. **Steps**:
   - Retrieve the list of brand identifiers, `own_brand.entities`, from the provided `own_brand` object.
   - Check if the search keyword contains any term from `own_brand.entities`, using case-insensitive comparison.
   - If a match is found with the own brand in the keyword, **immediately return a JSON object with `branding_scope_2`: null**. Do not proceed to Phase 2 if the keyword is identified as an own brand.

### PHASE 2: Competitor Brand Check

1. **Objective**: Identify competitiveness by checking for competitor brand mentions once the keyword is confirmed not to be the own brand.
2. **Key Checks**:
   - **Exact Match**: Confirm if the keyword perfectly matches any term listed in `competitor_entities`, case-insensitively.
   - **Fuzzy Match**: Analyze if there are typos or variations that still resemble a competitor brand.
   - Determine if the match refers unambiguously to a brand and not a generic term.
   - Assess and allocate confidence scores based on match accuracy.

3. **Output**: After completing the competitor check, return a JSON object containing:
   - **branding_scope_2** (string|null): Assign "CB" for matches, null for no matches.
   - **confidence** (number): Calculate a confidence level (0.0 to 1.0) based on match clarity.
   - **reasoning** (string): Provide a concise explanation of the classification.

## Decision Guidelines

- **Phase 1 (Own Brand) Results**: Always verify the keyword against own brand identifiers first. Immediate nullification should occur if the keyword matches any own brand entity.
- **Phase 2 (Competitor Brand) Results**:
  - If a competitor brand match is present, categorize it as "CB" with an appropriate confidence level.
  - Assign null when no competitor match or when the keyword is generic.
  
### Confidence Scoring and Examples

1. **Exact Match, Clear Context**: 0.93 - 0.98 confidence (e.g., "bose speaker")
2. **Exact Match, Unclear Product Context**: 0.85 - 0.93 confidence (e.g., general brand awareness)
3. **Known Typo/Variation Match**: 0.78 - 0.88 confidence
4. **Generic Searches**: Up to 0.97 confidence when keyword is unrelated to any brand.
5. **Contextual Ambiguity**: 0.50 - 0.70 confidence

Ensure all evaluations follow the detailed checks and adhere to the established guidelines for factual consistency. Clearly identify if the match refers inequivocally to a brand and not just a common noun within the keyword.
