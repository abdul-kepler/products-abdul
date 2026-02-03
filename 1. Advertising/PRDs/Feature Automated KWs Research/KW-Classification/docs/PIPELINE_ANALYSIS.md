# Search Term Classification Pipeline Analysis

## Executive Summary

This document analyzes the evolution from a monolithic 2-3 prompt approach to a 16-module pipeline for classifying Amazon Advertising Search Terms. The analysis covers why the old approach failed, how the new modular architecture solves those problems, and identifies critical success factors and potential weak points.

---

## Part 1: Why the Monolithic Approach Failed

### The Old Approach (2-3 Prompts)

The original system used two main prompts:

**Prompt 1: Brand + Relation Classification**
- Combined brand detection (OB/CB/NB) with relation classification (R/S/C/N) in a single pass
- Attempted to build alias sets, apply fuzzy matching, handle stoplists, and classify relations simultaneously
- Included complex rules for head noun analysis, complement detection, and substitute identification

**Prompt 2: Attribute Extraction**
- Extracted attributes, normalized them, assigned types, and ranked them
- Tried to handle product types, variants, use cases, and audiences in one pass

### Root Causes of Failure

#### 1. Cognitive Overload
The monolithic prompts violated a fundamental principle: **LLMs perform best when focused on a single, well-defined task**. Prompt 1 alone required the model to:
- Build brand alias sets from listing content
- Apply fuzzy matching with edit distance calculations
- Maintain a stoplist of 100+ generic words
- Classify brand scope (OB/CB/NB)
- Identify product core
- Determine head nouns in keywords
- Apply relation classification (R/S/C/N)
- Handle edge cases (brand-only keywords, mixed accessory/product terms)

This is too many mental models to hold simultaneously.

#### 2. Inconsistent Intermediate Results
When brand detection fails, relation classification cascades into errors. In the monolithic approach, there was no way to verify brand detection before proceeding to relation classification.

Example failure mode:
```
Keyword: "jbl earbuds case"
Expected: OB, C (Own Brand, Complement)
Actual: NB, R (Non-Branded, Relevant)
Reason: Model missed "jbl" as brand, then misclassified relation
```

#### 3. No Validation Checkpoints
The old prompts produced final outputs with no intermediate verification. If the model made an early mistake (e.g., wrong product core identification), there was no mechanism to catch it before the final classification.

#### 4. Prompt Complexity Arms Race
Each bug fix added more rules, creating prompts that were:
- 300+ lines of instructions
- Full of edge case handling
- Increasingly brittle
- Prone to rule conflicts

The "BrandScope Validation Gate" section in Prompt 1 (lines 73-88) is evidence of this - it's a defensive patch added because the model kept making OB classification errors.

#### 5. Lack of Explicit Data Dependencies
The monolithic approach assumed the model would implicitly:
- Extract brand entities before checking brand scope
- Understand product taxonomy before determining relevance
- Identify primary use before checking substitutes

These implicit assumptions failed under edge cases.

---

## Part 2: The 4-Stage Pipeline Architecture

### Design Philosophy

The new pipeline follows the principle: **Each module does ONE thing well, with explicit inputs and outputs that can be verified.**

### Stage 1: Brand Entity Extraction

**Purpose:** Build comprehensive brand dictionaries BEFORE attempting classification.

| Module | Responsibility | Output |
|--------|---------------|--------|
| M01 | Extract raw brand entities from listing | `brand_entities` |
| M01a | Generate search variations (typos, case, phonetic) | `variations` |
| M01b | Extract related terms (sub-brands, standards, manufacturer) | `sub_brands`, `searchable_standards`, `manufacturer` |
| M03 | Same as M01 chain, but for competitor ASINs | Competitor brand dictionaries |

**Why This Works:**
- Brand extraction is isolated from classification
- Variations are generated systematically, not ad-hoc
- Related terms (like "AirPods" for Apple) are explicitly captured
- Same process runs on competitors, ensuring consistency

**Critical Success Factor:** M01a must generate variations that real users would type. Common typos ("JLB" for "JBL") and phonetic spellings are essential.

### Stage 2: Brand Scope Classification

**Purpose:** Classify each search term as OB/CB/NB using the brand dictionaries from Stage 1.

| Module   | Responsibility | Output |
|----------|---------------|--------|
| M02/M02b | Check for own brand matches | `branding_scope` = OB or null |
| M04/M04b | Check for competitor brand matches | `branding_scope` = CB or null |
| M05/M05b | Confirm non-branded (no matches found) | `branding_scope` = NB or null |

**Why This Works:**
- Each module has a single focus: one type of brand check
- V3 format includes `matched_term` and `confidence` for debugging
- Hidden brand detection catches brands not in the competitor list

**Critical Success Factor:** The brand dictionaries from Stage 1 must be comprehensive. Missing variations = missed brand matches.

### Stage 3: Product Foundation

**Purpose:** Extract product characteristics needed for relevance classification.

| Module | Responsibility | Output |
|--------|---------------|--------|
| M06 | Create hierarchical product taxonomy | `taxonomy[]` (level + product_type + rank) |
| M07 | Extract variants, use cases, audiences | `variants`, `use_cases`, `audiences` |
| M08 | Rank attributes by importance | `attribute_table[]` |
| M09 | Identify primary intended use | `primary_use` (3-6 words) |
| M10 | Validate/clean primary use | `validated_use` |
| M11 | Identify hard constraints | `hard_constraints[]` |

**Why This Works:**
- Taxonomy is built before attribute ranking (M06 -> M08 dependency)
- Primary use is identified then validated (M09 -> M10 chain)
- Hard constraints are identified AFTER primary use is validated (M10 -> M11 dependency)
- Each module's output becomes explicit input to downstream modules

**Critical Success Factors:**
1. **M09/M10 (Primary Use):** Must be 3-6 words describing what the product DOES, not features. "portable hydration" not "32oz insulated water bottle"
2. **M11 (Hard Constraints):** Must distinguish function-critical attributes from preferences. "Bluetooth" is hard constraint for wireless earbuds; "White color" is not.

### Stage 4: Relevance Classification

**Purpose:** Using all extracted data, classify search terms as R/S/C/N.

| Module  | Responsibility | Output |
|---------|---------------|--------|
| M12b    | Combined decision tree | `classification` = R/S/C/N |
| M12-M16 | Individual steps (deprecated) | Same |

**Decision Logic (M12-M16):**
```
1. Hard Constraint Check
   - Violated? -> N
   - Not violated -> Step 2

2. Product Type Check
   - Same type -> Step 3a
   - Different type -> Step 3b

3a. Same Type, Same Use?
   - Yes -> R (Relevant)
   - No -> N (Negative)

3b. Different Type, Same Use?
   - Yes -> S (Substitute)
   - No -> Step 4

4. Complementary Check
   - Used together? -> C (Complementary)
   - Not related -> N (Negative)
```

**Why This Works:**
- Hard constraints are checked FIRST (fail-fast)
- Product type check narrows the decision path
- Same primary use is the key differentiator between R/S and N/C
- Clear decision tree prevents ambiguous classifications

**Critical Success Factor:** M12 depends heavily on the quality of `validated_use` and `hard_constraints`. Garbage in = garbage out.

---

## Part 3: Data Flow Dependencies

### Critical Dependency Chain

```
M06 (taxonomy) ----+
                   |
M07 (attributes) --+--> M08 (ranked attributes)
                              |
                              v
                         M09 (primary_use)
                              |
                              v
                         M10 (validated_use)
                              |
                              v
                         M11 (hard_constraints)
                              |
                              v
                         M12-M16 (classification)
```

### Parallel Processing Opportunities

These modules can run in parallel:
- M06 and M07 (both read from listing, don't depend on each other)
- M01a and M01b (both need brand_name from M01, but don't depend on each other)
- M02, M04, M05 (all three check different brand types independently)

### Blocking Dependencies

These must run sequentially:
1. M08 requires M06 + M07 outputs
2. M09 requires M08 output
3. M10 requires M09 output
4. M11 requires M10 output
5. M12-M16 require M11 output

---

## Part 4: What Makes Each Module's Task Distinct

### Extraction vs. Classification Modules

| Type | Modules | Characteristics |
|------|---------|-----------------|
| **Extraction** | M01, M01a, M01b, M03, M06, M07 | Read product data, produce structured outputs |
| **Transformation** | M08, M09, M10 | Take structured inputs, refine/rank/validate |
| **Classification** | M02-M05, M11, M12-M16 | Apply rules to produce categorical outputs |

### Single Responsibility Principle

Each module answers ONE question:

| Module | Question Answered |
|--------|------------------|
| M01a | "What variations of this brand name would users type?" |
| M01b | "What sub-brands and standards are associated with this brand?" |
| M06 | "What product type hierarchy does this product belong to?" |
| M09 | "What is the ONE core purpose of this product?" |
| M11 | "Which attributes, if changed, would make the product non-functional?" |
| M12 | "Given all context, how should this keyword be classified?" |

---

## Part 5: Potential Weak Points

### 1. M09/M10 Primary Use Ambiguity

**Risk:** Products with multiple legitimate uses.
- Example: "Bluetooth Speaker" - is primary use "audio listening" or "portable audio"?
- Impact: Affects S vs R classification for related keywords

**Mitigation:** M09 instructions must enforce "ONE core purpose" with validation examples.

### 2. M11 Hard Constraint Over/Under-Specification

**Risk:**
- Over-specification: Marking preferences as hard constraints -> excessive N classifications
- Under-specification: Missing critical constraints -> accepting irrelevant keywords as R

**Example:**
- Product: "32oz Insulated Water Bottle"
- Is "32oz" a hard constraint?
  - If yes: "water bottle" (no size) -> N
  - If no: "24oz water bottle" -> R (wrong, different product)

**Mitigation:** M11 needs clearer rules on size/capacity products. Question to ask: "Would a customer searching for X be satisfied with this exact product?"

### 3. Brand Variation Coverage

**Risk:** M01a might miss critical typos or phonetic spellings.
- Example: "Jay-BL" for "JBL" (phonetic)
- Impact: Keywords with unusual brand spellings get classified as NB instead of OB

**Mitigation:** M01a should include common phonetic patterns and L33t-speak variations.

### 4. Competitor List Completeness

**Risk:** Unknown competitors classified as NB instead of CB.
- Example: New competitor brand not in the list

**Mitigation:** M05_V3 includes "hidden brand detection" - but this relies on the model recognizing unlisted brands. Consider maintaining a global brand database.

### 5. Complement vs. Substitute Boundary

**Risk:** Edge cases where products are both.
- Example: "Wired earphones" for a wireless earbuds product
  - Same use (audio listening) -> S
  - But if the product listing emphasizes "wireless," then "wired" could be N

**Current Logic:** M12 checks hard constraints first. If "wireless" is a hard constraint, "wired earphones" -> N.

### 6. Sequential Processing Latency

**Risk:** The critical path (M06 -> M08 -> M09 -> M10 -> M11 -> M12) requires 6 sequential LLM calls.
- Minimum latency: 6 * average_call_time

**Mitigation:**
- Cache Stage 3 outputs per ASIN (they don't change per keyword)
- Only Stage 2 (brand scope) and Stage 4 (M12) need to run per keyword

---

## Part 6: Recommendations for Module Instructions

### General Principles

1. **Start with the single question the module answers**
2. **Define output format explicitly with examples**
3. **Include negative examples (what NOT to output)**
4. **Specify what to do with edge cases**

### Module-Specific Recommendations

#### M01a (Brand Variations)
```
MUST include:
- Case variations (all-caps, all-lower, title case)
- Hyphenation/spacing variations
- Common typos (adjacent key swaps, missing letters)
- Phonetic spellings for non-English brands

MUST NOT include:
- Generic product words (even if brand sounds like one)
- Variations longer than the original + 2 characters
```

#### M09 (Primary Use)
```
FORMAT: 3-6 words, verb + noun structure

MUST describe:
- What the product DOES (action/function)
- Core purpose only

MUST NOT include:
- Features (noise cancelling, fast charging)
- Specifications (32oz, Bluetooth 5.2)
- Adjectives (premium, professional, best)
- Marketing language (ultimate, revolutionary)

EXAMPLES:
- Water Bottle -> "portable hydration"
- Earbuds -> "audio listening"
- Phone Mount -> "phone mounting" (NOT "hands-free phone viewing")
```

#### M11 (Hard Constraints)
```
QUESTION TO ASK:
"If this attribute's value is different, would the product become
IMPOSSIBLE to use for its primary intended use?"

HARD CONSTRAINT examples:
- Bluetooth for wireless earbuds (function requires it)
- iPhone 15 compatibility for iPhone 15 case (physical fit)
- 32oz for "32oz Water Bottle" (size IS the product)

NOT HARD CONSTRAINT examples:
- White color (aesthetic preference)
- 40hr battery life (nice-to-have feature)
- Brand name (not functional requirement)
```

#### M12 (Decision Tree)
```
PROCESS IN ORDER:
1. Check hard_constraints -> if violated -> N (STOP)
2. Check product_type match
   - Same type -> check primary_use
     - Same use -> R
     - Different use -> N
   - Different type -> check primary_use
     - Same use -> S
     - Different use -> check complementary
       - Commonly used together -> C
       - Not related -> N

OUTPUT MUST INCLUDE:
- classification: R|S|C|N
- reasoning: which step determined the classification
- confidence: high|medium|low
```

---

## Conclusion

The modular pipeline architecture solves the fundamental problems of the monolithic approach:

1. **Single Responsibility:** Each module does one thing well
2. **Explicit Dependencies:** Data flows are traceable and verifiable
3. **Intermediate Validation:** Outputs can be checked before downstream processing
4. **Maintainability:** Bugs can be isolated to specific modules
5. **Scalability:** Modules can be optimized independently

The key to success is ensuring each module's instructions are clear, the output formats are strict, and the data dependencies are respected in execution order.

---

*Analysis completed: January 9, 2026*
