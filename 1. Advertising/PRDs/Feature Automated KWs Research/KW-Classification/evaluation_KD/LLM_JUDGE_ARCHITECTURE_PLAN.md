# LLM-as-a-Judge Evaluation Architecture Plan

> **Purpose**: Design a comprehensive evaluation system for the 16-module KW Classification pipeline
> **Based on**: 29 academic papers from [academic research](./academic-research/)
> **Scope**: OB/CB/NB branding + R/S/C/N relevance classification

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Judge Roles Definition](#judge-roles-definition)
3. [Cohen's Kappa & Structured Evaluation](#cohens-kappa--structured-evaluation)
4. [Strategies That Move the Needle](#strategies-that-move-the-needle)
5. [What to Implement vs Discard](#what-to-implement-vs-discard)
6. [Implementation Roadmap](#implementation-roadmap)
7. [Architecture Diagram](#architecture-diagram)

---

## Executive Summary

### The Problem

The KW Classification pipeline has 16 modules producing structured outputs (JSON). Current challenges:
- No systematic evaluation of module outputs
- Unknown error propagation between modules
- No inter-rater reliability measurement
- Manual review doesn't scale

### The Solution

A **three-tier judge architecture** based on academic research:

| Tier | Judge Role | Purpose | Frequency |
|------|------------|---------|-----------|
| **Tier 1** | Data Quality Gate | Catch malformed/invalid outputs | Every run |
| **Tier 2** | Rubric Scoring | Multi-dimensional accuracy assessment | Every run |
| **Tier 3** | Failure Bucketing | Categorize errors for systematic improvement | Post-batch |

### Key Research-Backed Decisions

| Decision | Research Source | Impact |
|----------|-----------------|--------|
| **Use PoLL (3-model panel)** | [2404.18796](https://arxiv.org/abs/2404.18796) | 7-8× cheaper than GPT-4, better reliability |
| **FLASK skill decomposition** | [2307.10928](https://arxiv.org/abs/2307.10928) | Skill-specific > holistic evaluation |
| **PORTIA for pairwise** | [2310.01432](https://arxiv.org/abs/2310.01432) | 98% consistency on position bias |
| **Length-control scoring** | [2404.04475](https://arxiv.org/abs/2404.04475) | Remove verbosity bias from reasoning |

---

## Judge Roles Definition

### Tier 1: Data Quality Gate

**Purpose**: Binary pass/fail validation before deeper evaluation

**What It Checks**:

| Check | Module Types | Failure Action |
|-------|--------------|----------------|
| JSON validity | All | Reject, re-run |
| Required fields present | All | Reject, re-run |
| Field type correctness | All | Reject, re-run |
| Value in allowed set | M02-M05 (OB/CB/NB), M12-M16 (R/S/C/N) | Reject, re-run |
| Array not empty | M01a (variations), M06 (taxonomy), M11 (constraints) | Flag for review |

**Implementation**:
```python
# Tier 1: Deterministic checks, no LLM needed
def data_quality_gate(output: dict, schema: dict) -> tuple[bool, list[str]]:
    errors = []

    # JSON schema validation
    if not validate_schema(output, schema):
        errors.append("schema_violation")

    # Required field check
    for field in schema["required"]:
        if field not in output:
            errors.append(f"missing_field:{field}")

    # Enum validation
    if "branding_scope" in output:
        if output["branding_scope"] not in ["OB", "CB", "NB", None]:
            errors.append("invalid_branding_scope")

    return len(errors) == 0, errors
```

**Cost**: Zero LLM calls (deterministic)

---

### Tier 2: Rubric Scoring Judges

**Purpose**: Multi-dimensional evaluation of output quality using LLM judges

**Design Principle**: Based on [FLASK](https://arxiv.org/abs/2307.10928) - decompose evaluation into independent dimensions, then aggregate.

#### Judge Types by Module Category

**A. Extraction Judges (M01, M01a, M01b, M06, M07)**

| Dimension | Weight | What It Measures |
|-----------|--------|------------------|
| **Completeness** | 0.35 | Did it extract all relevant entities? |
| **Precision** | 0.35 | Are extracted entities correct (no hallucinations)? |
| **Format Compliance** | 0.15 | Correct structure, types, separators |
| **Coverage** | 0.15 | Handles edge cases (abbreviations, typos) |

**Rubric Example (M01a - Brand Variations)**:
```
COMPLETENESS (0.35):
  1.0: All case variations + common typos + phonetic spellings included
  0.5: Basic variations present, missing typos or phonetic
  0.0: Major variations missing (e.g., all-caps version not included)

PRECISION (0.35):
  1.0: All variations are valid brand references
  0.5: 1-2 questionable variations included
  0.0: Generic words or unrelated terms included as variations

FORMAT_COMPLIANCE (0.15):
  1.0: Comma-separated, no duplicates, proper casing
  0.5: Minor format issues (extra spaces, inconsistent separators)
  0.0: Broken format, unparseable

COVERAGE (0.15):
  1.0: Handles multi-word brands, hyphenated names, numbers
  0.5: Basic cases covered, edge cases missed
  0.0: Only exact match, no variations generated
```

**B. Classification Judges (M02-M05, M12-M16)**

| Dimension | Weight | What It Measures |
|-----------|--------|------------------|
| **Classification Accuracy** | 0.40 | Correct label (OB/CB/NB or R/S/C/N) |
| **Evidence Quality** | 0.30 | Cites specific matching terms/rules |
| **Reasoning Validity** | 0.20 | Logical chain from evidence to conclusion |
| **Boundary Handling** | 0.10 | Correct behavior on edge cases |

**Rubric Example (M02 - Own Brand Classification)**:
```
CLASSIFICATION_ACCURACY (0.40):
  1.0: Correct classification matching ground truth
  0.5: Classification defensible but disagrees with annotation
  0.0: Clear misclassification (missed obvious brand match)

EVIDENCE_QUALITY (0.30):
  1.0: Cites exact matched_term from variations list
  0.5: Claims match but doesn't specify which variation
  0.0: No evidence, or cites non-existent term

REASONING_VALIDITY (0.20):
  1.0: Clear logic: "keyword contains 'jbl' which matches variation 'JBL'"
  0.5: Reasoning present but incomplete or circular
  0.0: No reasoning, or reasoning contradicts classification

BOUNDARY_HANDLING (0.10):
  1.0: Correctly handles partial matches, word boundaries
  0.5: Inconsistent on edge cases
  0.0: Fails on basic boundary cases (e.g., "jbl" in "adjustable")
```

**C. Foundation Judges (M08-M11)**

| Dimension | Weight | What It Measures |
|-----------|--------|------------------|
| **Semantic Accuracy** | 0.40 | Correct interpretation of product purpose |
| **Constraint Validity** | 0.30 | Hard constraints are truly non-negotiable |
| **Conciseness** | 0.15 | No marketing fluff, features, or adjectives |
| **Actionability** | 0.15 | Output usable by downstream modules |

**Rubric Example (M09 - Primary Intended Use)**:
```
SEMANTIC_ACCURACY (0.40):
  1.0: Captures the ONE core purpose (e.g., "portable hydration" for water bottle)
  0.5: Correct direction but too broad/narrow
  0.0: Wrong purpose identified

CONSTRAINT_VALIDITY (0.30):
  1.0: N/A for M09 (used in M11)

CONCISENESS (0.30):
  1.0: 3-6 words, verb+noun structure, no adjectives
  0.5: Slightly over/under word count, minor violations
  0.0: Contains features, marketing language, specifications

ACTIONABILITY (0.30):
  1.0: Clear enough for M10 validation and M12 classification
  0.5: Ambiguous but usable
  0.0: Too vague to use downstream
```

---

### Tier 3: Failure Bucketing Judge

**Purpose**: Categorize errors for systematic improvement (post-batch analysis)

**Failure Categories**:

| Category | Description | Example | Action |
|----------|-------------|---------|--------|
| **DATA_QUALITY** | Invalid output format | Missing required field | Fix schema enforcement |
| **ENTITY_MISS** | Failed to extract entity | Missed brand variation | Expand extraction rules |
| **ENTITY_HALLUCINATION** | Extracted non-existent entity | Added fake sub-brand | Add precision checks |
| **CLASSIFICATION_ERROR** | Wrong label | OB classified as NB | Review classification rules |
| **REASONING_FLAW** | Correct answer, wrong reasoning | Right label, bad evidence | Improve prompts |
| **BOUNDARY_ERROR** | Edge case failure | Partial match handling | Add edge case examples |
| **CASCADE_ERROR** | Upstream error propagated | Bad M09 → bad M12 | Fix upstream first |

**Implementation**:
```python
def bucket_failure(
    module_id: str,
    input_data: dict,
    output: dict,
    expected: dict,
    tier2_scores: dict
) -> dict:
    """Categorize failure for systematic analysis."""

    # Determine primary failure category
    if tier2_scores["format_compliance"] < 0.5:
        category = "DATA_QUALITY"
    elif tier2_scores["completeness"] < 0.5:
        category = "ENTITY_MISS"
    elif tier2_scores["precision"] < 0.5:
        category = "ENTITY_HALLUCINATION"
    elif tier2_scores["classification_accuracy"] < 0.5:
        category = "CLASSIFICATION_ERROR"
    elif tier2_scores["reasoning_validity"] < 0.5:
        category = "REASONING_FLAW"
    elif tier2_scores["boundary_handling"] < 0.5:
        category = "BOUNDARY_ERROR"
    else:
        category = "UNKNOWN"

    return {
        "category": category,
        "module_id": module_id,
        "lowest_dimension": min(tier2_scores, key=tier2_scores.get),
        "scores": tier2_scores,
        "needs_upstream_check": module_id in ["M08", "M09", "M10", "M11", "M12"]
    }
```

---

## Cohen's Kappa & Structured Evaluation

### Why Cohen's Kappa?

From [Sage (2512.16041)](https://arxiv.org/abs/2512.16041): "Substantial inconsistency in human judgments" - we need to measure agreement systematically.

**Cohen's Kappa** measures inter-rater reliability beyond chance agreement:
- κ = 1.0: Perfect agreement
- κ > 0.8: Almost perfect
- κ > 0.6: Substantial
- κ > 0.4: Moderate
- κ < 0.4: Poor

### Kappa Measurement Points

| Measurement | Rater 1 | Rater 2 | Purpose |
|-------------|---------|---------|---------|
| **Human-Human** | Annotator A | Annotator B | Establish annotation quality |
| **Human-LLM** | Human annotation | LLM judge score | Validate judge reliability |
| **LLM-LLM** | Judge Model A | Judge Model B | PoLL consistency check |
| **Run-Run** | Same judge, run 1 | Same judge, run 2 | Self-consistency |

### Implementation for KW Classification

**1. Classification Modules (M02-M05, M12-M16)**

For categorical outputs (OB/CB/NB, R/S/C/N):

```python
from sklearn.metrics import cohen_kappa_score

def compute_classification_kappa(
    labels_a: list[str],  # e.g., ["OB", "NB", "CB", ...]
    labels_b: list[str]
) -> float:
    """Compute Cohen's Kappa for classification agreement."""
    return cohen_kappa_score(labels_a, labels_b)

# Example: Human vs LLM Judge
human_labels = ["OB", "NB", "CB", "OB", "NB"]
judge_labels = ["OB", "NB", "NB", "OB", "NB"]  # 1 disagreement
kappa = compute_classification_kappa(human_labels, judge_labels)
# kappa ≈ 0.74 (substantial agreement)
```

**2. Extraction Modules (M01, M06, M07)**

For set-based outputs (variations, taxonomy levels):

```python
def compute_extraction_kappa(
    sets_a: list[set],  # e.g., [{"JBL", "jbl"}, {"Sony", "SONY"}]
    sets_b: list[set]
) -> float:
    """Compute agreement on set extraction using Jaccard-weighted Kappa."""
    agreements = []
    for set_a, set_b in zip(sets_a, sets_b):
        jaccard = len(set_a & set_b) / len(set_a | set_b) if set_a | set_b else 1.0
        agreements.append(1 if jaccard > 0.8 else 0)

    # Convert to binary agreement for Kappa
    perfect = [1] * len(agreements)
    return cohen_kappa_score(perfect, agreements)
```

**3. Foundation Modules (M09-M11)**

For semantic outputs (primary use, hard constraints):

```python
def compute_semantic_kappa(
    texts_a: list[str],  # e.g., ["portable hydration", "audio listening"]
    texts_b: list[str],
    similarity_threshold: float = 0.85
) -> float:
    """Compute agreement on semantic similarity."""
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')

    embeddings_a = model.encode(texts_a)
    embeddings_b = model.encode(texts_b)

    agreements = []
    for emb_a, emb_b in zip(embeddings_a, embeddings_b):
        similarity = cosine_similarity([emb_a], [emb_b])[0][0]
        agreements.append(1 if similarity > similarity_threshold else 0)

    perfect = [1] * len(agreements)
    return cohen_kappa_score(perfect, agreements)
```

### Kappa Targets by Module

| Module | Output Type | Target κ (Human-Judge) | Minimum κ |
|--------|-------------|------------------------|-----------|
| M02-M05 | Classification (OB/CB/NB) | ≥ 0.85 | 0.70 |
| M12-M16 | Classification (R/S/C/N) | ≥ 0.80 | 0.65 |
| M01, M01a | Set extraction | ≥ 0.75 | 0.60 |
| M06 | Taxonomy | ≥ 0.70 | 0.55 |
| M09-M10 | Semantic (primary use) | ≥ 0.70 | 0.55 |
| M11 | Hard constraints | ≥ 0.75 | 0.60 |

---

## Strategies That Move the Needle

Based on the 29 papers analyzed, these strategies provide the highest ROI:

### 1. PoLL (Panel of LLM Judges) - **IMPLEMENT**

**Source**: [2404.18796](https://arxiv.org/abs/2404.18796)

**Why It Matters**:
- Single GPT-4 judge: Cohen's κ = 0.627
- PoLL (3 models): Cohen's κ = **0.763** (+22% improvement)
- Cost: **7-8× cheaper** than GPT-4 alone

**Implementation for KW Classification**:
```python
# Panel composition (3 diverse model families)
POLL_JUDGES = [
    {"model": "gpt-4o-mini", "provider": "openai"},
    {"model": "claude-3-haiku", "provider": "anthropic"},
    {"model": "command-r", "provider": "cohere"}
]

def poll_evaluate(module_output: dict, rubric: dict) -> dict:
    """Run PoLL evaluation with 3 judges."""
    scores = []
    for judge in POLL_JUDGES:
        score = run_single_judge(module_output, rubric, judge)
        scores.append(score)

    # Aggregation strategy
    if is_classification_module:
        # Max voting for categorical outputs
        final_label = mode([s["label"] for s in scores])
    else:
        # Average for numeric scores
        final_score = mean([s["score"] for s in scores])

    return {
        "final_score": final_score,
        "individual_scores": scores,
        "agreement_rate": calculate_agreement(scores)
    }
```

**Expected Impact**: +20% judge reliability, -85% cost vs GPT-4

---

### 2. FLASK Skill Decomposition - **IMPLEMENT**

**Source**: [2307.10928](https://arxiv.org/abs/2307.10928)

**Why It Matters**:
- Holistic scoring: Spearman ρ = 0.641
- Skill-specific scoring: Spearman ρ = **0.680** (+6% improvement)
- Enables targeted debugging (which dimension failed?)

**Implementation**:
```python
# Module-specific skill decomposition
MODULE_SKILLS = {
    "M02": {
        "classification_accuracy": {"weight": 0.40, "type": "categorical"},
        "evidence_quality": {"weight": 0.30, "type": "text_match"},
        "reasoning_validity": {"weight": 0.20, "type": "logical"},
        "boundary_handling": {"weight": 0.10, "type": "edge_case"}
    },
    "M09": {
        "semantic_accuracy": {"weight": 0.40, "type": "semantic"},
        "conciseness": {"weight": 0.30, "type": "constraint"},
        "actionability": {"weight": 0.30, "type": "downstream"}
    }
    # ... defined for each module
}

def flask_evaluate(module_id: str, output: dict, expected: dict) -> dict:
    """Evaluate each skill dimension separately."""
    skills = MODULE_SKILLS[module_id]
    dimension_scores = {}

    for skill_name, skill_config in skills.items():
        score = evaluate_skill(output, expected, skill_config)
        dimension_scores[skill_name] = score

    # Weighted aggregate
    final_score = sum(
        dimension_scores[s] * skills[s]["weight"]
        for s in skills
    )

    return {
        "final_score": final_score,
        "dimension_scores": dimension_scores,
        "lowest_dimension": min(dimension_scores, key=dimension_scores.get)
    }
```

**Expected Impact**: Better failure diagnosis, targeted prompt improvements

---

### 3. Swap Augmentation for Classification - **IMPLEMENT**

**Source**: [JudgeLM (2310.17631)](https://arxiv.org/abs/2310.17631)

**Why It Matters**:
- Reduces position bias by **+5.44%** consistency
- Essential for M02-M05 when comparing keyword against multiple brand lists

**Implementation**:
```python
def evaluate_with_swap(keyword: str, brand_a: dict, brand_b: dict) -> dict:
    """Evaluate both orderings to reduce position bias."""

    # Order A: brand_a first
    score_ab = judge_brand_match(keyword, [brand_a, brand_b])

    # Order B: brand_b first
    score_ba = judge_brand_match(keyword, [brand_b, brand_a])

    # Check consistency
    if score_ab["match"] == score_ba["match"]:
        return {"result": score_ab, "consistent": True}
    else:
        # Flag for human review
        return {"result": None, "consistent": False, "needs_review": True}
```

**Expected Impact**: +5% classification consistency

---

### 4. Length-Controlled Evaluation - **IMPLEMENT**

**Source**: [LC AlpacaEval (2404.04475)](https://arxiv.org/abs/2404.04475)

**Why It Matters**:
- Verbose reasoning shouldn't score higher than concise reasoning
- Critical for M09 (primary use should be 3-6 words, not paragraphs)

**Implementation**:
```python
def evaluate_with_length_control(output: dict, expected: dict) -> dict:
    """Penalize verbosity, don't reward it."""

    # For M09: primary_use should be 3-6 words
    word_count = len(output["primary_use"].split())

    # Length penalty
    if word_count < 3:
        length_penalty = 0.2  # Too short
    elif word_count > 6:
        length_penalty = 0.1 * (word_count - 6)  # Penalize each extra word
    else:
        length_penalty = 0

    # Base score from semantic similarity
    base_score = semantic_similarity(output["primary_use"], expected["primary_use"])

    return {
        "score": max(0, base_score - length_penalty),
        "word_count": word_count,
        "length_penalty": length_penalty
    }
```

**Expected Impact**: Removes verbosity bias from evaluation

---

### 5. Cascade Error Detection - **IMPLEMENT**

**Source**: Pipeline analysis + [JudgeBench (2410.12784)](https://arxiv.org/abs/2410.12784)

**Why It Matters**:
- KW pipeline has 6 sequential dependencies: M06 → M08 → M09 → M10 → M11 → M12
- Error in M09 corrupts M10, M11, M12 evaluations
- Must isolate root cause vs downstream effect

**Implementation**:
```python
DEPENDENCY_CHAIN = {
    "M08": ["M06", "M07"],
    "M09": ["M08"],
    "M10": ["M09"],
    "M11": ["M10"],
    "M12": ["M11"]
}

def detect_cascade_error(
    module_id: str,
    module_scores: dict[str, float]
) -> dict:
    """Check if failure is due to upstream error."""

    if module_id not in DEPENDENCY_CHAIN:
        return {"is_cascade": False, "root_cause": module_id}

    # Check upstream modules
    for upstream in DEPENDENCY_CHAIN[module_id]:
        if module_scores.get(upstream, 1.0) < 0.7:
            return {
                "is_cascade": True,
                "root_cause": upstream,
                "message": f"Fix {upstream} first before evaluating {module_id}"
            }

    return {"is_cascade": False, "root_cause": module_id}
```

**Expected Impact**: Prevents wasted effort fixing symptoms instead of causes

---

## What to Implement vs Discard

### IMPLEMENT (High ROI)

| Strategy | Source | Complexity | Impact | Priority |
|----------|--------|------------|--------|----------|
| **PoLL (3-model panel)** | [2404.18796](https://arxiv.org/abs/2404.18796) | Medium | +20% reliability, -85% cost | **P0** |
| **FLASK skill decomposition** | [2307.10928](https://arxiv.org/abs/2307.10928) | Medium | Better debugging | **P0** |
| **Data quality gate** | Best practice | Low | Catch format errors | **P0** |
| **Cohen's Kappa tracking** | [2512.16041](https://arxiv.org/abs/2512.16041) | Low | Measure reliability | **P1** |
| **Swap augmentation** | [2310.17631](https://arxiv.org/abs/2310.17631) | Low | +5% consistency | **P1** |
| **Length-controlled eval** | [2404.04475](https://arxiv.org/abs/2404.04475) | Low | Remove verbosity bias | **P1** |
| **Cascade error detection** | Pipeline analysis | Low | Find root causes | **P1** |
| **Failure bucketing** | Best practice | Medium | Systematic improvement | **P2** |

### DEFER (Lower Priority)

| Strategy | Source | Why Defer |
|----------|--------|-----------|
| **Fine-tuned judge** | PROMETHEUS, JudgeLM | Need 10K+ labeled examples first |
| **PORTIA split-merge** | [2310.01432](https://arxiv.org/abs/2310.01432) | Complex, only for long text comparison |
| **Multi-agent debate** | ChatEval | Expensive, marginal gains for classification |
| **Self-rewarding** | [2401.10020](https://arxiv.org/abs/2401.10020) | Research-stage, not production-ready |

### DISCARD (Not Applicable)

| Strategy | Source | Why Discard |
|----------|--------|-------------|
| **FActScore atomic facts** | [2305.14251](https://arxiv.org/abs/2305.14251) | For long-form generation, not classification |
| **G-EVAL probability weighting** | [2303.16634](https://arxiv.org/abs/2303.16634) | Requires logprobs, not available in all APIs |
| **Reference-based evaluation** | Various | Our outputs are structured, not free-form |
| **Meta-rewarding** | [2407.19594](https://arxiv.org/abs/2407.19594) | Too complex for current needs |

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1-2)

**Goal**: Basic evaluation infrastructure

| Task | Output |
|------|--------|
| Implement data quality gate | `validators/data_quality.py` |
| Define rubrics for all 16 modules | `rubrics/module_rubrics.yaml` |
| Set up Cohen's Kappa computation | `metrics/kappa.py` |
| Create evaluation runner | `evaluation/runner.py` |

**Success Criteria**: Can run evaluation on any module, get Tier 1 pass/fail

### Phase 2: PoLL + FLASK (Week 3-4)

**Goal**: Research-backed evaluation quality

| Task | Output |
|------|--------|
| Implement PoLL with 3 judges | `judges/poll.py` |
| Implement FLASK skill decomposition | `judges/flask_evaluator.py` |
| Add swap augmentation for M02-M05 | `judges/swap_augment.py` |
| Add length control for M09-M11 | `judges/length_control.py` |

**Success Criteria**: κ ≥ 0.75 Human-Judge agreement on classification modules

### Phase 3: Systematic Improvement (Week 5-6)

**Goal**: Feedback loop for prompt improvement

| Task | Output |
|------|--------|
| Implement failure bucketing | `analysis/failure_buckets.py` |
| Implement cascade detection | `analysis/cascade_detector.py` |
| Build improvement suggestion generator | `improvement/suggester.py` |
| Create dashboard for tracking | `dashboard/` |

**Success Criteria**: Can identify top 3 failure categories per module

### Phase 4: Optimization (Week 7+)

**Goal**: Continuous improvement

| Task | Output |
|------|--------|
| A/B test evaluation strategies | Comparison reports |
| Collect data for future fine-tuning | `data/judge_training/` |
| Optimize judge prompts | Improved prompts |

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LLM-AS-A-JUDGE EVALUATION ARCHITECTURE                    │
└─────────────────────────────────────────────────────────────────────────────┘

                              MODULE OUTPUT
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  TIER 1: DATA QUALITY GATE                                                   │
│  ────────────────────────                                                    │
│  • JSON schema validation                                                    │
│  • Required field check                                                      │
│  • Enum value validation                                                     │
│  • Array non-empty check                                                     │
│                                                                              │
│  Output: PASS → continue | FAIL → reject & re-run                           │
│  Cost: $0 (deterministic)                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼ (if PASS)
┌─────────────────────────────────────────────────────────────────────────────┐
│  TIER 2: RUBRIC SCORING (PoLL + FLASK)                                       │
│  ─────────────────────────────────────                                       │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  PoLL: Panel of 3 Judges                                            │    │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐                       │    │
│  │  │ GPT-4o-   │  │ Claude-3  │  │ Command-R │                       │    │
│  │  │   mini    │  │   Haiku   │  │           │                       │    │
│  │  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘                       │    │
│  │        │              │              │                              │    │
│  │        └──────────────┼──────────────┘                              │    │
│  │                       ▼                                             │    │
│  │              ┌─────────────────┐                                    │    │
│  │              │   Aggregation   │                                    │    │
│  │              │ (vote/average)  │                                    │    │
│  │              └─────────────────┘                                    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  FLASK: Skill Decomposition                                         │    │
│  │                                                                     │    │
│  │  Extraction Modules (M01, M06, M07):                               │    │
│  │  ├── Completeness (0.35)                                           │    │
│  │  ├── Precision (0.35)                                              │    │
│  │  ├── Format Compliance (0.15)                                      │    │
│  │  └── Coverage (0.15)                                               │    │
│  │                                                                     │    │
│  │  Classification Modules (M02-M05, M12-M16):                        │    │
│  │  ├── Classification Accuracy (0.40)                                │    │
│  │  ├── Evidence Quality (0.30)                                       │    │
│  │  ├── Reasoning Validity (0.20)                                     │    │
│  │  └── Boundary Handling (0.10)                                      │    │
│  │                                                                     │    │
│  │  Foundation Modules (M08-M11):                                     │    │
│  │  ├── Semantic Accuracy (0.40)                                      │    │
│  │  ├── Conciseness (0.30)                                            │    │
│  │  └── Actionability (0.30)                                          │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  + Swap Augmentation (M02-M05): Evaluate both orderings                     │
│  + Length Control (M09-M11): Penalize verbose outputs                       │
│                                                                              │
│  Output: dimension_scores{}, final_score, lowest_dimension                  │
│  Cost: ~$0.003/evaluation (PoLL with small models)                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  METRICS & TRACKING                                                          │
│  ──────────────────                                                          │
│                                                                              │
│  • Cohen's Kappa: Human-Judge, Judge-Judge, Run-Run                         │
│  • Per-module accuracy trends                                                │
│  • Per-dimension score distributions                                         │
│  • Failure rate by category                                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼ (batch analysis)
┌─────────────────────────────────────────────────────────────────────────────┐
│  TIER 3: FAILURE BUCKETING                                                   │
│  ─────────────────────────                                                   │
│                                                                              │
│  Categories:                                                                 │
│  ├── DATA_QUALITY: Schema/format issues                                     │
│  ├── ENTITY_MISS: Failed extraction                                         │
│  ├── ENTITY_HALLUCINATION: False extraction                                 │
│  ├── CLASSIFICATION_ERROR: Wrong label                                      │
│  ├── REASONING_FLAW: Bad evidence/logic                                     │
│  ├── BOUNDARY_ERROR: Edge case failure                                      │
│  └── CASCADE_ERROR: Upstream module failure                                 │
│                                                                              │
│  + Cascade Detection: Check if upstream modules failed first                │
│                                                                              │
│  Output: Prioritized list of improvement actions                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  IMPROVEMENT LOOP                                                            │
│  ────────────────                                                            │
│                                                                              │
│  1. Top failure bucket → Most impactful module to fix                       │
│  2. Lowest dimension → Which skill to improve                               │
│  3. Example failures → Evidence for prompt revision                         │
│  4. Prompt update → Apply targeted improvement                              │
│  5. Re-evaluate → Measure improvement                                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Key Metrics to Track

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Human-Judge κ (classification)** | ≥ 0.80 | Weekly sample |
| **Judge-Judge κ (PoLL)** | ≥ 0.85 | Every batch |
| **Tier 1 pass rate** | ≥ 99% | Every run |
| **Tier 2 avg score** | ≥ 0.75 | Every batch |
| **Cascade error rate** | ≤ 10% | Every batch |
| **Top failure bucket coverage** | Top 3 = 80% of failures | Weekly |

---

## References

All strategies are based on the academic research in [docs/academic-research/](./academic-research/):

- **PoLL**: [Panel of LLM Judges (2404.18796)](https://arxiv.org/abs/2404.18796)
- **FLASK**: [Fine-grained Skill Evaluation (2307.10928)](https://arxiv.org/abs/2307.10928)
- **Swap Augmentation**: [JudgeLM (2310.17631)](https://arxiv.org/abs/2310.17631)
- **Length Control**: [LC AlpacaEval (2404.04475)](https://arxiv.org/abs/2404.04475)
- **Consistency**: [Sage (2512.16041)](https://arxiv.org/abs/2512.16041)
- **Bias Awareness**: [CALM (2410.02736)](https://arxiv.org/abs/2410.02736)

---

*Plan created: January 2026*
*Based on: 29 academic papers + KW Classification pipeline analysis*
*For: Kepler AI Classification Project*
