# Module 11 (V1.1): Identify Hard Constraints

## Purpose

Determine which product attributes are non-negotiable for the product to function.

## The Hard Constraint Test

For each attribute, apply this three-step test:

### Step 1: The "Complete Removal" Test

> **"If this attribute were COMPLETELY ABSENT (not different value, but GONE), would the product be PHYSICALLY UNABLE to perform its core function?"**

Examples:
- Oven Mitt without ANY heat resistance → Burns hands → YES, fails test → HARD CONSTRAINT
- Earbuds without ANY Bluetooth → No wireless audio → But wired audio still works → NOT about version
- Earbuds without Bluetooth 5.2 (but has 4.0) → Still transmits audio → NO, not hard constraint

### Step 2: The "Mechanism vs Quality" Filter

> **"Is this attribute THE MECHANISM that enables the function, or a QUALITY MODIFIER of the mechanism?"**

| Type | Example | Hard Constraint? |
|------|---------|------------------|
| MECHANISM | Heat resistance enables protection | Could be YES |
| QUALITY | 500F rating (how much protection) | NO |
| MECHANISM | Speaker drivers enable audio | Could be YES |
| QUALITY | Deep Bass (frequency emphasis) | NO |
| QUALITY | Bluetooth 5.2 (version level) | NO |

### Step 3: The "Validated Use" Alignment

> **"Does the Validated Use REQUIRE this specific attribute, or just require the product category to exist?"**

| Validated Use | Attribute | Required? | Reasoning |
|---------------|-----------|-----------|-----------|
| "Heat protection when cooking" | Heat Resistant | YES | Protection = heat resistance |
| "Listening to audio" | Deep Bass | NO | Listening does not require bass |
| "Drawing lines around eyes" | Waterproof | NO | Drawing does not require waterproof |
| "Protecting phone from damage" | iPhone 15 Fit | YES | Protection requires physical fit |

---

## STOP: These are NEVER Hard Constraints

Before marking ANY attribute as hard constraint, check these categories:

### 1. Technology Versions (NEVER)
The VERSION of a technology is quality, not existence:
- Bluetooth 5.2 - NO, Bluetooth 4.0 still plays audio
- WiFi 6 - NO, WiFi 5 still connects
- USB 3.0 - NO, USB 2.0 still transfers data

### 2. Durability/Longevity Features (NEVER)
Features that make product LAST LONGER don't enable function:
- Waterproof - NO, Product works when dry
- Rustproof - NO, Product works before it rusts
- Smudge-proof - NO, Product works even if it smudges later
- Long-lasting - NO, Product works even if short-lived

### 3. Performance Specs (NEVER)
Quantitative specs are quality levels:
- 32-hour battery - NO, 8-hour battery still plays audio
- 26lbs/day ice - NO, 10lbs/day still makes ice
- 24-hour wear - NO, 4-hour wear still draws lines

### 4. Marketing Differentiators (NEVER)
Features highlighted to differentiate from competitors:
- Deep Bass Sound - NO, Regular sound is still audio
- Self-Cleaning - NO, Manual cleaning works
- Speed Charging - NO, Regular charging works
- VoiceAware - NO, Calls work without it

### 5. Material Choices (NEVER)
Alternative materials perform same function:
- Stainless Steel bottle - NO, Plastic holds water too
- Silicone oven mitt - NO, Cotton protects from heat too
- Bamboo tray - NO, Plastic serves food too
- 304 Stainless Steel - NO, Regular steel organizes items too
- Bamboo organizer - NO, Plastic organizes too

### 6. Product-Defining Mechanisms (NEVER)
The mechanism that DEFINES what the product IS cannot be a constraint - it's just saying "this product must be this product":
- Ice Maker needs "ice making mechanism" - NO, Tautology: "ice maker makes ice"
- Phone Holder needs "holding mechanism" - NO, Tautology: "holder holds things"
- Suction mount needs "suction" - NO, That's what makes it a suction mount
- Magnetic holder needs "magnets" - NO, That's what makes it magnetic

The question is: What EXTRA attributes beyond "being this product type" are required?

### 7. Convenience/Usability Features (NEVER)
Features that make product easier to use but don't enable core function:
- Handles on tray - NO, Can carry tray without handles
- Built-in sharpener - NO, Can sharpen pencil separately
- Foldable design - NO, Non-foldable still works
- 360 degree swivel - NO, Fixed angle still holds phone

### 8. Size/Dimensions (Almost NEVER)
Size is usually a preference, not a requirement:
- 15x10 inch tray - NO, 12x8 still serves food
- 32oz bottle - NO, 16oz still hydrates
- 11-inch figure - NO, 6-inch still plays

Exception: Device compatibility (e.g., iPhone 15 case MUST fit iPhone 15)

---

## Input

**Product Title:** {{title}}

**Bullet Points:**
{{bullet_points}}

**Description:**
{{description}}

**Validated Intended Use:** {{validated_use}}

**Product Type Taxonomy:**
{{taxonomy}}

**Attributes:**
{{attribute_table}}

**Product Attributes:**
{{product_attributes}}

---

## Worked Examples

### Example A: True Wireless Earbuds
**Validated Use:** "Listening to audio"

| Attribute | Step 1: Remove entirely? | Step 2: Mechanism or Quality? | Step 3: Use requires it? | HARD? |
|-----------|-------------------------|-------------------------------|-------------------------|-------|
| Bluetooth 5.2 | Still has Bluetooth capability | QUALITY (version) | "Listening" works with any BT | NO |
| Deep Bass | Still produces sound | QUALITY (frequency) | "Listening" = any audio | NO |
| 32hr Battery | Still plays audio | QUALITY (duration) | "Listening" works with less | NO |
| Water Resistant | Still plays audio | DURABILITY feature | "Listening" does not need waterproof | NO |

**Result: 0 hard constraints**

**Key insight:** "Listening to audio" requires speakers that produce sound. Everything else (bass quality, battery length, water resistance) improves experience but doesn't enable the core function.

---

### Example B: iPhone 15 Pro Case
**Validated Use:** "Protecting phone from damage"

| Attribute | Step 1: Remove entirely? | Step 2: Mechanism or Quality? | HARD? |
|-----------|-------------------------|-------------------------------|-------|
| iPhone 15 Pro Fit | Case doesn't attach | MECHANISM (fit enables protection) | YES |
| Silicone Material | Other materials protect | QUALITY choice | NO |
| MagSafe | Case still protects | FEATURE addition | NO |
| Black Color | Case still protects | AESTHETIC | NO |

**Result: 1 hard constraint** (Device Compatibility)

**Key insight:** iPhone 14 case physically CANNOT protect iPhone 15 - wrong dimensions. This is physical incompatibility.

---

### Example C: Oven Mitt
**Validated Use:** "Heat protection when cooking"

| Attribute | Step 1: Remove entirely? | Step 2: Mechanism or Quality? | HARD? |
|-----------|-------------------------|-------------------------------|-------|
| Heat Resistant | Burns hands = no protection | MECHANISM (enables protection) | YES |
| 500F rating | 400F still protects | QUALITY (how much) | NO |
| Silicone Material | Cotton also protects | MATERIAL choice | NO |
| Slip-resistant | Still protects from heat | CONVENIENCE | NO |

**Result: 1 hard constraint** (Essential Physical Property)

**Key insight:** "Heat protection" literally requires heat resistance. Without it, you burn. The specific temperature rating is quality.

---

### Example D: Eyeliner Pencil
**Validated Use:** "Drawing lines around eyes"

| Attribute | Step 1: Remove entirely? | Step 2: Mechanism or Quality? | HARD? |
|-----------|-------------------------|-------------------------------|-------|
| Waterproof | Still draws lines | DURABILITY (lasts longer) | NO |
| Smudge-proof | Still draws lines | DURABILITY (stays put) | NO |
| 24-Hour Wear | Still draws lines | DURABILITY (longevity) | NO |
| Built-in Sharpener | Still draws lines | CONVENIENCE | NO |

**Result: 0 hard constraints**

**Key insight:** "Drawing lines around eyes" = making visible marks. A basic pencil does this. Waterproof makes lines LAST longer, not EXIST.

---

### Example E: Water Bottle
**Validated Use:** "Carrying drinks for hydration"

| Attribute | Step 1: Remove entirely? | Step 2: Mechanism or Quality? | HARD? |
|-----------|-------------------------|-------------------------------|-------|
| Stainless Steel | Plastic holds liquid too | MATERIAL choice | NO |
| 24oz Size | Any size holds liquid | QUALITY (capacity) | NO |
| Insulated | Non-insulated holds liquid | FEATURE (temperature) | NO |
| BPA-Free | Still holds liquid | SAFETY feature | NO |

**Result: 0 hard constraints**

---

## Pre-Output Checklist

Before returning hard_constraints, verify EACH attribute passes ALL checks:

- Would removing this attribute make the product PHYSICALLY UNABLE to perform?
- Is this the MECHANISM of function (not quality/durability/convenience)?
- Does the validated use REQUIRE this specific attribute?
- Is this NOT a technology version, durability feature, performance spec, or marketing claim?
- Is this NOT a material choice, product-defining mechanism, convenience feature, or size specification?
- Would a reasonable person say "this product is BROKEN" without this attribute?

**If ANY check fails - NOT a hard constraint**

---

## Expected Distribution

Most consumer products have **0-1 hard constraints**:

| Count | Product Types |
|-------|---------------|
| **0** | Water bottles, earbuds, trays, makeup, toys, organizers, ice makers, jackets, phone holders |
| **1** | Phone cases (device fit), oven mitts (heat resistance), cables (connector type) |
| **2+** | Extremely rare - only multi-compatibility products |

**WARNING: If you identified 2+ hard constraints, review each one again using the checklist.**

---

## Output Format

You MUST use Chain of Thought reasoning. First, analyze each attribute step-by-step in the "reasoning" field, then provide your final answer as a simple list.

Return JSON with this structure:

```json
{
  "reasoning": "Step-by-step analysis...",
  "hard_constraints": ["AttributeName"]
}
```

Example with 1 hard constraint (Oven Mitt):

```json
{
  "reasoning": "Analyzing Oven Mitt for 'Heat protection when cooking'. Heat Resistant: Remove entirely? YES - burns hands. MECHANISM. HARD CONSTRAINT. 500F rating: QUALITY. NOT hard. Silicone: MATERIAL choice. NOT hard. Conclusion: 1 hard constraint.",
  "hard_constraints": ["Heat Resistance"]
}
```

Example with 0 hard constraints (Earbuds):

```json
{
  "reasoning": "Analyzing Earbuds for 'Listening to audio'. Bluetooth 5.2: VERSION - NOT hard. Deep Bass: QUALITY - NOT hard. 32hr Battery: PERFORMANCE SPEC - NOT hard. Water Resistant: DURABILITY - NOT hard. Conclusion: 0 hard constraints.",
  "hard_constraints": []
}
```
