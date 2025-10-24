# 🤖 Claude AI Integration Reference

## ⚠️ **CRITICAL: Always Use Sonnet 4**

```python
# ✅ CORRECT - Latest model (as of Oct 2024)
model = "claude-sonnet-4-20250514"

# ❌ WRONG - Older version
model = "claude-3-5-sonnet-20241022"
model = "claude-3-5-sonnet-20240620"
```

---

## 📝 **Standard Implementation**

```python
import anthropic
import config

def generate_insights(data, context_type="SEO"):
    """
    Generate AI insights using Claude Sonnet 4
    
    Args:
        data: The data to analyze
        context_type: Type of analysis (SEO, GA4, etc.)
    """
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    
    # Build dynamic context (NO hardcoded brand names!)
    context = build_context(data, context_type)
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",  # ⚠️ ALWAYS THIS VERSION
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"{context}\n\nProvide analysis in JSON format..."
            }
        ]
    )
    
    # Parse response
    content = message.content[0].text
    
    return {
        "model": message.model,  # Include for tracking
        "insights": parsed_content
    }
```

---

## 🎯 **Prompt Patterns**

### **Generic Template:**
```python
context = f"""
You are an expert {domain} analyst. Analyze this {data_type} data and provide actionable recommendations.

## Data:
{dynamic_data}

## Task:
Provide analysis in JSON format with:
- critical_changes: Array of important observations
- insights: Array of strategic insights  
- recommendations: Array of 5 specific action items

Keep recommendations actionable and specific. Focus on {priority_focus}.
"""
```

### **For SEO:**
```python
context = f"""
You are an expert SEO analyst. Analyze this SEO data and provide actionable recommendations.

## Domain: {domain}
## Keywords: {keywords_data}
## Competitors: {competitor_data}
## Anomalies: {anomalies_data}

Provide analysis focusing on:
1. Statistical anomalies and their implications
2. Competitive positioning
3. Specific optimization opportunities
"""
```

### **For GA4:**
```python
context = f"""
You are an expert web analytics analyst. Analyze this GA4 data and provide actionable recommendations.

## Website: {domain}
## Traffic: {traffic_data}
## Conversions: {conversion_data}
## User Behavior: {behavior_data}

Identify:
1. Conversion funnel bottlenecks
2. High-value traffic sources
3. User experience issues
4. Revenue optimization opportunities
"""
```

---

## 📊 **Response Format**

### **Always Request JSON:**
```python
"Provide analysis in JSON format with the following structure:
{
  \"critical_changes\": [\"insight 1\", \"insight 2\"],
  \"insights\": [\"insight 1\", \"insight 2\"],
  \"recommendations\": [\"action 1\", \"action 2\"]
}
"
```

### **Parse Response:**
```python
import json
import re

# Extract JSON from markdown code blocks
content = message.content[0].text
json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)

if json_match:
    parsed = json.loads(json_match.group(1))
else:
    # Fallback if no code block
    parsed = json.loads(content)

return {
    "model": message.model,
    "critical_changes": parsed.get("critical_changes", []),
    "insights": parsed.get("insights", []),
    "recommendations": parsed.get("recommendations", [])
}
```

---

## 💡 **Best Practices**

### **1. Brand Agnostic**
```python
# ❌ BAD
context = "Analyze Nike's SEO performance..."

# ✅ GOOD
context = f"Analyze {domain}'s SEO performance..."
```

### **2. Dynamic Data**
```python
# ❌ BAD
keywords = "running shoes, basketball shoes"

# ✅ GOOD
keywords = "\n".join([f"- {kw}: #{pos}" for kw, pos in rankings.items()])
```

### **3. Specific Instructions**
```python
# ❌ BAD
"Give me SEO recommendations"

# ✅ GOOD
"Provide 5 specific, actionable SEO recommendations focusing on:
1. Quick wins (< 1 week implementation)
2. Technical optimizations
3. Content improvements
Keep each under 200 characters."
```

---

## 🔧 **Error Handling**

```python
def generate_insights(data):
    try:
        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": context}]
        )
        
        return parse_response(message)
        
    except anthropic.APIError as e:
        logger.error(f"Claude API error: {e}")
        return {
            "model": "error",
            "insights": [],
            "recommendations": ["Unable to generate AI insights due to API error"]
        }
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}")
        return {
            "model": "claude-sonnet-4-20250514",
            "insights": ["Raw response couldn't be parsed"],
            "raw_response": content
        }
```

---

## 💰 **Cost Optimization**

### **Token Management:**
```python
# Limit context length
max_keywords = 10  # Don't send 100 keywords to Claude
max_competitors = 5

# Use concise data format
context = f"Rankings: {json.dumps(rankings, indent=None)}"  # No pretty-print

# Set appropriate max_tokens
max_tokens = 1024  # Enough for 5 recommendations
```

### **Pricing (as of Oct 2024):**
- Input: $3 per million tokens
- Output: $15 per million tokens
- **Typical SEO report:** ~500 input + 500 output tokens = $0.01

---

## 🎯 **For GA4 Project**

### **Key Differences:**

| Aspect | SEO Project | GA4 Project |
|--------|-------------|-------------|
| **Model** | claude-sonnet-4-20250514 | claude-sonnet-4-20250514 ✅ |
| **Data Source** | SEranking API | Google Analytics Data API |
| **Focus** | Rankings, keywords | Traffic, conversions, behavior |
| **Prompt** | "SEO analyst" | "Web analytics analyst" |
| **Metrics** | Positions, volume | Sessions, users, revenue |

### **Reuse:**
- ✅ Same Claude integration pattern
- ✅ Same API structure (Flask + Cloud Run)
- ✅ Same n8n workflow pattern
- ✅ Same configuration approach

---

**Reference this when building GA4 integration!** 🚀




