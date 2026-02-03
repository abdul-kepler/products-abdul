# DSPy Optimization Plan for KW Classification v1.1

Objective: automate prompt/decision-rule tuning across modules M01–M16 using DSPy optimizers (prefer MIPROv2; keep GEPA/SIMBA as backups). Results must stay JSON-schema compliant.

## Dataset + Prompt Sources
- Datasets: `datasets/*.jsonl` (module-aligned names, e.g., `m01_extract_own_brand_entities_v3.jsonl`).
- Original prompts: `prompts/providers/<provider>/single|batch/*.md`.
- JSON schemas: `prompts/schemas/single|batch/*.json`.
- Experiments (Braintrust): project `Keyword-Classification-Pipeline-V1.1` (ID `17b25eb4-95bf-499b-9ee3-1b6118546ecc`).

## Target Modules (prioritized)
1) Brand scope path A: M01, M02, M04, M05 (providers: gpt-4o-mini, gpt-4o, gpt-5, claude-sonnet, gemini-2.0-flash).
2) Brand scope path B: M01a, M01b, M02b, M04b, M05b.
3) Relevance chain: M12 → M13 → M14 → M15 → M16, plus M12b.
4) Product definition: M06–M11 (lower priority).

## DSPy Configuration (defaults)
- LM: set per run (`--lm`), default `gpt-4o-mini`; can override to `gpt-4o`, `gpt-5`, `claude-sonnet`, `gemini-2.0-flash`.
- Optimizer: `MIPROv2(metric, max_bootstrapped_demos=6, max_labeled_demos=6, depth=2)`.
- Metric:
  - Extraction/generation (M01, M01a, M01b, M06…): exact-match or token-level F1 over expected JSON fields.
  - Binary/tri-class (M02/04/05 + b-variants): accuracy/F1 on labels (OB/CB/NB).
  - R/S/C/N (M12/M12b): accuracy/F1 on class.
- Train/dev split: use first N for train, last 20 for dev (override via CLI).

## Workflow
1) Run optimizer per module/provider with `scripts/dspy/optimize_module.py --module m01 --provider gpt-4o-mini`.
2) Optimizer emits:
   - `artifacts/dspy/<module>/<provider>/compiled.json` (DSPy compiled module).
   - `artifacts/dspy/<module>/<provider>/report.md` (metric, top errors, chosen demos).
3) Optionally export improved prompt text and patch the corresponding `prompts/providers/<provider>/...md` after review.
4) Log experiments to Braintrust via `scripts/dspy/upload_to_braintrust.py` (to implement after first successful run).

## Mapping: module → dataset → schema
- M01 → `datasets/m01_extract_own_brand_entities_v3.jsonl` → `prompts/schemas/single/m01_extract_own_brand_entities_schema.json`
- M01a → `datasets/m01a_extract_own_brand_variations_v2.jsonl` → `prompts/schemas/single/m01a_extract_own_brand_variations_schema.json`
- M01b → `datasets/m01b_extract_brand_related_terms.jsonl` → `prompts/schemas/single/m01b_extract_brand_related_terms_schema.json`
- M02 → `datasets/m02_classify_own_brand_keywords_v3.jsonl` → `prompts/schemas/single/m02_classify_own_brand_keywords_schema.json`
- M02b → `datasets/m02b_classify_own_brand_keywords_v3.jsonl` → `prompts/schemas/single/m02b_classify_own_brand_keywords_schema.json`
- M04 → `datasets/m04_classify_competitor_brand_keywords_v3.jsonl` → `prompts/schemas/single/m04_classify_competitor_brand_keywords_schema.json`
- M04b → `datasets/m04b_classify_competitor_brand_keywords_v3.jsonl` → `prompts/schemas/single/m04b_classify_competitor_brand_keywords_schema.json`
- M05 → `datasets/m05_classify_nonbranded_keywords_v3.jsonl` → `prompts/schemas/single/m05_classify_nonbranded_keywords_schema.json`
- M05b → `datasets/m05b_classify_nonbranded_keywords_v3.jsonl` → `prompts/schemas/single/m05b_classify_nonbranded_keywords_schema.json`
- M06–M16 analogічно (див. `prompts/schemas/single/`).

## Next Steps
- [ ] Run `optimize_module.py` for M01 (gpt-4o-mini) to validate pipeline end-to-end.
- [ ] Add Braintrust upload helper for DSPy run stats.
- [ ] After validation, batch-run M02/M04/M05 and b-variants.
