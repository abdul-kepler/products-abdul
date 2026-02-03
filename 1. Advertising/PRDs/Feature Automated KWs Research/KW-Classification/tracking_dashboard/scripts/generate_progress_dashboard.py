#!/usr/bin/env python3
"""
Generate Progress Dashboard from progress_history.yaml
"""

import json
import yaml
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent  # tracking_dashboard/
DATA_DIR = PROJECT_DIR / "data"
DASHBOARDS_DIR = PROJECT_DIR / "dashboards"

HISTORY_FILE = DATA_DIR / "progress_history.yaml"
SUGGESTIONS_FILE = DATA_DIR / "improvement_suggestions.json"
APPLIED_FILE = DATA_DIR / "applied_improvements.yaml"
MAPPINGS_FILE = DATA_DIR / "experiment_mappings.yaml"
IMPROVEMENT_HISTORY_FILE = DATA_DIR / "improvement_history.yaml"
BINARY_METRICS_FILE = DASHBOARDS_DIR / "binary_metrics.json"
OUTPUT_FILE = DASHBOARDS_DIR / "tracking_dashboard.html"


def load_experiment_mappings() -> dict:
    """Load experiment mappings with Braintrust metadata."""
    if MAPPINGS_FILE.exists():
        with open(MAPPINGS_FILE) as f:
            data = yaml.safe_load(f)
            # Create lookup by local_file for enrichment
            lookup = {}
            for exp in data.get('experiments', []):
                local_file = exp.get('local_file', '')
                if local_file:
                    # Use filename only for matching
                    filename = Path(local_file).name
                    lookup[filename] = exp
            return lookup
    return {}


def load_progress_history() -> list:
    """Load progress history."""
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE) as f:
            data = yaml.safe_load(f)
            return data.get('runs', [])
    return []


def load_suggestions() -> list:
    """Load improvement suggestions."""
    if SUGGESTIONS_FILE.exists():
        with open(SUGGESTIONS_FILE) as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                if 'modules' in data:
                    all_suggestions = []
                    for module, module_data in data['modules'].items():
                        suggestions = module_data.get('suggestions', [])
                        for s in suggestions:
                            s['module'] = module
                        all_suggestions.extend(suggestions)
                    return all_suggestions
                elif 'suggestions' in data:
                    return data['suggestions']
    return []


def load_applied_improvements() -> dict:
    """Load applied improvements tracking."""
    if APPLIED_FILE.exists():
        with open(APPLIED_FILE) as f:
            return yaml.safe_load(f) or {}
    return {}


def load_improvement_history() -> dict:
    """Load version-based improvement history."""
    if IMPROVEMENT_HISTORY_FILE.exists():
        with open(IMPROVEMENT_HISTORY_FILE) as f:
            return yaml.safe_load(f) or {}
    return {}


def load_binary_metrics() -> dict:
    """Load binary classification metrics."""
    if BINARY_METRICS_FILE.exists():
        with open(BINARY_METRICS_FILE) as f:
            return json.load(f)
    return {}


def generate_dashboard():
    """Generate the progress dashboard HTML."""
    # Load data
    progress_data = load_progress_history()
    suggestions_data = load_suggestions()
    applied_data = load_applied_improvements()
    experiment_mappings = load_experiment_mappings()
    improvement_history = load_improvement_history()
    binary_metrics = load_binary_metrics()

    print(f"Loaded {len(progress_data)} progress runs")
    print(f"Loaded {len(suggestions_data)} suggestions")
    print(f"Loaded applied improvements for {len(applied_data.get('prompt_versions', {}))} modules")
    print(f"Loaded {len(experiment_mappings)} experiment mappings")
    print(f"Loaded improvement history for {len(improvement_history.get('modules', {}))} modules")
    print(f"Loaded binary metrics for {len(binary_metrics)} modules")

    # Enrich progress data with Braintrust metadata
    enriched_count = 0
    for run in progress_data:
        data_source = run.get('data_source', '')
        if data_source and data_source in experiment_mappings:
            mapping = experiment_mappings[data_source]
            run['braintrust_id'] = mapping.get('braintrust_experiment_id')
            run['braintrust_name'] = mapping.get('braintrust_name')
            run['dataset_id'] = mapping.get('dataset_id')
            run['dataset_name'] = mapping.get('dataset_name')
            run['prompt_id'] = mapping.get('prompt_id')
            run['prompt_version_id'] = mapping.get('prompt_version_id')
            run['temperature'] = mapping.get('temperature')
            run['created'] = mapping.get('created')
            enriched_count += 1

    print(f"Enriched {enriched_count} progress runs with Braintrust metadata")

    # Read template
    template_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prompt Version Progress Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: #1e293b;
            --text-primary: #f1f5f9;
            --text-secondary: #94a3b8;
            --accent-blue: #3b82f6;
            --accent-green: #22c55e;
            --accent-yellow: #eab308;
            --accent-red: #ef4444;
            --accent-purple: #a855f7;
            --border-color: #334155;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 20px;
        }

        .container { max-width: 1400px; margin: 0 auto; }

        header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--border-color);
        }

        header h1 {
            font-size: 2rem;
            margin-bottom: 8px;
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        header p { color: var(--text-secondary); }

        .module-selector {
            display: flex;
            gap: 10px;
            justify-content: center;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }

        .module-btn {
            padding: 10px 20px;
            border: 1px solid var(--border-color);
            background: var(--bg-secondary);
            color: var(--text-primary);
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 14px;
        }

        .module-btn:hover { border-color: var(--accent-blue); }
        .module-btn.active { background: var(--accent-blue); border-color: var(--accent-blue); }

        .dashboard-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }

        @media (max-width: 1000px) { .dashboard-grid { grid-template-columns: 1fr; } }

        .card {
            background: var(--bg-card);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid var(--border-color);
        }

        .card h2 {
            font-size: 1.1rem;
            margin-bottom: 15px;
            color: var(--text-secondary);
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .card h2::before {
            content: '';
            width: 4px;
            height: 20px;
            background: var(--accent-blue);
            border-radius: 2px;
        }

        .chart-container { position: relative; height: 300px; }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }

        .stat-card {
            background: var(--bg-secondary);
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            border: 1px solid var(--border-color);
        }

        .stat-value { font-size: 1.8rem; font-weight: 700; margin-bottom: 5px; }
        .stat-label { font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase; }
        .stat-value.green { color: var(--accent-green); }
        .stat-value.yellow { color: var(--accent-yellow); }
        .stat-value.red { color: var(--accent-red); }
        .stat-value.blue { color: var(--accent-blue); }

        .full-width { grid-column: 1 / -1; }

        .progress-table { width: 100%; border-collapse: collapse; }
        .progress-table th, .progress-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }
        .progress-table th { color: var(--text-secondary); font-weight: 500; font-size: 0.85rem; text-transform: uppercase; }
        .progress-table tr:hover { background: rgba(59, 130, 246, 0.1); }

        .version-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .version-badge.v1 { background: #374151; color: #9ca3af; }
        .version-badge.v2 { background: #1e3a5f; color: #60a5fa; }
        .version-badge.v3 { background: #14532d; color: #4ade80; }

        .model-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            background: var(--bg-primary);
            color: var(--text-secondary);
        }

        .rate-bar { width: 100%; height: 8px; background: var(--bg-primary); border-radius: 4px; overflow: hidden; }
        .rate-bar-fill { height: 100%; border-radius: 4px; transition: width 0.3s; }

        .trend-indicator { display: inline-flex; align-items: center; gap: 4px; font-size: 0.85rem; }
        .trend-up { color: var(--accent-green); }
        .trend-down { color: var(--accent-red); }
        .trend-same { color: var(--text-secondary); }

        .suggestions-list { list-style: none; }
        .suggestions-list li {
            padding: 12px;
            border-left: 3px solid var(--accent-blue);
            background: rgba(59, 130, 246, 0.1);
            margin-bottom: 10px;
            border-radius: 0 8px 8px 0;
        }
        .suggestions-list li.validated { border-left-color: var(--accent-green); background: rgba(34, 197, 94, 0.1); }

        .suggestion-status { font-size: 0.75rem; padding: 2px 8px; border-radius: 4px; margin-left: 8px; }
        .suggestion-status.validated { background: var(--accent-green); color: white; }
        .suggestion-status.proposed { background: var(--accent-yellow); color: #000; }
        .suggestion-status.applied { background: var(--accent-green); color: white; }
        .suggestion-status.pending { background: var(--accent-yellow); color: #000; }
        .suggestion-status.data-fix { background: var(--accent-red); color: white; }

        .version-card { background: var(--bg-primary); border-radius: 8px; padding: 15px; margin-bottom: 15px; border-left: 4px solid var(--accent-blue); }
        .version-card.has-improvements { border-left-color: var(--accent-green); }
        .version-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .version-title { font-weight: 600; font-size: 1rem; }
        .version-meta { font-size: 0.8rem; color: var(--text-secondary); }
        .improvement-item { padding: 8px 12px; background: rgba(34, 197, 94, 0.1); border-radius: 6px; margin: 8px 0; font-size: 0.85rem; }
        .improvement-item .rubric { color: var(--accent-green); font-weight: 500; }
        .improvement-item .change { color: var(--text-secondary); margin-top: 4px; font-size: 0.8rem; }
        .no-improvements { color: var(--text-secondary); font-style: italic; font-size: 0.85rem; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📈 Prompt Version Progress Dashboard</h1>
            <p>Track LLM Judge Pass Rate & Match Rate across prompt versions and models</p>
        </header>

        <div class="module-selector" id="moduleSelector"></div>
        <div class="stats-grid" id="statsGrid"></div>

        <div class="dashboard-grid">
            <div class="card">
                <h2>Pass Rate by Version</h2>
                <div class="chart-container"><canvas id="passRateChart"></canvas></div>
            </div>
            <div class="card">
                <h2>Model Comparison</h2>
                <div class="chart-container"><canvas id="modelCompareChart"></canvas></div>
            </div>
            <div class="card full-width">
                <h2>Version History</h2>
                <table class="progress-table" id="progressTable">
                    <thead>
                        <tr>
                            <th>Module</th>
                            <th>Version</th>
                            <th>Model</th>
                            <th>Dataset</th>
                            <th>Pass Rate</th>
                            <th>Match Rate</th>
                            <th>Pass/Fail</th>
                            <th>Trend</th>
                            <th>BT Link</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
            <div class="card full-width" id="binaryMetricsCard" style="display: none;">
                <h2>📊 Binary Classification Metrics</h2>
                <p style="color: var(--text-secondary); font-size: 0.85rem; margin-bottom: 15px;">
                    Classifier performance metrics from full dataset evaluation
                </p>
                <div id="binaryMetricsTable"></div>
            </div>
            <div class="card full-width">
                <h2>Applied Improvements (by Version)</h2>
                <div id="appliedImprovements"></div>
            </div>

            <div class="card full-width">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <h2 style="margin: 0;">Improvement History by Version</h2>
                    <a href="MODULE_ANALYSIS_DASHBOARD.html" target="_blank" style="color: var(--accent-blue); text-decoration: none; font-size: 0.9rem;">
                        View Detailed Rubric Analysis →
                    </a>
                </div>
                <div id="suggestionsList"></div>
            </div>
        </div>
    </div>

    <script>
        const progressData = __PROGRESS_DATA__;
        const suggestionsData = __SUGGESTIONS_DATA__;
        const appliedData = __APPLIED_DATA__;
        const improvementHistory = __IMPROVEMENT_HISTORY__;
        const binaryMetrics = __BINARY_METRICS__;

        let passRateChart = null;
        let modelCompareChart = null;

        // Map base module to folder name
        const BASE_MODULE_FOLDER_MAP = {
            'm01': 'M01_ExtractOwnBrandEntities',
            'm01a': 'M01A_ExtractOwnBrandVariations_PathB',
            'm01b': 'M01B_ExtractBrandRelatedTerms_PathB',
            'm02': 'M02_ClassifyOwnBrandKeywords',
            'm02b': 'M02B_ClassifyOwnBrandKeywords_PathB',
            'm04': 'M04_ClassifyCompetitorBrandKeywords',
            'm04b': 'M04B_ClassifyCompetitorBrandKeywords_PathB',
            'm05': 'M05_ClassifyNonBrandedKeywords',
            'm05b': 'M05B_ClassifyNonBrandedKeywords_PathB',
            'm06': 'M06_GenerateProductTypeTaxonomy',
            'm07': 'M07_ExtractProductAttributes',
            'm08': 'M08_AssignAttributeRanks',
            'm09': 'M09_IdentifyPrimaryIntendedUse',
            'm10': 'M10_ValidatePrimaryIntendedUse',
            'm11': 'M11_IdentifyHardConstraints',
            'm12': 'M12_HardConstraintViolationCheck',
            'm13': 'M13_ProductTypeCheck',
            'm14': 'M14_PrimaryUseCheckSameType',
            'm15': 'M15_SubstituteCheck',
            'm16': 'M16_ComplementaryCheck',
        };

        // Extract base module from full module name (e.g., "m01_v3_gemini" -> "m01", "m01a_v2" -> "m01a")
        function getBaseModule(module) {
            const m = module.toLowerCase();
            // Match pattern: m01, m01a, m01b, m02, m02b, etc. (base module with optional letter suffix)
            const match = m.match(/^(m\d+[ab]?)/);
            return match ? match[1] : m;
        }

        // Get folder for a module (uses base module lookup)
        function getModuleFolder(module) {
            const baseModule = getBaseModule(module);
            return BASE_MODULE_FOLDER_MAP[baseModule] || module.toUpperCase();
        }

        // Get short name for folder (e.g., "M01_ExtractOwnBrandEntities" -> "M01")
        function getFolderShortName(folder) {
            const match = folder.match(/^(M\d+[A-B]?)_/);
            return match ? match[1] : folder;
        }

        // Get all unique folders with natural sort (M01, M01A, M01B, M02, M02B, ...)
        const folders = [...new Set(progressData.map(r => getModuleFolder(r.module)))].sort((a, b) => {
            // Extract module number and optional letter suffix
            const matchA = a.match(/^M(\d+)([A-B])?_/);
            const matchB = b.match(/^M(\d+)([A-B])?_/);
            if (!matchA || !matchB) return a.localeCompare(b);

            const numA = parseInt(matchA[1]);
            const numB = parseInt(matchB[1]);
            if (numA !== numB) return numA - numB;

            // Same number - base module (no letter) comes first
            const letterA = matchA[2] || '';
            const letterB = matchB[2] || '';
            return letterA.localeCompare(letterB);
        });

        // Map folder -> list of modules
        const folderModules = {};
        progressData.forEach(r => {
            const folder = getModuleFolder(r.module);
            if (!folderModules[folder]) folderModules[folder] = new Set();
            folderModules[folder].add(r.module);
        });

        function initModuleSelector() {
            const container = document.getElementById('moduleSelector');
            folders.forEach((folder, idx) => {
                const btn = document.createElement('button');
                const moduleCount = folderModules[folder].size;
                const shortName = getFolderShortName(folder);
                btn.className = 'module-btn' + (idx === 0 ? ' active' : '');
                btn.textContent = shortName + (moduleCount > 1 ? ` (${moduleCount})` : '');
                btn.title = folder; // Full name on hover
                btn.dataset.folder = folder;
                btn.onclick = () => selectFolder(folder);
                container.appendChild(btn);
            });
        }

        function selectFolder(folder) {
            document.querySelectorAll('.module-btn').forEach(btn => {
                btn.classList.toggle('active', btn.dataset.folder === folder);
            });

            // Get all runs from modules in this folder
            const moduleRuns = progressData.filter(r => getModuleFolder(r.module) === folder);
            // Sort: _v1 (baseline) first, then _v2, then base module (latest) last
            moduleRuns.sort((a, b) => {
                // Extract version from module name suffix (_v1 -> 1, _v2 -> 2, no suffix -> 999 = latest)
                const getModuleVersion = (mod) => {
                    const match = mod.match(/_v(\d+)$/i);
                    return match ? parseInt(match[1]) : 999; // no suffix = latest
                };
                const verA = getModuleVersion(a.module);
                const verB = getModuleVersion(b.module);
                if (verA !== verB) return verA - verB;
                // Same version - sort by module name
                return a.module.localeCompare(b.module);
            });

            updateStats(moduleRuns);
            updatePassRateChart(moduleRuns);
            updateModelCompareChart(moduleRuns);
            updateProgressTable(moduleRuns);
            updateBinaryMetrics(folder);
            updateAppliedImprovements(folder, moduleRuns);
            updateSuggestions(folder, moduleRuns);
        }

        function updateStats(runs) {
            if (runs.length === 0) return;
            const latest = runs[runs.length - 1];
            const first = runs[0];
            const improvement = latest.pass_rate - first.pass_rate;
            const improvementClass = improvement > 0 ? 'green' : improvement < 0 ? 'red' : 'yellow';

            document.getElementById('statsGrid').innerHTML = `
                <div class="stat-card">
                    <div class="stat-value blue">${latest.pass_rate.toFixed(1)}%</div>
                    <div class="stat-label">Current Pass Rate</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value ${improvementClass}">${improvement >= 0 ? '+' : ''}${improvement.toFixed(1)}%</div>
                    <div class="stat-label">Improvement</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value green">${latest.summary?.pass || 0}</div>
                    <div class="stat-label">Passing Tests</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value red">${latest.summary?.fail || 0}</div>
                    <div class="stat-label">Failing Tests</div>
                </div>
            `;
        }

        function updatePassRateChart(runs) {
            const ctx = document.getElementById('passRateChart').getContext('2d');
            // Sort by prompt_version: v1 first (left), v2, v3 last (right) for progression
            const getPromptVersion = (run) => {
                const match = run.prompt_version?.match(/v(\d+)/i);
                return match ? parseInt(match[1]) : 0;
            };
            const sortedRuns = [...runs].sort((a, b) => {
                const verA = getPromptVersion(a);
                const verB = getPromptVersion(b);
                if (verA !== verB) return verA - verB; // v1 < v2 < v3 (ascending for chart)
                return (a.model || '').localeCompare(b.model || '');
            });
            // Include module name in label for clarity, show full model name
            const labels = sortedRuns.map(r => `${r.prompt_version} (${r.model})`);
            const passRates = sortedRuns.map(r => r.pass_rate);
            const matchRates = sortedRuns.map(r => r.match_rate || 0);

            if (passRateChart) passRateChart.destroy();

            passRateChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        { label: 'Pass Rate %', data: passRates, borderColor: '#3b82f6', backgroundColor: 'rgba(59, 130, 246, 0.1)', fill: true, tension: 0.3, pointRadius: 6 },
                        { label: 'Match Rate %', data: matchRates, borderColor: '#22c55e', backgroundColor: 'rgba(34, 197, 94, 0.1)', fill: true, tension: 0.3, pointRadius: 6 }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { labels: { color: '#94a3b8' } } },
                    scales: {
                        y: { beginAtZero: true, max: 100, grid: { color: '#334155' }, ticks: { color: '#94a3b8' } },
                        x: { grid: { color: '#334155' }, ticks: { color: '#94a3b8' } }
                    }
                }
            });
        }

        function updateModelCompareChart(runs) {
            const ctx = document.getElementById('modelCompareChart').getContext('2d');
            const modelGroups = {};
            runs.forEach(r => {
                if (!modelGroups[r.model]) modelGroups[r.model] = [];
                modelGroups[r.model].push(r);
            });

            const labels = Object.keys(modelGroups);
            const avgPassRates = labels.map(model => {
                const modelRuns = modelGroups[model];
                return modelRuns.reduce((sum, r) => sum + r.pass_rate, 0) / modelRuns.length;
            });

            if (modelCompareChart) modelCompareChart.destroy();

            modelCompareChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Avg Pass Rate %',
                        data: avgPassRates,
                        backgroundColor: labels.map(l => l.includes('gpt-5') ? '#a855f7' : l.includes('gpt-4o-mini') ? '#60a5fa' : '#22c55e'),
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { beginAtZero: true, max: 100, grid: { color: '#334155' }, ticks: { color: '#94a3b8' } },
                        x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
                    }
                }
            });
        }

        function updateProgressTable(runs) {
            const tbody = document.querySelector('#progressTable tbody');
            tbody.innerHTML = '';
            // Sort by prompt_version field: latest (v3) at TOP, baseline (v1) at BOTTOM
            const sortedRuns = [...runs].sort((a, b) => {
                const getPromptVersion = (run) => {
                    const match = run.prompt_version?.match(/v(\d+)/i);
                    return match ? parseInt(match[1]) : 0;
                };
                const verA = getPromptVersion(a);
                const verB = getPromptVersion(b);
                if (verA !== verB) return verB - verA; // Higher version first (v3 > v2 > v1)
                // Same prompt version - sort by model name
                return (a.model || '').localeCompare(b.model || '');
            });

            sortedRuns.forEach((run, idx) => {
                let trend = '';
                if (idx === sortedRuns.length - 1) {
                    // Last row (v1) is baseline
                    trend = `<span class="trend-indicator trend-same">baseline</span>`;
                } else {
                    // Compare to NEXT row (older version) to show progress
                    const prev = sortedRuns[idx + 1];
                    const diff = run.pass_rate - prev.pass_rate;
                    if (diff > 0) trend = `<span class="trend-indicator trend-up">▲ +${diff.toFixed(1)}%</span>`;
                    else if (diff < 0) trend = `<span class="trend-indicator trend-down">▼ ${diff.toFixed(1)}%</span>`;
                    else trend = `<span class="trend-indicator trend-same">— 0%</span>`;
                }

                const passRateColor = run.pass_rate >= 80 ? '#22c55e' : run.pass_rate >= 60 ? '#eab308' : run.pass_rate >= 40 ? '#f97316' : '#ef4444';

                const row = document.createElement('tr');

                // Format dataset name (truncate if needed)
                const datasetName = run.dataset_name || 'N/A';
                const shortDataset = datasetName.length > 25 ? datasetName.slice(0, 22) + '...' : datasetName;

                // Braintrust link - use experiment name URL-encoded with correct org/project
                const btLink = run.braintrust_name
                    ? `<a href="https://www.braintrust.dev/app/KCC/p/Keyword-Classification-Pipeline-V1.1/experiments/${encodeURIComponent(run.braintrust_name)}" target="_blank" style="color: var(--accent-blue); font-size: 0.75rem; text-decoration: none;">View ↗</a>`
                    : '<span style="color: var(--text-secondary); font-size: 0.75rem;">—</span>';

                row.innerHTML = `
                    <td><span class="module-badge" style="background: #334155; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">${run.module.toUpperCase()}</span></td>
                    <td><span class="version-badge ${run.prompt_version}">${run.prompt_version}</span></td>
                    <td><span class="model-badge">${run.model}</span></td>
                    <td title="${datasetName}&#10;ID: ${run.dataset_id || 'N/A'}" style="font-size: 0.75rem; color: var(--text-secondary); max-width: 150px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${shortDataset}</td>
                    <td>
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <span style="width: 50px; font-weight: 600; color: ${passRateColor}">${run.pass_rate.toFixed(1)}%</span>
                            <div class="rate-bar" style="flex: 1; max-width: 80px;">
                                <div class="rate-bar-fill" style="width: ${run.pass_rate}%; background: ${passRateColor}"></div>
                            </div>
                        </div>
                    </td>
                    <td>${(run.match_rate || 0).toFixed(1)}%</td>
                    <td><span style="color: #22c55e">${run.summary?.pass || 0}</span> / <span style="color: #ef4444">${run.summary?.fail || 0}</span></td>
                    <td>${trend}</td>
                    <td>${btLink}</td>
                `;
                tbody.appendChild(row);
            });
        }

        function updateBinaryMetrics(folder) {
            const card = document.getElementById('binaryMetricsCard');
            const container = document.getElementById('binaryMetricsTable');

            // Get base module from folder (M02_ClassifyOwnBrandKeywords -> m02)
            const baseModule = folder.split('_')[0].toLowerCase();

            // Find all metrics entries for this module (new structure: {m02_v1_gpt4o: {..., module: 'm02'}, ...})
            const moduleMetrics = Object.entries(binaryMetrics)
                .filter(([key, val]) => val.module === baseModule)
                .sort((a, b) => {
                    // Sort by version (v1, v2, v3), then by model
                    const verA = parseInt(a[1].prompt_version?.replace('v', '') || '1');
                    const verB = parseInt(b[1].prompt_version?.replace('v', '') || '1');
                    if (verA !== verB) return verA - verB;
                    return (a[1].model || '').localeCompare(b[1].model || '');
                });

            if (moduleMetrics.length === 0) {
                card.style.display = 'none';
                return;
            }

            card.style.display = 'block';
            const labels = moduleMetrics[0][1].labels || {};

            // Color helpers
            const getColor = (val, t1 = 70, t2 = 50) => val >= t1 ? '#22c55e' : val >= t2 ? '#eab308' : '#ef4444';
            const getMccColor = (val) => val >= 0.5 ? '#22c55e' : val >= 0.2 ? '#eab308' : '#ef4444';

            // Build rows for each experiment
            const rows = moduleMetrics.map(([key, m]) => `
                <tr>
                    <td style="font-weight: 600;">${m.prompt_version || 'v1'}</td>
                    <td style="font-size: 0.8rem;">${m.model || '-'}</td>
                    <td style="font-size: 0.8rem; color: #64748b;">${m.dataset || '-'}</td>
                    <td style="text-align: right;">${m.total.toLocaleString()}</td>
                    <td style="text-align: right; color: #22c55e;">${m.tp}</td>
                    <td style="text-align: right; color: #3b82f6;">${m.tn}</td>
                    <td style="text-align: right; color: #ef4444;">${m.fp}</td>
                    <td style="text-align: right; color: #eab308;">${m.fn}</td>
                    <td style="text-align: right; font-weight: 600; color: ${getColor(m.accuracy)};">${m.accuracy}%</td>
                    <td style="text-align: right; font-weight: 600; color: ${getColor(m.precision)};">${m.precision}%</td>
                    <td style="text-align: right; font-weight: 600; color: ${getColor(m.recall)};">${m.recall}%</td>
                    <td style="text-align: right; font-weight: 600; color: ${getColor(m.f1)};">${m.f1}%</td>
                    <td style="text-align: right; font-weight: 600; color: ${getMccColor(m.mcc)};">${m.mcc.toFixed(3)}</td>
                </tr>
            `).join('');

            container.innerHTML = `
                <table class="progress-table" style="font-size: 0.85rem;">
                    <thead>
                        <tr>
                            <th>Version</th>
                            <th>Model</th>
                            <th>Dataset</th>
                            <th style="text-align: right;">N</th>
                            <th style="text-align: right; color: #22c55e;" title="${labels.tp || 'True Positive'}">TP</th>
                            <th style="text-align: right; color: #3b82f6;" title="${labels.tn || 'True Negative'}">TN</th>
                            <th style="text-align: right; color: #ef4444;" title="${labels.fp || 'False Positive'}">FP</th>
                            <th style="text-align: right; color: #eab308;" title="${labels.fn || 'False Negative'}">FN</th>
                            <th style="text-align: right;">Acc</th>
                            <th style="text-align: right;">Prec</th>
                            <th style="text-align: right;">Rec</th>
                            <th style="text-align: right;">F1</th>
                            <th style="text-align: right;">MCC</th>
                        </tr>
                    </thead>
                    <tbody>${rows}</tbody>
                </table>
                <div style="display: flex; justify-content: space-between; margin-top: 10px; font-size: 0.75rem; color: #64748b;">
                    <span>TP=${labels.tp || ''} | TN=${labels.tn || ''} | FP=${labels.fp || ''} | FN=${labels.fn || ''}</span>
                    ${moduleMetrics[0][1].note ? '<span style="color: #eab308;"><em>' + moduleMetrics[0][1].note + '</em></span>' : ''}
                </div>
            `;
        }

        function updateAppliedImprovements(family, moduleRuns) {
            const container = document.getElementById('appliedImprovements');

            // Get all unique modules in this family from the runs
            const modulesInFamily = [...new Set(moduleRuns.map(r => r.module.toUpperCase()))];

            // Collect version info from all modules in the family
            let allVersionCards = [];

            modulesInFamily.forEach(moduleKey => {
                const versions = appliedData.prompt_versions?.[moduleKey] || {};

                Object.keys(versions).forEach(ver => {
                    const v = versions[ver];
                    const applied = v.applied_suggestions || [];
                    const hasImprovements = applied.length > 0;

                    allVersionCards.push({
                        module: moduleKey,
                        version: ver,
                        data: v,
                        applied: applied,
                        hasImprovements: hasImprovements
                    });
                });
            });

            if (allVersionCards.length === 0) {
                container.innerHTML = '<p class="no-improvements">No version history available for this module family.</p>';
                return;
            }

            // Sort by version descending
            allVersionCards.sort((a, b) => b.version.localeCompare(a.version));

            container.innerHTML = allVersionCards.map(card => {
                const v = card.data;
                const applied = card.applied;
                const hasImprovements = card.hasImprovements;

                return `
                    <div class="version-card ${hasImprovements ? 'has-improvements' : ''}">
                        <div class="version-header">
                            <span class="version-title">
                                <span class="module-badge" style="background: #334155; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; margin-right: 6px;">${card.module}</span>
                                <span class="version-badge ${card.version}">${card.version}</span>
                                ${v.file || ''}
                            </span>
                            <span class="version-meta">
                                ${v.model || ''} | ${v.pass_rate ? v.pass_rate + '%' : ''} | ${v.date || ''}
                            </span>
                        </div>
                        <p style="color: var(--text-secondary); font-size: 0.85rem; margin-bottom: 10px;">${v.description || ''}</p>
                        ${hasImprovements ? `
                            <div style="margin-top: 10px;">
                                <strong style="color: var(--accent-green); font-size: 0.85rem;">✓ Applied Improvements:</strong>
                                ${applied.map(imp => `
                                    <div class="improvement-item">
                                        <span class="rubric">${imp.rubric}</span>
                                        <span class="suggestion-status applied">${imp.status}</span>
                                        <div class="change">${imp.suggestion_summary}</div>
                                    </div>
                                `).join('')}
                            </div>
                        ` : '<p class="no-improvements">No improvements applied in this version</p>'}
                    </div>
                `;
            }).join('');
        }

        function updateSuggestions(family, moduleRuns) {
            const container = document.getElementById('suggestionsList');

            // Get module key from folder name (e.g., M01_ExtractOwnBrandEntities -> M01)
            const moduleKey = family.split('_')[0];
            const moduleHistory = improvementHistory.modules?.[moduleKey];

            if (!moduleHistory || !moduleHistory.versions) {
                container.innerHTML = '<li class="no-improvements">No improvement history available for this module.</li>';
                return;
            }

            // Build version-based suggestions display
            const versions = Object.entries(moduleHistory.versions);
            let html = '';

            versions.forEach(([versionId, versionData]) => {
                const suggestions = versionData.suggestions || [];
                const appliedFrom = versionData.applied_from_v1 || versionData.applied_from_v2 || versionData.applied_from_v3 || [];
                const evaluation = versionData.evaluation || {};
                const improvement = versionData.improvement_vs_previous || '';

                const pendingSuggestions = suggestions.filter(s => s.status === 'pending');
                const appliedSuggestions = suggestions.filter(s => s.status === 'applied');

                html += `
                    <div style="margin-bottom: 20px; padding: 15px; background: #1e293b; border-radius: 8px; border-left: 3px solid ${pendingSuggestions.length > 0 ? '#f59e0b' : '#22c55e'};">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <div>
                                <span class="version-badge ${versionId}" style="font-size: 0.9rem;">${versionId.toUpperCase()}</span>
                                <span style="margin-left: 10px; color: #94a3b8;">${evaluation.model || ''}</span>
                                <span style="margin-left: 10px; font-weight: bold; color: ${evaluation.pass_rate >= 70 ? '#22c55e' : evaluation.pass_rate >= 50 ? '#f59e0b' : '#ef4444'};">
                                    ${evaluation.pass_rate || 0}%
                                </span>
                                ${improvement ? `<span style="margin-left: 10px; color: ${improvement.startsWith('+') ? '#22c55e' : '#ef4444'};">${improvement}</span>` : ''}
                            </div>
                            <span style="font-size: 0.75rem; color: #64748b;">${evaluation.date || ''}</span>
                        </div>

                        ${appliedFrom.length > 0 ? `
                            <div style="margin-bottom: 10px; padding: 8px; background: rgba(34, 197, 94, 0.1); border-radius: 4px;">
                                <span style="color: #22c55e; font-size: 0.8rem; font-weight: 600;">✓ Applied in this version:</span>
                                <ul style="margin: 5px 0 0 20px; color: #94a3b8; font-size: 0.85rem;">
                                    ${appliedFrom.map(a => `<li>${a}</li>`).join('')}
                                </ul>
                            </div>
                        ` : ''}

                        ${suggestions.length > 0 ? `
                            <div style="margin-top: 10px;">
                                <span style="color: #f59e0b; font-size: 0.8rem; font-weight: 600;">
                                    ${pendingSuggestions.length > 0 ? '⚠ Suggestions for next version:' : '✓ All suggestions applied'}
                                </span>
                                <ul style="margin: 8px 0 0 0; padding: 0; list-style: none;">
                                    ${suggestions.map(s => `
                                        <li style="padding: 8px; margin-top: 6px; background: #0f172a; border-radius: 4px; border-left: 2px solid ${s.status === 'pending' ? '#f59e0b' : '#22c55e'};">
                                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                                <strong style="color: #e2e8f0;">${s.rubric}</strong>
                                                <div>
                                                    <span style="font-size: 0.7rem; padding: 2px 6px; border-radius: 3px; background: ${s.priority === 'high' ? '#dc2626' : s.priority === 'medium' ? '#d97706' : '#059669'}; color: white;">
                                                        ${s.priority || 'medium'}
                                                    </span>
                                                    <span style="margin-left: 6px; font-size: 0.7rem; padding: 2px 6px; border-radius: 3px; background: ${s.status === 'pending' ? '#d97706' : '#059669'}; color: white;">
                                                        ${s.status}${s.applied_in ? ' → ' + s.applied_in : ''}
                                                    </span>
                                                </div>
                                            </div>
                                            <p style="margin: 6px 0 0 0; color: #94a3b8; font-size: 0.85rem;">${s.issue}</p>
                                            <p style="margin: 4px 0 0 0; color: #60a5fa; font-size: 0.85rem;">→ ${s.suggestion}</p>
                                            ${s.result ? `<p style="margin: 4px 0 0 0; color: #22c55e; font-size: 0.8rem;">Result: ${s.result}</p>` : ''}
                                        </li>
                                    `).join('')}
                                </ul>
                            </div>
                        ` : '<p style="color: #64748b; font-size: 0.85rem; margin-top: 10px;">No suggestions recorded for this version.</p>'}
                    </div>
                `;
            });

            container.innerHTML = html || '<li class="no-improvements">No improvement history available.</li>';
        }

        initModuleSelector();
        if (folders.length > 0) selectFolder(folders[0]);
    </script>
</body>
</html>'''

    # Replace placeholders with actual data
    html = template_content.replace(
        '__PROGRESS_DATA__',
        json.dumps(progress_data, indent=2)
    ).replace(
        '__SUGGESTIONS_DATA__',
        json.dumps(suggestions_data, indent=2)
    ).replace(
        '__APPLIED_DATA__',
        json.dumps(applied_data, indent=2)
    ).replace(
        '__IMPROVEMENT_HISTORY__',
        json.dumps(improvement_history, indent=2)
    ).replace(
        '__BINARY_METRICS__',
        json.dumps(binary_metrics, indent=2)
    )

    # Write output
    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        f.write(html)

    print(f"\nDashboard generated: {OUTPUT_FILE}")
    return str(OUTPUT_FILE)


if __name__ == "__main__":
    import argparse
    import subprocess

    parser = argparse.ArgumentParser(description="Generate Progress Dashboard")
    parser.add_argument("--no-open", action="store_true", help="Don't open in browser")
    args = parser.parse_args()

    output_path = generate_dashboard()

    if not args.no_open:
        subprocess.run(["xdg-open", output_path], capture_output=True)
