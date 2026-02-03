# Universal Judge Prompt Template

Use this template to evaluate any module output. Replace placeholders with actual values.

---

## Template

```
You are an expert evaluator for keyword classification. Your task is to evaluate a module's output using a multi-dimensional rubric.

## MODULE INFORMATION
- **Module ID**: {{module_id}}
- **Module Name**: {{module_name}}
- **Purpose**: {{module_purpose}}

## RUBRIC DIMENSIONS

{{#each dimensions}}
### {{name}} (Weight: {{weight}})
- **1.0**: {{levels.1_0}}
- **0.5**: {{levels.0_5}}
- **0.0**: {{levels.0_0}}

{{/each}}

## INPUT DATA
The module received this input:
```json
{{input_data}}
```

## MODULE OUTPUT (Evaluate This)
The module produced this output:
```json
{{module_output}}
```

## EXPECTED OUTPUT (Ground Truth)
The correct output should be:
```json
{{expected_output}}
```

## YOUR TASK

1. **Score each dimension** using the rubric levels (1.0, 0.5, or 0.0)
2. **Provide a brief reason** for each score (1 sentence max)
3. **Calculate the weighted average** as the final score
4. **Identify failure category** if score < 0.7

## OUTPUT FORMAT

Return ONLY this JSON (no other text):
```json
{
  "dimension_scores": {
    "{{dimension_1}}": {"score": <1.0|0.5|0.0>, "reason": "<1 sentence>"},
    "{{dimension_2}}": {"score": <1.0|0.5|0.0>, "reason": "<1 sentence>"},
    ...
  },
  "final_score": <weighted average 0.0-1.0>,
  "passed": <true if final_score >= 0.7>,
  "failure_category": "<DATA_QUALITY|ENTITY_MISS|ENTITY_HALLUCINATION|CLASSIFICATION_ERROR|REASONING_FLAW|BOUNDARY_ERROR|null>",
  "summary": "<1 sentence overall assessment>"
}
```
```

---

## Example: M02 (Own Brand Classification)

```
You are an expert evaluator for keyword classification. Your task is to evaluate a module's output using a multi-dimensional rubric.

## MODULE INFORMATION
- **Module ID**: M02
- **Module Name**: Own Brand Classification
- **Purpose**: Determine if a keyword contains own brand terms (OB) or not (null)

## RUBRIC DIMENSIONS

### Classification Accuracy (Weight: 0.40)
- **1.0**: Correct OB/null matching ground truth
- **0.5**: Classification defensible but annotator disagreed
- **0.0**: Clear miss (obvious brand present but marked null, or vice versa)

### Evidence Quality (Weight: 0.30)
- **1.0**: matched_term cites exact term from variations list
- **0.5**: Claims match but term not in provided variations
- **0.0**: No matched_term, or cites non-existent term

### Reasoning (Weight: 0.20)
- **1.0**: Clear explanation: "keyword contains X which matches variation Y"
- **0.5**: Reasoning present but vague or incomplete
- **0.0**: No reasoning or contradicts classification

### Boundary Handling (Weight: 0.10)
- **1.0**: Correctly handles partial matches (e.g., "jbl" in "adjustable" = no match)
- **0.5**: Inconsistent on edge cases
- **0.0**: Fails basic boundary checks

## INPUT DATA
The module received this input:
```json
{
  "keyword": "jbl earbuds wireless",
  "variations_own": "JBL, jbl, J-B-L, Jbl",
  "related_terms_own": "Vibe Beam, Tune, Live Pro"
}
```

## MODULE OUTPUT (Evaluate This)
The module produced this output:
```json
{
  "branding_scope": "OB",
  "matched_term": "jbl",
  "match_type": "variation",
  "confidence": "high",
  "reasoning": "The keyword 'jbl earbuds wireless' contains 'jbl' which exactly matches the variation 'jbl' in the brand variations list."
}
```

## EXPECTED OUTPUT (Ground Truth)
The correct output should be:
```json
{
  "branding_scope": "OB",
  "matched_term": "jbl"
}
```

## YOUR TASK

1. **Score each dimension** using the rubric levels (1.0, 0.5, or 0.0)
2. **Provide a brief reason** for each score (1 sentence max)
3. **Calculate the weighted average** as the final score
4. **Identify failure category** if score < 0.7

## OUTPUT FORMAT

Return ONLY this JSON (no other text):
```json
{
  "dimension_scores": {
    "classification_accuracy": {"score": <1.0|0.5|0.0>, "reason": "<1 sentence>"},
    "evidence_quality": {"score": <1.0|0.5|0.0>, "reason": "<1 sentence>"},
    "reasoning": {"score": <1.0|0.5|0.0>, "reason": "<1 sentence>"},
    "boundary_handling": {"score": <1.0|0.5|0.0>, "reason": "<1 sentence>"}
  },
  "final_score": <weighted average 0.0-1.0>,
  "passed": <true if final_score >= 0.7>,
  "failure_category": "<DATA_QUALITY|ENTITY_MISS|ENTITY_HALLUCINATION|CLASSIFICATION_ERROR|REASONING_FLAW|BOUNDARY_ERROR|null>",
  "summary": "<1 sentence overall assessment>"
}
```
```

---

## Example: M09 (Primary Intended Use)

```
You are an expert evaluator for keyword classification. Your task is to evaluate a module's output using a multi-dimensional rubric.

## MODULE INFORMATION
- **Module ID**: M09
- **Module Name**: Identify Primary Intended Use
- **Purpose**: Determine the single core purpose of the product in 3-6 words

## RUBRIC DIMENSIONS

### Semantic Accuracy (Weight: 0.40)
- **1.0**: Captures THE one core purpose (e.g., "portable hydration" for water bottle)
- **0.5**: Correct direction but too broad/narrow
- **0.0**: Wrong purpose identified

### Conciseness (Weight: 0.30)
- **1.0**: 3-6 words, verb+noun structure, no adjectives
- **0.5**: Slightly over/under (2 or 7-8 words)
- **0.0**: Too long (>8 words) or too short (1 word)

### No Features (Weight: 0.20)
- **1.0**: No specs, technologies, adjectives, marketing language
- **0.5**: 1 minor feature/adjective included
- **0.0**: Contains marketing language, specs, or technologies

### Actionability (Weight: 0.10)
- **1.0**: Clear enough for M10 validation and M12 classification
- **0.5**: Somewhat ambiguous but usable
- **0.0**: Too vague to use downstream

## INPUT DATA
The module received this input:
```json
{
  "title": "JBL Vibe Beam True Wireless Earbuds",
  "bullets": "Deep bass sound, 8 hours battery, Touch controls, Voice assistant",
  "description": "Experience crystal-clear audio with JBL Pure Bass sound...",
  "taxonomy": [
    {"level": 1, "product_type": "True Wireless Earbuds"},
    {"level": 2, "product_type": "Wireless Earbuds"},
    {"level": 3, "product_type": "Earbuds"}
  ]
}
```

## MODULE OUTPUT (Evaluate This)
The module produced this output:
```json
{
  "primary_use": "personal audio listening"
}
```

## EXPECTED OUTPUT (Ground Truth)
The correct output should be:
```json
{
  "primary_use": "personal audio listening"
}
```

## YOUR TASK

1. **Score each dimension** using the rubric levels (1.0, 0.5, or 0.0)
2. **Provide a brief reason** for each score (1 sentence max)
3. **Calculate the weighted average** as the final score
4. **Identify failure category** if score < 0.7

## OUTPUT FORMAT

Return ONLY this JSON (no other text):
```json
{
  "dimension_scores": {
    "semantic_accuracy": {"score": <1.0|0.5|0.0>, "reason": "<1 sentence>"},
    "conciseness": {"score": <1.0|0.5|0.0>, "reason": "<1 sentence>"},
    "no_features": {"score": <1.0|0.5|0.0>, "reason": "<1 sentence>"},
    "actionability": {"score": <1.0|0.5|0.0>, "reason": "<1 sentence>"}
  },
  "final_score": <weighted average 0.0-1.0>,
  "passed": <true if final_score >= 0.7>,
  "failure_category": "<DATA_QUALITY|ENTITY_MISS|ENTITY_HALLUCINATION|CLASSIFICATION_ERROR|REASONING_FLAW|BOUNDARY_ERROR|null>",
  "summary": "<1 sentence overall assessment>"
}
```
```

---

## Example: M12 (R/S/C/N Classification)

```
You are an expert evaluator for keyword classification. Your task is to evaluate a module's output using a multi-dimensional rubric.

## MODULE INFORMATION
- **Module ID**: M12
- **Module Name**: Combined R/S/C/N Classification
- **Purpose**: Classify keyword relevance: R (Relevant), S (Substitute), C (Complementary), N (Negative)

## RUBRIC DIMENSIONS

### Classification Accuracy (Weight: 0.45)
- **1.0**: Correct R/S/C/N matching ground truth
- **0.5**: Defensible classification but annotator disagreed
- **0.0**: Clear misclassification

### Decision Path (Weight: 0.25)
- **1.0**: Follows correct sequence: constraints → type → use → complement
- **0.5**: Correct answer but wrong reasoning path
- **0.0**: Wrong path leading to wrong answer

### Evidence (Weight: 0.20)
- **1.0**: Cites specific constraints, types, or uses from upstream modules
- **0.5**: References upstream but vaguely
- **0.0**: No connection to upstream data

### Confidence Calibration (Weight: 0.10)
- **1.0**: High confidence on clear cases, low on edge cases
- **0.5**: Mostly calibrated
- **0.0**: Overconfident on wrong answers

## DECISION TREE REFERENCE
```
1. Hard constraint violated? → YES → N
2. Same product type?
   → YES + Same primary use → R
   → YES + Different use → N
   → NO + Same primary use → S
   → NO + Different use → Used together? → YES → C, NO → N
```

## INPUT DATA
The module received this input:
```json
{
  "keyword": "wireless earbuds",
  "validated_use": "personal audio listening",
  "taxonomy": [
    {"level": 1, "product_type": "True Wireless Earbuds"},
    {"level": 2, "product_type": "Wireless Earbuds"}
  ],
  "hard_constraints": [
    {"attribute": "Wireless", "value": "Bluetooth", "reason": "core function"}
  ]
}
```

## MODULE OUTPUT (Evaluate This)
The module produced this output:
```json
{
  "classification": "R",
  "reasoning": "Same product type (wireless earbuds matches taxonomy level 2), same primary use (audio listening), no constraint violation.",
  "confidence": "high",
  "decision_path": "Step 1: No constraint violation → Step 2: Same type (YES) → Step 3a: Same use (YES) → R"
}
```

## EXPECTED OUTPUT (Ground Truth)
The correct output should be:
```json
{
  "classification": "R"
}
```

## YOUR TASK

1. **Score each dimension** using the rubric levels (1.0, 0.5, or 0.0)
2. **Provide a brief reason** for each score (1 sentence max)
3. **Calculate the weighted average** as the final score
4. **Identify failure category** if score < 0.7

## OUTPUT FORMAT

Return ONLY this JSON (no other text):
```json
{
  "dimension_scores": {
    "classification_accuracy": {"score": <1.0|0.5|0.0>, "reason": "<1 sentence>"},
    "decision_path": {"score": <1.0|0.5|0.0>, "reason": "<1 sentence>"},
    "evidence": {"score": <1.0|0.5|0.0>, "reason": "<1 sentence>"},
    "confidence_calibration": {"score": <1.0|0.5|0.0>, "reason": "<1 sentence>"}
  },
  "final_score": <weighted average 0.0-1.0>,
  "passed": <true if final_score >= 0.7>,
  "failure_category": "<DATA_QUALITY|ENTITY_MISS|ENTITY_HALLUCINATION|CLASSIFICATION_ERROR|REASONING_FLAW|BOUNDARY_ERROR|null>",
  "summary": "<1 sentence overall assessment>"
}
```
```
