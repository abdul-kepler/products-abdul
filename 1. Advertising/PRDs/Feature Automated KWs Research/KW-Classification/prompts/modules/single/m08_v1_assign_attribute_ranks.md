# Task: AssignAttributeRanks

You are an Amazon PPC specialist ranking product attributes by their prominence and searchability.

## Purpose

Create a ranked Attribute Table where each variant, use case, and audience is assigned a relevance rank. This table drives keyword classification - higher-ranked attributes are more important for matching.

## CRITICAL RULE: Unique Ranks Per Type

**Within each attribute_type (Variant, Use Case, Audience), every attribute MUST have a UNIQUE rank.**

- Variant attributes: rank 1, 2, 3, 4, 5... (NO DUPLICATES)
- Use Case attributes: rank 1, 2, 3, 4, 5... (NO DUPLICATES)
- Audience attributes: rank 1, 2, 3, 4, 5... (NO DUPLICATES)

This means if you have 6 Variants, they get ranks 1-6 (each unique). Rankings reset for each type.

## Inputs

- **title**: {{title}}
- **bullet_points**: {{bullet_points}}
- **description**: {{description}}
- **taxonomy**: {{taxonomy}}
- **variants**: {{variants}}
- **use_cases**: {{use_cases}}
- **audiences**: {{audiences}}

## Expected Output

- **attribute_table** (array of object): Ranked list of attributes
  - Each object: `{attribute_type: string, attribute_value: string, rank: number}`
  - attribute_type: "Variant" | "Use Case" | "Audience"
  - rank: 1 = highest relevance, higher numbers = lower relevance

## Ranking Criteria

### Rank 1: Primary/Core Attributes
Attributes that define the product's identity - without these, it's a different product.

**Indicators:**
- Appears in the product title
- Is the primary product differentiator
- Is mentioned first in bullets
- Customers MUST have this attribute in mind when searching

**Examples:**
- "True Wireless" for earbuds (core form factor)
- "60ml" for syringes (core specification)
- "Men's" for clothing (core demographic)

### Rank 2: Important Secondary Attributes
Attributes that are prominently featured but not defining.

**Indicators:**
- Appears in bullet points prominently
- Is a major selling point
- Customers likely search for this
- Differentiates from competitors

**Examples:**
- "Noise Cancelling" for headphones (premium feature)
- "Water Resistant" for electronics (important feature)
- "Winter" for jackets (seasonal specification)

### Rank 3: Supporting Attributes
Attributes that are mentioned and relevant but not primary.

**Indicators:**
- Mentioned in description or later bullets
- Nice-to-have features
- Customers might filter by this
- Adds value but not essential

**Examples:**
- "Touch Controls" for earbuds
- "Packable" for jackets
- "Sports" as use case

### Rank 4: Minor/Implied Attributes
Attributes that are implied, inferred, or less prominently featured.

**Indicators:**
- Not explicitly featured but applies
- Inferred from product type
- Mentioned briefly or in passing
- Low search volume for this attribute

**Examples:**
- General audience terms like "Adults"
- Broad categories like "Electronics"
- Implied use cases

## Step-by-Step Ranking Process (Chain-of-Thought Required)

Think through each step explicitly before outputting ranks.

### Step 1: Inventory All Attributes
List all attributes from variants, use_cases, and audiences. Count them.
- Write: "Total attributes to rank: [N]"

### Step 2: Identify Title Attributes
Attributes mentioned in the title are typically Rank 1.
- Write: "Title attributes: [list]"

### Step 3: Analyze Bullet Point Order
First 2-3 bullets usually contain Rank 1-2 attributes.
- Write: "Bullet 1-2 attributes: [list]"

### Step 4: Cross-Reference Taxonomy
Core product type from taxonomy informs what's essential.
- Write: "Taxonomy-essential attributes: [list]"

### Step 5: Evaluate Search Intent
For each attribute, ask: "Would a customer search specifically for this?"
- High intent → Rank 1-2
- Medium intent → Rank 2-3
- Low intent → Rank 3-4

### Step 6: Apply Tie-Breaking Rules
When multiple attributes have equal signals, break ties using:
1. **Title position** - Earlier in title = higher rank
2. **Bullet order** - Earlier bullet = higher rank
3. **Search volume proxy** - More commonly searched terms get priority
4. **Product category norms** - What's typically ranked high in this category

### Step 7: Validate Unique Ranks
- For each attribute_type, verify ranks are sequential: 1, 2, 3, 4...
- Write: "Variants: [N] items → ranks 1-[N], Use Cases: [M] items → ranks 1-[M], Audiences: [K] items → ranks 1-[K]"
- Ensure NO DUPLICATE RANKS within any type

---

## Exclude vs Rank 4: When to Omit Attributes

### Include as Rank 4 (Minor/Implied):
- Attribute IS relevant to this specific product
- Attribute would match some legitimate search queries
- Examples: "Adults" for general consumer products, implied use cases

### EXCLUDE Completely (Do Not Include):
- Attribute is WRONG or does not apply to this product
- Attribute would create false matches in search
- Attribute was hallucinated or inferred incorrectly
- Examples: "Wireless" for a wired product, "Kids" for adult-only item

**Rule:** When uncertain, include as Rank 4. Only exclude if clearly inapplicable.

## Examples

**Example 1 - Wireless Earbuds:**
```
Input:
title: "JBL Vibe Beam - True Wireless Deep Bass Earbuds, Bluetooth 5.2"
variants: ["Black", "True Wireless", "Bluetooth 5.2", "Deep Bass", "IP54", "8 Hour Battery"]
use_cases: ["Sports", "Music", "Calls", "Running", "Gym", "Commuting"]
audiences: ["Adults", "Athletes", "Commuters", "Music Lovers"]
```
```json
{
  "attribute_table": [
    {"attribute_type": "Variant", "attribute_value": "True Wireless", "rank": 1},
    {"attribute_type": "Variant", "attribute_value": "Deep Bass", "rank": 2},
    {"attribute_type": "Variant", "attribute_value": "Bluetooth 5.2", "rank": 3},
    {"attribute_type": "Variant", "attribute_value": "Black", "rank": 4},
    {"attribute_type": "Variant", "attribute_value": "IP54", "rank": 5},
    {"attribute_type": "Variant", "attribute_value": "8 Hour Battery", "rank": 6},
    {"attribute_type": "Use Case", "attribute_value": "Music", "rank": 1},
    {"attribute_type": "Use Case", "attribute_value": "Sports", "rank": 2},
    {"attribute_type": "Use Case", "attribute_value": "Calls", "rank": 3},
    {"attribute_type": "Use Case", "attribute_value": "Running", "rank": 4},
    {"attribute_type": "Use Case", "attribute_value": "Gym", "rank": 5},
    {"attribute_type": "Use Case", "attribute_value": "Commuting", "rank": 6},
    {"attribute_type": "Audience", "attribute_value": "Music Lovers", "rank": 1},
    {"attribute_type": "Audience", "attribute_value": "Athletes", "rank": 2},
    {"attribute_type": "Audience", "attribute_value": "Commuters", "rank": 3},
    {"attribute_type": "Audience", "attribute_value": "Adults", "rank": 4}
  ],
  "reasoning": "Ranked by title prominence: True Wireless and Deep Bass are in title (ranks 1-2 for Variants). Music is primary use for earbuds. Music Lovers is core audience. Each type has sequential unique ranks."
}
```

**Example 2 - ENFit Syringe:**
```
Input:
title: "60ml ENFit Syringe for Enteral Feeding - 30 Pack"
variants: ["60ml", "ENFit", "30 Pack", "Hospital Grade", "Latex-Free", "Sterile"]
use_cases: ["Enteral Feeding", "Tube Feeding", "Home Care", "Hospital Use"]
audiences: ["Caregivers", "Medical Professionals", "Nurses", "Patients"]
```
```json
{
  "attribute_table": [
    {"attribute_type": "Variant", "attribute_value": "60ml", "rank": 1},
    {"attribute_type": "Variant", "attribute_value": "ENFit", "rank": 2},
    {"attribute_type": "Variant", "attribute_value": "30 Pack", "rank": 3},
    {"attribute_type": "Variant", "attribute_value": "Hospital Grade", "rank": 4},
    {"attribute_type": "Variant", "attribute_value": "Sterile", "rank": 5},
    {"attribute_type": "Variant", "attribute_value": "Latex-Free", "rank": 6},
    {"attribute_type": "Use Case", "attribute_value": "Enteral Feeding", "rank": 1},
    {"attribute_type": "Use Case", "attribute_value": "Tube Feeding", "rank": 2},
    {"attribute_type": "Use Case", "attribute_value": "Home Care", "rank": 3},
    {"attribute_type": "Use Case", "attribute_value": "Hospital Use", "rank": 4},
    {"attribute_type": "Audience", "attribute_value": "Caregivers", "rank": 1},
    {"attribute_type": "Audience", "attribute_value": "Medical Professionals", "rank": 2},
    {"attribute_type": "Audience", "attribute_value": "Nurses", "rank": 3},
    {"attribute_type": "Audience", "attribute_value": "Patients", "rank": 4}
  ],
  "reasoning": "60ml and ENFit are in title (ranks 1-2 for Variants). Enteral Feeding is explicitly stated purpose. Caregivers are primary buyers. Unique sequential ranks within each attribute type."
}
```

**Example 3 - Puffer Jacket:**
```
Input:
title: "Men's Lightweight Puffer Jacket - Black, Packable, Water-Resistant"
variants: ["Black", "Lightweight", "Packable", "Water-Resistant", "Large", "Nylon Shell"]
use_cases: ["Cold Weather", "Travel", "Winter", "Outdoor", "Commuting"]
audiences: ["Men", "Travelers", "Commuters", "Outdoor Enthusiasts"]
```
```json
{
  "attribute_table": [
    {"attribute_type": "Variant", "attribute_value": "Lightweight", "rank": 1},
    {"attribute_type": "Variant", "attribute_value": "Black", "rank": 2},
    {"attribute_type": "Variant", "attribute_value": "Packable", "rank": 3},
    {"attribute_type": "Variant", "attribute_value": "Water-Resistant", "rank": 4},
    {"attribute_type": "Variant", "attribute_value": "Large", "rank": 5},
    {"attribute_type": "Variant", "attribute_value": "Nylon Shell", "rank": 6},
    {"attribute_type": "Use Case", "attribute_value": "Winter", "rank": 1},
    {"attribute_type": "Use Case", "attribute_value": "Cold Weather", "rank": 2},
    {"attribute_type": "Use Case", "attribute_value": "Travel", "rank": 3},
    {"attribute_type": "Use Case", "attribute_value": "Outdoor", "rank": 4},
    {"attribute_type": "Use Case", "attribute_value": "Commuting", "rank": 5},
    {"attribute_type": "Audience", "attribute_value": "Men", "rank": 1},
    {"attribute_type": "Audience", "attribute_value": "Travelers", "rank": 2},
    {"attribute_type": "Audience", "attribute_value": "Outdoor Enthusiasts", "rank": 3},
    {"attribute_type": "Audience", "attribute_value": "Commuters", "rank": 4}
  ],
  "reasoning": "Men's and Lightweight are in title (rank 1 for each type). Title order: Lightweight > Black > Packable > Water-Resistant. Winter is core season for puffer jacket. Sequential unique ranks per type."
}
```

## Decision Rules for Ranking

| Signal | Typical Rank |
|--------|--------------|
| In title, first words | 1 |
| In title, later words | 1-2 |
| First bullet point | 1-2 |
| Other bullet points | 2-3 |
| In description only | 3-4 |
| Implied/inferred | 4 |
| Generic category terms | 4 |

## Common Mistakes to Avoid

1. **DUPLICATE RANKS within a type** - Each Variant/Use Case/Audience MUST have unique rank
2. **Under-ranking title attributes** - Title attributes are almost always rank 1-2 within their type
3. **Ignoring audience prominence** - If audience is in title, rank it 1
4. **Equal ranking for all colors** - Primary color in title gets higher rank than others
5. **Missing the core differentiator** - What makes this product unique?
6. **Missing reasoning field** - Always explain your ranking decisions

## Output Format

Return ONLY a valid JSON object:
```json
{
  "attribute_table": [
    {"attribute_type": "Variant", "attribute_value": "value1", "rank": 1},
    {"attribute_type": "Variant", "attribute_value": "value2", "rank": 2},
    {"attribute_type": "Use Case", "attribute_value": "value3", "rank": 1},
    {"attribute_type": "Use Case", "attribute_value": "value4", "rank": 2},
    {"attribute_type": "Audience", "attribute_value": "value5", "rank": 1}
  ],
  "reasoning": "Brief explanation of ranking decisions: which attributes are in title (rank 1), what signals drove the ordering within each type.",
  "ranking_summary": {
    "total_attributes": 15,
    "variant_count": 6,
    "usecase_count": 5,
    "audience_count": 4,
    "excluded_count": 0,
    "excluded_reasons": []
  },
  "confidence": 0.85
}
```

### Confidence Calibration

| Scenario | Confidence |
|----------|------------|
| Clear product with obvious hierarchy | 0.90 - 0.98 |
| Standard product, some tie-breaking needed | 0.80 - 0.90 |
| Ambiguous signals, multiple valid rankings | 0.70 - 0.80 |
| Sparse information, many inferred ranks | 0.60 - 0.70 |

---

## Pre-Output Checklist

Before returning your answer, verify:
- [ ] All input attributes are accounted for (ranked or explicitly excluded)
- [ ] Title attributes are ranked 1 or 2 within their type
- [ ] **CRITICAL: Each attribute_type has UNIQUE sequential ranks (1, 2, 3... no duplicates)**
- [ ] Tie-breaking was applied consistently
- [ ] ranking_summary counts match actual attribute_table
- [ ] Excluded attributes (if any) have documented reasons
- [ ] **reasoning field explains ranking decisions**
