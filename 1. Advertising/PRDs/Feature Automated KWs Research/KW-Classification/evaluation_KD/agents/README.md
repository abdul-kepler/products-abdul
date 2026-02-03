# LLM-as-a-Judge Evaluation Agents

This directory contains agent definitions for the LLM-as-a-Judge evaluation workflow.

## Document Structure

| Document | Purpose |
|----------|---------|
| `../LLM_JUDGE_WORKFLOW.md` | **Reference** - Full workflow details, steps, commands, rules |
| `00_orchestrator.md` | **Execution** - How Claude should run the workflow |
| `01-07_*.md` | **Agent definitions** - What each agent does |

## How It Works

1. **Claude reads `00_orchestrator.md`** for execution instructions
2. **Orchestrator coordinates agents** following the workflow
3. **Each agent has a specific job** defined in its file
4. **After each agent runs**, orchestrator verifies the output
5. **Reference `LLM_JUDGE_WORKFLOW.md`** for technical details

## Agent Overview

| # | Agent | File | Responsibility |
|---|-------|------|----------------|
| 0 | **Orchestrator** | `00_orchestrator.md` | Coordinate all agents, execute workflow |
| 1 | **Evaluation Runner** | `01_evaluation_runner.md` | Run evaluations, collect pass/fail results |
| 2 | **Prompt Analyzer** | `02_prompt_analyzer.md` | Read prompts, extract requirements |
| 3 | **Rubric Validator** | `03_rubric_validator.md` | Compare rubrics vs prompts, classify issues |
| 4 | **Validation Experimenter** | `04_validation_experimenter.md` | Run 15x validation experiments |
| 5 | **Suggestion Generator** | `05_suggestion_generator.md` | Create improvement suggestions |
| 6 | **Dashboard Generator** | `06_dashboard_generator.md` | Generate HTML dashboards |
| 7 | **Rubric Updater** | `07_rubric_updater.md` | Update rubrics (with user approval) |

## Workflow Sequence

```
┌─────────────────┐
│  User Request   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Orchestrator   │ ◄─── Coordinates all agents
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Evaluation      │ ◄─── Step 1: Run evaluations
│ Runner          │      Output: Pass/fail results
└────────┬────────┘
         │
         ▼ (for each failing rubric <50%)
         │
┌─────────────────┐
│ Prompt          │ ◄─── Step 3.2: Read prompt
│ Analyzer        │      Output: Requirements, rules
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Rubric          │ ◄─── Step 3.3: Compare rubric vs prompt
│ Validator       │      Output: Issue classification
└────────┬────────┘
         │
         ├──── Model Issue ──── ► Document (no rubric change)
         │
         ├──── Prompt Issue ─── ► Suggest prompt clarification
         │
         └──── Judge Issue ──┐
                             │
                             ▼
                  ┌─────────────────┐
                  │ Validation      │ ◄─── Step 5.4: 15x validation
                  │ Experimenter    │      Output: Test results
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ Suggestion      │ ◄─── Step 5.5-5.7: Document
                  │ Generator       │      Output: JSON suggestion
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ Rubric          │ ◄─── Step 4: Update (with approval)
                  │ Updater         │      Requires: User approval
                  └────────┬────────┘
                           │
                           ▼
┌─────────────────┐
│ Dashboard       │ ◄─── Step 2, 5.8: Generate dashboards
│ Generator       │      Output: HTML files
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Final Results   │
│ to User         │
└─────────────────┘
```

## Critical Rules

### 1. Rubrics Must Match Prompts
> NEVER change a rubric unless it contradicts the prompt.

- If rubric matches prompt but model fails → **Model Issue** (don't change rubric)
- If rubric contradicts prompt → **Judge Issue** (fix rubric to match prompt)
- If prompt is unclear → **Prompt Issue** (clarify prompt first)

### 2. 15x Validation Required
> No suggestion marked as VALIDATED without 15 sample tests.

- Minimum 15 samples
- Must show ≥20% improvement
- Record baseline and fixed pass rates

### 3. User Approval for Rubric Changes
> Rubric Updater requires explicit user approval.

- Present changes clearly
- Wait for "yes" or approval
- Never auto-update rubrics

## How to Use

### Run Full Workflow
Tell Claude: "Run evaluation workflow on M01"

Claude will:
1. Execute Evaluation Runner
2. Analyze failing rubrics with Prompt Analyzer + Rubric Validator
3. Run validation experiments
4. Generate improvement suggestions
5. Regenerate dashboards
6. Present results

### Update a Rubric
After reviewing suggestions, tell Claude: "Update the M01_no_duplicates rubric"

Claude will:
1. Present the proposed change
2. Wait for your approval
3. Apply the change only after you say "yes"
4. Regenerate dashboards

## File Locations

| Resource | Path |
|----------|------|
| Agent definitions | `evaluation_KD/agents/*.md` |
| Main workflow | `evaluation_KD/LLM_JUDGE_WORKFLOW.md` |
| Rubric config | `evaluation_KD/config/rubrics_v2.yaml` |
| Prompts | `prompts/modules/*.md` |
| Judge results | `evaluation_experimentV2/judge_results/` |
| Suggestions | `evaluation_experimentV2/improvement_suggestions.json` |
| Dashboards | `evaluation_experimentV2/dashboards/` |
