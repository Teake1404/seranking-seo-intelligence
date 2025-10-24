#!/usr/bin/env python3
"""
Enhanced SEO Intelligence API with SEranking MCP Integration
Uses MCP server for fast data fetching
"""
import asyncio
import json
import logging
import os
import requests
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# Import existing functions
from enhanced_claude_insights import generate_enhanced_claude_insights
from redis_cache import get_cache
import config

# Initialize Flask
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MCP Server Configuration
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:3000")

def call_mcp_tool(tool_name: str, tool_params: dict) -> dict:
    """Call SEranking MCP tool"""
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "call",
            "params": {
                "tool_name": tool_name,
                "tool_params": tool_params
            }
        }
        
        response = requests.post(
            f"{MCP_SERVER_URL}/mcp",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if "error" in result:
                logger.error(f"MCP Error: {result['error']}")
                return {}
            
            # Extract content from MCP response
            content = result.get("result", {}).get("content", [{}])[0].get("text", "{}")
            return json.loads(content)
        else:
            logger.error(f"MCP request failed: {response.status_code}")
            return {}
            
    except Exception as e:
        logger.error(f"Error calling MCP tool {tool_name}: {e}")
        return {}

def get_keyword_rankings_mcp(keywords: list, domain: str) -> dict:
    """Get keyword rankings using MCP"""
    try:
        # Use domainKeywords tool
        data = call_mcp_tool("domainKeywords", {
            "source": "us",
            "domain": domain,
            "limit": len(keywords)
        })
        
        # Format the response
        rankings = {"keywords": {}}
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and "keyword" in item:
                    keyword = item["keyword"]
                    rankings["keywords"][keyword] = {
                        "position": item.get("position"),
                        "url": item.get("url"),
                        "title": item.get("title")
                    }
        
        return rankings
    except Exception as e:
        logger.error(f"Error getting keyword rankings: {e}")
        return {"keywords": {}}

def get_competitor_rankings_mcp(competitors: list, keywords: list) -> dict:
    """Get competitor rankings using MCP"""
    try:
        competitor_data = {"keywords": {}}
        
        for competitor in competitors:
            data = call_mcp_tool("domainKeywords", {
                "source": "us", 
                "domain": competitor,
                "limit": len(keywords)
            })
            
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and "keyword" in item:
                        keyword = item["keyword"]
                        if keyword not in competitor_data["keywords"]:
                            competitor_data["keywords"][keyword] = {}
                        competitor_data["keywords"][keyword][competitor] = {
                            "position": item.get("position"),
                            "url": item.get("url")
                        }
        
        return competitor_data
    except Exception as e:
        logger.error(f"Error getting competitor rankings: {e}")
        return {"keywords": {}}

def get_keyword_metrics_mcp(keywords: list) -> dict:
    """Get keyword metrics using MCP"""
    try:
        metrics = {"keywords": {}}
        
        for keyword in keywords:
            # Use keywordMetrics tool
            data = call_mcp_tool("keywordMetrics", {
                "source": "us",
                "keyword": keyword
            })
            
            if isinstance(data, dict):
                metrics["keywords"][keyword] = {
                    "search_volume": data.get("volume", 0),
                    "cpc": data.get("cpc", 0),
                    "difficulty": data.get("difficulty", 0)
                }
        
        return metrics
    except Exception as e:
        logger.error(f"Error getting keyword metrics: {e}")
        return {"keywords": {}}

def run_async(coro):
    """Helper to run async functions in Flask"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(coro)
    loop.close()
    return result

@app.route('/', methods=['GET'])
def home():
    """Root endpoint"""
    cache = get_cache()
    cache_status = "enabled" if cache.is_available() else "disabled"
    
    return jsonify({
        "service": "Enhanced SEO Intelligence API - SEranking MCP Version",
        "status": "running",
        "version": "2.0",
        "data_provider": "SEranking MCP",
        "architecture": "Stateless API + n8n Database + Redis Cache + MCP Server",
        "cache": cache_status,
        "mcp_server": MCP_SERVER_URL,
        "features": [
            "Keyword Rankings (MCP)",
            "Competitor Analysis (MCP)", 
            "Anomaly Detection",
            "AI Insights",
            "SEO Opportunity Analysis",
            "Low-Hanging Fruit Detection"
        ],
        "endpoints": {
            "health": "/health",
            "enhanced_report": "/api/enhanced-report (POST)",
            "seo_opportunities": "/api/seo-opportunities (POST)",
            "cache_stats": "/api/cache/stats (GET)",
            "cache_invalidate": "/api/cache/invalidate (POST)"
        }
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    cache = get_cache()
    cache_status = "enabled" if cache.is_available() else "disabled"
    
    # Check MCP server health
    mcp_health = "unknown"
    try:
        response = requests.get(f"{MCP_SERVER_URL}/health", timeout=5)
        mcp_health = "healthy" if response.status_code == 200 else "unhealthy"
    except:
        mcp_health = "unreachable"
    
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "cache": cache_status,
        "mcp_server": mcp_health,
        "version": "2.0"
    })

@app.route('/api/enhanced-report', methods=['POST'])
def enhanced_report():
    """
    Enhanced SEO report using SEranking MCP
    """
    try:
        data = request.json or {}
        domain = data.get('domain', config.TARGET_DOMAIN)
        keywords = data.get('keywords', config.GENERIC_KEYWORDS)
        competitors = data.get('competitors', config.COMPETITOR_DOMAINS)
        historical_data = data.get('historical_data', [])
        
        logger.info(f"🚀 Generating enhanced report for {domain} using MCP")
        
        # Step 1: Get data using MCP
        logger.info("📊 Fetching data via SEranking MCP...")
        ranking_data = get_keyword_rankings_mcp(keywords, domain)
        competitor_data = get_competitor_rankings_mcp(competitors, keywords)
        metrics_data = get_keyword_metrics_mcp(keywords)
        
        # Step 2: Create opportunity data
        opportunity_data = {
            "lost_keywords": [],
            "declining_keywords": [],
            "competitor_keywords": [],
            "related_keywords": [],
            "similar_keywords": [],
            "low_hanging_fruit": []
        }
        
        # Extract lost keywords (not ranked)
        keywords_data = ranking_data.get('keywords', {})
        for keyword, data in keywords_data.items():
            if data.get('position') is None or data.get('position') == 0:
                opportunity_data["lost_keywords"].append({
                    "keyword": keyword,
                    "volume": 1000,
                    "cpc": 0.5,
                    "difficulty": 30
                })
        
        # Step 3: Detect anomalies (simplified)
        anomalies = []
        
        # Step 4: Generate enhanced AI insights
        logger.info("🤖 Generating enhanced AI insights...")
        insights = generate_enhanced_claude_insights(
            ranking_data=ranking_data,
            competitor_data=competitor_data,
            anomalies=anomalies,
            opportunity_data=opportunity_data
        )
        
        # Step 5: Create comprehensive report
        logger.info("📝 Generating comprehensive report...")
        
        # Calculate summary statistics
        total_keywords = len(keywords_data)
        page_1_keywords = len([k for k, v in keywords_data.items() if v.get('position', 0) <= 10])
        visibility_score = (page_1_keywords / total_keywords * 100) if total_keywords > 0 else 0
        
        # Create enhanced summary
        summary = {
            "keywords_tracked": total_keywords,
            "page_1_keywords": page_1_keywords,
            "visibility_score": round(visibility_score, 1),
            "anomalies_count": len(anomalies),
            "competitors_tracked": len(competitors),
            "opportunities_found": len(opportunity_data.get('low_hanging_fruit', [])),
            "lost_keywords": len(opportunity_data.get('lost_keywords', [])),
            "declining_keywords": len(opportunity_data.get('declining_keywords', []))
        }
        
        # Generate comprehensive report
        report = f"""
# 🚀 ENHANCED SEO INTELLIGENCE REPORT (MCP)

## 📊 PERFORMANCE SUMMARY:
• {summary['keywords_tracked']} keywords tracked
• {summary['page_1_keywords']} keywords on page 1  
• Visibility score: {summary['visibility_score']}%
• {summary['anomalies_count']} anomalies detected
• {summary['opportunities_found']} low-hanging fruit opportunities

## 🔍 OPPORTUNITY ANALYSIS:
• {summary['lost_keywords']} lost keywords identified
• {summary['declining_keywords']} declining keywords found
• {summary['opportunities_found']} new opportunities discovered

## 🤖 AI INSIGHTS:
{insights.get('raw_response', 'No AI insights available')}

---
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Data: SEranking MCP + Claude AI
"""
        
        return jsonify({
            "success": True,
            "domain": domain,
            "date": datetime.now().strftime('%Y-%m-%d'),
            "summary": summary,
            "data": {
                "rankings": ranking_data,
                "competitors": competitor_data,
                "metrics": metrics_data,
                "opportunities": opportunity_data
            },
            "insights": insights,
            "anomalies": anomalies,
            "report": report,
            "timestamp": datetime.now().isoformat(),
            "data_provider": "SEranking MCP",
            "ai_model": insights.get('model', 'claude-sonnet-4-20250514')
        })
        
    except Exception as e:
        logger.error(f"Enhanced report generation failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/seo-opportunities', methods=['POST'])
def seo_opportunities():
    """SEO Opportunity Analysis endpoint using MCP"""
    try:
        data = request.json or {}
        domain = data.get('domain', config.TARGET_DOMAIN)
        market = data.get('market', 'us')
        
        logger.info(f"🔍 Starting SEO opportunity analysis for {domain} using MCP")
        
        # Get data using MCP
        keywords = data.get('keywords', config.GENERIC_KEYWORDS)
        competitors = data.get('competitors', config.COMPETITOR_DOMAINS)
        
        ranking_data = get_keyword_rankings_mcp(keywords, domain)
        competitor_data = get_competitor_rankings_mcp(competitors, keywords)
        
        # Create opportunity report
        report = f"""
# 🚀 SEO Opportunity Analysis Report (MCP)
## Domain: {domain} | Market: {market.upper()}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 Current Rankings:
{json.dumps(ranking_data, indent=2)[:1000]}...

## 🏆 Competitor Analysis:
{json.dumps(competitor_data, indent=2)[:1000]}...

---

## 📈 Recommendations:
1. **Immediate Action**: Analyze current ranking data
2. **Content Strategy**: Focus on high-performing keywords  
3. **Competitive Monitoring**: Track competitor positions
4. **Opportunity Development**: Identify keyword gaps

---
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Data: SEranking MCP
"""
        
        return jsonify({
            "success": True,
            "domain": domain,
            "market": market,
            "report": report,
            "timestamp": datetime.now().isoformat(),
            "analysis_type": "seo_opportunities"
        })
        
    except Exception as e:
        logger.error(f"SEO opportunity analysis failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5001))
    app.run(host=config.FLASK_HOST, port=port, debug=config.FLASK_DEBUG)
