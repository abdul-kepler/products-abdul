# Synthetic Datasets Overview

## Summary

We have **23 synthetic datasets (SD01-SD22 + SD1)** with a total of **~1,747 unique products** covering all 113 Amazon product types. Each dataset is focused on specific product verticals to ensure comprehensive coverage and balanced testing.

> **Note:** When running all 5 modules (M01, M01a, M01b, M06, M07) on these datasets, we generate **~8,700+ batch requests** total.

## Dataset Distribution

| Dataset | Records | Primary Categories | Focus Area |
|---------|---------|-------------------|------------|
| SD01 | 79 | Home & Kitchen, Sports & Outdoors | Kitchen Tools & Cookware |
| SD02 | 83 | Beauty & Personal Care, Health | Hair Care & Cosmetics |
| SD03 | 91 | Beauty, Health, Baby | Skincare & Personal Care |
| SD04 | 86 | Health & Household | Vitamins & Medical Supplies |
| SD05 | 98 | Pet Supplies | Pet Food, Toys & Accessories |
| SD06 | 74 | Baby Products | Baby Feeding & Gear |
| SD07 | 100 | Clothing, Shoes & Jewelry | Fashion & Apparel |
| SD08 | 86 | Sports & Outdoors, Clothing | Fitness & Activewear |
| SD09 | 89 | Electronics | Batteries, Cables & Lighting |
| SD10 | 90 | Home & Kitchen | Home Decor & Furniture |
| SD11 | 98 | Outdoor, Tools | Camping & Outdoor Gear |
| SD12 | 71 | Tools & Home Improvement | Hand Tools |
| SD13 | 89 | Automotive | Auto Parts & Accessories |
| SD14 | 76 | Office Products, Electronics | Office Supplies & Tech |
| SD15 | 63 | Patio, Lawn & Garden | Garden & Lawn Care |
| SD16 | 87 | Grocery & Gourmet Food, Appliances | Food & Kitchen Appliances |
| SD17 | 46 | Toys & Games | Games, Puzzles & Toys |
| SD18 | 89 | Arts, Crafts & Sewing, Home | Cleaning & Craft Supplies |
| SD19 | 61 | Electronics | Smart Devices & Security |
| SD20 | 67 | Health & Household | Medical Extended |
| SD21 | 36 | Sports & Outdoors, Home | Sports & Fitness Extended |
| SD22 | 88 | Mixed | Home, Pets & Crafts |
| SD1* | 87 | Mixed | Golden Dataset (verified products) |

**Total: ~1,747 products across 23 datasets (113 product types)**

> *SD1 is a special "golden dataset" with manually verified products used for baseline testing.

---

## Detailed Breakdown

### SD01 - Kitchen Tools & Cookware
- **Records:** 79
- **Categories:** Home & Kitchen, Industrial & Scientific, Patio/Lawn/Garden, Sports & Outdoors
- **Product Types:** COOKING_POT, CUTTING_BOARD, FOOD_BLENDER, KITCHEN_KNIFE, PRESSURE_COOKER
- **Sample Brands:** Chef Craft, Spyderco, Westminster

### SD02 - Hair Care & Cosmetics
- **Records:** 83
- **Categories:** Beauty & Personal Care, Health & Household, Pet Supplies
- **Product Types:** COSMETIC_BRUSH, HAIR_DRYER, HAIR_IRON, NAIL_POLISH, SHAMPOO
- **Sample Brands:** Every Man Jack, HECLOUD, REVLON

### SD03 - Skincare & Personal Care
- **Records:** 91
- **Categories:** Baby Products, Beauty & Personal Care, Health & Household, Home & Kitchen
- **Product Types:** MASCARA, PERSONAL_FRAGRANCE, SKIN_MOISTURIZER, SUNSCREEN, TOOTHBRUSH
- **Sample Brands:** Ceramedx, Neutrogena, REVLON

### SD04 - Vitamins & Medical Supplies
- **Records:** 86
- **Categories:** Health & Household, Industrial & Scientific
- **Product Types:** BLOOD_PRESSURE_MONITOR, MEDICATION, NUTRITIONAL_SUPPLEMENT, VITAMIN, WOUND_DRESSING
- **Sample Brands:** All Terrain, Ener-C, SupreH

### SD05 - Pet Food, Toys & Accessories
- **Records:** 98
- **Categories:** Patio/Lawn/Garden, Pet Supplies, Sports & Outdoors
- **Product Types:** ANIMAL_COLLAR, PET_APPAREL, PET_BED_MAT, PET_FOOD, PET_TOY
- **Sample Brands:** Audubon Park, Cool Pup, Pets First

### SD06 - Baby Feeding & Gear
- **Records:** 74
- **Categories:** Arts/Crafts/Sewing, Baby Products, Clothing/Shoes/Jewelry, Home & Kitchen, Toys & Games
- **Product Types:** BABY_BOTTLE, BABY_COSTUME, BABY_FORMULA, PACIFIER, STROLLER
- **Sample Brands:** Dr Brown's Natural Flow, Evenflo, NUTRICIA PEPTICATE

### SD07 - Fashion & Apparel
- **Records:** 100
- **Categories:** Automotive, Clothing/Shoes/Jewelry, Toys & Games
- **Product Types:** DRESS, HAT, SHIRT, SHOES, SOCKS
- **Sample Brands:** KYLASIEN, Oilkas, U-lite

### SD08 - Fitness & Activewear
- **Records:** 86
- **Categories:** Automotive, Clothing/Shoes/Jewelry, Sports & Outdoors
- **Product Types:** BACKPACK, EXERCISE_BLOCK, EXERCISE_MAT, PAJAMAS, SWIMWEAR
- **Sample Brands:** Cherokee, MYJAJAYI, POYIPI

### SD09 - Batteries, Cables & Lighting
- **Records:** 89
- **Categories:** Cell Phones & Accessories, Electronics, Home & Kitchen, Musical Instruments, Tools
- **Product Types:** BATTERY, ELECTRONIC_CABLE, LAMP, LIGHT_BULB, POWER_BANK
- **Sample Brands:** AKASUKI, AT&T, Maxell

### SD10 - Home Decor & Furniture
- **Records:** 90
- **Categories:** Baby Products, Home & Kitchen, Patio/Lawn/Garden, Sports & Outdoors
- **Product Types:** BLANKET, CHAIR, CURTAIN, PICTURE_FRAME, RUG
- **Sample Brands:** BUTCH & harold, Huggaroo, VINTEAM

### SD11 - Camping & Outdoor Gear
- **Records:** 98
- **Categories:** Automotive, Health & Household, Home & Kitchen, Patio/Lawn/Garden, Sports & Outdoors, Tools
- **Product Types:** CANDLE, FISHING_ROD, FLASHLIGHT, PLANTER, TENT
- **Sample Brands:** Denali Firebowls, HECLOUD, WishDeal

### SD12 - Hand Tools
- **Records:** 71
- **Categories:** Automotive, Industrial & Scientific, Patio/Lawn/Garden, Tools & Home Improvement
- **Product Types:** DRILL, HAMMER_MALLET, SCREWDRIVER, TAPE_MEASURE, WRENCH
- **Sample Brands:** Hutigertech, PTSTEL, True Temper

### SD13 - Auto Parts & Accessories
- **Records:** 89
- **Categories:** Automotive, Patio/Lawn/Garden, Sports & Outdoors, Tools & Home Improvement
- **Product Types:** AUTO_OIL, AUTO_PART, VEHICLE_LIGHT_BULB, VEHICLE_TIRE, WIPER_BLADE
- **Sample Brands:** AUTOBOO, Gator parts, Zilla

### SD14 - Office Supplies & Tech
- **Records:** 76
- **Categories:** Arts/Crafts/Sewing, Cell Phones & Accessories, Electronics, Office Products, Toys & Games
- **Product Types:** CALCULATOR, FILE_FOLDER, PRINTER, SCISSORS, WRITING_INSTRUMENT
- **Sample Brands:** Actume, Chef Craft, Liene

### SD15 - Garden & Lawn Care
- **Records:** 63
- **Categories:** Health & Household, Industrial & Scientific, Patio/Lawn/Garden, Tools & Home Improvement
- **Product Types:** FERTILIZER, GRADUATED_CYLINDER, HOSE_PIPE_FITTING, LAWN_MOWER, PLANT_SEED
- **Sample Brands:** Fisher Scientific, Forcecar, Thomas & Betts

### SD16 - Food & Kitchen Appliances
- **Records:** 87
- **Categories:** Appliances, Grocery & Gourmet Food, Home & Kitchen, Industrial & Scientific
- **Product Types:** CEREAL, COFFEE, FOOD_STORAGE_CONTAINER, RICE_COOKERS, SNACK_CHIP_AND_CRISP
- **Sample Brands:** Golden Star, Hamilton Beach, UNCLE BEN'S

### SD17 - Games, Puzzles & Toys
- **Records:** 46
- **Categories:** Baby Products, Musical Instruments, Office Products, Sports & Outdoors, Toys & Games, Video Games
- **Product Types:** BOARD_GAME, JUMP_ROPE, MUSICAL_INSTRUMENTS, PUZZLES, TOY_BUILDING_BLOCK
- **Sample Brands:** Giociiol, Kappa, Mchezo

### SD18 - Cleaning & Craft Supplies
- **Records:** 89
- **Categories:** Arts/Crafts/Sewing, Automotive, Beauty, Health & Household, Home & Kitchen, Office Products
- **Product Types:** CLEANING_AGENT, CLOTHES_HANGER, LAUNDRY_DETERGENT, SEWING_MACHINE, YARN
- **Sample Brands:** Bar Keepers Friend, Lily, Soft Scrub

### SD19 - Electronics & Smart Devices
- **Records:** 61
- **Categories:** Electronics, Cell Phones & Accessories, Tools & Home Improvement
- **Product Types:** SECURITY_CAMERA, SPEAKERS, CELLULAR_PHONE, REMOTE_CONTROL, FLASH_DRIVE
- **Sample Brands:** Various electronics brands

### SD20 - Health & Medical Extended
- **Records:** 67
- **Categories:** Health & Household, Baby Products, Patio/Lawn/Garden
- **Product Types:** ORTHOPEDIC_BRACE, INCONTINENCE_PROTECTOR, PROTEIN_SUPPLEMENT_POWDER, THERMOMETER, FIRST_AID_KIT
- **Sample Brands:** Various health brands

### SD21 - Sports & Fitness Extended
- **Records:** 36
- **Categories:** Sports & Outdoors, Clothing/Shoes/Jewelry, Home & Kitchen
- **Product Types:** GOLF_CLUB, BICYCLE, DUMBBELL, WATCH, CLOCK
- **Sample Brands:** Various sports and lifestyle brands

### SD22 - Home, Pets & Crafts Mixed
- **Records:** 88
- **Categories:** Arts/Crafts/Sewing, Clothing/Shoes/Jewelry, Tools, Pet Supplies, Home & Kitchen
- **Product Types:** PAINT, EARRING, LOCK, ANIMAL_CARRIER, LITTER_BOX, VACUUM_CLEANER, AIR_PURIFIER, GLITTER
- **Sample Brands:** Various home and craft brands

### SD1 - Golden Dataset (Mixed Categories)
- **Records:** 87
- **Categories:** Home & Kitchen, Automotive, Industrial & Scientific, Electronics, Health & Household
- **Product Types:** CAMERA_DIGITAL, VEHICLE_MAT, WOUND_DRESSING, SYRINGE, FOOD_STORAGE_BAG
- **Note:** This is a special "golden dataset" with manually verified products used for baseline testing and validation.

---

## Category Coverage Matrix

| Category | Datasets |
|----------|----------|
| Home & Kitchen | SD01, SD03, SD06, SD09, SD10, SD11, SD16, SD18, SD21, SD22 |
| Beauty & Personal Care | SD02, SD03, SD18 |
| Health & Household | SD02, SD03, SD04, SD11, SD15, SD18, SD20 |
| Pet Supplies | SD02, SD05, SD06, SD08, SD09, SD11, SD14, SD22 |
| Clothing, Shoes & Jewelry | SD06, SD07, SD08, SD21, SD22 |
| Sports & Outdoors | SD01, SD05, SD08, SD10, SD11, SD13, SD17, SD21 |
| Electronics | SD09, SD14, SD19 |
| Tools & Home Improvement | SD09, SD11, SD12, SD13, SD15, SD19, SD22 |
| Automotive | SD07, SD08, SD09, SD11, SD12, SD13, SD18 |
| Baby Products | SD03, SD06, SD10, SD17, SD20 |
| Toys & Games | SD06, SD07, SD14, SD17 |
| Patio, Lawn & Garden | SD01, SD05, SD10, SD11, SD12, SD13, SD15, SD20 |
| Office Products | SD14, SD17, SD18 |
| Grocery & Gourmet Food | SD16 |
| Arts, Crafts & Sewing | SD06, SD14, SD18, SD22 |
| Appliances | SD16, SD22 |
| Industrial & Scientific | SD01, SD04, SD09, SD12, SD15, SD16, SD18 |
| Cell Phones & Accessories | SD09, SD14, SD19 |

---

## Product Type Coverage

All **113 product types** from the Keepa export are now covered:

| SD Group | Product Types (Count) |
|----------|----------------------|
| SD01-SD18 | 90 original types |
| SD19 | SECURITY_CAMERA, SPEAKERS, CELLULAR_PHONE, REMOTE_CONTROL, FLASH_DRIVE |
| SD20 | ORTHOPEDIC_BRACE, INCONTINENCE_PROTECTOR, PROTEIN_SUPPLEMENT_POWDER, THERMOMETER, FIRST_AID_KIT |
| SD21 | GOLF_CLUB, BICYCLE, DUMBBELL, WATCH, CLOCK |
| SD22 | PAINT, EARRING, LOCK, ANIMAL_CARRIER, LITTER_BOX, VACUUM_CLEANER, AIR_PURIFIER, GLITTER |

---

## Usage in Pipeline

These datasets are used in the following module pipeline:

```
Synthetic Data (SD01-SD22)
         │
         ├──► M01: Extract Own Brand Entities
         ├──► M01a: Extract Own Brand Variations
         ├──► M01b: Extract Brand Related Terms
         ├──► M06: Generate Product Type Taxonomy
         └──► M07: Extract Product Attributes
                    │
                    ▼
              M08: Assign Attribute Ranks
                    │
                    ▼
              M09: Identify Primary Intended Use
                    │
                    ▼
              M10: Validate Primary Intended Use
                    │
                    ▼
              M11: Identify Hard Constraints
```

---

## File Location

- **Raw synthetic datasets:** `datasets/synthetic/`
- **Labeled results:** `datasets/synthetic_labeled/`
- **Experiment results:** `experiment_results/`
- **Readable CSVs:** `experiment_results_readable/`

---

*Generated: January 2026*
