#!/usr/bin/env python3
"""Fix module pages to filter out experiment results without pass_rate."""

import re
from pathlib import Path

MODULES_DIR = Path(__file__).parent / "modules"

def fix_filter(html_content: str) -> str:
    """Add pass_rate filter to progressData filtering."""

    # Find the pattern and add filter for pass_rate
    old_pattern = r"(const rawEvaluations = progressData\s*\n\s*\.filter\(d => \{[^}]+\}\))"

    # Check if already has pass_rate filter
    if "d.pass_rate !== undefined" in html_content:
        return html_content

    # Add filter for pass_rate
    new_code = r"""\1
            .filter(d => d.pass_rate !== undefined)  // Only include judge results"""

    return re.sub(old_pattern, new_code, html_content)


def main():
    html_files = sorted(MODULES_DIR.glob("m*.html"))

    for html_file in html_files:
        if html_file.name == "index.html":
            continue

        print(f"Processing {html_file.name}...")

        content = html_file.read_text()

        if "d.pass_rate !== undefined" in content:
            print(f"  Already fixed, skipping")
            continue

        new_content = fix_filter(content)

        if new_content != content:
            html_file.write_text(new_content)
            print(f"  Added pass_rate filter")
        else:
            print(f"  No changes needed")


if __name__ == "__main__":
    main()
