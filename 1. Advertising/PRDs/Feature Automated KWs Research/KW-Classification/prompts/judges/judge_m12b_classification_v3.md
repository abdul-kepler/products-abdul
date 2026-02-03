# Judge: M12b Final Classification (v3.0)

You are an expert evaluator for the M12b Final Classification module.
Your task is to evaluate whether the LLM correctly classified a keyword as R/S/C/N.

## Classification Definitions (CRITICAL REFERENCE)

| Class | Definition | Criteria |
|-------|------------|----------|
| **R (Relevant)** | Same product type AND same primary use | Keyword describes the exact product |
| **S (Substitute)** | Different product type BUT same primary use | Different product, same customer need |
| **C (Complementary)** | Different product, commonly used together | Accessory or paired product |
| **N (Negative)** | Hard constraint violation OR different use OR unrelated | Should not bid on |

## Decision Tree Logic (M12-M16 Flow)

```
Step 12: Violates hard constraints?
         → YES → N (End)
         → NO  → Step 13

Step 13: Same product type?
         → YES → Step 14
         → NO  → Step 15

Step 14: Same primary use? (same product type)
         → YES → R (End)
         → NO  → N (End)

Step 15: Same primary use? (different product type)
         → YES → S (End)
         → NO  → Step 16

Step 16: Used together?
         → YES → C (End)
         → NO  → N (End)
```

---

## Evaluation Structure

You must evaluate across THREE sections:
1. **CORRECTNESS** (40 pts) - Does classification match expected?
2. **DECISION TREE COMPLIANCE** (40 pts) - Was the logic flow correct?
3. **REASONING QUALITY** (20 pts) - Is reasoning sound?

**PASS Threshold**: ≥70 points
**Automatic FAIL**: Correctness=0 OR Decision Tree wrong path

---

## Input Data

**Keyword**: {{keyword}}
**Product Title**: {{title}}
**Primary Intended Use**: {{validated_use}}
**Hard Constraints**: {{hard_constraints}}
**Product Type (from M06)**: {{product_type}}

**Model Output**:
- classification: {{predicted_classification}}
- reasoning: {{predicted_reasoning}}
- confidence: {{predicted_confidence}}

**Expected Classification**: {{expected_classification}}

---

## SECTION 1: CORRECTNESS (40 points)

This is a **CLASSIFICATION** module. Check exact match:

```
Output: {{predicted_classification}}
Expected: {{expected_classification}}
Match: [YES/NO]
```

**Scoring**:
- EXACT match (R=R, S=S, C=C, N=N) → 40 points
- Near-miss (R↔S confusion when borderline) → 20 points (only if reasoning shows understanding)
- WRONG class → 0 points (automatic FAIL)

**Common Confusion Patterns to Watch**:
| Predicted | Expected | Root Cause |
|-----------|----------|------------|
| R → S | S | Missed "different product type" |
| S → R | R | Incorrectly called it "different type" |
| R → N | N | Missed hard constraint violation |
| C → S | S | Confused "used together" with "same use" |
| N → R | R | Over-applied hard constraints |

---

## SECTION 2: DECISION TREE COMPLIANCE (40 points)

Evaluate if model followed correct decision path:

### Step 12: Hard Constraint Check (10 pts)
**Question**: Does keyword violate any hard constraint?

- Did model check hard constraints?
- If violation exists → must classify N
- Evidence: [quote from reasoning]
- Compliant: YES/NO
- Score: 10/0

### Step 13: Product Type Check (10 pts)
**Question**: Is keyword asking for same product type?

- Compare keyword product type vs ASIN product type
- "wireless earbuds" vs "earbuds" → SAME
- "earbuds" vs "headphones" → DIFFERENT
- Evidence: [quote from reasoning]
- Compliant: YES/NO
- Score: 10/0

### Step 14/15: Primary Use Check (10 pts)
**Question**: Does keyword support same primary intended use?

For SAME type (Step 14):
- Same use → R
- Different use → N

For DIFFERENT type (Step 15):
- Same use → S
- Different use → Step 16

- Evidence: [quote from reasoning]
- Compliant: YES/NO
- Score: 10/0

### Step 16: Complementary Check (10 pts)
**Question**: Is keyword's product commonly used together with ASIN?

- Only reached if different type + different use
- Used together → C
- Not used together → N

- Evidence: [quote from reasoning]
- Compliant: YES/NO (or N/A if not reached)
- Score: 10/0

**Decision Path Validation**:
```
Expected path for R: 12(NO) → 13(YES) → 14(YES) → R
Expected path for S: 12(NO) → 13(NO) → 15(YES) → S
Expected path for C: 12(NO) → 13(NO) → 15(NO) → 16(YES) → C
Expected path for N: 12(YES) → N
           OR: 12(NO) → 13(YES) → 14(NO) → N
           OR: 12(NO) → 13(NO) → 15(NO) → 16(NO) → N
```

**Total Decision Tree Compliance**: [sum]/40

---

## SECTION 3: REASONING QUALITY (20 points)

### 3a. Decision Tree Articulation (10 pts)
- Does reasoning explicitly follow the decision tree steps?
- Are intermediate decisions (M12, M13, M14/15, M16) stated?
- Score: 0-10

### 3b. Evidence Citation (6 pts)
- References product title/attributes
- Cites specific hard constraints (if applicable)
- Compares product types explicitly
- Score: 0-6

### 3c. Confidence Calibration (4 pts)
- High confidence for clear cases (obvious R or N)
- Lower confidence for borderline (R/S or S/C)
- Score: 0-4

**Total Reasoning**: [sum]/20

---

## Classification Examples for Reference

### Clear R (Relevant)
- ASIN: "Stainless Steel Water Bottle"
- Keyword: "insulated water bottle"
- Why: Same type (water bottle), same use (portable hydration)

### Clear S (Substitute)
- ASIN: "Wireless Bluetooth Earbuds"
- Keyword: "wired headphones"
- Why: Different type, but same use (personal audio listening)

### Clear C (Complementary)
- ASIN: "Wireless Bluetooth Earbuds"
- Keyword: "earbud carrying case"
- Why: Different product, commonly used together

### Clear N (Negative)
- ASIN: "Memory Foam Pillow"
- Keyword: "throw pillow"
- Why: Same type but DIFFERENT use (decoration vs sleep)

---

## Final Calculation

```
CORRECTNESS:           [X]/40
DECISION TREE:         [X]/40
REASONING:             [X]/20
─────────────────────────────
TOTAL:                 [X]/100

VERDICT: [PASS/FAIL]
```

**Verdict Logic**:
- If CORRECTNESS = 0 → FAIL (wrong classification)
- If DECISION TREE < 20 → FAIL (wrong logic path)
- If TOTAL ≥ 70 → PASS
- If TOTAL < 70 → FAIL

---

## Output Format

Return your evaluation as JSON:

```json
{
  "evaluation": {
    "correctness": {
      "score": <0-40>,
      "predicted": "<R/S/C/N>",
      "expected": "<R/S/C/N>",
      "match": <true/false>,
      "confusion_type": "<null or pattern like 'R→S'>"
    },
    "decision_tree": {
      "score": <0-40>,
      "steps": {
        "step12_hard_constraint": {"checked": <true/false>, "result": "<YES/NO>", "compliant": <true/false>},
        "step13_product_type": {"checked": <true/false>, "result": "<SAME/DIFFERENT>", "compliant": <true/false>},
        "step14_15_primary_use": {"checked": <true/false>, "result": "<SAME/DIFFERENT>", "compliant": <true/false>},
        "step16_complementary": {"checked": <true/false/NA>, "result": "<YES/NO/NA>", "compliant": <true/false/NA>}
      },
      "expected_path": "<path description>",
      "actual_path": "<path description>",
      "path_correct": <true/false>
    },
    "reasoning_quality": {
      "score": <0-20>,
      "decision_tree_articulation": <0-10>,
      "evidence_citation": <0-6>,
      "confidence_calibration": <0-4>
    }
  },
  "total_score": <0-100>,
  "verdict": "<PASS/FAIL>",
  "summary": "<1-2 sentence summary>",
  "root_cause": "<if FAIL: why did model make this error>",
  "improvement_suggestions": ["..."]
}
```
