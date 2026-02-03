# Task: GenerateCompetitorBrandEntities

You are an Amazon marketplace expert identifying competitor brands for PPC keyword targeting.

## Purpose

Generate a comprehensive list of competitor brand entities that shoppers might search for when looking for products similar to this listing. These are brands selling substitute/competing products in the same category.

**IMPORTANT**: This is a generative task. You must use your knowledge of the Amazon marketplace and product categories to identify realistic competitors - there is no competitor list provided as input.

## Inputs

- **title**: {{title}}
- **bullet_points**: {{bullet_points}}
- **description**: {{description}}
- **brand_name**: {{brand_name}}
- **product_type**: {{product_type}}
- **category_root**: {{category_root}}
- **category_sub**: {{category_sub}}

## Expected Output

- **competitor_entities** (array of string): Flat list of competitor brands, sub-brands, product lines, and common misspellings.

## Step-by-Step Generation Process

### Step 1: Identify the Product Category and Market Segment

Analyze the inputs to understand:
- What specific product is this? (e.g., wireless earbuds, phone mount, puffer jacket)
- What price tier does it appear to be? (budget, mid-range, premium)
- What is the primary use case? (consumer, professional, specialized)

### Step 2: Recall Major Competitors in This Category

Think through:
- **Market leaders**: Who are the top 3-5 brands in this category on Amazon?
- **Direct competitors**: Brands at similar price points with similar products
- **Adjacent competitors**: Brands that compete in overlapping categories

### Step 3: Generate Brand Variations for Each Competitor

For each competitor brand identified:
1. **Primary brand name**: Official spelling
2. **Sub-brands/product lines**: If well-known (e.g., Apple -> AirPods)
3. **Common misspellings**: 2-3 realistic typos per major brand

### Step 4: Prioritize by Relevance

Order competitors by:
1. Direct category competitors (same product type)
2. Major brands shoppers commonly compare
3. Emerging/popular brands in the category

## Category-Specific Competitor Examples

### Electronics - Wireless Earbuds/Headphones
**If product is:** True wireless earbuds
**Likely competitors:** Apple (AirPods), Sony, Bose, Samsung (Galaxy Buds), Jabra, Beats, Anker (Soundcore), Skullcandy, JLab, Tozo, etc.

### Electronics - Phone Accessories (Mounts, Cases, Chargers)
**If product is:** Car phone mount
**Likely competitors:** iOttie, LISEN, Scosche, Miracase, VANMASS, VICSEED, TORRAS, Belkin, Spigen, etc.

### Apparel - Jackets/Outerwear
**If product is:** Puffer jacket
**Likely competitors:** The North Face, Patagonia, Columbia, Canada Goose, Marmot, Arc'teryx, Uniqlo, Amazon Essentials, etc.

### Home & Kitchen - Small Appliances
**If product is:** Coffee maker
**Likely competitors:** Keurig, Nespresso, Cuisinart, Mr. Coffee, Breville, Hamilton Beach, Ninja, De'Longhi, etc.

### Health & Personal Care - Supplements/Medical
**If product is:** Medical syringe
**Likely competitors:** BD (Becton Dickinson), Medline, McKesson, Monoject, Terumo, etc.

## Decision Rules

**INCLUDE:**
- Top brands in the exact product category
- Brands commonly appearing in "Customers also viewed" for this product type
- Both premium and budget competitor brands
- Well-known sub-brands (AirPods, Galaxy Buds, Soundcore)
- 2-3 common misspellings per major brand
- Brands that shoppers might compare when making purchase decisions

**EXCLUDE:**
- The seller's own brand (brand_name from input)
- Brands from completely different categories
- Obscure brands with no Amazon presence
- Generic/store brands unless category-relevant (like Amazon Basics)
- Retailers (Amazon, Walmart) unless they have private labels in this category

**QUANTITY GUIDELINES:**
- Aim for 15-30 competitor entities total
- Include 5-10 distinct competitor brands
- Add 2-3 misspellings for top 3-4 brands
- Include major sub-brands/product lines

## Examples

**Example 1 - Wireless Earbuds:**
```
Input:
title: "JBL Vibe Beam - True Wireless JBL Deep Bass Sound Earbuds"
brand_name: "JBL"
product_type: "HEADPHONES"
category_root: "Electronics"
category_sub: "Headphones, Earbuds & Accessories"
```
Think: This is a true wireless earbud product. Major competitors include Apple (AirPods), Sony, Bose, Samsung, Beats, Anker/Soundcore, and budget brands like Tozo and JLab.
```json
{
  "competitor_entities": [
    "Apple", "AirPods", "AirPod", "Airpods Pro", "Aple", "Appel",
    "Sony", "Sony WF", "Sonny", "Soney",
    "Bose", "Bose QuietComfort", "Boze", "Bosse",
    "Samsung", "Galaxy Buds", "Samung", "Samsng",
    "Beats", "Beats Studio Buds", "Beats Fit Pro", "Beets",
    "Anker", "Soundcore", "Ankor", "Ankr",
    "Jabra", "Jabra Elite", "Jabera",
    "Skullcandy", "Skull Candy",
    "Tozo", "JLab"
  ]
}
```

**Example 2 - Car Phone Mount:**
```
Input:
title: "Jikasho Vacuum Magnetic Phone Holder for Car Dashboard"
brand_name: "Jikasho"
product_type: "PORTABLE_ELECTRONIC_DEVICE_MOUNT"
category_root: "Cell Phones & Accessories"
category_sub: "Car Accessories"
```
Think: This is a car phone mount. Major competitors in this space include iOttie, LISEN, Scosche, and other car accessory brands.
```json
{
  "competitor_entities": [
    "iOttie", "iottie", "i Ottie", "IOttie",
    "LISEN", "Lisen", "Liesen",
    "Scosche", "Scoche", "Skosche",
    "Miracase", "Mira case",
    "VANMASS", "Vanmass",
    "VICSEED", "Vicseed",
    "TORRAS", "Torras",
    "Belkin", "Belkn",
    "Spigen", "Spigen car mount",
    "TOPK", "Mpow", "Anker"
  ]
}
```

**Example 3 - Medical Product:**
```
Input:
title: "60ml ENFit Syringe for Enteral Feeding - 30 Pack"
brand_name: "MedCare"
product_type: "SYRINGE"
category_root: "Health & Household"
category_sub: "Medical Supplies & Equipment"
```
Think: This is a medical syringe for enteral feeding. Competitors include major medical supply brands.
```json
{
  "competitor_entities": [
    "BD", "Becton Dickinson", "B-D",
    "Medline", "Med line", "Medlin",
    "McKesson", "Mckesson", "Mc Kesson",
    "Monoject", "Mono ject",
    "Terumo", "Teramo",
    "NeoMed", "Neo Med",
    "Vesco", "Vesco Medical",
    "Cardinal Health", "Cardinal"
  ]
}
```

**Example 4 - Apparel:**
```
Input:
title: "Men's Lightweight Puffer Jacket - Black, Size Large"
brand_name: "WarmCore"
product_type: "OUTERWEAR"
category_root: "Clothing, Shoes & Jewelry"
category_sub: "Men's Outerwear"
```
Think: This is a men's puffer jacket. Competitors range from premium outdoor brands to budget options.
```json
{
  "competitor_entities": [
    "The North Face", "North Face", "Northface", "TNF",
    "Patagonia", "Patagucci", "Patagona",
    "Columbia", "Columbia Sportswear", "Columba",
    "Amazon Essentials", "Amazon Basics",
    "Uniqlo", "Uniqulo",
    "Marmot", "Marmott",
    "Arc'teryx", "Arcteryx", "Arc teryx",
    "Eddie Bauer", "Eddoe Bauer",
    "Calvin Klein", "CK",
    "Tommy Hilfiger", "Tommy"
  ]
}
```

## Output Format

Return ONLY a valid JSON object:
```json
{
  "competitor_entities": ["entity1", "entity2", "entity3", ...]
}
```
