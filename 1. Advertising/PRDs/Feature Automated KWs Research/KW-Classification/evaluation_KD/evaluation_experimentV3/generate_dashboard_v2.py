#!/usr/bin/env python3
"""
Generate dashboards for Experiment V2 evaluation results.
IMPORTANT: Dashboards MUST match the exact format of V1 reference dashboards.
This script COPIES V1 template exactly and only replaces the data.

Reference templates:
- evaluation_KD/evaluation_experimentV1/dashboards/MATCH_RATE_DASHBOARD.html
- evaluation_KD/evaluation_experimentV1/dashboards/MODULE_ANALYSIS_DASHBOARD.html

Reads from: evaluation_experimentV2/judge_results/*.json
Outputs to: evaluation_experimentV2/dashboards/
"""

import json
import html
import re
from pathlib import Path
from datetime import datetime
from typing import Optional

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
RESULTS_DIR = SCRIPT_DIR / "judge_results"
DASHBOARDS_DIR = SCRIPT_DIR / "dashboards"
SUGGESTIONS_FILE = SCRIPT_DIR / "improvement_suggestions.json"

# V1 template paths
V1_DASHBOARDS_DIR = PROJECT_ROOT / "evaluation_KD" / "evaluation_experimentV1" / "dashboards"
V1_MODULE_ANALYSIS = V1_DASHBOARDS_DIR / "MODULE_ANALYSIS_DASHBOARD.html"
V1_MATCH_RATE = V1_DASHBOARDS_DIR / "MATCH_RATE_DASHBOARD.html"

# Module display names
MODULE_NAMES = {
    'm01': 'M01 - Extract Own Brand Entities',
    'm01a': 'M01a - Extract Brand Variations',
    'm01b': 'M01b - Extract Brand Related Terms',
    'm02': 'M02 - Classify Own Brand Keywords',
    'm04': 'M04 - Classify Competitor Brand Keywords',
}


def load_all_results() -> dict:
    """Load latest results for all modules."""
    results = {}
    for module in MODULE_NAMES.keys():
        pattern = f"{module}_judge_*.json"
        files = sorted(RESULTS_DIR.glob(pattern), reverse=True)
        if files:
            with open(files[0]) as f:
                results[module] = json.load(f)
                results[module]['_source_file'] = files[0].name
    return results


def build_module_data(all_results: dict) -> dict:
    """Build moduleData JavaScript object from evaluation results."""
    module_js_data = {}

    for module, data in all_results.items():
        evaluations = data.get('evaluations', [])
        summary = data.get('summary', {})
        pass_rate = data.get('pass_rate', 0)

        total = summary.get('pass', 0) + summary.get('fail', 0)

        # Build analysis summary by grouping evaluations by criterion and verdict
        analysis_summary = {}
        for ev in evaluations:
            criterion = ev.get('criterion', 'Unknown')
            verdict = ev.get('verdict', 'ERROR')
            if verdict == 'PASS':
                key = 'PASS - correct'
            else:
                key = f"FAIL - {criterion.lower()}"
            analysis_summary[key] = analysis_summary.get(key, 0) + 1

        # Build analysis table
        analysis_table = []
        seen_samples = set()
        for ev in evaluations[:5]:  # Limit to 5 rows for display
            sample_key = f"{ev.get('sample_id', '')}_{ev.get('criterion', '')}"
            if sample_key in seen_samples:
                continue
            seen_samples.add(sample_key)

            expected = ev.get('expected', {})
            actual = ev.get('output', {})

            issue_type = 'Model Correct' if ev['verdict'] == 'PASS' else 'Prompt Issue'

            analysis_table.append({
                'issueType': issue_type,
                'analysisSummary': f"{ev['verdict']} - {ev['criterion'].lower()[:30]}",
                'specificIssue': ev.get('reasoning', '')[:60] or 'None',
                'expectedOutput': json.dumps(expected)[:100] if expected else '{}',
                'actualOutput': json.dumps(actual)[:100] if actual else '{}',
            })

        module_js_data[module.upper()] = {
            'name': MODULE_NAMES.get(module, module.upper()),
            'description': get_module_description(module),
            'total': total,
            'pass': summary.get('pass', 0),
            'fail': summary.get('fail', 0),
            'passRate': round(pass_rate),
            'analysisSummary': analysis_summary,
            'analysisTable': analysis_table,
            'fixed': [],
            'recommendations': []
        }

    return module_js_data


def get_module_description(module: str) -> str:
    """Get module description."""
    descriptions = {
        'm01': 'Extracts brand name and variations from product listing',
        'm01a': 'Generates typo/case variations of brand name',
        'm01b': 'Extracts sub-brands, product lines, manufacturer',
        'm02': 'Classifies keyword as OB (Own Brand) or passes through',
        'm04': 'Classifies keyword as CB (Competitor Brand) or passes through',
    }
    return descriptions.get(module, 'Module evaluation')


def load_improvement_suggestions() -> list:
    """Load improvement suggestions from file (Claude curated)."""
    if SUGGESTIONS_FILE.exists():
        with open(SUGGESTIONS_FILE) as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'suggestions' in data:
                return data['suggestions']
    return []


def generate_module_analysis_dashboard(all_results: dict) -> str:
    """
    Generate MODULE_ANALYSIS_DASHBOARD by copying V1 template exactly
    and replacing only the data sections.
    """
    # Load V1 template
    if not V1_MODULE_ANALYSIS.exists():
        print(f"  ERROR: V1 template not found: {V1_MODULE_ANALYSIS}")
        return generate_fallback_module_analysis(all_results)

    with open(V1_MODULE_ANALYSIS) as f:
        template = f.read()

    # Build V2 module data
    module_js_data = build_module_data(all_results)

    # Load improvement suggestions
    improvement_suggestions = load_improvement_suggestions()
    print(f"  Loaded {len(improvement_suggestions)} Claude curated improvement suggestions from {SUGGESTIONS_FILE.name}")

    # Build sidebar module list HTML
    modules_sorted = sorted(module_js_data.items(), key=lambda x: x[1]['passRate'])
    sidebar_html = ""
    for module_id, m in modules_sorted:
        rate = m['passRate']
        if rate >= 80:
            rate_class = 'rate-excellent'
        elif rate >= 60:
            rate_class = 'rate-good'
        elif rate >= 40:
            rate_class = 'rate-warning'
        else:
            rate_class = 'rate-critical'

        sidebar_html += f'''
            <li class="module-item" data-module="{module_id}" onclick="selectModule('{module_id}')">
                <span class="module-name">{module_id}</span>
                <span class="module-rate {rate_class}">{rate}%</span>
            </li>
        '''

    # Update title
    template = template.replace(
        '<title>Module Evaluation Analysis Dashboard</title>',
        '<title>Module Evaluation Analysis Dashboard - Experiment V2</title>'
    )

    # Update subtitle
    template = template.replace(
        '<p>KW Classification Pipeline</p>',
        '<p>KW Classification Pipeline - Experiment V2</p>'
    )

    # Replace module list in sidebar
    template = re.sub(
        r'<ul class="module-list" id="moduleList">.*?</ul>',
        f'<ul class="module-list" id="moduleList">{sidebar_html}</ul>',
        template,
        flags=re.DOTALL
    )

    # Replace badge count
    template = re.sub(
        r'<span class="badge" id="totalIssuesBadge">\d+</span>',
        f'<span class="badge" id="totalIssuesBadge">{len(improvement_suggestions)}</span>',
        template
    )

    # Replace moduleData JavaScript object
    module_data_js = json.dumps(module_js_data, indent=12)
    # Find and replace using string methods to avoid regex escape issues
    start_marker = 'const moduleData = {'
    end_marker = '\n        };'
    start_idx = template.find(start_marker)
    if start_idx != -1:
        # Find the end of moduleData
        search_start = start_idx + len(start_marker)
        end_idx = template.find(end_marker, search_start)
        if end_idx != -1:
            template = template[:start_idx] + f'const moduleData = {module_data_js};' + template[end_idx + len(end_marker):]

    # Replace improvementSuggestions JavaScript array
    suggestions_js = json.dumps(improvement_suggestions, indent=12)
    start_marker = 'const improvementSuggestions = ['
    end_marker = '\n        ];'
    start_idx = template.find(start_marker)
    if start_idx != -1:
        search_start = start_idx + len(start_marker)
        end_idx = template.find(end_marker, search_start)
        if end_idx != -1:
            template = template[:start_idx] + f'const improvementSuggestions = {suggestions_js};' + template[end_idx + len(end_marker):]

    # Update first module selected
    first_module = modules_sorted[0][0] if modules_sorted else 'M01'
    template = re.sub(
        r"selectModule\('M01'\);",
        f"selectModule('{first_module}');",
        template
    )

    return template


def generate_fallback_module_analysis(all_results: dict) -> str:
    """Generate a fallback dashboard if V1 template not found."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <title>Module Analysis Dashboard - V2</title>
</head>
<body>
    <h1>ERROR: V1 Template Not Found</h1>
    <p>Please ensure V1 dashboards exist at:</p>
    <pre>{V1_MODULE_ANALYSIS}</pre>
</body>
</html>"""


def generate_match_rate_dashboard(all_results: dict) -> str:
    """
    Generate MATCH_RATE_DASHBOARD by copying V1 template exactly
    and replacing only the data sections.
    """
    # Load V1 template
    if not V1_MATCH_RATE.exists():
        print(f"  ERROR: V1 template not found: {V1_MATCH_RATE}")
        return "<html><body><h1>V1 template not found</h1></body></html>"

    with open(V1_MATCH_RATE) as f:
        template = f.read()

    # Build module data for match rate
    modules = []
    for module, data in all_results.items():
        evaluations = data.get('evaluations', [])
        summary = data.get('summary', {})
        pass_rate = data.get('pass_rate', 0)
        total = summary.get('pass', 0) + summary.get('fail', 0)

        modules.append({
            'id': module.upper(),
            'name': MODULE_NAMES.get(module, module.upper()),
            'total': total,
            'exact': summary.get('pass', 0),
            'semantic': 0,
            'mismatch': summary.get('fail', 0),
            'passRate': round(pass_rate)
        })

    # Sort by pass rate
    modules.sort(key=lambda x: x['passRate'])

    # Update title
    template = template.replace(
        '<title>Match Rate Dashboard</title>',
        '<title>Match Rate Dashboard - Experiment V2</title>'
    )

    # Replace moduleResults JavaScript
    modules_js = json.dumps(modules, indent=8)
    template = re.sub(
        r'const moduleResults = \[.*?\];',
        f'const moduleResults = {modules_js};',
        template,
        flags=re.DOTALL
    )

    return template


def generate_summary_dashboard(all_results: dict) -> str:
    """Generate a simple summary dashboard."""
    modules = []
    total_pass = 0
    total_fail = 0

    for module, data in all_results.items():
        summary = data.get('summary', {})
        pass_rate = data.get('pass_rate', 0)
        total_pass += summary.get('pass', 0)
        total_fail += summary.get('fail', 0)
        modules.append({
            'id': module.upper(),
            'passRate': round(pass_rate),
            'pass': summary.get('pass', 0),
            'fail': summary.get('fail', 0)
        })

    modules.sort(key=lambda x: x['passRate'])
    overall_rate = total_pass / (total_pass + total_fail) * 100 if (total_pass + total_fail) > 0 else 0

    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Experiment V2 Summary</title>
    <style>
        body {{ font-family: -apple-system, sans-serif; padding: 40px; background: #f5f7fa; }}
        h1 {{ color: #1a1a2e; margin-bottom: 30px; }}
        .card {{ background: white; padding: 20px; border-radius: 10px; margin-bottom: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }}
        .module {{ display: flex; justify-content: space-between; align-items: center; }}
        .rate {{ font-weight: bold; padding: 5px 15px; border-radius: 20px; }}
        .critical {{ background: #ff6b6b; color: white; }}
        .warning {{ background: #feca57; color: #333; }}
        .good {{ background: #4ecdc4; color: white; }}
        .excellent {{ background: #26de81; color: white; }}
    </style>
</head>
<body>
    <h1>Experiment V2 Summary</h1>
    <div class="card">
        <h2>Overall Pass Rate: {overall_rate:.1f}%</h2>
        <p>Total: {total_pass + total_fail} evaluations | Pass: {total_pass} | Fail: {total_fail}</p>
    </div>
    {''.join(f'''
    <div class="card">
        <div class="module">
            <span><strong>{m['id']}</strong></span>
            <span class="rate {'critical' if m['passRate'] < 40 else 'warning' if m['passRate'] < 60 else 'good' if m['passRate'] < 80 else 'excellent'}">{m['passRate']}%</span>
        </div>
        <p>Pass: {m['pass']} | Fail: {m['fail']}</p>
    </div>
    ''' for m in modules)}
</body>
</html>"""


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate V2 dashboards")
    parser.add_argument("--no-open", action="store_true", help="Don't open in browser")
    args = parser.parse_args()

    print("Loading evaluation results...")
    all_results = load_all_results()

    if not all_results:
        print("No results found in", RESULTS_DIR)
        return

    print(f"Found results for {len(all_results)} modules: {', '.join(all_results.keys())}")

    DASHBOARDS_DIR.mkdir(exist_ok=True)

    # Generate summary dashboard
    print("\nGenerating summary dashboard...")
    summary_html = generate_summary_dashboard(all_results)
    summary_path = DASHBOARDS_DIR / "SUMMARY_DASHBOARD.html"
    with open(summary_path, 'w') as f:
        f.write(summary_html)
    print(f"  Saved: {summary_path}")

    # Generate match rate dashboard (V1 format)
    print("Generating match rate dashboard (V1 format)...")
    match_html = generate_match_rate_dashboard(all_results)
    match_path = DASHBOARDS_DIR / "MATCH_RATE_DASHBOARD.html"
    with open(match_path, 'w') as f:
        f.write(match_html)
    print(f"  Saved: {match_path}")

    # Generate module analysis dashboard (V1 format)
    print("Generating module analysis dashboard (V1 format)...")
    module_html = generate_module_analysis_dashboard(all_results)
    module_path = DASHBOARDS_DIR / "MODULE_ANALYSIS_DASHBOARD.html"
    with open(module_path, 'w') as f:
        f.write(module_html)
    print(f"  Saved: {module_path}")

    print(f"\nAll dashboards saved to: {DASHBOARDS_DIR}")

    if not args.no_open:
        import subprocess
        subprocess.run(["open", str(module_path)])


if __name__ == "__main__":
    main()
