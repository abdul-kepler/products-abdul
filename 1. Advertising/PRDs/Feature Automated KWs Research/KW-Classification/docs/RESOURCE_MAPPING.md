# Resource Mapping System

## Overview

The Resource Mapping System provides a centralized way to track relationships between:
- **Local prompt files** → Braintrust prompt IDs
- **Local dataset files** → Braintrust dataset IDs
- **Modules** → Default prompts and datasets

## Architecture

```
evaluation_KD/evaluation_experimentV5/
├── resource_mappings.yaml   # CENTRAL SOURCE OF TRUTH
├── prompt_mappings.yaml     # Legacy (for backwards compatibility)
└── experiment_mappings.yaml # Experiment-level mappings

scripts/
├── mapping_loader.py        # Python API for accessing mappings
├── config.py                # Module definitions
└── upload/
    └── upload_prompts.py    # Upload with auto-mapping update
```

## Quick Start

### Python API

```python
from scripts.mapping_loader import get_mappings

# Get singleton instance
mappings = get_mappings()

# Get Braintrust prompt ID
prompt_id = mappings.get_prompt_id("m01")  # → '01cd3700-4728-...'

# Get local file path
prompt_path = mappings.get_prompt_path("m08")  # → Path('prompts/modules/...')

# Get Braintrust dataset ID
dataset_id = mappings.get_dataset_id("m01")  # → 'e2d331a7-e757-...'

# List all prompts with Braintrust IDs
uploaded = mappings.list_uploaded_prompts()  # → ['m01', 'm01a', ...]

# Find prompt by local file
key = mappings.find_prompt_by_file("prompts/modules/single/m08_v1_assign_attribute_ranks.md")
# → 'm08'

# Get module default
default_prompt = mappings.get_default_prompt("m01")  # → 'm01'
```

### CLI

```bash
# Show summary
python scripts/mapping_loader.py summary

# List all prompts
python scripts/mapping_loader.py list prompts

# List only uploaded prompts
python scripts/mapping_loader.py list prompts --uploaded

# List pending (not uploaded) prompts
python scripts/mapping_loader.py list prompts --pending

# Get specific prompt info
python scripts/mapping_loader.py get prompt m08

# Get specific dataset info
python scripts/mapping_loader.py get dataset m01_v3
```

## File Structure

### resource_mappings.yaml

The central mapping file with this structure:

```yaml
version: "3.0"
last_updated: "2026-01-20"
project:
  name: "Keyword-Classification-Pipeline-V1.1"
  id: "17b25eb4-95bf-499b-9ee3-1b6118546ecc"

prompts:
  m01:
    local_file: "prompts/modules/single/m01_v1_extract_own_brand_entities.md"
    schema_file: "prompts/json_schemas/single/m01_extract_own_brand_entities_schema.json"
    braintrust_id: "01cd3700-4728-4c75-9e6c-1553fddd3dce"
    braintrust_slug: "extract-own-brand-entities"
    braintrust_name: "M01_ExtractOwnBrandEntities"
    type: "extraction"
    model: "gpt-4o"

  m08_v2_pairwise:
    local_file: "prompts/modules/single/m08_v2_assign_attribute_ranks.md"
    schema_file: "prompts/json_schemas/single/m08_v2_assign_attribute_ranks_schema.json"
    braintrust_id: "2fe1c003-6750-4424-acdc-2353e19e790b"
    braintrust_slug: "assign-attribute-ranks-v2"
    braintrust_name: "M08_V2_AssignAttributeRanks"
    type: "ranking"
    model: "gpt-4o-mini"
    notes: "Pairwise comparison method"

datasets:
  m01:
    local_file: "datasets/single/m01_v1_extract_own_brand_entities.jsonl"
    braintrust_id: "e2d331a7-e757-4b66-b87d-97151470a11e"
    braintrust_name: "M01_ExtractOwnBrandEntities_V1.1"
    records: 50

module_defaults:
  m01: { prompt: "m01", dataset: "m01" }
  m08: { prompt: "m08", dataset: "m08" }

deleted_prompts:
  - id: "56e6bff2-..."
    reason: "Duplicate created by mistake"
    deleted_on: "2026-01-20"
```

### Prompt Keys

Prompt keys follow this convention:

| Key | Description |
|-----|-------------|
| `m01` | Base module prompt |
| `m01_v2` | Version 2 of module prompt |
| `m01_v3` | Version 3 of module prompt |
| `m08_v2_pairwise` | Specific variant (pairwise method) |
| `m08_v2_hierarchy` | Specific variant (hierarchy method) |

### Dataset Keys

Dataset keys follow similar convention:

| Key | Description |
|-----|-------------|
| `m01` | Base module dataset |
| `m01_v2` | Version 2 dataset |
| `m01_v3` | Version 3 dataset |
| `m06_sd1` | Variant dataset (SD1 = Sample Data 1) |
| `m08_sd1` | Variant dataset |

## Workflows

### Uploading a Prompt

```bash
# Upload and auto-update mappings
python scripts/upload/upload_prompts.py --module m08

# Upload specific file
python scripts/upload/upload_prompts.py --file prompts/modules/single/m08_v2_assign_attribute_ranks.md
```

The script automatically:
1. Uploads prompt to Braintrust
2. Updates `resource_mappings.yaml` with new Braintrust ID
3. Updates legacy `prompt_mappings.yaml` for backwards compatibility

### Checking Mapping Status

```bash
# Quick summary
python scripts/mapping_loader.py summary

# Output:
# ============================================================
# RESOURCE MAPPINGS SUMMARY
# ============================================================
# Project: Keyword-Classification-Pipeline-V1.1
# Project ID: 17b25eb4-95bf-499b-9ee3-1b6118546ecc
#
# Prompts:  15 / 32 uploaded
# Datasets: 25 / 28 uploaded
# Modules:  22 defined
```

### Finding Missing Mappings

```bash
# List prompts without Braintrust IDs
python scripts/mapping_loader.py list prompts --pending

# List all datasets
python scripts/mapping_loader.py list datasets
```

### Syncing Experiments

```bash
# Sync experiment results with Braintrust
python scripts/braintrust_sync.py --update-mappings --fetch-metadata
```

## Integration Points

### In Evaluation Scripts

```python
from scripts.mapping_loader import get_mappings

def run_evaluation(module: str):
    mappings = get_mappings()

    # Get paths
    prompt_path = mappings.get_prompt_path(module)
    dataset_path = mappings.get_dataset_path(module)

    # Get Braintrust IDs
    prompt_id = mappings.get_prompt_id(module)
    dataset_id = mappings.get_dataset_id(module)

    if not prompt_id:
        raise ValueError(f"No Braintrust ID for prompt: {module}")

    # Run evaluation...
```

### In Upload Scripts

```python
from scripts.mapping_loader import get_mappings

def after_upload(module_key: str, braintrust_id: str):
    mappings = get_mappings()
    mappings.update_prompt(module_key, {
        "braintrust_id": braintrust_id,
        "braintrust_slug": f"{module_key.replace('_', '-')}",
    })
```

## Best Practices

1. **Always use MappingLoader** - Don't hardcode Braintrust IDs in scripts
2. **Update after upload** - Scripts should auto-update mappings after uploading
3. **Use meaningful keys** - `m08_v2_pairwise` is better than `m08_v2_1`
4. **Document variants** - Add `notes` field explaining differences
5. **Track deletions** - Add to `deleted_prompts` when removing from Braintrust

## Troubleshooting

### "Mappings file not found"

```bash
# Check file exists
ls -la evaluation_KD/evaluation_experimentV5/resource_mappings.yaml
```

### "Prompt ID is None"

The prompt hasn't been uploaded to Braintrust yet:

```bash
# Check status
python scripts/mapping_loader.py get prompt m08_v2

# Upload it
python scripts/upload/upload_prompts.py --module m08
```

### "Duplicate prompt created"

1. Delete the duplicate in Braintrust UI
2. Add to `deleted_prompts` section in resource_mappings.yaml
3. Update the correct entry with the right ID

## Reference

### MappingLoader Methods

| Method | Description |
|--------|-------------|
| `get_prompt(key)` | Get full prompt dict |
| `get_prompt_id(key)` | Get Braintrust prompt ID |
| `get_prompt_path(key)` | Get local file Path |
| `get_prompt_slug(key)` | Get Braintrust slug |
| `get_schema_path(key)` | Get schema file Path |
| `get_dataset(key)` | Get full dataset dict |
| `get_dataset_id(key)` | Get Braintrust dataset ID |
| `get_dataset_path(key)` | Get local file Path |
| `find_prompt_by_file(path)` | Find key by local file |
| `find_prompt_by_braintrust_id(id)` | Find key by Braintrust ID |
| `list_prompts()` | List all prompt keys |
| `list_uploaded_prompts()` | List keys with Braintrust IDs |
| `list_unuploaded_prompts()` | List keys without IDs |
| `list_datasets()` | List all dataset keys |
| `list_modules()` | List canonical modules |
| `get_default_prompt(module)` | Get default prompt for module |
| `get_default_dataset(module)` | Get default dataset for module |
| `update_prompt(key, updates)` | Update and save prompt |
| `update_dataset(key, updates)` | Update and save dataset |
| `get_stats()` | Get mapping statistics |
| `print_summary()` | Print summary to console |
| `reload()` | Reload from file |

### Project Constants

| Constant | Value |
|----------|-------|
| Project Name | `Keyword-Classification-Pipeline-V1.1` |
| Project ID | `17b25eb4-95bf-499b-9ee3-1b6118546ecc` |
| Mappings File | `evaluation_KD/evaluation_experimentV5/resource_mappings.yaml` |
