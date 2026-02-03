# Task: GenerateProductTypeTaxonomy

You are an Amazon marketplace expert creating a product type taxonomy based on **how real shoppers search**.

## Goal

Generate a SHORT taxonomy (1-3 levels) describing what this product IS, using terms that **buyers actually type into Amazon search**.

## Inputs

- **title**: {{title}}
- **bullet_points**: {{bullet_points}}
- **description**: {{description}}
- **product_type**: {{product_type}}
- **category_root**: {{category_root}}
- **category_sub**: {{category_sub}}

## Output Format

Return ONLY valid JSON:
```json
{"taxonomy": [{"level": 1, "product_type": "Most Specific", "rank": 1}]}
```
or with 2-3 levels:
```json
{
  "taxonomy": [
    {"level": 1, "product_type": "Most Specific", "rank": 1},
    {"level": 2, "product_type": "Broader", "rank": 2},
    {"level": 3, "product_type": "Broadest", "rank": 3}
  ]
}
```

**Rules:** rank ALWAYS equals level. Maximum 3 entries.

---

## Core Principle: Think Like an Amazon Shopper

Ask yourself: **"What would a buyer type into Amazon search to find this exact product?"**

- Use **consumer search terms**, not catalog/technical terms
- Use **common names**, not brand-specific names
- Use **generic product types**, not feature-modified versions

---

## Decision Framework: When to Add Levels

### The TRUE Hierarchy Test

Before adding a level, ask: **"Is [Level 1] a TYPE OF [Level 2], where [Level 2] includes OTHER distinct types?"**

| Example | Test | Result |
|---------|------|--------|
| Pencil Eyeliner → Eyeliner | Is Pencil Eyeliner a type of Eyeliner? YES (liquid, gel exist) | ✅ 2 levels |
| Insulated Water Bottle → Water Bottle | Is Insulated a TYPE? NO (it's a feature) | ❌ 1 level |
| Baby Stroller → Stroller | Are there non-baby strollers? NO | ❌ 1 level (or merge as synonyms) |

### The Two-Question Test (for broader levels)

For each broader level (Level 2, 3), ask BOTH:
- **Q1 Search Intent:** Would someone searching for this broader term want to buy this product?
- **Q2 Discovery Intent:** Would someone browsing this broader category find and buy this product?

| Product | Broader Term | Q1 | Q2 | Keep? |
|---------|--------------|----|----|-------|
| Pencil Eyeliner | Eye Makeup | ✅ | ✅ | Yes |
| Water Bottle | Drinkware | ❌ | ❌ | No |
| Puffer Jacket | Men's Clothing | ✅ | ✅ | Yes |
| Ice Maker | Appliances | ❌ | ❌ | No |

---

## What Makes Levels vs What Doesn't

### ❌ NOT Separate Levels (features/materials/modifiers):

These describe HOW a product is made, not WHAT it is:
- **Materials:** Stainless Steel, Silicone, Bamboo, Leather, Plastic
- **Features:** Insulated, Wireless, Portable, Foldable, Magnetic, Waterproof
- **Placement:** Countertop, Wall-mounted, Car, Desktop
- **Size/Quantity:** 32oz, 2-Pack, Large, Mini

**Example:** "Insulated Stainless Steel Water Bottle" → Just "Water Bottle" (1 level)

### ✅ Separate Levels (true product subcategories):

These are distinct product types that shoppers search for specifically:
- **Pencil Eyeliner** → Eyeliner (pencil is a distinct type vs liquid/gel)
- **True Wireless Earbuds** → Wireless Earphones → Earphones (distinct technology)
- **Puffer Jacket** → Jacket (distinct style shoppers specifically search)
- **Transformer** → Action Figure → Toys (distinct product line)

---

## Synonyms: When to Merge with " / "

If two terms mean the **same thing**, put them on the **same level** with " / ":

| Type | Example | Format |
|------|---------|--------|
| Style variants | Puffer Jacket, Puffy Coat | "Puffer Jacket / Puffy Coat" |
| Regional terms | Flashlight, Torch | "Flashlight / Torch" |
| Word order | Pencil Eyeliner, Eyeliner Pencil | "Pencil Eyeliner / Eyeliner Pencil" |
| Generic variations | Men's Clothing, Apparel | "Men's Clothing / Apparel" |

**Test:** If both terms refer to the same product and one is NOT a subset of the other → same level.

---

## What to Exclude (Never in taxonomy)

- ❌ Brand names (JBL, Owala, KitchenAid)
- ❌ Size/quantity (32oz, 2-Pack, 20ml)
- ❌ Colors (Black, White, Denim)
- ❌ Materials as prefixes (Bamboo Tray → just "Serving Tray")
- ❌ Features as prefixes (Insulated Bottle → just "Water Bottle")
- ❌ Vague umbrellas (Gear, Stuff, Items, Products, Accessories)
- ❌ Too-broad categories (Electronics, Home & Kitchen, Appliances)

---

## Examples

### 1-Level Examples (simple, self-explanatory products):

**Water Bottle:**
```
title: "Owala FreeSip Insulated Stainless Steel Water Bottle with Straw"
```
```json
{"taxonomy": [{"level": 1, "product_type": "Water Bottle", "rank": 1}]}
```
*Why 1 level: "Insulated" and "Stainless Steel" are features, not product types.*

**Oven Mitt:**
```
title: "KITCHENAID Ribbed Soft Silicone Oven Mitt 2-Pack Set"
```
```json
{"taxonomy": [{"level": 1, "product_type": "Oven Mitt", "rank": 1}]}
```
*Why 1 level: "Silicone" is material, "Ribbed" is feature.*

**Ice Maker:**
```
title: "Countertop Ice Maker Machine, 26lb/Day"
```
```json
{"taxonomy": [{"level": 1, "product_type": "Ice Maker", "rank": 1}]}
```
*Why 1 level: "Countertop" is placement. "Appliances" fails Q1/Q2.*

**Car Phone Mount:**
```
title: "Jikasho Vacuum Magnetic Suction Phone Holder for Car"
```
```json
{"taxonomy": [{"level": 1, "product_type": "Car Phone Holders & Mounts", "rank": 1}]}
```
*Why 1 level: "Vacuum" and "Magnetic" are features.*

**Serving Tray:**
```
title: "Webacoo Bamboo Tray with Handles - Lightweight Serving Tray"
```
```json
{"taxonomy": [{"level": 1, "product_type": "Serving Tray", "rank": 1}]}
```
*Why 1 level: "Bamboo" is material.*

**Syringe:**
```
title: "ENFit® Syringe - 20ml - QTY 10"
```
```json
{"taxonomy": [{"level": 1, "product_type": "Syringe", "rank": 1}]}
```
*Why 1 level: "ENFit" is a connector standard/feature, not a product type.*

---

### 3-Level Examples (true hierarchies):

**True Wireless Earbuds:**
```
title: "JBL Vibe Beam - True Wireless JBL Deep Bass Sound Earbuds"
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
*Why 3 levels: Each is a distinct category shoppers search for. TWS ⊂ Wireless ⊂ Earphones.*

**Pencil Eyeliner:**
```
title: "Revlon ColorStay Pencil Waterproof Eyeliner"
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
*Why 3 levels: Pencil is a type of Eyeliner (vs liquid/gel). Eyeliner is a type of Eye Makeup.*

**Puffer Jacket (with synonyms):**
```
title: "Pioneer Camp Mens Lightweight Packable Puffer Jacket Winter Insulated Puffy Coat"
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
*Why synonyms: "Puffer Jacket" and "Puffy Coat" are the same product, different names.*

**Transformer:**
```
title: "Transformers Toys Heroic Optimus Prime Action Figure"
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
*Why 3 levels: Transformer is a specific toy line. Action Figure is broader. Toys is broadest searchable.*

**Kitchen Sink Caddy:**
```
title: "Cisily Kitchen Sink Caddy Organizer with High Brush Holder"
```
```json
{
  "taxonomy": [
    {"level": 1, "product_type": "Sink Caddy Organizer", "rank": 1},
    {"level": 2, "product_type": "Kitchen Caddy Organizer", "rank": 2},
    {"level": 3, "product_type": "Kitchen Storage and Organization", "rank": 3}
  ]
}
```
*Why 3 levels: Sink caddy ⊂ Kitchen caddy ⊂ Kitchen storage. All are searchable terms.*

---

## Quick Reference: Common Mistakes

| Input | ❌ Wrong | ✅ Correct |
|-------|----------|-----------|
| Insulated Stainless Steel Water Bottle | Insulated Water Bottle → Water Bottle | Water Bottle (1 level) |
| Silicone Oven Mitt | Silicone Oven Mitt → Oven Mitt | Oven Mitt (1 level) |
| Bamboo Serving Tray | Bamboo Tray → Serving Tray | Serving Tray (1 level) |
| Countertop Ice Maker | Countertop Ice Maker → Ice Maker | Ice Maker (1 level) |
| ENFit Syringe | ENFit Syringe → Syringe | Syringe (1 level) |
| Magnetic Car Phone Mount | Magnetic Mount → Phone Mount | Car Phone Holders & Mounts (1 level) |
| Baby Stroller | Baby Stroller → Stroller | Stroller / Baby Stroller (1 level, merged) |

---

## Summary Checklist

Before finalizing:
- [ ] Level 1 = what shoppers search for (not catalog terms)
- [ ] Each level passes TRUE Hierarchy Test (is X a TYPE OF Y?)
- [ ] Broader levels pass Two-Question Test (Q1 + Q2)
- [ ] No materials, features, sizes, colors in product_type
- [ ] No vague umbrella terms (Gear, Items, Accessories)
- [ ] Synonyms merged with " / " on same level
- [ ] 1 level is perfectly valid (don't force hierarchy)
- [ ] Maximum 3 levels
