# 🚀 SEO Intelligence API - Automated SEO Monitoring & Reporting

> **AI-powered SEO monitoring system that automates daily ranking checks, competitor analysis, and generates actionable insights using Claude AI.**

[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Run-4285F4?logo=google-cloud)](https://cloud.google.com/run)
[![SEranking](https://img.shields.io/badge/Data-SEranking-blue)](https://seranking.com)
[![Claude AI](https://img.shields.io/badge/AI-Claude%20Sonnet%204-purple)](https://www.anthropic.com/claude)
[![n8n](https://img.shields.io/badge/Automation-n8n-orange)](https://n8n.io)

---

## 🎯 **What It Does**

This system automatically:
- ✅ **Monitors keyword rankings daily** using SEranking API
- ✅ **Tracks competitor positions** for target keywords
- ✅ **Detects statistical anomalies** in ranking changes (z-score analysis)
- ✅ **Generates AI-powered insights** using Claude Sonnet 4
- ✅ **Sends daily Slack reports** with actionable recommendations
- ✅ **Stores 30+ days of history** for trend analysis

---

## 📊 **Architecture**

```
┌─────────────┐
│   n8n       │
│  Workflow   │──┐
└─────────────┘  │
                 │
      ┌──────────▼──────────┐
      │  Google Cloud Run   │
      │  (Flask API)        │
      └──────────┬──────────┘
                 │
      ┌──────────▼──────────┐
      │  SEranking API      │
      │  (Live SERP Data)   │
      └──────────┬──────────┘
                 │
      ┌──────────▼──────────┐
      │  Claude AI API      │
      │  (Insights)         │
      └─────────────────────┘
```

---

## 🚀 **Quick Start**

### **1. Clone Repository**
```bash
git clone https://github.com/YOUR_USERNAME/seranking-seo-intelligence.git
cd seranking-seo-intelligence
```

### **2. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **3. Configure Environment Variables**
Create a `.env` file:
```bash
# SEranking API
SERANKING_API_KEY=your_seranking_api_key

# Anthropic Claude AI
ANTHROPIC_API_KEY=your_anthropic_api_key

# Optional: Default domain and keywords
TARGET_DOMAIN=yourdomain.com
```

### **4. Test Locally**
```bash
python test_seranking_local.py
```

### **5. Deploy to Google Cloud Run**
See `DEPLOYMENT_GUIDE.md` for detailed instructions.

### **6. Import n8n Workflow**
1. Open n8n
2. Import `n8n_datatable_workflow.json`
3. Configure your Slack webhook
4. Update API URL to your Cloud Run endpoint
5. Activate workflow

---

## 📦 **What's Included**

| File | Purpose |
|------|---------|
| `final_api_seranking.py` | Main Flask API for Cloud Run |
| `seranking_mcp.py` | SEranking API integration |
| `claude_insights.py` | Claude AI integration |
| `config.py` | Configuration and settings |
| `n8n_datatable_workflow.json` | n8n workflow template |
| `Dockerfile` | Container configuration |
| `requirements.txt` | Python dependencies |
| `DEPLOYMENT_GUIDE.md` | Step-by-step deployment guide |

---

## 🎯 **Key Features**

### **1. Statistical Anomaly Detection**
- Uses z-score analysis (95% confidence intervals)
- Detects unusual ranking movements
- Requires 7+ days of data for accuracy
- Classifies severity: Critical, High, Medium

### **2. Top 10 Tracking**
- Identifies keywords entering/exiting Top 10
- Tracks position improvements/declines
- Highlights new opportunities

### **3. Competitor Intelligence**
- Monitors competitor positions for same keywords
- Identifies competitive gaps
- Tracks competitive threats

### **4. AI-Powered Insights**
- Claude Sonnet 4 analyzes all data
- Generates actionable recommendations
- Explains competitive landscape
- Provides specific optimization steps

### **5. Priority-Based Scheduling**
- High priority: Daily checks
- Medium priority: Weekly checks
- Low priority: Monthly checks
- Configurable per keyword

---

## 💰 **Cost Analysis**

### **Monthly Costs:**
- **SEranking API:** ~$50/month (trial available)
- **Anthropic Claude:** ~$20/month
- **Google Cloud Run:** ~$5-10/month (generous free tier)
- **n8n Cloud:** $20/month (or self-host for free)
- **Total:** ~$95/month for unlimited clients

### **Traditional SEO Reporting:**
- SEO analyst: 3 hours/week per client × $50/hr = $600/month
- **Savings per client:** $505/month (84% reduction)
- **10 clients:** Save $5,050/month

---

## 🔧 **Configuration**

### **Customize for Your Clients:**

**In n8n workflow, update the API call body:**
```json
{
  "domain": "yourclient.com",
  "keywords": ["keyword 1", "keyword 2", "keyword 3"],
  "keyword_priorities": {
    "keyword 1": "high",
    "keyword 2": "medium"
  },
  "competitors": ["competitor1.com", "competitor2.com"],
  "check_frequency": "daily"
}
```

**That's it!** New client configured in 60 seconds.

---

## 📊 **Sample Output**

### **Slack Report Includes:**
- ✅ Current keyword rankings
- ✅ Search volume & CPC data
- ✅ Top 10 entry/exit notifications
- ✅ Competitor position tracking
- ✅ AI-generated insights explaining changes
- ✅ 5 specific action recommendations

### **Data Stored:**
- ✅ 30+ days of ranking history
- ✅ Position changes over time
- ✅ Keyword metrics (volume, CPC, difficulty)
- ✅ Competitor movements

---

## 🛠️ **Tech Stack**

- **Backend:** Python + Flask
- **Deployment:** Google Cloud Run (serverless)
- **Automation:** n8n (workflow automation)
- **Data:** SEranking API
- **AI:** Anthropic Claude Sonnet 4
- **Database:** n8n Data Tables
- **Notifications:** Slack

---

## 📚 **Documentation**

- `DEPLOYMENT_GUIDE.md` - Deploy to Google Cloud
- `N8N_DATATABLE_SETUP.md` - Configure n8n workflow
- `API_REQUEST_EXAMPLES.md` - API usage examples

---

## 🤝 **For Agencies**

### **Perfect For:**
- ✅ SEO agencies managing 5-50+ clients
- ✅ Marketing teams with multiple brands
- ✅ Freelance SEO consultants
- ✅ E-commerce brands tracking multiple product categories

### **Benefits:**
- 🚀 **Scale:** Monitor unlimited clients with one system
- ⏰ **Time:** Reduce reporting time from hours to minutes
- 💰 **Cost:** 84% cheaper than manual reporting
- 🤖 **Quality:** AI insights match senior analyst level
- 📈 **Client Value:** Daily monitoring impresses clients

---

## 🔐 **Security**

- ✅ All API keys stored in environment variables
- ✅ No hardcoded credentials
- ✅ Cloud Run authentication supported
- ✅ .env file excluded from repository

---

## 📄 **License**

MIT License - Free for commercial use

---

## 🙋 **Support**

Questions? Issues? Open a GitHub issue or contact [your email/social].

---

**Built for SEO agencies who want to work smarter, not harder.** 🚀
