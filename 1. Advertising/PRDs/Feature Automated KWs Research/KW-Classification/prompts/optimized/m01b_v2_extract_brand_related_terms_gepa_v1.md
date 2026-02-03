# Task: ExtractBrandRelatedTerms

Your task is to extract brand-related entities from Amazon product listings, specifically identifying sub-brands, searchable standards, and the manufacturer. Each field must be assessed based on specific criteria to ensure only relevant terms are included. The output format should be in JSON as outlined below.

## Inputs

- **brand_name**: {{brand_name}}
- **title**: {{title}}
- **bullet_points**: {{bullet_points}}
- **description**: {{description}}
- **manufacturer**: {{manufacturer}}

## Output Format

```json
{
  "sub_brands": [],
  "searchable_standards": [],
  "manufacturer": null
}
```

### FIELD 1: sub_brands

Sub-brands are named sub-brands, product families, series, or brand-owned technologies within the parent brand.

#### INCLUDE in sub_brands:
- If customers commonly search Amazon for "[sub_brand] [brand]", it qualifies as a sub-brand.
- Trademarked sub-brand names or named product series (e.g., `ColorStay`, `Cyber Commander Series`).
- Brand-owned technologies (e.g., `OMNI-HEAT`, `TrueFX`).

#### EXCLUDE from sub_brands:
- Generic product types, features, size/color variants, and marketing fluff terms (e.g., `Pill Pouch`, `Waterproof`).
- Non-search terms like `Adapti-Flex Color Lock Technology™`.

### FIELD 2: searchable_standards

These are universal industry standards that work across multiple brands and are often searched independently from any particular brand.

#### INCLUDE in searchable_standards:
- Licensed material standards and licensed audio/video tech that shoppers search specifically for (e.g., `Gore-Tex`, `Dolby Atmos`).

#### EXCLUDE from searchable_standards:
- ISO/industry standards, generic technology standards, brand-specific technologies, eco-certifications, marketing phrases, and overly technical specs (e.g., `USB-C`, `Bluetooth`, `OEKO-TEX`).
- If in doubt, default to an empty array `[]`.

### FIELD 3: manufacturer

The manufacturer is the company that manufactures the product, only if different from the brand.

#### RULES:
- If `manufacturer` is the same as or contains `brand_name` (case-insensitive), set the manufacturer to `null`.
- Otherwise, provide a JSON object with the full manufacturer name, short name, and whether it is searchable.

```json
{
  "name": "Full Manufacturer Name",
  "short": "Short Name",
  "searchable": true/false
}
```

### EXAMPLES

- **JBL Earbuds**: Identify 'Vibe Beam' as a sub-brand but not 'Deep Bass Sound' (a marketing phrase).
- **Owala Bottle**: 'FreeSip' is a sub-brand, 'BlenderBottle' is a known manufacturer, thus searchable.
- **Revlon Eyeliner**: 'ColorStay' is a sub-brand.
- **KitchenAid Mitt**: Has no named sub-brand, 'Town & Country Living' is a non-searchable manufacturer.
- **Transformers Toy**: 'Cyber Commander Series’ is a sub-brand, 'Hasbro' is a searchable manufacturer.
- **Patagonia Hoody**: No sub-brands, 'NetPlus' not included despite being mentioned as it doesn't meet criteria.
- **MYHELP Wound Care**: Contains no sub-brands or searchable standards.

This task requires careful evaluation using the criteria provided to determine the appropriate categorizations and enhance searchability and product identification on platforms like Amazon.