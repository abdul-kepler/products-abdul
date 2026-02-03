"""
Shared module configuration for all DSPy optimizers (MIPRO, COPRO, GEPA).

Each module config contains:
- Common: name, dataset, prompt
- MIPRO/COPRO: input_keys, output_keys, positive_values, balance_field
- GEPA: input_template, output_key
"""

from pathlib import Path

# Base paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]  # dspy_optimize -> scripts -> project root
DATASETS_DIR = PROJECT_ROOT / "datasets" / "single"
PROMPTS_DIR = PROJECT_ROOT / "prompts" / "modules" / "single"


MODULE_CONFIGS = {
    # ============================================================
    # TEXT GENERATION MODULES (use GEPA)
    # ============================================================
    "m01": {
        "name": "ExtractOwnBrandEntities",
        "dataset": DATASETS_DIR / "m01_v3_extract_own_brand_entities.jsonl",
        "prompt": PROMPTS_DIR / "m01_v3_extract_own_brand_entities.md",
        # MIPRO fields
        "input_keys": ["brand_name", "title", "bullet_points", "description", "manufacturer"],
        "output_keys": ["brand_entities"],
        "positive_values": None,
        "balance_field": None,
        # GEPA fields
        "input_template": """Brand Name: {brand_name}
Title: {title}
Bullet Points: {bullet_points}
Description: {description}
Manufacturer: {manufacturer}

Extract brand entities from this product listing.""",
        "output_key": "brand_entities",
    },
    "m01a": {
        "name": "ExtractOwnBrandVariations",
        "dataset": DATASETS_DIR / "m01a_v2_extract_own_brand_variations.jsonl",
        "prompt": PROMPTS_DIR / "m01a_v2_extract_own_brand_variations.md",
        # MIPRO fields
        "input_keys": ["brand_name"],
        "output_keys": ["variations"],
        "positive_values": None,
        "balance_field": None,
        # GEPA fields
        "input_template": """Brand Name: {brand_name}

Generate variations of this brand name.""",
        "output_key": "variations",
    },
    "m01b": {
        "name": "ExtractBrandRelatedTerms",
        "dataset": DATASETS_DIR / "m01b_v1_extract_brand_related_terms.jsonl",
        "prompt": PROMPTS_DIR / "m01b_v1_extract_brand_related_terms.md",
        # MIPRO fields
        "input_keys": ["brand_name", "title", "bullet_points", "description", "manufacturer"],
        "output_keys": ["sub_brands"],
        "positive_values": None,
        "balance_field": None,
        # GEPA fields
        "input_template": """Brand Name: {brand_name}
Title: {title}
Bullet Points: {bullet_points}
Description: {description}
Manufacturer: {manufacturer}

Extract sub-brands, searchable standards, and manufacturer.""",
        "output_key": "sub_brands",
    },
    "m03": {
        "name": "GenerateCompetitorEntities",
        "dataset": DATASETS_DIR / "m03_v1_generate_competitor_entities.jsonl",
        "prompt": PROMPTS_DIR / "m03_v1_generate_competitor_entities.md",
        # MIPRO fields
        "input_keys": ["title", "bullet_points", "description", "brand_name", "product_type", "category_root", "category_sub", "known_competitor_brands"],
        "output_keys": ["competitor_entities"],
        "positive_values": None,
        "balance_field": None,
        # GEPA fields
        "input_template": """Title: {title}
Bullet Points: {bullet_points}
Description: {description}
Brand Name: {brand_name}
Product Type: {product_type}
Category: {category_root} > {category_sub}
Known Competitor Brands: {known_competitor_brands}

Generate competitor entities.""",
        "output_key": "competitor_entities",
    },
    "m06": {
        "name": "GenerateProductTypeTaxonomy",
        "dataset": DATASETS_DIR / "m06_v1_generate_product_type_taxonomy.jsonl",
        "prompt": PROMPTS_DIR / "m06_v1_generate_product_type_taxonomy.md",
        # MIPRO fields
        "input_keys": ["title", "bullet_points", "description", "product_type", "category_root", "category_sub"],
        "output_keys": ["taxonomy"],
        "positive_values": None,
        "balance_field": None,
        # GEPA fields
        "input_template": """Title: {title}
Bullet Points: {bullet_points}
Description: {description}
Product Type: {product_type}
Category Root: {category_root}
Category Sub: {category_sub}

Generate product type taxonomy.""",
        "output_key": "taxonomy",
    },
    "m07": {
        "name": "ExtractProductAttributes",
        "dataset": DATASETS_DIR / "m07_v1_extract_product_attributes.jsonl",
        "prompt": PROMPTS_DIR / "m07_v1_extract_product_attributes.md",
        # MIPRO fields
        "input_keys": ["title", "bullet_points", "description", "product_type", "category_root", "category_sub", "color", "size", "material"],
        "output_keys": ["variants"],
        "positive_values": None,
        "balance_field": None,
        # GEPA fields
        "input_template": """Title: {title}
Bullet Points: {bullet_points}
Description: {description}
Product Type: {product_type}
Category: {category_root} > {category_sub}
Color: {color}
Size: {size}
Material: {material}

Extract product attributes (variants, use cases, audiences).""",
        "output_key": "variants",
    },
    "m08": {
        "name": "AssignAttributeRanks",
        "dataset": DATASETS_DIR / "m08_v1_assign_attribute_ranks.jsonl",
        "prompt": PROMPTS_DIR / "m08_v1_assign_attribute_ranks.md",
        # MIPRO fields
        "input_keys": ["title", "bullet_points", "description", "taxonomy", "variants", "use_cases", "audiences"],
        "output_keys": ["attribute_table"],
        "positive_values": None,
        "balance_field": None,
        # GEPA fields
        "input_template": """Title: {title}
Bullet Points: {bullet_points}
Description: {description}
Taxonomy: {taxonomy}
Variants: {variants}
Use Cases: {use_cases}
Audiences: {audiences}

Assign ranks to these attributes.""",
        "output_key": "attribute_table",
    },
    "m09": {
        "name": "IdentifyPrimaryIntendedUse",
        "dataset": DATASETS_DIR / "m09_v1_identify_primary_intended_use.jsonl",
        "prompt": PROMPTS_DIR / "m09_v1_identify_primary_intended_use.md",
        # MIPRO fields
        "input_keys": ["title", "bullet_points", "description", "taxonomy", "attribute_table", "product_attributes"],
        "output_keys": ["primary_use"],
        "positive_values": None,
        "balance_field": None,
        # GEPA fields
        "input_template": """Product Information:
Title: {title}
Bullet Points: {bullet_points}
Description: {description}
Taxonomy: {taxonomy}
Attributes: {attribute_table}
Product Attributes: {product_attributes}

Identify the primary intended use of this product.""",
        "output_key": "primary_use",
    },
    "m10": {
        "name": "ValidatePrimaryIntendedUse",
        "dataset": DATASETS_DIR / "m10_v1_validate_primary_intended_use.jsonl",
        "prompt": PROMPTS_DIR / "m10_v1_validate_primary_intended_use.md",
        # MIPRO fields
        "input_keys": ["title", "bullet_points", "description", "taxonomy", "attribute_table", "product_attributes", "primary_use"],
        "output_keys": ["validated_use"],
        "positive_values": None,
        "balance_field": None,
        # GEPA fields
        "input_template": """Product Information:
Title: {title}
Bullet Points: {bullet_points}
Description: {description}
Taxonomy: {taxonomy}
Attributes: {attribute_table}
Product Attributes: {product_attributes}

Primary Use (from Module 9): {primary_use}

Validate and clean this primary use phrase.""",
        "output_key": "validated_use",
    },
    "m11": {
        "name": "IdentifyHardConstraints",
        "dataset": DATASETS_DIR / "m11_v1_identify_hard_constraints.jsonl",
        "prompt": PROMPTS_DIR / "m11_v1_identify_hard_constraints.md",
        # MIPRO fields
        "input_keys": ["title", "bullet_points", "description", "validated_use", "taxonomy", "attribute_table", "product_attributes"],
        "output_keys": ["hard_constraints"],
        "positive_values": None,
        "balance_field": None,
        # GEPA fields
        "input_template": """Title: {title}
Bullet Points: {bullet_points}
Description: {description}
Validated Use: {validated_use}
Taxonomy: {taxonomy}
Attribute Table: {attribute_table}
Product Attributes: {product_attributes}

Identify hard constraints for this product.""",
        "output_key": "hard_constraints",
    },

    # ============================================================
    # BINARY CLASSIFIERS (use MIPRO/COPRO)
    # ============================================================
    "m02": {
        "name": "ClassifyOwnBrandKeywords",
        "dataset": DATASETS_DIR / "m02_v1_classify_own_brand_keywords.jsonl",
        "prompt": PROMPTS_DIR / "m02_v1_classify_own_brand_keywords.md",
        # MIPRO fields
        "input_keys": ["keyword", "brand_entities"],
        "output_keys": ["branding_scope_1"],
        "positive_values": {"branding_scope_1": {"ob"}},
        "balance_field": "branding_scope_1",
        # GEPA fields (not typically used for classifiers)
        "input_template": """Keyword: {keyword}
Brand Entities: {brand_entities}

Classify this keyword.""",
        "output_key": "branding_scope_1",
    },
    "m02b": {
        "name": "ClassifyOwnBrandKeywords_PathB",
        "dataset": DATASETS_DIR / "m02b_v1_classify_own_brand_keywords.jsonl",
        "prompt": PROMPTS_DIR / "m02b_v1_classify_own_brand_keywords.md",
        "input_keys": ["keyword", "variations_own", "related_terms_own"],
        "output_keys": ["branding_scope_1"],
        "positive_values": {"branding_scope_1": {"ob"}},
        "balance_field": "branding_scope_1",
        "input_template": """Keyword: {keyword}
Own Brand Variations: {variations_own}
Related Terms: {related_terms_own}

Classify this keyword.""",
        "output_key": "branding_scope_1",
    },
    "m04": {
        "name": "ClassifyCompetitorBrandKeywords",
        "dataset": DATASETS_DIR / "m04_v1_classify_competitor_brand_keywords.jsonl",
        "prompt": PROMPTS_DIR / "m04_v1_classify_competitor_brand_keywords.md",
        "input_keys": ["keyword", "competitor_entities", "own_brand"],
        "output_keys": ["branding_scope_2"],
        "positive_values": {"branding_scope_2": {"cb"}},
        "balance_field": "branding_scope_2",
        "input_template": """Keyword: {keyword}
Competitor Entities: {competitor_entities}
Own Brand: {own_brand}

Classify this keyword.""",
        "output_key": "branding_scope_2",
    },
    "m04b": {
        "name": "ClassifyCompetitorBrandKeywords_PathB",
        "dataset": DATASETS_DIR / "m04b_v1_classify_competitor_brand_keywords.jsonl",
        "prompt": PROMPTS_DIR / "m04b_v1_classify_competitor_brand_keywords.md",
        "input_keys": ["keyword", "competitors", "own_brand"],
        "output_keys": ["branding_scope_2"],
        "positive_values": {"branding_scope_2": {"cb"}},
        "balance_field": "branding_scope_2",
        "input_template": """Keyword: {keyword}
Competitors: {competitors}
Own Brand: {own_brand}

Classify this keyword.""",
        "output_key": "branding_scope_2",
    },
    "m05": {
        "name": "ClassifyNonBrandedKeywords",
        "dataset": DATASETS_DIR / "m05_v1_classify_nonbranded_keywords.jsonl",
        "prompt": PROMPTS_DIR / "m05_v1_classify_nonbranded_keywords.md",
        "input_keys": ["keyword", "brand_entities", "competitor_entities"],
        "output_keys": ["branding_scope_3"],
        "positive_values": {"branding_scope_3": {"nb"}},
        "balance_field": "branding_scope_3",
        "input_template": """Keyword: {keyword}
Brand Entities: {brand_entities}
Competitor Entities: {competitor_entities}

Classify this keyword.""",
        "output_key": "branding_scope_3",
    },
    "m05b": {
        "name": "ClassifyNonBrandedKeywords_PathB",
        "dataset": DATASETS_DIR / "m05b_v1_classify_nonbranded_keywords.jsonl",
        "prompt": PROMPTS_DIR / "m05b_v1_classify_nonbranded_keywords.md",
        "input_keys": ["keyword", "own_brand", "competitors"],
        "output_keys": ["branding_scope_3"],
        "positive_values": {"branding_scope_3": {"nb"}},
        "balance_field": "branding_scope_3",
        "input_template": """Keyword: {keyword}
Own Brand: {own_brand}
Competitors: {competitors}

Classify this keyword.""",
        "output_key": "branding_scope_3",
    },
    "m12": {
        "name": "HardConstraintViolationCheck",
        "dataset": DATASETS_DIR / "m12_v1_check_hard_constraint.jsonl",
        "prompt": PROMPTS_DIR / "m12_v1_check_hard_constraint.md",
        "input_keys": ["keyword", "title", "bullet_points", "description", "validated_use", "taxonomy", "attribute_table", "product_attributes", "hard_constraints"],
        "output_keys": ["relevancy"],
        "positive_values": {"relevancy": {"r", "s", "c"}},
        "balance_field": "relevancy",
        "input_template": """Keyword: {keyword}
Title: {title}
Validated Use: {validated_use}

Check hard constraint violation.""",
        "output_key": "relevancy",
    },
    "m12b": {
        "name": "CombinedClassification",
        "dataset": DATASETS_DIR / "m12b_v1_combined_classification.jsonl",
        "prompt": PROMPTS_DIR / "m12b_v1_combined_classification.md",
        "input_keys": ["keyword", "title", "bullet_points", "description", "validated_use", "taxonomy", "attribute_table", "product_attributes", "hard_constraints"],
        "output_keys": ["relevancy"],
        "positive_values": {"relevancy": {"r", "s", "c"}},
        "balance_field": "relevancy",
        "input_template": """Keyword: {keyword}
Title: {title}
Validated Use: {validated_use}

Classify relevancy.""",
        "output_key": "relevancy",
    },
    "m13": {
        "name": "ProductTypeCheck",
        "dataset": DATASETS_DIR / "m13_v1_check_product_type.jsonl",
        "prompt": PROMPTS_DIR / "m13_v1_check_product_type.md",
        "input_keys": ["keyword", "title", "bullet_points", "description", "validated_use", "taxonomy", "attribute_table", "product_attributes", "hard_constraints"],
        "output_keys": ["same_type"],
        "positive_values": {"same_type": {"true", "yes"}},
        "balance_field": "same_type",
        "input_template": """Keyword: {keyword}
Title: {title}
Taxonomy: {taxonomy}

Check if same product type.""",
        "output_key": "same_type",
    },
    "m14": {
        "name": "PrimaryUseCheckSameType",
        "dataset": DATASETS_DIR / "m14_v1_check_primary_use_same_type.jsonl",
        "prompt": PROMPTS_DIR / "m14_v1_check_primary_use_same_type.md",
        "input_keys": ["keyword", "title", "bullet_points", "description", "validated_use", "taxonomy", "attribute_table", "product_attributes", "hard_constraints"],
        "output_keys": ["same_primary_use", "relevancy"],
        "positive_values": {"same_primary_use": {"true", "yes"}, "relevancy": {"r"}},
        "balance_field": "relevancy",
        "input_template": """Keyword: {keyword}
Validated Use: {validated_use}

Check primary use match.""",
        "output_key": "relevancy",
    },
    "m15": {
        "name": "SubstituteCheck",
        "dataset": DATASETS_DIR / "m15_v1_check_substitute.jsonl",
        "prompt": PROMPTS_DIR / "m15_v1_check_substitute.md",
        "input_keys": ["keyword", "title", "bullet_points", "description", "validated_use", "taxonomy", "attribute_table", "product_attributes", "hard_constraints"],
        "output_keys": ["same_primary_use", "relevancy"],
        "positive_values": {"same_primary_use": {"true", "yes"}, "relevancy": {"s"}},
        "balance_field": "relevancy",
        "input_template": """Keyword: {keyword}
Validated Use: {validated_use}

Check if substitute.""",
        "output_key": "relevancy",
    },
    "m16": {
        "name": "ComplementaryCheck",
        "dataset": DATASETS_DIR / "m16_v1_check_complementary.jsonl",
        "prompt": PROMPTS_DIR / "m16_v1_check_complementary.md",
        "input_keys": ["keyword", "title", "bullet_points", "description", "validated_use", "taxonomy", "attribute_table", "product_attributes", "hard_constraints"],
        "output_keys": ["used_together", "relevancy"],
        "positive_values": {"used_together": {"true", "yes"}, "relevancy": {"c"}},
        "balance_field": "relevancy",
        "input_template": """Keyword: {keyword}
Validated Use: {validated_use}

Check if complementary.""",
        "output_key": "relevancy",
    },
}


def get_config(module_name: str) -> dict:
    """Get configuration for a module."""
    config = MODULE_CONFIGS.get(module_name.lower())
    if not config:
        available = ", ".join(sorted(MODULE_CONFIGS.keys()))
        raise ValueError(f"Unknown module: {module_name}. Available: {available}")
    return config


def list_modules() -> list:
    """List all available modules."""
    return sorted(MODULE_CONFIGS.keys())


def list_classifier_modules() -> list:
    """List modules suitable for MIPRO/COPRO (binary classifiers)."""
    return [m for m, c in MODULE_CONFIGS.items() if c.get("positive_values")]


def list_textgen_modules() -> list:
    """List modules suitable for GEPA (text generation)."""
    return [m for m, c in MODULE_CONFIGS.items() if not c.get("positive_values")]
