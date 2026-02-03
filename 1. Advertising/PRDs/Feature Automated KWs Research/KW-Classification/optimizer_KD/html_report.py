"""
HTML Report Generator for Prompt Optimizer

Generates comprehensive HTML reports for optimization results.
Adapted from keyword-eval-agent for the KW-Classification optimizer.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


def generate_optimization_report(
    result_path: str,
    output_path: Optional[str] = None
) -> str:
    """
    Generate HTML report from optimization result JSON file.

    Args:
        result_path: Path to the optimization result JSON file
        output_path: Optional output path for HTML file (auto-generated if not specified)

    Returns:
        Path to the generated HTML file
    """
    # Load the result files
    result_path = Path(result_path)
    with open(result_path) as f:
        result_data = json.load(f)

    # Load prompts file
    prompts_path = result_path.with_suffix('.prompts.json')
    prompts_data = {}
    if prompts_path.exists():
        with open(prompts_path) as f:
            prompts_data = json.load(f)

    # Extract data
    module_name = result_path.stem.replace('optimization_', '').split('_')[0]
    original_prompt = prompts_data.get('original_prompt', '')
    improved_prompt = prompts_data.get('improved_prompt', '')
    iteration_prompts = prompts_data.get('iteration_prompts', [])

    # Generate HTML
    html = generate_html_report(
        prompt_name=module_name.upper(),
        prompt_text=original_prompt,
        improved_prompt=improved_prompt,
        result_data=result_data,
        iteration_prompts=iteration_prompts
    )

    # Save HTML
    if output_path is None:
        output_path = result_path.with_suffix('.html')
    else:
        output_path = Path(output_path)

    with open(output_path, 'w') as f:
        f.write(html)

    print(f"Report generated: {output_path}")
    return str(output_path)


def generate_html_report(
    prompt_name: str,
    prompt_text: str,
    improved_prompt: str,
    result_data: Dict[str, Any],
    iteration_prompts: List[str]
) -> str:
    """Generate comprehensive HTML report."""

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_str = datetime.now().strftime("%Y-%m-%d")

    # Extract key metrics
    success = result_data.get('success', False)
    best_iteration = result_data.get('best_iteration', 0)
    total_iterations = result_data.get('total_iterations', 0)
    original_accuracy = result_data.get('original_accuracy', 0)
    best_accuracy = result_data.get('best_accuracy', 0)
    scorers_used = result_data.get('scorers_used', [])
    iteration_results = result_data.get('iteration_results', [])

    improvement = best_accuracy - original_accuracy

    # Build iteration cards
    iter_cards_html = ""
    for ir in iteration_results:
        iter_num = ir.get('iteration', 0)
        accuracy = ir.get('accuracy', 0)
        pass_rate = ir.get('pass_rate', 0)
        failures = ir.get('failures_count', 0)
        improvements_count = len(ir.get('improvements', []))

        accuracy_class = "good" if accuracy >= 0.8 else "mid" if accuracy >= 0.5 else "bad"

        iter_cards_html += f"""
        <div class="iteration-card clickable" onclick="scrollToIteration({iter_num})">
            <div class="iteration-header">
                <span class="iteration-num">Iteration {iter_num}</span>
                <span class="iteration-accuracy {accuracy_class}">{accuracy:.1%}</span>
            </div>
            <div class="iteration-stats">
                <span>Pass Rate: {pass_rate:.1%}</span>
                <span>Failures: {failures}</span>
                <span>Suggestions: {improvements_count}</span>
            </div>
        </div>
        """

    # Build detailed iteration sections
    iter_details_html = ""
    for idx, ir in enumerate(iteration_results):
        iter_num = ir.get('iteration', 0)
        accuracy = ir.get('accuracy', 0)
        pass_rate = ir.get('pass_rate', 0)
        agg_scores = ir.get('aggregate_scores', {})
        failures_count = ir.get('failures_count', 0)
        improvements = ir.get('improvements', [])
        prompt_diff = ir.get('prompt_diff', '')
        prompt_length = ir.get('prompt_length', 0)
        iter_timestamp = ir.get('timestamp', '')

        # Get prompt text for this iteration
        prompt_text_iter = iteration_prompts[idx] if idx < len(iteration_prompts) else ''

        # Get test results for this iteration
        test_results = ir.get('test_results', [])

        # Build test results table
        test_rows_html = ""
        for i, tr in enumerate(test_results):
            keyword = tr.get('keyword', 'N/A')
            expected = tr.get('expected', {})
            output = tr.get('output', {})
            exact_match = tr.get('exact_match', False)
            scores = tr.get('scores', {})
            avg_score = tr.get('avg_score', 0)

            # Get classification values
            expected_class = expected.get('branding_scope_1', expected.get('branding_scope', 'N/A'))
            output_class = output.get('branding_scope', output.get('branding_scope_1', 'N/A'))
            confidence = output.get('confidence', 'N/A')
            reasoning = output.get('reasoning', '')[:80]

            row_class = "pass" if exact_match else "fail"
            status_icon = "✅" if exact_match else "❌"

            # Build mini scores
            failed_rules = [k for k, v in scores.items() if v < 0.7]
            if failed_rules:
                score_html = f"<span class='score-bad'>Failed: {', '.join(failed_rules[:2])}</span>"
            else:
                score_html = f"<span class='score-good'>All passed</span>"

            test_rows_html += f"""
            <tr class="{row_class}">
                <td>{i + 1}</td>
                <td class="keyword">{keyword}</td>
                <td><span class="tag expected">{expected_class if expected_class else 'null'}</span></td>
                <td><span class="tag output">{output_class if output_class else 'null'}</span></td>
                <td>{status_icon}</td>
                <td>{score_html}</td>
                <td class="reasoning">{reasoning}{'...' if len(str(reasoning)) > 80 else ''}</td>
            </tr>
            """

        # Build scores
        scores_html = ""
        for name, score in sorted(agg_scores.items(), key=lambda x: x[1]):
            bar_w = int(score * 100)
            color = "#2ecc71" if score >= 0.8 else "#f39c12" if score >= 0.5 else "#e74c3c"
            scores_html += f"""
            <div class="trace-score">
                <span>{name}</span>
                <div class="mini-bar" style="width:{bar_w}%;background:{color};"></div>
                <span>{score:.2f}</span>
            </div>
            """

        # Build improvements
        imp_html = ""
        for imp in improvements:
            severity = imp.get('severity', 'medium').upper()
            severity_class = "critical" if severity == "HIGH" else "warning"
            imp_html += f"""
            <div class="trace-improvement {severity_class}">
                <strong>[{imp.get('rule_id', 'N/A')}]</strong>
                <div class="trace-suggestion">{imp.get('suggestion', 'N/A')}</div>
            </div>
            """

        # Build diff
        diff_html = ""
        if prompt_diff and prompt_diff.strip():
            diff_lines = []
            for line in prompt_diff.split('\n'):
                escaped_line = line.replace("<", "&lt;").replace(">", "&gt;")
                if line.startswith('+') and not line.startswith('+++'):
                    diff_lines.append(f'<span class="diff-add">{escaped_line}</span>')
                elif line.startswith('-') and not line.startswith('---'):
                    diff_lines.append(f'<span class="diff-remove">{escaped_line}</span>')
                elif line.startswith('@@'):
                    diff_lines.append(f'<span class="diff-info">{escaped_line}</span>')
                else:
                    diff_lines.append(escaped_line)
            diff_formatted = '\n'.join(diff_lines)

            added = sum(1 for l in prompt_diff.split('\n') if l.startswith('+') and not l.startswith('+++'))
            removed = sum(1 for l in prompt_diff.split('\n') if l.startswith('-') and not l.startswith('---'))

            diff_html = f"""
            <div class="diff-section">
                <h4>📝 Prompt Changes</h4>
                <p class="diff-summary">
                    <span class="diff-add-badge">+{added} lines</span>
                    <span class="diff-remove-badge">-{removed} lines</span>
                </p>
                <pre class="diff-content">{diff_formatted}</pre>
            </div>
            """

        iter_header = f"🚀 Iteration {iter_num} - {accuracy:.1%} accuracy" if iter_num == 1 else f"Iteration {iter_num} - {accuracy:.1%} accuracy"

        iter_details_html += f"""
        <div class="iteration-detail" id="iter-{iter_num}">
            <h3>{iter_header}</h3>
            <p class="timestamp">{iter_timestamp}</p>

            <div class="trace-section">
                <h4>📊 Criteria Scores</h4>
                <div class="trace-scores">{scores_html}</div>
            </div>

            <div class="trace-section">
                <h4>📈 Metrics</h4>
                <div class="metrics-grid">
                    <div class="metric"><span class="metric-value">{accuracy:.1%}</span><span class="metric-label">Accuracy</span></div>
                    <div class="metric"><span class="metric-value">{pass_rate:.1%}</span><span class="metric-label">Pass Rate</span></div>
                    <div class="metric"><span class="metric-value">{failures_count}</span><span class="metric-label">Failures</span></div>
                    <div class="metric"><span class="metric-value">{prompt_length}</span><span class="metric-label">Prompt Chars</span></div>
                </div>
            </div>

            <div class="trace-section">
                <h4 class="collapsible" onclick="toggleCollapse(this)">🧪 Test Results ({len(test_results)} keywords)</h4>
                <div class="collapsible-content">
                    <div class="table-container">
                        <table class="test-table">
                            <thead>
                                <tr>
                                    <th>#</th>
                                    <th>Keyword</th>
                                    <th>Expected</th>
                                    <th>Output</th>
                                    <th>Match</th>
                                    <th>Scores</th>
                                    <th>Reasoning</th>
                                </tr>
                            </thead>
                            <tbody>
                                {test_rows_html}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div class="trace-section">
                <h4>💡 Improvement Suggestions ({len(improvements)})</h4>
                {imp_html if imp_html else '<p class="no-data">No improvements suggested - target reached!</p>'}
            </div>

            {diff_html}

            <div class="trace-section">
                <h4 class="collapsible collapsed" onclick="toggleCollapse(this)">📄 Full Prompt ({prompt_length} chars)</h4>
                <div class="collapsible-content hidden">
                    <pre class="prompt-box">{prompt_text_iter[:8000]}{'...' if len(prompt_text_iter) > 8000 else ''}</pre>
                </div>
            </div>
        </div>
        """

    # Get criteria with rubrics from result data
    criteria_with_rubrics = result_data.get('criteria_with_rubrics', [])

    # Build a lookup for criteria by name
    criteria_lookup = {c.get('name', ''): c for c in criteria_with_rubrics}

    # Fallback descriptions for backwards compatibility
    fallback_descriptions = {
        "ob_exact_match": "Checks if keyword contains an exact match of a brand name from the variations list",
        "ob_documented_typo": "Checks if keyword contains a documented typo/misspelling of the brand name",
        "ob_sub_brand": "Checks if keyword contains a sub-brand or product line name from related terms",
        "ob_manufacturer": "Checks if keyword contains the parent manufacturer name",
        "ob_short_brand": "Checks if keyword contains abbreviated or shortened brand name variants",
        "nb_similar_different_brand": "Ensures similar-sounding but different brands are NOT classified as OB",
        "nb_generic_keyword": "Ensures purely generic keywords without any brand terms are classified as NB",
        "nb_competitor_brand": "Ensures competitor brand keywords are NOT classified as OB",
        "nb_partial_word_match": "Ensures partial word matches (brand as substring) are NOT classified as OB",
        "nb_unlisted_typo": "Ensures unlisted/unknown typos are NOT incorrectly classified as OB",
    }

    # Build scorers/criteria list with multi-dimensional rubrics
    scorers_html = ""
    for scorer_name in scorers_used:
        # Try to get from criteria_with_rubrics first
        criterion = criteria_lookup.get(scorer_name, {})
        description = criterion.get('description') or fallback_descriptions.get(scorer_name, "Evaluates compliance with this classification criterion")
        dimensions = criterion.get('dimensions', [])
        examples = criterion.get('examples', {})
        criterion_type = criterion.get('criterion_type', '')

        # Determine type from name if not in criterion
        if not criterion_type:
            criterion_type = "OB" if scorer_name.startswith("ob_") else "NB" if scorer_name.startswith("nb_") else "CB" if scorer_name.startswith("cb_") else "General"
        type_class = "ob" if criterion_type == "OB" else "nb" if criterion_type == "NB" else "cb" if criterion_type == "CB" else "general"

        # Build multi-dimensional rubric HTML
        dimensions_html = ""
        if dimensions:
            dimensions_html = '<div class="rubric-dimensions">'
            for dim in dimensions:
                dim_name = dim.get('name', dim.get('dimension_id', 'Unknown'))
                weight = dim.get('weight', 0.33)
                levels = dim.get('levels', {})

                dimensions_html += f'''
                <div class="dimension">
                    <div class="dimension-header">
                        <span class="dimension-name">{dim_name}</span>
                        <span class="dimension-weight">{weight:.0%}</span>
                    </div>
                    <div class="dimension-levels">
                '''

                # Sort levels by score descending
                for score_key in sorted(levels.keys(), reverse=True):
                    score_desc = levels[score_key]
                    score_val = score_key.replace('score_', '') if 'score_' in score_key else score_key
                    score_class = "good" if "1" in str(score_val) else "partial" if "0.5" in str(score_val) else "bad"
                    dimensions_html += f'<div class="rubric-level {score_class}"><span class="rubric-score">{score_val}</span><span class="rubric-desc">{score_desc}</span></div>'

                dimensions_html += '</div></div>'
            dimensions_html += '</div>'

        # Build examples HTML
        examples_html = ""
        if examples:
            examples_html = '<div class="rubric-examples"><div class="examples-title">Examples:</div>'
            for score_key, example in examples.items():
                score_class = "good" if "1.0" in score_key else "partial" if "0.5" in score_key else "bad"
                examples_html += f'<div class="example {score_class}"><span class="example-score">{score_key}:</span> {example}</div>'
            examples_html += '</div>'

        scorers_html += f"""
        <div class="scorer-item">
            <div class="scorer-header">
                <span class="scorer-name">{scorer_name}</span>
                <span class="scorer-type-badge {type_class}">{criterion_type}</span>
            </div>
            <p class="scorer-desc">{description}</p>
            {dimensions_html}
            {examples_html}
        </div>
        """

    # Status indicator
    status_class = "success" if success else "warning"
    status_text = "✅ Target Reached" if success else "⚠️ Target Not Reached"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Optimization Report - {prompt_name} - {date_str}</title>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f7fa;
            color: #333;
            line-height: 1.6;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 20px;
        }}

        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}

        .header-meta {{
            display: flex;
            gap: 30px;
            flex-wrap: wrap;
            font-size: 14px;
            opacity: 0.9;
        }}

        .status-badge {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            margin-top: 15px;
        }}

        .status-badge.success {{
            background: rgba(46, 204, 113, 0.3);
            color: #2ecc71;
        }}

        .status-badge.warning {{
            background: rgba(243, 156, 18, 0.3);
            color: #f39c12;
        }}

        .card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}

        .card h2 {{
            color: #667eea;
            margin-bottom: 15px;
            font-size: 18px;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}

        .stat-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}

        .stat-value {{
            font-size: 36px;
            font-weight: bold;
            color: #667eea;
        }}

        .stat-value.good {{ color: #2ecc71; }}
        .stat-value.bad {{ color: #e74c3c; }}
        .stat-value.mid {{ color: #f39c12; }}

        .stat-label {{
            color: #666;
            font-size: 14px;
            margin-top: 5px;
        }}

        .table-container {{
            overflow-x: auto;
            max-height: 500px;
            overflow-y: auto;
        }}

        .test-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
        }}

        .test-table th {{
            background: #667eea;
            color: white;
            padding: 10px 8px;
            text-align: left;
            position: sticky;
            top: 0;
        }}

        .test-table td {{
            padding: 8px;
            border-bottom: 1px solid #e9ecef;
            vertical-align: top;
        }}

        .test-table tr.pass {{
            background: #f0fff4;
        }}

        .test-table tr.fail {{
            background: #fff5f5;
        }}

        .test-table tr:hover {{
            background: #f8f9fa !important;
        }}

        .keyword {{
            font-weight: 500;
            max-width: 200px;
            word-break: break-word;
        }}

        .tag {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-weight: bold;
            font-size: 11px;
        }}

        .tag.expected {{
            background: #e3f2fd;
            color: #1976d2;
        }}

        .tag.output {{
            background: #f3e5f5;
            color: #7b1fa2;
        }}

        .score-good {{
            color: #2ecc71;
            font-size: 11px;
        }}

        .score-bad {{
            color: #e74c3c;
            font-size: 11px;
        }}

        .reasoning {{
            font-size: 11px;
            color: #666;
            max-width: 200px;
        }}

        .iteration-summary {{
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            margin-bottom: 20px;
        }}

        .iteration-card {{
            background: white;
            border-radius: 8px;
            padding: 15px 20px;
            min-width: 180px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            border-left: 4px solid #667eea;
            cursor: pointer;
            transition: all 0.2s ease;
        }}

        .iteration-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }}

        .iteration-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }}

        .iteration-num {{
            font-weight: bold;
            color: #333;
        }}

        .iteration-accuracy {{
            font-size: 20px;
            font-weight: bold;
        }}

        .iteration-accuracy.good {{ color: #2ecc71; }}
        .iteration-accuracy.mid {{ color: #f39c12; }}
        .iteration-accuracy.bad {{ color: #e74c3c; }}

        .iteration-stats {{
            font-size: 12px;
            color: #666;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}

        .iteration-detail {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            border: 1px solid #e9ecef;
        }}

        .iteration-detail h3 {{
            color: #667eea;
            margin-bottom: 5px;
        }}

        .timestamp {{
            font-size: 12px;
            color: #999;
            margin-bottom: 15px;
        }}

        .trace-section {{
            margin-bottom: 20px;
        }}

        .trace-section h4 {{
            color: #495057;
            font-size: 14px;
            margin-bottom: 10px;
            border-bottom: 1px solid #e9ecef;
            padding-bottom: 5px;
        }}

        .trace-scores {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}

        .trace-score {{
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 13px;
        }}

        .trace-score span:first-child {{
            width: 180px;
            font-weight: 500;
        }}

        .mini-bar {{
            height: 12px;
            border-radius: 6px;
            min-width: 10px;
            max-width: 200px;
        }}

        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
        }}

        .metric {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}

        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
            display: block;
        }}

        .metric-label {{
            font-size: 12px;
            color: #666;
        }}

        .trace-improvement {{
            background: #fff8e1;
            padding: 12px;
            border-radius: 6px;
            margin-bottom: 10px;
            border-left: 3px solid #f39c12;
        }}

        .trace-improvement.critical {{
            background: #fff5f5;
            border-left-color: #e74c3c;
        }}

        .trace-suggestion {{
            font-size: 13px;
            color: #666;
            margin-top: 5px;
        }}

        .diff-section {{
            margin-bottom: 15px;
        }}

        .diff-content {{
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 15px;
            border-radius: 8px;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 11px;
            overflow-x: auto;
            white-space: pre;
            max-height: 400px;
            overflow-y: auto;
        }}

        .diff-add {{
            color: #4ade80;
            background: rgba(74, 222, 128, 0.1);
            display: block;
        }}

        .diff-remove {{
            color: #f87171;
            background: rgba(248, 113, 113, 0.1);
            display: block;
        }}

        .diff-info {{
            color: #60a5fa;
            font-weight: bold;
        }}

        .diff-summary {{
            margin-bottom: 10px;
            font-size: 13px;
        }}

        .diff-add-badge {{
            background: #065f46;
            color: #4ade80;
            padding: 3px 8px;
            border-radius: 4px;
            margin-right: 8px;
        }}

        .diff-remove-badge {{
            background: #7f1d1d;
            color: #f87171;
            padding: 3px 8px;
            border-radius: 4px;
        }}

        .prompt-box {{
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 15px;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 11px;
            max-height: 400px;
            overflow-y: auto;
            white-space: pre-wrap;
        }}

        .scorer-tag {{
            display: inline-block;
            background: #e3f2fd;
            color: #1976d2;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            margin: 4px;
        }}

        .no-data {{
            color: #999;
            font-style: italic;
        }}

        .scorer-item {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 12px 15px;
            margin-bottom: 10px;
            border-left: 4px solid #667eea;
        }}

        .scorer-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 6px;
        }}

        .scorer-name {{
            font-weight: 600;
            color: #333;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 13px;
        }}

        .scorer-type-badge {{
            font-size: 10px;
            font-weight: bold;
            padding: 2px 8px;
            border-radius: 10px;
        }}

        .scorer-type-badge.ob {{
            background: #e8f5e9;
            color: #2e7d32;
        }}

        .scorer-type-badge.nb {{
            background: #fff3e0;
            color: #ef6c00;
        }}

        .scorer-type-badge.cb {{
            background: #fce4ec;
            color: #c2185b;
        }}

        .scorer-type-badge.general {{
            background: #e3f2fd;
            color: #1565c0;
        }}

        .scorer-desc {{
            font-size: 13px;
            color: #666;
            margin: 0;
            line-height: 1.4;
        }}

        .rubric-dimensions {{
            margin-top: 12px;
            border-top: 1px solid #e9ecef;
            padding-top: 12px;
        }}

        .dimension {{
            margin-bottom: 16px;
            background: #f8f9fa;
            border-radius: 8px;
            padding: 12px;
        }}

        .dimension-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            padding-bottom: 8px;
            border-bottom: 1px solid #e0e0e0;
        }}

        .dimension-name {{
            font-weight: 600;
            color: #333;
            font-size: 13px;
        }}

        .dimension-weight {{
            background: #667eea;
            color: white;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: bold;
        }}

        .dimension-levels {{
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}

        .rubric-level {{
            display: flex;
            align-items: flex-start;
            gap: 10px;
            padding: 8px 10px;
            border-radius: 6px;
            font-size: 12px;
        }}

        .rubric-level.good {{
            background: #e8f5e9;
            border-left: 3px solid #2e7d32;
        }}

        .rubric-level.partial {{
            background: #fff8e1;
            border-left: 3px solid #f57c00;
        }}

        .rubric-level.bad {{
            background: #ffebee;
            border-left: 3px solid #c62828;
        }}

        .rubric-score {{
            font-weight: bold;
            min-width: 35px;
            padding: 3px 8px;
            border-radius: 4px;
            text-align: center;
            font-size: 11px;
        }}

        .rubric-level.good .rubric-score {{
            background: #2e7d32;
            color: white;
        }}

        .rubric-level.partial .rubric-score {{
            background: #f57c00;
            color: white;
        }}

        .rubric-level.bad .rubric-score {{
            background: #c62828;
            color: white;
        }}

        .rubric-desc {{
            color: #555;
            flex: 1;
            line-height: 1.4;
        }}

        .rubric-examples {{
            margin-top: 12px;
            padding: 10px;
            background: #f5f5f5;
            border-radius: 6px;
            font-size: 11px;
            border: 1px solid #e0e0e0;
        }}

        .examples-title {{
            font-weight: 600;
            color: #666;
            margin-bottom: 8px;
            font-size: 12px;
        }}

        .example {{
            margin-bottom: 6px;
            padding: 6px 8px;
            border-radius: 4px;
            line-height: 1.4;
        }}

        .example.good {{
            background: #e8f5e9;
            color: #1b5e20;
        }}

        .example.partial {{
            background: #fff8e1;
            color: #e65100;
        }}

        .example.bad {{
            background: #ffebee;
            color: #b71c1c;
        }}

        .example-score {{
            font-weight: bold;
            margin-right: 6px;
        }}

        .collapsible {{
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .collapsible::after {{
            content: '▼';
            font-size: 12px;
            transition: transform 0.3s;
        }}

        .collapsible.collapsed::after {{
            transform: rotate(-90deg);
        }}

        .collapsible-content {{
            max-height: 2000px;
            overflow: hidden;
            transition: max-height 0.3s;
            margin-top: 10px;
        }}

        .collapsible-content.hidden {{
            max-height: 0;
            margin-top: 0;
        }}

        footer {{
            text-align: center;
            color: #999;
            font-size: 12px;
            margin-top: 30px;
            padding: 20px;
        }}

        @media (max-width: 768px) {{
            .metrics-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
            .stats-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔧 Prompt Optimization Report</h1>
            <div class="header-meta">
                <span>📁 <strong>Module:</strong> {prompt_name}</span>
                <span>📅 <strong>Date:</strong> {timestamp}</span>
                <span>🔄 <strong>Iterations:</strong> {total_iterations}</span>
                <span>🎯 <strong>Best:</strong> {best_accuracy:.1%}</span>
            </div>
            <div class="status-badge {status_class}">{status_text}</div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{total_iterations}</div>
                <div class="stat-label">Total Iterations</div>
            </div>
            <div class="stat-card">
                <div class="stat-value {'good' if original_accuracy >= 0.8 else 'mid' if original_accuracy >= 0.5 else 'bad'}">{original_accuracy:.1%}</div>
                <div class="stat-label">Original Accuracy</div>
            </div>
            <div class="stat-card">
                <div class="stat-value {'good' if best_accuracy >= 0.8 else 'mid' if best_accuracy >= 0.5 else 'bad'}">{best_accuracy:.1%}</div>
                <div class="stat-label">Best Accuracy</div>
            </div>
            <div class="stat-card">
                <div class="stat-value {'good' if improvement > 0 else 'mid'}">{'+' if improvement >= 0 else ''}{improvement:.1%}</div>
                <div class="stat-label">Improvement</div>
            </div>
        </div>

        <div class="card">
            <h2>🔄 Iteration Overview</h2>
            <div class="iteration-summary">
                {iter_cards_html}
            </div>
        </div>

        <div class="card">
            <h2>📊 Iteration Details</h2>
            {iter_details_html}
        </div>

        <div class="card">
            <h2 class="collapsible" onclick="toggleCollapse(this)">🎯 Evaluation Criteria & Rubrics ({len(scorers_used)})</h2>
            <div class="collapsible-content">
                {scorers_html}
            </div>
        </div>

        <div class="card">
            <h2 class="collapsible collapsed" onclick="toggleCollapse(this)">📝 Original Prompt</h2>
            <div class="collapsible-content hidden">
                <pre class="prompt-box">{prompt_text[:10000]}{'...' if len(prompt_text) > 10000 else ''}</pre>
            </div>
        </div>

        <div class="card">
            <h2 class="collapsible collapsed" onclick="toggleCollapse(this)">✨ Best Prompt</h2>
            <div class="collapsible-content hidden">
                <pre class="prompt-box">{improved_prompt[:10000]}{'...' if len(improved_prompt) > 10000 else ''}</pre>
            </div>
        </div>

        <footer>
            Generated by KW-Classification Prompt Optimizer | {timestamp}
        </footer>
    </div>

    <script>
        function toggleCollapse(element) {{
            element.classList.toggle('collapsed');
            const content = element.nextElementSibling;
            content.classList.toggle('hidden');
        }}

        function scrollToIteration(iterNum) {{
            const targetElement = document.getElementById('iter-' + iterNum);
            if (targetElement) {{
                targetElement.scrollIntoView({{
                    behavior: 'smooth',
                    block: 'start'
                }});
                targetElement.style.transition = 'box-shadow 0.3s ease';
                targetElement.style.boxShadow = '0 0 20px rgba(102, 126, 234, 0.5)';
                setTimeout(() => {{
                    targetElement.style.boxShadow = '';
                }}, 1500);
            }}
        }}
    </script>
</body>
</html>
"""

    return html


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python html_report.py <result_json_path>")
        print("Example: python optimizer/html_report.py experiment_results/optimization_m02_v3_20260112_151312.json")
        sys.exit(1)

    result_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    generate_optimization_report(result_path, output_path)
