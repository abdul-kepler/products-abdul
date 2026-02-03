"""
Braintrust Scorers for V3 Pipeline_v1.1 Evaluation
==============================================

Push to Braintrust with:
    cd braintrust_integration/scorers
    braintrust push --if-exists replace braintrust_scorers.py

Or use helper script:
    python push_scorers.py

================================================================================
SCORER REFERENCE GUIDE
================================================================================

This file defines 27 scorers for evaluating the KW Classification pipeline.
Each scorer measures a specific aspect of model output quality.

--------------------------------------------------------------------------------
BINARY CLASSIFICATION SCORERS (M2, M4, M5, M9, M10, M11, M12)
--------------------------------------------------------------------------------

These scorers evaluate yes/no classification decisions. They return:
  - 1.0 = Correct (prediction matches ground truth)
  - 0.0 = Incorrect (prediction differs from ground truth)

| Scorer Slug     | Module | Field           | What It Measures                    |
|-----------------|--------|-----------------|-------------------------------------|
| m2-correct      | M2     | branding_scope_1| Own Brand (OB) classification       |
| m4-correct      | M4     | branding_scope_2| Competitor Brand (CB) classification|
| m5-correct      | M5     | branding_scope_3| Non-Branded (NB) classification     |
| m9-correct      | M9     | relationship_R  | Relevant (R) classification         |
| m10-correct     | M10    | relationship_N  | Negative (N) classification         |
| m11-correct     | M11    | relationship_S  | Substitute (S) classification       |
| m12-correct     | M12    | relationship_C  | Complementary (C) classification    |

Example:
  output:   {"branding_scope_1": "OB"}
  expected: {"branding_scope_1": "OB"}
  Score: 1.0 (correct match)

--------------------------------------------------------------------------------
LIST EXTRACTION SCORERS (M1, M3)
--------------------------------------------------------------------------------

These scorers evaluate how well the model extracts entities from text.
All return values 0.0-1.0 where higher is better.

| Scorer Slug      | Module | What It Measures                                    |
|------------------|--------|-----------------------------------------------------|
| m1-recall        | M1     | % of expected brand entities found by model         |
| m1-precision     | M1     | % of predicted brand entities that are correct      |
| m1-jaccard       | M1     | Overlap similarity (intersection / union) of sets   |
| m1-purity        | M1     | % of entities WITHOUT product words (quality check) |
| m1-length-comp   | M1     | % of entities with ≤3 words (proper brand names)    |
| m1-avg-length    | M1     | Normalized score based on avg words per entity      |
| m3-recall        | M3     | % of expected competitor entities found by model    |
| m3-precision     | M3     | % of predicted competitor entities that are correct |
| m3-jaccard       | M3     | Overlap similarity for competitor entities          |

Recall vs Precision:
  - Recall: "Did we find all expected items?" (penalizes missing items)
  - Precision: "Are all predictions correct?" (penalizes false positives)
  - Jaccard: "How similar are the sets?" (balanced measure)

Example:
  output:   {"brand_entities": ["JBL", "Harman"]}
  expected: {"brand_entities": ["JBL", "Harman", "Vibe"]}
  Recall: 2/3 = 0.67 (found 2 of 3 expected)
  Precision: 2/2 = 1.0 (all predictions correct)
  Jaccard: 2/3 = 0.67 (intersection=2, union=3)

M1 Quality Scorers:
  - m1-purity: Detects if brand entities contain product words like "oven", "mitt"
    Score 1.0 = all pure brand names, 0.0 = all contaminated with product words
  - m1-length-compliance: Brand names should be 1-3 words, not full product descriptions
    Score 1.0 = all proper length, 0.0 = all too long (4+ words)

--------------------------------------------------------------------------------
TAXONOMY SCORERS (M6)
--------------------------------------------------------------------------------

These scorers evaluate hierarchical product type classification.
Each level represents a different granularity (L1=most specific, L3=broadest).

| Scorer Slug  | Module | What It Measures                                    |
|--------------|--------|-----------------------------------------------------|
| m6-level1    | M6     | Accuracy at Level 1 (most specific category)        |
| m6-level2    | M6     | Accuracy at Level 2 (intermediate category)         |
| m6-level3    | M6     | Accuracy at Level 3 (broadest category)             |
| m6-overall   | M6     | Average accuracy across all levels                  |

Example:
  output:   {"taxonomy": [{"level": 1, "product_type": "Wireless Earbuds", "rank": 1}]}
  expected: {"taxonomy": [{"level": 1, "product_type": "Wireless Earbuds", "rank": 1},
                          {"level": 2, "product_type": "Earbuds", "rank": 1}]}
  m6-level1: 1.0 (correctly predicted "Wireless Earbuds" at level 1)
  m6-level2: 0.0 (did not predict level 2)
  m6-overall: 0.5 (average of levels)

--------------------------------------------------------------------------------
MULTI-FIELD SCORERS (M7)
--------------------------------------------------------------------------------

These scorers evaluate extraction of multiple attribute types.

| Scorer Slug   | Module | What It Measures                           |
|---------------|--------|--------------------------------------------|
| m7-variants   | M7     | Recall of product variants (color, size)   |
| m7-usecases   | M7     | Recall of use cases (gaming, travel)       |
| m7-audiences  | M7     | Recall of target audiences (students, pros)|
| m7-overall    | M7     | Average recall across all fields           |

Example:
  output:   {"variants": ["Wireless", "Black"], "use_cases": [], "audiences": []}
  expected: {"variants": ["Wireless", "Black", "32GB"], "use_cases": ["Gaming"], "audiences": ["Gamers"]}
  m7-variants: 2/3 = 0.67
  m7-usecases: 0/1 = 0.0
  m7-audiences: 0/1 = 0.0
  m7-overall: 0.22 (average)

--------------------------------------------------------------------------------
RANKING SCORERS (M8)
--------------------------------------------------------------------------------

These scorers evaluate attribute ranking quality using NDCG (Normalized Discounted
Cumulative Gain). NDCG measures if highly relevant items appear at top of ranking.

| Scorer Slug  | Module | What It Measures                           |
|--------------|--------|--------------------------------------------|
| m8-ndcg5     | M8     | NDCG@5 - ranking quality of top 5 items    |
| m8-ndcg10    | M8     | NDCG@10 - ranking quality of top 10 items  |

NDCG Interpretation:
  - 1.0 = Perfect ranking (items in ideal order)
  - 0.5 = Partially correct (some items out of order)
  - 0.0 = Completely wrong (reversed order)

Example:
  If expected rank is [A=1, B=2, C=3] and predicted is [B=1, A=2, C=3]:
  NDCG < 1.0 because A (most important) is not first

================================================================================
FIELD NAME HANDLING
================================================================================

All scorers handle both field name conventions:
  - Direct: "branding_scope_1"
  - Prefixed: "OUTPUT_branding_scope_1"

This ensures compatibility with different dataset/output formats.

================================================================================
NULL VALUE HANDLING
================================================================================

Scorers normalize null values to handle different representations:
  - Python None
  - String "null"
  - String "none"
  - Empty string ""

All are treated as equivalent null values for comparison.

================================================================================
"""

import math
from typing import Any, Dict, List, Optional

import braintrust
import pydantic


# Initialize project
# Project ID: 17b25eb4-95bf-499b-9ee3-1b6118546ecc
project = braintrust.projects.create(name="Keyword-Classification-Pipeline-V1.1")


# =============================================================================
# Parameter Models
# =============================================================================

class BinaryInput(pydantic.BaseModel):
    output: Dict[str, Any]
    expected: Dict[str, Any]


class ListInput(pydantic.BaseModel):
    output: Dict[str, Any]
    expected: Dict[str, Any]


class TaxonomyInput(pydantic.BaseModel):
    output: Dict[str, Any]
    expected: Dict[str, Any]


class RankingInput(pydantic.BaseModel):
    output: Dict[str, Any]
    expected: Dict[str, Any]


# =============================================================================
# Binary Classification Handlers
# =============================================================================


# ═══════════════════════════════════════════════════════════════════════════
# NORMALIZE NULL: Convert string "null"/"none"/"" to Python None
# Needed because YAML parses null as string sometimes
# ═══════════════════════════════════════════════════════════════════════════
def normalize_null(value):
    """Normalize null values - handle string 'null', None, empty string."""
    if value is None:
        return None
    if isinstance(value, str) and value.lower() in ("null", "none", ""):
        return None
    return value


# ═══════════════════════════════════════════════════════════════════════════
# M2 EXACT: Did the model correctly classify Own Brand (OB) vs null?
# 1.0 = correct, 0.0 = wrong
# ═══════════════════════════════════════════════════════════════════════════
def m2_correct_handler(output: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """M2: Own Brand (OB/null)"""
    if output is None or expected is None:
        return 0.0

    # Get prediction - check both possible field names
    if "branding_scope_1" in output:
        pred = output["branding_scope_1"]
    elif "OUTPUT_branding_scope_1" in output:
        pred = output["OUTPUT_branding_scope_1"]
    else:
        pred = None

    # Get expected - check both possible field names
    if "branding_scope_1" in expected:
        actual = expected["branding_scope_1"]
    elif "OUTPUT_branding_scope_1" in expected:
        actual = expected["OUTPUT_branding_scope_1"]
    else:
        actual = None

    # Normalize null values (handle "null" string vs None)
    pred = normalize_null(pred)
    actual = normalize_null(actual)

    return 1.0 if pred == actual else 0.0


# ═══════════════════════════════════════════════════════════════════════════
# M4 EXACT: Did the model correctly classify Competitor Brand (CB) vs null?
# 1.0 = correct, 0.0 = wrong
# ═══════════════════════════════════════════════════════════════════════════
def m4_correct_handler(output: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """M4: Competitor Brand (CB/null)"""
    if output is None or expected is None:
        return 0.0

    # Get prediction - check both possible field names
    if "branding_scope_2" in output:
        pred = output["branding_scope_2"]
    elif "OUTPUT_branding_scope_2" in output:
        pred = output["OUTPUT_branding_scope_2"]
    else:
        pred = None

    # Get expected - check both possible field names
    if "branding_scope_2" in expected:
        actual = expected["branding_scope_2"]
    elif "OUTPUT_branding_scope_2" in expected:
        actual = expected["OUTPUT_branding_scope_2"]
    else:
        actual = None

    # Normalize null values
    pred = normalize_null(pred)
    actual = normalize_null(actual)

    return 1.0 if pred == actual else 0.0


# ═══════════════════════════════════════════════════════════════════════════
# M5 EXACT: Did the model correctly classify Non-Branded (NB) vs null?
# 1.0 = correct, 0.0 = wrong
# ═══════════════════════════════════════════════════════════════════════════
def m5_correct_handler(output: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """M5: Non-Branded (NB/null)"""
    if output is None or expected is None:
        return 0.0

    # Get prediction - check both possible field names
    if "branding_scope_3" in output:
        pred = output["branding_scope_3"]
    elif "OUTPUT_branding_scope_3" in output:
        pred = output["OUTPUT_branding_scope_3"]
    else:
        pred = None

    # Get expected - check both possible field names
    if "branding_scope_3" in expected:
        actual = expected["branding_scope_3"]
    elif "OUTPUT_branding_scope_3" in expected:
        actual = expected["OUTPUT_branding_scope_3"]
    else:
        actual = None

    # Normalize null values
    pred = normalize_null(pred)
    actual = normalize_null(actual)

    return 1.0 if pred == actual else 0.0


# ═══════════════════════════════════════════════════════════════════════════
# M9 EXACT: Did the model correctly classify Relevant (R) vs null?
# 1.0 = correct, 0.0 = wrong
# ═══════════════════════════════════════════════════════════════════════════
def m9_correct_handler(output: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """M9: Relevant (R/null)"""
    if output is None or expected is None:
        return 0.0

    # Get prediction - check both possible field names
    if "relationship_R" in output:
        pred = output["relationship_R"]
    elif "OUTPUT_relationship_R" in output:
        pred = output["OUTPUT_relationship_R"]
    else:
        pred = None

    # Get expected - check both possible field names
    if "relationship_R" in expected:
        actual = expected["relationship_R"]
    elif "OUTPUT_relationship_R" in expected:
        actual = expected["OUTPUT_relationship_R"]
    else:
        actual = None

    # Normalize null values
    pred = normalize_null(pred)
    actual = normalize_null(actual)

    return 1.0 if pred == actual else 0.0


# ═══════════════════════════════════════════════════════════════════════════
# M10 EXACT: Did the model correctly classify Negative (N) vs null?
# 1.0 = correct, 0.0 = wrong
# ═══════════════════════════════════════════════════════════════════════════
def m10_correct_handler(output: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """M10: Negative (N/null)"""
    if output is None or expected is None:
        return 0.0

    # Get prediction - check both possible field names
    if "relationship_N" in output:
        pred = output["relationship_N"]
    elif "OUTPUT_relationship_N" in output:
        pred = output["OUTPUT_relationship_N"]
    else:
        pred = None

    # Get expected - check both possible field names
    if "relationship_N" in expected:
        actual = expected["relationship_N"]
    elif "OUTPUT_relationship_N" in expected:
        actual = expected["OUTPUT_relationship_N"]
    else:
        actual = None

    # Normalize null values
    pred = normalize_null(pred)
    actual = normalize_null(actual)

    return 1.0 if pred == actual else 0.0


# ═══════════════════════════════════════════════════════════════════════════
# M11 EXACT: Did the model correctly classify Substitute (S) vs null?
# 1.0 = correct, 0.0 = wrong
# ═══════════════════════════════════════════════════════════════════════════
def m11_correct_handler(output: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """M11: Substitute (S/null)"""
    if output is None or expected is None:
        return 0.0

    # Get prediction - check both possible field names
    if "relationship_S" in output:
        pred = output["relationship_S"]
    elif "OUTPUT_relationship_S" in output:
        pred = output["OUTPUT_relationship_S"]
    else:
        pred = None

    # Get expected - check both possible field names
    if "relationship_S" in expected:
        actual = expected["relationship_S"]
    elif "OUTPUT_relationship_S" in expected:
        actual = expected["OUTPUT_relationship_S"]
    else:
        actual = None

    # Normalize null values
    pred = normalize_null(pred)
    actual = normalize_null(actual)

    return 1.0 if pred == actual else 0.0


# ═══════════════════════════════════════════════════════════════════════════
# M12 EXACT: Hard Constraint Violation Check
# expected.relevancy == "N" → output.classification should be "N"
# expected.relevancy != "N" → output.classification should be null (pass to M13)
# ═══════════════════════════════════════════════════════════════════════════
def m12_correct_handler(output: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """M12: Hard Constraint Check - N (violated) or null (pass)"""
    if output is None or expected is None:
        return 0.0

    # Get expected relevancy
    exp_relevancy = expected.get("relevancy")
    exp_relevancy = normalize_null(exp_relevancy)

    # Get model prediction - from classification field
    pred = output.get("classification")
    pred = normalize_null(pred)

    # M12 logic: only outputs N (violation) or null (pass to M13)
    # If expected is N, model should output N
    # If expected is not N (Null/R/S/C), model should output null
    if exp_relevancy == "N":
        return 1.0 if pred == "N" else 0.0
    else:
        return 1.0 if pred is None else 0.0


# ═══════════════════════════════════════════════════════════════════════════
# M13 EXACT: Product Type Check
# expected.same_type (boolean) == output.same_type (boolean)
# ═══════════════════════════════════════════════════════════════════════════
def m13_correct_handler(output: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """M13: Product Type Check - same_type boolean"""
    if output is None or expected is None:
        return 0.0

    # Get expected same_type (boolean)
    exp_same_type = expected.get("same_type")

    # Get model prediction - from same_type or step2_product_type.same_type
    pred = output.get("same_type")
    if pred is None and "step2_product_type" in output:
        pred = output["step2_product_type"].get("same_type")

    # Compare booleans
    if exp_same_type is None or pred is None:
        return 0.0

    return 1.0 if bool(exp_same_type) == bool(pred) else 0.0


# ═══════════════════════════════════════════════════════════════════════════
# M14 EXACT: Primary Use Check (Same Type)
# expected.relevancy (R or N) == output.classification (R or N)
# ═══════════════════════════════════════════════════════════════════════════
def m14_correct_handler(output: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """M14: Primary Use Check - R (relevant) or N (different use)"""
    if output is None or expected is None:
        return 0.0

    # Get expected relevancy (R or N)
    exp_relevancy = expected.get("relevancy")
    exp_relevancy = normalize_null(exp_relevancy)

    # Get model prediction
    pred = output.get("classification")
    pred = normalize_null(pred)

    return 1.0 if pred == exp_relevancy else 0.0


# ═══════════════════════════════════════════════════════════════════════════
# M15 EXACT: Substitute Check
# expected.relevancy == "S" → output.classification should be "S"
# expected.relevancy != "S" → output.classification should be null (pass to M16)
# ═══════════════════════════════════════════════════════════════════════════
def m15_correct_handler(output: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """M15: Substitute Check - S (substitute) or null (pass to M16)"""
    if output is None or expected is None:
        return 0.0

    # Get expected relevancy
    exp_relevancy = expected.get("relevancy")
    exp_relevancy = normalize_null(exp_relevancy)

    # Get model prediction
    pred = output.get("classification")
    pred = normalize_null(pred)

    # M15 logic: only outputs S or null
    if exp_relevancy == "S":
        return 1.0 if pred == "S" else 0.0
    else:
        return 1.0 if pred is None else 0.0


# ═══════════════════════════════════════════════════════════════════════════
# M16 EXACT: Complementary Check
# expected.relevancy (C or N) == output.classification (C or N)
# ═══════════════════════════════════════════════════════════════════════════
def m16_correct_handler(output: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """M16: Complementary Check - C (complementary) or N (negative)"""
    if output is None or expected is None:
        return 0.0

    # Get expected relevancy (C or N)
    exp_relevancy = expected.get("relevancy")
    exp_relevancy = normalize_null(exp_relevancy)

    # Get model prediction
    pred = output.get("classification")
    pred = normalize_null(pred)

    return 1.0 if pred == exp_relevancy else 0.0


# =============================================================================
# List Extraction Handlers
# =============================================================================


# ═══════════════════════════════════════════════════════════════════════════
# M1 RECALL: What fraction of expected brand entities did the model find?
# 1.0 = found all, 0.5 = found half, 0.0 = found none
# ═══════════════════════════════════════════════════════════════════════════
def m1_recall_handler(output: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """M1: Brand Entities Recall"""
    if output is None:
        output = {}
    if expected is None:
        expected = {}
    pred_list = output.get("brand_entities") or output.get("OUTPUT_brand_entities") or []
    exp_list = expected.get("brand_entities") or expected.get("OUTPUT_brand_entities") or []

    if not exp_list:
        return 1.0

    pred_set = {str(x).lower() for x in pred_list} if pred_list else set()
    exp_set = {str(x).lower() for x in exp_list}

    intersection = len(pred_set & exp_set)
    return intersection / len(exp_set)


# ═══════════════════════════════════════════════════════════════════════════
# M1 PRECISION: What fraction of generated entities are actually correct?
# 1.0 = all correct, 0.5 = half garbage, 0.0 = all wrong
# ═══════════════════════════════════════════════════════════════════════════
def m1_precision_handler(output: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """M1: Brand Entities Precision"""
    if output is None:
        output = {}
    if expected is None:
        expected = {}
    pred_list = output.get("brand_entities") or output.get("OUTPUT_brand_entities") or []
    exp_list = expected.get("brand_entities") or expected.get("OUTPUT_brand_entities") or []

    if not pred_list:
        return 0.0 if exp_list else 1.0

    pred_set = {str(x).lower() for x in pred_list}
    exp_set = {str(x).lower() for x in exp_list} if exp_list else set()

    intersection = len(pred_set & exp_set)
    return intersection / len(pred_set)


# ═══════════════════════════════════════════════════════════════════════════
# M1 JACCARD: How similar are predicted and expected sets? (intersection/union)
# 1.0 = identical sets, 0.5 = partial overlap, 0.0 = no overlap
# ═══════════════════════════════════════════════════════════════════════════
def m1_jaccard_handler(output: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """M1: Brand Entities Jaccard"""
    if output is None:
        output = {}
    if expected is None:
        expected = {}
    pred_list = output.get("brand_entities") or output.get("OUTPUT_brand_entities") or []
    exp_list = expected.get("brand_entities") or expected.get("OUTPUT_brand_entities") or []

    pred_set = {str(x).lower() for x in pred_list} if pred_list else set()
    exp_set = {str(x).lower() for x in exp_list} if exp_list else set()

    union = pred_set | exp_set
    if not union:
        return 1.0

    intersection = pred_set & exp_set
    return len(intersection) / len(union)


# =============================================================================
# M1 Quality Scorers - detect product word contamination
# =============================================================================

PRODUCT_WORDS = {
    # Kitchen
    "oven", "mitt", "mitts", "glove", "gloves", "pot", "pan", "holder", "set", "pack",
    "kitchen", "sink", "caddy", "organizer", "dispenser", "sponge", "silicone", "ribbed",
    # Apparel
    "jacket", "coat", "puffer", "shirt", "pants", "shoes", "boots", "hat", "gloves",
    "men's", "mens", "women's", "womens", "kids", "lightweight", "waterproof", "windproof",
    "packable", "insulated", "quilted", "warm", "casual", "outdoor", "travel",
    # Electronics
    "headphones", "earbuds", "speaker", "charger", "cable", "case", "mount", "stand",
    "wireless", "bluetooth", "usb", "phone", "tablet", "laptop",
    # General
    "2-pack", "3-pack", "4-pack", "pack", "set", "kit", "bundle", "combo",
    "small", "medium", "large", "xl", "xxl", "size",
}


# ═══════════════════════════════════════════════════════════════════════════
# M1 PURITY: What fraction of entities contain NO product words (oven, mitt)?
# 1.0 = all pure brands, 0.3 = 70% contaminated with product terms
# ═══════════════════════════════════════════════════════════════════════════
def m1_purity_handler(output: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """M1: Brand Purity - percentage of entities WITHOUT product words.

    Score of 1.0 = all entities are pure brand names
    Score of 0.0 = all entities contain product words (bad)
    """
    if output is None:
        return 0.0

    entities = output.get("brand_entities") or output.get("OUTPUT_brand_entities") or []
    if not entities:
        return 1.0  # No entities = no contamination

    pure_count = 0
    for entity in entities:
        entity_lower = str(entity).lower()
        words = entity_lower.split()
        # Check if any word in entity is a product word
        has_product_word = any(word in PRODUCT_WORDS for word in words)
        if not has_product_word:
            pure_count += 1

    return pure_count / len(entities)


# ═══════════════════════════════════════════════════════════════════════════
# M1 LENGTH COMPLIANCE: What fraction of entities have ≤3 words?
# 1.0 = all proper length, 0.5 = half are too long (4+ words)
# ═══════════════════════════════════════════════════════════════════════════
def m1_length_violation_handler(output: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """M1: Length Compliance - percentage of entities with 3 or fewer words.

    Brand entities should be 1-3 words. 4+ words = likely product description.
    Score of 1.0 = all entities are proper length
    Score of 0.0 = all entities are too long (bad)
    """
    if output is None:
        return 0.0

    entities = output.get("brand_entities") or output.get("OUTPUT_brand_entities") or []
    if not entities:
        return 1.0

    compliant_count = 0
    for entity in entities:
        word_count = len(str(entity).split())
        if word_count <= 3:
            compliant_count += 1

    return compliant_count / len(entities)


# ═══════════════════════════════════════════════════════════════════════════
# M1 AVG LENGTH: Normalized score based on average words per entity
# 1.0 = ideal (1-2 words), 0.5 = borderline (3-4 words), 0.0 = too long (6+ words)
# ═══════════════════════════════════════════════════════════════════════════
def m1_avg_length_handler(output: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """M1: Average Word Count - normalized score based on average entity length.

    Ideal: 1-2 words (score = 1.0)
    Acceptable: 2-3 words (score = 0.7-1.0)
    Bad: 4+ words (score drops significantly)

    Returns 1.0 - (avg_words - 1.5) / 5, clamped to [0, 1]
    """
    if output is None:
        return 0.0

    entities = output.get("brand_entities") or output.get("OUTPUT_brand_entities") or []
    if not entities:
        return 1.0

    total_words = sum(len(str(e).split()) for e in entities)
    avg_words = total_words / len(entities)

    # Score: ideal is 1.5 words, penalty for longer
    # avg=1.5 -> score=1.0, avg=6.5 -> score=0.0
    score = 1.0 - (avg_words - 1.5) / 5.0
    return max(0.0, min(1.0, score))


# ═══════════════════════════════════════════════════════════════════════════
# M3 RECALL: What fraction of expected competitor entities did the model find?
# 1.0 = found all, 0.5 = found half, 0.0 = found none
# ═══════════════════════════════════════════════════════════════════════════
def m3_recall_handler(output: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """M3: Competitor Entities Recall"""
    if output is None:
        output = {}
    if expected is None:
        expected = {}
    pred_list = output.get("competitor_entities") or output.get("OUTPUT_competitor_entities") or []
    exp_list = expected.get("competitor_entities") or expected.get("OUTPUT_competitor_entities") or []

    if not exp_list:
        return 1.0

    pred_set = {str(x).lower() for x in pred_list} if pred_list else set()
    exp_set = {str(x).lower() for x in exp_list}

    intersection = len(pred_set & exp_set)
    return intersection / len(exp_set)


# =============================================================================
# Taxonomy Handlers (M6)
# =============================================================================


# ═══════════════════════════════════════════════════════════════════════════
# M6 LEVEL1: Did the model predict correct top-level category?
# 1.0 = correct category, 0.0 = wrong category
# ═══════════════════════════════════════════════════════════════════════════
def m6_level1_handler(output: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """M6: Level 1 Accuracy"""
    if output is None:
        output = {}
    if expected is None:
        expected = {}
    pred_taxonomy = output.get("taxonomy") or output.get("OUTPUT_taxonomy") or []
    exp_taxonomy = expected.get("taxonomy") or expected.get("OUTPUT_taxonomy") or []

    if isinstance(pred_taxonomy, str):
        pred_taxonomy = [{"level": i+1, "product_type": t.strip()} for i, t in enumerate(pred_taxonomy.split(","))]
    if isinstance(exp_taxonomy, str):
        exp_taxonomy = [{"level": i+1, "product_type": t.strip()} for i, t in enumerate(exp_taxonomy.split(","))]

    pred_at_level = {t.get("product_type", "").lower() for t in pred_taxonomy if t.get("level") == 1}
    exp_at_level = {t.get("product_type", "").lower() for t in exp_taxonomy if t.get("level") == 1}

    if not exp_at_level:
        return 1.0 if not pred_at_level else 0.0

    return len(pred_at_level & exp_at_level) / len(exp_at_level)


# ═══════════════════════════════════════════════════════════════════════════
# M6 LEVEL2: Did the model predict correct sub-category?
# 1.0 = correct sub-category, 0.0 = wrong sub-category
# ═══════════════════════════════════════════════════════════════════════════
def m6_level2_handler(output: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """M6: Level 2 Accuracy"""
    if output is None:
        output = {}
    if expected is None:
        expected = {}
    pred_taxonomy = output.get("taxonomy") or output.get("OUTPUT_taxonomy") or []
    exp_taxonomy = expected.get("taxonomy") or expected.get("OUTPUT_taxonomy") or []

    if isinstance(pred_taxonomy, str):
        pred_taxonomy = [{"level": i+1, "product_type": t.strip()} for i, t in enumerate(pred_taxonomy.split(","))]
    if isinstance(exp_taxonomy, str):
        exp_taxonomy = [{"level": i+1, "product_type": t.strip()} for i, t in enumerate(exp_taxonomy.split(","))]

    pred_at_level = {t.get("product_type", "").lower() for t in pred_taxonomy if t.get("level") == 2}
    exp_at_level = {t.get("product_type", "").lower() for t in exp_taxonomy if t.get("level") == 2}

    if not exp_at_level:
        return 1.0 if not pred_at_level else 0.0

    return len(pred_at_level & exp_at_level) / len(exp_at_level)


# =============================================================================
# Multi-Field Handlers (M7)
# =============================================================================


# ═══════════════════════════════════════════════════════════════════════════
# M7 VARIANTS: What fraction of expected product variants did the model find?
# 1.0 = found all variants, 0.5 = found half, 0.0 = found none
# ═══════════════════════════════════════════════════════════════════════════
def m7_variants_handler(output: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """M7: Variants Recall"""
    if output is None:
        output = {}
    if expected is None:
        expected = {}
    pred_list = output.get("variants") or output.get("OUTPUT_variants") or []
    exp_list = expected.get("variants") or expected.get("OUTPUT_variants") or []

    if not exp_list:
        return 1.0

    pred_set = {str(x).lower() for x in pred_list} if pred_list else set()
    exp_set = {str(x).lower() for x in exp_list}

    return len(pred_set & exp_set) / len(exp_set)


# ═══════════════════════════════════════════════════════════════════════════
# M7 USECASES: What fraction of expected use cases did the model find?
# 1.0 = found all use cases, 0.5 = found half, 0.0 = found none
# ═══════════════════════════════════════════════════════════════════════════
def m7_usecases_handler(output: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """M7: Use Cases Recall"""
    if output is None:
        output = {}
    if expected is None:
        expected = {}
    pred_list = output.get("use_cases") or output.get("OUTPUT_use_cases") or []
    exp_list = expected.get("use_cases") or expected.get("OUTPUT_use_cases") or []

    if not exp_list:
        return 1.0

    pred_set = {str(x).lower() for x in pred_list} if pred_list else set()
    exp_set = {str(x).lower() for x in exp_list}

    return len(pred_set & exp_set) / len(exp_set)


# =============================================================================
# Ranking Handler (M8)
# =============================================================================


# ═══════════════════════════════════════════════════════════════════════════
# M8 NDCG@5: How well does predicted ranking match expected? (top 5 items)
# 1.0 = perfect ranking, 0.5 = partially correct, 0.0 = completely wrong order
# ═══════════════════════════════════════════════════════════════════════════
def m8_ndcg5_handler(output: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """M8: NDCG@5"""
    if output is None:
        output = {}
    if expected is None:
        expected = {}
    pred_table = output.get("attribute_table") or output.get("OUTPUT_attribute_table") or []
    exp_table = expected.get("attribute_table") or expected.get("OUTPUT_attribute_table") or []

    if not exp_table:
        return 1.0 if not pred_table else 0.0

    exp_ranks = {}
    for item in exp_table:
        key = (item.get("attribute_type", ""), str(item.get("attribute_value", "")).lower())
        exp_ranks[key] = item.get("rank", 999)

    max_rank = max(exp_ranks.values()) if exp_ranks else 1

    pred_relevances = []
    for item in sorted(pred_table, key=lambda x: x.get("rank", 999)):
        key = (item.get("attribute_type", ""), str(item.get("attribute_value", "")).lower())
        exp_rank = exp_ranks.get(key, max_rank + 1)
        pred_relevances.append(max(0, max_rank - exp_rank + 1))

    def dcg(rels, k):
        return sum(r / math.log2(i + 2) for i, r in enumerate(rels[:k]))

    ideal = sorted(pred_relevances, reverse=True)
    dcg_val = dcg(pred_relevances, 5)
    idcg_val = dcg(ideal, 5)

    return dcg_val / idcg_val if idcg_val > 0 else 0.0


# =============================================================================
# Register Scorers
# =============================================================================

# Binary Classification
project.scorers.create(
    name="M2 Correct (OB)",
    slug="m2-correct",
    description="Binary: Own Brand (OB) vs null",
    parameters=BinaryInput,
    handler=m2_correct_handler,
)

project.scorers.create(
    name="M4 Correct (CB)",
    slug="m4-correct",
    description="Binary: Competitor Brand (CB) vs null",
    parameters=BinaryInput,
    handler=m4_correct_handler,
)

project.scorers.create(
    name="M5 Correct (NB)",
    slug="m5-correct",
    description="Binary: Non-Branded (NB) vs null",
    parameters=BinaryInput,
    handler=m5_correct_handler,
)

project.scorers.create(
    name="M9 Correct (R)",
    slug="m9-correct",
    description="Binary: Relevant (R) vs null",
    parameters=BinaryInput,
    handler=m9_correct_handler,
)

project.scorers.create(
    name="M10 Correct (N)",
    slug="m10-correct",
    description="Binary: Negative (N) vs null",
    parameters=BinaryInput,
    handler=m10_correct_handler,
)

project.scorers.create(
    name="M11 Correct (S)",
    slug="m11-correct",
    description="Binary: Substitute (S) vs null",
    parameters=BinaryInput,
    handler=m11_correct_handler,
)

project.scorers.create(
    name="M12 Correct (C)",
    slug="m12-correct",
    description="Binary: Complementary (C) vs null",
    parameters=BinaryInput,
    handler=m12_correct_handler,
)

# List Extraction
project.scorers.create(
    name="M1 Recall",
    slug="m1-recall",
    description="Brand entities recall",
    parameters=ListInput,
    handler=m1_recall_handler,
)

project.scorers.create(
    name="M1 Precision",
    slug="m1-precision",
    description="Brand entities precision",
    parameters=ListInput,
    handler=m1_precision_handler,
)

project.scorers.create(
    name="M1 Jaccard",
    slug="m1-jaccard",
    description="Brand entities Jaccard similarity",
    parameters=ListInput,
    handler=m1_jaccard_handler,
)

# M1 Quality Scorers
project.scorers.create(
    name="M1 Purity",
    slug="m1-purity",
    description="Brand purity - % of entities without product words (1.0 = all pure brand names)",
    parameters=ListInput,
    handler=m1_purity_handler,
)

project.scorers.create(
    name="M1 Length Compliance",
    slug="m1-length-compliance",
    description="Length compliance - % of entities with ≤3 words (1.0 = all proper length)",
    parameters=ListInput,
    handler=m1_length_violation_handler,
)

project.scorers.create(
    name="M1 Avg Length",
    slug="m1-avg-length",
    description="Average word count score (1.0 = ideal 1-2 words, drops for longer entities)",
    parameters=ListInput,
    handler=m1_avg_length_handler,
)

project.scorers.create(
    name="M3 Recall",
    slug="m3-recall",
    description="Competitor entities recall",
    parameters=ListInput,
    handler=m3_recall_handler,
)

def m3_precision_handler(output: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """M3: Competitor Entities Precision"""
    if output is None:
        output = {}
    if expected is None:
        expected = {}
    pred_list = output.get("competitor_entities") or output.get("OUTPUT_competitor_entities") or []
    exp_list = expected.get("competitor_entities") or expected.get("OUTPUT_competitor_entities") or []
    if not pred_list:
        return 0.0 if exp_list else 1.0
    pred_set = {str(x).lower() for x in pred_list}
    exp_set = {str(x).lower() for x in exp_list} if exp_list else set()
    return len(pred_set & exp_set) / len(pred_set)

project.scorers.create(
    name="M3 Precision",
    slug="m3-precision",
    description="Competitor entities precision",
    parameters=ListInput,
    handler=m3_precision_handler,
)

def m3_jaccard_handler(output: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """M3: Competitor Entities Jaccard"""
    if output is None:
        output = {}
    if expected is None:
        expected = {}
    pred_list = output.get("competitor_entities") or output.get("OUTPUT_competitor_entities") or []
    exp_list = expected.get("competitor_entities") or expected.get("OUTPUT_competitor_entities") or []
    pred_set = {str(x).lower() for x in pred_list} if pred_list else set()
    exp_set = {str(x).lower() for x in exp_list} if exp_list else set()
    union = pred_set | exp_set
    if not union:
        return 1.0
    return len(pred_set & exp_set) / len(union)

project.scorers.create(
    name="M3 Jaccard",
    slug="m3-jaccard",
    description="Competitor entities Jaccard similarity",
    parameters=ListInput,
    handler=m3_jaccard_handler,
)

# Taxonomy
project.scorers.create(
    name="M6 Level1",
    slug="m6-level1",
    description="Taxonomy level 1 accuracy",
    parameters=TaxonomyInput,
    handler=m6_level1_handler,
)

project.scorers.create(
    name="M6 Level2",
    slug="m6-level2",
    description="Taxonomy level 2 accuracy",
    parameters=TaxonomyInput,
    handler=m6_level2_handler,
)

def m6_level3_handler(output: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """M6: Level 3 Accuracy"""
    if output is None:
        output = {}
    if expected is None:
        expected = {}
    pred_taxonomy = output.get("taxonomy") or output.get("OUTPUT_taxonomy") or []
    exp_taxonomy = expected.get("taxonomy") or expected.get("OUTPUT_taxonomy") or []
    if isinstance(pred_taxonomy, str):
        pred_taxonomy = [{"level": i+1, "product_type": t.strip()} for i, t in enumerate(pred_taxonomy.split(","))]
    if isinstance(exp_taxonomy, str):
        exp_taxonomy = [{"level": i+1, "product_type": t.strip()} for i, t in enumerate(exp_taxonomy.split(","))]
    pred_at_level = {t.get("product_type", "").lower() for t in pred_taxonomy if t.get("level") == 3}
    exp_at_level = {t.get("product_type", "").lower() for t in exp_taxonomy if t.get("level") == 3}
    if not exp_at_level:
        return 1.0 if not pred_at_level else 0.0
    return len(pred_at_level & exp_at_level) / len(exp_at_level)

project.scorers.create(
    name="M6 Level3",
    slug="m6-level3",
    description="Taxonomy level 3 accuracy",
    parameters=TaxonomyInput,
    handler=m6_level3_handler,
)

def m6_overall_handler(output: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """M6: Overall Accuracy (average of all levels)"""
    l1 = m6_level1_handler(output, expected)
    l2 = m6_level2_handler(output, expected)
    l3 = m6_level3_handler(output, expected)
    return (l1 + l2 + l3) / 3

project.scorers.create(
    name="M6 Overall",
    slug="m6-overall",
    description="Taxonomy overall accuracy (avg of levels)",
    parameters=TaxonomyInput,
    handler=m6_overall_handler,
)

# Multi-field
project.scorers.create(
    name="M7 Variants",
    slug="m7-variants",
    description="Product variants recall",
    parameters=ListInput,
    handler=m7_variants_handler,
)

project.scorers.create(
    name="M7 UseCases",
    slug="m7-usecases",
    description="Use cases recall",
    parameters=ListInput,
    handler=m7_usecases_handler,
)

def m7_audiences_handler(output: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """M7: Audiences Recall"""
    if output is None:
        output = {}
    if expected is None:
        expected = {}
    pred_list = output.get("audiences") or output.get("OUTPUT_audiences") or []
    exp_list = expected.get("audiences") or expected.get("OUTPUT_audiences") or []
    if not exp_list:
        return 1.0
    pred_set = {str(x).lower() for x in pred_list} if pred_list else set()
    exp_set = {str(x).lower() for x in exp_list}
    return len(pred_set & exp_set) / len(exp_set)

project.scorers.create(
    name="M7 Audiences",
    slug="m7-audiences",
    description="Target audiences recall",
    parameters=ListInput,
    handler=m7_audiences_handler,
)

def m7_overall_handler(output: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """M7: Overall Recall (average of all fields)"""
    v = m7_variants_handler(output, expected)
    u = m7_usecases_handler(output, expected)
    a = m7_audiences_handler(output, expected)
    return (v + u + a) / 3

project.scorers.create(
    name="M7 Overall",
    slug="m7-overall",
    description="Overall attributes recall (avg of fields)",
    parameters=ListInput,
    handler=m7_overall_handler,
)

# Ranking
project.scorers.create(
    name="M8 NDCG@5",
    slug="m8-ndcg5",
    description="Attribute ranking NDCG@5",
    parameters=RankingInput,
    handler=m8_ndcg5_handler,
)

def m8_ndcg10_handler(output: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """M8: NDCG@10"""
    if output is None:
        output = {}
    if expected is None:
        expected = {}
    pred_table = output.get("attribute_table") or output.get("OUTPUT_attribute_table") or []
    exp_table = expected.get("attribute_table") or expected.get("OUTPUT_attribute_table") or []
    if not exp_table:
        return 1.0 if not pred_table else 0.0
    exp_ranks = {}
    for item in exp_table:
        key = (item.get("attribute_type", ""), str(item.get("attribute_value", "")).lower())
        exp_ranks[key] = item.get("rank", 999)
    max_rank = max(exp_ranks.values()) if exp_ranks else 1
    pred_relevances = []
    for item in sorted(pred_table, key=lambda x: x.get("rank", 999)):
        key = (item.get("attribute_type", ""), str(item.get("attribute_value", "")).lower())
        exp_rank = exp_ranks.get(key, max_rank + 1)
        pred_relevances.append(max(0, max_rank - exp_rank + 1))
    def dcg(rels, k):
        return sum(r / math.log2(i + 2) for i, r in enumerate(rels[:k]))
    ideal = sorted(pred_relevances, reverse=True)
    dcg_val = dcg(pred_relevances, 10)
    idcg_val = dcg(ideal, 10)
    return dcg_val / idcg_val if idcg_val > 0 else 0.0

project.scorers.create(
    name="M8 NDCG@10",
    slug="m8-ndcg10",
    description="Attribute ranking NDCG@10",
    parameters=RankingInput,
    handler=m8_ndcg10_handler,
)


# =============================================================================
# Entity Overlap Scorers (M1, M3, M6 - fuzzy matching)
# =============================================================================

class EntityOverlapInput(pydantic.BaseModel):
    input: Dict[str, Any]
    output: Dict[str, Any]
    expected: Optional[Dict[str, Any]] = None


def normalize_entity(entity: str) -> str:
    """Normalize entity for comparison."""
    if not entity:
        return ""
    return entity.lower().strip().replace("-", " ").replace("_", " ")


def entities_match(entity1: str, entity2: str) -> bool:
    """Check if two entities match (fuzzy)."""
    e1 = normalize_entity(entity1)
    e2 = normalize_entity(entity2)

    if not e1 or not e2:
        return False

    # Exact match
    if e1 == e2:
        return True

    # One contains the other
    if e1 in e2 or e2 in e1:
        return True

    # Check word overlap
    words1 = set(e1.split())
    words2 = set(e2.split())
    if words1 and words2:
        overlap = words1 & words2
        min_words = min(len(words1), len(words2))
        if min_words > 0 and len(overlap) >= min_words * 0.5:
            return True

    return False


def calculate_entity_overlap(expected: List, got: List) -> Dict[str, Any]:
    """Calculate overlap between expected and extracted entities."""
    if not expected:
        expected = []
    if not got:
        got = []

    expected_clean = [e for e in expected if e and isinstance(e, str)]
    got_clean = [g for g in got if g and isinstance(g, str)]

    if not expected_clean and not got_clean:
        return {"recall": 1.0, "precision": 1.0, "f1": 1.0, "matched_count": 0, "expected_count": 0, "got_count": 0}

    matched_expected = set()
    matched_got = set()

    for i, exp in enumerate(expected_clean):
        for j, g in enumerate(got_clean):
            if entities_match(exp, g):
                matched_expected.add(i)
                matched_got.add(j)

    recall = len(matched_expected) / len(expected_clean) if expected_clean else 1.0
    precision = len(matched_got) / len(got_clean) if got_clean else 1.0

    if precision + recall > 0:
        f1 = 2 * (precision * recall) / (precision + recall)
    else:
        f1 = 0.0

    return {"recall": recall, "precision": precision, "f1": f1, "matched_count": len(matched_expected), "expected_count": len(expected_clean), "got_count": len(got_clean)}


def m1_entity_overlap_handler(
    input: Dict[str, Any],
    output: Dict[str, Any],
    expected: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Optional[float]:
    """M1: Score brand entity extraction using overlap matching."""
    if not output or not expected:
        return None

    expected_entities = expected.get("brand_entities", [])
    got_entities = output.get("brand_entities", [])

    metrics = calculate_entity_overlap(expected_entities, got_entities)
    return metrics["f1"]


project.scorers.create(
    name="M1 Entity Overlap",
    slug="m1-entity-overlap",
    description="M1: Own Brand Entity extraction with overlap scoring (F1-based, not exact match)",
    parameters=EntityOverlapInput,
    handler=m1_entity_overlap_handler,
)


def m3_entity_overlap_handler(
    input: Dict[str, Any],
    output: Dict[str, Any],
    expected: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Optional[float]:
    """M3: Score competitor entity extraction using overlap matching."""
    if not output or not expected:
        return None

    expected_entities = expected.get("competitor_entities", [])
    got_entities = output.get("competitor_entities", [])

    metrics = calculate_entity_overlap(expected_entities, got_entities)
    return metrics["f1"]


project.scorers.create(
    name="M3 Entity Overlap",
    slug="m3-entity-overlap",
    description="M3: Competitor Entity extraction with overlap scoring (F1-based, not exact match)",
    parameters=EntityOverlapInput,
    handler=m3_entity_overlap_handler,
)


def flatten_taxonomy(items) -> List[str]:
    """Flatten taxonomy structure to list of product_type strings."""
    result = []
    if not items:
        return result

    for item in items:
        if isinstance(item, dict):
            pt = item.get("product_type", "")
            if pt:
                result.append(pt)
        elif isinstance(item, list):
            result.extend(flatten_taxonomy(item))
        elif isinstance(item, str) and item:
            result.append(item)

    return result


def taxonomy_items_match(item1: str, item2: str) -> bool:
    """Check if two taxonomy items match semantically."""
    i1 = item1.lower().strip() if item1 else ""
    i2 = item2.lower().strip() if item2 else ""

    if not i1 or not i2:
        return False

    if i1 == i2:
        return True

    if i1 in i2 or i2 in i1:
        return True

    words1 = set(i1.split())
    words2 = set(i2.split())
    stop_words = {"and", "or", "the", "a", "an", "of", "for", "with", "in", "on", "&"}
    words1 = words1 - stop_words
    words2 = words2 - stop_words

    if words1 and words2 and (words1 & words2):
        return True

    return False


def calculate_taxonomy_overlap(expected: List, got: List) -> Dict[str, Any]:
    """Calculate overlap between expected and generated taxonomy."""
    expected_flat = flatten_taxonomy(expected)
    got_flat = flatten_taxonomy(got)

    if not expected_flat and not got_flat:
        return {"recall": 1.0, "precision": 1.0, "f1": 1.0}

    matched_expected = set()
    matched_got = set()

    for i, exp in enumerate(expected_flat):
        for j, g in enumerate(got_flat):
            if taxonomy_items_match(exp, g):
                matched_expected.add(i)
                matched_got.add(j)

    recall = len(matched_expected) / len(expected_flat) if expected_flat else 1.0
    precision = len(matched_got) / len(got_flat) if got_flat else 1.0

    if precision + recall > 0:
        f1 = 2 * (precision * recall) / (precision + recall)
    else:
        f1 = 0.0

    return {"recall": recall, "precision": precision, "f1": f1}


def m6_taxonomy_overlap_handler(
    input: Dict[str, Any],
    output: Dict[str, Any],
    expected: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Optional[float]:
    """M6: Score taxonomy generation using semantic overlap."""
    if not output or not expected:
        return None

    expected_taxonomy = expected.get("product_type_taxonomy", [])
    got_taxonomy = output.get("product_type_taxonomy", [])

    metrics = calculate_taxonomy_overlap(expected_taxonomy, got_taxonomy)

    if metrics["recall"] >= 0.9:
        return max(0.9, metrics["f1"])
    elif metrics["recall"] >= 0.7:
        return max(0.7, metrics["f1"])
    else:
        return metrics["f1"]


project.scorers.create(
    name="M6 Taxonomy Overlap",
    slug="m6-taxonomy-overlap",
    description="M6: Taxonomy generation with semantic overlap (allows richer output, recall-focused)",
    parameters=EntityOverlapInput,
    handler=m6_taxonomy_overlap_handler,
)


# =============================================================================
# V3 PIPELINE SCORERS (M02_V3, M04_V3, M05_V3)
# =============================================================================
# These use the new field name "branding_scope" instead of "branding_scope_1/2/3"

def m02_v3_correct_handler(output: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """M02_V3: Own Brand (OB/null) using new field names."""
    if output is None or expected is None:
        return 0.0

    # V3 uses "branding_scope" (not "branding_scope_1")
    pred = output.get("branding_scope") or output.get("branding_scope_1")
    actual = expected.get("branding_scope_1") or expected.get("branding_scope")

    pred = normalize_null(pred)
    actual = normalize_null(actual)

    return 1.0 if pred == actual else 0.0


def m04_v3_correct_handler(output: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """M04_V3: Competitor Brand (CB/null) using new field names."""
    if output is None or expected is None:
        return 0.0

    # V3 uses "branding_scope" (not "branding_scope_2")
    pred = output.get("branding_scope") or output.get("branding_scope_2")
    actual = expected.get("branding_scope_2") or expected.get("branding_scope")

    pred = normalize_null(pred)
    actual = normalize_null(actual)

    return 1.0 if pred == actual else 0.0


def m05_v3_correct_handler(output: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """M05_V3: Non-Branded (NB/null) using new field names."""
    if output is None or expected is None:
        return 0.0

    # V3 uses "branding_scope" (not "branding_scope_3")
    pred = output.get("branding_scope") or output.get("branding_scope_3")
    actual = expected.get("branding_scope_3") or expected.get("branding_scope")

    pred = normalize_null(pred)
    actual = normalize_null(actual)

    return 1.0 if pred == actual else 0.0


def m02_v3_confidence_handler(output: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """M02_V3: Confidence calibration - penalize overconfident wrong answers."""
    if output is None:
        return 0.0

    pred = output.get("branding_scope") or output.get("branding_scope_1")
    actual = expected.get("branding_scope_1") or expected.get("branding_scope")
    confidence = output.get("confidence", 0.5)

    pred = normalize_null(pred)
    actual = normalize_null(actual)

    is_correct = pred == actual

    if is_correct:
        return confidence  # Reward high confidence when correct
    else:
        return 1.0 - confidence  # Penalize high confidence when wrong


def m02_v3_matched_term_handler(output: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """M02_V3: Check if matched_term is valid when OB is classified."""
    if output is None:
        return 0.0

    pred = output.get("branding_scope") or output.get("branding_scope_1")
    matched_term = output.get("matched_term")

    pred = normalize_null(pred)

    if pred == "OB":
        # Must have a matched_term
        return 1.0 if matched_term and matched_term != "null" else 0.0
    else:
        # null classification - matched_term should be null/empty
        return 1.0 if not matched_term or matched_term == "null" else 0.5


def m04_v3_competitor_match_handler(output: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """M04_V3: Check if matched_competitor is valid when CB is classified."""
    if output is None:
        return 0.0

    pred = output.get("branding_scope") or output.get("branding_scope_2")
    matched_competitor = output.get("matched_competitor")

    pred = normalize_null(pred)

    if pred == "CB":
        return 1.0 if matched_competitor and matched_competitor != "null" else 0.0
    else:
        return 1.0 if not matched_competitor or matched_competitor == "null" else 0.5


# Register V3 scorers
project.scorers.create(
    name="M02_V3 Correct",
    slug="m02-v3-correct",
    description="M02_V3: Own Brand classification accuracy (V3 pipeline with branding_scope field)",
    parameters=BinaryInput,
    handler=m02_v3_correct_handler,
)

project.scorers.create(
    name="M04_V3 Correct",
    slug="m04-v3-correct",
    description="M04_V3: Competitor Brand classification accuracy (V3 pipeline)",
    parameters=BinaryInput,
    handler=m04_v3_correct_handler,
)

project.scorers.create(
    name="M05_V3 Correct",
    slug="m05-v3-correct",
    description="M05_V3: Non-Branded classification accuracy (V3 pipeline)",
    parameters=BinaryInput,
    handler=m05_v3_correct_handler,
)

project.scorers.create(
    name="M02_V3 Confidence",
    slug="m02-v3-confidence",
    description="M02_V3: Confidence calibration - rewards correct high-confidence, penalizes wrong high-confidence",
    parameters=BinaryInput,
    handler=m02_v3_confidence_handler,
)

project.scorers.create(
    name="M02_V3 Matched Term",
    slug="m02-v3-matched-term",
    description="M02_V3: Validates matched_term field is present when OB, absent when null",
    parameters=BinaryInput,
    handler=m02_v3_matched_term_handler,
)

project.scorers.create(
    name="M04_V3 Competitor Match",
    slug="m04-v3-competitor-match",
    description="M04_V3: Validates matched_competitor field is present when CB, absent when null",
    parameters=BinaryInput,
    handler=m04_v3_competitor_match_handler,
)


# =============================================================================
# M12-M16 RELEVANCY SCORERS (for V1.1 classification pipeline)
# =============================================================================

def m12_relevancy_handler(output: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """M12: Hard constraint violation check - returns N if violated."""
    if output is None or expected is None:
        return 0.0

    # M12 output has "classification" field
    pred = output.get("classification") or output.get("relevancy")
    actual = expected.get("relevancy") or expected.get("classification")

    pred = normalize_null(pred)
    actual = normalize_null(actual)

    return 1.0 if pred == actual else 0.0


def m13_same_type_handler(output: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """M13: Product type check - same_type boolean."""
    if output is None or expected is None:
        return 0.0

    pred = output.get("same_type")
    actual = expected.get("same_type")

    # Handle boolean vs string
    if isinstance(pred, str):
        pred = pred.lower() == "true"
    if isinstance(actual, str):
        actual = actual.lower() == "true"

    return 1.0 if pred == actual else 0.0


def m14_relevancy_handler(output: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """M14: Primary use check (same type) - returns R or passes to M16."""
    if output is None or expected is None:
        return 0.0

    pred = output.get("classification") or output.get("relevancy")
    actual = expected.get("relevancy") or expected.get("classification")

    pred = normalize_null(pred)
    actual = normalize_null(actual)

    return 1.0 if pred == actual else 0.0


def m15_relevancy_handler(output: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """M15: Substitute check - returns S or passes to M16."""
    if output is None or expected is None:
        return 0.0

    pred = output.get("classification") or output.get("relevancy")
    actual = expected.get("relevancy") or expected.get("classification")

    pred = normalize_null(pred)
    actual = normalize_null(actual)

    return 1.0 if pred == actual else 0.0


def m16_relevancy_handler(output: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """M16: Complementary check - returns C or N."""
    if output is None or expected is None:
        return 0.0

    pred = output.get("classification") or output.get("relevancy")
    actual = expected.get("relevancy") or expected.get("classification")

    pred = normalize_null(pred)
    actual = normalize_null(actual)

    return 1.0 if pred == actual else 0.0


# Register M12-M16 scorers
project.scorers.create(
    name="M12 Relevancy",
    slug="m12-relevancy",
    description="M12: Hard constraint violation check (N if violated, null otherwise)",
    parameters=BinaryInput,
    handler=m12_relevancy_handler,
)

project.scorers.create(
    name="M13 Same Type",
    slug="m13-same-type",
    description="M13: Product type check - true if same type, false if different",
    parameters=BinaryInput,
    handler=m13_same_type_handler,
)

project.scorers.create(
    name="M14 Relevancy",
    slug="m14-relevancy",
    description="M14: Primary use check (same type) - R if matches, null otherwise",
    parameters=BinaryInput,
    handler=m14_relevancy_handler,
)

project.scorers.create(
    name="M15 Relevancy",
    slug="m15-relevancy",
    description="M15: Substitute check - S if substitute, null otherwise",
    parameters=BinaryInput,
    handler=m15_relevancy_handler,
)

project.scorers.create(
    name="M16 Relevancy",
    slug="m16-relevancy",
    description="M16: Complementary check - C if complementary, N if neither",
    parameters=BinaryInput,
    handler=m16_relevancy_handler,
)


# =============================================================================
# LLM JUDGE V3 SCORERS (M07, M08, M12b)
# =============================================================================
# These scorers use GPT-4o as a judge to evaluate model outputs with detailed
# domain-specific evaluation criteria.

import json
import os
from pathlib import Path

# Only load LLM judge if OpenAI API key is available
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if OPENAI_API_KEY:
    import openai

    # Judge configuration
    JUDGE_MODEL = "gpt-4o"
    JUDGE_TEMPERATURE = 0.1
    JUDGES_DIR = Path(__file__).parent.parent / "v1.1" / "prompts" / "judges"

    def _load_judge_prompt_v3(module: str) -> str:
        """Load v3 judge prompt from file."""
        judge_files = {
            "m07": "judge_m07_attribute_extraction_v3.md",
            "m08": "judge_m08_attribute_ranks_v3.md",
            "m12b": "judge_m12b_classification_v3.md",
        }

        if module.lower() not in judge_files:
            raise ValueError(f"No v3 judge for module: {module}")

        judge_file = JUDGES_DIR / judge_files[module.lower()]
        if not judge_file.exists():
            raise FileNotFoundError(f"Judge file not found: {judge_file}")

        return judge_file.read_text()

    def _build_judge_input_v3(judge_prompt: str, record: dict, module: str) -> str:
        """Build judge input by substituting variables in prompt."""
        inp = record.get("input", {})
        out = record.get("output", {})
        exp = record.get("expected", {})

        # Get common fields
        keyword = inp.get("keyword", "")
        title = inp.get("title", inp.get("product_title", ""))
        taxonomy = inp.get("taxonomy", {})

        # Substitute placeholders
        result = judge_prompt
        result = result.replace("{{keyword}}", str(keyword))
        result = result.replace("{{title}}", str(title))
        result = result.replace("{{taxonomy}}", json.dumps(taxonomy, indent=2) if isinstance(taxonomy, dict) else str(taxonomy))

        # Module-specific substitutions
        if module.lower() == "m12b":
            result = result.replace("{{predicted_classification}}", str(out.get("classification", "")))
            result = result.replace("{{expected_classification}}", str(exp.get("classification", exp.get("relevancy", ""))))
            result = result.replace("{{predicted_reasoning}}", str(out.get("reasoning", "")))
            result = result.replace("{{predicted_confidence}}", str(out.get("confidence", "")))
        elif module.lower() == "m08":
            result = result.replace("{{predicted_rankings}}", json.dumps(out.get("attribute_table", []), indent=2))
            result = result.replace("{{expected_rankings}}", json.dumps(exp.get("attribute_table", []), indent=2))
            result = result.replace("{{predicted_reasoning}}", str(out.get("reasoning", "")))
        elif module.lower() == "m07":
            result = result.replace("{{predicted_variants}}", json.dumps(out.get("variants", []), indent=2))
            result = result.replace("{{expected_variants}}", json.dumps(exp.get("variants", []), indent=2))
            result = result.replace("{{predicted_reasoning}}", str(out.get("reasoning", "")))

        return result

    def _run_judge_v3(prompt: str) -> dict:
        """Call GPT-4o judge and return result."""
        client = openai.OpenAI()

        response = client.chat.completions.create(
            model=JUDGE_MODEL,
            temperature=JUDGE_TEMPERATURE,
            response_format={"type": "json_object"},
            messages=[{"role": "system", "content": prompt}]
        )

        return json.loads(response.choices[0].message.content)

    def _get_predicted_class(output: dict) -> str:
        """Extract predicted class from output."""
        if not output:
            return ""
        return str(output.get("classification", output.get("relevancy", ""))).upper()

    def _normalize_expected_class(expected: dict) -> str:
        """Normalize expected class."""
        if not expected:
            return ""
        val = expected.get("classification", expected.get("relevancy", ""))
        if val is None or str(val).lower() in ("null", "none", ""):
            return "NONE"
        return str(val).upper()

    # ════════════════════════════════════════════════════════════════════════════
    # M12b LLM Judge v3: Classification with Decision Tree
    # ════════════════════════════════════════════════════════════════════════════
    def m12b_judge_v3_handler(
        input: Dict[str, Any],
        output: Dict[str, Any],
        expected: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Optional[float]:
        """M12b: LLM Judge v3 for R/S/C/N classification with decision tree evaluation."""
        if output is None or expected is None:
            return None

        try:
            judge_prompt = _load_judge_prompt_v3("m12b")
            record = {"input": input, "output": output, "expected": expected}
            judge_input = _build_judge_input_v3(judge_prompt, record, "m12b")
            result = _run_judge_v3(judge_input)

            total_score = result.get("total_score", 0)
            return total_score / 100.0
        except Exception as e:
            # Fallback to simple accuracy
            predicted = _get_predicted_class(output)
            expected_val = _normalize_expected_class(expected)
            return 1.0 if predicted == expected_val else 0.0

    # ════════════════════════════════════════════════════════════════════════════
    # M08 LLM Judge v3: Attribute Ranks with Conversion Criticality
    # ════════════════════════════════════════════════════════════════════════════
    def m08_judge_v3_handler(
        input: Dict[str, Any],
        output: Dict[str, Any],
        expected: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Optional[float]:
        """M08: LLM Judge v3 for attribute ranking with unique ranks per type."""
        if output is None or expected is None:
            return None

        try:
            judge_prompt = _load_judge_prompt_v3("m08")
            record = {"input": input, "output": output, "expected": expected}
            judge_input = _build_judge_input_v3(judge_prompt, record, "m08")
            result = _run_judge_v3(judge_input)

            total_score = result.get("total_score", 0)
            return total_score / 100.0
        except Exception:
            return 0.0

    # ════════════════════════════════════════════════════════════════════════════
    # M07 LLM Judge v3: Attribute Extraction with Type Categorization
    # ════════════════════════════════════════════════════════════════════════════
    def m07_judge_v3_handler(
        input: Dict[str, Any],
        output: Dict[str, Any],
        expected: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Optional[float]:
        """M07: LLM Judge v3 for attribute extraction with type categorization."""
        if output is None or expected is None:
            return None

        try:
            judge_prompt = _load_judge_prompt_v3("m07")
            record = {"input": input, "output": output, "expected": expected}
            judge_input = _build_judge_input_v3(judge_prompt, record, "m07")
            result = _run_judge_v3(judge_input)

            total_score = result.get("total_score", 0)
            return total_score / 100.0
        except Exception:
            return 0.0

    # Register LLM Judge v3 scorers
    project.scorers.create(
        name="M12b Judge v3",
        slug="m12b-judge-v3",
        description="LLM Judge v3: R/S/C/N classification with decision tree evaluation (GPT-4o)",
        parameters=EntityOverlapInput,
        handler=m12b_judge_v3_handler,
    )

    project.scorers.create(
        name="M08 Judge v3",
        slug="m08-judge-v3",
        description="LLM Judge v3: Attribute ranking with unique ranks per type (GPT-4o)",
        parameters=EntityOverlapInput,
        handler=m08_judge_v3_handler,
    )

    project.scorers.create(
        name="M07 Judge v3",
        slug="m07-judge-v3",
        description="LLM Judge v3: Attribute extraction with type categorization (GPT-4o)",
        parameters=EntityOverlapInput,
        handler=m07_judge_v3_handler,
    )

    print("✓ 44 scorers defined for ai-training-pipeline-v1 (including V3, M12-M16, and LLM Judge v3)")
else:
    print("✓ 41 scorers defined for ai-training-pipeline-v1 (LLM Judge v3 requires OPENAI_API_KEY)")
