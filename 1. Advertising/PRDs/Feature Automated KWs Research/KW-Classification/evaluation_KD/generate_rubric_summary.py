#!/usr/bin/env python3
"""
Generate Rubric Summary Spreadsheet - Aggregated stats per rubric with failure analysis.

Columns:
- Rubric ID
- Rubric Criterion
- Total Evaluations
- Pass
- Fail
- Pass Rate
- Common Failure Reasons (analyzed from reasoning)

Usage:
    python evaluation/generate_rubric_summary.py [--run TIMESTAMP]

    --run TIMESTAMP: Only use files from this specific run (e.g., 20260114_01)
                     If not specified, uses the latest file per module.
"""

import json
import csv
import sys
from pathlib import Path
from datetime import datetime
from glob import glob
from collections import defaultdict, Counter
import re

# Paths
SCRIPT_DIR = Path(__file__).parent
JUDGE_DIR = SCRIPT_DIR / "judge_results"
OUTPUT_DIR = SCRIPT_DIR / "evaluation_reports"

# Module order
MODULES = [
    "m01", "m01a", "m01b", "m02", "m03", "m04", "m05",
    "m06", "m07", "m08", "m09", "m10", "m11",
    "m12", "m12b", "m13", "m14", "m15", "m16"
]


def get_file_timestamp(filepath: str) -> str:
    """Extract timestamp from judge file name."""
    # Format: m01_judge_20260113_224504.json
    basename = Path(filepath).stem
    parts = basename.split('_')
    if len(parts) >= 4:
        return f"{parts[2]}_{parts[3]}"
    return ""


def load_all_judge_results(run_filter: str = None, first_run_only: bool = False) -> dict:
    """Load all judge results and aggregate by rubric.

    Args:
        run_filter: Optional timestamp prefix to filter files (e.g., "20260114_01")
        first_run_only: If True, use first file per module (first complete run)
    """

    rubric_data = defaultdict(lambda: {
        'criterion': '',
        'module': '',
        'pass': 0,
        'fail': 0,
        'error': 0,
        'fail_reasons': []
    })

    files_used = []

    for module in MODULES:
        pattern = str(JUDGE_DIR / f"{module}_judge_*.json")
        files = sorted(glob(pattern))
        if not files:
            continue

        # Filter by run timestamp if specified
        if run_filter:
            matching_files = [f for f in files if run_filter in get_file_timestamp(f)]
            if matching_files:
                selected_file = matching_files[-1]  # Latest matching file
            else:
                print(f"  Warning: No files for {module} matching run {run_filter}, skipping...")
                continue
        elif first_run_only:
            # Use the first file (from the first complete run)
            selected_file = files[0]
        else:
            # Use the latest file
            selected_file = files[-1]

        files_used.append(selected_file)
        print(f"Loading {Path(selected_file).name}...")

        with open(selected_file) as f:
            data = json.load(f)

        for eval_item in data.get('evaluations', []):
            rubric_id = eval_item.get('rubric_id', '')
            criterion = eval_item.get('criterion', '')
            verdict = eval_item.get('verdict', '')
            reasoning = eval_item.get('reasoning', '')

            rubric_data[rubric_id]['criterion'] = criterion
            rubric_data[rubric_id]['module'] = module.upper()

            if verdict == 'PASS':
                rubric_data[rubric_id]['pass'] += 1
            elif verdict == 'FAIL':
                rubric_data[rubric_id]['fail'] += 1
                # Extract failure reason
                rubric_data[rubric_id]['fail_reasons'].append(reasoning)
            else:
                rubric_data[rubric_id]['error'] += 1

    print(f"\nLoaded {len(files_used)} judge result files")
    return rubric_data


def analyze_failure_reasons(fail_reasons: list) -> str:
    """Analyze failure reasons and extract common patterns."""
    if not fail_reasons:
        return "N/A"

    # Common failure patterns to look for
    patterns = {
        'hallucination': r'hallucin|invented|fabricat|not found in input|not present in',
        'missing_brand': r'missed|not detected|failed to detect|brand.*not.*found',
        'product_words': r'product word|generic.*word|feature.*word|descriptor',
        'wrong_classification': r'incorrect.*classif|wrong.*classif|should.*be|expected.*but',
        'format_issue': r'format|structure|missing.*field|not.*expected',
        'duplicate': r'duplicate|repeated|same.*string',
        'word_boundary': r'boundary|partial.*match|substring',
        'case_sensitivity': r'case.*sensitiv|uppercase|lowercase',
        'count_issue': r'count|fewer than|more than|not.*8-12|not.*5-10',
        'type_mismatch': r'different.*type|not.*same.*type|type.*mismatch',
        'use_mismatch': r'different.*use|not.*same.*use|primary.*use.*differ',
        'not_complementary': r'not.*complementary|not.*used.*together',
        'not_substitute': r'not.*substitute|cannot.*replace',
    }

    # Count occurrences of each pattern
    pattern_counts = Counter()
    specific_issues = []

    for reason in fail_reasons:
        reason_lower = reason.lower()
        matched = False

        for pattern_name, pattern in patterns.items():
            if re.search(pattern, reason_lower):
                pattern_counts[pattern_name] += 1
                matched = True

        # Extract specific issue from reasoning
        if '1.' in reason:
            # Get first numbered point
            lines = reason.split('\n')
            for line in lines:
                if line.strip().startswith('1.') or line.strip().startswith('- '):
                    issue = line.strip()[:150]
                    if issue and len(issue) > 20:
                        specific_issues.append(issue)
                        break

    # Build summary
    summary_parts = []

    # Top patterns
    if pattern_counts:
        top_patterns = pattern_counts.most_common(3)
        pattern_summary = ", ".join([f"{name} ({count})" for name, count in top_patterns])
        summary_parts.append(f"Issues: {pattern_summary}")

    # Sample specific issues (deduplicated)
    unique_issues = list(set(specific_issues))[:3]
    if unique_issues:
        for issue in unique_issues:
            # Clean up the issue text
            issue = issue.replace('1.', '').replace('-', '').strip()
            if len(issue) > 100:
                issue = issue[:100] + "..."
            summary_parts.append(f"• {issue}")

    if not summary_parts:
        # Fallback: extract key phrases from first failure
        first_reason = fail_reasons[0][:300]
        summary_parts.append(first_reason)

    return " | ".join(summary_parts) if len(summary_parts) <= 2 else "\n".join(summary_parts)


def generate_summary(run_filter: str = None, first_run_only: bool = False):
    """Generate rubric summary spreadsheet."""

    if run_filter:
        print(f"Loading judge results for run: {run_filter}...")
    elif first_run_only:
        print("Loading judge results (FIRST RUN ONLY - first file per module)...")
    else:
        print("Loading judge results (latest file per module)...")
    rubric_data = load_all_judge_results(run_filter, first_run_only)

    OUTPUT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_file = OUTPUT_DIR / f"rubric_summary_{timestamp}.csv"

    rows = []

    # Sort rubrics by module order
    def sort_key(rubric_id):
        module = rubric_id.split('_')[0].lower()
        try:
            return MODULES.index(module)
        except ValueError:
            return 999

    sorted_rubrics = sorted(rubric_data.keys(), key=sort_key)

    for rubric_id in sorted_rubrics:
        data = rubric_data[rubric_id]

        total = data['pass'] + data['fail'] + data['error']
        pass_rate = (data['pass'] / total * 100) if total > 0 else 0

        # Analyze failure reasons
        fail_analysis = analyze_failure_reasons(data['fail_reasons'])

        row = {
            'Module': data['module'],
            'Rubric ID': rubric_id,
            'Rubric Criterion': data['criterion'],
            'Total Evaluations': total,
            'Pass': data['pass'],
            'Fail': data['fail'],
            'Error': data['error'],
            'Pass Rate': f"{pass_rate:.1f}%",
            'Failure Analysis': fail_analysis,
        }
        rows.append(row)

    # Write CSV
    if rows:
        fieldnames = [
            'Module', 'Rubric ID', 'Rubric Criterion',
            'Total Evaluations', 'Pass', 'Fail', 'Error', 'Pass Rate',
            'Failure Analysis'
        ]

        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        print(f"\nSummary saved to: {csv_file}")
        print(f"Total rubrics: {len(rows)}")

        # Overall summary
        total_pass = sum(r['Pass'] for r in rows)
        total_fail = sum(r['Fail'] for r in rows)
        total_all = total_pass + total_fail
        overall_rate = (total_pass / total_all * 100) if total_all > 0 else 0

        print(f"\nOverall: {total_pass} PASS, {total_fail} FAIL ({overall_rate:.1f}%)")

        # Print summary table
        print("\n" + "=" * 80)
        print(f"{'Rubric ID':<35} {'Criterion':<25} {'Pass':>6} {'Fail':>6} {'Rate':>8}")
        print("=" * 80)
        for row in rows:
            print(f"{row['Rubric ID']:<35} {row['Rubric Criterion'][:25]:<25} {row['Pass']:>6} {row['Fail']:>6} {row['Pass Rate']:>8}")

    return csv_file


if __name__ == "__main__":
    run_filter = None
    first_run_only = "--first-run" in sys.argv

    # Parse --run argument
    if "--run" in sys.argv:
        idx = sys.argv.index("--run")
        if idx + 1 < len(sys.argv):
            run_filter = sys.argv[idx + 1]

    # Show available runs if requested
    if "--list-runs" in sys.argv:
        print("Available judge result files:")
        all_files = sorted(glob(str(JUDGE_DIR / "*_judge_*.json")))
        timestamps = set()
        for f in all_files:
            ts = get_file_timestamp(f)
            if ts:
                timestamps.add(ts[:8])  # Just the date part
        print(f"Unique dates: {sorted(timestamps)}")
        for f in all_files:
            print(f"  {Path(f).name}")
        sys.exit(0)

    generate_summary(run_filter, first_run_only)
