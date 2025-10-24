#!/usr/bin/env python3
"""
Enhanced SEO Intelligence API for Google Cloud Run - Direct SEranking API
- Fetches data directly from SEranking API
- Uses Redis caching for performance
- Generates enhanced Claude AI insights
- Returns comprehensive report to n8n
"""
import asyncio
import json
import logging
import os
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import requests
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import time

# Import our modules
from enhanced_claude_insights import generate_enhanced_claude_insights
from seo_opportunity_analysis import analyze_seo_opportunities
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

# Rate limiting
rate_limit_lock = asyncio.Lock()
last_request_time = 0
MIN_REQUEST_INTERVAL = 1.0  # 1 second between requests

async def rate_limited_request(session, url, headers, params=None):
    """Make rate-limited requests to SEranking API"""
    global last_request_time
    
    async with rate_limit_lock:
        current_time = time.time()
        time_since_last = current_time - last_request_time
        
        if time_since_last < MIN_REQUEST_INTERVAL:
            await asyncio.sleep(MIN_REQUEST_INTERVAL - time_since_last)
        
        last_request_time = time.time()
        
        try:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 429:
                    # Rate limited, wait and retry
                    await asyncio.sleep(2)
                    async with session.get(url, headers=headers, params=params) as retry_response:
                        return await retry_response.json()
                elif response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"API request failed with status {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return None

async def get_keyword_rankings(keywords, domain):
    """Get keyword rankings from SEranking API"""
    cache = get_cache()
    cache_key = f"rankings:{domain}:{':'.join(keywords)}"
    
    # Check cache first
    if cache.is_available():
        cached_data = await cache.get(cache_key)
        if cached_data:
            logger.info("Returning cached rankings data")
            return json.dumps(cached_data)
    
    headers = {
        'Authorization': f'Bearer {config.SERANKING_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    url = "https://api.seranking.com/v3/rankings"
    
    async with aiohttp.ClientSession() as session:
        results = {"keywords": {}}
        
        for keyword in keywords:
            params = {
                'keyword': keyword,
                'domain': domain,
                'limit': 1
            }
            
            data = await rate_limited_request(session, url, headers, params)
            
            if data and 'rankings' in data and data['rankings']:
                ranking = data['rankings'][0]
                results["keywords"][keyword] = {
                    'position': ranking.get('position'),
                    'url': ranking.get('url'),
                    'title': ranking.get('title')
                }
            else:
                results["keywords"][keyword] = {
                    'position': None,
                    'url': None,
                    'title': None
                }
        
        # Cache the results
        if cache.is_available():
            await cache.set(cache_key, results, ttl=config.REDIS_CACHE_TTL.get('rankings', 3600))
        
        return json.dumps(results)

async def get_competitor_rankings(competitors, keywords):
    """Get competitor rankings from SEranking API"""
    cache = get_cache()
    cache_key = f"competitor_rankings:{':'.join(competitors)}:{':'.join(keywords)}"
    
    # Check cache first
    if cache.is_available():
        cached_data = await cache.get(cache_key)
        if cached_data:
            logger.info("Returning cached competitor data")
            return json.dumps(cached_data)
    
    headers = {
        'Authorization': f'Bearer {config.SERANKING_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    url = "https://api.seranking.com/v3/rankings"
    
    async with aiohttp.ClientSession() as session:
        results = {"keywords": {}}
        
        for competitor in competitors:
            for keyword in keywords:
                params = {
                    'keyword': keyword,
                    'domain': competitor,
                    'limit': 1
                }
                
                data = await rate_limited_request(session, url, headers, params)
                
                if data and 'rankings' in data and data['rankings']:
                    ranking = data['rankings'][0]
                    if keyword not in results["keywords"]:
                        results["keywords"][keyword] = {}
                    results["keywords"][keyword][competitor] = {
                        'position': ranking.get('position'),
                        'url': ranking.get('url'),
                        'title': ranking.get('title')
                    }
        
        # Cache the results
        if cache.is_available():
            await cache.set(cache_key, results, ttl=config.REDIS_CACHE_TTL.get('competitor_rankings', 3600))
        
        return json.dumps(results)

async def get_keyword_metrics(keywords):
    """Get keyword metrics from SEranking API"""
    cache = get_cache()
    cache_key = f"keyword_metrics:{':'.join(keywords)}"
    
    # Check cache first
    if cache.is_available():
        cached_data = await cache.get(cache_key)
        if cached_data:
            logger.info("Returning cached keyword metrics")
            return json.dumps(cached_data)
    
    headers = {
        'Authorization': f'Bearer {config.SERANKING_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    url = "https://api.seranking.com/v3/keywords/metrics"
    
    async with aiohttp.ClientSession() as session:
        results = {"keywords": {}}
        
        for keyword in keywords:
            params = {'keyword': keyword}
            
            data = await rate_limited_request(session, url, headers, params)
            
            if data:
                results["keywords"][keyword] = {
                    'search_volume': data.get('search_volume'),
                    'cpc': data.get('cpc'),
                    'difficulty': data.get('difficulty')
                }
            else:
                results["keywords"][keyword] = {
                    'search_volume': None,
                    'cpc': None,
                    'difficulty': None
                }
        
        # Cache the results
        if cache.is_available():
            await cache.set(cache_key, results, ttl=config.REDIS_CACHE_TTL.get('keyword_metrics', 86400))
        
        return json.dumps(results)

async def get_competitor_summary(domain, competitors):
    """Get competitor summary from SEranking API"""
    cache = get_cache()
    cache_key = f"competitor_summary:{domain}:{':'.join(competitors)}"
    
    # Check cache first
    if cache.is_available():
        cached_data = await cache.get(cache_key)
        if cached_data:
            logger.info("Returning cached competitor summary")
            return json.dumps(cached_data)
    
    headers = {
        'Authorization': f'Bearer {config.SERANKING_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    url = "https://api.seranking.com/v3/competitors/summary"
    
    async with aiohttp.ClientSession() as session:
        results = {"competitors": []}
        
        for competitor in competitors:
            params = {
                'domain': competitor,
                'target_domain': domain
            }
            
            data = await rate_limited_request(session, url, headers, params)
            
            if data:
                results["competitors"].append({
                    'domain': competitor,
                    'common_keywords': data.get('common_keywords', 0),
                    'visibility_score': data.get('visibility_score', 0)
                })
        
        # Cache the results
        if cache.is_available():
            await cache.set(cache_key, results, ttl=config.REDIS_CACHE_TTL.get('competitor_summary', 86400))
        
        return json.dumps(results)

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
        
        if isinstance(current_keywords, list):
            current_keywords_dict = {}
            for item in current_keywords:
                if isinstance(item, dict) and 'keyword' in item:
                    keyword = item['keyword']
                    current_keywords_dict[keyword] = item
            current_keywords = current_keywords_dict
        
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
    
    if isinstance(current_keywords, list):
        current_keywords_dict = {}
        for item in current_keywords:
            if isinstance(item, dict) and 'keyword' in item:
                keyword = item['keyword']
                current_keywords_dict[keyword] = item
        current_keywords = current_keywords_dict
    
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
    
    if isinstance(current_keywords, list):
        current_keywords_dict = {}
        for item in current_keywords:
            if isinstance(item, dict) and 'keyword' in item:
                keyword = item['keyword']
                current_keywords_dict[keyword] = item
        current_keywords = current_keywords_dict

    for keyword, info in current_keywords.items():
        current_pos = info.get('position')
        if not current_pos or current_pos <= 0:
            continue

        history = keyword_history.get(keyword)
        if history and len(history) >= 2:
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
                if abs(current_pos - avg_pos) > config.ANOMALY_THRESHOLD:
                    is_anomaly = True
                    severity = "high" if abs(current_pos - avg_pos) > (config.ANOMALY_THRESHOLD * 2) else "medium"
            
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
            if abs(current_pos - history[0]) > config.ANOMALY_THRESHOLD:
                anomalies.append({
                    "keyword": keyword,
                    "current_position": current_pos,
                    "expected_position": history[0],
                    "type": "significant_change",
                    "severity": "medium",
                    "z_score": "N/A (single data point)"
                })

    return anomalies

@app.route('/', methods=['GET'])
def home():
    """Root endpoint"""
    cache = get_cache()
    cache_status = "enabled" if cache.is_available() else "disabled"
    
    return jsonify({
        "service": "Enhanced SEO Intelligence API - Direct SEranking API",
        "status": "running",
        "version": "2.0",
        "data_provider": "SEranking Direct API",
        "architecture": "Stateless API + n8n Database + Redis Cache (Optional)",
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
            "generate_report": "/api/enhanced-report (POST)",
            "seo_opportunities": "/api/seo-opportunities (POST)",
            "cache_stats": "/api/cache/stats (GET)",
            "cache_invalidate": "/api/cache/invalidate (POST)"
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    cache = get_cache()
    cache_status = "enabled" if cache.is_available() else "disabled"
    
    return jsonify({
        "status": "healthy",
        "version": "2.0",
        "timestamp": datetime.now().isoformat(),
        "cache": cache_status
    })

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
        opportunity_results = analyze_seo_opportunities(domain, market)
        return jsonify({"success": True, "domain": domain, "market": market, "opportunities": opportunity_results})
    except Exception as e:
        logger.error(f"Error during SEO opportunity analysis: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/enhanced-report', methods=['POST'])
def generate_enhanced_report():
    """Generates a comprehensive SEO report"""
    start_time = datetime.now()
    data = request.json
    
    domain = data.get('domain', config.TARGET_DOMAIN)
    keywords = data.get('keywords', config.GENERIC_KEYWORDS)
    keyword_priorities = data.get('keyword_priorities', config.DEFAULT_KEYWORD_PRIORITIES)
    competitors = data.get('competitors', config.COMPETITOR_DOMAINS)
    check_frequency = data.get('check_frequency', 'daily')
    historical_data = data.get('historical_data', [])
    market = data.get('market', 'us')

    logger.info(f"Generating enhanced report for {domain} with {len(keywords)} keywords and {len(competitors)} competitors.")

    try:
        # 1. Fetch current data from SEranking API
        logger.info("Fetching current data from SEranking API...")
        current_rankings_str, competitor_rankings_str, keyword_metrics_str, competitor_summary_str = run_async(
            asyncio.gather(
                get_keyword_rankings(keywords=keywords, domain=domain),
                get_competitor_rankings(competitors=competitors, keywords=keywords),
                get_keyword_metrics(keywords=keywords),
                get_competitor_summary(domain=domain, competitors=competitors)
            )
        )
        
        current_rankings = json.loads(current_rankings_str)
        competitor_rankings = json.loads(competitor_rankings_str)
        keyword_metrics = json.loads(keyword_metrics_str)
        competitor_summary = json.loads(competitor_summary_str)

        # 2. Enrich current rankings with metrics
        enriched_rankings = []
        for kw, rank_info in current_rankings.get('keywords', {}).items():
            metrics = keyword_metrics.get('keywords', {}).get(kw, {})
            enriched_rankings.append({
                "keyword": kw,
                "position": rank_info.get('position'),
                "url": rank_info.get('url'),
                "title": rank_info.get('title'),
                "search_volume": metrics.get('search_volume'),
                "cpc": metrics.get('cpc'),
                "difficulty": metrics.get('difficulty'),
                "keyword_priority": keyword_priorities.get(kw, 'medium'),
                "date": datetime.now().strftime('%Y-%m-%d'),
                "timestamp": datetime.now().isoformat(),
                "in_top10": rank_info.get('position') is not None and rank_info.get('position') <= 10
            })
        
        # Add previous position for anomaly detection
        for current_kw_data in enriched_rankings:
            keyword = current_kw_data['keyword']
            previous_pos = None
            for hist_record in reversed(historical_data):
                if hist_record.get('keyword') == keyword and hist_record.get('position') is not None:
                    previous_pos = hist_record['position']
                    break
            current_kw_data['previous_position'] = previous_pos

        # 3. Anomaly Detection
        logger.info("Detecting anomalies...")
        anomalies = detect_anomalies(historical_data, current_rankings)

        # 4. Top 10 Changes
        logger.info("Detecting Top 10 changes...")
        top10_changes = detect_top10_changes(historical_data, current_rankings)

        # 5. SEO Opportunity Analysis
        logger.info("Performing SEO opportunity analysis...")
        opportunity_analysis_results = analyze_seo_opportunities(domain, market)

        # 6. Generate Enhanced Claude AI Insights
        logger.info("Generating enhanced Claude AI insights...")
        ai_insights = generate_enhanced_claude_insights(
            current_rankings,
            competitor_rankings,
            anomalies,
            opportunity_analysis_results
        )

        # 7. Construct Summary
        total_keywords_tracked = len(keywords)
        page_1_keywords = sum(1 for kw in enriched_rankings if kw.get('position') and kw['position'] <= 10)
        
        visibility_score = 0.0
        if total_keywords_tracked > 0:
            for kw_data in enriched_rankings:
                pos = kw_data.get('position')
                if pos and pos > 0 and pos <= 100:
                    visibility_score += (101 - pos)
            visibility_score = (visibility_score / (total_keywords_tracked * 100)) * 100

        summary = {
            "keywords_tracked": total_keywords_tracked,
            "page_1_keywords": page_1_keywords,
            "visibility_score": round(visibility_score, 2),
            "anomalies_count": len(anomalies),
            "new_top10_entries": len(top10_changes["new_entries"]),
            "top10_exits": len(top10_changes["exits"]),
            "competitors_tracked": len(competitors),
            "opportunities_found": len(opportunity_analysis_results.get('low_hanging_fruit', [])) + \
                                   len(opportunity_analysis_results.get('competitor_gap_keywords', []))
        }

        # 8. Generate Final Report Text
        report_text = f"""📊 SEO DAILY BRIEF (SEranking)

📊 PERFORMANCE SUMMARY:
• {summary['page_1_keywords']}/{summary['keywords_tracked']} keywords on page 1
• Visibility score: {summary['visibility_score']}%
• Anomalies detected: {summary['anomalies_count']}
• New opportunities identified: {summary['opportunities_found']}

📈 CURRENT RANKINGS ({domain}):
"""
        for kw_data in sorted(enriched_rankings, key=lambda x: x.get('position') or 999):
            pos_str = f"#{kw_data['position']}" if kw_data.get('position') else "Not ranked"
            prev_pos_str = f" (Prev: #{kw_data['previous_position']})" if kw_data.get('previous_position') else ""
            report_text += f"• \"{kw_data['keyword']}\": {pos_str}{prev_pos_str}\n"

        report_text += "\n💰 SEARCH VOLUME & VALUE:\n"
        for kw_data in sorted(enriched_rankings, key=lambda x: x.get('search_volume') or 0, reverse=True):
            if kw_data.get('search_volume'):
                report_text += f"• \"{kw_data['keyword']}\": {kw_data['search_volume']}/mo, ${kw_data['cpc']} CPC\n"

        if top10_changes["new_entries"] or top10_changes["exits"] or top10_changes["improvements"] or top10_changes["declines"]:
            report_text += "\n🔥 TOP 10 CHANGES:\n"
            for entry in top10_changes["new_entries"]:
                report_text += f"✅ \"{entry['keyword']}\": entered Top 10 at #{entry['current_position']}{f' (Prev: #{entry["previous_position"]})' if entry['previous_position'] else ''}\n"
            for exit_kw in top10_changes["exits"]:
                report_text += f"❌ \"{exit_kw['keyword']}\": exited Top 10 (Current: #{exit_kw['current_position']}, Prev: #{exit_kw['previous_position']})\n"
            for imp in top10_changes["improvements"]:
                report_text += f"⬆️ \"{imp['keyword']}\": improved to #{imp['current_position']} (Prev: #{imp['previous_position']})\n"
            for dec in top10_changes["declines"]:
                report_text += f"⬇️ \"{dec['keyword']}\": declined to #{dec['current_position']} (Prev: #{dec['previous_position']})\n"

        if competitor_summary and competitor_summary.get('competitors'):
            report_text += "\n🏆 COMPETITOR OVERVIEW:\n"
            for comp in competitor_summary['competitors']:
                report_text += f"• {comp['domain']}: tracking...\n"

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

        # 9. Return comprehensive response
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()

        return jsonify({
            "success": True,
            "domain": domain,
            "timestamp": datetime.now().isoformat(),
            "processing_time_seconds": round(processing_time, 2),
            "summary": summary,
            "current_rankings": enriched_rankings,
            "competitor_rankings": competitor_rankings,
            "keyword_metrics": keyword_metrics,
            "competitor_summary": competitor_summary,
            "anomalies": anomalies,
            "top10_changes": top10_changes,
            "opportunity_analysis": opportunity_analysis_results,
            "ai_insights": ai_insights,
            "report_text": report_text,
            "data_source": "SEranking Direct API",
            "cache_status": "enabled" if get_cache().is_available() else "disabled"
        })

    except Exception as e:
        logger.error(f"Error generating enhanced report: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
