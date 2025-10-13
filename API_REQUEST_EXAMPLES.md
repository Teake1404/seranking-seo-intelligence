# API Request Examples

## 📝 Basic Request (Uses Config Defaults)

```json
{
  "domain": "bagsoflove.co.uk",
  "keywords": ["personalized bags", "custom gifts"]
}
```

**Result:**
- Uses competitors from `config.py`: `notonthehighstreet.com`, `moonpig.com`, `gettingpersonal.co.uk`
- These are manually curated, niche-relevant competitors

---

## 🎯 Custom Competitors (Recommended)

```json
{
  "domain": "bagsoflove.co.uk",
  "keywords": ["personalized bags", "custom gifts"],
  "competitors": [
    "notonthehighstreet.com",
    "moonpig.com",
    "gettingpersonal.co.uk"
  ]
}
```

**Best practice:** Manually specify competitors who are true business competitors, not just SEO keyword overlap.

---

## 🤖 Auto-Discover Competitors (Use with Caution)

```json
{
  "domain": "bagsoflove.co.uk",
  "keywords": ["personalized bags", "custom gifts"],
  "competitors": [],
  "auto_discover_competitors": true
}
```

**Warning:** Auto-discovery uses keyword overlap, which often finds:
- Generic e-commerce sites (Amazon, eBay)
- Not true business competitors

**When to use:** 
- Exploring new markets
- You don't know the competitive landscape
- Large enterprise sites where any keyword overlap matters

---

## 🏅 Priority Keywords

```json
{
  "domain": "bagsoflove.co.uk",
  "keywords": [
    "personalized bags",
    "custom gifts",
    "photo blankets",
    "personalized mugs",
    "custom phone cases"
  ],
  "keyword_priorities": {
    "personalized bags": "high",
    "custom gifts": "high",
    "photo blankets": "medium",
    "personalized mugs": "medium",
    "custom phone cases": "low"
  },
  "check_frequency": "weekly"
}
```

**How it works:**
- `daily`: Check all keywords
- `weekly`: Check high + medium priority keywords
- `monthly`: Check only high priority keywords

**Use case:** Scale to 100+ keywords without excessive API costs

---

## 📊 Complete Example with All Features

```json
{
  "domain": "bagsoflove.co.uk",
  "keywords": [
    "personalized bags",
    "custom gifts",
    "photo gifts"
  ],
  "competitors": [
    "notonthehighstreet.com",
    "moonpig.com",
    "gettingpersonal.co.uk"
  ],
  "keyword_priorities": {
    "personalized bags": "high",
    "custom gifts": "high",
    "photo gifts": "medium"
  },
  "check_frequency": "daily",
  "historical_data": [
    {
      "keyword": "personalized bags",
      "position": 65,
      "date": "2024-10-09"
    },
    {
      "keyword": "custom gifts",
      "position": 20,
      "date": "2024-10-09"
    }
  ]
}
```

**Returns:**
- ✅ Current rankings from SEranking
- ✅ Top 10 entry/exit detection
- ✅ Statistical anomaly detection (z-scores)
- ✅ Competitor insights (from your specified list)
- ✅ Claude AI analysis and recommendations
- ✅ Search volume & CPC data

---

## 💡 Pro Tips

### 1. **Manual Competitors > Auto-Discovery**
For niche businesses, always manually specify competitors who:
- Target the same audience
- Offer similar products/services
- Compete for the same customer intent

Auto-discovery finds keyword overlap, not business competition.

### 2. **Priority Keywords for Scale**
Start with 5-10 "high" priority keywords, then add 20-50 "medium" and "low" priority ones. Use `check_frequency: "weekly"` to check high-priority daily, others weekly.

### 3. **Historical Data is Key**
The more historical data you provide, the better:
- **7+ days**: Basic anomaly detection
- **30+ days**: Robust statistical baselines
- **90+ days**: Seasonal trend detection

### 4. **Regional Settings**
Current settings: **UK** (`source=uk`, `engine_id=368`)

To change region, edit `seranking_mcp.py`:
```python
# Line 276: Change source
url = "https://api.seranking.com/v1/keywords/export?source=us"

# Line 62 & 163: Change engine_id
"engine_id": 200,  # 200 = US, 368 = UK, 250 = Egypt, etc.
```

See SEranking docs for all country codes.

---

## 🎯 Client Demo Request

Perfect request to demonstrate all features:

```json
{
  "domain": "client-website.com",
  "keywords": [
    "client main keyword 1",
    "client main keyword 2",
    "client secondary keyword 1"
  ],
  "competitors": [
    "client's actual competitor 1",
    "client's actual competitor 2"
  ],
  "historical_data": []
}
```

**First run:** No anomalies (no baseline yet)  
**After 7 days:** Anomaly detection kicks in  
**After 30 days:** Full statistical insights

---

**Remember:** The AI is only as good as the data you give it. Accurate competitors = accurate insights! 🎯



