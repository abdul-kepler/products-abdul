# UAT: Bid Optimization - Manual KW Targeting

## Overview

This document contains comprehensive test cases for the Bid Optimization logic used in Manual Keyword Targeting. Tests are divided into two types:

- **Type 1: Verification Tests** - "Is the system behaving as designed?"
- **Type 2: Validation Tests** - "Is the design achieving ACOS & Ad Sales goals?"

**Source Logic:** `Bid Logic_08 Sep'25` cell B4

---

## Variable Definitions

| Variable | Cell | Description |
|----------|------|-------------|
| Fixed Bid | A2 | Manual override bid |
| Fixed Bid Expiry | B2 | Expiry date for fixed bid |
| Ceiling Value | C2 | Manual ceiling cap |
| Ceiling Expiry | D2 | Expiry date for ceiling |
| Floor Value | E2 | Manual floor minimum |
| Floor Expiry | F2 | Expiry date for floor |
| Target ACOS | G2 | Target ACOS % |
| Current Bid | H2 | Current bid ($0.19 = AVOID marker) |
| Actual ACOS | I2 | Actual ACOS achieved |
| Spend | J2 | Ad spend |
| Price | K2 | Product price |
| Clicks | L2 | Click count |
| TOS% | M2 | Top of Search percentage |
| CVR | N2 | Conversion Rate (from waterfall) |
| Min Suggested Bid | O2 | Amazon's min suggested bid |
| Max Suggested Bid | P2 | Amazon's max suggested bid |
| Bid Before 0.19 | S2 | Last bid before ASIN+KW launched on our platform (ASIN+KW+MatchType level) - to continue momentum |
| Avg CPC Last 30d | T2 | Historic avg CPC (ASIN+SearchTerm level) - for existing KWs to continue momentum |

---

## Key Thresholds

| Threshold | Formula | Description |
|-----------|---------|-------------|
| ACOS Breach | I2 > G2 | ACOS exceeds Target |
| Spend Threshold | J2 > G2 × K2 | Spend > Target_ACOS × Price |
| Clicks Threshold | L2 > 20 | Clicks exceed 20 |
| TOS% Threshold | M2 < 50% | Below = increase bid, At/Above = decrease bid |
| CVR Cap | MIN(N2, 0.5) | 50% max CVR for calculations |
| Min Suggested Cap | MIN(O2, 0.5) | If Min Suggested < $0.50, use it; else use $0.50 |
| Global Min | 0.02 | $0.02 minimum bid |
| Global Max | 20 | $20.00 maximum bid |
| Avoid Marker | H2 = 0.19 | $0.19 triggers momentum continuation logic |

---

## TOS% Increase Formula (when TOS < 50%)

| Min Suggested Range | Increase Formula |
|---------------------|------------------|
| Blank | Bid × 1.15 |
| ≤ $1.00 | (MinSugg - 0.5)/2 + Bid |
| $1.01 - $2.00 | (MinSugg - 0.5)/3 + Bid |
| $2.01 - $3.00 | (MinSugg - 0.5)/4 + Bid |
| > $3.00 | (MinSugg - 0.5)/6 + Bid |
| Bid ≥ Min Suggested | Bid × 1.15 |

---

## CVR Waterfall Logic (Manual KW Targeting)

### Default CVR by Price Tier

| Price Range | Default CVR |
|-------------|-------------|
| K ≤ $25 | 15% |
| $25 < K ≤ $50 | 12.5% |
| $50 < K ≤ $100 | 10% |
| $100 < K ≤ $200 | 5% |
| K > $200 | 3% |

### Waterfall Levels

| Level | Granularity | Match Type | Floor Applied |
|-------|-------------|------------|---------------|
| L1 | ASIN + Search Term | Exact only | No (raw CVR) |
| L2 | ASIN + Keyword + Match Type | Broad/Phrase only | No (raw CVR) |
| L4 | ASIN + Campaign | All | Yes - MAX(Default, Calculated) |
| L5 | ASIN | All | Yes - MAX(Default, Calculated) |
| L6 | Default CVR | All | N/A (is the default) |

### Waterfall Thresholds
- **Lookback:** 60 days
- **Spend Threshold:** Spend ≥ Product Price
- **Orders Threshold:** Orders ≥ 1

---

# TYPE 1: VERIFICATION TESTS

*"Is the system behaving as designed?"*

## A. Fixed Bid Override (4 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| V01 | Filter: Fixed Bid ≠ blank AND Fixed Bid Expiry ≥ Today | Final Bid in Amazon = Fixed Bid value | Bid matches Fixed Bid exactly |
| V02 | Filter: Fixed Bid ≠ blank AND Fixed Bid Expiry < Today | Final Bid ≠ Fixed Bid value | Bid calculated, not using fixed |
| V03 | Filter: Fixed Bid ≠ blank AND Fixed Bid Expiry = blank | Final Bid ≠ Fixed Bid value | Bid calculated, not using fixed |
| V04 | Filter: Fixed Bid = blank | Final Bid calculated | No fixed bid override |

---

## B. Ceiling Logic (6 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| V05 | Filter: Manual Ceiling set AND Ceiling Expiry ≥ Today AND Current Bid was trending upward (TOS < 50%) | Final Bid ≤ Ceiling Value | Bid capped at manual ceiling |
| V06 | Filter: Manual Ceiling set AND Ceiling Expiry < Today | Final Bid may exceed old ceiling value | Manual ceiling no longer active |
| V07 | Filter: No Manual Ceiling (blank) AND high CVR product (>30%) AND favorable ACOS | Calculate: Price × Target_ACOS × MIN(CVR, 0.5). Final Bid should not exceed this | Effective ceiling applied |
| V08 | Filter: No Manual Ceiling AND CVR > 50% (from CVR waterfall) | Compare bid to: Price × Target_ACOS × 0.50 (not actual CVR) | CVR capped at 50% for ceiling calc |
| V09 | Filter: Manual Ceiling active AND Final Bid < Ceiling | Bid = calculated value (not ceiling) | Ceiling only caps, doesn't force |
| V10 | Filter: Ceiling Expiry = Today's date | Ceiling should still be active | Expiry is inclusive (>=TODAY) |

**Observable Output Method for V07:**
1. Find KWs where: Manual Ceiling = blank, ACOS is favorable, TOS < 50%
2. Note the Final Bid pushed to Amazon
3. Calculate: Product Price × Target ACOS × MIN(CVR, 0.50)
4. Final Bid should ≤ this calculated effective ceiling

---

## C. Floor Logic (6 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| V11 | Filter: Manual Floor set AND Floor Expiry ≥ Today AND ACOS unfavorable (system wants to decrease) | Final Bid ≥ Floor Value | Bid raised to manual floor |
| V12 | Filter: Manual Floor set AND Floor Expiry < Today AND ACOS unfavorable | Final Bid may go below old floor | Manual floor no longer active |
| V13 | Filter: No Manual Floor AND Min Suggested < $0.50 | Effective floor uses Min Suggested value | Floor = Min Suggested when < $0.50 |
| V14 | Filter: No Manual Floor AND Min Suggested ≥ $0.50 | Effective floor uses $0.50, not full Min Suggested | Min Suggested capped at $0.50 |
| V15 | Filter: No Manual Floor AND Min Suggested = blank | Effective floor calculation uses $0.50 default | Default cap applied |
| V16 | Filter: ACOS breach triggered (bid should be $0.02) AND No Manual Floor | Final Bid = $0.02 | Floor doesn't prevent breach response |

**Observable Output Method for V13-V14:**
1. Find KWs where: Manual Floor = blank, ACOS is unfavorable, system wants lower bid
2. Check Min Suggested value in Amazon data
3. If Min Suggested = $0.35 → Floor should be ~$0.35
4. If Min Suggested = $0.80 → Floor should be ~$0.50 (capped)

---

## D. ACOS Breach Detection (8 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| V17 | Filter: ACOS > Target ACOS AND Spend > (Target ACOS × Price) AND Clicks > 20 | Final Bid = $0.02 | Full breach, bid dropped |
| V18 | Filter: ACOS > Target ACOS AND Spend > (Target ACOS × Price) AND Clicks ≤ 20 | Final Bid = $0.02 | Spend threshold alone triggers |
| V19 | Filter: ACOS > Target ACOS AND Spend ≤ (Target ACOS × Price) AND Clicks > 20 | Final Bid = $0.02 | Clicks threshold alone triggers |
| V20 | Filter: ACOS > Target ACOS AND Spend ≤ (Target ACOS × Price) AND Clicks ≤ 20 | Final Bid ≠ $0.02 | No breach - thresholds not met |
| V21 | Filter: ACOS = Target ACOS (exactly) AND Spend exceeded AND Clicks exceeded | Final Bid ≠ $0.02 | No breach - ACOS not exceeded |
| V22 | Filter: ACOS < Target ACOS AND high spend/clicks | Final Bid ≠ $0.02 | No breach - ACOS favorable |
| V23 | Filter: Clicks = 20 exactly AND ACOS > Target AND Spend < threshold | Final Bid ≠ $0.02 | Clicks must EXCEED 20, not equal |
| V24 | Filter: Clicks = 21 AND ACOS > Target AND Spend < threshold | Final Bid = $0.02 | Clicks threshold met |

**How to Calculate Spend Threshold:**
- Spend Threshold = Target ACOS × Product Price
- Example: Target ACOS = 30%, Price = $50 → Threshold = $15

---

## E. TOS% Increase Logic - Below 50% (7 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| V25 | Filter: TOS < 50% AND Min Suggested = blank AND no ACOS breach | Compare: New Bid vs Previous Bid | New Bid = Previous × 1.15 (15% increase) |
| V26 | Filter: TOS < 50% AND Min Suggested ≤ $1.00 AND Previous Bid < Min Suggested | Calculate expected: (MinSugg - 0.5)/2 + PrevBid | Bid increase follows tier 1 formula |
| V27 | Filter: TOS < 50% AND Min Suggested between $1.01-$2.00 AND Previous Bid < Min Suggested | Calculate expected: (MinSugg - 0.5)/3 + PrevBid | Bid increase follows tier 2 formula |
| V28 | Filter: TOS < 50% AND Min Suggested between $2.01-$3.00 AND Previous Bid < Min Suggested | Calculate expected: (MinSugg - 0.5)/4 + PrevBid | Bid increase follows tier 3 formula |
| V29 | Filter: TOS < 50% AND Min Suggested > $3.00 AND Previous Bid < Min Suggested | Calculate expected: (MinSugg - 0.5)/6 + PrevBid | Bid increase follows tier 4 formula |
| V30 | Filter: TOS = 49% (just below threshold) | Bid should increase | 49% still triggers increase |
| V31 | Filter: TOS < 50% AND Previous Bid ≥ Min Suggested | New Bid = Previous × 1.15 | Falls back to 15% when bid already above min suggested |

---

## F. TOS% Decrease Logic - At/Above 50% (4 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| V32 | Filter: TOS ≥ 50% AND Previous Bid > $0.02 AND no ACOS breach | New Bid = Previous × 0.90 | 10% decrease applied |
| V33 | Filter: TOS = 50% (exactly at threshold) | Bid should decrease | 50% triggers decrease |
| V34 | Filter: TOS ≥ 50% AND Previous Bid = $0.02 | Bid uses effective floor | Can't decrease below floor |
| V35 | Filter: TOS = 100% (maximum) | New Bid = Previous × 0.90 | Same 10% decrease regardless of how high |

---

## G. Global Bounds (4 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| V36 | Filter: High-price item + high CVR + aggressive target ACOS (calculated bid would exceed $20) | Final Bid = $20.00 | Global max cap applied |
| V37 | Filter: ACOS breach triggered | Final Bid = $0.02 | Global min applied |
| V38 | Filter: Low price + low CVR + conservative target | Final Bid ≥ $0.02 | Never goes below global min |
| V39 | Filter: Sort by highest bids in portfolio | No bid > $20.00 | Global max enforced |

---

## H. $0.19 Avoidance (3 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| V40 | Filter: Final Bid in narrow range where calculation might land on $0.19 | Final Bid = $0.20 (not $0.19) | $0.19 avoided |
| V41 | Filter: Any bid at $0.18 | Bid = $0.18 (allowed) | $0.18 is valid |
| V42 | Filter: Any bid at $0.20 | Bid = $0.20 (allowed) | $0.20 is valid |

**Why $0.19 is avoided:** $0.19 is used as an internal "AVOID" marker in the system.

---

## I. Momentum Continuation Logic - S2 & T2 (6 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| V43 | Filter: Current Bid = $0.19 (AVOID marker) AND S2 (Bid Before 0.19) exists AND S2 < effective floor | Final Bid = effective floor | Floor overrides S2 |
| V44 | Filter: Current Bid = $0.19 AND S2 exists AND S2 within ceiling/floor range | Final Bid = S2 | Continues momentum with last bid |
| V45 | Filter: Current Bid = $0.19 AND S2 > effective ceiling AND T2 ≤ ceiling | Final Bid = T2 | Uses historic CPC when S2 too high |
| V46 | Filter: Current Bid = $0.19 AND S2 = blank AND T2 exists AND T2 ≤ ceiling | Final Bid = T2 | Uses historic CPC as fallback |
| V47 | Filter: Current Bid = $0.19 AND S2 > ceiling AND T2 > ceiling | Final Bid = effective ceiling | Both too high, caps at ceiling |
| V48 | Filter: Current Bid = $0.19 AND S2 = blank AND T2 = blank | Final Bid = effective floor | No history, starts at floor |

**Context:**
- S2 = Last bid before ASIN+KW was launched on our platform (ASIN+KW+MatchType level)
- T2 = Avg CPC last 30 days (ASIN+SearchTerm level)
- Goal: Continue momentum if bid is reasonable, don't start from scratch

---

## J. Ceiling-Floor Interaction (6 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| V49 | Filter: Manual Ceiling active AND Manual Floor active AND Ceiling > Floor | Bid constrained between floor and ceiling | MIN(ceiling, MAX(floor, bid)) |
| V50 | Filter: Manual Ceiling active AND Manual Floor active AND Ceiling < Floor (conflict) | Bid ≤ Ceiling (ceiling wins) | Ceiling takes priority in conflict |
| V51 | Filter: Manual Ceiling active AND No Manual Floor | Bid capped by ceiling, floored by effective floor | Hybrid constraint |
| V52 | Filter: No Manual Ceiling AND Manual Floor active AND effective ceiling < floor | Bid = Floor | Active floor enforced |
| V53 | Filter: No Manual Ceiling AND Manual Floor active AND effective ceiling > floor | Bid between floor and eff ceiling | Both constraints apply |
| V54 | Filter: No Manual Ceiling AND No Manual Floor | Bid between effective floor and ceiling | System-calculated bounds |

---

# TYPE 2: VALIDATION TESTS

*"Is the design achieving ACOS & Ad Sales goals?"*

## A. CVR Estimation Issues (7 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| VAL01 | Filter: Top 20 KWs by ACOS (worst performers) | Compare Estimated CVR vs Actual CVR (Orders/Clicks) | CVR overestimation → overbidding |
| VAL02 | Filter: Bottom 20 KWs by Spend (lowest spend, non-zero impressions) | Compare Estimated CVR vs Actual CVR from past data | CVR underestimation → underbidding |
| VAL03 | Filter: KWs where Spend dropped >50% vs prior period AND past ACOS was good | Check if CVR estimate dropped | Possible underestimation killing winners |
| VAL04 | Filter: KWs using CVR from L4/L5 (floored by default CVR) | Compare floored CVR vs actual KW performance | Floor may be inflating/deflating |
| VAL05 | Filter: Products with actual CVR > 50% | Check if bid uses 50% cap | High converters may be underbid |
| VAL06 | Filter: New ASINs using Default CVR (L6) | Compare Default CVR tier vs actual performance | Default may be wrong for category |
| VAL07 | Filter: KWs where bid = effective ceiling frequently | May indicate CVR too high | Ceiling constantly capping overbids |

---

## B. TOS% Threshold Issues (5 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| VAL08 | Filter: KWs where TOS crossed 50% recently AND Sales dropped >15% | Compare sales before/after threshold | 50% threshold too aggressive |
| VAL09 | Filter: KWs oscillating around 49-51% TOS | Check bid history for yo-yo pattern | Threshold causing instability |
| VAL10 | Filter: KWs with TOS > 50% AND ACOS favorable AND bid decreasing | Good performers being reduced | Missing sales opportunity |
| VAL11 | Filter: KWs with TOS < 30% for extended period | Check if increase rate is sufficient | May be underbidding chronically |
| VAL12 | Filter: KWs with Min Suggested > $3 AND TOS < 50% | Check increase rate: (MinSugg-0.5)/6 | Slowest tier may be too slow |

---

## C. ACOS Breach Response Issues (5 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| VAL13 | Filter: KWs where bid dropped to $0.02 AND Sales were >0 before | Compare sales before/after drop | Instant drop killing sales |
| VAL14 | Filter: KWs where ACOS exceeded target by <5% AND bid dropped to $0.02 | Check if response proportionate | Minor breach → major punishment |
| VAL15 | Filter: KWs where Spend = Target×Price ± 5% AND bid dropped | Check if threshold too sensitive | Edge cases triggering drops |
| VAL16 | Filter: KWs with Clicks = 21-25 AND bid = $0.02 AND no orders | Check conversion on clicks 22+ | Just missed conversions |
| VAL17 | Filter: KWs stuck at $0.02 for >30 days AND ACOS now favorable if re-enabled | Check recovery mechanism | No way back from breach |

---

## D. Fixed Bid/Ceiling Issues (4 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| VAL18 | Filter: KWs with Manual Ceiling AND TOS < 20% AND ACOS favorable | Ceiling may be too low | Underbidding good KWs |
| VAL19 | Filter: Manual Ceilings set >90 days ago | Check if still appropriate | Stale constraints |
| VAL20 | Filter: KWs where Manual Ceiling ≈ Manual Floor (within 10%) | Check bid flexibility | No room to optimize |
| VAL21 | Filter: Manual Fixed Bids expiring in next 7 days | Review if still needed | Upcoming changes |

---

## E. Fixed Floor Issues (4 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| VAL22 | Filter: KWs with Manual Floor AND ACOS > Target by >20% | Floor preventing reduction | Forced inefficiency |
| VAL23 | Filter: KWs where ACOS breach occurred but bid > $0.02 | Check if floor is blocking | Floor overriding safety |
| VAL24 | Filter: KWs where Min Suggested > $0.50 but bid < Min Suggested | System using $0.50 cap | May be underbidding |
| VAL25 | Filter: KWs where Final Bid = effective floor for >14 days | Floor may be dominating | No downside flexibility |

---

## F. Spend/Clicks Threshold Issues (4 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| VAL26 | Filter: High-price items ($100+) where spend threshold = $30+ | Takes long to breach | Delayed response |
| VAL27 | Filter: Low-price items ($10-) where spend threshold = $3- | Breaches quickly | Premature termination |
| VAL28 | Filter: KWs breached on clicks (>20) but spend was low | Check if conversion came later | Clicks threshold too low |
| VAL29 | Filter: KWs with Clicks = 18-22 range AND ACOS breach | Near-threshold sensitivity | Edge cases |

---

## G. Bid Increase Rate Issues (4 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| VAL30 | Filter: KWs with TOS < 30% for >21 days AND ACOS favorable | Check cumulative increase | Rate too slow |
| VAL31 | Filter: KWs where bid increased >50% in 7 days | Check if overshoot occurred | Rate too fast |
| VAL32 | Filter: KWs crossing Min Suggested tiers | Check for discontinuities | Tier jumps causing issues |
| VAL33 | Filter: Competitive KWs (high Min Suggested) with low TOS | Compare vs less competitive KWs | May need faster ramp |

---

## H. Momentum Continuation Issues - S2/T2 (3 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| VAL34 | Filter: Newly launched KWs (Current Bid was $0.19) where S2 was used | Compare performance vs starting fresh | S2 continuation helping/hurting |
| VAL35 | Filter: KWs where T2 (historic CPC) was used as starting bid | Check if CPC was appropriate | Historic CPC may be stale |
| VAL36 | Filter: KWs where S2/T2 both exceeded ceiling, started at ceiling | Check if ceiling was too restrictive | Missed momentum opportunity |

---

# SUMMARY

| Test Type | Count | Purpose |
|-----------|-------|---------|
| **Type 1: Verification** | 54 | Confirm system works as designed |
| **Type 2: Validation** | 36 | Find real issues affecting ACOS & Ad Sales |
| **TOTAL** | 90 | |

---

# Test Case Design Principles

Each test includes:
1. **How to Find** - Filter criteria to produce test cases from real data
2. **What to Observe** - Final bid output (not internal calculations)
3. **Pass Criteria / Issue if Found** - Clear success/failure definition

Tests are designed to be:
- **Producible** - Can find cases using filters on KW config
- **Observable** - Results visible in final bid pushed to Amazon
- **Actionable** - Clear pass/fail or issue identification
