# 🏗️ SEO Intelligence API - Architecture Reference

## 📊 **Core Architecture Pattern**

### **Design Principles:**
1. ✅ **Dynamic Configuration** - No hardcoded values (domain, keywords, etc.)
2. ✅ **API-First** - Client passes configuration via API request
3. ✅ **Stateless API** - Cloud Run handles data fetching only
4. ✅ **n8n Handles State** - Historical data stored in n8n Data Tables
5. ✅ **Separation of Concerns** - Data collection ≠ Analysis ≠ Reporting

---

## 🔧 **Key Components**

### **1. Flask API (Cloud Run)**
```python
# File: final_api_seranking.py (540 lines)

@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    # Get dynamic config from request
    data = request.get_json()
    target_domain = data.get('domain')
    keywords = data.get('keywords')
    competitors = data.get('competitors')
    historical_data = data.get('historical_data', [])
    
    # Fetch fresh data (parallel execution)
    async def fetch_all_data():
        tasks = [
            get_keyword_rankings(keywords, target_domain),
            get_competitor_rankings(competitors, keywords),
            get_keyword_metrics(keywords),
            get_competitor_summary(target_domain, competitors)
        ]
        return await asyncio.gather(*tasks)
    
    # Generate insights with Claude
    insights = generate_claude_insights(ranking_data, competitor_data, anomalies)
    
    # Return structured response
    return jsonify({
        "data": { enriched_rankings, rankings, competitors, metrics },
        "insights": insights,
        "anomalies": anomalies,
        "top10_changes": top10_changes
    })
```

**Key Patterns:**
- ✅ Everything is **dynamic** from request body
- ✅ **Parallel API calls** using `asyncio.gather()`
- ✅ Returns **enriched data** ready for n8n storage
- ✅ No hardcoded domains/keywords/priorities

---

### **2. Claude AI Integration**

```python
# File: claude_insights.py

def generate_claude_insights(ranking_data, competitor_data, anomalies, backlinks=None):
    """Generate AI-powered SEO insights using Claude Sonnet 4"""
    
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    
    # CRITICAL: Use latest model
    model = "claude-sonnet-4-20250514"  # ⚠️ NOT 3.5!
    
    message = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": context + "\n\nProvide analysis in JSON format..."
        }]
    )
    
    return parsed_insights
```

**Key Patterns:**
- ✅ **Model:** `claude-sonnet-4-20250514` (always use latest)
- ✅ **Brand-agnostic prompts** - No "Nike" or hardcoded brand names
- ✅ **Structured output** - JSON format for consistency
- ✅ **Dynamic context** - Built from actual data, not templates

---

### **3. Data Provider Integration**

```python
# File: seranking_mcp.py (476 lines)

# CRITICAL: Rate limiting for API compliance
_last_request_time = 0
_min_request_interval = 0.1  # 100ms = 10 RPS
_rate_limit_lock = None  # Thread-safe for parallel execution

async def make_seranking_request(endpoint, params, method="GET"):
    """Thread-safe rate limiting"""
    global _last_request_time, _rate_limit_lock
    
    if _rate_limit_lock is None:
        _rate_limit_lock = asyncio.Lock()
    
    # Lock protects timestamp updates
    async with _rate_limit_lock:
        # Calculate sleep time
        sleep_time = _min_request_interval - (time.time() - _last_request_time)
        _last_request_time = time.time() + max(0, sleep_time)
    
    # Sleep OUTSIDE lock
    if sleep_time > 0:
        await asyncio.sleep(sleep_time)
    
    # Make request with retry on 429
    # Timeout: 300 seconds (5 minutes)
```

**Key Patterns:**
- ✅ **Rate limiting** - Respects API limits (10 RPS for SEranking)
- ✅ **Thread-safe** - Uses `asyncio.Lock()` for parallel calls
- ✅ **Retry logic** - Auto-retry on 429 (rate limit) errors
- ✅ **Long timeouts** - 300s for async SERP tasks
- ✅ **Returns JSON strings** - Not parsed objects

---

### **4. Configuration Management**

```python
# File: config.py

# CRITICAL: Use environment variables, not hardcoded values
import os
from dotenv import load_dotenv

try:
    load_dotenv()  # Load .env for local development
except ImportError:
    pass  # On Cloud Run, use environment variables directly

# API Keys
SERANKING_API_KEY = os.getenv("SERANKING_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Dynamic defaults (can be overridden by API request)
TARGET_DOMAIN = os.getenv("TARGET_DOMAIN", "example.com")
GENERIC_KEYWORDS = ["keyword 1", "keyword 2"]  # Just defaults
DEFAULT_KEYWORD_PRIORITIES = {}  # Optional defaults

# Timeouts
REQUEST_TIMEOUT = 300  # 5 minutes for async tasks
```

**Key Patterns:**
- ✅ **Environment variables** - Never hardcode API keys
- ✅ **Safe imports** - `try/except` for optional dependencies
- ✅ **Defaults only** - Everything can be overridden by API request
- ✅ **Brand-agnostic** - No hardcoded client names

---

## 🎯 **n8n Workflow Pattern**

### **Flow:**
```
1. Schedule Trigger (Daily 9 AM)
   ↓
2. Get Historical Data (Data Table)
   ↓
3. Call Cloud Run API (POST with dynamic config)
   ↓
4. Prepare Data for Storage (Transform API response)
   ↓
5. Store in Data Table (INSERT operation)
   ↓
6. Format Message (Code node)
   ↓
7. Send Notification (Slack)
```

### **Key Patterns:**

#### **API Call Body:**
```javascript
{
  "domain": "client.com",  // Dynamic per client
  "keywords": ["kw1", "kw2"],  // Dynamic list
  "keyword_priorities": { "kw1": "high" },  // Optional
  "competitors": ["comp1.com"],  // Dynamic list
  "check_frequency": "daily",
  "historical_data": {{ $('Get History').all().map(i => i.json) }}  // From Data Table
}
```

#### **Prepare Data for Storage:**
```javascript
const apiResponse = $('Call API').first().json;
const historicalData = $('Get History').all();
const enrichedRankings = apiResponse.data.enriched_rankings;

return enrichedRankings.map(record => {
  // Find previous position from history
  const history = historicalData.find(h => h.json.keyword === record.keyword);
  const previousPos = history ? history.json.position : null;
  
  return {
    json: {
      ...record,
      previous_position: previousPos,  // ✅ Calculated in n8n
      change: previousPos ? record.position - previousPos : null
    }
  };
});
```

---

## 🚀 **Performance Optimizations**

### **1. Parallel API Calls**
```python
# Instead of sequential:
data1 = await api_call_1()
data2 = await api_call_2()  # Waits for call_1

# Use parallel:
data1, data2 = await asyncio.gather(api_call_1(), api_call_2())
# Both run simultaneously - 40-50% faster!
```

### **2. Rate Limiting Strategy**
- Use **global lock** for thread safety
- Sleep **outside lock** to allow parallel polling
- **Reserve time slots** by updating timestamp immediately
- Handle **429 errors** with exponential backoff

### **3. Timeout Management**
- **API timeouts:** 300s (SEranking SERP tasks are slow)
- **Cloud Run timeout:** 600s (10 minutes max)
- **n8n HTTP timeout:** 600000ms (10 minutes)
- Always set **longer than expected processing time**

---

## 🎨 **Claude AI Best Practices**

### **Model Selection:**
```python
# ✅ ALWAYS use latest Sonnet 4
model = "claude-sonnet-4-20250514"

# ❌ DON'T use older versions
model = "claude-3-5-sonnet-20241022"  # OLD!
```

### **Prompt Structure:**
```python
context = f"""
You are an expert [DOMAIN] analyst. Analyze this data and provide actionable recommendations.

[Dynamic data here - no hardcoded brand names]

Provide analysis in JSON format:
{{
  "critical_changes": [...],
  "competitive_insights": [...],
  "recommendations": [...]
}}
"""
```

**Key:**
- ✅ **Brand-agnostic** prompts
- ✅ **Structured JSON output**
- ✅ **Specific instructions** for format
- ✅ **Dynamic data injection**

---

## 📊 **Data Table Schema Pattern**

### **13 Columns for SEO Tracking:**

| Column | Type | Purpose |
|--------|------|---------|
| `date` | Date | Daily tracking (YYYY-MM-DD) |
| `timestamp` | String | Exact time of check |
| `domain` | Text | Client domain |
| `keyword` | Text | Tracked keyword |
| `position` | Number | Current ranking |
| `previous_position` | Number | Yesterday's ranking |
| `change` | Number | Position delta |
| `in_top10` | Boolean | Page 1 indicator |
| `search_volume` | Number | Monthly searches |
| `cpc` | Number | Cost per click |
| `difficulty` | Number | SEO difficulty |
| `keyword_priority` | Text | high/medium/low |
| `title` | Text | Page title |
| `url` | Text | Ranking URL |

**Pattern:**
- ✅ **Date + Keyword** = Primary identifier
- ✅ **INSERT** operation (not Upsert) = Build history
- ✅ **previous_position** = Calculated in n8n from history

---

## 🔐 **Security Pattern**

### **Local Development:**
```python
# .env file (gitignored)
SERANKING_API_KEY=xxx
ANTHROPIC_API_KEY=xxx
```

### **Production (Cloud Run):**
```bash
# Set via gcloud command or Console UI
gcloud run deploy service-name \
  --set-env-vars="SERANKING_API_KEY=xxx,ANTHROPIC_API_KEY=xxx"
```

### **Never:**
- ❌ Hardcode API keys in code
- ❌ Commit `.env` to GitHub
- ❌ Expose keys in logs

---

## 📁 **File Structure Pattern**

```
project/
├── main_api.py              # Flask API (Cloud Run entry point)
├── data_provider.py         # External API integration (SEranking/GA4)
├── ai_insights.py           # Claude AI integration
├── config.py                # Environment variables + defaults
├── requirements.txt         # Python dependencies
├── Dockerfile               # Cloud Run deployment
├── n8n_workflow.json        # n8n automation template
├── .env                     # Local secrets (gitignored)
├── .gitignore               # Exclude secrets, cache, etc.
└── README.md                # Documentation
```

---

## 🎯 **Key Takeaways for GA4 Project**

### **✅ DO:**
1. Use **Claude Sonnet 4** (`claude-sonnet-4-20250514`)
2. Make everything **dynamic** via API request body
3. Use **environment variables** for secrets
4. Implement **rate limiting** for API calls
5. Use **parallel execution** where possible
6. Let **n8n handle state** (Data Tables)
7. Keep API **stateless** (no database in Cloud Run)
8. Return **enriched data** ready for n8n storage

### **❌ DON'T:**
1. Hardcode brand names, domains, or keywords
2. Use older Claude models (3.5)
3. Store data in Cloud Run (use n8n Data Tables)
4. Skip rate limiting (causes 429 errors)
5. Use sequential API calls (slow!)
6. Commit `.env` or API keys to GitHub

---

## 🚀 **Quick Reference Commands**

### **Local Testing:**
```bash
python test_local.py
```

### **Deploy to Cloud Run:**
```bash
gcloud run deploy service-name \
  --source . \
  --platform managed \
  --region us-central1 \
  --timeout 600s \
  --memory 1Gi \
  --project PROJECT_ID
```

### **Push to GitHub:**
```bash
git add .
git commit -m "message"
git push origin main
```

---

## 📦 **Dependencies Pattern**

```txt
# requirements.txt
flask==3.0.0
flask-cors==4.0.0
gunicorn==21.2.0
anthropic==0.18.1
aiohttp==3.9.1
requests==2.31.0
python-dotenv==1.0.0
```

**Pattern:** Pin versions for reproducibility

---

## 🎨 **Response Format Pattern**

```python
# Consistent API response structure
{
    "success": true,
    "timestamp": "ISO-8601",
    "data_provider": "SEranking",  # Or GA4, etc.
    "data": {
        "enriched_rankings": [...],  # Ready for Data Table
        "raw_data": {...}
    },
    "insights": {
        "model": "claude-sonnet-4-20250514",
        "critical_changes": [...],
        "competitive_insights": [...],
        "recommendations": [...]
    },
    "summary": {
        "metrics_tracked": 4,
        "anomalies_count": 0
    }
}
```

---

**Save this for GA4 project reference!** 🎯




