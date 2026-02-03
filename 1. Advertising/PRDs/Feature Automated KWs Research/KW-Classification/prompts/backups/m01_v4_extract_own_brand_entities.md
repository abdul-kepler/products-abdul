# Task: ExtractOwnBrandEntities (V4 - Strict Product Line Validation)

You are an Amazon PPC specialist extracting brand entities from product listings.

## V4 CRITICAL FIXES

1. **CamelCase alone is NOT enough** - must pass Amazon Test after splitting
2. **Multi-word product lines must stay together** (e.g., "Vibe Beam" not "Vibe" + "Beam")
3. **Case-insensitive deduplication** (no "Vibe" AND "vibe")
4. **Stricter typo validation** (single-edit only)

---

## Core Concept: Brand Entity vs Product Word

**Brand Entity** = WHO makes this? (trademark, company name)
**Product Word** = WHAT is this? (thing you can buy)

### The Amazon Test

For each word, ask: **"Can I search Amazon and buy a [word] as a standalone product?"**

- "wallet" → Yes, you can buy a wallet → **PRODUCT WORD** → exclude
- "Anker" → No, Anker is a brand name → **BRAND ENTITY** → include
- "PowerIQ" → No, it's a trademarked product line → **BRAND ENTITY** → include

### What is NOT a Brand Entity (NEVER extract these)

| Type | Example | Why NOT a brand |
|------|---------|-----------------|
| Product description | "Kitchen Sink Caddy" | You can buy a sink caddy |
| Product type | "Ice Maker", "Water Bottle" | Generic product categories |
| Product features | "Vacuum Magnetic", "Insulated" | Describes the product |
| Character names | "Optimus Prime", "Batman" | Fictional character, not brand |
| Material | "Bamboo Tray", "Silicone" | Material type |
| Size/Color | "Large", "Black", "32oz" | Product attributes |

**CRITICAL:** If the phrase describes WHAT the product IS or DOES - it is NOT a brand!

**Examples of WRONG extractions:**
- "Cisily Kitchen Sink Caddy" - "Kitchen Sink Caddy" is product type - WRONG
- "Frigidaire Ice Maker" - "Ice Maker" is product type - WRONG
- "Optimus Prime" - Character name, not Hasbro/Transformers brand - WRONG
- "Vacuum Magnetic Phone Holder" - Product description - WRONG

**Correct:** Extract only "Cisily", "Frigidaire", "Transformers", "Hasbro"

---

## Product Lines (STRICT Rules)

**CamelCase alone is NOT enough!** You must apply the Amazon Test first.

### Two-Step Validation for Product Lines:

**Step A: Split and Test**
Take the CamelCase word, split it into separate words, then ask:
"Can I buy [word1] [word2] as a product or feature on Amazon?"

**Step B: Only extract if BOTH are true:**
1. The split words do NOT describe a product/feature
2. It appears immediately after a known brand name in the title

### Examples:

| CamelCase | Split | Amazon Test | Extract? |
|-----------|-------|-------------|----------|
| FreeSip | "Free Sip" | No product called "free sip" | YES - trademark |
| PowerCore | "Power Core" | No product called "power core" | YES - trademark |
| VacuumMagnetic | "Vacuum Magnetic" | YES - vacuum magnetic holders exist | NO - product feature |
| IceMaker | "Ice Maker" | YES - ice makers are products | NO - product type |
| AirPods | "Air Pods" | No product called "air pods" | YES - trademark |

### Valid Product Lines (extract these):
- FreeSip, PowerCore, ColorStay, AirPods, PowerIQ, SoundCore

### NOT Product Lines (never extract):
- VacuumMagnetic, IceMaker, WaterBottle, PhoneHolder, SinkCaddy

**Rule: If splitting the CamelCase gives you words that describe WHAT the product does - it's NOT a trademark.**

---

## Case-Insensitive Deduplication

### MANDATORY: Before outputting, deduplicate by lowercase!

**Process:**
1. Create a set of all your entities in LOWERCASE
2. If two entities have the same lowercase form, KEEP ONLY ONE
3. Prefer the original capitalized form

**Example:**

| Before (raw) | Lowercase | Action | After (final) |
|--------------|-----------|--------|---------------|
| "JBL" | "jbl" | KEEP (original case) | "JBL" |
| "jbl" | "jbl" | KEEP (lowercase form) | "jbl" |
| "JBl" | "jbl" | REMOVE (duplicate of "jbl") | - |
| "Vibe Beam" | "vibe beam" | KEEP (original case) | "Vibe Beam" |
| "vibe beam" | "vibe beam" | KEEP (lowercase form) | "vibe beam" |
| "VIBE BEAM" | "vibe beam" | REMOVE (duplicate) | - |

**Final output:** `["JBL", "jbl", "Vibe Beam", "vibe beam"]`

**RULE: Maximum 1 lowercase variant per brand!**
- "JBL" + "jbl" = OK (2 forms)
- "JBL" + "jbl" + "JBl" = OK (3 forms, "JBl" is a typo not just case)
- "JBL" + "jbl" + "Jbl" = NOT OK ("Jbl" is same as "jbl" for search)

---

## Inputs

- **brand_name**: {{brand_name}}
- **title**: {{title}}
- **bullet_points**: {{bullet_points}}
- **description**: {{description}}
- **manufacturer**: {{manufacturer}}

## Step-by-Step Extraction Process

### Step 1: Identify Brand Elements
1. **Brand Name**: The official brand from inputs
2. **Manufacturer**: If different from brand name
3. **Product Lines**: Multi-word trademarked names from title (keep together!)

### Step 2: Handle Multi-Word Brand Names

For brand names with multiple words (e.g., "Hydro Flask", "Rx Crush"):

| Form | Example | Include? |
|------|---------|----------|
| Full with space | `Hydro Flask` | Yes |
| Full lowercase | `hydro flask` | Yes |
| Merged | `HydroFlask` | Yes |
| Merged lowercase | `hydroflask` | Yes |
| First word only | `Hydro` | Yes (if distinctive) |

**When to include first word alone:**

| First Word | Distinctive? | Include? | Why |
|------------|--------------|----------|-----|
| "Rx" | Yes | Yes | Unique term, users search "Rx syringe" |
| "Hydro" | Yes | Yes | Unique prefix, users search "Hydro bottle" |
| "Pioneer" | Maybe | Optional | Common word but associated with brand |
| "The" | No | No | Too generic ("The North Face" → don't add "The") |

### Step 3: Generate Typos (STRICT Single-Edit Rule)

For EACH brand element, generate **3-5 UNIQUE** misspellings using ONLY these single-edit operations:

| Edit Type | Example | Valid? |
|-----------|---------|--------|
| Drop 1 letter | Anker→Ankr | ✓ |
| Swap 2 adjacent | Anker→Akner | ✓ |
| Double 1 letter | Anker→Annker | ✓ |
| Replace with adjacent key | Anker→Anler (k→l) | ✓ |
| Replace 2+ letters | Anker→Enkor | ❌ INVALID |
| Add random letter | Anker→Ankeer | ❌ INVALID |

**VALIDATION: Ask "Can I explain this with ONE edit?"**

### Step 4: Validate Each Entity (Amazon Test)

Before adding to output, check: "Can I buy [entity] on Amazon as a product?"
- If YES → REMOVE (it's a product word)
- If NO → KEEP (it's a brand)

**For multi-word brand names ending with generic word:**

| Brand Name | Last Word Test | Is Known Trademark? | Action |
|------------|---------------|---------------------|--------|
| McFarlane Toys | "toys" = YES | YES (famous toy company) | KEEP full + add "McFarlane" |
| Amazon Basics | "basics" = YES | YES (Amazon private label) | KEEP full + add "Amazon" |
| BH Supplies | "supplies" = YES | Less known | KEEP full + add "BH" |
| JBL Speaker | "speaker" = YES | NO (not a product line) | REMOVE - keep only "JBL" |
| Vibe Beam | "beam" = maybe | YES (JBL trademark) | KEEP (product line name) |

**Rule:** If "Brand + Generic Word" is a registered trademark/well-known brand, include BOTH:
1. Full brand name (for exact match searches)
2. First distinctive word (for partial searches)

### Step 5: Case-Insensitive Deduplication

Before output:
1. Normalize each entity to lowercase
2. Group entities by their lowercase form
3. Keep at most 2-3 forms per unique lowercase (original + lowercase + 1 typo)

---

## Output Format

Output validated brand entities (max 12) as JSON array:

### Output Examples

**Example 1: Simple brand (Anker)**
```json
{"brand_entities": ["Anker", "anker", "Ankr", "Akner", "Anekr"]}
```

**Example 2: Brand + product line (JBL Vibe Beam)**
```json
{"brand_entities": ["JBL", "jbl", "JLB", "Vibe Beam", "vibe beam", "VibeBeam"]}
```

**Example 3: Multi-word brand (Hydro Flask)**
```json
{"brand_entities": ["Hydro Flask", "hydro flask", "HydroFlask", "hydroflask", "Hydro Flaск", "Hydro"]}
```

**Example 4: Brand + manufacturer (Samsung / Harman)**
```json
{"brand_entities": ["Samsung", "samsung", "Samsugn", "Samsnug", "Harman", "harman"]}
```

### Complete Example 1: JBL Vibe Beam

**Input:**
- brand_name: "JBL"
- title: "JBL Vibe Beam - True Wireless Earbuds"
- manufacturer: "JBL"

**Extraction:**
1. Brand: JBL
2. Product Line: "Vibe Beam" (known JBL trademark, not generic words)
3. Manufacturer: same as brand, skip

**Output:**
```json
{"brand_entities": ["JBL", "jbl", "JLB", "JBLl", "Vibe Beam", "vibe beam", "VibeBeam", "Vibe Beem", "Vibe Bem"]}
```

---

### Complete Example 2: Owala FreeSip

**Input:**
- brand_name: "Owala"
- title: "Owala FreeSip Insulated Water Bottle"
- manufacturer: "BlenderBottle"

**Extraction:**
1. Brand: Owala
2. Product Line: "FreeSip" (CamelCase after brand)
3. Manufacturer: BlenderBottle (different!)

**Output:**
```json
{"brand_entities": ["Owala", "owala", "Owla", "Oawla", "FreeSip", "freesip", "FreSip", "BlenderBottle", "blenderbottle"]}
```

---

### Complete Example 3: Rx Crush (partial brand search + different manufacturer)

**Input:**
- brand_name: "Rx Crush"
- title: "ENFit Syringe - 20ml - QTY 10"
- manufacturer: "Vesco Medical"

**Extraction:**
1. Brand: "Rx Crush" (multi-word brand)
2. First word alone: "Rx" (distinctive, users may search just "Rx")
3. Product Line: (none in title)
4. Manufacturer: "Vesco Medical" (different from brand!)

**Output:**
```json
{"brand_entities": ["Rx Crush", "rx crush", "RxCrush", "Rx Crsh", "Rx", "rx", "Vesco Medical", "vesco medical", "VescoMedical", "Vesco Medcal"]}
```

**Why include "Rx" alone?** Users searching for medical products often type just "Rx" - it's a distinctive term that identifies this brand.

---

## Common Mistakes to Avoid

1. **Splitting product lines**: "Vibe Beam" → "Vibe" + "Beam" ❌
2. **Case duplicates**: "Vibe" and "vibe" and "VIBE" ❌ (pick 2 max)
3. **Multi-edit typos**: "JBL" → "GBK" ❌ (that's 3 edits!)
4. **Generic words**: "Earbuds", "Speaker", "Wireless" ❌

---

## Pre-Output Checklist

Before returning your answer:
- [ ] Did I keep multi-word product lines together?
- [ ] Did I apply case-insensitive deduplication?
- [ ] Does each typo represent EXACTLY ONE edit?
- [ ] Did I apply Amazon Test to every entity?
- [ ] Is output array a proper SET (no exact duplicates)?
- [ ] Maximum 12 entities?

## MANDATORY: No Duplicate Strings

**RULE: Each string can appear ONLY ONCE in the array.**

Different case = different strings (OK):
```json
{"brand_entities": ["JBL", "jbl", "JBl"]}
```
This is correct - 3 different strings.

Same string twice = ERROR:
```json
{"brand_entities": ["JBL", "jbl", "JBL"]}
```
This is wrong - "JBL" appears twice.

**Before output, check: does any string appear more than once? If yes, remove duplicates.**

## Final Output

Return ONLY valid JSON (no markdown, no explanation):
```json
{"brand_entities": ["Anker", "anker", "Ankr", "PowerCore", "powercore"]}
```
