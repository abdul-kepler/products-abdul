# Prompt Optimization Agent

Iterative prompt optimizer using LLM-as-a-judge evaluation for the KW-Classification pipeline.

## Overview

This agent automates prompt improvement through:
1. **Rule Extraction** - Extracts classification rules from the prompt
2. **LLM-as-a-Judge Scoring** - Evaluates each output against rules
3. **Failure Analysis** - Groups failures by rule to identify weak spots
4. **Suggestion Generation** - GPT-4o generates improvement suggestions
5. **Prompt Rewriting** - o3-mini reasoning model rewrites the prompt
6. **Iteration** - Repeats until target accuracy or max iterations

## Usage

### Command Line

```bash
# Basic usage - auto-detects prompt and dataset for module
python optimizer/run_optimization.py --module m02

# Specify files explicitly
python optimizer/run_optimization.py \
    --prompt prompts/modules/m02_own_brand.md \
    --dataset datasets/m02_dataset.jsonl

# With options
python optimizer/run_optimization.py \
    --module m02 \
    --max-iterations 5 \
    --target-accuracy 0.9 \
    --max-tests 20

# List available prompts and datasets
python optimizer/run_optimization.py --list
```

### Python API

```python
from optimizer import PromptOptimizer

# Initialize optimizer
optimizer = PromptOptimizer(
    module="m02",
    model="gpt-4o",           # Classification model
    optimizer_model="o3-mini", # Prompt rewriting model
    verbose=True
)

# Run optimization
result = optimizer.optimize(
    prompt_path="prompts/modules/m02_own_brand.md",
    dataset_path="datasets/m02_dataset.jsonl",
    max_iterations=3,
    target_accuracy=0.85,
    max_tests=50  # Optional: limit test cases
)

# Access results
print(f"Best accuracy: {result.best_accuracy:.1%}")
print(f"Improved prompt:\n{result.improved_prompt}")

# Save results
optimizer.save_result(result, "results/optimization_m02.json")
```

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `--module` | m02 | Module to optimize (m02, m04, m05, etc.) |
| `--prompt` | auto | Path to prompt file |
| `--dataset` | auto | Path to dataset JSONL file |
| `--max-iterations` | 3 | Maximum optimization iterations |
| `--target-accuracy` | 0.85 | Stop when accuracy reaches this |
| `--max-tests` | all | Limit number of test cases |
| `--model` | gpt-4o | Model for classification |
| `--optimizer-model` | o3-mini | Model for prompt rewriting |
| `--quiet` | false | Suppress verbose output |

## Output

Results are saved to `experiment_results/optimization_<module>_<timestamp>.json`:

```json
{
  "success": true,
  "best_iteration": 2,
  "total_iterations": 3,
  "original_accuracy": 0.72,
  "best_accuracy": 0.88,
  "scorers_used": ["ob_exact_match", "ob_fuzzy_match", ...],
  "iteration_results": [
    {
      "iteration": 1,
      "accuracy": 0.72,
      "aggregate_scores": {...},
      "improvements": [...]
    },
    ...
  ]
}
```

Prompts are saved separately to `*.prompts.json`.

## Flow Diagram

```
                    +------------------+
                    |   Load Prompt    |
                    |   Load Dataset   |
                    +--------+---------+
                             |
                             v
                    +------------------+
                    | Extract Rules    |
                    | Generate Scorers |
                    +--------+---------+
                             |
            +----------------+----------------+
            |                                 |
            v                                 |
   +------------------+                       |
   | Run Classification|                      |
   | on all keywords  |                       |
   +--------+---------+                       |
            |                                 |
            v                                 |
   +------------------+                       |
   | Score with LLM   |                       |
   | Judges (per rule)|                       |
   +--------+---------+                       |
            |                                 |
            v                                 |
   +------------------+                       |
   | Analyze Failures |                       |
   | Group by Rule    |                       |
   +--------+---------+                       |
            |                                 |
            v                                 |
   +------------------+     Yes               |
   | Accuracy >= 85%? +------------------+    |
   +--------+---------+                  |    |
            | No                         |    |
            v                            |    |
   +------------------+                  |    |
   | Generate         |                  |    |
   | Suggestions      |                  |    |
   | (GPT-4o)         |                  |    |
   +--------+---------+                  |    |
            |                            |    |
            v                            |    |
   +------------------+                  |    |
   | Rewrite Prompt   |                  |    |
   | (o3-mini)        |                  |    |
   +--------+---------+                  |    |
            |                            |    |
            +----------------------------+    |
                         Loop                 |
                                              v
                                     +------------------+
                                     | Save Results     |
                                     | Return Best      |
                                     +------------------+
```

## Integration with Braintrust

This optimizer works alongside Braintrust but runs locally without pushing to the Braintrust API. It uses the same scoring concepts:

- **Scorers** - Rule-based evaluators (like Braintrust scorers)
- **Test Cases** - Input/expected pairs from JSONL datasets
- **Metrics** - Accuracy, pass rate, per-rule scores

To compare optimized prompts in Braintrust:
1. Run optimization locally
2. Take the improved prompt
3. Run Braintrust evaluation with the new prompt
4. Compare scores in Braintrust UI

## Requirements

```
openai>=1.0.0
python-dotenv
```

Set `OPENAI_API_KEY` in your `.env` file.

## Available Modules Reference

The KW-Classification pipeline has 22 prompts organized into three phases. Each module has a corresponding dataset in `datasets/` with test cases.

### Phase 1: Brand Classification (M01-M05)

| Module | Name | Purpose | Records |
|--------|------|---------|---------|
| **M01** | ExtractOwnBrandEntities | Extract brand entities from product listings (brand name vs product words) | 99 |
| **M01a** | ExtractOwnBrandVariations | Generate spelling variations of own brand (typos, abbreviations) | 99 |
| **M01b** | ExtractBrandRelatedTerms | Extract brand-related terms (sub-brands, product lines) | 99 |
| **M02** | ClassifyOwnBrandKeywords | Classify if keyword contains **Own Brand (OB)** - verification-first, anti-hallucination | 916 |
| **M02_v3** | Own Brand Classification v3 | Same as M02, refined version | 916 |
| **M03** | GenerateCompetitorBrandEntities | Identify competitor brands for a product category (generative - no input list) | 19 |
| **M04** | ClassifyCompetitorBrandKeywords | Classify if keyword contains **Competitor Brand (CB)** - two-phase: check OB first | 1,759 |
| **M04_v3** | Competitor Brand Classification v3 | Same as M04, refined version | 1,759 |
| **M05** | ClassifyNonBrandedKeywords | Classify truly generic keywords as **Non-Branded (NB)** - catch ALL brand refs | 1,759 |
| **M05_v3** | Non-Branded Classification v3 | Same as M05, refined version | 1,759 |

### Phase 2: Product Analysis (M06-M08)

| Module | Name | Purpose | Records |
|--------|------|---------|---------|
| **M06** | GenerateProductTypeTaxonomy | Generate 3-level product type taxonomy (Category > Type > Subtype) | 12 |
| **M07** | ExtractProductAttributes | Extract searchable attributes (variants, use cases, audiences) | 12 |
| **M08** | AssignAttributeRanks | Rank attributes by search relevance (unique ranks per type) | 12 |

### Phase 3: Relevance Classification (M09-M16)

| Module | Name | Purpose | Records |
|--------|------|---------|---------|
| **M09** | IdentifyPrimaryIntendedUse | Distill product description into single primary use statement | 10 |
| **M10** | ValidatePrimaryIntendedUse | Validate/refine the primary intended use | 10 |
| **M11** | IdentifyHardConstraints | Extract hard constraints (size, voltage, compatibility) using "Complete Removal Test" | 10 |
| **M12** | HardConstraintViolationCheck | Check if keyword requests value conflicting with product constraints | 443 |
| **M12b** | CombinedClassificationDecision | Final **R/S/C/N** decision using decision tree | 443 |
| **M13** | ProductTypeCheck | Check if keyword's product type matches the product | 439 |
| **M14** | PrimaryUseCheck | Check if primary use matches (same product type) - focus on PURPOSE not features | 229 |
| **M15** | SubstituteCheck | Check if different product type can fulfill same need → **Substitute (S)** | 210 |
| **M16** | ComplementaryCheck | Check if products work together in usage → **Complementary (C)** | 179 |

### Classification Output Summary

**Brand Classification (M02/M04/M05):**
- `OB` = Own Brand
- `CB` = Competitor Brand
- `NB` = Non-Branded (generic)

**Relevance Classification (M12b):**
- `R` = Relevant (same type, same use)
- `S` = Substitute (different type, same use)
- `C` = Complementary (used together)
- `N` = Not Relevant (constraint violation or unrelated)

### Recommended Modules for Optimization

| Module | Why Good for Testing |
|--------|---------------------|
| **m02** | Core OB classification, clear pass/fail, 916 test cases |
| **m04** | Largest dataset (1,759), complex two-phase logic |
| **m05** | Catch-all for non-branded, tricky edge cases |
| **m12b** | Final R/S/C/N decision, multi-class classification |
| **m13** | Product type matching, good size (439 cases) |

### Quick Start Examples

```bash
# Test with small sample first
python optimizer/run_optimization.py --module m02 --max-tests 30 --max-iterations 2

# Full optimization on own brand classification
python optimizer/run_optimization.py --module m02 --max-iterations 3 --target-accuracy 0.85

# Optimize competitor brand (larger dataset)
python optimizer/run_optimization.py --module m04 --max-tests 100 --max-iterations 3

# Optimize relevance classification
python optimizer/run_optimization.py --module m12b --max-tests 50 --target-accuracy 0.90
```
