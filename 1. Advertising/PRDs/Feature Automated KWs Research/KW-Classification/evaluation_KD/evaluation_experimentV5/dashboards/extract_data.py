#!/usr/bin/env python3
"""
Extract data from PROGRESS_DASHBOARD.html to modules_data.js
"""
import re
from pathlib import Path

def extract_data():
    dashboard_path = Path(__file__).parent / 'PROGRESS_DASHBOARD.html'
    output_path = Path(__file__).parent / 'modules_data.js'

    content = dashboard_path.read_text()

    # Find the script section
    script_match = re.search(r'<script>(.*?)</script>', content, re.DOTALL)
    if not script_match:
        print("ERROR: Could not find script section")
        return

    script_content = script_match.group(1)

    # Extract each data section
    data_sections = []

    # progressData
    progress_match = re.search(r'(const progressData = \[.*?\];)', script_content, re.DOTALL)
    if progress_match:
        data_sections.append(progress_match.group(1))
        print(f"Extracted progressData: {len(progress_match.group(1))} chars")

    # suggestionsData
    suggestions_match = re.search(r'(const suggestionsData = \[.*?\];)', script_content, re.DOTALL)
    if suggestions_match:
        data_sections.append(suggestions_match.group(1))
        print(f"Extracted suggestionsData: {len(suggestions_match.group(1))} chars")

    # appliedData
    applied_match = re.search(r'(const appliedData = \{.*?\n\};)', script_content, re.DOTALL)
    if applied_match:
        data_sections.append(applied_match.group(1))
        print(f"Extracted appliedData: {len(applied_match.group(1))} chars")

    # improvementHistory
    history_match = re.search(r'(const improvementHistory = \{.*?\n\};)', script_content, re.DOTALL)
    if history_match:
        data_sections.append(history_match.group(1))
        print(f"Extracted improvementHistory: {len(history_match.group(1))} chars")

    # MODULE_FOLDER_MAP
    map_match = re.search(r'(const MODULE_FOLDER_MAP = \{.*?\};)', script_content, re.DOTALL)
    if map_match:
        data_sections.append(map_match.group(1))
        print(f"Extracted MODULE_FOLDER_MAP: {len(map_match.group(1))} chars")

    # Preserve existing binaryMetrics if present in current modules_data.js
    binary_metrics_section = ''
    if output_path.exists():
        existing_content = output_path.read_text()
        binary_match = re.search(r'(// Binary classification metrics.*?const binaryMetrics = \{.*?\n\};)',
                                 existing_content, re.DOTALL)
        if binary_match:
            binary_metrics_section = '\n' + binary_match.group(1)
            print(f"Preserved binaryMetrics: {len(binary_metrics_section)} chars")

    # Write to modules_data.js
    output_content = '''/**
 * Shared data for module dashboards
 * Auto-generated from PROGRESS_DASHBOARD.html
 *
 * Usage in HTML:
 *   <script src="modules_data.js"></script>
 *   <script>
 *     // Data available: progressData, suggestionsData, appliedData, improvementHistory, MODULE_FOLDER_MAP, binaryMetrics
 *     console.log(progressData.filter(d => d.module.startsWith('m01')));
 *   </script>
 */

'''
    output_content += '\n\n'.join(data_sections)

    # Append preserved binaryMetrics
    if binary_metrics_section:
        output_content += binary_metrics_section

    output_path.write_text(output_content)
    print(f"\nWritten to {output_path}")
    print(f"Total size: {len(output_content)} chars ({len(output_content)//1024} KB)")

if __name__ == '__main__':
    extract_data()
