#!/usr/bin/env python3
"""
Regenerate M01 dataset using GPT-4o to generate proper expected outputs.

This script:
1. Reads each record from the dataset
2. Uses the actual M01 prompt to generate expected output
3. Validates and saves the result
"""

import json
import os
import time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load environment
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")

INPUT_FILE = PROJECT_ROOT / "datasets" / "m01_extract_own_brand_entities.jsonl"  # Original
OUTPUT_FILE = PROJECT_ROOT / "datasets" / "m01_extract_own_brand_entities_v3.jsonl"
PROMPT_FILE = PROJECT_ROOT / "prompts" / "modules" / "m01_extract_own_brand_entities.md"

# Product words for validation
PRODUCT_WORDS = {
    'toys', 'toy', 'figure', 'figures', 'earbuds', 'earbud', 'speaker', 'speakers',
    'bottle', 'bottles', 'wallet', 'wallets', 'holder', 'holders', 'bag', 'bags',
    'case', 'cases', 'kitchen', 'bread', 'organizer', 'caddy', 'tray', 'maker',
    'phone', 'charger', 'jacket', 'shoes', 'snacks', 'drinks', 'headphones',
    'cable', 'adapter', 'stand', 'mount', 'rack', 'shelf', 'box', 'container',
    'cup', 'mug', 'plate', 'bowl', 'pan', 'pot', 'knife', 'spoon', 'fork',
    'bass', 'sound', 'audio', 'beam', 'wave', 'flow', 'ice',
}


def load_prompt() -> str:
    """Load the M01 prompt."""
    with open(PROMPT_FILE, 'r') as f:
        return f.read()


def create_user_message(record: dict) -> str:
    """Create user message with input data."""
    input_data = record.get('input', {})

    msg = f"""Extract brand entities from this product listing:

**brand_name**: {input_data.get('brand_name', '')}
**manufacturer**: {input_data.get('manufacturer', '')}
**title**: {input_data.get('title', '')}
**bullet_points**: {input_data.get('bullet_points', '')}
**description**: {input_data.get('description', '')}

Return ONLY a JSON object with this format:
{{"brand_entities": ["Entity1", "entity1", "Entty1", ...]}}

Remember:
- Max 10 entities total
- Include brand name + 3-5 typos (1 lowercase, rest spelling variations)
- Include manufacturer if different from brand + its typos
- Include sub-brands if they exist (trademarked product lines only)
- NO product words (toys, bottle, wallet, etc.)
- NO duplicates
- Each typo must be exactly 1 edit from original"""

    return msg


def validate_output(entities: list, input_data: dict) -> list:
    """Validate and fix the LLM output."""
    brand = input_data.get('brand_name', '').lower()

    # Remove duplicates (case-sensitive)
    seen = set()
    unique = []
    for e in entities:
        if e not in seen:
            unique.append(e)
            seen.add(e)

    # Remove invalid entities (ending with product words)
    valid = []
    for entity in unique:
        words = entity.lower().split()
        if words and words[-1] not in PRODUCT_WORDS:
            valid.append(entity)

    # Ensure max 10
    return valid[:10]


def generate_expected(client: OpenAI, prompt: str, record: dict, model: str = "gpt-4o") -> list:
    """Generate expected output using LLM."""
    user_msg = create_user_message(record)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_msg}
            ],
            response_format={"type": "json_object"},
            temperature=0,
            max_tokens=500
        )

        result = json.loads(response.choices[0].message.content)
        entities = result.get('brand_entities', [])

        # Validate
        return validate_output(entities, record.get('input', {}))

    except Exception as e:
        print(f"  Error: {e}")
        return []


def main():
    print("=" * 60)
    print("M01 DATASET REGENERATION WITH LLM")
    print("=" * 60)

    # Initialize
    client = OpenAI()
    prompt = load_prompt()

    # Load input
    with open(INPUT_FILE, 'r') as f:
        records = [json.loads(line) for line in f]

    print(f"Loaded {len(records)} records")
    print(f"Using model: gpt-4o")
    print()

    # Process
    output_records = []
    total_entities = 0

    for i, record in enumerate(records):
        brand = record['input'].get('brand_name', 'Unknown')
        print(f"[{i+1:3d}/{len(records)}] {brand}...", end=" ", flush=True)

        # Generate new expected
        new_entities = generate_expected(client, prompt, record)

        if new_entities:
            print(f"✓ {len(new_entities)} entities")
            total_entities += len(new_entities)
        else:
            # Fallback to original if generation failed
            new_entities = record.get('expected', {}).get('brand_entities', [])
            print(f"⚠ Using original ({len(new_entities)} entities)")

        # Update record
        record['expected']['brand_entities'] = new_entities
        output_records.append(record)

        # Rate limiting
        time.sleep(0.1)

    # Save output
    with open(OUTPUT_FILE, 'w') as f:
        for record in output_records:
            f.write(json.dumps(record) + '\n')

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total records: {len(output_records)}")
    print(f"Total entities: {total_entities}")
    print(f"Avg entities/record: {total_entities / len(output_records):.1f}")
    print(f"Output saved to: {OUTPUT_FILE}")

    # Final validation
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
                words = entity.lower().split()
                if words and words[-1] in PRODUCT_WORDS:
                    print(f"Line {i}: Product word: {entity}")
                    issues += 1

    if issues == 0:
        print("✓ All validation checks passed!")
    else:
        print(f"⚠ {issues} issues found")


if __name__ == "__main__":
    main()
