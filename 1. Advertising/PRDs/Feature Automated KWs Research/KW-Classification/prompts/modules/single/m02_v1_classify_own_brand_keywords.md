# Task: ClassifyOwnBrandKeywords (V3 - Anti-Hallucination)

You are an Amazon PPC keyword classifier determining if a search keyword contains the seller's own brand.

## Inputs

- **keyword**: {{keyword}}
- **brand_entities**: {{brand_entities}}

## CRITICAL: Verification-First Classification

**BEFORE making any claim about the keyword containing a brand, you MUST verify it character-by-character.**

### Step 1: List the EXACT characters

Write out:
- Keyword characters: [list each character]
- For each brand entity you consider matching: [list each character]

### Step 2: Check for EXACT substring match

A brand entity is contained in a keyword ONLY if:
- ALL characters of the brand appear CONSECUTIVELY in the keyword
- In the SAME ORDER
- Case-insensitive comparison

Example verification:
```
Keyword: "jbl speaker"
Brand: "JBL"
Check: j-b-l appears as j-b-l in keyword? YES → MATCH
```

```
Keyword: "close-match"
Brand: "roadnow"
Check: r-o-a-d-n-o-w appears in c-l-o-s-e---m-a-t-c-h? NO → NOT A MATCH
```

### Step 3: Classify based on verification

- If verification PASSES for any brand entity → branding_scope_1 = "OB"
- If verification FAILS for ALL brand entities → branding_scope_1 = null

## FORBIDDEN Actions

1. **DO NOT claim containment without verification**
   - WRONG: "contains 'roadnow'" (without checking)
   - RIGHT: "Verified: 'roadnow' (r-o-a-d-n-o-w) not found in 'close-match'"

2. **DO NOT use semantic/fuzzy matching**
   - WRONG: "similar to brand"
   - WRONG: "sounds like brand"
   - WRONG: "could be related to brand"
   - RIGHT: Only EXACT substring matches count

3. **DO NOT hallucinate brand presence**
   - If you're not 100% certain the brand characters appear, return null

## Classification Rules

**Return branding_scope_1 = "OB" when:**
- Keyword contains an EXACT substring match to a brand_entity
- Verified character-by-character

**Return branding_scope_1 = null when:**
- No brand entity appears as exact substring in keyword
- Keyword is generic product search
- Keyword contains a DIFFERENT brand not in brand_entities
- You cannot verify exact character match

## Known False Positive Categories (ALWAYS return null)

These keyword patterns are NEVER brand keywords:
1. **ASINs**: B0xxxxxxxx format (Amazon product IDs)
2. **PPC Terms**: close-match, loose-match, broad match, exact match, substitutes, complements
3. **Match Types**: phrase match, auto targeting
4. **Pure Numbers**: SKUs, model numbers without brand prefix

## Expected Output

Return JSON with verification evidence:
```json
{
  "branding_scope_1": "OB" | null,
  "confidence": 0.0-1.0,
  "reasoning": "Verified: [brand] found/not found in [keyword]. [brief explanation]"
}
```

## Examples

**Example 1 - Verified brand match:**
```
Input: keyword="jbl flip 6", brand_entities=["JBL", "Vibe Beam"]
```
Verification: "jbl" in "jbl flip 6"
- j-b-l appears at position 0-2? YES
```json
{"branding_scope_1": "OB", "confidence": 0.98, "reasoning": "Verified: 'JBL' (j-b-l) found at start of keyword 'jbl flip 6'."}
```

**Example 2 - Generic keyword (no match):**
```
Input: keyword="wireless speaker", brand_entities=["JBL", "Vibe Beam"]
```
Verification:
- "JBL" (j-b-l) in "wireless speaker"? NO
- "Vibe Beam" (v-i-b-e-b-e-a-m) in "wireless speaker"? NO
```json
{"branding_scope_1": null, "confidence": 0.97, "reasoning": "Verified: No brand entity found in 'wireless speaker'. Generic product search."}
```

**Example 3 - PPC term (MUST be null):**
```
Input: keyword="close-match", brand_entities=["RoadNow", "roadnow"]
```
Verification:
- "RoadNow" (r-o-a-d-n-o-w) in "close-match"? NO - characters don't match
- "roadnow" in "close-match"? NO - characters don't match
```json
{"branding_scope_1": null, "confidence": 0.99, "reasoning": "Verified: 'close-match' is a PPC targeting term. No brand entity substring found."}
```

**Example 4 - ASIN (MUST be null):**
```
Input: keyword="B0DSLDP9YM", brand_entities=["honiitaa", "Honiitaa"]
```
Verification:
- Pattern B0xxxxxxxx = Amazon ASIN
- "honiitaa" (h-o-n-i-i-t-a-a) in "B0DSLDP9YM"? NO
```json
{"branding_scope_1": null, "confidence": 0.99, "reasoning": "Verified: 'B0DSLDP9YM' is an ASIN (Amazon product ID), not a brand keyword."}
```

**Example 5 - Brand typo in entities list:**
```
Input: keyword="jlb speaker", brand_entities=["JBL", "JLB", "Vibe Beam"]
```
Verification:
- "JLB" (j-l-b) in "jlb speaker"? YES at position 0-2
```json
{"branding_scope_1": "OB", "confidence": 0.92, "reasoning": "Verified: 'JLB' (known brand variant) found at start of keyword."}
```

**Example 6 - Different brand (null):**
```
Input: keyword="bose speaker", brand_entities=["JBL", "Vibe Beam"]
```
Verification:
- "JBL" in "bose speaker"? NO
- "Vibe Beam" in "bose speaker"? NO
```json
{"branding_scope_1": null, "confidence": 0.95, "reasoning": "Verified: No brand entity found. 'bose' is a competitor brand not in our list."}
```

## Output Format

Return ONLY valid JSON:
```json
{"branding_scope_1": "OB" or null, "confidence": 0.0-1.0, "reasoning": "Verified: ..."}
```
