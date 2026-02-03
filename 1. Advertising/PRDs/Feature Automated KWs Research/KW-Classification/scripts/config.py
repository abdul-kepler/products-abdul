"""
KW Classification v1.1 Configuration

Project: ai-training-pipeline-v1.1
Modules: M01-M16 (16 modules total)

Environment variables:
    BRAINTRUST_API_KEY: API key from braintrust.dev
    OPENAI_API_KEY: API key from OpenAI
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Load .env from project root
ENV_FILE = PROJECT_ROOT / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)

# API Keys
BRAINTRUST_API_KEY = os.getenv("BRAINTRUST_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# v1.1 Project settings (Braintrust)
PROJECT_ID = "17b25eb4-95bf-499b-9ee3-1b6118546ecc"
PROJECT_NAME = "Keyword-Classification-Pipeline-V1.1"

# Paths - adapted for standalone project structure
# Note: Single-record prompts/datasets are in "single" subdirectory
PROMPTS_DIR = PROJECT_ROOT / "prompts" / "modules" / "single"
JUDGES_DIR = PROJECT_ROOT / "prompts" / "judges"
SCHEMAS_DIR = PROJECT_ROOT / "prompts" / "json_schemas"
DATASETS_DIR = PROJECT_ROOT / "datasets" / "single"
SCORERS_DIR = PROJECT_ROOT / "scorers"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
EXPERIMENT_RESULTS_DIR = PROJECT_ROOT / "experiment_results"

# 16 Modules for v1.1 + sub-modules (M01a, M01b, etc.)
MODULES = {
    "m01": {
        "name": "ExtractOwnBrandEntities",
        "slug": "extract_own_brand_entities",
        "type": "extraction",
        "description": "Extract brand entities from product data",
    },
    "m01a": {
        "name": "ExtractOwnBrandVariations",
        "slug": "extract_own_brand_variations",
        "type": "generation",
        "description": "Generate brand name search variations (typos, truncations, phonetic)",
        "model": "gpt-4o-mini",
        "temperature": 0.3,
        "max_tokens": 512,
        "response_format": "json_object",
    },
    "m01b": {
        "name": "ExtractBrandRelatedTerms",
        "slug": "extract_brand_related_terms",
        "type": "extraction",
        "description": "Extract product lines, technologies, and manufacturer from listing",
        "model": "gpt-4o-mini",
        "temperature": 0.0,
        "max_tokens": 1024,
        "response_format": "json_object",
    },
    "m02": {
        "name": "ClassifyOwnBrandKeywords",
        "slug": "classify_own_brand_keywords",
        "type": "binary_classifier",
        "description": "Classify if keyword matches own brand",
    },
    "m02b": {
        "name": "ClassifyOwnBrandKeywords_PathB",
        "slug": "classify_own_brand_keywords",
        "type": "binary_classifier",
        "description": "Path B: Classify if keyword matches own brand (uses M01a variations + M01b sub_brands/manufacturer)",
        "model": "gpt-4o-mini",
        "temperature": 0.0,
        "max_tokens": 512,
        "response_format": "json_schema",
    },
    "m03": {
        "name": "GenerateCompetitorEntities",
        "slug": "generate_competitor_entities",
        "type": "extraction",
        "description": "Generate competitor brand entities",
        "enabled": False,  # Disabled - not ready for automated testing
    },
    "m04": {
        "name": "ClassifyCompetitorBrandKeywords",
        "slug": "classify_competitor_brand_keywords",
        "type": "binary_classifier",
        "description": "Classify if keyword is competitor brand",
    },
    "m04b": {
        "name": "ClassifyCompetitorBrandKeywords_PathB",
        "slug": "classify_competitor_brand_keywords",
        "type": "binary_classifier",
        "description": "Path B: Classify if keyword is competitor brand (uses M01a + M01b for each competitor)",
        "model": "gpt-4o-mini",
        "temperature": 0.0,
        "max_tokens": 512,
        "response_format": "json_schema",
    },
    "m05": {
        "name": "ClassifyNonBrandedKeywords",
        "slug": "classify_nonbranded_keywords",
        "type": "binary_classifier",
        "description": "Classify if keyword is non-branded",
    },
    "m05b": {
        "name": "ClassifyNonBrandedKeywords_PathB",
        "slug": "classify_nonbranded_keywords",
        "type": "binary_classifier",
        "description": "Path B: Classify if keyword is non-branded (checks M01a + M01b for own + all competitors)",
        "model": "gpt-4o-mini",
        "temperature": 0.0,
        "max_tokens": 512,
        "response_format": "json_schema",
    },
    "m06": {
        "name": "GenerateProductTypeTaxonomy",
        "slug": "generate_product_type_taxonomy",
        "type": "extraction",
        "description": "Generate product type taxonomy",
    },
    "m07": {
        "name": "ExtractProductAttributes",
        "slug": "extract_product_attributes",
        "type": "extraction",
        "description": "Extract product attributes",
    },
    "m08": {
        "name": "AssignAttributeRanks",
        "slug": "assign_attribute_ranks",
        "type": "ranking",
        "description": "Assign ranks to product attributes",
    },
    "m09": {
        "name": "IdentifyPrimaryIntendedUse",
        "slug": "identify_primary_intended_use_v1.1",
        "type": "extraction",
        "description": "Determine the single core reason the product exists",
    },
    "m10": {
        "name": "ValidatePrimaryIntendedUse",
        "slug": "validate_primary_intended_use_v1.1",
        "type": "validation",
        "description": "Ensure the intended use phrase is clean and usable",
    },
    "m11": {
        "name": "IdentifyHardConstraints",
        "slug": "identify_hard_constraints_v1.1",
        "type": "extraction",
        "description": "Determine which attributes are non-negotiable for product to function",
    },
    "m12": {
        "name": "HardConstraintViolationCheck",
        "slug": "hard_constraint_violation_check_v1.1",
        "type": "classifier",
        "description": "Check if keyword violates hard constraints",
    },
    "m12b": {
        "name": "CombinedClassification",
        "slug": "combined_classification_v1.1",
        "type": "classifier",
        "description": "Final R/S/C/N classification decision",
    },
    "m13": {
        "name": "ProductTypeCheck",
        "slug": "product_type_check_v1.1",
        "type": "classifier",
        "description": "Check if keyword matches product type",
    },
    "m14": {
        "name": "PrimaryUseCheckSameType",
        "slug": "primary_use_check_same_type_v1.1",
        "type": "classifier",
        "description": "Check primary use alignment for same product type",
    },
    "m15": {
        "name": "SubstituteCheck",
        "slug": "substitute_check_v1.1",
        "type": "classifier",
        "description": "Determine if keyword product is a substitute",
    },
    "m16": {
        "name": "ComplementaryCheck",
        "slug": "complementary_check_v1.1",
        "type": "classifier",
        "description": "Determine if keyword product is complementary",
    },
}

# Model settings
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_TEMPERATURE = 0.0
DEFAULT_MAX_TOKENS = 4096


def load_api_key():
    """Load Braintrust API key."""
    global BRAINTRUST_API_KEY

    if BRAINTRUST_API_KEY:
        return BRAINTRUST_API_KEY

    # Try loading from .env again
    if ENV_FILE.exists():
        load_dotenv(ENV_FILE)
        BRAINTRUST_API_KEY = os.getenv("BRAINTRUST_API_KEY")
        if BRAINTRUST_API_KEY:
            return BRAINTRUST_API_KEY

    raise ValueError(
        f"BRAINTRUST_API_KEY not found. Create {ENV_FILE} with your API key "
        "or set BRAINTRUST_API_KEY environment variable."
    )


def get_module(module_id: str) -> dict:
    """Get module config by ID (e.g., 'm01' or '01' or '1')."""
    # Normalize module_id
    if not module_id.startswith("m"):
        module_id = f"m{module_id.zfill(2)}"

    if module_id not in MODULES:
        raise ValueError(f"Unknown module: {module_id}. Available: {list(MODULES.keys())}")

    return MODULES[module_id]


def get_prompt_path(module_id: str) -> Path:
    """Get path to prompt file for a module."""
    module = get_module(module_id)
    return PROMPTS_DIR / f"{module_id}_{module['slug']}.md"


def get_schema_path(module_id: str) -> Path:
    """Get path to JSON schema file for a module."""
    module = get_module(module_id)
    return SCHEMAS_DIR / f"{module_id}_{module['slug']}_schema.json"


def get_judge_path(module_id: str, version: str = "") -> Path:
    """Get path to judge prompt file for a module."""
    suffix = f"_{version}" if version else ""
    # Judge files use different naming convention
    judge_name_map = {
        "m01": "judge_m01_extract_brand_entities",
        "m01a": "judge_m01a_brand_variations",
        "m01b": "judge_m01b_brand_related_terms",
        "m02": "judge_m02_brand_classification",
        "m03": "judge_m03_competitor_entities",
        "m04": "judge_m04_competitor_brand",
        "m05": "judge_m05_nonbranded_keywords",
        "m06": "judge_m06_product_taxonomy",
        "m07": "judge_m07_attribute_extraction",
        "m08": "judge_m08_attribute_ranks",
        "m09": "judge_m09_primary_use",
        "m10": "judge_m10_validate_primary_use",
        "m11": "judge_m11_hard_constraints",
        "m12": "judge_m12_hard_constraint_check",
        "m12b": "judge_m12b_classification",
        "m13": "judge_m13_product_type_check",
        "m14": "judge_m14_primary_use_same_type",
        "m15": "judge_m15_substitute_check",
        "m16": "judge_m16_complementary_check",
    }
    base_name = judge_name_map.get(module_id, f"judge_{module_id}")
    return JUDGES_DIR / f"{base_name}{suffix}.md"


def get_dataset_path(module_id: str) -> Path:
    """Get path to dataset file for a module."""
    module = get_module(module_id)
    return DATASETS_DIR / f"{module_id}_{module['slug']}.jsonl"


def list_available_modules() -> list:
    """List modules that have both prompt and dataset files."""
    available = []
    for module_id in MODULES:
        prompt_path = get_prompt_path(module_id)
        dataset_path = get_dataset_path(module_id)
        if prompt_path.exists() and dataset_path.exists():
            available.append(module_id)
    return sorted(available)


def list_all_modules() -> list:
    """List all defined modules."""
    return sorted(MODULES.keys())


# Validate paths exist on import (optional, helps catch config issues early)
def validate_project_structure():
    """Check that required directories exist."""
    required_dirs = [PROMPTS_DIR, JUDGES_DIR, SCHEMAS_DIR, DATASETS_DIR]
    missing = [d for d in required_dirs if not d.exists()]
    if missing:
        print(f"Warning: Missing directories: {missing}")
    return len(missing) == 0
