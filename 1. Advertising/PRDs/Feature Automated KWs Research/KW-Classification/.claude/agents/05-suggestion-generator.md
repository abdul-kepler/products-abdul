---
name: suggestion-generator
description: Create improvement suggestions and write them to improvement_suggestions.json. Documents validated fixes with status labels. Called after Rubric Validator classifies issue type.
tools: Read, Write, Edit, Glob
model: inherit
---

# Agent: Suggestion Generator

## Responsibility
Create detailed, actionable improvement suggestions for failing rubrics based on investigation results and validation experiments.

## When Called
- Step 5.5, 5.6, 5.7 of the workflow
- After Rubric Validator has classified the issue type
- After Validation Experimenter has run experiments (if applicable)

## Required Inputs
- Failing rubric details (name, pass rate, module)
- Issue classification from Rubric Validator (Model Issue / Judge Issue / Prompt Issue)
- Validation experiment results (if any)
- Prompt analysis from Prompt Analyzer

## Criticality Classification

| Pass Rate | Criticality | Priority |
|-----------|-------------|----------|
| <20% | Critical | Investigate immediately |
| 20-35% | High | High priority |
| 35-50% | Medium | Address after critical/high |
| >50% | Low | Monitor, not urgent |

## Issue Type Classification (CRITICAL)

**You MUST correctly classify the root cause:**

| Issue Type | Definition | Solution | Examples |
|------------|------------|----------|----------|
| **Model Issue** | LLM capability limitation - model CAN'T do task even with clear instructions | Change model or fine-tune | Hallucinating facts, can't do complex math, context length limits |
| **Prompt Issue** | Prompt logic unclear/missing - model WOULD do task if instructions were clearer | Revise prompt instructions | Missing verification steps, unclear criteria, ambiguous rules |
| **Judge Issue** | Rubric/evaluation criteria incorrect | Fix rubric definition | Rubric too strict, wrong pass/fail conditions |
| **Improved** | Was failing, now fixed | No action needed | Previous version issues resolved |
| **Mixed** | Multiple root causes | Address each separately | Both prompt unclear AND rubric wrong |

### How to Differentiate Model vs Prompt Issue:

**Ask: "If I made the prompt instructions crystal clear, would the model succeed?"**

- **YES → Prompt Issue** (model capable, instructions unclear)
- **NO → Model Issue** (model fundamentally can't do it)

**Examples:**

❌ **Prompt Issue** (NOT Model Issue):
- "Model verified keyword against itself instead of brand entities" → Prompt didn't clearly specify WHAT to verify against
- "Model included product words in brand list" → Prompt's Amazon Test instructions not explicit enough
- "Model didn't do character-by-character check" → Prompt didn't include this step

✅ **Model Issue** (true capability limitation):
- Model consistently hallucinates brand names that don't exist in input (even with explicit "only use input text" instruction)
- Model can't maintain consistency across long context
- Model makes same error regardless of how instructions are phrased

## Status Labels

| Status | Label | When to Use |
|--------|-------|-------------|
| ✅ VALIDATED | `validated: true` | Fix tested and confirmed (≥20% improvement) |
| ⏳ PENDING | `validated: false` | Proposed but not yet tested |
| ⚠️ PARTIAL | `validated: true` | Fix helps but doesn't fully solve (10-19%) |
| 🔍 INVESTIGATING | `validated: false` | Root cause still being analyzed |

## Output File Location

> **MANDATORY**: Create the file in the CURRENT EXPERIMENT folder:
> ```
> evaluation_KD/evaluation_experimentVX/improvement_suggestions.json
> ```
>
> Replace `VX` with the current experiment number (V3, V4, etc.)

## Output Format

Generate suggestions JSON with this structure:

```json
{
  "module": "M01",
  "rubric": "No Duplicate Entities",
  "criticality": "Critical",
  "passRate": 33,
  "issueType": "Judge Issue",
  "analysisSummary": "✅ VALIDATED - Rubric fixed to allow case variations",
  "specificIssue": "Original rubric treated case variations (ZKX + zkx) as duplicates. Fixed rubric only fails on EXACT string duplicates.",
  "expectedOutput": "[\"ZKX\", \"zkx\", \"JLB\", \"SonicPulse\"]",
  "actualOutput": "[\"ZKX\", \"zkx\", \"ZKX Deep Bass\", \"SonicPulse\", ...]",
  "detailedSuggestion": "FIXED: Updated rubric to only fail on EXACT string duplicates. Case variations (ZKX vs zkx) are now allowed as intentional brand entity variants.",
  "promptChange": "<HTML formatted change description with experiment results>",
  "impact": "✅ VALIDATED: Rubric now aligns with prompt behavior",
  "validated": true,
  "experimentDate": "2026-01-16",
  "experimentModel": "gpt-4o-mini",
  "samplesTested": 15,
  "testResults": "Rubric fixed - now allows case variations as intended by prompt"
}
```

## Prompt Change Documentation Format

When documenting prompt changes, include:

### 1. Experiment Results Box (if validated)
```html
<div style="background:#d4edda;color:#333;padding:10px;border-radius:5px;margin-bottom:10px;border:1px solid #28a745;">
  <span style="color:#155724;font-weight:bold;">✅ EXPERIMENT RESULTS</span>
  <br>• Model: gpt-4o-mini
  <br>• Samples tested: 15
  <br>• Original: 5/15 passed (33%)
  <br>• With fix: 12/15 passed (80%)
  <br>• Improvement: +47%
</div>
```

### 2. Action Location
```html
<strong style="color:#28a745;">📍 APPLIED TO: rubrics_v2.yaml</strong>
<hr>
<strong>Rubric changes:</strong>
```

### 3. Specific Changes (OLD vs NEW)
```html
<pre style="background:#f5f5f5;color:#333;padding:10px;border-radius:5px;font-size:11px;">
OLD fail_definition:
  - Case-insensitive duplicates (ZKX and zkx)

NEW fail_definition:
  - EXACT same string appears more than once
  - NOTE: Case variations are ALLOWED
</pre>
```

## Format for Model Issues (from prompt-improver)

When documenting Model Issue improvements from `prompt-improver`, include iteration data:

```json
{
  "module": "M01",
  "rubric": "Amazon Test Applied",
  "criticality": "Critical",
  "passRate": 7,
  "issueType": "Model Issue",
  "analysisSummary": "✅ VALIDATED - Prompt rule improved through 15 iterations",
  "specificIssue": "Model was not correctly applying the Amazon Test - including generic terms that would return multiple product categories",
  "detailedSuggestion": "VALIDATED: Improved Amazon Test rule with explicit decision tree format",
  "promptChange": "<HTML with iteration results + OLD vs NEW prompt text>",
  "impact": "✅ VALIDATED: 7% → 67% (+60% improvement)",
  "validated": true,
  "experimentDate": "2026-01-16",
  "experimentModel": "gpt-4o",
  "iterationData": {
    "totalIterations": 15,
    "bestIteration": 8,
    "progression": [7, 13, 27, 33, 40, 47, 53, 67, 60, 60, 67, 67, 67, 67, 67],
    "baselinePassRate": 7,
    "bestPassRate": 67
  },
  "promptFile": "prompts/modules/m01_extract_own_brand_entities.md",
  "oldPromptText": "Apply the Amazon Test to each entity",
  "newPromptText": "## Amazon Test Decision Tree\n\n1. Search the entity on Amazon\n2. FAIL if: results show different product categories..."
}
```

### Iteration Results Box (for Model Issues)
```html
<div style="background:#d4edda;color:#333;padding:10px;border-radius:5px;margin-bottom:10px;border:1px solid #28a745;">
  <span style="color:#155724;font-weight:bold;">✅ PROMPT IMPROVEMENT RESULTS (15 iterations)</span>
  <br>• Model: gpt-4o
  <br>• Iterations: 15
  <br>• Best iteration: #8
  <br>• Baseline: 7% → Best: 67%
  <br>• Improvement: +60%
  <br>• Progression: 7→13→27→33→40→47→53→<strong>67</strong>→60→60→67→67→67→67→67
</div>
```

## Rules
1. ALWAYS include issue classification (Model/Judge/Prompt Issue)
2. **ALWAYS include `expectedOutput` and `actualOutput`** - Dashboard requires these fields
3. **CRITICAL: Use REAL samples from evaluation data** - Read judge results JSON files to get actual failures
4. Include validation status clearly (✅/⏳/⚠️/🔍)
5. For **Model Issues**: Include iteration data from `prompt-improver`, show OLD vs NEW prompt text
6. For **Judge Issues**: Show OLD vs NEW rubric criteria from `validation-experimenter`
7. For Prompt Issues: Suggest prompt clarification first
8. Include experiment results when validated
9. For Model Issues, do NOT recommend rubric changes - only prompt improvements

## MANDATORY: Getting Real Samples

**NEVER use placeholder/synthetic data.** Always read from evaluation results:

```bash
# Find latest judge results for a module
ls -t evaluation_KD/evaluation_experimentV4/judge_results/m01_*.json | head -1

# Extract real failures
cat <judge_results_file>.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
for e in data.get('evaluations', []):
    if e.get('verdict') == 'FAIL':
        print('Sample:', e.get('sample_id'))
        print('Rubric:', e.get('criterion'))
        print('Expected:', json.dumps(e.get('expected')))
        print('Actual:', json.dumps(e.get('output')))
        print('---')
"
```

### Required fields from real data:
- `expectedOutput`: From `expected` field in judge results
- `actualOutput`: From `output` field in judge results
- Include actual brand names (JBL, Owala, Pioneer Camp, etc.)
- Include actual keywords and inputs from test data

## Dashboard Display Rules

When suggestions are displayed on MODULE_ANALYSIS_DASHBOARD:

1. **Analysis Summary matches Donut Chart**: The Analysis Summary column must show the exact same text as the donut category (e.g., "FAIL - amazon test applied (5)")

2. **No Truncation**: All text fields (specificIssue, expectedOutput, actualOutput) must be full text - no character limits

3. **Issue Type from suggestions**: The Issue Type column uses the `issueType` field from this file

4. **Specific Issue from suggestions**: The Specific Issue column uses the `specificIssue` field from this file

5. **One row per rubric**: Each donut chart category has exactly one matching row in the Analysis Details table
