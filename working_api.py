#!/usr/bin/env python3
"""
SEO Insights API for Google Cloud Run
"""
import json
import os
import re
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

# Remove any config imports that might cause issues
# This API uses its own AI insights logic, no external API keys needed

def parse_n8n_data(raw_data):
    """Parse the raw data from n8n SEranking MCP"""
    try:
        if not raw_data or raw_data.strip() == '':
            return []
            
        print(f"Raw data: {raw_data[:200]}...")
        
        # First parse the outer JSON to get the text field
        outer_json_match = re.search(r'\{.*\}', raw_data, re.DOTALL)
        if outer_json_match:
            outer_json_str = outer_json_match.group()
            outer_data = json.loads(outer_json_str)
            
            # Extract the text field which contains the actual data
            if 'result' in outer_data and 'content' in outer_data['result']:
                content = outer_data['result']['content']
                if content and len(content) > 0 and 'text' in content[0]:
                    text_data = content[0]['text']
                    print(f"Extracted text: {text_data[:100]}...")
                    
                    # Parse the inner JSON array
                    inner_data = json.loads(text_data)
                    print(f"Parsed {len(inner_data)} items")
                    return inner_data
        
        print("No valid data found")
        return []
    except Exception as e:
        print(f"Error parsing data: {e}")
        return []

def parse_n8n_competitors_data(raw_data):
    """Parse competitors data from n8n SEranking MCP"""
    try:
        if not raw_data or raw_data.strip() == '':
            return []
            
        print(f"Competitors raw data: {raw_data[:200]}...")
        
        # First parse the outer JSON to get the text field
        outer_json_match = re.search(r'\{.*\}', raw_data, re.DOTALL)
        if outer_json_match:
            outer_json_str = outer_json_match.group()
            outer_data = json.loads(outer_json_str)
            
            # Extract the text field which contains the actual data
            if 'result' in outer_data and 'content' in outer_data['result']:
                content = outer_data['result']['content']
                if content and len(content) > 0 and 'text' in content[0]:
                    text_data = content[0]['text']
                    print(f"Extracted competitors text: {text_data[:100]}...")
                    
                    # Parse the inner JSON array
                    inner_data = json.loads(text_data)
                    print(f"Parsed {len(inner_data)} competitors")
                    return inner_data
        
        print("No valid competitors data found")
        return []
    except Exception as e:
        print(f"Error parsing competitors data: {e}")
        return []

def generate_claude_insights(rankings_data, competitors_data, domain):
    """Generate AI insights using Claude AI"""
    import anthropic
    
    # Initialize Claude client
    client = anthropic.Anthropic(
        api_key=os.getenv('ANTHROPIC_API_KEY')
    )
    
    # Prepare data for Claude
    data_summary = {
        "domain": domain,
        "total_keywords": len(rankings_data),
        "rankings": rankings_data[:10],  # Top 10 for context
        "competitors": competitors_data[:5]  # Top 5 competitors
    }
    
    # Create prompt for Claude
    prompt = f"""You are an SEO expert analyzing data for {domain}. 

Data Summary:
- Total keywords tracked: {data_summary['total_keywords']}
- Top rankings: {json.dumps(data_summary['rankings'], indent=2)}
- Top competitors: {json.dumps(data_summary['competitors'], indent=2)}

Please provide:
1. Executive summary of SEO performance
2. Top 3 actionable recommendations
3. Competitive insights
4. Priority areas for improvement

Format your response as a comprehensive SEO report with clear sections and actionable insights."""

    try:
        # Call Claude AI
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        claude_insights = response.content[0].text
        
        # Basic metrics for structure
        total_keywords = len(rankings_data)
        page_1_keywords = sum(1 for item in rankings_data if item.get('position', 0) <= 10 and item.get('position', 0) > 0)
        
        # Calculate visibility score
        visibility_score = 0.0
        if total_keywords > 0:
            for item in rankings_data:
                pos = item.get('position', 0)
                if pos > 0 and pos <= 100:
                    visibility_score += (101 - pos)
            visibility_score = (visibility_score / (total_keywords * 100)) * 100
        
        return {
            "total_keywords": total_keywords,
            "page_1_keywords": page_1_keywords,
            "visibility_score": round(visibility_score, 2),
            "claude_insights": claude_insights,
            "top_competitors": competitors_data[:5] if competitors_data else []
        }
        
    except Exception as e:
        return {
            "error": f"Claude AI analysis failed: {str(e)}",
            "total_keywords": len(rankings_data),
            "page_1_keywords": 0,
            "visibility_score": 0,
            "claude_insights": "Unable to generate AI insights due to API error."
        }

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "service": "Working AI Insights API",
        "status": "running",
        "version": "1.0",
        "message": "API is working properly!"
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/ai-insights', methods=['POST'])
def generate_ai_insights():
    """Generate AI insights from n8n data"""
    try:
        data = request.get_json(force=True, silent=True)
        
        if not data:
            return jsonify({"success": False, "error": "No JSON data received"}), 400

        # Extract data
        rankings_data_raw = data.get('rankings_data', '')
        competitors_data_raw = data.get('competitors_data', '')
        domain = data.get('domain', 'unknown.com')
        
        print(f"Processing data for {domain}")
        print(f"Rankings data length: {len(rankings_data_raw)}")
        print(f"Competitors data length: {len(competitors_data_raw)}")
        
        # Parse data
        rankings_data = parse_n8n_data(rankings_data_raw)
        competitors_data = parse_n8n_competitors_data(competitors_data_raw)
        
        print(f"Parsed {len(rankings_data)} rankings and {len(competitors_data)} competitors")
        
        # Generate insights using Claude AI
        insights = generate_claude_insights(rankings_data, competitors_data, domain)
        
        # Create report with Claude insights
        report = f"""📊 AI INSIGHTS REPORT - {domain.upper()}

📈 PERFORMANCE SUMMARY:
• {insights['page_1_keywords']}/{insights['total_keywords']} keywords on page 1
• Visibility score: {insights['visibility_score']}%

🤖 CLAUDE AI INSIGHTS:
{insights.get('claude_insights', 'No insights available')}

🏆 TOP COMPETITORS:"""
        
        if insights.get('top_competitors'):
            for comp in insights['top_competitors'][:3]:
                report += f"\n• {comp.get('domain', 'Unknown')}: {comp.get('common_keywords', 0):,} common keywords"
        
        return jsonify({
            "success": True,
            "domain": domain,
            "timestamp": datetime.now().isoformat(),
            "insights": insights,
            "report": report,
            "data_processed": {
                "rankings_count": len(rankings_data),
                "competitors_count": len(competitors_data)
            }
        })
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    print("🚀 Starting SEO Insights API...")
    print("📡 API will be available at: http://localhost:8080")
    print("🔗 Test endpoint: http://localhost:8080/health")
    print("🤖 AI Insights endpoint: http://localhost:8080/api/ai-insights")
    
    # Get port from environment variable (for Cloud Run)
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
