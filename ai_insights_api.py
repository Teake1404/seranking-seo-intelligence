#!/usr/bin/env python3
"""
AI Insights API for Google Cloud Run
- Receives data from n8n (from SEranking MCP)
- Generates enhanced Claude AI insights
- Returns AI-powered recommendations
"""
import json
import logging
import os
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# Import our modules
from enhanced_claude_insights import generate_enhanced_claude_insights
from seo_opportunity_analysis import SEOOpportunityAnalyzer
import config

# Initialize Flask
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/', methods=['GET'])
def home():
    """Root endpoint"""
    return jsonify({
        "service": "AI Insights API - SEranking Integration",
        "status": "running",
        "version": "1.0",
        "data_provider": "n8n + SEranking MCP",
        "architecture": "AI Insights Only",
        "features": [
            "AI-Powered SEO Insights",
            "SEO Opportunity Analysis",
            "Competitive Intelligence",
            "Actionable Recommendations"
        ],
        "endpoints": {
            "health": "/health",
            "ai_insights": "/api/ai-insights (POST)",
            "seo_opportunities": "/api/seo-opportunities (POST)"
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "1.0",
        "timestamp": datetime.now().isoformat(),
        "ai_powered": True
    })

@app.route('/api/seo-opportunities', methods=['POST'])
def seo_opportunities_endpoint():
    """SEO opportunity analysis endpoint"""
    data = request.json
    domain = data.get('domain')
    market = data.get('market')

    if not domain or not market:
        return jsonify({"success": False, "error": "Domain and market are required."}), 400

    try:
        logger.info(f"Starting SEO opportunity analysis for domain: {domain}, market: {market}")
        analyzer = SEOOpportunityAnalyzer(config.SERANKING_API_TOKEN)
        opportunity_results = analyzer.analyze_domain_performance()
        return jsonify({
            "success": True, 
            "domain": domain, 
            "market": market, 
            "opportunities": opportunity_results,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error during SEO opportunity analysis: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/ai-insights', methods=['POST'])
def generate_ai_insights():
    """
    Generates AI insights from data provided by n8n (from SEranking MCP)
    Expected input from n8n: Raw data from SEranking MCP
    """
    start_time = datetime.now()
    data = request.json
    
    # Extract raw data from n8n
    rankings_data_raw = data.get('rankings_data', '')
    backlinks_data_raw = data.get('backlinks_data', '')
    competitors_data_raw = data.get('competitors_data', '')
    domain = data.get('domain', 'bagsoflove.co.uk')
    market = data.get('market', 'uk')

    logger.info(f"Generating AI insights for {domain} from n8n data.")

    try:
        # Parse all data types from n8n
        logger.info("Parsing n8n data...")
        rankings_data = parse_n8n_data(rankings_data_raw)
        backlinks_data = parse_n8n_backlinks_data(backlinks_data_raw)
        competitors_data = parse_n8n_competitors_data(competitors_data_raw)
        
        logger.info(f"Parsed data - Rankings: {len(rankings_data)} items, Backlinks: {len(backlinks_data)} keys, Competitors: {len(competitors_data)} items")
        
        # Convert rankings to our expected format
        current_rankings = {
            "keywords": {}
        }
        
        for item in rankings_data:
            keyword = item.get('keyword')
            if keyword:
                current_rankings["keywords"][keyword] = {
                    'position': item.get('position'),
                    'url': item.get('url'),
                    'title': None,  # Not available in this data
                    'search_volume': item.get('volume'),
                    'cpc': item.get('cpc'),
                    'difficulty': item.get('difficulty'),
                    'traffic': item.get('traffic'),
                    'prev_position': item.get('prev_pos')
                }

        # Convert competitors data
        competitor_rankings = {
            "keywords": {}
        }
        
        # Process top competitors (limit to top 10 for performance)
        top_competitors = competitors_data[:10] if competitors_data else []
        
        # Convert backlinks data
        backlink_summary = {}
        if backlinks_data and 'summary' in backlinks_data and backlinks_data['summary']:
            summary = backlinks_data['summary'][0]  # Get first (and likely only) summary
            backlink_summary = {
                'total_backlinks': summary.get('backlinks', 0),
                'referring_domains': summary.get('refdomains', 0),
                'dofollow_backlinks': summary.get('dofollow_backlinks', 0),
                'nofollow_backlinks': summary.get('nofollow_backlinks', 0),
                'edu_backlinks': summary.get('edu_backlinks', 0),
                'gov_backlinks': summary.get('gov_backlinks', 0),
                'inlink_rank': summary.get('inlink_rank', 0),
                'domain_inlink_rank': summary.get('domain_inlink_rank', 0),
                'top_anchors': summary.get('top_anchors_by_backlinks', [])[:5],
                'top_pages': summary.get('top_pages_by_backlinks', [])[:5]
            }

        # 1. Detect anomalies from historical data
        logger.info("Detecting anomalies...")
        anomalies = detect_anomalies([], current_rankings)  # No historical data for now

        # 2. Detect Top 10 changes
        logger.info("Detecting Top 10 changes...")
        top10_changes = detect_top10_changes([], current_rankings)

        # 3. SEO Opportunity Analysis
        logger.info("Performing SEO opportunity analysis...")
        try:
            analyzer = SEOOpportunityAnalyzer(config.SERANKING_API_TOKEN)
            opportunity_analysis_results = analyzer.analyze_domain_performance()
        except Exception as e:
            logger.warning(f"SEO opportunity analysis failed: {e}")
            opportunity_analysis_results = {"error": str(e)}

        # 4. Generate Enhanced Claude AI Insights
        logger.info("Generating enhanced Claude AI insights...")
        ai_insights = generate_enhanced_claude_insights(
            current_rankings,
            competitor_rankings,
            anomalies,
            opportunity_analysis_results,
            backlink_summary  # Include backlink data
        )

        # 5. Generate Summary
        total_keywords = len(current_rankings.get('keywords', {}))
        page_1_keywords = sum(1 for kw_data in current_rankings.get('keywords', {}).values() 
                             if kw_data.get('position') and kw_data['position'] <= 10)
        
        # Calculate visibility score
        visibility_score = 0.0
        if total_keywords > 0:
            for kw_data in current_rankings.get('keywords', {}).values():
                pos = kw_data.get('position')
                if pos and pos > 0 and pos <= 100:
                    visibility_score += (101 - pos)
            visibility_score = (visibility_score / (total_keywords * 100)) * 100
        
        summary = {
            "keywords_tracked": total_keywords,
            "page_1_keywords": page_1_keywords,
            "visibility_score": round(visibility_score, 2),
            "anomalies_count": len(anomalies),
            "new_top10_entries": len(top10_changes["new_entries"]),
            "top10_exits": len(top10_changes["exits"]),
            "opportunities_found": len(opportunity_analysis_results.get('low_hanging_fruit', [])) + \
                                   len(opportunity_analysis_results.get('competitor_gap_keywords', []))
        }

        # 6. Generate Final Report Text
        report_text = f"""📊 SEO AI INSIGHTS REPORT - {domain.upper()}

📊 PERFORMANCE SUMMARY:
• {summary['page_1_keywords']}/{summary['keywords_tracked']} keywords on page 1
• Visibility score: {summary['visibility_score']}%
• Anomalies detected: {summary['anomalies_count']}
• New opportunities identified: {summary['opportunities_found']}

📈 CURRENT RANKINGS:
"""
        # Sort by position for better display
        sorted_keywords = sorted(current_rankings.get('keywords', {}).items(), 
                               key=lambda x: x[1].get('position') or 999)
        
        for keyword, rank_info in sorted_keywords:
            pos_str = f"#{rank_info.get('position')}" if rank_info.get('position') else "Not ranked"
            prev_pos = rank_info.get('prev_position')
            prev_str = f" (Prev: #{prev_pos})" if prev_pos else ""
            volume = rank_info.get('search_volume', 0)
            cpc = rank_info.get('cpc', 0)
            report_text += f"• \"{keyword}\": {pos_str}{prev_str} | Vol: {volume:,} | CPC: £{cpc}\n"

        if top10_changes["new_entries"] or top10_changes["exits"] or top10_changes["improvements"] or top10_changes["declines"]:
            report_text += "\n🔥 TOP 10 CHANGES:\n"
            for entry in top10_changes["new_entries"]:
                report_text += f"✅ \"{entry['keyword']}\": entered Top 10 at #{entry['current_position']}\n"
            for exit_kw in top10_changes["exits"]:
                report_text += f"❌ \"{exit_kw['keyword']}\": exited Top 10 (Current: #{exit_kw['current_position']})\n"
            for imp in top10_changes["improvements"]:
                report_text += f"⬆️ \"{imp['keyword']}\": improved to #{imp['current_position']}\n"
            for dec in top10_changes["declines"]:
                report_text += f"⬇️ \"{dec['keyword']}\": declined to #{dec['current_position']}\n"

        if top_competitors:
            report_text += "\n🏆 TOP COMPETITORS:\n"
            for comp in top_competitors[:5]:  # Show top 5
                report_text += f"• {comp.get('domain', 'Unknown')}: {comp.get('common_keywords', 0):,} common keywords\n"

        if backlink_summary:
            report_text += "\n🔗 BACKLINK PROFILE:\n"
            report_text += f"• Total backlinks: {backlink_summary.get('total_backlinks', 0):,}\n"
            report_text += f"• Referring domains: {backlink_summary.get('referring_domains', 0):,}\n"
            report_text += f"• Do-follow backlinks: {backlink_summary.get('dofollow_backlinks', 0):,}\n"
            report_text += f"• InLink Rank: {backlink_summary.get('inlink_rank', 0)}\n"
            
            if backlink_summary.get('top_anchors'):
                report_text += "\n🔗 TOP ANCHOR TEXTS:\n"
                for anchor in backlink_summary['top_anchors'][:3]:
                    report_text += f"• \"{anchor.get('anchor', 'Unknown')}\": {anchor.get('backlinks', 0):,} backlinks\n"

        if ai_insights.get('critical_changes'):
            report_text += "\n🔴 CRITICAL INSIGHTS (Claude AI):\n"
            for insight in ai_insights['critical_changes']:
                report_text += f"• {insight}\n"
        
        if ai_insights.get('competitive_insights'):
            report_text += "\n🎯 COMPETITIVE LANDSCAPE (Claude AI):\n"
            for insight in ai_insights['competitive_insights']:
                report_text += f"• {insight}\n"

        if ai_insights.get('opportunity_insights'):
            report_text += "\n💡 SEO OPPORTUNITIES (Claude AI):\n"
            for insight in ai_insights['opportunity_insights']:
                report_text += f"• {insight}\n"

        if ai_insights.get('recommendations'):
            report_text += "\n🎯 ACTIONABLE RECOMMENDATIONS (Claude AI):\n"
            for i, rec in enumerate(ai_insights['recommendations'], 1):
                report_text += f"{i}. {rec}\n"

        # 7. Return AI insights response
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()

        return jsonify({
            "success": True,
            "domain": domain,
            "timestamp": datetime.now().isoformat(),
            "processing_time_seconds": round(processing_time, 2),
            "summary": summary,
            "current_rankings": current_rankings,
            "competitor_rankings": competitor_rankings,
            "backlink_summary": backlink_summary,
            "top_competitors": top_competitors[:10],  # Include top 10 competitors
            "anomalies": anomalies,
            "top10_changes": top10_changes,
            "opportunity_analysis": opportunity_analysis_results,
            "ai_insights": ai_insights,
            "report_text": report_text,
            "data_source": "n8n + SEranking MCP",
            "ai_powered": True
        })

    except Exception as e:
        logger.error(f"Error generating AI insights: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

def parse_n8n_data(raw_data):
    """Parse the raw data from n8n SEranking MCP"""
    try:
        if not raw_data or raw_data.strip() == '':
            logger.warning("No rankings data provided")
            return []
            
        # Extract JSON from the raw data string
        import re
        # Look for JSON array pattern in the SSE data
        json_match = re.search(r'\[.*\]', raw_data, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            # Clean up the JSON string
            json_str = json_str.replace('\\"', '"').replace('\\n', '\n')
            return json.loads(json_str)
        else:
            logger.warning("No JSON array found in rankings data")
            return []
    except Exception as e:
        logger.error(f"Error parsing n8n rankings data: {e}")
        return []

def parse_n8n_backlinks_data(raw_data):
    """Parse backlinks data from n8n SEranking MCP"""
    try:
        if not raw_data or raw_data.strip() == '':
            logger.warning("No backlinks data provided")
            return {}
            
        # Extract JSON from the raw data string
        import re
        # Look for JSON object pattern in the SSE data
        json_match = re.search(r'\{.*\}', raw_data, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            # Clean up the JSON string
            json_str = json_str.replace('\\"', '"').replace('\\n', '\n')
            return json.loads(json_str)
        else:
            logger.warning("No JSON object found in backlinks data")
            return {}
    except Exception as e:
        logger.error(f"Error parsing n8n backlinks data: {e}")
        return {}

def parse_n8n_competitors_data(raw_data):
    """Parse competitors data from n8n SEranking MCP"""
    try:
        if not raw_data or raw_data.strip() == '':
            logger.warning("No competitors data provided")
            return []
            
        # Extract JSON from the raw data string
        import re
        # Look for JSON array pattern in the SSE data
        json_match = re.search(r'\[.*\]', raw_data, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            # Clean up the JSON string
            json_str = json_str.replace('\\"', '"').replace('\\n', '\n')
            return json.loads(json_str)
        else:
            logger.warning("No JSON array found in competitors data")
            return []
    except Exception as e:
        logger.error(f"Error parsing n8n competitors data: {e}")
        return []

def detect_top10_changes(historical_data: list, current_rankings: dict) -> dict:
    """Detect keywords that entered or exited Top 10"""
    changes = {
        "new_entries": [],
        "exits": [],
        "improvements": [],
        "declines": []
    }
    
    if not historical_data:
        current_keywords = current_rankings.get('keywords', {})
        for keyword, info in current_keywords.items():
            if info.get('position', 0) <= 10 and info.get('position', 0) > 0:
                changes["new_entries"].append({
                    "keyword": keyword,
                    "current_position": info['position'],
                    "previous_position": None
                })
        return changes
    
    recent_positions = {}
    for record in historical_data:
        keyword = record.get('keyword')
        if keyword and record.get('position'):
            recent_positions[keyword] = record['position']
    
    current_keywords = current_rankings.get('keywords', {})
    
    for keyword, info in current_keywords.items():
        current_pos = info.get('position')
        if not current_pos or current_pos <= 0:
            continue
            
        previous_pos = recent_positions.get(keyword)
        
        if previous_pos is None:
            if current_pos <= 10:
                changes["new_entries"].append({
                    "keyword": keyword,
                    "current_position": current_pos,
                    "previous_position": None
                })
        else:
            if current_pos <= 10 and previous_pos > 10:
                changes["new_entries"].append({
                    "keyword": keyword,
                    "current_position": current_pos,
                    "previous_position": previous_pos
                })
            elif current_pos > 10 and previous_pos <= 10:
                changes["exits"].append({
                    "keyword": keyword,
                    "current_position": current_pos,
                    "previous_position": previous_pos
                })
            elif current_pos <= 10 and previous_pos <= 10:
                if current_pos < previous_pos:
                    changes["improvements"].append({
                        "keyword": keyword,
                        "current_position": current_pos,
                        "previous_position": previous_pos
                    })
                elif current_pos > previous_pos:
                    changes["declines"].append({
                        "keyword": keyword,
                        "current_position": current_pos,
                        "previous_position": previous_pos
                    })
                    
    return changes

def detect_anomalies(historical_data: list, current_rankings: dict) -> list:
    """Detects anomalies in keyword rankings"""
    anomalies = []
    
    if not historical_data:
        logger.info("No historical data for anomaly detection.")
        return anomalies

    keyword_history = {}
    for record in historical_data:
        keyword = record.get('keyword')
        position = record.get('position')
        if keyword and position and position > 0:
            if keyword not in keyword_history:
                keyword_history[keyword] = []
            keyword_history[keyword].append(position)

    current_keywords = current_rankings.get('keywords', {})

    for keyword, info in current_keywords.items():
        current_pos = info.get('position')
        if not current_pos or current_pos <= 0:
            continue

        history = keyword_history.get(keyword)
        if history and len(history) >= 2:
            import numpy as np
            avg_pos = np.mean(history)
            std_dev = np.std(history)
            
            is_anomaly = False
            severity = "medium"
            anomaly_type = "position_change"

            if std_dev > 0:
                z_score = abs((current_pos - avg_pos) / std_dev)
                if z_score > 2.0:
                    is_anomaly = True
                    severity = "high" if z_score > 3.0 else "medium"
            else:
                if abs(current_pos - avg_pos) > 5:  # Simple threshold
                    is_anomaly = True
                    severity = "high" if abs(current_pos - avg_pos) > 10 else "medium"
            
            if is_anomaly:
                anomalies.append({
                    "keyword": keyword,
                    "current_position": current_pos,
                    "expected_position": round(avg_pos),
                    "type": anomaly_type,
                    "severity": severity,
                    "z_score": round(z_score, 2) if std_dev > 0 else "N/A"
                })
        elif history and len(history) == 1:
            if abs(current_pos - history[0]) > 5:
                anomalies.append({
                    "keyword": keyword,
                    "current_position": current_pos,
                    "expected_position": history[0],
                    "type": "significant_change",
                    "severity": "medium",
                    "z_score": "N/A (single data point)"
                })

    return anomalies

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
