# Task: ExtractOwnBrandVariations

Generate realistic brand name search variations for Amazon PPC.

## Input

- **brand_name**: {{brand_name}}

## Output Format

Return ONLY a JSON object with a "variations" array containing 10-14 strings:

```json
{"variations": ["BrandName", "brandname", "Brandnme"]}
```

## STRICT RULES

1. **EXACTLY 10-14 variations** — no more, no less
2. **NO DUPLICATES** — each variation must be unique
3. **First item = correct spelling**
4. **Strings only** — no numbers, no scores, no objects

## Variation Categories

Generate variations from these 6 categories:

### 1. CANONICAL (1 item)
The correct brand spelling — always first.

### 2. CASE/SPACING (2-4 items)
- Lowercase: `Owala` → `owala`
- Compound (no space): `Truly Indian` → `TrulyIndian`
- Hyphenated: `Truly Indian` → `Truly-Indian`
- Space insertion (for CamelCase): `KitchenAid` → `Kitchen Aid`, `kitchen aid`
  - Users often search CamelCase brands with spaces between words

### 3. TRUNCATION (0-1 item)
First word only IF brand has 2+ words AND first word is distinctive:
- `Truly Indian` → `Truly`
- `Antarctic Star` → `Antarctic`
- `Rx Crush` → `Rx`

Skip if first word is generic ("The", "My", "New").

### 4. KEYBOARD TYPOS (2-3 items)
Adjacent QWERTY key mistakes:
- `t` near `r,y,g`: `Truly` → `Teuly`
- `a` near `s,q`: `Owala` → `Owsla`
- `i` near `u,o`: `Indian` → `Undian`

### 5. PHONETIC/SPELLING (2-3 items)
Sound-alike mistakes:
- `Truly` → `Truely` (common misspelling)
- `Cisily` → `Cicily` (s/c confusion)
- `Owala` → `Ohwala` (sound interpretation)
- Missing/doubled letters: `Owala` → `Owla`, `Owalla`

### 6. SINGULAR/PLURAL (1-2 items)
For plural brand names (ending in 's'):
- `Transformers` → `Transformer` (drop the 's')
- `Transformers` → `transformer` (singular lowercase)

For singular brands commonly pluralized:
- `Transformer` → `Transformers`

**Skip if:**
- Brand is an acronym (JBL, IBM)
- Singular/plural doesn't apply (Owala, Nike)

## Examples

### Example 1: "Owala"
```json
{
  "variations": [
    "Owala",
    "owala",
    "OWALA",
    "Owla",
    "Owalla",
    "Ohwala",
    "Owalq",
    "Owals",
    "O-wala"
  ]
}
```
Count: 9 variations ✓

### Example 2: "Truly Indian"
```json
{
  "variations": [
    "Truly Indian",
    "truly indian",
    "TrulyIndian",
    "Truly-Indian",
    "Truly",
    "Truely Indian",
    "Trully Indian",
    "Truly Indien",
    "Teuly Indian",
    "Truly Inidan"
  ]
}
```
Count: 10 variations ✓

### Example 3: "JBL"
```json
{
  "variations": [
    "JBL",
    "jbl",
    "Jbl",
    "JLB",
    "JBK",
    "JNL",
    "J.B.L.",
    "J B L",
    "J-B-L",
    "JBl"
  ]
}
```
Count: 10 variations ✓

### Example 4: "Transformers"
```json
{
  "variations": [
    "Transformers",
    "transformers",
    "Transformer",
    "transformer",
    "Transfomers",
    "Transformrs",
    "Tranformers",
    "Tramsformers",
    "Transformerss",
    "Trans formers",
    "TRANSFORMERS"
  ]
}
```
Count: 11 variations ✓ (includes singular forms)

### Example 5: "KitchenAid"
```json
{
  "variations": [
    "KitchenAid",
    "kitchenaid",
    "Kitchen Aid",
    "kitchen aid",
    "Kitchen-Aid",
    "Kitchenaid",
    "KitchenAd",
    "KitchenAud",
    "KitchenAide",
    "Kitchin Aid"
  ]
}
```
Count: 10 variations ✓ (includes space insertion)

### Example 6: "Antarctic Star"
```json
{
  "variations": [
    "Antarctic Star",
    "antarctic star",
    "AntarcticStar",
    "Antarctic-Star",
    "Antarctic",
    "Antartic Star",
    "Antarcic Star",
    "Antarctik Star",
    "Antrctic Star",
    "Antarctic Starr"
  ]
}
```
Count: 10 variations ✓

## CRITICAL: Duplicate Check

**Before returning your response, you MUST perform this validation:**

1. Scan your variations list character by character
2. If ANY string appears more than once, DELETE the duplicate
3. Count the remaining UNIQUE items - must be exactly 10-14
4. If count < 10, add more unique typos or spacing variations
5. If count > 14, remove the weakest variations

**Example of duplicate that MUST be removed:**
```
["Owala", "owala", "Owla", "Owala", "Ohwala"]  ❌ "Owala" appears twice
["Owala", "owala", "Owla", "Ohwala", "Owalq"]  ✓ All unique
```

## Before Output Checklist

□ **SCAN FOR DUPLICATES** — each string must be unique (case-sensitive!)
□ Count is 10-14 items
□ First item is correct spelling
□ No duplicates in list
□ Only strings in array
□ Truncation included (if applicable)
□ Lowercase version included
□ At least 2 typos included
□ Singular/plural form included (if brand ends in 's' or is commonly pluralized)
□ Space-inserted version included (if CamelCase brand)

## DO NOT INCLUDE

- Sub-brands (FreeSip, ColorStay)
- Product names
- Category words (bottle, earbuds)
- Numbers or scores
- Nested objects

