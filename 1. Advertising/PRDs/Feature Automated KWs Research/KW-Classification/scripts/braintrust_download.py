#!/usr/bin/env python3
"""
Download experiment results from Braintrust.

Usage:
    python scripts/braintrust_download.py --experiment 34958fa0-920a-4e5c-92d1-aca1e8928381
    python scripts/braintrust_download.py --experiment 34958fa0-... --module m01 --prompt-version v3
    python scripts/braintrust_download.py --list-experiments
"""

import argparse
import csv
import json
import os
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))
from config import PROJECT_ID, PROJECT_NAME, load_api_key, MODULES, EXPERIMENT_RESULTS_DIR

try:
    import braintrust
    from braintrust_api import Braintrust as BraintrustAPI
except ImportError as e:
    print(f"Error: {e}")
    print("Run: pip install braintrust braintrust-api")
    sys.exit(1)


# Experiment mappings tracking file
PROJECT_ROOT = Path(__file__).parent.parent
MAPPINGS_FILE = PROJECT_ROOT / "evaluation_KD" / "evaluation_experimentV5" / "experiment_mappings.yaml"


def detect_module_from_name(name: str) -> Optional[str]:
    """Detect module ID from experiment name."""
    # Common patterns: M01_ExtractOwnBrandEntities, m01a-test, M01-V3-test, etc.
    name_upper = name.upper()

    # Try to extract module ID
    patterns = [
        r'(M\d{2}[A-Za-z]?)',  # M01, M01A, M01a
        r'(M\d{1,2})',  # M1, M01
    ]

    for pattern in patterns:
        match = re.search(pattern, name_upper)
        if match:
            module_id = match.group(1).lower()
            # Normalize to m01, m01a format
            if not module_id.startswith('m'):
                module_id = 'm' + module_id
            if len(module_id) == 2:  # m1 -> m01
                module_id = f"m0{module_id[1]}"
            return module_id

    return None


def detect_prompt_version_from_name(name: str) -> Optional[str]:
    """Detect prompt version from experiment name."""
    # Patterns: V3, v3, _v3_, -v3-
    match = re.search(r'[_-]?[Vv](\d+)[_-]?', name)
    if match:
        return f"v{match.group(1)}"
    return None


def detect_model_from_name(name: str) -> Optional[str]:
    """Detect model from experiment name."""
    name_lower = name.lower()
    # GPT models
    if 'gpt5' in name_lower or 'gpt-5' in name_lower:
        return 'gpt-5'
    if 'gpt4o-mini' in name_lower or 'gpt-4o-mini' in name_lower:
        return 'gpt-4o-mini'
    if 'gpt4o' in name_lower or 'gpt-4o' in name_lower:
        return 'gpt-4o'
    # Gemini models
    if 'gemini-2.0-flash' in name_lower or 'gemini2flash' in name_lower:
        return 'gemini-2.0-flash'
    if 'gemini-1.5-pro' in name_lower or 'gemini15pro' in name_lower:
        return 'gemini-1.5-pro'
    if 'gemini' in name_lower:
        return 'gemini'
    # Claude models
    if 'claude-3.5-sonnet' in name_lower or 'claude35sonnet' in name_lower:
        return 'claude-3.5-sonnet'
    if 'claude' in name_lower:
        return 'claude'
    return None


def list_experiments(client: BraintrustAPI, limit: int = 20):
    """List recent experiments."""
    print(f"\n{'='*80}")
    print("BRAINTRUST EXPERIMENTS")
    print(f"{'='*80}\n")

    try:
        experiments = list(client.experiments.list(project_id=PROJECT_ID))
        # Sort by created date (handle both datetime and string formats)
        def get_created(x):
            if hasattr(x, 'created') and x.created:
                if isinstance(x.created, datetime):
                    return x.created.isoformat()
                return str(x.created)
            return ''
        experiments = sorted(experiments, key=get_created, reverse=True)

        print(f"{'ID':<40} {'Name':<35} {'Created':<12}")
        print("-" * 87)

        for i, exp in enumerate(experiments[:limit]):
            if hasattr(exp, 'created') and exp.created:
                if isinstance(exp.created, datetime):
                    created = exp.created.strftime('%Y-%m-%d')
                else:
                    created = str(exp.created)[:10]
            else:
                created = 'N/A'
            exp_name = exp.name[:33] + ".." if len(exp.name) > 35 else exp.name
            print(f"{exp.id:<40} {exp_name:<35} {created:<12}")

        if len(experiments) > limit:
            print(f"\n... and {len(experiments) - limit} more experiments")

        print(f"\nTotal: {len(experiments)} experiments")

    except Exception as e:
        print(f"Error listing experiments: {e}")


def get_experiment_details(client: BraintrustAPI, experiment_id: str, api_key: str) -> dict:
    """Get experiment details including linked prompt and dataset."""
    import requests

    try:
        exp = client.experiments.retrieve(experiment_id)

        details = {
            'id': exp.id,
            'name': exp.name,
            'created': exp.created if hasattr(exp, 'created') else None,
            'project_id': exp.project_id if hasattr(exp, 'project_id') else None,
            'dataset_id': exp.dataset_id if hasattr(exp, 'dataset_id') else None,
            'dataset_version': exp.dataset_version if hasattr(exp, 'dataset_version') else None,
        }

        # Extract from experiment metadata
        exp_metadata = exp.metadata if hasattr(exp, 'metadata') and exp.metadata else {}
        details['model'] = exp_metadata.get('model')
        details['temperature'] = exp_metadata.get('temperature')
        details['dataset_name'] = exp_metadata.get('dataset')
        details['response_format'] = exp_metadata.get('response_format')
        details['use_cache'] = exp_metadata.get('use_cache')

        # Try to get dataset name from API if not in metadata
        if details['dataset_id'] and not details['dataset_name']:
            try:
                ds = client.datasets.retrieve(details['dataset_id'])
                details['dataset_name'] = ds.name if hasattr(ds, 'name') else None
            except:
                pass

        # Get prompt info from first event
        try:
            response = requests.post(
                f"https://api.braintrust.dev/v1/experiment/{experiment_id}/fetch",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"limit": 1}
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('events'):
                    event_metadata = data['events'][0].get('metadata') or {}
                    prompt_info = event_metadata.get('prompt') or {}
                    details['prompt_id'] = prompt_info.get('id')
                    details['prompt_version'] = prompt_info.get('version')
                    details['prompt_session_id'] = prompt_info.get('prompt_session_id')
        except:
            pass

        return details

    except Exception as e:
        print(f"Error getting experiment details: {e}")
        return {}


def fetch_experiment_results(experiment_id: str, api_key: str, limit: int = None) -> list:
    """Fetch experiment results using REST API."""
    import requests

    base_url = "https://api.braintrust.dev/v1"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    results = []
    cursor = None

    try:
        while True:
            # Build request payload
            payload = {"limit": min(limit or 100, 100)}
            if cursor:
                payload["cursor"] = cursor

            response = requests.post(
                f"{base_url}/experiment/{experiment_id}/fetch",
                headers=headers,
                json=payload
            )

            if response.status_code != 200:
                print(f"API Error: {response.status_code} - {response.text[:200]}")
                break

            data = response.json()
            events = data.get('events', [])

            for event in events:
                try:
                    # Filter: only process 'eval' type events (skip 'llm' and 'task' spans)
                    span_attrs = event.get('span_attributes') or {}
                    span_type = span_attrs.get('type', '')
                    if span_type and span_type != 'eval':
                        continue  # Skip non-eval events

                    # Parse Braintrust experiment event format
                    metadata = event.get('metadata') or {}
                    prompt_data = metadata.get('prompt') or {}
                    variables = prompt_data.get('variables') or {}

                    # Extract input - try variables first, then direct event.input
                    actual_input = variables.get('input') or {}
                    if not actual_input or actual_input == {}:
                        # Fallback to direct event.input (for non-prompt events)
                        direct_input = event.get('input')
                        if isinstance(direct_input, dict):
                            actual_input = direct_input
                        elif isinstance(direct_input, list):
                            # Skip LLM message format input
                            actual_input = {}

                    # Extract expected - try variables first, then direct event.expected
                    actual_expected = variables.get('expected') or {}
                    if not actual_expected or actual_expected == {}:
                        direct_expected = event.get('expected')
                        if isinstance(direct_expected, dict):
                            actual_expected = direct_expected

                    # For eval events, metadata is directly in event.metadata
                    # For prompt events, it's in variables.metadata
                    var_metadata = variables.get('metadata') or {}
                    if span_type == 'eval' and not var_metadata:
                        # Eval events store metadata directly in event.metadata
                        var_metadata = metadata  # Use event metadata directly

                    # Parse output from LLM response
                    raw_output = event.get('output') or []
                    actual_output = {}
                    if isinstance(raw_output, dict):
                        # Direct dict output
                        actual_output = raw_output
                    elif isinstance(raw_output, list) and raw_output:
                        first_output = raw_output[0]
                        if isinstance(first_output, dict):
                            message = first_output.get('message') or {}
                            content = message.get('content', '')
                            if content:
                                try:
                                    actual_output = json.loads(content)
                                except json.JSONDecodeError:
                                    actual_output = {'raw': content}

                    result = {
                        'id': event.get('id', ''),
                        'input': actual_input,
                        'output': actual_output,
                        'expected': actual_expected,
                        'metadata': var_metadata,
                        'scores': event.get('scores') or {},
                        'metrics': event.get('metrics') or {},
                    }
                    results.append(result)
                except Exception as e:
                    print(f"  Warning: Failed to parse event: {e}")
                    continue

                if limit and len(results) >= limit:
                    return results

            # Check for more pages
            cursor = data.get('cursor')
            if not cursor or not events:
                break

        return results

    except Exception as e:
        print(f"Error fetching experiment results: {e}")
        return []


def generate_filename(module_id: str, prompt_version: str, model: str, dataset_version: str = None) -> str:
    """Generate standard filename for experiment results."""
    module_config = MODULES.get(module_id, {})
    module_name = module_config.get('name', module_id.upper())

    # Format: M01_V3_ExtractOwnBrandEntities_v3_190126_gpt5.csv
    date_str = datetime.now().strftime('%d%m%y')

    version_prefix = prompt_version.upper()  # V3

    # Model suffix
    model_suffix = model.replace('-', '').replace('.', '') if model else ''
    model_suffix = model_suffix.replace('gpt4omini', 'gpt4omini').replace('gpt4o', 'gpt4o')

    # Dataset version in middle
    ds_version = dataset_version or prompt_version

    filename = f"{module_id.upper()}_{version_prefix}_{module_name}_{ds_version}_{date_str}_{model_suffix}.csv"

    return filename


def get_module_folder(module_id: str) -> Path:
    """Get the experiment results folder for a module."""
    module_config = MODULES.get(module_id, {})
    module_name = module_config.get('name', module_id.upper())

    folder_name = f"{module_id.upper()}_{module_name}"
    return EXPERIMENT_RESULTS_DIR / folder_name


# Column definitions for each module type (matching local file formats)
MODULE_COLUMNS = {
    # M01 family - Brand Entity Extraction
    'm01': ['name', 'ASIN', 'Brand', 'GoldenDataset', 'input', 'output', 'expected', 'metrics'],
    'm01a': ['name', 'ASIN', 'Brand', 'GoldenDataset', 'input', 'output', 'expected', 'metrics'],
    'm01b': ['name', 'ASIN', 'Brand', 'GoldenDataset', 'input', 'output', 'expected', 'metrics'],

    # M02 family - Own Brand Keywords Classification
    'm02': ['name', 'ASIN', 'Brand', 'Keyword', 'Expected CB', 'Output_OB', 'Reasoning', 'input', 'output', 'expected', 'metrics'],
    'm02b': ['name', 'ASIN', 'Brand', 'Keyword', 'Expected_OB', 'Output_OB', 'Reasoning', 'input', 'output', 'expected', 'metrics'],

    # M04 family - Competitor Brand Keywords Classification
    'm04': ['name', 'ASIN', 'Brand', 'Keyword', 'Expected CB', 'Output_CB', 'Reasoning', 'input', 'output', 'expected', 'metrics'],
    'm04b': ['name', 'ASIN', 'Brand', 'Keyword', 'Expected CB', 'Output_CB', 'Reasoning', 'input', 'output', 'expected', 'metrics'],

    # M05 family - Non-Branded Keywords Classification
    'm05': ['name', 'ASIN', 'Brand', 'Keyword', 'Expected_NB', 'Output_NB', 'Reasoning', 'input', 'output', 'expected', 'metrics'],
    'm05b': ['name', 'input', 'output', 'expected', 'metrics', 'ASIN', 'Brand', 'Keyword', 'Expected_NB', 'Output_NB', 'Reasoning'],

    # M06-M07 - Product Type & Attributes
    'm06': ['name', 'input', 'output', 'metrics', 'metadata', 'created', 'ASIN', 'Brand'],
    'm07': ['name', 'input', 'output', 'metrics', 'metadata', 'ASIN', 'Brand'],

    # M08 - Attribute Ranks
    'm08': ['name', 'input', 'output', 'expected', 'tags', 'metrics', 'metadata', 'comments', 'created', 'ASIN', 'Brand'],

    # M09-M11 - Primary Use & Hard Constraints
    'm09': ['name', 'input', 'output', 'expected', 'metrics', 'metadata', 'comments', 'created', 'ASIN', 'Brand', 'Primary_use', 'Reasoning'],
    'm10': ['name', 'input', 'output', 'expected', 'metrics', 'ASIN', 'Brand', 'Reasoning', 'validated_use', 'was_corrected'],
    'm11': ['name', 'input', 'output', 'expected', 'metrics', 'ASIN', 'Brand', 'Expected_hard_constrain', 'output_hard_constrain', 'Reasoning'],

    # M12 family - Hard Constraint Violation Check
    'm12': ['name', 'input', 'output', 'expected', 'ASIN', 'Brand', 'Keyword', 'Expected_Output', 'output_HC', 'Reasoning', 'metrics', 'metadata'],
    'm12b': ['name', 'input', 'output', 'expected', 'ASIN', 'Brand', 'Keyword', 'metrics', 'metadata'],  # Combined classification

    # M13-M16 - Product Checks
    'm13': ['name', 'input', 'output', 'expected', 'ASIN', 'Brand', 'Keyword', 'Expected_same_type', 'Output_same_type', 'Keyword_product_type', 'Reasoning', 'metadata', 'metrics'],
    'm14': ['name', 'input', 'output', 'expected', 'ASIN', 'Brand', 'Keyword', 'Expected_Output', 'output_HC', 'Reasoning', 'metadata', 'metrics'],
    'm15': ['name', 'input', 'output', 'expected', 'ASIN', 'Brand', 'Keyword', 'Expected_Output', 'output_HC', 'same_primary_use', 'keyword_product_type', 'Reasoning', 'metrics', 'metadata'],
    'm16': ['name', 'input', 'output', 'expected', 'ASIN', 'Brand', 'Keyword', 'Expected_Output', 'output_HC', 'used_together', 'relationship', 'Reasoning', 'metrics', 'metadata'],
}


def save_results_to_csv(results: list, output_path: Path, module_id: str):
    """Save experiment results to CSV file with module-specific columns."""
    if not results:
        print("No results to save")
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Get column definition for this module
    base_module = module_id.rstrip('ab')  # m01a -> m01, but keep m01a if defined
    fieldnames = MODULE_COLUMNS.get(module_id) or MODULE_COLUMNS.get(base_module) or MODULE_COLUMNS['m01']

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()

        for result in results:
            input_data = result.get('input', {})
            output_data = result.get('output', {})
            expected_data = result.get('expected', {})
            metadata = result.get('metadata', {})
            scores = result.get('scores', {})

            # Build row with all possible fields
            row = {
                'name': 'eval',
                'ASIN': metadata.get('asin', '') or input_data.get('asin', ''),
                'Brand': input_data.get('brand', '') or input_data.get('brand_name', ''),
                'input': json.dumps(input_data, ensure_ascii=False),
                'output': json.dumps(output_data, ensure_ascii=False),
                'expected': json.dumps(expected_data, ensure_ascii=False),
                'metrics': json.dumps(scores, ensure_ascii=False) if scores else '{}',
                'metadata': json.dumps(metadata, ensure_ascii=False) if metadata else '{}',
                'GoldenDataset': metadata.get('golden_dataset', True),
            }

            # Module-specific fields - Keyword field
            if module_id in ['m02', 'm02b', 'm04', 'm04b', 'm05', 'm05b', 'm12', 'm12b', 'm13', 'm14', 'm15', 'm16']:
                row['Keyword'] = input_data.get('keyword', '')

            # M02 family - Own Brand Keywords
            if module_id in ['m02', 'm02b']:
                row['Expected CB'] = expected_data.get('branding_scope_1', '')
                row['Expected_OB'] = expected_data.get('branding_scope_1', '')
                row['Output_OB'] = output_data.get('branding_scope_1', '') if isinstance(output_data, dict) else ''
                row['Reasoning'] = output_data.get('reasoning', '') if isinstance(output_data, dict) else ''

            # M04 family - Competitor Brand Keywords
            if module_id in ['m04', 'm04b']:
                row['Expected CB'] = expected_data.get('branding_scope_2', '')
                row['Output_CB'] = output_data.get('branding_scope_2', '') if isinstance(output_data, dict) else ''
                row['Reasoning'] = output_data.get('reasoning', '') if isinstance(output_data, dict) else ''

            # M05 family - Non-Branded Keywords
            if module_id in ['m05', 'm05b']:
                row['Expected_NB'] = expected_data.get('non_branded', '') or expected_data.get('branding_scope_3', '')
                row['Output_NB'] = output_data.get('non_branded', '') if isinstance(output_data, dict) else ''
                row['Reasoning'] = output_data.get('reasoning', '') if isinstance(output_data, dict) else ''

            # M06 - Product Type Taxonomy
            if module_id == 'm06':
                row['created'] = metadata.get('created', '')

            # M08 - Attribute Ranks
            if module_id == 'm08':
                row['tags'] = json.dumps(metadata.get('tags', []))
                row['comments'] = metadata.get('comments', '')
                row['created'] = metadata.get('created', '')

            # M09 - Primary Intended Use
            if module_id == 'm09':
                row['comments'] = metadata.get('comments', '')
                row['created'] = metadata.get('created', '')
                row['Primary_use'] = output_data.get('primary_use', '') if isinstance(output_data, dict) else ''
                row['Reasoning'] = output_data.get('reasoning', '') if isinstance(output_data, dict) else ''

            # M10 - Validate Primary Use
            if module_id == 'm10':
                row['Reasoning'] = output_data.get('reasoning', '') if isinstance(output_data, dict) else ''
                row['validated_use'] = output_data.get('validated_use', '') if isinstance(output_data, dict) else ''
                row['was_corrected'] = output_data.get('was_corrected', '') if isinstance(output_data, dict) else ''

            # M11 - Hard Constraints
            if module_id == 'm11':
                row['Expected_hard_constrain'] = expected_data.get('hard_constraint', '')
                row['output_hard_constrain'] = output_data.get('hard_constraint', '') if isinstance(output_data, dict) else ''
                row['Reasoning'] = output_data.get('reasoning', '') if isinstance(output_data, dict) else ''

            # M12 family - Hard Constraint Violation Check
            if module_id in ['m12', 'm12b']:
                row['Expected_Output'] = expected_data.get('output', '') or expected_data.get('expected_output', '')
                row['output_HC'] = output_data.get('output', '') if isinstance(output_data, dict) else ''
                row['Reasoning'] = output_data.get('reasoning', '') if isinstance(output_data, dict) else ''

            # M13 - Product Type Check
            if module_id == 'm13':
                row['Expected_same_type'] = expected_data.get('same_type', '')
                row['Output_same_type'] = output_data.get('same_type', '') if isinstance(output_data, dict) else ''
                row['Keyword_product_type'] = output_data.get('keyword_product_type', '') if isinstance(output_data, dict) else ''
                row['Reasoning'] = output_data.get('reasoning', '') if isinstance(output_data, dict) else ''

            # M14 - Primary Use Check Same Type
            if module_id == 'm14':
                row['Expected_Output'] = expected_data.get('output', '')
                row['output_HC'] = output_data.get('output', '') if isinstance(output_data, dict) else ''
                row['Reasoning'] = output_data.get('reasoning', '') if isinstance(output_data, dict) else ''

            # M15 - Substitute Check
            if module_id == 'm15':
                row['Expected_Output'] = expected_data.get('output', '')
                row['output_HC'] = output_data.get('output', '') if isinstance(output_data, dict) else ''
                row['same_primary_use'] = output_data.get('same_primary_use', '') if isinstance(output_data, dict) else ''
                row['keyword_product_type'] = output_data.get('keyword_product_type', '') if isinstance(output_data, dict) else ''
                row['Reasoning'] = output_data.get('reasoning', '') if isinstance(output_data, dict) else ''

            # M16 - Complementary Check
            if module_id == 'm16':
                row['Expected_Output'] = expected_data.get('output', '')
                row['output_HC'] = output_data.get('output', '') if isinstance(output_data, dict) else ''
                row['used_together'] = output_data.get('used_together', '') if isinstance(output_data, dict) else ''
                row['relationship'] = output_data.get('relationship', '') if isinstance(output_data, dict) else ''
                row['Reasoning'] = output_data.get('reasoning', '') if isinstance(output_data, dict) else ''

            writer.writerow(row)

    print(f"✓ Saved {len(results)} records to {output_path}")
    print(f"  Columns: {', '.join(fieldnames)}")


def save_experiment_metadata(output_path: Path, details: dict, records_count: int):
    """Save experiment metadata as JSON file alongside CSV."""
    meta_path = output_path.with_suffix('.meta.json')

    metadata = {
        'braintrust_experiment_id': details.get('id'),
        'braintrust_experiment_name': details.get('name'),
        'created': str(details.get('created')) if details.get('created') else None,
        'model': details.get('model'),
        'temperature': details.get('temperature'),
        'dataset_id': details.get('dataset_id'),
        'dataset_name': details.get('dataset_name'),
        'dataset_version': details.get('dataset_version'),
        'prompt_id': details.get('prompt_id'),
        'prompt_version': details.get('prompt_version'),
        'prompt_session_id': details.get('prompt_session_id'),
        'response_format': details.get('response_format'),
        'records_count': records_count,
        'downloaded_at': datetime.now().isoformat(),
    }

    with open(meta_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"✓ Metadata saved to {meta_path.name}")
    return metadata


def save_mapping(experiment_id: str, local_file: str, module_id: str, prompt_version: str,
                 model: str, details: dict = None):
    """Save experiment → local file mapping with full metadata."""
    import yaml

    MAPPINGS_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Load existing mappings
    mappings = {'experiments': []}
    if MAPPINGS_FILE.exists():
        with open(MAPPINGS_FILE) as f:
            mappings = yaml.safe_load(f) or {'experiments': []}

    details = details or {}

    # Add new mapping with full metadata
    mapping = {
        'braintrust_experiment_id': experiment_id,
        'braintrust_experiment_name': details.get('name'),
        'local_file': local_file,
        'module': module_id,
        'prompt_version': prompt_version,
        'model': model or details.get('model'),
        'temperature': details.get('temperature'),
        'dataset_id': details.get('dataset_id'),
        'dataset_name': details.get('dataset_name'),
        'prompt_id': details.get('prompt_id'),
        'prompt_version_id': details.get('prompt_version'),
        'downloaded_at': datetime.now().isoformat(),
    }

    # Remove existing mapping for same experiment
    mappings['experiments'] = [m for m in mappings['experiments'] if m.get('braintrust_experiment_id') != experiment_id]
    mappings['experiments'].append(mapping)

    with open(MAPPINGS_FILE, 'w') as f:
        yaml.dump(mappings, f, default_flow_style=False, sort_keys=False)

    print(f"✓ Mapping saved to {MAPPINGS_FILE}")


def download_experiment(
    client: BraintrustAPI,
    experiment_id: str,
    module_id: Optional[str] = None,
    prompt_version: Optional[str] = None,
    model: Optional[str] = None,
    limit: int = None,
    dry_run: bool = False,
    output_file: Optional[str] = None,
):
    """Download experiment results to local CSV file."""
    print(f"\n{'='*80}")
    print(f"DOWNLOADING EXPERIMENT: {experiment_id}")
    print(f"{'='*80}\n")

    # Get experiment details
    api_key = os.environ.get("BRAINTRUST_API_KEY")
    details = get_experiment_details(client, experiment_id, api_key)
    if not details:
        print("Failed to get experiment details")
        return

    print(f"Experiment: {details.get('name', 'N/A')}")
    print(f"Created: {details.get('created', 'N/A')}")
    print(f"Model: {details.get('model', 'N/A')}")
    print(f"Dataset ID: {details.get('dataset_id', 'N/A')}")
    print(f"Dataset: {details.get('dataset_name', 'N/A')}")
    print(f"Prompt ID: {details.get('prompt_id', 'N/A')[:20]}..." if details.get('prompt_id') else "Prompt ID: N/A")

    # Auto-detect module, version, model from name
    exp_name = details.get('name', '')

    if not module_id:
        module_id = detect_module_from_name(exp_name)
        if module_id:
            print(f"Auto-detected module: {module_id}")
        else:
            print("ERROR: Could not detect module. Use --module flag.")
            return

    if not prompt_version:
        prompt_version = detect_prompt_version_from_name(exp_name) or 'v1'
        print(f"Auto-detected prompt version: {prompt_version}")

    if not model:
        # Prefer model from experiment details (accurate), fall back to detection from name
        model = details.get('model') or detect_model_from_name(exp_name) or 'gpt-4o-mini'
        print(f"Model: {model}" + (" (from details)" if details.get('model') else " (auto-detected)"))

    # Generate output path
    if output_file:
        output_path = Path(output_file)
        if not output_path.is_absolute():
            output_path = PROJECT_ROOT / output_file
    else:
        filename = generate_filename(module_id, prompt_version, model)
        output_folder = get_module_folder(module_id)
        output_path = output_folder / filename

    print(f"\nOutput path: {output_path}")

    if dry_run:
        print("\n[DRY RUN] Would download and save to above location")
        return

    # Fetch results
    print(f"\nFetching experiment results...")
    api_key = os.environ.get("BRAINTRUST_API_KEY")
    results = fetch_experiment_results(experiment_id, api_key, limit)
    print(f"Fetched {len(results)} results")

    if not results:
        print("No results to download")
        return

    # Save to CSV
    save_results_to_csv(results, output_path, module_id)

    # Save metadata JSON
    save_experiment_metadata(output_path, details, len(results))

    # Save mapping (only if output is within project)
    try:
        rel_path = str(output_path.relative_to(PROJECT_ROOT))
        save_mapping(
            experiment_id=experiment_id,
            local_file=rel_path,
            module_id=module_id,
            prompt_version=prompt_version,
            model=model or details.get('model'),
            details=details,
        )
    except ValueError:
        print(f"  (Skipping mapping - output path is outside project)")

    print(f"\n✓ Download complete!")
    print(f"  File: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Download Braintrust experiment results")
    parser.add_argument("--experiment", "-e", type=str, help="Experiment ID to download")
    parser.add_argument("--module", "-m", type=str, help="Module ID (auto-detected if not provided)")
    parser.add_argument("--prompt-version", "-p", type=str, help="Prompt version (auto-detected if not provided)")
    parser.add_argument("--model", type=str, help="Model used (auto-detected if not provided)")
    parser.add_argument("--limit", "-l", type=int, default=None, help="Limit number of results")
    parser.add_argument("--output", "-o", type=str, default=None, help="Output file path (optional)")
    parser.add_argument("--list-experiments", action="store_true", help="List recent experiments")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without downloading")

    args = parser.parse_args()

    # Load API key
    try:
        api_key = load_api_key()
        os.environ["BRAINTRUST_API_KEY"] = api_key
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Initialize API client
    client = BraintrustAPI(api_key=api_key)

    if args.list_experiments:
        list_experiments(client)
        return

    if args.experiment:
        download_experiment(
            client=client,
            experiment_id=args.experiment,
            module_id=args.module,
            prompt_version=args.prompt_version,
            model=args.model,
            limit=args.limit,
            dry_run=args.dry_run,
            output_file=args.output,
        )
        return

    parser.print_help()


if __name__ == "__main__":
    main()
