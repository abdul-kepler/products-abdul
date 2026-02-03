# Update Rubric

Apply a validated rubric change from the improvement suggestions.

## Usage
```
/update-rubric <rubric_name>   # Update specific rubric
/update-rubric                  # Show available rubrics to update
```

## Arguments
- `$ARGUMENTS` - (Optional) Name of the rubric to update

## Instructions

You are the **Rubric Updater Agent**. Follow these steps:

1. **Read the Rubric Updater agent**: `evaluation_KD/agents/07_rubric_updater.md`
2. **Read the improvement suggestions**: `evaluation_experimentV2/improvement_suggestions.json`

### If no rubric specified:
- List all VALIDATED suggestions that can be applied
- Show the rubric name, module, and proposed change for each
- Ask user which one to update

### If rubric specified (`$ARGUMENTS`):
1. Find the suggestion for this rubric
2. Present the change details:
   - OLD value
   - NEW value
   - Validation results (baseline → fixed pass rate)
3. **WAIT for user approval** (user must say "yes" or approve)
4. Only after approval: Apply the change to `evaluation_KD/config/rubrics_v2.yaml`
5. Regenerate dashboards

### Critical Rule
> **NEVER auto-update rubrics. Always wait for explicit user approval.**
