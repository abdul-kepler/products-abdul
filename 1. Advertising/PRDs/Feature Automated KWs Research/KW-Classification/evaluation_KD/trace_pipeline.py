#!/usr/bin/env python3
"""
Pipeline Trace - Trace ASINs through M01-M16 modules
Shows data flow and classification results for each ASIN and its keywords
"""

import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
DATASETS_DIR = PROJECT_ROOT / "datasets"
RESULTS_DIR = PROJECT_ROOT / "experiment_results"

# The 10 ASINs with full pipeline coverage
FULL_COVERAGE_ASINS = [
    "B0F42MT8JX",  # Ice Maker
    "B000H3I2JG",  # Revlon Eyeliner
    "B09LCKZBTW",  # Serving Tray
    "B08J8GZXKZ",  # Oven Mitt
    "B0CJ4WZXQF",  # Sink Caddy
    "B077YYP739",  # Transformers Toy
    "B0DSHWLXG6",  # Phone Holder
    "B0BZYCJK89",  # Owala Water Bottle
    "B0BQPGJ9LQ",  # JBL Earbuds
    "B0D6YNWLTS",  # Puffer Jacket
]

# Module files mapping
MODULES = {
    # Stage 1: Brand Extraction (per ASIN)
    "M01": {"dataset": "m01_extract_own_brand_entities.jsonl", "desc": "Extract own brand entities"},
    "M01a": {"dataset": "m01a_extract_own_brand_variations.jsonl", "desc": "Extract brand variations"},
    "M01b": {"dataset": "m01b_extract_brand_related_terms.jsonl", "desc": "Extract brand-related terms"},
    "M03": {"dataset": "m03_generate_competitor_entities.jsonl", "desc": "Generate competitor entities"},

    # Stage 2: Brand Classification (per keyword)
    "M02": {"dataset": "m02_classify_own_brand_keywords.jsonl", "desc": "Classify own brand keywords"},
    "M04": {"dataset": "m04_classify_competitor_brand_keywords.jsonl", "desc": "Classify competitor keywords"},
    "M05": {"dataset": "m05_classify_nonbranded_keywords.jsonl", "desc": "Classify non-branded keywords"},

    # Stage 3: Product Analysis (per ASIN)
    "M06": {"dataset": "m06_generate_product_type_taxonomy.jsonl", "desc": "Generate product taxonomy"},
    "M07": {"dataset": "m07_extract_product_attributes.jsonl", "desc": "Extract product attributes"},
    "M08": {"dataset": "m08_assign_attribute_ranks.jsonl", "desc": "Assign attribute ranks"},
    "M09": {"dataset": "m09_identify_primary_intended_use_v1.1.jsonl", "desc": "Identify primary use"},
    "M10": {"dataset": "m10_validate_primary_intended_use_v1.1.jsonl", "desc": "Validate primary use"},
    "M11": {"dataset": "m11_identify_hard_constraints_v1.1.jsonl", "desc": "Identify hard constraints"},

    # Stage 4: Relevance Classification (per keyword)
    "M12": {"dataset": "m12_check_hard_constraint_v1.1.jsonl", "desc": "Check hard constraints"},
    "M12b": {"dataset": "m12b_combined_classification_v1.1.jsonl", "desc": "Combined classification"},
    "M13": {"dataset": "m13_check_product_type_v1.1.jsonl", "desc": "Check product type match"},
    "M14": {"dataset": "m14_check_primary_use_same_type_v1.1.jsonl", "desc": "Check primary use (same type)"},
    "M15": {"dataset": "m15_check_substitute_v1.1.jsonl", "desc": "Check substitute"},
    "M16": {"dataset": "m16_check_complementary_v1.1.jsonl", "desc": "Check complementary"},
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
    """Extract ASIN from various record formats."""
    # Try metadata.asin first (most reliable)
    if 'metadata' in record and 'asin' in record['metadata']:
        return record['metadata']['asin']

    # Try direct id field
    if 'id' in record:
        record_id = record['id']
        # Handle prefixed IDs like "M2_B0BQPGJ9LQ__keyword" or "M6_B0BQPGJ9LQ"
        if '_' in record_id:
            parts = record_id.split('_')
            # Skip module prefix (M2, M6, etc.)
            for part in parts[1:]:
                # ASIN pattern: starts with B0 and is 10 chars
                if part.startswith('B0') and len(part) >= 10:
                    return part[:10]
                # Handle "__" separator
                if '__' in part:
                    subpart = part.split('__')[0]
                    if subpart.startswith('B0') or subpart.startswith('B'):
                        return subpart
        # Plain ASIN as id
        if record_id.startswith('B'):
            return record_id

    # Try input.asin
    if 'input' in record and 'asin' in record.get('input', {}):
        return record['input']['asin']
    return None


def get_keyword_from_record(record: dict) -> str:
    """Extract keyword from record if present."""
    # Try input.keyword first
    if 'input' in record and 'keyword' in record.get('input', {}):
        return record['input']['keyword']
    # Try metadata.keyword
    if 'metadata' in record and 'keyword' in record.get('metadata', {}):
        return record['metadata']['keyword']
    return None


def load_module_data(module: str) -> dict:
    """Load dataset for a module and index by ASIN."""
    config = MODULES.get(module)
    if not config:
        return {}

    filepath = DATASETS_DIR / config['dataset']
    records = load_jsonl(filepath)

    # Index by ASIN, but store list of records (for multiple keywords per ASIN)
    by_asin = defaultdict(list)
    for r in records:
        asin = get_asin_from_record(r)
        if asin:
            by_asin[asin].append(r)

    return dict(by_asin)


def get_classification_from_expected(expected: dict, module: str = None) -> str:
    """Extract classification from expected field based on actual dataset format."""
    if not expected:
        return "?"

    # M02: branding_scope_1 = OB or None
    if 'branding_scope_1' in expected:
        val = expected['branding_scope_1']
        return "OB" if val == "OB" else "-"

    # M04: branding_scope_2 = CB or None
    if 'branding_scope_2' in expected:
        val = expected['branding_scope_2']
        return "CB" if val == "CB" else "-"

    # M05: branding_scope_3 = NB or None
    if 'branding_scope_3' in expected:
        val = expected['branding_scope_3']
        return "NB" if val == "NB" else "-"

    # M13: same_type = True/False
    if 'same_type' in expected:
        val = expected['same_type']
        if val is True or val == "True":
            return "Same"
        elif val is False or val == "False":
            return "Diff"
        return "?"

    # M14, M15, M16: relevancy = R/S/C/N/Null
    if 'relevancy' in expected:
        val = expected['relevancy']
        if val in ["R", "S", "C", "N"]:
            return val
        elif val == "Null" or val is None:
            return "-"
        return str(val)

    return "?"


def trace_asin(asin: str) -> dict:
    """Trace an ASIN through all modules."""
    trace = {
        "asin": asin,
        "stages": {},
        "keywords": defaultdict(dict),
    }

    # Stage 1: Brand Extraction
    for module in ["M01", "M01a", "M01b", "M03"]:
        data = load_module_data(module)
        if asin in data:
            records = data[asin]
            trace["stages"][module] = {
                "found": True,
                "records": len(records),
                "sample": records[0].get("expected", {}) if records else {},
            }
        else:
            trace["stages"][module] = {"found": False}

    # Stage 2 & 4: Keyword-based modules
    keyword_modules = ["M02", "M04", "M05", "M12", "M12b", "M13", "M14", "M15", "M16"]

    for module in keyword_modules:
        data = load_module_data(module)
        if asin in data:
            for record in data[asin]:
                keyword = get_keyword_from_record(record)
                if keyword:
                    classification = get_classification_from_expected(record.get("expected", {}))
                    trace["keywords"][keyword][module] = classification

    # Stage 3: Product Analysis
    for module in ["M06", "M07", "M08", "M09", "M10", "M11"]:
        data = load_module_data(module)
        if asin in data:
            records = data[asin]
            trace["stages"][module] = {
                "found": True,
                "records": len(records),
            }
            # Extract key outputs
            if records:
                expected = records[0].get("expected", {})
                if module == "M06" and "taxonomy" in expected:
                    trace["stages"][module]["taxonomy"] = expected["taxonomy"][:3] if expected["taxonomy"] else []
                elif module == "M09" and "primary_intended_use" in expected:
                    trace["stages"][module]["primary_use"] = expected["primary_intended_use"]
                elif module == "M11" and "hard_constraints" in expected:
                    trace["stages"][module]["constraints"] = expected.get("hard_constraints", [])
        else:
            trace["stages"][module] = {"found": False}

    return trace


def summarize_keywords(trace: dict) -> dict:
    """Summarize keyword classifications."""
    summary = {
        "OB": 0,
        "CB": 0,
        "NB": 0,
        "R": 0,
        "S": 0,
        "C": 0,
        "N": 0,
        "X": 0,
        "total": 0,
    }

    for keyword, modules in trace["keywords"].items():
        summary["total"] += 1

        # Determine final classification based on pipeline logic
        if modules.get("M02") == "OB":
            summary["OB"] += 1
        elif modules.get("M04") == "CB":
            summary["CB"] += 1
        elif modules.get("M05") == "NB":
            # NB keywords continue to relevance classification
            # Check M13 (same type) first, then M14/M15/M16
            if modules.get("M14") == "R":
                summary["R"] += 1
            elif modules.get("M15") == "S":
                summary["S"] += 1
            elif modules.get("M16") == "C":
                summary["C"] += 1
            elif modules.get("M14") == "N" or modules.get("M16") == "N":
                summary["N"] += 1
            else:
                summary["NB"] += 1  # No relevance data yet
        else:
            # Keywords only in relevance pipeline (no brand classification in dataset)
            if modules.get("M14") == "R":
                summary["R"] += 1
            elif modules.get("M15") == "S":
                summary["S"] += 1
            elif modules.get("M16") == "C":
                summary["C"] += 1
            elif modules.get("M14") == "N" or modules.get("M16") == "N":
                summary["N"] += 1

    return summary


def generate_report():
    """Generate pipeline trace report."""
    print("=" * 80)
    print("PIPELINE TRACE REPORT - M01-M16")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    all_traces = []

    for asin in FULL_COVERAGE_ASINS:
        print(f"\n{'='*80}")
        print(f"ASIN: {asin}")
        print("=" * 80)

        trace = trace_asin(asin)
        all_traces.append(trace)

        # Stage 1: Brand Extraction
        print("\n📦 STAGE 1: Brand Extraction")
        for module in ["M01", "M01a", "M01b", "M03"]:
            stage_data = trace["stages"].get(module, {})
            status = "✓" if stage_data.get("found") else "❌"
            print(f"  {module}: {status}")
            if module == "M01" and stage_data.get("found"):
                brands = stage_data.get("sample", {}).get("brand_entities", [])[:5]
                if brands:
                    print(f"       Brands: {', '.join(str(b) for b in brands)}...")

        # Stage 3: Product Analysis
        print("\n🔍 STAGE 3: Product Analysis")
        for module in ["M06", "M07", "M08", "M09", "M10", "M11"]:
            stage_data = trace["stages"].get(module, {})
            status = "✓" if stage_data.get("found") else "❌"
            print(f"  {module}: {status}")
            if module == "M06" and stage_data.get("taxonomy"):
                types = [t.get("product_type", "") for t in stage_data["taxonomy"]]
                print(f"       Taxonomy: {' > '.join(types)}")
            elif module == "M09" and stage_data.get("primary_use"):
                print(f"       Primary Use: {stage_data['primary_use']}")
            elif module == "M11" and stage_data.get("constraints"):
                print(f"       Constraints: {stage_data['constraints'][:3]}")

        # Keyword Summary
        summary = summarize_keywords(trace)
        print(f"\n🏷️  KEYWORD CLASSIFICATIONS ({summary['total']} keywords)")
        print(f"  OB: {summary['OB']:3d}  |  CB: {summary['CB']:3d}  |  NB: {summary['NB']:3d}")
        print(f"  R:  {summary['R']:3d}  |  S:  {summary['S']:3d}  |  C:  {summary['C']:3d}  |  N: {summary['N']:3d}")

        # Sample keywords with full trace
        print("\n📋 SAMPLE KEYWORD TRACES (first 5):")
        for i, (keyword, modules) in enumerate(list(trace["keywords"].items())[:5]):
            print(f"\n  {i+1}. \"{keyword[:50]}\"")
            # Show classification path
            path = []
            if "M02" in modules:
                path.append(f"M02:{modules['M02']}")
            if "M04" in modules:
                path.append(f"M04:{modules['M04']}")
            if "M05" in modules:
                path.append(f"M05:{modules['M05']}")
            if "M13" in modules:
                path.append(f"M13:{modules['M13']}")
            if "M14" in modules:
                path.append(f"M14:{modules['M14']}")
            if "M15" in modules:
                path.append(f"M15:{modules['M15']}")
            if "M16" in modules:
                path.append(f"M16:{modules['M16']}")
            print(f"     Path: {' → '.join(path)}")

    # Overall Summary
    print("\n" + "=" * 80)
    print("OVERALL SUMMARY")
    print("=" * 80)

    total_summary = {"OB": 0, "CB": 0, "NB": 0, "R": 0, "S": 0, "C": 0, "N": 0, "total": 0}

    print("\n| ASIN | Product | OB | CB | R | S | C | N | Total |")
    print("|------|---------|----|----|---|---|---|---|-------|")

    product_names = {
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

    for trace in all_traces:
        asin = trace["asin"]
        summary = summarize_keywords(trace)
        print(f"| {asin} | {product_names.get(asin, '?')[:13]} | {summary['OB']:2d} | {summary['CB']:2d} | {summary['R']:2d} | {summary['S']:2d} | {summary['C']:2d} | {summary['N']:2d} | {summary['total']:3d} |")

        for key in total_summary:
            total_summary[key] += summary.get(key, 0)

    print(f"| **TOTAL** | | **{total_summary['OB']}** | **{total_summary['CB']}** | **{total_summary['R']}** | **{total_summary['S']}** | **{total_summary['C']}** | **{total_summary['N']}** | **{total_summary['total']}** |")

    return all_traces


if __name__ == "__main__":
    traces = generate_report()
