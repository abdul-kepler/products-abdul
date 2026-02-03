#!/usr/bin/env python3
"""
Generate Full Evaluation Spreadsheet with LLM-as-Judge results.

Columns:
- Prompt Name
- Prompt Description
- ASIN
- Product Name
- Keyword
- Input Data
- Expected Output
- Actual Output
- Rubric ID
- Rubric Criterion
- LLM Judge Verdict (PASS/FAIL)
- LLM Judge Reasoning
"""

import json
import csv
from pathlib import Path
from datetime import datetime
from glob import glob

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATASETS_DIR = PROJECT_ROOT / "datasets"
RESULTS_DIR = PROJECT_ROOT / "batch_requests" / "20260112_2127" / "results"
JUDGE_DIR = SCRIPT_DIR / "judge_results"
OUTPUT_DIR = SCRIPT_DIR / "evaluation_reports"

# 10 ASINs with full pipeline coverage
FULL_COVERAGE_ASINS = [
    "B0F42MT8JX", "B000H3I2JG", "B09LCKZBTW", "B08J8GZXKZ", "B0CJ4WZXQF",
    "B077YYP739", "B0DSHWLXG6", "B0BZYCJK89", "B0BQPGJ9LQ", "B0D6YNWLTS",
]

ASIN_NAMES = {
    "B0F42MT8JX": "Ice Maker",
    "B000H3I2JG": "Revlon Eyeliner",
    "B09LCKZBTW": "Serving Tray",
    "B08J8GZXKZ": "Oven Mitt",
    "B0CJ4WZXQF": "Sink Caddy",
    "B077YYP739": "Transformers Toy",
    "B0DSHWLXG6": "Phone Holder",
    "B0BZYCJK89": "Water Bottle",
    "B0BQPGJ9LQ": "JBL Earbuds",
    "B0D6YNWLTS": "Puffer Jacket",
}

# Module configurations
MODULE_CONFIG = {
    "m01": {
        "name": "M01 - Extract Own Brand Entities",
        "description": "Extract brand name and variations from product listing",
        "dataset": "m01_extract_own_brand_entities.jsonl",
        "results": "m01_results.jsonl",
        "has_keyword": False,
        "expected_field": "brand_entities",
        "output_field": "brand_entities",
    },
    "m01a": {
        "name": "M01a - Extract Brand Variations",
        "description": "Generate typo/misspelling variations of brand name",
        "dataset": "m01a_extract_own_brand_variations.jsonl",
        "results": "m01a_results.jsonl",
        "has_keyword": False,
        "expected_field": "variations",
        "output_field": "variations",
    },
    "m01b": {
        "name": "M01b - Extract Brand Related Terms",
        "description": "Extract sub-brands, product lines, brand-owned technology",
        "dataset": "m01b_extract_brand_related_terms.jsonl",
        "results": "m01b_results.jsonl",
        "has_keyword": False,
        "expected_field": "sub_brands",
        "output_field": "sub_brands",
    },
    "m02": {
        "name": "M02 - Classify Own Brand Keywords",
        "description": "Classify if keyword contains own brand (OB)",
        "dataset": "m02_classify_own_brand_keywords.jsonl",
        "results": "m02_results.jsonl",
        "has_keyword": True,
        "expected_field": "branding_scope_1",
        "output_field": "branding_scope_1",
    },
    "m03": {
        "name": "M03 - Generate Competitor Entities",
        "description": "Generate list of competitor brands",
        "dataset": "m03_generate_competitor_entities.jsonl",
        "results": "m03_results.jsonl",
        "has_keyword": False,
        "expected_field": "competitors",
        "output_field": "competitors",
    },
    "m04": {
        "name": "M04 - Classify Competitor Brand Keywords",
        "description": "Classify if keyword contains competitor brand (CB)",
        "dataset": "m04_classify_competitor_brand_keywords.jsonl",
        "results": "m04_results.jsonl",
        "has_keyword": True,
        "expected_field": "branding_scope_2",
        "output_field": "branding_scope_2",
    },
    "m05": {
        "name": "M05 - Classify Non-Branded Keywords",
        "description": "Classify if keyword is non-branded (NB)",
        "dataset": "m05_classify_nonbranded_keywords.jsonl",
        "results": "m05_results.jsonl",
        "has_keyword": True,
        "expected_field": "branding_scope_3",
        "output_field": "branding_scope_3",
    },
    "m06": {
        "name": "M06 - Generate Product Type Taxonomy",
        "description": "Generate 3-level product type hierarchy",
        "dataset": "m06_generate_product_type_taxonomy.jsonl",
        "results": "m06_results.jsonl",
        "has_keyword": False,
        "expected_field": "taxonomy",
        "output_field": "taxonomy",
    },
    "m07": {
        "name": "M07 - Extract Product Attributes",
        "description": "Extract key product attributes from listing",
        "dataset": "m07_extract_product_attributes.jsonl",
        "results": "m07_results.jsonl",
        "has_keyword": False,
        "expected_field": "attributes",
        "output_field": "attributes",
    },
    "m08": {
        "name": "M08 - Assign Attribute Ranks",
        "description": "Rank attributes by importance",
        "dataset": "m08_assign_attribute_ranks.jsonl",
        "results": "m08_results.jsonl",
        "has_keyword": False,
        "expected_field": "ranked_attributes",
        "output_field": "attribute_table",
    },
    "m09": {
        "name": "M09 - Identify Primary Intended Use",
        "description": "Identify primary use/function of the product",
        "dataset": "m09_identify_primary_intended_use_v1.1.jsonl",
        "results": "m09_results.jsonl",
        "has_keyword": False,
        "expected_field": "primary_intended_use",
        "output_field": "primary_intended_use",
    },
    "m10": {
        "name": "M10 - Validate Primary Intended Use",
        "description": "Validate and clean primary use phrase",
        "dataset": "m10_validate_primary_intended_use_v1.1.jsonl",
        "results": "m10_results.jsonl",
        "has_keyword": False,
        "expected_field": "validated_use",
        "output_field": "validated_use",
    },
    "m11": {
        "name": "M11 - Identify Hard Constraints",
        "description": "Identify hard constraints for keyword exclusion",
        "dataset": "m11_identify_hard_constraints_v1.1.jsonl",
        "results": "m11_results.jsonl",
        "has_keyword": False,
        "expected_field": "hard_constraints",
        "output_field": "hard_constraints",
    },
    "m12": {
        "name": "M12 - Check Hard Constraint Violation",
        "description": "Check if keyword violates hard constraints (X)",
        "dataset": "m12_check_hard_constraint_v1.1.jsonl",
        "results": "m12_results.jsonl",
        "has_keyword": True,
        "expected_field": "violates_constraint",
        "output_field": "violates_constraint",
    },
    "m12b": {
        "name": "M12b - Combined Classification",
        "description": "Single-step relevance classification (R/S/C/N)",
        "dataset": "m12b_combined_classification_v1.1.jsonl",
        "results": "m12b_results.jsonl",
        "has_keyword": True,
        "expected_field": "classification",
        "output_field": "classification",
    },
    "m13": {
        "name": "M13 - Check Product Type Match",
        "description": "Check if keyword product is same type as ASIN",
        "dataset": "m13_check_product_type_v1.1.jsonl",
        "results": "m13_results.jsonl",
        "has_keyword": True,
        "expected_field": "same_type",
        "output_field": "same_product_type",
    },
    "m14": {
        "name": "M14 - Check Primary Use (Same Type)",
        "description": "Check if primary use matches - Relevant (R) or Not (N)",
        "dataset": "m14_check_primary_use_same_type_v1.1.jsonl",
        "results": "m14_results.jsonl",
        "has_keyword": True,
        "expected_field": "relevancy",
        "output_field": "classification",
    },
    "m15": {
        "name": "M15 - Check Substitute",
        "description": "Check if product is substitute (S) - different type, same use",
        "dataset": "m15_check_substitute_v1.1.jsonl",
        "results": "m15_results.jsonl",
        "has_keyword": True,
        "expected_field": "relevancy",
        "output_field": "classification",
    },
    "m16": {
        "name": "M16 - Check Complementary",
        "description": "Check if product is complementary (C) or not relevant (N)",
        "dataset": "m16_check_complementary_v1.1.jsonl",
        "results": "m16_results.jsonl",
        "has_keyword": True,
        "expected_field": "relevancy",
        "output_field": "classification",
    },
}


def load_jsonl(filepath: Path) -> list[dict]:
    """Load JSONL file."""
    if not filepath.exists():
        return []
    records = []
    with open(filepath) as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records


def get_asin_from_record(record: dict) -> str:
    """Extract ASIN from record."""
    if 'metadata' in record and 'asin' in record['metadata']:
        return record['metadata']['asin']
    if 'id' in record:
        record_id = record['id']
        if '_' in record_id:
            parts = record_id.split('_')
            for part in parts[1:]:
                if part.startswith('B0') and len(part) >= 10:
                    return part[:10]
                if '__' in part:
                    subpart = part.split('__')[0]
                    if subpart.startswith('B'):
                        return subpart
        if record_id.startswith('B'):
            return record_id
    return None


def get_keyword_from_record(record: dict) -> str:
    """Extract keyword from record."""
    if 'input' in record and 'keyword' in record.get('input', {}):
        return record['input']['keyword']
    if 'metadata' in record and 'keyword' in record.get('metadata', {}):
        return record['metadata']['keyword']
    return ""


def load_results_indexed(results_file: Path) -> dict:
    """Load results indexed by record index."""
    if not results_file.exists():
        return {}
    records = load_jsonl(results_file)
    indexed = {}
    for r in records:
        custom_id = r.get('custom_id', '')
        if '_' in custom_id:
            idx = int(custom_id.split('_')[1])
            content = r.get('response', {}).get('body', {}).get('choices', [{}])[0].get('message', {}).get('content', '{}')
            try:
                output = json.loads(content)
            except json.JSONDecodeError:
                output = {'error': 'Failed to parse'}
            indexed[idx] = output
    return indexed


def load_judge_results(module: str) -> dict:
    """Load the latest judge results for a module."""
    pattern = str(JUDGE_DIR / f"{module}_judge_*.json")
    files = sorted(glob(pattern))
    if not files:
        return {}

    # Use the latest file
    latest_file = files[-1]
    with open(latest_file) as f:
        data = json.load(f)

    # Index evaluations by sample_idx and rubric_id
    indexed = {}
    for eval_item in data.get('evaluations', []):
        sample_idx = eval_item.get('sample_idx', 0)
        rubric_id = eval_item.get('rubric_id', '')
        if sample_idx not in indexed:
            indexed[sample_idx] = {}
        indexed[sample_idx][rubric_id] = eval_item

    return indexed


def format_value(val, max_len=None):
    """Format value for spreadsheet display."""
    if val is None:
        return "null"
    if isinstance(val, bool):
        return str(val)
    if isinstance(val, (list, dict)):
        s = json.dumps(val, ensure_ascii=False)
        if max_len and len(s) > max_len:
            return s[:max_len] + "..."
        return s
    if max_len:
        return str(val)[:max_len]
    return str(val)


def format_input_full(record: dict, has_keyword: bool) -> str:
    """Create full input data summary (no truncation)."""
    input_data = record.get('input', {})
    parts = []

    if has_keyword and 'keyword' in input_data:
        parts.append(f"Keyword: {input_data['keyword']}")
    if 'brand_name' in input_data:
        parts.append(f"Brand: {input_data['brand_name']}")
    if 'title' in input_data:
        parts.append(f"Title: {input_data['title']}")
    if 'bullet_points' in input_data:
        bullets = input_data['bullet_points']
        if isinstance(bullets, str):
            parts.append(f"Bullets: {bullets[:500]}")
    if 'brand_entities' in input_data and input_data['brand_entities']:
        parts.append(f"Brand Entities: {json.dumps(input_data['brand_entities'])}")
    if 'competitors' in input_data and input_data['competitors']:
        parts.append(f"Competitors: {json.dumps(input_data['competitors'])}")
    if 'taxonomy' in input_data and input_data['taxonomy']:
        parts.append(f"Taxonomy: {json.dumps(input_data['taxonomy'])}")
    if 'validated_use' in input_data:
        parts.append(f"Validated Use: {input_data['validated_use']}")
    if 'hard_constraints' in input_data:
        parts.append(f"Hard Constraints: {json.dumps(input_data['hard_constraints'])}")
    if 'attribute_table' in input_data:
        parts.append(f"Attributes: {json.dumps(input_data['attribute_table'])}")

    return " | ".join(parts) if parts else json.dumps(input_data, ensure_ascii=False)


def calculate_match_percentage(expected, actual) -> str:
    """Calculate percentage match between expected and actual output."""
    if expected is None and actual is None:
        return "100%"
    if expected is None or actual is None:
        return "0%"

    # Normalize values
    def normalize(val):
        if val is None:
            return None
        if isinstance(val, bool):
            return val
        if isinstance(val, str):
            v = val.strip().lower()
            if v in ('null', 'none', ''):
                return None
            if v == 'true':
                return True
            if v == 'false':
                return False
            return v
        return val

    exp_norm = normalize(expected)
    act_norm = normalize(actual)

    # Exact match for simple types
    if not isinstance(expected, (list, dict)) and not isinstance(actual, (list, dict)):
        if exp_norm == act_norm:
            return "100%"
        # String similarity for strings
        if isinstance(expected, str) and isinstance(actual, str):
            exp_lower = str(expected).lower()
            act_lower = str(actual).lower()
            if exp_lower == act_lower:
                return "100%"
            # Partial match
            if exp_lower in act_lower or act_lower in exp_lower:
                shorter = min(len(exp_lower), len(act_lower))
                longer = max(len(exp_lower), len(act_lower))
                return f"{int(shorter/longer*100)}%"
        return "0%"

    # List comparison
    if isinstance(expected, list) and isinstance(actual, list):
        if not expected and not actual:
            return "100%"
        if not expected or not actual:
            return "0%"

        # Convert to sets for comparison (case-insensitive for strings)
        def to_comparable_set(lst):
            result = set()
            for item in lst:
                if isinstance(item, str):
                    result.add(item.lower())
                elif isinstance(item, dict):
                    # For dicts, use a key field or stringify
                    key = item.get('product_type') or item.get('attribute_value') or json.dumps(item, sort_keys=True)
                    result.add(str(key).lower() if isinstance(key, str) else str(key))
                else:
                    result.add(str(item))
            return result

        exp_set = to_comparable_set(expected)
        act_set = to_comparable_set(actual)

        if not exp_set:
            return "0%"

        intersection = exp_set & act_set
        union = exp_set | act_set

        # Jaccard similarity
        if union:
            return f"{int(len(intersection)/len(union)*100)}%"
        return "0%"

    # Dict comparison
    if isinstance(expected, dict) and isinstance(actual, dict):
        if not expected and not actual:
            return "100%"
        if not expected or not actual:
            return "0%"

        exp_keys = set(expected.keys())
        act_keys = set(actual.keys())
        common_keys = exp_keys & act_keys

        if not common_keys:
            return "0%"

        matches = sum(1 for k in common_keys if normalize(expected.get(k)) == normalize(actual.get(k)))
        return f"{int(matches/len(exp_keys)*100)}%"

    # Type mismatch
    return "0%"


def generate_spreadsheet():
    """Generate comprehensive spreadsheet with judge results."""

    OUTPUT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_file = OUTPUT_DIR / f"full_evaluation_spreadsheet_{timestamp}.csv"

    rows = []

    for module_id, config in MODULE_CONFIG.items():
        print(f"Processing {module_id}...")

        dataset_file = DATASETS_DIR / config['dataset']
        results_file = RESULTS_DIR / config['results']

        if not dataset_file.exists():
            print(f"  Dataset not found: {dataset_file}")
            continue

        dataset = load_jsonl(dataset_file)
        results = load_results_indexed(results_file)
        judge_results = load_judge_results(module_id)

        print(f"  Dataset: {len(dataset)}, Results: {len(results)}, Judge evals: {len(judge_results)}")

        # Process each record that has judge results
        for sample_idx, rubric_evals in judge_results.items():
            if sample_idx >= len(dataset):
                continue

            record = dataset[sample_idx]
            asin = get_asin_from_record(record)

            # Filter to our 10 ASINs
            if asin not in FULL_COVERAGE_ASINS:
                continue

            keyword = get_keyword_from_record(record) if config['has_keyword'] else ""

            # Get expected and actual
            expected_val = record.get('expected', {}).get(config['expected_field'])
            result = results.get(sample_idx, {})
            actual_val = result.get(config['output_field'])

            # Calculate match percentage once per record
            match_pct = calculate_match_percentage(expected_val, actual_val)

            # Create row for each rubric evaluation
            for rubric_id, eval_item in rubric_evals.items():
                reasoning = eval_item.get('reasoning', '')
                # Clean up reasoning - extract just the key part
                if '**Reasoning:**' in reasoning:
                    reasoning = reasoning.split('**Reasoning:**')[1]
                if '**Verdict:**' in reasoning:
                    reasoning = reasoning.split('**Verdict:**')[0]
                reasoning = reasoning.strip()

                row = {
                    'Prompt Name': config['name'],
                    'Prompt Description': config['description'],
                    'ASIN': asin,
                    'Product Name': ASIN_NAMES.get(asin, ''),
                    'Keyword': keyword,
                    'Input Data': format_input_full(record, config['has_keyword']),
                    'Expected Output': format_value(expected_val),
                    'Actual Output': format_value(actual_val),
                    'Expected vs Actual Match': match_pct,
                    'Rubric ID': rubric_id,
                    'Rubric Criterion': eval_item.get('criterion', ''),
                    'LLM Judge Verdict': eval_item.get('verdict', ''),
                    'LLM Judge Reasoning': reasoning,
                }
                rows.append(row)

        print(f"  Added {sum(1 for r in rows if r['Prompt Name'] == config['name'])} rows")

    # Write CSV
    if rows:
        fieldnames = [
            'Prompt Name', 'Prompt Description', 'ASIN', 'Product Name', 'Keyword',
            'Input Data', 'Expected Output', 'Actual Output', 'Expected vs Actual Match',
            'Rubric ID', 'Rubric Criterion', 'LLM Judge Verdict', 'LLM Judge Reasoning'
        ]

        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        print(f"\nSpreadsheet saved to: {csv_file}")
        print(f"Total rows: {len(rows)}")

        # Summary
        pass_count = sum(1 for r in rows if r['LLM Judge Verdict'] == 'PASS')
        fail_count = sum(1 for r in rows if r['LLM Judge Verdict'] == 'FAIL')
        total = pass_count + fail_count
        print(f"PASS: {pass_count}, FAIL: {fail_count}")
        if total > 0:
            print(f"Pass Rate: {pass_count/total*100:.1f}%")

    return csv_file


if __name__ == "__main__":
    generate_spreadsheet()
