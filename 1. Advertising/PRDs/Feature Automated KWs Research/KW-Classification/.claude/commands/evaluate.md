# LLM-as-a-Judge Evaluation Workflow

Run the LLM-as-a-Judge evaluation workflow on specified modules.

## Usage
```
/evaluate <module>     # Run evaluation on specific module (m01, m02, etc.)
/evaluate all          # Run evaluation on all modules
```

## Arguments
- `$ARGUMENTS` - Module name (m01, m01a, m01b, m02, m04, etc.) or "all"

## Instructions

You are the **Orchestrator Agent**. Follow these steps:

1. **Read the orchestrator instructions**: `evaluation_KD/agents/00_orchestrator.md`
2. **Read the workflow reference**: `evaluation_KD/LLM_JUDGE_WORKFLOW.md`
3. **Execute the full evaluation workflow** on module: `$ARGUMENTS`

### Execution Rules
- Execute ALL steps autonomously (Steps 1, 2, 3, 5)
- Do NOT stop to ask permission between steps
- Verify output after EVERY agent call before proceeding
- Only stop for Step 4 (Rubric Updates) which requires user approval
- Present FINAL results only

### Quick Reference - Agent Files
| Agent | File |
|-------|------|
| Evaluation Runner | `evaluation_KD/agents/01_evaluation_runner.md` |
| Prompt Analyzer | `evaluation_KD/agents/02_prompt_analyzer.md` |
| Rubric Validator | `evaluation_KD/agents/03_rubric_validator.md` |
| Validation Experimenter | `evaluation_KD/agents/04_validation_experimenter.md` |
| Suggestion Generator | `evaluation_KD/agents/05_suggestion_generator.md` |
| Dashboard Generator | `evaluation_KD/agents/06_dashboard_generator.md` |
| Rubric Updater | `evaluation_KD/agents/07_rubric_updater.md` |

Now read the orchestrator document and execute the workflow.
