# UAT: Bid Optimization - ASIN Targeting (CVR Waterfall Differences Only)

## Overview

This document contains test cases SPECIFIC to ASIN Targeting's CVR Waterfall logic. The bid optimization formula is **identical to Manual KW Targeting** - refer to `UAT_Bid_Optimization_Manual_KW.md` for all bid logic tests.

**Source Logic:** `Bid Logic_08 Sep'25` - ASIN Targeting formula + CVR Waterfall

---

## Context: Understanding ASIN Targeting

- **Target ASIN:** The competitor/related product you want your ad to appear on
- **Search Term:** In ASIN Targeting, this is itself a 10-digit ASIN (the actual product page where ad appeared)
- **Goal:** Show ad on target ASIN's product detail page

**Key Insight:** Unlike Manual KW where search terms are keywords, in ASIN Targeting the "search term" IS an ASIN.

---

## Key Differences: ASIN Targeting vs Manual KW Targeting

| Aspect | Manual KW | ASIN Targeting |
|--------|-----------|----------------|
| **Bid Logic** | TOS% + ACOS Breach | **IDENTICAL** |
| **CVR Lookback** | 60 days | 180 days |
| **Search Term Meaning** | Actual keywords | 10-digit ASIN (product page) |
| **L1** | ASIN + Search Term (Exact) | ASIN + Search Term (where ST = ASIN) |
| **L2** | ASIN + KW + Match Type | Campaign Target-Matched Search Term (0.75× floor) |
| **L3** | N/A | Search Term Level (split: 0.5× or 1× floor) |
| **L4** | ASIN + Campaign | ASIN Level (Default floor) |
| **L5** | ASIN Level | Default CVR |
| **L6** | Default CVR | N/A |

---

## Floor Multipliers (Unique to ASIN Targeting)

| Level | Floor Applied | Rationale |
|-------|---------------|-----------|
| L1 | None (raw CVR) | Trust direct ASIN + Search Term data |
| L2 | 0.75 × Default CVR | Campaign-level aggregated data less precise |
| L3a (Spend path) | 0.5 × Default CVR | Conservative for potentially zero-conversion data |
| L3b (Orders path) | 1.0 × Default CVR | Has conversions, more trust |
| L4 | 1.0 × Default CVR | Fallback protection |
| L5 | Default CVR | Final fallback |

---

## Default CVR by Price Tier

| Price Range | Default CVR |
|-------------|-------------|
| K ≤ $25 | 15% |
| $25 < K ≤ $50 | 12.5% |
| $50 < K ≤ $100 | 10% |
| $100 < K ≤ $200 | 5% |
| K > $200 | 3% |

---

## CVR Waterfall Hierarchy Summary

| Level | Granularity | Qualification | Floor |
|-------|-------------|---------------|-------|
| L1 | ASIN + Search Term | Spend ≥ Price OR Orders ≥ 1 | None (raw) |
| L2 | Campaign Target-Matched Search Term | Any matched ST has Spend ≥ Price OR Orders ≥ 1 | 0.75 × Default |
| L3a | Search Term (Spend path) | Spend ≥ Price | 0.5 × Default |
| L3b | Search Term (Orders path) | Orders ≥ 1 (Spend < Price) | 1.0 × Default |
| L4 | ASIN Level | Orders ≥ 1 | 1.0 × Default |
| L5 | Default | Fallback | N/A |

---

# TYPE 1: VERIFICATION TESTS (ASIN Targeting CVR Waterfall)

## A. L1: ASIN + Search Term Level (6 tests)

*Search Term = ASIN where ad appeared*

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| AT-V01 | Filter: Target ASIN where same ASIN appears as Search Term in last 180 days AND Spend ≥ Product Price | CVR = raw calculated CVR (no floor) | L1 selected, no floor applied |
| AT-V02 | Filter: L1 qualified AND Spend reached Price at Day X | CVR from Day X lookback period | Reverse cumulative spend logic |
| AT-V03 | Filter: L1 qualified via Spend path AND Orders = 0 | CVR = 0% | Zero CVR when no orders despite spend |
| AT-V04 | Filter: ASIN + Search Term with Spend < Price AND Orders ≥ 1 | CVR from full 180-day period | L1 Step 1b path |
| AT-V05 | Filter: ASIN + Search Term with Spend < Price AND Orders = 0 | Falls to L2 | L1 not qualified |
| AT-V06 | Filter: Data from Day 181 | Excluded from calculation | 180-day boundary |

**Key Concept:** L1 checks if the TARGET ASIN also appears as a SEARCH TERM against itself (same ASIN appears in search term report).

---

## B. L2: Campaign Target-Matched Search Term Level (7 tests)

*Unique to ASIN Targeting - checks other targets in same campaign*

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| AT-V07 | Filter: No L1 data AND Campaign has other target ASINs appearing as search terms | Uses L2 CVR | L2 level selected |
| AT-V08 | Filter: L2 qualified AND Campaign Target-Matched CVR < 0.75 × Default | CVR = 0.75 × Default CVR | Floor applied |
| AT-V09 | Filter: L2 qualified AND Campaign Target-Matched CVR > 0.75 × Default | CVR = Campaign Target-Matched CVR | Uses higher of two |
| AT-V10 | Filter: Campaign with multiple matched search terms | CVR = Average across all matched | Aggregation logic |
| AT-V11 | Filter: Matched search term with Spend ≥ Price (qualifies) | Included in average | Spend path qualification |
| AT-V12 | Filter: Matched search term with Orders ≥ 1 (qualifies) | Included in average | Orders path qualification |
| AT-V13 | Filter: Matched search term with Spend < Price AND Orders = 0 | Excluded from average | Does not qualify |

**Example:**
- Campaign ATC-X12345 has targets: B09JKL1234, B0A7MN5678, B09XYZ9012, B0BCDE3456
- Calculating bid for B09XYZ9012
- System checks: Do any of these 4 ASINs appear as search terms in last 180 days?
- If B09JKL1234 and B0BCDE3456 appear as search terms with Spend ≥ Price, use their average CVR

---

## C. L3: Search Term Level - Split Path (8 tests)

*Unique: Different floors for Spend-qualified vs Orders-qualified*

### L3a: Spend ≥ Price Path (0.5× floor)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| AT-V14 | Filter: No L1/L2 data AND Search Term Spend ≥ Price | Uses L3a path | L3 Spend path selected |
| AT-V15 | Filter: L3a qualified AND Search Term CVR < 0.5 × Default | CVR = 0.5 × Default CVR | Lower floor applied |
| AT-V16 | Filter: L3a qualified AND Search Term CVR > 0.5 × Default | CVR = Search Term CVR | Uses higher of two |
| AT-V17 | Filter: L3a qualified AND Orders = 0 | Search Term CVR = 0%, Floor = 0.5 × Default | Zero CVR, floor saves |

### L3b: Orders ≥ 1 Path (1× floor)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| AT-V18 | Filter: No L1/L2 data AND Search Term Spend < Price AND Orders ≥ 1 | Uses L3b path | L3 Orders path selected |
| AT-V19 | Filter: L3b qualified AND Search Term CVR < Default | CVR = Default CVR | Full floor applied |
| AT-V20 | Filter: L3b qualified AND Search Term CVR > Default | CVR = Search Term CVR | Uses higher of two |
| AT-V21 | Filter: Search Term Spend < Price AND Orders = 0 | Falls to L4 | L3 not qualified |

**Why Different Floors:**
- Spend-qualified (L3a): May have 0 orders → 0.5× floor (conservative)
- Orders-qualified (L3b): Has conversions → full Default floor (more trust)

---

## D. L4: ASIN Level (4 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| AT-V22 | Filter: No L1/L2/L3 data AND Orders ≥ 1 at ASIN level (180 days) | Uses L4 CVR | L4 level selected |
| AT-V23 | Filter: L4 qualified AND ASIN CVR < Default | CVR = Default CVR | Floor applied |
| AT-V24 | Filter: L4 qualified AND ASIN CVR > Default | CVR = ASIN CVR | Uses higher of two |
| AT-V25 | Filter: No Orders at ASIN level | Falls to L5 | L4 not qualified |

---

## E. L5: Default Level (2 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| AT-V26 | Filter: No data at any level (L1-L4) | Uses Default CVR by price | Falls to L5 |
| AT-V27 | Filter: New target ASIN, no historical data | Default CVR applied | Cold start handled |

---

## F. Floor Multiplier Verification (5 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| AT-V28 | Filter: Price = $30 (Default CVR = 12.5%) at L2 | Floor = 0.75 × 12.5% = 9.375% | L2 floor calculation |
| AT-V29 | Filter: Price = $30 at L3a (Spend path) | Floor = 0.5 × 12.5% = 6.25% | L3a floor calculation |
| AT-V30 | Filter: Price = $30 at L3b (Orders path) | Floor = 1.0 × 12.5% = 12.5% | L3b floor calculation |
| AT-V31 | Filter: Same ASIN at different levels in different targets | Compare floors across levels | Multipliers consistent |
| AT-V32 | Filter: Price boundary ($25.01) | Default = 12.5%, verify floors | Price tier + multiplier |

---

# TYPE 2: VALIDATION TESTS (ASIN Targeting CVR Waterfall)

## A. L1 Raw CVR Issues (4 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| AT-VAL01 | Filter: L1 targets with high ACOS | Raw CVR may be wrong | No floor to protect |
| AT-VAL02 | Filter: L1 targets with CVR = 0% (Spend path, no orders) | Bid = Target × 0% × Price = $0.02 | Zero CVR causing underbid |
| AT-VAL03 | Filter: L1 targets where Spend just reached Price threshold | Small sample size | CVR may be unreliable |
| AT-VAL04 | Filter: L1 targets with very high CVR (>30%) | Compare actual vs estimated | Possible overbidding |

---

## B. L2 Campaign Target-Matched Issues (5 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| AT-VAL05 | Filter: L2 targets where matched search terms have very different CVRs | Average may be misleading | High variance in inputs |
| AT-VAL06 | Filter: L2 targets where 0.75× floor dominated | Actual CVR vs 0.75× Default | Floor may be too high/low |
| AT-VAL07 | Filter: Campaigns with only 1 matched search term | Single point driving CVR | Low confidence estimate |
| AT-VAL08 | Filter: L2 targets in campaigns with many targets (5+) | Compare performance across | Campaign structure impact |
| AT-VAL09 | Filter: L2 targets where target ASIN is very different from matched ASINs | Relevance of matched data | Apples to oranges comparison |

---

## C. L3 Split Path Issues (5 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| AT-VAL10 | Filter: L3a targets (Spend path) with 0 orders using 0.5× floor | Actual CVR vs 0.5× Default | 0.5× may be too high for non-converters |
| AT-VAL11 | Filter: L3b targets (Orders path) where actual CVR << Default | Default floor causing overbid | Floor too aggressive |
| AT-VAL12 | Filter: Targets that barely qualified for L3a (Spend just ≥ Price) | Compare to similar L3b targets | Path selection sensitivity |
| AT-VAL13 | Filter: L3 targets with high ACOS | Check which path (3a vs 3b) | Path may be wrong |
| AT-VAL14 | Filter: Targets where L3a gave CVR = 0.5× Default (floor applied) | Actual performance vs floor | Validate 0.5× multiplier |

---

## D. 180-Day Lookback Issues (4 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| AT-VAL15 | Filter: Seasonal products with 180-day CVR ≠ recent 30-day | Bid accuracy | Stale data impact |
| AT-VAL16 | Filter: Products with significant price changes in 180 days | CVR calculated at wrong price point | Threshold mismatch |
| AT-VAL17 | Filter: Competitor ASINs that went OOS during 180-day period | Historic CVR inflated | Target page was unavailable |
| AT-VAL18 | Filter: Compare 180-day CVR vs 60-day CVR accuracy | Which predicts better? | Lookback optimization |

---

## E. Level Selection Issues (4 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| AT-VAL19 | Filter: Targets where L1 just missed qualification (Spend slightly < Price) | Compare L1 vs L2 CVR | Threshold sensitivity |
| AT-VAL20 | Filter: Targets using L4/L5 despite having Search Term data | Why didn't L3 qualify? | May be missing data |
| AT-VAL21 | Filter: Targets where level changed recently | Performance before/after | Level transition impact |
| AT-VAL22 | Filter: High-spend targets still using L5 (Default) | Why no data at higher levels? | Cold start duration |

---

## F. Floor Multiplier Calibration (4 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| AT-VAL23 | Filter: L2 targets, compare actual CVR vs 0.75× Default | Is 0.75× appropriate? | Multiplier calibration |
| AT-VAL24 | Filter: L3a targets, compare actual CVR vs 0.5× Default | Is 0.5× appropriate? | May be too low/high |
| AT-VAL25 | Filter: Targets where floor dominated at each level | Frequency of floor usage | Over-reliance on defaults |
| AT-VAL26 | Filter: Best/worst ACOS by level | Which level performs best? | Level accuracy comparison |

---

# SUMMARY

| Test Type | Count | Focus Area |
|-----------|-------|------------|
| **Type 1: Verification** | 32 | L1-L5 level selection, Floor multipliers, Split paths |
| **Type 2: Validation** | 26 | Raw CVR risk, Campaign matching, Path selection, Multiplier calibration |
| **TOTAL** | 58 | |

---

# Key Risk Areas for ASIN Targeting

| Risk | Description | Impact |
|------|-------------|--------|
| **L1 No Floor** | Raw CVR used, including CVR = 0% | Severe underbidding possible |
| **L2 Campaign Matching** | Relies on other targets' performance | May not reflect actual target |
| **L3 Split Path** | Different floors (0.5× vs 1×) | Path selection affects bid significantly |
| **0.75× Multiplier** | L2 floor assumption | May not fit all categories |
| **0.5× Multiplier** | L3a floor for spend-only | Very conservative for non-converters |

---

# Reference: Identical to Manual KW (See Manual KW Document)

The entire bid optimization formula is identical to Manual KW Targeting:

- Fixed Bid Override (V01-V04)
- Ceiling Logic (V05-V10)
- Floor Logic (V11-V16)
- ACOS Breach Detection (V17-V24)
- TOS% Increase Logic (V25-V31)
- TOS% Decrease Logic (V32-V35)
- Global Bounds (V36-V39)
- $0.19 Avoidance (V40-V42)
- Momentum S2/T2 (V43-V48)
- Ceiling-Floor Interaction (V49-V54)

Refer to `UAT_Bid_Optimization_Manual_KW.md` for all bid logic tests.
