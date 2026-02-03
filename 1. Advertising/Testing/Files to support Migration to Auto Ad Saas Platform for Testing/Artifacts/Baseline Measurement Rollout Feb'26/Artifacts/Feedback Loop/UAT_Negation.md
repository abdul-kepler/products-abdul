# UAT: Automated Negation

## Overview

This document contains comprehensive test cases for the Automated Negation feature. Negation identifies underperforming search terms and adds them as negative keywords to stop wasting ad spend on non-converting or high-ACOS traffic.

**Applies to:** Manual KW Targeting, Auto Targeting, ASIN Targeting

---

## Core Negation Criteria

A search term qualifies for negation if:

```
MIN(ACoS_7d, ACoS_15d, ACoS_30d, ACoS_90d) > Target_ACoS
AND
Lifetime_Ad_Spend(ASIN + Search_Term) >= ASIN's Price
```

### Rules

| Rule | Description |
|------|-------------|
| Target ACOS | Campaign-level if available, else ASIN-level Target ACOS |
| Zero-Sales Handling | If Ad_Sales = 0 AND Ad_Spend >= Price → Auto-qualifies for negation (worst performer) |
| Reversal | If search term no longer meets criteria → Remove from negation |

**Key Difference from Harvesting:**
- Harvesting: `MAX(ACoS) <= Target` (best case must be good)
- Negation: `MIN(ACoS) > Target` (worst case must be bad)

---

## Negation Components

| Component | Description |
|-----------|-------------|
| System Negation | Automated logic runs on triggers, evaluates criteria |
| Manual Override | User can manually set/clear negative status (takes precedence) |
| Custom Negatives | User can add keywords as negatives without search term data |
| Applied Status | Actual status on Amazon (synced from Amazon) |

---

## Triggers

| Trigger | Frequency | Behavior |
|---------|-----------|----------|
| **#1: Scheduled** | Every 3 hours | Batch evaluation of all search terms |
| **#2: Manual Override** | Immediate | Push to Amazon when user submits |
| **#3: Target ACOS Update** | Immediate | Re-evaluate all search terms for affected ASIN/Campaign |

---

## UI Columns

| Column | Location | Description |
|--------|----------|-------------|
| Negative KW? (Applied Status) | Search Term Config | True/False - actual status on Amazon |
| Negative Status – Manual? | Search Term Config | Dropdown: "Negative" / "Not Negative" |
| Custom Negative Keywords | Campaign Config (Manual KW) | Comma-separated text box |

---

## Negation Flow Summary

```
[Trigger #1: Scheduled - Every 3 Hours]
    → Evaluate all search terms against criteria
    → Negate qualifying terms (unless manual override exists)
    → Remove from negation if no longer qualifies
    → Push changes to Amazon

[Trigger #2: Manual Override]
    → User sets "Negative" or "Not Negative"
    → Immediately push to Amazon
    → System logic bypassed for this ST/Campaign combo
    → UI refreshes within 1 hour

[Trigger #3: Target ACOS Update]
    → Re-evaluate all STs for affected ASIN/Campaign
    → Apply/remove negations based on new Target ACOS
    → Push changes to Amazon
```

---

## Manual Override Precedence

```
If Manual Override = "Negative":
    → Negate (regardless of system logic)
    → System will NOT override

If Manual Override = "Not Negative":
    → Do NOT negate (regardless of system logic)
    → System will NOT override

If Manual Override = Empty/Cleared:
    → System logic applies
    → Can be auto-negated or auto-removed
```

---

# TYPE 1: VERIFICATION TESTS

## A. Core Negation Criteria (10 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| N-V01 | Filter: Search term with MIN(ACoS_7d, 15d, 30d, 90d) > Target ACOS AND Lifetime Spend >= Price | System negates the search term | Qualifies for negation |
| N-V02 | Filter: Search term with MIN(ACoS) <= Target ACOS | Search term NOT negated | Does NOT qualify (ACoS criteria failed) |
| N-V03 | Filter: Search term with Lifetime Spend < Price | Search term NOT negated | Does NOT qualify (Spend threshold not met) |
| N-V04 | Filter: Search term with Ad_Sales = 0 AND Ad_Spend >= Price | System negates the search term | Zero-sales auto-qualifies for negation |
| N-V05 | Filter: Search term with Campaign-level Target ACOS set | Uses Campaign Target ACOS for comparison | Campaign-level takes priority |
| N-V06 | Filter: Search term with NO Campaign-level Target ACOS | Uses ASIN-level Target ACOS | Falls back to ASIN-level |
| N-V07 | Filter: Search term where ACoS_7d > Target but ACoS_30d <= Target | Does NOT qualify | MIN() function used, not individual |
| N-V08 | Filter: Search term where ALL periods > Target ACOS | Qualifies for negation | MIN() still > Target |
| N-V09 | Filter: Previously negated search term now with MIN(ACoS) <= Target | Removed from negation | Reversal mechanism works |
| N-V10 | Filter: Previously negated, now Spend < Price (recalculated) | Remains negated (historical decision) | No reversal on spend drop |

---

## B. Trigger #1: Scheduled (8 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| N-V11 | Filter: Check negation process timing | Runs every 3 hours | Trigger frequency correct |
| N-V12 | Filter: Search term qualifying between trigger runs | Not negated until next trigger | Batch processing, not real-time |
| N-V13 | Filter: Multiple qualifying search terms at same trigger | All processed in same batch | Batch handles multiple STs |
| N-V14 | Filter: Negated search terms pushed to Amazon | Appears as negative keyword on Amazon | Amazon sync successful |
| N-V15 | Filter: Search terms un-negated (no longer qualify) | Removed from Amazon negatives | Reversal pushed to Amazon |
| N-V16 | Filter: Trigger execution log | Logged with timestamp | Logging implemented |
| N-V17 | Filter: Same search term in multiple campaigns | Evaluated independently per campaign | Campaign-specific negation |
| N-V18 | Filter: Trigger runs when no search terms qualify | Completes without error | Graceful empty handling |

---

## C. Trigger #2: Manual Override (10 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| N-V19 | Filter: User selects "Negative" for a search term | Immediately pushed to Amazon as negative | Manual negation works |
| N-V20 | Filter: User selects "Not Negative" for a negated term | Immediately removed from Amazon negatives | Manual un-negation works |
| N-V21 | Filter: Manual "Negative" on term that doesn't meet criteria | Still negated (manual takes precedence) | Override system logic |
| N-V22 | Filter: Manual "Not Negative" on term that meets criteria | NOT negated (manual takes precedence) | Override system logic |
| N-V23 | Filter: Scheduled trigger runs after manual override | Manual status unchanged | System doesn't override manual |
| N-V24 | Filter: Clear manual override on previously manual-negated term | System logic re-applies | Override cleared, system takes over |
| N-V25 | Filter: UI "Negative KW?" column after manual change | Updates within 1 hour | UI sync timing |
| N-V26 | Filter: Manual override dropdown options | Shows "Negative" and "Not Negative" | UI correct |
| N-V27 | Filter: Manual override persists across sessions | Same value shown on re-login | Persistence works |
| N-V28 | Filter: Manual override via bulk edit | All selected rows updated | Bulk edit works |

---

## D. Trigger #3: Target ACOS Update (8 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| N-V29 | Filter: Update Campaign-level Target ACOS (lower) | Previously safe STs now qualify for negation | Re-evaluation triggered |
| N-V30 | Filter: Update Campaign-level Target ACOS (higher) | Previously negated STs may be un-negated | Re-evaluation removes negation |
| N-V31 | Filter: Update ASIN-level Target ACOS | Re-evaluates STs using ASIN Target | ASIN-level trigger works |
| N-V32 | Filter: Campaign has custom Target ACOS, ASIN updated | No change (Campaign takes precedence) | Hierarchy respected |
| N-V33 | Filter: ASIN Target update on campaign without custom Target | Re-evaluates using new ASIN Target | Falls back correctly |
| N-V34 | Filter: Target ACOS update with manual overrides | Manual overrides unchanged | Manual takes precedence |
| N-V35 | Filter: Target ACOS update timing | Re-evaluation runs immediately | Not waiting for scheduled trigger |
| N-V36 | Filter: Target ACOS update pushes to Amazon | Changes reflected on Amazon | Amazon sync after re-evaluation |

---

## E. UI: Applied Negative Status (6 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| N-V37 | Filter: Search term negated by system | "Negative KW?" = True | Column shows correct status |
| N-V38 | Filter: Search term NOT negated | "Negative KW?" = False | Column shows correct status |
| N-V39 | Filter: Negation pushed to Amazon, check UI | UI updates within 24 hours (scheduled) | UI sync on schedule |
| N-V40 | Filter: Negation pushed to Amazon via manual override | UI updates within 1 hour | Faster UI sync for manual |
| N-V41 | Filter: "Negative KW?" column fetches from Amazon | Reflects actual Amazon status | Not just local DB |
| N-V42 | Filter: Search term removed from negation | "Negative KW?" changes to False | Status reversal shown |

---

## F. Custom Negative Keywords (8 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| N-V43 | Filter: Campaign Config UI, Manual KW Targeting tab | "Custom Negative Keywords" column exists | UI column present |
| N-V44 | Filter: Enter comma-separated keywords | All keywords added as negatives | Multi-entry works |
| N-V45 | Filter: Remove keyword from Custom Negative Keywords | Keyword removed from campaign negatives | Removal works |
| N-V46 | Filter: Custom negatives pushed to Amazon | Appears as negative keyword on Amazon | Amazon sync works |
| N-V47 | Filter: Custom negative keyword that never appeared as search term | Still added as negative | No search term data required |
| N-V48 | Filter: Bulk import template with Custom Negative Keywords column | Column exists at end of template | Bulk import template updated |
| N-V49 | Filter: Bulk import with Custom Negative Keywords | Keywords added from import | Bulk import processing works |
| N-V50 | Filter: Invalid characters in Custom Negative Keywords | Validation error shown | Client-side validation |

---

## G. Multi-Targeting Type Tests (6 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| N-V51 | Filter: Negation in Manual KW Targeting campaign | Works as documented | Manual KW supported |
| N-V52 | Filter: Negation in Auto Targeting campaign | Works as documented | Auto Targeting supported |
| N-V53 | Filter: Negation in ASIN Targeting campaign | Works as documented | ASIN Targeting supported |
| N-V54 | Filter: Same search term across different targeting types | Evaluated independently per campaign/type | Type-specific negation |
| N-V55 | Filter: ASIN as search term (ASIN Targeting) negated | ASIN added as negative ASIN target | Correct negative type |
| N-V56 | Filter: Keyword as search term negated | Keyword added as negative keyword | Correct negative type |

---

# TYPE 2: VALIDATION TESTS

## A. Negation Criteria Issues (8 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| N-VAL01 | Filter: Search terms just below Target ACOS (e.g., 29% vs 30% target) | Correctly NOT negated | Borderline accuracy |
| N-VAL02 | Filter: Search terms just above Target ACOS (e.g., 31% vs 30% target) | Correctly negated | Borderline accuracy |
| N-VAL03 | Filter: Search terms with volatile ACOS (7d bad, 30d good) | Check MIN() function impact | Recent spike causing false positive |
| N-VAL04 | Filter: Search terms with improving trend (90d bad, 7d good) | Still NOT negated (MIN is good) | Improving performers protected |
| N-VAL05 | Filter: High-price ASINs ($100+) | Spend threshold = $100+ | Takes long to qualify |
| N-VAL06 | Filter: Low-price ASINs ($10-) | Spend threshold = $10- | Qualifies quickly, low data |
| N-VAL07 | Filter: Search terms with exactly Price spend | Should qualify if ACoS > Target | Boundary condition |
| N-VAL08 | Filter: Search terms with near-zero spend but bad ACOS | Should NOT qualify (spend threshold) | Premature negation prevented |

---

## B. False Positive Issues (6 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| N-VAL09 | Filter: Negated search terms that later showed good performance (un-negated) | How often does reversal happen? | Criteria may be too aggressive |
| N-VAL10 | Filter: Negated search terms with high potential (high impressions, low clicks) | May be visibility issue, not term quality | Negating opportunity |
| N-VAL11 | Filter: Seasonal search terms negated in off-season | ACOS bad in off-season | Seasonal false positive |
| N-VAL12 | Filter: New search terms negated quickly | Limited data leading to negation | Insufficient data threshold |
| N-VAL13 | Filter: High-converting search terms negated (CVR > 10%) | Why is ACOS still bad? | Price/bid issue, not term quality |
| N-VAL14 | Filter: Branded search terms negated | Brand terms usually convert well | May indicate data issue |

---

## C. False Negative Issues (6 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| N-VAL15 | Filter: Search terms with consistently bad ACOS NOT negated | Why didn't they qualify? | Spend threshold too high |
| N-VAL16 | Filter: Search terms with 0 orders but NOT negated | Spend < Price | Wasting spend below threshold |
| N-VAL17 | Filter: Search terms with ACOS > 2× Target not negated | Check spend threshold | Obvious underperformers missed |
| N-VAL18 | Filter: Clearly irrelevant search terms not negated | Check criteria | Irrelevant traffic not caught |
| N-VAL19 | Filter: Search terms draining budget but below spend threshold | Cumulative spend impact | Threshold may be too high |
| N-VAL20 | Filter: % of search terms meeting criteria vs negated | Gap in execution | Logic vs execution mismatch |

---

## D. Manual Override Issues (5 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| N-VAL21 | Filter: Manual overrides that conflict with system logic | Performance after override | User judgment vs system |
| N-VAL22 | Filter: Manual "Not Negative" overrides on bad performers | Continued poor performance | User protecting bad terms |
| N-VAL23 | Filter: Manual "Negative" overrides on good performers | Lost opportunity | User negating good terms |
| N-VAL24 | Filter: Stale manual overrides (set long ago) | Performance change since override | Override may be outdated |
| N-VAL25 | Filter: Manual overrides never cleared | Accumulation over time | Override hygiene |

---

## E. Timing & Trigger Issues (6 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| N-VAL26 | Filter: Search terms qualified but not negated for >3 hours | Check trigger execution | Trigger not running |
| N-VAL27 | Filter: Search terms negated multiple times (duplicate execution) | Check trigger frequency | Trigger running too often |
| N-VAL28 | Filter: Gap between negation and Amazon sync | Delay in pushing | Sync lag |
| N-VAL29 | Filter: Gap between Amazon sync and UI update | Delay in UI refresh | UI sync lag |
| N-VAL30 | Filter: Negations during Target ACOS change | Timing of re-evaluation | Re-evaluation timing |
| N-VAL31 | Filter: Multiple triggers overlapping (scheduled + ACOS update) | Conflict handling | Trigger collision |

---

## F. Business Impact Validation (7 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| N-VAL32 | Filter: Ad spend before vs after negation | Spend reduction | Negation effectiveness |
| N-VAL33 | Filter: ACOS before vs after negation | ACOS improvement | Quality of negation decisions |
| N-VAL34 | Filter: Ad sales before vs after negation | Sales impact | Not losing sales from negation |
| N-VAL35 | Filter: % of search terms negated vs total | Negation rate | Too low = missed savings, Too high = over-aggressive |
| N-VAL36 | Filter: Negated search term count per campaign | Distribution | Identify problem campaigns |
| N-VAL37 | Filter: Negation frequency per ASIN | Which ASINs have most negations | ASIN quality indicator |
| N-VAL38 | Filter: Custom negatives vs system negatives | Source distribution | User vs system contribution |

---

## G. Amazon Sync Issues (5 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| N-VAL39 | Filter: Negations in portal vs negatives on Amazon | Mismatch | Sync failure |
| N-VAL40 | Filter: Negatives on Amazon not in portal | External changes | Amazon-side modifications |
| N-VAL41 | Filter: Negation push failures | Amazon API errors | API reliability |
| N-VAL42 | Filter: Bulk negation push performance | Processing time | Scalability |
| N-VAL43 | Filter: "Negative KW?" accuracy vs Amazon | Refresh accuracy | Fetch reliability |

---

# SUMMARY

| Test Type | Count | Focus Area |
|-----------|-------|------------|
| **Type 1: Verification** | 56 | Criteria logic, Triggers, Manual override, UI, Custom negatives |
| **Type 2: Validation** | 43 | False positives/negatives, Timing, Business impact, Amazon sync |
| **TOTAL** | 99 | |

---

# Key Thresholds to Monitor

| Threshold | Value | Risk |
|-----------|-------|------|
| ACOS Comparison | MIN(7d, 15d, 30d, 90d) > Target | Recent improvements protect terms |
| Spend Threshold | Lifetime Spend >= Price | Low-spend terms not evaluated |
| Trigger Frequency | Every 3 hours | Near real-time for scheduled |
| Manual UI Refresh | Within 1 hour | Fast feedback for manual actions |
| Scheduled UI Refresh | Within 24 hours | Batch refresh for system actions |

---

# Key Differences: Negation vs Harvesting

| Aspect | Harvesting | Negation |
|--------|------------|----------|
| **Goal** | Promote best performers | Remove worst performers |
| **ACOS Condition** | MAX(ACoS) <= Target | MIN(ACoS) > Target |
| **Interpretation** | Best case is good | Worst case is bad |
| **Spend Condition** | Same (>= Price) | Same (>= Price) |
| **Zero Sales** | Fails harvesting (ACoS=9999) | Qualifies for negation |
| **Action** | Add to targeted campaigns | Add to negative keywords |

---

# Reference Tickets

| Ticket | Description |
|--------|-------------|
| TEST-43 | Display negative status from Amazon |
| TEST-44 | Manual override precedence logic |
| TEST-55 | Trigger #3: Target ACOS update |
| TEST-161 | Custom Negative KWs in Campaign Config UI |
| TEST-165 | Custom Negative KWs in Bulk Import template |
| PROD-43 | Trigger #1 frequency change (24h → 3h) |
| AD-62 | Original Trigger #1 (scheduled) |
| AD-85 | Trigger #2 (manual override) |
| AD-86 | Trigger #3 (Target ACOS update) |
| AD-61 | Core negation logic (referenced) |

