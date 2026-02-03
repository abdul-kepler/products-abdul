# Task: Extract Brand Entities with Variations

You are tasked with extracting brand entities and their variations from product listings on Amazon. This involves identifying the primary brand name, sub-brands, product lines, and manufacturers, creating a set of potential misspellings or variations, and excluding generic product words.

## Inputs

- **brand_name**: {{brand_name}}
- **title**: {{title}}
- **bullet_points**: {{bullet_points}}
- **description**: {{description}}
- **manufacturer**: {{manufacturer}}

## Task Steps:

### Step 1: Identify Brand Elements
- **Brand Name**: Extracted directly from the inputs.
- **Manufacturer**: Extract if different from the brand name.
- **Sub-brands/Product Lines**: Identify unique sub-brands or product lines, particularly trademarked terms like "FreeSip", "ColorStay", etc.

### Step 2: Validate Brand Entities
- Use the "Amazon Test" for validation: Can the word be purchased as a standalone product on Amazon?
  - If YES, it is a product word and should be excluded.
  - If NO, it is a brand entity and should be included.

### Step 3: Generate Typos and Variants
1. **Exact Case Variant**: One lowercase or slight variation of the case.
2. **Phonetic Substitutions**: Replace similar sounding parts of the word (e.g., 'ph' -> 'f').
3. **Adjacent Key Substitution**: Replace letters with adjacent keyboard characters if applicable.
4. **Single Edit Variations**:
   - **Drop a Letter**: Remove one letter.
   - **Swap Adjacent Letters**: Swap two adjacent letters.
   - **Duplicate a Letter**: Duplicate a letter.
   - **Vowel Replacement**: Confuse vowels with similar sounding ones.
5. **Valid Composite Structures**: If a brand includes multiple words like "Cyber Commander Series", keep them in a plausible, non-generic formation.

### Step 4: Exclusion and Filtering
- Discard any variations that form common nouns or product categories ("wallet", "bottle", etc.).
- Avoid feature-specific final words which indicate it’s a product description ("wireless", "slim", etc.).
- Each word in multi-word brands needs individual validation.

### Step 5: Final Validation
- Check the final set for duplicates.
- If a conflict arises where a variation looks like a product or feature word, prefer exclusion unless it's integral to the brand's identity.

### Output Format:

```json
{
  "brand_entities": ["UniqueBrandName", "variation1", "variation2", ...]
}
```

- **Unique Entries**: The output should contain unique variations only.
- **Complete Entities**: Ensure the final list has all validated variations for identified brands and sub-brands, including the manufacturer if applicable and different.

## Example of Outputs: 

- Input Brand Name: "Owala"
- Expected Output: `{"brand_entities": ["Owala", "owala", "Owla", "Oawla", "Owalaa", "FreeSip"]}`

**Note**: Adjust the expected output based on each input scenario, considering unique brand names, sub-brands, and manufacturers listed in the provided textual inputs.
