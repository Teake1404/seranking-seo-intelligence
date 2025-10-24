"""
Enhanced Claude AI Integration for SEO Intelligence
Combines existing insights with SEO opportunity analysis
"""
import os
import json
from typing import Dict, List, Any

import anthropic
import config

# Get API key from config
ANTHROPIC_API_KEY = config.ANTHROPIC_API_KEY
CLAUDE_MODEL = config.CLAUDE_MODEL

def generate_enhanced_claude_insights(
    ranking_data: Dict,
    competitor_data: Dict,
    anomalies: List[Dict],
    opportunity_data: Dict = None,
    backlink_data: Dict = None
) -> Dict[str, Any]:
    """
    Enhanced Claude AI insights combining:
    - Existing ranking analysis
    - SEO opportunity analysis
    - Competitive intelligence
    - Anomaly detection
    
    Args:
        ranking_data: Domain keyword ranking data
        competitor_data: Competitor ranking data
        anomalies: Detected ranking anomalies
        opportunity_data: SEO opportunity analysis results
        backlink_data: Backlink analysis (optional)
    
    Returns:
        Dictionary with comprehensive AI-generated insights
    """
    
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY not configured. Please set it in config.py")
    
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        
        # Prepare comprehensive context for Claude
        context = f"""
You are an expert SEO analyst. Analyze this comprehensive SEO data and provide actionable recommendations.

CURRENT RANKINGS:
{json.dumps(ranking_data.get('keywords', {}), indent=2)[:1000]}

COMPETITOR DATA:
{json.dumps(competitor_data.get('keywords', {}), indent=2)[:1000]}

DETECTED ANOMALIES:
{json.dumps(anomalies, indent=2)[:1000]}
"""

        # Add opportunity analysis if available
        if opportunity_data:
            context += f"""

SEO OPPORTUNITY ANALYSIS:
- Lost Keywords: {len(opportunity_data.get('lost_keywords', []))} found
- Declining Keywords: {len(opportunity_data.get('declining_keywords', []))} found
- Competitor Keywords: {len(opportunity_data.get('competitor_keywords', []))} opportunities
- Related Keywords: {len(opportunity_data.get('related_keywords', []))} found
- Similar Keywords: {len(opportunity_data.get('similar_keywords', []))} found

TOP LOST KEYWORDS:
{json.dumps(opportunity_data.get('lost_keywords', [])[:5], indent=2)}

TOP COMPETITOR OPPORTUNITIES:
{json.dumps(opportunity_data.get('competitor_keywords', [])[:5], indent=2)}

LOW-HANGING FRUIT OPPORTUNITIES:
{json.dumps(opportunity_data.get('low_hanging_fruit', [])[:5], indent=2)}
"""

        # Add backlink data if available
        if backlink_data:
            context += f"""

BACKLINK ANALYSIS:
{json.dumps(backlink_data, indent=2)[:1000]}
"""

        context += """

Please provide:
1. CRITICAL CHANGES: Immediate issues requiring attention
2. COMPETITIVE INSIGHTS: Competitive landscape analysis
3. OPPORTUNITY INSIGHTS: New keyword opportunities and low-hanging fruit
4. BACKLINK INSIGHTS: Link building opportunities (if backlink data provided)
5. RECOMMENDATIONS: Specific, actionable next steps

Focus on:
- Immediate actions for lost/declining keywords
- Quick wins from low-hanging fruit opportunities
- Competitive threats and opportunities
- Content strategy recommendations
- Technical SEO priorities

Be specific and actionable. Prioritize by impact and effort.
"""

        # Call Claude API
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4000,
            messages=[{
                "role": "user",
                "content": context
            }]
        )
        
        # Parse Claude's response
        claude_response = response.content[0].text
        
        # Extract structured insights
        insights = {
            "ai_powered": True,
            "model": CLAUDE_MODEL,
            "raw_response": claude_response,
            "critical_changes": [],
            "competitive_insights": [],
            "opportunity_insights": [],
            "backlink_insights": [],
            "recommendations": []
        }
        
        # Parse the response to extract structured insights
        try:
            # Look for JSON in the response
            if "```json" in claude_response:
                json_start = claude_response.find("```json") + 7
                json_end = claude_response.find("```", json_start)
                json_str = claude_response[json_start:json_end].strip()
                
                parsed_insights = json.loads(json_str)
                insights.update(parsed_insights)
            else:
                # Fallback: extract insights from text
                insights = parse_text_insights(claude_response, insights)
                
        except Exception as e:
            print(f"Warning: Could not parse Claude response as JSON: {e}")
            insights = parse_text_insights(claude_response, insights)
        
        return insights
        
    except Exception as e:
        return {
            "ai_powered": False,
            "error": f"Claude API error: {str(e)}",
            "critical_changes": ["AI analysis failed - manual review required"],
            "competitive_insights": ["Unable to generate competitive insights"],
            "opportunity_insights": ["Unable to analyze opportunities"],
            "backlink_insights": ["Unable to analyze backlinks"],
            "recommendations": ["Review data manually and contact support if issues persist"]
        }

def parse_text_insights(text: str, insights: Dict) -> Dict:
    """Parse text response to extract structured insights"""
    
    # Extract critical changes
    if "CRITICAL CHANGES:" in text:
        start = text.find("CRITICAL CHANGES:") + len("CRITICAL CHANGES:")
        end = text.find("COMPETITIVE INSIGHTS:", start)
        if end == -1:
            end = text.find("OPPORTUNITY INSIGHTS:", start)
        if end == -1:
            end = text.find("RECOMMENDATIONS:", start)
        
        if end > start:
            critical_text = text[start:end].strip()
            insights["critical_changes"] = [line.strip() for line in critical_text.split('\n') if line.strip() and not line.strip().startswith('-')]
    
    # Extract competitive insights
    if "COMPETITIVE INSIGHTS:" in text:
        start = text.find("COMPETITIVE INSIGHTS:") + len("COMPETITIVE INSIGHTS:")
        end = text.find("OPPORTUNITY INSIGHTS:", start)
        if end == -1:
            end = text.find("RECOMMENDATIONS:", start)
        
        if end > start:
            competitive_text = text[start:end].strip()
            insights["competitive_insights"] = [line.strip() for line in competitive_text.split('\n') if line.strip() and not line.strip().startswith('-')]
    
    # Extract opportunity insights
    if "OPPORTUNITY INSIGHTS:" in text:
        start = text.find("OPPORTUNITY INSIGHTS:") + len("OPPORTUNITY INSIGHTS:")
        end = text.find("BACKLINK INSIGHTS:", start)
        if end == -1:
            end = text.find("RECOMMENDATIONS:", start)
        
        if end > start:
            opportunity_text = text[start:end].strip()
            insights["opportunity_insights"] = [line.strip() for line in opportunity_text.split('\n') if line.strip() and not line.strip().startswith('-')]
    
    # Extract backlink insights
    if "BACKLINK INSIGHTS:" in text:
        start = text.find("BACKLINK INSIGHTS:") + len("BACKLINK INSIGHTS:")
        end = text.find("RECOMMENDATIONS:", start)
        
        if end > start:
            backlink_text = text[start:end].strip()
            insights["backlink_insights"] = [line.strip() for line in backlink_text.split('\n') if line.strip() and not line.strip().startswith('-')]
    
    # Extract recommendations
    if "RECOMMENDATIONS:" in text:
        start = text.find("RECOMMENDATIONS:") + len("RECOMMENDATIONS:")
        recommendations_text = text[start:].strip()
        insights["recommendations"] = [line.strip() for line in recommendations_text.split('\n') if line.strip() and not line.strip().startswith('-')]
    
    return insights

def generate_opportunity_insights(opportunity_data: Dict) -> Dict[str, Any]:
    """
    Generate specific insights for SEO opportunities
    
    Args:
        opportunity_data: Results from SEO opportunity analysis
    
    Returns:
        Dictionary with opportunity-specific insights
    """
    
    insights = {
        "opportunity_analysis": True,
        "lost_keywords_count": len(opportunity_data.get('lost_keywords', [])),
        "declining_keywords_count": len(opportunity_data.get('declining_keywords', [])),
        "competitor_opportunities_count": len(opportunity_data.get('competitor_keywords', [])),
        "low_hanging_fruit_count": len(opportunity_data.get('low_hanging_fruit', [])),
        "priority_actions": [],
        "content_opportunities": [],
        "competitive_gaps": []
    }
    
    # Analyze lost keywords
    lost_keywords = opportunity_data.get('lost_keywords', [])
    if lost_keywords:
        high_volume_lost = [kw for kw in lost_keywords if kw.get('volume', 0) > 1000]
        insights["priority_actions"].append(f"Recover {len(high_volume_lost)} high-volume lost keywords")
    
    # Analyze declining keywords
    declining_keywords = opportunity_data.get('declining_keywords', [])
    if declining_keywords:
        insights["priority_actions"].append(f"Address {len(declining_keywords)} declining keyword positions")
    
    # Analyze competitor opportunities
    competitor_keywords = opportunity_data.get('competitor_keywords', [])
    if competitor_keywords:
        high_volume_competitor = [kw for kw in competitor_keywords if kw.get('volume', 0) > 5000]
        insights["competitive_gaps"].append(f"Target {len(high_volume_competitor)} high-volume competitor keywords")
    
    # Analyze low-hanging fruit
    low_hanging = opportunity_data.get('low_hanging_fruit', [])
    if low_hanging:
        insights["content_opportunities"].append(f"Create content for {len(low_hanging)} low-difficulty, high-volume keywords")
    
    return insights

