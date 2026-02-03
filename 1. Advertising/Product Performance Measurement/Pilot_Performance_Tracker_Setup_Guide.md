# Pilot Performance Tracker - Setup Guide

## Overview

This tracker helps measure the impact of the Ad SaaS platform rollout to pilot customers by comparing:
1. **Pre-rollout baseline** vs **Post-rollout performance**
2. **Day-over-Day (DoD)** trends
3. **Week-over-Week (WoW)** trends

## Quick Setup (Google Sheets)

### Step 1: Create the Spreadsheet
1. Create a new Google Sheet
2. Create 5 tabs:
   - `Account Overview`
   - `Pre vs Post Comparison`
   - `Daily Performance`
   - `Weekly Summary`
   - `Executive Dashboard`

### Step 2: Set Up Each Tab

#### Tab 1: Account Overview
| Column | Description |
|--------|-------------|
| Account Name | Client name |
| Account ID | Internal ID or Amazon Seller ID |
| Rollout Date | When automation was enabled |
| Pre-Rollout Period Start | Baseline start (typically 14-30 days before rollout) |
| Pre-Rollout Period End | Day before rollout |
| Status | Active / Paused / Monitoring |
| Notes | Any special circumstances |

#### Tab 2: Pre vs Post Comparison
Key columns:
- Account Name
- Period Type: `Pre-Rollout`, `Post-Rollout (Week 1)`, `Post-Rollout (Week 2)`, etc.
- Metrics: Ad Spend, Ad Sales, ACOS, ROAS, Impressions, Clicks, CTR, Orders, CVR, CPC
- Change vs Baseline row for each account

**Key Formulas:**
```
ACOS = Ad Spend / Ad Sales
ROAS = Ad Sales / Ad Spend
CTR = Clicks / Impressions
CVR = Orders / Clicks
CPC = Ad Spend / Clicks
```

#### Tab 3: Daily Performance
- One row per account per day
- Include DoD change columns:
  ```
  DoD Change % = (Today - Yesterday) / Yesterday * 100
  ```

#### Tab 4: Weekly Summary
- One row per account per week
- Include WoW change columns:
  ```
  WoW Change % = (This Week - Last Week) / Last Week * 100
  ```

#### Tab 5: Executive Dashboard
Aggregated view showing:
- Portfolio-level metrics
- Best/worst performing accounts
- Overall trend indicators

---

## Automation Options

### Option 1: Manual Updates (Quick Start)
- Pull data from Amazon Advertising Console weekly
- Update the tracker manually
- Best for: 1-5 pilot accounts, short-term tracking

### Option 2: Semi-Automated with Amazon Ads Reports
1. Set up scheduled reports in Amazon Advertising Console
2. Download and paste into tracker
3. Use VLOOKUP/INDEX-MATCH to auto-populate comparisons

### Option 3: Fully Automated (Recommended for Scale)
If you have API access, consider:

**A. Connect to Ad SaaS Platform Database**
- Query historical performance data directly
- Auto-populate pre/post metrics
- Real-time dashboard updates

**B. Use Google Apps Script**
```javascript
// Example: Auto-calculate change percentages
function calculateChanges() {
  var sheet = SpreadsheetApp.getActiveSheet();
  // Add formulas to calculate DoD/WoW changes
}
```

**C. Build a Looker Studio Dashboard**
- Connect to your data source
- Create pre-built comparison views
- Auto-refresh daily

---

## Recommended Tracking Cadence

| Activity | Frequency | Owner |
|----------|-----------|-------|
| Update daily metrics | Daily (if automated) or Weekly | Ops Team |
| Review WoW trends | Weekly | Account Manager |
| Pre vs Post comparison update | Weekly | Account Manager |
| Executive summary review | Bi-weekly | Leadership |

---

## Key Success Metrics

### Primary KPIs
| Metric | Target Direction | Why It Matters |
|--------|------------------|----------------|
| ACOS | Lower | Efficiency improvement |
| ROAS | Higher | Better returns |
| Ad Sales | Higher/Stable | Revenue impact |

### Secondary KPIs
| Metric | What to Watch |
|--------|---------------|
| CTR | Indicates targeting quality |
| CVR | Indicates listing/offer quality |
| CPC | Cost efficiency |
| Impressions | Reach/visibility |

---

## Interpreting Results

### Positive Signals
- ACOS decreasing while Ad Sales stable/increasing
- ROAS improving week-over-week
- CVR improving (better targeting)

### Watch Points
- Ad Spend increasing faster than Ad Sales
- ACOS spikes after rollout (may need bid adjustments)
- Impression drops (may indicate targeting too narrow)

### Expected Timeline
- **Week 1-2**: Learning period, metrics may fluctuate
- **Week 3-4**: Stabilization expected
- **Week 5+**: Clear trend should emerge

---

## Sample Pre-Rollout Baseline Periods

| Rollout Type | Recommended Baseline |
|--------------|---------------------|
| Standard | 14 days before rollout |
| Seasonal products | Same period last year + last 14 days |
| New campaigns | First 14 days of manual management |

---

## Questions?

Contact: Abdul (Product)

AWS S3
Vercel - 
Postgres by Neon on vercel