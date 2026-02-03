#!/usr/bin/env python3
"""
Generate Enhanced Error Analysis CSVs

Adds additional columns for deeper error analysis:
- Prompt_Instruction: Relevant instruction from the prompt
- Hypothesis_Discrepancy: Why the error occurred
- Hypothesis_Improvement: What to improve in the prompt
"""

import csv
import json
from pathlib import Path
from typing import Dict, List, Optional


# Error pattern analysis for each module
ERROR_PATTERNS = {
    "m04": {
        # Prompt instruction reference
        "prompt_file": "prompts/modules/m04_classify_competitor_brand_keywords.md",
        "key_instructions": [
            "If keyword contains ANY term from `own_brand.entities` → IMMEDIATELY return null",
            "Check competitor_entities list for brand matches",
            "Character-by-character substring verification"
        ],
        # Pattern detectors: (condition function, analysis dict)
        "patterns": {
            "hallucination_own_brand": {
                "detect": lambda e: "matches own brand" in e.get("Reasoning", "").lower() and e.get("Error_Type") == "FN",
                "instruction": "Only EXACT substring matches count - character-by-character verification required",
                "hypothesis": "Model hallucinates own brand matches in keywords that don't contain it",
                "improvement": "Add explicit anti-hallucination examples showing failed matches (e.g., 'amazon' does NOT contain 'JBL')"
            },
            "known_brand_not_in_list": {
                "detect": lambda e: ("not in competitor_entities" in e.get("Reasoning", "").lower() or
                                     "not in the competitor_entities list" in e.get("Reasoning", "").lower()) and e.get("Error_Type") == "FN",
                "instruction": "competitor_entities list is exhaustive for this product",
                "hypothesis": "Model recognizes brand but prompt says to only use provided list - model should use common knowledge for obvious brands",
                "improvement": "Add Step 5: Known Brand Check - detect recognizable brands beyond provided list (like M04b has)"
            },
            "own_brand_accessory": {
                "detect": lambda e: ("owala" in e.get("Keyword", "").lower() and
                                    ("boot" in e.get("Keyword", "").lower() or "lid" in e.get("Keyword", "").lower() or
                                     "accessories" in e.get("Keyword", "").lower())),
                "instruction": "Check if keyword contains own_brand entities",
                "hypothesis": "Keyword contains own brand but is for accessories - model sees own brand and returns null instead of checking if CB is also present",
                "improvement": "Clarify that own brand + accessory keywords are NOT competitor brand (correct behavior - these are OB or NB)"
            }
        }
    },
    "m04b": {
        "prompt_file": "prompts/modules/m04b_classify_competitor_brand_keywords.md",
        "key_instructions": [
            "Step 1: Own Brand Check - if EXACT match → SKIP (return null)",
            "Step 5: Known Brand Check (Beyond Provided List) - recognizable brands not in list",
            "Character/IP franchises (Disney, Marvel, Batman) should be recognized"
        ],
        "patterns": {
            "own_brand_as_competitor": {
                "detect": lambda e: e.get("Error_Type") == "FP" and e.get("Expected") == "null",
                "instruction": "Step 1: Check if keyword contains seller's own brand → SKIP and return null",
                "hypothesis": "Model marks own brand keywords as CB - Step 5 Known Brand Check overrides Step 1 Own Brand Check",
                "improvement": "Emphasize Step 1 priority: ALWAYS check own brand FIRST, return null immediately if match. Known Brand Check only for NON-own-brand keywords"
            },
            "transformers_brand_confusion": {
                "detect": lambda e: e.get("Brand_Name") == "Transformers" and "transformer" in e.get("Keyword", "").lower(),
                "instruction": "If own brand is in keyword → return null (not competitor)",
                "hypothesis": "Transformers is both a brand AND a generic product descriptor. Model sees 'transformer toy' as known IP and marks CB",
                "improvement": "Add explicit example: If own_brand='Transformers', then 'transformer toy' is OB not CB. Product line names within own brand are NOT competitors"
            },
            "known_brand_fn": {
                "detect": lambda e: e.get("Error_Type") == "FN" and e.get("Expected") == "CB",
                "instruction": "Step 5: Check for recognizable brands beyond provided list",
                "hypothesis": "Model fails to detect competitor brand - either typo, lesser-known brand, or Amazon-owned brand not in list",
                "improvement": "Expand known brand detection examples, add Amazon-owned brands (Alexa, Echo), add common brand typo patterns"
            }
        }
    },
    "m02b": {
        "prompt_file": "prompts/modules/m02b_classify_own_brand_keywords.md",
        "key_instructions": [
            "Character-by-character verification required",
            "Check variations_own and related_terms_own lists",
            "Only EXACT substring matches count"
        ],
        "patterns": {
            "other_brand_as_own": {
                "detect": lambda e: e.get("Error_Type") == "FP" and e.get("Expected") == "null",
                "instruction": "Only match against provided own_brand.entities, variations, and related_terms",
                "hypothesis": "Model recognizes brand in keyword but it's NOT seller's own brand - it's a different brand (competitor)",
                "improvement": "Add explicit negative examples: 'skullcandy headphones' for JBL seller is NOT OB because Skullcandy is a different brand"
            },
            "misspelling_not_detected": {
                "detect": lambda e: e.get("Error_Type") == "FN" and e.get("Expected") == "OB",
                "instruction": "Check variations_own list which includes common misspellings",
                "hypothesis": "Misspelling not in variations list (e.g., 'cisiky' for 'Cisily', 'Pineer' for 'Pioneer')",
                "improvement": "Generate common misspelling patterns algorithmically or expand variations list with phonetic/typo variants"
            }
        }
    },
    "m15": {
        "prompt_file": "prompts/modules/m15_substitute_check_v1.1.md",
        "key_instructions": [
            "Same core function - Both solve the same fundamental problem",
            "60% Rule: If primary use overlap ≥60%, classify as S",
            "NOT substitute: Accessory relationship - One supports/enhances the other"
        ],
        "patterns": {
            "accessory_as_substitute": {
                "detect": lambda e: e.get("Error_Type") == "FP" and ("boot" in e.get("Keyword", "").lower() or
                                                                      "lid" in e.get("Keyword", "").lower() or
                                                                      "accessories" in e.get("Keyword", "").lower() or
                                                                      "scoop" in e.get("Keyword", "").lower() or
                                                                      "parts" in e.get("Keyword", "").lower()),
                "instruction": "NOT substitute when: Accessory relationship - One supports/enhances the other",
                "hypothesis": "Model incorrectly treats accessories as substitutes because they're 'related' to the product",
                "improvement": "Add more explicit accessory vs substitute examples. Emphasize: 'water bottle boot' is accessory FOR water bottle, not substitute"
            },
            "same_category_as_substitute": {
                "detect": lambda e: e.get("Error_Type") == "FP" and "same" in e.get("Reasoning", "").lower() and "function" in e.get("Reasoning", "").lower(),
                "instruction": "Must serve IDENTICAL primary purpose to be substitute",
                "hypothesis": "Model interprets 'related function' as 'same function' - e.g., ice scoop and ice maker both involve ice but serve different functions",
                "improvement": "Clarify: Products in same category are NOT automatically substitutes. Add: 'Would buyer accept one INSTEAD of the other for their exact need?'"
            },
            "different_product_type_substitute_fn": {
                "detect": lambda e: e.get("Error_Type") == "FN" and e.get("Expected") == "S",
                "instruction": "Substitute relationship exists across product types when solving same problem",
                "hypothesis": "Model rejected substitute because products look different or are in different categories",
                "improvement": "Add cross-category substitute examples: 'wireless car charger' can substitute 'phone holder with charging' for the charging function"
            }
        }
    },
    "m13": {
        "prompt_file": "prompts/modules/m13_product_type_check_v1.1.md",
        "key_instructions": [
            "Modifiers describe attributes, not different products",
            "Gray Area: If unsure, use 4 decision questions",
            "Same type if core function unchanged"
        ],
        "patterns": {
            "modifier_as_different_type": {
                "detect": lambda e: e.get("Error_Type") == "FN" and e.get("Expected") == "True",
                "instruction": "Modifiers (color, size, brand, feature) don't change product type",
                "hypothesis": "Model treats modifier as creating different product type (e.g., 'pink igloo ice maker' vs 'ice maker')",
                "improvement": "Add examples: 'pink X' is same type as 'X', 'wireless X' is same type as 'X' unless wireless fundamentally changes function"
            },
            "accessory_same_type_fp": {
                "detect": lambda e: e.get("Error_Type") == "FP" and e.get("Output") == "True",
                "instruction": "Product + accessory are DIFFERENT product types",
                "hypothesis": "Model treats main product and its accessory as same type because they're used together",
                "improvement": "Add explicit: 'water bottle' and 'water bottle lid' are DIFFERENT product types"
            }
        }
    },
    "m16": {
        "prompt_file": "prompts/modules/m16_complementary_check_v1.1.md",
        "key_instructions": [
            "Would Amazon show 'Frequently bought together'?",
            "Same Category ≠ Complementary",
            "Relationship types: Maintenance, Storage, Accessories"
        ],
        "patterns": {
            "accessory_not_complementary": {
                "detect": lambda e: e.get("Error_Type") == "FN" and e.get("Expected") == "C",
                "instruction": "Accessories are complementary - they enhance or support the main product",
                "hypothesis": "Model rejected complementary for accessories, possibly applying too strict criteria",
                "improvement": "Emphasize that accessories ARE complementary by default. 'water bottle boot' complements 'water bottle'"
            },
            "same_category_as_complementary": {
                "detect": lambda e: e.get("Error_Type") == "FP" and e.get("Output") == "C",
                "instruction": "Same Category ≠ Complementary - similar products in same category are NOT complementary",
                "hypothesis": "Model marks products as complementary because they're in same category or used in similar contexts",
                "improvement": "Add more negative examples: Two different brands of same product are NOT complementary"
            }
        }
    }
}


def analyze_error(row: Dict, module: str) -> Dict:
    """Analyze a single error and add hypothesis columns."""
    patterns = ERROR_PATTERNS.get(module, {}).get("patterns", {})
    key_instructions = ERROR_PATTERNS.get(module, {}).get("key_instructions", [])

    result = {
        "Prompt_Instruction": "",
        "Hypothesis_Discrepancy": "",
        "Hypothesis_Improvement": ""
    }

    # Find matching pattern
    for pattern_name, pattern_info in patterns.items():
        if pattern_info["detect"](row):
            result["Prompt_Instruction"] = pattern_info["instruction"]
            result["Hypothesis_Discrepancy"] = pattern_info["hypothesis"]
            result["Hypothesis_Improvement"] = pattern_info["improvement"]
            break

    # If no specific pattern matched, use generic analysis
    if not result["Hypothesis_Discrepancy"]:
        error_type = row.get("Error_Type", "")
        if error_type == "FP":
            result["Prompt_Instruction"] = "; ".join(key_instructions[:2]) if key_instructions else "See prompt"
            result["Hypothesis_Discrepancy"] = "Model incorrectly classified as positive - criteria may be too loose"
            result["Hypothesis_Improvement"] = "Add stricter criteria or negative examples for this case type"
        elif error_type == "FN":
            result["Prompt_Instruction"] = "; ".join(key_instructions[:2]) if key_instructions else "See prompt"
            result["Hypothesis_Discrepancy"] = "Model failed to detect positive case - criteria may be too strict or case not covered"
            result["Hypothesis_Improvement"] = "Add positive examples covering this case pattern"

    return result


def process_error_csv(input_file: Path, output_file: Path, module: str):
    """Process error CSV and add analysis columns."""
    rows_processed = 0

    with open(input_file, 'r', encoding='utf-8') as f_in:
        reader = csv.DictReader(f_in)
        fieldnames = reader.fieldnames + ["Prompt_Instruction", "Hypothesis_Discrepancy", "Hypothesis_Improvement"]

        with open(output_file, 'w', newline='', encoding='utf-8') as f_out:
            writer = csv.DictWriter(f_out, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                analysis = analyze_error(row, module)
                row.update(analysis)
                writer.writerow(row)
                rows_processed += 1

    return rows_processed


def generate_summary_report(error_dir: Path, output_file: Path):
    """Generate summary report of all errors across modules."""
    summary = []

    for csv_file in sorted(error_dir.glob("*_errors.csv")):
        module = csv_file.stem.replace("_errors", "")

        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        if not rows:
            continue

        fp_count = sum(1 for r in rows if r.get("Error_Type") == "FP")
        fn_count = sum(1 for r in rows if r.get("Error_Type") == "FN")

        # Get unique ASINs and brands affected
        asins = set(r.get("ASIN", "") for r in rows if r.get("ASIN"))
        brands = set(r.get("Brand_Name", "") for r in rows if r.get("Brand_Name"))

        summary.append({
            "module": module,
            "total_errors": len(rows),
            "fp_count": fp_count,
            "fn_count": fn_count,
            "asins_affected": len(asins),
            "brands_affected": brands,
            "top_patterns": _get_top_patterns(rows, module)
        })

    # Write report
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Error Analysis Summary Report\n\n")

        for s in summary:
            f.write(f"## {s['module'].upper()}\n")
            f.write(f"- **Total Errors**: {s['total_errors']}\n")
            f.write(f"- **False Positives (FP)**: {s['fp_count']}\n")
            f.write(f"- **False Negatives (FN)**: {s['fn_count']}\n")
            f.write(f"- **ASINs Affected**: {s['asins_affected']}\n")
            f.write(f"- **Brands**: {', '.join(s['brands_affected'])}\n")
            f.write(f"- **Top Patterns**:\n")
            for pattern in s['top_patterns']:
                f.write(f"  - {pattern}\n")
            f.write("\n")

    return summary


def _get_top_patterns(rows: List[Dict], module: str) -> List[str]:
    """Identify top error patterns for a module."""
    patterns = []

    # Group by error type and look for common patterns
    fp_keywords = [r.get("Keyword", "") for r in rows if r.get("Error_Type") == "FP"]
    fn_keywords = [r.get("Keyword", "") for r in rows if r.get("Error_Type") == "FN"]

    if fp_keywords:
        patterns.append(f"FP: {len(fp_keywords)} cases - model over-classifying")
    if fn_keywords:
        patterns.append(f"FN: {len(fn_keywords)} cases - model under-classifying")

    # Module-specific patterns
    if module in ["m04", "m04b"]:
        own_brand_fps = sum(1 for r in rows if r.get("Error_Type") == "FP" and r.get("Expected") == "null")
        if own_brand_fps:
            patterns.append(f"Own brand marked as CB: {own_brand_fps} cases")

        known_brand_fns = sum(1 for r in rows if r.get("Error_Type") == "FN" and
                             "not in competitor_entities" in r.get("Reasoning", "").lower())
        if known_brand_fns:
            patterns.append(f"Known brand not detected (not in list): {known_brand_fns} cases")

    if module == "m15":
        accessory_fps = sum(1 for r in rows if r.get("Error_Type") == "FP" and
                          any(x in r.get("Keyword", "").lower() for x in ["boot", "lid", "scoop", "accessories"]))
        if accessory_fps:
            patterns.append(f"Accessories marked as substitutes: {accessory_fps} cases")

    return patterns[:5]


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate enhanced error analysis CSVs")
    parser.add_argument("--batch-dir", "-b", required=True, help="Batch directory with error_analysis subfolder")
    parser.add_argument("--modules", "-m", nargs="*", help="Specific modules to process")

    args = parser.parse_args()

    batch_path = Path(args.batch_dir)
    error_dir = batch_path / "error_analysis"
    enhanced_dir = batch_path / "error_analysis_enhanced"
    enhanced_dir.mkdir(parents=True, exist_ok=True)

    print(f"Input: {error_dir}")
    print(f"Output: {enhanced_dir}")
    print("=" * 60)

    # Process each error file
    for csv_file in sorted(error_dir.glob("*_errors.csv")):
        module = csv_file.stem.replace("_errors", "")

        if args.modules and module not in args.modules:
            continue

        output_file = enhanced_dir / f"{module}_errors_enhanced.csv"

        print(f"\nProcessing {module}...")
        count = process_error_csv(csv_file, output_file, module)
        print(f"  {count} errors → {output_file.name}")

    # Generate summary report
    summary_file = enhanced_dir / "SUMMARY_REPORT.md"
    generate_summary_report(error_dir, summary_file)
    print(f"\n{'='*60}")
    print(f"Summary report: {summary_file}")


if __name__ == "__main__":
    main()
