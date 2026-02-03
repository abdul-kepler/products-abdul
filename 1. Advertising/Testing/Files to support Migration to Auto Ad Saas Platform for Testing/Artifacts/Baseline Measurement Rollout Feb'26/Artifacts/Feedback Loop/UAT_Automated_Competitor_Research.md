# UAT Checklist: Automated Competitor Research

**Feature:** Automated Competitor Research (Shortlist Competitors → Extract Keywords)
**Version:** 1.0
**Last Updated:** January 2026
**Related Tickets:** PROD-323, PROD-331, PROD-1195, PROD-308, PROD-1129, PROD-2161, PROD-2162, PROD-2163, PROD-2170

---

## Logic Overview

### Purpose
Automatically identify competitors for a selected product and extract relevant keywords from those competitors to use in advertising campaigns. This is a 2-step user journey that replaces manual competitor research and keyword collection.

### Key Difference from Other Research Features

| Feature | Purpose | Output |
|---------|---------|--------|
| **Automated KW Research** | AI-generated keywords from OUR product listing | Keywords classified by R/S/C/N |
| **Automated Target ASIN Research** | Find competitor ASINs to TARGET with our ads | Qualified ASINs for ASIN Targeting campaigns |
| **Automated Competitor Research** | Find competitors to EXTRACT KEYWORDS from | Keywords from competitor rankings for our campaigns |

### End-to-End Process Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AUTOMATED COMPETITOR RESEARCH FLOW                        │
└─────────────────────────────────────────────────────────────────────────────┘

STEP 1: PRODUCT SELECTION (PROD-323)
┌─────────────────────────────────────────────────────────────────────────────┐
│  Trigger: User clicks "[Add Product]" in ASIN Config UI                     │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Product Selection Modal:                                           │   │
│  │  • Shows ALL synced products from Ads-API                          │   │
│  │  • Default filter: ELIGIBLE products only (toggle OFF)             │   │
│  │  • Toggle: "Show all products including ineligible"                │   │
│  │  • SP Status badges: ELIGIBLE / INELIGIBLE / SUPPRESSED            │   │
│  │  • Single product selection (radio buttons)                        │   │
│  │  • Search/filter by ASIN or product name                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Selection Rules:                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  ELIGIBLE     → Can select (enabled radio button)                   │   │
│  │  INELIGIBLE   → Cannot select (disabled + tooltip)                  │   │
│  │  SUPPRESSED   → Cannot select (disabled + critical warning)         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Button: "[Next: Select Competitors]" → Proceeds to Step 2                  │
│  Backend validation: Rejects INELIGIBLE/SUPPRESSED if submitted            │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
STEP 2: COMPETITOR SELECTION (PROD-331 / PROD-1195)
┌─────────────────────────────────────────────────────────────────────────────┐
│  Trigger: Automatic after Step 1 completion                                 │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Competitor Fetch (Auto):                                           │   │
│  │  • API call to fetch competitors for selected product              │   │
│  │  • Source: Listing Optimization team's competitor logic            │   │
│  │  • Up to 50 competitors per product                                │   │
│  │  • Loading state: 3-5 seconds                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Competitor Display:                                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Each competitor card shows:                                        │   │
│  │  • Product Image          • Product Title                          │   │
│  │  • ASIN                   • Rank (number)                          │   │
│  │  • Revenue ($)            • Price ($)                              │   │
│  │  • Root Keywords (tags)   • Checkbox (checked by default)          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Selection Rules:                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • ALL competitors auto-selected by default (checkboxes checked)   │   │
│  │  • User can DESELECT competitors they don't want                   │   │
│  │  • Counter: "X/Y competitors selected" (real-time)                 │   │
│  │  • Minimum: 5 competitors MUST be selected                         │   │
│  │  • "[Confirm & Continue]" button disabled if < 5 selected          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Button: "[Confirm & Continue]" → Proceeds to Keyword Extraction           │
│  Button: "[Back]" → Returns to Step 1                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
STEP 3: KEYWORD EXTRACTION (PROD-1129 / PROD-2170)
┌─────────────────────────────────────────────────────────────────────────────┐
│  Trigger: Automatic after competitor confirmation                           │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Jungle Scout API Integration:                                      │   │
│  │  • Endpoint: keywords_by_asin                                       │   │
│  │  • Input: Selected competitor ASINs                                 │   │
│  │  • Fetches keywords that competitors rank for                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Data Points Extracted (13 fields):                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Search Volume:                                                     │   │
│  │  • monthly_search_volume_exact                                     │   │
│  │  • monthly_search_volume_broad                                     │   │
│  │                                                                     │   │
│  │  Competitor Ranking:                                                │   │
│  │  • searched_asins_avg_organic_rank                                 │   │
│  │  • searched_asins_avg_sponsored_rank                               │   │
│  │  • searched_asins_organic_count                                    │   │
│  │  • searched_asins_sponsored_count                                  │   │
│  │                                                                     │   │
│  │  Competition & Relevancy:                                           │   │
│  │  • ease_of_ranking_score                                           │   │
│  │  • relevancy_score                                                 │   │
│  │                                                                     │   │
│  │  PPC Intelligence:                                                  │   │
│  │  • ppc_bid_broad                                                   │   │
│  │  • ppc_bid_exact                                                   │   │
│  │  • sp_brand_ad_bid                                                 │   │
│  │  • recommended_promotions                                          │   │
│  │  • updated_at                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
STEP 4: RESEARCH LIST UI (PROD-2161 / PROD-1462)
┌─────────────────────────────────────────────────────────────────────────────┐
│  Keywords displayed in Research List page                                   │
│  URL: portal.keplercommerce.com/amazon-ads/keywords/list                   │
│                                                                             │
│  TAB 1: Keyword Research Table                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Columns:                                                           │   │
│  │  • Keyword                    • JS Search Volume (Exact/Broad)     │   │
│  │  • JS Avg Organic Rank        • JS Avg Sponsored Rank              │   │
│  │  • JS Organic ASIN Count      • JS Sponsored ASIN Count            │   │
│  │  • JS Ease of Ranking         • JS Relevancy Score                 │   │
│  │  • JS PPC Bid (Exact/Broad)   • JS SP Brand Ad Bid                 │   │
│  │  • JS Recommended Promotions                                       │   │
│  │                                                                     │   │
│  │  Features:                                                          │   │
│  │  • Filter keywords by search                                       │   │
│  │  • Select All checkbox (respects current filter)                   │   │
│  │  • Bulk Edit selected keywords                                     │   │
│  │  • Export functionality                                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  TAB 2: Attribute Table                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Columns: Attribute Type, Value, Rank, Notes                       │   │
│  │                                                                     │   │
│  │  Features:                                                          │   │
│  │  • Add Row button                                                  │   │
│  │  • Delete Row button                                               │   │
│  │  • Import functionality                                            │   │
│  │  • Export functionality                                            │   │
│  │  • Auto-rank sequencing                                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Data Refresh & Maintenance

| Process | Trigger | Action |
|---------|---------|--------|
| **Gap-fill** | Every 7 days | Keywords with 3+ null fields → re-fetch from JS |
| **Auto-fetch** | New keyword added (non-JS source) | Fetch JS data for new keyword |
| **Backfill** | One-time | Populate JS data for all historical keywords |

---

## Test Summary

| Section | Type 1 (Verification) | Type 2 (Validation) | Total |
|---------|----------------------|---------------------|-------|
| 1. Product Selection (Step 1) | 18 | 10 | 28 |
| 2. Competitor Selection (Step 2) | 20 | 12 | 32 |
| 3. Competitor API Integration | 12 | 8 | 20 |
| 4. Keyword Extraction (Jungle Scout) | 18 | 10 | 28 |
| 5. Research List UI - Tab 1 | 15 | 8 | 23 |
| 6. Research List UI - Tab 2 | 12 | 8 | 20 |
| 7. Data Refresh & Maintenance | 10 | 6 | 16 |
| 8. End-to-End Flow | 8 | 6 | 14 |
| **TOTAL** | **113** | **68** | **181** |

---

## Section 1: Product Selection - Step 1 (PROD-323)

### Type 1: Verification Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 1.1.1 | Click "[Add Product]" in ASIN Config | Product Selection Modal opens | |
| 1.1.2 | Modal shows synced products from Ads-API | Products list displayed | |
| 1.1.3 | Default filter = ELIGIBLE products only | Only ELIGIBLE products visible | |
| 1.1.4 | Toggle "Show all products including ineligible" ON | All products visible with badges | |
| 1.1.5 | Toggle "Show all products including ineligible" OFF | Only ELIGIBLE products visible | |
| 1.1.6 | ELIGIBLE product has enabled radio button | Can select | |
| 1.1.7 | INELIGIBLE product has disabled radio button | Cannot select | |
| 1.1.8 | INELIGIBLE product shows tooltip on hover | "This product is not eligible for advertising" | |
| 1.1.9 | SUPPRESSED product has disabled radio button | Cannot select | |
| 1.1.10 | SUPPRESSED product shows critical warning tooltip | Warning message displayed | |
| 1.1.11 | Single product selection only (radio buttons) | Only one product selectable at a time | |
| 1.1.12 | Search by ASIN filters products | Matching ASINs shown | |
| 1.1.13 | Search by product name filters products | Matching products shown | |
| 1.1.14 | "[Next: Select Competitors]" disabled without selection | Button disabled | |
| 1.1.15 | "[Next: Select Competitors]" enabled with selection | Button enabled | |
| 1.1.16 | Click "[Next: Select Competitors]" | Proceeds to Step 2 | |
| 1.1.17 | Backend validates selected product is ELIGIBLE | Validation passes | |
| 1.1.18 | Click "Cancel" closes modal | Modal closes, returns to ASIN Config | |

### Type 2: Validation Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 1.2.1 | Large product list (500+ ASINs) | Modal loads in < 2 seconds | |
| 1.2.2 | Pagination with 50 products per page | Pages work correctly | |
| 1.2.3 | Search debounce (300ms) | Search not triggered on every keystroke | |
| 1.2.4 | Bypass UI to submit INELIGIBLE ASIN | Backend returns 400 error | |
| 1.2.5 | Bypass UI to submit SUPPRESSED ASIN | Backend returns 400 error | |
| 1.2.6 | All products are INELIGIBLE (toggle OFF) | Empty state message shown | |
| 1.2.7 | Modal closes with selection made | Confirmation dialog appears | |
| 1.2.8 | Products not yet in ASIN Config shown | Already configured products excluded | |
| 1.2.9 | Loading state while fetching products | Spinner/skeleton shown | |
| 1.2.10 | API error fetching products | Error message with retry option | |

---

## Section 2: Competitor Selection - Step 2 (PROD-331 / PROD-1195)

### Type 1: Verification Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 2.1.1 | Step 2 displays after Step 1 completion | UI transitions automatically | |
| 2.1.2 | Competitors auto-fetched on Step 2 load | API call triggered | |
| 2.1.3 | Loading state while fetching (3-5 seconds) | Loading indicator shown | |
| 2.1.4 | All competitors displayed with checkboxes | Cards rendered correctly | |
| 2.1.5 | All competitors checked by default | All checkboxes pre-selected | |
| 2.1.6 | Competitor card shows Product Image | Image displayed | |
| 2.1.7 | Competitor card shows Product Title | Title displayed | |
| 2.1.8 | Competitor card shows ASIN | ASIN displayed | |
| 2.1.9 | Competitor card shows Rank | Rank number displayed | |
| 2.1.10 | Competitor card shows Revenue (formatted) | Currency formatted (e.g., $3,200) | |
| 2.1.11 | Competitor card shows Price (formatted) | Currency formatted (e.g., $27.99) | |
| 2.1.12 | Competitor card shows Root Keywords | Keywords as tags/list | |
| 2.1.13 | Checkbox deselection works | Can uncheck competitor | |
| 2.1.14 | Counter shows "X/Y competitors selected" | Counter displayed correctly | |
| 2.1.15 | Counter updates in real-time | Updates on selection change | |
| 2.1.16 | Minimum 5 competitors required | Validation enforced | |
| 2.1.17 | "[Confirm & Continue]" disabled if < 5 selected | Button disabled | |
| 2.1.18 | "[Confirm & Continue]" enabled if ≥ 5 selected | Button enabled | |
| 2.1.19 | Click "[Confirm & Continue]" | Proceeds to keyword extraction | |
| 2.1.20 | Click "[Back]" | Returns to Step 1 | |

### Type 2: Validation Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 2.2.1 | Competitor API returns 50 competitors | All 50 displayed | |
| 2.2.2 | Competitor API returns < 5 competitors | Error/warning shown | |
| 2.2.3 | Competitor API returns 0 competitors | Empty state message | |
| 2.2.4 | Competitor API failure (500 error) | Error with retry option | |
| 2.2.5 | Retry after API failure | API retried, loading shown | |
| 2.2.6 | Long competitor title | Truncated with ellipsis | |
| 2.2.7 | Many root keywords (10+) | Truncated with "show more" | |
| 2.2.8 | Responsive design (mobile 375px) | Layout adapts | |
| 2.2.9 | Deselect to exactly 4 competitors | "[Confirm]" button disabled | |
| 2.2.10 | Navigate back clears previous selection | Step 1 state reset | |
| 2.2.11 | Step 2 not accessible directly (without Step 1) | Redirect to Step 1 | |
| 2.2.12 | Currency formatting accuracy | Matches locale settings | |

---

## Section 3: Competitor API Integration (PROD-308)

### Type 1: Verification Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 3.1.1 | API endpoint: GET competitors by product ID | Returns competitor list | |
| 3.1.2 | Response includes competitor ASIN | Field present | |
| 3.1.3 | Response includes competitor title | Field present | |
| 3.1.4 | Response includes competitor image URL | Field present | |
| 3.1.5 | Response includes competitor rank | Field present | |
| 3.1.6 | Response includes competitor revenue | Field present | |
| 3.1.7 | Response includes competitor price | Field present | |
| 3.1.8 | Response includes root keywords | Field present | |
| 3.1.9 | API endpoint: POST submit final selection | Accepts product + competitor ASINs | |
| 3.1.10 | API response time < 5 seconds | Performance within threshold | |
| 3.1.11 | API uses Listing Optimization competitor logic | Correct algorithm applied | |
| 3.1.12 | API handles invalid product ID | Returns appropriate error | |

### Type 2: Validation Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 3.2.1 | Large competitor set (50 ASINs) | All returned correctly | |
| 3.2.2 | Product with no competitors | Empty array returned | |
| 3.2.3 | API rate limiting | Graceful handling | |
| 3.2.4 | Concurrent requests | No race conditions | |
| 3.2.5 | Competitor data freshness | Recent data (< 24 hours) | |
| 3.2.6 | Missing optional fields | Nulls handled gracefully | |
| 3.2.7 | Invalid ASIN format in response | Filtered out | |
| 3.2.8 | API timeout handling | Error with retry | |

---

## Section 4: Keyword Extraction - Jungle Scout (PROD-1129 / PROD-2170)

### Type 1: Verification Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 4.1.1 | API call to keywords_by_asin endpoint | Request sent correctly | |
| 4.1.2 | Input: Selected competitor ASINs | ASINs passed as parameter | |
| 4.1.3 | Extract monthly_search_volume_exact | Field stored | |
| 4.1.4 | Extract monthly_search_volume_broad | Field stored | |
| 4.1.5 | Extract searched_asins_avg_organic_rank | Field stored | |
| 4.1.6 | Extract searched_asins_avg_sponsored_rank | Field stored | |
| 4.1.7 | Extract searched_asins_organic_count | Field stored | |
| 4.1.8 | Extract searched_asins_sponsored_count | Field stored | |
| 4.1.9 | Extract ease_of_ranking_score | Field stored | |
| 4.1.10 | Extract relevancy_score | Field stored | |
| 4.1.11 | Extract ppc_bid_broad | Field stored | |
| 4.1.12 | Extract ppc_bid_exact | Field stored | |
| 4.1.13 | Extract sp_brand_ad_bid | Field stored | |
| 4.1.14 | Extract recommended_promotions | Field stored | |
| 4.1.15 | Extract updated_at (timestamp) | Field stored | |
| 4.1.16 | Keywords stored in database | Persistence verified | |
| 4.1.17 | Duplicate keywords deduplicated | No duplicates stored | |
| 4.1.18 | Keywords linked to ASIN | Correct association | |

### Type 2: Validation Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 4.2.1 | JS API failure for one competitor | Other competitors processed | |
| 4.2.2 | JS API returns partial data (some fields null) | Nulls stored, no error | |
| 4.2.3 | Large keyword set (1000+ keywords) | All stored correctly | |
| 4.2.4 | API rate limits (JS) | Batching/retry logic | |
| 4.2.5 | Keyword already exists in system | Updated, not duplicated | |
| 4.2.6 | Special characters in keyword | Handled correctly | |
| 4.2.7 | Very long keyword (100+ chars) | Stored/truncated correctly | |
| 4.2.8 | Multiple competitors share same keyword | Keyword stored once | |
| 4.2.9 | Zero keywords returned for competitor | Handled gracefully | |
| 4.2.10 | API timeout | Retry with backoff | |

---

## Section 5: Research List UI - Tab 1 (PROD-2161 / PROD-2062)

### Type 1: Verification Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 5.1.1 | Navigate to Research List page | Page loads correctly | |
| 5.1.2 | Tab 1 displays keyword table | Table rendered | |
| 5.1.3 | Column: Keyword | Displayed | |
| 5.1.4 | Column: JS Search Volume (Exact) | Displayed | |
| 5.1.5 | Column: JS Search Volume (Broad) | Displayed | |
| 5.1.6 | Column: JS Avg Organic Rank | Displayed | |
| 5.1.7 | Column: JS Avg Sponsored Rank | Displayed | |
| 5.1.8 | Column: JS Ease of Ranking | Displayed | |
| 5.1.9 | Column: JS Relevancy Score | Displayed | |
| 5.1.10 | Column: JS PPC Bid (Exact/Broad) | Displayed | |
| 5.1.11 | Filter keywords by search | Filter works | |
| 5.1.12 | "Select All" checkbox in header | Selects all visible rows | |
| 5.1.13 | "Select All" with filter applied | Selects only filtered rows | |
| 5.1.14 | Bulk Edit button | Opens bulk edit modal | |
| 5.1.15 | Export functionality | CSV/Excel downloaded | |

### Type 2: Validation Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 5.2.1 | Large keyword list (10,000 rows) | Page performs well | |
| 5.2.2 | Pagination (10/20/50/100/200 per page) | All options work | |
| 5.2.3 | Column sorting | Sort works correctly | |
| 5.2.4 | Missing JS data (nulls) | Displayed as blank or "N/A" | |
| 5.2.5 | Search filter debounce | Not triggered on every keystroke | |
| 5.2.6 | Bulk edit 500 keywords | Completes successfully | |
| 5.2.7 | Export 10,000 keywords | File generated correctly | |
| 5.2.8 | Mobile responsive | Layout adapts | |

---

## Section 6: Research List UI - Tab 2 (PROD-2053 / PROD-2058)

### Type 1: Verification Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 6.1.1 | Tab 2 displays Attribute Table | Table rendered | |
| 6.1.2 | Column: Attribute Type | Displayed | |
| 6.1.3 | Column: Value | Displayed | |
| 6.1.4 | Column: Rank | Displayed | |
| 6.1.5 | Column: Notes | Displayed | |
| 6.1.6 | "Add Row" button visible | Button displayed | |
| 6.1.7 | Click "Add Row" | New empty row added | |
| 6.1.8 | "Delete Row" button visible | Button displayed | |
| 6.1.9 | Select row and click "Delete Row" | Row removed | |
| 6.1.10 | Rank auto-updates on delete | Sequence maintained | |
| 6.1.11 | Import functionality | File import works | |
| 6.1.12 | Export functionality | File export works | |

### Type 2: Validation Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 6.2.1 | Import file with 4 columns | Data imported correctly | |
| 6.2.2 | Import file with duplicate ranks | Validation error | |
| 6.2.3 | Delete all rows | Empty state handled | |
| 6.2.4 | Add row with same attribute+rank | Validation error | |
| 6.2.5 | Rank sequence validation | 1, 2, 3... enforced | |
| 6.2.6 | Large attribute table (100+ rows) | Performance acceptable | |
| 6.2.7 | Delete confirmation dialog | Confirmation shown | |
| 6.2.8 | Import overwrites existing data | Correct behavior | |

---

## Section 7: Data Refresh & Maintenance (PROD-2162 / PROD-2163 / PROD-2165)

### Type 1: Verification Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 7.1.1 | Gap-fill trigger: Every 7 days | Scheduled job runs | |
| 7.1.2 | Gap-fill: Keywords with 3+ null fields | Identified correctly | |
| 7.1.3 | Gap-fill: Re-fetch from JS API | API called, data updated | |
| 7.1.4 | Auto-fetch: New keyword from non-JS source | JS data fetched automatically | |
| 7.1.5 | Auto-fetch: Keyword from Harvesting | JS data populated | |
| 7.1.6 | Backfill: All existing keywords | JS data populated | |
| 7.1.7 | Backfill: One-time operation | Runs once, not repeated | |
| 7.1.8 | API failure during refresh | Logged, retry scheduled | |
| 7.1.9 | Null fields after refresh attempt | Stored as null | |
| 7.1.10 | updated_at timestamp refreshed | New timestamp stored | |

### Type 2: Validation Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 7.2.1 | Gap-fill with 10,000 keywords | Completes within timeout | |
| 7.2.2 | JS API rate limits during backfill | Batching respects limits | |
| 7.2.3 | Concurrent refresh jobs | No duplicate processing | |
| 7.2.4 | Threshold: 2 null fields | NOT flagged for gap-fill | |
| 7.2.5 | Threshold: 3 null fields | Flagged for gap-fill | |
| 7.2.6 | Auto-fetch async processing | Non-blocking keyword addition | |

---

## Section 8: End-to-End Flow

### Type 1: Verification Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 8.1.1 | Complete flow: Product → Competitors → Keywords | All steps complete | |
| 8.1.2 | Keywords appear in Research List | Data visible in UI | |
| 8.1.3 | Time to complete < 5 minutes | Within target | |
| 8.1.4 | ASIN Config updated with new product | Product added | |
| 8.1.5 | Competitor ASINs stored | Association saved | |
| 8.1.6 | Keywords linked to correct ASIN | Correct parent | |
| 8.1.7 | All 13 JS fields populated | No missing required fields | |
| 8.1.8 | User can filter keywords by ASIN | Filter works | |

### Type 2: Validation Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 8.2.1 | Network interruption mid-flow | Graceful recovery | |
| 8.2.2 | Browser refresh during Step 2 | State preserved or restart | |
| 8.2.3 | Concurrent users same product | No conflicts | |
| 8.2.4 | Second run for same product | Updates, not duplicates | |
| 8.2.5 | Full flow with maximum competitors (50) | Completes successfully | |
| 8.2.6 | Full flow with minimum competitors (5) | Completes successfully | |

---

## Regression Test Suite

### Critical Path Tests (Run on Every Release)

| # | Test Case | Priority |
|---|-----------|----------|
| R1 | Product Selection: ELIGIBLE product can be selected | P0 |
| R2 | Product Selection: INELIGIBLE product blocked | P0 |
| R3 | Competitor fetch returns valid data | P0 |
| R4 | Minimum 5 competitors validation | P0 |
| R5 | JS keyword extraction returns 13 fields | P0 |
| R6 | Keywords appear in Research List | P0 |
| R7 | Gap-fill scheduled job runs | P0 |
| R8 | End-to-end flow completes in < 5 minutes | P0 |

---

## Test Data Requirements

### Required Test Products

| ASIN | Status | Purpose |
|------|--------|---------|
| B0TEST001 | ELIGIBLE | Standard flow testing |
| B0TEST002 | INELIGIBLE | Blocked selection testing |
| B0TEST003 | SUPPRESSED | Critical warning testing |
| B0TEST004 | ELIGIBLE | Large competitor list testing |
| B0TEST005 | ELIGIBLE | No competitors testing |

### Required Test Competitors

| ASIN | Rank | Revenue | Price | Keywords |
|------|------|---------|-------|----------|
| B0COMP001 | 1 | $5,000 | $29.99 | 15 keywords |
| B0COMP002 | 2 | $3,200 | $24.99 | 12 keywords |
| B0COMP003 | 3 | $2,800 | $34.99 | 10 keywords |
| B0COMP004 | 4 | $1,500 | $19.99 | 8 keywords |
| B0COMP005 | 5 | $1,200 | $27.99 | 20 keywords |

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
