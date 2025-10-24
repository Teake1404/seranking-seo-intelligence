#!/usr/bin/env python3
"""
Enhanced SEO Intelligence API with Opportunity Analysis
Combines existing insights with SEO opportunity analysis
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

# Import SEO opportunity analysis
from seo_opportunity_analysis import SEOOpportunityAnalyzer

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
        "data_provider": "SEranking MCP",
        "architecture": "Stateless API + n8n Database + Redis Cache + Opportunity Analysis",
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

@app.route('/api/seo-opportunities', methods=['POST'])
def seo_opportunities():
    """
    SEO Opportunity Analysis endpoint
    Identifies low-hanging fruit and competitive gaps
    """
    try:
        data = request.json or {}
        domain = data.get('domain', config.TARGET_DOMAIN)
        market = data.get('market', 'us')
        
        logger.info(f"🔍 Starting SEO opportunity analysis for {domain}")
        
        # Initialize opportunity analyzer
        analyzer = SEOOpportunityAnalyzer(config.SERANKING_API_KEY)
        analyzer.domain = domain
        analyzer.market = market
        
        # Run comprehensive analysis
        report = analyzer.run_full_analysis()
        
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

@app.route('/api/enhanced-report', methods=['POST'])
def enhanced_report():
    """
    Enhanced SEO report combining:
    - Existing ranking analysis
    - SEO opportunity analysis
    - Enhanced AI insights
    """
    try:
        data = request.json or {}
        domain = data.get('domain', config.TARGET_DOMAIN)
        keywords = data.get('keywords', config.GENERIC_KEYWORDS)
        competitors = data.get('competitors', config.COMPETITOR_DOMAINS)
        historical_data = data.get('historical_data', [])
        
        logger.info(f"🚀 Generating enhanced report for {domain}")
        
        # Step 1: Get basic ranking data (existing functionality)
        logger.info("📊 Fetching ranking data...")
        ranking_data = run_async(get_keyword_rankings(keywords, domain))
        competitor_data = run_async(get_competitor_rankings(competitors, keywords))
        metrics_data = run_async(get_keyword_metrics(keywords))
        
        # Step 2: Run SEO opportunity analysis
        logger.info("🔍 Running SEO opportunity analysis...")
        analyzer = SEOOpportunityAnalyzer(config.SERANKING_API_KEY)
        analyzer.domain = domain
        analyzer.market = data.get('market', 'us')
        
        # Get opportunity data (without full report generation)
        opportunity_data = {
            "lost_keywords": [],
            "declining_keywords": [],
            "competitor_keywords": [],
            "related_keywords": [],
            "similar_keywords": [],
            "low_hanging_fruit": []
        }
        
        try:
            # Run opportunity analysis steps
            performance_data = analyzer.analyze_domain_performance()
            competitive_data = analyzer.competitive_analysis()
            opportunities_data = analyzer.find_keyword_opportunities(competitive_data.get('competitor_keywords', []))
            
            opportunity_data.update(performance_data)
            opportunity_data.update(opportunities_data)
            
            # Identify low-hanging fruit
            all_opportunities = opportunities_data.get('related_keywords', []) + opportunities_data.get('similar_keywords', [])
            low_hanging = [
                kw for kw in all_opportunities 
                if kw.get('difficulty', 100) < 30 and kw.get('volume', 0) > 1000
            ]
            low_hanging.sort(key=lambda x: x.get('volume', 0), reverse=True)
            opportunity_data['low_hanging_fruit'] = low_hanging[:10]
            
        except Exception as e:
            logger.warning(f"SEO opportunity analysis failed: {e}")
            opportunity_data = {"error": str(e)}
        
        # Step 3: Detect anomalies (existing functionality)
        logger.info("🔍 Detecting anomalies...")
        anomalies = []
        if historical_data:
            # Your existing anomaly detection logic here
            pass
        
        # Step 4: Generate enhanced AI insights
        logger.info("🤖 Generating enhanced AI insights...")
        insights = generate_enhanced_claude_insights(
            ranking_data=json.loads(ranking_data),
            competitor_data=json.loads(competitor_data),
            anomalies=anomalies,
            opportunity_data=opportunity_data
        )
        
        # Step 5: Generate opportunity-specific insights
        opportunity_insights = generate_opportunity_insights(opportunity_data)
        
        # Step 6: Create comprehensive report
        logger.info("📝 Generating comprehensive report...")
        
        # Parse ranking data for summary
        ranking_json = json.loads(ranking_data)
        keywords_data = ranking_json.get('keywords', {})
        
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
Data: SEranking MCP + Claude AI
"""
        
        return jsonify({
            "success": True,
            "domain": domain,
            "date": datetime.now().strftime('%Y-%m-%d'),
            "summary": summary,
            "data": {
                "rankings": ranking_json,
                "competitors": json.loads(competitor_data),
                "metrics": json.loads(metrics_data),
                "opportunities": opportunity_data
            },
            "insights": insights,
            "opportunity_insights": opportunity_insights,
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

# Keep existing endpoints for backward compatibility
@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    """Original report endpoint (backward compatibility)"""
    # Your existing implementation here
    pass

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
