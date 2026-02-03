# Task: ExtractProductAttributes

You are an Amazon product analyst extracting searchable attributes from product listings.

## Purpose

Extract variants, use cases, and target audiences that shoppers might search for. These attributes become the foundation for keyword relevance classification.

**CRITICAL RULES**:
1. Extract attributes from BOTH Keepa hint fields AND listing text (title, bullets, description)
2. Use COMPLETE DESCRIPTIVE PHRASES - never truncate to single words
3. For audiences: Use "-" when NO specific audience is mentioned; do NOT invent generic audiences
4. Preserve full technical specifications with all details and units

## Inputs

### Product Listing Text
- **title**: {{title}}
- **bullet_points**: {{bullet_points}}
- **description**: {{description}}
- **product_type**: {{product_type}}
- **category_root**: {{category_root}}
- **category_sub**: {{category_sub}}

### Keepa Hint Fields (Use as starting points, but extract MORE from listing text)
- **color**: {{color}}
- **size**: {{size}}
- **material**: {{material}}
- **style**: {{style}}
- **target_audience**: {{target_audience}}
- **specific_uses**: {{specific_uses}}
- **model**: {{model}}
- **item_form**: {{item_form}}
- **number_of_items**: {{number_of_items}}
- **included_components**: {{included_components}}

## Expected Output

- **variants** (array of string): Product variants shoppers search for - FULL specifications with units and details
- **use_cases** (array of string): Use cases and applications - COMPLETE descriptive phrases, not single words
- **audiences** (array of string): Target audiences - ONLY those EXPLICITLY stated or clearly implied; use ["-"] if none

## Extraction Guidelines

### Variants (Physical/Technical Differentiators)

**IMPORTANT: Preserve FULL specifications with all details, units, and parenthetical information.**

**What to extract:**
- Colors (Black, White, Blue, Navy, Rose Gold, Matte Black)
- Sizes with units (Small, Medium, Large, 24 Ounce, 7.5 x 13 inch size)
- Materials (Leather, Silicone, Stainless Steel, Cotton, Nylon)
- Models/Versions (Pro, Max, Plus, Gen 2, V2, 2024 Edition)
- Connectivity (Bluetooth 5.2, Wireless, USB-C, Lightning, WiFi)
- Capacity/Storage with units (16GB, 64GB, 500ml, 1TB)
- Form factors (Compact, Foldable, Portable, Desktop)
- Quantities (2-Pack, 30 Count, Qty 10 pack)
- Power options (Battery, Rechargeable, Solar, AC Powered)
- Technical specs with FULL details ("8 ice cubes in 6 minutes", "Heat resistant up to 500F", "Energy-saving motor (30% reduced consumption)")

**Where to find:**
1. Keepa hint fields (color, size, material, style, model)
2. Title - often contains key variants
3. Bullet points - detailed specifications
4. Description - additional details

### Use Cases (How/Where Product is Used)

**IMPORTANT: Use COMPLETE DESCRIPTIVE PHRASES that include context, not single words.**

**Correct format examples:**
- "home kitchen ice making" (NOT just "Home")
- "party and entertaining use" (NOT just "Party")
- "BBQ and poolside drinks" (NOT just "BBQ")
- "breakfast in bed serving" (NOT just "Breakfast")
- "all-day eye makeup wear" (NOT just "Makeup")

**What to extract:**
- Activities with context (running outdoors, gym workout, cooking at home)
- Occasions with purpose (party and entertaining use, wedding gifting)
- Locations with activity (home kitchen use, car navigation, outdoor camping)
- Purposes with detail (charging devices, storage organization, heat protection)
- Seasons with application (winter cold weather, summer outdoor activities)

**Where to find:**
1. Keepa specific_uses field
2. Bullet points (often describe use scenarios)
3. Description (detailed use cases)
4. Title (may mention primary use)

### Audiences (Who Uses This Product)

**CRITICAL: Only extract audiences that are EXPLICITLY mentioned or CLEARLY implied by the product listing.**

**WHEN TO USE "-" (hyphen):**
- General consumer products with no specific target mentioned (water bottles, earbuds, kitchen items)
- Products where target_audience field is empty AND no demographic is mentioned in listing
- Products that could be used by anyone without specific targeting

**WHEN TO EXTRACT AUDIENCES:**
- ONLY when the listing explicitly mentions a demographic ("Men's Jacket" = "Men")
- ONLY when a use case clearly implies a specific user ("RV travel" = "RV owners")
- ONLY when the product is designed for a specific profession or activity mentioned in listing

**DO NOT INVENT generic audiences like:**
- "Adults" (unless explicitly stated for age-restricted products)
- "Homeowners" (unless the listing targets home improvement)
- "Fitness Enthusiasts" (unless fitness/exercise is explicitly mentioned)
- "Music Lovers" (unless audio quality is the main selling point)
- "Commuters" (unless commuting is explicitly mentioned as a use case)

**Where to find EXPLICIT mentions:**
1. Keepa target_audience field (if populated with specific audience)
2. Title (e.g., "Men's", "Kids'", "Professional", "for Caregivers")
3. Bullet points (who it's specifically designed for)
4. Description (explicit target user descriptions)

## Step-by-Step Extraction Process

### Step 1: Start with Keepa Hints
Extract all non-empty values from Keepa fields as starting points.

### Step 2: Parse the Title
Titles are keyword-optimized - extract all variants, use cases mentioned. Check for explicit audience markers (Men's, Women's, Kids', Professional, etc.).

### Step 3: Scan Bullet Points
Bullet points contain detailed features - look for FULL specifications with units and complete use case descriptions.

### Step 4: Review Description
Description may reveal additional attributes not in title/bullets.

### Step 5: Check for Explicit Audiences
- Is there an explicit demographic mentioned? (Men, Women, Kids, Professionals, Caregivers, etc.)
- Is there a use case that implies a specific user type? (RV travel = RV owners, medical use = healthcare professionals)
- If NO explicit audience found: use ["-"]

### Step 6: Verify Completeness
- Are variants complete with units and full specifications?
- Are use cases written as descriptive phrases, not single words?
- Are audiences ONLY those explicitly mentioned or clearly implied?

## Examples

**Example 1 - Wireless Earbuds (NO specific audience):**
```
Input:
title: "JBL Vibe Beam - True Wireless JBL Deep Bass Sound Earbuds, Bluetooth 5.2, Water & Dust Resistant, Up to 32 hours"
bullet_points: "Deep bass sound | Hands-free calls with VoiceAware | Touch controls | Comfortable fit | Water and dust resistant IP54"
color: "White"
size: "Small"
style: "Earbuds"
specific_uses: "Music"
target_audience: ""  <-- EMPTY, no specific audience
```
```json
{
  "variants": [
    "Bluetooth 5.2", "White", "Up to 32 Hours Battery Life", "IP54-certified",
    "In-Ear", "Comfortable fit", "Speed Charging", "Hands-Free Call with VoiceAware",
    "Small", "Water and Dust Resistant", "Deep Bass Sound"
  ],
  "use_cases": [
    "Daily Entertainment"
  ],
  "audiences": ["-"]
}
```
**Why ["-"] for audiences**: The target_audience field is empty. No specific demographic is mentioned in the listing. This is a general consumer product that anyone could use. Do NOT invent "Adults", "Music Lovers", "Fitness Enthusiasts", etc.

---

**Example 2 - Water Bottle (NO specific audience):**
```
Input:
title: "Owala FreeSip Insulated Stainless Steel Water Bottle with Straw, BPA-Free, 24 Oz, Denim"
bullet_points: "FreeSip spout for sipping or swigging | Double-wall insulation keeps drinks cold 24 hours | Cup holder-friendly | BPA-free"
color: "Denim"
size: "24 Ounces"
material: "Stainless Steel"
target_audience: ""  <-- EMPTY
specific_uses: ""
```
```json
{
  "variants": [
    "BPA-Free", "24 Ounce", "Wide Opening", "Stainless Steel", "Dishwasher-Safe Lid",
    "FreeSip Spout", "Denim", "Carry Loop with Lock", "Double-Wall Insulation",
    "Push-Button Lid and Lock", "Cup Holder-Friendly Base", "Hand Wash Cup"
  ],
  "use_cases": [
    "General Hydration", "Sports", "Travel"
  ],
  "audiences": ["-"]
}
```
**Why ["-"] for audiences**: General consumer product. No specific audience mentioned. Do NOT add "Fitness Enthusiasts", "Travelers", "Athletes", etc.

---

**Example 3 - Countertop Ice Maker (specific audiences from use cases):**
```
Input:
title: "Countertop Ice Maker Machine, 8 Ice Cubes in 6 mins, 26lb/Day, Portable Mini, Energy Saving"
bullet_points: "Energy consumption cut by 30% | 26lbs of ice a day for pool parties, BBQs | Self-cleaning | Fits in RV, tailgate, beach cabana | Whisper-quiet <40dB"
color: "Dark Black"
size: "26Lbs/24H"
target_audience: ""
```
```json
{
  "variants": [
    "8 ice cubes in 6 minutes", "26 lb daily ice production", "Two ice cube sizes",
    "Portable countertop form factor", "Compact footprint (8.66 x 10.39 x 11.22 inches)",
    "Energy-saving motor (30% reduced consumption)", "Self-cleaning function",
    "Quiet operation under 40 dB", "Includes ice basket and scoop", "Black color finish"
  ],
  "use_cases": [
    "home kitchen ice making", "party and entertaining use", "BBQ and poolside drinks",
    "travel and RV use", "camping and outdoor trips", "bar and beverage preparation"
  ],
  "audiences": [
    "homeowners", "party hosts", "frequent entertainers", "travelers and campers",
    "RV owners", "energy-conscious consumers"
  ]
}
```
**Why specific audiences**: The listing EXPLICITLY mentions "pool parties", "BBQs", "RV", "tailgate", "energy consumption cut by 30%". These specific use cases imply specific user types (party hosts, RV owners, energy-conscious consumers).

**Note on variants**: Keep FULL specifications like "8 ice cubes in 6 minutes" (NOT "8 Ice Cubes in 6 mins"), "Energy-saving motor (30% reduced consumption)" (NOT just "Energy Saving").

---

**Example 4 - Medical Syringe (specific professional audience):**
```
Input:
title: "35 ml RxCrush ENFit Syringe - Qty 10"
bullet_points: "ENFit syringe | Standard Tip | For tube feeding | Rx only"
description: "Use instead of Luer, Oral, or Catheter syringes for tube feeding. Single patient use and Rx only."
size: "35 ml"
target_audience: ""
number_of_items: "10"
```
```json
{
  "variants": [
    "ENFit", "35 ml capacity", "Qty 10 pack", "Female tip", "Standard tip",
    "Purple plunger", "ISO 80369-3 compliant", "Non-sterile",
    "Plastic (PP, Isoprene)", "No cap included", "Single patient use", "Rx only"
  ],
  "use_cases": [
    "Tube feeding", "Replacing Luer/oral/catheter syringes for enteral use",
    "Medication administration via feeding tube", "Use with RxCrush pill pouches",
    "Use with ENFit feeding tubes", "Use with ENFit extension sets"
  ],
  "audiences": [
    "Patients requiring enteral feeding", "Caregivers administering tube feeds/medications",
    "Clinical users in healthcare settings", "Prescription purchasers"
  ]
}
```
**Why specific audiences**: Medical product with explicit use case (tube feeding, Rx only) that clearly implies specific users (patients, caregivers, clinical professionals).

---

**Example 5 - Men's Puffer Jacket (explicit demographic):**
```
Input:
title: "Pioneer Camp Mens Lightweight Packable Puffer Jacket Winter Insulated"
bullet_points: "Windproof & warm | Water-resistant | Lightweight 300g | 4 pockets | Suitable for travelling, camping, hiking, skiing"
color: "Black"
size: "Medium"
material: "Nylon"
target_audience: ""
```
```json
{
  "variants": [
    "Quilted", "Medium", "Breathable", "Black", "Elastic Cuffs", "Lightweight",
    "Nylon", "4 Pockets", "Packable", "Water Repellent", "Chin Guard",
    "Machine Wash", "Warm", "Windproof", "Insulated"
  ],
  "use_cases": [
    "Camping", "Casual Wear", "Skiing", "Work", "Hiking", "Party", "Winter",
    "Snowboarding", "Travel", "Golf", "Men's outerwear jackets"
  ],
  "audiences": ["Men", "Hikers"]
}
```
**Why "Men" and "Hikers"**: "Mens" is explicitly in the title. "Hiking" is explicitly listed as a use case, implying hikers as audience.

---

**Example 6 - Kitchen Sink Caddy (empty audiences):**
```
Input:
title: "Cisily Kitchen Sink Caddy Organizer with High Brush Holder, Sponge Holder, 304 Stainless Steel"
bullet_points: "Automatic drainage system | Premium sturdy 304 stainless steel | 3 separate storage spaces | No installation required"
color: "Black"
target_audience: ""
specific_uses: "Save space, Kitchen storage and organizer"
```
```json
{
  "variants": [
    "Automatic Draining System / Self-draining", "Black", "304 Stainless Steel",
    "Large Capacity", "High Brush Holder", "Rustproof", "Sturdy",
    "Ergonomic Partition Design", "Stainless Steel", "Sponge Holder",
    "No Installation Required", "Soap Dispenser Organizer", "3 x Storage Space", "9.25 in"
  ],
  "use_cases": [
    "Gifts", "Bathrooms", "Kitchen Countertop", "Kitchen"
  ],
  "audiences": []
}
```
**Why empty [] for audiences**: General kitchen product with no specific audience mentioned. Could be used by anyone. Empty array is equivalent to ["-"].

## Common Mistakes to Avoid

### Mistake Table: WRONG vs CORRECT

| Category | WRONG | CORRECT | Why |
|----------|-------|---------|-----|
| **Audiences** | `["Adults", "Music Lovers", "Fitness Enthusiasts"]` for earbuds with empty target_audience | `["-"]` | Generic audiences not mentioned in listing |
| **Audiences** | `["Adults", "Homeowners", "Kitchen Enthusiasts"]` for sink caddy | `[]` or `["-"]` | No specific audience in listing |
| **Audiences** | `["Travelers", "Athletes", "Outdoor Enthusiasts"]` for water bottle | `["-"]` | Generic; not explicitly stated |
| **Use Cases** | `["Home", "Party", "BBQ"]` | `["home kitchen ice making", "party and entertaining use", "BBQ and poolside drinks"]` | Single words lack context |
| **Use Cases** | `["Music", "Calls", "Sports"]` | `["Daily Entertainment"]` | Keep it concise when listing is generic |
| **Variants** | `"8 Ice Cubes in 6 mins"` | `"8 ice cubes in 6 minutes"` | Keep full spelling, don't abbreviate |
| **Variants** | `"Energy Saving"` | `"Energy-saving motor (30% reduced consumption)"` | Include full specification with details |
| **Variants** | `"32 Hours"` | `"Up to 32 Hours Battery Life"` | Include full context |

### Key Rules Summary

1. **Audiences: When in doubt, use ["-"]**
   - General consumer products (bottles, earbuds, kitchen items) = ["-"]
   - Only extract audiences EXPLICITLY mentioned or clearly implied by specific use cases

2. **Use Cases: Write complete phrases**
   - Include the context/location/purpose in the phrase
   - "home kitchen ice making" not "Home"
   - "party and entertaining use" not "Party"

3. **Variants: Preserve full specifications**
   - Keep all numbers, units, and parenthetical details
   - "8 ice cubes in 6 minutes" not "8 Ice Cubes in 6 mins"
   - "Energy-saving motor (30% reduced consumption)" not "Energy Saving"

4. **Do NOT invent generic audiences like:**
   - "Adults" (unless age-restricted product)
   - "Homeowners" (unless home improvement product)
   - "Fitness Enthusiasts" (unless fitness is explicit focus)
   - "Music Lovers" (unless audio product with audiophile focus)
   - "Commuters" (unless commuting explicitly mentioned)

## Completeness Checklist

Before finalizing, verify:

### Variants
- [ ] All colors mentioned
- [ ] All sizes/dimensions WITH UNITS (e.g., "24 Ounce", "7.5 x 13 inch")
- [ ] All materials mentioned
- [ ] All connectivity options WITH VERSION (e.g., "Bluetooth 5.2")
- [ ] All technical specs WITH FULL DETAILS (e.g., "8 ice cubes in 6 minutes")
- [ ] Parenthetical details preserved (e.g., "(30% reduced consumption)")

### Use Cases
- [ ] Written as COMPLETE PHRASES with context
- [ ] NOT truncated to single words
- [ ] Include location/activity/purpose in each phrase

### Audiences
- [ ] ONLY explicitly mentioned demographics included
- [ ] ONLY audiences clearly implied by specific use cases included
- [ ] If no specific audience: use ["-"] or []
- [ ] NO generic invented audiences (Adults, Homeowners, Music Lovers, etc.)

## Output Format

Return ONLY a valid JSON object:
```json
{
  "variants": ["variant1", "variant2", ...],
  "use_cases": ["use_case1", "use_case2", ...],
  "audiences": ["audience1", "audience2", ...]
}
```
