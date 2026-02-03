# Experiment Tracking Architecture Plan

## Problem Statement

Need a single source of truth for experiment results that feeds:
1. **Main Dashboard** - Heatmap view of all modules
2. **Module Pages** - Detailed view per module with history
3. **Future: Google Sheets** - For PM/stakeholder visibility

Currently data is scattered across:
- `modules_data.js` - JavaScript embedded data
- `progress_history.yaml` - YAML tracking
- `judge_results/*.json` - Raw judge outputs
- Braintrust - External platform

---

## Requirements

### Must Have
- [ ] Single data source for all dashboards
- [ ] Track: module, prompt_version, model, pass_rate, match_rate
- [ ] Support multiple experiments per module
- [ ] Easy to update (manual or automated)
- [ ] Version history preserved

### Should Have
- [ ] Links to Braintrust experiments
- [ ] Suggested improvements per version
- [ ] Dataset version tracking (separate from prompt version)
- [ ] Rubric-level breakdown (which rubrics pass/fail)

### Nice to Have
- [ ] Auto-sync from Braintrust API
- [ ] Google Sheets integration for PM visibility
- [ ] Diff view between versions

---

## Data Model

### Option A: Single JSON file per module

```
tracking_dashboard/
└── data/
    └── modules/
        ├── m01.json
        ├── m01a.json
        ├── m02.json
        └── ...
```

**m01.json structure:**
```json
{
  "module_id": "m01",
  "module_name": "ExtractOwnBrandEntities",
  "description": "Extract brand entities from product listings",
  "primary_rubric": "M01_brand_extracted",

  "experiments": [
    {
      "experiment_id": "m01_v1_gpt4omini_20260120",
      "prompt_version": "v1",
      "dataset_version": "v1",
      "model": "gpt-4o-mini",
      "timestamp": "2026-01-20T00:31:46",

      "metrics": {
        "pass_rate": 30.0,
        "match_rate": 10.0,
        "total_evaluations": 50,
        "pass": 15,
        "fail": 35,
        "error": 0
      },

      "rubric_breakdown": {
        "M01_brand_extracted": { "pass": 5, "fail": 45, "rate": 10.0 },
        "M01_lowercase_included": { "pass": 40, "fail": 10, "rate": 80.0 },
        "M01_typos_realistic": { "pass": 35, "fail": 15, "rate": 70.0 }
      },

      "links": {
        "braintrust_id": "e6720eee-6f86-4b87-966b-0591de5ce8a5",
        "braintrust_url": "https://braintrust.dev/app/...",
        "data_source": "M01_ExtractOwnBrandEntities_v1_150126_1.csv"
      },

      "suggestions": [
        {
          "rubric": "M01_brand_extracted",
          "issue": "Missing brand extraction for medical products",
          "suggestion": "Add explicit examples for medical/pharmaceutical brands",
          "priority": "high",
          "status": "applied",
          "applied_in": "v2"
        }
      ]
    },
    {
      "experiment_id": "m01_v2_gpt4o_20260120",
      "prompt_version": "v2",
      "...": "..."
    }
  ],

  "latest": {
    "prompt_version": "v5",
    "best_pass_rate": 58.4,
    "best_model": "gpt-4o-mini"
  }
}
```

**Pros:**
- Self-contained per module
- Easy to read/edit manually
- Git-friendly (can see diffs)
- No database needed

**Cons:**
- Need to aggregate for heatmap
- Potential duplication of suggestions

---

### Option B: Centralized JSON with index

```
tracking_dashboard/
└── data/
    ├── experiments_index.json    # Summary for heatmap
    ├── experiments/
    │   ├── m01_v1_gpt4omini.json
    │   ├── m01_v2_gpt4o.json
    │   └── ...
    └── modules_meta.json         # Module descriptions
```

**experiments_index.json (for heatmap):**
```json
{
  "last_updated": "2026-01-21T18:00:00",
  "modules": {
    "m01": {
      "v1": { "pass_rate": 30, "match_rate": 10, "model": "gpt-4o-mini" },
      "v2": { "pass_rate": 45, "match_rate": 30, "model": "gpt-4o" },
      "v3": { "pass_rate": 60, "match_rate": 40, "model": "gpt-5" },
      "v4": { "pass_rate": 54, "match_rate": 35, "model": "gpt-4o" },
      "v5": { "pass_rate": 58, "match_rate": 40, "model": "gpt-4o-mini" }
    },
    "m01a": {
      "v1": { "pass_rate": 59, "match_rate": 20, "model": "gpt-4o-mini" },
      "v2": { "pass_rate": 85, "match_rate": 60, "model": "gpt-5" }
    }
  }
}
```

**Pros:**
- Fast heatmap loading (single file)
- Detailed data separate
- Scalable

**Cons:**
- Need to keep index in sync
- Two places to update

---

### Option C: YAML + JSON hybrid

```
tracking_dashboard/
└── data/
    ├── progress.yaml             # Human-editable summary
    ├── experiments.json          # Machine-generated details
    └── suggestions.yaml          # Human-editable improvements
```

**Pros:**
- YAML is more readable for manual edits
- JSON for machine data

**Cons:**
- Mixed formats
- Need conversion scripts

---

### Option D: Google Sheets as source

```
Google Sheets (source of truth)
    ↓ (sync script)
tracking_dashboard/data/modules_data.js
    ↓ (loaded by)
Dashboard HTML pages
```

**Sheets structure:**
| Module | Version | Model | Pass Rate | Match Rate | BT Link | Suggestions |
|--------|---------|-------|-----------|------------|---------|-------------|
| m01 | v1 | gpt-4o-mini | 30% | 10% | link | ... |
| m01 | v2 | gpt-4o | 45% | 30% | link | ... |

**Pros:**
- PM can view/edit
- Familiar interface
- Easy collaboration

**Cons:**
- Requires API setup
- Network dependency
- Rate limits

---

## Recommended Architecture

### Hybrid: Option A + Index file

```
tracking_dashboard/
└── data/
    ├── heatmap_index.json        # Auto-generated for fast heatmap
    ├── modules/
    │   ├── m01.json              # Full module data
    │   ├── m01a.json
    │   └── ...
    └── sync_scripts/
        ├── build_index.py        # Generate heatmap_index from modules/
        ├── import_judge.py       # Import from judge_results/
        └── export_sheets.py      # Future: sync to Google Sheets
```

### Workflow

1. **After judge run:**
   ```bash
   python sync_scripts/import_judge.py judge_results/m01_v5_judge_xxx.json
   # → Updates data/modules/m01.json
   # → Regenerates data/heatmap_index.json
   ```

2. **Dashboard loads:**
   - Heatmap: `fetch('data/heatmap_index.json')`
   - Module page: `fetch('data/modules/m01.json')`

3. **Manual suggestions:**
   - Edit `data/modules/m01.json` directly
   - Run `build_index.py` to refresh

---

## Migration Plan

### Phase 1: Create data structure
- [ ] Create `tracking_dashboard/data/modules/` folder
- [ ] Define JSON schema for module files
- [ ] Create template `m01.json` with current data

### Phase 2: Build sync scripts
- [ ] `import_judge.py` - Import judge results
- [ ] `build_index.py` - Generate heatmap index
- [ ] Update dashboards to use new data source

### Phase 3: Migrate existing data
- [ ] Convert `progress_history.yaml` → JSON modules
- [ ] Import all existing judge results
- [ ] Verify dashboards work

### Phase 4: (Future) External integrations
- [ ] Google Sheets sync
- [ ] Braintrust API integration
- [ ] Automated CI/CD updates

---

## Decisions Made

| Question | Decision | Notes |
|----------|----------|-------|
| Granularity | **Aggregates + rubric breakdown** | Per-sample not needed, but split by rubric |
| Historical retention | **Keep ALL experiments** | Full history preserved |
| Suggestions on heatmap | **No** | Only on module pages |
| Multi-model display | See analysis below | |

---

## Multi-Model Strategy (Analysis)

**Problem:** One prompt version (e.g., v3) can be tested on multiple models (gpt-4o-mini, gpt-4o, gpt-5). How to show this?

### Option 4A: Best result per version (current approach)
```
Heatmap cell [m01, v3] → shows 60% (gpt-5) - the best result
```
- **Pros:** Simple, clean heatmap
- **Cons:** Hides model comparison, may mislead

### Option 4B: Separate rows per model
```
| Module      | V1  | V2  | V3  |
|-------------|-----|-----|-----|
| M01 (4o-mini) | 30% | 45% | 57% |
| M01 (4o)      | -   | 45% | 54% |
| M01 (gpt-5)   | -   | -   | 60% |
```
- **Pros:** Full transparency
- **Cons:** Table gets 3x larger, sparse

### Option 4C: Model toggle/filter
```
[Toggle: gpt-4o-mini | gpt-4o | gpt-5 | Best]

Heatmap shows only selected model's results
```
- **Pros:** Clean view, user choice
- **Cons:** More UI complexity

### Option 4D: Sub-cells with mini indicators
```
| Module | V1       | V2       | V3           |
|--------|----------|----------|--------------|
| M01    | 30% (m)  | 45% (4o) | 60%/54%/57%  |
```
- **Pros:** All data visible
- **Cons:** Cluttered, hard to read

### Recommendation: **4C (Model toggle) + 4A fallback**

1. Default view: Show **best result** per module+version
2. Add toggle to filter by specific model
3. Tooltip on hover shows all models tested

**Implementation:**
```javascript
// heatmap_index.json structure
{
  "m01": {
    "v3": {
      "best": { "pass_rate": 60, "model": "gpt-5" },
      "by_model": {
        "gpt-4o-mini": { "pass_rate": 57, "match_rate": 40 },
        "gpt-4o": { "pass_rate": 54, "match_rate": 35 },
        "gpt-5": { "pass_rate": 60, "match_rate": 40 }
      }
    }
  }
}
```

---

## Katerina's Metrics (from CSV)

Based on her tracker template, key metrics she cares about:

| Metric | Description | Source |
|--------|-------------|--------|
| LLM Model | Which model was used | Experiment config |
| Prompt version | v1, v2, v3... | Prompt file |
| Pass Rate % | LLM Judge average | Judge results |
| Match Rate % | Expected vs Actual | Judge results (primary rubric) |
| Suggested Improvements | What to fix | Manual analysis |

**Additional metrics we track:**
- Dataset version (V1, V2, V3) - when test cases change
- Rubric breakdown - which specific checks pass/fail
- Braintrust links - for drill-down
- Timestamp - when experiment ran

---

## Final Data Schema

### Module JSON (`data/modules/m01.json`)

```json
{
  "module_id": "m01",
  "module_name": "ExtractOwnBrandEntities",
  "description": "Extract brand entities from product listings",
  "primary_rubric": "M01_brand_extracted",

  "experiments": [
    {
      "id": "m01_v1_gpt4omini_20260120",
      "prompt_version": "v1",
      "dataset_version": "v1",
      "model": "gpt-4o-mini",
      "timestamp": "2026-01-20T00:31:46",

      "metrics": {
        "pass_rate": 30.0,
        "match_rate": 10.0,
        "total": 50,
        "pass": 15,
        "fail": 35
      },

      "rubrics": {
        "M01_brand_extracted": { "pass": 5, "total": 50, "rate": 10.0 },
        "M01_lowercase_included": { "pass": 40, "total": 50, "rate": 80.0 },
        "M01_typos_realistic": { "pass": 35, "total": 50, "rate": 70.0 }
      },

      "braintrust_url": "https://braintrust.dev/app/..."
    }
  ],

  "suggestions": [
    {
      "version": "v1",
      "rubric": "M01_brand_extracted",
      "issue": "Missing brand extraction for medical products",
      "suggestion": "Add explicit examples for medical brands",
      "priority": "high",
      "status": "applied",
      "applied_in": "v2"
    }
  ]
}
```

### Heatmap Index (`data/heatmap_index.json`)

```json
{
  "generated_at": "2026-01-21T19:00:00",
  "modules": {
    "m01": {
      "name": "ExtractOwnBrandEntities",
      "versions": {
        "v1": {
          "best": { "pass_rate": 30, "match_rate": 10, "model": "gpt-4o-mini" },
          "by_model": {
            "gpt-4o-mini": { "pass_rate": 30, "match_rate": 10 }
          }
        },
        "v3": {
          "best": { "pass_rate": 60, "match_rate": 40, "model": "gpt-5" },
          "by_model": {
            "gpt-4o-mini": { "pass_rate": 57, "match_rate": 38 },
            "gpt-4o": { "pass_rate": 54, "match_rate": 35 },
            "gpt-5": { "pass_rate": 60, "match_rate": 40 }
          }
        }
      }
    }
  }
}
```

---

## Next Steps

1. [x] Document architecture decisions
2. [ ] Create `tracking_dashboard/data/modules/` folder structure
3. [ ] Create template JSON for one module (m01)
4. [ ] Build `import_judge.py` script
5. [ ] Build `build_heatmap_index.py` script
6. [ ] Update heatmap dashboard to use new data source
7. [ ] Add model toggle to heatmap UI
