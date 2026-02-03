# Pipeline Trace Report - M01-M16

**Generated:** 2026-01-14

## Overview

This report traces all 10 ASINs with full pipeline coverage through the M01-M16 classification chain, verifying data flow and classification results.

## Summary

| ASIN | Product | OB | CB | R | S | C | N | Total KWs |
|------|---------|---:|---:|---:|---:|---:|---:|----------:|
| B0F42MT8JX | Ice Maker | 3 | 44 | 21 | 1 | 7 | 29 | 406 |
| B000H3I2JG | Revlon Eyeliner | 3 | 26 | 15 | 1 | 22 | 15 | 417 |
| B09LCKZBTW | Serving Tray | 0 | 1 | 23 | 6 | 17 | 13 | 294 |
| B08J8GZXKZ | Oven Mitt | 10 | 14 | 11 | 11 | 5 | 24 | 217 |
| B0CJ4WZXQF | Sink Caddy | 6 | 6 | 31 | 0 | 5 | 8 | 143 |
| B077YYP739 | Transformers Toy | 73 | 4 | 38 | 5 | 3 | 4 | 144 |
| B0DSHWLXG6 | Phone Holder | 3 | 18 | 10 | 2 | 4 | 4 | 145 |
| B0BZYCJK89 | Water Bottle | 18 | 31 | 12 | 1 | 2 | 0 | 127 |
| B0BQPGJ9LQ | JBL Earbuds | 31 | 39 | 13 | 2 | 5 | 11 | 120 |
| B0D6YNWLTS | Puffer Jacket | 2 | 25 | 29 | 2 | 5 | 0 | 92 |
| **TOTAL** | | **149** | **208** | **203** | **31** | **75** | **108** | **2,105** |

## Pipeline Coverage Status

All 10 ASINs have **complete coverage** across all pipeline stages:

| Stage | Modules | Coverage | Description |
|-------|---------|----------|-------------|
| Stage 1 | M01, M01a, M01b, M03 | 10/10 ✓ | Brand extraction & competitors |
| Stage 3 | M06, M07, M08, M09, M10, M11 | 10/10 ✓ | Product analysis |
| Stage 2+4 | M02, M04, M05, M13-M16 | 10/10 ✓ | Keyword classification |

---

## Detailed Traces by ASIN

### 1. B0F42MT8JX - Ice Maker (Antarctic Star)

**Stage 1: Brand Extraction**
- M01: ✓ Brand entities: Antarctic Star, AntarcticStar, Antartic Star...
- M01a: ✓ Brand variations extracted
- M01b: ✓ Brand-related terms extracted
- M03: ✓ Competitors generated

**Stage 3: Product Analysis**
- M06: ✓ Taxonomy: Ice Maker
- M07: ✓ Attributes extracted
- M08: ✓ Attribute ranks assigned
- M09: ✓ Primary use identified
- M10: ✓ Primary use validated
- M11: ✓ Hard constraints identified

**Keyword Classifications (406 total)**
| OB | CB | NB | R | S | C | N |
|---:|---:|---:|---:|---:|---:|---:|
| 3 | 44 | 298 | 21 | 1 | 7 | 29 |

**Sample Traces:**
1. "small portable ice maker" → M02:- → M04:- → M05:NB
2. "antarctic star ice maker" → M02:OB (Own Brand detected)
3. "frigidaire ice machine" → M02:- → M04:CB (Competitor Brand detected)

---

### 2. B000H3I2JG - Revlon Eyeliner

**Stage 1: Brand Extraction**
- M01: ✓ Brand entities: Revlon, ColorStay, Revlon Consumer Products Corporation...
- M01a: ✓ M01b: ✓ M03: ✓

**Stage 3: Product Analysis**
- M06: ✓ Taxonomy: Pencil Eyeliner > Eyeliner > Eye Makeup
- M07-M11: ✓ All stages complete

**Keyword Classifications (417 total)**
| OB | CB | NB | R | S | C | N |
|---:|---:|---:|---:|---:|---:|---:|
| 3 | 26 | 334 | 15 | 1 | 22 | 15 |

**Notable:** Highest C (Complementary) count at 22

---

### 3. B09LCKZBTW - Serving Tray (WEBACOO)

**Stage 1: Brand Extraction**
- M01: ✓ Brand entities: WEBACOO, Sachsen-Us, Webacoo...
- M01a: ✓ M01b: ✓ M03: ✓

**Stage 3: Product Analysis**
- M06: ✓ Taxonomy: Serving Tray
- M07-M11: ✓ All stages complete

**Keyword Classifications (294 total)**
| OB | CB | NB | R | S | C | N |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 1 | 233 | 23 | 6 | 17 | 13 |

**Notable:** Second highest S (Substitute) count at 6

---

### 4. B08J8GZXKZ - Oven Mitt (KitchenAid)

**Stage 1: Brand Extraction**
- M01: ✓ Brand entities: KitchenAid, Kitchen Aid, Kitchenaid...
- M01a: ✓ M01b: ✓ M03: ✓

**Stage 3: Product Analysis**
- M06: ✓ Taxonomy: Oven Mitt
- M11: ✓ Hard constraints: ['Heat Resistant up to 500°F']

**Keyword Classifications (217 total)**
| OB | CB | NB | R | S | C | N |
|---:|---:|---:|---:|---:|---:|---:|
| 10 | 14 | 141 | 11 | 11 | 5 | 24 |

**Notable:** Only ASIN with 10+ S (Substitute) keywords - **best for S testing**

---

### 5. B0CJ4WZXQF - Sink Caddy (Cisily)

**Stage 1: Brand Extraction**
- M01: ✓ Brand entities: Cisily, CISILY, Cisly...
- M01a: ✓ M01b: ✓ M03: ✓

**Stage 3: Product Analysis**
- M06: ✓ Taxonomy: Sink Caddy Organizer > Kitchen Caddy Organizer > Kitchen Storage and Organization

**Keyword Classifications (143 total)**
| OB | CB | NB | R | S | C | N |
|---:|---:|---:|---:|---:|---:|---:|
| 6 | 6 | 87 | 31 | 0 | 5 | 8 |

**Notable:** Highest R (Relevant) count at 31

**Sample Full Traces:**
- "oxo kitchen sink caddy" → M02:- → M04:CB → M05:- → M13:Same → M14:R
- "soap dispenser kitchen sink" → M02:- → M04:- → M05:NB → M13:Diff → M15:- → M16:C
- "kitchen sink" → M02:- → M04:- → M05:NB → M13:Diff → M15:- → M16:N

---

### 6. B077YYP739 - Transformers Toy (Hasbro)

**Stage 1: Brand Extraction**
- M01: ✓ Brand entities: Transformers, Hasbro, Cyber Commander Series, Optimus Prime...
- M01a: ✓ M01b: ✓ M03: ✓

**Stage 3: Product Analysis**
- M06: ✓ Taxonomy: Transformer > Action Figure > Toys

**Keyword Classifications (144 total)**
| OB | CB | NB | R | S | C | N |
|---:|---:|---:|---:|---:|---:|---:|
| 73 | 4 | 15 | 38 | 5 | 3 | 4 |

**Notable:** Highest OB (Own Brand) count at 73 - **best for OB testing**

---

### 7. B0DSHWLXG6 - Phone Holder (Jikasho)

**Stage 1: Brand Extraction**
- M01: ✓ Brand entities: Jikasho, Jikaso...
- M01a: ✓ M01b: ✓ M03: ✓

**Stage 3: Product Analysis**
- M06: ✓ Taxonomy: Car Phone Holders & Mounts

**Keyword Classifications (145 total)**
| OB | CB | NB | R | S | C | N |
|---:|---:|---:|---:|---:|---:|---:|
| 3 | 18 | 103 | 10 | 2 | 4 | 4 |

---

### 8. B0BZYCJK89 - Water Bottle (Owala)

**Stage 1: Brand Extraction**
- M01: ✓ Brand entities: Owala, Owala FreeSip, FreeSip...
- M01a: ✓ M01b: ✓ M03: ✓

**Stage 3: Product Analysis**
- M06: ✓ Taxonomy: Water Bottle

**Keyword Classifications (127 total)**
| OB | CB | NB | R | S | C | N |
|---:|---:|---:|---:|---:|---:|---:|
| 18 | 31 | 56 | 12 | 1 | 2 | 0 |

**Sample Full Trace:**
- "ironflask 40 oz" → M02:- → M04:CB → M05:- → M13:Same → M14:R

---

### 9. B0BQPGJ9LQ - JBL Earbuds

**Stage 1: Brand Extraction**
- M01: ✓ Brand entities: JBL, JBL Vibe, Vibe Beam, JLB...
- M01a: ✓ M01b: ✓ M03: ✓

**Stage 3: Product Analysis**
- M06: ✓ Taxonomy: True Wireless Earbuds > Wireless Earphones > Earphones

**Keyword Classifications (120 total)**
| OB | CB | NB | R | S | C | N |
|---:|---:|---:|---:|---:|---:|---:|
| 31 | 39 | 3 | 13 | 2 | 5 | 11 |

**Notable:** Highest CB (Competitor Brand) count at 39

---

### 10. B0D6YNWLTS - Puffer Jacket (Pioneer Camp)

**Stage 1: Brand Extraction**
- M01: ✓ Brand entities: Pioneer Camp, PioneerCamp, Pionner Camp...
- M01a: ✓ M01b: ✓ M03: ✓

**Stage 3: Product Analysis**
- M06: ✓ Taxonomy: Puffer Jacket / Puffy Coat > Jacket > Men's Clothing / Apparel
- M11: ✓ Hard constraints: ['Medium (Size)']

**Keyword Classifications (92 total)**
| OB | CB | NB | R | S | C | N |
|---:|---:|---:|---:|---:|---:|---:|
| 2 | 25 | 25 | 29 | 2 | 5 | 0 |

---

## Data Flow Verification

### Pipeline Flow Diagram

```
ASIN Input
    │
    ├─── M01: Extract Own Brand Entities ────────────────┐
    ├─── M01a: Extract Brand Variations ─────────────────┤ Stage 1: Brand Extraction
    ├─── M01b: Extract Brand-Related Terms ──────────────┤ (per ASIN, once)
    └─── M03: Generate Competitor Entities ──────────────┘
              │
              ▼
    ┌─── M06: Generate Product Type Taxonomy ────────────┐
    ├─── M07: Extract Product Attributes ────────────────┤
    ├─── M08: Assign Attribute Ranks ────────────────────┤ Stage 3: Product Analysis
    ├─── M09: Identify Primary Intended Use ─────────────┤ (per ASIN, once)
    ├─── M10: Validate Primary Intended Use ─────────────┤
    └─── M11: Identify Hard Constraints ─────────────────┘
              │
              ▼
    Per Keyword:
    ┌─── M02: Classify Own Brand ───── OB? ─────► STOP (Own Brand)
    │                                   │
    │                                   ▼ No
    ├─── M04: Classify Competitor ─── CB? ─────► STOP (Competitor Brand)
    │                                   │
    │                                   ▼ No
    └─── M05: Classify Non-Branded ── NB? ─────► Continue to Relevance
                                        │
                                        ▼
    ┌─── M12: Check Hard Constraints ─ X? ─────► STOP (Excluded)
    │                                   │
    │                                   ▼ No
    ├─── M13: Check Same Type ──────── Same? ──┐
    │                                   │      │
    │                                   ▼      ▼
    │                             M14: Check ─► R (Relevant)
    │                             Primary Use   │
    │                                   │      │
    │                                   ▼      ▼
    │                                   N ◄────┘
    │
    └─── M15: Check Substitute ──────── S? ────► STOP (Substitute)
                                        │
                                        ▼ No
    └─── M16: Check Complementary ──── C? ────► STOP (Complementary)
                                        │
                                        ▼ No
                                        N (Not Relevant)
```

### Data Flow Verification Results

| Input → Output | Status | Notes |
|----------------|--------|-------|
| M01 → M02 | ✓ | Brand entities used for OB classification |
| M03 → M04 | ✓ | Competitor entities used for CB classification |
| M06 → M13 | ✓ | Taxonomy used for same type check |
| M09 → M14 | ✓ | Primary use passed to relevance check |
| M11 → M12 | ✓ | Hard constraints used for exclusion check |
| M13 → M14/M15 | ✓ | Same type determines R vs S path |
| M15 → M16 | ✓ | Non-substitutes continue to complementary check |

---

## Recommendations

1. **S (Substitute) Testing:** Use B08J8GZXKZ (Oven Mitt) - only ASIN with 11 S keywords
2. **OB Testing:** Use B077YYP739 (Transformers) - 73 OB keywords
3. **CB Testing:** Use B0BQPGJ9LQ (JBL Earbuds) - 39 CB keywords
4. **C Testing:** Use B000H3I2JG (Revlon Eyeliner) - 22 C keywords
5. **R Testing:** Use B0CJ4WZXQF (Sink Caddy) - 31 R keywords
6. **X Testing:** Need synthetic test cases - 0 X keywords in dataset

---

*Generated by trace_pipeline.py*
