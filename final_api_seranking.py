#!/usr/bin/env python3
"""
SEO Intelligence API for Google Cloud Run - SEranking Version
- Fetches data from SEranking
- Detects anomalies using historical data from n8n
- Generates Claude AI insights
- Returns complete report to n8n
"""
import asyncio
import json
import logging
import os
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# Import SEranking MCP functions
from seranking_mcp import get_keyword_rankings, get_competitor_rankings, get_keyword_metrics
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

def detect_top10_changes(historical_data: list, current_rankings: dict) -> dict:
    """
    Detect keywords that entered or exited Top 10
    """
    changes = {
        "new_entries": [],  # Entered Top 10
        "exits": [],        # Dropped from Top 10
        "improvements": [], # Moved up within Top 10
        "declines": []      # Moved down within Top 10
    }
    
    # Quick exit if no historical data
    if not historical_data:
        # Check if any current rankings are in Top 10
        current_keywords = current_rankings.get('keywords', {})
        
        # Handle both dict and list formats (defensive coding)
        if isinstance(current_keywords, list):
            current_keywords_dict = {}
            for item in current_keywords:
                if isinstance(item, dict) and 'keyword' in item:
                    keyword = item['keyword']
                    current_keywords_dict[keyword] = item
            current_keywords = current_keywords_dict
        
        for keyword, info in current_keywords.items():
            if info.get('position', 0) <= 10:
                changes["new_entries"].append({
                    "keyword": keyword,
                    "current_position": info['position'],
                    "previous_position": None
                })
        return changes
    
    # Build lookup dict for O(1) access instead of O(n) search
    recent_positions = {}
    for record in historical_data:
        keyword = record.get('keyword')
        if keyword and record.get('position'):
            recent_positions[keyword] = record['position']
    
    # Compare with current positions
    current_keywords = current_rankings.get('keywords', {})
    
    # Handle both dict and list formats (defensive coding)
    if isinstance(current_keywords, list):
        current_keywords_dict = {}
        for item in current_keywords:
            if isinstance(item, dict) and 'keyword' in item:
                keyword = item['keyword']
                current_keywords_dict[keyword] = item
        current_keywords = current_keywords_dict
    
    for keyword, info in current_keywords.items():
        current_pos = info.get('position')
        if not current_pos:
            continue
            
        previous_pos = recent_positions.get(keyword)
        
        if previous_pos is None:
            # New keyword being tracked
            if current_pos <= 10:
                changes["new_entries"].append({
                    "keyword": keyword,
                    "current_position": current_pos,
                    "previous_position": None
                })
        elif previous_pos > 10 and current_pos <= 10:
            # Entered Top 10
            changes["new_entries"].append({
                "keyword": keyword,
                "current_position": current_pos,
                "previous_position": previous_pos
            })
        elif previous_pos <= 10 and current_pos > 10:
            # Dropped from Top 10
            changes["exits"].append({
                "keyword": keyword,
                "current_position": current_pos,
                "previous_position": previous_pos
            })
        elif previous_pos <= 10 and current_pos <= 10:
            # Movement within Top 10
            if current_pos < previous_pos:
                changes["improvements"].append({
                    "keyword": keyword,
                    "current_position": current_pos,
                    "previous_position": previous_pos,
                    "change": previous_pos - current_pos
                })
            elif current_pos > previous_pos:
                changes["declines"].append({
                    "keyword": keyword,
                    "current_position": current_pos,
                    "previous_position": previous_pos,
                    "change": current_pos - previous_pos
                })
    
    return changes

def calculate_anomalies_from_history(historical_data: list) -> list:
    """
    OPTIMIZED: Calculate statistical anomalies from historical data
    Takes <100ms even for 100+ keywords. This is NOT the bottleneck.
    """
    # Quick exit for insufficient data
    if len(historical_data) < 7:
        return []
    
    anomalies = []
    
    # Group by keyword (O(n) - one pass)
    by_keyword = {}
    for record in historical_data:
        keyword = record.get('keyword')
        position = record.get('position')
        if keyword and position:
            if keyword not in by_keyword:
                by_keyword[keyword] = []
            by_keyword[keyword].append(position)
    
    # Calculate anomalies for each keyword (O(k * m) where k=keywords, m=history length)
    for keyword, positions in by_keyword.items():
        # Skip keywords with insufficient data
        if len(positions) < 7:
            continue
        
        # Calculate statistics (vectorized where possible)
        n = len(positions)
        mean = sum(positions) / n
        variance = sum((p - mean) ** 2 for p in positions) / n
        std = variance ** 0.5
        
        # Skip if no variation (std=0 means all positions are identical)
        if std == 0:
            continue
        
        # Current position (most recent)
        current = positions[0]
        
        # Z-score analysis (95% confidence = 2.0σ)
        z_score = abs(current - mean) / std
        
        # Only flag significant anomalies
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
        "service": "SEO Intelligence API - SEranking Version",
        "status": "running",
        "version": "1.0",
        "data_provider": "SEranking",
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
        "service": "SEO Intelligence API",
        "data_provider": "SEranking",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    """
    Complete SEO report generation using SEranking
    
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
        logger.info("🚀 Generating SEO report (SEranking)...")
        
        # Get request data from n8n or user
        data = request.json or {}
        
        # Allow user to specify domain, keywords, and competitors
        target_domain = data.get('domain', config.TARGET_DOMAIN)
        keywords = data.get('keywords', config.GENERIC_KEYWORDS)  # Use ALL keywords from config
        
        # Competitors: Use provided list, or config defaults
        # Only auto-discover if explicitly requested with empty list AND auto_discover flag
        competitors = data.get('competitors')
        auto_discover = data.get('auto_discover_competitors', False)
        
        if competitors is None:
            # No competitors provided - use config defaults
            competitors = config.COMPETITOR_DOMAINS  # Use ALL competitors from config
        elif len(competitors) == 0 and not auto_discover:
            # Empty list but no auto-discover flag - use config defaults
            competitors = config.COMPETITOR_DOMAINS  # Use ALL competitors from config
        # else: use the provided competitors list (even if empty with auto_discover flag)
        
        historical_data = data.get('historical_data', [])  # n8n sends this
        
        # Priority-based keyword filtering
        # Use provided priorities, or defaults from config, or auto-assign "medium"
        keyword_priorities = data.get('keyword_priorities', config.DEFAULT_KEYWORD_PRIORITIES)
        check_frequency = data.get('check_frequency', 'daily')  # daily, weekly, monthly
        
        # Filter keywords based on priority and frequency
        if keyword_priorities and check_frequency != 'daily':
            filtered_keywords = []
            for keyword in keywords:
                priority = keyword_priorities.get(keyword, 'medium')
                if check_frequency == 'weekly' and priority in ['high', 'medium']:
                    filtered_keywords.append(keyword)
                elif check_frequency == 'monthly' and priority == 'high':
                    filtered_keywords.append(keyword)
                else:
                    filtered_keywords.append(keyword)
            keywords = filtered_keywords if filtered_keywords else keywords
        
        logger.info(f"📊 Fetching fresh data for {len(keywords)} keywords from SEranking...")
        
        # Fetch fresh data from SEranking IN PARALLEL (pass domain to functions)
        logger.info("🚀 Running SEranking API calls in parallel for speed...")
        
        import asyncio
        from seranking_mcp import get_competitor_summary
        
        async def fetch_all_data():
            """Fetch all SEranking data in parallel to save time"""
            tasks = [
                get_keyword_rankings(keywords, target_domain),
                get_competitor_rankings(competitors, keywords),
                get_keyword_metrics(keywords),
                get_competitor_summary(target_domain, competitors)
            ]
            return await asyncio.gather(*tasks)
        
        ranking_data, competitor_data, keyword_metrics, competitor_summary = run_async(fetch_all_data())
        
        ranking_json = json.loads(ranking_data)
        competitor_json = json.loads(competitor_data)
        metrics_json = json.loads(keyword_metrics)
        competitor_summary_json = json.loads(competitor_summary)
        
        # Calculate anomalies from historical data (OPTIMIZED - takes <100ms)
        if len(historical_data) >= 7:
            logger.info("🔍 Detecting statistical anomalies...")
            anomalies = calculate_anomalies_from_history(historical_data)
        else:
            logger.info(f"⚠️ Skipping anomaly detection: {len(historical_data)} records (need 7+)")
            anomalies = []
        
        # Detect Top 10 changes
        logger.info("🔍 Detecting Top 10 entry/exit...")
        top10_changes = detect_top10_changes(historical_data, ranking_json)
        
        logger.info(f"   Found {len(anomalies)} anomalies, {len(top10_changes.get('new_entries', []))} new Top 10 entries")
        
        # Generate Claude AI insights
        logger.info("🤖 Generating Claude AI insights...")
        insights = generate_claude_insights(
            ranking_json,
            competitor_json,
            anomalies,
            None
        )
        
        # Calculate summary stats
        domain_keywords = ranking_json.get('keywords', {})
        
        # Handle both dict and list formats (defensive coding)
        if isinstance(domain_keywords, list):
            # Convert list to dict format
            domain_keywords_dict = {}
            for item in domain_keywords:
                if isinstance(item, dict) and 'keyword' in item:
                    keyword = item['keyword']
                    domain_keywords_dict[keyword] = item
            domain_keywords = domain_keywords_dict
        
        total_keywords = len(domain_keywords)
        page_1_keywords = sum(1 for k, v in domain_keywords.items() if v.get('position') and v['position'] <= 10)
        
        # Calculate visibility
        total_score = 0
        for keyword, info in domain_keywords.items():
            position = info.get('position')
            if position and position <= 10:
                score = max(0, 100 - (position - 1) * 10)
                total_score += score
        
        visibility_score = round(total_score / total_keywords, 1) if total_keywords > 0 else 0
        
        # Format report  
        report = f"""📊 SEO DAILY BRIEF (SEranking)

📊 PERFORMANCE SUMMARY:
• {page_1_keywords}/{total_keywords} keywords on page 1
• Visibility score: {visibility_score}

"""
        
        # Add rankings
        if domain_keywords:
            report += "📈 CURRENT RANKINGS:\n"
            for keyword, info in list(domain_keywords.items())[:10]:
                if info.get('position'):
                    report += f"• \"{keyword}\": #{info['position']}\n"
            report += "\n"
        
        # Add keyword metrics
        # Handle metrics (defensive coding)
        metrics_keywords = metrics_json.get('keywords', {})
        if isinstance(metrics_keywords, list):
            # Convert list to dict
            metrics_dict = {}
            for item in metrics_keywords:
                if isinstance(item, dict) and 'keyword' in item:
                    metrics_dict[item['keyword']] = item
            metrics_keywords = metrics_dict
        
        if metrics_keywords:
            report += "💰 SEARCH VOLUME & VALUE:\n"
            for keyword, metrics in list(metrics_keywords.items())[:5]:
                volume = metrics.get('search_volume', 0)
                cpc = metrics.get('cpc', 0)
                if volume > 0:
                    report += f"• \"{keyword}\": {volume:,}/mo, ${cpc:.2f} CPC\n"
            report += "\n"
        
        # Add Top 10 changes
        if top10_changes.get('new_entries') or top10_changes.get('exits'):
            report += "🔥 TOP 10 CHANGES:\n"
            for entry in top10_changes.get('new_entries', [])[:3]:
                prev = f" (from #{entry['previous_position']})" if entry['previous_position'] else " (NEW)"
                report += f"✅ \"{entry['keyword']}\": entered Top 10 at #{entry['current_position']}{prev}\n"
            for exit in top10_changes.get('exits', [])[:3]:
                report += f"❌ \"{exit['keyword']}\": dropped from #{exit['previous_position']} to #{exit['current_position']}\n"
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
        
        # Add competitor summary
        if competitor_summary_json.get('competitors'):
            report += "🏆 COMPETITOR OVERVIEW:\n"
            for comp in competitor_summary_json['competitors'][:3]:
                report += f"• {comp['domain']}: "
                if comp.get('total_keywords'):
                    report += f"{comp['total_keywords']:,} keywords, ~{comp.get('traffic_sum', 0):,} monthly traffic\n"
                else:
                    report += "tracking...\n"
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
        
        report += f"\n---\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nData: SEranking\nAI: {insights.get('model')}"
        
        # Prepare enriched data for n8n Data Table storage
        enriched_rankings = []
        
        # Handle metrics format (defensive coding)
        metrics_data = metrics_json.get('keywords', {})
        if isinstance(metrics_data, list):
            metrics_dict = {}
            for item in metrics_data:
                if isinstance(item, dict) and 'keyword' in item:
                    metrics_dict[item['keyword']] = item
            metrics_data = metrics_dict
        
        for keyword, rank_info in domain_keywords.items():
            # Get metrics for this keyword
            metrics = metrics_data.get(keyword, {})
            
            # Get previous position from history
            prev_pos = None
            for hist_record in historical_data:
                if hist_record.get('keyword') == keyword:
                    prev_pos = hist_record.get('position')
                    break
            
            # Get keyword priority from request data
            priority = keyword_priorities.get(keyword, 'medium')
            
            enriched_rankings.append({
                "keyword": keyword,
                "domain": target_domain,
                "position": rank_info.get('position'),
                "previous_position": prev_pos,
                "url": rank_info.get('url'),
                "title": rank_info.get('title'),
                "date": datetime.now().strftime("%Y-%m-%d"),
                "timestamp": datetime.now().isoformat(),
                "keyword_priority": priority,
                "search_volume": metrics.get('search_volume', 0),
                "cpc": metrics.get('cpc', 0),
                "difficulty": metrics.get('difficulty', 0),
                "in_top10": rank_info.get('position') is not None and rank_info.get('position') <= 10
            })
        
        # Return everything to n8n
        response = {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "data_provider": "SEranking",
            "report": report,
            "data": {
                "rankings": ranking_json,
                "enriched_rankings": enriched_rankings,  # NEW: Ready for Data Table
                "competitors": competitor_json,
                "competitor_summary": competitor_summary_json,
                "metrics": metrics_json
            },
            "anomalies": anomalies,
            "top10_changes": top10_changes,
            "insights": insights,
            "summary": {
                "keywords_tracked": total_keywords,
                "page_1_keywords": page_1_keywords,
                "visibility_score": visibility_score,
                "anomalies_count": len(anomalies),
                "new_top10_entries": len(top10_changes.get('new_entries', [])),
                "top10_exits": len(top10_changes.get('exits', [])),
                "competitors_tracked": len(competitor_summary_json.get('competitors', []))
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
    logger.info(f"🚀 Starting SEO API (SEranking) on port {port}")
    logger.info(f"   Data Provider: SEranking")
    logger.info(f"   Stateless: Yes")
    logger.info(f"   Storage: Handled by n8n")
    logger.info(f"   Anomaly Detection: In API")
    app.run(host='0.0.0.0', port=port, debug=False)


