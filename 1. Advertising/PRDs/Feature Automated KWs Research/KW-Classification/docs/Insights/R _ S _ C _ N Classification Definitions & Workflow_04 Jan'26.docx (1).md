# **Keyword Classification System**

R / S / C / N Classification Definitions & Workflow

# **Part 1: Classification Definitions**

Keywords are classified into four categories based on their relationship to the ASIN (product). This classification determines bidding strategy and campaign structure.

## **Relevant (R)**

**Definition:** Keywords that describe the **same product type** as the ASIN and support the **same primary intended use**.

| Example ASIN | Keyword | Why Relevant |
| ----- | ----- | ----- |
| Stainless Steel Water Bottle | insulated water bottle | Same product type, same use (portable hydration) |
| Wireless Bluetooth Earbuds | wireless earphones | Same product type, same use (personal audio listening) |
| Memory Foam Pillow | bed pillow | Same product type, same use (head/neck support during sleep) |

## **Substitute (S)**

**Definition:** Keywords that describe a **different product type** but satisfy the **same primary intended use** as the ASIN.

| Example ASIN | Keyword | Why Substitute |
| ----- | ----- | ----- |
| Stainless Steel Water Bottle | plastic tumbler | Different product type, but still satisfies portable hydration |
| Wireless Bluetooth Earbuds | wired headphones | Different product type, but still satisfies personal audio listening |
| Memory Foam Pillow | buckwheat pillow | Different product type, but still satisfies head/neck support during sleep |

## **Complementary (C)**

**Definition:** Keywords that describe a **different product** that is **commonly used together** with the ASIN.

| Example ASIN | Keyword | Why Complementary |
| ----- | ----- | ----- |
| Stainless Steel Water Bottle | bottle cleaning brush | Used to maintain/clean the bottle |
| Wireless Bluetooth Earbuds | earbud carrying case | Used to store/protect the earbuds |
| Memory Foam Pillow | silk pillowcase | Used as a cover for the pillow |

## **Negative (N)**

**Definition:** Keywords that fall into any of the following conditions:

* **Violates a hard constraint** — incompatible specification makes purchase pointless  
* **Same product type but different primary use**  
* **Different product type, different use, and not used together**

| Example ASIN | Keyword | Why Negative |
| ----- | ----- | ----- |
| Stainless Steel Water Bottle (32oz) | 64oz water jug | Hard constraint violation (size incompatibility) |
| Wireless Bluetooth Earbuds | gaming headset with mic | Same category but different primary use (gaming communication vs. music listening) |
| Memory Foam Pillow | throw pillow | Same product type but different use (decoration vs. sleep support) |

# **Part 2: Classification Workflow (Prompts 9–16)**

**Context:** Prompts 1–8 have already been completed, producing the **Product Type Taxonomy** (from Prompt 6\) and **Attributes Taxonomy** (from Prompt 8). The workflow below replaces the previous Prompts 9–12 with an improved approach.

## **Phase 1: Establish Product Foundation**

### **Prompt 9: Identify Primary Intended Use**

**Purpose:** Determine the single, core reason the product exists.

**Inputs:**

* Product Title  
* Bullets, Description & Other Attributes  
* Product Type Taxonomy (Prompt 6 output)  
* Attributes Taxonomy (Prompt 8 output)

**Question:** *"Based only on the product information below, identify the single primary intended use of this product. Respond with ONE short phrase (3–6 words). Do not include secondary uses, features, benefits, or marketing language."*

**Output:** A 3–6 word phrase describing the primary intended use.

### **Prompt 10: Validate Primary Intended Use**

**Purpose:** Ensure the intended use phrase is clean and usable for classification.

**Input:** Output from Prompt 9

**Validation Criteria:**

* Describes what the product does, not how well it performs  
* No features, specifications, technologies, or materials  
* No adjectives, marketing language, or quality claims  
* Contains only ONE core action/purpose  
* 3–6 words long

**Output:**

* **VALID** → Use Prompt 9 output going forward  
* **Rewritten phrase** → Use this rewritten phrase going forward

### **Prompt 11: Identify Hard Constraints**

**Purpose:** Determine which product attributes are non-negotiable for the product to function.

**Inputs:**

* Validated Intended Use (from Prompt 9 or 10\)  
* Product Title  
* Bullets, Description & Other Attributes  
* Product Type Taxonomy (Prompt 6 output)  
* Attributes Taxonomy (Prompt 8 output)

**Question Applied to Each Attribute:** *"If this attribute's value is different, would the product become impossible to use for its intended function?"*

**Output:** List of attributes marked Yes (hard constraint) or No (soft constraint). Store only attributes marked "Yes" as the Hard Constraints list.

## **Phase 2: Keyword Classification**

Each keyword is processed through the following decision tree:

### **Prompt 12: Hard Constraint Violation Check**

**Question:** *"Does the keyword explicitly violate any hard constraint?"*

**Inputs:**

* Keyword  
* List of Hard Constraints (from Prompt 11\)  
* Product Title, Bullets, Description & Other Attributes  
* Product Type Taxonomy (Prompt 6 output)  
* Attributes Taxonomy (Prompt 8 output)

**Output:**

* **YES** → **NEGATIVE** (End)  
* **NO** → Proceed to Prompt 13

### **Prompt 13: Product Type Check**

**Question:** *"Is the keyword asking for the same product type as the ASIN?"*

**Output:**

* **YES** → Proceed to Prompt 14  
* **NO** → Proceed to Prompt 15

### **Prompt 14: Primary Intended Use Check (Same Product Type)**

**Question:** *"Does the keyword's product support the same primary use as the ASIN?"*

**Output:**

* **YES** → **RELEVANT** (End)  
* **NO** → **NEGATIVE** (End)

### **Prompt 15: Substitute Check (Different Product Type)**

**Question:** *"Does the keyword describe a different product that still satisfies the same primary use?"*

**Output:**

* **YES** → **SUBSTITUTE** (End)  
* **NO** → Proceed to Prompt 16

### **Prompt 16: Complementary Check**

**Question:** *"Is the keyword for a product commonly used together with this product?"*

**Output:**

* **YES** → **COMPLEMENTARY** (End)  
* **NO** → **NEGATIVE** (End)

## **Quick Reference Summary**

| Step | Question | If YES | If NO |
| :---: | ----- | :---: | :---: |
| **12** | Violates hard constraints? | **NEGATIVE** | → Step 13 |
| **13** | Same product type? | → Step 14 | → Step 15 |
| **14** | Same primary use? (same type) | **RELEVANT** | **NEGATIVE** |
| **15** | Same primary use? (diff type) | **SUBSTITUTE** | → Step 16 |
| **16** | Used together? | **COMPLEMENTARY** | **NEGATIVE** |

## **Decision Flowchart Summary**

The classification logic can be summarized as:

1. **Violates hard constraints?** → Yes → **NEGATIVE**  
2. **Same product type?**   
* → Yes → Same primary use?  → Yes → **RELEVANT**  
* → Yes → Same primary use?  → No → **NEGATIVE**  
3. **Different product type, same primary use?** → Yes → **SUBSTITUTE**  
4. **Used together?** → Yes → **COMPLEMENTARY**  
5. **Else** → **NEGATIVE**