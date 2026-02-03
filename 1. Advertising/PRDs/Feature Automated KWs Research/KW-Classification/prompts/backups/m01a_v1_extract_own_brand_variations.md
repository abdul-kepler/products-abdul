# Task: ExtractOwnBrandVariations

Generate realistic brand name search variations for Amazon PPC.

## Input

- **brand_name**: {{brand_name}}

## Output Format

Return ONLY a JSON object with a "variations" array containing 8-12 strings:

```json
{"variations": ["BrandName", "brandname", "Brandnme"]}
```

## STRICT RULES

1. **EXACTLY 8-12 variations** — no more, no less
2. **NO DUPLICATES** — each variation must be unique
3. **First item = correct spelling**
4. **Strings only** — no numbers, no scores, no objects

## Variation Categories

Generate variations from these 5 categories:

### 1. CANONICAL (1 item)
The correct brand spelling — always first.

### 2. CASE/SPACING (2-3 items)
- Lowercase: `Owala` → `owala`
- Compound (no space): `Truly Indian` → `TrulyIndian`
- Hyphenated: `Truly Indian` → `Truly-Indian`

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
    "J B L"
  ]
}
```
Count: 8 variations ✓

### Example 4: "Antarctic Star"
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

## Before Output Checklist

□ Count is 8-12 items
□ First item is correct spelling
□ No duplicates in list
□ Only strings in array
□ Truncation included (if applicable)
□ Lowercase version included
□ At least 2 typos included

## DO NOT INCLUDE

- Sub-brands (FreeSip, ColorStay)
- Product names
- Category words (bottle, earbuds)
- Numbers or scores
- Nested objects
