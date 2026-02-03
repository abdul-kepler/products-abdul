# M11 Multi-Agent Evaluation Plan
## Identify Hard Constraints Module

**Version:** 1.0
**Created:** 2026-01-26
**Target:** ~85% human agreement using adversarial debate + Likert scoring

---

## 1. Module Overview

### Purpose
M11 identifies which product attributes are **non-negotiable** for the product to function. Most products have **0 hard constraints**.

### Key Rule: The 99% Rule
> 99% of consumer products have ZERO hard constraints.

### Expected Distribution
| Count | Products |
|-------|----------|
| **0** | Earbuds, water bottles, jackets, trays, makeup, toys, organizers, ice makers |
| **1** | Phone cases (device fit), oven mitts (heat resist), cables (connector type) |
| **2+** | Almost never - extremely rare |

---

## 2. Evaluation Pipeline

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ InputFilter │ --> │   Critic    │ --> │  Defender   │ --> │    Judge    │ --> │ MetaJudge   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
    │                    │                    │                    │                    │
    v                    v                    v                    v                    v
 Validate          Find 3+ issues      Rebut issues        Score 0-5         Check for
 input/output      with evidence       with evidence       per criterion     sycophancy
```

### Pipeline Flow for M11

1. **InputFilter** (No LLM)
   - Validate JSON structure
   - Check for injection patterns
   - Ensure `attribute_table`, `validated_use`, and `hard_constraints` fields exist

2. **CriticAgent** (Temperature: 0.7)
   - Find weaknesses in hard constraint identification
   - Focus on: over-constraining, NEVER category violations, missed true constraints

3. **DefenderAgent** (Temperature: 0.5)
   - Rebut each criticism with evidence
   - Acknowledge valid issues

4. **JudgeAgent** (Temperature: 0.3)
   - Score on 5 criteria (0-5 each)
   - Provide justifications with evidence

5. **MetaJudge** (Temperature: 0.2)
   - Detect sycophantic evaluations
   - Recommend retry if needed

---

## 3. M11-Specific Evaluation Criteria

### 3.1 Accuracy (0-5)
**Question:** Did the module correctly identify hard constraints?

| Score | Definition |
|-------|------------|
| 0 | Completely wrong - listed many soft features as hard |
| 1 | Major errors - 3+ soft features marked as hard |
| 2 | Significant errors - 2 soft features or missed 1 true constraint |
| 3 | Acceptable - 1 soft feature marked, or minor miss |
| 4 | Good - Correct count, minor reasoning issues |
| 5 | Perfect - Correct identification with proper reasoning |

### 3.2 Relevance (0-5)
**Question:** Are the identified constraints relevant to the validated use?

| Score | Definition |
|-------|------------|
| 0 | Constraints have no connection to validated use |
| 1 | Most constraints irrelevant |
| 2 | Some constraints don't align with use |
| 3 | Constraints partially relevant |
| 4 | Constraints mostly relevant |
| 5 | All constraints directly tied to validated use |

### 3.3 Completeness (0-5)
**Question:** Did the module analyze all attributes properly?

| Score | Definition |
|-------|------------|
| 0 | No analysis performed |
| 1 | Most attributes not analyzed |
| 2 | Several attributes skipped |
| 3 | Core attributes analyzed |
| 4 | Nearly all attributes analyzed |
| 5 | Complete analysis of all attributes |

### 3.4 Clarity (0-5)
**Question:** Is the output clear and well-structured?

| Score | Definition |
|-------|------------|
| 0 | Malformed output, unparseable |
| 1 | Very confusing reasoning |
| 2 | Difficult to follow logic |
| 3 | Understandable but could be clearer |
| 4 | Clear with minor ambiguities |
| 5 | Crystal clear reasoning and output |

### 3.5 Reasoning (0-5)
**Question:** Did the module apply the 3-step test correctly?

| Score | Definition |
|-------|------------|
| 0 | No reasoning or completely flawed |
| 1 | 3-step test not applied |
| 2 | Test partially applied, notable gaps |
| 3 | Test applied but incomplete |
| 4 | Test applied well, minor gaps |
| 5 | Perfect application of 3-step test |

---

## 4. Critic Focus Areas for M11

### 4.1 Over-Constraining (Most Common Issue)
```
WEAKNESS: Output lists 3+ hard constraints for typical consumer product
CATEGORY: accuracy
SEVERITY: critical

Example:
Input: Earbuds with [Bluetooth 5.2, Deep Bass, 32hr Battery, Water Resistant]
Output: hard_constraints: ["Bluetooth", "Deep Bass"]
Issue: Consumer earbuds should have 0 hard constraints
```

### 4.2 NEVER Category Violations
```
WEAKNESS: Output includes attributes from NEVER categories
CATEGORY: accuracy
SEVERITY: critical

NEVER Categories:
- Technology versions (Bluetooth 5.2, WiFi 6)
- Durability features (Waterproof, Rustproof)
- Performance specs (32hr battery, 26lbs/day)
- Materials (Stainless Steel, Silicone)
- Quality markers (Premium, Sturdy)
```

### 4.3 3-Step Test Not Applied
```
WEAKNESS: Reasoning doesn't show application of 3-step test
CATEGORY: reasoning
SEVERITY: major

3-Step Test:
1. Complete Removal Test: Would product be PHYSICALLY UNABLE to function?
2. Mechanism vs Quality: Is this THE mechanism or a quality modifier?
3. Basic Product Check: Does a $1 version have this?
```

### 4.4 Missed True Constraints (Rare)
```
WEAKNESS: Missing device compatibility or safety constraint
CATEGORY: completeness
SEVERITY: critical

Valid Hard Constraints:
- Phone case: Device fit (iPhone 15 Pro fit)
- Oven mitt: Heat resistance (some level required)
- Cable: Connector type (USB-C, Lightning)
```

---

## 5. Expected Outputs

### 5.1 Typical Consumer Product (0 constraints)
```json
{
  "overall": 4.5,
  "scores": {
    "accuracy": 5,
    "relevance": 4,
    "completeness": 5,
    "clarity": 4,
    "reasoning": 4
  },
  "summary": "Module correctly identified 0 hard constraints for earbuds. Applied 3-step test properly. All attributes (Bluetooth 5.2, Deep Bass, Water Resistant) correctly classified as quality/durability features."
}
```

### 5.2 Device-Specific Product (1 constraint)
```json
{
  "overall": 4.2,
  "scores": {
    "accuracy": 5,
    "relevance": 4,
    "completeness": 4,
    "clarity": 4,
    "reasoning": 4
  },
  "summary": "Module correctly identified 1 hard constraint (iPhone 15 Pro fit) for phone case. Device compatibility is a true hard constraint as wrong-size case cannot physically protect phone."
}
```

### 5.3 Over-Constrained Error
```json
{
  "overall": 2.0,
  "scores": {
    "accuracy": 1,
    "relevance": 2,
    "completeness": 3,
    "clarity": 3,
    "reasoning": 1
  },
  "summary": "Module incorrectly listed 4 hard constraints for water bottle. Materials, insulation, and size are quality features, not mechanisms. 3-step test not properly applied."
}
```

---

## 6. Debate Examples

### Example A: Earbuds with 0 Constraints (Correct)

**Input:**
```json
{
  "title": "ZKX SonicPulse True Wireless Earbuds",
  "validated_use": "Listening to audio",
  "attributes": ["Bluetooth 5.2", "Deep Bass", "32hr Battery", "IP54 Water Resistant"]
}
```

**Output:**
```json
{
  "hard_constraints": [],
  "reasoning": "Applied 3-step test: Bluetooth 5.2 is VERSION (NEVER category). Deep Bass is QUALITY. Battery is PERFORMANCE. Water Resistant is DURABILITY. All fail Step 2 - none are MECHANISMS. Conclusion: 0 hard constraints."
}
```

**Critic:**
```
W1 (minor): Reasoning could explicitly state the validated use alignment
W2 (minor): Could mention that basic earbuds without these features still work
W3 (minor): Could reference the expected distribution (most products = 0)
```

**Defender:**
```
W1: Partially valid - reasoning implies use alignment but could be explicit
W2: Valid - would strengthen the argument
W3: Invalid - the reasoning already follows the logic, explicit reference unnecessary
```

**Judge Scores:**
- Accuracy: 5 (correct 0 constraints)
- Relevance: 4 (implicit use alignment)
- Completeness: 5 (all attributes analyzed)
- Clarity: 4 (good but could be more explicit)
- Reasoning: 4 (3-step test applied correctly)

**Overall: 4.4**

---

### Example B: Water Bottle Over-Constrained (Error)

**Input:**
```json
{
  "title": "Hydro Flask Wide Mouth Water Bottle",
  "validated_use": "Carrying drinks for hydration",
  "attributes": ["Stainless Steel", "Vacuum Insulated", "BPA-Free", "24oz"]
}
```

**Output:**
```json
{
  "hard_constraints": ["Stainless Steel", "BPA-Free"],
  "reasoning": "Stainless steel is required for durability. BPA-free is required for safety."
}
```

**Critic:**
```
W1 (critical): Stainless Steel is MATERIAL - plastic bottles hold liquid too
W2 (critical): BPA-Free is SAFETY certification - non-BPA bottles still hold liquid
W3 (major): 3-step test not applied - didn't ask "Would product be UNABLE to function?"
W4 (major): Reasoning confuses quality/safety with mechanism
```

**Defender:**
```
W1: Valid - material choice doesn't affect core function
W2: Valid - safety feature doesn't prevent liquid holding
W3: Valid - reasoning shows incomplete application of test
W4: Valid - acknowledged confusion between categories
```

**Judge Scores:**
- Accuracy: 1 (2 incorrect constraints)
- Relevance: 2 (constraints not tied to core function)
- Completeness: 3 (attributes listed but not tested)
- Clarity: 3 (reasoning is clear but wrong)
- Reasoning: 1 (3-step test not applied)

**Overall: 2.0**

---

## 7. Running M11 Evaluation

### CLI Commands

```bash
# Full evaluation (3 runs, aggregated)
python3 evaluation_KD/multi_agent_eval/run_eval.py --module m11 --limit 10

# Single run (development)
python3 evaluation_KD/multi_agent_eval/run_eval.py --module m11 --single-run --limit 5 --verbose

# Compare with binary evaluation
python3 evaluation_KD/multi_agent_eval/run_eval.py --module m11 --compare-binary --limit 10
```

### Expected Results Distribution

| Likert Range | Binary Equivalent | Expected % |
|--------------|-------------------|------------|
| 4.5 - 5.0 | Strong PASS | 40-50% |
| 3.5 - 4.4 | PASS | 25-35% |
| 2.5 - 3.4 | Borderline | 10-15% |
| 0.0 - 2.4 | FAIL | 5-15% |

---

## 8. Validation Criteria

### Human Agreement Target: 85%

**Methodology:**
1. Sample 20 M11 outputs
2. Have human expert score on same 5 criteria
3. Calculate correlation coefficient
4. Target: r > 0.85

### Key Validation Points

1. **Zero Constraint Products**
   - Earbuds, bottles, jackets should score 4+ if output is []
   - Score 2 or below if output has constraints

2. **Device-Specific Products**
   - Phone cases should have exactly 1 constraint (device fit)
   - Missing = score 2-3 for accuracy
   - Extra constraints = score 2-3 for accuracy

3. **NEVER Category Violations**
   - Any NEVER category item in constraints = score 1-2 for accuracy
   - Multiple violations = score 0-1

---

## 9. Cost Estimation

### Per Sample Cost (3 runs)

| Component | Tokens | Cost (GPT-4o-mini) |
|-----------|--------|-------------------|
| InputFilter | 0 | $0.00 |
| Critic x3 | ~2000 x3 | ~$0.003 |
| Defender x3 | ~1500 x3 | ~$0.002 |
| Judge x3 | ~2000 x3 | ~$0.003 |
| MetaJudge x3 | ~500 x3 | ~$0.001 |
| **Total** | ~18000 | **~$0.009** |

### Batch Estimation (100 samples)
- Full evaluation: ~$0.90
- Single-run mode: ~$0.30

---

## 10. Dashboard Features

The M11 Multi-Agent UI Dashboard includes:

1. **Overview Panel**
   - Module description
   - Current pass rate
   - Comparison with binary evaluation

2. **Debate Visualization**
   - Critic weaknesses (color-coded by severity)
   - Defender rebuttals
   - Verdict indicators

3. **Likert Score Display**
   - Radar chart for 5 criteria
   - Score distribution histogram
   - Trend over time

4. **Sample Browser**
   - Individual sample inspection
   - Input/output/expected comparison
   - Full debate transcript

5. **Confidence Metrics**
   - HIGH/MEDIUM/LOW distribution
   - Variance by criterion
   - Retry statistics

---

## 11. Files Created

```
evaluation_KD/multi_agent_eval/
├── docs/
│   └── M11_EVALUATION_PLAN.md    # This file
├── dashboards/
│   └── m11_multiagent.html        # Interactive UI
├── results/
│   └── m11_multiagent_*.json      # Evaluation results
└── prompts/
    └── m11_context.md             # M11-specific context
```

---

## 12. Next Steps

1. [ ] Run initial evaluation on 10 M11 samples
2. [ ] Review debate quality and adjust temperatures
3. [ ] Compare with binary evaluation results
4. [ ] Human validation on 20 samples
5. [ ] Iterate on prompts if agreement < 85%
6. [ ] Scale to full dataset
