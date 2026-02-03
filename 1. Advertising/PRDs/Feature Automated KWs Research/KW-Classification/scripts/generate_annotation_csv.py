#!/usr/bin/env python3
"""
Generate Annotation CSV Files

Creates CSV files formatted for human annotators to validate LLM outputs.
Supports all 22 modules with module-specific column structures.
"""

import argparse
import csv
import json
import random
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
EXPERIMENT_RESULTS_DIR = PROJECT_ROOT / "experiment_results"
ANNOTATION_TASKS_DIR = PROJECT_ROOT / "annotation_tasks"

# Module configurations with annotation column definitions
MODULE_ANNOTATION_CONFIG = {
    # Stage 1: Brand Entity Extraction
    "m01": {
        "name": "ExtractOwnBrandEntities",
        "columns": [
            "row_id", "asin", "product_title",
            "llm_brand_name", "llm_category",
            "annotator_a_brand", "annotator_a_category",
            "annotator_b_brand", "annotator_b_category",
            "brand_match", "category_match", "notes"
        ],
        "extract_fields": lambda row: {
            "product_title": _get_nested(row, "input", "title", default=""),
            "llm_brand_name": _get_nested(row, "output", "brand_name", default=""),
            "llm_category": _get_nested(row, "output", "category", default=""),
        }
    },
    "m01a": {
        "name": "ExtractOwnBrandVariations",
        "columns": [
            "row_id", "asin", "brand_name",
            "llm_variations",
            "annotator_a_variations", "annotator_b_variations",
            "overlap_score", "notes"
        ],
        "extract_fields": lambda row: {
            "brand_name": row.get("Brand", ""),
            "llm_variations": _format_list(_get_nested(row, "output", "variations", default=[])),
        }
    },
    "m01b": {
        "name": "ExtractBrandRelatedTerms",
        "columns": [
            "row_id", "asin", "brand_name",
            "llm_related_terms",
            "annotator_a_terms", "annotator_b_terms",
            "overlap_score", "notes"
        ],
        "extract_fields": lambda row: {
            "brand_name": row.get("Brand", ""),
            "llm_related_terms": _format_list(_get_nested(row, "output", "related_terms", default=[])),
        }
    },
    "m03": {
        "name": "GenerateCompetitorEntities",
        "columns": [
            "row_id", "asin", "category",
            "llm_competitors",
            "annotator_a_competitors", "annotator_b_competitors",
            "precision", "recall", "notes"
        ],
        "extract_fields": lambda row: {
            "category": _get_nested(row, "input", "category", default=""),
            "llm_competitors": _format_json(_get_nested(row, "output", "competitors", default=[])),
        }
    },

    # Stage 2: Brand Scope Classification
    "m02": {
        "name": "ClassifyOwnBrandKeywords",
        "columns": [
            "row_id", "asin", "keyword", "brand_name",
            "llm_classification", "llm_matched_term", "llm_confidence", "llm_reasoning",
            "annotator_a", "annotator_a_reasoning",
            "annotator_b", "annotator_b_reasoning",
            "agreement", "notes"
        ],
        "extract_fields": lambda row: {
            "keyword": row.get("Keyword", ""),
            "brand_name": row.get("Brand", ""),
            "llm_classification": _get_nested(row, "output", "classification", default=""),
            "llm_matched_term": _get_nested(row, "output", "matched_term", default=""),
            "llm_confidence": _get_nested(row, "output", "confidence", default=""),
            "llm_reasoning": _get_nested(row, "output", "reasoning", default=""),
        }
    },
    "m02b": {
        "name": "ClassifyOwnBrandKeywords_PathB",
        "columns": [
            "row_id", "asin", "keyword", "brand_name",
            "llm_classification", "llm_matched_term", "llm_confidence", "llm_reasoning",
            "annotator_a", "annotator_a_reasoning",
            "annotator_b", "annotator_b_reasoning",
            "agreement", "notes"
        ],
        "extract_fields": lambda row: {
            "keyword": row.get("Keyword", ""),
            "brand_name": row.get("Brand", ""),
            "llm_classification": _get_nested(row, "output", "classification", default=""),
            "llm_matched_term": _get_nested(row, "output", "matched_term", default=""),
            "llm_confidence": _get_nested(row, "output", "confidence", default=""),
            "llm_reasoning": _get_nested(row, "output", "reasoning", default=""),
        }
    },
    "m04": {
        "name": "ClassifyCompetitorBrandKeywords",
        "columns": [
            "row_id", "asin", "keyword", "brand_name",
            "llm_classification", "llm_matched_competitor", "llm_confidence", "llm_reasoning",
            "annotator_a", "annotator_a_reasoning",
            "annotator_b", "annotator_b_reasoning",
            "agreement", "notes"
        ],
        "extract_fields": lambda row: {
            "keyword": row.get("Keyword", ""),
            "brand_name": row.get("Brand", ""),
            "llm_classification": _get_nested(row, "output", "classification", default=""),
            "llm_matched_competitor": _get_nested(row, "output", "matched_competitor", default=""),
            "llm_confidence": _get_nested(row, "output", "confidence", default=""),
            "llm_reasoning": _get_nested(row, "output", "reasoning", default=""),
        }
    },
    "m04b": {
        "name": "ClassifyCompetitorBrandKeywords_PathB",
        "columns": [
            "row_id", "asin", "keyword", "brand_name",
            "llm_classification", "llm_matched_competitor", "llm_confidence", "llm_reasoning",
            "annotator_a", "annotator_a_reasoning",
            "annotator_b", "annotator_b_reasoning",
            "agreement", "notes"
        ],
        "extract_fields": lambda row: {
            "keyword": row.get("Keyword", ""),
            "brand_name": row.get("Brand", ""),
            "llm_classification": _get_nested(row, "output", "classification", default=""),
            "llm_matched_competitor": _get_nested(row, "output", "matched_competitor", default=""),
            "llm_confidence": _get_nested(row, "output", "confidence", default=""),
            "llm_reasoning": _get_nested(row, "output", "reasoning", default=""),
        }
    },
    "m05": {
        "name": "ClassifyNonBrandedKeywords",
        "columns": [
            "row_id", "asin", "keyword", "brand_name",
            "llm_classification", "llm_confidence", "llm_reasoning",
            "annotator_a", "annotator_a_reasoning",
            "annotator_b", "annotator_b_reasoning",
            "agreement", "notes"
        ],
        "extract_fields": lambda row: {
            "keyword": row.get("Keyword", ""),
            "brand_name": row.get("Brand", ""),
            "llm_classification": _get_nested(row, "output", "classification", default=""),
            "llm_confidence": _get_nested(row, "output", "confidence", default=""),
            "llm_reasoning": _get_nested(row, "output", "reasoning", default=""),
        }
    },
    "m05b": {
        "name": "ClassifyNonBrandedKeywords_PathB",
        "columns": [
            "row_id", "asin", "keyword", "brand_name",
            "llm_classification", "llm_confidence", "llm_reasoning",
            "annotator_a", "annotator_a_reasoning",
            "annotator_b", "annotator_b_reasoning",
            "agreement", "notes"
        ],
        "extract_fields": lambda row: {
            "keyword": row.get("Keyword", ""),
            "brand_name": row.get("Brand", ""),
            "llm_classification": _get_nested(row, "output", "classification", default=""),
            "llm_confidence": _get_nested(row, "output", "confidence", default=""),
            "llm_reasoning": _get_nested(row, "output", "reasoning", default=""),
        }
    },

    # Stage 3: Product Foundation
    "m06": {
        "name": "GenerateProductTypeTaxonomy",
        "columns": [
            "row_id", "asin", "product_title", "bullet_points", "description",
            "product_type", "category_root", "category_sub",
            "llm_taxonomy",
            "annotator_a_taxonomy", "annotator_b_taxonomy",
            "agreement", "notes"
        ],
        "extract_fields": lambda row: {
            "product_title": _get_nested(row, "input", "title", default=""),
            "bullet_points": _get_nested(row, "input", "bullet_points", default=""),
            "description": _get_nested(row, "input", "description", default=""),
            "product_type": _get_nested(row, "input", "product_type", default=""),
            "category_root": _get_nested(row, "input", "category_root", default=""),
            "category_sub": _get_nested(row, "input", "category_sub", default=""),
            "llm_taxonomy": _format_json(_get_nested(row, "output", "taxonomy", default=[])),
        }
    },
    "m07": {
        "name": "ExtractProductAttributes",
        "columns": [
            "row_id", "asin", "product_title", "bullet_points", "description",
            "product_type", "category_root", "category_sub",
            "color", "size", "material", "style", "target_audience",
            "specific_uses", "model", "item_form", "number_of_items", "included_components",
            "llm_variants", "llm_use_cases", "llm_audiences",
            "annotator_a_variants", "annotator_a_use_cases", "annotator_a_audiences",
            "annotator_b_variants", "annotator_b_use_cases", "annotator_b_audiences",
            "agreement", "notes"
        ],
        "extract_fields": lambda row: {
            "product_title": _get_nested(row, "input", "title", default=""),
            "bullet_points": _get_nested(row, "input", "bullet_points", default=""),
            "description": _get_nested(row, "input", "description", default=""),
            "product_type": _get_nested(row, "input", "product_type", default=""),
            "category_root": _get_nested(row, "input", "category_root", default=""),
            "category_sub": _get_nested(row, "input", "category_sub", default=""),
            "color": _get_nested(row, "input", "color", default=""),
            "size": _get_nested(row, "input", "size", default=""),
            "material": _get_nested(row, "input", "material", default=""),
            "style": _get_nested(row, "input", "style", default=""),
            "target_audience": _get_nested(row, "input", "target_audience", default=""),
            "specific_uses": _get_nested(row, "input", "specific_uses", default=""),
            "model": _get_nested(row, "input", "model", default=""),
            "item_form": _get_nested(row, "input", "item_form", default=""),
            "number_of_items": _get_nested(row, "input", "number_of_items", default=""),
            "included_components": _get_nested(row, "input", "included_components", default=""),
            "llm_variants": _format_list(_get_nested(row, "output", "variants", default=[])),
            "llm_use_cases": _format_list(_get_nested(row, "output", "use_cases", default=[])),
            "llm_audiences": _format_list(_get_nested(row, "output", "audiences", default=[])),
        }
    },
    "m08": {
        "name": "AssignAttributeRanks",
        "columns": [
            "row_id", "asin", "product_title", "bullet_points", "description",
            "taxonomy", "variants", "use_cases", "audiences",
            "llm_attribute_table",
            "annotator_a_attribute_table", "annotator_b_attribute_table",
            "agreement", "notes"
        ],
        "extract_fields": lambda row: {
            "product_title": _get_nested(row, "input", "title", default=""),
            "bullet_points": _get_nested(row, "input", "bullet_points", default=""),
            "description": _get_nested(row, "input", "description", default=""),
            "taxonomy": _format_json(_get_nested(row, "input", "taxonomy", default=[])),
            "variants": _format_list(_get_nested(row, "input", "variants", default=[])),
            "use_cases": _format_list(_get_nested(row, "input", "use_cases", default=[])),
            "audiences": _format_list(_get_nested(row, "input", "audiences", default=[])),
            "llm_attribute_table": _format_json(_get_nested(row, "output", "attribute_table", default=[])),
        }
    },
    "m09": {
        "name": "IdentifyPrimaryIntendedUse",
        "columns": [
            "row_id", "asin", "product_title", "bullet_points", "description",
            "taxonomy", "attribute_table", "product_attributes",
            "llm_primary_use", "llm_confidence", "llm_reasoning",
            "annotator_a_use", "annotator_a_reasoning",
            "annotator_b_use", "annotator_b_reasoning",
            "agreement", "notes"
        ],
        "extract_fields": lambda row: {
            "product_title": _get_nested(row, "input", "title", default=""),
            "bullet_points": _get_nested(row, "input", "bullet_points", default=""),
            "description": _get_nested(row, "input", "description", default=""),
            "taxonomy": _format_json(_get_nested(row, "input", "taxonomy", default=[])),
            "attribute_table": _format_json(_get_nested(row, "input", "attribute_table", default=[])),
            "product_attributes": _format_json(_get_nested(row, "input", "product_attributes", default={})),
            "llm_primary_use": _get_nested(row, "output", "primary_use", default=""),
            "llm_confidence": _get_nested(row, "output", "confidence", default=""),
            "llm_reasoning": _get_nested(row, "output", "reasoning", default=""),
        }
    },
    "m10": {
        "name": "ValidatePrimaryIntendedUse",
        "columns": [
            "row_id", "asin", "product_title", "bullet_points", "description",
            "taxonomy", "attribute_table", "product_attributes", "primary_use",
            "llm_validated_use", "llm_is_valid", "llm_reasoning",
            "annotator_a_valid", "annotator_a_validated_use", "annotator_a_reasoning",
            "annotator_b_valid", "annotator_b_validated_use", "annotator_b_reasoning",
            "agreement", "notes"
        ],
        "extract_fields": lambda row: {
            "product_title": _get_nested(row, "input", "title", default=""),
            "bullet_points": _get_nested(row, "input", "bullet_points", default=""),
            "description": _get_nested(row, "input", "description", default=""),
            "taxonomy": _format_json(_get_nested(row, "input", "taxonomy", default=[])),
            "attribute_table": _format_json(_get_nested(row, "input", "attribute_table", default=[])),
            "product_attributes": _format_json(_get_nested(row, "input", "product_attributes", default={})),
            "primary_use": _get_nested(row, "input", "primary_use", default=""),
            "llm_validated_use": _get_nested(row, "output", "validated_use", default=""),
            "llm_is_valid": _get_nested(row, "output", "is_valid", default=""),
            "llm_reasoning": _get_nested(row, "output", "reasoning", default=""),
        }
    },
    "m11": {
        "name": "IdentifyHardConstraints",
        "columns": [
            "row_id", "asin", "product_title", "bullet_points", "description",
            "validated_use", "taxonomy", "attribute_table", "product_attributes",
            "llm_hard_constraints", "llm_reasoning",
            "annotator_a_constraints", "annotator_a_reasoning",
            "annotator_b_constraints", "annotator_b_reasoning",
            "agreement", "notes"
        ],
        "extract_fields": lambda row: {
            "product_title": _get_nested(row, "input", "title", default=""),
            "bullet_points": _get_nested(row, "input", "bullet_points", default=""),
            "description": _get_nested(row, "input", "description", default=""),
            "validated_use": _get_nested(row, "input", "validated_use", default=""),
            "taxonomy": _format_json(_get_nested(row, "input", "taxonomy", default=[])),
            "attribute_table": _format_json(_get_nested(row, "input", "attribute_table", default=[])),
            "product_attributes": _format_json(_get_nested(row, "input", "product_attributes", default={})),
            "llm_hard_constraints": _format_list(_get_nested(row, "output", "hard_constraints", default=[])),
            "llm_reasoning": _get_nested(row, "output", "reasoning", default=""),
        }
    },

    # Stage 4: Relevance Classification
    # All M12-M16 share inputs: keyword, title, bullet_points, description, validated_use, taxonomy, attribute_table, product_attributes, hard_constraints
    "m12": {
        "name": "HardConstraintViolationCheck",
        "columns": [
            "row_id", "asin", "keyword", "brand_name",
            "product_title", "bullet_points", "description",
            "validated_use", "taxonomy", "attribute_table", "hard_constraints",
            "llm_violates", "llm_violated_constraint", "llm_confidence", "llm_reasoning",
            "annotator_a_violates", "annotator_a_reasoning",
            "annotator_b_violates", "annotator_b_reasoning",
            "agreement", "notes"
        ],
        "extract_fields": lambda row: {
            "keyword": row.get("Keyword", ""),
            "brand_name": row.get("Brand", ""),
            "product_title": _get_nested(row, "input", "title", default=""),
            "bullet_points": _get_nested(row, "input", "bullet_points", default=""),
            "description": _get_nested(row, "input", "description", default=""),
            "validated_use": _get_nested(row, "input", "validated_use", default=""),
            "taxonomy": _format_json(_get_nested(row, "input", "taxonomy", default=[])),
            "attribute_table": _format_json(_get_nested(row, "input", "attribute_table", default=[])),
            "hard_constraints": _format_list(_get_nested(row, "input", "hard_constraints", default=[])),
            "llm_violates": _get_nested(row, "output", "violates_constraint", default=""),
            "llm_violated_constraint": _get_nested(row, "output", "violated_constraint", default=""),
            "llm_confidence": _get_nested(row, "output", "confidence", default=""),
            "llm_reasoning": _get_nested(row, "output", "reasoning", default=""),
        }
    },
    "m12b": {
        "name": "CombinedClassification",
        "columns": [
            "row_id", "asin", "keyword", "brand_name",
            "product_title", "bullet_points", "description",
            "validated_use", "taxonomy", "attribute_table", "hard_constraints",
            "llm_relevancy", "llm_confidence", "llm_reasoning",
            "annotator_a_relevancy", "annotator_a_reasoning",
            "annotator_b_relevancy", "annotator_b_reasoning",
            "agreement", "notes"
        ],
        "extract_fields": lambda row: {
            "keyword": row.get("Keyword", ""),
            "brand_name": row.get("Brand", ""),
            "product_title": _get_nested(row, "input", "title", default=""),
            "bullet_points": _get_nested(row, "input", "bullet_points", default=""),
            "description": _get_nested(row, "input", "description", default=""),
            "validated_use": _get_nested(row, "input", "validated_use", default=""),
            "taxonomy": _format_json(_get_nested(row, "input", "taxonomy", default=[])),
            "attribute_table": _format_json(_get_nested(row, "input", "attribute_table", default=[])),
            "hard_constraints": _format_list(_get_nested(row, "input", "hard_constraints", default=[])),
            "llm_relevancy": _get_nested(row, "output", "relevancy", default=""),
            "llm_confidence": _get_nested(row, "output", "confidence", default=""),
            "llm_reasoning": _get_nested(row, "output", "reasoning", default=""),
        }
    },
    "m13": {
        "name": "ProductTypeCheck",
        "columns": [
            "row_id", "asin", "keyword", "brand_name",
            "product_title", "bullet_points", "description",
            "validated_use", "taxonomy", "attribute_table", "hard_constraints",
            "llm_same_type", "llm_confidence", "llm_reasoning",
            "annotator_a_same_type", "annotator_a_reasoning",
            "annotator_b_same_type", "annotator_b_reasoning",
            "agreement", "notes"
        ],
        "extract_fields": lambda row: {
            "keyword": row.get("Keyword", ""),
            "brand_name": row.get("Brand", ""),
            "product_title": _get_nested(row, "input", "title", default=""),
            "bullet_points": _get_nested(row, "input", "bullet_points", default=""),
            "description": _get_nested(row, "input", "description", default=""),
            "validated_use": _get_nested(row, "input", "validated_use", default=""),
            "taxonomy": _format_json(_get_nested(row, "input", "taxonomy", default=[])),
            "attribute_table": _format_json(_get_nested(row, "input", "attribute_table", default=[])),
            "hard_constraints": _format_list(_get_nested(row, "input", "hard_constraints", default=[])),
            "llm_same_type": _get_nested(row, "output", "same_type", default=""),
            "llm_confidence": _get_nested(row, "output", "confidence", default=""),
            "llm_reasoning": _get_nested(row, "output", "reasoning", default=""),
        }
    },
    "m14": {
        "name": "PrimaryUseCheckSameType",
        "columns": [
            "row_id", "asin", "keyword", "brand_name",
            "product_title", "bullet_points", "description",
            "validated_use", "taxonomy", "attribute_table", "hard_constraints",
            "llm_relevancy", "llm_confidence", "llm_reasoning",
            "annotator_a_relevancy", "annotator_a_reasoning",
            "annotator_b_relevancy", "annotator_b_reasoning",
            "agreement", "notes"
        ],
        "extract_fields": lambda row: {
            "keyword": row.get("Keyword", ""),
            "brand_name": row.get("Brand", ""),
            "product_title": _get_nested(row, "input", "title", default=""),
            "bullet_points": _get_nested(row, "input", "bullet_points", default=""),
            "description": _get_nested(row, "input", "description", default=""),
            "validated_use": _get_nested(row, "input", "validated_use", default=""),
            "taxonomy": _format_json(_get_nested(row, "input", "taxonomy", default=[])),
            "attribute_table": _format_json(_get_nested(row, "input", "attribute_table", default=[])),
            "hard_constraints": _format_list(_get_nested(row, "input", "hard_constraints", default=[])),
            "llm_relevancy": _get_nested(row, "output", "relevancy", default=""),
            "llm_confidence": _get_nested(row, "output", "confidence", default=""),
            "llm_reasoning": _get_nested(row, "output", "reasoning", default=""),
        }
    },
    "m15": {
        "name": "SubstituteCheck",
        "columns": [
            "row_id", "asin", "keyword", "brand_name",
            "product_title", "bullet_points", "description",
            "validated_use", "taxonomy", "attribute_table", "hard_constraints",
            "llm_relevancy", "llm_confidence", "llm_reasoning",
            "annotator_a_relevancy", "annotator_a_reasoning",
            "annotator_b_relevancy", "annotator_b_reasoning",
            "agreement", "notes"
        ],
        "extract_fields": lambda row: {
            "keyword": row.get("Keyword", ""),
            "brand_name": row.get("Brand", ""),
            "product_title": _get_nested(row, "input", "title", default=""),
            "bullet_points": _get_nested(row, "input", "bullet_points", default=""),
            "description": _get_nested(row, "input", "description", default=""),
            "validated_use": _get_nested(row, "input", "validated_use", default=""),
            "taxonomy": _format_json(_get_nested(row, "input", "taxonomy", default=[])),
            "attribute_table": _format_json(_get_nested(row, "input", "attribute_table", default=[])),
            "hard_constraints": _format_list(_get_nested(row, "input", "hard_constraints", default=[])),
            "llm_relevancy": _get_nested(row, "output", "relevancy", default=""),
            "llm_confidence": _get_nested(row, "output", "confidence", default=""),
            "llm_reasoning": _get_nested(row, "output", "reasoning", default=""),
        }
    },
    "m16": {
        "name": "ComplementaryCheck",
        "columns": [
            "row_id", "asin", "keyword", "brand_name",
            "product_title", "bullet_points", "description",
            "validated_use", "taxonomy", "attribute_table", "hard_constraints",
            "llm_relevancy", "llm_confidence", "llm_reasoning",
            "annotator_a_relevancy", "annotator_a_reasoning",
            "annotator_b_relevancy", "annotator_b_reasoning",
            "agreement", "notes"
        ],
        "extract_fields": lambda row: {
            "keyword": row.get("Keyword", ""),
            "brand_name": row.get("Brand", ""),
            "product_title": _get_nested(row, "input", "title", default=""),
            "bullet_points": _get_nested(row, "input", "bullet_points", default=""),
            "description": _get_nested(row, "input", "description", default=""),
            "validated_use": _get_nested(row, "input", "validated_use", default=""),
            "taxonomy": _format_json(_get_nested(row, "input", "taxonomy", default=[])),
            "attribute_table": _format_json(_get_nested(row, "input", "attribute_table", default=[])),
            "hard_constraints": _format_list(_get_nested(row, "input", "hard_constraints", default=[])),
            "llm_relevancy": _get_nested(row, "output", "relevancy", default=""),
            "llm_confidence": _get_nested(row, "output", "confidence", default=""),
            "llm_reasoning": _get_nested(row, "output", "reasoning", default=""),
        }
    },
}


def _get_nested(data: dict, *keys, default=None):
    """Safely get nested dictionary value."""
    result = data
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key, default)
        elif isinstance(result, str):
            # Try to parse as JSON
            try:
                parsed = json.loads(result)
                result = parsed.get(key, default) if isinstance(parsed, dict) else default
            except (json.JSONDecodeError, AttributeError):
                return default
        else:
            return default
    return result if result is not None else default


def _format_list(value) -> str:
    """Format list as comma-separated string."""
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    return str(value) if value else ""


def _format_json(value) -> str:
    """Format value as compact JSON."""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value) if value else ""


def _parse_json_field(value: str) -> any:
    """Parse JSON string, return original if not valid JSON."""
    if not value:
        return {}
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return {"raw": value}


def find_latest_experiment_csv(module_id: str) -> Optional[Path]:
    """Find the most recent experiment CSV for a module."""
    module_config = MODULE_ANNOTATION_CONFIG.get(module_id.lower())
    if not module_config:
        return None

    # Find matching directory
    module_name = module_config["name"]
    pattern = f"*{module_name}*"

    matching_dirs = list(EXPERIMENT_RESULTS_DIR.glob(pattern))
    if not matching_dirs:
        # Try with module ID prefix
        pattern = f"M{module_id[1:].upper()}*"
        matching_dirs = list(EXPERIMENT_RESULTS_DIR.glob(pattern))

    if not matching_dirs:
        return None

    # Find most recent CSV
    latest_csv = None
    latest_time = 0

    for dir_path in matching_dirs:
        for csv_file in dir_path.glob("*.csv"):
            mtime = csv_file.stat().st_mtime
            if mtime > latest_time:
                latest_time = mtime
                latest_csv = csv_file

    return latest_csv


def load_experiment_results(csv_path: Path) -> List[Dict]:
    """Load experiment results from CSV."""
    results = []

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Parse JSON fields
            parsed_row = {}
            for key, value in row.items():
                if key in ("input", "output", "expected", "metadata", "metrics"):
                    parsed_row[key] = _parse_json_field(value)
                else:
                    parsed_row[key] = value
            results.append(parsed_row)

    return results


def generate_annotation_csv(
    module_id: str,
    source_csv: Optional[Path] = None,
    sample_size: Optional[int] = None,
    shuffle: bool = True,
    output_dir: Optional[Path] = None,
    seed: Optional[int] = None
) -> Optional[Path]:
    """Generate annotation CSV for a module."""
    module_id = module_id.lower()
    config = MODULE_ANNOTATION_CONFIG.get(module_id)

    if not config:
        print(f"Error: Unknown module '{module_id}'")
        print(f"Available modules: {', '.join(MODULE_ANNOTATION_CONFIG.keys())}")
        return None

    # Find source CSV
    if source_csv is None:
        source_csv = find_latest_experiment_csv(module_id)
        if source_csv is None:
            print(f"Error: No experiment results found for module '{module_id}'")
            return None

    print(f"Source: {source_csv}")

    # Load results
    results = load_experiment_results(source_csv)
    print(f"Loaded {len(results)} records")

    if not results:
        print("Error: No results to process")
        return None

    # Shuffle if requested
    if shuffle:
        if seed is not None:
            random.seed(seed)
        random.shuffle(results)
        print(f"Shuffled results (seed={seed})")

    # Sample if requested
    if sample_size and sample_size < len(results):
        results = results[:sample_size]
        print(f"Sampled {sample_size} records")

    # Setup output
    if output_dir is None:
        output_dir = ANNOTATION_TASKS_DIR

    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"{module_id.upper()}_annotation_{timestamp}.csv"
    output_path = output_dir / output_filename

    # Generate annotation CSV
    columns = config["columns"]
    extract_fn = config["extract_fields"]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()

        for idx, row in enumerate(results, start=1):
            # Extract module-specific fields
            extracted = extract_fn(row)

            # Build annotation row
            annotation_row = {
                "row_id": idx,
                "asin": row.get("ASIN", ""),
            }
            annotation_row.update(extracted)

            # Fill empty annotator columns
            for col in columns:
                if col not in annotation_row:
                    annotation_row[col] = ""

            writer.writerow(annotation_row)

    print(f"Generated: {output_path}")
    print(f"Columns: {', '.join(columns)}")

    return output_path


def list_available_modules():
    """List modules with available experiment results."""
    print("Available modules for annotation:")
    print("-" * 60)

    for module_id, config in sorted(MODULE_ANNOTATION_CONFIG.items()):
        csv_path = find_latest_experiment_csv(module_id)
        status = "✓" if csv_path else "○"
        print(f"  {status} {module_id:6} - {config['name']}")
        if csv_path:
            print(f"          Latest: {csv_path.name}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate annotation CSV files for human validation"
    )
    subparsers = parser.add_subparsers(dest="command")

    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate annotation CSV")
    gen_parser.add_argument("module", help="Module ID (e.g., m12, m02b)")
    gen_parser.add_argument("--source", "-s", type=Path, help="Source CSV file")
    gen_parser.add_argument("--sample", "-n", type=int, help="Sample size")
    gen_parser.add_argument("--no-shuffle", action="store_true", help="Don't shuffle")
    gen_parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    gen_parser.add_argument("--output", "-o", type=Path, help="Output directory")

    # List command
    subparsers.add_parser("list", help="List available modules")

    # Batch command
    batch_parser = subparsers.add_parser("batch", help="Generate for multiple modules")
    batch_parser.add_argument("--modules", "-m", nargs="+", help="Module IDs")
    batch_parser.add_argument("--all", action="store_true", help="All available modules")
    batch_parser.add_argument("--sample", "-n", type=int, help="Sample size per module")
    batch_parser.add_argument("--seed", type=int, help="Random seed")

    args = parser.parse_args()

    if args.command == "generate":
        generate_annotation_csv(
            module_id=args.module,
            source_csv=args.source,
            sample_size=args.sample,
            shuffle=not args.no_shuffle,
            output_dir=args.output,
            seed=args.seed,
        )

    elif args.command == "list":
        list_available_modules()

    elif args.command == "batch":
        modules = args.modules or []

        if args.all:
            modules = [
                m for m in MODULE_ANNOTATION_CONFIG.keys()
                if find_latest_experiment_csv(m) is not None
            ]

        if not modules:
            print("No modules specified. Use --modules or --all")
            return

        print(f"Generating annotation CSVs for {len(modules)} modules")
        print("=" * 60)

        for module_id in modules:
            print(f"\n[{module_id.upper()}]")
            generate_annotation_csv(
                module_id=module_id,
                sample_size=args.sample,
                seed=args.seed,
            )

    else:
        parser.print_help()
        print("\nExamples:")
        print("  # List available modules")
        print("  python scripts/generate_annotation_csv.py list")
        print()
        print("  # Generate annotation CSV for M12")
        print("  python scripts/generate_annotation_csv.py generate m12")
        print()
        print("  # Generate with sampling")
        print("  python scripts/generate_annotation_csv.py generate m12 --sample 100")
        print()
        print("  # Generate for all modules with results")
        print("  python scripts/generate_annotation_csv.py batch --all --sample 50")


if __name__ == "__main__":
    main()
