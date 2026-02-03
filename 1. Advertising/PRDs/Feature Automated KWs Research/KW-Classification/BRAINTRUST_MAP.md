# Braintrust Resource Map

## Project Info

| Field | Value |
|-------|-------|
| **Project ID** | `17b25eb4-95bf-499b-9ee3-1b6118546ecc` |
| **Project Name** | `Keyword-Classification-Pipeline-V1.1` |
| **Dashboard** | https://www.braintrust.dev/app/projects/17b25eb4-95bf-499b-9ee3-1b6118546ecc |

---

## Datasets (26 active in Braintrust)

### Core Datasets

| Module | Braintrust Name | Local File | Records |
|--------|-----------------|------------|---------|
| M01 | `M01_ExtractOwnBrandEntities_v1` | m01_v1_extract_own_brand_entities.jsonl | 99 |
| M01a | `M01A_ExtractOwnBrandVariations_v1` | m01a_v1_extract_own_brand_variations.jsonl | 99 |
| M01b | `M01B_ExtractBrandRelatedTerms_v1` | m01b_v1_extract_brand_related_terms.jsonl | 99 |
| M02 | `M02_ClassifyOwnBrandKeywords_v1` | m02_v1_classify_own_brand_keywords.jsonl | 916 |
| M02b | `M02B_ClassifyOwnBrandKeywords_PathB_v1` | m02b_v1_classify_own_brand_keywords.jsonl | 916 |
| M03 | `M03_GenerateCompetitorEntities_v1` | m03_v1_generate_competitor_entities.jsonl | 19 |
| M04 | `M04_ClassifyCompetitorBrandKeywords` | m04_v1_classify_competitor_brand_keywords.jsonl | 1,759 |
| M04b | `M04B_ClassifyCompetitorBrandKeywords_PathB` | m04b_v1_classify_competitor_brand_keywords.jsonl | 1,759 |
| M05 | `M05_ClassifyNonbrandedKeywords_v1` | m05_v1_classify_nonbranded_keywords.jsonl | 1,759 |
| M05b | `M05B_ClassifyNonBrandedKeywords_PathB_v1` | m05b_v1_classify_nonbranded_keywords.jsonl | 1,759 |
| M06 | `M06_GenerateProductTypeTaxonomy_v1` | m06_v1_generate_product_type_taxonomy.jsonl | 12 |
| M07 | `M07_ExtractProductAttributes_v1` | m07_v1_extract_product_attributes.jsonl | 12 |
| M08 | `M08_AssignAttributeRanks_v1` | m08_v1_assign_attribute_ranks.jsonl | 12 |
| M09 | `M09_IdentifyPrimaryIntendedUse_v1` | m09_v1_identify_primary_intended_use.jsonl | 10 |
| M10 | `M10_ValidatePrimaryIntendedUse_v1` | m10_v1_validate_primary_intended_use.jsonl | 10 |
| M11 | `M11_IdentifyHardConstraints_v1` | m11_v1_identify_hard_constraints.jsonl | 10 |
| M12 | `M12_CheckHardConstraint_v1` | m12_v1_check_hard_constraint.jsonl | 443 |
| M12b | `M12B_CombinedClassification_v1` | m12b_v1_combined_classification.jsonl | 443 |
| M13 | `M13_CheckProductType_v1` | m13_v1_check_product_type.jsonl | 439 |
| M14 | `M14_CheckPrimaryUseSameType_v1` | m14_v1_check_primary_use_same_type.jsonl | 229 |
| M15 | `M15_CheckSubstitute_v1` | m15_v1_check_substitute.jsonl | 210 |
| M16 | `M16_CheckComplementary_v1` | m16_v1_check_complementary.jsonl | 179 |

### Specialized Datasets (SD)

| Module | Braintrust Name | Local File | Description |
|--------|-----------------|------------|-------------|
| M06_V2 | `M06_V2_GenerateProductTypeTaxonomy` | m06_sd1_generate_product_type_taxonomy.jsonl | V2 prompt version |
| M07_SD1 | `M07_SD1_ExtractProductAttributes` | m07_sd1_extract_product_attributes.jsonl | SD1 variant |
| M08_SD1 | `M08_SD1_AssignAttributeRanks` | m08_sd1_assign_attribute_ranks.jsonl | SD1 variant |

### Batched Datasets (50 keywords per request)

For keyword classification modules, batched datasets significantly reduce API calls (38x reduction).

| Module | Braintrust Name | Local File | Batched Records | Keywords |
|--------|-----------------|------------|-----------------|----------|
| M02 | `M02_ClassifyOwnBrandKeywords_Batched_v1` | batched/m02_b50.jsonl | 23 | 916 |
| M02b | `M02B_ClassifyOwnBrandKeywords_PathB_Batched_v1` | batched/m02b_b50.jsonl | 23 | 916 |
| M04 | `M04_ClassifyCompetitorBrandKeywords_Batched_v1` | batched/m04_b50.jsonl | 41 | 1,759 |
| M04b | `M04B_ClassifyCompetitorBrandKeywords_PathB_Batched_v1` | batched/m04b_b50.jsonl | 41 | 1,759 |
| M05 | `M05_ClassifyNonbrandedKeywords_Batched_v1` | batched/m05_b50.jsonl | 40 | 1,759 |
| M05b | `M05B_ClassifyNonBrandedKeywords_PathB_Batched_v1` | batched/m05b_b50.jsonl | 40 | 1,759 |
| M12 | `M12_CheckHardConstraint_Batched_v1` | batched/m12_b50.jsonl | 15 | 443 |
| M12b | `M12B_CombinedClassification_Batched_v1` | batched/m12b_b50.jsonl | 15 | 443 |
| M13 | `M13_CheckProductType_Batched_v1` | batched/m13_b50.jsonl | 15 | 439 |
| M14 | `M14_CheckPrimaryUseSameType_Batched_v1` | batched/m14_b50.jsonl | 10 | 229 |
| M15 | `M15_CheckSubstitute_Batched_v1` | batched/m15_b50.jsonl | 10 | 210 |
| M16 | `M16_CheckComplementary_Batched_v1` | batched/m16_b50.jsonl | 10 | 179 |

**Total: 283 batched records (10,811 keywords) - 38.2x reduction in API calls**

Batched dataset mappings stored in: `config/batched_dataset_mappings.json`

---

## Prompts (25 Local Files)

| Module | Local File | Description |
|--------|------------|-------------|
| M01 | m01_v1_extract_own_brand_entities.md | Extract brand entities from product data |
| M01a | m01a_v1_extract_own_brand_variations.md | Generate brand name variations |
| M01b | m01b_v1_extract_brand_related_terms.md | Extract product lines, technologies |
| M02 | m02_v1_classify_own_brand_keywords.md | Classify own brand keywords |
| M02b | m02b_v1_classify_own_brand_keywords.md | Path B with M01a/M01b context |
| M02_V6 | m02_v6_classify_own_brand_keywords.md | V6 experimental prompt |
| M03 | m03_v1_generate_competitor_entities.md | Generate competitor brand list |
| M04 | m04_v1_classify_competitor_brand_keywords.md | Classify competitor keywords |
| M04b | m04b_v1_classify_competitor_brand_keywords.md | Path B with variations context |
| M05 | m05_v1_classify_nonbranded_keywords.md | Classify non-branded keywords |
| M05b | m05b_v1_classify_nonbranded_keywords.md | Path B version |
| M06 | m06_v1_generate_product_type_taxonomy.md | Generate product taxonomy |
| M06_V2 | m06_v2_generate_product_type_taxonomy.md | V2 improved prompt |
| M07 | m07_v1_extract_product_attributes.md | Extract product attributes |
| M08 | m08_v1_assign_attribute_ranks.md | Rank attribute importance |
| M08_V2 | m08_v2_assign_attribute_ranks.md | V2 improved prompt |
| M09 | m09_v1_identify_primary_intended_use.md | Identify primary use |
| M10 | m10_v1_validate_primary_intended_use.md | Validate primary use |
| M11 | m11_v1_identify_hard_constraints.md | Identify hard constraints |
| M12 | m12_v1_check_hard_constraint.md | Check constraint violations |
| M12b | m12b_v1_combined_classification.md | Combined R/S/C/N classification |
| M13 | m13_v1_check_product_type.md | Product type matching |
| M14 | m14_v1_check_primary_use_same_type.md | Primary use alignment |
| M15 | m15_v1_check_substitute.md | Substitute determination |
| M16 | m16_v1_check_complementary.md | Complementary determination |

---

## Scorers (braintrust_scorers.py)

Push via: `cd scorers && braintrust push --project "Keyword-Classification-Pipeline-V1.1" braintrust_scorers.py`

### Binary Classification Scorers

| Scorer | Module | Field | Description |
|--------|--------|-------|-------------|
| `m2-correct` | M02 | branding_scope_1 | Own Brand (OB) classification |
| `m4-correct` | M04 | branding_scope_2 | Competitor Brand (CB) classification |
| `m5-correct` | M05 | branding_scope_3 | Non-Branded (NB) classification |
| `m9-correct` | M09 | relationship_R | Relevant (R) classification |
| `m10-correct` | M10 | relationship_N | Negative (N) classification |
| `m11-correct` | M11 | relationship_S | Substitute (S) classification |
| `m12-correct` | M12 | relationship_C | Complementary (C) classification |
| `m13-correct` | M13 | - | Product type check |
| `m14-correct` | M14 | - | Primary use same type |
| `m15-correct` | M15 | - | Substitute check |
| `m16-correct` | M16 | - | Complementary check |

### Path B Scorers

| Scorer | Module | Description |
|--------|--------|-------------|
| `m02b-correct` | M02b | OB classification with variations (Path B) |
| `m04b-correct` | M04b | CB classification with variations (Path B) |
| `m05b-correct` | M05b | NB classification with variations (Path B) |
| `m12b-correct` | M12b | Combined R/S/C/N classification |

### List Extraction Scorers (M01, M03)

| Scorer | Module | Description |
|--------|--------|-------------|
| `m1-recall` | M01 | Recall of extracted entities |
| `m1-precision` | M01 | Precision of extracted entities |
| `m1-jaccard` | M01 | Jaccard similarity |
| `m1-purity` | M01 | Purity of extraction |
| `m1-length-violation` | M01 | Length constraint violations |
| `m1-avg-length` | M01 | Average entity length |
| `m1-entity-overlap` | M01 | Entity overlap score |
| `m3-recall` | M03 | Competitor recall |
| `m3-precision` | M03 | Competitor precision |
| `m3-jaccard` | M03 | Competitor Jaccard |
| `m3-entity-overlap` | M03 | Competitor entity overlap |

### Taxonomy Scorers (M06)

| Scorer | Module | Description |
|--------|--------|-------------|
| `m6-level1` | M06 | Level 1 taxonomy match |
| `m6-level2` | M06 | Level 2 taxonomy match |
| `m6-level3` | M06 | Level 3 taxonomy match |
| `m6-overall` | M06 | Overall taxonomy score |
| `m6-taxonomy-overlap` | M06 | Taxonomy overlap |

### Attribute Scorers (M07, M08)

| Scorer | Module | Description |
|--------|--------|-------------|
| `m7-variants` | M07 | Variant extraction score |
| `m7-usecases` | M07 | Use case extraction score |
| `m7-audiences` | M07 | Audience extraction score |
| `m7-overall` | M07 | Overall attribute score |
| `m8-ndcg5` | M08 | NDCG@5 for ranking |
| `m8-ndcg10` | M08 | NDCG@10 for ranking |

---

## LLM-as-Judge Scorers (llm_judge_scorer.py)

Push via: `cd scorers && braintrust push llm_judge_scorer.py`

| Judge | Module | Evaluates |
|-------|--------|-----------|
| `llm_judge_m01` | M01 | Brand entity extraction quality |
| `llm_judge_m01a` | M01a | Brand variations quality |
| `llm_judge_m01b` | M01b | Related terms quality |
| `llm_judge_m02` | M02 | OB classification reasoning |
| `llm_judge_m03` | M03 | Competitor entities quality |
| `llm_judge_m04` | M04 | CB classification reasoning |
| `llm_judge_m05` | M05 | NB classification reasoning |
| `llm_judge_m06` | M06 | Taxonomy quality |
| `llm_judge_m07` | M07 | Attribute extraction quality |
| `llm_judge_m08` | M08 | Attribute ranking quality |
| `llm_judge_m09` | M09 | Primary use identification |
| `llm_judge_m10` | M10 | Use validation |
| `llm_judge_m11` | M11 | Hard constraints quality |
| `llm_judge_m12` | M12 | Constraint check reasoning |
| `llm_judge_m12b` | M12b | Final classification reasoning |
| `llm_judge_m13` | M13 | Product type check |
| `llm_judge_m14` | M14 | Primary use same type |
| `llm_judge_m15` | M15 | Substitute check |
| `llm_judge_m16` | M16 | Complementary check |

---

## Commands

### Upload Resources

```bash
# Upload all prompts
python scripts/upload/upload_prompts.py

# Upload all datasets
python scripts/upload/upload_datasets.py

# Upload batched datasets (keyword modules)
python scripts/upload/upload_batched_datasets.py

# Upload specific module
python scripts/upload/upload_prompts.py --module m02
python scripts/upload/upload_datasets.py --module m02

# Show current mappings
python scripts/upload/upload_prompts.py --show-mapping
```

### Push Scorers

```bash
cd scorers

# Push main scorers (27 scorers)
braintrust push --project "Keyword-Classification-Pipeline-V1.1" --if-exists replace braintrust_scorers.py

# Push LLM judges
braintrust push --project "Keyword-Classification-Pipeline-V1.1" llm_judge_scorer.py
```

### List Resources

```bash
# List all resources from Braintrust
python scripts/braintrust_list.py --all

# Export to JSON
python scripts/braintrust_list.py --export
```

---

## Baseline Testing

See `docs/BASELINE_TESTING_GUIDE.md` for:
- Pipeline architecture (V1.1 vs V3)
- Testing process workflow
- Cohen's Kappa calculation
- Error analysis methods

---

## Files Reference

| Type | Location |
|------|----------|
| Prompts | `prompts/modules/` |
| Judges | `prompts/judges/` |
| JSON Schemas | `prompts/json_schemas/` |
| Datasets | `datasets/` |
| Scorers | `scorers/` |
| Upload Scripts | `scripts/upload/` |
| Testing Scripts | `scripts/testing/` |
| Baseline Guide | `docs/BASELINE_TESTING_GUIDE.md` |
