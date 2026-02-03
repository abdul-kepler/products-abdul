# GEPA Evaluators Architecture Plan

## Overview

This document describes the specialized evaluators for GEPA optimization, based on:
- Academic research from `docs/academic-research_KD/` (29 papers, 2023-2025)
- Katya's rubrics from `evaluation_KD/config/rubrics_v5.yaml` (69+ rubrics)
- Module output analysis from datasets

## Evaluator Taxonomy

| Evaluator Type | Modules | Metric | Best For |
|----------------|---------|--------|----------|
| **ListEvaluator** | M01, M01a, M01b, M11 | F1 + constraints | Variable-length list outputs |
| **ClassifierEvaluator** | M12, M12B, M13-M16 | Confusion matrix | Discrete classifications |
| **StructuredEvaluator** | M06, M07, M08 | Rule-based + hybrid | Complex JSON structures |
| **LLMJudgeEvaluator** | M09, M10, M02-M05 | Semantic similarity | Short text generation |

---

## Module → Evaluator Mapping

### List Output Modules

| Module | Output | Evaluator | Key Metrics | Constraints |
|--------|--------|-----------|-------------|-------------|
| **M01** | `brand_entities[]` | ListEvaluator | F1, precision, recall | min_count ≥ 1 |
| **M01a** | `variations[]` | ListEvaluator | F1 + canonical_first | count ∈ [8, 12] |
| **M01b** | `sub_brands[]`, `manufacturer{}` | ListEvaluator | Weighted multi-field F1 | - |
| **M11** | `hard_constraints[]` | ListEvaluator | F1 | max_count ≤ 3, ~90% empty |

### Classifier Modules

| Module | Output | Classes | Evaluator | Scoring |
|--------|--------|---------|-----------|---------|
| **M12** | `relevancy` | N/null | ClassifierEvaluator | Confusion weights |
| **M12B** | `relevancy` | R/S/C/N | ClassifierEvaluator | Confusion weights |
| **M13** | `same_type` | true/false | ClassifierEvaluator | Boolean exact match |
| **M14** | `relevancy` | R/null | ClassifierEvaluator | Binary weights |
| **M15** | `relevancy` | S/null | ClassifierEvaluator | Binary weights |
| **M16** | `relevancy` | C/null | ClassifierEvaluator | Binary weights |

### Text Generation Modules

| Module | Output | Evaluator | Scoring |
|--------|--------|-----------|---------|
| **M09** | `primary_use` | LLMJudgeEvaluator | Semantic similarity |
| **M10** | `validated_use` | LLMJudgeEvaluator | Semantic similarity |

---

## Confusion Matrix Weights (ClassifierEvaluator)

Based on Katya's rubrics, misclassifications have different severity:

### M12/M12B: R/S/C/N Classification

```
Expected → Actual   Score   Reasoning
─────────────────────────────────────────────────
R → R               1.0     Exact match
R → S               0.5     Both "relevant family"
R → C               0.3     Both positive relevance
R → N               0.0     Complete opposite (severe)
S → R               0.5     Both "relevant family"
S → S               1.0     Exact match
S → C               0.4     Both non-primary but useful
S → N               0.1     Missed useful keyword
C → R               0.3     Both positive relevance
C → S               0.4     Both non-primary but useful
C → C               1.0     Exact match
C → N               0.1     Missed complementary
N → R               0.0     False positive (severe)
N → S               0.1     Minor false positive
N → C               0.1     Minor false positive
N → N               1.0     Exact match
null → N            1.0     Equivalent (M12 allows null for N)
```

### M13: Boolean same_type

```
Expected → Actual   Score
───────────────────────────
true → true         1.0
false → false       1.0
true → false        0.0
false → true        0.0
```

---

## Academic Best Practices Applied

### From llm-as-a-judge-research.md

1. **Multi-round scoring** (Section 1)
   - Implemented: `judge_rounds` parameter, median/mean aggregation
   - Temperature > 0 for variance in multi-round

2. **Swap augmentation for bias mitigation** (JudgeLM paper)
   - TODO: Add position swapping for pairwise comparisons

3. **Confidence filtering** (Survey 2411.15594)
   - TODO: Add confidence threshold, flag low-confidence for review

4. **Error localization** (TIGERScore paper)
   - Partially implemented: feedback includes specific failure reasons

### From Katya's Rubrics

1. **Binary Pass/Fail** → Converted to weighted scores for GEPA
2. **Edge cases** → Built into constraint validation:
   - M01a: canonical first, count 8-12
   - M11: expected 90% empty
   - M01b: manufacturer null when = brand

---

## Hybrid Scoring Strategy

For modules with ambiguous outputs, we use hybrid scoring:

```
final_score = (1.0 - hybrid_weight) * rule_score + hybrid_weight * judge_score
```

Default weights:
- `hybrid_weight = 0.3` (70% rule, 30% judge)
- Only call judge when rule_score is in "ambiguous zone" (0 < score < 1)

---

## Future Improvements

### Priority 1 (Next Sprint)
- [ ] Swap augmentation for position bias
- [ ] Confidence scoring per evaluation
- [ ] Schema validation before scoring

### Priority 2
- [ ] Multi-judge ensemble (PoLL approach: 3 diverse models)
- [ ] Inter-judge agreement metrics (Cohen's kappa)
- [ ] Calibration tests on held-out data

### Priority 3
- [ ] Fine-tuned lightweight judge (PROMETHEUS-style)
- [ ] Error localization with TIGERScore format
- [ ] Rubric-specific few-shot examples

---

## Testing

Run evaluator tests:
```bash
python -m pytest scripts/dspy_optimize/gepa/tests/test_evaluators.py -v
```

Quick validation:
```bash
cd scripts/dspy_optimize/gepa
python evaluator.py  # Lists all available evaluators
```

---

## References

- Academic papers: `docs/academic-research_KD/llm-as-a-judge-research.md`
- Rubric definitions: `evaluation_KD/config/rubrics_v5.yaml`
- Module configs: `scripts/dspy_optimize/module_config.py`
