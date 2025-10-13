"""
Claude AI Integration for SEO Intelligence
Generates truly AI-powered insights using Anthropic's Claude API
"""
import os
import json
from typing import Dict, List, Any

import anthropic
import config

# Get API key from config
ANTHROPIC_API_KEY = config.ANTHROPIC_API_KEY
CLAUDE_MODEL = config.CLAUDE_MODEL

def generate_claude_insights(
    ranking_data: Dict,
    competitor_data: Dict,
    anomalies: List[Dict],
    backlink_data: Dict = None
) -> Dict[str, Any]:
    """
    Use Claude AI to generate intelligent, context-aware SEO insights
    
    Args:
        ranking_data: Domain keyword ranking data
        competitor_data: Competitor ranking data
        anomalies: Detected ranking anomalies
        backlink_data: Backlink analysis (optional)
    
    Returns:
        Dictionary with AI-generated insights
    """
    
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY not configured. Please set it in config.py")
    
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        
        # Prepare context for Claude
        context = f"""
You are an expert SEO analyst. Analyze this SEO data and provide actionable recommendations.

CURRENT RANKINGS:
{json.dumps(ranking_data.get('keywords', {}), indent=2)[:1000]}

COMPETITOR DATA:
{json.dumps(competitor_data.get('keywords', {}), indent=2)[:1000]}

STATISTICAL ANOMALIES DETECTED (Based on 30-day historical patterns):
{json.dumps(anomalies, indent=2)}

IMPORTANT: The anomalies show statistical deviations from normal patterns:
- z_score: Number of standard deviations from 30-day mean (σ)
- expected_position: What the ranking should normally be
- deviation: How far from normal
- severity: critical (3σ+), high (2.5σ+), medium (2σ+)

Pay special attention to anomalies with high z_scores - these are statistically significant deviations from established patterns.

BACKLINKS:
{json.dumps(backlink_data, indent=2)[:500] if backlink_data else 'No backlink data'}

Please provide:
1. 3-5 critical insights focusing on the STATISTICAL ANOMALIES and explaining WHY they deviate from patterns
2. 2-3 competitive threats or opportunities based on the data
3. 1-2 insights about backlink profile (if data available)
4. 3-5 specific, actionable recommendations addressing the anomalies

For anomalies, explain:
- WHY the ranking deviated from its 30-day pattern
- WHAT likely caused this statistical outlier
- HOW to address it specifically

Format your response as JSON with these keys:
{{
  "critical_changes": ["insight 1 explaining statistical deviation", "insight 2"],
  "competitive_insights": ["insight 1", "insight 2"],
  "backlink_insights": ["insight 1", "insight 2"],
  "recommendations": ["specific action 1", "specific action 2"]
}}

Be data-driven, reference z-scores when relevant, and explain root causes of statistical deviations.
"""
        
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=2048,
            messages=[
                {"role": "user", "content": context}
            ]
        )
        
        # Parse Claude's response
        response_text = message.content[0].text
        
        # Extract JSON from response (Claude sometimes wraps it in markdown)
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            json_str = response_text.split("```")[1].split("```")[0].strip()
        else:
            json_str = response_text.strip()
        
        insights = json.loads(json_str)
        
        return {
            "ai_powered": True,
            "model": CLAUDE_MODEL,
            "critical_changes": insights.get("critical_changes", []),
            "competitive_insights": insights.get("competitive_insights", []),
            "backlink_insights": insights.get("backlink_insights", []),
            "recommendations": insights.get("recommendations", []),
            "raw_response": response_text
        }
        
    except Exception as e:
        raise Exception(f"Claude AI Error: {e}. Please check your API key and model configuration.")


# Fallback function removed - Claude AI is now required


async def main():
    """Test Claude integration with live data only"""
    print("="*80)
    print("Claude AI Insights Engine")
    print("="*80)
    print()
    print("This module provides Claude AI-powered SEO insights.")
    print()
    print("Usage:")
    print("  from claude_insights import generate_claude_insights")
    print()
    print("  insights = generate_claude_insights(")
    print("      ranking_data,")
    print("      competitor_data,")
    print("      anomalies,")
    print("      backlink_data")
    print("  )")
    print()
    print(f"✅ Claude AI configured: {bool(config.ANTHROPIC_API_KEY)}")
    print(f"✅ Model: {config.CLAUDE_MODEL}")
    print()
    print("No sample data - only live API data used.")
    print("="*80)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

