#!/usr/bin/env python3
"""
Regenerate M01 dataset with proper expected outputs following ALL prompt rules.

Rules from prompt:
1. Brand Elements: Brand + Manufacturer (if different) + Sub-brands
2. Typos: 4-6 UNIQUE per brand (1 lowercase + 3-5 spelling typos)
3. Single-edit: Each typo = exactly 1 edit operation
4. Amazon Test: Exclude entities ending with product words
5. Max 10 entities total
6. No duplicates (case-sensitive)
"""

import json
import os
import re
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI

# Load environment
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")

INPUT_FILE = PROJECT_ROOT / "datasets" / "m01_extract_own_brand_entities_v2.jsonl"
OUTPUT_FILE = PROJECT_ROOT / "datasets" / "m01_extract_own_brand_entities_v3.jsonl"

# Product words and features to exclude
PRODUCT_WORDS = {
    'toys', 'toy', 'figure', 'figures', 'earbuds', 'earbud', 'speaker', 'speakers',
    'bottle', 'bottles', 'wallet', 'wallets', 'holder', 'holders', 'bag', 'bags',
    'case', 'cases', 'kitchen', 'bread', 'organizer', 'caddy', 'tray', 'maker',
    'phone', 'charger', 'jacket', 'shoes', 'snacks', 'drinks', 'headphones',
    'cable', 'adapter', 'stand', 'mount', 'rack', 'shelf', 'box', 'container',
    'cup', 'mug', 'plate', 'bowl', 'pan', 'pot', 'knife', 'spoon', 'fork',
}

FEATURES = {
    'wireless', 'waterproof', 'deep', 'slim', 'rfid', 'insulated', 'stainless',
    'portable', 'rechargeable', 'bluetooth', 'electric', 'automatic', 'digital',
    'pro', 'max', 'plus', 'ultra', 'mini', 'lite', 'bass', 'sound', 'audio',
    'noise', 'fresh', 'pure', 'clean', 'clear', 'sport', 'active', 'fit', 'flex',
    'beam', 'wave', 'flow', 'stream', 'air', 'ice', 'hot', 'cold',
}


def generate_typos(word: str) -> list[str]:
    """Generate valid single-edit typos for a word."""
    if not word or len(word) < 2:
        return []

    typos = set()
    word_lower = word.lower()

    # 1. Lowercase variant (exactly 1)
    if word != word_lower:
        typos.add(word_lower)

    # 2. Missing letter (drop 1 letter)
    for i in range(len(word)):
        typo = word[:i] + word[i+1:]
        if typo and typo.lower() != word_lower:
            typos.add(typo)

    # 3. Swapped adjacent letters
    for i in range(len(word) - 1):
        typo = word[:i] + word[i+1] + word[i] + word[i+2:]
        if typo.lower() != word_lower:
            typos.add(typo)

    # 4. Doubled letter
    for i in range(len(word)):
        typo = word[:i+1] + word[i] + word[i+1:]
        if typo.lower() != word_lower:
            typos.add(typo)

    # 5. Phonetic substitutions (common ones)
    phonetic_map = {
        'y': ['i', 'ie', 'ee'],
        'i': ['y', 'e', 'ee'],
        'c': ['s', 'k'],
        's': ['c', 'z'],
        'k': ['c', 'ck'],
        'ph': ['f'],
        'f': ['ph'],
        'a': ['e', 'u'],
        'e': ['a', 'i'],
        'o': ['u', 'a'],
        'u': ['o', 'oo'],
    }

    for old, replacements in phonetic_map.items():
        if old in word.lower():
            for new in replacements:
                # Case-preserving replacement
                idx = word.lower().find(old)
                if idx >= 0:
                    typo = word[:idx] + new + word[idx+len(old):]
                    if typo.lower() != word_lower:
                        typos.add(typo)

    # 6. With space for compound words (CamelCase)
    if any(c.isupper() for c in word[1:]):
        spaced = re.sub(r'([a-z])([A-Z])', r'\1 \2', word)
        if spaced != word:
            typos.add(spaced)

    # Return unique typos, prioritizing diversity
    result = []

    # First add lowercase if exists
    if word_lower in typos:
        result.append(word_lower)
        typos.remove(word_lower)

    # Then add other typos (max 5 more for total of 4-6)
    for typo in sorted(typos, key=lambda x: (len(x), x)):
        if len(result) >= 5:
            break
        result.append(typo)

    return result


def is_valid_entity(entity: str) -> bool:
    """Check if entity passes the Amazon Test."""
    words = entity.lower().split()
    if not words:
        return False

    last_word = words[-1]

    # Check against product words and features
    if last_word in PRODUCT_WORDS or last_word in FEATURES:
        return False

    return True


def extract_brand_from_invalid(entity: str) -> Optional[str]:
    """Extract brand part from invalid [Brand] [ProductWord] entity."""
    words = entity.split()
    if len(words) < 2:
        return None

    last_word = words[-1].lower()
    if last_word in PRODUCT_WORDS or last_word in FEATURES:
        return ' '.join(words[:-1])

    return None


def generate_expected_output(input_data: dict) -> list[str]:
    """Generate expected brand_entities following all prompt rules."""
    brand_name = input_data.get('brand_name', '')
    manufacturer = input_data.get('manufacturer', '')
    title = input_data.get('title', '')

    entities = []
    seen = set()  # For case-sensitive deduplication

    def add_entity(entity: str):
        """Add entity if unique and valid."""
        if entity and entity not in seen and len(entities) < 10:
            if is_valid_entity(entity):
                entities.append(entity)
                seen.add(entity)

    def add_with_typos(word: str):
        """Add word and its typos."""
        if not word:
            return

        # Add original
        add_entity(word)

        # Add typos
        for typo in generate_typos(word):
            add_entity(typo)

    # 1. Add brand name + typos
    add_with_typos(brand_name)

    # 2. Add manufacturer if different from brand
    if manufacturer and manufacturer.lower() != brand_name.lower():
        add_with_typos(manufacturer)

    # 3. Try to extract sub-brands from title (trademarked product lines)
    # Look for capitalized words after brand name that aren't product words
    if title and brand_name:
        # Simple heuristic: find capitalized words near brand
        words = title.split()
        for i, word in enumerate(words):
            # Skip the brand name itself
            if word.lower() == brand_name.lower():
                continue

            # Check if it's a potential sub-brand (capitalized, not a product word)
            if word[0].isupper() and word.lower() not in PRODUCT_WORDS and word.lower() not in FEATURES:
                # Check if it's likely a trademark (not a common English word)
                if len(word) > 2 and not word.lower() in {'the', 'and', 'for', 'with', 'new', 'best', 'top', 'great'}:
                    # Only add if it seems like a product line name
                    if word.isalpha() and len(entities) < 8:  # Leave room for typos
                        add_entity(word)

    return entities


def validate_and_fix_record(record: dict) -> dict:
    """Validate and fix a single record's expected output."""
    input_data = record.get('input', {})
    original_expected = record.get('expected', {}).get('brand_entities', [])

    # Generate new expected output
    new_expected = generate_expected_output(input_data)

    # Also preserve any valid entities from original that we might have missed
    seen = set(e.lower() for e in new_expected)
    for entity in original_expected:
        if entity.lower() not in seen and is_valid_entity(entity) and len(new_expected) < 10:
            new_expected.append(entity)
            seen.add(entity.lower())

    # Final validation: remove duplicates (case-sensitive)
    final = []
    final_seen = set()
    for entity in new_expected:
        if entity not in final_seen:
            final.append(entity)
            final_seen.add(entity)

    record['expected']['brand_entities'] = final[:10]  # Enforce max 10
    return record


def main():
    print("=" * 60)
    print("M01 DATASET REGENERATION")
    print("=" * 60)

    # Load input
    with open(INPUT_FILE, 'r') as f:
        records = [json.loads(line) for line in f]

    print(f"Loaded {len(records)} records from {INPUT_FILE.name}")

    # Process each record
    fixed_records = []
    stats = {
        'total': len(records),
        'modified': 0,
        'entities_before': 0,
        'entities_after': 0,
    }

    for i, record in enumerate(records):
        original_entities = record.get('expected', {}).get('brand_entities', [])
        stats['entities_before'] += len(original_entities)

        fixed_record = validate_and_fix_record(record)
        new_entities = fixed_record['expected']['brand_entities']
        stats['entities_after'] += len(new_entities)

        if set(original_entities) != set(new_entities):
            stats['modified'] += 1

        fixed_records.append(fixed_record)

        if (i + 1) % 20 == 0:
            print(f"  Processed {i + 1}/{len(records)} records...")

    # Save output
    with open(OUTPUT_FILE, 'w') as f:
        for record in fixed_records:
            f.write(json.dumps(record) + '\n')

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total records: {stats['total']}")
    print(f"Modified records: {stats['modified']}")
    print(f"Entities before: {stats['entities_before']}")
    print(f"Entities after: {stats['entities_after']}")
    print(f"Output saved to: {OUTPUT_FILE}")

    # Validation check
    print()
    print("=" * 60)
    print("VALIDATION")
    print("=" * 60)

    issues = 0
    with open(OUTPUT_FILE, 'r') as f:
        for i, line in enumerate(f, 1):
            record = json.loads(line)
            entities = record['expected']['brand_entities']

            # Check duplicates
            if len(set(entities)) != len(entities):
                print(f"Line {i}: Has duplicates!")
                issues += 1

            # Check max 10
            if len(entities) > 10:
                print(f"Line {i}: More than 10 entities!")
                issues += 1

            # Check product words
            for entity in entities:
                if not is_valid_entity(entity):
                    print(f"Line {i}: Invalid entity: {entity}")
                    issues += 1

    if issues == 0:
        print("✓ All validation checks passed!")
    else:
        print(f"⚠ {issues} issues found")


if __name__ == "__main__":
    main()
