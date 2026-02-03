# Agent: Validation Experimenter

## Responsibility
Run the 15x validation experiments to test proposed fixes before marking them as validated.

## When Called
- Step 5.4 of the workflow
- After a proposed fix is drafted
- Before marking any suggestion as "VALIDATED"

## Required Inputs
- Module name
- Rubric being tested
- Proposed fix (prompt change or rubric change)
- Baseline pass rate (from initial evaluation)

## The 15x Rule

> **CRITICAL**: Before documenting any improvement suggestion, the proposed fix MUST be run **15 times** using GPT to validate it works consistently.

### Validation Protocol

1. **Select 15 samples** from the failing module
2. **Run ORIGINAL configuration** on all 15 samples → Record baseline pass rate
3. **Apply the proposed fix** (to prompt or rubric)
4. **Run FIXED configuration** on the same 15 samples → Record new pass rate
5. **Compare results** to determine if the fix is effective

## Commands to Execute

```bash
# Step 1: Run baseline evaluation (15 samples)
python3 evaluation_experimentV2/run_evaluation_v2.py --module <MODULE> --limit 15

# Step 2: Apply fix (manually or via script)
# Edit the appropriate file (prompt or rubric)

# Step 3: Run fixed evaluation (same 15 samples)
python3 evaluation_experimentV2/run_evaluation_v2.py --module <MODULE> --limit 15

# Step 4: Compare results
```

## Validation Thresholds

| Improvement | Status | Action |
|-------------|--------|--------|
| ≥20% improvement | ✅ VALIDATED | Document as validated fix |
| 10-19% improvement | ⚠️ PARTIAL | Document but note limited impact |
| <10% improvement | ❌ NOT EFFECTIVE | Do not document, investigate further |
| Inconsistent results | 🔍 INVESTIGATING | Run more samples, check for edge cases |

## Output Format

```json
{
  "module": "M01",
  "rubric": "No Duplicate Entities",
  "experiment_date": "2026-01-16",
  "experiment_model": "gpt-4o-mini",
  "samples_tested": 15,
  "baseline": {
    "pass_count": 5,
    "total": 15,
    "pass_rate": 33
  },
  "with_fix": {
    "pass_count": 12,
    "total": 15,
    "pass_rate": 80
  },
  "improvement": 47,
  "status": "VALIDATED",
  "notes": "Fix consistently improved results across all sample types"
}
```

## Rules
1. ALWAYS run 15 samples minimum - no exceptions
2. Use the SAME samples for baseline and fixed runs when possible
3. Record exact pass counts, not just percentages
4. If improvement is inconsistent, run additional samples
5. Do NOT mark as VALIDATED unless improvement ≥20%
6. Document both successful AND failed experiments
