# UAT Checklist: Automated Campaign Generation (ASIN Targeting)

**Feature:** Automated Campaign Generation - Sponsored Products ASIN Targeting (SPAS)
**Version:** 1.0
**Last Updated:** January 2026
**Related Tickets:** PROD-356, PROD-357, PROD-310, PROD-358, PROD-359, PROD-361, PROD-362

---

## Logic Overview

### Purpose
Automatically create Sponsored Products ASIN Targeting (SPAS) campaigns when new Brand Groups are identified from the ASIN Research qualification process. Each brand group results in one campaign targeting competitor ASINs from that brand.

### End-to-End Process Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                  AUTOMATED CAMPAIGN GENERATION FLOW                          │
└─────────────────────────────────────────────────────────────────────────────┘

Step 1: TRIGGER (PROD-356)
┌─────────────────────────────────────────────────────────────────────────────┐
│  Trigger Condition:                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  New Brand Group found/created in backend (from PROD-357)           │   │
│  │  + User has toggled ASIN Targeting ON                               │   │
│  │  + No blocking error conditions present                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Total Campaigns = Total Brand Groups                                       │
│  One campaign per Brand Group                                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
Step 2: CAMPAIGN NAMING (PROD-356)
┌─────────────────────────────────────────────────────────────────────────────┐
│  Format: ZZZZZZ-YYYY-XXXX-WW-V-UUUUUUUUUU-T-KW                              │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Field Breakdown:                                                   │   │
│  │  ┌──────────┬─────────────────────────────────────────────────────┐│   │
│  │  │ ZZZZZZ   │ Static value: "XXXXXX"                              ││   │
│  │  │ YYYY     │ "SPAS" (Sponsored Products ASIN Targeting)          ││   │
│  │  │ XXXX     │ Brand Code (4-character unique code)                ││   │
│  │  │ WW       │ Hardcoded: "XX"                                     ││   │
│  │  │ V        │ "S"                                                 ││   │
│  │  │ UUUUUUUU │ Client's ASIN (10 characters)                       ││   │
│  │  │ T        │ Hardcoded: "X"                                      ││   │
│  │  │ KW       │ Brand Group Name (truncate if exceeds limit)        ││   │
│  │  └──────────┴─────────────────────────────────────────────────────┘│   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ⚠️ If name exceeds Amazon character limit → truncate KW and append "_"    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
Step 3: BRAND CODE ASSIGNMENT (PROD-356)
┌─────────────────────────────────────────────────────────────────────────────┐
│  Brand Code Format: [First 2 chars][Serial Number]                          │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Rules:                                                             │   │
│  │  • First 2 characters = First letters of first 2 words in brand    │   │
│  │  • If single-word brand = First 2 characters of that word          │   │
│  │  • Last 2 characters = Serial number for that prefix               │   │
│  │  • Brand codes are GLOBAL at Kepler level (not per seller)         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Examples:                                                                  │
│  ┌─────────────────┬─────────────┐                                         │
│  │ Brand Name      │ Brand Code  │                                         │
│  ├─────────────────┼─────────────┤                                         │
│  │ Supreme One     │ SO01        │                                         │
│  │ Super Oats      │ SO02        │                                         │
│  │ Soapera         │ SO03        │                                         │
│  │ Truly Indian    │ TI01        │                                         │
│  │ Amazon Basics   │ AB01        │                                         │
│  └─────────────────┴─────────────┘                                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
Step 4: CAMPAIGN CONFIGURATION (PROD-356)
┌─────────────────────────────────────────────────────────────────────────────┐
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  Configuration Element    │  Value                                    │ │
│  ├───────────────────────────┼───────────────────────────────────────────┤ │
│  │  Targeting Type           │  Manual ASIN Targeting                    │ │
│  │  Placement Modifier       │  Skip (none)                              │ │
│  │  Bidding Strategy         │  Down Only                                │ │
│  │  Ad Group                 │  Default structure                        │ │
│  │  Portfolio                │  Skip (none)                              │ │
│  │  Daily Budget             │  User-defined OR Auto Budget (fallback)   │ │
│  │  Bid Configuration        │  Per bid logic ticket                     │ │
│  └───────────────────────────┴───────────────────────────────────────────┘ │
│                                                                             │
│  Negative ASIN Handling:                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  System continuously monitors Target ASIN performance               │   │
│  │  IF Target ASIN meets underperformance criteria:                    │   │
│  │  → Automatically add as NEGATIVE in Auto Campaign                   │   │
│  │  → Add to BOTH Substitute & Complement match types                  │   │
│  │  → Process runs ONGOING (not one-time)                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
Step 5: UI INTEGRATION
┌─────────────────────────────────────────────────────────────────────────────┐
│  A. Campaign Config UI (PROD-310)                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Display ASIN Targeting campaigns alongside other types           │   │
│  │  • Relevancy Tag = "XXXXXX" (hardcoded)                             │   │
│  │  • Match Type = "-" (dash)                                          │   │
│  │  • Custom Negative KWs = Non-editable (greyed out)                  │   │
│  │  • Editable: Target ACOS, Status, Daily Budget                      │   │
│  │  • Uniqueness: ASIN + Target Brand (Relevancy Tag optional)         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  B. KW Config UI (PROD-361)                                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Display Target ASINs in "Target" column (renamed from "Keyword") │   │
│  │  • Editable: Fixed Bid, Ceiling Bid, Floor Bid, KW Status,         │   │
│  │              Target ACOS, all bid expiries                          │   │
│  │  • N/A fields displayed as "N/A"                                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  C. ST Config UI (PROD-362)                                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Display Target ASINs in "Search Term" column                     │   │
│  │  • "Target" column (renamed from "Keyword")                         │   │
│  │  • For Auto campaigns: ST = Target ASIN, Target = Complement/Subst  │   │
│  │  • For Manual ASIN: Both columns show Target ASIN                   │   │
│  │  • Features: Add negatives, update remarks, view metrics            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
Step 6: VALIDATION RULES (PROD-358, PROD-359)
┌─────────────────────────────────────────────────────────────────────────────┐
│  UI Validation (PROD-358):                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Target ACOS: Must be 1-100% OR blank                             │   │
│  │  • Daily Budget: Must be ≥ $5 OR blank (if Auto Budget enabled)     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Bulk Import Validation (PROD-359):                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Same rules as UI validation                                      │   │
│  │  • Non-editable fields (Match Type, Tag, Custom Neg KWs):           │   │
│  │    → Either ignore input OR produce error                           │   │
│  │  • Editable fields via bulk: ASIN, Target ACOS, Daily Budget,       │   │
│  │    Ad Status, Targeting Spec (= Target Brand)                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Campaign Name Example

```
Brand Group: "Truly Indian"
Client ASIN: B09AHTRT6I
Brand Code: TI01

Campaign Name: XXXXXX-SPAS-TI01-XX-S-B09AHTRT6I-X-Truly Indian

If brand name is very long:
Brand Group: "Premium Organic Natural Wellness Solutions"
Campaign Name: XXXXXX-SPAS-PO01-XX-S-B09AHTRT6I-X-Premium Organic Nat_
                                                  ↑ truncated with underscore
```

---

## Test Summary

| Section | Type 1 (Verification) | Type 2 (Validation) | Total |
|---------|----------------------|---------------------|-------|
| 1. Campaign Trigger | 12 | 8 | 20 |
| 2. Campaign Naming | 15 | 10 | 25 |
| 3. Brand Code Assignment | 12 | 8 | 20 |
| 4. Campaign Configuration | 18 | 10 | 28 |
| 5. Negative ASIN Handling | 12 | 8 | 20 |
| 6. Campaign Config UI | 18 | 10 | 28 |
| 7. KW Config UI | 15 | 8 | 23 |
| 8. ST Config UI | 15 | 8 | 23 |
| 9. Validation Rules | 12 | 8 | 20 |
| 10. Bulk Import/Export | 14 | 8 | 22 |
| **TOTAL** | **143** | **86** | **229** |

---

## Section 1: Campaign Trigger (PROD-356)

### Type 1: Verification Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 1.1.1 | New Brand Group created in backend | Campaign creation triggers | |
| 1.1.2 | Brand Group exists, no new ASINs added | No new campaign created | |
| 1.1.3 | ASIN Targeting toggled ON | Campaigns activate | |
| 1.1.4 | ASIN Targeting toggled OFF | Campaigns do not activate | |
| 1.1.5 | Multiple Brand Groups created simultaneously | One campaign per group | |
| 1.1.6 | Total campaigns = Total brand groups | Count matches | |
| 1.1.7 | Blocking error condition present | Campaign NOT created | |
| 1.1.8 | Error condition resolved | Campaign creates on retry | |
| 1.1.9 | Brand Group with 1 qualified ASIN | Campaign created | |
| 1.1.10 | Brand Group with 50 qualified ASINs | Campaign created with all | |
| 1.1.11 | Trigger timestamp logged | Correct datetime | |
| 1.1.12 | Campaign linked to correct Client ASIN | Correct association | |

### Type 2: Validation Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 1.2.1 | Concurrent brand group creation | No duplicate campaigns | |
| 1.2.2 | Large batch: 100 brand groups | All 100 campaigns created | |
| 1.2.3 | Brand Group with missing data | Error logged, skipped | |
| 1.2.4 | API timeout during creation | Retry mechanism works | |
| 1.2.5 | Partial failure (3 of 10 fail) | 7 campaigns created, 3 logged | |
| 1.2.6 | Brand Group deletion after campaign created | Campaign persists | |
| 1.2.7 | ASIN disabled mid-creation | Appropriate handling | |
| 1.2.8 | Campaign creation performance < 30 seconds | Within threshold | |

---

## Section 2: Campaign Naming (PROD-356)

### Type 1: Verification Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 2.1.1 | ZZZZZZ field = "XXXXXX" | Static value correct | |
| 2.1.2 | YYYY field = "SPAS" | Campaign type correct | |
| 2.1.3 | WW field = "XX" | Hardcoded value correct | |
| 2.1.4 | V field = "S" | Hardcoded value correct | |
| 2.1.5 | T field = "X" | Hardcoded value correct | |
| 2.1.6 | UUUUUUUUUU = Client's ASIN | Correct ASIN inserted | |
| 2.1.7 | KW = Brand Group Name | Correct brand name | |
| 2.1.8 | Format matches: ZZZZZZ-YYYY-XXXX-WW-V-UUUUUUUUUU-T-KW | All fields in order | |
| 2.1.9 | Name within Amazon character limit | No truncation needed | |
| 2.1.10 | Name exceeds Amazon limit | KW truncated with "_" | |
| 2.1.11 | Brand name = "Truly Indian" | Name: XXXXXX-SPAS-TI01-XX-S-B0XXX-X-Truly Indian | |
| 2.1.12 | ASIN with 10 characters | All 10 chars included | |
| 2.1.13 | Hyphens used as separators | Correct delimiter | |
| 2.1.14 | No special characters in name (except hyphen) | Clean format | |
| 2.1.15 | Campaign name unique per Brand Group + ASIN | No duplicates | |

### Type 2: Validation Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 2.2.1 | Boundary: Name exactly at Amazon limit | No truncation | |
| 2.2.2 | Boundary: Name 1 char over limit | KW truncated by 1 + "_" | |
| 2.2.3 | Very long brand name (100 chars) | Truncated appropriately | |
| 2.2.4 | Brand name with special characters | Characters handled/sanitized | |
| 2.2.5 | Brand name with unicode | Handled correctly | |
| 2.2.6 | Empty brand name | Error or default handling | |
| 2.2.7 | Numeric-only brand name ("12345") | Handled correctly | |
| 2.2.8 | Same brand different ASIN | Unique campaign names | |
| 2.2.9 | Same ASIN different brand | Unique campaign names | |
| 2.2.10 | Truncation underscore always at end | "_" is final character | |

---

## Section 3: Brand Code Assignment (PROD-356)

### Type 1: Verification Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 3.1.1 | Two-word brand "Supreme One" | Code = "SO01" | |
| 3.1.2 | Second brand with same prefix "Super Oats" | Code = "SO02" | |
| 3.1.3 | One-word brand "Soapera" | Code = "SO03" | |
| 3.1.4 | Brand with 3+ words "Best Foods International" | Uses first 2 words → "BF01" | |
| 3.1.5 | Serial number increments correctly | 01, 02, 03... | |
| 3.1.6 | Global at Kepler level (not per seller) | Same brand = same code across sellers | |
| 3.1.7 | Code = exactly 4 characters | Length verified | |
| 3.1.8 | First 2 chars = letters | Alphabetic only | |
| 3.1.9 | Last 2 chars = numbers | Numeric only | |
| 3.1.10 | Brand code uniqueness | No duplicate codes | |
| 3.1.11 | Brand code persisted in database | Lookup returns same code | |
| 3.1.12 | New brand creates new code | Incremented serial | |

### Type 2: Validation Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 3.2.1 | Brand starting with number "3M" | Handled appropriately | |
| 3.2.2 | Brand with special chars "Ben & Jerry's" | Uses B and J → "BJ01" | |
| 3.2.3 | Single letter brand "X" | Handled (e.g., "X_01" or "XX01") | |
| 3.2.4 | 99 brands with same prefix | Codes SO01 through SO99 | |
| 3.2.5 | 100th brand with same prefix | Handles overflow (e.g., error or extend) | |
| 3.2.6 | Brand name all numbers "123" | Appropriate handling | |
| 3.2.7 | Brand with leading space " Acme" | Trimmed, code = "AC01" | |
| 3.2.8 | Case sensitivity "ACME" vs "acme" | Same brand, same code | |

---

## Section 4: Campaign Configuration (PROD-356)

### Type 1: Verification Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 4.1.1 | Targeting Type = Manual ASIN Targeting | Correct type set | |
| 4.1.2 | Placement Modifier = None | No modifiers applied | |
| 4.1.3 | Bidding Strategy = Down Only | Correct strategy | |
| 4.1.4 | Ad Group = Default structure | Default used | |
| 4.1.5 | Portfolio = None/Skip | No portfolio assigned | |
| 4.1.6 | Daily Budget = User-defined (when available) | User value used | |
| 4.1.7 | Daily Budget fallback to Auto Budget | System-computed used | |
| 4.1.8 | Daily Budget minimum = $5 | Enforced minimum | |
| 4.1.9 | Bid Configuration per bid logic | Correct bids applied | |
| 4.1.10 | Campaign status = User toggle (ON/OFF) | Respects user setting | |
| 4.1.11 | All Target ASINs from Brand Group added | Complete list | |
| 4.1.12 | Target ACOS inherited correctly | From config hierarchy | |
| 4.1.13 | Campaign created on Amazon API | API call successful | |
| 4.1.14 | Campaign ID returned and stored | ID persisted locally | |
| 4.1.15 | Campaign synced with Amazon | Status matches | |
| 4.1.16 | Client ASIN = Advertised product | Correct ASIN promoted | |
| 4.1.17 | Target ASINs = Competitor products | Correct targeting | |
| 4.1.18 | Campaign active only when toggled ON | Respects activation state | |

### Type 2: Validation Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 4.2.1 | User Budget = $4.99 | Rejected, minimum $5 | |
| 4.2.2 | User Budget = $5.00 | Accepted | |
| 4.2.3 | Auto Budget disabled, no user budget | Error or default handling | |
| 4.2.4 | Target ACOS = 0% | Rejected per validation | |
| 4.2.5 | Target ACOS = 101% | Rejected per validation | |
| 4.2.6 | Amazon API failure on creation | Retry and error logging | |
| 4.2.7 | Concurrent campaign creation | No race conditions | |
| 4.2.8 | Large campaign (200 Target ASINs) | Created successfully | |
| 4.2.9 | Budget changed mid-campaign | Update applied | |
| 4.2.10 | Campaign audit trail | Creation event logged | |

---

## Section 5: Negative ASIN Handling (PROD-356)

### Type 1: Verification Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 5.1.1 | Target ASIN meets underperformance criteria | Added as negative | |
| 5.1.2 | Negative added to Substitute match type | In Auto Campaign | |
| 5.1.3 | Negative added to Complement match type | In Auto Campaign | |
| 5.1.4 | Monitoring runs continuously | Not one-time | |
| 5.1.5 | Monitoring frequency (e.g., daily) | Runs at expected interval | |
| 5.1.6 | Target ASIN performs well | NOT added as negative | |
| 5.1.7 | Previously negated ASIN improves | Remains negative (no auto-removal) | |
| 5.1.8 | Negative ASIN logged | Action recorded | |
| 5.1.9 | Multiple Target ASINs underperform | All negated correctly | |
| 5.1.10 | Criteria from Google Sheet applied | Correct thresholds | |
| 5.1.11 | Negative sync to Amazon API | Successfully pushed | |
| 5.1.12 | UI reflects negative status | Updated in ST Config | |

### Type 2: Validation Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 5.2.1 | Boundary: ASIN exactly at threshold | Correct decision | |
| 5.2.2 | High spend, zero sales | Added as negative | |
| 5.2.3 | Low spend, zero sales | Not negated (insufficient data) | |
| 5.2.4 | Data lag handling | Uses available data | |
| 5.2.5 | Multiple ASINs hit threshold same day | All processed | |
| 5.2.6 | Negative already exists | No duplicate negative | |
| 5.2.7 | Manual negative override | System respects manual | |
| 5.2.8 | Error during Amazon sync | Retry mechanism | |

---

## Section 6: Campaign Config UI (PROD-310)

### Type 1: Verification Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 6.1.1 | ASIN Targeting campaigns visible in list | Displayed alongside others | |
| 6.1.2 | Relevancy Tag = "XXXXXX" | Hardcoded value shown | |
| 6.1.3 | ASIN Column = Advertised ASIN | Client ASIN displayed | |
| 6.1.4 | Campaign Name per naming convention | Correct format | |
| 6.1.5 | Match Type = "-" (dash) | Displayed correctly | |
| 6.1.6 | Target ACOS editable | User can modify | |
| 6.1.7 | Status editable | User can modify | |
| 6.1.8 | Daily Budget editable | User can modify | |
| 6.1.9 | Custom Negative KWs non-editable | Greyed out/disabled | |
| 6.1.10 | Sorting includes ASIN Targeting | Sorts correctly | |
| 6.1.11 | Filtering includes ASIN Targeting | Filters correctly | |
| 6.1.12 | Pagination includes ASIN Targeting | Paginated correctly | |
| 6.1.13 | No new UI components required | Existing layout used | |
| 6.1.14 | Target Brand column visible (Targeting Spec) | Displays brand group | |
| 6.1.15 | Uniqueness = ASIN + Target Brand | Correct identification | |
| 6.1.16 | Bulk export includes ASIN Targeting | Export works | |
| 6.1.17 | Bulk import for ASIN Targeting | Import works | |
| 6.1.18 | No additional icons/indicators needed | Clean UI | |

### Type 2: Validation Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 6.2.1 | Edit Target ACOS to 0% | Validation error | |
| 6.2.2 | Edit Daily Budget to $3 | Validation error | |
| 6.2.3 | Large account (1000 campaigns) | UI performs well | |
| 6.2.4 | Mixed campaign types sorting | All types included | |
| 6.2.5 | Filter by campaign type "ASIN Targeting" | Only ASIN campaigns shown | |
| 6.2.6 | Search by campaign name | Finds ASIN campaigns | |
| 6.2.7 | Attempt edit Relevancy Tag | Blocked/ignored | |
| 6.2.8 | Attempt edit Match Type | Blocked/ignored | |
| 6.2.9 | Concurrent edits | No data loss | |
| 6.2.10 | Save changes syncs to Amazon | API call successful | |

---

## Section 7: KW Config UI (PROD-361)

### Type 1: Verification Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 7.1.1 | Target ASINs displayed in "Target" column | Column shows ASINs | |
| 7.1.2 | Column renamed from "Keyword" to "Target" | New name visible | |
| 7.1.3 | Fixed Bid editable | User can modify | |
| 7.1.4 | Fixed Bid - Expiry editable | User can modify | |
| 7.1.5 | Ceiling Bid editable | User can modify | |
| 7.1.6 | Ceiling Bid - Expiry editable | User can modify | |
| 7.1.7 | Floor Bid editable | User can modify | |
| 7.1.8 | Floor Bid - Expiry editable | User can modify | |
| 7.1.9 | KW Status editable | User can modify | |
| 7.1.10 | Target ACOS editable | User can modify | |
| 7.1.11 | N/A fields display "N/A" | Correct placeholder | |
| 7.1.12 | All metrics populated (where applicable) | Data shown correctly | |
| 7.1.13 | Bulk import for ASIN targets | Works correctly | |
| 7.1.14 | Bulk export for ASIN targets | Works correctly | |
| 7.1.15 | Validation rules applied | Invalid input rejected | |

### Type 2: Validation Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 7.2.1 | Fixed Bid without expiry | Bid not functional (per spec) | |
| 7.2.2 | Ceiling Bid without expiry | Bid not functional (per spec) | |
| 7.2.3 | Floor Bid without expiry | Bid not functional (per spec) | |
| 7.2.4 | Large batch update (500 ASINs) | Completes successfully | |
| 7.2.5 | Invalid ASIN format in bulk | Validation error | |
| 7.2.6 | Bid expiry in past | Validation error | |
| 7.2.7 | Concurrent bid updates | No race conditions | |
| 7.2.8 | All metrics calculate correctly | Accurate values | |

---

## Section 8: ST Config UI (PROD-362)

### Type 1: Verification Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 8.1.1 | Target ASINs from Auto (Complement) displayed | Shown in list | |
| 8.1.2 | Target ASINs from Auto (Substitute) displayed | Shown in list | |
| 8.1.3 | Target ASINs from Manual ASIN Targeting displayed | Shown in list | |
| 8.1.4 | "Search Term" column shows Target ASIN | Correct value | |
| 8.1.5 | "Target" column (renamed from Keyword) | New name visible | |
| 8.1.6 | Auto campaign: Target column = "Complement" or "Substitute" | Correct match type | |
| 8.1.7 | Manual ASIN: Both columns show Target ASIN | Correct display | |
| 8.1.8 | Add negatives functionality works | Can add negative | |
| 8.1.9 | Update user remarks works | Can update remarks | |
| 8.1.10 | All metrics displayed correctly | Accurate values | |
| 8.1.11 | N/A fields show "N/A" | Correct placeholder | |
| 8.1.12 | Bulk import for ASIN targets | Works correctly | |
| 8.1.13 | Bulk export for ASIN targets | Works correctly | |
| 8.1.14 | Validation rules applied | Invalid input rejected | |
| 8.1.15 | Same features as Search Terms | Feature parity | |

### Type 2: Validation Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 8.2.1 | Filter by match type "Complement" | Shows only complement | |
| 8.2.2 | Filter by match type "Substitute" | Shows only substitute | |
| 8.2.3 | Search by ASIN value | Finds target ASIN | |
| 8.2.4 | Sort by metrics | Sorts correctly | |
| 8.2.5 | Large dataset (5000 target ASINs) | UI performs well | |
| 8.2.6 | Mixed Search Terms + Target ASINs | Both displayed | |
| 8.2.7 | Negative status sync with Amazon | Status accurate | |
| 8.2.8 | Performance metrics accuracy | Matches Amazon data | |

---

## Section 9: Validation Rules (PROD-358, PROD-359)

### Type 1: Verification Tests - UI (PROD-358)

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 9.1.1 | Target ACOS = 50% | Accepted | |
| 9.1.2 | Target ACOS = 0% | Error: "Must be between 1-100%" | |
| 9.1.3 | Target ACOS = 101% | Error: "Must be between 1-100%" | |
| 9.1.4 | Target ACOS = blank | Accepted (exception) | |
| 9.1.5 | Daily Budget = $10 | Accepted | |
| 9.1.6 | Daily Budget = $4 | Error: "Must be >= $5" | |
| 9.1.7 | Daily Budget = blank (Auto Budget ON) | Accepted (exception) | |
| 9.1.8 | Daily Budget = blank (Auto Budget OFF) | Error expected | |
| 9.1.9 | Submission blocked on error | Cannot submit | |
| 9.1.10 | Error message displayed clearly | User sees message | |

### Type 1: Verification Tests - Bulk Import (PROD-359)

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 9.1.11 | Bulk: Target ACOS = 50% | Accepted | |
| 9.1.12 | Bulk: Target ACOS = 0% | Error or rejected | |
| 9.1.13 | Bulk: Daily Budget = $4 | Error or rejected | |
| 9.1.14 | Bulk: Non-editable field modified (Match Type) | Ignored or error | |

### Type 2: Validation Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 9.2.1 | Target ACOS = 1% (boundary) | Accepted | |
| 9.2.2 | Target ACOS = 100% (boundary) | Accepted | |
| 9.2.3 | Target ACOS = 0.9% | Error | |
| 9.2.4 | Target ACOS = 100.1% | Error | |
| 9.2.5 | Daily Budget = $5.00 (boundary) | Accepted | |
| 9.2.6 | Daily Budget = $4.99 | Error | |
| 9.2.7 | Multiple validation errors | All errors shown | |
| 9.2.8 | Bulk: Partial valid/invalid rows | Valid rows processed, invalid logged | |

---

## Section 10: Bulk Import/Export (PROD-310, PROD-361, PROD-362)

### Type 1: Verification Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 10.1.1 | Export Campaign Config includes ASIN Targeting | All campaigns exported | |
| 10.1.2 | Import Campaign Config for ASIN Targeting | Campaigns updated | |
| 10.1.3 | Export KW Config includes Target ASINs | All targets exported | |
| 10.1.4 | Import KW Config for Target ASINs | Targets updated | |
| 10.1.5 | Export ST Config includes Target ASINs | All targets exported | |
| 10.1.6 | Import ST Config for Target ASINs | Targets updated | |
| 10.1.7 | Template format correct | All columns present | |
| 10.1.8 | Import: ASIN field editable | User can set | |
| 10.1.9 | Import: Target ACOS field editable | User can set | |
| 10.1.10 | Import: Daily Budget field editable | User can set | |
| 10.1.11 | Import: Ad Status field editable | User can set | |
| 10.1.12 | Import: Targeting Spec field = Target Brand | User can set | |
| 10.1.13 | Non-matching record skipped | No campaign found = skip | |
| 10.1.14 | Matching record updated | Fields updated | |

### Type 2: Validation Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| 10.2.1 | Large export (10,000 rows) | Completes successfully | |
| 10.2.2 | Large import (10,000 rows) | Processes within timeout | |
| 10.2.3 | Import with header row mismatch | Error or handled gracefully | |
| 10.2.4 | Import empty file | No changes, no error | |
| 10.2.5 | Import duplicate rows | Handled appropriately | |
| 10.2.6 | Export file format (CSV/Excel) | Correct format | |
| 10.2.7 | Special characters in brand name | Exported/imported correctly | |
| 10.2.8 | Unicode characters | Handled correctly | |

---

## Regression Test Suite

### Critical Path Tests (Run on Every Release)

| # | Test Case | Priority |
|---|-----------|----------|
| R1 | End-to-end: Brand Group created → Campaign auto-created | P0 |
| R2 | Campaign naming convention accuracy | P0 |
| R3 | Brand code assignment uniqueness | P0 |
| R4 | Campaign configuration matches spec | P0 |
| R5 | Negative ASIN automation works | P0 |
| R6 | UI displays ASIN Targeting campaigns | P0 |
| R7 | Validation rules enforced | P0 |
| R8 | Bulk import/export functional | P0 |
| R9 | Amazon API sync successful | P0 |
| R10 | Budget/Bid changes reflected on Amazon | P0 |

---

## Test Data Requirements

### Required Brand Groups

| Brand Name | Expected Code | Purpose |
|------------|---------------|---------|
| Supreme One | SO01 | Two-word brand |
| Super Oats | SO02 | Same prefix, different serial |
| Soapera | SO03 | Single-word brand |
| Truly Indian | TI01 | Standard two-word |
| Best Foods International | BF01 | Multi-word (use first 2) |
| X | XX01 or X_01 | Single letter edge case |
| 3M | 3M01 or TM01 | Starts with number |
| Premium Organic Natural Wellness | PO01 | Very long name (truncation test) |

### Required Client ASINs

| ASIN | Purpose |
|------|---------|
| B09AHTRT6I | Standard 10-char ASIN |
| B0TESTASN1 | Test ASIN 1 |
| B0TESTASN2 | Test ASIN 2 |
| B0TESTASIN | Full 10-char test |

### Required Target ASINs

| ASIN | Brand | Purpose |
|------|-------|---------|
| B0COMP0001 | Supreme One | Competitor 1 |
| B0COMP0002 | Supreme One | Competitor 2 (same brand) |
| B0COMP0003 | Super Oats | Different brand |
| B0UNDERPERF | Supreme One | Underperformer (for negative test) |

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
