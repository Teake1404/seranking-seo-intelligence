# 📊 n8n Data Tables Setup - SEO Analysis AI

## 🎯 Why Data Tables vs SQLite?

**Data Tables** (New n8n Feature):
- ✅ **No credentials** needed - built into n8n
- ✅ **Visual UI** - see your data in a table view
- ✅ **Per-project** - perfect for agencies with multiple clients
- ✅ **Easy setup** - click to create, no SQL needed
- ✅ **50MB limit** - enough for thousands of ranking records

**Perfect for:** Agency managing multiple clients, each with their own project/table

---

## 🚀 Step-by-Step Setup

### Step 1: Create Your Data Table

1. **Login to n8n** (https://cloud.n8n.io or your instance)

2. **Create or select a project:**
   - Click "Projects" (left sidebar)
   - Click "+ New project" OR select existing project
   - Name it: "Client Name - SEO Tracking" (e.g., "BagsOfLove SEO")

3. **Create the Data Table:**
   - Inside your project, click **"Data tables"** tab
   - Click **"+ Create Data table"** (top right)
   - Name: `SEO_Rankings`
   - Click **"Create"**

4. **Add Columns:**
   Click "Add column" and create these **13 columns**:

   | Column Name | Type in n8n | Description | Why Needed |
   |-------------|-------------|-------------|------------|
   | `keyword` | Text | The keyword being tracked | Core |
   | `domain` | Text | Domain (e.g., bagsoflove.co.uk) | Core |
   | `position` | Number | Current ranking position | **Anomaly detection** |
   | `previous_position` | Number | Position from previous day | **Change tracking** |
   | `url` | Text | Ranking URL | Context |
   | `title` | Text | Page title | Context |
   | `date` | **Date** | Date measured (YYYY-MM-DD) | **Time-series analysis** |
   | `timestamp` | Text | ISO timestamp (for precision) | Full datetime |
   | `keyword_priority` | Text | high/medium/low | **Priority filtering** |
   | `search_volume` | Number | Monthly searches | **Trend correlation** |
   | `cpc` | Number | Cost per click (decimal) | Value tracking |
   | `difficulty` | Number | Keyword difficulty (0-100) | Competitive analysis |
   | `in_top10` | Boolean | True if position ≤ 10 | **Top 10 tracking** |

5. **Click "Save"**

✅ Your data table is ready!

---

### Step 2: Import the Workflow

1. **In your project**, click **"Workflows"** tab
2. **Click "+ New workflow"**
3. **Click ⋮** (three dots) → **"Import from File"**
4. **Upload:** `n8n_datatable_workflow.json`
5. **Click "Import"**

✅ Workflow imported with Data Table nodes configured!

---

### Step 3: Connect Data Table to Workflow

The workflow is pre-configured, but verify:

1. **Click "Get 30-Day History from Data Table" node**
2. **Verify:**
   - Operation: "Search"
   - Data Table: `SEO_Rankings`
   - Filter: date after 30 days ago
3. **Click "Store in Data Table" node**
4. **Verify:**
   - Operation: "Insert"
   - Data Table: `SEO_Rankings`
   - Field mappings are correct

✅ No credentials needed - it just works!

---

### Step 4: Configure Your Domain & Keywords

1. **Click "Call Cloud Run API" node**
2. **Update the JSON Body:**
   ```json
   {
     "domain": "your-client-domain.com",
     "keywords": ["keyword1", "keyword2", "keyword3"],
     "competitors": ["competitor1.com", "competitor2.com"],
     "historical_data": {{ $json }}
   }
   ```
3. **Verify URL:** `https://seranking-seo-api-671647576749.us-central1.run.app/api/generate-report`

---

### Step 5: Set Up Slack (Optional)

1. **Get Slack webhook URL** (see previous guide)
2. **In n8n:**
   - Click "Settings" → "Variables"
   - Add variable: `SLACK_WEBHOOK_URL` = your webhook
3. **OR** update "Send to Slack" node directly with your webhook URL

---

### Step 6: Test the Workflow

1. **Click "Execute Workflow"** (bottom right)
2. **Watch the execution:**
   - ✅ Trigger → Get History (empty first time)
   - ✅ Call API → Returns rankings + insights
   - ✅ Prepare Data → Formats for Data Table
   - ✅ Store in Data Table → Saves records
   - ✅ Send Slack → Notification sent

3. **View the stored data:**
   - Click "Data tables" tab
   - Click "SEO_Rankings"
   - **You should see your first rankings!** 🎉

---

### Step 7: Activate the Workflow

1. **Toggle "Active" ON** (top right)
2. Workflow runs **automatically every weekday at 9 AM**

---

## 📊 Data Table View

After the first run, your Data Table will look like:

| keyword | domain | position | date | timestamp |
|---------|--------|----------|------|-----------|
| custom gifts | bagsoflove.co.uk | 18 | 2024-10-10 | 2024-10-10T09:00:00Z |
| personalized bags | bagsoflove.co.uk | 61 | 2024-10-10 | 2024-10-10T09:00:00Z |
| photo gifts | bagsoflove.co.uk | 2 | 2024-10-10 | 2024-10-10T09:00:00Z |
| photo blanket | bagsoflove.co.uk | 6 | 2024-10-10 | 2024-10-10T09:00:00Z |

**You can:**
- ✅ View data in the UI
- ✅ Edit manually if needed
- ✅ Export to CSV
- ✅ Query by date range

---

## 🏢 Multi-Client Setup (For Agencies)

**For each client:**

1. **Create a new project:**
   - "Client A - SEO"
   - "Client B - SEO"

2. **Each project has:**
   - Its own Data Table (`SEO_Rankings`)
   - Its own workflow (import the same workflow)
   - Its own API call (different domain/keywords)

3. **Benefits:**
   - ✅ Client data is isolated
   - ✅ Easy to manage multiple clients
   - ✅ Each client gets their own Slack channel
   - ✅ Scales to 100+ clients

---

## 🔄 Daily Workflow

```
Day 1:
  9 AM → Trigger
  → Data Table: Empty
  → API: Get live rankings
  → Store: 4 keywords × 1 day = 4 records
  → Slack: Basic report (no anomalies yet)

Day 7:
  9 AM → Trigger
  → Data Table: 28 records (4 keywords × 7 days)
  → API: Anomaly detection STARTS working! 🎉
  → Store: Add 4 more records (32 total)
  → Slack: Report with anomalies detected

Day 30:
  9 AM → Trigger
  → Data Table: 120 records (4 keywords × 30 days)
  → API: Robust statistical baselines
  → Store: Add 4 more records (124 total)
  → Slack: Full insights with trends
```

---

## 💾 Data Table Size

**Your storage usage:**
- 4 keywords × 365 days = 1,460 records/year
- ~0.5KB per record = ~730KB/year
- **50MB limit** = ~68 years of data! ✅

---

## ✅ Advantages Over SQLite

| Task | SQLite (Old) | Data Tables (New) |
|------|-------------|-------------------|
| Setup | 5 minutes | 30 seconds ✅ |
| View data | Need DBeaver/DB tool | Built-in UI ✅ |
| Credentials | Manual setup | None needed ✅ |
| Multi-client | Complex | One project per client ✅ |
| Export data | SQL query | Click export ✅ |
| Visual inspection | No | Yes ✅ |

---

## 📁 Files You Need

**Import to n8n:**
- `n8n_datatable_workflow.json` ← **NEW! Uses Data Tables**

**Already deployed:**
- Your Cloud Run API: `https://seranking-seo-api-671647576749.us-central1.run.app`

---

## 🎯 Quick Start Checklist

- [ ] Create n8n project for client
- [ ] Create Data Table: `SEO_Rankings` (7 columns)
- [ ] Import workflow: `n8n_datatable_workflow.json`
- [ ] Update domain & keywords in API call node
- [ ] Set Slack webhook (optional)
- [ ] Execute workflow manually to test
- [ ] Check Data Table - should have 4 records
- [ ] Activate workflow (toggle ON)
- [ ] Done! Runs daily at 9 AM

---

## 🚀 You're Ready!

**Your setup:**
- ✅ Cloud Run API deployed
- ✅ SEranking integration working
- ✅ Data Tables workflow ready to import
- ✅ Multi-client scalable architecture

**Import the workflow and test it!** 🎉

