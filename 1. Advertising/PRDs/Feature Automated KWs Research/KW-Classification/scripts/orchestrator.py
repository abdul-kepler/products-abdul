#!/usr/bin/env python3
"""
Experiment Orchestrator for KW Classification Pipeline

Automates the workflow of testing prompts against datasets and saving results.

Usage:
    # Run single module with sample
    python scripts/orchestrator.py run --module m12 --samples 50

    # Run multiple modules
    python scripts/orchestrator.py run --modules m12,m13,m14,m15,m16 --samples 100

    # Run all modules
    python scripts/orchestrator.py run --all --samples 50

    # Full dataset + upload to Braintrust
    python scripts/orchestrator.py run --module m12b --full --upload-braintrust

    # Only save CSV locally
    python scripts/orchestrator.py run --module m15 --samples 50 --output csv

    # Save both CSV and upload to Braintrust
    python scripts/orchestrator.py run --module m12 --samples 50 --output both
"""

import argparse
import json
import os
import sys
import csv
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))
from config import (
    PROJECT_ROOT, MODULES, PROMPTS_DIR, SCHEMAS_DIR, DATASETS_DIR,
    EXPERIMENT_RESULTS_DIR, PROJECT_NAME, get_module, load_api_key,
    OPENAI_API_KEY, DEFAULT_MODEL, DEFAULT_TEMPERATURE
)

try:
    from openai import OpenAI
    import braintrust
except ImportError as e:
    print(f"Error: {e}")
    print("Run: pip install openai braintrust")
    sys.exit(1)

from experiment_registry import ExperimentRegistry, ExperimentRecord, compute_prompt_hash


# ============================================================================
# Configuration
# ============================================================================

@dataclass
class ExperimentConfig:
    """Configuration for an experiment run."""
    modules: List[str]
    samples: Optional[int] = None  # None = full dataset
    output_mode: str = "csv"  # "csv", "braintrust", "both"
    model: str = DEFAULT_MODEL
    temperature: float = DEFAULT_TEMPERATURE
    version: str = "v1"
    parallel_requests: int = 5
    dry_run: bool = False


# ============================================================================
# Data Loading
# ============================================================================

def find_prompt_file(module_id: str) -> Optional[Path]:
    """Find prompt file for a module (handles various naming conventions)."""
    module = get_module(module_id)
    slug = module["slug"]

    # Try different naming patterns
    patterns = [
        PROMPTS_DIR / f"{module_id}_{slug}.md",
        PROMPTS_DIR / f"{slug}.md",
        PROMPTS_DIR / f"{module_id.lower()}_{slug}.md",
    ]

    for pattern in patterns:
        if pattern.exists():
            return pattern

    # Fallback: glob search
    matches = list(PROMPTS_DIR.glob(f"*{module_id}*.md")) + list(PROMPTS_DIR.glob(f"*{slug}*.md"))
    if matches:
        return matches[0]

    return None


def find_schema_file(module_id: str) -> Optional[Path]:
    """Find JSON schema file for a module."""
    module = get_module(module_id)
    slug = module["slug"]

    patterns = [
        SCHEMAS_DIR / f"{module_id}_{slug}_schema.json",
        SCHEMAS_DIR / f"{slug}_schema.json",
        SCHEMAS_DIR / f"{module_id}_{slug.replace('_v1.1', '')}_schema_v1.1.json",
    ]

    for pattern in patterns:
        if pattern.exists():
            return pattern

    # Fallback: glob search
    matches = list(SCHEMAS_DIR.glob(f"*{module_id}*schema*.json"))
    if matches:
        return matches[0]

    return None


def find_dataset_file(module_id: str) -> Optional[Path]:
    """Find dataset file for a module."""
    module = get_module(module_id)
    slug = module["slug"]

    patterns = [
        DATASETS_DIR / f"{module_id}_{slug}.jsonl",
        DATASETS_DIR / f"{slug}.jsonl",
        DATASETS_DIR / f"{module_id}_{slug.replace('_v1.1', '')}_v1.1.jsonl",
    ]

    for pattern in patterns:
        if pattern.exists():
            return pattern

    # Fallback: glob search
    matches = list(DATASETS_DIR.glob(f"*{module_id}*.jsonl"))
    if matches:
        return matches[0]

    return None


def load_prompt(prompt_path: Path) -> str:
    """Load prompt content from file."""
    return prompt_path.read_text(encoding="utf-8")


def load_schema(schema_path: Path) -> dict:
    """Load JSON schema from file."""
    return json.loads(schema_path.read_text(encoding="utf-8"))


def load_dataset(dataset_path: Path, samples: Optional[int] = None) -> List[dict]:
    """Load dataset records from JSONL file."""
    records = []
    with open(dataset_path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    if samples and samples < len(records):
        # Stratified sampling would be better, but simple random for now
        import random
        random.seed(42)  # Reproducible
        records = random.sample(records, samples)

    return records


# ============================================================================
# Template Rendering
# ============================================================================

def render_template(prompt_template: str, record: dict) -> str:
    """Render prompt template with record data using {{variable}} syntax."""
    rendered = prompt_template

    input_data = record.get("input", record)

    # Flatten nested input for template rendering
    flat_data = {}
    for key, value in input_data.items():
        if isinstance(value, (dict, list)):
            flat_data[key] = json.dumps(value, indent=2)
        else:
            flat_data[key] = str(value) if value is not None else ""

    # Replace {{variable}} patterns
    for key, value in flat_data.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)

    return rendered


# ============================================================================
# LLM Execution
# ============================================================================

class LLMRunner:
    """Handles LLM API calls with rate limiting."""

    def __init__(self, model: str = DEFAULT_MODEL, temperature: float = DEFAULT_TEMPERATURE):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = model
        self.temperature = temperature
        self._lock = threading.Lock()
        self._request_count = 0

    def run(self, prompt: str, schema: Optional[dict] = None) -> dict:
        """Execute LLM call and return parsed response with metrics."""
        messages = [{"role": "user", "content": prompt}]

        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
        }

        # Add structured output if schema provided
        if schema:
            kwargs["response_format"] = schema

        start_time = time.time()

        try:
            response = self.client.chat.completions.create(**kwargs)
            duration = time.time() - start_time

            content = response.choices[0].message.content
            usage = response.usage

            # Calculate cost estimate (gpt-4o-mini pricing)
            prompt_cost = (usage.prompt_tokens / 1_000_000) * 0.15
            completion_cost = (usage.completion_tokens / 1_000_000) * 0.60
            estimated_cost = prompt_cost + completion_cost

            # Try to parse as JSON
            try:
                parsed = json.loads(content)
            except json.JSONDecodeError:
                parsed = {"raw_output": content, "parse_error": True}

            # Add metrics to result
            parsed["_metrics"] = {
                "duration": duration,
                "llm_duration": duration,
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens,
                "estimated_cost": estimated_cost,
            }

            return parsed

        except Exception as e:
            return {"error": str(e), "error_type": type(e).__name__}

    def run_batch(self, items: List[tuple], parallel: int = 5) -> List[dict]:
        """Run multiple LLM calls in parallel."""
        results = [None] * len(items)

        def process_item(idx, prompt, schema):
            result = self.run(prompt, schema)
            with self._lock:
                self._request_count += 1
            return idx, result

        with ThreadPoolExecutor(max_workers=parallel) as executor:
            futures = {
                executor.submit(process_item, idx, prompt, schema): idx
                for idx, (prompt, schema) in enumerate(items)
            }

            for future in as_completed(futures):
                idx, result = future.result()
                results[idx] = result

        return results


# ============================================================================
# Result Processing
# ============================================================================

def compare_outputs(expected: Any, actual: Any, module_type: str) -> dict:
    """Compare expected vs actual output and calculate metrics."""
    result = {
        "match": False,
        "expected": expected,
        "actual": actual,
    }

    if module_type in ("binary_classifier", "classifier"):
        # Compare classification values
        exp_val = str(expected).lower().strip() if expected else ""
        act_val = str(actual).lower().strip() if actual else ""
        result["match"] = exp_val == act_val

    elif module_type == "extraction":
        # For lists, compare sets
        if isinstance(expected, list) and isinstance(actual, list):
            exp_set = set(str(x).lower() for x in expected)
            act_set = set(str(x).lower() for x in actual)

            if exp_set or act_set:
                precision = len(exp_set & act_set) / len(act_set) if act_set else 0
                recall = len(exp_set & act_set) / len(exp_set) if exp_set else 0
                f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

                result["precision"] = precision
                result["recall"] = recall
                result["f1"] = f1
                result["match"] = f1 >= 0.8  # Consider 80%+ as match
            else:
                result["match"] = True
        else:
            result["match"] = str(expected).lower() == str(actual).lower()

    elif module_type in ("validation", "ranking"):
        # Text comparison
        exp_norm = str(expected).lower().strip() if expected else ""
        act_norm = str(actual).lower().strip() if actual else ""
        result["match"] = exp_norm == act_norm

    else:
        # Default: exact match
        result["match"] = expected == actual

    return result


def calculate_metrics(results: List[dict]) -> dict:
    """Calculate aggregate metrics from results."""
    total = len(results)
    correct = sum(1 for r in results if r.get("comparison", {}).get("match", False))
    errors = sum(1 for r in results if "error" in r.get("output", {}))

    metrics = {
        "total": total,
        "correct": correct,
        "errors": errors,
        "accuracy": correct / total if total > 0 else 0,
        "error_rate": errors / total if total > 0 else 0,
    }

    # Add precision/recall/f1 if available
    precisions = [r["comparison"]["precision"] for r in results if "precision" in r.get("comparison", {})]
    recalls = [r["comparison"]["recall"] for r in results if "recall" in r.get("comparison", {})]
    f1s = [r["comparison"]["f1"] for r in results if "f1" in r.get("comparison", {})]

    if precisions:
        metrics["avg_precision"] = sum(precisions) / len(precisions)
        metrics["avg_recall"] = sum(recalls) / len(recalls)
        metrics["avg_f1"] = sum(f1s) / len(f1s)

    return metrics


# ============================================================================
# Output Handlers
# ============================================================================

def get_output_folder(module_id: str) -> Path:
    """Get output folder for a module following naming convention."""
    module = get_module(module_id)
    folder_name = f"{module_id.upper()}_{module['name']}"
    folder_path = EXPERIMENT_RESULTS_DIR / folder_name
    folder_path.mkdir(parents=True, exist_ok=True)
    return folder_path


def get_output_filename(module_id: str, version: str = "v1") -> str:
    """Generate output filename following naming convention."""
    module = get_module(module_id)
    date_str = datetime.now().strftime("%d%m%y")

    # Find next run number
    folder = get_output_folder(module_id)
    existing = list(folder.glob(f"*_{date_str}_*.csv"))
    run_num = len(existing) + 1

    return f"{module_id.upper()}_{module['name']}_{version}_{date_str}_{run_num}.csv"


def get_module_specific_columns(module_id: str) -> List[str]:
    """Get module-specific columns for CSV output."""
    # Define module-specific extracted fields
    module_columns = {
        "m12": ["Expected_Output", "output_HC"],
        "m12b": ["Expected_Output", "output_HC"],
        "m13": ["Expected_same_type", "Output_same_type", "Keyword_product_type"],
        "m14": ["Expected_Output", "output_HC"],
        "m15": ["Expected_Output", "output_HC", "same_primary_use", "keyword_product_type"],
        "m16": ["Expected_Output", "output_HC", "used_together", "relationship"],
    }
    return module_columns.get(module_id, ["Expected_Output", "output_HC"])


def extract_module_specific_values(module_id: str, result: dict) -> dict:
    """Extract module-specific values from result."""
    output = result.get("output", {})
    expected = result.get("expected", {})

    values = {}

    if module_id == "m13":
        values["Expected_same_type"] = expected.get("same_type", "")
        values["Output_same_type"] = output.get("same_type", "")
        values["Keyword_product_type"] = output.get("keyword_product_type", "")
    elif module_id == "m15":
        values["Expected_Output"] = expected.get("relevancy", "")
        values["output_HC"] = output.get("relevancy", "")
        values["same_primary_use"] = output.get("same_primary_use", "")
        values["keyword_product_type"] = output.get("keyword_product_type", "")
    elif module_id == "m16":
        values["Expected_Output"] = expected.get("relevancy", "")
        values["output_HC"] = output.get("relevancy", "")
        values["used_together"] = output.get("used_together", "")
        values["relationship"] = output.get("relationship", "")
    else:
        # Default for m12, m12b, m14, and others
        values["Expected_Output"] = expected.get("relevancy", "")
        values["output_HC"] = output.get("relevancy", "")

    return values


def save_to_csv(results: List[dict], module_id: str, version: str = "v1", run_metrics: dict = None) -> Path:
    """Save results to CSV file matching existing format."""
    folder = get_output_folder(module_id)
    filename = get_output_filename(module_id, version)
    filepath = folder / filename

    if not results:
        print(f"  No results to save for {module_id}")
        return filepath

    # Base columns + module-specific + trailing columns
    module_columns = get_module_specific_columns(module_id)
    fieldnames = ["name", "input", "output", "expected", "ASIN", "Brand", "Keyword"] + \
                 module_columns + ["Reasoning", "metrics", "metadata"]

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()

        for result in results:
            input_data = result.get("input", {})
            output_data = result.get("output", {})
            expected_data = result.get("expected", {})
            record_metadata = result.get("metadata", {})

            # Build metrics dict
            metrics_dict = {
                "cached": None,
                "duration": result.get("duration", 0),
                "llm_duration": result.get("llm_duration", 0),
                "time_to_first_token": result.get("time_to_first_token", 0),
                "prompt_tokens": result.get("prompt_tokens", 0),
                "completion_tokens": result.get("completion_tokens", 0),
                "total_tokens": result.get("total_tokens", 0),
                "estimated_cost": result.get("estimated_cost", 0),
            }

            # Build metadata dict matching existing format
            metadata_dict = {
                "asin": record_metadata.get("asin", ""),
                "module_id": module_id,
                "split": record_metadata.get("split", "eval"),
                "version": version,
                "keyword": input_data.get("keyword", ""),
                "brand_name": record_metadata.get("brand_name", ""),
            }

            # Get module-specific values
            module_values = extract_module_specific_values(module_id, result)

            # Extract reasoning - handle both direct and nested formats
            reasoning = output_data.get("reasoning", "")
            if not reasoning and isinstance(output_data, dict):
                # For M12B-style outputs with step-based reasoning
                for step_key in ["step1_hard_constraint", "step2_product_type", "step3_primary_use", "step4_complementary"]:
                    step_data = output_data.get(step_key)
                    if isinstance(step_data, dict) and step_data.get("reasoning"):
                        reasoning = step_data.get("reasoning", "")
                        break

            row = {
                "name": "eval",
                "input": json.dumps(input_data),
                "output": json.dumps(output_data),
                "expected": json.dumps(expected_data),
                "ASIN": record_metadata.get("asin", ""),
                "Brand": record_metadata.get("brand_name", ""),
                "Keyword": input_data.get("keyword", ""),
                "Reasoning": reasoning,
                "metrics": json.dumps(metrics_dict),
                "metadata": json.dumps(metadata_dict),
                **module_values,
            }
            writer.writerow(row)

    return filepath


def upload_to_braintrust(results: List[dict], module_id: str, metrics: dict) -> str:
    """Upload results to Braintrust as experiment."""
    module = get_module(module_id)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # "root" prefix indicates local test runs
    experiment_name = f"root_{module_id}_{module['name']}_{timestamp}"

    try:
        load_api_key()

        experiment = braintrust.init(
            project=PROJECT_NAME,
            experiment=experiment_name,
            metadata={
                "module": module_id,
                "module_name": module["name"],
                "timestamp": timestamp,
                "total_samples": metrics["total"],
                "accuracy": metrics["accuracy"],
            }
        )

        for result in results:
            experiment.log(
                input=result.get("input", {}),
                output=result.get("output", {}),
                expected=result.get("expected", {}),
                scores={"correct": 1.0 if result.get("comparison", {}).get("match") else 0.0},
                metadata={"module": module_id}
            )

        summary = experiment.summarize()
        return f"https://www.braintrust.dev/app/{PROJECT_NAME}/experiments/{experiment_name}"

    except Exception as e:
        print(f"  Error uploading to Braintrust: {e}")
        return ""


# ============================================================================
# Main Orchestrator
# ============================================================================

def run_module_experiment(
    module_id: str,
    config: ExperimentConfig,
    runner: LLMRunner
) -> dict:
    """Run experiment for a single module."""
    print(f"\n{'='*60}")
    print(f"Module: {module_id.upper()}")
    print(f"{'='*60}")

    module = get_module(module_id)

    # Find files
    prompt_path = find_prompt_file(module_id)
    schema_path = find_schema_file(module_id)
    dataset_path = find_dataset_file(module_id)

    if not prompt_path:
        print(f"  ERROR: Prompt file not found for {module_id}")
        return {"error": "prompt_not_found"}

    if not dataset_path:
        print(f"  ERROR: Dataset file not found for {module_id}")
        return {"error": "dataset_not_found"}

    print(f"  Prompt: {prompt_path.name}")
    print(f"  Schema: {schema_path.name if schema_path else 'None'}")
    print(f"  Dataset: {dataset_path.name}")

    # Load data
    prompt_template = load_prompt(prompt_path)
    schema = load_schema(schema_path) if schema_path else None
    records = load_dataset(dataset_path, config.samples)

    print(f"  Records: {len(records)}")

    if config.dry_run:
        print("  [DRY RUN] Skipping LLM calls")
        return {"dry_run": True, "records": len(records)}

    # Prepare LLM calls
    items = []
    for record in records:
        rendered_prompt = render_template(prompt_template, record)
        items.append((rendered_prompt, schema))

    # Execute
    print(f"  Running {len(items)} LLM calls (parallel={config.parallel_requests})...")
    start_time = time.time()
    outputs = runner.run_batch(items, parallel=config.parallel_requests)
    elapsed = time.time() - start_time
    print(f"  Completed in {elapsed:.1f}s ({len(items)/elapsed:.1f} req/s)")

    # Process results
    results = []
    for record, output in zip(records, outputs):
        expected = record.get("expected", {})

        # Extract metrics from output (added by LLMRunner)
        metrics_data = output.pop("_metrics", {}) if isinstance(output, dict) else {}

        # Get the primary output field based on module type
        if module["type"] in ("binary_classifier", "classifier"):
            exp_val = expected.get("relevancy", expected.get("classification", expected.get("result")))
            act_val = output.get("relevancy", output.get("classification", output.get("result")))
        else:
            exp_val = expected
            act_val = output

        comparison = compare_outputs(exp_val, act_val, module["type"])

        results.append({
            "input": record.get("input", {}),
            "expected": expected,
            "output": output,
            "comparison": comparison,
            "metadata": record.get("metadata", {}),
            # Metrics from LLM call
            "duration": metrics_data.get("duration", 0),
            "llm_duration": metrics_data.get("llm_duration", 0),
            "prompt_tokens": metrics_data.get("prompt_tokens", 0),
            "completion_tokens": metrics_data.get("completion_tokens", 0),
            "total_tokens": metrics_data.get("total_tokens", 0),
            "estimated_cost": metrics_data.get("estimated_cost", 0),
        })

    # Calculate metrics
    metrics = calculate_metrics(results)
    print(f"  Accuracy: {metrics['accuracy']:.1%} ({metrics['correct']}/{metrics['total']})")
    if metrics.get("avg_f1"):
        print(f"  Avg F1: {metrics['avg_f1']:.3f}")

    # Output
    output_paths = {}
    registry = ExperimentRegistry()
    local_id = registry.generate_local_id(module_id)

    # Compute prompt hash for versioning
    prompt_hash = compute_prompt_hash(prompt_path) if prompt_path else None

    if config.output_mode in ("csv", "both"):
        csv_path = save_to_csv(results, module_id, config.version)
        output_paths["csv"] = str(csv_path)
        print(f"  CSV: {csv_path}")

    braintrust_id = None
    braintrust_url = None

    if config.output_mode in ("braintrust", "both"):
        bt_url = upload_to_braintrust(results, module_id, metrics)
        if bt_url:
            output_paths["braintrust"] = bt_url
            braintrust_url = bt_url
            # Extract braintrust_id from URL
            braintrust_id = bt_url.split("/")[-1] if bt_url else None
            print(f"  Braintrust: {bt_url}")

    # Register experiment
    record = ExperimentRecord(
        local_id=local_id,
        module_id=module_id,
        csv_path=output_paths.get("csv", ""),
        created_at=datetime.now().isoformat(),
        braintrust_id=braintrust_id,
        braintrust_url=braintrust_url,
        uploaded_at=datetime.now().isoformat() if braintrust_url else None,
        prompt_version=config.version,
        prompt_hash=prompt_hash,
        dataset_version="v1.1",
        samples=len(results),
        accuracy=metrics.get("accuracy", 0),
        metrics=metrics,
        status="uploaded" if braintrust_url else "local_only",
        model=config.model,
    )
    registry.add_experiment(record)
    print(f"  Registered: {local_id}")

    return {
        "module": module_id,
        "local_id": local_id,
        "metrics": metrics,
        "outputs": output_paths,
        "elapsed": elapsed,
    }


def run_experiments(config: ExperimentConfig) -> dict:
    """Run experiments for all configured modules."""
    print("\n" + "=" * 60)
    print("EXPERIMENT ORCHESTRATOR")
    print("=" * 60)
    print(f"Modules: {', '.join(config.modules)}")
    print(f"Samples: {config.samples or 'full'}")
    print(f"Output: {config.output_mode}")
    print(f"Model: {config.model}")

    runner = LLMRunner(model=config.model, temperature=config.temperature)

    results = {}
    for module_id in config.modules:
        try:
            result = run_module_experiment(module_id, config, runner)
            results[module_id] = result
        except Exception as e:
            print(f"  ERROR: {e}")
            results[module_id] = {"error": str(e)}

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    for module_id, result in results.items():
        if "error" in result:
            print(f"  {module_id}: ERROR - {result['error']}")
        elif "dry_run" in result:
            print(f"  {module_id}: DRY RUN ({result['records']} records)")
        else:
            metrics = result.get("metrics", {})
            print(f"  {module_id}: {metrics.get('accuracy', 0):.1%} accuracy")

    return results


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Experiment Orchestrator for KW Classification Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run single module with sample
  python scripts/orchestrator.py run --module m12 --samples 50

  # Run multiple modules
  python scripts/orchestrator.py run --modules m12,m13,m14,m15,m16 --samples 100

  # Run all modules
  python scripts/orchestrator.py run --all --samples 50

  # Full dataset + upload to Braintrust
  python scripts/orchestrator.py run --module m12b --full --upload-braintrust

  # List available modules
  python scripts/orchestrator.py list
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run experiments")
    run_parser.add_argument("--module", "-m", help="Single module ID (e.g., m12)")
    run_parser.add_argument("--modules", help="Comma-separated module IDs (e.g., m12,m13,m14)")
    run_parser.add_argument("--all", action="store_true", help="Run all modules")
    run_parser.add_argument("--samples", "-n", type=int, help="Number of samples (default: full dataset)")
    run_parser.add_argument("--full", action="store_true", help="Use full dataset")
    run_parser.add_argument("--output", "-o", choices=["csv", "braintrust", "both"], default="csv",
                          help="Output mode (default: csv)")
    run_parser.add_argument("--upload-braintrust", action="store_true", help="Upload to Braintrust")
    run_parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Model to use (default: {DEFAULT_MODEL})")
    run_parser.add_argument("--version", "-v", default="v1", help="Version label for output files")
    run_parser.add_argument("--parallel", "-p", type=int, default=5, help="Parallel requests (default: 5)")
    run_parser.add_argument("--dry-run", action="store_true", help="Don't make LLM calls")

    # List command
    list_parser = subparsers.add_parser("list", help="List available modules")

    args = parser.parse_args()

    if args.command == "list":
        print("Available modules:")
        for module_id, module in sorted(MODULES.items()):
            prompt_path = find_prompt_file(module_id)
            dataset_path = find_dataset_file(module_id)
            enabled = module.get("enabled", True)
            if prompt_path and dataset_path and enabled:
                status = "✓"
            elif not enabled:
                status = "○"  # Disabled
            else:
                status = "✗"  # Missing files
            disabled_tag = " [disabled]" if not enabled else ""
            print(f"  {status} {module_id}: {module['name']} ({module['type']}){disabled_tag}")
        return

    if args.command == "run":
        # Determine modules to run
        if args.all:
            # Only include enabled modules
            modules = [m for m, cfg in MODULES.items() if cfg.get("enabled", True)]
        elif args.modules:
            modules = [m.strip() for m in args.modules.split(",")]
        elif args.module:
            modules = [args.module]
        else:
            parser.error("Specify --module, --modules, or --all")
            return

        # Determine output mode
        output_mode = args.output
        if args.upload_braintrust:
            output_mode = "both" if output_mode == "csv" else "braintrust"

        # Determine samples
        samples = None if args.full else args.samples

        config = ExperimentConfig(
            modules=modules,
            samples=samples,
            output_mode=output_mode,
            model=args.model,
            version=args.version,
            parallel_requests=args.parallel,
            dry_run=args.dry_run,
        )

        run_experiments(config)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
