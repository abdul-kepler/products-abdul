# Baseline Results - January 12, 2026

**Run Date:** 2026-01-12
**Model:** gpt-4o-mini
**Temperature:** 0
**Samples:** 20 per module (or max available)
**Total Modules:** 21 (M03 excluded)

## Summary Table

| Module | Description | Accuracy | Correct | Total | Grade |
|--------|-------------|----------|---------|-------|-------|
| M01 | Extract Brand Entities | **100%** | 20 | 20 | A |
| M01a | Brand Variations | **100%** | 20 | 20 | A |
| M01b | Related Terms | **100%** | 20 | 20 | A |
| M02 | Own Brand Classification | **100%** | 20 | 20 | A |
| M02b | Own Brand (v3 with context) | **95%** | 19 | 20 | A |
| M04 | Competitor Classification | **95%** | 19 | 20 | A |
| M04b | Competitor (v3 with context) | **90%** | 18 | 20 | A |
| M05 | Non-Branded Classification | **85%** | 17 | 20 | B |
| M05b | Non-Branded (v3 with context) | **85%** | 17 | 20 | B |
| M06 | Product Taxonomy | **67%** | 8 | 12 | D |
| M07 | Attribute Extraction | **100%** | 12 | 12 | A |
| M08 | Attribute Ranking | **67%** | 8 | 12 | D |
| M09 | Primary Use ID | **80%** | 8 | 10 | B |
| M10 | Validate Use | **80%** | 8 | 10 | B |
| M11 | Hard Constraints | **80%** | 8 | 10 | B |
| M12 | Constraint Check | **100%** | 20 | 20 | A |
| M12b | Combined R/S/C/N | **65%** | 13 | 20 | D |
| M13 | Product Type Check | **60%** | 12 | 20 | F |
| M14 | Same Type Use Check | **100%** | 20 | 20 | A |
| M15 | Substitute Check | **95%** | 19 | 20 | A |
| M16 | Complementary Check | **95%** | 19 | 20 | A |

## Grade Distribution

| Grade | Range | Count | Modules |
|-------|-------|-------|---------|
| **A** | ≥90% | 12 | M01, M01a, M01b, M02, M02b, M04, M04b, M07, M12, M14, M15, M16 |
| **B** | 80-89% | 5 | M05, M05b, M09, M10, M11 |
| **C** | 70-79% | 0 | - |
| **D** | 60-69% | 3 | M06, M08, M12b |
| **F** | <60% | 1 | M13 |

## Modules Needing Improvement

### Priority 1: Critical (F Grade)
- **M13 (60%)** - Product Type Check
  - Often fails to correctly identify product type matches
  - Needs better taxonomy alignment

### Priority 2: High (D Grade)
- **M12b (65%)** - Combined R/S/C/N Classification
  - Decision tree logic not followed correctly
  - Needs clearer step-by-step reasoning

- **M06 (67%)** - Product Type Taxonomy
  - Taxonomy structure inconsistent
  - Level assignments sometimes wrong

- **M08 (67%)** - Attribute Ranking
  - Ranking criteria unclear
  - Top attributes not correctly prioritized

## Braintrust Experiments

Project: `Keyword-Classification-Pipeline-V1.1`
Dashboard: https://www.braintrust.dev/app/KCC/p/Keyword-Classification-Pipeline-V1.1/experiments

| Module | Experiment URL |
|--------|----------------|
| M01 | [M01_baseline_20260112_1158](https://www.braintrust.dev/app/KCC/p/Keyword-Classification-Pipeline-V1.1/experiments/M01_baseline_20260112_1158) |
| M01a | [M01A_baseline_20260112_1159](https://www.braintrust.dev/app/KCC/p/Keyword-Classification-Pipeline-V1.1/experiments/M01A_baseline_20260112_1159) |
| M01b | [M01B_baseline_20260112_1200](https://www.braintrust.dev/app/KCC/p/Keyword-Classification-Pipeline-V1.1/experiments/M01B_baseline_20260112_1200) |
| M02 | [M02_baseline_20260112_1200](https://www.braintrust.dev/app/KCC/p/Keyword-Classification-Pipeline-V1.1/experiments/M02_baseline_20260112_1200) |
| M02b | [M02B_baseline_20260112_1310](https://www.braintrust.dev/app/KCC/p/Keyword-Classification-Pipeline-V1.1/experiments/M02B_baseline_20260112_1310) |
| M04 | [M04_baseline_20260112_1201](https://www.braintrust.dev/app/KCC/p/Keyword-Classification-Pipeline-V1.1/experiments/M04_baseline_20260112_1201) |
| M04b | [M04B_baseline_20260112_1313](https://www.braintrust.dev/app/KCC/p/Keyword-Classification-Pipeline-V1.1/experiments/M04B_baseline_20260112_1313) |
| M05 | [M05_baseline_20260112_1202](https://www.braintrust.dev/app/KCC/p/Keyword-Classification-Pipeline-V1.1/experiments/M05_baseline_20260112_1202) |
| M05b | [M05B_baseline_20260112_1316](https://www.braintrust.dev/app/KCC/p/Keyword-Classification-Pipeline-V1.1/experiments/M05B_baseline_20260112_1316) |
| M06 | [M06_baseline_20260112_1202](https://www.braintrust.dev/app/KCC/p/Keyword-Classification-Pipeline-V1.1/experiments/M06_baseline_20260112_1202) |
| M07 | [M07_baseline_20260112_1203](https://www.braintrust.dev/app/KCC/p/Keyword-Classification-Pipeline-V1.1/experiments/M07_baseline_20260112_1203) |
| M08 | [M08_baseline_20260112_1204](https://www.braintrust.dev/app/KCC/p/Keyword-Classification-Pipeline-V1.1/experiments/M08_baseline_20260112_1204) |
| M09 | [M09_baseline_20260112_1206](https://www.braintrust.dev/app/KCC/p/Keyword-Classification-Pipeline-V1.1/experiments/M09_baseline_20260112_1206) |
| M10 | [M10_baseline_20260112_1206](https://www.braintrust.dev/app/KCC/p/Keyword-Classification-Pipeline-V1.1/experiments/M10_baseline_20260112_1206) |
| M11 | [M11_baseline_20260112_1207](https://www.braintrust.dev/app/KCC/p/Keyword-Classification-Pipeline-V1.1/experiments/M11_baseline_20260112_1207) |
| M12 | [M12_baseline_20260112_1207](https://www.braintrust.dev/app/KCC/p/Keyword-Classification-Pipeline-V1.1/experiments/M12_baseline_20260112_1207) |
| M12b | [M12B_baseline_20260112_1208](https://www.braintrust.dev/app/KCC/p/Keyword-Classification-Pipeline-V1.1/experiments/M12B_baseline_20260112_1208) |
| M13 | [M13_baseline_20260112_1210](https://www.braintrust.dev/app/KCC/p/Keyword-Classification-Pipeline-V1.1/experiments/M13_baseline_20260112_1210) |
| M14 | [M14_baseline_20260112_1211](https://www.braintrust.dev/app/KCC/p/Keyword-Classification-Pipeline-V1.1/experiments/M14_baseline_20260112_1211) |
| M15 | [M15_baseline_20260112_1212](https://www.braintrust.dev/app/KCC/p/Keyword-Classification-Pipeline-V1.1/experiments/M15_baseline_20260112_1212) |
| M16 | [M16_baseline_20260112_1214](https://www.braintrust.dev/app/KCC/p/Keyword-Classification-Pipeline-V1.1/experiments/M16_baseline_20260112_1214) |

## Local Results

```
/home/kostya/PycharmProjects/PythonProject1/experiment_results/
├── experiment_summary_20260112_baseline.json
├── m01_results_20260112_1159.jsonl
├── m01a_results_20260112_1200.jsonl
├── m01b_results_20260112_1200.jsonl
├── m02_results_20260112_1201.jsonl
├── m02b_results_20260112_1313.jsonl
├── m04_results_20260112_1202.jsonl
├── m04b_results_20260112_1316.jsonl
├── m05_results_20260112_1202.jsonl
├── m05b_results_20260112_1317.jsonl
├── m06_results_20260112_1203.jsonl
├── m07_results_20260112_1204.jsonl
├── m08_results_20260112_1206.jsonl
├── m09_results_20260112_1206.jsonl
├── m10_results_20260112_1207.jsonl
├── m11_results_20260112_1207.jsonl
├── m12_results_20260112_1208.jsonl
├── m12b_results_20260112_1210.jsonl
├── m13_results_20260112_1211.jsonl
├── m14_results_20260112_1212.jsonl
├── m15_results_20260112_1214.jsonl
└── m16_results_20260112_1215.jsonl
```

## Next Steps

1. **Fix M13** - Review prompt, add more examples for product type matching
2. **Improve M12b** - Clarify decision tree steps in prompt
3. **Enhance M06** - Add taxonomy examples and structure validation
4. **Tune M08** - Define clearer ranking criteria
