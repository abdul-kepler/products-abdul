#!/usr/bin/env python3
"""Fix widget order in module HTML files.

Correct order:
1. Stats Grid
2. Charts (Pass Rate by Prompt Version + Model Comparison)
3. Evaluation History (Version History Table)
4. Binary Classification Metrics
5. Known Issues Section
6. Error Details Modal
7. Model Cost Matrix
8. ... rest
"""

import re
from pathlib import Path

MODULES_DIR = Path(__file__).parent / "modules"

def fix_widget_order(html_content: str) -> str:
    """Reorder widgets in HTML content."""

    # Extract sections using regex
    # Binary Metrics Section
    binary_match = re.search(
        r'(<!-- Binary Classification Metrics.*?</div>\s*</div>\s*</div>)',
        html_content, re.DOTALL
    )

    # Known Issues Section
    known_issues_match = re.search(
        r'(<!-- Known Issues Section.*?</div>\s*</div>\s*</div>)',
        html_content, re.DOTALL
    )

    # Error Details Modal
    modal_match = re.search(
        r'(<!-- Error Details Modal.*?</div>\s*</div>)',
        html_content, re.DOTALL
    )

    # Version History Table (Evaluation History)
    eval_history_match = re.search(
        r'(<!-- Version History Table -->.*?</table>\s*</div>)',
        html_content, re.DOTALL
    )

    if not all([binary_match, known_issues_match, eval_history_match]):
        print("  Some sections not found, skipping")
        return html_content

    binary_section = binary_match.group(1)
    known_issues_section = known_issues_match.group(1)
    modal_section = modal_match.group(1) if modal_match else ""
    eval_history_section = eval_history_match.group(1)

    # Remove old sections from content
    new_content = html_content
    new_content = new_content.replace(binary_section, "<!-- PLACEHOLDER_BINARY -->")
    new_content = new_content.replace(known_issues_section, "<!-- PLACEHOLDER_KNOWN_ISSUES -->")
    if modal_section:
        new_content = new_content.replace(modal_section, "<!-- PLACEHOLDER_MODAL -->")
    new_content = new_content.replace(eval_history_section, "<!-- PLACEHOLDER_EVAL_HISTORY -->")

    # Find the position after Charts (dashboard-grid closing div)
    # Insert in correct order: Eval History, Binary Metrics, Known Issues, Modal

    # Remove all placeholders first
    new_content = new_content.replace("<!-- PLACEHOLDER_BINARY -->", "")
    new_content = new_content.replace("<!-- PLACEHOLDER_KNOWN_ISSUES -->", "")
    new_content = new_content.replace("<!-- PLACEHOLDER_MODAL -->", "")
    new_content = new_content.replace("<!-- PLACEHOLDER_EVAL_HISTORY -->", "")

    # Find insertion point (after </div> that closes dashboard-grid for charts)
    # Pattern: closing </div> after Model Comparison chart
    insert_pattern = r'(</div>\s*</div>\s*</div>\s*)(<!-- Model Cost Matrix -->)'

    # Build new section order
    new_sections = f"""
        {eval_history_section}

        {binary_section}

        {known_issues_section}

        {modal_section}

        """

    # Replace - insert sections before Model Cost Matrix
    new_content = re.sub(
        insert_pattern,
        r'\1' + new_sections + r'\2',
        new_content
    )

    return new_content


def main():
    html_files = sorted(MODULES_DIR.glob("m*.html"))

    for html_file in html_files:
        print(f"Processing {html_file.name}...")

        content = html_file.read_text()

        # Check if already in correct order (Evaluation History before Binary Metrics)
        eval_pos = content.find("<!-- Version History Table -->")
        binary_pos = content.find("<!-- Binary Classification Metrics")

        if eval_pos > 0 and binary_pos > 0 and eval_pos < binary_pos:
            print(f"  Already in correct order, skipping")
            continue

        new_content = fix_widget_order(content)

        if new_content != content:
            html_file.write_text(new_content)
            print(f"  Fixed widget order")
        else:
            print(f"  No changes needed")


if __name__ == "__main__":
    main()
