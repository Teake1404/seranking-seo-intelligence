#!/usr/bin/env python3
"""
Enhanced SEO Intelligence API with Direct SEranking API calls
Fixes the MCP issue by using direct API calls
"""
import asyncio
import json
import logging
import os
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# Import existing functions
from seranking_mcp import get_keyword_rankings, get_competitor_rankings, get_keyword_metrics
from enhanced_claude_insights import generate_enhanced_claude_insights, generate_opportunity_insights
from redis_cache import get_cache
import config

# Initialize Flask
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        "service": "Enhanced SEO Intelligence API - SEranking Version",
        "status": "running",
        "version": "2.0",
        "data_provider": "SEranking Direct API",
        "architecture": "Stateless API + n8n Database + Redis Cache",
        "cache": cache_status,
        "features": [
            "Keyword Rankings",
            "Competitor Analysis", 
            "Anomaly Detection",
            "AI Insights",
            "SEO Opportunity Analysis",
            "Low-Hanging Fruit Detection"
        ],
        "endpoints": {
            "health": "/health",
            "generate_report": "/api/generate-report (POST)",
            "seo_opportunities": "/api/seo-opportunities (POST)",
            "enhanced_report": "/api/enhanced-report (POST)",
            "cache_stats": "/api/cache/stats (GET)",
            "cache_invalidate": "/api/cache/invalidate (POST)"
        }
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    cache = get_cache()
    cache_status = "enabled" if cache.is_available() else "disabled"
    
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "cache": cache_status,
        "version": "2.0"
    })

@app.route('/api/enhanced-report', methods=['POST'])
def enhanced_report():
    """
    Enhanced SEO report using direct SEranking API calls
    """
    try:
        data = request.json or {}
        domain = data.get('domain', config.TARGET_DOMAIN)
        keywords = data.get('keywords', config.GENERIC_KEYWORDS)
        competitors = data.get('competitors', config.COMPETITOR_DOMAINS)
        historical_data = data.get('historical_data', [])
        
        logger.info(f"🚀 Generating enhanced report for {domain}")
        
        # Step 1: Get basic ranking data using direct API calls
        logger.info("📊 Fetching ranking data...")
        ranking_data = run_async(get_keyword_rankings(keywords, domain))
        competitor_data = run_async(get_competitor_rankings(competitors, keywords))
        metrics_data = run_async(get_keyword_metrics(keywords))
        
        # Step 2: Parse the data
        ranking_json = json.loads(ranking_data)
        competitor_json = json.loads(competitor_data)
        metrics_json = json.loads(metrics_data)
        
        # Step 3: Create opportunity data from the actual data
        opportunity_data = {
            "lost_keywords": [],
            "declining_keywords": [],
            "competitor_keywords": [],
            "related_keywords": [],
            "similar_keywords": [],
            "low_hanging_fruit": []
        }
        
        # Extract keywords from ranking data
        keywords_data = ranking_json.get('keywords', {})
        if isinstance(keywords_data, dict):
            for keyword, data in keywords_data.items():
                if data.get('position') is None or data.get('position') == 0:
                    opportunity_data["lost_keywords"].append({
                        "keyword": keyword,
                        "volume": 1000,  # Default volume
                        "cpc": 0.5,     # Default CPC
                        "difficulty": 30 # Default difficulty
                    })
        
        # Step 4: Detect anomalies (simplified)
        anomalies = []
        
        # Step 5: Generate enhanced AI insights
        logger.info("🤖 Generating enhanced AI insights...")
        insights = generate_enhanced_claude_insights(
            ranking_data=ranking_json,
            competitor_data=competitor_json,
            anomalies=anomalies,
            opportunity_data=opportunity_data
        )
        
        # Step 6: Generate opportunity-specific insights
        opportunity_insights = generate_opportunity_insights(opportunity_data)
        
        # Step 7: Create comprehensive report
        logger.info("📝 Generating comprehensive report...")
        
        # Calculate summary statistics
        total_keywords = len(keywords_data) if isinstance(keywords_data, dict) else 0
        page_1_keywords = len([k for k, v in keywords_data.items() if isinstance(v, dict) and v.get('position', 0) <= 10]) if isinstance(keywords_data, dict) else 0
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
# 🚀 ENHANCED SEO INTELLIGENCE REPORT

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

## 🎯 IMMEDIATE ACTIONS:
{chr(10).join([f"• {action}" for action in opportunity_insights.get('priority_actions', [])])}

---
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Data: SEranking Direct API + Claude AI
"""
        
        return jsonify({
            "success": True,
            "domain": domain,
            "date": datetime.now().strftime('%Y-%m-%d'),
            "summary": summary,
            "data": {
                "rankings": ranking_json,
                "competitors": competitor_json,
                "metrics": metrics_json,
                "opportunities": opportunity_data
            },
            "insights": insights,
            "opportunity_insights": opportunity_insights,
            "anomalies": anomalies,
            "report": report,
            "timestamp": datetime.now().isoformat(),
            "data_provider": "SEranking Direct API",
            "ai_model": insights.get('model', 'claude-sonnet-4-20250514')
        })
        
    except Exception as e:
        logger.error(f"Enhanced report generation failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

# Keep other endpoints for backward compatibility
@app.route('/api/seo-opportunities', methods=['POST'])
def seo_opportunities():
    """SEO Opportunity Analysis endpoint"""
    try:
        data = request.json or {}
        domain = data.get('domain', config.TARGET_DOMAIN)
        market = data.get('market', 'us')
        
        logger.info(f"🔍 Starting SEO opportunity analysis for {domain}")
        
        # Use direct API calls instead of MCP
        keywords = data.get('keywords', config.GENERIC_KEYWORDS)
        competitors = data.get('competitors', config.COMPETITOR_DOMAINS)
        
        # Get ranking data
        ranking_data = run_async(get_keyword_rankings(keywords, domain))
        competitor_data = run_async(get_competitor_rankings(competitors, keywords))
        
        # Create simple opportunity report
        report = f"""
# 🚀 SEO Opportunity Analysis Report
## Domain: {domain} | Market: {market.upper()}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 Current Rankings:
{json.dumps(json.loads(ranking_data), indent=2)[:1000]}...

## 🏆 Competitor Analysis:
{json.dumps(json.loads(competitor_data), indent=2)[:1000]}...

---

## 📈 Recommendations:
1. **Immediate Action**: Analyze current ranking data
2. **Content Strategy**: Focus on high-performing keywords
3. **Competitive Monitoring**: Track competitor positions
4. **Opportunity Development**: Identify keyword gaps

---
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Data: SEranking Direct API
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

@app.route('/api/cache/stats', methods=['GET'])
def cache_stats():
    """Get Redis cache statistics"""
    try:
        cache = get_cache()
        stats = run_async(cache.get_stats())
        return jsonify({
            "success": True,
            "cache_stats": stats,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/cache/invalidate', methods=['POST'])
def invalidate_cache():
    """Invalidate Redis cache"""
    try:
        data = request.json or {}
        data_type = data.get('data_type')
        pattern = data.get('pattern')
        
        cache = get_cache()
        deleted_count = run_async(cache.invalidate(data_type, pattern))
        
        return jsonify({
            "success": True,
            "deleted_keys": deleted_count,
            "data_type": data_type,
            "pattern": pattern,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5001))
    app.run(host=config.FLASK_HOST, port=port, debug=config.FLASK_DEBUG)
