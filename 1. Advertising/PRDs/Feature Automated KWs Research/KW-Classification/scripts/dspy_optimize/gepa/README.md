# GEPA Optimizer

Genetic-Pareto optimizer for text generation modules using LLM reflection.

## Installation

```bash
pip install gepa litellm python-dotenv
```

## Quick Start

```bash
# Run text generation modules
./run_gepa.sh --preset lite

# Run specific modules
./run_gepa.sh -m m09 m10

# Run all text gen modules
./run_gepa.sh --all
```

## Supported Modules

| Module | Description | Output Type |
|--------|-------------|-------------|
| M01 | Extract Own Brand Entities | `list[string]` |
| M01a | Extract Own Brand Variations | `list[string]` |
| M01b | Extract Brand Related Terms | `multi-field` |
| M06 | Generate Product Type Taxonomy | `list[object]` |
| M07 | Extract Product Attributes | `multi-field` |
| M08 | Assign Attribute Ranks | `list[object]` |
| M09 | Identify Primary Intended Use | `string` |
| M10 | Validate Primary Intended Use | `string` |

## Presets

| Preset | Train | Val | Budget | Use Case |
|--------|-------|-----|--------|----------|
| `lite` | 10 | 3 | 30 | Quick test (~3 min) |
| `light` | 20 | 5 | 50 | Default (~5 min) |
| `medium` | 30 | 10 | 100 | Balanced (~10 min) |
| `full` | 50 | 15 | 200 | Production (~20 min) |

```bash
./run_gepa.sh --preset medium
```

## Files

| File | Description |
|------|-------------|
| `run_gepa.sh` | Batch runner |
| `optimize_gepa.py` | Core GEPA optimization |
| `evaluator.py` | LLM-as-Judge evaluator |

## How GEPA Works

GEPA uses evolutionary optimization with LLM reflection:

```
┌─────────────────────────────────────────────────────────────┐
│  1. Start with seed prompt                                  │
│                    ↓                                        │
│  2. Evaluate on training data (LLM-as-Judge)               │
│                    ↓                                        │
│  3. Select candidates from Pareto frontier                  │
│                    ↓                                        │
│  4. LLM reflects on failures                               │
│     "Why did this prompt fail? How to improve?"            │
│                    ↓                                        │
│  5. Generate mutated prompt based on reflection            │
│                    ↓                                        │
│  6. Evaluate mutation on validation data                   │
│                    ↓                                        │
│  7. Keep if better (Pareto selection)                      │
│                    ↓                                        │
│  8. Repeat until budget exhausted                          │
│                    ↓                                        │
│  9. Return best prompt from Pareto frontier                │
└─────────────────────────────────────────────────────────────┘
```

### Key Concepts

**Pareto Frontier**: Set of prompts where no single prompt dominates all others across all examples. GEPA tracks prompts that excel on different subsets.

**LLM Reflection**: Instead of random mutations, GEPA uses a strong LLM (GPT-4o) to analyze WHY a prompt failed and propose targeted improvements.

**LLM-as-Judge**: Evaluates outputs semantically rather than exact match. Handles variations like "portable hydration" ≈ "beverage storage".

## Output Format

Results saved to: `artifacts/dspy_gepa/{module}/{provider}/{timestamp}/optimized.json`

```json
{
  "module": "m01a",
  "module_name": "ExtractOwnBrandVariations",
  "task_model": "openai/gpt-4o-mini",
  "reflection_model": "openai/gpt-4o",
  "judge_model": "gpt-4o",
  "budget": 30,
  "train_size": 10,
  "val_size": 3,
  "initial_prompt_length": 4756,
  "optimized_prompt_length": 3366,
  "optimized_prompt": "# Task: ExtractOwnBrandVariations...",
  "final_score": 0.733,
  "initial_score": 0.700,
  "improvement": 0.033
}
```

## Evaluator Architecture

GEPA uses specialized evaluators for different module types:

### Evaluator Types

| Type | Modules | Metric | Best For |
|------|---------|--------|----------|
| **ListEvaluator** | M01, M01a, M01b, M11 | F1 + constraints | List outputs |
| **ClassifierEvaluator** | M12, M12B, M13-M16 | Confusion weights | Classifications |
| **StructuredEvaluator** | M06, M07, M08 | Rule + hybrid | Complex JSON |
| **LLMJudgeEvaluator** | M09, M10 | Semantic similarity | Short text |

### LLM-as-Judge (M09, M10)

Semantic comparison using GPT-4o:

```python
Score 1.0: Semantically identical
Score 0.8-0.9: Same core meaning, minor differences
Score 0.6-0.7: Partially overlapping meaning
Score 0.4-0.5: Weak relationship
Score 0.0-0.1: Completely different
```

### Classifier Scoring (M12, M12B, M13-M16)

Uses confusion matrix weights for partial credit:

```
R → S: 0.5 (both "relevant family")
R → C: 0.3 (both positive)
S → C: 0.4 (both non-primary)
R → N: 0.0 (severe error)
```

### List Scoring (M01, M01a, M01b, M11)

F1-score with module-specific constraints:

| Module | Constraint |
|--------|------------|
| M01 | min_count ≥ 1 |
| M01a | count ∈ [8-12], first = canonical |
| M01b | weighted multi-field |
| M11 | max 3, ~90% should be empty |

### Hybrid scoring for structured outputs (M06/M07/M08)

Structured modules use rule-based scoring with optional LLM fallback:

```
final_score = 0.7 * rule_score + 0.3 * judge_score
```

This improves robustness for synonyms and formatting variants.

## Why GEPA over MIPRO for Text Generation?

| Aspect | MIPRO | GEPA |
|--------|-------|------|
| **Metric** | Exact match | Semantic (LLM judge) |
| **Optimization** | Bayesian search | Evolutionary + reflection |
| **Feedback** | Score only | Why it failed + how to fix |
| **Overfit risk** | High ("kitchen context" bug) | Low |
| **Large prompts** | Can hang | Stable |

### Real Example

**MIPRO on M01a**: Hung for 19+ minutes, then failed
**GEPA on M01a**: Completed in 3 min, +3.3% improvement

## CLI Reference

```bash
./run_gepa.sh [OPTIONS] [MODULES...]

Options:
  -m, --modules M1 M2   Specific modules to run
  -p, --preset NAME     lite | light | medium | full
  --all                 Run all text gen modules
  --p1                  Priority 1: m09, m10
  --p2                  Priority 1+2: + m01, m01a, m01b
  --task-model MODEL    Task LLM (default: openai/gpt-4o-mini)
  --reflection MODEL    Reflection LLM (default: openai/gpt-4o)
  --judge MODEL         Judge LLM (default: gpt-4o)
  --judge-rounds N      Judge rounds (default: 1)
  --judge-agg NAME      mean | median (default: mean)
  --hybrid-weight W     LLM fallback weight for structured modules (default: 0.3)
  --train N             Training set size
  --val N               Validation set size
  --budget N            Max metric calls
  --dry-run             Show commands without executing
  -h, --help            Show help
```

## Troubleshooting

### Score shows 0.000

Fixed in latest version. The score is now correctly extracted from `val_aggregate_scores`.

### Slow optimization

GEPA is slower than MIPRO because:
1. Each iteration calls reflection LLM (GPT-4o)
2. LLM-as-Judge evaluates each output

Reduce cost/time with:
```bash
./run_gepa.sh --preset lite --budget 20
```

### API rate limits

```bash
# GEPA handles rate limits internally
# If issues persist, reduce budget
./run_gepa.sh --budget 30
```

## References

- [GEPA GitHub](https://github.com/gepa-ai/gepa)
- [GEPA Paper](https://arxiv.org/abs/...) (if available)
- [LiteLLM Docs](https://docs.litellm.ai/)
