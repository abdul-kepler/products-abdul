#!/usr/bin/env python3
"""
Experiment Registry

Tracks local experiments and their Braintrust mappings.
Maintains a central registry of all experiment runs with metadata.
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
from dataclasses import dataclass, asdict, field

# Registry file location
REGISTRY_DIR = Path(__file__).parent.parent / "experiment_results"
REGISTRY_FILE = REGISTRY_DIR / ".registry.json"


@dataclass
class ExperimentRecord:
    """Single experiment record."""
    local_id: str
    module_id: str
    csv_path: str
    created_at: str

    # Braintrust mapping
    braintrust_id: Optional[str] = None
    braintrust_url: Optional[str] = None
    uploaded_at: Optional[str] = None

    # Versioning
    prompt_version: str = "v1"
    prompt_hash: Optional[str] = None
    dataset_version: str = "v1.1"

    # Metrics
    samples: int = 0
    accuracy: float = 0.0
    metrics: Dict = field(default_factory=dict)

    # Status: local_only, uploaded, synced, failed
    status: str = "local_only"

    # Additional metadata
    model: str = "gpt-4o-mini"
    notes: str = ""


class ExperimentRegistry:
    """Manages experiment registry."""

    def __init__(self, registry_path: Path = REGISTRY_FILE):
        self.registry_path = registry_path
        self.data = {"experiments": {}, "metadata": {}}
        self._load()

    def _load(self):
        """Load registry from file."""
        if self.registry_path.exists():
            try:
                with open(self.registry_path) as f:
                    self.data = json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Could not parse {self.registry_path}, starting fresh")
                self.data = {"experiments": {}, "metadata": {}}
        else:
            self.data = {"experiments": {}, "metadata": {}}

    def _save(self):
        """Save registry to file."""
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.registry_path, "w") as f:
            json.dump(self.data, f, indent=2, default=str)

    def generate_local_id(self, module_id: str) -> str:
        """Generate unique local experiment ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"exp_{timestamp}_{module_id}"

    def add_experiment(self, record: ExperimentRecord) -> str:
        """Add new experiment to registry."""
        self.data["experiments"][record.local_id] = asdict(record)
        self._save()
        return record.local_id

    def update_experiment(self, local_id: str, **kwargs) -> bool:
        """Update experiment fields."""
        if local_id not in self.data["experiments"]:
            return False

        self.data["experiments"][local_id].update(kwargs)
        self._save()
        return True

    def get_experiment(self, local_id: str) -> Optional[Dict]:
        """Get experiment by local ID."""
        return self.data["experiments"].get(local_id)

    def find_by_braintrust_id(self, braintrust_id: str) -> Optional[Dict]:
        """Find experiment by Braintrust ID."""
        for exp in self.data["experiments"].values():
            if exp.get("braintrust_id") == braintrust_id:
                return exp
        return None

    def find_by_csv_path(self, csv_path: str) -> Optional[Dict]:
        """Find experiment by CSV path."""
        csv_path_str = str(csv_path)
        for exp in self.data["experiments"].values():
            if exp.get("csv_path") == csv_path_str:
                return exp
        return None

    def list_experiments(
        self,
        module_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """List experiments with optional filtering."""
        results = []
        for exp in self.data["experiments"].values():
            if module_id and exp.get("module_id") != module_id:
                continue
            if status and exp.get("status") != status:
                continue
            results.append(exp)

        # Sort by created_at descending
        results.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return results[:limit]

    def list_not_uploaded(self) -> List[Dict]:
        """List experiments not yet uploaded to Braintrust."""
        return self.list_experiments(status="local_only")

    def mark_uploaded(
        self,
        local_id: str,
        braintrust_id: str,
        braintrust_url: str
    ) -> bool:
        """Mark experiment as uploaded to Braintrust."""
        return self.update_experiment(
            local_id,
            braintrust_id=braintrust_id,
            braintrust_url=braintrust_url,
            uploaded_at=datetime.now().isoformat(),
            status="uploaded"
        )

    def get_stats(self) -> Dict:
        """Get registry statistics."""
        experiments = self.data["experiments"].values()

        status_counts = {}
        module_counts = {}

        for exp in experiments:
            status = exp.get("status", "unknown")
            module = exp.get("module_id", "unknown")

            status_counts[status] = status_counts.get(status, 0) + 1
            module_counts[module] = module_counts.get(module, 0) + 1

        return {
            "total": len(self.data["experiments"]),
            "by_status": status_counts,
            "by_module": module_counts,
        }

    def delete_experiment(self, local_id: str) -> bool:
        """Delete experiment from registry."""
        if local_id in self.data["experiments"]:
            del self.data["experiments"][local_id]
            self._save()
            return True
        return False

    def cleanup_missing_files(self) -> List[str]:
        """Remove entries for CSV files that no longer exist."""
        removed = []
        to_remove = []

        for local_id, exp in self.data["experiments"].items():
            csv_path = exp.get("csv_path")
            if csv_path and not Path(csv_path).exists():
                to_remove.append(local_id)

        for local_id in to_remove:
            del self.data["experiments"][local_id]
            removed.append(local_id)

        if removed:
            self._save()

        return removed


def compute_prompt_hash(prompt_path: Path) -> str:
    """Compute hash of prompt file for versioning."""
    if not prompt_path.exists():
        return ""
    content = prompt_path.read_text()
    return hashlib.md5(content.encode()).hexdigest()[:8]


# CLI for registry management
def main():
    import argparse

    parser = argparse.ArgumentParser(description="Experiment Registry Management")
    subparsers = parser.add_subparsers(dest="command")

    # List command
    list_parser = subparsers.add_parser("list", help="List experiments")
    list_parser.add_argument("--module", "-m", help="Filter by module")
    list_parser.add_argument("--status", "-s", help="Filter by status")
    list_parser.add_argument("--limit", "-n", type=int, default=20)

    # Stats command
    subparsers.add_parser("stats", help="Show registry statistics")

    # Not uploaded command
    subparsers.add_parser("pending", help="List experiments not uploaded")

    # Cleanup command
    subparsers.add_parser("cleanup", help="Remove entries for missing files")

    # Show command
    show_parser = subparsers.add_parser("show", help="Show experiment details")
    show_parser.add_argument("local_id", help="Local experiment ID")

    args = parser.parse_args()
    registry = ExperimentRegistry()

    if args.command == "list":
        experiments = registry.list_experiments(
            module_id=args.module,
            status=args.status,
            limit=args.limit
        )
        print(f"Experiments ({len(experiments)}):")
        print("-" * 80)
        for exp in experiments:
            bt_status = "✓" if exp.get("braintrust_url") else "○"
            acc = exp.get("accuracy", 0)
            print(f"  {bt_status} {exp['local_id']}")
            print(f"      Module: {exp['module_id']} | Accuracy: {acc:.1%} | Status: {exp['status']}")
            print(f"      CSV: {exp.get('csv_path', 'N/A')}")
            if exp.get("braintrust_url"):
                print(f"      BT: {exp['braintrust_url']}")
            print()

    elif args.command == "stats":
        stats = registry.get_stats()
        print("Registry Statistics")
        print("=" * 40)
        print(f"Total experiments: {stats['total']}")
        print("\nBy status:")
        for status, count in sorted(stats["by_status"].items()):
            print(f"  {status}: {count}")
        print("\nBy module:")
        for module, count in sorted(stats["by_module"].items()):
            print(f"  {module}: {count}")

    elif args.command == "pending":
        experiments = registry.list_not_uploaded()
        print(f"Pending upload ({len(experiments)}):")
        print("-" * 60)
        for exp in experiments:
            print(f"  {exp['local_id']} ({exp['module_id']}) - {exp.get('accuracy', 0):.1%}")

    elif args.command == "cleanup":
        removed = registry.cleanup_missing_files()
        if removed:
            print(f"Removed {len(removed)} entries:")
            for r in removed:
                print(f"  - {r}")
        else:
            print("No cleanup needed")

    elif args.command == "show":
        exp = registry.get_experiment(args.local_id)
        if exp:
            print(json.dumps(exp, indent=2))
        else:
            print(f"Experiment not found: {args.local_id}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
