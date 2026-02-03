#!/usr/bin/env python3
"""
Mapping Loader - Central access to resource mappings.

This module provides a single source of truth for all prompt/dataset/Braintrust mappings.

Usage:
    from scripts.mapping_loader import MappingLoader, get_mappings

    # Quick access (uses singleton)
    mappings = get_mappings()
    prompt_id = mappings.get_prompt_id("m01")
    dataset_id = mappings.get_dataset_id("m01")

    # Full control
    loader = MappingLoader()
    prompt_info = loader.get_prompt("m08_v2_pairwise")
    dataset_info = loader.get_dataset("m08_sd1")

Examples:
    # Get Braintrust prompt ID
    >>> get_mappings().get_prompt_id("m08")
    'd6a085bf-1952-4f92-b220-3011583350d3'

    # Get local file path
    >>> get_mappings().get_prompt_path("m08")
    Path('prompts/modules/m08_assign_attribute_ranks.md')

    # List all prompts with Braintrust IDs
    >>> get_mappings().list_uploaded_prompts()
    ['m01', 'm01_v2', 'm01_v3', 'm01a', 'm01a_v2', ...]
"""

from pathlib import Path
from typing import Optional, Dict, List, Any
import yaml

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
MAPPINGS_FILE = PROJECT_ROOT / "evaluation_KD" / "evaluation_experimentV5" / "resource_mappings.yaml"


class MappingLoader:
    """Load and access resource mappings."""

    _instance = None
    _data = None

    def __new__(cls):
        """Singleton pattern - only one instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize and load mappings if not already loaded."""
        if MappingLoader._data is None:
            self.reload()

    def reload(self) -> None:
        """Reload mappings from file."""
        if not MAPPINGS_FILE.exists():
            raise FileNotFoundError(f"Mappings file not found: {MAPPINGS_FILE}")

        with open(MAPPINGS_FILE) as f:
            MappingLoader._data = yaml.safe_load(f)

    @property
    def data(self) -> dict:
        """Get raw mapping data."""
        return MappingLoader._data

    @property
    def prompts(self) -> dict:
        """Get all prompt mappings."""
        return self.data.get("prompts", {})

    @property
    def datasets(self) -> dict:
        """Get all dataset mappings."""
        return self.data.get("datasets", {})

    @property
    def module_defaults(self) -> dict:
        """Get module default mappings."""
        return self.data.get("module_defaults", {})

    @property
    def project_id(self) -> str:
        """Get Braintrust project ID."""
        return self.data.get("project", {}).get("id", "")

    @property
    def project_name(self) -> str:
        """Get Braintrust project name."""
        return self.data.get("project", {}).get("name", "")

    # -------------------------------------------------------------------------
    # Prompt Access
    # -------------------------------------------------------------------------

    def get_prompt(self, key: str) -> Optional[dict]:
        """
        Get prompt mapping by key.

        Args:
            key: Prompt key (e.g., "m01", "m08_v2_pairwise")

        Returns:
            Prompt mapping dict or None if not found
        """
        return self.prompts.get(key)

    def get_prompt_id(self, key: str) -> Optional[str]:
        """Get Braintrust prompt ID by key."""
        prompt = self.get_prompt(key)
        return prompt.get("braintrust_id") if prompt else None

    def get_prompt_slug(self, key: str) -> Optional[str]:
        """Get Braintrust prompt slug by key."""
        prompt = self.get_prompt(key)
        return prompt.get("braintrust_slug") if prompt else None

    def get_prompt_path(self, key: str) -> Optional[Path]:
        """Get local prompt file path by key."""
        prompt = self.get_prompt(key)
        if prompt and prompt.get("local_file"):
            return PROJECT_ROOT / prompt["local_file"]
        return None

    def get_schema_path(self, key: str) -> Optional[Path]:
        """Get local schema file path by key."""
        prompt = self.get_prompt(key)
        if prompt and prompt.get("schema_file"):
            return PROJECT_ROOT / prompt["schema_file"]
        return None

    def find_prompt_by_file(self, local_file: str) -> Optional[str]:
        """
        Find prompt key by local file path.

        Args:
            local_file: Relative path like "prompts/modules/m08_assign_attribute_ranks.md"

        Returns:
            Prompt key or None
        """
        # Normalize path
        local_file = str(local_file).replace(str(PROJECT_ROOT) + "/", "")

        for key, prompt in self.prompts.items():
            if prompt.get("local_file") == local_file:
                return key
        return None

    def find_prompt_by_braintrust_id(self, braintrust_id: str) -> Optional[str]:
        """Find prompt key by Braintrust ID."""
        for key, prompt in self.prompts.items():
            if prompt.get("braintrust_id") == braintrust_id:
                return key
        return None

    def list_prompts(self) -> List[str]:
        """List all prompt keys."""
        return list(self.prompts.keys())

    def list_uploaded_prompts(self) -> List[str]:
        """List prompt keys that have Braintrust IDs."""
        return [
            key for key, prompt in self.prompts.items()
            if prompt.get("braintrust_id")
        ]

    def list_unuploaded_prompts(self) -> List[str]:
        """List prompt keys that don't have Braintrust IDs."""
        return [
            key for key, prompt in self.prompts.items()
            if not prompt.get("braintrust_id")
        ]

    # -------------------------------------------------------------------------
    # Dataset Access
    # -------------------------------------------------------------------------

    def get_dataset(self, key: str) -> Optional[dict]:
        """
        Get dataset mapping by key.

        Args:
            key: Dataset key (e.g., "m01", "m08_sd1")

        Returns:
            Dataset mapping dict or None if not found
        """
        return self.datasets.get(key)

    def get_dataset_id(self, key: str) -> Optional[str]:
        """Get Braintrust dataset ID by key."""
        dataset = self.get_dataset(key)
        return dataset.get("braintrust_id") if dataset else None

    def get_dataset_path(self, key: str) -> Optional[Path]:
        """Get local dataset file path by key."""
        dataset = self.get_dataset(key)
        if dataset and dataset.get("local_file"):
            return PROJECT_ROOT / dataset["local_file"]
        return None

    def find_dataset_by_file(self, local_file: str) -> Optional[str]:
        """Find dataset key by local file path."""
        local_file = str(local_file).replace(str(PROJECT_ROOT) + "/", "")

        for key, dataset in self.datasets.items():
            if dataset.get("local_file") == local_file:
                return key
        return None

    def find_dataset_by_braintrust_id(self, braintrust_id: str) -> Optional[str]:
        """Find dataset key by Braintrust ID."""
        for key, dataset in self.datasets.items():
            if dataset.get("braintrust_id") == braintrust_id:
                return key
        return None

    def list_datasets(self) -> List[str]:
        """List all dataset keys."""
        return list(self.datasets.keys())

    def list_uploaded_datasets(self) -> List[str]:
        """List dataset keys that have Braintrust IDs."""
        return [
            key for key, dataset in self.datasets.items()
            if dataset.get("braintrust_id")
        ]

    # -------------------------------------------------------------------------
    # Module Access
    # -------------------------------------------------------------------------

    def get_default_prompt(self, module: str) -> Optional[str]:
        """Get default prompt key for a module."""
        defaults = self.module_defaults.get(module)
        return defaults.get("prompt") if defaults else None

    def get_default_dataset(self, module: str) -> Optional[str]:
        """Get default dataset key for a module."""
        defaults = self.module_defaults.get(module)
        return defaults.get("dataset") if defaults else None

    def list_modules(self) -> List[str]:
        """List all canonical modules."""
        return list(self.module_defaults.keys())

    # -------------------------------------------------------------------------
    # Update Methods
    # -------------------------------------------------------------------------

    def update_prompt(self, key: str, updates: dict) -> None:
        """
        Update prompt mapping and save to file.

        Args:
            key: Prompt key
            updates: Dict of fields to update
        """
        if key not in self.prompts:
            self.data["prompts"][key] = {}

        self.data["prompts"][key].update(updates)
        self._save()

    def update_dataset(self, key: str, updates: dict) -> None:
        """
        Update dataset mapping and save to file.

        Args:
            key: Dataset key
            updates: Dict of fields to update
        """
        if key not in self.datasets:
            self.data["datasets"][key] = {}

        self.data["datasets"][key].update(updates)
        self._save()

    def _save(self) -> None:
        """Save mappings to file."""
        from datetime import datetime
        self.data["last_updated"] = datetime.now().strftime("%Y-%m-%d")

        with open(MAPPINGS_FILE, "w") as f:
            yaml.dump(
                self.data,
                f,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
                width=120
            )

    # -------------------------------------------------------------------------
    # Reporting
    # -------------------------------------------------------------------------

    def get_stats(self) -> dict:
        """Get mapping statistics."""
        prompts_uploaded = len(self.list_uploaded_prompts())
        prompts_total = len(self.list_prompts())
        datasets_uploaded = len(self.list_uploaded_datasets())
        datasets_total = len(self.list_datasets())

        return {
            "prompts": {
                "total": prompts_total,
                "uploaded": prompts_uploaded,
                "pending": prompts_total - prompts_uploaded,
            },
            "datasets": {
                "total": datasets_total,
                "uploaded": datasets_uploaded,
                "pending": datasets_total - datasets_uploaded,
            },
            "modules": len(self.list_modules()),
        }

    def print_summary(self) -> None:
        """Print mapping summary to console."""
        stats = self.get_stats()

        print("\n" + "=" * 60)
        print("RESOURCE MAPPINGS SUMMARY")
        print("=" * 60)
        print(f"Project: {self.project_name}")
        print(f"Project ID: {self.project_id}")
        print()
        print(f"Prompts:  {stats['prompts']['uploaded']:3d} / {stats['prompts']['total']:3d} uploaded")
        print(f"Datasets: {stats['datasets']['uploaded']:3d} / {stats['datasets']['total']:3d} uploaded")
        print(f"Modules:  {stats['modules']:3d} defined")

        # Show unuploaded prompts
        unuploaded = self.list_unuploaded_prompts()
        if unuploaded:
            print(f"\nPrompts without Braintrust IDs:")
            for key in unuploaded[:10]:
                prompt = self.get_prompt(key)
                print(f"  - {key}: {prompt.get('local_file', 'N/A')}")
            if len(unuploaded) > 10:
                print(f"  ... and {len(unuploaded) - 10} more")

        print("=" * 60)


# Singleton accessor
_loader_instance: Optional[MappingLoader] = None


def get_mappings() -> MappingLoader:
    """Get singleton MappingLoader instance."""
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = MappingLoader()
    return _loader_instance


# CLI
def main():
    """CLI for mapping operations."""
    import argparse

    parser = argparse.ArgumentParser(description="Resource Mapping Loader")
    subparsers = parser.add_subparsers(dest="command")

    # Summary command
    subparsers.add_parser("summary", help="Show mapping summary")

    # List command
    list_parser = subparsers.add_parser("list", help="List resources")
    list_parser.add_argument("type", choices=["prompts", "datasets", "modules"])
    list_parser.add_argument("--uploaded", action="store_true", help="Only show uploaded")
    list_parser.add_argument("--pending", action="store_true", help="Only show pending upload")

    # Get command
    get_parser = subparsers.add_parser("get", help="Get specific resource")
    get_parser.add_argument("type", choices=["prompt", "dataset"])
    get_parser.add_argument("key", help="Resource key (e.g., m01, m08_v2)")

    args = parser.parse_args()
    loader = MappingLoader()

    if args.command == "summary":
        loader.print_summary()

    elif args.command == "list":
        if args.type == "prompts":
            if args.uploaded:
                items = loader.list_uploaded_prompts()
            elif args.pending:
                items = loader.list_unuploaded_prompts()
            else:
                items = loader.list_prompts()
            print(f"Prompts ({len(items)}):")
            for key in items:
                prompt = loader.get_prompt(key)
                bt_id = prompt.get("braintrust_id", "")[:8] if prompt.get("braintrust_id") else "---"
                print(f"  {key:<20} [{bt_id}] {prompt.get('local_file', '')}")

        elif args.type == "datasets":
            if args.uploaded:
                items = loader.list_uploaded_datasets()
            else:
                items = loader.list_datasets()
            print(f"Datasets ({len(items)}):")
            for key in items:
                dataset = loader.get_dataset(key)
                bt_id = dataset.get("braintrust_id", "")[:8] if dataset.get("braintrust_id") else "---"
                print(f"  {key:<20} [{bt_id}] {dataset.get('local_file', '')}")

        elif args.type == "modules":
            items = loader.list_modules()
            print(f"Modules ({len(items)}):")
            for module in items:
                defaults = loader.module_defaults.get(module, {})
                print(f"  {module:<8} prompt={defaults.get('prompt')}, dataset={defaults.get('dataset')}")

    elif args.command == "get":
        if args.type == "prompt":
            info = loader.get_prompt(args.key)
        else:
            info = loader.get_dataset(args.key)

        if info:
            import json
            print(json.dumps(info, indent=2))
        else:
            print(f"Not found: {args.key}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
