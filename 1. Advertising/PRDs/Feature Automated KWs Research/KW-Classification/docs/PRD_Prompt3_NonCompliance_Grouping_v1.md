# PRD: Prompt 3 Enhancement - Non-Compliance Grouping

**Version:** 1.0
**Date:** February 1, 2026
**Author:** Abdul
**Status:** Draft

---

## 1. Overview

### 1.1 Background

Prompt 3 in the Automated Keyword Research pipeline is responsible for mapping keywords to a Global Mapping Table based on Product Types and Attributes (Variants, Use Cases, Audiences). The preceding 16 modules (M01-M16) have been enhanced to improve quality of attribute extraction and R/S/C/N classification.

This PRD defines enhancements to Prompt 3 to introduce **non-compliance grouping** - a mechanism to identify and deprioritize keywords that explicitly contradict product attributes.

### 1.2 Problem Statement

**Current behavior:**
- Keywords are mapped to the most specific matching row based on Product Type + Attribute alignment
- Keywords that don't match any attribute fall back to the "PT-alone" row
- No distinction is made between keywords that are **neutral** (no attribute mentioned) vs. keywords that **contradict** an attribute

**Example gap:**
- Product: Digital Camera, Color=Blue (rank 1)
- Keyword A: "digital camera" → PT-alone row (neutral - no color mentioned) ✓
- Keyword B: "red digital camera" → Currently also falls to PT-alone row ✗

Keyword B explicitly contradicts the product's color attribute, yet receives the same grouping as neutral keywords.

### 1.3 Proposed Solution

Extend the Global Mapping Table with **non-compliant rows** that capture keywords which explicitly contradict product attributes. Non-compliant rows are ordered inversely by attribute rank - the most critical non-compliance goes to the last row.

---

## 2. Scope

### 2.1 In Scope

- Enhancement to Prompt 3 (keyword-to-attribute mapping)
- Addition of non-compliant rows to the Global Mapping Table
- Logic for detecting attribute contradiction vs. absence
- Assignment rules for mixed compliance scenarios
- Output schema updates

### 2.2 Out of Scope

- Changes to M01-M16 (attribute extraction and R/S/C/N classification)
- Hard constraint logic (handled by M11 - keywords failing hard constraints are already marked Negative)
- Changes to BrandScope classification (OB/CB/NB)

### 2.3 Prerequisite

This grouping applies **only to Relevant (R) keywords**. Keywords classified as Substitute (S), Complementary (C), or Negative (N) by the upstream modules are handled separately (Group 1 in existing logic).

---

## 3. Definitions

| Term | Definition |
|------|------------|
| **Compliant** | Keyword explicitly matches or aligns with the attribute value (e.g., "blue camera" matches Color=Blue) |
| **Non-Compliant** | Keyword explicitly contradicts the attribute value (e.g., "red camera" contradicts Color=Blue) |
| **Absent/Neutral** | Keyword does not mention the attribute dimension at all (e.g., "digital camera" has no color reference) |
| **Attribute Rank** | Priority of the attribute; lower rank = higher importance (Rank 1 is most critical) |

---

## 4. Requirements

### 4.1 Global Mapping Table Structure

#### 4.1.1 Current Structure (per Product Type block)

```
Row 1: PT + Variant (rank 1)
Row 2: PT + Variant (rank 2)
...
Row N: PT + Use Case (rank 1)
...
Row M: PT + Audience (rank 1)
...
Row L: PT alone (fallback)
```

#### 4.1.2 New Structure (Option B: Compliance Dominates PT Hierarchy)

The Global Mapping Table is organized into **two distinct sections**:
1. **Compliant Section**: All compliant rows across ALL Product Types
2. **Non-Compliant Section**: All non-compliant rows across ALL Product Types

This ensures **any compliant keyword (regardless of PT) ranks higher than any non-compliant keyword**.

```
╔══════════════════════════════════════════════════════════════════════════╗
║  SECTION: COMPLIANT                                                       ║
╠══════════════════════════════════════════════════════════════════════════╣
║  --- PT1 Block (Primary Product Type) ---                                 ║
║  Row 1:  PT1 + Variant (rank 1)         [Compliant]                       ║
║  Row 2:  PT1 + Variant (rank 2)         [Compliant]                       ║
║  ...                                                                      ║
║  Row N:  PT1 alone                      [Fallback]                        ║
║                                                                           ║
║  --- PT2 Block (Secondary Product Type) ---                               ║
║  Row N+1: PT2 + Variant (rank 1)        [Compliant]                       ║
║  Row N+2: PT2 + Variant (rank 2)        [Compliant]                       ║
║  ...                                                                      ║
║  Row M:   PT2 alone                     [Fallback]                        ║
╠══════════════════════════════════════════════════════════════════════════╣
║  SECTION: NON-COMPLIANT                                                   ║
╠══════════════════════════════════════════════════════════════════════════╣
║  --- PT2 Block (Secondary PT first - lower priority NC) ---               ║
║  Row M+1: PT2 + Attribute (lowest rank) [Non-Compliant]                   ║
║  ...                                                                      ║
║  Row X:   PT2 + Attribute (rank 1)      [Non-Compliant]                   ║
║                                                                           ║
║  --- PT1 Block (Primary PT last - highest priority NC = worst) ---        ║
║  Row X+1: PT1 + Attribute (lowest rank) [Non-Compliant]                   ║
║  ...                                                                      ║
║  Row Y:   PT1 + Attribute (rank 1)      [Non-Compliant] ← LAST ROW        ║
╚══════════════════════════════════════════════════════════════════════════╝
```

**Key principles:**
1. **Compliance dominates**: All compliant rows appear before all non-compliant rows
2. **Within Compliant section**: PT hierarchy applies (PT1 before PT2)
3. **Within Non-Compliant section**: Reverse order - PT2 NC before PT1 NC, and within each PT, lowest-rank NC first, highest-rank NC last
4. **Last row**: Non-compliant on rank-1 attribute of PT1 = worst possible match

### 4.2 Compliance Classification Rules

For each keyword, evaluate each attribute and classify as:

| Classification | Condition | Example |
|----------------|-----------|---------|
| **Compliant** | Keyword explicitly matches or semantically aligns with attribute value | "blue camera" + Color=Blue |
| **Non-Compliant** | Keyword explicitly contradicts attribute value | "red camera" + Color=Blue |
| **Absent** | Keyword does not reference the attribute dimension | "digital camera" + Color=Blue |

#### 4.2.1 Semantic Tolerance for Compliance

Minor variations should be treated as **Compliant**:

| Keyword | Product Attribute | Verdict | Reason |
|---------|-------------------|---------|--------|
| "light blue camera" | Color=Blue | Compliant | Shade of blue |
| "navy camera" | Color=Blue | Compliant | Shade of blue |
| "sky blue camera" | Color=Blue | Compliant | Shade of blue |
| "blue-green camera" | Color=Blue | Compliant | Contains blue |
| "red camera" | Color=Blue | Non-Compliant | Different color |
| "camera" | Color=Blue | Absent | No color mentioned |
| "colorful camera" | Color=Blue | Absent | No specific color |

### 4.3 Keyword Assignment Rules

#### 4.3.1 Rule 1: Pure Compliant Keywords

If a keyword is **compliant on one or more attributes** and **non-compliant on none**:
- Assign to the most specific compliant row (existing Subset Rule applies)
- More attribute matches = more specific row

**Example:**
- Keyword: "blue metal camera for kids"
- Matches: Color=Blue ✓, Material=Metal ✓, Audience=Kids ✓
- Assignment: Most specific combination row (PT + Color + Material + Audience)

#### 4.3.2 Rule 2: Pure Absent Keywords

If a keyword has **no compliant matches** and **no non-compliant contradictions** (all absent):
- Assign to the **PT-alone fallback row**

**Example:**
- Keyword: "digital camera"
- Color: Absent, Material: Absent, Audience: Absent
- Assignment: PT-alone row

#### 4.3.3 Rule 3: Any Non-Compliance Present

If a keyword has **at least one non-compliant attribute** (regardless of other compliant matches):
- Assign to the **non-compliant row of the highest-ranked non-compliant attribute**

**Example:**
- Keyword: "blue plastic camera"
- Color=Blue (rank 1): Compliant ✓
- Material=Metal (rank 2): Non-Compliant ✗ (plastic ≠ metal)
- Audience=Kids (rank 3): Absent
- Assignment: **Material non-compliant row** (highest-ranked non-compliant attribute)

#### 4.3.4 Rule 4: Multiple Non-Compliances

If a keyword contradicts **multiple attributes**:
- Assign to the non-compliant row of the **highest-ranked** non-compliant attribute

**Example:**
- Keyword: "red plastic camera for adults"
- Color=Blue (rank 1): Non-Compliant ✗
- Material=Metal (rank 2): Non-Compliant ✗
- Audience=Kids (rank 3): Non-Compliant ✗
- Assignment: **Color non-compliant row** (rank 1 = highest-ranked non-compliant)

#### 4.3.5 Rule 5: Non-Compliance Overrides Subset Rule

The Subset Rule (combination rows for multi-attribute matches) does **NOT apply** when any non-compliance is present.

**Example:**
- Keyword: "blue metal camera for adults"
- Color=Blue (rank 1): Compliant ✓
- Material=Metal (rank 2): Compliant ✓
- Audience=Kids (rank 3): Non-Compliant ✗
- Assignment: **Audience non-compliant row** (NOT a Color+Material combination row)

### 4.4 Assignment Priority Summary

```
Priority 1: Check for any non-compliance
            → YES: Assign to highest-ranked non-compliant attribute's row
            → NO: Continue to Priority 2

Priority 2: Check for compliant matches
            → YES: Assign to most specific compliant row (Subset Rule)
            → NO: Continue to Priority 3

Priority 3: All attributes absent
            → Assign to PT-alone fallback row
```

---

## 5. Output Schema

### 5.1 Top-Level Output Structure

The output includes a new `Sections` array that explicitly marks the compliant and non-compliant sections:

```json
{
  "Sections": [
    {
      "SectionName": "Compliant",
      "SectionOrder": 1,
      "StartRow": 1,
      "EndRow": 8,
      "Description": "All compliant and fallback rows across all Product Types"
    },
    {
      "SectionName": "Non-Compliant",
      "SectionOrder": 2,
      "StartRow": 9,
      "EndRow": 16,
      "Description": "All non-compliant rows across all Product Types (reverse priority order)"
    }
  ],
  "MappingTable": [...],
  "KeywordMapping": [...]
}
```

### 5.2 MappingTable Schema Update

```json
{
  "MappingTable": [
    {
      "InitialRow": 1,
      "Section": "Compliant",
      "ProductType": "Digital Camera",
      "ProductTypeRank": 1,
      "DimensionType": "Variant",
      "DimensionValue": "Blue",
      "DimensionSubtype": "Color",
      "AttributeRank": 1,
      "ComplianceType": "Compliant",
      "FinalMappingRow": 1
    },
    {
      "InitialRow": 16,
      "Section": "Non-Compliant",
      "ProductType": "Digital Camera",
      "ProductTypeRank": 1,
      "DimensionType": "Variant",
      "DimensionValue": "Blue",
      "DimensionSubtype": "Color",
      "AttributeRank": 1,
      "ComplianceType": "Non-Compliant",
      "FinalMappingRow": 16
    }
  ]
}
```

**New/Updated fields:**
- `Section` ∈ {"Compliant", "Non-Compliant"} - Indicates which section the row belongs to
- `ProductTypeRank` - Rank of the Product Type (1 = primary)
- `AttributeRank` - Rank of the attribute within the PT
- `ComplianceType` ∈ {"Compliant", "Non-Compliant", "Fallback"}

### 5.3 KeywordMapping Schema Update

```json
{
  "KeywordMapping": [
    {
      "Keyword": "red digital camera",
      "Tag3": "NBR",
      "BrandScope": "NB",
      "Relation": "R",
      "Section": "Non-Compliant",
      "FinalMappingRow": 16,
      "ComplianceStatus": "Non-Compliant",
      "NonCompliantAttribute": "Color",
      "NonCompliantAttributeRank": 1,
      "NonCompliantProductType": "Digital Camera",
      "NonCompliantProductTypeRank": 1
    }
  ]
}
```

**New fields:**
- `Section` ∈ {"Compliant", "Non-Compliant"} - Which section the keyword is assigned to
- `ComplianceStatus` ∈ {"Compliant", "Non-Compliant", "Neutral"}
- `NonCompliantAttribute`: The attribute that triggered non-compliance (null if compliant/neutral)
- `NonCompliantAttributeRank`: Rank of the non-compliant attribute (null if compliant/neutral)
- `NonCompliantProductType`: The PT of the non-compliant row (null if compliant/neutral)
- `NonCompliantProductTypeRank`: Rank of that PT (null if compliant/neutral)

---

## 6. Examples

### 6.1 Example Product Setup (Multi-PT)

**Product with 2 Product Types:**

| Attribute | Type | Subtype | PT Rank | Attr Rank |
|-----------|------|---------|---------|-----------|
| Digital Camera | Product Type | - | 1 | - |
| Action Camera | Product Type | - | 2 | - |
| Blue | Variant | Color | - | 1 |
| Metal | Variant | Material | - | 2 |
| Kids | Audience | - | - | 3 |

*(Same attributes apply to both Product Types)*

### 6.2 Expected Mapping Table (Option B Structure)

```
╔═══════════════════════════════════════════════════════════════════════════════════════╗
║  SECTION: COMPLIANT (Rows 1-8)                                                         ║
╠═══════════════════════════════════════════════════════════════════════════════════════╣
```

| Row | Section | PT | PT Rank | Dimension | Value | Attr Rank | Compliance |
|-----|---------|-----|---------|-----------|-------|-----------|------------|
| 1 | Compliant | Digital Camera | 1 | Variant | Blue (Color) | 1 | Compliant |
| 2 | Compliant | Digital Camera | 1 | Variant | Metal (Material) | 2 | Compliant |
| 3 | Compliant | Digital Camera | 1 | Audience | Kids | 3 | Compliant |
| 4 | Compliant | Digital Camera | 1 | None | - | - | Fallback |
| 5 | Compliant | Action Camera | 2 | Variant | Blue (Color) | 1 | Compliant |
| 6 | Compliant | Action Camera | 2 | Variant | Metal (Material) | 2 | Compliant |
| 7 | Compliant | Action Camera | 2 | Audience | Kids | 3 | Compliant |
| 8 | Compliant | Action Camera | 2 | None | - | - | Fallback |

```
╠═══════════════════════════════════════════════════════════════════════════════════════╣
║  SECTION: NON-COMPLIANT (Rows 9-14)                                                    ║
║  Note: PT2 (Action Camera) NC rows come BEFORE PT1 (Digital Camera) NC rows            ║
║        Within each PT: lowest-rank NC first, highest-rank NC last                      ║
╠═══════════════════════════════════════════════════════════════════════════════════════╣
```

| Row | Section | PT | PT Rank | Dimension | Value | Attr Rank | Compliance |
|-----|---------|-----|---------|-----------|-------|-----------|------------|
| 9 | Non-Compliant | Action Camera | 2 | Audience | Kids | 3 | Non-Compliant |
| 10 | Non-Compliant | Action Camera | 2 | Variant | Metal (Material) | 2 | Non-Compliant |
| 11 | Non-Compliant | Action Camera | 2 | Variant | Blue (Color) | 1 | Non-Compliant |
| 12 | Non-Compliant | Digital Camera | 1 | Audience | Kids | 3 | Non-Compliant |
| 13 | Non-Compliant | Digital Camera | 1 | Variant | Metal (Material) | 2 | Non-Compliant |
| 14 | Non-Compliant | Digital Camera | 1 | Variant | Blue (Color) | 1 | **Non-Compliant (LAST)** |

### 6.3 Keyword Assignment Examples

| Keyword | PT Match | Color | Material | Audience | Assignment | Section | Row |
|---------|----------|-------|----------|----------|------------|---------|-----|
| "blue digital camera" | PT1 | ✓ | - | - | PT1 Compliant Color | Compliant | 1 |
| "blue metal digital camera for kids" | PT1 | ✓ | ✓ | ✓ | PT1 Most specific | Compliant | 1 |
| "digital camera" | PT1 | - | - | - | PT1 Fallback | Compliant | 4 |
| "blue action camera" | PT2 | ✓ | - | - | PT2 Compliant Color | Compliant | 5 |
| "action camera" | PT2 | - | - | - | PT2 Fallback | Compliant | 8 |
| "red action camera" | PT2 | ✗ | - | - | PT2 NC Color | Non-Compliant | 11 |
| "action camera for adults" | PT2 | - | - | ✗ | PT2 NC Audience | Non-Compliant | 9 |
| "red digital camera" | PT1 | ✗ | - | - | PT1 NC Color | Non-Compliant | **14** |
| "blue plastic digital camera" | PT1 | ✓ | ✗ | - | PT1 NC Material | Non-Compliant | 13 |
| "red plastic camera for adults" | PT1 | ✗ | ✗ | ✗ | PT1 NC Color (highest) | Non-Compliant | **14** |

Legend: ✓ = Compliant, ✗ = Non-Compliant, - = Absent

### 6.4 Key Observations from Examples

1. **"blue action camera" (Row 5) ranks HIGHER than "red digital camera" (Row 14)**
   - Compliant PT2 keyword beats Non-Compliant PT1 keyword
   - This is the desired behavior (Option B)

2. **"red action camera" (Row 11) ranks HIGHER than "red digital camera" (Row 14)**
   - NC on secondary PT ranks higher than NC on primary PT
   - NC on primary PT is the worst case

3. **Row 14 is the worst possible match**
   - Non-Compliant on rank-1 attribute (Color) of rank-1 PT (Digital Camera)
   - Multiple keywords can land here if they all fail on the most critical attribute

---

## 7. Edge Cases

### 7.1 Synonyms and Translations

Apply semantic equivalence for compliance checking:

| Keyword | Attribute | Verdict |
|---------|-----------|---------|
| "metallic camera" | Material=Metal | Compliant |
| "aluminum camera" | Material=Metal | Compliant (metal variant) |
| "wooden camera" | Material=Metal | Non-Compliant |
| "camera for children" | Audience=Kids | Compliant (synonym) |
| "camera para niños" | Audience=Kids | Compliant (translation) |

### 7.2 Ambiguous Keywords

When a keyword is ambiguous or could be interpreted multiple ways:
- Default to **Absent** (not Non-Compliant)
- Only mark Non-Compliant when there is clear contradiction

| Keyword | Attribute | Verdict | Reason |
|---------|-----------|---------|--------|
| "professional camera" | Audience=Kids | Non-Compliant | Explicitly different audience |
| "camera" | Audience=Kids | Absent | No audience indicated |
| "everyday camera" | Use Case=Travel | Absent | Generic, not contradictory |

### 7.3 Multiple Product Types

When multiple Product Types exist, the table is organized with **compliance dominating PT hierarchy**:

```
╔═══════════════════════════════════════════════════════════════════════════╗
║  SECTION: COMPLIANT                                                        ║
╠═══════════════════════════════════════════════════════════════════════════╣
║  PT1 (Primary) compliant rows + fallback                                   ║
║  PT2 (Secondary) compliant rows + fallback                                 ║
║  PT3 (Tertiary) compliant rows + fallback                                  ║
║  ... (all PTs in ascending PT rank order)                                  ║
╠═══════════════════════════════════════════════════════════════════════════╣
║  SECTION: NON-COMPLIANT                                                    ║
╠═══════════════════════════════════════════════════════════════════════════╣
║  PT3 (Tertiary) non-compliant rows (lowest attr rank → highest)            ║
║  PT2 (Secondary) non-compliant rows (lowest attr rank → highest)           ║
║  PT1 (Primary) non-compliant rows (lowest attr rank → highest)             ║
║  ... (all PTs in DESCENDING PT rank order - primary PT NC rows LAST)       ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

**Rationale:** A compliant keyword for a secondary product is still a better match than a non-compliant keyword for the primary product. The worst possible case is non-compliance on the highest-ranked attribute of the primary PT.

---

## 8. Validation & Testing

### 8.1 Test Cases Required

1. **Pure compliant scenarios** - Keywords matching 1, 2, or all attributes
2. **Pure absent scenarios** - Keywords with no attribute references
3. **Single non-compliance** - Keywords contradicting exactly one attribute
4. **Multiple non-compliance** - Keywords contradicting 2+ attributes
5. **Mixed compliance** - Keywords with some compliant + some non-compliant
6. **Semantic tolerance** - Synonyms, translations, shade variations
7. **Ambiguous keywords** - Edge cases that could be interpreted multiple ways

### 8.2 Acceptance Criteria

**Table Structure:**
- [ ] Output includes `Sections` array with Compliant and Non-Compliant sections clearly marked
- [ ] All compliant rows (across all PTs) appear before all non-compliant rows
- [ ] Within Compliant section: PTs ordered by ascending PT rank (PT1 before PT2)
- [ ] Within Non-Compliant section: PTs ordered by descending PT rank (PT2 NC before PT1 NC)
- [ ] Within each PT's NC block: rows ordered by ascending attribute rank (lowest NC first, highest NC last)
- [ ] Last row in table = NC on rank-1 attribute of PT1

**Row Assignment:**
- [ ] Each MappingTable row includes `Section` field ("Compliant" or "Non-Compliant")
- [ ] Each KeywordMapping entry includes `Section` field
- [ ] Keywords with any non-compliance go to Non-Compliant section
- [ ] Keywords with multiple non-compliances go to highest-ranked NC attribute's row
- [ ] Subset Rule does not apply when non-compliance present
- [ ] Absent/neutral keywords go to PT-alone fallback (in Compliant section)

**Classification:**
- [ ] Semantic tolerance correctly identifies compliant variations (shades, synonyms)
- [ ] Ambiguous keywords default to Absent, not Non-Compliant
- [ ] Explicit contradictions correctly identified as Non-Compliant

---

## 9. Implementation Notes

### 9.1 Prompt Structure Suggestion

The enhanced Prompt 3 should include:

1. **Phase 0 (NEW): Compliance Classification**
   - For each keyword × attribute combination, classify as Compliant/Non-Compliant/Absent
   - Output intermediate classification before assignment

2. **Phase 1: Build Extended Mapping Table**
   - Compliant rows (existing logic)
   - PT-alone fallback
   - Non-compliant rows (reverse rank order)

3. **Phase 2-4:** Existing logic with updated assignment rules

### 9.2 Performance Consideration

The mapping table roughly doubles in size. For a product with:
- 2 Product Types
- 6 Attributes each

Before: 2 × 7 = 14 rows
After: 2 × 13 = 26 rows (6 compliant + 1 fallback + 6 non-compliant per PT)

This is acceptable per stakeholder confirmation.

---

## 10. Open Questions

None at this time. All decision points resolved.

---

## 11. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-01 | Abdul | Initial draft |
| 1.1 | 2026-02-01 | Abdul | Updated to Option B (compliance dominates PT hierarchy); Added Sections output; Multi-PT examples |

---

*End of Document*
