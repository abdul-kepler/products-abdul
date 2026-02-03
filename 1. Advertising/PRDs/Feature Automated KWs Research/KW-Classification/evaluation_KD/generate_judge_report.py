#!/usr/bin/env python3
"""Generate interactive HTML report from LLM Judge evaluation results."""

import json
import html
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
RESULTS_DIR = SCRIPT_DIR / "judge_results"
DATASETS_DIR = PROJECT_ROOT / "datasets"
BATCH_RESULTS_DIR = PROJECT_ROOT / "batch_requests" / "20260112_2127" / "results"

MODULE_FILES = {
    'm01': {
        'dataset': 'm01_extract_own_brand_entities.jsonl',
        'results': 'm01_results.jsonl',
    },
    'm01a': {
        'dataset': 'm01a_extract_own_brand_variations.jsonl',
        'results': 'm01a_results.jsonl',
    },
    'm01b': {
        'dataset': 'm01b_extract_brand_related_terms.jsonl',
        'results': 'm01b_results.jsonl',
    },
    'm02': {
        'dataset': 'm02_classify_own_brand_keywords.jsonl',
        'results': 'm02_results.jsonl',
    },
    'm03': {
        'dataset': 'm03_generate_competitor_entities.jsonl',
        'results': 'm03_results.jsonl',
    },
    'm04': {
        'dataset': 'm04_classify_competitor_brand_keywords.jsonl',
        'results': 'm04_results.jsonl',
    },
    'm05': {
        'dataset': 'm05_classify_nonbranded_keywords.jsonl',
        'results': 'm05_results.jsonl',
    },
}

def load_jsonl(file_path: Path) -> list[dict]:
    """Load records from a JSONL file."""
    records = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records

def load_dataset(module: str) -> dict[str, dict]:
    """Load dataset indexed by ASIN/ID."""
    config = MODULE_FILES.get(module, {})
    if not config:
        return {}
    file_path = DATASETS_DIR / config['dataset']
    if not file_path.exists():
        return {}
    records = load_jsonl(file_path)
    return {r['id']: r for r in records}

def load_batch_results(module: str) -> dict[int, dict]:
    """Load batch results indexed by index."""
    config = MODULE_FILES.get(module, {})
    if not config:
        return {}
    file_path = BATCH_RESULTS_DIR / config['results']
    if not file_path.exists():
        return {}
    records = load_jsonl(file_path)

    indexed = {}
    for r in records:
        custom_id = r.get('custom_id', '')
        if '_' in custom_id:
            idx = int(custom_id.split('_')[1])
            content = r.get('response', {}).get('body', {}).get('choices', [{}])[0].get('message', {}).get('content', '{}')
            try:
                output = json.loads(content)
            except json.JSONDecodeError:
                output = {'error': 'Failed to parse output'}
            indexed[idx] = output
    return indexed

def get_latest_result(module: str) -> Path:
    """Get the latest result file for a module."""
    pattern = f"{module}_judge_*.json"
    files = sorted(RESULTS_DIR.glob(pattern), reverse=True)
    return files[0] if files else None


def compare_outputs(expected: dict, actual: dict) -> dict:
    """Compare expected vs actual outputs and return match info."""
    # Handle different output structures
    expected_items = set()
    actual_items = set()

    # Extract items from expected
    if isinstance(expected, dict):
        for key, value in expected.items():
            if isinstance(value, list):
                expected_items.update(str(v).lower() for v in value)
            else:
                expected_items.add(str(value).lower())
    elif isinstance(expected, list):
        expected_items.update(str(v).lower() for v in expected)

    # Extract items from actual
    if isinstance(actual, dict):
        for key, value in actual.items():
            if isinstance(value, list):
                actual_items.update(str(v).lower() for v in value)
            else:
                actual_items.add(str(value).lower())
    elif isinstance(actual, list):
        actual_items.update(str(v).lower() for v in actual)

    # Calculate overlap
    overlap = expected_items & actual_items
    missing = expected_items - actual_items  # In expected but not in actual
    extra = actual_items - expected_items    # In actual but not in expected

    # Determine match type
    if not expected_items and not actual_items:
        match_type = 'exact'
        match_pct = 100
    elif expected_items == actual_items:
        match_type = 'exact'
        match_pct = 100
    elif overlap:
        match_pct = len(overlap) / len(expected_items) * 100 if expected_items else 0
        match_type = 'partial' if match_pct < 100 else 'exact'
    else:
        match_type = 'mismatch'
        match_pct = 0

    return {
        'type': match_type,
        'percentage': match_pct,
        'overlap': list(overlap)[:5],  # Limit for display
        'missing': list(missing)[:5],
        'extra': list(extra)[:5],
        'overlap_count': len(overlap),
        'missing_count': len(missing),
        'extra_count': len(extra),
    }

def generate_report(result_file: Path) -> str:
    """Generate HTML report from result file."""

    with open(result_file) as f:
        data = json.load(f)

    module = data['module']
    module_upper = module.upper()
    model = data['model']
    timestamp = data['timestamp']
    summary = data['summary']
    pass_rate = data['pass_rate']
    evaluations = data['evaluations']

    # Load dataset and batch results for expected/actual outputs
    dataset = load_dataset(module)
    batch_results = load_batch_results(module)

    # Create mapping from sample_id to expected/actual
    dataset_list = list(dataset.values())
    sample_data = {}
    for idx, record in enumerate(dataset_list):
        sample_id = record['id']
        sample_data[sample_id] = {
            'input': record.get('input', {}),
            'expected': record.get('expected', {}),
            'actual': batch_results.get(idx, {}),
            'metadata': record.get('metadata', {}),
        }

    # Group evaluations by rubric
    by_rubric = {}
    for eval in evaluations:
        rubric_id = eval['rubric_id']
        if rubric_id not in by_rubric:
            by_rubric[rubric_id] = {'pass': 0, 'fail': 0, 'evals': [], 'criterion': eval['criterion']}
        by_rubric[rubric_id]['evals'].append(eval)
        if eval['verdict'] == 'PASS':
            by_rubric[rubric_id]['pass'] += 1
        else:
            by_rubric[rubric_id]['fail'] += 1

    # Group evaluations by sample
    by_sample = {}
    for eval in evaluations:
        sample_id = eval['sample_id']
        if sample_id not in by_sample:
            by_sample[sample_id] = {'pass': 0, 'fail': 0, 'evals': []}
        by_sample[sample_id]['evals'].append(eval)
        if eval['verdict'] == 'PASS':
            by_sample[sample_id]['pass'] += 1
        else:
            by_sample[sample_id]['fail'] += 1

    # Build HTML
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM Judge Report - {module_upper}</title>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #e0e0e0;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        header {{
            text-align: center;
            padding: 30px 0;
            margin-bottom: 30px;
        }}
        h1 {{
            font-size: 2.5rem;
            background: linear-gradient(90deg, #00d9ff, #00ff88);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}
        .meta {{
            color: #888;
            font-size: 0.9rem;
        }}
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .card {{
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .card h3 {{
            font-size: 0.9rem;
            color: #888;
            margin-bottom: 10px;
        }}
        .card .value {{
            font-size: 2rem;
            font-weight: bold;
        }}
        .card .value.pass {{ color: #00ff88; }}
        .card .value.fail {{ color: #ff4757; }}
        .card .value.rate {{ color: #00d9ff; }}
        .tabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}
        .tab {{
            padding: 10px 20px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
        }}
        .tab:hover {{
            background: rgba(255,255,255,0.1);
        }}
        .tab.active {{
            background: rgba(0, 217, 255, 0.2);
            border-color: #00d9ff;
        }}
        .tab-content {{
            display: none;
        }}
        .tab-content.active {{
            display: block;
        }}
        .rubric-section {{
            background: rgba(255,255,255,0.03);
            border-radius: 12px;
            margin-bottom: 20px;
            border: 1px solid rgba(255,255,255,0.1);
            overflow: hidden;
        }}
        .rubric-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 20px;
            background: rgba(255,255,255,0.05);
            cursor: pointer;
        }}
        .rubric-header:hover {{
            background: rgba(255,255,255,0.08);
        }}
        .rubric-title {{
            font-weight: 600;
        }}
        .rubric-stats {{
            display: flex;
            gap: 15px;
            align-items: center;
        }}
        .stat {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
        }}
        .stat.pass {{
            background: rgba(0, 255, 136, 0.2);
            color: #00ff88;
        }}
        .stat.fail {{
            background: rgba(255, 71, 87, 0.2);
            color: #ff4757;
        }}
        .progress-bar {{
            width: 100px;
            height: 6px;
            background: rgba(255,255,255,0.1);
            border-radius: 3px;
            overflow: hidden;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #00ff88, #00d9ff);
            transition: width 0.3s;
        }}
        .rubric-content {{
            display: none;
            padding: 20px;
        }}
        .rubric-content.open {{
            display: block;
        }}
        .eval-item {{
            background: rgba(255,255,255,0.03);
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
            border-left: 3px solid #00d9ff;
        }}
        .eval-item.pass {{
            border-left-color: #00ff88;
        }}
        .eval-item.fail {{
            border-left-color: #ff4757;
        }}
        .eval-header {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }}
        .sample-id {{
            font-family: monospace;
            color: #00d9ff;
        }}
        .verdict {{
            font-weight: bold;
            padding: 2px 10px;
            border-radius: 4px;
        }}
        .verdict.pass {{
            background: rgba(0, 255, 136, 0.2);
            color: #00ff88;
        }}
        .verdict.fail {{
            background: rgba(255, 71, 87, 0.2);
            color: #ff4757;
        }}
        .reasoning {{
            font-size: 0.9rem;
            line-height: 1.6;
            color: #aaa;
            white-space: pre-wrap;
            background: rgba(0,0,0,0.2);
            padding: 10px;
            border-radius: 6px;
            max-height: 300px;
            overflow-y: auto;
        }}
        .output-comparison {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin: 15px 0;
        }}
        .output-box {{
            background: rgba(0,0,0,0.3);
            border-radius: 8px;
            padding: 12px;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .output-box h4 {{
            font-size: 0.8rem;
            color: #888;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .output-box.expected h4 {{
            color: #00ff88;
        }}
        .output-box.actual h4 {{
            color: #00d9ff;
        }}
        .output-content {{
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.8rem;
            color: #e0e0e0;
            white-space: pre-wrap;
            word-break: break-word;
            max-height: 200px;
            overflow-y: auto;
        }}
        .input-section {{
            background: rgba(0,0,0,0.2);
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 15px;
            border: 1px solid rgba(255,255,255,0.05);
        }}
        .input-section h4 {{
            font-size: 0.8rem;
            color: #ffa502;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .input-content {{
            font-size: 0.85rem;
            color: #aaa;
        }}
        .input-field {{
            margin-bottom: 8px;
        }}
        .input-field strong {{
            color: #ccc;
        }}
        .collapsible-header {{
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .collapsible-header:hover {{
            opacity: 0.8;
        }}
        .collapsible-content {{
            display: none;
        }}
        .collapsible-content.open {{
            display: block;
        }}
        .toggle-icon {{
            transition: transform 0.3s;
        }}
        .toggle-icon.open {{
            transform: rotate(90deg);
        }}
        .match-indicator {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-left: 10px;
        }}
        .match-indicator.exact {{
            background: rgba(0, 255, 136, 0.2);
            color: #00ff88;
        }}
        .match-indicator.partial {{
            background: rgba(255, 165, 2, 0.2);
            color: #ffa502;
        }}
        .match-indicator.mismatch {{
            background: rgba(255, 71, 87, 0.2);
            color: #ff4757;
        }}
        .match-details {{
            font-size: 0.75rem;
            color: #888;
            margin-top: 8px;
            padding: 8px;
            background: rgba(0,0,0,0.2);
            border-radius: 4px;
        }}
        .match-details .overlap {{
            color: #00ff88;
        }}
        .match-details .missing {{
            color: #ff4757;
        }}
        .match-details .extra {{
            color: #ffa502;
        }}
        .sample-section {{
            background: rgba(255,255,255,0.03);
            border-radius: 12px;
            margin-bottom: 15px;
            border: 1px solid rgba(255,255,255,0.1);
            overflow: hidden;
        }}
        .sample-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 20px;
            background: rgba(255,255,255,0.05);
            cursor: pointer;
        }}
        .sample-content {{
            display: none;
            padding: 15px;
        }}
        .sample-content.open {{
            display: block;
        }}
        .mini-eval {{
            display: flex;
            justify-content: space-between;
            padding: 8px 12px;
            background: rgba(255,255,255,0.03);
            border-radius: 6px;
            margin-bottom: 5px;
            cursor: pointer;
        }}
        .mini-eval:hover {{
            background: rgba(255,255,255,0.06);
        }}
        .detail-modal {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            z-index: 1000;
            padding: 40px;
            overflow-y: auto;
        }}
        .detail-modal.open {{
            display: block;
        }}
        .modal-content {{
            max-width: 800px;
            margin: 0 auto;
            background: #1a1a2e;
            border-radius: 12px;
            padding: 30px;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .modal-close {{
            float: right;
            font-size: 1.5rem;
            cursor: pointer;
            color: #888;
        }}
        .modal-close:hover {{
            color: #fff;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>LLM Judge Report - {module_upper}</h1>
            <p class="meta">Model: {model} | Generated: {timestamp[:19].replace('T', ' ')}</p>
        </header>

        <div class="summary-cards">
            <div class="card">
                <h3>Total Evaluations</h3>
                <div class="value rate">{len(evaluations)}</div>
            </div>
            <div class="card">
                <h3>Pass</h3>
                <div class="value pass">{summary['pass']}</div>
            </div>
            <div class="card">
                <h3>Fail</h3>
                <div class="value fail">{summary['fail']}</div>
            </div>
            <div class="card">
                <h3>Pass Rate</h3>
                <div class="value rate">{pass_rate:.1f}%</div>
            </div>
        </div>

        <div class="tabs">
            <div class="tab active" onclick="showTab('by-rubric')">By Rubric</div>
            <div class="tab" onclick="showTab('by-sample')">By Sample</div>
        </div>

        <div id="by-rubric" class="tab-content active">
'''

    # Add rubric sections
    for rubric_id, rubric_data in by_rubric.items():
        total = rubric_data['pass'] + rubric_data['fail']
        rate = (rubric_data['pass'] / total * 100) if total > 0 else 0

        html_content += f'''
            <div class="rubric-section">
                <div class="rubric-header" onclick="toggleRubric('{rubric_id}')">
                    <span class="rubric-title">{rubric_data['criterion']}</span>
                    <div class="rubric-stats">
                        <span class="stat pass">{rubric_data['pass']} Pass</span>
                        <span class="stat fail">{rubric_data['fail']} Fail</span>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {rate}%"></div>
                        </div>
                        <span>{rate:.0f}%</span>
                    </div>
                </div>
                <div id="{rubric_id}" class="rubric-content">
'''

        for eval in rubric_data['evals']:
            verdict_class = eval['verdict'].lower()
            reasoning_escaped = html.escape(eval['reasoning'])
            sid = eval['sample_id']
            sdata = sample_data.get(sid, {})
            input_data = sdata.get('input', {})
            expected = sdata.get('expected', {})
            actual = sdata.get('actual', {})

            # Format input summary
            brand_name = input_data.get('brand_name', 'N/A')
            title = input_data.get('title', 'N/A')[:100] + '...' if len(input_data.get('title', '')) > 100 else input_data.get('title', 'N/A')

            # Format outputs as JSON
            expected_json = json.dumps(expected, indent=2) if expected else '{}'
            actual_json = json.dumps(actual, indent=2) if actual else '{}'

            # Compare outputs
            match_info = compare_outputs(expected, actual)
            match_type = match_info['type']
            match_pct = match_info['percentage']

            # Match indicator HTML
            if match_type == 'exact':
                match_icon = '✓'
                match_label = 'MATCH'
            elif match_type == 'partial':
                match_icon = '◐'
                match_label = f'{match_pct:.0f}% Match'
            else:
                match_icon = '✗'
                match_label = 'MISMATCH'

            # Match details HTML
            match_details_html = ''
            if match_info['overlap_count'] > 0 or match_info['missing_count'] > 0 or match_info['extra_count'] > 0:
                details_parts = []
                if match_info['overlap_count'] > 0:
                    details_parts.append(f'<span class="overlap">✓ {match_info["overlap_count"]} matching</span>')
                if match_info['missing_count'] > 0:
                    details_parts.append(f'<span class="missing">✗ {match_info["missing_count"]} missing</span>')
                if match_info['extra_count'] > 0:
                    details_parts.append(f'<span class="extra">+ {match_info["extra_count"]} extra</span>')
                match_details_html = f'<div class="match-details">{" | ".join(details_parts)}</div>'

            eval_id = f"{rubric_id}_{sid}".replace('-', '_')

            html_content += f'''
                    <div class="eval-item {verdict_class}">
                        <div class="eval-header">
                            <span class="sample-id">{sid}</span>
                            <span class="match-indicator {match_type}">{match_icon} {match_label}</span>
                            <span class="verdict {verdict_class}">{eval['verdict']}</span>
                        </div>
                        <div class="input-section">
                            <div class="collapsible-header" onclick="toggleCollapsible('{eval_id}_input')">
                                <h4>Input Data</h4>
                                <span class="toggle-icon" id="{eval_id}_input_icon">▶</span>
                            </div>
                            <div id="{eval_id}_input" class="collapsible-content">
                                <div class="input-content">
                                    <div class="input-field"><strong>Brand:</strong> {html.escape(brand_name)}</div>
                                    <div class="input-field"><strong>Title:</strong> {html.escape(title)}</div>
                                </div>
                            </div>
                        </div>
                        <div class="output-comparison">
                            <div class="output-box expected">
                                <h4>Expected Output</h4>
                                <div class="output-content">{html.escape(expected_json)}</div>
                            </div>
                            <div class="output-box actual">
                                <h4>Actual Output</h4>
                                <div class="output-content">{html.escape(actual_json)}</div>
                            </div>
                        </div>
                        {match_details_html}
                        <div class="collapsible-header" onclick="toggleCollapsible('{eval_id}_reason')">
                            <h4 style="color: #888; font-size: 0.8rem;">Judge Reasoning</h4>
                            <span class="toggle-icon" id="{eval_id}_reason_icon">▶</span>
                        </div>
                        <div id="{eval_id}_reason" class="collapsible-content">
                            <div class="reasoning">{reasoning_escaped}</div>
                        </div>
                    </div>
'''

        html_content += '''
                </div>
            </div>
'''

    html_content += '''
        </div>

        <div id="by-sample" class="tab-content">
'''

    # Add sample sections
    for sample_id, sample_data in by_sample.items():
        total = sample_data['pass'] + sample_data['fail']
        rate = (sample_data['pass'] / total * 100) if total > 0 else 0

        html_content += f'''
            <div class="sample-section">
                <div class="sample-header" onclick="toggleSample('{sample_id}')">
                    <span class="sample-id">{sample_id}</span>
                    <div class="rubric-stats">
                        <span class="stat pass">{sample_data['pass']} Pass</span>
                        <span class="stat fail">{sample_data['fail']} Fail</span>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {rate}%"></div>
                        </div>
                    </div>
                </div>
                <div id="sample-{sample_id}" class="sample-content">
'''

        for eval in sample_data['evals']:
            verdict_class = eval['verdict'].lower()
            html_content += f'''
                    <div class="mini-eval" onclick="showDetail('{eval['rubric_id']}', '{sample_id}')">
                        <span>{eval['criterion']}</span>
                        <span class="verdict {verdict_class}">{eval['verdict']}</span>
                    </div>
'''

        html_content += '''
                </div>
            </div>
'''

    html_content += '''
        </div>
    </div>

    <script>
        function showTab(tabId) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            document.querySelector(`.tab[onclick="showTab('${tabId}')"]`).classList.add('active');
            document.getElementById(tabId).classList.add('active');
        }

        function toggleRubric(rubricId) {
            document.getElementById(rubricId).classList.toggle('open');
        }

        function toggleSample(sampleId) {
            document.getElementById('sample-' + sampleId).classList.toggle('open');
        }

        function toggleCollapsible(id) {
            const content = document.getElementById(id);
            const icon = document.getElementById(id + '_icon');
            content.classList.toggle('open');
            icon.classList.toggle('open');
        }
    </script>
</body>
</html>
'''

    return html_content


def main():
    import sys

    module = sys.argv[1] if len(sys.argv) > 1 else 'm01'

    result_file = get_latest_result(module)
    if not result_file:
        print(f"No results found for module {module}")
        return

    print(f"Generating report from: {result_file.name}")

    html_content = generate_report(result_file)

    output_file = SCRIPT_DIR / f"judge_report_{module}.html"
    with open(output_file, 'w') as f:
        f.write(html_content)

    print(f"Report saved to: {output_file}")

    # Open in browser
    import subprocess
    subprocess.run(['open', str(output_file)])


if __name__ == "__main__":
    main()
