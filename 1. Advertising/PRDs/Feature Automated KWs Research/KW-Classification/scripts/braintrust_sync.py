#!/usr/bin/env python3
"""
Sync and match local experiment files with Braintrust experiments.

Usage:
    python scripts/braintrust_sync.py                    # Show matching status
    python scripts/braintrust_sync.py --update-mappings  # Update experiment_mappings.yaml
"""

import argparse
import os
import re
import sys
import requests
from pathlib import Path
from datetime import datetime
from difflib import SequenceMatcher

import yaml

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))
from config import PROJECT_ID, load_api_key, EXPERIMENT_RESULTS_DIR

try:
    from braintrust_api import Braintrust as BraintrustAPI
except ImportError as e:
    print(f"Error: {e}")
    print("Run: pip install braintrust-api")
    sys.exit(1)


PROJECT_ROOT = Path(__file__).parent.parent
MAPPINGS_FILE = PROJECT_ROOT / "evaluation_KD" / "evaluation_experimentV5" / "experiment_mappings.yaml"


def get_experiment_metadata(client: BraintrustAPI, experiment_id: str, api_key: str) -> dict:
    """Get full experiment metadata including prompt and dataset info via REST API."""
    try:
        exp = client.experiments.retrieve(experiment_id)

        metadata = {
            'id': exp.id,
            'name': exp.name,
            'created': str(exp.created) if hasattr(exp, 'created') and exp.created else None,
            'project_id': exp.project_id if hasattr(exp, 'project_id') else None,
            'dataset_id': exp.dataset_id if hasattr(exp, 'dataset_id') else None,
            'dataset_version': exp.dataset_version if hasattr(exp, 'dataset_version') else None,
        }

        # Extract from experiment metadata
        exp_metadata = exp.metadata if hasattr(exp, 'metadata') and exp.metadata else {}
        metadata['model'] = exp_metadata.get('model')
        metadata['temperature'] = exp_metadata.get('temperature')
        metadata['dataset_name'] = exp_metadata.get('dataset')

        # Try to get dataset name from API if not in metadata
        if metadata['dataset_id'] and not metadata['dataset_name']:
            try:
                ds = client.datasets.retrieve(metadata['dataset_id'])
                metadata['dataset_name'] = ds.name if hasattr(ds, 'name') else None
            except:
                pass

        # Get prompt info from first event via REST API
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
                    metadata['prompt_id'] = prompt_info.get('id')
                    metadata['prompt_version_id'] = prompt_info.get('version')
                    metadata['prompt_session_id'] = prompt_info.get('prompt_session_id')
        except:
            pass

        return metadata
    except Exception as e:
        print(f"  Warning: Could not get metadata for {experiment_id}: {e}")
        return {}


def normalize_name(name: str) -> str:
    """Normalize filename/experiment name for comparison."""
    # Remove common suffixes and normalize
    name = name.lower()
    name = re.sub(r'\.csv$', '', name)
    name = re.sub(r'_\d{6}_\d+$', '', name)  # Remove date_number suffix like _150126_1
    name = re.sub(r'_\d{6}_gpt\d+$', '', name)  # Remove date_model suffix like _190126_gpt5
    name = re.sub(r'-[a-f0-9]{8}$', '', name)  # Remove hash suffix
    name = re.sub(r'_20\d{6}_\d+$', '', name)  # Remove _20260119_1414 suffix
    name = re.sub(r'[_-]+', '_', name)  # Normalize separators
    name = name.strip('_')
    return name


def extract_info_from_filename(filename: str) -> dict:
    """Extract module, version, model from filename."""
    info = {
        'module': None,
        'prompt_version': 'v1',
        'model': 'gpt-4o-mini',
        'dataset_variant': None,
    }

    name = filename.upper()

    # Extract module (M01, M01A, etc.)
    match = re.search(r'(M\d{2}[A-Z]?)', name)
    if match:
        info['module'] = match.group(1).lower()

    # Extract prompt version (V2, V3, etc.)
    match = re.search(r'[_-]V(\d+)[_-]', name)
    if match:
        info['prompt_version'] = f'v{match.group(1)}'

    # Extract model
    if 'GPT5' in name or 'GPT-5' in name:
        info['model'] = 'gpt-5'
    elif 'GPT4O' in name and 'MINI' not in name:
        info['model'] = 'gpt-4o'

    # Extract dataset variant (sd1, gd1, etc.)
    match = re.search(r'[_-](SD\d*|GD\d*)[_-]', name, re.IGNORECASE)
    if match:
        info['dataset_variant'] = match.group(1).lower()

    return info


def similarity(a: str, b: str) -> float:
    """Calculate string similarity ratio."""
    return SequenceMatcher(None, a, b).ratio()


def find_best_match(local_name: str, experiments: list) -> tuple:
    """Find best matching Braintrust experiment for a local file."""
    local_normalized = normalize_name(local_name)
    local_info = extract_info_from_filename(local_name)

    # Check for model in filename
    local_has_gpt5 = 'gpt5' in local_name.lower() or 'gpt-5' in local_name.lower()

    best_match = None
    best_score = 0

    for exp in experiments:
        exp_normalized = normalize_name(exp['name'])
        exp_info = extract_info_from_filename(exp['name'])
        exp_has_gpt5 = 'gpt5' in exp['name'].lower() or 'gpt-5' in exp['name'].lower()

        # Module must match
        if local_info['module'] != exp_info['module']:
            continue

        # Start with similarity score
        score = similarity(local_normalized, exp_normalized)

        # Boost for matching components
        if local_info['prompt_version'] == exp_info['prompt_version']:
            score += 0.15
        if local_info['dataset_variant'] == exp_info['dataset_variant']:
            score += 0.15

        # Model matching is important
        if local_has_gpt5 == exp_has_gpt5:
            score += 0.2
        else:
            score -= 0.3  # Penalize model mismatch

        # Exact match after normalization is best
        if local_normalized == exp_normalized:
            score = 1.5

        if score > best_score:
            best_score = score
            best_match = exp

    # Cap score at 1.0 for display
    return best_match, min(best_score, 1.0)


def get_all_local_files() -> list:
    """Get all local experiment CSV files."""
    files = []
    for csv_file in EXPERIMENT_RESULTS_DIR.glob("*/*.csv"):
        rel_path = csv_file.relative_to(PROJECT_ROOT)
        files.append({
            'path': csv_file,
            'relative_path': str(rel_path),
            'filename': csv_file.name,
            'folder': csv_file.parent.name,
            'info': extract_info_from_filename(csv_file.name),
        })
    return sorted(files, key=lambda x: x['filename'])


def get_all_experiments(client: BraintrustAPI) -> list:
    """Get all Braintrust experiments."""
    experiments = []
    for exp in client.experiments.list(project_id=PROJECT_ID):
        experiments.append({
            'id': exp.id,
            'name': exp.name,
            'created': exp.created if hasattr(exp, 'created') else None,
            'dataset_id': exp.dataset_id if hasattr(exp, 'dataset_id') else None,
            'info': extract_info_from_filename(exp.name),
        })
    return experiments


def sync_and_match(client: BraintrustAPI, update_mappings: bool = False, fetch_metadata: bool = False):
    """Sync local files with Braintrust experiments.

    Args:
        client: Braintrust API client
        update_mappings: Whether to update experiment_mappings.yaml
        fetch_metadata: Whether to fetch full metadata for each matched experiment
    """
    print(f"\n{'='*100}")
    print("BRAINTRUST ↔ LOCAL FILES SYNC")
    print(f"{'='*100}\n")

    # Get all data
    local_files = get_all_local_files()
    experiments = get_all_experiments(client)

    print(f"Local files: {len(local_files)}")
    print(f"Braintrust experiments: {len(experiments)}")
    print()

    # Match files
    matches = []
    unmatched_local = []
    unmatched_bt = list(experiments)

    print(f"{'Local File':<60} {'Match':<6} {'Braintrust Experiment':<50}")
    print("-" * 120)

    for local_file in local_files:
        best_match, score = find_best_match(local_file['filename'], unmatched_bt)

        if best_match and score >= 0.6:
            status = "✓" if score >= 0.8 else "~"
            print(f"{local_file['filename']:<60} {status:<6} {best_match['name'][:48]:<50}")

            matches.append({
                'local': local_file,
                'braintrust': best_match,
                'score': score,
            })

            # Remove from unmatched
            unmatched_bt = [e for e in unmatched_bt if e['id'] != best_match['id']]
        else:
            print(f"{local_file['filename']:<60} {'✗':<6} {'(no match)':<50}")
            unmatched_local.append(local_file)

    # Summary
    print(f"\n{'='*100}")
    print("SUMMARY")
    print(f"{'='*100}")
    print(f"✓ Matched: {len(matches)}")
    print(f"✗ Unmatched local files: {len(unmatched_local)}")
    print(f"✗ Unmatched Braintrust experiments: {len(unmatched_bt)}")

    # Show unmatched
    if unmatched_local:
        print(f"\n--- Unmatched Local Files ---")
        for f in unmatched_local:
            print(f"  • {f['filename']}")

    if unmatched_bt:
        print(f"\n--- Unmatched Braintrust Experiments ---")
        for exp in unmatched_bt[:10]:
            print(f"  • {exp['name']} ({exp['id'][:8]}...)")
        if len(unmatched_bt) > 10:
            print(f"  ... and {len(unmatched_bt) - 10} more")

    # Update mappings file
    if update_mappings:
        print(f"\n{'='*100}")
        print("UPDATING MAPPINGS FILE")
        print(f"{'='*100}")

        api_key = os.environ.get("BRAINTRUST_API_KEY")

        mappings = {
            'version': '2.0',
            'last_updated': datetime.now().strftime('%Y-%m-%d'),
            'sync_summary': {
                'total_local_files': len(local_files),
                'total_braintrust_experiments': len(experiments),
                'matched': len(matches),
                'unmatched_local': len(unmatched_local),
                'unmatched_braintrust': len(unmatched_bt),
            },
            'experiments': [],
            'unmatched_local_files': [],
            'unmatched_braintrust_experiments': [],
        }

        # Add matched experiments with full metadata
        for i, match in enumerate(matches):
            local = match['local']
            bt = match['braintrust']
            info = local['info']

            entry = {
                'braintrust_experiment_id': bt['id'],
                'braintrust_name': bt['name'],
                'local_file': local['relative_path'],
                'module': info['module'],
                'prompt_version': info['prompt_version'],
                'model': info['model'],
                'dataset_variant': info['dataset_variant'],
                'dataset_id': bt.get('dataset_id'),
                'match_score': round(match['score'], 2),
                'status': 'matched' if match['score'] >= 0.8 else 'partial_match',
            }

            # Fetch full metadata if requested
            if fetch_metadata and api_key:
                print(f"  Fetching metadata [{i+1}/{len(matches)}]: {bt['name'][:40]}...", end='\r')
                full_meta = get_experiment_metadata(client, bt['id'], api_key)
                if full_meta:
                    entry['model'] = full_meta.get('model') or entry['model']
                    entry['temperature'] = full_meta.get('temperature')
                    entry['dataset_name'] = full_meta.get('dataset_name')
                    entry['dataset_version'] = full_meta.get('dataset_version')
                    entry['prompt_id'] = full_meta.get('prompt_id')
                    entry['prompt_version_id'] = full_meta.get('prompt_version_id')
                    entry['prompt_session_id'] = full_meta.get('prompt_session_id')
                    entry['created'] = full_meta.get('created')

            mappings['experiments'].append(entry)

        if fetch_metadata:
            print(f"\n  Fetched metadata for {len(matches)} experiments")

        # Add unmatched local files
        for f in unmatched_local:
            mappings['unmatched_local_files'].append({
                'local_file': f['relative_path'],
                'module': f['info']['module'],
                'prompt_version': f['info']['prompt_version'],
                'model': f['info']['model'],
            })

        # Add unmatched Braintrust experiments
        for exp in unmatched_bt:
            mappings['unmatched_braintrust_experiments'].append({
                'braintrust_experiment_id': exp['id'],
                'braintrust_name': exp['name'],
                'module': exp['info']['module'],
            })

        # Save
        MAPPINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(MAPPINGS_FILE, 'w') as f:
            yaml.dump(mappings, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

        print(f"✓ Mappings saved to: {MAPPINGS_FILE}")

    return matches, unmatched_local, unmatched_bt


def main():
    parser = argparse.ArgumentParser(description="Sync local files with Braintrust experiments")
    parser.add_argument("--update-mappings", "-u", action="store_true",
                        help="Update experiment_mappings.yaml with sync results")
    parser.add_argument("--fetch-metadata", "-f", action="store_true",
                        help="Fetch full metadata (model, prompt_id, dataset_id) for each experiment")

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

    sync_and_match(client, update_mappings=args.update_mappings, fetch_metadata=args.fetch_metadata)


if __name__ == "__main__":
    main()
