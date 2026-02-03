# UAT Master Summary: Ad SaaS Platform Features

**Document Purpose:** Consolidated summary of all features, their logic, and test coverage
**Last Updated:** January 2026
**Total Features:** 11
**Total Test Cases:** 1,200+

---

## Table of Contents

1. [Auto Budget Management](#1-auto-budget-management)
2. [Bid Optimization - Manual KW Targeting](#2-bid-optimization---manual-kw-targeting)
3. [Bid Optimization - Auto Targeting](#3-bid-optimization---auto-targeting)
4. [Bid Optimization - ASIN Targeting](#4-bid-optimization---asin-targeting)
5. [Automated Harvesting](#5-automated-harvesting)
6. [Automated Negation](#6-automated-negation)
7. [Intelligent Pacing](#7-intelligent-pacing)
8. [High Performers Isolation](#8-high-performers-isolation)
9. [Automated KW Research](#9-automated-kw-research)
10. [Automated Target ASIN Research](#10-automated-target-asin-research)
11. [Automated Campaign Generation](#11-automated-campaign-generation)

---

# 1. Auto Budget Management

**UAT Document:** `UAT_Auto_Budget.md`
**Tests:** 183 (Verification + Validation)

## What It Does
Automatically calculates and distributes the ASIN-level daily budget across all active campaigns based on performance metrics, campaign maturity, and spend efficiency.

## How It Works

```
ASIN Daily Budget (User Input)
        ↓
┌───────────────────────────────────────────────────────────────┐
│  STEP 1: CLASSIFY CAMPAIGNS                                   │
│  • Immature: Ad_Spend_30d ≤ 5% of ASIN Spend                 │
│  • Fixed: User-set fixed budget                               │
│  • No Activity: No Spend AND No Sales                         │
│  • Normal: Has performance data to evaluate                   │
└───────────────────────────────────────────────────────────────┘
        ↓
┌───────────────────────────────────────────────────────────────┐
│  STEP 2: ENFORCE MINIMUM BUDGET ($5)                          │
│  Each campaign gets at least $5 minimum                       │
└───────────────────────────────────────────────────────────────┘
        ↓
┌───────────────────────────────────────────────────────────────┐
│  STEP 3: IDENTIFY WINNERS & LOSERS                            │
│  • Winner: ACOS ≤ Target ACOS                                │
│  • Loser: ACOS > Target ACOS                                 │
└───────────────────────────────────────────────────────────────┘
        ↓
┌───────────────────────────────────────────────────────────────┐
│  STEP 4: REDISTRIBUTE BUDGET                                  │
│  • Losers: Reduce share (max 20% drop)                        │
│  • Winners: Boost share based on efficiency                   │
└───────────────────────────────────────────────────────────────┘
        ↓
    Push to Amazon
```

## Key Formulas

| Formula | Purpose |
|---------|---------|
| `Is_Immature = Campaign_Spend_30d ≤ ASIN_Spend_30d × 5%` | Identify new campaigns |
| `Loser_Drop = MIN(\|ACOS_Delta\|/2 + (1-Spend_Ratio)/4, 0.2)` | Cap reduction at 20% |
| `Winner_Boost = (1/ACOS) × Spend_Ratio` | Higher efficiency = more budget |
| `Final_Budget = Minimum + Post_Reduction + Boost_Allocation` | Combined calculation |

## Test Case Mapping

| Logic Area | Verification Tests | Validation Tests |
|------------|-------------------|------------------|
| Campaign Classification | Verify immature detection at 5% threshold | Boundary: Exactly 5% spend |
| Minimum Budget | Verify $5 minimum enforced | Edge: Budget less than $5 total |
| Winner/Loser Detection | Verify ACOS vs Target comparison | Boundary: ACOS = Target exactly |
| Budget Redistribution | Verify losers lose max 20% | Large ASIN with 50+ campaigns |
| Boost Calculation | Verify winners get proportional boost | All campaigns are losers scenario |

---

# 2. Bid Optimization - Manual KW Targeting

**UAT Document:** `UAT_Bid_Optimization_Manual_KW.md`
**Tests:** ~80 (Verification + Validation)

## What It Does
Automatically adjusts keyword bids to achieve Target ACOS while maximizing ad sales. Uses Top-of-Search (TOS%) as the primary signal for bid direction.

## How It Works

```
┌───────────────────────────────────────────────────────────────┐
│  INPUT: Current Bid, Target ACOS, Actual ACOS, TOS%, CVR     │
└───────────────────────────────────────────────────────────────┘
        ↓
┌───────────────────────────────────────────────────────────────┐
│  CHECK 1: Fixed Bid Override                                  │
│  If Fixed Bid set AND not expired → Use Fixed Bid            │
└───────────────────────────────────────────────────────────────┘
        ↓
┌───────────────────────────────────────────────────────────────┐
│  CHECK 2: ACOS Breach Detection                               │
│  If ACOS > Target AND Spend > Target×Price AND Clicks > 20   │
│  → Drop bid to $0.02 (emergency brake)                        │
└───────────────────────────────────────────────────────────────┘
        ↓
┌───────────────────────────────────────────────────────────────┐
│  CHECK 3: TOS% Direction                                      │
│  TOS < 50% → Increase bid (tiered by Min Suggested Bid)      │
│  TOS ≥ 50% → Decrease bid by 10%                             │
└───────────────────────────────────────────────────────────────┘
        ↓
┌───────────────────────────────────────────────────────────────┐
│  APPLY BOUNDS                                                 │
│  • Ceiling: Manual OR Price × Target_ACOS × CVR(capped 50%)  │
│  • Floor: Manual OR MIN(Min_Suggested, $0.50)                │
│  • Global: $0.02 min, $20.00 max                              │
└───────────────────────────────────────────────────────────────┘
```

## Key Thresholds

| Threshold | Value | Action |
|-----------|-------|--------|
| ACOS Breach | ACOS > Target AND Spend > Target×Price AND Clicks > 20 | Bid → $0.02 |
| TOS Threshold | 50% | Below = increase, At/Above = decrease |
| CVR Cap | 50% | Max CVR used in calculations |
| Global Min | $0.02 | Absolute minimum bid |
| Global Max | $20.00 | Absolute maximum bid |

## CVR Waterfall (60-day lookback)

```
L1: ASIN + Search Term (Exact only) → Raw CVR
    ↓ (if no data)
L2: ASIN + Keyword + Match Type → Raw CVR
    ↓ (if no data)
L4: ASIN + Campaign → MAX(Calculated, Default)
    ↓ (if no data)
L5: ASIN Level → MAX(Calculated, Default)
    ↓ (if no data)
L6: Default CVR by Price Tier
```

## Test Case Mapping

| Logic Area | Verification Tests | Validation Tests |
|------------|-------------------|------------------|
| Fixed Bid Override | Verify fixed bid used when active | Expiry date boundary |
| ACOS Breach | Verify $0.02 drop when all conditions met | Boundary: Exactly 20 clicks |
| TOS% Direction | Verify increase below 50%, decrease at/above | Boundary: TOS = 50% exactly |
| Ceiling Logic | Verify bid capped at ceiling | CVR > 50% capped scenario |
| Floor Logic | Verify bid not below floor | Min Suggested < $0.50 |
| CVR Waterfall | Verify correct level selection | All levels empty fallback |

---

# 3. Bid Optimization - Auto Targeting

**UAT Document:** `UAT_Bid_Optimization_Auto_Targeting.md`
**Tests:** ~60 (Verification + Validation)

## What It Does
Adjusts bids for Auto Targeting campaigns (Close Match, Loose Match, Substitute, Complement) using **Impressions** instead of TOS% as the primary signal.

## How It Works (Key Differences from Manual KW)

| Aspect | Manual KW | Auto Targeting |
|--------|-----------|----------------|
| Direction Signal | TOS% (50% threshold) | Impressions (100/1000 thresholds) |
| ACOS Breach | YES → $0.02 | **NO** - not present |
| CVR Lookback | 60 days | 180 days |
| Hold Zone | None | Impressions 100-999 |

```
┌───────────────────────────────────────────────────────────────┐
│  IMPRESSIONS-BASED BID ADJUSTMENT                             │
│                                                               │
│  Impressions < 100      → INCREASE bid (tiered formula)      │
│  Impressions 100-999    → HOLD bid (no change)               │
│  Impressions ≥ 1000     → DECREASE bid by 10%                │
└───────────────────────────────────────────────────────────────┘
```

## Match Type CVR Multipliers

| Match Type | Multiplier | Example (ASIN CVR = 10%) |
|------------|------------|--------------------------|
| Close Match | 1.0 (100%) | 10% |
| Loose Match | 0.2 (20%) | 2% |
| Substitute | 0.7 (70%) | 7% |
| Complement | 0.2 (20%) | 2% |

## Test Case Mapping

| Logic Area | Verification Tests | Validation Tests |
|------------|-------------------|------------------|
| Impressions Logic | Verify increase at <100, hold at 100-999 | Boundary: Exactly 100 impressions |
| No ACOS Breach | Verify bid ≠ $0.02 even with bad ACOS | High ACOS + Low Impressions scenario |
| Match Type Multipliers | Verify CVR floor calculation per type | Same ASIN, different match types |
| Hold Zone | Verify no change in 100-999 range | Edge: 999 impressions |

---

# 4. Bid Optimization - ASIN Targeting

**UAT Document:** `UAT_Bid_Optimization_ASIN_Targeting.md`
**Tests:** ~50 (Verification + Validation)

## What It Does
Optimizes bids for ASIN Targeting campaigns where ads appear on competitor product pages. Bid logic is **identical to Manual KW**, but CVR Waterfall is unique.

## How It Works
- **Bid Logic:** Same as Manual KW (TOS%, ACOS Breach, etc.)
- **CVR Waterfall:** Unique 5-level hierarchy with different floor multipliers
- **Search Term:** In ASIN Targeting, the "search term" IS a 10-digit ASIN (competitor product page)

## CVR Waterfall (180-day lookback)

| Level | Granularity | Floor Multiplier |
|-------|-------------|------------------|
| L1 | ASIN + Search Term (where ST = ASIN) | None (raw CVR) |
| L2 | Campaign Target-Matched Search Term | 0.75 × Default |
| L3a | Search Term (Spend path) | 0.5 × Default |
| L3b | Search Term (Orders path) | 1.0 × Default |
| L4 | ASIN Level | 1.0 × Default |
| L5 | Default CVR | N/A |

## Test Case Mapping

| Logic Area | Verification Tests | Validation Tests |
|------------|-------------------|------------------|
| L1 Selection | Verify ASIN+ST level used when qualified | 180-day boundary |
| L2 Campaign Match | Verify other campaign targets checked | Multiple matched search terms |
| L3 Split Path | Verify 0.5× for spend, 1.0× for orders | Zero orders with spend |
| Floor Application | Verify correct multiplier per level | CVR < floor scenario |

---

# 5. Automated Harvesting

**UAT Document:** `UAT_Harvesting.md`
**Tests:** ~50 (Verification + Validation)

## What It Does
Identifies high-performing search terms from discovery campaigns (Broad, Phrase, Auto) and promotes them to targeted campaigns for better control and optimization.

## How It Works

```
┌───────────────────────────────────────────────────────────────┐
│  HARVESTING CRITERIA                                          │
│                                                               │
│  MAX(ACoS_7d, ACoS_15d, ACoS_30d, ACoS_90d) ≤ Target_ACoS    │
│  AND                                                          │
│  Lifetime_Ad_Spend(ASIN + Search_Term) ≥ ASIN's Price        │
└───────────────────────────────────────────────────────────────┘
        ↓
┌───────────────────────────────────────────────────────────────┐
│  ROUTING RULES                                                │
│                                                               │
│  Phrase Match → Exact + Phrase (same relevancy group)        │
│  Broad Match  → Dedicated Harvesting Campaign (-HV suffix)   │
│  Auto (KW)    → Dedicated Harvesting Campaign (-HV suffix)   │
│  Auto (ASIN)  → ASIN Targeting Campaign (brand group)        │
└───────────────────────────────────────────────────────────────┘
```

## Key Rules

| Rule | Description |
|------|-------------|
| Target ACOS | ASIN-level if available, else Global |
| Zero-Sales | ACoS = 9999 → auto-fails harvesting |
| Trigger | Every 24 hours |
| Harvesting Campaign | Starts PAUSED, requires manual activation |

## Test Case Mapping

| Logic Area | Verification Tests | Validation Tests |
|------------|-------------------|------------------|
| Qualification | Verify MAX(ACoS) ≤ Target AND Spend ≥ Price | Boundary: ACoS_7d > Target but ACoS_30d ≤ |
| Phrase Routing | Verify added to Exact + Phrase campaigns | Missing Exact campaign scenario |
| Broad/Auto Routing | Verify dedicated -HV campaign created | First harvest for ASIN |
| ASIN Harvesting | Verify 10-digit ASIN routed to ASIN Targeting | Brand lookup via Keepa |

---

# 6. Automated Negation

**UAT Document:** `UAT_Negation.md`
**Tests:** ~50 (Verification + Validation)

## What It Does
Identifies underperforming search terms and adds them as negative keywords to stop wasting ad spend on non-converting or high-ACOS traffic.

## How It Works

```
┌───────────────────────────────────────────────────────────────┐
│  NEGATION CRITERIA                                            │
│                                                               │
│  MIN(ACoS_7d, ACoS_15d, ACoS_30d, ACoS_90d) > Target_ACoS    │
│  AND                                                          │
│  Lifetime_Ad_Spend(ASIN + Search_Term) ≥ ASIN's Price        │
└───────────────────────────────────────────────────────────────┘
        ↓
┌───────────────────────────────────────────────────────────────┐
│  TRIGGERS                                                     │
│                                                               │
│  #1: Scheduled     - Every 3 hours                           │
│  #2: Manual Override - Immediate                              │
│  #3: Target ACOS Update - Immediate re-evaluation            │
└───────────────────────────────────────────────────────────────┘
```

## Key Difference from Harvesting

| Feature | Function | Implication |
|---------|----------|-------------|
| Harvesting | `MAX(ACoS) ≤ Target` | Best case must be good |
| Negation | `MIN(ACoS) > Target` | Worst case must be bad |

## Manual Override Precedence

```
Manual = "Negative"      → Always negate (system won't override)
Manual = "Not Negative"  → Never negate (system won't override)
Manual = Empty           → System logic applies
```

## Test Case Mapping

| Logic Area | Verification Tests | Validation Tests |
|------------|-------------------|------------------|
| Qualification | Verify MIN(ACoS) > Target AND Spend ≥ Price | Boundary: One period ≤ Target |
| Zero-Sales | Verify auto-qualifies for negation | Spend = Price exactly |
| Manual Override | Verify user setting takes precedence | Clear override scenario |
| Reversal | Verify negation removed when no longer qualifies | ACOS improves over time |

---

# 7. Intelligent Pacing

**UAT Document:** `UAT_Pacing.md`
**Tests:** ~60 (Verification + Validation)

## What It Does
Automatically determines **which campaigns to activate** and **how much budget to allocate** to maximize ad sales within ACOS constraints using ML-based projection and knapsack optimization.

## How It Works

```
┌───────────────────────────────────────────────────────────────┐
│  PROJECTION ENGINE                                            │
│  • CVR Estimation (ML Model)                                  │
│  • CTR Waterfall (3d → 180d)                                 │
│  • Impression Share Heuristic (multi-factor)                 │
│                     ↓                                         │
│  Output: Projected Spend, Sales, ACOS per Campaign           │
└───────────────────────────────────────────────────────────────┘
        ↓
┌───────────────────────────────────────────────────────────────┐
│  BUDGET OPTIMIZER                                             │
│  • Filter: Projected ACOS ≤ Target ACOS                      │
│  • Knapsack Solver: Maximize sales within budget constraint  │
│                     ↓                                         │
│  Output: Selected Campaigns to Activate                       │
└───────────────────────────────────────────────────────────────┘
        ↓
┌───────────────────────────────────────────────────────────────┐
│  EXECUTION ENGINE                                             │
│  • Selected → ACTIVE                                          │
│  • Non-selected → PAUSED                                      │
└───────────────────────────────────────────────────────────────┘
```

## Feasibility Scoring Dimensions

| Dimension | Components |
|-----------|------------|
| Account Readiness | Ad history, indexing maturity, CTR benchmarks |
| ASIN Readiness | Review count, rating quality, CVR performance |
| Competitiveness | CPC levels, keyword saturation |
| Win Probability | Likelihood of hitting target ACOS |

## Test Case Mapping

| Logic Area | Verification Tests | Validation Tests |
|------------|-------------------|------------------|
| Projection | Verify CVR estimation accuracy | New ASIN with no history |
| ACOS Filter | Verify campaigns above Target excluded | Boundary: Projected = Target exactly |
| Knapsack | Verify sales maximization within budget | Budget constraint binding |
| Execution | Verify state changes pushed to Amazon | API failure handling |

---

# 8. High Performers Isolation

**UAT Document:** `UAT_Isolation.md`
**Tests:** ~50 (Verification + Validation)

## What It Does
Identifies top-performing search terms and promotes them to dedicated "solo" campaigns for greater control, better optimization, and reduced cannibalization.

## How It Works

```
┌───────────────────────────────────────────────────────────────┐
│  HIGH PERFORMER CRITERIA (ALL must be met)                    │
│                                                               │
│  1. Top 5% Rank by Ad Sales (30D)                            │
│     • If 5% < 5 terms → use that count                       │
│     • If 5% > 5 terms → cap at TOP 5                         │
│                                                               │
│  2. MAX(ACoS_1d, 3d, 7d, 15d, 30d) ≤ Campaign Target ACOS   │
│                                                               │
│  3. Ad_Orders_30d (ASIN-level) ≥ 100                         │
└───────────────────────────────────────────────────────────────┘
        ↓
┌───────────────────────────────────────────────────────────────┐
│  SOLO CAMPAIGN CREATION                                       │
│  • KW Search Terms → Solo SPKW Exact Campaign                │
│  • ASIN Search Terms → Solo ASIN Targeting Campaign          │
│  • Default State: PAUSED (manual activation required)        │
└───────────────────────────────────────────────────────────────┘
        ↓
┌───────────────────────────────────────────────────────────────┐
│  AUTO-PAUSE MECHANISM (on solo activation)                    │
│  • Find exact match KWs matching high-performer              │
│  • In other campaigns (same ASIN)                            │
│  • Auto-pause those KWs                                      │
│  • Preserve manually paused KWs                              │
└───────────────────────────────────────────────────────────────┘
```

## Trigger Frequency

| Trigger | Frequency |
|---------|-----------|
| High Performer Filtering | Every 7 days |
| Solo Campaign Creation | On qualification |
| Keyword Auto-Pause | On solo activation |
| Keyword Auto-Enable | On solo deactivation |

## Test Case Mapping

| Logic Area | Verification Tests | Validation Tests |
|------------|-------------------|------------------|
| Top 5% Rank | Verify ranking calculation | Edge: Exactly 5% = 5 terms |
| ACOS Consistency | Verify MAX across all periods | One period exceeds Target |
| Order Volume | Verify ASIN Orders ≥ 100 | Boundary: Exactly 100 orders |
| Auto-Pause | Verify exact KWs paused | Phrase/Broad not affected |
| Auto-Enable | Verify KWs re-enabled on deactivation | Manual pause preserved |

---

# 9. Automated KW Research

**UAT Document:** `UAT_Automated_KW_Research.md`
**Tests:** 141 (86 Verification + 55 Validation)

## What It Does
Automatically discovers and classifies relevant keywords for each ASIN using AI (OpenAI GPT-4) to analyze product listings and generate organized keyword groups with relevance tags.

## How It Works

```
┌───────────────────────────────────────────────────────────────┐
│  TRIGGER                                                      │
│  • ASIN ENABLED via ASIN Config for first time               │
│  • Every 30 days (automatic refresh)                          │
│  • Manual trigger via UI                                      │
└───────────────────────────────────────────────────────────────┘
        ↓
┌───────────────────────────────────────────────────────────────┐
│  STEP 1: FETCH PDP CONTENT                                    │
│  • Product Title, Bullet Points, Description                 │
│  • Backend Keywords (if available)                            │
│  • Brand Name, Category                                       │
└───────────────────────────────────────────────────────────────┘
        ↓
┌───────────────────────────────────────────────────────────────┐
│  STEP 2: PROMPT #1 - BRANDING SCOPE                          │
│  AI determines:                                               │
│  • NB (Non-Branded): Generic keywords only                   │
│  • OB (Own Brand): Can use own brand name                    │
│  • CB (Competitor Brand): Can reference competitors          │
└───────────────────────────────────────────────────────────────┘
        ↓
┌───────────────────────────────────────────────────────────────┐
│  STEP 3: PROMPT #2 - LISTING ATTRIBUTES                      │
│  AI extracts:                                                 │
│  • Product type, key features, use cases                     │
│  • Target audience, materials, sizes                          │
└───────────────────────────────────────────────────────────────┘
        ↓
┌───────────────────────────────────────────────────────────────┐
│  STEP 4: PROMPT #3 - KEYWORD GENERATION                      │
│  AI generates keywords classified as:                        │
│  • R (Root): Direct product descriptors                      │
│  • S (Synonym): Alternative terms                            │
│  • C (Complementary): Related/accessory terms                │
│  • N (Negative): Irrelevant terms to exclude                 │
└───────────────────────────────────────────────────────────────┘
        ↓
┌───────────────────────────────────────────────────────────────┐
│  STEP 5: RELEVANCE TAG ASSIGNMENT                            │
│  Format: [Branding][Relationship][Rank]                      │
│  Examples: NBR1, OBS2, CBC3, NBN1                            │
└───────────────────────────────────────────────────────────────┘
```

## Relevance Tag Structure

| Component | Values | Description |
|-----------|--------|-------------|
| Branding | NB, OB, CB | Non-Branded, Own Brand, Competitor Brand |
| Relationship | R, S, C, N | Root, Synonym, Complementary, Negative |
| Rank | 1, 2, 3... | Priority within group |

## Test Case Mapping

| Logic Area | Verification Tests | Validation Tests |
|------------|-------------------|------------------|
| Trigger | Verify fires on ASIN enable | 30-day refresh timing |
| PDP Fetching | Verify all content fields extracted | Missing bullet points |
| Prompt #1 | Verify branding scope classification | Edge: Brand-like generic term |
| Prompt #2 | Verify attribute extraction | Minimal listing content |
| Prompt #3 | Verify R/S/C/N classification | Ambiguous keyword |
| Tag Format | Verify [Branding][Rel][Rank] structure | Invalid tag handling |

---

# 10. Automated Target ASIN Research

**UAT Document:** `UAT_Automated_Target_ASIN_Research.md`
**Tests:** 208 (131 Verification + 77 Validation)

## What It Does
Automatically identifies and qualifies competitor ASINs for ASIN Targeting campaigns by analyzing top search terms, scraping Amazon SERP, enriching competitor data, and applying qualification criteria.

## How It Works

```
┌───────────────────────────────────────────────────────────────┐
│  STEP 1: TRIGGER EVALUATION                                   │
│  Trigger #1: ASIN ENABLED for first time                     │
│  Trigger #2: Every 14 days                                    │
│  Condition: Spend_15d > $100 AND Orders_15d > 5              │
└───────────────────────────────────────────────────────────────┘
        ↓
┌───────────────────────────────────────────────────────────────┐
│  STEP 2: SEARCH TERM FILTERING                                │
│  • Filter terms accounting for ≥50% of total ad spend        │
│  • Exclude search terms that ARE ASINs                       │
│  • Rank by CVR, select TOP 5                                 │
└───────────────────────────────────────────────────────────────┘
        ↓
┌───────────────────────────────────────────────────────────────┐
│  STEP 3: SERP SCRAPING                                        │
│  • For each of 5 search terms                                │
│  • Scrape Amazon Page 1 (~45-50 ASINs)                       │
│  • Extract: ASIN, Title, Price, Sponsored flag, Position     │
└───────────────────────────────────────────────────────────────┘
        ↓
┌───────────────────────────────────────────────────────────────┐
│  STEP 4: ATTRIBUTE ENRICHMENT                                 │
│  • Fetch product detail page for each ASIN                   │
│  • Collect: Price, Rating, Reviews, Fulfillment, Brand       │
│  • Price fallback: Buy Box → FBA → FBM → 30d avg            │
└───────────────────────────────────────────────────────────────┘
        ↓
┌───────────────────────────────────────────────────────────────┐
│  STEP 5: ASIN QUALIFICATION                                   │
│                                                               │
│  LEVEL 1 (Strict): Our Price ≤ Competitor Price              │
│  + Rating > 4 OR close to competitor                         │
│  + Review thresholds met                                      │
│                                                               │
│  LEVEL 2 (Relaxed): Our Price ≤ 1.1× Competitor             │
│  + Rating ≥ 4 OR within 0.3 of competitor                   │
│  + Review thresholds + FBA requirement                        │
└───────────────────────────────────────────────────────────────┘
        ↓
┌───────────────────────────────────────────────────────────────┐
│  STEP 6: GROUP BY BRAND                                       │
│  • Group qualified ASINs by brand_name                       │
│  • Each brand group = one campaign unit                      │
└───────────────────────────────────────────────────────────────┘
```

## Qualification Criteria Summary

| Level | Price | Rating | Reviews | Fulfillment |
|-------|-------|--------|---------|-------------|
| L1 | Ours ≤ Comp | >4 OR same digit & within 0.5 | Various thresholds | N/A |
| L2 | Ours ≤ 1.1× Comp | ≥4 OR within 0.3 | Various thresholds | FBA required (or both FBM) |

## Test Case Mapping

| Logic Area | Verification Tests | Validation Tests |
|------------|-------------------|------------------|
| Trigger | Verify Spend > $100 AND Orders > 5 | Boundary: Exactly $100/$5 |
| Search Term Filter | Verify 50% spend threshold | Cumulative spend calculation |
| SERP Scraping | Verify ~45-50 ASINs returned | Timeout/retry handling |
| Enrichment | Verify price fallback hierarchy | All prices unavailable |
| L1 Qualification | Verify all criteria checked | Boundary: Price equal |
| L2 Qualification | Verify relaxed criteria | Boundary: 1.1× price |
| Brand Grouping | Verify correct group assignment | Missing brand name |

---

# 11. Automated Campaign Generation

**UAT Document:** `UAT_Automated_Campaign_Generation.md`
**Tests:** 229 (143 Verification + 86 Validation)

## What It Does
Automatically creates Sponsored Products ASIN Targeting (SPAS) campaigns when new Brand Groups are identified from the ASIN Research qualification process.

## How It Works

```
┌───────────────────────────────────────────────────────────────┐
│  TRIGGER                                                      │
│  • New Brand Group created in backend                        │
│  • User has toggled ASIN Targeting ON                        │
│  • No blocking error conditions                               │
└───────────────────────────────────────────────────────────────┘
        ↓
┌───────────────────────────────────────────────────────────────┐
│  CAMPAIGN NAMING                                              │
│  Format: ZZZZZZ-YYYY-XXXX-WW-V-UUUUUUUUUU-T-KW               │
│                                                               │
│  ZZZZZZ = "XXXXXX" (static)                                  │
│  YYYY   = "SPAS" (campaign type)                             │
│  XXXX   = Brand Code (4-char unique)                         │
│  WW     = "XX" (hardcoded)                                   │
│  V      = "S"                                                │
│  UUUUU  = Client's ASIN                                      │
│  T      = "X"                                                │
│  KW     = Brand Group Name (truncate if needed)              │
└───────────────────────────────────────────────────────────────┘
        ↓
┌───────────────────────────────────────────────────────────────┐
│  BRAND CODE ASSIGNMENT                                        │
│  • First 2 chars: First letters of first 2 words            │
│  • Last 2 chars: Serial number                               │
│  • Examples: Supreme One → SO01, Soapera → SO03             │
│  • Global at Kepler level (not per seller)                   │
└───────────────────────────────────────────────────────────────┘
        ↓
┌───────────────────────────────────────────────────────────────┐
│  CAMPAIGN CONFIGURATION                                       │
│  • Targeting Type: Manual ASIN Targeting                     │
│  • Bidding Strategy: Down Only                               │
│  • Placement Modifier: None                                   │
│  • Daily Budget: User-defined OR Auto Budget                 │
│  • Negatives: Auto-add underperforming Target ASINs          │
└───────────────────────────────────────────────────────────────┘
        ↓
┌───────────────────────────────────────────────────────────────┐
│  UI INTEGRATION                                               │
│  • Campaign Config: Relevancy Tag = "XXXXXX", Match = "-"    │
│  • KW Config: Target ASINs in "Target" column               │
│  • ST Config: Target ASINs from Auto + Manual campaigns      │
└───────────────────────────────────────────────────────────────┘
```

## Campaign Configuration Details

| Element | Value |
|---------|-------|
| Targeting Type | Manual ASIN Targeting |
| Bidding Strategy | Down Only |
| Placement Modifier | None |
| Daily Budget | User-defined OR Auto Budget (min $5) |
| Negative Handling | Auto-add underperforming ASINs to Auto Campaign negatives |

## Test Case Mapping

| Logic Area | Verification Tests | Validation Tests |
|------------|-------------------|------------------|
| Trigger | Verify campaign created per brand group | Multiple groups simultaneously |
| Naming | Verify format with all fields | Exceeds Amazon char limit |
| Brand Code | Verify 4-char generation | Same prefix collision |
| Configuration | Verify all settings applied | Budget validation |
| Negative Auto-Add | Verify underperformers negated | Criteria boundary |
| UI Display | Verify all columns populated | Filter/sort functionality |

---

# Cross-Feature Test Coverage Matrix

| Feature | Triggers | Classification | Calculation | API Sync | UI | Bulk |
|---------|----------|----------------|-------------|----------|----|----|
| Auto Budget | ✅ | ✅ Campaign Types | ✅ Formulas | ✅ | ✅ | - |
| Bid Optimization | ✅ | ✅ Override/Breach | ✅ Bid Calc | ✅ | ✅ | - |
| Harvesting | ✅ | ✅ ACOS Check | ✅ MAX(ACoS) | ✅ | ✅ | - |
| Negation | ✅ | ✅ ACOS Check | ✅ MIN(ACoS) | ✅ | ✅ | ✅ |
| Pacing | ✅ | ✅ Feasibility | ✅ ML Projection | ✅ | ✅ | - |
| Isolation | ✅ | ✅ Top 5% | ✅ Ranking | ✅ | ✅ | - |
| KW Research | ✅ | ✅ Branding/R/S/C/N | ✅ AI Prompts | - | ✅ | ✅ |
| ASIN Research | ✅ | ✅ L1/L2 Qual | ✅ Qualification | - | ✅ | - |
| Campaign Gen | ✅ | ✅ Brand Groups | ✅ Naming | ✅ | ✅ | ✅ |

---

# Test Execution Priority

## P0 - Critical (Run Every Release)

| Feature | Critical Test |
|---------|---------------|
| Auto Budget | Budget distribution sums to ASIN budget |
| Bid Optimization | ACOS Breach → $0.02 (Manual KW only) |
| Harvesting | Qualifying search term routes correctly |
| Negation | MIN(ACoS) > Target triggers negation |
| Pacing | Knapsack selects within budget |
| Isolation | Top 5% identification accuracy |
| KW Research | OpenAI integration returns valid JSON |
| ASIN Research | Qualification logic accuracy |
| Campaign Gen | Campaign created per brand group |

## P1 - High (Run Weekly)

- All boundary condition tests
- All fallback/error handling tests
- CVR waterfall level selection
- UI column display accuracy

## P2 - Medium (Run Monthly)

- Performance/load tests
- Bulk import/export
- Edge cases (empty data, nulls)

---

# Document Links

| Feature | UAT Document |
|---------|--------------|
| Auto Budget | [UAT_Auto_Budget.md](./UAT_Auto_Budget.md) |
| Bid Opt - Manual KW | [UAT_Bid_Optimization_Manual_KW.md](./UAT_Bid_Optimization_Manual_KW.md) |
| Bid Opt - Auto | [UAT_Bid_Optimization_Auto_Targeting.md](./UAT_Bid_Optimization_Auto_Targeting.md) |
| Bid Opt - ASIN | [UAT_Bid_Optimization_ASIN_Targeting.md](./UAT_Bid_Optimization_ASIN_Targeting.md) |
| Harvesting | [UAT_Harvesting.md](./UAT_Harvesting.md) |
| Negation | [UAT_Negation.md](./UAT_Negation.md) |
| Pacing | [UAT_Pacing.md](./UAT_Pacing.md) |
| Isolation | [UAT_Isolation.md](./UAT_Isolation.md) |
| KW Research | [UAT_Automated_KW_Research.md](./UAT_Automated_KW_Research.md) |
| ASIN Research | [UAT_Automated_Target_ASIN_Research.md](./UAT_Automated_Target_ASIN_Research.md) |
| Campaign Gen | [UAT_Automated_Campaign_Generation.md](./UAT_Automated_Campaign_Generation.md) |

---

**Document Version:** 1.0
**Author:** Abdul
**Date:** January 2026
