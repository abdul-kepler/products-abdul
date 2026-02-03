# MIPRO Optimizer

DSPy MIPRO optimizer for binary classification modules.

## Installation

```bash
pip install dspy-ai python-dotenv
```

## Quick Start

```bash
# Run all classifier modules
./run_mipro.sh --preset lite

# Run specific modules
./run_mipro.sh -m m02 m04 m05

# Dry run
./run_mipro.sh --dry-run
```

## Supported Modules

| Module | Description | Output Type |
|--------|-------------|-------------|
| M02 | Exclude Broad Brand Match | `true/false` |
| M04 | Exclude Individual Brand Keyword | `true/false` |
| M05 | Exclude Competitor Keyword | `true/false` |
| M12 | Combined Classification | `true/false` |
| M13 | Product Type Check | `true/false` |
| M14 | Attribute Relevance | `true/false` |
| M15 | Keyword Quality | `true/false` |
| M16 | Final Validation | `true/false` |

## Presets

| Preset | Train | Dev | Demos | Use Case |
|--------|-------|-----|-------|----------|
| `lite` | 15 | 5 | 2 | Quick test |
| `light` | 30 | 10 | 3 | Default |
| `medium` | 50 | 15 | 4 | Balanced |
| `full` | 80 | 25 | 5 | Production |

```bash
./run_mipro.sh --preset medium
```

## Files

| File | Description |
|------|-------------|
| `run_mipro.sh` | Batch runner for MIPRO |
| `optimize.py` | **Unified optimizer for all modules** |
| `base_runner.py` | Core optimization logic |
| `module_config.py` | Module input/output configurations |
| `canary_loader.py` | Loads edge-case test data |
| `optimize_with_canary.py` | MIPRO with canary weighting |

## How MIPRO Works

1. **Bootstrap demos** - Find successful examples from training data
2. **Propose instructions** - Generate instruction candidates via LLM
3. **Bayesian search** - Find best (instruction, demos) combination
4. **Evaluate** - Score with exact-match metric
5. **Output** - Best performing configuration

```
Input: JSONL dataset + prompt template
         ↓
   Bootstrap few-shot demos
         ↓
   Propose instruction candidates
         ↓
   Bayesian optimization search
         ↓
   Evaluate with exact-match metric
         ↓
Output: optimized.json
```

## Output Format

Results saved to: `artifacts/dspy_mipro/{module}/{provider}/optimized.json`

```json
{
  "module": "m02",
  "provider": "gpt-4o-mini",
  "score": 0.95,
  "instruction": "Classify whether the brand keyword...",
  "demos": [
    {
      "brand_name": "Nike",
      "keyword": "nike shoes",
      "output": "false"
    }
  ],
  "input_keys": ["brand_name", "keyword"],
  "output_keys": ["output"]
}
```

## Canary Cases

Canary cases are critical edge cases that must pass. Located in `datasets/canary/`.

```bash
# Load canary cases for a module
python -c "from canary_loader import load_canary_cases; print(load_canary_cases('m02'))"
```

Canary cases are weighted 3x in evaluation to prevent regression.

## Troubleshooting

### MIPRO hangs on "Proposing instructions"

Large prompts can cause timeouts. Solutions:
1. Reduce threads: `./run_mipro.sh --threads 1`
2. Use smaller preset: `./run_mipro.sh --preset lite`
3. For text generation modules, use GEPA instead

### Low scores

1. Check dataset quality
2. Increase training size
3. Add more canary cases for edge scenarios

## CLI Reference

```bash
./run_mipro.sh [OPTIONS] [MODULES...]

Options:
  -m, --modules M1 M2   Specific modules to run
  -p, --preset NAME     lite | light | medium | full
  --provider MODEL      LLM provider (default: gpt-4o-mini)
  --train N             Training set size
  --dev N               Dev set size
  --demos N             Max few-shot demos
  --threads N           Parallel threads (default: 4)
  --dry-run             Show commands without executing
  -h, --help            Show help
```
