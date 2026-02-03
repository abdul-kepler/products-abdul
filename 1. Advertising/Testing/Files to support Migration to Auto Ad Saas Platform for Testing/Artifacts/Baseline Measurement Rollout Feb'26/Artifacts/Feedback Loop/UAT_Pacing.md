# UAT: Intelligent Pacing Automation (PROD-1000)

## Overview

This document contains comprehensive test cases for the Intelligent Pacing Automation feature. Pacing automatically determines **which campaigns to activate** and **how much budget to allocate** to maximize ad sales within ACOS constraints.

**Two Core Engines:**
- **Projection Engine (US3)**: Projects ad spend and ad sales per campaign
- **Budget Optimizer (US4)**: Selects optimal campaign mix via knapsack optimization

---

## Core Logic Flow

```
Daily Budget + Target ACOS + All Campaigns
              ↓
    ┌─────────────────────┐
    │  PROJECTION ENGINE  │
    │  - CVR Estimation   │  (ML model)
    │  - CTR Waterfall    │  (3d → 180d)
    │  - IS Heuristic     │  (multi-factor)
    └──────────┬──────────┘
               ↓
    Projected Spend, Sales, ACOS per Campaign
               ↓
    ┌─────────────────────┐
    │  BUDGET OPTIMIZER   │
    │  - ACOS Filter      │  (< Target ACOS)
    │  - Knapsack Solver  │  (maximize sales)
    └──────────┬──────────┘
               ↓
    Selected Campaigns to Activate
               ↓
    ┌─────────────────────┐
    │  EXECUTION ENGINE   │
    │  - Amazon Ads API   │
    └─────────────────────┘
```

---

## Campaign States

| State | Description |
|-------|-------------|
| **ACTIVE** | Campaign is enabled and spending |
| **PAUSED** | Campaign is disabled (not meeting criteria or budget constrained) |
| **QUEUED** | Campaign waiting for activation (meets criteria, awaiting slot) |
| **BLOCKED** | Campaign excluded from consideration (manual block or safety rails) |

---

## Projection Engine Components

### 1. CVR Estimation (ML Model)
- Uses ML model to estimate conversion rate per campaign
- Inputs: Historical performance, ASIN attributes, keyword characteristics

### 2. CTR Waterfall
- Lookback hierarchy: 3d → 7d → 14d → 30d → 60d → 180d
- Falls back to longer periods when insufficient data

### 3. Impression Share Heuristic
Multi-factor scoring:

| Factor | Description |
|--------|-------------|
| **Relevancy** | Semantic relevancy via embeddings |
| **Difficulty** | Keyword competitiveness |
| **Performance** | Historical campaign performance |
| **Bid Competitiveness** | Bid vs. suggested bid |

### Projection Outputs
- **Projected Spend**: Estimated daily spend
- **Projected Sales**: Estimated daily ad sales
- **Projected ACOS**: Projected Spend / Projected Sales

---

## Budget Optimizer Components

### 1. ACOS Filter
- Only campaigns with Projected ACOS <= Target ACOS qualify
- Campaigns above threshold are excluded from optimization

### 2. Knapsack Optimization
- **Constraint**: Daily Budget
- **Objective**: Maximize total projected ad sales
- **Decision**: Which campaigns to activate

### 3. Execution
- Selected campaigns → ACTIVE state
- Non-selected campaigns → PAUSED state
- Executed via Amazon Ads API

---

## Feasibility Scoring Dimensions

| Dimension | Components |
|-----------|------------|
| **Account Readiness** | Ad history, indexing maturity, CTR benchmarks |
| **ASIN Readiness** | Review count, rating quality, CVR performance |
| **Competitiveness** | CPC levels, keyword saturation |
| **Win Probability** | Likelihood of hitting target ACOS |
| **Goal Alignment** | Growth vs. Efficiency mode |

---

## Evaluation Cadence

| Trigger | Frequency | Scope |
|---------|-----------|-------|
| **Scheduled** | Daily | All campaigns for all ASINs |
| **Manual Override** | Immediate | Specific campaign |
| **Budget Change** | Immediate | Affected ASIN's campaigns |

---

# TYPE 1: VERIFICATION TESTS

## A. Projection Engine - CVR Estimation (8 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| P-V01 | Filter: Campaign with sufficient historical conversion data | CVR estimate exists | ML model produces estimate |
| P-V02 | Filter: Campaign with no historical data (new campaign) | Falls back to default CVR | Cold start handled |
| P-V03 | Filter: Campaign with recent performance change | CVR estimate updates | Model reacts to changes |
| P-V04 | Filter: Compare CVR estimate vs actual CVR (last 7 days) | Within acceptable variance | Estimation accuracy |
| P-V05 | Filter: ASIN with high-quality attributes (good reviews, ratings) | Higher CVR estimate | ASIN attributes influence |
| P-V06 | Filter: ASIN with poor attributes | Lower CVR estimate | ASIN attributes influence |
| P-V07 | Filter: Campaign with seasonal variation | CVR accounts for seasonality | Seasonal adjustment |
| P-V08 | Filter: Multiple campaigns same ASIN | Different CVR per campaign | Campaign-level estimation |

---

## B. Projection Engine - CTR Waterfall (7 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| P-V09 | Filter: Campaign with 3-day CTR data | Uses 3-day CTR | Primary lookback used |
| P-V10 | Filter: Campaign with no 3-day data, has 7-day | Falls back to 7-day CTR | Waterfall works |
| P-V11 | Filter: Campaign with no data until 30-day | Uses 30-day CTR | Deep fallback works |
| P-V12 | Filter: Campaign with no data until 180-day | Uses 180-day CTR | Maximum fallback |
| P-V13 | Filter: New campaign with no CTR data | Uses default CTR | Cold start handled |
| P-V14 | Filter: Campaign where 3-day CTR differs significantly from 30-day | Correctly uses 3-day (recent) | Recency prioritized |
| P-V15 | Filter: Compare projected CTR vs actual CTR | Within acceptable variance | CTR accuracy |

---

## C. Projection Engine - Impression Share (8 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| P-V16 | Filter: Campaign with high relevancy keywords | Higher IS score | Relevancy impacts IS |
| P-V17 | Filter: Campaign with low relevancy keywords | Lower IS score | Relevancy impacts IS |
| P-V18 | Filter: Campaign in high-difficulty keyword space | Lower IS score | Difficulty impacts IS |
| P-V19 | Filter: Campaign in low-difficulty keyword space | Higher IS score | Difficulty impacts IS |
| P-V20 | Filter: Campaign with strong historical performance | Higher IS score | Performance impacts IS |
| P-V21 | Filter: Campaign with bid > suggested bid | Higher IS score | Bid competitiveness impacts IS |
| P-V22 | Filter: Campaign with bid < suggested bid | Lower IS score | Bid competitiveness impacts IS |
| P-V23 | Filter: Calculate composite IS score | All factors weighted correctly | Multi-factor scoring works |

---

## D. Projection Engine - Outputs (6 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| P-V24 | Filter: Campaign with all projection components | Projected Spend calculated | Spend = IS × Clicks × CPC |
| P-V25 | Filter: Campaign with all projection components | Projected Sales calculated | Sales = Clicks × CVR × Price |
| P-V26 | Filter: Campaign with all projection components | Projected ACOS calculated | ACOS = Spend / Sales |
| P-V27 | Filter: Campaign where CVR = 0 | Projected ACOS = 9999 (or max) | Zero-sales handling |
| P-V28 | Filter: Compare projected vs actual (7-day lookback) | Variance tracked | Projection accuracy |
| P-V29 | Filter: All campaigns for an ASIN | Each has projections | Complete coverage |

---

## E. Budget Optimizer - ACOS Filter (6 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| P-V30 | Filter: Campaign with Projected ACOS <= Target | Included in optimization | Qualifies |
| P-V31 | Filter: Campaign with Projected ACOS > Target | Excluded from optimization | Does not qualify |
| P-V32 | Filter: Campaign at exactly Target ACOS | Included in optimization | Boundary included |
| P-V33 | Filter: ASIN-level Target ACOS applies | Uses ASIN Target | ASIN target respected |
| P-V34 | Filter: Campaign-level Target ACOS override | Uses Campaign Target | Campaign override works |
| P-V35 | Filter: No campaigns meet ACOS threshold | No campaigns activated | Graceful empty handling |

---

## F. Budget Optimizer - Knapsack Optimization (10 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| P-V36 | Filter: ASIN with Daily Budget < Total Projected Spend (all campaigns) | Subset of campaigns activated | Budget constraint respected |
| P-V37 | Filter: Knapsack selects campaigns | Maximizes total projected sales | Optimization objective |
| P-V38 | Filter: Two campaigns, one has higher ACOS but higher sales | Lower ACOS selected (if ACOS is constraint) | ACOS constraint precedence |
| P-V39 | Filter: Total spend of activated campaigns | Stays within daily budget | Budget not exceeded |
| P-V40 | Filter: ASIN with Budget >> Total Projected Spend | All qualifying campaigns activated | Budget not wasted |
| P-V41 | Filter: Campaign with 0 projected sales | Not selected | Zero-value excluded |
| P-V42 | Filter: Budget change mid-day | Re-optimization triggered | Dynamic adjustment |
| P-V43 | Filter: Multiple ASINs with different budgets | Each ASIN optimized separately | ASIN-level optimization |
| P-V44 | Filter: Knapsack solver runtime | Completes within timeout | Performance acceptable |
| P-V45 | Filter: Tie-breaker when campaigns have equal value | Consistent selection | Deterministic behavior |

---

## G. Execution Engine (8 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| P-V46 | Filter: Campaign selected by optimizer | State changed to ACTIVE | Activation executed |
| P-V47 | Filter: Campaign not selected by optimizer | State changed to PAUSED | Pause executed |
| P-V48 | Filter: Campaign state changes pushed to Amazon | Amazon Ads API call successful | Amazon sync works |
| P-V49 | Filter: Verify campaign status on Amazon | Matches system state | Sync accurate |
| P-V50 | Filter: API rate limits | Requests stay within limits | Rate limiting respected |
| P-V51 | Filter: API failure during execution | Retry mechanism triggers | Error handling |
| P-V52 | Filter: Execution logging | All state changes logged | Audit trail |
| P-V53 | Filter: Daily scheduled execution | Runs at configured time | Scheduling works |

---

## H. Campaign States (8 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| P-V54 | Filter: Campaign meeting all criteria | State = ACTIVE | Correct state assignment |
| P-V55 | Filter: Campaign not meeting ACOS criteria | State = PAUSED | Correct state assignment |
| P-V56 | Filter: Campaign meeting criteria but budget exhausted | State = QUEUED | Waiting for slot |
| P-V57 | Filter: Campaign manually blocked by user | State = BLOCKED | Manual block honored |
| P-V58 | Filter: QUEUED campaign when slot opens | State changes to ACTIVE | Queue processing |
| P-V59 | Filter: State change history | All transitions logged | State tracking |
| P-V60 | Filter: Campaign transitions PAUSED → QUEUED → ACTIVE | Correct state progression | State machine works |
| P-V61 | Filter: Campaign state after manual override | Reflects override | Manual takes precedence |

---

## I. Manual Override & Controls (8 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| P-V62 | Filter: User manually activates a PAUSED campaign | Campaign becomes ACTIVE | Manual activation works |
| P-V63 | Filter: User manually pauses an ACTIVE campaign | Campaign becomes PAUSED | Manual pause works |
| P-V64 | Filter: User sets BLOCKED state | Campaign excluded from optimization | Block works |
| P-V65 | Filter: User clears BLOCKED state | Campaign re-enters optimization | Unblock works |
| P-V66 | Filter: Manual override persists across daily runs | Override not overwritten | Persistence |
| P-V67 | Filter: Override reason logged | Reason captured | Audit trail |
| P-V68 | Filter: Bulk manual override | All selected campaigns updated | Bulk actions work |
| P-V69 | Filter: Manual override UI | Dashboard shows override controls | UI available |

---

## J. Safety Rails & Guardrails (8 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| P-V70 | Filter: Minimum active campaigns per ASIN | At least N campaigns active | Minimum enforced |
| P-V71 | Filter: Cooldown period after state change | No rapid flip-flopping | Cooldown enforced |
| P-V72 | Filter: Maximum state changes per day | Limit respected | Rate limiting |
| P-V73 | Filter: Campaign violating safety threshold | Blocked from activation | Safety rail triggers |
| P-V74 | Filter: New campaign (cold start) | Conservative treatment | Cold start protection |
| P-V75 | Filter: Extreme ACOS spike | Automatic pause considered | Performance guardrail |
| P-V76 | Filter: Budget nearly exhausted | Graceful degradation | Budget protection |
| P-V77 | Filter: Safety rail violation logged | Alert generated | Monitoring |

---

## K. Dashboard & UI (8 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| P-V78 | Filter: Pacing dashboard | Shows all campaign states | Dashboard loads |
| P-V79 | Filter: Feasibility score breakdown | Shows dimension scores | Detail view works |
| P-V80 | Filter: Priority queue view | Shows QUEUED campaigns in order | Queue visible |
| P-V81 | Filter: Performance metrics per campaign | ACOS, Sales, Spend shown | Metrics displayed |
| P-V82 | Filter: Historical state change timeline | Timeline visible | History accessible |
| P-V83 | Filter: Export functionality | Data exported correctly | Export works |
| P-V84 | Filter: Dashboard refresh | Updates with latest data | Real-time updates |
| P-V85 | Filter: Filter/sort capabilities | Filtering works | Usability |

---

# TYPE 2: VALIDATION TESTS

## A. CVR Estimation Accuracy (6 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| P-VAL01 | Filter: Campaigns where actual CVR >> projected CVR | Model underestimating | Underbidding, lost opportunity |
| P-VAL02 | Filter: Campaigns where actual CVR << projected CVR | Model overestimating | Overbidding, wasted spend |
| P-VAL03 | Filter: CVR prediction error by campaign type | Error distribution | Systematic bias |
| P-VAL04 | Filter: CVR prediction error by ASIN attributes | Error correlation | Model feature gaps |
| P-VAL05 | Filter: New campaigns CVR accuracy | New vs. established | Cold start accuracy |
| P-VAL06 | Filter: Seasonal products CVR accuracy | Seasonal adjustment quality | Seasonality handling |

---

## B. Projection Accuracy (6 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| P-VAL07 | Filter: Projected vs actual daily spend (MAPE) | Mean Absolute Percentage Error | Spend projection accuracy |
| P-VAL08 | Filter: Projected vs actual daily sales (MAPE) | Mean Absolute Percentage Error | Sales projection accuracy |
| P-VAL09 | Filter: Projected vs actual ACOS (MAPE) | Mean Absolute Percentage Error | ACOS projection accuracy |
| P-VAL10 | Filter: High-variance campaigns | Projection stability | Volatile predictions |
| P-VAL11 | Filter: Consistent over/under projection | Systematic bias | Calibration needed |
| P-VAL12 | Filter: Projection accuracy by keyword type | Error by intent | Intent-specific issues |

---

## C. Optimization Quality (8 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| P-VAL13 | Filter: Activated campaigns actual ACOS vs projected | Projection vs reality | Activation decision quality |
| P-VAL14 | Filter: Paused campaigns that would have performed well | Missed opportunity | Over-conservative |
| P-VAL15 | Filter: Activated campaigns that underperformed | Poor selection | Over-aggressive |
| P-VAL16 | Filter: Total actual sales vs projected (daily) | Portfolio performance | Optimization effectiveness |
| P-VAL17 | Filter: Budget utilization rate | Spend vs Budget | Under/over-utilization |
| P-VAL18 | Filter: Optimal vs random selection | Performance difference | Optimization value add |
| P-VAL19 | Filter: Campaign selection consistency | Day-to-day stability | Flip-flopping |
| P-VAL20 | Filter: Edge cases (small budget, many campaigns) | Optimization behavior | Boundary conditions |

---

## D. State Management Issues (6 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| P-VAL21 | Filter: Campaigns frequently switching states | Flip-flop frequency | Unstable decisions |
| P-VAL22 | Filter: QUEUED campaigns never activated | Stuck in queue | Queue processing issue |
| P-VAL23 | Filter: BLOCKED campaigns never reviewed | Stale blocks | Block hygiene |
| P-VAL24 | Filter: State vs Amazon mismatch | Sync failures | Execution reliability |
| P-VAL25 | Filter: State change latency | Time from decision to execution | Execution speed |
| P-VAL26 | Filter: Manual overrides accumulation | Override hygiene | Override management |

---

## E. Business Impact (8 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| P-VAL27 | Filter: ASIN ACOS before vs after pacing | ACOS improvement | Primary metric |
| P-VAL28 | Filter: ASIN ad sales before vs after pacing | Sales change | Revenue impact |
| P-VAL29 | Filter: ASIN ad spend efficiency | Spend vs Target | Budget utilization |
| P-VAL30 | Filter: Wasted spend on paused campaigns (before pacing) | Spend reduction | Waste elimination |
| P-VAL31 | Filter: Time to optimal portfolio | Days to stabilize | Convergence speed |
| P-VAL32 | Filter: User override rate | Manual intervention frequency | Trust/acceptance |
| P-VAL33 | Filter: Support tickets related to pacing | Issue frequency | User experience |
| P-VAL34 | Filter: A/B test: pacing ON vs OFF | Performance difference | Feature value |

---

## F. Safety Rails Effectiveness (5 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| P-VAL35 | Filter: Safety rail triggers | Frequency and reason | Rail calibration |
| P-VAL36 | Filter: False positives (good campaigns blocked) | Overly conservative | Lost opportunity |
| P-VAL37 | Filter: False negatives (bad campaigns not blocked) | Under-protection | Wasted spend |
| P-VAL38 | Filter: Cooldown period effectiveness | Stability impact | Cooldown calibration |
| P-VAL39 | Filter: Minimum active campaigns impact | Performance vs constraint | Minimum calibration |

---

## G. Feasibility Scoring Validation (6 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| P-VAL40 | Filter: High feasibility score campaigns, poor actual performance | Score vs reality | Scoring inaccuracy |
| P-VAL41 | Filter: Low feasibility score campaigns, good actual performance | Score vs reality | Scoring inaccuracy |
| P-VAL42 | Filter: Feasibility score vs actual ACOS correlation | Predictive power | Score validity |
| P-VAL43 | Filter: Dimension contributions to total score | Weight effectiveness | Dimension calibration |
| P-VAL44 | Filter: Account readiness score accuracy | Dimension validation | Account scoring |
| P-VAL45 | Filter: ASIN readiness score accuracy | Dimension validation | ASIN scoring |

---

## H. Execution Reliability (5 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| P-VAL46 | Filter: API call failures | Failure rate | Reliability |
| P-VAL47 | Filter: Execution latency | Time to execute | Performance |
| P-VAL48 | Filter: Retry success rate | Recovery effectiveness | Error handling |
| P-VAL49 | Filter: Rate limit breaches | API compliance | Rate limiting |
| P-VAL50 | Filter: System uptime | Availability | Reliability |

---

# SUMMARY

| Test Type | Count | Focus Area |
|-----------|-------|------------|
| **Type 1: Verification** | 85 | Projection Engine, Budget Optimizer, Execution, States, UI |
| **Type 2: Validation** | 50 | Accuracy, Optimization quality, Business impact, Safety rails |
| **TOTAL** | 135 | |

---

# Key Thresholds to Monitor

| Threshold | Target | Risk |
|-----------|--------|------|
| CVR Estimation Accuracy | MAPE < 30% | Under/over-bidding |
| Spend Projection Accuracy | MAPE < 25% | Budget misallocation |
| ACOS Projection Accuracy | MAPE < 25% | Wrong campaign selection |
| Optimization Value Add | > 15% ROAS improvement | Feature effectiveness |
| State Flip-Flop Rate | < 10% daily | Instability |
| API Failure Rate | < 5% | Execution reliability |
| Budget Utilization | 80-100% | Under-utilization |

---

# Key Components Overview

| Component | Function | Key Metric |
|-----------|----------|------------|
| **CVR Model** | Estimates conversion rate | Prediction accuracy |
| **CTR Waterfall** | Estimates click-through rate | Lookback selection |
| **IS Heuristic** | Estimates impression share | Factor weighting |
| **ACOS Filter** | Screens campaigns | Threshold accuracy |
| **Knapsack Solver** | Selects optimal mix | Optimization quality |
| **Execution Engine** | Activates/pauses | Reliability |
| **Safety Rails** | Prevents bad decisions | False positive/negative |

---

# Reference Tickets

| Ticket | Description |
|--------|-------------|
| PROD-1000 | Epic: Intelligent Pacing Automation |
| PROD-1494 | US3: Projection Engine |
| PROD-1495 | US4: Budget Optimizer |

