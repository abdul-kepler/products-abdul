# Task: ExtractBrandRelatedTerms

Extract brand-related entities from Amazon product listings.

## Input

- **brand_name**: {{brand_name}}
- **title**: {{title}}
- **bullet_points**: {{bullet_points}}
- **description**: {{description}}
- **manufacturer**: {{manufacturer}}

## Output Format

```json
{
  "sub_brands": [],
  "searchable_standards": [],
  "manufacturer": null
}
```

---

## FIELD 1: sub_brands

Named sub-brands, product families, series, **or brand-owned technologies** within the parent brand.

### INCLUDE in sub_brands:
- Trademarked sub-brand names: `FreeSip`, `ColorStay`, `Vibe Beam`
- Named product series: `Cyber Commander Series`
- **Brand-owned technologies** that customers search WITH the brand:
  - `OMNI-HEAT` (Columbia's technology) → people search "Columbia OMNI-HEAT"
  - `IceFlow` (Stanley's product line) → people search "Stanley IceFlow"
  - `QuietComfort` (Bose's product line) → people search "Bose QuietComfort"
  - `TrueFX` (Mattel's technology) → collectors search "Mattel TrueFX"

### EXCLUDE from sub_brands:
- **Generic product types**: Pill Pouch, Pill Crusher, Water Bottle, Oven Mitt
- **Feature descriptions**: Deep Bass Sound, Waterproof, Lightweight
- **Size/color variants**: Large, Black, 24oz
- **Marketing fluff nobody searches**: "Adapti-Flex Color Lock Technology™"

### Test: Would someone search Amazon for "[sub_brand] [brand]"?
- ✓ "FreeSip Owala" — YES, it's a sub-brand
- ✓ "ColorStay Revlon" — YES
- ✓ "OMNI-HEAT Columbia" — YES, brand technology
- ✗ "Pill Pouch Rx Crush" — NO, that's a product type
- ✗ "Deep Bass Sound JBL" — NO, marketing phrase

---

## FIELD 2: searchable_standards

**UNIVERSAL industry standards that work ACROSS BRANDS - not brand-specific technologies.**

### THE KEY DISTINCTION:
- **Universal standard** = Works across brands → goes in `searchable_standards`
- **Brand technology** = Only this brand uses it → goes in `sub_brands` (if searchable)

### THE KEY QUESTION: Would shoppers search "[this term] [product type]" WITHOUT a brand name?

### INCLUDE in searchable_standards (VERY RARE - most products have NONE):
- **Licensed material standards**: `Gore-Tex` → people search "Gore-Tex jacket"
- **Licensed audio/video tech**: `Dolby Atmos` → people search "Dolby Atmos soundbar"

**That's basically it.** Most products should return `[]` for this field.

### NOT searchable_standards (common mistakes):
- **ISO/industry standards** that became universal: `ENFit` (ISO 80369-3), `USB-C`, `Bluetooth` — these are like "USB 2.0", everyone has them, they don't differentiate

### EXCLUDE from searchable_standards:

- **Generic technology standards** (not brand-differentiating):
  - `USB-C`, `USB-A`, `Lightning` — generic connectors
  - `Bluetooth`, `Bluetooth 5.3`, `WiFi`, `NFC` — everyone has these
  - `MagSafe` — now too generic for phone accessories

- **Brand-specific technologies** (→ put in sub_brands instead):
  - `OMNI-HEAT` — Columbia trademark → sub_brands
  - `TrueFX` — Mattel trademark → sub_brands
  - `QuietComfort` — Bose trademark → sub_brands
  - `Cocoon® Cloud®` — brand trademark → sub_brands
  - `VoiceAware` — JBL trademark → sub_brands

- **Eco-certifications** (nobody searches these on Amazon):
  - `STANDARD 100 by OEKO-TEX`, `GOTS certified`, `USDA organic`, `Energy Star`

- **Marketing phrases**:
  - `Adapti-Flex Color Lock Technology™` — nobody searches this
  - `Military-Grade` — vague marketing term

- **Technical specs**:
  - `DWR technology`, `IPX4`, `CP65`, `RoHS`, `REACH` — too technical

### Decision Framework:
| Question | YES → | NO → |
|----------|-------|------|
| Is this used by MULTIPLE brands? | Continue | → sub_brands (if brand-specific) |
| Would shoppers search WITHOUT brand name? | INCLUDE | EXCLUDE |

### Examples:
| Term | Category | Result |
|------|----------|--------|
| `Gore-Tex` | Licensed material, people search it | ✓ searchable_standards |
| `Dolby Atmos` | Licensed audio tech, people search it | ✓ searchable_standards |
| `ENFit` | ISO standard, universal in category | ✗ EXCLUDE |
| `USB-C`, `Bluetooth` | Generic tech, everyone has it | ✗ EXCLUDE |
| `MagSafe` | Too generic now | ✗ EXCLUDE |
| `OMNI-HEAT` | Columbia trademark | → sub_brands |
| `TrueFX` | Mattel trademark | → sub_brands |
| `Cocoon® Cloud®` | Brand trademark | → sub_brands |
| `Air Jordan` | Nike trademark | → sub_brands |
| `OEKO-TEX` | Eco-cert, nobody searches | ✗ EXCLUDE |
| `Military-Grade` | Marketing fluff | ✗ EXCLUDE |

### When in doubt, return `[]`
Most products have NO universal searchable standards. Empty array is the correct default.

---

## FIELD 3: manufacturer

Company that manufactures the product, **IF different from brand**.

### RULE: manufacturer = brand → return `null`

Compare input `manufacturer` to `brand_name` (case-insensitive):
- `brand_name: "JBL"`, `manufacturer: "JBL"` → `null`
- `brand_name: "Cisily"`, `manufacturer: "Cisily"` → `null`
- `brand_name: "Antarctic Star"`, `manufacturer: "Antarctic Star"` → `null`
- `brand_name: "Jikasho"`, `manufacturer: "Jikasho"` → `null`
- `brand_name: "REVLON"`, `manufacturer: "Revlon"` → `null` (case-insensitive)
- `brand_name: "Truly Indian"`, `manufacturer: "Truly Indian Foods LLC"` → `null` (contains brand)

### RULE: Different manufacturer → return object

```json
{
  "name": "Full Manufacturer Name",
  "short": "Short Name",
  "searchable": true/false
}
```

### searchable = true:
Known company that consumers might search for:
- `Hasbro` — major toy company
- `BlenderBottle` — known bottle brand

### searchable = false:
OEM/unknown manufacturer that nobody searches for:
- `Town & Country Living`
- `Resolve Designs`

---

## Examples

### Example 1: JBL Earbuds
```
brand_name: "JBL"
manufacturer: "JBL"
title: "JBL Vibe Beam - True Wireless JBL Deep Bass Sound Earbuds"
bullet_points: "...VoiceAware lets you balance how much of your own voice you hear..."
```

**Analysis:**
- `Vibe Beam` = sub-brand (named product family)
- `VoiceAware` = NOT searchable (brand-specific, nobody searches "VoiceAware earbuds")
- `Deep Bass Sound` = NOT searchable (marketing phrase)
- manufacturer = brand → null

```json
{
  "sub_brands": ["Vibe Beam"],
  "searchable_standards": [],
  "manufacturer": null
}
```

### Example 2: Owala Bottle
```
brand_name: "Owala"
manufacturer: "BlenderBottle"
title: "Owala FreeSip Insulated Stainless Steel Water Bottle"
bullet_points: "Patented FreeSip spout..."
```

**Analysis:**
- `FreeSip` = sub-brand (patented, named product line)
- No searchable standards
- BlenderBottle ≠ Owala, known company → searchable: true

```json
{
  "sub_brands": ["FreeSip"],
  "searchable_standards": [],
  "manufacturer": {
    "name": "BlenderBottle",
    "short": "BlenderBottle",
    "searchable": true
  }
}
```

### Example 3: Revlon Eyeliner
```
brand_name: "REVLON"
manufacturer: "Revlon"
title: "Revlon ColorStay Pencil Waterproof Eyeliner"
description: "Formulated with ColorStay Adapti-Flex Color Lock Technology™"
```

**Analysis:**
- `ColorStay` = sub-brand (Revlon product line)
- `Adapti-Flex Color Lock Technology™` = NOT searchable (nobody searches this)
- manufacturer = brand (case-insensitive) → null

```json
{
  "sub_brands": ["ColorStay"],
  "searchable_standards": [],
  "manufacturer": null
}
```

### Example 4: KitchenAid Mitt (OEM)
```
brand_name: "KitchenAid"
manufacturer: "Town & Country Living"
title: "KITCHENAID Ribbed Soft Silicone Oven Mitt"
```

**Analysis:**
- No named sub-brand
- No searchable standards
- Town & Country Living = OEM, nobody searches this

```json
{
  "sub_brands": [],
  "searchable_standards": [],
  "manufacturer": {
    "name": "Town & Country Living",
    "short": "Town & Country",
    "searchable": false
  }
}
```

### Example 5: Transformers Toy
```
brand_name: "Transformers"
manufacturer: "Hasbro"
title: "Transformers Toys Heroic Optimus Prime Action Figure"
bullet_points: "...Cyber Commander Series figure..."
```

**Analysis:**
- `Cyber Commander Series` = sub-brand (named series)
- No searchable standards
- Hasbro = major toy company, very searchable

```json
{
  "sub_brands": ["Cyber Commander Series"],
  "searchable_standards": [],
  "manufacturer": {
    "name": "Hasbro",
    "short": "Hasbro",
    "searchable": true
  }
}
```

### Example 6: Pioneer Camp Jacket
```
brand_name: "Pioneer Camp"
manufacturer: null
title: "Pioneer Camp Mens Lightweight Packable Puffer Jacket"
bullet_points: "...DWR technology with a waterproof rating..."
```

**Analysis:**
- No named sub-brand
- `DWR technology` = NOT searchable (consumers search "waterproof jacket", not "DWR jacket")
- No manufacturer provided

```json
{
  "sub_brands": [],
  "searchable_standards": [],
  "manufacturer": null
}
```

### Example 7: Medical Syringe with ENFit
```
brand_name: "Rx Crush"
manufacturer: "Vesco Medical"
title: "ENFit® Syringe - 20ml - QTY 10"
bullet_points: "ENFit\nStandard ENFit Tip..."
```

**Analysis:**
- No named sub-brand
- `ENFit` = ISO 80369-3 universal standard, NOT searchable (like USB-C, it's now universal for enteral syringes)
- Vesco Medical ≠ Rx Crush, OEM → searchable: false

```json
{
  "sub_brands": [],
  "searchable_standards": [],
  "manufacturer": {
    "name": "Vesco Medical",
    "short": "Vesco",
    "searchable": false
  }
}
```

---

## PRE-OUTPUT VALIDATION CHECKLIST

Before outputting, verify:

□ **manufacturer**: Did you check if manufacturer = brand_name (case-insensitive)?
  - If they match or one contains the other → MUST return `null`

□ **searchable_standards**: For each item, ask: "Would a shopper type this in Amazon search?"
  - If NO or UNLIKELY → remove it
  - When in doubt → return `[]`

□ **sub_brands**: Only named product lines, NOT generic product types or features
