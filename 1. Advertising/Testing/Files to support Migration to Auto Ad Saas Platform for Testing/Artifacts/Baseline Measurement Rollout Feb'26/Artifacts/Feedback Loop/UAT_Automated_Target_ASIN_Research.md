# UAT Checklist: Automated Target ASIN Research

**Feature:** Automated Target ASIN Research (PROD-1114 Epic)
**Version:** 1.0
**Last Updated:** January 2026
**Related Tickets:** PROD-297, PROD-300, PROD-761, PROD-762, PROD-765, PROD-303, PROD-357

---

## Logic Overview

### Purpose
Automatically identify and qualify competitor ASINs for ASIN Targeting campaigns by:
1. Triggering research based on ASIN performance thresholds
2. Analyzing top-performing search terms
3. Scraping competitor ASINs from Amazon SERP
4. Enriching ASIN data with competitive attributes
5. Qualifying ASINs against our products
6. Grouping qualified ASINs by brand for campaign creation

### End-to-End Process Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AUTOMATED TARGET ASIN RESEARCH FLOW                       │
└─────────────────────────────────────────────────────────────────────────────┘

Step 1: TRIGGER EVALUATION (PROD-297)
┌─────────────────────────────────────────────────────────────────────────────┐
│  Trigger #1: ASIN ENABLED for first time via ASIN Config                    │
│  Trigger #2: Every 14 days (automatic)                                      │
│                                                                             │
│  Condition:                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  IF (ASIN_Ad_Spend_15d > $100 AND ASIN_Ad_Orders_15d > 5)           │   │
│  │      → Trigger ASIN Research Process                                │   │
│  │  ELSE                                                               │   │
│  │      → Skip and recheck after 15 days                               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Scope: All ASINs where ASIN Targeting campaigns exist                      │
│         AND ASIN Status = ENABLED                                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
Step 2: SEARCH TERM FILTERING (PROD-300)
┌─────────────────────────────────────────────────────────────────────────────┐
│  Input: All search terms with ad spend data (last 14 days)                  │
│                                                                             │
│  Filtering Logic:                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  1. Filter search terms accounting for ≥50% of total ad spend       │   │
│  │  2. Only include terms with valid CVR and impressions data          │   │
│  │  3. Exclude search terms that are ASINs (Search Term ≠ ASIN)        │   │
│  │  4. Rank remaining terms by CVR (descending)                        │   │
│  │  5. Select TOP 5 search terms                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Output: [SearchTerm, Spend, CVR, Clicks, Orders] × 5                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
Step 3: SERP SCRAPING (PROD-761)
┌─────────────────────────────────────────────────────────────────────────────┐
│  For each of 5 search terms:                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  URL: https://www.amazon.com/s?k=<encoded_search_term>              │   │
│  │  Target: Page 1 only (~45-50 listings)                              │   │
│  │                                                                     │   │
│  │  Data Extracted per ASIN:                                           │   │
│  │  • ASIN (data-asin)        • Title                                  │   │
│  │  • Product URL             • Image URL                              │   │
│  │  • Sponsored Flag          • Position Index (1-50)                  │   │
│  │  • Search Term             • Timestamp                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Processing:                                                                │
│  • Deduplicate within same run                                              │
│  • New ASINs → Insert into DB                                               │
│  • Existing ASINs → Retain (no deletion/overwrite)                          │
│                                                                             │
│  Storage: target_asin_raw                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
Step 4: ATTRIBUTE ENRICHMENT (PROD-762)
┌─────────────────────────────────────────────────────────────────────────────┐
│  For each ASIN in target_asin_raw:                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Source: https://www.amazon.com/dp/<ASIN>                           │   │
│  │                                                                     │   │
│  │  Price Fallback Hierarchy:                                          │   │
│  │  Buy Box Price → FBA Price → FBM Price → BB_30d avg → FBA_30d avg   │   │
│  │                                                                     │   │
│  │  Attributes Collected:                                              │   │
│  │  • Price               • Rating                                     │   │
│  │  • Review Count        • Fulfillment Type (FBA/FBM)                 │   │
│  │  • Brand Name          • Price per Unit (if available)              │   │
│  │  • Timestamp           • Marketplace                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Storage: target_asin_enriched                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
Step 5: DEDUPLICATION & MASTER STORAGE (PROD-765)
┌─────────────────────────────────────────────────────────────────────────────┐
│  Processing:                                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  1. Deduplicate within batch by (ASIN, marketplace)                 │   │
│  │  2. Compare against target_asin_master                              │   │
│  │  3. INSERT new ASINs (qualification_status = "Pending")             │   │
│  │  4. RETAIN all existing ASINs (no deletion/overwrite)               │   │
│  │  5. APPEND new rows for reappearing ASINs (preserve history)        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Storage: target_asin_master (append-only audit trail)                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
Step 6: ASIN QUALIFICATION (PROD-303)
┌─────────────────────────────────────────────────────────────────────────────┐
│  Compare Our ASIN vs Each Competitor (Target) ASIN                          │
│                                                                             │
│  ┌───────────────────────── QUALIFIED LEVEL 1 ─────────────────────────┐   │
│  │  (Strict Criteria - Strong Competitive Position)                    │   │
│  │                                                                     │   │
│  │  Our.PricePerUOM <= Competitor.PricePerUOM                          │   │
│  │  AND                                                                │   │
│  │  (Our.Rating > 4 OR                                                 │   │
│  │   (Our.Rating > Competitor.Rating - 0.5                             │   │
│  │    AND FirstDigit(Our.Rating) == FirstDigit(Competitor.Rating)))    │   │
│  │  AND                                                                │   │
│  │  ((Our.Reviews < 1000 AND Competitor.Reviews > 1000                 │   │
│  │    AND Our.Reviews >= 0.1 × Competitor.Reviews)                     │   │
│  │   OR (Our.Reviews < 1000 AND Competitor.Reviews < 1000)             │   │
│  │   OR (Our.Reviews > 1000))                                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌───────────────────────── QUALIFIED LEVEL 2 ─────────────────────────┐   │
│  │  (Relaxed Criteria - Acceptable Competitive Position)               │   │
│  │                                                                     │   │
│  │  Our.PricePerUOM <= 1.1 × Competitor.PricePerUOM                    │   │
│  │  AND                                                                │   │
│  │  (Our.Rating >= 4 OR Our.Rating >= Competitor.Rating - 0.3)         │   │
│  │  AND                                                                │   │
│  │  ((Our.Reviews > 100 AND Our.Reviews >= 0.1 × Competitor.Reviews)   │   │
│  │   OR (Our.Reviews < 100 AND Competitor.Reviews <= 500))             │   │
│  │  AND                                                                │   │
│  │  (Our.FulfillmentType == "FBA" OR                                   │   │
│  │   (Our.FulfillmentType == "FBM" AND Competitor.FulfillmentType == "FBM"))│
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  NOT QUALIFIED: Does not meet Level 1 or Level 2 criteria                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
Step 7: GROUP BY BRAND (PROD-357)
┌─────────────────────────────────────────────────────────────────────────────┐
│  Input: Qualified ASINs (qualification_status = "Qualified")                │
│                                                                             │
│  Processing:                                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  1. Group all qualified ASINs by brand_name                         │   │
│  │  2. Each brand group = one campaign entity                          │   │
│  │  3. If new ASIN qualifies for existing brand → append to group      │   │
│  │  4. Exclude ASINs with missing brand names                          │   │
│  │  5. Remove duplicates within same brand group                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Output Structure:                                                          │
│  • brand_name                                                               │
│  • asin_list (array of ASINs)                                               │
│  • asin_count                                                               │
│  • group_creation_date                                                      │
│                                                                             │
│  Storage: asin_target_groups                                                │
│                                                                             │
│  → Feeds into Automated Campaign Creation (PROD-356)                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Data Tables

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `target_asin_raw` | Raw SERP scrape data | ASIN, Title, URL, Position, Sponsored, Search Term |
| `target_asin_enriched` | Enriched ASIN attributes | ASIN, Price, Rating, Reviews, Fulfillment, Brand |
| `target_asin_master` | Master ASIN repository | ASIN, All attributes, Qualification Status/Level |
| `asin_target_groups` | Brand-grouped ASINs | Brand Name, ASIN List, Count, Creation Date |

### Qualification Decision Matrix

| Our Reviews | Competitor Reviews | Level 1 | Level 2 |
|-------------|-------------------|---------|---------|
| < 1000 | > 1000 | Ours >= 10% of theirs | N/A |
| < 1000 | < 1000 | Always eligible | N/A |
| > 1000 | Any | Always eligible | N/A |
| > 100 | Any | N/A | Ours >= 10% of theirs |
| < 100 | <= 500 | N/A | Always eligible |

---

## Test Summary

| Section | Type 1 (Verification) | Type 2 (Validation) | Total |
|---------|----------------------|---------------------|-------|
| 1. Trigger Evaluation | 15 | 8 | 23 |
| 2. Search Term Filtering | 18 | 10 | 28 |
| 3. SERP Scraping | 20 | 12 | 32 |
| 4. Attribute Enrichment | 18 | 10 | 28 |
| 5. Deduplication & Storage | 15 | 8 | 23 |
| 6. ASIN Qualification | 25 | 15 | 40 |
| 7. Brand Grouping | 12 | 8 | 20 |
| 8. UI & Monitoring | 8 | 6 | 14 |
| **TOTAL** | **131** | **77** | **208** |

---

## Section 1: Trigger Evaluation (PROD-297)

### Type 1: Verification Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 1.1.1 | Enable ASIN for first time via ASIN Config | Research process triggers immediately | |
| 1.1.2 | ASIN with Ad_Spend_15d = $101, Ad_Orders_15d = 6 | Research process triggers | |
| 1.1.3 | ASIN with Ad_Spend_15d = $100 (exactly), Ad_Orders_15d = 6 | Research does NOT trigger | |
| 1.1.4 | ASIN with Ad_Spend_15d = $150, Ad_Orders_15d = 5 (exactly) | Research does NOT trigger | |
| 1.1.5 | ASIN with Ad_Spend_15d = $50, Ad_Orders_15d = 10 | Research does NOT trigger (spend too low) | |
| 1.1.6 | ASIN with Ad_Spend_15d = $200, Ad_Orders_15d = 2 | Research does NOT trigger (orders too low) | |
| 1.1.7 | ASIN Status = DISABLED with qualifying metrics | Research does NOT trigger | |
| 1.1.8 | ASIN with no ASIN Targeting campaigns | Research does NOT trigger | |
| 1.1.9 | Verify 14-day automatic trigger cycle | System runs every 14 days exactly | |
| 1.1.10 | ASIN fails condition, verify recheck after 15 days | System rechecks at correct interval | |
| 1.1.11 | Multiple ASINs qualify simultaneously | All qualifying ASINs process | |
| 1.1.12 | ASIN Targeting campaign DISABLED, ASIN ENABLED | Research still triggers | |
| 1.1.13 | Verify trigger timestamp logging | All trigger events logged correctly | |
| 1.1.14 | Verify evaluation timestamp logging | All evaluations logged | |
| 1.1.15 | ASIN re-enabled after being disabled | Triggers on re-enable | |

### Type 2: Validation Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 1.2.1 | Boundary: Ad_Spend_15d = $100.01 | Research triggers | |
| 1.2.2 | Boundary: Ad_Orders_15d = 5.1 (if decimals allowed) | Verify expected behavior | |
| 1.2.3 | Multiple marketplaces with same ASIN | Each marketplace evaluated independently | |
| 1.2.4 | Large account with 500+ ASINs | All ASINs evaluated within timeout | |
| 1.2.5 | Concurrent trigger evaluations | No race conditions | |
| 1.2.6 | Trigger during high system load | Process completes successfully | |
| 1.2.7 | Network timeout during evaluation | Graceful retry/error handling | |
| 1.2.8 | Verify no duplicate triggers | Same ASIN not triggered twice in same cycle | |

---

## Section 2: Search Term Filtering (PROD-300)

### Type 1: Verification Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 2.1.1 | Fetch search terms from last 14 days | Only 14-day data retrieved | |
| 2.1.2 | Search terms totaling 50% of spend | Included in filter set | |
| 2.1.3 | Search terms totaling 49% of spend | NOT included in filter set | |
| 2.1.4 | Search term with valid CVR and impressions | Included for ranking | |
| 2.1.5 | Search term with CVR = 0 | Excluded from selection | |
| 2.1.6 | Search term with impressions = 0 | Excluded from selection | |
| 2.1.7 | Search term that IS an ASIN (e.g., B0ABC12345) | Excluded from selection | |
| 2.1.8 | Rank remaining terms by CVR descending | Correct order verified | |
| 2.1.9 | Select exactly top 5 search terms | Only 5 selected regardless of ties | |
| 2.1.10 | Verify output includes SearchTerm field | Field present | |
| 2.1.11 | Verify output includes Spend field | Field present | |
| 2.1.12 | Verify output includes CVR field | Field present | |
| 2.1.13 | Verify output includes Clicks field | Field present | |
| 2.1.14 | Verify output includes Orders field | Field present | |
| 2.1.15 | Only 3 search terms qualify | System processes 3 (not error) | |
| 2.1.16 | No search terms qualify (all < 50% spend) | System handles gracefully | |
| 2.1.17 | Persist filtered dataset to database | Data stored correctly | |
| 2.1.18 | Multiple ASINs share same search terms | Correct association maintained | |

### Type 2: Validation Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 2.2.1 | Boundary: Search term at exactly 50% cumulative spend | Included in filter | |
| 2.2.2 | CVR calculation accuracy (Orders/Clicks) | Correct to 4 decimal places | |
| 2.2.3 | Tie-breaker: Two terms with identical CVR | Deterministic selection (e.g., alphabetical) | |
| 2.2.4 | Large dataset: 10,000 search terms | Filtering completes in < 30 seconds | |
| 2.2.5 | Search term with special characters | Handled correctly | |
| 2.2.6 | Search term with non-ASCII characters | Handled correctly | |
| 2.2.7 | Data consistency across reruns | Same input produces same output | |
| 2.2.8 | Requalified search term from previous run | Re-processed correctly | |
| 2.2.9 | Historical data overlap handling | No duplicate processing | |
| 2.2.10 | Schema validation on output | Matches expected format | |

---

## Section 3: SERP Scraping (PROD-761)

### Type 1: Verification Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 3.1.1 | Scrape SERP Page 1 for valid search term | Returns ~45-50 ASINs | |
| 3.1.2 | Verify ASIN field extracted (data-asin) | Valid ASIN format | |
| 3.1.3 | Verify Title field extracted | Non-empty string | |
| 3.1.4 | Verify Product URL format | amazon.com/dp/<ASIN> | |
| 3.1.5 | Verify Image URL extracted | Valid URL format | |
| 3.1.6 | Verify Sponsored Flag (true/false) | Boolean value | |
| 3.1.7 | Verify Position Index (1-50) | Integer in range | |
| 3.1.8 | Verify Search Term stored | Matches input term | |
| 3.1.9 | Verify Timestamp stored | Current datetime | |
| 3.1.10 | Deduplicate ASINs within same run | No duplicates in output | |
| 3.1.11 | New ASIN not in database | Inserted successfully | |
| 3.1.12 | Existing ASIN in database | Retained, not overwritten | |
| 3.1.13 | Process all 5 search terms | 5 SERP pages scraped | |
| 3.1.14 | Combine ASINs from all terms | Single unified list | |
| 3.1.15 | Store in target_asin_raw table | Data persisted correctly | |
| 3.1.16 | Requalified term rescraping | Fresh data fetched | |
| 3.1.17 | Log success per search term | Success logged | |
| 3.1.18 | Log failure per search term | Failure logged with details | |
| 3.1.19 | Marketplace = amazon.com | Correct marketplace captured | |
| 3.1.20 | JSON schema validation passes | Output matches expected schema | |

### Type 2: Validation Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 3.2.1 | Search term with < 45 results | All available ASINs returned | |
| 3.2.2 | Search term with 0 results | Graceful handling, empty set | |
| 3.2.3 | Scraper timeout (network issue) | Retry mechanism triggered | |
| 3.2.4 | Retry success after initial failure | ASIN data captured on retry | |
| 3.2.5 | All 2 retries fail | Error logged, continue to next term | |
| 3.2.6 | Sponsored-only results page | Sponsored flag correctly marked | |
| 3.2.7 | Mixed sponsored/organic results | Both types captured correctly | |
| 3.2.8 | Special characters in product title | Title stored correctly | |
| 3.2.9 | Very long product title | Truncated appropriately | |
| 3.2.10 | ASIN appears in multiple search terms | Stored once with all source terms | |
| 3.2.11 | Performance: 5 terms × 50 ASINs | Completes in < 60 seconds | |
| 3.2.12 | Historical record maintained | Previous scrape data retained | |

---

## Section 4: Attribute Enrichment (PROD-762)

### Type 1: Verification Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 4.1.1 | Fetch product detail page for ASIN | Page retrieved successfully | |
| 4.1.2 | Extract Buy Box Price | Correct price value | |
| 4.1.3 | Buy Box unavailable, fallback to FBA Price | FBA price used | |
| 4.1.4 | FBA unavailable, fallback to FBM Price | FBM price used | |
| 4.1.5 | All prices unavailable, use 30-day averages | Average price used | |
| 4.1.6 | Extract Rating (e.g., 4.5) | Correct decimal value | |
| 4.1.7 | Extract Review Count | Correct integer | |
| 4.1.8 | Determine Fulfillment Type = FBA | Correct when Prime/FBA | |
| 4.1.9 | Determine Fulfillment Type = FBM | Correct when not FBA | |
| 4.1.10 | Extract Brand Name | Correct brand string | |
| 4.1.11 | Extract Price per Unit (when available) | Correct calculation | |
| 4.1.12 | Store Timestamp | Current datetime stored | |
| 4.1.13 | Store Marketplace | amazon.com stored | |
| 4.1.14 | All attributes written to target_asin_enriched | Data persisted correctly | |
| 4.1.15 | Existing ASIN re-enriched | New row appended (not overwritten) | |
| 4.1.16 | Null values handled | No errors, null stored | |
| 4.1.17 | Failure rate ≤ 1% | Logged and retried | |
| 4.1.18 | Schema validation passes | All records pass | |

### Type 2: Validation Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 4.2.1 | Price with currency symbols | Parsed correctly ($25.99 → 25.99) | |
| 4.2.2 | Price with comma separator ($1,234.56) | Parsed correctly | |
| 4.2.3 | Rating = 0 (no ratings) | Stored as 0 or null | |
| 4.2.4 | Review Count > 100,000 | Large numbers handled | |
| 4.2.5 | Brand Name with special characters | Stored correctly | |
| 4.2.6 | Multi-unit product (Price per Unit) | Unit price calculated correctly | |
| 4.2.7 | Item Package Quantity extraction | Correctly extracted | |
| 4.2.8 | Historical trend preservation | Multiple snapshots over time | |
| 4.2.9 | Large batch (500+ ASINs) | Completes within timeout | |
| 4.2.10 | Product page unavailable (404) | Error logged, ASIN skipped | |

---

## Section 5: Deduplication & Master Storage (PROD-765)

### Type 1: Verification Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 5.1.1 | Duplicate ASIN within same batch | Stored only once | |
| 5.1.2 | Unique key = (ASIN, marketplace) | Dedup by this key | |
| 5.1.3 | New ASIN not in target_asin_master | Inserted with status "Pending" | |
| 5.1.4 | Existing ASIN in master table | Retained, not deleted | |
| 5.1.5 | Reappearing ASIN with updated data | New row appended | |
| 5.1.6 | qualification_status default = "Pending" | Set correctly | |
| 5.1.7 | qualification_level default = NULL | Set correctly | |
| 5.1.8 | Append-only audit trail maintained | No deletions ever | |
| 5.1.9 | All enriched fields transferred | Price, Rating, Reviews, etc. | |
| 5.1.10 | Source Search Term preserved | Correct term stored | |
| 5.1.11 | Timestamp on insertion | Correct datetime | |
| 5.1.12 | Log: total ASINs processed | Correct count | |
| 5.1.13 | Log: new ASINs inserted | Correct count | |
| 5.1.14 | Log: duplicates skipped | Correct count | |
| 5.1.15 | Schema validation on master table | All records valid | |

### Type 2: Validation Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 5.2.1 | Batch of 200 ASINs, 50 existing | 150 inserted, 50 skipped | |
| 5.2.2 | Transaction integrity on failure | Rollback partial inserts | |
| 5.2.3 | Concurrent writes to master table | No data corruption | |
| 5.2.4 | Index performance on (ASIN, marketplace) | Fast lookup verified | |
| 5.2.5 | Historical querying efficiency | Query returns in < 5 seconds | |
| 5.2.6 | Data ready for qualification logic | Correct format for downstream | |
| 5.2.7 | Edge: All ASINs are duplicates | Log shows 0 new, all skipped | |
| 5.2.8 | Edge: Empty batch input | No errors, log shows 0 processed | |

---

## Section 6: ASIN Qualification (PROD-303)

### Type 1: Verification Tests - Level 1 Qualification

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 6.1.1 | Our.PricePerUOM < Competitor.PricePerUOM | Price condition met | |
| 6.1.2 | Our.PricePerUOM = Competitor.PricePerUOM | Price condition met | |
| 6.1.3 | Our.PricePerUOM > Competitor.PricePerUOM | Price condition NOT met | |
| 6.1.4 | Our.Rating = 4.5 (> 4) | Rating condition met | |
| 6.1.5 | Our.Rating = 4.0, Competitor.Rating = 4.3 | Rating condition met (same first digit, diff < 0.5) | |
| 6.1.6 | Our.Rating = 3.9, Competitor.Rating = 4.3 | Rating condition NOT met (different first digit) | |
| 6.1.7 | Our.Rating = 4.1, Competitor.Rating = 4.7 | Rating condition NOT met (diff > 0.5) | |
| 6.1.8 | Our.Reviews = 500, Competitor.Reviews = 1500 | Review condition met (≥ 10% of 1500) | |
| 6.1.9 | Our.Reviews = 50, Competitor.Reviews = 1500 | Review condition NOT met (< 10% of 1500) | |
| 6.1.10 | Our.Reviews = 800, Competitor.Reviews = 800 | Review condition met (both < 1000) | |
| 6.1.11 | Our.Reviews = 1500 | Review condition met (> 1000) | |
| 6.1.12 | All Level 1 conditions met | Qualification_Level = "Qualified_Level1" | |
| 6.1.13 | Qualification_Status = "Qualified" | Status set correctly | |

### Type 1: Verification Tests - Level 2 Qualification

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 6.1.14 | Our.PricePerUOM = 1.05 × Competitor.PricePerUOM | Price condition met (≤ 1.1×) | |
| 6.1.15 | Our.PricePerUOM = 1.1 × Competitor.PricePerUOM | Price condition met (exactly 1.1×) | |
| 6.1.16 | Our.PricePerUOM = 1.15 × Competitor.PricePerUOM | Price condition NOT met | |
| 6.1.17 | Our.Rating = 4.0 | Rating condition met (≥ 4) | |
| 6.1.18 | Our.Rating = 3.8, Competitor.Rating = 4.0 | Rating condition met (≥ 4.0 - 0.3) | |
| 6.1.19 | Our.Rating = 3.5, Competitor.Rating = 4.0 | Rating condition NOT met | |
| 6.1.20 | Our.Reviews = 150, Competitor.Reviews = 1000 | Review condition met (≥ 10% of 1000) | |
| 6.1.21 | Our.Reviews = 50, Competitor.Reviews = 400 | Review condition met (< 100 and comp ≤ 500) | |
| 6.1.22 | Our.Reviews = 50, Competitor.Reviews = 600 | Review condition NOT met | |
| 6.1.23 | Our.FulfillmentType = FBA | Fulfillment condition met | |
| 6.1.24 | Our.FulfillmentType = FBM, Competitor.FulfillmentType = FBM | Fulfillment condition met | |
| 6.1.25 | Our.FulfillmentType = FBM, Competitor.FulfillmentType = FBA | Fulfillment condition NOT met | |
| 6.1.26 | All Level 2 conditions met (not Level 1) | Qualification_Level = "Qualified_Level2" | |

### Type 1: Verification Tests - Not Qualified

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 6.1.27 | Fails Level 1 and Level 2 price | Qualification_Status = "Not Qualified" | |
| 6.1.28 | Fails Level 1 and Level 2 rating | Qualification_Status = "Not Qualified" | |
| 6.1.29 | Fails Level 1 and Level 2 reviews | Qualification_Status = "Not Qualified" | |
| 6.1.30 | Qualified ASIN stored with correct fields | ASIN, status, date, source term, attributes | |

### Type 2: Validation Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 6.2.1 | Boundary: Our.PricePerUOM = Competitor × 1.1001 | NOT qualified Level 2 | |
| 6.2.2 | Boundary: Our.Rating = 3.99 | NOT qualified via rating > 4 rule | |
| 6.2.3 | Boundary: Our.Reviews = 99 vs Competitor.Reviews = 501 | NOT qualified Level 2 | |
| 6.2.4 | FirstDigit function: Rating 4.9 vs 4.1 | Same first digit (4) | |
| 6.2.5 | FirstDigit function: Rating 3.9 vs 4.1 | Different first digit (3 vs 4) | |
| 6.2.6 | Large batch: 500 ASINs qualification | Completes in < 30 seconds | |
| 6.2.7 | Requalification of previously stored ASINs | All backend ASINs evaluated | |
| 6.2.8 | Mixed qualification results | Correct distribution of L1/L2/Not | |
| 6.2.9 | Null attribute handling | Graceful error, marked not qualified | |
| 6.2.10 | Price per Unit calculation accuracy | Correct to 2 decimal places | |
| 6.2.11 | Qualification date timestamp | Correct datetime stored | |
| 6.2.12 | Source search term preserved | Correct term in output | |
| 6.2.13 | Multiple Our ASINs vs same Competitor | Each pairing evaluated independently | |
| 6.2.14 | Same Competitor ASIN qualifies for multiple Our ASINs | Stored correctly for each | |
| 6.2.15 | Audit trail of qualification changes | History preserved | |

---

## Section 7: Brand Grouping (PROD-357)

### Type 1: Verification Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 7.1.1 | Group qualified ASINs by brand_name | Correct groupings created | |
| 7.1.2 | 50 ASINs across 10 brands | 10 brand groups created | |
| 7.1.3 | New ASIN for existing brand | Appended to existing group | |
| 7.1.4 | asin_count updated on append | Correct count | |
| 7.1.5 | group_creation_date set on new group | Correct datetime | |
| 7.1.6 | ASIN with missing brand_name | Excluded from grouping | |
| 7.1.7 | Duplicate ASIN within same brand | Stored only once | |
| 7.1.8 | Verify brand_name field stored | Correct string | |
| 7.1.9 | Verify asin_list field stored | Array of ASINs | |
| 7.1.10 | Verify asin_count field stored | Correct integer | |
| 7.1.11 | Data stored in asin_target_groups table | Persisted correctly | |
| 7.1.12 | Execute immediately after qualification | Correct sequence | |

### Type 2: Validation Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 7.2.1 | Brand name with special characters | Group created correctly | |
| 7.2.2 | Brand name with unicode characters | Handled correctly | |
| 7.2.3 | Large brand group (200+ ASINs) | All ASINs included | |
| 7.2.4 | Many small brand groups (100 brands, 1 ASIN each) | All groups created | |
| 7.2.5 | last_updated field on modification | Timestamp updated | |
| 7.2.6 | Concurrent group modifications | No data corruption | |
| 7.2.7 | Log: groups created/modified | Correct counts | |
| 7.2.8 | Output ready for Campaign Creation (PROD-356) | Correct format verified | |

---

## Section 8: UI & Monitoring

### Type 1: Verification Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 8.1.1 | View qualified ASINs in UI | List displays correctly | |
| 8.1.2 | Filter by qualification level (L1/L2) | Filter works | |
| 8.1.3 | Filter by brand name | Filter works | |
| 8.1.4 | View trigger history/logs | Timestamps visible | |
| 8.1.5 | View research process status | Current status shown | |
| 8.1.6 | Error notifications displayed | Alerts shown for failures | |
| 8.1.7 | Manual trigger option (if available) | Triggers process | |
| 8.1.8 | Export qualified ASINs | CSV/Excel export works | |

### Type 2: Validation Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 8.2.1 | UI performance with 1000+ ASINs | Page loads in < 3 seconds | |
| 8.2.2 | Pagination handling | Correct page navigation | |
| 8.2.3 | Sort by any column | Sorting works correctly | |
| 8.2.4 | Real-time status updates | UI refreshes automatically | |
| 8.2.5 | Mobile responsiveness (if applicable) | Layout adapts | |
| 8.2.6 | Error message clarity | User-friendly messages | |

---

## Regression Test Suite

### Critical Path Tests (Run on Every Release)

| # | Test Case | Priority |
|---|-----------|----------|
| R1 | End-to-end: ASIN enabled → Research triggered → ASINs qualified | P0 |
| R2 | Trigger threshold: Spend > $100 AND Orders > 5 | P0 |
| R3 | Search term filtering: Top 5 by CVR, 50% spend threshold | P0 |
| R4 | SERP scraping returns valid ASINs | P0 |
| R5 | Attribute enrichment populates all required fields | P0 |
| R6 | Level 1 qualification logic accuracy | P0 |
| R7 | Level 2 qualification logic accuracy | P0 |
| R8 | Brand grouping creates correct campaign units | P0 |
| R9 | Data persistence across all tables | P0 |
| R10 | No data loss on rerun/requalification | P0 |

---

## Test Data Requirements

### Required Test ASINs

| Our ASIN | Price | Rating | Reviews | Fulfillment | Purpose |
|----------|-------|--------|---------|-------------|---------|
| TEST001 | $25.00 | 4.5 | 1500 | FBA | Level 1 qualification (strong) |
| TEST002 | $30.00 | 4.2 | 200 | FBA | Level 2 qualification (relaxed) |
| TEST003 | $35.00 | 3.5 | 50 | FBM | Not qualified (fails rating) |
| TEST004 | $20.00 | 4.8 | 80 | FBA | Level 2 edge case (reviews) |
| TEST005 | $40.00 | 4.0 | 500 | FBM | Fulfillment type testing |

### Required Competitor ASINs

| ASIN | Brand | Price | Rating | Reviews | Fulfillment | Purpose |
|------|-------|-------|--------|---------|-------------|---------|
| COMP001 | BrandA | $25.00 | 4.3 | 1200 | FBA | Standard competitor |
| COMP002 | BrandA | $28.00 | 4.1 | 800 | FBM | Same brand, different profile |
| COMP003 | BrandB | $22.00 | 4.6 | 2500 | FBA | High-performing competitor |
| COMP004 | BrandC | $30.00 | 3.8 | 300 | FBA | Lower rating competitor |
| COMP005 | BrandD | $35.00 | 4.0 | 400 | FBM | FBM competitor |

### Required Search Terms

| Search Term | 14d Spend | CVR | Purpose |
|-------------|-----------|-----|---------|
| "test keyword 1" | $500 | 12% | Top performer |
| "test keyword 2" | $400 | 10% | Second rank |
| "test keyword 3" | $300 | 8% | Third rank |
| "B0TESTASIN" | $200 | 15% | Should be excluded (is ASIN) |
| "test keyword 4" | $100 | 5% | Below 50% threshold |

---

## Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Product Owner | | | |
| QA Lead | | | |
| Dev Lead | | | |
| UAT Tester | | | |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Jan 2026 | Abdul | Initial UAT checklist created |
