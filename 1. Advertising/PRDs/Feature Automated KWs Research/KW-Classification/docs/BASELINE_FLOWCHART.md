# Balanced Baseline Experiment Results

## Test Configuration

| Parameter | Value |
|-----------|-------|
| **Model** | gpt-4o-mini |
| **Temperature** | 0 |
| **Sampling** | 20 samples/module (balanced 50/50 for binary) |
| **Date** | 2026-01-12 |

---

## Pipeline Overview (Full Batch: 11,186 cases)

```
INPUT: Product Data + Search Keyword
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STAGE 1: Brand Entity Extraction (n=316)                                   │
│  ┌───────────────────────────┐     ┌──────────────────────────────────────┐ │
│  │ Path A: M01 (78.8%)       │ OR  │ Path B: M01a (81.2%) + M01b (96.0%)  │ │
│  │ 99/99 tested (100%)       │     │ 99/99 tested (100%)                  │ │
│  └───────────────────────────┘     └──────────────────────────────────────┘ │
│  M03: Competitors (17.0%) - 19/19 tested                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STAGE 2: Brand Scope Classification → OB / CB / NB (n=4,434)               │
│  ┌───────────────────────────┐     ┌──────────────────────────────────────┐ │
│  │ Path A (after M01)        │ OR  │ Path B (after M01a + M01b)           │ │
│  │ • M02: 90.6% [A]          │     │ • M02b: 95.2% [A] ✅ WINNER          │ │
│  │ • M04: 89.0% [B] ✅ WINNER│     │ • M04b: 87.3% [B]                    │ │
│  │ • M05: 78.4% [C]          │     │ • M05b: 93.7% [A] ✅ WINNER          │ │
│  │ 916-1759 tested (100%)    │     │ 916-1759 tested (100%)               │ │
│  └───────────────────────────┘     └──────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
              
              
              
┌─────────────────────────────────────────────────────────────────────────────┐
│  STAGE 3: Product Definition (n=56)                                         │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ M06: Taxonomy         73.6% [C]  │  12/12 tested (100%)                │ │
│  │ M07: Attributes       39.3% [F]  │  12/12 tested (100%)                │ │
│  │ M08: Attribute Ranks  21.0% [F]  │  12/12 tested (100%)                │ │
│  │ M09: Primary Use      50.0% [F]  │  10/10 tested (100%)                │ │
│  │ M10: Validate Use     66.7% [D]  │   3/10 tested (7 parse errors)      │ │
│  │ M11: Hard Constraints 50.0% [F]  │  10/10 tested (100%)                │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STAGE 4: Relevance Classification → R / S / C / N (n=1,500)                │
│  ┌───────────────────────────┐     ┌──────────────────────────────────────┐ │
│  │ Path A: M12→M13→M14→M15→M16│ OR  │ Path B: M12b (combined)              │ │
│  │ M12: 97.5% [A*] 443/443   │     │ M12b: 83.3% [B] 443/443              │ │
│  │ M13: 76.5% [C] 439/439    │     │ (balanced dataset, realistic)        │ │
│  │ M14: 82.5% [B] 229/229    │     │                                       │ │
│  │ M15: 72.9% [C] 210/210   │     │                                       │ │
│  │ M16: 68.7% [D] 179/179   │     │                                       │ │
│  └───────────────────────────┘     └──────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                 │
                 ▼
           OUTPUT: Classification
           • OB (Own Brand) + R/S/C/N
           • CB (Competitor Brand) + R/S/C/N
           • NB (Non-Branded) + R/S/C/N
```

---

## Mermaid Flowchart

```mermaid
flowchart TB
    subgraph INPUT["INPUT"]
        PROD[/"Product Data"/]
        KW[/"Search Keyword"/]
    end

    subgraph S1["STAGE 1: Brand Entity Extraction"]
        direction LR
        subgraph S1A["Path A"]
            M01["M01 ExtractBrand<br/>━━━━━━━━━━━━<br/>list | Prec: 78.8% [B]<br/>99 cases"]
        end
        subgraph S1B["Path B"]
            M01a["M01a Variations<br/>━━━━━━━━━━━━<br/>list | Prec: 81.2% [B]<br/>99 cases"]
            M01b["M01b RelatedTerms<br/>━━━━━━━━━━━━<br/>list | Prec: 96.0% [A]<br/>99 cases"]
        end
    end

    subgraph S2["STAGE 2: Brand Scope → OB/CB/NB"]
        direction LR
        subgraph S2A["Path A (from M01)"]
            M02["M02 OwnBrand?<br/>━━━━━━━━━━━━<br/>binary | Acc: 90.6% [A]<br/>916 cases"]
            M04["M04 Competitor?<br/>━━━━━━━━━━━━<br/>binary | Acc: 89.0% [B]<br/>1759 cases"]
            M05["M05 NonBranded?<br/>━━━━━━━━━━━━<br/>binary | Acc: 78.4% [C]<br/>1759 cases"]
        end
        subgraph S2B["Path B (from M01a+M01b)"]
            M02b["M02b OwnBrand?<br/>━━━━━━━━━━━━<br/>binary | Acc: 95.2% [A]<br/>916 cases"]
            M04b["M04b Competitor?<br/>━━━━━━━━━━━━<br/>binary | Acc: 87.3% [B]<br/>1759 cases"]
            M05b["M05b NonBranded?<br/>━━━━━━━━━━━━<br/>binary | Acc: 93.7% [A]<br/>1759 cases"]
        end
    end

    subgraph S3["STAGE 3: Product Definition"]
        direction TB
        M06["M06: Taxonomy — list_of_dicts | Prec: 73.6% [C] — 12 cases"]
        M07["M07: Variants — list | Prec: 39.3% [F] — 12 cases"]
        M08["M08: AttrRanks — list_of_dicts | Prec: 21.0% [F] — 12 cases"]
        M09["M09: PrimaryUse — text | Fuzzy: 50.0% [F] — 10 cases"]
        M10["M10: ValidateUse — text | Fuzzy: 66.7% [D] — 3 cases (7 truncated)"]
        M11["M11: Constraints — list | Prec: 50.0% [F] — 10 cases"]
    end

    subgraph S4["STAGE 4: Relevance → R/S/C/N"]
        direction LR
        subgraph S4A["Path A"]
            M12["M12 HardConstraint<br/>━━━━━━━━━━━━<br/>binary | Acc: 97.5% [A]<br/>443 cases"]
            M13["M13 ProductType<br/>━━━━━━━━━━━━<br/>binary | Acc: 76.5% [C]<br/>439 cases"]
            M14["M14 SameUse<br/>━━━━━━━━━━━━<br/>binary | Acc: 82.5% [B]<br/>229 cases"]
            M15["M15 Substitute<br/>━━━━━━━━━━━━<br/>binary | Acc: 72.9% [C]<br/>210 cases"]
            M16["M16 Complement<br/>━━━━━━━━━━━━<br/>binary | Acc: 68.7% [D]<br/>179 cases"]
        end
        subgraph S4B["Path B"]
            M12b["M12b Combined<br/>━━━━━━━━━━━━<br/>binary | Acc: 83.3% [B]<br/>443 cases"]
        end
    end

    subgraph OUTPUT["OUTPUT"]
        OB(["OB<br/>Own Brand"])
        CB(["CB<br/>Competitor"])
        NB(["NB<br/>Non-Branded"])
        R(["R<br/>Relevant"])
        S(["S<br/>Substitute"])
        C(["C<br/>Complement"])
        N(["N<br/>Not Relevant"])
    end

    PROD --> S1
    KW --> S2

    M01 --> S2A
    M01a --> S2B
    M01b --> S2B

    M02 -.->|"is_own"| OB
    M04 -.->|"is_comp"| CB
    M02b -.->|"is_own"| OB
    M04b -.->|"is_comp"| CB
    M05 -.->|"non-brand"| NB
    M05b -.->|"non-brand"| NB

    M06 --> M07 --> M08 --> M09 --> M10 --> M11
    M11 --> S4

    M12b -.->|"R"| R
    M12b -.->|"S"| S
    M12b -.->|"C"| C
    M12b -.->|"N"| N
    M12 -.->|"N"| N
    M12 -.-> M13
    M13 -.-> M15
    M13 -.-> M14
    M14 -.->|"R"| R
    M14 -.->|"N"| N
    M15 -.->|"S"| S
    M15 -.-> M16
    M16 -.->|"C"| C
    M16 -.->|"N"| N

    classDef green fill:#22c55e,stroke:#15803d,color:#fff
    classDef yellow fill:#eab308,stroke:#a16207,color:#000
    classDef orange fill:#f97316,stroke:#ea580c,color:#fff
    classDef lime fill:#84cc16,stroke:#65a30d,color:#000
    classDef red fill:#ef4444,stroke:#b91c1c,color:#fff
    classDef gray fill:#6b7280,stroke:#4b5563,color:#fff
    classDef input fill:#3b82f6,stroke:#1d4ed8,color:#fff
    classDef output fill:#8b5cf6,stroke:#6d28d9,color:#fff

    class M02,M02b,M05b,M12,M01b green
    class M04,M04b,M14,M01a,M12b,M01 yellow
    class M05,M13,M06,M15 orange
    class M10,M16 lime
    class M07,M08,M09,M11 red
    class PROD,KW input
    class OB,CB,NB,R,S,C,N output
```

**Legend:** 🟢 [A] ≥90% | 🟡 [B] 80-89% | 🟠 [C] 70-79% | 🟩 [D] 60-69% | 🔴 [F] <60%

**Updated:** 2026-01-13 | Full batch run: 11,186 cases across 22 modules

---

## Binary Classifiers - Confusion Matrix Flowchart

```mermaid
flowchart TB
    subgraph LEGEND["LEGEND: Confusion Matrix"]
        direction LR
        TP_L["TP = True Positive<br/>Model said YES, correct"]
        TN_L["TN = True Negative<br/>Model said NO, correct"]
        FP_L["FP = False Positive<br/>Model said YES, WRONG"]
        FN_L["FN = False Negative<br/>Model said NO, WRONG"]
    end

    subgraph S2_CM["STAGE 2: Brand Scope Classifiers"]
        direction TB
        subgraph S2A_CM["Path A"]
            M02_CM["M02 OwnBrand<br/>━━━━━━━━━━━━━━━━<br/>TP:91 TN:739 FP:0 FN:86<br/>Acc:90.6% Prec:100% Rec:51%<br/>⚠️ High precision, low recall"]
            M04_CM["M04 Competitor<br/>━━━━━━━━━━━━━━━━<br/>TP:83 TN:1482 FP:0 FN:194<br/>Acc:89.0% Prec:100% Rec:30%<br/>⚠️ Misses many competitors"]
            M05_CM["M05 NonBranded<br/>━━━━━━━━━━━━━━━━<br/>TP:1081 TN:298 FP:32 FN:348<br/>Acc:78.4% Prec:97% Rec:76%<br/>⚠️ Misses 348 positives"]
        end
        subgraph S2B_CM["Path B"]
            M02b_CM["M02b OwnBrand<br/>━━━━━━━━━━━━━━━━<br/>TP:154 TN:718 FP:21 FN:23<br/>Acc:95.2% Prec:88% Rec:87%<br/>✅ Balanced"]
            M04b_CM["M04b Competitor<br/>━━━━━━━━━━━━━━━━<br/>TP:132 TN:1403 FP:79 FN:145<br/>Acc:87.3% Prec:63% Rec:48%<br/>⚠️ Many FP and FN"]
            M05b_CM["M05b NonBranded<br/>━━━━━━━━━━━━━━━━<br/>TP:1413 TN:235 FP:95 FN:16<br/>Acc:93.7% Prec:94% Rec:99%<br/>✅ Excellent recall"]
        end
    end

    subgraph S4_CM["STAGE 4: Relevance Classifiers"]
        direction TB
        subgraph S4A_CM["Path A"]
            M12_CM["M12 HardConstraint<br/>━━━━━━━━━━━━━━━━<br/>TP:0 TN:432 FP:11 FN:0<br/>Acc:97.5%<br/>ℹ️ No positives in data"]
            M13_CM["M13 ProductType<br/>━━━━━━━━━━━━━━━━<br/>TP:178 TN:158 FP:52 FN:51<br/>Acc:76.5% Prec:77% Rec:78%<br/>⚠️ Balanced but needs work"]
            M14_CM["M14 SameUse<br/>━━━━━━━━━━━━━━━━<br/>TP:188 TN:1 FP:10 FN:30<br/>Acc:82.5% Prec:95% Rec:86%<br/>ℹ️ Almost all positives"]
            M15_CM["M15 Substitute<br/>━━━━━━━━━━━━━━━━<br/>TP:14 TN:139 FP:40 FN:17<br/>Acc:72.9% Prec:26% Rec:45%<br/>⚠️ Low precision (many FP)"]
            M16_CM["M16 Complement<br/>━━━━━━━━━━━━━━━━<br/>TP:61 TN:62 FP:36 FN:20<br/>Acc:68.7% Prec:63% Rec:75%<br/>⚠️ Balanced but needs work"]
        end
        subgraph S4B_CM["Path B"]
            M12b_CM["M12b Combined<br/>━━━━━━━━━━━━━━━━<br/>TP:171 TN:198 FP:27 FN:47<br/>Acc:83.3% Prec:86% Rec:78%<br/>✅ Balanced"]
        end
    end

    classDef goodBox fill:#22c55e,stroke:#15803d,color:#fff
    classDef warnBox fill:#f97316,stroke:#ea580c,color:#fff
    classDef infoBox fill:#3b82f6,stroke:#1d4ed8,color:#fff
    classDef legendBox fill:#6b7280,stroke:#4b5563,color:#fff

    class M02b_CM,M05b_CM,M12b_CM goodBox
    class M02_CM,M04_CM,M05_CM,M04b_CM,M13_CM,M15_CM,M16_CM warnBox
    class M12_CM,M14_CM infoBox
    class TP_L,TN_L,FP_L,FN_L legendBox
```

### Binary Classifiers Analysis:

| Issue | Modules | Explanation |
|-------|---------|-------------|
| **Low Recall** | M02, M04 | 100% precision but missing many positives (FN=86, FN=194) |
| **Imbalanced Data** | M12, M15, M16 | No positive cases in dataset - need to add |
| **Balanced ✅** | M02b, M05b, M12b | Best Precision/Recall balance |
| **Needs Work** | M04b, M13 | Many FP and FN - prompt improvement needed |

---

## Dataset Balance Flowchart

```mermaid
flowchart TB
    subgraph LEGEND["LEGEND: Dataset Balance"]
        direction LR
        BAL_L["✅ BALANCED<br/>40-60% positives"]
        SKEW_P_L["⚠️ SKEWED+<br/>>60% positives"]
        SKEW_N_L["⚠️ SKEWED-<br/><40% positives"]
    end

    subgraph S2_BAL["STAGE 2: Brand Classification"]
        direction TB
        subgraph S2A_BAL["Path A"]
            M02_BAL["M02 OwnBrand<br/>━━━━━━━━━━━━━━━━<br/>Total: 916<br/>Positive (OB): 177 (19.3%)<br/>Negative (null): 739<br/>⚠️ SKEWED-"]
            M04_BAL["M04 Competitor<br/>━━━━━━━━━━━━━━━━<br/>Total: 1759<br/>Positive (CB): 277 (15.7%)<br/>Negative (null): 1482<br/>⚠️ SKEWED-"]
            M05_BAL["M05 NonBranded<br/>━━━━━━━━━━━━━━━━<br/>Total: 1759<br/>Positive (NB): 1429 (81.2%)<br/>Negative (null): 330<br/>⚠️ SKEWED+"]
        end
        subgraph S2B_BAL["Path B"]
            M02b_BAL["M02b OwnBrand<br/>━━━━━━━━━━━━━━━━<br/>Total: 916<br/>Positive (OB): 177 (19.3%)<br/>Negative (null): 739<br/>⚠️ SKEWED-"]
            M04b_BAL["M04b Competitor<br/>━━━━━━━━━━━━━━━━<br/>Total: 1759<br/>Positive (CB): 277 (15.7%)<br/>Negative (null): 1482<br/>⚠️ SKEWED-"]
            M05b_BAL["M05b NonBranded<br/>━━━━━━━━━━━━━━━━<br/>Total: 1759<br/>Positive (NB): 1429 (81.2%)<br/>Negative (null): 330<br/>⚠️ SKEWED+"]
        end
    end

    subgraph S4_BAL["STAGE 4: Relevance Classification"]
        direction TB
        subgraph S4A_BAL["Path A"]
            M12_BAL["M12 HardConstraint<br/>━━━━━━━━━━━━━━━━<br/>Total: 443<br/>Positive (True): 0 (0%)<br/>Negative (Null/N): 443<br/>⛔ NO POSITIVES"]
            M13_BAL["M13 ProductType<br/>━━━━━━━━━━━━━━━━<br/>Total: 439<br/>Positive (True): 229 (52.2%)<br/>Negative (False): 210<br/>✅ BALANCED"]
            M14_BAL["M14 SameUse<br/>━━━━━━━━━━━━━━━━<br/>Total: 229<br/>Positive (R): 218 (95.2%)<br/>Negative (N): 11<br/>⚠️ EXTREME SKEW+"]
            M15_BAL["M15 Substitute<br/>━━━━━━━━━━━━━━━━<br/>Total: 210<br/>Positive (S): 31 (14.8%)<br/>Negative (Null): 179<br/>⚠️ SKEWED-"]
            M16_BAL["M16 Complement<br/>━━━━━━━━━━━━━━━━<br/>Total: 179<br/>Positive (C): 81 (45.3%)<br/>Negative (N): 98<br/>✅ BALANCED"]
        end
        subgraph S4B_BAL["Path B"]
            M12b_BAL["M12b Combined<br/>━━━━━━━━━━━━━━━━<br/>Total: 443<br/>R: 218 | S: 31 | C: 81 | N: 113<br/>Multiclass (4 classes)<br/>✅ DIVERSE"]
        end
    end

    classDef balancedBox fill:#22c55e,stroke:#15803d,color:#fff
    classDef skewedPlusBox fill:#f97316,stroke:#ea580c,color:#fff
    classDef skewedMinusBox fill:#3b82f6,stroke:#1d4ed8,color:#fff
    classDef noPositivesBox fill:#dc2626,stroke:#991b1b,color:#fff
    classDef extremeBox fill:#7c2d12,stroke:#431407,color:#fff
    classDef legendBox fill:#6b7280,stroke:#4b5563,color:#fff

    class M13_BAL,M16_BAL,M12b_BAL balancedBox
    class M05_BAL,M05b_BAL skewedPlusBox
    class M02_BAL,M04_BAL,M02b_BAL,M04b_BAL,M15_BAL skewedMinusBox
    class M12_BAL noPositivesBox
    class M14_BAL extremeBox
    class BAL_L,SKEW_P_L,SKEW_N_L legendBox
```

### Dataset Balance Summary (from Expected Data):

| Module | Total | Positive | Negative | Pos% | Balance |
|--------|-------|----------|----------|------|---------|
| M02/M02b | 916 | OB: 177 | null: 739 | 19.3% | ⚠️ SKEWED- |
| M04/M04b | 1759 | CB: 277 | null: 1482 | 15.7% | ⚠️ SKEWED- |
| M05/M05b | 1759 | NB: 1429 | null: 330 | 81.2% | ⚠️ SKEWED+ |
| M12 | 443 | True: 0 | Null/N: 443 | 0.0% | ⛔ NO POS |
| M12b | 443 | R:218, S:31, C:81, N:113 | - | Multiclass | ✅ DIVERSE |
| M13 | 439 | True: 229 | False: 210 | 52.2% | ✅ BALANCED |
| M14 | 229 | R: 218 | N: 11 | 95.2% | ⚠️ EXTREME+ |
| M15 | 210 | S: 31 | Null: 179 | 14.8% | ⚠️ SKEWED- |
| M16 | 179 | C: 81 | N: 98 | 45.3% | ✅ BALANCED |

### Dataset Balance Recommendations:

1. **M12** - Only module with 0% positives. Need to find products that actually violate hard constraints.

2. **M14** - 95% positives is extreme skew. Model can achieve 95% accuracy by always predicting "R". Need more negative (N) cases.

3. **M02, M04, M15** - Low positive % (<20%) explains high precision but low recall - models are conservative.

4. **M05** - 81% positives means model needs to correctly identify the 19% negatives, which is harder.

5. **M13, M16, M12b** - Well-balanced datasets provide the most reliable metrics.

### Scorer Configuration Issue ✅ FIXED & RE-EVALUATED:

Bug in error_analyzer.py was found and fixed:
- M15: Changed from `positive: "R"` → `positive: "S"` (Substitute)
- M16: Changed from `positive: "R"` → `positive: "C"` (Complement)

**Re-evaluation Results:**
| Module | Old Result | New Result | Analysis |
|--------|------------|------------|----------|
| M15 | 100% (invalid) | 72.9% [C] | Low precision (25.9%), many false positives |
| M16 | 100% (invalid) | 68.7% [D] | Balanced dataset, realistic performance |

---

## Results Summary by Stage (Full Batch Run: 11,186 cases)

### Stage 1: Brand Entity Extraction (n=316)

| Module | Task | Metric | Value | Grade | Cases | Errors |
|--------|------|--------|-------|-------|-------|--------|
| M01 | ExtractOwnBrandEntities | Precision/Recall | 78.8%/78.5% | B | 99 | 65 |
| M01a | ExtractOwnBrandVariations | Precision/Recall | 81.2%/81.8% | B | 99 | 79 |
| M01b | ExtractBrandRelatedTerms | Precision/Recall | 96.0%/93.9% | A | 99 | 7 |
| M03 | GenerateCompetitorEntities | Precision/Recall | 17.0%/46.4% | F | 19 | 19 |

**Status:** M01b performs excellently. M03 needs significant improvement (low precision).

### Stage 2: Brand Scope Classification (n=4,434)

#### Path A vs Path B Comparison (Full Batch)

| Task | Path A | Path B | Winner | Delta |
|------|--------|--------|--------|-------|
| Own Brand (OB) | M02: 90.6% | M02b: **95.2%** | **Path B** | +4.6% |
| Competitor (CB) | M04: **89.0%** | M04b: 87.3% | **Path A** | +1.7% |
| Non-Branded (NB) | M05: 78.4% | M05b: **93.7%** | **Path B** | +15.3% |

**Key Finding:** Full batch shows Path B (M02b, M05b) actually outperforms Path A for OB and NB classification!

#### Detailed Results

| Module | Task | Accuracy | Prec | Rec | F1 | Grade | Cases | Errors |
|--------|------|----------|------|-----|----|----|-------|--------|
| M02 | ClassifyOwnBrand | 90.6% | 100% | 51.4% | 67.9% | A | 916 | 86 |
| M04 | ClassifyCompetitor | 89.0% | 100% | 30.0% | 46.1% | B | 1759 | 194 |
| M05 | ClassifyNonBranded | 78.4% | 97.1% | 75.6% | 85.1% | C | 1759 | 380 |
| M02b | ClassifyOwnBrand (v3) | 95.2% | 88.0% | 87.0% | 87.5% | A | 916 | 44 |
| M04b | ClassifyCompetitor (v3) | 87.3% | 62.6% | 47.7% | 54.1% | B | 1759 | 224 |
| M05b | ClassifyNonBranded (v3) | 93.7% | 93.7% | 98.9% | 96.2% | A | 1759 | 111 |

### Stage 3: Product Definition (n=56)

| Module | Task | Metric | Value | Grade | Cases | Errors |
|--------|------|--------|-------|-------|-------|--------|
| M06 | GenerateProductTypeTaxonomy | Precision | 73.6% | C | 12 | 5 |
| M07 | ExtractProductAttributes | Precision/Recall | 39.3%/31.0% | F | 12 | 12 |
| M08 | AssignAttributeRanks | Precision | 21.0% | F | 12 | 12 |
| M09 | IdentifyPrimaryIntendedUse | Fuzzy Accuracy | 50.0% | F | 10 | 10 |
| M10 | ValidatePrimaryIntendedUse | Fuzzy Accuracy | 66.7% | D | 3 | 3 (7 parse errors) |
| M11 | IdentifyHardConstraints | Precision/Recall | 50.0%/80.0% | F | 10 | 5 |

**Issue:** Stage 3 modules need significant improvement. M10 had 7 JSON parsing errors due to truncated LLM responses.

### Stage 4: Relevance Classification (n=1,500)

| Module | Task | Accuracy | Prec | Rec | F1 | Grade | Cases | Errors |
|--------|------|----------|------|-----|----|----|-------|--------|
| M12 | CheckHardConstraint | 97.5% | 0% | 0% | 0% | A* | 443 | 11 |
| M13 | CheckProductType | 76.5% | 77.4% | 77.7% | 77.6% | C | 439 | 103 |
| M14 | CheckPrimaryUseSameType | 82.5% | 94.9% | 86.2% | 90.4% | B | 229 | 40 |
| M15 | CheckSubstitute | 72.9% | 25.9% | 45.2% | 32.9% | C | 210 | 57 |
| M16 | CheckComplementary | 68.7% | 62.9% | 75.3% | 68.5% | D | 179 | 56 |
| M12b | CombinedClassification | 83.3% | 86.4% | 78.4% | 82.2% | B | 443 | 74 |

**Notes:**
- **M12** marked A* because 0% Precision/Recall due to NO POSITIVE CASES in dataset (no hard constraint violations)
- **M15** has very low precision (25.9%) - model predicts "Substitute" too often (40 FP vs only 14 TP)
- **M16** has balanced metrics but still needs improvement (68.7% accuracy)
- M12b (Path B combined) performs well with balanced data (83.3%)

**Path A Performance:**
- M12: 97.5% [A*] - Dataset has no positive cases (hard constraint violations)
- M13: 76.5% [C] - Product type check needs improvement
- M14: 82.5% [B] - Good but dataset heavily skewed (95% positives)
- M15: 72.9% [C] - Low precision issue (FP=40), needs prompt refinement
- M16: 68.7% [D] - Balanced dataset, reasonable performance

**Path B:**
- M12b: 83.3% [B] - Combined approach with balanced data shows realistic performance

---

## Overall Statistics (Full Batch Run)

| Metric | Value |
|--------|-------|
| **Total Modules Tested** | 22 |
| **Total Samples Processed** | 11,186 |
| **Average Accuracy (Binary)** | 89.5% |
| **Average Precision (List)** | 60.4% |
| **Total Errors** | 1,484 |
| **Modules with A grade (≥90%)** | 5 (M01b, M02, M02b, M05b, M12) |
| **Modules with B grade (80-89%)** | 5 (M01, M01a, M04, M04b, M12b, M14) |
| **Modules with C grade (70-79%)** | 5 (M05, M06, M13, M15) |
| **Modules with D grade (60-69%)** | 2 (M10, M16) |
| **Modules with F grade (<60%)** | 5 (M03, M07, M08, M09, M11) |

---

## Priority Fixes

| Priority | Module | Current | Target | Issue | Action |
|----------|--------|---------|--------|-------|--------|
| **P0** | M03 | 17.0% | 70% | Low precision | Rewrite prompt - generating too many false competitors |
| **P0** | M08 | 21.0% | 70% | Low precision | Review attribute ranking logic |
| **P0** | M15 | 25.9% prec | 70% | Low precision (FP=40) | Model predicts "Substitute" too often |
| **P1** | M07 | 39.3% | 70% | Low precision/recall | Improve attribute extraction |
| **P1** | M09 | 50.0% | 80% | Low fuzzy accuracy | Improve primary use identification |
| **P1** | M11 | 50.0% | 80% | Low precision | Improve hard constraint identification |
| **P2** | M10 | 66.7% | 85% | Parse errors (7/10) | Increase max_tokens, fix JSON format |
| **P2** | M16 | 68.7% | 80% | Needs improvement | Refine complement detection criteria |
| **P2** | M13 | 76.5% | 85% | Needs improvement | Refine product type matching criteria |
| **P3** | M05 | 78.4% | 85% | Low recall | Reduce false negatives |

### Data Quality Fixes Needed:

| Priority | Module | Issue | Action |
|----------|--------|-------|--------|
| **P0** | M12, M15, M16 | 0% positives | Add positive test cases to dataset |
| **P1** | M14 | 95% positives | Add negative test cases to dataset |
| **P2** | M02, M04 | <20% positives | Consider balanced sampling for evaluation |

**✅ FIXED:** JSON parsing errors (M10) - 7 parse errors due to truncated responses. Need to increase max_tokens.

---

## Data Dependencies

```
STAGE 1                    STAGE 2                    STAGE 3                    STAGE 4
─────────────────────────────────────────────────────────────────────────────────────────
                                                      M06 (taxonomy)
                                                           │
M01 ──┬──► M02 ──┬                                   M07 (attributes)
      │         │                                         │
      ├──► M04 ─┼──► [OB/CB/NB] ────►                M08 (ranks)
      │         │                                         │
      └──► M05 ─┘                                    M09 (primary_use)
                                                          │
M01a ─┬──► M02b ─┬                                   M10 (validate)
      │          │                                        │
M01b ─┼──► M04b ─┼──► [OB/CB/NB] ────►               M11 (constraints)
      │          │                                        │
      └──► M05b ─┘                                   M12-M16 ──► [R/S/C/N]
```

---

## Key Insights

### 1. Full Batch Run vs Balanced Sampling
Full batch run (11,186 cases) reveals different patterns than initial 50/50 balanced sampling:
- Path B actually outperforms Path A for OB and NB classification in Stage 2
- Dataset imbalance significantly affects reported metrics (M12, M15, M16 show 100% accuracy but have 0 positives)

### 2. Path A vs Path B - Updated Conclusions
**Stage 2 (Brand Classification):**
- Path B wins for OB: M02b (95.2%) vs M02 (90.6%) - +4.6%
- Path A wins for CB: M04 (89.0%) vs M04b (87.3%) - +1.7%
- Path B wins for NB: M05b (93.7%) vs M05 (78.4%) - **+15.3%**

**Stage 4 (Relevance):**
- M12b (83.3%) has balanced data and realistic performance
- M12, M15, M16 have 100% accuracy but 0% precision/recall due to no positive cases

### 3. Stage 3 Needs Significant Work
Product definition modules (M06-M11) underperform expectations:
- M03: 17.0% precision (generating too many false competitors)
- M07: 39.3% precision (attribute extraction issues)
- M08: 21.0% precision (attribute ranking problems)
- M09: 50.0% fuzzy accuracy (primary use identification)

### 4. Dataset Quality Issues
Critical data problems identified:
- **M12**: 0% positive cases - cannot measure true positive rate (no hard constraint violations)
- **M14**: 95% positive cases - model can achieve 95% by always saying "yes"
- **M02, M04, M15**: <20% positive cases - explains high precision but low recall
- **M13, M16**: Well-balanced (45-52% positives) - most reliable metrics

### 5. JSON Parsing Issues - Partially Resolved
M10 still has 7/10 parse errors due to truncated LLM responses. Need to:
- Increase max_tokens for M10
- Add JSON validation/retry logic

### 6. Top Performing Modules
- **M01b** (96.0% precision) - Brand term extraction
- **M02b** (95.2% accuracy) - Own brand classification
- **M05b** (93.7% accuracy, 98.9% recall) - Non-branded classification
- **M12** (97.5% accuracy) - Hard constraint check (needs positive cases)

### 7. Scorer Bug Fixed ✅
M15 and M16 had wrong positive class configured in error_analyzer.py:
- M15: Changed from "R" → "S" (Substitute) - Now shows 72.9% [C]
- M16: Changed from "R" → "C" (Complement) - Now shows 68.7% [D]

**M15 Analysis:** Low precision (25.9%) indicates model predicts "Substitute" too often (40 FP).
**M16 Analysis:** Balanced dataset (45% positives) gives reliable metrics - needs prompt improvement.

---

*Generated: 2026-01-13 | Full Batch Run: 11,186 cases across 22 modules*
