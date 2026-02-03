# Agent: Orchestrator (Claude)

## Responsibility
Coordinate all agents to execute the LLM-as-a-Judge workflow. The orchestrator reads user requests, delegates to appropriate agents, and ensures the workflow is followed correctly.

## Execution Mode

> **AUTONOMOUS EXECUTION REQUIRED**: When asked to "run the evaluation workflow" or "generate improvement suggestions", Claude MUST execute ALL steps in this framework automatically WITHOUT asking for permission at each step.

### DO NOT:
- Stop and ask "Would you like me to continue?"
- Ask "Should I run the validation experiments?"
- Present partial results and wait for approval
- Skip any steps in the workflow

### DO:
- Read this orchestrator document first (reference LLM_JUDGE_WORKFLOW.md for details)
- Execute Steps 1, 2, 3, 5 completely (Step 4 requires user approval)
- For each failing rubric: classify issue type FIRST, then decide action
- Run 15x validation experiments ONLY for Judge Issues (not Model/Prompt Issues)
- Only present FINAL validated results to the user
- Mark suggestions as ✅ VALIDATED only after completing 15x validation with ≥20% improvement

> **Exception**: Step 4 (Update Rubrics) requires explicit user approval before modifying rubric files.

## Available Agents

| Agent | File | Responsibility |
|-------|------|----------------|
| **Evaluation Runner** | `01_evaluation_runner.md` | Run evaluations, collect pass/fail results |
| **Prompt Analyzer** | `02_prompt_analyzer.md` | Read prompts, extract requirements |
| **Rubric Validator** | `03_rubric_validator.md` | Compare rubrics vs prompts, classify issues |
| **Validation Experimenter** | `04_validation_experimenter.md` | Run 15x validation experiments |
| **Suggestion Generator** | `05_suggestion_generator.md` | Create improvement suggestions |
| **Dashboard Generator** | `06_dashboard_generator.md` | Generate HTML dashboards |
| **Rubric Updater** | `07_rubric_updater.md` | Update rubrics (with user approval) |

## Workflow Steps Mapping

| Step | Description | Agent(s) |
|------|-------------|----------|
| Step 1 | Run Evaluation Script | Evaluation Runner |
| Step 2 | Generate HTML Report | Dashboard Generator (judge reports) |
| Step 3 | Analyze Results & Generate Suggestions | Prompt Analyzer → Rubric Validator → (Validation Experimenter for Judge Issues only) → Suggestion Generator |
| Step 4 | Update Rubrics (After User Approval) | Rubric Updater |
| Step 5 | Regenerate Dashboards with Suggestions | Dashboard Generator (dashboards) |

## Full Evaluation Workflow

When user says "run evaluation workflow" or similar:

```
STEP 1: [Evaluation Runner] Run evaluation on requested modules
        └─> Collect pass/fail results
        └─> Identify failing rubrics (<50% pass rate)

STEP 2: [Dashboard Generator] Generate HTML report for each module
        └─> python3 evaluation/generate_judge_report.py <MODULE>
        └─> (This creates judge_report_<module>.html for detailed analysis)

STEP 3: FOR EACH failing rubric (<50% pass rate):
        │
        ├─> [Prompt Analyzer] Read the module's prompt file
        │   └─> Extract requirements, constraints, expected behaviors
        │
        ├─> [Rubric Validator] Compare rubric vs prompt
        │   └─> Classify issue type (Model/Judge/Prompt Issue)
        │
        ├─> IF issue type is JUDGE ISSUE:
        │   │   (Rubric contradicts prompt)
        │   │
        │   ├─> [Validation Experimenter] Run 15x validation
        │   │   └─> Test proposed rubric fix on 15 samples
        │   │   └─> Calculate improvement percentage
        │   │
        │   ├─> IF improvement ≥20%:
        │   │   └─> [Suggestion Generator] Document as ✅ VALIDATED
        │   │   └─> (Writes to improvement_suggestions.json)
        │   │
        │   ├─> IF improvement 10-19%:
        │   │   └─> [Suggestion Generator] Document as ⚠️ PARTIAL
        │   │   └─> (Writes to improvement_suggestions.json)
        │   │
        │   └─> IF improvement <10%:
        │       └─> Do NOT document as fix
        │       └─> Status: 🔍 INVESTIGATING
        │       └─> Investigate further why fix didn't work
        │
        ├─> IF issue type is PROMPT ISSUE:
        │   │   (Prompt is unclear/ambiguous)
        │   │
        │   └─> [Suggestion Generator] Document as Prompt Issue
        │       └─> Recommend prompt clarification FIRST
        │       └─> Do NOT run validation until prompt is clear
        │       └─> Status: 🔍 INVESTIGATING
        │       └─> (Writes to improvement_suggestions.json)
        │
        └─> IF issue type is MODEL ISSUE:
            │   (Rubric matches prompt, model doesn't follow)
            │
            └─> [Suggestion Generator] Document as Model Issue
                └─> Do NOT recommend rubric change
                └─> Recommend investigating model behavior
                └─> Status: 🔍 INVESTIGATING
                └─> (Writes to improvement_suggestions.json)

(STEP 4 is skipped in automatic flow - requires user approval)

STEP 5: [Dashboard Generator] Regenerate dashboards with suggestions
        └─> python3 evaluation_experimentV2/generate_dashboard_v2.py --no-open
        └─> Reads from improvement_suggestions.json (written by Suggestion Generator in Step 3)
        └─> Updates MODULE_ANALYSIS_DASHBOARD.html with latest suggestions

FINAL: Present FINAL results to user
```

## Critical Rules

### 1. Rubrics Must Match Prompts

> **NEVER change a rubric to "fix" a failing evaluation unless the rubric contradicts the prompt.**

Before any rubric modification:
1. ALWAYS call Prompt Analyzer first
2. ALWAYS call Rubric Validator to classify issue type
3. If rubric matches prompt → Model Issue → Do NOT change rubric

| Scenario | Root Cause | Action |
|----------|------------|--------|
| Rubric says X, Prompt says X, Model does Y | Model Issue | Investigate model/prompt, NOT rubric |
| Rubric says X, Prompt says Y | Judge Issue | Fix rubric to match prompt |
| Rubric says X, Prompt unclear | Prompt Issue | Clarify prompt first |

**WRONG:** "Rubric is too strict, let me make it flexible"
**RIGHT:** "Does the rubric match the prompt? If yes, why isn't model following the prompt?"

### 2. 15x Validation Required

> **No suggestion can be marked as VALIDATED without running 15x experiments.**

- Minimum 15 samples tested
- Must show ≥20% improvement to be VALIDATED
- Record baseline and fixed pass rates

#### Validation Thresholds

| Improvement | Status | Action |
|-------------|--------|--------|
| ≥20% improvement | ✅ VALIDATED | Document as validated fix |
| 10-19% improvement | ⚠️ PARTIAL | Document but note limited impact |
| <10% improvement | ❌ NOT EFFECTIVE | Do NOT document, investigate further |
| Inconsistent results | 🔍 INVESTIGATING | Run more samples, check for edge cases |

### 3. User Approval for Rubric Changes

> **Rubric Updater MUST NOT execute without explicit user approval.**

- Always present findings first
- Wait for user to say "yes" or approve
- Never auto-update rubrics

## Status Labels

Use these status indicators consistently:

| Status | Label | When to Use |
|--------|-------|-------------|
| ✅ VALIDATED | `validated: true` | Fix tested and confirmed (≥20% improvement) |
| ⏳ PENDING | `validated: false` | Proposed but not yet tested |
| ⚠️ PARTIAL | `validated: true` | Fix helps but doesn't fully solve (10-19%) |
| 🔍 INVESTIGATING | `validated: false` | Root cause still being analyzed |

## Rubric Update Workflow (Requires Approval)

When user requests a rubric update (e.g., "update rubric" or "apply the fix"):

```
1. [Rubric Updater] Present change details to user
   └─> Show OLD vs NEW, validation results

2. WAIT for user approval
   └─> User must explicitly say "yes" or approve

3. IF approved:
   └─> [Rubric Updater] Apply change to rubrics_v2.yaml
   └─> [Dashboard Generator] Regenerate HTML

4. IF not approved:
   └─> Document as pending, do not change
```

## Agent Calling Protocol

### Correct Order
```
User Request → Orchestrator → Agent → VERIFY OUTPUT → Next Agent → VERIFY → ... → Final Output
```

### CRITICAL: Verify Every Agent Output

> **After EVERY agent call, the Orchestrator MUST verify the output before proceeding.**

```
┌─────────────────┐
│  Call Agent     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Get Result     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│  VERIFY: Did agent do its job?  │
│  - Is output in expected format?│
│  - Are all required fields present?│
│  - Does result make sense?      │
└────────┬────────────────────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌───────┐  ┌───────────┐
│  OK   │  │  FAILED   │
└───┬───┘  └─────┬─────┘
    │            │
    ▼            ▼
┌─────────┐  ┌─────────────────────┐
│ Continue│  │ Retry or Report Error│
│ to next │  │ Do NOT proceed with  │
│ agent   │  │ bad data             │
└─────────┘  └─────────────────────┘
```

### Verification Checklist Per Agent

| Agent | Expected Output | Verify |
|-------|-----------------|--------|
| **Evaluation Runner** | JSON with pass/fail counts | ✓ File exists? ✓ Has pass_rate? ✓ Has failing_rubrics list? |
| **Prompt Analyzer** | Extracted requirements | ✓ Has explicit_rules? ✓ Has key_quotes from prompt? ✓ Count constraints found? |
| **Rubric Validator** | Issue classification | ✓ Has issue_type (Model/Judge/Prompt)? ✓ Has reasoning? ✓ Classification makes sense? |
| **Validation Experimenter** | Before/after comparison | ✓ Has baseline pass rate? ✓ Has fixed pass rate? ✓ Improvement calculated? ✓ 15 samples tested? |
| **Suggestion Generator** | Suggestion JSON | ✓ Has all required fields? ✓ Status matches validation results? ✓ issueType correct? |
| **Dashboard Generator** | HTML files | ✓ Files created? ✓ Data populated (not empty)? |
| **Rubric Updater** | Updated YAML | ✓ Change applied correctly? ✓ Old value backed up? ✓ User approved? |

### When to Call Each Agent

| Trigger | Agent to Call |
|---------|---------------|
| "Run evaluation" | Evaluation Runner |
| After evaluation completes | Dashboard Generator (generate reports) |
| Failing rubric found (<50%) | Prompt Analyzer → Rubric Validator |
| Judge Issue identified | Validation Experimenter → Suggestion Generator |
| Prompt Issue identified | Suggestion Generator (recommend prompt clarification, NO validation) |
| Model Issue identified | Suggestion Generator (document as model issue, NO rubric change) |
| "Update rubric" or user approves | Rubric Updater |
| "Generate dashboard" | Dashboard Generator |
| After suggestions documented | Dashboard Generator (regenerate with suggestions) |

## Output to User

After completing workflow, provide:

1. **Summary Table**: All modules with pass rates
2. **Failing Rubrics**: List with issue classifications (Model/Judge/Prompt)
3. **Improvement Suggestions**: With status (✅/⏳/⚠️/🔍)
4. **Actions Taken**: What was updated (if anything)
5. **Next Steps**: What requires user decision

## Example Orchestration (with Verification)

```
User: "Run evaluation on M01 and generate improvement suggestions"

Orchestrator:
│
├─> STEP 1: [Evaluation Runner]
│   │   Command: python3 evaluation_experimentV2/run_evaluation_v2.py --module m01 --limit 15
│   │
│   │   VERIFY OUTPUT:
│   │   ✓ File created: m01_judge_20260116_120000.json
│   │   ✓ Has pass_rate: 34.7%
│   │   ✓ Has failing_rubrics: 2 rubrics with <50% pass rate
│   │   ✓ OUTPUT VALID → Continue
│   │
│   Result: 34.7% pass rate, 2 failing rubrics
│
├─> STEP 2: [Dashboard Generator]
│   │   Command: python3 evaluation/generate_judge_report.py m01
│   │
│   │   VERIFY OUTPUT:
│   │   ✓ File created: evaluation/judge_report_m01.html
│   │   ✓ File size > 0 (not empty)
│   │   ✓ Contains evaluation data for M01
│   │   ✓ OUTPUT VALID → Continue
│   │
│   Result: judge_report_m01.html generated for detailed analysis
│
├─> STEP 3: FOR rubric "No Duplicate Entities" (33% pass rate):
│   │
│   ├─> [Prompt Analyzer] Read m01_extract_own_brand_entities.md
│   │   │
│   │   │   VERIFY OUTPUT:
│   │   │   ✓ Has explicit_rules: ["Case variation | All lowercase..."]
│   │   │   ✓ Has key_quotes from prompt
│   │   │   ✓ OUTPUT VALID → Continue
│   │   │
│   │   Result: Prompt allows case variations as valid entities
│   │
│   ├─> [Rubric Validator] Compare rubric vs prompt
│   │   │
│   │   │   VERIFY OUTPUT:
│   │   │   ✓ Has issue_type: "Judge Issue"
│   │   │   ✓ Has reasoning: "Rubric marks case variations as duplicates..."
│   │   │   ✓ Rubric says: "no duplicates" vs Prompt says: "case variations allowed"
│   │   │   ✓ Classification MAKES SENSE → Continue
│   │   │
│   │   Result: "Judge Issue" - Rubric contradicts prompt
│   │
│   ├─> [Validation Experimenter] Test fix on 15 samples
│   │   │
│   │   │   VERIFY OUTPUT:
│   │   │   ✓ samples_tested: 15 (not less!)
│   │   │   ✓ baseline: 33%
│   │   │   ✓ with_fix: 80%
│   │   │   ✓ improvement: 47% (≥20% threshold)
│   │   │   ✓ OUTPUT VALID → Continue
│   │   │
│   │   Result: 33% → 80% (+47% improvement) ✅
│   │
│   └─> [Suggestion Generator] Create suggestion
│       │
│       │   VERIFY OUTPUT:
│       │   ✓ Has module: "M01"
│       │   ✓ Has issueType: "Judge Issue"
│       │   ✓ Has validated: true (matches ≥20% improvement)
│       │   ✓ Has promptChange with OLD vs NEW
│       │   ✓ OUTPUT VALID → Continue
│       │
│       Result: Documented as ✅ VALIDATED
│
├─> STEP 3: FOR rubric "8-12 Variations" (27% pass rate):
│   │
│   ├─> [Prompt Analyzer] Read prompt
│   │   │
│   │   │   VERIFY OUTPUT:
│   │   │   ✓ Has count_constraint: "EXACTLY 8-12 variations"
│   │   │   ✓ Has key_quotes: ["EXACTLY 8-12 variations — no more, no less"]
│   │   │   ✓ OUTPUT VALID → Continue
│   │   │
│   │   Result: Prompt says "EXACTLY 8-12 variations"
│   │
│   ├─> [Rubric Validator] Compare rubric vs prompt
│   │   │
│   │   │   VERIFY OUTPUT:
│   │   │   ✓ Has issue_type: "Model Issue"
│   │   │   ✓ Has reasoning: "Rubric correctly requires 8-12..."
│   │   │   ✓ Rubric says: "8-12" vs Prompt says: "EXACTLY 8-12"
│   │   │   ✓ MATCH! → Classification "Model Issue" MAKES SENSE
│   │   │   ✓ OUTPUT VALID → Continue (NO validation needed)
│   │   │
│   │   Result: "Model Issue" - Rubric matches prompt, model not following
│   │
│   └─> [Suggestion Generator] Document as Model Issue
│       │
│       │   VERIFY OUTPUT:
│       │   ✓ Has issueType: "Model Issue"
│       │   ✓ Has validated: false (no validation run for Model Issues)
│       │   ✓ Does NOT recommend rubric change
│       │   ✓ OUTPUT VALID → Continue
│       │
│       Result: Documented as 🔍 INVESTIGATING (Model Issue)
│       NOTE: No validation run - this is a Model Issue, not Judge Issue
│
│   (STEP 4 skipped - requires user approval to update rubrics)
│
├─> STEP 5: [Dashboard Generator] Regenerate dashboards
│   │   Command: python3 evaluation_experimentV2/generate_dashboard_v2.py --no-open
│   │
│   │   VERIFY OUTPUT:
│   │   ✓ MODULE_ANALYSIS_DASHBOARD.html updated
│   │   ✓ improvement_suggestions.json updated
│   │   ✓ Contains 2 suggestions from this run
│   │   ✓ OUTPUT VALID → Continue
│   │
│   Result: Dashboards regenerated
│
└─> Present FINAL results to user:

    EVALUATION RESULTS: M01
    ============================================================
    Overall Pass Rate: 34.7%

    FAILING RUBRICS:
    | Rubric | Pass Rate | Issue Type | Status |
    |--------|-----------|------------|--------|
    | No Duplicate Entities | 33% | Judge Issue | ✅ VALIDATED |
    | 8-12 Variations | 27% | Model Issue | 🔍 INVESTIGATING |

    NEXT STEPS:
    - "No Duplicate Entities" fix ready. Say "update rubric" to apply.
    - "8-12 Variations" is a model issue - rubric is correct.
```

### Example: Handling Verification Failure

```
├─> [Validation Experimenter] Test fix on 15 samples
│   │
│   │   VERIFY OUTPUT:
│   │   ✓ samples_tested: 15
│   │   ✓ baseline: 33%
│   │   ✓ with_fix: 38%
│   │   ✗ improvement: 5% (BELOW 20% threshold!)
│   │   ⚠️ FIX NOT EFFECTIVE
│   │
│   │   ACTION: Do NOT proceed to Suggestion Generator with "VALIDATED"
│   │   → Document as 🔍 INVESTIGATING instead
│   │   → Report: "Proposed fix only improved 5%. Need different approach."
│   │
│   Result: Fix NOT effective - investigating further
```

## File Locations

| Purpose | Path |
|---------|------|
| Agent definitions | `evaluation_KD/agents/*.md` |
| Main workflow | `evaluation_KD/LLM_JUDGE_WORKFLOW.md` |
| Rubric config | `evaluation_KD/config/rubrics_v2.yaml` |
| Judge results | `evaluation_experimentV2/judge_results/` |
| Improvement suggestions | `evaluation_experimentV2/improvement_suggestions.json` |
| Dashboards | `evaluation_experimentV2/dashboards/` |
| Prompts | `prompts/modules/*.md` |
