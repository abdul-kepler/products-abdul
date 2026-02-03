# Task: GenerateProductTypeTaxonomy

You are an Amazon marketplace expert creating a simple product type taxonomy.

## Purpose

Generate a SHORT taxonomy (1-3 levels) describing what this product IS. Start with the most specific product type, then optionally add 1-2 broader categories.

## Inputs

- **title**: {{title}}
- **bullet_points**: {{bullet_points}}
- **description**: {{description}}
- **product_type**: {{product_type}}
- **category_root**: {{category_root}}
- **category_sub**: {{category_sub}}

## Expected Output

- **taxonomy** (array): 1-3 entries from specific to general
  - `{level: 1, product_type: "Most Specific", rank: 1}` - REQUIRED
  - `{level: 2, product_type: "Broader", rank: 2}` - OPTIONAL
  - `{level: 3, product_type: "Broadest", rank: 3}` - OPTIONAL

## ⚠️ CRITICAL RULES

1. **RANK ALWAYS EQUALS LEVEL**: rank 1 for level 1, rank 2 for level 2, rank 3 for level 3
2. **MAXIMUM 3 entries** - never more than 3 items in taxonomy
3. **Level 1 = MOST SPECIFIC** - the exact product type shoppers search for
4. **Simple products need only 1 level** - if product is self-explanatory, use 1 entry
5. **Use "/" for alternatives** - e.g., "Puffer Jacket / Puffy Coat"

## ⚠️ KEY DECISION: When to Add Levels

**Ask yourself: "Is this a DISTINCT product subcategory that shoppers search for separately?"**

### ❌ DO NOT create extra levels for MATERIAL/FEATURE MODIFIERS:
These words describe HOW a product is made, not WHAT it is:
- Insulated, Stainless Steel, Silicone, Bamboo, Ceramic, Wooden, Plastic
- Ribbed, Quilted, Padded, Textured
- Portable, Foldable, Compact, Mini, Large

**Examples of WRONG multi-level outputs:**
- ❌ "Insulated Water Bottle → Water Bottle" - WRONG (just use "Water Bottle")
- ❌ "Silicone Oven Mitt → Oven Mitt" - WRONG (just use "Oven Mitt")
- ❌ "Bamboo Serving Tray → Serving Tray" - WRONG (just use "Serving Tray")
- ❌ "Stainless Steel Ice Maker → Ice Maker" - WRONG (just use "Ice Maker")

### ✅ DO create extra levels for TRUE PRODUCT VARIANTS:
These are distinct product types that shoppers search for as separate categories:
- "ENFit Syringe" (specialized medical standard) → "Syringe"
- "Pencil Eyeliner" (distinct from liquid/gel) → "Eyeliner"
- "True Wireless Earbuds" (distinct technology) → "Wireless Earphones"
- "Puffer Jacket" (distinct style shoppers search for) → "Jacket"

## When to Use 1, 2, or 3 Levels

### Use 1 Level (simple, everyday products):
Products where the basic name is what shoppers search for, regardless of materials or features:
- Water Bottle (not "Insulated Water Bottle")
- Oven Mitt (not "Silicone Oven Mitt")
- Ice Maker (not "Countertop Ice Maker")
- Serving Tray (not "Bamboo Serving Tray")
- Car Phone Holders & Mounts

### Use 2 Levels (when there's a true product subcategory):
The first level is a distinct product type shoppers search for specifically:
- ENFit Syringe → Syringe (ENFit is a specific medical connector standard)
- Kitchen Sink Caddy → Kitchen Caddy Organizer

### Use 3 Levels (when product has clear hierarchy with distinct subcategories):
- True Wireless Earbuds → Wireless Earphones → Earphones
- Puffer Jacket → Jacket → Men's Clothing
- Transformer → Action Figure → Toys
- Pencil Eyeliner → Eyeliner → Eye Makeup

## Examples from Dataset

**Example 1 - Simple product (1 level):**
```
title: "Owala FreeSip Insulated Stainless Steel Water Bottle"
product_type: "BOTTLE"
```
```json
{"taxonomy": [{"level": 1, "product_type": "Water Bottle", "rank": 1}]}
```

**Example 2 - Simple product (1 level):**
```
title: "KITCHENAID Ribbed Soft Silicone Oven Mitt 2-Pack Set"
product_type: "POT_HOLDER"
```
```json
{"taxonomy": [{"level": 1, "product_type": "Oven Mitt", "rank": 1}]}
```

**Example 3 - Two levels:**
```
title: "ENFit® Syringe - 20ml - QTY 10"
product_type: "SYRINGE"
```
```json
{
  "taxonomy": [
    {"level": 1, "product_type": "ENFit Syringe", "rank": 1},
    {"level": 2, "product_type": "Syringe", "rank": 2}
  ]
}
```

**Example 4 - Three levels:**
```
title: "JBL Vibe Beam - True Wireless JBL Deep Bass Sound Earbuds"
product_type: "HEADPHONES"
```
```json
{
  "taxonomy": [
    {"level": 1, "product_type": "True Wireless Earbuds", "rank": 1},
    {"level": 2, "product_type": "Wireless Earphones", "rank": 2},
    {"level": 3, "product_type": "Earphones", "rank": 3}
  ]
}
```

**Example 5 - Three levels with alternatives:**
```
title: "Pioneer Camp Mens Lightweight Packable Puffer Jacket"
product_type: "COAT"
```
```json
{
  "taxonomy": [
    {"level": 1, "product_type": "Puffer Jacket / Puffy Coat", "rank": 1},
    {"level": 2, "product_type": "Jacket", "rank": 2},
    {"level": 3, "product_type": "Men's Clothing / Apparel", "rank": 3}
  ]
}
```

**Example 6 - Three levels:**
```
title: "Transformers Toys Heroic Optimus Prime Action Figure"
product_type: "TOY_FIGURE"
```
```json
{
  "taxonomy": [
    {"level": 1, "product_type": "Transformer", "rank": 1},
    {"level": 2, "product_type": "Action Figure", "rank": 2},
    {"level": 3, "product_type": "Toys", "rank": 3}
  ]
}
```

**Example 7 - One level:**
```
title: "Jikasho Vacuum Magnetic Suction Phone Holder for Car"
product_type: "PORTABLE_ELECTRONIC_DEVICE_MOUNT"
```
```json
{"taxonomy": [{"level": 1, "product_type": "Car Phone Holders & Mounts", "rank": 1}]}
```

**Example 8 - Three levels:**
```
title: "Revlon ColorStay Pencil Waterproof Eyeliner"
product_type: "EYELID_COLOR"
```
```json
{
  "taxonomy": [
    {"level": 1, "product_type": "Pencil Eyeliner", "rank": 1},
    {"level": 2, "product_type": "Eyeliner", "rank": 2},
    {"level": 3, "product_type": "Eye Makeup", "rank": 3}
  ]
}
```

## What NOT to Include

❌ **NO brand names** - "JBL Earbuds" → just "Earbuds"
❌ **NO size/quantity** - "20ml Syringe" → just "Syringe"
❌ **NO colors** - "Black Jacket" → just "Jacket"
❌ **NO material prefixes as separate levels** - "Bamboo Serving Tray" → just "Serving Tray" (1 level)
❌ **NO feature prefixes as separate levels** - "Insulated Water Bottle" → just "Water Bottle" (1 level)
❌ **NO unnecessary categories** - Don't add "Medical Equipment", "Electronics", "Home & Kitchen"
❌ **NO more than 3 levels**
❌ **NO duplicate concepts** - Don't have both "Earbuds" and "Earphones" at different levels

## Common Mistakes to Avoid

| Product Title | ❌ WRONG Output | ✅ CORRECT Output |
|---------------|-----------------|-------------------|
| "Insulated Stainless Steel Water Bottle" | Insulated Water Bottle → Water Bottle | Water Bottle (1 level) |
| "Silicone Oven Mitt 2-Pack" | Silicone Oven Mitt → Oven Mitt | Oven Mitt (1 level) |
| "Bamboo Serving Tray" | Bamboo Serving Tray → Serving Tray | Serving Tray (1 level) |
| "Countertop Ice Maker" | Countertop Ice Maker → Ice Maker | Ice Maker (1 level) |
| "Magnetic Car Phone Mount" | Magnetic Phone Mount → Phone Mount | Car Phone Holders & Mounts (1 level) |

**Remember**: Materials (bamboo, silicone, stainless steel) and features (insulated, magnetic, countertop) are NOT separate product categories - they describe the SAME product.

## Output Format

Return ONLY valid JSON:
```json
{"taxonomy": [{"level": 1, "product_type": "...", "rank": 1}]}
```
or
```json
{"taxonomy": [{"level": 1, "product_type": "...", "rank": 1}, {"level": 2, "product_type": "...", "rank": 2}]}
```
or
```json
{"taxonomy": [{"level": 1, "product_type": "...", "rank": 1}, {"level": 2, "product_type": "...", "rank": 2}, {"level": 3, "product_type": "...", "rank": 3}]}
```
