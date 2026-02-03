# UAT: High Performers Isolation (PROD-1112)

## Overview

This document contains comprehensive test cases for the Automated High Performers Isolation feature. Isolation identifies top-performing search terms and promotes them to dedicated "solo" campaigns for greater control, better optimization, and reduced cannibalization.

**Two Types of Isolation:**
1. **Manual KW Targeting Isolation**: Keyword search terms → Solo SPKW Exact campaigns
2. **ASIN Targeting Isolation**: ASIN search terms (10-digit) → Solo ASIN Targeting campaigns

---

## High Performer Criteria

A search term qualifies as a **high performer** if ALL conditions are met:

```
1. Top 5% Rank by Ad Sales (30D)
   - Must rank in top 5% of all search terms for same ASIN
   - If 5% < 5 terms → use that count
   - If 5% > 5 terms → cap at TOP 5 only

2. Consistent ACOS Performance
   MAX(ACoS_1d, ACoS_3d, ACoS_7d, ACoS_15d, ACoS_30d) <= Campaign Target ACOS

3. ASIN Order Volume
   Ad_Orders_30d (ASIN-level) >= 100
```

---

## Trigger Frequency

| Trigger | Frequency | Action |
|---------|-----------|--------|
| **High Performer Filtering** | Every 7 days | Evaluate search terms against criteria |
| **Solo Campaign Creation** | On qualification | Create paused solo campaign |
| **Solo Activation** | Manual | User activates solo campaign |
| **Keyword Auto-Pause** | On solo activation | Pause exact KWs in other campaigns |
| **Keyword Auto-Enable** | On solo deactivation | Re-enable previously system-paused KWs |

---

## Solo Campaign Configuration

### Manual KW Targeting (Keyword Search Terms)

| Attribute | Value |
|-----------|-------|
| **Naming Convention** | `HPXXXX-SPKW-[BrandCode]-XX-S-[ASIN]-E-[KW]` |
| **Match Type** | Exact |
| **Targeting Type** | Manual Keyword |
| **Bidding Strategy** | Down Only |
| **Placement Modifier** | None |
| **Keywords** | Single high-performing search term |
| **Negatives** | None |
| **Default State** | Paused |
| **Activation** | Manual by user |

### ASIN Targeting (ASIN Search Terms)

| Attribute | Value |
|-----------|-------|
| **Naming Convention** | Similar, with ASIN as target |
| **Targeting Type** | ASIN Targeting |
| **Targets** | Single 10-digit ASIN (the search term) |
| **Default State** | Paused |
| **Activation** | Manual by user |

---

## Auto-Pause Mechanism

```
[Solo Campaign Activated]
    → Find exact match KWs matching high-performing search term
    → In other campaigns (same ASIN)
    → Auto-pause those KWs
    → Mark: "Paused – Exists in HP Solo Campaign"

[Solo Campaign Deactivated]
    → Find previously system-paused KWs
    → Re-enable them
    → UNLESS manually paused by user (don't touch)
```

**Scope:**
- Only **exact match** keywords affected
- Only keywords from **same ASIN**
- **Phrase/Broad** match types NOT affected
- **Manual user pauses** are preserved (not auto-enabled)

---

## UI Updates

### Search Term Config

| Column | Display |
|--------|---------|
| **System Remarks** | "High Performing" (for qualifying search terms) |

### KW Config

| Column | Display |
|--------|---------|
| **System Remarks** | "High Performing" (for KW in solo campaign) |
| **System Remarks** | "Paused – Exists in HP Solo Campaign" (for auto-paused KWs) |

### Campaign Config

| Column | Display |
|--------|---------|
| **Targeted KW** or **Relevancy** | Shows the keyword being targeted (for solo campaigns) |
| **Target ACOS** | Editable |
| **Budget** | Editable |
| **Status** | Editable |

---

# TYPE 1: VERIFICATION TESTS

## A. High Performer Criteria - Top 5% Rank (8 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| I-V01 | Filter: Search term in top 5% by Ad Sales (30D) for its ASIN | Marked as "High Performing" | Qualifies |
| I-V02 | Filter: Search term NOT in top 5% by Ad Sales | Not marked | Does not qualify |
| I-V03 | Filter: ASIN with 50 search terms (5% = 2.5 terms) | Top 2 or 3 qualify | 5% rule applied |
| I-V04 | Filter: ASIN with 200 search terms (5% = 10 terms) | Only Top 5 qualify | Capped at 5 |
| I-V05 | Filter: ASIN with 10 search terms (5% = 0.5 terms) | At least Top 1 qualifies | Minimum 1 rule |
| I-V06 | Filter: Tied Ad Sales at rank boundary | Check tie-breaking | Consistent behavior |
| I-V07 | Filter: Search term with $0 Ad Sales | Cannot be top 5% | Zero-sales excluded |
| I-V08 | Filter: 30-day lookback boundary | Uses exact 30 days | Lookback correct |

---

## B. High Performer Criteria - ACOS (8 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| I-V09 | Filter: Top 5% search term with MAX(ACoS) <= Target | Qualifies as high performer | ACOS check passes |
| I-V10 | Filter: Top 5% search term with MAX(ACoS) > Target | Does NOT qualify | ACOS check fails |
| I-V11 | Filter: Search term with 1d ACOS spike > Target (but 30d <= Target) | Does NOT qualify | MAX() function used |
| I-V12 | Filter: Search term with all periods <= Target | Qualifies | All periods good |
| I-V13 | Filter: Campaign-level Target ACOS used | Correct Target applied | Campaign priority |
| I-V14 | Filter: No Campaign Target, ASIN Target exists | Uses ASIN Target | Fallback works |
| I-V15 | Filter: Search term with 0 sales (no ACOS data) | Check handling | Edge case |
| I-V16 | Filter: Compare MAX(1d, 3d, 7d, 15d, 30d) calculation | Correct MAX used | Formula correct |

---

## C. High Performer Criteria - Order Volume (6 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| I-V17 | Filter: ASIN with >= 100 Ad Orders (30D) | Search terms can qualify | Volume threshold met |
| I-V18 | Filter: ASIN with < 100 Ad Orders (30D) | No search terms qualify | Volume threshold not met |
| I-V19 | Filter: ASIN with exactly 100 Ad Orders | Qualifies | Boundary included |
| I-V20 | Filter: ASIN with 99 Ad Orders | Does NOT qualify | Boundary respected |
| I-V21 | Filter: Order count at ASIN level (not search term) | Aggregated correctly | Correct level |
| I-V22 | Filter: New ASIN with limited history | Handle appropriately | Cold start |

---

## D. Trigger & Scheduling (6 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| I-V23 | Filter: High performer filtering schedule | Runs every 7 days | Frequency correct |
| I-V24 | Filter: Search term qualifying mid-cycle | Not processed until next 7-day run | Batch processing |
| I-V25 | Filter: Multiple ASINs processed in same run | All evaluated | Complete coverage |
| I-V26 | Filter: High performer list updated after run | New qualifiers added | List maintained |
| I-V27 | Filter: Search term no longer qualifies | Status removed | Disqualification works |
| I-V28 | Filter: Trigger execution logging | Logged with timestamp | Audit trail |

---

## E. Solo Campaign Creation - Manual KW (10 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| I-V29 | Filter: New high performer identified | Solo campaign created | Auto-creation works |
| I-V30 | Filter: Solo campaign naming convention | Format: `HPXXXX-SPKW-[BrandCode]-XX-S-[ASIN]-E-[KW]` | Naming correct |
| I-V31 | Filter: Brand code assignment | Unique 4-char code per brand | Brand codes correct |
| I-V32 | Filter: Long keyword name | Truncated with underscore | Truncation works |
| I-V33 | Filter: Solo campaign default state | Created as PAUSED | Not auto-activated |
| I-V34 | Filter: Solo campaign match type | Exact match only | Match type correct |
| I-V35 | Filter: Solo campaign bidding strategy | Down Only | Strategy correct |
| I-V36 | Filter: Solo campaign has single keyword | Only the high performer KW | 1 KW per campaign |
| I-V37 | Filter: Same search term qualifies again | No duplicate solo campaign | Deduplication |
| I-V38 | Filter: Solo campaign appears in Campaign Config | Visible in UI | UI updated |

---

## F. Solo Campaign Creation - ASIN Targeting (8 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| I-V39 | Filter: Search term is 10-digit ASIN | Routed to ASIN Targeting isolation | Correct routing |
| I-V40 | Filter: Search term is keyword (not ASIN) | Routed to Manual KW isolation | Correct routing |
| I-V41 | Filter: ASIN search term solo campaign | Created as ASIN Targeting campaign | Campaign type correct |
| I-V42 | Filter: ASIN solo campaign default state | Created as PAUSED | Not auto-activated |
| I-V43 | Filter: ASIN solo campaign has single target | Only the high performer ASIN | 1 target per campaign |
| I-V44 | Filter: Same ASIN qualifies again | No duplicate solo campaign | Deduplication |
| I-V45 | Filter: ASIN solo campaign in Campaign Config | Visible in UI | UI updated |
| I-V46 | Filter: Mix of KW and ASIN search terms qualifying | Both types processed correctly | Multi-type handling |

---

## G. Auto-Pause Mechanism (10 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| I-V47 | Filter: Solo campaign activated | Exact KWs in other campaigns (same ASIN) paused | Auto-pause triggers |
| I-V48 | Filter: System remark on auto-paused KW | "Paused – Exists in HP Solo Campaign" | Remark shown |
| I-V49 | Filter: Exact match KWs only | Phrase/Broad KWs NOT paused | Match type scope |
| I-V50 | Filter: KWs in different ASIN campaigns | NOT paused | ASIN scope |
| I-V51 | Filter: KW in solo campaign row | Does NOT show "Paused" remark | Solo excluded |
| I-V52 | Filter: Solo campaign deactivated | Previously system-paused KWs re-enabled | Auto-enable works |
| I-V53 | Filter: Manually paused KW when solo activated | Remains paused after solo deactivated | Manual override preserved |
| I-V54 | Filter: KW auto-paused then manually paused | Stays paused after solo deactivated | Manual takes precedence |
| I-V55 | Filter: Multiple campaigns have same exact KW | All are paused | Multi-campaign scope |
| I-V56 | Filter: Rapid solo activate/deactivate | Stable state management | No flip-flop issues |

---

## H. Manual Override & User Control (8 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| I-V57 | Filter: User manually activates solo campaign | Campaign becomes ACTIVE | Manual activation |
| I-V58 | Filter: User manually pauses solo campaign | Campaign becomes PAUSED | Manual pause |
| I-V59 | Filter: User edits Target ACOS on solo campaign | Update saved | Campaign Config works |
| I-V60 | Filter: User edits Budget on solo campaign | Update saved | Campaign Config works |
| I-V61 | Filter: User manually pauses a KW via KW Config | Override persists | Manual KW control |
| I-V62 | Filter: User manually enables a KW via bulk file | Override persists | Bulk control |
| I-V63 | Filter: User deletes solo campaign | Campaign removed | Deletion works |
| I-V64 | Filter: After solo deletion, auto-paused KWs | Re-enabled (if not manually paused) | Cleanup works |

---

## I. UI Updates (8 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| I-V65 | Filter: High performer in Search Term Config | System Remarks = "High Performing" | ST UI correct |
| I-V66 | Filter: High performer KW in solo campaign (KW Config) | System Remarks = "High Performing" | KW UI correct |
| I-V67 | Filter: Auto-paused KW in KW Config | System Remarks = "Paused – Exists in HP Solo Campaign" | Pause remark correct |
| I-V68 | Filter: Solo campaign in Campaign Config | "Targeted KW" column shows keyword | Campaign UI correct |
| I-V69 | Filter: Solo campaign editable fields | Target ACOS, Budget, Status editable | Edit capability |
| I-V70 | Filter: Non-high performer search term | No "High Performing" remark | Correct exclusion |
| I-V71 | Filter: Search term loses high performer status | Remark removed | Status update |
| I-V72 | Filter: UI refresh after isolation run | Updates visible | Sync timing |

---

# TYPE 2: VALIDATION TESTS

## A. Criteria Threshold Issues (8 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| I-VAL01 | Filter: Search terms just outside top 5% | Why didn't they qualify? | Threshold sensitivity |
| I-VAL02 | Filter: Top 5% with MAX(ACOS) just above Target | Excluded despite high sales | ACOS threshold impact |
| I-VAL03 | Filter: ASINs with exactly 100 orders (boundary) | Qualification stability | Boundary sensitivity |
| I-VAL04 | Filter: High performers that later underperform | Did criteria predict well? | Criteria accuracy |
| I-VAL05 | Filter: Search terms with volatile ACOS (1d spike) | Excluded despite good average | MAX() function impact |
| I-VAL06 | Filter: Low-order ASINs with great performers | Cannot qualify | Volume threshold too high |
| I-VAL07 | Filter: ASINs with many similar performers | Only 5 qualify | Cap impact |
| I-VAL08 | Filter: Top 5% calculation accuracy | Verify percentile | Math check |

---

## B. Solo Campaign Performance (8 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| I-VAL09 | Filter: Solo campaign ACOS vs pre-isolation ACOS | Performance change | Isolation effectiveness |
| I-VAL10 | Filter: Solo campaign Ad Sales vs pre-isolation | Sales change | Revenue impact |
| I-VAL11 | Filter: Solo campaigns never activated | Opportunity cost | Activation bottleneck |
| I-VAL12 | Filter: Activated solo campaigns with poor performance | ACOS > Target | Criteria not predictive |
| I-VAL13 | Filter: Time from qualification to activation | User delay | Adoption/awareness |
| I-VAL14 | Filter: Solo campaign vs regular campaign performance | Compare efficiency | Isolation value |
| I-VAL15 | Filter: Solo campaigns with declining performance | Trend analysis | Performance decay |
| I-VAL16 | Filter: Cost of solo campaign management | Overhead | Operational burden |

---

## C. Auto-Pause Impact (6 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| I-VAL17 | Filter: KWs auto-paused, performance impact on campaigns | Sales/ACOS change | Cannibalization reduction |
| I-VAL18 | Filter: KWs auto-paused incorrectly (not exact match) | Scope error | Logic bug |
| I-VAL19 | Filter: KWs auto-enabled but shouldn't be | Manual override lost | Persistence bug |
| I-VAL20 | Filter: Campaigns with many KWs auto-paused | Campaign performance | Concentration risk |
| I-VAL21 | Filter: Solo + non-solo running simultaneously | Overlap detection | Auto-pause failure |
| I-VAL22 | Filter: User confusion about auto-paused KWs | Support tickets | UX clarity |

---

## D. Business Impact (7 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| I-VAL23 | Filter: Total Ad Sales from high performers pre vs post isolation | Sales change | Feature value |
| I-VAL24 | Filter: Total ACOS from high performers pre vs post isolation | Efficiency change | Feature value |
| I-VAL25 | Filter: % of search terms qualifying as high performers | Rate | Too low = limited impact |
| I-VAL26 | Filter: % of solo campaigns activated | Adoption | User engagement |
| I-VAL27 | Filter: Budget allocation to solo vs regular campaigns | Distribution | Budget shift |
| I-VAL28 | Filter: High performer contribution to total Ad Sales | Concentration | Top performer importance |
| I-VAL29 | Filter: A/B: Isolation ON vs OFF | Performance difference | Feature validation |

---

## E. Edge Cases & Timing (6 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| I-VAL30 | Filter: Search term qualifies then disqualifies | Status change handling | Lifecycle management |
| I-VAL31 | Filter: Solo campaign exists but search term no longer qualifies | Orphan campaign | Cleanup needed |
| I-VAL32 | Filter: Multiple search terms from same ASIN qualify | All get solo campaigns | Multi-isolation |
| I-VAL33 | Filter: Same search term across multiple ASINs | Independent treatment | ASIN scope |
| I-VAL34 | Filter: 7-day cycle boundary cases | Timing accuracy | Schedule reliability |
| I-VAL35 | Filter: High volume of new qualifiers | Processing capacity | Scale handling |

---

## F. ASIN Targeting Isolation (6 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| I-VAL36 | Filter: ASIN search term solo campaigns performance | ACOS/Sales | ASIN isolation value |
| I-VAL37 | Filter: ASIN vs KW isolation comparison | Which performs better? | Type comparison |
| I-VAL38 | Filter: ASIN isolation adoption rate | % activated | User engagement |
| I-VAL39 | Filter: ASIN solo campaigns with poor performance | Criteria quality | ASIN-specific issues |
| I-VAL40 | Filter: ASIN overlap with ASIN Targeting campaigns | Conflict detection | Campaign structure |
| I-VAL41 | Filter: 10-digit ASIN detection accuracy | Routing correctness | Classification accuracy |

---

# SUMMARY

| Test Type | Count | Focus Area |
|-----------|-------|------------|
| **Type 1: Verification** | 72 | Criteria logic, Campaign creation, Auto-pause, UI |
| **Type 2: Validation** | 41 | Threshold accuracy, Performance, Business impact |
| **TOTAL** | 113 | |

---

# Key Thresholds to Monitor

| Threshold | Value | Risk |
|-----------|-------|------|
| Top 5% Rank | Top 5% by Ad Sales (capped at 5) | Too many/few qualifiers |
| ACOS Comparison | MAX(1d, 3d, 7d, 15d, 30d) <= Target | Recent spikes cause exclusion |
| Order Volume | >= 100 Ad Orders (ASIN, 30D) | Low-volume ASINs excluded |
| Trigger Frequency | Every 7 days | Weekly batch |
| Auto-Pause Scope | Exact match only, same ASIN | Limited scope |

---

# Key Differences: Isolation vs Harvesting

| Aspect | Harvesting | Isolation |
|--------|------------|-----------|
| **Goal** | Promote to targeted campaigns | Give dedicated campaign |
| **Criteria** | MAX(ACOS) <= Target, Spend >= Price | Top 5%, MAX(ACOS) <= Target, 100+ orders |
| **Campaign** | Existing campaigns (Exact/Phrase/-HV) | New solo campaign (1 KW only) |
| **State** | May be active | Always starts PAUSED |
| **Auto-Pause** | No | Yes (exact KWs in other campaigns) |
| **Trigger** | Every 24 hours | Every 7 days |

---

# Reference Tickets

| Ticket | Description |
|--------|-------------|
| PROD-1112 | Epic: Automated High Performers Isolation |
| PROD-1113 | ASIN Targeting - Isolation Logic Engine |
| PROD-1130 | Manual KW Targeting - Isolation Logic Engine |
| PROD-14 | UI Updates for Isolation |
| TEST-225 | Trigger for isolation logic |
| TEST-226 | Solo campaign creation |
| TEST-227 | Auto-pause mechanism |
| TEST-240 | High performer filtering criteria |
| TEST-277 | Auto budget for isolation campaigns |

