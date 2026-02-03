#!/usr/bin/env python3
"""
Generate Evaluation Spreadsheet - Comprehensive evaluation data for all modules.

Columns:
- Prompt Name
- Prompt Description
- ASIN
- Product Name
- Keyword (if applicable)
- Input Data (key fields)
- Expected Output
- Actual Output
- Match (Pass/Fail)
- Reasoning (from model output)
"""

import json
import csv
from pathlib import Path
from datetime import datetime

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATASETS_DIR = PROJECT_ROOT / "datasets"
RESULTS_DIR = PROJECT_ROOT / "batch_requests" / "20260112_2127" / "results"
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

# Module configurations with descriptions and rubrics
MODULE_CONFIG = {
    "m01": {
        "name": "M01 - Extract Own Brand Entities",
        "description": "Extract brand name and variations from product listing",
        "dataset": "m01_extract_own_brand_entities.jsonl",
        "results": "m01_results.jsonl",
        "has_keyword": False,
        "expected_field": "brand_entities",
        "output_field": "brand_entities",
        "rubric": "Brand extracted correctly, no hallucination, no product words, Amazon test applied, no duplicates",
    },
    "m01a": {
        "name": "M01a - Extract Brand Variations",
        "description": "Generate typo/misspelling variations of brand name",
        "dataset": "m01a_extract_own_brand_variations.jsonl",
        "results": "m01a_results.jsonl",
        "has_keyword": False,
        "expected_field": "variations",
        "output_field": "variations",
        "rubric": "8-12 variations, first is canonical, no unrelated terms",
    },
    "m01b": {
        "name": "M01b - Extract Brand Related Terms",
        "description": "Extract sub-brands, product lines, and brand-owned technology",
        "dataset": "m01b_extract_brand_related_terms.jsonl",
        "results": "m01b_results.jsonl",
        "has_keyword": False,
        "expected_field": "sub_brands",
        "output_field": "sub_brands",
        "rubric": "Sub-brands found, no universal standards, manufacturer null when same as brand",
    },
    "m02": {
        "name": "M02 - Classify Own Brand Keywords",
        "description": "Classify if keyword contains own brand (OB) or not",
        "dataset": "m02_classify_own_brand_keywords.jsonl",
        "results": "m02_results.jsonl",
        "has_keyword": True,
        "expected_field": "branding_scope_1",
        "output_field": "branding_scope_1",
        "rubric": "OB when keyword contains brand from variations, null otherwise. Case insensitive, word boundary respected.",
    },
    "m03": {
        "name": "M03 - Generate Competitor Entities",
        "description": "Generate list of competitor brands for the product category",
        "dataset": "m03_generate_competitor_entities.jsonl",
        "results": "m03_results.jsonl",
        "has_keyword": False,
        "expected_field": "competitors",
        "output_field": "competitors",
        "rubric": "5-10 relevant competitors, no hallucinated brands, no own brand included",
    },
    "m04": {
        "name": "M04 - Classify Competitor Brand Keywords",
        "description": "Classify if keyword contains competitor brand (CB) or not",
        "dataset": "m04_classify_competitor_brand_keywords.jsonl",
        "results": "m04_results.jsonl",
        "has_keyword": True,
        "expected_field": "branding_scope_2",
        "output_field": "branding_scope_2",
        "rubric": "CB when competitor brand in keyword, null otherwise. Own brand excluded, word boundary respected.",
    },
    "m05": {
        "name": "M05 - Classify Non-Branded Keywords",
        "description": "Classify if keyword is non-branded (NB) - no brand references",
        "dataset": "m05_classify_nonbranded_keywords.jsonl",
        "results": "m05_results.jsonl",
        "has_keyword": True,
        "expected_field": "branding_scope_3",
        "output_field": "branding_scope_3",
        "rubric": "NB when keyword has zero brand references, null otherwise. Hidden brands and typos caught.",
    },
    "m06": {
        "name": "M06 - Generate Product Type Taxonomy",
        "description": "Generate 3-level product type hierarchy (Category > Subcategory > Product Type)",
        "dataset": "m06_generate_product_type_taxonomy.jsonl",
        "results": "m06_results.jsonl",
        "has_keyword": False,
        "expected_field": "taxonomy",
        "output_field": "taxonomy",
        "rubric": "Three-level hierarchy, product type focused, no brands in taxonomy, appropriate specificity",
    },
    "m07": {
        "name": "M07 - Extract Product Attributes",
        "description": "Extract key product attributes from listing (size, color, material, etc.)",
        "dataset": "m07_extract_product_attributes.jsonl",
        "results": "m07_results.jsonl",
        "has_keyword": False,
        "expected_field": "attributes",
        "output_field": "attributes",
        "rubric": "Attributes from listing, key attributes captured, correct format, no duplicates",
    },
    "m08": {
        "name": "M08 - Assign Attribute Ranks",
        "description": "Rank attributes by importance for search relevance",
        "dataset": "m08_assign_attribute_ranks.jsonl",
        "results": "m08_results.jsonl",
        "has_keyword": False,
        "expected_field": "ranked_attributes",
        "output_field": "attribute_table",
        "rubric": "Logical ranking, primary attributes ranked highest, consistent ordering",
    },
    "m09": {
        "name": "M09 - Identify Primary Intended Use",
        "description": "Identify the primary intended use/function of the product",
        "dataset": "m09_identify_primary_intended_use_v1.1.jsonl",
        "results": "m09_results.jsonl",
        "has_keyword": False,
        "expected_field": "primary_intended_use",
        "output_field": "primary_intended_use",
        "rubric": "Describes what product DOES not what it IS, 3-6 words, no adjectives/features",
    },
    "m10": {
        "name": "M10 - Validate Primary Intended Use",
        "description": "Validate and clean the primary intended use phrase",
        "dataset": "m10_validate_primary_intended_use_v1.1.jsonl",
        "results": "m10_results.jsonl",
        "has_keyword": False,
        "expected_field": "validated_use",
        "output_field": "validated_use",
        "rubric": "Output clean, word count 3-6, describes function not features",
    },
    "m11": {
        "name": "M11 - Identify Hard Constraints",
        "description": "Identify hard constraints that would exclude keywords (size, compatibility, etc.)",
        "dataset": "m11_identify_hard_constraints_v1.1.jsonl",
        "results": "m11_results.jsonl",
        "has_keyword": False,
        "expected_field": "hard_constraints",
        "output_field": "hard_constraints",
        "rubric": "Relevant constraints identified, no soft preferences, constraint-specific",
    },
    "m13": {
        "name": "M13 - Check Product Type Match",
        "description": "Check if keyword product is same type as ASIN product",
        "dataset": "m13_check_product_type_v1.1.jsonl",
        "results": "m13_results.jsonl",
        "has_keyword": True,
        "expected_field": "same_type",
        "output_field": "same_product_type",
        "rubric": "True if same product type, False if different. Based on taxonomy comparison.",
    },
    "m14": {
        "name": "M14 - Check Primary Use (Same Type)",
        "description": "For same-type products, check if primary use matches (R) or not (N)",
        "dataset": "m14_check_primary_use_same_type_v1.1.jsonl",
        "results": "m14_results.jsonl",
        "has_keyword": True,
        "expected_field": "relevancy",
        "output_field": "classification",
        "rubric": "R when primary use matches, N when different. Same type products only.",
    },
    "m15": {
        "name": "M15 - Check Substitute",
        "description": "For different-type products, check if substitute (S) - different type, same use",
        "dataset": "m15_check_substitute_v1.1.jsonl",
        "results": "m15_results.jsonl",
        "has_keyword": True,
        "expected_field": "relevancy",
        "output_field": "classification",
        "rubric": "S when product can substitute (different type, same use), Null otherwise.",
    },
    "m16": {
        "name": "M16 - Check Complementary",
        "description": "For non-substitutes, check if complementary (C) - used together with ASIN",
        "dataset": "m16_check_complementary_v1.1.jsonl",
        "results": "m16_results.jsonl",
        "has_keyword": True,
        "expected_field": "relevancy",
        "output_field": "classification",
        "rubric": "C when products used together, N when no relationship.",
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
                output = {'error': 'Failed to parse', 'raw': content[:500]}
            indexed[idx] = output
    return indexed


def normalize_value(val):
    """Normalize value for comparison."""
    if val is None:
        return None
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        val = val.strip().lower()
        if val in ('null', 'none', ''):
            return None
        if val == 'true':
            return True
        if val == 'false':
            return False
        return val
    return val


def format_value(val, max_len=100):
    """Format value for spreadsheet display."""
    if val is None:
        return "null"
    if isinstance(val, bool):
        return str(val)
    if isinstance(val, (list, dict)):
        s = json.dumps(val, ensure_ascii=False)
        if len(s) > max_len:
            return s[:max_len] + "..."
        return s
    return str(val)[:max_len]


def format_input_data(record: dict, has_keyword: bool) -> str:
    """Format input data for display."""
    input_data = record.get('input', {})
    parts = []

    # Key fields to include
    if has_keyword and 'keyword' in input_data:
        parts.append(f"keyword: {input_data['keyword']}")
    if 'brand_name' in input_data:
        parts.append(f"brand: {input_data['brand_name']}")
    if 'title' in input_data:
        title = input_data['title'][:80] + "..." if len(input_data.get('title', '')) > 80 else input_data.get('title', '')
        parts.append(f"title: {title}")
    if 'brand_entities' in input_data and input_data['brand_entities']:
        entities = input_data['brand_entities'][:5]
        parts.append(f"brand_entities: {entities}")
    if 'competitors' in input_data and input_data['competitors']:
        comps = input_data['competitors'][:5] if isinstance(input_data['competitors'], list) else input_data['competitors']
        parts.append(f"competitors: {comps}")
    if 'taxonomy' in input_data:
        tax = input_data['taxonomy']
        if isinstance(tax, list) and tax:
            types = [t.get('product_type', '') for t in tax[:3]]
            parts.append(f"taxonomy: {' > '.join(types)}")
    if 'validated_use' in input_data:
        parts.append(f"validated_use: {input_data['validated_use']}")

    return " | ".join(parts) if parts else json.dumps(input_data, ensure_ascii=False)[:200]


def generate_spreadsheet(max_per_module: int = 100):
    """Generate comprehensive evaluation spreadsheet."""

    OUTPUT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_file = OUTPUT_DIR / f"evaluation_spreadsheet_{timestamp}.csv"

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

        count = 0
        for idx, record in enumerate(dataset):
            if count >= max_per_module:
                break

            asin = get_asin_from_record(record)
            if asin not in FULL_COVERAGE_ASINS:
                continue

            keyword = get_keyword_from_record(record) if config['has_keyword'] else ""

            # Get expected and actual
            expected_val = record.get('expected', {}).get(config['expected_field'])
            result = results.get(idx, {})
            actual_val = result.get(config['output_field'])

            # Get reasoning if available
            reasoning = result.get('reasoning', '')
            if not reasoning and 'keyword_product_type' in result:
                reasoning = f"keyword_type: {result.get('keyword_product_type', '')}"

            # Determine match
            expected_norm = normalize_value(expected_val)
            actual_norm = normalize_value(actual_val)
            match = "PASS" if expected_norm == actual_norm else "FAIL"

            row = {
                'Prompt Name': config['name'],
                'Prompt Description': config['description'],
                'ASIN': asin,
                'Product Name': ASIN_NAMES.get(asin, ''),
                'Keyword': keyword,
                'Input Data': format_input_data(record, config['has_keyword']),
                'Expected Output': format_value(expected_val),
                'Actual Output': format_value(actual_val),
                'Match': match,
                'Rubric': config['rubric'],
                'Reasoning': reasoning[:500] if reasoning else '',
            }
            rows.append(row)
            count += 1

        print(f"  Added {count} rows")

    # Write CSV
    if rows:
        fieldnames = ['Prompt Name', 'Prompt Description', 'ASIN', 'Product Name', 'Keyword',
                      'Input Data', 'Expected Output', 'Actual Output', 'Match', 'Rubric', 'Reasoning']

        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        print(f"\nSpreadsheet saved to: {csv_file}")
        print(f"Total rows: {len(rows)}")

        # Summary
        pass_count = sum(1 for r in rows if r['Match'] == 'PASS')
        fail_count = sum(1 for r in rows if r['Match'] == 'FAIL')
        print(f"PASS: {pass_count}, FAIL: {fail_count}, Accuracy: {pass_count/(pass_count+fail_count)*100:.1f}%")

    return csv_file


if __name__ == "__main__":
    generate_spreadsheet(max_per_module=100)
