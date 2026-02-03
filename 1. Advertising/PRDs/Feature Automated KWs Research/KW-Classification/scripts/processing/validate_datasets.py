#!/usr/bin/env python3
"""
Validate datasets against prompt variable definitions.

Checks that:
1. All variables in prompts have corresponding fields in datasets
2. All input fields in datasets are used by prompts
3. Data types match expected formats
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set, Any, Tuple
from collections import defaultdict


# Paths
PROMPTS_DIR = Path(__file__).parent.parent / "prompts" / "Pipeline_v1.1" / "Prompts"
DATASETS_DIR = Path(__file__).parent.parent / "datasets"
MODULE_REF = Path(__file__).parent.parent / "MODULE_REFERENCE.md"

# Module mapping: prompt file -> dataset file
MODULE_MAPPING = {
    "m01_extract_own_brand_entities": "m01_extract_own_brand_entities",
    "m02_classify_own_brand_keywords": "m02_classify_own_brand_keywords",
    "m03_generate_competitor_entities": "m03_generate_competitor_entities",
    "m04_classify_competitor_brand_keywords": "m04_classify_competitor_brand_keywords",
    "m05_classify_nonbranded_keywords": "m05_classify_nonbranded_keywords",
    "m06_generate_product_type_taxonomy": "m06_generate_product_type_taxonomy",
    "m07_extract_product_attributes": "m07_extract_product_attributes",
    "m08_assign_attribute_ranks": "m08_assign_attribute_ranks",
    "m09_identify_primary_intended_use": "m09_identify_primary_intended_use",
    "m10_validate_primary_intended_use": "m10_validate_primary_intended_use",
    "m11_identify_hard_constraints": "m11_identify_hard_constraints",
    "m12_keyword_classification_decision": "m12_keyword_classification_decision",
}

# 16-module variant mappings
MODULE_MAPPING_16 = {
    "m12_check_hard_constraint": "m12_check_hard_constraint",
    "m13_check_product_type": "m13_check_product_type",
    "m14_check_primary_use": "m14_check_primary_use_same_type",
    "m15_check_substitute": "m15_check_substitute",
    "m16_check_complementary": "m16_check_complementary",
}


def extract_prompt_variables(prompt_path: Path) -> Set[str]:
    """Extract all {{variable}} patterns from prompt file."""
    if not prompt_path.exists():
        return set()

    content = prompt_path.read_text()
    # Match {{variable_name}} pattern
    variables = set(re.findall(r'\{\{(\w+)\}\}', content))
    return variables


def extract_dataset_fields(dataset_path: Path, sample_size: int = 5) -> Tuple[Set[str], List[Dict]]:
    """Extract input field names from dataset JSONL file."""
    if not dataset_path.exists():
        return set(), []

    fields = set()
    samples = []

    with open(dataset_path, 'r') as f:
        for i, line in enumerate(f):
            if i >= sample_size:
                break
            try:
                example = json.loads(line)
                input_data = example.get('input', {})
                fields.update(input_data.keys())
                samples.append(example)
            except json.JSONDecodeError:
                continue

    return fields, samples


def check_field_types(samples: List[Dict], field: str) -> str:
    """Determine the data type of a field across samples."""
    types = set()
    for sample in samples:
        value = sample.get('input', {}).get(field)
        if value is None:
            types.add('null')
        elif isinstance(value, str):
            types.add('string')
        elif isinstance(value, list):
            types.add('array')
        elif isinstance(value, dict):
            types.add('object')
        elif isinstance(value, bool):
            types.add('boolean')
        elif isinstance(value, (int, float)):
            types.add('number')

    return '/'.join(sorted(types)) if types else 'unknown'


def validate_module(module_name: str, prompt_file: str, dataset_file: str) -> Dict:
    """Validate a single module's prompt against its dataset."""
    prompt_path = PROMPTS_DIR / f"{prompt_file}.md"
    dataset_path = DATASETS_DIR / f"{dataset_file}.jsonl"

    result = {
        'module': module_name,
        'prompt_file': str(prompt_path.name) if prompt_path.exists() else 'MISSING',
        'dataset_file': str(dataset_path.name) if dataset_path.exists() else 'MISSING',
        'status': 'OK',
        'issues': [],
        'prompt_variables': [],
        'dataset_fields': [],
    }

    if not prompt_path.exists():
        result['status'] = 'ERROR'
        result['issues'].append(f"Prompt file not found: {prompt_path}")
        return result

    if not dataset_path.exists():
        result['status'] = 'ERROR'
        result['issues'].append(f"Dataset file not found: {dataset_path}")
        return result

    # Extract variables and fields
    prompt_vars = extract_prompt_variables(prompt_path)
    dataset_fields, samples = extract_dataset_fields(dataset_path)

    result['prompt_variables'] = sorted(prompt_vars)
    result['dataset_fields'] = sorted(dataset_fields)

    # Check for missing fields in dataset
    missing_in_dataset = prompt_vars - dataset_fields
    if missing_in_dataset:
        result['status'] = 'WARNING'
        result['issues'].append(f"Variables in prompt but missing in dataset: {sorted(missing_in_dataset)}")

    # Check for extra fields in dataset (not necessarily an error)
    extra_in_dataset = dataset_fields - prompt_vars
    if extra_in_dataset:
        # This is informational, not an error
        result['issues'].append(f"Fields in dataset not used by prompt: {sorted(extra_in_dataset)}")

    # Check field types
    field_types = {}
    for field in dataset_fields:
        field_types[field] = check_field_types(samples, field)
    result['field_types'] = field_types

    # Check for empty/null values
    empty_fields = []
    for field in dataset_fields:
        all_empty = all(
            not sample.get('input', {}).get(field)
            for sample in samples
        )
        if all_empty:
            empty_fields.append(field)

    if empty_fields:
        result['status'] = 'WARNING'
        result['issues'].append(f"Fields with all empty/null values: {empty_fields}")

    return result


def validate_all():
    """Validate all modules."""
    print("=" * 70)
    print("DATASET VALIDATION REPORT")
    print("=" * 70)

    all_results = []

    # Validate main modules (M01-M12)
    print("\n### 12-Module Variant (M01-M12) ###\n")
    for prompt_name, dataset_name in MODULE_MAPPING.items():
        result = validate_module(prompt_name, prompt_name, dataset_name)
        all_results.append(result)
        print_result(result)

    # Validate 16-module variant (M12-M16 separate)
    print("\n### 16-Module Variant (M12-M16 separate) ###\n")
    for prompt_name, dataset_name in MODULE_MAPPING_16.items():
        result = validate_module(prompt_name, prompt_name, dataset_name)
        all_results.append(result)
        print_result(result)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    ok_count = sum(1 for r in all_results if r['status'] == 'OK')
    warn_count = sum(1 for r in all_results if r['status'] == 'WARNING')
    error_count = sum(1 for r in all_results if r['status'] == 'ERROR')

    print(f"\nTotal modules checked: {len(all_results)}")
    print(f"  ✓ OK: {ok_count}")
    print(f"  ⚠ WARNING: {warn_count}")
    print(f"  ✗ ERROR: {error_count}")

    # Show critical issues
    if warn_count > 0 or error_count > 0:
        print("\n### Issues to Address ###\n")
        for result in all_results:
            if result['status'] != 'OK' and result['issues']:
                print(f"\n{result['module']}:")
                for issue in result['issues']:
                    if 'missing in dataset' in issue.lower():
                        print(f"  ❌ {issue}")
                    else:
                        print(f"  ⚠️  {issue}")


def print_result(result: Dict):
    """Print validation result for a single module."""
    status_icon = {
        'OK': '✓',
        'WARNING': '⚠',
        'ERROR': '✗'
    }

    icon = status_icon.get(result['status'], '?')
    print(f"{icon} {result['module']}")
    print(f"  Prompt vars: {result['prompt_variables']}")
    print(f"  Dataset fields: {result['dataset_fields']}")

    if result.get('field_types'):
        types_str = ', '.join(f"{k}:{v}" for k, v in result['field_types'].items())
        print(f"  Field types: {types_str}")

    if result['issues']:
        for issue in result['issues']:
            print(f"  → {issue}")
    print()


if __name__ == "__main__":
    validate_all()
