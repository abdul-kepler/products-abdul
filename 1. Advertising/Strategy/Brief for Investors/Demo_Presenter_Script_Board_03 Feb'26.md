# Investor Demo - Presenter Script

**Date:** February 3, 2026
**Duration:** 10-15 minutes
**Presenter:** Abdul
**Audience:** Board / Investors

---

## Pre-Demo Checklist (DO TODAY - Feb 2)

### Actions to Take NOW for Passive Features to Show Tomorrow

| Action | Purpose | How to Verify |
|--------|---------|---------------|
| 1. Ensure test ASIN has **30+ days of data** | Bid optimization logs will have history | Check bid logs in UI |
| 2. Verify **Auto Budget** is enabled for test ASIN | Budget distribution will be visible | Campaign Config shows budget per campaign |
| 3. Check that **at least one search term was harvested** | Show harvesting output | Check Harvested Terms list |
| 4. Check that **at least one search term was negated** | Show negation output | Check Negated Terms list |
| 5. Run **KW Research** on test ASIN if not done | Fresh AI output to show | Check KW Research results |
| 6. Run **Target ASIN Research** if not done | Competitor qualification results | Check ASIN Research output |
| 7. Verify **at least one campaign was auto-generated** | Show campaign generation | Check for SPAS campaigns |
| 8. Take **screenshots** of bid logs showing changes | Backup if live system is slow | Save to presentation folder |
| 9. Note down **specific numbers** to reference | "This ASIN went from 45% to 28% ACOS" | Write on notecard |

### System Check (Morning of Demo)

- [ ] Platform is accessible and logged in
- [ ] Test ASIN data is loading correctly
- [ ] No error messages on Campaign Config screen
- [ ] Screenshots are ready as backup
- [ ] Notes/numbers are ready

---

## Demo Script

### OPENING (30 seconds)

**[Screen: Title slide or platform homepage]**

**SAY:**
> "Thank you for your time today. I'm going to walk you through a live demo of our Ad SaaS Platform. This is the product that's now ready for rollout to our first test customers.
>
> In the next 12-15 minutes, I'll show you the complete end-to-end workflow - from onboarding an ASIN to automated optimization. I'll cover both the features you can see working immediately, and the ones that work behind the scenes over time."

---

### PART 1: THE PROBLEM (1 minute)

**[Screen: Can stay on homepage or show a simple slide]**

**SAY:**
> "First, let me remind you of the problem we're solving.
>
> Managing Amazon PPC at scale is incredibly manual. An agency managing 100 ASINs might have thousands of keywords, hundreds of campaigns. Nobody can optimize 24/7. Nobody can catch every underperforming keyword, adjust every bid at the right time, or reallocate budget in real-time.
>
> That's what our platform does. It automates the entire lifecycle - from keyword discovery to campaign creation to ongoing optimization.
>
> Let me show you how."

---

### PART 2: ACTIVE FEATURES (6-7 minutes)

#### Step 1: Campaign Configuration (1.5 minutes)

**[Screen: Navigate to Campaign Config]**

**ACTION:**
1. Click on "Campaign Config" in the navigation
2. Click the ASIN dropdown
3. Select your test ASIN (e.g., "Product 2 - B09C5PRFGQ")

**SAY:**
> "This is our Campaign Configuration screen. Let me select an ASIN we're testing.
>
> [Select ASIN]
>
> You can see the four match types for Auto campaigns: Close Match, Loose Match, Substitute, and Complimentary. Each one can be independently controlled."

**ACTION:**
1. Point to the Status toggle (show it's ON)
2. Point to Default Bid field
3. Point to Budget field
4. Point to Target ACOS field

**SAY:**
> "For each match type, we set:
> - Status: On or Off
> - Default Bid: Starting bid amount
> - Budget: Daily budget
> - Target ACOS: Our efficiency target
>
> Notice the timestamps showing 'Last updated' - every change is logged. This gives Account Managers full visibility and accountability.
>
> When we submit this, campaigns are created directly in Amazon - no need to go to Seller Central."

**TRANSITION:**
> "But how do we know which keywords to target? That's where our AI comes in."

---

#### Step 2: AI Keyword Research (2 minutes)

**[Screen: Navigate to Keyword Research or show results]**

**ACTION:**
1. Navigate to Keyword Research section
2. Select the test ASIN
3. Show the research output (or trigger if fast enough)

**SAY:**
> "This is our Automated Keyword Research feature - and this was the action item from our last meeting about value proposition.
>
> When an ASIN is enabled, our system automatically:
> 1. Fetches the product listing - title, bullets, description
> 2. Runs it through AI to understand the product
> 3. Generates and classifies keywords"

**ACTION:** Point to each section as you explain

**SAY:**
> "The AI first determines the Branding Scope:
> - NB: Non-Branded - generic keywords only
> - OB: Own Brand - can use the brand name
> - CB: Competitor Brand - can reference competitors
>
> Then it extracts product attributes - what is this product, who uses it, what's it made of.
>
> Finally, it generates keywords with R/S/C/N classification:
> - R for Root: Direct product terms - highest priority
> - S for Synonym: Alternative ways people search
> - C for Complementary: Related terms
> - N for Negative: Terms to exclude
>
> [Point to example keywords]
>
> This gives us a prioritized keyword list instantly. What used to take a specialist hours now takes minutes."

**IMPORTANT - Acknowledge the Status:**
> "I should note - the feature is fully developed and deployed. The current challenge is output accuracy - results need manual review before use. We've been working on improvements, two-thirds are complete and deploying this week. If quality improves as expected, we can reduce or eliminate manual review, which will speed up our rollout significantly."

**TRANSITION:**
> "Keywords are one targeting strategy. The other is targeting competitor products directly."

---

#### Step 3: Competitor ASIN Discovery (2 minutes)

**[Screen: Navigate to Target ASIN Research results]**

**ACTION:**
1. Show the research output for test ASIN
2. Point to the different sections

**SAY:**
> "This is our Automated Target ASIN Research.
>
> The system analyzes which search terms are driving results for this product, then scrapes Amazon to find who else appears for those searches.
>
> [Point to search terms section]
>
> First, it identifies the top 5 search terms by conversion rate - these are the terms where we're most competitive.
>
> [Point to competitor ASINs]
>
> Then it scrapes Amazon's search results - about 45-50 products per search term.
>
> [Point to qualification criteria]
>
> Here's the key part: it qualifies each competitor. We only want to target ASINs where we have a realistic chance of winning the sale.
>
> The criteria include:
> - Price comparison: Is our price competitive?
> - Rating: Do we have similar or better reviews?
> - Review count: Do we have social proof?
>
> [Point to brand groups]
>
> Qualified ASINs are grouped by brand. Each brand group becomes a targeting campaign."

**TRANSITION:**
> "And those campaigns are created automatically."

---

#### Step 4: Auto Campaign Generation (1 minute)

**[Screen: Show a generated campaign in Campaign Config]**

**ACTION:**
1. Navigate back to Campaign Config
2. Show a campaign with "SPAS" in the name or Relevancy Tag = competitor brand

**SAY:**
> "Here's a campaign that was automatically generated.
>
> [Point to campaign name]
>
> The naming convention encodes all the information: campaign type, brand code, ASIN, and target brand.
>
> [Point to configuration]
>
> It's pre-configured with:
> - Manual ASIN Targeting
> - Down Only bidding strategy
> - Budget based on our settings
>
> Notice the status is PAUSED by default. We don't auto-activate - the Account Manager reviews and turns it on. Human stays in control.
>
> This entire flow - from research to campaign creation - happens automatically when an ASIN is enabled."

**TRANSITION:**
> "That's the setup. Now let me show you what happens over time - the optimization engine."

---

### PART 3: PASSIVE FEATURES (4-5 minutes)

#### Step 5: Bid Optimization (1.5 minutes)

**[Screen: Navigate to Bid Strategy Logs or show screenshot]**

**ACTION:**
1. Show bid change history
2. Point to a specific example with before/after

**SAY:**
> "This is where the magic happens over time. Our Bid Optimization runs continuously, adjusting bids based on performance.
>
> [Point to a specific bid change]
>
> Let me walk through this example:
> - This keyword had a bid of $0.75
> - ACOS was running at 45% - above our 30% target
> - Top of Search percentage was only 30% - meaning we weren't getting premium placement
> - The system increased the bid to $0.90
> - Result: ACOS dropped to 28%
>
> The logic: Low TOS means we're not competitive enough, so increase bid. High TOS means we might be overpaying, so decrease.
>
> [Point to ACOS breach example if available]
>
> We also have an emergency brake. If ACOS breaches badly - spending way over target with enough data to be confident - the bid drops to $0.02. This stops the bleeding immediately."

**SAY (Key Differentiator):**
> "What makes this special: We use CVR waterfalls. The system looks at conversion data at multiple levels - search term, keyword, campaign, ASIN - to make bid decisions even with limited data.
>
> I should note: CVR estimation accuracy is still being improved, which affects bid optimization quality. But the architecture is in place."

---

#### Step 6: Budget Management (1 minute)

**[Screen: Show Auto Budget distribution or Campaign Config with multiple campaigns]**

**ACTION:**
1. Show budget distribution for an ASIN with multiple campaigns

**SAY:**
> "Auto Budget Management distributes the ASIN-level daily budget across all campaigns.
>
> [Point to distribution]
>
> Campaigns are classified as:
> - Winners: ACOS at or below target
> - Losers: ACOS above target
> - Immature: Not enough data yet
>
> Budget flows from losers to winners. But we cap the reduction at 20% per cycle - we don't want to kill a campaign that might recover.
>
> Every campaign gets at least $5 minimum - enough to keep gathering data.
>
> This runs automatically. Account Managers set the ASIN budget, the system handles allocation."

---

#### Step 7: Harvesting & Negation (1 minute)

**[Screen: Show Harvested Terms and Negated Terms lists]**

**ACTION:**
1. Show the harvested terms list
2. Show the negated terms list

**SAY:**
> "These two features work together to continuously improve targeting.
>
> [Point to harvested terms]
>
> **Harvesting**: When a search term performs well - ACOS consistently below target, sufficient spend - it gets promoted. From Broad or Auto campaigns to dedicated Exact match campaigns where we can optimize it specifically.
>
> [Point to example]
> This term 'organic chickpeas' was harvested because it had 18% ACOS against a 25% target.
>
> [Point to negated terms]
>
> **Negation**: The opposite. When a search term consistently underperforms - ACOS always above target - it gets added as a negative keyword.
>
> [Point to example]
> 'Cheap curry' was negated - 85% ACOS, clearly not our customer.
>
> This happens automatically every few hours. No manual search term mining needed."

---

#### Step 8: High Performers Isolation (30 seconds)

**[Screen: Show Solo Campaign if available]**

**ACTION:**
1. Point to a solo campaign or describe the concept

**SAY:**
> "Finally, our top performers get VIP treatment.
>
> When a search term is in the top 5% by sales, with consistent ACOS, and the ASIN has 100+ orders, we create a dedicated 'solo' campaign just for that term.
>
> This prevents cannibalization and gives maximum control over our best performers.
>
> The system even auto-pauses the same keyword in other campaigns to avoid competing with ourselves."

---

### PART 4: DIFFERENTIATORS (1 minute)

**[Screen: Can show comparison table or just speak]**

**SAY:**
> "Let me quickly highlight what makes this different from tools like Xnurta or Perpetua:
>
> **One:** Inventory-aware bidding. We can adjust bids based on stock levels - competitors don't do this.
>
> **Two:** Organic rank integration. If you're ranking well organically, we can reduce ad spend on those keywords.
>
> **Three:** End-to-end automation. From keyword research to campaign creation to ongoing optimization - one platform.
>
> **Four:** CVR waterfalls. Intelligent bid decisions even with limited data by looking at multiple hierarchy levels.
>
> **Five:** Human-in-the-loop. Nothing deploys without review. AI suggests, humans approve."

---

### PART 5: CHALLENGES & DISCUSSION (2-3 minutes)

**[Screen: Can show challenges document or speak from notes]**

**SAY:**
> "Before we open for questions, I want to be transparent about where we stand.
>
> **Intelligent Pacing** has been deployed - about 2 weeks ago. Development is complete. UAT is pending and will be done alongside our test account runs.
>
> **Challenge 1: Keyword Research Quality**
> The feature is fully developed and deployed. The issue is output accuracy - results currently require manual review. This is a bottleneck for scaling rollout.
>
> We initiated an improvement project. Two-thirds is complete and ready to deploy this week. The remaining third is still in design phase.
>
> Our plan: Deploy the improvements, test if quality is satisfactory. If yes, we can roll out with reduced or no manual review - which speeds up everything.
>
> **Challenge 2: CVR Estimation**
> This is a core enhancement that would improve multiple features: bid optimization, budget allocation, and pacing.
>
> Currently, we use historical moving averages - past performance predicts future. But this can't account for seasonality, price changes, competitive dynamics, or keywords with sparse history.
>
> The fix: a machine learning model trained on multiple features. We have 3,000 accounts of training data. Challenge is it requires ML expertise and iterative R&D.
>
> **Challenge 3: Test Account Budget** - This is a new constraint.
> We have 7 ASINs - all from the same client using an anchor approach. If the first ASIN performs well, they'll allow more. This makes testing slow.
>
> The bigger issue: even with 7 ASINs, the budget is too limited. We need $1,000 to $2,000 per ASIN - a healthy budget that gives wiggle room.
>
> Why does budget matter? Pacing needs sufficient spend to make reallocation decisions. Keyword Research is one of our core USPs, but without budget we can't utilize those keywords. With small budgets, many features simply won't activate or show their potential.
>
> Per Bob: getting new clients takes months. Improving UX helps. Budget subsidization helps convince hesitant clients. We should start with clients we have good relationships with.
>
> **Next Step:** I'll prepare a proposal on how we can subsidize the advertising budget to accelerate testing.
>
> **Other Items:**
> - **Reporting** is important - without it we can't measure baseline or get signals if things are working. Engineering delivers in about 2 weeks.
> - **APDC** (diagnostics) is deprioritized until after rollout. It will help us diagnose root causes when there's underperformance.
> - **UI/UX** needs improvement - currently bare minimum, frustrating for Account Managers. We'll start redesign work in 2-3 weeks after collecting learnings.
>
> I've prepared an updated challenges document which I can share."

---

### CLOSING (30 seconds)

**SAY:**
> "To summarize: The core platform is ready. All 11 features are developed and deployed. We have one ASIN actively testing and expanding to more this week.
>
> The key decision point for you: Do we want to accelerate testing with a subsidy program, or proceed at the current pace with client budgets?
>
> Happy to take any questions."

---

## Quick Reference Card

Keep this visible during the demo:

| Feature | Where to Show | Key Number to Mention |
|---------|---------------|----------------------|
| Campaign Config | Campaign Config page | "4 match types, all configurable" |
| KW Research | Keyword Research results | "R/S/C/N classification" |
| ASIN Research | Target ASIN Research | "45-50 competitors analyzed" |
| Campaign Gen | SPAS campaign in config | "Auto-created, PAUSED by default" |
| Bid Optimization | Bid Strategy Logs | "TOS% drives direction" |
| Auto Budget | Campaign budget distribution | "20% max reduction, $5 minimum" |
| Harvesting | Harvested Terms list | "ACOS 18% - promoted to Exact" |
| Negation | Negated Terms list | "ACOS 85% - blocked" |
| Isolation | Solo Campaign | "Top 5% by sales" |

---

## If Something Goes Wrong

| Problem | Fallback |
|---------|----------|
| Platform slow/down | Use prepared screenshots |
| Data not loading | Switch to explaining with diagrams |
| Feature output empty | "This ASIN doesn't have this yet, let me show you the concept..." |
| Time running short | Skip to Challenges section |

---

## Post-Demo Follow-ups

- [ ] Share updated challenges document (v2)
- [ ] Share Value Prop document for KW Research
- [ ] Prepare subsidy proposal (due Feb 7)
- [ ] Send recording/notes if requested

---

**Good luck!**
