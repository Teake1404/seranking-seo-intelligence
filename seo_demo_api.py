#!/usr/bin/env python3
"""
SEO Intelligence Demo API - Lead Magnet Version
Provides instant AI-powered SEO insights using mock data
Perfect for ecommerce agency owners to see immediate value
"""
import json
import logging
import os
import random
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

# Import Claude AI for insights
from claude_insights import generate_claude_insights

# Initialize Flask
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock data for demo purposes
MOCK_DOMAINS = [
    "bagsoflove.co.uk",
    "notonthehighstreet.com", 
    "moonpig.com",
    "gettingpersonal.co.uk",
    "photobox.co.uk"
]

MOCK_KEYWORDS = [
    "custom t shirts",
    "personalized gifts",
    "photo gifts", 
    "custom mugs",
    "photo blanket",
    "personalized jewelry",
    "custom phone cases",
    "photo books",
    "personalized home decor",
    "custom canvas prints"
]

def generate_mock_rankings(domain: str, keywords: list) -> dict:
    """Generate realistic mock ranking data"""
    rankings = {
        "domain": domain,
        "timestamp": datetime.now().isoformat(),
        "keywords": {}
    }
    
    for keyword in keywords:
        # Generate realistic positions with some variation
        base_position = random.randint(1, 50)
        
        # Make some keywords perform better (more realistic)
        if "photo" in keyword.lower():
            base_position = random.randint(1, 15)
        elif "custom" in keyword.lower():
            base_position = random.randint(10, 30)
        
        rankings["keywords"][keyword] = {
            "position": base_position,
            "url": f"https://{domain}/products/{keyword.replace(' ', '-')}",
            "title": f"{keyword.title()} - {domain.replace('.co.uk', '').replace('.com', '').title()}"
        }
    
    return rankings

def generate_mock_competitor_data(domain: str, keywords: list) -> dict:
    """Generate mock competitor ranking data"""
    competitors = [d for d in MOCK_DOMAINS if d != domain][:3]
    
    competitor_data = {
        "competitors": {},
        "timestamp": datetime.now().isoformat(),
        "keywords": {}
    }
    
    # Initialize competitor structure
    for competitor in competitors:
        competitor_data["competitors"][competitor] = {}
    
    # Generate keyword rankings for each competitor
    for keyword in keywords:
        keyword_data = {}
        for competitor in competitors:
            # Generate competitive positions
            position = random.randint(1, 60)
            if competitor == "notonthehighstreet.com" and "gifts" in keyword:
                position = random.randint(1, 20)  # Strong competitor for gifts
            
            keyword_data[competitor] = {
                "position": position,
                "url": f"https://{competitor}/products/{keyword.replace(' ', '-')}",
                "title": f"{keyword.title()} - {competitor.replace('.co.uk', '').replace('.com', '').title()}"
            }
        
        competitor_data["keywords"][keyword] = keyword_data
    
    return competitor_data

def generate_mock_metrics(keywords: list) -> dict:
    """Generate mock keyword metrics"""
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "keywords": {}
    }
    
    for keyword in keywords:
        # Generate realistic metrics
        search_volume = random.randint(100, 50000)
        if "photo" in keyword.lower():
            search_volume = random.randint(5000, 25000)
        elif "custom" in keyword.lower():
            search_volume = random.randint(2000, 15000)
        
        metrics["keywords"][keyword] = {
            "search_volume": search_volume,
            "competition": random.choice(["Low", "Medium", "High"]),
            "competition_index": random.randint(20, 100),
            "cpc": round(random.uniform(0.20, 2.50), 2),
            "difficulty": random.randint(10, 80)
        }
    
    return metrics

def generate_mock_competitor_summary(domain: str, competitors: list) -> dict:
    """Generate mock competitor summary"""
    return {
        "timestamp": datetime.now().isoformat(),
        "auto_discovered": False,
        "competitors": [
            {
                "domain": comp,
                "common_keywords": random.randint(50, 500),
                "total_keywords": random.randint(1000, 10000),
                "traffic_sum": random.randint(10000, 500000),
                "price_sum": random.randint(1000, 50000)
            }
            for comp in competitors
        ]
    }

def calculate_demo_anomalies(rankings: dict) -> list:
    """Generate realistic anomalies for demo"""
    anomalies = []
    
    # Pick 1-2 keywords to have anomalies
    keywords = list(rankings["keywords"].keys())
    anomaly_keywords = random.sample(keywords, min(2, len(keywords)))
    
    for keyword in anomaly_keywords:
        current_pos = rankings["keywords"][keyword]["position"]
        
        # Generate anomaly (improvement or decline)
        if random.choice([True, False]):
            # Improvement
            expected_pos = current_pos + random.randint(5, 15)
            deviation = current_pos - expected_pos
            anomaly_type = "improvement"
        else:
            # Decline  
            expected_pos = current_pos - random.randint(5, 15)
            deviation = current_pos - expected_pos
            anomaly_type = "decline"
        
        anomalies.append({
            'keyword': keyword,
            'current_position': current_pos,
            'expected_position': expected_pos,
            'deviation': deviation,
            'z_score': round(random.uniform(2.0, 3.5), 2),
            'type': anomaly_type,
            'severity': random.choice(['medium', 'high', 'critical']),
            'previous_position': current_pos + random.randint(-3, 3),
            'change': random.randint(-5, 5)
        })
    
    return anomalies

def detect_demo_top10_changes(rankings: dict) -> dict:
    """Generate realistic Top 10 changes for demo"""
    changes = {
        "new_entries": [],
        "exits": [],
        "improvements": [],
        "declines": []
    }
    
    # Pick 1-2 keywords for Top 10 changes
    keywords = list(rankings["keywords"].keys())
    change_keywords = random.sample(keywords, min(2, len(keywords)))
    
    for keyword in change_keywords:
        current_pos = rankings["keywords"][keyword]["position"]
        
        if current_pos <= 10:
            # New entry or improvement
            if random.choice([True, False]):
                changes["new_entries"].append({
                    "keyword": keyword,
                    "current_position": current_pos,
                    "previous_position": random.randint(11, 25)
                })
            else:
                changes["improvements"].append({
                    "keyword": keyword,
                    "current_position": current_pos,
                    "previous_position": current_pos + random.randint(1, 3),
                    "change": random.randint(1, 3)
                })
    
    return changes

@app.route('/', methods=['GET'])
def home():
    """Demo homepage with interactive form"""
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🚀 SEO Intelligence Demo - AI-Powered Insights</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container { 
                max-width: 800px; 
                margin: 0 auto; 
                background: white; 
                border-radius: 20px; 
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            .header { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; 
                padding: 40px; 
                text-align: center; 
            }
            .header h1 { font-size: 2.5em; margin-bottom: 10px; }
            .header p { font-size: 1.2em; opacity: 0.9; }
            .form-section { padding: 40px; }
            .form-group { margin-bottom: 25px; }
            label { 
                display: block; 
                margin-bottom: 8px; 
                font-weight: 600; 
                color: #333; 
            }
            input, select, textarea { 
                width: 100%; 
                padding: 12px; 
                border: 2px solid #e1e5e9; 
                border-radius: 8px; 
                font-size: 16px;
                transition: border-color 0.3s;
            }
            input:focus, select:focus, textarea:focus { 
                outline: none; 
                border-color: #667eea; 
            }
            .btn { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; 
                border: none; 
                padding: 15px 30px; 
                border-radius: 8px; 
                font-size: 18px; 
                font-weight: 600;
                cursor: pointer;
                width: 100%;
                transition: transform 0.2s;
            }
            .btn:hover { transform: translateY(-2px); }
            .btn:disabled { 
                opacity: 0.6; 
                cursor: not-allowed; 
                transform: none; 
            }
            .loading { 
                display: none; 
                text-align: center; 
                padding: 20px; 
                color: #667eea; 
            }
            .spinner { 
                border: 3px solid #f3f3f3; 
                border-top: 3px solid #667eea; 
                border-radius: 50%; 
                width: 30px; 
                height: 30px; 
                animation: spin 1s linear infinite; 
                margin: 0 auto 10px; 
            }
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
            .features { 
                background: #f8f9fa; 
                padding: 40px; 
                border-top: 1px solid #e1e5e9; 
            }
            .features h3 { 
                text-align: center; 
                margin-bottom: 30px; 
                color: #333; 
            }
            .feature-grid { 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
                gap: 20px; 
            }
            .feature { 
                background: white; 
                padding: 20px; 
                border-radius: 10px; 
                text-align: center; 
                box-shadow: 0 2px 10px rgba(0,0,0,0.05); 
            }
            .feature-icon { font-size: 2em; margin-bottom: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 SEO Intelligence Demo</h1>
                <p>AI-Powered SEO Insights for Ecommerce Agencies</p>
            </div>
            
            <div class="form-section">
                <form id="demoForm">
                    <div class="form-group">
                        <label for="domain">Your Ecommerce Domain:</label>
                        <input type="text" id="domain" name="domain" placeholder="e.g., yourstore.com" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="keywords">Target Keywords (comma-separated):</label>
                        <textarea id="keywords" name="keywords" rows="3" placeholder="e.g., custom t shirts, personalized gifts, photo mugs" required></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label for="competitors">Competitor Domains (comma-separated):</label>
                        <input type="text" id="competitors" name="competitors" placeholder="e.g., competitor1.com, competitor2.com">
                    </div>
                    
                    <button type="submit" class="btn" id="generateBtn">
                        🎯 Generate AI SEO Insights
                    </button>
                </form>
                
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>🤖 AI is analyzing your SEO data...</p>
                </div>
            </div>
            
            <div class="features">
                <h3>✨ What You'll Get</h3>
                <div class="feature-grid">
                    <div class="feature">
                        <div class="feature-icon">📊</div>
                        <h4>Real-time Rankings</h4>
                        <p>Current keyword positions across search engines</p>
                    </div>
                    <div class="feature">
                        <div class="feature-icon">🔍</div>
                        <h4>Anomaly Detection</h4>
                        <p>AI identifies unusual ranking changes automatically</p>
                    </div>
                    <div class="feature">
                        <div class="feature-icon">🏆</div>
                        <h4>Competitor Analysis</h4>
                        <p>Track competitor rankings and market share</p>
                    </div>
                    <div class="feature">
                        <div class="feature-icon">💡</div>
                        <h4>AI Recommendations</h4>
                        <p>Actionable insights powered by Claude AI</p>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            document.getElementById('demoForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const form = e.target;
                const loading = document.getElementById('loading');
                const generateBtn = document.getElementById('generateBtn');
                
                // Show loading
                form.style.display = 'none';
                loading.style.display = 'block';
                generateBtn.disabled = true;
                
                // Prepare data
                const formData = new FormData(form);
                const data = {
                    domain: formData.get('domain'),
                    keywords: formData.get('keywords').split(',').map(k => k.trim()),
                    competitors: formData.get('competitors') ? 
                        formData.get('competitors').split(',').map(c => c.trim()) : []
                };
                
                try {
                    const response = await fetch('/api/demo-report', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(data)
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        // Show results in a new window
                        const resultsWindow = window.open('', '_blank', 'width=1000,height=800');
                        
                        // Safely access nested properties with fallbacks
                        const summary = result.summary || {};
                        const data = result.data || {};
                        const enrichedRankings = data.enriched_rankings || [];
                        const anomalies = result.anomalies || [];
                        const insights = result.insights || {};
                        const recommendations = insights.recommendations || [];
                        
                        resultsWindow.document.write(`
                            <html>
                                <head>
                                    <title>SEO Intelligence Report - ${data.domain || 'Unknown Domain'}</title>
                                    <style>
                                        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 20px; line-height: 1.6; }
                                        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }
                                        .section { margin-bottom: 30px; padding: 20px; border: 1px solid #e1e5e9; border-radius: 10px; }
                                        .keyword { background: #f8f9fa; padding: 10px; margin: 5px 0; border-radius: 5px; }
                                        .anomaly { background: #fff3cd; border-left: 4px solid #ffc107; padding: 10px; margin: 5px 0; }
                                        .recommendation { background: #d1ecf1; border-left: 4px solid #17a2b8; padding: 10px; margin: 5px 0; }
                                        pre { background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; }
                                    </style>
                                </head>
                                <body>
                                    <div class="header">
                                        <h1>🚀 SEO Intelligence Report</h1>
                                        <p>Domain: ${data.domain || 'Unknown'} | Generated: ${new Date().toLocaleString()}</p>
                                    </div>
                                    
                                    <div class="section">
                                        <h2>📊 Executive Summary</h2>
                                        <p>Keywords Tracked: ${summary.keywords_tracked || 0}</p>
                                        <p>Page 1 Rankings: ${summary.page_1_keywords || 0}</p>
                                        <p>Visibility Score: ${summary.visibility_score || 0}</p>
                                        <p>Anomalies Detected: ${summary.anomalies_count || 0}</p>
                                    </div>
                                    
                                    <div class="section">
                                        <h2>📈 Current Rankings</h2>
                                        ${enrichedRankings.map(ranking => `
                                            <div class="keyword">
                                                <strong>${ranking.keyword || 'Unknown'}</strong> - Position #${ranking.position || 'Not ranked'}
                                                ${ranking.search_volume ? ` | Volume: ${ranking.search_volume.toLocaleString()}/mo` : ''}
                                                ${ranking.cpc ? ` | CPC: $${ranking.cpc}` : ''}
                                            </div>
                                        `).join('')}
                                    </div>
                                    
                                    ${anomalies.length > 0 ? `
                                    <div class="section">
                                        <h2>🚨 AI-Detected Anomalies</h2>
                                        ${anomalies.map(anomaly => `
                                            <div class="anomaly">
                                                <strong>${anomaly.keyword || 'Unknown'}</strong> - ${anomaly.type || 'anomaly'} detected
                                                <br>Current: #${anomaly.current_position || 'N/A'} | Expected: #${anomaly.expected_position || 'N/A'}
                                                <br>Z-Score: ${anomaly.z_score || 'N/A'} (${anomaly.severity || 'unknown'} severity)
                                            </div>
                                        `).join('')}
                                    </div>
                                    ` : ''}
                                    
                                    <div class="section">
                                        <h2>💡 AI Recommendations</h2>
                                        ${recommendations.map((rec, i) => `
                                            <div class="recommendation">
                                                ${i + 1}. ${rec || 'No recommendation available'}
                                            </div>
                                        `).join('')}
                                    </div>
                                    
                                    <div class="section">
                                        <h2>📋 Full Report</h2>
                                        <pre>${result.report || 'No report available'}</pre>
                                    </div>
                                    
                                    <div style="text-align: center; margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 10px;">
                                        <h3>🚀 Ready to Get This for Your Clients?</h3>
                                        <p>This demo shows just a fraction of what our SEO Intelligence API can do.</p>
                                        <p><strong>Contact us to set up automated SEO monitoring for your agency!</strong></p>
                                    </div>
                                </body>
                            </html>
                        `);
                        resultsWindow.document.close();
                    } else {
                        alert('Error generating report: ' + result.error);
                    }
                } catch (error) {
                    alert('Error: ' + error.message);
                } finally {
                    // Hide loading
                    form.style.display = 'block';
                    loading.style.display = 'none';
                    generateBtn.disabled = false;
                }
            });
        </script>
    </body>
    </html>
    """
    return html_template

@app.route('/api/demo-report', methods=['POST'])
def generate_demo_report():
    """Generate SEO report using mock data for demo purposes"""
    try:
        logger.info("🚀 Generating SEO demo report...")
        
        # Get request data
        data = request.json or {}
        domain = data.get('domain', 'demo-store.com')
        keywords = data.get('keywords', ['custom gifts', 'personalized items'])
        competitors = data.get('competitors', ['competitor1.com', 'competitor2.com'])
        
        # Generate mock data
        logger.info("📊 Generating mock SEO data...")
        
        rankings = generate_mock_rankings(domain, keywords)
        competitor_data = generate_mock_competitor_data(domain, keywords)
        metrics = generate_mock_metrics(keywords)
        competitor_summary = generate_mock_competitor_summary(domain, competitors)
        
        # Generate anomalies and changes
        anomalies = calculate_demo_anomalies(rankings)
        top10_changes = detect_demo_top10_changes(rankings)
        
        # Generate Claude AI insights
        logger.info("🤖 Generating Claude AI insights...")
        insights = generate_claude_insights(
            rankings,
            competitor_data,
            anomalies,
            None
        )
        
        # Calculate summary stats
        total_keywords = len(rankings["keywords"])
        page_1_keywords = sum(1 for k, v in rankings["keywords"].items() if v.get('position') and v['position'] <= 10)
        
        # Calculate visibility score
        total_score = 0
        for keyword, info in rankings["keywords"].items():
            position = info.get('position')
            if position and position <= 10:
                score = max(0, 100 - (position - 1) * 10)
                total_score += score
        
        visibility_score = round(total_score / total_keywords, 1) if total_keywords > 0 else 0
        
        # Format report
        report = f"""📊 SEO INTELLIGENCE REPORT (DEMO)

📊 PERFORMANCE SUMMARY:
• {page_1_keywords}/{total_keywords} keywords on page 1
• Visibility score: {visibility_score}
• Anomalies detected: {len(anomalies)}

📈 CURRENT RANKINGS:
"""
        
        for keyword, info in rankings["keywords"].items():
            if info.get('position'):
                report += f"• \"{keyword}\": #{info['position']}\n"
        
        report += "\n💰 SEARCH VOLUME & VALUE:\n"
        for keyword, metrics_data in metrics["keywords"].items():
            volume = metrics_data.get('search_volume', 0)
            cpc = metrics_data.get('cpc', 0)
            if volume > 0:
                report += f"• \"{keyword}\": {volume:,}/mo, ${cpc:.2f} CPC\n"
        
        if anomalies:
            report += "\n🚨 AI-DETECTED ANOMALIES:\n"
            for anomaly in anomalies[:3]:
                emoji = "📈" if anomaly['type'] == 'improvement' else "📉"
                report += f"{emoji} \"{anomaly['keyword']}\": #{anomaly['current_position']} "
                report += f"(expected: #{anomaly['expected_position']}, "
                report += f"{anomaly['z_score']}σ deviation)\n"
        
        if insights.get('recommendations'):
            report += "\n💡 AI RECOMMENDATIONS:\n"
            for i, rec in enumerate(insights['recommendations'][:5], 1):
                report += f"{i}. {rec}\n"
        
        report += f"\n---\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nData: Demo Mode\nAI: {insights.get('model')}"
        
        # Prepare enriched data
        enriched_rankings = []
        for keyword, rank_info in rankings["keywords"].items():
            metrics_data = metrics["keywords"].get(keyword, {})
            
            enriched_rankings.append({
                "keyword": keyword,
                "domain": domain,
                "position": rank_info.get('position'),
                "url": rank_info.get('url'),
                "title": rank_info.get('title'),
                "date": datetime.now().strftime("%Y-%m-%d"),
                "timestamp": datetime.now().isoformat(),
                "search_volume": metrics_data.get('search_volume', 0),
                "cpc": metrics_data.get('cpc', 0),
                "difficulty": metrics_data.get('difficulty', 0),
                "in_top10": rank_info.get('position') is not None and rank_info.get('position') <= 10
            })
        
        # Return demo response
        response = {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "data_provider": "Demo Mode",
            "report": report,
            "data": {
                "rankings": rankings,
                "enriched_rankings": enriched_rankings,
                "competitors": competitor_data,
                "competitor_summary": competitor_summary,
                "metrics": metrics
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
                "competitors_tracked": len(competitor_summary.get('competitors', []))
            }
        }
        
        logger.info(f"✅ Demo report generated with {len(anomalies)} anomalies")
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

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        "status": "healthy",
        "service": "SEO Intelligence Demo",
        "mode": "demo",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"🚀 Starting SEO Intelligence Demo on port {port}")
    logger.info(f"   Mode: Demo (Mock Data)")
    logger.info(f"   Purpose: Lead Magnet for Ecommerce Agencies")
    app.run(host='0.0.0.0', port=port, debug=False)
