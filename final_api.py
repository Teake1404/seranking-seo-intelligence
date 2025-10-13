#!/usr/bin/env python3
"""
Nike SEO Intelligence API for Google Cloud Run
- Fetches data from DataForSEO
- Detects anomalies using historical data from n8n
- Generates Claude AI insights
- Returns complete report to n8n
"""
import asyncio
import json
import logging
import os
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# Import MCP functions
from dataforseo_mcp import get_nike_keyword_rankings, get_competitor_rankings, get_keyword_metrics
from claude_insights import generate_claude_insights
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

def calculate_anomalies_from_history(historical_data: list) -> list:
    """
    Calculate statistical anomalies from historical data provided by n8n
    n8n sends historical data, we calculate anomalies
    """
    if len(historical_data) < 7:  # Need at least 1 week
        return []
    
    anomalies = []
    
    # Group by keyword
    by_keyword = {}
    for record in historical_data:
        keyword = record.get('keyword')
        if keyword not in by_keyword:
            by_keyword[keyword] = []
        if record.get('position'):
            by_keyword[keyword].append(record['position'])
    
    # Calculate anomalies for each keyword
    for keyword, positions in by_keyword.items():
        if len(positions) < 7:
            continue
        
        # Calculate statistics
        mean = sum(positions) / len(positions)
        variance = sum((p - mean) ** 2 for p in positions) / len(positions)
        std = variance ** 0.5
        
        # Current position (most recent)
        current = positions[0]
        
        # Z-score
        if std > 0:
            z_score = abs(current - mean) / std
            
            # Is it an anomaly? (2 standard deviations = 95% confidence)
            if z_score >= 2.0:
                deviation = current - mean
                anomalies.append({
                    'keyword': keyword,
                    'current_position': current,
                    'expected_position': round(mean, 1),
                    'deviation': round(deviation, 1),
                    'z_score': round(z_score, 2),
                    'type': 'improvement' if deviation < 0 else 'decline',
                    'severity': 'critical' if z_score >= 3.0 else 'high' if z_score >= 2.5 else 'medium',
                    'previous_position': positions[1] if len(positions) > 1 else current,
                    'change': (positions[1] - current) if len(positions) > 1 else 0
                })
    
    # Sort by z-score (most significant first)
    anomalies.sort(key=lambda x: x['z_score'], reverse=True)
    return anomalies

@app.route('/', methods=['GET'])
def home():
    """Root endpoint"""
    return jsonify({
        "service": "Nike SEO Intelligence API",
        "status": "running",
        "version": "3.0",
        "architecture": "Stateless API + n8n Database",
        "endpoints": {
            "health": "/health",
            "generate_report": "/api/generate-report (POST)"
        }
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        "status": "healthy",
        "service": "Nike SEO Intelligence API",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    """
    Complete Nike SEO report generation
    
    n8n sends:
      - keywords to fetch
      - historical_data (for anomaly detection)
    
    API returns:
      - fresh data (for n8n to store)
      - anomalies (calculated here)
      - Claude AI insights
      - formatted report
    """
    try:
        logger.info("🚀 Generating Nike SEO report...")
        
        # Get request data from n8n
        data = request.json or {}
        keywords = data.get('keywords', config.GENERIC_KEYWORDS[:3])
        historical_data = data.get('historical_data', [])  # n8n sends this
        
        logger.info(f"📊 Fetching fresh data for {len(keywords)} keywords...")
        
        # Fetch fresh data from DataForSEO
        ranking_data = run_async(get_nike_keyword_rankings(keywords))
        competitor_data = run_async(get_competitor_rankings(None, keywords))
        keyword_metrics = run_async(get_keyword_metrics(keywords))
        
        ranking_json = json.loads(ranking_data)
        competitor_json = json.loads(competitor_data)
        metrics_json = json.loads(keyword_metrics)
        
        # Calculate anomalies from historical data n8n provided
        logger.info("🔍 Detecting statistical anomalies...")
        anomalies = calculate_anomalies_from_history(historical_data)
        logger.info(f"   Found {len(anomalies)} anomalies")
        
        # Generate Claude AI insights
        logger.info("🤖 Generating Claude AI insights...")
        insights = generate_claude_insights(
            ranking_json,
            competitor_json,
            anomalies,  # Anomalies calculated here, sent to Claude
            None
        )
        
        # Calculate summary stats
        nike_keywords = ranking_json.get('keywords', {})
        total_keywords = len(nike_keywords)
        page_1_keywords = sum(1 for k, v in nike_keywords.items() if v.get('position') and v['position'] <= 10)
        
        # Calculate visibility
        total_score = 0
        for keyword, info in nike_keywords.items():
            position = info.get('position')
            if position and position <= 10:
                score = max(0, 100 - (position - 1) * 10)
                total_score += score
        
        visibility_score = round(total_score / total_keywords, 1) if total_keywords > 0 else 0
        
        # Format report
        report = f"""🏃 NIKE DAILY SEO BRIEF

📊 PERFORMANCE SUMMARY:
• {page_1_keywords}/{total_keywords} keywords on page 1
• Visibility score: {visibility_score}

"""
        
        # Add rankings
        if nike_keywords:
            report += "📈 CURRENT RANKINGS:\n"
            for keyword, info in list(nike_keywords.items())[:10]:
                if info.get('position'):
                    report += f"• \"{keyword}\": #{info['position']}\n"
            report += "\n"
        
        # Add keyword metrics
        if metrics_json.get('keywords'):
            report += "💰 SEARCH VOLUME & VALUE:\n"
            for keyword, metrics in list(metrics_json.get('keywords', {}).items())[:5]:
                volume = metrics.get('search_volume', 0)
                cpc = metrics.get('cpc', 0)
                if volume > 0:
                    report += f"• \"{keyword}\": {volume:,}/mo, ${cpc:.2f} CPC\n"
            report += "\n"
        
        # Add anomalies if any
        if anomalies:
            report += "🚨 STATISTICAL ANOMALIES DETECTED:\n"
            for anomaly in anomalies[:3]:
                emoji = "📈" if anomaly['type'] == 'improvement' else "📉"
                report += f"{emoji} \"{anomaly['keyword']}\": #{anomaly['current_position']} "
                report += f"(expected: #{anomaly['expected_position']}, "
                report += f"{anomaly['z_score']}σ deviation)\n"
            report += "\n"
        
        # Add Claude AI insights
        if insights.get('critical_changes'):
            report += "🔴 CRITICAL INSIGHTS (Claude AI):\n"
            for change in insights['critical_changes'][:3]:
                report += f"• {change}\n"
            report += "\n"
        
        if insights.get('competitive_insights'):
            report += "🎯 COMPETITIVE LANDSCAPE:\n"
            for insight in insights['competitive_insights'][:3]:
                clean = insight.replace('⚠️ ', '').replace('🎯 ', '')
                report += f"• {clean}\n"
            report += "\n"
        
        if insights.get('recommendations'):
            report += "💡 RECOMMENDATIONS (Claude AI):\n"
            for i, rec in enumerate(insights['recommendations'][:5], 1):
                report += f"{i}. {rec}\n"
        
        report += f"\n---\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nAI Model: {insights.get('model')}"
        
        # Return everything to n8n
        # n8n will store the data in its database
        response = {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "report": report,
            "data": {
                "rankings": ranking_json,
                "competitors": competitor_json,
                "metrics": metrics_json
            },
            "anomalies": anomalies,
            "insights": insights,
            "summary": {
                "keywords_tracked": total_keywords,
                "page_1_keywords": page_1_keywords,
                "visibility_score": visibility_score,
                "anomalies_count": len(anomalies)
            }
        }
        
        logger.info(f"✅ Report generated with {len(anomalies)} anomalies")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

# For Google Cloud Run
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"🚀 Starting Nike SEO API on port {port}")
    logger.info(f"   Stateless: Yes")
    logger.info(f"   Storage: Handled by n8n")
    logger.info(f"   Anomaly Detection: In API (for Claude AI)")
    app.run(host='0.0.0.0', port=port, debug=False)

