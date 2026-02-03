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

## Status Labels

| Status | Label | When to Use |
|--------|-------|-------------|
| ✅ VALIDATED | `validated: true` | Fix tested and confirmed (≥20% improvement) |
| ⏳ PENDING | `validated: false` | Proposed but not yet tested |
| ⚠️ PARTIAL | `validated: true` | Fix helps but doesn't fully solve (10-19%) |
| 🔍 INVESTIGATING | `validated: false` | Root cause still being analyzed |

## Output Format

Generate suggestions for `evaluation_experimentV2/improvement_suggestions.json`:

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

## Rules
1. ALWAYS include issue classification (Model/Judge/Prompt Issue)
2. Use synthetic brand names in examples (ZKX, SonicPulse, HydroFlux) - NEVER real brands
3. Include validation status clearly (✅/⏳/⚠️/🔍)
4. For Model Issues, do NOT recommend rubric changes
5. For Judge Issues, show OLD vs NEW rubric criteria
6. For Prompt Issues, suggest prompt clarification first
7. Include experiment results when validated
