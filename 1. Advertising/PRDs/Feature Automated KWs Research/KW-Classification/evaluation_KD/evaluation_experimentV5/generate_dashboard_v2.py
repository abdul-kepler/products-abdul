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
V1_DASHBOARDS_DIR = PROJECT_ROOT / "evaluation_experimentV1" / "dashboards"
V1_MODULE_ANALYSIS = V1_DASHBOARDS_DIR / "MODULE_ANALYSIS_DASHBOARD.html"
V1_MATCH_RATE = V1_DASHBOARDS_DIR / "MATCH_RATE_DASHBOARD.html"

# Module display names - ALL modules
MODULE_NAMES = {
    'm01': 'M01 - Extract Own Brand Entities',
    'm01_v1': 'M01 v1 - Extract Own Brand Entities',
    'm01_v2': 'M01 v2 - Extract Own Brand Entities',
    'm01a': 'M01A - Extract Brand Variations',
    'm01a_v2': 'M01A v2 - Extract Brand Variations',
    'm01b': 'M01B - Extract Brand Related Terms',
    'm02': 'M02 - Classify Own Brand Keywords',
    'm02b': 'M02B - Classify Own Brand Keywords (Path B)',
    'm04': 'M04 - Classify Competitor Brand Keywords',
    'm04b': 'M04B - Classify Competitor Brand (Path B)',
    'm05': 'M05 - Classify Non-Branded Keywords',
    'm05b': 'M05B - Classify Non-Branded (Path B)',
    'm06_gd': 'M06 GD - Generate Product Type Taxonomy',
    'm06_sd': 'M06 SD - Generate Product Type Taxonomy',
    'm07_gd': 'M07 GD - Extract Product Attributes',
    'm07_sd': 'M07 SD - Extract Product Attributes',
    'm08': 'M08 - Assign Attribute Ranks',
    'm08_sd': 'M08 SD - Assign Attribute Ranks',
    'm08_v2': 'M08 v2 - Assign Attribute Ranks',
    'm08_v2_sd': 'M08 v2 SD - Assign Attribute Ranks',
    'm09': 'M09 - Identify Primary Intended Use',
    'm10': 'M10 - Validate Primary Intended Use',
    'm11': 'M11 - Identify Hard Constraints',
    'm12': 'M12 - Hard Constraint Violation Check',
    'm13': 'M13 - Product Type Check',
    'm14': 'M14 - Primary Use Check Same Type',
    'm15': 'M15 - Substitute Check',
    'm16': 'M16 - Complementary Check',
}


def load_all_results() -> dict:
    """Load latest results for all modules (auto-discover from judge_results)."""
    results = {}

    # Auto-discover all modules from judge_results folder
    all_files = list(RESULTS_DIR.glob("*_judge_*.json"))
    discovered_modules = set()
    for f in all_files:
        # Extract module name: m01_judge_xxx.json -> m01, m01_v2_judge_xxx.json -> m01_v2
        name = f.name
        judge_idx = name.find('_judge_')
        if judge_idx > 0:
            module = name[:judge_idx]
            discovered_modules.add(module)

    # Load latest result for each discovered module
    for module in discovered_modules:
        pattern = f"{module}_judge_*.json"
        files = sorted(RESULTS_DIR.glob(pattern), reverse=True)
        if files:
            with open(files[0]) as f:
                results[module] = json.load(f)
                results[module]['_source_file'] = files[0].name
                # Add module name if not in MODULE_NAMES
                if module not in MODULE_NAMES:
                    MODULE_NAMES[module] = module.upper().replace('_', ' ')
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
            'model': data.get('model', 'unknown'),
            'promptVersion': data.get('prompt_version', 'unknown'),
            'dataSource': data.get('data_source', 'unknown'),
            'timestamp': data.get('timestamp', ''),
            'analysisSummary': analysis_summary,
            'analysisTable': analysis_table,
            'fixed': [],
            'recommendations': []
        }

    return module_js_data


def get_module_description(module: str) -> str:
    """Get module description."""
    # Base descriptions - strip version suffixes for lookup
    base_module = module.split('_')[0] if '_' in module else module
    descriptions = {
        'm01': 'Extracts brand name and variations from product listing',
        'm01a': 'Generates typo/case variations of brand name',
        'm01b': 'Extracts sub-brands, product lines, manufacturer',
        'm02': 'Classifies keyword as OB (Own Brand) or passes through',
        'm02b': 'Classifies keyword as OB (Path B workflow)',
        'm04': 'Classifies keyword as CB (Competitor Brand) or passes through',
        'm04b': 'Classifies keyword as CB (Path B workflow)',
        'm05': 'Classifies non-branded keywords',
        'm05b': 'Classifies non-branded keywords (Path B)',
        'm06': 'Generates product type taxonomy from listing',
        'm07': 'Extracts product attributes from listing',
        'm08': 'Assigns importance ranks to attributes',
        'm09': 'Identifies primary intended use of product',
        'm10': 'Validates M09 primary intended use output',
        'm11': 'Identifies hard constraints for product',
        'm12': 'Checks for hard constraint violations',
        'm13': 'Validates product type classification',
        'm14': 'Checks primary use for same product type',
        'm15': 'Identifies substitute products',
        'm16': 'Identifies complementary products',
    }
    return descriptions.get(base_module, descriptions.get(module, 'Module evaluation'))


def load_improvement_suggestions() -> list:
    """Load improvement suggestions from file (Claude curated)."""
    if SUGGESTIONS_FILE.exists():
        with open(SUGGESTIONS_FILE) as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                # Format: {"modules": {"M01": {"suggestions": [...]}, "M04": {"suggestions": [...]}}}
                if 'modules' in data:
                    all_suggestions = []
                    for module, module_data in data['modules'].items():
                        suggestions = module_data.get('suggestions', [])
                        for s in suggestions:
                            s['module'] = module  # Ensure module is set
                        all_suggestions.extend(suggestions)
                    return all_suggestions
                elif 'suggestions' in data:
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

        prompt_ver = m.get('promptVersion', '?')
        model = m.get('model', '?')

        sidebar_html += f'''
            <li class="module-item" data-module="{module_id}" onclick="selectModule('{module_id}')">
                <span class="module-name">{module_id}</span>
                <span class="module-rate {rate_class}">{rate}%</span>
                <span style="display:block; font-size:0.7rem; color:#64748b; margin-top:2px;">{prompt_ver} | {model}</span>
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
            'fail': summary.get('fail', 0),
            'model': data.get('model', 'unknown'),
            'promptVersion': data.get('prompt_version', 'unknown'),
            'timestamp': data.get('timestamp', '')[:16] if data.get('timestamp') else ''
        })

    modules.sort(key=lambda x: x['passRate'])
    overall_rate = total_pass / (total_pass + total_fail) * 100 if (total_pass + total_fail) > 0 else 0

    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Experiment V5 Summary</title>
    <style>
        body {{ font-family: -apple-system, sans-serif; padding: 40px; background: #0f172a; color: #e2e8f0; }}
        h1 {{ color: #f1f5f9; margin-bottom: 30px; }}
        .card {{ background: #1e293b; padding: 20px; border-radius: 10px; margin-bottom: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.3); }}
        .module {{ display: flex; justify-content: space-between; align-items: center; }}
        .rate {{ font-weight: bold; padding: 5px 15px; border-radius: 20px; }}
        .critical {{ background: #ef4444; color: white; }}
        .warning {{ background: #f59e0b; color: #1e293b; }}
        .good {{ background: #22c55e; color: white; }}
        .excellent {{ background: #10b981; color: white; }}
        .meta {{ font-size: 0.85rem; color: #94a3b8; margin-top: 8px; }}
        .meta span {{ margin-right: 15px; }}
        .badge {{ background: #334155; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; }}
    </style>
</head>
<body>
    <h1>Experiment V5 Summary</h1>
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
        <div class="meta">
            <span>Prompt: <span class="badge">{m['promptVersion']}</span></span>
            <span>Model: <span class="badge">{m['model']}</span></span>
            <span>Evaluated: {m['timestamp']}</span>
        </div>
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
