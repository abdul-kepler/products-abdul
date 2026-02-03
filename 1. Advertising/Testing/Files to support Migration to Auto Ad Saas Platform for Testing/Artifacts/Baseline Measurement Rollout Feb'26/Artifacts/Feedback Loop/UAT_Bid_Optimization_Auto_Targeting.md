# UAT: Bid Optimization - Auto Targeting (Differences from Manual KW)

## Overview

This document contains test cases SPECIFIC to Auto Targeting that differ from Manual KW Targeting. For common tests (Fixed Bid, Ceiling, Floor, Global Bounds, $0.19 Avoidance, Momentum S2/T2, Ceiling-Floor Interaction), refer to `UAT_Bid_Optimization_Manual_KW.md`.

**Source Logic:** `Bid Logic_08 Sep'25` - Auto Targeting formula

---

## Key Differences: Auto vs Manual KW Targeting

| Aspect | Manual KW | Auto |
|--------|-----------|------|
| **Bid Adjustment Trigger** | TOS% (M2) with 50% threshold | Impressions (Q2) with 100/1000 thresholds |
| **Increase Logic** | TOS < 50% | Impressions < 100 |
| **Hold Logic** | None | Impressions 100-999 |
| **Decrease Logic** | TOS ≥ 50% → 10% decrease | Impressions ≥ 1000 → 10% decrease |
| **ACOS Breach** | YES - drops to $0.02 | **NO** - not present in formula |
| **CVR Lookback** | 60 days | 180 days |
| **CVR Levels** | L1→L2→L4→L5→L6 | L1→L2→L3 |
| **CVR Floor** | Default CVR at L4/L5 | ASIN CVR × Match Type Multiplier |
| **Match Type Adjustment** | None | Close=1.0, Loose=0.2, Substitute=0.7, Complement=0.2 |
| **Click-Tiered CVR** | None | Yes at L2 (<20, 20-99, ≥100 clicks) |

---

## New Variables (Auto-specific)

| Variable | Cell | Description |
|----------|------|-------------|
| Impressions (Last Day) | Q2 | Yesterday's impressions - replaces TOS% |
| Match Type | - | Close Match, Loose Match, Substitute, Complement |

---

## New Thresholds (Auto-specific)

| Threshold | Value | Action |
|-----------|-------|--------|
| Low Impressions | Q2 < 100 | Increase bid |
| Mid Impressions | 100 ≤ Q2 < 1000 | Hold bid (no change) |
| High Impressions | Q2 ≥ 1000 | Decrease bid by 10% |

---

## CVR Waterfall Logic (Auto Targeting)

### CVR Floor Definition

CVR Floor = ASIN Level CVR × Match Type Multiplier

| Match Type | Multiplier | Example (ASIN CVR = 10%) |
|------------|------------|--------------------------|
| Close Match | 1.0 (100%) | 10% |
| Loose Match | 0.2 (20%) | 2% |
| Substitute | 0.7 (70%) | 7% |
| Complement | 0.2 (20%) | 2% |

### Default CVR by Price Tier

| Price Range | Default CVR |
|-------------|-------------|
| K ≤ $25 | 15% |
| $25 < K ≤ $50 | 12.5% |
| $50 < K ≤ $100 | 10% |
| $100 < K ≤ $200 | 5% |
| K > $200 | 3% |

### Waterfall Hierarchy

**Level 1: ASIN + Match Type Level**
- Lookback: 180 days
- Check: Ad Orders ≥ 1 at ASIN + Match Type level
- If Yes: CVR = MAX(Calculated CVR, CVR_Floor)
  - CVR calculated from point where cumulative spend = Product Price
  - If CVR = 0: Use CVR from first order point
- If No: Proceed to L2

**Level 2: ASIN Level (Click-Tiered)**
- Lookback: 180 days
- Check: Ad Orders ≥ 1 at ASIN level
- If Yes: CVR based on clicks at ASIN + Match Type level:

| Clicks (ASIN+MatchType) | CVR Formula | Rationale |
|-------------------------|-------------|-----------|
| < 20 clicks | CVR_Floor × 1.5 | Exploration boost |
| 20-99 clicks | CVR_Floor | Standard floor |
| ≥ 100 clicks | MIN(CVR_Floor, 1/clicks × 1.5) | Taper if no conversion |

- If No: Proceed to L3

**Level 3: Default Level**
- Fallback: Use Default CVR (price-based)

---

# TYPE 1: VERIFICATION TESTS (Auto-specific)

## A. Impressions-Based Bid Adjustment (7 tests)

*Replaces TOS% logic from Manual KW*

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| A-V01 | Filter: Impressions (yesterday) < 100 AND Min Suggested = blank | Compare: New Bid vs Previous Bid | New Bid = Previous × 1.15 (15% increase) |
| A-V02 | Filter: Impressions < 100 AND Min Suggested ≤ $1.00 AND Bid < Min Suggested | Calculate: (MinSugg - 0.5)/2 + PrevBid | Tier 1 increase formula |
| A-V03 | Filter: Impressions < 100 AND Min Suggested > $3.00 AND Bid < Min Suggested | Calculate: (MinSugg - 0.5)/6 + PrevBid | Tier 4 increase formula |
| A-V04 | Filter: Impressions = 99 (just below threshold) | Bid should increase | 99 still triggers increase |
| A-V05 | Filter: Impressions between 100-999 | New Bid = Previous Bid (unchanged) | Hold zone - no adjustment |
| A-V06 | Filter: Impressions = 100 (exactly at threshold) | New Bid = Previous Bid | 100 triggers hold, not increase |
| A-V07 | Filter: Impressions ≥ 1000 | New Bid = Previous × 0.90 | 10% decrease applied |

**Key Difference from Manual KW:** There's a "hold zone" (100-999 impressions) where bid stays unchanged. Manual KW has no hold zone.

---

## B. No ACOS Breach Logic (4 tests)

*CRITICAL: Auto targeting does NOT have ACOS breach → $0.02 drop*

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| A-V08 | Filter: ACOS > Target ACOS AND Spend > (Target × Price) AND Clicks > 20 | Final Bid ≠ $0.02 | No breach drop in Auto |
| A-V09 | Filter: ACOS significantly > Target (e.g., 2x) | Bid adjusted by impressions logic only | ACOS doesn't force $0.02 |
| A-V10 | Filter: High ACOS + Low Impressions (<100) | Bid may INCREASE despite bad ACOS | Impressions override ACOS |
| A-V11 | Filter: High ACOS + High Impressions (≥1000) | Bid decreases 10% (not to $0.02) | Gradual decrease only |

**Why this matters:** Auto targets can continue spending even with very poor ACOS - the only brake is the 10% decrease at ≥1000 impressions.

---

## C. CVR Floor - Match Type Multipliers (5 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| A-V12 | Filter: Match Type = Close Match | CVR Floor = ASIN CVR × 1.0 | No discount applied |
| A-V13 | Filter: Match Type = Loose Match | CVR Floor = ASIN CVR × 0.2 | 80% discount applied |
| A-V14 | Filter: Match Type = Substitute | CVR Floor = ASIN CVR × 0.7 | 30% discount applied |
| A-V15 | Filter: Match Type = Complement | CVR Floor = ASIN CVR × 0.2 | 80% discount applied |
| A-V16 | Filter: Same ASIN, different Match Types | Compare CVR Floors across types | Should differ by multiplier |

**Example Calculation:**
- ASIN CVR = 10%
- Close Match CVR Floor = 10% × 1.0 = 10%
- Loose Match CVR Floor = 10% × 0.2 = 2%
- Substitute CVR Floor = 10% × 0.7 = 7%
- Complement CVR Floor = 10% × 0.2 = 2%

---

## D. CVR Waterfall - L1: ASIN + Match Type Level (6 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| A-V17 | Filter: Auto target with Orders ≥ 1 at ASIN+MatchType level (180 days) | Uses L1 CVR | L1 level selected |
| A-V18 | Filter: L1 data exists, calculated CVR < CVR Floor | CVR = CVR Floor | Floor applied at L1 |
| A-V19 | Filter: L1 data exists, calculated CVR > CVR Floor | CVR = Calculated CVR | MAX(calc, floor) |
| A-V20 | Filter: L1 with cumulative spend reaching price at Day X | CVR calculated from Day X period | Spend threshold logic |
| A-V21 | Filter: L1 with CVR = 0 at spend threshold | CVR from first order point | Zero CVR fallback |
| A-V22 | Filter: Data from Day 181 (outside lookback) | Excluded from L1 | 180-day boundary |

**Lookback Difference:** Auto uses 180 days vs Manual KW's 60 days.

---

## E. CVR Waterfall - L2: Click-Tiered Formula (6 tests)

*Unique to Auto targeting - uses clicks to tier CVR*

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| A-V23 | Filter: No L1 data, Orders ≥ 1 at ASIN level, Clicks < 20 at ASIN+MatchType | CVR = CVR Floor × 1.5 | Low clicks = aggressive CVR |
| A-V24 | Filter: Same as above, Clicks = 19 | CVR = CVR Floor × 1.5 | Boundary test |
| A-V25 | Filter: Same criteria, Clicks 20-99 at ASIN+MatchType | CVR = CVR Floor | Mid clicks = floor CVR |
| A-V26 | Filter: Same criteria, Clicks = 20 exactly | CVR = CVR Floor | 20 is mid tier, not low |
| A-V27 | Filter: Same criteria, Clicks ≥ 100 at ASIN+MatchType | CVR = MIN(CVR Floor, 1/clicks × 1.5) | High clicks formula |
| A-V28 | Filter: Clicks = 100, CVR Floor = 5% | CVR = MIN(5%, 1/100 × 1.5) = MIN(5%, 1.5%) = 1.5% | Formula verification |

**L2 Click-Tiered CVR Summary:**

| Clicks (ASIN+MatchType) | CVR Formula | Rationale |
|-------------------------|-------------|-----------|
| < 20 | CVR_Floor × 1.5 | Exploration boost |
| 20-99 | CVR_Floor | Standard floor |
| ≥ 100 | MIN(CVR_Floor, 1/clicks × 1.5) | Taper down if no conversion |

---

## F. CVR Waterfall - L3: Default Level (2 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| A-V29 | Filter: No Orders at ASIN+MatchType (L1) AND No Orders at ASIN (L2) | Uses Default CVR by price | Falls to L3 |
| A-V30 | Filter: New ASIN, no historical data | Default CVR applied | Cold start handled |

---

# TYPE 2: VALIDATION TESTS (Auto-specific)

## A. Impressions Threshold Issues (6 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| A-VAL01 | Filter: Targets stuck at <100 impressions for >14 days despite bid increases | Check if 100 threshold too high | Can't break into auction |
| A-VAL02 | Filter: Targets with 100-500 impressions AND poor ACOS | Bid held despite inefficiency | Hold zone causing losses |
| A-VAL03 | Filter: Targets crossing 1000 impressions AND sales dropped >20% | Check sales before/after decrease | 1000 threshold too aggressive |
| A-VAL04 | Filter: Targets oscillating around 99-101 impressions | Check bid yo-yo pattern | Threshold causing instability |
| A-VAL05 | Filter: Targets with 900-1000 impressions AND favorable ACOS | About to decrease good performer | Missing opportunity |
| A-VAL06 | Filter: High-performing targets that dropped after crossing 1000 | Compare performance trajectory | 10% decrease hurt winners |

---

## B. No ACOS Breach Safety Issues (5 tests)

*CRITICAL: Auto has no emergency brake on runaway ACOS*

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| A-VAL07 | Filter: Auto targets with ACOS > 2× Target for >7 days | Total wasted spend | No kill switch causing losses |
| A-VAL08 | Filter: Auto targets where ACOS > Target but Impressions < 100 | Bid increasing on losers | Inverse of desired behavior |
| A-VAL09 | Filter: Auto targets with >$100 spend and 0 orders | Continued bleeding | No spend threshold protection |
| A-VAL10 | Filter: Compare ACOS distribution: Auto vs Manual KW | Auto may have worse tail | Missing breach logic impact |
| A-VAL11 | Filter: Auto targets where manual intervention was needed | Cases system couldn't handle | Design gap identification |

---

## C. Match Type Multiplier Issues (5 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| A-VAL12 | Filter: Loose Match targets with actual CVR > 20% of ASIN CVR | Multiplier too conservative | Underbidding on converters |
| A-VAL13 | Filter: Loose Match targets with actual CVR < 10% of ASIN CVR | Multiplier too aggressive | Overbidding on poor match |
| A-VAL14 | Filter: Complement targets with strong performance | 20% multiplier may be wrong | Category-specific variance |
| A-VAL15 | Filter: Substitute targets vs Close Match, same ASIN | Compare actual CVR ratios | Is 70% accurate? |
| A-VAL16 | Filter: Top ACOS targets by Match Type | Which type has worst ACOS? | Multiplier calibration needed |

---

## D. Click-Tiered CVR Issues (5 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| A-VAL17 | Filter: Targets with < 20 clicks AND high ACOS | 1.5× multiplier causing overbid | Exploration too aggressive |
| A-VAL18 | Filter: Targets with 20-99 clicks AND low spend (underbidding) | CVR Floor may be too low | Missing sales opportunity |
| A-VAL19 | Filter: Targets with ≥ 100 clicks AND 0 orders | Check if 1/clicks × 1.5 is reasonable | High click, no convert |
| A-VAL20 | Filter: Targets crossing 20 or 100 click thresholds recently | Check bid discontinuity | Tier jumps causing issues |
| A-VAL21 | Filter: Targets with 100+ clicks where CVR Floor > 1/clicks × 1.5 | CVR dropped significantly | May be underbidding now |

---

## E. 180-Day Lookback Issues (4 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| A-VAL22 | Filter: Seasonal products with 180-day CVR different from recent 30-day | Check bid accuracy | Stale data impact |
| A-VAL23 | Filter: Products with price changes in last 180 days | CVR may be from old price point | Threshold mismatch |
| A-VAL24 | Filter: Products with listing changes (images, bullets) in last 180 days | Historic CVR may not reflect current | Stale conversion data |
| A-VAL25 | Filter: Compare CVR accuracy: 180-day vs 60-day lookback | Which predicts better? | Lookback optimization |

---

## F. L2 Fallback Issues (3 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| A-VAL26 | Filter: Targets using L2 (ASIN level) where actual CVR differs significantly | L2 generalization error | ASIN CVR ≠ Target CVR |
| A-VAL27 | Filter: Targets where L1 has 0 orders but L2 used | Check if L1 should have qualified | Premature fallback |
| A-VAL28 | Filter: New Match Types for established ASINs using L2 | Performance vs L2 prediction | Cold start for match type |

---

# SUMMARY

| Test Type | Count | Focus Area |
|-----------|-------|------------|
| **Type 1: Verification** | 30 | Impressions logic, No ACOS breach, Match Type multipliers, Click-tiered CVR |
| **Type 2: Validation** | 28 | Threshold calibration, Missing safety, Multiplier accuracy, Lookback staleness |
| **TOTAL** | 58 | |

---

# Critical Design Differences to Monitor

| Risk | Auto Targeting | Manual KW |
|------|---------------|-----------|
| **Runaway ACOS** | HIGH - No $0.02 kill switch | LOW - Breach drops to $0.02 |
| **Slow Response** | MEDIUM - Hold zone delays action | LOW - Always adjusting |
| **CVR Accuracy** | MEDIUM - Match type assumptions | MEDIUM - Level assumptions |
| **Exploration Cost** | HIGH - 1.5× boost on low clicks | MEDIUM - Default CVR only |

---

# Reference: Common Tests (See Manual KW Document)

The following test categories apply equally to Auto Targeting - refer to `UAT_Bid_Optimization_Manual_KW.md`:

- Fixed Bid Override (V01-V04)
- Ceiling Logic (V05-V10) - same effective_ceiling formula
- Floor Logic (V11-V16) - same effective_floor formula
- Global Bounds (V36-V39)
- $0.19 Avoidance (V40-V42)
- Momentum Continuation S2/T2 (V43-V48)
- Ceiling-Floor Interaction (V49-V54)
