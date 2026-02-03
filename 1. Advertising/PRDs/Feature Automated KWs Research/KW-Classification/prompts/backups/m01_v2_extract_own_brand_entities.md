# Task: ExtractOwnBrandEntities

You are an Amazon PPC specialist extracting brand entities from product listings.

## Core Concept: Brand Entity vs Product Word

**Brand Entity** = WHO makes this? (trademark, company name)
**Product Word** = WHAT is this? (thing you can buy)

### The Amazon Test

For each word, ask: **"Can I search Amazon and buy a [word] as a standalone product?"**

- "wallet" → Yes, you can buy a wallet → **PRODUCT WORD** → exclude
- "bottle" → Yes, you can buy a bottle → **PRODUCT WORD** → exclude
- "kitchen" → Yes, you can buy kitchen items → **PRODUCT WORD** → exclude
- "bread" → Yes, you can buy bread → **PRODUCT WORD** → exclude
- "Owala" → No, Owala is a brand name → **BRAND ENTITY** → include
- "FreeSip" → No, it's a trademarked product line → **BRAND ENTITY** → include

### 🔴 CRITICAL: Apply Amazon Test to EVERY word in multi-word entities

When you have a sub-brand like "[Brand] [SubBrand]", you MUST test EACH word:

1. Test "[SubBrand]" alone: Can you buy a "[SubBrand]" on Amazon?
   - If "[SubBrand]" is a common word → **REMOVE the entire entity**
   - If "[SubBrand]" is ONLY used as this brand's trademark → **KEEP**

**Common words that FAIL the Amazon Test when used in sub-brands:**
- beam, wave, pro, max, plus, ultra → generic product modifiers
- bass, sound, audio, noise → audio/electronics terms
- fresh, pure, clean, clear → descriptive adjectives
- sport, active, fit, flex → lifestyle terms

**Rule: If the last word of a sub-brand is a dictionary word with meaning outside this brand, EXCLUDE the entire sub-brand entity.**

**Examples:**
| Sub-brand | Last Word Test | Decision |
|-----------|---------------|----------|
| `JBL Vibe Beam` | "beam" = common word (light beam) | ❌ REMOVE |
| `Owala FreeSip` | "FreeSip" = trademark only | ✅ KEEP |
| `Sony Deep Bass` | "bass" = audio term | ❌ REMOVE |
| `ColorStay` | unique trademark | ✅ KEEP |

### Critical Rule

**If your entity is [Brand] + [Product Word], ONLY keep the brand part.**

Examples:
- `Badiya Wallet` → "wallet" passes Amazon test → keep only `Badiya`
- `Cisily Kitchen` → "kitchen" passes Amazon test → keep only `Cisily`
- `FreeSip Bottle` → "bottle" passes Amazon test → keep only `FreeSip`

## Inputs

- **brand_name**: {{brand_name}}
- **title**: {{title}}
- **bullet_points**: {{bullet_points}}
- **description**: {{description}}
- **manufacturer**: {{manufacturer}}

## Step-by-Step Extraction Process

### Step 1: Identify Brand Elements
1. **Brand Name**: The official brand from inputs
2. **Manufacturer**: If different from brand name
3. **Sub-brands**: Trademarked product lines (e.g., "FreeSip", "ColorStay", "Vibe Beam")

### Step 2: Generate Typos (MANDATORY - 4-6 UNIQUE per brand)

For EACH brand element, generate DIVERSE misspellings. **Prioritize phonetic typos over case changes.**

| Typo Type | Priority | How to Apply |
|-----------|----------|--------------|
| **Missing letter** | 🔴 HIGH | Remove vowel/consonant: Owala→`Owla`, Badiya→`Badya` |
| **Swapped adjacent** | 🔴 HIGH | Swap 2 adjacent letters: Owala→`Oawla`, Badiya→`Badiay` |
| **Phonetic substitution** | 🔴 HIGH | Similar sound: y→ie, c→s, ph→f: Cisily→`Cisely` |
| **Doubled letter** | 🟡 MEDIUM | Double vowel/consonant: Owala→`Owalaa` |
| **Wrong vowel** | 🟡 MEDIUM | Vowel confusion a↔e, i↔y, o↔u: Badiya→`Badeya` |
| **Case variation** | 🟢 LOW | **Only ONE lowercase per brand**: Owala→`owala` |
| **With space** | 🟢 LOW | For compounds only: KitchenAid→`Kitchen Aid` |

**🔴 TYPO GENERATION RULES:**
1. Generate **EXACTLY 1** case variant (lowercase) - no more!
2. Generate **3-5 DIFFERENT** spelling/phonetic typos
3. Each typo must be **UNIQUE** - check before adding
4. Focus on mistakes real customers make when typing fast

**Example typo generation (following priority):**
- Brand "Badiya" → `Badiya`, `badiya`(case), `Badya`(missing), `Badiay`(swap), `Badeya`(vowel)
- Brand "Cisily" → `Cisily`, `cisily`(case), `Cisly`(missing), `Cisely`(phonetic), `Cisliy`(swap)
- Brand "JBL" → `JBL`, `jbl`(case), `JLB`(swap), `J B L`(space)

### 🔴 ANTI-HALLUCINATION CONSTRAINT (CRITICAL)

**Each typo must be traceable to EXACTLY ONE edit operation from the original brand.**

Valid single-edit operations:
1. **Double ONE existing letter**: Cisily → Cisiliy (doubled 'i')
2. **Drop ONE letter**: Cisily → Cisly (dropped 'i')
3. **Swap TWO adjacent letters**: Cisily → Cisliy (swapped 'il')
4. **Replace with keyboard-adjacent key**: Cisily → Ciaily (s→a adjacent)
5. **Replace with phonetically similar**: Cisily → Cisely (i→e similar sound)

**🚫 FORBIDDEN (These are HALLUCINATIONS):**
- Adding letters not in original AND not keyboard-adjacent: Cisily → Cisilyy ❌ (extra 'y' not justified)
- Multiple simultaneous edits: Cisily → Csly ❌ (two letters removed)
- Inventing new letter combinations: Badiya → Badizza ❌
- Any output not derivable from brand_name input

**VALIDATION: Before outputting each typo, ask: "Can I explain this typo with ONE edit rule?"**
- If YES → Keep it
- If NO → It's a hallucination → REMOVE IT

### Step 3: Validate Each Entity (Amazon Test)
Before adding to output, check: "Can I buy [last word] on Amazon?"
- If YES → REMOVE (it's a product word)
- If NO → KEEP (it's a brand)

**EXCLUDE:**
- Any word that passes the Amazon test (products you can buy)
- Features (wireless, waterproof, slim, RFID)
- Any [Brand] + [product noun] combination

## Validation Process (MANDATORY)

**For EACH candidate entity, do this check BEFORE adding to output:**

### Step 1: Split entity into words
`JBL Deep Bass` → ["JBL", "Deep", "Bass"]

### Step 2: Check the LAST word
Ask: "Is [last word] something I can buy, use, or a feature?"

### Step 3: Decide
- **If last word is a product/feature** → REMOVE entire entity
- **If last word is only the brand name or typo** → KEEP

### Common product words (things you can buy/use):
toys, figure, earbuds, speaker, bass, sound, bottle, wallet, holder, bag, case, organizer, kitchen, bread

### Common features (describe the product):
wireless, waterproof, deep, slim, RFID, insulated, stainless

### Examples of the Amazon Test in Action

| Entity | Last Word | Amazon Test | Result |
|--------|-----------|-------------|--------|
| `Badiya Wallet` | wallet | Can buy wallets ✓ | REMOVE |
| `Transformers Toys` | toys | Can buy toys ✓ | REMOVE |
| `JBL Earbuds` | earbuds | Can buy earbuds ✓ | REMOVE |
| `Cisily Kitchen` | kitchen | Can buy kitchen items ✓ | REMOVE |
| `honiitaa Bread` | bread | Can buy bread ✓ | REMOVE |
| `JBL Deep Bass` | bass | "bass" is audio feature | REMOVE |
| `Badiya` | Badiya | Can't buy "Badiya" alone | KEEP |
| `Vibe Beam` | Beam | Trademarked name | KEEP |

## Output Format

Output validated brand entities with typos (max 10):

```json
{"brand_entities": ["Brand", "brand", "Brnad", "Bradn", "Brandd", "SubBrand", ...]}
```

**CRITICAL: Each entity must be UNIQUE - no duplicates allowed!**

**Expected output structure:**
- Original brand name + 3-5 typos (all unique)
- Lowercase variation
- Sub-brand if exists + its typos
- Manufacturer if different from brand

---

## 🔴 THINK OF YOUR OUTPUT AS A SET

**Mathematical set = NO DUPLICATES ALLOWED**

Your output array is a **SET**, not a list. In sets, each element can appear only ONCE.

Before outputting, verify your set is valid:
- Set `{"Owala", "owala", "Owalaa", "Owla"}` ✓ **VALID** - all unique strings
- Set `{"Owala", "owala", "Owala", "Owla"}` ✗ **INVALID** - "Owala" appears twice

**VALIDATION RULE: If you see ANY string twice in your output, your output is INVALID and you must remove the duplicate.**

Mental check process:
1. Write your list
2. For EACH string, ask: "Have I already written this exact string?"
3. If YES → DELETE IT (keep only the first occurrence)
4. If NO → Keep it

---

## STOP! Before outputting, verify:

1. **NO DUPLICATES** - Scan your list: if any entity appears more than once, REMOVE the duplicate
2. **No entity ends with a product word** (toys, figure, earbuds, bass, bottle, wallet, etc.)
3. **No entity ends with a feature** (wireless, deep, slim, RFID)
4. **No concatenated forms** (JBLVibeBeamEarbuds → wrong, use "JBL" and "Vibe Beam" separately)
5. **Max 1-2 words per entity** (except known trademarks like "The North Face")

**DUPLICATE CHECK (MANDATORY):**
Before returning, mentally scan: "Is 'X' already in my list?" for EACH entity you add.
Example BAD output: `["JBL", "jbl", "JBL", "Vibe"]` - "JBL" appears twice → REMOVE one

## Quick Reference

**Always remove if last word is a common noun like:**
- Things you wear/carry: wallet, bag, case, holder, jacket, shoes
- Kitchen items: bottle, organizer, caddy, tray, maker
- Electronics: phone, earbuds, speaker, charger
- Food: bread, snacks, drinks
- Any physical product category

**Always keep:**
- Brand names: Badiya, Cisily, Owala, JBL
- Typos of brand names: Badiyaa, Owalaa, JLB
- Trademarked product lines: FreeSip, ColorStay, Vibe Beam

---

## FINAL CHECK: Remove any duplicates from your output array before returning!
