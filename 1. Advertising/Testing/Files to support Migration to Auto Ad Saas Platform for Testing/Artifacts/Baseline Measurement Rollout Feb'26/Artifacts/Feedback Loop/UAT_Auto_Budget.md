# UAT: ASIN Auto Budget Management

## Overview

This document contains comprehensive test cases for the ASIN Auto Budget Management feature. Auto Budget automatically calculates and distributes the ASIN-level daily budget across active campaigns based on performance metrics, campaign maturity, and spend efficiency.

**Applies to:** Manual KW Targeting, Auto Targeting, ASIN Targeting, High Performer Isolation Campaigns

**Source:** [ASIN Auto Budget Logic_23 Sep'25](https://docs.google.com/spreadsheets/d/1WAwq71ODv9TxmcJEyKQRE1q_p0m3jrmnQopMloj3XpY)

---

## How the Auto-Budget Logic Works

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ASIN DAILY BUDGET (User Input)                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STEP 1: CAMPAIGN CLASSIFICATION                           │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐│
│  │   IMMATURE   │ │    FIXED     │ │  NO ACTIVITY │ │       NORMAL         ││
│  │  (Col O)     │ │   (Col P)    │ │   (Col Q)    │ │   (Remaining)        ││
│  │              │ │              │ │              │ │                      ││
│  │ Ad Spend_30d │ │ User-set     │ │ No Spend AND │ │ Has performance      ││
│  │ <= 5% of     │ │ fixed budget │ │ No Sales     │ │ data to evaluate     ││
│  │ ASIN Spend   │ │              │ │ (ACOS blank) │ │                      ││
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                 STEP 2: MINIMUM BUDGET ENFORCEMENT ($5)                      │
│                                                                              │
│  Each campaign gets at least $5 (changed from $2 on Sep 23, 2025)           │
│                                                                              │
│  Formula: Minimum_Budget = MAX(Immature_Budget, Fixed_Budget, NoActivity)   │
│           If total < $5, pad to reach $5 minimum                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│              STEP 3: CALCULATE AVAILABLE BUDGET FOR DISTRIBUTION             │
│                                                                              │
│  Available_Budget = ASIN_Next_Budget - SUM(All_Minimum_Budgets)             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                STEP 4: IDENTIFY LOSERS & REDUCE THEIR SHARE                  │
│                                                                              │
│  LOSER = Campaign where ACOS > Target ACOS (Delta < 0)                      │
│                                                                              │
│  Budget_Share_Drop = MIN( |ACOS_Delta|/2 + (1-Spend_Ratio)/4 , 0.2 )        │
│                                                                              │
│  Maximum reduction: 20% of budget share                                      │
│  Factors considered:                                                         │
│    • How much ACOS exceeds Target (worse = more reduction)                  │
│    • How much budget is underutilized (less spend = more reduction)         │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                 STEP 5: IDENTIFY WINNERS & CALCULATE BOOST                   │
│                                                                              │
│  WINNER = Campaign where ACOS <= Target ACOS (Delta >= 0)                   │
│                                                                              │
│  Boost_Score = (1 / ACOS) × Spend_to_Budget_Ratio                           │
│                                                                              │
│  % Boost = Campaign_Boost_Score / SUM(All_ASIN_Boost_Scores)                │
│                                                                              │
│  Winners with:                                                               │
│    • Lower ACOS = Higher boost score                                        │
│    • Higher spend efficiency = Higher boost score                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STEP 6: FINAL BUDGET CALCULATION                          │
│                                                                              │
│  FINAL_BUDGET = (Remaining_Budget × %_Boost)                                │
│                 + Post_Reduction_Budget                                      │
│                 + Minimum_Budget                                             │
│                                                                              │
│  Where:                                                                      │
│    Remaining_Budget = Available - SUM(Post_Reduction_Budgets)               │
│    Post_Reduction_Budget = Original_Share × (1 - Budget_Share_Drop)         │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          PUSH TO AMAZON                                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Key Formulas (from Google Sheet)

### 1. Immature Campaign Detection (Column C)
```
Is_Immature = IF(Campaign_Ad_Spend_30d <= ASIN_Ad_Spend_30d × 0.05, "Yes", "No")
```

### 2. ACOS Calculation (Column G)
```
ACOS = IF(Ad_Spend <= 0, blank,
       IF(Ad_Spend / Ad_Sales = ERROR, 9999,
          Ad_Spend / Ad_Sales))
```
*Returns 9999 when there are no sales (infinite ACOS)*

### 3. Spend to Budget Ratio (Column K)
```
Spend_Ratio = Ad_Spend_1d / Current_Budget
```

### 4. Immature Campaign Budget (Column O)
```
IF Campaign is Immature:
  Budget = MAX(
    MIN(
      0.2 × Available_Budget / Count_Immature_Campaigns,
      (MEDIAN(Campaign_Spends) / ASIN_Budget × Available_Budget × 0.5) / Count_Immature_Campaigns
    ),
    $5  // Minimum
  )
```

### 5. No Spend & No Sales Budget (Column Q)
```
IF ACOS is blank AND not Immature:
  Budget = (Current_Budget / ASIN_Last_Budget) × Available_Budget
```

### 6. Minimum Budget Enforcement (Columns R & S)
```
Required_Padding = $5 - SUM(Immature_Budget, Fixed_Budget, NoActivity_Budget)

Final_Minimum = IF Required_Padding > 0:
                  Immature + Fixed + NoActivity + Required_Padding
                ELSE:
                  MAX(Immature, Fixed, NoActivity)
```

### 7. ACOS Delta (Column U)
```
For Normal campaigns only (not Immature, Fixed, or NoActivity):
  Delta = Target_ACOS - Actual_ACOS

  Positive Delta = WINNER (under target)
  Negative Delta = LOSER (over target)
```

### 8. Loser Budget Share Drop (Column V)
```
IF Delta < 0 (LOSER):
  Drop = MIN(
    |Delta| / 2 + (1 - Spend_Ratio) / 4,
    0.2  // Max 20% reduction
  )
```

### 9. Winner Boost Score (Column W)
```
IF Delta >= 0 AND Normal campaign (WINNER):
  Boost_Score = (1 / ACOS) × Spend_Ratio
```

### 10. Boost Percentage (Column X)
```
%_Boost = Campaign_Boost_Score / SUM(All_ASIN_Boost_Scores)
```

### 11. Final Budget (Column AD)
```
Final_Budget = ((Available_Budget - SUM(Post_Reduction_Budgets)) × %_Boost)
               + Post_Reduction_Budget
               + Minimum_Budget
```

---

## Core Concepts

### Campaign Classifications

| Classification | Criteria | Budget Source |
|---------------|----------|---------------|
| **Immature** | Ad_Spend_30d <= 5% of ASIN_Ad_Spend_30d | Column O formula |
| **Fixed Budget** | User manually set fixed budget | Column P (user input) |
| **No Activity** | No spend AND no sales (blank ACOS) | Column Q formula |
| **Normal (Winner)** | ACOS <= Target ACOS | Gets boost from losers |
| **Normal (Loser)** | ACOS > Target ACOS | Loses up to 20% share |

### Budget Redistribution Logic

```
                    LOSER CAMPAIGNS                    WINNER CAMPAIGNS
                    ───────────────                    ────────────────
                          │                                   │
                          │ Lose up to 20%                    │ Receive redistributed
                          │ of budget share                   │ budget based on
                          │                                   │ Boost Score
                          │                                   │
                          └───────────────┬───────────────────┘
                                          │
                                          ▼
                              ┌───────────────────────┐
                              │   REDISTRIBUTED       │
                              │   BUDGET POOL         │
                              │                       │
                              │ Sum of budget taken   │
                              │ from all losers       │
                              └───────────────────────┘
```

### Auto-Budget Toggle
- **ASIN-Level Setting**: Each ASIN has an Auto-Budget toggle (ON/OFF)
- **When ON**: System automatically calculates campaign budgets using the logic above
- **When OFF**: User must manually set campaign budgets

### Fixed Budget Override
- User can set a **fixed daily budget** for specific campaigns
- Fixed budget campaigns are excluded from winner/loser evaluation
- Remaining ASIN budget is distributed among non-fixed campaigns

---

## Trigger Scenarios

### When Auto-Budget is ON

| Trigger | Description |
|---------|-------------|
| **1. Auto-Budget Enabled** | Toggle switched ON via UI or Bulk Import |
| **2. ASIN Daily Budget Updated** | Budget amount changed via UI or Bulk Import |
| **3. Campaign Status Change** | Campaign activated or deactivated |
| **4. Active Keyword Count Change** | Keywords turned ON/OFF (only if no fixed budget) |
| **5. Fixed Budget Change** | Fixed budget set/changed for any active campaign |
| **6. Scheduled Daily Recalculation** | Every 24 hours for all active campaigns |

### When Auto-Budget is OFF

| Trigger | Description |
|---------|-------------|
| **Fixed Budget Change** | Only the specific campaign budget is updated |

---

## Budget Validation Rules

| Rule | Condition | Error Message |
|------|-----------|---------------|
| Minimum Budget | Active campaign budget < $5 | "Invalid Campaign Budget: The manual daily budget for this active campaign must be at least $5." |
| Blank Budget | Active campaign with Auto-Budget OFF and blank budget | "Please enter a Daily Campaign Budget, deactivate the campaign, or enable Auto-Budget from the ASIN config." |

**Note:** Minimum budget changed from $2 to $5 on September 23, 2025.

---

## Weighted Average Budget Calculation

When campaign budget changes multiple times in a day:

```
Weighted Average Budget = Σ(Budget_i × Duration_i) / Σ(Duration_i)
```

**Example:**
- 00:00-12:00 (12 hours): Budget = $50
- 12:00-24:00 (12 hours): Budget = $100
- Weighted Average = (50 × 12 + 100 × 12) / 24 = $75

---

## Data Sources by Targeting Type

| Targeting Type | Historical Data Source |
|----------------|------------------------|
| **Manual KW Targeting** | Campaign-level or KW+ASIN level |
| **Auto Targeting** | Campaign + Match Type + ASIN level |
| **ASIN Targeting** | Same ASIN Targeting campaign |
| **HP Isolation** | KW + ASIN level |

---

# TYPE 1: VERIFICATION TESTS

## A. Auto-Budget Toggle (8 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| B-V01 | Filter: ASIN with Auto-Budget = ON | System calculates campaign budgets | Auto distribution active |
| B-V02 | Filter: ASIN with Auto-Budget = OFF | System does NOT auto-calculate | Manual mode active |
| B-V03 | Filter: Toggle Auto-Budget ON via UI | Budget recalculation triggered | Trigger #1 works |
| B-V04 | Filter: Toggle Auto-Budget ON via Bulk Import | Budget recalculation triggered | Bulk import trigger |
| B-V05 | Filter: Toggle Auto-Budget OFF | Auto-distribution stops | Toggle off works |
| B-V06 | Filter: Auto-Budget toggle persists | Same value after refresh/re-login | Persistence |
| B-V07 | Filter: New ASIN added | Default Auto-Budget state | Default value set |
| B-V08 | Filter: Auto-Budget toggle in UI | Visible and editable | UI available |

---

## B. ASIN Daily Budget (8 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| B-V09 | Filter: Set ASIN Daily Budget via UI | Budget saved and recalculation triggered | UI input works |
| B-V10 | Filter: Set ASIN Daily Budget via Bulk Import | Budget saved and recalculation triggered | Bulk import works |
| B-V11 | Filter: Update ASIN Daily Budget | Campaigns re-distributed | Trigger #2 works |
| B-V12 | Filter: ASIN Daily Budget = $0 | Handle gracefully | Edge case |
| B-V13 | Filter: ASIN Daily Budget validation | Minimum value enforced | Validation works |
| B-V14 | Filter: Sum of campaign budgets vs ASIN budget | Should approximately equal | Distribution accurate |
| B-V15 | Filter: ASIN Daily Budget persists | Same value after refresh | Persistence |
| B-V16 | Filter: Multiple ASINs with different budgets | Independent calculations | ASIN isolation |

---

## C. Campaign Classification - Immature Detection (8 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| B-V17 | Filter: Campaign with Ad_Spend_30d = 4% of ASIN_Spend_30d | Classified as Immature | Below 5% threshold |
| B-V18 | Filter: Campaign with Ad_Spend_30d = 5% of ASIN_Spend_30d | Classified as Immature | At 5% threshold |
| B-V19 | Filter: Campaign with Ad_Spend_30d = 6% of ASIN_Spend_30d | Classified as NOT Immature | Above 5% threshold |
| B-V20 | Filter: New campaign with $0 spend | Classified as Immature | Zero spend = immature |
| B-V21 | Filter: Immature campaign budget formula | Uses Column O formula | Correct formula applied |
| B-V22 | Filter: Multiple immature campaigns for same ASIN | Budget split evenly with cap | Count-based distribution |
| B-V23 | Filter: Immature campaign gets minimum $5 | Budget >= $5 | Minimum enforced |
| B-V24 | Filter: Immature status updates daily | Classification refreshes | Dynamic classification |

---

## D. Campaign Classification - No Activity (6 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| B-V25 | Filter: Campaign with $0 spend AND $0 sales | Classified as No Activity | Blank ACOS |
| B-V26 | Filter: Campaign with spend but no sales | NOT No Activity (has ACOS 9999) | Has spend = not no activity |
| B-V27 | Filter: No Activity campaign budget formula | Uses Column Q formula | Correct formula |
| B-V28 | Filter: No Activity budget = ratio-based | Budget = (Current/ASIN_Last) × Available | Ratio preserved |
| B-V29 | Filter: No Activity campaign gets minimum $5 | Budget >= $5 | Minimum enforced |
| B-V30 | Filter: Campaign transitions from No Activity | Reclassified when activity starts | Dynamic classification |

---

## E. Fixed Budget Override (8 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| B-V31 | Filter: Set fixed budget for a campaign | Campaign excluded from winner/loser evaluation | Fixed override works |
| B-V32 | Filter: Fixed budget + remaining distributed | Non-fixed campaigns share remainder | Correct distribution |
| B-V33 | Filter: Fixed budget > ASIN budget | Validation error or cap | Boundary handling |
| B-V34 | Filter: Multiple campaigns with fixed budgets | Each gets fixed, rest distributed | Multi-fixed works |
| B-V35 | Filter: Remove fixed budget | Campaign re-enters auto-distribution | Override removal |
| B-V36 | Filter: Fixed budget change triggers recalculation | Other campaigns redistributed | Trigger #5 works |
| B-V37 | Filter: Fixed budget via UI | Saved correctly | UI input works |
| B-V38 | Filter: Fixed budget via Bulk Import | Saved correctly | Bulk import works |

---

## F. Winner/Loser Classification (10 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| B-V39 | Filter: Campaign with ACOS < Target ACOS | Classified as Winner | Positive Delta |
| B-V40 | Filter: Campaign with ACOS = Target ACOS | Classified as Winner | Zero Delta = Winner |
| B-V41 | Filter: Campaign with ACOS > Target ACOS | Classified as Loser | Negative Delta |
| B-V42 | Filter: Campaign with ACOS = 9999 (no sales) | Classified as Loser | Infinite ACOS = Loser |
| B-V43 | Filter: Delta calculation accuracy | Delta = Target - Actual ACOS | Formula correct |
| B-V44 | Filter: Immature campaigns excluded from classification | Neither Winner nor Loser | Classification bypass |
| B-V45 | Filter: Fixed budget campaigns excluded | Neither Winner nor Loser | Classification bypass |
| B-V46 | Filter: No Activity campaigns excluded | Neither Winner nor Loser | Classification bypass |
| B-V47 | Filter: Classification updates on recalculation | Winner/Loser status refreshes | Dynamic classification |
| B-V48 | Filter: Multiple Winners for same ASIN | All receive boost proportionally | Multi-winner handling |

---

## G. Loser Budget Share Drop (8 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| B-V49 | Filter: Loser with small ACOS overage | Small budget drop | Proportional reduction |
| B-V50 | Filter: Loser with large ACOS overage | Larger budget drop (up to 20%) | Max cap respected |
| B-V51 | Filter: Loser with low spend ratio | Additional drop from underutilization | Spend factor applied |
| B-V52 | Filter: Loser with high spend ratio | Less drop from spend factor | Spend factor reduces penalty |
| B-V53 | Filter: Drop formula = MIN(\|Delta\|/2 + (1-Spend_Ratio)/4, 0.2) | Correct calculation | Formula verified |
| B-V54 | Filter: Maximum drop = 20% | No drop exceeds 20% | Cap enforced |
| B-V55 | Filter: Drop applied to budget ratio | Not absolute budget | Ratio-based |
| B-V56 | Filter: Total budget taken from Losers | Sum matches redistributed pool | Budget conservation |

---

## H. Winner Boost Score Calculation (8 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| B-V57 | Filter: Winner with low ACOS | High boost score | 1/ACOS factor |
| B-V58 | Filter: Winner with high ACOS (but still under target) | Lower boost score | ACOS inverse relationship |
| B-V59 | Filter: Winner with high spend ratio | Higher boost score | Spend efficiency rewarded |
| B-V60 | Filter: Winner with low spend ratio | Lower boost score | Low efficiency penalized |
| B-V61 | Filter: Boost Score formula = (1/ACOS) × Spend_Ratio | Correct calculation | Formula verified |
| B-V62 | Filter: % Boost = Score / Sum(All Scores) | Proportional distribution | Normalization correct |
| B-V63 | Filter: Sum of all % Boosts = 100% | Complete distribution | No boost leak |
| B-V64 | Filter: Only Winners receive boost | Losers/Immature/Fixed get none | Eligibility enforced |

---

## I. Final Budget Calculation (10 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| B-V65 | Filter: Winner final budget | Includes boost + base + minimum | Formula complete |
| B-V66 | Filter: Loser final budget | Reduced share + minimum | Reduction applied |
| B-V67 | Filter: Immature final budget | Uses Column O formula + minimum | Separate formula |
| B-V68 | Filter: Fixed budget campaign | Exact user-specified amount | No modification |
| B-V69 | Filter: No Activity final budget | Uses Column Q formula + minimum | Ratio-based |
| B-V70 | Filter: Sum of all final budgets | Equals ASIN Daily Budget | Budget conservation |
| B-V71 | Filter: Minimum $5 enforced for all | No campaign < $5 | Minimum applied |
| B-V72 | Filter: Redistributed budget fully allocated | No leftover | Complete redistribution |
| B-V73 | Filter: Budget rounding | Consistent rounding rules | No precision loss |
| B-V74 | Filter: Column AD matches expected | Final budget = formula result | Formula accuracy |

---

## J. Trigger: Campaign Status Change (6 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| B-V75 | Filter: Activate campaign (Auto-Budget ON) | Budget recalculation triggered | Trigger #3 works |
| B-V76 | Filter: Deactivate campaign (Auto-Budget ON) | Budget recalculation triggered | Trigger #3 works |
| B-V77 | Filter: Status change via Campaign Config UI | Recalculation triggered | UI trigger works |
| B-V78 | Filter: Status change via Bulk Import | Recalculation triggered | Bulk trigger works |
| B-V79 | Filter: Multiple status changes in batch | Single recalculation | Batch efficiency |
| B-V80 | Filter: Status change (Auto-Budget OFF) | No auto-recalculation | Auto-Budget OFF respected |

---

## K. Trigger: Active Keyword Count Change (6 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| B-V81 | Filter: Keyword turned ON (campaign no fixed budget) | Budget recalculation triggered | Trigger #4 works |
| B-V82 | Filter: Keyword turned OFF (campaign no fixed budget) | Budget recalculation triggered | Trigger #4 works |
| B-V83 | Filter: Keyword change via KW Config UI | Recalculation triggered | UI trigger works |
| B-V84 | Filter: Keyword change via Bulk Import | Recalculation triggered | Bulk trigger works |
| B-V85 | Filter: Keyword change (campaign HAS fixed budget) | NO recalculation | Fixed budget exception |
| B-V86 | Filter: Multiple keyword changes in batch | Single recalculation | Batch efficiency |

---

## L. Trigger: Scheduled Daily Recalculation (6 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| B-V87 | Filter: Scheduled recalculation timing | Runs every 24 hours | Trigger #6 works |
| B-V88 | Filter: All ASINs with Auto-Budget ON | All recalculated | Complete coverage |
| B-V89 | Filter: ASINs with Auto-Budget OFF | NOT recalculated | OFF respected |
| B-V90 | Filter: Recalculation logs | Logged with timestamp | Audit trail |
| B-V91 | Filter: No changes in 24 hours | Still recalculates | Scheduled runs |
| B-V92 | Filter: Recalculation during manual change | No conflict | Concurrent handling |

---

## M. Validation: Budget Minimum (8 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| B-V93 | Filter: Active campaign budget < $5 (Auto-Budget OFF) | Rejected with error | Minimum enforced |
| B-V94 | Filter: Active campaign budget = blank (Auto-Budget OFF) | Rejected with error | Blank not allowed |
| B-V95 | Filter: Active campaign budget exactly $5 | Accepted | Boundary included |
| B-V96 | Filter: Active campaign budget = $4.99 | Rejected | Below minimum |
| B-V97 | Filter: Paused campaign budget < $5 | Accepted | Only active validated |
| B-V98 | Filter: Error message displayed | Correct wording (mentions $5) | UX correct |
| B-V99 | Filter: Validation on UI input | Real-time validation | Client-side validation |
| B-V100 | Filter: Auto-calculated budget < $5 | Padded to $5 | Auto-enforcement |

---

## N. Amazon Push (8 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| B-V101 | Filter: Budget recalculation complete | New budgets pushed to Amazon | Push triggered |
| B-V102 | Filter: Verify budget on Amazon | Matches system budget | Sync accurate |
| B-V103 | Filter: Push timing | Within acceptable latency | Performance |
| B-V104 | Filter: Push failure handling | Retry mechanism | Error handling |
| B-V105 | Filter: Multiple campaigns updated | All pushed | Batch push |
| B-V106 | Filter: Push logging | All changes logged | Audit trail |
| B-V107 | Filter: Amazon API rate limits | Respected | Rate limiting |
| B-V108 | Filter: Campaign budget history on Amazon | Changes reflected | History tracked |

---

## O. Weighted Average Calculation (6 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| B-V109 | Filter: Budget changed once in 24 hours | Simple calculation | Single change |
| B-V110 | Filter: Budget changed multiple times in 24 hours | Weighted average used | Multi-change |
| B-V111 | Filter: Budget change at midnight | 24-hour boundary handled | Edge case |
| B-V112 | Filter: Duration calculation accuracy | Time-weighted correctly | Formula correct |
| B-V113 | Filter: Weighted average used in Column J | Last Updated Budget is weighted | Integration |
| B-V114 | Filter: No budget change in 24 hours | Uses existing budget | No change case |

---

## P. Multi-Targeting Type Support (8 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| B-V115 | Filter: Manual KW Targeting campaign | Auto-budget applies | Type supported |
| B-V116 | Filter: Auto Targeting campaign | Auto-budget applies | Type supported |
| B-V117 | Filter: ASIN Targeting campaign | Auto-budget applies | Type supported |
| B-V118 | Filter: HP Isolation campaign | Auto-budget applies | Type supported |
| B-V119 | Filter: Mixed targeting types for same ASIN | All included in distribution | Multi-type mix |
| B-V120 | Filter: Historical data source per type | Correct source used | Data source |
| B-V121 | Filter: Same ASIN, different campaign types | All compete for same budget pool | Type inclusion |
| B-V122 | Filter: Auto Targeting match type data | Match Type + ASIN level | Data granularity |

---

# TYPE 2: VALIDATION TESTS

## A. Winner/Loser Classification Accuracy (8 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| B-VAL01 | Filter: Campaigns classified as Winners | ACOS actually <= Target | Misclassification |
| B-VAL02 | Filter: Campaigns classified as Losers | ACOS actually > Target | Misclassification |
| B-VAL03 | Filter: Campaigns near Target ACOS boundary | Correct classification | Boundary errors |
| B-VAL04 | Filter: ACOS = 9999 campaigns | Classified as Loser | Infinite ACOS handling |
| B-VAL05 | Filter: Campaigns with volatile ACOS | Classification stability | Flip-flopping |
| B-VAL06 | Filter: Classification timing vs data freshness | Uses current data | Stale data |
| B-VAL07 | Filter: Delta calculation accuracy | Target - Actual correct | Math errors |
| B-VAL08 | Filter: Multiple campaigns with same ACOS | Consistent classification | Tie handling |

---

## B. Budget Redistribution Effectiveness (8 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| B-VAL09 | Filter: Budget taken from Losers | Sum matches given to Winners | Budget leak |
| B-VAL10 | Filter: Loser budget reduction | Matches formula (max 20%) | Over/under reduction |
| B-VAL11 | Filter: Winner budget boost | Proportional to Boost Score | Unfair distribution |
| B-VAL12 | Filter: High-performing Winners | Receive more boost | Reward alignment |
| B-VAL13 | Filter: Severely underperforming Losers | Capped at 20% reduction | Excessive penalty |
| B-VAL14 | Filter: Redistribution preserves total | ASIN budget unchanged | Total conservation |
| B-VAL15 | Filter: Immature campaigns | Not penalized as Losers | Protection working |
| B-VAL16 | Filter: No Activity campaigns | Not penalized as Losers | Protection working |

---

## C. Immature Campaign Handling (6 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| B-VAL17 | Filter: 5% threshold accuracy | Correct campaigns classified | Threshold errors |
| B-VAL18 | Filter: Immature budget formula | Uses MIN of 20% or median-based | Formula errors |
| B-VAL19 | Filter: Immature campaigns given fair chance | Adequate budget to grow | Underfunding |
| B-VAL20 | Filter: Immature to Mature transition | Reclassified correctly | Transition timing |
| B-VAL21 | Filter: Multiple immature campaigns | Budget split fairly | Uneven split |
| B-VAL22 | Filter: Immature campaign performance | ACOS trend over time | Growth trajectory |

---

## D. Minimum Budget Enforcement (5 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| B-VAL23 | Filter: Campaigns with calculated budget < $5 | Padded to $5 | Below minimum |
| B-VAL24 | Filter: Many campaigns with $5 minimum | Total exceeds ASIN budget | Budget overflow |
| B-VAL25 | Filter: $5 minimum impact on redistribution | Fair remaining distribution | Crowding effect |
| B-VAL26 | Filter: Previous $2 minimum campaigns | Updated to $5 | Migration complete |
| B-VAL27 | Filter: Minimum enforcement timing | Applied before Amazon push | Enforcement timing |

---

## E. ACOS Impact Analysis (8 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| B-VAL28 | Filter: ASIN ACOS before vs after Auto-Budget | ACOS improvement | No improvement |
| B-VAL29 | Filter: Winner campaigns ACOS trend | Maintained or improved | Winners declining |
| B-VAL30 | Filter: Loser campaigns ACOS trend | Improved with less budget | Losers not recovering |
| B-VAL31 | Filter: Overall portfolio ACOS | Trending toward targets | Portfolio drift |
| B-VAL32 | Filter: ACOS vs budget correlation | More budget to better ACOS | Inverse correlation |
| B-VAL33 | Filter: Campaigns consistently missing target | Budget reduction working | Persistent losers |
| B-VAL34 | Filter: Campaigns consistently beating target | Budget increase justified | ROI positive |
| B-VAL35 | Filter: Redistribution ACOS impact | Net positive effect | Redistribution hurts |

---

## F. Ad Sales Impact Analysis (6 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| B-VAL36 | Filter: ASIN Ad Sales before vs after Auto-Budget | Sales maintained or improved | Sales decline |
| B-VAL37 | Filter: Winner campaigns Ad Sales trend | Growing with more budget | Winners not scaling |
| B-VAL38 | Filter: Loser campaigns Ad Sales trend | Acceptable with less budget | Excessive sales loss |
| B-VAL39 | Filter: Total Ad Sales vs Budget | ROAS maintained | Efficiency loss |
| B-VAL40 | Filter: Budget utilization rate | Spend vs Budget ratio | Under/over spend |
| B-VAL41 | Filter: Campaigns hitting budget cap | Lost opportunity tracking | Capped winners |

---

## G. Trigger Timing Issues (6 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| B-VAL42 | Filter: Multiple triggers in quick succession | Recalculation frequency | Over-calculation |
| B-VAL43 | Filter: Delay between trigger and recalculation | Latency | Slow response |
| B-VAL44 | Filter: Delay between recalculation and Amazon push | Sync latency | Delayed push |
| B-VAL45 | Filter: Scheduled trigger timing accuracy | Actual vs expected | Schedule drift |
| B-VAL46 | Filter: Missed triggers | Trigger reliability | Missed recalculations |
| B-VAL47 | Filter: Concurrent triggers handling | Conflict resolution | Race conditions |

---

## H. Amazon Sync Issues (5 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| B-VAL48 | Filter: Budget mismatch (system vs Amazon) | Sync failures | Reliability |
| B-VAL49 | Filter: Push failures | Failure rate | API issues |
| B-VAL50 | Filter: Retry success rate | Recovery | Error handling |
| B-VAL51 | Filter: Budget changes not reflected | Sync lag | Delay issues |
| B-VAL52 | Filter: External budget changes on Amazon | Conflict detection | External modifications |

---

## I. Weighted Average Issues (4 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| B-VAL53 | Filter: Frequent budget changes | Weighted average accuracy | Calculation complexity |
| B-VAL54 | Filter: Budget changes near midnight | Boundary handling | Edge case accuracy |
| B-VAL55 | Filter: Weighted average vs simple average | Difference impact | Method comparison |
| B-VAL56 | Filter: Duration tracking accuracy | Timestamp precision | Data quality |

---

## J. Boost Score Fairness (5 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| B-VAL57 | Filter: Boost Score distribution | Proportional to performance | Skewed distribution |
| B-VAL58 | Filter: Low ACOS high spend ratio vs High ACOS low spend | Fair scoring | Formula bias |
| B-VAL59 | Filter: Campaigns with similar performance | Similar boost scores | Unexplained variance |
| B-VAL60 | Filter: Extreme Boost Score outliers | Reasonable range | Score inflation |
| B-VAL61 | Filter: Boost Score stability | Day-to-day consistency | Volatile scoring |

---

# SUMMARY

| Test Type | Count | Focus Area |
|-----------|-------|------------|
| **Type 1: Verification** | 122 | Classification, Formulas, Triggers, Validation, Amazon Push |
| **Type 2: Validation** | 61 | Accuracy, Redistribution, ACOS/Sales Impact, Fairness |
| **TOTAL** | 183 | |

---

# Key Thresholds to Monitor

| Threshold | Value | Risk |
|-----------|-------|------|
| Minimum Campaign Budget | **$5** (updated Sep 23, 2025) | Active campaigns must have >= $5 |
| Immature Campaign Threshold | 5% of ASIN Ad Spend 30d | Below = Immature classification |
| Maximum Loser Budget Drop | 20% | Cap on budget share reduction |
| Infinite ACOS Value | 9999 | Used when no sales |
| Recalculation Frequency | Every 24 hours | Plus on-demand triggers |
| Budget Push Latency | Near real-time | Amazon sync delay |
| Sum Accuracy | 100% of ASIN budget | No budget leak |

---

# Key Components Overview

| Component | Function | Key Metric |
|-----------|----------|------------|
| **Auto-Budget Toggle** | Enable/disable auto-distribution | Toggle state |
| **ASIN Daily Budget** | Total budget pool | User input |
| **Campaign Classification** | Immature, Fixed, No Activity, Normal | Correct categorization |
| **Winner/Loser Detection** | ACOS vs Target comparison | Delta accuracy |
| **Loser Budget Drop** | Reduce underperformers' share | Max 20% reduction |
| **Winner Boost Score** | Reward outperformers | Proportional boost |
| **Final Budget Calculation** | Sum of all components | Total = ASIN budget |
| **Minimum Enforcement** | $5 floor per campaign | No campaign below |
| **Amazon Push** | Sync to Amazon | Reliability, latency |

---

# Reference Documents

| Source | Description |
|--------|-------------|
| [ASIN Auto Budget Logic_23 Sep'25](https://docs.google.com/spreadsheets/d/1WAwq71ODv9TxmcJEyKQRE1q_p0m3jrmnQopMloj3XpY) | Master formula sheet |
| TEST-60 | Triggers for auto-budget recalculation |
| TEST-61 | Logic columns O, Q, Z |
| TEST-62 | Weighted average budget calculation |
| TEST-65 | Invalid budget validation fix |
| TEST-105 | Validation when auto-budget disabled |
| TEST-200 | Auto Targeting auto budget logic |
| TEST-262 | ASIN Targeting auto budget logic |
| TEST-277 | HP Isolation auto budget |
| TEST-279 | ASIN Targeting auto budget validations |
| TEST-280 | Auto Targeting auto budget validations |

