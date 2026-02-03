# COPRO Optimizer

DSPy COPRO optimizer - focuses on instruction text improvement without few-shot demos.

## Installation

```bash
pip install dspy-ai python-dotenv
```

## Quick Start

```bash
# Run specific modules
./run_copro.sh -m m02 m04

# Run all classifier modules
./run_copro.sh

# Dry run
./run_copro.sh --dry-run
```

## What is COPRO?

COPRO (Cooperative Prompt Optimization) is a simpler alternative to MIPRO. Key differences:

| Aspect | MIPRO | COPRO |
|--------|-------|-------|
| **Optimizes** | Instruction + few-shot demos | Instruction only |
| **Method** | Bayesian search | Iterative rewriting |
| **Complexity** | Higher | Lower |
| **Speed** | Slower | Faster |
| **Overfitting** | Can overfit to demos | Less risk |

## When to Use COPRO

- When you don't need few-shot examples
- When MIPRO is overfitting to specific demos
- For faster iteration during development
- When your prompt is already good but needs refinement

## How COPRO Works

```
┌─────────────────────────────────────────────────────────────┐
│  1. Start with seed instruction (your prompt)              │
│                    ↓                                        │
│  2. Generate N instruction candidates (breadth)            │
│                    ↓                                        │
│  3. Evaluate each candidate on training data               │
│                    ↓                                        │
│  4. Select best candidate                                  │
│                    ↓                                        │
│  5. Repeat for D iterations (depth)                        │
│                    ↓                                        │
│  6. Return best instruction found                          │
└─────────────────────────────────────────────────────────────┘
```

### Key Parameters

- **breadth**: Number of instruction candidates per iteration (default: 3)
- **depth**: Number of optimization iterations (default: 2)

Higher values = more exploration, but slower and more expensive.

## Files

| File | Description |
|------|-------------|
| `run_copro.sh` | Batch runner |
| `optimize_copro.py` | Core COPRO logic |

## Supported Modules

Same as MIPRO - all binary classifiers:

| Module | Description |
|--------|-------------|
| M02 | Exclude Broad Brand Match |
| M04 | Exclude Individual Brand Keyword |
| M05 | Exclude Competitor Keyword |
| M12 | Combined Classification |
| M13 | Product Type Check |
| M14 | Attribute Relevance |
| M15 | Keyword Quality |
| M16 | Final Validation |

## Output Format

Results saved to: `artifacts/dspy_copro/{module}/{provider}/copro_result.json`

```json
{
  "module": "m02",
  "provider": "gpt-4o-mini",
  "optimizer": "COPRO",
  "breadth": 3,
  "depth": 2,
  "train_size": 30,
  "dev_size": 10,
  "original_prompt": "...",
  "optimized_instruction": "...",
  "input_keys": ["brand_name", "keyword"],
  "output_keys": ["output"]
}
```

## CLI Reference

```bash
./run_copro.sh [OPTIONS] [MODULES...]

Options:
  -m, --modules M1 M2   Specific modules to run
  --provider MODEL      LLM provider (default: gpt-4o-mini)
  --train N             Training set size (default: 30)
  --dev N               Validation set size (default: 10)
  --breadth N           Candidates per iteration (default: 3)
  --depth N             Iterations (default: 2)
  --temp T              Temperature (default: 0.2)
  --dry-run             Show commands without executing
  -h, --help            Show help
```

## Examples

```bash
# Quick test with minimal exploration
./run_copro.sh -m m02 --breadth 2 --depth 1

# More thorough optimization
./run_copro.sh -m m02 --breadth 5 --depth 3

# Single module with Python
python optimize_copro.py m02 --breadth 3 --depth 2
```

## Comparison: MIPRO vs COPRO vs GEPA

| Aspect | MIPRO | COPRO | GEPA |
|--------|-------|-------|------|
| **Best for** | Classifiers | Classifiers | Text generation |
| **Optimizes** | Instruction + demos | Instruction only | Entire prompt |
| **Method** | Bayesian + demo selection | Iterative rewriting | Evolutionary + reflection |
| **Metric** | Exact match | Exact match | Semantic (LLM judge) |
| **Speed** | Medium | Fast | Slow |
| **Cost** | Medium | Low | High |

## Note on Dependencies

COPRO imports from the `mipro/` folder:
- `module_config.py` - Module configurations
- `base_runner.py` - Common utilities

Make sure to run from the `copro/` directory or adjust PYTHONPATH.
