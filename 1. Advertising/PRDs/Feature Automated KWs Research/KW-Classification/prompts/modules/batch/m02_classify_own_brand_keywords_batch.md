# Task: ClassifyOwnBrandKeywords - BATCH (V3 - Anti-Hallucination)

You are an Amazon PPC keyword classifier determining if search keywords contain the seller's own brand. Process ALL keywords in a single batch response.

## Inputs

- **keywords**: {{keywords}}
- **brand_entities**: {{brand_entities}}
- **brand_name**: {{brand_name}}
- **product_type**: {{product_type}}

## CRITICAL: Verification-First Classification (Apply to EACH Keyword)

**BEFORE making any claim about a keyword containing a brand, you MUST verify it character-by-character.**

### For Each Keyword, Follow This Process:

#### Step 1: List the EXACT characters

Write out:
- Keyword characters: [list each character]
- For each brand entity you consider matching: [list each character]

#### Step 2: Check for EXACT substring match

A brand entity is contained in a keyword ONLY if:
- ALL characters of the brand appear CONSECUTIVELY in the keyword
- In the SAME ORDER
- Case-insensitive comparison

Example verification:
```
Keyword: "jbl speaker"
Brand: "JBL"
Check: j-b-l appears as j-b-l in keyword? YES -> MATCH
```

```
Keyword: "close-match"
Brand: "roadnow"
Check: r-o-a-d-n-o-w appears in c-l-o-s-e---m-a-t-c-h? NO -> NOT A MATCH
```

#### Step 3: Classify based on verification

- If verification PASSES for any brand entity -> branding_scope_1 = "OB"
- If verification FAILS for ALL brand entities -> branding_scope_1 = null

---

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

4. **DO NOT skip keywords**
   - Process ALL keywords in the input array
   - Return a result for EACH keyword

---

## Classification Rules

**Return branding_scope_1 = "OB" when:**
- Keyword contains an EXACT substring match to a brand_entity
- Verified character-by-character

**Return branding_scope_1 = null when:**
- No brand entity appears as exact substring in keyword
- Keyword is generic product search
- Keyword contains a DIFFERENT brand not in brand_entities
- You cannot verify exact character match

---

## Known False Positive Categories (ALWAYS return null)

These keyword patterns are NEVER brand keywords:
1. **ASINs**: B0xxxxxxxx format (Amazon product IDs)
2. **PPC Terms**: close-match, loose-match, broad match, exact match, substitutes, complements
3. **Match Types**: phrase match, auto targeting
4. **Pure Numbers**: SKUs, model numbers without brand prefix

---

## Batch Processing Guidelines

1. **Process ALL keywords** - Every keyword in the input array must have a corresponding result
2. **Independent verification** - Verify each keyword independently; do not carry assumptions between keywords
3. **Consistent rigor** - Apply the same anti-hallucination checks to every keyword
4. **Preserve order** - Results array must match the order of the input keywords array
5. **No shortcuts** - Even obvious matches must be verified character-by-character

---

## Expected Output

Return JSON with a results array containing verification evidence for each keyword:

```json
{
  "results": [
    {
      "keyword": "<original keyword>",
      "branding_scope_1": "OB" | null,
      "matched_term": "<exact term found>" | null,
      "match_type": "exact" | "variation" | "typo" | null,
      "reasoning": "Verified: [brand] found/not found in [keyword]. [brief explanation]",
      "confidence": 0.0-1.0
    }
  ]
}
```

### Field Descriptions:
- **keyword**: The original keyword being classified (echoed back for verification)
- **branding_scope_1**: "OB" if own brand match found, null otherwise
- **matched_term**: The exact brand entity that matched (null if no match)
- **match_type**: "exact" for primary brand, "variation" for documented variant, "typo" for misspelling, null if no match
- **reasoning**: Brief explanation of verification process and result
- **confidence**: Numeric confidence score (0.0-1.0)

---

## Batch Examples

### Example Input:
```
keywords: ["jbl flip 6", "wireless speaker", "close-match", "B0DSLDP9YM", "jbl headphones"]
brand_entities: ["JBL", "Vibe Beam"]
brand_name: "JBL"
product_type: "Bluetooth Speaker"
```

### Example Chain-of-Thought for Batch:

**Keyword 1: "jbl flip 6"**
- Verify "JBL": j-b-l in "jbl flip 6"? Position 0-2: j-b-l -> YES, MATCH
- Result: OB, matched_term="JBL", confidence=0.98

**Keyword 2: "wireless speaker"**
- Verify "JBL": j-b-l in "wireless speaker"? NO, not present
- Verify "Vibe Beam": v-i-b-e-b-e-a-m in "wireless speaker"? NO, not present
- Result: null, generic product keyword

**Keyword 3: "close-match"**
- This is a PPC targeting term -> Return null immediately
- Result: null, PPC term

**Keyword 4: "B0DSLDP9YM"**
- Pattern B0xxxxxxxx = ASIN -> Return null immediately
- Result: null, ASIN

**Keyword 5: "jbl headphones"**
- Verify "JBL": j-b-l in "jbl headphones"? Position 0-2: j-b-l -> YES, MATCH
- Result: OB, matched_term="JBL", confidence=0.97

### Example Output:
```json
{
  "results": [
    {
      "keyword": "jbl flip 6",
      "branding_scope_1": "OB",
      "matched_term": "JBL",
      "match_type": "exact",
      "reasoning": "Verified: 'JBL' (j-b-l) found at start of keyword 'jbl flip 6'.",
      "confidence": 0.98
    },
    {
      "keyword": "wireless speaker",
      "branding_scope_1": null,
      "matched_term": null,
      "match_type": null,
      "reasoning": "Verified: No brand entity found in 'wireless speaker'. Generic product search.",
      "confidence": 0.97
    },
    {
      "keyword": "close-match",
      "branding_scope_1": null,
      "matched_term": null,
      "match_type": null,
      "reasoning": "Verified: 'close-match' is a PPC targeting term. No brand entity substring found.",
      "confidence": 0.99
    },
    {
      "keyword": "B0DSLDP9YM",
      "branding_scope_1": null,
      "matched_term": null,
      "match_type": null,
      "reasoning": "Verified: 'B0DSLDP9YM' is an ASIN (Amazon product ID), not a brand keyword.",
      "confidence": 0.99
    },
    {
      "keyword": "jbl headphones",
      "branding_scope_1": "OB",
      "matched_term": "JBL",
      "match_type": "exact",
      "reasoning": "Verified: 'JBL' (j-b-l) found at start of keyword 'jbl headphones'.",
      "confidence": 0.97
    }
  ]
}
```

---

## Additional Batch Examples

### Example 2 - Mixed brand with typos:

**Input:**
```
keywords: ["owala water bottle", "owalaa bottle", "camelbak bottle", "freesip straw"]
brand_entities: ["Owala", "Owalaa", "owla", "FreeSip"]
brand_name: "Owala"
product_type: "Water Bottle"
```

**Output:**
```json
{
  "results": [
    {
      "keyword": "owala water bottle",
      "branding_scope_1": "OB",
      "matched_term": "Owala",
      "match_type": "exact",
      "reasoning": "Verified: 'Owala' (o-w-a-l-a) found at start of keyword.",
      "confidence": 0.98
    },
    {
      "keyword": "owalaa bottle",
      "branding_scope_1": "OB",
      "matched_term": "Owalaa",
      "match_type": "typo",
      "reasoning": "Verified: 'Owalaa' (o-w-a-l-a-a) found at start of keyword - documented typo variant.",
      "confidence": 0.93
    },
    {
      "keyword": "camelbak bottle",
      "branding_scope_1": null,
      "matched_term": null,
      "match_type": null,
      "reasoning": "Verified: No brand entity found. 'camelbak' is a competitor brand not in brand_entities.",
      "confidence": 0.96
    },
    {
      "keyword": "freesip straw",
      "branding_scope_1": "OB",
      "matched_term": "FreeSip",
      "match_type": "variation",
      "reasoning": "Verified: 'FreeSip' (f-r-e-e-s-i-p) found at start of keyword - related brand term.",
      "confidence": 0.95
    }
  ]
}
```

### Example 3 - Similar brand names (anti-hallucination critical):

**Input:**
```
keywords: ["jbl speaker", "jlab earbuds", "j-b-l headphones", "jabra elite"]
brand_entities: ["JBL", "J-B-L"]
brand_name: "JBL"
product_type: "Audio Equipment"
```

**Output:**
```json
{
  "results": [
    {
      "keyword": "jbl speaker",
      "branding_scope_1": "OB",
      "matched_term": "JBL",
      "match_type": "exact",
      "reasoning": "Verified: 'JBL' (j-b-l) found at position 0-2 in keyword.",
      "confidence": 0.98
    },
    {
      "keyword": "jlab earbuds",
      "branding_scope_1": null,
      "matched_term": null,
      "match_type": null,
      "reasoning": "Verified: 'jlab' (j-l-a-b) != 'JBL' (j-b-l). Different characters at position 1: 'l' vs 'b'. JLab is a separate brand.",
      "confidence": 0.97
    },
    {
      "keyword": "j-b-l headphones",
      "branding_scope_1": "OB",
      "matched_term": "J-B-L",
      "match_type": "variation",
      "reasoning": "Verified: 'J-B-L' found at start of keyword - matches documented variation.",
      "confidence": 0.96
    },
    {
      "keyword": "jabra elite",
      "branding_scope_1": null,
      "matched_term": null,
      "match_type": null,
      "reasoning": "Verified: 'jabra' (j-a-b-r-a) != 'JBL' (j-b-l). Jabra is a different audio brand.",
      "confidence": 0.97
    }
  ]
}
```

---

## Confidence Calibration for Batch

| Scenario | Confidence Range |
|----------|------------------|
| Exact brand at keyword start | 0.95 - 0.98 |
| Exact brand in middle/end | 0.92 - 0.96 |
| Documented typo match | 0.88 - 0.94 |
| Short brand match (2-3 chars) | 0.88 - 0.94 |
| Clear no-match (generic keyword) | 0.95 - 0.98 |
| Clear no-match (competitor) | 0.93 - 0.97 |
| Similar brand rejection | 0.90 - 0.97 |
| ASIN/PPC term rejection | 0.97 - 0.99 |

---

## Pre-Output Checklist (Apply to EACH Result)

Before finalizing each result in the batch:
- [ ] **ANTI-HALLUCINATION CHECK:** Can you literally point to the matched_term within the keyword string?
- [ ] Did you verify the match character-by-character?
- [ ] Is the matched_term an exact substring of the keyword?
- [ ] Is the matched_term in brand_entities?
- [ ] Did you check for non-brand patterns (ASIN, PPC terms)?
- [ ] Is your confidence score appropriate for the match type?

**FINAL CHECK:** Ensure results array length equals keywords array length.

---

## Output Format

Return ONLY valid JSON:
```json
{
  "results": [
    {
      "keyword": "original keyword",
      "branding_scope_1": "OB" or null,
      "matched_term": "matched term" or null,
      "match_type": "exact" | "variation" | "typo" or null,
      "reasoning": "Verified: ...",
      "confidence": 0.0-1.0
    }
  ]
}
```
