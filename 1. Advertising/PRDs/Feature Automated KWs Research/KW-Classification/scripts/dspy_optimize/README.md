# DSPy Prompt Optimization

This directory contains tools for optimizing prompts using two different approaches:

1. **MIPRO** (DSPy) - For binary classifiers with exact-match metrics
2. **GEPA** - For text generation with semantic evaluation

## Quick Start

```bash
# Install dependencies
pip install dspy-ai gepa litellm python-dotenv

# Set API key
export OPENAI_API_KEY="sk-..."

# Run MIPRO for classifiers (M02, M04, M05, M12-M16)
cd mipro && ./run_mipro.sh --preset lite

# Run GEPA for text generation (M01, M01a, M01b, M06-M10)
cd gepa && ./run_gepa.sh --preset lite
```

## When to Use Which Optimizer

| Module Output Type | Optimizer | Why |
|--------------------|-----------|-----|
| `true/false`, `yes/no` | **MIPRO** | Exact match works perfectly |
| Free text, lists, JSON | **GEPA** | Semantic evaluation needed |

### Module Assignment

| Optimizer | Modules | Description |
|-----------|---------|-------------|
| **MIPRO** | M02, M04, M05, M12, M13, M14, M15, M16 | Binary classifiers |
| **GEPA** | M01, M01a, M01b, M06, M07, M08, M09, M10 | Text generation |

---

## MIPRO (DSPy)

MIPRO uses Bayesian optimization to find the best combination of:
- **Instruction** - How to describe the task
- **Few-shot demos** - Example input/output pairs

### Installation

```bash
pip install dspy-ai python-dotenv
```

### Files

| File | Description |
|------|-------------|
| `run_mipro.sh` | Batch runner for all classifier modules |
| `run_copro.sh` | Alternative COPRO optimizer |
| `base_runner.py` | Core MIPRO optimization logic |
| `module_config.py` | Module configurations (input/output keys) |
| `canary_loader.py` | Loads canary test cases |
| `optimize_with_canary.py` | MIPRO with canary case weighting |
| `optimize_m*.py` | Individual module optimizers |

### Usage

```bash
# Run all classifiers with lite preset
./run_mipro.sh --preset lite

# Run specific modules
./run_mipro.sh -m m02 m04

# Presets
./run_mipro.sh --preset lite    # train=15, dev=5, demos=2
./run_mipro.sh --preset light   # train=30, dev=10, demos=3
./run_mipro.sh --preset medium  # train=50, dev=15, demos=4
./run_mipro.sh --preset full    # train=80, dev=25, demos=5

# Dry run (show commands without executing)
./run_mipro.sh --dry-run
```

### How MIPRO Works

```
┌─────────────────────────────────────────────────────────────┐
│  1. Load training data (JSONL)                              │
│                    ↓                                        │
│  2. Bootstrap few-shot demos from successful examples       │
│                    ↓                                        │
│  3. Propose instruction candidates via LLM                  │
│                    ↓                                        │
│  4. Bayesian search over (instruction, demos) combinations  │
│                    ↓                                        │
│  5. Evaluate with exact-match metric                        │
│                    ↓                                        │
│  6. Return best (instruction, demos) pair                   │
└─────────────────────────────────────────────────────────────┘
```

### Output

Results saved to: `artifacts/dspy_mipro/{module}/{provider}/`

```json
{
  "module": "m02",
  "score": 0.95,
  "instruction": "Classify if brand should be excluded...",
  "demos": [
    {"input": "...", "output": "true"},
    {"input": "...", "output": "false"}
  ]
}
```

### Canary Cases

Canary cases are edge cases that must pass. They're weighted higher in evaluation.

```
datasets/canary/
├── m02_canary.jsonl
├── m04_canary.jsonl
├── m05_canary.jsonl
├── m12_canary.jsonl
└── m16_canary.jsonl
```

---

## GEPA (Genetic-Pareto)

GEPA uses evolutionary optimization with LLM reflection to improve prompts.
Better for text generation where output is semantic, not exact.

### Installation

```bash
pip install gepa litellm python-dotenv
```

### Files

| File | Description |
|------|-------------|
| `gepa/run_gepa.sh` | Batch runner |
| `gepa/optimize_gepa.py` | Core GEPA optimization |
| `gepa/evaluator.py` | LLM-as-Judge evaluator |

### Usage

```bash
cd gepa

# Run text generation modules
./run_gepa.sh --preset lite

# Run specific modules
./run_gepa.sh -m m09 m10

# Run all text gen modules
./run_gepa.sh --all

# Presets
./run_gepa.sh --preset lite    # train=10, val=3, budget=30
./run_gepa.sh --preset light   # train=20, val=5, budget=50
./run_gepa.sh --preset medium  # train=30, val=10, budget=100
./run_gepa.sh --preset full    # train=50, val=15, budget=200
```

### How GEPA Works

```
┌─────────────────────────────────────────────────────────────┐
│  1. Start with seed prompt                                  │
│                    ↓                                        │
│  2. Evaluate on training data with LLM-as-Judge             │
│                    ↓                                        │
│  3. LLM reflects on failures and proposes mutations         │
│                    ↓                                        │
│  4. Test mutated prompt on validation data                  │
│                    ↓                                        │
│  5. Keep if better (Pareto selection)                       │
│                    ↓                                        │
│  6. Repeat until budget exhausted                           │
│                    ↓                                        │
│  7. Return best prompt from Pareto frontier                 │
└─────────────────────────────────────────────────────────────┘
```

### Output

Results saved to: `artifacts/dspy_gepa/{module}/{provider}/{timestamp}/`

```json
{
  "module": "m01a",
  "final_score": 0.733,
  "initial_score": 0.700,
  "improvement": 0.033,
  "optimized_prompt": "# Task: ExtractOwnBrandVariations..."
}
```

---

## Comparison: MIPRO vs GEPA

| Aspect | MIPRO | GEPA |
|--------|-------|------|
| **Approach** | Bayesian + demo selection | Evolutionary + LLM reflection |
| **Optimizes** | Instruction + few-shot demos | Entire prompt text |
| **Metric** | Exact match | Semantic (LLM-as-Judge) |
| **Speed** | Faster | Slower |
| **Cost** | Cheaper | More expensive |
| **Best for** | Classification | Text generation |
| **Stability** | Can hang on large prompts | More stable |
| **Overfit risk** | Higher (e.g., "kitchen context") | Lower |

---

## Environment Setup

### Required Environment Variables

```bash
# .env file in project root
OPENAI_API_KEY=sk-...
```

### Python Dependencies

```bash
pip install dspy-ai gepa litellm python-dotenv
```

### Directory Structure

```
scripts/dspy_optimize/
├── README.md              # This file (overview)
│
├── mipro/                 # MIPRO optimizer (classifiers)
│   ├── README.md          # MIPRO documentation
│   ├── run_mipro.sh         # Batch runner
│   ├── optimize.py        # Unified optimizer for all modules
│   ├── base_runner.py     # Core optimization logic
│   ├── module_config.py   # Module configurations
│   ├── canary_loader.py   # Edge case loader
│   └── optimize_with_canary.py
│
├── copro/                 # COPRO optimizer (instruction-only)
│   ├── README.md          # COPRO documentation
│   ├── run_copro.sh       # Batch runner
│   └── optimize_copro.py  # Core optimization
│
├── gepa/                  # GEPA optimizer (text generation)
│   ├── README.md          # GEPA documentation
│   ├── run_gepa.sh        # Batch runner
│   ├── optimize_gepa.py   # Core optimization
│   └── evaluator.py       # LLM-as-Judge

artifacts/
├── dspy/                  # MIPRO results
│   └── {module}/{provider}/optimized.json
│
└── gepa/                  # GEPA results
    └── {module}/{provider}/{timestamp}/optimized.json
```

---

## Troubleshooting

### MIPRO hangs on "Proposing instructions"

MIPRO can hang when prompts are too large. Solutions:
1. Use `--threads 1` to avoid rate limiting
2. Switch to GEPA for text generation modules
3. Reduce `--train-size`

### GEPA score shows 0

Fixed in latest version. Score is now correctly extracted from `val_aggregate_scores`.

### API Rate Limits

```bash
# Reduce parallel threads
./run_mipro.sh --threads 1

# Use smaller preset
./run_mipro.sh --preset lite
```

---

## References

- [DSPy Documentation](https://dspy-docs.vercel.app/)
- [GEPA GitHub](https://github.com/gepa-ai/gepa)
- [LiteLLM](https://docs.litellm.ai/)
