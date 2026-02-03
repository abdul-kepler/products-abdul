# Adversarial Debate Evaluation System

## Purpose

This system evaluates LLM module outputs using a **multi-agent adversarial debate** approach with **Likert scoring (0-5)**. Instead of a single judge, four specialized agents debate the quality of an output, reducing bias and improving reliability.

**Goal:** Achieve ~85% agreement with human evaluators.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ADVERSARIAL DEBATE PIPELINE                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   INPUT DATA                                                                 │
│   ├── input_data      → The question/prompt given to the module             │
│   ├── output_data     → The module's response (what we're evaluating)       │
│   └── expected_data   → Ground truth / reference answer                     │
│                                                                              │
│                              ▼                                               │
│   ┌──────────────────────────────────────────────────────────────────────┐  │
│   │  STEP 0: INPUT FILTER (Temperature: 0.0)                             │  │
│   │  ────────────────────────────────────────────────────────────────────│  │
│   │  Purpose: Security check - detect prompt injection attempts          │  │
│   │  Output:  { is_valid: bool, rejection_reason: string }               │  │
│   │  Action:  If invalid → reject immediately, skip evaluation           │  │
│   └──────────────────────────────────────────────────────────────────────┘  │
│                              ▼                                               │
│   ┌──────────────────────────────────────────────────────────────────────┐  │
│   │  STEP 1: CRITIC AGENT (Temperature: 0.7 - Creative)                  │  │
│   │  ────────────────────────────────────────────────────────────────────│  │
│   │  Role:    Adversarial - Find ALL weaknesses in the output            │  │
│   │  Input:   input_data, output_data, expected_data (ground truth)      │  │
│   │  Must:    Find 3+ specific weaknesses with evidence                  │  │
│   │                                                                       │  │
│   │  Output:                                                              │  │
│   │  {                                                                    │  │
│   │    chain_of_thought: "First I compared... then I noticed...",        │  │
│   │    weaknesses: [                                                      │  │
│   │      { id: "W1", category: "ACCURACY", claim: "...",                 │  │
│   │        evidence: "The output says X but should be Y",                │  │
│   │        severity: 4 }  // 1=Minor, 2=Low, 3=Moderate, 4=Major, 5=Critical │
│   │    ],                                                                 │  │
│   │    strengths: [ { id: "S1", category: "...", description: "..." } ], │  │
│   │    initial_score: 3,  // Critic's preliminary 0-5 score              │  │
│   │    overall_assessment: "The output has X issues..."                  │  │
│   │  }                                                                    │  │
│   └──────────────────────────────────────────────────────────────────────┘  │
│                              ▼                                               │
│   ┌──────────────────────────────────────────────────────────────────────┐  │
│   │  STEP 2: DEFENDER AGENT (Temperature: 0.5 - Balanced)                │  │
│   │  ────────────────────────────────────────────────────────────────────│  │
│   │  Role:    Defend the output - Rebut each weakness from Critic        │  │
│   │  Input:   All of above + Critic's weaknesses[]                       │  │
│   │  Must:    Address EVERY weakness, provide counter-evidence           │  │
│   │  Rules:   - No strawmanning (must address actual claims)             │  │
│   │           - Must concede if weakness is genuinely valid              │  │
│   │                                                                       │  │
│   │  Output:                                                              │  │
│   │  {                                                                    │  │
│   │    defenses: [                                                        │  │
│   │      { weakness_id: "W1",                                            │  │
│   │        verdict: "partially_valid",  // valid|partially_valid|invalid │  │
│   │        rebuttal: "The critic claims X, but actually...",             │  │
│   │        evidence: "The output correctly states...",                   │  │
│   │        concession: "However, I acknowledge that..." }                │  │
│   │    ],                                                                 │  │
│   │    overall_argument: "While there are some issues, the output..."    │  │
│   │  }                                                                    │  │
│   └──────────────────────────────────────────────────────────────────────┘  │
│                              ▼                                               │
│   ┌──────────────────────────────────────────────────────────────────────┐  │
│   │  STEP 3: JUDGE AGENT (Temperature: 0.3 - Consistent)                 │  │
│   │  ────────────────────────────────────────────────────────────────────│  │
│   │  Role:    Neutral arbiter - Score each debated point + final score   │  │
│   │  Input:   Full Critic output + Full Defender output                  │  │
│   │  Method:  PAIRWISE evaluation (score both sides per weakness)        │  │
│   │                                                                       │  │
│   │  Output:                                                              │  │
│   │  {                                                                    │  │
│   │    point_judgments: [                                                 │  │
│   │      { weakness_id: "W1",                                            │  │
│   │        critic_score: 4,      // How strong was Critic's argument     │  │
│   │        defender_score: 2,    // How strong was Defender's rebuttal   │  │
│   │        winner: "critic",     // critic|defender|tie                  │  │
│   │        reasoning: "The Critic correctly identified..." }             │  │
│   │    ],                                                                 │  │
│   │    debate_summary: { critic_wins: 2, defender_wins: 0, ties: 1,      │  │
│   │                      overall_winner: "critic" },                     │  │
│   │    rubric_scores: {          // 0-5 Likert scale each                │  │
│   │      ACCURACY: 3, COMPLETENESS: 2, CLARITY: 3,                       │  │
│   │      RELEVANCE: 4, REASONING: 3                                      │  │
│   │    },                                                                 │  │
│   │    justifications: { ACCURACY: "The output...", ... },               │  │
│   │    dimension_average: 3.0,   // Mean of rubric_scores                │  │
│   │    debate_adjustment: -0.5,  // ±0.5 based on debate winner          │  │
│   │    final_score: 2.5,         // dimension_average + debate_adjustment│  │
│   │    summary: "The response is acceptable but..."                      │  │
│   │  }                                                                    │  │
│   │                                                                       │  │
│   │  FINAL SCORE FORMULA:                                                 │  │
│   │  ┌─────────────────────────────────────────────────────────────────┐ │  │
│   │  │ final_score = dimension_average + debate_adjustment              │ │  │
│   │  │                                                                  │ │  │
│   │  │ debate_adjustment:                                               │ │  │
│   │  │   +0.5  if Defender wins majority of points                     │ │  │
│   │  │   -0.5  if Critic wins majority of points                       │ │  │
│   │  │    0.0  if tie                                                   │ │  │
│   │  └─────────────────────────────────────────────────────────────────┘ │  │
│   └──────────────────────────────────────────────────────────────────────┘  │
│                              ▼                                               │
│   ┌──────────────────────────────────────────────────────────────────────┐  │
│   │  STEP 4: META-JUDGE (Temperature: 0.2 - Very Consistent)             │  │
│   │  ────────────────────────────────────────────────────────────────────│  │
│   │  Role:    Quality control - Detect sycophancy in Judge's evaluation  │  │
│   │  Input:   Full outputs from Critic, Defender, and Judge              │  │
│   │                                                                       │  │
│   │  SYCOPHANCY TRIGGERS (Red Flags):                                    │  │
│   │  • "Both sides made good points" without specifics                   │  │
│   │  • Scores 4-5 while valid weaknesses were identified                 │  │
│   │  • Vague justifications ("good output", "well done")                 │  │
│   │  • Ignored Defender concessions                                      │  │
│   │  • Superlatives without evidence                                     │  │
│   │                                                                       │  │
│   │  Output:                                                              │  │
│   │  {                                                                    │  │
│   │    is_sycophantic: false,                                            │  │
│   │    judgment_quality: 4,      // 0-5 scale                            │  │
│   │    confidence: 0.8,          // judgment_quality / 5.0               │  │
│   │    should_retry: false,      // true if sycophantic OR quality < 3   │  │
│   │    sycophancy_triggers: [],                                          │  │
│   │    recommendation: "accept"  // or "retry"                           │  │
│   │  }                                                                    │  │
│   │                                                                       │  │
│   │  RETRY LOGIC:                                                         │  │
│   │  If should_retry=true → System reruns evaluation (up to 2 retries)   │  │
│   └──────────────────────────────────────────────────────────────────────┘  │
│                              ▼                                               │
│   ┌──────────────────────────────────────────────────────────────────────┐  │
│   │  AGGREGATION (Default: 3 runs)                                       │  │
│   │  ────────────────────────────────────────────────────────────────────│  │
│   │  • Runs full pipeline 3 times                                        │  │
│   │  • Takes MEDIAN of each score (robust to outliers)                   │  │
│   │  • Calculates confidence based on variance:                          │  │
│   │      HIGH   = variance ≤ 0.5 (scores consistent)                     │  │
│   │      MEDIUM = variance ≤ 1.0                                         │  │
│   │      LOW    = variance > 1.0 (scores inconsistent, review manually)  │  │
│   └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Likert Scale (0-5)

| Score | Label | Description | When to Use |
|-------|-------|-------------|-------------|
| **0** | Completely Wrong | Missing, empty, or entirely incorrect | Output is unusable |
| **1** | Major Issues | Fundamental problems, mostly wrong | Core task failed |
| **2** | Significant Problems | Multiple notable issues | Partially addresses task |
| **3** | Acceptable | Usable with some issues | Meets minimum requirements |
| **4** | Good | Minor issues only | Solid output |
| **5** | Excellent | No significant issues | Exceptional quality |

---

## Rubric Dimensions

Each dimension scored 0-5:

| Dimension | Question to Ask |
|-----------|-----------------|
| **ACCURACY** | Is the output factually correct? Does it match ground truth? |
| **COMPLETENESS** | Does it address ALL required aspects? Missing anything? |
| **CLARITY** | Is it well-structured and easy to understand? |
| **RELEVANCE** | Does it stay on topic? Address the actual question? |
| **REASONING** | Is the logic sound? Are decisions justified? |

---

## Module-Specific Critic Categories

The system supports **module-specific critic prompts** with tailored weakness categories. When a module-specific prompt exists (e.g., `critic_m01.md`), it uses specialized categories instead of generic ones.

### Generic Categories (Default)
| Category | What to Look For |
|----------|------------------|
| **ACCURACY** | Factual errors, incorrect information |
| **COMPLETENESS** | Missing important information |
| **CLARITY** | Confusing, ambiguous, poorly organized |
| **RELEVANCE** | Off-topic, doesn't answer the question |

### M01 Categories (Brand Entity Extraction)
| Category | What to Look For |
|----------|------------------|
| **FALSE_POSITIVE** | Extracted non-brand (product type, measurement, material) |
| **FALSE_NEGATIVE** | Missed valid brand entity (brand, manufacturer, sub-brand) |
| **FILTER_VIOLATION** | Exclusion filter not applied correctly |
| **TYPO_ERROR** | Invalid typos (multiple edits, unrealistic) |
| **DEDUPLICATION_ERROR** | Duplicate strings in output |
| **COUNT_VIOLATION** | More than 12 entities |

### M11 Categories (Hard Constraints)
| Category | What to Look For |
|----------|------------------|
| **FALSE_POSITIVE** | Marked something as hard constraint that shouldn't be |
| **FALSE_NEGATIVE** | Missed a genuine hard constraint |
| **REASONING_ERROR** | 3-step test not applied correctly |
| **CATEGORY_CONFUSION** | Confused MECHANISM with QUALITY/DURABILITY |
| **DISTRIBUTION_VIOLATION** | Unreasonable number of constraints |

To add categories for a new module:
1. Create `prompts/critic_{module_id}.md` with module-specific rules
2. Add categories to `MODULE_CATEGORIES` dict in `agents/critic_agent.py`

---

## Usage

### Prerequisites

```bash
pip install openai python-dotenv pyyaml
echo "OPENAI_API_KEY=sk-..." >> .env
```

### Commands

```bash
# Single run (fast, cheap - for development/debugging)
python3 evaluation_KD/multi_agent_eval/run_eval.py --module m11 --single-run --limit 5

# Full evaluation (3 runs + aggregation + meta-judge)
python3 evaluation_KD/multi_agent_eval/run_eval.py --module m11 --limit 10

# Verbose (see all agent outputs)
python3 evaluation_KD/multi_agent_eval/run_eval.py --module m11 --verbose --limit 3

# List available modules
python3 evaluation_KD/multi_agent_eval/run_eval.py --list-modules

# Override model
python3 evaluation_KD/multi_agent_eval/run_eval.py --module m11 --model gpt-4o --limit 5
```

### CLI Options

| Option | Description |
|--------|-------------|
| `--module`, `-m` | Module to evaluate (m01-m16) |
| `--limit`, `-l` | Number of samples to evaluate |
| `--single-run` | Skip aggregation & meta-judge (faster, cheaper) |
| `--verbose`, `-v` | Show detailed agent outputs |
| `--model` | Override model (default: gpt-4o-mini) |
| `--compare-binary` | Compare with binary evaluation results |
| `--list-modules` | Show available modules |

---

## Output Structure

Results saved to: `evaluation_KD/multi_agent_eval/results/`

```json
{
  "experiment": "multi_agent_v1",
  "module": "m11",
  "mode": "aggregated",
  "summary": {
    "total": 10,
    "avg_overall": 3.2,
    "avg_scores": { "accuracy": 3.5, "relevance": 4.0, ... },
    "confidence": { "HIGH": 7, "MEDIUM": 2, "LOW": 1 }
  },
  "results": [
    {
      "sample_id": "B0BQPGJ9LQ",
      "input_data": { ... },
      "output_data": { ... },
      "expected_data": { ... },
      "result": {
        "overall": 2.5,
        "final_score": 2.5,
        "dimension_average": 3.0,
        "debate_adjustment": -0.5,
        "scores": { "accuracy": 3, "relevance": 4, ... },
        "rubric_scores": { "ACCURACY": 3, "RELEVANCE": 4, ... },
        "justifications": { "ACCURACY": "The output...", ... },
        "point_judgments": [ { "weakness_id": "W1", "winner": "critic", ... } ],
        "judge_debate_summary": { "critic_wins": 2, "defender_wins": 0, "ties": 1 },
        "debate": {
          "weaknesses": [ ... ],
          "defenses": [ ... ],
          "chain_of_thought": "..."
        },
        "meta_judge": {
          "is_sycophantic": false,
          "judgment_quality": 4,
          "confidence": 0.8,
          "should_retry": false
        }
      }
    }
  ]
}
```

---

## Dashboard

### Generating Dashboards

Use the dashboard generator to create HTML visualizations from results:

```bash
# Generate dashboard from results JSON
python3 evaluation_KD/multi_agent_eval/generate_dashboard.py \
    evaluation_KD/multi_agent_eval/results/m01_multiagent_aggregated_*.json \
    -o evaluation_KD/multi_agent_eval/dashboards/m01_results.html \
    --open

# With custom config (optional)
python3 evaluation_KD/multi_agent_eval/generate_dashboard.py \
    results/m11_results.json \
    -c config/m11_dashboard_config.yaml \
    -o dashboards/m11_custom.html
```

### Dashboard Generator Options

| Option | Description |
|--------|-------------|
| `-o, --output` | Output HTML file path |
| `-c, --config` | Custom YAML/JSON config file |
| `-m, --module` | Override module ID |
| `-t, --title` | Override dashboard title |
| `--open` | Open in browser after generation |

### Dashboard Features

The generated dashboard includes:
- **Summary tab**: Overall scores, score distribution chart, confidence levels
- **Agent Flow tab**: Visual explanation of the 4-agent pipeline
- **Per-sample details**: Expandable sections showing:
  - **INPUT** (blue box): What each agent received
  - **OUTPUT** (green box): What each agent produced
  - Critic weaknesses with categories and severity
  - Defender rebuttals with verdicts
  - Judge point judgments with winner
  - Meta-Judge sycophancy check results

### Auto-detected Categories

The dashboard generator auto-detects weakness categories from the data, so it works with any module's specific categories without manual configuration.

---

## Quality Assurance

### 1. Calibration (Human Agreement)

Measures if LLM judge agrees with human labels:

```bash
# Create human labels first (see calibration/human_labels_template.csv)
python3 evaluation_KD/multi_agent_eval/calibration/measure_agreement.py \
    --human calibration/human_labels.csv \
    --llm results/m11_multiagent_*.json
```

Target: **85% within ±1 agreement**

### 2. Bias Detection

Detects systematic scoring issues:

```bash
python3 evaluation_KD/multi_agent_eval/calibration/detect_bias.py \
    --results results/m11_multiagent_*.json
```

| Bias | Detection | Fix |
|------|-----------|-----|
| **Leniency** | Mean > 3.5 | Strengthen Critic prompt |
| **Severity** | Mean < 2.5 | Strengthen Defender prompt |
| **Central Tendency** | >80% scores are 2-4 | Add rubric anchoring examples |
| **Dimension Bias** | Spread > 1.5 between dimensions | Review dimension definitions |

### 3. Rubric Anchoring

Concrete examples for each score level per module:
- Location: `config/rubric_anchors_m11.yaml`
- Purpose: Ensures consistent interpretation of scores

---

## Configuration

Edit `config/agent_config.yaml`:

```yaml
models:
  default: "gpt-4o-mini"
  overrides:
    judge: "gpt-4o"  # Use stronger model for judge

temperatures:
  critic: 0.7      # Higher = more creative weakness finding
  defender: 0.5    # Balanced
  judge: 0.3       # Lower = more consistent scoring
  meta_judge: 0.2  # Very low = reliable sycophancy detection

retry:
  max_retries: 2

aggregation:
  num_runs: 3
  method: "median"
```

---

## File Structure

```
evaluation_KD/multi_agent_eval/
├── run_eval.py                     # CLI entry point
├── generate_dashboard.py           # Dashboard generator from results JSON
├── Adversarial_Debate_Evaluation_System.md  # This documentation
│
├── agents/
│   ├── __init__.py
│   ├── base_agent.py               # Abstract base class, LLM client
│   ├── input_filter.py             # Step 0: Security/injection check
│   ├── critic_agent.py             # Step 1: Find weaknesses (+ MODULE_CATEGORIES)
│   ├── defender_agent.py           # Step 2: Rebut weaknesses
│   ├── judge_agent.py              # Step 3: Score debate
│   └── meta_judge.py               # Step 4: Sycophancy detection
│
├── pipeline/
│   ├── __init__.py
│   ├── orchestrator.py             # Coordinates full pipeline
│   ├── aggregator.py               # 3-run aggregation with median
│   └── retry_handler.py            # Retry logic on sycophancy
│
├── prompts/
│   ├── critic.md                   # Generic critic prompt template
│   ├── critic_m01.md               # M01-specific critic (brand extraction)
│   ├── critic_m11.md               # M11-specific critic (hard constraints)
│   ├── m11_context.md              # M11 module context/rules
│   ├── defender.md                 # Defender prompt template
│   ├── judge.md                    # Judge prompt template
│   └── meta_judge.md               # Meta-judge prompt template
│
├── config/
│   ├── agent_config.yaml           # Models, temperatures, injection patterns
│   ├── likert_rubrics.yaml         # Scoring criteria definitions
│   └── rubric_anchors_m11.yaml     # Concrete score examples for M11
│
├── calibration/
│   ├── measure_agreement.py        # Human vs LLM agreement
│   ├── detect_bias.py              # Bias detection
│   └── human_labels_template.csv   # Template for human labels
│
├── results/                        # Output JSON files
│   └── {module}_multiagent_{mode}_{timestamp}.json
│
└── dashboards/                     # Generated HTML dashboards
    └── {module}_results.html
```

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **4 agents instead of 1** | Reduces single-judge bias, enables debate |
| **Adversarial structure** | Critic attacks, Defender defends → balanced evaluation |
| **Temperature gradient** | Critic creative (0.7) → Judge consistent (0.3) |
| **Pairwise scoring** | Judge scores both sides per point → fair comparison |
| **Meta-judge** | Catches sycophancy that single judges miss |
| **3-run aggregation** | Median reduces noise, variance indicates confidence |
| **Debate adjustment ±0.5** | Final score reflects debate outcome, not just rubric |

---

## Interpreting Results

| Scenario | What It Means |
|----------|---------------|
| `final_score: 2.5, debate_adjustment: -0.5` | Output scored 3.0 on rubric, but Critic won debate → penalized |
| `confidence: HIGH` | All 3 runs agreed (variance ≤ 0.5) |
| `confidence: LOW` | Runs disagreed significantly → review manually |
| `is_sycophantic: true` | Judge was too lenient, results may be inflated |
| `critic_wins: 3, defender_wins: 0` | Critic's weaknesses were all valid → output has real issues |
| `defender_wins: 3, critic_wins: 0` | Critic's claims were mostly unfounded → output is solid |

---

## Adding a New Module

To add evaluation support for a new module:

### 1. Add Module to CSV Map

In `run_eval.py`, add entry to `MODULE_CSV_MAP`:

```python
'm08': {
    'folder': 'M08_AssignAttributeRanks',
    'file': 'M08_AssignAttributeRanks_v1_150126_1.csv',
    'rubrics': 'M08',
},
```

### 2. Create Module-Specific Critic Prompt (Optional but Recommended)

Create `prompts/critic_{module_id}.md` with:
- Module-specific rules the critic should check
- Custom weakness categories relevant to the module
- Severity scale calibrated for this module's task
- Examples of common errors

### 3. Register Module Categories

In `agents/critic_agent.py`, add to `MODULE_CATEGORIES`:

```python
M08_CATEGORIES = [
    "MISSING_ATTRIBUTE",
    "EXTRA_ATTRIBUTE",
    "RANK_VIOLATION",
    "COLOR_PRIORITY_ERROR",
    "AUDIENCE_ERROR",
    "HIERARCHY_VIOLATION",
]

MODULE_CATEGORIES = {
    "m11": M11_CATEGORIES,
    "m01": M01_CATEGORIES,
    "m08": M08_CATEGORIES,  # Add new module
}
```

### 4. Run Evaluation

```bash
python3 evaluation_KD/multi_agent_eval/run_eval.py --module m08 --limit 10
```

### 5. Generate Dashboard

```bash
python3 evaluation_KD/multi_agent_eval/generate_dashboard.py \
    results/m08_multiagent_aggregated_*.json \
    -o dashboards/m08_results.html --open
```
