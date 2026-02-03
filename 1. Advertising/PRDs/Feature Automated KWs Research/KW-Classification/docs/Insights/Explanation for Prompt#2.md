1\. **Attribute Text**  
**What it is:**  
 The **normalized, shopper-facing value** that represents a real product characteristic.  
**Key rules:**

* Canonical form (merge synonyms, fix casing, unify units)  
* No duplicates or stylistic variants  
* Should be something a shopper would recognize or filter by

**Examples:**

* Ready to Eat (not “Heat & Eat”, “Ready-made”)  
* USB-C (not “Type C”, “USB Type-C”)  
* 12 Ounce (not “12oz”, “12 oz”)  
* Gluten-Free (not “No Gluten”)

**Think of it as:**  
*“The clean attribute value that could appear in filters, bullets, or structured data.”*  
2\. **Attribute Type**  
**What it is:**  
 The **semantic role** the attribute plays in defining or selling the product.  
You only allow four types (by design):  
• Product Type  
Defines **what the product fundamentally is**.

* Hierarchical  
* Used for taxonomy & browse nodes

Examples:

* Wireless Bluetooth Headphones  
* Headphones  
* Audio Accessories

• Variant  
Defines **how this product differs from other versions of the same product**.

* Comparable across SKUs  
* Often filterable

Examples:

* Gluten-Free  
* Noise Cancelling  
* 12 Ounce  
* 2 Pack

• Use Case  
Defines **why / when / how the product is used**.

* Situational or functional  
* Strongly impacts conversion when explicit

Examples:

* Dinner  
* Travel  
* Workout  
* Everyday Use

• Audience  
Defines **who the product is intended for**.

* Demographic or role-based  
* Strong when explicit, weak when generic

Examples:

* Kids  
* Adults  
* Students  
* Family

**Think of Attribute Type as:**  
*“What dimension of meaning this attribute contributes.”*  
3\. **Variant Subtype**  
*(Only applies when Attribute Type \= Variant)*  
**What it is:**  
 A **controlled classification of the variant’s nature**, used for ranking logic and consistency.  
Allowed values:

* Size  
* Pack Size  
* Flavor  
* Color  
* Material  
* Format  
* Dietary Preference  
* Feature  
* Other

**Why it exists:**  
 Because **not all variants are equally important**.  
Example:

* Gluten-Free → Dietary Preference (very high impact)  
* Ready to Eat → Format (mid impact)  
* 12 Ounce → Size (lower impact)  
* Round Shape → Feature (trivial)

**Think of Variant Subtype as:**  
*“What kind of choice the shopper is making.”*  
4\. **Rank (per Attribute Type)**  
**What it is:**  
 A **relative importance order** within each Attribute Type.  
Product Type Ranking

* Most specific → broadest  
* Mirrors taxonomy depth

Example:

* Wireless Bluetooth Headphones  
* Headphones  
* Audio Accessories

Variant Ranking  
One continuous ladder (not reset per subtype)

* Ranked by **conversion criticality**

General rule of thumb:

* **Non-negotiable / deal-breaker** (e.g., Organic, Vegan, Certified)  
* **Core format or function** (e.g., Noise Cancelling, Ready to Eat)  
* **Secondary features**  
* **Size / pack**  
* **Obvious or tautological traits**

Use Case & Audience Ranking

* Ranked by **how strongly they drive purchase intent**  
* Explicit, primary use \> generic or implied use

Examples:

* Shockproof Protection \> Everyday Use  
* Kids \> All Ages

**Think of Rank as:**  
*“If space or attention is limited, what must be shown first.”*  
One-sentence summary  
This terminology separates **what the product is**, **how it varies**, **why it’s used**, and **who it’s for**, then ranks each signal by **how much it actually influences conversion and discovery**.  
If you want, next we can:  
Formalize this into a **machine-readable schema**  
Stress-test edge cases (e.g., models, series, compatibility)

* Align it directly with **Amazon facets & indexing behavior**

