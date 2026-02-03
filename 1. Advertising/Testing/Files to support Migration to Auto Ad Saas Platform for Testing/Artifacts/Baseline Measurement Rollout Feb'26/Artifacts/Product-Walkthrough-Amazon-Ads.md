# KC Ad SaaS Platform - Internal Walkthrough Guide

> **Audience:** Account Managers (Internal Team)
> **Status:** Production-ready with some features in development
> **Last Updated:** January 2026

---

## Table of Contents

1. [Platform Overview](#1-platform-overview)
2. [Getting Started](#2-getting-started)
3. [Campaign Setup & Launch](#3-campaign-setup--launch)
4. [Keyword Research](#4-keyword-research)
5. [Campaign Configuration](#5-campaign-configuration)
6. [Bid Management & Optimization](#6-bid-management--optimization)
7. [Budget Management & Pacing](#7-budget-management--pacing)
8. [Monitoring & Optimization](#8-monitoring--optimization)
9. [Reporting](#9-reporting)
10. [Troubleshooting & FAQs](#10-troubleshooting--faqs)

---

## 1. Platform Overview

### What is the KC Ad SaaS Platform?

The KC Ad SaaS Platform is an Amazon advertising management tool that combines AI-powered automation with manual control. It helps manage Sponsored Products campaigns at scale with features for:

- **Automated Keyword Research** - AI-driven keyword discovery and classification
- **Campaign Configuration** - Set up Auto and Manual campaigns with granular control
- **Bid Optimization** - Automated bid adjustments based on performance
- **Budget Pacing** - Intelligent budget allocation and spend distribution
- **Performance Monitoring** - Track ACOS, spend, and conversions

### Key Differentiators vs. Competitors (e.g., Xnurta)

| Feature | KC Platform | Competitors |
|---------|-------------|-------------|
| Inventory-level bid adjustments | Yes | Limited |
| Organic rank-based bid adjustments | Yes | No |
| Keyword research-driven advertising | Comprehensive | Basic |
| Lock Ad Placements | Yes | Rare |
| Pausing underperforming ad groups | Automated | Manual |

### Campaign Types Supported

1. **Auto Campaigns** - Amazon automatically targets based on product info
   - Close Match
   - Loose Match
   - Substitute
   - Complimentary

2. **Manual KW Campaigns** - You control which keywords to target

3. **SB & SD Ads** - Sponsored Brands and Sponsored Display (in scope)

---

## 2. Getting Started

### Prerequisites

Before setting up campaigns, ensure you have:

- [ ] Access to the KC Ad SaaS Platform
- [ ] Client's Amazon Seller/Vendor Central credentials linked
- [ ] Product catalog synced (ASINs available)
- [ ] Client's advertising goals documented (Target ACOS, budget, etc.)

### Initial Setup Checklist

1. **Verify ASIN sync** - Confirm all client products are visible
2. **Set client goals** - Document Target ACOS, daily/monthly budget
3. **Review product categories** - Understand the product types for keyword research
4. **Check existing campaigns** - If migrating, review current campaign structure

---

## 3. Campaign Setup & Launch

### Overview

Campaign setup involves selecting products (ASINs), choosing campaign types, and configuring targeting parameters.

### Step-by-Step: Creating a New Campaign

#### Step 1: Select ASINs

1. Navigate to **Campaign Config**
2. In the "Select ASINs" section, click the dropdown
3. Select one or more products by their ASIN (e.g., `Product 2 - B09C5PRFGQ`)
4. Selected ASINs appear as tags that can be removed with ✕

> **Tip:** Group similar products together for more efficient campaign management.

#### Step 2: Choose Campaign Type

Toggle between:
- **Auto** - For automatic targeting campaigns
- **Manual KW** - For manual keyword campaigns

#### Step 3: Configure Match Types (Auto Campaigns)

For each selected ASIN, configure the following match types:

| Match Type | What it Targets | When to Use |
|------------|-----------------|-------------|
| **Close Match** | Closely related search terms | Best for relevant traffic, usually enabled |
| **Loose Match** | Loosely related search terms | Broader reach, monitor ACOS |
| **Substitute** | Competitor/substitute products | Conquest campaigns |
| **Complimentary** | Complementary products | Cross-sell opportunities |

#### Step 4: Set Campaign Parameters

For each match type, configure:

| Parameter | Description | Recommended Starting Point |
|-----------|-------------|---------------------------|
| **Status** | On/Off toggle | Start with Close Match "On" |
| **Default Bid ($)** | Starting bid amount | $0.30 - $0.75 depending on category |
| **Budget ($)** | Daily budget | Based on client's monthly budget ÷ 30 |
| **Target ACOS (%)** | Target advertising cost of sale | Client's break-even or target margin |
| **Negative Keywords** | Terms to exclude | Enter comma-separated (e.g., "cheap, free, used") |

#### Step 5: Submit Configuration

1. Review all settings for each ASIN
2. Click **Submit Configuration**
3. System will create/update campaigns in Amazon

> **Note:** Changes are logged with timestamps showing "Last updated" for each field.

---

## 4. Keyword Research

### Overview

The Automated Keyword Research feature uses AI to discover and classify keywords for your products. Keywords are organized using the R/S/C/N classification system.

### R/S/C/N Classification System

| Classification | Meaning | Action |
|---------------|---------|--------|
| **R** - Relevant | Highly relevant to the product | Add to campaigns, bid aggressively |
| **S** - Semi-relevant | Somewhat related | Test with moderate bids |
| **C** - Consider | May be relevant in context | Low priority, test carefully |
| **N** - Not Relevant | Not appropriate for product | Exclude / add as negative |

### Keyword Research Workflow

#### Step 1: Product Analysis

The system analyzes:
- Product Type (e.g., "Indian Curry", "Food")
- Variant/Use Case/Audience attributes (e.g., "Ready to Eat", "Vegan")

#### Step 2: Cluster Generation

Keywords are grouped into clusters based on:
- **Product Type** + **Attribute** + **Manufacturing** + **Consideration** combinations
- Each cluster represents a unique targeting opportunity

Example clusters for "Chana Masala Curried Chickpeas":
- Indian Curry + Ready to Eat
- Indian Food + Vegan
- Food + Ready to Eat + Vegan

#### Step 3: Review & Approve

1. Review AI-generated keywords
2. Adjust classifications if needed
3. Approve keywords for campaign addition

### Step-by-Step: Running Keyword Research

1. Navigate to **Keyword Research** section
2. Select the ASIN(s) for research
3. Click **Start Research**
4. Review generated keywords and classifications
5. Make adjustments to R/S/C/N tags as needed
6. Click **Apply to Campaigns**

> **Feature Status:** Semi-automated - AI generates suggestions, AM reviews and approves

---

## 5. Campaign Configuration

### Campaign Config Interface

The Campaign Config screen shows a table for each selected ASIN with columns:

| Column | Description | Editable |
|--------|-------------|----------|
| Match Types | Close/Loose/Substitute/Complimentary | No (row identifier) |
| Status | On/Off toggle | Yes |
| Default Bid ($) | Bid amount | Yes |
| Budget ($) | Daily budget | Yes |
| Target ACOS (%) | Target ACOS | Yes |
| Negative Keywords | Excluded terms | Yes |

### Editing Configuration

1. Click on any editable field
2. Enter new value
3. System auto-saves and shows "Last updated" timestamp with previous value in parentheses

Example:
```
Default Bid: $0.50
Last updated: 10/05/2025 00:07:43 (0.3)
```

### Bulk Operations

- Select multiple ASINs to apply the same settings
- Use naming rules for campaign organization
- Bulk bid changes available across campaigns

---

## 6. Bid Management & Optimization

### Overview

The platform offers both manual bid control and automated bid optimization.

### Manual Bid Adjustments

1. Navigate to Campaign Config
2. Update **Default Bid ($)** for each match type
3. Changes sync to Amazon

### Automated Bid Optimization

The system can automatically:
- Adjust bids based on performance metrics
- Apply dayparting (bid by time of day/day of week)
- Pause underperforming ad groups
- Lock ad placements to maintain position

### Bid Strategy Considerations

| Scenario | Recommended Action |
|----------|-------------------|
| ACOS above target | Decrease bid or pause |
| ACOS below target with good sales | Increase bid to capture more volume |
| No impressions | Increase bid significantly or check relevance |
| High impressions, low clicks | Review ad copy/product listing |
| High clicks, no conversions | Check product page, price, reviews |

### CVR (Conversion Rate) Estimation

The platform uses a CVR estimation model to predict conversion likelihood and optimize bids accordingly. This factors in:
- Historical conversion data
- Relevance signals
- Competition levels

> **Feature Status:** CVR Estimation Enhancement in development (ML-based)

---

## 7. Budget Management & Pacing

### Overview

Budget management ensures client spend is distributed effectively across campaigns and time periods.

### Setting Budgets

1. Set **Budget ($)** per match type/campaign
2. System tracks spend against budget
3. Alerts when approaching budget limits

### Automated Pacing

The pacing system:
- Distributes budget evenly or strategically across the month
- Adjusts spend rate based on performance
- Prevents overspend early in the period
- Reallocates budget from underperforming to high-performing campaigns

### Budget Dayparting

Optimize spend by time:
- Reduce bids during low-conversion hours
- Increase bids during peak shopping times

> **Feature Status:** Budget optimization in development, manual budget control fully functional

---

## 8. Monitoring & Optimization

### Daily Monitoring Checklist

- [ ] Check overall spend vs. budget
- [ ] Review ACOS trends
- [ ] Identify underperforming campaigns (ACOS > target)
- [ ] Check for campaigns with no impressions
- [ ] Review new search term reports for negative keyword opportunities

### Weekly Optimization Tasks

- [ ] Harvest converting search terms → add as keywords
- [ ] Add non-converting terms as negatives
- [ ] Adjust bids based on performance trends
- [ ] Review and adjust Target ACOS if needed
- [ ] Run keyword research for new opportunities

### Key Metrics to Track

| Metric | What it Tells You | Target |
|--------|-------------------|--------|
| **ACOS** | Ad spend ÷ Ad sales | Client-specific |
| **ROAS** | Ad sales ÷ Ad spend | Inverse of ACOS |
| **Impressions** | Visibility | Growth trend |
| **Clicks** | Traffic | CTR > 0.3% |
| **CTR** | Click-through rate | > 0.3% |
| **CVR** | Conversion rate | Category dependent |
| **CPC** | Cost per click | Below break-even |

### RCA (Root Cause Analysis)

When performance drops, use the RCA templates:
1. Compare Week-over-Week metrics
2. Identify which campaigns/keywords changed
3. Check for external factors (competition, seasonality)
4. Document findings and action taken

---

## 9. Reporting

### Available Reports

| Report Type | Description | Frequency |
|-------------|-------------|-----------|
| Performance Dashboard | Overview of key metrics | Real-time |
| Campaign Performance | Detailed campaign-level data | Daily/Weekly |
| Search Term Report | Search terms triggering ads | Weekly |
| Changes Log | All modifications made | On-demand |

### Generating Reports

1. Navigate to **Reporting** section
2. Select report type
3. Choose date range
4. Select campaigns/ASINs to include
5. Export as needed (PDF, CSV)

> **Feature Status:** Reporting features being developed by Krell and team

---

## 10. Troubleshooting & FAQs

### Common Issues

#### Campaign not spending
- Check if Status is "On"
- Verify bid is competitive (increase by 50-100%)
- Confirm budget is not exhausted
- Check for targeting restrictions

#### ACOS too high
- Review search term report for irrelevant terms
- Add negatives for non-converting searches
- Lower bids on underperforming keywords
- Check if product listing needs improvement

#### "Never updated" showing for fields
- Field has not been configured yet
- Click and enter values, then submit

#### Changes not reflecting in Amazon
- Allow 1-2 hours for sync
- Check for any error messages
- Verify Amazon API connection status

### Best Practices

1. **Start conservative** - Begin with Close Match only, expand after data
2. **Set realistic ACOS targets** - Based on product margins
3. **Regular negative keyword hygiene** - Review search terms weekly
4. **Document everything** - Use changes log for accountability
5. **Test before scaling** - Prove ROI on small budget before increasing

---

## Appendix

### Glossary

| Term | Definition |
|------|------------|
| ASIN | Amazon Standard Identification Number |
| ACOS | Advertising Cost of Sale (spend/sales) |
| ROAS | Return on Ad Spend (sales/spend) |
| CPC | Cost Per Click |
| CTR | Click-Through Rate |
| CVR | Conversion Rate |
| Match Type | How closely search term matches keyword |
| Negative Keyword | Term you don't want to trigger ads |
| Dayparting | Adjusting bids by time of day |
| Pacing | Distributing budget over time |

### Related Documents

- [PRDs/summary.md](./PRDs/summary.md) - Feature documentation index
- [Strategy/summary.md](./Strategy/summary.md) - Strategic planning documents
- [PRDs/Feature Automated KWs Research/summary.md](./PRDs/Feature%20Automated%20KWs%20Research/summary.md) - Keyword research details
- [PRDs/Feature Automated Bid Optimization/summary.md](./PRDs/Feature%20Automated%20Bid%20Optimization/summary.md) - Bid optimization details

### Contact

For questions or issues, contact the Product team.

---

*This document is for internal use only. UI and features may change as the platform evolves.*
