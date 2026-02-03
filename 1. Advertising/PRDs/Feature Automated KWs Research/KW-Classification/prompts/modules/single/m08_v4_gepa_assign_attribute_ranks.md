# Task: Assign and Rank Product Attributes

You are tasked with analyzing a given list of product attributes and assigning them a rank based on their relevance, prominence, and searchability. The ranked list will help in keyword classification where higher-ranked attributes have more significance for accurate search matching.

## Purpose

To create a ranked Attribute Table where each variant, use case, and audience is assigned a relevance rank. This is essential to identify the most prominent features of a product for effective Amazon PPC (Pay-Per-Click) marketing strategies.

## Critical Rule: Unique Ranks Per Attribute Type

**Within each attribute type (Variant, Use Case, Audience), every attribute MUST have a UNIQUE rank.**

- Variants: assign ranks 1, 2, 3,... as needed (NO DUPLICATES)
- Use Case attributes: assign ranks 1, 2, 3,... as needed (NO DUPLICATES)
- Audiences: assign ranks 1, 2, 3,... as needed (NO DUPLICATES)

Rankings reset for each attribute type.

## Inputs

- **title**: The product's title.
- **bullet_points**: Key points that highlight the product's features.
- **description**: Detailed product description.
- **taxonomy**: Product categorization.
- **variants**: List of product variants.
- **use_cases**: List of use cases for the product.
- **audiences**: Target audience of the product.

## Expected Output

- **attribute_table** (array of objects): Ranked list of attributes.
  - Each object: `{attribute_type: string, attribute_value: string, rank: number}`
  - attribute_type: "Variant" | "Use Case" | "Audience"
  - rank: 1 = highest relevance, higher numbers = lower relevance.

## Ranking Criteria

### Rank 1: Primary/Core Attributes
- Key attributes defining the product's identity. Without these, it’s a different product.
- Indicators: Present in the title, primary differentiators, or prominently in bullet points.

### Rank 2: Important Secondary Attributes
- Features that are crucial but not defining.
- Indicators: Prominently featured in bullet points, major selling points.

### Rank 3: Supporting Attributes
- Features that add value and are nice to have but are not critical.
- Indicators: Mentioned in description or later bullets.

### Rank 4: Minor/Implied Attributes
- Features that are mentioned briefly or implied.
- Indicators: Relevant but less significant.

## Step-by-Step Approach

1. **Inventory All Attributes**: Count and list attributes from variants, use_cases, and audiences.
2. **Identify Title Attributes**: Determine which attributes are mentioned in the title.
3. **Analyze Bullet Points**: Examine the first few bullet points for important features.
4. **Cross-Reference Taxonomy**: Use the core product type from taxonomy to identify essential features.
5. **Evaluate Search Intent**: Determine customer search intent for each attribute.
6. **Apply Tie-Breakers**:
   - Title Position: Earlier in title = higher rank.
   - Bullet Order: Earlier bullet = higher rank.
   - Search Volume: More common terms = higher rank.
   - Product Norms: Prioritize attributes typical to the product category.
7. **Validate Unique Ranks**: Ensure each attribute type has a unique, sequential rank.

## Decision Rule for Exclusion

Attributes can be included as Rank 4 if they are relevant but implied, and should only be excluded if they are factually inapplicable to the product.

## Output Format

Return a JSON object:
```json
{
  "attribute_table": [
    {"attribute_type": "Variant", "attribute_value": "value1", "rank": 1},
    {"attribute_type": "Use Case", "attribute_value": "value2", "rank": 2},
    {"attribute_type": "Audience", "attribute_value": "value3", "rank": 1}
  ],
  "reasoning": "Explanation of how ranks were determined with reference to the title, bullet points, and product differentiators.",
  "ranking_summary": {
    "total_attributes": X,
    "variant_count": Y,
    "usecase_count": Z,
    "audience_count": A,
    "excluded_count": B,
    "excluded_reasons": []
  },
  "confidence": 0.XX
}
```

## Confidence Calibration

Confidence in the ranking should be adjusted based on how clearly the attributes are identified and ranked.

- **0.90 - 0.98**: Clear and well-defined product hierarchy.
- **0.80 - 0.90**: Standard product with some ambiguity.
- **0.70 - 0.80**: Ambiguous product identity with multiple possible rankings.
- **0.60 - 0.70**: Sparse data, with many inferred decisions.

## Pre-Output Checklist

- All input attributes accounted for (ranked or explicitly excluded).
- Followed ranking principles, ensuring unique ranks within each type.
- Consistent tie-breaking application.
- Matches between ranking summary and attribute table.
- Clear reasoning for rankings provided.
