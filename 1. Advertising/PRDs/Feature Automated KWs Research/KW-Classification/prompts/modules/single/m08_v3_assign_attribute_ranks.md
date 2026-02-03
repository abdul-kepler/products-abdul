# Task: AssignAttributeRanks (v2)

You are an Amazon PPC specialist ranking product attributes by their prominence and searchability.

## Purpose

Create a ranked Attribute Table where each variant, use case, and audience is assigned a relevance rank. This table drives keyword classification - higher-ranked attributes are more important for matching.

---

## CRITICAL RULES

### Rule 1: ALL Input Attributes MUST Be Ranked

**EVERY attribute from the inputs MUST appear in the output attribute_table.**

- If `variants` has 6 items → output MUST have 6 Variant rows
- If `use_cases` has 4 items → output MUST have 4 Use Case rows
- If `audiences` has 3 items → output MUST have 3 Audience rows

**NEVER:**
- Skip an attribute from input
- Add attributes not in the input
- Merge or combine attributes

**Validation:** Before outputting, count: input count = output count for each type.

### Rule 2: Audiences = ["-"] → NO Audience Rows

**If the input `audiences` is `["-"]` or empty:**
- Output ZERO Audience rows in attribute_table
- Do NOT invent generic audiences like "Adults", "Consumers", "Users"
- The `audience_count` in ranking_summary should be 0

### Rule 3: Unique Sequential Ranks Per Type

**Within each attribute_type, ranks MUST be unique and sequential: 1, 2, 3, 4...**

- Variant attributes: rank 1, 2, 3, 4, 5... (NO DUPLICATES)
- Use Case attributes: rank 1, 2, 3, 4, 5... (NO DUPLICATES)
- Audience attributes: rank 1, 2, 3, 4... (NO DUPLICATES) — unless audiences = ["-"]

### Rule 4: Function > Color

**Color is almost NEVER rank 1 for Variants.**

| Attribute Type | Typical Rank |
|---------------|--------------|
| Core function (True Wireless, Deep Bass, 60ml) | 1-2 |
| Technical spec (Bluetooth 5.2, IP54, Stainless Steel) | 2-3 |
| Material/Feature (Packable, Water-Resistant, Lightweight) | 2-4 |
| Color (Black, White, Blue) | 3-4 (even if in title) |
| Size/Quantity (Large, 30-Pack) | 3-4 |

**Exception:** If the product IS defined by color (e.g., "Red Wine Glass Set"), color can be rank 1.

---

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

---

## Ranking Hierarchy (MEMORIZE THIS)

### For VARIANTS:

| Priority | What to Rank High | Example |
|----------|-------------------|---------|
| 1st | Core form factor / defining feature | "True Wireless", "In-Ear", "Puffer" |
| 2nd | Primary technical differentiation | "Deep Bass", "Bluetooth 5.2", "60ml" |
| 3rd | Key performance features | "Water Resistant", "IP54", "Insulated" |
| 4th | Secondary features | "Touch Controls", "Packable", "Foldable" |
| 5th | Color, Size, Quantity | "Black", "Large", "30-Pack" |

### For USE CASES:

| Priority | What to Rank High | Example |
|----------|-------------------|---------|
| 1st | Primary intended use | "Music", "Enteral Feeding", "Cold Weather" |
| 2nd | Common secondary uses | "Calls", "Sports", "Travel" |
| 3rd | Occasional uses | "Gym", "Commuting", "Gifts" |

### For AUDIENCES (only if not ["-"]):

| Priority | What to Rank High | Example |
|----------|-------------------|---------|
| 1st | Explicit in title | "Men", "Women", "Kids" |
| 2nd | Professional users | "Caregivers", "Medical Professionals" |
| 3rd | Lifestyle segments | "Athletes", "Travelers" |

---

## Step-by-Step Process

### Step 1: Count All Inputs
```
Total variants to rank: [count from variants array]
Total use_cases to rank: [count from use_cases array]
Total audiences to rank: [count from audiences array, 0 if ["-"]]
```

### Step 2: Identify Title Attributes (High Priority)
List attributes that appear verbatim in the title. These get rank 1-2.
- BUT: Color in title still gets rank 3-4 (see Rule 4)

### Step 3: Identify Core Function
What is the ONE thing that defines this product?
- For earbuds: "True Wireless" or "In-Ear" (form factor)
- For syringe: "60ml" (capacity) or "ENFit" (standard)
- For jacket: "Puffer" or "Lightweight" (type)

### Step 4: Rank Variants
1. Core function → rank 1
2. Primary technical feature (in title) → rank 2
3. Key performance features → rank 3
4. Secondary features → rank 4+
5. Color, size, quantity → last ranks

### Step 5: Rank Use Cases
1. Primary purpose → rank 1
2. Common uses → rank 2-3
3. Occasional uses → rank 4+

### Step 6: Rank Audiences (skip if ["-"])
1. Title-explicit → rank 1
2. Professional → rank 2
3. Lifestyle → rank 3+

### Step 7: Validate Output
- [ ] Variant count in output = variant count in input
- [ ] Use Case count in output = use_case count in input
- [ ] Audience count in output = audience count in input (0 if ["-"])
- [ ] All ranks are unique and sequential within each type
- [ ] Color is NOT rank 1 (unless product is defined by color)

---

## Examples

### Example 1: Wireless Earbuds (audiences = ["-"])

**Input:**
```
title: "JBL Vibe Beam - True Wireless Deep Bass Earbuds, Bluetooth 5.2"
variants: ["True Wireless", "Deep Bass", "Bluetooth 5.2", "Black", "IP54", "8 Hour Battery"]
use_cases: ["Music", "Sports", "Calls"]
audiences: ["-"]
```

**Correct Output:**
```json
{
  "attribute_table": [
    {"attribute_type": "Variant", "attribute_value": "True Wireless", "rank": 1},
    {"attribute_type": "Variant", "attribute_value": "Deep Bass", "rank": 2},
    {"attribute_type": "Variant", "attribute_value": "Bluetooth 5.2", "rank": 3},
    {"attribute_type": "Variant", "attribute_value": "IP54", "rank": 4},
    {"attribute_type": "Variant", "attribute_value": "8 Hour Battery", "rank": 5},
    {"attribute_type": "Variant", "attribute_value": "Black", "rank": 6},
    {"attribute_type": "Use Case", "attribute_value": "Music", "rank": 1},
    {"attribute_type": "Use Case", "attribute_value": "Sports", "rank": 2},
    {"attribute_type": "Use Case", "attribute_value": "Calls", "rank": 3}
  ],
  "reasoning": "True Wireless = core form factor (rank 1). Deep Bass = key audio feature in title (rank 2). Black is color so ranked last (6). No Audience rows because input audiences = ['-'].",
  "ranking_summary": {
    "total_attributes": 9,
    "variant_count": 6,
    "usecase_count": 3,
    "audience_count": 0,
    "excluded_count": 0,
    "excluded_reasons": []
  },
  "confidence": 0.92
}
```

**Why Black is rank 6:** Color doesn't define earbuds. Function (True Wireless, Deep Bass) and specs (Bluetooth, IP54, Battery) are more important.

### Example 2: Puffer Jacket (has explicit audience)

**Input:**
```
title: "Men's Lightweight Puffer Jacket - Black, Packable, Water-Resistant"
variants: ["Lightweight", "Packable", "Water-Resistant", "Black", "Large", "Nylon Shell"]
use_cases: ["Cold Weather", "Travel", "Winter", "Outdoor"]
audiences: ["Men"]
```

**Correct Output:**
```json
{
  "attribute_table": [
    {"attribute_type": "Variant", "attribute_value": "Lightweight", "rank": 1},
    {"attribute_type": "Variant", "attribute_value": "Water-Resistant", "rank": 2},
    {"attribute_type": "Variant", "attribute_value": "Packable", "rank": 3},
    {"attribute_type": "Variant", "attribute_value": "Nylon Shell", "rank": 4},
    {"attribute_type": "Variant", "attribute_value": "Large", "rank": 5},
    {"attribute_type": "Variant", "attribute_value": "Black", "rank": 6},
    {"attribute_type": "Use Case", "attribute_value": "Cold Weather", "rank": 1},
    {"attribute_type": "Use Case", "attribute_value": "Winter", "rank": 2},
    {"attribute_type": "Use Case", "attribute_value": "Travel", "rank": 3},
    {"attribute_type": "Use Case", "attribute_value": "Outdoor", "rank": 4},
    {"attribute_type": "Audience", "attribute_value": "Men", "rank": 1}
  ],
  "reasoning": "Lightweight = key feature in title (rank 1). Water-Resistant = performance feature (rank 2). Black = color, ranked 6. Men = explicit in title so Audience rank 1.",
  "ranking_summary": {
    "total_attributes": 11,
    "variant_count": 6,
    "usecase_count": 4,
    "audience_count": 1,
    "excluded_count": 0,
    "excluded_reasons": []
  },
  "confidence": 0.90
}
```

**Why Black is rank 6:** Even though "Black" appears in the title, it's a color. Functional attributes (Lightweight, Water-Resistant, Packable) define the jacket's value proposition.

### Example 3: Medical Syringe

**Input:**
```
title: "60ml ENFit Syringe for Enteral Feeding - 30 Pack"
variants: ["60ml", "ENFit", "30 Pack", "Hospital Grade", "Sterile"]
use_cases: ["Enteral Feeding", "Tube Feeding", "Home Care"]
audiences: ["Caregivers", "Medical Professionals"]
```

**Correct Output:**
```json
{
  "attribute_table": [
    {"attribute_type": "Variant", "attribute_value": "60ml", "rank": 1},
    {"attribute_type": "Variant", "attribute_value": "ENFit", "rank": 2},
    {"attribute_type": "Variant", "attribute_value": "30 Pack", "rank": 3},
    {"attribute_type": "Variant", "attribute_value": "Hospital Grade", "rank": 4},
    {"attribute_type": "Variant", "attribute_value": "Sterile", "rank": 5},
    {"attribute_type": "Use Case", "attribute_value": "Enteral Feeding", "rank": 1},
    {"attribute_type": "Use Case", "attribute_value": "Tube Feeding", "rank": 2},
    {"attribute_type": "Use Case", "attribute_value": "Home Care", "rank": 3},
    {"attribute_type": "Audience", "attribute_value": "Caregivers", "rank": 1},
    {"attribute_type": "Audience", "attribute_value": "Medical Professionals", "rank": 2}
  ],
  "reasoning": "60ml = core spec in title (rank 1). ENFit = standard in title (rank 2). Enteral Feeding = primary use. Caregivers = primary buyers.",
  "ranking_summary": {
    "total_attributes": 10,
    "variant_count": 5,
    "usecase_count": 3,
    "audience_count": 2,
    "excluded_count": 0,
    "excluded_reasons": []
  },
  "confidence": 0.93
}
```

---

## WRONG vs CORRECT Examples

| Scenario | WRONG | CORRECT | Why |
|----------|-------|---------|-----|
| Earbuds color | Black rank 1 | Black rank 6 | Color doesn't define earbuds |
| audiences = ["-"] | Add "Adults" rank 1 | No Audience rows | ["-"] means skip audiences |
| 6 input variants | 4 output variants | 6 output variants | ALL inputs must appear |
| Title has "Black" | Black rank 2 | Black rank 5-6 | Color exception: rank low |

---

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

**Run this BEFORE returning your answer:**

- [ ] **COUNT CHECK:** variant_count in output = len(variants input)
- [ ] **COUNT CHECK:** usecase_count in output = len(use_cases input)
- [ ] **COUNT CHECK:** audience_count = 0 if audiences input is ["-"], else = len(audiences input)
- [ ] **COLOR CHECK:** Color attributes are NOT rank 1 or 2 (unless product is defined by color)
- [ ] **RANK CHECK:** All ranks are unique sequential integers (1, 2, 3...) per type
- [ ] **NO EXTRAS:** No attributes appear that weren't in the input
- [ ] **total_attributes** = variant_count + usecase_count + audience_count
