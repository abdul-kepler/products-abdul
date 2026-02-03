#!/usr/bin/env python3
"""
Extract optimized prompts from optimizer artifacts.

Converts GEPA, MIPRO, COPRO results into standalone prompt files.

Usage:
    python extract_optimized.py m02 --source mipro
    python extract_optimized.py m02 --source gepa --cleanup
    python extract_optimized.py --list  # Show available results
"""

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[1]
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
OUTPUT_DIR = PROJECT_ROOT / "prompts" / "optimized"
REGISTRY_FILE = OUTPUT_DIR / "registry.json"

# Import module config for input/output keys
import sys
sys.path.insert(0, str(SCRIPT_DIR))
from module_config import MODULE_CONFIGS


def load_registry() -> dict:
    """Load or create registry."""
    if REGISTRY_FILE.exists():
        return json.loads(REGISTRY_FILE.read_text())
    return {}


def save_registry(registry: dict):
    """Save registry."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REGISTRY_FILE.write_text(json.dumps(registry, indent=2, ensure_ascii=False))


def get_next_version(registry: dict, module: str, optimizer: str) -> int:
    """Get next version number for module+optimizer combo."""
    if module not in registry:
        return 1
    versions = registry[module].get("versions", {})
    # Count versions for this optimizer
    count = sum(1 for v in versions.values() if v.get("optimizer") == optimizer)
    return count + 1


def find_latest_artifact(module: str, optimizer: str) -> Path | None:
    """Find the latest artifact for a module."""
    optimizer_dir = ARTIFACTS_DIR / f"dspy_{optimizer}" / module

    if not optimizer_dir.exists():
        return None

    # Find provider folders
    for provider_dir in optimizer_dir.iterdir():
        if not provider_dir.is_dir():
            continue

        # For GEPA: look for latest/ or timestamped folders
        if optimizer == "gepa":
            latest = provider_dir / "latest" / "optimized.json"
            if latest.exists():
                return latest
            # Or find most recent timestamped folder
            for ts_dir in sorted(provider_dir.iterdir(), reverse=True):
                if ts_dir.is_dir() and (ts_dir / "optimized.json").exists():
                    return ts_dir / "optimized.json"

        # For MIPRO
        elif optimizer == "mipro":
            result = provider_dir / "optimized.json"
            if result.exists():
                return result

        # For COPRO
        elif optimizer == "copro":
            result = provider_dir / "copro_result.json"
            if result.exists():
                return result

    return None


def format_demos_as_examples(demos: list, input_keys: list, output_keys: list) -> str:
    """Format MIPRO demos as markdown examples."""
    if not demos:
        return ""

    lines = ["## Examples", ""]

    for i, demo in enumerate(demos, 1):
        lines.append(f"### Example {i}")
        lines.append("")
        lines.append("**Input:**")
        lines.append("```json")

        # Extract input fields
        input_data = {k: demo.get(k) for k in input_keys if k in demo}
        lines.append(json.dumps(input_data, indent=2, ensure_ascii=False))
        lines.append("```")
        lines.append("")
        lines.append("**Output:**")
        lines.append("```json")

        # Extract output fields
        output_data = {}
        for k in output_keys:
            if k in demo:
                val = demo[k]
                # Convert "None" string to null
                if val == "None" or val == "NULL":
                    val = None
                output_data[k] = val
        lines.append(json.dumps(output_data, indent=2, ensure_ascii=False))
        lines.append("```")
        lines.append("")

    return "\n".join(lines)


def format_input_variables(input_keys: list, module_config: dict) -> str:
    """Format input variables section."""
    lines = ["## Input Variables", ""]

    # Try to add descriptions based on common key names
    descriptions = {
        # Keywords & Classification
        "keyword": "The search keyword to classify",

        # Brand-related
        "brand_name": "The brand name",
        "brand_entities": "List of own brand name variations",
        "variations_own": "Own brand variations",
        "related_terms_own": "Related brand terms",
        "own_brand": "Own brand name",
        "competitor_entities": "List of competitor brand names",
        "competitors": "List of competitor brands",
        "known_competitor_brands": "Known competitor brand names in the category",

        # Product basics
        "title": "Product title",
        "bullet_points": "Product bullet points",
        "description": "Product description",
        "manufacturer": "Product manufacturer",

        # Category & Taxonomy
        "product_type": "Product type",
        "category_root": "Root category",
        "category_sub": "Sub-category",
        "taxonomy": "Product taxonomy hierarchy",

        # Attributes
        "attribute_table": "Product attribute rankings",
        "product_attributes": "Product attributes",
        "variants": "Product variants",
        "color": "Product color",
        "size": "Product size",
        "material": "Product material",
        "style": "Product style",
        "model": "Product model",
        "item_form": "Item form/format",
        "number_of_items": "Number of items included",
        "included_components": "Components included with product",

        # Use & Audience
        "primary_use": "Primary intended use",
        "validated_use": "Validated primary use of the product",
        "use_cases": "Product use cases",
        "specific_uses": "Specific use scenarios",
        "audiences": "Target audiences",
        "target_audience": "Target audience for the product",

        # Constraints
        "hard_constraints": "Hard constraints for the product",
    }

    for key in input_keys:
        desc = descriptions.get(key, "")
        if desc:
            lines.append(f"- `{key}`: {desc}")
        else:
            lines.append(f"- `{key}`")

    lines.append("")
    return "\n".join(lines)


def format_output_section(output_keys: list, module_config: dict) -> str:
    """Format output section."""
    lines = ["## Output Format", ""]
    lines.append("Return a JSON object with the following fields:")
    lines.append("```json")
    lines.append("{")

    output_lines = []
    for key in output_keys:
        output_lines.append(f'  "{key}": ...')
    output_lines.append('  "confidence": 0.0-1.0')
    output_lines.append('  "reasoning": "explanation"')

    lines.append(",\n".join(output_lines))
    lines.append("}")
    lines.append("```")
    lines.append("")

    return "\n".join(lines)


def extract_gepa(artifact_path: Path, module: str, config: dict) -> tuple[str, dict]:
    """Extract prompt from GEPA result."""
    data = json.loads(artifact_path.read_text())

    prompt = data.get("optimized_prompt", "")

    metadata = {
        "score": data.get("final_score"),
        "baseline_score": data.get("initial_score"),
        "model": data.get("task_model", "").replace("openai/", ""),
        "train_size": data.get("train_size"),
        "val_size": data.get("val_size"),
    }

    return prompt, metadata


def extract_mipro(artifact_path: Path, module: str, config: dict) -> tuple[str, dict]:
    """Extract prompt from MIPRO result."""
    data = json.loads(artifact_path.read_text())

    instruction = data.get("instruction", "")
    demos = data.get("demos", [])
    input_keys = config.get("input_keys", [])
    output_keys = config.get("output_keys", [])

    # Build prompt
    lines = [
        "## Instructions",
        "",
        instruction,
        "",
    ]

    # Add input variables
    lines.append(format_input_variables(input_keys, config))

    # Add examples from demos
    if demos:
        lines.append(format_demos_as_examples(demos, input_keys, output_keys))

    # Add output format
    lines.append(format_output_section(output_keys, config))

    prompt = "\n".join(lines)

    metadata = {
        "score": data.get("score"),
        "baseline_score": None,  # MIPRO doesn't track baseline
        "model": data.get("provider", ""),
        "train_size": None,
        "demos_count": len(demos),
    }

    return prompt, metadata


def extract_copro(artifact_path: Path, module: str, config: dict) -> tuple[str, dict]:
    """Extract prompt from COPRO result."""
    data = json.loads(artifact_path.read_text())

    instruction = data.get("optimized_instruction", "")
    input_keys = config.get("input_keys", [])
    output_keys = config.get("output_keys", [])

    # Build prompt
    lines = [
        "## Instructions",
        "",
        instruction,
        "",
    ]

    # Add input variables
    lines.append(format_input_variables(input_keys, config))

    # Add output format
    lines.append(format_output_section(output_keys, config))

    prompt = "\n".join(lines)

    metadata = {
        "score": None,  # COPRO doesn't return score
        "baseline_score": None,
        "model": data.get("provider", ""),
        "train_size": data.get("train_size"),
        "breadth": data.get("breadth"),
        "depth": data.get("depth"),
    }

    return prompt, metadata


def extract_optimized(
    module: str,
    optimizer: str,
    cleanup: bool = False,
) -> Path | None:
    """Extract optimized prompt from artifacts."""

    # Get module config
    if module not in MODULE_CONFIGS:
        print(f"Unknown module: {module}")
        return None

    config = MODULE_CONFIGS[module]
    module_name = config["name"]

    # Find artifact
    artifact_path = find_latest_artifact(module, optimizer)
    if not artifact_path:
        print(f"No artifacts found for {module} with {optimizer}")
        return None

    print(f"Found artifact: {artifact_path}")

    # Extract based on optimizer
    extractors = {
        "gepa": extract_gepa,
        "mipro": extract_mipro,
        "copro": extract_copro,
    }

    if optimizer not in extractors:
        print(f"Unknown optimizer: {optimizer}")
        return None

    prompt_content, metadata = extractors[optimizer](artifact_path, module, config)

    # Load registry
    registry = load_registry()

    # Get version number
    version = get_next_version(registry, module, optimizer)

    # Generate filename: m02_mipro_v1_classify_own_brand_keywords.md
    base_name = config["prompt"].stem  # e.g., m02_v1_classify_own_brand_keywords
    # Remove version from original name
    parts = base_name.split("_")
    # Find and remove version part (v1, v2, etc.)
    parts_clean = [p for p in parts if not (p.startswith("v") and p[1:].isdigit())]
    clean_name = "_".join(parts_clean)

    filename = f"{clean_name}_{optimizer}_v{version}.md"
    output_path = OUTPUT_DIR / filename

    # Write prompt (clean, no header - metadata goes to registry)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path.write_text(prompt_content.strip() + "\n")

    print(f"Created: {output_path}")

    # Update registry
    if module not in registry:
        registry[module] = {"current_version": None, "versions": {}}

    date_str = datetime.now().strftime("%Y-%m-%d")
    version_key = f"{optimizer}_v{version}"
    registry[module]["versions"][version_key] = {
        "file": filename,
        "module_name": module_name,
        "optimizer": optimizer,
        "date": date_str,
        "source": str(artifact_path.relative_to(PROJECT_ROOT)),
        **{k: v for k, v in metadata.items() if v is not None},
    }
    registry[module]["current_version"] = version_key

    save_registry(registry)
    print(f"Updated registry: {module} -> {version_key}")

    # Cleanup artifacts if requested
    if cleanup:
        artifact_dir = artifact_path.parent
        if artifact_dir.name == "latest":
            artifact_dir = artifact_dir.parent  # Go up to provider dir

        # Find module dir to remove
        module_artifact_dir = ARTIFACTS_DIR / f"dspy_{optimizer}" / module
        if module_artifact_dir.exists():
            shutil.rmtree(module_artifact_dir)
            print(f"Cleaned up: {module_artifact_dir}")

    return output_path


def list_available():
    """List available artifacts for extraction."""
    print("Available artifacts:\n")

    for optimizer in ["gepa", "mipro", "copro"]:
        optimizer_dir = ARTIFACTS_DIR / f"dspy_{optimizer}"
        if not optimizer_dir.exists():
            continue

        print(f"=== {optimizer.upper()} ===")
        for module_dir in sorted(optimizer_dir.iterdir()):
            if module_dir.is_dir():
                artifact = find_latest_artifact(module_dir.name, optimizer)
                if artifact:
                    # Try to get score
                    try:
                        data = json.loads(artifact.read_text())
                        score = data.get("final_score") or data.get("score") or "?"
                        if isinstance(score, float):
                            score = f"{score:.2f}"
                    except:
                        score = "?"
                    print(f"  {module_dir.name}: score={score}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Extract optimized prompts from artifacts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("module", nargs="?", help="Module to extract (e.g., m02)")
    parser.add_argument("--source", "-s", choices=["gepa", "mipro", "copro"],
                        help="Optimizer source")
    parser.add_argument("--cleanup", "-c", action="store_true",
                        help="Delete artifacts after extraction")
    parser.add_argument("--list", "-l", action="store_true",
                        help="List available artifacts")

    args = parser.parse_args()

    if args.list:
        list_available()
        return

    if not args.module:
        parser.error("Module required. Use --list to see available.")

    if not args.source:
        parser.error("--source required (gepa, mipro, or copro)")

    extract_optimized(args.module, args.source, args.cleanup)


if __name__ == "__main__":
    main()
