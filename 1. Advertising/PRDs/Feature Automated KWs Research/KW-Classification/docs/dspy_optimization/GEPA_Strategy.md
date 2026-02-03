# GEPA Optimization Strategy (Current State + Plan)

This document summarizes the current GEPA tooling in the repo, what data/assets exist, what is working well, what is missing, and a recommended optimization plan and reporting process.

## 1) What we already have

### GEPA tooling
- Scripts: `scripts/dspy_optimize/gepa/`
  - `optimize_gepa.py` - GEPA runner for text generation modules
  - `evaluator.py` - LLM-as-Judge semantic evaluator
  - `run_gepa.sh` - batch runner with presets and module groups
  - `README.md` - usage and overview
- Output directory: `artifacts/dspy_gepa/{module}/{provider}/{timestamp}/optimized.json`

### Module configuration
- `scripts/dspy_optimize/module_config.py` defines:
  - datasets and prompts per module
  - GEPA input templates and output keys
  - MIPRO/COPRO input/output keys

### Data sources and evaluation
- Training datasets: `datasets/single/*.jsonl`
  - V1 datasets with expected labels (used for GEPA/MIPRO)
  - SD1 datasets with empty expected for M07/M08
- LLM-judge results (rubrics): `evaluation_KD/evaluation_experimentV5/judge_results/`
- Experiment outputs: `experiment_results/` (module CSVs)
- DSPy plan notes: `docs/dspy_module_improvements.md`

### Recent helper assets
- Judge feedback JSONL (for GEPA feedback) can be generated from `evaluation_KD/.../judge_results` using:
  - `scripts/analysis/build_gepa_feedback_dataset.py`

## 2) What is good already

- GEPA runner is already integrated with presets and batch execution.
- Evaluator supports multiple modules and has a unified interface.
- Module configuration centralizes datasets and prompt paths.
- Judging infrastructure exists (rubrics + judge outputs) for feedback and error analysis.
 - Structured evaluators added for M06/M07/M08 (rule-based scoring on lists/tables) with optional LLM fallback.

## 3) Gaps / risks

- **Evaluator is generic semantic judge** for many modules; structured outputs now use rule-based scoring but still lack rubric-aware grading.
- **GEPA uses only expected outputs**; it does not yet leverage rubric-level failure reasons or judge feedback.
- **Dataset versions**: module_config uses m01_v2 etc; some modules have newer v3. Need explicit version control.
- **Train/val split** is sequential; no stratification or stability checks.
- **No canonical report** format across runs (metrics, cost, sample errors, prompt diff).
- **SD1 datasets** for M07/M08 are empty expected and should not be used for GEPA.
- **Prompt deployment** pipeline (copy optimized prompt to prompts/modules) is not automated or validated.

## 4) Recommended strategy (phased)

### Phase A: Data readiness
1) Lock dataset versions per module (v1 vs v2 vs v3). Update `module_config.py` accordingly.
2) Only run GEPA on datasets with non-empty expected.
3) Create stable train/dev splits and record them (seeded sampling).
4) For structured outputs (taxonomy/attribute tables), add a deterministic or rubric-guided score alongside LLM judge.

### Phase B: Evaluation alignment
1) Use `evaluation_KD` rubrics as the primary judge for GEPA scoring, when possible.
2) Convert judge outputs to feedback strings (rubric + reasoning + expected vs output) and pass to GEPA reflection.
3) If multiple judges are used, aggregate scores consistently:
   - example: average score or weighted average with a primary judge.
4) Keep schema validation strict (JSON schema check before scoring).
5) Incorporate academic best practices where cheap and robust:
   - multi-dimensional scoring (structure + content)
   - multi-round scoring (median/mean) for noisy judges
   - bias mitigation by randomizing order of candidates when comparing

### Phase C: Optimization flow
1) Start with lower-risk modules:
   - M09, M10 (short text outputs)
2) Then brand extraction:
   - M01, M01a, M01b
3) Then structured outputs:
   - M06, M07, M08
4) For each module:
   - run a small preset (lite) to validate
   - run medium/full with fixed train/val
   - store optimized prompt and a diff

### Phase D: Deployment and governance
1) Validate optimized prompts on a held-out evaluation set (judge + metrics).
2) Keep a prompt registry (source file, optimized version, date, metrics).
3) Only promote if it improves the primary metric without degrading secondary rubrics.
4) Log cost, time, and model versions used for reproducibility.

## 5) Suggested report structure

Create a per-run report file under `docs/dspy_optimization/reports/`:

```
# GEPA Report - {module} - {date}

## Summary
- Module:
- Dataset version:
- Task model / Reflection model / Judge model:
- Train/Val sizes:
- Budget:
- Initial score -> Final score:
- Cost estimate:

## Prompt Changes
- Diff summary (high-level)
- Key added constraints or clarifications

## Metrics
- Overall score change
- Top rubric improvements
- New failure modes (if any)

## Examples
- 2-3 improved cases
- 2-3 regressions

## Decision
- Promote / Hold / Reject
- Next steps
```

## 6) Concrete next actions

1) Update `module_config.py` to reflect the newest dataset versions (e.g., m01_v3 if desired).
2) Add a rubric-aware evaluator for structured outputs (M06-M08).
3) Integrate judge feedback into GEPA runs (use `build_gepa_feedback_dataset.py`).
4) Produce one full GEPA run for M09/M10 as baseline.
5) Create the first report under `docs/dspy_optimization/reports/`.

## 7) Checklist for each GEPA run

- [ ] Dataset expected is non-empty
- [ ] Train/val split recorded
- [ ] Prompt schema validation enabled
- [ ] Judge model and rules defined
- [ ] Cost/time recorded
- [ ] Report written
