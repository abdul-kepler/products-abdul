# ASIN Keyword Coverage Analysis

## Overview

This document analyzes keyword coverage across all classification types (OB, CB, R, S, C, N, X) for ASINs in the M01-M16 evaluation pipeline.

## Complete Picture - Dataset Summary

### Pipeline Coverage

| Stage | ASINs | Keywords | Description |
|-------|------:|:---------|:------------|
| M01 (Brand extraction) | **99** | - | Brand entities extracted |
| M02-M05 (Brand classification) | **12** | 1,883 | OB + CB + NB keywords |
| M06-M16 (Relevance pipeline) | **10** | 439 | R + S + C + N + X classified |
| **Full Pipeline (M01-M16)** | **10** | 2,322 | Complete end-to-end |

### Data Flow & Gaps

```
99 ASINs in M01 (Brand Extraction)
    │
    ├── 87 ASINs: Brand data only, NO keywords ❌
    │   └── Cannot be used for keyword classification testing
    │
    └── 12 ASINs: Have keywords in M02-M05
            │
            ├── 2 ASINs: Keywords but NO relevance data (M06-M16) ❌
            │   • B0C9SPJ9ZQ (66 keywords: 14 OB, 34 CB, 18 NB)
            │   • B0CVQJY9C6 (61 keywords: 14 OB, 29 CB, 18 NB)
            │
            └── 10 ASINs: FULL PIPELINE COVERAGE ✓
                └── Can trace M01 → M02 → ... → M16
```

### All 99 ASINs - Complete Status

| # | ASIN | OB | CB | NB | R | S | C | N | X | Total | M01 | M02-05 | M06-16 |
|---|------|---:|---:|---:|---:|---:|---:|---:|---:|------:|:---:|:------:|:------:|
| 1 | B0F42MT8JX | 3 | 44 | 325 | 22 | 1 | 7 | 29 | 0 | 431 | ✓ | ✓ | ✓ |
| 2 | B000H3I2JG | 3 | 27 | 336 | 15 | 1 | 22 | 15 | 0 | 419 | ✓ | ✓ | ✓ |
| 3 | B09LCKZBTW | 0 | 1 | 237 | 23 | 6 | 17 | 13 | 0 | 297 | ✓ | ✓ | ✓ |
| 4 | B08J8GZXKZ | 10 | 14 | 146 | 11 | 11 | 5 | 24 | 0 | 221 | ✓ | ✓ | ✓ |
| 5 | B0CJ4WZXQF | 6 | 6 | 122 | 32 | 0 | 5 | 8 | 0 | 179 | ✓ | ✓ | ✓ |
| 6 | B077YYP739 | 73 | 4 | 20 | 43 | 5 | 3 | 4 | 0 | 152 | ✓ | ✓ | ✓ |
| 7 | B0DSHWLXG6 | 3 | 18 | 105 | 10 | 2 | 4 | 4 | 0 | 146 | ✓ | ✓ | ✓ |
| 8 | B0BZYCJK89 | 18 | 36 | 56 | 17 | 1 | 8 | 1 | 0 | 137 | ✓ | ✓ | ✓ |
| 9 | B0BQPGJ9LQ | 31 | 39 | 17 | 16 | 2 | 5 | 11 | 0 | 121 | ✓ | ✓ | ✓ |
| 10 | B0D6YNWLTS | 2 | 25 | 29 | 29 | 2 | 5 | 0 | 0 | 92 | ✓ | ✓ | ✓ |
| 11 | B0C9SPJ9ZQ | 14 | 34 | 18 | 0 | 0 | 0 | 0 | 0 | 66 | ✓ | ✓ | ❌ |
| 12 | B0CVQJY9C6 | 14 | 29 | 18 | 0 | 0 | 0 | 0 | 0 | 61 | ✓ | ✓ | ❌ |
| 13-99 | (87 ASINs) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | ✓ | ❌ | ❌ |
| **TOTAL** | **99** | **177** | **277** | **1,429** | **218** | **31** | **81** | **109** | **0** | **2,322** | **99** | **12** | **10** |

### Keyword Totals by Classification

| Category | Total Keywords | % of Total |
|----------|---------------:|-----------:|
| NB (Non-Branded) | 1,429 | 61.5% |
| CB (Competitor Brand) | 277 | 11.9% |
| R (Relevant) | 218 | 9.4% |
| OB (Own Brand) | 177 | 7.6% |
| N (Not Relevant) | 109 | 4.7% |
| C (Complementary) | 81 | 3.5% |
| S (Substitute) | 31 | 1.3% |
| X (Excluded) | 0 | 0.0% |
| **TOTAL** | **2,322** | **100%** |

---

## Classification Types

| Code | Name | Description | Module |
|------|------|-------------|--------|
| OB | Own Brand | Keyword contains own brand | M02 |
| CB | Competitor Brand | Keyword contains competitor brand | M04 |
| NB | Non-Branded | No brand in keyword | M05 |
| R | Relevant | Same type, same use | M14 |
| S | Substitute | Different type, same use | M15 |
| C | Complementary | Different type, used together | M16 |
| N | Not Relevant | No relationship | M14/M16 |
| X | Excluded | Violates hard constraint | M12 |

## Best 10 ASINs (Ranked by Coverage Balance)

| Rank | ASIN | Product | OB | CB | R | S | C | N | X | Score |
|------|------|---------|----|----|---|---|---|---|---|-------|
| 1 | B08J8GZXKZ | Oven Mitt | 10 | 14 | 11 | **11** | 5 | 24 | 0 | 55 |
| 2 | B0BQPGJ9LQ | JBL Earbuds | 31 | 39 | 16 | 2 | 5 | 11 | 0 | 47 |
| 3 | B000H3I2JG | Revlon Eyeliner | 3 | 27 | 15 | 1 | **22** | 15 | 0 | 44 |
| 4 | B0F42MT8JX | Ice Maker | 3 | 44 | 22 | 1 | 7 | **29** | 0 | 41 |
| 5 | B0BZYCJK89 | Owala Water Bottle | 18 | 36 | 17 | 1 | 8 | 1 | 0 | 40 |
| 6 | B09LCKZBTW | Serving Tray | 0 | 1 | 23 | 6 | **17** | 13 | 0 | 37 |
| 7 | B077YYP739 | Transformers Toy | **73** | 4 | **43** | 5 | 3 | 4 | 0 | 36 |
| 8 | B0CJ4WZXQF | Sink Caddy | 6 | 6 | **32** | 0 | 5 | 8 | 0 | 35 |
| 9 | B0DSHWLXG6 | Phone Holder | 3 | 18 | 10 | 2 | 4 | 4 | 0 | 33 |
| 10 | B0D6YNWLTS | Puffer Jacket | 2 | 25 | **29** | 2 | 5 | 0 | 0 | 29 |

### Scoring Methodology

Score = min(OB,10) + min(CB,10) + min(R,10) + min(S,10) + min(C,10) + min(N,10) + min(X,10)

This rewards having at least 10 keywords of each type (max score = 70).

## Selection Analysis

**Best overall:** `B08J8GZXKZ` (Oven Mitt) - Only ASIN with 10+ in 5 categories including **S (Substitute)**

### Coverage Strengths

| Classification | ASINs with 10+ | Status |
|----------------|----------------|--------|
| R (Relevant) | 10/10 | ✅ Good |
| CB (Competitor) | 8/10 | ✅ Good |
| N (Not Relevant) | 5/10 | ⚠️ Partial |
| C (Complementary) | 3/10 | ⚠️ Partial |
| OB (Own Brand) | 3/10 | ⚠️ Partial |
| S (Substitute) | 1/10 | ⚠️ Sparse |
| X (Excluded) | 0/10 | ❌ None |

### Coverage Gaps

1. **X (Excluded):** Zero keywords across all ASINs - No hard constraint violations in dataset
2. **S (Substitute):** Very sparse - only B08J8GZXKZ has 10+ keywords
3. **OB (Own Brand):** Uneven distribution - some ASINs have only 2-3

## Detailed Coverage Per ASIN

### 1. B08J8GZXKZ - Oven Mitt (Score: 55)
- **Best for:** S (Substitute) testing - only ASIN with 11 S keywords
- **Strengths:** Balanced coverage across OB, CB, R, S, N
- **Gaps:** C (only 5), X (0)

### 2. B0BQPGJ9LQ - JBL Earbuds (Score: 47)
- **Best for:** OB and CB testing
- **Strengths:** High OB (31), high CB (39)
- **Gaps:** S (only 2), X (0)

### 3. B000H3I2JG - Revlon Eyeliner (Score: 44)
- **Best for:** C (Complementary) testing - highest C count (22)
- **Strengths:** Good CB (27), balanced R/N
- **Gaps:** OB (only 3), S (only 1), X (0)

### 4. B0F42MT8JX - Ice Maker (Score: 41)
- **Best for:** N (Not Relevant) testing - highest N count (29)
- **Strengths:** High CB (44), good R (22)
- **Gaps:** OB (only 3), S (only 1), X (0)

### 5. B0BZYCJK89 - Owala Water Bottle (Score: 40)
- **Best for:** Brand classification (OB/CB)
- **Strengths:** Good OB (18), high CB (36)
- **Gaps:** N (only 1), S (only 1), X (0)

### 6. B09LCKZBTW - Serving Tray (Score: 37)
- **Best for:** C (Complementary) testing
- **Strengths:** High C (17), balanced R/N/S
- **Gaps:** OB (0), CB (only 1), X (0)

### 7. B077YYP739 - Transformers Toy (Score: 36)
- **Best for:** OB and R testing
- **Strengths:** Highest OB (73), highest R (43)
- **Gaps:** CB (only 4), C (only 3), X (0)

### 8. B0CJ4WZXQF - Sink Caddy (Score: 35)
- **Best for:** R (Relevant) testing
- **Strengths:** High R (32)
- **Gaps:** OB (6), CB (6), S (0), X (0)

### 9. B0DSHWLXG6 - Phone Holder (Score: 33)
- **Best for:** General balanced testing
- **Strengths:** Has all types except X
- **Gaps:** Low counts across most types, X (0)

### 10. B0D6YNWLTS - Puffer Jacket (Score: 29)
- **Best for:** R (Relevant) testing
- **Strengths:** High R (29), good CB (25)
- **Gaps:** OB (only 2), N (0), X (0)

## Recommendations

1. **Primary test case:** Use `B08J8GZXKZ` (Oven Mitt) for comprehensive testing - best balanced coverage
2. **S classification testing:** Focus on `B08J8GZXKZ` - only ASIN with sufficient S keywords
3. **X classification:** Cannot test - need to generate synthetic test cases with hard constraint violations
4. **Full pipeline trace:** All 10 ASINs can be traced through M01-M16

## Pipeline Flow

```
ASIN + Keywords
      │
      ├── M01 → M01a → M01b: Extract brand info (once per ASIN)
      ├── M03: Generate competitors (once per ASIN)
      ├── M06 → M07 → M08 → M09 → M10 → M11: Product analysis (once per ASIN)
      │
      └── Per Keyword:
          ├── M02: Check OB → stops if OB
          ├── M04: Check CB → stops if CB
          ├── M05: Check NB → continues if NB
          │
          └── If NB:
              ├── M12: Check X → stops if X
              ├── M13: Check same type
              │   ├── M14: Same type → R or N
              │   └── M15: Different type → S or continue
              │       └── M16: Complementary → C or N
              │
              └── M12b: Combined classification (alternative single-step)
```

---
*Generated: 2026-01-14*
