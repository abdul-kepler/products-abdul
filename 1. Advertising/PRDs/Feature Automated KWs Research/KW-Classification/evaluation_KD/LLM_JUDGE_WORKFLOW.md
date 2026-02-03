# LLM-as-a-Judge Evaluation Workflow

> **This is the REFERENCE DOCUMENT** for the LLM-as-a-Judge evaluation workflow.
>
> **For execution instructions, see:** `evaluation_KD/agents/00_orchestrator.md`

---

## Quick Start

### For Claude (Orchestrator)
When asked to run the evaluation workflow:
1. Read `evaluation_KD/agents/00_orchestrator.md` for execution instructions
2. Follow the agent workflow with verification at each step
3. Use this document as reference for details

### Key Commands
```bash
# Run evaluation (15 samples for validation)
python3 evaluation_KD/evaluation_experimentV3/run_evaluation_v2.py --module <MODULE> --limit 15

# Regenerate dashboards
python3 evaluation_KD/evaluation_experimentV3/generate_dashboard_v2.py --no-open
```

---

## Critical Rule: Rubrics Must Match Prompts

> **NEVER change a rubric to "fix" a failing evaluation unless the rubric contradicts the prompt.**

| Scenario | Root Cause | Action |
|----------|------------|--------|
| Rubric says X, Prompt says X, Model does Y | **Model Issue** | Investigate model/prompt, NOT rubric |
| Rubric says X, Prompt says Y | **Judge Issue** | Fix rubric to match prompt |
| Rubric says X, Prompt unclear | **Prompt Issue** | Clarify prompt first |

**WRONG:** "Rubric is too strict, let me make it flexible"
**RIGHT:** "Does the rubric match the prompt? If yes, why isn't model following the prompt?"

---

## Agent Architecture

This workflow is executed by specialized agents coordinated by the Orchestrator.

| Agent | File | Responsibility |
|-------|------|----------------|
| **Orchestrator** | `00_orchestrator.md` | **Execution instructions** - How to run the workflow |
| **Evaluation Runner** | `01_evaluation_runner.md` | Run evaluations, collect pass/fail results |
| **Prompt Analyzer** | `02_prompt_analyzer.md` | Read prompts, extract requirements |
| **Rubric Validator** | `03_rubric_validator.md` | Compare rubrics vs prompts, classify issues |
| **Validation Experimenter** | `04_validation_experimenter.md` | Run 15x validation for Judge Issues (rubric fixes) |
| **Prompt Improver** | `08_prompt_improver.md` | Run 15 iterations for Model Issues (prompt improvements) |
| **Suggestion Generator** | `05_suggestion_generator.md` | Create improvement suggestions |
| **Dashboard Generator** | `06_dashboard_generator.md` | Generate HTML dashboards |
| **Rubric Updater** | `07_rubric_updater.md` | Update rubrics (with user approval) |

See `evaluation_KD/agents/README.md` for full agent documentation.

---

## File Locations

| File | Path |
|------|------|
| **Orchestrator instructions** | `evaluation_KD/agents/00_orchestrator.md` |
| **Agent definitions** | `evaluation_KD/agents/*.md` |
| **Rubric config** | `evaluation_KD/config/rubrics_v3.yaml` |
| Evaluation script | `evaluation_KD/evaluation_experimentV3/run_evaluation_v2.py` |
| Dashboard generator | `evaluation_KD/evaluation_experimentV3/generate_dashboard_v2.py` |
| Improvement suggestions | `evaluation_KD/evaluation_experimentV3/improvement_suggestions.json` |
| Output dashboards | `evaluation_KD/evaluation_experimentV3/dashboards/` |
| Prompts | `prompts/modules/*.md` |

---

## Experiment Folder Management

### Folder Structure

All experiments are stored in `evaluation_KD/` with the naming convention `evaluation_experimentVX`:

```
evaluation_KD/
├── evaluation_experimentV1/    # First experiment
├── evaluation_experimentV2/    # Second experiment
├── evaluation_experimentV3/    # Current experiment (rubrics v3)
└── config/
    ├── rubrics_v2.yaml
    └── rubrics_v3.yaml
```

### Standard Experiment Folder Structure

Each experiment folder MUST contain:

```
evaluation_experimentVX/
├── dashboards/                 # Generated HTML dashboards
│   ├── SUMMARY_DASHBOARD.html
│   ├── MATCH_RATE_DASHBOARD.html
│   └── MODULE_ANALYSIS_DASHBOARD.html
├── judge_results/              # JSON evaluation results
│   └── <module>_judge_<timestamp>.json
├── config/                     # Experiment-specific config (optional)
├── improvement_suggestions.json  # Claude curated suggestions
├── run_evaluation_v2.py        # Evaluation script
└── generate_dashboard_v2.py    # Dashboard generator
```

### Creating a New Experiment

When starting a new evaluation cycle:

1. **Create new folder:**
   ```bash
   mkdir -p evaluation_KD/evaluation_experimentVX/{dashboards,judge_results,config}
   ```

2. **Copy scripts from previous experiment:**
   ```bash
   cp evaluation_KD/evaluation_experimentV3/run_evaluation_v2.py evaluation_KD/evaluation_experimentVX/
   cp evaluation_KD/evaluation_experimentV3/generate_dashboard_v2.py evaluation_KD/evaluation_experimentVX/
   ```

3. **Create new rubrics version (if needed):**
   ```bash
   cp evaluation_KD/config/rubrics_v3.yaml evaluation_KD/config/rubrics_v4.yaml
   # Update version metadata in the new file
   ```

4. **Update script paths** to point to new experiment folder

### Current Active Experiment

> **CURRENT:** `evaluation_experimentV3` with `rubrics_v3.yaml`
>
> **TRIGGER:** Say "Kate's evaluation experiment" to create a new experiment version.

Update this section when starting a new experiment version.

---

## Overview

This document describes the workflow for running LLM-as-a-Judge evaluations on module outputs. Follow these steps to evaluate prompt quality and identify rubric issues.

---

## Step 1: Run the Evaluation Script

### Command Syntax

```bash
# For V2 experiments (recommended)
python3 evaluation_experimentV2/run_evaluation_v2.py --module <MODULE> --limit <SAMPLES>

# Legacy path (V1)
python3 evaluation/run_llm_judge.py --module <MODULE> --limit <SAMPLES>
```

### Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `--module` / `-m` | Module to evaluate (m01, m01a, m01b) | `--module m01` |
| `--limit` / `-l` | Number of samples to evaluate | `--limit 20` |
| `--rubric` / `-r` | (Optional) Specific rubric to evaluate | `--rubric M01_no_duplicates` |
| `--model` | (Optional) Model for judge (default: gpt-4o-mini) | `--model gpt-4o-mini` |

### Examples

```bash
# Run all rubrics on 20 samples for M01
python3 evaluation/run_llm_judge.py --module m01 --limit 20

# Run specific rubric only
python3 evaluation/run_llm_judge.py --module m01 --rubric M01_no_product_words --limit 20

# List available rubrics for a module
python3 evaluation/run_llm_judge.py --module m01 --list-rubrics
```

### Output

Results are saved to: `evaluation/judge_results/<module>_judge_<timestamp>.json`

---

## Step 2: Generate HTML Report

### Command

```bash
python3 evaluation/generate_judge_report.py <MODULE>
```

### Example

```bash
python3 evaluation/generate_judge_report.py m01
```

### Output

Report saved to: `evaluation/judge_report_<module>.html`

### Report Features

- **Summary Cards**: Total evaluations, Pass/Fail counts, Pass Rate
- **By Rubric View**: Expandable sections for each rubric
- **By Sample View**: See all rubrics for each ASIN
- **Match Indicator**: Shows if Expected matches Actual output
  - ✓ MATCH (green) - Exact match
  - ◐ X% Match (orange) - Partial overlap
  - ✗ MISMATCH (red) - No overlap
- **Input Data**: Collapsible section with brand_name, title
- **Expected vs Actual**: Side-by-side JSON comparison
- **Judge Reasoning**: Full explanation from GPT-4o mini

---

## Step 3: Analyze Results - Check for Rubric Issues

### Rule: If a rubric fails > 50%, investigate for contradiction

When a rubric has a pass rate below 50%, it may indicate the rubric contradicts the prompt's intended behavior.

### Investigation Process

#### 3.1 Identify the Failing Rubric

Look at the summary in the terminal output or HTML report:

```
SUMMARY
============================================================
Total evaluations: 100
PASS: 58
FAIL: 42
Pass Rate: 58.0%
```

Or check individual rubric pass rates in the HTML report.

#### 3.2 Read the Prompt

Open the prompt file for the module:

```bash
# M01 prompt location
cat prompts/modules/m01_extract_own_brand_entities.md
```

#### 3.3 Compare Rubric vs Prompt

**Check if the rubric contradicts what the prompt asks the model to do.**

### Common Contradiction Patterns

| Contradiction Type | Example | Fix |
|-------------------|---------|-----|
| **Rubric forbids what prompt requires** | Prompt asks for typos, rubric marks typos as "hallucination" | Update rubric to allow typo variations |
| **Rubric is too strict** | Prompt allows case variations, rubric marks them as "duplicates" | Clarify that case variations are valid |
| **Rubric misunderstands output** | Prompt generates variations, rubric expects exact matches | Adjust rubric criteria |

### Example: M01 Rubric Fixes

**Problem 1: No Hallucination (5% pass rate)**

```
Prompt says:
  "### Step 2: Generate Typos (MANDATORY - 3-5 per brand)
   For EACH brand element, you MUST generate common customer misspellings"

Rubric said:
  FAIL: "Output contains brand not found in title or listing_brand"

Contradiction: Typos like "Owalaa" won't exist in input - they're generated!

Fix:
  FAIL: "Output contains a completely different brand not related to input"
  PASS: "Typos/variations are clearly derived from the input brand"
```

**Problem 2: No Duplicates (25% pass rate)**

```
Prompt says:
  "| Case variation | All lowercase: Owala→`owala`, JBL→`jbl` |"

Rubric said:
  FAIL: "Same entity appears more than once"

Contradiction: "JBL" and "jbl" are different variations, not duplicates!

Fix:
  FAIL: "Exact same string appears more than once (e.g., 'JBL', 'JBL')"
  PASS: "Case variations are different entries, not duplicates"
```

---

## Step 4: Update Rubrics (After User Approval)

> **IMPORTANT**: Do NOT update rubrics automatically. Always present findings to the user and wait for approval before making changes.

### 4.1 Present Findings to User

When a rubric fails > 50%, prepare a summary:

```
RUBRIC ISSUE FOUND: M01_no_hallucination (5% pass rate)

PROMPT SAYS:
  "Generate Typos (MANDATORY - 3-5 per brand)"

CURRENT RUBRIC SAYS:
  FAIL: "Output contains brand not found in title or listing_brand"

CONTRADICTION:
  The prompt requires generating typos like "Owalaa" which won't exist
  in the input. The rubric incorrectly marks these as hallucinations.

SUGGESTED FIX:
  FAIL: "Output contains a completely different brand not related to input"
  PASS: "Typos/variations clearly derived from the input brand"

Do you want me to update this rubric?
```

### 4.2 Wait for User Approval

- **User approves** → Proceed to update rubrics
- **User declines** → Keep rubric as-is, document the issue
- **User suggests changes** → Incorporate feedback into the fix

### Files to Update (After Approval)

1. **`evaluation_KD/config/rubrics_v2.yaml`** - Main rubric definitions (YAML config)
2. After updating YAML, regenerate HTML: `python3 evaluation/generate_interactive_report.py`

> **Note**: Rubric definitions are stored in YAML config file. The Python scripts read from this file.

### Rubric Structure (YAML Format)

```yaml
M01_no_hallucination:
  module: "M01"
  criterion: "No Hallucination"
  check: "Base brand must come from input; typos must be variations of that brand"
  codeBased: false
  fail_definition: |
    - Output contains a completely different brand not related to input
    - Brand name invented from scratch
  pass_definition: |
    - All base brands traceable to input data
    - Typos/variations clearly derived from input brand
```

### After Updating

1. Regenerate the interactive rubrics HTML:
   ```bash
   python3 evaluation/generate_interactive_report.py
   ```

2. Re-run the evaluation to verify improvement:
   ```bash
   python3 evaluation/run_llm_judge.py --module m01 --limit 20
   ```

3. Regenerate the judge report:
   ```bash
   python3 evaluation/generate_judge_report.py m01
   ```

---

## Step 5: Generate Improvement Suggestions

> **PURPOSE**: Create detailed, actionable improvement suggestions for failing rubrics that can be validated through experiments.

### 5.1 Identify Failing Rubrics

From the evaluation results, identify rubrics with <50% pass rate:

| Pass Rate | Criticality | Priority |
|-----------|-------------|----------|
| <20% | Critical | Investigate immediately |
| 20-35% | High | High priority |
| 35-50% | Medium | Address after critical/high |
| >50% | Low | Monitor, not urgent |

### 5.2 Classify the Issue Type

For each failing rubric, determine the root cause:

| Issue Type | Description | Example |
|------------|-------------|---------|
| **Prompt Issue** | Prompt instructions cause incorrect output | Prompt says "generate 15-30 entities" but rubric expects 5-10 |
| **Judge Issue** | Rubric contradicts prompt behavior | Rubric marks typos as "hallucination" but prompt requires typos |
| **Model Issue** | Model fails despite correct prompt | Model ignores clear instructions |

### 5.3 Investigation Process

For each failing rubric:

1. **Read the prompt file**:
   ```bash
   cat prompts/modules/m01_extract_own_brand_entities.md
   ```

2. **Compare rubric vs prompt**:
   - What does the prompt ask the model to do?
   - What does the rubric check for?
   - Is there a contradiction?

3. **Analyze failing samples**:
   - Look at expected vs actual outputs
   - Identify patterns in failures
   - Note specific examples

### 5.4 Run Validation Experiments (15x Rule)

> **CRITICAL**: Before documenting any improvement suggestion, you MUST run the proposed fix **15 times** using GPT to validate it works consistently.

#### Validation Protocol

1. **Select 15 failing samples** from the module
2. **Run ORIGINAL prompt** on all 15 samples → Record baseline pass rate
3. **Apply the proposed fix** to the prompt
4. **Run FIXED prompt** on the same 15 samples → Record new pass rate
5. **Compare results** to determine if the fix is effective

#### Required Metrics

| Metric | How to Calculate |
|--------|------------------|
| Baseline Pass Rate | (Original passes / 15) × 100% |
| Fixed Pass Rate | (Fixed passes / 15) × 100% |
| Improvement | Fixed Pass Rate - Baseline Pass Rate |
| Consistency | Did improvement hold across all 15 runs? |

#### Example Validation Run

```bash
# Step 1: Run original prompt on 15 samples
python3 evaluation/run_llm_judge.py --module m01 --limit 15
# Result: 5/15 passed (33%)

# Step 2: Apply fix to prompt file
# Edit: prompts/modules/m01_extract_own_brand_entities.md

# Step 3: Run fixed prompt on same 15 samples
python3 evaluation/run_llm_judge.py --module m01 --limit 15
# Result: 12/15 passed (80%)

# Step 4: Calculate improvement
# Improvement: 80% - 33% = +47%
```

#### Validation Thresholds

| Improvement | Status | Action |
|-------------|--------|--------|
| ≥20% improvement | ✅ VALIDATED | Document as validated fix |
| 10-19% improvement | ⚠️ PARTIAL | Document but note limited impact |
| <10% improvement | ❌ NOT EFFECTIVE | Do not document, investigate further |
| Inconsistent results | 🔍 INVESTIGATING | Run more samples, check for edge cases |

#### What to Record

After running 15x validation, record:

```javascript
{
    experimentDate: "2026-01-16",
    experimentModel: "gpt-4o-mini",
    samplesTested: 15,
    testResults: "Original: 5/15 (33%), With fix: 12/15 (80%)",
    validated: true  // Only if ≥20% improvement
}
```

### 5.4a Run 15 Iterations for Model Issues (see 08-prompt-improver.md)

> **For Model Issues ONLY**: When the rubric matches the prompt but the model fails, use iterative prompt improvement.

#### The 15-Iteration Loop

Unlike the 15x validation (which tests ONE fix 15 times), this runs **15 different iterations** of improvement:

```
Iteration 1: Analyze baseline → Improve rule → Test → Record results
Iteration 2: Analyze what still fails → Improve rule again → Test → Record
Iteration 3: ... continue analyzing and improving ...
...
Iteration 15: Final improvement attempt
```

#### Iteration Protocol

1. **Read the current prompt** and identify the failing rule
2. **Analyze failures** - Why is the model not following the rule?
3. **Improve the rule** (do NOT add dataset samples - improve the LOGIC only)
4. **Test on 5 samples** - Run evaluation
5. **Analyze results** - Did it improve? What still fails?
6. **Repeat** - 15 iterations total
7. **Report best version** - Which iteration performed best?

#### Rules for Improving Prompts

**DO:**
- Improve rule logic and instructions
- Make rules clearer and more specific
- Add explicit constraints or conditions
- Restructure confusing sections

**DO NOT:**
- Add samples from the test dataset
- Hardcode specific keywords or values
- Add exceptions for specific test cases

#### What to Record (Each Iteration)

```javascript
{
    iteration: 3,
    changeDescription: "Added explicit FAIL conditions for generic descriptors",
    changeLocation: "Section: Amazon Test Rules",
    oldText: "Apply the Amazon Test to each entity",
    newText: "FAIL the Amazon Test if: The term is a generic descriptor...",
    passRate: 27,
    samplesTested: 5,
    analysis: "Improved +14%. Model now excludes generic descriptors."
}
```

#### Final Output

```javascript
{
    module: "M01",
    rubric: "Amazon Test Applied",
    totalIterations: 15,
    bestIteration: 8,
    progression: [7, 13, 27, 33, 40, 47, 53, 67, 60, 60, 67, 67, 67, 67, 67],
    baselinePassRate: 7,
    bestPassRate: 67,
    improvement: "+60%",
    validated: true,
    recommendedPromptChanges: {
        file: "prompts/modules/m01_extract_own_brand_entities.md",
        oldText: "...",
        newText: "..."
    }
}
```

### 5.5 Document the Improvement Suggestion

Create a detailed suggestion with this structure:

```javascript
{
    module: "M10",
    criticality: "Critical",  // Critical, High, Medium, Low
    passRate: 13,

    // Issue Classification
    issueType: "Prompt Issue",  // Prompt Issue, Judge Issue, Model Issue
    analysisSummary: "✅ VALIDATED - null output + format issue",

    // Problem Description
    specificIssue: "Model returns null for 7/10 samples when input is empty/unclear",
    expectedOutput: '"organizing kitchen sink items", "making ice cubes"',
    actualOutput: 'null, "portable drink storage"',

    // Solution
    detailedSuggestion: "VALIDATED FIX: Combined null-handling fallback + strict adjective removal",

    // Specific Prompt Changes (with file location)
    promptChange: `
        <div style="background:#e8f5e9;padding:10px;">
            <strong>✅ EXPERIMENT RESULTS</strong>
            • Model: gpt-4o-mini
            • Samples tested: 10
            • Original: 7/10 passed (70%)
            • With fix: 9/10 passed (90%)
            • Improvement: +20%
        </div>

        <strong>📍 ACTION: ADD NEW SECTION</strong>
        File: m10_validate_primary_intended_use_v1.1.md
        Location: BEFORE "## Output Format" section

        <pre>
        ## MANDATORY: Handle Null/Invalid Input

        **RULE: This module MUST ALWAYS output a valid result.**

        When Input is Null/Empty:
        1. DO NOT return null
        2. DO derive from product context
        </pre>
    `,

    // Validation Results
    impact: "✅ VALIDATED: 9/10 samples passed (90%) vs 7/10 baseline (70%)",
    validated: true,
    experimentDate: "2026-01-15",
    experimentModel: "gpt-4o-mini",
    samplesTested: 10,
    testResults: "Original: 7/10 (70%), With fix: 9/10 (90%)"
}
```

### 5.6 Suggestion Status Labels

Use these status indicators:

| Status | Label | Meaning |
|--------|-------|---------|
| ✅ VALIDATED | `validated: true` | Fix tested and confirmed working |
| ⏳ PENDING | `validated: false` | Proposed but not yet tested |
| ⚠️ PARTIAL | `validated: true` | Fix helps but doesn't fully solve |
| 🔍 INVESTIGATING | `validated: false` | Root cause still being analyzed |

### 5.7 Prompt Change Documentation Format

When documenting prompt changes, include:

1. **Experiment Results Box**:
   ```
   ✅ EXPERIMENT RESULTS
   • Model: gpt-4o-mini
   • Samples tested: 10
   • Original: 7/10 passed (70%)
   • With fix: 9/10 passed (90%)
   • Improvement: +20%
   ```

2. **Action Location**:
   ```
   📍 ACTION: ADD/MODIFY/REMOVE SECTION
   File: <prompt_file.md>
   Location: <where in the file>
   ```

3. **Specific Changes** (OLD vs NEW):
   ```
   OLD: "Aim for 15-30 competitor entities"
   NEW: "STRICT LIMIT: Maximum 10 distinct brands"
   ```

4. **New Content to Add** (if applicable):
   ```
   ## NEW SECTION: Handle Edge Case

   When X happens:
   1. Do Y
   2. Do Z
   ```

### 5.8 Update Dashboard with Suggestions

After documenting suggestions, regenerate the dashboard:

```bash
python3 evaluation_experimentV2/generate_dashboard_v2.py
```

The MODULE_ANALYSIS_DASHBOARD will display suggestions in the "Improvement Suggestions" section.

---

## Quick Reference Commands

```bash
# Full evaluation workflow (single module)
python3 evaluation/run_llm_judge.py --module m01 --limit 20
python3 evaluation/generate_judge_report.py m01

# Run ALL modules (M01-M16)
python3 evaluation/run_llm_judge.py --module all --limit 10

# List available rubric versions
python3 evaluation/run_llm_judge.py --list-versions

# Use specific rubric version
python3 evaluation/run_llm_judge.py --module m01 --rubrics-version v2 --limit 20

# List rubrics for a module (with version)
python3 evaluation/run_llm_judge.py --module m01 --list-rubrics --rubrics-version v2

# Test single rubric
python3 evaluation/run_llm_judge.py --module m01 --rubric M01_no_duplicates --limit 10

# Regenerate rubrics HTML (after editing)
python3 evaluation/generate_interactive_report.py
```

### Run All Modules Example

```bash
# Run complete evaluation flow for new experiment version
python3 evaluation/run_llm_judge.py --module all --limit 10 --rubrics-version v2

# Output:
# INFO: Loading rubrics from rubrics_v2.yaml
# INFO: Rubrics version 2.4
# INFO: Loaded 18 modules, 69 rubrics
#
# ============================================================
# RUNNING ALL MODULES (M01-M16)
# Rubrics Version: v2
# ============================================================
#
# ... evaluates each module ...
#
# ============================================================
# ALL MODULES SUMMARY
# ============================================================
#   M01: 75.0%
#   M01A: 80.0%
#   ...
#   M16: 85.0%
```

---

## File Locations

| File | Purpose |
|------|---------|
| `evaluation_KD/agents/*.md` | **Agent definitions for workflow automation** |
| `evaluation_KD/config/rubrics_v2.yaml` | **Rubric definitions (source of truth)** |
| `evaluation_experimentV2/run_evaluation_v2.py` | Main evaluation script (V2) |
| `evaluation_experimentV2/generate_dashboard_v2.py` | Dashboard generator (V2) |
| `evaluation_experimentV2/improvement_suggestions.json` | Claude curated improvement suggestions |
| `evaluation_experimentV2/judge_results/` | JSON evaluation results (V2) |
| `evaluation_experimentV2/dashboards/` | Generated dashboards (V2) |
| `evaluation/run_llm_judge.py` | Legacy evaluation script (V1) |
| `evaluation/generate_judge_report.py` | HTML report generator |
| `evaluation/generate_interactive_report.py` | Interactive rubrics HTML generator |
| `evaluation/judge_results/` | JSON evaluation results (V1) |
| `prompts/modules/` | Prompt files to check against rubrics |
| `datasets/` | Expected outputs (ground truth) |
| `batch_requests/*/results/` | Actual module outputs |

---

---

## Dashboard Data Sourcing Requirements

> **CRITICAL**: All dashboard data MUST be pulled dynamically from experiment results. Never use hardcoded static data.

### Versioning Rule

**Each experiment version gets its own dashboards.** When running a new experiment version:

1. **Create NEW dashboard files** with version/timestamp suffix
2. **Do NOT overwrite** previous experiment dashboards
3. **Store in version-specific folder** or use naming convention

```
evaluation_experimentV1/dashboards/           # Experiment V1 dashboards
evaluation_experimentV2/dashboards/           # Experiment V2 dashboards (NEW)

# OR use naming convention:
dashboards/MATCH_RATE_DASHBOARD_v1.html
dashboards/MATCH_RATE_DASHBOARD_v2.html       # NEW version
dashboards/MATCH_RATE_DASHBOARD_20260115.html # Timestamped
```

### Dashboard Generation Workflow

When starting a **new experiment version**:

```bash
# 1. Run evaluation for new experiment
python3 evaluation/run_llm_judge.py --module all --experiment-version v2

# 2. Generate NEW dashboards (creates new files, doesn't overwrite)
python3 evaluation/generate_dashboards.py --version v2 --output evaluation_experimentV2/dashboards/

# 3. Result: New dashboard files created
#    - evaluation_experimentV2/dashboards/MATCH_RATE_DASHBOARD.html
#    - evaluation_experimentV2/dashboards/MODULE_ANALYSIS_DASHBOARD.html
#    - evaluation_experimentV2/dashboards/FAILURE_ANALYSIS_DASHBOARD.html
```

### Data Source Hierarchy

All dashboards should load data from these sources in order of preference:

| Priority | Source | Location | Description |
|----------|--------|----------|-------------|
| 1 | Latest Judge Results | `evaluation/judge_results/*_judge_*.json` | Most recent LLM-as-a-Judge evaluation |
| 2 | Latest Experiment Results | `evaluation/experiment_results/*.json` | Iterative experiment outputs |
| 3 | Evaluation Spreadsheet | `evaluation/evaluation_reports/*.csv` | Full evaluation CSVs |
| 4 | Batch Results | `batch_requests/*/results/*.jsonl` | Raw module outputs |

### Implementation Requirements

When creating or updating dashboards:

1. **Auto-detect latest files**: Use timestamp patterns to find most recent results
   ```javascript
   // Example: Find latest judge results
   const latestFile = files.sort((a, b) =>
       b.match(/(\d{8}_\d{6})/)[1].localeCompare(a.match(/(\d{8}_\d{6})/)[1])
   )[0];
   ```

2. **Load data dynamically**: Dashboards should either:
   - Fetch JSON data via script at page load
   - Be regenerated by a Python script that reads latest results
   - Use a data file that gets updated when new experiments run

3. **Show data source metadata**: Always display:
   - Source file name
   - Timestamp of data
   - Sample count
   - Experiment/batch ID

4. **Update on experiment completion**: After running evaluations, regenerate dashboards:
   ```bash
   # After running evaluation
   python3 evaluation/run_llm_judge.py --module m01 --limit 20

   # Regenerate dashboards with latest data
   python3 evaluation/generate_dashboard.py --type match-rate
   python3 evaluation/generate_dashboard.py --type module-analysis
   ```

### Dashboard Generator Script Pattern

All dashboard generators should follow this pattern:

```python
def load_latest_results(module: str) -> dict:
    """Load most recent judge results for a module."""
    results_dir = Path("evaluation/judge_results")
    pattern = f"{module}_judge_*.json"
    files = sorted(results_dir.glob(pattern), reverse=True)

    if not files:
        raise FileNotFoundError(f"No results for {module}")

    latest = files[0]
    print(f"Loading data from: {latest.name}")

    with open(latest) as f:
        return json.load(f)

def generate_dashboard(output_path: str):
    """Generate dashboard with latest data."""
    # Load ALL module results
    all_data = {}
    for module in ['m01', 'm01a', 'm01b', 'm02', ...]:
        try:
            all_data[module] = load_latest_results(module)
        except FileNotFoundError:
            print(f"Warning: No data for {module}")

    # Generate HTML with embedded data
    html = render_dashboard_template(all_data)

    # Add metadata
    html = add_data_source_info(html, all_data)

    with open(output_path, 'w') as f:
        f.write(html)
```

### Required Data Source Display

Every dashboard MUST show this information block:

```html
<div class="data-source-info">
    <strong>Data Source:</strong> judge_results/m01_judge_20260115_143022.json
    <br>
    <strong>Generated:</strong> 2026-01-15 14:35:00
    <br>
    <strong>Samples:</strong> 280 across 19 modules
    <br>
    <strong>Rubrics Version:</strong> v2.4
</div>
```

### Dashboards That Need Dynamic Data

| Dashboard | Data Source | Generator Script |
|-----------|-------------|------------------|
| `MATCH_RATE_DASHBOARD.html` | judge_results/*.json | `generate_match_rate_dashboard.py` |
| `MODULE_ANALYSIS_DASHBOARD.html` | experiment_results/*.json | `generate_module_dashboard.py` |
| `interactive_rubrics.html` | config/rubrics_v2.yaml | `generate_interactive_report.py` |
| `judge_report_*.html` | judge_results/*.json | `generate_judge_report.py` |

### Dashboard Format Requirements

> **CRITICAL**: All dashboards MUST use the **V1 FORMAT** (styling, layout, charts) but populated with **DATA FROM THE CURRENT EXPERIMENT**.

#### What This Means

| Aspect | Source |
|--------|--------|
| **FORMAT** (HTML/CSS/JS structure, styling, layout, chart types) | Copy from V1 reference templates |
| **DATA** (pass rates, evaluations, module results, samples) | Load dynamically from latest experiment's `judge_results/*.json` |

#### Reference Templates (FORMAT ONLY - do not copy data)

| Dashboard | Reference Template |
|-----------|-------------------|
| `MATCH_RATE_DASHBOARD.html` | `evaluation_KD/evaluation_experimentV1/dashboards/MATCH_RATE_DASHBOARD.html` |
| `MODULE_ANALYSIS_DASHBOARD.html` | `evaluation_KD/evaluation_experimentV1/dashboards/MODULE_ANALYSIS_DASHBOARD.html` |

#### Format Requirements (from V1 templates):

1. **Light Theme**: Background `#f5f7fa`, white cards with subtle shadows
2. **Chart.js Library**: Use `<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>`
3. **Stacked Bar Charts**: For match rate visualization with colors:
   - Exact Match: `#27ae60` (green)
   - Semantic Match: `#3498db` (blue)
   - Mismatch: `#e74c3c` (red)
4. **Sidebar Navigation**: MODULE_ANALYSIS_DASHBOARD uses fixed sidebar with module list sorted by pass rate
5. **Color-coded Badges**: Pass rate badges use:
   - `rate-critical` (red) for <40%
   - `rate-warning` (orange) for 40-60%
   - `rate-good` (teal) for 60-80%
   - `rate-excellent` (green) for >80%
6. **Sortable Tables**: Include column sort functionality
7. **Failure Analysis**: Pie/doughnut charts for root cause breakdown
8. **Improvement Suggestions**: Detailed cards with prompt change recommendations

#### Data Requirements (from current experiment):

1. **Load from latest judge results**: `evaluation_experimentV2/judge_results/*.json` (or current experiment folder)
2. **Include all evaluated modules**: Display only modules that have judge results
3. **Show actual pass/fail counts**: From the experiment's evaluation data
4. **Display real timestamps**: From when evaluations were run
5. **Use real sample data**: Expected vs actual outputs from the experiment

**IMPORTANT**:
- Copy the V1 HTML/CSS/JS structure EXACTLY
- Replace ALL hardcoded data with dynamically loaded data from the current experiment
- Never use V1's data values - only use V1's visual format

### Validation Checklist for Dashboards

Before committing any dashboard changes:

- [ ] Data is loaded from files, not hardcoded
- [ ] Latest file detection logic works correctly
- [ ] Data source metadata is displayed
- [ ] Dashboard regenerates correctly with new data
- [ ] Timestamp in dashboard matches source file timestamp

---

## Checklist

- [ ] **Step 1**: Run evaluation with `run_llm_judge.py`
- [ ] **Step 2**: Generate HTML report with `generate_judge_report.py`
- [ ] **Step 3**: Analyze results - Check pass rates for each rubric
- [ ] **Step 4**: If any rubric < 50% pass rate (rubric issue):
  - [ ] Read the prompt file
  - [ ] Identify contradiction between rubric and prompt
  - [ ] Document WHERE and WHY it contradicts
  - [ ] **Present findings to user with suggested fix**
  - [ ] **Wait for user approval**
  - [ ] Update rubric in both files (only after approval)
  - [ ] Re-run evaluation to verify fix
- [ ] **Step 5**: Generate Improvement Suggestions for failing rubrics:
  - [ ] Classify issue type (Prompt Issue / Judge Issue / Model Issue)
  - [ ] Investigate root cause by reading prompt and analyzing samples
  - [ ] Run validation experiments with proposed fixes
  - [ ] Document detailed suggestion with:
    - [ ] Specific issue description
    - [ ] Expected vs actual output examples
    - [ ] Prompt change with file location and OLD/NEW comparison
    - [ ] Experiment results (samples tested, baseline vs fixed)
    - [ ] Validation status (✅ VALIDATED / ⏳ PENDING / ⚠️ PARTIAL)
  - [ ] Add suggestion to dashboard data
- [ ] **Regenerate dashboards with latest data**
