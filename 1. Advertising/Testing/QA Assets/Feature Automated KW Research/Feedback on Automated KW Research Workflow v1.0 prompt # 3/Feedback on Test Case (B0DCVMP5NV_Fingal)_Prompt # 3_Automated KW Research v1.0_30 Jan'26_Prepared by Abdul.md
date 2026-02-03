# Keyword Group Validation Report
**Product:** B0DCVMP5NV (Food Warming Mat)
**Date:** January 28, 2026

---

## Summary

Validated 796 keywords against their assigned group rankings to verify each keyword contains the correct **Product Type + Attribute** combination.

| Metric | Count | % |
|--------|-------|---|
| **Total Keywords** | 796 | 100% |
| **Correctly Grouped** | 587 | 74% |
| **Incorrectly Grouped** | 209 | 26% |

---

## Key Issues Found

### 1. Product Type Mismatch (128 keywords)
Keywords assigned to "Food Warming Mat" groups but contain "tray/plate" instead of "mat/pad":

| Assigned Group | Issue | Count |
|----------------|-------|-------|
| NBR1 (Mat + Electric) | Keywords are about trays, not mats | 45 |
| NBR17 (Mat + Generic) | Keywords are about trays/plates | 46 |
| NBR18 (Warmer + Electric) | Keywords contain "mat" (should be NBR1) | 37 |

**Examples:**
- `"electric warming tray"` → Assigned NBR1, should be NBR18
- `"warming tray for food"` → Assigned NBR17, should be NBR27

### 2. Missing Attribute (81 keywords)
Keywords matched product type but missing the required attribute:

| Group | Missing Attribute | Count |
|-------|-------------------|-------|
| NBR1 | Missing "electric" | 35 |
| NBR6 | Missing "rollable/foldable" | 5 |
| NBR11 | Missing "silicone" | 7 |
| Others | Various attributes | 34 |

**Examples:**
- `"food warming mat"` → Assigned NBR1, missing "electric"
- `"warming mat for food"` → Assigned NBR11, missing "silicone"

---

## Recommended Actions

1. **Re-classify tray keywords** - Move "warming tray" keywords from Mat groups (NBR1-17) to Warmer groups (NBR18-27)

2. **Re-classify mat keywords** - Move "warming mat" keywords from Warmer groups (NBR18-27) to Mat groups (NBR1-17)

3. **Review attribute matching** - Keywords without specific attributes should fall to generic groups (NBR17 or NBR27)

---

## Addendum

See attached Excel file `keyword_validation_results_v2.xlsx` for full keyword-by-keyword validation with:
- Valid/Invalid flag for each keyword
- Expected product type and attribute
- Reason for invalidation

**Filter by `Valid = FALSE`** to see all keywords requiring review.
