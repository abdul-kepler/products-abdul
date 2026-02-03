# UAT: Automated Harvesting (EPIC-1108)

## Overview

This document contains comprehensive test cases for the Automated Harvesting feature. Harvesting identifies high-performing search terms from discovery campaigns and promotes them to targeted campaigns for better control.

**Applies to:** Manual KW Targeting (Broad & Phrase), Auto Targeting, ASIN Targeting

---

## Core Harvesting Criteria

A search term qualifies for harvesting if:

```
MAX(ACoS_7d, ACoS_15d, ACoS_30d, ACoS_90d) ≤ Target_ACoS
AND
Lifetime_Ad_Spend(ASIN + Search_Term) ≥ ASIN's Price
```

### Rules

| Rule | Description |
|------|-------------|
| Target ACOS | ASIN-level if available, else Global Target ACOS |
| Zero-Sales Handling | If Ad_Sales = 0 AND Ad_Spend > 0 → Set ACoS = 9999 (auto-fails) |
| Trigger Frequency | Every 24 hours |

---

## Harvesting Routes

| Source Campaign | Search Term Type | Destination | Details |
|-----------------|------------------|-------------|---------|
| **Phrase Match** | Keyword | Exact + Phrase campaigns | Same relevancy group |
| **Broad Match** | Keyword | Dedicated Harvesting Campaign | Per ASIN, `-HV` suffix, starts Paused |
| **Auto Targeting** | Keyword | Dedicated Harvesting Campaign | Per ASIN, `-HV` suffix, starts Paused |
| **Auto Targeting** | ASIN (10-digit) | ASIN Targeting Campaign | Brand group based |

---

## Harvesting Flow Summary

```
[Phrase Campaign]
    → Search Term qualifies
    → Add to Exact + Phrase (same relevancy group)
    → Auto-active (follows source campaign state)

[Broad Campaign]
    → Search Term qualifies
    → Add to Dedicated Harvesting Campaign (per ASIN)
    → Starts Paused, requires manual activation

[Auto Campaign - Keyword]
    → Search Term qualifies
    → Add to Dedicated Harvesting Campaign (per ASIN)
    → Starts Paused, requires manual activation

[Auto Campaign - ASIN]
    → Search Term (ASIN) qualifies
    → Add to ASIN Targeting Campaign (brand group)
    → source_type = "harvested" in backend DB
```

---

## Dedicated Harvesting Campaign Details

| Attribute | Value |
|-----------|-------|
| Naming Convention | `XXXXXX-SPKW-XX01-XX-S-BXXXXXXXXXX-E-HV` |
| Default Status | Paused |
| Activation | Manual only (via Campaign Config UI) |
| Scope | One per ASIN (shared between Broad + Auto) |
| Creation Trigger | First qualifying search term for that ASIN |

---

## ASIN Harvesting Details (Auto → ASIN Targeting)

| Attribute | Description |
|-----------|-------------|
| Search Term Type | 10-digit ASIN (product page where ad appeared) |
| Destination | ASIN Targeting Campaign |
| Brand Grouping | Uses Keepa for brand lookup |
| Backend DB | source_type = "harvested" |
| Campaign Logic | If brand group exists → append; else → create new |

---

# TYPE 1: VERIFICATION TESTS

## A. Core Harvesting Criteria (8 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| H-V01 | Filter: Search term with MAX(ACoS_7d, 15d, 30d, 90d) ≤ Target ACOS AND Lifetime Spend ≥ Price | System Remarks = "Harvested" | Qualifies for harvesting |
| H-V02 | Filter: Search term with MAX(ACoS) > Target ACOS | System Remarks ≠ "Harvested" | Does NOT qualify (ACOS failed) |
| H-V03 | Filter: Search term with Lifetime Spend < Price | System Remarks ≠ "Harvested" | Does NOT qualify (Spend threshold not met) |
| H-V04 | Filter: Search term with Ad_Sales = 0 AND Ad_Spend > 0 | System Remarks ≠ "Harvested" | Zero-sales auto-fails (ACoS = 9999) |
| H-V05 | Filter: Search term with ASIN-level Target ACOS set | Uses ASIN Target ACOS for comparison | ASIN-level takes priority |
| H-V06 | Filter: Search term with NO ASIN-level Target ACOS | Uses Global Target ACOS | Falls back to global |
| H-V07 | Filter: Search term where ACoS_7d > Target but ACoS_30d ≤ Target | Does NOT qualify | MAX() function used, not individual |
| H-V08 | Filter: Check harvesting process timing | Runs every 24 hours | Trigger frequency correct |

---

## B. Phrase Match Harvesting (6 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| H-V09 | Filter: Qualified search term from Phrase campaign | Added to Exact campaign (same relevancy group) | Exact campaign updated |
| H-V10 | Filter: Same qualified search term from Phrase | Also added to Phrase campaign (same relevancy group) | Phrase campaign updated |
| H-V11 | Filter: Harvested keyword in Exact campaign | System Remarks = "Harvested" | UI updated correctly |
| H-V12 | Filter: Harvested keyword in Phrase campaign | System Remarks = "Harvested" | UI updated correctly |
| H-V13 | Filter: Phrase → Exact harvesting, check relevancy group | Campaign belongs to same relevancy group as source | Correct group matching |
| H-V14 | Filter: Search term from Phrase, no matching Exact campaign exists | Check system behavior | Handles missing campaign gracefully |

---

## C. Broad Match Harvesting (7 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| H-V15 | Filter: First qualified search term from Broad campaign for an ASIN | Dedicated Harvesting Campaign created | Campaign auto-created |
| H-V16 | Filter: Campaign naming for harvesting campaign | Name ends with `-HV` suffix | Naming convention correct |
| H-V17 | Filter: Default status of new harvesting campaign | Status = Paused | Not auto-activated |
| H-V18 | Filter: Second qualified search term from Broad (same ASIN) | Added to existing Harvesting Campaign | No duplicate campaign created |
| H-V19 | Filter: Harvested keyword in dedicated campaign | System Remarks = "Harvested" | UI updated correctly |
| H-V20 | Filter: Harvesting campaign in Campaign Config UI | Can be manually activated | Manual activation available |
| H-V21 | Filter: Check if system auto-activates harvesting campaign | Should NOT auto-activate | Requires manual activation |

---

## D. Auto Targeting Harvesting - Keywords (7 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| H-V22 | Filter: Qualified search term (keyword, not ASIN) from Auto campaign | Added to Dedicated Harvesting Campaign | Correct routing |
| H-V23 | Filter: First keyword from Auto for an ASIN | Dedicated Harvesting Campaign created | Campaign auto-created |
| H-V24 | Filter: Campaign naming | Name ends with `-HV` suffix | Naming convention correct |
| H-V25 | Filter: Default status | Status = Paused | Not auto-activated |
| H-V26 | Filter: Subsequent keywords from Auto (same ASIN) | Added to same Harvesting Campaign | No duplicate campaigns |
| H-V27 | Filter: Broad + Auto keywords for same ASIN | Both go to same Dedicated Campaign | Shared harvesting campaign |
| H-V28 | Filter: Harvested keyword from Auto | System Remarks = "Harvested" | UI updated correctly |

---

## E. Auto Targeting Harvesting - ASINs (10 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| H-V29 | Filter: Qualified search term that is an ASIN (10-digit) from Auto campaign | Routes to ASIN Targeting (not Dedicated KW Campaign) | Correct routing for ASIN STs |
| H-V30 | Filter: Harvested ASIN where brand group exists | Appended to existing brand group campaign | No new campaign created |
| H-V31 | Filter: Harvested ASIN where brand group does NOT exist | New campaign created for brand | Campaign auto-created |
| H-V32 | Filter: Backend DB entry for harvested ASIN | source_type = "harvested" | Correct source tagging |
| H-V33 | Filter: Harvested ASIN in ASIN Targeting campaign | System Remarks = "Harvested" | UI updated correctly |
| H-V34 | Filter: Search Term Config for harvested ASIN | System Remarks = "Harvested" | Source ST marked |
| H-V35 | Filter: Harvested ASIN from Auto belonging to ASIN Config "X" | Target added to ASIN Targeting for same ASIN Config | Correct ASIN Config matching |
| H-V36 | Filter: Same ASIN harvested from different Auto campaigns | Check for duplicates | No duplicate targets |
| H-V37 | Filter: Harvested ASIN where ASIN = ASIN Config (self-targeting) | Still qualifies if criteria met | Self-targeting allowed |
| H-V38 | Filter: Brand lookup for harvested ASIN | Brand retrieved from Keepa | Brand identification works |

---

## F. UI Updates (4 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| H-V39 | Filter: Search Term Config for any harvested search term | System Remarks = "Harvested" | ST marked correctly |
| H-V40 | Filter: Keyword Config for any harvested keyword | System Remarks = "Harvested" | KW marked correctly |
| H-V41 | Filter: Qualified but not yet executed | System Remarks ≠ "Harvested" | Only marked AFTER execution |
| H-V42 | Filter: Timestamp of UI update vs harvesting execution | UI updated after execution | Correct trigger timing |

---

# TYPE 2: VALIDATION TESTS

## A. Harvesting Criteria Issues (6 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| H-VAL01 | Filter: Search terms just above Target ACOS (e.g., 31% vs 30% target) | Correctly excluded from harvesting | Borderline accuracy |
| H-VAL02 | Filter: Search terms just below Spend threshold (e.g., $19.99 vs $20 price) | Correctly excluded | Spend threshold accuracy |
| H-VAL03 | Filter: Search terms with volatile ACOS (7d good, 30d bad) | Check MAX() function impact | Short-term spike causing exclusion |
| H-VAL04 | Filter: Search terms with improving trend (90d bad, 7d good) | Still excluded due to MAX() | Good recent performers missed |
| H-VAL05 | Filter: High-price ASINs ($100+) | Spend threshold = $100+ | Takes long to qualify |
| H-VAL06 | Filter: Low-price ASINs ($10-) | Spend threshold = $10- | Qualifies quickly, low data |

---

## B. Phrase Harvesting Issues (4 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| H-VAL07 | Filter: Harvested to Exact but Exact campaign paused/disabled | Keyword added but not active | Wasted harvesting |
| H-VAL08 | Filter: Relevancy group mismatch | Keyword in wrong group | Incorrect targeting |
| H-VAL09 | Filter: Duplicate keywords after harvesting | Same KW already existed | No deduplication |
| H-VAL10 | Filter: Performance of harvested KWs in Exact vs Phrase | Compare ACOS | Exact should outperform |

---

## C. Broad/Auto Keyword Harvesting Issues (5 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| H-VAL11 | Filter: Dedicated Harvesting Campaigns never activated | Keywords sitting unused | Manual activation bottleneck |
| H-VAL12 | Filter: Dedicated Campaigns with many keywords but 0 spend | Campaign paused too long | Missed opportunity |
| H-VAL13 | Filter: Multiple Harvesting Campaigns per ASIN | Should be one per ASIN | Duplicate campaigns |
| H-VAL14 | Filter: Harvesting Campaign naming inconsistent | Some -HW vs -HV | Naming convention error |
| H-VAL15 | Filter: Performance of harvested KWs post-activation | ACOS vs pre-harvest performance | Validates harvesting criteria |

---

## D. ASIN Harvesting Issues (6 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| H-VAL16 | Filter: Harvested ASINs with high ACOS in ASIN Targeting | Performance post-harvest | Criteria not predictive |
| H-VAL17 | Filter: Harvested ASINs in wrong brand group | Brand lookup error | Keepa data issue |
| H-VAL18 | Filter: Harvested ASINs as targets but source ASIN Config different | Cross-ASIN contamination | Routing error |
| H-VAL19 | Filter: ASINs from Auto not appearing in ASIN Targeting | Missed harvesting | Logic gap |
| H-VAL20 | Filter: Duplicate ASIN targets after harvesting | Same ASIN already existed | No deduplication |
| H-VAL21 | Filter: Harvested ASIN performance vs ASIN Research ASINs | Compare ACOS/Ad Sales | Source quality comparison |

---

## E. Timing & Trigger Issues (4 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| H-VAL22 | Filter: Search terms qualified but not harvested for >24 hours | Check trigger execution | Trigger not running |
| H-VAL23 | Filter: Search terms harvested multiple times | Duplicate execution | Trigger running too often |
| H-VAL24 | Filter: Gap between qualification and UI update | Delay in marking | UI sync lag |
| H-VAL25 | Filter: Search terms that qualified then disqualified | ACOS changed after harvest | No reversal mechanism |

---

## F. Business Impact Validation (5 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| H-VAL26 | Filter: Top performers NOT harvested | Why didn't they qualify? | Criteria too strict |
| H-VAL27 | Filter: Harvested keywords with poor post-harvest ACOS | ACOS > Target after harvest | Criteria not predictive |
| H-VAL28 | Filter: % of qualified search terms vs total | Harvesting rate | Too low = missed opportunity |
| H-VAL29 | Filter: Ad Sales from harvested keywords | Contribution to total | Harvesting value |
| H-VAL30 | Filter: Harvesting campaigns vs regular Manual KW performance | ACOS comparison | Validates dedicated campaign approach |

---

# SUMMARY

| Test Type | Count | Focus Area |
|-----------|-------|------------|
| **Type 1: Verification** | 42 | Criteria logic, Routing, Campaign creation, UI updates |
| **Type 2: Validation** | 30 | Threshold accuracy, Performance prediction, Business impact |
| **TOTAL** | 72 | |

---

# Key Thresholds to Monitor

| Threshold | Value | Risk |
|-----------|-------|------|
| ACOS Comparison | MAX(7d, 15d, 30d, 90d) ≤ Target | Recent improvements ignored |
| Spend Threshold | Lifetime Spend ≥ Price | High-price items slow to qualify |
| Zero-Sales | ACoS = 9999 | Auto-exclusion |
| Trigger Frequency | Every 24 hours | Daily batch, not real-time |

---

# Reference Tickets

| Ticket | Description |
|--------|-------------|
| TEST-176 | Core harvesting criteria |
| TEST-177 | UI updates for harvested terms |
| TEST-178 | Phrase match harvesting process |
| TEST-196 | Broad & Auto harvesting to dedicated campaign |
| TEST-197 | Trigger for harvesting process |
| TEST-198 | Activation trigger for harvesting campaigns |
| PROD-368 | Filter ASINs for harvesting (ASIN Targeting) |
| PROD-369 | Update harvested ASINs to backend DB |
| PROD-1108 | Epic: Automated Harvesting |
| PROD-1109 | ASIN Targeting - Harvesting Logic Engine |
| PROD-1110 | ASIN Targeting - Harvesting Routing Engine |
