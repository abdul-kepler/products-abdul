#!/usr/bin/env python3
"""
Sync module HTML files from evaluation_experimentV5 to tracking_dashboard.
Apply necessary modifications:
1. Remove Module Info block
2. Add known_issues_data.js script
3. Add Known Issues section and modal
4. Add Applied Improvements and Improvement History sections
5. Add Match Rate curve to chart
6. Add pass_rate filter for evaluations
"""

import re
from pathlib import Path

SOURCE_DIR = Path(__file__).parent.parent.parent / "evaluation_KD" / "evaluation_experimentV5" / "dashboards" / "modules"
TARGET_DIR = Path(__file__).parent.parent / "dashboards" / "modules"

def process_module(content: str) -> str:
    """Apply all modifications to module HTML."""

    # 1. Add known_issues_data.js after modules_data.js
    content = content.replace(
        '<script src="../modules_data.js"></script>',
        '<script src="../modules_data.js"></script>\n    <script src="../known_issues_data.js"></script>'
    )

    # 2. Remove Module Info block (lines 45-67 in original)
    content = re.sub(
        r'\s*<!-- Module Info -->.*?</div>\s*</div>\s*(?=<!-- Stats Grid -->)',
        '\n\n        ',
        content,
        flags=re.DOTALL
    )

    # 3. Add pass_rate filter AND dataset truncation
    # Replace the entire evaluations mapping to add both features
    old_eval_map = r"""\.map\(d => \(\{
                version: d\.prompt_version \|\| 'v1',
                model: d\.model,
                dataset: d\.dataset_name \|\| d\.data_source,
                passRate: d\.pass_rate,
                matchRate: d\.match_rate \|\| 0,
                pass: d\.summary\?\.pass \|\| 0,
                fail: d\.summary\?\.fail \|\| 0,
                date: d\.timestamp \? d\.timestamp\.split\('T'\)\[0\] : '',
                btName: d\.braintrust_name \|\| '',
                btId: d\.braintrust_id \|\| ''
            \}\)\)
            \.sort\(\(a, b\) => b\.passRate - a\.passRate\);"""

    new_eval_map = """.filter(d => d.pass_rate !== undefined)  // Only include judge results
            .map(d => ({
                version: d.prompt_version || 'v1',
                model: d.model,
                dataset: (() => {
                    const ds = d.data_source || d.dataset_name || '-';
                    const name = ds.split('/').pop().replace('.csv', '');
                    return name.length > 30 ? name.slice(0, 27) + '...' : name;
                })(),
                datasetFull: d.data_source || d.dataset_name || '-',
                passRate: d.pass_rate,
                matchRate: d.match_rate || 0,
                pass: d.summary?.pass || 0,
                fail: d.summary?.fail || 0,
                date: d.timestamp ? d.timestamp.split('T')[0] : '',
                btName: d.braintrust_name || '',
                btId: d.braintrust_id || ''
            }))
            .sort((a, b) => {
                // First by version descending (v5 > v4 > v3...)
                const versionCompare = b.version.localeCompare(a.version);
                if (versionCompare !== 0) return versionCompare;
                // Then by date descending (newest first)
                return b.date.localeCompare(a.date);
            });"""

    content = re.sub(old_eval_map, new_eval_map, content)

    # 4. Add Match Rate dataset to chart
    old_chart_datasets = r"""datasets: \[\{
                        label: 'Pass Rate %',
                        data: chartData,
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba\(59, 130, 246, 0\.1\)',
                        fill: true,
                        tension: 0\.3,
                        pointRadius: 6
                    \}\]"""

    new_chart_datasets = """datasets: [{
                        label: 'Pass Rate %',
                        data: chartData,
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        fill: true,
                        tension: 0.3,
                        pointRadius: 6
                    }, {
                        label: 'Match Rate %',
                        data: evaluations.map(e => e.matchRate).reverse(),
                        borderColor: '#22c55e',
                        backgroundColor: 'rgba(34, 197, 94, 0.1)',
                        fill: false,
                        tension: 0.3,
                        pointRadius: 6,
                        borderDash: [5, 5]
                    }]"""

    content = re.sub(old_chart_datasets, new_chart_datasets, content)

    # 5. Add Known Issues section after Binary Metrics
    known_issues_html = """
        <!-- Known Issues Section (for modules with error analysis) -->
        <div id="knownIssuesSection" style="display: none;">
            <div class="card">
                <h2>Known Issues Analysis</h2>
                <p id="issuesSummary" style="color: var(--text-secondary); font-size: 0.85rem; margin-bottom: 15px;"></p>
                <div id="issueCategories"></div>
            </div>
        </div>

        <!-- Error Details Modal -->
        <div id="errorModal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 1000; overflow: auto;">
            <div style="background: var(--card-bg); margin: 5% auto; padding: 20px; border-radius: 12px; max-width: 900px; max-height: 80vh; overflow: auto;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <h3 id="modalTitle" style="margin: 0; color: var(--text-primary);"></h3>
                    <button onclick="closeModal()" style="background: none; border: none; color: var(--text-secondary); font-size: 1.5rem; cursor: pointer;">&times;</button>
                </div>
                <div id="modalContent"></div>
            </div>
        </div>
"""

    # Insert after binaryMetricsSection closing </div></div>
    content = re.sub(
        r'(<!-- Binary Classification Metrics.*?</div>\s*</div>)(\s*<!-- Model Cost Matrix -->)',
        r'\1' + known_issues_html + r'\2',
        content,
        flags=re.DOTALL
    )

    # 6. Add Applied Improvements and Improvement History sections before closing </div> of container
    improvements_html = """
        <!-- Applied Improvements (by Version) -->
        <div class="card">
            <h2>Applied Improvements (by Version)</h2>
            <div id="appliedImprovements"></div>
        </div>

        <!-- Improvement History by Version -->
        <div class="card">
            <h2>Improvement History by Version</h2>
            <div id="improvementHistory"></div>
        </div>
"""

    # Insert before <!-- Suggestions -->
    content = content.replace(
        '        <!-- Suggestions -->',
        improvements_html + '\n        <!-- Suggestions -->'
    )

    # 7. Fix binaryMetrics lookup to use versioned keys (e.g., m04_v1_gpt4omini)
    old_binary_lookup = r"""if \(typeof binaryMetrics !== 'undefined' && binaryMetrics\[moduleId\]\) \{
            const m = binaryMetrics\[moduleId\];"""

    new_binary_lookup = """// Find binary metrics key that starts with moduleId (e.g., m04_v1_gpt4omini)
        const binaryMetricsKeys = Object.keys(binaryMetrics || {}).filter(k => k.startsWith(moduleId + '_'));
        if (binaryMetricsKeys.length > 0) {
            const m = binaryMetrics[binaryMetricsKeys[0]];"""

    content = re.sub(old_binary_lookup, new_binary_lookup, content)

    # 8. Add Known Issues rendering JS code before closing </script>
    known_issues_js = """
        // Render Known Issues section (if data available)
        if (typeof knownIssuesData !== 'undefined' && knownIssuesData[moduleId]) {
            const issues = knownIssuesData[moduleId];
            document.getElementById('knownIssuesSection').style.display = 'block';
            document.getElementById('issuesSummary').innerHTML =
                `<strong>${issues.total_errors}</strong> errors analyzed for prompt <strong>${issues.prompt_version}</strong>. ` +
                `Categorized into ${issues.categories.length} root cause categories.`;

            const categoriesHtml = issues.categories.map(cat => `
                <div style="background: rgba(30, 41, 59, 0.5); border: 1px solid ${cat.color}40; border-radius: 8px; padding: 15px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <span style="font-size: 1.5rem;">${cat.icon}</span>
                            <div>
                                <strong style="color: ${cat.color};">${cat.name}</strong>
                                <span style="background: ${cat.color}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; margin-left: 8px;">${cat.count} errors</span>
                            </div>
                        </div>
                        <button onclick="showErrorDetails('${moduleId}', '${cat.id}')"
                                style="background: ${cat.color}20; border: 1px solid ${cat.color}; color: ${cat.color}; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 0.8rem;">
                            View Details
                        </button>
                    </div>
                    <p style="color: var(--text-secondary); font-size: 0.85rem; margin: 0;">${cat.description}</p>
                </div>
            `).join('');
            document.getElementById('issueCategories').innerHTML = categoriesHtml;
        }

        // Modal functions for Known Issues
        function showErrorDetails(modId, categoryId) {
            const issues = knownIssuesData[modId];
            const category = issues.categories.find(c => c.id === categoryId);
            if (!category) return;

            document.getElementById('modalTitle').innerHTML = `${category.icon} ${category.name} <span style="font-size: 0.8rem; color: var(--text-secondary);">(${category.count} errors)</span>`;

            const errorsHtml = `
                <p style="color: var(--text-secondary); margin-bottom: 15px;">${category.description}</p>
                <table style="width: 100%; border-collapse: collapse; font-size: 0.85rem;">
                    <thead>
                        <tr style="border-bottom: 1px solid var(--border-color);">
                            <th style="padding: 8px; text-align: left; color: #64748b;">Keyword</th>
                            <th style="padding: 8px; text-align: center; color: #64748b;">Expected</th>
                            <th style="padding: 8px; text-align: center; color: #64748b;">Output</th>
                            <th style="padding: 8px; text-align: left; color: #64748b;">Reasoning</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${category.errors.map(e => `
                            <tr style="border-bottom: 1px solid var(--border-color)20;">
                                <td style="padding: 8px; color: var(--text-primary);"><code>${e.keyword}</code></td>
                                <td style="padding: 8px; text-align: center;"><span style="background: #22c55e20; color: #22c55e; padding: 2px 6px; border-radius: 4px;">${e.expected}</span></td>
                                <td style="padding: 8px; text-align: center;"><span style="background: #ef444420; color: #ef4444; padding: 2px 6px; border-radius: 4px;">${e.output}</span></td>
                                <td style="padding: 8px; color: var(--text-secondary); font-size: 0.8rem;">${e.reasoning}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
                ${category.truncated ? `<p style="color: #eab308; font-size: 0.8rem; margin-top: 10px;">Showing ${category.errors.length} of ${category.total_in_category} errors</p>` : ''}
            `;
            document.getElementById('modalContent').innerHTML = errorsHtml;
            document.getElementById('errorModal').style.display = 'block';
        }

        function closeModal() {
            document.getElementById('errorModal').style.display = 'none';
        }

        // Close modal on outside click
        document.getElementById('errorModal').addEventListener('click', function(e) {
            if (e.target === this) closeModal();
        });

        // Render Applied Improvements (by Version)
        function renderAppliedImprovements() {
            const container = document.getElementById('appliedImprovements');
            const moduleKey = moduleId.toUpperCase();
            const versions = appliedData?.prompt_versions?.[moduleKey] || {};

            if (Object.keys(versions).length === 0) {
                container.innerHTML = '<p style="color: var(--text-secondary);">No applied improvements recorded for this module.</p>';
                return;
            }

            const versionCards = Object.entries(versions)
                .sort((a, b) => b[0].localeCompare(a[0]))
                .map(([version, data]) => {
                    const suggestions = data.applied_suggestions || [];
                    const suggestionsHtml = suggestions.map(s => `
                        <div style="background: rgba(34, 197, 94, 0.1); border-left: 3px solid #22c55e; padding: 8px 12px; margin-top: 8px; border-radius: 0 6px 6px 0;">
                            <div style="font-weight: 600; color: var(--text-primary); font-size: 0.85rem;">${s.rubric || 'General'}</div>
                            <div style="color: var(--text-secondary); font-size: 0.8rem; margin-top: 4px;">${s.suggestion_summary || s.change || s.description || ''}</div>
                        </div>
                    `).join('');

                    return `
                        <div style="background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 8px; padding: 16px; margin-bottom: 12px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                                <span class="version-badge ${version.toLowerCase()}" style="font-size: 0.9rem; padding: 4px 12px;">${version}</span>
                                <span style="color: var(--text-secondary); font-size: 0.8rem;">${data.date || ''}</span>
                            </div>
                            ${data.description ? `<p style="color: var(--text-secondary); font-size: 0.85rem; margin-bottom: 8px;">${data.description}</p>` : ''}
                            ${suggestionsHtml || '<p style="color: var(--text-secondary); font-size: 0.8rem;">No specific changes documented.</p>'}
                        </div>
                    `;
                }).join('');

            container.innerHTML = versionCards;
        }

        // Render Improvement History by Version
        function renderImprovementHistory() {
            const container = document.getElementById('improvementHistory');
            const moduleKey = moduleId.toUpperCase();
            const moduleHistory = improvementHistory?.modules?.[moduleKey];

            if (!moduleHistory || Object.keys(moduleHistory.versions || {}).length === 0) {
                container.innerHTML = '<p style="color: var(--text-secondary);">No improvement history available for this module.</p>';
                return;
            }

            const versionsHtml = Object.entries(moduleHistory.versions)
                .sort((a, b) => a[0].localeCompare(b[0]))
                .map(([version, data]) => {
                    const rubrics = data.rubric_breakdown || {};
                    const rubricsHtml = Object.entries(rubrics).map(([rubric, info]) => {
                        const passColor = info.pass_rate >= 70 ? '#22c55e' : info.pass_rate >= 50 ? '#eab308' : '#ef4444';
                        return `
                            <div style="display: flex; justify-content: space-between; align-items: center; padding: 6px 0; border-bottom: 1px solid var(--border-color);">
                                <span style="color: var(--text-primary); font-size: 0.85rem;">${rubric}</span>
                                <span style="color: ${passColor}; font-weight: 600;">${info.pass_rate}%</span>
                            </div>
                        `;
                    }).join('');

                    const suggestions = data.suggestions_applied || [];
                    const suggestionsHtml = suggestions.length > 0 ? `
                        <div style="margin-top: 12px;">
                            <div style="font-weight: 600; color: var(--text-secondary); font-size: 0.8rem; margin-bottom: 6px;">Applied Suggestions:</div>
                            ${suggestions.map(s => `<div style="color: #22c55e; font-size: 0.8rem;">+ ${s}</div>`).join('')}
                        </div>
                    ` : '';

                    return `
                        <div style="background: rgba(30, 41, 59, 0.5); border: 1px solid var(--border-color); border-radius: 8px; padding: 16px; margin-bottom: 12px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                                <span class="version-badge ${version.toLowerCase().replace('_', '-')}" style="font-size: 0.9rem; padding: 4px 12px;">${version}</span>
                                ${data.pass_rate ? `<span style="color: ${data.pass_rate >= 70 ? '#22c55e' : data.pass_rate >= 50 ? '#eab308' : '#ef4444'}; font-weight: 600;">${data.pass_rate}% Pass Rate</span>` : ''}
                            </div>
                            ${rubricsHtml}
                            ${suggestionsHtml}
                        </div>
                    `;
                }).join('');

            container.innerHTML = versionsHtml;
        }

        // Initialize new widgets
        if (typeof appliedData !== 'undefined') renderAppliedImprovements();
        if (typeof improvementHistory !== 'undefined') renderImprovementHistory();
"""

    # Insert before </script>
    content = content.replace(
        '\n    </script>\n</body>',
        known_issues_js + '\n    </script>\n</body>'
    )

    return content


def main():
    print("Syncing modules from evaluation_experimentV5...")

    if not SOURCE_DIR.exists():
        print(f"Source directory not found: {SOURCE_DIR}")
        return 1

    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    for source_file in sorted(SOURCE_DIR.glob("m*.html")):
        if source_file.name == "index.html":
            continue

        print(f"  Processing {source_file.name}...")

        content = source_file.read_text()
        modified_content = process_module(content)

        target_file = TARGET_DIR / source_file.name
        target_file.write_text(modified_content)
        print(f"    -> {target_file.name}")

    print("\nDone!")
    return 0


if __name__ == "__main__":
    exit(main())
