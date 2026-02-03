# Caching Strategy for 16-Module Pipeline

## Executive Summary

This document defines the caching architecture for the Amazon keyword classification pipeline. The key insight is that **Stage 3 outputs (M06-M11) are ASIN-specific, not keyword-specific**, meaning they can be computed once per product and reused for all keywords.

---

## Pipeline Stage Analysis

### Stage 1: Brand Entity Extraction (M01, M01a, M01b, M03)
**Caching Level:** ASIN
**Reasoning:** Brand entities are extracted from product data, not keywords
**Cache Key:** `{asin}`
**TTL:** 24 hours (product data rarely changes)

### Stage 2: Brand Scope Classification (M02, M04, M05)
**Caching Level:** ASIN + Keyword
**Reasoning:** Depends on both product's brand entities AND the keyword
**Cache Key:** `{asin}:{keyword_hash}`
**TTL:** 1 hour (keyword-specific, high volume)

### Stage 3: Product Foundation (M06-M11)
**Caching Level:** ASIN ONLY
**Reasoning:** These modules analyze the PRODUCT, not the keyword
**Cache Key:** `{asin}`
**TTL:** 24 hours

### Stage 4: Relevance Classification (M12-M16)
**Caching Level:** ASIN + Keyword
**Reasoning:** Final classification depends on keyword-product relationship
**Cache Key:** `{asin}:{keyword_hash}`
**TTL:** 1 hour

---

## Stage 3 Deep Dive: Maximum Caching Opportunity

### Module Outputs (All ASIN-Only)

| Module | Output | Why ASIN-Only |
|--------|--------|---------------|
| M06 | Product Type | Determined by product taxonomy |
| M07 | Core Attributes | Extracted from product bullets/description |
| M08 | Attribute Table | Structured from product data |
| M09 | Primary Intended Use | Derived from product function |
| M10 | Validated Primary Use | Validation of M09 output |
| M11 | Hard Constraints | Product specifications |

### Performance Impact

```
Without Caching:
- 100 keywords × 6 modules = 600 LLM calls
- ~600 × 0.5s = 300s latency
- ~600 × $0.01 = $6.00 cost

With ASIN-Level Caching:
- 1st keyword: 6 LLM calls (cold cache)
- 2nd-100th keywords: 0 LLM calls (cache hits)
- Total: 6 LLM calls
- ~6 × 0.5s = 3s latency (per ASIN)
- ~6 × $0.01 = $0.06 cost (per ASIN)

Savings: 99% reduction after warm-up
```

---

## Cache Implementation Architecture

### Redis Schema

```python
# Stage 1: Brand Entities (ASIN-level)
key: "brand_entities:{asin}"
value: {
    "own_brand": {...},
    "competitors": [...],
    "computed_at": "2025-01-09T10:00:00Z"
}
ttl: 86400  # 24 hours

# Stage 3: Product Foundation (ASIN-level)
key: "product_foundation:{asin}"
value: {
    "m06_product_type": {...},
    "m07_core_attributes": {...},
    "m08_attribute_table": {...},
    "m09_primary_use": {...},
    "m10_validated_use": {...},
    "m11_hard_constraints": {...},
    "computed_at": "2025-01-09T10:00:00Z"
}
ttl: 86400  # 24 hours

# Stage 2 & 4: Keyword-specific (ASIN + Keyword)
key: "brand_scope:{asin}:{keyword_hash}"
value: {
    "branding_scope": "OB|CB|NB",
    "confidence": 0.95,
    "matched_term": "...",
    "computed_at": "2025-01-09T10:00:00Z"
}
ttl: 3600  # 1 hour

key: "relevance:{asin}:{keyword_hash}"
value: {
    "classification": "R|S|C|N",
    "confidence": 0.95,
    "reasoning": "...",
    "computed_at": "2025-01-09T10:00:00Z"
}
ttl: 3600  # 1 hour
```

### Python Cache Wrapper

```python
import hashlib
import json
from functools import wraps
from typing import Optional, Callable
import redis

class PipelineCache:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    @staticmethod
    def hash_keyword(keyword: str) -> str:
        """Create consistent hash for keyword."""
        return hashlib.sha256(keyword.lower().strip().encode()).hexdigest()[:16]

    def get_product_foundation(self, asin: str) -> Optional[dict]:
        """Get cached Stage 3 outputs for ASIN."""
        key = f"product_foundation:{asin}"
        data = self.redis.get(key)
        return json.loads(data) if data else None

    def set_product_foundation(self, asin: str, data: dict, ttl: int = 86400):
        """Cache Stage 3 outputs for ASIN."""
        key = f"product_foundation:{asin}"
        self.redis.setex(key, ttl, json.dumps(data))

    def get_brand_scope(self, asin: str, keyword: str) -> Optional[dict]:
        """Get cached brand scope classification."""
        key = f"brand_scope:{asin}:{self.hash_keyword(keyword)}"
        data = self.redis.get(key)
        return json.loads(data) if data else None

    def set_brand_scope(self, asin: str, keyword: str, data: dict, ttl: int = 3600):
        """Cache brand scope classification."""
        key = f"brand_scope:{asin}:{self.hash_keyword(keyword)}"
        self.redis.setex(key, ttl, json.dumps(data))

    def get_relevance(self, asin: str, keyword: str) -> Optional[dict]:
        """Get cached relevance classification."""
        key = f"relevance:{asin}:{self.hash_keyword(keyword)}"
        data = self.redis.get(key)
        return json.loads(data) if data else None

    def set_relevance(self, asin: str, keyword: str, data: dict, ttl: int = 3600):
        """Cache relevance classification."""
        key = f"relevance:{asin}:{self.hash_keyword(keyword)}"
        self.redis.setex(key, ttl, json.dumps(data))


def cached_asin_only(cache_key_prefix: str, ttl: int = 86400):
    """Decorator for ASIN-only cached functions."""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(self, asin: str, *args, **kwargs):
            cache = getattr(self, 'cache', None)
            if cache:
                key = f"{cache_key_prefix}:{asin}"
                cached = cache.redis.get(key)
                if cached:
                    return json.loads(cached)

            result = func(self, asin, *args, **kwargs)

            if cache and result:
                cache.redis.setex(key, ttl, json.dumps(result))

            return result
        return wrapper
    return decorator


def cached_asin_keyword(cache_key_prefix: str, ttl: int = 3600):
    """Decorator for ASIN+Keyword cached functions."""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(self, asin: str, keyword: str, *args, **kwargs):
            cache = getattr(self, 'cache', None)
            if cache:
                kw_hash = PipelineCache.hash_keyword(keyword)
                key = f"{cache_key_prefix}:{asin}:{kw_hash}"
                cached = cache.redis.get(key)
                if cached:
                    return json.loads(cached)

            result = func(self, asin, keyword, *args, **kwargs)

            if cache and result:
                kw_hash = PipelineCache.hash_keyword(keyword)
                cache.redis.setex(f"{cache_key_prefix}:{asin}:{kw_hash}", ttl, json.dumps(result))

            return result
        return wrapper
    return decorator
```

### Usage in Pipeline

```python
class KeywordClassificationPipeline:
    def __init__(self, redis_client: redis.Redis):
        self.cache = PipelineCache(redis_client)
        self.llm = LLMClient()

    @cached_asin_only("product_foundation", ttl=86400)
    def compute_product_foundation(self, asin: str) -> dict:
        """Compute Stage 3 outputs - cached at ASIN level."""
        product_data = self.fetch_product_data(asin)

        # Run M06-M11 (only runs if not cached)
        m06_result = self.run_m06(product_data)
        m07_result = self.run_m07(product_data)
        m08_result = self.run_m08(product_data, m07_result)
        m09_result = self.run_m09(product_data, m08_result)
        m10_result = self.run_m10(m09_result, product_data)
        m11_result = self.run_m11(product_data, m08_result)

        return {
            "m06_product_type": m06_result,
            "m07_core_attributes": m07_result,
            "m08_attribute_table": m08_result,
            "m09_primary_use": m09_result,
            "m10_validated_use": m10_result,
            "m11_hard_constraints": m11_result,
        }

    @cached_asin_keyword("brand_scope", ttl=3600)
    def classify_brand_scope(self, asin: str, keyword: str) -> dict:
        """Run M02/M04/M05 - cached at ASIN+Keyword level."""
        brand_entities = self.get_brand_entities(asin)

        # M02: Own Brand check
        m02_result = self.run_m02(keyword, brand_entities)
        if m02_result["branding_scope"] == "OB":
            return m02_result

        # M04: Competitor Brand check
        m04_result = self.run_m04(keyword, brand_entities)
        if m04_result["branding_scope"] == "CB":
            return m04_result

        # M05: Non-Branded confirmation
        m05_result = self.run_m05(keyword, brand_entities)
        return m05_result

    @cached_asin_keyword("relevance", ttl=3600)
    def classify_relevance(self, asin: str, keyword: str) -> dict:
        """Run M12-M16 - cached at ASIN+Keyword level."""
        foundation = self.compute_product_foundation(asin)  # Uses cache

        m12_result = self.run_m12(keyword, foundation)
        return m12_result

    def classify_keyword(self, asin: str, keyword: str) -> dict:
        """Full pipeline - maximally cached."""
        # Stage 2: Brand Scope (keyword-specific)
        brand_scope = self.classify_brand_scope(asin, keyword)

        # Stage 3: Product Foundation (ASIN-only, cached)
        foundation = self.compute_product_foundation(asin)

        # Stage 4: Relevance (keyword-specific)
        relevance = self.classify_relevance(asin, keyword)

        return {
            "branding_scope": brand_scope["branding_scope"],
            "relation": relevance["classification"],
            "confidence": min(brand_scope["confidence"], relevance["confidence"]),
            "foundation": foundation,
        }
```

---

## Batch Processing Optimization

### Batch by ASIN Strategy

```python
def process_keyword_batch(self, keywords: list[tuple[str, str]]) -> list[dict]:
    """
    Process keywords batch, grouped by ASIN for cache efficiency.

    Args:
        keywords: List of (asin, keyword) tuples

    Returns:
        List of classification results
    """
    # Group by ASIN
    by_asin = defaultdict(list)
    for asin, keyword in keywords:
        by_asin[asin].append(keyword)

    results = []

    for asin, asin_keywords in by_asin.items():
        # Warm cache with product foundation (1 call per ASIN)
        foundation = self.compute_product_foundation(asin)

        # Process all keywords for this ASIN
        for keyword in asin_keywords:
            result = self.classify_keyword(asin, keyword)
            results.append((asin, keyword, result))

    return results
```

---

## Cache Invalidation

### When to Invalidate

| Event | Invalidate |
|-------|------------|
| Product data updated | `product_foundation:{asin}`, `brand_entities:{asin}` |
| Brand entities changed | `brand_entities:{asin}`, all `brand_scope:{asin}:*` |
| Prompt updated | All caches for affected module |
| Full refresh | All caches |

### Invalidation Commands

```python
def invalidate_asin(self, asin: str):
    """Invalidate all caches for an ASIN."""
    patterns = [
        f"product_foundation:{asin}",
        f"brand_entities:{asin}",
        f"brand_scope:{asin}:*",
        f"relevance:{asin}:*",
    ]
    for pattern in patterns:
        if "*" in pattern:
            for key in self.redis.scan_iter(pattern):
                self.redis.delete(key)
        else:
            self.redis.delete(pattern)

def invalidate_module(self, module: str):
    """Invalidate caches when a prompt is updated."""
    # Map module to cache patterns
    module_cache_map = {
        "M06": ["product_foundation:*"],
        "M07": ["product_foundation:*"],
        "M08": ["product_foundation:*"],
        "M09": ["product_foundation:*"],
        "M10": ["product_foundation:*"],
        "M11": ["product_foundation:*"],
        "M02": ["brand_scope:*"],
        "M04": ["brand_scope:*"],
        "M05": ["brand_scope:*"],
        "M12": ["relevance:*"],
    }
    patterns = module_cache_map.get(module, [])
    for pattern in patterns:
        for key in self.redis.scan_iter(pattern):
            self.redis.delete(key)
```

---

## Cost Savings Analysis

### Assumptions
- 100 keywords per ASIN
- $0.01 per LLM call (average)
- 6 Stage 3 modules

### Without Caching
```
Per ASIN: 100 keywords × 16 modules = 1,600 calls
Cost: 1,600 × $0.01 = $16.00 per ASIN
```

### With ASIN-Level Caching (Stage 3)
```
Per ASIN:
- Stage 1: 4 calls (ASIN-level, cached after first)
- Stage 2: 100 × 3 = 300 calls (keyword-specific)
- Stage 3: 6 calls (ASIN-level, cached after first)
- Stage 4: 100 × 5 = 500 calls (keyword-specific)

First keyword: 4 + 3 + 6 + 5 = 18 calls
Remaining 99: 99 × (3 + 5) = 792 calls (Stage 1 & 3 from cache)

Total: 18 + 792 = 810 calls
Cost: 810 × $0.01 = $8.10 per ASIN

Savings: 49% reduction
```

### With Haiku for Pattern Matching (Additional)
```
If M01a, M02-M05 use Haiku ($0.00025/call instead of $0.01):

Stage 2 (Haiku): 300 × $0.00025 = $0.075
Stage 1 partial (Haiku): 50% = $0.05
Stage 3 (Sonnet): 6 × $0.01 = $0.06
Stage 4 (Sonnet): 500 × $0.01 = $5.00

Total: $5.185 per ASIN
Savings: 68% reduction from baseline
```

---

## Implementation Checklist

- [ ] Set up Redis instance for caching
- [ ] Implement `PipelineCache` class
- [ ] Add `@cached_asin_only` decorator to Stage 3 modules
- [ ] Add `@cached_asin_keyword` decorator to Stage 2/4 modules
- [ ] Implement batch processing with ASIN grouping
- [ ] Add cache invalidation endpoints
- [ ] Monitor cache hit rates
- [ ] Set up TTL tuning based on data change frequency
