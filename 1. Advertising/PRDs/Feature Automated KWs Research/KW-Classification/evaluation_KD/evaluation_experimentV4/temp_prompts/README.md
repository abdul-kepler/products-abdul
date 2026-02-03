# Temporary Prompts Folder

This folder is used by the prompt-improver agent for 15-iteration experiments.

## Purpose
- Store **temporary copies** of prompts during iteration testing
- Allow modifications without touching original prompt files
- Files here are **temporary** and should be deleted after experiments complete

## Rules
1. **Never commit modified prompts here** - they are temporary test files
2. **Original prompts in `prompts/modules/` are READ-ONLY**
3. **Always copy original -> temp before modifying**
4. **Delete temp files after experiment completes**

## Workflow
```bash
# 1. Copy original to temp
cp prompts/modules/m01_extract_own_brand_entities.md temp_prompts/m01_temp.md

# 2. Modify temp file for testing
# (agent modifies temp_prompts/m01_temp.md)

# 3. Run evaluation with temp prompt
python3 run_llm_judge.py --module M01 --prompt-file temp_prompts/m01_temp.md

# 4. Record results, then delete temp
rm temp_prompts/m01_temp.md
```
