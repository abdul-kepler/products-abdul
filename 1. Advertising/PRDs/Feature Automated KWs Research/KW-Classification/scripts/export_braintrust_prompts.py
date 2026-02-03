#!/usr/bin/env python3
"""
Export all prompts from Braintrust and create local mapping.

Usage:
    python scripts/export_braintrust_prompts.py

This creates: evaluation_KD/evaluation_experimentV5/prompt_mappings.yaml
"""

import os
import sys
import yaml
from pathlib import Path
from datetime import datetime

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))
from config import PROJECT_ID, PROJECT_NAME, load_api_key, PROMPTS_DIR

try:
    import requests
except ImportError:
    print("Error: requests package not installed. Run: pip install requests")
    sys.exit(1)


def fetch_prompts_via_api(api_key: str, project_id: str) -> list:
    """Fetch all prompts from Braintrust via REST API."""
    url = f"https://api.braintrust.dev/v1/project/{project_id}/prompt"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching prompts: {response.status_code}")
        print(response.text)
        return []

    return response.json().get("objects", [])


def match_to_local_file(prompt_name: str, prompt_slug: str) -> str:
    """Try to match prompt to local file."""
    # Try various patterns
    patterns = [
        f"{prompt_slug.replace('-', '_')}.md",
        f"{prompt_name.lower().replace(' ', '_')}.md",
    ]

    # Also try module-based patterns
    if prompt_name.startswith("M") and "_" in prompt_name:
        parts = prompt_name.split("_", 1)
        module = parts[0].lower()
        name = parts[1].lower().replace(" ", "_")
        patterns.append(f"{module}_{name}.md")

    for pattern in patterns:
        path = PROMPTS_DIR / pattern
        if path.exists():
            return str(path.relative_to(Path(__file__).parent.parent))

    return ""


def main():
    # Load API key
    try:
        api_key = load_api_key()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    print(f"Fetching prompts from Braintrust...")
    print(f"Project: {PROJECT_NAME}")
    print(f"Project ID: {PROJECT_ID}")

    prompts = fetch_prompts_via_api(api_key, PROJECT_ID)

    if not prompts:
        print("No prompts found or error fetching prompts")
        return

    print(f"\nFound {len(prompts)} prompts")
    print("=" * 100)
    print(f"{'Name':<45} {'ID':<40} {'Slug':<30}")
    print("-" * 100)

    mappings = {
        "version": "1.0",
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "project_id": PROJECT_ID,
        "project_name": PROJECT_NAME,
        "prompts": []
    }

    for p in prompts:
        name = p.get("name", "")
        prompt_id = p.get("id", "")
        slug = p.get("slug", "")

        print(f"{name:<45} {prompt_id:<40} {slug:<30}")

        local_file = match_to_local_file(name, slug)

        mappings["prompts"].append({
            "braintrust_id": prompt_id,
            "braintrust_name": name,
            "braintrust_slug": slug,
            "local_file": local_file,
            "last_synced": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

    # Save mappings
    output_path = Path(__file__).parent.parent / "evaluation_KD" / "evaluation_experimentV5" / "prompt_mappings.yaml"

    with open(output_path, "w") as f:
        yaml.dump(mappings, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print(f"\n{'=' * 100}")
    print(f"Saved prompt mappings to: {output_path}")
    print(f"Total prompts: {len(mappings['prompts'])}")


if __name__ == "__main__":
    main()
