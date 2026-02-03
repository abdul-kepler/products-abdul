# UAT: Automated Keyword Research

## Overview

This document contains comprehensive test cases for the Automated Keyword Research feature. The system uses AI (OpenAI/LLM) to automatically classify keywords based on branding scope and product relationship, rank listing attributes, and group keywords for campaign optimization.

**Applies to:** All ASIN-level keyword research and classification workflows

**Source:** PROD-1099 (Epic), PROD-116, PROD-117, PROD-118, PROD-130, PROD-131, PROD-132, PROD-1102, PROD-1264

---

## How Automated KW Research Works

### High-Level Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TRIGGER: KW Fetching Completed (from JungleScout)        │
│                           OR Manual Trigger via UI                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                STEP 1: FETCH ASIN CONTENT FROM PDP                          │
│                                                                              │
│  Scrape/Fetch from Amazon PDP or 3rd party (Keepa):                         │
│    • Title                                                                   │
│    • Bullet Points                                                           │
│    • Description                                                             │
│    • Product Attributes                                                      │
│    • (Optional) User-provided Product Details                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│         STEP 2: RUN PROMPT #1 & PROMPT #2 (Parallel via OpenAI)             │
│                                                                              │
│  ┌─────────────────────────────┐   ┌─────────────────────────────┐         │
│  │       PROMPT #1             │   │       PROMPT #2             │         │
│  │                             │   │                             │         │
│  │  Branding Scope:            │   │  Listing Attributes:        │         │
│  │   • NB (Non-Branded)        │   │   • Product Types (PT)      │         │
│  │   • OB (Own-Branded)        │   │   • Variants (V)            │         │
│  │   • CB (Competitor-Branded) │   │   • Use Cases (U)           │         │
│  │                             │   │   • Audiences (A)           │         │
│  │  KW-Product Relationship:   │   │                             │         │
│  │   • R (Relevant)            │   │  Ranking: Most specific     │         │
│  │   • S (Substitute)          │   │  to broadest                │         │
│  │   • C (Complementary)       │   │                             │         │
│  │   • N (Negative)            │   │                             │         │
│  └─────────────────────────────┘   └─────────────────────────────┘         │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    USER REVIEW & EDIT (UI #1 & UI #2)                       │
│                                                                              │
│  User can review, edit, add, delete outputs before proceeding               │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STEP 3: RUN PROMPT #3 (via OpenAI)                       │
│                                                                              │
│  KW Grouping & Ranking:                                                      │
│    • Groups KWs by attribute combinations                                   │
│    • Assigns Group # and Rank # to each KW                                  │
│    • Creates 4 output tables:                                               │
│      1. Non-Branded KWs                                                     │
│      2. Own-Branded KWs                                                     │
│      3. Competitor-Branded KWs                                              │
│      4. Keywords: Branding & Relationship Summary                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    USER REVIEW & SUBMIT (UI #3)                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│              STEP 4: UPDATE KW RESEARCH UI WITH RELEVANCE TAGS              │
│                                                                              │
│  Final tags format: [Branding][Relationship][Group/Rank]                    │
│  Examples: NBR1, OBS2, CBC3, NBN1                                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Key Concepts

### Branding Scope Classification

| Code | Classification | Definition |
|------|---------------|------------|
| **NB** | Non-Branded | Keywords with NO brand names (own or competitor), including misspellings |
| **OB** | Own-Branded | Keywords containing ONLY own brand name or misspelled own brand |
| **CB** | Competitor-Branded | Keywords containing ONLY competitor brand name or misspelled competitor brand |

### KW-Product Relationship Classification

| Code | Classification | Definition |
|------|---------------|------------|
| **R** | Relevant | Directly relates to the product or product type |
| **S** | Substitute | Represents a substitute for the product, PT, or variant |
| **C** | Complementary | Something typically used WITH the product |
| **N** | Negative | Should be excluded (irrelevant, wrong variant/audience) |

### Relevance Tag Format

```
[Branding Scope][Relationship][Group/Rank#]

Examples:
  NBR1 = Non-Branded + Relevant + Rank 1
  OBS2 = Own-Branded + Substitute + Rank 2
  CBC3 = Competitor-Branded + Complementary + Rank 3
  NBN1 = Non-Branded + Negative + Rank 1
```

### Product Type (PT) Hierarchy Rules

1. **Purity**: PT must NOT include Variant, Use Cases, or Audience
2. **Hierarchy**: Most specific → Broader → Broadest (superset relationship)
3. **No Duplicates**: Synonyms/translations merged into single line (e.g., "TV / Television")
4. **Completeness**: All major PTs must be captured

---

## UI Structure

| Tab | Name | Content |
|-----|------|---------|
| **Tab #1** | Branding Scope & KW-Product Relationship | Prompt #1 output - KW classification |
| **Tab #2** | Listing Attributes Ranking | Prompt #2 output - PT, V, U, A rankings |
| **Tab #3** | KW Grouping & Ranking | Prompt #3 output - Grouped/ranked KWs |

---

## Trigger Scenarios

| Trigger | Description |
|---------|-------------|
| **Automatic** | KW fetching from JungleScout completed for ASIN |
| **Manual** | User clicks "Run KW Research" button on ASIN Config page |

---

# TYPE 1: VERIFICATION TESTS

## A. Trigger & Initiation (8 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| KW-V01 | Filter: ASIN with KW fetching just completed | Automated KW Research process starts | Auto-trigger works |
| KW-V02 | Filter: ASIN Config page → "Run KW Research" button | Process starts on click | Manual trigger works |
| KW-V03 | Filter: KW Research Status column on ASIN Config | Status updates (Pending → In Progress → Complete) | Status tracking |
| KW-V04 | Filter: ASIN with missing PDP content | Error displayed with guidance | Graceful error handling |
| KW-V05 | Filter: Re-run KW Research on existing ASIN | New results replace old (or version created) | Re-run handling |
| KW-V06 | Filter: Multiple ASINs triggered simultaneously | Each processes independently | Parallel processing |
| KW-V07 | Filter: "View KW Research" hyperlink | Routes to KW Research UI for that ASIN | Navigation works |
| KW-V08 | Filter: ASIN not in ASIN Config | Cannot trigger KW Research | Validation |

---

## B. PDP Content Fetching (8 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| KW-V09 | Filter: ASIN with complete PDP | Title, Bullets, Description, Attributes fetched | Full fetch |
| KW-V10 | Filter: ASIN with partial PDP (missing description) | Process handles gracefully | Partial data handling |
| KW-V11 | Filter: PDP content stored in backend | Data persists for ASIN | Storage works |
| KW-V12 | Filter: Keepa fallback when scrape fails | 3rd party source used | Fallback mechanism |
| KW-V13 | Filter: "Product Details (Optional)" field | User input captured and used | Optional field works |
| KW-V14 | Filter: PDP content with special characters | Properly escaped/handled | Character handling |
| KW-V15 | Filter: Large PDP content (long description) | Truncated appropriately for API | Size limits |
| KW-V16 | Filter: PDP content refresh | Re-fetches latest content | Data freshness |

---

## C. OpenAI Integration (8 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| KW-V17 | Filter: API connection to OpenAI | Secure, authenticated connection | Connection established |
| KW-V18 | Filter: KW + ASIN content sent as input | Structured prompt inputs | Input formatting |
| KW-V19 | Filter: OpenAI response received | Valid JSON/structured output | Response parsing |
| KW-V20 | Filter: API timeout handling | Graceful timeout with retry | Timeout handling |
| KW-V21 | Filter: API rate limit hit | Queued and retried | Rate limiting |
| KW-V22 | Filter: OpenAI error response | Error logged and surfaced | Error handling |
| KW-V23 | Filter: Output stored in backend | Results persisted | Storage |
| KW-V24 | Filter: Cost tracking per ASIN | API usage logged | Cost monitoring |

---

## D. Prompt #1 - Branding Scope & Relationship (10 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| KW-V25 | Filter: KWs classified as NB (Non-Branded) | No brand names present | NB accuracy |
| KW-V26 | Filter: KWs classified as OB (Own-Branded) | Only own brand present | OB accuracy |
| KW-V27 | Filter: KWs classified as CB (Competitor-Branded) | Only competitor brand present | CB accuracy |
| KW-V28 | Filter: KWs classified as R (Relevant) | Directly relates to product | R accuracy |
| KW-V29 | Filter: KWs classified as S (Substitute) | True substitute for product/PT | S accuracy |
| KW-V30 | Filter: KWs classified as C (Complementary) | Used WITH product | C accuracy |
| KW-V31 | Filter: KWs classified as N (Negative) | Should be excluded | N accuracy |
| KW-V32 | Filter: Misspelled brand names | Correctly classified (OB/CB) | Misspelling handling |
| KW-V33 | Filter: KW with multiple brands | Flagged or handled correctly | Multi-brand edge case |
| KW-V34 | Filter: Output displayed on Tab #1 UI | All classifications visible | UI population |

---

## E. Prompt #2 - Listing Attributes Ranking (10 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| KW-V35 | Filter: Product Types (PT) extracted | Correct PTs identified | PT extraction |
| KW-V36 | Filter: PT purity check | No variants/use cases in PT | PT purity |
| KW-V37 | Filter: PT hierarchy ranking | Most specific → Broadest | PT ranking |
| KW-V38 | Filter: PT synonyms merged | Single line with "/" separator | PT deduplication |
| KW-V39 | Filter: Variants (V) extracted | Correct variants identified | V extraction |
| KW-V40 | Filter: Use Cases (U) extracted | Correct use cases identified | U extraction |
| KW-V41 | Filter: Audiences (A) extracted | Correct audiences identified | A extraction |
| KW-V42 | Filter: V/U/A ranking | Highest relevance first | V/U/A ranking |
| KW-V43 | Filter: V/U/A without duplicates | Synonyms merged | V/U/A deduplication |
| KW-V44 | Filter: Output displayed on Tab #2 UI | All attributes visible | UI population |

---

## F. User Review & Edit (Tab #1 & #2) (8 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| KW-V45 | Filter: Edit button on row | Row becomes editable | Edit mode |
| KW-V46 | Filter: Change classification (NB→OB) | Change saved | Edit save |
| KW-V47 | Filter: Delete row | Row removed | Delete works |
| KW-V48 | Filter: Add row | New row inserted | Add works |
| KW-V49 | Filter: Drag & drop reorder | Row position changed | Reorder works |
| KW-V50 | Filter: Save/Cancel buttons | Changes persisted or discarded | Save/Cancel |
| KW-V51 | Filter: Submit to proceed to Prompt #3 | Triggers next step | Workflow progression |
| KW-V52 | Filter: Validation on submit | Invalid data flagged | Submit validation |

---

## G. Prompt #3 - KW Grouping & Ranking (10 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| KW-V53 | Filter: Non-Branded table generated | All NB KWs grouped | NB table |
| KW-V54 | Filter: Own-Branded table generated | All OB KWs grouped | OB table |
| KW-V55 | Filter: Competitor-Branded table generated | All CB KWs grouped | CB table |
| KW-V56 | Filter: Summary table (counts) | Branding × Group counts | Summary accurate |
| KW-V57 | Filter: KW assigned to correct Group # | Based on attribute match | Grouping logic |
| KW-V58 | Filter: KW assigned Rank # | Ranking within group | Ranking logic |
| KW-V59 | Filter: KW with multi-attributes | Placed in most specific group | Multi-attribute handling |
| KW-V60 | Filter: "No-Mapping" group | KWs without group assignment | Unmatched KWs |
| KW-V61 | Filter: 4th table (Branding & Relationship) | Complete KW summary | Summary table |
| KW-V62 | Filter: Output displayed on Tab #3 UI | All tables visible | UI population |

---

## H. User Review & Edit (Tab #3) (8 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| KW-V63 | Filter: Edit Group #/Rank # | Number field editable | Edit mode |
| KW-V64 | Filter: Change Group # | KW moves to new group | Group change |
| KW-V65 | Filter: Change Rank # | KW reordered within group | Rank change |
| KW-V66 | Filter: Delete row from table 1-3 | Row removed | Delete works |
| KW-V67 | Filter: Add row to table 1-3 | New row inserted | Add works |
| KW-V68 | Filter: Drag & drop (edit mode only) | Row repositioned | Reorder works |
| KW-V69 | Filter: Final submit | Workflow completes | Final submit |
| KW-V70 | Filter: Validation on final submit | Invalid data flagged | Submit validation |

---

## I. Relevance Tag Update (8 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| KW-V71 | Filter: Main KW Research UI | Relevancy Tag column updated | Tag population |
| KW-V72 | Filter: Tag format (e.g., NBR1) | Correct format applied | Tag format |
| KW-V73 | Filter: New tag creation | System creates if not exists | New tag handling |
| KW-V74 | Filter: Existing tag reuse | System reuses existing tag | Tag reuse |
| KW-V75 | Filter: Tags with "R" as 3rd digit | PT + V/U/A displayed | R-tag display |
| KW-V76 | Filter: Multiple KWs same tag | All receive same tag | Tag consistency |
| KW-V77 | Filter: Tag update on re-run | Old tags replaced | Tag refresh |
| KW-V78 | Filter: Bulk Import with new tags | New tags accepted | Import handling |

---

## J. UI Navigation & Display (8 tests)

| ID | How to Find Test Case | What to Observe | Pass Criteria |
|----|----------------------|-----------------|---------------|
| KW-V79 | Filter: ASIN dropdown | Only ASINs with completed prompts | Dropdown filtering |
| KW-V80 | Filter: Tab switching | Correct content loads | Tab navigation |
| KW-V81 | Filter: Large KW list | Pagination/scrolling works | Performance |
| KW-V82 | Filter: Search/filter on tables | Finds matching KWs | Search functionality |
| KW-V83 | Filter: Export functionality | Data exports correctly | Export |
| KW-V84 | Filter: Bulk edit | Multiple rows edited | Bulk operations |
| KW-V85 | Filter: Responsive display | Works on different screens | Responsiveness |
| KW-V86 | Filter: Loading states | Spinners shown during processing | UX feedback |

---

# TYPE 2: VALIDATION TESTS

## A. Branding Scope Accuracy (8 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| KW-VAL01 | Filter: KWs in NB bucket | No brand names (own or competitor) present | NB contamination |
| KW-VAL02 | Filter: KWs in OB bucket | Only own brand present | OB contamination |
| KW-VAL03 | Filter: KWs in CB bucket | Only competitor brand present | CB contamination |
| KW-VAL04 | Filter: Misspelled brands in NB | Should be in OB/CB | Misspelling missed |
| KW-VAL05 | Filter: Brand variations (abbrev, nicknames) | Correctly classified | Brand variation handling |
| KW-VAL06 | Filter: Generic brand-like words | Not misclassified as branded | False positive |
| KW-VAL07 | Filter: New competitor brands | Detected and classified | Brand detection |
| KW-VAL08 | Filter: Cross-check with known brand list | Matches expectations | Classification accuracy |

---

## B. KW-Product Relationship Accuracy (8 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| KW-VAL09 | Filter: KWs marked as Relevant (R) | Directly relates to product | R misclassification |
| KW-VAL10 | Filter: KWs marked as Substitute (S) | True substitutes only | S misclassification |
| KW-VAL11 | Filter: KWs marked as Complementary (C) | Used WITH product | C misclassification |
| KW-VAL12 | Filter: KWs marked as Negative (N) | Should be excluded | N misclassification |
| KW-VAL13 | Filter: Substitutes in R bucket | Should be S not R | S/R confusion |
| KW-VAL14 | Filter: Complementary in S bucket | Should be C not S | C/S confusion |
| KW-VAL15 | Filter: Relevant in N bucket | Should be R not N | R/N confusion |
| KW-VAL16 | Filter: Edge cases (product variants) | Correctly classified | Variant handling |

---

## C. Product Type Quality (6 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| KW-VAL17 | Filter: PTs with variants/use cases | Should not include V/U/A | PT impurity |
| KW-VAL18 | Filter: PT hierarchy ranking | Superset relationship maintained | Ranking error |
| KW-VAL19 | Filter: Duplicate PT lines | Synonyms should be merged | Duplication |
| KW-VAL20 | Filter: Missing major PTs | All relevant PTs captured | Incomplete coverage |
| KW-VAL21 | Filter: PTs matching listing content | Reflects product identity | PT accuracy |
| KW-VAL22 | Filter: PT translations | Merged with base PT | Translation handling |

---

## D. V/U/A Quality (6 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| KW-VAL23 | Filter: Invalid V/U/A additions | Nothing contradicts listing | Invalid additions |
| KW-VAL24 | Filter: Missing V/U/A from listing | Core attributes captured | Missing attributes |
| KW-VAL25 | Filter: Duplicate V/U/A lines | Synonyms merged | Duplication |
| KW-VAL26 | Filter: V/U/A ranking order | Highest relevance first | Ranking accuracy |
| KW-VAL27 | Filter: V/U/A cross-contamination | Each in correct category | Category mixing |
| KW-VAL28 | Filter: V/U/A relevance to product | All make sense for product | Relevance check |

---

## E. Grouping Quality (8 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| KW-VAL29 | Filter: KWs in Group N | Contains all required attributes | Missing attribute |
| KW-VAL30 | Filter: KWs in Group N | No extra attributes | Extra attribute |
| KW-VAL31 | Filter: "No-Mapping" group KWs | Should not fit other groups | Missed mapping |
| KW-VAL32 | Filter: Multi-attribute KWs | In most specific group | Wrong group |
| KW-VAL33 | Filter: Synonym-based grouping | Synonyms recognized | Synonym gaps |
| KW-VAL34 | Filter: Group count distribution | Reasonable spread | Imbalanced groups |
| KW-VAL35 | Filter: Empty groups | Should not exist if KWs qualify | Empty group |
| KW-VAL36 | Filter: Group definitions | Match documented rules | Definition mismatch |

---

## F. Ranking Quality (5 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| KW-VAL37 | Filter: Rank 1 KWs per group | Most important/relevant | Wrong rank 1 |
| KW-VAL38 | Filter: Rank progression | Logical ordering | Ranking inconsistency |
| KW-VAL39 | Filter: Same-rank KWs | Tied appropriately | Tie handling |
| KW-VAL40 | Filter: Rank stability | Consistent across re-runs | Rank volatility |
| KW-VAL41 | Filter: Manual rank changes | Preserved after updates | Rank persistence |

---

## G. Business Impact (8 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| KW-VAL42 | Filter: Campaigns using auto-classified KWs | ACOS improvement | No ACOS benefit |
| KW-VAL43 | Filter: Negative KWs added to campaigns | Reduced wasted spend | N not applied |
| KW-VAL44 | Filter: Relevant KWs prioritized | Higher impressions | R not prioritized |
| KW-VAL45 | Filter: Substitute KWs in separate campaigns | Proper segmentation | S not segmented |
| KW-VAL46 | Filter: Complementary KWs strategy | Cross-sell opportunities | C not utilized |
| KW-VAL47 | Filter: Time saved vs manual research | Automation ROI | Low time savings |
| KW-VAL48 | Filter: Classification accuracy over time | Improving or stable | Degradation |
| KW-VAL49 | Filter: User edit frequency | Low = good AI quality | High edit rate |

---

## H. Error Handling & Edge Cases (6 tests)

| ID | How to Find Cases | What to Check | Issue if Found |
|----|-------------------|---------------|----------------|
| KW-VAL50 | Filter: ASINs with very few KWs | Process completes | Small data failure |
| KW-VAL51 | Filter: ASINs with 1000+ KWs | Process completes | Large data failure |
| KW-VAL52 | Filter: Non-English ASINs | Handles non-English | Language issues |
| KW-VAL53 | Filter: Special character KWs | Properly processed | Character encoding |
| KW-VAL54 | Filter: API failures during process | Graceful recovery | Error recovery |
| KW-VAL55 | Filter: Partial process completion | Can resume/retry | Partial failure |

---

# SUMMARY

| Test Type | Count | Focus Area |
|-----------|-------|------------|
| **Type 1: Verification** | 86 | Triggers, API, Prompts, UI, Tags |
| **Type 2: Validation** | 55 | Classification Accuracy, Quality, Business Impact |
| **TOTAL** | 141 | |

---

# Key Thresholds to Monitor

| Threshold | Value | Risk |
|-----------|-------|------|
| API Cost per ASIN | $1-2 | Monitor for cost explosion |
| Classification Accuracy | > 90% | Manual edits needed if low |
| Processing Time | < 5 minutes | UX degradation if slow |
| User Edit Rate | < 20% | AI quality issue if high |

---

# Key Components Overview

| Component | Function | Key Metric |
|-----------|----------|------------|
| **Trigger System** | Initiate KW Research | Trigger reliability |
| **PDP Fetcher** | Get ASIN content | Data completeness |
| **OpenAI Integration** | Run AI prompts | API reliability |
| **Prompt #1** | Branding + Relationship | Classification accuracy |
| **Prompt #2** | PT/V/U/A extraction | Attribute quality |
| **Prompt #3** | Grouping + Ranking | Group accuracy |
| **Relevance Tags** | Final tag assignment | Tag correctness |
| **UI Tabs** | User review/edit | Usability |

---

# Reference Documents

| Source | Description |
|--------|-------------|
| PROD-1099 | Epic: ADS: Automated KW Research |
| PROD-116 | Deploy Triggers for KW Research |
| PROD-117 | Set Up Portal ↔ OpenAI Connection |
| PROD-118 | Fetch & Store ASIN Content from PDP |
| PROD-130 | Prompt #3 Output UI |
| PROD-131 | Assemble Full KW Research Workflow |
| PROD-132 | Implement KW Research UI modifications |
| PROD-1102 | Relevance Tagging Framework |
| PROD-1264 | KW Research Manual Trigger & Status |
| [Miro Schema](https://miro.com/app/board/uXjVJNp9oB8=/) | Workflow diagram |

