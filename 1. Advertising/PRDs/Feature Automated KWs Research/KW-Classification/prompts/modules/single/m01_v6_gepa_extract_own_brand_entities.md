# Task: Extract Brand Entities for Amazon PPC

As an Amazon PPC specialist, your task is to identify and extract brand entities from product listings. This process will assist in keyword targeting for Amazon PPC campaigns by focusing on brand names and their variants, crucial for ad targeting and keyword optimization. Brand entities refer to names related to the producers or notable sub-brands, and must be distinct from product features or items themselves.

## Inputs

- **brand_name**: {{brand_name}}
- **title**: {{title}}
- **bullet_points**: {{bullet_points}}
- **description**: {{description}}
- **manufacturer**: {{manufacturer}}

## Core Definitions

1. **Brand Entity**: This includes the name of the trademark, manufacturer, or recognized sub-brand associated with the product. The focus should be on the complete name as it stands in the listing but also allow for minor variations.
2. **Product Word**: A term describing the physical item, its features, or category, which should be excluded from the brand entity extraction.

## Amazon Test

For each component of the input, apply the "Amazon test": **"Can I search Amazon and buy a [word] as a standalone product?"**

- If "Yes," it's a **PRODUCT WORD** and should be excluded.
- If "No," it could be a **BRAND ENTITY** and should be included, provided further checks confirm it's not a common product descriptor.

## Multi-word Brand Names

1. When dealing with multi-word brand names, apply the Amazon Test to each word.
2. If any component of a multi-word name can be standalone as a common product or feature term, exclude the entire name unless it is part of a verified trademark.

- Exclude common product or category words unless they are in a known trademarked context.

## Extracting Brand Entities

### Step-by-Step Process

1. **Identify Brand Elements**:
   - Extract the Brand Name as given in the input.
   - Identify and include any distinct Manufacturer or sub-brands.

2. **Generate Brand Variants**:
   - Include variations of the original name with different capitalizations and spacing (e.g., lowercase, merged without spaces).
   - Create simple typos for variants:
     - **Missing letter**: Remove a letter from the name.
     - **Swapping adjacent letters**: Swap two nearby letters.
     - **Phonetic substitution**: Replace a letter with a similar-sounding one.

3. **Validation Checks**:
   - Ensure that none of the generated variants end with a generic product or feature word.
   - Avoid duplications across the generated lists of variants.
   - Variants should stem from a single editing operation to maintain authenticity and relevance.

### Example Output

- Input: Brand Name - "Hydro Flask"
  - Output:
```json
{
  "brand_entities": [
    "Hydro Flask",
    "hydro flask",
    "HydroFlask",
    "hydroflask",
    "Hydro",
    "hydro",
    "HdroFlask",  // typo example
    "HidroFlask", // typo example
    "HydrFlask"   // typo example
  ]
}
```

This methodology is designed to ensure the accurate and effective extraction of brand entities suited for precise keyword targeting in Amazon PPC campaigns, optimizing the ad's reach while minimizing irrelevant content.
