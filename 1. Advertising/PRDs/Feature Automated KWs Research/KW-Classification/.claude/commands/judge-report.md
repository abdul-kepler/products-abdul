# Generate Judge Report

Generate HTML judge report for evaluation results.

## Usage
```
/judge-report <module>   # Generate report for specific module
/judge-report all        # Generate reports for all modules
```

## Arguments
- `$ARGUMENTS` - Module name (m01, m02, etc.) or "all"

## Instructions

You are the **Dashboard Generator Agent**. Follow these steps:

1. **Read the Dashboard Generator agent**: `evaluation_KD/agents/06_dashboard_generator.md`
2. **Generate the judge report** for module: `$ARGUMENTS`

### Commands to Run

For single module:
```bash
python3 evaluation/generate_judge_report.py $ARGUMENTS
```

For all modules:
```bash
python3 evaluation/generate_judge_report.py all
```

### Verify Output
- Check that HTML file was created: `evaluation/judge_report_<module>.html`
- Confirm file is not empty
- Report the file location to user
