"""
Rubric Loader - Loads binary Pass/Fail rubrics from YAML configuration.

Each rubric defines:
- criterion: What specific thing to check
- task: What the evaluator should do
- fail_definition: When to mark as Fail
- pass_definition: When to mark as Pass
- examples: Few-shot hard examples (Pass and Fail)
"""

import yaml
from pathlib import Path
from typing import Optional


class RubricLoader:
    """Load and manage binary Pass/Fail rubrics."""

    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "rubrics.yaml"

        self.config_path = Path(config_path)
        self._config = None
        self._load_config()

    def _load_config(self):
        """Load the YAML configuration file."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self._config = yaml.safe_load(f)
        else:
            self._config = {"rubrics": {}, "judges": {}}

    def get_rubric(self, rubric_id: str) -> Optional[dict]:
        """
        Get a specific rubric by ID.

        Args:
            rubric_id: e.g., "M02_correct_classification"

        Returns:
            Rubric dict with criterion, task, fail/pass definitions, examples
        """
        rubrics = self._config.get("rubrics", {})
        return rubrics.get(rubric_id)

    def get_rubrics_for_module(self, module_id: str) -> list[str]:
        """
        Get all rubric IDs for a specific module.

        Args:
            module_id: e.g., "M02"

        Returns:
            List of rubric IDs like ["M02_correct_classification", "M02_matched_term_valid", ...]
        """
        rubrics = self._config.get("rubrics", {})
        matching = []

        for rubric_id, rubric in rubrics.items():
            if rubric.get("module") == module_id:
                matching.append(rubric_id)

        return matching

    def get_all_rubric_ids(self) -> list[str]:
        """Get all rubric IDs."""
        return list(self._config.get("rubrics", {}).keys())

    def get_poll_panel(self) -> list[dict]:
        """Get the PoLL judge panel configuration."""
        judges = self._config.get("judges", {})
        return judges.get("poll_panel", [
            {"model": "gpt-4o-mini", "provider": "openai"},
            {"model": "claude-3-haiku-20240307", "provider": "anthropic"},
            {"model": "command-r", "provider": "cohere"}
        ])

    def get_output_format(self) -> dict:
        """Get the expected output format."""
        judges = self._config.get("judges", {})
        return judges.get("output_format", {
            "reasoning": "string",
            "label": "Pass | Fail"
        })

    def get_failure_categories(self) -> dict:
        """Get failure category definitions."""
        return self._config.get("failure_categories", {})

    def list_modules(self) -> list[str]:
        """Get list of all modules that have rubrics."""
        rubrics = self._config.get("rubrics", {})
        modules = set()

        for rubric in rubrics.values():
            if "module" in rubric:
                modules.add(rubric["module"])

        return sorted(modules)

    def get_rubric_summary(self, rubric_id: str) -> dict:
        """Get a brief summary of a rubric."""
        rubric = self.get_rubric(rubric_id)
        if not rubric:
            return None

        return {
            "id": rubric_id,
            "module": rubric.get("module"),
            "criterion": rubric.get("criterion"),
            "task": rubric.get("task"),
            "has_examples": len(rubric.get("examples", [])) > 0
        }

    def get_module_summary(self, module_id: str) -> dict:
        """Get summary of all rubrics for a module."""
        rubric_ids = self.get_rubrics_for_module(module_id)

        criteria = []
        for rid in rubric_ids:
            rubric = self.get_rubric(rid)
            if rubric:
                criteria.append({
                    "id": rid,
                    "criterion": rubric.get("criterion"),
                    "has_examples": len(rubric.get("examples", [])) > 0
                })

        return {
            "module_id": module_id,
            "num_criteria": len(criteria),
            "criteria": criteria
        }

    def format_rubric_for_display(self, rubric_id: str) -> str:
        """Format a rubric for human-readable display."""
        rubric = self.get_rubric(rubric_id)
        if not rubric:
            return f"Rubric {rubric_id} not found"

        lines = [
            f"## {rubric_id}",
            f"**Module:** {rubric.get('module', 'N/A')}",
            f"**Criterion:** {rubric.get('criterion', 'N/A')}",
            "",
            f"**Task:** {rubric.get('task', 'N/A')}",
            "",
            "**Fail Definition:**",
            rubric.get('fail_definition', 'N/A'),
            "",
            "**Pass Definition:**",
            rubric.get('pass_definition', 'N/A'),
        ]

        examples = rubric.get('examples', [])
        if examples:
            lines.append("")
            lines.append(f"**Examples:** {len(examples)} provided")
            for i, ex in enumerate(examples, 1):
                lines.append(f"  {i}. {ex.get('label', 'N/A')}: {ex.get('reasoning', 'N/A')[:50]}...")

        return "\n".join(lines)
