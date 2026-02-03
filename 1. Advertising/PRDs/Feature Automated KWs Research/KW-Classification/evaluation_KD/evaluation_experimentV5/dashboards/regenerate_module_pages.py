#!/usr/bin/env python3
"""
Regenerate module pages to match the exact format of m01.html.
Each module page loads data from modules_data.js and uses the same
simple rendering approach as m01.html.

Usage: python regenerate_module_pages.py [--force]
"""

import argparse
from pathlib import Path

# Module configurations matching m01.html format
MODULE_CONFIGS = {
    'm01': {
        'name': 'Extract Own Brand Entities',
        'type': 'Entity Extraction',
        'description': 'Entity Extraction: Extract brand entities from product listings',
        'model': 'gpt-4o-mini',
        'records': 50,
        'versions': ['v1', 'v2', 'v3'],
        'btId': None,
        'inputTokens': 1500,
        'outputTokens': 300
    },
    'm01a': {
        'name': 'Extract Own Brand Variations',
        'type': 'Extraction',
        'description': 'Extraction task: Generate typo and spelling variations for brand entities',
        'model': 'gpt-4o-mini',
        'records': 40,
        'versions': ['v1', 'v2'],
        'btId': '416420ef-b087-4f2b-9ef5-d82edf7cdfbf',
        'inputTokens': 1200,
        'outputTokens': 400
    },
    'm01b': {
        'name': 'Extract Brand Related Terms',
        'type': 'Extraction',
        'description': 'Extraction task: Extract terms related to brand entities',
        'model': 'gpt-4o-mini',
        'records': 60,
        'versions': ['v1'],
        'btId': '8b4a666e-b140-4ba7-ba67-6be650f3a8b0',
        'inputTokens': 1200,
        'outputTokens': 400
    },
    'm02': {
        'name': 'Classify Own Brand Keywords',
        'type': 'Binary Classifier',
        'description': 'Classification task: Determine if keyword relates to own brand',
        'model': 'gpt-4o-mini',
        'records': 916,  # From CSV
        'versions': ['v1'],
        'btId': '52bb2595-e579-44ca-ab2d-30e567049246',
        'inputTokens': 1500,
        'outputTokens': 100
    },
    'm02b': {
        'name': 'Classify Own Brand (Path B)',
        'type': 'Binary Classifier',
        'description': 'Classification task: Own brand classification using Path B method',
        'model': 'gpt-4o-mini',
        'records': 916,  # From CSV
        'versions': ['v1'],
        'btId': None,
        'inputTokens': 1500,
        'outputTokens': 100
    },
    'm04': {
        'name': 'Classify Competitor Keywords',
        'type': 'Binary Classifier',
        'description': 'Classification task: Identify competitor brand keywords',
        'model': 'gpt-4o-mini',
        'records': 1759,  # From CSV
        'versions': ['v1'],
        'btId': None,
        'alert': 'DATA ISSUE: Expected values incorrect for brands not in competitor_entities list',
        'inputTokens': 1500,
        'outputTokens': 100
    },
    'm04b': {
        'name': 'Classify Competitor (Path B)',
        'type': 'Binary Classifier',
        'description': 'Classification task: Competitor classification using Path B method',
        'model': 'gpt-4o-mini',
        'records': 1759,  # From CSV
        'versions': ['v1'],
        'btId': '2e81badf-ce5f-46da-9eec-d7b6f91584d7',
        'inputTokens': 1500,
        'outputTokens': 100
    },
    'm05': {
        'name': 'Classify Non-Branded Keywords',
        'type': 'Binary Classifier',
        'description': 'Classification task: Identify non-branded keywords',
        'model': 'gpt-4o-mini',
        'records': 1759,  # From CSV
        'versions': ['v1'],
        'btId': 'b591351d-6a14-42e2-8783-357c8b1556ab',
        'inputTokens': 1500,
        'outputTokens': 100
    },
    'm05b': {
        'name': 'Classify Non-Branded (Path B)',
        'type': 'Binary Classifier',
        'description': 'Classification task: Non-branded classification using Path B method',
        'model': 'gpt-4o-mini',
        'records': 1759,  # From CSV
        'versions': ['v1'],
        'btId': None,
        'inputTokens': 1500,
        'outputTokens': 100
    },
    'm06': {
        'name': 'Generate Product Taxonomy',
        'type': 'Extraction',
        'description': 'Extraction task: Generate hierarchical product type taxonomy',
        'model': 'gpt-4o-mini',
        'records': 30,
        'versions': ['v1'],
        'btId': 'ee5bb5ac-b613-4579-b462-a9b61455d34b',
        'inputTokens': 1200,
        'outputTokens': 400
    },
    'm07': {
        'name': 'Extract Product Attributes',
        'type': 'Extraction',
        'description': 'Extraction task: Extract product attributes from listings',
        'model': 'gpt-4o-mini',
        'records': 30,
        'versions': ['v1', 'v2'],
        'btId': 'c10225d0-4dbf-4b7d-8daa-80124142fdca',
        'inputTokens': 1200,
        'outputTokens': 400
    },
    'm08': {
        'name': 'Rank Product Attributes',
        'type': 'Ranking',
        'description': 'Ranking task: Rank product attributes by importance for search',
        'model': 'gpt-4o',
        'records': 20,
        'versions': ['v1', 'v2'],
        'btId': 'a81d8b7b-29e6-4cc4-8fa8-9fc23dcced67',
        'inputTokens': 2000,
        'outputTokens': 500
    },
    'm09': {
        'name': 'Identify Primary Intended Use',
        'type': 'Extraction',
        'description': 'Extraction task: Identify the primary intended use of a product',
        'model': 'gpt-4o-mini',
        'records': 100,
        'versions': ['v1'],
        'btId': None,
        'inputTokens': 1200,
        'outputTokens': 400
    },
    'm10': {
        'name': 'Validate Primary Intended Use',
        'type': 'Validation',
        'description': 'Validation task: Validate M09 output correctness',
        'model': 'gpt-4o-mini',
        'records': 100,
        'versions': ['v1'],
        'btId': None,
        'alert': 'JUDGE ISSUE: Strict string matching instead of semantic equivalence',
        'inputTokens': 2500,
        'outputTokens': 200
    },
    'm11': {
        'name': 'Identify Hard Constraints',
        'type': 'Extraction',
        'description': 'Extraction task: Identify product hard constraints',
        'model': 'gpt-4o-mini',
        'records': 100,
        'versions': ['v1', 'v2'],
        'btId': None,
        'inputTokens': 1200,
        'outputTokens': 400
    },
    'm12': {
        'name': 'Hard Constraint Violation Check',
        'type': 'Classifier',
        'description': 'Classification task: Check if keywords violate hard constraints',
        'model': 'gpt-4o-mini',
        'records': 442,  # From CSV (no ground truth labels)
        'versions': ['v1'],
        'btId': None,
        'inputTokens': 1800,
        'outputTokens': 150
    },
    'm12b': {
        'name': 'Hard Constraint Check (Path B)',
        'type': 'Classifier',
        'description': 'Classification task: Hard constraint check using Path B method',
        'model': 'gpt-4o-mini',
        'records': 442,  # From CSV
        'versions': ['v1'],
        'btId': None,
        'inputTokens': 1800,
        'outputTokens': 150
    },
    'm13': {
        'name': 'Product Type Check',
        'type': 'Binary Classifier',
        'description': 'Classification task: Check if product type matches',
        'model': 'gpt-4o-mini',
        'records': 438,  # From binary metrics
        'versions': ['v1'],
        'btId': None,
        'inputTokens': 1800,
        'outputTokens': 150
    },
    'm14': {
        'name': 'Primary Use Check Same Type',
        'type': 'Binary Classifier',
        'description': 'Classification task: Check if primary use matches product type',
        'model': 'gpt-4o-mini',
        'records': 228,  # From CSV
        'versions': ['v1'],
        'btId': None,
        'inputTokens': 1800,
        'outputTokens': 150
    },
    'm15': {
        'name': 'Substitute Check',
        'type': 'Binary Classifier',
        'description': 'Classification task: Check for substitute products',
        'model': 'gpt-4o-mini',
        'records': 210,  # From CSV (only 31 labeled)
        'versions': ['v1'],
        'btId': None,
        'inputTokens': 1800,
        'outputTokens': 150
    },
    'm16': {
        'name': 'Complementary Check',
        'type': 'Binary Classifier',
        'description': 'Classification task: Check for complementary products',
        'model': 'gpt-4o-mini',
        'records': 179,  # From CSV
        'versions': ['v1'],
        'btId': None,
        'inputTokens': 1800,
        'outputTokens': 150
    },
}

ALL_MODULES = ['m01', 'm01a', 'm01b', 'm02', 'm02b', 'm04', 'm04b', 'm05', 'm05b',
               'm06', 'm07', 'm08', 'm09', 'm10', 'm11', 'm12', 'm12b', 'm13', 'm14', 'm15', 'm16']


def get_model_recommendations(task_type: str, records: int) -> dict:
    """
    Get model recommendations based on task type and dataset size.
    Returns dict with model name as key and recommendation reason as value.
    Always provides both OpenAI and Gemini options for comparison.
    """
    is_large_dataset = records > 500

    recommendations = {
        'Extraction': {
            'GPT-4o-mini': 'Best price/quality for extraction tasks. Handles structured JSON output reliably.',
            'Gemini 2.0 Flash': 'Cheapest option at $0.10/1M input. Good for simple extractions with consistent schemas.',
        },
        'Binary Classifier': {
            'GPT-4o-mini': 'Optimal for binary yes/no decisions. Fast inference, low cost.',
            'Gemini 2.0 Flash': 'Most cost-effective at $0.10/1M. Great for high-volume binary classification.',
        },
        'Classifier': {
            'GPT-4o-mini': 'Best value for multi-class classification. Reliable category assignment.',
            'Gemini 2.0 Flash': 'Budget-friendly option. Suitable when cost matters more than marginal accuracy gains.',
        },
        'Ranking': {
            'GPT-4o': 'Superior reasoning for ranking tasks. Better at complex comparisons.',
            'o1-mini': 'Chain-of-thought reasoning for complex ranking criteria. Worth the cost for critical rankings.',
        },
        'Validation': {
            'GPT-4o-mini': 'Sufficient for validation/verification checks. Good accuracy at low cost.',
            'Gemini 2.0 Flash': 'Cheapest option for simple pass/fail validation logic.',
        },
    }

    # Filter out None values and return
    result = {k: v for k, v in recommendations.get(task_type, {
        'GPT-4o-mini': 'Default recommendation. Good balance of cost and quality.',
        'Gemini 2.0 Flash': 'Budget alternative. Lowest cost option.',
    }).items() if v is not None}

    return result


def generate_nav_tabs(active_module):
    """Generate navigation tabs HTML."""
    tabs = []
    for m in ALL_MODULES:
        active = 'active' if m == active_module else ''
        tabs.append(f'            <a href="{m}.html" class="nav-tab {active}">{m.upper()}</a>')
    return '\n'.join(tabs)


def generate_module_page(module_id: str, config: dict) -> str:
    """Generate HTML page matching m01.html format exactly."""

    input_tokens = config.get('inputTokens', 1500)
    output_tokens = config.get('outputTokens', 200)
    records = config['records']
    task_type = config['type']

    # Alert HTML - will be placed AFTER Model Cost Matrix
    alert_html = ''
    if config.get('alert'):
        alert_html = f'''
        <div style="background: rgba(239, 68, 68, 0.15); border: 1px solid #ef4444; border-radius: 8px; padding: 15px; margin: 20px 0;">
            <strong style="color: #ef4444;">⚠️ Known Issue:</strong>
            <span style="color: var(--text-secondary);"> {config["alert"]}</span>
        </div>'''

    # Model recommendations based on task type with reasons
    model_recommendations = get_model_recommendations(task_type, records)
    recommendations_json = str(model_recommendations).replace("'", '"')

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{module_id.upper()} - {config["name"]}</title>
    <link rel="stylesheet" href="../shared-styles.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="../modules_data.js"></script>
</head>
<body>
    <div class="container">
        <a href="../PROGRESS_DASHBOARD.html" class="back-link">← Back to Dashboard</a> | <a href="index.html" class="back-link">All Modules</a>

        <header>
            <h1>{module_id.upper()} - {config["name"]}</h1>
            <p>{config["description"]}</p>
        </header>

        <!-- Module Navigation -->
        <nav class="nav-tabs">
{generate_nav_tabs(module_id)}
        </nav>

        <!-- Module Info -->
        <div class="module-info">
            <div class="info-item">
                <div class="info-label">Task Type</div>
                <div class="info-value">{config["type"]}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Default Model</div>
                <div class="info-value">{config["model"]}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Dataset Records</div>
                <div class="info-value">{records}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Prompt Versions</div>
                <div class="info-value">{", ".join(config["versions"])}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Braintrust ID</div>
                <div class="info-value" style="font-size: 0.75rem;">{config["btId"] or "N/A"}</div>
            </div>
        </div>

        <!-- Stats Grid -->
        <div class="stats-grid" id="statsGrid"></div>

        <!-- Charts -->
        <div class="dashboard-grid">
            <div class="card">
                <h2>Pass Rate by Prompt Version</h2>
                <div class="chart-container"><canvas id="passRateChart"></canvas></div>
            </div>
            <div class="card">
                <h2>Model Comparison</h2>
                <div class="chart-container"><canvas id="modelChart"></canvas></div>
            </div>
        </div>

        <!-- Version History Table -->
        <div class="card">
            <h2>Evaluation History</h2>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Prompt Ver.</th>
                        <th>Model</th>
                        <th>Dataset</th>
                        <th>Pass Rate</th>
                        <th>Match Rate</th>
                        <th>Pass/Fail</th>
                        <th>Date</th>
                        <th>Braintrust</th>
                    </tr>
                </thead>
                <tbody id="historyTable"></tbody>
            </table>
        </div>

        <!-- Binary Classification Metrics (only for classifier modules) -->
        <div id="binaryMetricsSection" style="display: none;">
            <div class="card">
                <h2>Binary Classification Results</h2>
                <!-- Info row: Prompt, Model, Dataset -->
                <div id="binaryInfoRow" style="display: flex; gap: 20px; margin-bottom: 15px; flex-wrap: wrap;"></div>
                <!-- Horizontal Confusion Matrix -->
                <div id="confusionMatrix" style="display: flex; gap: 15px; justify-content: center; flex-wrap: wrap; margin-bottom: 20px;"></div>
                <!-- Metrics row -->
                <div id="metricsDisplay" style="display: flex; gap: 15px; justify-content: center; flex-wrap: wrap;"></div>
            </div>
        </div>

        <!-- Model Cost Matrix -->
        <div class="card">
            <h2>Model Cost Matrix</h2>
            <p style="color: var(--text-secondary); font-size: 0.85rem; margin-bottom: 15px;">
                Estimated costs for {records} records (~{input_tokens} input + ~{output_tokens} output tokens each)
            </p>
            <table class="model-matrix">
                <thead>
                    <tr>
                        <th style="text-align: left; width: 180px;">Model</th>
                        <th>Input $/1M</th>
                        <th>Output $/1M</th>
                        <th>Est. Cost</th>
                        <th>Quality</th>
                        <th style="text-align: left; width: 300px;">Why Recommended</th>
                    </tr>
                </thead>
                <tbody id="costMatrix"></tbody>
            </table>
            <div class="model-legend">
                <div class="legend-item"><div class="legend-color recommended"></div>★ Recommended for this task</div>
                <div class="legend-item"><div class="legend-color good"></div>Good value</div>
                <div class="legend-item"><div class="legend-color moderate"></div>Moderate</div>
                <div class="legend-item"><div class="legend-color expensive"></div>Expensive</div>
            </div>
        </div>
{alert_html}
        <!-- Suggestions -->
        <div class="card">
            <h2>Improvement Suggestions</h2>
            <div id="suggestions"></div>
        </div>
    </div>

    <script>
        // Module configuration
        const moduleId = '{module_id}';
        const taskType = '{task_type}';
        const totalInput = {records} * {input_tokens};
        const totalOutput = {records} * {output_tokens};

        // Task-specific model recommendations with reasons
        const recommendations = {recommendations_json};

        // Filter data for this module from modules_data.js
        // Exact match: m04 should NOT include m04b data
        const evaluations = progressData
            .filter(d => {{
                const mod = d.module.toLowerCase();
                // Exact match or match module followed by underscore (for dataset naming)
                return mod === moduleId || mod.startsWith(moduleId + '_');
            }})
            .map(d => ({{
                version: d.prompt_version || 'v1',
                model: d.model,
                dataset: d.dataset_name || d.data_source,
                passRate: d.pass_rate,
                matchRate: d.match_rate || 0,
                pass: d.summary?.pass || 0,
                fail: d.summary?.fail || 0,
                date: d.timestamp ? d.timestamp.split('T')[0] : '',
                btName: d.braintrust_name || '',
                btId: d.braintrust_id || ''
            }}))
            .sort((a, b) => b.passRate - a.passRate);

        // Get suggestions for this module
        const modKey = moduleId.toUpperCase().replace(/[AB]$/, '');
        const suggestions = suggestionsData
            .filter(s => s.module === modKey || s.module === moduleId.toUpperCase())
            .map(s => ({{
                rubric: s.rubric,
                criticality: s.criticality || 'Medium',
                passRate: s.passRate || 0,
                issue: s.specificIssue || s.analysisSummary || '',
                suggestion: s.detailedSuggestion || s.promptChange || s.rubricChange || '',
                status: s.validated ? 'validated' : 'pending'
            }}));

        // Model pricing with task-specific recommendations
        const models = [
            {{ name: 'GPT-4o-mini', provider: 'openai', input: 0.15, output: 0.60, quality: 85 }},
            {{ name: 'GPT-4o', provider: 'openai', input: 2.50, output: 10.00, quality: 95 }},
            {{ name: 'GPT-5', provider: 'openai', input: 10.00, output: 30.00, quality: 98 }},
            {{ name: 'Gemini 2.0 Flash', provider: 'google', input: 0.10, output: 0.40, quality: 82 }},
            {{ name: 'Gemini 1.5 Pro', provider: 'google', input: 1.25, output: 5.00, quality: 88 }},
            {{ name: 'o1-mini', provider: 'openai', input: 3.00, output: 12.00, quality: 92 }},
        ].map(m => ({{
            ...m,
            recommended: recommendations[m.name] ? true : false,
            reason: recommendations[m.name] || null
        }}));

        // Calculate stats
        const bestPassRate = evaluations.length > 0 ? Math.max(...evaluations.map(e => e.passRate)) : 0;
        const latestEval = evaluations[0] || {{ pass: 0, fail: 0, passRate: 0 }};
        const firstEval = evaluations[evaluations.length - 1] || {{ passRate: 0 }};
        const improvement = latestEval.passRate - firstEval.passRate;

        // Render stats grid
        document.getElementById('statsGrid').innerHTML = `
            <div class="stat-card">
                <div class="stat-value blue">${{bestPassRate}}%</div>
                <div class="stat-label">Best Pass Rate</div>
            </div>
            <div class="stat-card">
                <div class="stat-value ${{improvement >= 0 ? 'green' : 'red'}}">${{improvement >= 0 ? '+' : ''}}${{improvement.toFixed(0)}}%</div>
                <div class="stat-label">Improvement</div>
            </div>
            <div class="stat-card">
                <div class="stat-value green">${{latestEval.pass}}</div>
                <div class="stat-label">Passing Tests</div>
            </div>
            <div class="stat-card">
                <div class="stat-value red">${{latestEval.fail}}</div>
                <div class="stat-label">Failing Tests</div>
            </div>
        `;

        // Render history table
        document.getElementById('historyTable').innerHTML = evaluations.length > 0
            ? evaluations.map(e => {{
                const passColor = e.passRate >= 70 ? '#22c55e' : e.passRate >= 50 ? '#eab308' : '#ef4444';
                const btLink = e.btName ? `https://www.braintrust.dev/app/KCC/p/Keyword-Classification-Pipeline-V1.1/experiments/${{encodeURIComponent(e.btName)}}` : '#';
                return `
                    <tr>
                        <td><span class="version-badge ${{e.version}}">${{e.version}}</span></td>
                        <td><span class="model-badge">${{e.model}}</span></td>
                        <td style="font-size: 0.8rem; color: var(--text-secondary);">${{e.dataset}}</td>
                        <td>
                            <span style="color: ${{passColor}}; font-weight: 600;">${{e.passRate}}%</span>
                            <div class="rate-bar" style="width: 60px; margin-top: 4px;">
                                <div class="rate-bar-fill" style="width: ${{e.passRate}}%; background: ${{passColor}};"></div>
                            </div>
                        </td>
                        <td>${{e.matchRate}}%</td>
                        <td><span style="color: #22c55e;">${{e.pass}}</span> / <span style="color: #ef4444;">${{e.fail}}</span></td>
                        <td style="font-size: 0.8rem;">${{e.date}}</td>
                        <td>${{e.btName ? `<a href="${{btLink}}" target="_blank" style="color: var(--accent-blue); text-decoration: none; font-size: 0.8rem;">View ↗</a>` : '-'}}</td>
                    </tr>
                `;
            }}).join('')
            : '<tr><td colspan="8" style="text-align: center; color: var(--text-secondary);">No evaluation data available</td></tr>';

        // Render cost matrix
        document.getElementById('costMatrix').innerHTML = models.map(m => {{
            const cost = (totalInput / 1_000_000) * m.input + (totalOutput / 1_000_000) * m.output;
            const costClass = m.recommended ? 'recommended' : cost < 0.05 ? 'good' : cost < 0.50 ? 'moderate' : 'expensive';
            const providerBadge = `<span class="provider-badge ${{m.provider}}">${{m.provider === 'openai' ? 'OpenAI' : 'Google'}}</span>`;
            const reasonCell = m.reason
                ? `<span style="color: #22c55e;">★</span> <span style="color: var(--text-secondary); font-size: 0.8rem;">${{m.reason}}</span>`
                : '<span style="color: #64748b;">-</span>';
            return `
                <tr>
                    <td class="model-name">${{m.name}}${{providerBadge}}</td>
                    <td style="color: var(--text-secondary);">$${{m.input.toFixed(2)}}</td>
                    <td style="color: var(--text-secondary);">$${{m.output.toFixed(2)}}</td>
                    <td class="cost-cell ${{costClass}}">$${{cost.toFixed(4)}}</td>
                    <td>
                        <div style="display: flex; align-items: center; gap: 4px;">
                            <div style="width: 50px; height: 6px; background: #334155; border-radius: 3px;">
                                <div style="width: ${{m.quality}}%; height: 100%; background: ${{m.quality >= 90 ? '#22c55e' : '#3b82f6'}}; border-radius: 3px;"></div>
                            </div>
                            <span style="font-size: 0.7rem; color: #94a3b8;">${{m.quality}}</span>
                        </div>
                    </td>
                    <td style="text-align: left;">${{reasonCell}}</td>
                </tr>
            `;
        }}).join('');

        // Render suggestions
        document.getElementById('suggestions').innerHTML = suggestions.length > 0
            ? suggestions.map(s => {{
                const statusClass = s.status === 'validated' ? 'validated' : s.status === 'applied' ? 'validated' : '';
                const priorityColor = s.criticality === 'High' ? '#ef4444' : s.criticality === 'Medium' ? '#eab308' : '#22c55e';
                return `
                    <div class="suggestion-item ${{statusClass}}">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <strong style="color: var(--text-primary);">${{s.rubric}}</strong>
                            <div>
                                <span style="font-size: 0.7rem; padding: 2px 8px; border-radius: 4px; background: ${{priorityColor}}; color: white;">${{s.criticality}}</span>
                                <span class="suggestion-status ${{s.status}}">${{s.status}}</span>
                            </div>
                        </div>
                        ${{s.passRate ? `<p style="color: var(--text-secondary); font-size: 0.85rem; margin-bottom: 6px;"><strong>Pass Rate:</strong> ${{s.passRate}}%</p>` : ''}}
                        <p style="color: var(--text-secondary); font-size: 0.85rem; margin-bottom: 6px;">
                            <strong>Issue:</strong> ${{s.issue}}
                        </p>
                        <p style="color: var(--accent-blue); font-size: 0.85rem;">
                            <strong>Suggestion:</strong> ${{s.suggestion}}
                        </p>
                    </div>
                `;
            }}).join('')
            : '<p style="color: var(--text-secondary);">No suggestions available for this module.</p>';

        // Render binary classification metrics (if available)
        if (typeof binaryMetrics !== 'undefined' && binaryMetrics[moduleId]) {{
            const m = binaryMetrics[moduleId];
            const labels = m.labels || {{}};
            document.getElementById('binaryMetricsSection').style.display = 'block';

            // Get experiment info from latest evaluation
            const latest = evaluations[0] || {{}};
            const promptVer = latest.version || 'v1';
            const model = latest.model || '-';
            const dataset = latest.dataset || '-';

            // Compact table with all metrics in one row
            const getColor = (val, t1 = 70, t2 = 50) => val >= t1 ? '#22c55e' : val >= t2 ? '#eab308' : '#ef4444';
            const getMccColor = (val) => val >= 0.5 ? '#22c55e' : val >= 0.2 ? '#eab308' : '#ef4444';

            // Labels for header (shorter)
            const tpLbl = labels.tp || '';
            const tnLbl = labels.tn && labels.tn !== '-' ? labels.tn : '';
            const fpLbl = labels.fp && labels.fp !== '-' ? labels.fp : '';
            const fnLbl = labels.fn || '';

            const tableHtml = `
                <table style="width: 100%; border-collapse: collapse; font-size: 0.72rem;">
                    <thead>
                        <tr style="border-bottom: 1px solid var(--border-color);">
                            <th style="padding: 5px 4px; text-align: left; color: #64748b; font-weight: 500;">Prompt</th>
                            <th style="padding: 5px 4px; text-align: left; color: #64748b; font-weight: 500;">Model</th>
                            <th style="padding: 5px 4px; text-align: left; color: #64748b; font-weight: 500; max-width: 120px;">Dataset</th>
                            <th style="padding: 5px 4px; text-align: right; color: #94a3b8; font-weight: 500;">N</th>
                            <th style="padding: 5px 4px; text-align: right; color: #22c55e; font-weight: 500;" title="${{tpLbl}}">TP</th>
                            <th style="padding: 5px 4px; text-align: right; color: #3b82f6; font-weight: 500;" title="${{tnLbl}}">TN</th>
                            <th style="padding: 5px 4px; text-align: right; color: #ef4444; font-weight: 500;" title="${{fpLbl}}">FP</th>
                            <th style="padding: 5px 4px; text-align: right; color: #eab308; font-weight: 500;" title="${{fnLbl}}">FN</th>
                            <th style="padding: 5px 4px; text-align: right; color: #94a3b8; font-weight: 500;">Acc</th>
                            <th style="padding: 5px 4px; text-align: right; color: #94a3b8; font-weight: 500;">Prec</th>
                            <th style="padding: 5px 4px; text-align: right; color: #94a3b8; font-weight: 500;">Rec</th>
                            <th style="padding: 5px 4px; text-align: right; color: #94a3b8; font-weight: 500;">F1</th>
                            <th style="padding: 5px 4px; text-align: right; color: #94a3b8; font-weight: 500;">MCC</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="padding: 6px 4px; text-align: left;"><span class="version-badge ${{promptVer}}" style="font-size: 0.65rem; padding: 2px 6px;">${{promptVer}}</span></td>
                            <td style="padding: 6px 4px; text-align: left; color: #94a3b8;">${{model}}</td>
                            <td style="padding: 6px 4px; text-align: left; color: #64748b; max-width: 120px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${{dataset}}">${{dataset}}</td>
                            <td style="padding: 6px 4px; text-align: right; font-weight: 600;">${{m.total.toLocaleString()}}</td>
                            <td style="padding: 6px 4px; text-align: right; font-weight: 600; color: #22c55e;">${{m.tp}}</td>
                            <td style="padding: 6px 4px; text-align: right; font-weight: 600; color: #3b82f6;">${{m.tn}}</td>
                            <td style="padding: 6px 4px; text-align: right; font-weight: 600; color: #ef4444;">${{m.fp}}</td>
                            <td style="padding: 6px 4px; text-align: right; font-weight: 600; color: #eab308;">${{m.fn}}</td>
                            <td style="padding: 6px 4px; text-align: right; font-weight: 600; color: ${{getColor(m.accuracy)}};">${{m.accuracy}}%</td>
                            <td style="padding: 6px 4px; text-align: right; font-weight: 600; color: ${{getColor(m.precision)}};">${{m.precision}}%</td>
                            <td style="padding: 6px 4px; text-align: right; font-weight: 600; color: ${{getColor(m.recall)}};">${{m.recall}}%</td>
                            <td style="padding: 6px 4px; text-align: right; font-weight: 600; color: ${{getColor(m.f1)}};">${{m.f1}}%</td>
                            <td style="padding: 6px 4px; text-align: right; font-weight: 600; color: ${{getMccColor(m.mcc)}};">${{m.mcc.toFixed(3)}}</td>
                        </tr>
                    </tbody>
                </table>
                <div style="display: flex; justify-content: space-between; margin-top: 6px; font-size: 0.65rem; color: #64748b;">
                    <span>TP=${{tpLbl}} TN=${{tnLbl}} FP=${{fpLbl}} FN=${{fnLbl}}</span>
                    ${{m.note ? `<span style="color: #eab308;"><em>${{m.note}}</em></span>` : ''}}
                </div>
            `;
            document.getElementById('confusionMatrix').innerHTML = tableHtml;
            document.getElementById('binaryInfoRow').style.display = 'none';
            document.getElementById('metricsDisplay').style.display = 'none';
        }}

        // Charts
        if (evaluations.length > 0) {{
            // Pass Rate Chart
            const chartLabels = evaluations.map(e => `${{e.version}} (${{e.model}})`).reverse();
            const chartData = evaluations.map(e => e.passRate).reverse();

            new Chart(document.getElementById('passRateChart'), {{
                type: 'line',
                data: {{
                    labels: chartLabels,
                    datasets: [{{
                        label: 'Pass Rate %',
                        data: chartData,
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        fill: true,
                        tension: 0.3,
                        pointRadius: 6
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{ legend: {{ labels: {{ color: '#94a3b8' }} }} }},
                    scales: {{
                        y: {{ beginAtZero: true, max: 100, grid: {{ color: '#334155' }}, ticks: {{ color: '#94a3b8' }} }},
                        x: {{ grid: {{ color: '#334155' }}, ticks: {{ color: '#94a3b8' }} }}
                    }}
                }}
            }});

            // Model Comparison Chart
            const modelStats = {{}};
            evaluations.forEach(e => {{
                if (!modelStats[e.model]) modelStats[e.model] = {{ total: 0, count: 0 }};
                modelStats[e.model].total += e.passRate;
                modelStats[e.model].count++;
            }});
            const modelLabels = Object.keys(modelStats);
            const modelAvgs = modelLabels.map(m => Math.round(modelStats[m].total / modelStats[m].count));
            const barColors = ['#60a5fa', '#22c55e', '#a855f7', '#f59e0b', '#ef4444', '#06b6d4'];

            new Chart(document.getElementById('modelChart'), {{
                type: 'bar',
                data: {{
                    labels: modelLabels,
                    datasets: [{{
                        label: 'Avg Pass Rate',
                        data: modelAvgs,
                        backgroundColor: barColors.slice(0, modelLabels.length),
                        borderRadius: 6
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{ legend: {{ display: false }} }},
                    scales: {{
                        y: {{ beginAtZero: true, max: 100, grid: {{ color: '#334155' }}, ticks: {{ color: '#94a3b8' }} }},
                        x: {{ grid: {{ display: false }}, ticks: {{ color: '#94a3b8' }} }}
                    }}
                }}
            }});
        }} else {{
            document.getElementById('passRateChart').parentElement.innerHTML = '<p style="color: var(--text-secondary); text-align: center; padding: 100px 0;">No evaluation data available</p>';
            document.getElementById('modelChart').parentElement.innerHTML = '<p style="color: var(--text-secondary); text-align: center; padding: 100px 0;">No evaluation data available</p>';
        }}
    </script>
</body>
</html>
'''


def main():
    parser = argparse.ArgumentParser(description='Regenerate module pages')
    parser.add_argument('--force', action='store_true', help='Overwrite all files')
    args = parser.parse_args()

    output_dir = Path(__file__).parent / 'modules'
    output_dir.mkdir(exist_ok=True)

    generated = []
    skipped = []

    for module_id, config in MODULE_CONFIGS.items():
        output_file = output_dir / f'{module_id}.html'

        # Overwrite if --force, otherwise skip existing
        if output_file.exists() and not args.force:
            skipped.append(module_id)
            continue

        html = generate_module_page(module_id, config)
        output_file.write_text(html)
        generated.append(module_id)
        print(f'Generated: {output_file.name}')

    print(f'\nGenerated: {len(generated)} files')
    if skipped:
        print(f'Skipped (already exist, use --force to overwrite): {", ".join(skipped)}')


if __name__ == '__main__':
    main()
